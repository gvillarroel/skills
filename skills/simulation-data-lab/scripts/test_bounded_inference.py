#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

"""Finite-support inference, numerical decision, and replay regression tests."""

from __future__ import annotations

import copy
import json
import math
import tempfile
import unittest
from pathlib import Path

import test_analyze_simulation_hypotheses as cli_tests
from analyze_simulation_hypotheses import analyze_point, bounded_interval
from run_simulation_experiment import SimulationError, canonical_json_bytes, normalize_spec
from validate_simulation_bundle import audit_point_result


def make_case(baseline, comparison, *, pairing="paired", threshold=0.005, operator="ge"):
    spec = json.loads(cli_tests.TEMPLATE_SPEC.read_text("utf-8"))
    spec["replications"] = len(baseline)
    hypothesis = spec["hypotheses"][0]
    hypothesis["practicalThreshold"].update(value=threshold, operator=operator)
    hypothesis["assumptionIds"].append("test-support")
    spec["assumptions"].append({
        "assumptionId": "test-support", "sourceType": "assumed",
        "statement": "Independent replication pairs have a priori arm support [0, 1].",
    })
    analysis = hypothesis["analysis"]
    analysis.update(
        pairing=pairing, intervalMethod="bounded-hoeffding-bonferroni",
        outcomeBounds={
            "baseline": {"low": 0, "high": 1},
            "comparison": {"low": 0, "high": 1},
            "assumptionId": "test-support",
        },
    )
    spec["seedPolicy"] = "paired-across-scenarios" if pairing == "paired" else "independent-by-run"
    rows, seeds = [], {}
    for arm_index, (arm, values) in enumerate((("baseline-stock", baseline), ("higher-stock", comparison))):
        for index, value in enumerate(values):
            run_id = f"{arm}-{index}"
            rows.append({
                "run_id": run_id, "coupling_id": f"pair-{index}", "scenario_id": arm,
                "design_point_id": "typical-demand", "outcome_name": "fill_rate", "value": str(value),
            })
            seeds[run_id] = index if pairing == "paired" else index + arm_index * len(values)
    return spec, rows, seeds


def evaluate(spec, rows, seeds, *, audit=False, version="mean-difference-v3"):
    normalized = normalize_spec(spec)
    args = (normalized, normalized["hypotheses"][0], "typical-demand", "primary", rows, seeds)
    return audit_point_result(*args, version) if audit else analyze_point(*args)


class BoundedInferenceTests(unittest.TestCase):
    def test_formula_matches_weighted_sum_oracle_for_both_pairings(self):
        for pairing in ("paired", "independent"):
            with self.subTest(pairing=pairing):
                spec, rows, seeds = make_case([0.5] * 64, [0.5] * 64, pairing=pairing)
                point = evaluate(spec, rows, seeds)
                # Weighted-sum Hoeffding: sum of squared summand ranges.
                squared_ranges = 4 / 64 if pairing == "paired" else 2 / 64
                oracle = math.sqrt(math.log(80) * squared_ranges / 2)
                self.assertAlmostEqual(point["interval"]["high"], oracle, places=14)
                self.assertAlmostEqual(point["interval"]["low"], -oracle, places=14)
                self.assertEqual(point["inferenceDiagnostics"], [])
                self.assertEqual(point, evaluate(spec, rows, seeds, audit=True))

    def test_zero_events_have_positive_uncertainty_with_nonconstant_support(self):
        spec, rows, seeds = make_case([0] * 32, [0] * 32)
        spec["hypotheses"][0]["analysis"]["outcomeBounds"]["baseline"]["high"] = 0
        point = evaluate(spec, rows, seeds)
        self.assertEqual(point["mcse"], 0)
        self.assertEqual(point["interval"]["low"], 0)
        self.assertGreater(point["interval"]["high"], 0.26)
        self.assertEqual(point["status"], "inconclusive")
        self.assertEqual(point, evaluate(spec, rows, seeds, audit=True))

    def test_fixed_a_priori_support_can_identify_a_constant_contrast(self):
        spec, rows, seeds = make_case([0] * 2, [1] * 2)
        support = spec["hypotheses"][0]["analysis"]["outcomeBounds"]
        support["baseline"]["high"] = 0
        support["comparison"]["low"] = 1
        point = evaluate(spec, rows, seeds)
        self.assertEqual(point["interval"]["low"], 1)
        self.assertEqual(point["interval"]["high"], 1)
        self.assertEqual(point["status"], "supports")

    def test_bounds_are_not_fitted_from_observed_extrema(self):
        spec, rows, seeds = make_case([0] * 32, [0] * 32)
        broad = evaluate(spec, rows, seeds)
        spec["hypotheses"][0]["analysis"]["outcomeBounds"]["comparison"]["high"] = 100
        wide = evaluate(spec, rows, seeds)
        self.assertGreater(wide["interval"]["high"], broad["interval"]["high"])

    def test_out_of_support_samples_fail_both_implementations(self):
        for arm in (0, 1):
            for outside in (-0.01, 1.01, math.nan, math.inf):
                samples = [[0.2, 0.4], [0.3, 0.5]]
                samples[arm][0] = outside
                spec, rows, seeds = make_case(*samples)
                for audit in (False, True):
                    with self.subTest(arm=arm, outside=outside, audit=audit):
                        with self.assertRaises(SimulationError):
                            evaluate(spec, rows, seeds, audit=audit)

    def test_missing_unknown_or_invalid_support_is_rejected_before_planning(self):
        original, _, _ = make_case([0, 0], [1, 1])
        mutations = [
            lambda a: a.pop("outcomeBounds"),
            lambda a: a["outcomeBounds"].update(assumptionId="missing-assumption"),
            lambda a: a["outcomeBounds"]["baseline"].update(low=2),
            lambda a: a["outcomeBounds"]["baseline"].update(low=True),
            lambda a: a["outcomeBounds"]["baseline"].update(high=math.inf),
            lambda a: a["outcomeBounds"]["baseline"].update(low=-1e308, high=1e308),
            lambda a: a["outcomeBounds"].update(baseline={"low": -1e308, "high": 0}, comparison={"low": 0, "high": 1e308}),
            lambda a: a.update(intervalMethod="normal-approximation"),
        ]
        for index, mutate in enumerate(mutations):
            with self.subTest(index=index):
                spec = copy.deepcopy(original)
                mutate(spec["hypotheses"][0]["analysis"])
                with self.assertRaises(SimulationError):
                    normalize_spec(spec)

    def test_unrepresentable_adjusted_level_is_rejected(self):
        spec, rows, seeds = make_case([0, 0], [0.3, 0.5])
        spec["hypotheses"][0]["analysis"]["intervalLevel"] = math.nextafter(1.0, 0.0)
        for audit in (False, True):
            with self.assertRaises(SimulationError):
                evaluate(spec, rows, seeds, audit=audit)

    def test_exchange_of_arms_reverses_interval_and_inequality(self):
        first = make_case([0.1] * 128, [0.9] * 128, threshold=0.1)
        second = make_case([0.9] * 128, [0.1] * 128, threshold=-0.1, operator="le")
        positive, negative = evaluate(*first), evaluate(*second)
        self.assertEqual(positive["status"], "supports")
        self.assertEqual(negative["status"], "supports")
        self.assertEqual(positive["interval"]["low"], -negative["interval"]["high"])

    def test_exact_binomial_enumeration_meets_nominal_coverage(self):
        # Enumerate all sufficient statistics; this is not a seed-dependent pass.
        for n in (2, 8, 32, 64):
            spec, _, _ = make_case([0] * n, [0] * n)
            analysis = spec["hypotheses"][0]["analysis"]
            analysis["outcomeBounds"]["baseline"]["high"] = 0
            intervals = [bounded_interval(analysis, [0] * n, [1] * k + [0] * (n-k), k/n) for k in range(n+1)]
            for p in (0, 0.001, 0.01, 0.1, 0.5, 0.9, 0.99, 1):
                with self.subTest(n=n, p=p):
                    covered = math.fsum(
                        math.comb(n, k) * p**k * (1-p)**(n-k)
                        for k, interval in enumerate(intervals) if interval["low"] <= p <= interval["high"]
                    )
                    self.assertGreaterEqual(covered + 1e-14, 0.975)

    def test_deterministic_nextafter_boundary_is_not_rounded_into_support(self):
        for operator, value in (("ge", math.nextafter(1.0, 0.0)), ("le", math.nextafter(1.0, 2.0))):
            spec, rows, seeds = make_case([0], [value], threshold=1, operator=operator)
            spec.update(uncertaintyMode="deterministic", seedPolicy="independent-by-run")
            analysis = spec["hypotheses"][0]["analysis"]
            analysis.update(pairing="deterministic", intervalMethod="none", intervalLevel=None)
            analysis.pop("outcomeBounds")
            current = evaluate(spec, rows, seeds)
            legacy = evaluate(spec, rows, seeds, audit=True, version="mean-difference-v2")
            self.assertEqual(current["estimate"], value)
            self.assertEqual(current["status"], "challenges")
            self.assertEqual(legacy["status"], "supports")
            self.assertEqual(current, evaluate(spec, rows, seeds, audit=True))

    def test_stochastic_endpoint_nextafter_is_not_rounded(self):
        spec, rows, seeds = make_case([0] * 64, [0.9, 1.0] * 32)
        analysis = spec["hypotheses"][0]["analysis"]
        analysis.update(intervalMethod="normal-approximation")
        analysis.pop("outcomeBounds")
        low = evaluate(spec, rows, seeds)["interval"]["low"]
        spec["hypotheses"][0]["practicalThreshold"]["value"] = math.nextafter(low, math.inf)
        point = evaluate(spec, rows, seeds)
        self.assertEqual(point["status"], "inconclusive")
        self.assertEqual(point, evaluate(spec, rows, seeds, audit=True))

    def test_bounded_bundles_pass_and_tampering_or_legacy_relabeling_fails(self):
        helper = cli_tests.AnalyzerTests()
        for pairing in ("paired", "independent"):
            with tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary) / "bounded"
                spec, _, _ = make_case([0] * 32, [0] * 32, pairing=pairing)
                helper.prepare_bundle(root, spec)
                report = helper.analyze_and_validate(root)
                self.assertEqual(report["analyzer"], "mean-difference-v3")
                for version in ("mean-difference-v1", "mean-difference-v2"):
                    forged = copy.deepcopy(report)
                    forged["analyzer"] = version
                    (root / "analysis/hypothesis-results.json").write_bytes(canonical_json_bytes(forged))
                    rejected = helper.run_cli(cli_tests.VALIDATOR, "--root", root)
                    self.assertEqual(rejected.returncode, 2, rejected.stderr)
                    self.assertIn("requires mean-difference-v3", rejected.stderr)
                forged = copy.deepcopy(report)
                forged["results"][0]["designPointResults"][0]["interval"]["high"] = 0
                (root / "analysis/hypothesis-results.json").write_bytes(canonical_json_bytes(forged))
                rejected = helper.run_cli(cli_tests.VALIDATOR, "--root", root)
                self.assertEqual(rejected.returncode, 2, rejected.stderr)
                self.assertIn("independent recomputation", rejected.stderr)


if __name__ == "__main__":
    unittest.main()
