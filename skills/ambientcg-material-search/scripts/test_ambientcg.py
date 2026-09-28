#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
import sys
import io
import json
import tempfile
import unittest
from pathlib import Path

sys.dont_write_bytecode = True
import ambientcg as a
from asset_io import ResourceError, entry_for


def fixture():
    return {"id": "Wood095", "title": "Wood", "url": "https://ambientcg.com/a/Wood095", "type": "material", "releaseDate": "2025-01-01",
            "downloads": [{"attributes": "1K-JPG", "extension": "zip", "url": "https://ambientcg.com/get?file=one.zip", "size": 500},
                          {"attributes": "4K-PNG", "extension": "zip", "url": "https://ambientcg.com/get?file=four.zip", "size": 2000}]}


class AmbientTests(unittest.TestCase):
    def test_previews_use_requested_directory_and_preserve_identity(self):
        url = "https://acg-media.struffelproductions.com/Wood095.png"
        class Client:
            def data(self, *args, **kwargs): return {"assets": [fixture() | {"thumbnails": {"512-PNG": url}}]}
            def open(self, url):
                raw = b"\x89PNG\r\n\x1a\nfixture"; r = io.BytesIO(raw); r.url = url; r.headers = {"Content-Length": str(len(raw))}; return r
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as tmp:
            root = Path(tmp); manifest = root / "options.json"
            manifest.write_text(json.dumps({"provider": "ambientCG", "schema_version": 1, "results": [{"option": 2, "id": "Wood095"}]}))
            result = a.previews(Client(), manifest, root / "previews")
            self.assertEqual(result["previews"][0]["id"], "Wood095")
            self.assertEqual(Path(result["previews"][0]["path"]).parent, root / "previews")

    def test_variants_bind_format_and_resolution(self):
        asset = a.normalize(fixture())
        chosen = entry_for(asset["variants"], "4K-PNG/zip")
        self.assertEqual(chosen["bytes"], 2000)
        self.assertTrue(chosen["url"].endswith("four.zip"))

    def test_missing_variant_does_not_fall_back(self):
        with self.assertRaises(ResourceError): entry_for(a.normalize(fixture())["variants"], "4K-JPG/zip")

    def test_future_release_is_not_free_public_download(self):
        with self.assertRaises(ResourceError): a.normalize(fixture() | {"releaseDate": "2999-01-01"})

    def test_exact_lookup_rejects_different_returned_id(self):
        class Client:
            def data(self, url, params): return {"assets": [fixture()]}
        with self.assertRaises(ResourceError): a.inspect(Client(), "Wood001")

    def test_unknown_dimensions_are_preserved_not_guessed(self):
        asset = a.normalize(fixture() | {"dimensions": {"width": 0, "height": 0}})
        self.assertEqual(asset["dimensions"]["width"], 0)
        self.assertEqual(asset["license"]["title"], "CC0")


if __name__ == "__main__": unittest.main()
