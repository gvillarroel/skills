#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

"""Black-box and adversarial tests for the simulation bundle validator."""

from __future__ import annotations

import csv
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from run_simulation_experiment import canonical_json_bytes, sha256_file


SKILL_ROOT = Path(__file__).resolve().parent.parent
RUNNER = Path(__file__).with_name("run_simulation_experiment.py")
VALIDATOR = Path(__file__).with_name("validate_simulation_bundle.py")
ANALYZER = Path(__file__).with_name("analyze_simulation_hypotheses.py")
TEMPLATE_SPEC = SKILL_ROOT / "assets/templates/experiment.json"
TEMPLATE_MODEL = SKILL_ROOT / "assets/templates/model.py"


class ValidatorTests(unittest.TestCase):
    def run_cli(self, script: Path, *arguments: object) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(script), *(str(item) for item in arguments)],
            check=False,
            capture_output=True,
            text=True,
            timeout=60,
        )

    def prepare_complete_bundle(
        self,
        root: Path,
        *,
        deterministic: bool = False,
        time_unit: str | None = None,
        model_text: str | None = None,
        root_seed: int | None = None,
    ) -> None:
        root.mkdir(parents=True)
        spec = json.loads(TEMPLATE_SPEC.read_text("utf-8"))
        if deterministic:
            spec["replications"] = 1
            spec["uncertaintyMode"] = "deterministic"
            spec["seedPolicy"] = "independent-by-run"
            analysis = spec["hypotheses"][0]["analysis"]
            analysis["pairing"] = "deterministic"
            analysis["intervalMethod"] = "none"
            analysis["intervalLevel"] = None
            analysis.pop("outcomeBounds", None)
            spec["hypotheses"][0]["practicalThreshold"]["value"] = 0.0
        else:
            spec["replications"] = 12
        if root_seed is not None:
            spec["rootSeed"] = root_seed
        if time_unit is not None:
            spec["timeUnit"] = time_unit
        (root / "experiment.json").write_text(
            json.dumps(spec, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )
        if model_text is None:
            shutil.copyfile(TEMPLATE_MODEL, root / "model.py")
        else:
            (root / "model.py").write_text(model_text, encoding="utf-8")
        plan = self.run_cli(
            RUNNER,
            "plan",
            "--spec",
            root / "experiment.json",
            "--output-dir",
            root / "design",
        )
        self.assertEqual(plan.returncode, 0, plan.stderr)
        run = self.run_cli(RUNNER, "run", "--root", root, "--model", "model.py")
        self.assertEqual(run.returncode, 0, run.stderr)
        analyzed = self.run_cli(ANALYZER, "--root", root)
        self.assertEqual(analyzed.returncode, 0, analyzed.stderr)

    def test_complete_bundle_passes_and_writes_canonical_report(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "bundle"
            self.prepare_complete_bundle(root)
            report_path = root / "validation-report.json"
            result = self.run_cli(VALIDATOR, "--root", root, "--report", report_path)
            self.assertEqual(result.returncode, 0, result.stderr)
            report = json.loads(result.stdout)
            self.assertIs(report["ok"], True)
            self.assertEqual(report["executionStatus"], "complete")
            self.assertEqual(report["runCounts"]["failed"], 0)
            self.assertEqual(sum(report["hypothesisStatuses"].values()), 1)
            self.assertTrue(report["releaseEligible"])
            self.assertEqual(report_path.read_bytes(), canonical_json_bytes(report))

    def test_tampered_outcomes_fail_hash_validation(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "bundle"
            self.prepare_complete_bundle(root)
            outcome_path = root / "data/outcomes.csv"
            outcome_path.write_bytes(outcome_path.read_bytes() + b"\n")
            result = self.run_cli(VALIDATOR, "--root", root)
            self.assertEqual(result.returncode, 2)
            self.assertIn("hash mismatch", result.stderr)

    def test_missing_outcome_fails_even_after_manifest_is_rehashed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "bundle"
            self.prepare_complete_bundle(root)
            path = root / "data/outcomes.csv"
            with path.open("r", encoding="utf-8", newline="") as handle:
                reader = csv.DictReader(handle)
                columns = reader.fieldnames
                rows = list(reader)
            self.assertIsNotNone(columns)
            rows.pop()
            with path.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=columns, lineterminator="\n")
                writer.writeheader()
                writer.writerows(rows)
            manifest_path = root / "execution-manifest.json"
            manifest = json.loads(manifest_path.read_text("utf-8"))
            for record in manifest["files"]:
                if record["path"] == "data/outcomes.csv":
                    record["sha256"] = sha256_file(path)
                    record["rows"] = len(rows)
            manifest_path.write_bytes(canonical_json_bytes(manifest))
            result = self.run_cli(VALIDATOR, "--root", root)
            self.assertEqual(result.returncode, 2)
            self.assertIn("missing outcomes", result.stderr)

    def test_noncanonical_hypothesis_results_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "bundle"
            self.prepare_complete_bundle(root)
            path = root / "analysis/hypothesis-results.json"
            value = json.loads(path.read_text("utf-8"))
            path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
            result = self.run_cli(VALIDATOR, "--root", root)
            self.assertEqual(result.returncode, 2)
            self.assertIn("canonical JSON", result.stderr)

    def test_fabricated_hypothesis_status_is_rejected_after_canonical_rewrite(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "bundle"
            self.prepare_complete_bundle(root)
            path = root / "analysis/hypothesis-results.json"
            value = json.loads(path.read_text("utf-8"))
            observed = value["results"][0]["status"]
            value["results"][0]["status"] = (
                "challenges-under-model"
                if observed != "challenges-under-model"
                else "supports-under-model"
            )
            path.write_bytes(canonical_json_bytes(value))
            result = self.run_cli(VALIDATOR, "--root", root)
            self.assertEqual(result.returncode, 2)
            self.assertIn("independent recomputation", result.stderr)

    def test_execution_manifest_schema_version_requires_an_exact_integer(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "bundle"
            self.prepare_complete_bundle(root)
            path = root / "execution-manifest.json"
            original = json.loads(path.read_text("utf-8"))

            clean = self.run_cli(VALIDATOR, "--root", root)
            self.assertEqual(clean.returncode, 0, clean.stderr)

            for replacement in (True, False, 1.0):
                with self.subTest(replacement=replacement):
                    mutated = json.loads(json.dumps(original))
                    mutated["schemaVersion"] = replacement
                    path.write_bytes(canonical_json_bytes(mutated))
                    validation = self.run_cli(VALIDATOR, "--root", root)
                    self.assertEqual(validation.returncode, 2, validation.stderr)
                    self.assertIn(
                        "execution-manifest.json.schemaVersion must be a non-negative integer",
                        validation.stderr,
                    )

    def test_execution_manifest_rng_root_seed_requires_an_exact_integer(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            parent = Path(temporary)
            cases = (
                ("zero-seed", 0, (False,)),
                ("one-seed", 1, (True, 1.0)),
            )
            for bundle_name, root_seed, replacements in cases:
                root = parent / bundle_name
                self.prepare_complete_bundle(root, root_seed=root_seed)
                path = root / "execution-manifest.json"
                original = json.loads(path.read_text("utf-8"))

                clean = self.run_cli(VALIDATOR, "--root", root)
                self.assertEqual(clean.returncode, 0, clean.stderr)

                for replacement in replacements:
                    with self.subTest(root_seed=root_seed, replacement=replacement):
                        mutated = json.loads(json.dumps(original))
                        mutated["rng"]["rootSeed"] = replacement
                        path.write_bytes(canonical_json_bytes(mutated))
                        validation = self.run_cli(VALIDATOR, "--root", root)
                        self.assertEqual(validation.returncode, 2, validation.stderr)
                        self.assertIn(
                            "execution-manifest.json.rng.rootSeed must be a non-negative integer",
                            validation.stderr,
                        )

    def test_hypothesis_report_schema_version_requires_an_exact_integer(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "bundle"
            self.prepare_complete_bundle(root)
            path = root / "analysis/hypothesis-results.json"
            original = json.loads(path.read_text("utf-8"))

            clean = self.run_cli(VALIDATOR, "--root", root)
            self.assertEqual(clean.returncode, 0, clean.stderr)

            for replacement in (True, False, 1.0):
                with self.subTest(replacement=replacement):
                    mutated = json.loads(json.dumps(original))
                    mutated["schemaVersion"] = replacement
                    path.write_bytes(canonical_json_bytes(mutated))
                    validation = self.run_cli(VALIDATOR, "--root", root)
                    self.assertEqual(validation.returncode, 2, validation.stderr)
                    self.assertIn(
                        "analysis/hypothesis-results.json.schemaVersion must be a non-negative integer",
                        validation.stderr,
                    )

    def test_booleans_cannot_substitute_for_numeric_zero_or_one_in_results(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "bundle"
            self.prepare_complete_bundle(root, deterministic=True)
            path = root / "analysis/hypothesis-results.json"
            value = json.loads(path.read_text("utf-8"))

            clean = self.run_cli(VALIDATOR, "--root", root)
            self.assertEqual(clean.returncode, 0, clean.stderr)
            result = value["results"][0]
            self.assertIs(result["modelConditional"], True)
            self.assertIs(result["challengeSearch"]["performed"], True)
            self.assertIs(result["challengeSearch"]["reversalFound"], False)

            numeric_paths: list[tuple[tuple[str | int, ...], bool]] = []

            def collect_numeric_zero_or_one(
                item: object,
                item_path: tuple[str | int, ...] = (),
            ) -> None:
                if isinstance(item, bool):
                    return
                if isinstance(item, (int, float)) and item in (0, 1):
                    numeric_paths.append((item_path, bool(item)))
                    return
                if isinstance(item, dict):
                    for key, child in item.items():
                        collect_numeric_zero_or_one(child, (*item_path, key))
                elif isinstance(item, list):
                    for index, child in enumerate(item):
                        collect_numeric_zero_or_one(child, (*item_path, index))

            collect_numeric_zero_or_one(value["results"])
            self.assertEqual({replacement for _, replacement in numeric_paths}, {False, True})

            for numeric_path, replacement in numeric_paths:
                with self.subTest(path=numeric_path, replacement=replacement):
                    mutated = json.loads(json.dumps(value))
                    target = mutated["results"]
                    for component in numeric_path[:-1]:
                        target = target[component]
                    target[numeric_path[-1]] = replacement
                    path.write_bytes(canonical_json_bytes(mutated))
                    validation = self.run_cli(VALIDATOR, "--root", root)
                    self.assertEqual(validation.returncode, 2, validation.stderr)
                    self.assertIn("independent recomputation", validation.stderr)

    def test_tampered_observation_and_event_time_units_are_rejected(self) -> None:
        model = '''
import platform
MODEL_METADATA = {
    "modelId": "time-bearing-model",
    "modelVersion": "1.0.0",
    "engine": "python-standard-library",
    "engineVersion": platform.python_version(),
    "rng": "none",
    "rngVersion": platform.python_version(),
    "reproducibility": "bitwise",
}
def simulate(run):
    return {
        "outcomes": {"fill_rate": 0.5, "unmet_units": 1.0},
        "observations": [
            {"sim_time": 1.25, "variable": "queue_length", "value": 2.0, "unit": "item"}
        ],
        "events": [
            {"sim_time": 1.5, "event_type": "arrival", "payload": {"count": 1}}
        ],
    }
'''
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "bundle"
            self.prepare_complete_bundle(root, time_unit="hour", model_text=model)
            table_relatives = ("data/observations.csv", "data/events.csv")
            original_tables = {
                relative: (root / relative).read_bytes() for relative in table_relatives
            }
            manifest_path = root / "execution-manifest.json"
            original_manifest = manifest_path.read_bytes()

            for relative in table_relatives:
                with self.subTest(table=relative):
                    for original_relative, payload in original_tables.items():
                        (root / original_relative).write_bytes(payload)
                    manifest_path.write_bytes(original_manifest)

                    table_path = root / relative
                    with table_path.open("r", encoding="utf-8", newline="") as handle:
                        reader = csv.DictReader(handle)
                        columns = reader.fieldnames
                        rows = list(reader)
                    self.assertIsNotNone(columns)
                    self.assertTrue(rows)
                    rows[0]["time_unit"] = "day"
                    with table_path.open("w", encoding="utf-8", newline="") as handle:
                        writer = csv.DictWriter(handle, fieldnames=columns, lineterminator="\n")
                        writer.writeheader()
                        writer.writerows(rows)

                    manifest = json.loads(original_manifest)
                    record = next(item for item in manifest["files"] if item["path"] == relative)
                    record["sha256"] = sha256_file(table_path)
                    manifest_path.write_bytes(canonical_json_bytes(manifest))

                    validation = self.run_cli(VALIDATOR, "--root", root)
                    self.assertEqual(validation.returncode, 2, validation.stderr)
                    self.assertIn("time_unit must exactly match", validation.stderr)

    def test_time_bearing_rows_require_declared_experiment_time_unit(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "bundle"
            self.prepare_complete_bundle(root)
            with (root / "data/runs.csv").open("r", encoding="utf-8", newline="") as handle:
                run = next(csv.DictReader(handle))
            common = {
                key: run[key]
                for key in (
                    "experiment_id",
                    "run_id",
                    "scenario_id",
                    "design_point_id",
                    "replicate_id",
                    "coupling_id",
                )
            }
            injected_rows = {
                "data/observations.csv": {
                    **common,
                    "observation_index": "1",
                    "sim_time": "0",
                    "time_unit": "hour",
                    "entity_type": "",
                    "entity_id": "",
                    "variable": "queue_length",
                    "value": "1",
                    "unit": "item",
                    "source_type": "simulated",
                    "is_warmup": "false",
                },
                "data/events.csv": {
                    **common,
                    "event_index": "1",
                    "sim_time": "0",
                    "time_unit": "hour",
                    "entity_type": "",
                    "entity_id": "",
                    "event_type": "arrival",
                    "payload_json": "{}",
                    "source_type": "simulated",
                },
            }
            original_tables = {
                relative: (root / relative).read_bytes() for relative in injected_rows
            }
            manifest_path = root / "execution-manifest.json"
            original_manifest = manifest_path.read_bytes()

            for relative, injected in injected_rows.items():
                with self.subTest(table=relative):
                    for original_relative, payload in original_tables.items():
                        (root / original_relative).write_bytes(payload)
                    manifest_path.write_bytes(original_manifest)

                    table_path = root / relative
                    with table_path.open("r", encoding="utf-8", newline="") as handle:
                        columns = csv.DictReader(handle).fieldnames
                    self.assertIsNotNone(columns)
                    with table_path.open("w", encoding="utf-8", newline="") as handle:
                        writer = csv.DictWriter(handle, fieldnames=columns, lineterminator="\n")
                        writer.writeheader()
                        writer.writerow(injected)

                    manifest = json.loads(original_manifest)
                    record = next(item for item in manifest["files"] if item["path"] == relative)
                    record["sha256"] = sha256_file(table_path)
                    record["rows"] = 1
                    manifest_path.write_bytes(canonical_json_bytes(manifest))

                    validation = self.run_cli(VALIDATOR, "--root", root)
                    self.assertEqual(validation.returncode, 2, validation.stderr)
                    self.assertIn("experiment.timeUnit is not declared", validation.stderr)

    def test_allow_incomplete_writes_non_release_diagnostic_report(self) -> None:
        bad_model = '''
import platform
MODEL_METADATA = {
    "modelId": "failing-model",
    "modelVersion": "1.0.0",
    "engine": "python-standard-library",
    "engineVersion": platform.python_version(),
    "rng": "random.Random-MT19937",
    "rngVersion": platform.python_version(),
    "reproducibility": "exact-within-locked-environment",
}
def simulate(run):
    raise RuntimeError()
'''
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "bundle"
            root.mkdir(parents=True)
            spec = json.loads(TEMPLATE_SPEC.read_text("utf-8"))
            spec["replications"] = 2
            (root / "experiment.json").write_text(
                json.dumps(spec, indent=2) + "\n", encoding="utf-8"
            )
            (root / "model.py").write_text(bad_model, encoding="utf-8")
            plan = self.run_cli(
                RUNNER,
                "plan",
                "--spec",
                root / "experiment.json",
                "--output-dir",
                root / "design",
            )
            self.assertEqual(plan.returncode, 0, plan.stderr)
            run = self.run_cli(RUNNER, "run", "--root", root, "--model", "model.py")
            self.assertEqual(run.returncode, 2)
            report_path = root / "diagnostic-validation.json"
            result = self.run_cli(
                VALIDATOR,
                "--root",
                root,
                "--allow-incomplete",
                "--report",
                report_path,
            )
            self.assertEqual(result.returncode, 2)
            report = json.loads(report_path.read_text("utf-8"))
            self.assertIs(report["ok"], False)
            self.assertIs(report["releaseEligible"], False)
            self.assertEqual(report["executionStatus"], "incomplete")
            self.assertEqual(report["unresolvedHypothesisIds"], ["h1-fill-rate"])


if __name__ == "__main__":
    unittest.main()
