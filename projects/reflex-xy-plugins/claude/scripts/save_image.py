#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Save a native XY PNG as a new project-local export without invoking a model."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import struct
import sys
import unicodedata
from uuid import uuid4

MAX_IMAGE_BYTES = 32 * 1024 * 1024
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


def save_image(project_dir: Path, source_dir: Path, title: str) -> dict:
    project = project_dir.resolve(strict=True)
    if not project.is_dir():
        raise ValueError("The current project is not a directory.")
    chart_root = project / ".xy-charts"
    if chart_root.resolve(strict=True) != chart_root or not chart_root.is_dir():
        raise ValueError("The chart directory must be a real project-local directory.")
    source = source_dir.resolve(strict=True)
    if not source.is_relative_to(chart_root) or source == chart_root:
        raise ValueError("Choose an existing chart from this project's chart directory.")
    exports = chart_root / "exports"
    if source.is_relative_to(exports):
        raise ValueError("The source must be a rendered chart, not a saved export.")
    image = source / "chart.png"
    if image.resolve(strict=True) != image or not image.is_file():
        raise ValueError("The chart image must be a regular file in its render directory.")
    if not 33 <= image.stat().st_size <= MAX_IMAGE_BYTES:
        raise ValueError("The chart image is empty or exceeds the 32 MiB save limit.")
    with image.open("rb") as source_file:
        content = source_file.read(MAX_IMAGE_BYTES + 1)
    if len(content) > MAX_IMAGE_BYTES:
        raise ValueError("The chart image exceeds the 32 MiB save limit.")
    if content[:8] != PNG_SIGNATURE or content[12:16] != b"IHDR" or content[8:12] != b"\x00\x00\x00\r":
        raise ValueError("The rendered image is not a PNG.")
    width, height = struct.unpack(">II", content[16:24])
    if not 1 <= width <= 8192 or not 1 <= height <= 8192:
        raise ValueError("The PNG dimensions exceed the supported save limit.")
    if exports.resolve(strict=False) != exports:
        raise ValueError("The export directory must not redirect through a symlink or junction.")
    exports.mkdir(exist_ok=True)
    if exports.resolve(strict=True) != exports or not exports.is_dir():
        raise ValueError("The export directory must stay inside the current project.")
    normalized = unicodedata.normalize("NFKD", title).encode("ascii", "ignore").decode("ascii").lower()
    stem = re.sub(r"[^a-z0-9]+", "-", normalized).strip("-")[:48].rstrip("-") or "chart"
    destination = exports / f"{stem}-{uuid4().hex[:12]}.png"
    # Exclusive creation prevents repeat saves from replacing an existing file.
    with destination.open("xb") as target:
        target.write(content)
    return {
        "schema_version": 1,
        "path": str(destination),
        "name": destination.name,
        "bytes": len(content),
        "sha256": hashlib.sha256(content).hexdigest(),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-dir", type=Path, required=True)
    parser.add_argument("--source-dir", type=Path, required=True)
    args = parser.parse_args()
    try:
        raw = sys.stdin.buffer.read(8193)
        if len(raw) > 8192:
            raise ValueError("The image save request is too large.")
        request = json.loads(raw)
        if not isinstance(request, dict) or set(request) != {"title"} or not isinstance(request["title"], str) or len(request["title"]) > 1024:
            raise ValueError("The image save request must contain one bounded title.")
        print(json.dumps(save_image(args.project_dir, args.source_dir, request["title"]), ensure_ascii=False))
        return 0
    except (OSError, ValueError, TypeError, json.JSONDecodeError) as error:
        print(json.dumps({"error": {"code": "save_image_failed", "message": str(error)}}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
