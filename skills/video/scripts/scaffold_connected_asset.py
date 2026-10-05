#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright"]
# ///
"""Create a content-sized label asset with explicit connector ports."""
import argparse
import json
import math
from pathlib import Path
from xml.sax.saxutils import escape

from playwright.sync_api import sync_playwright


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--label", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    if not args.label.strip() or len(args.label) > 200 or any(ord(c) < 32 for c in args.label):
        parser.error("Use one nonempty label of at most 200 characters without control characters.")
    if args.output.resolve() == args.report.resolve():
        parser.error("SVG output and JSON report must use different paths.")
    with sync_playwright() as browser_api:
        browser = browser_api.chromium.launch(headless=True)
        page = browser.new_page()
        metrics = page.evaluate("""label => {
          const ctx = document.createElement('canvas').getContext('2d');
          ctx.font = '18px "Open Sans", Arial, sans-serif';
          const m = ctx.measureText(label);
          return {width: Math.max(m.width, m.actualBoundingBoxLeft + m.actualBoundingBoxRight),
                  ascent: m.actualBoundingBoxAscent, descent: m.actualBoundingBoxDescent};
        }""", args.label)
        browser.close()
    width = max(36, math.ceil(metrics["width"]) + 16)
    height = max(36, math.ceil(metrics["ascent"] + metrics["descent"]) + 16)
    baseline = (height + metrics["ascent"] - metrics["descent"]) / 2
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title">
  <title id="title">{escape(args.label)}</title>
  <rect id="node" x="1" y="1" width="{width - 2}" height="{height - 2}" fill="#ffffff"/>
  <text id="label" x="{width / 2:g}" y="{baseline:g}" text-anchor="middle" font-family="Open Sans, Arial, sans-serif" font-size="18" fill="#000000">{escape(args.label)}</text>
  <circle id="in" cx="2" cy="{height / 2:g}" r="1.5" fill="#333e48"/>
  <circle id="out" cx="{width - 2}" cy="{height / 2:g}" r="1.5" fill="#333e48"/>
</svg>
'''
    with sync_playwright() as browser_api:
        browser = browser_api.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": width, "height": height})
        page.set_content('<style>html,body{margin:0}</style>' + svg)
        painted = page.evaluate("""() => {
          const b=document.querySelector('#label').getBBox();
          return {x:b.x,y:b.y,width:b.width,height:b.height,
                  label:document.querySelector('#label').textContent,
                  fontPx:parseFloat(getComputedStyle(document.querySelector('#label')).fontSize)};
        }""")
        browser.close()
    if (painted["label"] != args.label or painted["fontPx"] != 18 or
            min(painted["x"], painted["y"], width-painted["x"]-painted["width"],
                height-painted["y"]-painted["height"]) < 5):
        parser.error("Native label painting cannot retain the protected text clearance.")
    report = {"schemaVersion": 1, "ok": True, "label": args.label, "width": width, "height": height,
              "fontSizePx": 18, "measuredText": metrics, "ports": [
                  {"id": "in", "selector": "#in", "anchor": "center"},
                  {"id": "out", "selector": "#out", "anchor": "center"}],
              "paintedText": painted,
              "scope": "Native single-label painting and text clearance only; inspect final compositor placement and routes."}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(svg, encoding="utf-8")
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(args.output), "report": str(args.report),
                      "width": width, "height": height, "fontSizePx": 18}))


if __name__ == "__main__":
    main()
