#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Scaffold a ratio-specific video project and blank scene contract."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import re
import sys


ID_RE = re.compile(r"^[a-z][a-z0-9-]*$")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Scaffold a video project without generating specialist assets.")
    parser.add_argument("project", type=Path)
    parser.add_argument("--id", required=True)
    parser.add_argument("--width", required=True, type=int)
    parser.add_argument("--height", required=True, type=int)
    parser.add_argument("--fps", required=True, type=float)
    parser.add_argument("--duration", required=True, type=float)
    parser.add_argument("--background", default="#ffffff")
    parser.add_argument("--safe-margin", type=int, default=0)
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--json", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    failures: list[str] = []
    if not ID_RE.fullmatch(args.id):
        failures.append("--id must be lowercase hyphen-case")
    if args.width <= 0 or args.height <= 0 or args.fps <= 0 or args.duration <= 0:
        failures.append("width, height, fps, and duration must be positive")
    if args.safe_margin < 0 or args.safe_margin * 2 >= min(args.width, args.height):
        failures.append("--safe-margin must fit inside the canvas")
    contract_path = args.project / "source" / "scene-contract.json"
    if contract_path.exists() and not args.force:
        failures.append(f"contract exists; pass --force to overwrite: {contract_path}")
    if failures:
        report = {"schemaVersion": 1, "ok": False, "passed": False, "failures": failures}
    else:
        divisor = math.gcd(args.width, args.height)
        contract = {
            "schemaVersion": 1,
            "id": args.id,
            "canvas": {
                "width": args.width,
                "height": args.height,
                "aspectRatio": f"{args.width // divisor}:{args.height // divisor}",
                "fps": args.fps,
                "durationSeconds": args.duration,
                "background": args.background,
                "safeArea": {edge: args.safe_margin for edge in ("top", "right", "bottom", "left")},
            },
            "masterClock": {"mode": "deterministic", "loop": False},
            "elements": [],
            "events": [],
            "tracks": [],
            "interactions": [],
        }
        for relative in ("source", "src", "artifacts/assets", "artifacts/videos", "artifacts/reviews"):
            (args.project / relative).mkdir(parents=True, exist_ok=True)
        contract_path.write_text(json.dumps(contract, indent=2) + "\n", encoding="utf-8", newline="\n")
        report = {
            "schemaVersion": 1,
            "ok": True,
            "passed": True,
            "project": str(args.project),
            "sceneContract": str(contract_path),
            "canvas": contract["canvas"],
        }
    if args.json:
        print(json.dumps(report, indent=2))
    elif report.get("ok"):
        print(f"PASS video project scaffold: {contract_path}")
    else:
        for failure in report.get("failures", []):
            print(f"FAIL: {failure}", file=sys.stderr)
    return 0 if report.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
