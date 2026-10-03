#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Independently inspect synthetic density-case artifacts and replay frozen tools."""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path

METRICS = ("named_records", "typed_relations", "temporal_anchors", "context_statements")
COUNTS = {
    "reference": [[120, 128], [90, 94], [190, 200], [145, 150]],
    "draft-a": [[180, 190], [110, 115], [250, 260], [92, 104]],
    "draft-b": [[135, 150], [98, 110], [205, 220], [170, 190]],
    "draft-c": [[130, 130], [100, 100], [205, 205], [155, 155]],
}


def expected_profile(name: str, control: bool) -> dict:
    intervals = [[128, 128], [94, 94], [200, 200], [150, 150]] if control else COUNTS[name]
    letter = "a" if control else dict(zip(COUNTS, "abcd"))[name]
    return {
        "schema_version": 1, "family": "timeline",
        "comparison_basis": "same-full-poster-area",
        "counting_protocol": "usefulcharts-knowledge-v1", "coverage": "full-body",
        "image_sha256": letter*64, "method": "ocr" if name == "draft-b" else "manual-census",
        "census_review": "pending" if name == "draft-b" else "pass",
        "semantic_review": "pending" if name == "draft-b" else "pass",
        "legibility_review": "fail" if name == "draft-c" else "pass",
        "counts": dict(zip(METRICS, intervals)),
    }


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def inspect(run: Path, control: bool) -> dict:
    workspace = run / "workspace"
    output = run / "independent-density"
    output.mkdir(parents=True, exist_ok=True)
    findings = []
    names = ("reference", "candidate") if control else tuple(COUNTS)
    profiles = {name: workspace / ("" if control else "result") / f"{name}.json" for name in names}
    before = {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in profiles.values()}
    for name, path in profiles.items():
        actual = read_json(path)
        for key, expected in expected_profile(name, control).items():
            if actual.get(key) != expected:
                findings.append({"code": "profile-value-mismatch", "profile": name,
                                 "field": key, "expected": expected, "actual": actual.get(key)})
        if "synthetic" not in str(actual.get("ledger", "")).lower():
            findings.append({"code": "synthetic-ledger-missing", "profile": name})
    decisions = []
    for name in names[1:]:
        replay_path = output / f"{name}.json"
        command = ["uv", "run", "--script", str(workspace / "skills/usefulcharts-style/scripts/compare_density.py"),
                   str(profiles["reference"]), str(profiles[name]), "--report", str(replay_path)]
        completed = subprocess.run(command, capture_output=True, text=True, encoding="utf-8")
        (output / f"{name}-stderr.txt").write_text(completed.stderr, encoding="utf-8")
        if completed.returncode:
            findings.append({"code": "replay-failed", "candidate": name, "exit_code": completed.returncode})
            continue
        replay = read_json(replay_path)
        delivered_path = workspace / "result" / ("density.json" if control else f"{name}-density.json")
        delivered = read_json(delivered_path)
        if delivered != replay:
            findings.append({"code": "report-not-equal-to-replay", "candidate": name})
        expected_status = "meets-measured-floor" if control else "below-reference" if name == "draft-a" else "needs-evidence"
        if replay.get("status") != expected_status or replay.get("passes_measured_floor") is not control:
            findings.append({"code": "decision-mismatch", "candidate": name, "expected": expected_status})
        if replay.get("minimum_ratio") != 1:
            findings.append({"code": "minimum-changed", "candidate": name})
        shortfalls = {c["metric"]: c.get("shortfall") for c in replay.get("checks", [])}
        expected_shortfalls = {metric: 58 if name == "draft-a" and metric == "context_statements" else 0
                               for metric in METRICS}
        if shortfalls != expected_shortfalls:
            findings.append({"code": "shortfall-mismatch", "candidate": name,
                             "expected": expected_shortfalls, "actual": shortfalls})
        decisions.append({"candidate": name, "replay_status": replay["status"],
                          "delivered_equals_replay": delivered == replay, "shortfalls": shortfalls,
                          "command": command})
    after = {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in profiles.values()}
    if before != after:
        findings.append({"code": "input-mutated-by-replay"})
    result = {"run": run.name, "case": "command-control" if control else "naturalistic",
              "passed_machine_contract": not findings, "findings": findings, "decisions": decisions,
              "inputs_unchanged": before == after,
              "prose_review": "Independent human review still required; this script does not judge prose or aesthetics."}
    (output / "inspection.json").write_text(json.dumps(result, indent=2)+"\n", encoding="utf-8")
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("runs", type=Path, nargs="+")
    parser.add_argument("--control", action="store_true")
    args = parser.parse_args()
    passed = True
    for run in args.runs:
        result = inspect(run.resolve(), args.control)
        print(json.dumps({key: result[key] for key in ("run", "case", "passed_machine_contract", "findings")}))
        passed = passed and result["passed_machine_contract"]
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
