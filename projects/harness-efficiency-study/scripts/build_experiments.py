#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Generate and drift-check the harness-efficiency experiment contracts."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


ROOT_SEED = 20260904
REPLICATIONS = 200

MODEL_NAMES = ("luna", "terra", "sol")
PRICE_SUFFIXES = (
    "quality_logit",
    "latency_multiplier",
    "input_usd_per_million_tokens",
    "cache_read_usd_per_million_tokens",
    "cache_write_usd_per_million_tokens",
    "output_usd_per_million_tokens",
)

LABEL_PARAMETERS = {
    "harness_name",
    "provider_route",
    "tool_policy",
    "cache_policy",
    "compaction_policy",
    "billing_mode",
    "model_policy",
    "phase_plan_model",
    "phase_execute_model",
    "phase_verify_model",
    "phase_compact_model",
}

DESIGN_PARAMETERS = {
    "tasks_per_run",
    "task_complexity_mean",
    "task_complexity_sd",
    "initial_context_tokens_mean",
    "initial_context_tokens_sd",
    "required_tool_calls_mean",
    "required_tool_calls_sd",
    "relevant_tool_count",
    "registered_tool_count",
    "base_model_calls_mean",
    "model_calls_per_complexity",
    "task_output_tokens_mean",
    "task_output_tokens_sd",
    "tool_result_tokens_mean",
    "tool_result_tokens_sd",
    "context_growth_tokens_per_call",
    "tool_latency_seconds_mean",
    "tool_latency_seconds_sd",
    "model_latency_base_seconds",
    "model_latency_seconds_per_1k_tokens",
    "tool_error_probability",
    "provider_error_probability",
    "session_continuity_probability",
    "inter_call_gap_seconds_mean",
    "parallelizable_fraction",
    "verification_strength",
    "verification_noise_sd",
    "quality_acceptance_threshold",
    "base_quality_logit",
    "difficulty_quality_penalty_logit",
    "tool_success_quality_weight_logit",
    "provider_failure_quality_penalty_logit",
    "retry_quality_penalty_logit",
    "human_review_probability",
    "human_review_minutes_mean",
    "human_review_minutes_sd",
    "human_rework_minutes_per_rejected_task",
    "human_hourly_value_usd",
    "failure_cost_usd",
    "sla_seconds_per_task",
    "sla_penalty_usd_per_minute",
    "policy_violation_base_probability",
    "policy_violation_tool_scale",
    "verified_task_value_usd",
    "provider_cost_reference_usd_per_task",
    "normalization_acceptance_floor",
    "external_tool_cost_usd_per_call",
    "failed_request_billable_fraction",
    "cache_minimum_tokens",
    "scenario_profile_effect_scale",
    "cache_cost_scale",
    "provider_latency_scale",
    # Volume is epistemic in this study, so it belongs to design points.
    "billing_period_tasks",
}

SCENARIO_PARAMETERS = {
    "quality_offset_logit",
    "latency_multiplier",
    "tool_efficiency_multiplier",
    "prompt_tokens",
    "orchestration_tokens_per_call",
    "tool_exposure_fraction",
    "tool_schema_tokens_per_tool",
    "tool_output_cap_tokens",
    "model_output_cap_tokens",
    "tool_selection_accuracy",
    "tool_confusion_penalty_logit",
    "failed_tool_result_fraction",
    "tool_result_retention_fraction",
    "output_retention_fraction",
    "cache_retention_seconds",
    "prefix_stability_probability",
    "context_window_tokens",
    "long_context_threshold_tokens",
    "long_context_input_multiplier",
    "long_context_output_multiplier",
    "compaction_enabled",
    "compaction_trigger_fraction",
    "compaction_reserve_tokens",
    "compaction_keep_tokens",
    "compaction_summary_fraction",
    "compaction_information_loss",
    "compaction_cache_reset_probability",
    "context_overflow_quality_penalty_logit",
    "max_retries",
    "retry_delay_seconds",
    "retry_backoff_multiplier",
    "parallelism",
    "parallel_overhead_seconds",
    "parallel_conflict_probability",
    "harness_latency_seconds_per_call",
    "human_approval_seconds_per_tool_call",
    "subscription_fee_usd_per_period",
    "subscription_allowance_usd_per_period",
    "overage_enabled",
    "overage_multiplier",
    "automatic_discount_fraction",
}

MODEL_PARAMETERS = {f"{model}_{suffix}" for model in MODEL_NAMES for suffix in PRICE_SUFFIXES}
REQUIRED_PARAMETERS = LABEL_PARAMETERS | DESIGN_PARAMETERS | SCENARIO_PARAMETERS | MODEL_PARAMETERS


UNITS: dict[str, str] = {
    "tasks_per_run": "task/run",
    "task_complexity_mean": "1",
    "task_complexity_sd": "1",
    "initial_context_tokens_mean": "token/task",
    "initial_context_tokens_sd": "token/task",
    "required_tool_calls_mean": "call/task",
    "required_tool_calls_sd": "call/task",
    "relevant_tool_count": "tool",
    "base_model_calls_mean": "call/task",
    "model_calls_per_complexity": "call/task",
    "task_output_tokens_mean": "token/task",
    "task_output_tokens_sd": "token/task",
    "tool_result_tokens_mean": "token/call",
    "tool_result_tokens_sd": "token/call",
    "context_growth_tokens_per_call": "token/call",
    "tool_latency_seconds_mean": "s/call",
    "tool_latency_seconds_sd": "s/call",
    "model_latency_base_seconds": "s/call",
    "model_latency_seconds_per_1k_tokens": "s/1k-token",
    "tool_error_probability": "1",
    "provider_error_probability": "1",
    "session_continuity_probability": "1",
    "inter_call_gap_seconds_mean": "s",
    "parallelizable_fraction": "1",
    "verification_strength": "1",
    "verification_noise_sd": "1",
    "quality_acceptance_threshold": "1",
    "base_quality_logit": "logit",
    "difficulty_quality_penalty_logit": "logit",
    "tool_success_quality_weight_logit": "logit",
    "provider_failure_quality_penalty_logit": "logit",
    "retry_quality_penalty_logit": "logit/retry",
    "human_review_probability": "1",
    "human_review_minutes_mean": "min/task",
    "human_review_minutes_sd": "min/task",
    "human_rework_minutes_per_rejected_task": "min/rejected-task",
    "human_hourly_value_usd": "USD/h",
    "failure_cost_usd": "USD/rejected-task",
    "sla_seconds_per_task": "s/task",
    "sla_penalty_usd_per_minute": "USD/min",
    "policy_violation_base_probability": "1",
    "policy_violation_tool_scale": "1/tool",
    "verified_task_value_usd": "USD/accepted-task",
    "provider_cost_reference_usd_per_task": "USD/task",
    "normalization_acceptance_floor": "1",
    "external_tool_cost_usd_per_call": "USD/call",
    "failed_request_billable_fraction": "1",
    "cache_minimum_tokens": "token",
    "scenario_profile_effect_scale": "1",
    "cache_cost_scale": "1",
    "provider_latency_scale": "1",
    "billing_period_tasks": "task/period",
    "quality_offset_logit": "logit",
    "latency_multiplier": "1",
    "tool_efficiency_multiplier": "1",
    "prompt_tokens": "token/call",
    "orchestration_tokens_per_call": "token/call",
    "registered_tool_count": "tool",
    "tool_exposure_fraction": "1",
    "tool_schema_tokens_per_tool": "token/tool/call",
    "tool_output_cap_tokens": "token/call",
    "model_output_cap_tokens": "token/call",
    "tool_selection_accuracy": "1",
    "tool_confusion_penalty_logit": "logit",
    "failed_tool_result_fraction": "1",
    "tool_result_retention_fraction": "1",
    "output_retention_fraction": "1",
    "cache_retention_seconds": "s",
    "prefix_stability_probability": "1",
    "context_window_tokens": "token",
    "long_context_threshold_tokens": "token",
    "long_context_input_multiplier": "1",
    "long_context_output_multiplier": "1",
    "compaction_enabled": "1",
    "compaction_trigger_fraction": "1",
    "compaction_reserve_tokens": "token",
    "compaction_keep_tokens": "token",
    "compaction_summary_fraction": "1",
    "compaction_information_loss": "1",
    "compaction_cache_reset_probability": "1",
    "context_overflow_quality_penalty_logit": "logit",
    "max_retries": "retry",
    "retry_delay_seconds": "s",
    "retry_backoff_multiplier": "1",
    "parallelism": "call",
    "parallel_overhead_seconds": "s/batch",
    "parallel_conflict_probability": "1",
    "harness_latency_seconds_per_call": "s/call",
    "human_approval_seconds_per_tool_call": "s/call",
    "subscription_fee_usd_per_period": "USD/period",
    "subscription_allowance_usd_per_period": "USD/period",
    "overage_enabled": "1",
    "overage_multiplier": "1",
    "automatic_discount_fraction": "1",
}
for model in MODEL_NAMES:
    UNITS[f"{model}_quality_logit"] = "logit"
    UNITS[f"{model}_latency_multiplier"] = "1"
    for kind in ("input", "cache_read", "cache_write", "output"):
        UNITS[f"{model}_{kind}_usd_per_million_tokens"] = "USD/1M-token"


OUTCOMES = [
    ("accepted_task_fraction", "1", "Fraction of tasks accepted by the fixed external verifier."),
    ("external_quality_score", "1", "Mean external-verifier quality score."),
    ("policy_violation_fraction", "1", "Fraction of tasks with a simulated tool-policy violation."),
    ("provider_cost_usd_per_task", "USD/task", "Token-rate ledger cost, independent of cash settlement."),
    ("marginal_cash_cost_usd_per_task", "USD/task", "Incremental cash charge after allowance accounting."),
    ("allocated_cash_cost_usd_per_task", "USD/task", "Subscription and overage cash allocated across period tasks."),
    ("economic_loss_usd_per_task", "USD/task", "Cash, human time, SLA penalty, and expected failure loss."),
    ("normalized_provider_cost", "1", "Provider ledger cost divided by the declared reference cost."),
    ("normalized_cost_per_verified_work", "1", "Economic loss normalized by accepted work and reference cost."),
    ("wall_seconds_per_task", "s/task", "Simulated critical-path duration."),
    ("normalized_wall_time", "1", "Wall time divided by the SLA reference."),
    ("human_minutes_per_task", "min/task", "Human review and rework time."),
    ("uncached_input_tokens_per_task", "token/task", "Input tokens not served from cache."),
    ("cache_read_tokens_per_task", "token/task", "Input tokens billed as cache reads."),
    ("cache_write_tokens_per_task", "token/task", "Input tokens billed as cache writes."),
    ("output_tokens_per_task", "token/task", "Generated output tokens."),
    ("tool_schema_tokens_per_task", "token/task", "Serialized tool-schema tokens exposed to the model."),
    ("tool_result_tokens_per_task", "token/task", "Retained tool-result tokens."),
    ("model_calls_per_task", "call/task", "Model calls including retries and compaction."),
    ("tool_calls_per_task", "call/task", "Tool calls including retries."),
    ("retries_per_task", "retry/task", "Tool or provider retries."),
    ("compactions_per_task", "compaction/task", "Context compactions."),
    ("cache_hit_fraction", "1", "Eligible input fraction served from cache."),
    ("budget_exhausted_fraction", "1", "Fraction of tasks terminated at the hard budget."),
]
OUTCOME_UNITS = {name: unit for name, unit, _ in OUTCOMES}


BASE_DESIGN: dict[str, Any] = {
    "tasks_per_run": 4,
    "task_complexity_mean": 0.50,
    "task_complexity_sd": 0.12,
    "initial_context_tokens_mean": 48000,
    "initial_context_tokens_sd": 9000,
    "required_tool_calls_mean": 18,
    "required_tool_calls_sd": 4,
    "relevant_tool_count": 6,
    "registered_tool_count": 40,
    "base_model_calls_mean": 8,
    "model_calls_per_complexity": 18,
    "task_output_tokens_mean": 4500,
    "task_output_tokens_sd": 900,
    "tool_result_tokens_mean": 2200,
    "tool_result_tokens_sd": 700,
    "context_growth_tokens_per_call": 3500,
    "tool_latency_seconds_mean": 1.4,
    "tool_latency_seconds_sd": 0.35,
    "model_latency_base_seconds": 1.3,
    "model_latency_seconds_per_1k_tokens": 0.10,
    "tool_error_probability": 0.055,
    "provider_error_probability": 0.018,
    "session_continuity_probability": 0.72,
    "inter_call_gap_seconds_mean": 180,
    "parallelizable_fraction": 0.46,
    "verification_strength": 0.88,
    "verification_noise_sd": 0.045,
    "quality_acceptance_threshold": 0.68,
    "base_quality_logit": 0.82,
    "difficulty_quality_penalty_logit": 1.25,
    "tool_success_quality_weight_logit": 0.78,
    "provider_failure_quality_penalty_logit": 0.90,
    "retry_quality_penalty_logit": 0.12,
    "human_review_probability": 0.28,
    "human_review_minutes_mean": 9.0,
    "human_review_minutes_sd": 2.5,
    "human_rework_minutes_per_rejected_task": 18.0,
    "human_hourly_value_usd": 90.0,
    "failure_cost_usd": 60.0,
    "sla_seconds_per_task": 180.0,
    "sla_penalty_usd_per_minute": 0.75,
    "policy_violation_base_probability": 0.002,
    "policy_violation_tool_scale": 0.0003,
    "verified_task_value_usd": 125.0,
    "provider_cost_reference_usd_per_task": 1.0,
    "normalization_acceptance_floor": 0.10,
    "external_tool_cost_usd_per_call": 0.002,
    "failed_request_billable_fraction": 0.80,
    "cache_minimum_tokens": 1024,
    "scenario_profile_effect_scale": 1.0,
    "cache_cost_scale": 1.0,
    "provider_latency_scale": 1.0,
    "billing_period_tasks": 300,
}


WORKLOAD_OVERRIDES: dict[str, dict[str, Any]] = {
    "localized-bug": {"task_complexity_mean": 0.28, "initial_context_tokens_mean": 18000, "initial_context_tokens_sd": 4000, "required_tool_calls_mean": 8, "required_tool_calls_sd": 2, "relevant_tool_count": 4, "registered_tool_count": 18, "base_model_calls_mean": 5, "model_calls_per_complexity": 9, "task_output_tokens_mean": 1800, "task_output_tokens_sd": 350, "tool_result_tokens_mean": 900, "tool_result_tokens_sd": 250, "context_growth_tokens_per_call": 1100, "tool_latency_seconds_mean": 0.8, "parallelizable_fraction": 0.25, "verification_strength": 0.90, "quality_acceptance_threshold": 0.62, "human_review_minutes_mean": 5.0, "failure_cost_usd": 18.0, "sla_seconds_per_task": 90.0, "session_continuity_probability": 0.88, "inter_call_gap_seconds_mean": 45},
    "test-debug": {"task_complexity_mean": 0.38, "initial_context_tokens_mean": 28000, "required_tool_calls_mean": 16, "required_tool_calls_sd": 3, "relevant_tool_count": 5, "registered_tool_count": 24, "base_model_calls_mean": 7, "model_calls_per_complexity": 14, "task_output_tokens_mean": 2700, "tool_result_tokens_mean": 1600, "context_growth_tokens_per_call": 1900, "tool_latency_seconds_mean": 1.0, "parallelizable_fraction": 0.32, "verification_strength": 0.95, "quality_acceptance_threshold": 0.66, "human_review_minutes_mean": 6.0, "failure_cost_usd": 25.0, "sla_seconds_per_task": 135.0, "session_continuity_probability": 0.90, "inter_call_gap_seconds_mean": 35},
    "multi-file-feature": {"task_complexity_mean": 0.62, "initial_context_tokens_mean": 62000, "initial_context_tokens_sd": 11000, "required_tool_calls_mean": 26, "required_tool_calls_sd": 5, "relevant_tool_count": 8, "registered_tool_count": 55, "base_model_calls_mean": 10, "model_calls_per_complexity": 22, "task_output_tokens_mean": 6500, "task_output_tokens_sd": 1200, "tool_result_tokens_mean": 2500, "context_growth_tokens_per_call": 4500, "tool_latency_seconds_mean": 1.2, "parallelizable_fraction": 0.48, "verification_strength": 0.88, "quality_acceptance_threshold": 0.71, "human_review_minutes_mean": 12.0, "failure_cost_usd": 68.0, "sla_seconds_per_task": 270.0, "session_continuity_probability": 0.68, "inter_call_gap_seconds_mean": 240},
    "repository-refactor": {"task_complexity_mean": 0.74, "initial_context_tokens_mean": 92000, "initial_context_tokens_sd": 16000, "required_tool_calls_mean": 36, "required_tool_calls_sd": 7, "relevant_tool_count": 9, "registered_tool_count": 80, "base_model_calls_mean": 13, "model_calls_per_complexity": 27, "task_output_tokens_mean": 8200, "task_output_tokens_sd": 1500, "tool_result_tokens_mean": 2900, "context_growth_tokens_per_call": 6500, "tool_latency_seconds_mean": 1.3, "parallelizable_fraction": 0.54, "verification_strength": 0.92, "quality_acceptance_threshold": 0.74, "human_review_minutes_mean": 16.0, "failure_cost_usd": 95.0, "sla_seconds_per_task": 360.0, "session_continuity_probability": 0.58, "inter_call_gap_seconds_mean": 420},
    "external-integration": {"task_complexity_mean": 0.68, "initial_context_tokens_mean": 68000, "required_tool_calls_mean": 32, "required_tool_calls_sd": 7, "relevant_tool_count": 13, "registered_tool_count": 120, "base_model_calls_mean": 11, "model_calls_per_complexity": 24, "task_output_tokens_mean": 6800, "tool_result_tokens_mean": 3800, "tool_result_tokens_sd": 1200, "context_growth_tokens_per_call": 5200, "tool_latency_seconds_mean": 2.0, "tool_latency_seconds_sd": 0.8, "tool_error_probability": 0.11, "parallelizable_fraction": 0.58, "verification_strength": 0.82, "quality_acceptance_threshold": 0.72, "human_review_probability": 0.38, "human_review_minutes_mean": 18.0, "failure_cost_usd": 115.0, "sla_seconds_per_task": 420.0, "session_continuity_probability": 0.46, "inter_call_gap_seconds_mean": 720},
    "ci-browser": {"task_complexity_mean": 0.65, "initial_context_tokens_mean": 52000, "required_tool_calls_mean": 40, "required_tool_calls_sd": 9, "relevant_tool_count": 10, "registered_tool_count": 75, "base_model_calls_mean": 10, "model_calls_per_complexity": 22, "task_output_tokens_mean": 5400, "tool_result_tokens_mean": 4400, "tool_result_tokens_sd": 1400, "context_growth_tokens_per_call": 4700, "tool_latency_seconds_mean": 3.0, "tool_latency_seconds_sd": 1.0, "tool_error_probability": 0.13, "parallelizable_fraction": 0.66, "verification_strength": 0.96, "quality_acceptance_threshold": 0.72, "human_review_probability": 0.35, "human_review_minutes_mean": 15.0, "failure_cost_usd": 85.0, "sla_seconds_per_task": 480.0, "session_continuity_probability": 0.52, "inter_call_gap_seconds_mean": 360},
    "long-session": {"task_complexity_mean": 0.86, "initial_context_tokens_mean": 180000, "initial_context_tokens_sd": 32000, "required_tool_calls_mean": 50, "required_tool_calls_sd": 9, "relevant_tool_count": 11, "registered_tool_count": 95, "base_model_calls_mean": 16, "model_calls_per_complexity": 34, "task_output_tokens_mean": 14000, "task_output_tokens_sd": 2400, "tool_result_tokens_mean": 3700, "tool_result_tokens_sd": 1000, "context_growth_tokens_per_call": 10500, "tool_latency_seconds_mean": 1.5, "parallelizable_fraction": 0.42, "verification_strength": 0.88, "quality_acceptance_threshold": 0.80, "human_review_probability": 0.45, "human_review_minutes_mean": 24.0, "failure_cost_usd": 150.0, "sla_seconds_per_task": 720.0, "session_continuity_probability": 0.76, "inter_call_gap_seconds_mean": 300},
    "parallel-analysis": {"task_complexity_mean": 0.55, "initial_context_tokens_mean": 76000, "initial_context_tokens_sd": 13000, "required_tool_calls_mean": 38, "required_tool_calls_sd": 7, "relevant_tool_count": 7, "registered_tool_count": 48, "base_model_calls_mean": 9, "model_calls_per_complexity": 19, "task_output_tokens_mean": 7200, "tool_result_tokens_mean": 3100, "context_growth_tokens_per_call": 4300, "tool_latency_seconds_mean": 1.6, "parallelizable_fraction": 0.86, "verification_strength": 0.84, "quality_acceptance_threshold": 0.68, "human_review_minutes_mean": 10.0, "failure_cost_usd": 58.0, "sla_seconds_per_task": 240.0, "session_continuity_probability": 0.70, "inter_call_gap_seconds_mean": 120},
}


MODEL_VALUES = {
    "luna_quality_logit": 0.60,
    "luna_latency_multiplier": 0.65,
    "luna_input_usd_per_million_tokens": 0.20,
    "luna_cache_read_usd_per_million_tokens": 0.02,
    "luna_cache_write_usd_per_million_tokens": 0.25,
    "luna_output_usd_per_million_tokens": 1.20,
    "terra_quality_logit": 1.15,
    "terra_latency_multiplier": 1.00,
    "terra_input_usd_per_million_tokens": 2.00,
    "terra_cache_read_usd_per_million_tokens": 0.20,
    "terra_cache_write_usd_per_million_tokens": 2.50,
    "terra_output_usd_per_million_tokens": 12.00,
    "sol_quality_logit": 1.48,
    "sol_latency_multiplier": 1.45,
    "sol_input_usd_per_million_tokens": 4.00,
    "sol_cache_read_usd_per_million_tokens": 0.40,
    "sol_cache_write_usd_per_million_tokens": 5.00,
    "sol_output_usd_per_million_tokens": 20.00,
}

LITERATURE_SCENARIO_FIELDS = {
    "subscription_fee_usd_per_period",
    "subscription_allowance_usd_per_period",
    "automatic_discount_fraction",
    "long_context_threshold_tokens",
    "context_window_tokens",
} | {
    name
    for name in MODEL_PARAMETERS
    if "_usd_per_million_tokens" in name
}


SOURCE_URLS = [
    "https://docs.github.com/en/copilot/reference/copilot-billing/models-and-pricing",
    "https://docs.github.com/en/copilot/concepts/billing/usage-based-billing-for-individuals",
    "https://docs.github.com/en/copilot/tutorials/optimize-ai-usage",
    "https://docs.github.com/en/copilot/concepts/agents/copilot-cli/context-management",
    "https://github.com/earendil-works/pi/blob/main/packages/coding-agent/README.md",
    "https://github.com/earendil-works/pi/blob/main/packages/coding-agent/docs/models.md",
    "https://github.com/earendil-works/pi/blob/main/packages/coding-agent/docs/compaction.md",
]


ASSUMPTIONS = [
    {"assumptionId": "a1-structural-calibration", "statement": "All behavioral coefficients are explicit structural assumptions, not measurements of product superiority.", "sourceType": "assumed"},
    {"assumptionId": "a2-price-snapshot", "statement": "Token prices and GitHub plan economics are frozen to the public 2026-09-04 snapshot.", "sourceType": "literature"},
    {"assumptionId": "a3-common-random-tasks", "statement": "Each coupling ID preserves the same latent task, provider load, tool failures, and verifier shocks across scenarios.", "sourceType": "assumed"},
    {"assumptionId": "a4-fixed-verifier", "statement": "Compared scenarios face the same external verifier at each design point.", "sourceType": "assumed"},
    {"assumptionId": "a5-cache-accounting", "statement": "Uncached input, cache reads, cache writes, and output form separate token ledgers.", "sourceType": "assumed"},
    {"assumptionId": "a6-economic-boundary", "statement": "Provider-value, marginal-cash, allocated-cash, human-time, SLA, and failure costs remain distinct until economic loss is calculated.", "sourceType": "assumed"},
    {"assumptionId": "a7-excluded-effects", "statement": "Vendor ecosystem, governance, privacy, negotiation, and user-learning effects are outside the model boundary.", "sourceType": "assumed"},
]


def param(name: str, value: Any, source_type: str = "assumed") -> dict[str, Any]:
    unit = "category" if name in LABEL_PARAMETERS else UNITS[name]
    return {
        "name": name,
        "value": value,
        "unit": unit,
        "sourceType": source_type,
        "description": f"Declared {name.replace('_', ' ')} input for the simulation mechanism.",
    }


def design_parameters(
    workload: str,
    *,
    billing_period_tasks: int = 300,
    harness_name: str | None = None,
    overrides: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    values = dict(BASE_DESIGN)
    values.update(WORKLOAD_OVERRIDES[workload])
    values["billing_period_tasks"] = billing_period_tasks
    values.update(overrides or {})
    if set(values) != DESIGN_PARAMETERS:
        missing = sorted(DESIGN_PARAMETERS - set(values))
        extra = sorted(set(values) - DESIGN_PARAMETERS)
        raise ValueError(f"design parameter contract mismatch; missing={missing}, extra={extra}")
    parameters = [param(name, values[name]) for name in sorted(values)]
    if harness_name is not None:
        parameters.append(param("harness_name", harness_name))
    return parameters


def scenario_parameters(
    labels: dict[str, str],
    mechanics: dict[str, Any],
    *,
    include_harness: bool = True,
) -> list[dict[str, Any]]:
    expected_labels = LABEL_PARAMETERS if include_harness else LABEL_PARAMETERS - {"harness_name"}
    if set(labels) != expected_labels:
        raise ValueError(f"label contract mismatch; missing={sorted(expected_labels - set(labels))}, extra={sorted(set(labels) - expected_labels)}")
    values = dict(mechanics)
    values.update(MODEL_VALUES)
    if set(values) != SCENARIO_PARAMETERS | MODEL_PARAMETERS:
        expected = SCENARIO_PARAMETERS | MODEL_PARAMETERS
        raise ValueError(f"scenario parameter contract mismatch; missing={sorted(expected - set(values))}, extra={sorted(set(values) - expected)}")
    parameters = [param(name, labels[name]) for name in sorted(labels)]
    parameters.extend(param(name, values[name], "literature" if name in LITERATURE_SCENARIO_FIELDS else "assumed") for name in sorted(values))
    return parameters


def base_mechanics(**changes: Any) -> dict[str, Any]:
    values: dict[str, Any] = {
        "quality_offset_logit": 0.0,
        "latency_multiplier": 1.0,
        "tool_efficiency_multiplier": 1.0,
        "prompt_tokens": 4000,
        "orchestration_tokens_per_call": 400,
        "tool_exposure_fraction": 0.60,
        "tool_schema_tokens_per_tool": 170,
        "tool_output_cap_tokens": 8000,
        "model_output_cap_tokens": 12000,
        "tool_selection_accuracy": 0.92,
        "tool_confusion_penalty_logit": 0.28,
        "failed_tool_result_fraction": 0.60,
        "tool_result_retention_fraction": 0.72,
        "output_retention_fraction": 0.94,
        "cache_retention_seconds": 86400,
        "prefix_stability_probability": 0.90,
        "context_window_tokens": 400000,
        "long_context_threshold_tokens": 272000,
        "long_context_input_multiplier": 2.0,
        "long_context_output_multiplier": 1.5,
        "compaction_enabled": True,
        "compaction_trigger_fraction": 0.80,
        "compaction_reserve_tokens": 16384,
        "compaction_keep_tokens": 20000,
        "compaction_summary_fraction": 0.08,
        "compaction_information_loss": 0.07,
        "compaction_cache_reset_probability": 0.90,
        "context_overflow_quality_penalty_logit": 1.20,
        "max_retries": 2,
        "retry_delay_seconds": 3.0,
        "retry_backoff_multiplier": 2.0,
        "parallelism": 4,
        "parallel_overhead_seconds": 0.35,
        "parallel_conflict_probability": 0.03,
        "harness_latency_seconds_per_call": 0.60,
        "human_approval_seconds_per_tool_call": 0.20,
        "subscription_fee_usd_per_period": 39.0,
        "subscription_allowance_usd_per_period": 70.0,
        "overage_enabled": True,
        "overage_multiplier": 1.0,
        "automatic_discount_fraction": 0.0,
    }
    values.update(changes)
    return values


def labels(
    *,
    harness: str | None,
    route: str,
    tool: str,
    cache: str,
    compaction: str,
    billing: str,
    policy: str,
    plan: str,
    execute: str,
    verify: str,
    compact: str,
) -> dict[str, str]:
    result = {
        "provider_route": route,
        "tool_policy": tool,
        "cache_policy": cache,
        "compaction_policy": compaction,
        "billing_mode": billing,
        "model_policy": policy,
        "phase_plan_model": plan,
        "phase_execute_model": execute,
        "phase_verify_model": verify,
        "phase_compact_model": compact,
    }
    if harness is not None:
        result["harness_name"] = harness
    return result


def scenario(scenario_id: str, label: str, description: str, tags: list[str], label_values: dict[str, str], mechanics: dict[str, Any], *, include_harness: bool = True) -> dict[str, Any]:
    return {"scenarioId": scenario_id, "label": label, "description": description, "tags": tags, "parameters": scenario_parameters(label_values, mechanics, include_harness=include_harness)}


def point(point_id: str, description: str, workload: str, *, billing_period_tasks: int = 300, harness_name: str | None = None, overrides: dict[str, Any] | None = None) -> dict[str, Any]:
    return {"designPointId": point_id, "description": description, "parameters": design_parameters(workload, billing_period_tasks=billing_period_tasks, harness_name=harness_name, overrides=overrides)}


def contrast(hypothesis_id: str, claim: str, outcome: str, baseline: str, comparison: str, primary: list[str], challenge: list[str], threshold: float, unit: str, operator: str, falsification: str) -> dict[str, Any]:
    assumption_ids = ["a1-structural-calibration", "a2-price-snapshot", "a3-common-random-tasks", "a4-fixed-verifier", "a5-cache-accounting", "a6-economic-boundary"]
    return {
        "hypothesisId": hypothesis_id,
        "claim": claim,
        "claimScope": "model-internal",
        "assumptionIds": assumption_ids,
        "externalValidationRequired": True,
        "outcome": outcome,
        "scenarioIds": [baseline, comparison],
        "estimand": f"Paired mean difference in {outcome} ({comparison} minus {baseline}).",
        "analysis": {"kind": "scenario-contrast", "estimator": "mean-difference", "baselineScenarioId": baseline, "comparisonScenarioId": comparison, "primaryDesignPointIds": primary, "challengeDesignPointIds": challenge, "pairing": "paired", "intervalMethod": "normal-approximation", "intervalLevel": 0.95, "aggregationRule": "all-design-points"},
        "practicalThreshold": {"value": threshold, "unit": unit, "operator": operator},
        "decisionRule": "Support under the model only when every declared 95% paired interval clears the practical threshold; challenge when an interval lies wholly on the failing side; otherwise report inconclusive.",
        "falsificationRule": falsification,
    }


def not_identifiable(hypothesis_id: str, claim: str, outcome: str, scenario_ids: list[str], reason: str) -> dict[str, Any]:
    return {
        "hypothesisId": hypothesis_id,
        "claim": claim,
        "claimScope": "conditional-real-world",
        "assumptionIds": [item["assumptionId"] for item in ASSUMPTIONS],
        "externalValidationRequired": True,
        "outcome": outcome,
        "scenarioIds": scenario_ids,
        "estimand": "Real-world difference in verified work per total economic cost across the named products.",
        "analysis": {"kind": "not-identifiable", "reason": reason},
        "practicalThreshold": {"value": 0.0, "unit": OUTCOME_UNITS[outcome], "operator": "ge"},
        "decisionRule": "Do not rank products in reality from synthetic outcomes; require matched tasks, fixed verifiers, telemetry, and observed human costs.",
        "falsificationRule": "A preregistered matched-task field trial whose interval reverses a modeled ordering falsifies any attempted real-world extrapolation.",
    }


def base_experiment(experiment_id: str, title: str, description: str) -> dict[str, Any]:
    return {
        "schemaVersion": 1,
        "experimentId": experiment_id,
        "title": title,
        "description": description,
        "phase": "robustness",
        "paradigm": "monte-carlo",
        "engine": {"name": "python-standard-library", "versionConstraint": ">=3.11"},
        "rootSeed": ROOT_SEED,
        "uncertaintyMode": "stochastic",
        "seedPolicy": "paired-across-scenarios",
        "replications": REPLICATIONS,
    }


def controlled_harness() -> dict[str, Any]:
    spec = base_experiment("controlled-harness", "Controlled harness and provider-route comparison", "Separates harness mechanics from provider settlement while holding latent tasks, model, verifier, and random shocks fixed.")
    fixed_terra = dict(policy="fixed_terra", plan="terra", execute="terra", verify="terra", compact="terra")
    copilot_mechanics = base_mechanics(quality_offset_logit=0.02, prompt_tokens=5200, orchestration_tokens_per_call=520, tool_exposure_fraction=0.25, tool_output_cap_tokens=5000, tool_selection_accuracy=0.94, tool_confusion_penalty_logit=0.30, tool_result_retention_fraction=0.68, compaction_information_loss=0.055, parallelism=4, parallel_conflict_probability=0.025, harness_latency_seconds_per_call=0.75)
    pi_mechanics = base_mechanics(prompt_tokens=3500, orchestration_tokens_per_call=300, tool_exposure_fraction=0.175, tool_output_cap_tokens=12500, tool_selection_accuracy=0.91, tool_confusion_penalty_logit=0.22, tool_result_retention_fraction=0.78, compaction_information_loss=0.09, parallelism=6, parallel_conflict_probability=0.04, harness_latency_seconds_per_call=0.50)
    direct_mechanics = dict(pi_mechanics, subscription_fee_usd_per_period=0.0, subscription_allowance_usd_per_period=0.0)
    spec["scenarios"] = [
        scenario("copilot-cli-copilot-route", "Copilot CLI through GitHub Copilot", "Copilot CLI, fixed Terra, GitHub route, and Pro+ accounting.", ["baseline", "copilot-cli", "github-copilot"], labels(harness="copilot-cli", route="github-copilot", tool="task-scoped", cache="stable-prefix", compaction="threshold-summary", billing="subscription", **fixed_terra), copilot_mechanics),
        scenario("pi-cli-copilot-route", "Pi CLI through GitHub Copilot", "Pi, the same fixed Terra model, GitHub route, and Pro+ accounting.", ["comparison", "pi-cli", "github-copilot"], labels(harness="pi-cli", route="github-copilot", tool="task-scoped", cache="stable-prefix", compaction="threshold-summary", billing="subscription", **fixed_terra), pi_mechanics),
        scenario("pi-cli-openai-api", "Pi CLI through OpenAI API", "The same Pi and Terra mechanics settled directly at token rates.", ["comparison", "pi-cli", "openai-api"], labels(harness="pi-cli", route="openai-api", tool="task-scoped", cache="stable-prefix", compaction="threshold-summary", billing="direct", **fixed_terra), direct_mechanics),
    ]
    primary = [f"central-{name}" for name in WORKLOAD_OVERRIDES]
    spec["designPoints"] = [point(f"central-{name}", f"Central assumptions for the {name} workload.", name) for name in WORKLOAD_OVERRIDES] + [
        point("challenge-copilot-favoring-diverse-tools", "A preregistered Copilot-favoring case: many relevant integrations emphasize its assumed tool-selection and context-preservation advantages.", "external-integration", overrides={"relevant_tool_count": 22, "registered_tool_count": 96, "required_tool_calls_mean": 46, "scenario_profile_effect_scale": 1.45}),
        point("challenge-pi-favoring-minimal-loop", "A preregistered Pi-favoring case: a small read-edit-test loop emphasizes its assumed lower fixed prompt and orchestration overhead.", "localized-bug", overrides={"registered_tool_count": 4, "required_tool_calls_mean": 5, "base_model_calls_mean": 3, "scenario_profile_effect_scale": 0.65}),
        point("challenge-cold-prefix-churn", "Low continuity and long gaps deny cache reads.", "repository-refactor", overrides={"session_continuity_probability": 0.08, "inter_call_gap_seconds_mean": 108000, "cache_cost_scale": 1.25}),
        point("challenge-hot-stable-prefix", "Near-continuous sessions maximize provider cache opportunity.", "test-debug", overrides={"session_continuity_probability": 0.98, "inter_call_gap_seconds_mean": 15, "cache_cost_scale": 0.80}),
        point("challenge-tool-registry-sprawl", "Five hundred registered tools, with few relevant choices, materially stress schema cost and confusion.", "external-integration", overrides={"registered_tool_count": 500, "relevant_tool_count": 5, "required_tool_calls_mean": 38, "scenario_profile_effect_scale": 1.70}),
        point("challenge-long-context-threshold", "Most calls cross the long-context billing threshold.", "long-session", overrides={"initial_context_tokens_mean": 300000, "context_growth_tokens_per_call": 15000, "scenario_profile_effect_scale": 1.35}),
        point("challenge-lossy-compaction", "Long context plus strict verification exposes compaction information loss.", "long-session", overrides={"initial_context_tokens_mean": 350000, "context_growth_tokens_per_call": 18000, "verification_strength": 0.98, "quality_acceptance_threshold": 0.86, "scenario_profile_effect_scale": 1.55}),
        point("challenge-unreliable-tools", "High tool failure stresses retries and human recovery.", "ci-browser", overrides={"tool_error_probability": 0.30, "provider_error_probability": 0.05, "failure_cost_usd": 180.0, "scenario_profile_effect_scale": 1.40}),
    ]
    challenge = [item["designPointId"] for item in spec["designPoints"] if item["designPointId"].startswith("challenge-")]
    scenario_ids = [item["scenarioId"] for item in spec["scenarios"]]
    spec["outcomes"] = [{"name": n, "unit": u, "description": d} for n, u, d in OUTCOMES]
    spec["assumptions"] = [dict(item) for item in ASSUMPTIONS]
    spec["hypotheses"] = [
        not_identifiable("h-real-world-best-harness", "One named harness is categorically most efficient in real production use.", "normalized_cost_per_verified_work", scenario_ids, "No observed matched-task executions, user learning, ecosystem effects, or organization-specific constraints are present."),
        contrast("h-pi-copilot-normalized-cost", "Pi through GitHub lowers normalized cost per verified work by at least 0.10 relative to Copilot CLI under the declared mechanisms.", "normalized_cost_per_verified_work", scenario_ids[0], scenario_ids[1], primary, challenge, -0.10, "1", "le", "Diverse-tool, long-context, and unreliable-tool challenges test whether selection, preservation, or retry mechanics reverse the advantage."),
        contrast("h-pi-copilot-quality-noninferior", "Pi through GitHub is quality-noninferior to Copilot CLI within 0.02 under the declared mechanisms.", "external_quality_score", scenario_ids[0], scenario_ids[1], primary, challenge, -0.02, "1", "ge", "Compaction and tool-sprawl challenges falsify the claim if their upper interval endpoint is below -0.02."),
        contrast("h-provider-route-ledger-equivalence", "With Pi and Terra fixed, direct OpenAI routing does not increase normalized provider-ledger cost by more than 0.02.", "normalized_provider_cost", scenario_ids[1], scenario_ids[2], primary, challenge, 0.02, "1", "le", "A route-specific cache or long-context difference above 0.02 would challenge equivalence."),
        contrast("h-provider-route-marginal-cash", "Before allowance exhaustion, direct API settlement has nonnegative marginal cash cost relative to GitHub subscription settlement.", "marginal_cash_cost_usd_per_task", scenario_ids[1], scenario_ids[2], primary, challenge, 0.0, "USD/task", "ge", "Expensive long-context portfolios test whether both routes enter overage and erase the marginal difference."),
    ]
    spec["extensions"] = extension("Task prompt through fixed verification or budget termination, including model, cache, tools, retries, compaction, human time, and failure loss.")
    return spec


def monthly_economics() -> dict[str, Any]:
    spec = base_experiment("monthly-economics", "Monthly allowance and direct-API economics", "Compares 30-day homogeneous task portfolios with separate token-value, marginal-cash, allocated-cash, and economic-loss ledgers.")
    auto = dict(policy="phase_routing", plan="luna", execute="terra", verify="sol", compact="luna")
    shared = base_mechanics(prompt_tokens=3500, orchestration_tokens_per_call=320, tool_exposure_fraction=0.175, tool_output_cap_tokens=9000, tool_selection_accuracy=0.92, parallelism=5, harness_latency_seconds_per_call=0.58, automatic_discount_fraction=0.10)
    copilot = dict(shared, prompt_tokens=5200, orchestration_tokens_per_call=520, tool_exposure_fraction=0.25, tool_selection_accuracy=0.94, compaction_information_loss=0.055, harness_latency_seconds_per_call=0.75)
    direct = dict(shared, subscription_fee_usd_per_period=0.0, subscription_allowance_usd_per_period=0.0, automatic_discount_fraction=0.0)
    spec["scenarios"] = [
        scenario("copilot-proplus-auto", "Copilot CLI Pro+ with auto selection", "Copilot CLI with Pro+ fee, allowance, overage, and 10 percent auto-model discount.", ["baseline", "copilot-cli", "subscription"], labels(harness="copilot-cli", route="github-copilot", tool="task-scoped", cache="stable-prefix", compaction="threshold-summary", billing="subscription", **auto), copilot),
        scenario("pi-copilot-proplus-auto", "Pi through Copilot Pro+ with auto selection", "Pi through GitHub Copilot with identical plan accounting and phase routing.", ["comparison", "pi-cli", "subscription"], labels(harness="pi-cli", route="github-copilot", tool="task-scoped", cache="stable-prefix", compaction="threshold-summary", billing="subscription", **auto), shared),
        scenario("pi-openai-api-auto", "Pi through direct OpenAI API routing", "Pi with the same phase policy and direct token settlement without a subscription allowance.", ["comparison", "pi-cli", "direct-api"], labels(harness="pi-cli", route="openai-api", tool="task-scoped", cache="stable-prefix", compaction="threshold-summary", billing="direct", **auto), direct),
    ]
    definitions = [
        ("low-localized-hot", "localized-bug", 30, {"session_continuity_probability": 0.98, "inter_call_gap_seconds_mean": 20}),
        ("low-feature-cold", "multi-file-feature", 24, {"session_continuity_probability": 0.10, "inter_call_gap_seconds_mean": 108000}),
        ("low-long-hot", "long-session", 16, {"session_continuity_probability": 0.94, "inter_call_gap_seconds_mean": 45}),
        ("medium-localized-hot", "localized-bug", 320, {"session_continuity_probability": 0.98, "inter_call_gap_seconds_mean": 20}),
        ("medium-feature-mixed", "multi-file-feature", 240, {"session_continuity_probability": 0.62, "inter_call_gap_seconds_mean": 900}),
        ("medium-integration-cold", "external-integration", 180, {"session_continuity_probability": 0.12, "inter_call_gap_seconds_mean": 100000}),
        ("medium-long-hot", "long-session", 120, {"session_continuity_probability": 0.94, "inter_call_gap_seconds_mean": 45}),
        ("high-localized-hot", "localized-bug", 3200, {"session_continuity_probability": 0.99, "inter_call_gap_seconds_mean": 10}),
        ("high-feature-mixed", "multi-file-feature", 1400, {"session_continuity_probability": 0.68, "inter_call_gap_seconds_mean": 600}),
        ("high-integration-cold", "external-integration", 950, {"session_continuity_probability": 0.10, "inter_call_gap_seconds_mean": 108000}),
        ("high-long-hot", "long-session", 720, {"session_continuity_probability": 0.96, "inter_call_gap_seconds_mean": 25}),
        ("high-browser-low-reuse", "ci-browser", 1000, {"session_continuity_probability": 0.25, "inter_call_gap_seconds_mean": 7200}),
    ]
    spec["designPoints"] = [point(point_id, f"Thirty-day homogeneous {workload} portfolio with {volume} tasks and declared cache continuity.", workload, billing_period_tasks=volume, overrides=overrides) for point_id, workload, volume, overrides in definitions]
    all_ids = [item[0] for item in definitions]
    low = [item for item in all_ids if item.startswith("low-")]
    medium = [item for item in all_ids if item.startswith("medium-")]
    high = [item for item in all_ids if item.startswith("high-")]
    scenario_ids = [item["scenarioId"] for item in spec["scenarios"]]
    spec["outcomes"] = [{"name": n, "unit": u, "description": d} for n, u, d in OUTCOMES]
    spec["assumptions"] = [dict(item) for item in ASSUMPTIONS]
    spec["hypotheses"] = [
        not_identifiable("h-real-monthly-value", "One billing route is universally cheaper for real organizations.", "economic_loss_usd_per_task", scenario_ids, "Organization-specific volume, negotiated rates, quality, opportunity cost, and observed human intervention are absent."),
        contrast("h-low-volume-direct-allocated-cash", "At low volume, direct API settlement reduces allocated cash per task by at least one cent relative to Pi on Pro+.", "allocated_cash_cost_usd_per_task", scenario_ids[1], scenario_ids[2], low, medium + high, -0.01, "USD/task", "le", "Medium and high portfolios test where allowance amortization reverses the low-volume result."),
        contrast("h-high-volume-subscription-marginal-cash", "At high volume, Pro+ allowance and overage settlement reduces marginal cash by at least one cent per task relative to direct API.", "marginal_cash_cost_usd_per_task", scenario_ids[2], scenario_ids[1], high, low + medium, -0.01, "USD/task", "le", "Low-volume and cold-cache portfolios test whether the claimed high-volume difference disappears."),
        contrast("h-monthly-pi-harness-cost", "With plan and phase routing fixed, Pi reduces normalized cost per verified work by at least 0.05 relative to Copilot CLI.", "normalized_cost_per_verified_work", scenario_ids[0], scenario_ids[1], medium, low + high, -0.05, "1", "le", "Cold-cache and long-context portfolios challenge whether fixed-overhead savings survive quality and retries."),
        contrast("h-direct-cash-without-auto-discount", "Without the GitHub auto-model discount or allowance, direct API marginal cash cost is nonnegative relative to the same Pi workload through Copilot.", "marginal_cash_cost_usd_per_task", scenario_ids[1], scenario_ids[2], low + medium, high, 0.0, "USD/task", "ge", "High-volume overage and cache-heavy extremes test whether cash settlement can reverse the explicit discount and allowance advantage."),
    ]
    spec["extensions"] = extension("Thirty-day homogeneous task portfolio including token value, subscription fee, included allowance, overage, verification, human recovery, SLA, and failure loss.", {"subscriptionAccounting": {"plan": "Copilot Pro+", "monthlyFeeUsd": 39.0, "includedAiCredits": 7000, "includedValueUsd": 70.0, "creditUsd": 0.01, "automaticDiscountFraction": 0.10}})
    return spec


def usage_policy() -> dict[str, Any]:
    spec = base_experiment("usage-policy", "Resource-aware usage and phase routing", "Tests selective tools, stable prefixes, bounded outputs, deliberate compaction, and phase-aware model routing across Copilot CLI and Pi strata.")
    no_harness = False
    unaware_labels = labels(harness=None, route="openai-api", tool="eager-all", cache="incidental", compaction="reactive", billing="direct", policy="fixed_sol", plan="sol", execute="sol", verify="sol", compact="sol")
    aware_labels = labels(harness=None, route="openai-api", tool="required-plus-neighbors", cache="stable-prefix", compaction="proactive", billing="direct", policy="fixed_terra", plan="terra", execute="terra", verify="terra", compact="terra")
    routed_labels = labels(harness=None, route="openai-api", tool="required-plus-neighbors", cache="stable-prefix", compaction="proactive", billing="direct", policy="phase_routing", plan="luna", execute="terra", verify="sol", compact="luna")
    direct = {"subscription_fee_usd_per_period": 0.0, "subscription_allowance_usd_per_period": 0.0}
    spec["scenarios"] = [
        scenario("resource-unaware-frontier", "Resource-unaware frontier", "Eager tool exposure, incidental caching, reactive compaction, and Sol for every phase.", ["baseline", "resource-unaware"], unaware_labels, base_mechanics(quality_offset_logit=0.02, prompt_tokens=4500, orchestration_tokens_per_call=600, tool_exposure_fraction=1.0, tool_output_cap_tokens=20000, tool_selection_accuracy=0.84, tool_confusion_penalty_logit=0.015, tool_result_retention_fraction=0.90, prefix_stability_probability=0.55, compaction_trigger_fraction=0.94, compaction_summary_fraction=0.13, compaction_information_loss=0.14, parallelism=8, parallel_overhead_seconds=0.75, parallel_conflict_probability=0.09, harness_latency_seconds_per_call=0.82, **direct), include_harness=no_harness),
        scenario("resource-aware-frontier", "Resource-aware frontier", "Task-scoped tools, stable prefixes, bounded results, proactive compaction, and fixed Terra.", ["comparison", "resource-aware"], aware_labels, base_mechanics(prompt_tokens=3000, orchestration_tokens_per_call=260, tool_exposure_fraction=0.14, tool_output_cap_tokens=5000, tool_selection_accuracy=0.95, tool_confusion_penalty_logit=0.01, tool_result_retention_fraction=0.62, prefix_stability_probability=0.95, compaction_trigger_fraction=0.76, compaction_summary_fraction=0.055, compaction_information_loss=0.045, parallelism=4, parallel_overhead_seconds=0.28, parallel_conflict_probability=0.025, harness_latency_seconds_per_call=0.52, **direct), include_harness=no_harness),
        scenario("resource-aware-phase-routing", "Resource-aware phase routing", "The resource-aware controls with Luna planning, Terra execution, and Sol verification.", ["comparison", "resource-aware", "phase-routing"], routed_labels, base_mechanics(prompt_tokens=3000, orchestration_tokens_per_call=260, tool_exposure_fraction=0.14, tool_output_cap_tokens=5000, tool_selection_accuracy=0.95, tool_confusion_penalty_logit=0.01, tool_result_retention_fraction=0.62, prefix_stability_probability=0.95, compaction_trigger_fraction=0.76, compaction_summary_fraction=0.055, compaction_information_loss=0.045, parallelism=4, parallel_overhead_seconds=0.28, parallel_conflict_probability=0.025, harness_latency_seconds_per_call=0.52, **direct), include_harness=no_harness),
    ]
    points: list[dict[str, Any]] = []
    for harness, scale in (("copilot-cli", 1.05), ("pi-cli", 0.95)):
        for workload in WORKLOAD_OVERRIDES:
            points.append(point(f"primary-{harness}-{workload}", f"Central {workload} workload in the {harness} stratum.", workload, harness_name=harness, overrides={"scenario_profile_effect_scale": scale}))
        stressors = [
            ("hot-cache", "test-debug", {"session_continuity_probability": 0.99, "inter_call_gap_seconds_mean": 10, "cache_cost_scale": 0.75, "scenario_profile_effect_scale": 0.90 * scale}),
            ("cold-cache", "repository-refactor", {"session_continuity_probability": 0.05, "inter_call_gap_seconds_mean": 129600, "cache_cost_scale": 1.20, "scenario_profile_effect_scale": 1.15 * scale}),
            ("cache-churn", "multi-file-feature", {"session_continuity_probability": 0.18, "inter_call_gap_seconds_mean": 45, "cache_cost_scale": 1.40, "scenario_profile_effect_scale": 1.30 * scale}),
            ("tool-sprawl", "external-integration", {"registered_tool_count": 500, "relevant_tool_count": 5, "required_tool_calls_mean": 44, "scenario_profile_effect_scale": 1.70 * scale}),
            ("lossy-long-session", "long-session", {"initial_context_tokens_mean": 340000, "context_growth_tokens_per_call": 18000, "verification_strength": 0.98, "quality_acceptance_threshold": 0.86, "scenario_profile_effect_scale": 1.50 * scale}),
            ("unreliable-tools", "ci-browser", {"tool_error_probability": 0.32, "provider_error_probability": 0.06, "failure_cost_usd": 190.0, "scenario_profile_effect_scale": 1.45 * scale}),
        ]
        for suffix, workload, overrides in stressors:
            points.append(point(f"challenge-{harness}-{suffix}", f"{suffix.replace('-', ' ')} stress case in the {harness} stratum.", workload, harness_name=harness, overrides=overrides))
    spec["designPoints"] = points
    primary = [item["designPointId"] for item in points if item["designPointId"].startswith("primary-")]
    challenge = [item["designPointId"] for item in points if item["designPointId"].startswith("challenge-")]
    scenario_ids = [item["scenarioId"] for item in spec["scenarios"]]
    spec["outcomes"] = [{"name": n, "unit": u, "description": d} for n, u, d in OUTCOMES]
    spec["assumptions"] = [dict(item) for item in ASSUMPTIONS]
    spec["hypotheses"] = [
        contrast("h-aware-cost-reduction", "Resource-aware fixed-Terra usage reduces normalized cost per verified work by at least 10 percent.", "normalized_cost_per_verified_work", scenario_ids[0], scenario_ids[1], primary, challenge, -0.10, "1", "le", "Cold cache, tool failure, and long context test whether control overhead or reduced capability reverses the reduction."),
        contrast("h-aware-quality-noninferior", "Resource-aware fixed-Terra usage is quality-noninferior within 0.02 to resource-unaware fixed-Sol usage.", "external_quality_score", scenario_ids[0], scenario_ids[1], primary, challenge, -0.02, "1", "ge", "High-complexity and strict-verification points test whether Terra stays inside the quality margin."),
        contrast("h-aware-latency-reduction", "Resource-aware fixed-Terra usage reduces normalized wall time by at least 10 percent.", "normalized_wall_time", scenario_ids[0], scenario_ids[1], primary, challenge, -0.10, "1", "le", "Highly parallel tool work tests whether the broad eager policy is faster despite overhead."),
        contrast("h-phase-routing-cost", "Phase-aware routing reduces normalized cost per verified work by at least 5 percent relative to resource-aware fixed Terra.", "normalized_cost_per_verified_work", scenario_ids[1], scenario_ids[2], primary, challenge, -0.05, "1", "le", "Verification-heavy long-context work tests whether Sol verification erases Luna planning savings."),
        contrast("h-phase-routing-quality", "Phase-aware routing is quality-noninferior within 0.01 relative to resource-aware fixed Terra.", "external_quality_score", scenario_ids[1], scenario_ids[2], primary, challenge, -0.01, "1", "ge", "Exploration-heavy tasks test whether cheaper planning loses information that later verification cannot recover."),
    ]
    spec["extensions"] = extension("Task start through fixed verification, including schemas, results, cache, tools, retries, compaction, routing, latency, human review, and failure loss.", {"policyContrast": "Policies are crossed with Copilot CLI and Pi CLI design-point strata; labels have no hidden effect."})
    return spec


def extension(system_boundary: str, extra: dict[str, Any] | None = None) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "studyFamily": "harness-efficiency-20260904",
        "commonRandomNumbers": True,
        "systemBoundary": system_boundary,
        "sourceSnapshotDate": "2026-09-04",
        "sourceUrls": SOURCE_URLS,
    }
    payload.update(extra or {})
    return {"simulation-data-lab": payload}


def validate_generated(study_id: str, spec: dict[str, Any]) -> None:
    outcome_names = [item["name"] for item in spec["outcomes"]]
    if outcome_names != [item[0] for item in OUTCOMES]:
        raise ValueError(f"{study_id}: outcome contract drift")
    if not 150 <= spec["replications"] <= 250:
        raise ValueError(f"{study_id}: replications outside frozen range")
    scenario_ids = [item["scenarioId"] for item in spec["scenarios"]]
    design_ids = [item["designPointId"] for item in spec["designPoints"]]
    if len(scenario_ids) != len(set(scenario_ids)) or len(design_ids) != len(set(design_ids)):
        raise ValueError(f"{study_id}: duplicate scenario or design-point ID")
    run_count = len(scenario_ids) * len(design_ids) * spec["replications"]
    # Conservative current-model budget: plan + run + outcomes + seven diagnostics
    # per run, plus one summary row per scenario/design/outcome cell.
    estimated_rows = run_count * (2 + len(OUTCOMES) + 7) + len(scenario_ids) * len(design_ids) * len(OUTCOMES)
    if estimated_rows >= 1_000_000:
        raise ValueError(f"{study_id}: conservative materialized-row estimate is {estimated_rows:,}")
    for scenario_item in spec["scenarios"]:
        scenario_names = {item["name"] for item in scenario_item["parameters"]}
        for design_item in spec["designPoints"]:
            design_names = {item["name"] for item in design_item["parameters"]}
            overlap = scenario_names & design_names
            merged = scenario_names | design_names
            if overlap or merged != REQUIRED_PARAMETERS:
                raise ValueError(f"{study_id}/{scenario_item['scenarioId']}/{design_item['designPointId']}: overlap={sorted(overlap)}, missing={sorted(REQUIRED_PARAMETERS - merged)}, extra={sorted(merged - REQUIRED_PARAMETERS)}")


def build_all() -> dict[str, dict[str, Any]]:
    studies = {"controlled-harness": controlled_harness(), "monthly-economics": monthly_economics(), "usage-policy": usage_policy()}
    for study_id, spec in studies.items():
        validate_generated(study_id, spec)
    return studies


def rendered(spec: dict[str, Any]) -> str:
    return json.dumps(spec, indent=2, ensure_ascii=False) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-root", type=Path, default=Path(__file__).resolve().parents[1] / "studies", help="Directory with one generated subdirectory per study.")
    parser.add_argument("--check", action="store_true", help="Fail if generated experiment files are missing or stale.")
    args = parser.parse_args()
    studies = build_all()
    differences: list[str] = []
    for study_id, spec in studies.items():
        target = args.output_root / study_id / "experiment.json"
        expected = rendered(spec)
        if args.check:
            if not target.exists():
                differences.append(f"missing: {target}")
            elif target.read_text(encoding="utf-8") != expected:
                differences.append(f"out of date: {target}")
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(expected, encoding="utf-8", newline="\n")
            print(f"wrote {target}")
    if differences:
        print("\n".join(differences), file=sys.stderr)
        return 1
    if args.check:
        print(f"ok: {len(studies)} experiment files match generator")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
