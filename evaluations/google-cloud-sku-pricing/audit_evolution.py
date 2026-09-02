#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Audit pricing evolution correctness, provenance, and holdout isolation."""

from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import sqlite3
import sys
from typing import Any, Iterable


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"Expected a JSON object: {path}")
    return value


def phase_for(path: Path, run_root: Path) -> str:
    relative = path.relative_to(run_root / "harbor-trials")
    return relative.parts[0]


def iter_json_events(path: Path) -> Iterable[dict[str, Any]]:
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(event, dict):
            yield event


def nested_values(value: Any) -> Iterable[Any]:
    yield value
    if isinstance(value, dict):
        for child in value.values():
            yield from nested_values(child)
    elif isinstance(value, list):
        for child in value:
            yield from nested_values(child)


def event_uses_tool(event: dict[str, Any]) -> bool:
    for value in nested_values(event):
        if not isinstance(value, dict):
            continue
        event_type = str(value.get("type", "")).lower().replace("_", "")
        role = str(value.get("role", "")).lower()
        if event_type.startswith("tool") or role in {"tool", "toolresult"}:
            return True
    return False


def event_is_model_error(event: dict[str, Any]) -> bool:
    for value in nested_values(event):
        if not isinstance(value, dict):
            continue
        if str(value.get("stopReason", "")).lower() == "error":
            return True
        if value.get("errorMessage"):
            return True
    return False


def scan_event_logs(paths: Iterable[Path]) -> dict[str, int]:
    tool_events = 0
    error_events = 0
    files_with_errors = 0
    for path in paths:
        file_has_error = False
        for event in iter_json_events(path):
            if event_uses_tool(event):
                tool_events += 1
            if event_is_model_error(event):
                error_events += 1
                file_has_error = True
        files_with_errors += int(file_has_error)
    return {
        "toolEvents": tool_events,
        "modelErrorEvents": error_events,
        "filesWithModelErrors": files_with_errors,
    }


def normalized_text(path: Path) -> str:
    return "\n".join(path.read_text(encoding="utf-8").splitlines()).strip()


def audit(run_root: Path, benchmark: Path, source_skill: Path) -> dict[str, Any]:
    findings: list[str] = []
    run = read_json(run_root / "run.json")
    evaluation_paths = sorted(run_root.glob("harbor-trials/*/*/evaluation.json"))
    evaluations = [(phase_for(path, run_root), read_json(path)) for path in evaluation_paths]
    phase_counts = Counter(phase for phase, _ in evaluations)
    if phase_counts.get("development", 0) < 2:
        findings.append(f"development-trial-count:{phase_counts.get('development', 0)}")
    for phase in ("holdout-baseline", "holdout-candidate"):
        if phase_counts.get(phase, 0) != 4:
            findings.append(f"{phase}-trial-count:{phase_counts.get(phase, 0)}")
    for phase, row in evaluations:
        if row.get("reward") != 1.0:
            findings.append(f"reward:{phase}/{row.get('taskName')}")
        if row.get("error"):
            findings.append(f"trial-error:{phase}/{row.get('taskName')}")
        if (row.get("skillProvenance") or {}).get("status") != "verified":
            findings.append(f"provenance:{phase}/{row.get('taskName')}")

    verification_paths = sorted(run_root.glob("harbor-trials/*/*/trials/*/verifier/verification.json"))
    verified_answers = 0
    covered_question_ids: set[str] = set()
    failed_verifications = 0
    for path in verification_paths:
        verification = read_json(path)
        relative = path.relative_to(run_root)
        if not verification.get("ok") or verification.get("reward") != 1.0:
            findings.append(f"verification:{relative}")
            failed_verifications += 1
        if verification.get("mismatches") or verification.get("envelopeFindings"):
            findings.append(f"verification-findings:{relative}")
        correct = int(verification.get("correct", 0))
        total = int(verification.get("total", 0))
        if correct != 10 or total != 10:
            findings.append(f"verification-count:{relative}")
        verified_answers += correct
        covered_question_ids.update(str(value) for value in verification.get("correctIds", []))

    connection = sqlite3.connect(benchmark)
    connection.row_factory = sqlite3.Row
    try:
        benchmark_rows = list(
            connection.execute(
                "SELECT question_id, split, prompt, source_skus_json FROM questions ORDER BY question_id"
            )
        )
    finally:
        connection.close()
    expected_ids = {row["question_id"] for row in benchmark_rows}
    if covered_question_ids != expected_ids:
        findings.append(f"question-coverage:{len(covered_question_ids)}/{len(expected_ids)}")
    if len(expected_ids) != 100:
        findings.append(f"benchmark-question-count:{len(expected_ids)}")
    expected_answer_evaluations = 10 * len(verification_paths)
    if verified_answers != expected_answer_evaluations:
        findings.append(
            f"verified-answer-evaluations:{verified_answers}/{expected_answer_evaluations}"
        )

    holdout_rows = [row for row in benchmark_rows if row["split"] == "holdout"]
    forbidden_tokens: set[str] = {row["question_id"] for row in holdout_rows}
    forbidden_tokens.update(row["prompt"] for row in holdout_rows)
    for row in holdout_rows:
        forbidden_tokens.update(json.loads(row["source_skus_json"]))
    reflection_files = sorted(
        path
        for path in (run_root / "reflection-calls").rglob("*")
        if path.is_file() and ".git" not in path.parts
    )
    reflection_text = "\n".join(
        path.read_text(encoding="utf-8", errors="replace") for path in reflection_files
    )
    leaked_tokens = sorted(token for token in forbidden_tokens if token and token in reflection_text)
    if leaked_tokens:
        findings.append(f"holdout-leak:{len(leaked_tokens)}")

    task_event_paths = sorted(run_root.glob("harbor-trials/*/*/trials/*/agent/pi.txt"))
    reflection_event_paths = sorted(run_root.glob("reflection-calls/*/events.jsonl"))
    task_events = scan_event_logs(task_event_paths)
    reflection_events = scan_event_logs(reflection_event_paths)
    if task_events["filesWithModelErrors"]:
        findings.append(f"task-model-error-files:{task_events['filesWithModelErrors']}")
    if reflection_events["filesWithModelErrors"]:
        findings.append(
            f"reflection-model-error-files:{reflection_events['filesWithModelErrors']}"
        )
    if reflection_events["toolEvents"]:
        findings.append(f"reflection-tool-events:{reflection_events['toolEvents']}")

    baseline_snapshot = Path(str(run.get("baselineSnapshot") or source_skill)).resolve()
    source_text = normalized_text(baseline_snapshot / "SKILL.md")
    candidate_text = normalized_text(run_root / "candidate-skill" / "SKILL.md")
    selected_candidate_changed = source_text != candidate_text
    holdout = run.get("holdout") or {}
    baseline_mean = holdout.get("baselineMeanReward")
    candidate_mean = holdout.get("candidateMeanReward")
    promoted = bool(holdout.get("promoted"))
    if baseline_mean != 1.0 or candidate_mean != 1.0:
        findings.append(f"holdout-score:{baseline_mean}/{candidate_mean}")
    candidate_verification_failures = sum(
        row.get("reward") != 1.0 or bool(row.get("error"))
        for phase, row in evaluations
        if phase == "holdout-candidate"
    )
    candidate_model_error_files = sum(
        1
        for path in task_event_paths
        if "holdout-candidate" in path.parts
        and any(event_is_model_error(event) for event in iter_json_events(path))
    )
    recomputed_candidate_failures = max(
        candidate_verification_failures, candidate_model_error_files
    )
    if recomputed_candidate_failures:
        findings.append(f"holdout-candidate-failures:{recomputed_candidate_failures}")
    if promoted and (failed_verifications or recomputed_candidate_failures or candidate_mean != 1.0):
        findings.append("unsafe-promotion")
    if selected_candidate_changed and not promoted:
        findings.append("changed-candidate-not-promoted")

    return {
        "ok": not findings,
        "runId": run.get("evolutionId"),
        "snapshotId": "gcp-pricing-636387a8dd1a10dc",
        "trials": len(evaluations),
        "phaseCounts": dict(sorted(phase_counts.items())),
        "verificationFiles": len(verification_paths),
        "failedVerifications": failed_verifications,
        "verifiedAnswerEvaluations": verified_answers,
        "expectedAnswerEvaluations": expected_answer_evaluations,
        "uniqueQuestionCoverage": len(covered_question_ids),
        "uniqueHoldoutQuestions": len(holdout_rows),
        "reflectionFiles": len(reflection_files),
        "holdoutLeakTokens": len(leaked_tokens),
        "taskEventAudit": task_events,
        "reflectionEventAudit": reflection_events,
        "selectedCandidateChanged": selected_candidate_changed,
        "baselineSnapshot": str(baseline_snapshot),
        "reportedPromoted": promoted,
        "baselineHoldoutMean": baseline_mean,
        "candidateHoldoutMean": candidate_mean,
        "recomputedCandidateFailures": recomputed_candidate_failures,
        "findings": findings,
    }


def build_parser() -> argparse.ArgumentParser:
    repository_root = Path(__file__).resolve().parents[2]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--run-root",
        type=Path,
        default=repository_root
        / "evaluations"
        / "runs"
        / "google-cloud-sku-pricing-evolution-20260825-v5-clean",
    )
    parser.add_argument(
        "--benchmark",
        type=Path,
        default=repository_root
        / "evaluations"
        / "datasets"
        / "google-cloud-sku-pricing-100"
        / "processed"
        / "v2"
        / "benchmark.sqlite",
    )
    parser.add_argument(
        "--source-skill",
        type=Path,
        default=repository_root / "skills" / "google-cloud-sku-pricing",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    result = audit(args.run_root.resolve(), args.benchmark.resolve(), args.source_skill.resolve())
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
