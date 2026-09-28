#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Deterministic identity, retrieval and download failure tests. No network."""

import argparse
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import destockd as d


def raw(film="Film A", shot="shot_001", color="bw"):
    return {"film": film, "shot": shot, "color_type": color,
            "keyframe": "/keyframes/a.jpg", "preview": "https://clips.destockd.com/a_preview.mp4",
            "clip": "https://clips.destockd.com/a.mp4", "score": 0.31}


class Response(io.BytesIO):
    def __init__(self, content, mime="video/mp4", length=None):
        super().__init__(content)
        self.headers = {"Content-Type": mime, "Content-Length": str(len(content) if length is None else length)}
        self.url = "https://clips.destockd.com/actual.mp4"
        self.status = 200


class DownloadClient:
    def __init__(self, content, **kwargs):
        self.content, self.kwargs, self.requested = content, kwargs, []

    def open(self, url, media=False):
        self.requested.append(url)
        return Response(self.content, **self.kwargs)


class Tests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.mp4 = b"\x00\x00\x00\x18ftypisom" + b"\x00" * 96

    def selection(self, **kwargs):
        return argparse.Namespace(url=None, manifest=None, id=None, option=None, **kwargs)

    def manifest(self):
        first, second = d.normalize(raw()), d.normalize(raw("Second # Film / unicode \u03a9", "shot_009"))
        path = self.root / "options.json"
        d.write_json(path, {"schema_version": 1, "results": [{**second, "option": 2}, {**first, "option": 1}]})
        return path, first, second

    def test_selection_uses_saved_number_not_array_position(self):
        path, _, second = self.manifest()
        args = self.selection()
        args.manifest, args.option = path, 2
        self.assertEqual(d.resolve_selection(args), (second["film"], second["shot"]))

    def test_id_selection_and_unicode_url_roundtrip(self):
        path, _, second = self.manifest()
        args = self.selection()
        args.manifest, args.id = path, second["id"]
        self.assertEqual(d.resolve_selection(args), (second["film"], second["shot"]))
        args.manifest, args.id, args.url = None, None, second["page_url"]
        self.assertEqual(d.resolve_selection(args), (second["film"], second["shot"]))

    def test_ambiguous_selection_rejected(self):
        path, first, _ = self.manifest()
        args = self.selection()
        args.manifest, args.id, args.option = path, first["id"], 1
        with self.assertRaises(d.DestockdError):
            d.resolve_selection(args)

    def test_stale_option_is_not_substituted(self):
        path, _, _ = self.manifest()
        args = self.selection()
        args.manifest, args.option = path, 3
        with self.assertRaises(d.DestockdError):
            d.resolve_selection(args)

    def test_tampered_identity_rejected(self):
        path, _, _ = self.manifest()
        data = json.loads(path.read_text())
        data["results"][0]["film"] = "Different film"
        d.write_json(path, data)
        args = self.selection()
        args.manifest, args.option = path, 2
        with self.assertRaises(d.DestockdError):
            d.resolve_selection(args)

    def test_refresh_rejects_other_shot(self):
        class Client:
            def get(self, path):
                return raw(shot="shot_002")
        with self.assertRaises(d.DestockdError):
            d.refresh(Client(), "Film A", "shot_001")

    def test_source_origins(self):
        for url in ("http://destockd.com/x", "https://destockd.com.evil.test/x", "https://localhost/x",
                    "https://user:password@destockd.com/x", "https://destockd.com:444/x", "file:///tmp/x"):
            with self.subTest(url=url), self.assertRaises(d.DestockdError):
                d.public_url(url, media=True)
        self.assertEqual(d.public_url("/keyframes/a.jpg"), d.BASE + "/keyframes/a.jpg")

    def test_search_deduplicates_and_filters_after_rank_fusion(self):
        class Client:
            def get(self, path, **params):
                values = [raw(), raw("Other", color="color"), raw()] if params["q"] == "first" else [raw("Other", color="color"), raw()]
                return {"results": values, "has_more": False, "total": len(values)}
        out = self.root / "search.json"
        args = d.parser().parse_args(["search", "--query", "first", "--query", "second", "--color", "bw", "--out", str(out)])
        d.discover(args, Client())
        result = json.loads(out.read_text())
        self.assertEqual(len(result["results"]), 1)
        self.assertEqual(result["results"][0]["film"], "Film A")
        self.assertEqual(len(result["results"][0]["query_matches"]), 2)
        self.assertEqual(result["retrieval"]["unique_candidates"], 2)
        self.assertFalse(result["results"][0]["visual_verified"])

    def test_pagination_stops_on_exhaustion(self):
        calls = []
        class Client:
            def get(self, path, **params):
                calls.append(params["page"])
                return {"results": [raw(shot=f"shot_00{params['page']}")], "has_more": params["page"] == 1}
        args = d.parser().parse_args(["search", "--query", "first", "--pages", "3", "--out", str(self.root / "x.json")])
        result = d.discover(args, Client())
        self.assertEqual(calls, [1, 2])
        self.assertEqual(len(result["results"]), 2)

    def test_empty_filtered_window_preserves_scope(self):
        class Client:
            def get(self, path, **params):
                return {"results": [raw()], "has_more": True}
        args = d.parser().parse_args(["search", "--query", "first", "--color", "color", "--out", str(self.root / "x.json")])
        result = d.discover(args, Client())
        self.assertEqual(result["results"], [])
        self.assertTrue(result["retrieval"]["pages"][0]["has_more"])

    def test_gallery_escapes_titles_and_preserves_identity(self):
        row = {**d.normalize(raw('<script>alert("x")</script>')), "option": 1}
        out = self.root / "gallery.html"
        d.gallery({"results": [row], "retrieved_at": "today"}, out)
        text = out.read_text()
        self.assertNotIn("<script>", text)
        self.assertIn("&lt;script&gt;", text)
        self.assertIn(row["id"], text)
        self.assertIn('preload="none"', text)

    def test_success_downloads_clip_and_records_hash(self):
        client = DownloadClient(self.mp4)
        out = self.root / "chosen.mp4"
        with patch.object(d, "probe", return_value={"verification": "test_probe"}):
            receipt = d.download(client, d.normalize(raw()), out, 1)
        self.assertEqual(out.read_bytes(), self.mp4)
        self.assertEqual(client.requested, [raw()["clip"]])
        self.assertEqual(receipt["bytes"], len(self.mp4))
        self.assertEqual(receipt["sha256"], d.hashlib.sha256(self.mp4).hexdigest())
        self.assertTrue(Path(str(out) + ".json").is_file())
        self.assertEqual(len(list(self.root.iterdir())), 2)

    def test_existing_output_and_receipt_are_preserved(self):
        for name in ("chosen.mp4", "chosen.mp4.json"):
            with self.subTest(name=name):
                path = self.root / name
                path.write_bytes(b"original")
                with self.assertRaises(d.DestockdError):
                    d.download(DownloadClient(self.mp4), d.normalize(raw()), self.root / "chosen.mp4", 1)
                self.assertEqual(path.read_bytes(), b"original")
                path.unlink()

    def test_invalid_media_and_truncation_leave_no_partial_files(self):
        cases = [(b"<html>error</html>", {}), (self.mp4, {"mime": "text/html"}),
                 (self.mp4, {"length": len(self.mp4) + 1}), (self.mp4, {"length": 2 * 1024 * 1024})]
        for content, options in cases:
            with self.subTest(options=options), self.assertRaises(d.DestockdError):
                d.download(DownloadClient(content, **options), d.normalize(raw()), self.root / "chosen.mp4", 1)
            self.assertEqual(list(self.root.iterdir()), [])

    def test_failed_probe_leaves_no_output(self):
        with patch.object(d, "probe", side_effect=d.DestockdError("invalid media")):
            with self.assertRaises(d.DestockdError):
                d.download(DownloadClient(self.mp4), d.normalize(raw()), self.root / "chosen.mp4", 1)
        self.assertEqual(list(self.root.iterdir()), [])

    def test_preview_substitution_rejected(self):
        row = d.normalize(raw())
        row["clip"] = row["preview"]
        with self.assertRaises(d.DestockdError):
            d.download(DownloadClient(self.mp4), row, self.root / "chosen.mp4", 1)

    def test_missing_ffprobe_reports_limited_verification(self):
        with patch.object(d.shutil, "which", return_value=None):
            info = d.probe(self.root / "not-read.mp4")
        self.assertEqual(info["verification"], "mp4_signature_and_transfer_only")
        self.assertIsNone(info["duration_seconds"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
