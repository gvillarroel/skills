#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Expose literal retained tool failures without changing their classification."""
import argparse
import json
from pathlib import Path


def texts(value):
    if isinstance(value, dict):
        return [str(value["text"])] if "text" in value else sum((texts(item) for item in value.values()), [])
    if isinstance(value, list):
        return sum((texts(item) for item in value), [])
    return []


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("run_ids", nargs="+")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[2]
    for run_id in args.run_ids:
        run = root / "evaluations/runs" / run_id
        failures = []
        for line, source in enumerate((run / "events.jsonl").read_text(encoding="utf-8").splitlines(), 1):
            event = json.loads(source)
            if event.get("type") == "tool_execution_end" and event.get("isError") is True:
                failures.append({"line": line, "tool": event.get("toolName"), "text": texts(event.get("result", {}))})
        result = {"runId": run_id, "failures": failures}
        (run / "retained-tool-errors.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(result))


if __name__ == "__main__":
    main()
