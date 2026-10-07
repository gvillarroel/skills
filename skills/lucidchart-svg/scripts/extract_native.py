#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Extract an explicit SVG metadata graph; write a diagnostic ledger before any graph.

Run: uv run --script extract_native.py source.svg --coordinates user-space
     --output graph.json --report mapping.json [--semantic-edges]
No network, account access, topology inference, or source modification is performed.
"""

from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import re
import sys
import xml.etree.ElementTree as ET

sys.dont_write_bytecode = True

SVG = "http://www.w3.org/2000/svg"
XML = "http://www.w3.org/XML/1998/namespace"
NUMBER = r"[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?"
NUM_RE = re.compile(NUMBER)
ID_RE = re.compile(r"[A-Za-z0-9_.~-]{1,36}\Z")
GRAPHICS = {"rect", "circle", "ellipse", "polygon", "path", "line", "polyline", "text", "use", "image"}
NEVER_RENDERED = {"defs", "marker", "clipPath", "mask", "pattern", "linearGradient", "radialGradient", "symbol", "metadata", "title", "desc"}
INHERITED = {"fill", "stroke", "stroke-width", "stroke-dasharray", "font-family", "font-size", "font-weight", "font-style", "text-decoration", "text-anchor", "visibility", "color", "fill-opacity", "stroke-opacity", "marker-start", "marker-end", "marker-mid", "white-space"}
UNMAPPED_PRESENTATION = {"paint-order", "stroke-linecap", "stroke-linejoin", "stroke-miterlimit", "stroke-dashoffset", "writing-mode", "direction", "dominant-baseline", "alignment-baseline", "baseline-shift", "letter-spacing", "word-spacing", "textLength", "lengthAdjust", "font-stretch", "font-variant", "font-feature-settings", "font-kerning", "line-height", "text-transform"}
PROPERTIES = INHERITED | UNMAPPED_PRESENTATION | {"display", "opacity", "vector-effect", "x", "y", "width", "height", "cx", "cy", "r", "rx", "ry", "transform", "filter", "mask", "clip-path", "overflow", "animation", "animation-name"}
UNITS = {"": 1, "px": 1, "pt": 96 / 72, "pc": 16, "in": 96, "cm": 96 / 2.54, "mm": 96 / 25.4, "q": 96 / 101.6}
COLORS = {"black": "#000000", "white": "#ffffff", "red": "#ff0000", "green": "#008000", "blue": "#0000ff", "yellow": "#ffff00", "gray": "#808080", "grey": "#808080", "silver": "#c0c0c0", "maroon": "#800000", "purple": "#800080", "fuchsia": "#ff00ff", "lime": "#00ff00", "olive": "#808000", "navy": "#000080", "teal": "#008080", "aqua": "#00ffff"}
IDENTITY = (1.0, 0.0, 0.0, 1.0, 0.0, 0.0)


class MappingError(ValueError):
    pass


def load_sibling(name: str):
    path = Path(__file__).with_name(name + ".py")
    spec = importlib.util.spec_from_file_location("lucid_" + name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def tag(node: ET.Element) -> str:
    return node.tag.split("}")[-1]


def svg_node(node: ET.Element) -> bool:
    return node.tag.startswith("{" + SVG + "}")


def nums(raw: str, expected: int | None = None) -> list[float]:
    tokens = NUM_RE.findall(raw)
    if re.sub(NUMBER, "", raw).strip(" ,\t\r\n"):
        raise MappingError("Expected finite numeric coordinates, without unsupported units or tokens")
    values = [float(token) for token in tokens]
    if not all(math.isfinite(value) for value in values) or (expected is not None and len(values) != expected):
        raise MappingError(f"Expected {expected or 'a sequence of'} finite numbers")
    return values


def length(raw: str | None, default: float | None = None) -> float:
    if raw is None:
        if default is not None:
            return default
        raise MappingError("A required numeric length is missing")
    match = re.fullmatch(r"\s*(" + NUMBER + r")\s*([a-z]*)\s*", raw, re.I)
    if not match or match[2].lower() not in UNITS:
        raise MappingError(f"Unsupported length {raw!r}; resolve percentages/relative units explicitly")
    result = float(match[1]) * UNITS[match[2].lower()]
    if not math.isfinite(result):
        raise MappingError("Lengths must be finite")
    return result


def whole(value: float, label: str) -> int:
    if not math.isclose(value, round(value), rel_tol=0, abs_tol=1e-8) or value < 0:
        raise MappingError(f"{label} must map to a nonnegative whole number in the native contract")
    return round(value)


def multiply(a: tuple, b: tuple) -> tuple:
    aa, ab, ac, ad, ae, af = a
    ba, bb, bc, bd, be, bf = b
    return (aa * ba + ac * bb, ab * ba + ad * bb, aa * bc + ac * bd, ab * bc + ad * bd, aa * be + ac * bf + ae, ab * be + ad * bf + af)


def point(matrix: tuple, value: tuple | list) -> tuple[float, float]:
    a, b, c, d, e, f = matrix
    x, y = value
    return (a * x + c * y + e, b * x + d * y + f)


def transform(raw: str | None) -> tuple:
    matrix = IDENTITY
    remaining = raw or ""
    while remaining.strip():
        match = re.match(r"\s*([A-Za-z]+)\s*\(([^)]*)\)\s*,?", remaining)
        if not match:
            raise MappingError("Unsupported or malformed transform list")
        name, values = match[1], nums(match[2])
        if name == "translate" and len(values) in (1, 2):
            current = (1, 0, 0, 1, values[0], values[1] if len(values) == 2 else 0)
        elif name == "scale" and len(values) in (1, 2):
            current = (values[0], 0, 0, values[-1], 0, 0)
        elif name == "matrix" and len(values) == 6:
            current = tuple(values)
        else:
            raise MappingError("Only translation, positive axis scaling, and representable affine matrices are supported; rotation/skew require another route")
        if current[1] != 0 or current[2] != 0 or current[0] <= 0 or current[3] <= 0:
            raise MappingError("Negative, singular, rotated, or skewed transforms cannot preserve this native mapping")
        matrix = multiply(matrix, current)
        if not all(math.isfinite(value) for value in matrix):
            raise MappingError("Transform accumulation is nonfinite")
        remaining = remaining[match.end():]
    return matrix


def viewport_transform(box: list[float], width: float, height: float, aspect: str | None) -> tuple:
    x, y, w, h = box
    if min(w, h, width, height) <= 0:
        raise MappingError("Viewport and viewBox dimensions must be positive")
    parts = (aspect or "xMidYMid meet").split()
    if len(parts) == 1 and parts[0] == "none":
        return (width / w, 0, 0, height / h, -x * width / w, -y * height / h)
    if len(parts) == 1:
        parts.append("meet")
    if len(parts) != 2 or not re.fullmatch(r"x(?:Min|Mid|Max)Y(?:Min|Mid|Max)", parts[0]) or parts[1] not in {"meet", "slice"}:
        raise MappingError("Unsupported preserveAspectRatio value")
    scale = (min if parts[1] == "meet" else max)(width / w, height / h)
    factors = {"Min": 0, "Mid": .5, "Max": 1}
    tx = -x * scale + (width - w * scale) * factors[parts[0][1:4]]
    ty = -y * scale + (height - h * scale) * factors[parts[0][5:8]]
    return (scale, 0, 0, scale, tx, ty)


def paint(raw: str) -> str:
    value = raw.strip().lower()
    if value in COLORS:
        return COLORS[value]
    if re.fullmatch(r"#[0-9a-f]{6}", value):
        return value
    if re.fullmatch(r"#[0-9a-f]{3}", value):
        return "#" + "".join(char * 2 for char in value[1:])
    match = re.fullmatch(r"rgb\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)", value)
    if match and all(int(component) <= 255 for component in match.groups()):
        return "#" + "".join(f"{int(component):02x}" for component in match.groups())
    raise MappingError(f"Paint {raw!r} is outside the opaque solid color profile; retain artwork or use a reviewed hybrid route")


def declarations(raw: str) -> dict[str, str]:
    if re.search(r"[\\{}]|/\*|!important|var\(|(?:^|[;\s])@", raw, re.I):
        raise MappingError("Unsupported inline CSS syntax/cascade; resolve styles with a reviewed renderer")
    result = {}
    for declaration in raw.split(";"):
        if not declaration.strip():
            continue
        if ":" not in declaration:
            raise MappingError("Malformed inline style declaration")
        key, value = (item.strip() for item in declaration.split(":", 1))
        if key not in PROPERTIES:
            raise MappingError(f"Inline style property {key!r} is outside the native profile")
        result[key] = value
    return result


def property_object(pairs: list[tuple[str, object]]) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            raise MappingError("Duplicate field in data-lucid-properties")
        try:
            key.encode("utf-8")
            if isinstance(value, str):
                value.encode("utf-8")
        except UnicodeEncodeError as error:
            raise MappingError("Properties must contain valid Unicode text") from error
        result[key] = value
    return result


def nonfinite_property(value: str):
    raise MappingError(f"Nonfinite JSON property {value!r}")


def validate_property_literals(value):
    if isinstance(value, str):
        try:
            value.encode("utf-8")
        except UnicodeEncodeError as error:
            raise MappingError("Properties must contain valid Unicode text") from error
    elif isinstance(value, dict):
        for key, item in value.items():
            validate_property_literals(key)
            validate_property_literals(item)
    elif isinstance(value, list):
        for item in value:
            validate_property_literals(item)
    elif type(value) in (int, float):
        try:
            finite = math.isfinite(value)
        except OverflowError:
            finite = False
        if not finite:
            raise MappingError("Property numbers must be finite")


def line_points(node: ET.Element) -> list[tuple[float, float]]:
    kind = tag(node)
    if kind == "line":
        return [(length(node.get("x1"), 0), length(node.get("y1"), 0)), (length(node.get("x2"), 0), length(node.get("y2"), 0))]
    if kind == "polyline":
        values = nums(node.get("points", ""))
        if len(values) < 4 or len(values) % 2:
            raise MappingError("Polyline must contain at least two coordinate pairs")
        return list(zip(values[::2], values[1::2]))
    if kind != "path":
        raise MappingError("Explicit edge geometry must be line, polyline, or an open linear path")
    raw = node.get("d", "")
    if re.sub(r"[MmLlHhVv]|" + NUMBER, "", raw).strip(" ,\t\r\n"):
        raise MappingError("Curved, closed, or malformed edge path cannot be represented by the linear route profile")
    tokens = re.findall(r"[MmLlHhVv]|" + NUMBER, raw)
    result = []
    index = 0
    command = None
    current = (0.0, 0.0)
    while index < len(tokens):
        if re.fullmatch(r"[MmLlHhVv]", tokens[index]):
            command = tokens[index]
            index += 1
            if command.upper() == "M" and result:
                raise MappingError("Multiple edge subpaths are unsupported")
        if command is None or (not result and command.upper() != "M"):
            raise MappingError("Edge path must begin with a moveto")
        count = 2 if command.upper() in {"M", "L"} else 1
        if index + count > len(tokens) or any(re.fullmatch(r"[MmLlHhVv]", token) for token in tokens[index:index + count]):
            raise MappingError("Malformed edge path coordinates")
        values = [float(token) for token in tokens[index:index + count]]
        if not all(math.isfinite(value) for value in values):
            raise MappingError("Edge path coordinates must be finite")
        index += count
        relative = command.islower()
        if command.upper() in {"M", "L"}:
            current = (values[0] + (current[0] if relative else 0), values[1] + (current[1] if relative else 0))
        elif command.upper() == "H":
            current = (values[0] + (current[0] if relative else 0), current[1])
        else:
            current = (current[0], values[0] + (current[1] if relative else 0))
        result.append(current)
        if command.upper() == "M":
            command = "l" if relative else "L"
    if len(result) < 2:
        raise MappingError("Edge path requires at least two points")
    return result


class Mapper:
    def __init__(self, root: ET.Element, *, coordinates: str, semantic_edges: bool = False, viewport: list[float] | None = None):
        self.root = root
        self.coordinates = coordinates
        self.semantic_edges = semantic_edges
        self.viewport = viewport
        self.parents = {child: parent for parent in root.iter() for child in parent}
        self.refs = {node: node.get("id") or f"{tag(node)}[{index}]" for index, node in enumerate(root.iter(), 1)}
        self.by_id = {}
        self.styles = {}
        self.matrices = {}
        self.ledger = []
        self.id_map = {}
        self.nodes = {}
        self.source_geometry = {}
        self.edge_ids = set()
        self.order = {node: index for index, node in enumerate(root.iter())}
        self.page = None
        self.catalog = None
        self.node_elements = [node for node in root.iter() if node.get("data-node-id") is not None]
        self.edge_elements = [node for node in root.iter() if node.get("data-source") is not None or node.get("data-target") is not None]

    def note(self, node: ET.Element | None, feature: str, action: str, detail: str, **extra):
        self.ledger.append({"source_ref": self.refs.get(node, "document"), "feature": feature, "action": action, "detail": detail, **extra})

    def chain(self, node: ET.Element) -> list[ET.Element]:
        result = [node]
        while result[-1] in self.parents:
            result.append(self.parents[result[-1]])
        return list(reversed(result))

    def style(self, node: ET.Element) -> dict:
        if node in self.styles:
            return self.styles[node]
        parent = self.parents.get(node)
        result = {key: value for key, value in self.style(parent).items() if key in INHERITED} if parent is not None else {}
        result.update({key: value for key, value in node.attrib.items() if key in PROPERTIES})
        for key, value in declarations(node.get("style", "")).items():
            if value == "inherit":
                inherited = self.style(parent).get(key) if parent is not None else None
                if inherited is None:
                    result.pop(key, None)
                else:
                    result[key] = inherited
            elif value in {"initial", "unset", "revert", "revert-layer"}:
                raise MappingError(f"CSS keyword {value!r} requires a broader cascade profile")
            else:
                result[key] = value
        self.styles[node] = result
        return result

    def visible(self, node: ET.Element) -> bool:
        return not any(tag(parent) in NEVER_RENDERED or self.style(parent).get("display") == "none" for parent in self.chain(node)) and self.style(node).get("visibility", "visible") == "visible"

    def matrix(self, node: ET.Element) -> tuple:
        if node in self.matrices:
            return self.matrices[node]
        if node is self.root:
            result = self.root_matrix
        else:
            parent = self.parents[node]
            if tag(node) == "svg":
                raise MappingError("Nested SVG viewports require a separate reviewed normalization stage")
            result = multiply(self.matrix(parent), transform(self.style(node).get("transform")))
        self.matrices[node] = result
        return result

    def initialize_page(self):
        if self.viewport and (not all(math.isfinite(value) for value in self.viewport) or min(self.viewport) <= 0):
            raise MappingError("Explicit viewport values must be finite and positive in either coordinate mode")
        style = self.style(self.root)
        box = nums(self.root.get("viewBox", ""), 4) if self.root.get("viewBox") is not None else None
        width = length(style.get("width", self.root.get("width")), None) if style.get("width", self.root.get("width")) is not None else None
        height = length(style.get("height", self.root.get("height")), None) if style.get("height", self.root.get("height")) is not None else None
        if self.viewport:
            width, height = self.viewport
        outer = transform(style.get("transform"))
        if self.coordinates == "user-space":
            if box:
                self.page = box[2:]
                normalization = (1, 0, 0, 1, -box[0], -box[1])
            elif width is not None and height is not None:
                self.page = [width, height]
                normalization = IDENTITY
            else:
                raise MappingError("User-space mode requires a viewBox or two resolved root dimensions")
            self.root_matrix = multiply(normalization, outer)
        else:
            if width is None or height is None:
                raise MappingError("Viewport-pixels mode requires explicit root dimensions or --viewport WIDTH HEIGHT")
            self.page = [width, height]
            normalization = viewport_transform(box, width, height, self.root.get("preserveAspectRatio")) if box else IDENTITY
            self.root_matrix = multiply(outer, normalization)
        if not all(math.isfinite(value) for value in self.page) or min(self.page) <= 0 or max(self.page) > 20000:
            raise MappingError("Chosen page dimensions must fit the positive 20000-pixel native range")
        self.note(self.root, "coordinates", "preserved", "Declared coordinate policy and root mapping", mode=self.coordinates, root_matrix=list(self.root_matrix), page_size=self.page, source_view_box=box, source_viewport=[width, height])

    def map_id(self, source: str) -> str:
        if not source or not source.strip():
            raise MappingError("Semantic IDs must not be empty")
        if source in self.id_map:
            return self.id_map[source]
        result = source if ID_RE.fullmatch(source) else "svg-" + hashlib.sha256(source.encode("utf-8")).hexdigest()[:28]
        if result in self.id_map.values():
            raise MappingError("Deterministic native ID collision")
        self.id_map[source] = result
        return result

    def shape_type(self, source: str) -> str:
        if source in {"rectangle", "ellipse", "circle", "diamond", "text"}:
            return source
        if self.catalog is None:
            try:
                self.catalog = load_sibling("native_catalog")
            except (FileNotFoundError, ImportError) as error:
                raise MappingError("This native type requires the bundled verified native catalog") from error
        try:
            self.catalog.spec(source)
        except (ValueError, KeyError) as error:
            raise MappingError(f"Native type {source!r} is not verified by the catalog") from error
        return source

    def audit(self):
        ids = [node.get("id") for node in self.root.iter() if node.get("id")]
        for value, count in Counter(ids).items():
            if count > 1:
                self.note(None, "duplicate-svg-id", "blocked", f"SVG ID {value!r} occurs {count} times")
        self.by_id = {node.get("id"): node for node in self.root.iter() if node.get("id")}
        declared = [node.get("data-node-id") for node in self.node_elements]
        for value, count in Counter(declared).items():
            if count > 1:
                self.note(None, "duplicate-node-id", "blocked", f"Node metadata {value!r} occurs {count} times")
        if not self.node_elements:
            self.note(None, "missing-node-metadata", "blocked", "No data-node-id objects; geometry/proximity is not a graph contract")
        rich = {"use", "image", "foreignObject", "filter", "mask", "clipPath", "pattern", "linearGradient", "radialGradient", "animate", "animateTransform", "animateMotion", "set", "symbol"}
        for node in self.root.iter():
            kind = tag(node)
            if not svg_node(node):
                if not any(tag(parent) in {"metadata", "title", "desc"} for parent in self.chain(node)):
                    self.note(node, "foreign-namespace", "blocked", "Foreign content is not SVG primitive geometry")
                continue
            if not any(tag(parent) in {"metadata", "title", "desc"} for parent in self.chain(node)):
                known = GRAPHICS | NEVER_RENDERED | rich | {"svg", "g", "style", "a", "tspan", "stop"}
                if kind not in known:
                    self.note(node, "unsupported-svg-element", "blocked", f"Element {kind!r} has no defined primitive mapping/visibility semantics")
                structural = {"id", "class", "style", "version", "viewBox", "preserveAspectRatio", "d", "points", "x1", "y1", "x2", "y2", "markerUnits", "markerWidth", "markerHeight", "refX", "refY", "orient", "href", "offset", "stop-color", "stop-opacity"}
                for key in node.attrib:
                    local = key.split("}")[-1]
                    if local in PROPERTIES or local in structural or local.startswith("data-") or local.startswith("aria-") or local == "role" or key.startswith("{" + XML + "}"):
                        continue
                    if not any(tag(parent) in NEVER_RENDERED for parent in self.chain(node)):
                        self.note(node, "unsupported-svg-attribute", "blocked", f"Attribute {local!r} has no defined mapping; source value is {node.attrib[key]!r}")
            if kind == "style":
                self.note(node, "stylesheet-cascade", "blocked", "Native profile does not compute stylesheet cascade; SVG asset route remains separate")
            if kind == "svg" and node is not self.root:
                self.note(node, "nested-viewport", "blocked", "Normalize nested viewport mappings explicitly before primitive extraction")
            if kind in rich:
                self.note(node, kind, "blocked", "Feature needs artwork/hybrid or reviewed normalization; no native replacement is inferred")
            try:
                style = self.style(node)
                transform(style.get("transform"))
                for key in ("filter", "mask", "clip-path", "animation", "animation-name"):
                    if style.get(key, "none") not in {"none", ""}:
                        self.note(node, key, "blocked", "Feature is outside the static primitive native profile")
                for key in UNMAPPED_PRESENTATION:
                    if key in style:
                        self.note(node, key, "blocked", "Source presentation field has no verified mapping in this profile")
                for key in ("fill-opacity", "stroke-opacity"):
                    if key in style and length(style[key]) != 1:
                        self.note(node, key, "blocked", "Per-paint alpha cannot be replaced by whole-shape opacity")
                if kind in GRAPHICS and not any(tag(parent) in NEVER_RENDERED for parent in self.chain(node)) and not self.visible(node):
                    self.note(node, "hidden-content", "blocked", "Native graph would introduce visible content; preserve source or use a reviewed explicit adaptation")
                if kind in {"g", "svg", "a"} and "opacity" in style and length(style["opacity"]) != 1:
                    self.note(node, "group-opacity", "blocked", "Group compositing is not equivalent to distributing opacity among native objects")
                if kind == "g":
                    self.note(node, "svg-group", "adapted", "SVG containers establish ownership/transforms; native object groups are not inferred from incidental drawing containers")
                if kind == "a" and any(key.split("}")[-1] == "href" for key in node.attrib):
                    self.note(node, "link-interaction", "omitted", "Static native graph does not copy SVG link behavior; preserve original source")
                if any(key.startswith("aria-") or key == "role" for key in node.attrib):
                    self.note(node, "accessibility", "omitted", "Source accessibility metadata is retained in original, outside the native graph contract")
            except MappingError as error:
                self.note(node, "style-or-transform", "blocked", str(error))
        for node in self.node_elements:
            if any(parent in self.node_elements for parent in self.chain(node)[:-1]):
                self.note(node, "nested-node-ownership", "blocked", "Nested declared nodes need an explicit ownership normalization")

    def label(self, node: ET.Element) -> tuple[str, ET.Element | None]:
        candidates = [child for child in node.iter() if svg_node(child) and tag(child) == "text" and not child.get("data-edge-id")]
        if tag(node) == "text":
            candidates = [node]
        if len(candidates) > 1:
            raise MappingError("Multiple text candidates; select/recover a literal label explicitly before extraction")
        if "data-label" in node.attrib:
            if candidates:
                literal = self.text_content(candidates[0])
                if literal != node.get("data-label"):
                    raise MappingError("data-label conflicts with source literal text")
            else:
                self.note(node, "metadata-label", "adapted", "Explicit metadata becomes native literal text; source visible-label appearance is unverified")
            return node.get("data-label", ""), candidates[0] if candidates else None
        if not candidates:
            self.note(node, "label-content", "preserved", "No literal text is declared; this is not a claim that outlined artwork contains no label")
            return "", None
        return self.text_content(candidates[0]), candidates[0]

    def text_content(self, node: ET.Element) -> str:
        for child in node.iter():
            if child is node:
                continue
            if tag(child) in {"title", "desc", "metadata"}:
                continue
            if not svg_node(child) or tag(child) != "tspan" or any(key not in {"{" + XML + "}space"} for key in child.attrib):
                raise MappingError("Positioned/styled text spans and text paths require explicit reviewed text reconstruction")
        def content(current):
            value = current.text or ""
            for child in current:
                if tag(child) not in {"title", "desc", "metadata"}:
                    value += content(child)
                value += child.tail or ""
            return value
        value = content(node)
        self.note(node, "literal-text", "preserved", "XML-decoded characters and whitespace retained; glyph metrics remain subject to native text layout", literal=value, xml_space=node.get("{" + XML + "}space"))
        return value

    def text_style(self, node: ET.Element | None, prefix: str = "") -> dict:
        if node is None:
            return {}
        style = self.style(node)
        if style.get("stroke", "none") != "none" and length(style.get("stroke-width"), 1) > 0:
            raise MappingError("Outlined/stroked text cannot be represented by native literal label formatting")
        if length(style.get("opacity"), 1) != 1:
            raise MappingError("Independent text opacity cannot be represented by native label formatting")
        matrix = self.matrix(node)
        if not math.isclose(matrix[0], matrix[3], rel_tol=1e-9, abs_tol=1e-9):
            raise MappingError("Nonuniform text scaling cannot be represented by one native font size")
        result = {prefix + "text_color" if not prefix else prefix + "color": paint(style.get("fill", "black"))}
        if "font-size" in style:
            size = length(style["font-size"]) * matrix[0]
            if size <= 0:
                raise MappingError("Font size must be positive")
            result[prefix + "font_size"] = size
        else:
            self.note(node, "font-size", "adapted", "Source font size is unspecified; compiler's explicit default is used")
        if "font-family" in style:
            family = style["font-family"].strip().strip("'\"")
            if not re.fullmatch(r"[A-Za-z0-9 _.-]{1,100}", family):
                raise MappingError("Font fallback lists/complex family tokens require explicit font selection")
            result[prefix + "font_family"] = family
            self.note(node, "font-family", "unknown", "Declared family copied; Lucid availability and glyph metrics require live verification", family=family)
        else:
            self.note(node, "font-family", "adapted", "Source family is unspecified; compiler's explicit default is used")
        weight = style.get("font-weight", "normal")
        if weight not in {"normal", "400", "bold", "700"}:
            raise MappingError("Font weight requires an unsupported native weight distinction")
        result[prefix + "bold"] = weight in {"bold", "700"}
        italic = style.get("font-style", "normal")
        if italic not in {"normal", "italic"}:
            raise MappingError("Oblique/other font style is outside this profile")
        result[prefix + "italic"] = italic == "italic"
        decoration = set(style.get("text-decoration", "none").split())
        if not decoration <= {"none", "underline", "line-through"}:
            raise MappingError("Unsupported text decoration")
        result[prefix + "underline"] = "underline" in decoration
        result[prefix + "strike"] = "line-through" in decoration
        anchor = style.get("text-anchor", "start")
        if anchor not in {"start", "middle"}:
            raise MappingError("End-aligned text has no verified native right alignment in this profile")
        result[prefix + "text_align" if not prefix else prefix + "align"] = "left" if anchor == "start" else "center"
        self.note(node, "text-layout", "adapted", "Native label is laid out within its object/line; SVG baseline, padding, literal space rendering, and label x/y are not copied")
        return result

    def stroke_style(self, node: ET.Element, matrix: tuple) -> dict:
        style = self.style(node)
        stroke = style.get("stroke", "none")
        if style.get("vector-effect", "none") not in {"none", "non-scaling-stroke"}:
            raise MappingError("Unsupported vector effect")
        scaling = 1 if style.get("vector-effect") == "non-scaling-stroke" else matrix[0]
        if stroke != "none" and length(style.get("stroke-width"), 1) > 0 and style.get("vector-effect") != "non-scaling-stroke" and not math.isclose(matrix[0], matrix[3], rel_tol=1e-9, abs_tol=1e-9):
            raise MappingError("Nonuniform stroke scaling cannot preserve one native border width")
        width = whole(length(style.get("stroke-width"), 1) * scaling, "stroke width")
        result = {"stroke": "#000000" if stroke == "none" else paint(stroke), "stroke_width": 0 if stroke == "none" else width, "stroke_style": "solid"}
        if stroke == "none" or width == 0:
            self.note(node, "no-visible-stroke", "unknown", "Represented with stroke_width=0; exact Lucid invisibility must be checked after live import")
        raw = style.get("stroke-dasharray", "none")
        if raw != "none":
            values = nums(raw)
            if len(values) != 2 or values[1] <= 0 or values[0] < 0:
                raise MappingError("Only explicit two-value dash candidates can map to known native style enums")
            if values[0] == 0:
                result["stroke_style"] = "dotted"
            else:
                result["stroke_style"] = "dashed"
            self.note(node, "dash-pattern", "adapted", "Mapped to the known native style enum; exact source dash/gap lengths are not preserved", source_dash=values, native_style=result["stroke_style"])
        return result

    def bounds(self, node: ET.Element, geometry: ET.Element) -> tuple[list[float], str]:
        style = self.style(geometry)
        kind = tag(geometry)
        if "data-box" in node.attrib:
            if kind != "text":
                raise MappingError("data-box selects plain text bounds; it cannot override unsupported shape geometry")
            raw = nums(node.get("data-box", ""), 4)
            matrix = self.matrix(node)
            inferred = "text" if kind == "text" else {"rect": "rectangle", "circle": "circle", "ellipse": "ellipse", "polygon": "diamond"}.get(kind)
        elif kind == "rect":
            raw = [length(style.get("x"), 0), length(style.get("y"), 0), length(style.get("width")), length(style.get("height"))]
            matrix, inferred = self.matrix(geometry), "rectangle"
        elif kind in {"circle", "ellipse"}:
            cx, cy = length(style.get("cx"), 0), length(style.get("cy"), 0)
            rx = length(style.get("r")) if kind == "circle" else length(style.get("rx"))
            ry = rx if kind == "circle" else length(style.get("ry"))
            raw = [cx - rx, cy - ry, 2 * rx, 2 * ry]
            matrix, inferred = self.matrix(geometry), kind
        elif kind == "polygon":
            values = nums(geometry.get("points", ""), 8)
            pairs = list(zip(values[::2], values[1::2]))
            x, y = min(v[0] for v in pairs), min(v[1] for v in pairs)
            w, h = max(v[0] for v in pairs) - x, max(v[1] for v in pairs) - y
            expected = {(x + w / 2, y), (x + w, y + h / 2), (x + w / 2, y + h), (x, y + h / 2)}
            if set(pairs) != expected:
                raise MappingError("Polygon is not the supported symmetric diamond")
            for a, b in zip(pairs, pairs[1:] + pairs[:1]):
                if a[0] == b[0] or a[1] == b[1]:
                    raise MappingError("Diamond point order is invalid")
            raw = [x, y, w, h]
            matrix, inferred = self.matrix(geometry), "diamond"
        else:
            raise MappingError("Native node requires a supported primary geometry or plain text with data-box")
        if min(raw[2:]) <= 0:
            raise MappingError("Node width and height must be positive")
        x, y = point(matrix, raw[:2])
        output = [x, y, raw[2] * matrix[0], raw[3] * matrix[3]]
        if min(output[:2]) < -1e-8 or x + output[2] > self.page[0] + 1e-8 or y + output[3] > self.page[1] + 1e-8:
            raise MappingError("Mapped object extends outside the chosen source page; clipping/cropping cannot be silently replaced")
        return output, inferred

    def extract_node(self, node: ET.Element):
        source = node.get("data-node-id", "")
        if not svg_node(node) or not self.visible(node):
            raise MappingError("Declared node must be visible SVG content, not a definition/foreign object")
        geometry = [child for child in node.iter() if svg_node(child) and tag(child) in GRAPHICS - {"text"} and not child.get("data-source") and not child.get("data-target")]
        if tag(node) == "text":
            geometry = [node]
        elif not geometry and "data-box" in node.attrib:
            texts = [child for child in node.iter() if svg_node(child) and tag(child) == "text"]
            if len(texts) == 1:
                geometry = texts
        if len(geometry) != 1:
            raise MappingError("Declared node must own exactly one primary geometry; compound artwork needs a reviewed route")
        primary = geometry[0]
        bounds, inferred = self.bounds(node, primary)
        native_type = self.shape_type(node.get("data-lucid-type", inferred or ""))
        if inferred != native_type:
            self.note(node, "native-type-selection", "adapted", "Explicit verified native type selects a semantic shape; its rendering may differ from the primary SVG geometry", source_type=inferred, native_type=native_type)
        if native_type in {"circle", "ellipse"} and (native_type == "ellipse" or bounds[2] != bounds[3]):
            self.note(node, "ellipse-rendering", "unknown", "Native circle alias/bounds require live rendering verification; numeric source bounds are recovered")
        label, label_node = self.label(node)
        item = dict(zip(("x", "y", "width", "height"), bounds))
        item.update(id=self.map_id(source), type=native_type, label=label, z_index=self.order[primary])
        item.update(self.text_style(label_node))
        if native_type != "text":
            style = self.style(primary)
            item["fill"] = paint(style.get("fill", "black"))
            item.update(self.stroke_style(primary, self.matrix(primary)))
            opacity = length(style.get("opacity"), 1)
            if not 0 <= opacity <= 1:
                raise MappingError("Opacity must be in [0,1]")
            item["opacity"] = whole(opacity * 100, "opacity percentage")
            if opacity != 1 and label_node is not None:
                raise MappingError("Geometry-only opacity would also change its fused native label; use separate reviewed native objects")
            if tag(primary) == "rect":
                rx = length(style.get("rx", style.get("ry")), 0)
                ry = length(style.get("ry", style.get("rx")), 0)
                if rx < 0 or ry < 0:
                    raise MappingError("Corner radii must be nonnegative")
                matrix = self.matrix(primary)
                rx = min(rx * matrix[0], bounds[2] / 2)
                ry = min(ry * matrix[3], bounds[3] / 2)
                if not math.isclose(rx, ry, rel_tol=1e-9, abs_tol=1e-9):
                    raise MappingError("Elliptical corner rounding cannot map to one native rounding value")
                item["rounding"] = whole(2 * rx, "native rounding")
        elif tag(primary) != "text":
            raise MappingError("Text type must use an explicitly boxed text element")
        if "data-lucid-properties" in node.attrib:
            try:
                properties = json.loads(node.get("data-lucid-properties", ""), object_pairs_hook=property_object, parse_constant=nonfinite_property)
            except json.JSONDecodeError as error:
                raise MappingError("data-lucid-properties must be a JSON object") from error
            if not isinstance(properties, dict):
                raise MappingError("data-lucid-properties must be a JSON object")
            validate_property_literals(properties)
            item["properties"] = properties
        if source in self.nodes:
            raise MappingError("Duplicate declared node")
        self.nodes[source] = item
        self.source_geometry[source] = inferred
        self.note(node, "node", "preserved", "Explicit identity, supported bounds and literal content recovered", source_id=source, native_id=item["id"], bounds=bounds)

    def marker(self, node: ET.Element, name: str) -> str:
        raw = self.style(node).get(name, "none")
        if raw == "none":
            return "none"
        match = re.fullmatch(r"url\(\s*['\"]?#([^'\")\s]+)['\"]?\s*\)", raw)
        marker = self.by_id.get(match[1]) if match else None
        if marker is None or tag(marker) != "marker":
            raise MappingError("Marker reference is unresolved or external")
        if marker.get("orient") not in {"auto", "auto-start-reverse"}:
            raise MappingError("Fixed-angle marker orientation is outside the recognized arrow profile")
        if name == "marker-start" and marker.get("orient") != "auto-start-reverse":
            raise MappingError("Source marker must face outward via auto-start-reverse to match a native source arrow")
        children = [child for child in marker if tag(child) not in {"title", "desc", "metadata"}]
        if len(children) != 1 or not svg_node(children[0]) or tag(children[0]) != "polygon":
            raise MappingError("Only a verified right-pointing triangular polygon marker is recognized; arbitrary marker artwork requires a reviewed route")
        shape = children[0]
        if transform(self.style(marker).get("transform")) != IDENTITY or transform(self.style(shape).get("transform")) != IDENTITY:
            raise MappingError("Transformed marker artwork requires independently resolved tip/reference geometry")
        values = nums(shape.get("points", ""), 6)
        pairs = list(zip(values[::2], values[1::2]))
        x0, x1 = min(x for x, _ in pairs), max(x for x, _ in pairs)
        y0, y1 = min(y for _, y in pairs), max(y for _, y in pairs)
        if x0 == x1 or y0 == y1 or set(pairs) != {(x0, y0), (x1, (y0 + y1) / 2), (x0, y1)}:
            raise MappingError("Marker geometry is not the recognized triangular arrow")
        if length(marker.get("markerWidth"), 3) <= 0 or length(marker.get("markerHeight"), 3) <= 0:
            raise MappingError("Zero/negative marker dimensions do not match visible native arrow artwork")
        if marker.get("markerUnits", "strokeWidth") not in {"strokeWidth", "userSpaceOnUse"}:
            raise MappingError("Unsupported marker coordinate units")
        if length(marker.get("refX"), 0) != x1 or length(marker.get("refY"), 0) != (y0 + y1) / 2:
            raise MappingError("Marker reference point must be the triangle tip to match the native endpoint")
        if any(length(self.style(part).get("opacity"), 1) != 1 for part in (marker, shape)):
            raise MappingError("Independent marker opacity cannot be represented by native endpoint formatting")
        if self.style(shape).get("fill", "black") in {"none", "transparent"} or self.style(shape).get("stroke", "none") != "none":
            raise MappingError("Outlined/transparent triangle marker does not match the supported solid arrow class")
        marker_color = paint(self.style(shape).get("fill", "black"))
        edge_stroke = self.style(node).get("stroke", "none")
        edge_color = "#000000" if edge_stroke == "none" else paint(edge_stroke)
        if marker_color != edge_color:
            raise MappingError("Independent marker color has no native endpoint color mapping")
        self.note(marker, "marker", "adapted", "Tip-aligned triangle recognized as native arrow class; exact marker dimensions/glyph require live visual verification", native_marker="arrow", source_property=name)
        return "arrow"

    def port(self, source: str, endpoint: tuple, node: ET.Element) -> dict:
        target = self.nodes[source]
        x = (endpoint[0] - target["x"]) / target["width"]
        y = (endpoint[1] - target["y"]) / target["height"]
        tolerance = 1e-7
        if x < -tolerance or y < -tolerance or x > 1 + tolerance or y > 1 + tolerance:
            raise MappingError(f"Endpoint does not match declared node {source!r}")
        kind = self.source_geometry[source]
        if kind == "rectangle" and target.get("rounding", 0) > 0:
            radius = target["rounding"] / 2
            px, py = endpoint[0] - target["x"], endpoint[1] - target["y"]
            w, h = target["width"], target["height"]
            straight = (any(math.isclose(px, boundary, abs_tol=tolerance) for boundary in (0, w)) and radius <= py <= h - radius) or (any(math.isclose(py, boundary, abs_tol=tolerance) for boundary in (0, h)) and radius <= px <= w - radius)
            cx = radius if px <= radius else w - radius
            cy = radius if py <= radius else h - radius
            corner = (px <= radius or px >= w - radius) and (py <= radius or py >= h - radius) and math.isclose((px - cx) ** 2 + (py - cy) ** 2, radius ** 2, rel_tol=tolerance, abs_tol=tolerance)
            if not straight and not corner:
                raise MappingError("Rounded rectangle endpoint does not meet the actual source contour")
        elif kind in {"rectangle", "text"} and not any(math.isclose(v, boundary, abs_tol=tolerance) for v in (x, y) for boundary in (0, 1)):
            raise MappingError("Rectangle endpoint is inside the node rather than on its perimeter")
        if kind == "diamond" and not math.isclose(abs(2 * x - 1) + abs(2 * y - 1), 1, abs_tol=tolerance):
            raise MappingError("Diamond endpoint does not meet the source contour")
        if kind in {"circle", "ellipse"} and not math.isclose((2 * x - 1) ** 2 + (2 * y - 1) ** 2, 1, abs_tol=tolerance):
            raise MappingError("Ellipse endpoint does not meet the source contour")
        self.note(node, "endpoint", "preserved", "Semantic reference and geometric perimeter independently matched", node_id=source, point=list(endpoint), port={"x": x, "y": y})
        return {"x": x, "y": y}

    def extract_edge(self, node: ET.Element) -> dict:
        if not svg_node(node) or not self.visible(node):
            raise MappingError("Declared edge must be visible SVG content")
        source, target = node.get("data-source"), node.get("data-target")
        if source not in self.nodes or target not in self.nodes:
            raise MappingError("Both explicit edge endpoints must resolve to declared supported nodes")
        source_id = node.get("data-edge-id", node.get("id", ""))
        if not source_id or source_id in self.edge_ids or source_id in self.nodes:
            raise MappingError("Edge must have a globally unique explicit id or data-edge-id")
        self.edge_ids.add(source_id)
        points = [point(self.matrix(node), value) for value in line_points(node)]
        if any(a == b for a, b in zip(points, points[1:])):
            raise MappingError("Zero-length edge segment cannot be represented reliably")
        if len(points) > 2 and self.style(node).get("fill", "black") != "none":
            x0, y0 = points[0]
            x1, y1 = points[-1]
            if any(not math.isclose((x1 - x0) * (y - y0), (y1 - y0) * (x - x0), abs_tol=1e-8) for x, y in points[1:-1]):
                raise MappingError("Filled open edge path encloses artwork; native line would drop its filled region")
        style = self.stroke_style(node, self.matrix(node))
        visible = style["stroke_width"] > 0 and length(self.style(node).get("opacity"), 1) > 0
        if not visible and not self.semantic_edges:
            raise MappingError("Semantic edge has no visible source stroke; --semantic-edges is required to introduce native arrow artwork")
        if self.style(node).get("marker-mid", "none") != "none":
            raise MappingError("Mid-path markers have no native line equivalent in this profile")
        if "opacity" in self.style(node) and length(self.style(node)["opacity"]) != 1 and visible:
            raise MappingError("Edge opacity has no verified native line opacity mapping")
        source_marker, target_marker = self.marker(node, "marker-start"), self.marker(node, "marker-end")
        marker_visible = source_marker != "none" or target_marker != "none"
        if not visible:
            style = {"stroke": "#000000", "stroke_width": 1, "stroke_style": "solid"}
            source_marker, target_marker = "none", "arrow"
            self.note(node, "semantic-edge-artwork", "adapted", "Original source line has no visible stroke; explicit option introduces black 1 px destination arrow; source marker presence recorded separately", source_visible_stroke=False, source_visible_markers=marker_visible)
        else:
            self.note(node, "source-visible-edge", "preserved", "Source has a visible stroke; marker/dash substitutions are recorded separately", source_visible_stroke=True)
        item = {"id": self.map_id(source_id), "source": self.nodes[source]["id"], "target": self.nodes[target]["id"], "source_port": self.port(source, points[0], node), "target_port": self.port(target, points[-1], node), "source_marker": source_marker, "target_marker": target_marker, "line_type": "straight", "z_index": self.order[node], **style}
        if len(points) > 2:
            item["joints"] = [{"x": x, "y": y} for x, y in points[1:-1]]
        labels = [label for label in self.root.iter() if label.get("data-edge-id") == source_id and tag(label) == "text"]
        if len(labels) > 1:
            raise MappingError("Multiple edge labels require explicit reviewed selection")
        if labels:
            item["label"] = self.text_content(labels[0])
            item.update(self.text_style(labels[0], "label_"))
            item.update(label_position=.5, label_side="top")
            self.note(labels[0], "edge-label-placement", "adapted", "Native label midpoint/top replaces the SVG label x/y; content and supported styles copied")
        self.note(node, "edge", "preserved", "Explicit topology and transformed route endpoints recovered", source_id=source_id, native_id=item["id"], transformed_points=[list(value) for value in points])
        return item

    def unowned(self):
        for node in self.root.iter():
            if not svg_node(node) or tag(node) not in GRAPHICS:
                continue
            if any(tag(parent) in NEVER_RENDERED for parent in self.chain(node)):
                self.note(node, "definition-geometry", "omitted", "Not directly painted; source definition retained in original SVG")
                continue
            if any(owner in self.node_elements for owner in self.chain(node)) or node in self.edge_elements:
                continue
            if tag(node) == "text" and node.get("data-edge-id") in self.edge_ids:
                continue
            self.note(node, "unmapped-artwork", "blocked", "Source graphic is not owned by a declared node/edge; retain SVG artwork or supply a reviewed hybrid mapping")

    def extract(self) -> tuple[dict | None, dict]:
        self.audit()
        try:
            self.initialize_page()
        except MappingError as error:
            self.note(self.root, "coordinate-mapping", "blocked", str(error))
            self.page = None
        if self.page is not None:
            for node in self.node_elements:
                try:
                    self.extract_node(node)
                except (MappingError, ValueError) as error:
                    self.note(node, "node-mapping", "blocked", str(error), source_id=node.get("data-node-id"))
            edges = []
            for node in self.edge_elements:
                try:
                    edges.append(self.extract_edge(node))
                except MappingError as error:
                    self.note(node, "edge-mapping", "blocked", str(error))
        else:
            edges = []
        self.unowned()
        graph = {"title": self.root.get("data-title", "Extracted SVG diagram"), "page_width": self.page[0], "page_height": self.page[1], "nodes": list(self.nodes.values()), "edges": edges} if self.page else None
        if graph is not None:
            self.note(self.root, "page-background", "adapted", "Native page uses compiler background default; SVG canvas transparency is not represented as a native page fill")
        blocked = any(item["action"] == "blocked" for item in self.ledger)
        report = {"schema_version": 1, "profile": "explicit-svg-metadata-v1", "coordinates": self.coordinates, "semantic_edges_authorized": self.semantic_edges, "native_mapping_eligibility": "blocked" if blocked else "eligible", "declared_node_count": len(self.node_elements), "declared_edge_count": len(self.edge_elements), "resolved_node_count": len(self.nodes), "resolved_edge_count": len(edges), "source_to_native_ids": self.id_map, "ledger": self.ledger, "live_import": "not executed", "source_unchanged": True, "asset_route": "Native mapping diagnostics do not establish SVG asset import eligibility; inspect the original separately"}
        return None if blocked else graph, report


def extract_file(source: Path, *, coordinates: str, semantic_edges: bool = False, viewport: list[float] | None = None) -> tuple[dict | None, dict]:
    report = {"schema_version": 1, "profile": "explicit-svg-metadata-v1", "source": str(source), "coordinates": coordinates, "native_mapping_eligibility": "blocked", "live_import": "not executed", "ledger": []}
    try:
        inspector = load_sibling("inspect_svg")
        data, inspection = inspector.inspect(source)
        report["sha256"] = inspection["sha256"]
        report["upload_preflight"] = {"ready_for_upload": inspection["ready_for_upload"], "blocking_flags": inspection["blocking_flags"], "scope": "Local XML/resource preflight only; no live service acceptance"}
        if inspection["blocking_flags"]:
            report["ledger"] = [{"source_ref": "document", "feature": flag, "action": "blocked", "detail": "Source fails resource/XML preflight; preserve original and repair deliberately before reconstruction"} for flag in inspection["blocking_flags"]]
        mapper = Mapper(ET.fromstring(data), coordinates=coordinates, semantic_edges=semantic_edges, viewport=viewport)
        graph, result = mapper.extract()
        result["ledger"] = report["ledger"] + result["ledger"]
        if inspection["blocking_flags"]:
            graph = None
            result["native_mapping_eligibility"] = "blocked"
        report.update(result)
        if graph is not None:
            try:
                compiler = load_sibling("build_native")
                compiler.build_document(graph)
            except (ValueError, TypeError, KeyError) as error:
                report["ledger"].append({"source_ref": "document", "feature": "compiler-contract", "action": "blocked", "detail": str(error)})
                report["native_mapping_eligibility"] = "blocked"
                graph = None
        return graph, report
    except (OSError, ValueError, ET.ParseError) as error:
        report["ledger"].append({"source_ref": "document", "feature": "input", "action": "blocked", "detail": str(error)})
        return None, report


def main() -> int:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("--coordinates", required=True, choices=("user-space", "viewport-pixels"))
    parser.add_argument("--viewport", type=float, nargs=2, metavar=("WIDTH", "HEIGHT"), help="Explicit fixed viewport when root dimensions are unresolved")
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--report", required=True, type=Path)
    parser.add_argument("--semantic-edges", action="store_true", help="Explicitly introduce black destination arrows for unstroked semantic edges; disclose source invisibility")
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()
    try:
        paths = [path.resolve() for path in (args.input, args.output, args.report)]
        if len(set(paths)) != 3:
            raise MappingError("Source, graph, and report paths must be distinct; the original is immutable")
        for target in (args.output, args.report):
            if args.input.exists() and target.exists() and args.input.samefile(target):
                raise MappingError("Output/report aliases the source file; the original is immutable")
        if args.output.exists() and args.report.exists() and args.output.samefile(args.report):
            raise MappingError("Graph and report paths alias the same file")
        if args.report.exists() and not args.overwrite:
            raise MappingError("Report already exists; choose a new path or use --overwrite")
        graph, report = extract_file(args.input, coordinates=args.coordinates, semantic_edges=args.semantic_edges, viewport=args.viewport)
        if args.output.exists() and not args.overwrite:
            report["ledger"].append({"source_ref": "document", "feature": "output-path", "action": "blocked", "detail": "Graph already exists; choose a new path or use --overwrite"})
            report["native_mapping_eligibility"] = "blocked"
            graph = None
        report["graph_written"] = False
        report["output"] = None
        report["blocking_count"] = sum(item["action"] == "blocked" for item in report["ledger"])
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2, ensure_ascii=False, allow_nan=False) + "\n", encoding="utf-8")
        if graph is not None:
            try:
                args.output.parent.mkdir(parents=True, exist_ok=True)
                args.output.write_text(json.dumps(graph, indent=2, ensure_ascii=False, allow_nan=False) + "\n", encoding="utf-8")
                report["graph_written"] = True
                report["output"] = str(args.output)
            except (OSError, UnicodeError, ValueError) as error:
                report["ledger"].append({"source_ref": "document", "feature": "output-write", "action": "blocked", "detail": str(error)})
                report["native_mapping_eligibility"] = "blocked"
                report["blocking_count"] += 1
                graph = None
            args.report.write_text(json.dumps(report, indent=2, ensure_ascii=False, allow_nan=False) + "\n", encoding="utf-8")
        print(json.dumps({"report": str(args.report), "graph": str(args.output) if graph is not None else None, "native_mapping_eligibility": report["native_mapping_eligibility"], "blocking_count": report["blocking_count"], "live_import": "not executed"}, ensure_ascii=False))
        return 0 if graph is not None else 2
    except (OSError, MappingError, ValueError) as error:
        print(f"SVG extraction failed: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
