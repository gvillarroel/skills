#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Render a content-sized native ECharts 6.1.0 conceptual graph in the workspace."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import subprocess


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="Node/edge JSON; see the compact-diagrams reference.")
    parser.add_argument("--svg", type=Path, required=True)
    parser.add_argument("--option", type=Path, required=True)
    parser.add_argument("--review", type=Path, required=True)
    parser.add_argument("--probe", action="store_true", help="Record expected layout rejection as accepted:false without a delivered SVG; use fresh comparison paths.")
    parser.add_argument("--no-install", action="store_true", help="Require an existing workspace ECharts 6.1.0 dependency.")
    args = parser.parse_args()
    workspace = Path.cwd().resolve()
    bundle = Path(__file__).resolve().parents[1]
    for output in (args.svg, args.option, args.review):
        if not output.resolve().is_relative_to(workspace) or output.resolve().is_relative_to(bundle):
            parser.error("Write generated artifacts inside the current task workspace.")
    if args.probe and (args.svg.exists() or args.option.exists()):
        parser.error("Probe comparisons need fresh SVG/option paths so rejected input cannot leave a stale candidate.")
    node = shutil.which("node")
    if not node:
        parser.error("Node is required for native ECharts rendering.")
    package = workspace / "node_modules/echarts/package.json"
    installed = package.is_file() and json.loads(package.read_text(encoding="utf-8")).get("version") == "6.1.0"
    if not installed:
        if args.no_install:
            parser.error("Install echarts@6.1.0 in the task workspace or omit --no-install.")
        npm = shutil.which("npm.cmd") or shutil.which("npm")
        if not npm:
            parser.error("npm is required to install the pinned workspace dependency.")
        result = subprocess.run([npm, "install", "--prefix", str(workspace), "--no-audit", "--no-fund", "echarts@6.1.0"], cwd=workspace)
        if result.returncode:
            return result.returncode
    template = bundle / "assets/templates/render-concept-graph.mjs"
    command = [node, str(template), str(args.input), str(args.svg), str(args.option), str(args.review)]
    if args.probe:
        command.append("--probe")
    result = subprocess.run(command, cwd=workspace)
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
