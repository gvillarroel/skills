#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["Pillow>=11,<13"]
# ///
"""Run: uv run --script scripts/import_assets.py --brief scene.json --plan assets.json --output assembled.json --report import.json."""
from __future__ import annotations

import argparse
import copy
import hashlib
import html
import json
import math
import os
from pathlib import Path
import re
import sys
import xml.etree.ElementTree as ET

sys.dont_write_bytecode = True
import explainer as engine

NUMBER = r"[-+]?(?:\d*\.\d+|\d+\.?\d*)(?:[eE][-+]?\d+)?"
TRANSLATE = re.compile(rf"^translate\(\s*({NUMBER})(?:[\s,]+({NUMBER}))?\s*\)$")
STYLE_KEYS = {"fill", "stroke", "stroke-width", "opacity", "font-size", "text-anchor", "color",
              "stroke-linecap", "stroke-linejoin", "stroke-dasharray", "data-fill-role", "data-stroke-role"}
GEOMETRY = {"circle": {"cx", "cy", "r"}, "ellipse": {"cx", "cy", "rx", "ry"},
            "rect": {"x", "y", "width", "height", "rx"}, "line": {"x1", "y1", "x2", "y2"},
            "path": {"d"}, "polygon": {"points"}, "polyline": {"points"}, "text": {"x", "y"}}


def numeric(value, context):
    if not re.fullmatch(NUMBER, str(value)) or not math.isfinite(float(value)):
        raise ValueError(f"{context} must be one finite number without units.")
    return float(value)


def svg_marks(source, asset, palette):
    raw = source.read_text(encoding="utf-8-sig")
    if re.search(r"<!\s*(?:DOCTYPE|ENTITY)", raw, re.I):
        raise ValueError("SVG must not contain a DTD or entity declarations.")
    root = ET.fromstring(raw)
    tag = lambda node: node.tag.removeprefix("{http://www.w3.org/2000/svg}")
    if tag(root) != "svg":
        raise ValueError("Asset root must be SVG in the SVG namespace.")
    box = [numeric(v, "viewBox") for v in re.split(r"[\s,]+", root.get("viewBox", "").strip())]
    if len(box) != 4 or box[:2] != [0, 0] or min(box[2:]) <= 0:
        raise ValueError("Flatten the SVG to a positive viewBox starting at 0 0; placement uses native pixel dimensions.")
    if not any(tag(n) == "title" and (n.text or "").strip() for n in root):
        raise ValueError("SVG needs a direct title describing the subject.")
    placement = asset.get("placement", [0, 0])
    if len(placement) != 2 or not all(engine.number(v) for v in placement):
        raise ValueError("Asset placement must be [x, y] in its view's local coordinates.")
    reverse = {v: k for k, v in reversed(list(palette["roles"].items()))}
    marks, seen, selectors = [], set(), {}

    def role(paint, style, channel):
        declared = style.get(f"data-{channel}-role")
        if declared:
            if declared not in palette["roles"] and declared != "none":
                raise ValueError(f"Unknown palette role: {declared}")
            if paint not in (None, "none", "currentColor", palette["roles"].get(declared)):
                raise ValueError(f"{channel} disagrees with its declared palette role.")
            return declared
        if paint in (None, "none"):
            return "none"
        if paint == "currentColor":
            paint = style.get("color")
        if paint not in reverse:
            raise ValueError(f"Paint {paint!r} is outside the active palette. Normalize exact tokens before import.")
        return reverse[paint]

    def walk(node, inherited, offset, ancestors=()):
        kind = tag(node)
        if kind in {"title", "desc", "metadata"}:
            return
        if kind not in {"svg", "g", *GEOMETRY}:
            raise ValueError(f"Unsupported SVG element: {kind}. Flatten it before import or use the custom-scene route.")
        allowed = STYLE_KEYS | {"id", "transform", "role", "aria-label", "aria-labelledby", "font-family", "class"}
        allowed |= {"viewBox", "width", "height", "version"} if kind == "svg" else GEOMETRY.get(kind, set())
        bad = [k for k in node.attrib if k not in allowed and not k.startswith("data-")]
        if bad:
            raise ValueError(f"Unsupported SVG attributes on {kind}: {', '.join(bad)}")
        dx, dy = offset
        if node.get("transform"):
            transform = TRANSLATE.fullmatch(node.get("transform"))
            if not transform:
                raise ValueError("Only group/element translation is supported. Bake scale, rotate, skew and matrix transforms into geometry.")
            dx += numeric(transform[1], "translation"); dy += numeric(transform[2] or 0, "translation")
        style = {**inherited, **{k: v for k, v in node.attrib.items() if k in STYLE_KEYS}}
        if node.get("opacity"):
            style["opacity"] = str(numeric(inherited.get("opacity", 1), "opacity") * numeric(node.get("opacity"), "opacity"))
        if kind in {"svg", "g"}:
            identity = node.get("id")
            if identity:
                if not engine.SAFE_ID.fullmatch(identity) or identity in seen:
                    raise ValueError("SVG group IDs must be unique lowercase hyphen-case names.")
                seen.add(identity); selectors[identity] = []
                ancestors = (*ancestors, identity)
            for child in node:
                walk(child, style, (dx, dy), ancestors)
            return
        identity = node.get("id", "")
        if not engine.SAFE_ID.fullmatch(identity) or identity in seen:
            raise ValueError("Every rendered SVG shape needs a unique lowercase hyphen-case ID.")
        seen.add(identity)
        selectors[identity] = [f"{asset['id']}-{identity}"]
        for ancestor in ancestors: selectors[ancestor].append(f"{asset['id']}-{identity}")
        if len(node):
            raise ValueError("Flatten text/tspan and nested rendered elements into direct single-line shapes.")
        attrs, output_kind = {}, kind
        for key in GEOMETRY[kind] - {"d", "points"}:
            if key in node.attrib or key != "rx":
                attrs[key] = numeric(node.get(key, 0), f"{identity}.{key}")
        for key in {"x", "x1", "x2", "cx"} & attrs.keys(): attrs[key] += dx
        for key in {"y", "y1", "y2", "cy"} & attrs.keys(): attrs[key] += dy
        if kind in {"path", "polygon", "polyline"}:
            output_kind = "path"; attrs = {"translateX": dx, "translateY": dy}
        mark = {"id": f"{asset['id']}-{identity}", "view": asset["view"], "kind": output_kind, "attrs": attrs,
                "fill": role(style.get("fill"), style, "fill"), "stroke": role(style.get("stroke"), style, "stroke"),
                "strokeWidth": numeric(style.get("stroke-width", 3), "stroke width"),
                "linecap": style.get("stroke-linecap", "round"), "linejoin": style.get("stroke-linejoin", "round")}
        if style.get("opacity"):
            mark["opacity"] = numeric(style["opacity"], "opacity")
        if style.get("stroke-dasharray") and style["stroke-dasharray"] != "none":
            if not re.fullmatch(r"[0-9.,\s]+", style["stroke-dasharray"]): raise ValueError("Dash lengths must be nonnegative literal numbers.")
            mark["dash"] = style["stroke-dasharray"]
        if kind == "path": mark["d"] = node.get("d", "")
        if kind in {"polyline", "polygon"}:
            points = [numeric(v, "points") for v in re.split(r"[\s,]+", node.get("points", "").strip())]
            if len(points) < 4 or len(points) % 2: raise ValueError("Polyline/polygon points need complete coordinate pairs.")
            mark["d"] = " ".join(f"{'M' if i == 0 else 'L'}{points[i]} {points[i+1]}" for i in range(0, len(points), 2)) + (" Z" if kind == "polygon" else "")
        if kind == "text":
            attrs["fontSize"] = numeric(style.get("font-size", 32), "font size")
            mark.update(text=node.text or "", anchor=style.get("text-anchor", "start"), textRole="direct")
        marks.append(mark)
    walk(root, {"fill": "none", "stroke": "none"}, tuple(placement))
    if not marks: raise ValueError("An explanatory asset must contain visible editable geometry.")
    return marks, box, selectors


def assemble(brief_path, plan_path, output_path):
    brief_path, plan_path, output_path = map(lambda p: Path(p).resolve(), [brief_path, plan_path, output_path])
    if output_path.is_relative_to(engine.BUNDLE):
        raise ValueError("The skill is read-only. Write assembled briefs outside the bundle.")
    brief = json.loads(brief_path.read_text(encoding="utf-8-sig"))
    plan = json.loads(plan_path.read_text(encoding="utf-8-sig"))
    if not isinstance(plan, dict) or plan.get("schemaVersion") != 1 or not isinstance(plan.get("assets"), list) or not plan["assets"]:
        raise ValueError("Use schemaVersion 1 and a nonempty assets list.")
    palette = json.loads((engine.BUNDLE / "assets/palettes/colorsets.json").read_text(encoding="utf-8"))["colorsets"][brief.get("palette", {}).get("mode", "colorset1")]
    existing = {m["id"] for m in brief.get("marks", [])}
    views = {v["id"]: v["region"] for v in brief.get("views", [])}
    events = {e["id"] for e in brief.get("events", [])} | {"establish", "hold"}
    imported, provenance, asset_ids = [], [], set()
    for asset in plan["assets"]:
        if not isinstance(asset, dict) or not engine.SAFE_ID.fullmatch(str(asset.get("id", ""))) or asset["id"] in asset_ids:
            raise ValueError("Asset IDs must be unique lowercase hyphen-case names.")
        asset_ids.add(asset["id"])
        if not all(isinstance(asset.get(k), str) and asset[k].strip() for k in ["path", "producer", "purpose", "view"]):
            raise ValueError("Each asset needs path, producer, purpose and view.")
        if asset["view"] not in views: raise ValueError("Asset view is undeclared.")
        moments = asset.get("moments", [])
        if not isinstance(moments, list) or not moments or any(m not in events for m in moments):
            raise ValueError("Assign the asset to declared event IDs, establish or hold.")
        source = (plan_path.parent / asset["path"]).resolve()
        if not source.is_file():
            raise ValueError(f"Asset source does not exist: {source}. Resolve path relative to the asset-plan JSON, not the command workspace. For deliverables/asset-plan.json use assets/mechanism.svg.")
        marks, box, selectors = svg_marks(source, asset, palette)
        px, py = asset.get("placement", [0, 0]); region = views[asset["view"]]
        if px < 0 or py < 0 or px + box[2] > region[2] or py + box[3] > region[3]:
            raise ValueError("The asset's native viewBox and placement must fit its declared view; author at the target dimensions.")
        bindings = asset.get("bindings", {})
        if not isinstance(bindings, dict) or set(bindings) - selectors.keys():
            raise ValueError("Bindings must name actual shape IDs in this SVG, without the asset prefix.")
        indexed = {m["id"]: m for m in marks}
        for selector, change in bindings.items():
            if not isinstance(change, dict) or set(change) - {"attrs", "offset", "entity", "value", "digits", "unit", "text", "textRole"}:
                raise ValueError("Bind attrs, relative offset or direct-value fields; do not replace imported identities or literal paths.")
            if "attrs" in change and not isinstance(change["attrs"], dict): raise ValueError("Bound attrs must be a keyed expression object.")
            if f"{asset['id']}-{selector}" not in indexed and set(change) - {"offset"}:
                raise ValueError("A group binding accepts relative offset only; bind other fields on individual shapes.")
            if not selectors[selector]: raise ValueError("An animated group must contain actual rendered shapes.")
            offset = change.get("offset")
            if offset is not None and (not isinstance(offset, list) or len(offset) != 2): raise ValueError("Relative offset is [dx-expression, dy-expression].")
            for mid in selectors[selector]:
                mark = indexed[mid]
                mark.update({k: copy.deepcopy(v) for k, v in change.items() if k not in ["attrs", "offset"]})
                mark["attrs"].update(copy.deepcopy(change.get("attrs", {})))
                if offset is not None:
                    if mark["kind"] == "path":
                        channels = [(["translateX"], offset[0]), (["translateY"], offset[1])]
                    else:
                        channels = [([k for k in ["x", "cx", "x1", "x2"] if k in mark["attrs"]], offset[0]),
                                    ([k for k in ["y", "cy", "y1", "y2"] if k in mark["attrs"]], offset[1])]
                    for keys, delta in channels:
                        for key in keys: mark["attrs"][key] = {"add": [mark["attrs"].get(key, 0), copy.deepcopy(delta)]}
        for mark in marks:
            if mark["id"] in existing: raise ValueError(f"Imported mark ID collides: {mark['id']}")
            existing.add(mark["id"])
        ports = asset.get("ports", {})
        if not isinstance(ports, dict) or any(not isinstance(p, list) or len(p) != 2 or not all(engine.number(n) for n in p) or not 0 <= p[0] <= box[2] or not 0 <= p[1] <= box[3] for p in ports.values()):
            raise ValueError("Ports must be named [x,y] coordinates inside the native SVG viewBox.")
        provenance.append({"id": asset["id"], "producer": asset["producer"], "purpose": asset["purpose"],
                           "moments": moments, "view": asset["view"], "source": str(source),
                           "sha256": hashlib.sha256(source.read_bytes()).hexdigest(), "viewBox": box,
                           "placement": asset.get("placement", [0, 0]), "ports": ports,
                           "hooks": sorted(bindings), "selectors": selectors, "markIds": [m["id"] for m in marks]})
        # Assets are inserted in plan order behind original dynamic overlays.
        imported.extend(marks)
    brief["marks"] = imported + brief.get("marks", [])
    brief["assetProvenance"] = provenance
    report = engine.preflight(brief, brief_path.parent)
    report.update(assets=provenance, importedMarks=len(imported), output=str(output_path))
    if report["ok"]: engine.write_json(output_path, brief)
    return report


def scaffold(brief_path, plan_path, output_path, view_id=None):
    brief_path, plan_path, output_path = map(lambda p: Path(p).resolve(), [brief_path, plan_path, output_path])
    if any(p.is_relative_to(engine.BUNDLE) for p in [plan_path, output_path]):
        raise ValueError("The skill is read-only; scaffold outputs must be project-owned.")
    if output_path.exists():
        raise ValueError("Scaffold SVG already exists. Edit that authored file or choose a fresh path; do not replace it.")
    brief = json.loads(brief_path.read_text(encoding="utf-8-sig"))
    candidates = [v for v in brief.get("views", []) if v.get("id") == view_id] if view_id else [v for v in brief.get("views", []) if v.get("importance") == "main"]
    if len(candidates) != 1: raise ValueError("Choose exactly one declared view with --view, or declare one main view.")
    view = candidates[0]; region = view.get("region", [])
    if len(region) != 4 or not all(engine.number(n) for n in region) or min(region[2:]) <= 0:
        raise ValueError("Scaffold view needs valid native dimensions.")
    width, height = region[2:]
    title = html.escape(view.get("question", "Explanatory mechanism"))
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width:g} {height:g}" font-family="Explainer">\n<title>{title}</title>\n<desc>Project-owned editable vector asset. Geometry uses this view\'s local coordinates.</desc>\n<!-- Draw recognizable structure, actuator and changing quantity here. Use unique lowercase shape IDs and exact palette paint. -->\n</svg>\n'
    relative = Path(os.path.relpath(output_path, plan_path.parent)).as_posix()
    preserved_plan = plan_path.exists()
    if preserved_plan:
        plan = json.loads(plan_path.read_text(encoding="utf-8-sig"))
        matching = [a for a in plan.get("assets", []) if isinstance(a, dict)
                    and (plan_path.parent / a.get("path", "")).resolve() == output_path]
        if len(matching) != 1 or matching[0].get("view") != view["id"]:
            raise ValueError("Existing plan must name this exact SVG path once in the selected view. Preserve the plan and correct its path/view before scaffolding.")
    else:
        plan = {"schemaVersion": 1, "assets": [{"id": "mechanism", "path": relative, "producer": "standalone-vector",
                 "purpose": view.get("question", "Explain the mechanism."), "view": view["id"], "placement": [0, 0],
                 "moments": ["establish", *[e["id"] for e in brief.get("events", [])], "hold"], "ports": {}, "bindings": {}}]}
    output_path.parent.mkdir(parents=True, exist_ok=True); output_path.write_text(svg, encoding="utf-8")
    if not preserved_plan: engine.write_json(plan_path, plan)
    return {"ok": True, "findings": [], "svg": str(output_path), "plan": str(plan_path), "view": view["id"],
            "planPreserved": preserved_plan, "nativeSize": [width, height],
            "next": "Author the subject's actual geometry and bind moving parts/quantities in the plan before import. An empty scaffold is not a deliverable."}


def main():
    parser = argparse.ArgumentParser(description="Expand palette-normalized editable SVG assets into seekable, audited scene marks.")
    for arg in ["brief", "plan", "output", "report"]: parser.add_argument(f"--{arg}", required=True)
    parser.add_argument("--scaffold", action="store_true", help="Create a blank correctly sized SVG and plan before standalone drawing.")
    parser.add_argument("--view", help="Scaffold view ID; defaults to the main view.")
    args = parser.parse_args()
    try:
        report = scaffold(args.brief, args.plan, args.output, args.view) if args.scaffold else assemble(args.brief, args.plan, args.output)
    except (ValueError, KeyError, TypeError, ET.ParseError) as error:
        report = {"ok": False, "findings": [{"code": "asset", "message": str(error)}]}
    except OSError as error:
        print(f"Asset import infrastructure error: {error}", file=sys.stderr); return 2
    engine.write_json(args.report, report)
    print(json.dumps({"ok": report["ok"], "report": str(Path(args.report).resolve()), "findings": len(report["findings"])}))
    return 0


if __name__ == "__main__": raise SystemExit(main())
