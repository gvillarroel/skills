"""Paired Monte Carlo model for tool-using coding-harness efficiency.

The runner supplies one merged ``run["parameters"]`` mapping containing both
scenario and design-point parameters.  This module deliberately has no
brand-specific performance branches: ``harness_name`` and ``provider_route``
are provenance labels only.  A harness changes results only through explicit
mechanism parameters such as prompt size, visible tools, selection accuracy,
cache behavior, retry policy, parallelism, latency, billing, and model policy.

``REQUIRED_PARAMETERS`` is the canonical parameter contract.  Every listed
parameter is mandatory even when a mechanism is disabled, so a zero or false
value remains an explicit experimental assumption rather than a hidden model
default.  Extra parameters are tolerated for experiment annotations but never
silently substituted for a required input.

Common random numbers are implemented with named SHA-256 substreams derived
only from ``run["seed"]``.  Neither scenario IDs nor harness/provider labels
enter a seed.  Consequently, paired scenarios share latent task difficulty and
the same potential random draws even when their policies take different paths.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import math
import platform
import random
from typing import Any, Iterable


MODEL_METADATA = {
    "modelId": "coding-harness-efficiency-portfolio",
    "modelVersion": "1.0.0",
    "engine": "python-standard-library",
    "engineVersion": platform.python_version(),
    "rng": "random.Random-MT19937-with-SHA256-named-substreams",
    "rngVersion": platform.python_version(),
    "reproducibility": "exact-within-locked-environment",
}


MODEL_NAMES = ("luna", "terra", "sol")

OUTCOME_NAMES = (
    "accepted_task_fraction",
    "external_quality_score",
    "policy_violation_fraction",
    "provider_cost_usd_per_task",
    "marginal_cash_cost_usd_per_task",
    "allocated_cash_cost_usd_per_task",
    "economic_loss_usd_per_task",
    "normalized_provider_cost",
    "normalized_cost_per_verified_work",
    "wall_seconds_per_task",
    "normalized_wall_time",
    "human_minutes_per_task",
    "uncached_input_tokens_per_task",
    "cache_read_tokens_per_task",
    "cache_write_tokens_per_task",
    "output_tokens_per_task",
    "tool_schema_tokens_per_task",
    "tool_result_tokens_per_task",
    "model_calls_per_task",
    "tool_calls_per_task",
    "retries_per_task",
    "compactions_per_task",
    "cache_hit_fraction",
    "budget_exhausted_fraction",
)


_LABEL_PARAMETERS = (
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
)

_BASE_NUMERIC_PARAMETERS = (
    "tasks_per_run",
    "task_complexity_mean",
    "task_complexity_sd",
    "initial_context_tokens_mean",
    "initial_context_tokens_sd",
    "required_tool_calls_mean",
    "required_tool_calls_sd",
    "relevant_tool_count",
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
    "quality_offset_logit",
    "latency_multiplier",
    "tool_efficiency_multiplier",
    "prompt_tokens",
    "orchestration_tokens_per_call",
    "registered_tool_count",
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
    "billing_period_tasks",
    "overage_multiplier",
    "automatic_discount_fraction",
)

_BOOLEAN_PARAMETERS = ("compaction_enabled", "overage_enabled")

_MODEL_NUMERIC_PARAMETERS = tuple(
    f"{model}_{suffix}"
    for model in MODEL_NAMES
    for suffix in (
        "quality_logit",
        "latency_multiplier",
        "input_usd_per_million_tokens",
        "cache_read_usd_per_million_tokens",
        "cache_write_usd_per_million_tokens",
        "output_usd_per_million_tokens",
    )
)

REQUIRED_PARAMETERS = (
    *_LABEL_PARAMETERS,
    *_BASE_NUMERIC_PARAMETERS,
    *_BOOLEAN_PARAMETERS,
    *_MODEL_NUMERIC_PARAMETERS,
)


_PROBABILITY_PARAMETERS = {
    "tool_error_probability",
    "provider_error_probability",
    "session_continuity_probability",
    "parallelizable_fraction",
    "verification_strength",
    "quality_acceptance_threshold",
    "human_review_probability",
    "policy_violation_base_probability",
    "normalization_acceptance_floor",
    "failed_request_billable_fraction",
    "tool_exposure_fraction",
    "tool_selection_accuracy",
    "failed_tool_result_fraction",
    "tool_result_retention_fraction",
    "output_retention_fraction",
    "prefix_stability_probability",
    "compaction_trigger_fraction",
    "compaction_summary_fraction",
    "compaction_cache_reset_probability",
    "parallel_conflict_probability",
    "automatic_discount_fraction",
}

_INTEGER_PARAMETERS = {
    "tasks_per_run",
    "relevant_tool_count",
    "registered_tool_count",
    "max_retries",
    "parallelism",
    "billing_period_tasks",
}

_STRICTLY_POSITIVE_PARAMETERS = {
    "tasks_per_run",
    "sla_seconds_per_task",
    "verified_task_value_usd",
    "provider_cost_reference_usd_per_task",
    "normalization_acceptance_floor",
    "context_window_tokens",
    "long_context_threshold_tokens",
    "long_context_input_multiplier",
    "long_context_output_multiplier",
    "retry_backoff_multiplier",
    "parallelism",
    "billing_period_tasks",
    "overage_multiplier",
    "latency_multiplier",
    "tool_efficiency_multiplier",
    "provider_latency_scale",
}


@dataclass(frozen=True)
class _CallRecord:
    """A billable provider-ledger entry used for independent reconciliation."""

    model: str
    uncached_input_tokens: float
    cache_read_tokens: float
    cache_write_tokens: float
    output_tokens: float
    prompt_tokens: float
    schema_tokens: float
    long_context: bool


def _named_seed(run_seed: int, stream: str) -> int:
    material = f"harness-efficiency/substream/v1\0{run_seed}\0{stream}".encode("utf-8")
    return int.from_bytes(hashlib.sha256(material).digest()[:8], "big")


def _rng(run_seed: int, stream: str) -> random.Random:
    return random.Random(_named_seed(run_seed, stream))


def _uniform(run_seed: int, stream: str) -> float:
    return _rng(run_seed, stream).random()


def _bernoulli(run_seed: int, stream: str, probability: float) -> bool:
    return _uniform(run_seed, stream) < probability


def _normal(run_seed: int, stream: str, mean: float, standard_deviation: float) -> float:
    if standard_deviation == 0.0:
        return mean
    return _rng(run_seed, stream).gauss(mean, standard_deviation)


def _nonnegative_normal(
    run_seed: int, stream: str, mean: float, standard_deviation: float
) -> float:
    return max(0.0, _normal(run_seed, stream, mean, standard_deviation))


def _stochastic_count(run_seed: int, stream: str, value: float, minimum: int = 0) -> int:
    bounded = max(float(minimum), value)
    lower = math.floor(bounded)
    fractional = bounded - lower
    return int(lower + (_uniform(run_seed, f"{stream}/round") < fractional))


def _clamp(value: float, lower: float, upper: float) -> float:
    return min(upper, max(lower, value))


def _logistic(value: float) -> float:
    if value >= 0.0:
        decay = math.exp(-value)
        return 1.0 / (1.0 + decay)
    growth = math.exp(value)
    return growth / (1.0 + growth)


def _probability_logit(probability: float) -> float:
    numerical_probability = _clamp(probability, 1e-12, 1.0 - 1e-12)
    return math.log(numerical_probability / (1.0 - numerical_probability))


def _number(parameters: dict[str, Any], name: str) -> float:
    value = parameters[name]
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"parameter {name!r} must be numeric")
    result = float(value)
    if not math.isfinite(result):
        raise ValueError(f"parameter {name!r} must be finite")
    return result


def _validated_parameters(raw_parameters: Any) -> dict[str, Any]:
    if not isinstance(raw_parameters, dict):
        raise ValueError("run['parameters'] must be a mapping")
    missing = sorted(set(REQUIRED_PARAMETERS) - set(raw_parameters))
    if missing:
        raise ValueError("missing required parameters: " + ", ".join(missing))

    parameters = dict(raw_parameters)
    for name in _LABEL_PARAMETERS:
        if not isinstance(parameters[name], str) or not parameters[name].strip():
            raise ValueError(f"parameter {name!r} must be a non-empty string")
    for name in _BOOLEAN_PARAMETERS:
        if not isinstance(parameters[name], bool):
            raise ValueError(f"parameter {name!r} must be boolean")
    for name in (*_BASE_NUMERIC_PARAMETERS, *_MODEL_NUMERIC_PARAMETERS):
        parameters[name] = _number(parameters, name)

    for name in _INTEGER_PARAMETERS:
        if not parameters[name].is_integer():
            raise ValueError(f"parameter {name!r} must be an integer")
        parameters[name] = int(parameters[name])
    for name in _PROBABILITY_PARAMETERS:
        if not 0.0 <= parameters[name] <= 1.0:
            raise ValueError(f"parameter {name!r} must be in [0, 1]")
    for name in _STRICTLY_POSITIVE_PARAMETERS:
        if parameters[name] <= 0.0:
            raise ValueError(f"parameter {name!r} must be greater than zero")

    signed_parameters = {
        "base_quality_logit",
        "quality_offset_logit",
        "difficulty_quality_penalty_logit",
        "tool_success_quality_weight_logit",
        "provider_failure_quality_penalty_logit",
        "retry_quality_penalty_logit",
        "policy_violation_tool_scale",
        "tool_confusion_penalty_logit",
        "compaction_information_loss",
        "context_overflow_quality_penalty_logit",
        "scenario_profile_effect_scale",
        *(f"{model}_quality_logit" for model in MODEL_NAMES),
    }
    for name in (*_BASE_NUMERIC_PARAMETERS, *_MODEL_NUMERIC_PARAMETERS):
        if name not in signed_parameters and parameters[name] < 0.0:
            raise ValueError(f"parameter {name!r} must be non-negative")

    if parameters["model_policy"] not in {
        "fixed_luna",
        "fixed_terra",
        "fixed_sol",
        "phase_routing",
    }:
        raise ValueError(
            "model_policy must be fixed_luna, fixed_terra, fixed_sol, or phase_routing"
        )
    for name in (
        "phase_plan_model",
        "phase_execute_model",
        "phase_verify_model",
        "phase_compact_model",
    ):
        if parameters[name] not in MODEL_NAMES:
            raise ValueError(f"parameter {name!r} must be luna, terra, or sol")
    if parameters["billing_mode"] not in {"direct", "subscription"}:
        raise ValueError("billing_mode must be direct or subscription")
    if parameters["compaction_reserve_tokens"] >= parameters["context_window_tokens"]:
        raise ValueError("compaction_reserve_tokens must be below context_window_tokens")

    exposed_tools = int(
        math.floor(
            parameters["registered_tool_count"] * parameters["tool_exposure_fraction"]
            + 0.5
        )
    )
    stable_prefix = (
        parameters["prompt_tokens"]
        + parameters["orchestration_tokens_per_call"]
        + exposed_tools * parameters["tool_schema_tokens_per_tool"]
    )
    if stable_prefix > parameters["context_window_tokens"]:
        raise ValueError("prompt plus exposed tool schemas exceeds the context window")

    profile_scale = parameters["scenario_profile_effect_scale"]
    effective_latency = 1.0 + profile_scale * (parameters["latency_multiplier"] - 1.0)
    effective_tool_efficiency = 1.0 + profile_scale * (
        parameters["tool_efficiency_multiplier"] - 1.0
    )
    if effective_latency <= 0.0 or effective_tool_efficiency <= 0.0:
        raise ValueError("scenario-profile scaling produced a non-positive multiplier")
    return parameters


def _model_for_phase(parameters: dict[str, Any], phase: str) -> str:
    policy = parameters["model_policy"]
    if policy.startswith("fixed_"):
        return policy.removeprefix("fixed_")
    return str(parameters[f"phase_{phase}_model"])


def _independent_provider_cost(
    records: Iterable[_CallRecord], parameters: dict[str, Any]
) -> float:
    """Re-price records independently from the incremental simulation ledger."""

    total = 0.0
    cache_scale = parameters["cache_cost_scale"]
    input_tier = parameters["long_context_input_multiplier"]
    output_tier = parameters["long_context_output_multiplier"]
    for record in records:
        prefix = f"{record.model}_"
        applied_input_tier = input_tier if record.long_context else 1.0
        applied_output_tier = output_tier if record.long_context else 1.0
        total += (
            record.uncached_input_tokens
            * parameters[prefix + "input_usd_per_million_tokens"]
            * applied_input_tier
            + record.cache_read_tokens
            * parameters[prefix + "cache_read_usd_per_million_tokens"]
            * cache_scale
            * applied_input_tier
            + record.cache_write_tokens
            * parameters[prefix + "cache_write_usd_per_million_tokens"]
            * cache_scale
            * applied_input_tier
            + record.output_tokens
            * parameters[prefix + "output_usd_per_million_tokens"]
            * applied_output_tier
        ) / 1_000_000.0
    return total


def _diagnostic(check_id: str, difference: float, tolerance: float, message: str) -> dict[str, Any]:
    passed = math.isfinite(difference) and abs(difference) <= tolerance
    return {
        "check_id": check_id,
        "status": "pass" if passed else "fail",
        "value": float(abs(difference)) if math.isfinite(difference) else 1e308,
        "threshold": float(tolerance),
        "invalidates_hypotheses": not passed,
        "message": message,
    }


def _simulate_task(
    run_seed: int,
    task_index: int,
    parameters: dict[str, Any],
    incoming_cache: tuple[float, str] | None,
) -> tuple[dict[str, Any], tuple[float, str] | None]:
    task_stream = f"task/{task_index}"
    profile_scale = parameters["scenario_profile_effect_scale"]
    effective_latency_multiplier = 1.0 + profile_scale * (
        parameters["latency_multiplier"] - 1.0
    )
    effective_tool_efficiency = 1.0 + profile_scale * (
        parameters["tool_efficiency_multiplier"] - 1.0
    )

    complexity = _clamp(
        _normal(
            run_seed,
            f"{task_stream}/latent/complexity",
            parameters["task_complexity_mean"],
            parameters["task_complexity_sd"],
        ),
        0.0,
        1.0,
    )
    initial_context = _nonnegative_normal(
        run_seed,
        f"{task_stream}/latent/initial-context",
        parameters["initial_context_tokens_mean"],
        parameters["initial_context_tokens_sd"],
    )
    latent_tool_calls = _nonnegative_normal(
        run_seed,
        f"{task_stream}/latent/required-tool-calls",
        parameters["required_tool_calls_mean"],
        parameters["required_tool_calls_sd"],
    )
    required_tool_calls = _stochastic_count(
        run_seed,
        f"{task_stream}/required-tool-calls",
        latent_tool_calls / effective_tool_efficiency,
    )
    planned_model_calls = _stochastic_count(
        run_seed,
        f"{task_stream}/planned-model-calls",
        parameters["base_model_calls_mean"]
        + complexity * parameters["model_calls_per_complexity"],
        minimum=1,
    )
    latent_task_output = _nonnegative_normal(
        run_seed,
        f"{task_stream}/latent/task-output",
        parameters["task_output_tokens_mean"],
        parameters["task_output_tokens_sd"],
    )

    exposed_tools = int(
        math.floor(
            parameters["registered_tool_count"] * parameters["tool_exposure_fraction"]
            + 0.5
        )
    )
    relevant_tools = parameters["relevant_tool_count"]
    availability_fraction = (
        1.0
        if relevant_tools == 0
        else min(1.0, exposed_tools / float(relevant_tools))
    )
    distractors = max(0, exposed_tools - relevant_tools)
    selection_probability = availability_fraction * _logistic(
        _probability_logit(parameters["tool_selection_accuracy"])
        - distractors * parameters["tool_confusion_penalty_logit"]
    )
    schema_tokens_per_call = exposed_tools * parameters["tool_schema_tokens_per_tool"]
    stable_prefix_tokens = (
        parameters["prompt_tokens"]
        + parameters["orchestration_tokens_per_call"]
        + schema_tokens_per_call
    )

    tool_calls = 0
    retries = 0
    successful_tool_actions = 0
    tool_result_tokens = 0.0
    parallel_tool_latencies: list[float] = []
    serial_tool_latency = 0.0
    for action_index in range(required_tool_calls):
        base_result_tokens = _nonnegative_normal(
            run_seed,
            f"{task_stream}/tool/{action_index}/latent-result",
            parameters["tool_result_tokens_mean"],
            parameters["tool_result_tokens_sd"],
        )
        action_succeeded = False
        for attempt in range(parameters["max_retries"] + 1):
            attempt_stream = f"{task_stream}/tool/{action_index}/attempt/{attempt}"
            tool_calls += 1
            selected_correctly = _bernoulli(
                run_seed, f"{attempt_stream}/selection", selection_probability
            )
            tool_error = _bernoulli(
                run_seed,
                f"{attempt_stream}/tool-error",
                parameters["tool_error_probability"],
            )
            is_parallelizable = _bernoulli(
                run_seed,
                f"{attempt_stream}/parallelizable",
                parameters["parallelizable_fraction"],
            )
            parallel_conflict = (
                is_parallelizable
                and parameters["parallelism"] > 1
                and _bernoulli(
                    run_seed,
                    f"{attempt_stream}/parallel-conflict",
                    parameters["parallel_conflict_probability"],
                )
            )
            succeeded = selected_correctly and not tool_error and not parallel_conflict
            result_fraction = 1.0 if succeeded else parameters["failed_tool_result_fraction"]
            tool_result_tokens += (
                min(parameters["tool_output_cap_tokens"], base_result_tokens * result_fraction)
                * parameters["tool_result_retention_fraction"]
            )
            latency = _nonnegative_normal(
                run_seed,
                f"{attempt_stream}/latency",
                parameters["tool_latency_seconds_mean"],
                parameters["tool_latency_seconds_sd"],
            )
            if is_parallelizable and parameters["parallelism"] > 1:
                parallel_tool_latencies.append(latency)
            else:
                serial_tool_latency += latency
            if succeeded:
                action_succeeded = True
                break
            if attempt < parameters["max_retries"]:
                retries += 1
        if action_succeeded:
            successful_tool_actions += 1

    parallel_tool_latency = 0.0
    parallelism = parameters["parallelism"]
    for start in range(0, len(parallel_tool_latencies), parallelism):
        batch = parallel_tool_latencies[start : start + parallelism]
        parallel_tool_latency += max(batch) + parameters["parallel_overhead_seconds"]
    tool_wall_seconds = serial_tool_latency + parallel_tool_latency
    external_tool_cost = tool_calls * parameters["external_tool_cost_usd_per_call"]

    records: list[_CallRecord] = []
    provider_cost = 0.0
    uncached_input_tokens = 0.0
    cache_read_tokens = 0.0
    cache_write_tokens = 0.0
    output_tokens = 0.0
    tool_schema_tokens = 0.0
    model_calls = 0
    compactions = 0
    provider_failures = 0
    context_overflows = 0
    model_wall_seconds = 0.0
    successful_primary_model_qualities: list[float] = []
    cache_state = incoming_cache

    def record_call(
        model: str,
        uncached: float,
        cache_read: float,
        cache_write: float,
        output: float,
        prompt_total: float,
        schema: float,
        long_context: bool,
    ) -> None:
        nonlocal provider_cost
        nonlocal uncached_input_tokens, cache_read_tokens, cache_write_tokens
        nonlocal output_tokens, tool_schema_tokens
        record = _CallRecord(
            model=model,
            uncached_input_tokens=float(uncached),
            cache_read_tokens=float(cache_read),
            cache_write_tokens=float(cache_write),
            output_tokens=float(output),
            prompt_tokens=float(prompt_total),
            schema_tokens=float(schema),
            long_context=long_context,
        )
        records.append(record)
        uncached_input_tokens += uncached
        cache_read_tokens += cache_read
        cache_write_tokens += cache_write
        output_tokens += output
        tool_schema_tokens += schema

        prefix = f"{model}_"
        input_tier = parameters["long_context_input_multiplier"] if long_context else 1.0
        output_tier = parameters["long_context_output_multiplier"] if long_context else 1.0
        provider_cost += (
            uncached
            * parameters[prefix + "input_usd_per_million_tokens"]
            * input_tier
            + cache_read
            * parameters[prefix + "cache_read_usd_per_million_tokens"]
            * parameters["cache_cost_scale"]
            * input_tier
            + cache_write
            * parameters[prefix + "cache_write_usd_per_million_tokens"]
            * parameters["cache_cost_scale"]
            * input_tier
            + output
            * parameters[prefix + "output_usd_per_million_tokens"]
            * output_tier
        ) / 1_000_000.0

    def execute_provider_call(
        call_name: str,
        model: str,
        requested_prompt_tokens: float,
        requested_output_tokens: float,
        *,
        cache_allowed: bool,
    ) -> bool:
        nonlocal cache_state, context_overflows, model_calls, retries, model_wall_seconds
        prompt_total = min(requested_prompt_tokens, parameters["context_window_tokens"])
        if requested_prompt_tokens > parameters["context_window_tokens"]:
            context_overflows += 1
        long_context = prompt_total > parameters["long_context_threshold_tokens"]
        model_latency_multiplier = parameters[f"{model}_latency_multiplier"]
        latency_for_attempt = (
            parameters["harness_latency_seconds_per_call"]
            + parameters["provider_latency_scale"]
            * effective_latency_multiplier
            * model_latency_multiplier
            * (
                parameters["model_latency_base_seconds"]
                + parameters["model_latency_seconds_per_1k_tokens"]
                * (prompt_total + requested_output_tokens)
                / 1_000.0
            )
        )

        for attempt in range(parameters["max_retries"] + 1):
            model_calls += 1
            model_wall_seconds += latency_for_attempt
            failed = _bernoulli(
                run_seed,
                f"{task_stream}/provider/{call_name}/attempt/{attempt}/error",
                parameters["provider_error_probability"],
            )
            if failed:
                billable_fraction = parameters["failed_request_billable_fraction"]
                charged_prompt = prompt_total * billable_fraction
                charged_schema = min(schema_tokens_per_call, prompt_total) * billable_fraction
                record_call(
                    model,
                    charged_prompt,
                    0.0,
                    0.0,
                    0.0,
                    charged_prompt,
                    charged_schema,
                    long_context,
                )
                if attempt < parameters["max_retries"]:
                    retries += 1
                    model_wall_seconds += parameters["retry_delay_seconds"] * (
                        parameters["retry_backoff_multiplier"] ** attempt
                    )
                continue

            cache_read = 0.0
            cache_write = 0.0
            eligible_prefix = min(stable_prefix_tokens, prompt_total)
            cache_enabled = (
                cache_allowed
                and parameters["cache_retention_seconds"] > 0.0
                and eligible_prefix >= parameters["cache_minimum_tokens"]
            )
            if cache_enabled:
                cached_prefix = 0.0
                cached_model = ""
                if cache_state is not None:
                    cached_prefix, cached_model = cache_state
                gap = 0.0
                if parameters["inter_call_gap_seconds_mean"] > 0.0:
                    gap = _rng(
                        run_seed, f"{task_stream}/provider/{call_name}/cache-gap"
                    ).expovariate(1.0 / parameters["inter_call_gap_seconds_mean"])
                survival_probability = math.exp(
                    -gap / parameters["cache_retention_seconds"]
                )
                hit_probability = (
                    parameters["session_continuity_probability"]
                    * parameters["prefix_stability_probability"]
                    * survival_probability
                )
                if (
                    cached_model == model
                    and cached_prefix > 0.0
                    and _bernoulli(
                        run_seed,
                        f"{task_stream}/provider/{call_name}/cache-hit",
                        hit_probability,
                    )
                ):
                    cache_read = min(cached_prefix, eligible_prefix)
                cache_write = max(0.0, eligible_prefix - cache_read)
                cache_state = (eligible_prefix, model)
            uncached = max(0.0, prompt_total - cache_read - cache_write)
            produced_output = min(
                requested_output_tokens, parameters["model_output_cap_tokens"]
            )
            record_call(
                model,
                uncached,
                cache_read,
                cache_write,
                produced_output,
                prompt_total,
                min(schema_tokens_per_call, prompt_total),
                long_context,
            )
            return True
        return False

    dynamic_context = initial_context
    remaining_task_output = latent_task_output
    compaction_quality_loss = 0.0
    trigger_tokens = min(
        parameters["context_window_tokens"] * parameters["compaction_trigger_fraction"],
        parameters["context_window_tokens"] - parameters["compaction_reserve_tokens"],
    )
    for call_index in range(planned_model_calls):
        projected_prompt = stable_prefix_tokens + dynamic_context
        if parameters["compaction_enabled"] and projected_prompt > trigger_tokens:
            compactions += 1
            summary_output = min(
                parameters["model_output_cap_tokens"],
                dynamic_context * parameters["compaction_summary_fraction"],
            )
            compact_model = _model_for_phase(parameters, "compact")
            compacted = execute_provider_call(
                f"compact/{call_index}",
                compact_model,
                projected_prompt,
                summary_output,
                cache_allowed=False,
            )
            if compacted:
                dynamic_context = (
                    min(dynamic_context, parameters["compaction_keep_tokens"])
                    + summary_output
                )
                compaction_quality_loss += parameters["compaction_information_loss"]
                if _bernoulli(
                    run_seed,
                    f"{task_stream}/compact/{call_index}/cache-reset",
                    parameters["compaction_cache_reset_probability"],
                ):
                    cache_state = None
            else:
                provider_failures += 1

        if planned_model_calls == 1:
            phase = "execute"
        elif call_index == 0:
            phase = "plan"
        elif call_index == planned_model_calls - 1:
            phase = "verify"
        else:
            phase = "execute"
        model = _model_for_phase(parameters, phase)
        calls_remaining = planned_model_calls - call_index
        requested_output = min(
            parameters["model_output_cap_tokens"],
            remaining_task_output / calls_remaining if calls_remaining else 0.0,
        )
        succeeded = execute_provider_call(
            f"main/{call_index}",
            model,
            stable_prefix_tokens + dynamic_context,
            requested_output,
            cache_allowed=True,
        )
        if succeeded:
            successful_primary_model_qualities.append(parameters[f"{model}_quality_logit"])
            remaining_task_output = max(0.0, remaining_task_output - requested_output)
            dynamic_context += requested_output * parameters["output_retention_fraction"]
        else:
            provider_failures += 1
        if planned_model_calls > 0:
            dynamic_context += tool_result_tokens / planned_model_calls
        dynamic_context += parameters["context_growth_tokens_per_call"]

    tool_success_fraction = (
        1.0
        if required_tool_calls == 0
        else successful_tool_actions / required_tool_calls
    )
    average_model_quality = (
        sum(successful_primary_model_qualities) / len(successful_primary_model_qualities)
        if successful_primary_model_qualities
        else 0.0
    )
    quality_logit = (
        parameters["base_quality_logit"]
        + profile_scale * parameters["quality_offset_logit"]
        + average_model_quality
        - complexity * parameters["difficulty_quality_penalty_logit"]
        + (tool_success_fraction - 1.0)
        * parameters["tool_success_quality_weight_logit"]
        - provider_failures * parameters["provider_failure_quality_penalty_logit"]
        - retries * parameters["retry_quality_penalty_logit"]
        - compaction_quality_loss
        - context_overflows * parameters["context_overflow_quality_penalty_logit"]
    )
    latent_quality = _logistic(quality_logit)
    measured_quality = _clamp(
        latent_quality
        + _normal(
            run_seed,
            f"{task_stream}/verification/noise",
            0.0,
            parameters["verification_noise_sd"]
            * (1.0 - parameters["verification_strength"]),
        ),
        0.0,
        1.0,
    )

    unnecessary_tool_ratio = max(0, tool_calls - required_tool_calls) / max(
        1, required_tool_calls
    )
    violation_probability = _logistic(
        _probability_logit(parameters["policy_violation_base_probability"])
        + parameters["policy_violation_tool_scale"] * unnecessary_tool_ratio
    )
    policy_violation = _bernoulli(
        run_seed, f"{task_stream}/policy/violation", violation_probability
    )
    violation_detected = policy_violation and _bernoulli(
        run_seed,
        f"{task_stream}/policy/detection",
        parameters["verification_strength"],
    )
    provisionally_accepted = (
        measured_quality >= parameters["quality_acceptance_threshold"]
        and not violation_detected
        and bool(successful_primary_model_qualities)
    )

    review_minutes = 0.0
    if _bernoulli(
        run_seed,
        f"{task_stream}/human/review",
        parameters["human_review_probability"],
    ):
        review_minutes = _nonnegative_normal(
            run_seed,
            f"{task_stream}/human/review-minutes",
            parameters["human_review_minutes_mean"],
            parameters["human_review_minutes_sd"],
        )
    approval_minutes = (
        tool_calls * parameters["human_approval_seconds_per_tool_call"] / 60.0
    )
    base_human_minutes = review_minutes + approval_minutes
    base_wall_seconds = (
        tool_wall_seconds + model_wall_seconds + base_human_minutes * 60.0
    )

    return (
        {
            "accepted": provisionally_accepted,
            "quality": measured_quality,
            "policy_violation": policy_violation,
            "provider_cost": provider_cost,
            "external_tool_cost": external_tool_cost,
            "human_minutes": base_human_minutes,
            "wall_seconds": base_wall_seconds,
            "uncached_input_tokens": uncached_input_tokens,
            "cache_read_tokens": cache_read_tokens,
            "cache_write_tokens": cache_write_tokens,
            "output_tokens": output_tokens,
            "tool_schema_tokens": tool_schema_tokens,
            "tool_result_tokens": tool_result_tokens,
            "model_calls": model_calls,
            "tool_calls": tool_calls,
            "retries": retries,
            "compactions": compactions,
            "records": records,
        },
        cache_state,
    )


def simulate(run: dict[str, Any]) -> dict[str, Any]:
    """Simulate one paired portfolio replication and return the 24 outcomes."""

    if not isinstance(run, dict):
        raise ValueError("run must be a mapping")
    seed = run.get("seed")
    if isinstance(seed, bool) or not isinstance(seed, int):
        raise ValueError("run['seed'] must be an integer")
    parameters = _validated_parameters(run.get("parameters"))
    task_count = parameters["tasks_per_run"]

    tasks: list[dict[str, Any]] = []
    all_records: list[_CallRecord] = []
    cache_state: tuple[float, str] | None = None
    for task_index in range(task_count):
        task, cache_state = _simulate_task(seed, task_index, parameters, cache_state)
        tasks.append(task)
        all_records.extend(task["records"])

    total_provider_cost = sum(task["provider_cost"] for task in tasks)
    total_external_tool_cost = sum(task["external_tool_cost"] for task in tasks)
    discounted_task_costs = [
        task["provider_cost"] * (1.0 - parameters["automatic_discount_fraction"])
        for task in tasks
    ]
    discounted_provider_cost = sum(discounted_task_costs)

    budget_exhausted = [False] * task_count
    allocated_subscription_fee = 0.0
    if parameters["billing_mode"] == "subscription":
        period_share = task_count / parameters["billing_period_tasks"]
        allowance = parameters["subscription_allowance_usd_per_period"] * period_share
        allocated_subscription_fee = (
            parameters["subscription_fee_usd_per_period"] * period_share
        )
        cumulative = 0.0
        for index, task_cost in enumerate(discounted_task_costs):
            cumulative += task_cost
            budget_exhausted[index] = cumulative > allowance + 1e-15
        overage_usage = max(0.0, discounted_provider_cost - allowance)
        provider_marginal_cash = (
            overage_usage * parameters["overage_multiplier"]
            if parameters["overage_enabled"]
            else 0.0
        )
    else:
        provider_marginal_cash = discounted_provider_cost

    marginal_cash_total = provider_marginal_cash + total_external_tool_cost
    allocated_cash_total = marginal_cash_total + allocated_subscription_fee

    accepted_count = 0
    total_quality = 0.0
    policy_violation_count = 0
    total_human_minutes = 0.0
    total_wall_seconds = 0.0
    total_failure_cost = 0.0
    total_sla_cost = 0.0
    for index, task in enumerate(tasks):
        accepted = bool(task["accepted"])
        if (
            parameters["billing_mode"] == "subscription"
            and budget_exhausted[index]
            and not parameters["overage_enabled"]
        ):
            accepted = False
        human_minutes = task["human_minutes"]
        wall_seconds = task["wall_seconds"]
        if not accepted:
            human_minutes += parameters["human_rework_minutes_per_rejected_task"]
            wall_seconds += parameters["human_rework_minutes_per_rejected_task"] * 60.0
            total_failure_cost += parameters["failure_cost_usd"]
        accepted_count += int(accepted)
        total_quality += task["quality"]
        policy_violation_count += int(task["policy_violation"])
        total_human_minutes += human_minutes
        total_wall_seconds += wall_seconds
        total_sla_cost += (
            max(0.0, wall_seconds - parameters["sla_seconds_per_task"])
            / 60.0
            * parameters["sla_penalty_usd_per_minute"]
        )

    total_human_cost = (
        total_human_minutes / 60.0 * parameters["human_hourly_value_usd"]
    )
    economic_loss_total = (
        allocated_cash_total
        + total_human_cost
        + total_failure_cost
        + total_sla_cost
    )

    total_uncached = sum(task["uncached_input_tokens"] for task in tasks)
    total_cache_read = sum(task["cache_read_tokens"] for task in tasks)
    total_cache_write = sum(task["cache_write_tokens"] for task in tasks)
    total_output = sum(task["output_tokens"] for task in tasks)
    total_schema = sum(task["tool_schema_tokens"] for task in tasks)
    total_tool_results = sum(task["tool_result_tokens"] for task in tasks)
    total_model_calls = sum(task["model_calls"] for task in tasks)
    total_tool_calls = sum(task["tool_calls"] for task in tasks)
    total_retries = sum(task["retries"] for task in tasks)
    total_compactions = sum(task["compactions"] for task in tasks)
    total_prompt_tokens = total_uncached + total_cache_read + total_cache_write

    accepted_fraction = accepted_count / task_count
    provider_cost_per_task = total_provider_cost / task_count
    marginal_cash_per_task = marginal_cash_total / task_count
    allocated_cash_per_task = allocated_cash_total / task_count
    economic_loss_per_task = economic_loss_total / task_count
    wall_seconds_per_task = total_wall_seconds / task_count
    outcomes = {
        "accepted_task_fraction": accepted_fraction,
        "external_quality_score": total_quality / task_count,
        "policy_violation_fraction": policy_violation_count / task_count,
        "provider_cost_usd_per_task": provider_cost_per_task,
        "marginal_cash_cost_usd_per_task": marginal_cash_per_task,
        "allocated_cash_cost_usd_per_task": allocated_cash_per_task,
        "economic_loss_usd_per_task": economic_loss_per_task,
        "normalized_provider_cost": provider_cost_per_task
        / parameters["provider_cost_reference_usd_per_task"],
        "normalized_cost_per_verified_work": economic_loss_per_task
        / (
            max(accepted_fraction, parameters["normalization_acceptance_floor"])
            * parameters["verified_task_value_usd"]
        ),
        "wall_seconds_per_task": wall_seconds_per_task,
        "normalized_wall_time": wall_seconds_per_task
        / parameters["sla_seconds_per_task"],
        "human_minutes_per_task": total_human_minutes / task_count,
        "uncached_input_tokens_per_task": total_uncached / task_count,
        "cache_read_tokens_per_task": total_cache_read / task_count,
        "cache_write_tokens_per_task": total_cache_write / task_count,
        "output_tokens_per_task": total_output / task_count,
        "tool_schema_tokens_per_task": total_schema / task_count,
        "tool_result_tokens_per_task": total_tool_results / task_count,
        "model_calls_per_task": total_model_calls / task_count,
        "tool_calls_per_task": total_tool_calls / task_count,
        "retries_per_task": total_retries / task_count,
        "compactions_per_task": total_compactions / task_count,
        "cache_hit_fraction": (
            total_cache_read / total_prompt_tokens if total_prompt_tokens > 0.0 else 0.0
        ),
        "budget_exhausted_fraction": sum(budget_exhausted) / task_count,
    }

    record_prompt_total = sum(record.prompt_tokens for record in all_records)
    record_partition_total = sum(
        record.uncached_input_tokens
        + record.cache_read_tokens
        + record.cache_write_tokens
        for record in all_records
    )
    repriced_provider_cost = _independent_provider_cost(all_records, parameters)
    expected_allocated_cash = marginal_cash_total + allocated_subscription_fee
    fraction_violation = max(
        max(0.0, -outcomes[name], outcomes[name] - 1.0)
        for name in (
            "accepted_task_fraction",
            "external_quality_score",
            "policy_violation_fraction",
            "cache_hit_fraction",
            "budget_exhausted_fraction",
        )
    )
    nonnegative_violation = max(
        (0.0 if math.isfinite(value) and value >= 0.0 else 1.0)
        for value in outcomes.values()
    )
    diagnostics = [
        _diagnostic(
            "prompt-token-partition-reconciliation",
            record_partition_total - record_prompt_total,
            max(1e-8, record_prompt_total * 1e-12),
            "Uncached input, cache reads, and cache writes reconcile to billed prompt tokens.",
        ),
        _diagnostic(
            "provider-ledger-repricing",
            total_provider_cost - repriced_provider_cost,
            max(1e-10, repriced_provider_cost * 1e-10),
            "An independent pass over call records reproduces the provider token ledger.",
        ),
        _diagnostic(
            "cash-allocation-reconciliation",
            allocated_cash_total - expected_allocated_cash,
            max(1e-10, expected_allocated_cash * 1e-10),
            "Allocated cash reconciles to marginal cash plus the prorated subscription fee.",
        ),
        _diagnostic(
            "accepted-task-count-reconciliation",
            outcomes["accepted_task_fraction"] * task_count - accepted_count,
            1e-10,
            "The accepted-task fraction reconciles to the portfolio task count.",
        ),
        _diagnostic(
            "bounded-fractions",
            fraction_violation,
            1e-12,
            "All probability-like outcomes remain within [0, 1].",
        ),
        _diagnostic(
            "finite-nonnegative-outcomes",
            nonnegative_violation,
            0.0,
            "All 24 outcomes are finite and non-negative.",
        ),
        _diagnostic(
            "schema-contained-in-prompt",
            max(0.0, total_schema - total_prompt_tokens),
            max(1e-8, total_prompt_tokens * 1e-12),
            "Repeated tool-schema tokens do not exceed total billed prompt tokens.",
        ),
    ]
    if tuple(outcomes) != OUTCOME_NAMES:
        raise RuntimeError("internal outcome schema drift")
    return {"outcomes": outcomes, "diagnostics": diagnostics}
