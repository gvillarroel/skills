#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Verify decision types and exact evidence sets for the attribution probe."""

from argparse import ArgumentParser
import json
from pathlib import Path


EXPECTED = {
    "global": ("direct", {"s1", "s5"}),
    "local": ("derived", {"s1"}),
    "returned": ("joint", {"s3", "s4"}),
    "layer": ("unsupported", set()),
    "presence": ("unsupported", set()),
}


def grade(workspace):
    answer = json.loads((workspace / "findings.json").read_bytes())
    if not isinstance(answer, dict):
        return ["expected an object of attribution decisions"]
    failures = []
    for case, (status, locators) in EXPECTED.items():
        row = answer.get(case, {})
        if not isinstance(row, dict) or row.get("status") != status:
            failures.append(f"{case}: incorrect attribution status")
            continue
        actual = row.get("locators")
        if (not isinstance(actual, list) or len(actual) != len(locators)
                or not all(isinstance(item, str) for item in actual) or set(actual) != locators):
            failures.append(f"{case}: incorrect source support set")
        elif not isinstance(row.get("rationale"), str) or not row["rationale"].strip():
            failures.append(f"{case}: missing rationale")
    if set(answer) != set(EXPECTED):
        failures.append("unexpected case roster")
    if {path.name for path in workspace.iterdir()} != {"skills", "findings.json"}:
        failures.append("unexpected output artifact")
    return failures


if __name__ == "__main__":
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("workspace", type=Path)
    args = parser.parse_args()
    failures = grade(args.workspace)
    print(json.dumps({"passed": not failures, "expected_cases": len(EXPECTED), "findings": failures}, indent=2))
    raise SystemExit(bool(failures))
