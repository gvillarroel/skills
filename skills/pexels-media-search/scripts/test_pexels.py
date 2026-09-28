#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
import io
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.dont_write_bytecode = True
import pexels as p
from asset_io import ResourceError

PHOTO = {"id": 2014422, "width": 3024, "height": 3024, "url": "https://www.pexels.com/photo/2014422/", "photographer": "Fixture Author",
         "src": {"original": "https://images.pexels.com/photos/2014422/original.jpeg", "medium": "https://images.pexels.com/photos/2014422/preview.jpeg"}}
VIDEO = {"id": 2499611, "url": "https://www.pexels.com/video/2499611/", "duration": 22,
         "video_files": [{"id": 125004, "width": 1080, "height": 1920, "file_type": "video/mp4", "link": "https://videos.pexels.com/a.mp4"}]}


class PexelsTests(unittest.TestCase):
    def test_missing_key_is_an_actionable_status_without_secret(self):
        with patch.dict(os.environ, {}, clear=True):
            result = p.run(p.parser().parse_args(["status"]))
            self.assertFalse(result["api_key_configured"])
            with self.assertRaises(ResourceError): p.credentials()

    def test_status_never_serializes_a_configured_key(self):
        with patch.dict(os.environ, {"PEXELS_API_KEY": "synthetic-secret"}):
            result = p.run(p.parser().parse_args(["status"]))
            self.assertTrue(result["api_key_configured"])
            self.assertNotIn("synthetic-secret", json.dumps(result))

    def test_same_numeric_photo_and_video_are_distinct(self):
        photo = p.normalize(PHOTO, "photo")
        video = p.normalize(VIDEO | {"id": PHOTO["id"]}, "video")
        self.assertNotEqual(photo["id"], video["id"])

    def test_original_download_and_authentication_boundary(self):
        class Client:
            def __init__(self): self.requests = []
            def data(self, url, params=None, headers=None):
                self.requests.append((url, headers)); return PHOTO
            def open(self, url):
                self.requests.append((url, None))
                raw = b"\xff\xd8\xffimage"; r = io.BytesIO(raw); r.url = url; r.headers = {"Content-Length": str(len(raw))}; return r
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as tmp, patch.dict(os.environ, {"PEXELS_API_KEY": "synthetic-secret"}):
            client = Client(); out = Path(tmp) / "chosen.jpeg"
            receipt = p.run(p.parser().parse_args(["download", "--id", "photo:2014422", "--output", str(out)]), client)
            self.assertEqual(client.requests[0][1], {"Authorization": "synthetic-secret"})
            self.assertEqual(client.requests[1], (PHOTO["src"]["original"], None))
            self.assertNotIn("synthetic-secret", json.dumps(receipt))

    def test_video_requires_explicit_rendition_and_uses_documented_route(self):
        class Client:
            def data(self, url, params=None, headers=None):
                self.url = url; return VIDEO
        with patch.dict(os.environ, {"PEXELS_API_KEY": "synthetic-secret"}):
            client = Client()
            with self.assertRaises(ResourceError): p.run(p.parser().parse_args(["download", "--id", "video:2499611", "--output", "unused.mp4"]), client)
            self.assertTrue(client.url.endswith("/v1/videos/videos/2499611"))

    def test_returned_asset_id_must_match_selection(self):
        class Client:
            def data(self, *args, **kwargs): return PHOTO
        with self.assertRaises(ResourceError): p.inspect(Client(), "photo:999", {"Authorization": "fixture"})


if __name__ == "__main__": unittest.main()
