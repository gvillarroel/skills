#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Observable conflict detection, evidence, decisions and immutable I/O tests.

Run: python -B test_review_conflicts.py --receipt /path/to/qa.json
Fixtures and CLI artifacts use TemporaryDirectory; no services or model calls.
Python 3.11+, standard library only.
"""
import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timezone

HERE = Path(__file__).resolve().parent
CORE = HERE / "semantic_model.py"
HELPER = HERE / "review_conflicts.py"
sys.path.insert(0, str(HERE))
spec = importlib.util.spec_from_file_location("conflicts_under_test", HELPER)
helper = importlib.util.module_from_spec(spec)
spec.loader.exec_module(helper)


def fixture():
    contract = {"schema_version": "1", "id": "test-conflicts", "version": "1",
                "types": {"Entity": {"attributes": {}, "closed_attributes": True}},
                "relations": {}, "require_source_bindings": True, "checks": []}
    sources = [{"id": "source:" + x, "locator": "fixture#" + x,
                "text": "Original evidence " + x, "selected": x == "A"} for x in "ABC"]
    model = {"schema_version": "1", "contract_id": contract["id"], "contract_version": "1",
             "sources": sources,
             "nodes": [{"id": x, "type": "Entity", "label": x, "definition": "Entity " + x,
                        "source_ids": ["source:" + x]} for x in "ABC"],
             "relations": [], "bindings": {"source:" + x: [x] for x in "ABC"}}
    return contract, model


def assertion(aid, source, value="enabled", polarity="positive", scope=None, reviewed=True):
    record = {"id": aid, "subject": "A", "predicate": "supports_sso", "value": value,
              "polarity": polarity, "source_ids": [source],
              "scope": copy.deepcopy(scope if scope is not None else {
                  "context": "production", "version": "v1", "unit": "state",
                  "time": {"kind": "all_time"}}),
              "normalization": {"status": "reviewed", "reviewer": "human:test",
                                "rationale": "Explicit fixture normalization only."} if reviewed else {"status": "unreviewed"}}
    return record


def payload(left=None, right=None, functional=False):
    return {"schema_version": "1", "functional_predicates": ["supports_sso"] if functional else [],
            "assertions": [left or assertion("claim:A", "source:A"),
                           right or assertion("claim:B", "source:B", polarity="negative")]}


def relation(rid, predicate, left="A", right="B", source="source:A"):
    return {"id": rid, "type": predicate, "from": left, "to": right, "source_ids": [source]}


def rules(contract, *names):
    for name in names:
        contract["relations"][name] = {"from_types": ["Entity"], "to_types": ["Entity"]}


def decision_input(review, choice="prefer_assertion", assertion_id="claim:A"):
    card = review["findings"][0]
    record = {"conflict_id": card["id"], "fingerprint": card["fingerprint"],
              "choice": choice, "reviewer": "human:test", "rationale": "Explicit fixture choice, not automatic truth."}
    if choice == "prefer_assertion":
        record["assertion_id"] = assertion_id
    return {"schema_version": "1", "review_revision": review["review_revision"], "decisions": [record]}


class ScanTests(unittest.TestCase):
    def setUp(self):
        self.contract, self.model = fixture()

    def scan(self, claims=None):
        before = copy.deepcopy((self.model, self.contract, claims))
        result = helper.scan(self.model, self.contract, claims)
        self.assertEqual((self.model, self.contract, claims), before)
        return result

    def test_explicit_reviewed_opposition_is_grounded_and_not_auto_resolved(self):
        result = self.scan(payload())
        self.assertEqual(result["scan_status"], "completed")
        self.assertEqual(result["counts"]["requires_user_decision"], 1)
        item = result["findings"][0]
        self.assertEqual(item["classification"], "confirmed_conflict")
        self.assertEqual(item["status"], "open")
        self.assertIsNone(item["resolution"])
        self.assertEqual({x["id"] for x in item["assertions"]}, {"claim:A", "claim:B"})
        self.assertEqual({x["evidence"][0]["source_id"] for x in item["assertions"]}, {"source:A", "source:B"})
        self.assertTrue(all(x["evidence"][0]["locator"] and x["evidence"][0]["original_excerpt"] for x in item["assertions"]))

    def test_unreviewed_normalization_is_only_possible(self):
        claims = payload(right=assertion("claim:B", "source:B", polarity="negative", reviewed=False))
        result = self.scan(claims)
        self.assertEqual(result["findings"][0]["classification"], "possible_conflict")
        self.assertIn("normalization_needs_review", result["findings"][0]["scope_notes"])

    def test_reviewed_normalization_needs_actual_reviewer_and_rationale(self):
        for field in ("reviewer", "rationale"):
            with self.subTest(field=field):
                claims = payload()
                del claims["assertions"][0]["normalization"][field]
                with self.assertRaises(helper.core.EngineError):
                    self.scan(claims)

    def test_functional_values_conflict_and_multivalue_values_do_not(self):
        a = assertion("claim:A", "source:A", value="active")
        b = assertion("claim:B", "source:B", value="inactive")
        self.assertEqual(self.scan(payload(a, b, True))["findings"][0]["classification"], "confirmed_conflict")
        self.assertEqual(self.scan(payload(a, b, False))["findings"], [])

    def test_two_negative_different_values_are_not_conflicting(self):
        a = assertion("claim:A", "source:A", value="a", polarity="negative")
        b = assertion("claim:B", "source:B", value="b", polarity="negative")
        self.assertEqual(self.scan(payload(a, b, True))["findings"], [])

    def test_unknown_null_is_not_negative_evidence(self):
        claims = payload(left=assertion("claim:A", "source:A", value=None))
        result = self.scan(claims)
        self.assertEqual(result["findings"], [])
        self.assertEqual(result["warnings"][0]["code"], "UNKNOWN_VALUE_NOT_NEGATION")

    def test_numeric_equivalence_does_not_create_functional_conflict(self):
        claims = payload(assertion("claim:A", "source:A", 1), assertion("claim:B", "source:B", 1.0), True)
        self.assertEqual(self.scan(claims)["findings"], [])

    def test_different_contexts_or_versions_are_scope_differences(self):
        for field in ("context", "version"):
            with self.subTest(field=field):
                claims = payload()
                claims["assertions"][1]["scope"][field] = "other"
                result = self.scan(claims)
                self.assertEqual(result["findings"][0]["classification"], "scope_difference")
                self.assertEqual(result["counts"]["requires_user_decision"], 0)

    def test_unknown_context_or_one_missing_version_is_possible(self):
        for field in ("context", "version"):
            with self.subTest(field=field):
                claims = payload()
                del claims["assertions"][1]["scope"][field]
                self.assertEqual(self.scan(claims)["findings"][0]["classification"], "possible_conflict")

    def test_different_numeric_units_need_comparison(self):
        claims = payload(assertion("claim:A", "source:A", 60), assertion("claim:B", "source:B", 1), True)
        claims["assertions"][0]["scope"]["unit"] = "seconds"
        claims["assertions"][1]["scope"]["unit"] = "minutes"
        item = self.scan(claims)["findings"][0]
        self.assertEqual(item["classification"], "possible_conflict")
        self.assertIn("unit_comparison_required", item["scope_notes"])

    def test_unknown_numeric_unit_needs_review(self):
        claims = payload(assertion("claim:A", "source:A", 1), assertion("claim:B", "source:B", 2), True)
        for a in claims["assertions"]:
            del a["scope"]["unit"]
        self.assertEqual(self.scan(claims)["findings"][0]["classification"], "possible_conflict")

    def test_disjoint_intervals_can_coexist_and_touching_intervals_overlap(self):
        claims = payload()
        claims["assertions"][0]["scope"]["time"] = {"kind": "interval", "from": "2026-01-01", "to": "2026-01-31"}
        claims["assertions"][1]["scope"]["time"] = {"kind": "interval", "from": "2026-02-01", "to": None}
        self.assertEqual(self.scan(claims)["findings"][0]["classification"], "scope_difference")
        claims["assertions"][1]["scope"]["time"]["from"] = "2026-01-31"
        self.assertEqual(self.scan(claims)["findings"][0]["classification"], "confirmed_conflict")

    def test_unknown_time_is_possible(self):
        claims = payload()
        claims["assertions"][0]["scope"]["time"] = {"kind": "unknown"}
        self.assertEqual(self.scan(claims)["findings"][0]["classification"], "possible_conflict")

    def test_explicit_null_time_does_not_crash_or_confirm(self):
        claims = payload()
        claims["assertions"][0]["scope"]["time"] = None
        try:
            result = self.scan(claims)
        except helper.core.EngineError:
            return  # Rejection is also a safe, explicit policy for null time.
        self.assertEqual(result["findings"][0]["classification"], "possible_conflict")

    def test_invalid_iso_interval_rejected(self):
        for value in ("2026-99-01", "2026-1-01", 3):
            with self.subTest(value=value):
                claims = payload()
                claims["assertions"][0]["scope"]["time"] = {"kind": "interval", "from": value, "to": None}
                with self.assertRaises(helper.core.EngineError):
                    self.scan(claims)

    def test_scope_changes_change_review_revision(self):
        first = self.scan(payload())
        claims = payload()
        claims["assertions"][0]["scope"]["version"] = "v2"
        self.assertNotEqual(first["review_revision"], self.scan(claims)["review_revision"])

    def test_exclusions_are_deduplicated_with_both_relation_ids_and_sources(self):
        rules(self.contract, "same", "different")
        self.contract["relations"]["same"].update(symmetric=True, exclusive_with=["different"])
        self.contract["relations"]["different"].update(symmetric=True, exclusive_with=["same"])
        self.model["relations"] = [relation("r:1", "same", source="source:A"), relation("r:2", "different", "B", "A", "source:B")]
        report = self.scan()
        self.assertEqual(len(report["findings"]), 1)
        item = report["findings"][0]
        self.assertEqual(item["classification"], "constraint_conflict")
        self.assertEqual({r["id"] for r in item["assertions"]}, {"r:1", "r:2"})
        self.assertEqual({r["evidence"][0]["source_id"] for r in item["assertions"]}, {"source:A", "source:B"})

    def test_dag_cycle_shows_all_witness_edges(self):
        rules(self.contract, "broader")
        self.contract["relations"]["broader"]["acyclic"] = True
        self.model["relations"] = [relation("AB", "broader"), relation("BC", "broader", "B", "C", "source:B"), relation("CA", "broader", "C", "A", "source:C")]
        item = self.scan()["findings"][0]
        self.assertEqual(item["rule"]["id"], "acyclic")
        self.assertEqual({x["id"] for x in item["assertions"]}, {"AB", "BC", "CA"})

    def test_non_dag_cycle_is_not_reported_as_contradiction(self):
        rules(self.contract, "related")
        self.model["relations"] = [relation("AB", "related"), relation("BA", "related", "B", "A")]
        self.assertEqual(self.scan()["findings"], [])

    def test_cardinality_conflict_shows_node_and_involved_edges(self):
        rules(self.contract, "owns")
        self.contract["types"]["Entity"]["outgoing"] = {"owns": {"max": 1}}
        self.model["relations"] = [relation("AB", "owns"), relation("AC", "owns", "A", "C", "source:B")]
        item = self.scan()["findings"][0]
        self.assertEqual(item["rule"]["id"], "cardinality")
        self.assertEqual(item["rule"]["actual"], 2)
        self.assertEqual({x["id"] for x in item["assertions"]}, {"A", "AB", "AC"})

    def test_invalid_model_is_incomplete_not_empty_success(self):
        self.model["nodes"][0]["definition"] = ""
        report = self.scan(payload())
        self.assertEqual(report["scan_status"], "incomplete")
        self.assertEqual(report["semantic_status"], "not_run")

    def test_competency_failure_is_not_silently_successful_conflict_scan(self):
        self.contract["checks"] = [{"id": "missing", "query": {"op": "nodes_of_type", "type": "Entity"}, "expect": ["absent"]}]
        report = self.scan()
        self.assertTrue(report["scan_status"] != "completed" or report["findings"], "Invalid competency expectation must be visible as a finding or incomplete scan")

    def test_competency_check_identifier_preserves_slashes(self):
        check_id = "https://example.invalid/checks/selection/source-A"
        self.contract["checks"] = [{"id": check_id, "query": {"op": "bindings", "source_id": "source:A"}, "expect": ["B"]}]
        report = self.scan()
        item = report["findings"][0]
        self.assertEqual(item["rule"]["check_id"], check_id)
        self.assertEqual(item["assertions"][0]["id"], "check:" + check_id)
        self.assertEqual(item["status"], "open")

    def test_cardinality_preserves_full_iri_predicate_and_subject(self):
        predicate = "https://example.invalid/vocabulary/hasPart"
        subject = "https://example.invalid/items/A"
        rules(self.contract, predicate)
        self.contract["types"]["Entity"]["outgoing"] = {predicate: {"max": 1}}
        self.model["nodes"][0]["id"] = subject
        self.model["bindings"]["source:A"] = [subject]
        self.model["relations"] = [relation("r/AB", predicate, subject, "B"), relation("r/AC", predicate, subject, "C", "source:B")]
        item = self.scan()["findings"][0]
        self.assertEqual(item["rule"]["predicate"], predicate)
        self.assertEqual({a["id"] for a in item["assertions"]}, {subject, "r/AB", "r/AC"})

    def test_missing_required_relation_review_remains_actionable(self):
        rules(self.contract, "equivalent")
        self.contract["relations"]["equivalent"]["review_required"] = True
        self.model["relations"] = [relation("r:unreviewed", "equivalent")]
        report = self.scan()
        self.assertEqual(report["validation"]["contract_status"], "invalid")
        self.assertEqual(report["counts"]["requires_user_decision"], 1)
        item = report["findings"][0]
        self.assertEqual(item["classification"], "constraint_conflict")
        self.assertEqual(item["rule"]["id"], "review_required")
        self.assertEqual(item["assertions"][0]["id"], "r:unreviewed")
        self.assertIsNone(item["resolution"])
        self.assertIn("request_evidence", {o["choice"] for o in item["resolution_options"]})

    def test_claim_evidence_and_subject_must_exist(self):
        for key, value in [("subject", "missing"), ("source_ids", ["missing"])]:
            with self.subTest(key=key):
                claims = payload()
                claims["assertions"][0][key] = value
                with self.assertRaises(helper.core.EngineError):
                    self.scan(claims)

    def test_json_markdown_shows_both_assertions_sources_and_options(self):
        result = self.scan(payload())
        text = helper.render_markdown(result)
        for value in ("claim:A", "claim:B", "source:A", "source:B", "fixture#A", "fixture#B", "Original evidence A", "Original evidence B", "prefer_assertion", "defer"):
            self.assertIn(value, text)
        json.dumps(result, allow_nan=False)

    def test_markdown_surfaces_actual_unknown_warning_without_negation(self):
        unknown_id = "claim:unmeasured/retention"
        claims = payload(assertion(unknown_id, "source:A", value=None), assertion("claim:known", "source:B", value="enabled"))
        result = self.scan(claims)
        before = copy.deepcopy(result)
        text = helper.render_markdown(result)
        warning_lines = [line for line in text.splitlines() if "UNKNOWN_VALUE_NOT_NEGATION" in line]
        self.assertEqual(len(warning_lines), 1)
        self.assertIn(unknown_id, warning_lines[0])
        self.assertRegex(warning_lines[0].casefold(), r"unknown.*not.*negation")
        self.assertEqual(result["findings"], [])
        self.assertEqual(result, before)

    def test_markdown_explains_nonfunctional_multivalues_without_inventing_warnings(self):
        claims = payload(assertion("claim:east", "source:A", value="east"), assertion("claim:west", "source:B", value="west"))
        result = self.scan(claims)
        text = helper.render_markdown(result)
        self.assertEqual(result["findings"], [])
        self.assertEqual(result["warnings"], [])
        self.assertRegex(text.casefold(), r"positive.*coexist.*not.*functional")
        self.assertNotIn("UNKNOWN_VALUE_NOT_NEGATION", text)


class DecisionTests(unittest.TestCase):
    def setUp(self):
        self.contract, self.model = fixture()
        self.review = helper.scan(self.model, self.contract, payload())

    def test_prefer_only_records_explicit_choice_and_keeps_evidence(self):
        original = copy.deepcopy((self.model, self.review))
        result = helper.record_decisions(self.review, decision_input(self.review))
        item = result["findings"][0]
        self.assertEqual(item["status"], "decision_recorded_pending_validation")
        self.assertEqual(item["resolution"]["assertion_id"], "claim:A")
        self.assertEqual(len(item["assertions"]), 2)
        self.assertFalse(result["models_modified"])
        self.assertEqual((self.model, self.review), original)
        self.assertNotEqual(item["status"], "resolved")

    def test_defer_and_request_evidence_keep_pending(self):
        for choice in ("defer", "request_evidence"):
            with self.subTest(choice=choice):
                result = helper.record_decisions(self.review, decision_input(self.review, choice))
                self.assertEqual(result["findings"][0]["status"], "deferred")
                self.assertIsNotNone(result["findings"][0]["resolution"])

    def test_no_decisions_do_not_choose_automatically(self):
        data = {"schema_version": "1", "review_revision": self.review["review_revision"], "decisions": []}
        result = helper.record_decisions(self.review, data)
        self.assertEqual(result["findings"][0]["status"], "open")
        self.assertIsNone(result["findings"][0]["resolution"])

    def test_scope_and_correction_choices_need_details(self):
        for choice in ("separate_scopes", "correct_assertions"):
            with self.subTest(choice=choice):
                with self.assertRaises(helper.core.EngineError):
                    helper.record_decisions(self.review, decision_input(self.review, choice))
        data = decision_input(self.review, "separate_scopes")
        data["decisions"][0]["proposed_scopes"] = {"claim:A": {"context": "production"}, "claim:B": {"context": "test"}}
        self.assertEqual(helper.record_decisions(self.review, data)["findings"][0]["status"], "decision_recorded_pending_validation")

    def test_separate_scopes_requires_a_real_discriminator(self):
        for scopes in ({"claim:A": {}, "claim:B": {}},
                       {"claim:A": {"context": "same"}, "claim:B": {"context": "same"}},
                       {"claim:A": {"unit": "seconds"}, "claim:B": {"unit": "minutes"}}):
            with self.subTest(scopes=scopes):
                data = decision_input(self.review, "separate_scopes")
                data["decisions"][0]["proposed_scopes"] = scopes
                with self.assertRaises(helper.core.EngineError):
                    helper.record_decisions(self.review, data)

    def test_reviewer_rationale_and_selected_assertion_are_required(self):
        for field, value in [("reviewer", ""), ("rationale", ""), ("assertion_id", "missing")]:
            with self.subTest(field=field):
                data = decision_input(self.review)
                data["decisions"][0][field] = value
                with self.assertRaises(helper.core.EngineError):
                    helper.record_decisions(self.review, data)

    def test_stale_revision_and_fingerprint_rejected(self):
        for field in ("review_revision", "fingerprint"):
            with self.subTest(field=field):
                data = decision_input(self.review)
                target = data if field == "review_revision" else data["decisions"][0]
                target[field] = "obsolete"
                with self.assertRaises(helper.core.EngineError) as caught:
                    helper.record_decisions(self.review, data)
                self.assertIn(caught.exception.code, {"STALE_REVIEW", "STALE_CONFLICT"})

    def test_duplicate_decision_or_replacement_of_recorded_choice_rejected(self):
        data = decision_input(self.review)
        data["decisions"].append(copy.deepcopy(data["decisions"][0]))
        before = copy.deepcopy(self.review)
        with self.assertRaises(helper.core.EngineError):
            helper.record_decisions(self.review, data)
        self.assertEqual(self.review, before)
        result = helper.record_decisions(self.review, decision_input(self.review))
        with self.assertRaises(helper.core.EngineError):
            helper.record_decisions(result, decision_input(self.review))

    def test_unknown_choice_is_rejected(self):
        with self.assertRaises(helper.core.EngineError):
            helper.record_decisions(self.review, decision_input(self.review, "automatic-majority"))

    def test_changed_evidence_without_matching_fingerprint_is_rejected(self):
        changed = copy.deepcopy(self.review)
        changed["findings"][0]["assertions"][0]["evidence"][0]["original_excerpt"] = "Changed after scan"
        with self.assertRaises(helper.core.EngineError):
            helper.record_decisions(changed, decision_input(self.review))


class CliTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.contract_data, self.model_data = fixture()
        self.contract = self.write("contract.json", self.contract_data)
        self.model = self.write("model.json", self.model_data)
        self.claims = self.write("claims.json", payload())
        self.inputs = [self.contract, self.model, self.claims]
        self.snapshots = {p: p.read_bytes() for p in self.inputs}

    def tearDown(self):
        self.tmp.cleanup()

    def write(self, name, value):
        path = self.root / name
        path.write_text(json.dumps(value, ensure_ascii=False), encoding="utf-8")
        return path

    def run_cli(self, *args, expected=None):
        process = subprocess.run([sys.executable, "-B", str(HELPER), *map(str, args)], capture_output=True, text=True, encoding="utf-8")
        self.assertNotIn("Traceback", process.stderr)
        self.assertTrue(process.stdout.strip(), process.stderr)
        value = json.loads(process.stdout)
        if expected is not None:
            self.assertEqual(process.returncode, expected, (value, process.stderr))
        for path, original in self.snapshots.items():
            self.assertEqual(path.read_bytes(), original, str(path))
        return process.returncode, value

    def scan_args(self, report, markdown=None, claims=True):
        args = ["scan", "--model", self.model, "--contract", self.contract, "--report", report]
        if claims:
            args += ["--claims", self.claims]
        if markdown:
            args += ["--markdown", markdown]
        return args

    def test_scan_exit_one_and_files_contain_both_sides(self):
        report, markdown = self.root / "review.json", self.root / "review.md"
        self.run_cli(*self.scan_args(report, markdown), expected=1)
        text = markdown.read_text(encoding="utf-8")
        for key in ("claim:A", "claim:B", "Original evidence A", "Original evidence B"):
            self.assertIn(key, text)
        self.assertEqual(json.loads(report.read_text())["findings"][0]["status"], "open")

    def test_slash_check_id_cli_reports_a_grounded_case_without_traceback(self):
        check_id = "audit/checks/source/A"
        self.contract_data["checks"] = [{"id": check_id, "query": {"op": "bindings", "source_id": "source:A"}, "expect": ["B"]}]
        self.write(self.contract.name, self.contract_data)
        self.snapshots[self.contract] = self.contract.read_bytes()
        report = self.root / "slash-check-review.json"
        self.run_cli(*self.scan_args(report, claims=False), expected=1)
        item = json.loads(report.read_text(encoding="utf-8"))["findings"][0]
        self.assertEqual(item["rule"]["check_id"], check_id)

    def test_missing_required_review_cli_never_returns_empty_success(self):
        rules(self.contract_data, "equivalent")
        self.contract_data["relations"]["equivalent"]["review_required"] = True
        self.model_data["relations"] = [relation("r:unreviewed", "equivalent")]
        for path, value in [(self.contract, self.contract_data), (self.model, self.model_data)]:
            self.write(path.name, value)
            self.snapshots[path] = path.read_bytes()
        report = self.root / "missing-review.json"
        self.run_cli(*self.scan_args(report, claims=False), expected=1)
        result = json.loads(report.read_text(encoding="utf-8"))
        self.assertEqual(result["findings"][0]["rule"]["id"], "review_required")
        self.assertEqual(result["findings"][0]["status"], "open")

    def test_addition_previews_cross_boundary_conflict_without_staging_or_mutation(self):
        rules(self.contract_data, "same", "different")
        self.contract_data["relations"]["same"].update(symmetric=True, exclusive_with=["different"])
        self.contract_data["relations"]["different"].update(symmetric=True, exclusive_with=["same"])
        self.model_data["relations"] = [relation("old:same", "same", source="source:A")]
        self.contract.write_text(json.dumps(self.contract_data), encoding="utf-8")
        self.model.write_text(json.dumps(self.model_data), encoding="utf-8")
        self.snapshots.update({p: p.read_bytes() for p in (self.contract, self.model)})
        addition = self.write("addition.json", {"relations": [relation("new:different", "different", "B", "A", "source:B")]})
        self.snapshots[addition] = addition.read_bytes()
        report = self.root / "addition-review.json"
        self.run_cli(*self.scan_args(report, claims=False), "--addition", addition, expected=1)
        result = json.loads(report.read_text())
        self.assertEqual(len(result["findings"]), 1)
        self.assertEqual({a["id"] for a in result["findings"][0]["assertions"]}, {"old:same", "new:different"})
        self.assertEqual(len(self.model_data["relations"]), 1)
        link = self.root / "addition-hardlink.json"
        os.link(addition, link)
        self.run_cli(*self.scan_args(link, claims=False), "--addition", addition, expected=2)

    def test_competency_failure_cli_reports_nonzero_and_current_evidence(self):
        self.contract_data["checks"] = [{"id": "expected-population", "query": {"op": "nodes_of_type", "type": "Entity"}, "expect": ["missing"]}]
        self.contract.write_text(json.dumps(self.contract_data), encoding="utf-8")
        self.snapshots[self.contract] = self.contract.read_bytes()
        report = self.root / "competency-review.json"
        self.run_cli(*self.scan_args(report, claims=False), expected=1)
        result = json.loads(report.read_text())
        self.assertEqual(result["validation"]["contract_status"], "invalid")
        self.assertTrue(result["findings"])

    def test_no_findings_or_scope_differences_only_exit_zero(self):
        self.run_cli(*self.scan_args(self.root / "none.json", claims=False), expected=0)
        claims = payload()
        claims["assertions"][1]["scope"]["context"] = "elsewhere"
        self.claims.write_text(json.dumps(claims), encoding="utf-8")
        self.snapshots[self.claims] = self.claims.read_bytes()
        self.run_cli(*self.scan_args(self.root / "scope.json"), expected=0)

    def test_decision_exit_one_not_resolved_and_inputs_immutable(self):
        review = helper.scan(self.model_data, self.contract_data, payload())
        review_path, decisions = self.write("review.json", review), self.write("decisions.json", decision_input(review))
        self.snapshots.update({p: p.read_bytes() for p in (review_path, decisions)})
        output = self.root / "decision-record.json"
        self.run_cli("decide", "--review", review_path, "--decisions", decisions, "--report", output, expected=1)
        self.assertEqual(json.loads(output.read_text())["findings"][0]["status"], "decision_recorded_pending_validation")

    def test_existing_output_preserved(self):
        output = self.root / "existing.json"
        output.write_text("preserve", encoding="utf-8")
        self.run_cli(*self.scan_args(output), expected=2)
        self.assertEqual(output.read_text(), "preserve")

    def test_report_and_markdown_cannot_overwrite_inputs_or_each_other(self):
        for filename in self.inputs:
            with self.subTest(filename=filename.name):
                self.run_cli(*self.scan_args(filename), expected=2)
                self.run_cli(*self.scan_args(self.root / (filename.stem + "-report.json"), filename), expected=2)
        path = self.root / "collision.json"
        self.run_cli(*self.scan_args(path, path), expected=2)
        self.assertFalse(path.exists())

    def test_hardlink_outputs_cannot_overwrite_inputs(self):
        for i, filename in enumerate(self.inputs):
            with self.subTest(filename=filename.name):
                link = self.root / ("hardlink" + str(i))
                os.link(filename, link)
                self.run_cli(*self.scan_args(link), expected=2)
                self.run_cli(*self.scan_args(self.root / ("out" + str(i) + ".json"), link), expected=2)

    def test_malformed_claims_and_json_do_not_traceback_or_return_zero(self):
        for i, claims in enumerate([[], {}, {"schema_version": "1", "assertions": []}, {"schema_version": "1", "assertions": [{"id": "broken"}]}]):
            # No functional predicates is allowed; an empty assertion population
            # is meaningful only when all other required fields are present.
            if claims == {"schema_version": "1", "assertions": []}:
                continue
            self.claims.write_text(json.dumps(claims), encoding="utf-8")
            self.snapshots[self.claims] = self.claims.read_bytes()
            self.run_cli(*self.scan_args(self.root / (str(i) + ".json")), expected=2)
        self.claims.write_text('{"id":1,"id":2}', encoding="utf-8")
        self.snapshots[self.claims] = self.claims.read_bytes()
        self.run_cli(*self.scan_args(self.root / "duplicate.json"), expected=2)

    def test_malformed_review_is_structured_processor_error(self):
        values = [[], {}, {"scan_status": "completed", "review_revision": "x"}, {"scan_status": "completed", "review_revision": "x", "findings": [None]}]
        for i, review in enumerate(values):
            with self.subTest(review=review):
                rp = self.write("bad-review" + str(i) + ".json", review)
                dp = self.write("decision" + str(i) + ".json", {"schema_version": "1", "review_revision": "x", "decisions": []})
                self.run_cli("decide", "--review", rp, "--decisions", dp, "--report", self.root / ("bad-out" + str(i) + ".json"), expected=2)

    def test_invalid_choice_shapes_are_structured_errors(self):
        review = helper.scan(self.model_data, self.contract_data, payload())
        rp = self.write("review.json", review)
        for i, (field, value) in enumerate([("choice", []), ("choice", {}), ("assertion_id", [])]):
            with self.subTest(field=field, value=value):
                decisions = decision_input(review)
                decisions["decisions"][0][field] = value
                dp = self.write("bad-decision" + str(i) + ".json", decisions)
                self.run_cli("decide", "--review", rp, "--decisions", dp, "--report", self.root / ("bad-choice-out" + str(i) + ".json"), expected=2)


if __name__ == "__main__":
    receipt = None
    if "--receipt" in sys.argv:
        i = sys.argv.index("--receipt")
        receipt = Path(sys.argv[i + 1]).resolve()
        del sys.argv[i:i + 2]
    before = hashlib.sha256(HELPER.read_bytes()).hexdigest()
    core_before = hashlib.sha256(CORE.read_bytes()).hexdigest()
    program = unittest.main(verbosity=2, exit=False)
    result = program.result
    after = hashlib.sha256(HELPER.read_bytes()).hexdigest()
    core_after = hashlib.sha256(CORE.read_bytes()).hexdigest()
    if receipt:
        outcome = {"status": "passed" if result.wasSuccessful() and before == after and core_before == core_after else "failed",
                   "checked_at_utc": datetime.now(timezone.utc).isoformat(), "tests_run": result.testsRun,
                   "failures": [{"test": str(t), "traceback": text} for t, text in result.failures],
                   "errors": [{"test": str(t), "traceback": text} for t, text in result.errors],
                   "skipped": [{"test": str(t), "reason": reason} for t, reason in result.skipped],
                   "helper_sha256_before": before, "helper_sha256_after": after,
                   "core_sha256_before": core_before, "core_sha256_after": core_after,
                   "sources_unchanged_during_run": before == after and core_before == core_after,
                   "test_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                   "scope": "Declared conflict detection, evidence presentation, explicit decision recording and immutable CLI inputs. No semantic-truth certification or external services."}
        receipt.parent.mkdir(parents=True, exist_ok=True)
        receipt.write_text(json.dumps(outcome, indent=2), encoding="utf-8")
    raise SystemExit(0 if result.wasSuccessful() and before == after and core_before == core_after else 1)
