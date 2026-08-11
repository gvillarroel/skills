#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

from __future__ import annotations

import unittest

from visual_palette import Raster, _lighten_rgb, analyze_visible_palette


class VisualPaletteTests(unittest.TestCase):
    def test_kanban_lighten_transform_retains_canonical_color_groups(self) -> None:
        tokens = ("#007298", "#e77204", "#45842a", "#652f6c")
        pixels = bytearray()
        for token in tokens:
            red, green, blue = _lighten_rgb(token, 10)
            pixels.extend(bytes((red, green, blue, 255)) * 32)
        raster = Raster(width=32, height=4, rgba=bytes(pixels))

        result = analyze_visible_palette(
            raster,
            "colorset2",
            required_groups=("accent", "warning", "success", "special"),
            min_distinct_colors=4,
            min_pixels_per_color=24,
            min_palette_pixels=96,
            min_palette_ratio=0.95,
            tolerance=1,
        )

        self.assertTrue(result["ok"], result)
        self.assertEqual(result["visibleDistinctColors"], 4)
        self.assertEqual(
            result["visibleTokens"],
            ["#007298", "#45842a", "#652f6c", "#e77204"],
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
