#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Observable ontology coverage, residual, conflict-binding and CLI tests.

Standard library only. All evidence is synthetic and lives in TemporaryDirectory.
Run: python test_ontology_coverage.py [--receipt /path/to/qa.json]
No reasoner, service, model or external ontology is invoked by these tests.
Python 3.11+, standard library only.
"""
import copy
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timezone

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import ontology_coverage as coverage
import semantic_model as core
import review_conflicts as conflict_engine

HELPER = HERE / "ontology_coverage.py"


def hashfile(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


class CoverageFixture(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="ontology-coverage-")
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name).resolve()
        self.ontology = self.write("ontology.json", {"synthetic": True, "version": "1"})
        self.ontology_hash = hashfile(self.ontology)
        self.payload = {"schema_version": "1", "suite": {"id": "synthetic-suite", "version": "1", "cases": []},
                        "candidates": [{"id": "candidate:A", "label": "Synthetic ontology A", "ontology": {"iri": "https://example.invalid/ontology/A", "version": "1", "artifact": "ontology.json", "sha256": self.ontology_hash}, "assessments": []}]}
        self.make_cases(10)

    def write(self, name, value):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")
        return path

    def make_cases(self, count):
        self.payload["suite"]["cases"] = [{"id": "C" + str(i), "title": "Synthetic case " + str(i), "expected": "Expected behavior " + str(i), "method": "Inspect the supplied synthetic assertion", "kind": "competency", "weight": 1} for i in range(count)]
        self.payload["candidates"][0]["assessments"] = [self.assessment("C" + str(i)) for i in range(count)]

    def assessment(self, cid, status="pass"):
        row = {"case_id": cid, "status": status, "observed": "Synthetic observation for " + cid, "reason": "Fixture, not a real vendor result", "ontology_sha256": self.ontology_hash,
               "evidence_mode": "reviewed", "evidence": [{"locator": "synthetic://" + cid, "observation": "Explicit fixture evidence"}]}
        if status != "pass":
            row["next_action"] = "Review or execute this synthetic case"
        return row

    def evaluate(self, previous=None):
        return coverage.evaluate(self.payload, self.root, previous)

    def candidate(self, previous=None):
        return self.evaluate(previous)["candidates"][0]

    def summary(self):
        return self.candidate()["summary"]

    def install_conflict_review(self, status="open", scope_difference=False):
        model = {"schema_version": "1", "contract_id": "conflict-fixture", "contract_version": "1",
                 "sources": [{"id": "s:A", "locator": "synthetic#A", "text": "Service supports local deployment in release one."}, {"id": "s:B", "locator": "synthetic#B", "text": "Service does not support local deployment in release one."}],
                 "nodes": [{"id": "service:A", "type": "Service", "label": "Service", "definition": "Synthetic test subject", "source_ids": ["s:A", "s:B"]}], "relations": [], "bindings": {"s:A": ["service:A"], "s:B": ["service:A"]}}
        contract = {"schema_version": "1", "id": "conflict-fixture", "version": "1", "types": {"Service": {"attributes": {}}}, "relations": {}, "checks": []}
        claims = {"schema_version": "1", "functional_predicates": [], "assertions": []}
        for tag, polarity in [("A", "positive"), ("B", "negative")]:
            scope = {"context": "enterprise", "version": "1", "time": {"kind": "all_time"}}
            if scope_difference and tag == "B":
                scope["version"] = "2"
            claims["assertions"].append({"id": "claim:" + tag, "subject": "service:A", "predicate": "supports", "value": "local", "polarity": polarity,
                                         "source_ids": ["s:" + tag], "scope": scope, "normalization": {"status": "reviewed", "reviewer": "process:fixture", "rationale": "Literal synthetic statement"}})
        review = conflict_engine.scan(model, contract, claims)
        self.assertEqual(len(review["findings"]), 1)
        if not scope_difference:
            item = review["findings"][0]
            if status != "open":
                choice = "defer" if status == "deferred" else "prefer_assertion"
                decision = {"conflict_id": item["id"], "fingerprint": item["fingerprint"], "choice": choice, "reviewer": "user:synthetic-fixture", "rationale": "Synthetic explicit decision; not the real user", "assertion_id": "claim:A"}
                review = conflict_engine.record_decisions(review, {"schema_version": "1", "review_revision": review["review_revision"], "decisions": [decision]})
        path = self.write("conflict-review.json", review)
        self.payload["candidates"][0]["conflict_review"] = {"artifact": path.name, "sha256": hashfile(path), "ontology_sha256": self.ontology_hash}
        return review

    def pin_formal(self, axis, status, ontology_hash=None):
        report = self.write(axis + ".json", {"synthetic_fixture_result": status})
        item = {"status": status, "tool": "SyntheticFixtureTool", "version": "0", "artifact": report.name, "sha256": hashfile(report), "ontology_sha256": ontology_hash or self.ontology_hash}
        self.payload["candidates"][0].setdefault("formal_checks", {})[axis] = item
        return report

    def run_cli(self, args=None, expected=0):
        input_file = self.write("input.json", self.payload)
        before = {p: p.read_bytes() for p in self.root.iterdir() if p.is_file()}
        argv = [sys.executable, "-B", str(HELPER), "--input", str(input_file)]
        argv += list(map(str, args)) if args is not None else ["--report", str(self.root / "out.json")]
        result = subprocess.run(argv, capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(result.returncode, expected, result.stdout + "\n" + result.stderr)
        try:
            output = json.loads(result.stdout)
        except json.JSONDecodeError:
            self.fail("CLI did not return structured JSON: " + result.stdout + "\n" + result.stderr)
        for path, value in before.items():
            self.assertEqual(path.read_bytes(), value, "Input/evidence changed: " + str(path))
        return result, output


class MetricsTests(CoverageFixture):
    def test_large_finite_weight_does_not_overflow_percentage_intermediate(self):
        self.make_cases(1)
        self.payload["suite"]["cases"][0]["weight"] = 1e307
        summary = self.summary()
        self.assertEqual(summary["weighted_strict_coverage_percent"], 100)
        self.assertEqual(summary["weight_denominator"], 1e307)
        json.dumps(summary, allow_nan=False)

    def test_unbounded_integer_weights_retain_exact_denominator(self):
        self.make_cases(2)
        for case in self.payload["suite"]["cases"]:
            case["weight"] = 10 ** 400
        self.payload["candidates"][0]["assessments"][-1] = self.assessment("C1", "fail")
        summary = self.summary()
        self.assertEqual(summary["weighted_strict_coverage_percent"], 50)
        self.assertEqual(summary["weight_denominator"], 2 * 10 ** 400)
        json.dumps(summary, allow_nan=False)

    def test_nonrepresentable_total_weight_is_a_structured_error(self):
        self.make_cases(2)
        for case in self.payload["suite"]["cases"]:
            case["weight"] = 1e308
        with self.assertRaises(core.EngineError) as error:
            self.evaluate()
        self.assertEqual(error.exception.code, "NUMERIC_OVERFLOW")

    def test_nonfinite_weight_is_rejected_by_direct_api(self):
        for value in (float("inf"), float("nan")):
            with self.subTest(value=str(value)):
                self.payload["suite"]["cases"][0]["weight"] = value
                with self.assertRaises(core.EngineError):
                    self.evaluate()

    def test_nine_pass_one_failure_exposes_exact_ten_percent_residual(self):
        self.payload["candidates"][0]["assessments"][-1] = self.assessment("C9", "fail")
        c = self.candidate();s = c["summary"]
        self.assertEqual((s["fully_covered_cases"], s["applicable_cases"]), (9, 10))
        self.assertEqual(s["strict_coverage_percent"], 90)
        self.assertEqual(s["not_fully_covered_percent"], 10)
        self.assertEqual(s["status_breakdown"]["fail"]["percent"], 10)
        self.assertEqual([r["case_id"] for r in c["residual_cases"]], ["C9"])
        self.assertTrue(c["residual_cases"][0]["next_action"])

    def test_nine_pass_one_unknown_is_not_demonstrated_failure(self):
        self.payload["candidates"][0]["assessments"][-1] = self.assessment("C9", "unknown")
        s = self.summary()
        self.assertEqual(s["strict_coverage_percent"], 90)
        self.assertEqual(s["status_breakdown"]["unknown"]["percent"], 10)
        self.assertEqual(s["status_breakdown"]["fail"]["percent"], 0)

    def test_partial_and_error_get_no_invented_partial_credit(self):
        self.payload["candidates"][0]["assessments"][-2:] = [self.assessment("C8", "partial"), self.assessment("C9", "error")]
        s = self.summary()
        self.assertEqual(s["strict_coverage_percent"], 80)
        self.assertEqual(s["status_breakdown"]["partial"]["percent"], 10)
        self.assertEqual(s["status_breakdown"]["error"]["percent"], 10)
        self.assertFalse(s["partial_credit_assumed"])

    def test_missing_observations_remain_in_denominator(self):
        self.payload["candidates"][0]["assessments"].pop()
        c = self.candidate()
        self.assertEqual(c["summary"]["applicable_cases"], 10)
        self.assertEqual(c["summary"]["strict_coverage_percent"], 90)
        self.assertEqual(c["residual_cases"][0]["reported_status"], "unknown")
        self.assertEqual(c["residual_cases"][0]["evidence_mode"], "not_provided")

    def test_weighted_and_unweighted_coverage_are_distinct(self):
        self.make_cases(2)
        self.payload["suite"]["cases"][0]["weight"] = 9
        self.payload["candidates"][0]["assessments"][1] = self.assessment("C1", "fail")
        s = self.summary()
        self.assertEqual(s["strict_coverage_percent"], 50)
        self.assertEqual(s["weighted_strict_coverage_percent"], 90)
        self.assertEqual(s["weight_denominator"], 10)

    def test_markdown_separates_weighted_measurement_from_case_counts(self):
        self.make_cases(2)
        self.payload["suite"]["cases"][0]["weight"] = 9
        self.payload["candidates"][0]["assessments"][1] = self.assessment("C1", "fail")
        report = self.evaluate()
        before = copy.deepcopy(report)
        text = coverage.render_markdown(report)
        table_rows = [[cell.strip() for cell in line.strip().strip("|").split("|")] for line in text.splitlines() if line.startswith("| ")]
        count_header = next(row for row in table_rows if any("applicable" in cell.casefold() for cell in row))
        count_row = next(row for row in table_rows if row[0] == "Synthetic ontology A" and len(row) == len(count_header))
        weighted_header = next(row for row in table_rows if any("denominator" in cell.casefold() for cell in row))
        weighted_row = next(row for row in table_rows if row[0] == "Synthetic ontology A" and len(row) == len(weighted_header))
        counts = dict(zip(count_header, count_row)); weighted = dict(zip(weighted_header, weighted_row))
        self.assertEqual(next(value for key, value in counts.items() if "applicable" in key.casefold()), "1/2")
        self.assertEqual(float(next(value for key, value in counts.items() if "strict coverage" in key.casefold()).removesuffix("%")), 50)
        self.assertEqual(float(next(value for key, value in weighted.items() if "coverage" in key.casefold()).removesuffix("%")), 90)
        self.assertEqual(float(next(value for key, value in weighted.items() if "denominator" in key.casefold())), 10)
        self.assertEqual(report, before)

    def test_markdown_empty_applicable_suite_has_no_weighted_percentage(self):
        self.make_cases(0)
        text = coverage.render_markdown(self.evaluate())
        rows = [[cell.strip() for cell in line.strip().strip("|").split("|")] for line in text.splitlines() if line.startswith("| ")]
        header = next(row for row in rows if any("denominator" in cell.casefold() for cell in row))
        row = next(row for row in rows if row[0] == "Synthetic ontology A" and len(row) == len(header))
        values = dict(zip(header, row))
        self.assertEqual(next(value for key, value in values.items() if "coverage" in key.casefold()), "not evaluable")
        self.assertEqual(next(value for key, value in values.items() if "denominator" in key.casefold()), "0")

    def test_required_failure_blocks_even_when_total_is_ninety(self):
        self.payload["suite"]["cases"][-1]["required"] = True
        self.payload["candidates"][0]["assessments"][-1] = self.assessment("C9", "fail")
        self.install_conflict_review(scope_difference=True)
        c = self.candidate()
        self.assertEqual(c["summary"]["strict_coverage_percent"], 90)
        self.assertEqual(c["required_cases_not_fully_covered"], ["C9"])
        self.assertEqual(c["readiness"], "blocked_by_required_cases")

    def test_global_justified_exclusion_is_common_to_candidates(self):
        self.payload["suite"]["cases"][-1].update(applicable=False, exclusion_reason="Outside the declared scope")
        other = copy.deepcopy(self.payload["candidates"][0]);other["id"] = "candidate:B"
        self.payload["candidates"].append(other)
        report = self.evaluate()
        self.assertEqual([c["summary"]["applicable_cases"] for c in report["candidates"]], [9, 9])
        self.assertEqual([c["excluded_cases"][0]["id"] for c in report["candidates"]], ["C9", "C9"])

    def test_candidate_specific_na_is_rejected(self):
        self.payload["candidates"][0]["assessments"][-1]["status"] = "not_applicable"
        with self.assertRaises(core.EngineError):self.evaluate()

    def test_unjustified_or_required_exclusions_are_rejected(self):
        for variant in [{"applicable": False}, {"applicable": False, "exclusion_reason": "Scope", "required": True}]:
            with self.subTest(variant=variant):
                original = copy.deepcopy(self.payload["suite"]["cases"][-1])
                self.payload["suite"]["cases"][-1].update(variant)
                with self.assertRaises(core.EngineError):self.evaluate()
                self.payload["suite"]["cases"][-1] = original

    def test_zero_applicable_cases_has_no_percentage(self):
        self.make_cases(0)
        s = self.summary()
        self.assertEqual(s["applicable_cases"], 0)
        self.assertIsNone(s["strict_coverage_percent"])
        self.assertIsNone(s["not_fully_covered_percent"])
        self.assertIsNone(s["weighted_strict_coverage_percent"])

    def test_duplicate_case_observation_and_candidate_ids_rejected(self):
        for key in ("case", "assessment", "candidate"):
            with self.subTest(key=key):
                original = copy.deepcopy(self.payload)
                if key == "case":self.payload["suite"]["cases"].append(copy.deepcopy(self.payload["suite"]["cases"][0]))
                elif key == "assessment":self.payload["candidates"][0]["assessments"].append(copy.deepcopy(self.payload["candidates"][0]["assessments"][0]))
                else:self.payload["candidates"].append(copy.deepcopy(self.payload["candidates"][0]))
                with self.assertRaises(core.EngineError):self.evaluate()
                self.payload = original

    def test_unknown_case_and_invalid_weights_rejected(self):
        for weight in (0, -1, True, "9"):
            with self.subTest(weight=weight):
                self.payload["suite"]["cases"][0]["weight"] = weight
                with self.assertRaises(core.EngineError):self.evaluate()
        self.payload["suite"]["cases"][0]["weight"] = 1
        self.payload["candidates"][0]["assessments"][0]["case_id"] = "not-registered"
        with self.assertRaises(core.EngineError):self.evaluate()

    def test_case_kinds_have_independent_denominators(self):
        self.payload["suite"]["cases"][0]["kind"] = "formal"
        self.payload["candidates"][0]["assessments"][0] = self.assessment("C0", "fail")
        c = self.candidate()
        self.assertEqual(c["by_kind"]["formal"]["applicable_cases"], 1)
        self.assertEqual(c["by_kind"]["formal"]["strict_coverage_percent"], 0)
        self.assertEqual(c["by_kind"]["competency"]["applicable_cases"], 9)

    def test_markdown_exposes_residual_expected_observed_and_action(self):
        self.payload["candidates"][0]["assessments"][-1] = self.assessment("C9", "fail")
        text = coverage.render_markdown(self.evaluate())
        for value in ("90.0%", "C9", "Expected behavior 9", "Synthetic observation for C9", "Review or execute this synthetic case"):
            self.assertIn(value, text)


class EvidenceConflictTests(CoverageFixture):
    def test_changed_ontology_artifact_is_rejected(self):
        self.ontology.write_text("changed", encoding="utf-8")
        with self.assertRaises(core.EngineError) as error:self.evaluate()
        self.assertEqual(error.exception.code, "STALE_ARTIFACT")

    def test_assessment_for_other_ontology_is_rejected(self):
        self.payload["candidates"][0]["assessments"][0]["ontology_sha256"] = "other"
        with self.assertRaises(core.EngineError) as error:self.evaluate()
        self.assertEqual(error.exception.code, "STALE_ASSESSMENT")

    def test_claimed_pass_requires_evidence(self):
        row = self.payload["candidates"][0]["assessments"][0]
        for field in ("evidence", "evidence_mode"):
            old = row.pop(field)
            with self.subTest(field=field), self.assertRaises(core.EngineError):self.evaluate()
            row[field] = old

    def test_executed_result_hash_is_pinned(self):
        result = self.write("measurement.json", {"synthetic": "pass"})
        row = self.payload["candidates"][0]["assessments"][0]
        row.update(evidence_mode="executed", result_artifact=result.name, result_sha256=hashfile(result))
        self.assertEqual(self.summary()["strict_coverage_percent"], 100)
        result.write_text("modified", encoding="utf-8")
        with self.assertRaises(core.EngineError):self.evaluate()

    def test_all_active_decision_states_block_linked_passes(self):
        for status in ("open", "deferred", "decision_recorded_pending_validation"):
            with self.subTest(status=status):
                self.payload["candidates"][0]["assessments"][0].pop("conflict_ids", None)
                review = self.install_conflict_review(status)
                self.payload["candidates"][0]["assessments"][0]["conflict_ids"] = [review["findings"][0]["id"]]
                c = self.candidate();row = c["cases"][0]
                self.assertEqual(row["reported_status"], "pass")
                self.assertEqual(row["effective_status"], "conflicted")
                self.assertEqual(c["summary"]["strict_coverage_percent"], 90)
                self.assertEqual(c["readiness"], "blocked_by_conflicts")

    def test_global_unlinked_conflict_remains_visible_at_ninety_percent(self):
        self.install_conflict_review()
        self.payload["candidates"][0]["assessments"][-1] = self.assessment("C9", "fail")
        c = self.candidate()
        self.assertEqual(c["summary"]["strict_coverage_percent"], 90)
        self.assertEqual(c["conflict_review"]["open_count"], 1)
        self.assertEqual(c["readiness"], "blocked_by_conflicts")
        text = coverage.render_markdown(self.evaluate())
        self.assertIn("claim:A", text);self.assertIn("claim:B", text)
        self.assertIn("synthetic#A", text);self.assertIn("synthetic#B", text)

    def test_scope_difference_does_not_block_linked_pass(self):
        review = self.install_conflict_review(scope_difference=True)
        self.payload["candidates"][0]["assessments"][0]["conflict_ids"] = [review["findings"][0]["id"]]
        c = self.candidate()
        self.assertEqual(c["cases"][0]["effective_status"], "pass")
        self.assertEqual(c["conflict_review"]["open_count"], 0)
        self.assertEqual(c["readiness"], "covered_on_declared_suite")

    def test_missing_or_incomplete_scan_is_not_assessed(self):
        self.assertEqual(self.candidate()["readiness"], "conflicts_not_assessed")
        path = self.write("incomplete.json", {"scan_status": "incomplete"})
        self.payload["candidates"][0]["conflict_review"] = {"artifact": path.name, "sha256": hashfile(path), "ontology_sha256": self.ontology_hash}
        c = self.candidate()
        self.assertEqual(c["conflict_review"]["scan_status"], "incomplete")
        self.assertEqual(c["readiness"], "conflicts_not_assessed")

    def test_stale_conflict_binding_and_tampered_card_rejected(self):
        review = self.install_conflict_review()
        binding = self.payload["candidates"][0]["conflict_review"]
        binding["ontology_sha256"] = "other"
        with self.assertRaises(core.EngineError):self.evaluate()
        binding["ontology_sha256"] = self.ontology_hash
        review["findings"][0]["assertions"][0]["evidence"][0]["original_excerpt"] = "tampered"
        path = self.write("conflict-review.json", review);binding["sha256"] = hashfile(path)
        with self.assertRaises(core.EngineError) as error:self.evaluate()
        self.assertEqual(error.exception.code, "STALE_CONFLICT")

    def test_conflict_file_hash_and_unknown_conflict_ids_rejected(self):
        self.install_conflict_review()
        self.payload["candidates"][0]["conflict_review"]["sha256"] = "wrong"
        with self.assertRaises(core.EngineError):self.evaluate()
        self.payload["candidates"][0].pop("conflict_review")
        self.payload["candidates"][0]["assessments"][0]["conflict_ids"] = ["missing"]
        with self.assertRaises(core.EngineError):self.evaluate()

    def test_unverified_resolved_finding_state_is_rejected(self):
        review = self.install_conflict_review()
        review["findings"][0]["status"] = "resolved"
        path = self.write("conflict-review.json", review)
        self.payload["candidates"][0]["conflict_review"]["sha256"] = hashfile(path)
        with self.assertRaises(core.EngineError):self.evaluate()

    def test_formal_axes_are_separate_and_inconsistency_blocks(self):
        self.pin_formal("owl_consistency", "inconsistent")
        self.pin_formal("shacl", "conformant")
        c = self.candidate()
        self.assertEqual(c["summary"]["strict_coverage_percent"], 100)
        self.assertEqual(c["readiness"], "blocked_by_formal_check")
        self.assertEqual(c["formal_checks"]["owl_consistency"]["status"], "inconsistent")
        self.assertEqual(c["formal_checks"]["shacl"]["status"], "conformant")

    def test_formal_error_and_other_ontology_receipt_are_not_passes(self):
        self.pin_formal("shacl", "error")
        self.assertEqual(self.candidate()["readiness"], "blocked_by_formal_check")
        self.payload["candidates"][0]["formal_checks"]["shacl"]["ontology_sha256"] = "other"
        with self.assertRaises(core.EngineError):self.evaluate()

    def test_unexecuted_formal_checks_stay_not_checked(self):
        c = self.candidate()
        self.assertEqual(c["formal_checks"]["owl_consistency"]["status"], "not_checked")
        self.assertEqual(c["formal_checks"]["shacl"]["status"], "not_checked")


class ProgressTests(CoverageFixture):
    def test_previous_report_retains_historical_noninteger_percentages(self):
        self.make_cases(3)
        self.payload["candidates"][0]["assessments"][-1] = self.assessment("C2", "fail")
        previous = self.evaluate()
        self.assertEqual(previous["candidates"][0]["summary"]["strict_coverage_percent"], 66.66666666666667)
        self.assertEqual(self.evaluate(previous)["comparison"]["status"], "comparable")

    def test_previous_summary_does_not_accept_boolean_in_place_of_count(self):
        self.make_cases(1)
        previous = self.evaluate()
        previous["candidates"][0]["summary"]["applicable_cases"] = True
        with self.assertRaises(core.EngineError) as error:
            self.evaluate(previous)
        self.assertEqual(error.exception.code, "STALE_PREVIOUS_REPORT")

    def test_previous_case_weight_does_not_accept_boolean_coercion(self):
        previous = self.evaluate()
        previous["candidates"][0]["cases"][0]["weight"] = True
        with self.assertRaises(core.EngineError):
            self.evaluate(previous)

    def test_same_suite_records_improvements_and_regressions_across_ontology_hashes(self):
        self.payload["candidates"][0]["assessments"][0] = self.assessment("C0", "fail")
        old = self.evaluate()
        self.ontology.write_text('{"synthetic":true,"version":"2"}', encoding="utf-8")
        self.ontology_hash = hashfile(self.ontology)
        self.payload["candidates"][0]["ontology"].update(version="2", sha256=self.ontology_hash)
        self.payload["candidates"][0]["assessments"] = [self.assessment("C" + str(i), "fail" if i == 1 else "pass") for i in range(10)]
        report = self.evaluate(old);change = report["comparison"]["candidates"][0]
        self.assertEqual(change["status"], "comparable")
        self.assertEqual(change["newly_fully_covered"], ["C0"])
        self.assertEqual(change["regressions"], ["C1"])
        self.assertEqual(change["change_percentage_points"], 0)
        self.assertNotEqual(change["before_ontology"]["sha256"], change["after_ontology"]["sha256"])

    def test_changed_suite_is_not_comparable(self):
        old = self.evaluate()
        self.payload["suite"]["version"] = "2"
        self.payload["suite"]["cases"][0]["expected"] = "Different obligation"
        comparison = self.evaluate(old)["comparison"]
        self.assertEqual(comparison["status"], "not_comparable")
        self.assertNotIn("candidates", comparison)

    def test_new_and_removed_candidates_are_explicit(self):
        old = self.evaluate()
        self.payload["candidates"][0]["id"] = "candidate:B"
        result = self.evaluate(old)["comparison"]
        self.assertEqual(result["removed_candidate_ids"], ["candidate:A"])
        self.assertEqual(result["candidates"][0]["status"], "new_candidate")


class CliTests(CoverageFixture):
    def test_weight_total_overflow_has_json_error_and_no_partial_report(self):
        self.make_cases(2)
        for case in self.payload["suite"]["cases"]:
            case["weight"] = 1e308
        report = self.root / "overflow-report.json"
        result, output = self.run_cli(["--report", report], expected=2)
        self.assertNotIn("Traceback", result.stderr)
        self.assertEqual(output["status"], "error")
        self.assertEqual(output["errors"][0]["code"], "NUMERIC_OVERFLOW")
        self.assertFalse(report.exists())

    def test_ninety_percent_is_successful_measurement_not_acceptance(self):
        self.payload["candidates"][0]["assessments"][-1] = self.assessment("C9", "fail")
        result, output = self.run_cli(["--report", self.root / "report.json", "--markdown", self.root / "report.md"])
        self.assertEqual(output["status"], "completed")
        report = json.loads((self.root / "report.json").read_text())
        self.assertEqual(report["candidates"][0]["summary"]["strict_coverage_percent"], 90)
        self.assertIn("90.0%", (self.root / "report.md").read_text(encoding="utf-8"))

    def test_reports_cannot_overwrite_inputs_ontology_or_measurement(self):
        measured = self.write("result.json", {"fixture": True})
        self.payload["candidates"][0]["assessments"][0].update(evidence_mode="executed", result_artifact=measured.name, result_sha256=hashfile(measured))
        for output in (self.root / "input.json", self.ontology, measured):
            with self.subTest(output=output):
                _, result = self.run_cli(["--report", output], expected=2)
                self.assertEqual(result["status"], "error")

    def test_reports_cannot_overwrite_pinned_conflict_or_formal_report(self):
        self.install_conflict_review()
        formal = self.pin_formal("shacl", "conformant")
        for output in (self.root / "conflict-review.json", formal):
            with self.subTest(output=output):self.run_cli(["--report", output], expected=2)

    def test_hardlink_aliases_of_ontology_and_input_are_protected(self):
        input_file = self.write("input.json", self.payload)
        for i, source in enumerate((input_file, self.ontology)):
            alias = self.root / ("alias-" + str(i) + ".json")
            os.link(source, alias)
            with self.subTest(source=source):self.run_cli(["--report", alias], expected=2)

    def test_existing_outputs_and_colliding_outputs_are_preserved(self):
        output = self.write("existing.json", {"previous": True})
        self.run_cli(["--report", output], expected=2)
        self.run_cli(["--report", self.root / "same.json", "--markdown", self.root / "same.json"], expected=2)
        self.assertFalse((self.root / "same.json").exists())

    def test_malformed_statuses_are_structured_errors(self):
        original = copy.deepcopy(self.payload)
        for value in ([], {}, True, "not-applicable"):
            with self.subTest(value=value):
                self.payload = copy.deepcopy(original)
                self.payload["candidates"][0]["assessments"][0]["status"] = value
                self.run_cli(expected=2)

    def test_unsupported_time_field_is_not_silently_accepted(self):
        self.payload["candidates"][0]["assessments"][0]["timestamp"] = "yesterday"
        self.run_cli(expected=2)

    def test_malformed_completed_conflict_review_is_structured_error(self):
        path = self.write("bad-review.json", {"scan_status": "completed"})
        self.payload["candidates"][0]["conflict_review"] = {"artifact": path.name, "sha256": hashfile(path), "ontology_sha256": self.ontology_hash}
        self.run_cli(expected=2)

    def test_malformed_previous_report_is_structured_error(self):
        current = self.evaluate()
        previous = self.write("previous.json", {"schema_version": "1", "suite_fingerprint": current["suite_fingerprint"], "candidates": [{}]})
        self.run_cli(["--previous", previous, "--report", self.root / "report.json"], expected=2)


if __name__ == "__main__":
    receipt = None
    if "--receipt" in sys.argv:
        i = sys.argv.index("--receipt")
        receipt = Path(sys.argv[i + 1]).resolve()
        del sys.argv[i:i + 2]
    tracked = [HELPER, HERE / "semantic_model.py", HERE / "review_conflicts.py"]
    before = {p.name: hashfile(p) for p in tracked}
    program = unittest.main(verbosity=2, exit=False)
    result = program.result
    after = {p.name: hashfile(p) for p in tracked}
    if receipt:
        data = {"status": "passed" if result.wasSuccessful() and before == after else "failed", "checked_at_utc": datetime.now(timezone.utc).isoformat(), "tests_run": result.testsRun,
                "failures": [{"test": str(t), "traceback": text} for t, text in result.failures], "errors": [{"test": str(t), "traceback": text} for t, text in result.errors], "skipped": [{"test": str(t), "reason": reason} for t, reason in result.skipped],
                "source_sha256_before": before, "source_sha256_after": after, "sources_unchanged_during_run": before == after, "test_sha256": hashfile(Path(__file__)),
                "scope": "Synthetic recorded-result aggregation, fixed denominators, residuals, evidence identity, conflict bindings, progress and immutable CLI inputs. No ontology truth, reasoner correctness or semantic completeness certification."}
        receipt.parent.mkdir(parents=True, exist_ok=True)
        receipt.write_text(json.dumps(data, indent=2), encoding="utf-8")
    raise SystemExit(0 if result.wasSuccessful() and before == after else 1)
