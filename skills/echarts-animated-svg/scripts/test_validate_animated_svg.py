#!/usr/bin/env python3
"""Regression tests for the bundled ECharts animated-SVG validator."""

from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent


def load_module(filename: str, module_name: str):
    spec = importlib.util.spec_from_file_location(module_name, SCRIPT_DIR / filename)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


animate = load_module("animate_echarts_svg.py", "animate_echarts_svg")
validator = load_module("validate_animated_svg.py", "validate_animated_svg")


class ValidatorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.root = Path(self.tempdir.name)
        self.static_svg = self.root / "bar.static.svg"
        self.animated_svg = self.root / "bar.animated.svg"
        template = SCRIPT_DIR.parent / "assets" / "templates" / "static-bar-chart.svg"
        self.static_svg.write_bytes(template.read_bytes())
        animate.animate_svg(self.static_svg, self.animated_svg, "bar", 800, 90, 1100)

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def validate(self):
        return validator.validate_pair(
            self.static_svg,
            self.animated_svg,
            "bar",
            800,
            90,
            1100,
        )

    def test_valid_generated_pair_passes(self) -> None:
        result = self.validate()
        self.assertTrue(result["passed"], result["findings"])
        self.assertEqual(result["evidence"]["drawableCount"], 20)
        self.assertTrue(result["evidence"]["sourceGeometryPreserved"])

    def test_changed_label_fails(self) -> None:
        text = self.animated_svg.read_text(encoding="utf-8")
        self.animated_svg.write_text(text.replace("Quarterly Tickets", "Changed", 1), encoding="utf-8")
        result = self.validate()
        self.assertFalse(result["passed"])
        self.assertTrue(any("labels" in item.lower() or "source elements" in item.lower() for item in result["findings"]))


if __name__ == "__main__":
    unittest.main()
