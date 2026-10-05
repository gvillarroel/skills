#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["pillow"]
# ///
"""Compose measured fallback concepts as a compact spine, branch and feedback."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import re
import subprocess

from build_composite_scene import build


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--node", action="append", required=True, help="Stable-id=Complete label; 2–6 spine nodes.")
    parser.add_argument("--feedback", action="store_true", help="Connect the last spine node back to the first.")
    parser.add_argument("--branch", help="Spine-id=Complete branch label; placed above its source.")
    parser.add_argument("--meaning", action="append", default=[], help="Source-id:target-id=Complete relationship meaning; metadata only.")
    parser.add_argument("--width", type=int, required=True)
    parser.add_argument("--height", type=int, required=True)
    parser.add_argument("--duration", type=float, default=8)
    parser.add_argument("--id", default="compact-scene")
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--html", type=Path, required=True)
    parser.add_argument("--review", type=Path, required=True)
    parser.add_argument("--project-root", type=Path, default=Path.cwd())
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    root = args.project_root.resolve()
    destinations = [path.resolve() for path in [args.contract, args.html, args.review]]
    if any(not path.is_relative_to(root) for path in destinations) or len(set(destinations)) != 3:
        parser.error("Use three distinct task-owned paths inside project-root.")
    if any(path.exists() for path in destinations) and not args.force:
        parser.error("An output exists; use fresh paths or --force for an authorized rebuild.")
    if not 2 <= len(args.node) <= 6 or min(args.width, args.height) < 100 or not math.isfinite(args.duration) or args.duration <= 0:
        parser.error("Use 2–6 nodes, positive duration and a canvas of at least 100×100.")
    if not re.fullmatch(r"[a-z][a-z0-9-]*", args.id):
        parser.error("Scene id must be lowercase hyphen-case.")
    nodes = []
    for raw in args.node:
        identity, separator, label = raw.partition("=")
        if not separator or not re.fullmatch(r"[a-z][a-z0-9-]*", identity) or not label.strip():
            parser.error("Each node needs stable-id=Complete label.")
        nodes.append({"id": identity, "label": label})
    spine = list(nodes)
    if len({node["id"] for node in nodes}) != len(nodes):
        parser.error("Node IDs must be unique.")
    branch_source = None
    if args.branch:
        branch_source, separator, label = args.branch.partition("=")
        if not separator or branch_source not in {node["id"] for node in spine} or not label.strip():
            parser.error("Branch must name a spine source and its complete label.")
        identity = f"{branch_source}-branch"
        if identity in {node["id"] for node in nodes}:
            parser.error("Branch ID collides with a spine node.")
        nodes.append({"id": identity, "label": label})
    pairs = {(a["id"],b["id"]) for a,b in zip(spine,spine[1:])}
    if args.feedback:
        pairs.add((spine[-1]["id"],spine[0]["id"]))
    if branch_source:
        pairs.add((branch_source,nodes[-1]["id"]))
    meanings = {}
    for raw in args.meaning:
        pair, separator, meaning = raw.partition("=")
        source, colon, target = pair.partition(":")
        key = (source,target)
        if not separator or not colon or key not in pairs or key in meanings or len(meaning.strip()) < 12:
            parser.error("Meaning requires a unique declared source-id:target-id and at least 12 description characters.")
        meanings[key] = meaning
    source_dir = args.contract.resolve().parent / f"{args.id}-assets"
    if source_dir.exists() and any(source_dir.iterdir()) and not args.force:
        parser.error("The asset folder is not empty; use fresh paths or --force for an authorized rebuild.")
    source_dir.mkdir(parents=True, exist_ok=True)
    for node in nodes:
        svg, report = source_dir / f"{node['id']}.svg", source_dir / f"{node['id']}.json"
        subprocess.run(["uv", "run", "--script", str(Path(__file__).with_name("scaffold_connected_asset.py")),
                        "--label", node["label"], "--output", str(svg), "--report", str(report)], check=True,
                       stdout=subprocess.DEVNULL)
        meta = json.loads(report.read_text(encoding="utf-8"))
        node.update({"width": meta["width"], "height": meta["height"], "svg": svg, "report": report})
    gap, outside, return_clearance = 52, 22, 10
    width = sum(node["width"] for node in spine) + gap * (len(spine) - 1)
    row_height = max(node["height"] for node in spine)
    above = (nodes[-1]["height"] + gap) if branch_source else 0
    below = return_clearance if args.feedback else 0
    envelope_width = width + (2 * outside if args.feedback else 0)
    envelope_height = above + row_height + below
    if envelope_width > args.width - 48 or envelope_height > args.height - 48:
        parser.error("Canvas cannot fit readable labels, complete heads and signal travel; enlarge it instead of shrinking type.")
    x = (args.width - width) / 2
    row_y = (args.height - envelope_height) / 2 + above
    for node in spine:
        node.update({"x": x, "y": row_y + (row_height - node["height"]) / 2})
        x += node["width"] + gap
    if branch_source:
        parent = next(node for node in spine if node["id"] == branch_source)
        branch = nodes[-1]
        branch.update({"x": parent["x"] + (parent["width"] - branch["width"]) / 2,
                       "y": row_y - gap - branch["height"]})
        if branch["x"] < 24 or branch["x"] + branch["width"] > args.width - 24:
            parser.error("Complete branch label exceeds the protected canvas margin; enlarge the canvas.")
    min_x = min(node["x"] for node in nodes)
    max_x = max(node["x"] + node["width"] for node in nodes)
    min_y = min(node["y"] for node in nodes)
    max_y = max(node["y"] + node["height"] for node in nodes)
    if args.feedback:
        min_x = min(min_x, spine[0]["x"] - outside - 7)
        max_x = max(max_x, spine[-1]["x"] + spine[-1]["width"] + outside + 7)
        max_y = max(max_y, row_y + row_height + return_clearance + 7)
    envelope_width, envelope_height = max_x-min_x, max_y-min_y
    if envelope_width > args.width-48 or envelope_height > args.height-48:
        parser.error("The full label and moving signal envelope exceeds the protected canvas margin.")
    dx, dy = (args.width-envelope_width)/2-min_x, (args.height-envelope_height)/2-min_y
    for node in nodes:
        node["x"] += dx
        node["y"] += dy
    row_y += dy
    min_x += dx
    min_y += dy
    elements = []
    for node in nodes:
        elements.append({"id": node["id"], "assetId": node["id"], "producerSkill": "repo-native",
            "fallbackReason": "No specialist is available; measured native-size label fallback.",
            "kind": "svg", "src": node["svg"].relative_to(root).as_posix(),
            "sha256": hashlib.sha256(node["svg"].read_bytes()).hexdigest(),
            "validationReport": node["report"].relative_to(root).as_posix(),
            "intrinsic": {"width": node["width"], "height": node["height"]},
            "background": "#ffffff", "bounds": {"x": node["x"] / args.width, "y": node["y"] / args.height,
                "width": node["width"] / args.width, "height": node["height"] / args.height},
            "zIndex": 10, "fit": "contain", "overflow": "visible", "clock": "static",
            "ports": [{"id": "in", "x": 0, "y": .5}, {"id": "out", "x": 1, "y": .5},
                      {"id": "top", "x": .5, "y": 0}, {"id": "bottom", "x": .5, "y": 1}], "states": []})
    relations = [(a["id"], "out", b["id"], "in", "#9e1b32", []) for a, b in zip(spine, spine[1:])]
    if args.feedback:
        first, last = spine[0], spine[-1]
        right, left = last["x"] + last["width"] + outside, first["x"] - outside
        bottom = row_y + row_height + return_clearance
        points = [(right, row_y + row_height/2), (right, bottom), (left, bottom), (left, row_y + row_height/2)]
        relations.append((last["id"], "out", first["id"], "in", "#333e48", points))
    if branch_source:
        relations.append((branch_source, "top", nodes[-1]["id"], "bottom", "#696969", []))
    interactions = []
    slot = args.duration * .8 / len(relations)
    for index, (source, port, target, target_port, color, points) in enumerate(relations):
        connector = {"path": "straight", "color": color, "width": 4, "zIndex": 20, "persistAfter": True}
        if points:
            connector["waypoints"] = [{"x": px/args.width, "y": py/args.height} for px, py in points]
        interactions.append({"id": f"route-{index + 1}", "type": "signal-route", "channel": "signal",
            "source": {"element": source, "port": port}, "target": {"element": target, "port": target_port},
            "start": index * slot, "end": (index + 1) * slot, "emits": [], "consumes": [],
            "meaning": meanings.get((source,target),
                f"{next(n['label'] for n in nodes if n['id']==source)} sends a signal to {next(n['label'] for n in nodes if n['id']==target)}."), "connector": connector,
            "validationChecks": ["Native labels, complete heads, independent lanes and moving tokens remain readable."]})
    divisor = math.gcd(args.width, args.height)
    scene = {"schemaVersion": 1, "id": args.id, "canvas": {"width": args.width, "height": args.height,
        "aspectRatio": f"{args.width//divisor}:{args.height//divisor}", "fps": 30,
        "durationSeconds": args.duration, "background": "#f7f7f7",
        "safeArea": {edge: 24 for edge in ["top", "right", "bottom", "left"]}},
        "masterClock": {"mode": "deterministic", "loop": False}, "elements": elements,
        "events": [], "tracks": [], "interactions": interactions}
    args.contract.parent.mkdir(parents=True, exist_ok=True)
    args.contract.write_text(json.dumps(scene, indent=2) + "\n", encoding="utf-8")
    result = build(argparse.Namespace(contract=args.contract, output=args.html, project_root=root,
        force=args.force, allow_missing_hashes=False, require_producer_reports=True, report=None))
    args.review.parent.mkdir(parents=True, exist_ok=True)
    args.review.write_text(json.dumps({"scope": "Measured simple-label fallback; inspect actual final states.",
        "occupiedBounds": {"x": min_x, "y": min_y, "width": envelope_width, "height": envelope_height}, "gapPx": gap,
        "fontPx": 18, "retainedNodes": len(nodes), "retainedRelations": len(relations),
        "buildPassed": result["passed"]}, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"contract": str(args.contract), "html": str(args.html), "review": str(args.review),
                      "occupiedWidth": envelope_width, "occupiedHeight": envelope_height}))


if __name__ == "__main__":
    main()
