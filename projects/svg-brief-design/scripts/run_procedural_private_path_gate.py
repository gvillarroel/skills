#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = ["harbor==0.18.0", "PyYAML>=6,<7"]
# ///
"""Resolve one frozen Windows-spelled WSL dataset path before native execution."""
import asyncio
import contextlib
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys
from harbor.job import Job
from harbor.models.job.config import DatasetConfig, JobConfig
from run_procedural_private_gate import ROOT, STAGE, prepare
from prepare_procedural_study import write


async def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "doctor"
    assert mode in {"doctor", "run"}
    manifest, contracts = prepare()
    failed = json.loads((ROOT / "private-gate-started.json").read_text())
    for role, value in contracts.items():
        previous = failed["contracts"][role]
        assert previous["original_config_sha256"] == value["original_config_sha256"]
        assert previous["skill_digest"] == value["skill_digest"]
        # Harbor serializes its exception set in process-dependent order.
        # Compare typed configs, then preserve the exact predecessor JSON.
        assert JobConfig.model_validate(previous["effective_config"]) == JobConfig.model_validate(value["effective_config"])
    contracts = failed["contracts"]
    original_worker = Path(__file__).with_name("run_procedural_private_gate.py")
    assert hashlib.sha256(original_worker.read_bytes()).hexdigest() == failed["runner_sha256"]
    # The predecessor failed in Job.create, before a job directory, lock,
    # trial, agent container or model call existed. Never resume partial jobs.
    assert not (ROOT / "private-jobs").exists()
    assert not (ROOT / "private-path-gate-started.json").exists()
    raw_paths = {d["path"] for value in contracts.values()
                 for d in value["effective_config"]["datasets"]}
    assert len(raw_paths) == 1
    raw = raw_paths.pop()
    assert raw.startswith("\\mnt\\c\\") and not Path(raw).exists()
    resolved = Path(raw.replace("\\", "/"))
    assert resolved.is_absolute() and resolved.is_dir()
    # Keep the frozen JobConfig and scorer untouched. Only the native local
    # resolver receives a copy with equivalent platform path separators.
    original_resolver = DatasetConfig._get_local_task_configs

    async def resolve_dataset(self, disable_verification):
        if str(self.path) != raw:
            return await original_resolver(self, disable_verification)
        assert not disable_verification
        local = self.model_copy(update={"path": resolved})
        tasks = await original_resolver(local, disable_verification)
        assert sorted(task.path.name for task in tasks) == sorted(self.task_names)
        assert len(tasks) == 3
        return tasks

    DatasetConfig._get_local_task_configs = resolve_dataset
    config = JobConfig.model_validate(contracts["baseline"]["effective_config"])
    tasks = await config.datasets[0].get_task_configs(disable_verification=False)
    task_hashes = {}
    for task in tasks:
        task_hashes[task.path.name] = {
            p.relative_to(task.path).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(task.path.rglob("*")) if p.is_file()
        }
    if mode == "doctor":
        print(json.dumps({"ready": True, "tasks_resolved": len(tasks), "native_job_calls": 0,
                          "frozen_configs_unchanged": True, "predecessor_model_calls": 0}))
        return
    seal = {"started_at": datetime.now(timezone.utc).isoformat(),
            "stage_manifest_sha256": hashlib.sha256((STAGE / "attempt.json").read_bytes()).hexdigest(),
            "runner_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            "failed_start_sha256": hashlib.sha256((ROOT / "private-gate-started.json").read_bytes()).hexdigest(),
            "path_resolution": {"configured": raw, "resolved": str(resolved)},
            "contracts": contracts, "task_files_sha256": task_hashes,
            "max_calls": 18, "retries": 0, "predecessor_model_calls": 0,
            "private_feedback_mutation_forbidden": True}
    write(ROOT / "private-path-gate-started.json", seal)
    print(json.dumps({"private_gate_started": True, "winner": manifest["winnerCandidate"], "max_calls": 18}), flush=True)
    summaries = {}
    for role, data in contracts.items():
        config = JobConfig.model_validate(data["effective_config"])
        with (ROOT / f"private-path-{role}.stdout.txt").open("x") as out, (ROOT / f"private-path-{role}.stderr.txt").open("x") as err:
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                job = await Job.create(config)
                await job.run()
        result = json.loads((config.jobs_dir / config.job_name / "result.json").read_text())
        summaries[role] = {"completed": result["stats"]["n_completed_trials"], "errors": result["stats"]["n_errored_trials"]}
        print(json.dumps({"role": role, **summaries[role]}), flush=True)
    write(ROOT / "private-gate-finished.json", {"finished_at": datetime.now(timezone.utc).isoformat(),
          "summaries": summaries, "no_private_content_printed": True})


if __name__ == "__main__":
    asyncio.run(main())
