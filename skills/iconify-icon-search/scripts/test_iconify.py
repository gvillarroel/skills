#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
import sys
import unittest
from urllib.parse import parse_qs, urlsplit

sys.dont_write_bytecode = True
import iconify as i
from asset_io import ResourceError


class IconifyTests(unittest.TestCase):
    def test_monochrome_export_rejects_off_palette_paint(self):
        for color in ("red", "#abcdef", "#ff000080"):
            with self.assertRaises(ResourceError):
                i.svg_entry("lucide:home", color, 24)
        self.assertIn("color=%239e1b32", i.svg_entry("lucide:home", "#9e1b32", 24)["url"])
        self.assertIn("currentColor", i.svg_entry("lucide:home", "currentColor", 24)["url"])
    def test_icon_alias_remains_selected_identity(self):
        class Client:
            def data(self, url, params):
                if url.endswith(".json"): return {"icons": {"house": {}}, "aliases": {"home": {"parent": "house"}}}
                return {"info": {"name": "Lucide", "license": {"title": "ISC"}}}
        asset = i.inspect(Client(), "lucide:home")
        self.assertEqual(asset["id"], "lucide:home")
        self.assertEqual(asset["license"]["title"], "ISC")

    def test_missing_icon_is_not_replaced(self):
        class Client:
            def data(self, url, params): return {"icons": {}, "not_found": ["missing"]}
        with self.assertRaises(ResourceError): i.inspect(Client(), "lucide:missing")

    def test_color_and_size_are_encoded_in_exact_svg_request(self):
        url = i.svg_entry("lucide:house", "#9e1b32", 32)["url"]
        self.assertEqual(urlsplit(url).path, "/lucide/house.svg")
        self.assertEqual(parse_qs(urlsplit(url).query), {"color": ["#9e1b32"], "height": ["32"]})

    def test_invalid_identity_and_color_fail(self):
        with self.assertRaises(ResourceError): i.split_id("../../x")
        with self.assertRaises(ResourceError): i.svg_entry("lucide:house", "red&script=1", 24)


if __name__ == "__main__": unittest.main()
