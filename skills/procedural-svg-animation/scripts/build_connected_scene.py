#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Build and validate compact ordered concept scenes without catalog metadata."""
import argparse
import json
import math
from pathlib import Path
import sys
import unicodedata
import xml.etree.ElementTree as ET

NS = "http://www.w3.org/2000/svg"
ET.register_namespace("", NS)
CONTRACTS = Path(__file__).resolve().parents[1] / "assets/palettes/colorsets.json"


def number(value):
    return f"{value:.3f}".rstrip("0").rstrip(".")


def element(parent, tag, text=None, **attrs):
    child = ET.SubElement(parent, f"{{{NS}}}{tag}", {key.replace("_", "-"): str(value) for key, value in attrs.items()})
    child.text = text
    return child


def label_width(label):
    # Reserve wide glyphs explicitly; final-font browser inspection is still required.
    return 18 * sum(1 if char in "MWmw@%" or unicodedata.east_asian_width(char) in {"W", "F"} else .72 for char in label) + 20


def build_scene(config):
    labels = config["labels"]
    if not isinstance(labels, list) or not 2 <= len(labels) <= 12 or any(not isinstance(label, str) or not label.strip() for label in labels):
        raise ValueError("Provide 2–12 nonempty stage labels")
    if len(set(labels)) != len(labels):
        raise ValueError("Stage labels must be unique so every route has identifiable endpoints")
    duration = config["duration_ms"]
    if type(duration) is not int or not 1000 <= duration <= 120000:
        raise ValueError("Duration must be an integer from 1000 to 120000 ms")
    if type(config["seed"]) is not int or type(config["include_return"]) is not bool:
        raise ValueError("Seed must be an integer and include_return a boolean")
    palette = json.loads(CONTRACTS.read_text(encoding="utf-8"))["colorsets"][config["palette"]]
    colors = [paint for paint in palette["solidSequence"] if paint != palette["roles"]["surface"]]
    widths = [max(32, label_width(label)) for label in labels]
    node_height, gap, margin, return_drop = 36, 48, 18, 32
    occupied_width = sum(widths) + gap * (len(labels) - 1)
    minimum_width = math.ceil(occupied_width + 2 * margin)
    minimum_height = node_height + 2 * margin + (return_drop + 12 if config["include_return"] else 0)
    width = config["width"] if config["width"] is not None else minimum_width
    height = config["height"] if config["height"] is not None else minimum_height
    if type(width) is not int or type(height) is not int or width < minimum_width or height < minimum_height:
        raise ValueError(f"Readable labels, heads and motion need at least {minimum_width}×{minimum_height}; enlarge the canvas instead of shrinking text")
    if width > 10000 or height > 10000:
        raise ValueError("Canvas dimensions must not exceed 10000")
    offset_x = (width - occupied_width) / 2
    offset_y = (height - minimum_height) / 2 + margin
    cy = offset_y + node_height / 2
    nodes = []
    cursor = offset_x
    for index, (label, node_width) in enumerate(zip(labels, widths, strict=True)):
        nodes.append({"id": f"stage-{index}", "label": label, "x": cursor, "y": offset_y, "width": node_width, "height": node_height, "cx": cursor + node_width / 2})
        cursor += node_width + gap
    routes = []
    for index in range(len(nodes) - 1):
        source, target = nodes[index], nodes[index + 1]
        start, end = source["x"] + source["width"] + 4, target["x"] - 5
        routes.append({"source": source["label"], "target": target["label"], "d": f"M{number(start)} {number(cy)}H{number(end)}", "length": end-start})
    if config["include_return"]:
        source, target = nodes[-1], nodes[0]
        start_y, end_y = offset_y + node_height + 4, offset_y + node_height + 5
        lane_y = offset_y + node_height + return_drop
        routes.append({"source": source["label"], "target": target["label"], "d": f"M{number(source['cx'])} {number(start_y)}V{number(lane_y)}H{number(target['cx'])}V{number(end_y)}", "length": lane_y-start_y + source["cx"]-target["cx"] + lane_y-end_y})
    root = ET.Element(f"{{{NS}}}svg", {"viewBox": f"0 0 {width} {height}", "width": str(width), "height": str(height), "role": "img", "data-scene-kind": "connected-route", "data-palette": config["palette"], "data-colorset": config["palette"], "data-seed": str(config["seed"]), "data-duration-ms": str(duration)})
    element(root, "title", "Connected concept route")
    element(root, "desc", "Stages in order: " + ", ".join(labels) + ". Routes reveal before a token moves. Direction remains visible with reduced motion.")
    element(root, "metadata", json.dumps(config, sort_keys=True, ensure_ascii=False), id="connected-scene-contract")
    element(root, "style", ".psvg-reduced-layer{display:none}@media(prefers-reduced-motion:reduce){.psvg-motion-layer{display:none}.psvg-reduced-layer{display:inline}}text{font-family:Arial,Helvetica,sans-serif;font-size:18px;font-weight:600}")
    element(root, "rect", width=width, height=height, fill=palette["roles"]["surface"])
    defs = element(root, "defs")
    marker = element(defs, "marker", id="scene-arrow", viewBox="0 0 10 10", refX="9", refY="5", markerUnits="userSpaceOnUse", markerWidth="10", markerHeight="10", orient="auto")
    element(marker, "path", d="M0 0L10 5L0 10Z", fill=palette["roles"]["ink"])
    route_group = element(root, "g", id="scene-routes")
    for index, route in enumerate(routes):
        element(route_group, "path", id=f"route-{index}", d=route["d"], fill="none", stroke=palette["roles"]["ink"], stroke_width="2", marker_end="url(#scene-arrow)", data_source=route["source"], data_target=route["target"])
    node_group = element(root, "g", id="scene-nodes")
    for index, node in enumerate(nodes):
        fill = colors[index]
        group = element(node_group, "g", id=node["id"], data_label=node["label"])
        element(group, "rect", x=number(node["x"]), y=number(node["y"]), width=number(node["width"]), height=node_height, rx="5", fill=fill)
        element(group, "text", node["label"], x=number(node["cx"]), y=number(cy), text_anchor="middle", dominant_baseline="middle", fill=palette["textOnFill"][fill])
    motion = element(root, "g", **{"class": "psvg-motion-layer"})
    for index, route in enumerate(routes):
        start = .28 + index * .6 / len(routes)
        finish = .28 + (index + 1) * .6 / len(routes)
        reveal = element(motion, "path", d=route["d"], fill="none", stroke=palette["roles"]["primary"], stroke_width="2", pathLength="1", stroke_dasharray="1", stroke_dashoffset="1")
        element(reveal, "animate", attributeName="stroke-dashoffset", values="1;0;0;1", keyTimes="0;.22;.94;1", dur=f"{duration}ms", repeatCount="indefinite")
        token = element(motion, "circle", r="4", fill=palette["roles"]["primary"], opacity="0", data_route=str(index))
        # The token stays away from both ports and the complete arrowhead envelope.
        first, last = 5 / route["length"], 1 - 18 / route["length"]
        if last <= first:
            raise ValueError("Route is too short for the token and complete head")
        follow = element(token, "animateMotion", keyPoints=f"{number(first)};{number(first)};{number(last)};{number(last)};{number(first)}", keyTimes=f"0;{number(start)};{number(finish)};.94;1", calcMode="linear", dur=f"{duration}ms", repeatCount="indefinite")
        element(follow, "mpath", href=f"#route-{index}")
        element(token, "animate", attributeName="opacity", values="0;0;1;1;0;0", keyTimes=f"0;{number(start)};{number(start+.002)};{number(finish-.002)};{number(finish)};1", dur=f"{duration}ms", repeatCount="indefinite")
    element(root, "g", id="reduced-state", **{"class": "psvg-reduced-layer"})
    return root


def canonical(element):
    return (element.tag, sorted(element.attrib.items()), (element.text or "").strip(), [canonical(child) for child in element])


def validate(path):
    source = path.read_text(encoding="utf-8")
    if "<!DOCTYPE" in source or "<!ENTITY" in source:
        raise ValueError("External declarations are not part of a connected scene")
    root = ET.fromstring(source)
    metadata = root.find(f"{{{NS}}}metadata[@id='connected-scene-contract']")
    if metadata is None or not metadata.text:
        raise ValueError("Missing connected-scene construction contract")
    expected = build_scene(json.loads(metadata.text))
    if canonical(root) != canonical(expected):
        raise ValueError("Scene differs from its readable construction contract; correct build flags and rebuild")
    return {"passed": True, "source": str(path), "sceneKind": "connected-route", "width": int(root.get("width")), "height": int(root.get("height")), "routes": len(root.findall(f".//{{{NS}}}path[@data-source]"))}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    build = commands.add_parser("build", help="Create a content-sized ordered scene with optional final-to-first return")
    build.add_argument("--label", action="append", required=True)
    build.add_argument("--output", type=Path, required=True)
    build.add_argument("--palette", choices=("colorset1", "colorset2"), default="colorset1")
    build.add_argument("--seed", type=int, default=73021)
    build.add_argument("--duration-ms", type=int, default=6000)
    build.add_argument("--width", type=int)
    build.add_argument("--height", type=int)
    build.add_argument("--return-route", action="store_true")
    build.add_argument("--force", action="store_true")
    check = commands.add_parser("validate", help="Check readable geometry, semantics and motion against the construction contract")
    check.add_argument("source", type=Path)
    args = parser.parse_args()
    try:
        if args.command == "validate":
            report = validate(args.source)
        else:
            config = {"labels": args.label, "palette": args.palette, "seed": args.seed, "duration_ms": args.duration_ms, "width": args.width, "height": args.height, "include_return": args.return_route}
            root = build_scene(config)
            if args.output.exists() and not args.force:
                raise ValueError("Output already exists; pass --force for an intentional rebuild")
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(ET.tostring(root, encoding="unicode") + "\n", encoding="utf-8")
            report = validate(args.output)
        print(json.dumps(report, ensure_ascii=False))
        return 0
    except (OSError, ValueError, KeyError, ET.ParseError) as error:
        print(f"Connected scene failed: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
