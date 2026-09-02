#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

"""Validate an ECharts static SVG and its post-processed animated derivative."""

from __future__ import annotations

import argparse
import collections
import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any


NETWORK_RE = re.compile(
    r"(?:https?:)?//(?!www\.w3\.org/2000/svg)|<script\b|<image\b|"
    r"(?:xlink:)?href\s*=\s*['\"](?:https?:)?//",
    re.IGNORECASE,
)
SKIP_TAGS = {
    "defs",
    "clipPath",
    "mask",
    "pattern",
    "linearGradient",
    "radialGradient",
    "filter",
    "style",
    "script",
    "title",
    "desc",
}
DRAWABLE_TAGS = {"path", "rect", "circle", "ellipse", "line", "polyline", "polygon", "text"}
IGNORED_ATTRIBUTES = {
    "class",
    "data-easv-order",
    "data-easv-replay",
    "data-echarts-chart-type",
    "style",
    "pathLength",
}


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def element_signature(element: ET.Element) -> tuple[str, tuple[tuple[str, str], ...], str]:
    attributes = tuple(
        sorted(
            (local_name(name), value)
            for name, value in element.attrib.items()
            if local_name(name) not in IGNORED_ATTRIBUTES
        )
    )
    return local_name(element.tag), attributes, (element.text or "").strip()


def source_signatures(root: ET.Element) -> collections.Counter[tuple[str, tuple[tuple[str, str], ...], str]]:
    return collections.Counter(
        element_signature(element)
        for element in root.iter()
        if local_name(element.tag) != "style"
    )


def visible_drawables(root: ET.Element) -> list[ET.Element]:
    result: list[ET.Element] = []

    def walk(element: ET.Element, skipped: bool = False) -> None:
        tag = local_name(element.tag)
        in_skipped_subtree = skipped or tag in SKIP_TAGS
        if not in_skipped_subtree and tag in DRAWABLE_TAGS:
            result.append(element)
        for child in element:
            walk(child, in_skipped_subtree)

    walk(root)
    return result


def validate_pair(
    static_path: Path,
    animated_path: Path,
    chart_type: str,
    duration_ms: int,
    stagger_ms: int,
    max_delay_ms: int,
) -> dict[str, Any]:
    findings: list[str] = []
    evidence: dict[str, Any] = {}

    for label, path in (("static", static_path), ("animated", animated_path)):
        if not path.is_file():
            findings.append(f"Missing {label} SVG: {path}")
        elif path.stat().st_size == 0:
            findings.append(f"Empty {label} SVG: {path}")
    if findings:
        return {"passed": False, "findings": findings, "evidence": evidence}

    static_text = static_path.read_text(encoding="utf-8")
    animated_text = animated_path.read_text(encoding="utf-8")
    try:
        static_root = ET.fromstring(static_text)
        animated_root = ET.fromstring(animated_text)
    except ET.ParseError as exc:
        return {
            "passed": False,
            "findings": [f"Invalid SVG XML: {exc}"],
            "evidence": evidence,
        }

    if local_name(static_root.tag) != "svg" or local_name(animated_root.tag) != "svg":
        findings.append("Both documents must have an <svg> root.")

    missing_elements = list(
        (source_signatures(static_root) - source_signatures(animated_root)).elements()
    )
    if missing_elements:
        findings.append(
            f"Animated SVG changed or dropped {len(missing_elements)} source elements."
        )

    static_labels = [
        (element.text or "").strip()
        for element in static_root.iter()
        if local_name(element.tag) in {"title", "desc", "text"}
        and (element.text or "").strip()
    ]
    animated_labels = [
        (element.text or "").strip()
        for element in animated_root.iter()
        if local_name(element.tag) in {"title", "desc", "text"}
        and (element.text or "").strip()
    ]
    if static_labels != animated_labels:
        findings.append("Title, description, or chart labels were not preserved exactly.")

    root_classes = set(animated_root.attrib.get("class", "").split())
    expected_profile = f"easv-profile-{chart_type.replace('_', '-').lower()}"
    for class_name in {"echarts-animated-svg", expected_profile, "easv-playing"}:
        if class_name not in root_classes:
            findings.append(f"Animated SVG root is missing class: {class_name}")
    if animated_root.attrib.get("data-echarts-chart-type") != chart_type:
        findings.append(f"Expected chart profile {chart_type!r}.")
    if animated_root.attrib.get("data-easv-replay") != "remove-and-readd-easv-playing":
        findings.append("Animated SVG lacks the replay contract marker.")

    drawables = visible_drawables(animated_root)
    orders: list[int] = []
    delays: list[int] = []
    for element in drawables:
        classes = set(element.attrib.get("class", "").split())
        if "easv-mark" not in classes or not any(name.startswith("easv-") and name != "easv-mark" for name in classes):
            findings.append(f"Drawable <{local_name(element.tag)}> lacks an animation role.")
            continue
        try:
            order = int(element.attrib["data-easv-order"])
        except (KeyError, ValueError):
            findings.append(f"Drawable <{local_name(element.tag)}> lacks a valid order.")
            continue
        delay_match = re.search(r"--easv-delay:\s*(\d+)ms", element.attrib.get("style", ""))
        if not delay_match:
            findings.append(f"Drawable order {order} lacks a delay.")
            continue
        orders.append(order)
        delay = int(delay_match.group(1))
        delays.append(delay)
        expected_delay = min(order * stagger_ms, max_delay_ms)
        if delay != expected_delay:
            findings.append(
                f"Drawable order {order} delay is {delay} ms; expected {expected_delay} ms."
            )
    if orders != list(range(len(drawables))):
        findings.append("Drawable animation order is not contiguous document order.")

    required_css = (
        f"animation: easv-fade {duration_ms}ms",
        f"animation: easv-pop {duration_ms}ms",
        f"animation: easv-scale-y {duration_ms}ms",
        f"animation: easv-draw {duration_ms}ms",
        "@media (prefers-reduced-motion: reduce)",
        "animation: none !important",
        "opacity: 1 !important",
    )
    for marker in required_css:
        if marker not in animated_text:
            findings.append(f"Animation CSS is missing: {marker}")
    if NETWORK_RE.search(animated_text):
        findings.append("Animated SVG contains an external network or executable reference.")

    evidence.update(
        {
            "staticBytes": len(static_text.encode("utf-8")),
            "animatedBytes": len(animated_text.encode("utf-8")),
            "sourceGeometryPreserved": not missing_elements,
            "labelsPreserved": static_labels == animated_labels,
            "labelCount": len(static_labels),
            "drawableCount": len(drawables),
            "orders": orders,
            "delaysMs": delays,
            "chartType": animated_root.attrib.get("data-echarts-chart-type"),
            "durationMs": duration_ms,
            "staggerMs": stagger_ms,
            "maxDelayMs": max_delay_ms,
            "remoteReferenceCount": len(NETWORK_RE.findall(animated_text)),
        }
    )
    return {"passed": not findings, "findings": findings, "evidence": evidence}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("static_svg", type=Path)
    parser.add_argument("animated_svg", type=Path)
    parser.add_argument("--chart-type", required=True)
    parser.add_argument("--duration-ms", type=int, default=760)
    parser.add_argument("--stagger-ms", type=int, default=36)
    parser.add_argument("--max-delay-ms", type=int, default=1100)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()

    result = validate_pair(
        args.static_svg.resolve(),
        args.animated_svg.resolve(),
        args.chart_type,
        args.duration_ms,
        args.stagger_ms,
        args.max_delay_ms,
    )
    payload = {
        "schemaVersion": 1,
        "staticSvg": str(args.static_svg.resolve()),
        "animatedSvg": str(args.animated_svg.resolve()),
        **result,
    }
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2))
    return 0 if payload["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
