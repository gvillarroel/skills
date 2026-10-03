#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Finalize filled SVG marks without changing open strokes or geometry."""
import math
import re
import xml.etree.ElementTree as ET

NS = "http://www.w3.org/2000/svg"
ET.register_namespace("", NS)
ET.register_namespace("xlink", "http://www.w3.org/1999/xlink")


def luminance(paint):
    channels = [int(paint[index:index + 2], 16) / 255 for index in (1, 3, 5)]
    return sum((value / 12.92 if value <= .04045 else ((value + .055) / 1.055) ** 2.4) * weight
               for value, weight in zip(channels, (.2126, .7152, .0722)))


def text_on(paint):
    level = luminance(paint)
    return "#000000" if (level + .05) / .05 >= 1.05 / (level + .05) else "#ffffff"


def composite(front, back, alpha):
    alpha = max(0, min(1, alpha))
    return "#" + "".join(f"{round(int(front[index:index + 2], 16) * alpha + int(back[index:index + 2], 16) * (1 - alpha)):02x}" for index in (1, 3, 5))


def category_style(index, palette, canvas="#ffffff"):
    """Use all distinct solids before finite, contrast-checked 1–3px borders."""
    if not isinstance(index, int) or index < 0:
        raise ValueError("Category index must be a nonnegative integer")
    solids = [paint for paint in dict.fromkeys(palette["solidSequence"]) if paint.lower() != canvas.lower()]
    if not solids:
        raise ValueError("The canvas leaves no category colors")
    fill = solids[index % len(solids)]
    style = dict(fill=fill, text=palette["textOnFill"][fill], stroke="none", strokeWidth=0, strokeDasharray=None, tier="solid", cue=None)
    variant = index // len(solids) - 1
    if variant < 0:
        return style
    level = luminance(fill)
    borders = [paint for paint in dict.fromkeys(palette["allowed"]) if paint != fill and
               (max(level, luminance(paint)) + .05) / (min(level, luminance(paint)) + .05) >= 3]
    if variant >= len(borders) * 9:
        return dict(style, tier="structural", cue="label-symbol-or-split")
    return dict(style, stroke=borders[variant % len(borders)], strokeWidth=1 + variant // (len(borders) * 3),
                strokeDasharray=(None, "6 4", "1 3")[(variant // len(borders)) % 3], tier="overflow")


def finalize_svg(source, palette):
    root = ET.fromstring(source)
    root.set("data-fill-style", "solid-first")
    parents = {child: parent for parent in root.iter() for child in parent}
    for style in root.iter(f"{{{NS}}}style"):
        # Label presentation attributes must control paint, including their
        # opacity-synchronized SMIL contrast. Typography stays in the stylesheet.
        style.text = re.sub(r"(\.psvg-(?:title|subtitle|kicker|label|node-label|note)\{[^}]*?)fill:#[0-9a-f]{6};?", r"\1", style.text or "")
    shapes = []
    exempt_tags = {"defs", "mask", "clipPath", "pattern"}
    excluded = set()
    for element in root.iter():
        parent = parents.get(element)
        tag = element.tag.split("}")[-1]
        if tag in exempt_tags or parent in excluded or element.get("data-paint-mode") in {"source", "line-art"}:
            excluded.add(element)
            continue
        if tag not in {"rect", "circle", "ellipse", "polygon", "path"}:
            continue
        fill = element.get("fill")
        if fill is None and "psvg-panel" in element.get("class", ""):
            fill = palette["surface"]
        if not fill or not re.fullmatch(r"#[0-9a-f]{6}", fill):
            continue
        if tag == "path" and not re.search(r"[zZ]\s*$", element.get("d", "")):
            continue
        if element.get("data-outline-tier") == "overflow":
            shapes.append((element, fill))
            continue
        stroke = element.get("stroke")
        if stroke and re.fullmatch(r"#[0-9a-f]{6}", stroke) and luminance(fill) > .6 and luminance(stroke) < .5:
            fill = stroke
            element.set("fill", fill)
        element.set("stroke", "none")
        element.set("data-fill-style", "solid")
        shapes.append((element, fill))
    for text in root.iter(f"{{{NS}}}text"):
        if text in excluded:
            continue
        x, y = float(text.get("x", 0)), float(text.get("y", 0)) - 3
        background = palette["surface"]
        containing = None
        for shape, fill in shapes:
            # Match local coordinates only; do not infer through unrelated
            # transformed groups or use path bounding boxes as filled regions.
            if parents.get(shape) is not parents.get(text):
                continue
            tag = shape.tag.split("}")[-1]
            if tag == "rect":
                hit = float(shape.get("x", 0)) <= x <= float(shape.get("x", 0)) + float(shape.get("width", 0)) and float(shape.get("y", 0)) <= y <= float(shape.get("y", 0)) + float(shape.get("height", 0))
            elif tag in {"circle", "ellipse"}:
                rx, ry = float(shape.get("rx", shape.get("r", 0))), float(shape.get("ry", shape.get("r", 0)))
                hit = rx > 0 and ry > 0 and ((x - float(shape.get("cx", 0))) / rx) ** 2 + ((y - float(shape.get("cy", 0))) / ry) ** 2 <= 1
            else:
                hit = False
            if hit:
                alpha = float(shape.get("fill-opacity", 1)) * float(shape.get("opacity", 1))
                background = composite(fill, background, alpha)
                containing = (shape, fill)
        text.set("fill", text_on(background))
        text.set("stroke", "none")
        if containing:
            shape, fill = containing
            for animation in shape.findall(f"{{{NS}}}animate"):
                if animation.get("attributeName") != "opacity" or not animation.get("values"):
                    continue
                alphas = [float(value) for value in animation.get("values").split(";")]
                times = [float(value) for value in animation.get("keyTimes", ";".join(str(index / (len(alphas) - 1)) for index in range(len(alphas)))).split(";")]
                paint_at = lambda alpha: text_on(composite(fill, palette["surface"], alpha * float(shape.get("fill-opacity", 1))))
                event_times, values = [], []
                for index, alpha in enumerate(alphas):
                    event_times.append(times[index])
                    values.append(paint_at(alpha))
                    if index + 1 == len(alphas) or values[-1] == paint_at(alphas[index + 1]) or animation.get("calcMode") == "discrete":
                        continue
                    low, high = 0., 1.
                    for _ in range(40):
                        middle = (low + high) / 2
                        if paint_at(alpha + middle * (alphas[index + 1] - alpha)) == values[-1]:
                            low = middle
                        else:
                            high = middle
                    event_times.append(times[index] + high * (times[index + 1] - times[index]))
                    values.append(paint_at(alphas[index + 1]))
                attributes = {key: value for key, value in animation.attrib.items() if key in {"dur", "begin", "repeatCount", "repeatDur", "fill"}}
                attributes.update(attributeName="fill", values=";".join(values), keyTimes=";".join(f"{time:.9g}" for time in event_times), calcMode="discrete")
                ET.SubElement(text, f"{{{NS}}}animate", attributes)
    return '<?xml version="1.0" encoding="UTF-8"?>\n' + ET.tostring(root, encoding="unicode") + "\n"
