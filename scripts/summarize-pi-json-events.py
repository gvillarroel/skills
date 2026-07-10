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


def policy_path(path: str, events_path: Path) -> str:
    candidate = Path(path)
    workspace = events_path.parent / "workspace"
    resolved = candidate.resolve() if candidate.is_absolute() else (workspace / candidate).resolve()
    try:
        return resolved.relative_to(workspace.resolve()).as_posix()
    except ValueError:
        prompt_path = (workspace.parent / "prompt.md").resolve()
        if resolved == prompt_path:
            return "../prompt.md"
        return resolved.as_posix()


def result_size(result: Any) -> int:
    if result is None:
        return 0
    if isinstance(result, str):
        return len(result.encode("utf-8"))
    try:
        return len(json.dumps(result, ensure_ascii=False).encode("utf-8"))
    except TypeError:
        return len(str(result).encode("utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser(description="Summarize pi JSON event tool calls and file-like reads.")
    parser.add_argument("events", type=Path, help="pi --mode json output JSONL file.")
    parser.add_argument("--output", type=Path, help="Optional JSON summary path.")
    parser.add_argument("--fail-on-tool-error", action="store_true", help="Exit nonzero when any tool call reports isError.")
    parser.add_argument("--fail-on-invalid-json", action="store_true", help="Exit nonzero when a non-empty JSONL line is invalid JSON.")
    parser.add_argument("--require-tool-call", action="store_true", help="Exit nonzero when the trace contains no completed tool calls.")
    parser.add_argument(
        "--require-model",
        help="Require this to be the only observed assistant model, for example gpt-5.3-codex-spark.",
    )
    parser.add_argument(
        "--max-read-result-bytes",
        type=int,
        help="Fail when any completed read tool call returns more than this many serialized bytes.",
    )
    parser.add_argument(
        "--max-total-read-result-bytes",
        type=int,
        help="Fail when all completed read calls return more than this many serialized bytes in total.",
    )
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

    if not args.events.is_file():
        parser.error(f"events file not found: {args.events}")
    for option_name, value in (
        ("--max-read-result-bytes", args.max_read_result_bytes),
        ("--max-total-read-result-bytes", args.max_total_read_result_bytes),
    ):
        if value is not None and value < 0:
            parser.error(f"{option_name} must be zero or greater")
    for option_name, patterns in (
        ("--forbid-read-regex", args.forbid_read_regex),
        ("--forbid-command-regex", args.forbid_command_regex),
        ("--require-read-regex", args.require_read_regex),
    ):
        for pattern in patterns:
            try:
                re.compile(pattern)
            except re.error as error:
                parser.error(f"invalid {option_name} value {pattern!r}: {error}")

    tool_counts: Counter[str] = Counter()
    path_counts: Counter[str] = Counter()
    path_bytes: Counter[str] = Counter()
    read_paths: Counter[str] = Counter()
    policy_read_paths: Counter[str] = Counter()
    read_path_bytes: Counter[str] = Counter()
    model_counts: Counter[str] = Counter()
    provider_counts: Counter[str] = Counter()
    usage_totals: Counter[str] = Counter()
    calls: list[dict[str, Any]] = []
    starts: dict[str, dict[str, Any]] = {}
    findings: list[dict[str, Any]] = []
    invalid_json_lines: list[int] = []
    invalid_event_lines: list[int] = []
    session: dict[str, Any] | None = None
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
            invalid_json_lines.append(line_number)
            continue
        if not isinstance(event, dict):
            invalid_event_lines.append(line_number)
            continue
        if event.get("type") == "session" and session is None:
            session = {
                "version": event.get("version"),
                "id": event.get("id"),
                "cwd": event.get("cwd"),
            }
        if event.get("type") == "message_end":
            message = event.get("message")
            if isinstance(message, dict) and message.get("role") == "assistant":
                model = message.get("model")
                provider = message.get("provider")
                if isinstance(model, str):
                    model_counts[model] += 1
                if isinstance(provider, str):
                    provider_counts[provider] += 1
                usage = message.get("usage")
                if isinstance(usage, dict):
                    for key in ("input", "output", "cacheRead", "cacheWrite", "totalTokens"):
                        value = usage.get(key)
                        if isinstance(value, (int, float)):
                            usage_totals[key] += value
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
            normalized_path = policy_path(path, args.events)
            path_counts[path] += 1
            path_bytes[path] += size
            if tool == "read":
                read_paths[path] += 1
                policy_read_paths[normalized_path] += 1
                read_path_bytes[path] += size
                if args.max_read_result_bytes is not None and size > args.max_read_result_bytes:
                    findings.append(
                        {
                            "code": "read-result-too-large",
                            "line": line_number,
                            "path": path,
                            "resultBytes": size,
                            "maximumBytes": args.max_read_result_bytes,
                        }
                    )
                if path not in allowed_reads and normalized_path not in allowed_reads:
                    for pattern in forbidden_read_patterns:
                        if pattern.search(normalized_path):
                            findings.append(
                                {
                                    "code": "forbidden-read",
                                    "line": line_number,
                                    "path": path,
                                    "policyPath": normalized_path,
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
                "policyPath": policy_path(path, args.events) if path else None,
                "command": command[:240] if isinstance(command, str) else None,
                "isError": bool(event.get("isError")),
                "resultBytes": size,
            }
        )

    for required_path in args.require_read:
        if read_paths[required_path] == 0 and policy_read_paths[required_path] == 0:
            findings.append({"code": "missing-required-read", "path": required_path})
    for pattern in required_read_patterns:
        if not any(pattern.search(path) for path in policy_read_paths):
            findings.append({"code": "missing-required-read-regex", "pattern": pattern.pattern})
    if args.fail_on_invalid_json and (invalid_json_lines or invalid_event_lines):
        findings.append(
            {
                "code": "invalid-event-records",
                "invalidJsonCount": len(invalid_json_lines),
                "invalidJsonLineSamples": invalid_json_lines[:20],
                "nonObjectCount": len(invalid_event_lines),
                "nonObjectLineSamples": invalid_event_lines[:20],
            }
        )
    if args.require_tool_call and not calls:
        findings.append({"code": "missing-tool-call"})
    if args.require_model and set(model_counts) != {args.require_model}:
        findings.append(
            {
                "code": "observed-model-set-mismatch",
                "requiredModel": args.require_model,
                "observedModels": sorted(model_counts),
            }
        )
    total_read_result_bytes = sum(read_path_bytes.values())
    if (
        args.max_total_read_result_bytes is not None
        and total_read_result_bytes > args.max_total_read_result_bytes
    ):
        findings.append(
            {
                "code": "total-read-results-too-large",
                "resultBytes": total_read_result_bytes,
                "maximumBytes": args.max_total_read_result_bytes,
            }
        )

    summary = {
        "passed": not findings,
        "session": session,
        "models": dict(model_counts),
        "providers": dict(provider_counts),
        "usageTotals": dict(usage_totals),
        "invalidJsonLineCount": len(invalid_json_lines),
        "invalidJsonLineSamples": invalid_json_lines[:20],
        "invalidEventRecordCount": len(invalid_event_lines),
        "invalidEventRecordLineSamples": invalid_event_lines[:20],
        "toolCounts": dict(tool_counts),
        "paths": [
            {"path": path, "calls": path_counts[path], "resultBytes": path_bytes[path]}
            for path, _ in path_counts.most_common()
        ],
        "readPaths": [
            {"path": path, "calls": read_paths[path], "resultBytes": read_path_bytes[path]}
            for path, _ in read_paths.most_common()
        ],
        "policyReadPaths": [
            {"path": path, "calls": calls}
            for path, calls in policy_read_paths.most_common()
        ],
        "totalReadResultBytes": total_read_result_bytes,
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
