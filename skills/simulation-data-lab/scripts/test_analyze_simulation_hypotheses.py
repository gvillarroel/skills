#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

"""Black-box tests for machine-readable simulation hypothesis analysis."""

from __future__ import annotations

import copy
import csv
import json
import math
import shutil
import statistics
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Any

from analyze_simulation_hypotheses import analyze_point
from run_simulation_experiment import SimulationError, canonical_json_bytes, normalize_spec


SKILL_ROOT = Path(__file__).resolve().parent.parent
RUNNER = Path(__file__).with_name("run_simulation_experiment.py")
ANALYZER = Path(__file__).with_name("analyze_simulation_hypotheses.py")
VALIDATOR = Path(__file__).with_name("validate_simulation_bundle.py")
TEMPLATE_SPEC = SKILL_ROOT / "assets/templates/experiment.json"
TEMPLATE_MODEL = SKILL_ROOT / "assets/templates/model.py"


class AnalyzerTests(unittest.TestCase):
    def run_cli(self, script: Path, *arguments: object) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(script), *(str(item) for item in arguments)],
            check=False,
            capture_output=True,
            text=True,
            timeout=60,
        )

    def prepare_bundle(self, root: Path, spec: dict[str, Any]) -> None:
        root.mkdir(parents=True)
        (root / "experiment.json").write_text(
            json.dumps(spec, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )
        shutil.copyfile(TEMPLATE_MODEL, root / "model.py")
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

    def analyze_and_validate(self, root: Path) -> dict[str, Any]:
        analyzed = self.run_cli(ANALYZER, "--root", root)
        self.assertEqual(analyzed.returncode, 0, analyzed.stderr)
        validated = self.run_cli(VALIDATOR, "--root", root)
        self.assertEqual(validated.returncode, 0, validated.stderr)
        return json.loads((root / "analysis/hypothesis-results.json").read_text("utf-8"))

    def template_spec(self) -> dict[str, Any]:
        spec = json.loads(TEMPLATE_SPEC.read_text("utf-8"))
        spec["replications"] = 6
        # Keep the normal-method regression cohort separate from the bounded template.
        spec["hypotheses"][0]["analysis"]["intervalMethod"] = "normal-approximation-bonferroni"
        spec["hypotheses"][0]["analysis"].pop("outcomeBounds", None)
        return spec

    def test_paired_analysis_reports_every_design_point_and_complete_pairs(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "bundle"
            spec = self.template_spec()
            self.prepare_bundle(root, spec)
            report = self.analyze_and_validate(root)
            result = report["results"][0]
            self.assertEqual(
                [(item["designPointId"], item["role"]) for item in result["designPointResults"]],
                [("low-demand", "challenge"), ("typical-demand", "primary")],
            )
            self.assertTrue(
                all(item["sample"]["completePairs"] == 6 for item in result["designPointResults"])
            )
            self.assertTrue(result["challengeSearch"]["performed"])

    def test_unpaired_analysis_uses_independent_samples(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "bundle"
            spec = self.template_spec()
            spec["seedPolicy"] = "independent-by-run"
            spec["hypotheses"][0]["analysis"]["pairing"] = "independent"
            self.prepare_bundle(root, spec)
            report = self.analyze_and_validate(root)
            for point in report["results"][0]["designPointResults"]:
                self.assertIsNone(point["sample"]["completePairs"])
                self.assertEqual(point["interval"]["method"], "normal-wald-unpaired-bonferroni-v3")

    def test_deterministic_analysis_has_no_interval_and_zero_mcse(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "bundle"
            spec = self.template_spec()
            spec["uncertaintyMode"] = "deterministic"
            spec["replications"] = 1
            spec["seedPolicy"] = "independent-by-run"
            analysis = spec["hypotheses"][0]["analysis"]
            analysis["pairing"] = "deterministic"
            analysis["intervalMethod"] = "none"
            analysis["intervalLevel"] = None
            self.prepare_bundle(root, spec)
            report = self.analyze_and_validate(root)
            for point in report["results"][0]["designPointResults"]:
                self.assertIsNone(point["interval"])
                self.assertEqual(point["mcse"], 0.0)

    def test_planner_rejects_unclassified_design_point(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "bundle"
            root.mkdir(parents=True)
            spec = self.template_spec()
            extra = copy.deepcopy(spec["designPoints"][0])
            extra["designPointId"] = "unclassified-demand"
            extra["parameters"][0]["value"] = 80
            spec["designPoints"].append(extra)
            (root / "experiment.json").write_text(
                json.dumps(spec, indent=2) + "\n", encoding="utf-8"
            )
            result = self.run_cli(
                RUNNER,
                "plan",
                "--spec",
                root / "experiment.json",
                "--output-dir",
                root / "design",
            )
            self.assertEqual(result.returncode, 2)
            self.assertIn("must classify every design point", result.stderr)

    def test_not_identifiable_analysis_does_not_invent_an_effect(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "bundle"
            spec = self.template_spec()
            spec["scenarios"] = [spec["scenarios"][0]]
            hypothesis = spec["hypotheses"][0]
            hypothesis["scenarioIds"] = ["baseline-stock"]
            hypothesis["estimand"] = "causal effect of an unspecified policy versus baseline"
            hypothesis["analysis"] = {
                "kind": "not-identifiable",
                "reason": "No intervention scenario or counterfactual mechanism was supplied.",
            }
            self.prepare_bundle(root, spec)
            report = self.analyze_and_validate(root)
            result = report["results"][0]
            self.assertEqual(result["status"], "not-identifiable-from-design")
            self.assertEqual(result["designPointResults"], [])
            self.assertFalse(result["challengeSearch"]["performed"])
            with (root / "data/outcomes.csv").open("r", encoding="utf-8", newline="") as handle:
                self.assertGreater(len(list(csv.DictReader(handle))), 0)

    def synthetic_point(
        self,
        baseline: list[float],
        comparison: list[float],
        *,
        method: str = "normal-approximation-bonferroni",
        level: float = 0.95,
        operator: str = "ge",
        pairing: str = "paired",
    ) -> dict[str, Any]:
        spec = self.template_spec()
        self.assertEqual(len(baseline), len(comparison))
        spec["replications"] = len(baseline)
        analysis = spec["hypotheses"][0]["analysis"]
        analysis["intervalMethod"] = method
        analysis["intervalLevel"] = level
        analysis["pairing"] = pairing
        if pairing == "independent":
            spec["seedPolicy"] = "independent-by-run"
        spec["hypotheses"][0]["practicalThreshold"].update(value=0, operator=operator)
        spec = normalize_spec(spec)
        rows = []
        seeds = {}
        for arm, values in (("baseline-stock", baseline), ("higher-stock", comparison)):
            for index, value in enumerate(values):
                run_id = f"{arm}-{index}"
                rows.append({
                    "run_id": run_id,
                    "coupling_id": f"pair-{index}",
                    "scenario_id": arm,
                    "design_point_id": "typical-demand",
                    "outcome_name": "fill_rate",
                    "value": str(value),
                })
                seeds[run_id] = index
        return analyze_point(
            spec, spec["hypotheses"][0], "typical-demand", "primary", rows, seeds
        )

    def test_zero_observed_variance_never_certifies_stochastic_equality(self) -> None:
        for pairing in ("paired", "independent"):
            for value in (0.0, 1.0):
                with self.subTest(pairing=pairing, value=value):
                    result = self.synthetic_point([value] * 64, [value] * 64, pairing=pairing)
                    self.assertEqual(result["estimate"], 0)
                    self.assertEqual(result["mcse"], 0)
                    self.assertEqual(result["status"], "inconclusive")
                    self.assertIn("zero-observed-contrast-variance", result["inferenceDiagnostics"])

    def test_constant_nonzero_paired_difference_also_requires_an_exact_oracle(self) -> None:
        baseline = [float(i) for i in range(64)]
        result = self.synthetic_point(baseline, [x + 1 for x in baseline])
        self.assertEqual(result["estimate"], 1)
        self.assertEqual(result["status"], "inconclusive")

    def test_small_normal_sample_is_descriptive_only(self) -> None:
        result = self.synthetic_point([0.0, 0.0], [100.0, 101.0])
        self.assertGreater(result["interval"]["low"], 0)
        self.assertEqual(result["status"], "inconclusive")
        self.assertEqual(result["inferenceDiagnostics"], ["insufficient-replications-for-normal-decision"])

    def test_minimum_replication_boundary_is_explicit(self) -> None:
        for count in (29, 30):
            values = [10.0 + index % 2 for index in range(count)]
            point = self.synthetic_point([0.0] * count, values)
            self.assertEqual(point["status"], "inconclusive" if count < 30 else "supports")

    def test_unrepresentable_normal_quantile_fails_with_a_domain_error(self) -> None:
        with self.assertRaisesRegex(SimulationError, "stable normal quantiles"):
            self.synthetic_point(
                [0.0] * 32, [float(i) for i in range(32)], level=math.nextafter(1.0, 0.0)
            )

    def test_bonferroni_changes_a_marginal_pointwise_reversal_to_inconclusive(self) -> None:
        # Balanced offsets give an exact contrast MCSE of one with 32 pairs.
        comparison = [-2.1 + sign * math.sqrt(31) for sign in (-1, 1) for _ in range(16)]
        unadjusted = self.synthetic_point([0.0] * 32, comparison, method="normal-approximation")
        adjusted = self.synthetic_point([0.0] * 32, comparison)
        self.assertAlmostEqual(adjusted["mcse"], 1, places=12)
        self.assertEqual(unadjusted["status"], "challenges")
        self.assertEqual(adjusted["status"], "inconclusive")
        self.assertEqual(adjusted["interval"]["level"], 0.975)
        self.assertAlmostEqual(adjusted["interval"]["high"], 0.141402727604947, places=12)

    def test_family_interval_oracle_for_independent_gaussian_means(self) -> None:
        # Exact normal coverage is a model oracle, not another random test batch.
        alpha, cells = 0.05, 20
        adjusted_q = statistics.NormalDist().inv_cdf(1 - alpha / (2 * cells))
        marginal_coverage = 2 * statistics.NormalDist().cdf(adjusted_q) - 1
        self.assertGreaterEqual(marginal_coverage ** cells, 1 - alpha)
        self.assertLess((1 - alpha) ** cells, 0.36)

    def test_direction_reversal_preserves_interval_decision(self) -> None:
        values = [3 + sign * math.sqrt(31) for sign in (-1, 1) for _ in range(16)]
        increase = self.synthetic_point([0.0] * 32, values)
        decrease = self.synthetic_point(values, [0.0] * 32, operator="le")
        self.assertEqual(increase["status"], "supports")
        self.assertEqual(decrease["status"], "supports")
        self.assertAlmostEqual(increase["estimate"], -decrease["estimate"])
        self.assertAlmostEqual(increase["interval"]["low"], -decrease["interval"]["high"])

    def test_validator_rejects_a_removed_inference_guard(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "bundle"
            self.prepare_bundle(root, self.template_spec())
            report = self.analyze_and_validate(root)
            point = report["results"][0]["designPointResults"][0]
            self.assertIn("insufficient-replications-for-normal-decision", point["inferenceDiagnostics"])
            point["inferenceDiagnostics"] = []
            (root / "analysis/hypothesis-results.json").write_bytes(canonical_json_bytes(report))
            result = self.run_cli(VALIDATOR, "--root", root)
            self.assertEqual(result.returncode, 2)
            self.assertIn("independent recomputation", result.stderr)

    def test_validator_rejects_nonstring_analyzer_identity_without_a_traceback(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "bundle"
            self.prepare_bundle(root, self.template_spec())
            report = self.analyze_and_validate(root)
            report["analyzer"] = []
            (root / "analysis/hypothesis-results.json").write_bytes(canonical_json_bytes(report))
            result = self.run_cli(VALIDATOR, "--root", root)
            self.assertEqual(result.returncode, 2)
            self.assertIn("analyzer", result.stderr)
            self.assertNotIn("Traceback", result.stderr)

    def test_validator_rejects_pointwise_bounds_claimed_as_simultaneous(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "bundle"
            spec = self.template_spec()
            spec["replications"] = 64
            self.prepare_bundle(root, spec)
            report = self.analyze_and_validate(root)
            point = next(p for p in report["results"][0]["designPointResults"] if p["designPointId"] == "typical-demand")
            half_width = 1.959963984540054 * point["mcse"]
            point["interval"].update(low=point["estimate"] - half_width, high=point["estimate"] + half_width)
            (root / "analysis/hypothesis-results.json").write_bytes(canonical_json_bytes(report))
            result = self.run_cli(VALIDATOR, "--root", root)
            self.assertEqual(result.returncode, 2)
            self.assertIn("independent recomputation", result.stderr)


if __name__ == "__main__":
    unittest.main()
