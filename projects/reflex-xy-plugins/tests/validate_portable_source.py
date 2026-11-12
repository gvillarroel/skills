#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["pillow==13.0.0"]
# ///
"""Run only downloaded chart.py and compare its native paint and image pixels."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

from PIL import Image, ImageChops

from artifact_contract import inspect_html, inspect_svg, require


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact-root", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--palettes", type=Path, required=True)
    parser.add_argument("--cases", default="generic-mixed-colorset1,generic-mixed-colorset2,sankey-colorset2,pie-colorset1,facets-colorset2")
    parser.add_argument("--python", type=Path, required=True)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    palettes = json.loads(args.palettes.read_text(encoding="utf-8"))["colorsets"]
    rows = []
    for name in args.cases.split(","):
        source = args.artifact_root / name
        dest = args.output_dir / name
        dest.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source / "chart.py", dest / "chart.py")
        palette = palettes["colorset1" if name.endswith("colorset1") else "colorset2"]
        row = {"case": name}
        try:
            env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1", "PYTHONIOENCODING": "utf-8"}
            done = subprocess.run([str(args.python), "chart.py"], cwd=dest, env=env,
                                  capture_output=True, text=True, encoding="utf-8", timeout=90)
            row.update(returncode=done.returncode, stdout=done.stdout, stderr=done.stderr)
            require(done.returncode == 0, "Downloaded chart source could not execute independently")
            original = inspect_svg(source / "chart.svg", set(palette["allowed"]), allow_derived=True)
            rebuilt = inspect_svg(dest / "chart.svg", set(palette["allowed"]), allow_derived=True)
            row["original_svg"] = original
            row["rebuilt_svg"] = rebuilt
            require(original == rebuilt, "Downloaded chart source changed native SVG dimensions, geometry, or paints")
            with Image.open(source / "chart.png") as before, Image.open(dest / "chart.png") as after:
                require(before.size == after.size, "Downloaded chart source changed PNG dimensions")
                extent = ImageChops.difference(before.convert("RGB"), after.convert("RGB")).getbbox()
                row["png_difference_extent"] = extent
                require(extent is None, "Downloaded chart source changed native PNG pixels")
            row["html"] = inspect_html(dest / "chart.html")
            row["passed"] = True
        except Exception as error:
            row["passed"] = False
            row["failure"] = f"{type(error).__name__}: {error}"
        rows.append(row)
        print(json.dumps({key: row[key] for key in ["case", "passed"]}), flush=True)
    report = {"passed": all(row["passed"] for row in rows), "cases": rows}
    (args.output_dir / "report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"passed": report["passed"], "cases": len(rows)}))
    raise SystemExit(0 if report["passed"] else 1)


if __name__ == "__main__":
    main()
