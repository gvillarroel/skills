#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "Pillow>=11.0.0",
#   "playwright>=1.52.0",
# ]
# ///

"""Deterministic and end-to-end regression tests for pixel-art image/video conversion."""

from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import shutil
import subprocess
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
    previous = sys.dont_write_bytecode
    sys.dont_write_bytecode = True
    try:
        spec.loader.exec_module(module)
    finally:
        sys.dont_write_bytecode = previous
    return module


RENDER = load_script("pixel_art_test_target", "pixel_art.py")
VALIDATE = load_script("pixel_art_validation_test_target", "validate_pixel_art.py")


def quiet_main(module, arguments: list[str]) -> int:
    with contextlib.redirect_stdout(io.StringIO()):
        return module.main(arguments)


def make_sprite(path: Path) -> None:
    image = Image.new("RGBA", (80, 48), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    draw.rectangle((4, 28, 75, 43), fill=(31, 74, 80, 255))
    draw.ellipse((9, 5, 35, 31), fill=(226, 130, 71, 255))
    draw.rectangle((46, 7, 68, 27), fill=(231, 213, 166, 255))
    image.save(path)


def make_svg(path: Path) -> None:
    path.write_text(
        """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 80 48">
  <rect width="80" height="48" fill="#f7e2ad"/>
  <circle cx="19" cy="16" r="10" fill="#e47c47"/>
  <path d="M 0 36 L 30 20 L 50 34 L 80 16 L 80 48 L 0 48 Z" fill="#285c54"/>
</svg>
""",
        encoding="utf-8",
        newline="\n",
    )


def make_video(path: Path) -> None:
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        raise RuntimeError("ffmpeg not found")
    result = subprocess.run(
        [
            ffmpeg, "-hide_banner", "-loglevel", "error", "-y",
            "-f", "lavfi", "-i", "testsrc2=size=80x48:rate=8:duration=1",
            "-f", "lavfi", "-i", "sine=frequency=440:duration=1",
            "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac",
            "-shortest", str(path),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr)


class PixelArtTests(unittest.TestCase):
    def test_color_parser_and_profile_defaults(self) -> None:
        self.assertEqual(RENDER.parse_color("#abc"), (170, 187, 204))
        self.assertEqual(RENDER.parse_color("#123456"), (18, 52, 86))
        self.assertEqual(RENDER.PROFILES["chunky"], (8, 16))
        self.assertEqual(RENDER.PROFILES["detailed"], (3, 32))

    def test_adaptive_palette_is_deterministic_and_bounded(self) -> None:
        image = Image.new("RGB", (32, 32))
        pixels = image.load()
        for y in range(32):
            for x in range(32):
                pixels[x, y] = (x * 8, y * 8, (x + y) * 4)
        first = RENDER.adaptive_palette([image], 8)
        second = RENDER.adaptive_palette([image], 8)
        self.assertEqual(first, second)
        self.assertTrue(2 <= len(first) <= 8)
        output = RENDER.quantize_frame(image, RENDER.build_palette_image(first), dither="none", dither_strength=0)
        self.assertLessEqual(len(output.getcolors(maxcolors=256) or []), 8)

    def test_bayer_pattern_is_stable(self) -> None:
        source = Image.new("RGB", (17, 13), (105, 115, 125))
        first = RENDER.bayer_perturb(source, 0.7)
        second = RENDER.bayer_perturb(source, 0.7)
        self.assertEqual(first.tobytes(), second.tobytes())
        self.assertNotEqual(first.tobytes(), source.tobytes())

    def test_static_png_preserves_hard_alpha_and_exact_grid(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "sprite.png"
            output = root / "sprite-pixel.png"
            report = root / "sprite.json"
            make_sprite(source)
            self.assertEqual(
                quiet_main(
                    RENDER,
                    [
                        str(source), "-o", str(output), "--quality-profile", "manual",
                        "--width", "160", "--height", "96", "--pixel-size", "4",
                        "--palette", "custom", "--color", "#333e48", "--color", "#9e1b32",
                        "--color", "#e7e7e7", "--json-report", str(report),
                    ],
                ),
                0,
            )
            with Image.open(output) as image:
                self.assertEqual(image.size, (160, 96))
                self.assertEqual(image.getchannel("A").getextrema(), (0, 255))
            self.assertEqual(
                quiet_main(
                    VALIDATE,
                    [
                        str(output), "--manifest", str(report), "--expect-width", "160",
                        "--expect-height", "96", "--expect-pixel-size", "4",
                        "--expect-source-kind", "raster", "--expect-palette-mode", "custom",
                        "--max-colors", "3",
                    ],
                ),
                0,
            )
            self.assertTrue(json.loads(report.read_text(encoding="utf-8"))["render"]["alphaPreserved"])

    def test_lossless_webp_output(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source, output, report = root / "source.png", root / "styled.webp", root / "styled.json"
            make_sprite(source)
            self.assertEqual(
                quiet_main(
                    RENDER,
                    [str(source), "-o", str(output), "--palette", "forest4", "--width", "160", "--height", "96", "--json-report", str(report)],
                ),
                0,
            )
            self.assertEqual(
                quiet_main(VALIDATE, [str(output), "--manifest", str(report), "--expect-palette-mode", "forest4", "--max-colors", "4"]),
                0,
            )

    def test_static_svg_is_rendered_directly(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source, output, report = root / "source.svg", root / "styled.png", root / "styled.json"
            make_svg(source)
            self.assertEqual(
                quiet_main(
                    RENDER,
                    [str(source), "-o", str(output), "--width", "160", "--height", "96", "--pixel-size", "4", "--json-report", str(report)],
                ),
                0,
            )
            self.assertEqual(json.loads(report.read_text(encoding="utf-8"))["source"]["kind"], "svg")
            self.assertEqual(
                quiet_main(VALIDATE, [str(output), "--manifest", str(report), "--expect-source-kind", "svg", "--expect-pixel-size", "4"]),
                0,
            )

    def test_preserve_mode_keeps_more_than_64_exact_source_colors(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "many-colors.png"
            image = Image.new("RGB", (73, 49))
            pixels = image.load()
            for y in range(image.height):
                for x in range(image.width):
                    pixels[x, y] = ((x * 37 + y * 11) % 256, (x * 13 + y * 29) % 256, (x * 7 + y * 43) % 256)
            image.save(source)
            for suffix in ("png", "webp"):
                output, report = root / f"preserved.{suffix}", root / f"preserved-{suffix}.json"
                self.assertEqual(
                    quiet_main(
                        RENDER,
                        [str(source), "-o", str(output), "--width", "160", "--height", "96",
                         "--pixel-size", "4", "--palette", "preserve", "--json-report", str(report)],
                    ),
                    0,
                )
                manifest = json.loads(report.read_text(encoding="utf-8"))
                self.assertIsNone(manifest["render"]["palette"])
                self.assertTrue(manifest["render"]["sourceColorsExact"])
                with Image.open(output) as converted:
                    self.assertGreater(len(converted.convert("RGB").getcolors(maxcolors=1000) or []), 64)
                self.assertEqual(
                    quiet_main(VALIDATE, [str(output), "--manifest", str(report), "--expect-palette-mode", "preserve"]),
                    0,
                )

    def test_preserve_mode_handles_alpha_and_svg(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            sprite, svg = root / "sprite.png", root / "scene.svg"
            make_sprite(sprite)
            make_svg(svg)
            for source in (sprite, svg):
                output, report = root / f"{source.stem}-exact.png", root / f"{source.stem}-exact.json"
                self.assertEqual(
                    quiet_main(RENDER, [str(source), "-o", str(output), "--width", "160", "--height", "96",
                                        "--pixel-size", "4", "--palette", "preserve", "--json-report", str(report)]),
                    0,
                )
                self.assertEqual(
                    quiet_main(VALIDATE, [str(output), "--manifest", str(report), "--expect-palette-mode", "preserve"]),
                    0,
                )

    def test_preserve_mode_rejects_color_changes_and_lossy_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            source = Path(temporary) / "source.png"
            make_sprite(source)
            for extra in (
                ["--contrast", "1.1"], ["--saturation", "1.1"], ["--dither", "bayer4"],
                ["--alpha", "flatten"], ["--colors", "64"],
            ):
                with self.subTest(extra=extra), contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
                    RENDER.parse_args([str(source), "-o", str(Path(temporary) / "out.png"), "--palette", "preserve", *extra])
            for suffix in ("gif", "mp4"):
                with self.subTest(suffix=suffix), contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
                    RENDER.parse_args([str(source), "-o", str(Path(temporary) / f"out.{suffix}"), "--palette", "preserve"])

    def test_preserve_validator_rejects_a_changed_rgb_even_with_updated_checksum(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source, output, report = root / "source.png", root / "pixel.png", root / "pixel.json"
            Image.new("RGB", (80, 48), (41, 93, 157)).save(source)
            self.assertEqual(
                quiet_main(RENDER, [str(source), "-o", str(output), "--width", "160", "--height", "96",
                                    "--pixel-size", "4", "--palette", "preserve", "--json-report", str(report)]),
                0,
            )
            with Image.open(output) as image:
                altered = image.copy()
            ImageDraw.Draw(altered).rectangle((0, 0, 3, 3), fill=(42, 93, 157))
            altered.save(output)
            manifest = json.loads(report.read_text(encoding="utf-8"))
            manifest["sha256"] = RENDER.sha256_file(output)
            report.write_text(json.dumps(manifest), encoding="utf-8")
            with self.assertRaisesRegex(SystemExit, "RGB values differing"):
                quiet_main(VALIDATE, [str(output), "--manifest", str(report), "--expect-palette-mode", "preserve"])

    def test_custom_palette_requires_multiple_distinct_colors(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            source = Path(temporary) / "source.png"
            make_sprite(source)
            with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
                RENDER.parse_args([str(source), "-o", str(Path(temporary) / "out.png"), "--palette", "custom", "--color", "#fff"])

    @unittest.skipUnless(shutil.which("ffmpeg") and shutil.which("ffprobe"), "ffmpeg and ffprobe are required")
    def test_mp4_preserves_audio_and_gif_has_exact_palette(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "source.mp4"
            make_video(source)
            mp4, mp4_report = root / "pixel.mp4", root / "pixel-mp4.json"
            gif, gif_report = root / "pixel.gif", root / "pixel-gif.json"
            contact = root / "contact.png"
            common = [str(source), "--width", "160", "--height", "96", "--pixel-size", "4", "--fps", "8", "--duration", "1"]
            self.assertEqual(
                quiet_main(RENDER, [*common, "-o", str(mp4), "--palette", "sunset8", "--json-report", str(mp4_report)]),
                0,
            )
            self.assertEqual(
                quiet_main(
                    VALIDATE,
                    [
                        str(mp4), "--manifest", str(mp4_report), "--expect-width", "160", "--expect-height", "96",
                        "--expect-fps", "8", "--expect-duration", "1", "--expect-audio", "keep",
                        "--min-frames", "8", "--min-distinct-frames", "2", "--max-colors", "8",
                    ],
                ),
                0,
            )
            self.assertEqual(
                quiet_main(
                    RENDER,
                    [
                        *common, "-o", str(gif), "--palette", "custom", "--color", "#1c1c1c",
                        "--color", "#9e1b32", "--color", "#f7f7f7", "--contact-sheet", str(contact),
                        "--json-report", str(gif_report),
                    ],
                ),
                0,
            )
            self.assertTrue(contact.is_file())
            self.assertEqual(
                quiet_main(
                    VALIDATE,
                    [
                        str(gif), "--manifest", str(gif_report), "--expect-fps", "8",
                        "--expect-duration", "1", "--expect-loop", "0", "--expect-audio", "drop",
                        "--min-frames", "8", "--min-distinct-frames", "2", "--max-colors", "3",
                    ],
                ),
                0,
            )

    @unittest.skipUnless(shutil.which("ffmpeg") and shutil.which("ffprobe"), "ffmpeg and ffprobe are required")
    def test_preserve_mode_mkv_round_trips_exact_video_rgb_and_audio(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source, output, report = root / "source.mp4", root / "preserved.mkv", root / "preserved.json"
            make_video(source)
            self.assertEqual(
                quiet_main(RENDER, [str(source), "-o", str(output), "--width", "160", "--height", "96",
                                    "--pixel-size", "4", "--fps", "8", "--duration", "1",
                                    "--palette", "preserve", "--json-report", str(report)]),
                0,
            )
            self.assertEqual(
                quiet_main(VALIDATE, [str(output), "--manifest", str(report), "--expect-palette-mode", "preserve",
                                      "--expect-fps", "8", "--expect-audio", "keep", "--min-frames", "8"]),
                0,
            )


if __name__ == "__main__":
    unittest.main(verbosity=2)
