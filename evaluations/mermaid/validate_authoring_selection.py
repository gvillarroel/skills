#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Independently grade the Mermaid authoring and selection evaluation."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import time
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from html import escape
from pathlib import Path
from typing import Callable

from visual_palette import (
    COLOR_GROUPS,
    COLORSET_GROUPS,
    evaluate_visual_palette,
    make_counterfactual_source,
)

STANDARD_TOKENS = set(COLOR_GROUPS["primary"])
EXTENDED_TOKENS = {
    color
    for group in COLORSET_GROUPS["colorset2"]
    for color in COLOR_GROUPS[group]
}


@dataclass(frozen=True)
class CaseContract:
    case_id: str
    relative_path: str
    family: str
    declarations: tuple[str, ...]
    colorset: str
    fidelity_check: Callable[[str], list[str]]
    required_visual_groups: tuple[str, ...]
    minimum_visible_colors: int = 1
    minimum_palette_ratio: float = 0.001


def require_terms(source: str, *terms: str) -> list[str]:
    lowered = source.casefold()
    return [f"missing source term: {term}" for term in terms if term.casefold() not in lowered]


def case_01(source: str) -> list[str]:
    findings = require_terms(source, "Intake", "Validate", "Authorize", "Repair", "Archive", "valid", "invalid")
    if source.count("Validate") < 2:
        findings.append("repair loop does not visibly return to Validate")
    return findings


def case_02(source: str) -> list[str]:
    terms = (
        "Client", "Gateway", "Inventory", "Payment", "Submit order", "Reserve items", "Reserved",
        "Charge 125 USD", "Approved", "Order confirmed",
    )
    findings = require_terms(source, *terms)
    positions = [source.casefold().find(term.casefold()) for term in terms[4:]]
    if any(position < 0 for position in positions) or positions != sorted(positions):
        findings.append("interaction messages are not preserved in supplied order")
    return findings


def case_03(source: str) -> list[str]:
    findings = require_terms(
        source,
        "CUSTOMER", "ORDER", "ORDER_ITEM", "PRODUCT", "customer_id", "order_id", "product_id",
        "email", "placed_at", "quantity", "unit_price_usd", "PK", "FK",
    )
    if len(re.findall(r"(?:\|\||o\{|\|\{).*?--", source)) < 3 and source.count("--") < 3:
        findings.append("fewer than three cardinality relationships are encoded")
    return findings


def case_04(source: str) -> list[str]:
    rows = (
        ("Solar", "Grid", "42"), ("Wind", "Grid", "35"), ("Grid", "Residential", "46"),
        ("Grid", "Industry", "24"), ("Grid", "Storage", "7"), ("Storage", "Residential", "4"),
    )
    findings = require_terms(source, "GWh", *(value for row in rows for value in row))
    for start, end, value in rows:
        if not re.search(rf"{re.escape(start)}\s*,\s*{re.escape(end)}\s*,\s*{value}(?:\.0+)?\b", source, re.IGNORECASE):
            findings.append(f"missing exact weighted transfer {start}->{end}:{value}")
    return findings


def case_05(source: str) -> list[str]:
    states = ("New", "Triaged", "In Progress", "Rejected", "Waiting on Customer", "Resolved", "Closed", "Reopened")
    findings = require_terms(source, *states)
    expected_pairs = (
        ("New", "Triaged"), ("Triaged", "In Progress"), ("Triaged", "Rejected"),
        ("In Progress", "Waiting on Customer"), ("In Progress", "Resolved"),
        ("Waiting on Customer", "In Progress"), ("Resolved", "Closed"), ("Resolved", "Reopened"),
        ("Reopened", "In Progress"),
    )
    aliases = {state: re.sub(r"\W+", "", state) for state in states}
    for label, alias in re.findall(r'^\s*state\s+"([^"]+)"\s+as\s+([A-Za-z0-9_]+)\s*$', source, re.MULTILINE):
        aliases[label] = alias
    for start, end in expected_pairs:
        if not re.search(
            rf"^\s*{re.escape(aliases[start])}\s*-->\s*{re.escape(aliases[end])}(?:\s|$)",
            source,
            re.MULTILINE,
        ):
            findings.append(f"missing transition evidence {start}->{end}")
    return findings


def case_06(source: str) -> list[str]:
    findings = require_terms(source, "Q1", "Q2", "Q3", "Q4", "12", "18", "15", "24", "USD", "million")
    positions = [source.find(quarter) for quarter in ("Q1", "Q2", "Q3", "Q4")]
    if positions != sorted(positions) or any(position < 0 for position in positions):
        findings.append("quarters are not preserved in Q1-Q4 order")
    return findings


def case_07(source: str) -> list[str]:
    findings = require_terms(
        source, "Design", "API", "UI", "Integration", "Release", "2026-09-01", "5d", "8d", "6d", "4d", "2026-09-22",
    )
    if source.casefold().count("after") < 3:
        findings.append("task dependency expressions are incomplete")
    if "milestone" not in source.casefold():
        findings.append("Release is not encoded as a milestone")
    return findings


def case_08(source: str) -> list[str]:
    findings = require_terms(
        source, "Effort", "Impact", "Search", "Bulk export", "Audit log", "Theme picker",
        "0.25", "0.82", "0.70", "0.45", "0.74", "0.20", "0.30",
    )
    if "x-axis" not in source.casefold() or "y-axis" not in source.casefold():
        findings.append("quadrant axes are not explicitly labeled")
    return findings


CONTRACTS = (
    CaseContract("case-01", "deliverables/standard/case-01.mmd", "flowchart", ("flowchart", "graph"), "colorset1", case_01, ("primary",)),
    CaseContract("case-02", "deliverables/extended/case-02.mmd", "sequenceDiagram", ("sequenceDiagram",), "colorset2", case_02, ("accent",)),
    CaseContract("case-03", "deliverables/standard/case-03.mmd", "erDiagram", ("erDiagram",), "colorset1", case_03, ("primary",)),
    CaseContract("case-04", "deliverables/extended/case-04.mmd", "sankey", ("sankey", "sankey-beta"), "colorset2", case_04, ("accent", "warning", "success", "special"), 4, 0.02),
    CaseContract("case-05", "deliverables/standard/case-05.mmd", "stateDiagram", ("stateDiagram", "stateDiagram-v2"), "colorset1", case_05, ("primary",)),
    CaseContract("case-06", "deliverables/standard/case-06.mmd", "xyChart", ("xychart", "xychart-beta"), "colorset1", case_06, ("primary",)),
    CaseContract("case-07", "deliverables/standard/case-07.mmd", "gantt", ("gantt",), "colorset1", case_07, ("primary",)),
    CaseContract("case-08", "deliverables/extended/case-08.mmd", "quadrantChart", ("quadrantChart",), "colorset2", case_08, ("accent", "warning", "success", "special"), 4, 0.15),
)


def first_declaration(source: str) -> str:
    lines = source.splitlines()
    index = 0
    if lines and lines[0].strip() == "---":
        index = 1
        while index < len(lines) and lines[index].strip() != "---":
            index += 1
        index += 1
    for line in lines[index:]:
        stripped = line.strip()
        if stripped and not stripped.startswith("%%"):
            return stripped.split()[0].rstrip(":")
    return ""


def has_error_svg(path: Path) -> bool:
    root = ET.parse(path).getroot()
    if root.get("aria-roledescription") == "error":
        return True
    for element in root.iter():
        classes = set((element.get("class") or "").casefold().split())
        if {"error-icon", "error-text"} & classes:
            return True
    return False


def render_source(source: Path, target: Path, *, transparent: bool = False) -> tuple[bool, str]:
    mmdc = shutil.which("mmdc")
    if mmdc:
        command = [mmdc]
    else:
        npx = shutil.which("npx")
        if not npx:
            return False, "neither mmdc nor npx is available"
        command = [npx, "-y", "@mermaid-js/mermaid-cli@11.16.0"]
    target.parent.mkdir(parents=True, exist_ok=True)
    render_command = [*command, "-i", str(source), "-o", str(target)]
    if transparent:
        render_command.extend(["-b", "transparent"])
    detail = ""
    completed = None
    for attempt in range(1, 3):
        try:
            completed = subprocess.run(
                render_command,
                text=True,
                encoding="utf-8",
                errors="replace",
                capture_output=True,
                check=False,
                timeout=180,
            )
            if completed.returncode == 0:
                break
            detail = (completed.stderr.strip() or completed.stdout.strip())[-2000:]
        except subprocess.TimeoutExpired as error:
            detail = f"renderer timeout: {error}"
        if attempt == 1:
            time.sleep(0.25)
    if completed is None or completed.returncode != 0:
        exit_code = completed.returncode if completed is not None else "timeout"
        return False, f"renderer exit {exit_code}: {detail}"
    if target.suffix.casefold() == ".svg":
        try:
            if has_error_svg(target):
                return False, "renderer emitted a Mermaid error SVG"
        except (ET.ParseError, OSError) as error:
            return False, f"invalid SVG: {error}"
    return True, ""


def write_gallery(render_dir: Path, records: list[dict[str, object]]) -> Path:
    render_dir.mkdir(parents=True, exist_ok=True)
    cards: list[str] = []
    for record in records:
        case_id = str(record["id"])
        svg_name = f"{case_id}.svg"
        cards.append(
            f'<article class="card" data-case-id="{escape(case_id)}">'
            f'<header><strong>{escape(case_id)}</strong><span>{escape(str(record["family"]))} · {escape(str(record["colorset"]))}</span></header>'
            f'<img src="{escape(svg_name)}" alt="Rendered {escape(case_id)} Mermaid diagram">'
            f'</article>'
        )
    html = """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Mermaid authoring evaluation</title><style>
*{box-sizing:border-box}body{margin:0;padding:24px;background:#f7f7f7;color:#333e48;font:16px Arial,sans-serif}
h1{margin:0 0 20px;font-size:24px}.grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:18px}
.card{min-width:0;background:#fff;border:1px solid #cfcfcf;border-radius:10px;padding:12px;box-shadow:0 2px 8px #0001}
header{display:flex;justify-content:space-between;gap:12px;align-items:baseline;margin-bottom:10px}header span{color:#696969;font-size:13px}
img{display:block;width:100%;height:390px;object-fit:contain;background:#fff;border:1px solid #e7e7e7}
@media(max-width:800px){.grid{grid-template-columns:1fr}img{height:340px}}
</style></head><body><h1>Mermaid authoring evaluation</h1><main class="grid">""" + "".join(cards) + "</main></body></html>\n"
    gallery = render_dir / "index.html"
    gallery.write_text(html, encoding="utf-8")
    return gallery


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Grade the isolated Mermaid authoring-selection evaluation.")
    parser.add_argument("workspace", type=Path, help="Isolated pi workspace containing deliverables/.")
    parser.add_argument("--output", type=Path, required=True, help="Write the JSON evaluation report.")
    parser.add_argument("--render-dir", type=Path, required=True, help="Write independent SVG renders and gallery here.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    workspace = args.workspace.resolve()
    output = args.output.resolve()
    render_dir = args.render_dir.resolve()
    manifest_path = workspace / "deliverables" / "selection.json"
    global_findings: list[str] = []
    manifest_cases: dict[str, dict[str, object]] = {}
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        cases = manifest.get("cases")
        if not isinstance(cases, list) or len(cases) != len(CONTRACTS):
            global_findings.append("selection.json must contain exactly eight cases")
        else:
            for item in cases:
                if isinstance(item, dict) and isinstance(item.get("id"), str):
                    manifest_cases[str(item["id"])] = item
    except (OSError, json.JSONDecodeError) as error:
        global_findings.append(f"selection.json is unreadable: {error}")

    records: list[dict[str, object]] = []
    for contract in CONTRACTS:
        source_path = workspace / contract.relative_path
        findings: list[str] = []
        try:
            source = source_path.read_text(encoding="utf-8")
        except OSError as error:
            source = ""
            findings.append(f"source missing or unreadable: {error}")

        declaration = first_declaration(source) if source else ""
        routing_ok = declaration in contract.declarations
        if not routing_ok:
            findings.append(f"declaration {declaration!r} does not match expected family {contract.family}")

        source_palette_ok = (
            'theme: "base"' in source
            and f'colorset: "{contract.colorset}"' in source
            and "%%{init:" not in source
        )
        source_colors = {color.casefold() for color in re.findall(r"#[0-9a-fA-F]{6}", source)}
        if contract.colorset == "colorset1":
            source_palette_ok = source_palette_ok and bool(source_colors & STANDARD_TOKENS) and not bool(source_colors & EXTENDED_TOKENS)
        else:
            source_palette_ok = source_palette_ok and bool(source_colors & EXTENDED_TOKENS)
        if not source_palette_ok:
            findings.append(f"palette contract failed for {contract.colorset}")

        fidelity_findings = contract.fidelity_check(source) if source else ["source unavailable for fidelity review"]
        fidelity_ok = not fidelity_findings
        findings.extend(fidelity_findings)

        rendered_path = render_dir / f"{contract.case_id}.svg"
        rendered_png = render_dir / f"{contract.case_id}.png"
        counterfactual_source_path = render_dir / f"{contract.case_id}.counterfactual.mmd"
        counterfactual_png = render_dir / f"{contract.case_id}.counterfactual.png"
        svg_ok, svg_error = render_source(source_path, rendered_path) if source else (False, "source unavailable")
        png_ok, png_error = (
            render_source(source_path, rendered_png, transparent=True)
            if source
            else (False, "source unavailable")
        )
        render_ok = svg_ok and png_ok
        if not svg_ok:
            findings.append(svg_error)
        if not png_ok:
            findings.append(png_error)

        visual_palette: dict[str, object] = {}
        counterfactual_replacements = 0
        if render_ok:
            counterfactual_source, counterfactual_replacements = make_counterfactual_source(
                source,
                contract.colorset,
            )
            counterfactual_source_path.write_text(counterfactual_source, encoding="utf-8")
            counterfactual_ok, counterfactual_error = render_source(
                counterfactual_source_path,
                counterfactual_png,
                transparent=True,
            )
            if counterfactual_ok and counterfactual_replacements:
                visual_contract = {
                    "requiredGroups": list(contract.required_visual_groups),
                    "minDistinctColors": contract.minimum_visible_colors,
                    "minPixelsPerColor": 24.0,
                    "minPaletteEffectivePixels": 64.0,
                    "minPaletteCoverageRatio": contract.minimum_palette_ratio,
                    "minInfluenceEffectivePixels": 32.0,
                    "minInfluenceRatio": 0.0005,
                }
                try:
                    visual_palette = evaluate_visual_palette(
                        rendered_png,
                        counterfactual_png,
                        contract.colorset,
                        visual_contract,
                    )
                except (OSError, ValueError) as error:
                    findings.append(f"visual palette analysis failed: {error}")
            else:
                findings.append(
                    counterfactual_error
                    or "counterfactual palette replaced no signature colors"
                )
        visual_palette_ok = bool(visual_palette.get("palette", {}).get("ok"))
        palette_influence_ok = bool(visual_palette.get("influence", {}).get("ok"))
        if render_ok and not visual_palette_ok:
            findings.append(f"rasterized SVG has insufficient visible {contract.colorset} coverage")
        if render_ok and not palette_influence_ok:
            findings.append("palette configuration did not change enough visible pixels")
        palette_ok = source_palette_ok and visual_palette_ok and palette_influence_ok

        manifest_item = manifest_cases.get(contract.case_id)
        manifest_declaration = ""
        manifest_colorset = ""
        if manifest_item:
            manifest_declaration = str(manifest_item.get("declaration", "")).split()[0].rstrip(":")
            manifest_colorset = str(manifest_item.get("colorset", ""))
            manifest_colorset = {"standard": "colorset1", "extended": "colorset2"}.get(
                manifest_colorset,
                manifest_colorset,
            )
        manifest_ok = bool(
            manifest_item
            and manifest_item.get("output") == contract.relative_path
            and manifest_item.get("selectedFamily") == contract.family
            and manifest_declaration == declaration
            and manifest_colorset == contract.colorset
            and isinstance(manifest_item.get("reason"), str)
            and str(manifest_item.get("reason")).strip()
        )
        if not manifest_ok:
            findings.append("selection.json entry does not match the source and contract")

        score = 0.0
        score += 5.0 if routing_ok else 0.0
        score += 2.5 if palette_ok else 0.0
        score += 2.5 if render_ok else 0.0
        score += 2.5 if fidelity_ok else 0.0
        records.append(
            {
                "id": contract.case_id,
                "source": contract.relative_path,
                "family": contract.family,
                "declaration": declaration,
                "colorset": contract.colorset,
                "routingOk": routing_ok,
                "paletteOk": palette_ok,
                "visualPaletteOk": visual_palette_ok,
                "paletteInfluenceOk": palette_influence_ok,
                "renderOk": render_ok,
                "renderedPaletteTokens": visual_palette.get("palette", {}).get("visibleTokens", []),
                "counterfactualReplacements": counterfactual_replacements,
                "visualPalette": visual_palette,
                "fidelityOk": fidelity_ok,
                "manifestOk": manifest_ok,
                "score": score,
                "maxScore": 12.5,
                "findings": findings,
            }
        )

    score = round(sum(float(record["score"]) for record in records), 2)
    grade = "A" if score >= 90 else "B" if score >= 80 else "C" if score >= 70 else "D"
    passed = (
        not global_findings
        and score >= 90
        and all(
            record["routingOk"]
            and record["paletteOk"]
            and record["renderOk"]
            and record["fidelityOk"]
            and record["manifestOk"]
            for record in records
        )
    )
    gallery = write_gallery(render_dir, records)
    result = {
        "ok": passed,
        "score": score,
        "maxScore": 100.0,
        "grade": grade,
        "routingAccuracy": f"{sum(bool(record['routingOk']) for record in records)}/8",
        "paletteAccuracy": f"{sum(bool(record['paletteOk']) for record in records)}/8",
        "renderAccuracy": f"{sum(bool(record['renderOk']) for record in records)}/8",
        "fidelityAccuracy": f"{sum(bool(record['fidelityOk']) for record in records)}/8",
        "manifestAccuracy": f"{sum(bool(record['manifestOk']) for record in records)}/8",
        "gallery": str(gallery),
        "globalFindings": global_findings,
        "cases": records,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
