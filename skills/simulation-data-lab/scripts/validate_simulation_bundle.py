#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

"""Validate a complete simulation-data-lab bundle independently of its model."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import statistics
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any

from model_variable_review import build_variable_review_files, variable_review_summary

from run_simulation_experiment import (
    DIAGNOSTIC_COLUMNS,
    EVENT_COLUMNS,
    OBSERVATION_COLUMNS,
    OUTCOME_COLUMNS,
    REPRODUCIBILITY_LEVELS,
    RUN_COLUMNS,
    RUN_PLAN_COLUMNS,
    SCHEMA_VERSION,
    SUMMARY_COLUMNS,
    SEED_DERIVATION,
    TOOL_VERSION,
    SimulationError,
    build_data_dictionary,
    build_summary_rows,
    canonical_json_bytes,
    load_json,
    normalize_spec,
    read_csv,
    require_exact_keys,
    require_finite_number,
    require_id,
    require_list,
    require_nonnegative_integer,
    require_object,
    require_text,
    reject_duplicate_keys,
    reject_json_constant,
    safe_bundle_path,
    sha256_bytes,
    sha256_file,
    verify_plan,
)


CORE_FILE_COLUMNS = {
    "data/runs.csv": RUN_COLUMNS,
    "data/outcomes.csv": OUTCOME_COLUMNS,
    "data/observations.csv": OBSERVATION_COLUMNS,
    "data/events.csv": EVENT_COLUMNS,
    "data/diagnostics.csv": DIAGNOSTIC_COLUMNS,
    "analysis/summary.csv": SUMMARY_COLUMNS,
}
NON_TABLE_FILES = frozenset({"analysis/explore.sql", "data-dictionary.json"})
REQUIRED_MANIFEST_FILES = frozenset({*CORE_FILE_COLUMNS, *NON_TABLE_FILES})


def parse_iso8601(value: Any, label: str) -> datetime:
    text = require_text(value, label)
    try:
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError as error:
        raise SimulationError(f"{label} must be an ISO 8601 timestamp") from error
    if parsed.tzinfo is None:
        raise SimulationError(f"{label} must include a timezone")
    return parsed


def parse_csv_integer(value: str, label: str, *, positive: bool = False) -> int:
    try:
        parsed = int(value)
    except ValueError as error:
        raise SimulationError(f"{label} must be an integer") from error
    if positive and parsed <= 0:
        raise SimulationError(f"{label} must be positive")
    if not positive and parsed < 0:
        raise SimulationError(f"{label} must be non-negative")
    return parsed


def parse_csv_number(value: str, label: str) -> float:
    try:
        parsed = float(value)
    except ValueError as error:
        raise SimulationError(f"{label} must be numeric") from error
    if not math.isfinite(parsed):
        raise SimulationError(f"{label} must be finite")
    return parsed


def validate_manifest(
    root: Path,
    spec: dict[str, Any],
    spec_raw: bytes,
    plan_rows: list[dict[str, str]],
) -> tuple[dict[str, Any], dict[str, int]]:
    value, raw = load_json(root / "execution-manifest.json", "execution-manifest.json")
    manifest = require_object(value, "execution-manifest.json")
    require_exact_keys(
        manifest,
        {
            "schemaVersion",
            "toolVersion",
            "experimentId",
            "uncertaintyMode",
            "status",
            "startedAt",
            "completedAt",
            "wallSeconds",
            "specSha256",
            "normalizedSpecSha256",
            "planManifestSha256",
            "model",
            "rng",
            "environment",
            "runCounts",
            "files",
            "invocation",
        },
        "execution-manifest.json",
    )
    if raw != canonical_json_bytes(manifest):
        raise SimulationError("execution-manifest.json must use canonical JSON")
    manifest_schema_version = require_nonnegative_integer(
        manifest["schemaVersion"], "execution-manifest.json.schemaVersion"
    )
    if manifest_schema_version != SCHEMA_VERSION:
        raise SimulationError(f"execution-manifest.json.schemaVersion must be {SCHEMA_VERSION}")
    if manifest["toolVersion"] != TOOL_VERSION:
        raise SimulationError(
            f"execution-manifest.json.toolVersion must be {TOOL_VERSION} for this validator"
        )
    if manifest["experimentId"] != spec["experimentId"]:
        raise SimulationError("execution manifest experimentId differs from experiment.json")
    if manifest["uncertaintyMode"] != spec["uncertaintyMode"]:
        raise SimulationError("execution manifest uncertaintyMode differs from experiment.json")
    if manifest["status"] not in {"complete", "incomplete"}:
        raise SimulationError("execution manifest status must be complete or incomplete")
    started = parse_iso8601(manifest["startedAt"], "execution-manifest.json.startedAt")
    completed = parse_iso8601(manifest["completedAt"], "execution-manifest.json.completedAt")
    if completed < started:
        raise SimulationError("execution manifest completedAt precedes startedAt")
    if require_finite_number(manifest["wallSeconds"], "execution-manifest.json.wallSeconds") < 0:
        raise SimulationError("execution manifest wallSeconds must be non-negative")
    if manifest["specSha256"] != sha256_bytes(spec_raw):
        raise SimulationError("execution manifest specSha256 does not match experiment.json")
    if manifest["normalizedSpecSha256"] != sha256_bytes(canonical_json_bytes(spec)):
        raise SimulationError("execution manifest normalizedSpecSha256 does not match experiment.json")
    if manifest["planManifestSha256"] != sha256_file(root / "design/plan-manifest.json"):
        raise SimulationError("execution manifest planManifestSha256 does not match the plan")

    model = require_object(manifest["model"], "execution-manifest.json.model")
    require_exact_keys(
        model,
        {
            "path",
            "sha256",
            "modelId",
            "modelVersion",
            "engine",
            "engineVersion",
            "rng",
            "rngVersion",
            "reproducibility",
        },
        "execution-manifest.json.model",
    )
    model_relative, model_path = safe_bundle_path(root, model["path"], "execution manifest model.path")
    if not model_path.is_file():
        raise SimulationError(f"execution manifest model is missing: {model_relative}")
    if model["sha256"] != sha256_file(model_path):
        raise SimulationError("execution manifest model hash does not match the model file")
    require_id(model["modelId"], "execution-manifest.json.model.modelId")
    for key in ("modelVersion", "engine", "engineVersion", "rng", "rngVersion"):
        require_text(model[key], f"execution-manifest.json.model.{key}")
    if model["engine"] != spec["engine"]["name"]:
        raise SimulationError("execution manifest model engine differs from experiment.engine.name")
    if model["reproducibility"] not in REPRODUCIBILITY_LEVELS:
        raise SimulationError("execution manifest model reproducibility is unsupported")

    rng = require_object(manifest["rng"], "execution-manifest.json.rng")
    require_exact_keys(
        rng,
        {
            "rootSeed",
            "seedPolicy",
            "seedDerivation",
            "algorithm",
            "implementationVersion",
            "reproducibility",
        },
        "execution-manifest.json.rng",
    )
    rng_root_seed = require_nonnegative_integer(
        rng["rootSeed"], "execution-manifest.json.rng.rootSeed"
    )
    if rng_root_seed != spec["rootSeed"] or rng["seedPolicy"] != spec["seedPolicy"]:
        raise SimulationError("execution manifest RNG settings differ from experiment.json")
    if rng["algorithm"] != model["rng"] or rng["implementationVersion"] != model["rngVersion"]:
        raise SimulationError("execution manifest RNG metadata differs from model metadata")
    if rng["reproducibility"] != model["reproducibility"]:
        raise SimulationError("execution manifest RNG reproducibility differs from model metadata")
    if rng["seedDerivation"] != SEED_DERIVATION:
        raise SimulationError("execution manifest RNG seed derivation is unsupported")

    environment = require_object(manifest["environment"], "execution-manifest.json.environment")
    require_exact_keys(
        environment,
        {"pythonVersion", "operatingSystem", "operatingSystemRelease", "machine"},
        "execution-manifest.json.environment",
    )
    for key, item in environment.items():
        require_text(item, f"execution-manifest.json.environment.{key}")

    invocation = require_object(manifest["invocation"], "execution-manifest.json.invocation")
    require_exact_keys(invocation, {"subcommand", "root", "model"}, "execution-manifest.json.invocation")
    if invocation != {"subcommand": "run", "root": ".", "model": model_relative}:
        raise SimulationError("execution manifest invocation is not the expected portable form")

    raw_counts = require_object(manifest["runCounts"], "execution-manifest.json.runCounts")
    require_exact_keys(raw_counts, {"planned", "ok", "invalid", "failed"}, "execution-manifest.json.runCounts")
    counts: dict[str, int] = {}
    for key in ("planned", "ok", "invalid", "failed"):
        value = raw_counts[key]
        if isinstance(value, bool) or not isinstance(value, int) or value < 0:
            raise SimulationError(f"execution-manifest.json.runCounts.{key} must be non-negative")
        counts[key] = value
    if counts["planned"] != len(plan_rows):
        raise SimulationError("execution manifest planned count differs from the deterministic plan")
    if counts["ok"] + counts["invalid"] + counts["failed"] != counts["planned"]:
        raise SimulationError("execution manifest runCounts do not sum to planned")
    expected_status = "complete" if counts["invalid"] == 0 and counts["failed"] == 0 else "incomplete"
    if manifest["status"] != expected_status:
        raise SimulationError("execution manifest status disagrees with its run counts")

    file_values = require_list(manifest["files"], "execution-manifest.json.files")
    records: dict[str, dict[str, Any]] = {}
    for index, raw_record in enumerate(file_values):
        label = f"execution-manifest.json.files[{index}]"
        record = require_object(raw_record, label)
        require_exact_keys(record, {"path", "sha256"}, label, {"rows"})
        relative, path = safe_bundle_path(root, record["path"], f"{label}.path")
        if relative in records:
            raise SimulationError(f"duplicate execution manifest file path: {relative}")
        if not path.is_file():
            raise SimulationError(f"execution manifest file is missing: {relative}")
        digest = require_text(record["sha256"], f"{label}.sha256")
        if digest != sha256_file(path):
            raise SimulationError(f"execution manifest hash mismatch: {relative}")
        if "rows" in record:
            rows = record["rows"]
            if isinstance(rows, bool) or not isinstance(rows, int) or rows < 0:
                raise SimulationError(f"{label}.rows must be a non-negative integer")
        records[relative] = record
    if set(records) != set(REQUIRED_MANIFEST_FILES):
        missing = sorted(REQUIRED_MANIFEST_FILES - records.keys())
        extra = sorted(records.keys() - REQUIRED_MANIFEST_FILES)
        details = []
        if missing:
            details.append(f"missing {', '.join(missing)}")
        if extra:
            details.append(f"unexpected {', '.join(extra)}")
        raise SimulationError("execution manifest file inventory differs: " + "; ".join(details))
    return manifest, counts


def validate_runs(
    root: Path,
    plan_rows: list[dict[str, str]],
    manifest_counts: dict[str, int],
) -> tuple[list[dict[str, str]], set[str], dict[str, str]]:
    rows = read_csv(root / "data/runs.csv", RUN_COLUMNS, "data/runs.csv")
    expected = {row["run_id"]: row for row in plan_rows}
    if len(expected) != len(plan_rows):
        raise SimulationError("deterministic plan contains duplicate run_id values")
    observed: dict[str, dict[str, str]] = {}
    statuses = Counter()
    for index, row in enumerate(rows, start=2):
        run_id = row["run_id"]
        if run_id in observed:
            raise SimulationError(f"data/runs.csv has duplicate run_id at row {index}: {run_id}")
        if run_id not in expected:
            raise SimulationError(f"data/runs.csv has an unplanned run_id at row {index}: {run_id}")
        plan = expected[run_id]
        for key in RUN_PLAN_COLUMNS:
            if row[key] != plan[key]:
                raise SimulationError(f"data/runs.csv row {index} changes planned field {key}")
        if row["status"] not in {"ok", "invalid", "failed"}:
            raise SimulationError(f"data/runs.csv row {index} has unsupported status")
        if row["status"] == "ok" and (row["error_type"] or row["error_message"]):
            raise SimulationError(f"successful run {run_id} must not contain an error")
        if row["status"] != "ok" and (not row["error_type"] or not row["error_message"]):
            raise SimulationError(f"non-successful run {run_id} must record its error")
        statuses[row["status"]] += 1
        observed[run_id] = row
    if set(observed) != set(expected):
        missing = sorted(set(expected) - observed.keys())
        raise SimulationError(f"data/runs.csv is missing planned runs: {', '.join(missing[:10])}")
    computed_counts = {
        "planned": len(rows),
        "ok": statuses["ok"],
        "invalid": statuses["invalid"],
        "failed": statuses["failed"],
    }
    if computed_counts != manifest_counts:
        raise SimulationError("data/runs.csv status counts differ from execution-manifest.json")
    ok_ids = {run_id for run_id, row in observed.items() if row["status"] == "ok"}
    status_by_id = {run_id: row["status"] for run_id, row in observed.items()}
    return rows, ok_ids, status_by_id


def validate_outcomes(
    root: Path,
    spec: dict[str, Any],
    runs: list[dict[str, str]],
    ok_ids: set[str],
) -> list[dict[str, Any]]:
    rows = read_csv(root / "data/outcomes.csv", OUTCOME_COLUMNS, "data/outcomes.csv")
    run_map = {row["run_id"]: row for row in runs}
    units = {item["name"]: item["unit"] for item in spec["outcomes"]}
    observed: set[tuple[str, str]] = set()
    normalized: list[dict[str, Any]] = []
    common_keys = tuple(key for key in RUN_PLAN_COLUMNS if key != "seed")
    for index, row in enumerate(rows, start=2):
        run_id = row["run_id"]
        if run_id not in run_map:
            raise SimulationError(f"data/outcomes.csv row {index} references unknown run_id")
        for key in common_keys:
            if row[key] != run_map[run_id][key]:
                raise SimulationError(f"data/outcomes.csv row {index} changes run field {key}")
        outcome_name = row["outcome_name"]
        if outcome_name not in units:
            raise SimulationError(f"data/outcomes.csv row {index} uses undeclared outcome {outcome_name}")
        if row["unit"] != units[outcome_name]:
            raise SimulationError(f"data/outcomes.csv row {index} changes the declared unit")
        if row["source_type"] != "simulated":
            raise SimulationError(f"data/outcomes.csv row {index} must use source_type=simulated")
        if run_map[run_id]["status"] == "failed":
            raise SimulationError(f"failed run {run_id} must not contain outcome rows")
        key = (run_id, outcome_name)
        if key in observed:
            raise SimulationError(f"data/outcomes.csv duplicates {run_id}/{outcome_name}")
        observed.add(key)
        normalized.append({**row, "value": parse_csv_number(row["value"], f"data/outcomes.csv row {index} value")})
    expected = {(run_id, outcome) for run_id in ok_ids for outcome in units}
    missing = sorted(expected - observed)
    if missing:
        formatted = ", ".join(f"{run}/{outcome}" for run, outcome in missing[:10])
        raise SimulationError(f"successful runs are missing outcomes: {formatted}")
    return normalized


def validate_observations(
    root: Path,
    runs: dict[str, dict[str, str]],
    declared_time_unit: str | None,
) -> int:
    rows = read_csv(root / "data/observations.csv", OBSERVATION_COLUMNS, "data/observations.csv")
    common_keys = tuple(key for key in RUN_PLAN_COLUMNS if key != "seed")
    seen: set[tuple[str, int]] = set()
    for index, row in enumerate(rows, start=2):
        if declared_time_unit is None:
            raise SimulationError(
                "data/observations.csv contains time-bearing rows but "
                "experiment.timeUnit is not declared"
            )
        if row["time_unit"] != declared_time_unit:
            raise SimulationError(
                f"data/observations.csv row {index} time_unit must exactly match "
                "experiment.timeUnit"
            )
        run_id = row["run_id"]
        if run_id not in runs:
            raise SimulationError(f"data/observations.csv row {index} references unknown run_id")
        if runs[run_id]["status"] == "failed":
            raise SimulationError(f"failed run {run_id} must not contain observation rows")
        for key in common_keys:
            if row[key] != runs[run_id][key]:
                raise SimulationError(f"data/observations.csv row {index} changes run field {key}")
        observation_index = parse_csv_integer(
            row["observation_index"], f"data/observations.csv row {index} observation_index", positive=True
        )
        if (run_id, observation_index) in seen:
            raise SimulationError(f"data/observations.csv duplicates an observation index for {run_id}")
        seen.add((run_id, observation_index))
        parse_csv_number(row["sim_time"], f"data/observations.csv row {index} sim_time")
        parse_csv_number(row["value"], f"data/observations.csv row {index} value")
        require_text(row["variable"], f"data/observations.csv row {index} variable")
        require_text(row["unit"], f"data/observations.csv row {index} unit")
        if row["source_type"] != "simulated":
            raise SimulationError(f"data/observations.csv row {index} must use source_type=simulated")
        if row["is_warmup"] not in {"true", "false"}:
            raise SimulationError(f"data/observations.csv row {index} has invalid is_warmup")
    return len(rows)


def validate_events(
    root: Path,
    runs: dict[str, dict[str, str]],
    declared_time_unit: str | None,
) -> int:
    rows = read_csv(root / "data/events.csv", EVENT_COLUMNS, "data/events.csv")
    common_keys = tuple(key for key in RUN_PLAN_COLUMNS if key != "seed")
    seen: set[tuple[str, int]] = set()
    for index, row in enumerate(rows, start=2):
        if declared_time_unit is None:
            raise SimulationError(
                "data/events.csv contains time-bearing rows but experiment.timeUnit is not declared"
            )
        if row["time_unit"] != declared_time_unit:
            raise SimulationError(
                f"data/events.csv row {index} time_unit must exactly match experiment.timeUnit"
            )
        run_id = row["run_id"]
        if run_id not in runs:
            raise SimulationError(f"data/events.csv row {index} references unknown run_id")
        if runs[run_id]["status"] == "failed":
            raise SimulationError(f"failed run {run_id} must not contain event rows")
        for key in common_keys:
            if row[key] != runs[run_id][key]:
                raise SimulationError(f"data/events.csv row {index} changes run field {key}")
        event_index = parse_csv_integer(row["event_index"], f"data/events.csv row {index} event_index", positive=True)
        if (run_id, event_index) in seen:
            raise SimulationError(f"data/events.csv duplicates an event index for {run_id}")
        seen.add((run_id, event_index))
        parse_csv_number(row["sim_time"], f"data/events.csv row {index} sim_time")
        require_text(row["event_type"], f"data/events.csv row {index} event_type")
        if row["source_type"] != "simulated":
            raise SimulationError(f"data/events.csv row {index} must use source_type=simulated")
        try:
            payload = json.loads(
                row["payload_json"],
                object_pairs_hook=reject_duplicate_keys,
                parse_constant=reject_json_constant,
            )
        except (json.JSONDecodeError, SimulationError, ValueError) as error:
            raise SimulationError(f"data/events.csv row {index} payload_json is invalid") from error
        if canonical_json_bytes(payload).decode("utf-8").rstrip("\n") != row["payload_json"]:
            raise SimulationError(f"data/events.csv row {index} payload_json is not canonical")
    return len(rows)


def validate_diagnostics(
    root: Path,
    runs: dict[str, dict[str, str]],
    status_by_id: dict[str, str],
) -> int:
    rows = read_csv(root / "data/diagnostics.csv", DIAGNOSTIC_COLUMNS, "data/diagnostics.csv")
    seen: set[tuple[str, int]] = set()
    invalidating: set[str] = set()
    for index, row in enumerate(rows, start=2):
        run_id = row["run_id"]
        if run_id not in runs:
            raise SimulationError(f"data/diagnostics.csv row {index} references unknown run_id")
        if runs[run_id]["status"] == "failed":
            raise SimulationError(f"failed run {run_id} must not contain diagnostic rows")
        for key in ("experiment_id", "run_id", "scenario_id", "design_point_id", "replicate_id"):
            if row[key] != runs[run_id][key]:
                raise SimulationError(f"data/diagnostics.csv row {index} changes run field {key}")
        diagnostic_index = parse_csv_integer(
            row["diagnostic_index"], f"data/diagnostics.csv row {index} diagnostic_index", positive=True
        )
        if (run_id, diagnostic_index) in seen:
            raise SimulationError(f"data/diagnostics.csv duplicates a diagnostic index for {run_id}")
        seen.add((run_id, diagnostic_index))
        require_text(row["check_id"], f"data/diagnostics.csv row {index} check_id")
        require_text(row["message"], f"data/diagnostics.csv row {index} message")
        if row["status"] not in {"pass", "warn", "fail"}:
            raise SimulationError(f"data/diagnostics.csv row {index} has invalid status")
        if row["value"]:
            parse_csv_number(row["value"], f"data/diagnostics.csv row {index} value")
        if row["threshold"]:
            parse_csv_number(row["threshold"], f"data/diagnostics.csv row {index} threshold")
        if row["invalidates_hypotheses"] not in {"true", "false"}:
            raise SimulationError(
                f"data/diagnostics.csv row {index} has invalid invalidates_hypotheses"
            )
        if row["invalidates_hypotheses"] == "true" and row["status"] != "fail":
            raise SimulationError(
                f"data/diagnostics.csv row {index} invalidates hypotheses without status=fail"
            )
        if row["status"] == "fail" and row["invalidates_hypotheses"] == "true":
            invalidating.add(run_id)
    for run_id, status in status_by_id.items():
        if status == "invalid" and run_id not in invalidating:
            raise SimulationError(f"invalid run {run_id} lacks an invalidating diagnostic")
        if run_id in invalidating and status != "invalid":
            raise SimulationError(f"run {run_id} has an invalidating diagnostic but status={status}")
    return len(rows)


def validate_summary(
    root: Path,
    spec: dict[str, Any],
    outcomes: list[dict[str, Any]],
    ok_ids: set[str],
) -> int:
    expected_rows = build_summary_rows(spec["experimentId"], outcomes, ok_ids)
    from run_simulation_experiment import csv_bytes

    expected = csv_bytes(SUMMARY_COLUMNS, expected_rows)
    try:
        observed = (root / "analysis/summary.csv").read_bytes()
    except OSError as error:
        raise SimulationError(f"cannot read analysis/summary.csv: {error}") from error
    if observed != expected:
        raise SimulationError("analysis/summary.csv does not independently recompute from valid outcomes")
    return len(expected_rows)


def validate_dictionary_and_queries(root: Path, spec: dict[str, Any]) -> None:
    dictionary_value, dictionary_raw = load_json(root / "data-dictionary.json", "data-dictionary.json")
    expected_dictionary = build_data_dictionary(spec)
    if dictionary_value != expected_dictionary or dictionary_raw != canonical_json_bytes(expected_dictionary):
        raise SimulationError("data-dictionary.json differs from the core table contract")
    try:
        sql = (root / "analysis/explore.sql").read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as error:
        raise SimulationError(f"cannot read analysis/explore.sql: {error}") from error
    for relative in (
        "design/scenario-factors.csv",
        "design/design-point-parameters.csv",
        "data/runs.csv",
        "data/outcomes.csv",
        "analysis/summary.csv",
    ):
        if relative not in sql:
            raise SimulationError(f"analysis/explore.sql does not expose {relative}")


def validate_file_records(root: Path, manifest: dict[str, Any]) -> dict[str, int]:
    row_counts: dict[str, int] = {}
    records = {record["path"]: record for record in manifest["files"]}
    for relative, columns in CORE_FILE_COLUMNS.items():
        rows = read_csv(root / relative, columns, relative)
        if records[relative].get("rows") != len(rows):
            raise SimulationError(f"execution manifest row count mismatch: {relative}")
        row_counts[relative] = len(rows)
    for relative in NON_TABLE_FILES:
        if "rows" in records[relative]:
            raise SimulationError(f"execution manifest must not assign row counts to {relative}")
    return row_counts


def audit_number(value: float, analyzer: str = "mean-difference-v2") -> float:
    if not math.isfinite(value):
        raise SimulationError("hypothesis recomputation produced a non-finite number")
    result = value if analyzer == "mean-difference-v3" else float(format(value, ".15g"))
    return 0.0 if result == 0.0 else result


def audit_variance(values: list[float], mean: float) -> float:
    if len(values) < 2:
        raise SimulationError("stochastic hypothesis recomputation needs at least two observations")
    return math.fsum((value - mean) ** 2 for value in values) / (len(values) - 1)


def audit_point_status(
    operator: str,
    threshold: float,
    estimate: float,
    interval: dict[str, Any] | None,
) -> str:
    if interval is None:
        if operator == "ge":
            return "supports" if estimate >= threshold else "challenges"
        return "supports" if estimate <= threshold else "challenges"
    if operator == "ge":
        if interval["low"] >= threshold:
            return "supports"
        if interval["high"] < threshold:
            return "challenges"
    else:
        if interval["high"] <= threshold:
            return "supports"
        if interval["low"] > threshold:
            return "challenges"
    return "inconclusive"


def audit_limitations(
    spec: dict[str, Any], hypothesis: dict[str, Any], analyzer: str
) -> list[str]:
    assumptions = {
        item["assumptionId"]: item["statement"] for item in spec["assumptions"]
    }
    values = [
        f"Assumption {assumption_id}: {assumptions[assumption_id]}"
        for assumption_id in hypothesis["assumptionIds"]
    ]
    values.append("The conclusion is conditional on the implemented model and analyzed design range.")
    analysis = hypothesis["analysis"]
    if (
        analyzer in {"mean-difference-v2", "mean-difference-v3"}
        and spec["uncertaintyMode"] == "stochastic"
        and analysis["kind"] == "scenario-contrast"
    ):
        if analysis["intervalMethod"] == "bounded-hoeffding-bonferroni":
            values.append(
                "Hoeffding-Bonferroni intervals cover this hypothesis's declared design-point "
                "family conditional on fixed sample sizes, independent replications, and "
                "valid a priori outcome bounds; observed extrema do not establish those bounds."
            )
            values.append(
                "The distribution-free intervals may be conservative. Empirical MCSE is "
                "descriptive and does not determine their width; no sequential, clustered, "
                "or across-hypothesis coverage is claimed."
            )
        elif analysis["intervalMethod"] == "normal-approximation-bonferroni":
            values.append(
                "Bonferroni controls the declared family of design-point intervals within "
                "this hypothesis only, conditional on adequate marginal normal approximations."
            )
        else:
            values.append(
                "Intervals are pointwise; the declared level does not give simultaneous "
                "coverage across design points or hypotheses."
            )
        if analysis["intervalMethod"] != "bounded-hoeffding-bonferroni":
            values.append(
                "At least 30 replications and nonzero observed contrast variance are required "
                "for automated normal-Wald decisions; these guards do not establish adequate "
                "coverage for skewed, rare-event, clustered, or adaptively stopped samples."
            )
    if hypothesis["externalValidationRequired"]:
        values.append("External empirical validation is required before applying the result to reality.")
    return sorted(set(values))


def audit_decision_text(status: str, hypothesis_id: str, analyzer: str) -> str:
    messages = {
        "supports-under-model": "Every primary and challenge design point meets the preregistered threshold.",
        "challenges-under-model": "At least one primary or challenge design point contradicts the preregistered threshold.",
        "inconclusive-under-model": "No design point contradicts the threshold, but at least one interval crosses it.",
        "not-identifiable-from-design": "The declared design cannot identify the requested contrast.",
    }
    if analyzer in {"mean-difference-v2", "mean-difference-v3"}:
        messages["inconclusive-under-model"] = (
            "No eligible design point contradicts the threshold, but at least one interval "
            "crosses it or an inference guard prevents a decision."
        )
    return f"{hypothesis_id}: {messages[status]}"


def audit_bounded_interval(
    analysis: dict[str, Any], baseline: list[float], comparison: list[float], center: float,
) -> dict[str, Any]:
    """Recompute bounded inference from raw observations, not the reported MCSE."""
    bounds = analysis["outcomeBounds"]
    widths: dict[str, float] = {}
    for name, sample in (("baseline", baseline), ("comparison", comparison)):
        lower, upper = bounds[name]["low"], bounds[name]["high"]
        if min(sample) < lower or max(sample) > upper:
            raise SimulationError("observations violate the preregistered support bounds")
        widths[name] = upper - lower
    count = len(analysis["primaryDesignPointIds"]) + len(analysis["challengeDesignPointIds"])
    marginal = 1 - (1 - analysis["intervalLevel"]) / count
    if not 0 < marginal < 1:
        raise SimulationError("adjusted bounded interval level is not representable")
    logarithm = math.log(2) + math.log(count) - math.log1p(-analysis["intervalLevel"])
    if analysis["pairing"] == "paired":
        spread = math.fsum([widths["baseline"], widths["comparison"]]) / math.sqrt(len(baseline))
        mode = "paired"
    else:
        spread = math.hypot(
            widths["baseline"] / math.sqrt(len(baseline)),
            widths["comparison"] / math.sqrt(len(comparison)),
        )
        mode = "unpaired"
    half_width = audit_number(spread * math.sqrt(logarithm / 2), "mean-difference-v3")
    floor = audit_number(bounds["comparison"]["low"] - bounds["baseline"]["high"], "mean-difference-v3")
    ceiling = audit_number(bounds["comparison"]["high"] - bounds["baseline"]["low"], "mean-difference-v3")
    return {
        "level": marginal,
        "low": audit_number(max(floor, center - half_width), "mean-difference-v3"),
        "high": audit_number(min(ceiling, center + half_width), "mean-difference-v3"),
        "method": f"hoeffding-{mode}-bonferroni-v3",
    }


def audit_point_result(
    spec: dict[str, Any],
    hypothesis: dict[str, Any],
    design_point_id: str,
    role: str,
    outcomes: list[dict[str, Any]],
    seeds_by_run: dict[str, int],
    analyzer: str,
) -> dict[str, Any]:
    analysis = hypothesis["analysis"]
    relevant: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in outcomes:
        if row["outcome_name"] == hypothesis["outcome"]:
            relevant[(row["design_point_id"], row["scenario_id"])].append(row)
    baseline_rows = sorted(
        relevant[(design_point_id, analysis["baselineScenarioId"])],
        key=lambda item: item["run_id"],
    )
    comparison_rows = sorted(
        relevant[(design_point_id, analysis["comparisonScenarioId"])],
        key=lambda item: item["run_id"],
    )
    planned = spec["replications"]
    if len(baseline_rows) != planned or len(comparison_rows) != planned:
        raise SimulationError(
            f"hypothesis {hypothesis['hypothesisId']} design point {design_point_id} "
            "does not have every planned scenario outcome"
        )
    baseline_values = [float(row["value"]) for row in baseline_rows]
    comparison_values = [float(row["value"]) for row in comparison_rows]
    pairing = analysis["pairing"]
    complete_pairs: int | None = None
    if pairing == "paired":
        baseline_by_coupling = {row["coupling_id"]: row for row in baseline_rows}
        comparison_by_coupling = {row["coupling_id"]: row for row in comparison_rows}
        if len(baseline_by_coupling) != planned or len(comparison_by_coupling) != planned:
            raise SimulationError("paired hypothesis contains duplicate coupling IDs")
        if set(baseline_by_coupling) != set(comparison_by_coupling):
            raise SimulationError("paired hypothesis has mismatched coupling IDs")
        differences: list[float] = []
        for coupling_id in sorted(baseline_by_coupling):
            baseline_row = baseline_by_coupling[coupling_id]
            comparison_row = comparison_by_coupling[coupling_id]
            if seeds_by_run[baseline_row["run_id"]] != seeds_by_run[comparison_row["run_id"]]:
                raise SimulationError("paired hypothesis has mismatched run seeds")
            differences.append(float(comparison_row["value"]) - float(baseline_row["value"]))
        complete_pairs = len(differences)
        estimate_raw = math.fsum(differences) / complete_pairs
        mcse_raw = math.sqrt(audit_variance(differences, estimate_raw) / complete_pairs)
        interval_method = "normal-wald-paired-v1"
    elif pairing == "independent":
        baseline_mean = math.fsum(baseline_values) / len(baseline_values)
        comparison_mean = math.fsum(comparison_values) / len(comparison_values)
        estimate_raw = comparison_mean - baseline_mean
        mcse_raw = math.sqrt(
            audit_variance(baseline_values, baseline_mean) / len(baseline_values)
            + audit_variance(comparison_values, comparison_mean) / len(comparison_values)
        )
        interval_method = "normal-wald-unpaired-v1"
    else:
        estimate_raw = comparison_values[0] - baseline_values[0]
        mcse_raw = 0.0
        interval_method = "none"
    estimate = audit_number(estimate_raw, analyzer)
    mcse = audit_number(mcse_raw, analyzer)
    is_bounded = analysis["intervalMethod"] == "bounded-hoeffding-bonferroni"
    if is_bounded:
        interval = audit_bounded_interval(analysis, baseline_values, comparison_values, estimate_raw)
    elif spec["uncertaintyMode"] == "stochastic":
        level = analysis["intervalLevel"]
        if analyzer in {"mean-difference-v2", "mean-difference-v3"}:
            suffix = analyzer.rsplit("-", 1)[1]
            interval_method = interval_method.replace("-v1", f"-{suffix}")
            if analysis["intervalMethod"] == "normal-approximation-bonferroni":
                comparisons = len(analysis["primaryDesignPointIds"]) + len(
                    analysis["challengeDesignPointIds"]
                )
                level = 1.0 - (1.0 - level) / comparisons
                interval_method = interval_method.replace(f"-{suffix}", f"-bonferroni-{suffix}")
        if not 0 < 0.5 + level / 2 < 1:
            raise SimulationError("normal quantile is outside the representable open unit interval")
        quantile = statistics.NormalDist().inv_cdf(0.5 + level / 2)
        interval: dict[str, Any] | None = {
            "level": level,
            "low": audit_number(estimate_raw - quantile * mcse_raw, analyzer),
            "high": audit_number(estimate_raw + quantile * mcse_raw, analyzer),
            "method": interval_method,
        }
    else:
        interval = None
    threshold = hypothesis["practicalThreshold"]
    result = {
        "designPointId": design_point_id,
        "role": role,
        "status": audit_point_status(threshold["operator"], threshold["value"], estimate, interval),
        "estimate": estimate,
        "interval": interval,
        "mcse": mcse,
        "sample": {
            "plannedPerScenario": planned,
            "baselineObserved": len(baseline_rows),
            "comparisonObserved": len(comparison_rows),
            "completePairs": complete_pairs,
        },
    }
    if analyzer in {"mean-difference-v2", "mean-difference-v3"}:
        diagnostics = []
        if spec["uncertaintyMode"] == "stochastic" and not is_bounded:
            if planned < 30:
                diagnostics.append("insufficient-replications-for-normal-decision")
            if mcse_raw == 0:
                diagnostics.append("zero-observed-contrast-variance")
        result["inferenceDiagnostics"] = diagnostics
        if diagnostics:
            result["status"] = "inconclusive"
    return result


def audit_hypothesis_result(
    spec: dict[str, Any],
    hypothesis: dict[str, Any],
    outcomes: list[dict[str, Any]],
    seeds_by_run: dict[str, int],
    analyzer: str,
) -> dict[str, Any]:
    analysis = hypothesis["analysis"]
    limitations = audit_limitations(spec, hypothesis, analyzer)
    if analysis["kind"] == "not-identifiable":
        status = "not-identifiable-from-design"
        return {
            "hypothesisId": hypothesis["hypothesisId"],
            "status": status,
            "estimand": hypothesis["estimand"],
            "analysisMethod": analysis,
            "threshold": hypothesis["practicalThreshold"],
            "designPointResults": [],
            "decision": audit_decision_text(status, hypothesis["hypothesisId"], analyzer),
            "modelConditional": True,
            "challengeSearch": {
                "performed": False,
                "method": "",
                "summary": analysis["reason"],
                "reversalFound": False,
                "reversalDesignPointIds": [],
            },
            "limitations": limitations,
        }
    roles = {
        **{value: "primary" for value in analysis["primaryDesignPointIds"]},
        **{value: "challenge" for value in analysis["challengeDesignPointIds"]},
    }
    points = [
        audit_point_result(spec, hypothesis, design_id, roles[design_id], outcomes, seeds_by_run, analyzer)
        for design_id in sorted(roles)
    ]
    challenging = sorted(
        item["designPointId"] for item in points if item["status"] == "challenges"
    )
    inconclusive = sorted(
        item["designPointId"] for item in points if item["status"] == "inconclusive"
    )
    if challenging:
        status = "challenges-under-model"
    elif inconclusive:
        status = "inconclusive-under-model"
    else:
        status = "supports-under-model"
    challenge_ids = set(analysis["challengeDesignPointIds"])
    reversals = sorted(
        item["designPointId"]
        for item in points
        if item["designPointId"] in challenge_ids and item["status"] == "challenges"
    )
    return {
        "hypothesisId": hypothesis["hypothesisId"],
        "status": status,
        "estimand": hypothesis["estimand"],
        "analysisMethod": analysis,
        "threshold": hypothesis["practicalThreshold"],
        "designPointResults": points,
        "decision": audit_decision_text(status, hypothesis["hypothesisId"], analyzer),
        "modelConditional": True,
        "challengeSearch": {
            "performed": True,
            "method": "preregistered challenge design points",
            "summary": (
                "Challenge design points that contradicted the threshold: "
                + (", ".join(reversals) if reversals else "none")
                + "."
            ),
            "reversalFound": bool(reversals),
            "reversalDesignPointIds": reversals,
        },
        "limitations": limitations,
    }


def validate_hypothesis_results(
    root: Path,
    spec: dict[str, Any],
    runs: list[dict[str, str]],
    outcomes: list[dict[str, Any]],
) -> tuple[str | None, Counter[str]]:
    path = root / "analysis/hypothesis-results.json"
    if not spec["hypotheses"]:
        if path.exists():
            raise SimulationError("hypothesis results must not exist when no hypotheses are declared")
        return None, Counter()
    if not path.is_file():
        raise SimulationError("analysis/hypothesis-results.json is required for declared hypotheses")
    value, raw = load_json(path, "analysis/hypothesis-results.json")
    report = require_object(value, "analysis/hypothesis-results.json")
    require_exact_keys(
        report,
        {
            "schemaVersion",
            "toolVersion",
            "analyzer",
            "experimentId",
            "analysisPhase",
            "generatedAt",
            "inputHashes",
            "results",
        },
        "analysis/hypothesis-results.json",
    )
    report_schema_version = require_nonnegative_integer(
        report["schemaVersion"], "analysis/hypothesis-results.json.schemaVersion"
    )
    if report_schema_version != SCHEMA_VERSION or report["toolVersion"] != TOOL_VERSION:
        raise SimulationError("hypothesis results schema or tool version is unsupported")
    analyzer = require_text(report["analyzer"], "analysis/hypothesis-results.json.analyzer")
    if analyzer not in {"mean-difference-v1", "mean-difference-v2", "mean-difference-v3"}:
        raise SimulationError("hypothesis results analyzer is unsupported")
    if analyzer != "mean-difference-v3" and any(
        h["analysis"].get("intervalMethod") == "bounded-hoeffding-bonferroni"
        for h in spec["hypotheses"]
    ):
        raise SimulationError("bounded inference requires mean-difference-v3")
    if report["analyzer"] == "mean-difference-v1" and any(
        h["analysis"].get("intervalMethod") == "normal-approximation-bonferroni"
        for h in spec["hypotheses"]
    ):
        raise SimulationError("legacy analyzer cannot certify Bonferroni intervals")
    if report["experimentId"] != spec["experimentId"] or report["analysisPhase"] != spec["phase"]:
        raise SimulationError("hypothesis results identity differs from experiment.json")
    parse_iso8601(report["generatedAt"], "analysis/hypothesis-results.json.generatedAt")
    expected_hashes = {
        "normalizedSpec": hashlib.sha256(canonical_json_bytes(spec)).hexdigest(),
        "runs": sha256_file(root / "data/runs.csv"),
        "outcomes": sha256_file(root / "data/outcomes.csv"),
    }
    if report["inputHashes"] != expected_hashes:
        raise SimulationError("hypothesis results input hashes do not match the validated bundle")
    seeds_by_run = {row["run_id"]: int(row["seed"]) for row in runs}
    expected_results = [
        audit_hypothesis_result(spec, hypothesis, outcomes, seeds_by_run, report["analyzer"])
        for hypothesis in spec["hypotheses"]
    ]
    if canonical_json_bytes(report["results"]) != canonical_json_bytes(expected_results):
        raise SimulationError(
            "hypothesis results do not match independent recomputation from runs and outcomes"
        )
    if raw != canonical_json_bytes(report):
        raise SimulationError("analysis/hypothesis-results.json must use canonical JSON")
    statuses = Counter(result["status"] for result in expected_results)
    return sha256_bytes(raw), statuses


def command_validate(args: argparse.Namespace) -> int:
    root = args.root.resolve()
    if not root.is_dir():
        raise SimulationError("bundle root must be an existing directory")
    spec, spec_raw, plan_rows = verify_plan(root)
    manifest, manifest_counts = validate_manifest(root, spec, spec_raw, plan_rows)
    rows, ok_ids, status_by_id = validate_runs(root, plan_rows, manifest_counts)
    run_map = {row["run_id"]: row for row in rows}
    outcomes = validate_outcomes(root, spec, rows, ok_ids)
    declared_time_unit = spec.get("timeUnit")
    observation_count = validate_observations(root, run_map, declared_time_unit)
    event_count = validate_events(root, run_map, declared_time_unit)
    diagnostic_count = validate_diagnostics(root, run_map, status_by_id)
    summary_count = validate_summary(root, spec, outcomes, ok_ids)
    validate_dictionary_and_queries(root, spec)
    row_counts = validate_file_records(root, manifest)
    complete = manifest["status"] == "complete"
    if not complete:
        if not args.allow_incomplete:
            raise SimulationError(
                "execution is incomplete; use --allow-incomplete only for diagnostic inspection"
            )
        hypothesis_digest = None
        hypothesis_statuses: Counter[str] = Counter()
    else:
        hypothesis_digest, hypothesis_statuses = validate_hypothesis_results(
            root, spec, rows, outcomes
        )

    report = {
        "schemaVersion": SCHEMA_VERSION,
        "toolVersion": TOOL_VERSION,
        "ok": complete,
        "releaseEligible": complete,
        "experimentId": spec["experimentId"],
        "executionStatus": manifest["status"],
        "runCounts": manifest_counts,
        "rowCounts": {
            **row_counts,
            "validatedObservations": observation_count,
            "validatedEvents": event_count,
            "validatedDiagnostics": diagnostic_count,
            "recomputedSummaries": summary_count,
        },
        "hypothesisStatuses": dict(sorted(hypothesis_statuses.items())),
        "modelReview": variable_review_summary(spec),
        "unresolvedHypothesisIds": (
            [] if complete else [item["hypothesisId"] for item in spec["hypotheses"]]
        ),
        "digests": {
            "experiment": sha256_bytes(spec_raw),
            "planManifest": sha256_file(root / "design/plan-manifest.json"),
            "executionManifest": sha256_file(root / "execution-manifest.json"),
            "hypothesisResults": hypothesis_digest,
        },
        "verifiedFiles": sorted([
            *REQUIRED_MANIFEST_FILES,
            *(f"design/{name}" for name in build_variable_review_files(spec)),
        ]),
    }
    payload = canonical_json_bytes(report)
    if args.report is not None:
        report_path = args.report.resolve()
        if report_path.exists():
            raise SimulationError("validation report already exists; refusing to replace it")
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_bytes(payload)
    sys.stdout.buffer.write(payload)
    return 0 if complete else 2


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Validate simulation run completeness, hashes, tidy tables, summaries, and model-conditional claims."
    )
    parser.add_argument("--root", type=Path, required=True, help="simulation bundle root")
    parser.add_argument("--report", type=Path, help="optional fresh path for the canonical JSON audit report")
    parser.add_argument(
        "--allow-incomplete",
        action="store_true",
        help="permit failed or invalid runs for diagnostic inspection; never treat that result as release evidence",
    )
    parser.set_defaults(handler=command_validate)
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
