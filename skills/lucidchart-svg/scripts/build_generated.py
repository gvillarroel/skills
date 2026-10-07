#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Package explicit data-backed layouts; Lucid determines their final geometry.

Run: uv run --script build_generated.py layout.json --output layout.lucid --report layout-report.json
Input: {graph?: native-compiler graph, collections?: [{id,values:[objects]}],
layouts: [{id,type,position?,collectionId?,... documented fields}]}
Only inline collections are accepted; external data and image URL fields require
a separately reviewed resource workflow. This command does not access Lucid.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import re
import sys

sys.dont_write_bytecode = True

from build_native import (GraphError, build_document, compatibility_report,
                          document_bytes, identifier, package_bytes,
                          reject_nonfinite, require_object, unique_json_object)

SOURCES = ["https://lucid.readme.io/docs/data-backed-shapes-si",
           "https://lucid.readme.io/docs/data-si", "https://lucid.readme.io/docs/pages-si"]
FIELDS = {
    "orgChart": {"position", "collectionId", "idField", "foreignKeyField", "nameField", "roleField", "extraFields"},
    "mindMap": {"position", "collectionId", "idField", "parentIdField", "textField"},
    "umlSequence": {"position", "markup"},
    "assistedLayout": {"shapeIds"},
}
REQUIRED = {
    "orgChart": {"position", "collectionId", "idField", "foreignKeyField", "nameField"},
    "mindMap": {"position", "collectionId", "idField", "parentIdField", "textField"},
    "umlSequence": {"position", "markup"},
    "assistedLayout": set(),
}


def literal(value: object, context: str, *, limit: int = 10_000) -> str:
    if not isinstance(value, str) or not value.strip() or len(value) > limit:
        raise GraphError(f"{context} must be a nonblank string of at most {limit} characters")
    try:
        value.encode("utf-8")
    except UnicodeError as error:
        raise GraphError(f"{context} has invalid Unicode") from error
    return value


def data_value(value: object, context: str) -> None:
    # Flat JSON scalars avoid undocumented nested data-cell coercion.
    if value is None or isinstance(value, bool):
        return
    if isinstance(value, str):
        if len(value) > 50_000:
            raise GraphError(f"{context} exceeds the local 50000-character data-cell limit")
        value.encode("utf-8")
        return
    if isinstance(value, (int, float)):
        try:
            if math.isfinite(value):
                return
        except OverflowError:
            pass
    raise GraphError(f"{context} must be a finite JSON scalar")


def position(value: object, context: str) -> dict:
    raw = require_object(value, context, {"x", "y"}, {"x", "y"})
    for key, number in raw.items():
        if isinstance(number, bool) or not isinstance(number, (int, float)) or not 0 <= number <= 20_000 or not math.isfinite(number):
            raise GraphError(f"{context}.{key} must be finite and within 0..20000")
    return dict(raw)


def forest(rows: list[dict], layout: dict, context: str) -> dict:
    """Check declared identities, labels, parent references and cycles without inference."""
    id_field = layout["idField"]
    parent_field = layout["foreignKeyField" if layout["type"] == "orgChart" else "parentIdField"]
    label_field = layout["nameField" if layout["type"] == "orgChart" else "textField"]
    identities, parents = set(), {}
    for index, row in enumerate(rows):
        item = f"{context}.rows[{index}]"
        identity = literal(row.get(id_field), f"{item}.{id_field}")
        if identity in identities:
            raise GraphError(f"{item}: duplicate primary key {identity!r}")
        identities.add(identity)
        literal(row.get(label_field), f"{item}.{label_field}")
        parent = row.get(parent_field)
        if parent is not None and parent != "":
            parent = literal(parent, f"{item}.{parent_field}")
        parents[identity] = parent or None
    for identity, parent in parents.items():
        if parent is not None and parent not in identities:
            raise GraphError(f"{context}: dangling parent {parent!r} on {identity!r}")
    visited = set()
    for identity in identities:
        trail, current = set(), identity
        while current is not None and current not in visited:
            if current in trail:
                raise GraphError(f"{context}: parent cycle at {current!r}")
            trail.add(current)
            current = parents[current]
        visited.update(trail)
    roots = [identity for identity, parent in parents.items() if parent is None]
    if layout["type"] == "mindMap" and len(roots) != 1:
        raise GraphError(f"{context}: local mind-map policy requires exactly one explicit root")
    return {"item_count": len(rows), "root_ids": roots,
            "relationship_count": sum(parent is not None for parent in parents.values())}


def build_generated(source: object) -> tuple[dict, dict]:
    root = require_object(source, "input", {"graph", "collections", "layouts"}, {"layouts"})
    graph = root.get("graph", {"nodes": []})
    document = build_document(graph)
    page = document["pages"][0]
    used = {page["id"]}
    for kind in ("shapes", "lines", "groups", "layers"):
        used.update(item["id"] for item in page.get(kind, []))
    collection_map = {}
    raw_collections = root.get("collections", [])
    if not isinstance(raw_collections, list):
        raise GraphError("input.collections must be an array")
    for index, item in enumerate(raw_collections):
        context = f"collections[{index}]"
        raw = require_object(item, context, {"id", "values"}, {"id", "values"})
        collection_id = identifier(raw["id"], f"{context}.id")
        if collection_id in used:
            raise GraphError(f"{context}.id collides with another object")
        used.add(collection_id)
        rows = raw["values"]
        if not isinstance(rows, list) or not rows or len(rows) > 4000:
            raise GraphError(f"{context}.values must contain 1..4000 rows")
        for row_index, row in enumerate(rows):
            if not isinstance(row, dict) or not row:
                raise GraphError(f"{context}.values[{row_index}] must be a nonempty object")
            for key, value in row.items():
                literal(key, f"{context}.column", limit=128)
                data_value(value, f"{context}.values[{row_index}].{key}")
        collection_map[collection_id] = raw
    # This local cap keeps inline content bounded; the vendor's 1MB data-directory
    # cap concerns external data files, which this driver does not produce.
    if len(json.dumps(raw_collections, ensure_ascii=False).encode("utf-8")) > 1_000_000:
        raise GraphError("Inline collections exceed the local 1000000-byte limit")
    layouts = root["layouts"]
    if not isinstance(layouts, list) or not layouts:
        raise GraphError("input.layouts must be a nonempty array")
    native_layouts, decisions = [], []
    totals = {"orgChart": 0, "mindMap": 0}
    shape_ids = {shape["id"] for shape in page["shapes"]}
    for index, item in enumerate(layouts):
        context = f"layouts[{index}]"
        if not isinstance(item, dict) or not isinstance(item.get("type"), str) or item["type"] not in FIELDS:
            raise GraphError(f"{context}.type must be orgChart, mindMap, umlSequence or assistedLayout")
        family = item["type"]
        raw = require_object(item, context, FIELDS[family] | {"id", "type"}, REQUIRED[family] | {"id", "type"})
        layout_id = identifier(raw["id"], f"{context}.id")
        if layout_id in used:
            raise GraphError(f"{context}.id collides with another object")
        used.add(layout_id)
        result = dict(raw)
        if "position" in raw:
            result["position"] = position(raw["position"], f"{context}.position")
        decision = {"id": layout_id, "type": family, "geometry": "Lucid-generated; source coordinates and text metrics are not preserved"}
        if family in totals:
            collection_id = identifier(raw["collectionId"], f"{context}.collectionId")
            if collection_id not in collection_map:
                raise GraphError(f"{context}.collectionId is undefined")
            for key in FIELDS[family] - {"position", "extraFields"}:
                if key in raw:
                    literal(raw[key], f"{context}.{key}", limit=128 if key.endswith("Field") else 10_000)
            if "extraFields" in raw:
                fields = raw["extraFields"]
                if not isinstance(fields, list) or any(not isinstance(field, str) for field in fields) or len(fields) != len(set(fields)):
                    raise GraphError(f"{context}.extraFields must be an array of unique field names")
                for field in fields:
                    literal(field, f"{context}.extraFields", limit=128)
            rows = collection_map[collection_id]["values"]
            optional_fields = raw.get("extraFields", []) + ([raw["roleField"]] if "roleField" in raw else [])
            if any(not any(field in row for row in rows) for field in optional_fields):
                raise GraphError(f"{context}: a requested optional display/data field is absent from all rows")
            decision.update(forest(rows, raw, context))
            totals[family] += len(rows)
            if totals[family] > 4000:
                raise GraphError(f"Total generated {family} items exceed the documented 4000-item document limit")
            decision["collection_id"] = collection_id
        elif family == "umlSequence":
            literal(raw["markup"], f"{context}.markup", limit=50_000)
            if re.search(r"(?im)^\s*!(?:include\w*|import)\b", raw["markup"]):
                raise GraphError(f"{context}.markup contains an external include/import directive requiring separate resource review")
            decision["markup_characters"] = len(raw["markup"])
            decision["markup_validation"] = "nonempty/length only; Lucid's supported PlantUML-style sequence grammar requires live validation"
        else:
            selected = raw.get("shapeIds", sorted(shape_ids))
            if not isinstance(selected, list) or not selected or any(not isinstance(value, str) for value in selected) or len(set(selected)) != len(selected):
                raise GraphError(f"{context}.shapeIds must select unique existing shapes")
            if set(selected) - shape_ids:
                raise GraphError(f"{context}.shapeIds contains undefined or non-shape IDs")
            decision["shape_ids"] = selected
        native_layouts.append(result)
        decisions.append(decision)
    if raw_collections:
        document["collections"] = raw_collections
    page["dataBackedShapes"] = native_layouts
    report = {"schema_version": 1, "scope": "local documented data-backed subset, not live import or SVG parsing",
              "live_import": "not executed", "rendered_fidelity": "not measured", "source_urls": SOURCES,
              "page_extent_check": "Generated dimensions are unknown; inspect finite-page clipping and autoTiling after live creation",
              "generated_layouts": decisions, "totals": totals,
              "policies": ["string primary/parent keys; flat scalar data cells", "mind maps require one explicit root; org charts allow forests",
                           "inline collection bytes limited to1000000 locally; no external files or remote image fields"],
              "native_graph": compatibility_report(graph, document)}
    return document, report


def main(argv: list[str] | None = None) -> int:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("input", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--document-json", type=Path)
    parser.add_argument("--report", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        paths = [args.input, args.output, args.report] + ([args.document_json] if args.document_json is not None else [])
        if len({path.resolve() for path in paths}) != len(paths):
            raise GraphError("Input and output paths must be distinct")
        for index, first in enumerate(paths):
            for second in paths[index + 1:]:
                if first.exists() and second.exists() and first.samefile(second):
                    raise GraphError("Input and output paths alias the same existing file")
        if args.output.suffix.lower() != ".lucid":
            raise GraphError("--output must have a .lucid extension")
        source = json.loads(args.input.read_text(encoding="utf-8-sig"), object_pairs_hook=unique_json_object, parse_constant=reject_nonfinite)
        document, report = build_generated(source)
        raw = document_bytes(document)
        outputs = [(args.output, package_bytes(raw)), (args.report, (json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False) + "\n").encode("utf-8"))]
        if args.document_json is not None:
            outputs.append((args.document_json, raw))
        for path, content in outputs:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)
        print(json.dumps({"package": str(args.output), "report": str(args.report), "generated_layout_count": len(document["pages"][0]["dataBackedShapes"]),
                          "local_validation": "passed documented subset checks", "live_import": "not executed", "geometry": "Lucid-generated"}))
        return 0
    except (ValueError, TypeError, OSError, UnicodeError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
