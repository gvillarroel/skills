#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Plan weighted grid regions and assemble portable, static vector fragments."""

from __future__ import annotations

import argparse
import base64
import copy
import hashlib
import json
import math
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import unquote_to_bytes

sys.dont_write_bytecode = True
from route_connectors import NORMALS, anchor, route
from palette_contract import require_color
SVG = "http://www.w3.org/2000/svg"
ET.register_namespace("", SVG)
ET.register_namespace("xlink", "http://www.w3.org/1999/xlink")
ID = re.compile(r"^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$")
URL = re.compile(r"url\(\s*['\"]?([^)'\"]+)['\"]?\s*\)", re.I)
BLOCKED = {"script", "foreignObject", "image", "animate", "animateMotion", "animateTransform", "set", "audio", "video"}


def tag(name):
    return f"{{{SVG}}}{name}"


def local(name):
    return name.rsplit("}", 1)[-1]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def number(value, name, minimum=0, positive=False):
    require(isinstance(value, (int, float)) and not isinstance(value, bool)
            and math.isfinite(value), f"{name} must be a finite number")
    require(value > minimum if positive else value >= minimum, f"{name} is too small")
    return float(value)


def text_value(value, name):
    require(isinstance(value, str) and value.strip(), f"{name} must be nonempty text")
    return value


def identity(value, name):
    require(isinstance(value, str) and ID.fullmatch(value) and len(value) <= 64,
            f"{name} must be lowercase hyphen-case, <=64 characters")
    return value


def semantic_colors(spec):
    """One optional opaque categorical accent per canonical concept."""
    colors = {}
    for concept in spec.get("concepts", []):
        if "color" not in concept:
            continue
        value = concept["color"]
        require(isinstance(value, str) and re.fullmatch(r"#[0-9a-fA-F]{6}", value),
                f"Concept {concept['id']} color must be opaque #RRGGBB")
        value = value.lower()
        require_color(value)
        require(value not in colors.values(), "Use one concept ID for one color meaning; distinct colored concepts need distinct colors")
        colors[concept["id"]] = value
    return colors


def integer(value, name):
    require(isinstance(value, int) and not isinstance(value, bool) and value > 0,
            f"{name} must be a positive integer")
    return value


def tracks(weights, length, gap, origin):
    require(isinstance(weights, list) and weights, "Grid weights must be a nonempty list")
    values = [number(x, "Track weight", positive=True) for x in weights]
    available = length - gap * (len(values) - 1)
    require(available > 0, "Gutters consume the available grid space")
    result = []
    for weight in values:
        size = available * weight / sum(values)
        result.append([origin, size])
        origin += size + gap
    return result


def bounds(xs, ys, span):
    row, col = span["row"] - 1, span["column"] - 1
    endr, endc = row + span["rows"] - 1, col + span["columns"] - 1
    return [xs[col][0], ys[row][0], xs[endc][0] + xs[endc][1] - xs[col][0],
            ys[endr][0] + ys[endr][1] - ys[row][0]]


def resolve_objects(panel):
    objects = panel.get("objects", {})
    require(isinstance(objects, dict), "Panel objects must map semantic IDs to bounds")
    for oid, obj in objects.items():
        identity(oid, "Object ID")
        box = obj["box"]
        require(isinstance(box, list) and len(box)==4, f"Object {oid} needs normalized [x,y,width,height]")
        for value in box:
            number(value, f"{oid}.box")
        require(box[2]>0 and box[3]>0 and box[0]+box[2]<=1.000001 and box[1]+box[3]<=1.000001,
                f"Object {oid} must fit the source viewBox")
        require(obj.get("kind", "node") in {"node", "container"}, f"Invalid object kind: {oid}")
        require(obj.get("shape", "rect") in {"rect", "ellipse"}, f"Unsupported object shape: {oid}")
    ports, bindings = {}, {}
    for name, value in panel.get("ports", {}).items():
        if isinstance(value, dict):
            oid, side = value.get("object"), value.get("side")
            require(oid in objects and side in NORMALS, f"Port {name} needs a known object and left/right/top/bottom side")
            ports[name] = anchor(objects[oid]["box"], side)
            bindings[name] = {"object":oid,"side":side}
        else:
            ports[name] = value
    return objects, ports, bindings


def plan(spec, *, defer_ports=False):
    require(spec.get("version") == 1, "Expected composition version 1")
    for key in ("title", "thesis"):
        text_value(spec.get(key), key)
    c = spec["canvas"]
    for key in ("width", "height", "displayWidth", "minTextPx"):
        number(c[key], f"canvas.{key}", positive=True)
    for key in ("margin", "gap", "titleHeight", "footerHeight"):
        number(c[key], f"canvas.{key}")
    width = c["width"] - 2 * c["margin"]
    height = c["height"] - 2 * c["margin"] - c["titleHeight"] - c["footerHeight"]
    xs = tracks(spec["grid"]["columns"], width, c["gap"], c["margin"])
    ys = tracks(spec["grid"]["rows"], height, c["gap"], c["margin"] + c["titleHeight"])
    concepts = set()
    for concept in spec.get("concepts", []):
        cid = identity(concept["id"], "Concept ID")
        require(cid not in concepts, f"Duplicate concept: {cid}")
        text_value(concept["label"], "Concept label")
        concepts.add(cid)
    colors = semantic_colors(spec)
    occupied, panels, panel_ids = set(), [], set()
    require(isinstance(spec.get("panels"), list) and spec["panels"], "At least one panel is required")
    for panel in spec["panels"]:
        pid = identity(panel["id"], "Panel ID")
        require(pid not in panel_ids, f"Duplicate panel: {pid}")
        panel_ids.add(pid)
        for key in ("title", "question", "claim", "family", "reason", "alternative", "source"):
            text_value(panel.get(key), f"{pid}.{key}")
        span = panel["span"]
        for key in ("row", "column", "rows", "columns"):
            integer(span[key], f"{pid}.span.{key}")
        require(span["row"] + span["rows"] - 1 <= len(ys)
                and span["column"] + span["columns"] - 1 <= len(xs), f"{pid} exceeds grid")
        cells = {(r, col) for r in range(span["row"], span["row"] + span["rows"])
                 for col in range(span["column"], span["column"] + span["columns"])}
        require(not cells & occupied, f"{pid} overlaps another panel's cells")
        occupied |= cells
        require(isinstance(panel.get("concepts", []), list), f"{pid}.concepts must be a list")
        require(set(panel.get("concepts", [])) <= concepts, f"{pid} uses an unknown concept")
        pad = number(panel.get("padding", 12), f"{pid}.padding")
        head = number(panel.get("headerHeight", 34), f"{pid}.headerHeight")
        require(panel.get("frame", "none") in {"none", "line", "fill"}, f"Invalid frame for {pid}")
        box = bounds(xs, ys, span)
        body = [box[0] + pad, box[1] + head + pad, box[2] - 2 * pad, box[3] - head - 2 * pad]
        require(body[2] > 0 and body[3] > 0, f"{pid} has no usable body space")
        require(isinstance(panel.get("ports", {}), dict), f"{pid}.ports must be an object")
        objects, ports, bindings = resolve_objects(panel)
        for name, point in ports.items():
            identity(name, "Port name")
            require(isinstance(point, list) and len(point) == 2, f"Invalid port: {pid}.{name}")
            for n in point:
                require(number(n, "Port coordinate") <= 1, "Ports must be normalized to 0..1")
        panels.append({"id": pid, "family": panel["family"], "panel": box, "body": body,
                       "ports": ports, "concepts": panel.get("concepts", []),
                       "objects": objects, "portBindings": bindings})
    links, link_ids, warnings = spec.get("links", []), set(), []
    by_id = {p["id"]: p for p in panels}
    for link in links:
        lid = identity(link["id"], "Link ID")
        require(lid not in link_ids, f"Duplicate link: {lid}")
        link_ids.add(lid)
        text_value(link.get("relation"), f"{lid}.relation")
        require(isinstance(link.get("directed", False), bool), f"{lid}.directed must be boolean")
        require(isinstance(link.get("label", ""), str), f"{lid}.label must be text")
        for key in ("from", "to"):
            parts = link[key].split(".")
            require(len(parts) == 2 and parts[0] in by_id, f"Unknown endpoint panel: {link[key]}")
            identity(parts[1], "Endpoint port")
            if parts[1] not in by_id[parts[0]]["ports"]:
                require(defer_ports, f"Unknown endpoint: {link[key]}")
                warnings.append(f"Deferred endpoint coordinates: {link[key]}")
        require(isinstance(link.get("via", []), list), f"{lid}.via must be a list")
        for point in link.get("via", []):
            require(isinstance(point, list) and len(point) == 2, "Waypoints need [x,y]")
            for n, limit in zip(point, (c["width"], c["height"])):
                require(number(n, "Waypoint") <= limit, "Waypoint outside canvas")
    report = {"version": 1, "title": spec["title"], "canvas": c, "tracks": {"columns": xs, "rows": ys},
              "panels": panels, "links": [], "warnings": warnings}
    if colors:
        report["semanticColors"] = colors
    return report


def parse_svg(path, allow_style=False):
    return parse_svg_bytes(path.read_bytes(), allow_style=allow_style)


def parse_svg_bytes(raw, allow_style=False, depth=0):
    require(len(raw) <= 8 * 1024 * 1024 and depth <= 6, "SVG import size or nesting limit exceeded")
    require(not re.search(br"<!\s*(DOCTYPE|ENTITY)", raw, re.I), "SVG entity declarations are unsupported")
    root = ET.fromstring(raw)
    require(root.tag == tag("svg"), "Expected SVG namespace and root")
    for parent in list(root.iter()):
        for index, child in enumerate(list(parent)):
            if child.tag != tag("image"):
                continue
            href = child.get("href", child.get("{http://www.w3.org/1999/xlink}href", ""))
            require(href.startswith("data:image/svg+xml"), "Only embedded vector SVG images can be inlined; raster/external images are unsupported")
            header, separator, encoded = href.partition(",")
            require(separator and header.lower() in {"data:image/svg+xml", "data:image/svg+xml;base64", "data:image/svg+xml;charset=utf-8"}, "Unsupported embedded SVG encoding")
            decoded = base64.b64decode(encoded, validate=True) if header.endswith(";base64") else unquote_to_bytes(encoded)
            nested, _, _ = parse_svg_bytes(decoded, allow_style=allow_style, depth=depth + 1)
            prefix = f"embedded-{hashlib.sha256(raw).hexdigest()[:10]}-{sum(1 for e in root.iter() if e is not child)}-{index}-"
            # Distinguish same-size images under different parents without random IDs.
            prefix += str(list(root.iter()).index(child)) + "-"
            nested = namespace(nested, prefix)
            require(child.get("width") and child.get("height"), "Embedded SVG image needs explicit width and height")
            wrapper = ET.Element(tag("g"))
            for key, value in child.attrib.items():
                if local(key) not in {"href", "x", "y", "width", "height", "preserveAspectRatio"}:
                    wrapper.set(key, value)
            for key in ("x", "y", "width", "height", "preserveAspectRatio"):
                nested.set(key, child.get(key, "xMidYMid meet" if key == "preserveAspectRatio" else "0"))
            wrapper.append(nested)
            parent.remove(child)
            parent.insert(index, wrapper)
    ids = set()
    for el in root.iter():
        kind = local(el.tag)
        require(el.tag.startswith(f"{{{SVG}}}"), f"Non-SVG element: {kind}")
        require(kind not in BLOCKED, f"Unsupported SVG element: {kind}; export native static vectors")
        if kind == "style":
            require(allow_style, "Stylesheet found; use audit_diagram.py prepare first")
            css = el.text or ""
            require(not re.search(r"@import|@font-face", css, re.I), "External CSS is unsupported")
            for ref in URL.findall(css):
                require(ref.startswith("#"), "External CSS resources are unsupported")
        eid = el.get("id")
        if eid:
            require(eid not in ids, f"Duplicate source ID: {eid}")
            ids.add(eid)
        for key, value in el.attrib.items():
            k = local(key)
            require(not k.lower().startswith("on"), f"Event handler unsupported: {k}")
            require(k != "base", "SVG base URI is unsupported")
            if k == "href":
                require(value.startswith("#"), "External SVG references are unsupported")
            require(not re.search(r"(?:animation|transition)\s*:", value, re.I), "Animated inline style is unsupported")
            for ref in URL.findall(value):
                require(ref.startswith("#"), "External SVG resources are unsupported")
    for el in root.iter():
        for key, value in el.attrib.items():
            refs = URL.findall(value)
            if local(key) == "href":
                refs.append(value)
            for ref in refs:
                require(ref[1:] in ids, f"Unresolved SVG reference: {ref}")
            if local(key) in {"aria-labelledby", "aria-describedby"}:
                require(all(ref in ids for ref in value.split()), "Unresolved accessible SVG reference")
    vb = root.get("viewBox", "").replace(",", " ").split()
    require(len(vb) == 4, "SVG needs a numeric four-value viewBox")
    viewbox = [float(n) for n in vb]
    require(all(math.isfinite(n) for n in viewbox) and viewbox[2] > 0 and viewbox[3] > 0,
            "SVG viewBox dimensions must be positive and finite")
    return root, viewbox, hashlib.sha256(raw).hexdigest()


def namespace(root, prefix):
    ids = {el.get("id"): prefix + el.get("id") for el in root.iter() if el.get("id")}
    for el in root.iter():
        for key, value in list(el.attrib.items()):
            if key == "id":
                el.set(key, ids[value])
            elif local(key) == "href":
                el.set(key, "#" + ids[value[1:]])
            elif key in {"aria-labelledby", "aria-describedby"}:
                el.set(key, " ".join(ids[x] for x in value.split()))
            else:
                el.set(key, URL.sub(lambda m: f"url(#{ids[m.group(1)[1:]]})", value))
    return root


def element(parent, kind, attrs=None, text=None):
    child = ET.SubElement(parent, tag(kind), {k: str(v) for k, v in (attrs or {}).items()})
    if text is not None:
        child.text = text
    return child


def write_target(path, overwrite):
    require(overwrite or not path.exists(), f"Output exists: {path}; use --overwrite for your generated file")
    path.parent.mkdir(parents=True, exist_ok=True)


def compose(spec, spec_path):
    report = plan(spec)
    c = spec["canvas"]
    scale_display = c["width"] / c["displayWidth"]
    base_font = max(14, c["minTextPx"] * scale_display)
    root = ET.Element(tag("svg"), {"viewBox": f"0 0 {c['width']} {c['height']}",
        "width": str(c["width"]), "height": str(c["height"]), "role": "img", "data-colorset": "colorset2",
        "aria-labelledby": "composition-title composition-desc", "font-family": "Arial, sans-serif",
        "font-size": str(base_font), "fill": "#1c1c1c"})
    element(root, "title", {"id": "composition-title"}, spec["title"])
    element(root, "desc", {"id": "composition-desc"}, spec["thesis"])
    element(root, "rect", {"width": c["width"], "height": c["height"], "fill": "#ffffff"})
    element(root, "text", {"x": c["margin"], "y": c["margin"] + base_font * 1.6,
                            "font-size": base_font * 1.7, "font-weight": 700}, spec["title"])
    defs = element(root, "defs")
    marker = element(defs, "marker", {"id": "composition-arrow", "viewBox": "0 0 10 10",
        "refX": 9, "refY": 5, "markerWidth": 6, "markerHeight": 6, "markerUnits":"userSpaceOnUse", "orient": "auto-start-reverse"})
    element(marker, "path", {"d": "M 1 1 L 9 5 L 1 9 Z", "fill": "#696969"})
    port_positions, port_bindings, scene_objects = {}, {}, {}
    for panel, geo in zip(spec["panels"], report["panels"]):
        source = Path(panel["source"])
        source = source if source.is_absolute() else spec_path.parent / source
        fragment, vb, digest = parse_svg(source)
        fragment = namespace(copy.deepcopy(fragment), f"asset-{panel['id']}-")
        bx, by, bw, bh = geo["body"]
        fit = min(bw / vb[2], bh / vb[3])
        fw, fh = vb[2] * fit, vb[3] * fit
        fx, fy = bx + (bw - fw) / 2, by + (bh - fh) / 2
        geo.update({"source": panel["source"], "sourceSha256": digest, "viewBox": vb,
                    "scale": fit, "fitted": [fx, fy, fw, fh], "mappedPorts": {}})
        geo["mappedObjects"] = {}
        for oid,obj in geo["objects"].items():
            u,v,ow,oh = obj["box"]
            mapped={**obj,"box":[fx+u*fw,fy+v*fh,ow*fw,oh*fh]}
            scene_objects[f"{panel['id']}.{oid}"]=mapped
            geo["mappedObjects"][oid]=mapped
        for i,box in enumerate(panel.get('routingObstacles',[])):
            require(len(box)==4 and all(isinstance(v,(int,float)) and math.isfinite(v) for v in box) and box[2]>0 and box[3]>0,
                    'Routing obstacle must be a finite normalized [x,y,width,height] box')
            u,v,ow,oh=box;mapped=[fx+u*fw,fy+v*fh,ow*fw,oh*fh]
            # Labels wholly inside a leaf node are already protected by it.
            if any(o.get('kind','node')=='node' and mapped[0]>=o['box'][0] and mapped[1]>=o['box'][1] and
                   mapped[0]+mapped[2]<=o['box'][0]+o['box'][2] and mapped[1]+mapped[3]<=o['box'][1]+o['box'][3]
                   for o in geo['mappedObjects'].values()):continue
            scene_objects[f"routing:{panel['id']}:{i}"]={'box':mapped,'kind':'node'}
        px,py,pw,ph=geo['panel']
        scene_objects[f"heading:{panel['id']}"]={'box':[px,py,pw,panel.get('headerHeight',34)],'kind':'node'}
        if fw * fh / (bw * bh) < 0.45:
            report["warnings"].append(f"{panel['id']}: poor aspect fit; consider source geometry or grid tracks")
        group = element(root, "g", {"id": f"panel-{panel['id']}", "data-panel-id": panel["id"],
            "data-family": panel["family"], "data-body": json.dumps(geo["body"]),
            "data-panel-box": json.dumps(geo["panel"]), "role": "group",
            "aria-labelledby": f"panel-title-{panel['id']}"})
        element(group, "desc", text=f"{panel['question']} {panel['claim']}")
        x, y, w, h = geo["panel"]
        frame = panel.get("frame", "none")
        if frame != "none":
            element(group, "rect", {"x": x, "y": y, "width": w, "height": h, "rx": 6,
                "fill": "#f7f7f7" if frame == "fill" else "none",
                "stroke": "#e7e7e7" if frame == "line" else "none"})
        element(group, "text", {"id": f"panel-title-{panel['id']}", "data-panel-title": "true",
            "x": x + panel.get("padding", 12), "y": y + base_font * 1.4,
            "font-size": base_font * 1.2, "font-weight": 700}, panel["title"])
        # Nested SVG preserves source-root attributes, inheritance, and viewBox coordinates.
        fragment.set("x", str(fx))
        fragment.set("y", str(fy))
        fragment.set("width", str(fw))
        fragment.set("height", str(fh))
        fragment.set("preserveAspectRatio", "xMidYMid meet")
        # Nested SVG viewports normally clip; preserve intentional renderer clipping.
        fragment.set("overflow", fragment.get("overflow", "hidden"))
        fragment.set("data-source", panel["id"])
        group.append(fragment)
        for name, point in geo["ports"].items():
            position = [fx + point[0] * fw, fy + point[1] * fh]
            port_positions[f"{panel['id']}.{name}"] = position
            geo["mappedPorts"][name] = position
            if name in geo["portBindings"]:
                binding=geo["portBindings"][name]
                port_bindings[f"{panel['id']}.{name}"]={**binding,"object":f"{panel['id']}.{binding['object']}"}
    previous_routes=[]
    panel_boxes={p["id"]:p["panel"] for p in report["panels"]}
    for link in spec.get("links", []):
        start, end = port_positions[link["from"]], port_positions[link["to"]]
        endpoints=[port_bindings.get(link[key]) for key in ("from","to")]
        preferred=[(start[0]+end[0])/2,(start[1]+end[1])/2]
        a,b=[panel_boxes[link[key].split('.')[0]] for key in ("from","to")]
        for axis in (0,1):
            if a[axis]+a[axis+2]<=b[axis]:preferred[axis]=(a[axis]+a[axis+2]+b[axis])/2
            elif b[axis]+b[axis+2]<=a[axis]:preferred[axis]=(b[axis]+b[axis+2]+a[axis])/2
        points = route(start,end,scene_objects,endpoints,canvas=(c["width"],c["height"]),
                       previous=previous_routes,via=link.get("via"),preferred=preferred)
        previous_routes.append(points)
        d = "M " + " L ".join(f"{p[0]:.3f},{p[1]:.3f}" for p in points)
        g = element(root, "g", {"id": f"relation-{link['id']}", "data-relation-id": link["id"],
            "data-endpoints": json.dumps(endpoints)})
        element(g, "title", text=link["relation"])
        attrs = {"d": d, "fill": "none", "stroke": "#696969", "stroke-width": 1.6}
        if link.get("directed", False):
            attrs["marker-end"] = "url(#composition-arrow)"
        element(g, "path", attrs)
        label = link.get("label", link["relation"])
        if label:
            lengths = [math.dist(a, b) for a, b in zip(points, points[1:])]
            idx = lengths.index(max(lengths))
            lx, ly = [(a + b) / 2 for a, b in zip(points[idx], points[idx + 1])]
            element(g, "text", {"x": lx, "y": ly - 7, "text-anchor": "middle",
                "paint-order": "stroke", "stroke": "#ffffff", "stroke-width": 5,
                "stroke-linejoin": "round"}, label)
        report["links"].append({**link, "points": points, "endpoints": endpoints})
    if spec.get("note"):
        element(root, "text", {"x": c["margin"], "y": c["height"] - c["margin"],
                               "font-size": base_font}, spec["note"])
    element(root, "metadata", {"id": "composition-report"}, json.dumps(report, ensure_ascii=False))
    return ET.tostring(root, encoding="unicode", xml_declaration=True), report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["layout", "compose"])
    parser.add_argument("--spec", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--report", type=Path)
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--inspect", action="store_true", help="Save authoring diagnostics without failing; require a clean final run without this flag")
    args = parser.parse_args()
    report_writable = False
    try:
        spec = json.loads(args.spec.read_text(encoding="utf-8-sig"))
        output_path = args.output.resolve()
        protected = {args.spec.resolve(), *( (args.spec.parent / p["source"]).resolve() for p in spec["panels"])}
        require(output_path not in protected, "Output cannot replace the spec or a source asset")
        if args.report:
            require(args.report.resolve() not in protected | {output_path}, "Report path collides with an input/output")
            write_target(args.report, args.overwrite)
            report_writable = True
        require(not args.inspect or args.report is not None, "Inspection requires --report for persisted diagnostics")
        if args.command == "layout":
            result = plan(spec, defer_ports=True)
            payload = json.dumps(result, indent=2, ensure_ascii=False) + "\n"
        else:
            require(args.report is not None, "compose requires --report")
            payload, result = compose(spec, args.spec)
        result["ok"] = True
        for path in [args.output] + ([args.report] if args.report else []):
            write_target(path, args.overwrite)
        args.output.write_text(payload, encoding="utf-8")
        if args.report:
            args.report.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(json.dumps({"ok": True, "output": str(args.output), "panels": len(result["panels"]),
                          "warnings": result["warnings"]}))
        return 0
    except (ValueError, KeyError, TypeError, OSError, ET.ParseError) as exc:
        result = {"ok": False, "error": str(exc)}
        if report_writable:
            try:
                args.report.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
            except OSError as report_error:
                result["reportError"] = str(report_error)
                report_writable = False
        print(json.dumps(result))
        return 0 if args.inspect and report_writable else 1


if __name__ == "__main__":
    raise SystemExit(main())
