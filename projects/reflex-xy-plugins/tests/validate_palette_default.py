#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["pillow==13.0.0"]
# ///
"""Verify fresh XY requests default to Colorset 1 after explicit Colorset 2."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import xml.etree.ElementTree as ET

from artifact_contract import color, inspect_html, inspect_png, inspect_svg, require


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--renderer", type=Path, required=True)
    parser.add_argument("--skill-dir", type=Path)
    parser.add_argument("--python", type=Path)
    parser.add_argument("--palettes", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    args.output_dir = args.output_dir.resolve()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    palettes = json.loads(args.palettes.read_text(encoding="utf-8"))["colorsets"]
    generic = {"version": 1, "factory": "chart", "title": "Independent supplied measurements",
        "data": {"x": [0, 2, 5, 9, 14], "y": [4, 7, 3, 11, 8]},
        "marks": [{"kind": "line", "args": ["x", "y"], "kwargs": {}},
                  {"kind": "scatter", "args": ["x", "y"], "kwargs": {}}]}
    cases = [
        ("preset-explicit-cs2", {"preset": "scatter", "colorset": "colorset2"}, "colorset2"),
        ("preset-omitted-after-cs2", {"preset": "scatter"}, "colorset1"),
        ("generic-explicit-cs2", {**generic, "colorset": "colorset2"}, "colorset2"),
        ("generic-omitted-after-cs2", generic, "colorset1"),
    ]
    rows = []
    for name, spec, expected in cases:
        output = args.output_dir / name
        command = [str(args.python.resolve()), str(args.renderer.resolve())] if args.python else ["uv", "run", "--script", str(args.renderer.resolve())]
        command += ["--output-dir", str(output)]
        if args.skill_dir:
            command += ["--skill-dir", str(args.skill_dir.resolve())]
        env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1", "PYTHONIOENCODING": "utf-8",
               "UV_CACHE_DIR": str(args.output_dir / "uv-cache")}
        row = {"case": name, "expected_palette": expected}
        try:
            done = subprocess.run(command, cwd=args.output_dir, env=env, input=json.dumps(spec),
                encoding="utf-8", capture_output=True, timeout=120)
            row.update(returncode=done.returncode, stderr=done.stderr)
            require(done.returncode == 0, "Renderer failed: " + done.stderr)
            metadata = json.loads(done.stdout)
            require(metadata["palette"] == expected, "Fresh request inherited the previous palette")
            row["metadata"] = metadata
            palette = palettes[expected]
            svg = output / metadata["files"]["svg"]
            row["native_svg"] = inspect_svg(svg, set(palette["allowed"]))
            row["native_png"] = inspect_png(output / metadata["files"]["png"], palette["roles"]["background"])
            row["offline_html"] = inspect_html(output / metadata["files"]["html"])
            expected_ink = palette["roles"]["primary" if expected == "colorset1" else "secondary"]
            ink_nodes = []
            for node in ET.parse(svg).getroot().iter():
                tag = node.tag.rsplit("}", 1)[-1]
                if tag not in {"circle", "path", "line", "rect", "polygon", "polyline"}:
                    continue
                if any(color(node.attrib[field]) == expected_ink for field in ["fill", "stroke"] if field in node.attrib):
                    ink_nodes.append(tag)
            require(ink_nodes, f"Actual native marks do not use {expected}'s expected ink {expected_ink}")
            row["native_mark_ink"] = {"paint": expected_ink, "geometry_nodes": len(ink_nodes)}
            saved = json.loads((output / metadata["files"]["spec"]).read_text(encoding="utf-8"))
            require(saved["colorset"] == expected, "Saved request has the wrong normalized palette")
            if "data" in spec:
                require(saved["data"] == spec["data"], "Default palette selection changed supplied data")
            source = (output / metadata["files"]["source"]).read_text(encoding="utf-8")
            compile(source, str(output / "chart.py"), "exec")
            require(expected_ink in source, "Editable Python omitted the expected mark ink")
            row["source_sha256"] = hashlib.sha256(source.encode()).hexdigest()
            row["passed"] = True
        except Exception as error:
            row["passed"] = False
            row["failure"] = f"{type(error).__name__}: {error}"
        rows.append(row)
        print(json.dumps({key: row[key] for key in ["case", "expected_palette", "passed"]}), flush=True)
    report = {"passed": all(row["passed"] for row in rows), "scope": "palette-default-only",
        "sequence": [row["expected_palette"] for row in rows],
        "renderer_sha256": hashlib.sha256(args.renderer.read_bytes()).hexdigest(), "cases": rows}
    (args.output_dir / "report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"passed": report["passed"], "cases": len(rows)}))
    raise SystemExit(0 if report["passed"] else 1)


if __name__ == "__main__":
    main()
