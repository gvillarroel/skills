#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Check evaluator-owned semantic oracles for isolated Lucidchart SVG cases.

Run: uv run --script evaluations/lucidchart-svg/validate_artifacts.py CASE WORKSPACE
Status notes need a separate human review; no prose string is used as a grader.
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
import xml.etree.ElementTree as ET
import zipfile


class TextContent(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []

    def handle_data(self, data: str) -> None:
        self.parts.append(data)

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() == "br":
            self.parts.append("\n")


def literal_text(value: str) -> str:
    parser = TextContent()
    parser.feed(value)
    parser.close()
    return "".join(parser.parts).strip()


NATURAL_SVG = '<svg xmlns="http://www.w3.org/2000/svg" width="500" height="180" viewBox="0 0 500 180"><g id="n-request" data-node-id="request"><rect x="20" y="50" width="110" height="60" fill="#ffffff" stroke="#333333"/><text x="75" y="85">Request &amp; review</text></g><g id="n-check" data-node-id="check"><polygon points="250,40 300,80 250,120 200,80" fill="#ffffff" stroke="#333333"/><text x="250" y="85">Approved?</text></g><g id="n-publish" data-node-id="publish"><rect x="370" y="50" width="110" height="60" fill="#ffffff" stroke="#333333"/><text x="425" y="85">Publish</text></g><path id="e-review" data-source="request" data-target="check" d="M130 80 L200 80"/><path id="e-yes" data-source="check" data-target="publish" d="M300 80 L370 80"/><text data-edge-id="e-yes" x="330" y="70">yes</text></svg>'
GENERAL_SVG = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 500"><g transform="translate(10 20)"><g data-node-id="alert" id="alert"><ellipse cx="170" cy="50" rx="70" ry="30" fill="#ffeecc" stroke="#333333"/><text x="170" y="55">Alert &amp; triage</text></g><g data-node-id="resolve" id="resolve"><rect x="100" y="170" width="140" height="60" fill="#ffffff" stroke="#333333"/><text x="170" y="205">Resolve &lt;P1&gt;</text></g><g data-node-id="close" id="close"><rect x="100" y="320" width="140" height="60" fill="#eeeeee" stroke="#333333"/><text x="170" y="355">Close</text></g><text id="note" data-node-id="note" data-box="250 180 130 40" x="250" y="205" fill="#111111">SLA: 30 min</text><path id="e-triage" data-source="alert" data-target="resolve" d="M170 80L170 170"/><path id="e-close" data-source="resolve" data-target="close" d="M170 230L170 320"/></g></svg>'
BOUNDARY_SVG = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 200"><image href="https://example.com/logo.png" width="100" height="50"/><path d="M20 20L280 180 M20 180L280 20"/><foreignObject x="20" y="80" width="200" height="40"><div xmlns="http://www.w3.org/1999/xhtml">Unknown topology</div></foreignObject></svg>'

# Oracles are derived directly from the task's explicit SVG geometry and semantics.
# They intentionally do not import or call any skill-owned implementation.
CASES = {
    "contract": {
        "package": "deliverables/flow.lucid", "document": "deliverables/document.json",
        "graph": "inputs/graph.json", "note": "deliverables/status.md",
        "nodes": [("start", "rectangle", "Start <draft> & review", (20, 30, 100, 50), None),
                  ("end", "rectangle", "Finish", (220, 30, 100, 50), None)],
        "edges": [("link", "start", "end", "approved")], "ports": ((1, .5), (0, .5)),
    },
    "naturalistic": {
        "package": "out/approval.lucid", "document": "out/document.json", "graph": "out/graph.json",
        "note": "out/mapping.md", "source": "input/approval.svg", "svg": NATURAL_SVG,
        "nodes": [("request", "rectangle", "Request & review", (20, 50, 110, 60), "#ffffff"),
                  ("check", "diamond", "Approved?", (200, 40, 100, 80), "#ffffff"),
                  ("publish", "rectangle", "Publish", (370, 50, 110, 60), "#ffffff")],
        "edges": [("e-review", "request", "check", ""), ("e-yes", "check", "publish", "yes")],
        "ports": ((1, .5), (0, .5)),
    },
    "generalization": {
        "package": "deliver/incident.lucid", "document": "deliver/document.json", "graph": "deliver/graph.json",
        "note": "deliver/changes.md", "source": "source/incident.svg", "svg": GENERAL_SVG,
        "nodes": [("alert", "circle", "Alert & triage", (110, 40, 140, 60), "#ffeecc"),
                  ("resolve", "rectangle", "Resolve <P1>", (110, 190, 140, 60), "#ffffff"),
                  ("close", "rectangle", "Close", (110, 340, 140, 60), "#eeeeee"),
                  ("note", "text", "SLA: 30 min", (260, 200, 130, 40), None)],
        "edges": [("e-triage", "alert", "resolve", ""), ("e-close", "resolve", "close", "")],
        "ports": ((.5, 1), (.5, 0)),
    },
    "boundary": {"source": "input/ambiguous.svg", "svg": BOUNDARY_SVG,
                 "inspection": "result/inspection.json", "note": "result/status.md"},
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def numbers_equal(observed: object, expected: tuple[float, ...], keys: tuple[str, ...]) -> bool:
    return isinstance(observed, dict) and all(
        type(observed.get(key)) in (int, float)
        and math.isfinite(observed[key])
        and math.isclose(observed[key], value, abs_tol=1e-8)
        for key, value in zip(keys, expected)
    )


def source_identity(workspace: Path, spec: dict) -> bytes:
    raw = (workspace / spec["source"]).read_bytes()
    expected = spec["svg"].encode("utf-8")
    require(raw in (expected, expected + b"\n", expected + b"\r\n"), "Source SVG bytes differ from the supplied fixture")
    require(ET.fromstring(raw).tag == "{http://www.w3.org/2000/svg}svg", "Source is not SVG XML")
    return raw


def inspect_identity(workspace: Path, raw: bytes, path: str) -> dict:
    report = json.loads((workspace / path).read_text(encoding="utf-8"))
    require(report.get("sha256") == hashlib.sha256(raw).hexdigest(), "Inspection hash is not the actual source hash")
    require(report.get("bytes") == len(raw) and report.get("valid_svg") is True, "Inspection byte count/XML status differs")
    return report


def validate(workspace: Path, case: str) -> dict:
    spec = CASES[case]
    checks: list[str] = []
    note = workspace / spec["note"]
    require(note.is_file() and note.stat().st_size > 0, "Required status/mapping note is missing or empty")
    if "source" in spec:
        raw = source_identity(workspace, spec)
        checks.append("exact supplied SVG source identity")
    if case == "boundary":
        report = inspect_identity(workspace, raw, spec["inspection"])
        require("https://example.com/logo.png" in report.get("external_resources", []), "External image dependency was not reported")
        require({"external-resource", "foreignObject-needs-review"} <= set(report.get("blocking_flags", [])), "Boundary blockers were not detected")
        require(report.get("ready_for_upload") is False and report.get("safe_to_render_offline") is False, "Unsafe boundary asset was marked ready")
        generated = [p for p in workspace.rglob("*") if p.is_file() and "skills" not in p.relative_to(workspace).parts]
        forbidden = [p.relative_to(workspace).as_posix() for p in generated if p.suffix == ".lucid" or p.name in {"graph.json", "document.json"}]
        for path in generated:
            if path.suffix.lower() != ".json":
                continue
            data = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(data, dict) and ("nodes" in data or "pages" in data):
                forbidden.append(path.relative_to(workspace).as_posix())
        require(not forbidden, "Boundary case fabricated native files: " + ", ".join(forbidden))
        checks.extend(["actual inspection identity and external/foreignObject blockers", "no native graph or package fabricated"])
    else:
        package = workspace / spec["package"]
        document_raw = (workspace / spec["document"]).read_bytes()
        with zipfile.ZipFile(package) as archive:
            require(archive.namelist() == ["document.json"], "Native package must contain only root document.json, without image resources")
            require(archive.read("document.json") == document_raw, "Separate document JSON and ZIP entry differ byte-for-byte")
        document = json.loads(document_raw)
        require(document.get("version") == 1 and len(document.get("pages", [])) == 1, "Expected a one-page version-1 document")
        page = document["pages"][0]
        shapes = page.get("shapes", [])
        lines = page.get("lines", [])
        require(len(shapes) == len(spec["nodes"]) and len(lines) == len(spec["edges"]), "Object or connector count differs from source semantics")
        objects = [page, *shapes, *lines]
        ids = [o.get("id") for o in objects]
        require(all(isinstance(i, str) and re.fullmatch(r"[A-Za-z0-9_.~-]{1,36}", i) for i in ids), "Invalid native object IDs")
        require(len(ids) == len(set(ids)), "Native IDs are not globally unique")
        by_id = {s["id"]: s for s in shapes}
        by_label = {literal_text(s.get("text", "")): s for s in shapes}
        require(set(by_label) == {n[2] for n in spec["nodes"]}, "Native object labels differ")
        recovered_ids = {node_id: by_label[label]["id"] for node_id, _, label, _, _ in spec["nodes"]}
        for node_id, kind, label, box, fill in spec["nodes"]:
            node = by_label[label]
            require(node.get("type") == kind, f"{node_id}: actual native shape type is incorrect")
            require(numbers_equal(node.get("boundingBox"), box, ("x", "y", "w", "h")), f"{node_id}: source geometry/translation differs")
            require(literal_text(node.get("text", "")) == label, f"{node_id}: literal object label differs")
            if kind == "text":
                require("style" not in node or not node["style"], "Native text note has unsupported shape style")
                require("#111111" in node.get("text", "").lower(), "Native text note lost its text color")
            elif fill is not None:
                require(node.get("style", {}).get("fill", {}).get("color", "").lower() == fill, f"{node_id}: source fill differs")
                require(node.get("style", {}).get("stroke", {}).get("color", "").lower() == "#333333", f"{node_id}: source stroke differs")
        by_edge = {line["id"]: line for line in lines}
        semantic_edges = {(line.get("endpoint1", {}).get("shapeId"), line.get("endpoint2", {}).get("shapeId")): line for line in lines}
        require(set(semantic_edges) == {(recovered_ids[e[1]], recovered_ids[e[2]]) for e in spec["edges"]}, "Native connector topology differs")
        for edge_id, source, target, label in spec["edges"]:
            line = semantic_edges[recovered_ids[source], recovered_ids[target]]
            require(line.get("lineType") == "straight", f"{edge_id}: arrow route differs")
            for key, node_id, port, arrow in zip(("endpoint1", "endpoint2"), (recovered_ids[source], recovered_ids[target]), spec["ports"], ("none", "arrow")):
                endpoint = line.get(key, {})
                require(endpoint.get("type") == "shapeEndpoint" and endpoint.get("shapeId") == node_id, f"{edge_id}: endpoint is not attached to the correct native shape")
                require(numbers_equal(endpoint.get("position"), port, ("x", "y")), f"{edge_id}: horizontal/vertical connection port differs")
                require(endpoint.get("style") == arrow, f"{edge_id}: direction marker differs")
            observed_labels = [literal_text(item.get("text", "")) for item in line.get("text", [])]
            require(observed_labels == ([label] if label else []), f"{edge_id}: literal branch label differs")
        graph = json.loads((workspace / spec["graph"]).read_text(encoding="utf-8"))
        graph_nodes = {n["id"]: n for n in graph.get("nodes", [])}
        require(set(graph_nodes) == set(by_id), "Recovered graph node identity differs")
        for node_id, kind, label, box, _ in spec["nodes"]:
            node = graph_nodes[recovered_ids[node_id]]
            require(node.get("label") == label, f"{node_id}: recovered graph label differs")
            require(numbers_equal(node, box, ("x", "y", "width", "height")), f"{node_id}: recovered graph bounds differ")
        graph_edges = {e["id"]: e for e in graph.get("edges", [])}
        require(set(graph_edges) == set(by_edge), "Recovered graph edge identity differs")
        for edge_id, source, target, label in spec["edges"]:
            edge = graph_edges[semantic_edges[recovered_ids[source], recovered_ids[target]]["id"]]
            require((edge.get("source"), edge.get("target"), edge.get("label", "")) == (recovered_ids[source], recovered_ids[target], label), f"{edge_id}: recovered topology/label differs")
        checks.extend(["native ZIP and separate JSON byte identity, without image assets", "actual native shape types and decoded literal labels", "exact source geometry, translation and applicable colors", "unique source identities and attached directional ports", "recovered graph semantics match the explicit source"])
        if case == "naturalistic":
            require((workspace / "out/upload.svg").read_bytes() == raw, "Upload SVG was not preserved byte-for-byte")
            report = inspect_identity(workspace, raw, "out/inspection.json")
            require(report.get("ready_for_upload") is True and report.get("external_resources") == [], "Clean SVG asset inspection is incorrect")
            require(report.get("labels") == ["Request & review", "Approved?", "Publish", "yes"], "SVG inspection lost literal labels")
            checks.append("unchanged prepared SVG and inspection byte identity")
    return {"case": case, "workspace": str(workspace), "artifact_checks_passed": True,
            "checks": checks, "manual_status_review_required": True, "status_note": str(note),
            "manual_review": ["Reports local preparation separately from authenticated Lucid acceptance, export and upload.",
                              "States editability/approximations or missing topology and dependencies relevant to the case; no fabricated remote result."],
            "status_note_text": note.read_text(encoding="utf-8")}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("case", choices=CASES)
    parser.add_argument("workspace", type=Path)
    parser.add_argument("--report", type=Path)
    parser.add_argument("--compact", action="store_true", help="Omit status-note contents from stdout; the report retains them for manual review.")
    args = parser.parse_args()
    try:
        result = validate(args.workspace.resolve(), args.case)
        code = 0
    except (OSError, ValueError, KeyError, TypeError, ET.ParseError, zipfile.BadZipFile) as error:
        result = {"case": args.case, "workspace": str(args.workspace.resolve()), "artifact_checks_passed": False, "error": str(error)}
        code = 1
    encoded = json.dumps(result, indent=2, ensure_ascii=False) + "\n"
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(encoded, encoding="utf-8")
    # Preserve human-readable UTF-8 reports while supporting Windows cp1252 consoles.
    console_result = {key: value for key, value in result.items() if not args.compact or key != "status_note_text"}
    print(json.dumps(console_result, indent=2, ensure_ascii=True))
    return code


if __name__ == "__main__":
    sys.exit(main())
