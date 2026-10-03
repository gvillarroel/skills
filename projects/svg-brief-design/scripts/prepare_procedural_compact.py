#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""Freeze compact candidate IDs after a successful live mount preflight."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
from prepare_procedural_study import REPO, wsl, write, hashes

ROOT = REPO / "evaluations/runs/svp3"
PARENT = REPO / "evaluations/runs/svp2"

if __name__ == "__main__":
    assert not list((PARENT / "population").rglob("pi.txt"))
    assert not list((PARENT / "population").rglob("lock.json"))
    assert all(r["passed"] for r in json.loads((ROOT / "path-length-probe.json").read_text())["rows"])
    protocol = json.loads((PARENT / "protocol.json").read_text())
    for source, name in (("baseline", "b"), ("procedural-v1", "p")):
        original = PARENT / source / "skills/svg-brief-design"
        snapshot = ROOT / "inputs" / name / "svg-brief-design"
        if snapshot.exists():
            assert hashes(snapshot) == hashes(original)
        else:
            shutil.copytree(original, snapshot)
    for name in ("development", "validation"):
        template = json.loads((PARENT / f"templates/{name}.json").read_text())
        template["jobs_dir"] = wsl(ROOT / "jobs")
        target = ROOT / f"templates/{name}.json"
        if target.exists():
            assert json.loads(target.read_text()) == template
        else:
            write(target, template)
    longest = wsl(ROOT / "generation-000/candidates/p/harbor-jobs/harbor-pop-g000-p/vector-030--d3c57e0c21dbede0__1234567/artifacts/logs/artifacts/deliverable/illustration.svg")
    protocol.update(study="svp3", registered_at=datetime.now(timezone.utc).isoformat(),
                    superseded_configuration=str(PARENT), superseded_configuration_model_calls=0,
                    candidate_id_mapping={"b": "unchanged original guide", "p": "original procedural generators v1"},
                    maximum_expected_artifact_path_length=len(longest),
                    mount_readiness_sha256=hashlib.sha256((ROOT / "path-length-probe.json").read_bytes()).hexdigest())
    assert len(longest) <= 210  # The successful 200-character target included /probe.txt.
    protocol["templates"] = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in (ROOT / "templates").glob("*.json")}
    for name in ("prepare_procedural_compact.py", "run_procedural_compact.py"):
        protocol["runtime"]["helpers"][name] = hashlib.sha256((Path(__file__).parent / name).read_bytes()).hexdigest()
    write(ROOT / "protocol.json", protocol)
    argv = ["--job-template", wsl(ROOT / "templates/development.json"), "--candidate", "b=" + wsl(ROOT / "inputs/b/svg-brief-design"),
            "--candidate", "p=" + wsl(ROOT / "inputs/p/svg-brief-design"), "--baseline", "b", "--generation", "0",
            "--reward-key", "visual_similarity", "--pass-threshold", "0", "--minimum-development-pass-rate", "1",
            "--required-reward", "artifact_valid=1", "--minimum-holdout-gain", ".015", "--allow-task-regressions", "--output", wsl(ROOT)]
    write(ROOT / "generation-000-argv.json", argv)
    write(PARENT / "prelaunch-disposition.json", {"cancelled_before_native_job_create": True, "model_calls": 0,
           "agent_traces": 0, "job_locks": 0, "reason": "212-character mount path failed task-free readiness; compact IDs fit within the successfully probed 210-character complete-file limit.",
           "successor": wsl(ROOT), "cumulative_prior_model_calls": 3})
    print(json.dumps({"registered": True, "longest_artifact_path": len(longest), "model_calls_so_far": 3}))
