#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["Pillow>=11,<13"]
# ///
"""Compose editable calibrated inlet or vehicle artwork from a project-owned rate/integral brief."""
from __future__ import annotations

import argparse
import copy
import json
import math
import os
from pathlib import Path
import re
import sys
import xml.etree.ElementTree as ET

sys.dont_write_bytecode = True
import explainer as engine
import import_assets as importer

NUMBER = re.compile(r"[-+]?(?:\d*\.\d+|\d+\.?\d*)(?:[eE][-+]?\d+)?")


def expression(op, *values):
    return {op: list(values)}


def fmt(value):
    # Round-trip native dimensions exactly; rounded viewBoxes can exceed their views.
    return str(float(value)) if value != int(value) else str(int(value))


class Drawing:
    def __init__(self, scale, palette, title):
        self.scale, self.palette = scale, palette
        self.root = ET.Element("svg", xmlns="http://www.w3.org/2000/svg",
                               viewBox=f"0 0 {fmt(1030*scale)} {fmt(920*scale)}",
                               **{"font-family": "Explainer", "fill": "none", "stroke": "none"})
        ET.SubElement(self.root, "title").text = title
        ET.SubElement(self.root, "desc").text = "Editable original geometry with state-driven hooks; no autonomous animation clock."
        self.parent = self.root

    def add(self, kind, identity, *, fill="none", stroke=None, sw=3, text=None, **attrs):
        if stroke is None:
            stroke = "none" if fill != "none" else "ink"
        cooked = {"id": identity, "fill": self.palette.get(fill, fill), "stroke": self.palette.get(stroke, stroke),
                  "stroke-width": fmt(sw*self.scale), "stroke-linecap": "round", "stroke-linejoin": "round"}
        for key, value in attrs.items():
            key = key.replace("_", "-")
            if key == "d": value = NUMBER.sub(lambda m: fmt(float(m[0])*self.scale), value)
            elif isinstance(value, (int, float)): value = fmt(value*self.scale)
            cooked[key] = str(value)
        node = ET.SubElement(self.parent, kind, cooked)
        if text is not None: node.text = text
        return node

    def label(self, identity, x, y, text, size=32, fill="ink", anchor="start"):
        return self.add("text", identity, fill=fill, stroke="none", x=x, y=y,
                        font_size=size, text_anchor=anchor, text=text)

    def serialize(self):
        ET.indent(self.root)
        return ET.tostring(self.root, encoding="unicode") + "\n"


def chart_marks(view, source, unit, limit, duration, paint, scale):
    def label(identity, x, y, text, anchor="start"):
        return {"id": f"{view}-{identity}", "view": view, "kind": "text",
                "attrs": {"x": x*scale, "y": y*scale, "fontSize": 32*scale},
                "text": text, "anchor": anchor, "fill": "ink"}
    x, y, width, height = 66, 66, 500, 228
    marks = []
    for i, value in enumerate([0, limit/2, limit]):
        py = y+height-height*value/limit
        marks += [{"id": f"{view}-grid-{i}", "view": view, "kind": "line",
                   "attrs": {"x1": x*scale, "x2": (x+width)*scale, "y1": py*scale, "y2": py*scale},
                   "fill": "none", "stroke": "line", "strokeWidth": 2*scale},
                  label(f"tick-{i}", x-15, py+10, fmt(value), "end")]
    for i, value in enumerate([0, duration/2, duration]):
        px = x+width*value/duration
        marks += [label(f"time-{i}", px, 345, fmt(value), "middle")]
    marks += [label("unit", x, 35, unit), label("seconds", 614, 345, "s", "end"),
              {"id": f"{view}-history", "view": view, "kind": "plot",
               "attrs": {"x": x*scale, "y": y*scale, "width": width*scale, "height": height*scale},
               "xValue": "time", "yValue": source, "xDomain": [0, duration], "yDomain": [0, limit],
               "samples": 240, "fill": "none", "stroke": paint, "strokeWidth": 5*scale}]
    return marks


def inlet_art(draw, source, quantity, maximum, capacity, fps, quantity_role, source_label, quantity_label):
    s, e = draw.scale, expression
    draw.add("path", "tank-shell", d="M640 312 V780 C640 832 940 832 940 780 V312 Z", fill="muted", sw=5)
    draw.add("ellipse", "tank-cap", cx=790, cy=312, rx=150, ry=38, fill="muted", sw=5)
    # The rectangular cutaway and its graduated ruler have identical zero/capacity edges.
    draw.add("rect", "fluid", x=655, y=610, width=270, height=170, fill=quantity_role, stroke="none")
    draw.add("line", "waterline", x1=655, x2=925, y1=610, y2=610, stroke=quantity_role, sw=5)
    draw.add("path", "tank-bottom", d="M640 780 C640 825 940 825 940 780", sw=5)
    draw.add("path", "tank-feet", d="M665 810 V850 H700 V820 M880 820 V850 H915 V810", sw=5)
    draw.add("path", "capacity-rail", d="M960 314 H973 V780 H960", stroke="muted", sw=2)
    for i in range(5):
        value, y = capacity*i/4, 780-466*i/4
        draw.add("line", f"capacity-tick-{i}", x1=955, x2=979, y1=y, y2=y, stroke="muted", sw=2)
        draw.label(f"capacity-label-{i}", 1020, y+10, fmt(value), anchor="end")
    draw.label("capacity-unit", 975, 257, "L")
    draw.add("rect", "pipe-shell", x=100, y=305, width=555, height=50, rx=25, fill="muted", sw=3)
    draw.add("rect", "pipe-channel", x=101, y=317, width=554, height=26, rx=13, fill="surface", stroke="none")
    draw.add("path", "valve-body", d="M305 283 H405 L430 305 V355 L405 377 H305 L280 355 V305 Z", fill="muted", sw=5)
    draw.add("path", "open-channel", d="M280 317 H430 M280 343 H430", stroke="line", sw=2)
    draw.add("line", "valve-gate", x1=342, y1=306, x2=368, y2=354, stroke="primary", sw=10)
    draw.add("circle", "gate-bearing", cx=355, cy=330, r=5, fill="ink", stroke="none")
    draw.add("line", "valve-stem", x1=355, y1=230, x2=355, y2=283, sw=6)
    draw.add("circle", "wheel-rim", cx=355, cy=180, r=50, stroke="primary", sw=6)
    # Asymmetric spoke makes different actuator states distinguishable in a still.
    draw.add("path", "wheel", d="M-50 0 H50 M0 -50 V50 M-35 -35 L35 35 M-35 35 L35 -35 M20 -8 L43 -8",
             transform=f"translate({fmt(355*s)} {fmt(180*s)})", stroke="primary", sw=4)
    draw.add("circle", "wheel-hub", cx=355, cy=180, r=9, fill="primary", stroke="none")
    draw.add("path", "flow-direction", d="M130 405 H235 M225 395 L235 405 L225 415", sw=3)
    draw.label("input-value", 485, 252, source_label, size=40, fill="primary")
    draw.label("quantity-value", 640, 905, quantity_label, size=40, fill=quantity_role)
    level = e("sub", 780*s, e("mul", quantity, 466*s/capacity))
    angle = e("mul", e("sub", 90, e("mul", source, 80/maximum)), math.pi/180)
    vx, vy = e("mul", 27*s, e("cos", angle)), e("mul", 27*s, e("sin", angle))
    bindings = {"fluid": {"attrs": {"y": level, "height": e("mul", quantity, 466*s/capacity)}},
                "waterline": {"attrs": {"y1": level, "y2": level}},
                "valve-gate": {"attrs": {"x1": e("sub", 355*s, vx), "x2": e("add", 355*s, vx),
                                          "y1": e("sub", 330*s, vy), "y2": e("add", 330*s, vy)}},
                "wheel": {"attrs": {"rotation": e("mul", source, 150/maximum)}},
                "input-value": {"value": source, "unit": "L/s", "digits": 1},
                "quantity-value": {"value": quantity, "unit": "L", "digits": 1}}
    # Keep four samples per repeated-marker spacing at maximum input. A correct
    # integral alone does not prevent a low-fps transport loop from looking reversed.
    cycles_per_unit = min(6/capacity, fps/(4*9*maximum))
    for i in range(9):
        draw.add("circle", f"tracer-{i}", cx=110+530*i/9, cy=330, r=5, fill=quantity_role, stroke="none")
        # Quantitative phase is proportional to accumulated volume, not instantaneous rate*time.
        bindings[f"tracer-{i}"] = {"attrs": {
            "cx": e("add", 110*s, e("mul", 530*s, e("mod", e("add", e("mul", quantity, cycles_per_unit), i/9), 1))),
            "r": e("mul", 6*s, e("sqrt", e("div", source, maximum)))}}
    return bindings, {"supply": [100*s,330*s], "tank-inlet": [655*s,330*s]}, {
        "capacity": capacity, "zeroY": 780*s, "capacityY": 314*s, "pixelsPerUnit": 466*s/capacity,
        "tracerMeaning": "Qualitative transport; phase follows the analytic integral and stops at zero input.",
        "tracerCount":9,"tracerCyclesPerUnit":cycles_per_unit,"maximumPhaseAdvancePerFrame":cycles_per_unit*maximum/fps}


def vehicle_art(draw, source, quantity, maximum, extent, quantity_role, source_label, quantity_label):
    s, e = draw.scale, expression
    pixels = (1030-385-35)*s/extent
    draw.add("line", "road", x1=80, x2=1005, y1=460, y2=460, stroke="ink", sw=4)
    for i in range(5):
        px = 180+(1030-385-35)*i/4
        draw.add("line", f"distance-tick-{i}", x1=px, x2=px, y1=470, y2=485, stroke="muted", sw=2)
        draw.label(f"distance-label-{i}", px, 530, fmt(extent*i/4), anchor="middle")
    draw.label("distance-unit", 850, 530, "m")
    draw.label("input-value", 100, 170, source_label, size=40, fill="primary")
    draw.label("quantity-value", 100, 700, quantity_label, size=40, fill=quantity_role)
    draw.add("line", "velocity-shaft", x1=110, y1=255, x2=270, y2=255, stroke="primary", sw=6)
    draw.add("line", "velocity-head-up", x1=255, y1=242, x2=270, y2=255, stroke="primary", sw=6)
    draw.add("line", "velocity-head-down", x1=255, y1=268, x2=270, y2=255, stroke="primary", sw=6)
    draw.parent = ET.SubElement(draw.root, "g", id="car")
    draw.add("path", "car-body", d="M95 405 L110 365 L172 355 L202 310 H281 L319 355 L366 365 L385 406 V431 H95 Z", fill="muted", sw=5)
    draw.add("path", "rear-window", d="M184 350 L211 320 H236 V350 Z", fill="quiet", sw=3)
    draw.add("path", "front-window", d="M245 320 H274 L305 350 H245 Z", fill="quiet", sw=3)
    draw.add("line", "door", x1=245, x2=245, y1=357, y2=416, stroke="line", sw=2)
    draw.add("line", "door-handle", x1=256, x2=275, y1=369, y2=369, sw=3)
    draw.add("rect", "front-lamp", x=365, y=378, width=15, height=11, rx=3, fill="quiet", sw=2)
    draw.add("line", "bumper", x1=366, x2=383, y1=414, y2=414, sw=4)
    bindings = {"car": {"offset": [e("mul", quantity, pixels), 0]},
                "input-value": {"value": source, "unit": "m/s", "digits": 1},
                "quantity-value": {"value": quantity, "unit": "m", "digits": 1}}
    for name, cx in [("rear",180),("front",330)]:
        draw.add("circle", f"{name}-tyre", cx=cx, cy=425, r=35, fill="ink", sw=5)
        draw.add("circle", f"{name}-rim", cx=cx, cy=425, r=25, fill="surface", sw=3)
        draw.add("path", f"{name}-spokes", d="M-23 0 H23 M0 -23 V23 M0 0 L15 15",
                 transform=f"translate({fmt(cx*s)} {fmt(425*s)})", stroke="ink", sw=3)
        draw.add("circle", f"{name}-hub", cx=cx, cy=425, r=5, fill="ink", stroke="none")
        bindings[f"{name}-spokes"] = {"attrs": {"rotation": e("mul", quantity, pixels/(35*s)*180/math.pi)}}
    draw.parent = draw.root
    draw.add("path", "position-pointer", d="M-9 0 L0 -12 L9 0 Z", transform=f"translate({fmt(180*s)} {fmt(567*s)})",
             fill=quantity_role, stroke="none")
    bindings["position-pointer"] = {"attrs": {"translateX": e("add", 180*s, e("mul", quantity, pixels))}}
    head = e("add", 110*s, e("mul", source, 350*s/maximum))
    bindings["velocity-shaft"] = {"attrs": {"x2": head}}
    ratio = e("div",source,maximum)
    back = e("sub",head,e("mul",15*s,ratio))
    bindings["velocity-head-up"] = {"attrs": {"x1":back,"x2":head,"y1":e("sub",255*s,e("mul",13*s,ratio))}}
    bindings["velocity-head-down"] = {"attrs": {"x1":back,"x2":head,"y1":e("add",255*s,e("mul",13*s,ratio))}}
    return bindings, {"distance-zero": [180*s,460*s]}, {
        "extent": extent, "pixelsPerUnit": pixels, "distanceAnchor": "rear wheel centre",
        "wheelRadius": 35*s, "roadY": 460*s, "wheelRotation": "Clockwise distance/radius in downward-y SVG coordinates."}


def compose(brief_path, output_path, svg_path, plan_path, *, kind, source=None, quantity=None,
            capacity=None, source_label=None, quantity_label=None, expected_palette=None):
    paths = list(map(lambda p: Path(p).resolve(), [brief_path, output_path, svg_path, plan_path]))
    brief_path, output_path, svg_path, plan_path = paths
    if len(set(paths)) != 4: raise ValueError("Input brief, output brief, SVG and plan paths must be distinct.")
    if any(p.is_relative_to(engine.BUNDLE) for p in paths[1:]): raise ValueError("The skill is read-only; use project-owned output paths.")
    if any(p.exists() for p in paths[1:]): raise ValueError("Composition outputs already exist. Preserve them; use fresh paths or edit the project-owned assets by ID.")
    brief = copy.deepcopy(json.loads(brief_path.read_text(encoding="utf-8-sig")))
    source = source or (next(iter(brief["sources"])) if len(brief["sources"]) == 1 else None)
    quantity = quantity or next((k for k,v in brief["derived"].items() if v["expr"] == {"integrate": [source,"time"]}), None)
    if source not in brief["sources"] or quantity not in brief["derived"]: raise ValueError("Choose an existing source and its accumulated quantity with --source and --quantity.")
    if brief["derived"][quantity]["expr"] != {"integrate": [source,"time"]}: raise ValueError("This composer needs accumulation from zero of one source, with no outflow/losses. Author other models separately.")
    domain, output = brief["sources"][source]["domain"], brief["output"]
    if domain[0] != 0 or domain[1] <= 0: raise ValueError("This composer needs a nonnegative source with domain starting at zero.")
    maximum, duration = domain[1], output["duration"]
    if not engine.number(duration) or duration <= 0: raise ValueError("Duration must be positive and finite.")
    if output["width"] < 960 or output["height"] < 540 or output["width"] < output["height"]:
        raise ValueError("This three-view composition needs a landscape canvas of at least 960 by 540. Use custom geometry for smaller or portrait output.")
    units = ("L/s","L") if kind == "inlet" else ("m/s","m")
    if (brief["sources"][source]["unit"], brief["derived"][quantity]["unit"]) != units:
        raise ValueError(f"{kind} requires units {units}; choose matching IDs or author another mechanism.")
    extent = maximum*duration
    if capacity is not None and (not engine.number(capacity) or capacity < extent):
        raise ValueError("Capacity must cover maximum input times duration; do not hide overflow with a clamp.")
    if kind == "vehicle" and capacity is not None: raise ValueError("Vehicle distance extent comes from its control domain and duration, not tank capacity.")
    limit = capacity if capacity is not None else extent
    scale = min(output["width"]/1920,output["height"]/1080)
    ox, oy = (output["width"]-1920*scale)/2, (output["height"]-1080*scale)/2
    mode = brief["palette"].get("mode","colorset1")
    if expected_palette is not None and expected_palette != mode:
        raise ValueError("The palette assertion differs from the input model. Set the requested palette in the numerical model; composition does not silently replace it.")
    roles = json.loads((engine.BUNDLE/"assets/palettes/colorsets.json").read_text(encoding="utf-8"))["colorsets"][mode]["roles"]
    quantity_role = "secondary" if mode == "colorset2" else "primary"
    brief["views"] = [{"id":"mechanism","question":"What does the initiating control change in the actual mechanism?","region":[ox+65*scale,oy+55*scale,1030*scale,920*scale],"importance":"main"},
                      {"id":"rate","question":"How does the input change over time?","region":[ox+1190*scale,oy+85*scale,650*scale,390*scale],"importance":"support"},
                      {"id":"history","question":"How does accumulated input change the total?","region":[ox+1190*scale,oy+590*scale,650*scale,390*scale],"importance":"support"}]
    brief["marks"] = chart_marks("rate",source,units[0],maximum,duration,"primary",scale) + chart_marks("history",quantity,units[1],limit,duration,quantity_role,scale)
    draw = Drawing(scale,roles,"Controlled inlet, connected transport and calibrated reservoir" if kind == "inlet" else "Changing-speed vehicle, wheel contacts and calibrated distance ruler")
    producer = "bundled calibrated vector composer; original editable geometry, no companion skill invoked"
    source_label = source_label or ("Flow" if kind == "inlet" else "Speed")
    quantity_label = quantity_label or ("Stored" if kind == "inlet" else "Distance")
    if len(source_label) > 20 or len(quantity_label) > 20: raise ValueError("Use short direct labels; keep prose outside the film.")
    if kind == "inlet": bindings,ports,calibration = inlet_art(draw,source,quantity,maximum,limit,output["fps"],quantity_role,source_label,quantity_label)
    else: bindings,ports,calibration = vehicle_art(draw,source,quantity,maximum,extent,quantity_role,source_label,quantity_label)
    brief["composition"] = {"producer":producer,"kind":kind,"source":source,"quantity":quantity,
                            "calibration":calibration,"modelScope":"Imposed nonnegative rate, analytic accumulation from zero; illustrative geometry."}
    if kind == "inlet": brief["composition"]["modelScope"] += " Constant cross-section, no outflow; actuator opening is illustrative, not a measured hydraulic law."
    asset = {"id":"mechanism","path":Path(os.path.relpath(svg_path,plan_path.parent)).as_posix(),"producer":producer,
             "purpose":"Recognizable causal mechanism, calibrated measurement and complementary synchronized consequences.",
             "view":"mechanism","placement":[0,0],"moments":["establish",*[e["id"] for e in brief["events"]],"hold"],"ports":ports,"bindings":bindings}
    # Validate generated geometry and bindings in memory before any deliverable is written.
    raw = draw.serialize()
    class Source:
        def read_text(self, **kwargs): return raw
    palette = {"roles":roles}
    marks,box,selectors = importer.svg_marks(Source(),asset,palette)
    indexed = {m["id"]:m for m in marks}
    for selector, change in bindings.items():
        for identity in selectors[selector]:
            mark = indexed[identity]
            mark.update({k:copy.deepcopy(v) for k,v in change.items() if k not in ["attrs","offset"]})
            mark["attrs"].update(copy.deepcopy(change.get("attrs",{})))
            if "offset" in change:
                for axis,keys in enumerate((["translateX"] if mark["kind"] == "path" else [k for k in ["x","cx","x1","x2"] if k in mark["attrs"]],
                                            ["translateY"] if mark["kind"] == "path" else [k for k in ["y","cy","y1","y2"] if k in mark["attrs"]])):
                    for key in keys: mark["attrs"][key] = expression("add",mark["attrs"].get(key,0),copy.deepcopy(change["offset"][axis]))
    expanded = copy.deepcopy(brief); expanded["marks"] = marks+brief["marks"]
    report = engine.preflight(expanded,brief_path.parent)
    if not report["ok"]: return report
    svg_path.parent.mkdir(parents=True,exist_ok=True); svg_path.write_text(raw,encoding="utf-8")
    engine.write_json(output_path,brief); engine.write_json(plan_path,{"schemaVersion":1,"assets":[asset]})
    return {"ok":True,"findings":[],"brief":str(output_path),"svg":str(svg_path),"plan":str(plan_path),
            "kind":kind,"nativeSize":box[2:],"calibration":calibration,"next":"Import this scene and plan, build, inspect the still, audit, check, render and verify the exact MP4."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ["brief","output","svg","plan","report"]: parser.add_argument(f"--{name}",required=True)
    parser.add_argument("--kind",choices=["inlet","vehicle"],required=True)
    for name in ["source","quantity","source-label","quantity-label"]: parser.add_argument(f"--{name}")
    parser.add_argument("--capacity",type=float)
    parser.add_argument("--palette",choices=["colorset1","colorset2"],help="Optional assertion; must match the input model's palette.")
    args = parser.parse_args()
    try:
        report = compose(args.brief,args.output,args.svg,args.plan,kind=args.kind,source=args.source,
                         quantity=args.quantity,capacity=args.capacity,source_label=args.source_label,quantity_label=args.quantity_label,expected_palette=args.palette)
    except (ValueError,KeyError,TypeError,ET.ParseError) as error:
        report = {"ok":False,"findings":[{"code":"composition","message":str(error)}]}
    except OSError as error:
        print(f"Composition infrastructure error: {error}",file=sys.stderr); return 2
    engine.write_json(args.report,report)
    print(json.dumps({"ok":report["ok"],"report":str(Path(args.report).resolve()),"findings":len(report["findings"])}))
    return 0


if __name__ == "__main__": raise SystemExit(main())
