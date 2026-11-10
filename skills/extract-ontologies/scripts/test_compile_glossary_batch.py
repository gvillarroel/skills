#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Exercise source pins and record isolation through the batch CLI."""

from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest

SCRIPT = Path(__file__).with_name("compile_glossary_batch.py")


class GlossaryBatchTests(unittest.TestCase):
    def setUp(self):
        workspace = TemporaryDirectory()
        self.addCleanup(workspace.cleanup)
        self.root = Path(workspace.name)
        self.output = self.root / "batch.json"
        self.manifest = {"documents": {}}
        self.frames = {}
        for name in ("First", "Middle", "Last"):
            source = f"{name} means a\u2028device.\n".encode()
            path = self.root / f"{name}.txt"
            path.write_bytes(source)
            pin = sha256(source).hexdigest()
            self.manifest["documents"][name] = {"path": path.name, "sha256": pin}
            draft = {
                "source_sha256": pin,
                "proposals": [{
                    "kind": "definition",
                    "lane": "entity",
                    "term": {"quote": name},
                    "value": {"quote": "a\u2028device"},
                    "evidence": {"start_line": 1, "end_line": 1},
                }],
            }
            self.frames[name] = name.encode() + b"\t" + json.dumps(draft, ensure_ascii=False).encode()

    def invoke(self, raw, exit_code, output=None):
        manifest = self.root / "manifest.json"
        records = self.root / "drafts.txt"
        manifest.write_text(json.dumps(self.manifest), encoding="utf-8")
        records.write_bytes(raw)
        output = self.output if output is None else output
        result = subprocess.run(
            [sys.executable, "-B", str(SCRIPT), "--manifest", str(manifest),
             "--records", str(records), "--output", str(output)],
            capture_output=True, text=True, check=False,
        )
        self.assertEqual(result.returncode, exit_code, result.stdout + result.stderr)
        if exit_code != 2:
            ledger = json.loads(output.read_bytes())
            self.assertEqual(ledger["records_sha256"], sha256(raw).hexdigest())
            self.assertEqual(ledger["status"], "compiled" if exit_code == 0 else "partial")
            return ledger
        self.assertEqual(json.loads(result.stdout)["status"], "error")

    def test_clean_crlf_and_unicode_replay_byte_for_byte(self):
        raw = b"\r\n".join(self.frames.values())
        ledger = self.invoke(raw, 0)
        replay = self.root / "replay.json"
        self.invoke(raw, 0, replay)
        self.assertEqual(self.output.read_bytes(), replay.read_bytes())
        self.assertEqual(ledger["expected_documents"], ["First", "Last", "Middle"])
        value = ledger["documents"]["Middle"]["proposals"][0]["value"]
        self.assertEqual(value["quote"], "a\u2028device")

    def test_invalid_utf8_only_quarantines_its_document(self):
        raw = b"\n".join([self.frames["First"], b"Middle\t\xff", self.frames["Last"]])
        ledger = self.invoke(raw, 1)
        self.assertEqual(set(ledger["documents"]), {"First", "Last"})
        self.assertEqual(
            [(item["document"], item["line"], item["code"]) for item in ledger["diagnostics"]],
            [("Middle", 2, "invalid-record")],
        )

    def test_duplicate_header_quarantines_a_valid_draft_even_if_duplicate_is_broken(self):
        raw = b"\n".join([*self.frames.values(), b"Middle\t{"])
        ledger = self.invoke(raw, 1)
        self.assertEqual(set(ledger["documents"]), {"First", "Last"})
        self.assertEqual(ledger["diagnostics"], [
            {"document": "Middle", "lines": [2, 4], "code": "duplicate-document"},
        ])

    def test_reports_unattributed_records_and_missing_and_stale_sources(self):
        (self.root / "Middle.txt").write_text("Modified source", encoding="utf-8")
        raw = b"\n".join([self.frames["First"], self.frames["Middle"], b"Unknown\t{}", b"{"])
        ledger = self.invoke(raw, 1)
        self.assertEqual(set(ledger["documents"]), {"First"})
        self.assertEqual([item["code"] for item in ledger["diagnostics"]],
                         ["unexpected-document", "unframed-record", "missing-document", "stale-source"])

    def test_path_escape_is_fatal_and_existing_output_is_preserved(self):
        raw = b"\n".join(self.frames.values())
        self.invoke(raw, 0)
        previous = self.output.read_bytes()
        self.invoke(raw, 2)
        self.assertEqual(self.output.read_bytes(), previous)
        self.manifest["documents"]["First"]["path"] = "../First.txt"
        new_output = self.root / "invalid.json"
        self.invoke(raw, 2, new_output)
        self.assertFalse(new_output.exists())


if __name__ == "__main__":
    unittest.main()
