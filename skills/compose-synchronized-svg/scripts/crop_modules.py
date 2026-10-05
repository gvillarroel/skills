#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["pillow>=10.0.0"]
# ///
"""Capture compact-plan module crops at the overview's actual pixel scale."""

from __future__ import annotations

import argparse
import json
import math
import re
from pathlib import Path

from PIL import Image


def crop_modules(plan: dict, screenshot: Path, output_dir: Path) -> dict:
    if plan.get("navigation"):
        raise ValueError("World plans need the browser audit's camera-anchor crops, not overview crops.")
    x, y, width, height = map(float, plan["viewBox"])
    if width <= 0 or height <= 0:
        raise ValueError("The plan viewBox must have positive dimensions.")
    with Image.open(screenshot) as image:
        sx, sy = image.width / width, image.height / height
        if abs(sx - sy) > max(sx, sy) * 0.01:
            raise ValueError("Screenshot aspect ratio differs from the plan; use the auditor's SVG screenshot.")
        output_dir.mkdir(parents=True, exist_ok=True)
        crops = []
        for module in plan["modules"]:
            if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", module["id"]):
                raise ValueError("Module IDs must be lowercase hyphen-case, not file paths.")
            mx, my, mw, mh = map(float, module["region"])
            box = (math.floor((mx - x) * sx), math.floor((my - y) * sy),
                   math.ceil((mx + mw - x) * sx), math.ceil((my + mh - y) * sy))
            if box[0] < 0 or box[1] < 0 or box[2] > image.width or box[3] > image.height:
                raise ValueError(f"Module {module['id']!r} escapes the overview screenshot.")
            if box[2] <= box[0] or box[3] <= box[1]:
                raise ValueError(f"Module {module['id']!r} has no visible crop area.")
            target = output_dir / f"{module['id']}.png"
            if target.resolve() == screenshot.resolve():
                raise ValueError("A module crop must not replace its input screenshot.")
            image.crop(box).save(target)
            crops.append({"id": module["id"], "path": str(target), "pixelBox": list(box)})
    return {"ok": True, "screenshot": str(screenshot), "scale": sx, "upscaled": False, "modules": crops}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--screenshot", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    bundle = Path(__file__).resolve().parent.parent
    destinations = [args.output_dir.resolve(), args.report.resolve()]
    if any(path.is_relative_to(bundle) for path in destinations):
        parser.error("The skill bundle is read-only; keep generated crops and reports in the workspace.")
    if args.report.resolve() in {args.plan.resolve(), args.screenshot.resolve()}:
        parser.error("The report must not replace its input plan or screenshot.")
    try:
        plan = json.loads(args.plan.read_text(encoding="utf-8-sig"))
        report = crop_modules(plan, args.screenshot, args.output_dir)
    except (ValueError, KeyError, TypeError, OSError) as error:
        report = {"ok": False, "error": str(error)}
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
