#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["resvg-py==0.2.6", "Pillow==11.3.0", "numpy==2.2.6", "defusedxml==0.7.1"]
# ///
"""Auxiliary rendered layout evidence only: never a reward or promotion gate.

Run in the verifier image to retain its pinned fonts. Input SVGs remain unchanged.
The diagnostic has no reference-art input and cannot measure semantic correctness.
"""
import argparse
import copy
import hashlib
import io
import json
import math
from pathlib import Path
import re
import xml.etree.ElementTree as StdET

from defusedxml import ElementTree as ET
import numpy as np
from PIL import Image
import resvg_py

DRAWABLE = {"path", "rect", "circle", "ellipse", "line", "polyline", "polygon", "text", "use"}
DEFINITIONS = {"defs", "clipPath", "mask", "marker", "pattern", "symbol"}
FORBIDDEN = {"script", "foreignObject", "image", "iframe", "animate", "animateMotion", "animateTransform", "set", "audio", "video"}


def local(node):
    return node.tag.rsplit("}", 1)[-1]


def parse(data):
    if len(data) > 2_000_000:
        raise ValueError("SVG exceeds 2 MB")
    source = data.decode("utf-8-sig")
    if re.search(r"<!ENTITY|<!DOCTYPE|<\?xml-stylesheet|@import|@font-face", source, re.I):
        raise ValueError("External or dynamic content is unsupported")
    root = ET.fromstring(source)
    if root.tag != "{http://www.w3.org/2000/svg}svg":
        raise ValueError("Input must be SVG")
    box = [float(x) for x in root.get("viewBox", "").replace(",", " ").split()]
    if len(box) != 4 or not all(math.isfinite(x) for x in box) or min(box[2:]) <= 0:
        raise ValueError("A finite positive viewBox is required")
    for node in root.iter():
        if local(node) in FORBIDDEN:
            raise ValueError("Only static vector inputs are supported")
        for name, value in node.attrib.items():
            key = name.rsplit("}", 1)[-1].lower()
            if key.startswith("on") or (key == "href" and not value.startswith("#")):
                raise ValueError("External or executable attributes are unsupported")
    for ref in re.findall(r"url\(\s*[\"']?([^\)\"']+)", source, re.I):
        if not ref.strip().startswith("#"):
            raise ValueError("External resources are unsupported")
    return root, box


def render_rgba(root, width, height):
    fonts = Path("/usr/share/fonts/truetype/dejavu")
    if not fonts.is_dir():
        raise RuntimeError("Run inside the pinned verifier image with DejaVu fonts")
    png = resvg_py.svg_to_bytes(
        svg_string=StdET.tostring(root, encoding="unicode"), width=width, height=height,
        skip_system_fonts=True, font_dirs=[str(fonts)], font_family="DejaVu Sans",
        sans_serif_family="DejaVu Sans", serif_family="DejaVu Serif", monospace_family="DejaVu Sans Mono",
    )
    return np.asarray(Image.open(io.BytesIO(png)).convert("RGBA"))


def render(root, width, height):
    return render_rgba(root, width, height)[:, :, 3] >= 128


def hide(node):
    # The pinned resvg ignores inline !important overrides of stylesheet rules.
    # An inert empty group guarantees removal while retaining sibling position.
    # Keep the explicit CSS override as well, but do not rely on it for removal.
    tail = node.tail
    node.clear()
    node.tag = "{http://www.w3.org/2000/svg}g"
    node.tail = tail
    node.set("style", "display: none !important")
    node.set("display", "none")


def visible_channels(rgba):
    normalized = rgba.astype(float) / 255
    alpha = normalized[:, :, 3:4]
    # Compare over both black and white to preserve transparency differences.
    return np.concatenate((normalized[:, :, :3] * alpha,
                           normalized[:, :, :3] * alpha + 1 - alpha), axis=2)


def isolate(root, target_index):
    """Keep ancestor transforms, fonts, masks and removed-node sibling slots."""
    result = copy.deepcopy(root)
    index = 0

    def visit(node, in_definition=False, in_target=False):
        nonlocal index
        name = local(node)
        if in_definition or name in DEFINITIONS:
            return
        if name == "text":
            in_target = index == target_index
            index += 1
        if name in DRAWABLE and not in_target:
            hide(node)
        for child in node:
            visit(child, False, in_target)

    visit(result)
    return result


def diagnose(data):
    root, box = parse(data)
    # Match the viewBox directly so CSS viewport sizing does not distort the test.
    scale = 768 / max(box[2:])
    width, height = max(1, round(box[2] * scale)), max(1, round(box[3] * scale))
    root.set("width", str(width))
    root.set("height", str(height))
    texts = []

    def collect(node):
        if local(node) in DEFINITIONS:
            return
        if local(node) == "text":
            texts.append("".join(node.itertext()).strip())
        for child in node:
            collect(child)

    collect(root)
    if len(texts) > 100:
        raise ValueError("More than 100 text elements requires a separate audit")
    masks = [render(isolate(root, i), width, height) for i in range(len(texts))]
    full_scene = visible_channels(render_rgba(root, width, height))
    observable = []
    for index, ink in enumerate(masks):
        removed = copy.deepcopy(root)
        live_texts = []

        def collect_live(node):
            if local(node) in DEFINITIONS:
                return
            if local(node) == "text":
                live_texts.append(node)
            for child in node:
                collect_live(child)

        collect_live(removed)
        hide(live_texts[index])
        without = visible_channels(render_rgba(removed, width, height))
        visible_change = np.max(np.abs(full_scene - without), axis=2) > 4 / 255
        observable.append(float(np.count_nonzero(visible_change & ink) / ink.sum()) if ink.any() else None)
    overlaps = []
    for i in range(len(masks)):
        for j in range(i + 1, len(masks)):
            pixels = int(np.count_nonzero(masks[i] & masks[j]))
            if pixels >= 4:
                overlaps.append({"text_indices": [i, j], "intersecting_ink_pixels": pixels,
                                 "fraction_of_smaller_text_ink": pixels / max(1, min(int(masks[i].sum()), int(masks[j].sum())))})
    padding = 64
    expanded = copy.deepcopy(root)
    expanded.set("viewBox", " ".join(map(str, [box[0] - padding / scale, box[1] - padding / scale,
                                                box[2] + 2 * padding / scale, box[3] + 2 * padding / scale])))
    expanded.set("width", str(width + 2 * padding))
    expanded.set("height", str(height + 2 * padding))
    expanded_mask = render(expanded, width + 2 * padding, height + 2 * padding)
    outside = expanded_mask.copy()
    # One-pixel tolerance avoids edge antialiasing being reported as clipping.
    outside[padding - 1:padding + height + 1, padding - 1:padding + width + 1] = False
    return {"diagnostic_version": "1.0.1", "source_sha256": hashlib.sha256(data).hexdigest(),
            "fitness_unchanged": True, "removal_intervention": "inert_empty_svg_group",
            "render_size": [width, height], "text_strings": texts,
            "text_ink_pixels": [int(m.sum()) for m in masks], "text_ink_intersections": overlaps,
            "observable_text_ink_fraction": observable,
            "ink_beyond_viewbox_pixels": int(outside.sum()), "semantic_adherence": None,
            "limitations": ["Diagnostic observations require human review; intentional overlaps and bleeds are possible.",
                            "ViewBox expansion detects only nearby overflow; percentages, viewport units, filters and nested viewports may change geometry.",
                            "Text intersections measure separately rendered ink, not bounding boxes; outlines and use-instanced text are not classified as text.",
                            "Removed drawable nodes become empty groups. Sibling positions remain, but selectors depending on removed node types, IDs or descendants may change other elements.",
                            "Observable text ink compares the full scene with each text removed: low fractions suggest occlusion or matching background; this is not a perceptual legibility score.",
                            "Spelling, diagram meaning and code decodability are not measured.",
                            "All clipping masks remain active; clipping inside a clipPath is not diagnosed."]}


def self_test():
    prefix = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 100">'
    collision = diagnose((prefix + '<text x="10" y="50" font-size="24">LABEL</text><text x="10" y="50" font-size="24">LABEL</text></svg>').encode())
    separated = diagnose((prefix + '<text x="10" y="30" font-size="16">A</text><text x="150" y="80" font-size="16">B</text></svg>').encode())
    clipped = diagnose((prefix + '<rect x="190" y="20" width="20" height="20"/></svg>').encode())
    hidden = diagnose((prefix + '<text x="10" y="50" font-size="24">LABEL</text><rect width="200" height="100"/></svg>').encode())
    forced_display = diagnose((prefix + '<style>text { display:block !important }</style><text x="10" y="30" font-size="16" style="display:block!important">A</text><text x="150" y="80" font-size="16">B</text></svg>').encode())
    assert len(collision["text_ink_intersections"]) == 1
    assert separated["text_ink_intersections"] == []
    assert separated["ink_beyond_viewbox_pixels"] == 0
    assert clipped["ink_beyond_viewbox_pixels"] > 0
    assert hidden["observable_text_ink_fraction"] == [0.0]
    assert all(value > 0.9 for value in separated["observable_text_ink_fraction"])
    assert forced_display["text_ink_intersections"] == [], forced_display
    assert all(value > 0.9 for value in forced_display["observable_text_ink_fraction"]), forced_display
    print(json.dumps({"self_test": "passed", "cases": 5, "model_calls": 0}))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("svg", nargs="?", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return
    if not args.svg:
        parser.error("Provide an SVG or --self-test")
    result = diagnose(args.svg.read_bytes())
    serialized = json.dumps(result, indent=2, allow_nan=False)
    if args.output:
        # The project boundary is the only writable scope for diagnostics.
        scope = Path(__file__).resolve().parents[3]
        if not args.output.resolve().is_relative_to(scope):
            parser.error("Output must remain inside this repository")
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open("x", encoding="utf-8") as handle:
            handle.write(serialized + "\n")
    print(serialized)


if __name__ == "__main__":
    main()
