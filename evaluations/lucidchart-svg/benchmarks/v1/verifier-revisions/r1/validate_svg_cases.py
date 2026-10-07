#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Independent SVG benchmark oracle; no skill code is imported or executed.

Run: uv run --script validate_svg_cases.py CASE WORKSPACE --report REPORT.json
Notes require manual review. Prose keywords and self-reported fidelity are not scores.
"""

from __future__ import annotations

import argparse
from collections import Counter
import hashlib
from html.parser import HTMLParser
import json
import math
from pathlib import Path
import re
import sys
import xml.etree.ElementTree as ET
import zipfile


GEOMETRY_SVG = '''<svg xmlns="http://www.w3.org/2000/svg" id="dispatch-canvas" width="800" height="360" viewBox="10 20 400 360" preserveAspectRatio="none" data-title="Dispatch sketch">
  <g id="dispatch-stage" transform="translate(20 30) scale(1 2)">
    <g id="receive-group" data-node-id="receive">
      <rect id="receive-box" x="10" y="20" width="110" height="40" rx="4" fill="#EAF3FA" stroke="#25364A" stroke-width="1"/>
      <text id="receive-label" x="17" y="44" font-family="Georgia" font-size="11" font-weight="bold" fill="#17334D">Receive &amp; classify</text>
    </g>
    <g id="archive-group" data-node-id="archive" transform="matrix(1.5 0 0 1.5 170 65)">
      <rect id="archive-box" x="10" y="5" width="90" height="36" fill="#FFF0D6" stroke="#8B4A18" stroke-width="2" stroke-dasharray="6 2"/>
      <text id="archive-label" x="16" y="27" font-family="Verdana" font-size="10" font-style="italic" fill="#623211">Archive &lt;Q4&gt;</text>
    </g>
  </g>
</svg>
'''
RELATIONS_SVG = '''<svg xmlns="http://www.w3.org/2000/svg" id="release-canvas" width="720" height="300" viewBox="0 0 720 300" data-title="Release routing">
  <defs>
    <marker id="gold-head" markerWidth="8" markerHeight="8" refX="8" refY="4" orient="auto"><polygon points="0,0 8,4 0,8" fill="#946200"/></marker>
    <marker id="blue-head" markerWidth="10" markerHeight="6" refX="10" refY="3" orient="auto"><polygon points="0,0 10,3 0,6" fill="#264E8A"/></marker>
  </defs>
  <g id="intake-card" data-node-id="incoming"><rect x="30" y="30" width="120" height="60" fill="#FFF3D4" stroke="#5F4B20" stroke-width="2"/><text x="42" y="65" font-family="Arial" font-size="14" fill="#332A18">Receive batch</text></g>
  <g id="screen-card" data-node-id="qa"><circle cx="360" cy="180" r="45" fill="#E4F2E8" stroke="#24513A" stroke-width="2"/><text x="329" y="185" font-family="Arial" font-size="14" font-weight="bold" fill="#153A27">QA gate</text></g>
  <g id="release-card" data-node-id="outgoing"><rect x="540" y="30" width="120" height="60" rx="6" fill="#EAF0FC" stroke="#264E8A" stroke-width="2"/><text x="555" y="65" font-family="Arial" font-size="14" fill="#1B355E">Release &lt;R7&gt;</text></g>
  <polyline id="screen-route" data-edge-id="screen-flow" data-source="incoming" data-target="qa" points="150,60 225,60 225,180 315,180" fill="none" stroke="#946200" stroke-width="2" marker-end="url(#gold-head)"/>
  <text id="screen-caption" data-edge-id="screen-flow" x="235" y="120" font-family="Arial" font-size="12" fill="#6B4800">screened</text>
  <polyline id="release-route" data-edge-id="release-flow" data-source="qa" data-target="outgoing" points="405,180 480,180 480,60 540,60" fill="none" stroke="#264E8A" stroke-width="3" stroke-dasharray="5 3" marker-end="url(#blue-head)"/>
  <text id="release-caption" data-edge-id="release-flow" x="488" y="120" font-family="Arial" font-size="12" font-style="italic" fill="#1B355E">approved &amp; queued</text>
</svg>
'''
ASSET_SVG = '''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="480" height="240" viewBox="0 0 480 240" aria-labelledby="badge-title badge-desc">
  <title id="badge-title">Night-shift operations badge</title>
  <desc id="badge-desc">A dusk gradient panel with a clipped moon illustration and queue status.</desc>
  <defs>
    <linearGradient id="dusk" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#142943"/><stop offset="1" stop-color="#526795"/></linearGradient>
    <clipPath id="moon-window"><circle cx="390" cy="66" r="44"/></clipPath>
  </defs>
  <rect x="8" y="8" width="464" height="224" rx="20" fill="url(#dusk)"/>
  <g clip-path="url(#moon-window)"><rect x="342" y="18" width="96" height="96" fill="#F8DF9B"/><path d="M340 75 Q390 35 440 75 L440 120 L340 120 Z" fill="#DCA861"/><path d="M340 96 Q388 58 440 98 L440 124 L340 124 Z" fill="#8D6B6C"/></g>
  <path d="M30 166 C130 132 210 210 310 170" fill="none" stroke="#C5D9ED" stroke-width="3"/>
  <text x="30" y="64" font-family="Arial" font-size="25" font-weight="bold" fill="#FFFFFF">Night shift — queue 7</text>
  <text x="30" y="105" font-family="Arial" font-size="17" fill="#E8F0FF">Ready &amp; monitored</text>
  <text x="30" y="206" font-family="Arial" font-size="14" fill="#E8F0FF">Window: 22:00–06:00</text>
</svg>
'''


def node(identity, source_ref, kind, label, box, fill, stroke, width, dash,
         rounding, color, family, size, bold=False, italic=False):
    return dict(id=identity, source_ref=source_ref, type=kind, label=label, box=box,
                fill=fill, stroke=stroke, stroke_width=width, stroke_style=dash,
                rounding=rounding, text_color=color, font_family=family,
                font_size=size, bold=bold, italic=italic)


# Geometry is hand-derived: root R=(2,0,0,1,-20,-20); ordered group
# G=(1,0,0,2,20,30), so RG=(2,0,0,2,20,10). The archive child
# C=(1.5,0,0,1.5,170,65) yields RGC=(3,0,0,3,360,140).
# Thus receive=(40,50,220,80), archive=(390,155,270,108), font sizes
# 22/30, stroke widths 2/6, and receive rounding diameter 2*(4*2)=16.
CASES = {
    "geometry": dict(source="inputs/dispatch.svg", svg=GEOMETRY_SVG,
        base="outputs/dispatch", package="diagram.lucid", note="fidelity.md",
        title="Dispatch sketch", page=(800, 360), matrix=(2, 0, 0, 1, -20, -20),
        root_ref="dispatch-canvas", nodes=[
            node("receive", "receive-group", "rectangle", "Receive & classify", (40, 50, 220, 80),
                 "#EAF3FA", "#25364A", 2, "solid", 16, "#17334D", "Georgia", 22, bold=True),
            node("archive", "archive-group", "rectangle", "Archive <Q4>", (390, 155, 270, 108),
                 "#FFF0D6", "#8B4A18", 6, "dashed", 0, "#623211", "Verdana", 30, italic=True)], edges=[]),
    "relations": dict(source="source/release-route.svg", svg=RELATIONS_SVG,
        base="deliver/release", package="native.lucid", note="changes.md",
        title="Release routing", page=(720, 300), matrix=(1, 0, 0, 1, 0, 0),
        root_ref="release-canvas", nodes=[
            node("incoming", "intake-card", "rectangle", "Receive batch", (30, 30, 120, 60),
                 "#FFF3D4", "#5F4B20", 2, "solid", 0, "#332A18", "Arial", 14),
            node("qa", "screen-card", "circle", "QA gate", (315, 135, 90, 90),
                 "#E4F2E8", "#24513A", 2, "solid", 0, "#153A27", "Arial", 14, bold=True),
            node("outgoing", "release-card", "rectangle", "Release <R7>", (540, 30, 120, 60),
                 "#EAF0FC", "#264E8A", 2, "solid", 12, "#1B355E", "Arial", 14)], edges=[
            dict(id="screen-flow", source_ref="screen-route", source="incoming", target="qa", label="screened",
                 points=((150, 60), (225, 60), (225, 180), (315, 180)), stroke="#946200",
                 width=2, dash="solid", color="#6B4800", italic=False, marker_ref="gold-head"),
            dict(id="release-flow", source_ref="release-route", source="qa", target="outgoing", label="approved & queued",
                 points=((405, 180), (480, 180), (480, 60), (540, 60)), stroke="#264E8A",
                 width=3, dash="dashed", color="#1B355E", italic=True, marker_ref="blue-head")]),
    "asset": dict(source="source/night-shift.svg", svg=ASSET_SVG,
                  upload="ready/night-shift.svg", inspection="review/inspection.json", note="review/fidelity.md"),
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def numeric(value, expected):
    return type(value) in (int, float) and math.isfinite(value) and math.isclose(value, expected, rel_tol=0, abs_tol=1e-8)


def numbers(value, expected, keys):
    return isinstance(value, dict) and all(numeric(value.get(key), target) for key, target in zip(keys, expected))


def sequence(value, expected):
    return isinstance(value, (list, tuple)) and len(value) == len(expected) and all(numeric(a, b) for a, b in zip(value, expected))


def color(value, expected):
    return isinstance(value, str) and value.lower() == expected.lower()


def load(path):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            require(key not in result, f"Duplicate JSON key: {key}")
            result[key] = value
        return result
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique,
                      parse_constant=lambda value: (_ for _ in ()).throw(ValueError(f"Nonfinite JSON: {value}")))


class Text(HTMLParser):
    def __init__(self, value):
        super().__init__(convert_charrefs=True)
        self.parts, self.styles, self.tags = [], {}, set()
        self.feed(value)
        self.close()

    def handle_data(self, value):
        self.parts.append(value)

    def handle_starttag(self, tag, attrs):
        self.tags.add(tag.lower())
        if tag.lower() == "br":
            self.parts.append("\n")
        for key, value in attrs:
            if key == "style" and value:
                for declaration in value.split(";"):
                    if ":" in declaration:
                        name, content = declaration.split(":", 1)
                        self.styles[name.strip().lower()] = content.strip()


def text_check(value, label, expected):
    require(isinstance(value, str), "Native label is not HTML text")
    parsed = Text(value)
    require("".join(parsed.parts) == label, f"Literal label differs: {label}")
    require(color(parsed.styles.get("color"), expected["text_color"]), f"Text color differs: {label}")
    family = parsed.styles.get("font-family", "").strip("'\"")
    require(family == expected["font_family"], f"Font family differs: {label}")
    size = parsed.styles.get("font-size", "")
    require(size.endswith("px") and numeric(float(size[:-2]), expected["font_size"]), f"Font size differs: {label}")
    require(parsed.styles.get("text-align") == "left", f"Text alignment differs: {label}")
    bold = bool(parsed.tags & {"b", "strong"}) or parsed.styles.get("font-weight") in {"bold", "700", "800", "900"}
    italic = bool(parsed.tags & {"i", "em"}) or parsed.styles.get("font-style") == "italic"
    require(bold == expected["bold"], f"Bold formatting differs: {label}")
    require(italic == expected["italic"], f"Italic formatting differs: {label}")
    require(not (parsed.tags & {"u", "s", "strike", "del"}) and parsed.styles.get("text-decoration", "none") == "none", f"Unrequested text decoration: {label}")


def required_paths(spec):
    if "base" not in spec:
        return [spec[key] for key in ("source", "upload", "inspection", "note")]
    return [spec["source"], *[f'{spec["base"]}/{name}' for name in
            ("graph.json", "inspection.json", "mapping.json", spec["package"], "document.json", spec["note"])]]


def inspection_check(workspace, path, raw):
    root = ET.fromstring(raw)
    report = load(workspace / path)
    counts = dict(Counter(element.tag.removeprefix("{http://www.w3.org/2000/svg}") for element in root.iter()))
    labels = ["".join(element.itertext()).strip() for element in root.iter("{http://www.w3.org/2000/svg}text")]
    require(report.get("sha256") == hashlib.sha256(raw).hexdigest() and report.get("bytes") == len(raw), "Inspection is not tied to actual source bytes")
    require(report.get("valid_svg") is True and report.get("element_counts") == counts, "Inspection XML inventory differs")
    require(report.get("labels") == labels, "Inspection literal text inventory differs")
    require(numeric(report.get("width_px"), float(root.get("width"))) and numeric(report.get("height_px"), float(root.get("height"))), "Inspection viewport differs")
    require(sequence(report.get("view_box"), [float(v) for v in root.get("viewBox").split()]), "Inspection viewBox differs")
    for key in ("external_resources", "blocking_flags", "unresolved_fragment_references", "duplicate_ids"):
        require(report.get(key) == [], f"Unexpected inspection {key}")
    require(report.get("ready_for_upload") is True and report.get("safe_to_render_offline") is True, "Self-contained source was not identified as locally eligible")
    require(report.get("embedded_raster_resource_count") == 0, "Unexpected embedded raster count")
    return report


def route_check(value, expected, label):
    require(isinstance(value, list) and len(value) == len(expected), f"{label}: route-point count differs")
    require(all(numbers(point, target, ("x", "y")) for point, target in zip(value, expected)), f"{label}: interior route turns differ")


def organizing_check(document, page, graph, visible_ids):
    """Allow coherent nonvisual grouping without adding geometry or dataset layouts."""
    for root in (document, page, graph):
        require(not any(root.get(key) for key in ("dataBackedShapes", "collections", "orgCharts", "mindMaps", "umlSequenceDiagrams")), "Undeclared generated layouts or collections were introduced")
    sets = []
    for root, native in ((page, True), (graph, False)):
        records, parents, layer_ids = {}, {}, set()
        for kind in ("groups", "layers"):
            values = root.get(kind, [])
            require(isinstance(values, list), f"{kind} must be an array")
            z_key = "zIndex" if native else "z_index"
            layer_key = "layerIndex" if native else "layer_index"
            allowed = {"id", "items", z_key} if kind == "groups" else {"id", "items", "title", layer_key}
            for value in values:
                require(isinstance(value, dict) and set(value) <= allowed and {"id", "items"} <= set(value), "Organizing metadata contains unsupported or visible fields")
                identity = value["id"]
                require(isinstance(identity, str) and re.fullmatch(r"[A-Za-z0-9_.~-]{1,36}", identity) and identity not in records and identity not in visible_ids and identity != page.get("id"), "Organizing identity is invalid or duplicated")
                members = value["items"]
                require(isinstance(members, list) and all(isinstance(item, str) for item in members) and len(members) == len(set(members)), "Organizing membership is invalid or duplicated")
                normalized = {"kind": kind, "items": frozenset(members)}
                if kind == "layers":
                    require(isinstance(value.get("title"), str), "Layer title is not text")
                    normalized["title"] = value["title"]
                    layer_ids.add(identity)
                for field in (z_key, layer_key):
                    if field in value:
                        require(type(value[field]) in (int, float) and math.isfinite(value[field]) and value[field] == int(value[field]), "Organizing order must be a finite integer")
                        normalized["z_index" if field == z_key else "layer_index"] = value[field]
                records[identity] = normalized
        for identity, record in records.items():
            for member in record["items"]:
                require(member in visible_ids | records.keys() and member not in layer_ids, "Organizing membership has a dangling or ineligible reference")
                require(member not in parents, "Organizing membership has multiple direct parents")
                parents[member] = identity
        completed = set()
        for member in parents:
            visited, current = set(), member
            while current in parents and current not in completed:
                require(current not in visited, "Organizing membership contains a cycle")
                visited.add(current)
                current = parents[current]
            completed.update(visited)
        sets.append(records)
    require(sets[0] == sets[1], "Graph and native organizing memberships disagree")
    return set(sets[0])


def native_check(workspace, spec):
    base = workspace / spec["base"]
    raw_document = (base / "document.json").read_bytes()
    with zipfile.ZipFile(base / spec["package"]) as archive:
        require(archive.namelist() == ["document.json"], "Package is not a native document-only ZIP")
        require(archive.read("document.json") == raw_document, "ZIP document and separate JSON differ byte-for-byte")
    document, graph, mapping = (load(base / name) for name in ("document.json", "graph.json", "mapping.json"))
    require(document.get("version") == 1 and len(document.get("pages", [])) == 1, "Expected one version-1 page")
    require(document.get("documentSettings", {}).get("units") == "px", "Native document units differ from viewport pixels")
    page = document["pages"][0]
    require(page.get("title") == graph.get("title") == spec["title"], "Source page title differs")
    require(numbers(page.get("settings", {}).get("size"), spec["page"], ("w", "h")), "Native page size differs")
    settings = page.get("settings", {})
    require(settings.get("size", {}).get("type") == "custom" and settings.get("infiniteCanvas") is False and settings.get("autoTiling") is False, "Native finite viewport settings differ")
    require(numbers(graph, spec["page"], ("page_width", "page_height")), "Graph viewport differs")
    shapes, lines = page.get("shapes", []), page.get("lines", [])
    require(len(shapes) == len(spec["nodes"]) and len(lines) == len(spec["edges"]), "Native object counts differ")
    require(len(graph.get("nodes", [])) == len(shapes) and len(graph.get("edges", [])) == len(lines), "Graph object counts differ")
    ids = [item.get("id") for item in [page, *shapes, *lines]]
    require(all(isinstance(value, str) and re.fullmatch(r"[A-Za-z0-9_.~-]{1,36}", value) for value in ids) and len(ids) == len(set(ids)), "Native object identities are invalid or duplicated")
    organizing_ids = organizing_check(document, page, graph, set(ids) - {page["id"]})
    identities = mapping.get("source_to_native_ids", {})
    expected_ids = {item["id"] for item in [*spec["nodes"], *spec["edges"]]}
    require(expected_ids <= set(identities) and len(set(identities.values())) == len(identities), "Source-to-native identity mapping is incomplete or duplicated")
    source_ids = {element.get("id") for element in ET.fromstring(spec["svg"]).iter() if element.get("id")}
    require(all(source in source_ids and identities[source] in organizing_ids for source in set(identities) - expected_ids), "Additional source attribution is not tied to valid organizing metadata")
    native_nodes, graph_nodes = ({item["id"]: item for item in items} for items in (shapes, graph["nodes"]))
    native_edges, graph_edges = ({item["id"]: item for item in items} for items in (lines, graph.get("edges", [])))
    require(set(native_nodes) == set(graph_nodes) == {identities[n["id"]] for n in spec["nodes"]}, "Node IDs disagree across artifacts")
    require(set(native_edges) == set(graph_edges) == {identities[e["id"]] for e in spec["edges"]}, "Edge IDs disagree across artifacts")
    ledger = mapping.get("ledger", [])
    for expected in spec["nodes"]:
        identity, label = identities[expected["id"]], expected["label"]
        emitted, recovered = native_nodes[identity], graph_nodes[identity]
        require(emitted.get("type") == recovered.get("type") == expected["type"], f"{label}: shape type differs")
        require(numbers(emitted.get("boundingBox"), expected["box"], ("x", "y", "w", "h")), f"{label}: actual native geometry differs")
        require(numbers(recovered, expected["box"], ("x", "y", "width", "height")), f"{label}: graph geometry differs")
        require(numeric(emitted.get("boundingBox", {}).get("rotation", 0), 0) and numeric(recovered.get("rotation", 0), 0), f"{label}: unrequested rotation")
        require(numeric(emitted.get("opacity", 100), 100) and numeric(recovered.get("opacity", 100), 100), f"{label}: object opacity differs")
        require(recovered.get("label") == label, f"{label}: graph literal label differs")
        style = emitted.get("style", {})
        require(color(style.get("fill", {}).get("color"), expected["fill"]) and color(recovered.get("fill"), expected["fill"]), f"{label}: fill differs")
        stroke = style.get("stroke", {})
        require(color(stroke.get("color"), expected["stroke"]) and numeric(stroke.get("width"), expected["stroke_width"]) and stroke.get("style") == expected["stroke_style"], f"{label}: actual border differs")
        require(color(recovered.get("stroke"), expected["stroke"]) and numeric(recovered.get("stroke_width"), expected["stroke_width"]) and recovered.get("stroke_style") == expected["stroke_style"], f"{label}: graph border differs")
        require(numeric(style.get("rounding", 0), expected["rounding"]) and numeric(recovered.get("rounding", 0), expected["rounding"]), f"{label}: rounded corners differ")
        text_check(emitted.get("text"), label, expected)
        require(color(style.get("textColor"), expected["text_color"]), f"{label}: shape text color differs")
        for field in ("text_color", "font_family", "font_size", "bold", "italic"):
            observed, target = recovered.get(field), expected[field]
            require(numeric(observed, target) if field == "font_size" else color(observed, target) if field == "text_color" else observed == target, f"{label}: graph {field} differs")
        require(recovered.get("underline", False) is False and recovered.get("strike", False) is False, f"{label}: graph text decoration differs")
        require(any(entry.get("source_ref") == expected["source_ref"] and entry.get("feature") == "node" and entry.get("source_id") == expected["id"] and entry.get("native_id") == identity for entry in ledger), f"{label}: source attribution missing")
    for expected in spec["edges"]:
        identity = identities[expected["id"]]
        emitted, recovered = native_edges[identity], graph_edges[identity]
        for index, key in enumerate(("source", "target")):
            attached = emitted.get(f"endpoint{index + 1}", {})
            target, port, marker = identities[expected[key]], (1, .5) if index == 0 else (0, .5), "none" if index == 0 else "arrow"
            require(attached.get("type") == "shapeEndpoint" and attached.get("shapeId") == target and numbers(attached.get("position"), port, ("x", "y")) and attached.get("style") == marker, f"{identity}: actual topology, port, or marker differs")
            value = recovered.get(key)
            graph_target = value.get("shapeId") if isinstance(value, dict) else value
            graph_port = value.get("position") if isinstance(value, dict) else recovered.get(f"{key}_port")
            require(graph_target == target and numbers(graph_port, port, ("x", "y")) and recovered.get(f"{key}_marker") == marker, f"{identity}: graph attachment differs")
        for item, type_key, straight_key, elbow_key in ((emitted, "lineType", "joints", "elbowControlPoints"), (recovered, "line_type", "joints", "elbow_points")):
            kind = item.get(type_key)
            require(kind in {"straight", "elbow"}, f"{identity}: route type changed")
            route_check(item.get(straight_key if kind == "straight" else elbow_key), expected["points"][1:-1], identity)
        stroke = emitted.get("stroke", {})
        require(color(stroke.get("color"), expected["stroke"]) and numeric(stroke.get("width"), expected["width"]) and stroke.get("style") == expected["dash"], f"{identity}: actual connector paint differs")
        require(color(recovered.get("stroke"), expected["stroke"]) and numeric(recovered.get("stroke_width"), expected["width"]) and recovered.get("stroke_style") == expected["dash"], f"{identity}: graph connector paint differs")
        labels = emitted.get("text", [])
        require(len(labels) == 1 and recovered.get("label") == expected["label"], f"{identity}: edge label differs")
        label_style = dict(text_color=expected["color"], font_family="Arial", font_size=12, bold=False, italic=expected["italic"])
        text_check(labels[0].get("text"), expected["label"], label_style)
        position = labels[0].get("position")
        require(type(position) in (int, float) and math.isfinite(position) and 0 <= position <= 1 and labels[0].get("side") in {"top", "middle", "bottom"}, f"{identity}: native label position is invalid")
        # Exact SVG x/y placement has no direct native equivalent; the reviewer
        # judges declared placement changes rather than enforcing one adapter.
        require(any(entry.get("source_ref") == expected["source_ref"] and entry.get("feature") == "edge" and entry.get("source_id") == expected["id"] and entry.get("native_id") == identity for entry in ledger), f"{identity}: source edge attribution missing")
        require(any(entry.get("source_ref") == expected["marker_ref"] and entry.get("feature") == "marker" and entry.get("action") == "adapted" for entry in ledger), f"{identity}: source marker adaptation missing")
    require(mapping.get("coordinates") == "viewport-pixels", "Mapping coordinate policy differs")
    require(any(entry.get("source_ref") == spec["root_ref"] and entry.get("feature") == "coordinates" and sequence(entry.get("root_matrix"), spec["matrix"]) for entry in ledger), "Coordinate attribution/matrix differs")


def validate(case, workspace):
    spec = CASES[case]
    paths = required_paths(spec)
    for relative in paths:
        path = workspace / relative
        require(path.is_file() and not path.is_symlink() and path.resolve().is_relative_to(workspace) and path.stat().st_size > 0, f"Required artifact missing, redirected, or empty: {relative}")
    raw = (workspace / spec["source"]).read_bytes()
    require(raw == spec["svg"].encode("utf-8"), "Source bytes differ from the supplied UTF-8/LF fixture")
    inspection = spec.get("inspection", f'{spec.get("base", "")}/inspection.json')
    report = inspection_check(workspace, inspection, raw)
    checks = ["Exact UTF-8/LF source bytes", "Inspection tied to actual XML/resource inventory"]
    if case == "asset":
        require((workspace / spec["upload"]).read_bytes() == raw, "Visual asset is not byte-preserving")
        features = report.get("feature_counts", {})
        require(features.get("linearGradient") == 1 and features.get("clipPath") == 1 and features.get("clipping") == 1 and features.get("paint-server-reference") == 1, "Rich artwork inventory is incomplete")
        for path in workspace.rglob("*"):
            if not path.is_file() or "skills" in path.relative_to(workspace).parts:
                continue
            require(path.suffix.lower() != ".lucid", "Fabricated native package in visual-asset case")
            if path.suffix.lower() == ".json":
                value = load(path)
                require(not isinstance(value, dict) or not ({"nodes", "pages"} & value.keys()), "Fabricated graph/document in visual-asset case")
        checks.extend(["Byte-identical visual asset retains gradient, clip path and Unicode labels", "No fabricated editable graph/document/package"])
        note = spec["note"]
    else:
        native_check(workspace, spec)
        checks.extend(["ZIP document and separate JSON byte identity", "Hand-derived native and graph geometry/styles/text",
                       "Explicit source attribution, topology, route turns and arrow adaptations"])
        note = f'{spec["base"]}/{spec["note"]}'
    return dict(case=case, workspace=str(workspace), artifact_checks_passed=True, checks=checks,
                artifacts={relative: hashlib.sha256((workspace / relative).read_bytes()).hexdigest() for relative in paths},
                manual_status_review_required=True, status_note=note,
                manual_review=["Judge the note against concrete source/output details and declared changes; no prose keyword score.",
                               "Check visual-inspection evidence or an accurate explanation of unavailable rendering.",
                               "Require honest local versus live-import boundaries and relevant editability/fidelity limitations."],
                status_note_text=(workspace / note).read_text(encoding="utf-8"))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("case", choices=CASES)
    parser.add_argument("workspace", type=Path)
    parser.add_argument("--report", required=True, type=Path)
    args = parser.parse_args()
    if args.report.resolve().is_relative_to(args.workspace.resolve()):
        parser.error("Write evaluator reports outside the evaluated workspace")
    try:
        result = validate(args.case, args.workspace.resolve())
        code = 0
    except (OSError, ValueError, KeyError, TypeError, AttributeError, IndexError, ET.ParseError, zipfile.BadZipFile) as error:
        result = dict(case=args.case, workspace=str(args.workspace.resolve()), artifact_checks_passed=False, error=str(error))
        code = 1
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({key: value for key, value in result.items() if key != "status_note_text"}, indent=2, ensure_ascii=True))
    return code


if __name__ == "__main__":
    sys.exit(main())
