#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any


def path_from_args(args: Any) -> str | None:
    if not isinstance(args, dict):
        return None
    for key in ("path", "file", "filePath", "target", "pattern"):
        value = args.get(key)
        if isinstance(value, str):
            return value
    return None


def result_size(result: Any) -> int:
    if result is None:
        return 0
    if isinstance(result, str):
        return len(result)
    try:
        return len(json.dumps(result, ensure_ascii=False))
    except TypeError:
        return len(str(result))


def main() -> int:
    parser = argparse.ArgumentParser(description="Summarize pi JSON event tool calls and file-like reads.")
    parser.add_argument("events", type=Path, help="pi --mode json output JSONL file.")
    args = parser.parse_args()

    tool_counts: Counter[str] = Counter()
    path_counts: Counter[str] = Counter()
    path_bytes: Counter[str] = Counter()
    calls: list[dict[str, Any]] = []
    starts: dict[str, dict[str, Any]] = {}

    for line_number, line in enumerate(args.events.read_text(encoding="utf-8", errors="replace").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if event.get("type") == "tool_execution_start":
            starts[str(event.get("toolCallId", ""))] = event
            continue

        if event.get("type") != "tool_execution_end":
            continue

        tool = str(event.get("toolName", ""))
        tool_counts[tool] += 1
        start = starts.get(str(event.get("toolCallId", "")), {})
        tool_args = start.get("args")
        path = path_from_args(tool_args)
        size = result_size(event.get("result"))
        if path:
            path_counts[path] += 1
            path_bytes[path] += size
        calls.append(
            {
                "line": line_number,
                "tool": tool,
                "path": path,
                "isError": bool(event.get("isError")),
                "resultBytes": size,
            }
        )

    summary = {
        "toolCounts": dict(tool_counts),
        "paths": [
            {"path": path, "calls": path_counts[path], "resultBytes": path_bytes[path]}
            for path, _ in path_counts.most_common()
        ],
        "calls": calls,
    }
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
