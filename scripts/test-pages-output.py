#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

"""Regression checks for the destructive boundary of generated Pages output."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch


spec = importlib.util.spec_from_file_location("build_pages", Path(__file__).with_name("build-pages.py"))
assert spec and spec.loader
build_pages = importlib.util.module_from_spec(spec)
spec.loader.exec_module(build_pages)


class PagesOutputTests(unittest.TestCase):
    def test_rebuild_preserves_authored_docs_and_unrelated_dist_files(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            guide = root / "docs" / "README.md"
            guide.parent.mkdir()
            guide.write_text("# Authored guide\n", encoding="utf-8")
            output = root / "dist" / "pages"
            output.mkdir(parents=True)
            (output / "old.html").write_text("old", encoding="utf-8")
            other = root / "dist" / "keep.txt"
            other.write_text("unrelated", encoding="utf-8")
            with patch.object(build_pages, "ROOT", root), patch.object(build_pages, "PAGES_ROOT", output):
                build_pages.reset_pages_output()
            self.assertEqual(guide.read_text(encoding="utf-8"), "# Authored guide\n")
            self.assertEqual(other.read_text(encoding="utf-8"), "unrelated")
            self.assertEqual(list(output.iterdir()), [])

    def test_cleanup_rejects_repository_docs_and_outside_paths(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            parent = Path(directory).resolve()
            root = parent / "repo"
            root.mkdir()
            for output in (root, root / "docs", parent / "outside"):
                with self.subTest(output=output):
                    output.mkdir(exist_ok=True)
                    marker = output / "keep.txt"
                    marker.write_text("keep", encoding="utf-8")
                    with patch.object(build_pages, "ROOT", root), patch.object(build_pages, "PAGES_ROOT", output):
                        with self.assertRaises(ValueError):
                            build_pages.reset_pages_output()
                    self.assertEqual(marker.read_text(encoding="utf-8"), "keep")

    def test_cleanup_rejects_symlink_to_another_directory(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            outside = root / "outside"
            outside.mkdir()
            marker = outside / "keep.txt"
            marker.write_text("keep", encoding="utf-8")
            output = root / "dist" / "pages"
            output.parent.mkdir()
            try:
                output.symlink_to(outside, target_is_directory=True)
            except OSError as error:
                self.skipTest(f"Directory symlinks unavailable: {error}")
            with patch.object(build_pages, "ROOT", root), patch.object(build_pages, "PAGES_ROOT", output):
                with self.assertRaises(ValueError):
                    build_pages.reset_pages_output()
            self.assertEqual(marker.read_text(encoding="utf-8"), "keep")


if __name__ == "__main__":
    unittest.main()
