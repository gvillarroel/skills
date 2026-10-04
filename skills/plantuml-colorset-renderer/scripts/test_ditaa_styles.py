#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["pillow>=11.0"]
# ///
"""Source and raster contract regressions for standalone Ditaa styling."""
from pathlib import Path
import tempfile
import unittest
from PIL import Image, ImageDraw
from ditaa_styles import prepare_ditaa_source, finish_ditaa_png
from palette_paints import COLORSETS, rgb, solid_colors

SOURCE = "@startditaa\n+-----------+\n| Request   |\n| {io}      |\n+-----------+\n@endditaa\n"


class DitaaStyleTests(unittest.TestCase):
    def test_seed_tags_only_replace_free_spaces(self):
        prepared, plan = prepare_ditaa_source(SOURCE)
        self.assertIn("@startditaa -S", prepared)
        self.assertIn("Request", prepared)
        self.assertIn("{io}", prepared)
        self.assertEqual([len(line) for line in prepared.splitlines()[1:-1]], [13] * 4)
        self.assertEqual(plan["boxes"][0]["fill"], "#9e1b32")
        self.assertEqual(plan["boxes"][0]["text"], "#ffffff")
        self.assertEqual(SOURCE.count("-S"), 0)

    def test_six_digit_tags_fail_before_rendering(self):
        with self.assertRaisesRegex(ValueError, "six-digit"):
            prepare_ditaa_source(SOURCE.replace("{io}      ", "c9E1B32    "))

    def test_small_box_without_free_tag_space_fails(self):
        with self.assertRaisesRegex(ValueError, "four free"):
            prepare_ditaa_source("@startditaa\n+---+\n| A |\n+---+\n@endditaa\n")

    def test_nested_or_shared_boxes_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "nested"):
            prepare_ditaa_source("@startditaa\n+-------------+\n| +-------+   |\n| | Node  |   |\n| +-------+   |\n+-------------+\n@endditaa\n")

    def test_supported_box_does_not_hide_an_unsupported_second_box(self):
        source = SOURCE.replace("@endditaa", "\n+...........+\n| Other     |\n|           |\n+...........+\n@endditaa")
        with self.assertRaisesRegex(ValueError, "unsupported or unclosed"):
            prepare_ditaa_source(source)

    def test_existing_supported_tag_is_retained(self):
        prepared, plan = prepare_ditaa_source(SOURCE.replace("{io}      ", "{io} c333 "))
        self.assertEqual(prepared.count("c333"), 1)
        self.assertTrue(plan["boxes"][0]["explicitColor"])
        self.assertEqual(plan["boxes"][0]["fill"], "#363636")

    def test_lowercase_hex_tag_is_normalized_without_moving_markup(self):
        prepared, plan = prepare_ditaa_source(SOURCE.replace("{io}      ", "{io} cabc "))
        self.assertEqual(prepared.count("cABC"), 1)
        self.assertNotIn("cabc", prepared)
        self.assertEqual([len(line) for line in prepared.splitlines()[1:-1]], [13] * 4)
        self.assertTrue(plan["boxes"][0]["explicitColor"])
        self.assertEqual(plan["boxes"][0]["nativeColor"], "#aabbcc")

    def test_white_native_seed_still_gets_a_visible_solid_fill(self):
        _, plan = prepare_ditaa_source(SOURCE.replace("{io}      ", "{io} cfff "))
        self.assertEqual(plan["boxes"][0]["nativeColor"], "#ffffff")
        self.assertEqual(plan["boxes"][0]["fill"], "#9e1b32")

    def test_auto_fill_exhaustion_fails_before_duplicate_styles(self):
        boxes = []
        for index in range(len(solid_colors("colorset1")) + 1):
            boxes.extend(["+-----------+", "| Node %02d   |" % index, "|           |", "+-----------+", ""])
        with self.assertRaisesRegex(ValueError, "exhausted the unique solid fills"):
            prepare_ditaa_source("@startditaa\n" + "\n".join(boxes) + "\n@endditaa\n")

    def test_raster_contour_is_removed_and_internal_strokes_survive(self):
        _, plan = prepare_ditaa_source(SOURCE)
        box = plan["boxes"][0]
        image = Image.new("RGB", (170, 112), "white")
        draw = ImageDraw.Draw(image)
        draw.rectangle((25, 35, 145, 77), fill=rgb(box["nativeColor"]), outline="black", width=2)
        draw.line((50, 48, 70, 48), fill="black", width=1)
        draw.line((145, 55, 165, 55), fill="black", width=1)
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "diagram.png"
            image.save(path)
            summary = finish_ditaa_png(path, plan)
            finished = Image.open(path).convert("RGB")
            self.assertGreater(summary["removedContourPixels"], 0)
            self.assertEqual(finished.getpixel((80, 35)), rgb(box["fill"]))
            self.assertEqual(finished.getpixel((60, 48)), rgb(box["text"]))
            self.assertEqual(finished.getpixel((160, 55)), (0, 0, 0))
            self.assertEqual(finished.getpixel((80, 60)), rgb(box["fill"]))
            actual = {"#" + "".join(f"{c:02x}" for c in color) for _, color in finished.getcolors(170 * 112)}
            self.assertFalse(actual - set(COLORSETS["colorset1"]["allowed"]))

    def test_internal_connector_gets_contrast_without_erasing_external_relation(self):
        source = "@startditaa\n+-----------+\n| API       |\n| {s}       |\n+-----+-----+\n      |\n      v\n@endditaa\n"
        _, plan = prepare_ditaa_source(source)
        box = plan["boxes"][0]
        image = Image.new("RGB", (170, 140), "white")
        draw = ImageDraw.Draw(image)
        draw.rectangle((25, 35, 145, 82), fill=rgb(box["nativeColor"]), outline="black", width=2)
        draw.line((85, 76, 85, 106), fill="black", width=1)
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "diagram.png"
            image.save(path)
            finish_ditaa_png(path, plan)
            with Image.open(path) as result:
                self.assertEqual(result.getpixel((85, 77)), rgb(box["text"]))
                self.assertEqual(result.getpixel((85, 96)), (0, 0, 0))

    def test_mismatched_native_dimensions_fail_without_rewriting(self):
        _, plan = prepare_ditaa_source(SOURCE)
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "diagram.png"
            Image.new("RGB", (20, 20), "white").save(path)
            before = path.read_bytes()
            with self.assertRaisesRegex(ValueError, "dimensions"):
                finish_ditaa_png(path, plan)
            self.assertEqual(path.read_bytes(), before)


if __name__ == "__main__":
    unittest.main()
