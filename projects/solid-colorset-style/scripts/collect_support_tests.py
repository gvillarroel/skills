#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Summarize observed support regression counts from retained command logs."""
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[3]


def main():
    report = json.loads((ROOT / "projects/colorset-audit/artifacts/data/support-tests.json").read_text())
    for row in report["checks"]:
        log = (ROOT / row["log"]).read_text(encoding="utf-8")
        count = re.search(r"Ran (\d+) tests?", log)
        if not count:
            raise RuntimeError(f"No test count in {row['log']}")
        row["tests"] = int(count.group(1))
    report.update(date="2026-10-03", suiteCount=len(report["checks"]),
                  unitCaseCount=sum(row["tests"] for row in report["checks"]))
    destination = ROOT / "evaluations/solid-colorset-style/support-tests-20261003.json"
    destination.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: value for key, value in report.items() if key != "checks"}, indent=2))
    raise SystemExit(0 if report["ok"] else 1)


if __name__ == "__main__":
    main()
