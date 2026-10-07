#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Package an explicit semantic graph as a local Lucid Standard Import v1 file.

Run: uv run --script scripts/build_native.py graph.json --output diagram.lucid
This helper performs no SVG inference, account access, network calls, or live import.
"""

from __future__ import annotations

import argparse
import html
import io
import json
import math
from pathlib import Path
import re
import sys
import zipfile

sys.dont_write_bytecode = True
from native_catalog import catalog_metadata, format_properties, native_type, spec, validate_properties


ID_PATTERN = re.compile(r"[A-Za-z0-9_.~-]{1,36}\Z")
COLOR_PATTERN = re.compile(r"#[0-9A-Fa-f]{6}\Z")
FONT_PATTERN = re.compile(r"[A-Za-z0-9][A-Za-z0-9 ,._-]{0,127}\Z")
STROKE_STYLES = {"solid", "dashed", "dotted"}
LINE_TYPES = {"straight", "elbow", "curved"}
MARKERS = {"none", "aggregation", "arrow", "hollowArrow", "openArrow", "async1", "async2",
           "closedSquare", "openSquare", "bpmnConditional", "bpmnDefault", "closedCircle",
           "openCircle", "composition", "exactlyOne", "generalization", "many", "nesting",
           "one", "oneOrMore", "zeroOrMore", "zeroOrOne"}
TEXT_FIELDS = {"text_color", "font_size", "font_family", "bold", "italic", "underline", "strike", "text_align", "vertical_align"}
LABEL_FIELDS = {"label_position", "label_side", "label_color", "label_font_size", "label_font_family",
                "label_bold", "label_italic", "label_underline", "label_strike", "label_align", "label_vertical_align"}
NODE_REQUIRED = {"id", "type", "x", "y", "width", "height", "label"}
NODE_FIELDS = NODE_REQUIRED | TEXT_FIELDS | {"fill", "stroke", "stroke_width", "stroke_style", "rounding", "rotation", "opacity", "z_index", "properties"}
EDGE_REQUIRED = {"id", "source", "target"}
EDGE_FIELDS = EDGE_REQUIRED | LABEL_FIELDS | {"label", "labels", "source_port", "target_port", "line_type", "stroke", "stroke_width", "stroke_style",
                                         "source_marker", "target_marker", "z_index", "joints", "elbow_points", "smart"}
ROOT_FIELDS = {"title", "nodes", "edges", "page_width", "page_height", "page_fill", "infinite_canvas", "auto_tiling", "groups", "layers"}
MULTI_LABEL_FIELDS = {"text", "position", "side", "color", "font_size", "font_family", "bold", "italic", "underline", "strike", "text_align", "vertical_align"}
MISSING = object()
MAX_DOCUMENT_BYTES = 2_000_000
MAX_PAGE_SIZE = 20_000
SCHEMA_SOURCES = [
    "https://lucid.readme.io/docs/overview-si",
    "https://lucid.readme.io/docs/pages-si",
    "https://lucid.readme.io/docs/shapes-si",
    "https://lucid.readme.io/docs/standard-library-si",
    "https://lucid.readme.io/docs/shape-library-si",
    "https://lucid.readme.io/docs/lines-si",
    "https://lucid.readme.io/docs/reference-si",
    "https://lucid.readme.io/docs/groups-si",
    "https://lucid.readme.io/docs/layers-si",
]
CONTRACT = """Input contract (coordinates and font sizes are pixels):
  {"title":"Optional page title", "nodes":[
    {"id":"a", "type":"rectangle", "x":20, "y":20,
     "width":100, "height":60, "label":"Start",
     "fill":"#ffffff", "stroke":"#000000",
     "text_color":"#000000", "font_size":14},
    {"id":"b", "type":"ellipse", "x":180, "y":20,
     "width":100, "height":60, "label":"End"}], "edges":[
    {"id":"e", "source":"a", "target":"b", "label":"Optional",
     "source_port":{"x":1,"y":0.5},
     "target_port":{"x":0,"y":0.5}}]}
Required top-level array: nodes. edges defaults to []. Only documented fields are accepted.
Node types are the documented allowlist in sibling native_catalog.py; ellipse
aliases native circle. Type-specific vendor fields belong in node.properties.
The common label is required; use an empty label for types forbidding text.
x/y denote the top-left corner.
Node coordinates must be finite and nonnegative; width/height must be positive, and
the full node bounds must fit inside 20000 by 20000 pixels. IDs must be globally
unique ASCII alphanumeric or -_.~, length 1..36. Labels are literal text, not HTML.
Colors use #RRGGBB. font_size is finite and positive. font_family uses 1..128 ASCII
letters/digits/spaces/comma/period/underscore/hyphen, beginning with a letter/digit.
Text flags bold/italic/underline/strike are booleans; text_align is left or center;
vertical_align accepts the documented center value. Labels are escaped literal
text. Text shapes reject fill/stroke/stroke_width/stroke_style/rounding.
Common optional node fields: stroke_width (integer >=0), stroke_style
(solid/dashed/dotted), rounding (integer >=0, twice corner radius), rotation
(0..360 degrees), opacity (whole 0..100), z_index (signed integer), font_family,
bold, italic, underline, strike, text_align, vertical_align. Rotation is rejected
on documented incompatible types. Width 0 is emitted literally; its no-stroke
rendering semantics require a live check. Fractional stroke widths are rejected.
Default non-cloud node styling is white
fill, black 1px solid border, black 14px text.
For namedShape/namedContainer, fill/stroke/textColor are omitted unless explicitly
provided, and text formatting uses only explicit options, preserving native
provider/library defaults. Connections default to attached straight arrows;
source/target positions are normalized x/y in [0,1], defaulting to the
right/left midpoint. Optional edge fields: line_type (straight/elbow/curved),
stroke/stroke_width/stroke_style, source_marker/target_marker (22 documented styles),
z_index, joints (straight absolute points), elbow_points (orthogonal elbow points),
smart (boolean). smart:true omits both ports and conflicts with explicit ports or
route points. Curved routing uses Lucid's curve family, not exact SVG Bezier data.
Markers: none aggregation arrow hollowArrow openArrow async1 async2 closedSquare
openSquare bpmnConditional bpmnDefault closedCircle openCircle composition
exactlyOne generalization many nesting one oneOrMore zeroOrMore zeroOrOne.
Edge labels default to black 14px at midpoint, top side. Optional label fields:
label_position (0..1), label_side (top/middle/bottom), label_color, label_font_size,
label_font_family, label_bold/italic/underline/strike, label_align (left/center),
label_vertical_align (center). Label options require label.
Alternatively labels:[{text,position?,side?,color?,font_size?,font_family?,bold?,
italic?,underline?,strike?,text_align?,vertical_align?}] uses the same style values
and defaults. labels is exclusive with label and all label_* keys.
source/target may alternatively be explicit endpoint objects without a style:
{type:"shapeEndpoint",shapeId:"node",position?:{x,y}},
{type:"lineEndpoint",lineId:"other-edge",position:0..1}, or
{type:"positionEndpoint",position:{x,y}}. Markers remain source_marker/target_marker.
Object endpoints conflict with corresponding source_port/target_port. Omitted
shape-object position stays omitted (automatic attachment); smart:true requires
two shape endpoints with no positions. Line attachment references are acyclic.
Explicit elbow points require resolvable fixed shape or absolute endpoints.
Absolute endpoint/control coordinates may be negative, bounded to +/-20000px.
Optional graph fields: paired page_width/page_height (1..20000), page_fill,
infinite_canvas, auto_tiling; explicit size or tiling conflicts with infinite canvas.
groups:[{id,items:[IDs],z_index?}], layers:[{id,title,items:[IDs],layer_index?}].
IDs share the global namespace. Groups may contain shapes, lines, groups; layers
may contain shapes, lines, groups. Membership is acyclic with one direct parent.
Outputs contain one page and document.json only. --report writes machine-readable
emitted choices, defaults, supported fields, and live-check/approximation notices.
Packaging is deterministic; existing supported graph defaults remain unchanged.
This validates the supported documented subset, not a full upstream schema.
Live import and layout must be verified separately with an authorized account.
"""


class GraphError(ValueError):
    """An explicit graph or output contract is invalid."""


def require_object(value: object, label: str, allowed: set[str], required: set[str]) -> dict:
    if not isinstance(value, dict):
        raise GraphError(f"{label} must be an object")
    if any(not isinstance(key, str) for key in value):
        raise GraphError(f"{label} field names must be strings")
    extra = set(value) - allowed
    missing = required - set(value)
    if extra:
        raise GraphError(f"{label} has unsupported fields: {', '.join(sorted(extra))}")
    if missing:
        raise GraphError(f"{label} is missing: {', '.join(sorted(missing))}")
    return value


def identifier(value: object, label: str) -> str:
    if not isinstance(value, str) or not ID_PATTERN.fullmatch(value):
        raise GraphError(f"{label} must contain 1..36 ASCII alphanumeric or -_.~ characters")
    return value


def number(value: object, label: str, *, minimum: float = 0, positive: bool = False, maximum: float | None = None) -> int | float:
    if type(value) not in (int, float):
        raise GraphError(f"{label} must be a finite number, not a boolean or string")
    try:
        finite = math.isfinite(value)
    except OverflowError:
        finite = False
    if not finite or value < minimum or (positive and value <= 0) or (maximum is not None and value > maximum):
        raise GraphError(f"{label} is outside the supported finite range")
    return value


def integer(value: object, label: str, *, minimum: int | None = None, maximum: int | None = None) -> int:
    if type(value) is not int or (minimum is not None and value < minimum) or (maximum is not None and value > maximum):
        raise GraphError(f"{label} must be an integer in the supported range")
    try:
        if not math.isfinite(value):
            raise GraphError(f"{label} must be a finite integer")
    except OverflowError as error:
        raise GraphError(f"{label} is outside the supported finite range") from error
    return value


def boolean(value: object, label: str) -> bool:
    if type(value) is not bool:
        raise GraphError(f"{label} must be a boolean")
    return value


def choice(value: object, label: str, choices: set[str]) -> str:
    if not isinstance(value, str) or value not in choices:
        raise GraphError(f"{label} must be one of: {', '.join(sorted(choices))}")
    return value


def text(value: object, label: str) -> str:
    if not isinstance(value, str):
        raise GraphError(f"{label} must be a string")
    # JSON accepts isolated Unicode surrogates; UTF-8 text in the import does not.
    try:
        value.encode("utf-8")
    except UnicodeEncodeError as error:
        raise GraphError(f"{label} must contain valid Unicode text") from error
    return value


def color(value: object, label: str) -> str:
    if not isinstance(value, str) or not COLOR_PATTERN.fullmatch(value):
        raise GraphError(f"{label} must be a #RRGGBB color")
    return value.lower()


def position(value: object, label: str) -> dict:
    item = require_object(value, label, {"x", "y"}, {"x", "y"})
    return {key: number(item[key], f"{label}.{key}", maximum=1) for key in ("x", "y")}


def absolute_points(value: object, label: str) -> list[dict]:
    if not isinstance(value, list):
        raise GraphError(f"{label} must be an array of absolute x/y points")
    points = []
    for index, raw in enumerate(value):
        context = f"{label}[{index}]"
        item = require_object(raw, context, {"x", "y"}, {"x", "y"})
        points.append({key: number(item[key], f"{context}.{key}", minimum=-MAX_PAGE_SIZE, maximum=MAX_PAGE_SIZE) for key in ("x", "y")})
    return points


def font_family(value: object, label: str) -> str:
    if not isinstance(value, str) or not FONT_PATTERN.fullmatch(value) or any(not family.strip() for family in value.split(",")):
        raise GraphError(f"{label} must be a safe ASCII font-family name or list (1..128 characters)")
    return value


def css_font_family(value: str) -> str:
    # Quote names such as "Source Sans 3" or "Font.Name" that are not a sequence
    # of CSS identifiers. Input validation excludes quotes and escape characters.
    identifier_sequence = re.compile(r"[-_A-Za-z][-_A-Za-z0-9]*(?: +[-_A-Za-z][-_A-Za-z0-9]*)*\Z")
    return ",".join(family if identifier_sequence.fullmatch(family.strip()) else f"'{family.strip()}'" for family in value.split(","))


def text_options(item: dict, context: str, *, label: bool = False) -> dict:
    names = {"text_color": "label_color", "font_size": "label_font_size", "font_family": "label_font_family",
             "bold": "label_bold", "italic": "label_italic", "underline": "label_underline", "strike": "label_strike",
             "text_align": "label_align", "vertical_align": "label_vertical_align"} if label else {key: key for key in TEXT_FIELDS}
    result = {}
    for field, source in names.items():
        if source not in item:
            continue
        value, name = item[source], f"{context}.{source}"
        if field == "text_color":
            result[field] = color(value, name)
        elif field == "font_size":
            result[field] = number(value, name, positive=True)
        elif field == "font_family":
            result[field] = font_family(value, name)
        elif field == "text_align":
            result[field] = choice(value, name, {"left", "center"})
        elif field == "vertical_align":
            result[field] = choice(value, name, {"center"})
        else:
            result[field] = boolean(value, name)
    return result


def formatted_text(label: str, font_size: int | float = 14, text_color: str = "#000000", **options: object) -> str:
    escaped = "<br>".join(html.escape(line, quote=True) for line in label.split("\n"))
    for flag, tag in (("strike", "s"), ("underline", "u"), ("italic", "i"), ("bold", "b")):
        if options.get(flag, False):
            escaped = f"<{tag}>{escaped}</{tag}>"
    style = f'font-family:{css_font_family(options.get("font_family", "Liberation Sans"))};font-size:{font_size}px;color:{text_color};text-align:{options.get("text_align", "center")}'
    if "vertical_align" in options:
        style += f';vertical-align:{options["vertical_align"]}'
    return f'<p style="{html.escape(style, quote=True)}">{escaped}</p>'


def formatted_library_text(label: str, options: dict) -> str:
    escaped = "<br>".join(html.escape(line, quote=True) for line in label.split("\n"))
    for flag, tag in (("strike", "s"), ("underline", "u"), ("italic", "i"), ("bold", "b")):
        if options.get(flag, False):
            escaped = f"<{tag}>{escaped}</{tag}>"
    fields = (("font_family", "font-family", ""), ("font_size", "font-size", "px"), ("text_color", "color", ""),
              ("text_align", "text-align", ""), ("vertical_align", "vertical-align", ""))
    style = ";".join(f"{css}:{css_font_family(options[key]) if key == 'font_family' else options[key]}{suffix}" for key, css, suffix in fields if key in options)
    return f'<p style="{html.escape(style, quote=True)}">{escaped}</p>' if style else escaped


def stroke_options(item: dict, context: str) -> dict:
    return {
        "color": color(item.get("stroke", "#000000"), f"{context}.stroke"),
        "width": integer(item.get("stroke_width", 1), f"{context}.stroke_width", minimum=0),
        "style": choice(item.get("stroke_style", "solid"), f"{context}.stroke_style", STROKE_STYLES),
    }


def register_id(raw: object, context: str, ids: set[str]) -> str:
    object_id = identifier(raw, context)
    if object_id in ids:
        raise GraphError(f"Duplicate object ID: {object_id}")
    ids.add(object_id)
    return object_id


def resolve_endpoint(endpoint: dict, boxes: dict[str, dict]) -> dict:
    if endpoint["type"] == "positionEndpoint":
        return endpoint["position"]
    if endpoint["type"] != "shapeEndpoint" or "position" not in endpoint:
        raise GraphError("Explicit elbow points require fixed shape ports or absolute endpoints; line attachment geometry is not resolved")
    box, port = boxes[endpoint["shapeId"]], endpoint["position"]
    if box.get("rotation", 0) not in (0, 360):
        raise GraphError("Explicit elbow points with rotated shape ports require a verified rotation-pivot contract")
    return {"x": box["x"] + box["w"] * port["x"], "y": box["y"] + box["h"] * port["y"]}


def endpoint(raw: object, context: str, marker: str, default_port: dict, smart: bool,
             node_ids: set[str], line_ids: set[str], legacy_port: object = MISSING) -> dict:
    if isinstance(raw, str):
        shape_id = identifier(raw, context)
        if shape_id not in node_ids:
            raise GraphError(f"{context} references an unknown node: {shape_id}")
        result = {"type": "shapeEndpoint", "style": marker, "shapeId": shape_id}
        if not smart:
            result["position"] = position(default_port if legacy_port is MISSING else legacy_port, f"{context}_port")
        return result
    item = require_object(raw, context, {"type", "shapeId", "lineId", "position"}, {"type"})
    kind = choice(item["type"], f"{context}.type", {"shapeEndpoint", "lineEndpoint", "positionEndpoint"})
    if legacy_port is not MISSING:
        raise GraphError(f"{context}: endpoint objects conflict with a separate port field")
    result = {"type": kind, "style": marker}
    if kind == "shapeEndpoint":
        require_object(item, context, {"type", "shapeId", "position"}, {"type", "shapeId"})
        shape_id = identifier(item["shapeId"], f"{context}.shapeId")
        if shape_id not in node_ids:
            raise GraphError(f"{context}.shapeId references an unknown node: {shape_id}")
        result["shapeId"] = shape_id
        if "position" in item:
            if smart:
                raise GraphError(f"{context}: smart lines conflict with an explicit shape position")
            result["position"] = position(item["position"], f"{context}.position")
    elif kind == "lineEndpoint":
        require_object(item, context, {"type", "lineId", "position"}, {"type", "lineId", "position"})
        if smart:
            raise GraphError(f"{context}: smart lines require two shape endpoints")
        line_id = identifier(item["lineId"], f"{context}.lineId")
        if line_id not in line_ids:
            raise GraphError(f"{context}.lineId references an unknown edge: {line_id}")
        result.update(lineId=line_id, position=number(item["position"], f"{context}.position", maximum=1))
    else:
        require_object(item, context, {"type", "position"}, {"type", "position"})
        if smart:
            raise GraphError(f"{context}: smart lines require two shape endpoints")
        result["position"] = absolute_points([item["position"]], f"{context}.position")[0]
    return result


def line_labels(edge: dict, context: str) -> list[dict] | None:
    if "labels" in edge:
        if set(edge) & ({"label"} | LABEL_FIELDS):
            raise GraphError(f"{context}.labels conflicts with label and label_* fields")
        if not isinstance(edge["labels"], list):
            raise GraphError(f"{context}.labels must be an array")
        result = []
        for index, raw in enumerate(edge["labels"]):
            name = f"{context}.labels[{index}]"
            item = require_object(raw, name, MULTI_LABEL_FIELDS, {"text"})
            options = text_options(item, name)
            if "color" in item:
                options["text_color"] = color(item["color"], f"{name}.color")
            result.append({"text": formatted_text(text(item["text"], f"{name}.text"), **options),
                           "position": number(item.get("position", .5), f"{name}.position", maximum=1),
                           "side": choice(item.get("side", "top"), f"{name}.side", {"top", "middle", "bottom"})})
        return result
    if "label" not in edge:
        if set(edge) & LABEL_FIELDS:
            raise GraphError(f"{context}: label styling requires a label")
        return None
    return [{"text": formatted_text(text(edge["label"], f"{context}.label"), **text_options(edge, context, label=True)),
             "position": number(edge.get("label_position", .5), f"{context}.label_position", maximum=1),
             "side": choice(edge.get("label_side", "top"), f"{context}.label_side", {"top", "middle", "bottom"})}]


def validate_line_attachments(lines: list[dict]) -> None:
    dependencies = {line["id"]: {line[key]["lineId"] for key in ("endpoint1", "endpoint2") if line[key]["type"] == "lineEndpoint"} for line in lines}
    ready = [line_id for line_id, targets in dependencies.items() if not targets]
    dependents: dict[str, list[str]] = {line_id: [] for line_id in dependencies}
    for line_id, targets in dependencies.items():
        for target in targets:
            dependents[target].append(line_id)
    completed = 0
    while ready:
        target = ready.pop()
        completed += 1
        for line_id in dependents[target]:
            dependencies[line_id].remove(target)
            if not dependencies[line_id]:
                ready.append(line_id)
    if completed != len(lines):
        raise GraphError("Line attachment references must be acyclic")


def validate_elbow(points: list[dict], context: str) -> None:
    previous_axis = None
    for start, end in zip(points, points[1:]):
        same_x = math.isclose(start["x"], end["x"], rel_tol=0, abs_tol=1e-8)
        same_y = math.isclose(start["y"], end["y"], rel_tol=0, abs_tol=1e-8)
        if same_x == same_y:
            raise GraphError(f"{context} must form nonzero orthogonal segments including its endpoints")
        axis = "vertical" if same_x else "horizontal"
        if axis == previous_axis:
            raise GraphError(f"{context} control points must form 90-degree turns")
        previous_axis = axis


def collections(root: dict, ids: set[str]) -> tuple[list[dict], list[dict]]:
    groups, layers = [], []
    for key, allowed, required, destination in (
        ("groups", {"id", "items", "z_index"}, {"id", "items"}, groups),
        ("layers", {"id", "title", "items", "layer_index"}, {"id", "title", "items"}, layers),
    ):
        for index, raw in enumerate(root.get(key, [])):
            context = f"{key}[{index}]"
            item = require_object(raw, context, allowed, required)
            result = {"id": register_id(item["id"], f"{context}.id", ids)}
            if key == "layers":
                result["title"] = text(item["title"], f"{context}.title")
            if not isinstance(item["items"], list):
                raise GraphError(f"{context}.items must be an array of IDs")
            result["items"] = [identifier(value, f"{context}.items") for value in item["items"]]
            if len(result["items"]) != len(set(result["items"])):
                raise GraphError(f"{context}.items contains duplicate membership")
            if "z_index" in item:
                result["zIndex"] = integer(item["z_index"], f"{context}.z_index")
            if "layer_index" in item:
                result["layerIndex"] = integer(item["layer_index"], f"{context}.layer_index")
            destination.append(result)
    layer_ids = {item["id"] for item in layers}
    parents = {}
    for container in groups + layers:
        for child in container["items"]:
            if child not in ids or child in layer_ids:
                raise GraphError(f"{container['id']}.items references an unknown or ineligible item: {child}")
            if child in parents:
                raise GraphError(f"Item {child} has more than one direct group/layer parent")
            parents[child] = container["id"]
    # Iterative walk avoids recursion limits for deeply nested, otherwise valid groups.
    completed = set()
    for item in parents:
        visited, current = set(), item
        while current in parents and current not in completed:
            if current in visited:
                raise GraphError("Group membership must be acyclic")
            visited.add(current)
            current = parents[current]
        completed.update(visited)
    return groups, layers


def build_document(graph: object) -> dict:
    root = require_object(graph, "graph", ROOT_FIELDS, {"nodes"})
    title = text(root.get("title", "Imported diagram"), "graph.title")
    if not title.strip():
        raise GraphError("graph.title must not be blank")
    for key in ("nodes", "edges", "groups", "layers"):
        if not isinstance(root.get(key, []), list):
            raise GraphError(f"graph.{key} must be an array")
    ids: set[str] = set()
    node_ids: set[str] = set()
    shapes, boxes = [], {}
    max_x = max_y = 0
    for index, raw in enumerate(root["nodes"]):
        context = f"nodes[{index}]"
        node = require_object(raw, context, NODE_FIELDS, NODE_REQUIRED)
        node_id = register_id(node["id"], f"{context}.id", ids)
        node_ids.add(node_id)
        try:
            actual_type = native_type(node["type"])
            shape_spec = spec(node["type"])
        except (ValueError, TypeError, OverflowError) as error:
            raise GraphError(f"{context}.type: {error}") from error
        x = number(node["x"], f"{context}.x", maximum=MAX_PAGE_SIZE)
        y = number(node["y"], f"{context}.y", maximum=MAX_PAGE_SIZE)
        width = number(node["width"], f"{context}.width", positive=True, maximum=MAX_PAGE_SIZE)
        height = number(node["height"], f"{context}.height", positive=True, maximum=MAX_PAGE_SIZE)
        if x + width > MAX_PAGE_SIZE or y + height > MAX_PAGE_SIZE:
            raise GraphError(f"{context} bounds exceed 20000 by 20000 pixels")
        max_x, max_y = max(max_x, x + width), max(max_y, y + height)
        options = text_options(node, context)
        label = text(node["label"], f"{context}.label")
        forbidden = set(shape_spec.get("forbidden_common", []))
        if "text" in forbidden and (label or set(node) & TEXT_FIELDS):
            raise GraphError(f"{context}: this native type forbids text; use an empty label and no text styling")
        if "style" in forbidden and set(node) & {"fill", "stroke", "stroke_width", "stroke_style", "rounding"}:
            raise GraphError(f"{context}: this native type does not accept fill, stroke, or rounding")
        item = {
            "id": node_id,
            "type": actual_type,
            "boundingBox": {"x": x, "y": y, "w": width, "h": height},
        }
        if "rotation" in node:
            if not shape_spec.get("rotation_supported", True):
                raise GraphError(f"{context}: this native type does not support rotation")
            item["boundingBox"]["rotation"] = number(node["rotation"], f"{context}.rotation", maximum=360)
        if "text" not in forbidden:
            item["text"] = formatted_library_text(label, options) if actual_type in {"namedShape", "namedContainer"} else formatted_text(label, **options)
        item["zIndex"] = integer(node.get("z_index", 1), f"{context}.z_index")
        if "style" not in forbidden:
            if actual_type in {"namedShape", "namedContainer"}:
                style = {}
                if "fill" in node:
                    style["fill"] = {"type": "color", "color": color(node["fill"], f"{context}.fill")}
                explicit_stroke = {}
                if "stroke" in node:
                    explicit_stroke["color"] = color(node["stroke"], f"{context}.stroke")
                if "stroke_width" in node:
                    explicit_stroke["width"] = integer(node["stroke_width"], f"{context}.stroke_width", minimum=0)
                if "stroke_style" in node:
                    explicit_stroke["style"] = choice(node["stroke_style"], f"{context}.stroke_style", STROKE_STYLES)
                if explicit_stroke:
                    style["stroke"] = explicit_stroke
                if "text_color" in node:
                    style["textColor"] = options["text_color"]
            else:
                style = {
                    "fill": {"type": "color", "color": color(node.get("fill", "#ffffff"), f"{context}.fill")},
                    "stroke": stroke_options(node, context),
                    "textColor": options.get("text_color", "#000000"),
                }
            if "rounding" in node:
                style["rounding"] = integer(node["rounding"], f"{context}.rounding", minimum=0)
            if style:
                item["style"] = style
        if "opacity" in node:
            item["opacity"] = integer(node["opacity"], f"{context}.opacity", minimum=0, maximum=100)
        try:
            properties = validate_properties(node["type"], node.get("properties", {}), width, height)
            item.update(format_properties(node["type"], properties))
        except (ValueError, TypeError, OverflowError) as error:
            raise GraphError(f"{context}.properties: {error}") from error
        boxes[node_id] = item["boundingBox"]
        shapes.append(item)
    lines, raw_edges, line_ids = [], [], set()
    for index, raw in enumerate(root.get("edges", [])):
        context = f"edges[{index}]"
        edge = require_object(raw, context, EDGE_FIELDS, EDGE_REQUIRED)
        line_ids.add(register_id(edge["id"], f"{context}.id", ids))
        raw_edges.append(edge)
    for index, edge in enumerate(raw_edges):
        context = f"edges[{index}]"
        edge_id = edge["id"]
        line_type = choice(edge.get("line_type", "straight"), f"{context}.line_type", LINE_TYPES)
        smart = boolean(edge.get("smart", False), f"{context}.smart")
        if smart and set(edge) & {"source_port", "target_port", "joints", "elbow_points"}:
            raise GraphError(f"{context}: smart lines conflict with explicit ports or route points")
        if "joints" in edge and line_type != "straight":
            raise GraphError(f"{context}.joints requires line_type straight")
        if "elbow_points" in edge and line_type != "elbow":
            raise GraphError(f"{context}.elbow_points requires line_type elbow")
        endpoints = []
        for key, default, default_marker in (("source", {"x": 1, "y": .5}, "none"), ("target", {"x": 0, "y": .5}, "arrow")):
            marker = choice(edge.get(f"{key}_marker", default_marker), f"{context}.{key}_marker", MARKERS)
            endpoints.append(endpoint(edge[key], f"{context}.{key}", marker, default, smart, node_ids, line_ids, edge.get(f"{key}_port", MISSING)))
        item = {
            "id": edge_id,
            "lineType": line_type,
            "endpoint1": endpoints[0],
            "endpoint2": endpoints[1],
            "stroke": stroke_options(edge, context),
            "zIndex": integer(edge.get("z_index", 0), f"{context}.z_index"),
        }
        labels = line_labels(edge, context)
        if labels is not None:
            item["text"] = labels
        if "joints" in edge:
            item["joints"] = absolute_points(edge["joints"], f"{context}.joints")
        if "elbow_points" in edge:
            controls = absolute_points(edge["elbow_points"], f"{context}.elbow_points")
            validate_elbow([resolve_endpoint(endpoints[0], boxes), *controls, resolve_endpoint(endpoints[1], boxes)], f"{context}.elbow_points")
            item["elbowControlPoints"] = controls
        lines.append(item)
    validate_line_attachments(lines)
    groups, layers = collections(root, ids)
    page_id, index = "page1", 1
    while page_id in ids:
        index += 1
        page_id = f"page{index}"
    settings = {"fillColor": color(root.get("page_fill", "#ffffff"), "graph.page_fill"), "size": {
        "type": "custom",
        "w": min(MAX_PAGE_SIZE, max(100, math.ceil(max_x) + 32)),
        "h": min(MAX_PAGE_SIZE, max(100, math.ceil(max_y) + 32)),
    }}
    if ("page_width" in root) != ("page_height" in root):
        raise GraphError("graph.page_width and page_height must be provided together")
    if "infinite_canvas" in root:
        settings["infiniteCanvas"] = boolean(root["infinite_canvas"], "graph.infinite_canvas")
    if root.get("infinite_canvas", False) and set(root) & {"page_width", "page_height", "auto_tiling"}:
        raise GraphError("Explicit page size or tiling is ineffective with infinite_canvas true")
    if "page_width" in root:
        settings["size"] = {"type": "custom", "w": number(root["page_width"], "graph.page_width", minimum=1, maximum=MAX_PAGE_SIZE),
                            "h": number(root["page_height"], "graph.page_height", minimum=1, maximum=MAX_PAGE_SIZE)}
        settings.setdefault("infiniteCanvas", False)
        settings["autoTiling"] = boolean(root.get("auto_tiling", False), "graph.auto_tiling")
    elif "auto_tiling" in root:
        settings["autoTiling"] = boolean(root["auto_tiling"], "graph.auto_tiling")
    if settings.get("infiniteCanvas", False):
        settings.pop("size")
    page = {"id": page_id, "title": title, "settings": settings, "shapes": shapes, "lines": lines}
    if "groups" in root:
        page["groups"] = groups
    if "layers" in root:
        page["layers"] = layers
    return {"version": 1, "documentSettings": {"units": "px"}, "pages": [page]}


def compatibility_report(graph: dict, document: dict) -> dict:
    page = document["pages"][0]
    approximations, live_checks, decisions = [], [], []
    if any(node["type"] == "ellipse" for node in graph["nodes"]):
        approximations.append("ellipse nodes use native circle shapes with the supplied rectangular bounds; verify rendered geometry in Lucid")
    for node, shape in zip(graph["nodes"], page["shapes"]):
        decisions.append({"id": shape["id"], "kind": "shape", "source_type": node["type"], "native_type": shape["type"],
                          "explicit_fields": sorted(node), "emitted": shape})
        if shape["type"] in {"namedShape", "namedContainer"}:
            live_checks.append({"id": shape["id"], "feature": "native_library_defaults", "reason": "Unspecified fill/stroke/textColor are omitted to retain native library styling; provider appearance requires a live rendered check"})
        if "font_family" in node:
            live_checks.append({"id": shape["id"], "feature": "font_family", "reason": "Font declaration emitted; availability, substitution, and text layout require a live rendered check"})
        if "rotation" in node:
            live_checks.append({"id": shape["id"], "feature": "rotation", "reason": "Clockwise native rotation emitted; SVG pivot/transform equivalence requires a live rendered check"})
        if shape.get("style", {}).get("stroke", {}).get("width") == 0:
            live_checks.append({"id": shape["id"], "feature": "zero_width_stroke", "reason": "Integer width 0 emitted; the documented schema does not establish invisible-stroke rendering semantics"})
    for edge, line in zip(graph.get("edges", []), page["lines"]):
        decisions.append({"id": line["id"], "kind": "line", "explicit_fields": sorted(edge), "emitted": line})
        if line["lineType"] == "curved":
            approximations.append(f"Line {line['id']} uses Lucid curved routing; exact SVG Bezier control geometry is not represented")
        if line["stroke"]["width"] == 0:
            live_checks.append({"id": line["id"], "feature": "zero_width_stroke", "reason": "Integer width 0 emitted; invisible-stroke rendering semantics require a live check"})
        if "label_font_family" in edge or any("font_family" in label for label in edge.get("labels", [])):
            live_checks.append({"id": line["id"], "feature": "label_font_family", "reason": "Font availability and exact line-label layout require a live rendered check"})
    return {
        "report_version": 1,
        "supported_fields": {"graph": sorted(ROOT_FIELDS), "node": sorted(NODE_FIELDS), "edge": sorted(EDGE_FIELDS),
                             "line_label": sorted(MULTI_LABEL_FIELDS), "endpoint_object": ["type", "shapeId", "lineId", "position"],
                             "group": ["id", "items", "z_index"], "layer": ["id", "title", "items", "layer_index"]},
        "enums": {"stroke_style": sorted(STROKE_STYLES), "line_type": sorted(LINE_TYPES), "marker": sorted(MARKERS),
                  "text_align": ["left", "center"], "vertical_align": ["center"], "label_side": ["top", "middle", "bottom"]},
        "defaults": {"node_fill": "#ffffff", "node_style_scope": "Non-cloud types; namedShape/namedContainer emit only explicit style keys",
                     "node_text_scope": "Non-cloud nodes and line labels; namedShape/namedContainer text emits only explicit formatting",
                     "stroke_color": "#000000", "stroke_width": 1, "stroke_style": "solid",
                     "text_color": "#000000", "font_family": "Liberation Sans", "font_size_px": 14, "text_align": "center",
                     "opacity_percent": "100 when omitted (vendor default)",
                     "node_z_index": 1, "line_z_index": 0, "line_type": "straight", "source_marker": "none", "target_marker": "arrow",
                     "source_port": {"x": 1, "y": .5}, "target_port": {"x": 0, "y": .5}, "label_position": .5, "label_side": "top",
                     "page_size": "tight node extent plus 32px; minimum 100px; maximum 20000px unless explicit", "page_fill": "#ffffff"},
        "decisions": decisions,
        "page_settings": page["settings"],
        "groups": page.get("groups", []), "layers": page.get("layers", []),
        "approximations": approximations,
        "requires_live_check": live_checks,
        "unsupported_source_features": ["arbitrary SVG paths and exact Bezier controls", "custom dash arrays or marker geometry", "SVG fill:none",
                                        "fractional stroke widths", "text baseline/anchor/padding/letter-spacing", "unresolved SVG transforms and root viewBox scaling"],
        "schema_sources": SCHEMA_SOURCES,
        "catalog_sources": sorted({url for node in graph["nodes"] for url in spec(node["type"])["source_urls"]}),
        "native_catalog": catalog_metadata(),
        "local_validation": "passed documented subset checks",
        "live_import": "not executed",
        "rendered_fidelity": "not measured; emitted data does not establish visual equivalence",
    }


def document_bytes(document: dict) -> bytes:
    raw = (json.dumps(document, indent=2, ensure_ascii=False, allow_nan=False) + "\n").encode("utf-8")
    if len(raw) >= MAX_DOCUMENT_BYTES:
        raise GraphError("document.json must be smaller than the conservative 2000000-byte limit")
    return raw


def package_bytes(raw: bytes) -> bytes:
    target = io.BytesIO()
    with zipfile.ZipFile(target, "w", compression=zipfile.ZIP_STORED) as archive:
        entry = zipfile.ZipInfo("document.json", date_time=(2000, 1, 1, 0, 0, 0))
        entry.compress_type = zipfile.ZIP_STORED
        entry.create_system = 0
        entry.external_attr = 0x20  # Fixed DOS archive bit; no platform-specific permissions.
        archive.writestr(entry, raw)
    return target.getvalue()


def unique_json_object(pairs: list[tuple[str, object]]) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            raise GraphError(f"Duplicate JSON field: {key}")
        result[key] = value
    return result


def reject_nonfinite(value: str) -> None:
    raise GraphError(f"Invalid JSON numeric constant: {value}")


def main(argv: list[str] | None = None) -> int:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0], epilog=CONTRACT, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("input", type=Path, help="Explicit semantic graph JSON; SVG files are not accepted")
    parser.add_argument("--output", required=True, type=Path, help="Exact .lucid ZIP output path")
    parser.add_argument("--document-json", type=Path, help="Optional exact path for the same document.json bytes")
    parser.add_argument("--report", type=Path, help="Optional exact JSON path for emitted compatibility decisions and live-check limits")
    args = parser.parse_args(argv)
    try:
        if args.output.suffix.lower() != ".lucid":
            raise GraphError("--output must have a .lucid extension")
        paths = [args.input.resolve(), args.output.resolve()]
        if args.document_json is not None:
            paths.append(args.document_json.resolve())
        if args.report is not None:
            paths.append(args.report.resolve())
        if len(set(paths)) != len(paths):
            raise GraphError("Input and output paths must be distinct")
        for index, path in enumerate(paths):
            for other in paths[index + 1:]:
                if path.exists() and other.exists() and path.samefile(other):
                    raise GraphError("Input and output files must not alias through hard links")
        graph = json.loads(args.input.read_text(encoding="utf-8-sig"), object_pairs_hook=unique_json_object, parse_constant=reject_nonfinite)
        document = build_document(graph)
        raw = document_bytes(document)
        package = package_bytes(raw)
        report = compatibility_report(graph, document)
        report.update(package=str(args.output), document_json=str(args.document_json) if args.document_json is not None else None)
        report_raw = (json.dumps(report, indent=2, ensure_ascii=False, allow_nan=False) + "\n").encode("utf-8")
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_bytes(package)
        if args.document_json is not None:
            args.document_json.parent.mkdir(parents=True, exist_ok=True)
            args.document_json.write_bytes(raw)
        if args.report is not None:
            args.report.parent.mkdir(parents=True, exist_ok=True)
            args.report.write_bytes(report_raw)
        page = document["pages"][0]
        print(json.dumps({
            "package": str(args.output),
            "document_json": str(args.document_json) if args.document_json is not None else None,
            "report": str(args.report) if args.report is not None else None,
            "shape_count": len(page["shapes"]),
            "connector_count": len(page["lines"]),
            "group_count": len(page.get("groups", [])),
            "layer_count": len(page.get("layers", [])),
            "local_validation": "passed documented subset checks",
            "approximations": report["approximations"],
            "requires_live_check": report["requires_live_check"],
            "live_import": "not executed",
        }, ensure_ascii=False))
        return 0
    except (ValueError, OSError, UnicodeError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
