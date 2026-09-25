#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Validate a flat hierarchy and build one offline, interactive SVG explorer."""

from __future__ import annotations

import argparse
import html
import json
import math
import random
from pathlib import Path

MAX_NODES = 20000
MAX_DEPTH = 64


def nonempty(value, context):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{context} must be a nonempty string")
    return value


def normalize(source):
    if not isinstance(source, dict):
        raise ValueError("Input must be a JSON object")
    title = nonempty(source.get("title"), "title")
    provenance = nonempty(source.get("provenance"), "provenance")
    dimensions = source.get("dimensions")
    rows = source.get("nodes")
    if not isinstance(dimensions, list) or not 1 <= len(dimensions) <= 16:
        raise ValueError("Provide between 1 and 16 dimensions")
    if not isinstance(rows, list) or not 1 <= len(rows) <= MAX_NODES:
        raise ValueError(f"Provide between 1 and {MAX_NODES} nodes")
    dims, keys = [], set()
    for raw in dimensions:
        if not isinstance(raw, dict):
            raise ValueError("Every dimension must be an object")
        key = nonempty(raw.get("key"), "Dimension key")
        if key in keys:
            raise ValueError(f"Duplicate dimension key: {key}")
        keys.add(key)
        dim = {"key": key, "label": nonempty(raw.get("label"), key), "type": raw.get("type")}
        if dim["type"] == "numeric":
            dim.update(unit=nonempty(raw.get("unit"), f"{key} unit"),
                       period=nonempty(raw.get("period"), f"{key} period"),
                       aggregation=raw.get("aggregation", "none"))
            if dim["aggregation"] not in {"none", "sum"}:
                raise ValueError(f"{key}: aggregation must be none or sum")
        elif dim["type"] == "categorical":
            if "categories" in raw:
                categories = raw["categories"]
                if not isinstance(categories, list) or any(not isinstance(v, str) or not v.strip() for v in categories):
                    raise ValueError(f"{key}: categories must be nonempty strings")
                if len(categories) != len(set(categories)):
                    raise ValueError(f"{key}: duplicate categories")
                dim["categories"] = categories[:]
        else:
            raise ValueError(f"{key}: type must be categorical or numeric")
        dims.append(dim)
    nodes, by_id = [], {}
    for raw in rows:
        if not isinstance(raw, dict):
            raise ValueError("Every node must be an object")
        identity = nonempty(raw.get("id"), "Node ID")
        if identity in by_id:
            raise ValueError(f"Duplicate node ID: {identity}")
        if "parentId" not in raw:
            raise ValueError(f"{identity}: parentId is required; use null for the root")
        parent = raw["parentId"]
        if parent is not None:
            nonempty(parent, f"{identity} parentId")
        values = raw.get("values", {})
        if not isinstance(values, dict):
            raise ValueError(f"{identity}: values must be an object")
        clean = {}
        for dim in dims:
            key, value = dim["key"], values.get(dim["key"])
            if value is not None:
                if dim["type"] == "categorical":
                    nonempty(value, f"{identity}/{key}")
                elif isinstance(value, bool) or not isinstance(value, (float, int)) or not math.isfinite(value) or not 0 <= value <= 9007199254740991:
                    raise ValueError(f"{identity}/{key}: numeric values must be finite, nonnegative, and within JavaScript precision")
            clean[key] = value
        node = dict(id=identity, parentId=parent, label=nonempty(raw.get("label"), identity),
                    values=clean, children=[], count=1, depth=0, aggregates={})
        nodes.append(node)
        by_id[identity] = node
    roots = [node for node in nodes if node["parentId"] is None]
    if len(roots) != 1:
        raise ValueError("The hierarchy must have exactly one root")
    root = roots[0]
    for node in nodes:
        if node is root:
            continue
        if node["parentId"] not in by_id:
            raise ValueError(f"{node['id']}: missing parent {node['parentId']}")
        by_id[node["parentId"]]["children"].append(node["id"])
    order, stack, visited = [], [root], set()
    while stack:
        node = stack.pop()
        if node["id"] in visited:
            raise ValueError("Cycle detected")
        visited.add(node["id"])
        if node["depth"] > MAX_DEPTH:
            raise ValueError(f"Hierarchy depth exceeds {MAX_DEPTH}")
        order.append(node)
        for identity in reversed(node["children"]):
            by_id[identity]["depth"] = node["depth"] + 1
            stack.append(by_id[identity])
    if len(visited) != len(nodes):
        raise ValueError("Cycle or disconnected component detected")
    for node in reversed(order):
        children = [by_id[identity] for identity in node["children"]]
        node["count"] += sum(child["count"] for child in children)
        for dim in dims:
            if dim["type"] == "numeric" and dim["aggregation"] == "sum":
                key, own = dim["key"], node["values"][dim["key"]]
                known = int(own is not None) + sum(child["aggregates"][key]["known"] for child in children)
                total = (own or 0) + sum(child["aggregates"][key]["value"] or 0 for child in children)
                if not math.isfinite(total) or total > 9007199254740991:
                    raise ValueError(f"{key}: subtree sum exceeds JavaScript numeric precision")
                node["aggregates"][key] = {"value": total if known else None, "known": known}
    root["x0"], root["x1"] = 0.0, math.tau
    for node in order:
        cursor = node["x0"]
        unit = (node["x1"] - node["x0"]) / node["count"]
        for identity in node["children"]:
            child = by_id[identity]
            child["x0"], child["x1"] = cursor, cursor + child["count"] * unit
            cursor = child["x1"]
    for dim in dims:
        key = dim["key"]
        observed = list(dict.fromkeys(node["values"][key] for node in nodes if node["values"][key] is not None))
        dim["missing"] = sum(node["values"][key] is None for node in nodes)
        if dim["type"] == "categorical":
            categories = dim.setdefault("categories", observed)
            if any(value not in categories for value in observed):
                raise ValueError(f"{key}: declared categories omit an observed value")
            if len(categories) > 8:
                raise ValueError(f"{key}: at most eight categories are supported; group explicitly")
        else:
            dim["maxIndividual"] = max(observed, default=0)
            dim["maxSubtree"] = root["aggregates"][key]["value"] or 0 if dim["aggregation"] == "sum" else None
    return {"title": title, "description": nonempty(source.get("description", "One hierarchy. Multiple perspectives."), "description"),
            "entityLabel": nonempty(source.get("entityLabel", "records"), "entityLabel"), "provenance": provenance,
            "dimensions": dims, "nodes": order, "rootId": root["id"], "maxDepth": max(n["depth"] for n in order),
            "patternId": "hierarchy-radial-lenses"}


def demo(size=1200):
    if not 2 <= size <= MAX_NODES:
        raise ValueError(f"Demo size must be between 2 and {MAX_NODES}")
    rng = random.Random(73021)
    divisions = ["Engineering", "Product", "Customer operations", "Commercial", "Finance", "People"]
    departments = ["Platform", "Data", "Experience", "Operations"]
    roles = ["Engineering", "Product", "Operations", "Sales", "Finance", "People", "Leadership"]
    nodes = []

    def add(parent, label, level, role):
        index = len(nodes)
        identity = f"p{index:05d}"
        contract = "Permanent" if level != "Individual contributor" else rng.choices(["Permanent", "Contractor", "Fixed term"], [7, 2, 1])[0]
        tokens = int(rng.lognormvariate(10.6, 1.15) // 100 * 100)
        if index and index % 31 == 0:
            tokens = None
        elif index and index % 29 == 0:
            tokens = 0
        nodes.append({"id": identity, "parentId": parent, "label": label,
                      "values": {"leadership": level, "contract": contract, "role": role, "tokens": tokens}})
        return identity

    root = add(None, "Alex Morgan · Chief executive", "L1", "Leadership")
    leads = []
    for division in divisions:
        if len(nodes) >= size:
            break
        director = add(root, f"{division} · VP", "L2", "Leadership")
        for department in departments:
            if len(nodes) >= size:
                break
            manager = add(director, f"{division} / {department}", "L3", "Leadership")
            for team in range(3):
                if len(nodes) >= size:
                    break
                lead = add(manager, f"{division} · {department} team {team + 1}", "L4", "Leadership")
                leads.append((lead, division, department))
    given = ["Jordan", "Taylor", "Casey", "Sam", "Riley", "Avery", "Morgan", "Cameron", "Jamie", "Quinn", "Robin", "Drew"]
    family = ["Lee", "Parker", "Reed", "Patel", "Chen", "Rivera", "Wright", "Kim", "Brown", "Carter", "Singh", "Diaz"]
    for index in range(size - len(nodes)):
        parent, division, department = leads[index % len(leads)]
        if index % 7 == 0 and len(nodes) > 120:
            candidates = [n for n in nodes[103:] if n["values"]["leadership"] == "L4"]
            if candidates:
                parent = candidates[index % len(candidates)]["id"]
        role = {"Customer operations": "Operations", "Commercial": "Sales"}.get(division, division)
        is_lead = index % 19 == 0
        add(parent, f"{given[index % 12]} {family[(index // 12) % 12]} · {department} {index + 1:04d}", "L4" if is_lead else "Individual contributor", "Leadership" if is_lead else role)
    return {"title": "Organization atlas", "description": "Explore the same organization through a different lens.",
            "entityLabel": "people", "provenance": "Synthetic organization for demonstration. Fictional identities, reporting lines, and AI usage; August 2026.",
            "dimensions": [
                {"key": "leadership", "label": "Leadership", "type": "categorical", "categories": ["L1", "L2", "L3", "L4", "Individual contributor"]},
                {"key": "contract", "label": "Contract", "type": "categorical", "categories": ["Permanent", "Contractor", "Fixed term"]},
                {"key": "role", "label": "Role", "type": "categorical", "categories": roles},
                {"key": "tokens", "label": "AI tokens", "type": "numeric", "unit": "tokens", "period": "August 2026", "aggregation": "sum"}
            ], "nodes": nodes}


def build(source, output):
    data = normalize(source)
    template = (Path(__file__).resolve().parent.parent / "assets" / "templates" / "explorer.html").read_text(encoding="utf-8")
    payload = json.dumps(data, ensure_ascii=False, separators=(",", ":"), allow_nan=False).replace("<", "\\u003c").replace("&", "\\u0026").replace("\u2028", "\\u2028").replace("\u2029", "\\u2029")
    rendered = template.replace("__TITLE__", html.escape(data["title"])).replace("__PAYLOAD__", payload)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(rendered, encoding="utf-8")
    return {"ok": True, "output": str(output), "nodes": len(data["nodes"]), "levels": data["maxDepth"] + 1,
            "rootId": data["rootId"], "dimensions": len(data["dimensions"]), "patternId": data["patternId"],
            "numericTotals": data["nodes"][0]["aggregates"], "bytes": output.stat().st_size}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--input", type=Path)
    group.add_argument("--demo", action="store_true")
    parser.add_argument("--demo-size", type=int, default=1200)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--data-output", type=Path)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    try:
        paths = [p.resolve() for p in [args.input, args.output, args.data_output, args.report] if p]
        if len(paths) != len(set(paths)):
            raise ValueError("Input, output, data-output, and report paths must be distinct")
        source = demo(args.demo_size) if args.demo else json.loads(args.input.read_text(encoding="utf-8-sig"))
        report = build(source, args.output)
        if args.data_output:
            args.data_output.parent.mkdir(parents=True, exist_ok=True)
            args.data_output.write_text(json.dumps(source, indent=2, ensure_ascii=False, allow_nan=False) + "\n", encoding="utf-8")
        if args.report:
            args.report.parent.mkdir(parents=True, exist_ok=True)
            args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(report))
        return 0
    except (ValueError, OSError) as error:
        print(json.dumps({"ok": False, "error": str(error)}))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
