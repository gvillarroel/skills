#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = ["harbor==0.18.0", "PyYAML>=6,<7"]
# ///
"""Execute one frozen independent gate at short native job paths; expose no prompts."""
import asyncio
import contextlib
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import yaml
from harbor.job import Job
from harbor.models.job.config import JobConfig
from prepare_procedural_study import write

ROOT = Path(__file__).resolve().parents[3] / "evaluations/runs/svp3"
STAGE = ROOT / "holdout/generation-001/attempt-000"
ENGINE = Path("/mnt/c/Users/villa/.codex/skills/harbor-population-search/scripts/search_harbor_population.py")


def engine():
    spec = importlib.util.spec_from_file_location("private_population_contract", ENGINE)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def prepare():
    module = engine()
    manifest = json.loads((STAGE / "attempt.json").read_text())
    assert manifest["mode"] == "analyze-only"
    assert json.loads((STAGE / "result.json").read_text())["status"] == "staged"
    selected = json.loads((ROOT / "run.json").read_text())["selectedWinner"]
    assert selected == manifest["winnerCandidate"] and selected != "b"
    contracts = {}
    for role, short in (("baseline", "b"), ("winner", "w")):
        original = yaml.safe_load((STAGE / role / "harbor-job.yaml").read_text())
        clone = dict(original)
        clone["job_name"], clone["jobs_dir"] = short, str(ROOT / "private-jobs")
        assert module.config_fingerprint(original) == module.config_fingerprint(clone)
        config = JobConfig.model_validate(clone)
        assert config.n_attempts == 3 and config.n_concurrent_trials == 3 and config.retry.max_retries == 0
        assert sum(len(d.task_names) for d in config.datasets) == 3
        contracts[role] = {"original_config_sha256": hashlib.sha256((STAGE / role / "harbor-job.yaml").read_bytes()).hexdigest(),
                           "effective_config": config.model_dump(mode="json", exclude_none=True),
                           "skill_digest": module.directory_digest(Path(config.agents[0].skills[0]))}
    return manifest, contracts


async def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "doctor"
    assert mode in {"doctor", "run"}
    manifest, contracts = prepare()
    if mode == "doctor":
        print(json.dumps({"ready": True, "winner": manifest["winnerCandidate"], "max_calls": 18, "identity_fields_changed_only": ["job_name", "jobs_dir"], "native_job_calls": 0}))
        return
    seal = {"started_at": datetime.now(timezone.utc).isoformat(), "stage_manifest_sha256": hashlib.sha256((STAGE / "attempt.json").read_bytes()).hexdigest(),
            "runner_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(), "contracts": contracts,
            "max_calls": 18, "retries": 0, "private_feedback_mutation_forbidden": True}
    write(ROOT / "private-gate-started.json", seal)
    print(json.dumps({"private_gate_started": True, "winner": manifest["winnerCandidate"], "max_calls": 18}), flush=True)
    summaries = {}
    for role, data in contracts.items():
        config = JobConfig.model_validate(data["effective_config"])
        with (ROOT / f"private-{role}.stdout.txt").open("w") as out, (ROOT / f"private-{role}.stderr.txt").open("w") as err:
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                job = await Job.create(config)
                await job.run()
        # Only native counters leave this worker; the population analyzer applies
        # the exact frozen scoring/provenance gate after both jobs have finished.
        result = json.loads((config.jobs_dir / config.job_name / "result.json").read_text())
        summaries[role] = {"completed": result["stats"]["n_completed_trials"], "errors": result["stats"]["n_errored_trials"]}
        print(json.dumps({"role": role, **summaries[role]}), flush=True)
    write(ROOT / "private-gate-finished.json", {"finished_at": datetime.now(timezone.utc).isoformat(), "summaries": summaries, "no_private_content_printed": True})


if __name__ == "__main__":
    asyncio.run(main())
