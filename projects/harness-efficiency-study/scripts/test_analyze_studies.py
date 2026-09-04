#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

"""Unit tests for the cross-study harness-efficiency analyzer."""

from __future__ import annotations

import csv
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest


MODULE_PATH = Path(__file__).with_name("analyze_studies.py")
SPEC = importlib.util.spec_from_file_location("analyze_studies", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


SCENARIOS = {
    "controlled-harness": ["copilot-cli-copilot-route", "pi-cli-copilot-route"],
    "monthly-economics": ["copilot-proplus-auto", "pi-openai-api-auto"],
    "usage-policy": ["resource-unaware-frontier", "resource-aware-frontier"],
}


def _write_csv(path: Path, fields: list[str], rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def _make_bundle(root: Path, study: str) -> None:
    bundle = root / study
    (bundle / "analysis").mkdir(parents=True)
    (bundle / "data").mkdir(parents=True)
    scenarios = SCENARIOS[study]
    point_id = "low-local-bug" if study == "monthly-economics" else "primary-local-bug"
    parameters = [
        {"name": "workload_name", "value": "local-bug", "unit": "1", "sourceType": "synthetic"},
        {"name": "tasks_per_run", "value": 10, "unit": "task", "sourceType": "synthetic"},
        {"name": "billing_period_tasks", "value": 10, "unit": "task/month", "sourceType": "synthetic"},
    ]
    hypothesis = {
        "hypothesisId": "h1",
        "outcome": "accepted_task_fraction",
        "analysis": {
            "kind": "scenario-contrast",
            "baselineScenarioId": scenarios[0],
            "comparisonScenarioId": scenarios[1],
        },
    }
    experiment_id = f"{study}-fixture"
    spec = {
        "experimentId": experiment_id,
        "scenarios": [{"scenarioId": item, "parameters": []} for item in scenarios],
        "designPoints": [{"designPointId": point_id, "parameters": parameters}],
        "hypotheses": [hypothesis],
    }
    (bundle / "experiment.json").write_text(json.dumps(spec), encoding="utf-8")
    (bundle / "validation-report.json").write_text(
        json.dumps({"ok": True, "releaseEligible": True}), encoding="utf-8"
    )

    outcome_fields = [
        "experiment_id", "run_id", "scenario_id", "design_point_id", "replicate_id",
        "coupling_id", "outcome_name", "value", "unit", "source_type",
    ]
    metrics = {
        scenarios[0]: {
            "accepted_task_fraction": 0.7,
            "external_quality_score": 0.72,
            "policy_violation_fraction": 0.02,
            "provider_cost_usd_per_task": 0.3,
            "marginal_cash_cost_usd_per_task": 0.1,
            "allocated_cash_cost_usd_per_task": 0.5,
            "economic_loss_usd_per_task": 4.0,
            "normalized_provider_cost": 1.0,
            "normalized_cost_per_verified_work": 0.8,
            "wall_seconds_per_task": 100.0,
            "normalized_wall_time": 1.0,
            "human_minutes_per_task": 1.0,
            "uncached_input_tokens_per_task": 1000.0,
            "cache_read_tokens_per_task": 2000.0,
            "cache_write_tokens_per_task": 100.0,
            "tool_schema_tokens_per_task": 500.0,
            "tool_result_tokens_per_task": 300.0,
            "model_calls_per_task": 2.0,
            "tool_calls_per_task": 3.0,
            "retries_per_task": 0.1,
            "compactions_per_task": 0.0,
            "cache_hit_fraction": 0.6,
            "budget_exhausted_fraction": 0.0,
        },
        scenarios[1]: {
            "accepted_task_fraction": 0.8,
            "external_quality_score": 0.82,
            "policy_violation_fraction": 0.01,
            "provider_cost_usd_per_task": 0.2,
            "marginal_cash_cost_usd_per_task": 0.08,
            "allocated_cash_cost_usd_per_task": 0.4,
            "economic_loss_usd_per_task": 3.0,
            "normalized_provider_cost": 0.67,
            "normalized_cost_per_verified_work": 0.5,
            "wall_seconds_per_task": 80.0,
            "normalized_wall_time": 0.8,
            "human_minutes_per_task": 0.8,
            "uncached_input_tokens_per_task": 800.0,
            "cache_read_tokens_per_task": 2200.0,
            "cache_write_tokens_per_task": 80.0,
            "tool_schema_tokens_per_task": 200.0,
            "tool_result_tokens_per_task": 250.0,
            "model_calls_per_task": 2.0,
            "tool_calls_per_task": 2.0,
            "retries_per_task": 0.05,
            "compactions_per_task": 0.0,
            "cache_hit_fraction": 0.7,
            "budget_exhausted_fraction": 0.0,
        },
    }
    outcome_rows: list[dict[str, object]] = []
    for replicate in range(2):
        for scenario in scenarios:
            for outcome, value in metrics[scenario].items():
                outcome_rows.append(
                    {
                        "experiment_id": experiment_id,
                        "run_id": f"{scenario}-{replicate}",
                        "scenario_id": scenario,
                        "design_point_id": point_id,
                        "replicate_id": replicate,
                        "coupling_id": f"pair-{replicate}",
                        "outcome_name": outcome,
                        "value": value,
                        "unit": "1",
                        "source_type": "synthetic",
                    }
                )
    _write_csv(bundle / "data" / "outcomes.csv", outcome_fields, outcome_rows)
    _write_csv(
        bundle / "analysis" / "summary.csv",
        ["experiment_id", "scenario_id", "design_point_id", "outcome_name", "unit", "source_type", "n", "mean", "stddev", "mcse", "min", "p05", "median", "p95", "max"],
        [{"experiment_id": experiment_id, "scenario_id": scenarios[0], "design_point_id": point_id, "outcome_name": "accepted_task_fraction", "unit": "1", "source_type": "synthetic", "n": 2, "mean": 0.7, "stddev": 0, "mcse": 0, "min": 0.7, "p05": 0.7, "median": 0.7, "p95": 0.7, "max": 0.7}],
    )
    result = {
        "hypothesisId": "h1",
        "status": "supports-under-model",
        "threshold": {"operator": "ge", "value": 0.05, "unit": "1"},
        "designPointResults": [
            {
                "designPointId": point_id,
                "role": "challenge",
                "status": "supports",
                "estimate": 0.1,
                "interval": {"low": 0.08, "high": 0.12},
                "mcse": 0.01,
                "sample": {"completePairs": 2},
            }
        ],
        "challengeSearch": {"reversalDesignPointIds": []},
    }
    (bundle / "analysis" / "hypothesis-results.json").write_text(
        json.dumps({"experimentId": experiment_id, "results": [result]}),
        encoding="utf-8",
    )


class AnalyzeStudiesTests(unittest.TestCase):
    def test_validated_bundles_emit_all_outputs_and_correct_deltas(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            runs = root / "runs"
            for study in MODULE.STUDY_NAMES:
                _make_bundle(runs, study)
            output = root / "analysis"
            payload = MODULE.analyze(runs, output)
            expected = {
                "scenario-summary.csv",
                "workload-ranking.csv",
                "pairwise-deltas.csv",
                "pareto-frontier.csv",
                "break-even.csv",
                "study-results.json",
                "report.md",
            }
            self.assertEqual(expected, {path.name for path in output.iterdir()})
            self.assertEqual(payload["outputRows"]["workloadRanking"], 6)
            with (output / "pairwise-deltas.csv").open(encoding="utf-8", newline="") as handle:
                rows = list(csv.DictReader(handle))
            controlled = next(row for row in rows if row["study"] == "controlled-harness")
            self.assertAlmostEqual(float(controlled["estimate_comparison_minus_baseline"]), 0.1)
            with (output / "break-even.csv").open(encoding="utf-8", newline="") as handle:
                break_even = list(csv.DictReader(handle))
            point = next(row for row in break_even if row["record_type"] == "design-point")
            self.assertAlmostEqual(float(point["comparison_minus_baseline_usd_per_task"]), -0.1)
            self.assertEqual(point["lower_cost_scenario"], "pi-openai-api-auto")

    def test_non_release_bundle_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            runs = root / "runs"
            for study in MODULE.STUDY_NAMES:
                _make_bundle(runs, study)
            invalid = runs / "usage-policy" / "validation-report.json"
            invalid.write_text(
                json.dumps({"ok": False, "releaseEligible": False}), encoding="utf-8"
            )
            with self.assertRaisesRegex(MODULE.AnalysisError, "not release eligible"):
                MODULE.analyze(runs, root / "analysis")

    def test_break_even_interpolation_uses_a_sign_change(self) -> None:
        rows = []
        for point, volume, baseline_cost, comparison_cost in (
            ("low", 10, 1.0, 0.2),
            ("high", 100, 0.1, 0.2),
        ):
            for scenario, cost in (
                ("copilot-proplus-auto", baseline_cost),
                ("pi-openai-api-auto", comparison_cost),
            ):
                rows.append(
                    {
                        "study": "monthly-economics",
                        "design_point_id": point,
                        "workload": "same-workload",
                        "scenario_id": scenario,
                        "allocated_cash_cost_usd_per_task": cost,
                    }
                )
        bundle = {
            "spec": {
                "designPoints": [
                    {
                        "designPointId": point,
                        "parameters": [
                            {
                                "name": "workload_name",
                                "value": "same-workload",
                                "unit": "1",
                                "sourceType": "synthetic",
                            },
                            {
                                "name": "billing_period_tasks",
                                "value": volume,
                                "unit": "task/month",
                                "sourceType": "synthetic",
                            },
                        ],
                    }
                    for point, volume in (("low", 10), ("high", 100))
                ]
            }
        }
        result = MODULE._monthly_break_even_rows(rows, bundle)
        interpolation = next(row for row in result if row["record_type"] == "interpolation")
        self.assertEqual(interpolation["interpolation_status"], "linear-interpolation-model-conditional")
        self.assertAlmostEqual(
            float(interpolation["interpolated_break_even_monthly_tasks"]), 90.0
        )

    def test_existing_nonempty_output_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            runs = root / "runs"
            for study in MODULE.STUDY_NAMES:
                _make_bundle(runs, study)
            output = root / "analysis"
            output.mkdir()
            (output / "sentinel.txt").write_text("preserve", encoding="utf-8")
            with self.assertRaisesRegex(MODULE.AnalysisError, "fresh or empty"):
                MODULE.analyze(runs, output)
            self.assertEqual((output / "sentinel.txt").read_text(encoding="utf-8"), "preserve")


if __name__ == "__main__":
    unittest.main()
