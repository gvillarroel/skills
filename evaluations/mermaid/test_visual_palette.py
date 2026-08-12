#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

from __future__ import annotations

import unittest

from visual_palette import Raster, _lighten_rgb, analyze_visible_palette


class VisualPaletteTests(unittest.TestCase):
    def test_standard_red_neutral_plot_palette_counts_every_visible_token(self) -> None:
        tokens = ("#9e1b32", "#4f4f4f", "#828282", "#333e48", "#696969")
        pixels = bytearray()
        for token in tokens:
            red, green, blue = bytes.fromhex(token.removeprefix("#"))
            pixels.extend(bytes((red, green, blue, 255)) * 32)
        raster = Raster(width=32, height=5, rgba=bytes(pixels))

        result = analyze_visible_palette(
            raster,
            "colorset1",
            required_groups=("primary",),
            min_distinct_colors=5,
            min_pixels_per_color=24,
            min_palette_pixels=128,
            min_palette_ratio=0.95,
            tolerance=1,
        )

        self.assertTrue(result["ok"], result)
        self.assertEqual(result["visibleDistinctColors"], 5)

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
