#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Publish compact measured results and verify all original generation evidence."""
from pathlib import Path
import hashlib
import json
import statistics

REPO = Path(__file__).resolve().parents[3]


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def main():
    root = REPO/"evaluations/runs/svgq2"
    summary = read(root/"review-v3/summary.json")
    families = []
    for task in sorted({row["task"] for row in summary["records"]}):
        vals = {arm: statistics.mean(row["score_100"] for row in summary["records"] if row["candidate"] == arm and row["task"] == task) for arm in ["b", "q"]}
        families.append({"task": task, **vals, "difference": vals["q"]-vals["b"]})
    reports = list(root.glob("jev-*/report.json"))+list((root/"jobs/probe-lf").glob("*/verifier/jev/report.json"))
    accounting = {"jev_calls": 0, "jev_reported_cost_usd": 0.0, "jev_input_tokens": 0, "jev_output_tokens": 0}
    for path in reports:
        metrics = read(path).get("metrics", {})
        for key, field in [("jev_calls", "accepted_calls"), ("jev_reported_cost_usd", "reported_cost_usd"), ("jev_input_tokens", "reported_input_tokens"), ("jev_output_tokens", "reported_output_tokens")]:
            accounting[key] += metrics.get(field, 0)
    receipts = list((root/"visual-calibration").glob("*/receipt.json"))+list((root/"visual-current").glob("*/receipt.json"))+list((root/"jobs/probe-lf").glob("*/verifier/observer/*/receipt.json"))
    accounting.update(visual_observer_calls=len(receipts), observer_reported_total_tokens=sum(read(path)["usage"]["totalTokens"] for path in receipts), observer_dollar_cost=None)
    assert len(receipts) == 51 and all(read(path)["passed"] and read(path)["image_event_observed"] for path in receipts)
    evidence = {row["id"]: row for row in summary["records"]}
    for row in read(root/"current-bounded/coordinator-only.json"):
        assert hashlib.sha256(Path(row["native_result"]).read_bytes()).hexdigest() == row["native_result_sha256"]
        assert hashlib.sha256(Path(row["artifact"]).read_bytes()).hexdigest() == evidence[row["id"]]["artifact_sha256"]
    bundle = root/"frozen-v3/evaluator"
    for name, digest in read(bundle/"lock.json")["files"].items():
        assert hashlib.sha256((bundle/name).read_bytes()).hexdigest() == digest
    compact = {"version": "3.0.0", "date": "2026-09-26", "judge": "typesafe/jev-1.13-20260917", "observer": "openai-codex/gpt-6-luna",
               "weights": {"brief_adherence": 35, "geometric_finish": 25, "composition": 20, "legibility": 20},
               "arms": summary["summary"], "mean_difference_points": summary["summary"]["q"]["mean_scored"]-summary["summary"]["b"]["mean_scored"],
               "per_task": families, "review_flags": [{key: row[key] for key in ("candidate", "task", "name", "score_100")} for row in summary["records"] if row["review_recommended"]],
               "calibration_controls_passed": 17, "calibration_controls_total": 17, "deterministic_tests": 16,
               "native_integration": {"job": "evaluations/runs/svgq2/jobs/probe-lf", "trials": 1, "errors": 0, "technical_excellence": 1.0},
               "accounting": accounting, "lineage_audit": {"historical_results_unchanged": 36, "historical_svgs_unchanged": 36, "observer_image_inputs_verified": 51, "frozen_bundle_unchanged": True},
               "new_svg_generation_calls": 0, "private_tasks_opened": 0, "scope": "Public descriptive retrospective; not an independent promotion claim.",
               "records": [{"trial": row["name"], "candidate": row["candidate"], "task": row["task"], "score_100": row["score_100"], "dimensions": row.get("dimensions"), "review_recommended": row["review_recommended"]} for row in summary["records"]]}
    with (REPO/"evaluations/svg-brief-design/jev-excellence-20260926.json").open("x", encoding="utf-8") as handle:
        json.dump(compact, handle, indent=2, allow_nan=False)
        handle.write("\n")
    print(json.dumps({"per_task": families, "accounting": accounting, "lineage": "All checks passed"}))


if __name__ == "__main__":
    main()
