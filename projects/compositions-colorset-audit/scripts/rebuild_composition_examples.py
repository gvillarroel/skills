#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Regenerate both authored synchronized SVG examples from their current briefs."""
from pathlib import Path
import subprocess
import sys

root = Path(__file__).resolve().parents[3]
skill = root / "skills/compose-synchronized-svg"
scratch = root / "projects/compositions-colorset-audit/artifacts/manifests"
scratch.mkdir(parents=True, exist_ok=True)
for brief, name in (("composition-brief.json", "inference-pulse"), ("heatwave-tree-brief.json", "heatwave-tree")):
    source = skill / "assets/examples/compose-synchronized-svg" / brief
    plan = scratch / f"{name}-plan.json"
    output = source.with_name(f"{name}.svg")
    subprocess.run([sys.executable, str(skill / "scripts/compile_synchronized_svg_plan.py"), "--brief", str(source), "--output", str(plan), "--force", "--json"], check=True)
    subprocess.run([sys.executable, str(skill / "scripts/compose_synchronized_svg.py"), "--spec", str(plan), "--output", str(output), "--force", "--json"], check=True)
