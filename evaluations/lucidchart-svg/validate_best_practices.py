#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Independent artifact oracles for three prompt-defined Lucidchart cases.

This evaluator imports no skill code. It does not infer geometry from candidate
reports, execute candidate scripts, repair artifacts, or score narrative phrases.
The narrative and any live-render claims require a separate human review.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import sys
import zipfile
from html.parser import HTMLParser
from pathlib import Path
from typing import Any


SOURCE_SVG = ('<svg xmlns="http://www.w3.org/2000/svg" width="300" height="200" '
    'viewBox="0 0 100 100" data-title="Audit"><defs><marker id="head" '
    'orient="auto" markerWidth="3" markerHeight="3" refX="3" refY="1.5">'
    '<polygon points="0,0 3,1.5 0,3" fill="#333333"/></marker></defs>'
    '<g transform="translate(5 0)"><g data-node-id="request"><rect x="0" '
    'y="10" width="20" height="30" fill="#ffffff" stroke="#333333" '
    'stroke-width="0.5"/><text x="10" y="25" text-anchor="middle" '
    'font-family="Arial" font-size="5" fill="#111111">A &amp; B</text></g>'
    '<g data-node-id="audit"><rect x="60" y="10" width="20" height="30" '
    'rx="2" ry="2" fill="#eeeeee" stroke="#333333" stroke-width="0.5" '
    'stroke-dasharray="2 1"/><text x="70" y="25" text-anchor="middle" '
    'font-family="Arial" font-size="5" fill="#111111">Audit</text></g>'
    '<path id="e" data-source="request" data-target="audit" d="M20 25 L60 25" '
    'fill="none" stroke="#333333" stroke-width="0.5" marker-end="url(#head)"/>'
    '<text data-edge-id="e" x="40" y="20" text-anchor="middle" '
    'font-family="Arial" font-size="5" fill="#111111">yes</text></g></svg>\n').encode()

# These values come from the evaluation prompts, not from skill implementation.
CONTRACT = {
    "title": "Rich native contract", "page_width": 1000, "page_height": 400,
    "page_fill": "#FFFFFF", "auto_tiling": False,
    "nodes": [
        {"id": "work", "type": "bpmnActivity", "x": 20, "y": 20,
         "width": 150, "height": 80, "label": "Review <P1> & accept",
         "fill": "#EEEEEE", "stroke": "#333333", "stroke_width": 2,
         "stroke_style": "dashed", "opacity": 80, "font_family": "Arial",
         "font_size": 16, "bold": True, "text_align": "left",
         "properties": {"activityType": "task", "taskType": "user"}},
        {"id": "entity", "type": "table", "x": 350, "y": 20,
         "width": 220, "height": 120, "label": "",
         "properties": {"rowCount": 2, "colCount": 2, "cells": [
             {"xPosition": 0, "yPosition": 0, "mergeCellsRight": 1,
              "text": "Invoice <literal>"},
             {"xPosition": 0, "yPosition": 1, "text": "id PK"},
             {"xPosition": 1, "yPosition": 1, "text": "integer"}]}},
        {"id": "compute", "type": "namedShape", "x": 700, "y": 20,
         "width": 80, "height": 80, "label": "Compute",
         "properties": {"className": "ArchAmazonEC2AWS2024"}},
    ],
    "edges": [{"id": "rel", "source": "work", "target": "entity",
               "source_port": {"x": 1, "y": 0.5},
               "target_port": {"x": 0, "y": 0.5}, "line_type": "elbow",
               "elbow_points": [{"x": 260, "y": 60}, {"x": 260, "y": 80}],
               "stroke": "#111111", "stroke_width": 2,
               "source_marker": "one", "target_marker": "zeroOrMore",
               "labels": [
                   {"text": "1", "position": 0.1, "side": "top",
                    "color": "#111111", "font_size": 12},
                   {"text": "0..*", "position": 0.9, "side": "bottom",
                    "color": "#111111", "font_size": 12}]}],
    "groups": [{"id": "pair", "items": ["work", "entity", "rel"], "z_index": 2}],
    "layers": [{"id": "semantic", "title": "Diagram",
                "items": ["pair", "compute"], "layer_index": 0}],
}

GENERATED = {
    "graph": {"title": "Generated families", "infinite_canvas": True,
              "nodes": [{"id": "note", "type": "rectangle", "x": 10, "y": 10,
                         "width": 100, "height": 50, "label": "Reference"}]},
    "collections": [{"id": "people", "values": [
        {"id": "ada", "parent": "", "name": "Ada & team", "role": "Director"},
        {"id": "lin", "parent": "ada", "name": "Lin <P1>", "role": "Engineer"},
        {"id": "kai", "parent": "ada", "name": "Kai", "role": "Analyst"}]}],
    "layouts": [
        {"id": "organization", "type": "orgChart", "position": {"x": 150, "y": 150},
         "collectionId": "people", "idField": "id", "foreignKeyField": "parent",
         "nameField": "name", "roleField": "role"},
        {"id": "topics", "type": "mindMap", "position": {"x": 150, "y": 650},
         "collectionId": "people", "idField": "id", "parentIdField": "parent",
         "textField": "name"},
        {"id": "sequence", "type": "umlSequence", "position": {"x": 900, "y": 150},
         "markup": "@startuml\nUser -> API : Request\nAPI --> User : Result\n@enduml"},
        {"id": "arrange", "type": "assistedLayout", "shapeIds": ["note"]},
    ],
}


class ValidationError(ValueError):
    """A candidate artifact violates the independent fixture contract."""


def require(condition: Any, message: str) -> None:
    if not condition:
        raise ValidationError(message)


def strict_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        require(key not in result, f"Duplicate JSON key: {key}")
        result[key] = value
    return result


def reject_constant(value: str) -> None:
    raise ValidationError(f"Non-finite JSON constant: {value}")


def load_json_bytes(data: bytes) -> Any:
    return json.loads(data.decode("utf-8-sig"), object_pairs_hook=strict_pairs,
                      parse_constant=reject_constant)


def same(actual: Any, expected: Any, label: str) -> None:
    # Avoid Python's bool/int equality when comparing JSON oracle values.
    if isinstance(expected, bool) or expected is None:
        require(actual is expected, f"{label}: expected {expected!r}, got {actual!r}")
    elif isinstance(expected, (int, float)):
        require(type(actual) in (int, float), f"{label}: expected a number")
        try:
            close = math.isfinite(actual) and math.isclose(actual, expected, abs_tol=1e-8)
        except OverflowError:
            close = False
        require(close, f"{label}: expected {expected!r}, got {actual!r}")
    elif isinstance(expected, dict):
        require(isinstance(actual, dict) and set(actual) == set(expected),
                f"{label}: dictionary keys differ from the oracle")
        for key, value in expected.items():
            same(actual[key], value, f"{label}.{key}")
    elif isinstance(expected, list):
        require(isinstance(actual, list) and len(actual) == len(expected),
                f"{label}: list length differs from the oracle")
        for index, value in enumerate(expected):
            same(actual[index], value, f"{label}[{index}]")
    else:
        require(type(actual) is type(expected) and actual == expected,
                f"{label}: expected {expected!r}, got {actual!r}")


def subset(actual: dict[str, Any], expected: dict[str, Any], label: str) -> None:
    require(isinstance(actual, dict), f"{label}: expected an object")
    for key, value in expected.items():
        require(key in actual, f"{label}: missing {key}")
        same(actual[key], value, f"{label}.{key}")


def color(actual: Any, expected: str, label: str) -> None:
    require(isinstance(actual, str) and actual.lower() == expected.lower(),
            f"{label}: expected {expected}")


class TextOracle(HTMLParser):
    def __init__(self, text: str):
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self.styles: dict[str, str] = {}
        self.tags: set[str] = set()
        self.feed(text)
        self.close()

    def handle_data(self, data: str) -> None:
        self.parts.append(data)

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.tags.add(tag)
        if tag == "br":
            self.parts.append("\n")
        for key, value in attrs:
            if key == "style" and value:
                for declaration in value.split(";"):
                    if ":" in declaration:
                        name, content = declaration.split(":", 1)
                        self.styles[name.strip().lower()] = content.strip()


def text(actual: Any, literal: str, label: str, *, family: str | None = None,
         size: float | None = None, ink: str | None = None,
         align: str | None = None, bold: bool | None = None) -> TextOracle:
    require(isinstance(actual, str), f"{label}: expected native text string")
    oracle = TextOracle(actual)
    same("".join(oracle.parts), literal, f"{label}.literal")
    require(oracle.tags <= {"p", "span", "br", "b", "strong", "i", "em", "u", "s", "strike"},
            f"{label}: literal content became unexpected HTML tags")
    if family is not None:
        require(oracle.styles.get("font-family", "").strip("\"'") == family,
                f"{label}: source font family was not retained")
    if size is not None:
        value = oracle.styles.get("font-size", "")
        require(re.fullmatch(r"(?:\d+(?:\.\d*)?|\.\d+)px", value) is not None,
                f"{label}: font size must be explicit pixels")
        same(float(value[:-2]), size, f"{label}.font_size")
    if ink is not None:
        color(oracle.styles.get("color"), ink, f"{label}.color")
    if align is not None:
        same(oracle.styles.get("text-align"), align, f"{label}.text_align")
    if bold is not None:
        css_bold = oracle.styles.get("font-weight") in {"bold", "700"}
        same(bool(oracle.tags & {"b", "strong"}) or css_bold, bold, f"{label}.bold")
    return oracle


def indexed(items: Any, expected_ids: set[str], label: str) -> dict[str, dict[str, Any]]:
    require(isinstance(items, list), f"{label}: expected array")
    require(all(isinstance(item, dict) and isinstance(item.get("id"), str) for item in items),
            f"{label}: every item requires a string id")
    result = {item["id"]: item for item in items}
    require(len(result) == len(items), f"{label}: duplicate ids")
    require(set(result) == expected_ids, f"{label}: unexpected or missing objects")
    return result


class Evaluator:
    def __init__(self, kind: str, workspace: Path, smoke: bool):
        self.kind = kind
        self.workspace = workspace.resolve()
        self.smoke = smoke
        self.checks: list[str] = []

    def path(self, relative: str) -> Path:
        path = (self.workspace / relative).resolve()
        require(path.is_relative_to(self.workspace), f"Artifact escapes workspace: {relative}")
        require(path.is_file(), f"Missing required artifact: {relative}")
        require(path.stat().st_size <= 10_000_000, f"Artifact exceeds evaluator bound: {relative}")
        return path

    def read_json(self, relative: str) -> Any:
        return load_json_bytes(self.path(relative).read_bytes())

    def check_package(self) -> tuple[dict[str, Any], dict[str, Any]]:
        data = self.path("out/document.json").read_bytes()
        with zipfile.ZipFile(self.path("out/diagram.lucid")) as archive:
            require(archive.namelist() == ["document.json"],
                    "Package must contain exactly one root document.json")
            require(archive.getinfo("document.json").file_size <= 2_000_000,
                    "Packaged document exceeds Standard Import document bound")
            require(archive.testzip() is None, "Package CRC validation failed")
            require(archive.read("document.json") == data,
                    "Packaged document.json differs from the separate output bytes")
        document = load_json_bytes(data)
        subset(document, {"version": 1, "documentSettings": {"units": "px"}}, "document")
        require(isinstance(document.get("pages"), list) and len(document["pages"]) == 1,
                "Fixture must produce exactly one page")
        page = document["pages"][0]
        require(isinstance(page.get("id"), str), "Page id is missing")
        ids = [page["id"]]
        for category in ("shapes", "lines", "groups", "layers", "dataBackedShapes"):
            objects = page.get(category, [])
            require(isinstance(objects, list), f"Page {category} is not an array")
            for obj in objects:
                require(isinstance(obj, dict) and isinstance(obj.get("id"), str),
                        f"Page {category} has an invalid object id")
                ids.append(obj["id"])
        for collection in document.get("collections", []):
            require(isinstance(collection, dict) and isinstance(collection.get("id"), str),
                    "Collection id is missing")
            ids.append(collection["id"])
        require(len(ids) == len(set(ids)), "Document ids are not globally unique")
        require(all(re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]*", item) for item in ids),
                "Document contains an invalid id")
        self.checks.append("Archive integrity, unique ids, units and exact JSON byte equality")
        return document, page

    def native_report(self, report: Any, graph: dict[str, Any], page: dict[str, Any]) -> None:
        require(isinstance(report, dict), "Native report is not an object")
        same(report.get("report_version"), 1, "native_report.report_version")
        shapes = {obj["id"]: obj for obj in page.get("shapes", [])}
        lines = {obj["id"]: obj for obj in page.get("lines", [])}
        decisions = indexed(report.get("decisions"), set(shapes) | set(lines), "report.decisions")
        inputs = {obj["id"]: obj for obj in graph.get("nodes", []) + graph.get("edges", [])}
        for object_id, decision in decisions.items():
            is_shape = object_id in shapes
            same(decision.get("kind"), "shape" if is_shape else "line", f"decision.{object_id}.kind")
            same(decision.get("emitted"), (shapes if is_shape else lines)[object_id],
                 f"decision.{object_id}.emitted")
            fields = decision.get("explicit_fields")
            require(isinstance(fields, list) and len(fields) == len(set(fields))
                    and all(isinstance(field, str) for field in fields),
                    f"decision.{object_id}: explicit field inventory is invalid")
            same(set(fields), set(inputs[object_id]), f"decision.{object_id}.explicit_fields")
            if is_shape:
                same(decision.get("source_type"), inputs[object_id]["type"],
                     f"decision.{object_id}.source_type")
                same(decision.get("native_type"), shapes[object_id]["type"],
                     f"decision.{object_id}.native_type")
        same(report.get("page_settings"), page.get("settings"), "report.page_settings")
        same(report.get("groups"), page.get("groups", []), "report.groups")
        same(report.get("layers"), page.get("layers", []), "report.layers")
        require(isinstance(report.get("requires_live_check"), list),
                "Native report lacks structured live-check inventory")
        for field in ("local_validation", "live_import", "rendered_fidelity"):
            require(isinstance(report.get(field), str) and report[field].strip(),
                    f"Native report lacks {field} disclosure")
        self.checks.append("Structured native decisions match emitted objects and explicit input fields")

    def naturalistic(self, document: dict[str, Any], page: dict[str, Any]) -> None:
        same(self.path("input/source.svg").read_bytes(), SOURCE_SVG, "original SVG bytes")
        digest = hashlib.sha256(SOURCE_SVG).hexdigest()
        inspection = self.read_json("out/inspection.json")
        subset(inspection, {"sha256": digest, "bytes": len(SOURCE_SVG), "valid_svg": True,
                           "view_box": [0, 0, 100, 100], "width_px": 300, "height_px": 200,
                           "labels": ["A & B", "Audit", "yes"],
                           "duplicate_ids": [], "unresolved_fragment_references": [],
                           "external_resources": []}, "inspection")
        subset(inspection.get("element_counts", {}),
               {"svg": 1, "g": 3, "rect": 2, "text": 3, "path": 1,
                "defs": 1, "marker": 1, "polygon": 1}, "inspection.element_counts")
        graph = self.read_json("out/graph.json")
        subset(graph, {"title": "Audit", "page_width": 300, "page_height": 200}, "graph")
        nodes = indexed(graph.get("nodes"), {"request", "audit"}, "graph.nodes")
        shapes = indexed(page.get("shapes"), {"request", "audit"}, "page.shapes")
        settings = page.get("settings", {})
        subset(settings, {"size": {"type": "custom", "w": 300, "h": 200},
                          "infiniteCanvas": False, "autoTiling": False}, "page.settings")
        same(page.get("title"), "Audit", "page.title")
        for object_id, x, label, fill, dash, rounding in (
            ("request", 60, "A & B", "#ffffff", "solid", 0),
            ("audit", 180, "Audit", "#eeeeee", "dashed", 8),
        ):
            subset(nodes[object_id], {"id": object_id, "type": "rectangle", "x": x,
                   "y": 20, "width": 40, "height": 60, "label": label,
                   "font_family": "Arial", "font_size": 10, "stroke_width": 1,
                   "stroke_style": dash, "rounding": rounding}, f"graph.node.{object_id}")
            color(nodes[object_id].get("fill"), fill, f"graph.{object_id}.fill")
            color(nodes[object_id].get("stroke"), "#333333", f"graph.{object_id}.stroke")
            color(nodes[object_id].get("text_color"), "#111111", f"graph.{object_id}.text")
            shape = shapes[object_id]
            subset(shape, {"type": "rectangle", "boundingBox": {"x": x, "y": 20, "w": 40, "h": 60}}, object_id)
            style = shape.get("style", {})
            subset(style.get("stroke", {}), {"width": 1, "style": dash}, f"{object_id}.stroke")
            color(style.get("stroke", {}).get("color"), "#333333", f"{object_id}.stroke.color")
            same(style.get("rounding"), rounding, f"{object_id}.rounding")
            subset(style.get("fill", {}), {"type": "color"}, f"{object_id}.fill")
            color(style.get("fill", {}).get("color"), fill, f"{object_id}.fill.color")
            text(shape.get("text"), label, object_id, family="Arial", size=10,
                 ink="#111111", align="center")
        edges = indexed(graph.get("edges"), {"e"}, "graph.edges")
        subset(edges["e"], {"source": "request", "target": "audit",
               "source_port": {"x": 1, "y": 0.5}, "target_port": {"x": 0, "y": 0.5},
               "line_type": "straight", "source_marker": "none", "target_marker": "arrow",
               "stroke_width": 1, "stroke_style": "solid", "label": "yes",
               "label_font_family": "Arial", "label_font_size": 10}, "graph.edge.e")
        color(edges["e"].get("stroke"), "#333333", "graph.edge.e.stroke")
        color(edges["e"].get("label_color"), "#111111", "graph.edge.e.label_color")
        line = indexed(page.get("lines"), {"e"}, "page.lines")["e"]
        self.check_line(line, edges["e"])
        labels = line.get("text", [])
        require(len(labels) == 1, "Source edge label count changed")
        text(labels[0].get("text"), "yes", "e.text", family="Arial", size=10, ink="#111111")
        mapping = self.read_json("out/mapping.json")
        subset(mapping, {"sha256": digest, "coordinates": "viewport-pixels",
                        "source_unchanged": True, "declared_node_count": 2,
                        "declared_edge_count": 1, "resolved_node_count": 2,
                        "resolved_edge_count": 1, "blocking_count": 0,
                        "source_to_native_ids": {"request": "request", "audit": "audit", "e": "e"}}, "mapping")
        ledger = mapping.get("ledger")
        require(isinstance(ledger, list), "Mapping feature ledger is missing")
        coordinates = [entry for entry in ledger if entry.get("feature") == "coordinates"]
        require(len(coordinates) == 1, "Mapping must expose one root coordinate decision")
        subset(coordinates[0], {"action": "preserved", "mode": "viewport-pixels",
                              "root_matrix": [2, 0, 0, 2, 50, 0], "page_size": [300, 200],
                              "source_view_box": [0, 0, 100, 100], "source_viewport": [300, 200]}, "root_mapping")
        required_actions = {"dash-pattern": "adapted", "marker": "adapted",
                            "font-family": "unknown", "text-layout": "adapted",
                            "page-background": "adapted"}
        for feature, action in required_actions.items():
            entries = [entry for entry in ledger if entry.get("feature") == feature]
            require(entries and all(entry.get("action") == action for entry in entries),
                    f"Mapping must disclose {feature} as {action}")
        dash_entries = [entry for entry in ledger if entry.get("feature") == "dash-pattern"]
        require(len(dash_entries) == 1, "Only the Audit node has a source dash pattern")
        subset(dash_entries[0], {"source_dash": [2, 1], "native_style": "dashed"}, "dash_mapping")
        self.native_report(self.read_json("out/native-report.json"), graph, page)
        require(not document.get("collections") and not page.get("dataBackedShapes"),
                "Fixed SVG reconstruction must not introduce generated layouts")
        require(not page.get("groups") and not page.get("layers"),
                "Incidental SVG groups must not become inferred native ownership")
        self.checks.append("Exact SVG source, metadata topology, manual viewport oracle and explicit adaptation ledger")

    def check_line(self, line: dict[str, Any], source: dict[str, Any]) -> None:
        same(line.get("lineType"), source["line_type"], f"line.{source['id']}.type")
        for index, key in enumerate(("source", "target"), start=1):
            same(line.get(f"endpoint{index}"),
                 {"type": "shapeEndpoint", "style": source[f"{key}_marker"],
                  "shapeId": source[key], "position": source[f"{key}_port"]},
                 f"line.{source['id']}.endpoint{index}")
        stroke = line.get("stroke", {})
        subset(stroke, {"width": source["stroke_width"],
                        "style": source.get("stroke_style", "solid")}, "line.stroke")
        color(stroke.get("color"), source["stroke"], "line.stroke.color")

    def contract(self, document: dict[str, Any], page: dict[str, Any]) -> None:
        graph = self.read_json("input/graph.json")
        same(graph, CONTRACT, "input contract identity")
        same(page.get("title"), CONTRACT["title"], "page.title")
        settings = page.get("settings", {})
        subset(settings, {"size": {"type": "custom", "w": 1000, "h": 400},
                          "infiniteCanvas": False, "autoTiling": False}, "page.settings")
        color(settings.get("fillColor"), "#FFFFFF", "page.fillColor")
        shapes = indexed(page.get("shapes"), {"work", "entity", "compute"}, "page.shapes")
        for node in CONTRACT["nodes"]:
            shape = shapes[node["id"]]
            subset(shape, {"type": node["type"], "boundingBox": {
                   "x": node["x"], "y": node["y"], "w": node["width"], "h": node["height"]}}, node["id"])
            for key, value in node["properties"].items():
                if key != "cells":
                    same(shape.get(key), value, f"{node['id']}.{key}")
            require("properties" not in shape, "Vendor properties must be emitted at shape top level")
        work = shapes["work"]
        same(work.get("opacity"), 80, "work.opacity")
        style = work.get("style", {})
        subset(style.get("fill", {}), {"type": "color"}, "work.fill")
        color(style.get("fill", {}).get("color"), "#EEEEEE", "work.fill.color")
        subset(style.get("stroke", {}), {"width": 2, "style": "dashed"}, "work.stroke")
        color(style.get("stroke", {}).get("color"), "#333333", "work.stroke.color")
        text(work.get("text"), "Review <P1> & accept", "work.text",
             family="Arial", size=16, align="left", bold=True)
        text(shapes["entity"].get("text", ""), "", "entity.outer_label")
        cells = shapes["entity"].get("cells")
        require(isinstance(cells, list) and len(cells) == 3, "Table cells changed")
        for index, (cell, expected) in enumerate(zip(cells, CONTRACT["nodes"][1]["properties"]["cells"])):
            same(set(cell), set(expected), f"cell[{index}].fields")
            for key, value in expected.items():
                if key == "text":
                    text(cell[key], value, f"cell[{index}].text")
                else:
                    same(cell[key], value, f"cell[{index}].{key}")
        compute = shapes["compute"]
        require("style" not in compute or compute["style"] == {},
                "Named library shape received unrequested styling")
        parsed = text(compute.get("text"), "Compute", "compute.text")
        require(not (set(parsed.styles) & {"font-family", "font-size", "color"}),
                "Named library text received unrequested font or ink defaults")
        line = indexed(page.get("lines"), {"rel"}, "page.lines")["rel"]
        edge = CONTRACT["edges"][0]
        self.check_line(line, edge)
        same(line.get("elbowControlPoints"), edge["elbow_points"], "rel.interior_route")
        require("joints" not in line, "Elbow route became unrelated line joints")
        labels = line.get("text")
        require(isinstance(labels, list) and len(labels) == 2, "Relationship labels changed")
        for index, expected in enumerate(edge["labels"]):
            subset(labels[index], {"position": expected["position"], "side": expected["side"]}, f"rel.label[{index}]")
            text(labels[index].get("text"), expected["text"], f"rel.label[{index}].text",
                 size=expected["font_size"], ink=expected["color"])
        same(page.get("groups"), [{"id": "pair", "items": ["work", "entity", "rel"], "zIndex": 2}], "groups")
        same(page.get("layers"), [{"id": "semantic", "title": "Diagram", "items": ["pair", "compute"], "layerIndex": 0}], "layers")
        report = self.read_json("out/native-report.json")
        self.native_report(report, graph, page)
        require(any(item.get("id") == "compute" and item.get("feature") == "native_library_defaults"
                    for item in report["requires_live_check"]),
                "Named shape default rendering must remain a live-check item")
        require(not document.get("collections") and not page.get("dataBackedShapes"),
                "Explicit mixed fixed-layout contract gained generated objects")
        self.checks.append("Rich input identity, native properties, literal cell merges, route, markers, groups, layers and library defaults")

    def generalization(self, document: dict[str, Any], page: dict[str, Any]) -> None:
        source = self.read_json("input/layout.json")
        same(source, GENERATED, "input generated-family identity")
        same(document.get("collections"), GENERATED["collections"], "literal collections")
        same(page.get("dataBackedShapes"), GENERATED["layouts"], "literal generated layout fields")
        same(page.get("title"), GENERATED["graph"]["title"], "page.title")
        same(page.get("settings", {}).get("infiniteCanvas"), True, "page.infiniteCanvas")
        require("size" not in page.get("settings", {}), "Infinite generated page gained a finite crop")
        note = indexed(page.get("shapes"), {"note"}, "ordinary native shapes")["note"]
        subset(note, {"type": "rectangle", "boundingBox": {"x": 10, "y": 10, "w": 100, "h": 50}}, "note")
        text(note.get("text"), "Reference", "note.text")
        same(page.get("lines", []), [], "ordinary native lines")
        require(not page.get("groups") and not page.get("layers"), "Generated fixture gained extra ownership")
        report = self.read_json("out/layout-report.json")
        same(report.get("schema_version"), 1, "layout report version")
        same(report.get("totals"), {"orgChart": 3, "mindMap": 3}, "generated totals")
        decisions = indexed(report.get("generated_layouts"), {item["id"] for item in GENERATED["layouts"]}, "generated decisions")
        for layout in GENERATED["layouts"]:
            decision = decisions[layout["id"]]
            same(decision.get("type"), layout["type"], f"layout.{layout['id']}.type")
            require(isinstance(decision.get("geometry"), str) and decision["geometry"].strip(),
                    f"layout.{layout['id']} lacks geometry disclosure")
        for object_id in ("organization", "topics"):
            subset(decisions[object_id], {"item_count": 3, "root_ids": ["ada"],
                   "relationship_count": 2, "collection_id": "people"}, object_id)
        same(decisions["sequence"].get("markup_characters"), len(GENERATED["layouts"][2]["markup"]), "sequence markup length")
        require(isinstance(decisions["sequence"].get("markup_validation"), str)
                and decisions["sequence"]["markup_validation"].strip(), "Sequence validation scope is missing")
        same(decisions["arrange"].get("shape_ids"), ["note"], "assisted layout membership")
        for key in ("scope", "live_import", "rendered_fidelity", "page_extent_check"):
            require(isinstance(report.get(key), str) and report[key].strip(), f"Generated report lacks {key}")
        self.native_report(report.get("native_graph"), GENERATED["graph"], page)
        self.checks.append("Exact collections, parents, literal markup and all generated fields; independent counts and infinite-page check")

    def run(self) -> dict[str, Any]:
        require(self.workspace.is_dir(), "Candidate workspace does not exist")
        document, page = self.check_package()
        getattr(self, self.kind)(document, page)
        note_name = "status.md" if self.kind == "contract" else "changes.md"
        if not self.smoke:
            note = self.path(f"out/{note_name}").read_text(encoding="utf-8-sig")
            require(note.strip(), f"Narrative artifact out/{note_name} is empty")
            self.checks.append("Required narrative artifact exists; its factual content requires manual review")
        return {"schema_version": 1, "kind": self.kind, "workspace": str(self.workspace),
                "passed": True, "smoke": self.smoke, "checks": self.checks,
                "manual_review": [
                    "Review English narrative against prompt requirements; no phrase-based grading was performed.",
                    "Confirm no actual live import or measured visual-equivalence claim is made.",
                    "Service acceptance, text metrics, native editing and rendered glyphs remain untested.",
                ]}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("kind", choices=("naturalistic", "contract", "generalization"))
    parser.add_argument("workspace", type=Path)
    parser.add_argument("--report", type=Path, required=True,
                        help="Evaluator-owned JSON path outside the candidate workspace")
    parser.add_argument("--smoke", action="store_true",
                        help="Check local smoke artifacts without requiring a narrative deliverable")
    args = parser.parse_args()
    workspace = args.workspace.resolve()
    report_path = args.report.resolve()
    if report_path.is_relative_to(workspace):
        parser.error("--report must be outside the candidate workspace")
    evaluator = Evaluator(args.kind, workspace, args.smoke)
    try:
        result = evaluator.run()
    except (ValidationError, ValueError, OSError, KeyError, TypeError, zipfile.BadZipFile) as error:
        result = {"schema_version": 1, "kind": args.kind, "workspace": str(workspace),
                  "passed": False, "smoke": args.smoke, "checks": evaluator.checks,
                  "error": f"{type(error).__name__}: {error}"}
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"kind": args.kind, "passed": result["passed"], "report": str(report_path)}, indent=2))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
