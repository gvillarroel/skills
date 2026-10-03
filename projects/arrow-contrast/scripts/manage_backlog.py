#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Record arrow validation without promoting previous broader release statuses."""
import argparse
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[3]
BASELINE = "45d51fea02490eef1ae5a8b2e83440827872a527"
OWNERS = {"mermaid", "plantuml-colorset-renderer", "echarts-animated-svg",
          "slidev-echarts", "slidev-animejs", "slidev-quality-audit", "d3",
          "threejs-animated-3d", "procedural-svg-animation", "svg-brief-design",
          "compose-synchronized-svg", "diagram-composition", "usefulcharts-style",
          "hyperframes-explainer", "video", "manim-svg-video"}
NOTE = "Arrow contrast revision 2026-10-03: [shaft/head contrast, terminal placement and validation](evaluations/arrow-contrast/validation-20261003.md)."


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--state", choices=("in-progress", "validating"), default="in-progress")
    parser.add_argument("--restore", action="store_true")
    parser.add_argument("--skills", nargs="+", choices=sorted(OWNERS), default=sorted(OWNERS))
    args = parser.parse_args()
    baseline = subprocess.check_output(["git", "show", f"{BASELINE}:SKILLS.md"], cwd=ROOT, text=True, encoding="utf-8")
    previous = {line.split("|")[1].strip(): line.split("|")[2].strip()
                for line in baseline.splitlines() if line.startswith("| ") and len(line.split("|")) >= 6}
    path = ROOT / "SKILLS.md"
    lines = path.read_text(encoding="utf-8").splitlines()
    for index, line in enumerate(lines):
        fields = line.split("|")
        if not line.startswith("| ") or len(fields) < 6 or fields[1].strip() not in args.skills:
            continue
        name = fields[1].strip()
        fields[2] = " " + (previous[name] if args.restore else f"`{args.state}`") + " "
        if NOTE not in fields[-2]:
            fields[-2] = fields[-2].rstrip() + " " + NOTE + " "
        lines[index] = "|".join(fields)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Recorded arrow revision for {len(args.skills)} relevant bundles.")


if __name__ == "__main__":
    main()
