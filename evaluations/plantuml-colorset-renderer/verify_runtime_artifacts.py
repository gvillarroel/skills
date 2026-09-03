#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "pillow>=11.0.0",
#   "playwright>=1.52.0",
# ]
# ///

"""Independently validate PlantUML renderer report, SVG, PNG, and browser output."""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

from PIL import Image
from playwright.sync_api import Browser, Page, sync_playwright


EXPECTED_DIAGRAMS = {
    "class": {
        "source": "class.puml",
        "type": "CLASS",
        "labels": ["Runtime Class", "Order", "Payment", "authorize(): bool", "uses"],
    },
    "mindmap": {
        "source": "mindmap.puml",
        "type": "MINDMAP",
        "labels": ["Runtime Mindmap", "Renderer", "Colorset 2 theme", "SVG", "PNG"],
    },
    "sequence": {
        "source": "sequence.puml",
        "type": "SEQUENCE",
        "labels": ["Runtime Sequence", "User", "API", "DB", "create order", "accepted"],
    },
}
EXPECTED_COLORSET2_TOKENS = {
    "#9E1B32",
    "#007298",
    "#E77204",
    "#45842A",
    "#00ACE6",
    "#652F6C",
    "#333E48",
    "#696969",
    "#FFCCD5",
    "#CDF3FF",
    "#FFE5CC",
    "#DBFFCC",
    "#F9CCFF",
}
REMOTE_VALUE_RE = re.compile(r"^(?:https?:)?//", re.IGNORECASE)
REMOTE_STYLE_RE = re.compile(r"url\(\s*['\"]?(?:https?:)?//", re.IGNORECASE)


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def image_stats(data: bytes) -> dict[str, Any]:
    with Image.open(io.BytesIO(data)) as image:
        image.load()
        rgb = image.convert("RGB")
        sample = rgb.resize((96, 64))
        colors = sample.getcolors(maxcolors=96 * 64) or []
        nonwhite = sum(count for count, color in colors if min(color) < 245)
        return {
            "width": rgb.width,
            "height": rgb.height,
            "mode": image.mode,
            "format": image.format,
            "colorCount": len(colors),
            "nonwhiteSampleCount": nonwhite,
            "sha256": hashlib.sha256(data).hexdigest(),
        }


def parse_size(value: str | None) -> float:
    if not value:
        return 0.0
    match = re.match(r"^\s*([0-9]+(?:\.[0-9]+)?)", value)
    return float(match.group(1)) if match else 0.0


def attach_browser_errors(page: Page, errors: list[str], diagram_id: str, viewport: str) -> None:
    page.on(
        "console",
        lambda message: errors.append(
            f"{diagram_id}/{viewport}:console:{message.type}:{message.text}"
        )
        if message.type == "error"
        else None,
    )
    page.on(
        "pageerror",
        lambda error: errors.append(f"{diagram_id}/{viewport}:pageerror:{error}"),
    )
    page.on(
        "requestfailed",
        lambda request: errors.append(
            f"{diagram_id}/{viewport}:requestfailed:{request.url}"
        ),
    )


def browser_sample(
    browser: Browser,
    svg_path: Path,
    diagram_id: str,
    viewport_name: str,
    viewport: dict[str, int],
    errors: list[str],
    screenshot: Path | None,
) -> dict[str, Any]:
    context = browser.new_context(viewport=viewport)
    page = context.new_page()
    attach_browser_errors(page, errors, diagram_id, viewport_name)
    page.goto(svg_path.as_uri(), wait_until="load")
    page.wait_for_timeout(100)
    png = page.screenshot(path=str(screenshot.resolve()) if screenshot else None)
    dom = page.evaluate(
        """() => {
          const root = document.documentElement;
          const box = root.getBoundingClientRect();
          return {
            root: root.localName,
            diagramType: root.getAttribute('data-diagram-type'),
            text: root.textContent || '',
            width: box.width,
            height: box.height,
            viewportWidth: innerWidth,
            viewportHeight: innerHeight,
            scrollWidth: document.documentElement.scrollWidth,
            scrollHeight: document.documentElement.scrollHeight,
            visible: box.width > 0 && box.height > 0,
          };
        }"""
    )
    context.close()
    return {"viewport": viewport, "dom": dom, "frame": image_stats(png)}


def validate_report(report: dict[str, Any], findings: list[str]) -> dict[str, dict[str, Any]]:
    expected_scalars = {
        "ok": True,
        "colorset": "colorset2",
        "theme": "assets/themes/cs2.puml",
        "engine": "kroki",
        "sourceDiagramCount": 3,
        "renderedDiagramCount": 3,
        "coveredDiagramCount": 3,
        "expectedUnavailableDiagramCount": 0,
        "renderedOutputCount": 6,
        "failedDiagramCount": 0,
    }
    for field, expected in expected_scalars.items():
        if report.get(field) != expected:
            findings.append(f"report.{field} is {report.get(field)!r}; expected {expected!r}")
    if report.get("formats") != ["svg", "png"]:
        findings.append("report.formats must preserve the requested ['svg', 'png'] order")

    results = report.get("results")
    if not isinstance(results, list) or len(results) != 3:
        findings.append("report.results must contain exactly three entries")
        return {}
    by_id: dict[str, dict[str, Any]] = {}
    for result in results:
        if not isinstance(result, dict) or not isinstance(result.get("diagramId"), str):
            findings.append("each report result must be an object with a diagramId")
            continue
        diagram_id = result["diagramId"]
        if diagram_id in by_id:
            findings.append(f"duplicate report diagramId: {diagram_id}")
        by_id[diagram_id] = result
    if set(by_id) != set(EXPECTED_DIAGRAMS):
        findings.append(
            f"report diagram IDs are {sorted(by_id)}; expected {sorted(EXPECTED_DIAGRAMS)}"
        )
    return by_id


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True, help="PlantUML output directory")
    parser.add_argument("--report", type=Path, required=True, help="Evaluator JSON report")
    parser.add_argument("--screenshot-dir", type=Path, required=True)
    args = parser.parse_args()

    output = args.output.resolve()
    findings: list[str] = []
    browser_errors: list[str] = []
    evidence: dict[str, Any] = {"diagrams": {}}

    report_path = output / "report.json"
    validation_path = output / "validation.json"
    for path in (report_path, validation_path):
        if not path.is_file() or path.stat().st_size == 0:
            findings.append(f"missing or empty JSON artifact: {path}")
    if findings:
        report: dict[str, Any] = {}
        validation: dict[str, Any] = {}
    else:
        try:
            report = json.loads(report_path.read_text(encoding="utf-8-sig"))
            validation = json.loads(validation_path.read_text(encoding="utf-8-sig"))
        except (OSError, json.JSONDecodeError) as error:
            findings.append(f"could not parse report or validation JSON: {error}")
            report = {}
            validation = {}

    by_id = validate_report(report, findings) if report else {}
    expected_validation = {
        "ok": True,
        "colorset": "colorset2",
        "checkedDiagramCount": 3,
        "expectedFormats": ["png", "svg"],
        "findings": [],
    }
    for field, expected in expected_validation.items():
        if validation.get(field) != expected:
            findings.append(
                f"validation.{field} is {validation.get(field)!r}; expected {expected!r}"
            )

    static_ok = bool(by_id) and not findings
    if by_id:
        for diagram_id, expected in EXPECTED_DIAGRAMS.items():
            result = by_id.get(diagram_id, {})
            if result.get("source") != expected["source"]:
                findings.append(f"{diagram_id}: wrong source path in report")
            for field, expected_value in {
                "status": "rendered",
                "themeMode": "inject",
                "themeApplied": True,
                "availability": "available",
                "requestedFormats": ["svg", "png"],
                "expectedFormats": ["svg", "png"],
                "skippedFormats": [],
                "krokiDiagramType": "plantuml",
                "ok": True,
                "error": None,
            }.items():
                if result.get(field) != expected_value:
                    findings.append(
                        f"{diagram_id}: {field} is {result.get(field)!r}; expected {expected_value!r}"
                    )
            outputs = result.get("outputs") if isinstance(result.get("outputs"), list) else []
            by_format = {
                item.get("format"): item for item in outputs if isinstance(item, dict)
            }
            if set(by_format) != {"svg", "png"}:
                findings.append(f"{diagram_id}: output formats must be exactly svg and png")

            svg_path = output / "svg" / f"{diagram_id}.svg"
            png_path = output / "png" / f"{diagram_id}.png"
            diagram_evidence: dict[str, Any] = {}
            for fmt, path in (("svg", svg_path), ("png", png_path)):
                if not path.is_file() or path.stat().st_size == 0:
                    findings.append(f"{diagram_id}: missing or empty {fmt} artifact")
                    continue
                item = by_format.get(fmt, {})
                expected_relative = f"{fmt}/{diagram_id}.{fmt}"
                if item.get("path") != expected_relative:
                    findings.append(f"{diagram_id}: wrong {fmt} output path in report")
                if item.get("engine") != "kroki":
                    findings.append(f"{diagram_id}: wrong {fmt} render engine in report")
                if item.get("size_bytes") != path.stat().st_size:
                    findings.append(f"{diagram_id}: stale {fmt} byte count in report")

            if svg_path.is_file() and svg_path.stat().st_size:
                svg_text = svg_path.read_text(encoding="utf-8")
                try:
                    root = ET.fromstring(svg_text)
                except ET.ParseError as error:
                    findings.append(f"{diagram_id}: invalid SVG XML: {error}")
                else:
                    text_content = " ".join("".join(root.itertext()).split())
                    if local_name(root.tag) != "svg":
                        findings.append(f"{diagram_id}: XML root is not svg")
                    if root.attrib.get("data-diagram-type") != expected["type"]:
                        findings.append(f"{diagram_id}: wrong data-diagram-type")
                    width = parse_size(root.attrib.get("width"))
                    height = parse_size(root.attrib.get("height"))
                    view_box = root.attrib.get("viewBox", "").split()
                    if width < 100 or height < 100 or len(view_box) != 4:
                        findings.append(f"{diagram_id}: SVG dimensions or viewBox are invalid")
                    for label in expected["labels"]:
                        if label not in text_content:
                            findings.append(f"{diagram_id}: SVG is missing label {label!r}")
                    uppercase = svg_text.upper()
                    tokens = sorted(
                        token for token in EXPECTED_COLORSET2_TOKENS if token in uppercase
                    )
                    if not tokens:
                        findings.append(f"{diagram_id}: SVG lacks a Colorset 2 palette token")
                    if "SYNTAX ERROR" in uppercase or ">ERROR LINE" in uppercase:
                        findings.append(f"{diagram_id}: SVG contains a PlantUML error marker")
                    for element in root.iter():
                        for name, value in element.attrib.items():
                            if local_name(name) == "href" and REMOTE_VALUE_RE.match(value):
                                findings.append(
                                    f"{diagram_id}: SVG contains a remote href {value!r}"
                                )
                            if local_name(name) == "style" and REMOTE_STYLE_RE.search(value):
                                findings.append(f"{diagram_id}: SVG style contains a remote URL")
                    diagram_evidence["svg"] = {
                        "bytes": svg_path.stat().st_size,
                        "sha256": sha256_file(svg_path),
                        "width": width,
                        "height": height,
                        "viewBox": root.attrib.get("viewBox"),
                        "diagramType": root.attrib.get("data-diagram-type"),
                        "colorsetTokens": tokens,
                        "labels": expected["labels"],
                    }

            if png_path.is_file() and png_path.stat().st_size:
                png_data = png_path.read_bytes()
                if not png_data.startswith(b"\x89PNG\r\n\x1a\n"):
                    findings.append(f"{diagram_id}: invalid PNG signature")
                try:
                    stats = image_stats(png_data)
                except Exception as error:  # Pillow raises format-specific subclasses.
                    findings.append(f"{diagram_id}: invalid PNG: {error}")
                else:
                    if stats["format"] != "PNG" or stats["width"] < 100 or stats["height"] < 100:
                        findings.append(f"{diagram_id}: PNG dimensions or format are invalid")
                    if stats["colorCount"] < 8 or stats["nonwhiteSampleCount"] < 100:
                        findings.append(f"{diagram_id}: PNG appears blank or visually incomplete")
                    diagram_evidence["png"] = {
                        "bytes": png_path.stat().st_size,
                        **stats,
                    }
            evidence["diagrams"][diagram_id] = diagram_evidence

    static_ok = static_ok and not findings
    if static_ok:
        args.screenshot_dir.mkdir(parents=True, exist_ok=True)
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            for diagram_id, expected in EXPECTED_DIAGRAMS.items():
                svg_path = output / "svg" / f"{diagram_id}.svg"
                desktop = browser_sample(
                    browser,
                    svg_path,
                    diagram_id,
                    "desktop",
                    {"width": 1024, "height": 768},
                    browser_errors,
                    args.screenshot_dir / f"{diagram_id}-desktop.png",
                )
                mobile = browser_sample(
                    browser,
                    svg_path,
                    diagram_id,
                    "mobile",
                    {"width": 390, "height": 844},
                    browser_errors,
                    args.screenshot_dir / f"{diagram_id}-mobile.png",
                )
                for viewport_name, sample in (("desktop", desktop), ("mobile", mobile)):
                    dom = sample["dom"]
                    frame = sample["frame"]
                    if dom["root"] != "svg" or dom["diagramType"] != expected["type"]:
                        findings.append(
                            f"{diagram_id}/{viewport_name}: browser loaded the wrong root or diagram type"
                        )
                    if not dom["visible"] or dom["width"] < 100 or dom["height"] < 100:
                        findings.append(
                            f"{diagram_id}/{viewport_name}: SVG is not visibly rendered"
                        )
                    for label in expected["labels"]:
                        if label not in dom["text"]:
                            findings.append(
                                f"{diagram_id}/{viewport_name}: rendered SVG is missing {label!r}"
                            )
                    if frame["colorCount"] < 8 or frame["nonwhiteSampleCount"] < 100:
                        findings.append(
                            f"{diagram_id}/{viewport_name}: screenshot appears blank"
                        )
                evidence["diagrams"][diagram_id]["browser"] = {
                    "desktop": desktop,
                    "mobile": mobile,
                }
            browser.close()

    if browser_errors:
        findings.extend(browser_errors)
    result = {
        "schemaVersion": 1,
        "passed": not findings,
        "output": str(output),
        "findings": findings,
        "browserErrors": browser_errors,
        "evidence": evidence,
    }
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
