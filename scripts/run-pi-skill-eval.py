#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

from __future__ import annotations

import argparse
import datetime as dt
import json
import shutil
import subprocess
import sys
from pathlib import Path


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
    prompt_path.write_text(prompt, encoding="utf-8")

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
            prompt,
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
        artifact_check_path.write_text(json.dumps({"outputs": artifact_checks}, indent=2), encoding="utf-8")

    print(f"Pi exit code: {result.returncode}")
    print(f"Stdout: {stdout_path}")
    print(f"Stderr: {stderr_path}")
    if args.expect_output:
        print(f"Artifact check: {artifact_check_path}")
    if missing_outputs:
        print(f"Missing expected outputs: {', '.join(missing_outputs)}", file=sys.stderr)
        return result.returncode or 3
    return result.returncode


if __name__ == "__main__":
    sys.exit(main())
