#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Unit and CLI regressions for deterministic Boolean evidence indexing."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import boolean_rule_pair
import index_rule_evidence
from semantic_model import EngineError

COMPARE_CLI = HERE / "compare_document_versions.py"
INDEX_CLI = HERE / "index_rule_evidence.py"


class IndexRuleEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.base = self.root / "base.txt"
        self.head = self.root / "head.txt"
        self.base.write_text("😀 café and tea\n", encoding="utf-8")
        self.head.write_text("A and B\n", encoding="utf-8")

    def tearDown(self):
        self.temp.cleanup()

    def pair(self, *, base_row=None):
        base_quote = self.base.read_text(encoding="utf-8").rstrip("\n")
        head_quote = self.head.read_text(encoding="utf-8").rstrip("\n")
        return {
            "source_sha256": {"base": hashlib.sha256(self.base.read_bytes()).hexdigest(),
                              "head": hashlib.sha256(self.head.read_bytes()).hexdigest()},
            "atoms": {"A": "café proposition", "B": "tea proposition"},
            "base": [base_row or {"rule": ["plain", ["and", "A", "B"], None],
                                  "evidence": {"start_line": 1, "end_line": 1, "quote": base_quote}}],
            "head": [{"rule": ["plain", ["and", "A", "B"], None],
                      "evidence": {"start_line": 1, "end_line": 1, "quote": head_quote}}],
        }

    def run_compare(self, pair):
        pair_path = self.root / "pair.json"
        output = self.root / "result.json"
        pair_path.write_text(json.dumps(pair, ensure_ascii=False), encoding="utf-8")
        process = subprocess.run([sys.executable, str(COMPARE_CLI), "--base", str(self.base),
                                  "--head", str(self.head), "--boolean-pair", str(pair_path),
                                  "--output", str(output)], capture_output=True, text=True, check=False)
        return process, output

    def test_token_index_has_codepoint_and_exact_utf8_offsets(self):
        quote = "😀 café"
        tokens = index_rule_evidence.index_quote(quote)
        cafe = tokens[1]
        self.assertEqual((cafe["text"], cafe["start"], cafe["end"]), ("café", 2, 6))
        raw = quote.encode("utf-8")
        self.assertEqual(raw[cafe["byte_start"]:cafe["byte_end"]].decode("utf-8"), "café")

    def test_index_cli_emits_digest_quote_and_tokens(self):
        source = self.root / "source.txt"
        source.write_bytes("A 😀 café\r\nB\r\n".encode("utf-8"))
        output = self.root / "index.json"
        proc = subprocess.run([sys.executable, str(INDEX_CLI), "--source", str(source),
                               "--start-line", "1", "--end-line", "2", "--output", str(output)],
                              capture_output=True, text=True, check=False)
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        data = json.loads(output.read_text(encoding="utf-8"))
        self.assertEqual(data["source_sha256"], hashlib.sha256(source.read_bytes()).hexdigest())
        self.assertEqual(data["evidence"]["quote"], "A 😀 café\nB")
        self.assertEqual(data["tokens"][2]["text"], "café")

    def test_index_cli_rejects_wrong_line_bounds(self):
        output = self.root / "index.json"
        proc = subprocess.run([sys.executable, str(INDEX_CLI), "--source", str(self.base),
                               "--start-line", "2", "--end-line", "3", "--output", str(output)],
                              capture_output=True, text=True, check=False)
        self.assertEqual(proc.returncode, 2)
        self.assertFalse(output.exists())

    def test_index_cli_never_overwrites_existing_output(self):
        output = self.root / "index.json"
        output.write_text("preserve", encoding="utf-8")
        proc = subprocess.run([sys.executable, str(INDEX_CLI), "--source", str(self.base),
                               "--start-line", "1", "--end-line", "1", "--output", str(output)],
                              capture_output=True, text=True, check=False)
        self.assertEqual(proc.returncode, 2)
        self.assertEqual(output.read_text(encoding="utf-8"), "preserve")

    def test_stale_source_digest_is_rejected_for_indexed_boolean_pair(self):
        indexed = {"rule": ["plain", ["and", "A", "B"], None],
                   "evidence": {"start_line": 1, "end_line": 1},
                   "atom_refs": {"A": [[2, 2]], "B": [[4, 4]]}}
        pair = self.pair(base_row=indexed)
        self.base.write_text("Changed after indexing.\n", encoding="utf-8")
        proc, output = self.run_compare(pair)
        self.assertEqual(proc.returncode, 2)
        self.assertIn("BOOLEAN_PAIR_BINDING_MISMATCH", proc.stdout)
        self.assertFalse(output.exists())

    def test_valid_discontiguous_atom_ranges_compile_exact_evidence(self):
        row = {"rule": ["plain", ["and", "A", "B"], None],
               "evidence": {"start_line": 1, "end_line": 1},
               "atom_refs": {"A": [[2, 2], [4, 4]], "B": [[2, 2]]}}
        # Distinct atoms may not share the same span set; use the second proposition's own range.
        row["atom_refs"]["B"] = [[4, 4]]
        pair = self.pair(base_row=row)
        pair["atoms"] = {"A": "café and tea phrase", "B": "tea proposition"}
        proc, output = self.run_compare(pair)
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        result = json.loads(output.read_text(encoding="utf-8"))
        compiled = result["reviewed_rules"]["base"][0]
        self.assertEqual(compiled["evidence"]["quote"], "😀 café and tea")
        self.assertEqual([part["quote"] for part in compiled["atom_evidence"]["A"]], ["café", "tea"])
        self.assertEqual(compiled["atom_evidence"]["A"][0]["byte_start"], len("😀 ".encode("utf-8")))

    def test_punctuation_only_atom_range_is_rejected(self):
        self.base.write_text("A. B\n", encoding="utf-8")
        row = {"rule": ["plain", "A", None], "evidence": {"start_line": 1, "end_line": 1},
               "atom_refs": {"A": [[2, 2]]}}
        with self.assertRaises(EngineError):
            boolean_rule_pair.compare_rules(self.pair(base_row=row),
                {"base": [self.base.read_text(encoding="utf-8").rstrip("\n")],
                 "head": [self.head.read_text(encoding="utf-8").rstrip("\n")]},
                {"base": hashlib.sha256(self.base.read_bytes()).hexdigest(),
                 "head": hashlib.sha256(self.head.read_bytes()).hexdigest()})

    def test_wrong_atom_ref_shape_and_token_bounds_are_rejected(self):
        for refs in ({"A": {"first": 2, "last": 2}, "B": [[4, 4]]},
                     {"A": [[1, 99]], "B": [[4, 4]]}):
            with self.subTest(refs=refs):
                row = {"rule": ["plain", ["and", "A", "B"], None],
                       "evidence": {"start_line": 1, "end_line": 1}, "atom_refs": refs}
                pair = self.pair(base_row=row)
                lines = {"base": [self.base.read_text(encoding="utf-8").rstrip("\n")],
                         "head": [self.head.read_text(encoding="utf-8").rstrip("\n")]}
                digests = {side: hashlib.sha256(path.read_bytes()).hexdigest()
                           for side, path in (("base", self.base), ("head", self.head))}
                with self.assertRaises(EngineError):
                    boolean_rule_pair.compare_rules(pair, lines, digests)

    def test_legacy_boolean_pair_row_and_result_fields_are_unchanged(self):
        pair = self.pair()
        original_row = dict(pair["base"][0])
        proc, output = self.run_compare(pair)
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        result = json.loads(output.read_text(encoding="utf-8"))
        self.assertEqual(result["reviewed_rules"]["base"][0], original_row)
        self.assertNotIn("atom_evidence", result["reviewed_rules"]["base"][0])


if __name__ == "__main__":
    unittest.main()
