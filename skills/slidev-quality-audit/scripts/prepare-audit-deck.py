#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Prepare a task-owned scratch Slidev deck with explicit local npm paths."""
from __future__ import annotations

import argparse
import json
import os
import shlex
import shutil
import subprocess
from pathlib import Path

BUNDLE = Path(__file__).resolve().parent.parent


def prepare(deck: Path, workspace: Path) -> Path:
    deck = deck.resolve()
    workspace = workspace.resolve()
    if deck == workspace or not deck.is_relative_to(workspace) or deck.is_relative_to(BUNDLE):
        raise ValueError("Choose a child deck directory inside the current task workspace, outside the skill bundle")
    package = deck / "package.json"
    content = package.read_text(encoding="utf-8") if package.exists() else (BUNDLE / "assets/templates/package.json").read_text(encoding="utf-8")
    data = json.loads(content)
    if not isinstance(data, dict) or any(not isinstance(data.get(key, {}), dict) for key in ("dependencies", "devDependencies")):
        raise ValueError("The deck package must be a JSON object with dependency objects")
    dependencies = {**data.get("dependencies", {}), **data.get("devDependencies", {})}
    missing = [name for name in ("@slidev/cli", "playwright", "tsx") if name not in dependencies]
    if missing:
        raise ValueError("The deck package must declare: " + ", ".join(missing) + ". Preserve an existing deck's dependency choices and use its normal setup workflow")
    deck.mkdir(parents=True, exist_ok=True)
    if not package.exists():
        package.write_text(content, encoding="utf-8")
        print("Created the bundled scratch dependency package")
    else:
        print("Retained the existing dependency package")
    return package


def npm_command() -> list[str]:
    npm = shutil.which("npm")
    if not npm:
        raise ValueError("Install Node.js and npm before preparing the deck")
    if os.name == "nt":
        cli = Path(npm).parent / "node_modules/npm/bin/npm-cli.js"
        node = shutil.which("node")
        if not cli.is_file() or not node:
            raise ValueError("A Node.js npm CLI installation is required for direct Windows execution")
        return [node, str(cli)]
    return [npm]


def display(command: list[str]) -> str:
    return subprocess.list2cmdline(command) if os.name == "nt" else shlex.join(command)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--deck", type=Path, required=True, help="Child directory owned by the current task workspace")
    parser.add_argument("--prepare-only", action="store_true", help="Validate/create the package without installing dependencies")
    args = parser.parse_args()
    try:
        package = prepare(args.deck, Path.cwd())
        deck = package.parent
        install = npm_command() + (["ci"] if (deck / "package-lock.json").is_file() else ["install", "--no-package-lock"]) + ["--prefix", str(deck)]
        print("Deck package: " + str(package), flush=True)
        print("Install command: " + display(install), flush=True)
        if not args.prepare_only:
            subprocess.run(install, cwd=deck, check=True)
        print("Write the supplied slide to: " + str(deck / "slides.md"))
        print("Build command: " + display(npm_command() + ["--prefix", str(deck), "run", "build"]))
        return 0
    except (ValueError, OSError, subprocess.CalledProcessError) as exc:
        parser.error(str(exc))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
