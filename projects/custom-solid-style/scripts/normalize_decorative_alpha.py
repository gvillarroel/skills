#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Make ordinary excerpt and fixture fills opaque, preserving declared alpha."""
import json
from pathlib import Path
import re

ROOT=Path(__file__).resolve().parents[3]
BUNDLE=ROOT / "skills/d3"
HIERARCHIES={"circle-pack","hierarchical-bars","icicle","sunburst","treemap"}
FUNCTIONS={"renderCirclePack","renderHierarchicalBars","renderIcicle","renderSunburst","renderTreemap"}
changed=[]
for path in [*(BUNDLE / "references/patterns").glob("*.md"),BUNDLE / "assets/examples/d3-animated-svg/gallery.js"]:
    before=path.read_text(encoding="utf-8")
    lines=before.splitlines(keepends=True)
    function=""
    result=[]
    for index,line in enumerate(lines):
        name=re.search(r"function\s+(render\w+)\s*\(",line)
        if name:
            function=name[1]
        if path.stem in HIERARCHIES or function in FUNCTIONS:
            line=line.replace('.attr("data-opacity-role", "semantic").attr("fill-opacity",', '.attr("fill-opacity",')
            # Position, containment, and area already encode the hierarchy.
            line=re.sub(r'\.attr\("fill-opacity",[^;\n]+?\)(?=\.attr|\s*;|\s*$)', '.attr("fill-opacity", 1)',line)
        future=''.join(lines[index:index+9])
        animated_fill='attr("attributeName", "fill-opacity")' in future
        if 'data-opacity-role' not in line and not animated_fill:
            line=re.sub(r'\.attr\("fill-opacity",\s*(?:\.\d+|0\.\d+)\)', '.attr("fill-opacity", 1)',line)
        result.append(line)
    after=''.join(result)
    if before!=after:
        path.write_text(after.rstrip()+"\n",encoding="utf-8")
        changed.append(path.relative_to(ROOT).as_posix())
(ROOT / "projects/custom-solid-style/artifacts/data/decorative-alpha-normalization.json").write_text(json.dumps({"files":changed,"hierarchyRule":"Depth/containment is already conveyed by geometry; use opaque hierarchy fills.","preserved":"Declared data/overlap alpha and fill-opacity animation baselines."},indent=2)+"\n",encoding="utf-8")
print(json.dumps({"changedCount":len(changed),"files":changed},indent=2))
