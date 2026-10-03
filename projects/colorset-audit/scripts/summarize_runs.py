#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Summarize retained colorset forward tests without printing full traces."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
for directory in sorted((ROOT / "evaluations/runs").glob("*colorset*")):
    if "20261002" not in directory.name:
        continue
    result_path = directory / "evaluation-result.json"
    if not result_path.is_file():
        continue
    result = json.loads(result_path.read_text(encoding="utf-8"))
    print(directory.name, "PASS" if result.get("passed") else "FAIL", result.get("gates"))
    if not result.get("passed"):
        events_path = directory / "event-check.json"
        if events_path.exists():
            check = json.loads(events_path.read_text(encoding="utf-8"))
            for call in check.get("calls", []):
                if call.get("isError"):
                    print("  TOOL ERROR", (call.get("command") or call.get("path") or "")[:400])
            for key, value in check.items():
                if key not in {"calls", "observedModels", "readSurface"} and ("error" in key.lower() or "fail" in key.lower()):
                    print(" ", key, str(value)[:350])
        for line in (directory / "events.jsonl").read_text(encoding="utf-8").splitlines():
            event = json.loads(line)
            if event.get("type") == "tool_execution_end" and event.get("isError"):
                print("  ERROR RESULT", str(event.get("result"))[:600])
