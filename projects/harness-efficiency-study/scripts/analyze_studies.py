#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

"""Consolidate validated harness-efficiency simulation bundles.

This analyzer never treats a simulated contrast as empirical product evidence.
It keeps provider-ledger value, marginal cash, allocated subscription cash, and
economic loss in separate columns and only consumes release-eligible bundles.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import statistics
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


STUDY_NAMES = ("controlled-harness", "monthly-economics", "usage-policy")
KEY_METRICS = (
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


class AnalysisError(ValueError):
    """A fail-closed input or analysis error."""


def _load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise AnalysisError(f"required file is missing: {path}") from exc
    except json.JSONDecodeError as exc:
        raise AnalysisError(f"invalid JSON in {path}: {exc}") from exc


def _read_csv(path: Path) -> list[dict[str, str]]:
    try:
        with path.open("r", encoding="utf-8", newline="") as handle:
            return list(csv.DictReader(handle))
    except FileNotFoundError as exc:
        raise AnalysisError(f"required file is missing: {path}") from exc


def _write_csv(path: Path, rows: Iterable[dict[str, Any]], fields: list[str]) -> None:
    materialized = list(rows)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        for row in materialized:
            writer.writerow({field: row.get(field, "") for field in fields})


def _canonical_json(value: Any) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ) + "\n"


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _number(value: str | float | int) -> float:
    result = float(value)
    if not math.isfinite(result):
        raise AnalysisError(f"non-finite numeric value: {value!r}")
    return result


def _percentile(sorted_values: list[float], probability: float) -> float:
    if not sorted_values:
        raise AnalysisError("cannot calculate a percentile of no values")
    if len(sorted_values) == 1:
        return sorted_values[0]
    position = (len(sorted_values) - 1) * probability
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return sorted_values[lower]
    weight = position - lower
    return sorted_values[lower] * (1.0 - weight) + sorted_values[upper] * weight


def _describe(values: list[float]) -> dict[str, float | int]:
    if not values:
        raise AnalysisError("cannot describe an empty sample")
    ordered = sorted(values)
    mean = math.fsum(values) / len(values)
    standard_deviation = statistics.stdev(values) if len(values) > 1 else 0.0
    return {
        "n": len(values),
        "mean": mean,
        "stddev": standard_deviation,
        "mcse": standard_deviation / math.sqrt(len(values)),
        "min": ordered[0],
        "p05": _percentile(ordered, 0.05),
        "median": _percentile(ordered, 0.5),
        "p95": _percentile(ordered, 0.95),
        "max": ordered[-1],
    }


def _parameter_map(owner: dict[str, Any]) -> dict[str, Any]:
    parameters = owner.get("parameters", [])
    if not isinstance(parameters, list):
        raise AnalysisError("experiment parameters must be an array")
    result: dict[str, Any] = {}
    for item in parameters:
        if not isinstance(item, dict) or "name" not in item or "value" not in item:
            raise AnalysisError("invalid parameter entry in experiment.json")
        result[str(item["name"])] = item["value"]
    return result


def _workload_label(design_point_id: str, parameters: dict[str, Any]) -> str:
    for name in ("workload_name", "workload_family", "workload_id", "task_family"):
        value = parameters.get(name)
        if isinstance(value, str) and value:
            return value
    tokens = design_point_id.split("-")
    if tokens and tokens[0] in {"low", "medium", "high", "primary", "challenge"}:
        tokens = tokens[1:]
    if len(tokens) >= 2 and tokens[:2] in (["copilot", "cli"], ["pi", "cli"]):
        tokens = tokens[2:]
    return "-".join(tokens) or design_point_id


def _validate_bundle(study_name: str, root: Path) -> dict[str, Any]:
    validation_path = root / "validation-report.json"
    validation = _load_json(validation_path)
    if not isinstance(validation, dict):
        raise AnalysisError(f"{study_name}: validation report must be an object")
    if validation.get("ok") is not True or validation.get("releaseEligible") is not True:
        raise AnalysisError(
            f"{study_name}: bundle is not release eligible; refusing consolidated analysis"
        )
    spec = _load_json(root / "experiment.json")
    hypothesis_results = _load_json(root / "analysis" / "hypothesis-results.json")
    outcomes = _read_csv(root / "data" / "outcomes.csv")
    summary = _read_csv(root / "analysis" / "summary.csv")
    if not isinstance(spec, dict) or not isinstance(hypothesis_results, dict):
        raise AnalysisError(f"{study_name}: malformed spec or hypothesis result")
    if not outcomes or not summary:
        raise AnalysisError(f"{study_name}: empty outcomes or summary table")
    expected_id = spec.get("experimentId")
    if hypothesis_results.get("experimentId") != expected_id:
        raise AnalysisError(f"{study_name}: hypothesis experiment ID does not match")
    return {
        "root": root,
        "validation": validation,
        "spec": spec,
        "hypothesis_results": hypothesis_results,
        "outcomes": outcomes,
        "summary": summary,
        "hashes": {
            "experiment": _sha256(root / "experiment.json"),
            "outcomes": _sha256(root / "data" / "outcomes.csv"),
            "summary": _sha256(root / "analysis" / "summary.csv"),
            "hypothesisResults": _sha256(root / "analysis" / "hypothesis-results.json"),
            "validationReport": _sha256(validation_path),
        },
    }


def _scenario_summaries(
    bundles: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    groups: dict[tuple[str, str, str, str], list[float]] = defaultdict(list)
    for study_name, bundle in bundles.items():
        for row in bundle["outcomes"]:
            design_point_id = row["design_point_id"]
            if design_point_id.startswith(("primary-", "central-")):
                design_group = "primary"
            elif design_point_id.startswith("challenge-"):
                design_group = "challenge"
            elif design_point_id.startswith("low-"):
                design_group = "low-volume"
            elif design_point_id.startswith("medium-"):
                design_group = "medium-volume"
            elif design_point_id.startswith("high-"):
                design_group = "high-volume"
            else:
                design_group = "unclassified"
            value = _number(row["value"])
            groups[(study_name, "all", row["scenario_id"], row["outcome_name"])].append(value)
            groups[(study_name, design_group, row["scenario_id"], row["outcome_name"])].append(value)
    result: list[dict[str, Any]] = []
    for (study, design_group, scenario, outcome), values in sorted(groups.items()):
        result.append(
            {
                "study": study,
                "design_group": design_group,
                "scenario_id": scenario,
                "outcome_name": outcome,
                **_describe(values),
            }
        )
    return result


def _workload_rows(bundles: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    values: dict[tuple[str, str, str, str], list[float]] = defaultdict(list)
    design_metadata: dict[tuple[str, str], dict[str, Any]] = {}
    for study_name, bundle in bundles.items():
        for point in bundle["spec"].get("designPoints", []):
            point_id = str(point["designPointId"])
            params = _parameter_map(point)
            design_metadata[(study_name, point_id)] = {
                "workload": _workload_label(point_id, params),
                "tasks_per_run": params.get("tasks_per_run", ""),
                "billing_period_tasks": params.get("billing_period_tasks", ""),
            }
        for row in bundle["outcomes"]:
            outcome = row["outcome_name"]
            if outcome in KEY_METRICS:
                key = (
                    study_name,
                    row["design_point_id"],
                    row["scenario_id"],
                    outcome,
                )
                values[key].append(_number(row["value"]))

    cells: dict[tuple[str, str, str], dict[str, Any]] = {}
    for (study, point, scenario, outcome), sample in sorted(values.items()):
        cell = cells.setdefault(
            (study, point, scenario),
            {
                "study": study,
                "design_point_id": point,
                "scenario_id": scenario,
                **design_metadata.get(
                    (study, point),
                    {"workload": point, "tasks_per_run": "", "billing_period_tasks": ""},
                ),
            },
        )
        cell[outcome] = _describe(sample)["mean"]

    rows = list(cells.values())
    by_point: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        by_point[(row["study"], row["design_point_id"])].append(row)
    for point_rows in by_point.values():
        ranked = sorted(
            point_rows,
            key=lambda row: (
                _number(row.get("normalized_cost_per_verified_work", math.inf)),
                -_number(row.get("accepted_task_fraction", 0.0)),
                _number(row.get("wall_seconds_per_task", math.inf)),
                row["scenario_id"],
            ),
        )
        for rank, row in enumerate(ranked, start=1):
            row["efficiency_rank_within_design_point"] = rank
    return sorted(rows, key=lambda row: (row["study"], row["design_point_id"], row["scenario_id"]))


def _pairwise_rows(bundles: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for study_name, bundle in bundles.items():
        spec_hypotheses = {
            item["hypothesisId"]: item for item in bundle["spec"].get("hypotheses", [])
        }
        for item in bundle["hypothesis_results"].get("results", []):
            hypothesis_id = item["hypothesisId"]
            hypothesis = spec_hypotheses.get(hypothesis_id, {})
            analysis = hypothesis.get("analysis", {})
            threshold = item.get("threshold", {})
            points = item.get("designPointResults", [])
            if not points:
                result.append(
                    {
                        "study": study_name,
                        "hypothesis_id": hypothesis_id,
                        "aggregate_status": item.get("status", ""),
                        "baseline_scenario_id": analysis.get("baselineScenarioId", ""),
                        "comparison_scenario_id": analysis.get("comparisonScenarioId", ""),
                        "outcome_name": hypothesis.get("outcome", ""),
                        "design_point_id": "",
                        "role": "",
                        "point_status": "not-identifiable",
                        "estimate_comparison_minus_baseline": "",
                        "interval_low": "",
                        "interval_high": "",
                        "mcse": "",
                        "threshold_operator": threshold.get("operator", ""),
                        "threshold_value": threshold.get("value", ""),
                        "threshold_unit": threshold.get("unit", ""),
                        "complete_pairs": "",
                    }
                )
                continue
            for point in points:
                interval = point.get("interval") or {}
                result.append(
                    {
                        "study": study_name,
                        "hypothesis_id": hypothesis_id,
                        "aggregate_status": item.get("status", ""),
                        "baseline_scenario_id": analysis.get("baselineScenarioId", ""),
                        "comparison_scenario_id": analysis.get("comparisonScenarioId", ""),
                        "outcome_name": hypothesis.get("outcome", ""),
                        "design_point_id": point.get("designPointId", ""),
                        "role": point.get("role", ""),
                        "point_status": point.get("status", ""),
                        "estimate_comparison_minus_baseline": point.get("estimate", ""),
                        "interval_low": interval.get("low", ""),
                        "interval_high": interval.get("high", ""),
                        "mcse": point.get("mcse", ""),
                        "threshold_operator": threshold.get("operator", ""),
                        "threshold_value": threshold.get("value", ""),
                        "threshold_unit": threshold.get("unit", ""),
                        "complete_pairs": (point.get("sample") or {}).get("completePairs", ""),
                    }
                )
    return result


def _pareto_rows(workload_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in workload_rows:
        grouped[(row["study"], row["design_point_id"])].append(row)
    result: list[dict[str, Any]] = []
    for point_rows in grouped.values():
        for candidate in point_rows:
            dominated_by: list[str] = []
            dominates: list[str] = []
            for rival in point_rows:
                if rival is candidate:
                    continue
                rival_no_worse = (
                    _number(rival["accepted_task_fraction"])
                    >= _number(candidate["accepted_task_fraction"])
                    and _number(rival["provider_cost_usd_per_task"])
                    <= _number(candidate["provider_cost_usd_per_task"])
                    and _number(rival["wall_seconds_per_task"])
                    <= _number(candidate["wall_seconds_per_task"])
                )
                rival_strict = (
                    _number(rival["accepted_task_fraction"])
                    > _number(candidate["accepted_task_fraction"])
                    or _number(rival["provider_cost_usd_per_task"])
                    < _number(candidate["provider_cost_usd_per_task"])
                    or _number(rival["wall_seconds_per_task"])
                    < _number(candidate["wall_seconds_per_task"])
                )
                if rival_no_worse and rival_strict:
                    dominated_by.append(rival["scenario_id"])
                candidate_no_worse = (
                    _number(candidate["accepted_task_fraction"])
                    >= _number(rival["accepted_task_fraction"])
                    and _number(candidate["provider_cost_usd_per_task"])
                    <= _number(rival["provider_cost_usd_per_task"])
                    and _number(candidate["wall_seconds_per_task"])
                    <= _number(rival["wall_seconds_per_task"])
                )
                candidate_strict = (
                    _number(candidate["accepted_task_fraction"])
                    > _number(rival["accepted_task_fraction"])
                    or _number(candidate["provider_cost_usd_per_task"])
                    < _number(rival["provider_cost_usd_per_task"])
                    or _number(candidate["wall_seconds_per_task"])
                    < _number(rival["wall_seconds_per_task"])
                )
                if candidate_no_worse and candidate_strict:
                    dominates.append(rival["scenario_id"])
            result.append(
                {
                    "study": candidate["study"],
                    "design_point_id": candidate["design_point_id"],
                    "workload": candidate["workload"],
                    "scenario_id": candidate["scenario_id"],
                    "accepted_task_fraction": candidate["accepted_task_fraction"],
                    "provider_cost_usd_per_task": candidate["provider_cost_usd_per_task"],
                    "wall_seconds_per_task": candidate["wall_seconds_per_task"],
                    "pareto_frontier": not dominated_by,
                    "dominated_by_count": len(dominated_by),
                    "dominated_by_scenarios": ";".join(sorted(dominated_by)),
                    "dominates_count": len(dominates),
                    "dominates_scenarios": ";".join(sorted(dominates)),
                }
            )
    return sorted(result, key=lambda row: (row["study"], row["design_point_id"], row["scenario_id"]))


def _monthly_break_even_rows(
    workload_rows: list[dict[str, Any]], bundle: dict[str, Any]
) -> list[dict[str, Any]]:
    monthly_rows = [row for row in workload_rows if row["study"] == "monthly-economics"]
    by_point_scenario = {
        (row["design_point_id"], row["scenario_id"]): row for row in monthly_rows
    }
    point_metadata: dict[str, tuple[str, float]] = {}
    for point in bundle["spec"].get("designPoints", []):
        point_id = str(point["designPointId"])
        params = _parameter_map(point)
        workload = _workload_label(point_id, params)
        volume_value = params.get("billing_period_tasks", params.get("tasks_per_run"))
        if volume_value is None:
            raise AnalysisError(f"monthly design point {point_id} has no task volume")
        point_metadata[point_id] = (workload, _number(volume_value))

    baseline = "copilot-proplus-auto"
    comparison = "pi-openai-api-auto"
    rows: list[dict[str, Any]] = []
    curves: dict[str, list[tuple[float, float, str]]] = defaultdict(list)
    for point_id, (workload, volume) in sorted(point_metadata.items()):
        baseline_row = by_point_scenario.get((point_id, baseline))
        comparison_row = by_point_scenario.get((point_id, comparison))
        if baseline_row is None or comparison_row is None:
            raise AnalysisError(f"monthly design point {point_id} lacks break-even scenarios")
        baseline_cost = _number(baseline_row["allocated_cash_cost_usd_per_task"])
        comparison_cost = _number(comparison_row["allocated_cash_cost_usd_per_task"])
        delta = comparison_cost - baseline_cost
        if delta < 0.0:
            winner = comparison
        elif delta > 0.0:
            winner = baseline
        else:
            winner = "tie"
        curves[workload].append((volume, delta, point_id))
        rows.append(
            {
                "record_type": "design-point",
                "workload": workload,
                "design_point_id": point_id,
                "monthly_tasks": volume,
                "baseline_scenario_id": baseline,
                "comparison_scenario_id": comparison,
                "baseline_allocated_cash_usd_per_task": baseline_cost,
                "comparison_allocated_cash_usd_per_task": comparison_cost,
                "comparison_minus_baseline_usd_per_task": delta,
                "lower_cost_scenario": winner,
                "interpolated_break_even_monthly_tasks": "",
                "interpolation_status": "point-estimate-only",
            }
        )

    for workload, curve in sorted(curves.items()):
        curve.sort()
        crossing: float | None = None
        bracket = ""
        for (x0, y0, id0), (x1, y1, id1) in zip(curve, curve[1:]):
            if y0 == 0.0:
                crossing = x0
                bracket = id0
                break
            if y1 == 0.0:
                crossing = x1
                bracket = id1
                break
            if (y0 < 0.0 < y1) or (y1 < 0.0 < y0):
                crossing = x0 + (-y0) * (x1 - x0) / (y1 - y0)
                bracket = f"{id0};{id1}"
                break
        rows.append(
            {
                "record_type": "interpolation",
                "workload": workload,
                "design_point_id": bracket,
                "monthly_tasks": "",
                "baseline_scenario_id": baseline,
                "comparison_scenario_id": comparison,
                "baseline_allocated_cash_usd_per_task": "",
                "comparison_allocated_cash_usd_per_task": "",
                "comparison_minus_baseline_usd_per_task": "",
                "lower_cost_scenario": "",
                "interpolated_break_even_monthly_tasks": "" if crossing is None else crossing,
                "interpolation_status": (
                    "not-bracketed-by-comparable-design-points"
                    if crossing is None
                    else "linear-interpolation-model-conditional"
                ),
            }
        )
    return rows


def _metric_lookup(rows: list[dict[str, Any]]) -> dict[tuple[str, str, str, str], float]:
    return {
        (
            row["study"],
            row["design_group"],
            row["scenario_id"],
            row["outcome_name"],
        ): _number(row["mean"])
        for row in rows
    }


def _strongest_counterexample(pairwise_rows: list[dict[str, Any]]) -> dict[str, Any] | None:
    candidates: list[tuple[float, dict[str, Any]]] = []
    for row in pairwise_rows:
        if row["role"] != "challenge" or row["estimate_comparison_minus_baseline"] == "":
            continue
        estimate = _number(row["estimate_comparison_minus_baseline"])
        threshold = _number(row["threshold_value"])
        if row["threshold_operator"] == "le":
            opposition = estimate - threshold
        elif row["threshold_operator"] == "ge":
            opposition = threshold - estimate
        else:
            continue
        candidates.append((opposition, row))
    if not candidates:
        return None
    opposition, row = max(candidates, key=lambda item: (item[0], item[1]["design_point_id"]))
    return {"oppositionMargin": opposition, **row}


def _render_report(
    bundles: dict[str, dict[str, Any]],
    scenario_rows: list[dict[str, Any]],
    pairwise_rows: list[dict[str, Any]],
    break_even_rows: list[dict[str, Any]],
) -> str:
    lookup = _metric_lookup(scenario_rows)
    lines = [
        "# Harness efficiency simulation report",
        "",
        "All numerical comparisons below are conditional on the declared synthetic mechanism, parameter ranges, and rate-card snapshot. They are not empirical proof that one harness is better on real repositories.",
        "",
        "## Study-level summaries",
        "",
    ]
    for study_name in STUDY_NAMES:
        design_group = "primary" if study_name in {"controlled-harness", "usage-policy"} else "all"
        scenarios = [item["scenarioId"] for item in bundles[study_name]["spec"].get("scenarios", [])]
        ranked = sorted(
            scenarios,
            key=lambda scenario: (
                lookup.get((study_name, design_group, scenario, "normalized_cost_per_verified_work"), math.inf),
                -lookup.get((study_name, design_group, scenario, "accepted_task_fraction"), 0.0),
            ),
        )
        lines.append(f"### {study_name}")
        lines.append("")
        lines.append(f"Displayed cohort: `{design_group}` design points.")
        lines.append("")
        for scenario in ranked:
            acceptance = lookup.get((study_name, design_group, scenario, "accepted_task_fraction"), math.nan)
            provider = lookup.get((study_name, design_group, scenario, "provider_cost_usd_per_task"), math.nan)
            marginal = lookup.get((study_name, design_group, scenario, "marginal_cash_cost_usd_per_task"), math.nan)
            allocated = lookup.get((study_name, design_group, scenario, "allocated_cash_cost_usd_per_task"), math.nan)
            economic = lookup.get((study_name, design_group, scenario, "economic_loss_usd_per_task"), math.nan)
            wall = lookup.get((study_name, design_group, scenario, "wall_seconds_per_task"), math.nan)
            lines.append(
                f"- `{scenario}`: acceptance {acceptance:.3f}; provider ledger ${provider:.4f}/task; marginal cash ${marginal:.4f}/task; allocated cash ${allocated:.4f}/task; economic loss ${economic:.2f}/task; wall time {wall:.1f} s/task."
            )
        lines.append("")

    lines.extend(["## Preregistered hypotheses", ""])
    for study_name in STUDY_NAMES:
        lines.append(f"### {study_name}")
        lines.append("")
        for result in bundles[study_name]["hypothesis_results"].get("results", []):
            reversals = (result.get("challengeSearch") or {}).get("reversalDesignPointIds", [])
            suffix = f"; challenge reversals: {', '.join(reversals)}" if reversals else ""
            lines.append(f"- `{result['hypothesisId']}`: **{result['status']}**{suffix}.")
        lines.append("")

    counterexample = _strongest_counterexample(pairwise_rows)
    lines.extend(["## Strongest preregistered counterexample", ""])
    if counterexample and counterexample["oppositionMargin"] > 0.0:
        lines.append(
            "The largest threshold contradiction was "
            f"`{counterexample['study']}/{counterexample['design_point_id']}` for "
            f"`{counterexample['hypothesis_id']}`: comparison-minus-baseline "
            f"{_number(counterexample['estimate_comparison_minus_baseline']):.6g} versus "
            f"the `{counterexample['threshold_operator']}` threshold "
            f"{_number(counterexample['threshold_value']):.6g}."
        )
    elif counterexample:
        lines.append(
            "No preregistered challenge contradicted its threshold. The closest challenge was "
            f"`{counterexample['study']}/{counterexample['design_point_id']}`; this is a closest-to-threshold result, not a counterexample."
        )
    else:
        lines.append("No executable challenge contrast was present.")
    lines.append("")

    point_rows = [row for row in break_even_rows if row["record_type"] == "design-point"]
    lines.extend(["## Monthly economics boundary", ""])
    copilot_wins = sum(row["lower_cost_scenario"] == "copilot-proplus-auto" for row in point_rows)
    api_wins = sum(row["lower_cost_scenario"] == "pi-openai-api-auto" for row in point_rows)
    lines.append(
        f"Across {len(point_rows)} simulated monthly design points, allocated cash was lower for Copilot Pro+ in {copilot_wins}, for Pi with direct OpenAI API in {api_wins}, and tied in {len(point_rows) - copilot_wins - api_wins}. Interpolation rows are emitted only when comparable points bracket a crossover."
    )
    lines.extend(
        [
            "",
            "## Decision guidance under the model",
            "",
            "- Compare `harness × provider route × model × tool policy`; a product label alone is not an intervention.",
            "- Minimize the visible tool registry and retained tool output while preserving every tool the task actually requires.",
            "- Keep stable prompt prefixes and sessions within the cache lifetime; separately track cache reads and writes.",
            "- Route model strength by phase only when quality noninferiority survives the challenge points.",
            "- Choose subscriptions from expected monthly volume and allowance exhaustion, not from nominal token prices alone.",
            "- Validate on matched real repository tasks with a fixed external verifier before making a production-standard choice.",
            "",
            "## Exploration files",
            "",
            "Use `scenario-summary.csv` for portfolio averages, `workload-ranking.csv` for task-family slices, `pairwise-deltas.csv` for preregistered contrasts, `pareto-frontier.csv` for cost/quality/time trade-offs, and `break-even.csv` for monthly-plan decisions. Each original bundle also contains `analysis/explore.sql`, `analysis/summary.csv`, a data dictionary, and replication-level outcomes.",
            "",
        ]
    )
    return "\n".join(lines)


def analyze(runs_root: Path, output_dir: Path) -> dict[str, Any]:
    if output_dir.exists() and any(output_dir.iterdir()):
        raise AnalysisError(f"output directory must be fresh or empty: {output_dir}")
    output_dir.mkdir(parents=True, exist_ok=True)
    bundles = {
        study: _validate_bundle(study, runs_root / study) for study in STUDY_NAMES
    }

    scenario_rows = _scenario_summaries(bundles)
    workload_rows = _workload_rows(bundles)
    pairwise_rows = _pairwise_rows(bundles)
    pareto_rows = _pareto_rows(workload_rows)
    break_even_rows = _monthly_break_even_rows(
        workload_rows, bundles["monthly-economics"]
    )

    scenario_fields = [
        "study", "design_group", "scenario_id", "outcome_name", "n", "mean", "stddev", "mcse",
        "min", "p05", "median", "p95", "max",
    ]
    workload_fields = [
        "study", "design_point_id", "workload", "scenario_id", "tasks_per_run",
        "billing_period_tasks", "efficiency_rank_within_design_point", *KEY_METRICS,
    ]
    pairwise_fields = [
        "study", "hypothesis_id", "aggregate_status", "baseline_scenario_id",
        "comparison_scenario_id", "outcome_name", "design_point_id", "role",
        "point_status", "estimate_comparison_minus_baseline", "interval_low",
        "interval_high", "mcse", "threshold_operator", "threshold_value",
        "threshold_unit", "complete_pairs",
    ]
    pareto_fields = [
        "study", "design_point_id", "workload", "scenario_id",
        "accepted_task_fraction", "provider_cost_usd_per_task",
        "wall_seconds_per_task", "pareto_frontier", "dominated_by_count",
        "dominated_by_scenarios", "dominates_count", "dominates_scenarios",
    ]
    break_even_fields = [
        "record_type", "workload", "design_point_id", "monthly_tasks",
        "baseline_scenario_id", "comparison_scenario_id",
        "baseline_allocated_cash_usd_per_task",
        "comparison_allocated_cash_usd_per_task",
        "comparison_minus_baseline_usd_per_task", "lower_cost_scenario",
        "interpolated_break_even_monthly_tasks", "interpolation_status",
    ]
    _write_csv(output_dir / "scenario-summary.csv", scenario_rows, scenario_fields)
    _write_csv(output_dir / "workload-ranking.csv", workload_rows, workload_fields)
    _write_csv(output_dir / "pairwise-deltas.csv", pairwise_rows, pairwise_fields)
    _write_csv(output_dir / "pareto-frontier.csv", pareto_rows, pareto_fields)
    _write_csv(output_dir / "break-even.csv", break_even_rows, break_even_fields)

    counterexample = _strongest_counterexample(pairwise_rows)
    payload = {
        "schemaVersion": 1,
        "generatedAt": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "inferenceBoundary": (
            "Simulation-conditional only; real-world harness superiority is not identified."
        ),
        "studies": {
            name: {
                "experimentId": bundle["spec"]["experimentId"],
                "validationOk": True,
                "releaseEligible": True,
                "outcomeRows": len(bundle["outcomes"]),
                "summaryRows": len(bundle["summary"]),
                "hypotheses": [
                    {
                        "hypothesisId": item["hypothesisId"],
                        "status": item["status"],
                        "reversalDesignPointIds": (
                            item.get("challengeSearch") or {}
                        ).get("reversalDesignPointIds", []),
                    }
                    for item in bundle["hypothesis_results"].get("results", [])
                ],
                "inputHashes": bundle["hashes"],
            }
            for name, bundle in bundles.items()
        },
        "strongestPreregisteredCounterexample": counterexample,
        "outputRows": {
            "scenarioSummary": len(scenario_rows),
            "workloadRanking": len(workload_rows),
            "pairwiseDeltas": len(pairwise_rows),
            "paretoFrontier": len(pareto_rows),
            "breakEven": len(break_even_rows),
        },
    }
    (output_dir / "study-results.json").write_text(
        _canonical_json(payload), encoding="utf-8", newline=""
    )
    (output_dir / "report.md").write_text(
        _render_report(bundles, scenario_rows, pairwise_rows, break_even_rows),
        encoding="utf-8",
        newline="",
    )
    return payload


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Consolidate three validated harness-efficiency simulation bundles."
    )
    parser.add_argument(
        "--runs-root",
        type=Path,
        required=True,
        help="directory containing controlled-harness, monthly-economics, and usage-policy bundles",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        required=True,
        help="fresh output directory for consolidated tables and report",
    )
    return parser


def main() -> int:
    args = _build_parser().parse_args()
    try:
        result = analyze(args.runs_root.resolve(), args.output_dir.resolve())
    except (AnalysisError, OSError, ValueError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, sort_keys=True))
        return 2
    print(
        json.dumps(
            {
                "ok": True,
                "outputDirectory": str(args.output_dir.resolve()),
                "outputRows": result["outputRows"],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
