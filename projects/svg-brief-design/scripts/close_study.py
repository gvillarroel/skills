#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""Summarize preserved development evidence without rescoring or model calls."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import statistics

REPO = Path(__file__).resolve().parents[3]
STUDY = REPO / "evaluations/runs/svg-brief-design-20260925-r2"


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_once(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8", newline="\n") as handle:
        json.dump(value, handle, indent=2)
        handle.write("\n")


def summarize(job):
    root = read_json(job / "result.json")
    assert root["finished_at"] and root["stats"]["n_completed_trials"] == 6
    rows = []
    for result_path in sorted(job.glob("*/result.json")):
        result = read_json(result_path)
        trial = result_path.parent
        audit = read_json(trial / "agent/skill-input-audit.json")
        integrity = read_json(trial / "agent/skill-integrity.json")
        assert audit["reference_absent"] and audit["verifier_absent"]
        assert integrity["unchanged"]
        assert integrity["files"] == audit["skill_files"]
        messages = []
        tools = []
        for line in (trial / "agent/pi.txt").read_text(encoding="utf-8").splitlines():
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                continue
            if event.get("type") == "message_end" and event.get("message", {}).get("role") == "assistant":
                messages.append(event["message"])
            if event.get("type") == "tool_execution_start":
                tools.append(event.get("toolName"))
        assert messages and all(m.get("model") == "gpt-6-luna" for m in messages)
        assert set(tools) <= {"write"}
        exception = result.get("exception_info")
        terminal_error = messages[-1].get("errorMessage") if exception else None
        if exception:
            assert exception["exception_type"] == "RuntimeError"
            assert messages[-1].get("stopReason") == "error"
            assert terminal_error == "WebSocket closed 1011"
        rewards = (result.get("verifier_result") or {}).get("rewards") or {}
        rows.append({
            "task": result["task_name"],
            "evaluable": exception is None,
            "visual_similarity": rewards.get("visual_similarity") if not exception else None,
            "style_similarity": rewards.get("style_similarity") if not exception else None,
            "artifact_valid": rewards.get("artifact_valid") if not exception else None,
            "terminal_error": terminal_error,
            "evidence": str(result_path.relative_to(STUDY)).replace("\\", "/"),
            "result_sha256": sha256(result_path),
            "pi_trace_sha256": sha256(trial / "agent/pi.txt"),
            "input_audit_sha256": sha256(trial / "agent/skill-input-audit.json"),
            "integrity_sha256": sha256(trial / "agent/skill-integrity.json"),
        })
    assert len(rows) == 6
    complete = all(row["evaluable"] for row in rows)
    return {
        "candidate": job.name.split("-development-")[-1],
        "job": str(job.relative_to(STUDY)).replace("\\", "/"),
        "planned_trials": 6,
        "evaluable_trials": sum(row["evaluable"] for row in rows),
        "provider_error_trials": sum(not row["evaluable"] for row in rows),
        "mean_visual_similarity": statistics.mean(row["visual_similarity"] for row in rows) if complete else None,
        "mean_style_similarity": statistics.mean(row["style_similarity"] for row in rows) if complete else None,
        "technical_valid_trials": sum(row["artifact_valid"] == 1 for row in rows),
        "input_boundary_and_integrity_checks": "passed",
        "rows": rows,
    }


def main():
    assert not (STUDY / "search/holdout").exists(), "Private gate must remain unopened"
    assert not (STUDY / "closeout.json").exists(), "Preserve the existing closeout"
    results = [summarize(p.parent) for p in sorted((STUDY / "search/development").glob("generation-*/harbor-jobs/*/result.json"))]
    assert {r["candidate"] for r in results} == {"baseline", "visual-grammar", "semantic-structure", "graphic-economy"}
    by_name = {result["candidate"]: result for result in results}
    baseline = by_name["baseline"]
    guide = by_name["visual-grammar"]
    gain = guide["mean_visual_similarity"] - baseline["mean_visual_similarity"]
    threshold = read_json(STUDY / "protocol.json")["private_gate"]["minimumMeanGain"]
    assert 0 < gain < threshold
    baseline_cases = {row["task"]: row for row in baseline["rows"]}
    paired = [{"task": row["task"], "baseline": baseline_cases[row["task"]]["visual_similarity"], "guide": row["visual_similarity"], "delta": row["visual_similarity"] - baseline_cases[row["task"]]["visual_similarity"]} for row in guide["rows"]]
    source = REPO / "skills/svg-brief-design"
    frozen = STUDY / "candidates/visual-grammar/svg-brief-design"
    files = {p.relative_to(source).as_posix(): sha256(p) for p in sorted(source.rglob("*")) if p.is_file()}
    assert files == {p.relative_to(frozen).as_posix(): sha256(p) for p in sorted(frozen.rglob("*")) if p.is_file()}
    summary = {
        "schema_version": 1,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "study_id": STUDY.name,
        "status": "closed-without-promotion",
        "model": "openai-codex/gpt-6-luna",
        "pi_version": "0.84.2",
        "harbor_version": "0.18.0",
        "canonical_candidate": "visual-grammar",
        "canonical_status": "experimental; validating",
        "promoted": False,
        "private_gate_opened": False,
        "selected_finalist": None,
        "development_native_trials": sum(r["planned_trials"] for r in results),
        "development_provider_error_trials": sum(r["provider_error_trials"] for r in results),
        "preliminary_separate_native_trials": 6,
        "private_native_trials": 0,
        "mean_gain": gain,
        "relative_gain": gain / baseline["mean_visual_similarity"],
        "required_mean_gain": threshold,
        "improved_cases": sum(r["delta"] > 0 for r in paired),
        "regressed_cases": sum(r["delta"] < 0 for r in paired),
        "semantic_correctness": None,
        "cost_usd": None,
        "source_files": files,
        "candidates": results,
        "paired_comparison": paired,
        "decision": "No evaluable candidate meets the preregistered development gain. Preserve the baseline and unopened private gate. The user-authorized local skill is an experimental copy of the fully measured first guide, not a promoted winner.",
        "recovery": "Eleven native trials end with message-only WebSocket closed 1011. The stock recovery contract does not accept this as an allowlisted external retry. No trials were retried and no failures were converted to numeric zero fitness.",
        "next_study": "First diagnose the transport on a task-free provider probe and record a repaired execution profile. Register a fresh bounded study before any new inference; preserve every previous job. Reserve independent validation before development and require repeated naturalistic/generalization and unforced routing checks before release.",
    }
    write_once(STUDY / "closeout.json", summary)
    compact = {key: value for key, value in summary.items() if key not in {"candidates", "paired_comparison"}}
    compact["candidates"] = [{key: value for key, value in result.items() if key != "rows"} for result in results]
    write_once(REPO / "evaluations/svg-brief-design/study-20260925.json", compact)
    print(json.dumps({"status": summary["status"], "mean_gain": gain, "provider_errors": summary["development_provider_error_trials"], "artwork_boundary_checks": 24, "private_gate_opened": False}))


if __name__ == "__main__":
    main()
