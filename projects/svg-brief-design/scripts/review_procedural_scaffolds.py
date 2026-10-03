#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["resvg-py==0.2.6", "Pillow==11.3.0", "defusedxml==0.7.1"]
# ///
"""Render all original generator families for a local visual review."""
import json
from pathlib import Path
import sys
from PIL import Image, ImageDraw

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "skills/svg-brief-design/scripts"))
from scaffold import defaults, build
from render_svg import render


def main():
    folder = REPO / "projects/svg-brief-design/artifacts/reviews/procedural-boxed-20260926"
    folder.mkdir(parents=True, exist_ok=False)
    sheet = Image.new("RGB", (4*330, 2*365), "#eeeeee")
    draw = ImageDraw.Draw(sheet)
    records = []
    for i, kind in enumerate(("radial", "globe", "wave", "flow", "panel", "frond", "composition")):
        recipe = defaults(kind)
        if kind == "composition":
            recipe["parameters"]["items"] = [
                {"id": "left", "kind": "frond", "box": [30, 180, 205, 250], "parameters": {"rotation": -42, "pairs": 9, "spread": .28}},
                {"id": "right", "kind": "frond", "box": [245, 180, 205, 250], "parameters": {"rotation": 42, "pairs": 11, "spread": .3}}]
        source = folder / f"{kind}.svg"
        source.write_text(build(recipe), encoding="utf-8")
        source.with_suffix(".json").write_text(json.dumps(recipe, indent=2))
        records.append({"kind": kind, **render(source, source.with_suffix(".png"), 320)})
        with Image.open(source.with_suffix(".png")) as preview:
            sheet.paste(preview, ((i%4)*330+5, (i//4)*365+28))
        draw.text(((i%4)*330+8, (i//4)*365+8), kind, fill="black")
    sheet.save(folder / "contact-sheet.jpg", quality=94)
    (folder / "render-audit.json").write_text(json.dumps(records, indent=2))
    print(folder / "contact-sheet.jpg")


if __name__ == "__main__":
    main()
