#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Independently audit a deterministic Pi-through-Copilot cost bundle.

This validator intentionally does not import the simulator. It reconstructs every
cost from the exported call ledger with hard-coded, dated rate-card expectations,
then reconciles scenario, contrast, and scale tables. It performs no network or
model calls.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import defaultdict
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

MILLION = Decimal(1000000)
AI_CREDIT_USD = Decimal("0.01")
ABS_TOL = Decimal("0.0000000001")
REL_TOL = Decimal("0.00000001")

# GitHub Copilot list prices captured for the 2026-09-04 study. The Luna
# threshold deliberately differs from the direct OpenAI API threshold.
EXPECTED_RATE_CARD: dict[str, dict[str, Any]] = {
    "luna": {
        "threshold": 200_000,
        "short": {
            "uncached": Decimal("0.20"),
            "read": Decimal("0.02"),
            "write": Decimal("0.25"),
            "output": Decimal("1.20"),
        },
        "long": {
            "uncached": Decimal("0.40"),
            "read": Decimal("0.04"),
            "write": Decimal("0.50"),
            "output": Decimal("1.80"),
        },
    },
    "terra": {
        "threshold": 272_000,
        "short": {
            "uncached": Decimal("2.00"),
            "read": Decimal("0.20"),
            "write": Decimal("2.50"),
            "output": Decimal("12.00"),
        },
        "long": {
            "uncached": Decimal("4.00"),
            "read": Decimal("0.40"),
            "write": Decimal("5.00"),
            "output": Decimal("18.00"),
        },
    },
    "sol": {
        "threshold": 272_000,
        "short": {
            "uncached": Decimal("4.00"),
            "read": Decimal("0.40"),
            "write": Decimal("5.00"),
            "output": Decimal("20.00"),
        },
        "long": {
            "uncached": Decimal("8.00"),
            "read": Decimal("0.80"),
            "write": Decimal("10.00"),
            "output": Decimal("30.00"),
        },
    },
}

REQUIRED_FILES = (
    "call-ledger.csv",
    "scenario-results.csv",
    "contrast-results.csv",
    "scale-results.csv",
    "study-results.json",
)


@dataclass
class Audit:
    """Collect compact, actionable validation results."""

    checks: int = 0
    failures: list[dict[str, Any]] = field(default_factory=list)
    warnings: list[dict[str, Any]] = field(default_factory=list)

    def check(
        self,
        condition: bool,
        code: str,
        message: str,
        **context: Any,
    ) -> bool:
        self.checks += 1
        if not condition:
            item: dict[str, Any] = {"code": code, "message": message}
            if context:
                item["context"] = _json_safe(context)
            self.failures.append(item)
        return condition

    def warn(self, code: str, message: str, **context: Any) -> None:
        item: dict[str, Any] = {"code": code, "message": message}
        if context:
            item["context"] = _json_safe(context)
        self.warnings.append(item)

    def report(self, bundle: Path) -> dict[str, Any]:
        return {
            "schema_version": "1.0",
            "validator": "independent-pi-cost-elasticity-audit",
            "mode": "offline_deterministic_validation",
            "bundle": str(bundle.resolve()),
            "status": "pass" if not self.failures else "fail",
            "checks": self.checks,
            "failure_count": len(self.failures),
            "warning_count": len(self.warnings),
            "failures": self.failures,
            "warnings": self.warnings,
            "rate_card_oracle": _json_safe(EXPECTED_RATE_CARD),
        }


def _json_safe(value: Any) -> Any:
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, Mapping):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(item) for item in value]
    return value


def _read_csv(path: Path, audit: Audit) -> list[dict[str, str]]:
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            audit.check(
                bool(reader.fieldnames),
                "csv.missing_header",
                "CSV must contain a header row.",
                path=path,
            )
            rows = list(reader)
    except (OSError, csv.Error) as exc:
        audit.check(
            False, "csv.read_error", "Could not read CSV.", path=path, error=str(exc)
        )
        return []
    audit.check(
        bool(rows), "csv.empty", "CSV must contain at least one data row.", path=path
    )
    return rows


def _read_json(path: Path, audit: Audit) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        audit.check(
            False,
            "json.read_error",
            "Could not read valid JSON.",
            path=path,
            error=str(exc),
        )
        return {}


def _text(row: Mapping[str, Any], *names: str, default: str = "") -> str:
    for name in names:
        value = row.get(name)
        if value is not None and str(value).strip() != "":
            return str(value).strip()
    return default


def _dec(
    row: Mapping[str, Any],
    *names: str,
    default: Decimal | None = None,
) -> Decimal | None:
    value = _text(row, *names)
    if not value:
        return default
    try:
        return Decimal(value)
    except InvalidOperation:
        return None


def _int(row: Mapping[str, Any], *names: str, default: int | None = None) -> int | None:
    value = _dec(row, *names)
    if value is None:
        return default
    if value != value.to_integral_value():
        return None
    return int(value)


def _truthy(value: Any) -> bool:
    return str(value).strip().lower() in {"1", "true", "yes", "y", "on"}


def _close(left: Decimal | None, right: Decimal | None) -> bool:
    if left is None or right is None:
        return False
    difference = abs(left - right)
    return difference <= max(ABS_TOL, REL_TOL * max(abs(left), abs(right)))


def _canonical_model(value: str) -> str | None:
    lowered = value.strip().lower()
    for model in EXPECTED_RATE_CARD:
        if model in lowered:
            return model
    return None


def _tier_for(model: str, full_input_tokens: int) -> str:
    # The threshold itself remains in the short tier; only requests above it
    # receive long-context pricing.
    return (
        "long"
        if full_input_tokens > EXPECTED_RATE_CARD[model]["threshold"]
        else "short"
    )


def _scenario_key(row: Mapping[str, Any]) -> tuple[str, str, str, str]:
    return (
        _text(row, "contrast_id"),
        _text(row, "scenario_id"),
        _text(row, "role").lower(),
        _canonical_model(_text(row, "model")) or _text(row, "model").lower(),
    )


def _row_context(row: Mapping[str, Any]) -> dict[str, str]:
    return {
        "contrast_id": _text(row, "contrast_id"),
        "scenario_id": _text(row, "scenario_id"),
        "role": _text(row, "role"),
        "model": _text(row, "model"),
        "call_index": _text(row, "call_index"),
    }


def _flatten(value: Any, prefix: str = "") -> dict[str, Any]:
    flattened: dict[str, Any] = {}
    if isinstance(value, Mapping):
        for key in sorted(value):
            child = f"{prefix}.{key}" if prefix else str(key)
            flattened.update(_flatten(value[key], child))
    elif isinstance(value, list):
        flattened[prefix] = value
    else:
        flattened[prefix] = value
    return flattened


def _parse_object(value: Any) -> dict[str, Any] | None:
    if isinstance(value, Mapping):
        return dict(value)
    if isinstance(value, str) and value.strip():
        try:
            parsed = json.loads(value)
        except json.JSONDecodeError:
            return None
        if isinstance(parsed, Mapping):
            return dict(parsed)
    return None


def _parameter_matches_path(parameter: str, path: str) -> bool:
    normalized_parameter = parameter.strip().lower().replace("-", "_")
    normalized_path = path.strip().lower().replace("-", "_")
    leaf = normalized_path.rsplit(".", 1)[-1]
    return normalized_parameter in {normalized_path, leaf} or normalized_path.endswith(
        f".{normalized_parameter}"
    )


def _audit_ledger(
    ledger: Sequence[Mapping[str, str]],
    audit: Audit,
) -> dict[tuple[str, str, str, str], dict[str, Any]]:
    aggregates: dict[tuple[str, str, str, str], dict[str, Any]] = {}
    seen_calls: set[tuple[tuple[str, str, str, str], int]] = set()

    for row_number, row in enumerate(ledger, start=2):
        context = {**_row_context(row), "csv_row": row_number}
        key = _scenario_key(row)
        model = _canonical_model(_text(row, "model"))
        if not audit.check(
            model is not None,
            "ledger.unknown_model",
            "Every ledger row must use Luna, Terra, or Sol.",
            **context,
        ):
            continue

        token_fields = {
            "uncached": _int(row, "input_uncached_tokens", "uncached_input_tokens"),
            "read": _int(row, "cache_read_tokens", "cached_input_tokens"),
            "write": _int(row, "cache_write_tokens"),
            "full": _int(row, "full_input_tokens", "input_tokens"),
            "output": _int(row, "output_tokens"),
            "discarded": _int(row, "discarded_context_tokens", default=0),
        }
        for field_name, value in token_fields.items():
            audit.check(
                value is not None and value >= 0,
                "ledger.invalid_token_count",
                "Token counts must be non-negative integers.",
                field=field_name,
                value=value,
                **context,
            )
        if any(value is None for value in token_fields.values()):
            continue
        uncached = int(token_fields["uncached"])
        read = int(token_fields["read"])
        write = int(token_fields["write"])
        full = int(token_fields["full"])
        output = int(token_fields["output"])
        discarded = int(token_fields["discarded"])
        audit.check(
            full == uncached + read + write,
            "ledger.input_partition",
            "full_input_tokens must equal uncached + cache-read + cache-write tokens.",
            expected=uncached + read + write,
            observed=full,
            **context,
        )

        threshold = _int(row, "long_context_threshold_tokens")
        expected_threshold = int(EXPECTED_RATE_CARD[model]["threshold"])
        audit.check(
            threshold == expected_threshold,
            "ledger.threshold",
            "Ledger threshold does not match the Pi-through-Copilot rate-card oracle.",
            expected=expected_threshold,
            observed=threshold,
            **context,
        )
        expected_tier = _tier_for(model, full)
        observed_tier = _text(row, "pricing_tier", "tier").lower()
        audit.check(
            observed_tier == expected_tier,
            "ledger.pricing_tier",
            "Pricing tier must be derived from full input tokens; the threshold is inclusive-short.",
            expected=expected_tier,
            observed=observed_tier,
            full_input_tokens=full,
            **context,
        )

        expected_rates = EXPECTED_RATE_CARD[model][expected_tier]
        observed_rates = {
            "uncached": _dec(
                row, "input_rate_per_million", "uncached_input_rate_per_million"
            ),
            "read": _dec(row, "cache_read_rate_per_million"),
            "write": _dec(row, "cache_write_rate_per_million"),
            "output": _dec(row, "output_rate_per_million"),
        }
        for rate_name, expected_rate in expected_rates.items():
            audit.check(
                _close(observed_rates[rate_name], expected_rate),
                "ledger.rate",
                "Ledger rate must match the independent dated Copilot rate card.",
                rate=rate_name,
                expected=expected_rate,
                observed=observed_rates[rate_name],
                tier=expected_tier,
                **context,
            )

        expected_costs = {
            "uncached": Decimal(uncached) * expected_rates["uncached"] / MILLION,
            "read": Decimal(read) * expected_rates["read"] / MILLION,
            "write": Decimal(write) * expected_rates["write"] / MILLION,
            "output": Decimal(output) * expected_rates["output"] / MILLION,
        }
        observed_costs = {
            "uncached": _dec(row, "input_uncached_cost_usd", "uncached_input_cost_usd"),
            "read": _dec(row, "cache_read_cost_usd"),
            "write": _dec(row, "cache_write_cost_usd"),
            "output": _dec(row, "output_cost_usd"),
        }
        for cost_name, expected_cost in expected_costs.items():
            audit.check(
                _close(observed_costs[cost_name], expected_cost),
                "ledger.component_cost",
                "Token-class cost does not equal tokens × rate / 1,000,000.",
                component=cost_name,
                expected=expected_cost,
                observed=observed_costs[cost_name],
                **context,
            )
        expected_provider_cost = sum(expected_costs.values(), Decimal(0))
        observed_provider_cost = _dec(row, "provider_cost_usd", "total_cost_usd")
        audit.check(
            _close(observed_provider_cost, expected_provider_cost),
            "ledger.provider_cost",
            "provider_cost_usd must equal the independently recomputed component sum.",
            expected=expected_provider_cost,
            observed=observed_provider_cost,
            **context,
        )
        observed_credits = _dec(row, "ai_credits")
        audit.check(
            _close(observed_credits, expected_provider_cost / AI_CREDIT_USD),
            "ledger.ai_credits",
            "AI credits must be provider USD divided by $0.01.",
            expected=expected_provider_cost / AI_CREDIT_USD,
            observed=observed_credits,
            **context,
        )

        call_index = _int(row, "call_index")
        audit.check(
            call_index is not None and call_index >= 1,
            "ledger.call_index",
            "call_index must be a positive integer.",
            **context,
        )
        if call_index is not None:
            call_key = (key, call_index)
            audit.check(
                call_key not in seen_calls,
                "ledger.duplicate_call",
                "A scenario cannot contain the same call_index twice.",
                **context,
            )
            seen_calls.add(call_key)

        aggregate = aggregates.setdefault(
            key,
            {
                "call_count": 0,
                "main_call_count": 0,
                "compactions": 0,
                "long_context_calls": 0,
                "max_input_tokens": 0,
                "input_uncached_tokens": 0,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "output_tokens": 0,
                "discarded_context_tokens": 0,
                "input_uncached_cost_usd": Decimal(0),
                "cache_read_cost_usd": Decimal(0),
                "cache_write_cost_usd": Decimal(0),
                "output_cost_usd": Decimal(0),
                "provider_cost_usd": Decimal(0),
                "rows": [],
            },
        )
        aggregate["call_count"] += 1
        call_kind = _text(row, "call_kind").lower()
        is_compaction = (
            _truthy(row.get("compaction_event", "")) or "compact" in call_kind
        )
        if is_compaction:
            aggregate["compactions"] += 1
        else:
            # ScenarioBuild.main_call_count is the number of ordinary provider
            # requests, regardless of whether a builder labels them model_roundtrip,
            # tool_decision, tool_followup, or main_model_call.
            aggregate["main_call_count"] += 1
        if expected_tier == "long":
            aggregate["long_context_calls"] += 1
        aggregate["max_input_tokens"] = max(aggregate["max_input_tokens"], full)
        aggregate["input_uncached_tokens"] += uncached
        aggregate["cache_read_tokens"] += read
        aggregate["cache_write_tokens"] += write
        aggregate["output_tokens"] += output
        aggregate["discarded_context_tokens"] += discarded
        aggregate_cost_fields = {
            "uncached": "input_uncached_cost_usd",
            "read": "cache_read_cost_usd",
            "write": "cache_write_cost_usd",
            "output": "output_cost_usd",
        }
        for name, cost in expected_costs.items():
            aggregate[aggregate_cost_fields[name]] += cost
        aggregate["provider_cost_usd"] += expected_provider_cost
        aggregate["rows"].append(row)

    audit.check(
        bool(aggregates),
        "ledger.no_scenarios",
        "Ledger must yield at least one scenario.",
    )
    return aggregates


def _scenario_decimal(
    row: Mapping[str, Any],
    semantic_name: str,
) -> Decimal | None:
    aliases: dict[str, tuple[str, ...]] = {
        "input_uncached_tokens": (
            "input_uncached_tokens",
            "total_input_uncached_tokens",
        ),
        "cache_read_tokens": ("cache_read_tokens", "total_cache_read_tokens"),
        "cache_write_tokens": ("cache_write_tokens", "total_cache_write_tokens"),
        "output_tokens": ("output_tokens", "total_output_tokens"),
        "input_uncached_cost_usd": (
            "input_uncached_cost_usd",
            "total_input_uncached_cost_usd",
        ),
        "cache_read_cost_usd": ("cache_read_cost_usd", "total_cache_read_cost_usd"),
        "cache_write_cost_usd": ("cache_write_cost_usd", "total_cache_write_cost_usd"),
        "output_cost_usd": ("output_cost_usd", "total_output_cost_usd"),
    }
    return _dec(row, *aliases.get(semantic_name, (semantic_name,)))


def _audit_scenarios(
    scenarios: Sequence[Mapping[str, str]],
    aggregates: Mapping[tuple[str, str, str, str], Mapping[str, Any]],
    audit: Audit,
) -> dict[tuple[str, str, str, str], Mapping[str, str]]:
    scenario_map: dict[tuple[str, str, str, str], Mapping[str, str]] = {}
    for row_number, row in enumerate(scenarios, start=2):
        key = _scenario_key(row)
        context = {**_row_context(row), "csv_row": row_number}
        audit.check(
            key not in scenario_map,
            "scenario.duplicate",
            "Scenario summary key must be unique.",
            **context,
        )
        scenario_map[key] = row
        aggregate = aggregates.get(key)
        if not audit.check(
            aggregate is not None,
            "scenario.missing_ledger_rows",
            "Every scenario summary needs matching call-ledger rows.",
            **context,
        ):
            continue

        integer_fields = (
            "call_count",
            "main_call_count",
            "compactions",
            "long_context_calls",
            "max_input_tokens",
            "discarded_context_tokens",
        )
        for name in integer_fields:
            observed = _int(row, name)
            expected = int(aggregate[name])
            audit.check(
                observed == expected,
                "scenario.aggregate_integer",
                "Scenario integer summary does not reconcile to its ledger.",
                field=name,
                expected=expected,
                observed=observed,
                **context,
            )
        decimal_fields = (
            "input_uncached_tokens",
            "cache_read_tokens",
            "cache_write_tokens",
            "output_tokens",
            "input_uncached_cost_usd",
            "cache_read_cost_usd",
            "cache_write_cost_usd",
            "output_cost_usd",
            "provider_cost_usd",
        )
        for name in decimal_fields:
            observed = _scenario_decimal(row, name)
            expected = Decimal(aggregate[name])
            audit.check(
                _close(observed, expected),
                "scenario.aggregate_decimal",
                "Scenario token/cost summary does not reconcile to its ledger.",
                field=name,
                expected=expected,
                observed=observed,
                **context,
            )
        expected_credits = Decimal(aggregate["provider_cost_usd"]) / AI_CREDIT_USD
        audit.check(
            _close(_dec(row, "ai_credits"), expected_credits),
            "scenario.ai_credits",
            "Scenario AI credits must equal provider USD divided by $0.01.",
            expected=expected_credits,
            observed=_dec(row, "ai_credits"),
            **context,
        )
        parameters = _parse_object(row.get("parameters_json"))
        if audit.check(
            parameters is not None,
            "scenario.parameters_json",
            "Scenario must expose a valid parameters_json object for OFAT auditing.",
            **context,
        ):
            parameter = _text(row, "changed_parameter")
            matching_paths = [
                path
                for path in _flatten(parameters)
                if _parameter_matches_path(parameter, path)
            ]
            audit.check(
                len(matching_paths) == 1,
                "scenario.changed_parameter_path",
                "changed_parameter must identify exactly one parameter leaf.",
                changed_parameter=parameter,
                matching_paths=matching_paths,
                **context,
            )
            if len(matching_paths) == 1:
                expected_value = _flatten(parameters)[matching_paths[0]]
                audit.check(
                    _text(row, "changed_value") == str(expected_value),
                    "scenario.changed_value",
                    "changed_value must match its parameter leaf.",
                    expected=expected_value,
                    observed=_text(row, "changed_value"),
                    **context,
                )

    for key in aggregates:
        audit.check(
            key in scenario_map,
            "ledger.missing_scenario_summary",
            "Every ledger scenario needs a scenario-results.csv row.",
            scenario_key=key,
        )
    return scenario_map


def _find_scenario_for_contrast(
    scenario_map: Mapping[tuple[str, str, str, str], Mapping[str, str]],
    contrast_id: str,
    scenario_id: str,
    role: str,
    model: str,
) -> Mapping[str, str] | None:
    direct = scenario_map.get((contrast_id, scenario_id, role, model))
    if direct is not None:
        return direct
    candidates = [
        row
        for key, row in scenario_map.items()
        if key[0] == contrast_id and key[2] == role and key[3] == model
    ]
    return candidates[0] if len(candidates) == 1 else None


def _audit_contrasts(
    contrasts: Sequence[Mapping[str, str]],
    scenario_map: Mapping[tuple[str, str, str, str], Mapping[str, str]],
    audit: Audit,
) -> None:
    seen: set[tuple[str, str]] = set()
    for row_number, row in enumerate(contrasts, start=2):
        contrast_id = _text(row, "contrast_id")
        model = _canonical_model(_text(row, "model"))
        context = {"contrast_id": contrast_id, "model": model, "csv_row": row_number}
        if not audit.check(
            model is not None,
            "contrast.unknown_model",
            "Contrast must identify Luna, Terra, or Sol.",
            **context,
        ):
            continue
        audit.check(
            (contrast_id, model) not in seen,
            "contrast.duplicate",
            "contrast_id + model must be unique.",
            **context,
        )
        seen.add((contrast_id, model))
        baseline_id = _text(row, "baseline_scenario_id")
        comparison_id = _text(row, "comparison_scenario_id")
        baseline = _find_scenario_for_contrast(
            scenario_map, contrast_id, baseline_id, "baseline", model
        )
        comparison = _find_scenario_for_contrast(
            scenario_map, contrast_id, comparison_id, "comparison", model
        )
        if not audit.check(
            baseline is not None and comparison is not None,
            "contrast.scenario_pair",
            "Contrast must resolve to exactly one baseline and one comparison scenario.",
            baseline_scenario_id=baseline_id,
            comparison_scenario_id=comparison_id,
            **context,
        ):
            continue

        baseline_cost = _dec(baseline, "provider_cost_usd")
        comparison_cost = _dec(comparison, "provider_cost_usd")
        if baseline_cost is None or comparison_cost is None:
            audit.check(
                False,
                "contrast.missing_cost",
                "Scenario costs must be numeric.",
                **context,
            )
            continue
        expected_delta = comparison_cost - baseline_cost
        expected_pct = (
            expected_delta / baseline_cost * Decimal(100)
            if baseline_cost != 0
            else None
        )
        cost_checks = {
            "baseline_provider_cost_usd": baseline_cost,
            "comparison_provider_cost_usd": comparison_cost,
            "cost_delta_usd": expected_delta,
        }
        for field_name, expected in cost_checks.items():
            audit.check(
                _close(_dec(row, field_name), expected),
                "contrast.cost_reconciliation",
                "Contrast cost must be derived from its scenario pair.",
                field=field_name,
                expected=expected,
                observed=_dec(row, field_name),
                **context,
            )
        if expected_pct is not None:
            observed_pct = _dec(
                row,
                "cost_change_pct",
                "percent_change",
                "pct_change",
                "delta_percent",
            )
            audit.check(
                _close(observed_pct, expected_pct),
                "contrast.percent_change",
                "Percent change must equal delta / baseline × 100.",
                expected=expected_pct,
                observed=observed_pct,
                **context,
            )
        expected_cheaper = (
            "baseline"
            if baseline_cost < comparison_cost
            else "comparison"
            if comparison_cost < baseline_cost
            else "tie"
        )
        audit.check(
            _text(row, "cheaper_role").lower() == expected_cheaper,
            "contrast.cheaper_role",
            "cheaper_role must agree with the reconstructed costs.",
            expected=expected_cheaper,
            observed=_text(row, "cheaper_role"),
            **context,
        )

        parameter = _text(row, "changed_parameter")
        baseline_parameters = _parse_object(row.get("baseline_parameters_json"))
        comparison_parameters = _parse_object(row.get("comparison_parameters_json"))
        if baseline_parameters is None:
            baseline_parameters = _parse_object(baseline.get("parameters_json"))
        if comparison_parameters is None:
            comparison_parameters = _parse_object(comparison.get("parameters_json"))
        if not audit.check(
            baseline_parameters is not None and comparison_parameters is not None,
            "ofat.missing_parameters",
            "Both sides must expose complete parameter objects for OFAT validation.",
            **context,
        ):
            continue
        scenario_baseline_parameters = _parse_object(baseline.get("parameters_json"))
        scenario_comparison_parameters = _parse_object(
            comparison.get("parameters_json")
        )
        audit.check(
            scenario_baseline_parameters == baseline_parameters,
            "ofat.baseline_parameter_reconciliation",
            "Contrast baseline_parameters_json must equal its scenario parameters_json.",
            **context,
        )
        audit.check(
            scenario_comparison_parameters == comparison_parameters,
            "ofat.comparison_parameter_reconciliation",
            "Contrast comparison_parameters_json must equal its scenario parameters_json.",
            **context,
        )
        flat_baseline = _flatten(baseline_parameters)
        flat_comparison = _flatten(comparison_parameters)
        all_paths = sorted(set(flat_baseline) | set(flat_comparison))
        changed_paths = [
            path
            for path in all_paths
            if flat_baseline.get(path, object()) != flat_comparison.get(path, object())
        ]
        audit.check(
            len(changed_paths) == 1,
            "ofat.changed_count",
            "A one-factor-at-a-time contrast must change exactly one parameter leaf.",
            changed_parameter=parameter,
            changed_paths=changed_paths,
            **context,
        )
        if len(changed_paths) == 1:
            changed_path = changed_paths[0]
            audit.check(
                _parameter_matches_path(parameter, changed_path),
                "ofat.declared_parameter",
                "The changed leaf must match changed_parameter.",
                declared=parameter,
                observed_path=changed_path,
                **context,
            )
            baseline_value = _text(row, "baseline_value", "baseline_changed_value")
            comparison_value = _text(
                row, "comparison_value", "comparison_changed_value"
            )
            expected_baseline_value = flat_baseline.get(changed_path)
            expected_comparison_value = flat_comparison.get(changed_path)
            audit.check(
                baseline_value == str(expected_baseline_value),
                "ofat.baseline_value",
                "baseline_value must match the changed leaf in parameters_json.",
                expected=expected_baseline_value,
                observed=baseline_value,
                **context,
            )
            audit.check(
                comparison_value == str(expected_comparison_value),
                "ofat.comparison_value",
                "comparison_value must match the changed leaf in parameters_json.",
                expected=expected_comparison_value,
                observed=comparison_value,
                **context,
            )
            baseline_numeric = _dec({"value": baseline_value}, "value")
            comparison_numeric = _dec({"value": comparison_value}, "value")
            observed_elasticity = _dec(row, "point_elasticity", "elasticity")
            if (
                observed_elasticity is not None
                and baseline_numeric not in {None, Decimal(0)}
                and comparison_numeric is not None
                and comparison_numeric != baseline_numeric
                and baseline_cost != 0
            ):
                expected_elasticity = (expected_delta / baseline_cost) / (
                    (comparison_numeric - baseline_numeric) / baseline_numeric
                )
                audit.check(
                    _close(observed_elasticity, expected_elasticity),
                    "contrast.elasticity",
                    "Elasticity must be (% cost change) / (% parameter change).",
                    expected=expected_elasticity,
                    observed=observed_elasticity,
                    **context,
                )


def _audit_scale(
    scale_rows: Sequence[Mapping[str, str]],
    contrasts: Sequence[Mapping[str, str]],
    expected_volumes: set[int],
    audit: Audit,
) -> None:
    contrast_map: dict[tuple[str, str], Mapping[str, str]] = {}
    for row in contrasts:
        model = _canonical_model(_text(row, "model"))
        if model is not None:
            contrast_map[(_text(row, "contrast_id"), model)] = row
    volumes_by_contrast: dict[tuple[str, str], set[int]] = defaultdict(set)
    for row_number, row in enumerate(scale_rows, start=2):
        model = _canonical_model(_text(row, "model"))
        key = (_text(row, "contrast_id"), model or _text(row, "model").lower())
        context = {
            "contrast_id": key[0],
            "model": key[1],
            "csv_row": row_number,
        }
        contrast = contrast_map.get(key)
        if not audit.check(
            contrast is not None,
            "scale.unknown_contrast",
            "Scale row must resolve to a contrast summary.",
            **context,
        ):
            continue
        volume = _int(
            row,
            "volume_executions",
            "volume",
            "monthly_executions",
            "executions",
        )
        if not audit.check(
            volume is not None and volume > 0,
            "scale.invalid_volume",
            "Scale volume must be a positive integer.",
            observed=volume,
            **context,
        ):
            continue
        volumes_by_contrast[key].add(volume)
        per_execution_values = {
            "baseline_provider_cost_usd": _dec(contrast, "baseline_provider_cost_usd"),
            "comparison_provider_cost_usd": _dec(
                contrast, "comparison_provider_cost_usd"
            ),
            "cost_delta_usd": _dec(contrast, "cost_delta_usd"),
            "savings_usd": _dec(contrast, "savings_usd"),
        }
        for field_name, per_execution in per_execution_values.items():
            expected = (
                per_execution * Decimal(volume) if per_execution is not None else None
            )
            observed = _dec(row, field_name)
            audit.check(
                _close(observed, expected),
                "scale.cost",
                "Scaled contrast value must equal its per-execution value × volume.",
                field=field_name,
                expected=expected,
                observed=observed,
                volume=volume,
                **context,
            )
        for role in ("baseline", "comparison"):
            expected_cost = per_execution_values[f"{role}_provider_cost_usd"]
            expected_credits = (
                expected_cost * Decimal(volume) / AI_CREDIT_USD
                if expected_cost is not None
                else None
            )
            observed_credits = _dec(row, f"{role}_ai_credits")
            audit.check(
                _close(observed_credits, expected_credits),
                "scale.ai_credits",
                "Scaled AI credits must equal scaled provider cost / $0.01.",
                role=role,
                expected=expected_credits,
                observed=observed_credits,
                volume=volume,
                **context,
            )
        expected_credit_delta = (
            per_execution_values["cost_delta_usd"] * Decimal(volume) / AI_CREDIT_USD
            if per_execution_values["cost_delta_usd"] is not None
            else None
        )
        audit.check(
            _close(_dec(row, "ai_credit_delta"), expected_credit_delta),
            "scale.ai_credit_delta",
            "Scaled AI-credit delta must equal scaled cost delta / $0.01.",
            expected=expected_credit_delta,
            observed=_dec(row, "ai_credit_delta"),
            volume=volume,
            **context,
        )

    for key in contrast_map:
        audit.check(
            volumes_by_contrast.get(key, set()) == expected_volumes,
            "scale.volume_coverage",
            "Every contrast must be scaled to exactly the declared study volumes.",
            expected=sorted(expected_volumes),
            observed=sorted(volumes_by_contrast.get(key, set())),
            contrast_key=key,
        )


def _audit_stable_system_oracle(
    scenarios: Mapping[tuple[str, str, str, str], Mapping[str, str]],
    audit: Audit,
) -> None:
    expected_deltas = {
        "luna": Decimal("0.00043"),
        "terra": Decimal("0.0043"),
        "sol": Decimal("0.0086"),
    }
    oracle_ids = {
        "stable-system-10-calls",
        "system-prompt-plus-1k-stable-10",
    }
    for model, expected_delta in expected_deltas.items():
        baseline = next(
            (
                row
                for key, row in scenarios.items()
                if key[0] in oracle_ids and key[2] == "baseline" and key[3] == model
            ),
            None,
        )
        comparison = next(
            (
                row
                for key, row in scenarios.items()
                if key[0] in oracle_ids and key[2] == "comparison" and key[3] == model
            ),
            None,
        )
        if not audit.check(
            baseline is not None and comparison is not None,
            "oracle.stable_system_missing",
            "Required stable-system-10-calls oracle scenarios are missing.",
            model=model,
        ):
            continue
        audit.check(
            _int(baseline, "call_count") == 10 and _int(comparison, "call_count") == 10,
            "oracle.stable_system_calls",
            "Stable system-prompt oracle must use exactly ten model calls.",
            model=model,
        )
        baseline_cost = _dec(baseline, "provider_cost_usd")
        comparison_cost = _dec(comparison, "provider_cost_usd")
        observed_delta = (
            comparison_cost - baseline_cost
            if baseline_cost is not None and comparison_cost is not None
            else None
        )
        audit.check(
            _close(observed_delta, expected_delta),
            "oracle.stable_system_delta",
            "Adding 1,000 stable system tokens over ten calls must cost one cold write plus nine cache reads.",
            expected=expected_delta,
            observed=observed_delta,
            model=model,
        )
        write_delta = _scenario_decimal(comparison, "cache_write_tokens")
        baseline_write = _scenario_decimal(baseline, "cache_write_tokens")
        read_delta = _scenario_decimal(comparison, "cache_read_tokens")
        baseline_read = _scenario_decimal(baseline, "cache_read_tokens")
        audit.check(
            write_delta is not None
            and baseline_write is not None
            and write_delta - baseline_write == Decimal(1000),
            "oracle.stable_system_write_partition",
            "The extra stable prefix must be written once (1,000 cache-write tokens).",
            model=model,
        )
        audit.check(
            read_delta is not None
            and baseline_read is not None
            and read_delta - baseline_read == Decimal(9000),
            "oracle.stable_system_read_partition",
            "The extra stable prefix must be read on the remaining nine calls (9,000 cache-read tokens).",
            model=model,
        )


def _audit_threshold_oracle(
    ledger: Sequence[Mapping[str, str]],
    audit: Audit,
) -> None:
    expected = {
        "baseline": (199_500, Decimal("0.00519"), "short"),
        "comparison": (200_500, Decimal("0.00982"), "long"),
    }
    oracle_ids = {
        "system-threshold-warm",
        "system-prompt-plus-1k-cross-threshold",
    }
    for role, (input_tokens, expected_cost, expected_tier) in expected.items():
        matches = [
            row
            for row in ledger
            if _text(row, "contrast_id") in oracle_ids
            and _canonical_model(_text(row, "model")) == "luna"
            and _text(row, "role").lower() == role
            and _int(row, "full_input_tokens") == input_tokens
            and _int(row, "cache_read_tokens") == input_tokens
            and _int(row, "input_uncached_tokens", default=0) == 0
            and _int(row, "cache_write_tokens", default=0) == 0
            and _int(row, "output_tokens") == 1000
        ]
        if not audit.check(
            len(matches) == 1,
            "oracle.threshold_shape",
            "Warm Luna threshold oracle must contain exactly one all-cache-read call with the specified input and output.",
            role=role,
            input_tokens=input_tokens,
            match_count=len(matches),
        ):
            continue
        row = matches[0]
        audit.check(
            _text(row, "pricing_tier").lower() == expected_tier,
            "oracle.threshold_tier",
            "199.5K must be short-tier and 200.5K must be long-tier for Luna through Copilot.",
            role=role,
            expected=expected_tier,
            observed=_text(row, "pricing_tier"),
        )
        audit.check(
            _close(_dec(row, "provider_cost_usd"), expected_cost),
            "oracle.threshold_cost",
            "Warm Luna threshold cost does not match the hand oracle.",
            role=role,
            expected=expected_cost,
            observed=_dec(row, "provider_cost_usd"),
        )


def _oracle_call_cost(
    model: str,
    *,
    uncached: int = 0,
    read: int = 0,
    write: int = 0,
    output: int = 0,
) -> Decimal:
    full = uncached + read + write
    rates = EXPECTED_RATE_CARD[model][_tier_for(model, full)]
    return (
        Decimal(uncached) * rates["uncached"]
        + Decimal(read) * rates["read"]
        + Decimal(write) * rates["write"]
        + Decimal(output) * rates["output"]
    ) / MILLION


def _long_schedule_oracle(
    model: str,
    *,
    cap: int | None,
    compaction_input_mode: str,
    retain_system_prefix: bool,
) -> dict[str, Any]:
    """Recreate the preregistered 39-call schedule independently of the model."""

    current = 40_000
    cold = True
    total = Decimal(0)
    main_cost = Decimal(0)
    compaction_cost = Decimal(0)
    compactions = 0
    max_input = 0
    main_prompts: list[int] = []
    for main_index in range(39):
        if main_index > 0:
            candidate = current + 20_000
            if cap is not None and candidate > cap:
                buckets = {
                    "uncached": {"uncached": current},
                    "cache_read": {"read": current},
                    "cache_write": {"write": current},
                }
                kwargs = buckets[compaction_input_mode]
                cost = _oracle_call_cost(model, **kwargs, output=20_000)
                total += cost
                compaction_cost += cost
                compactions += 1
                max_input = max(max_input, current)
                current = 40_000
                cold = True
            else:
                current = candidate

        if cold:
            if main_index == 0 or not retain_system_prefix:
                read = 0
                write = current
            else:
                read = 20_000
                write = current - 20_000
            cold = False
        else:
            read = current - 20_000
            write = 20_000
        cost = _oracle_call_cost(model, read=read, write=write, output=1_000)
        total += cost
        main_cost += cost
        max_input = max(max_input, current)
        main_prompts.append(current)
    return {
        "provider_cost_usd": total,
        "main_cost_usd": main_cost,
        "compaction_cost_usd": compaction_cost,
        "compactions": compactions,
        "max_input_tokens": max_input,
        "main_prompts": main_prompts,
    }


def _scenario_by_id_role_model(
    scenarios: Mapping[tuple[str, str, str, str], Mapping[str, str]],
    contrast_id: str,
    role: str,
    model: str,
) -> tuple[tuple[str, str, str, str], Mapping[str, str]] | None:
    matches = [
        (key, row)
        for key, row in scenarios.items()
        if key[0] == contrast_id and key[2] == role and key[3] == model
    ]
    return matches[0] if len(matches) == 1 else None


def _audit_exact_long_oracles(
    scenarios: Mapping[tuple[str, str, str, str], Mapping[str, str]],
    aggregates: Mapping[tuple[str, str, str, str], Mapping[str, Any]],
    audit: Audit,
) -> None:
    """Check primary and sensitivity scenarios against a separate state machine."""

    no_compact = {
        model: _long_schedule_oracle(
            model,
            cap=None,
            compaction_input_mode="uncached",
            retain_system_prefix=False,
        )
        for model in EXPECTED_RATE_CARD
    }
    capped = {
        (model, mode, retained): _long_schedule_oracle(
            model,
            cap=200_000,
            compaction_input_mode=mode,
            retain_system_prefix=retained,
        )
        for model in EXPECTED_RATE_CARD
        for mode in ("uncached", "cache_read", "cache_write")
        for retained in (False, True)
    }

    expected_scenarios = (
        ("long-cap-200k-uncached", "baseline", lambda model: no_compact[model]),
        (
            "long-cap-200k-uncached",
            "comparison",
            lambda model: capped[(model, "uncached", False)],
        ),
        (
            "compaction-input-cache-read-sensitivity",
            "baseline",
            lambda model: capped[(model, "uncached", False)],
        ),
        (
            "compaction-input-cache-read-sensitivity",
            "comparison",
            lambda model: capped[(model, "cache_read", False)],
        ),
        (
            "compaction-input-cache-write-sensitivity",
            "baseline",
            lambda model: capped[(model, "uncached", False)],
        ),
        (
            "compaction-input-cache-write-sensitivity",
            "comparison",
            lambda model: capped[(model, "cache_write", False)],
        ),
        (
            "compaction-retained-system-sensitivity",
            "baseline",
            lambda model: capped[(model, "uncached", False)],
        ),
        (
            "compaction-retained-system-sensitivity",
            "comparison",
            lambda model: capped[(model, "uncached", True)],
        ),
    )
    for contrast_id, role, expected_for_model in expected_scenarios:
        for model in EXPECTED_RATE_CARD:
            found = _scenario_by_id_role_model(scenarios, contrast_id, role, model)
            if not audit.check(
                found is not None,
                "oracle.long_scenario_missing",
                "Required preregistered long-session scenario is missing.",
                contrast_id=contrast_id,
                role=role,
                model=model,
            ):
                continue
            key, row = found
            expected = expected_for_model(model)
            context = {"contrast_id": contrast_id, "role": role, "model": model}
            audit.check(
                _close(_dec(row, "provider_cost_usd"), expected["provider_cost_usd"]),
                "oracle.long_cost",
                "Long-session scenario cost does not match the independent 39-call state machine.",
                expected=expected["provider_cost_usd"],
                observed=_dec(row, "provider_cost_usd"),
                **context,
            )
            audit.check(
                _int(row, "main_call_count") == 39,
                "oracle.long_main_calls",
                "Preregistered long-session scenario must contain 39 main calls.",
                observed=_int(row, "main_call_count"),
                **context,
            )
            audit.check(
                _int(row, "compactions") == expected["compactions"],
                "oracle.long_compactions",
                "Compaction count does not match the independent schedule.",
                expected=expected["compactions"],
                observed=_int(row, "compactions"),
                **context,
            )
            audit.check(
                _int(row, "max_input_tokens") == expected["max_input_tokens"],
                "oracle.long_max_input",
                "Maximum input does not match the independent schedule.",
                expected=expected["max_input_tokens"],
                observed=_int(row, "max_input_tokens"),
                **context,
            )
            main_ledger_cost = sum(
                (
                    _dec(call, "provider_cost_usd") or Decimal(0)
                    for call in aggregates[key]["rows"]
                    if not _truthy(call.get("compaction_event", ""))
                    and "compact" not in _text(call, "call_kind").lower()
                ),
                Decimal(0),
            )
            actual_main_prompts = [
                _int(call, "full_input_tokens")
                for call in sorted(
                    aggregates[key]["rows"],
                    key=lambda call: _int(call, "call_index", default=0) or 0,
                )
                if not _truthy(call.get("compaction_event", ""))
                and "compact" not in _text(call, "call_kind").lower()
            ]
            audit.check(
                actual_main_prompts == expected["main_prompts"],
                "oracle.long_prompt_schedule",
                "Main prompts must follow the exact independent 40k-to-800k or reset schedule.",
                expected=expected["main_prompts"],
                observed=actual_main_prompts,
                **context,
            )
            audit.check(
                _close(main_ledger_cost, expected["main_cost_usd"]),
                "oracle.long_main_cost",
                "Main-call subtotal does not match the independent schedule.",
                expected=expected["main_cost_usd"],
                observed=main_ledger_cost,
                **context,
            )

    # Explicit headline hand calculations supplied in the preregistration.
    luna_expected = {
        ("long-cap-200k-uncached", "baseline"): Decimal("1.0204"),
        ("long-cap-200k-uncached", "comparison"): Decimal("0.5952"),
        ("compaction-input-cache-read-sensitivity", "comparison"): Decimal("0.4512"),
        ("compaction-input-cache-write-sensitivity", "comparison"): Decimal("0.6352"),
    }
    for (contrast_id, role), expected_cost in luna_expected.items():
        found = _scenario_by_id_role_model(scenarios, contrast_id, role, "luna")
        if found is None:
            continue
        _, row = found
        audit.check(
            _close(_dec(row, "provider_cost_usd"), expected_cost),
            "oracle.luna_long_headline",
            "Luna long-session headline cost does not match the hand oracle.",
            contrast_id=contrast_id,
            role=role,
            expected=expected_cost,
            observed=_dec(row, "provider_cost_usd"),
        )
    primary = _scenario_by_id_role_model(
        scenarios, "long-cap-200k-uncached", "comparison", "luna"
    )
    if primary is not None:
        primary_key, _ = primary
        main_cost = sum(
            (
                _dec(call, "provider_cost_usd") or Decimal(0)
                for call in aggregates[primary_key]["rows"]
                if not _truthy(call.get("compaction_event", ""))
            ),
            Decimal(0),
        )
        audit.check(
            _close(main_cost, Decimal("0.3392")),
            "oracle.luna_capped_main_subtotal",
            "Luna capped main-call subtotal must equal the $0.3392 hand oracle.",
            expected=Decimal("0.3392"),
            observed=main_cost,
        )


def _audit_long_sessions(
    scenarios: Mapping[tuple[str, str, str, str], Mapping[str, str]],
    aggregates: Mapping[tuple[str, str, str, str], Mapping[str, Any]],
    audit: Audit,
) -> None:
    context_keys = [
        key
        for key, row in scenarios.items()
        if _text(row, "study_family").lower() == "long_session"
        and _text(row, "changed_parameter").lower() == "compaction_strategy"
    ]
    contrast_models = sorted({(key[0], key[3]) for key in context_keys})
    if not audit.check(
        bool(contrast_models),
        "long_session.missing",
        "Bundle must include at least one long-session compaction contrast.",
    ):
        return

    for contrast_id, model in contrast_models:
        baseline_key = next(
            (
                key
                for key in context_keys
                if key[0] == contrast_id and key[2] == "baseline" and key[3] == model
            ),
            None,
        )
        comparison_key = next(
            (
                key
                for key in context_keys
                if key[0] == contrast_id and key[2] == "comparison" and key[3] == model
            ),
            None,
        )
        if baseline_key is None or comparison_key is None:
            continue
        baseline = scenarios[baseline_key]
        comparison = scenarios[comparison_key]
        baseline_compactions = _int(baseline, "compactions")
        comparison_compactions = _int(comparison, "compactions")
        baseline_max = _int(baseline, "max_input_tokens")
        comparison_max = _int(comparison, "max_input_tokens")
        threshold = int(EXPECTED_RATE_CARD[model]["threshold"])
        context = {"contrast_id": contrast_id, "model": model}
        audit.check(
            baseline_compactions == 0
            and comparison_compactions is not None
            and comparison_compactions > 0,
            "long_session.compaction_count",
            "Context-policy contrast must compare no compaction with at least one compaction.",
            baseline_compactions=baseline_compactions,
            comparison_compactions=comparison_compactions,
            **context,
        )
        audit.check(
            baseline_max is not None and baseline_max > threshold,
            "long_session.baseline_crosses_threshold",
            "Uncompacted long-session baseline must cross the model's Copilot long-context threshold.",
            max_input_tokens=baseline_max,
            threshold=threshold,
            **context,
        )
        audit.check(
            comparison_max is not None and comparison_max <= threshold,
            "long_session.compacted_below_threshold",
            "Compacted comparison must keep every request at or below the pricing threshold.",
            max_input_tokens=comparison_max,
            threshold=threshold,
            **context,
        )
        audit.check(
            _int(baseline, "main_call_count") == _int(comparison, "main_call_count"),
            "long_session.main_workload",
            "Compaction policy must not change the number of main workload calls.",
            baseline_main_calls=_int(baseline, "main_call_count"),
            comparison_main_calls=_int(comparison, "main_call_count"),
            **context,
        )

        compact_rows = sorted(
            aggregates[comparison_key]["rows"],
            key=lambda row: _int(row, "call_index", default=0) or 0,
        )
        last_main_input: int | None = None
        expect_reset = False
        observed_resets = 0
        for row in compact_rows:
            kind = _text(row, "call_kind").lower()
            is_compaction = (
                _truthy(row.get("compaction_event", "")) or "compact" in kind
            )
            full = _int(row, "full_input_tokens")
            if is_compaction:
                audit.check(
                    _int(row, "output_tokens", default=0) > 0,
                    "long_session.compaction_summary",
                    "Each compaction call must emit summary tokens.",
                    call_index=_int(row, "call_index"),
                    **context,
                )
                expect_reset = True
                continue
            if is_compaction or full is None:
                continue
            if expect_reset and last_main_input is not None:
                audit.check(
                    full < last_main_input,
                    "long_session.context_reset",
                    "The first main call after compaction must have a smaller prompt than the pre-compaction main call.",
                    before=last_main_input,
                    after=full,
                    call_index=_int(row, "call_index"),
                    **context,
                )
                observed_resets += int(full < last_main_input)
                expect_reset = False
            elif last_main_input is not None:
                audit.check(
                    full >= last_main_input,
                    "long_session.append_only_growth",
                    "Main-call context must not shrink except immediately after compaction.",
                    previous=last_main_input,
                    current=full,
                    call_index=_int(row, "call_index"),
                    **context,
                )
            last_main_input = full
        audit.check(
            comparison_compactions is not None
            and observed_resets == comparison_compactions,
            "long_session.reset_count",
            "Every compaction must be followed by one observed context reset.",
            expected=comparison_compactions,
            observed=observed_resets,
            **context,
        )
    _audit_exact_long_oracles(scenarios, aggregates, audit)


def _extract_volumes(study: Mapping[str, Any], audit: Audit) -> set[int]:
    raw = study.get("volumes", [])
    volumes: set[int] = set()
    if isinstance(raw, list):
        for value in raw:
            try:
                parsed = int(value)
            except (TypeError, ValueError):
                continue
            if parsed > 0:
                volumes.add(parsed)
    audit.check(
        volumes == {1_000, 1_000_000},
        "study.volumes",
        "Study must report both 1,000 and 1,000,000 hypothetical executions.",
        expected=[1000, 1000000],
        observed=sorted(volumes),
    )
    return volumes or {1_000, 1_000_000}


def _audit_study_json(
    study: Mapping[str, Any],
    csv_counts: Mapping[str, int],
    audit: Audit,
) -> None:
    provenance = study.get("provenance", {})
    provenance_text = json.dumps(provenance, sort_keys=True).lower()
    audit.check(
        "simulat" in provenance_text
        or "determin" in provenance_text
        or "offline" in provenance_text,
        "study.provenance_mode",
        "Provenance must explicitly identify the bundle as a simulation/offline deterministic study.",
    )
    audit.check(
        isinstance(provenance, Mapping)
        and provenance.get("real_pi_or_copilot_calls") is False,
        "study.no_real_provider_calls",
        "Provenance must explicitly state that no real Pi or Copilot calls were made.",
        observed=provenance.get("real_pi_or_copilot_calls")
        if isinstance(provenance, Mapping)
        else None,
    )
    audit.check(
        isinstance(provenance, Mapping)
        and provenance.get("automatic_model_discount_applied") is False,
        "study.no_auto_discount",
        "Fixed-model Pi-through-Copilot study must explicitly apply no automatic-model discount.",
        observed=provenance.get("automatic_model_discount_applied")
        if isinstance(provenance, Mapping)
        else None,
    )
    rate_card = study.get("rate_card")
    audit.check(
        isinstance(rate_card, Mapping),
        "study.rate_card",
        "study-results.json must embed the exact rate card used.",
    )
    if isinstance(rate_card, Mapping):
        for model, expected in EXPECTED_RATE_CARD.items():
            raw_model = rate_card.get(model)
            context = {"model": model}
            if not audit.check(
                isinstance(raw_model, Mapping),
                "study.rate_card_model",
                "Embedded rate card is missing a model.",
                **context,
            ):
                continue
            audit.check(
                _int(raw_model, "long_context_threshold_tokens")
                == int(expected["threshold"]),
                "study.rate_card_threshold",
                "Embedded threshold must match the independent Copilot oracle.",
                expected=expected["threshold"],
                observed=raw_model.get("long_context_threshold_tokens"),
                **context,
            )
            for tier in ("short", "long"):
                raw_tier = raw_model.get(tier)
                if not audit.check(
                    isinstance(raw_tier, Mapping),
                    "study.rate_card_tier",
                    "Embedded rate card is missing a pricing tier.",
                    tier=tier,
                    **context,
                ):
                    continue
                aliases = {
                    "uncached": "uncached_input",
                    "read": "cache_read",
                    "write": "cache_write",
                    "output": "output",
                }
                for semantic, field_name in aliases.items():
                    observed = _dec(raw_tier, field_name)
                    audit.check(
                        _close(observed, expected[tier][semantic]),
                        "study.rate_card_rate",
                        "Embedded rate must match the independent Copilot oracle.",
                        tier=tier,
                        rate=field_name,
                        expected=expected[tier][semantic],
                        observed=observed,
                        **context,
                    )
    for field_name, expected_count in csv_counts.items():
        value = study.get(field_name)
        if isinstance(value, list):
            audit.check(
                len(value) == expected_count,
                "study.json_csv_count",
                "study-results.json array must contain the same number of records as its CSV.",
                field=field_name,
                expected=expected_count,
                observed=len(value),
            )


def validate_bundle(bundle: Path) -> tuple[Audit, dict[str, Any]]:
    audit = Audit()
    for model, rate in EXPECTED_RATE_CARD.items():
        threshold = int(rate["threshold"])
        audit.check(
            _tier_for(model, threshold) == "short"
            and _tier_for(model, threshold + 1) == "long",
            "oracle.threshold_boundary",
            "Independent tier oracle must switch only after the exact threshold.",
            model=model,
            threshold=threshold,
        )
    audit.check(
        bundle.is_dir(),
        "bundle.not_directory",
        "Bundle path must be a directory.",
        path=bundle,
    )
    for filename in REQUIRED_FILES:
        audit.check(
            (bundle / filename).is_file(),
            "bundle.missing_file",
            "Required bundle file is missing.",
            path=bundle / filename,
        )
    if audit.failures:
        return audit, audit.report(bundle)

    ledger = _read_csv(bundle / "call-ledger.csv", audit)
    scenarios = _read_csv(bundle / "scenario-results.csv", audit)
    contrasts = _read_csv(bundle / "contrast-results.csv", audit)
    scale_rows = _read_csv(bundle / "scale-results.csv", audit)
    study_raw = _read_json(bundle / "study-results.json", audit)
    study = study_raw if isinstance(study_raw, Mapping) else {}
    audit.check(
        isinstance(study_raw, Mapping),
        "study.root_type",
        "study-results.json root must be a JSON object.",
    )

    aggregates = _audit_ledger(ledger, audit)
    scenario_map = _audit_scenarios(scenarios, aggregates, audit)
    _audit_contrasts(contrasts, scenario_map, audit)
    expected_volumes = _extract_volumes(study, audit)
    _audit_scale(scale_rows, contrasts, expected_volumes, audit)
    _audit_stable_system_oracle(scenario_map, audit)
    _audit_threshold_oracle(ledger, audit)
    _audit_long_sessions(scenario_map, aggregates, audit)
    _audit_study_json(
        study,
        {
            "scenarios": len(scenarios),
            "contrasts": len(contrasts),
            "scale_results": len(scale_rows),
        },
        audit,
    )
    return audit, audit.report(bundle)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Offline independent validator for a deterministic Pi-through-Copilot "
            "cost-elasticity bundle. Performs no model, provider, or network calls."
        )
    )
    parser.add_argument(
        "bundle", type=Path, help="Directory containing the generated bundle"
    )
    parser.add_argument(
        "--report",
        type=Path,
        help="Optional path for the JSON audit report; stdout is always populated",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    _, report = validate_bundle(args.bundle)
    rendered = json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    if args.report is not None:
        try:
            args.report.parent.mkdir(parents=True, exist_ok=True)
            with args.report.open("w", encoding="utf-8", newline="\n") as handle:
                handle.write(rendered)
        except OSError as exc:
            error = {
                "status": "fail",
                "failure_count": 1,
                "failures": [
                    {
                        "code": "report.write_error",
                        "message": "Could not write audit report.",
                        "context": {"path": str(args.report), "error": str(exc)},
                    }
                ],
            }
            print(json.dumps(error, indent=2), file=sys.stderr)
            return 2
    print(rendered, end="")
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
