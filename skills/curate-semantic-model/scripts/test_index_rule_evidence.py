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

    def test_different_partitions_cannot_reuse_same_tokens_for_two_atoms(self):
        self.base.write_text("A one B two\n", encoding="utf-8")
        row = {"rule": ["plain", ["or", "A", "B"], None],
               "evidence": {"start_line": 1, "end_line": 1},
               "atom_refs": {"A": [[1, 4]], "B": [[1, 2], [3, 4]]}}
        proc, output = self.run_compare(self.pair(base_row=row))
        self.assertEqual(proc.returncode, 2, proc.stdout + proc.stderr)
        self.assertIn("Distinct atoms need different source token coverage", proc.stdout)
        self.assertFalse(output.exists())

    def test_fingerprint_uses_token_coverage_and_preserves_fragments(self):
        self.base.write_text("café checks postal code or city\n", encoding="utf-8")
        lines = {"base": ["café checks postal code or city"], "head": ["A and B"]}
        row = {"rule": ["plain", ["or", "A", "B"], None],
               "evidence": {"start_line": 1, "end_line": 1},
               "atom_refs": {"A": [[1, 4]], "B": [[1, 2], [6, 6]]}}
        pair = self.pair(base_row=row)

        def compare():
            result = boolean_rule_pair.compare_rules(pair, lines, pair["source_sha256"])
            return result["reviewed_rules"]["base"][0]

        first = compare()
        row["atom_refs"] = {"B": [[1, 2], [6, 6]], "A": [[1, 2], [3, 4]]}
        split = compare()
        self.assertEqual(first["atom_evidence_sha256"], split["atom_evidence_sha256"])
        self.assertEqual([part["quote"] for part in split["atom_evidence"]["A"]], ["café checks", "postal code"])
        row["atom_refs"]["A"] = [[1, 3]]
        self.assertNotEqual(first["atom_evidence_sha256"], compare()["atom_evidence_sha256"])

    def test_exact_quote_and_numeric_ranges_have_same_coverage(self):
        self.base.write_text("The parser accepts the .csv extension.\n", encoding="utf-8")
        row = {"rule": ["plain", "A", None], "evidence": {"start_line": 1, "end_line": 1},
               "atom_refs": {"A": [{"quote": "parser accepts"}, [5, 6]]}}
        pair = self.pair(base_row=row)
        lines = {"base": ["The parser accepts the .csv extension."], "head": ["A and B"]}
        mixed = boolean_rule_pair.compare_rules(pair, lines, pair["source_sha256"])["reviewed_rules"]["base"][0]
        self.assertEqual([span["quote"] for span in mixed["atom_evidence"]["A"]], ["parser accepts", ".csv"])
        self.assertEqual(mixed["atom_refs"], row["atom_refs"])
        row["atom_refs"]["A"] = [[2, 3], [5, 6]]
        numeric = boolean_rule_pair.compare_rules(pair, lines, pair["source_sha256"])["reviewed_rules"]["base"][0]
        self.assertEqual(mixed["atom_evidence_sha256"], numeric["atom_evidence_sha256"])
        self.assertEqual(mixed["atom_evidence"], numeric["atom_evidence"])

    def test_repeated_literal_needs_the_exact_occurrence(self):
        self.base.write_text("Example key, operative key.\n", encoding="utf-8")
        row = {"rule": ["plain", "A", None], "evidence": {"start_line": 1, "end_line": 1},
               "atom_refs": {"A": [{"quote": "key"}]}}
        pair = self.pair(base_row=row)
        proc, output = self.run_compare(pair)
        self.assertEqual(proc.returncode, 2, proc.stdout + proc.stderr)
        self.assertIn("Atom quote repeats", proc.stdout)
        self.assertFalse(output.exists())
        row["atom_refs"]["A"][0]["first_token"] = 5
        proc, output = self.run_compare(pair)
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        compiled = json.loads(output.read_bytes())["reviewed_rules"]["base"][0]
        self.assertEqual(compiled["atom_evidence"]["A"][0]["tokens"], [5, 5])

    def test_quote_requires_literal_token_boundaries_and_explicit_position(self):
        self.base.write_text("Café stores .csv.\n", encoding="utf-8")
        selectors = ({"quote": "afé"}, {"quote": "cs"}, {"quote": "café"}, {"quote": "stores  .csv"},
                     {"quote": "stores", "first_token": 1}, {"quote": "Café", "first_token": True},
                     {"quote": "Café", "first_token": None}, {"quote": "Café", "end_token": 1})
        for selector in selectors:
            with self.subTest(selector=selector):
                row = {"rule": ["plain", "A", None], "evidence": {"start_line": 1, "end_line": 1},
                       "atom_refs": {"A": [selector]}}
                proc, output = self.run_compare(self.pair(base_row=row))
                self.assertEqual(proc.returncode, 2, proc.stdout + proc.stderr)
                self.assertFalse(output.exists())

    def test_exact_quote_can_span_normalized_lines_in_its_citation(self):
        self.base.write_bytes(b"\xef\xbb\xbf" + "Café\r\nsecure\tkey\r\n".encode("utf-8"))
        row = {"rule": ["plain", "A", None], "evidence": {"start_line": 1, "end_line": 2},
               "atom_refs": {"A": [{"quote": "Café\nsecure\tkey"}]}}
        pair = self.pair(base_row=row)
        proc, output = self.run_compare(pair)
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        record = json.loads(output.read_bytes())
        self.assertEqual(record["source_sha256"]["base"], hashlib.sha256(self.base.read_bytes()).hexdigest())
        span = record["reviewed_rules"]["base"][0]["atom_evidence"]["A"][0]
        self.assertEqual(span["tokens"], [1, 3])
        self.assertEqual(span["quote"], "Café\nsecure\tkey")
        self.assertEqual(span["byte_end"], len(span["quote"].encode("utf-8")))

    def test_literal_and_numeric_forms_cannot_duplicate_coverage(self):
        self.base.write_text("A reviewed rule.\n", encoding="utf-8")
        row = {"rule": ["plain", ["or", "A", "B"], None],
               "evidence": {"start_line": 1, "end_line": 1},
               "atom_refs": {"A": [[2, 3]], "B": [{"quote": "reviewed rule"}]}}
        proc, output = self.run_compare(self.pair(base_row=row))
        self.assertEqual(proc.returncode, 2, proc.stdout + proc.stderr)
        self.assertIn("Distinct atoms need different source token coverage", proc.stdout)
        self.assertFalse(output.exists())

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
