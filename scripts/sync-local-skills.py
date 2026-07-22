#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Synchronize versioned skill sources into the ignored local installation."""

from __future__ import annotations

import argparse
import hashlib
import os
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = ROOT / "skills"
DEFAULT_DESTINATION = ROOT / ".agents" / "skills"


def file_digest(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def source_files(source: Path) -> list[Path]:
    try:
        relative_source = source.relative_to(ROOT)
    except ValueError:
        return sorted(path for path in source.rglob("*") if path.is_file())

    result = subprocess.run(
        ["git", "-C", str(ROOT), "ls-files", "-z", "--", relative_source.as_posix()],
        check=True,
        capture_output=True,
    )
    return sorted(
        ROOT / os.fsdecode(item)
        for item in result.stdout.split(b"\0")
        if item
    )


def pending_files(source: Path, destination: Path) -> list[tuple[Path, Path]]:
    pending: list[tuple[Path, Path]] = []
    for source_path in source_files(source):
        destination_path = destination / source_path.relative_to(source)
        if not destination_path.is_file() or file_digest(source_path) != file_digest(destination_path):
            pending.append((source_path, destination_path))
    return pending


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Copy canonical skills/ sources into the ignored .agents/skills installation."
    )
    parser.add_argument("--check", action="store_true", help="Report drift without writing files.")
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE, help="Canonical skill source root.")
    parser.add_argument(
        "--destination",
        type=Path,
        default=DEFAULT_DESTINATION,
        help="Local installed skill root.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    source = args.source.resolve()
    destination = args.destination.resolve()
    if not source.is_dir():
        print(f"Canonical skill source does not exist: {source}", file=sys.stderr)
        return 2

    pending = pending_files(source, destination)
    if args.check:
        if pending:
            print(f"Local skill installation is out of date: {len(pending)} source-owned file(s) differ.")
            for source_path, _ in pending[:20]:
                print(f"- {source_path.relative_to(source).as_posix()}")
            if len(pending) > 20:
                print(f"- ... and {len(pending) - 20} more")
            return 1
        print(f"Local skill installation matches all {len(source_files(source))} canonical source files.")
        return 0

    for source_path, destination_path in pending:
        destination_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_path, destination_path)

    print(
        f"Synchronized {len(pending)} changed file(s) from {source} to {destination}; "
        "additional local files were preserved."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
