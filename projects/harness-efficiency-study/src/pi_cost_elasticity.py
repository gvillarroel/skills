"""Deterministic, offline cost-elasticity model for Pi routed through Copilot.

This module never calls Pi, GitHub Copilot, a model API, or the network.  It
turns explicit hypothetical token flows into a call-by-call billing ledger.
Every input token belongs to exactly one mutually exclusive billing bucket:
uncached input, cache read, or cache write.  The complete prompt size selects
the short- or long-context price tier for the entire request.

The rate card is the public GitHub Copilot model-pricing table captured for the
2026-09-04 study.  In particular, the Copilot threshold for Luna is 200,000
input tokens, while the thresholds for Terra and Sol are 272,000 tokens.
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
from collections.abc import Callable, Iterable, Sequence
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

MODEL_VERSION = "pi-copilot-cost-elasticity-1.0.0"
AI_CREDIT_USD = 0.01
RATE_SOURCE_URL = (
    "https://docs.github.com/en/copilot/reference/copilot-billing/models-and-pricing"
)


@dataclass(frozen=True)
class TierRate:
    """USD prices per one million tokens for one pricing tier."""

    uncached_input: float
    cache_read: float
    cache_write: float
    output: float


@dataclass(frozen=True)
class ModelRate:
    """Short/long prices and the Copilot long-context boundary."""

    model: str
    long_context_threshold_tokens: int
    short: TierRate
    long: TierRate


RATE_CARD: dict[str, ModelRate] = {
    "luna": ModelRate(
        model="luna",
        long_context_threshold_tokens=200_000,
        short=TierRate(0.20, 0.02, 0.25, 1.20),
        long=TierRate(0.40, 0.04, 0.50, 1.80),
    ),
    "terra": ModelRate(
        model="terra",
        long_context_threshold_tokens=272_000,
        short=TierRate(2.00, 0.20, 2.50, 12.00),
        long=TierRate(4.00, 0.40, 5.00, 18.00),
    ),
    "sol": ModelRate(
        model="sol",
        long_context_threshold_tokens=272_000,
        short=TierRate(4.00, 0.40, 5.00, 20.00),
        long=TierRate(8.00, 0.80, 10.00, 30.00),
    ),
}


def _round_metric(value: float) -> float:
    """Keep exported arithmetic readable while retaining sub-microcent detail."""

    return round(float(value), 12)


@dataclass(frozen=True)
class CallSpec:
    """Unpriced token partition for one hypothetical provider request."""

    call_kind: str
    input_uncached_tokens: int = 0
    cache_read_tokens: int = 0
    cache_write_tokens: int = 0
    output_tokens: int = 0
    logical_step: int = 0
    compaction_event: bool = False
    discarded_context_tokens: int = 0
    note: str = ""

    @property
    def full_input_tokens(self) -> int:
        return (
            self.input_uncached_tokens
            + self.cache_read_tokens
            + self.cache_write_tokens
        )

    def validate(self) -> None:
        integer_fields = {
            "input_uncached_tokens": self.input_uncached_tokens,
            "cache_read_tokens": self.cache_read_tokens,
            "cache_write_tokens": self.cache_write_tokens,
            "output_tokens": self.output_tokens,
            "logical_step": self.logical_step,
            "discarded_context_tokens": self.discarded_context_tokens,
        }
        for field_name, value in integer_fields.items():
            if isinstance(value, bool) or not isinstance(value, int) or value < 0:
                raise ValueError(f"{field_name} must be a non-negative integer")
        if not self.call_kind:
            raise ValueError("call_kind must be non-empty")


@dataclass(frozen=True)
class PricedCall:
    """One row of the mutually exclusive call-level billing ledger."""

    contrast_id: str
    scenario_id: str
    role: str
    model: str
    call_index: int
    logical_step: int
    call_kind: str
    input_uncached_tokens: int
    cache_read_tokens: int
    cache_write_tokens: int
    full_input_tokens: int
    output_tokens: int
    long_context_threshold_tokens: int
    pricing_tier: str
    input_rate_per_million: float
    cache_read_rate_per_million: float
    cache_write_rate_per_million: float
    output_rate_per_million: float
    input_uncached_cost_usd: float
    cache_read_cost_usd: float
    cache_write_cost_usd: float
    output_cost_usd: float
    provider_cost_usd: float
    ai_credits: float
    compaction_event: bool
    discarded_context_tokens: int
    note: str


@dataclass(frozen=True)
class ScenarioBuild:
    """Call specs plus non-billing counters for a scenario."""

    calls: tuple[CallSpec, ...]
    main_call_count: int
    tool_calls: int = 0
    tool_result_tokens_generated: int = 0
    tool_result_tokens_injected: int = 0


@dataclass(frozen=True)
class ScenarioSimulation:
    """Priced scenario with the exact parameter mapping that generated it."""

    contrast_id: str
    study_family: str
    scenario_id: str
    role: str
    model: str
    changed_parameter: str
    changed_value: Any
    parameters: dict[str, Any]
    interpretation: str
    build: ScenarioBuild
    ledger: tuple[PricedCall, ...]


@dataclass(frozen=True)
class ContrastPlan:
    """A one-factor-at-a-time comparison."""

    contrast_id: str
    study_family: str
    changed_parameter: str
    baseline_parameters: dict[str, Any]
    comparison_parameters: dict[str, Any]
    builder: Callable[[ModelRate, dict[str, Any]], ScenarioBuild]
    interpretation: str

    def validate_ofat(self) -> None:
        keys = set(self.baseline_parameters) | set(self.comparison_parameters)
        differences = [
            key
            for key in sorted(keys)
            if self.baseline_parameters.get(key) != self.comparison_parameters.get(key)
        ]
        if differences != [self.changed_parameter]:
            raise ValueError(
                f"{self.contrast_id} is not OFAT: expected only "
                f"{self.changed_parameter!r}, found {differences!r}"
            )


@dataclass(frozen=True)
class SimulationBundle:
    """Analysis-ready results from all deterministic contrasts."""

    scenarios: tuple[dict[str, Any], ...]
    ledger: tuple[dict[str, Any], ...]
    contrasts: tuple[dict[str, Any], ...]
    scale_results: tuple[dict[str, Any], ...]
    break_even: tuple[dict[str, Any], ...]
    volumes: tuple[int, ...]


def _ensure_nonnegative_int(name: str, value: Any) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError(f"{name} must be a non-negative integer")
    return value


def price_call(
    spec: CallSpec,
    model_rate: ModelRate,
    *,
    contrast_id: str,
    scenario_id: str,
    role: str,
    call_index: int,
) -> PricedCall:
    """Price one call, using total input to select the request-wide tier."""

    spec.validate()
    full_input = spec.full_input_tokens
    is_long = full_input > model_rate.long_context_threshold_tokens
    tier_name = "long" if is_long else "short"
    rates = model_rate.long if is_long else model_rate.short
    scale = 1_000_000.0
    input_cost = _round_metric(
        spec.input_uncached_tokens * rates.uncached_input / scale
    )
    read_cost = _round_metric(spec.cache_read_tokens * rates.cache_read / scale)
    write_cost = _round_metric(spec.cache_write_tokens * rates.cache_write / scale)
    output_cost = _round_metric(spec.output_tokens * rates.output / scale)
    provider_cost = _round_metric(input_cost + read_cost + write_cost + output_cost)
    return PricedCall(
        contrast_id=contrast_id,
        scenario_id=scenario_id,
        role=role,
        model=model_rate.model,
        call_index=call_index,
        logical_step=spec.logical_step,
        call_kind=spec.call_kind,
        input_uncached_tokens=spec.input_uncached_tokens,
        cache_read_tokens=spec.cache_read_tokens,
        cache_write_tokens=spec.cache_write_tokens,
        full_input_tokens=full_input,
        output_tokens=spec.output_tokens,
        long_context_threshold_tokens=model_rate.long_context_threshold_tokens,
        pricing_tier=tier_name,
        input_rate_per_million=rates.uncached_input,
        cache_read_rate_per_million=rates.cache_read,
        cache_write_rate_per_million=rates.cache_write,
        output_rate_per_million=rates.output,
        input_uncached_cost_usd=input_cost,
        cache_read_cost_usd=read_cost,
        cache_write_cost_usd=write_cost,
        output_cost_usd=output_cost,
        provider_cost_usd=provider_cost,
        ai_credits=_round_metric(provider_cost / AI_CREDIT_USD),
        compaction_event=spec.compaction_event,
        discarded_context_tokens=spec.discarded_context_tokens,
        note=spec.note,
    )


def _repeated_prompt_build(
    *,
    stable_prefix_tokens: int,
    dynamic_tokens: int,
    model_calls: int,
    output_tokens_per_call: int,
    prefix_churn: bool = False,
    initially_hot: bool = False,
) -> ScenarioBuild:
    """Repeat a fixed prompt while making its cache semantics explicit."""

    for name, value in (
        ("stable_prefix_tokens", stable_prefix_tokens),
        ("dynamic_tokens", dynamic_tokens),
        ("model_calls", model_calls),
        ("output_tokens_per_call", output_tokens_per_call),
    ):
        _ensure_nonnegative_int(name, value)
    if model_calls == 0:
        return ScenarioBuild(calls=(), main_call_count=0)

    calls: list[CallSpec] = []
    for index in range(1, model_calls + 1):
        if prefix_churn:
            read_tokens = 0
            write_tokens = stable_prefix_tokens
            cache_note = "changed prefix is rewritten"
        elif initially_hot or index > 1:
            read_tokens = stable_prefix_tokens
            write_tokens = 0
            cache_note = "stable prefix is read from cache"
        else:
            read_tokens = 0
            write_tokens = stable_prefix_tokens
            cache_note = "first stable prefix is written to cache"
        calls.append(
            CallSpec(
                call_kind="model_roundtrip",
                input_uncached_tokens=dynamic_tokens,
                cache_read_tokens=read_tokens,
                cache_write_tokens=write_tokens,
                output_tokens=output_tokens_per_call,
                logical_step=index,
                note=cache_note,
            )
        )
    return ScenarioBuild(calls=tuple(calls), main_call_count=model_calls)


def _build_system_prompt(model: ModelRate, p: dict[str, Any]) -> ScenarioBuild:
    del model
    system_tokens = int(p["system_prompt_tokens"])
    other_tokens = int(p["other_prompt_tokens"])
    if p["system_cache_mode"] == "stable":
        stable = other_tokens + system_tokens
        dynamic = 0
    elif p["system_cache_mode"] == "dynamic":
        stable = other_tokens
        dynamic = system_tokens
    else:
        raise ValueError(f"unsupported system_cache_mode: {p['system_cache_mode']}")
    return _repeated_prompt_build(
        stable_prefix_tokens=stable,
        dynamic_tokens=dynamic,
        model_calls=int(p["model_calls"]),
        output_tokens_per_call=int(p["output_tokens_per_call"]),
    )


def _build_threshold_crossing(model: ModelRate, p: dict[str, Any]) -> ScenarioBuild:
    system_tokens = int(p["system_prompt_tokens"])
    other_tokens = model.long_context_threshold_tokens - 4_500
    return _repeated_prompt_build(
        stable_prefix_tokens=other_tokens + system_tokens,
        dynamic_tokens=0,
        model_calls=1,
        output_tokens_per_call=int(p["output_tokens_per_call"]),
        initially_hot=p["cache_state"] == "warm",
    )


def _build_schema(model: ModelRate, p: dict[str, Any]) -> ScenarioBuild:
    del model
    return _repeated_prompt_build(
        stable_prefix_tokens=int(p["other_prompt_tokens"])
        + int(p["visible_tool_schema_tokens"]),
        dynamic_tokens=0,
        model_calls=int(p["model_calls"]),
        output_tokens_per_call=int(p["output_tokens_per_call"]),
    )


def _build_output(model: ModelRate, p: dict[str, Any]) -> ScenarioBuild:
    del model
    return _repeated_prompt_build(
        stable_prefix_tokens=int(p["prompt_tokens"]),
        dynamic_tokens=0,
        model_calls=int(p["model_calls"]),
        output_tokens_per_call=int(p["output_tokens_per_call"]),
    )


def _build_prefix_churn(model: ModelRate, p: dict[str, Any]) -> ScenarioBuild:
    del model
    return _repeated_prompt_build(
        stable_prefix_tokens=int(p["prompt_tokens"]),
        dynamic_tokens=0,
        model_calls=int(p["model_calls"]),
        output_tokens_per_call=int(p["output_tokens_per_call"]),
        prefix_churn=bool(p["prefix_churn"]),
    )


def _build_extra_roundtrip(model: ModelRate, p: dict[str, Any]) -> ScenarioBuild:
    del model
    return _repeated_prompt_build(
        stable_prefix_tokens=int(p["prompt_tokens"]),
        dynamic_tokens=0,
        model_calls=int(p["model_calls"]),
        output_tokens_per_call=int(p["output_tokens_per_call"]),
    )


def _tool_loop_build(
    *,
    tool_count: int,
    execution_mode: str,
    initial_prompt_tokens: int,
    tool_argument_tokens: int,
    tool_result_tokens: int,
    retain_tool_results: bool,
    final_output_tokens: int,
) -> ScenarioBuild:
    """Build sequential or one-batch tool use with append-only cache writes."""

    for name, value in (
        ("tool_count", tool_count),
        ("initial_prompt_tokens", initial_prompt_tokens),
        ("tool_argument_tokens", tool_argument_tokens),
        ("tool_result_tokens", tool_result_tokens),
        ("final_output_tokens", final_output_tokens),
    ):
        _ensure_nonnegative_int(name, value)

    if tool_count == 0:
        return ScenarioBuild(
            calls=(
                CallSpec(
                    call_kind="final_response",
                    cache_write_tokens=initial_prompt_tokens,
                    output_tokens=final_output_tokens,
                    logical_step=1,
                    note="cold initial prompt",
                ),
            ),
            main_call_count=1,
        )

    result_append = tool_result_tokens if retain_tool_results else 0
    calls: list[CallSpec] = []

    if execution_mode == "batched":
        calls.append(
            CallSpec(
                call_kind="parallel_tool_request",
                cache_write_tokens=initial_prompt_tokens,
                output_tokens=tool_count * tool_argument_tokens,
                logical_step=1,
                note="all tool arguments emitted in one model roundtrip",
            )
        )
        append_tokens = tool_count * (tool_argument_tokens + result_append)
        calls.append(
            CallSpec(
                call_kind="final_response",
                cache_read_tokens=initial_prompt_tokens,
                cache_write_tokens=append_tokens,
                output_tokens=final_output_tokens,
                logical_step=2,
                note="parallel tool arguments and retained results appended once",
            )
        )
    elif execution_mode == "sequential":
        cached_prompt = initial_prompt_tokens
        calls.append(
            CallSpec(
                call_kind="tool_request",
                cache_write_tokens=cached_prompt,
                output_tokens=tool_argument_tokens,
                logical_step=1,
                note="cold initial prompt before first tool",
            )
        )
        append_tokens = tool_argument_tokens + result_append
        for tool_index in range(2, tool_count + 1):
            calls.append(
                CallSpec(
                    call_kind="tool_request",
                    cache_read_tokens=cached_prompt,
                    cache_write_tokens=append_tokens,
                    output_tokens=tool_argument_tokens,
                    logical_step=tool_index,
                    note="prior tool exchange appended before next tool",
                )
            )
            cached_prompt += append_tokens
        calls.append(
            CallSpec(
                call_kind="final_response",
                cache_read_tokens=cached_prompt,
                cache_write_tokens=append_tokens,
                output_tokens=final_output_tokens,
                logical_step=tool_count + 1,
                note="last tool exchange appended before final response",
            )
        )
    else:
        raise ValueError(f"unsupported execution_mode: {execution_mode}")

    return ScenarioBuild(
        calls=tuple(calls),
        main_call_count=len(calls),
        tool_calls=tool_count,
        tool_result_tokens_generated=tool_count * tool_result_tokens,
        tool_result_tokens_injected=tool_count * result_append,
    )


def _build_tools(model: ModelRate, p: dict[str, Any]) -> ScenarioBuild:
    del model
    return _tool_loop_build(
        tool_count=int(p["tool_count"]),
        execution_mode=str(p["execution_mode"]),
        initial_prompt_tokens=int(p["initial_prompt_tokens"]),
        tool_argument_tokens=int(p["tool_argument_tokens"]),
        tool_result_tokens=int(p["tool_result_tokens"]),
        retain_tool_results=bool(p["retain_tool_results"]),
        final_output_tokens=int(p["final_output_tokens"]),
    )


def _long_session_build(
    *,
    model: ModelRate,
    main_calls: int,
    initial_prompt_tokens: int,
    growth_tokens_per_call: int,
    main_output_tokens: int,
    compaction_strategy: str,
    compaction_input_mode: str,
    post_compaction_cache_mode: str,
    summary_tokens: int,
    retained_system_tokens: int,
) -> ScenarioBuild:
    """Build a fixed-work long session with optional proactive compaction.

    Work is frozen at ``main_calls`` and a logical 20k-token increment (by
    default) between calls.  Compaction changes only the prompt retained for
    billing and future reasoning.  A compaction call is an additional provider
    request and is therefore represented directly in the ledger.
    """

    for name, value in (
        ("main_calls", main_calls),
        ("initial_prompt_tokens", initial_prompt_tokens),
        ("growth_tokens_per_call", growth_tokens_per_call),
        ("main_output_tokens", main_output_tokens),
        ("summary_tokens", summary_tokens),
        ("retained_system_tokens", retained_system_tokens),
    ):
        _ensure_nonnegative_int(name, value)
    if main_calls < 1:
        raise ValueError("main_calls must be at least one")
    if retained_system_tokens > initial_prompt_tokens:
        raise ValueError("retained_system_tokens cannot exceed initial prompt")

    if compaction_strategy == "none":
        cap: int | None = None
    elif compaction_strategy == "cap_200k":
        cap = 200_000
    elif compaction_strategy == "cap_pricing_threshold":
        cap = model.long_context_threshold_tokens
    else:
        raise ValueError(f"unsupported compaction_strategy: {compaction_strategy}")

    calls: list[CallSpec] = []
    current_prompt = initial_prompt_tokens
    cold_prompt = True
    main_step = 0

    while main_step < main_calls:
        if main_step > 0:
            candidate = current_prompt + growth_tokens_per_call
            if cap is not None and candidate > cap:
                if compaction_input_mode == "uncached":
                    uncached, read, write = current_prompt, 0, 0
                elif compaction_input_mode == "cache_read":
                    uncached, read, write = 0, current_prompt, 0
                elif compaction_input_mode == "cache_write":
                    uncached, read, write = 0, 0, current_prompt
                else:
                    raise ValueError(
                        f"unsupported compaction_input_mode: {compaction_input_mode}"
                    )
                calls.append(
                    CallSpec(
                        call_kind="compaction",
                        input_uncached_tokens=uncached,
                        cache_read_tokens=read,
                        cache_write_tokens=write,
                        output_tokens=summary_tokens,
                        logical_step=main_step,
                        compaction_event=True,
                        discarded_context_tokens=max(
                            current_prompt - summary_tokens, 0
                        ),
                        note=(
                            f"compact before main step {main_step + 1}; "
                            f"input mode={compaction_input_mode}"
                        ),
                    )
                )
                current_prompt = initial_prompt_tokens
                cold_prompt = True
            else:
                current_prompt = candidate

        main_step += 1
        if cold_prompt:
            if post_compaction_cache_mode == "cold_write" or main_step == 1:
                read_tokens = 0
                write_tokens = current_prompt
                note = "cold prompt written after start or compaction"
            elif post_compaction_cache_mode == "retain_system_prefix":
                read_tokens = retained_system_tokens
                write_tokens = current_prompt - retained_system_tokens
                note = "stable system prefix survives compaction"
            else:
                raise ValueError(
                    "post_compaction_cache_mode must be cold_write or "
                    "retain_system_prefix"
                )
            cold_prompt = False
        else:
            read_tokens = current_prompt - growth_tokens_per_call
            write_tokens = growth_tokens_per_call
            note = "prior prompt read; new turn appended"
        calls.append(
            CallSpec(
                call_kind="main_model_call",
                cache_read_tokens=read_tokens,
                cache_write_tokens=write_tokens,
                output_tokens=main_output_tokens,
                logical_step=main_step,
                note=note,
            )
        )

    return ScenarioBuild(calls=tuple(calls), main_call_count=main_calls)


def _build_long_session(model: ModelRate, p: dict[str, Any]) -> ScenarioBuild:
    return _long_session_build(
        model=model,
        main_calls=int(p["main_calls"]),
        initial_prompt_tokens=int(p["initial_prompt_tokens"]),
        growth_tokens_per_call=int(p["growth_tokens_per_call"]),
        main_output_tokens=int(p["main_output_tokens"]),
        compaction_strategy=str(p["compaction_strategy"]),
        compaction_input_mode=str(p["compaction_input_mode"]),
        post_compaction_cache_mode=str(p["post_compaction_cache_mode"]),
        summary_tokens=int(p["summary_tokens"]),
        retained_system_tokens=int(p["retained_system_tokens"]),
    )


def _with_change(
    baseline: dict[str, Any], key: str, comparison_value: Any
) -> tuple[dict[str, Any], dict[str, Any]]:
    left = dict(baseline)
    right = dict(baseline)
    right[key] = comparison_value
    return left, right


def build_contrast_plans() -> tuple[ContrastPlan, ...]:
    """Return the preregistered deterministic OFAT portfolio."""

    plans: list[ContrastPlan] = []

    for calls in (1, 10, 50):
        baseline, comparison = _with_change(
            {
                "system_prompt_tokens": 4_000,
                "other_prompt_tokens": 46_000,
                "system_cache_mode": "stable",
                "model_calls": calls,
                "output_tokens_per_call": 500,
            },
            "system_prompt_tokens",
            5_000,
        )
        plans.append(
            ContrastPlan(
                contrast_id=f"stable-system-{calls}-calls"
                if calls != 1
                else "stable-system-1-call",
                study_family="system_prompt",
                changed_parameter="system_prompt_tokens",
                baseline_parameters=baseline,
                comparison_parameters=comparison,
                builder=_build_system_prompt,
                interpretation=(
                    f"Marginal cost of 1,000 stable system tokens across {calls} "
                    "model call(s); the prefix is written once and then read."
                ),
            )
        )

    baseline, comparison = _with_change(
        {
            "system_prompt_tokens": 4_000,
            "other_prompt_tokens": 46_000,
            "system_cache_mode": "dynamic",
            "model_calls": 10,
            "output_tokens_per_call": 500,
        },
        "system_prompt_tokens",
        5_000,
    )
    plans.append(
        ContrastPlan(
            contrast_id="dynamic-system-10-calls",
            study_family="system_prompt",
            changed_parameter="system_prompt_tokens",
            baseline_parameters=baseline,
            comparison_parameters=comparison,
            builder=_build_system_prompt,
            interpretation=(
                "Marginal cost of 1,000 system tokens when that segment misses "
                "the cache on every one of ten calls."
            ),
        )
    )

    for cache_state in ("cold", "warm"):
        baseline, comparison = _with_change(
            {
                "system_prompt_tokens": 4_000,
                "cache_state": cache_state,
                "output_tokens_per_call": 1_000,
            },
            "system_prompt_tokens",
            5_000,
        )
        plans.append(
            ContrastPlan(
                contrast_id=f"system-threshold-{cache_state}",
                study_family="threshold_discontinuity",
                changed_parameter="system_prompt_tokens",
                baseline_parameters=baseline,
                comparison_parameters=comparison,
                builder=_build_threshold_crossing,
                interpretation=(
                    "The 1,000-token prompt increase moves total input from 500 "
                    "tokens below to 500 tokens above this model's Copilot "
                    f"long-context threshold, with a {cache_state} prefix."
                ),
            )
        )

    for mode in ("sequential", "batched"):
        baseline, comparison = _with_change(
            {
                "tool_count": 4,
                "execution_mode": mode,
                "initial_prompt_tokens": 50_000,
                "tool_argument_tokens": 100,
                "tool_result_tokens": 2_000,
                "retain_tool_results": True,
                "final_output_tokens": 500,
            },
            "tool_count",
            5,
        )
        plans.append(
            ContrastPlan(
                contrast_id=f"{mode}-tools-4-to-5",
                study_family="tool_invocations",
                changed_parameter="tool_count",
                baseline_parameters=baseline,
                comparison_parameters=comparison,
                builder=_build_tools,
                interpretation=(
                    "Marginal fifth tool. Sequential mode adds a provider "
                    "roundtrip and replays accumulated context; batched mode "
                    "only enlarges the existing tool exchange."
                ),
            )
        )

    baseline, comparison = _with_change(
        {
            "tool_count": 4,
            "execution_mode": "sequential",
            "initial_prompt_tokens": 800_000,
            "tool_argument_tokens": 100,
            "tool_result_tokens": 2_000,
            "retain_tool_results": True,
            "final_output_tokens": 500,
        },
        "tool_count",
        5,
    )
    plans.append(
        ContrastPlan(
            contrast_id="tool-count-4-vs-5-sequential-800k",
            study_family="tool_invocations",
            changed_parameter="tool_count",
            baseline_parameters=baseline,
            comparison_parameters=comparison,
            builder=_build_tools,
            interpretation=(
                "Conditional 800k-context stress case for the marginal fifth "
                "sequential tool. Every request uses long-context rates and the "
                "extra roundtrip replays accumulated context."
            ),
        )
    )

    baseline, comparison = _with_change(
        {
            "other_prompt_tokens": 31_000,
            "visible_tool_schema_tokens": 19_000,
            "model_calls": 10,
            "output_tokens_per_call": 500,
        },
        "visible_tool_schema_tokens",
        20_000,
    )
    plans.append(
        ContrastPlan(
            contrast_id="stable-tool-schema-10-calls",
            study_family="tool_schema",
            changed_parameter="visible_tool_schema_tokens",
            baseline_parameters=baseline,
            comparison_parameters=comparison,
            builder=_build_schema,
            interpretation=(
                "Marginal 1,000 stable tokens in visible tool definitions over "
                "ten model calls."
            ),
        )
    )

    baseline, comparison = _with_change(
        {
            "prompt_tokens": 50_000,
            "model_calls": 1,
            "output_tokens_per_call": 500,
        },
        "output_tokens_per_call",
        1_500,
    )
    plans.append(
        ContrastPlan(
            contrast_id="output-1k-one-call",
            study_family="output",
            changed_parameter="output_tokens_per_call",
            baseline_parameters=baseline,
            comparison_parameters=comparison,
            builder=_build_output,
            interpretation="Marginal 1,000 output tokens in one cold model call.",
        )
    )

    baseline, comparison = _with_change(
        {
            "tool_count": 4,
            "execution_mode": "sequential",
            "initial_prompt_tokens": 50_000,
            "tool_argument_tokens": 100,
            "tool_result_tokens": 2_000,
            "retain_tool_results": False,
            "final_output_tokens": 500,
        },
        "retain_tool_results",
        True,
    )
    plans.append(
        ContrastPlan(
            contrast_id="retain-tool-results-4-tools",
            study_family="tool_results",
            changed_parameter="retain_tool_results",
            baseline_parameters=baseline,
            comparison_parameters=comparison,
            builder=_build_tools,
            interpretation=(
                "Cost of injecting and retaining four 2,000-token tool results. "
                "The tools still execute in both arms."
            ),
        )
    )

    baseline, comparison = _with_change(
        {
            "tool_count": 4,
            "execution_mode": "sequential",
            "initial_prompt_tokens": 50_000,
            "tool_argument_tokens": 100,
            "tool_result_tokens": 2_000,
            "retain_tool_results": True,
            "final_output_tokens": 500,
        },
        "tool_result_tokens",
        3_000,
    )
    plans.append(
        ContrastPlan(
            contrast_id="tool-result-size-plus-1k",
            study_family="tool_results",
            changed_parameter="tool_result_tokens",
            baseline_parameters=baseline,
            comparison_parameters=comparison,
            builder=_build_tools,
            interpretation=(
                "Marginal 1,000 tokens in each of four retained sequential tool "
                "results."
            ),
        )
    )

    baseline, comparison = _with_change(
        {
            "tool_count": 4,
            "execution_mode": "sequential",
            "initial_prompt_tokens": 50_000,
            "tool_argument_tokens": 100,
            "tool_result_tokens": 2_000,
            "retain_tool_results": True,
            "final_output_tokens": 500,
        },
        "tool_result_tokens",
        10_000,
    )
    plans.append(
        ContrastPlan(
            contrast_id="tool-result-2k-vs-10k-sequential-4",
            study_family="tool_results",
            changed_parameter="tool_result_tokens",
            baseline_parameters=baseline,
            comparison_parameters=comparison,
            builder=_build_tools,
            interpretation=(
                "Stress comparison between 2,000- and 10,000-token retained "
                "results for each of four sequential tools."
            ),
        )
    )

    baseline, comparison = _with_change(
        {
            "prompt_tokens": 50_000,
            "model_calls": 10,
            "output_tokens_per_call": 500,
            "prefix_churn": False,
        },
        "prefix_churn",
        True,
    )
    plans.append(
        ContrastPlan(
            contrast_id="prefix-churn-10-calls",
            study_family="cache_policy",
            changed_parameter="prefix_churn",
            baseline_parameters=baseline,
            comparison_parameters=comparison,
            builder=_build_prefix_churn,
            interpretation=(
                "Cost of invalidating a 50,000-token prefix on every call rather "
                "than writing it once and reading it nine times."
            ),
        )
    )

    baseline, comparison = _with_change(
        {
            "prompt_tokens": 50_000,
            "model_calls": 10,
            "output_tokens_per_call": 500,
        },
        "model_calls",
        11,
    )
    plans.append(
        ContrastPlan(
            contrast_id="extra-roundtrip-10-to-11",
            study_family="roundtrips",
            changed_parameter="model_calls",
            baseline_parameters=baseline,
            comparison_parameters=comparison,
            builder=_build_extra_roundtrip,
            interpretation=(
                "One extra warm model roundtrip with a 50,000-token cached "
                "prompt and 500 output tokens."
            ),
        )
    )

    long_common: dict[str, Any] = {
        "main_calls": 39,
        "initial_prompt_tokens": 40_000,
        "growth_tokens_per_call": 20_000,
        "main_output_tokens": 1_000,
        "compaction_strategy": "none",
        "compaction_input_mode": "uncached",
        "post_compaction_cache_mode": "cold_write",
        "summary_tokens": 20_000,
        "retained_system_tokens": 20_000,
    }
    for strategy, slug in (
        ("cap_200k", "long-cap-200k-uncached"),
        ("cap_pricing_threshold", "long-cap-pricing-threshold-uncached"),
    ):
        baseline, comparison = _with_change(
            long_common, "compaction_strategy", strategy
        )
        plans.append(
            ContrastPlan(
                contrast_id=slug,
                study_family="long_session",
                changed_parameter="compaction_strategy",
                baseline_parameters=baseline,
                comparison_parameters=comparison,
                builder=_build_long_session,
                interpretation=(
                    "Same 39 main calls and logical 40k-to-800k workload; the "
                    "comparison compacts before the configured cap, pays an "
                    "uncached summary call, and cold-writes a 40k post-compaction "
                    "prompt."
                ),
            )
        )

    compact_common = dict(long_common)
    compact_common["compaction_strategy"] = "cap_200k"
    for mode in ("cache_read", "cache_write"):
        baseline, comparison = _with_change(
            compact_common, "compaction_input_mode", mode
        )
        plans.append(
            ContrastPlan(
                contrast_id=f"compaction-input-{mode.replace('_', '-')}-sensitivity",
                study_family="compaction_sensitivity",
                changed_parameter="compaction_input_mode",
                baseline_parameters=baseline,
                comparison_parameters=comparison,
                builder=_build_long_session,
                interpretation=(
                    "Sensitivity of the 200k-cap strategy to whether the "
                    f"compaction request is billed as {mode.replace('_', ' ')} "
                    "instead of uncached input."
                ),
            )
        )

    baseline, comparison = _with_change(
        compact_common,
        "post_compaction_cache_mode",
        "retain_system_prefix",
    )
    plans.append(
        ContrastPlan(
            contrast_id="compaction-retained-system-sensitivity",
            study_family="compaction_sensitivity",
            changed_parameter="post_compaction_cache_mode",
            baseline_parameters=baseline,
            comparison_parameters=comparison,
            builder=_build_long_session,
            interpretation=(
                "Sensitivity when a 20,000-token stable system prefix survives "
                "each compaction instead of the full 40,000-token reset prompt "
                "being cold-written."
            ),
        )
    )

    for plan in plans:
        plan.validate_ofat()
    return tuple(plans)


def _simulate_scenario(
    plan: ContrastPlan,
    model_rate: ModelRate,
    *,
    role: str,
    parameters: dict[str, Any],
) -> ScenarioSimulation:
    build = plan.builder(model_rate, parameters)
    scenario_id = f"{plan.contrast_id}-{model_rate.model}-{role}"
    ledger = tuple(
        price_call(
            spec,
            model_rate,
            contrast_id=plan.contrast_id,
            scenario_id=scenario_id,
            role=role,
            call_index=index,
        )
        for index, spec in enumerate(build.calls, start=1)
    )
    return ScenarioSimulation(
        contrast_id=plan.contrast_id,
        study_family=plan.study_family,
        scenario_id=scenario_id,
        role=role,
        model=model_rate.model,
        changed_parameter=plan.changed_parameter,
        changed_value=parameters[plan.changed_parameter],
        parameters=dict(parameters),
        interpretation=plan.interpretation,
        build=build,
        ledger=ledger,
    )


def _sum_ledger(ledger: Sequence[PricedCall], field: str) -> int | float:
    return sum(getattr(row, field) for row in ledger)


def aggregate_scenario(simulation: ScenarioSimulation) -> dict[str, Any]:
    """Aggregate one scenario without losing its exact parameter mapping."""

    ledger = simulation.ledger
    provider_cost = _round_metric(float(_sum_ledger(ledger, "provider_cost_usd")))
    return {
        "contrast_id": simulation.contrast_id,
        "study_family": simulation.study_family,
        "scenario_id": simulation.scenario_id,
        "role": simulation.role,
        "model": simulation.model,
        "changed_parameter": simulation.changed_parameter,
        "changed_value": simulation.changed_value,
        "provider_cost_usd": provider_cost,
        "ai_credits": _round_metric(provider_cost / AI_CREDIT_USD),
        "call_count": len(ledger),
        "main_call_count": simulation.build.main_call_count,
        "tool_calls": simulation.build.tool_calls,
        "compactions": sum(1 for row in ledger if row.compaction_event),
        "long_context_calls": sum(1 for row in ledger if row.pricing_tier == "long"),
        "max_input_tokens": max((row.full_input_tokens for row in ledger), default=0),
        "input_uncached_tokens": int(_sum_ledger(ledger, "input_uncached_tokens")),
        "cache_read_tokens": int(_sum_ledger(ledger, "cache_read_tokens")),
        "cache_write_tokens": int(_sum_ledger(ledger, "cache_write_tokens")),
        "output_tokens": int(_sum_ledger(ledger, "output_tokens")),
        "input_uncached_cost_usd": _round_metric(
            float(_sum_ledger(ledger, "input_uncached_cost_usd"))
        ),
        "cache_read_cost_usd": _round_metric(
            float(_sum_ledger(ledger, "cache_read_cost_usd"))
        ),
        "cache_write_cost_usd": _round_metric(
            float(_sum_ledger(ledger, "cache_write_cost_usd"))
        ),
        "output_cost_usd": _round_metric(float(_sum_ledger(ledger, "output_cost_usd"))),
        "discarded_context_tokens": int(
            _sum_ledger(ledger, "discarded_context_tokens")
        ),
        "tool_result_tokens_generated": simulation.build.tool_result_tokens_generated,
        "tool_result_tokens_injected": simulation.build.tool_result_tokens_injected,
        "parameters_json": json.dumps(
            simulation.parameters, sort_keys=True, separators=(",", ":")
        ),
        "interpretation": simulation.interpretation,
    }


def _numeric_change(left: Any, right: Any) -> tuple[float | None, float | None]:
    if isinstance(left, bool) or isinstance(right, bool):
        return None, None
    if not isinstance(left, (int, float)) or not isinstance(right, (int, float)):
        return None, None
    delta = float(right) - float(left)
    percent = delta / float(left) * 100.0 if float(left) != 0 else None
    return delta, percent


def aggregate_contrast(
    baseline: dict[str, Any], comparison: dict[str, Any]
) -> dict[str, Any]:
    """Calculate cost deltas and elasticity for an OFAT pair."""

    baseline_cost = float(baseline["provider_cost_usd"])
    comparison_cost = float(comparison["provider_cost_usd"])
    cost_delta = _round_metric(comparison_cost - baseline_cost)
    cost_pct = (
        _round_metric(cost_delta / baseline_cost * 100.0) if baseline_cost else None
    )
    parameter_delta, parameter_pct = _numeric_change(
        baseline["changed_value"], comparison["changed_value"]
    )
    elasticity = (
        _round_metric(cost_pct / parameter_pct)
        if cost_pct is not None and parameter_pct not in (None, 0.0)
        else None
    )
    if math.isclose(cost_delta, 0.0, abs_tol=1e-15):
        cheaper_role = "tie"
    else:
        cheaper_role = "baseline" if cost_delta > 0 else "comparison"
    return {
        "contrast_id": baseline["contrast_id"],
        "study_family": baseline["study_family"],
        "model": baseline["model"],
        "changed_parameter": baseline["changed_parameter"],
        "baseline_scenario_id": baseline["scenario_id"],
        "comparison_scenario_id": comparison["scenario_id"],
        "baseline_value": baseline["changed_value"],
        "comparison_value": comparison["changed_value"],
        "parameter_delta": parameter_delta,
        "parameter_change_pct": parameter_pct,
        "baseline_provider_cost_usd": baseline_cost,
        "comparison_provider_cost_usd": comparison_cost,
        "cost_delta_usd": cost_delta,
        "savings_usd": _round_metric(baseline_cost - comparison_cost),
        "cost_change_pct": cost_pct,
        "point_elasticity": elasticity,
        "baseline_ai_credits": baseline["ai_credits"],
        "comparison_ai_credits": comparison["ai_credits"],
        "ai_credit_delta": _round_metric(
            comparison["ai_credits"] - baseline["ai_credits"]
        ),
        "call_count_delta": comparison["call_count"] - baseline["call_count"],
        "tool_call_delta": comparison["tool_calls"] - baseline["tool_calls"],
        "compaction_delta": comparison["compactions"] - baseline["compactions"],
        "long_context_call_delta": (
            comparison["long_context_calls"] - baseline["long_context_calls"]
        ),
        "input_uncached_token_delta": (
            comparison["input_uncached_tokens"] - baseline["input_uncached_tokens"]
        ),
        "cache_read_token_delta": (
            comparison["cache_read_tokens"] - baseline["cache_read_tokens"]
        ),
        "cache_write_token_delta": (
            comparison["cache_write_tokens"] - baseline["cache_write_tokens"]
        ),
        "output_token_delta": comparison["output_tokens"] - baseline["output_tokens"],
        "cheaper_role": cheaper_role,
        "baseline_parameters_json": baseline["parameters_json"],
        "comparison_parameters_json": comparison["parameters_json"],
        "interpretation": baseline["interpretation"],
    }


def _validate_volumes(volumes: Iterable[int]) -> tuple[int, ...]:
    normalized = tuple(int(volume) for volume in volumes)
    if not normalized:
        raise ValueError("at least one scale volume is required")
    if any(volume <= 0 for volume in normalized):
        raise ValueError("scale volumes must be positive integers")
    if len(set(normalized)) != len(normalized):
        raise ValueError("scale volumes must be unique")
    return normalized


def simulate_all(
    *,
    volumes: Iterable[int] = (1_000, 1_000_000),
    models: Iterable[str] = ("luna", "terra", "sol"),
) -> SimulationBundle:
    """Run the complete deterministic portfolio entirely in memory."""

    volume_values = _validate_volumes(volumes)
    model_names = tuple(models)
    if not model_names or any(name not in RATE_CARD for name in model_names):
        raise ValueError(f"models must be drawn from {tuple(RATE_CARD)}")
    if len(set(model_names)) != len(model_names):
        raise ValueError("models must be unique")

    scenario_rows: list[dict[str, Any]] = []
    ledger_rows: list[dict[str, Any]] = []
    contrast_rows: list[dict[str, Any]] = []

    for plan in build_contrast_plans():
        plan.validate_ofat()
        for model_name in model_names:
            rate = RATE_CARD[model_name]
            baseline_sim = _simulate_scenario(
                plan,
                rate,
                role="baseline",
                parameters=plan.baseline_parameters,
            )
            comparison_sim = _simulate_scenario(
                plan,
                rate,
                role="comparison",
                parameters=plan.comparison_parameters,
            )
            baseline_row = aggregate_scenario(baseline_sim)
            comparison_row = aggregate_scenario(comparison_sim)
            scenario_rows.extend((baseline_row, comparison_row))
            ledger_rows.extend(asdict(row) for row in baseline_sim.ledger)
            ledger_rows.extend(asdict(row) for row in comparison_sim.ledger)
            contrast_rows.append(aggregate_contrast(baseline_row, comparison_row))

    scale_rows: list[dict[str, Any]] = []
    for contrast in contrast_rows:
        for volume in volume_values:
            baseline_cost = _round_metric(
                contrast["baseline_provider_cost_usd"] * volume
            )
            comparison_cost = _round_metric(
                contrast["comparison_provider_cost_usd"] * volume
            )
            scale_rows.append(
                {
                    "contrast_id": contrast["contrast_id"],
                    "study_family": contrast["study_family"],
                    "model": contrast["model"],
                    "volume_executions": volume,
                    "baseline_provider_cost_usd": baseline_cost,
                    "comparison_provider_cost_usd": comparison_cost,
                    "cost_delta_usd": _round_metric(comparison_cost - baseline_cost),
                    "savings_usd": _round_metric(baseline_cost - comparison_cost),
                    "baseline_ai_credits": _round_metric(baseline_cost / AI_CREDIT_USD),
                    "comparison_ai_credits": _round_metric(
                        comparison_cost / AI_CREDIT_USD
                    ),
                    "ai_credit_delta": _round_metric(
                        (comparison_cost - baseline_cost) / AI_CREDIT_USD
                    ),
                }
            )

    scenario_lookup = {row["scenario_id"]: row for row in scenario_rows}
    break_even_rows: list[dict[str, Any]] = []
    for contrast in contrast_rows:
        if contrast["study_family"] != "long_session":
            continue
        comparison = scenario_lookup[contrast["comparison_scenario_id"]]
        savings = max(float(contrast["savings_usd"]), 0.0)
        compactions = int(comparison["compactions"])
        for failure_loss in (10.0, 50.0, 100.0, 500.0, 1_000.0):
            raw_probability = _round_metric(savings / failure_loss)
            per_compaction_probability = (
                _round_metric(savings / (compactions * failure_loss))
                if compactions
                else None
            )
            break_even_rows.append(
                {
                    "contrast_id": contrast["contrast_id"],
                    "model": contrast["model"],
                    "compactions_per_execution": compactions,
                    "provider_savings_usd_per_execution": float(
                        contrast["savings_usd"]
                    ),
                    "quality_loss_budget_usd_per_execution": savings,
                    "quality_loss_budget_usd_per_compaction": (
                        _round_metric(savings / compactions) if compactions else None
                    ),
                    "failure_loss_usd": failure_loss,
                    "break_even_incremental_failure_probability": raw_probability,
                    "break_even_incremental_failure_probability_capped": min(
                        raw_probability, 1.0
                    ),
                    "break_even_failure_probability_per_compaction_independent": (
                        per_compaction_probability
                    ),
                }
            )

    return SimulationBundle(
        scenarios=tuple(scenario_rows),
        ledger=tuple(ledger_rows),
        contrasts=tuple(contrast_rows),
        scale_results=tuple(scale_rows),
        break_even=tuple(break_even_rows),
        volumes=volume_values,
    )


def rate_card_as_dict() -> dict[str, Any]:
    """Serialize the embedded rate card with provenance."""

    return {
        name: {
            "long_context_threshold_tokens": rate.long_context_threshold_tokens,
            "short": asdict(rate.short),
            "long": asdict(rate.long),
        }
        for name, rate in RATE_CARD.items()
    }


def bundle_as_dict(bundle: SimulationBundle) -> dict[str, Any]:
    """Return the complete JSON-ready study object."""

    return {
        "model_version": MODEL_VERSION,
        "provenance": {
            "execution_mode": "deterministic-offline-simulation",
            "real_pi_or_copilot_calls": False,
            "provider_route": "Pi through GitHub Copilot, fixed manual model",
            "rate_source_url": RATE_SOURCE_URL,
            "rate_card_capture_date": "2026-09-04",
            "automatic_model_discount_applied": False,
            "ai_credit_usd": AI_CREDIT_USD,
            "context_availability_caveat": (
                "The 800k prompt path is a conditional cost simulation. It does "
                "not assert that every Pi-through-Copilot client can submit an "
                "800k request."
            ),
        },
        "rate_card": rate_card_as_dict(),
        "volumes": list(bundle.volumes),
        "scenarios": list(bundle.scenarios),
        "contrasts": list(bundle.contrasts),
        "scale_results": list(bundle.scale_results),
        "break_even": list(bundle.break_even),
    }


CSV_FILES: tuple[tuple[str, str], ...] = (
    ("call-ledger.csv", "ledger"),
    ("scenario-results.csv", "scenarios"),
    ("contrast-results.csv", "contrasts"),
    ("scale-results.csv", "scale_results"),
    ("break-even.csv", "break_even"),
)


def _write_csv(path: Path, rows: Sequence[dict[str, Any]]) -> None:
    if not rows:
        raise ValueError(f"cannot write empty CSV: {path.name}")
    fieldnames = list(rows[0])
    for row in rows:
        if list(row) != fieldnames:
            raise ValueError(f"inconsistent columns while writing {path.name}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def _write_text_lf(path: Path, content: str) -> None:
    """Write deterministic UTF-8 text without platform newline translation."""

    with path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(content)


def _data_dictionary(bundle: SimulationBundle) -> dict[str, Any]:
    return {
        "model_version": MODEL_VERSION,
        "grain": {
            "call-ledger.csv": "one hypothetical provider request",
            "scenario-results.csv": "one scenario arm and model",
            "contrast-results.csv": "one OFAT contrast and model",
            "scale-results.csv": "one contrast, model, and algebraic volume",
            "break-even.csv": "one long-session contrast, model, and failure-loss value",
        },
        "billing_partition_invariant": (
            "full_input_tokens = input_uncached_tokens + cache_read_tokens + "
            "cache_write_tokens; the three buckets are mutually exclusive"
        ),
        "pricing_tier_rule": (
            "short when full_input_tokens <= model threshold; long otherwise; "
            "the selected tier prices the entire request"
        ),
        "cost_formula": ("sum(tokens_in_bucket * tier_rate_per_million / 1,000,000)"),
        "ai_credit_formula": "provider_cost_usd / 0.01",
        "scale_rule": (
            "per-execution deterministic result multiplied by volume; no rows "
            "are materialized per execution"
        ),
        "break_even_probability_units": {
            "break_even_incremental_failure_probability": (
                "savings per execution divided by loss per degraded execution"
            ),
            "break_even_failure_probability_per_compaction_independent": (
                "savings per execution divided by compactions per execution and "
                "loss per independently degraded compaction"
            ),
        },
        "row_counts": {
            "ledger": len(bundle.ledger),
            "scenarios": len(bundle.scenarios),
            "contrasts": len(bundle.contrasts),
            "scale_results": len(bundle.scale_results),
            "break_even": len(bundle.break_even),
        },
    }


def _explore_sql() -> str:
    return """-- DuckDB exploration queries for the deterministic Pi cost study.
-- Run from the bundle directory. No network access or provider calls are needed.

CREATE OR REPLACE VIEW calls AS
SELECT * FROM read_csv_auto('call-ledger.csv', header = true);

CREATE OR REPLACE VIEW scenarios AS
SELECT * FROM read_csv_auto('scenario-results.csv', header = true);

CREATE OR REPLACE VIEW contrasts AS
SELECT * FROM read_csv_auto('contrast-results.csv', header = true);

CREATE OR REPLACE VIEW scaled AS
SELECT * FROM read_csv_auto('scale-results.csv', header = true);

-- Highest monthly deltas at one million hypothetical executions.
SELECT contrast_id, model, cost_delta_usd, savings_usd
FROM scaled
WHERE volume_executions = 1000000
ORDER BY abs(cost_delta_usd) DESC;

-- Verify the mutually exclusive input-token partition.
SELECT count(*) AS invalid_rows
FROM calls
WHERE full_input_tokens !=
      input_uncached_tokens + cache_read_tokens + cache_write_tokens;

-- Show the pricing discontinuity around each model-specific threshold.
SELECT contrast_id, role, model, max_input_tokens, long_context_calls,
       provider_cost_usd
FROM scenarios
WHERE contrast_id LIKE 'system-threshold-%'
ORDER BY contrast_id, model, role;

-- Compare sequential and batched marginal fifth-tool costs.
SELECT contrast_id, model, cost_delta_usd, call_count_delta,
       cache_read_token_delta, cache_write_token_delta
FROM contrasts
WHERE contrast_id IN ('sequential-tools-4-to-5', 'batched-tools-4-to-5')
ORDER BY model, contrast_id;

-- Long-session economics and maximum tolerable quality loss.
SELECT c.contrast_id, c.model, c.baseline_provider_cost_usd,
       c.comparison_provider_cost_usd, c.savings_usd,
       b.quality_loss_budget_usd_per_compaction
FROM contrasts c
JOIN read_csv_auto('break-even.csv', header = true) b
  USING (contrast_id, model)
WHERE b.failure_loss_usd = 100
ORDER BY c.contrast_id, c.model;
"""


def _find_contrast(
    bundle: SimulationBundle, contrast_id: str, model: str
) -> dict[str, Any]:
    for row in bundle.contrasts:
        if row["contrast_id"] == contrast_id and row["model"] == model:
            return row
    raise KeyError((contrast_id, model))


def _summary_markdown(bundle: SimulationBundle) -> str:
    included_models = tuple(
        name
        for name in RATE_CARD
        if any(row["model"] == name for row in bundle.contrasts)
    )
    lines = [
        "# Deterministic Pi cost-elasticity simulation",
        "",
        (
            "This bundle is an offline arithmetic simulation. It made **zero real "
            "Pi, Copilot, or model API calls**. Provider costs are token-list-price "
            "value; they are not necessarily incremental cash on a prepaid plan."
        ),
        "",
        "## Canonical one-million-execution deltas",
        "",
        "| Contrast | " + " | ".join(name.title() for name in included_models) + " |",
        "|---|" + "---:|" * len(included_models),
    ]
    for contrast_id, label in (
        ("stable-system-10-calls", "+1k stable system tokens, 10 calls"),
        ("dynamic-system-10-calls", "+1k uncached system tokens, 10 calls"),
        ("system-threshold-cold", "+1k crossing threshold, cold"),
        ("sequential-tools-4-to-5", "fifth sequential tool"),
        ("batched-tools-4-to-5", "fifth batched tool"),
        ("prefix-churn-10-calls", "prefix churn, 10 calls"),
    ):
        values = []
        for model_name in included_models:
            row = _find_contrast(bundle, contrast_id, model_name)
            values.append(f"${row['cost_delta_usd'] * 1_000_000:,.2f}")
        lines.append(f"| {label} | " + " | ".join(values) + " |")

    lines.extend(
        [
            "",
            "## Long-session strategies",
            "",
            (
                "The fixed workload has 39 main calls and grows logically from a "
                "40k prompt to 800k without compaction. The 200k strategy inserts "
                "an uncached summary call and cold-writes a 40k prompt after every "
                "compaction. It therefore includes the cost of cache loss rather "
                "than assuming compaction is free."
            ),
            "",
            "| Model | No compaction / execution | Cap 200k / execution | Savings / execution | Compactions |",
            "|---|---:|---:|---:|---:|",
        ]
    )
    scenario_lookup = {row["scenario_id"]: row for row in bundle.scenarios}
    for model_name in included_models:
        row = _find_contrast(bundle, "long-cap-200k-uncached", model_name)
        comparison = scenario_lookup[row["comparison_scenario_id"]]
        lines.append(
            f"| {model_name.title()} | ${row['baseline_provider_cost_usd']:,.6f} | "
            f"${row['comparison_provider_cost_usd']:,.6f} | "
            f"${row['savings_usd']:,.6f} | {comparison['compactions']} |"
        )

    lines.extend(
        [
            "",
            "## Interpretation boundaries",
            "",
            "- Luna uses the GitHub Copilot 200k boundary; Terra and Sol use 272k.",
            (
                "- The 800k path is conditional cost arithmetic, not a claim that "
                "every Pi/Copilot integration accepts an 800k prompt."
            ),
            "- Fixed-model Pi routing receives no assumed automatic-model discount.",
            (
                "- Compaction can lose useful information. `break-even.csv` "
                "converts provider savings into both a per-execution failure "
                "threshold and an independent per-compaction failure threshold."
            ),
            (
                "- `scale-results.csv` multiplies one deterministic execution by "
                "1,000 and 1,000,000; it does not fabricate one million "
                "observations."
            ),
            "",
            f"Rate source: {RATE_SOURCE_URL}",
            "",
        ]
    )
    return "\n".join(lines)


def write_bundle(output_dir: str | Path, bundle: SimulationBundle) -> dict[str, Any]:
    """Write deterministic CSV/JSON/SQL/Markdown artifacts to ``output_dir``."""

    target = Path(output_dir).resolve()
    target.mkdir(parents=True, exist_ok=True)

    for filename, attribute in CSV_FILES:
        rows = getattr(bundle, attribute)
        _write_csv(target / filename, rows)

    study_payload = bundle_as_dict(bundle)
    _write_text_lf(
        target / "study-results.json",
        json.dumps(study_payload, indent=2, sort_keys=True) + "\n",
    )
    _write_text_lf(
        target / "data-dictionary.json",
        json.dumps(_data_dictionary(bundle), indent=2, sort_keys=True) + "\n",
    )
    _write_text_lf(target / "explore.sql", _explore_sql())
    _write_text_lf(target / "summary.md", _summary_markdown(bundle))

    artifact_names = [filename for filename, _ in CSV_FILES] + [
        "study-results.json",
        "data-dictionary.json",
        "explore.sql",
        "summary.md",
    ]
    digests = {
        name: hashlib.sha256((target / name).read_bytes()).hexdigest()
        for name in artifact_names
    }
    manifest = {
        "model_version": MODEL_VERSION,
        "execution_mode": "deterministic-offline-simulation",
        "real_pi_or_copilot_calls": False,
        "volumes": list(bundle.volumes),
        "row_counts": {
            "ledger": len(bundle.ledger),
            "scenarios": len(bundle.scenarios),
            "contrasts": len(bundle.contrasts),
            "scale_results": len(bundle.scale_results),
            "break_even": len(bundle.break_even),
        },
        "sha256": digests,
    }
    _write_text_lf(
        target / "manifest.json",
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
    )
    return manifest


__all__ = [
    "AI_CREDIT_USD",
    "MODEL_VERSION",
    "RATE_CARD",
    "RATE_SOURCE_URL",
    "CallSpec",
    "ContrastPlan",
    "ModelRate",
    "PricedCall",
    "ScenarioBuild",
    "SimulationBundle",
    "TierRate",
    "aggregate_contrast",
    "aggregate_scenario",
    "build_contrast_plans",
    "bundle_as_dict",
    "price_call",
    "rate_card_as_dict",
    "simulate_all",
    "write_bundle",
]
