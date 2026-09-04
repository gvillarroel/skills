#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Deterministic hand-oracle tests for the offline Pi cost model."""

from __future__ import annotations

import csv
import importlib.util
import json
import math
import sys
import tempfile
import unittest
from pathlib import Path

MODEL_PATH = Path(__file__).resolve().parents[1] / "src" / "pi_cost_elasticity.py"
SPEC = importlib.util.spec_from_file_location("pi_cost_elasticity", MODEL_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"could not load model from {MODEL_PATH}")
model = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = model
SPEC.loader.exec_module(model)


def find_row(
    rows: tuple[dict[str, object], ...], **matches: object
) -> dict[str, object]:
    candidates = [
        row
        for row in rows
        if all(row.get(column) == expected for column, expected in matches.items())
    ]
    if len(candidates) != 1:
        raise AssertionError(f"expected one row for {matches}, found {len(candidates)}")
    return candidates[0]


class RateCardTests(unittest.TestCase):
    def test_model_specific_copilot_thresholds(self) -> None:
        self.assertEqual(model.RATE_CARD["luna"].long_context_threshold_tokens, 200_000)
        self.assertEqual(
            model.RATE_CARD["terra"].long_context_threshold_tokens, 272_000
        )
        self.assertEqual(model.RATE_CARD["sol"].long_context_threshold_tokens, 272_000)

    def test_exact_boundary_is_short_and_next_token_is_long(self) -> None:
        rate = model.RATE_CARD["luna"]
        at_boundary = model.price_call(
            model.CallSpec(call_kind="oracle", cache_write_tokens=200_000),
            rate,
            contrast_id="oracle",
            scenario_id="at",
            role="baseline",
            call_index=1,
        )
        over_boundary = model.price_call(
            model.CallSpec(call_kind="oracle", cache_write_tokens=200_001),
            rate,
            contrast_id="oracle",
            scenario_id="over",
            role="comparison",
            call_index=1,
        )
        self.assertEqual(at_boundary.pricing_tier, "short")
        self.assertEqual(over_boundary.pricing_tier, "long")
        self.assertTrue(
            math.isclose(at_boundary.provider_cost_usd, 0.05, abs_tol=1e-12)
        )
        self.assertTrue(
            math.isclose(over_boundary.provider_cost_usd, 0.1000005, abs_tol=1e-12)
        )

    def test_hand_priced_mixed_partition(self) -> None:
        row = model.price_call(
            model.CallSpec(
                call_kind="oracle",
                input_uncached_tokens=1_000,
                cache_read_tokens=2_000,
                cache_write_tokens=3_000,
                output_tokens=4_000,
            ),
            model.RATE_CARD["luna"],
            contrast_id="oracle",
            scenario_id="mixed",
            role="baseline",
            call_index=1,
        )
        expected = (
            1_000 * 0.20 + 2_000 * 0.02 + 3_000 * 0.25 + 4_000 * 1.20
        ) / 1_000_000
        self.assertEqual(row.full_input_tokens, 6_000)
        self.assertTrue(math.isclose(row.provider_cost_usd, expected, abs_tol=1e-12))

    def test_negative_tokens_are_rejected(self) -> None:
        with self.assertRaises(ValueError):
            model.price_call(
                model.CallSpec(call_kind="invalid", cache_read_tokens=-1),
                model.RATE_CARD["luna"],
                contrast_id="invalid",
                scenario_id="invalid",
                role="baseline",
                call_index=1,
            )


class PortfolioOracleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.bundle = model.simulate_all()

    def contrast(self, contrast_id: str, model_name: str = "luna") -> dict[str, object]:
        return find_row(
            self.bundle.contrasts, contrast_id=contrast_id, model=model_name
        )

    def scenario(
        self, contrast_id: str, role: str, model_name: str = "luna"
    ) -> dict[str, object]:
        return find_row(
            self.bundle.scenarios,
            contrast_id=contrast_id,
            role=role,
            model=model_name,
        )

    def test_all_plans_are_structurally_ofat(self) -> None:
        for plan in model.build_contrast_plans():
            plan.validate_ofat()
            left = plan.baseline_parameters
            right = plan.comparison_parameters
            differences = [key for key in left if left[key] != right[key]]
            self.assertEqual(differences, [plan.changed_parameter])

        for row in self.bundle.contrasts:
            left = json.loads(str(row["baseline_parameters_json"]))
            right = json.loads(str(row["comparison_parameters_json"]))
            keys = set(left) | set(right)
            differences = [key for key in keys if left.get(key) != right.get(key)]
            self.assertEqual(differences, [row["changed_parameter"]])

    def test_preregistration_exactly_matches_runtime_plans(self) -> None:
        source_path = (
            Path(__file__).resolve().parents[1]
            / "source"
            / "pi-cost-elasticity-spec-20260904.json"
        )
        preregistration = json.loads(source_path.read_text(encoding="utf-8"))
        registered = preregistration["scenarios"]
        plans = model.build_contrast_plans()
        self.assertEqual(
            [scenario["id"] for scenario in registered],
            [plan.contrast_id for plan in plans],
        )
        for scenario, plan in zip(registered, plans, strict=True):
            self.assertEqual(scenario["study_family"], plan.study_family)
            self.assertEqual(scenario["changed_parameter"], plan.changed_parameter)
            baseline = dict(scenario["invariants"])
            comparison = dict(scenario["invariants"])
            baseline[scenario["changed_parameter"]] = scenario["baseline_value"]
            comparison[scenario["changed_parameter"]] = scenario["comparison_value"]
            self.assertEqual(baseline, plan.baseline_parameters)
            self.assertEqual(comparison, plan.comparison_parameters)

    def test_ledger_partition_and_cost_reconcile(self) -> None:
        for row in self.bundle.ledger:
            self.assertEqual(
                row["full_input_tokens"],
                row["input_uncached_tokens"]
                + row["cache_read_tokens"]
                + row["cache_write_tokens"],
            )
            components = (
                row["input_uncached_cost_usd"]
                + row["cache_read_cost_usd"]
                + row["cache_write_cost_usd"]
                + row["output_cost_usd"]
            )
            self.assertTrue(
                math.isclose(
                    row["provider_cost_usd"], components, rel_tol=0.0, abs_tol=1e-15
                )
            )
            expected_tier = (
                "long"
                if row["full_input_tokens"] > row["long_context_threshold_tokens"]
                else "short"
            )
            self.assertEqual(row["pricing_tier"], expected_tier)

    def test_stable_system_1k_ten_call_oracles(self) -> None:
        expected = {"luna": 0.00043, "terra": 0.0043, "sol": 0.0086}
        for model_name, delta in expected.items():
            row = self.contrast("stable-system-10-calls", model_name)
            self.assertTrue(
                math.isclose(row["cost_delta_usd"], delta, abs_tol=1e-12),
                (model_name, row["cost_delta_usd"]),
            )

    def test_dynamic_system_1k_ten_call_oracles(self) -> None:
        expected = {"luna": 0.002, "terra": 0.02, "sol": 0.04}
        for model_name, delta in expected.items():
            row = self.contrast("dynamic-system-10-calls", model_name)
            self.assertTrue(
                math.isclose(row["cost_delta_usd"], delta, abs_tol=1e-12),
                (model_name, row["cost_delta_usd"]),
            )

    def test_luna_threshold_crossing_oracles(self) -> None:
        cold = self.contrast("system-threshold-cold")
        warm = self.contrast("system-threshold-warm")
        self.assertTrue(
            math.isclose(cold["baseline_provider_cost_usd"], 0.051075, abs_tol=1e-12)
        )
        self.assertTrue(
            math.isclose(cold["comparison_provider_cost_usd"], 0.10205, abs_tol=1e-12)
        )
        self.assertTrue(math.isclose(cold["cost_delta_usd"], 0.050975, abs_tol=1e-12))
        self.assertTrue(
            math.isclose(warm["baseline_provider_cost_usd"], 0.00519, abs_tol=1e-12)
        )
        self.assertTrue(
            math.isclose(warm["comparison_provider_cost_usd"], 0.00982, abs_tol=1e-12)
        )
        self.assertTrue(math.isclose(warm["cost_delta_usd"], 0.00463, abs_tol=1e-12))

    def test_fifth_tool_oracles(self) -> None:
        batched = self.contrast("batched-tools-4-to-5")
        sequential = self.contrast("sequential-tools-4-to-5")
        self.assertTrue(
            math.isclose(batched["cost_delta_usd"], 0.000645, abs_tol=1e-12)
        )
        # The exact sequential ledger replays 58.4k accumulated prompt tokens,
        # writes the fifth 2.1k exchange, and emits 100 net extra output tokens.
        self.assertTrue(
            math.isclose(sequential["cost_delta_usd"], 0.001813, abs_tol=1e-12),
            sequential["cost_delta_usd"],
        )
        self.assertEqual(sequential["call_count_delta"], 1)
        self.assertEqual(batched["call_count_delta"], 0)

    def test_fifth_tool_800k_stress_is_long_tier(self) -> None:
        contrast = self.contrast("tool-count-4-vs-5-sequential-800k")
        baseline = self.scenario("tool-count-4-vs-5-sequential-800k", "baseline")
        comparison = self.scenario("tool-count-4-vs-5-sequential-800k", "comparison")
        self.assertEqual(baseline["long_context_calls"], baseline["call_count"])
        self.assertEqual(comparison["long_context_calls"], comparison["call_count"])
        self.assertTrue(
            math.isclose(contrast["cost_delta_usd"], 0.033566, abs_tol=1e-12)
        )

    def test_tool_result_stress_is_distinct_from_local_elasticity(self) -> None:
        local = self.contrast("tool-result-size-plus-1k")
        stress = self.contrast("tool-result-2k-vs-10k-sequential-4")
        self.assertEqual(local["parameter_delta"], 1_000.0)
        self.assertEqual(stress["parameter_delta"], 8_000.0)
        self.assertGreater(stress["cost_delta_usd"], local["cost_delta_usd"])

    def test_long_session_luna_oracles(self) -> None:
        main = self.contrast("long-cap-200k-uncached")
        no_compaction = self.scenario("long-cap-200k-uncached", "baseline")
        cap_uncached = self.scenario("long-cap-200k-uncached", "comparison")
        cap_read = self.scenario(
            "compaction-input-cache-read-sensitivity", "comparison"
        )
        cap_write = self.scenario(
            "compaction-input-cache-write-sensitivity", "comparison"
        )
        self.assertTrue(
            math.isclose(no_compaction["provider_cost_usd"], 1.0204, abs_tol=1e-12)
        )
        self.assertTrue(
            math.isclose(cap_uncached["provider_cost_usd"], 0.5952, abs_tol=1e-12)
        )
        self.assertTrue(
            math.isclose(cap_read["provider_cost_usd"], 0.4512, abs_tol=1e-12)
        )
        self.assertTrue(
            math.isclose(cap_write["provider_cost_usd"], 0.6352, abs_tol=1e-12)
        )
        self.assertTrue(math.isclose(main["savings_usd"], 0.4252, abs_tol=1e-12))
        self.assertEqual(no_compaction["main_call_count"], 39)
        self.assertEqual(no_compaction["long_context_calls"], 30)
        self.assertEqual(no_compaction["max_input_tokens"], 800_000)
        self.assertEqual(cap_uncached["main_call_count"], 39)
        self.assertEqual(cap_uncached["compactions"], 4)
        self.assertEqual(cap_uncached["long_context_calls"], 0)
        self.assertEqual(cap_uncached["max_input_tokens"], 200_000)

    def test_model_threshold_cap_has_expected_compaction_counts(self) -> None:
        expected_compactions = {"luna": 4, "terra": 3, "sol": 3}
        for model_name, count in expected_compactions.items():
            row = self.scenario(
                "long-cap-pricing-threshold-uncached", "comparison", model_name
            )
            self.assertEqual(row["compactions"], count)
            self.assertEqual(row["long_context_calls"], 0)

    def test_compaction_break_even_has_both_probability_units(self) -> None:
        row = find_row(
            self.bundle.break_even,
            contrast_id="long-cap-200k-uncached",
            model="luna",
            failure_loss_usd=100.0,
        )
        self.assertEqual(row["compactions_per_execution"], 4)
        self.assertTrue(
            math.isclose(
                row["break_even_incremental_failure_probability"],
                0.004252,
                abs_tol=1e-12,
            )
        )
        self.assertTrue(
            math.isclose(
                row["break_even_failure_probability_per_compaction_independent"],
                0.001063,
                abs_tol=1e-12,
            )
        )

    def test_scale_rows_are_algebraic_products(self) -> None:
        contrast = self.contrast("stable-system-10-calls")
        scaled = find_row(
            self.bundle.scale_results,
            contrast_id="stable-system-10-calls",
            model="luna",
            volume_executions=1_000_000,
        )
        self.assertTrue(
            math.isclose(
                scaled["cost_delta_usd"],
                contrast["cost_delta_usd"] * 1_000_000,
                abs_tol=1e-9,
            )
        )
        self.assertLess(len(self.bundle.scale_results), 1_000)

    def test_ai_credits_are_value_units_not_discounted(self) -> None:
        for row in self.bundle.scenarios:
            self.assertTrue(
                math.isclose(
                    row["ai_credits"],
                    row["provider_cost_usd"] / 0.01,
                    abs_tol=1e-12,
                )
            )


class BundleWriterTests(unittest.TestCase):
    def test_writer_emits_parseable_complete_bundle(self) -> None:
        bundle = model.simulate_all(models=("luna",))
        expected_files = {
            "call-ledger.csv",
            "scenario-results.csv",
            "contrast-results.csv",
            "scale-results.csv",
            "break-even.csv",
            "study-results.json",
            "data-dictionary.json",
            "explore.sql",
            "summary.md",
            "manifest.json",
        }
        with tempfile.TemporaryDirectory() as raw_dir:
            output_dir = Path(raw_dir)
            manifest = model.write_bundle(output_dir, bundle)
            self.assertEqual(
                {path.name for path in output_dir.iterdir()}, expected_files
            )
            self.assertFalse(manifest["real_pi_or_copilot_calls"])
            self.assertEqual(manifest["row_counts"]["contrasts"], len(bundle.contrasts))

            study = json.loads((output_dir / "study-results.json").read_text("utf-8"))
            self.assertFalse(study["provenance"]["real_pi_or_copilot_calls"])
            self.assertEqual(
                study["rate_card"]["luna"]["long_context_threshold_tokens"], 200_000
            )

            with (output_dir / "call-ledger.csv").open(
                "r", encoding="utf-8", newline=""
            ) as handle:
                rows = list(csv.DictReader(handle))
            self.assertEqual(len(rows), len(bundle.ledger))
            self.assertIn("input_uncached_tokens", rows[0])
            self.assertIn("cache_read_tokens", rows[0])
            self.assertIn("cache_write_tokens", rows[0])
            self.assertIn(
                "zero real Pi", (output_dir / "summary.md").read_text("utf-8")
            )


if __name__ == "__main__":
    unittest.main()
