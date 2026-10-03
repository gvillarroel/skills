#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright>=1.52.0", "pillow>=10.0.0"]
# ///
"""Verify generated foregrounds against actual rendered surface roles."""

from __future__ import annotations

import copy
import json
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest

sys.dont_write_bytecode = True
from playwright.sync_api import sync_playwright
import compile_synchronized_svg_plan as compiler
import compose_synchronized_svg as composer
from text_contrast import audit_text_contrast

TEMPLATES = Path(__file__).resolve().parents[1] / "assets/templates"


class SvgTextPairTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.playwright = sync_playwright().start()
        cls.browser = cls.playwright.chromium.launch(headless=True)

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.playwright.stop()

    def render(self, brief):
        temporary = tempfile.TemporaryDirectory(prefix="text-pairs-")
        self.addCleanup(temporary.cleanup)
        directory = Path(temporary.name)
        plan, _ = compiler.compile_brief(brief)
        spec, svg = directory / "plan.json", directory / "diagram.svg"
        spec.write_text(json.dumps(plan), encoding="utf-8")
        composer.compose(SimpleNamespace(spec=spec, output=svg, report=None, force=True))
        page = self.browser.new_page(viewport={"width": 1800, "height": 1200})
        self.addCleanup(page.close)
        page.goto(svg.as_uri())
        page.wait_for_function("window.svgSync && document.documentElement.dataset.syncReady === 'true'")
        page.evaluate("() => {svgSync.pause(); svgSync.pauseCamera(); svgSync.reset();}")
        return page, plan

    def test_readable_value_text_does_not_recolor_the_brand_mark(self):
        brief = json.loads((TEMPLATES / "composition-brief.json").read_text(encoding="utf-8"))
        brief["theme"] = {"conceptColors": {"input-rate": "#828282"}}
        page, plan = self.render(brief)
        actual = page.evaluate("""() => ({
          mark:getComputedStyle(document.documentElement).getPropertyValue('--concept-input-rate').trim(),
          fill:getComputedStyle(document.querySelector('text[data-bind="input-rate"]')).fill,
          explicit:(() => {const t=document.createElementNS('http://www.w3.org/2000/svg','text');
            t.setAttribute('fill','#ffffff');document.documentElement.appendChild(t);
            const fill=getComputedStyle(t).fill;t.remove();return fill;})()
        })""")
        self.assertEqual(actual["mark"], "#828282")
        self.assertEqual(plan["theme"]["conceptColors"]["input-rate"], "#828282")
        self.assertEqual(actual["fill"], "rgb(0, 0, 0)")
        self.assertEqual(actual["explicit"], "rgb(255, 255, 255)")
        self.assertTrue(audit_text_contrast(page)["ok"])

    def test_near_threshold_text_remains_readable_during_focus(self):
        brief = json.loads((TEMPLATES / "composition-brief.json").read_text(encoding="utf-8"))
        brief["theme"] = {"colors": {"canvas": "#ffffff", "surface": "#ffffff", "ink": "#696969", "muted": "#696969"}}
        page, plan = self.render(brief)
        for focus in [None, *[item["id"] for item in plan["focusGroups"]]]:
            page.evaluate("focus => svgSync.setFocus(focus)", focus)
            report = audit_text_contrast(page)
            self.assertTrue(report["ok"], report)
            self.assertGreater(report["checked"], 60)

    def test_navigation_text_and_focus_border_use_the_inverse_surface(self):
        brief = json.loads((TEMPLATES / "navigable-world-brief.json").read_text(encoding="utf-8"))
        page, _ = self.render(brief)
        colors = page.evaluate("""() => {
          const control=document.querySelector('.navigation-control:not([aria-disabled="true"])');control.focus();
          return {background:getComputedStyle(document.querySelector('.navigation-hud-panel')).fill,
            tier:getComputedStyle(document.querySelector('.navigation-current-tier')).fill,
            help:getComputedStyle(document.querySelector('.navigation-help')).fill,
            focus:getComputedStyle(control.querySelector('rect')).stroke};
        }""")
        self.assertEqual(colors["background"], "rgb(51, 62, 72)")
        self.assertEqual(colors["focus"], "rgb(255, 255, 255)")
        self.assertEqual(colors["tier"], "rgb(255, 255, 255)")
        self.assertEqual(colors["help"], colors["tier"])
        self.assertTrue(audit_text_contrast(page)["ok"])


if __name__ == "__main__":
    unittest.main()
