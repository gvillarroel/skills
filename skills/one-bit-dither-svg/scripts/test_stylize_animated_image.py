#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "Pillow>=11.0.0",
#   "playwright>=1.52.0",
# ]
# ///

"""Regression tests for animated one-bit image conversion."""

from __future__ import annotations

import importlib.util
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

from PIL import Image, ImageDraw


SCRIPT_DIR = Path(__file__).resolve().parent


def load_script(name: str, filename: str):
    spec = importlib.util.spec_from_file_location(name, SCRIPT_DIR / filename)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {filename}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ANIMATED = load_script("one_bit_dither_animated_test_target", "stylize_animated_image.py")
VALIDATOR = load_script("one_bit_dither_gif_validator_test_target", "validate_animated_gif.py")


def make_source_gif(path: Path) -> None:
    frames: list[Image.Image] = []
    for index in range(4):
        frame = Image.new("RGBA", (80, 48), (245, 240, 222, 255))
        draw = ImageDraw.Draw(frame)
        draw.rectangle((4 + index * 14, 10, 22 + index * 14, 34), fill=(18, 28, 42, 255))
        draw.ellipse((54 - index * 7, 6, 72 - index * 7, 24), fill=(220, 92, 42, 255))
        frames.append(frame)
    frames[0].save(
        path,
        save_all=True,
        append_images=frames[1:],
        duration=[80, 120, 100, 100],
        loop=0,
        disposal=2,
    )


def make_source_svg(path: Path) -> None:
    path.write_text(
        """<svg xmlns="http://www.w3.org/2000/svg" width="80" height="48" viewBox="0 0 80 48">
  <rect width="80" height="48" fill="#f5f0de"/>
  <rect x="4" y="10" width="18" height="24" fill="#121c2a">
    <animate attributeName="x" values="4;58;4" dur="1s" repeatCount="indefinite"/>
  </rect>
  <circle cx="62" cy="16" r="9" fill="#dc5c2a">
    <animate attributeName="cy" values="10;34;10" dur="1s" repeatCount="indefinite"/>
  </circle>
</svg>
""",
        encoding="utf-8",
        newline="\n",
    )


def make_css_source_svg(path: Path) -> None:
    path.write_text(
        """<svg xmlns="http://www.w3.org/2000/svg" width="80" height="48" viewBox="0 0 80 48">
  <style>
    @keyframes slide { 0% { transform: translateX(0px); } 50% { transform: translateX(52px); } 100% { transform: translateX(0px); } }
    .moving { animation: slide 1s linear infinite; }
  </style>
  <rect width="80" height="48" fill="#f5f0de"/>
  <rect class="moving" x="4" y="12" width="20" height="24" fill="#121c2a"/>
</svg>
""",
        encoding="utf-8",
        newline="\n",
    )


class AnimatedDitherTests(unittest.TestCase):
    def test_svg_capture_blocks_external_resources(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            source_path = Path(temporary) / "external.svg"
            source_path.write_text(
                """<svg xmlns="http://www.w3.org/2000/svg" width="80" height="48" viewBox="0 0 80 48">
  <image href="https://example.invalid/external.png" width="80" height="48"/>
  <rect width="20" height="20"><animate attributeName="x" values="0;60;0" dur="1s" repeatCount="indefinite"/></rect>
</svg>
""",
                encoding="utf-8",
                newline="\n",
            )
            source_info = ANIMATED.ENGINE.inspect_source(source_path, 0)
            with self.assertRaisesRegex(SystemExit, "blocked external resources"):
                ANIMATED.capture_svg_animation(
                    source_path,
                    source_info=source_info,
                    size=(80, 48),
                    fps=2,
                    duration_seconds=1,
                    max_frames=10,
                    timeout_ms=30000,
                )

    def test_css_svg_animation_is_sampled_at_explicit_timeline_positions(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            source_path = Path(temporary) / "source.svg"
            make_css_source_svg(source_path)
            source_info = ANIMATED.ENGINE.inspect_source(source_path, 0)
            source = ANIMATED.capture_svg_animation(
                source_path,
                source_info=source_info,
                size=(80, 48),
                fps=4,
                duration_seconds=1,
                max_frames=10,
                timeout_ms=30000,
            )
            self.assertEqual(source.kind, "svg")
            self.assertEqual(source.frame_count, 4)
            self.assertGreaterEqual(len({frame.tobytes() for frame in source.frames}), 3)

    def test_source_timing_is_resampled_to_requested_fps(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            source_path = Path(temporary) / "source.gif"
            make_source_gif(source_path)
            source = ANIMATED.load_animation(source_path)
            self.assertEqual(source.frame_count, 4)
            self.assertEqual(source.duration_ms, 400)
            indices, duration = ANIMATED.build_timeline(
                source,
                fps=10,
                duration_seconds=None,
                max_frames=20,
            )
            self.assertEqual(len(indices), 4)
            self.assertEqual(indices, [0, 1, 2, 3])
            self.assertAlmostEqual(duration, 0.4)

    def test_explicit_duration_wraps_source_timeline(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            source_path = Path(temporary) / "source.gif"
            make_source_gif(source_path)
            source = ANIMATED.load_animation(source_path)
            indices, duration = ANIMATED.build_timeline(
                source,
                fps=10,
                duration_seconds=0.8,
                max_frames=20,
            )
            self.assertEqual(indices, [0, 1, 2, 3, 0, 1, 2, 3])
            self.assertAlmostEqual(duration, 0.8)

    def test_global_regional_palette_is_shared_across_frames(self) -> None:
        grids = {
            0: ([[[(255, 0, 0), (0, 0, 255)]][0]], [[255, 255]]),
            1: ([[[(255, 0, 0), (0, 255, 0)]][0]], [[255, 255]]),
        }
        palette = ANIMATED.build_global_region_palette(grids, alpha_threshold=24, requested_colors=3)
        self.assertEqual(set(palette), {(255, 0, 0), (0, 0, 255), (0, 255, 0)})
        assignments = ANIMATED.assign_global_regions(
            [[(255, 0, 0), (0, 255, 0)]],
            [[255, 255]],
            alpha_threshold=24,
            region_colors=palette,
        )
        self.assertNotEqual(assignments[0][0], assignments[0][1])

    @unittest.skipUnless(shutil.which("ffmpeg"), "ffmpeg is required for the integration test")
    def test_end_to_end_hd_pipeline_contract_at_small_fixture_size(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source_path = root / "source.gif"
            output_path = root / "styled.gif"
            manifest_path = root / "styled.json"
            contact_path = root / "contact.png"
            make_source_gif(source_path)
            result = ANIMATED.main(
                [
                    str(source_path),
                    "--output",
                    str(output_path),
                    "--mode",
                    "original",
                    "--quality-profile",
                    "manual",
                    "--render-width",
                    "160",
                    "--render-height",
                    "96",
                    "--cell-size",
                    "2",
                    "--fps",
                    "10",
                    "--colors",
                    "2",
                    "--contact-sheet",
                    str(contact_path),
                    "--json-report",
                    str(manifest_path),
                ]
            )
            self.assertEqual(result, 0)
            self.assertTrue(output_path.is_file())
            self.assertTrue(contact_path.is_file())
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            self.assertEqual(manifest["source"]["kind"], "raster")
            self.assertEqual(manifest["render"]["frameCount"], 4)
            self.assertEqual(manifest["probe"]["paletteColors"], ["#000000", "#ffffff"])
            validation_result = VALIDATOR.main(
                [
                    str(output_path),
                    "--manifest",
                    str(manifest_path),
                    "--expect-mode",
                    "original",
                    "--expect-source-kind",
                    "raster",
                    "--expect-source-format",
                    "GIF",
                    "--expect-width",
                    "160",
                    "--expect-height",
                    "96",
                    "--expect-fps",
                    "10",
                    "--expect-loop",
                    "0",
                    "--min-frames",
                    "4",
                    "--max-colors",
                    "2",
                ]
            )
            self.assertEqual(validation_result, 0)

    def test_animated_svg_requires_explicit_capture_duration(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source_path = root / "source.svg"
            make_source_svg(source_path)
            with self.assertRaisesRegex(SystemExit, "requires --duration-seconds"):
                ANIMATED.main(
                    [
                        str(source_path),
                        "--output",
                        str(root / "styled.gif"),
                        "--mode",
                        "original",
                    ]
                )

    @unittest.skipUnless(shutil.which("ffmpeg"), "ffmpeg is required for the integration test")
    def test_direct_animated_svg_pipeline_captures_real_motion(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source_path = root / "source.animated.svg"
            output_path = root / "styled.gif"
            manifest_path = root / "styled.json"
            contact_path = root / "contact.png"
            make_source_svg(source_path)
            result = ANIMATED.main(
                [
                    str(source_path),
                    "--output",
                    str(output_path),
                    "--mode",
                    "original",
                    "--quality-profile",
                    "manual",
                    "--render-width",
                    "160",
                    "--render-height",
                    "96",
                    "--cell-size",
                    "2",
                    "--fps",
                    "4",
                    "--duration-seconds",
                    "1",
                    "--colors",
                    "2",
                    "--contact-sheet",
                    str(contact_path),
                    "--json-report",
                    str(manifest_path),
                ]
            )
            self.assertEqual(result, 0)
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            self.assertEqual(manifest["source"]["kind"], "svg")
            self.assertEqual(manifest["source"]["format"], "SVG")
            self.assertEqual(manifest["render"]["captureMethod"], "browser-timeline")
            self.assertEqual(manifest["render"]["frameCount"], 4)
            validation_result = VALIDATOR.main(
                [
                    str(output_path),
                    "--manifest",
                    str(manifest_path),
                    "--expect-mode",
                    "original",
                    "--expect-source-kind",
                    "svg",
                    "--expect-source-format",
                    "SVG",
                    "--expect-width",
                    "160",
                    "--expect-height",
                    "96",
                    "--expect-fps",
                    "4",
                    "--expect-loop",
                    "0",
                    "--min-frames",
                    "4",
                    "--min-distinct-frames",
                    "3",
                    "--max-colors",
                    "2",
                ]
            )
            self.assertEqual(validation_result, 0)
            self.assertTrue(output_path.is_file())
            self.assertTrue(contact_path.is_file())


if __name__ == "__main__":
    unittest.main(verbosity=2)
