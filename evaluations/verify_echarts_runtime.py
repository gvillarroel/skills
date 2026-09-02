#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "pillow>=11.0.0",
#   "playwright>=1.52.0",
# ]
# ///

"""Independently verify a static/animated ECharts SVG artifact pair."""

from __future__ import annotations

import argparse
import collections
import hashlib
import io
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

from PIL import Image
from playwright.sync_api import sync_playwright


NETWORK_RE = re.compile(
    r"(?:https?:)?//(?!www\.w3\.org/2000/svg)|<script\b|<image\b|"
    r"(?:xlink:)?href\s*=\s*['\"](?:https?:)?//",
    re.IGNORECASE,
)
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


def image_stats(png: bytes) -> dict[str, Any]:
    image = Image.open(io.BytesIO(png)).convert("RGB")
    colors = image.resize((96, 64)).getcolors(maxcolors=96 * 64) or []
    nonwhite = sum(count for count, color in colors if min(color) < 245)
    return {
        "width": image.width,
        "height": image.height,
        "colorCount": len(colors),
        "nonwhiteSampleCount": nonwhite,
        "sha256": hashlib.sha256(png).hexdigest(),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("static_svg", type=Path)
    parser.add_argument("animated_svg", type=Path)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--screenshot", type=Path, required=True)
    args = parser.parse_args()

    static_path = args.static_svg.resolve()
    animated_path = args.animated_svg.resolve()
    findings: list[str] = []
    browser_errors: list[str] = []

    for path in (static_path, animated_path):
        if not path.is_file() or path.stat().st_size == 0:
            findings.append(f"Missing or empty SVG: {path}")

    evidence: dict[str, Any] = {}
    if not findings:
        static_text = static_path.read_text(encoding="utf-8")
        animated_text = animated_path.read_text(encoding="utf-8")
        try:
            static_root = ET.fromstring(static_text)
            animated_root = ET.fromstring(animated_text)
        except ET.ParseError as exc:
            findings.append(f"Invalid XML: {exc}")
        else:
            static_signatures = collections.Counter(
                element_signature(element)
                for element in static_root.iter()
                if local_name(element.tag) != "style"
            )
            animated_signatures = collections.Counter(
                element_signature(element)
                for element in animated_root.iter()
                if local_name(element.tag) != "style"
            )
            missing_geometry = list((static_signatures - animated_signatures).elements())
            if missing_geometry:
                findings.append(
                    f"Animated SVG changed or dropped {len(missing_geometry)} source elements."
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

            animation_markers = {
                "playingClass": "easv-playing" in animated_root.attrib.get("class", ""),
                "chartType": animated_root.attrib.get("data-echarts-chart-type"),
                "keyframes": "@keyframes easv-" in animated_text,
                "delays": "--easv-delay:" in animated_text,
                "reducedMotion": "prefers-reduced-motion: reduce" in animated_text,
                "remoteReferences": bool(NETWORK_RE.search(animated_text)),
            }
            if not animation_markers["playingClass"]:
                findings.append("Animated SVG lacks the active playback class.")
            if animation_markers["chartType"] != "bar":
                findings.append("Animated SVG does not identify the bar profile.")
            if not animation_markers["keyframes"] or not animation_markers["delays"]:
                findings.append("Animated SVG lacks keyframes or stagger delays.")
            if not animation_markers["reducedMotion"]:
                findings.append("Animated SVG lacks a reduced-motion fallback.")
            if animation_markers["remoteReferences"]:
                findings.append("Animated SVG contains an external network reference.")

            evidence["static"] = {
                "sourceElementCount": sum(static_signatures.values()),
                "animatedElementCount": sum(animated_signatures.values()),
                "labels": static_labels,
                "sourceGeometryPreserved": not missing_geometry,
                **animation_markers,
            }

    if not findings:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": 760, "height": 540})
            page.on("console", lambda message: browser_errors.append(
                f"console:{message.type}:{message.text}"
            ) if message.type == "error" else None)
            page.on("pageerror", lambda error: browser_errors.append(f"pageerror:{error}"))
            page.on("requestfailed", lambda request: browser_errors.append(
                f"requestfailed:{request.url}"
            ))
            page.goto(animated_path.as_uri(), wait_until="load")
            page.wait_for_timeout(100)
            early_png = page.screenshot()
            page.wait_for_timeout(2100)
            final_png = page.screenshot(path=str(args.screenshot.resolve()))
            dom = page.evaluate(
                """() => {
                  const svg = document.documentElement;
                  const marks = [...document.querySelectorAll('.easv-mark')];
                  const visible = marks.filter((node) => {
                    const style = getComputedStyle(node);
                    const box = node.getBoundingClientRect();
                    return Number(style.opacity) > 0.95 && box.width >= 0 && box.height >= 0;
                  });
                  return {
                    root: svg.localName,
                    markCount: marks.length,
                    visibleMarkCount: visible.length,
                    text: document.body?.innerText || svg.textContent || '',
                    overflowX: Math.max(0, document.documentElement.scrollWidth - innerWidth),
                  };
                }"""
            )
            browser.close()

            browser = playwright.chromium.launch(headless=True)
            context = browser.new_context(
                viewport={"width": 760, "height": 540},
                reduced_motion="reduce",
            )
            page = context.new_page()
            page.goto(animated_path.as_uri(), wait_until="load")
            page.wait_for_timeout(100)
            reduced = page.evaluate(
                """() => {
                  const marks = [...document.querySelectorAll('.easv-mark')];
                  return {
                    markCount: marks.length,
                    allVisible: marks.every((node) => Number(getComputedStyle(node).opacity) > 0.95),
                    animations: marks.reduce((sum, node) => sum + node.getAnimations().length, 0),
                  };
                }"""
            )
            browser.close()

            early_stats = image_stats(early_png)
            final_stats = image_stats(final_png)
            if dom["root"] != "svg":
                findings.append("Browser did not load the SVG document directly.")
            if dom["markCount"] < 6 or dom["visibleMarkCount"] != dom["markCount"]:
                findings.append("Not all animated marks reached their final visible state.")
            if final_stats["colorCount"] < 8 or final_stats["nonwhiteSampleCount"] < 100:
                findings.append("Final browser render appears blank or lacks chart color diversity.")
            if early_stats["sha256"] == final_stats["sha256"]:
                findings.append("Early and final browser frames are identical; animation was not observed.")
            if dom["overflowX"] != 0:
                findings.append("Browser render has horizontal overflow.")
            if not reduced["allVisible"] or reduced["animations"] != 0:
                findings.append("Reduced-motion mode does not expose the final static chart immediately.")
            for label in evidence["static"]["labels"]:
                if label not in dom["text"]:
                    findings.append(f"Rendered chart is missing label: {label}")
            evidence["browser"] = {
                "dom": dom,
                "earlyFrame": early_stats,
                "finalFrame": final_stats,
                "frameChanged": early_stats["sha256"] != final_stats["sha256"],
                "reducedMotion": reduced,
            }

    if browser_errors:
        findings.extend(browser_errors)

    report = {
        "schemaVersion": 1,
        "passed": not findings,
        "staticSvg": str(static_path),
        "animatedSvg": str(animated_path),
        "findings": findings,
        "browserErrors": browser_errors,
        "evidence": evidence,
    }
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
