#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Independent public-development artifact checks; no skill code is imported.

Run: uv run --script validate_native_cases.py CASE WORKSPACE --report PATH
CASE is contract, semantic, or generated. Notes require direct human review.
The oracles below are frozen literals from the three benchmark task inputs.
"""

from __future__ import annotations

import argparse
import hashlib
from html.parser import HTMLParser
import json
import math
from pathlib import Path
import re
import sys
import zipfile


OUTPUTS = {
    "contract": ["input/contract.json", "out/contract/diagram.lucid", "out/contract/document.json", "out/contract/native-report.json", "out/contract/notes.md"],
    "semantic": ["out/semantic/graph.json", "out/semantic/diagram.lucid", "out/semantic/document.json", "out/semantic/native-report.json", "out/semantic/notes.md"],
    "generated": ["out/generated/layout.json", "out/generated/diagram.lucid", "out/generated/document.json", "out/generated/layout-report.json", "out/generated/notes.md"],
}

# The digest concerns parsed literal input, never a compiler self-report.
CONTRACT_INPUT_DIGEST = "eb71dfc87bfcafbe927120c5b1ed783e5e082fceaed13fee74604d09895e776b"
CONTRACT_BOXES = {
    "handoff-lanes": (20, 20, 860, 260), "scan": (70, 105, 180, 70),
    "register": (460, 80, 320, 160), "caption": (950, 90, 180, 80),
}
SEMANTIC_BOXES = {
    "intake": (50, 90, 60, 60), "review": (200, 80, 180, 80),
    "outcome": (480, 90, 100, 100), "publish": (700, 40, 180, 80),
    "repeat": (700, 230, 180, 80), "closed": (1050, 100, 60, 60),
    "batch": (120, 500, 300, 180), "measurement": (720, 500, 320, 180),
}
SEMANTIC_LABELS = {
    "intake": "Sample received", "review": "Review <assay> & sign", "outcome": "Result acceptable?",
    "publish": "Publish certificate", "repeat": "Repeat measurement", "closed": "Review closed", "batch": "", "measurement": "",
}
BPMN_FLOWS = {
    "arrive-review": ("intake", "review", ""), "review-outcome": ("review", "outcome", ""),
    "acceptable": ("outcome", "publish", "pass"), "unacceptable": ("outcome", "repeat", "rework"),
    "publish-close": ("publish", "closed", ""), "repeat-close": ("repeat", "closed", ""),
}
STAFF = [
    {"person_id": "o-north", "reports_to": "", "display_name": "Nora & operations", "job_title": "North director", "office": "North", "fte": 1.0},
    {"person_id": "o-triage", "reports_to": "o-north", "display_name": "Mina <triage>", "job_title": "Coordinator", "office": "North", "fte": 0.8},
    {"person_id": "o-courier", "reports_to": "o-triage", "display_name": "Jules", "job_title": "Courier", "office": "North", "fte": 0.6},
    {"person_id": "o-south", "reports_to": None, "display_name": "Theo", "job_title": "South director", "office": "South", "fte": 1.0},
    {"person_id": "o-route", "reports_to": "o-south", "display_name": "Rae", "job_title": "Route planner", "office": "South", "fte": 0.9},
    {"person_id": "o-store", "reports_to": "o-south", "display_name": "Emery", "job_title": "Stores lead", "office": "South", "fte": 1.0},
]
TOPICS = [
    {"topic_id": "m-delivery", "parent_topic": None, "caption": "Delivery <R2>", "priority": 1},
    {"topic_id": "m-intake", "parent_topic": "m-delivery", "caption": "Intake & evidence", "priority": 2},
    {"topic_id": "m-proof", "parent_topic": "m-intake", "caption": "Proof of custody", "priority": 3},
    {"topic_id": "m-pack", "parent_topic": "m-intake", "caption": "Packing", "priority": 3},
    {"topic_id": "m-dispatch", "parent_topic": "m-delivery", "caption": "Dispatch", "priority": 2},
    {"topic_id": "m-route", "parent_topic": "m-dispatch", "caption": "Route checks", "priority": 3},
    {"topic_id": "m-confirm", "parent_topic": "m-dispatch", "caption": "Arrival confirmed", "priority": 3},
]
SEQUENCE = "\n".join([
    "@startuml", "participant Analyst", "participant Registry", "participant Queue",
    "Analyst -> Registry : submit <lot>", "Registry -> Queue : enqueue & audit", "alt accepted",
    "Queue --> Registry : receipt", "Registry --> Analyst : confirmed", "else declined",
    "Queue --> Registry : reason", "Registry --> Analyst : revise", "end", "@enduml",
])
GENERATED_BOXES = {"inspect-card": (1100, 650, 180, 70), "release-card": (1420, 650, 180, 70), "archive-card": (1800, 650, 180, 70)}
GENERATED_LABELS = {"inspect-card": "Inspect <lot>", "release-card": "Release & record", "archive-card": "Reference archive"}
LAYOUTS = [
    {"id": "org-panel", "type": "orgChart", "position": {"x": 40, "y": 100}, "collectionId": "staff-roster", "idField": "person_id", "foreignKeyField": "reports_to", "nameField": "display_name", "roleField": "job_title", "extraFields": ["office", "fte"]},
    {"id": "topics-panel", "type": "mindMap", "position": {"x": 40, "y": 900}, "collectionId": "delivery-topics", "idField": "topic_id", "parentIdField": "parent_topic", "textField": "caption"},
    {"id": "sequence-panel", "type": "umlSequence", "position": {"x": 1100, "y": 100}, "markup": SEQUENCE},
    {"id": "cards-reflow", "type": "assistedLayout", "shapeIds": ["inspect-card", "release-card"]},
]


def same(actual: object, expected: object) -> bool:
    """JSON scalar types matter; finite int/float values are both JSON numbers."""
    if isinstance(expected, bool):
        return type(actual) is bool and actual == expected
    if isinstance(expected, (int, float)):
        return type(actual) in (int, float) and math.isfinite(actual) and actual == expected
    if isinstance(expected, dict):
        return isinstance(actual, dict) and actual.keys() == expected.keys() and all(same(actual[k], v) for k, v in expected.items())
    if isinstance(expected, list):
        return isinstance(actual, list) and len(actual) == len(expected) and all(same(a, e) for a, e in zip(actual, expected))
    if isinstance(expected, str) and re.fullmatch(r"#[0-9A-Fa-f]{6}", expected):
        return isinstance(actual, str) and actual.lower() == expected.lower()
    return type(actual) is type(expected) and actual == expected


def unique_object(pairs: list[tuple]) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"Duplicate JSON key: {key}")
        result[key] = value
    return result


def load_json(raw: bytes) -> object:
    def reject(value: str) -> None:
        raise ValueError(f"Non-finite JSON token: {value}")
    return json.loads(raw.decode("utf-8-sig"), object_pairs_hook=unique_object, parse_constant=reject)


class Text(HTMLParser):
    """Decode emitted literal text and inspect its actual formatting declarations."""
    def __init__(self, value: object):
        super().__init__(convert_charrefs=True)
        self.parts, self.css, self.tags, self.invalid = [], {}, set(), []
        if not isinstance(value, str):
            self.invalid.append("text is not a string")
        else:
            self.feed(value)
            self.close()

    def handle_starttag(self, tag: str, attrs: list[tuple]) -> None:
        if tag not in {"p", "br", "b", "i", "u", "s", "span"}:
            self.invalid.append(f"Unexpected text element {tag}")
        self.tags.add(tag)
        if tag == "br":
            self.parts.append("\n")
        for key, value in attrs:
            if key != "style" or not isinstance(value, str):
                self.invalid.append(f"Unexpected text attribute {key}")
            else:
                for declaration in value.split(";"):
                    if ":" in declaration:
                        name, content = declaration.split(":", 1)
                        self.css[name.strip().lower()] = content.strip()

    def handle_startendtag(self, tag: str, attrs: list[tuple]) -> None:
        self.handle_starttag(tag, attrs)

    def handle_data(self, data: str) -> None:
        self.parts.append(data)

    @property
    def literal(self) -> str:
        return "".join(self.parts)


class Oracle:
    def __init__(self, case: str, workspace: Path):
        self.case, self.workspace = case, workspace.resolve()
        self.errors, self.check_count, self.artifacts = [], 0, []

    def check(self, condition: bool, message: str) -> None:
        self.check_count += 1
        if not condition:
            self.errors.append(message)

    def eq(self, actual: object, expected: object, message: str) -> None:
        self.check(same(actual, expected), message)

    def file(self, relative: str) -> bytes:
        path = self.workspace / relative
        if not path.resolve().is_relative_to(self.workspace) or not path.is_file():
            raise ValueError(f"Required workspace file is missing or escapes workspace: {relative}")
        raw = path.read_bytes()
        if not raw:
            raise ValueError(f"Required file is empty: {relative}")
        self.artifacts.append({"path": relative, "bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()})
        return raw

    def objects(self, value: object, expected: set[str], context: str) -> dict:
        self.check(isinstance(value, list), f"{context} must be an array")
        items = value if isinstance(value, list) else []
        self.check(all(isinstance(item, dict) and isinstance(item.get("id"), str) for item in items), f"{context} contains an invalid object ID")
        result = {item["id"]: item for item in items if isinstance(item, dict) and isinstance(item.get("id"), str)}
        self.check(len(result) == len(items), f"{context} contains duplicate IDs")
        self.eq(set(result), expected, f"{context} IDs/count differ from supplied objects")
        return result

    def text(self, raw: object, literal: str, context: str, css: dict | None = None, tags: set | None = None) -> None:
        parsed = Text(raw)
        self.check(not parsed.invalid, f"{context} contains unsupported or unescaped text markup")
        self.eq(parsed.literal, literal, f"{context} literal text changed")
        for key, value in (css or {}).items():
            actual = parsed.css.get(key, "").strip("'\"")
            self.check(actual.lower() == value.lower(), f"{context} {key} declaration changed")
        for tag in tags or set():
            self.check(tag in parsed.tags, f"{context} lost {tag} formatting")

    def bounds(self, shape: dict, bounds: tuple, context: str, rotation: int | None = None) -> None:
        expected = dict(zip(("x", "y", "w", "h"), bounds))
        if rotation is not None:
            expected["rotation"] = rotation
        self.eq(shape.get("boundingBox"), expected, f"{context} fixed bounds/rotation changed")

    def style(self, shape: dict, fill: str, stroke: str, width: int, color: str, context: str, dash: str = "solid", rounding: int | None = None) -> None:
        style = shape.get("style", {})
        self.eq(style.get("fill"), {"type": "color", "color": fill}, f"{context} fill changed")
        self.eq(style.get("stroke"), {"color": stroke, "width": width, "style": dash}, f"{context} outline changed")
        self.eq(style.get("textColor"), color, f"{context} text color changed")
        if rounding is not None:
            self.eq(style.get("rounding"), rounding, f"{context} rounding changed")

    def plain(self, shape: dict, context: str) -> None:
        self.eq(shape.get("opacity", 100), 100, f"{context} gained transparency")
        self.eq(shape.get("style", {}).get("rounding", 0), 0, f"{context} gained rounded corners")
        self.check(not (Text(shape.get("text", "")).tags & {"b", "i", "u", "s"}), f"{context} gained text decoration")

    def table(self, shape: dict, header: str, rows: list[tuple], context: str) -> None:
        self.eq(shape.get("type"), "table", f"{context} must be an editable table")
        self.eq(shape.get("rowCount"), len(rows) + 1, f"{context} row count changed")
        self.eq(shape.get("colCount"), len(rows[0]), f"{context} column count changed")
        cells = shape.get("cells", [])
        expected = {(0, 0): (header, len(rows[0]) - 1)}
        expected.update({(x, y): (text, 0) for y, row in enumerate(rows, 1) for x, text in enumerate(row)})
        actual = {(cell.get("xPosition"), cell.get("yPosition")): cell for cell in cells if isinstance(cell, dict)}
        self.check(len(actual) == len(cells) == len(expected), f"{context} duplicate/extra/missing cells")
        self.eq(set(actual), set(expected), f"{context} field grid/order changed")
        for position, (literal, merge) in expected.items():
            cell = actual.get(position, {})
            self.text(cell.get("text"), literal, f"{context} cell {position}")
            self.eq(cell.get("mergeCellsRight", 0), merge, f"{context} cell {position} horizontal merge changed")
            self.eq(cell.get("mergeCellsDown", 0), 0, f"{context} cell {position} gained a vertical merge")

    def attached(self, line: dict, source: str, target: str, context: str, source_marker: str = "none", target_marker: str = "arrow") -> None:
        for field, node, marker in (("endpoint1", source, source_marker), ("endpoint2", target, target_marker)):
            endpoint = line.get(field, {})
            self.eq(endpoint.get("type"), "shapeEndpoint", f"{context} lost an attached endpoint")
            self.eq(endpoint.get("shapeId"), node, f"{context} endpoint direction/topology changed")
            self.eq(endpoint.get("style"), marker, f"{context} endpoint marker changed")
            if "position" in endpoint:
                pos = endpoint["position"]
                self.check(isinstance(pos, dict) and set(pos) == {"x", "y"} and all(type(v) in (int, float) and math.isfinite(v) and 0 <= v <= 1 for v in pos.values()), f"{context} invalid normalized port")

    def label(self, line: dict, literal: str, context: str) -> None:
        labels = [label for label in line.get("text", []) if Text(label.get("text")).literal]
        self.eq(len(labels), 1 if literal else 0, f"{context} line-label count changed")
        if literal and labels:
            self.text(labels[0].get("text"), literal, f"{context} line label")

    def editing_organization(self, page: dict, shapes: dict, lines: dict) -> None:
        """Allow harmless groups/layers while checking their actual object references."""
        groups = {item["id"]: item for item in page.get("groups", [])}
        ordinary = set(shapes) | set(lines)
        valid_items = ordinary | set(groups)
        group_parents, layer_parents = {}, {}
        for field, parents, allowed in (("groups", group_parents, {"id", "items", "zIndex"}), ("layers", layer_parents, {"id", "title", "items", "layerIndex"})):
            for item in page.get(field, []):
                self.check(set(item) <= allowed, f"{field} gained unsupported semantic fields")
                members = item.get("items", [])
                self.check(isinstance(members, list) and all(isinstance(x, str) for x in members), f"{field} membership must contain object IDs")
                if not isinstance(members, list) or not all(isinstance(x, str) for x in members):
                    continue
                self.check(len(set(members)) == len(members) and set(members) <= valid_items, f"{field} membership duplicates or invents an object")
                for member in members:
                    self.check(member not in parents, f"{field} gives an object multiple direct parents")
                    parents[member] = item["id"]
                if field == "layers":
                    self.check(isinstance(item.get("title"), str), "Layer title must be a literal string")
        for identity in groups:
            visited, current = set(), identity
            while current in group_parents:
                if current in visited:
                    self.check(False, "Editing groups contain a membership cycle")
                    break
                visited.add(current)
                current = group_parents[current]

    def package(self) -> tuple[dict, dict, object]:
        raw = {path: self.file(path) for path in OUTPUTS[self.case]}
        prefix = f"out/{self.case}/"
        path = self.workspace / f"{prefix}diagram.lucid"
        with zipfile.ZipFile(path) as archive:
            self.eq(archive.namelist(), ["document.json"], "Resource-free ZIP must contain only root document.json")
            info = archive.getinfo("document.json")
            if info.file_size > 2_000_000:
                raise ValueError("Packaged document JSON exceeds two million bytes")
            if archive.testzip() is not None:
                raise ValueError("ZIP CRC validation failed")
            document = load_json(archive.read(info))
        self.eq(document, load_json(raw[f"{prefix}document.json"]), "Separate document JSON differs from ZIP document")
        if not isinstance(document, dict):
            raise ValueError("Packaged document must be an object")
        self.eq(document.get("version"), 1, "Standard Import version must be one")
        self.eq(document.get("documentSettings", {}).get("units"), "px", "Document units must be pixels")
        pages = document.get("pages", [])
        if not isinstance(pages, list) or len(pages) != 1 or not isinstance(pages[0], dict):
            raise ValueError("Package must contain exactly one page")
        page = pages[0]
        ids = [page.get("id")]
        for field in ("shapes", "lines", "groups", "layers", "dataBackedShapes"):
            items = page.get(field, [])
            self.check(isinstance(items, list), f"Page {field} must be an array")
            ids += [item.get("id") for item in items if isinstance(item, dict)] if isinstance(items, list) else []
        ids += [item.get("id") for item in document.get("collections", []) if isinstance(item, dict)]
        self.check(all(isinstance(value, str) and value for value in ids) and len(set(ids)) == len(ids), "Document object IDs must be nonblank and globally unique")
        report_name = "layout-report.json" if self.case == "generated" else "native-report.json"
        report = load_json(raw[prefix + report_name])
        self.check(isinstance(report, dict) and bool(report), "Preparation report must be a nonempty JSON object")
        self.check(bool(raw[prefix + "notes.md"].decode("utf-8-sig").strip()), "English notes must be nonblank and await direct review")
        input_path = "input/contract.json" if self.case == "contract" else prefix + ("layout.json" if self.case == "generated" else "graph.json")
        return document, page, load_json(raw[input_path])

    def page(self, page: dict, title: str, color: str, size: tuple | None) -> None:
        self.eq(page.get("title"), title, "Page title changed")
        expected = {"fillColor": color, "infiniteCanvas": size is None}
        if size is not None:
            expected.update(size={"type": "custom", "w": size[0], "h": size[1]}, autoTiling=False)
        self.eq(page.get("settings"), expected, "Finite page/tiling/background or infinite-canvas settings changed")

    def graph_consistency(self, graph: object, shapes: dict, lines: dict) -> None:
        if not isinstance(graph, dict):
            self.check(False, "Preparation graph must be a JSON object")
            return
        nodes = self.objects(graph.get("nodes"), set(shapes), "Preparation graph nodes")
        edges = self.objects(graph.get("edges", []), set(lines), "Preparation graph edges")
        for identity, node in nodes.items():
            shape = shapes.get(identity, {})
            self.eq(node.get("type"), shape.get("type"), f"Graph/package type mismatch: {identity}")
            self.eq([node.get(k) for k in ("x", "y", "width", "height")], [shape.get("boundingBox", {}).get(k) for k in ("x", "y", "w", "h")], f"Graph/package bounds mismatch: {identity}")
            self.text(shape.get("text", ""), node.get("label"), f"Graph/package label: {identity}")
            style = shape.get("style", {})
            for source_key, emitted in (("fill", style.get("fill", {}).get("color")), ("stroke", style.get("stroke", {}).get("color")), ("stroke_width", style.get("stroke", {}).get("width")), ("stroke_style", style.get("stroke", {}).get("style")), ("text_color", style.get("textColor")), ("rounding", style.get("rounding")), ("opacity", shape.get("opacity")), ("z_index", shape.get("zIndex"))):
                if source_key in node:
                    self.eq(emitted, node[source_key], f"Graph/package {source_key} mismatch: {identity}")
            css = {target: f"{node[key]}px" if key == "font_size" else node[key] for key, target in (("font_size", "font-size"), ("font_family", "font-family"), ("text_color", "color"), ("text_align", "text-align"), ("vertical_align", "vertical-align")) if key in node}
            self.text(shape.get("text", ""), node.get("label"), f"Graph/package text style: {identity}", css)
            for source_key, tag in (("bold", "b"), ("italic", "i"), ("underline", "u"), ("strike", "s")):
                if source_key in node:
                    self.eq(tag in Text(shape.get("text", "")).tags, node[source_key], f"Graph/package {source_key} mismatch: {identity}")
            for key, value in node.get("properties", {}).items():
                if key not in {"cells", "lanes"}:
                    self.eq(shape.get(key), value, f"Graph/package native property {key} mismatch: {identity}")
        for identity, edge in edges.items():
            line = lines.get(identity, {})
            for raw_key, emitted_key in (("source", "endpoint1"), ("target", "endpoint2")):
                value = edge.get(raw_key)
                shape_id = value if isinstance(value, str) else value.get("shapeId") if isinstance(value, dict) else None
                if shape_id is not None:
                    self.eq(shape_id, line.get(emitted_key, {}).get("shapeId"), f"Graph/package attachment mismatch: {identity}")
                endpoint = line.get(emitted_key, {})
                self.eq(endpoint.get("style"), edge.get(f"{raw_key}_marker", "none" if raw_key == "source" else "arrow"), f"Graph/package marker mismatch: {identity}")
                if isinstance(value, dict):
                    for key, item in value.items():
                        self.eq(endpoint.get(key), item, f"Graph/package explicit endpoint {key} mismatch: {identity}")
                if f"{raw_key}_port" in edge:
                    self.eq(endpoint.get("position"), edge[f"{raw_key}_port"], f"Graph/package port mismatch: {identity}")
            for source_key, native_key, default in (("line_type", "lineType", "straight"), ("z_index", "zIndex", 0)):
                self.eq(line.get(native_key), edge.get(source_key, default), f"Graph/package {source_key} mismatch: {identity}")
            for key, default in (("stroke", "#000000"), ("stroke_width", 1), ("stroke_style", "solid")):
                native_key = {"stroke": "color", "stroke_width": "width", "stroke_style": "style"}[key]
                self.eq(line.get("stroke", {}).get(native_key), edge.get(key, default), f"Graph/package connector {key} mismatch: {identity}")
            for source_key, emitted_key in (("joints", "joints"), ("elbow_points", "elbowControlPoints")):
                self.eq(line.get(emitted_key, []), edge.get(source_key, []), f"Graph/package route mismatch: {identity}")
            if "labels" in edge:
                labels = edge["labels"]
            elif "label" in edge:
                labels = [{"text": edge["label"], "position": edge.get("label_position", 0.5), "side": edge.get("label_side", "top")}]
            else:
                labels = []
            labels = [label for label in labels if label.get("text")]
            native_labels = [label for label in line.get("text", []) if Text(label.get("text")).literal]
            self.eq(len(native_labels), len(labels), f"Graph/package annotation count mismatch: {identity}")
            for raw_label, native_label in zip(labels, native_labels):
                self.text(native_label.get("text"), raw_label.get("text"), f"Graph/package annotation: {identity}")
                self.eq([native_label.get("position"), native_label.get("side")], [raw_label.get("position", 0.5), raw_label.get("side", "top")], f"Graph/package annotation placement mismatch: {identity}")

    def contract(self, document: dict, page: dict, source: object) -> None:
        digest = hashlib.sha256(json.dumps(source, sort_keys=True, ensure_ascii=False, separators=(",", ":"), allow_nan=False).encode()).hexdigest()
        self.eq(digest, CONTRACT_INPUT_DIGEST, "Saved command-contract input differs from frozen supplied values")
        self.page(page, "Inventory handoff <Q4>", "#F8FAFC", (1200, 600))
        self.eq(document.get("collections", []), [], "Contract gained data collections")
        self.eq(page.get("dataBackedShapes", []), [], "Fixed contract gained generated layouts")
        shapes = self.objects(page.get("shapes"), set(CONTRACT_BOXES), "Contract shapes")
        lines = self.objects(page.get("lines"), {"register-link", "callout-link"}, "Contract lines")
        for identity, bounds in CONTRACT_BOXES.items():
            self.bounds(shapes.get(identity, {}), bounds, identity, 5 if identity == "caption" else None)
        lanes, scan, register, caption = (shapes.get(k, {}) for k in CONTRACT_BOXES)
        self.eq(lanes.get("type"), "swimLanes", "Container type changed")
        self.text(lanes.get("text"), "Stock & custody", "Container label")
        self.eq(lanes.get("vertical"), True, "Lane orientation changed")
        self.eq(lanes.get("titleBar"), {"height": 28, "verticalText": False}, "Lane title bar changed")
        expected_lanes = [("Receiving <dock>", 360, "#DBEAFE", "#EFF6FF"), ("Control & archive", 500, "#E2E8F0", "#F8FAFC")]
        actual_lanes = lanes.get("lanes", [])
        self.eq(len(actual_lanes), 2, "Lane count changed")
        for actual, (title, width, header, fill) in zip(actual_lanes, expected_lanes):
            self.text(actual.get("title"), title, "Lane literal title")
            self.eq([actual.get(k) for k in ("width", "headerFill", "laneFill")], [width, header, fill], "Lane widths/colors/order changed")
        self.eq(lanes.get("magnetize"), False, "Lane magnetization choice changed")
        self.eq(lanes.get("zIndex"), -1, "Container stack changed")
        self.style(lanes, "#FFFFFF", "#334155", 2, "#000000", "Container")
        self.eq(scan.get("type"), "predefinedProcess", "Subprocess type changed")
        self.eq(scan.get("sideWidth"), 0.12, "Subprocess side width changed")
        self.style(scan, "#E0F2FE", "#075985", 3, "#0C4A6E", "Scan", "dashed", 8)
        self.eq([scan.get("opacity"), scan.get("zIndex")], [85, 2], "Scan opacity/stack changed")
        self.text(scan.get("text"), "Scan <batch> & seal", "Scan label", {"font-family": "Arial", "font-size": "18px", "color": "#0C4A6E", "text-align": "left", "vertical-align": "center"}, {"b", "i"})
        self.table(register, "Register <literal> & bins", [("batch_id PK", "text", "required"), ("bin <slot>", "integer", "0..99")], "Register")
        self.style(register, "#FFFFFF", "#475569", 2, "#000000", "Register")
        self.eq(register.get("userSpecifiedRows"), [{"index": 0, "size": 40}, {"index": 1, "size": 60}, {"index": 2, "size": 60}], "Table row dimensions changed")
        self.eq(register.get("userSpecifiedCols"), [{"index": 0, "size": 140}, {"index": 1, "size": 100}, {"index": 2, "size": 80}], "Table column dimensions changed")
        self.eq([register.get("verticalBorder"), register.get("horizontalBorder")], [True, False], "Table border settings changed")
        header_cell = next((c for c in register.get("cells", []) if c.get("xPosition") == c.get("yPosition") == 0), {})
        self.eq(header_cell.get("style"), {"fill": {"type": "color", "color": "#CBD5E1"}}, "Table header fill changed")
        self.eq(caption.get("type"), "rectangle", "Caption type changed")
        self.style(caption, "#FEF3C7", "#92400E", 1, "#000000", "Caption")
        self.text(caption.get("text"), "Local package only", "Caption label", {"font-size": "15px"}, {"u"})
        relation = lines.get("register-link", {})
        self.attached(relation, "scan", "register", "Register relationship", "exactlyOne", "zeroOrMore")
        self.eq(relation.get("endpoint1", {}).get("position"), {"x": 1, "y": 0.5}, "Source port changed")
        self.eq(relation.get("endpoint2", {}).get("position"), {"x": 0, "y": 0.5}, "Target port changed")
        self.eq(relation.get("lineType"), "elbow", "Elbow routing changed")
        self.eq(relation.get("elbowControlPoints"), [{"x": 350, "y": 140}, {"x": 350, "y": 160}], "Elbow control points changed")
        self.eq(relation.get("stroke"), {"color": "#334155", "width": 2, "style": "dotted"}, "Relationship stroke changed")
        self.eq(relation.get("zIndex"), 3, "Relationship stack changed")
        labels = relation.get("text", [])
        self.eq(len(labels), 3, "Multi-label count changed")
        for label, (literal, position, side, color, size, tag) in zip(labels, [("1", 0.08, "top", "#075985", 12, "b"), ("records & bins", 0.52, "middle", "#000000", 13, "i"), ("0..*", 0.92, "bottom", "#000000", 12, "u")]):
            self.eq([label.get("position"), label.get("side")], [position, side], "Multi-label position/side changed")
            self.text(label.get("text"), literal, "Multi-label", {"font-size": f"{size}px", "color": color}, {tag})
        callout = lines.get("callout-link", {})
        self.eq(callout.get("endpoint1"), {"type": "shapeEndpoint", "style": "none", "shapeId": "caption", "position": {"x": 0, "y": 1}}, "Callout attachment changed")
        self.eq(callout.get("endpoint2"), {"type": "positionEndpoint", "style": "openArrow", "position": {"x": 900, "y": 360}}, "Absolute callout endpoint changed")
        self.eq(callout.get("joints"), [{"x": 920, "y": 300}], "Callout interior point changed")
        self.eq(callout.get("lineType"), "straight", "Callout routing changed")
        self.eq(callout.get("stroke"), {"color": "#92400E", "width": 1, "style": "solid"}, "Callout stroke changed")
        self.label(callout, "unverified <render>", "Callout")
        if callout.get("text"):
            label = callout["text"][0]
            self.eq([label.get("position"), label.get("side")], [0.7, "bottom"], "Callout label placement changed")
            self.text(label.get("text"), "unverified <render>", "Callout label style", {"font-size": "11px", "color": "#92400E"})
        self.eq(page.get("groups"), [{"id": "scan-register", "items": ["scan", "register", "register-link"], "zIndex": 4}], "Group membership/stack changed")
        self.eq(page.get("layers"), [{"id": "handoff", "title": "Custody & records", "items": ["handoff-lanes", "scan-register"], "layerIndex": 0}, {"id": "annotation", "title": "Review notes", "items": ["caption", "callout-link"], "layerIndex": 1}], "Layer membership/order/title changed")
        self.graph_consistency(source, shapes, lines)

    def semantic(self, document: dict, page: dict, graph: object) -> None:
        self.page(page, "Laboratory review & records", "#FFFFFF", (1300, 800))
        self.eq(document.get("collections", []), [], "Fixed semantic view gained data collections")
        self.eq(page.get("dataBackedShapes", []), [], "Fixed semantic view gained reflow layouts")
        shapes = self.objects(page.get("shapes"), set(SEMANTIC_BOXES), "Semantic shapes")
        lines = self.objects(page.get("lines"), set(BPMN_FLOWS) | {"batch-measurement"}, "Semantic lines")
        self.editing_organization(page, shapes, lines)
        for identity, bounds in SEMANTIC_BOXES.items():
            shape = shapes.get(identity, {})
            self.bounds(shape, bounds, identity)
            self.style(shape, "#FFFFFF", "#334155", 2, "#0F172A", identity)
            self.text(shape.get("text"), SEMANTIC_LABELS[identity], identity, {"font-family": "Arial", "font-size": "14px", "color": "#0F172A"})
            self.plain(shape, identity)
        for identity, group in (("intake", "start"), ("closed", "end")):
            event = shapes.get(identity, {})
            self.eq(event.get("type"), "bpmnEvent", f"{identity} lost its formal event role")
            self.eq(event.get("eventGroup"), group, f"{identity} event group changed")
            self.eq(event.get("eventType", "none"), "none", f"{identity} gained an event trigger")
            self.eq([event.get("nonInterrupting", False), event.get("throwing", False)], [False, False], f"{identity} gained unsupported event modifiers")
        for identity, task_type in (("review", "user"), ("publish", "service"), ("repeat", "manual")):
            task = shapes.get(identity, {})
            self.eq([task.get("type"), task.get("activityType"), task.get("taskType")], ["bpmnActivity", "task", task_type], f"{identity} formal task role/subtype changed")
            self.eq([task.get("activityMarker1", "none"), task.get("activityMarker2", "none")], ["none", "none"], f"{identity} gained an activity marker")
        gateway = shapes.get("outcome", {})
        self.eq([gateway.get("type"), gateway.get("gatewayType")], ["bpmnGateway", "exclusive"], "Exclusive branch semantics changed")
        for identity, (source, target, label) in BPMN_FLOWS.items():
            line = lines.get(identity, {})
            self.attached(line, source, target, identity)
            self.label(line, label, identity)
            self.eq(line.get("stroke"), {"color": "#334155", "width": 2, "style": "solid"}, f"{identity} sequence-flow stroke changed")
            for annotation in line.get("text", []):
                if Text(annotation.get("text")).literal:
                    self.text(annotation.get("text"), label, f"{identity} label style", {"font-family": "Arial", "font-size": "14px", "color": "#0F172A"})
        self.table(shapes.get("batch", {}), "Batch <lab>", [("batch_id PK", "uuid"), ("collected_at", "timestamp"), ("lot_code", "text")], "Batch entity")
        self.table(shapes.get("measurement", {}), "Measurement & result", [("measurement_id PK", "uuid"), ("batch_id FK", "uuid"), ("value", "decimal")], "Measurement entity")
        relation = lines.get("batch-measurement", {})
        self.eq(relation.get("stroke"), {"color": "#334155", "width": 2, "style": "solid"}, "ER relationship stroke changed")
        endpoints = [relation.get("endpoint1", {}), relation.get("endpoint2", {})]
        self.eq({p.get("shapeId") for p in endpoints}, {"batch", "measurement"}, "ER endpoint topology changed")
        for endpoint in endpoints:
            self.eq(endpoint.get("type"), "shapeEndpoint", "ER cardinality must attach to an entity")
            self.eq(endpoint.get("style"), {"batch": "exactlyOne", "measurement": "zeroOrMore"}.get(endpoint.get("shapeId")), "ER cardinality is wrong at its respective entity")
        labels = relation.get("text", [])
        self.eq(len(labels), 2, "ER must display both multiplicity labels")
        seen = set()
        for label in labels:
            literal = Text(label.get("text")).literal
            seen.add(literal)
            node = {"1": "batch", "0..*": "measurement"}.get(literal)
            position = label.get("position")
            source_node = endpoints[0].get("shapeId")
            self.check(node is not None and type(position) in (int, float) and math.isfinite(position) and (0 <= position <= 0.25 if node == source_node else 0.75 <= position <= 1), "ER multiplicity label is not near its respective entity")
            self.text(label.get("text"), literal, "ER multiplicity", {"font-family": "Arial", "font-size": "14px", "color": "#0F172A"})
        self.eq(seen, {"1", "0..*"}, "ER literal multiplicities changed")
        self.graph_consistency(graph, shapes, lines)

    def generated(self, document: dict, page: dict, source: object) -> None:
        self.page(page, "Delivery planning <R2>", "#F1F5F9", None)
        collections = self.objects(document.get("collections"), {"staff-roster", "delivery-topics"}, "Collections")
        for identity, rows in (("staff-roster", STAFF), ("delivery-topics", TOPICS)):
            self.eq(collections.get(identity), {"id": identity, "values": rows}, f"{identity} literal records/row order/scalar types changed")
        layouts = self.objects(page.get("dataBackedShapes"), {x["id"] for x in LAYOUTS}, "Generated layouts")
        for expected in LAYOUTS:
            actual = layouts.get(expected["id"], {})
            if expected["type"] == "assistedLayout":
                self.eq(set(actual), {"id", "type", "shapeIds"}, "Assisted layout gained undeclared fields")
                self.eq(actual.get("type"), "assistedLayout", "Assisted layout family changed")
                self.eq(set(actual.get("shapeIds", [])), {"inspect-card", "release-card"}, "Assisted selection changed or included archive")
                self.eq(len(actual.get("shapeIds", [])), 2, "Assisted selection duplicates an ID")
            else:
                self.eq(actual, expected, f"{expected['id']} family/origin/field mapping/markup changed")
        shapes = self.objects(page.get("shapes"), set(GENERATED_BOXES), "Generated native cards")
        lines = self.objects(page.get("lines"), {"eligible-link"}, "Generated native connectors")
        self.editing_organization(page, shapes, lines)
        for identity, bounds in GENERATED_BOXES.items():
            shape = shapes.get(identity, {})
            self.eq(shape.get("type"), "rectangle", f"{identity} lost its generic rectangle")
            self.bounds(shape, bounds, identity)
            self.style(shape, "#FFFFFF", "#475569", 1, "#0F172A", identity)
            self.text(shape.get("text"), GENERATED_LABELS[identity], identity, {"font-family": "Arial", "font-size": "14px", "color": "#0F172A"})
            self.plain(shape, identity)
        link = lines.get("eligible-link", {})
        self.attached(link, "inspect-card", "release-card", "Eligible connector")
        self.label(link, "eligible", "Eligible connector")
        self.eq(link.get("stroke"), {"color": "#475569", "width": 1, "style": "solid"}, "Eligible connector stroke changed")
        if not isinstance(source, dict):
            self.check(False, "Generated preparation input must be an object")
        else:
            source_collections = self.objects(source.get("collections"), set(collections), "Preparation collections")
            self.eq(source_collections, collections, "Preparation/package collection data differ")
            source_layouts = self.objects(source.get("layouts"), set(layouts), "Preparation layouts")
            self.eq(source_layouts, layouts, "Preparation/package layout definitions differ")
            self.graph_consistency(source.get("graph"), shapes, lines)
        # Counts are calculated from the frozen records, not report totals.
        self.eq({r["person_id"] for r in STAFF if r["reports_to"] in (None, "")}, {"o-north", "o-south"}, "Organization forest oracle error")
        self.eq(sum(r["reports_to"] not in (None, "") for r in STAFF), 4, "Organization relationship oracle error")
        self.eq(sum(r["parent_topic"] is not None for r in TOPICS), 6, "Mind-map relationship oracle error")

    def run(self) -> dict:
        try:
            document, page, source = self.package()
            getattr(self, self.case)(document, page, source)
        except (OSError, ValueError, TypeError, KeyError, AttributeError, zipfile.BadZipFile, OverflowError) as error:
            self.errors.append(f"Invalid or unreadable artifact: {error}")
        return {"schema_version": 1, "case": self.case, "scope": "Independent local artifact checks; public development benchmark",
                "passed": not self.errors, "check_count": self.check_count, "violations": self.errors, "artifacts": self.artifacts,
                "manual_review_required": True,
                "manual_review": ["Judge factual English notes, route/editability claims, material adaptations and local-versus-live limits directly.",
                                  "Package structure cannot establish live parser acceptance, typography, clipping, generated geometry or rendered fidelity."],
                "live_actions_required": False}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("case", choices=sorted(OUTPUTS))
    parser.add_argument("workspace", type=Path)
    parser.add_argument("--report", required=True, type=Path)
    args = parser.parse_args()
    if args.report.resolve().is_relative_to(args.workspace.resolve()):
        print("Error: evaluator report must be outside the evaluated workspace", file=sys.stderr)
        return 2
    result = Oracle(args.case, args.workspace).run()
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps({"case": args.case, "passed": result["passed"], "checks": result["check_count"], "violation_count": len(result["violations"]), "manual_review_required": True, "report": str(args.report)}))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
