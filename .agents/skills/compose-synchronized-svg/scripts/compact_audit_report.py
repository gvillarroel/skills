#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

"""Compact a synchronized-SVG browser report without hiding failures."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def collection_size(value: Any) -> int:
    if value is None:
        return 0
    if isinstance(value, (dict, list, tuple, set)):
        return len(value)
    return 1


def compact_report(report: dict[str, Any]) -> dict[str, Any]:
    """Keep release evidence compact while retaining every failing check in full."""

    checks = report.get("checks", [])
    if not isinstance(checks, list):
        checks = []
    valid_checks = [item for item in checks if isinstance(item, dict)]
    passed_ids = [str(item.get("id", "unknown")) for item in valid_checks if item.get("ok") is True]
    failed_checks = [item for item in valid_checks if item.get("ok") is not True]

    snapshots = report.get("snapshots", {})
    if not isinstance(snapshots, dict):
        snapshots = {}
    snapshot_summary = {
        str(key): collection_size(value)
        for key, value in snapshots.items()
    }

    return {
        "ok": report.get("ok") is True,
        "artifact": report.get("artifact"),
        "report": report.get("report"),
        "screenshot": report.get("screenshot"),
        "failures": report.get("failures", []),
        "warnings": report.get("warnings", []),
        "browserErrors": report.get("browserErrors", {}),
        "metrics": report.get("metrics", {}),
        "checkSummary": {
            "total": len(valid_checks),
            "passed": len(passed_ids),
            "failed": len(failed_checks),
            "passedIds": passed_ids,
            "failedIds": [str(item.get("id", "unknown")) for item in failed_checks],
        },
        "failedChecks": failed_checks,
        "snapshotSummary": snapshot_summary,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Compact a full synchronized-SVG browser audit while retaining failures."
    )
    parser.add_argument("report", type=Path, help="Full browser-audit JSON report")
    parser.add_argument("--output", type=Path, required=True, help="Compact JSON output path")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    source = args.report.resolve()
    output = args.output.resolve()
    if source == output:
        raise SystemExit("Input and output paths must be distinct.")
    report = json.loads(source.read_text(encoding="utf-8"))
    if not isinstance(report, dict):
        raise SystemExit("Browser audit must contain one JSON object.")
    compact = compact_report(report)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(compact, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(f"Compact browser audit: {'PASS' if compact['ok'] else 'FAIL'}")
    print(f"Output: {output}")
    return 0 if compact["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
