#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Black-box tests for the source-bound reviewed Boolean comparison mode."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest


CLI = Path(__file__).with_name("compare_document_versions.py")


class BooleanRulePairCLITest(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.base = self.root / "base.txt"
        self.head = self.root / "head.txt"
        self.base.write_text("Base reviewed rule.\n", encoding="utf-8")
        self.head.write_text("Head reviewed rule.\n", encoding="utf-8")
        self.pair_path = self.root / "pair.json"
        self.output = self.root / "result.json"
        self.output_counter = 0

    def tearDown(self):
        self.temp.cleanup()

    def pair(self, base_rule, head_rule, *, base_rows=None, head_rows=None):
        return {
            "source_sha256": {"base": hashlib.sha256(self.base.read_bytes()).hexdigest(),
                              "head": hashlib.sha256(self.head.read_bytes()).hexdigest()},
            "atoms": {"A": "reviewed proposition A", "B": "reviewed proposition B"},
            "base": base_rows or [{"rule": base_rule, "evidence": {
                "start_line": 1, "end_line": 1, "quote": self.base.read_text().rstrip("\n")}}],
            "head": head_rows or [{"rule": head_rule, "evidence": {
                "start_line": 1, "end_line": 1, "quote": self.head.read_text().rstrip("\n")}}],
        }

    def run_pair(self, pair, *, output=None):
        self.pair_path.write_text(json.dumps(pair), encoding="utf-8")
        destination = output or self.output
        return subprocess.run([sys.executable, str(CLI), "--base", str(self.base), "--head", str(self.head),
                               "--boolean-pair", str(self.pair_path), "--output", str(destination)],
                              check=False, capture_output=True, text=True)

    def checked(self, pair):
        self.output_counter += 1
        destination = self.root / f"result-{self.output_counter}.json"
        process = self.run_pair(pair, output=destination)
        self.assertEqual(process.returncode, 0, process.stdout + process.stderr)
        self.assertEqual(json.loads(process.stdout)["engine_status"], "completed")
        return json.loads(destination.read_text(encoding="utf-8"))

    def test_base_implies_head_has_head_not_base_witness(self):
        result = self.checked(self.pair(["plain", "A", None], ["if", "A", "B"]))
        self.assertEqual(result["classification"], "base-implies-head")
        self.assertEqual(result["counterexamples"]["base_not_head"], None)
        self.assertIsNotNone(result["counterexamples"]["head_not_base"])

    def test_head_implies_base_has_base_not_head_witness(self):
        result = self.checked(self.pair(["if", "A", "B"], ["plain", "A", None]))
        self.assertEqual(result["classification"], "head-implies-base")
        self.assertIsNotNone(result["counterexamples"]["base_not_head"])
        self.assertIsNone(result["counterexamples"]["head_not_base"])

    def test_iff_is_biconditional_and_not_sufficient_only(self):
        result = self.checked(self.pair(["iff", "A", "B"], ["plain", "A", None]))
        self.assertEqual(result["classification"], "different")
        self.assertIsNotNone(result["counterexamples"]["base_not_head"])
        self.assertIsNotNone(result["counterexamples"]["head_not_base"])

    def test_and_or_and_scoped_negation_produce_concrete_difference(self):
        result = self.checked(self.pair(["plain", ["not", ["and", "A", "B"]], None],
                                         ["plain", ["or", ["not", "A"], "B"], None]))
        self.assertEqual(result["classification"], "different")
        self.assertIsNotNone(result["counterexamples"]["base_not_head"])
        self.assertIsNotNone(result["counterexamples"]["head_not_base"])

    def test_or_and_formulas_and_rule_order_have_stable_equivalence(self):
        base = [{"rule": ["plain", ["or", "A", "B"], None], "evidence": {
            "start_line": 1, "end_line": 1, "quote": "Base reviewed rule."}},
                {"rule": ["plain", ["or", "B", "A"], None], "evidence": {
            "start_line": 1, "end_line": 1, "quote": "Base reviewed rule."}}]
        head = [{"rule": ["plain", ["or", "B", "A"], None], "evidence": {
            "start_line": 1, "end_line": 1, "quote": "Head reviewed rule."}},
                {"rule": ["plain", ["or", "A", "B"], None], "evidence": {
            "start_line": 1, "end_line": 1, "quote": "Head reviewed rule."}}]
        result = self.checked(self.pair(None, None, base_rows=base, head_rows=head))
        self.assertEqual(result["classification"], "same")
        self.assertEqual(result["fingerprints"]["base"], result["fingerprints"]["head"])

    def test_fingerprint_ignores_inessential_reviewed_atoms(self):
        first = self.checked(self.pair(["plain", "A", None], ["plain", "A", None]))
        second_pair = self.pair(["plain", "A", None], ["plain", "A", None])
        second_pair["atoms"]["C"] = "reviewed but inessential proposition C"
        second = self.checked(second_pair)
        self.assertEqual(first["fingerprints"]["base"]["essential_atoms"], ["A"])
        self.assertEqual(first["fingerprints"]["base"]["sha256"], second["fingerprints"]["base"]["sha256"])
        self.assertIn("C", second["atoms"])

    def test_jointly_satisfiable_is_reported(self):
        result = self.checked(self.pair(["plain", "A", None], ["plain", "A", None]))
        self.assertEqual(result["classification"], "same")
        self.assertEqual(result["region_counts"]["neither"], 2)
        self.assertTrue(result["jointly_satisfiable"])

    def test_contradiction_holds_instead_of_vacuous_implication(self):
        result = self.checked(self.pair(["plain", ["and", "A", ["not", "A"]], None],
                                         ["plain", "B", None]))
        self.assertEqual(result["status"], "vacuous-or-tautological-rule-set")
        self.assertEqual(result["classification"], "hold")

    def test_tautology_holds(self):
        result = self.checked(self.pair(["plain", ["or", "A", ["not", "A"]], None],
                                         ["plain", "B", None]))
        self.assertEqual(result["classification"], "hold")

    def test_exact_line_quote_is_required(self):
        pair = self.pair(["plain", "A", None], ["plain", "A", None])
        pair["base"][0]["evidence"]["quote"] = "invented quote"
        process = self.run_pair(pair)
        self.assertEqual(process.returncode, 2)
        self.assertEqual(json.loads(process.stdout)["semantic_status"], "not_run")
        self.assertFalse(self.output.exists())

    def test_stale_source_sha256_is_rejected(self):
        pair = self.pair(["plain", "A", None], ["plain", "A", None])
        self.head.write_text("Edited after review.\n", encoding="utf-8")
        process = self.run_pair(pair)
        self.assertEqual(process.returncode, 2)
        self.assertEqual(json.loads(process.stdout)["error"]["code"], "BOOLEAN_PAIR_BINDING_MISMATCH")

    def test_output_is_never_overwritten(self):
        first = self.checked(self.pair(["plain", "A", None], ["plain", "A", None]))
        # Put a result at the fixed destination used by the second call.
        initial = self.run_pair(self.pair(["plain", "A", None], ["plain", "A", None]))
        self.assertEqual(initial.returncode, 0, initial.stdout + initial.stderr)
        original = self.output.read_bytes()
        process = self.run_pair(self.pair(["plain", "A", None], ["plain", "B", None]))
        self.assertEqual(process.returncode, 2)
        self.assertEqual(self.output.read_bytes(), original)
        self.assertEqual(first["classification"], "same")

    def test_modes_cover_only_if_unless_and_plain(self):
        for mode in ("if", "only-if", "iff", "unless", "plain"):
            with self.subTest(mode=mode):
                result = self.checked(self.pair([mode, "A", "B"] if mode != "plain" else [mode, "A", None],
                                                 ["plain", "A", None]))
                self.assertIn(result["classification"], {"same", "base-implies-head", "head-implies-base", "different", "hold"})


if __name__ == "__main__":
    unittest.main()
