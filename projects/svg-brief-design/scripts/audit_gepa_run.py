#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""Audit completed native GEPA evidence without rescoring or invoking a model."""
from pathlib import Path
from collections import Counter
import hashlib
import json
import statistics
import argparse

REPO = Path(__file__).resolve().parents[3]
parser = argparse.ArgumentParser()
parser.add_argument("--study", type=Path, default=REPO / "evaluations/runs/svg-brief-design-gepa-20260925")
STUDY = parser.parse_args().study.resolve()
RUN = STUDY / "run-async-compatible"


def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def files(root):
    return {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(root.rglob("*")) if p.is_file()}


def main():
    run = read(RUN / "run.json")
    assert run["evaluationBoundary"]["validationOptimizerVisible"] is False
    assert run["evaluationBoundary"]["candidateDigestFrozenBeforeValidation"] == run["evaluationBoundary"]["candidateDigestAfterValidation"]
    assert run["skillProvenance"]["sourceUnchanged"]
    baseline = files(RUN / "baseline-snapshot/skills/svg-brief-design")
    candidate = files(RUN / "candidate-skill")
    assert set(baseline) == set(candidate) == {"SKILL.md", "references/svg-mechanics.md", "agents/openai.yaml"}
    assert all(candidate[name] == baseline[name] for name in baseline if name != "SKILL.md")
    rows = []
    for evaluation_file in sorted((RUN / "harbor-trials").glob("*/*/evaluation.json")):
        evaluation = read(evaluation_file)
        phase = evaluation_file.parent.parent.name
        if evaluation["skillProvenance"].get("status") == "candidate-rejected":
            rows.append({"phase": phase, "candidate_rejected": True, "reward": evaluation["reward"], "reason": evaluation["error"]})
            continue
        assert evaluation["skillProvenance"]["verified"]
        result_files = list((evaluation_file.parent / "trials").glob("*/result.json"))
        assert len(result_files) == 1
        result_path = result_files[0]
        trial = result_path.parent
        result = read(result_path)
        audit = read(trial / "agent/skill-input-audit.json")
        integrity = read(trial / "agent/skill-integrity.json")
        loading = read(trial / "agent/loading-contract.json")
        assert audit["reference_absent"] and audit["verifier_absent"] and audit["ambient_skills_disabled"]
        assert integrity["unchanged"] and audit["skill_files"] == integrity["files"]
        assert loading["transport"] == "sse"
        assistant = []
        tools = []
        for line in (trial / "agent/pi.txt").read_text(encoding="utf-8").splitlines():
            event = json.loads(line)
            if event.get("type") == "message_end" and event.get("message", {}).get("role") == "assistant":
                assistant.append(event["message"])
            if event.get("type") == "tool_execution_start":
                tools.append(event.get("toolName"))
            assert not (event.get("type") == "tool_execution_end" and event.get("isError"))
        assert assistant and all(m.get("model") == "gpt-6-luna" for m in assistant)
        assert set(tools) <= {"write"}
        rewards = (result.get("verifier_result") or {}).get("rewards") or {}
        usage = result.get("agent_result") or {}
        total = usage.get("n_input_tokens") + usage.get("n_output_tokens") if usage.get("n_input_tokens") is not None and usage.get("n_output_tokens") is not None else None
        rows.append({
            "phase": phase, "task": result["task_name"],
            "skill_md_sha256": integrity["files"]["SKILL.md"],
            "reward": evaluation.get("reward"), "artifact_valid": rewards.get("artifact_valid"),
            "evaluable": evaluation["evaluable"], "execution_error": (result.get("exception_info") or {}).get("exception_type"),
            "tokens": total, "native_result": str(result_path.relative_to(STUDY)).replace("\\", "/"),
            "native_result_sha256": hashlib.sha256(result_path.read_bytes()).hexdigest(),
        })
    real = [row for row in rows if not row.get("candidate_rejected")]
    private = [row for row in real if row["phase"] != "development"]
    additional_gate_passed = bool(private) and all(row["artifact_valid"] == 1 and row["evaluable"] and row["execution_error"] is None for row in private)
    resources = {}
    for phase in sorted({row["phase"] for row in real}):
        phase_rows = [row for row in real if row["phase"] == phase]
        observed = [row["tokens"] for row in phase_rows if row["tokens"] is not None]
        resources[phase] = {"trials": len(phase_rows), "token_coverage": len(observed), "total_tokens": sum(observed) if len(observed) == len(phase_rows) else None}
    reflection = [read(p) for p in sorted((STUDY / "reflection").glob("call-*/receipt.json"))]
    summary = {
        "schema_version": 1, "study": STUDY.name, "complete": True,
        "model": run["model"], "harbor": run["harborVersion"], "gepa": run["gepaVersion"],
        "optimizer": run["gepa"], "validation": run["validation"], "holdout": run["holdout"],
        "baseline_files": baseline, "candidate_files": candidate,
        "phase_counts": dict(Counter(row["phase"] for row in rows)),
        "native_trials": len(real), "candidate_rejection_evaluations": len(rows) - len(real),
        "all_runtime_input_integrity_model_checks_passed": True,
        "additional_private_artifact_gate_passed": additional_gate_passed,
        "eligible_for_manual_promotion_review": run["holdout"]["promoted"] and additional_gate_passed,
        "resources": resources, "reflection_calls": len(reflection),
        "reflection_total_tokens": sum(r["usage"]["totalTokens"] for r in reflection) if all(r.get("usage", {}).get("totalTokens") is not None for r in reflection) else None,
        "cost_usd": None, "semantic_accuracy": None, "rows": rows,
    }
    destination = STUDY / "audit.json"
    with destination.open("x", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=2)
    print(json.dumps({key: value for key, value in summary.items() if key not in {"rows", "validation", "holdout", "baseline_files", "candidate_files"}}, indent=2))


if __name__ == "__main__":
    main()
