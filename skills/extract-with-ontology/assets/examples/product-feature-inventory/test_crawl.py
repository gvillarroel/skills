#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Checks for bounded, replayable GitHub Docs source discovery."""

from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

import crawl


REVISION = "a" * 40


class CrawlTests(unittest.TestCase):
    def setUp(self):
        temp = TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.out = self.root / "corpus"
        self.path = self.root / "spec.json"
        self.content = {
            "start": b"# Start\r\n[Section](/en/team/section/#part)\r\n[Leaf](./leaf.md)\r\n",
            "leaf": b"# Leaf\n[End](/team/end#part)\n",
            "section": b"\xef\xbb\xbf# Section\n[End](../end.md)\n",
            "end": b"# End\n[Start](https://docs.github.com/en/team/start)\n",
        }
        self.paths = {
            "start": "content/team/start.md",
            "leaf": "content/team/leaf.md",
            "section": "content/team/section/index.md",
            "end": "content/team/end.md",
        }
        self.spec = {
            "version": 1, "repository": "github/docs", "revision": REVISION,
            "max_depth": 2, "max_sources": 4, "max_source_bytes": 1024, "seeds": ["start"],
            "allowlist": [{"source_id": name, "source_path": self.paths[name],
                           "sha256": sha256(raw).hexdigest()} for name, raw in self.content.items()],
        }

    def loaded(self, spec=None):
        self.path.write_text(json.dumps(self.spec if spec is None else spec), encoding="utf-8")
        return crawl.load_spec(self.path)

    def mock_fetch(self, name, url, limit):
        self.assertEqual(url, f"https://raw.githubusercontent.com/github/docs/{REVISION}/{self.paths[name]}")
        self.assertEqual(limit, 1024)
        return self.content[name]

    def run_mock_crawl(self):
        loaded = self.loaded()
        with patch.object(crawl, "online_fetch", side_effect=self.mock_fetch):
            crawl.crawl(self.out, *loaded)
        return loaded

    def test_breadth_first_paths_and_pinned_provenance(self):
        raw, content = crawl.canonical_manifest(*self.loaded(), self.mock_fetch)
        manifest = json.loads(raw)
        rows = {row["source_id"]: row for row in manifest["sources"]}
        self.assertEqual(content, self.content)
        self.assertEqual([row["source_id"] for row in manifest["sources"]], sorted(self.content))
        self.assertEqual(rows["start"]["depth"], 0)
        self.assertIsNone(rows["start"]["discovered_from"])
        self.assertEqual(rows["leaf"]["depth"], 1)
        self.assertEqual(rows["section"]["depth"], 1)
        self.assertEqual(rows["end"]["depth"], 2)
        self.assertEqual(rows["end"]["discovered_from"], "leaf")
        self.assertEqual(rows["end"]["path"], "sources/end.md")
        self.assertEqual(rows["end"]["url"], f"https://github.com/github/docs/blob/{REVISION}/content/team/end.md")
        self.assertEqual(rows["section"]["bytes"], len(self.content["section"]))
        self.assertEqual(rows["start"]["sha256"], sha256(self.content["start"]).hexdigest())
        self.assertEqual(manifest["links"], [{"from": left, "to": right} for left, right in
            [("end", "start"), ("leaf", "end"), ("section", "end"), ("start", "leaf"), ("start", "section")]])

    def test_link_exclusions_and_supported_destinations(self):
        source = "\n".join([
            "[allowed](/en/team/end?unused=1#anchor)",
            '[angle](<end.md> "title")',
            "[inline code \x60example\x60](https://docs.github.com/en/team/end)",
            "![image](/team/end)",
            r"\[escaped](/team/end)",
            "\x60[inline](/team/end)\x60",
            "\x60\x60[double \x60 tick](/team/end)\x60\x60",
            "\x60\x60\x60md", "[backtick fence](/team/end)", "\x60\x60\x60",
            "~~~md", "[tilde fence](/team/end)", "~~~",
            "> \x60\x60\x60md", "> [quoted fence](/team/end)", "> \x60\x60\x60",
            "    [indented code](/team/end)",
            "<!-- [comment](/team/end) -->",
            "[foreign](https://docs.github.com.evil.test/team/end)",
            "[spoof](https://docs.github.com@evil.test/team/end)",
            "[downgrade](http://docs.github.com/team/end)",
            "[protocol](javascript:alert(1))",
            "[fragment](#team/end)",
            "[unknown](/team/outside-allowlist)",
            '[not closed](/team/end "title"',
        ])
        result = list(crawl.linked_sources(source, "/team/start", {"/team/end": "end"}))
        self.assertEqual(result, ["end", "end", "end"])

    def test_manifest_replay_has_no_network_or_writes(self):
        loaded = self.run_mock_crawl()
        files = sorted(path for path in self.out.rglob("*") if path.is_file())
        before = [(path, path.stat().st_mtime_ns, path.read_bytes()) for path in files]
        with patch.object(crawl, "online_fetch", side_effect=AssertionError("Unexpected network")):
            crawl.verify(self.out, *loaded)
        self.assertEqual(before, [(path, path.stat().st_mtime_ns, path.read_bytes()) for path in files])

    def test_missing_depth_rejected_instead_of_silent_truncation(self):
        spec = self.spec | {"max_depth": 1}
        with self.assertRaisesRegex(ValueError, "unreachable.*end"):
            crawl.canonical_manifest(*self.loaded(spec), self.mock_fetch)

    def test_roster_bound_fails_before_fetching(self):
        with self.assertRaisesRegex(ValueError, "source count bound"):
            self.loaded(self.spec | {"max_sources": 3})

    def test_invalid_commit_path_and_output_id(self):
        with self.assertRaisesRegex(ValueError, "full lowercase commit SHA"):
            self.loaded(self.spec | {"revision": "main"})
        for unsafe in ("../secret.md", "content/../secret.md", "/content/team/start.md", "content\\start.md"):
            with self.subTest(path=unsafe):
                spec = deepcopy(self.spec)
                spec["allowlist"][0]["source_path"] = unsafe
                with self.assertRaisesRegex(ValueError, "Invalid allowed"):
                    self.loaded(spec)
        spec = deepcopy(self.spec)
        spec["allowlist"][0]["source_id"] = "con"
        with self.assertRaisesRegex(ValueError, "Invalid allowed"):
            self.loaded(spec)

    def test_rejects_duplicate_spec_fields(self):
        self.path.write_text('{"version": 1, "version": 1}', encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "duplicate JSON field"):
            crawl.load_spec(self.path)

    def test_bad_digest_or_oversized_source_leaves_no_output(self):
        loaded = self.loaded()
        for raw in (b"wrong digest", b"x" * 1025):
            with self.subTest(size=len(raw)):
                with patch.object(crawl, "online_fetch", return_value=raw):
                    with self.assertRaisesRegex(ValueError, "Size or digest mismatch"):
                        crawl.crawl(self.out, *loaded)
                self.assertFalse(self.out.exists())

    def test_existing_output_is_untouched(self):
        loaded = self.run_mock_crawl()
        manifest = (self.out / "manifest.json").read_bytes()
        with patch.object(crawl, "online_fetch", side_effect=AssertionError("Unexpected network")):
            with self.assertRaisesRegex(ValueError, "new directory"):
                crawl.crawl(self.out, *loaded)
        self.assertEqual((self.out / "manifest.json").read_bytes(), manifest)

    def test_verify_rejects_a_modified_source(self):
        loaded = self.run_mock_crawl()
        (self.out / "sources" / "start.md").write_bytes(self.content["start"] + b"changed")
        with self.assertRaisesRegex(ValueError, "Size or digest mismatch"):
            crawl.verify(self.out, *loaded)

    def test_verify_rejects_extra_source_or_manifest_tampering(self):
        loaded = self.run_mock_crawl()
        extra = self.out / "sources" / "unknown.md"
        extra.write_bytes(b"unknown")
        with self.assertRaisesRegex(ValueError, "filenames differ"):
            crawl.verify(self.out, *loaded)
        extra.unlink()
        manifest = self.out / "manifest.json"
        manifest.write_bytes(manifest.read_bytes() + b"\n")
        with self.assertRaisesRegex(ValueError, "does not match"):
            crawl.verify(self.out, *loaded)


if __name__ == "__main__":
    unittest.main()
