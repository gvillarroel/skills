#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["pillow>=10.0.0"]
# ///
"""Verify actual-scale module crops and boundaries of screenshot evidence."""
import argparse
import tempfile
import unittest
from pathlib import Path

from PIL import Image
from crop_modules import crop_modules


class CropModuleTests(unittest.TestCase):
    work_dir = Path.cwd() / "output/module-crop-tests"

    def setUp(self):
        self.work_dir.mkdir(parents=True, exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(dir=self.work_dir)
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.screenshot = self.root / "overview.png"
        image = Image.new("RGB", (100, 50), "white")
        image.paste("red", (20, 10, 60, 40))
        image.save(self.screenshot)
        self.plan = {"viewBox": [10, 20, 200, 100],
                     "modules": [{"id": "red-module", "region": [50, 40, 80, 60]}]}

    def test_crop_preserves_pixels_at_source_scale(self):
        report = crop_modules(self.plan, self.screenshot, self.root / "crops")
        self.assertEqual(report["scale"], 0.5)
        self.assertFalse(report["upscaled"])
        self.assertEqual(report["modules"][0]["pixelBox"], [20, 10, 60, 40])
        with Image.open(report["modules"][0]["path"]) as crop:
            self.assertEqual(crop.size, (40, 30))
            self.assertEqual(crop.getextrema(), ((255, 255), (0, 0), (0, 0)))

    def test_world_and_mismatched_screenshot_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "camera-anchor"):
            crop_modules({**self.plan, "navigation": {"worldBounds": [0, 0, 100, 100]}}, self.screenshot, self.root / "crops")
        with self.assertRaisesRegex(ValueError, "aspect ratio"):
            crop_modules({**self.plan, "viewBox": [0, 0, 100, 100]}, self.screenshot, self.root / "crops")

    def test_escaping_ids_and_source_overwrite_are_rejected(self):
        for bad_id in ("../red-module", "overview"):
            plan = {**self.plan, "modules": [{"id": bad_id, "region": [50, 40, 80, 60]}]}
            with self.assertRaises(ValueError):
                crop_modules(plan, self.screenshot, self.root)
        with Image.open(self.screenshot) as source:
            self.assertEqual(source.size, (100, 50))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--work-dir", type=Path, default=CropModuleTests.work_dir)
    args, remaining = parser.parse_known_args()
    CropModuleTests.work_dir = args.work_dir
    unittest.main(argv=[__file__, *remaining])
