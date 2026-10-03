#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "Pillow>=11.0.0",
#   "playwright>=1.52.0",
# ]
# ///

"""Focused deterministic tests for the one-bit SVG transformer and validator."""

from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

from PIL import Image


SCRIPT_DIR = Path(__file__).resolve().parent


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


stylize = load_module("one_bit_stylize", SCRIPT_DIR / "stylize_svg.py")
validator = load_module("one_bit_validator", SCRIPT_DIR / "validate_stylized_svg.py")


class ColorTests(unittest.TestCase):
    def test_parse_and_normalize_hex(self) -> None:
        self.assertEqual(stylize.parse_hex_color("#Ab3"), (170, 187, 51))
        self.assertEqual(stylize.color_hex((170, 187, 51)), "#aabb33")
        with self.assertRaises(Exception):
            stylize.parse_hex_color("orange")

    def test_region_companion_uses_stronger_contrast(self) -> None:
        self.assertEqual(stylize.choose_companion((20, 30, 40)).companion, stylize.WHITE)
        self.assertEqual(stylize.choose_companion((240, 210, 60)).companion, stylize.BLACK)


class QualityProfileTests(unittest.TestCase):
    def test_profiles_increase_sampling_density(self) -> None:
        compact = stylize.resolve_quality_settings("compact")
        balanced = stylize.resolve_quality_settings("balanced")
        detailed = stylize.resolve_quality_settings("detailed")
        compact_columns = compact["render_width"] / compact["cell_size"]
        balanced_columns = balanced["render_width"] / balanced["cell_size"]
        detailed_columns = detailed["render_width"] / detailed["cell_size"]
        self.assertLess(compact_columns, balanced_columns)
        self.assertLess(balanced_columns, detailed_columns)
        self.assertLess(compact["region_colors"], detailed["region_colors"])

    def test_explicit_values_override_one_profile_field_at_a_time(self) -> None:
        resolved = stylize.resolve_quality_settings(
            "detailed",
            render_width=1024,
            cell_size=3,
            contrast=1.4,
            region_colors=9,
        )
        self.assertEqual(resolved["render_width"], 1024)
        self.assertEqual(resolved["cell_size"], 3)
        self.assertEqual(resolved["matrix_size"], 4)
        self.assertEqual(resolved["contrast"], 1.4)
        self.assertEqual(resolved["region_colors"], 9)


class RasterInputTests(unittest.TestCase):
    def test_common_raster_formats_are_detected_from_content(self) -> None:
        formats = {
            "PNG": ".png",
            "JPEG": ".jpg",
            "WEBP": ".webp",
            "BMP": ".bmp",
            "TIFF": ".tiff",
        }
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            source = Image.new("RGBA", (48, 30), (30, 90, 180, 200))
            for format_name, suffix in formats.items():
                with self.subTest(format=format_name):
                    path = root / f"source{suffix}"
                    frame = source.convert("RGB") if format_name in {"JPEG", "BMP"} else source
                    try:
                        frame.save(path, format=format_name)
                    except OSError as error:
                        self.skipTest(f"Pillow build does not encode {format_name}: {error}")
                    info = stylize.inspect_source(path)
                    self.assertEqual(info.kind, "raster")
                    self.assertEqual(info.format, format_name)
                    self.assertEqual((info.width, info.height), (48, 30))
                    self.assertEqual(info.frame_count, 1)

    def test_exif_orientation_changes_intrinsic_aspect_ratio(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            path = Path(temporary_directory) / "rotated.jpg"
            image = Image.new("RGB", (40, 20), (120, 80, 40))
            exif = Image.Exif()
            exif[274] = 6
            image.save(path, exif=exif)
            info = stylize.inspect_source(path)
            self.assertEqual((info.width, info.height), (20, 40))
            self.assertAlmostEqual(stylize.source_aspect_ratio(path), 0.5)

    def test_animated_gif_frame_can_be_selected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            path = Path(temporary_directory) / "animated.gif"
            red = Image.new("RGBA", (12, 8), (255, 0, 0, 255))
            blue = Image.new("RGBA", (12, 8), (0, 0, 255, 255))
            red.save(path, save_all=True, append_images=[blue], duration=100, loop=0)
            info = stylize.inspect_source(path, 1)
            self.assertEqual(info.frame_count, 2)
            self.assertEqual(info.frame_index, 1)
            rendered = stylize.render_raster(path, 24, 16, 1)
            center = rendered.getpixel((12, 8))
            self.assertGreater(center[2], center[0])
            with self.assertRaises(SystemExit):
                stylize.inspect_source(path, 2)

    def test_png_alpha_survives_raster_loading(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            path = Path(temporary_directory) / "alpha.png"
            image = Image.new("RGBA", (16, 16), (200, 30, 50, 255))
            image.putpixel((0, 0), (0, 0, 0, 0))
            image.save(path)
            rendered = stylize.render_raster(path, 16, 16)
            self.assertEqual(rendered.getpixel((0, 0))[3], 0)
            self.assertEqual(rendered.getpixel((8, 8))[3], 255)

    def test_cmyk_jpeg_is_normalized_to_rgba(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            path = Path(temporary_directory) / "print-photo.jpg"
            Image.new("CMYK", (24, 16), (30, 120, 0, 10)).save(path, format="JPEG")
            rendered = stylize.render_raster(path, 48, 32)
            self.assertEqual(rendered.mode, "RGBA")
            self.assertEqual(rendered.size, (48, 32))
            self.assertEqual(rendered.getextrema()[3], (255, 255))


class GridTests(unittest.TestCase):
    def setUp(self) -> None:
        self.pixels = [
            [(0, 0, 0), (255, 255, 255), (230, 30, 30), (30, 80, 230)],
            [(255, 255, 255), (0, 0, 0), (230, 30, 30), (30, 80, 230)],
            [(0, 0, 0), (255, 255, 255), (245, 210, 50), (20, 40, 60)],
            [(255, 255, 255), (0, 0, 0), (245, 210, 50), (20, 40, 60)],
        ]
        self.alphas = [[255] * 4 for _ in range(4)]

    def test_original_mode_has_exact_two_color_contract(self) -> None:
        grid, paints, regions = stylize.build_paint_grid(
            self.pixels,
            self.alphas,
            mode="original",
            matrix_size=4,
            contrast=1.0,
            alpha_threshold=24,
        )
        self.assertEqual([paint.color for paint in paints], [stylize.BLACK, stylize.WHITE])
        self.assertEqual(regions, [])
        self.assertTrue({cell for row in grid for cell in row}.issubset({0, 1}))

    def test_custom_mode_uses_requested_color_and_white(self) -> None:
        custom = (158, 27, 50)
        _, paints, regions = stylize.build_paint_grid(
            self.pixels,
            self.alphas,
            mode="custom",
            matrix_size=4,
            contrast=1.0,
            alpha_threshold=24,
            custom_color=custom,
        )
        self.assertEqual([paint.color for paint in paints], [custom, stylize.WHITE])
        self.assertEqual(regions, [])

    def test_regional_quantization_and_pairing_are_deterministic(self) -> None:
        first_assignments, first_colors = stylize.quantize_regions(self.pixels, self.alphas, 24, 4)
        second_assignments, second_colors = stylize.quantize_regions(self.pixels, self.alphas, 24, 4)
        self.assertEqual(first_assignments, second_assignments)
        self.assertEqual(first_colors, second_colors)
        self.assertGreaterEqual(len(first_colors), 2)
        self.assertLessEqual(len(first_colors), 4)

        grid, paints, pairs = stylize.build_paint_grid(
            self.pixels,
            self.alphas,
            mode="regional",
            matrix_size=4,
            contrast=1.0,
            alpha_threshold=24,
            region_assignments=first_assignments,
            region_colors=first_colors,
        )
        self.assertEqual(len(paints), len(pairs) * 2)
        self.assertTrue(all(pair.companion in {stylize.BLACK, stylize.WHITE} for pair in pairs))
        self.assertTrue(all(cell >= 0 for row in grid for cell in row))

    def test_regional_palette_keeps_small_saturated_zones(self) -> None:
        histogram = {
            (18 + index * 5, 38 + index * 6, 76 + index * 8): 120
            for index in range(8)
        }
        rare_colors = {(205, 55, 40), (225, 195, 45), (45, 120, 60)}
        histogram.update({color: 4 for color in rare_colors})
        palette = stylize.select_region_palette(histogram, 6)
        self.assertTrue(rare_colors.issubset(set(palette)), palette)

    def test_transparent_cells_are_omitted(self) -> None:
        alphas = [row[:] for row in self.alphas]
        alphas[1][2] = 0
        grid, _, _ = stylize.build_paint_grid(
            self.pixels,
            alphas,
            mode="original",
            matrix_size=4,
            contrast=1.0,
            alpha_threshold=24,
        )
        self.assertEqual(grid[1][2], -1)


class ArtifactTests(unittest.TestCase):
    def build_artifact(
        self,
        mode: str,
        custom_color=None,
        source_info=None,
    ) -> tuple[str, dict[str, object]]:
        pixels = [
            [(0, 0, 0), (255, 255, 255), (40, 70, 100), (240, 210, 30)],
            [(255, 255, 255), (0, 0, 0), (40, 70, 100), (240, 210, 30)],
            [(0, 0, 0), (255, 255, 255), (40, 70, 100), (240, 210, 30)],
            [(255, 255, 255), (0, 0, 0), (40, 70, 100), (240, 210, 30)],
        ]
        alphas = [[255] * 4 for _ in range(4)]
        assignments = None
        colors = None
        if mode == "regional":
            assignments, colors = stylize.quantize_regions(pixels, alphas, 24, 3)
        grid, paints, pairs = stylize.build_paint_grid(
            pixels,
            alphas,
            mode=mode,
            matrix_size=4,
            contrast=1.0,
            alpha_threshold=24,
            custom_color=custom_color,
            region_assignments=assignments,
            region_colors=colors,
        )
        return stylize.build_svg(
            width=16,
            height=16,
            cell_size=4,
            grid=grid,
            paints=paints,
            mode=mode,
            matrix_size=4,
            contrast=1.0,
            alpha_threshold=24,
            source_name="fixture.png" if source_info and source_info.kind == "raster" else "fixture.svg",
            title="Fixture",
            custom_color=custom_color,
            region_pairs=pairs,
            quality_profile="balanced",
            source_info=source_info,
        )

    def test_all_modes_pass_independent_validator(self) -> None:
        cases = [
            ("original", None),
            ("custom", (158, 27, 50)),
            ("regional", None),
        ]
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            for mode, custom_color in cases:
                with self.subTest(mode=mode):
                    markup, _ = self.build_artifact(mode, custom_color)
                    path = root / f"{mode}.svg"
                    path.write_text(markup, encoding="utf-8")
                    report = validator.validate_svg(
                        path,
                        expect_mode=mode,
                        expect_custom_color=stylize.color_hex(custom_color) if custom_color else None,
                    )
                    self.assertTrue(report["ok"])
                    self.assertEqual(report["mode"], mode)
                    self.assertEqual(report["qualityProfile"], "balanced")

    def test_artifact_contains_no_raster_or_script_nodes(self) -> None:
        markup, _ = self.build_artifact("original")
        self.assertNotIn("<image", markup)
        self.assertNotIn("<script", markup)
        self.assertIn("shape-rendering:crispEdges", markup)

    def test_raster_provenance_passes_independent_validator(self) -> None:
        source_info = stylize.SourceInfo("raster", "PNG", 0, 1, 640, 360)
        markup, _ = self.build_artifact("original", source_info=source_info)
        with tempfile.TemporaryDirectory() as temporary_directory:
            path = Path(temporary_directory) / "raster-source.svg"
            path.write_text(markup, encoding="utf-8")
            report = validator.validate_svg(
                path,
                expect_mode="original",
                expect_source_kind="raster",
                expect_source_format="PNG",
                expect_source_frame=0,
            )
            self.assertEqual(report["sourceKind"], "raster")
            self.assertEqual(report["sourceFormat"], "PNG")

    def test_aspect_ratio_prefers_viewbox(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            source = Path(temporary_directory) / "source.svg"
            source.write_text(
                '<svg xmlns="http://www.w3.org/2000/svg" width="10" height="10" viewBox="0 0 16 9"/>',
                encoding="utf-8",
            )
            self.assertAlmostEqual(stylize.source_aspect_ratio(source), 16 / 9)
            self.assertEqual(stylize.resolve_render_size(source, 320, None), (320, 180))

    def test_validator_rejects_raster_image_injection(self) -> None:
        markup, _ = self.build_artifact("original")
        markup = markup.replace("  </g>", '    <image href="data:image/png;base64,AA==" />\n  </g>')
        with tempfile.TemporaryDirectory() as temporary_directory:
            path = Path(temporary_directory) / "bad.svg"
            path.write_text(markup, encoding="utf-8")
            with self.assertRaises(validator.ValidationFailure):
                validator.validate_svg(path, expect_mode="original")


if __name__ == "__main__":
    unittest.main(verbosity=2)
