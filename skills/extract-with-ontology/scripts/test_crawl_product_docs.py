#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Checks for bounded, replayable documentation source discovery."""

from copy import deepcopy
from hashlib import sha256
import json
import os
from pathlib import Path
from subprocess import run
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

import crawl_product_docs as crawl


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

    def test_comments_inside_code_do_not_consume_links(self):
        text = "\n".join([
            "\x60\x60\x60html", "<!--", "[fenced](invalid)", "\x60\x60\x60",
            "    <!-- [indented](invalid)",
            "\x60<!-- [inline](invalid)\x60 [after inline](first.md)",
            "<!-- [comment](invalid)", "\x60\x60\x60", "[comment fence](invalid)",
            "--> [after comment](second.md)", "[ordinary](third.md)",
        ])
        self.assertEqual(list(crawl.markdown_targets(text)), ["first.md", "second.md", "third.md"])

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

    def repository_spec(self):
        spec = deepcopy(self.spec)
        spec.update(version=2, repository="Example/docs", docs_origin="https://docs.example.org",
                    docs_base_path="/v3")
        paths = {
            "start": ("guide/start.markdown", "/v3/start/"),
            "leaf": ("guide/leaf.md", "/v3/leaf/"),
            "section": ("guide/section/index.md", "/v3/section/"),
            "end": ("other/end.mdx", "/v3/end/"),
        }
        self.content = {
            "start": b"[via alias](/old/section?campaign=1#intro)\n[relative](leaf.md#part)\n"
                     b"[foreign](https://other.example.org/v3/end/)\n"
                     b"[foreign raw](https://docs.example.org@other.example.org/v3/end/)\n"
                     b"[outside](/v3/other/)\n",
            "leaf": b"[repository relative](../other/end.mdx)\n",
            "section": b"[publisher relative](../end/)\n",
            "end": b"[publisher absolute](https://docs.example.org/v3/start)\n"
                   b"[Liquid]({{site.url}}{{site.baseurl}}/leaf/#local)\n",
        }
        for row in spec["allowlist"]:
            name = row["source_id"]
            row["source_path"], row["publisher_path"] = paths[name]
            row["sha256"] = sha256(self.content[name]).hexdigest()
            if name == "section":
                row["aliases"] = ["/old/section/"]
        return spec

    def test_repository_capture_and_replay(self):
        spec = self.repository_spec()
        loaded = self.loaded(spec)
        paths = {row["source_id"]: row["source_path"] for row in spec["allowlist"]}
        seen = []

        def fetch(name, url, limit):
            seen.append(name)
            self.assertEqual(url, f"https://raw.githubusercontent.com/Example/docs/{REVISION}/{paths[name]}")
            return self.content[name]

        with patch.object(crawl, "online_fetch", side_effect=fetch):
            crawl.crawl(self.out, *loaded)
        self.assertEqual(seen, ["start", "leaf", "section", "end"])
        manifest = json.loads((self.out / "manifest.json").read_bytes())
        rows = {row["source_id"]: row for row in manifest["sources"]}
        self.assertEqual(rows["section"]["publisher_url"], "https://docs.example.org/v3/section/")
        self.assertEqual(rows["end"]["depth"], 2)
        self.assertEqual(rows["end"]["discovered_from"], "leaf")
        self.assertEqual(manifest["links"], [{"from": left, "to": right} for left, right in
            [("end", "leaf"), ("end", "start"), ("leaf", "end"), ("section", "end"),
             ("start", "leaf"), ("start", "section")]])
        with patch.object(crawl, "online_fetch", side_effect=AssertionError("Unexpected network")):
            crawl.verify(self.out, *loaded)

    def test_repository_scope_rejects_unsafe_or_ambiguous_config(self):
        spec = self.repository_spec()
        for change in ({"repository": "org/../other"}, {"repository": "org/repo?ref=main"},
                       {"docs_origin": "http://docs.example.org"},
                       {"docs_origin": "https://docs.example.org@evil.test"},
                       {"docs_origin": "https://docs.example.org/path"},
                       {"docs_origin": "https://127.0.0.1"}, {"docs_base_path": "/v3/"},
                       {"docs_base_path": "/v3/../private"}):
            with self.subTest(change=change), self.assertRaises(ValueError):
                self.loaded(spec | change)
        for fields in ({"source_path": "docs/../../secret.md"}, {"source_path": "docs/file.txt"},
                       {"publisher_path": "//other.example.org/docs"}, {"publisher_path": "/v3/../docs"},
                       {"publisher_path": "/v3/section"}, {"aliases": ["/v3/section/"]},
                       {"aliases": "/legacy"}, {"aliases": ["/outside?query=value"]}):
            with self.subTest(fields=fields), self.assertRaises(ValueError):
                malformed = deepcopy(spec)
                malformed["allowlist"][0].update(fields)
                self.loaded(malformed)

    def test_repository_source_link_ambiguity_fails_closed(self):
        spec = self.repository_spec()
        section = next(row for row in spec["allowlist"] if row["source_id"] == "section")
        section["aliases"].append("/v3/start/leaf.md")
        with self.assertRaisesRegex(ValueError, "two destinations"):
            crawl.canonical_manifest(*self.loaded(spec), lambda name, url, limit: self.content[name])

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

    def test_manifest_publication_failure_clears_claimed_output(self):
        loaded = self.loaded()
        rename = Path.rename

        def reject_manifest(path, target):
            if path.name == "manifest.json":
                raise OSError("Injected manifest publication failure")
            return rename(path, target)

        with patch.object(crawl, "online_fetch", side_effect=self.mock_fetch):
            with patch.object(Path, "rename", reject_manifest):
                with self.assertRaisesRegex(OSError, "publication failure"):
                    crawl.crawl(self.out, *loaded)
        self.assertFalse(self.out.exists())
        self.run_mock_crawl()

    def test_verify_rejects_symlinked_source_directory_inside_output(self):
        loaded = self.run_mock_crawl()
        raw_sources = self.out / "sources"
        other = raw_sources.rename(self.out / "other")
        try:
            raw_sources.symlink_to(other, target_is_directory=True)
        except OSError as error:
            self.skipTest(f"Directory symlinks unavailable: {error}")
        with self.assertRaisesRegex(ValueError, "regular manifest"):
            crawl.verify(self.out, *loaded)

    @unittest.skipUnless(os.name == "nt", "Windows directory junctions")
    def test_verify_rejects_junction_inside_output(self):
        loaded = self.run_mock_crawl()
        raw_sources = self.out / "sources"
        other = raw_sources.rename(self.out / "other")
        run(["cmd.exe", "/c", "mklink", "/J", str(raw_sources), str(other)],
            check=True, capture_output=True)
        with self.assertRaisesRegex(ValueError, "regular manifest"):
            crawl.verify(self.out, *loaded)

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
