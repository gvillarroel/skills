#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright>=1.52.0"]
# ///
"""Verify valid-token preservation and rendered CS1 solid capacity before borders."""

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
import colorset_adapter
from test_build_contract_artifact import common
import build_contract_artifact

SOLIDS = ["#9e1b32", "#333e48", "#4f4f4f", "#696969", "#828282", "#9c9c9c",
          "#b5b5b5", "#cfcfcf", "#e7e7e7", "#363636", "#f7f7f7", "#1c1c1c",
          "#000000", "#6d1222", "#e8002a", "#ffccd5"]
ARTIFACTS: Path

INSPECT = r'''selector => {
const svg=document.querySelector('svg');svg.pauseAnimations?.();svg.setCurrentTime?.(10);
window.D3SolidStyle?.normalize(svg);
const hex=v=>{const m=v.match(/^rgb\((\d+),\s*(\d+),\s*(\d+)\)$/);return m?'#'+m.slice(1).map(n=>(+n).toString(16).padStart(2,'0')).join(''):v;};
return [...svg.querySelectorAll(selector)].map(node=>({
fill:hex(getComputedStyle(node).fill),stroke:getComputedStyle(node).stroke,
width:parseFloat(getComputedStyle(node).strokeWidth),
tier:node.closest('[data-outline-tier]')?.dataset.outlineTier,
label:node.parentElement.querySelector('text')?.textContent,
text:node.parentElement.querySelector('text')?hex(getComputedStyle(node.parentElement.querySelector('text')).fill):null
}));
}'''


class ColorsetPriorityTests(unittest.TestCase):
    def test_allowed_tokens_are_preserved_before_foreign_hue_fallback(self):
        palette = json.loads(colorset_adapter.CONTRACT.read_text(encoding="utf-8"))["colorsets"]["colorset1"]
        tokens = palette["allowed"] + ["#007298", "#e77204", "#cdf3ff"]
        source = '<html><body><svg>' + ''.join(f'<rect fill="{paint}"/>' for paint in tokens) + '</svg></body></html>'
        result = colorset_adapter.adapt_artifact(source, "colorset1")
        self.assertEqual(re.findall(r'<rect fill="(#[a-f0-9]{6})"', result),
                         palette["allowed"] + ["#333e48", "#9e1b32", "#e7e7e7"])
        self.assertIn('<rect fill="#ffccd5"/>', result)

    def test_flow_and_wedge_render_all_sixteen_solids_before_overflow(self):
        palettes = json.loads(colorset_adapter.CONTRACT.read_text(encoding="utf-8"))["colorsets"]
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(**({} if Path(playwright.chromium.executable_path).exists() else {"channel": "msedge"}))
            page = browser.new_page(viewport={"width": 1440, "height": 1100}, reduced_motion="reduce")
            errors = []
            page.on("pageerror", lambda error: errors.append(str(error)))
            for kind in ["flow", "logo"]:
                values = common(ARTIFACTS, kind)
                if kind == "flow":
                    labels = [f"Step {index:02}" for index in range(1, 17)]
                    values.update(width=3600, height=240, flow_node=labels,
                                  link=list(zip(labels, labels[1:])), link_value=["1"] * 15)
                    selector = ".flow-node > rect"
                else:
                    values.update(brand="Priority", tagline="Complete solid capacity",
                                  logo_mode="wedges", wedge_count=18)
                    selector = ".wedge"
                document, _ = build_contract_artifact.build(argparse.Namespace(**values))
                artifact = ARTIFACTS / f"{kind}-cs1.html"
                artifact.write_text(document, encoding="utf-8")
                page.goto(artifact.as_uri())
                page.wait_for_timeout(750)
                nodes = page.evaluate(INSPECT, selector)
                self.assertEqual([node["fill"] for node in nodes[:16]], SOLIDS)
                self.assertTrue(all(node["stroke"] == "none" and node["width"] == 0 and node["tier"] == "solid" for node in nodes[:16]))
                if kind == "flow":
                    self.assertEqual([node["label"] for node in nodes], labels)
                    self.assertEqual([node["text"] for node in nodes], [palettes["colorset1"]["textOnFill"][paint] for paint in SOLIDS])
                else:
                    self.assertTrue(all(node["stroke"] != "none" and node["width"] > 0 and node["tier"] == "overflow" for node in nodes[16:]))
                self.assertEqual(errors, [])
                page.locator("svg").screenshot(path=str(ARTIFACTS / f"{kind}-cs1.png"))
                (ARTIFACTS / f"{kind}-cs1.json").write_text(json.dumps(nodes, indent=2) + "\n", encoding="utf-8")
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
    result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(ColorsetPriorityTests))
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())
