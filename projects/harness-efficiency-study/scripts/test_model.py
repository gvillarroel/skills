#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Boundary, invariance, and perturbation tests for the harness model."""

from __future__ import annotations

import importlib.util
import math
from pathlib import Path
import sys
import unittest


MODEL_PATH = Path(__file__).resolve().parents[1] / "src" / "model.py"
SPEC = importlib.util.spec_from_file_location("harness_efficiency_model", MODEL_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"could not load model from {MODEL_PATH}")
model = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = model
SPEC.loader.exec_module(model)


def base_parameters() -> dict[str, object]:
    parameters: dict[str, object] = {
        "harness_name": "reference-harness",
        "provider_route": "direct-reference-route",
        "tool_policy": "balanced",
        "cache_policy": "short",
        "compaction_policy": "threshold",
        "billing_mode": "direct",
        "model_policy": "fixed_sol",
        "phase_plan_model": "luna",
        "phase_execute_model": "terra",
        "phase_verify_model": "sol",
        "phase_compact_model": "luna",
        "tasks_per_run": 24,
        "task_complexity_mean": 0.55,
        "task_complexity_sd": 0.16,
        "initial_context_tokens_mean": 4_000.0,
        "initial_context_tokens_sd": 500.0,
        "required_tool_calls_mean": 5.0,
        "required_tool_calls_sd": 1.2,
        "relevant_tool_count": 4,
        "base_model_calls_mean": 2.0,
        "model_calls_per_complexity": 4.0,
        "task_output_tokens_mean": 1_200.0,
        "task_output_tokens_sd": 180.0,
        "tool_result_tokens_mean": 320.0,
        "tool_result_tokens_sd": 70.0,
        "context_growth_tokens_per_call": 160.0,
        "tool_latency_seconds_mean": 1.8,
        "tool_latency_seconds_sd": 0.35,
        "model_latency_base_seconds": 1.0,
        "model_latency_seconds_per_1k_tokens": 0.22,
        "tool_error_probability": 0.05,
        "provider_error_probability": 0.04,
        "session_continuity_probability": 0.96,
        "inter_call_gap_seconds_mean": 8.0,
        "parallelizable_fraction": 0.7,
        "verification_strength": 0.9,
        "verification_noise_sd": 0.08,
        "quality_acceptance_threshold": 0.62,
        "base_quality_logit": 1.8,
        "difficulty_quality_penalty_logit": 1.5,
        "tool_success_quality_weight_logit": 1.1,
        "provider_failure_quality_penalty_logit": 0.7,
        "retry_quality_penalty_logit": 0.08,
        "human_review_probability": 0.25,
        "human_review_minutes_mean": 4.0,
        "human_review_minutes_sd": 0.8,
        "human_rework_minutes_per_rejected_task": 8.0,
        "human_hourly_value_usd": 75.0,
        "failure_cost_usd": 35.0,
        "sla_seconds_per_task": 900.0,
        "sla_penalty_usd_per_minute": 0.5,
        "policy_violation_base_probability": 0.015,
        "policy_violation_tool_scale": 0.3,
        "verified_task_value_usd": 100.0,
        "provider_cost_reference_usd_per_task": 0.25,
        "normalization_acceptance_floor": 0.02,
        "external_tool_cost_usd_per_call": 0.001,
        "failed_request_billable_fraction": 0.2,
        "cache_minimum_tokens": 1_024.0,
        "scenario_profile_effect_scale": 1.0,
        "cache_cost_scale": 1.0,
        "provider_latency_scale": 1.0,
        "quality_offset_logit": 0.0,
        "latency_multiplier": 1.0,
        "tool_efficiency_multiplier": 1.0,
        "prompt_tokens": 1_400.0,
        "orchestration_tokens_per_call": 180.0,
        "registered_tool_count": 10,
        "tool_exposure_fraction": 0.6,
        "tool_schema_tokens_per_tool": 55.0,
        "tool_output_cap_tokens": 600.0,
        "model_output_cap_tokens": 1_500.0,
        "tool_selection_accuracy": 0.97,
        "tool_confusion_penalty_logit": 0.015,
        "failed_tool_result_fraction": 0.12,
        "tool_result_retention_fraction": 0.75,
        "output_retention_fraction": 0.8,
        "cache_retention_seconds": 3_600.0,
        "prefix_stability_probability": 0.97,
        "context_window_tokens": 32_000.0,
        "long_context_threshold_tokens": 16_000.0,
        "long_context_input_multiplier": 1.5,
        "long_context_output_multiplier": 1.2,
        "compaction_trigger_fraction": 0.78,
        "compaction_reserve_tokens": 4_000.0,
        "compaction_keep_tokens": 5_000.0,
        "compaction_summary_fraction": 0.12,
        "compaction_information_loss": 0.08,
        "compaction_cache_reset_probability": 0.8,
        "context_overflow_quality_penalty_logit": 1.0,
        "max_retries": 2,
        "retry_delay_seconds": 0.5,
        "retry_backoff_multiplier": 2.0,
        "parallelism": 4,
        "parallel_overhead_seconds": 0.15,
        "parallel_conflict_probability": 0.02,
        "harness_latency_seconds_per_call": 0.12,
        "human_approval_seconds_per_tool_call": 0.0,
        "subscription_fee_usd_per_period": 20.0,
        "subscription_allowance_usd_per_period": 50.0,
        "billing_period_tasks": 200,
        "overage_multiplier": 1.0,
        "automatic_discount_fraction": 0.0,
        "compaction_enabled": True,
        "overage_enabled": True,
    }
    model_values = {
        "luna": (0.15, 0.75, 0.50, 0.05, 0.60, 2.00),
        "terra": (0.45, 1.00, 1.00, 0.10, 1.25, 4.00),
        "sol": (0.75, 1.30, 2.00, 0.20, 2.50, 8.00),
    }
    for name, (quality, latency, input_rate, read_rate, write_rate, output_rate) in model_values.items():
        parameters[f"{name}_quality_logit"] = quality
        parameters[f"{name}_latency_multiplier"] = latency
        parameters[f"{name}_input_usd_per_million_tokens"] = input_rate
        parameters[f"{name}_cache_read_usd_per_million_tokens"] = read_rate
        parameters[f"{name}_cache_write_usd_per_million_tokens"] = write_rate
        parameters[f"{name}_output_usd_per_million_tokens"] = output_rate
    return parameters


def make_run(parameters: dict[str, object], seed: int = 20260904) -> dict[str, object]:
    return {
        "seed": seed,
        "scenario_id": "test-scenario",
        "design_point_id": "test-design",
        "replicate_id": 1,
        "coupling_id": "paired-1",
        "parameters": parameters,
    }


class HarnessEfficiencyModelTests(unittest.TestCase):
    def test_fixed_seed_is_deterministic(self) -> None:
        run = make_run(base_parameters())
        self.assertEqual(model.simulate(run), model.simulate(run))

    def test_labels_do_not_create_brand_winners(self) -> None:
        first = base_parameters()
        second = dict(first)
        second.update(
            {
                "harness_name": "renamed-harness",
                "provider_route": "renamed-provider-route",
                "tool_policy": "renamed-tool-policy",
                "cache_policy": "renamed-cache-policy",
                "compaction_policy": "renamed-compaction-policy",
            }
        )
        first_outcomes = model.simulate(make_run(first))["outcomes"]
        second_outcomes = model.simulate(make_run(second))["outcomes"]
        self.assertEqual(first_outcomes, second_outcomes)

    def test_output_price_increases_provider_cost_without_changing_tokens(self) -> None:
        low_price = base_parameters()
        high_price = dict(low_price)
        high_price["sol_output_usd_per_million_tokens"] = (
            float(low_price["sol_output_usd_per_million_tokens"]) * 10.0
        )
        low = model.simulate(make_run(low_price))["outcomes"]
        high = model.simulate(make_run(high_price))["outcomes"]
        self.assertEqual(low["output_tokens_per_task"], high["output_tokens_per_task"])
        self.assertGreater(
            high["provider_cost_usd_per_task"], low["provider_cost_usd_per_task"]
        )

    def test_cold_cache_eliminates_reads(self) -> None:
        parameters = base_parameters()
        parameters["cache_policy"] = "cold"
        parameters["cache_retention_seconds"] = 0.0
        outcomes = model.simulate(make_run(parameters))["outcomes"]
        self.assertEqual(0.0, outcomes["cache_read_tokens_per_task"])
        self.assertEqual(0.0, outcomes["cache_hit_fraction"])

    def test_eager_more_tools_increases_schema_and_uncached_input(self) -> None:
        focused = base_parameters()
        focused["cache_retention_seconds"] = 0.0
        focused["registered_tool_count"] = 6
        focused["tool_exposure_fraction"] = 0.5
        eager = dict(focused)
        eager["tool_policy"] = "eager"
        eager["registered_tool_count"] = 30
        eager["tool_exposure_fraction"] = 1.0
        focused_outcomes = model.simulate(make_run(focused))["outcomes"]
        eager_outcomes = model.simulate(make_run(eager))["outcomes"]
        self.assertGreater(
            eager_outcomes["tool_schema_tokens_per_task"],
            focused_outcomes["tool_schema_tokens_per_task"],
        )
        self.assertGreater(
            eager_outcomes["uncached_input_tokens_per_task"],
            focused_outcomes["uncached_input_tokens_per_task"],
        )

    def test_outcome_contract_bounds_and_diagnostics(self) -> None:
        result = model.simulate(make_run(base_parameters(), seed=17))
        outcomes = result["outcomes"]
        self.assertEqual(tuple(outcomes), model.OUTCOME_NAMES)
        self.assertEqual(24, len(outcomes))
        for name, value in outcomes.items():
            self.assertTrue(math.isfinite(value), name)
            self.assertGreaterEqual(value, 0.0, name)
        for name in (
            "accepted_task_fraction",
            "external_quality_score",
            "policy_violation_fraction",
            "cache_hit_fraction",
            "budget_exhausted_fraction",
        ):
            self.assertLessEqual(outcomes[name], 1.0, name)
        for diagnostic in result["diagnostics"]:
            self.assertEqual("pass", diagnostic["status"], diagnostic)
            self.assertFalse(diagnostic["invalidates_hypotheses"], diagnostic)


if __name__ == "__main__":
    unittest.main(verbosity=2)
