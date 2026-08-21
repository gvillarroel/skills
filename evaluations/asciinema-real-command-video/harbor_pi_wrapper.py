#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""Run the installed Windows Pi CLI for a workspace-backed Harbor trial."""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys


def resolve_pi_command() -> list[str]:
    """Resolve Pi without routing multiline prompts through a Windows shim."""

    node = shutil.which("node.exe") or shutil.which("node")
    for shim_name in ("pi.cmd", "pi.ps1", "pi"):
        shim = shutil.which(shim_name)
        if not shim:
            continue
        npm_bin = Path(shim).resolve().parent
        for package_scope in ("@earendil-works", "@mariozechner"):
            cli = (
                npm_bin
                / "node_modules"
                / package_scope
                / "pi-coding-agent"
                / "dist"
                / "cli.js"
            )
            if node and cli.is_file():
                return [node, str(cli)]

    resolved_exe = shutil.which("pi.exe")
    if resolved_exe:
        return [resolved_exe]
    raise SystemExit("The installed Pi JavaScript CLI was not found on Windows PATH.")


def pi_version(pi_command: list[str]) -> str:
    completed = subprocess.run(
        [*pi_command, "--version"],
        stdin=subprocess.DEVNULL,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
        timeout=60,
    )
    if completed.returncode != 0:
        raise SystemExit(f"Pi version check exited {completed.returncode}.")
    return completed.stdout.strip()


def check_command(args: argparse.Namespace) -> int:
    pi_command = resolve_pi_command()
    observed = pi_version(pi_command)
    if observed != args.expected_version:
        raise SystemExit(
            f"Pi version mismatch: expected {args.expected_version}, observed {observed}."
        )
    print(json.dumps({"pi": pi_command, "version": observed}, sort_keys=True))
    return 0


def run_command(args: argparse.Namespace) -> int:
    pi_command = resolve_pi_command()
    observed = pi_version(pi_command)
    if observed != args.expected_version:
        raise SystemExit(
            f"Pi version mismatch: expected {args.expected_version}, observed {observed}."
        )
    try:
        prompt = base64.b64decode(args.prompt_base64, validate=True).decode("utf-8")
    except (ValueError, UnicodeDecodeError) as error:
        raise SystemExit(f"Prompt payload is invalid: {error}") from error

    output_path = args.output.resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    command = [
        *pi_command,
        "--print",
        "--mode",
        "json",
        "--no-session",
        "--no-context-files",
        "--no-extensions",
        "--no-skills",
        "--skill",
        args.skill_path,
        "--no-prompt-templates",
        "--no-themes",
        "--provider",
        args.provider,
        "--model",
        args.model,
        "--thinking",
        args.thinking,
        prompt,
    ]
    process = subprocess.Popen(
        command,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
        bufsize=1,
    )
    assert process.stdout is not None
    prompt_sha256 = hashlib.sha256(prompt.encode("utf-8")).hexdigest()
    with output_path.open("w", encoding="utf-8", newline="\n") as output:
        output.write(
            json.dumps(
                {
                    "type": "harbor_pi_wrapper",
                    "promptBytes": len(prompt.encode("utf-8")),
                    "promptSha256": prompt_sha256,
                },
                sort_keys=True,
            )
            + "\n"
        )
        output.flush()
        for line in process.stdout:
            stripped = line.rstrip("\r\n")
            try:
                event = json.loads(stripped)
            except json.JSONDecodeError:
                event = None
            if isinstance(event, dict) and event.get("type") == "message_update":
                continue
            output.write(stripped + "\n")
            output.flush()
            print(stripped, flush=True)
    return process.wait()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    check = subparsers.add_parser("check")
    check.add_argument("--expected-version", required=True)
    run = subparsers.add_parser("run")
    run.add_argument("--expected-version", required=True)
    run.add_argument("--prompt-base64", required=True)
    run.add_argument("--provider", required=True)
    run.add_argument("--model", required=True)
    run.add_argument("--skill-path", required=True)
    run.add_argument(
        "--thinking",
        required=True,
        choices=["off", "minimal", "low", "medium", "high", "xhigh"],
    )
    run.add_argument("--output", type=Path, required=True)
    return parser


def main() -> int:
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if callable(reconfigure):
            reconfigure(encoding="utf-8", errors="replace")
    args = build_parser().parse_args()
    if args.command == "check":
        return check_command(args)
    return run_command(args)


if __name__ == "__main__":
    sys.exit(main())
