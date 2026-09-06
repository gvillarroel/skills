#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

"""Check review declarations, readable outputs, and mathematical-only integration."""

from __future__ import annotations

import copy
import csv
import io
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from model_variable_review import (
    DIMENSIONS,
    build_variable_review_files,
    review_row_count,
    variable_review_summary,
)
from run_simulation_experiment import (
    SimulationError,
    build_plan,
    canonical_json_bytes,
    normalize_spec,
    sha256_file,
    verify_plan,
)


SCRIPTS = Path(__file__).resolve().parent
TEMPLATES = SCRIPTS.parent / "assets/templates"


def template_spec():
    return json.loads((TEMPLATES / "experiment.json").read_text("utf-8"))


def review_of(spec):
    return spec["extensions"]["simulation-data-lab"]["variableReview"]


class ModelReviewTests(unittest.TestCase):
    def run_cli(self, script, *arguments):
        return subprocess.run(
            [sys.executable, str(SCRIPTS / script), *(str(item) for item in arguments)],
            check=False, capture_output=True, text=True, timeout=60,
        )

    def prepare(self, root, *, legacy=False):
        spec = template_spec()
        spec["replications"] = 4
        if legacy:
            review_of(spec)  # Assert this fixture really exercises removal.
            del spec["extensions"]["simulation-data-lab"]["variableReview"]
        (root / "experiment.json").write_bytes(canonical_json_bytes(spec))
        shutil.copyfile(TEMPLATES / "model.py", root / "model.py")
        return spec

    def plan(self, root, *, require=True):
        return self.run_cli(
            "run_simulation_experiment.py", "plan", "--spec", root / "experiment.json",
            "--output-dir", root / "design", *(["--require-variable-review"] if require else []),
        )

    def test_template_records_candidates_interactions_and_critical_gaps(self):
        spec = normalize_spec(template_spec())
        review = review_of(spec)
        self.assertEqual({item["dimension"] for item in review["coverageChecks"]}, DIMENSIONS)
        self.assertEqual(review_row_count(spec), 9)
        summary = variable_review_summary(spec)
        self.assertEqual(summary["status"], "limitations-required")
        self.assertEqual(summary["criticalVariableIds"], [
            "carry-over", "demand-dependence", "economic-objective", "supply-availability",
        ])
        self.assertEqual(summary["criticalInteractionIds"], ["temporal-inventory-feedback"])
        self.assertEqual(summary["documentedParameterNames"], ["demand_mean", "demand_sd", "stock_units"])
        self.assertEqual(summary["exhaustiveness"], "not-certified")

    def test_export_derives_actual_settings_and_preserves_decision_only_candidate(self):
        spec = template_spec()
        spec["scenarios"][0]["parameters"][0]["value"] = 99.125
        spec = normalize_spec(spec)
        files = build_variable_review_files(spec)
        rows = list(csv.DictReader(io.StringIO(files["variable-inventory.csv"].decode())))
        stock = next(row for row in rows if row["variable_id"] == "stock")
        bindings = json.loads(stock["parameter_bindings_json"])["stock_units"]
        self.assertEqual(bindings[0], {
            "scope": "scenarios", "ownerId": "baseline-stock", "value": 99.125,
            "unit": "item", "sourceType": "assumed",
        })
        economic = next(row for row in rows if row["variable_id"] == "economic-objective")
        self.assertEqual(economic["affects_outcomes_json"], "[]")
        self.assertEqual(economic["source_type"], "model-review-declaration")
        rendered = files["model-review.md"].decode()
        for fragment in ("99.125", "Decision scope only", "not a certificate", "Questions for the human reviewer"):
            self.assertIn(fragment, rendered)
        self.assertEqual(files, build_variable_review_files(spec))

    def test_added_parameter_cannot_be_silently_undocumented(self):
        spec = template_spec()
        spec["scenarios"][0]["parameters"].append({
            "name": "new_cost", "unit": "currency", "value": 3, "sourceType": "assumed",
        })
        with self.assertRaisesRegex(SimulationError, "undocumented: new_cost"):
            normalize_spec(spec)

    def test_duplicate_parameter_ownership_is_rejected(self):
        spec = template_spec()
        duplicate = copy.deepcopy(review_of(spec)["variables"][0])
        duplicate["variableId"] = "duplicate-stock"
        review_of(spec)["variables"].append(duplicate)
        with self.assertRaisesRegex(SimulationError, "ownership is duplicated"):
            normalize_spec(spec)

    def test_parameter_units_must_match(self):
        spec = template_spec()
        review_of(spec)["variables"][0]["unit"] = "USD"
        with self.assertRaisesRegex(SimulationError, "unit differs"):
            normalize_spec(spec)

    def test_unknown_parameter_and_outcome_links_are_rejected(self):
        for field in ("parameterNames", "affectsOutcomes"):
            with self.subTest(field=field):
                spec = template_spec()
                review_of(spec)["variables"][0][field] = ["nonexistent"]
                with self.assertRaisesRegex(SimulationError, "unknown references"):
                    normalize_spec(spec)

    def test_declared_outcome_needs_a_represented_path(self):
        spec = template_spec()
        for item in review_of(spec)["variables"]:
            item["affectsOutcomes"] = [name for name in item["affectsOutcomes"] if name != "unmet_units"]
        with self.assertRaisesRegex(SimulationError, "path to outcomes: unmet_units"):
            normalize_spec(spec)

    def test_omitted_variable_cannot_claim_an_implemented_parameter(self):
        spec = template_spec()
        review_of(spec)["variables"][0]["treatment"] = "excluded"
        with self.assertRaisesRegex(SimulationError, "cannot own implemented parameters"):
            normalize_spec(spec)

    def test_interactions_require_known_represented_participants(self):
        for variant in ("unknown", "omitted", "empty"):
            with self.subTest(variant=variant):
                spec = template_spec()
                item = review_of(spec)["interactions"][0]
                item["variableIds"] = {
                    "unknown": ["missing"], "omitted": ["stock", "carry-over"], "empty": [],
                }[variant]
                with self.assertRaises(SimulationError):
                    normalize_spec(spec)

    def test_review_dimensions_are_complete_unique_and_meaningfully_linked(self):
        for variant in ("missing", "duplicate", "empty-reviewed", "unknown-status"):
            with self.subTest(variant=variant):
                spec = template_spec()
                checks = review_of(spec)["coverageChecks"]
                if variant == "missing":
                    checks.pop()
                elif variant == "duplicate":
                    checks.append(copy.deepcopy(checks[0]))
                elif variant == "empty-reviewed":
                    checks[0]["variableIds"] = []
                else:
                    checks[0]["status"] = "passed"
                with self.assertRaises(SimulationError):
                    normalize_spec(spec)

    def test_absent_review_retains_legacy_plan_and_explicitly_reports_absence(self):
        spec = template_spec()
        del spec["extensions"]["simulation-data-lab"]["variableReview"]
        normalized = normalize_spec(spec)
        self.assertNotIn("variableReview", normalized["extensions"]["simulation-data-lab"])
        self.assertEqual(review_row_count(normalized), 0)
        self.assertEqual(set(build_plan(normalized)), {
            "run-plan.csv", "scenario-factors.csv", "design-point-parameters.csv",
        })
        self.assertEqual(variable_review_summary(normalized)["status"], "not-recorded")

    def test_new_study_flag_rejects_missing_review_but_allows_legacy_replay(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.prepare(root, legacy=True)
            result = self.plan(root)
            self.assertEqual(result.returncode, 2)
            self.assertIn("new studies require", result.stderr)
            self.assertFalse((root / "design").exists())
            result = self.plan(root, require=False)
            self.assertEqual(result.returncode, 0, result.stderr)
            verify_plan(root)

    def test_malformed_versions_keys_ids_and_resource_limits_fail_closed(self):
        for variant in ("bool-version", "float-version", "null-review", "extra-key", "duplicate-id", "long-text", "oversized-list"):
            with self.subTest(variant=variant):
                spec = template_spec()
                review = review_of(spec)
                if variant == "bool-version":
                    review["schemaVersion"] = True
                elif variant == "float-version":
                    review["schemaVersion"] = 1.0
                elif variant == "null-review":
                    spec["extensions"]["simulation-data-lab"]["variableReview"] = None
                elif variant == "extra-key":
                    review["completenessScore"] = 100
                elif variant == "duplicate-id":
                    review["variables"][1]["variableId"] = review["variables"][0]["variableId"]
                elif variant == "long-text":
                    review["scope"] = "x" * 2001
                else:
                    review["openQuestions"] = ["Question"] * 201
                with self.assertRaises(SimulationError):
                    normalize_spec(spec)

    def test_recorded_review_does_not_imply_exhaustiveness_or_code_coverage(self):
        spec = template_spec()
        for item in review_of(spec)["variables"] + review_of(spec)["interactions"]:
            if item["treatment"] in {"excluded", "unresolved"}:
                item["decisionImpact"] = "low"
        summary = variable_review_summary(normalize_spec(spec))
        self.assertEqual(summary["status"], "review-recorded")
        self.assertEqual(summary["exhaustiveness"], "not-certified")
        self.assertEqual(summary["implementationCoverage"], "declarations-only-not-code-proof")

    def test_manifest_binds_both_views_and_counts_only_csv_rows(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.prepare(root)
            result = self.plan(root)
            self.assertEqual(result.returncode, 0, result.stderr)
            manifest = json.loads((root / "design/plan-manifest.json").read_text("utf-8"))
            records = {item["path"]: item for item in manifest["files"]}
            self.assertEqual(records["variable-inventory.csv"]["rows"], 9)
            self.assertNotIn("rows", records["model-review.md"])
            for name in ("variable-inventory.csv", "model-review.md"):
                self.assertEqual(records[name]["sha256"], sha256_file(root / "design" / name))
            verify_plan(root)

    def test_missing_or_tampered_views_are_rejected_before_model_import(self):
        for name in ("model-review.md", "variable-inventory.csv"):
            for variant in ("missing", "tampered", "rehashed"):
                with self.subTest(name=name, variant=variant), tempfile.TemporaryDirectory() as temporary:
                    root = Path(temporary)
                    self.prepare(root)
                    self.assertEqual(self.plan(root).returncode, 0)
                    path = root / "design" / name
                    if variant == "missing":
                        path.unlink()  # Only a disposable generated fixture inside this temporary root.
                    else:
                        path.write_bytes(path.read_bytes() + b"Changed review\n")
                        if variant == "rehashed":
                            manifest_path = root / "design/plan-manifest.json"
                            manifest = json.loads(manifest_path.read_text("utf-8"))
                            for record in manifest["files"]:
                                if record["path"] == name:
                                    record["sha256"] = sha256_file(path)
                            manifest_path.write_bytes(canonical_json_bytes(manifest))
                    (root / "model.py").write_text("raise RuntimeError('MODEL_IMPORT_SENTINEL')\n", encoding="utf-8")
                    result = self.run_cli("run_simulation_experiment.py", "run", "--root", root)
                    self.assertEqual(result.returncode, 2)
                    self.assertNotIn("MODEL_IMPORT_SENTINEL", result.stderr)
                    self.assertIn("design/", result.stderr)
                    self.assertFalse((root / "data").exists())

    def test_full_pipeline_reports_review_limits_separately_and_preserves_math(self):
        outcomes = []
        for legacy in (False, True):
            with self.subTest(legacy=legacy), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                self.prepare(root, legacy=legacy)
                result = self.plan(root, require=not legacy)
                self.assertEqual(result.returncode, 0, result.stderr)
                for script, arguments in (
                    ("run_simulation_experiment.py", ("run", "--root", root)),
                    ("analyze_simulation_hypotheses.py", ("--root", root)),
                    ("validate_simulation_bundle.py", ("--root", root)),
                ):
                    result = self.run_cli(script, *arguments)
                    self.assertEqual(result.returncode, 0, result.stderr)
                report = json.loads(result.stdout)
                self.assertTrue(report["releaseEligible"])
                self.assertEqual(report["modelReview"]["status"], "not-recorded" if legacy else "limitations-required")
                self.assertEqual("design/model-review.md" in report["verifiedFiles"], not legacy)
                self.assertEqual(report["hypothesisStatuses"], {"inconclusive-under-model": 1})
                outcomes.append((root / "data/outcomes.csv").read_bytes())
        self.assertEqual(outcomes[0], outcomes[1])


if __name__ == "__main__":
    unittest.main()
