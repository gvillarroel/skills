#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["Pillow>=11,<13", "playwright>=1.51,<2"]
# ///
"""Check portable asset geometry, source integrity, reuse and SVG rejection."""
import io
import base64
import json
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path
from unittest.mock import patch

from PIL import Image
import media_assets as media


class MediaTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="line-world-media-test-", dir=Path.cwd())
        self.root = Path(self.temp.name)
        self.source = b'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 100"><path fill="#76b900" d="M0 0H800V100H0Z"/></svg>'
        (self.root / "logo.svg").write_bytes(self.source)
        self.entry = {"id": "test-company", "kind": "logo", "label": "A & B", "sourceFile": "logo.svg",
                      "sourcePage": "https://example.org/brand", "identityEvidence": "Official test fixture",
                      "contributionEvidence": "Company behind the fixture product", "reviewed": True,
                      "rights": {"creator": "Fixture author", "license": "Test fixture", "credit": "Fixture author"}}

    def tearDown(self):
        self.temp.cleanup()

    def build(self, entry=None):
        request = self.root / "request.json"
        request.write_text(json.dumps({"assets": [entry or self.entry]}), encoding="utf-8")
        return media.build(request, self.root / "output")

    def test_vector_wordmark_remains_complete_and_proportional(self):
        self.build()
        svg = ET.parse(self.root / "output/test-company.circle.svg").getroot()
        nested = svg.find("{http://www.w3.org/2000/svg}svg")
        self.assertEqual(nested.get("viewBox"), "0 0 800 100")
        self.assertEqual(nested.get("preserveAspectRatio"), "xMidYMid meet")
        self.assertEqual(nested.find("{http://www.w3.org/2000/svg}path").get("d"), "M0 0H800V100H0Z")
        self.assertEqual((self.root / "output/originals/test-company.svg").read_bytes(), self.source)

    def test_cache_reuses_exact_source_but_invalidates_changes(self):
        self.build()
        self.assertEqual(self.build()["reused"], ["test-company"])
        (self.root / "logo.svg").write_bytes(self.source.replace(b"#76b900", b"#007298"))
        self.assertEqual(self.build()["reused"], [])

    def test_corrupted_output_is_rebuilt(self):
        self.build()
        (self.root / "output/test-company.circle.svg").write_text("broken", encoding="utf-8")
        self.assertEqual(self.build()["reused"], [])
        ET.parse(self.root / "output/test-company.circle.svg")

    def test_pinned_source_drift_is_rejected(self):
        entry = {**self.entry, "sourceSha256": "0" * 64}
        with self.assertRaisesRegex(ValueError, "Pinned source"):
            self.build(entry)

    def test_active_and_remote_svg_are_rejected(self):
        for child in ['<script>alert(1)</script>', '<image href="https://example.org/a.png"/>', '<path onclick="bad()"/>', '<path fill="url(https://example.org/paint)"/>', '<style>@import "https://example.org/a.css";</style>']:
            with self.subTest(child=child), self.assertRaises(ValueError):
                media.vector_source(('<svg viewBox="0 0 10 10">' + child + '</svg>').encode())
        media.vector_source(b'<svg viewBox="0 0 10 10"><path fill="url(\'#local\')"/></svg>')

    def test_portrait_is_explicitly_raster_and_has_local_graph_path(self):
        image = Image.new("RGB", (200, 400), "red"); stream = io.BytesIO(); image.save(stream, format="PNG")
        (self.root / "face.png").write_bytes(stream.getvalue())
        self.build({**self.entry, "kind": "portrait", "sourceFile": "face.png", "focus": [.5, .25]})
        manifest = json.loads((self.root / "output/manifest.json").read_text(encoding="utf-8"))
        self.assertFalse(manifest["assets"][0]["vectorArtwork"])
        node = json.loads((self.root / "output/graph-nodes.json").read_text(encoding="utf-8"))["nodes"][0]
        self.assertTrue((self.root / "output" / node["image"]).is_file())
        svg = (self.root / "output" / node["image"]).read_text(encoding="utf-8")
        self.assertIn("data:image/png;base64,", svg)
        self.assertIn('clip-path="url(#portrait)"', svg)

    def test_unreviewed_identity_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "reviewed"):
            self.build({**self.entry, "reviewed": False})

    def test_nested_vector_wrapper_is_accepted_but_raster_is_not(self):
        prefix = b'<svg viewBox="0 0 256 256"><image href="data:image/'
        media.vector_source(prefix + b'svg+xml;base64,' + base64.b64encode(self.source) + b'"/></svg>')
        with self.assertRaisesRegex(ValueError, "vector SVG"):
            media.vector_source(prefix + b'png;base64,abcd"/></svg>')

    def test_cached_download_needs_no_network(self):
        entry = dict(self.entry); entry.pop("sourceFile"); entry["downloadUrl"] = "https://example.org/brand.svg"
        with patch.object(media, "fetch", return_value=self.source) as download:
            self.build(entry); self.build(entry)
            self.assertEqual(download.call_count, 1)


if __name__ == "__main__":
    unittest.main()
