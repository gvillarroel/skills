#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Create the compact illustrative workspace figure from exported vector logos."""

import argparse
import copy
import json
import sys
import xml.etree.ElementTree as ET
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skill-root", required=True, type=Path)
    parser.add_argument("--artifacts", required=True, type=Path)
    args = parser.parse_args()
    sys.dont_write_bytecode = True
    sys.path.insert(0, str(args.skill_root.resolve() / "scripts"))
    from compose_diagram import compose, element, namespace, parse_svg, plan, tag
    from route_connectors import radial_anchor

    artifacts = args.artifacts.resolve()
    sources = artifacts / "svgs" / "panels"
    sources.mkdir(parents=True, exist_ok=True)
    manifests = artifacts / "manifests"
    manifests.mkdir(parents=True, exist_ok=True)
    spec = {
        "version": 1,
        "title": "One workspace, three complementary views",
        "thesis": "A topology, responsibility matrix, and integrated review model explain one proposed workspace without repeating product names.",
        "note": "Illustrative proposal. Roles describe this design, not product capabilities. Icons identify tools; lines identify relations.",
        "canvas": {"width": 1280, "height": 800, "displayWidth": 1280, "minTextPx": 15,
                   "margin": 28, "gap": 42, "titleHeight": 100, "footerHeight": 40},
        "grid": {"columns": [1, 1, 1.1, 1.1], "rows": [1, 1.1]},
        "concepts": [{"id": key, "label": label} for key, label in
                     [("copilot", "GitHub Copilot"), ("claude", "Claude"), ("cloud", "Cloud environment"), ("workspace", "Shared workspace")]],
        "panels": [], "links": []}
    tool_colors = {"copilot": "#276bc8", "claude": "#b26a20", "cloud": "#24745a"}
    for concept in spec["concepts"]:
        if concept["id"] in tool_colors:
            concept["color"] = tool_colors[concept["id"]]
    spec["concepts"].append({"id":"review","label":"Human review","color":"#9e1b32"})
    for pid, title, question, claim, family, reason, alternative, span, ports in [
        ("topology", "01 / Shared context", "Which tools share the workspace?", "Three peers connect to the same workspace.",
         "direct-hub", "A hub shows unordered peers in a wide region.", "A flow would invent a sequence among the tools.",
         [1, 1, 1, 2], {"context": [0.65, 0.55]}),
        ("roles", "02 / Responsibility matrix", "Which responsibilities differ?", "The proposed roles differ along independent permissions.",
         "comparison-matrix", "Aligned columns reveal identical and different permissions.", "A network would make attribute comparison harder.",
         [2, 1, 1, 2], {"policy": [0.98, 0.65]}),
        ("synthesis", "03 / Integrated review model", "How do context and roles operate together?", "Proposals enter source only through human review in this design.",
         "layered-architecture", "Ownership containers and one real checkpoint combine the two views.", "A full flowchart would repeat the entire topology.",
         [1, 3, 2, 2], {"context": [0.10, 0.25], "policy": [0.14, 0.685]})]:
        spec["panels"].append({"id": pid, "title": title, "question": question, "claim": claim,
            "family": family, "reason": reason, "alternative": alternative,
            "concepts": ["copilot", "claude", "cloud", "workspace"], "source": f"../svgs/panels/{pid}.svg",
            "span": dict(zip(["row", "column", "rows", "columns"], span)), "ports": ports,
            "padding": 10, "headerHeight": 38, "frame": "none"})
        if pid=="synthesis": spec["panels"][-1]["concepts"].append("review")
    spec["links"] = [
        {"id": "context-bridge", "from": "topology.context", "to": "synthesis.context", "relation": "shared context", "label": "", "directed": False},
        {"id": "policy-bridge", "from": "roles.policy", "to": "synthesis.policy", "relation": "constrains review and publication", "label": "", "directed": False}]
    geometry = plan(spec)
    logos = {key: parse_svg(artifacts / "svgs" / "logos" / f"{key}.svg")[0] for key in ("copilot", "claude", "cloud")}
    ink, muted, accent = "#26323d", "#536575", "#9e1b32"
    active_objects, active_size = None, None

    def register(mark, name, x, y, width, height, concept=None, kind="node"):
        mark.set("data-node-id", name)
        mark.set("data-node-kind", kind)
        if concept: mark.set("data-concept-id", concept)
        if active_objects is not None:
            active_objects[name]={"box":[x/active_size[0],y/active_size[1],width/active_size[0],height/active_size[1]],"kind":kind}
        return mark

    def text(root, x, y, label, size=17, weight=400, anchor="start", color=ink):
        return element(root, "text", {"x": x, "y": y, "font-size": size, "font-weight": weight, "text-anchor": anchor, "fill": color}, label)

    def line(root, x1, y1, x2, y2, color="#adb5bd", dash=None, connector=False, owners=None):
        attrs = {"x1": x1, "y1": y1, "x2": x2, "y2": y2, "stroke": color, "stroke-width": 1.8}
        if dash: attrs["stroke-dasharray"] = dash
        if connector or owners: attrs["data-connector"]="native"
        if owners: attrs.update({"data-from-node":owners[0],"data-to-node":owners[1]})
        return element(root, "line", attrs)

    def rect(root, x, y, w, h, fill="#f2f4f6", stroke="none", rx=5):
        return element(root, "rect", {"x": x, "y": y, "width": w, "height": h, "fill": fill, "stroke": stroke, "rx": rx})

    def icon(root, name, x, y, size, occurrence):
        frame = rect(root, x-4, y-4, size+8, size+8, "#ffffff", tool_colors[name], 6)
        frame.set("stroke-width", "2.4")
        frame.set("data-color-concept", name)
        frame.set("data-color-channel", "stroke")
        register(frame, occurrence, x-4,y-4,size+8,size+8,concept=name)
        svg = namespace(copy.deepcopy(logos[name]), occurrence + "-")
        for key, value in {"x": x, "y": y, "width": size, "height": size, "preserveAspectRatio": "xMidYMid meet",
                           "data-concept-id": name, "aria-label": {"copilot": "GitHub Copilot", "claude": "Claude", "cloud": "Cloud environment"}[name]}.items():
            svg.set(key, str(value))
        root.append(svg)
        svg.set("data-brand-artwork", "true")

    for panel, geo in zip(spec["panels"], geometry["panels"]):
        w, h = geo["body"][2:]
        active_objects, active_size = {}, (w,h)
        root = ET.Element(tag("svg"), {"viewBox": f"0 0 {w} {h}", "font-family": "Arial, sans-serif", "fill": ink})
        element(root, "title", text=panel["question"])
        element(root, "desc", text=panel["claim"])
        pid = panel["id"]
        if pid == "topology":
            cx, cy = w * 0.50, h * 0.55
            workspace_box=[cx-80,cy-33,160,66]
            for box in ([24,11,68,68],[24,h-80,68,68],[w-92,14,64,64]):
                a=radial_anchor(box,[cx,cy])
                b=radial_anchor(workspace_box,[box[0]+box[2]/2,box[1]+box[3]/2])
                line(root,*a,*b,connector=True)
            icon(root, "copilot", 28, 15, 60, "topology-copilot")
            icon(root, "claude", 28, h - 76, 60, "topology-claude")
            icon(root, "cloud", w - 88, 18, 56, "topology-cloud")
            register(rect(root, *workspace_box, "#edf0f3", "#cbd1d8"),"workspace",*workspace_box)
            text(root, cx, cy - 3, "Shared", 18, 600, "middle")
            text(root, cx, cy + 21, "workspace", 18, 600, "middle")
            text(root, w - 8, h - 10, "Peers, no implied order", 15, 400, "end", muted)
            panel["ports"]={"context":{"object":"workspace","side":"right"}}
        elif pid == "roles":
            text(root, 6, 21, "PROPOSED ROLE", 15, 600, color=muted)
            cols = [w * 0.43, w * 0.66, w * 0.88]
            for x, label in zip(cols, ["Context", "Draft", "Publish"]): text(root, x, 21, label, 17, 600, "middle")
            line(root, 6, 37, w - 6, 37, "#cbd1d8")
            for i, (name, values) in enumerate([("copilot", ["Yes", "Yes", "—"]), ("claude", ["Yes", "Yes", "—"]), ("cloud", ["Yes", "—", "Yes"]) ]):
                y = 60 + i * 57
                icon(root, name, 20, y - 17, 36, f"roles-{name}")
                for x, value in zip(cols, values): text(root, x, y + 10, value, 17, 600 if value == "Yes" else 400, "middle", ink if value == "Yes" else muted)
                if i < 2: line(root, 6, y + 28, w - 6, y + 28, "#e5e8eb")
            bracket=element(root, "path", {"d": f"M {w*.965} 42 H {w*.98} V {h-18} H {w*.965}",
                "fill": "none", "stroke": "#68737e", "stroke-width": 1.3})
            matrix_box=[w*.965,42,w*.015,h-60]
            register(bracket,"role-matrix",*matrix_box,kind="container")
            panel["ports"]={"policy":{"object":"role-matrix","side":"right"}}
        else:
            register(rect(root,w*.05,17,w*.90,h-36,"#fafbfc","#cbd1d8",8),"workspace",w*.05,17,w*.90,h-36,kind="container")
            text(root, w * 0.10, 49, "SHARED WORKSPACE", 15, 700, color=muted)
            register(rect(root,w*.10,h*.15,w*.80,h*.23,"#edf0f3"),"context",w*.10,h*.15,w*.80,h*.23,kind="container")
            icon(root, "copilot", w * 0.20, h * 0.19, 48, "synthesis-copilot")
            icon(root, "claude", w * 0.34, h * 0.19, 48, "synthesis-claude")
            text(root, w * 0.62, h * 0.24, "Shared context", 18, 600, "middle")
            text(root, w * 0.62, h * 0.30, "Source + instructions", 16, 400, "middle", muted)
            line(root,w*.5,h*.38,w*.5,h*.62,owners=("context","review"))
            rect(root,w*.5-96,h*.465,192,h*.072,"#fafbfc",rx=0)
            text(root, w * 0.5, h * 0.51, "Proposed changes", 18, 600, "middle")
            review=register(rect(root,w*.14,h*.62,w*.72,h*.13,"#fff3f3",accent),"review",w*.14,h*.62,w*.72,h*.13,concept="review")
            review.set("data-color-concept","review");review.set("data-color-channel","stroke")
            text(root, w * 0.5, h * 0.68, "Human review", 19, 700, "middle")
            text(root, w * 0.5, h * 0.72, "Required before source changes", 15, 400, "middle")
            line(root,w*.5,h*.75,w*.5,h*.82,owners=("review","published"))
            register(rect(root,w*.14,h*.82,w*.72,h*.13,"#edf0f3"),"published",w*.14,h*.82,w*.72,h*.13,kind="container")
            icon(root, "cloud", w * 0.23, h * 0.83, 48, "synthesis-cloud")
            text(root, w * 0.60, h * 0.86, "Reviewed source", 18, 600, "middle")
            text(root, w * 0.60, h * 0.91, "Published result", 16, 400, "middle", muted)
            panel["ports"]={"context":{"object":"context","side":"left"},"policy":{"object":"review","side":"left"}}
        panel["objects"]=active_objects
        (sources / f"{pid}.svg").write_text(ET.tostring(root, encoding="unicode"), encoding="utf-8")

    spec_path = manifests / "composition.json"
    spec_path.write_text(json.dumps(spec, indent=2) + "\n", encoding="utf-8")
    svg_text, report = compose(spec, spec_path)
    # A shared visual key belongs below the page title, outside the panel grid.
    assembled = ET.fromstring(svg_text)
    active_objects=None
    for i, (name, label) in enumerate([("copilot", "GitHub Copilot"), ("claude", "Claude"), ("cloud", "Cloud environment")]):
        x = 30 + i * 250
        icon(assembled, name, x, 76, 28, f"key-{name}")
        text(assembled, x + 38, 96, label, 16)
    target = artifacts / "svgs" / "workspace-composition.svg"
    target.write_text(ET.tostring(assembled, encoding="unicode"), encoding="utf-8")
    (manifests / "composition-report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"ok": True, "svg": str(target), "panelCount": len(report["panels"])}))


if __name__ == "__main__":
    main()
