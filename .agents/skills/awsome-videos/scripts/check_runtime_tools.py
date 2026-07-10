#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Preflight runtime tools for awsome-videos production workflows."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
from typing import Any, Callable


sys.dont_write_bytecode = True

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent

REQUIRED_FILES = [
    "SKILL.md",
    "references/awesome-fireship-patterns.md",
    "references/video-production-playbook.md",
    "references/evaluation-rubric.md",
    "references/command-contracts.md",
    "references/visual-asset-composition-workflow.md",
    "assets/templates/brief-template.md",
    "assets/templates/production-notes-template.md",
    "scripts/scaffold_production_package.py",
    "scripts/select_video_patterns.py",
    "scripts/check_video_brief.py",
    "scripts/create_concept_renderer.py",
    "scripts/check_renderer_contract.py",
    "scripts/render_concept_video.py",
    "scripts/check_video_artifact.py",
    "scripts/score_video_readiness.py",
    "scripts/score_style_fidelity.py",
    "scripts/finalize_production_notes.py",
    "scripts/check_production_package.py",
    "scripts/check_visual_contract.py",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Preflight awsome-videos runtime tools and bundled files.")
    parser.add_argument("--skill-dir", type=Path, default=SKILL_DIR)
    parser.add_argument("--require-ffmpeg", action="store_true")
    parser.add_argument("--require-ffprobe", action="store_true")
    parser.add_argument("--require-render-tools", action="store_true", help="Require both ffmpeg and ffprobe.")
    parser.add_argument("--require-node", action="store_true")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


def run(cmd: list[str], timeout: float = 10.0) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, text=True, capture_output=True, check=False, timeout=timeout)


def common_tool_paths(name: str) -> list[Path]:
    paths: list[Path] = []
    for env_name in [name.upper(), f"{name.upper()}_PATH"]:
        raw = os.environ.get(env_name)
        if raw:
            paths.append(Path(raw))
    home = Path.home()
    username = os.environ.get("USER") or os.environ.get("USERNAME")
    executable_names = [name, f"{name}.exe"] if not name.endswith(".exe") else [name]
    for executable in executable_names:
        paths.extend(
            [
                home / "AppData" / "Local" / "Microsoft" / "WinGet" / "Links" / executable,
                Path("C:/ProgramData/chocolatey/bin") / executable,
                Path("C:/ffmpeg/bin") / executable,
            ]
        )
    if username:
        for executable in executable_names:
            paths.extend(
                [
                    Path("/mnt/c/Users") / username / "AppData" / "Local" / "Microsoft" / "WinGet" / "Links" / executable,
                    Path("/mnt/c/ProgramData/chocolatey/bin") / executable,
                    Path("/mnt/c/ffmpeg/bin") / executable,
                ]
            )
    return paths


def resolve_tool(name: str) -> str | None:
    tool = shutil.which(name)
    if tool:
        return tool
    for candidate in common_tool_paths(name):
        if candidate.is_file():
            return str(candidate)
    return None


def first_line(value: str) -> str:
    return value.strip().splitlines()[0] if value.strip() else ""


def command_version(path: str, args: list[str] | None = None) -> str | None:
    try:
        result = run([path, *(args or ["--version"])])
    except (OSError, subprocess.SubprocessError):
        return None
    output = first_line(result.stdout) or first_line(result.stderr)
    return output or None


def check_python() -> dict[str, Any]:
    version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    ok = sys.version_info >= (3, 11)
    return {
        "ok": ok,
        "executable": sys.executable,
        "version": version,
        "required": ">=3.11",
        "failure": None if ok else f"Python >=3.11 required, found {version}",
    }


def check_tool(
    name: str,
    required: bool,
    resolver: Callable[[str], str | None] = resolve_tool,
) -> dict[str, Any]:
    path = resolver(name)
    ok = bool(path)
    info: dict[str, Any] = {
        "ok": ok,
        "required": required,
        "path": path,
        "version": command_version(path) if path else None,
        "failure": None,
        "warning": None,
    }
    if required and not path:
        info["failure"] = f"{name} is required but was not found on PATH or common install locations"
    elif not required and not path:
        info["warning"] = f"{name} not found; MP4 rendering or strict audio/video validation may fail"
    return info


def check_required_files(skill_dir: Path, required_files: list[str] = REQUIRED_FILES) -> dict[str, Any]:
    missing = [relative for relative in required_files if not (skill_dir / relative).exists()]
    return {
        "ok": not missing,
        "skillDir": str(skill_dir),
        "checked": required_files,
        "missing": missing,
        "failure": None if not missing else "missing required skill files: " + ", ".join(missing),
    }


def build_result(
    skill_dir: Path,
    *,
    require_ffmpeg: bool = False,
    require_ffprobe: bool = False,
    require_render_tools: bool = False,
    require_node: bool = False,
    resolver: Callable[[str], str | None] = resolve_tool,
) -> dict[str, Any]:
    failures: list[str] = []
    warnings: list[str] = []
    ffmpeg_required = require_ffmpeg or require_render_tools
    ffprobe_required = require_ffprobe or require_render_tools
    checks = {
        "python": check_python(),
        "uv": check_tool("uv", True, resolver),
        "requiredFiles": check_required_files(skill_dir),
        "ffmpeg": check_tool("ffmpeg", ffmpeg_required, resolver),
        "ffprobe": check_tool("ffprobe", ffprobe_required, resolver),
        "node": check_tool("node", require_node, resolver),
    }
    for name, info in checks.items():
        failure = info.get("failure")
        warning = info.get("warning")
        if failure:
            failures.append(f"{name}: {failure}")
        if warning:
            warnings.append(f"{name}: {warning}")
    return {
        "ok": not failures,
        "skillDir": str(skill_dir),
        "requirements": {
            "ffmpeg": ffmpeg_required,
            "ffprobe": ffprobe_required,
            "node": require_node,
        },
        "checks": checks,
        "failures": failures,
        "warnings": warnings,
    }


def main() -> int:
    args = parse_args()
    result = build_result(
        args.skill_dir,
        require_ffmpeg=args.require_ffmpeg,
        require_ffprobe=args.require_ffprobe,
        require_render_tools=args.require_render_tools,
        require_node=args.require_node,
    )
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8", newline="\n")
    if args.json:
        print(json.dumps(result, indent=2))
    elif result["ok"]:
        print("PASS awsome-videos runtime preflight")
        for name, info in result["checks"].items():
            path = info.get("path") or info.get("executable") or info.get("skillDir")
            print(f"- {name}: ok ({path})")
    else:
        print("FAIL awsome-videos runtime preflight")
        for failure in result["failures"]:
            print(f"- {failure}")
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
