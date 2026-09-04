#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

"""Black-box tests for the simulation planner and engine-agnostic runner."""

from __future__ import annotations

import csv
import hashlib
import io
import json
import os
import py_compile
import runpy
import shutil
import subprocess
import sys
import tempfile
import unittest
from collections.abc import Callable
from pathlib import Path
from types import SimpleNamespace
from typing import Any
from unittest import mock


SKILL_ROOT = Path(__file__).resolve().parent.parent
SCRIPT = Path(__file__).with_name("run_simulation_experiment.py")
TEMPLATE_SPEC = SKILL_ROOT / "assets/templates/experiment.json"
TEMPLATE_MODEL = SKILL_ROOT / "assets/templates/model.py"


class RunnerTests(unittest.TestCase):
    def run_cli(self, *arguments: object) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT), *(str(item) for item in arguments)],
            check=False,
            capture_output=True,
            text=True,
            timeout=60,
        )

    def prepare_bundle(
        self,
        root: Path,
        mutate: Callable[[dict[str, Any]], None] | None = None,
        model_text: str | None = None,
    ) -> dict[str, Any]:
        root.mkdir(parents=True)
        spec = json.loads(TEMPLATE_SPEC.read_text("utf-8"))
        spec["replications"] = 8
        if mutate is not None:
            mutate(spec)
        (root / "experiment.json").write_text(
            json.dumps(spec, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )
        if model_text is None:
            shutil.copyfile(TEMPLATE_MODEL, root / "model.py")
        else:
            (root / "model.py").write_text(model_text, encoding="utf-8")
        return spec

    def plan_and_run(
        self, root: Path
    ) -> tuple[subprocess.CompletedProcess[str], subprocess.CompletedProcess[str]]:
        planned = self.run_cli(
            "plan", "--spec", root / "experiment.json", "--output-dir", root / "design"
        )
        self.assertEqual(planned.returncode, 0, planned.stderr)
        executed = self.run_cli("run", "--root", root, "--model", "model.py")
        return planned, executed

    def read_rows(self, path: Path) -> list[dict[str, str]]:
        with path.open("r", encoding="utf-8", newline="") as handle:
            return list(csv.DictReader(handle))

    def test_schema_version_requires_exact_integer_one(self) -> None:
        for label, value in (("true", True), ("false", False), ("float", 1.0)):
            with self.subTest(label=label), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary) / "bundle"
                self.prepare_bundle(
                    root,
                    mutate=lambda spec, replacement=value: spec.__setitem__(
                        "schemaVersion", replacement
                    ),
                )
                planned = self.run_cli(
                    "plan",
                    "--spec",
                    root / "experiment.json",
                    "--output-dir",
                    root / "design",
                )
                self.assertEqual(planned.returncode, 2)
                self.assertIn("schemaVersion must be the integer 1", planned.stderr)
                self.assertFalse((root / "design").exists())

    def test_root_seed_and_replications_reject_bool_or_float_substitutions(self) -> None:
        cases = (
            ("root-seed-bool", "rootSeed", True),
            ("root-seed-float", "rootSeed", 20_260_903.0),
            ("replications-bool", "replications", True),
            ("replications-float", "replications", 8.0),
        )
        for label, field, value in cases:
            with self.subTest(label=label), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary) / "bundle"
                self.prepare_bundle(
                    root,
                    mutate=lambda spec, key=field, replacement=value: spec.__setitem__(
                        key, replacement
                    ),
                )
                planned = self.run_cli(
                    "plan",
                    "--spec",
                    root / "experiment.json",
                    "--output-dir",
                    root / "design",
                )
                self.assertEqual(planned.returncode, 2)
                self.assertIn(f"experiment.{field} must be", planned.stderr)
                self.assertFalse((root / "design").exists())

    def test_plan_manifest_rejects_bool_int_float_equal_substitutions(self) -> None:
        def single_cell_spec(spec: dict[str, Any]) -> None:
            spec["uncertaintyMode"] = "deterministic"
            spec["seedPolicy"] = "independent-by-run"
            spec["replications"] = 1
            spec["scenarios"] = [spec["scenarios"][0]]
            spec["designPoints"] = [spec["designPoints"][0]]
            hypothesis = spec["hypotheses"][0]
            hypothesis["scenarioIds"] = [spec["scenarios"][0]["scenarioId"]]
            hypothesis["analysis"] = {
                "kind": "not-identifiable",
                "reason": "A one-scenario fixture has no executable contrast.",
            }

        def replace_file_rows(manifest: dict[str, Any], path: str, value: Any) -> None:
            file_record = next(item for item in manifest["files"] if item["path"] == path)
            file_record["rows"] = value

        mutations: tuple[tuple[str, Callable[[dict[str, Any]], None]], ...] = (
            (
                "schema-bool",
                lambda manifest: manifest.__setitem__("schemaVersion", True),
            ),
            (
                "schema-float",
                lambda manifest: manifest.__setitem__("schemaVersion", 1.0),
            ),
            ("run-count-bool", lambda manifest: manifest.__setitem__("runCount", True)),
            ("run-count-float", lambda manifest: manifest.__setitem__("runCount", 1.0)),
            (
                "replication-count-bool",
                lambda manifest: manifest.__setitem__("replicationsPerDesignPoint", True),
            ),
            (
                "run-plan-row-count-bool",
                lambda manifest: replace_file_rows(manifest, "run-plan.csv", True),
            ),
            (
                "scenario-row-count-float",
                lambda manifest: replace_file_rows(manifest, "scenario-factors.csv", 1.0),
            ),
        )
        for label, mutate_manifest in mutations:
            with self.subTest(label=label), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary) / "bundle"
                self.prepare_bundle(root, mutate=single_cell_spec)
                planned = self.run_cli(
                    "plan",
                    "--spec",
                    root / "experiment.json",
                    "--output-dir",
                    root / "design",
                )
                self.assertEqual(planned.returncode, 0, planned.stderr)
                manifest_path = root / "design/plan-manifest.json"
                manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
                mutate_manifest(manifest)
                manifest_path.write_bytes(
                    (
                        json.dumps(
                            manifest,
                            ensure_ascii=False,
                            sort_keys=True,
                            separators=(",", ":"),
                            allow_nan=False,
                        )
                        + "\n"
                    ).encode("utf-8")
                )

                executed = self.run_cli("run", "--root", root, "--model", "model.py")
                self.assertEqual(executed.returncode, 2)
                self.assertIn("does not match", executed.stderr)
                self.assertFalse((root / "data").exists())

    def test_same_spec_reproduces_plan_outcomes_and_summary(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            parent = Path(temporary)
            roots = [parent / "a", parent / "b"]
            for root in roots:
                self.prepare_bundle(root)
                _, executed = self.plan_and_run(root)
                self.assertEqual(executed.returncode, 0, executed.stderr)
            for relative in (
                "design/run-plan.csv",
                "design/scenario-factors.csv",
                "design/design-point-parameters.csv",
                "data/runs.csv",
                "data/outcomes.csv",
                "analysis/summary.csv",
                "analysis/explore.sql",
                "data-dictionary.json",
            ):
                self.assertEqual(
                    (roots[0] / relative).read_bytes(),
                    (roots[1] / relative).read_bytes(),
                    relative,
                )
            explore_sql = (roots[0] / "analysis/explore.sql").read_text("utf-8")
            self.assertIn("v_paired_outcome_differences", explore_sql)
            self.assertIn("difference_b_minus_a", explore_sql)

    def test_paired_seed_policy_reuses_only_declared_couplings(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "bundle"
            self.prepare_bundle(root)
            planned = self.run_cli(
                "plan", "--spec", root / "experiment.json", "--output-dir", root / "design"
            )
            self.assertEqual(planned.returncode, 0, planned.stderr)
            rows = self.read_rows(root / "design/run-plan.csv")
            paired: dict[tuple[str, str], set[tuple[str, str]]] = {}
            for row in rows:
                key = (row["design_point_id"], row["replicate_id"])
                paired.setdefault(key, set()).add((row["seed"], row["coupling_id"]))
            self.assertTrue(paired)
            self.assertTrue(all(len(values) == 1 for values in paired.values()))
            self.assertEqual(
                len({next(iter(values))[0] for values in paired.values()}), len(paired)
            )

    def test_scenario_order_does_not_change_semantic_plan_or_results(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            parent = Path(temporary)
            first = parent / "first"
            second = parent / "second"
            self.prepare_bundle(first)
            self.prepare_bundle(second, lambda spec: spec["scenarios"].reverse())
            for root in (first, second):
                _, executed = self.plan_and_run(root)
                self.assertEqual(executed.returncode, 0, executed.stderr)
            self.assertEqual(
                (first / "design/run-plan.csv").read_bytes(),
                (second / "design/run-plan.csv").read_bytes(),
            )
            self.assertEqual(
                (first / "data/outcomes.csv").read_bytes(),
                (second / "data/outcomes.csv").read_bytes(),
            )

    def test_different_root_seed_changes_outcomes_without_schema_drift(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            parent = Path(temporary)
            first = parent / "first"
            second = parent / "second"
            self.prepare_bundle(first)
            self.prepare_bundle(
                second, lambda spec: spec.__setitem__("rootSeed", spec["rootSeed"] + 1)
            )
            for root in (first, second):
                _, executed = self.plan_and_run(root)
                self.assertEqual(executed.returncode, 0, executed.stderr)
            first_rows = self.read_rows(first / "data/outcomes.csv")
            second_rows = self.read_rows(second / "data/outcomes.csv")
            self.assertEqual(list(first_rows[0]), list(second_rows[0]))
            self.assertNotEqual(
                [row["value"] for row in first_rows],
                [row["value"] for row in second_rows],
            )

    def test_existing_plan_is_not_replaced(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "bundle"
            self.prepare_bundle(root)
            arguments = (
                "plan",
                "--spec",
                root / "experiment.json",
                "--output-dir",
                root / "design",
            )
            first = self.run_cli(*arguments)
            self.assertEqual(first.returncode, 0, first.stderr)
            before = {path.name: path.read_bytes() for path in (root / "design").iterdir()}
            second = self.run_cli(*arguments)
            self.assertEqual(second.returncode, 2)
            self.assertIn("already exists", second.stderr)
            after = {path.name: path.read_bytes() for path in (root / "design").iterdir()}
            self.assertEqual(before, after)

    def test_nonfinite_model_output_is_retained_as_failed_evidence(self) -> None:
        bad_model = '''
import platform
MODEL_METADATA = {
    "modelId": "nonfinite-model",
    "modelVersion": "1.0.0",
    "engine": "python-standard-library",
    "engineVersion": platform.python_version(),
    "rng": "random.Random-MT19937",
    "rngVersion": platform.python_version(),
    "reproducibility": "exact-within-locked-environment",
}
def simulate(run):
    return {"outcomes": {"fill_rate": float("nan"), "unmet_units": 0.0}}
'''
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "bundle"
            self.prepare_bundle(root, model_text=bad_model)
            _, executed = self.plan_and_run(root)
            self.assertEqual(executed.returncode, 2)
            result = json.loads(executed.stdout)
            self.assertEqual(result["status"], "incomplete")
            rows = self.read_rows(root / "data/runs.csv")
            self.assertTrue(rows)
            self.assertEqual({row["status"] for row in rows}, {"failed"})
            self.assertEqual(self.read_rows(root / "data/outcomes.csv"), [])
            manifest = json.loads(
                (root / "execution-manifest.json").read_text("utf-8")
            )
            self.assertEqual(
                manifest["runCounts"]["failed"], manifest["runCounts"]["planned"]
            )

    def test_dataclass_model_import_is_supported(self) -> None:
        model = '''
from __future__ import annotations
import platform
from dataclasses import dataclass
@dataclass
class Result:
    fill_rate: float
MODEL_METADATA = {
    "modelId": "dataclass-model", "modelVersion": "1.0.0",
    "engine": "python-standard-library", "engineVersion": platform.python_version(),
    "rng": "none", "rngVersion": platform.python_version(),
    "reproducibility": "bitwise",
}
def simulate(run):
    value = Result(0.5)
    return {"outcomes": {"fill_rate": value.fill_rate, "unmet_units": 1.0}}
'''
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "bundle"
            self.prepare_bundle(root, model_text=model)
            _, executed = self.plan_and_run(root)
            self.assertEqual(executed.returncode, 0, executed.stderr)

    def test_reviewed_source_bytes_override_timestamp_valid_stale_bytecode(self) -> None:
        model = '''
import platform
MODEL_METADATA = {
    "modelId": "stale-bytecode-model", "modelVersion": "1.0.0",
    "engine": "python-standard-library", "engineVersion": platform.python_version(),
    "rng": "none", "rngVersion": platform.python_version(),
    "reproducibility": "bitwise",
}
def simulate(run):
    return {"outcomes": {"fill_rate": 0.9, "unmet_units": 1.0}}
'''
        stale_model = model.replace("0.9", "0.1")
        stale_bytes = stale_model.encode("utf-8")
        reviewed_bytes = model.encode("utf-8")
        self.assertEqual(len(stale_bytes), len(reviewed_bytes))
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "bundle"
            self.prepare_bundle(root)
            model_path = root / "model.py"
            frozen_timestamp = 1_700_000_000
            model_path.write_bytes(stale_bytes)
            os.utime(model_path, (frozen_timestamp, frozen_timestamp))
            cached_path = Path(
                py_compile.compile(
                    str(model_path),
                    doraise=True,
                    invalidation_mode=py_compile.PycInvalidationMode.TIMESTAMP,
                )
            )
            self.assertTrue(cached_path.is_file())

            model_path.write_bytes(reviewed_bytes)
            os.utime(model_path, (frozen_timestamp, frozen_timestamp))
            _, executed = self.plan_and_run(root)
            self.assertEqual(executed.returncode, 0, executed.stderr)
            fill_rates = {
                row["value"]
                for row in self.read_rows(root / "data/outcomes.csv")
                if row["outcome_name"] == "fill_rate"
            }
            self.assertEqual(fill_rates, {"0.90000000000000002"})
            manifest = json.loads(
                (root / "execution-manifest.json").read_text(encoding="utf-8")
            )
            self.assertEqual(
                manifest["model"]["sha256"], hashlib.sha256(reviewed_bytes).hexdigest()
            )

    def test_time_unit_is_required_and_propagated_for_time_bearing_rows(self) -> None:
        model = '''
import platform
MODEL_METADATA = {
    "modelId": "time-bearing-model", "modelVersion": "1.0.0",
    "engine": "python-standard-library", "engineVersion": platform.python_version(),
    "rng": "none", "rngVersion": platform.python_version(),
    "reproducibility": "bitwise",
}
def simulate(run):
    return {
        "outcomes": {"fill_rate": 0.5, "unmet_units": 1.0},
        "observations": [{
            "sim_time": 1.25, "variable": "queue_length", "value": 2.0, "unit": "item"
        }],
        "events": [{"sim_time": 1.5, "event_type": "arrival", "payload": {"count": 1}}],
    }
'''
        with tempfile.TemporaryDirectory() as temporary:
            parent = Path(temporary)
            missing = parent / "missing"
            self.prepare_bundle(missing, model_text=model)
            _, missing_run = self.plan_and_run(missing)
            self.assertEqual(missing_run.returncode, 2)
            missing_rows = self.read_rows(missing / "data/runs.csv")
            self.assertEqual({row["status"] for row in missing_rows}, {"failed"})
            self.assertTrue(
                all("experiment.timeUnit" in row["error_message"] for row in missing_rows)
            )

            declared = parent / "declared"
            self.prepare_bundle(
                declared,
                mutate=lambda spec: spec.__setitem__("timeUnit", "hour"),
                model_text=model,
            )
            _, declared_run = self.plan_and_run(declared)
            self.assertEqual(declared_run.returncode, 0, declared_run.stderr)
            observations = self.read_rows(declared / "data/observations.csv")
            events = self.read_rows(declared / "data/events.csv")
            self.assertTrue(observations)
            self.assertTrue(events)
            self.assertEqual({row["time_unit"] for row in observations}, {"hour"})
            self.assertEqual({row["time_unit"] for row in events}, {"hour"})
            dictionary = json.loads(
                (declared / "data-dictionary.json").read_text(encoding="utf-8")
            )
            self.assertEqual(dictionary["declaredTimeUnit"], "hour")
            time_columns = {
                table["path"]: {column["name"]: column for column in table["columns"]}
                for table in dictionary["tables"]
                if table["path"] in {"data/observations.csv", "data/events.csv"}
            }
            self.assertEqual(set(time_columns), {"data/observations.csv", "data/events.csv"})
            for columns in time_columns.values():
                self.assertEqual(columns["time_unit"]["type"], "string")
                self.assertIn("experiment.timeUnit", columns["time_unit"]["description"])

    def test_description_only_challenge_difference_is_rejected(self) -> None:
        def mutate(spec: dict[str, Any]) -> None:
            primary_parameters = json.loads(json.dumps(spec["designPoints"][0]["parameters"]))
            challenge_parameters = json.loads(json.dumps(primary_parameters))
            challenge_parameters[0]["description"] = "Only this non-model prose differs."
            spec["designPoints"][1]["parameters"] = challenge_parameters

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "bundle"
            self.prepare_bundle(root, mutate=mutate)
            planned = self.run_cli(
                "plan", "--spec", root / "experiment.json", "--output-dir", root / "design"
            )
            self.assertEqual(planned.returncode, 2)
            self.assertIn("model parameter value map", planned.stderr)
            self.assertFalse((root / "design").exists())

    def test_source_only_challenge_difference_is_rejected(self) -> None:
        def mutate(spec: dict[str, Any]) -> None:
            primary_parameters = json.loads(json.dumps(spec["designPoints"][0]["parameters"]))
            challenge_parameters = json.loads(json.dumps(primary_parameters))
            challenge_parameters[0]["sourceType"] = "literature"
            spec["designPoints"][1]["parameters"] = challenge_parameters

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "bundle"
            self.prepare_bundle(root, mutate=mutate)
            planned = self.run_cli(
                "plan", "--spec", root / "experiment.json", "--output-dir", root / "design"
            )
            self.assertEqual(planned.returncode, 2)
            self.assertIn("model parameter value map", planned.stderr)
            self.assertFalse((root / "design").exists())

    def test_joint_core_row_budget_rejects_maxima_cartesian_product(self) -> None:
        def mutate(spec: dict[str, Any]) -> None:
            spec["replications"] = 25_000
            while len(spec["outcomes"]) < 100:
                index = len(spec["outcomes"])
                spec["outcomes"].append(
                    {
                        "name": f"metric_{index:03d}",
                        "unit": "1",
                        "description": "Synthetic outcome used to exercise the joint row budget.",
                    }
                )

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "bundle"
            self.prepare_bundle(root, mutate=mutate)
            planned = self.run_cli(
                "plan", "--spec", root / "experiment.json", "--output-dir", root / "design"
            )
            self.assertEqual(planned.returncode, 2)
            self.assertIn("in-memory materialized rows", planned.stderr)
            self.assertIn("joint local-runner limit", planned.stderr)
            self.assertFalse((root / "design").exists())

    def test_optional_rows_consume_remaining_joint_materialized_row_budget(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "bundle"
            spec = self.prepare_bundle(root)
            planned = self.run_cli(
                "plan", "--spec", root / "experiment.json", "--output-dir", root / "design"
            )
            self.assertEqual(planned.returncode, 0, planned.stderr)

            runner = runpy.run_path(str(SCRIPT))
            run_rows = self.read_rows(root / "design/run-plan.csv")
            planned_core_rows = runner["planned_core_row_count"](
                len(run_rows),
                len(spec["scenarios"]) * len(spec["designPoints"]),
                len(spec["outcomes"]),
            )
            command_run = runner["command_run"]
            command_run.__globals__["MAX_IN_MEMORY_MATERIALIZED_ROWS"] = (
                planned_core_rows + 1
            )
            captured_stdout = SimpleNamespace(buffer=io.BytesIO())
            with mock.patch.object(sys, "stdout", captured_stdout):
                return_code = command_run(SimpleNamespace(root=root, model="model.py"))

            self.assertEqual(return_code, 2)
            runs = self.read_rows(root / "data/runs.csv")
            self.assertEqual(sum(row["status"] == "ok" for row in runs), 1)
            self.assertEqual(sum(row["status"] == "failed" for row in runs), len(runs) - 1)
            self.assertTrue(
                all(
                    "joint local-runner limit" in row["error_message"]
                    for row in runs
                    if row["status"] == "failed"
                )
            )
            diagnostics = self.read_rows(root / "data/diagnostics.csv")
            self.assertEqual(len(diagnostics), 1)

    def test_engine_metadata_mismatch_is_rejected_before_execution(self) -> None:
        model = TEMPLATE_MODEL.read_text("utf-8").replace(
            '"engine": "python-standard-library"', '"engine": "simpy"'
        )
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "bundle"
            self.prepare_bundle(root, model_text=model)
            planned = self.run_cli(
                "plan", "--spec", root / "experiment.json", "--output-dir", root / "design"
            )
            self.assertEqual(planned.returncode, 0, planned.stderr)
            executed = self.run_cli("run", "--root", root, "--model", "model.py")
            self.assertEqual(executed.returncode, 2)
            self.assertIn("must exactly match", executed.stderr)
            self.assertFalse((root / "data").exists())

    def test_model_mutation_during_execution_prevents_publication(self) -> None:
        model = '''
import platform
from pathlib import Path
MODEL_METADATA = {
    "modelId": "mutating-model", "modelVersion": "1.0.0",
    "engine": "python-standard-library", "engineVersion": platform.python_version(),
    "rng": "none", "rngVersion": platform.python_version(),
    "reproducibility": "bitwise",
}
def simulate(run):
    path = Path(__file__)
    text = path.read_text(encoding="utf-8")
    if not text.endswith("# mutated\\n"):
        path.write_text(text + "# mutated\\n", encoding="utf-8")
    return {"outcomes": {"fill_rate": 0.5, "unmet_units": 1.0}}
'''
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "bundle"
            self.prepare_bundle(root, model_text=model)
            planned = self.run_cli(
                "plan", "--spec", root / "experiment.json", "--output-dir", root / "design"
            )
            self.assertEqual(planned.returncode, 0, planned.stderr)
            executed = self.run_cli("run", "--root", root, "--model", "model.py")
            self.assertEqual(executed.returncode, 2)
            self.assertIn("changed during execution", executed.stderr)
            self.assertFalse((root / "data").exists())

    def test_invalidating_warning_is_rejected_as_a_failed_run(self) -> None:
        model = '''
import platform
MODEL_METADATA = {
    "modelId": "bad-diagnostic-model", "modelVersion": "1.0.0",
    "engine": "python-standard-library", "engineVersion": platform.python_version(),
    "rng": "none", "rngVersion": platform.python_version(),
    "reproducibility": "bitwise",
}
def simulate(run):
    return {
        "outcomes": {"fill_rate": 0.5, "unmet_units": 1.0},
        "diagnostics": [{
            "check_id": "contradictory-diagnostic", "status": "warn",
            "message": "Invalidating warnings are not allowed.",
            "invalidates_hypotheses": True,
        }],
    }
'''
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "bundle"
            self.prepare_bundle(root, model_text=model)
            _, executed = self.plan_and_run(root)
            self.assertEqual(executed.returncode, 2)
            rows = self.read_rows(root / "data/runs.csv")
            self.assertEqual({row["status"] for row in rows}, {"failed"})
            self.assertEqual(self.read_rows(root / "data/outcomes.csv"), [])

    def test_windows_drive_or_stream_like_model_path_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "bundle"
            self.prepare_bundle(root)
            planned = self.run_cli(
                "plan", "--spec", root / "experiment.json", "--output-dir", root / "design"
            )
            self.assertEqual(planned.returncode, 0, planned.stderr)
            executed = self.run_cli("run", "--root", root, "--model", "C:/outside.py")
            self.assertEqual(executed.returncode, 2)
            self.assertIn("safe relative path", executed.stderr)


if __name__ == "__main__":
    unittest.main()
