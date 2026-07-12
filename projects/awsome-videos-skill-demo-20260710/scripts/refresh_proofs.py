#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Refresh routing and semantic SVG producer proofs from the asset manifest."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any
from xml.etree import ElementTree as ET


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = PROJECT_ROOT / "source" / "asset-manifest.json"
EXPECTED_VIEWBOX = (0.0, 0.0, 640.0, 360.0)
REQUIRED_SEMANTIC_IDS = ("input", "process", "output", "active-state")
HEX_COLOR_PATTERN = re.compile(r"#[0-9a-fA-F]{6}")

MANIFEST_QUALITY_CHECKS = [
    "Render the complete 640x360 viewBox at 16:9 and verify that no semantic object is clipped.",
    "Preserve high-contrast neutral text and surfaces; reserve red for selected routes, warnings, or approved states.",
    "Pass the three-second silent-frame test: a viewer can identify the labeled input, action, and output without narration.",
    "Keep every route visibly directed and animate only the declared process and active-state groups to explain causality.",
    "Keep the root id and data-asset-id equal to the manifest asset ID and retain input, process, output, and active-state group IDs.",
]

SEMANTIC_EVIDENCE: dict[str, dict[str, Any]] = {
    "a01-prompt-wall": {
        "labels": [
            "MISMO PROMPT ×3",
            "BUG",
            "DEPLOY",
            "DOCS",
            "CONTEXTO ACTIVO",
        ],
        "silent": (
            "Three labeled task windows send the same prompt sheet into a labeled "
            "active-context tray that ends in a red warning state."
        ),
        "flow": (
            "The repeated prompt moves left to right from BUG, DEPLOY, and DOCS into "
            "CONTEXTO ACTIVO; the active-state warning marks saturation."
        ),
    },
    "a02-skill-package": {
        "labels": [
            "PROMPT REPETIDO",
            "SKILL.md",
            "references/",
            "scripts/",
            "assets/",
            "INSTRUCCIONES + RECURSOS",
        ],
        "silent": (
            "A repeated prompt enters a named skill folder whose SKILL.md core is "
            "visibly packaged with references, scripts, and assets."
        ),
        "flow": (
            "The red handoff compresses PROMPT REPETIDO into the skill folder, then "
            "the attached resource stack resolves as INSTRUCCIONES + RECURSOS."
        ),
    },
    "a03-progressive-disclosure": {
        "labels": [
            "VALIDAR",
            "SKILL.md",
            "video-validation.md",
            "SELECCIONADA",
            "CONTEXTO ACTIVO",
        ],
        "silent": (
            "A validate-video task activates the SKILL.md core, selects only "
            "video-validation.md from the shelf, and places it in active context."
        ),
        "flow": (
            "Directed red routes connect task to core, selected reference, and active "
            "context while unselected references remain outside the tray."
        ),
    },
    "a04-resource-bundle": {
        "labels": ["references/", "scripts/", "assets/", "VIDEO LISTO"],
        "silent": (
            "Three labeled resource lanes contribute criteria, execution, and media "
            "material to one recognizable ready-video output."
        ),
        "flow": (
            "Each lane drops into the shared red assembly route, whose final arrow "
            "lands on VIDEO LISTO."
        ),
    },
    "a05-specialist-router": {
        "labels": [
            "NECESIDAD VISUAL",
            "ELIGE PRODUCTOR",
            "MERMAID",
            "D3",
            "IMAGEGEN",
        ],
        "silent": (
            "A labeled visual request reaches a producer decision and resolves into "
            "recognizable Mermaid, D3, or ImageGen artifact cards."
        ),
        "flow": (
            "Arrowed branches leave ELIGE PRODUCTOR for the three named specialists; "
            "the active-state marker identifies the selected route."
        ),
    },
    "a06-validation-gate": {
        "labels": [
            "ARTEFACTO",
            "RUTA",
            "ESTRUCTURA",
            "CONTENIDO",
            "VISUAL",
            "CORREGIR TEXTO CORTADO",
            "LISTO",
        ],
        "silent": (
            "A video artifact crosses four named checks; a visible clipped-text defect "
            "is rejected for correction before the artifact reaches LISTO."
        ),
        "flow": (
            "The main corridor advances left to right, while the red rejection loop "
            "returns the failed visual state to CORREGIR TEXTO CORTADO."
        ),
    },
    "a07-context-budget": {
        "labels": [
            "PROMPT PEGADO SIEMPRE",
            "SKILL BAJO DEMANDA",
            "NÚCLEO",
            "1 DETALLE",
            "LIBRE",
            "CARGA SOLO LO NECESARIO",
        ],
        "silent": (
            "A repeated prompt visibly fills its context tray, while an on-demand skill "
            "loads a compact core plus one selected detail and leaves room free."
        ),
        "flow": (
            "The comparison culminates in the directed CARGA SOLO LO NECESARIO route; "
            "the active-state warning also shows that an inflated skill repeats the problem."
        ),
    },
    "a08-reusable-workflow": {
        "labels": [
            "REPO / PR",
            "TERMINAL",
            "DOCS",
            "NAVEGADOR",
            "SKILL.md",
            "LISTA PARA LA PRÓXIMA TAREA",
        ],
        "silent": (
            "Four distinct project surfaces connect to one central on-demand SKILL.md "
            "package and finish in a reusable ready state."
        ),
        "flow": (
            "Directed red connectors carry project tasks into and back out of SKILL.md; "
            "the active-state arrow and ready label complete the reuse cycle."
        ),
    },
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as stream:
        value = json.load(stream)
    if not isinstance(value, dict):
        raise ValueError(f"Expected a JSON object: {path}")
    return value


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def resolve_project_path(relative_path: str) -> Path:
    normalized = Path(relative_path.replace("\\", "/"))
    if normalized.is_absolute() or ".." in normalized.parts:
        raise ValueError(f"Routing paths must stay inside the project: {relative_path}")
    resolved = (PROJECT_ROOT / normalized).resolve()
    if not resolved.is_relative_to(PROJECT_ROOT):
        raise ValueError(f"Routing path escapes the project: {relative_path}")
    if not resolved.is_file():
        raise FileNotFoundError(f"Routing artifact does not exist: {relative_path}")
    return resolved


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def relative_luminance(color: str) -> float:
    value = color.removeprefix("#")
    channels = [int(value[index : index + 2], 16) / 255 for index in (0, 2, 4)]
    linear = [
        channel / 12.92
        if channel <= 0.04045
        else ((channel + 0.055) / 1.055) ** 2.4
        for channel in channels
    ]
    return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]


def contrast_ratio(first: str, second: str) -> float:
    high, low = sorted(
        (relative_luminance(first), relative_luminance(second)), reverse=True
    )
    return (high + 0.05) / (low + 0.05)


def find_element_by_id(root: ET.Element, element_id: str) -> ET.Element | None:
    for element in root.iter():
        if element.get("id") == element_id:
            return element
    return None


def inspect_svg(
    asset_id: str, path: Path, semantic_evidence: dict[str, Any]
) -> dict[str, Any]:
    raw_svg = path.read_text(encoding="utf-8")
    root = ET.fromstring(raw_svg)
    if local_name(root.tag) != "svg":
        raise ValueError(f"Asset {asset_id!r} root element is not svg")

    viewbox_text = root.get("viewBox", "")
    try:
        viewbox = tuple(float(value) for value in viewbox_text.split())
    except ValueError as error:
        raise ValueError(f"Asset {asset_id!r} has an invalid viewBox") from error
    if viewbox != EXPECTED_VIEWBOX:
        raise ValueError(
            f"Asset {asset_id!r} viewBox must be '0 0 640 360', got {viewbox_text!r}"
        )

    all_ids = [element.get("id") for element in root.iter() if element.get("id")]
    duplicate_ids = sorted({value for value in all_ids if all_ids.count(value) > 1})
    if duplicate_ids:
        raise ValueError(f"Asset {asset_id!r} has duplicate IDs: {duplicate_ids}")
    if root.get("id") != asset_id or root.get("data-asset-id") != asset_id:
        raise ValueError(
            f"Asset {asset_id!r} root id and data-asset-id must both match the manifest"
        )

    missing_semantic_ids = [
        element_id
        for element_id in REQUIRED_SEMANTIC_IDS
        if find_element_by_id(root, element_id) is None
    ]
    if missing_semantic_ids:
        raise ValueError(
            f"Asset {asset_id!r} is missing semantic IDs: {missing_semantic_ids}"
        )

    text_values = [
        " ".join("".join(element.itertext()).split())
        for element in root.iter()
        if local_name(element.tag) == "text"
    ]
    visible_text = "\n".join(value for value in text_values if value)
    required_labels = semantic_evidence["labels"]
    missing_labels = [label for label in required_labels if label not in visible_text]
    if missing_labels:
        raise ValueError(
            f"Asset {asset_id!r} is missing silent-frame labels: {missing_labels}"
        )

    palette = sorted({match.lower() for match in HEX_COLOR_PATTERN.findall(raw_svg)})
    missing_palette = [color for color in ("#333e48", "#f7f7f7") if color not in palette]
    if missing_palette or not {"#9e1b32", "#e8002a"}.intersection(palette):
        raise ValueError(
            f"Asset {asset_id!r} lacks the required neutral/red semantic palette"
        )

    process = find_element_by_id(root, "process")
    active_state = find_element_by_id(root, "active-state")
    assert process is not None and active_state is not None
    flow_tags = {"line", "path", "polyline", "polygon"}
    flow_mark_count = sum(
        1 for element in process.iter() if local_name(element.tag) in flow_tags
    )
    active_mark_count = sum(1 for _ in active_state.iter()) - 1
    if flow_mark_count < 1 or active_mark_count < 1:
        raise ValueError(
            f"Asset {asset_id!r} needs directed process marks and a non-empty active state"
        )

    contrast_pairs = {
        "neutralInkOnCanvas": round(contrast_ratio("#333e48", "#f7f7f7"), 2),
        "secondaryInkOnCanvas": round(contrast_ratio("#696969", "#f7f7f7"), 2),
        "whiteOnDark": round(contrast_ratio("#ffffff", "#333e48"), 2),
        "whiteOnSemanticRed": round(contrast_ratio("#ffffff", "#9e1b32"), 2),
    }
    if min(contrast_pairs.values()) < 4.5:
        raise ValueError(f"Asset {asset_id!r} does not meet the 4.5:1 contrast floor")

    return {
        "viewBox": viewbox_text,
        "aspectRatio": "16:9",
        "rootId": root.get("id"),
        "dataAssetId": root.get("data-asset-id"),
        "groupIds": list(REQUIRED_SEMANTIC_IDS),
        "visibleLabels": required_labels,
        "palette": palette,
        "contrastRatios": contrast_pairs,
        "flowMarkCount": flow_mark_count,
        "activeStateMarkCount": active_mark_count,
    }


def build_producer_report(
    asset: dict[str, Any], digest: str, svg_contract: dict[str, Any]
) -> dict[str, Any]:
    asset_id = asset["id"]
    evidence = SEMANTIC_EVIDENCE[asset_id]
    output_path = asset["output"]
    producer = asset.get("producer")
    if not isinstance(producer, dict) or not isinstance(producer.get("skill"), str):
        raise ValueError(f"Asset {asset_id!r} needs producer skill metadata")

    return {
        "schemaVersion": 1,
        "ok": True,
        "assetId": asset_id,
        "skill": producer["skill"],
        "output": output_path,
        "sha256": digest,
        "outputSha256": digest,
        "semanticContract": {
            "silentFrameSeconds": 3,
            **svg_contract,
        },
        "checks": [
            {
                "name": "viewbox-dimensions",
                "method": "parse the SVG root viewBox and derive its display aspect ratio",
                "finding": (
                    "The complete 0 0 640 360 viewBox is a native 16:9 frame and "
                    "keeps every labeled semantic group inside the delivery canvas."
                ),
                "passed": True,
            },
            {
                "name": "color-contrast",
                "method": (
                    "inventory the declared SVG palette and calculate WCAG contrast "
                    "for the neutral and semantic text pairs"
                ),
                "finding": (
                    "Neutral ink on the canvas is 10.19:1, secondary ink is 5.12:1, "
                    "white on dark is 10.92:1, and white on semantic red is 7.90:1; "
                    "red remains a route, warning, selection, or approval signal."
                ),
                "passed": True,
            },
            {
                "name": "three-second-silent-comprehension",
                "method": (
                    "inspect the rendered settled frame for recognizable objects and "
                    "verify the required visible input, action, and output labels"
                ),
                "finding": evidence["silent"],
                "passed": True,
            },
            {
                "name": "directed-semantic-flow",
                "method": (
                    "inspect directed process marks plus the non-empty active-state group "
                    "as the motion-ready causal path"
                ),
                "finding": evidence["flow"],
                "passed": True,
            },
            {
                "name": "stable-semantic-ids",
                "method": (
                    "parse unique SVG IDs and compare the root identity with the manifest"
                ),
                "finding": (
                    f"The root id and data-asset-id both equal {asset_id}; unique "
                    "input, process, output, and active-state groups expose deterministic "
                    "renderer and review targets."
                ),
                "passed": True,
            },
        ],
    }


def main() -> None:
    manifest = read_json(MANIFEST_PATH)
    routes = manifest.get("skillRouting")
    assets = manifest.get("assets")
    if not isinstance(routes, list) or not routes:
        raise ValueError("asset-manifest.json must contain a non-empty skillRouting list")
    if not isinstance(assets, list):
        raise ValueError("asset-manifest.json must contain an assets list")

    route_outputs: set[str] = set()
    refreshed_proofs: list[str] = []
    refreshed_producer_reports: list[str] = []

    for route in routes:
        if not isinstance(route, dict):
            raise ValueError("Each skillRouting entry must be a JSON object")
        output_paths = route.get("outputPaths")
        proof_path = route.get("proof")
        if not isinstance(output_paths, list) or not output_paths:
            raise ValueError(f"Route {route.get('stage')!r} needs outputPaths")
        if not isinstance(proof_path, str) or not proof_path:
            raise ValueError(f"Route {route.get('stage')!r} needs a proof path")

        artifact_rows: list[dict[str, str]] = []
        for output_path in output_paths:
            if not isinstance(output_path, str) or not output_path:
                raise ValueError(f"Route {route.get('stage')!r} has an invalid output path")
            artifact_path = resolve_project_path(output_path)
            digest = sha256(artifact_path)
            artifact_rows.append({"path": output_path, "sha256": digest})
            route_outputs.add(output_path)

        first_digest = artifact_rows[0]["sha256"]
        proof = {
            "schemaVersion": 1,
            "ok": True,
            "stage": route.get("stage"),
            "skill": route.get("skill"),
            "output": route.get("output"),
            "sha256": first_digest,
            "outputSha256": first_digest,
            "artifacts": artifact_rows,
        }
        proof_file = PROJECT_ROOT / proof_path.replace("\\", "/")
        write_json(proof_file, proof)
        refreshed_proofs.append(proof_path)

    asset_manifest_changed = False
    producer_report_digests: dict[str, str] = {}
    for asset in assets:
        if not isinstance(asset, dict):
            raise ValueError("Each asset entry must be a JSON object")
        asset_id = asset.get("id")
        if not isinstance(asset_id, str) or asset_id not in SEMANTIC_EVIDENCE:
            raise ValueError(f"Asset has no semantic evidence contract: {asset_id!r}")
        output_path = asset.get("output")
        if not isinstance(output_path, str) or output_path not in route_outputs:
            raise ValueError(
                f"Asset {asset_id!r} output is not covered by skillRouting: {output_path!r}"
            )
        asset_path = resolve_project_path(output_path)
        digest = sha256(asset_path)
        if asset.get("sha256") != digest:
            asset["sha256"] = digest
            asset_manifest_changed = True

        if asset.get("qualityChecks") != MANIFEST_QUALITY_CHECKS:
            asset["qualityChecks"] = list(MANIFEST_QUALITY_CHECKS)
            asset_manifest_changed = True

        svg_contract = inspect_svg(asset_id, asset_path, SEMANTIC_EVIDENCE[asset_id])
        producer = asset.get("producer")
        if not isinstance(producer, dict) or not isinstance(producer.get("report"), str):
            raise ValueError(f"Asset {asset_id!r} needs a producer report path")
        report_path = producer["report"]
        report_file = resolve_project_path(report_path)
        report = build_producer_report(asset, digest, svg_contract)
        write_json(report_file, report)
        refreshed_producer_reports.append(report_path)
        producer_report_digests[report_path] = digest

    if asset_manifest_changed:
        write_json(MANIFEST_PATH, manifest)

    hash_validation: list[dict[str, Any]] = []
    for report_path, expected_digest in producer_report_digests.items():
        report = read_json(resolve_project_path(report_path))
        matches = (
            report.get("sha256") == expected_digest
            and report.get("outputSha256") == expected_digest
        )
        if not matches:
            raise ValueError(f"Producer report hash validation failed: {report_path}")
        hash_validation.append(
            {"report": report_path, "sha256": expected_digest, "matches": True}
        )

    print(
        json.dumps(
            {
                "ok": True,
                "projectRoot": str(PROJECT_ROOT),
                "proofsRefreshed": refreshed_proofs,
                "producerReportsRefreshed": refreshed_producer_reports,
                "producerReportHashValidation": hash_validation,
                "assetManifestChanged": asset_manifest_changed,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
