#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright>=1.52.0"]
# ///
"""Inspect the final D3 direct-recipe cohort and retain browser evidence."""

from __future__ import annotations

import json
import argparse
import xml.etree.ElementTree as ET
from pathlib import Path

from playwright.sync_api import Error, sync_playwright


ROOT = Path(__file__).resolve().parents[3]
ARTIFACTS = ROOT / "projects/skill-authoring-audit/artifacts"


def settle(page) -> None:
    # The explanation is finite. Advance declarative SVG animation and finish
    # finite CSS animation rather than capturing a transient reveal frame.
    page.evaluate("""() => {
      document.querySelectorAll('svg').forEach(svg => {
        // beginElement() restarts at the current SVG clock. Advance from that
        // clock after replay rather than seeking back to its restart instant.
        if(svg.setCurrentTime) svg.setCurrentTime((svg.getCurrentTime?.() || 0)+20);
        if(svg.pauseAnimations) svg.pauseAnimations();
      });
      document.getAnimations().forEach(a => {if(Number.isFinite(a.effect.getComputedTiming().endTime)) a.finish()});
    }""")
    page.wait_for_function("""() => Array.from(document.querySelectorAll('svg text')).every(n => {
      let opacity=1; for(let p=n;p&&p instanceof Element;p=p.parentElement) opacity*=Number(getComputedStyle(p).opacity);
      return !n.textContent.trim() || opacity>.99;
    })""", timeout=10000)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prefix", default="20261002-authoring-d3-recipe-luna")
    parser.add_argument("--report", default="d3-recipe-independent.json")
    args = parser.parse_args()
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
            raise RuntimeError("No installed Chromium browser is available")
        for repetition in (1, 2, 3):
            run_id = f"{args.prefix}-{repetition}"
            run = ROOT / "evaluations/runs" / run_id
            svg_path = run / "workspace/out/decode.svg"
            html = run / "workspace/out/decode.html"
            svg = ET.parse(svg_path).getroot()
            namespace = {"s": "http://www.w3.org/2000/svg"}
            texts = [(node.text or "").strip() for node in svg.findall(".//s:text", namespace)]
            checks = {
                "strictHarness": json.loads((run / "evaluation-result.json").read_text(encoding="utf-8"))["passed"],
                "dimensions": svg.attrib.get("viewBox") == "0 0 720 440",
                "accessible": svg.find("s:title", namespace) is not None and svg.find("s:desc", namespace) is not None,
                "exactTokens": all(token in texts for token in ("the", "answer", "is", "42", "next")),
                "colorset": svg.attrib.get("data-colorset") == "colorset2",
                "portableSvg": not svg.findall(".//s:script", namespace) and not svg.findall(".//s:foreignObject", namespace) and not svg.findall(".//s:image", namespace),
            }
            page = browser.new_page(viewport={"width": 900, "height": 640})
            errors, requests, screenshots = [], [], []
            page.on("pageerror", lambda error: errors.append(str(error)))
            page.on("request", lambda request: requests.append(request.url) if request.url.startswith(("http://", "https://")) else None)
            page.route("http://**/*", lambda route: route.abort())
            page.route("https://**/*", lambda route: route.abort())
            try:
                page.goto(html.as_uri(), wait_until="load")
                settle(page)
                button = page.get_by_role("button", name="Replay", exact=False).first
                checks["replayPresent"] = button.count() == 1
                for _ in range(2):
                    button.click()
                    settle(page)
                checks["replayTwice"] = True
                for label, path in (("html", html), ("svg", svg_path)):
                    if label == "svg":
                        page.goto(path.as_uri(), wait_until="load")
                        settle(page)
                    bounds = page.evaluate("""() => {
                      const s=document.querySelector('svg'), frame=s.getBoundingClientRect();
                      return Array.from(s.querySelectorAll('text')).filter(n=>n.textContent.trim()).map(n=>{
                        const r=n.getBoundingClientRect();
                        return {text:n.textContent, visible:r.width>0&&r.height>0, inside:r.left>=frame.left-1&&r.right<=frame.right+1&&r.top>=frame.top-1&&r.bottom<=frame.bottom+1};
                      });
                    }""")
                    checks[f"{label}TextBounds"] = all(row["visible"] and row["inside"] for row in bounds)
                    screenshot = ARTIFACTS / "screenshots" / f"{run_id}-{label}.png"
                    screenshot.parent.mkdir(parents=True, exist_ok=True)
                    page.screenshot(path=str(screenshot), full_page=False, timeout=10000)
                    screenshots.append(screenshot.relative_to(ROOT).as_posix())
            except Error as error:
                errors.append(str(error))
                checks["browserInspection"] = False
            checks["offline"] = not requests
            checks["noBrowserErrors"] = not errors
            page.close()
            results.append({"run": run_id, "passed": all(checks.values()), "checks": checks, "tokens": texts, "screenshots": screenshots, "browserErrors": errors, "remoteRequests": requests, "manualSemanticReviewRequired": True})
        browser.close()
    report = {"passed": all(result["passed"] for result in results), "results": results}
    output = ARTIFACTS / "reviews" / args.report
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"passed": report["passed"], "results": [{"run": row["run"], "checks": row["checks"], "browserErrors": row["browserErrors"]} for row in results]}, indent=2))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
