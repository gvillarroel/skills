#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["pillow==13.0.0"]
# ///
"""Independent checks for native XY artifacts, separate from adapter self-tests."""
from __future__ import annotations

import argparse
from collections import Counter
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET

from PIL import Image, ImageChops


def require(value: object, message: str) -> None:
    if not value:
        raise AssertionError(message)


def color(value: str) -> str | None:
    value = value.strip().lower()
    if value in {"none", "transparent", "currentcolor", "inherit"} or value.startswith("url(#"):
        return None
    if value in {"black", "white"}:
        return {"black": "#000000", "white": "#ffffff"}[value]
    if re.fullmatch(r"#[a-f0-9]{3}", value):
        return "#" + "".join(ch * 2 for ch in value[1:])
    if re.fullmatch(r"#[a-f0-9]{6}", value):
        return value
    if re.fullmatch(r"#[a-f0-9]{8}", value):
        return None if value[-2:] == "00" else value[:7]
    found = re.fullmatch(r"rgba?\(([^)]+)\)", value)
    if found:
        parts = re.split(r"[\s,/]+", found[1].strip())
        if len(parts) == 4 and float(parts[3]) == 0:
            return None
        require(len(parts) in {3, 4}, "Malformed RGB paint")
        return "#" + "".join(f"{round(float(ch)):02x}" for ch in parts[:3])
    raise AssertionError(f"Unrecognized explicit paint: {value}")


class Assets(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.external: list[dict] = []
        self.scripts = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attrs = dict(attrs)
        if tag == "script":
            self.scripts += 1
        for key in {"src", "href"}:
            value = attrs.get(key, "") or ""
            if value.startswith(("http:", "https:", "//")) and tag in {
                "script", "link", "img", "iframe", "audio", "video", "source"
            }:
                self.external.append({"tag": tag, "attribute": key, "value": value})


def inspect_svg(path: Path, allowed: set[str], expected: tuple[int, int] | None = None,
                allow_derived: bool = False) -> dict:
    raw = path.read_text(encoding="utf-8")
    require("<!DOCTYPE" not in raw.upper() and "<!ENTITY" not in raw.upper(), "SVG external entity declaration")
    root = ET.fromstring(raw)
    require(root.tag.rsplit("}", 1)[-1] == "svg", "Native output is not an SVG")
    width = int(float(root.attrib["width"].removesuffix("px")))
    height = int(float(root.attrib["height"].removesuffix("px")))
    require(width > 0 and height > 0, "Empty SVG dimensions")
    if expected:
        require((width, height) == expected, f"Unexpected native SVG dimensions {(width, height)}")
    paints: Counter[str] = Counter()
    geometry = 0
    for node in root.iter():
        tag = node.tag.rsplit("}", 1)[-1]
        require(tag not in {"script", "foreignObject", "iframe"}, f"Executable SVG element {tag}")
        geometry += tag in {"path", "circle", "rect", "line", "polyline", "polygon"}
        for key, value in node.attrib.items():
            local_key = key.rsplit("}", 1)[-1]
            require(not local_key.lower().startswith("on"), "SVG event-handler attribute")
            if local_key == "href":
                require(value.startswith(("#", "data:image/")), "SVG external reference")
            if local_key in {"fill", "stroke", "stop-color", "color"}:
                normalized = color(value)
                if normalized:
                    paints[normalized] += 1
            if local_key == "style":
                require("url(" not in value or "url(#" in value, "External SVG style URL")
                for match in re.finditer(r"(?:^|;)\s*(?:fill|stroke|stop-color|color)\s*:\s*([^;]+)", value):
                    normalized = color(match[1])
                    if normalized:
                        paints[normalized] += 1
    require(geometry >= 3, "SVG contains no meaningful chart geometry")
    require(paints, "SVG contains no explicit chart paint")
    unexpected = sorted(set(paints) - allowed)
    require(allow_derived or not unexpected, "Non-canonical SVG paint: " + str(unexpected))
    return {"width": width, "height": height, "geometry": geometry,
            "paints": dict(paints), "non_canonical_paints": unexpected}


def inspect_png(path: Path, background: str, expected: tuple[int, int] | None = None) -> dict:
    with Image.open(path) as opened:
        require(opened.format == "PNG", "Image output is not a native PNG")
        opened.load()
        image = opened.convert("RGB")
    if expected:
        require(image.size == expected, f"Unexpected native PNG dimensions {image.size}")
    require(min(image.size) >= 100, "PNG is too small for this acceptance fixture")
    diff = ImageChops.difference(image, Image.new("RGB", image.size, background))
    extent = diff.getbbox()
    require(extent and extent[2] - extent[0] >= 50 and extent[3] - extent[1] >= 50,
            "PNG has no meaningful non-background chart extent")
    unique = image.getcolors(maxcolors=image.width * image.height)
    require(unique and len(unique) > 5, "PNG appears blank or flat")
    return {"width": image.width, "height": image.height, "paint_extent": extent,
            "unique_colors": len(unique)}


def inspect_html(path: Path) -> dict:
    raw = path.read_text(encoding="utf-8")
    assets = Assets()
    assets.feed(raw)
    require(not assets.external, "Standalone HTML loads remote assets: " + str(assets.external))
    require(assets.scripts >= 1 and "data-xy-slot" in raw and "WebGL" in raw,
            "HTML is not a self-contained interactive XY export")
    require(len(raw) > 10000, "HTML lacks the embedded XY client")
    return {"bytes": path.stat().st_size, "inline_scripts": assets.scripts,
            "external_assets": assets.external}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--svg", type=Path, required=True)
    parser.add_argument("--png", type=Path, required=True)
    parser.add_argument("--html", type=Path, required=True)
    parser.add_argument("--palettes", type=Path, required=True)
    parser.add_argument("--colorset", choices=["colorset1", "colorset2"], required=True)
    parser.add_argument("--width", type=int)
    parser.add_argument("--height", type=int)
    parser.add_argument("--allow-derived", action="store_true")
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    palette = json.loads(args.palettes.read_text(encoding="utf-8"))["colorsets"][args.colorset]
    expected = (args.width, args.height) if args.width and args.height else None
    report = {"colorset": args.colorset, "passed": True,
              "svg": inspect_svg(args.svg, set(palette["allowed"]), expected, args.allow_derived),
              "png": inspect_png(args.png, palette["roles"]["background"], expected),
              "html": inspect_html(args.html)}
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report))


if __name__ == "__main__":
    main()
