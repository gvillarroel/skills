#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["resvg-py==0.2.6", "Pillow==11.3.0", "defusedxml==0.7.1"]
# ///
"""Render an original static SVG for visual inspection; never infer semantics."""
import argparse
import io
import json
import math
from pathlib import Path
import re

from defusedxml import ElementTree as ET
from PIL import Image
import resvg_py


def render(source, output, size=960, font_dir=None):
    raw = source.read_bytes()
    if not raw or len(raw) > 2_000_000:
        raise ValueError("SVG must be nonempty and below 2 MB")
    text = raw.decode("utf-8-sig")
    if re.search(r"<!ENTITY|<!DOCTYPE|<\?xml-stylesheet|@import|@font-face", text, re.I):
        raise ValueError("External definitions are unsupported")
    root = ET.fromstring(text)
    if root.tag != "{http://www.w3.org/2000/svg}svg":
        raise ValueError("Expected an SVG root")
    colorset = root.get("data-colorset", "colorset1")
    contract = json.loads((Path(__file__).resolve().parents[1] / "assets/palettes/colorsets.json").read_text(encoding="utf-8"))["colorsets"]
    if colorset not in contract:
        raise ValueError("SVG colorset must be colorset1 or colorset2")
    allowed = set(contract[colorset]["allowed"])
    paint_keys = {"fill", "stroke", "color", "stop-color", "flood-color", "lighting-color"}
    for element in root.iter():
        paints = [value for key,value in element.attrib.items() if key in paint_keys]
        css = element.get("style", "")
        if element.tag.endswith("}style"):
            css += element.text or ""
        paints.extend(re.findall(r"(?:fill|stroke|color|stop-color|flood-color|lighting-color)\s*:\s*([^;}]+)", css))
        for paint in paints:
            paint = paint.strip()
            if paint not in allowed and paint not in {"none", "currentColor", "inherit", "transparent"} and not re.fullmatch(r"url\(\s*['\"]?#[\w-]+['\"]?\s*\)", paint):
                raise ValueError(f"Authored SVG paint {paint!r} violates {colorset}")
    box = [float(v) for v in root.get("viewBox", "").replace(",", " ").split()]
    if len(box) != 4 or not all(math.isfinite(v) for v in box) or min(box[2:]) <= 0:
        raise ValueError("Expected a finite positive viewBox")
    forbidden = {"script", "foreignObject", "image", "iframe", "animate", "animateMotion", "animateTransform", "set"}
    for element in root.iter():
        if element.tag.rsplit("}", 1)[-1] in forbidden:
            raise ValueError("Only static vector SVGs are supported")
        for key, value in element.attrib.items():
            local = key.rsplit("}", 1)[-1].lower()
            if local.startswith("on") or (local == "href" and not value.startswith("#")):
                raise ValueError("Executable and external attributes are unsupported")
    if any(not target.strip().startswith("#") for target in re.findall(r"url\(\s*[\"']?([^\)\"']+)", text, re.I)):
        raise ValueError("External resources are unsupported")
    scale = size / max(box[2:])
    width, height = max(1, round(box[2] * scale)), max(1, round(box[3] * scale))
    options = {"font_family": "DejaVu Sans", "sans_serif_family": "DejaVu Sans"}
    if font_dir:
        options.update(font_dirs=[str(font_dir)], skip_system_fonts=True)
    image = Image.open(io.BytesIO(resvg_py.svg_to_bytes(svg_string=text, width=width, height=height, **options))).convert("RGBA")
    alpha = image.getchannel("A")
    bounds = alpha.getbbox()
    if bounds is None:
        raise ValueError("SVG renders empty")
    visible = Image.alpha_composite(Image.new("RGBA", image.size, "white"), image).convert("RGB")
    if visible.getextrema() == ((255, 255), (255, 255), (255, 255)):
        raise ValueError("No artwork is visible on white")
    output.parent.mkdir(parents=True, exist_ok=True)
    visible.save(output, format="PNG")
    touched = bounds[0] == 0 or bounds[1] == 0 or bounds[2] == width or bounds[3] == height
    return {"preview": str(output), "colorset": colorset, "size": [width, height], "ink_bounds": list(bounds),
            "touches_canvas_edge": touched, "text_elements": sum(e.tag.endswith("}text") for e in root.iter()),
            "semantic_quality": "requires visual review", "font_note": "Appearance depends on available fonts unless --font-dir is supplied."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("svg", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--size", type=int, default=960)
    parser.add_argument("--font-dir", type=Path)
    args = parser.parse_args()
    try:
        if not 128 <= args.size <= 4096:
            raise ValueError("size must be between 128 and 4096")
        if args.svg.resolve() == args.output.resolve():
            raise ValueError("Preview must not overwrite the SVG")
        print(json.dumps(render(args.svg, args.output, args.size, args.font_dir)))
    except (ValueError, OSError, ET.ParseError) as error:
        parser.exit(2, f"Cannot render SVG: {error}\n")


if __name__ == "__main__":
    main()
