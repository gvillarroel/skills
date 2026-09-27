#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Keep SMIL animation lifetime separate from SVG paint validation."""

import importlib.util
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("palette_checker", ROOT / "skills/d3/scripts/check_palette_contract.py")
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)


class AnimationPaintTests(unittest.TestCase):
    def check(self, markup):
        folder = ROOT / "projects/library-composition/artifacts"
        folder.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=folder) as temporary:
            source = Path(temporary) / "sample.svg"
            source.write_text(f'<svg data-colorset="colorset1">{markup}</svg>', encoding="utf-8")
            return checker.validate_artifact(source, colorset="colorset1")

    def test_animation_lifetime_is_not_a_color(self):
        for tag in ("animate", "animateMotion", "animateTransform", "set"):
            for lifetime in ("freeze", "remove"):
                with self.subTest(tag=tag, lifetime=lifetime):
                    result = self.check(f'<rect fill="#9e1b32"><{tag} fill="{lifetime}"/></rect>')
                    self.assertTrue(result["ok"], result)

    def test_invalid_rect_paint_still_fails(self):
        for paint in ("freeze", "remove", "red"):
            with self.subTest(paint=paint):
                self.assertFalse(self.check(f'<rect fill="{paint}"/>')["ok"])

    def test_animation_target_color_still_checked(self):
        result = self.check('<animate attributeName="fill" from="#9e1b32" to="#007298" fill="freeze"/>')
        self.assertFalse(result["ok"])
        self.assertEqual(result["forbiddenColors"], ["#007298"])

    def test_invalid_animation_fill_still_fails(self):
        self.assertFalse(self.check('<animate fill="pink"/>')["ok"])


if __name__ == "__main__":
    unittest.main()
