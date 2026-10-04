#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Finish native style gaps without changing PlantUML layout or source semantics."""
from __future__ import annotations

import re
import json
from pathlib import Path
import xml.etree.ElementTree as ET
from arrow_contrast import contains, contrast, path_points, property_value, rect_bounds, set_style
from palette_paints import COLORSETS, canonical, readable_text

STYLE_VERSION = "scoped-solid-v3"
SHAPES = {"rect", "circle", "ellipse", "polygon", "path"}
STYLE_RULES = json.loads((Path(__file__).resolve().parent.parent / "assets/themes/native-style-rules.json").read_text(encoding="utf-8"))


def local(node):
    return node.tag.rsplit("}", 1)[-1]


def context(root):
    parents = {child: parent for parent in root.iter() for child in parent}
    order = {node: index for index, node in enumerate(root.iter())}
    def ancestors(node):
        while node in parents:
            node = parents[node]
            yield node
    def definition(node):
        return any(local(parent) in {"defs", "clipPath", "marker", "mask"} for parent in ancestors(node))
    return parents, order, ancestors, definition


def opaque_fill(node):
    fill = property_value(node, "fill", "none").lower()
    if not re.fullmatch(r"#[0-9a-f]{6}", fill):
        return None
    if float(property_value(node, "fill-opacity", "1")) * float(property_value(node, "opacity", "1")) < .999:
        return None
    return fill


def painted_shapes(root):
    _, _, ancestors, definition = context(root)
    return [node for node in root.iter() if local(node) in SHAPES and opaque_fill(node)
            and not definition(node) and node.get("data-arrow-id") is None
            and not any("link" in parent.get("class", "").split() or "message" in parent.get("class", "").split() for parent in ancestors(node))]


def background_at(root, point, before, shapes=None):
    _, order, _, _ = context(root)
    paint = property_value(root, "background", property_value(root, "background-color", "#ffffff"))
    paint = canonical(paint) if re.fullmatch(r"#[0-9a-fA-F]{3,6}|white|black", paint) else "#ffffff"
    for node in shapes if shapes is not None else painted_shapes(root):
        if order[node] < order[before] and contains(node, point):
            paint = opaque_fill(node) or paint
    return paint


def text_points(node):
    """Use native textLength and baseline; do not guess a browser font width."""
    if node.get("transform") or "textLength" not in node.attrib or not (node.text or "").strip():
        return []
    x, baseline = float(node.get("x", 0)), float(node.get("y", 0))
    width, size = float(node.get("textLength", 0)), float(node.get("font-size", 14))
    if node.get("text-anchor") == "middle":
        x -= width / 2
    elif node.get("text-anchor") == "end":
        x -= width
    return [(x + width * fraction, baseline - size * .4) for fraction in (.15, .5, .85)]


def timing_label_surface(root, node, backgrounds, canvas):
    """Back a terminal state label without extending its measured timing span."""
    fills = backgrounds-{canvas}
    if len(fills) != 1:
        return None
    fill = next(iter(fills))
    width, size = float(node.get('textLength', 0)), float(node.get('font-size', 14))
    x, baseline = float(node.get('x', 0)), float(node.get('y', 0))
    if node.get('text-anchor') == 'middle':
        x -= width/2
    elif node.get('text-anchor') == 'end':
        x -= width
    bounds = (x-2, baseline-size-2, x+width+2, baseline+2)
    viewbox = [float(value) for value in root.get('viewBox', '').split()]
    if len(viewbox) != 4 or bounds[0] < viewbox[0] or bounds[1] < viewbox[1] or bounds[2] > viewbox[0]+viewbox[2] or bounds[3] > viewbox[1]+viewbox[3]:
        raise ValueError('Native timing label surface cannot fit the viewport; increase native display spacing without changing events.')
    parents, _, _, _ = context(root)
    parent = parents[node]
    namespace = node.tag.rsplit('}', 1)[0]+'}' if '}' in node.tag else ''
    surface = ET.Element(namespace+'rect', {
        'x': f'{bounds[0]:g}', 'y': f'{bounds[1]:g}',
        'width': f'{bounds[2]-bounds[0]:g}', 'height': f'{bounds[3]-bounds[1]:g}',
        'fill': fill, 'stroke': 'none', 'stroke-width': '0',
        'data-style-role': 'label-surface',
    })
    parent.insert(list(parent).index(node), surface)
    # The native outer display frame can end before its terminal state label.
    # Pad that container only; measurement ticks, traces and state spans keep
    # their original coordinates. Do not widen an actual data axis.
    verticals = [line for line in root.iter() if local(line) == 'line'
                 and float(property_value(line, 'stroke-width', '1')) == 1
                 and float(line.get('x1', 0)) == float(line.get('x2', 0))
                 and float(line.get('y1', 0)) <= bounds[1]
                 and float(line.get('y2', 0)) >= bounds[3]]
    if verticals:
        frame = max(verticals, key=lambda line: float(line.get('x1', 0)))
        old_right = float(frame.get('x1', 0))
        if old_right < bounds[2]:
            new_right = bounds[2]+4
            if new_right > viewbox[0]+viewbox[2]:
                raise ValueError('Native timing label needs more outer display padding inside the viewport.')
            frame.set('x1', f'{new_right:g}')
            frame.set('x2', f'{new_right:g}')
            frame.set('data-style-role', 'display-frame')
            for line in root.iter():
                if local(line) == 'line' and float(line.get('y1', 0)) == float(line.get('y2', 0)) and abs(float(line.get('x2', 0))-old_right) < .01 and float(property_value(line, 'stroke-width', '1')) == 1:
                    line.set('x2', f'{new_right:g}')
                    line.set('data-style-role', 'display-frame')
    return surface


def presentation_source(source):
    """Remove comments and quoted facts before inspecting authored properties."""
    source = re.sub(r"(?s)/'.*?'/", "", source)
    lines = []
    for line in source.splitlines():
        if line.lstrip().startswith("'"):
            continue
        # Quoted labels and display facts are not presentation declarations.
        line = re.sub(r'"(?:[^"\\]|\\.)*"', '""', line)
        lines.append(line.split("'", 1)[0])
    return "\n".join(lines)


def source_has_property(source, name):
    source = presentation_source(source)
    if re.search(r"(?im)^\s*skinparam\s+"+name+r"\s+", source):
        return True
    blocks = re.findall(r"(?is)<style>(.*?)</style>|skinparam\s+\w+\s*\{([^}]+)\}", source)
    return any(re.search(r"(?i)\b"+name+r"\s+", first+second) for first, second in blocks)


def source_has_style(source):
    """Explicit authored presentation remains authoritative over bundled defaults."""
    source = presentation_source(source)
    lines = source.splitlines()
    styles = re.findall(r"(?is)<style>(.*?)</style>|skinparam\s+\w+\s*\{([^}]+)\}", source)
    if re.search(r"(?im)^\s*!theme\b|^\s*skinparam\s+\w*(?:Color|Thickness)\b", source) or any(re.search(r"(?i)\b(?:\w*Color|\w*Thickness)\b", first+second) for first, second in styles):
        return True
    for line in lines:
        head = line.partition(':')[0]
        if re.match(r"(?i)\s*(?:title|caption|header|footer)\b", head):
            continue
        if re.search(r"\[[^\]]*#[0-9a-f]{3,8}\b|\bis\s+colored\b|\b(?:line\.dotted|line\.dashed)\b", head, re.I):
            return True
        if re.match(r"(?i)\s*(?:class|object|component|rectangle|actor|participant|database|queue|node|cloud|storage|package|folder|artifact|interface|entity|boundary|control|collections|card|agent|usecase|state|archimate|bar|line|scatter)\b", head) and re.search(r"#[0-9a-f]{3,8}\b|#(?:red|blue|green|white|black|orange|purple|yellow|gray|grey)\b", head, re.I):
            return True
    return False


def finish_native_styles(root, colorset, source="", enabled=True):
    if not enabled:
        return {"version": STYLE_VERSION, "mode": "native-notation", "textCount": 0, "bodyCount": 0}
    explicit = source_has_style(source)
    rules = STYLE_RULES["colorsets"][colorset]
    paints = [rules["canvas"], rules["saltButton"], *rules["archimate"].values()]
    if any(paint not in COLORSETS[colorset]["allowed"] for paint in paints):
        raise ValueError("Native style rules must use exact selected palette paints.")
    _, _, ancestors, definition = context(root)
    family = root.get("data-diagram-type", "")
    body_count = 0
    chart_map = {}
    if family == 'CHART' and colorset == 'colorset1' and not explicit:
        # Native chart defaults are scoped by mark kind. Compress absent kinds
        # so a line-only or scatter-only chart does not start with gray.
        native_marks = {'bar': '#9e1b32', 'line': '#333e48', 'scatter': '#4f4f4f'}
        active = set(re.findall(r'(?im)^\s*(bar|line|scatter)\s+', presentation_source(source)))
        rank = [kind for kind in native_marks if kind in active]
        chart_map = dict(zip(rank, native_marks.values()))
        for node in root.iter():
            tag, fill = local(node), opaque_fill(node)
            kind = 'bar' if tag == 'rect' and fill == native_marks['bar'] else 'scatter' if tag in {'circle', 'ellipse', 'polygon'} and fill == native_marks['scatter'] else 'line' if tag in {'line', 'path'} and canonical(property_value(node, 'stroke', '#000000')) == native_marks['line'] else None
            if kind not in chart_map:
                continue
            paint = chart_map[kind]
            node.set('data-native-mark', kind)
            if kind == 'line':
                set_style(node, stroke=paint)
            else:
                node.set('fill', paint)
                set_style(node, fill=paint, stroke='none', **{'stroke-width': '0'})
                node.set('data-style-role', 'solid-body')
                body_count += 1
        if chart_map:
            root.set('data-native-mark-map', json.dumps(chart_map, separators=(',', ':')))
    # The native grammar BackGroundColor is shared by tokens and the viewport.
    # Deliver a white default canvas so solid tokens retain their silhouettes.
    if family in {"EBNF", "REGEX"} and not source_has_property(source, "BackGroundColor"):
        set_style(root, background=rules["canvas"])
        viewbox = [float(value) for value in root.get("viewBox", "").split()]
        if len(viewbox) == 4:
            for node in root.iter():
                if local(node) == "rect" and rect_bounds(node) == (viewbox[0], viewbox[1], viewbox[0]+viewbox[2], viewbox[1]+viewbox[3]):
                    node.set("fill", rules["canvas"])
                    set_style(node, fill=rules["canvas"], stroke="none", **{"stroke-width": "0"})
                    node.set("data-style-role", "canvas")
    # ArchiMate's named native layers bypass themes. Map exact layer tokens before
    # generic nearest-palette normalization loses their categorical identity.
    layer_names = {"#c9ffc9": "technology", "#c2f0ff": "application",
                   "#ffffcc": "business", "#ccccff": "motivation",
                   "#f8e7c0": "strategy", "#97ff97": "physical",
                   "#ffe0e0": "implementation"}
    layer_map = dict(rules['archimate'])
    active_layer_map = {}
    if colorset == 'colorset1' and not explicit:
        active = {layer_names[paint] for node in root.iter()
                  if local(node) in SHAPES and (paint := opaque_fill(node)) in layer_names}
        rank = rules['archimateRoleOrder']
        if len(rank) != len(layer_names) or set(rank) != set(layer_names.values()):
            raise ValueError('CS1 ArchiMate role order must name every native layer exactly once.')
        pool = [rules['archimate'][name] for name in rank]
        active_layer_map = dict(zip((name for name in rank if name in active), pool))
        layer_map.update(active_layer_map)
    layers = {paint: layer_map[name] for paint, name in layer_names.items()}
    if not explicit:
        for node in root.iter():
            if local(node) in SHAPES and opaque_fill(node) in layers:
                native = opaque_fill(node)
                paint = layers[native]
                node.set("fill", paint)
                set_style(node, fill=paint, stroke="none", **{"stroke-width": "0"})
                node.set("data-style-role", "solid-body")
                if colorset == 'colorset1':
                    node.set('data-native-layer', layer_names[native])
                body_count += 1
    if active_layer_map:
        root.set('data-native-layer-map', json.dumps(active_layer_map, separators=(',', ':')))
    # Salt's button geometry has a hardcoded native bevel/outline, unlike its
    # wireframe field and grid lines. Match that primitive, not every rectangle.
    if family == "SALT" and not explicit:
        for node in root.iter():
            if local(node) == "rect" and opaque_fill(node) == "#eeeeee" and float(property_value(node, "stroke-width", "1")) == 2.5:
                node.set("fill", rules["saltButton"])
                set_style(node, fill=rules["saltButton"], stroke="none", **{"stroke-width": "0"})
                node.set("data-style-role", "solid-body")
                body_count += 1
    if family == "GANTT" and not explicit:
        for node in root.iter():
            if local(node) == "rect" and opaque_fill(node) not in {None, "#ffffff"} and float(node.get("rx", "0")) > 0:
                set_style(node, stroke="none", **{"stroke-width": "0"})
                node.set("data-style-role", "solid-body")
                body_count += 1
    # Native railroad primitives hardcode borders even when LineThickness is 0.
    # Only filled token rectangles are decorative bodies. Open reference tokens,
    # repetition frames, rails, and endpoint glyphs retain semantic line art.
    if family in {"EBNF", "REGEX"} and not explicit:
        for node in root.iter():
            if local(node) == "rect" and opaque_fill(node) and not definition(node) and node.get("data-style-role") != "canvas":
                set_style(node, stroke="none", **{"stroke-width": "0"})
                node.set("data-style-role", "solid-body")
                body_count += 1
    for group in root.iter():
        classes = group.get("class", "").split()
        if not any(name in classes for name in ("entity", "participant")):
            continue
        shapes = [node for node in group.iter() if local(node) in SHAPES and opaque_fill(node)]
        if not shapes:
            continue
        body = max(shapes, key=lambda node: ((b[2]-b[0])*(b[3]-b[1])) if (b := rect_bounds(node)) else 0)
        backing = opaque_fill(body)
        for node in group.iter():
            if node is body or local(node) not in {"line", "path", "rect"}:
                continue
            bounds = rect_bounds(node)
            body_bounds = rect_bounds(body)
            if bounds is None or body_bounds is None:
                continue
            # Compartment separators and cylinder/queue curves are open geometry.
            missing = property_value(node, "stroke", "none") == "none" or float(property_value(node, "stroke-width", "1")) == 0
            open_detail = local(node) == "line" or local(node) == "path" and property_value(node, "fill", "none") == "none"
            # Native component icon tabs are tiny closed shapes inside the body.
            icon = local(node) == "rect" and float(node.get("width", 0)) <= 15 and float(node.get("height", 0)) <= 10 and contains(body, ((bounds[0]+bounds[2])/2, (bounds[1]+bounds[3])/2))
            if missing and (open_detail or icon):
                set_style(node, stroke=readable_text(backing), **{"stroke-width": str(STYLE_RULES["semanticDetailWidth"])})
                node.set("data-style-role", "semantic-detail")
                if icon:
                    set_style(node, fill=backing)
        if not explicit and property_value(body, "stroke", "none") == "none" and body.get("data-style-role") != "solid-body":
            body.set("data-style-role", "solid-body")
            body_count += 1
    shapes = painted_shapes(root)
    if family == "ACTIVITY":
        for node in root.iter():
            if local(node) == "line" and property_value(node, "stroke", "none") == "none":
                points = path_points(node)
                if points:
                    backing = background_at(root, points[len(points)//2], node, shapes)
                    set_style(node, stroke=readable_text(backing), **{"stroke-width": str(STYLE_RULES["semanticDetailWidth"])})
                    node.set("data-style-role", "semantic-detail")
    text_count = 0
    label_surface_count = 0
    # An explicit FontColor remains a source-style exception; otherwise labels
    # follow their actual painted backing, including exterior participant labels.
    explicit_text = source_has_property(source, r"\w*FontColor")
    for node in root.iter():
        if local(node) != "text" or definition(node) or explicit_text:
            continue
        points = text_points(node)
        if not points or any(parent.get("transform") for parent in ancestors(node)):
            continue
        backgrounds = {background_at(root, point, node, shapes) for point in points}
        choices = {readable_text(fill) for fill in backgrounds}
        if len(choices) != 1:
            choices = {paint for paint in ("#000000", "#ffffff") if all(contrast(paint, fill) >= 4.5 for fill in backgrounds)}
        if len(choices) != 1 and family == 'TIMING' and not explicit:
            surface = timing_label_surface(root, node, backgrounds, rules['canvas'])
            if surface is not None:
                shapes = painted_shapes(root)
                backgrounds = {background_at(root, point, node, shapes) for point in points}
                choices = {readable_text(fill) for fill in backgrounds}
                label_surface_count += 1
        if len(choices) != 1:
            raise ValueError("A native label crosses incompatible fills; move it to a single surface in the source.")
        paint = next(iter(choices))
        node.set("fill", paint)
        if "fill:" in node.get("style", ""):
            set_style(node, fill=paint)
        node.set("data-style-role", "contrast-label")
        text_count += 1
    root.set("data-native-style", STYLE_VERSION)
    root.set("data-source-style", "explicit" if explicit else "bundled")
    result = {"version": STYLE_VERSION, "mode": "explicit-source" if explicit else "bundled-solid", "textCount": text_count, "bodyCount": body_count}
    if label_surface_count:
        result['labelSurfaceCount'] = label_surface_count
    if active_layer_map:
        result['archimateLayers'] = active_layer_map
    if chart_map:
        result['chartMarks'] = chart_map
    return result


def style_findings(root):
    """Recompute artifact evidence; palette membership alone is not style proof."""
    findings = []
    shapes = painted_shapes(root)
    for node in root.iter():
        role = node.get("data-style-role")
        if role in {"solid-body", "label-surface"}:
            if not opaque_fill(node):
                findings.append("solid body must have an opaque fill")
            stroke = property_value(node, "stroke", "none")
            if stroke != "none" and float(property_value(node, "stroke-width", "1")) > 0:
                findings.append("solid body has a decorative outline")
        elif role == "contrast-label":
            points = text_points(node)
            backgrounds = {background_at(root, point, node, shapes) for point in points}
            paint = property_value(node, "fill", "#000000").lower()
            if paint not in {"#000000", "#ffffff"}:
                findings.append("label must use exact black or white")
            elif len(backgrounds) == 1 and paint != readable_text(next(iter(backgrounds))):
                findings.append("label must use the higher-contrast black or white")
            elif any(contrast(paint, fill) < 4.5 for fill in backgrounds):
                findings.append("label has insufficient contrast on its actual backing")
        if node.get("data-arrow-id") is not None:
            points = path_points(node)
            stroke = property_value(node, "stroke", "none")
            paint = stroke if stroke != "none" else property_value(node, "fill", "none")
            if re.fullmatch(r"#[0-9a-fA-F]{6}", paint) and any(contrast(paint, background_at(root, point, node, shapes)) < 3 for point in points):
                findings.append("native connector has insufficient contrast on its actual backing")
    return findings
