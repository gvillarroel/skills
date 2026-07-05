#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

from __future__ import annotations

import argparse
import json
import re
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
    parser.add_argument("--output", type=Path, help="Optional JSON summary path.")
    parser.add_argument("--fail-on-tool-error", action="store_true", help="Exit nonzero when any tool call reports isError.")
    parser.add_argument(
        "--require-read",
        action="append",
        default=[],
        help="Require an exact read-tool path. May be repeated.",
    )
    parser.add_argument(
        "--require-read-regex",
        action="append",
        default=[],
        help="Require at least one read-tool path matching this regex. May be repeated.",
    )
    parser.add_argument(
        "--allow-read",
        action="append",
        default=[],
        help="Allow an exact read-tool path even when it matches a forbidden regex. May be repeated.",
    )
    parser.add_argument(
        "--forbid-read-regex",
        action="append",
        default=[],
        help="Fail when a read-tool path matches this regex, unless the path is explicitly allowed. May be repeated.",
    )
    parser.add_argument(
        "--forbid-command-regex",
        action="append",
        default=[],
        help="Fail when a shell command or other tool command string matches this regex. May be repeated.",
    )
    args = parser.parse_args()

    tool_counts: Counter[str] = Counter()
    path_counts: Counter[str] = Counter()
    path_bytes: Counter[str] = Counter()
    read_paths: Counter[str] = Counter()
    calls: list[dict[str, Any]] = []
    starts: dict[str, dict[str, Any]] = {}
    findings: list[dict[str, Any]] = []
    forbidden_read_patterns = [re.compile(pattern) for pattern in args.forbid_read_regex]
    forbidden_command_patterns = [re.compile(pattern) for pattern in args.forbid_command_regex]
    required_read_patterns = [re.compile(pattern) for pattern in args.require_read_regex]
    allowed_reads = set(args.allow_read)

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
        command = tool_args.get("command") if isinstance(tool_args, dict) else None
        size = result_size(event.get("result"))
        if isinstance(command, str):
            for pattern in forbidden_command_patterns:
                if pattern.search(command):
                    findings.append(
                        {
                            "code": "forbidden-command",
                            "line": line_number,
                            "tool": tool,
                            "pattern": pattern.pattern,
                            "commandSample": command[:240],
                        }
                    )
                    break
        if path:
            path_counts[path] += 1
            path_bytes[path] += size
            if tool == "read":
                read_paths[path] += 1
                if path not in allowed_reads:
                    for pattern in forbidden_read_patterns:
                        if pattern.search(path):
                            findings.append(
                                {
                                    "code": "forbidden-read",
                                    "line": line_number,
                                    "path": path,
                                    "pattern": pattern.pattern,
                                }
                            )
                            break
        if args.fail_on_tool_error and event.get("isError"):
            findings.append({"code": "tool-error", "line": line_number, "tool": tool, "path": path})
        calls.append(
            {
                "line": line_number,
                "tool": tool,
                "path": path,
                "command": command[:240] if isinstance(command, str) else None,
                "isError": bool(event.get("isError")),
                "resultBytes": size,
            }
        )

    for required_path in args.require_read:
        if read_paths[required_path] == 0:
            findings.append({"code": "missing-required-read", "path": required_path})
    for pattern in required_read_patterns:
        if not any(pattern.search(path) for path in read_paths):
            findings.append({"code": "missing-required-read-regex", "pattern": pattern.pattern})

    summary = {
        "passed": not findings,
        "toolCounts": dict(tool_counts),
        "paths": [
            {"path": path, "calls": path_counts[path], "resultBytes": path_bytes[path]}
            for path, _ in path_counts.most_common()
        ],
        "readPaths": [
            {"path": path, "calls": read_paths[path], "resultBytes": path_bytes[path]}
            for path, _ in read_paths.most_common()
        ],
        "calls": calls,
        "findings": findings,
    }
    text = json.dumps(summary, indent=2, ensure_ascii=False)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0 if not findings else 1


if __name__ == "__main__":
    raise SystemExit(main())
