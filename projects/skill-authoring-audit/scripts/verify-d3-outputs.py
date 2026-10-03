#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright>=1.52.0"]
# ///
"""Independently inspect the D3 audit cohort's data, geometry, and rendering."""

from __future__ import annotations

import json
import xml.etree.ElementTree as ET
from pathlib import Path

from playwright.sync_api import Error, sync_playwright


ROOT = Path(__file__).resolve().parents[3]
OUTPUT = ROOT / "projects/skill-authoring-audit/artifacts"
EXPECTED = [("Design", "8"), ("API", "15"), ("QA", "11")]


def main() -> int:
    results = []
    with sync_playwright() as playwright:
        browser = None
        for channel in (None, "msedge", "chrome"):
            try:
                browser = playwright.chromium.launch(headless=True, **({"channel": channel} if channel else {}))
                break
            except Error:
                continue
        if browser is None:
            raise RuntimeError("No available Chromium browser for independent inspection")
        for repetition in (1, 2, 3):
            run_id = f"20261002-authoring-d3-luna-{repetition}"
            run = ROOT / "evaluations/runs" / run_id
            artifact = run / "workspace/out/chart.svg"
            html = run / "workspace/out/chart.html"
            svg = ET.parse(artifact).getroot()
            namespace = {"s": "http://www.w3.org/2000/svg"}
            circles = svg.findall(".//s:circle", namespace)
            data_marks = [circle for circle in circles if "data-value" in circle.attrib]
            checks = {
                "strictHarness": json.loads((run / "evaluation-result.json").read_text(encoding="utf-8"))["passed"],
                "dimensions": svg.attrib.get("viewBox") == "0 0 720 440",
                "accessible": svg.find("s:title", namespace) is not None and svg.find("s:desc", namespace) is not None,
                "exactValues": [circle.attrib["data-value"] for circle in data_marks] == [value for _, value in EXPECTED],
                "orderedLabels": all(label in circle.attrib.get("aria-label", "") for circle, (label, _) in zip(data_marks, EXPECTED)) and len(data_marks) == 3,
                "portableSvg": not svg.findall(".//s:script", namespace) and not svg.findall(".//s:foreignObject", namespace),
                "linearGeometry": len(data_marks) == 3 and all(abs(float(mark.attrib["cx"]) - (132 + float(value) * 32)) < 0.1 for mark, (_, value) in zip(data_marks, EXPECTED)),
            }
            page = browser.new_page(viewport={"width": 900, "height": 640}, device_scale_factor=1)
            errors = []
            network = []
            page.on("pageerror", lambda error: errors.append(str(error)))
            page.on("request", lambda request: network.append(request.url) if request.url.startswith(("http://", "https://")) else None)
            page.goto(html.as_uri(), wait_until="load")
            page.wait_for_function("document.querySelectorAll('svg circle[data-value]').length === 3")
            page.wait_for_function("""expected => {
              const marks = Array.from(document.querySelectorAll('svg circle[data-value]'));
              return marks.length === expected.length && marks.every((mark, index) => Math.abs(Number(mark.getAttribute('cx')) - expected[index]) < 0.1);
            }""", arg=[float(mark.attrib["cx"]) for mark in data_marks], timeout=10000)
            bounds = page.evaluate("""() => {
              const svg = document.querySelector('svg');
              const frame = svg.getBoundingClientRect();
              return Array.from(svg.querySelectorAll('text')).filter(n => n.textContent.trim()).map(n => {
                const r = n.getBoundingClientRect();
                return {text:n.textContent, visible:r.width>0 && r.height>0,
                  inside:r.left>=frame.left-1 && r.right<=frame.right+1 && r.top>=frame.top-1 && r.bottom<=frame.bottom+1};
              });
            }""")
            checks.update({"noBrowserErrors": not errors, "offline": not network, "readableTextBounds": all(row["visible"] and row["inside"] for row in bounds)})
            screenshot = OUTPUT / "screenshots" / f"{run_id}.png"
            screenshot.parent.mkdir(parents=True, exist_ok=True)
            page.screenshot(path=str(screenshot), full_page=True)
            page.close()
            results.append({"run": run_id, "passed": all(checks.values()), "checks": checks, "textBounds": bounds, "browserErrors": errors, "networkRequests": network, "screenshot": screenshot.relative_to(ROOT).as_posix()})
        browser.close()
    report = {"passed": all(result["passed"] for result in results), "results": results}
    path = OUTPUT / "reviews/d3-independent.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"passed": report["passed"], "runs": len(results), "checks": [row["checks"] for row in results]}, indent=2))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
