#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["pillow>=10.0.0", "playwright>=1.52.0"]
# ///
"""Browser regressions for local text/background measurement and exact restoration."""

from __future__ import annotations

import unittest
from unittest.mock import patch

from playwright.sync_api import sync_playwright

from text_contrast import audit_text_contrast, _contrast


def svg(body: str) -> str:
    return ('<svg xmlns="http://www.w3.org/2000/svg" width="500" height="240">'
            '<style>text {font: bold 22px sans-serif}</style>'
            '<rect width="500" height="240" fill="white"/>' + body + '</svg>')


class TextContrastTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.playwright = sync_playwright().start()
        cls.browser = cls.playwright.chromium.launch(headless=True)

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.playwright.stop()

    def inspect(self, body, *, dpr=1):
        context = self.browser.new_context(viewport={"width": 540, "height": 280}, device_scale_factor=dpr)
        self.addCleanup(context.close)
        page = context.new_page()
        page.set_content(svg(body))
        before = page.content()
        report = audit_text_contrast(page)
        self.assertEqual(page.content(), before, "Every style on every node must be restored")
        return report, {item["id"]: item for item in report["findings"]}

    def test_actual_dark_and_pale_panels_override_white_canvas(self):
        report, findings = self.inspect(
            '<rect x="0" y="0" width="240" height="110" fill="#252525"/>'
            '<text id="good-dark" x="10" y="36" fill="white">Readable dark</text>'
            '<text id="bad-dark" x="10" y="80" fill="#203332">Unreadable dark</text>'
            '<rect x="250" y="0" width="250" height="110" fill="#fff0a8"/>'
            '<text id="bad-pale" x="260" y="36" fill="white">Pale label</text>'
            '<text id="good-pale" x="260" y="80" fill="#203332">Readable pale</text>')
        self.assertEqual(report["checked"], 4)
        self.assertEqual(report["failed"], 2)
        self.assertEqual(report["incomplete"], 0)
        self.assertEqual(findings["good-dark"]["status"], "pass")
        self.assertEqual(findings["bad-dark"]["status"], "fail")
        self.assertEqual(findings["bad-pale"]["status"], "fail")
        self.assertEqual(findings["good-pale"]["status"], "pass")
        self.assertEqual(findings["bad-dark"]["background"], [37, 37, 37])

    def test_fill_and_text_opacity_reduce_effective_contrast(self):
        report, findings = self.inspect(
            '<text id="alpha" x="20" y="40" fill="#000000" fill-opacity=".3">Alpha text</text>'
            '<text id="opacity" x="20" y="90" fill="#000000" opacity=".4">Faded text</text>')
        self.assertEqual(report["failed"], 2)
        self.assertAlmostEqual(findings["alpha"]["ratio"], _contrast([178.5] * 3, [255] * 3), places=8)
        self.assertAlmostEqual(findings["opacity"]["ratio"], _contrast([153] * 3, [255] * 3), places=8)

    def test_gradient_background_uses_worst_glyph_region(self):
        report, findings = self.inspect(
            '<defs><linearGradient id="bg"><stop stop-color="#152025"/>'
            '<stop offset="1" stop-color="#fff0a8"/></linearGradient></defs>'
            '<rect width="490" height="100" fill="url(#bg)"/>'
            '<text id="gradient" x="10" y="55" fill="white">Across dark and very pale backgrounds</text>')
        self.assertEqual(findings["gradient"]["status"], "fail")
        self.assertGreater(findings["gradient"]["backgroundSamples"], 20)
        self.assertEqual(report["incomplete"], 0)

    def test_homogeneous_wrapped_tspans_are_measured(self):
        report, findings = self.inspect(
            '<text id="wrapped" x="20" y="40" fill="#203332">'
            '<tspan>First line</tspan><tspan x="20" dy="30">Second line</tspan></text>')
        self.assertTrue(report["ok"])
        self.assertEqual(findings["wrapped"]["status"], "pass")

    def test_unsupported_text_paints_and_group_compositing_are_incomplete(self):
        report, findings = self.inspect(
            '<defs><linearGradient id="fg"><stop stop-color="black"/><stop offset="1" stop-color="white"/></linearGradient></defs>'
            '<text id="gradient-fill" x="10" y="30" fill="url(#fg)">Gradient fill</text>'
            '<text id="mixed" x="10" y="65" fill="black"><tspan fill="white">Mixed paint</tspan></text>'
            '<g opacity=".5"><rect y="70" width="250" height="50" fill="black"/>'
            '<text id="group-alpha" x="10" y="103" fill="white">Group alpha</text></g>'
            '<g style="filter:saturate(.4)"><text id="filtered" x="10" y="150">Filtered</text></g>')
        self.assertEqual(report["incomplete"], 4)
        self.assertFalse(report["ok"])
        for key in ("gradient-fill", "mixed", "group-alpha", "filtered"):
            self.assertEqual(findings[key]["status"], "inconclusive")

    def test_dpr_two_matches_css_pixel_coordinates(self):
        body = ('<rect x="10" y="20" width="210" height="70" fill="#203332"/>'
                '<text id="label" x="20" y="62" fill="white">Dark surface</text>')
        first, a = self.inspect(body, dpr=1)
        second, b = self.inspect(body, dpr=2)
        self.assertTrue(first["ok"] and second["ok"])
        self.assertEqual(a["label"]["background"], b["label"]["background"])
        self.assertAlmostEqual(a["label"]["ratio"], b["label"]["ratio"], places=8)

    def test_css_precedence_and_color_mix_resolve_in_the_browser(self):
        report, findings = self.inspect(
            '<text id="style" x="20" y="40" fill="white" style="fill:#203332">CSS wins</text>'
            '<text id="mix" x="20" y="80" fill="color-mix(in srgb, black 90%, white)">CSS color mix</text>')
        self.assertTrue(report["ok"])
        self.assertEqual(findings["style"]["color"][:3], [32, 51, 50])
        self.assertEqual(findings["mix"]["status"], "pass")

    def test_hidden_disabled_and_empty_coverage_do_not_fake_a_pass(self):
        report, _ = self.inspect(
            '<text x="10" y="30" opacity="0">Transparent</text>'
            '<g style="display:none"><text x="10" y="60">Hidden ancestor</text></g>'
            '<text x="600" y="40">Offscreen</text>'
            '<g aria-disabled="true"><text x="10" y="90">Disabled control</text></g>')
        self.assertEqual(report["skipped"], 4)
        self.assertEqual(report["checked"], 0)
        self.assertFalse(report["ok"])

    def test_every_style_is_restored_when_mask_capture_fails(self):
        page = self.browser.new_page(viewport={"width": 540, "height": 280})
        self.addCleanup(page.close)
        page.set_content(svg('<g style="fill:blue"><text x="20" y="40" style="fill:black">Text</text></g>'))
        before = page.content()
        capture = page.screenshot
        calls = 0
        def broken_capture(**kwargs):
            nonlocal calls
            calls += 1
            if calls == 2:
                raise RuntimeError("test capture failure")
            return capture(**kwargs)
        with patch.object(page, "screenshot", side_effect=broken_capture):
            with self.assertRaisesRegex(RuntimeError, "test capture failure"):
                audit_text_contrast(page)
        self.assertEqual(page.content(), before)

    def test_repeated_audits_do_not_start_filter_transitions(self):
        page = self.browser.new_page(viewport={"width": 540, "height": 280})
        self.addCleanup(page.close)
        page.set_content(svg('<style>rect {transition:filter 2s}</style>'
                             '<text id="near" x="20" y="40" fill="#767676">Near threshold</text>'))
        before = page.content()
        for _ in range(3):
            report = audit_text_contrast(page)
            self.assertTrue(report["ok"], report)
            self.assertEqual(page.content(), before)
            self.assertEqual(page.locator("rect").evaluate("el => getComputedStyle(el).filter"), "none")


if __name__ == "__main__":
    unittest.main()
