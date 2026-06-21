#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

DEFAULT_MAX_BYTES = 5 * 1024 * 1024
DISALLOWED_EXTENSIONS = {
    ".mp4",
    ".webm",
    ".mov",
    ".avi",
    ".mkv",
    ".gif",
    ".apng",
}


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def git_candidates(root: Path) -> list[Path]:
    result = subprocess.run(
        ["git", "ls-files", "-z", "--cached", "--others", "--exclude-standard"],
        cwd=root,
        check=True,
        capture_output=True,
    )
    raw = result.stdout.decode("utf-8", errors="replace")
    return [root / item for item in raw.split("\0") if item]


def rel(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def main() -> int:
    parser = argparse.ArgumentParser(description="Check files that are eligible for git before publishing.")
    parser.add_argument(
        "--max-mb",
        type=float,
        default=DEFAULT_MAX_BYTES / 1024 / 1024,
        help="Maximum allowed file size in MiB for versioned files.",
    )
    args = parser.parse_args()

    root = repo_root()
    max_bytes = int(args.max_mb * 1024 * 1024)
    findings: list[str] = []

    for path in git_candidates(root):
        if not path.is_file():
            continue
        relative = rel(path, root)
        suffix = path.suffix.lower()
        size = path.stat().st_size
        if suffix in DISALLOWED_EXTENSIONS:
            findings.append(f"{relative}: rendered media extension '{suffix}' is not allowed in git")
        if size > max_bytes:
            mb = size / 1024 / 1024
            findings.append(f"{relative}: {mb:.2f} MiB exceeds the {args.max_mb:.2f} MiB limit")

    if findings:
        print(f"Payload check failed with {len(findings)} finding(s):")
        for finding in findings:
            print(f"- {finding}")
        return 1

    print("Payload check passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
