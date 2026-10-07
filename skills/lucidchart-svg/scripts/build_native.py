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


TYPE_MAP = {"rectangle": "rectangle", "ellipse": "circle", "diamond": "diamond", "text": "text"}
ID_PATTERN = re.compile(r"[A-Za-z0-9_.~-]{1,36}\Z")
COLOR_PATTERN = re.compile(r"#[0-9A-Fa-f]{6}\Z")
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
]
CONTRACT = """Input contract (all coordinates and font sizes are pixels):
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
Node types: rectangle, ellipse, diamond, text. x/y denote the top-left corner.
Coordinates must be finite and nonnegative; width/height must be positive, and
the full node bounds must fit inside 20000 by 20000 pixels. IDs must be globally
unique ASCII alphanumeric or -_.~, length 1..36. Labels are literal text, not HTML.
Optional colors must use #RRGGBB. font_size must be finite and positive.
Text nodes accept text_color/font_size only; fill/stroke are rejected because
Lucid's native text shape does not accept a style object. ellipse uses the native
circle shape with the explicit width and height; this approximation requires
a live rendered check. Default node styling is white
fill, black 1px solid border, black 14px text. Connections are attached straight
arrows; source/target positions are normalized x/y in [0,1], defaulting to the
right/left midpoint. Edge labels use black 14px text at the line midpoint.
Outputs contain one page and document.json only. Packaging is deterministic.
This validates the supported documented subset, not a full upstream schema.
Live import and layout must be verified separately with an authorized account.
"""


class GraphError(ValueError):
    """An explicit graph or output contract is invalid."""


def require_object(value: object, label: str, allowed: set[str], required: set[str]) -> dict:
    if not isinstance(value, dict):
        raise GraphError(f"{label} must be an object")
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


def formatted_text(label: str, font_size: int | float = 14, text_color: str = "#000000") -> str:
    escaped = "<br>".join(html.escape(line, quote=True) for line in label.split("\n"))
    return f'<p style="font-family:Liberation Sans;font-size:{font_size}px;color:{text_color};text-align:center">{escaped}</p>'


def build_document(graph: object) -> dict:
    root = require_object(graph, "graph", {"title", "nodes", "edges"}, {"nodes"})
    title = text(root.get("title", "Imported diagram"), "graph.title")
    if not title.strip():
        raise GraphError("graph.title must not be blank")
    for key in ("nodes", "edges"):
        if not isinstance(root.get(key, []), list):
            raise GraphError(f"graph.{key} must be an array")
    ids: set[str] = set()
    node_ids: set[str] = set()
    shapes = []
    node_required = {"id", "type", "x", "y", "width", "height", "label"}
    node_allowed = node_required | {"fill", "stroke", "text_color", "font_size"}
    max_x = max_y = 0
    for index, raw in enumerate(root["nodes"]):
        context = f"nodes[{index}]"
        node = require_object(raw, context, node_allowed, node_required)
        node_id = identifier(node["id"], f"{context}.id")
        if node_id in ids:
            raise GraphError(f"Duplicate object ID: {node_id}")
        ids.add(node_id)
        node_ids.add(node_id)
        node_type = node["type"]
        if not isinstance(node_type, str) or node_type not in TYPE_MAP:
            raise GraphError(f"{context}.type must be rectangle, ellipse, diamond, or text")
        x = number(node["x"], f"{context}.x", maximum=MAX_PAGE_SIZE)
        y = number(node["y"], f"{context}.y", maximum=MAX_PAGE_SIZE)
        width = number(node["width"], f"{context}.width", positive=True, maximum=MAX_PAGE_SIZE)
        height = number(node["height"], f"{context}.height", positive=True, maximum=MAX_PAGE_SIZE)
        if x + width > MAX_PAGE_SIZE or y + height > MAX_PAGE_SIZE:
            raise GraphError(f"{context} bounds exceed 20000 by 20000 pixels")
        max_x, max_y = max(max_x, x + width), max(max_y, y + height)
        fill = color(node.get("fill", "#ffffff"), f"{context}.fill")
        stroke = color(node.get("stroke", "#000000"), f"{context}.stroke")
        ink = color(node.get("text_color", "#000000"), f"{context}.text_color")
        size = number(node.get("font_size", 14), f"{context}.font_size", positive=True)
        label = text(node["label"], f"{context}.label")
        item = {
            "id": node_id,
            "type": TYPE_MAP[node_type],
            "boundingBox": {"x": x, "y": y, "w": width, "h": height},
            "text": formatted_text(label, size, ink),
            "zIndex": 1,
        }
        if node_type == "text":
            if "fill" in node or "stroke" in node:
                raise GraphError(f"{context}: text nodes do not accept fill or stroke")
        else:
            item["style"] = {
                "fill": {"type": "color", "color": fill},
                "stroke": {"color": stroke, "width": 1, "style": "solid"},
                "textColor": ink,
            }
        shapes.append(item)
    lines = []
    edge_required = {"id", "source", "target"}
    edge_allowed = edge_required | {"label", "source_port", "target_port"}
    for index, raw in enumerate(root.get("edges", [])):
        context = f"edges[{index}]"
        edge = require_object(raw, context, edge_allowed, edge_required)
        edge_id = identifier(edge["id"], f"{context}.id")
        if edge_id in ids:
            raise GraphError(f"Duplicate object ID: {edge_id}")
        ids.add(edge_id)
        endpoints = []
        for key, default, style in (("source", {"x": 1, "y": .5}, "none"), ("target", {"x": 0, "y": .5}, "arrow")):
            shape_id = identifier(edge[key], f"{context}.{key}")
            if shape_id not in node_ids:
                raise GraphError(f"{context}.{key} references an unknown node: {shape_id}")
            port = position(edge.get(f"{key}_port", default), f"{context}.{key}_port")
            endpoints.append({"type": "shapeEndpoint", "style": style, "shapeId": shape_id, "position": port})
        item = {
            "id": edge_id,
            "lineType": "straight",
            "endpoint1": endpoints[0],
            "endpoint2": endpoints[1],
            "stroke": {"color": "#000000", "width": 1, "style": "solid"},
            "zIndex": 0,
        }
        if "label" in edge:
            item["text"] = [{"text": formatted_text(text(edge["label"], f"{context}.label")), "position": .5, "side": "top"}]
        lines.append(item)
    page_id = "page1"
    index = 1
    while page_id in ids:
        index += 1
        page_id = f"page{index}"
    return {
        "version": 1,
        "documentSettings": {"units": "px"},
        "pages": [{
            "id": page_id,
            "title": title,
            "settings": {"fillColor": "#ffffff", "size": {
                "type": "custom",
                "w": min(MAX_PAGE_SIZE, max(100, math.ceil(max_x) + 32)),
                "h": min(MAX_PAGE_SIZE, max(100, math.ceil(max_y) + 32)),
            }},
            "shapes": shapes,
            "lines": lines,
        }],
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
    args = parser.parse_args(argv)
    try:
        if args.output.suffix.lower() != ".lucid":
            raise GraphError("--output must have a .lucid extension")
        paths = [args.input.resolve(), args.output.resolve()]
        if args.document_json is not None:
            paths.append(args.document_json.resolve())
        if len(set(paths)) != len(paths):
            raise GraphError("Input and output paths must be distinct")
        graph = json.loads(args.input.read_text(encoding="utf-8-sig"), object_pairs_hook=unique_json_object, parse_constant=reject_nonfinite)
        document = build_document(graph)
        raw = document_bytes(document)
        package = package_bytes(raw)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_bytes(package)
        if args.document_json is not None:
            args.document_json.parent.mkdir(parents=True, exist_ok=True)
            args.document_json.write_bytes(raw)
        page = document["pages"][0]
        print(json.dumps({
            "package": str(args.output),
            "document_json": str(args.document_json) if args.document_json is not None else None,
            "shape_count": len(page["shapes"]),
            "connector_count": len(page["lines"]),
            "local_validation": "passed documented subset checks",
            "approximations": ["ellipse nodes use native circle shapes with the supplied rectangular bounds; verify rendered geometry in Lucid"] if any(node["type"] == "ellipse" for node in graph["nodes"]) else [],
            "live_import": "not executed",
        }, ensure_ascii=False))
        return 0
    except (GraphError, OSError, json.JSONDecodeError, UnicodeError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
