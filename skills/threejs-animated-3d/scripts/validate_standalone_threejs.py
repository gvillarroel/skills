#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "playwright>=1.52.0",
# ]
# ///

"""Validate one standalone Three.js HTML artifact without ad hoc probes."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any

from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import Page, sync_playwright


REMOTE_REFERENCE_RE = re.compile(
    r"(?:src|href)\s*=\s*[\"']\s*(?:https?:)?//",
    re.IGNORECASE,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("html", type=Path, help="Standalone Three.js HTML file.")
    parser.add_argument("--report", type=Path, help="Optional JSON report path.")
    parser.add_argument("--screenshot", type=Path, help="Optional desktop screenshot path.")
    parser.add_argument("--browser-channel", help="Optional Chromium channel such as msedge.")
    return parser.parse_args()


def add(findings: list[str], condition: bool, message: str) -> None:
    if not condition:
        findings.append(message)


def canvas_probe(page: Page) -> dict[str, Any]:
    return page.evaluate(
        """() => {
          const canvas = document.querySelector('#scene-canvas');
          if (!(canvas instanceof HTMLCanvasElement)) return { exists: false };
          const sample = document.createElement('canvas');
          sample.width = 64;
          sample.height = 36;
          const context = sample.getContext('2d', { willReadFrequently: true });
          context.drawImage(canvas, 0, 0, sample.width, sample.height);
          const pixels = context.getImageData(0, 0, sample.width, sample.height).data;
          const colors = new Set();
          let nonwhite = 0;
          for (let index = 0; index < pixels.length; index += 4) {
            const red = pixels[index];
            const green = pixels[index + 1];
            const blue = pixels[index + 2];
            const alpha = pixels[index + 3];
            if (alpha <= 8) continue;
            colors.add(`${red >> 3}:${green >> 3}:${blue >> 3}`);
            if (red < 245 || green < 245 || blue < 245) nonwhite += 1;
          }
          return {
            exists: true,
            cssWidth: canvas.getBoundingClientRect().width,
            cssHeight: canvas.getBoundingClientRect().height,
            pixelWidth: canvas.width,
            pixelHeight: canvas.height,
            colorBucketCount: colors.size,
            nonwhiteSampleCount: nonwhite,
            dataUrl: canvas.toDataURL('image/png'),
            canvasCount: document.querySelectorAll('canvas').length,
            replayCount: document.querySelectorAll('#replay').length,
            ready: window.__threeRuntimeSceneReady === true,
            runtimeApi: Boolean(window.__threeRuntimeScene),
            overflowX: document.documentElement.scrollWidth - innerWidth,
          };
        }"""
    )


def data_url_hash(probe: dict[str, Any]) -> str | None:
    value = probe.get("dataUrl")
    return hashlib.sha256(value.encode("ascii")).hexdigest() if isinstance(value, str) else None


def inspect_viewport(
    browser: Any,
    source: Path,
    *,
    width: int,
    height: int,
    controls: bool,
    screenshot: Path | None,
) -> tuple[dict[str, Any], list[str]]:
    context = browser.new_context(viewport={"width": width, "height": height})
    page = context.new_page()
    errors: list[str] = []
    page.on(
        "console",
        lambda message: errors.append(f"console: {message.text}")
        if message.type == "error"
        else None,
    )
    page.on("pageerror", lambda error: errors.append(f"page: {error}"))
    page.on(
        "requestfailed",
        lambda request: errors.append(
            f"request: {request.method} {request.url}: {request.failure}"
        ),
    )
    page.goto(source.as_uri(), wait_until="load")
    page.wait_for_function("window.__threeRuntimeSceneReady === true", timeout=30_000)
    # The ready flag marks scene construction. Allow the first WebGL frame to
    # reach the preserved drawing buffer before treating a blank sample as a
    # render failure, especially under software rendering on Windows CI.
    page.wait_for_timeout(1_200)
    first = canvas_probe(page)
    first_hash = data_url_hash(first)
    page.wait_for_timeout(700)
    second = canvas_probe(page)
    second_hash = data_url_hash(second)

    control_evidence: dict[str, Any] = {}
    if controls:
        page.locator("#replay").click()
        control_evidence["replayStatus"] = page.locator("#status").inner_text()
        box = page.locator("#scene-canvas").bounding_box()
        if box is not None:
            center_x = box["x"] + box["width"] / 2
            center_y = box["y"] + box["height"] / 2
            page.mouse.move(center_x, center_y)
            page.mouse.down()
            page.mouse.move(center_x + 60, center_y + 25, steps=4)
            control_evidence["dragStatus"] = page.locator("#status").inner_text()
            page.mouse.up()
            control_evidence["releaseStatus"] = page.locator("#status").inner_text()
        control_evidence["finalCanvasCount"] = page.locator("canvas").count()
        control_evidence["finalReplayCount"] = page.locator("#replay").count()

    if screenshot is not None:
        screenshot.parent.mkdir(parents=True, exist_ok=True)
        page.screenshot(path=str(screenshot), full_page=True)
    context.close()
    first.pop("dataUrl", None)
    second.pop("dataUrl", None)
    return (
        {
            "viewport": {"width": width, "height": height},
            "first": first,
            "second": second,
            "firstFrameSha256": first_hash,
            "secondFrameSha256": second_hash,
            "frameChanged": bool(first_hash and second_hash and first_hash != second_hash),
            "controls": control_evidence,
        },
        errors,
    )


def main() -> int:
    args = parse_args()
    source = args.html.resolve()
    findings: list[str] = []
    browser_errors: list[str] = []
    evidence: dict[str, Any] = {}
    add(findings, source.is_file(), f"HTML file does not exist: {source}")

    if source.is_file():
        text = source.read_text(encoding="utf-8")
        evidence["static"] = {
            "bytes": source.stat().st_size,
            "sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
            "remoteReferenceCount": len(REMOTE_REFERENCE_RE.findall(text)),
        }
        for token, message in (
            ("<canvas", "missing canvas element"),
            ('id="replay"', "missing replay control"),
            ("THREE.PerspectiveCamera", "missing perspective camera"),
            ("THREE.AmbientLight", "missing ambient light"),
            ("THREE.DirectionalLight", "missing directional light"),
            ("requestAnimationFrame", "missing animation loop"),
            ("preserveDrawingBuffer: true", "canvas is not probeable"),
        ):
            add(findings, token in text, message)
        add(findings, not REMOTE_REFERENCE_RE.search(text), "external network reference found")

        try:
            with sync_playwright() as playwright:
                launch_options: dict[str, Any] = {"headless": True}
                if args.browser_channel:
                    launch_options["channel"] = args.browser_channel
                browser = playwright.chromium.launch(**launch_options)
                desktop, desktop_errors = inspect_viewport(
                    browser,
                    source,
                    width=1280,
                    height=720,
                    controls=True,
                    screenshot=args.screenshot.resolve() if args.screenshot else None,
                )
                mobile, mobile_errors = inspect_viewport(
                    browser,
                    source,
                    width=390,
                    height=844,
                    controls=False,
                    screenshot=None,
                )
                browser.close()
                evidence["desktop"] = desktop
                evidence["mobile"] = mobile
                browser_errors.extend(desktop_errors + mobile_errors)
        except PlaywrightError as error:
            findings.append(f"browser validation failed: {error}")

    for name in ("desktop", "mobile"):
        viewport = evidence.get(name)
        if not isinstance(viewport, dict):
            continue
        first = viewport["first"]
        add(findings, bool(first.get("ready")), f"{name} ready flag is false")
        add(findings, bool(first.get("runtimeApi")), f"{name} runtime API is missing")
        add(findings, first.get("canvasCount") == 1, f"{name} canvas count is not one")
        add(findings, first.get("replayCount") == 1, f"{name} replay count is not one")
        add(findings, first.get("colorBucketCount", 0) >= 12, f"{name} color diversity is too low")
        add(findings, first.get("nonwhiteSampleCount", 0) >= 40, f"{name} canvas appears blank")
        add(findings, first.get("cssWidth", 0) >= 280, f"{name} canvas is too narrow")
        add(findings, first.get("cssHeight", 0) >= 180, f"{name} canvas is too short")
        add(findings, first.get("overflowX", 0) <= 1, f"{name} page overflows horizontally")
        add(findings, bool(viewport.get("frameChanged")), f"{name} animation frame did not change")

    controls = evidence.get("desktop", {}).get("controls", {})
    add(findings, controls.get("replayStatus") == "Replay started.", "replay did not reset")
    add(findings, controls.get("dragStatus") == "Dragging camera.", "pointer drag did not engage")
    add(
        findings,
        controls.get("releaseStatus") == "Drag to orbit. Replay resets the scene.",
        "pointer release status is incorrect",
    )
    add(findings, controls.get("finalCanvasCount") == 1, "interaction duplicated the canvas")
    add(findings, controls.get("finalReplayCount") == 1, "interaction duplicated replay")
    findings.extend(browser_errors)

    report = {
        "schemaVersion": 1,
        "passed": not findings,
        "artifact": str(source),
        "findings": findings,
        "browserErrors": browser_errors,
        "evidence": evidence,
    }
    if args.report:
        report_path = args.report.resolve()
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
