#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["pillow>=11.0"]
# ///
"""Normalize reviewed published vector paint defaults and raster-only Ditaa assets."""
import json
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from PIL import Image
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "skills/mermaid/scripts"))
from palette_paints import COLORSETS, require_svg_palette, svg_paints
rows=[]
for skill in ("mermaid", "plantuml-colorset-renderer"):
    for path in (ROOT / "skills" / skill / "assets/examples").rglob("*.svg"):
        if "node_modules" in path.parts:
            continue
        colorset = "colorset1" if "colorset1" in path.parts or "plantuml-colorset-renderer-cs1" in path.parts else "colorset2"
        tree=ET.parse(path)
        changes=svg_paints(tree.getroot(),colorset,normalize=True)
        require_svg_palette(tree.getroot(),colorset)
        if changes:
            tree.write(path, encoding="utf-8", xml_declaration=True)
        rows.append({"path":path.relative_to(ROOT).as_posix(),"colorset":colorset,"changed":bool(changes),"remapped":changes})
for folder,colorset in [("plantuml-colorset-renderer","colorset2"),("plantuml-colorset-renderer-cs1","colorset1")]:
    for path in (ROOT / "skills/plantuml-colorset-renderer/assets/examples" / folder / "png").glob("*.png"):
        colors=COLORSETS[colorset]["allowed"]
        palette=Image.new("P",(1,1))
        channels=[int(color[i:i+2],16) for color in colors for i in (1,3,5)]
        palette.putpalette(channels+channels[:3]*(256-len(colors)))
        with Image.open(path) as source:
            mapped=source.convert("RGB").quantize(palette=palette,dither=Image.Dither.NONE).convert("RGB")
            changed=source.convert("RGB").tobytes()!=mapped.tobytes()
            if changed:
                mapped.save(path)
        rows.append({"path":path.relative_to(ROOT).as_posix(),"colorset":colorset,"changed":changed,"rasterQuantization":True})
out=ROOT / "projects/colorset-audit/artifacts/data/normalized-published-diagrams.json"
out.parent.mkdir(parents=True,exist_ok=True)
out.write_text(json.dumps(rows,indent=2)+"\n",encoding="utf-8")
print(json.dumps({"checked":len(rows),"changed":sum(row["changed"] for row in rows),"inventory":out.relative_to(ROOT).as_posix()}))
