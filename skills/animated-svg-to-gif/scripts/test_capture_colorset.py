#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright>=1.49.0"]
# ///
"""Reject off-palette authored backgrounds before launching capture tools."""
import importlib.util
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

PATH = Path(__file__).with_name("convert_animated_svg_to_gif.py")
SPEC = importlib.util.spec_from_file_location("capture_converter", PATH)
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class BackgroundContractTests(unittest.TestCase):
    def parse(self, *argv):
        with patch.object(sys, "argv", ["convert", "source.svg", *argv]):
            return MODULE.parse_args()

    def test_default_and_shorthand_backgrounds(self):
        self.assertEqual(self.parse().background, "#ffffff")
        self.assertEqual(self.parse("--background", "#fff").background, "#ffffff")
        self.assertEqual(self.parse("--background", "transparent").background, "transparent")

    def test_extended_color_requires_active_set(self):
        with self.assertRaises(SystemExit):
            self.parse("--background", "#007298")
        self.assertEqual(self.parse("--colorset", "colorset2", "--background", "#007298").background, "#007298")

    def test_rogue_background_rejected(self):
        for token in ("#abcdef", "red", "rgb(255,0,0)"):
            with self.assertRaises(SystemExit):
                self.parse("--background", token)


if __name__ == "__main__":
    unittest.main()
