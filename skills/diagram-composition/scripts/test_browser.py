#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright>=1.52.0"]
# ///
"""Browser controls for geometry, readability, and CSS import fidelity."""

import json
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

sys.dont_write_bytecode = True
from audit_diagram import run
from compose_diagram import compose, parse_svg
from test_composition import panel


class BrowserTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="diagram-browser-", dir=Path.cwd())
        self.root = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def audit(self, content, minimum=14, overflow="hidden"):
        source = self.root / "source.svg"
        source.write_text(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 300" overflow="{overflow}">' + content + '</svg>', encoding="utf-8")
        p = panel("single", 1, 1, 1, 1); p["source"] = "source.svg"
        spec = {"version": 1, "title": "Readable figure", "thesis": "One geometric control.",
                "canvas": {"width": 500, "height": 440, "displayWidth": 500, "minTextPx": minimum,
                "margin": 20, "gap": 20, "titleHeight": 50, "footerHeight": 20},
                "grid": {"columns": [1], "rows": [1]}, "concepts": [{"id": "engine", "label": "Engine"}],
                "panels": [p]}
        svg, _ = compose(spec, self.root / "plan.json")
        figure = self.root / "figure.svg"; figure.write_text(svg, encoding="utf-8")
        return run(SimpleNamespace(command="audit", input=figure, output=None,
            report=self.root / "audit.json", screenshot=self.root / "preview.png", overwrite=True))

    def test_readable(self):
        result = self.audit('<text x="20" y="60" font-size="20">Engine</text>')
        self.assertTrue(result["ok"], result)
        self.assertGreaterEqual(result["minimumObservedPx"], 14)

    def test_small_text(self):
        result = self.audit('<text x="20" y="60" font-size="8">Tiny</text>')
        self.assertFalse(result["ok"])
        self.assertIn("small-text", {x["kind"] for x in result["issues"]})

    def test_small_tspan(self):
        result = self.audit('<text x="20" y="60" font-size="20">Engine <tspan font-size="8">condition</tspan></text>')
        self.assertIn("small-text", {x["kind"] for x in result["issues"]})

    def test_collision(self):
        result = self.audit('<text x="20" y="60" font-size="20">Engine</text><text x="25" y="60" font-size="20">Collision</text>')
        self.assertIn("text-collision", {x["kind"] for x in result["issues"]})

    def test_text_overflow(self):
        result = self.audit('<text x="380" y="60" font-size="20">Outside the body</text>')
        self.assertIn("panel-overflow", {x["kind"] for x in result["issues"]})

    def test_cross_panel_connector_crosses_label(self):
        result = self.audit('<text x="20" y="60" font-size="20">Readable label</text><g data-relation-id="test-link"><path d="M0 55 L200 55" stroke="black"/></g>')
        self.assertIn("connector-text-collision", {x["kind"] for x in result["issues"]})

    def test_mark_overflow(self):
        result = self.audit('<circle cx="500" cy="60" r="30"/><text x="20" y="80" font-size="20">Engine</text>', overflow="visible")
        self.assertIn("mark-overflow", {x["kind"] for x in result["issues"]})

    def test_intentional_viewport_clip_reported_for_review(self):
        result = self.audit('<line x1="20" y1="40" x2="20" y2="2000" stroke="black"/><text x="40" y="80" font-size="20">Lifeline</text>')
        self.assertTrue(result["ok"])
        self.assertEqual(len(result["clippedMarks"]), 1)

    def test_prepare_styles_and_local_gradient(self):
        source, dest = self.root / "css.svg", self.root / "ready.svg"
        source.write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><style>.label{fill:#9e1b32;font-size:18px}.shape{fill:url(#paint)}</style><defs><linearGradient id="paint"><stop offset="0" stop-color="red"/></linearGradient></defs><rect class="shape" width="100" height="100"/><text class="label" x="10" y="30">Hello</text></svg>', encoding="utf-8")
        result = run(SimpleNamespace(command="prepare", input=source, output=dest, report=None, screenshot=None, overwrite=False))
        self.assertTrue(result["ok"])
        root, _, _ = parse_svg(dest)
        content = dest.read_text(encoding="utf-8")
        self.assertNotIn('<style', content)
        self.assertIn('rgb(158, 27, 50)', content)
        self.assertIn('url(#paint)', content)

    def test_unused_renderer_animation_css(self):
        source, dest = self.root / "unused.svg", self.root / "ready.svg"
        source.write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><style>@keyframes pulse{to{opacity:0}}.unused{animation:pulse 2s infinite}</style><circle cx="50" cy="50" r="20"/></svg>', encoding="utf-8")
        result = run(SimpleNamespace(command="prepare", input=source, output=dest, report=None, screenshot=None, overwrite=False))
        self.assertTrue(result["ok"])
        self.assertNotIn("@keyframes", dest.read_text(encoding="utf-8"))

    def test_active_animation_is_not_a_static_export(self):
        source, dest = self.root / "active.svg", self.root / "ready.svg"
        source.write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><style>@keyframes pulse{to{opacity:0}}circle{animation:pulse 2s infinite}</style><circle cx="50" cy="50" r="20"/></svg>', encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "Active CSS animation"):
            run(SimpleNamespace(command="prepare", input=source, output=dest, report=None, screenshot=None, overwrite=False))


if __name__ == "__main__":
    unittest.main()
