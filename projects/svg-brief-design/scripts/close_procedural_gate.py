#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Seal the incomplete gate without altering native artifacts or reading private content."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
ROOT = REPO / "evaluations/runs/svp3"


def main():
    job = ROOT / "private-jobs/b"
    native = json.loads((job / "result.json").read_text())
    assert native["finished_at"] is None
    assert not (ROOT / "private-jobs/w").exists()
    records = []
    for trial in sorted(p for p in job.iterdir() if p.is_dir()):
        result_path = trial / "result.json"
        trace = trial / "agent/pi.txt"
        result = json.loads(result_path.read_text()) if result_path.exists() else {}
        events = [json.loads(line) for line in trace.read_text().splitlines()] if trace.exists() else []
        messages = [e for e in events if e.get("type") == "message_end" and e.get("message", {}).get("role") == "assistant"]
        records.append({"trial": trial.name, "has_native_result": bool(result),
                        "agent_execution_observed": bool(messages),
                        "exception_type": (result.get("exception_info") or {}).get("exception_type"),
                        "has_native_reward": bool((result.get("verifier_result") or {}).get("rewards"))})
    assert sum(r["agent_execution_observed"] for r in records) == 3
    assert sum(r["has_native_reward"] for r in records) == 2
    assert any(r["exception_type"] == "CancelledError" for r in records)
    result = {
        "closed_at": datetime.now(timezone.utc).isoformat(),
        "status": "inconclusive-infrastructure-failure", "promoted": False,
        "selected_candidate": "q", "candidate_mutated_after_gate": False,
        "native_population_gate_state": "staged; not overwritten or fabricated",
        "cause": "The compatibility resolver normalized task paths but left metric source resolution under the Windows-spelled dataset name. Harbor's progress-metric lookup raised IndexError and cancelled the incomplete job.",
        "expected_validation_trials": 18, "observed_validation_agent_executions": 3,
        "completed_baseline_measurements": 2, "winner_agent_executions": 0,
        "prelaunch_path_failure_agent_executions": 0, "semantic_retries": 0,
        "private_cohort_consumed": True, "additional_organic_reserve_unopened": True,
        "recovery": "Not eligible: the installed recovery skill denies incomplete/cancelled roots except an exact pre-agent SIGTERM contract, which this completed-agent/progress-hook failure does not satisfy.",
        "decision": "Keep the native partial root intact. Do not compute a private gain, run the winner, replay completed trials, mutate the candidate or claim independent promotion. Ship the requested new capabilities as an experimental development winner, with the original baseline preserved.",
        "future_preflight": "Normalize dataset paths before freezing any new study. Check that every resolved task source has a populated native metric registry before any model call. A new unbiased claim needs a fresh private cohort.",
        "trials": records,
        "native_tree_sha256": {p.relative_to(job).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                               for p in sorted(job.rglob("*")) if p.is_file()},
        "stage_manifest_sha256": hashlib.sha256((ROOT / "holdout/generation-001/attempt-000/attempt.json").read_bytes()).hexdigest(),
        "path_runner_sha256": hashlib.sha256((REPO / "projects/svg-brief-design/scripts/run_procedural_private_path_gate.py").read_bytes()).hexdigest(),
    }
    with (ROOT / "independent-gate-disposition.json").open("x", encoding="utf-8") as handle:
        json.dump(result, handle, indent=2)
        handle.write("\n")
    print(json.dumps({key: result[key] for key in ("status", "promoted", "observed_validation_agent_executions", "completed_baseline_measurements", "winner_agent_executions")}))


if __name__ == "__main__":
    main()
