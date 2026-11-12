#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Check native export bytes, uniqueness and project boundaries with no model."""

from __future__ import annotations

import hashlib
import importlib.util
import os
from pathlib import Path
import struct
import tempfile
import unittest
import zlib

MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "save_image.py"
SPEC = importlib.util.spec_from_file_location("xy_native_save", MODULE_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def tiny_png(width=1, height=1):
    def chunk(name, data):
        return struct.pack(">I", len(data)) + name + data + struct.pack(">I", zlib.crc32(name + data))
    header = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    return b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", header) + chunk(b"IDAT", zlib.compress(b"\x00\xb2\x18\x2b")) + chunk(b"IEND", b"")


class SaveImageTests(unittest.TestCase):
    def setUp(self):
        configured = os.environ.get("XY_TEST_OUTPUT_DIR")
        if not configured:
            raise RuntimeError("Set XY_TEST_OUTPUT_DIR to a disposable artifact directory inside the workspace.")
        base = Path(configured).resolve()
        base.mkdir(parents=True, exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(prefix="save-image-", dir=base)
        self.root = Path(self.temp.name).resolve()
        if not self.root.is_relative_to(base):
            raise RuntimeError("The resolved test directory escaped the requested artifact root.")
        self.addCleanup(self.temp.cleanup)
        self.project = self.root / "project"
        self.source = self.project / ".xy-charts" / "render-1"
        self.source.mkdir(parents=True)
        self.content = tiny_png()
        (self.source / "chart.png").write_bytes(self.content)

    def save(self, title="Measured result"):
        return MODULE.save_image(self.project, self.source, title)

    def test_exact_native_bytes_and_source_are_preserved(self):
        result = self.save()
        target = Path(result["path"])
        self.assertEqual(target.read_bytes(), self.content)
        self.assertEqual((self.source / "chart.png").read_bytes(), self.content)
        self.assertEqual(result["sha256"], hashlib.sha256(self.content).hexdigest())
        self.assertEqual(result["bytes"], len(self.content))
        self.assertEqual(target.parent, self.project / ".xy-charts" / "exports")

    def test_repeat_saves_never_replace_an_existing_export(self):
        first = self.save()
        second = self.save()
        self.assertNotEqual(first["path"], second["path"])
        self.assertEqual(Path(first["path"]).read_bytes(), self.content)
        self.assertEqual(Path(second["path"]).read_bytes(), self.content)

    def test_title_is_a_bounded_filename_not_a_path_or_command(self):
        result = self.save("../../Revenue; $(touch forbidden) `literal` 🚀" * 10)
        self.assertRegex(result["name"], r"^[a-z0-9-]+-[a-f0-9]{12}\.png$")
        self.assertLessEqual(len(result["name"]), 65)
        self.assertTrue(Path(result["path"]).is_relative_to(self.project))
        self.assertFalse((self.project / "forbidden").exists())

    def test_outside_source_is_rejected_without_creating_exports(self):
        outside = self.root / "outside"
        outside.mkdir()
        (outside / "chart.png").write_bytes(self.content)
        with self.assertRaisesRegex(ValueError, "this project's chart directory"):
            MODULE.save_image(self.project, outside, "Outside")
        self.assertFalse((self.project / ".xy-charts" / "exports").exists())

    def test_invalid_png_does_not_create_an_export(self):
        (self.source / "chart.png").write_bytes(b"Not a PNG" * 5)
        with self.assertRaisesRegex(ValueError, "not a PNG"):
            self.save()
        self.assertFalse((self.project / ".xy-charts" / "exports").exists())

    def test_oversized_dimensions_are_rejected(self):
        (self.source / "chart.png").write_bytes(tiny_png(width=9000))
        with self.assertRaisesRegex(ValueError, "dimensions"):
            self.save()

    def test_existing_export_file_is_not_replaced_by_a_directory(self):
        exports = self.project / ".xy-charts" / "exports"
        exports.write_text("Keep this authored file", encoding="utf-8")
        with self.assertRaises(OSError):
            self.save()
        self.assertEqual(exports.read_text(encoding="utf-8"), "Keep this authored file")

    def test_symlink_export_cannot_redirect_writes_outside_the_project(self):
        outside = self.root / "outside"
        outside.mkdir()
        exports = self.project / ".xy-charts" / "exports"
        try:
            exports.symlink_to(outside, target_is_directory=True)
        except OSError as error:
            self.skipTest(f"This environment cannot create symlinks: {error}")
        with self.assertRaisesRegex(ValueError, "symlink or junction"):
            self.save()
        self.assertEqual(list(outside.iterdir()), [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
