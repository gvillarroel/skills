#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Inventory Python, Node and Pi with version-only calls; do not start a session."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import subprocess
import sys


MAX_WRAPPER_BYTES = 65536
ENTRY = re.compile(
    r"(?:%dp0%|%~dp0|\$(?:basedir|PSScriptRoot))[\\/]+"
    r"(node_modules[\\/](?:@[a-z0-9_.-]+[\\/])?pi-coding-agent[\\/]"
    r"dist[\\/](?:bundle[\\/])?cli\.(?:js|mjs))(?=[\"'\s]|$)",
    re.IGNORECASE,
)
VERSIONS = {
    "python": re.compile(r"Python \d+\.\d+(?:\.\d+)?(?:[a-z0-9.+-]*)?", re.IGNORECASE),
    "node": re.compile(r"v\d+\.\d+\.\d+(?:[-+][a-z0-9.-]+)?", re.IGNORECASE),
    "pi": re.compile(r"(?:(?:pi|pi-coding-agent)(?: version)?\s+)?v?\d+\.\d+\.\d+(?:[-+][a-z0-9.-]+)?", re.IGNORECASE),
}
EXECUTION_FAILURES = {"execution-failed", "timeout", "unexpected-output"}


def missing(name: str, detail: str, status: str = "missing") -> dict:
    return {"name": name, "passed": False, "status": status, "command": None,
            "version": None, "exit_code": None, "detail": detail}


def find_node(lookup=shutil.which, platform_name: str | None = None) -> list[str] | None:
    names = ("node.exe", "node") if (platform_name or os.name) == "nt" else ("node",)
    for name in names:
        if found := lookup(name):
            return [str(found)]
    return None


def resolve_pi(node: list[str] | None, *, lookup=shutil.which, platform_name: str | None = None) -> dict:
    """Resolve npm's local entry on Windows without executing a shell wrapper."""
    system = platform_name or os.name
    names = ("pi.exe", "pi.cmd", "pi.ps1", "pi") if system == "nt" else ("pi",)
    found = next((path for name in names if (path := lookup(name))), None)
    if not found:
        return missing("pi", "Pi was not found on PATH. No package was installed.")
    launcher = Path(found)
    if system != "nt" and launcher.suffix.lower() not in {".cmd", ".bat", ".ps1"}:
        return {"command": [str(found)], "launcher": "direct"}
    if launcher.suffix.lower() in {".exe", ".com"}:
        return {"command": [str(found)], "launcher": "direct"}
    try:
        with launcher.open("rb") as stream:
            raw = stream.read(MAX_WRAPPER_BYTES + 1)
        if len(raw) > MAX_WRAPPER_BYTES:
            return missing("pi", "The launcher exceeds the bounded npm-wrapper read size; it was not executed.", "unresolved-wrapper")
        text = raw.decode("utf-8-sig")
    except (OSError, UnicodeError):
        return missing("pi", "The npm launcher could not be read; it was not executed.", "unresolved-wrapper")
    entries = {value.replace("\\", "/") for value in ENTRY.findall(text)}
    if len(entries) != 1:
        return missing("pi", "No single recognized local Pi CLI entry was found in the npm launcher; it was not executed.", "unresolved-wrapper")
    relative = PurePosixPath(next(iter(entries)))
    if relative.is_absolute() or ".." in relative.parts:
        return missing("pi", "The npm launcher entry is not a contained relative package path.", "unresolved-wrapper")
    entry = launcher.parent.joinpath(*relative.parts)
    if not entry.is_file():
        return missing("pi", "The Pi CLI entry referenced by the npm launcher is missing.", "unresolved-wrapper")
    adjacent_node = launcher.parent / "node.exe"
    actual_node = [str(adjacent_node)] if adjacent_node.is_file() else node
    if not actual_node:
        return missing("pi", "The npm Pi entry exists, but no local or PATH Node runtime was found.")
    return {"command": [*actual_node, str(entry)], "launcher": "windows-npm-entry"}


def probe(name: str, command: list[str] | None, *, runner=subprocess.run, launcher: str = "direct") -> dict:
    if not command:
        return missing(name, f"The {name} runtime was not found. No installation was attempted.")
    argv = [*command, "--version"]
    common = {"name": name, "command": argv, "launcher": launcher, "version": None}
    try:
        result = runner(argv, stdin=subprocess.DEVNULL, capture_output=True, text=True,
                        encoding="utf-8", errors="replace", timeout=10, check=False,
                        shell=False, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0) if os.name == "nt" else 0)
    except subprocess.TimeoutExpired:
        return {**common, "passed": False, "status": "timeout", "exit_code": None,
                "detail": "The required version command exceeded its 10-second limit."}
    except OSError:
        return {**common, "passed": False, "status": "execution-failed", "exit_code": None,
                "detail": "The required version command could not start."}
    if result.returncode != 0:
        return {**common, "passed": False, "status": "execution-failed", "exit_code": result.returncode,
                "detail": "The required version command returned a nonzero exit status."}
    lines = (result.stdout or result.stderr or "").strip().splitlines()
    version = lines[0].strip() if lines else ""
    if len(lines) != 1 or not VERSIONS[name].fullmatch(version):
        return {**common, "passed": False, "status": "unexpected-output", "exit_code": 0,
                "detail": "The version command did not return a recognized version line."}
    return {**common, "passed": True, "status": "available", "exit_code": 0,
            "version": version, "detail": "The installed runtime answered its version flag."}


def build_report(*, lookup=shutil.which, runner=subprocess.run, platform_name: str | None = None) -> dict:
    node = find_node(lookup, platform_name)
    pi = resolve_pi(node, lookup=lookup, platform_name=platform_name)
    checks = [probe("python", [sys.executable], runner=runner), probe("node", node, runner=runner)]
    checks.append(probe("pi", pi["command"], runner=runner, launcher=pi.get("launcher", "direct")) if pi["command"] else pi)
    return {"schema_version": 1, "host": "pi", "passed": all(check["passed"] for check in checks),
            "checks": checks, "scope": "Version inventory only. Python runs this helper; it is not an extension runtime dependency. No compiler, package manager, session, extension, model or account action is requested."}


def exit_code(report: dict, fail_on_missing: bool = False) -> int:
    if any(check["status"] in EXECUTION_FAILURES for check in report["checks"]):
        return 1
    return int(fail_on_missing and not report["passed"])


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", choices=["pi"], required=True)
    parser.add_argument("--fail-on-missing", action="store_true", help="Exit 1 for missing/unresolvable runtimes as well as actual execution failures.")
    args = parser.parse_args()
    report = build_report()
    print(json.dumps(report, indent=2))
    return exit_code(report, args.fail_on_missing)


if __name__ == "__main__":
    raise SystemExit(main())
