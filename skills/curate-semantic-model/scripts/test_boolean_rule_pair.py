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

    def run_pair(self, pair, *, output=None, mode="--boolean-pair"):
        self.pair_path.write_text(json.dumps(pair), encoding="utf-8")
        destination = output or self.output
        return subprocess.run([sys.executable, str(CLI), "--base", str(self.base), "--head", str(self.head),
                               mode, str(self.pair_path), "--output", str(destination)],
                              check=False, capture_output=True, text=True)

    def checked(self, pair, *, mode="--boolean-pair"):
        self.output_counter += 1
        destination = self.root / f"result-{self.output_counter}.json"
        process = self.run_pair(pair, output=destination, mode=mode)
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

    def test_three_branch_exactly_one_rejects_all_overlap(self):
        pair = self.pair(["plain", ["exactly-one", "A", "B", "C"], None],
                         ["plain", ["or", "A", "B", "C"], None])
        pair["atoms"]["C"] = "reviewed proposition C"
        result = self.checked(pair)
        self.assertEqual(result["classification"], "base-implies-head")
        self.assertEqual(result["region_counts"], {"base_not_head": 0, "head_not_base": 4,
                                                   "both": 3, "neither": 1})

    def test_exactly_one_preserves_repetition_and_fingerprint(self):
        result = self.checked(self.pair(["plain", ["exactly-one", "A", "A", "B"], None],
                                        ["plain", ["and", ["not", "A"], "B"], None]))
        self.assertEqual(result["classification"], "same")
        self.assertEqual(result["fingerprints"]["base"], result["fingerprints"]["head"])

    def test_exactly_one_requires_at_least_two_branches(self):
        pair = self.pair(["plain", ["exactly-one", "A"], None], ["plain", "A", None])
        process = self.run_pair(pair)
        self.assertEqual(process.returncode, 2, process.stdout + process.stderr)
        self.assertIn("Invalid Boolean operator arity", process.stdout)
        self.assertFalse(self.output.exists())

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

    def test_consequence_uses_all_reviewed_premises(self):
        first = ["if", "B", "A"]
        second = ["if", "C", "B"]
        candidate = ["if", "C", "A"]
        premise = {"start_line": 1, "end_line": 1, "quote": "Base reviewed rule."}
        rows = [{"rule": rule, "evidence": premise} for rule in (first, second)]
        pair = self.pair(None, candidate, base_rows=rows)
        pair["atoms"]["C"] = "reviewed proposition C"
        result = self.checked(pair, mode="--boolean-consequence")
        self.assertEqual((result["status"], result["classification"]), ("evaluated", "entailed"))
        self.assertIsNone(result["counterexamples"]["base_not_head"])
        self.assertIsNotNone(result["region_witnesses"]["both"])
        pair["base"].pop()
        result = self.checked(pair, mode="--boolean-consequence")
        self.assertEqual(result["classification"], "independent")
        self.assertEqual(result["counterexamples"]["base_not_head"], {"A": True, "B": True, "C": False})
        self.assertIsNotNone(result["region_witnesses"]["both"])

    def test_consequence_distinguishes_refutation_and_candidate_profiles(self):
        cases = [
            ("B", ["not", "B"], "refuted", "contingent"),
            ("B", ["or", "A", ["not", "A"]], "entailed", "tautology"),
            ("B", ["and", "A", ["not", "A"]], "refuted", "contradiction"),
            (["or", "A", ["not", "A"]], "B", "independent", "contingent"),
        ]
        for premise, candidate, classification, profile in cases:
            with self.subTest(premise=premise, candidate=candidate):
                result = self.checked(self.pair(["plain", premise, None], ["plain", candidate, None]),
                                      mode="--boolean-consequence")
                self.assertEqual(result["classification"], classification)
                self.assertEqual(result["candidate_profile"], profile)
                self.assertEqual(result["region_witnesses"]["both"] is None, classification == "refuted")
                self.assertEqual(result["counterexamples"]["base_not_head"] is None, classification == "entailed")

    def test_consequence_holds_on_inconsistent_premises_before_candidate_profile(self):
        premise = ["plain", ["and", "A", ["not", "A"]], None]
        candidate = ["plain", ["or", "B", ["not", "B"]], None]
        result = self.checked(self.pair(premise, candidate), mode="--boolean-consequence")
        self.assertEqual((result["status"], result["classification"]), ("hold", "inconsistent-premises"))
        self.assertEqual(result["premise_profile"], "contradiction")
        self.assertEqual(result["candidate_profile"], "tautology")
        self.assertIsNone(result["region_witnesses"]["both"])
        self.assertIsNone(result["counterexamples"]["base_not_head"])

    def test_consequence_fails_before_evaluation_on_stale_candidate_source(self):
        pair = self.pair(["plain", "A", None], ["plain", "A", None])
        self.head.write_text("Edited candidate.\n", encoding="utf-8")
        process = self.run_pair(pair, mode="--boolean-consequence")
        self.assertEqual(process.returncode, 2)
        summary = json.loads(process.stdout)
        self.assertEqual(summary["semantic_status"], "not_run")
        self.assertEqual(summary["error"]["code"], "BOOLEAN_PAIR_BINDING_MISMATCH")
        self.assertFalse(self.output.exists())

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
