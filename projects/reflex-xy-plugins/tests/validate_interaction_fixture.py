#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright==1.64.1"]
# ///
"""Independently verify the focused skill-only progressive-controls artifact."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import xml.etree.ElementTree as ET

from playwright.sync_api import sync_playwright


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--html", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    results = []
    with sync_playwright() as runtime:
        browser = runtime.chromium.launch(headless=True, channel="msedge")
        for width in (1100, 390):
            context = browser.new_context(viewport={"width": width, "height": 900}, accept_downloads=True)
            page = context.new_page()
            errors = []
            page.on("pageerror", lambda error: errors.append(str(error)))
            page.goto(args.html.resolve().as_uri())
            svg = page.locator("figure svg")
            assert svg.get_attribute("viewBox") == "0 0 400 220"
            assert svg.locator("path").get_attribute("d") == "M40 180 L190 110 L350 40"
            assert svg.locator("path").get_attribute("stroke") == "#9e1b32"
            assert page.locator("button:visible").count() == 1
            summary = page.get_by_text("More options", exact=True)
            assert page.locator("input:visible").count() == 0
            for control in (summary, page.get_by_role("button", name="Save SVG", exact=True)):
                box = control.bounding_box()
                assert box and box["width"] >= 44 and box["height"] >= 44
            page.screenshot(path=str(args.output_dir / f"initial-{width}.png"), full_page=True)
            summary.focus()
            summary.press("Enter")
            assert page.locator("details").get_attribute("open") is not None
            assert page.locator("input:visible").count() == 2
            for label in page.locator("label.choice").all():
                box = label.bounding_box()
                assert box and box["width"] >= 44 and box["height"] >= 44
            page.locator('input[value="colorset2"]').check()
            assert svg.locator("path").get_attribute("stroke") == "#007298"
            assert svg.locator("path").get_attribute("d") == "M40 180 L190 110 L350 40"
            summary.focus()
            summary.press("Space")
            assert page.locator("details").get_attribute("open") is None
            assert page.locator("input:visible").count() == 0
            summary.press("Enter")
            assert page.locator('input[value="colorset2"]').is_checked()
            with page.expect_download() as pending:
                page.get_by_role("button", name="Save SVG", exact=True).click()
            path = args.output_dir / f"download-{width}.svg"
            pending.value.save_as(path)
            exported = ET.parse(path).getroot()
            line = exported.find("{http://www.w3.org/2000/svg}path")
            assert line is not None and line.attrib["d"] == "M40 180 L190 110 L350 40"
            assert line.attrib["stroke"] == "#007298"
            overflow = page.evaluate("({width:innerWidth,scroll:document.documentElement.scrollWidth})")
            assert overflow["scroll"] <= overflow["width"]
            assert not errors, errors
            page.screenshot(path=str(args.output_dir / f"expanded-{width}.png"), full_page=True)
            results.append({"width": width, "passed": True, "initial_actions": 2,
                "keyboard": ["Enter", "Space"], "geometry_preserved": True,
                "download_matches_selection": True, "overflow": overflow, "errors": errors})
            context.close()
        browser.close()
    report = {"passed": True, "cases": results, "scope": "isolated static interaction fixture; no live MCP claim"}
    (args.output_dir / "report.json").write_text(json.dumps(report, indent=2)+"\n", encoding="utf-8")
    print(json.dumps(report))


if __name__ == "__main__":
    main()
