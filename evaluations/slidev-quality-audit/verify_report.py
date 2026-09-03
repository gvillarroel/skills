#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

"""Verify the wrapped-inline Slidev quality-audit regression artifacts."""

from __future__ import annotations

import argparse
import json
import struct
from pathlib import Path


PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("report", type=Path)
    parser.add_argument("--screenshots", type=Path, required=True)
    return parser.parse_args()


def png_dimensions(path: Path) -> tuple[int, int]:
    data = path.read_bytes()
    if len(data) < 24 or data[:8] != PNG_SIGNATURE or data[12:16] != b"IHDR":
        raise AssertionError(f"Not a valid PNG with an IHDR chunk: {path}")
    return struct.unpack(">II", data[16:24])


def main() -> None:
    args = parse_args()
    report = json.loads(args.report.read_text(encoding="utf-8"))

    assert report["slideCount"] == 2, report["slideCount"]
    assert report["stateCount"] == 2, report["stateCount"]
    assert report["severityCounts"].get("error", 0) == 0, report["severityCounts"]

    covered = [item for item in report["findings"] if item["ruleId"] == "covered-content"]
    wrapped_false_positives = [
        item
        for item in covered
        if item["slide"] == 1 or "wrapped-inline" in item["target"]
    ]
    assert not wrapped_false_positives, wrapped_false_positives

    true_controls = [
        item
        for item in covered
        if item["slide"] == 2 and "covered-target" in item["target"]
    ]
    assert len(true_controls) == 1, covered

    for slide in (1, 2):
        screenshot = args.screenshots / f"slide-{slide:03d}-click-00.png"
        assert screenshot.is_file() and screenshot.stat().st_size > 10_000, screenshot
        assert png_dimensions(screenshot) == (1280, 720), (screenshot, png_dimensions(screenshot))

    print(
        "PASS: two slides and two states; no error findings; wrapped inline text "
        "has no covered-content false positive; genuine overlay control detected; "
        "both screenshots are valid 1280x720 PNGs."
    )


if __name__ == "__main__":
    main()
