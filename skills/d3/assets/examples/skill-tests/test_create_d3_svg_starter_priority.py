#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright>=1.52.0"]
# ///
"""Inspect default editable starter category paints and source-data preservation."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys
import unittest

from playwright.sync_api import sync_playwright

SKILL_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(SKILL_ROOT / "scripts"))
import create_d3_svg_starter as starter

ARTIFACTS: Path
SOLIDS = ["#9e1b32", "#333e48", "#4f4f4f", "#696969", "#828282", "#9c9c9c"]
SELECTORS = {
    "animated-network": "circle",
    "blank": "circle",
    "context-window-matrix": "rect",
    "inline-bar-table": "rect",
    "operational-dashboard": "g.row > rect:nth-of-type(3)",
}
INSPECT = r'''selector => {
const svg=document.querySelector('svg');svg.pauseAnimations?.();svg.setCurrentTime?.(10);
window.D3SolidStyle.normalize(svg);
const hex=v=>{const m=v.match(/^rgb\((\d+),\s*(\d+),\s*(\d+)\)$/);return m?'#'+m.slice(1).map(n=>(+n).toString(16).padStart(2,'0')).join(''):v;};
return {nodes:[...svg.querySelectorAll(selector)].filter(node=>node.__data__).map(node=>({
data:node.__data__,fill:hex(getComputedStyle(node).fill),stroke:getComputedStyle(node).stroke,
opacity:+getComputedStyle(node).opacity,fillOpacity:+getComputedStyle(node).fillOpacity,
tier:node.dataset.outlineTier ?? null,width:parseFloat(getComputedStyle(node).strokeWidth),
text:node.parentElement.querySelector('text')?.textContent,
textFill:node.parentElement.querySelector('text')?hex(getComputedStyle(node.parentElement.querySelector('text')).fill):null
})),unresolved:[...svg.querySelectorAll('[data-arrow-unresolved]')].map(node=>node.dataset.arrowUnresolved),
labels:[...svg.querySelectorAll('text')].map(node=>node.textContent)};
}'''


def strip_paints(value):
    if isinstance(value, dict):
        return {key: strip_paints(child) for key, child in value.items() if key != "color"}
    if isinstance(value, list):
        return [strip_paints(child) for child in value]
    return value


class StarterPriorityTests(unittest.TestCase):
    def test_all_default_modes_keep_data_and_render_correct_category_paints(self):
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(**({} if Path(playwright.chromium.executable_path).exists() else {"channel": "msedge"}))
            page = browser.new_page(viewport={"width": 1440, "height": 1100}, reduced_motion="reduce")
            for colorset in ("colorset1", "colorset2"):
                for pattern in starter.STARTER_DATA:
                    with self.subTest(colorset=colorset, pattern=pattern):
                        directory = ARTIFACTS / colorset / pattern
                        starter.write_starter(directory, pattern, "Editable priority inspection", True, False, colorset)
                        data = json.loads((directory / "data.js").read_text(encoding="utf-8").split(" = ", 1)[1].rstrip(";\n"))
                        self.assertEqual(strip_paints(data), strip_paints(starter.STARTER_DATA[pattern]))
                        if colorset == "colorset2":
                            self.assertEqual(starter.pattern_code_for(pattern, colorset), starter.PATTERN_CODE[pattern].strip())
                        errors = []
                        page.on("pageerror", lambda error: errors.append(str(error)))
                        page.goto((directory / "index.html").as_uri())
                        page.wait_for_timeout(900)
                        result = page.evaluate(INSPECT, SELECTORS[pattern])
                        self.assertEqual(errors, [])
                        self.assertEqual(result["unresolved"], [])
                        nodes = result["nodes"]
                        self.assertTrue(nodes)
                        self.assertTrue(all(node["stroke"] == "none" and node["opacity"] == 1 and node["fillOpacity"] == 1 for node in nodes))
                        if pattern == "animated-network":
                            expected = [SOLIDS[0], SOLIDS[1], SOLIDS[1], SOLIDS[2], SOLIDS[3]] if colorset == "colorset1" else ["#007298", "#652f6c", "#652f6c", "#e77204", "#45842a"]
                            self.assertEqual([node["fill"] for node in nodes], expected)
                            self.assertEqual([node["text"] for node in nodes], [node["id"] for node in data["nodes"]])
                            self.assertTrue(all(node["textFill"] in {"#000000", "#ffffff"} for node in nodes))
                        elif pattern == "blank":
                            self.assertEqual({node["fill"] for node in nodes}, {SOLIDS[0] if colorset == "colorset1" else "#e77204"})
                        elif pattern == "context-window-matrix":
                            used = [node for node in nodes if not node["data"].get("unused") and node["fill"] == node["data"].get("color")]
                            self.assertEqual(len(used), sum(segment["units"] for segment in data["segments"] if not segment.get("unused")) + 6)
                            distinct = list(dict.fromkeys(node["fill"] for node in used))
                            self.assertEqual(distinct, SOLIDS if colorset == "colorset1" else ["#007298", "#45842a", "#e77204", "#652f6c", "#00ace6", "#f1c319"])
                        elif pattern == "inline-bar-table":
                            body = [node for node in nodes if node["fill"] != "#e7e7e7"]
                            mapping = {"on track": SOLIDS[2], "watch": SOLIDS[1], "behind": SOLIDS[0]} if colorset == "colorset1" else {"on track": "#45842a", "watch": "#e77204", "behind": "#9e1b32"}
                            self.assertEqual([node["fill"] for node in body], [mapping[row["status"]] for row in data["rows"]])
                        else:
                            mapping = {"critical": SOLIDS[0], "watch": SOLIDS[1], "stable": SOLIDS[2], "healthy": SOLIDS[3]} if colorset == "colorset1" else {"critical": "#9e1b32", "watch": "#e77204", "stable": "#007298", "healthy": "#45842a"}
                            self.assertEqual([node["fill"] for node in nodes], [mapping[row["status"]] for row in data["services"]])
                        (directory / "inspection.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
                        page.locator("svg").screenshot(path=str(directory / "desktop.png"))
                        page.set_viewport_size({"width": 390, "height": 844})
                        page.locator("svg").screenshot(path=str(directory / "mobile.png"))
                        page.set_viewport_size({"width": 1440, "height": 1100})
            browser.close()


def main():
    global ARTIFACTS
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifacts", type=Path, required=True)
    args = parser.parse_args()
    ARTIFACTS = args.artifacts.resolve()
    if ARTIFACTS.is_relative_to(SKILL_ROOT):
        parser.error("Artifacts must be outside the skill resource")
    ARTIFACTS.mkdir(parents=True, exist_ok=True)
    result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(StarterPriorityTests))
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())
