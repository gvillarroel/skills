#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any


DEFAULT_MODEL = "openai-codex/gpt-5.3-codex-spark"
COPY_IGNORE = {
    "node_modules",
    ".git",
    ".cache",
    ".vite",
    "dist",
    "output",
    "playwright-report",
    "test-results",
    "__pycache__",
}
RUNTIME_EXCLUDED_DIRS = {
    Path("assets") / "examples",
}


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def copy_skill_only(source: Path, target: Path, profile: str) -> None:
    def ignore(current_dir: str, names: list[str]) -> set[str]:
        ignored = {name for name in names if name in COPY_IGNORE}
        if profile == "runtime":
            current = Path(current_dir)
            for name in names:
                rel = (current / name).relative_to(source)
                if rel in RUNTIME_EXCLUDED_DIRS:
                    ignored.add(name)
        return ignored

    shutil.copytree(source, target, ignore=ignore)


def pi_command_prefix() -> list[str]:
    for executable in ("pi", "pi.cmd", "pi.exe", "pi.ps1"):
        found = shutil.which(executable)
        if not found:
            continue
        path = Path(found)
        if path.suffix.lower() == ".ps1":
            return ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(path)]
        return [str(path)]
    raise FileNotFoundError("Could not find pi, pi.cmd, pi.exe, or pi.ps1 on PATH.")


def path_from_args(args: Any) -> str | None:
    if not isinstance(args, dict):
        return None
    for key in ("path", "file", "filePath", "target", "pattern"):
        value = args.get(key)
        if isinstance(value, str):
            return value
    return None


def extract_fenced_commands(prompt: str) -> list[str]:
    commands: list[str] = []
    for match in re.finditer(r"```(?:bash|sh|shell)?\s*\n(.*?)\n```", prompt, flags=re.IGNORECASE | re.DOTALL):
        command = match.group(1).strip()
        if command:
            commands.append(command)
    return commands


def normalize_recorded_command(command: str) -> str:
    command = command.strip()
    match = re.match(r"^cd\s+\S+\s+&&\s+(?P<body>.+)$", command, flags=re.DOTALL)
    if match:
        return match.group("body").strip()
    return command


def command_block_was_run(expected: str, actual_commands: list[str]) -> bool:
    if expected in actual_commands:
        return True
    expected_lines = [line.strip() for line in expected.splitlines() if line.strip()]
    if len(expected_lines) <= 1:
        return False
    start = 0
    for expected_line in expected_lines:
        for index in range(start, len(actual_commands)):
            if actual_commands[index] == expected_line:
                start = index + 1
                break
        else:
            return False
    return True


def collect_tool_calls(events_path: Path) -> list[dict[str, Any]]:
    starts: dict[str, dict[str, Any]] = {}
    calls: list[dict[str, Any]] = []
    for line_number, line in enumerate(events_path.read_text(encoding="utf-8", errors="replace").splitlines(), start=1):
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
        start = starts.get(str(event.get("toolCallId", "")), {})
        tool_args = start.get("args")
        command = tool_args.get("command") if isinstance(tool_args, dict) else None
        calls.append(
            {
                "line": line_number,
                "tool": str(event.get("toolName", "")),
                "path": path_from_args(tool_args),
                "command": command if isinstance(command, str) else None,
                "isError": bool(event.get("isError")),
            }
        )
    return calls


def event_check_report(
    *,
    events_path: Path,
    prompt: str,
    require_prompt_read_first: bool,
    require_exact_command_from_prompt: bool,
    fail_on_tool_error: bool,
    forbid_read_regex: list[str],
    forbid_command_regex: list[str],
) -> dict[str, Any]:
    calls = collect_tool_calls(events_path)
    findings: list[dict[str, Any]] = []
    forbidden_read_patterns = [re.compile(pattern) for pattern in forbid_read_regex]
    forbidden_command_patterns = [re.compile(pattern) for pattern in forbid_command_regex]

    if require_prompt_read_first:
        first = calls[0] if calls else None
        if not first or first.get("tool") != "read" or first.get("path") != "../prompt.md":
            findings.append(
                {
                    "code": "prompt-not-read-first",
                    "firstTool": first,
                }
            )

    if require_exact_command_from_prompt:
        expected_commands = extract_fenced_commands(prompt)
        actual_commands = [normalize_recorded_command(str(call.get("command"))) for call in calls if call.get("command")]
        if not expected_commands:
            findings.append({"code": "no-fenced-command-in-prompt"})
        else:
            missing_commands = [
                command for command in expected_commands if not command_block_was_run(command, actual_commands)
            ]
            if missing_commands:
                findings.append(
                    {
                        "code": "missing-exact-prompt-command",
                        "expectedCommands": missing_commands,
                        "actualCommandSamples": actual_commands[:5],
                    }
                )

    for call in calls:
        if fail_on_tool_error and call.get("isError"):
            findings.append({"code": "tool-error", "line": call.get("line"), "tool": call.get("tool")})
        path = call.get("path")
        if isinstance(path, str):
            for pattern in forbidden_read_patterns:
                if pattern.search(path):
                    findings.append(
                        {
                            "code": "forbidden-read",
                            "line": call.get("line"),
                            "path": path,
                            "pattern": pattern.pattern,
                        }
                    )
                    break
        command = call.get("command")
        if isinstance(command, str):
            for pattern in forbidden_command_patterns:
                if pattern.search(command):
                    findings.append(
                        {
                            "code": "forbidden-command",
                            "line": call.get("line"),
                            "pattern": pattern.pattern,
                            "commandSample": command[:240],
                        }
                    )
                    break

    return {"passed": not findings, "callCount": len(calls), "calls": calls, "findings": findings}


def parse_expected_value(raw: str) -> Any:
    lowered = raw.strip().lower()
    if lowered in {"true", "false", "null"}:
        return json.loads(lowered)
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return raw


def nested_value(data: Any, dotted_path: str) -> Any:
    current = data
    for part in dotted_path.split("."):
        if isinstance(current, dict) and part in current:
            current = current[part]
            continue
        return None
    return current


def output_json_field_report(workspace: Path, specs: list[str]) -> dict[str, Any]:
    findings: list[dict[str, Any]] = []
    checks: list[dict[str, Any]] = []
    for spec in specs:
        path_part, separator, field_spec = spec.partition("::")
        field_path, equals, expected_raw = field_spec.partition("=")
        if not separator or not equals or not path_part or not field_path:
            findings.append({"code": "invalid-json-field-spec", "spec": spec})
            continue
        output_path = workspace / Path(path_part)
        try:
            data = json.loads(output_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            findings.append({"code": "json-output-read-failed", "path": path_part, "error": str(exc)})
            continue
        expected = parse_expected_value(expected_raw)
        actual = nested_value(data, field_path)
        passed = actual == expected
        checks.append({"path": path_part, "field": field_path, "expected": expected, "actual": actual, "passed": passed})
        if not passed:
            findings.append(
                {
                    "code": "json-output-field-mismatch",
                    "path": path_part,
                    "field": field_path,
                    "expected": expected,
                    "actual": actual,
                }
            )
    return {"passed": not findings, "checks": checks, "findings": findings}


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run an isolated pi forward test with only one skill bundle copied into the workspace."
    )
    parser.add_argument("skill", help="Skill directory name under .agents/skills.")
    prompt_group = parser.add_mutually_exclusive_group(required=True)
    prompt_group.add_argument("--prompt", help="Evaluation prompt text.")
    prompt_group.add_argument("--prompt-file", type=Path, help="Path to a prompt file.")
    parser.add_argument("--model", default=DEFAULT_MODEL, help=f"Pi model to use. Default: {DEFAULT_MODEL}")
    parser.add_argument("--thinking", default="high", help="Pi thinking level. Default: high")
    parser.add_argument("--mode", choices=["text", "json"], default="text", help="Pi output mode. Default: text")
    parser.add_argument(
        "--profile",
        choices=["runtime", "full"],
        default="runtime",
        help="Skill copy profile. runtime excludes acceptance fixtures under assets/examples; full copies the whole skill except dependency/build output. Default: runtime.",
    )
    parser.add_argument("--run-id", help="Stable run id. Defaults to a timestamped id.")
    parser.add_argument("--timeout-seconds", type=int, default=900, help="Subprocess timeout. Default: 900")
    parser.add_argument(
        "--expect-output",
        action="append",
        default=[],
        type=Path,
        help="Expected non-empty output path relative to the isolated workspace. May be repeated.",
    )
    parser.add_argument("--require-prompt-read-first", action="store_true", help="In JSON mode, fail unless the first tool call reads ../prompt.md.")
    parser.add_argument(
        "--require-exact-command-from-prompt",
        action="store_true",
        help="In JSON mode, fail unless a fenced prompt command is run exactly as a shell command.",
    )
    parser.add_argument("--fail-on-event-tool-error", action="store_true", help="In JSON mode, fail when any tool call reports isError.")
    parser.add_argument(
        "--forbid-event-read-regex",
        action="append",
        default=[],
        help="In JSON mode, fail when a read-tool path matches this regex. May be repeated.",
    )
    parser.add_argument(
        "--forbid-event-command-regex",
        action="append",
        default=[],
        help="In JSON mode, fail when a shell command string matches this regex. May be repeated.",
    )
    parser.add_argument(
        "--expect-output-json-field",
        action="append",
        default=[],
        help="Assert a workspace-relative JSON output field, formatted as path::dotted.field=value. May be repeated.",
    )
    args = parser.parse_args()

    for expected in args.expect_output:
        if expected.is_absolute() or ".." in expected.parts:
            print(f"--expect-output must be a workspace-relative path: {expected}", file=sys.stderr)
            return 2

    root = repo_root()
    source_skill = root / ".agents" / "skills" / args.skill
    if not source_skill.exists():
        print(f"Skill not found: {source_skill}", file=sys.stderr)
        return 2

    if args.prompt_file:
        prompt = args.prompt_file.read_text(encoding="utf-8")
    else:
        prompt = args.prompt or ""

    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_id = args.run_id or f"{stamp}-{args.skill}-pi"
    run_dir = root / "evaluations" / "runs" / run_id
    workspace = run_dir / "workspace"
    skill_target = workspace / "skills" / args.skill
    workspace.mkdir(parents=True, exist_ok=False)
    copy_skill_only(source_skill, skill_target, args.profile)

    prompt_path = run_dir / "prompt.md"
    stdout_path = run_dir / ("events.jsonl" if args.mode == "json" else "stdout.md")
    stderr_path = run_dir / "stderr.txt"
    command_path = run_dir / "command.txt"
    artifact_check_path = run_dir / "artifact-check.json"
    event_check_path = run_dir / "event-check.json"
    json_field_check_path = run_dir / "json-field-check.json"
    prompt_path.write_text(prompt, encoding="utf-8")

    launcher_prompt = (
        f"You are running an isolated forward test for `{args.skill}`. "
        "Use the read tool to read `../prompt.md` first, then follow it exactly. "
        "The shell tool is bash, not PowerShell; do not run PowerShell commands. "
        "Do not list directories or inspect script source before reading the prompt. "
        "If the prompt gives an exact command, run it verbatim and verify the required outputs."
    )

    try:
        command = [
            *pi_command_prefix(),
            "--model",
            args.model,
            "--thinking",
            args.thinking,
            "--mode",
            args.mode,
            "--no-context-files",
            "--no-extensions",
            "--no-skills",
            "--no-prompt-templates",
            "--no-themes",
            "--no-session",
            "--skill",
            f"skills/{args.skill}",
            "--print",
            launcher_prompt,
        ]
    except FileNotFoundError as error:
        print(str(error), file=sys.stderr)
        return 127

    print(f"Run directory: {run_dir}")
    print(f"Workspace: {workspace}")
    print(f"Skill copy: {skill_target}")
    print(f"Profile: {args.profile}")
    print(f"Model: {args.model}")

    try:
        result = subprocess.run(
            command,
            cwd=workspace,
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
            timeout=args.timeout_seconds,
            check=False,
        )
    except subprocess.TimeoutExpired as error:
        command_path.write_text(subprocess.list2cmdline(command), encoding="utf-8")
        stdout_path.write_text(error.stdout or "", encoding="utf-8")
        stderr_path.write_text(error.stderr or "Timed out.", encoding="utf-8")
        print(f"Pi timed out after {args.timeout_seconds} seconds.", file=sys.stderr)
        return 124

    command_path.write_text(subprocess.list2cmdline(command), encoding="utf-8")
    stdout_path.write_text(result.stdout, encoding="utf-8")
    stderr_path.write_text(result.stderr, encoding="utf-8")
    artifact_checks = []
    missing_outputs = []
    for expected in args.expect_output:
        output_path = workspace / expected
        exists = output_path.exists()
        size = output_path.stat().st_size if output_path.is_file() else 0
        check = {
            "path": expected.as_posix(),
            "exists": exists,
            "isFile": output_path.is_file(),
            "sizeBytes": size,
        }
        artifact_checks.append(check)
        if not exists or not output_path.is_file() or size <= 0:
            missing_outputs.append(expected.as_posix())
    if args.expect_output:
        artifact_check_path.write_text(
            json.dumps(
                {
                    "passed": not missing_outputs,
                    "expectedOutputCount": len(args.expect_output),
                    "missingOutputs": missing_outputs,
                    "outputs": artifact_checks,
                },
                indent=2,
            ),
            encoding="utf-8",
        )

    print(f"Pi exit code: {result.returncode}")
    print(f"Stdout: {stdout_path}")
    print(f"Stderr: {stderr_path}")
    if args.expect_output:
        print(f"Artifact check: {artifact_check_path}")
    event_check_requested = (
        args.require_prompt_read_first
        or args.require_exact_command_from_prompt
        or args.fail_on_event_tool_error
        or bool(args.forbid_event_read_regex)
        or bool(args.forbid_event_command_regex)
    )
    event_check_failed = False
    if event_check_requested:
        if args.mode != "json":
            event_report = {
                "passed": False,
                "findings": [{"code": "event-check-requires-json-mode"}],
            }
        else:
            event_report = event_check_report(
                events_path=stdout_path,
                prompt=prompt,
                require_prompt_read_first=args.require_prompt_read_first,
                require_exact_command_from_prompt=args.require_exact_command_from_prompt,
                fail_on_tool_error=args.fail_on_event_tool_error,
                forbid_read_regex=args.forbid_event_read_regex,
                forbid_command_regex=args.forbid_event_command_regex,
            )
        event_check_path.write_text(json.dumps(event_report, indent=2), encoding="utf-8")
        print(f"Event check: {event_check_path}")
        event_check_failed = event_report.get("passed") is not True

    json_field_failed = False
    if args.expect_output_json_field:
        json_field_report = output_json_field_report(workspace, args.expect_output_json_field)
        json_field_check_path.write_text(json.dumps(json_field_report, indent=2), encoding="utf-8")
        print(f"JSON field check: {json_field_check_path}")
        json_field_failed = json_field_report.get("passed") is not True

    if missing_outputs:
        print(f"Missing expected outputs: {', '.join(missing_outputs)}", file=sys.stderr)
        return result.returncode or 3
    if event_check_failed:
        print("Event checks failed.", file=sys.stderr)
        return result.returncode or 4
    if json_field_failed:
        print("JSON field checks failed.", file=sys.stderr)
        return result.returncode or 5
    return result.returncode


if __name__ == "__main__":
    sys.exit(main())
