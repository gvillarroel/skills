#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Declare reviewed data/overlap alpha, leaving decorative translucency opaque."""
import json
from pathlib import Path
import re

ROOT=Path(__file__).resolve().parents[3]
BUNDLE=ROOT / "skills/d3"
# These mechanisms need overlapping fills to expose shared or nested regions.
OVERLAP={"task-overlap","task-overlap-dense","radar","chord","directed-chord","alluvial","cluster-hulls","forecast-fan","bollinger-bands","difference-chart","polygon-clipping","solar-terminator","scatterplot-matrix","occlusion-labels","bubble-map","focus-context"}
FUNCTIONS={"renderTaskOverlap","renderTaskOverlapDense","renderRadar","renderChord","renderDirectedChord","renderAlluvial","renderClusterHulls","renderForecastFan","renderBollingerBands","renderDifferenceChart","renderPolygonClipping","renderSolarTerminator","renderScatterplotMatrix","renderOcclusionLabels","renderBubbleMap","renderFocusContext"}
changed=[]


def annotate(text,pattern=None):
    lines=text.splitlines(keepends=True)
    function=""
    result=[]
    for line in lines:
        name=re.search(r"function\s+(render\w+)\s*\(",line)
        if name:
            function=name[1]
        # A data accessor explicitly encodes value/state, rather than a fixed tint.
        dynamic=re.search(r'\.attr\("(?:fill-opacity|opacity)",\s*(?:d\s*=>|\(d(?:\s*,\s*i)?\)\s*=>)',line)
        overlap=pattern in OVERLAP or function in FUNCTIONS
        static=re.search(r'\.attr\("(?:fill-opacity|opacity)",\s*(\.\d+|0\.\d+)\)',line)
        if dynamic or overlap and static:
            # The .96 task-dot tint is ordinary paint, not the set intersections.
            if not dynamic and (pattern=="task-overlap-dense" or function=="renderTaskOverlapDense") and float(static[1])>.5:
                result.append(line)
                continue
            if 'data-opacity-role' not in line:
                match=dynamic or static
                line=line[:match.start()]+'.attr("data-opacity-role", "semantic")'+line[match.start():]
        result.append(line)
    return ''.join(result)


for path in (BUNDLE / "references/patterns").glob("*.md"):
    before=path.read_text(encoding="utf-8")
    after=annotate(before,path.stem)
    # These ordinary categorical marks encode value using geometry already.
    if path.stem in {"circular-bar","er-schema","gantt-rollout"}:
        after=re.sub(r'\.attr\("fill-opacity",\s*\.\d+\)', '.attr("fill-opacity", 1)',after)
    if before!=after:
        path.write_text(after.rstrip()+"\n",encoding="utf-8")
        changed.append(path.relative_to(ROOT).as_posix())

gallery=BUNDLE / "assets/examples/d3-animated-svg/gallery.js"
before=gallery.read_text(encoding="utf-8")
after=annotate(before)
# The cartogram's scaled area is its value encoding; fill is categorical paint.
after=after.replace('.attr("fill-opacity", .32 + region.v * .18).attr("stroke", region.c).attr("stroke-width", 2)', '.attr("fill-opacity", 1).attr("stroke", "none")')
gallery.write_text(after,encoding="utf-8")
changed.append(gallery.relative_to(ROOT).as_posix())
(ROOT / "projects/custom-solid-style/artifacts/data/semantic-alpha-declarations.json").write_text(json.dumps({"files":changed,"overlapPatterns":sorted(OVERLAP),"rule":"Data accessors explicitly declare semantic value/state alpha; reviewed overlap/nested-region paths explicitly declare semantic alpha; ordinary constant tints remain opaque."},indent=2)+"\n",encoding="utf-8")
print(json.dumps({"changedCount":len(changed),"files":changed},indent=2))
