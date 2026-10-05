#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright>=1.51"]
# ///
"""Capture a task SVG in Chromium for delivery-size visual inspection."""
from pathlib import Path
import argparse
import json
import math
import xml.etree.ElementTree as ET
from playwright.sync_api import sync_playwright


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--width", type=int, help="Review width; defaults to the source viewBox width.")
    args = parser.parse_args()
    source = args.source.read_text(encoding="utf-8")
    root = ET.fromstring(source)
    view = [float(v) for v in root.get("viewBox", "").replace(",", " ").split()]
    width = args.width or (view[2] if len(view) == 4 else float(root.get("width", "900").removesuffix("px")))
    height = math.ceil(width * view[3] / view[2]) if len(view) == 4 else 520
    if not 1 <= width <= 16384 or not 1 <= height <= 16384:
        parser.error("Review dimensions must be positive and at most 16384 pixels.")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": math.ceil(width), "height": height})
        errors = []
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.set_content("<!doctype html><style>body{margin:0;background:white}</style>" + source)
        svg = page.locator("svg").first
        svg.evaluate("(svg, width) => {svg.style.width=width+'px';svg.style.height='auto'}", width)
        page.evaluate("document.fonts.ready")
        svg.screenshot(path=str(args.output.resolve()), animations="disabled")
        labels = page.locator("svg text").all_text_contents()
        browser.close()
    print(json.dumps({"ok": not errors, "output": str(args.output), "width": width,
                      "height": height, "labelCount": len(labels), "pageErrors": errors}))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
