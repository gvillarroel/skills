#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Observable contract, staging, reduction and file-safety tests; standard library.

Run: python test_semantic_model.py [--receipt /absolute/path/to/qa.json]
Fixtures and CLI outputs live only in TemporaryDirectory. No service or model.
These tests do not verify the truth of natural-language semantic assertions.
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
REF = HERE.parent / "assets" / "examples" / "semantic-model"
spec = importlib.util.spec_from_file_location("semantic_model_under_test", CORE)
engine = importlib.util.module_from_spec(spec)
spec.loader.exec_module(engine)


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def codes(report):
    return {issue["code"] for issue in report["errors"]}


def edge(rid, predicate, left, right, source="s:A", **extra):
    result = {"id": rid, "type": predicate, "from": left, "to": right,
              "source_ids": [source]}
    result.update(extra)
    return result


def graph_fixture(closure=False):
    contract = {"schema_version": "1", "id": "class-graph", "version": "1",
                "types": {"Class": {"attributes": {}, "closed_attributes": True}},
                "relations": {"is_a": {"from_types": ["Class"], "to_types": ["Class"],
                                          "acyclic": True, "transitive": True,
                                          "reduce_closure": closure}},
                "require_source_bindings": True,
                "checks": [
                    {"id": "all-classes", "query": {"op": "nodes_of_type", "type": "Class"}, "expect": ["A", "B", "C"]},
                    {"id": "A-ancestors", "query": {"op": "reachable", "from": "A", "relation": "is_a"}, "expect": ["B", "C"]},
                    {"id": "source-A", "query": {"op": "bindings", "source_id": "s:A"}, "expect": ["A"]}]}
    model = {"schema_version": "1", "contract_id": "class-graph", "contract_version": "1",
             "sources": [{"id": "s:" + n, "text": "Source " + n, "locator": "synthetic#" + n,
                          "selected": n == "A", "required": n == "B", "weight": 1} for n in "ABC"],
             "nodes": [{"id": n, "type": "Class", "label": "Class " + n,
                        "definition": "Definition " + n, "source_ids": ["s:" + n], "attributes": {}} for n in "ABC"],
             "relations": [edge("AB", "is_a", "A", "B"), edge("BC", "is_a", "B", "C"), edge("AC", "is_a", "A", "C")],
             "bindings": {"s:" + n: [n] for n in "ABC"}, "metadata": {"protected": "keep"}}
    return contract, model


class ModelTests(unittest.TestCase):
    def setUp(self):
        self.contract = read(REF / "example-contract.json")
        self.model = read(REF / "example-model.json")
        self.addition = read(REF / "example-addition.json")

    def invalid(self, model, code, contract=None, baseline=None):
        report = engine.validate(model, contract or self.contract, baseline)
        self.assertEqual(report["engine_status"], "completed")
        self.assertEqual(report["contract_status"], "invalid")
        self.assertIn(code, codes(report))
        return report

    def test_packaged_examples_conform_without_semantic_truth_claim(self):
        report = engine.validate(self.model, self.contract)
        self.assertEqual(report["contract_status"], "valid")
        self.assertEqual(report["semantic_status"], "not_run")
        self.assertTrue(report["competency_checks"])
        self.assertTrue(all(c["passed"] for c in report["competency_checks"]))

    def test_unknown_node_type_has_type_and_path_diagnostic(self):
        self.model["nodes"][0]["type"] = "Unregistered"
        report = self.invalid(self.model, "UNDECLARED_TYPE")
        item = next(e for e in report["errors"] if e["code"] == "UNDECLARED_TYPE")
        self.assertEqual(item["entity"], "req:retrieve")
        self.assertEqual(item["type"], "Unregistered")
        self.assertIn("type", item["path"])
        self.assertEqual(item["rule_version"], self.contract["version"])

    def test_unknown_type_accumulates_common_field_and_provenance_diagnostics(self):
        self.model["nodes"][0].update(type="Unregistered", definition="", source_ids=["source:absent"])
        report = self.invalid(self.model, "UNDECLARED_TYPE")
        self.assertIn("MISSING_REQUIRED_FIELD", codes(report))
        self.assertIn("PROVENANCE_SCOPE", codes(report))
        for issue in report["errors"]:
            if issue["entity"] == "req:retrieve" and issue["code"] in {"UNDECLARED_TYPE", "MISSING_REQUIRED_FIELD", "PROVENANCE_SCOPE"}:
                self.assertEqual(issue["type"], "Unregistered")

    def test_required_definition_missing(self):
        del self.model["nodes"][0]["definition"]
        self.invalid(self.model, "MISSING_REQUIRED_FIELD")

    def test_attribute_contract_missing_closed_enum_and_type(self):
        mutations = [("MISSING_ATTRIBUTE", {}), ("UNKNOWN_ATTRIBUTE", {"domain": "context", "extra": True}),
                     ("ATTRIBUTE_ENUM", {"domain": "unknown"}), ("ATTRIBUTE_TYPE", {"domain": 9})]
        for code, attrs in mutations:
            with self.subTest(code=code):
                model = copy.deepcopy(self.model)
                model["nodes"][0]["attributes"] = attrs
                self.invalid(model, code)

    def test_integer_does_not_accept_boolean(self):
        self.contract["types"]["Requirement"]["attributes"]["count"] = {"type": "integer"}
        self.model["nodes"][0]["attributes"]["count"] = True
        self.invalid(self.model, "ATTRIBUTE_TYPE")

    def test_numeric_array_length_and_item_constraints(self):
        attrs = self.contract["types"]["Requirement"]["attributes"]
        attrs["priority"] = {"type": "integer", "minimum": 1, "maximum": 5}
        attrs["tags"] = {"type": "array", "min_length": 1, "max_length": 2, "items_type": "string"}
        for extra, code in [({"priority": 0}, "ATTRIBUTE_RANGE"), ({"priority": 6}, "ATTRIBUTE_RANGE"),
                            ({"tags": []}, "ATTRIBUTE_LENGTH"), ({"tags": ["a", "b", "c"]}, "ATTRIBUTE_LENGTH"),
                            ({"tags": [7]}, "ATTRIBUTE_ITEMS_TYPE")]:
            with self.subTest(extra=extra):
                model = copy.deepcopy(self.model)
                model["nodes"][0]["attributes"].update(extra)
                self.invalid(model, code)

    def test_cardinality_counts_distinct_targets(self):
        self.model["relations"][1] = copy.deepcopy(self.model["relations"][0])
        self.model["relations"][1]["id"] = "duplicate-retrieval"
        self.invalid(self.model, "CARDINALITY_VIOLATION")

    def test_dangling_reference(self):
        self.model["relations"][0]["to"] = "missing"
        self.invalid(self.model, "DANGLING_REFERENCE")

    def test_relation_endpoint_types(self):
        self.model["relations"][0]["type"] = "is_a"
        self.invalid(self.model, "RELATION_TYPE_MISMATCH")

    def test_unknown_relation(self):
        self.model["relations"][0]["type"] = "invented"
        report = self.invalid(self.model, "UNDECLARED_RELATION")
        self.assertEqual(next(e["type"] for e in report["errors"] if e["code"] == "UNDECLARED_RELATION"), "invented")

    def test_declared_review_required(self):
        del self.model["relations"][0]["review"]
        self.invalid(self.model, "REVIEW_REQUIRED")

    def test_forbidden_cycle_is_per_predicate(self):
        contract, model = graph_fixture()
        model["relations"].append(edge("CA", "is_a", "C", "A"))
        report = self.invalid(model, "CYCLE_FORBIDDEN", contract)
        witness = next(e["actual"] for e in report["errors"] if e["code"] == "CYCLE_FORBIDDEN")
        self.assertEqual(witness[0], witness[-1])

    def test_cycles_allowed_for_associative_predicate(self):
        self.model["relations"].extend([
            edge("assoc-1", "related_to", "req:retrieve", "req:store", "source:retrieve"),
            edge("assoc-2", "related_to", "req:store", "req:retrieve", "source:store")])
        self.assertEqual(engine.validate(self.model, self.contract)["contract_status"], "valid")

    def test_exclusive_symmetric_predicates_catch_reversed_endpoints(self):
        review = {"decision": "accepted", "reviewer": "fixture", "rationale": "synthetic assertion"}
        self.model["relations"].extend([
            edge("same", "same_acceptance", "req:retrieve", "req:store", "source:retrieve", review=review),
            edge("distinct", "distinct_acceptance", "req:store", "req:retrieve", "source:store", review=review)])
        self.invalid(self.model, "INCOMPATIBLE_RELATION")

    def test_symmetric_exclusion_applies_against_reverse_directional_assertion(self):
        contract, model = graph_fixture()
        contract["relations"]["related"] = {"from_types": ["Class"], "to_types": ["Class"],
                                               "symmetric": True, "exclusive_with": ["is_a"]}
        model["relations"].append(edge("BA-related", "related", "B", "A"))
        self.invalid(model, "INCOMPATIBLE_RELATION", contract)

    def test_unknown_source_provenance_rejected_for_node_and_edge(self):
        for field in ["nodes", "relations"]:
            with self.subTest(collection=field):
                model = copy.deepcopy(self.model)
                model[field][0]["source_ids"] = ["source:missing"]
                self.invalid(model, "PROVENANCE_SCOPE")

    def test_sources_need_explicit_representation(self):
        self.model["sources"].append({"id": "unbound", "text": "new", "locator": "fixture#new"})
        self.invalid(self.model, "SOURCE_UNREPRESENTED")

    def test_binding_requires_existing_target(self):
        self.model["bindings"]["source:retrieve"] = ["missing"]
        self.invalid(self.model, "INVALID_BINDING")

    def test_baseline_source_and_vote_fields_are_preserved_exactly(self):
        baseline = copy.deepcopy(self.model)
        for field, value in [("text", "changed"), ("locator", "elsewhere"), ("selected", False),
                             ("required", True), ("weight", 99)]:
            with self.subTest(field=field):
                model = copy.deepcopy(baseline)
                model["sources"][0][field] = value
                self.invalid(model, "SOURCE_MUTATION", baseline=baseline)

    def test_baseline_metadata_is_preserved(self):
        baseline = copy.deepcopy(self.model)
        self.model["metadata"]["purpose"] = "changed"
        self.invalid(self.model, "METADATA_LOSS", baseline=baseline)

    def test_competency_answers_are_enforced(self):
        self.model["bindings"]["source:retrieve"].append("req:learn")
        self.invalid(self.model, "COMPETENCY_CHECK_FAILED")

    def test_nodes_where_uses_and_and_exact_scalar_types(self):
        attrs = self.contract["types"]["Requirement"]["attributes"]
        attrs.update(enabled={"type": "boolean"}, facet_rank={"type": "number"})
        for node in self.model["nodes"]:
            if node["type"] == "Requirement":
                node["attributes"].update(enabled=True, facet_rank=1.0 if node["id"] == "req:learn" else 1)
        query = {"op": "nodes_where", "type": "Requirement",
                 "equals": {"domain": "context", "enabled": True, "facet_rank": 1}}
        self.contract["checks"].append({"id": "typed-facet", "query": query, "expect": ["req:retrieve"]})
        report = engine.validate(self.model, self.contract)
        self.assertEqual(report["contract_status"], "valid")
        self.assertEqual(engine.query_result(self.model, query), ["req:retrieve"])
        self.assertTrue(next(t["passed"] for t in report["competency_checks"] if t["id"] == "typed-facet"))

    def test_nodes_where_detects_changed_business_question_answer(self):
        query = {"op": "nodes_where", "type": "Requirement", "equals": {"domain": "metadata"}}
        self.contract["checks"].append({"id": "metadata-facet", "query": query, "expect": ["req:store"]})
        self.assertEqual(engine.validate(self.model, self.contract)["contract_status"], "valid")
        self.model["nodes"][1]["attributes"]["domain"] = "context"
        report = self.invalid(self.model, "COMPETENCY_CHECK_FAILED")
        item = next(t for t in report["competency_checks"] if t["id"] == "metadata-facet")
        self.assertEqual(item["actual"], [])

    def test_unknown_contract_constraints_fail_closed(self):
        self.contract["types"]["Requirement"]["unsupported"] = True
        with self.assertRaises(engine.EngineError) as caught:
            engine.validate(self.model, self.contract)
        self.assertEqual(caught.exception.code, "UNSUPPORTED_CONSTRAINT")

    def test_unknown_query_fails_closed(self):
        self.contract["checks"][0]["query"]["op"] = "invented_query"
        with self.assertRaises(engine.EngineError) as caught:
            engine.validate(self.model, self.contract)
        self.assertEqual(caught.exception.code, "UNSUPPORTED_CONSTRAINT")

    def test_malformed_known_contract_values_raise_structured_engine_error(self):
        for target in ["attribute_type", "items_type", "query_op"]:
            with self.subTest(target=target):
                contract = copy.deepcopy(self.contract)
                if target == "attribute_type":
                    contract["types"]["Requirement"]["attributes"]["domain"]["type"] = []
                elif target == "items_type":
                    contract["types"]["Requirement"]["attributes"]["domain"] = {"type": "array", "items_type": []}
                else:
                    contract["checks"][0]["query"]["op"] = []
                with self.assertRaises(engine.EngineError):
                    engine.validate(self.model, contract)

    def test_closure_reduction_needs_transitive_acyclic_directional_rule(self):
        for changed in [{"transitive": False}, {"acyclic": False}, {"symmetric": True}]:
            with self.subTest(changed=changed):
                contract, model = graph_fixture(True)
                contract["relations"]["is_a"].update(changed)
                with self.assertRaises(engine.EngineError):
                    engine.validate(model, contract)

    def test_valid_staging_adds_without_mutating_either_input(self):
        before = copy.deepcopy((self.model, self.addition))
        candidate, report = engine.stage(self.model, self.addition, self.contract)
        self.assertEqual(report["contract_status"], "valid")
        self.assertEqual((self.model, self.addition), before)
        self.assertEqual(len(candidate["nodes"]), len(self.model["nodes"]) + 1)
        self.assertEqual(candidate["sources"][:len(self.model["sources"])], self.model["sources"])
        self.assertEqual(candidate["bindings"]["source:store"], ["req:store"])

    def test_staging_cross_boundary_cycle_rejected_without_mutation(self):
        contract, model = graph_fixture()
        addition = {"relations": [edge("CA", "is_a", "C", "A")]}
        before = copy.deepcopy((model, addition))
        candidate, report = engine.stage(model, addition, contract)
        self.assertIsNone(candidate)
        self.assertIn("CYCLE_FORBIDDEN", codes(report))
        self.assertEqual((model, addition), before)

    def test_invalid_baseline_cannot_be_staged(self):
        self.model["nodes"][0]["type"] = "undeclared"
        candidate, report = engine.stage(self.model, self.addition, self.contract)
        self.assertIsNone(candidate)
        self.assertEqual(report["phase"], "baseline")

    def test_reduce_deduplicates_assertions_preserves_nodes_sources_votes_and_queries(self):
        contract, model = graph_fixture(False)
        model["relations"].append(edge("AB-duplicate", "is_a", "A", "B", "s:B"))
        original = copy.deepcopy(model)
        candidate, report = engine.reduce_model(model, contract)
        self.assertEqual(report["contract_status"], "valid")
        self.assertEqual(model, original)
        self.assertEqual(candidate["nodes"], original["nodes"])
        self.assertEqual(candidate["sources"], original["sources"])
        self.assertEqual(candidate["bindings"], original["bindings"])
        self.assertEqual(len(candidate["relations"]), 3)
        keeper = next(e for e in candidate["relations"] if e["id"] == "AB")
        self.assertEqual(keeper["source_ids"], ["s:A", "s:B"])
        self.assertEqual(candidate["history"][0]["original_assertion"]["id"], "AB-duplicate")
        self.assertTrue(all(t["passed"] for t in report["competency_checks"]))

    def test_reduce_only_removes_permitted_transitive_closure(self):
        for permitted, count in [(False, 3), (True, 2)]:
            with self.subTest(permitted=permitted):
                contract, model = graph_fixture(permitted)
                candidate, report = engine.reduce_model(model, contract)
                self.assertEqual(report["contract_status"], "valid")
                self.assertEqual(len(candidate["relations"]), count)
                self.assertEqual(candidate["nodes"], model["nodes"])
                self.assertEqual(engine.query_result(candidate, contract["checks"][1]["query"]), ["B", "C"])
                self.assertFalse(report["reduction"]["global_optimum_proved"])

    def test_direct_neighbor_obligation_prevents_closure_removal(self):
        contract, model = graph_fixture(True)
        contract["checks"].append({"id": "direct-A", "query": {"op": "neighbors", "from": "A", "relation": "is_a"}, "expect": ["B", "C"]})
        candidate, report = engine.reduce_model(model, contract)
        self.assertEqual(len(candidate["relations"]), 3)
        self.assertTrue(any(s["relation_id"] == "AC" for s in report["reduction"]["skipped"]))

    def test_assertions_with_different_review_evidence_are_not_silently_collapsed(self):
        contract, model = graph_fixture()
        model["relations"][0]["review"] = {"rationale": "first"}
        model["relations"].append(edge("AB-other", "is_a", "A", "B", review={"rationale": "second"}))
        candidate, report = engine.reduce_model(model, contract)
        self.assertEqual(len(candidate["relations"]), 4)
        self.assertEqual(report["reduction"]["operations"], [])

    def test_reduce_requires_declared_competency_tests(self):
        self.contract["checks"] = []
        before = copy.deepcopy(self.model)
        with self.assertRaises(engine.EngineError) as caught:
            engine.reduce_model(self.model, self.contract)
        self.assertEqual(caught.exception.code, "PRESERVATION_NOT_SPECIFIED")
        self.assertEqual(self.model, before)


class CliTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="semantic-skill-qa-")
        self.addCleanup(self.temp.cleanup)
        self.dir = Path(self.temp.name)
        self.contract = self.write("contract.json", read(REF / "example-contract.json"))
        self.model = self.write("model.json", read(REF / "example-model.json"))
        self.addition = self.write("addition.json", read(REF / "example-addition.json"))
        self.originals = {p: p.read_bytes() for p in [self.contract, self.model, self.addition]}

    def write(self, name, value):
        p = self.dir / name
        p.write_text(json.dumps(value), encoding="utf-8")
        return p

    def run_cli(self, command="validate", *extra):
        args = [sys.executable, "-B", str(CORE), command, "--contract", str(self.contract),
                "--base" if command == "stage" else "--model", str(self.model)]
        if command == "stage":
            args.extend(["--addition", str(self.addition)])
        process = subprocess.run(args + list(map(str, extra)), capture_output=True, text=True)
        self.assertNotIn("Traceback", process.stderr, process.stderr)
        lines = process.stdout.strip().splitlines()
        self.assertTrue(lines, process.stderr)
        return process.returncode, json.loads(lines[-1])

    def assert_originals(self):
        for p, data in self.originals.items():
            self.assertEqual(p.read_bytes(), data, "Input modified: " + str(p))

    def test_cli_validate_success_is_read_only(self):
        code, report = self.run_cli("validate")
        self.assertEqual(code, 0)
        self.assertEqual(report["semantic_status"], "not_run")
        self.assert_originals()

    def test_cli_stage_success_writes_new_candidate_only(self):
        candidate, reportpath = self.dir / "candidate.json", self.dir / "report.json"
        code, report = self.run_cli("stage", "--candidate", candidate, "--report", reportpath)
        self.assertEqual(code, 0)
        self.assertTrue(candidate.is_file())
        self.assertFalse(report["accepted_model_modified"])
        self.assertEqual(read(reportpath), report)
        self.assert_originals()

    def test_cli_reduce_success_writes_new_candidate_only(self):
        candidate = self.dir / "candidate.json"
        code, report = self.run_cli("reduce", "--candidate", candidate)
        self.assertEqual(code, 0)
        self.assertTrue(candidate.is_file())
        self.assertEqual(read(candidate)["nodes"], read(self.model)["nodes"])
        self.assert_originals()

    def test_invalid_stage_has_no_candidate_and_preserves_base(self):
        add = read(self.addition)
        add["nodes"][0]["type"] = "unknown"
        self.addition.write_text(json.dumps(add), encoding="utf-8")
        self.originals[self.addition] = self.addition.read_bytes()
        candidate = self.dir / "candidate.json"
        code, report = self.run_cli("stage", "--candidate", candidate)
        self.assertEqual(code, 1)
        self.assertEqual(report["contract_status"], "invalid")
        self.assertFalse(candidate.exists())
        self.assert_originals()

    def test_unknown_contract_has_engine_error_not_false_pass(self):
        contract = read(self.contract)
        contract["unknown_constraint"] = True
        self.contract.write_text(json.dumps(contract), encoding="utf-8")
        self.originals[self.contract] = self.contract.read_bytes()
        code, report = self.run_cli()
        self.assertEqual(code, 2)
        self.assertEqual(report["engine_status"], "error")
        self.assertIsNone(report["contract_status"])
        self.assert_originals()

    def test_json_parse_duplicate_keys_and_nonfinite_values_fail_closed(self):
        for text in ['{bad', '{"x":1,"x":2}', '{"x":NaN}', '{"x":1e10000}']:
            with self.subTest(text=text):
                self.model.write_text(text, encoding="utf-8")
                before = self.model.read_bytes()
                code, report = self.run_cli()
                self.assertEqual(code, 2)
                self.assertEqual(report["engine_status"], "error")
                self.assertIsNone(report["contract_status"])
                self.assertEqual(self.model.read_bytes(), before)

    def test_candidate_cannot_overwrite_base_or_contract(self):
        for destination in [self.model, self.contract]:
            with self.subTest(destination=destination):
                code, report = self.run_cli("stage", "--candidate", destination)
                self.assertEqual(code, 2)
                self.assertIn("INPUT_OVERWRITE_FORBIDDEN", codes(report))
                self.assert_originals()

    def test_report_cannot_overwrite_input_or_candidate(self):
        for destination in [self.model, self.contract, self.addition]:
            with self.subTest(destination=destination):
                # Addition is a protected input of stage, not ordinary validate.
                code, report = self.run_cli("stage", "--candidate", self.dir / "new.json", "--report", destination)
                self.assertEqual(code, 2)
                self.assert_originals()
        candidate = self.dir / "new.json"
        code, report = self.run_cli("stage", "--candidate", candidate, "--report", candidate)
        self.assertEqual(code, 2)
        self.assertFalse(candidate.exists())

    def test_existing_candidate_is_not_overwritten(self):
        candidate = self.dir / "accepted-existing.json"
        sentinel = b'{"existing":"accepted"}'
        candidate.write_bytes(sentinel)
        code, report = self.run_cli("stage", "--candidate", candidate)
        self.assertEqual(code, 2)
        self.assertEqual(candidate.read_bytes(), sentinel)
        self.assert_originals()

    def test_report_hardlink_cannot_overwrite_accepted_model(self):
        reportpath = self.dir / "report-hardlink.json"
        try:
            os.link(self.model, reportpath)
        except OSError as exc:
            self.skipTest("Filesystem does not support hard links: " + str(exc))
        code, report = self.run_cli("validate", "--report", reportpath)
        self.assertEqual(code, 2)
        self.assert_originals()

    def test_report_hardlinks_cannot_overwrite_contract_addition_or_baseline(self):
        for target in [self.contract, self.addition]:
            with self.subTest(target=target.name):
                alias = self.dir / ("report-alias-" + target.name)
                try:
                    os.link(target, alias)
                except OSError as exc:
                    self.skipTest("Filesystem does not support hard links: " + str(exc))
                code, report = self.run_cli("stage", "--candidate", self.dir / "new.json", "--report", alias)
                self.assertEqual(code, 2)
                self.assert_originals()
        baseline = self.dir / "baseline.json"
        baseline.write_bytes(self.originals[self.model])
        alias = self.dir / "report-baseline-alias.json"
        os.link(baseline, alias)
        code, report = self.run_cli("validate", "--baseline", baseline, "--report", alias)
        self.assertEqual(code, 2)
        self.assertEqual(baseline.read_bytes(), self.originals[self.model])
        self.assert_originals()

    def test_candidate_and_report_hardlink_collision_preserves_existing_candidate(self):
        candidate = self.dir / "existing-candidate.json"
        sentinel = b'{"existing":"keep"}'
        candidate.write_bytes(sentinel)
        alias = self.dir / "report-candidate-alias.json"
        try:
            os.link(candidate, alias)
        except OSError as exc:
            self.skipTest("Filesystem does not support hard links: " + str(exc))
        code, report = self.run_cli("stage", "--candidate", candidate, "--report", alias)
        self.assertEqual(code, 2)
        self.assertEqual(candidate.read_bytes(), sentinel)
        self.assertEqual(alias.read_bytes(), sentinel)
        self.assert_originals()

    def test_candidate_hardlink_aliases_cannot_overwrite_any_input(self):
        for target in [self.model, self.contract, self.addition]:
            with self.subTest(target=target.name):
                alias = self.dir / ("candidate-alias-" + target.name)
                try:
                    os.link(target, alias)
                except OSError as exc:
                    self.skipTest("Filesystem does not support hard links: " + str(exc))
                code, report = self.run_cli("stage", "--candidate", alias)
                self.assertEqual(code, 2)
                self.assert_originals()

    def test_malformed_known_contract_value_is_cli_engine_error_without_traceback(self):
        contract = read(self.contract)
        contract["types"]["Requirement"]["attributes"]["domain"]["type"] = []
        self.contract.write_text(json.dumps(contract), encoding="utf-8")
        self.originals[self.contract] = self.contract.read_bytes()
        code, report = self.run_cli()
        self.assertEqual(code, 2)
        self.assertEqual(report["engine_status"], "error")
        self.assertIsNone(report["contract_status"])
        self.assert_originals()

    def test_nodes_where_malformed_and_unknown_attribute_filters_are_cli_engine_errors(self):
        original = read(self.contract)
        for equals in [{}, [], {"undeclared": "x"}, {"domain": ["context"]}, {"domain": True}]:
            with self.subTest(equals=equals):
                contract = copy.deepcopy(original)
                contract["checks"].append({"id": "bad-facet", "query": {"op": "nodes_where", "type": "Requirement", "equals": equals}, "expect": []})
                self.contract.write_text(json.dumps(contract), encoding="utf-8")
                self.originals[self.contract] = self.contract.read_bytes()
                code, report = self.run_cli()
                self.assertEqual(code, 2)
                self.assertEqual(report["engine_status"], "error")
                self.assertIsNone(report["contract_status"])
                self.assert_originals()


if __name__ == "__main__":
    receipt = None
    if "--receipt" in sys.argv:
        i = sys.argv.index("--receipt")
        receipt = Path(sys.argv[i + 1]).resolve()
        del sys.argv[i:i + 2]
    before = hashlib.sha256(CORE.read_bytes()).hexdigest()
    program = unittest.main(verbosity=2, exit=False)
    result = program.result
    after = hashlib.sha256(CORE.read_bytes()).hexdigest()
    if receipt:
        payload = {"status": "passed" if result.wasSuccessful() and before == after else "failed",
                   "scope": "Deterministic JSON contract, staging, reduction and CLI file-safety invariants; no semantic-truth evaluation or external calls.",
                   "checked_at_utc": datetime.now(timezone.utc).isoformat(), "tests_run": result.testsRun,
                   "failures": [{"test": str(t), "traceback": detail} for t, detail in result.failures],
                   "errors": [{"test": str(t), "traceback": detail} for t, detail in result.errors],
                   "skipped": [{"test": str(t), "reason": reason} for t, reason in result.skipped],
                   "core_sha256_before": before, "core_sha256_after": after,
                   "core_unchanged_during_run": before == after,
                   "test_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
        receipt.parent.mkdir(parents=True, exist_ok=True)
        receipt.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    raise SystemExit(0 if result.wasSuccessful() and before == after else 1)
