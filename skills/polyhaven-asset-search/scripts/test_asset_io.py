#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Offline contracts for selection, transfers, content and archive boundaries."""
import hashlib
import io
import json
import sys
import tempfile
import unittest
import zipfile
from argparse import Namespace
from pathlib import Path
from urllib.request import Request

sys.dont_write_bytecode = True
from asset_io import (Redirects, ResourceError, checked_url, download_one, fetch_file,
                      safe_member, save_results, selection, zip_inventory)

PNG = b"\x89PNG\r\n\x1a\n" + b"fixture-image-bytes"


class Response(io.BytesIO):
    def __init__(self, data, mime="image/png", length=None):
        super().__init__(data)
        self.url = "https://files.example/test.png"
        self.headers = {"Content-Type": mime, "Content-Length": str(len(data) if length is None else length)}


class FakeClient:
    def __init__(self, data=PNG, mime="image/png", length=None):
        self.data, self.mime, self.length = data, mime, length

    def open(self, url):
        return Response(self.data, self.mime, self.length)


class Contracts(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=Path.cwd())
        self.root = Path(self.temp.name)
        self.entry = {"url": "https://files.example/test.png", "extension": "png", "bytes": len(PNG), "md5": hashlib.md5(PNG).hexdigest()}

    def tearDown(self):
        self.temp.cleanup()

    def test_saved_position_is_identity_not_list_index(self):
        path = self.root / "options.json"
        save_results("X", [{"id": "a"}, {"id": "b"}], path)
        doc = json.loads(path.read_text()); doc["results"].reverse(); path.write_text(json.dumps(doc))
        self.assertEqual(selection(Namespace(manifest=path, id=None, option=2), "X"), "b")

    def test_wrong_provider_and_ambiguous_selectors_fail(self):
        path = self.root / "options.json"
        save_results("X", [{"id": "a"}], path)
        for args, provider in [(Namespace(manifest=path, id=None, option=1), "Y"), (Namespace(manifest=path, id="a", option=1), "X"), (Namespace(manifest=None, id=None, option=None), "X")]:
            with self.assertRaises(ResourceError): selection(args, provider)

    def test_url_origins_and_userinfo_are_rejected(self):
        for url in ["http://files.example/a", "https://files.example.evil/a", "https://user@files.example/a", "https://files.example:444/a", "file:///tmp/a"]:
            with self.assertRaises(ResourceError): checked_url(url, {"files.example"})

    def test_credentials_never_cross_origin_redirect(self):
        req = Request("https://api.example/data", headers={"Authorization": "synthetic-secret"})
        with self.assertRaises(ResourceError): Redirects({"api.example", "files.example"}).redirect_request(req, None, 302, "", {}, "https://files.example/data")

    def test_correct_transfer_receipt_and_protection(self):
        target = self.root / "image.png"
        receipt = download_one(FakeClient(), "X", {"id": "a"}, "original", self.entry, target)
        self.assertEqual(target.read_bytes(), PNG)
        self.assertEqual(receipt["file"]["sha256"], hashlib.sha256(PNG).hexdigest())
        self.assertEqual(receipt["asset_id"], "a")
        with self.assertRaises(ResourceError): download_one(FakeClient(), "X", {"id": "a"}, "original", self.entry, target)
        self.assertEqual(target.read_bytes(), PNG)

    def test_bad_checksum_leaves_no_file_or_partial(self):
        with self.assertRaises(ResourceError): fetch_file(FakeClient(), self.entry | {"md5": "0" * 32}, self.root / "bad.png")
        self.assertEqual(list(self.root.iterdir()), [])

    def test_truncated_http_and_wrong_api_size_fail(self):
        for client, entry in [(FakeClient(length=999), self.entry), (FakeClient(), self.entry | {"bytes": 999})]:
            with self.assertRaises(ResourceError): fetch_file(client, entry, self.root / "bad.png")
        self.assertEqual(list(self.root.iterdir()), [])

    def test_limit_and_wrong_extension_fail(self):
        with self.assertRaises(ResourceError): fetch_file(FakeClient(), self.entry, self.root / "bad.png", 0.000001)
        with self.assertRaises(ResourceError): download_one(FakeClient(), "X", {"id": "a"}, "original", self.entry, self.root / "bad.jpg")

    def test_html_is_not_a_download(self):
        with self.assertRaises(ResourceError): fetch_file(FakeClient(b"<html>Denied</html>", "text/html"), {"url": "https://files.example/a", "extension": "png"}, self.root / "bad.png")
        self.assertEqual(list(self.root.iterdir()), [])

    def test_svg_external_code_is_rejected(self):
        for raw in [b'<svg xmlns="http://www.w3.org/2000/svg"><script>alert(1)</script></svg>', b'<svg xmlns="http://www.w3.org/2000/svg" onload="alert(1)"/>']:
            with self.assertRaises(ResourceError): fetch_file(FakeClient(raw, "image/svg+xml"), {"url": "https://files.example/a", "extension": "svg"}, self.root / "bad.svg")

    def test_traversal_and_windows_reserved_paths_fail(self):
        for name in ["../x", "/absolute", "a\\..\\x", "a:b", "CON.txt", "folder./x"]:
            with self.assertRaises(ResourceError): safe_member(name)

    def test_zip_collision_and_traversal_fail(self):
        for names in [["a.png", "A.png"], ["../outside.txt"]]:
            zpath = self.root / "sample.zip"
            with zipfile.ZipFile(zpath, "w") as z:
                for name in names: z.writestr(name, b"test")
            with self.assertRaises(ResourceError): zip_inventory(zpath)

    def test_gallery_escapes_untrusted_text(self):
        out = self.root / "data.json"; page = self.root / "options.html"
        save_results("X", [{"id": "a", "title": "<script>bad()</script>", "page_url": "https://example.com/"}], out, page)
        self.assertNotIn("<script>", page.read_text())
        self.assertIn('data-resource-id="a"', page.read_text())


if __name__ == "__main__":
    unittest.main()
