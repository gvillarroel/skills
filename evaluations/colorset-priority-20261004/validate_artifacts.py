#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Independent priority oracle for frozen isolated output records."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET

EXPECTED = ["#9e1b32", "#333e48", "#4f4f4f", "#696969", "#828282", "#9c9c9c", "#b5b5b5", "#cfcfcf", "#e7e7e7", "#363636", "#f7f7f7", "#1c1c1c", "#000000", "#ffffff", "#6d1222", "#e8002a", "#ffccd5"]
LABELS = ["Capture", "Triage", "Review", "Plan", "Build", "Test", "Package", "Approve", "Release", "Observe", "Support", "Archive", "Audit", "Train", "Renew", "Retire", "Recover", "Reconcile"]


def luminance(paint):
    values = [int(paint[i:i+2], 16) / 255 for i in (1, 3, 5)]
    return sum((x / 12.92 if x <= .04045 else ((x + .055) / 1.055) ** 2.4) * weight for x, weight in zip(values, (.2126, .7152, .0722)))


def contrast(a, b):
    levels = sorted((luminance(a), luminance(b)))
    return (levels[1] + .05) / (levels[0] + .05)


def text_on(fill):
    return max(("#000000", "#ffffff"), key=lambda paint: contrast(fill, paint))


def canonical_paint(value):
    if not isinstance(value, str):
        return value
    value = value.strip().lower()
    match = re.fullmatch(r"rgb\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)", value)
    if match:
        return "#" + "".join(f"{int(channel):02x}" for channel in match.groups())
    if re.fullmatch(r"#[0-9a-f]{3}", value):
        return "#" + "".join(channel * 2 for channel in value[1:])
    return value


def style_fields(style):
    return {
        "fill": canonical_paint(style.get("fill", style.get("color"))),
        "text": canonical_paint(style.get("text", style.get("textColor"))),
        "stroke": canonical_paint(style.get("stroke", style.get("borderColor", "none"))),
        "strokeWidth": style.get("strokeWidth", style.get("borderWidth", 0)),
        "opacity": style.get("opacity", 1),
    }


def check_styles(styles, canvas, findings, where):
    sequence = [paint for paint in EXPECTED if paint != canvas]
    if len(styles) < len(sequence):
        findings.append(f"{where}: only {len(styles)} styles for {len(sequence)} usable solids")
    for index, raw in enumerate(styles):
        style = style_fields(raw)
        expected = sequence[index % len(sequence)]
        if style["fill"] != expected:
            findings.append(f"{where}[{index}]: expected {expected}, observed {style['fill']}")
        if style["text"] != text_on(expected):
            findings.append(f"{where}[{index}]: inside text is not maximum-contrast exact black/white")
        if style["opacity"] != 1:
            findings.append(f"{where}[{index}]: category opacity is not 1")
        if index < len(sequence):
            if style["stroke"] != "none" or float(style["strokeWidth"]) != 0:
                findings.append(f"{where}[{index}]: first-cycle decorative border")
        elif style["stroke"] == "none" or not 1 <= float(style["strokeWidth"]) <= 3 or contrast(expected, style["stroke"]) < 3:
            findings.append(f"{where}[{index}]: overflow border is absent or lacks bounded contrast")


def check_prepared_option(option, findings, where):
    canvas = option.get("backgroundColor", "#ffffff").lower()
    graph = next((series for series in option.get("series", []) if series.get("type") == "graph"), None)
    if graph is None:
        findings.append(f"{where}: no native graph series")
        return
    nodes = graph.get("data", [])
    styles = [{**node.get("itemStyle", {}), "text": node.get("label", {}).get("color", graph.get("label", {}).get("color"))} for node in nodes]
    check_styles(styles, canvas, findings, where + ".nodes")
    for edge in graph.get("links", graph.get("edges", [])):
        style = {**graph.get("lineStyle", {}), **edge.get("lineStyle", {})}
        paint = style.get("color")
        alpha = style.get("opacity", 1)
        if not isinstance(paint, str) or not re.fullmatch(r"#[0-9a-f]{6}", paint):
            findings.append(f"{where}: native edge has no exact solid paint")
        elif alpha != 1 or contrast(paint, canvas) < 3:
            findings.append(f"{where}: native edge canvas contrast or opacity fails")


def artifact_identities(workspace, outputs):
    return [{"path": name, "sizeBytes": (workspace / name).stat().st_size, "sha256": hashlib.sha256((workspace / name).read_bytes()).hexdigest()} for name in outputs if (workspace / name).is_file()]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("run_id")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[2]
    run = root / "evaluations/runs" / args.run_id
    manifest = json.loads((run / "run-manifest.json").read_text(encoding="utf-8"))
    workspace = run / "workspace"
    skill = manifest["skill"]["name"]
    findings = []
    checks = []
    contract = workspace / "contract.json"
    if contract.is_file():
        record = json.loads(contract.read_text(encoding="utf-8"))
        if [item.get("canvas") for item in record.get("canvases", [])] != ["#ffffff", "#000000"]:
            findings.append("contract: missing exact white/dark canvas pair")
        for entry in record.get("canvases", []):
            check_styles(entry.get("styles", []), entry["canvas"], findings, "contract." + entry["canvas"])
            if "preparedOption" in entry:
                check_prepared_option(entry["preparedOption"], findings, "contract.preparedOption." + entry["canvas"])
            if "boxplotPreparedOption" in entry:
                boxes = entry["boxplotPreparedOption"].get("series", [])
                if len(boxes) != 2 or [series.get("itemStyle", {}).get("color") for series in boxes] != EXPECTED[:2]:
                    findings.append("default boxplots: native series omitted-itemStyle allocation is not primary red then gray1")
                if any(series.get("itemStyle", {}).get("borderColor") != EXPECTED[index] for index, series in enumerate(boxes)):
                    findings.append("default boxplots: semantic whisker/median paint does not match its category body")
        checks.append("independent literal category order, canvas exclusion, black/white text, opacity and overflow")
    prepared = workspace / "prepared-option.json"
    if prepared.is_file():
        record = json.loads(prepared.read_text(encoding="utf-8"))
        option = record.get("option", record)
        check_prepared_option(option, findings, "prepared-option")
        graph = next((series for series in option.get("series", []) if series.get("type") == "graph"), {})
        if [node.get("name") for node in graph.get("data", [])] != LABELS:
            findings.append("prepared-option: group labels or order differ from the task")
        checks.append("prepared native graph bodies, labels, and edge styles")
    allocation = workspace / "allocation.json"
    if allocation.is_file():
        record = json.loads(allocation.read_text(encoding="utf-8"))
        canvas = record.get("canvas")
        if isinstance(canvas, dict):
            canvas = canvas.get("background", canvas.get("backgroundColor"))
        if record.get("labels") != LABELS or canonical_paint(canvas) != "#ffffff":
            findings.append("allocation: labels or actual canvas differ from the task")
        check_styles(record.get("styles", []), "#ffffff", findings, "allocation")
        svg = ET.parse(workspace / "priority.svg").getroot()
        marked = [element for element in svg.iter() if element.get("data-category-index") is not None]
        category_bodies = {}
        for element in marked:
            index = int(element.get("data-category-index"))
            tag = element.tag.rsplit("}", 1)[-1]
            if tag == "g":
                element = next((child for child in element.iter() if child.tag.rsplit("}", 1)[-1] in {"rect", "path", "polygon", "circle", "ellipse"}), None)
            elif tag not in {"rect", "path", "polygon", "circle", "ellipse"}:
                continue
            if element is not None:
                category_bodies.setdefault(index, set()).add(element)
        if set(category_bodies) != set(range(len(LABELS))) or any(len(bodies) != 1 for bodies in category_bodies.values()):
            findings.append("actual SVG: ordered category marks are missing or ambiguous")
        else:
            sequence = [paint for paint in EXPECTED if paint != "#ffffff"]
            for index, bodies in sorted(category_bodies.items()):
                mark = next(iter(bodies))
                # Browser review independently resolves inherited/CSS presentation.
                local_styles = dict(re.findall(r"([-\w]+)\s*:\s*([^;]+)", mark.get("style", "")))
                actual = canonical_paint(mark.get("fill", local_styles.get("fill")))
                if actual is not None and actual != sequence[index % len(sequence)]:
                    findings.append(f"actual SVG mark {index}: explicit fill differs from priority")
        checks.append("actual exported SVG category identities and explicit body paint")
    if skill == "mermaid" and not contract.is_file():
        svg = ET.parse(workspace / "priority.svg").getroot()
        visible = " ".join(element.text or "" for element in svg.iter())
        if any(label not in visible for label in LABELS):
            findings.append("native Mermaid SVG: task labels are missing")
        nodes = [element for element in svg.iter() if "node" in element.get("class", "").split()]
        if len(nodes) != 18:
            findings.append(f"native Mermaid SVG: expected18 nodes, observed {len(nodes)}")
        edges = [element for element in svg.iter() if element.get("data-edge") == "true"]
        if len(edges) != 17:
            findings.append(f"native Mermaid SVG: expected17 relationships, observed {len(edges)}")
        identities = {element.get("id") for element in svg.iter() if element.get("id")}
        if any(identity not in identities for attribute in ("aria-labelledby", "aria-describedby") for identity in svg.get(attribute, "").split()) or not svg.get("aria-labelledby") or not svg.get("aria-describedby"):
            findings.append("native Mermaid SVG: accessible title/description identity is missing or unresolved")
        checks.append("native Mermaid node/relationship count, source labels and accessible identities; literal-slot contract is graded separately")
    if skill == "plantuml-colorset-renderer":
        record = json.loads((workspace / "render-report.json").read_text(encoding="utf-8"))
        if not record.get("ok") or record.get("failedDiagramCount") != 0:
            findings.append("native PlantUML report: renderer failure")
        for diagram in record.get("results", []):
            for output in diagram.get("outputs", []):
                if output.get("native_style", {}).get("version") != "scoped-solid-v3":
                    findings.append("native PlantUML report: stale style delivery version")
                if output.get("format") == "png" and output.get("svg_derived") is not True:
                    findings.append("native PlantUML report: PNG was not generated from the same finished SVG")
        svg = ET.parse(workspace / "renders/svg/priority.svg").getroot()
        visible = " ".join(element.text or "" for element in svg.iter())
        if any(label not in visible for label in ("Intake", "Review", "Record", "Archive")):
            findings.append("native PlantUML SVG: architecture task labels are missing")
        if (workspace / "renders/svg/layers.svg").is_file():
            layers = ET.parse(workspace / "renders/svg/layers.svg").getroot()
            visible = " ".join(element.text or "" for element in layers.iter())
            if any(label not in visible for label in ("Business", "Application", "Technology", "Motivation", "Strategy", "Physical", "Implementation")):
                findings.append("native PlantUML SVG: seven layer roles are not preserved")
        checks.append("native PlantUML successful stylev3 outputs, exact source labels and SVG-derived PNG fidelity")
    if skill == "vectorize-art-patterns":
        record = json.loads((workspace / "bailly.json").read_text(encoding="utf-8"))
        source = workspace / "skills/vectorize-art-patterns/assets/base-images/bailly-beauties-fancy.jpg"
        if record.get("input_sha256") != hashlib.sha256(source.read_bytes()).hexdigest():
            findings.append("vectorization: source artwork identity differs from bundled provenance")
        if record.get("output_sha256") != hashlib.sha256((workspace / "bailly.svg").read_bytes()).hexdigest():
            findings.append("vectorization: reported SVG identity differs from actual output")
        if not record.get("ok") or record.get("path_count", 0) < 1 or record.get("contour_count", 0) < 1:
            findings.append("vectorization: source-backed contours are absent")
        if any(paint not in EXPECTED for paint in record.get("palette", [])):
            findings.append("vectorization: actual source-led palette uses paints outside Colorset1")
        mapping = record.get("colorset_mapping", [])
        targets = [entry.get("target") for entry in mapping]
        palettes = json.loads((workspace / "skills/vectorize-art-patterns/assets/palettes/colorsets.json").read_text(encoding="utf-8"))["colorsets"]
        if targets != record.get("palette") or len(targets) != 16 or len(set(targets)) != 16:
            findings.append("controlled source-art vectorization: sixteen distinct mapped source colors were collapsed or reordered")
        if not targets or targets[0] not in palettes["colorset1"]["backgroundCandidates"]:
            findings.append("controlled source-art vectorization: category priority overrode its qualified source background")
        if targets == EXPECTED[:len(targets)]:
            findings.append("controlled source-art vectorization: source palette was replaced by categorical index order")
        actual = ET.parse(workspace / "bailly.svg").getroot()
        actual_fills = {canonical_paint(element.get("fill")) for element in actual.iter() if element.tag.rsplit("}", 1)[-1] in {"rect", "path", "polygon"} and element.get("fill") not in (None, "none")}
        if actual_fills != set(targets):
            findings.append("controlled source-art vectorization: actual native contour fills differ from the source mapping")
        if any(element.tag.rsplit("}", 1)[-1] == "image" for element in actual.iter()):
            findings.append("vectorization: editable contours were replaced by a raster image wrapper")
        checks.append("source artwork SHA, SVG SHA, contour presence and finite source-led palette; no forced category-index recolor")
    report = {
        "schemaVersion": 1, "runId": args.run_id, "skill": skill,
        "reviewerSha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "payloadSha256": manifest["skill"]["payloadSha256"],
        "passed": not findings, "checks": checks,
        "findings": findings,
        "artifactIdentities": artifact_identities(workspace, manifest["expectedOutputs"]),
        "browserReviewRequired": True,
    }
    output = args.output or run / "independent-artifact-check.json"
    if output.exists():
        previous = output.with_name(output.stem + ".previous.json")
        if not previous.exists():
            previous.write_bytes(output.read_bytes())
    output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"runId": args.run_id, "passed": not findings, "findings": findings, "output": str(output)}))
    return 0 if not findings else 1


if __name__ == "__main__":
    raise SystemExit(main())
