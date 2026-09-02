#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "pillow>=11.0.0",
#   "playwright>=1.52.0",
# ]
# ///

"""Browser-check a generated standalone procedural SVG."""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

from PIL import Image
from playwright.sync_api import Browser, sync_playwright


EXPECTED_METADATA = {
    "data-pattern-id": "procedural-svg-phyllotaxis-bloom",
    "data-seed": "104729",
    "data-palette": "colorset2",
    "data-motion": "full",
    "data-duration-ms": "7200",
    "data-loop": "true",
    "data-deterministic": "true",
    "data-standalone": "true",
}


def image_stats(png: bytes) -> dict[str, Any]:
    image = Image.open(io.BytesIO(png)).convert("RGB")
    colors = image.resize((96, 64)).getcolors(maxcolors=96 * 64) or []
    return {
        "width": image.width,
        "height": image.height,
        "colorCount": len(colors),
        "nonwhiteSampleCount": sum(count for count, color in colors if min(color) < 245),
        "sha256": hashlib.sha256(png).hexdigest(),
    }


def attach_error_capture(page, errors: list[str]) -> None:
    page.on(
        "console",
        lambda message: errors.append(f"console:{message.type}:{message.text}")
        if message.type == "error"
        else None,
    )
    page.on("pageerror", lambda error: errors.append(f"pageerror:{error}"))
    page.on(
        "requestfailed",
        lambda request: errors.append(f"requestfailed:{request.url}"),
    )


def sample_normal(
    browser: Browser,
    uri: str,
    viewport: dict[str, int],
    errors: list[str],
    screenshot: Path | None = None,
) -> dict[str, Any]:
    context = browser.new_context(viewport=viewport, reduced_motion="no-preference")
    page = context.new_page()
    attach_error_capture(page, errors)
    page.goto(uri, wait_until="load")
    page.wait_for_timeout(200)
    early_png = page.screenshot()
    page.wait_for_timeout(1800)
    final_png = page.screenshot(path=str(screenshot.resolve()) if screenshot else None)
    dom = page.evaluate(
        """() => {
          const root = document.documentElement;
          const motion = document.querySelector('[data-motion-layer="animated"]');
          const reduced = document.querySelector('[data-motion-layer="reduced"]');
          return {
            root: root.localName,
            patternId: root.dataset.patternId,
            title: root.querySelector(':scope > title')?.textContent || '',
            description: root.querySelector(':scope > desc')?.textContent || '',
            motionDisplay: motion ? getComputedStyle(motion).display : null,
            reducedDisplay: reduced ? getComputedStyle(reduced).display : null,
            motionCircleCount: motion?.querySelectorAll('circle').length || 0,
            reducedCircleCount: reduced?.querySelectorAll('circle').length || 0,
            runningAnimations: document.getAnimations().filter((item) => item.playState === 'running').length,
            scrollWidth: document.documentElement.scrollWidth,
            viewportWidth: innerWidth,
          };
        }"""
    )
    context.close()
    early = image_stats(early_png)
    final = image_stats(final_png)
    return {
        "viewport": viewport,
        "dom": dom,
        "earlyFrame": early,
        "finalFrame": final,
        "frameChanged": early["sha256"] != final["sha256"],
    }


def sample_reduced(browser: Browser, uri: str, errors: list[str]) -> dict[str, Any]:
    context = browser.new_context(
        viewport={"width": 1100, "height": 720},
        reduced_motion="reduce",
    )
    page = context.new_page()
    attach_error_capture(page, errors)
    page.goto(uri, wait_until="load")
    page.wait_for_timeout(200)
    png = page.screenshot()
    dom = page.evaluate(
        """() => {
          const motion = document.querySelector('[data-motion-layer="animated"]');
          const reduced = document.querySelector('[data-motion-layer="reduced"]');
          return {
            motionDisplay: motion ? getComputedStyle(motion).display : null,
            reducedDisplay: reduced ? getComputedStyle(reduced).display : null,
            animationCount: document.getAnimations().length,
            reducedCircleCount: reduced?.querySelectorAll('circle').length || 0,
          };
        }"""
    )
    context.close()
    return {"dom": dom, "frame": image_stats(png)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("svg", type=Path)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--screenshot", type=Path, required=True)
    args = parser.parse_args()

    svg_path = args.svg.resolve()
    findings: list[str] = []
    browser_errors: list[str] = []
    evidence: dict[str, Any] = {}
    if not svg_path.is_file() or svg_path.stat().st_size == 0:
        findings.append(f"Missing or empty SVG: {svg_path}")
    else:
        text = svg_path.read_text(encoding="utf-8")
        try:
            root = ET.fromstring(text)
        except ET.ParseError as exc:
            findings.append(f"Invalid SVG XML: {exc}")
        else:
            metadata = {name: root.attrib.get(name) for name in EXPECTED_METADATA}
            for name, expected in EXPECTED_METADATA.items():
                if metadata[name] != expected:
                    findings.append(f"{name} is {metadata[name]!r}; expected {expected!r}.")
            evidence["static"] = {
                "bytes": svg_path.stat().st_size,
                "sha256": hashlib.sha256(svg_path.read_bytes()).hexdigest(),
                "metadata": metadata,
            }

    if not findings:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            desktop = sample_normal(
                browser,
                svg_path.as_uri(),
                {"width": 1100, "height": 720},
                browser_errors,
                args.screenshot,
            )
            mobile = sample_normal(
                browser,
                svg_path.as_uri(),
                {"width": 390, "height": 844},
                browser_errors,
            )
            reduced = sample_reduced(browser, svg_path.as_uri(), browser_errors)
            browser.close()
        evidence.update({"desktop": desktop, "mobile": mobile, "reducedMotion": reduced})

        for name, sample in (("desktop", desktop), ("mobile", mobile)):
            dom = sample["dom"]
            if dom["root"] != "svg" or dom["patternId"] != EXPECTED_METADATA["data-pattern-id"]:
                findings.append(f"{name} did not load the expected SVG root.")
            if not dom["title"] or not dom["description"]:
                findings.append(f"{name} lacks a rendered title or description.")
            if dom["motionDisplay"] == "none" or dom["reducedDisplay"] != "none":
                findings.append(f"{name} selected the wrong motion layer.")
            if dom["motionCircleCount"] < 200 or dom["reducedCircleCount"] != dom["motionCircleCount"]:
                findings.append(f"{name} has incomplete or mismatched phyllotaxis layers.")
            if dom["runningAnimations"] < 100 or not sample["frameChanged"]:
                findings.append(f"{name} did not demonstrate active procedural motion.")
            for frame_name in ("earlyFrame", "finalFrame"):
                frame = sample[frame_name]
                if frame["colorCount"] < 12 or frame["nonwhiteSampleCount"] < 250:
                    findings.append(f"{name} {frame_name} appears blank or visually incomplete.")

        reduced_dom = reduced["dom"]
        if reduced_dom["motionDisplay"] != "none" or reduced_dom["reducedDisplay"] == "none":
            findings.append("Reduced-motion mode did not select the static layer.")
        if reduced_dom["animationCount"] != 0:
            findings.append("Reduced-motion mode still has active CSS animations.")
        if reduced["frame"]["colorCount"] < 12 or reduced["frame"]["nonwhiteSampleCount"] < 250:
            findings.append("Reduced-motion frame appears blank or visually incomplete.")

    if browser_errors:
        findings.extend(browser_errors)
    report = {
        "schemaVersion": 1,
        "passed": not findings,
        "artifact": str(svg_path),
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
