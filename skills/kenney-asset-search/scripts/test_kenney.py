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
import zipfile
from pathlib import Path

sys.dont_write_bytecode = True
import kenney as k
from asset_io import ResourceError

PACK = '''<meta property="og:url" content="https://kenney.nl/assets/example"><h1>Example</h1>
<a href="https://creativecommons.org/publicdomain/zero/1.0/">CC0</a>
<a href="https://kenney.itch.io/kenney-game-assets">Paid bundle</a>
<a id="donate-text" href="https://kenney.nl/media/pages/assets/example/hash/pack.zip">Continue without donating</a>'''


class Client:
    def __init__(self, text): self.text = text
    def data(self, *args, **kwargs): return self.text


class KenneyTests(unittest.TestCase):
    def test_previews_keep_local_paths_and_saved_option_numbers(self):
        class ImageClient:
            def open(self, url, **kwargs):
                raw = b"\x89PNG\r\n\x1a\nfixture"
                response = io.BytesIO(raw)
                response.url = url
                response.headers = {"Content-Length": str(len(raw))}
                return response
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as tmp:
            root = Path(tmp)
            manifest = root / "options.json"
            manifest.write_text(json.dumps({"schema_version": 1, "provider": "Kenney", "results": [
                {"option": 3, "id": "example", "thumbnail": "https://kenney.nl/media/pages/assets/example/hash/preview.png"}]}))
            output = root / "previews"
            result = k.previews(ImageClient(), manifest, output)
            self.assertEqual(result["previews"][0]["option"], 3)
            self.assertEqual(Path(result["previews"][0]["path"]), output / "3-example.png")
            with self.assertRaises(ResourceError): k.previews(ImageClient(), manifest, output)

    def test_free_pack_link_ignores_paid_bundle(self):
        asset = k.inspect(Client(PACK), "example")
        self.assertEqual(asset["variants"][0]["url"], "https://kenney.nl/media/pages/assets/example/hash/pack.zip")

    def test_missing_free_link_or_wrong_pack_fails(self):
        for html in [PACK.replace('id="donate-text"', ''), PACK.replace('/assets/example/hash/', '/assets/other/hash/')]:
            with self.assertRaises(ResourceError): k.inspect(Client(html), "example")

    def test_search_deduplicates_actual_asset_links(self):
        text = '<a href="https://kenney.nl/assets/example"></a><h2><a href="https://kenney.nl/assets/example">Example</a></h2><a href="https://kenney.nl/assets/example">Again</a><a href="https://kenney.nl/assets/tag:space">Space</a>'
        self.assertEqual([r["id"] for r in k.search_rows(text)], ["example"])

    def test_extract_exact_member_and_keep_license(self):
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as tmp:
            root = Path(tmp); path = root / "pack.zip"
            with zipfile.ZipFile(path, "w") as z:
                z.writestr("Sprites/hero.png", b"hero"); z.writestr("Sprites/other.png", b"other"); z.writestr("License.txt", "CC0 fixture")
            result = k.extract_selected(path, ["Sprites/hero.png"], root / "chosen")
            self.assertEqual({f["path"] for f in result["files"]}, {"Sprites/hero.png", "License.txt"})
            self.assertFalse((root / "chosen/Sprites/other.png").exists())
            with self.assertRaises(ResourceError): k.extract_selected(path, ["Sprites/hero.png"], root / "chosen")

    def test_unknown_member_cannot_create_an_output(self):
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as tmp:
            path = Path(tmp) / "pack.zip"
            with zipfile.ZipFile(path, "w") as z: z.writestr("a.txt", "a")
            with self.assertRaises(ResourceError): k.extract_selected(path, ["missing.txt"], Path(tmp) / "chosen")
            self.assertFalse((Path(tmp) / "chosen").exists())


if __name__ == "__main__": unittest.main()
