#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["xy==0.0.8"]
# ///
"""Exercise the installed XY native backend and three real output formats."""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import platform
import struct
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

from xy_colorsets import css, load_palette, theme


def outside_bundle(path: Path) -> Path:
    resolved = path.resolve()
    bundle = Path(__file__).resolve().parents[1]
    if resolved.is_relative_to(bundle):
        raise ValueError("Diagnostic outputs must be outside the skill bundle")
    return resolved


def run_probe(output_dir: Path, colorset: str = "colorset1") -> dict:
    import xy

    primary = load_palette(colorset)["roles"]["primary"]
    chart = xy.chart(
        xy.line([0, 1, 2, 3], [1, 3, 2, 4], name="Signal", color=primary),
        xy.scatter([0, 1, 2, 3], [1, 3, 2, 4], color=primary, size=7, opacity=1, stroke_width=0),
        xy.x_axis(label="Sample"), xy.y_axis(label="Value"),
        theme(colorset),
        title="XY environment probe", width=640, height=360,
    )
    memory = chart.memory_report()
    if memory.get("backend") != "native":
        raise RuntimeError("XY did not report its required native compute backend")
    output_dir.mkdir(parents=True, exist_ok=True)
    chart.to_html(output_dir / "chart.html", custom_css=css(colorset))
    chart.to_svg(str(output_dir / "chart.svg"))
    chart.to_png(str(output_dir / "chart.png"), scale=1)
    files = {}
    for name in ("chart.html", "chart.svg", "chart.png"):
        path = output_dir / name
        data = path.read_bytes()
        if not data:
            raise RuntimeError(f"Empty output: {name}")
        files[name] = {
            "path": str(path), "bytes": len(data),
            "sha256": hashlib.sha256(data).hexdigest(),
        }
    svg = ET.fromstring((output_dir / "chart.svg").read_text(encoding="utf-8"))
    if not svg.tag.endswith("svg"):
        raise RuntimeError("SVG root is invalid")
    png = (output_dir / "chart.png").read_bytes()
    if png[:8] != b"\x89PNG\r\n\x1a\n" or png[12:16] != b"IHDR":
        raise RuntimeError("PNG header is invalid")
    dimensions = struct.unpack(">II", png[16:24])
    if dimensions != (640, 360):
        raise RuntimeError(f"Unexpected PNG dimensions: {dimensions}")
    html = (output_dir / "chart.html").read_text(encoding="utf-8")
    if "<script" not in html or "XY environment probe" not in html:
        raise RuntimeError("HTML export is missing its client or chart title")
    return {
        "xy_version": importlib.metadata.version("xy"),
        "colorset": colorset,
        "backend": memory["backend"],
        "png_dimensions": list(dimensions),
        "memory": memory, "files": files,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--colorset", choices=("colorset1", "colorset2"), default="colorset1")
    args = parser.parse_args()
    try:
        output_dir = outside_bundle(args.output_dir)
        report_path = outside_bundle(args.report)
        targets = {output_dir / name for name in ("chart.html", "chart.svg", "chart.png")}
        if report_path in targets or report_path == output_dir:
            raise ValueError("Report path must be separate from chart output paths")
    except ValueError as error:
        parser.error(str(error))
    report = {
        "schema_version": 1, "passed": False,
        "python_version": platform.python_version(),
        "platform": platform.platform(),
    }
    try:
        report.update(run_probe(output_dir, args.colorset))
        report["passed"] = True
    except Exception as error:
        report["error"] = {"type": type(error).__name__, "message": str(error)}
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    if report["passed"]:
        print(f"XY {report['xy_version']}: native backend and HTML/SVG/PNG export passed.")
    else:
        print(f"XY diagnostic failed: {report['error']['message']}", file=sys.stderr)
    print(f"Report: {report_path}")
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
