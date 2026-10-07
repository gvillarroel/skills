#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Check SVG detection, upload-copy fidelity, dependencies, and output boundaries."""

import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

sys.dont_write_bytecode = True
SCRIPT = Path(__file__).with_name("inspect_svg.py")
spec = importlib.util.spec_from_file_location("inspect_svg", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class SvgTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="lucid-svg-test-", dir=Path.cwd())
        self.root = Path(self.temp.name)
        self.source = self.root / "source.svg"

    def tearDown(self):
        self.temp.cleanup()

    def write(self, inner="", attrs='viewBox="-10 0 200 100"'):
        self.source.write_text(f'<svg xmlns="http://www.w3.org/2000/svg" {attrs}>{inner}</svg>', encoding="utf-8")

    def test_byte_preserving_copy_and_geometry(self):
        self.write('<rect id="a" width="30" height="20"/><text>Approval &amp; review</text>')
        output, report = self.root / "nested/upload.svg", self.root / "report.json"
        run = subprocess.run([sys.executable, str(SCRIPT), "prepare", str(self.source), "--output", str(output), "--report", str(report)], capture_output=True)
        self.assertEqual(run.returncode, 0, run.stderr)
        self.assertEqual(output.read_bytes(), self.source.read_bytes())
        result = json.loads(report.read_text(encoding="utf-8"))
        self.assertEqual(result["labels"], ["Approval & review"])
        self.assertEqual(result["view_box"], [-10, 0, 200, 100])
        self.assertEqual(result["vector_element_count"], 2)

    def test_unicode_labels_with_legacy_pipe_encoding(self):
        self.write('<text>Review → publish</text>')
        environment = dict(os.environ, PYTHONIOENCODING="cp1252")
        run = subprocess.run([sys.executable, str(SCRIPT), "inspect", str(self.source)], capture_output=True, env=environment)
        self.assertEqual(run.returncode, 0, run.stderr)
        self.assertEqual(json.loads(run.stdout)["labels"], ["Review → publish"])

    def test_html_is_not_svg(self):
        self.source.write_text("<html><body>Sign in</body></html>", encoding="utf-8")
        with self.assertRaises(module.SvgError):
            module.inspect(self.source)

    def test_invalid_viewbox(self):
        for value in ("0 0 nan 100", "0 0 -1 100", "0 0 100", ""):
            self.write(attrs=f'viewBox="{value}"')
            with self.assertRaises(module.SvgError):
                module.inspect(self.source)

    def test_dimensions_without_viewbox(self):
        self.write(attrs='width="1in" height="72pt"')
        _, result = module.inspect(self.source)
        self.assertEqual(result["width_px"], 96)
        self.assertEqual(result["height_px"], 96)
        self.assertTrue(result["ready_for_upload"])

    def test_external_resources_are_blocked(self):
        for content in ('<image href="https://example.com/x.png"/>', '<rect style="fill:url(../paint.svg#x)"/>', '<style>@import "https://example.com/font.css";</style>'):
            self.write(content)
            _, result = module.inspect(self.source)
            self.assertFalse(result["ready_for_upload"])

    def test_active_content_and_dynamic_links_are_blocked(self):
        for content in ('<script>alert(1)</script>', '<rect onclick="run()"/>', '<a href="javascript:run()"/>', '<animate attributeName="href" values="a;b"/>', '<style>.x{fill:u\\72l(remote)}</style>'):
            self.write(content)
            _, result = module.inspect(self.source)
            self.assertFalse(result["safe_to_render_offline"])

    def test_dtd_rejected_in_utf8_and_utf16(self):
        value = '<!DOCTYPE svg [<!ENTITY a "test">]><svg xmlns="http://www.w3.org/2000/svg"/>'
        for encoding in ("utf-8", "utf-16"):
            self.source.write_bytes(value.encode(encoding))
            with self.assertRaises(module.SvgError):
                module.inspect(self.source)

    def test_internal_fragment_and_raster_warning(self):
        self.write('<defs><path id="x" d="M0 0L1 1"/></defs><use href="#x"/><image href="data:image/png;base64,aGVsbG8="/>')
        _, result = module.inspect(self.source)
        self.assertTrue(result["ready_for_upload"])
        self.assertEqual(result["embedded_raster_resource_count"], 1)
        self.assertIn("embedded-raster-image", result["portability_warnings"])

    def test_nested_svg_data_requires_review(self):
        self.write('<image href="data:image/svg+xml;base64,aGVsbG8="/>')
        _, result = module.inspect(self.source)
        self.assertFalse(result["ready_for_upload"])

    def test_xml_stylesheet_instruction_needs_review(self):
        self.write()
        self.source.write_bytes(b'<?xml-stylesheet href="https://example.com/a.css"?>' + self.source.read_bytes())
        _, result = module.inspect(self.source)
        self.assertIn("external-stylesheet-instruction", result["blocking_flags"])

    def test_foreign_object_nested_content_requires_review(self):
        self.write('<foreignObject><iframe xmlns="http://www.w3.org/1999/xhtml" srcdoc="&lt;script&gt;run()&lt;/script&gt;"/><img xmlns="http://www.w3.org/1999/xhtml" srcset="https://example.com/a.png 2x"/></foreignObject>')
        _, result = module.inspect(self.source)
        self.assertFalse(result["safe_to_render_offline"])
        self.assertIn("foreignObject-needs-review", result["blocking_flags"])

    def test_unresolved_fragment_report(self):
        self.write('<use href="#missing"/>')
        _, result = module.inspect(self.source)
        self.assertEqual(result["unresolved_fragment_references"], ["missing"])

    def test_existing_output_is_preserved(self):
        self.write()
        output = self.root / "upload.svg"
        output.write_bytes(b"previous")
        run = subprocess.run([sys.executable, str(SCRIPT), "prepare", str(self.source), "--output", str(output)], capture_output=True)
        self.assertEqual(run.returncode, 2)
        self.assertEqual(output.read_bytes(), b"previous")

    def test_source_cannot_be_report(self):
        self.write()
        original = self.source.read_bytes()
        run = subprocess.run([sys.executable, str(SCRIPT), "inspect", str(self.source), "--report", str(self.source), "--overwrite"], capture_output=True)
        self.assertEqual(run.returncode, 2)
        self.assertEqual(self.source.read_bytes(), original)

    def test_rejected_prepare_leaves_diagnostic_but_no_copy(self):
        self.write('<script/>')
        output, report = self.root / "upload.svg", self.root / "report.json"
        run = subprocess.run([sys.executable, str(SCRIPT), "prepare", str(self.source), "--output", str(output), "--report", str(report)], capture_output=True)
        self.assertEqual(run.returncode, 2)
        self.assertFalse(output.exists())
        self.assertEqual(json.loads(report.read_text())["blocking_flags"], ["script"])


if __name__ == "__main__":
    unittest.main()
