#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

"""Regression checks for safe Pages cleanup and native HTML metadata."""

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

    def test_body_metadata_ignores_script_and_comment_literals(self) -> None:
        prefix = (
            "<!doctype html>\r\n<html><head>\r\n"
            "<title>Unicode Ω 😀\u2028 text</title>\r\n"
            "<script>const markup = '<body data-example-id=\"script\">';</script>\r\n"
            "<!-- <body data-example-id=\"comment\"> -->\r\n"
            "</head>\r\n"
        )
        body = '<BODY title=\'literal data-example-id="text" > value\'\r\n class="deck">'
        suffix = "<main>Slide content</main></BODY></html>"
        source = prefix + body + suffix
        result = build_pages.ensure_body_attribute(source, "data-example-id", "slidev-echarts")
        expected_body = body[:-1] + ' data-example-id="slidev-echarts">'
        self.assertEqual(result, prefix + expected_body + suffix)

    def test_body_metadata_preserves_existing_case_and_spacing(self) -> None:
        source = '<body DATA-EXAMPLE-ID = \'existing\' title="a > b">Content</body>'
        self.assertEqual(
            build_pages.ensure_body_attribute(source, "data-example-id", "replacement"),
            source,
        )

    def test_body_metadata_updates_only_first_real_body_and_is_idempotent(self) -> None:
        source = '<body id="first">First</body>\n<body id="duplicate">Second</body>'
        expected = (
            '<body id="first" data-example-id="slidev-echarts">First</body>\n'
            '<body id="duplicate">Second</body>'
        )
        result = build_pages.ensure_body_attribute(source, "data-example-id", "slidev-echarts")
        self.assertEqual(result, expected)
        self.assertEqual(
            build_pages.ensure_body_attribute(result, "data-example-id", "slidev-echarts"),
            expected,
        )

    def test_body_metadata_does_not_modify_markup_without_a_real_body(self) -> None:
        source = '<head><script>const text = "<body>";</script><!-- <body> --></head>'
        self.assertEqual(
            build_pages.ensure_body_attribute(source, "data-example-id", "slidev-echarts"),
            source,
        )

    def test_body_metadata_escapes_inserted_attribute_value(self) -> None:
        self.assertEqual(
            build_pages.ensure_body_attribute("<body/>", "data-example-id", 'a" & b'),
            '<body data-example-id="a&quot; &amp; b"/>',
        )


    def test_head_metadata_ignores_script_and_comment_literals(self) -> None:
        prefix = (
            '<html><head>\n<script>const page = `<meta name="pattern-id" '
            'content="script"></head><body>`;</script>\n'
            '<!-- <meta name="example-id" content="comment"></head> -->\n'
        )
        suffix = '</HEAD><body>Real content</body></html>'
        metadata = (
            '  <meta name="example-id" content="slidev-echarts">\n'
            '  <meta name="pattern-id" content="slidev-echarts">\n'
            '  <meta name="pattern-page" content="true">\n'
        )
        result = build_pages.ensure_html_head_meta(prefix + suffix, "slidev-echarts")
        self.assertEqual(result, prefix + metadata + suffix)
        self.assertEqual(build_pages.ensure_html_head_meta(result, "slidev-echarts"), result)

    def test_head_metadata_fills_only_missing_native_tags(self) -> None:
        source = '<head><META NAME=\'pattern-id\' CONTENT=\'kept\'></head><body></body>'
        expected = (
            '<head><META NAME=\'pattern-id\' CONTENT=\'kept\'>'
            '  <meta name="example-id" content="slidev-echarts">\n'
            '  <meta name="pattern-page" content="true">\n'
            '</head><body></body>'
        )
        self.assertEqual(build_pages.ensure_html_head_meta(source, "slidev-echarts"), expected)

    def test_favicon_ignores_script_literals_and_preserves_native_icon(self) -> None:
        prefix = '<head><script>const icon = `<link rel="icon"></head>`;</script>'
        suffix = '</head><body></body>'
        inserted = '  <link rel="icon" href="../../favicon.ico">\n'
        result = build_pages.ensure_html_favicon(prefix + suffix)
        self.assertEqual(result, prefix + inserted + suffix)
        self.assertEqual(build_pages.ensure_html_favicon(result), result)

    def test_head_helpers_preserve_markup_without_a_real_head(self) -> None:
        source = '<script>const page = "<head></head>";</script><body></body>'
        self.assertEqual(build_pages.ensure_html_head_meta(source, "slidev-echarts"), source)
        self.assertEqual(build_pages.ensure_html_favicon(source), source)


    def test_normalization_preserves_structured_web_asset_bytes(self) -> None:
        script = (
            'const separators = "\u0085\u2028\u2029";\r\n'
            'const label = `keep trailing spaces   \r\nsecond line  `;  \r\n'
        )
        sources = {
            ".js": script,
            ".mjs": script,
            ".ts": script,
            ".html": "<head><script>" + script + "</script></head>\r\n<body>  </body>\r\n",
            ".svg": '<svg xmlns="http://www.w3.org/2000/svg"><script>' + script + "</script></svg>\r\n",
            ".vue": "<script setup>" + script + "</script>\r\n<template><div>  </div></template>\r\n",
            ".css": ':root { --label: "keep \u0085\u2028\u2029 spaces  "; }  \r\n',
        }
        with tempfile.TemporaryDirectory() as directory:
            for suffix, source in sources.items():
                with self.subTest(suffix=suffix):
                    path = Path(directory) / ("asset" + suffix)
                    original = source.encode("utf-8")
                    path.write_bytes(original)
                    build_pages.normalize_text_file(path)
                    self.assertEqual(path.read_bytes(), original)

    def test_normalization_still_cleans_prose_whitespace(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "guide.md"
            path.write_bytes(b"# Guide  \r\n\r\n")
            build_pages.normalize_text_file(path)
            self.assertEqual(path.read_bytes(), b"# Guide\n")


if __name__ == "__main__":
    unittest.main()
