#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
import io
import json
import sys
import tempfile
import time
import unittest
from pathlib import Path

sys.dont_write_bytecode = True
import polyhaven as p
from asset_io import ResourceError


class FakeClient:
    def __init__(self, files): self.files = files
    def open(self, url):
        raw = self.files[url]
        if isinstance(raw, Exception): raise raw
        r = io.BytesIO(raw); r.url = url; r.headers = {"Content-Length": str(len(raw))}
        return r


class PolyHavenTests(unittest.TestCase):
    def test_gallery_keeps_curated_numbers_and_utf8_source_urls(self):
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as tmp:
            root = Path(tmp)
            manifest = root / "options.json"
            manifest.write_text(json.dumps({"schema_version": 1, "provider": "Poly Haven", "results": [
                {"option": 4, "id": "wood", "title": "Wood \u2014 aged", "page_url": "https://polyhaven.com/a/wood",
                 "thumbnail": "https://cdn.polyhaven.com/asset_img/thumbs/wood.png"}]}), encoding="utf-8")
            output = root / "options.html"
            p.run(p.parser().parse_args(["gallery", "--manifest", str(manifest), "--html", str(output)]))
            text = output.read_text(encoding="utf-8")
            self.assertIn("Option 4", text)
            self.assertIn("Wood \u2014 aged", text)
            self.assertIn('src="https://cdn.polyhaven.com/', text)

    def test_previews_stay_in_requested_directory_and_keep_option_ids(self):
        url = "https://cdn.polyhaven.com/asset_img/thumbs/wood.png"
        class Client(FakeClient):
            def data(self, *args, **kwargs):
                return {"name": "Wood", "type": 1, "thumbnail_url": url}
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as tmp:
            root = Path(tmp); manifest = root / "options.json"
            manifest.write_text(json.dumps({"schema_version": 1, "provider": "Poly Haven", "results": [{"option": 2, "id": "wood"}]}))
            output = root / "previews"
            result = p.previews(Client({url: b"\x89PNG\r\n\x1a\nfixture"}), manifest, output)
            self.assertEqual(result["previews"][0]["option"], 2)
            self.assertEqual(Path(result["previews"][0]["path"]), output / "2-wood.png")
            self.assertTrue((output / "previews.json").exists())

    def test_variant_paths_do_not_flatten_dependencies_as_independent_maps(self):
        data = {"gltf": {"1k": {"gltf": {"url": "https://dl.polyhaven.org/model.gltf", "include": {"textures/color.png": {"url": "https://dl.polyhaven.org/color.png"}}}}}}
        rows = p.variants(data)
        self.assertEqual([r["key"] for r in rows], ["gltf/1k/gltf"])
        self.assertIn("textures/color.png", rows[0]["include"])

    def test_unreleased_asset_is_rejected(self):
        with self.assertRaises(ResourceError): p.normalize("future_asset", {"date_published": time.time() + 3600})

    def test_complete_model_bundle_preserves_relative_dependencies(self):
        urls = ["https://dl.polyhaven.org/model.gltf", "https://dl.polyhaven.org/color.png"]
        data = [b'{"asset":{"version":"2.0"},"images":[{"uri":"textures/color.png"}]}', b"\x89PNG\r\n\x1a\nfixture"]
        entry = {"key": "gltf/1k/gltf", "url": urls[0], "extension": "gltf", "bytes": len(data[0]), "include": {"textures/color.png": {"url": urls[1], "size": len(data[1])}}}
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as tmp:
            target = Path(tmp) / "model"
            receipt = p.bundle(FakeClient(dict(zip(urls, data))), {"id": "model", "variants": [entry]}, [entry["key"]], target, 1)
            self.assertEqual((target / "textures/color.png").read_bytes(), data[1])
            self.assertEqual(len(receipt["files"]), 2)
            self.assertTrue((target / "receipt.json").exists())

    def test_failed_dependency_leaves_no_partial_bundle(self):
        url = "https://dl.polyhaven.org/model.gltf"
        entry = {"key": "gltf", "url": url, "extension": "gltf", "include": {"../outside.png": {"url": "https://dl.polyhaven.org/a.png"}}}
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as tmp:
            with self.assertRaises(ResourceError): p.bundle(FakeClient({url: b'{}'}), {"id": "model", "variants": [entry]}, ["gltf"], Path(tmp) / "model", 1)
            self.assertEqual(list(Path(tmp).iterdir()), [])

    def test_bundle_cap_covers_all_files(self):
        entry = {"key": "image", "url": "https://dl.polyhaven.org/a.png", "bytes": 100, "include": {"b.png": {"url": "https://dl.polyhaven.org/b.png", "size": 100}}}
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as tmp:
            with self.assertRaises(ResourceError): p.bundle(FakeClient({}), {"id": "a", "variants": [entry]}, ["image"], Path(tmp) / "out", 0.00015)


if __name__ == "__main__": unittest.main()
