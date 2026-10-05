#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright"]
# ///
"""Check measured fallback assets at native size and exact named outputs."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from playwright.sync_api import sync_playwright


class AssetTest(unittest.TestCase):
    def test_complete_glyphs_and_ports(self):
        with tempfile.TemporaryDirectory(prefix="compact-asset-", dir=Path.cwd()) as folder:
            with sync_playwright() as api:
                browser = api.chromium.launch(headless=True)
                page = browser.new_page()
                for index, label in enumerate(["Input", "Controller", "Review < & >", "MMMM WWWW"]):
                    svg = Path(folder) / f"{index}.svg"
                    report = Path(folder) / f"{index}.json"
                    result = subprocess.run([sys.executable, str(Path(__file__).with_name("scaffold_connected_asset.py")),
                                             "--label", label, "--output", str(svg), "--report", str(report)],
                                            capture_output=True, text=True)
                    self.assertEqual(result.returncode, 0, result.stderr)
                    meta = json.loads(report.read_text(encoding="utf-8"))
                    page.set_content(svg.read_text(encoding="utf-8"))
                    geometry = page.evaluate("""() => {
                      const svg = document.querySelector('svg');
                      const text = document.querySelector('#label');
                      const b = text.getBBox();
                      return {label: text.textContent, font: getComputedStyle(text).fontSize,
                        x: b.x, y: b.y, right: b.x+b.width, bottom: b.y+b.height,
                        width: svg.viewBox.baseVal.width, height: svg.viewBox.baseVal.height,
                        ports: [...document.querySelectorAll('circle')].map(p => {
                          const b=p.getBBox(); return [b.x,b.y,b.x+b.width,b.y+b.height];
                        })};
                    }""")
                    self.assertEqual(geometry["label"], label)
                    self.assertEqual(geometry["font"], "18px")
                    self.assertGreaterEqual(geometry["x"], 5)
                    self.assertGreaterEqual(geometry["y"], 5)
                    self.assertLessEqual(geometry["right"], meta["width"] - 5)
                    self.assertLessEqual(geometry["bottom"], meta["height"] - 5)
                    self.assertLessEqual(meta["height"], 36)
                    for left, top, right, bottom in geometry["ports"]:
                        self.assertGreaterEqual(min(left, top), 0)
                        self.assertLessEqual(right, meta["width"])
                        self.assertLessEqual(bottom, meta["height"])
                browser.close()

    def test_rejects_invalid_contract_before_writing(self):
        with tempfile.TemporaryDirectory(prefix="compact-asset-", dir=Path.cwd()) as folder:
            output = Path(folder) / "same.svg"
            command = [sys.executable, str(Path(__file__).with_name("scaffold_connected_asset.py")),
                       "--label", "Input", "--output", str(output), "--report", str(output)]
            result = subprocess.run(command, capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main()
