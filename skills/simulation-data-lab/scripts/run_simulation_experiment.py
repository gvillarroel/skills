#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

"""Plan and run engine-agnostic simulation experiments as tidy data bundles."""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import math
import platform
import re
import shutil
import statistics
import sys
import tempfile
import time
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from types import ModuleType
from typing import Any, Callable, Iterable

from model_variable_review import (
    build_variable_review_files,
    review_row_count,
    validate_variable_review,
)


SCHEMA_VERSION = 1
TOOL_VERSION = "1.0.0"
SEED_DERIVATION = "sha256-semantic-key-v1"
SEED_DOMAIN = "simulation-data-lab/run-seed/v1"
MAX_RUNS = 100_000
MAX_OUTCOMES = 100
# The local runner retains its run plan and all result tables in memory. Enforce
# one shared ceiling across planned core rows plus accumulated observations,
# events, and diagnostics; independent table maxima permit unsafe combinations.
MAX_IN_MEMORY_MATERIALIZED_ROWS = 1_000_000
MAX_RECORDS_PER_RUN = 10_000

ID_PATTERN = re.compile(r"^[a-z0-9][a-z0-9-]{0,62}[a-z0-9]$|^[a-z0-9]$")
NAME_PATTERN = re.compile(r"^[a-z][a-z0-9_]{0,62}$")
SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")

PARADIGMS = frozenset(
    {
        "monte-carlo",
        "discrete-event",
        "agent-based",
        "system-dynamics",
        "continuous-time",
        "hybrid",
        "custom",
    }
)
PHASES = frozenset({"pilot", "exploratory", "confirmatory", "robustness"})
UNCERTAINTY_MODES = frozenset({"stochastic", "deterministic"})
SEED_POLICIES = frozenset({"paired-across-scenarios", "independent-by-run"})
SOURCE_TYPES = frozenset({"assumed", "calibrated", "observed", "synthetic", "literature"})
CLAIM_SCOPES = frozenset(
    {"model-internal", "conditional-real-world", "empirically-calibrated"}
)
THRESHOLD_OPERATORS = frozenset({"ge", "le"})
ANALYSIS_KINDS = frozenset({"scenario-contrast", "not-identifiable"})
PAIRING_MODES = frozenset({"paired", "independent", "deterministic"})
REPRODUCIBILITY_LEVELS = frozenset(
    {"bitwise", "exact-within-locked-environment", "statistical-only"}
)

RUN_PLAN_COLUMNS = (
    "experiment_id",
    "run_id",
    "scenario_id",
    "design_point_id",
    "replicate_id",
    "coupling_id",
    "seed",
)
PARAMETER_COLUMNS = (
    "experiment_id",
    "owner_id",
    "parameter_name",
    "value_json",
    "unit",
    "source_type",
)
RUN_COLUMNS = (*RUN_PLAN_COLUMNS, "status", "error_type", "error_message")
OUTCOME_COLUMNS = (
    "experiment_id",
    "run_id",
    "scenario_id",
    "design_point_id",
    "replicate_id",
    "coupling_id",
    "outcome_name",
    "value",
    "unit",
    "source_type",
)
OBSERVATION_COLUMNS = (
    "experiment_id",
    "run_id",
    "scenario_id",
    "design_point_id",
    "replicate_id",
    "coupling_id",
    "observation_index",
    "sim_time",
    "time_unit",
    "entity_type",
    "entity_id",
    "variable",
    "value",
    "unit",
    "source_type",
    "is_warmup",
)
EVENT_COLUMNS = (
    "experiment_id",
    "run_id",
    "scenario_id",
    "design_point_id",
    "replicate_id",
    "coupling_id",
    "event_index",
    "sim_time",
    "time_unit",
    "entity_type",
    "entity_id",
    "event_type",
    "payload_json",
    "source_type",
)
DIAGNOSTIC_COLUMNS = (
    "experiment_id",
    "run_id",
    "scenario_id",
    "design_point_id",
    "replicate_id",
    "diagnostic_index",
    "check_id",
    "status",
    "value",
    "threshold",
    "invalidates_hypotheses",
    "message",
)
SUMMARY_COLUMNS = (
    "experiment_id",
    "scenario_id",
    "design_point_id",
    "outcome_name",
    "unit",
    "source_type",
    "n",
    "mean",
    "stddev",
    "mcse",
    "min",
    "p05",
    "median",
    "p95",
    "max",
)


class SimulationError(ValueError):
    """A safe, user-facing simulation contract error."""


def planned_core_row_count(
    run_count: int, design_cell_count: int, outcome_count: int
) -> int:
    """Conservatively count core rows retained together during execution."""

    return (
        run_count  # design/run-plan.csv, retained while the run executes
        + run_count  # data/runs.csv
        + run_count * outcome_count  # data/outcomes.csv
        + design_cell_count * outcome_count  # analysis/summary.csv upper bound
    )


def enforce_materialized_row_budget(
    planned_core_rows: int, optional_rows: int = 0
) -> None:
    """Reject a local run whose jointly materialized tables exceed the limit."""

    materialized_rows = planned_core_rows + optional_rows
    if materialized_rows > MAX_IN_MEMORY_MATERIALIZED_ROWS:
        raise SimulationError(
            f"experiment requires up to {materialized_rows} in-memory materialized rows "
            f"({planned_core_rows} planned core rows plus {optional_rows} observation, "
            "event, and diagnostic rows); the joint local-runner limit is "
            f"{MAX_IN_MEMORY_MATERIALIZED_ROWS}. Reduce runs, declared outcomes, or "
            "optional output, or use a streaming adapter"
        )


def canonical_json_bytes(value: Any) -> bytes:
    return (
        json.dumps(
            value,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
        + "\n"
    ).encode("utf-8")


def reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise SimulationError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def reject_json_constant(value: str) -> None:
    raise SimulationError(f"non-finite JSON constant is not allowed: {value}")


def load_json(path: Path, label: str) -> tuple[Any, bytes]:
    try:
        raw = path.read_bytes()
    except OSError as error:
        raise SimulationError(f"cannot read {label}: {error}") from error
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as error:
        raise SimulationError(f"{label} must be UTF-8") from error
    try:
        value = json.loads(
            text,
            object_pairs_hook=reject_duplicate_keys,
            parse_constant=reject_json_constant,
        )
    except SimulationError:
        raise
    except (json.JSONDecodeError, ValueError) as error:
        raise SimulationError(f"invalid {label} JSON: {error}") from error
    return value, raw


def sha256_bytes(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def require_object(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise SimulationError(f"{label} must be an object")
    return value


def require_list(value: Any, label: str) -> list[Any]:
    if not isinstance(value, list):
        raise SimulationError(f"{label} must be an array")
    return value


def require_text(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip() or "\x00" in value:
        raise SimulationError(f"{label} must be a non-empty string without NUL bytes")
    return value.strip()


def require_id(value: Any, label: str) -> str:
    text = require_text(value, label)
    if not ID_PATTERN.fullmatch(text):
        raise SimulationError(f"{label} must be lowercase hyphen-case and at most 64 characters")
    return text


def require_name(value: Any, label: str) -> str:
    text = require_text(value, label)
    if not NAME_PATTERN.fullmatch(text):
        raise SimulationError(f"{label} must be lowercase snake_case and at most 63 characters")
    return text


def require_exact_keys(
    value: dict[str, Any],
    required: set[str],
    label: str,
    optional: set[str] | None = None,
) -> None:
    allowed = required | (optional or set())
    missing = sorted(required - value.keys())
    extra = sorted(value.keys() - allowed)
    if missing:
        raise SimulationError(f"{label} is missing keys: {', '.join(missing)}")
    if extra:
        raise SimulationError(f"{label} has unknown keys: {', '.join(extra)}")


def require_finite_number(value: Any, label: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise SimulationError(f"{label} must be a finite number")
    number = float(value)
    if not math.isfinite(number):
        raise SimulationError(f"{label} must be finite")
    return number


def require_nonnegative_integer(value: Any, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise SimulationError(f"{label} must be a non-negative integer")
    return value


def require_positive_integer(value: Any, label: str) -> int:
    result = require_nonnegative_integer(value, label)
    if result == 0:
        raise SimulationError(f"{label} must be positive")
    return result


def normalize_json_value(value: Any, label: str) -> Any:
    if value is None or isinstance(value, (str, bool, int)):
        return value
    if isinstance(value, float):
        if not math.isfinite(value):
            raise SimulationError(f"{label} must not contain NaN or infinity")
        return value
    if isinstance(value, list):
        return [normalize_json_value(item, f"{label}[{index}]") for index, item in enumerate(value)]
    if isinstance(value, dict):
        normalized: dict[str, Any] = {}
        for key in sorted(value):
            if not isinstance(key, str) or not key or "\x00" in key:
                raise SimulationError(f"{label} object keys must be non-empty strings")
            normalized[key] = normalize_json_value(value[key], f"{label}.{key}")
        return normalized
    raise SimulationError(f"{label} contains an unsupported JSON value")


def normalize_parameters(value: Any, label: str) -> list[dict[str, Any]]:
    parameters = require_list(value, label)
    seen: set[str] = set()
    normalized: list[dict[str, Any]] = []
    for index, raw in enumerate(parameters):
        item_label = f"{label}[{index}]"
        parameter = require_object(raw, item_label)
        require_exact_keys(
            parameter,
            {"name", "value", "unit", "sourceType"},
            item_label,
            {"description"},
        )
        name = require_name(parameter["name"], f"{item_label}.name")
        if name in seen:
            raise SimulationError(f"duplicate parameter name in {label}: {name}")
        seen.add(name)
        source_type = require_text(parameter["sourceType"], f"{item_label}.sourceType")
        if source_type not in SOURCE_TYPES:
            raise SimulationError(
                f"{item_label}.sourceType must be one of: {', '.join(sorted(SOURCE_TYPES))}"
            )
        normalized.append(
            {
                "name": name,
                "value": normalize_json_value(parameter["value"], f"{item_label}.value"),
                "unit": require_text(parameter["unit"], f"{item_label}.unit"),
                "sourceType": source_type,
                **(
                    {"description": require_text(parameter["description"], f"{item_label}.description")}
                    if "description" in parameter
                    else {}
                ),
            }
        )
    return sorted(normalized, key=lambda item: item["name"])


def model_visible_parameter_maps(parameters: list[dict[str, Any]]) -> dict[str, Any]:
    """Return exactly the parameter maps exposed to ``simulate(run)``."""

    return {
        "parameters": {item["name"]: item["value"] for item in parameters},
        "parameter_units": {item["name"]: item["unit"] for item in parameters},
        "parameter_sources": {item["name"]: item["sourceType"] for item in parameters},
    }


def normalize_spec(value: Any) -> dict[str, Any]:
    spec = require_object(value, "experiment")
    require_exact_keys(
        spec,
        {
            "schemaVersion",
            "experimentId",
            "title",
            "phase",
            "paradigm",
            "engine",
            "rootSeed",
            "uncertaintyMode",
            "seedPolicy",
            "replications",
            "scenarios",
            "designPoints",
            "outcomes",
            "hypotheses",
            "assumptions",
        },
        "experiment",
        {"description", "extensions", "timeUnit"},
    )
    schema_version = spec["schemaVersion"]
    if type(schema_version) is not int or schema_version != SCHEMA_VERSION:
        raise SimulationError(
            f"experiment.schemaVersion must be the integer {SCHEMA_VERSION}"
        )
    experiment_id = require_id(spec["experimentId"], "experiment.experimentId")
    phase = require_text(spec["phase"], "experiment.phase")
    if phase not in PHASES:
        raise SimulationError(f"experiment.phase must be one of: {', '.join(sorted(PHASES))}")
    paradigm = require_text(spec["paradigm"], "experiment.paradigm")
    if paradigm not in PARADIGMS:
        raise SimulationError(
            f"experiment.paradigm must be one of: {', '.join(sorted(PARADIGMS))}"
        )
    engine = require_object(spec["engine"], "experiment.engine")
    require_exact_keys(engine, {"name"}, "experiment.engine", {"versionConstraint"})
    normalized_engine = {"name": require_id(engine["name"], "experiment.engine.name")}
    if "versionConstraint" in engine:
        normalized_engine["versionConstraint"] = require_text(
            engine["versionConstraint"], "experiment.engine.versionConstraint"
        )
    root_seed = require_nonnegative_integer(spec["rootSeed"], "experiment.rootSeed")
    if root_seed > 2**53 - 1:
        raise SimulationError("experiment.rootSeed must not exceed 2^53-1 for JSON interoperability")
    uncertainty_mode = require_text(spec["uncertaintyMode"], "experiment.uncertaintyMode")
    if uncertainty_mode not in UNCERTAINTY_MODES:
        raise SimulationError(
            "experiment.uncertaintyMode must be one of: "
            + ", ".join(sorted(UNCERTAINTY_MODES))
        )
    seed_policy = require_text(spec["seedPolicy"], "experiment.seedPolicy")
    if seed_policy not in SEED_POLICIES:
        raise SimulationError(
            f"experiment.seedPolicy must be one of: {', '.join(sorted(SEED_POLICIES))}"
        )
    replications = require_positive_integer(spec["replications"], "experiment.replications")
    if uncertainty_mode == "deterministic" and replications != 1:
        raise SimulationError("deterministic experiments must use exactly one replication")
    if uncertainty_mode == "deterministic" and seed_policy != "independent-by-run":
        raise SimulationError("deterministic experiments must use seedPolicy independent-by-run")

    scenario_values = require_list(spec["scenarios"], "experiment.scenarios")
    if not scenario_values:
        raise SimulationError("experiment.scenarios must not be empty")
    scenarios: list[dict[str, Any]] = []
    scenario_ids: set[str] = set()
    for index, raw in enumerate(scenario_values):
        label = f"experiment.scenarios[{index}]"
        scenario = require_object(raw, label)
        require_exact_keys(
            scenario,
            {"scenarioId", "label", "parameters"},
            label,
            {"description", "tags"},
        )
        scenario_id = require_id(scenario["scenarioId"], f"{label}.scenarioId")
        if scenario_id in scenario_ids:
            raise SimulationError(f"duplicate scenarioId: {scenario_id}")
        scenario_ids.add(scenario_id)
        item: dict[str, Any] = {
            "scenarioId": scenario_id,
            "label": require_text(scenario["label"], f"{label}.label"),
            "parameters": normalize_parameters(scenario["parameters"], f"{label}.parameters"),
        }
        if "description" in scenario:
            item["description"] = require_text(scenario["description"], f"{label}.description")
        if "tags" in scenario:
            tags = [require_id(tag, f"{label}.tags") for tag in require_list(scenario["tags"], f"{label}.tags")]
            if len(tags) != len(set(tags)):
                raise SimulationError(f"{label}.tags contains duplicates")
            item["tags"] = sorted(tags)
        scenarios.append(item)

    design_values = require_list(spec["designPoints"], "experiment.designPoints")
    if not design_values:
        raise SimulationError("experiment.designPoints must not be empty")
    design_points: list[dict[str, Any]] = []
    design_ids: set[str] = set()
    for index, raw in enumerate(design_values):
        label = f"experiment.designPoints[{index}]"
        point = require_object(raw, label)
        require_exact_keys(point, {"designPointId", "parameters"}, label, {"description"})
        design_id = require_id(point["designPointId"], f"{label}.designPointId")
        if design_id in design_ids:
            raise SimulationError(f"duplicate designPointId: {design_id}")
        design_ids.add(design_id)
        item = {
            "designPointId": design_id,
            "parameters": normalize_parameters(point["parameters"], f"{label}.parameters"),
        }
        if "description" in point:
            item["description"] = require_text(point["description"], f"{label}.description")
        design_points.append(item)

    for scenario in scenarios:
        scenario_names = {item["name"] for item in scenario["parameters"]}
        for point in design_points:
            overlap = sorted(scenario_names & {item["name"] for item in point["parameters"]})
            if overlap:
                raise SimulationError(
                    f"scenario {scenario['scenarioId']} and design point {point['designPointId']} "
                    f"define the same parameters: {', '.join(overlap)}"
                )

    outcome_values = require_list(spec["outcomes"], "experiment.outcomes")
    if not outcome_values:
        raise SimulationError("experiment.outcomes must not be empty")
    if len(outcome_values) > MAX_OUTCOMES:
        raise SimulationError(f"experiment.outcomes exceeds the schema v1 limit of {MAX_OUTCOMES}")
    outcomes: list[dict[str, str]] = []
    outcome_names: set[str] = set()
    for index, raw in enumerate(outcome_values):
        label = f"experiment.outcomes[{index}]"
        outcome = require_object(raw, label)
        require_exact_keys(outcome, {"name", "unit", "description"}, label)
        name = require_name(outcome["name"], f"{label}.name")
        if name in outcome_names:
            raise SimulationError(f"duplicate outcome name: {name}")
        outcome_names.add(name)
        outcomes.append(
            {
                "name": name,
                "unit": require_text(outcome["unit"], f"{label}.unit"),
                "description": require_text(outcome["description"], f"{label}.description"),
            }
        )

    assumption_values = require_list(spec["assumptions"], "experiment.assumptions")
    assumptions: list[dict[str, str]] = []
    assumption_ids: set[str] = set()
    for index, raw in enumerate(assumption_values):
        label = f"experiment.assumptions[{index}]"
        assumption = require_object(raw, label)
        require_exact_keys(assumption, {"assumptionId", "statement", "sourceType"}, label)
        assumption_id = require_id(assumption["assumptionId"], f"{label}.assumptionId")
        if assumption_id in assumption_ids:
            raise SimulationError(f"duplicate assumptionId: {assumption_id}")
        assumption_ids.add(assumption_id)
        source_type = require_text(assumption["sourceType"], f"{label}.sourceType")
        if source_type not in SOURCE_TYPES:
            raise SimulationError(
                f"{label}.sourceType must be one of: {', '.join(sorted(SOURCE_TYPES))}"
            )
        assumptions.append(
            {
                "assumptionId": assumption_id,
                "statement": require_text(assumption["statement"], f"{label}.statement"),
                "sourceType": source_type,
            }
        )

    hypothesis_values = require_list(spec["hypotheses"], "experiment.hypotheses")
    hypotheses: list[dict[str, Any]] = []
    hypothesis_ids: set[str] = set()
    for index, raw in enumerate(hypothesis_values):
        label = f"experiment.hypotheses[{index}]"
        hypothesis = require_object(raw, label)
        require_exact_keys(
            hypothesis,
            {
                "hypothesisId",
                "claim",
                "claimScope",
                "assumptionIds",
                "externalValidationRequired",
                "outcome",
                "scenarioIds",
                "estimand",
                "analysis",
                "practicalThreshold",
                "decisionRule",
                "falsificationRule",
            },
            label,
        )
        hypothesis_id = require_id(hypothesis["hypothesisId"], f"{label}.hypothesisId")
        if hypothesis_id in hypothesis_ids:
            raise SimulationError(f"duplicate hypothesisId: {hypothesis_id}")
        hypothesis_ids.add(hypothesis_id)
        claim_scope = require_text(hypothesis["claimScope"], f"{label}.claimScope")
        if claim_scope not in CLAIM_SCOPES:
            raise SimulationError(
                f"{label}.claimScope must be one of: {', '.join(sorted(CLAIM_SCOPES))}"
            )
        used_assumptions = [
            require_id(item, f"{label}.assumptionIds")
            for item in require_list(hypothesis["assumptionIds"], f"{label}.assumptionIds")
        ]
        if len(used_assumptions) != len(set(used_assumptions)):
            raise SimulationError(f"{label}.assumptionIds contains duplicates")
        unknown_assumptions = sorted(set(used_assumptions) - assumption_ids)
        if unknown_assumptions:
            raise SimulationError(
                f"{label}.assumptionIds references unknown assumptions: {', '.join(unknown_assumptions)}"
            )
        outcome = require_name(hypothesis["outcome"], f"{label}.outcome")
        if outcome not in outcome_names:
            raise SimulationError(f"{label}.outcome references an unknown outcome: {outcome}")
        used_scenarios = [
            require_id(item, f"{label}.scenarioIds")
            for item in require_list(hypothesis["scenarioIds"], f"{label}.scenarioIds")
        ]
        if not used_scenarios:
            raise SimulationError(f"{label}.scenarioIds must not be empty")
        if len(used_scenarios) != len(set(used_scenarios)):
            raise SimulationError(f"{label}.scenarioIds contains duplicates")
        unknown_scenarios = sorted(set(used_scenarios) - scenario_ids)
        if unknown_scenarios:
            raise SimulationError(
                f"{label}.scenarioIds references unknown scenarios: {', '.join(unknown_scenarios)}"
            )
        raw_analysis = require_object(hypothesis["analysis"], f"{label}.analysis")
        analysis_kind = require_text(raw_analysis.get("kind"), f"{label}.analysis.kind")
        if analysis_kind not in ANALYSIS_KINDS:
            raise SimulationError(
                f"{label}.analysis.kind must be one of: {', '.join(sorted(ANALYSIS_KINDS))}"
            )
        if analysis_kind == "not-identifiable":
            require_exact_keys(raw_analysis, {"kind", "reason"}, f"{label}.analysis")
            normalized_analysis: dict[str, Any] = {
                "kind": analysis_kind,
                "reason": require_text(raw_analysis["reason"], f"{label}.analysis.reason"),
            }
        else:
            require_exact_keys(
                raw_analysis,
                {
                    "kind",
                    "estimator",
                    "baselineScenarioId",
                    "comparisonScenarioId",
                    "primaryDesignPointIds",
                    "challengeDesignPointIds",
                    "pairing",
                    "intervalMethod",
                    "intervalLevel",
                    "aggregationRule",
                },
                f"{label}.analysis",
                optional={"outcomeBounds"},
            )
            estimator = require_text(raw_analysis["estimator"], f"{label}.analysis.estimator")
            if estimator != "mean-difference":
                raise SimulationError(f"{label}.analysis.estimator must be mean-difference in schema v1")
            baseline = require_id(
                raw_analysis["baselineScenarioId"], f"{label}.analysis.baselineScenarioId"
            )
            comparison = require_id(
                raw_analysis["comparisonScenarioId"], f"{label}.analysis.comparisonScenarioId"
            )
            if baseline == comparison:
                raise SimulationError(f"{label}.analysis scenarios must be distinct")
            if {baseline, comparison} != set(used_scenarios) or len(used_scenarios) != 2:
                raise SimulationError(
                    f"{label}.scenarioIds must contain exactly the baseline and comparison scenarios"
                )
            primary_ids = [
                require_id(item, f"{label}.analysis.primaryDesignPointIds")
                for item in require_list(
                    raw_analysis["primaryDesignPointIds"],
                    f"{label}.analysis.primaryDesignPointIds",
                )
            ]
            challenge_ids = [
                require_id(item, f"{label}.analysis.challengeDesignPointIds")
                for item in require_list(
                    raw_analysis["challengeDesignPointIds"],
                    f"{label}.analysis.challengeDesignPointIds",
                )
            ]
            if not primary_ids:
                raise SimulationError(f"{label}.analysis.primaryDesignPointIds must not be empty")
            if not challenge_ids:
                raise SimulationError(
                    f"{label}.analysis.challengeDesignPointIds must include a preregistered challenge"
                )
            if len(primary_ids) != len(set(primary_ids)) or len(challenge_ids) != len(set(challenge_ids)):
                raise SimulationError(f"{label}.analysis design-point IDs must be unique")
            if set(primary_ids) & set(challenge_ids):
                raise SimulationError(f"{label}.analysis primary and challenge design points must be disjoint")
            unknown_designs = sorted((set(primary_ids) | set(challenge_ids)) - design_ids)
            if unknown_designs:
                raise SimulationError(
                    f"{label}.analysis references unknown design points: {', '.join(unknown_designs)}"
                )
            omitted_designs = sorted(design_ids - (set(primary_ids) | set(challenge_ids)))
            if omitted_designs:
                raise SimulationError(
                    f"{label}.analysis must classify every design point; omitted: "
                    + ", ".join(omitted_designs)
                )
            points_by_id = {item["designPointId"]: item for item in design_points}
            primary_parameter_value_maps = {
                canonical_json_bytes(
                    model_visible_parameter_maps(points_by_id[design_id]["parameters"])[
                        "parameters"
                    ]
                )
                for design_id in primary_ids
            }
            for design_id in challenge_ids:
                challenge_parameter_value_map = canonical_json_bytes(
                    model_visible_parameter_maps(points_by_id[design_id]["parameters"])[
                        "parameters"
                    ]
                )
                if challenge_parameter_value_map in primary_parameter_value_maps:
                    raise SimulationError(
                        f"{label}.analysis challenge design point {design_id} must differ "
                        "from every primary model parameter value map"
                    )
            pairing = require_text(raw_analysis["pairing"], f"{label}.analysis.pairing")
            if pairing not in PAIRING_MODES:
                raise SimulationError(
                    f"{label}.analysis.pairing must be one of: {', '.join(sorted(PAIRING_MODES))}"
                )
            interval_method = require_text(
                raw_analysis["intervalMethod"], f"{label}.analysis.intervalMethod"
            )
            interval_level = raw_analysis["intervalLevel"]
            if uncertainty_mode == "deterministic":
                if pairing != "deterministic" or interval_method != "none" or interval_level is not None:
                    raise SimulationError(
                        f"{label}.analysis must use deterministic pairing, intervalMethod none, "
                        "and null intervalLevel for a deterministic experiment"
                    )
            else:
                if pairing == "deterministic":
                    raise SimulationError(f"{label}.analysis cannot use deterministic pairing")
                expected_seed_policy = (
                    "paired-across-scenarios" if pairing == "paired" else "independent-by-run"
                )
                if seed_policy != expected_seed_policy:
                    raise SimulationError(
                        f"{label}.analysis pairing requires seedPolicy {expected_seed_policy}"
                    )
                if interval_method not in {
                    "normal-approximation", "normal-approximation-bonferroni",
                    "bounded-hoeffding-bonferroni",
                }:
                    raise SimulationError(
                        f"{label}.analysis.intervalMethod must be normal-approximation "
                        "or normal-approximation-bonferroni or bounded-hoeffding-bonferroni"
                    )
                interval_level = require_finite_number(
                    interval_level, f"{label}.analysis.intervalLevel"
                )
                if not 0 < interval_level < 1:
                    raise SimulationError(f"{label}.analysis.intervalLevel must be between 0 and 1")
                if replications < 2:
                    raise SimulationError(
                        f"{label}.analysis requires at least two stochastic replications"
                    )
            aggregation_rule = require_text(
                raw_analysis["aggregationRule"], f"{label}.analysis.aggregationRule"
            )
            if aggregation_rule != "all-design-points":
                raise SimulationError(
                    f"{label}.analysis.aggregationRule must be all-design-points in schema v1"
                )
            normalized_analysis = {
                "kind": analysis_kind,
                "estimator": estimator,
                "baselineScenarioId": baseline,
                "comparisonScenarioId": comparison,
                "primaryDesignPointIds": sorted(primary_ids),
                "challengeDesignPointIds": sorted(challenge_ids),
                "pairing": pairing,
                "intervalMethod": interval_method,
                "intervalLevel": interval_level,
                "aggregationRule": aggregation_rule,
            }
            if interval_method == "bounded-hoeffding-bonferroni":
                bounds_label = f"{label}.analysis.outcomeBounds"
                bounds = require_object(raw_analysis.get("outcomeBounds"), bounds_label)
                require_exact_keys(bounds, {"baseline", "comparison", "assumptionId"}, bounds_label)
                support_assumption = require_id(bounds["assumptionId"], f"{bounds_label}.assumptionId")
                if support_assumption not in used_assumptions:
                    raise SimulationError(f"{bounds_label}.assumptionId must be in hypothesis.assumptionIds")
                normalized_bounds: dict[str, Any] = {"assumptionId": support_assumption}
                for arm in ("baseline", "comparison"):
                    arm_bounds = require_object(bounds[arm], f"{bounds_label}.{arm}")
                    require_exact_keys(arm_bounds, {"low", "high"}, f"{bounds_label}.{arm}")
                    low = require_finite_number(arm_bounds["low"], f"{bounds_label}.{arm}.low")
                    high = require_finite_number(arm_bounds["high"], f"{bounds_label}.{arm}.high")
                    if low > high or not math.isfinite(high - low):
                        raise SimulationError(f"{bounds_label}.{arm} must have ordered, finite-width support")
                    normalized_bounds[arm] = {"low": low, "high": high}
                left, right = normalized_bounds["baseline"], normalized_bounds["comparison"]
                contrast_low = right["low"] - left["high"]
                contrast_high = right["high"] - left["low"]
                if not all(math.isfinite(number) for number in (
                    contrast_low, contrast_high, contrast_high - contrast_low,
                )):
                    raise SimulationError(f"{bounds_label} must give finite-width contrast support")
                normalized_analysis["outcomeBounds"] = normalized_bounds
            elif "outcomeBounds" in raw_analysis:
                raise SimulationError(f"{label}.analysis.outcomeBounds requires bounded-hoeffding-bonferroni")
        threshold = require_object(hypothesis["practicalThreshold"], f"{label}.practicalThreshold")
        require_exact_keys(threshold, {"value", "unit", "operator"}, f"{label}.practicalThreshold")
        operator = require_text(threshold["operator"], f"{label}.practicalThreshold.operator")
        if operator not in THRESHOLD_OPERATORS:
            raise SimulationError(
                f"{label}.practicalThreshold.operator must be one of: "
                f"{', '.join(sorted(THRESHOLD_OPERATORS))}"
            )
        threshold_unit = require_text(threshold["unit"], f"{label}.practicalThreshold.unit")
        outcome_unit = next(item["unit"] for item in outcomes if item["name"] == outcome)
        if threshold_unit != outcome_unit:
            raise SimulationError(
                f"{label}.practicalThreshold.unit must match outcome {outcome!r} unit {outcome_unit!r}"
            )
        external_required = hypothesis["externalValidationRequired"]
        if not isinstance(external_required, bool):
            raise SimulationError(f"{label}.externalValidationRequired must be boolean")
        hypotheses.append(
            {
                "hypothesisId": hypothesis_id,
                "claim": require_text(hypothesis["claim"], f"{label}.claim"),
                "claimScope": claim_scope,
                "assumptionIds": used_assumptions,
                "externalValidationRequired": external_required,
                "outcome": outcome,
                "scenarioIds": used_scenarios,
                "estimand": require_text(hypothesis["estimand"], f"{label}.estimand"),
                "analysis": normalized_analysis,
                "practicalThreshold": {
                    "value": require_finite_number(
                        threshold["value"], f"{label}.practicalThreshold.value"
                    ),
                    "unit": threshold_unit,
                    "operator": operator,
                },
                "decisionRule": require_text(hypothesis["decisionRule"], f"{label}.decisionRule"),
                "falsificationRule": require_text(
                    hypothesis["falsificationRule"], f"{label}.falsificationRule"
                ),
            }
        )

    run_count = len(scenarios) * len(design_points) * replications
    if run_count > MAX_RUNS:
        raise SimulationError(
            f"experiment expands to {run_count} runs; the planner limit is {MAX_RUNS}"
        )
    design_cell_count = len(scenarios) * len(design_points)
    core_row_count = planned_core_row_count(
        run_count, design_cell_count, len(outcomes)
    )
    enforce_materialized_row_budget(core_row_count)
    normalized: dict[str, Any] = {
        "schemaVersion": SCHEMA_VERSION,
        "experimentId": experiment_id,
        "title": require_text(spec["title"], "experiment.title"),
        "phase": phase,
        "paradigm": paradigm,
        "engine": normalized_engine,
        "rootSeed": root_seed,
        "uncertaintyMode": uncertainty_mode,
        "seedPolicy": seed_policy,
        "replications": replications,
        "scenarios": sorted(scenarios, key=lambda item: item["scenarioId"]),
        "designPoints": sorted(design_points, key=lambda item: item["designPointId"]),
        "outcomes": sorted(outcomes, key=lambda item: item["name"]),
        "hypotheses": sorted(hypotheses, key=lambda item: item["hypothesisId"]),
        "assumptions": sorted(assumptions, key=lambda item: item["assumptionId"]),
    }
    if "description" in spec:
        normalized["description"] = require_text(spec["description"], "experiment.description")
    if "timeUnit" in spec:
        normalized["timeUnit"] = require_text(spec["timeUnit"], "experiment.timeUnit")
    if "extensions" in spec:
        normalized["extensions"] = normalize_json_value(spec["extensions"], "experiment.extensions")
    try:
        validate_variable_review(normalized)
    except ValueError as error:
        raise SimulationError(str(error)) from error
    enforce_materialized_row_budget(core_row_count + review_row_count(normalized))
    return normalized


def semantic_seed(root_seed: int, *parts: str) -> int:
    payload = "\0".join((SEED_DOMAIN, str(root_seed), *parts)).encode("utf-8")
    return int.from_bytes(hashlib.sha256(payload).digest()[:8], "big") & ((1 << 63) - 1)


def stable_token(*parts: str, length: int = 12) -> str:
    return hashlib.sha256("\0".join(parts).encode("utf-8")).hexdigest()[:length]


def csv_bytes(columns: Iterable[str], rows: Iterable[dict[str, Any]]) -> bytes:
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(
        buffer,
        fieldnames=list(columns),
        extrasaction="raise",
        lineterminator="\n",
    )
    writer.writeheader()
    for row in rows:
        writer.writerow(row)
    return buffer.getvalue().encode("utf-8")


def build_plan(spec: dict[str, Any]) -> dict[str, bytes]:
    experiment_id = spec["experimentId"]
    run_rows: list[dict[str, Any]] = []
    for scenario in spec["scenarios"]:
        scenario_id = scenario["scenarioId"]
        for point in spec["designPoints"]:
            design_id = point["designPointId"]
            for replicate_id in range(1, spec["replications"] + 1):
                pair_key = f"{design_id}:r{replicate_id:06d}"
                if spec["seedPolicy"] == "paired-across-scenarios":
                    seed_parts = (experiment_id, design_id, str(replicate_id), "simulation")
                    coupling_id = f"paired-{stable_token(experiment_id, pair_key, length=24)}"
                else:
                    seed_parts = (
                        experiment_id,
                        scenario_id,
                        design_id,
                        str(replicate_id),
                        "simulation",
                    )
                    coupling_id = (
                        "independent-"
                        f"{stable_token(experiment_id, scenario_id, pair_key, length=24)}"
                    )
                run_id = (
                    f"{scenario_id}-{design_id}-r{replicate_id:06d}-"
                    f"{stable_token(experiment_id, scenario_id, design_id, str(replicate_id), length=8)}"
                )
                run_rows.append(
                    {
                        "experiment_id": experiment_id,
                        "run_id": run_id,
                        "scenario_id": scenario_id,
                        "design_point_id": design_id,
                        "replicate_id": replicate_id,
                        "coupling_id": coupling_id,
                        "seed": semantic_seed(spec["rootSeed"], *seed_parts),
                    }
                )
    scenario_rows = [
        {
            "experiment_id": experiment_id,
            "owner_id": scenario["scenarioId"],
            "parameter_name": parameter["name"],
            "value_json": canonical_json_bytes(parameter["value"]).decode("utf-8").rstrip("\n"),
            "unit": parameter["unit"],
            "source_type": parameter["sourceType"],
        }
        for scenario in spec["scenarios"]
        for parameter in scenario["parameters"]
    ]
    design_rows = [
        {
            "experiment_id": experiment_id,
            "owner_id": point["designPointId"],
            "parameter_name": parameter["name"],
            "value_json": canonical_json_bytes(parameter["value"]).decode("utf-8").rstrip("\n"),
            "unit": parameter["unit"],
            "source_type": parameter["sourceType"],
        }
        for point in spec["designPoints"]
        for parameter in point["parameters"]
    ]
    files = {
        "run-plan.csv": csv_bytes(RUN_PLAN_COLUMNS, run_rows),
        "scenario-factors.csv": csv_bytes(PARAMETER_COLUMNS, scenario_rows),
        "design-point-parameters.csv": csv_bytes(PARAMETER_COLUMNS, design_rows),
    }
    files.update(build_variable_review_files(spec))
    return files


def build_plan_manifest(spec: dict[str, Any], spec_raw: bytes, files: dict[str, bytes]) -> dict[str, Any]:
    records = []
    for name, raw in sorted(files.items()):
        record = {"path": name, "sha256": sha256_bytes(raw)}
        if name.endswith(".csv"):
            record["rows"] = max(
                0, len(list(csv.reader(io.StringIO(raw.decode("utf-8"), newline="")))) - 1,
            )
        records.append(record)
    return {
        "schemaVersion": SCHEMA_VERSION,
        "toolVersion": TOOL_VERSION,
        "experimentId": spec["experimentId"],
        "runCount": len(spec["scenarios"]) * len(spec["designPoints"]) * spec["replications"],
        "scenarioCount": len(spec["scenarios"]),
        "designPointCount": len(spec["designPoints"]),
        "replicationsPerDesignPoint": spec["replications"],
        "uncertaintyMode": spec["uncertaintyMode"],
        "seedPolicy": spec["seedPolicy"],
        "seedDerivation": SEED_DERIVATION,
        "specSha256": sha256_bytes(spec_raw),
        "normalizedSpecSha256": sha256_bytes(canonical_json_bytes(spec)),
        "files": records,
    }


def read_csv(path: Path, columns: Iterable[str], label: str) -> list[dict[str, str]]:
    try:
        with path.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            expected = list(columns)
            if reader.fieldnames != expected:
                raise SimulationError(
                    f"{label} columns differ; expected {expected}, found {reader.fieldnames}"
                )
            rows = list(reader)
            if any(None in row for row in rows):
                raise SimulationError(f"{label} contains cells beyond its declared columns")
    except UnicodeDecodeError as error:
        raise SimulationError(f"{label} must be UTF-8") from error
    except OSError as error:
        raise SimulationError(f"cannot read {label}: {error}") from error
    return rows


def verify_plan(root: Path) -> tuple[dict[str, Any], bytes, list[dict[str, str]]]:
    spec_value, spec_raw = load_json(root / "experiment.json", "experiment.json")
    spec = normalize_spec(spec_value)
    design = root / "design"
    manifest_value, manifest_raw = load_json(design / "plan-manifest.json", "design/plan-manifest.json")
    manifest = require_object(manifest_value, "design/plan-manifest.json")
    expected_files = build_plan(spec)
    expected_manifest = build_plan_manifest(spec, spec_raw, expected_files)
    canonical_manifest_raw = canonical_json_bytes(manifest)
    if manifest_raw != canonical_manifest_raw:
        raise SimulationError("design/plan-manifest.json must use canonical JSON")
    # Compare canonical bytes, not Python values: bool, int, and float values
    # such as true, 1, and 1.0 can compare equal despite distinct JSON types.
    if canonical_manifest_raw != canonical_json_bytes(expected_manifest):
        raise SimulationError(
            "design/plan-manifest.json does not match experiment.json and the deterministic plan"
        )
    for name, expected_raw in expected_files.items():
        try:
            observed = (design / name).read_bytes()
        except OSError as error:
            raise SimulationError(f"cannot read design/{name}: {error}") from error
        if observed != expected_raw:
            raise SimulationError(f"design/{name} does not reproduce from experiment.json")
    rows = read_csv(design / "run-plan.csv", RUN_PLAN_COLUMNS, "design/run-plan.csv")
    return spec, spec_raw, rows


def command_plan(args: argparse.Namespace) -> int:
    value, raw = load_json(args.spec.resolve(), "experiment spec")
    spec = normalize_spec(value)
    if getattr(args, "require_variable_review", False) and validate_variable_review(spec) is None:
        raise SimulationError("new studies require extensions.simulation-data-lab.variableReview")
    files = build_plan(spec)
    manifest = build_plan_manifest(spec, raw, files)
    output = args.output_dir.resolve()
    if output.exists():
        raise SimulationError("output directory already exists; choose a fresh path")
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary: Path | None = None
    try:
        temporary = Path(tempfile.mkdtemp(prefix=f".{output.name}.tmp-", dir=output.parent))
        for name, content in files.items():
            (temporary / name).write_bytes(content)
        (temporary / "plan-manifest.json").write_bytes(canonical_json_bytes(manifest))
        if output.exists():
            raise SimulationError("output directory appeared while planning; nothing was replaced")
        temporary.replace(output)
        temporary = None
    except OSError as error:
        raise SimulationError(f"cannot publish plan: {error}") from error
    finally:
        if temporary is not None and temporary.exists():
            shutil.rmtree(temporary, ignore_errors=True)
    sys.stdout.buffer.write(
        canonical_json_bytes(
            {
                "ok": True,
                "experimentId": spec["experimentId"],
                "runCount": manifest["runCount"],
                "outputDirectory": str(output),
                "files": [*sorted(files), "plan-manifest.json"],
            }
        )
    )
    return 0


def safe_bundle_path(root: Path, raw: str, label: str) -> tuple[str, Path]:
    text = require_text(raw, label)
    if "\\" in text:
        raise SimulationError(f"{label} must use forward slashes")
    pure = PurePosixPath(text)
    if pure.is_absolute() or any(
        part in {"", ".", ".."} or ":" in part for part in pure.parts
    ):
        raise SimulationError(f"{label} must be a safe relative path")
    normalized = pure.as_posix()
    candidate = (root / Path(*pure.parts)).resolve()
    try:
        candidate.relative_to(root.resolve())
    except ValueError as error:
        raise SimulationError(f"{label} resolves outside the bundle") from error
    return normalized, candidate


def load_model(
    root: Path, model_path: str
) -> tuple[ModuleType, str, Path, str, dict[str, str]]:
    normalized_path, path = safe_bundle_path(root, model_path, "model path")
    if not path.is_file():
        raise SimulationError(f"model file does not exist: {normalized_path}")
    try:
        source_bytes = path.read_bytes()
    except OSError as error:
        raise SimulationError(f"cannot read model file {normalized_path}: {error}") from error
    before_digest = sha256_bytes(source_bytes)
    module_name = f"_simulation_data_lab_model_{stable_token(str(path), before_digest, length=16)}"
    module = ModuleType(module_name)
    module.__file__ = str(path)
    module.__package__ = ""
    module.__cached__ = None
    original_path = list(sys.path)
    previous_module = sys.modules.get(module_name)
    try:
        sys.path.insert(0, str(path.parent))
        sys.modules[module_name] = module
        # Compile the exact reviewed bytes whose digest is returned for the
        # execution manifest. Bypassing SourceFileLoader also makes a stale,
        # timestamp-valid __pycache__ incapable of changing executed behavior.
        code = compile(source_bytes, str(path), "exec", dont_inherit=True)
        exec(code, module.__dict__)
    except Exception as error:
        if previous_module is None:
            sys.modules.pop(module_name, None)
        else:
            sys.modules[module_name] = previous_module
        raise SimulationError(f"model import failed: {type(error).__name__}: {error}") from error
    finally:
        sys.path[:] = original_path
    if sha256_file(path) != before_digest:
        raise SimulationError("model file changed while it was imported; execution was aborted")
    simulate = getattr(module, "simulate", None)
    if not callable(simulate):
        raise SimulationError("model must define callable simulate(run)")
    raw_metadata = getattr(module, "MODEL_METADATA", None)
    metadata = require_object(raw_metadata, "MODEL_METADATA")
    require_exact_keys(
        metadata,
        {
            "modelId",
            "modelVersion",
            "engine",
            "engineVersion",
            "rng",
            "rngVersion",
            "reproducibility",
        },
        "MODEL_METADATA",
    )
    normalized_metadata = {
        key: require_text(metadata[key], f"MODEL_METADATA.{key}")
        for key in (
            "modelId",
            "modelVersion",
            "engine",
            "engineVersion",
            "rng",
            "rngVersion",
            "reproducibility",
        )
    }
    require_id(normalized_metadata["modelId"], "MODEL_METADATA.modelId")
    if normalized_metadata["reproducibility"] not in REPRODUCIBILITY_LEVELS:
        raise SimulationError(
            "MODEL_METADATA.reproducibility must be one of: "
            + ", ".join(sorted(REPRODUCIBILITY_LEVELS))
        )
    for key in ("engineVersion", "rngVersion"):
        if normalized_metadata[key].lower() in {"unknown", "latest", "unavailable"}:
            raise SimulationError(f"MODEL_METADATA.{key} must record the actual version")
    return module, normalized_path, path, before_digest, normalized_metadata


def parameter_context(spec: dict[str, Any]) -> dict[tuple[str, str], dict[str, Any]]:
    result: dict[tuple[str, str], dict[str, Any]] = {}
    scenarios = {item["scenarioId"]: item for item in spec["scenarios"]}
    points = {item["designPointId"]: item for item in spec["designPoints"]}
    for scenario_id, scenario in scenarios.items():
        for design_id, point in points.items():
            combined = [*point["parameters"], *scenario["parameters"]]
            result[(scenario_id, design_id)] = model_visible_parameter_maps(combined)
    return result


def format_number(value: float) -> str:
    if value == 0:
        return "0"
    return format(value, ".17g")


def normalize_model_result(
    raw: Any,
    expected_outcomes: dict[str, str],
    run_id: str,
    time_unit: str | None,
) -> dict[str, Any]:
    result = require_object(raw, f"result for {run_id}")
    require_exact_keys(result, {"outcomes"}, f"result for {run_id}", {"observations", "events", "diagnostics"})
    raw_outcomes = require_object(result["outcomes"], f"result for {run_id}.outcomes")
    if set(raw_outcomes) != set(expected_outcomes):
        missing = sorted(set(expected_outcomes) - raw_outcomes.keys())
        extra = sorted(raw_outcomes.keys() - set(expected_outcomes))
        details = []
        if missing:
            details.append(f"missing {', '.join(missing)}")
        if extra:
            details.append(f"unexpected {', '.join(extra)}")
        raise SimulationError(f"result for {run_id}.outcomes differs: {'; '.join(details)}")
    outcomes = {
        name: require_finite_number(raw_outcomes[name], f"result for {run_id}.outcomes.{name}")
        for name in sorted(expected_outcomes)
    }

    raw_observations = require_list(
        result.get("observations", []), f"result for {run_id}.observations"
    )
    raw_events = require_list(result.get("events", []), f"result for {run_id}.events")
    if (raw_observations or raw_events) and time_unit is None:
        raise SimulationError(
            f"result for {run_id} emits observations or events, so experiment.timeUnit "
            "must be declared"
        )
    if len(raw_observations) > MAX_RECORDS_PER_RUN:
        raise SimulationError(
            f"result for {run_id}.observations exceeds the per-run limit of {MAX_RECORDS_PER_RUN}"
        )
    observations: list[dict[str, Any]] = []
    for index, raw_item in enumerate(raw_observations):
        label = f"result for {run_id}.observations[{index}]"
        item = require_object(raw_item, label)
        require_exact_keys(
            item,
            {"sim_time", "variable", "value", "unit"},
            label,
            {"entity_type", "entity_id", "is_warmup"},
        )
        is_warmup = item.get("is_warmup", False)
        if not isinstance(is_warmup, bool):
            raise SimulationError(f"{label}.is_warmup must be boolean")
        entity_type = item.get("entity_type", "")
        entity_id = item.get("entity_id", "")
        if not isinstance(entity_type, str) or not isinstance(entity_id, str):
            raise SimulationError(f"{label} entity_type and entity_id must be strings when present")
        observations.append(
            {
                "sim_time": require_finite_number(item["sim_time"], f"{label}.sim_time"),
                "time_unit": time_unit,
                "variable": require_name(item["variable"], f"{label}.variable"),
                "value": require_finite_number(item["value"], f"{label}.value"),
                "unit": require_text(item["unit"], f"{label}.unit"),
                "entity_type": entity_type,
                "entity_id": entity_id,
                "is_warmup": is_warmup,
            }
        )

    if len(raw_events) > MAX_RECORDS_PER_RUN:
        raise SimulationError(
            f"result for {run_id}.events exceeds the per-run limit of {MAX_RECORDS_PER_RUN}"
        )
    events: list[dict[str, Any]] = []
    for index, raw_item in enumerate(raw_events):
        label = f"result for {run_id}.events[{index}]"
        item = require_object(raw_item, label)
        require_exact_keys(
            item,
            {"sim_time", "event_type"},
            label,
            {"entity_type", "entity_id", "payload"},
        )
        entity_type = item.get("entity_type", "")
        entity_id = item.get("entity_id", "")
        if not isinstance(entity_type, str) or not isinstance(entity_id, str):
            raise SimulationError(f"{label} entity_type and entity_id must be strings when present")
        events.append(
            {
                "sim_time": require_finite_number(item["sim_time"], f"{label}.sim_time"),
                "time_unit": time_unit,
                "event_type": require_name(item["event_type"], f"{label}.event_type"),
                "entity_type": entity_type,
                "entity_id": entity_id,
                "payload_json": canonical_json_bytes(
                    normalize_json_value(item.get("payload", {}), f"{label}.payload")
                ).decode("utf-8").rstrip("\n"),
            }
        )

    raw_diagnostics = require_list(
        result.get("diagnostics", []), f"result for {run_id}.diagnostics"
    )
    if len(raw_diagnostics) > MAX_RECORDS_PER_RUN:
        raise SimulationError(
            f"result for {run_id}.diagnostics exceeds the per-run limit of {MAX_RECORDS_PER_RUN}"
        )
    diagnostics: list[dict[str, Any]] = []
    for index, raw_item in enumerate(raw_diagnostics):
        label = f"result for {run_id}.diagnostics[{index}]"
        item = require_object(raw_item, label)
        require_exact_keys(
            item,
            {"check_id", "status", "message"},
            label,
            {"value", "threshold", "invalidates_hypotheses"},
        )
        status = require_text(item["status"], f"{label}.status")
        if status not in {"pass", "warn", "fail"}:
            raise SimulationError(f"{label}.status must be pass, warn, or fail")
        invalidates = item.get("invalidates_hypotheses", status == "fail")
        if not isinstance(invalidates, bool):
            raise SimulationError(f"{label}.invalidates_hypotheses must be boolean")
        if invalidates and status != "fail":
            raise SimulationError(
                f"{label}.invalidates_hypotheses may be true only when status is fail"
            )
        diagnostic: dict[str, Any] = {
            "check_id": require_id(item["check_id"], f"{label}.check_id"),
            "status": status,
            "message": require_text(item["message"], f"{label}.message"),
            "value": "",
            "threshold": "",
            "invalidates_hypotheses": invalidates,
        }
        for key in ("value", "threshold"):
            if key in item:
                diagnostic[key] = format_number(require_finite_number(item[key], f"{label}.{key}"))
        diagnostics.append(diagnostic)
    return {
        "outcomes": outcomes,
        "observations": observations,
        "events": events,
        "diagnostics": diagnostics,
    }


def percentile(values: list[float], probability: float) -> float:
    if not values:
        raise SimulationError("cannot calculate a percentile of an empty sample")
    ordered = sorted(values)
    if len(ordered) == 1:
        return ordered[0]
    position = (len(ordered) - 1) * probability
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return ordered[lower]
    weight = position - lower
    return ordered[lower] * (1 - weight) + ordered[upper] * weight


def build_summary_rows(
    experiment_id: str,
    outcome_rows: list[dict[str, Any]],
    ok_run_ids: set[str],
) -> list[dict[str, Any]]:
    groups: dict[tuple[str, str, str, str], list[float]] = defaultdict(list)
    for row in outcome_rows:
        if row["run_id"] not in ok_run_ids:
            continue
        key = (row["scenario_id"], row["design_point_id"], row["outcome_name"], row["unit"])
        groups[key].append(float(row["value"]))
    summaries: list[dict[str, Any]] = []
    for (scenario_id, design_id, outcome_name, unit), values in sorted(groups.items()):
        n = len(values)
        mean = statistics.fmean(values)
        stddev = statistics.stdev(values) if n > 1 else 0.0
        summaries.append(
            {
                "experiment_id": experiment_id,
                "scenario_id": scenario_id,
                "design_point_id": design_id,
                "outcome_name": outcome_name,
                "unit": unit,
                "source_type": "simulated",
                "n": n,
                "mean": format_number(mean),
                "stddev": format_number(stddev),
                "mcse": format_number(stddev / math.sqrt(n)),
                "min": format_number(min(values)),
                "p05": format_number(percentile(values, 0.05)),
                "median": format_number(percentile(values, 0.5)),
                "p95": format_number(percentile(values, 0.95)),
                "max": format_number(max(values)),
            }
        )
    return summaries


def build_data_dictionary(spec: dict[str, Any]) -> dict[str, Any]:
    descriptions: dict[str, dict[str, str]] = {
        "design/design-point-parameters.csv": {
            "description": "Declared parameter values for each design point.",
            "grain": "design-point-parameter",
        },
        "design/scenario-factors.csv": {
            "description": "Declared parameter values for each scenario.",
            "grain": "scenario-parameter",
        },
        "data/runs.csv": {
            "description": "One row per planned scenario, design point, and execution replication.",
            "grain": "run",
        },
        "data/outcomes.csv": {
            "description": "One numeric replication-level outcome per run and declared outcome.",
            "grain": "run-outcome",
        },
        "data/observations.csv": {
            "description": "Optional long-form state observations emitted within simulation runs.",
            "grain": "run-time-entity-variable",
        },
        "data/events.csv": {
            "description": "Optional ordered events emitted within simulation runs.",
            "grain": "run-event",
        },
        "data/diagnostics.csv": {
            "description": "Model and numerical checks, including whether a finding invalidates inference.",
            "grain": "run-check",
        },
        "analysis/summary.csv": {
            "description": "Descriptive outcome statistics by scenario and design point over valid replicates.",
            "grain": "scenario-design-point-outcome",
        },
    }
    columns_by_path = {
        "design/design-point-parameters.csv": PARAMETER_COLUMNS,
        "design/scenario-factors.csv": PARAMETER_COLUMNS,
        "data/runs.csv": RUN_COLUMNS,
        "data/outcomes.csv": OUTCOME_COLUMNS,
        "data/observations.csv": OBSERVATION_COLUMNS,
        "data/events.csv": EVENT_COLUMNS,
        "data/diagnostics.csv": DIAGNOSTIC_COLUMNS,
        "analysis/summary.csv": SUMMARY_COLUMNS,
    }
    type_map = {
        "replicate_id": "integer",
        "seed": "integer",
        "observation_index": "integer",
        "event_index": "integer",
        "diagnostic_index": "integer",
        "n": "integer",
        "value": "number",
        "sim_time": "number",
        "threshold": "number-or-empty",
        "invalidates_hypotheses": "boolean",
        "is_warmup": "boolean",
        "mean": "number",
        "stddev": "number",
        "mcse": "number",
        "min": "number",
        "p05": "number",
        "median": "number",
        "p95": "number",
        "max": "number",
    }
    column_descriptions = {
        "sim_time": "Simulation time expressed in the row's time_unit.",
        "time_unit": "Unit of sim_time; exactly experiment.timeUnit.",
    }
    tables = []
    for path in sorted(columns_by_path):
        tables.append(
            {
                "path": path,
                **descriptions[path],
                "columns": [
                    {
                        "name": name,
                        "type": type_map.get(name, "string"),
                        "description": column_descriptions.get(
                            name, name.replace("_", " ").capitalize() + "."
                        ),
                    }
                    for name in columns_by_path[path]
                ],
            }
        )
    return {
        "schemaVersion": SCHEMA_VERSION,
        "experimentId": spec["experimentId"],
        "declaredTimeUnit": spec.get("timeUnit"),
        "conventions": {
            "tableShape": "tidy-long",
            "missingValues": "Empty strings are allowed only in explicitly optional text or diagnostic fields.",
            "sourceLabel": "Simulation-generated measurements use source_type=simulated.",
            "unitRule": "Every numeric outcome and observation has an explicit unit; use 1 when dimensionless.",
            "timeUnitRule": "Observations and events require experiment.timeUnit; every emitted row repeats it as time_unit.",
        },
        "declaredOutcomes": spec["outcomes"],
        "tables": tables,
    }


def build_explore_sql() -> str:
    return """-- DuckDB starter queries for a simulation-data-lab bundle.
-- Run this file from the bundle root so the relative paths resolve.
CREATE OR REPLACE VIEW v_runs AS
SELECT * FROM read_csv_auto('data/runs.csv', header = true);

CREATE OR REPLACE VIEW v_scenario_factors AS
SELECT * FROM read_csv_auto('design/scenario-factors.csv', header = true);

CREATE OR REPLACE VIEW v_design_point_parameters AS
SELECT * FROM read_csv_auto('design/design-point-parameters.csv', header = true);

CREATE OR REPLACE VIEW v_outcomes AS
SELECT * FROM read_csv_auto('data/outcomes.csv', header = true);

CREATE OR REPLACE VIEW v_summary AS
SELECT * FROM read_csv_auto('analysis/summary.csv', header = true);

CREATE OR REPLACE VIEW v_run_outcomes AS
SELECT r.scenario_id, r.design_point_id, r.replicate_id, r.coupling_id,
       r.seed, r.status, o.outcome_name, o.value, o.unit, o.source_type
FROM v_runs AS r
LEFT JOIN v_outcomes AS o USING (
  experiment_id, run_id, scenario_id, design_point_id, replicate_id, coupling_id
);

-- Rows appear only when two successful scenarios share a semantic coupling.
-- The direction is explicit: scenario_b value minus scenario_a value.
CREATE OR REPLACE VIEW v_paired_outcome_differences AS
SELECT a.design_point_id, a.replicate_id, a.coupling_id,
       a.scenario_id AS scenario_a, b.scenario_id AS scenario_b,
       a.outcome_name, b.value - a.value AS difference_b_minus_a, a.unit
FROM v_run_outcomes AS a
JOIN v_run_outcomes AS b
  ON a.design_point_id = b.design_point_id
 AND a.replicate_id = b.replicate_id
 AND a.coupling_id = b.coupling_id
 AND a.outcome_name = b.outcome_name
 AND a.unit = b.unit
WHERE a.scenario_id < b.scenario_id
  AND a.status = 'ok' AND b.status = 'ok'
  AND a.value IS NOT NULL AND b.value IS NOT NULL;

-- Inspect completeness before analyzing effects.
SELECT status, count(*) AS runs FROM v_runs GROUP BY status ORDER BY status;

-- Explore scenario distributions without mixing design points.
SELECT scenario_id, design_point_id, outcome_name, n, mean, mcse, p05, median, p95
FROM v_summary
ORDER BY outcome_name, design_point_id, scenario_id;

-- For paired designs, inspect replication-level contrasts before aggregation.
SELECT design_point_id, scenario_a, scenario_b, outcome_name,
       count(*) AS complete_pairs,
       avg(difference_b_minus_a) AS mean_difference_b_minus_a
FROM v_paired_outcome_differences
GROUP BY design_point_id, scenario_a, scenario_b, outcome_name
ORDER BY outcome_name, design_point_id, scenario_a, scenario_b;
"""


def file_record(root: Path, relative: str, rows: int | None = None) -> dict[str, Any]:
    record: dict[str, Any] = {"path": relative, "sha256": sha256_file(root / relative)}
    if rows is not None:
        record["rows"] = rows
    return record


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def command_run(args: argparse.Namespace) -> int:
    root = args.root.resolve()
    if not root.is_dir():
        raise SimulationError("bundle root must be an existing directory")
    for relative in ("data", "analysis", "data-dictionary.json", "execution-manifest.json"):
        if (root / relative).exists():
            raise SimulationError(f"refusing to replace existing run output: {relative}")
    spec, spec_raw, plan_rows = verify_plan(root)
    module, model_relative, model_path, model_sha256, model_metadata = load_model(
        root, args.model
    )
    if model_metadata["engine"] != spec["engine"]["name"]:
        raise SimulationError(
            "MODEL_METADATA.engine must exactly match experiment.engine.name; "
            f"found {model_metadata['engine']!r} and {spec['engine']['name']!r}"
        )
    simulate: Callable[[dict[str, Any]], Any] = getattr(module, "simulate")
    expected_outcomes = {item["name"]: item["unit"] for item in spec["outcomes"]}
    contexts = parameter_context(spec)
    planned_core_rows = planned_core_row_count(
        len(plan_rows),
        len(spec["scenarios"]) * len(spec["designPoints"]),
        len(expected_outcomes),
    ) + review_row_count(spec)

    run_rows: list[dict[str, Any]] = []
    outcome_rows: list[dict[str, Any]] = []
    observation_rows: list[dict[str, Any]] = []
    event_rows: list[dict[str, Any]] = []
    diagnostic_rows: list[dict[str, Any]] = []
    started_at = utc_now()
    start_clock = time.perf_counter()

    for plan_row in plan_rows:
        common = {
            "experiment_id": plan_row["experiment_id"],
            "run_id": plan_row["run_id"],
            "scenario_id": plan_row["scenario_id"],
            "design_point_id": plan_row["design_point_id"],
            "replicate_id": int(plan_row["replicate_id"]),
            "coupling_id": plan_row["coupling_id"],
            "seed": int(plan_row["seed"]),
        }
        context = contexts[(common["scenario_id"], common["design_point_id"])]
        model_input = {**common, **json.loads(json.dumps(context))}
        if "timeUnit" in spec:
            model_input["time_unit"] = spec["timeUnit"]
        status = "ok"
        error_type = ""
        error_message = ""
        normalized: dict[str, Any] | None = None
        try:
            normalized = normalize_model_result(
                simulate(model_input),
                expected_outcomes,
                common["run_id"],
                spec.get("timeUnit"),
            )
            optional_total = (
                len(observation_rows)
                + len(event_rows)
                + len(diagnostic_rows)
                + len(normalized["observations"])
                + len(normalized["events"])
                + len(normalized["diagnostics"])
            )
            # Reserve the conservative planned core footprint, then charge the
            # accumulated and newly returned optional rows before appending any.
            enforce_materialized_row_budget(planned_core_rows, optional_total)
            if any(
                item["status"] == "fail" and item["invalidates_hypotheses"]
                for item in normalized["diagnostics"]
            ):
                status = "invalid"
                error_type = "InvalidatingDiagnostic"
                error_message = "One or more diagnostics invalidate hypothesis analysis."
        except Exception as error:
            status = "failed"
            error_type = type(error).__name__
            error_message = " ".join(str(error).splitlines()).strip()[:1000] or error_type
            normalized = None
        run_rows.append(
            {
                **common,
                "status": status,
                "error_type": error_type,
                "error_message": error_message,
            }
        )
        if normalized is None:
            continue
        for name, value in normalized["outcomes"].items():
            outcome_rows.append(
                {
                    **{key: common[key] for key in RUN_PLAN_COLUMNS if key != "seed"},
                    "outcome_name": name,
                    "value": format_number(value),
                    "unit": expected_outcomes[name],
                    "source_type": "simulated",
                }
            )
        for index, item in enumerate(normalized["observations"], start=1):
            observation_rows.append(
                {
                    **{key: common[key] for key in RUN_PLAN_COLUMNS if key != "seed"},
                    "observation_index": index,
                    "sim_time": format_number(item["sim_time"]),
                    "time_unit": item["time_unit"],
                    "entity_type": item["entity_type"],
                    "entity_id": item["entity_id"],
                    "variable": item["variable"],
                    "value": format_number(item["value"]),
                    "unit": item["unit"],
                    "source_type": "simulated",
                    "is_warmup": str(item["is_warmup"]).lower(),
                }
            )
        for index, item in enumerate(normalized["events"], start=1):
            event_rows.append(
                {
                    **{key: common[key] for key in RUN_PLAN_COLUMNS if key != "seed"},
                    "event_index": index,
                    "sim_time": format_number(item["sim_time"]),
                    "time_unit": item["time_unit"],
                    "entity_type": item["entity_type"],
                    "entity_id": item["entity_id"],
                    "event_type": item["event_type"],
                    "payload_json": item["payload_json"],
                    "source_type": "simulated",
                }
            )
        for index, item in enumerate(normalized["diagnostics"], start=1):
            diagnostic_rows.append(
                {
                    "experiment_id": common["experiment_id"],
                    "run_id": common["run_id"],
                    "scenario_id": common["scenario_id"],
                    "design_point_id": common["design_point_id"],
                    "replicate_id": common["replicate_id"],
                    "diagnostic_index": index,
                    "check_id": item["check_id"],
                    "status": item["status"],
                    "value": item["value"],
                    "threshold": item["threshold"],
                    "invalidates_hypotheses": str(item["invalidates_hypotheses"]).lower(),
                    "message": item["message"],
                }
            )

    if sha256_file(model_path) != model_sha256:
        raise SimulationError("model file changed during execution; no run output was published")
    ok_ids = {row["run_id"] for row in run_rows if row["status"] == "ok"}
    summary_rows = build_summary_rows(spec["experimentId"], outcome_rows, ok_ids)
    completed_at = utc_now()
    elapsed_seconds = time.perf_counter() - start_clock
    counts = defaultdict(int)
    for row in run_rows:
        counts[row["status"]] += 1

    temporary = Path(tempfile.mkdtemp(prefix=".simulation-run.tmp-", dir=root))
    published = False
    published_paths: list[Path] = []
    try:
        (temporary / "data").mkdir()
        (temporary / "analysis").mkdir()
        table_payloads = {
            "data/runs.csv": (RUN_COLUMNS, run_rows),
            "data/outcomes.csv": (OUTCOME_COLUMNS, outcome_rows),
            "data/observations.csv": (OBSERVATION_COLUMNS, observation_rows),
            "data/events.csv": (EVENT_COLUMNS, event_rows),
            "data/diagnostics.csv": (DIAGNOSTIC_COLUMNS, diagnostic_rows),
            "analysis/summary.csv": (SUMMARY_COLUMNS, summary_rows),
        }
        row_counts: dict[str, int] = {}
        for relative, (columns, rows) in table_payloads.items():
            (temporary / relative).write_bytes(csv_bytes(columns, rows))
            row_counts[relative] = len(rows)
        (temporary / "analysis/explore.sql").write_text(build_explore_sql(), encoding="utf-8", newline="\n")
        (temporary / "data-dictionary.json").write_bytes(canonical_json_bytes(build_data_dictionary(spec)))
        files = [
            file_record(temporary, relative, row_counts.get(relative))
            for relative in sorted(
                [*table_payloads, "analysis/explore.sql", "data-dictionary.json"]
            )
        ]
        manifest = {
            "schemaVersion": SCHEMA_VERSION,
            "toolVersion": TOOL_VERSION,
            "experimentId": spec["experimentId"],
            "uncertaintyMode": spec["uncertaintyMode"],
            "status": "complete" if counts["failed"] == 0 and counts["invalid"] == 0 else "incomplete",
            "startedAt": started_at,
            "completedAt": completed_at,
            "wallSeconds": float(format(elapsed_seconds, ".9g")),
            "specSha256": sha256_bytes(spec_raw),
            "normalizedSpecSha256": sha256_bytes(canonical_json_bytes(spec)),
            "planManifestSha256": sha256_file(root / "design/plan-manifest.json"),
            "model": {
                "path": model_relative,
                "sha256": model_sha256,
                **model_metadata,
            },
            "rng": {
                "rootSeed": spec["rootSeed"],
                "seedPolicy": spec["seedPolicy"],
                "seedDerivation": SEED_DERIVATION,
                "algorithm": model_metadata["rng"],
                "implementationVersion": model_metadata["rngVersion"],
                "reproducibility": model_metadata["reproducibility"],
            },
            "environment": {
                "pythonVersion": platform.python_version(),
                "operatingSystem": platform.system(),
                "operatingSystemRelease": platform.release(),
                "machine": platform.machine(),
            },
            "runCounts": {
                "planned": len(plan_rows),
                "ok": counts["ok"],
                "invalid": counts["invalid"],
                "failed": counts["failed"],
            },
            "files": files,
            "invocation": {
                "subcommand": "run",
                "root": ".",
                "model": model_relative,
            },
        }
        (temporary / "execution-manifest.json").write_bytes(canonical_json_bytes(manifest))
        for relative in ("data", "analysis", "data-dictionary.json", "execution-manifest.json"):
            if (root / relative).exists():
                raise SimulationError(f"run output appeared before publication: {relative}")
        for relative in ("data", "analysis", "data-dictionary.json", "execution-manifest.json"):
            source = temporary / relative
            target = root / relative
            source.replace(target)
            published_paths.append(target)
        published = True
    except OSError as error:
        for path in reversed(published_paths):
            if path.is_dir():
                shutil.rmtree(path, ignore_errors=True)
            else:
                try:
                    path.unlink()
                except FileNotFoundError:
                    pass
        raise SimulationError(f"cannot publish complete run output: {error}") from error
    finally:
        if temporary.exists():
            shutil.rmtree(temporary, ignore_errors=True)

    result = {
        "ok": manifest["status"] == "complete",
        "experimentId": spec["experimentId"],
        "status": manifest["status"],
        "published": published,
        "runCounts": manifest["runCounts"],
        "outcomeRows": len(outcome_rows),
        "observationRows": len(observation_rows),
        "eventRows": len(event_rows),
    }
    sys.stdout.buffer.write(canonical_json_bytes(result))
    return 0 if result["ok"] else 2


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Plan or run a reproducible simulation-data-lab experiment."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    plan_parser = subparsers.add_parser(
        "plan", help="expand a validated experiment spec into a deterministic run plan"
    )
    plan_parser.add_argument("--spec", type=Path, required=True)
    plan_parser.add_argument("--output-dir", type=Path, required=True)
    plan_parser.add_argument(
        "--require-variable-review", action="store_true",
        help="require the declared variable review for a new study; omit only for legacy replay",
    )
    plan_parser.set_defaults(handler=command_plan)

    run_parser = subparsers.add_parser(
        "run", help="execute every planned run through a Python model adapter"
    )
    run_parser.add_argument("--root", type=Path, required=True)
    run_parser.add_argument(
        "--model",
        default="model.py",
        help="bundle-relative Python model adapter path (default: model.py)",
    )
    run_parser.set_defaults(handler=command_run)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.handler(args)
    except SimulationError as error:
        print(f"error: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
