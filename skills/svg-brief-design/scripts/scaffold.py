#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Build original editable SVG scaffolds from small, editable JSON recipes."""
import argparse
import copy
import json
import math
from pathlib import Path
import xml.etree.ElementTree as ET

NS = "http://www.w3.org/2000/svg"
ET.register_namespace("", NS)
KINDS = ("blank", "orbit", "radial", "globe", "wave", "flow", "panel", "frond", "composition")
PALETTES = json.loads((Path(__file__).resolve().parents[1] / "assets/palettes/colorsets.json").read_text(encoding="utf-8"))["colorsets"]


def number(value):
    value = float(value)
    if not math.isfinite(value):
        raise ValueError("All coordinates must be finite")
    return f"{value:.5f}".rstrip("0").rstrip(".") if value else "0"


def node(parent, tag, text=None, **attrs):
    attributes = {key.replace("_", "-"): number(value) if isinstance(value, (int, float)) else str(value)
                  for key, value in attrs.items() if value is not None}
    item = ET.SubElement(parent, f"{{{NS}}}{tag}", attributes)
    if text is not None:
        item.text = str(text)
    return item


def point(x, y):
    return f"{number(x)},{number(y)}"


def path_points(points, close=False):
    return "M " + " L ".join(point(*p) for p in points) + (" Z" if close else "")


def bounded(params, key, default, low, high):
    value = float(params.get(key, default))
    if not math.isfinite(value) or not low <= value <= high:
        raise ValueError(f"{key} must be between {low} and {high}")
    return value


def count(params, key, default, low, high):
    value = bounded(params, key, default, low, high)
    if int(value) != value:
        raise ValueError(f"{key} must be an integer")
    return int(value)


def arrow(group, start, end, weight, identity):
    dx, dy = end[0] - start[0], end[1] - start[1]
    length = math.hypot(dx, dy)
    if length < weight * 5:
        raise ValueError("Arrow endpoints need more separation")
    ux, uy = dx / length, dy / length
    size = min(weight * 4, length / 4)
    back = (end[0] - ux * size, end[1] - uy * size)
    node(group, "line", id=identity + "-shaft", x1=start[0], y1=start[1], x2=end[0], y2=end[1])
    node(group, "path", id=identity + "-head", d=path_points([
        (back[0] - uy * size * .5, back[1] + ux * size * .5), end,
        (back[0] + uy * size * .5, back[1] - ux * size * .5)]))


def label(group, text, x, y, size, identity, anchor="middle"):
    node(group, "text", text, id=identity, x=x, y=y, font_size=size,
         font_family="DejaVu Sans, sans-serif", text_anchor=anchor,
         dominant_baseline="middle", fill="currentColor", stroke="none")


def defaults(kind):
    if kind not in KINDS:
        raise ValueError("Unknown scaffold kind")
    settings = {
        "blank": {},
        "orbit": {"count": 5, "inner_ratio": .64, "coverage": 1.35, "taper": 1.1, "rotation": -90, "direction": 1},
        "radial": {"count": 7, "inner_ratio": .36, "twist": .42, "gap": .12, "rotation": -90},
        "globe": {"meridians": 5, "parallels": 4, "tilt": 18},
        "wave": {"cycles": 2, "amplitude": .65, "phase": 0, "damping": 0, "x_label": "", "y_label": ""},
        "flow": {"labels": ["Input", "Process", "Output"], "direction": "horizontal", "rounding": 5},
        "panel": {"title": "Heading", "rows": ["Detail"], "header": "", "border": False},
        "frond": {"pairs": 12, "bend": .3, "spread": .34, "rotation": 0},
        "composition": {"items": []},
    }
    wide = kind in {"wave", "flow", "panel"}
    return {"version": 1, "kind": kind, "canvas": {"width": 720 if wide else 480,
            "height": 300 if wide else 480, "margin": 28},
            "style": {"stroke": 2, "color": "#000000", "colorset": "colorset1"}, "parameters": settings[kind], "underlay": [], "details": []}


def orbit(group, p, box, weight):
    """Repeat original tapered polar bands while preserving a clear central disk."""
    x, y, w, h = box
    cx, cy = x + w / 2, y + h / 2
    outer = min(w, h) / 2 - weight
    inner = outer * bounded(p, "inner_ratio", .64, .2, .9)
    n = count(p, "count", 5, 3, 24)
    coverage = bounded(p, "coverage", 1.35, .25, 1.8)
    taper = bounded(p, "taper", 1.1, .5, 3)
    rotation = math.radians(bounded(p, "rotation", -90, -360, 360))
    direction = p.get("direction", 1)
    if direction not in (-1, 1):
        raise ValueError("direction must be 1 or -1")
    span = outer - inner
    sweep = direction * 2 * math.pi / n * coverage
    steps = max(96, math.ceil(abs(sweep) * 40))
    for band in range(n):
        outside, inside = [], []
        for j in range(steps + 1):
            t = j / steps
            angle = rotation + direction * band * 2 * math.pi / n + t * sweep
            mid = (inner + outer) / 2 + span * .12 * math.sin(2 * math.pi * t)
            half = span * .35 * max(0, math.sin(math.pi * t)) ** taper
            # .12 + .35 < .5 keeps both boundaries strictly inside the
            # declared annulus for every t, regardless of repetition count.
            outside.append((cx + (mid + half) * math.cos(angle), cy + (mid + half) * math.sin(angle)))
            inside.append((cx + (mid - half) * math.cos(angle), cy + (mid - half) * math.sin(angle)))
        node(group, "path", id=f"orbit-band-{band + 1}",
             d=path_points(outside + list(reversed(inside)), close=True),
             fill="currentColor", stroke="none")


def radial(group, p, box, weight):
    x, y, w, h = box
    cx, cy, radius = x + w / 2, y + h / 2, min(w, h) / 2 - weight
    n = count(p, "count", 7, 3, 48)
    inner = radius * bounded(p, "inner_ratio", .36, .08, .8)
    gap = bounded(p, "gap", .12, .02, .5)
    rotation = math.radians(bounded(p, "rotation", -90, -360, 360))
    step = math.tau / n
    twist = step * bounded(p, "twist", .42, -.85, .85)
    for index in range(n):
        a, b = rotation + step * (index + gap / 2), rotation + step * (index + 1 - gap / 2)
        points = [(cx + r * math.cos(angle), cy + r * math.sin(angle))
                  for r, angle in ((radius, a), (radius, b), (inner, b + twist), (inner, a + twist))]
        node(group, "path", id=f"blade-{index}", d=path_points(points, True), fill="currentColor", stroke="none")


def globe(group, p, box, weight):
    x, y, w, h = box
    cx, cy, radius = x + w / 2, y + h / 2, min(w, h) / 2 - weight
    tilt = math.radians(bounded(p, "tilt", 18, -70, 70))
    meridians = count(p, "meridians", 5, 1, 24)
    parallels = count(p, "parallels", 4, 0, 24)

    def project(px, py, pz):
        return cx + radius * px, cy - radius * (py * math.cos(tilt) - pz * math.sin(tilt))

    node(group, "circle", id="sphere-outline", cx=cx, cy=cy, r=radius)
    for index in range(meridians):
        longitude = math.pi * index / meridians
        points = [project(math.sin(t) * math.cos(longitude), math.cos(t), math.sin(t) * math.sin(longitude))
                  for t in (math.tau * j / 160 for j in range(161))]
        node(group, "path", id=f"meridian-{index}", d=path_points(points))
    for index in range(parallels):
        latitude = math.pi * ((index + 1) / (parallels + 1) - .5)
        points = [project(math.cos(latitude) * math.cos(t), math.sin(latitude), math.cos(latitude) * math.sin(t))
                  for t in (math.tau * j / 160 for j in range(161))]
        node(group, "path", id=f"parallel-{index}", d=path_points(points))


def wave(group, p, box, weight):
    x, y, w, h = box
    left, right, mid = x + 24, x + w - 20, y + h / 2
    amplitude = bounded(p, "amplitude", .65, .05, .9) * (h / 2 - 16)
    cycles = bounded(p, "cycles", 2, .1, 30)
    phase = math.radians(bounded(p, "phase", 0, -360, 360))
    damping = bounded(p, "damping", 0, 0, 10)
    arrow(group, (left, mid), (right + 12, mid), weight, "axis-x")
    arrow(group, (left, y + h - 12), (left, y + 12), weight, "axis-y")
    samples = max(160, math.ceil(cycles * 60))
    points = [(left + (right - left) * t, mid - amplitude * math.exp(-damping * t) * math.sin(math.tau * cycles * t + phase))
              for t in (j / samples for j in range(samples + 1))]
    node(group, "path", id="waveform", d=path_points(points), stroke_width=weight * 1.2)
    if p.get("x_label"):
        label(group, p["x_label"], right, mid + 18, 13, "axis-x-label")
    if p.get("y_label"):
        label(group, p["y_label"], left + 12, y + 14, 13, "axis-y-label")


def flow(group, p, box, weight):
    x, y, w, h = box
    labels = p.get("labels", [])
    if not isinstance(labels, list) or not 2 <= len(labels) <= 12 or not all(isinstance(v, str) and v for v in labels):
        raise ValueError("flow labels must contain 2–12 nonempty strings")
    direction = p.get("direction", "horizontal")
    if direction not in {"horizontal", "vertical"}:
        raise ValueError("flow direction must be horizontal or vertical")
    horizontal = direction == "horizontal"
    n = len(labels)
    along = w if horizontal else h
    gap = min(48, along / (n * 3))
    length = (along - (n - 1) * gap) / n
    bw, bh = (length, min(h, 70)) if horizontal else (min(w, 280), length)
    if min(bw, bh) < 24:
        raise ValueError("Canvas too small for this flow; enlarge it or reduce the node count")
    rounding = bounded(p, "rounding", 5, 0, min(bw, bh) / 2)
    for i, text in enumerate(labels):
        nx = x + i * (length + gap) if horizontal else x + (w - bw) / 2
        ny = y + (h - bh) / 2 if horizontal else y + i * (length + gap)
        size = min(18, (bw - 20) / max(1, len(text) * .65), bh * .32)
        if size < 9:
            raise ValueError("Flow labels would be too small; widen the canvas or shorten labels")
        node(group, "rect", id=f"node-{i}", x=nx, y=ny, width=bw, height=bh, rx=rounding)
        label(group, text, nx + bw / 2, ny + bh / 2, size, f"label-{i}")
        if i < n - 1:
            start = (nx + bw, ny + bh / 2) if horizontal else (nx + bw / 2, ny + bh)
            end = (start[0] + gap, start[1]) if horizontal else (start[0], start[1] + gap)
            arrow(group, start, end, weight, f"edge-{i}-{i+1}")


def panel(group, p, box, weight):
    x, y, w, h = box
    title = str(p.get("title", ""))
    header = str(p.get("header", ""))
    rows = p.get("rows", [])
    if not isinstance(rows, list) or len(rows) > 12 or not all(isinstance(row, str) for row in rows):
        raise ValueError("panel rows must be at most 12 strings")
    if p.get("border", False):
        node(group, "rect", id="panel-border", x=x, y=y, width=w, height=h)
    content = ([header] if header else []) + ([title] if title else []) + rows
    if not content:
        return
    padding = 12
    line_height = (h - 2 * padding) / (len(content) + (.5 if title else 0))
    cursor = y + padding
    for i, text in enumerate(content):
        is_title = bool(title) and i == bool(header)
        allocated = line_height * (1.5 if is_title else 1)
        size = min(28 if is_title else 16, allocated * .55, (w - 2 * padding) / max(1, len(text) * .7))
        if size < 9:
            raise ValueError("Panel text would be too small; enlarge the canvas or reduce content")
        label(group, text, x + padding, cursor + allocated / 2, size, f"panel-text-{i}", "start")
        cursor += allocated


def frond(group, p, box, weight):
    x, y, w, h = box
    pairs = count(p, "pairs", 12, 3, 32)
    bend = bounded(p, "bend", .3, -.65, .65)
    spread = bounded(p, "spread", .34, .1, .48)
    rotation = bounded(p, "rotation", 0, -180, 180)
    stem = node(group, "g", id="frond")

    def center(t):
        return x + w * (.5 + bend * (t * t - .5)), y + h * (1 - t)

    hull = [center(j / 100) for j in range(101)]
    node(stem, "path", id="stem", d=path_points(hull))
    for i in range(pairs):
        t = .12 + .82 * i / pairs
        px, py = center(t)
        length = w * spread * (math.sin(math.pi * t) ** .8)
        for side in (-1, 1):
            tx, ty = px + side * length, py - h * .1 * (1 - t)
            fullness = length * .085
            first, second = (px+side*length*.45, py-fullness), (px+side*length*.55, py+fullness)
            hull.extend(((px, py), first, (tx, ty), second))
            d = (f"M {point(px, py)} Q {point(*first)} {point(tx, ty)} "
                 f"Q {point(*second)} {point(px, py)} Z")
            node(stem, "path", id=f"leaflet-{i}-{'left' if side<0 else 'right'}", d=d, stroke_width=weight * .7)
    # A Bezier lies inside its control hull. Fit that hull after rotation,
    # preserving aspect and making no assumptions about rendered path parsing.
    angle = math.radians(rotation)
    c, s = math.cos(angle), math.sin(angle)
    rotated = [(c*px-s*py, s*px+c*py) for px, py in hull]
    xs, ys = [v[0] for v in rotated], [v[1] for v in rotated]
    scale = min(1, (w-2*weight)/(max(xs)-min(xs)), (h-2*weight)/(max(ys)-min(ys)))
    tx = x+w/2-scale*(max(xs)+min(xs))/2
    ty = y+h/2-scale*(max(ys)+min(ys))/2
    stem.set("transform", "matrix(" + " ".join(number(v) for v in (scale*c, scale*s, -scale*s, scale*c, tx, ty)) + ")")


def composition(group, p, box, weight):
    x, y, w, h = box
    items = p.get("items", [])
    if not isinstance(items, list) or len(items) > 40:
        raise ValueError("composition items must be a list with at most 40 entries")
    for index, item in enumerate(items):
        if not isinstance(item, dict):
            raise ValueError("Each composition item must be an object")
        kind = item.get("kind")
        if kind not in DRAW or kind == "composition":
            raise ValueError("Composition items need a supported non-composition scaffold kind")
        values = item.get("box", [])
        if len(values) != 4:
            raise ValueError("Each item needs box [x, y, width, height] in canvas units")
        ix, iy, iw, ih = map(float, values)
        if not all(math.isfinite(v) for v in (ix, iy, iw, ih)) or min(iw, ih) < max(48, 3*weight):
            raise ValueError("Item box must be finite and large enough")
        if ix < x or iy < y or ix+iw > x+w or iy+ih > y+h:
            raise ValueError("Item box must stay inside the canvas margins")
        identity = str(item.get("id", f"part-{index}"))
        part = node(group, "g", id=identity)
        params = dict(defaults(kind)["parameters"])
        params.update(item.get("parameters", {}))
        DRAW[kind](part, params, (ix, iy, iw, ih), weight)
        for child in list(part.iter())[1:]:
            if child.get("id"):
                child.set("id", identity + "-" + child.get("id"))


DRAW = {"orbit": orbit, "radial": radial, "globe": globe, "wave": wave, "flow": flow, "panel": panel, "frond": frond, "composition": composition}
DETAIL_TAGS = {"g", "path", "rect", "circle", "ellipse", "line", "polyline", "polygon", "text"}
DETAIL_ATTRS = {"id", "d", "points", "x", "y", "x1", "y1", "x2", "y2", "cx", "cy", "r", "rx", "ry",
                "width", "height", "transform", "fill", "fill-rule", "stroke", "stroke-width", "stroke-linecap",
                "stroke-linejoin", "opacity", "font-family", "font-size", "font-weight", "text-anchor", "dominant-baseline"}


def add_detail(parent, detail, allowed):
    if not isinstance(detail, dict) or detail.get("tag") not in DETAIL_TAGS:
        raise ValueError("Details require a supported static SVG tag")
    attrs = detail.get("attrs", {})
    if not isinstance(attrs, dict) or set(attrs) - DETAIL_ATTRS:
        raise ValueError("Unsupported detail attribute")
    if any("url(" in str(value).lower() or "data:" in str(value).lower() for value in attrs.values()):
        raise ValueError("Details cannot embed or fetch resources")
    for key in ("fill", "stroke"):
        if key in attrs and attrs[key] not in {"none", "currentColor"} and attrs[key] not in allowed:
            raise ValueError(f"Detail {key} must be an exact token from the active colorset")
    element = node(parent, detail["tag"], detail.get("text"), **attrs)
    for child in detail.get("children", []):
        add_detail(element, child, allowed)


def build(recipe):
    if recipe.get("version") != 1 or recipe.get("kind") not in KINDS:
        raise ValueError("Expected recipe version 1 and a known kind")
    canvas, style, p = recipe["canvas"], recipe["style"], recipe["parameters"]
    w, h = bounded(canvas, "width", 480, 80, 10000), bounded(canvas, "height", 480, 80, 10000)
    margin = bounded(canvas, "margin", 28, 4, min(w, h) / 3)
    weight = bounded(style, "stroke", 2, .2, 40)
    color = str(style.get("color", "#000000"))
    colorset = style.get("colorset", "colorset1")
    if colorset not in PALETTES:
        raise ValueError("Style colorset must be colorset1 or colorset2")
    allowed = set(PALETTES[colorset]["allowed"])
    if color not in allowed:
        raise ValueError("Color must be an exact lowercase six-digit token from the active colorset")
    if weight >= margin:
        raise ValueError("Margin must exceed the stroke width")
    root = ET.Element(f"{{{NS}}}svg", {"viewBox": f"0 0 {number(w)} {number(h)}", "width": number(w), "height": number(h), "color": color, "data-colorset": colorset})
    underlay = node(root, "g", id="underlay", fill="none", stroke="currentColor", stroke_width=weight)
    background = recipe.get("underlay", [])
    if not isinstance(background, list) or len(background) > 500:
        raise ValueError("underlay must be a list with at most 500 entries")
    for detail in background:
        add_detail(underlay, detail, allowed)
    group = node(root, "g", id="structure", fill="none", stroke="currentColor", stroke_width=weight, stroke_linecap="round", stroke_linejoin="round")
    if recipe["kind"] in DRAW:
        DRAW[recipe["kind"]](group, p, (margin, margin, w-2*margin, h-2*margin), weight)
    detail_group = node(root, "g", id="details", fill="none", stroke="currentColor", stroke_width=weight)
    details = recipe.get("details", [])
    if not isinstance(details, list) or len(details) > 500:
        raise ValueError("details must be a list with at most 500 entries")
    for detail in details:
        add_detail(detail_group, detail, allowed)
    ids = [e.get("id") for e in root.iter() if e.get("id")]
    if len(ids) != len(set(ids)):
        raise ValueError("Element IDs must be unique")
    ET.indent(root)
    return ET.tostring(root, encoding="unicode") + "\n"


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value, encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    init = sub.add_parser("init", help="Create a recipe and its editable SVG scaffold")
    init.add_argument("kind", choices=KINDS)
    init.add_argument("--recipe", type=Path, required=True)
    init.add_argument("--output", type=Path, required=True)
    init.add_argument("--colorset", choices=("colorset1", "colorset2"), default="colorset1")
    render = sub.add_parser("build", help="Regenerate SVG after editing the JSON recipe")
    render.add_argument("recipe", type=Path)
    render.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        recipe = defaults(args.kind) if args.command == "init" else json.loads(args.recipe.read_text(encoding="utf-8-sig"))
        if args.command == "init":
            recipe["style"]["colorset"] = args.colorset
        svg = build(copy.deepcopy(recipe))
        if args.output.resolve() == args.recipe.resolve():
            raise ValueError("Recipe and SVG paths must differ")
        if args.command == "init":
            if args.recipe.exists() or args.output.exists():
                raise ValueError("init requires new paths; use build to update an existing SVG")
            write(args.recipe, json.dumps(recipe, indent=2, ensure_ascii=False) + "\n")
        write(args.output, svg)
    except (ValueError, KeyError, TypeError, OSError, RecursionError) as error:
        parser.exit(2, f"Cannot build scaffold: {error}\n")
    print(json.dumps({"output": str(args.output), "recipe": str(args.recipe), "kind": recipe["kind"], "editable": True}))


if __name__ == "__main__":
    main()
