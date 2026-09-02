#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Validate project-owned video overlay and Mermaid handoff artifacts."""

from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path
import xml.etree.ElementTree as ET


PROJECT = Path(__file__).resolve().parents[1]
SVG_DIR = PROJECT / "artifacts" / "svgs"
MANIFEST_DIR = PROJECT / "artifacts" / "manifests"
OVERLAY = PROJECT / "source" / "overlay.html"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_report(path: Path, report: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def validate_svg(path: Path, required_terms: list[str]) -> tuple[dict[str, object], list[str]]:
    failures: list[str] = []
    if not path.is_file():
        return {}, [f"Missing SVG: {path}"]
    text = path.read_text(encoding="utf-8")
    if "Syntax error" in text or "error-icon" in text and "class=\"error-icon\"" in text:
        failures.append(f"Mermaid error marker in {path.name}")
    try:
        root = ET.fromstring(text)
    except ET.ParseError as exc:
        return {}, [f"Invalid SVG {path.name}: {exc}"]
    if root.tag.rsplit("}", 1)[-1] != "svg":
        failures.append(f"Root is not SVG in {path.name}")
    view_box = root.attrib.get("viewBox", "")
    if len(view_box.split()) != 4:
        failures.append(f"Missing viewBox in {path.name}")
    title = next((child for child in root if child.tag.rsplit("}", 1)[-1] == "title"), None)
    desc = next((child for child in root if child.tag.rsplit("}", 1)[-1] == "desc"), None)
    if title is None or not "".join(title.itertext()).strip():
        failures.append(f"Missing accessible title in {path.name}")
    if desc is None or not "".join(desc.itertext()).strip():
        failures.append(f"Missing accessible description in {path.name}")
    if not root.attrib.get("aria-labelledby") or not root.attrib.get("aria-describedby"):
        failures.append(f"Missing rendered ARIA references in {path.name}")
    visible_text = " ".join(re.sub(r"\s+", " ", item).strip() for item in root.itertext())
    for term in required_terms:
        if term not in visible_text:
            failures.append(f"Missing visible term {term!r} in {path.name}")
    return {
        "path": path.relative_to(PROJECT).as_posix(),
        "sha256": sha256(path),
        "sizeBytes": path.stat().st_size,
        "viewBox": view_box,
        "title": "".join(title.itertext()).strip() if title is not None else None,
        "description": "".join(desc.itertext()).strip() if desc is not None else None,
        "requiredTerms": required_terms,
    }, failures


def main() -> int:
    mermaid_specs = {
        "lm-railroad.svg": ["contexto", "LM", "respuesta"],
        "agent-railroad.svg": ["objetivo", "observar", "LM", "actuar", "observacion", "terminar"],
        "harness-flow.svg": ["HARNESS", "AGENTE", "LM", "Acción", "Observación", "Permiso", "Herramienta", "Resultado"],
    }
    assets: list[dict[str, object]] = []
    failures: list[str] = []
    for name, terms in mermaid_specs.items():
        asset, asset_failures = validate_svg(SVG_DIR / name, terms)
        assets.append(asset)
        failures.extend(asset_failures)
    mermaid_report = {
        "schemaVersion": 1,
        "ok": not failures,
        "passed": not failures,
        "producerSkill": "mermaid",
        "assets": assets,
        "failures": failures,
    }
    write_report(MANIFEST_DIR / "mermaid-producer-report.json", mermaid_report)

    overlay_failures: list[str] = []
    overlay_text = OVERLAY.read_text(encoding="utf-8") if OVERLAY.is_file() else ""
    required_overlay_terms = [
        "¿QUÉ ES UN AGENTE?",
        "LM",
        "AGENTE",
        "HARNESS",
        "window.renderVideoFrame",
        "window.renderConceptFrame",
    ]
    for term in required_overlay_terms:
        if term not in overlay_text:
            overlay_failures.append(f"Overlay missing required term: {term}")
    for forbidden in ("requestAnimationFrame", "setInterval", "http://", "https://", "//cdn", "gsap"):
        if forbidden.lower() in overlay_text.lower():
            overlay_failures.append(f"Overlay contains forbidden runtime dependency: {forbidden}")
    overlay_report = {
        "schemaVersion": 1,
        "ok": not overlay_failures,
        "passed": not overlay_failures,
        "producerSkill": "repo-native",
        "fallbackReason": "Timecoded editorial captions and the persistent execution token are video-level composition, not diagram internals.",
        "asset": {
            "path": OVERLAY.relative_to(PROJECT).as_posix(),
            "sha256": sha256(OVERLAY) if OVERLAY.is_file() else None,
            "sizeBytes": OVERLAY.stat().st_size if OVERLAY.is_file() else 0,
            "clock": "master",
        },
        "failures": overlay_failures,
    }
    write_report(MANIFEST_DIR / "overlay-producer-report.json", overlay_report)
    combined = {
        "schemaVersion": 1,
        "ok": mermaid_report["ok"] and overlay_report["ok"],
        "passed": mermaid_report["ok"] and overlay_report["ok"],
        "reports": ["mermaid-producer-report.json", "overlay-producer-report.json"],
        "failures": failures + overlay_failures,
    }
    write_report(MANIFEST_DIR / "asset-validation.json", combined)
    print(json.dumps(combined, ensure_ascii=False, indent=2))
    return 0 if combined["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
