#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Print strict trial findings with the failed command and bounded diagnostics."""
from pathlib import Path
import json
import sys

sys.stdout.reconfigure(encoding="utf-8")
root = Path(__file__).resolve().parents[3]
for name in sys.argv[1:]:
    run = root / "evaluations/runs" / name
    report = json.loads((run / "event-check.json").read_text(encoding="utf-8"))
    print(name, report["findings"])
    records = (run / "events.jsonl").read_text(encoding="utf-8").splitlines()
    for finding in report["findings"]:
        if "line" not in finding:
            continue
        line = finding["line"]
        calls = [c for c in report["calls"] if c["line"] == line]
        print(json.dumps(calls, ensure_ascii=False))
        record = json.loads(records[line - 1])
        contents = record.get("result", {}).get("content", [])
        print("\n".join(c.get("text", "")[:1600] for c in contents if c.get("type") == "text"))
