#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import platform
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Any


DEFAULT_MODEL = "openai-codex/gpt-5.3-codex-spark"
SAFE_SKILL_NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
SAFE_RUN_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,159}$")
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
SNAPSHOT_IGNORED_SUFFIXES = {".pyc", ".pyo"}
SNAPSHOT_IGNORED_DIRS = {"__pycache__"}
STRICT_ASSETS_EXAMPLES_READ_PATTERN = r"(?i)(?:^|[\\/])assets[\\/]examples(?:[\\/]|$)"
STRICT_COMMON_FORBIDDEN_READ_PATTERNS = [
    r"(?i)^\.\.(?![\\/]prompt\.md$)",
    r"(?i)^(?:[A-Za-z]:[\\/]|/|\\\\)",
]


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def is_safe_workspace_relative(path: Path) -> bool:
    return (
        path != Path(".")
        and not path.is_absolute()
        and not path.drive
        and not path.root
        and ".." not in path.parts
        and all(":" not in part for part in path.parts)
    )


def targets_skill_payload(path: Path) -> bool:
    return bool(path.parts) and path.parts[0].lower() == "skills"


def is_within(path: Path, parent: Path) -> bool:
    try:
        path.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False


def normalize_policy_path(path: str, workspace: Path) -> str:
    candidate = Path(path)
    resolved = candidate.resolve() if candidate.is_absolute() else (workspace / candidate).resolve()
    if is_within(resolved, workspace):
        return resolved.relative_to(workspace.resolve()).as_posix()
    prompt_path = (workspace.parent / "prompt.md").resolve()
    if resolved == prompt_path:
        return "../prompt.md"
    return resolved.as_posix()


def strict_forbidden_read_patterns(skill: str, profile: str) -> list[str]:
    patterns = list(STRICT_COMMON_FORBIDDEN_READ_PATTERNS)
    if profile == "runtime":
        patterns.insert(0, STRICT_ASSETS_EXAMPLES_READ_PATTERN)
    patterns.append(rf"(?i)^skills[\\/](?!{re.escape(skill)}(?:[\\/]|$))")
    return patterns


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def snapshot_tree(root: Path) -> dict[str, dict[str, Any]]:
    snapshot: dict[str, dict[str, Any]] = {}
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        relative = path.relative_to(root)
        if any(part in SNAPSHOT_IGNORED_DIRS for part in relative.parts):
            continue
        if path.suffix.lower() in SNAPSHOT_IGNORED_SUFFIXES:
            continue
        snapshot[relative.as_posix()] = {
            "sizeBytes": path.stat().st_size,
            "sha256": sha256_file(path),
        }
    return snapshot


def snapshot_digest(snapshot: dict[str, dict[str, Any]]) -> str:
    encoded = json.dumps(snapshot, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return sha256_bytes(encoded)


def compare_snapshots(
    before: dict[str, dict[str, Any]], after: dict[str, dict[str, Any]]
) -> dict[str, Any]:
    before_paths = set(before)
    after_paths = set(after)
    added = sorted(after_paths - before_paths)
    removed = sorted(before_paths - after_paths)
    modified = sorted(path for path in before_paths & after_paths if before[path] != after[path])
    return {
        "passed": not added and not removed and not modified,
        "beforeDigest": snapshot_digest(before),
        "afterDigest": snapshot_digest(after),
        "added": added,
        "removed": removed,
        "modified": modified,
    }


def write_json(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def timeout_text(value: str | bytes | None, fallback: str = "") -> str:
    if value is None:
        return fallback
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    return value


def capture_version(command: list[str], cwd: Path) -> str | None:
    try:
        result = subprocess.run(
            command,
            cwd=cwd,
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
            timeout=10,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    if result.returncode != 0:
        return None
    output = (result.stdout or result.stderr).strip()
    return output.splitlines()[0] if output else None


def git_metadata(root: Path) -> dict[str, Any]:
    revision = capture_version(["git", "rev-parse", "HEAD"], root)
    try:
        status = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=root,
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
            timeout=15,
            check=False,
        )
        dirty = bool(status.stdout.strip()) if status.returncode == 0 else None
    except (OSError, subprocess.TimeoutExpired):
        dirty = None
    return {"commit": revision, "dirty": dirty}


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
        if not isinstance(event, dict):
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


def collect_observed_models(events_path: Path) -> list[dict[str, str]]:
    observed: set[tuple[str, str]] = set()
    for line in events_path.read_text(encoding="utf-8", errors="replace").splitlines():
        if not line.strip():
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(event, dict):
            continue
        if event.get("type") != "message_end":
            continue
        message = event.get("message")
        if not isinstance(message, dict) or message.get("role") != "assistant":
            continue
        provider = message.get("provider")
        model = message.get("model")
        if isinstance(model, str):
            observed.add((provider if isinstance(provider, str) else "", model))
    return [{"provider": provider, "model": model} for provider, model in sorted(observed)]


def expected_model_identity(requested: str) -> dict[str, str]:
    provider, separator, model = requested.partition("/")
    if separator:
        return {"provider": provider, "model": model}
    return {"provider": "", "model": provider}


def event_check_report(
    *,
    events_path: Path,
    prompt: str,
    require_prompt_read_first: bool,
    require_exact_command_from_prompt: bool,
    require_observed_model: bool,
    requested_model: str,
    fail_on_invalid_json: bool,
    fail_on_tool_error: bool,
    forbid_read_regex: list[str],
    forbid_command_regex: list[str],
) -> dict[str, Any]:
    calls = collect_tool_calls(events_path)
    observed_models = collect_observed_models(events_path)
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

    if require_observed_model:
        expected_model = expected_model_identity(requested_model)
        if observed_models != [expected_model]:
            findings.append(
                {
                    "code": "observed-model-mismatch",
                    "expected": expected_model,
                    "observed": observed_models,
                }
            )

    if fail_on_invalid_json:
        invalid_lines: list[int] = []
        for line_number, line in enumerate(
            events_path.read_text(encoding="utf-8", errors="replace").splitlines(), start=1
        ):
            if not line.strip():
                continue
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                invalid_lines.append(line_number)
                continue
            if not isinstance(event, dict):
                invalid_lines.append(line_number)
        if invalid_lines:
            findings.append(
                {
                    "code": "invalid-event-json",
                    "count": len(invalid_lines),
                    "lineSamples": invalid_lines[:20],
                }
            )

    for call in calls:
        if fail_on_tool_error and call.get("isError"):
            findings.append({"code": "tool-error", "line": call.get("line"), "tool": call.get("tool")})
        path = call.get("path")
        if call.get("tool") == "read" and isinstance(path, str):
            workspace = events_path.parent / "workspace"
            policy_path = normalize_policy_path(path, workspace)
            for pattern in forbidden_read_patterns:
                if pattern.search(policy_path):
                    findings.append(
                        {
                            "code": "forbidden-read",
                            "line": call.get("line"),
                            "path": path,
                            "policyPath": policy_path,
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

    return {
        "passed": not findings,
        "callCount": len(calls),
        "observedModels": observed_models,
        "calls": calls,
        "findings": findings,
    }


def parse_expected_value(raw: str) -> Any:
    lowered = raw.strip().lower()
    if lowered in {"true", "false", "null"}:
        return json.loads(lowered)
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return raw


def nested_value(data: Any, dotted_path: str) -> tuple[bool, Any]:
    current = data
    for part in dotted_path.split("."):
        if isinstance(current, dict) and part in current:
            current = current[part]
            continue
        if isinstance(current, list) and part.isdigit():
            index = int(part)
            if 0 <= index < len(current):
                current = current[index]
                continue
        return False, None
    return True, current


def output_json_field_report(workspace: Path, specs: list[str]) -> dict[str, Any]:
    findings: list[dict[str, Any]] = []
    checks: list[dict[str, Any]] = []
    for spec in specs:
        path_part, separator, field_spec = spec.partition("::")
        field_path, equals, expected_raw = field_spec.partition("=")
        if not separator or not equals or not path_part or not field_path:
            findings.append({"code": "invalid-json-field-spec", "spec": spec})
            continue
        relative_path = Path(path_part)
        output_path = workspace / relative_path
        if not is_safe_workspace_relative(relative_path) or not is_within(output_path, workspace):
            findings.append({"code": "json-output-outside-workspace", "path": path_part})
            continue
        try:
            data = json.loads(output_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            findings.append({"code": "json-output-read-failed", "path": path_part, "error": str(exc)})
            continue
        expected = parse_expected_value(expected_raw)
        exists, actual = nested_value(data, field_path)
        passed = exists and actual == expected
        checks.append(
            {
                "path": path_part,
                "field": field_path,
                "exists": exists,
                "expected": expected,
                "actual": actual,
                "passed": passed,
            }
        )
        if not passed:
            findings.append(
                {
                    "code": "json-output-field-mismatch" if exists else "json-output-field-missing",
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
        "--strict",
        action="store_true",
        help="Require JSON mode, expected outputs, prompt-first, valid event JSON, the requested model, zero tool errors, and a clean runtime read surface.",
    )
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
        "--require-observed-model",
        action="store_true",
        help="In JSON mode, fail unless assistant events report exactly the requested provider/model.",
    )
    parser.add_argument(
        "--fail-on-invalid-event-json",
        action="store_true",
        help="In JSON mode, fail when a non-empty event line is invalid JSON.",
    )
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

    if args.strict:
        if args.mode != "json":
            print("--strict requires --mode json.", file=sys.stderr)
            return 2
        if not args.expect_output:
            print("--strict requires at least one --expect-output path.", file=sys.stderr)
            return 2
        args.require_prompt_read_first = True
        args.require_observed_model = True
        args.fail_on_invalid_event_json = True
        args.fail_on_event_tool_error = True
        for pattern in strict_forbidden_read_patterns(args.skill, args.profile):
            if pattern not in args.forbid_event_read_regex:
                args.forbid_event_read_regex.append(pattern)

    for label, patterns in (
        ("--forbid-event-read-regex", args.forbid_event_read_regex),
        ("--forbid-event-command-regex", args.forbid_event_command_regex),
    ):
        for pattern in patterns:
            try:
                re.compile(pattern)
            except re.error as error:
                print(f"Invalid {label} value {pattern!r}: {error}", file=sys.stderr)
                return 2

    if not SAFE_SKILL_NAME_RE.fullmatch(args.skill):
        print(f"Invalid skill name: {args.skill}", file=sys.stderr)
        return 2
    if args.timeout_seconds <= 0:
        print("--timeout-seconds must be greater than zero.", file=sys.stderr)
        return 2

    for expected in args.expect_output:
        if not is_safe_workspace_relative(expected) or targets_skill_payload(expected):
            print(
                "--expect-output must be workspace-relative and outside the read-only skills/ tree: "
                f"{expected}",
                file=sys.stderr,
            )
            return 2

    for spec in args.expect_output_json_field:
        path_part, separator, field_spec = spec.partition("::")
        field_path, equals, _ = field_spec.partition("=")
        if (
            not separator
            or not equals
            or not field_path
            or not is_safe_workspace_relative(Path(path_part))
            or targets_skill_payload(Path(path_part))
        ):
            print(
                "--expect-output-json-field must use safe/path.json::dotted.field=value: "
                f"{spec}",
                file=sys.stderr,
            )
            return 2

    root = repo_root()
    source_skill = root / ".agents" / "skills" / args.skill
    if not source_skill.is_dir() or not (source_skill / "SKILL.md").is_file():
        print(f"Skill not found: {source_skill}", file=sys.stderr)
        return 2

    if args.prompt_file:
        if not args.prompt_file.is_file():
            print(f"Prompt file not found: {args.prompt_file}", file=sys.stderr)
            return 2
        prompt = args.prompt_file.read_text(encoding="utf-8")
        prompt_source = args.prompt_file.resolve().as_posix()
    else:
        prompt = args.prompt or ""
        prompt_source = "inline"
    if not prompt.strip():
        print("Evaluation prompt must not be empty.", file=sys.stderr)
        return 2

    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_id = args.run_id or f"{stamp}-{args.skill}-pi"
    if not SAFE_RUN_ID_RE.fullmatch(run_id):
        print(
            "--run-id must be 1-160 characters using only letters, digits, dot, underscore, or hyphen.",
            file=sys.stderr,
        )
        return 2
    try:
        pi_prefix = pi_command_prefix()
    except FileNotFoundError as error:
        print(str(error), file=sys.stderr)
        return 127
    run_dir = root / "evaluations" / "runs" / run_id
    workspace = run_dir / "workspace"
    skill_target = workspace / "skills" / args.skill
    if run_dir.exists():
        print(f"Run directory already exists: {run_dir}", file=sys.stderr)
        return 2
    try:
        workspace.mkdir(parents=True, exist_ok=False)
    except OSError as error:
        print(f"Could not create run workspace {workspace}: {error}", file=sys.stderr)
        return 2
    copy_skill_only(source_skill, skill_target, args.profile)

    prompt_path = run_dir / "prompt.md"
    stdout_path = run_dir / ("events.jsonl" if args.mode == "json" else "stdout.md")
    stderr_path = run_dir / "stderr.txt"
    command_path = run_dir / "command.txt"
    artifact_check_path = run_dir / "artifact-check.json"
    event_check_path = run_dir / "event-check.json"
    json_field_check_path = run_dir / "json-field-check.json"
    skill_integrity_check_path = run_dir / "skill-integrity-check.json"
    manifest_path = run_dir / "run-manifest.json"
    result_path = run_dir / "evaluation-result.json"
    prompt_path.write_text(prompt, encoding="utf-8")
    initial_skill_snapshot = snapshot_tree(skill_target)

    launcher_prompt = (
        f"You are running an isolated forward test for `{args.skill}`. "
        "Use the read tool to read `../prompt.md` first, then follow it exactly. "
        f"The loaded bundle is rooted at `skills/{args.skill}` from the current workspace; never prefix that path with `../`. "
        "The shell tool is bash, not PowerShell; do not run PowerShell commands. "
        "Do not list directories or inspect script source before reading the prompt. "
        "If the prompt gives an exact command, run it verbatim and verify the required outputs."
    )

    command = [
        *pi_prefix,
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

    manifest = {
        "schemaVersion": 1,
        "runId": run_id,
        "createdAtUtc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "skill": {
            "name": args.skill,
            "profile": args.profile,
            "fileCount": len(initial_skill_snapshot),
            "payloadSha256": snapshot_digest(initial_skill_snapshot),
        },
        "prompt": {
            "source": prompt_source,
            "sizeBytes": len(prompt.encode("utf-8")),
            "sha256": sha256_bytes(prompt.encode("utf-8")),
        },
        "pi": {
            "model": args.model,
            "thinking": args.thinking,
            "mode": args.mode,
            "timeoutSeconds": args.timeout_seconds,
        },
        "environment": {
            "piVersion": capture_version([*pi_prefix, "--version"], root),
            "uvVersion": capture_version(["uv", "--version"], root),
            "pythonVersion": platform.python_version(),
            "platform": platform.platform(),
            "git": git_metadata(root),
        },
        "expectedOutputs": [path.as_posix() for path in args.expect_output],
        "expectedJsonFields": args.expect_output_json_field,
        "eventPolicy": {
            "strict": args.strict,
            "requirePromptReadFirst": args.require_prompt_read_first,
            "requireExactCommandFromPrompt": args.require_exact_command_from_prompt,
            "requireObservedModel": args.require_observed_model,
            "failOnInvalidEventJson": args.fail_on_invalid_event_json,
            "failOnToolError": args.fail_on_event_tool_error,
            "forbidReadRegex": args.forbid_event_read_regex,
            "forbidCommandRegex": args.forbid_event_command_regex,
        },
        "command": command,
    }
    write_json(manifest_path, manifest)

    print(f"Run directory: {run_dir}")
    print(f"Workspace: {workspace}")
    print(f"Skill copy: {skill_target}")
    print(f"Profile: {args.profile}")
    print(f"Model: {args.model}")
    print(f"Manifest: {manifest_path}")

    started_at = dt.datetime.now(dt.timezone.utc)
    started_monotonic = time.monotonic()
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
        stdout_path.write_text(timeout_text(error.stdout), encoding="utf-8")
        stderr_path.write_text(timeout_text(error.stderr, "Timed out."), encoding="utf-8")
        integrity_report = compare_snapshots(initial_skill_snapshot, snapshot_tree(skill_target))
        write_json(skill_integrity_check_path, integrity_report)
        write_json(
            result_path,
            {
                "passed": False,
                "returnCode": 124,
                "piExitCode": None,
                "timedOut": True,
                "startedAtUtc": started_at.isoformat(),
                "finishedAtUtc": dt.datetime.now(dt.timezone.utc).isoformat(),
                "durationSeconds": round(time.monotonic() - started_monotonic, 3),
                "gates": {"skillIntegrity": integrity_report["passed"]},
            },
        )
        print(f"Pi timed out after {args.timeout_seconds} seconds.", file=sys.stderr)
        return 124
    except OSError as error:
        command_path.write_text(subprocess.list2cmdline(command), encoding="utf-8")
        stdout_path.write_text("", encoding="utf-8")
        stderr_path.write_text(str(error), encoding="utf-8")
        integrity_report = compare_snapshots(initial_skill_snapshot, snapshot_tree(skill_target))
        write_json(skill_integrity_check_path, integrity_report)
        write_json(
            result_path,
            {
                "passed": False,
                "returnCode": 127,
                "piExitCode": None,
                "timedOut": False,
                "startedAtUtc": started_at.isoformat(),
                "finishedAtUtc": dt.datetime.now(dt.timezone.utc).isoformat(),
                "durationSeconds": round(time.monotonic() - started_monotonic, 3),
                "gates": {"skillIntegrity": integrity_report["passed"]},
                "error": str(error),
            },
        )
        print(f"Could not execute Pi: {error}", file=sys.stderr)
        return 127

    command_path.write_text(subprocess.list2cmdline(command), encoding="utf-8")
    stdout_path.write_text(result.stdout, encoding="utf-8")
    stderr_path.write_text(result.stderr, encoding="utf-8")
    artifact_checks = []
    missing_outputs = []
    for expected in args.expect_output:
        output_path = workspace / expected
        contained = is_within(output_path, workspace)
        artifact_error: str | None = None
        try:
            exists = contained and output_path.exists()
            is_file = contained and output_path.is_file()
            size = output_path.stat().st_size if is_file else 0
            digest = sha256_file(output_path) if is_file else None
        except OSError as error:
            exists = False
            is_file = False
            size = 0
            digest = None
            artifact_error = str(error)
        check = {
            "path": expected.as_posix(),
            "containedInWorkspace": contained,
            "exists": exists,
            "isFile": is_file,
            "sizeBytes": size,
            "sha256": digest,
            "error": artifact_error,
        }
        artifact_checks.append(check)
        if not contained or not exists or not is_file or size <= 0:
            missing_outputs.append(expected.as_posix())
    if args.expect_output:
        write_json(
            artifact_check_path,
            {
                "passed": not missing_outputs,
                "expectedOutputCount": len(args.expect_output),
                "missingOutputs": missing_outputs,
                "outputs": artifact_checks,
            },
        )

    print(f"Pi exit code: {result.returncode}")
    print(f"Stdout: {stdout_path}")
    print(f"Stderr: {stderr_path}")
    if args.expect_output:
        print(f"Artifact check: {artifact_check_path}")
    event_check_requested = (
        args.require_prompt_read_first
        or args.require_exact_command_from_prompt
        or args.require_observed_model
        or args.fail_on_invalid_event_json
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
                require_observed_model=args.require_observed_model,
                requested_model=args.model,
                fail_on_invalid_json=args.fail_on_invalid_event_json,
                fail_on_tool_error=args.fail_on_event_tool_error,
                forbid_read_regex=args.forbid_event_read_regex,
                forbid_command_regex=args.forbid_event_command_regex,
            )
        write_json(event_check_path, event_report)
        print(f"Event check: {event_check_path}")
        event_check_failed = event_report.get("passed") is not True

    json_field_failed = False
    if args.expect_output_json_field:
        json_field_report = output_json_field_report(workspace, args.expect_output_json_field)
        write_json(json_field_check_path, json_field_report)
        print(f"JSON field check: {json_field_check_path}")
        json_field_failed = json_field_report.get("passed") is not True

    integrity_report = compare_snapshots(initial_skill_snapshot, snapshot_tree(skill_target))
    write_json(skill_integrity_check_path, integrity_report)
    print(f"Skill integrity check: {skill_integrity_check_path}")
    integrity_failed = integrity_report.get("passed") is not True

    return_code = result.returncode
    if missing_outputs:
        print(f"Missing expected outputs: {', '.join(missing_outputs)}", file=sys.stderr)
        return_code = return_code or 3
    elif event_check_failed:
        print("Event checks failed.", file=sys.stderr)
        return_code = return_code or 4
    elif json_field_failed:
        print("JSON field checks failed.", file=sys.stderr)
        return_code = return_code or 5
    elif integrity_failed:
        print("The isolated run modified its read-only skill bundle.", file=sys.stderr)
        return_code = return_code or 6

    write_json(
        result_path,
        {
            "passed": return_code == 0,
            "returnCode": return_code,
            "piExitCode": result.returncode,
            "timedOut": False,
            "startedAtUtc": started_at.isoformat(),
            "finishedAtUtc": dt.datetime.now(dt.timezone.utc).isoformat(),
            "durationSeconds": round(time.monotonic() - started_monotonic, 3),
            "gates": {
                "artifacts": None if not args.expect_output else not missing_outputs,
                "events": None if not event_check_requested else not event_check_failed,
                "jsonFields": None if not args.expect_output_json_field else not json_field_failed,
                "skillIntegrity": not integrity_failed,
            },
        },
    )
    print(f"Evaluation result: {result_path}")
    return return_code


if __name__ == "__main__":
    sys.exit(main())
