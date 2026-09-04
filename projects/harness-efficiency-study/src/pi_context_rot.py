"""Offline context-length, compaction-quality, and retry cost simulator.

This module is intentionally standard-library only.  It consumes the versioned
CSV bundle produced by ``pi_cost_elasticity.py`` and never imports, executes, or
contacts Pi, Copilot, a model provider, or any API.

The quality mechanism is a transparent sensitivity model, not an empirical
estimate for GPT-5.6.  Historical benchmark slopes are retained only as clearly
labelled proxy design points.
"""

from __future__ import annotations

import csv
import gzip
import hashlib
import io
import json
import math
import platform
import random
import zlib
from collections import defaultdict
from collections.abc import Mapping, Sequence
from itertools import pairwise
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "1.0.0"
MODEL_VERSION = "1.0.0"
STUDY_ID = "pi-context-rot-cost-quality-sensitivity-20260904"
SOURCE_TYPE = "simulated"
COMPLETION_SLO = 0.95
MAIN_CALL_COUNT = 39
MONTE_CARLO_SEED = 20_260_904
MONTE_CARLO_TASKS = 200_000
NORMAL_95 = 1.959963984540054

MODELS = ("luna", "terra", "sol")
GENERIC_ONSETS = (16_000.0, 32_000.0, 113_000.0, 200_000.0, 400_000.0, 600_000.0)
GENERIC_BETAS = (0.0, 0.25, 0.5, 1.0, 2.0)
FIDELITY_VALUES = (1.0, 0.99, 0.97, 0.95, 0.9, 0.8)
MAX_ATTEMPTS_VALUES = (1, 3)
EVIDENCE_PROFILES = ("uniform", "front_loaded", "back_loaded")
RETENTION_THRESHOLDS = (0.95, 0.90, 0.85, 0.80, 0.70, 0.50)
GZIP_COMPRESSION_LEVEL = 9
GZIP_ARTIFACTS = (
    "quality-stratum-results.csv.gz",
    "quality-aggregate-results.csv.gz",
    "quality-contrast-results.csv.gz",
    "break-even.csv.gz",
    "scale-results.csv.gz",
)
SCALE_ASSIGNED_SESSIONS = (1_000, 1_000_000)

TASK_STRATA = (
    {"stratum_id": "easy", "weight": 0.25, "baseline_success_probability": 0.95},
    {"stratum_id": "typical", "weight": 0.50, "baseline_success_probability": 0.80},
    {"stratum_id": "hard", "weight": 0.25, "baseline_success_probability": 0.55},
)

# Fixed low-anchor onsets and exact final calibrated slopes supplied by the
# evidence audit.  These are historical task proxies, never GPT-5.6 estimates.
CALIBRATED_PROXY_PROFILES = (
    {
        "calibration_id": "chroma-context-rot-proxy",
        "onset_tokens": 268.617647,
        "beta": 1.260046681,
        "beta_provenance": (
            "Historical Chroma Context Rot proxy: 267/306 at 268.617647 mean "
            "tokens versus 191/306 at 112672.843137 mean tokens."
        ),
    },
    {
        "calibration_id": "ruler-gpt-4-1106-proxy",
        "onset_tokens": 4_000.0,
        "beta": 1.519149139,
        "beta_provenance": (
            "Historical RULER GPT-4-1106 proxy: probability 0.966 at 4k "
            "tokens versus 0.812 at 128k tokens."
        ),
    },
    {
        "calibration_id": "nolima-gpt-4-1-proxy",
        "onset_tokens": 1_000.0,
        "beta": 1.947000033,
        "beta_provenance": (
            "Historical NoLiMa GPT-4.1 proxy: probability 0.956 at 1k "
            "tokens versus 0.647 at 128k tokens."
        ),
    },
)

PRIMARY_PARAMETER_ID = "primary-onset-200k-half-odds-f095-k3-uniform"
PRIMARY_ONSET_TOKENS = 200_000.0
PRIMARY_GROW_EXCESS_AUC = 31.0 / 13.0
PRIMARY_BETA = -math.log(0.5) / PRIMARY_GROW_EXCESS_AUC

STRATEGY_SOURCES: Mapping[str, tuple[str, str]] = {
    "grow_to_800k": ("long-cap-200k-uncached", "baseline"),
    "cap_200k_uncached": ("long-cap-200k-uncached", "comparison"),
    "cap_200k_cache_read": ("compaction-input-cache-read-sensitivity", "comparison"),
    "cap_200k_cache_write": ("compaction-input-cache-write-sensitivity", "comparison"),
    "cap_pricing_threshold_uncached": (
        "long-cap-pricing-threshold-uncached",
        "comparison",
    ),
}

EVIDENCE_INPUT_COLUMNS = (
    "evidence_id",
    "series_id",
    "study",
    "model",
    "task",
    "metric",
    "context_tokens",
    "score",
    "score_unit",
    "sample_size",
    "sample_unit",
    "evidence_status",
    "numeric_precision",
    "source_location",
    "source_url",
    "derivation",
    "uncertainty",
    "limitations",
    "target_model_scope",
)

TRAJECTORY_COLUMNS = (
    "trajectory_id",
    "model",
    "strategy_id",
    "source_contrast_id",
    "source_scenario_id",
    "source_role",
    "main_call_count",
    "compaction_count",
    "compaction_positions_json",
    "prompt_sequence_tokens_json",
    "minimum_prompt_tokens",
    "mean_prompt_tokens",
    "maximum_prompt_tokens",
    "provider_cost_per_attempt_usd",
    "onset_tokens",
    "excess_token_call_area",
    "normalized_excess_auc",
    "normalization_formula",
    "source_type",
)

QUALITY_COMMON_COLUMNS = (
    "parameter_set_id",
    "design_role",
    "model",
    "strategy_id",
    "source_scenario_id",
    "source_contrast_id",
    "source_role",
    "calibration_id",
    "onset_tokens",
    "beta",
    "beta_provenance",
    "target_model_scope",
    "per_compaction_fidelity",
    "evidence_profile",
    "max_attempts",
    "normalized_excess_auc",
    "effective_evidence_fidelity",
)

STRATUM_COLUMNS = QUALITY_COMMON_COLUMNS + (
    "stratum_id",
    "stratum_weight",
    "baseline_success_probability",
    "single_attempt_success_probability",
    "completion_probability",
    "expected_attempts",
    "provider_cost_per_attempt_usd",
    "weighted_completion_contribution",
    "weighted_attempts_contribution",
    "weighted_assigned_cost_contribution_usd",
    "source_type",
)

AGGREGATE_COLUMNS = QUALITY_COMMON_COLUMNS + (
    "weighted_baseline_success_probability",
    "weighted_single_attempt_success_probability",
    "completion_probability",
    "expected_attempts",
    "provider_cost_per_attempt_usd",
    "provider_cost_per_assigned_session_usd",
    "provider_cost_per_successful_session_usd",
    "completion_slo_target",
    "completion_slo_met",
    "source_type",
)

CONTRAST_COLUMNS = (
    "quality_contrast_id",
    "parameter_set_id",
    "design_role",
    "model",
    "baseline_strategy_id",
    "comparison_strategy_id",
    "calibration_id",
    "onset_tokens",
    "beta",
    "per_compaction_fidelity",
    "evidence_profile",
    "max_attempts",
    "baseline_completion_probability",
    "comparison_completion_probability",
    "delta_completion_probability_comparison_minus_baseline",
    "baseline_expected_attempts",
    "comparison_expected_attempts",
    "delta_expected_attempts_comparison_minus_baseline",
    "baseline_provider_cost_per_assigned_session_usd",
    "comparison_provider_cost_per_assigned_session_usd",
    "provider_cost_savings_per_assigned_session_usd",
    "baseline_provider_cost_per_successful_session_usd",
    "comparison_provider_cost_per_successful_session_usd",
    "delta_provider_cost_per_successful_session_usd",
    "baseline_completion_slo_met",
    "comparison_completion_slo_met",
    "dominance_status",
    "source_type",
)

BREAK_EVEN_COLUMNS = (
    "break_even_id",
    "quality_contrast_id",
    "parameter_set_id",
    "model",
    "comparison_strategy_id",
    "provider_cost_savings_per_assigned_session_usd",
    "completion_probability_loss",
    "break_even_failure_loss_usd_per_incremental_unresolved_session",
    "break_even_status",
    "interpretation",
    "source_type",
)

SCALE_COLUMNS = (
    "scale_result_id",
    "parameter_set_id",
    "design_role",
    "model",
    "strategy_id",
    "calibration_id",
    "onset_tokens",
    "beta",
    "per_compaction_fidelity",
    "evidence_profile",
    "max_attempts",
    "assigned_sessions",
    "expected_completed_sessions",
    "expected_unresolved_sessions",
    "expected_provider_spend_usd",
    "provider_cost_per_successful_session_usd",
    "completion_probability",
    "source_type",
)

MONTE_CARLO_COLUMNS = (
    "monte_carlo_id",
    "parameter_set_id",
    "model",
    "baseline_strategy_id",
    "comparison_strategy_id",
    "task_count",
    "seed",
    "rng",
    "coupling",
    "max_attempts",
    "analytic_baseline_completion_probability",
    "analytic_comparison_completion_probability",
    "analytic_delta_completion_probability",
    "mc_baseline_completion_probability",
    "mc_comparison_completion_probability",
    "mc_delta_completion_probability",
    "mcse_delta_completion_probability",
    "ci95_low_delta_completion_probability",
    "ci95_high_delta_completion_probability",
    "analytic_baseline_cost_per_successful_session_usd",
    "analytic_comparison_cost_per_successful_session_usd",
    "analytic_delta_cost_per_successful_session_usd",
    "mc_baseline_cost_per_successful_session_usd",
    "mc_comparison_cost_per_successful_session_usd",
    "mc_delta_cost_per_successful_session_usd",
    "mcse_delta_cost_per_successful_session_usd",
    "ci95_low_delta_cost_per_successful_session_usd",
    "ci95_high_delta_cost_per_successful_session_usd",
    "completion_delta_analytic_inside_ci95",
    "cost_delta_analytic_inside_ci95",
    "source_type",
)

FIDELITY_BOUNDARY_COLUMNS = (
    "boundary_id",
    "parameter_set_id",
    "model",
    "baseline_strategy_id",
    "comparison_strategy_id",
    "onset_tokens",
    "evidence_profile",
    "max_attempts",
    "baseline_beta_for_fidelity_search",
    "fixed_fidelity_for_beta_search",
    "fidelity_search_lower_bound",
    "fidelity_search_upper_bound",
    "beta_search_lower_bound",
    "beta_search_upper_bound",
    "bisection_tolerance",
    "bisection_max_iterations",
    "minimum_fidelity_cost_per_success_not_above_grow",
    "minimum_fidelity_cost_status",
    "minimum_fidelity_completion_slo",
    "minimum_fidelity_completion_slo_status",
    "minimum_beta_at_f095_cost_per_success_not_above_grow",
    "minimum_beta_cost_status",
    "grow_cost_per_attempt_usd",
    "comparison_cost_per_attempt_usd",
    "source_type",
)

EVIDENCE_CURVE_COLUMNS = EVIDENCE_INPUT_COLUMNS + (
    "anchor_eligible",
    "reference_evidence_id",
    "reference_context_tokens",
    "reference_score",
    "retention",
    "curve_order",
)

EVIDENCE_ONSET_COLUMNS = (
    "evidence_onset_id",
    "series_id",
    "study",
    "model",
    "task",
    "metric",
    "retention_threshold",
    "threshold_status",
    "interpolated_context_tokens",
    "lower_evidence_id",
    "upper_evidence_id",
    "lower_context_tokens",
    "upper_context_tokens",
    "lower_retention",
    "upper_retention",
    "interpolation_scale",
    "anchor_count",
    "target_model_scope",
    "limitations",
)


def _truthy(value: Any) -> bool:
    return str(value).strip().lower() in {"1", "true", "yes", "y"}


def _finite_float(value: Any, field: str) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{field} must be numeric; got {value!r}") from exc
    if not math.isfinite(number):
        raise ValueError(f"{field} must be finite; got {value!r}")
    return number


def _read_csv(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        raise FileNotFoundError(path)
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise ValueError(f"CSV has no header: {path}")
        return [dict(row) for row in reader]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _canonical_float(value: float) -> str:
    if not math.isfinite(value):
        raise ValueError(f"Cannot serialize non-finite value: {value!r}")
    if value == 0:
        return "0"
    return format(value, ".15g")


def _csv_value(value: Any) -> Any:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, float):
        return _canonical_float(value)
    if value is None:
        return ""
    return value


def _write_csv(
    path: Path, rows: Sequence[Mapping[str, Any]], columns: Sequence[str]
) -> None:
    if path.suffix == ".gz":
        raw_handle = path.open("wb")
        compressed_handle = gzip.GzipFile(
            filename="",
            mode="wb",
            compresslevel=GZIP_COMPRESSION_LEVEL,
            fileobj=raw_handle,
            mtime=0,
        )
        handle = io.TextIOWrapper(
            compressed_handle, encoding="utf-8", newline="", write_through=True
        )
    else:
        raw_handle = None
        compressed_handle = None
        handle = path.open("w", encoding="utf-8", newline="")
    try:
        writer = csv.DictWriter(handle, fieldnames=list(columns), lineterminator="\n")
        writer.writeheader()
        for row in rows:
            unexpected = set(row) - set(columns)
            if unexpected:
                raise ValueError(
                    f"Unexpected columns for {path.name}: {sorted(unexpected)}"
                )
            writer.writerow({column: _csv_value(row.get(column)) for column in columns})
    finally:
        handle.close()
        if compressed_handle is not None and not compressed_handle.closed:
            compressed_handle.close()
        if raw_handle is not None and not raw_handle.closed:
            raw_handle.close()


def _write_text(path: Path, text: str) -> None:
    path.write_text(text.rstrip("\n") + "\n", encoding="utf-8", newline="\n")


def _json_text(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def _slug_number(value: float) -> str:
    if float(value).is_integer():
        return str(int(value))
    return _canonical_float(value).replace(".", "p").replace("-", "m")


def logit(probability: float) -> float:
    if not 0.0 < probability < 1.0:
        raise ValueError("probability must be strictly between zero and one")
    return math.log(probability) - math.log1p(-probability)


def logistic(value: float) -> float:
    if value >= 0.0:
        return 1.0 / (1.0 + math.exp(-value))
    exp_value = math.exp(value) if value > -745.0 else 0.0
    return exp_value / (1.0 + exp_value)


def normalized_excess_auc(prompt_tokens: Sequence[float], onset_tokens: float) -> float:
    """Return excess token-call area in fixed 100k-token units per call.

    ``sum(max(prompt_i - onset, 0)) / (100000 * n)`` gives the required
    31/13 oracle for a 40k..800k by-20k trajectory with a 200k onset.
    """

    if not prompt_tokens:
        raise ValueError("prompt_tokens must not be empty")
    if onset_tokens <= 0.0 or not math.isfinite(onset_tokens):
        raise ValueError("onset_tokens must be finite and positive")
    prompts = [_finite_float(value, "prompt_tokens") for value in prompt_tokens]
    if any(value < 0.0 for value in prompts):
        raise ValueError("prompt token counts must be non-negative")
    excess = sum(max(value - onset_tokens, 0.0) for value in prompts)
    return excess / (100_000.0 * len(prompts))


def profile_weights(call_count: int, profile: str) -> list[float]:
    if call_count <= 0:
        raise ValueError("call_count must be positive")
    if profile == "uniform":
        return [1.0] * call_count
    if profile == "front_loaded":
        return [float(call_count - index + 1) for index in range(1, call_count + 1)]
    if profile == "back_loaded":
        return [float(index) for index in range(1, call_count + 1)]
    raise ValueError(f"Unknown evidence profile: {profile!r}")


def effective_evidence_fidelity(
    call_count: int,
    compaction_positions: Sequence[int],
    per_compaction_fidelity: float,
    evidence_profile: str = "uniform",
) -> float:
    """Weighted retention of evidence introduced across the call trajectory.

    A compaction recorded at logical position ``j`` happens after main call ``j``
    and before call ``j + 1``.  Evidence introduced on call ``i`` is therefore
    transformed by each compaction whose position is greater than or equal to
    ``i``.  This convention yields four losses for evidence from calls 1..9 in
    the cap-200k trajectory, three for calls 10..18, and so on.
    """

    fidelity = _finite_float(per_compaction_fidelity, "per_compaction_fidelity")
    if not 0.0 <= fidelity <= 1.0:
        raise ValueError("per_compaction_fidelity must be in [0, 1]")
    positions = [int(value) for value in compaction_positions]
    if positions != sorted(positions) or len(set(positions)) != len(positions):
        raise ValueError("compaction_positions must be unique and sorted")
    if any(position < 1 or position > call_count for position in positions):
        raise ValueError("compaction position is outside the call trajectory")
    weights = profile_weights(call_count, evidence_profile)
    retained = 0.0
    total_weight = sum(weights)
    for call_index, weight in enumerate(weights, start=1):
        subsequent_losses = sum(position >= call_index for position in positions)
        retained += weight * fidelity**subsequent_losses
    return retained / total_weight


def single_attempt_probability(
    baseline_probability: float,
    beta: float,
    excess_auc: float,
    evidence_fidelity: float,
) -> float:
    if beta < 0.0 or excess_auc < 0.0:
        raise ValueError("beta and excess_auc must be non-negative")
    if not 0.0 < evidence_fidelity <= 1.0:
        raise ValueError("evidence_fidelity must be in (0, 1]")
    return logistic(
        logit(baseline_probability) - beta * excess_auc + math.log(evidence_fidelity)
    )


def capped_retry_metrics(probability: float, max_attempts: int) -> tuple[float, float]:
    """Return completion probability and expected attempts including the first."""

    if not 0.0 <= probability <= 1.0:
        raise ValueError("probability must be in [0, 1]")
    if max_attempts < 1:
        raise ValueError("max_attempts must be at least one")
    failure_probability = 1.0 - probability
    completion = 1.0 - failure_probability**max_attempts
    expected_attempts = sum(
        failure_probability**attempt for attempt in range(max_attempts)
    )
    return completion, expected_attempts


def _load_cost_trajectories(
    cost_bundle: Path,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    scenario_path = cost_bundle / "scenario-results.csv"
    ledger_path = cost_bundle / "call-ledger.csv"
    scenarios = _read_csv(scenario_path)
    ledger = _read_csv(ledger_path)
    by_scenario: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in ledger:
        by_scenario[row["scenario_id"]].append(row)

    trajectories: list[dict[str, Any]] = []
    for model in MODELS:
        for strategy_id, (contrast_id, role) in STRATEGY_SOURCES.items():
            matches = [
                row
                for row in scenarios
                if row.get("model") == model
                and row.get("contrast_id") == contrast_id
                and row.get("role") == role
            ]
            if len(matches) != 1:
                raise ValueError(
                    f"Expected one scenario for model={model}, strategy={strategy_id}; "
                    f"found {len(matches)}"
                )
            scenario = matches[0]
            scenario_id = scenario["scenario_id"]
            calls = sorted(
                by_scenario.get(scenario_id, []), key=lambda row: int(row["call_index"])
            )
            if not calls:
                raise ValueError(f"No ledger rows for {scenario_id}")
            main_calls = [
                row for row in calls if row.get("call_kind") == "main_model_call"
            ]
            if len(main_calls) != MAIN_CALL_COUNT:
                raise ValueError(
                    f"{scenario_id} must contain {MAIN_CALL_COUNT} main calls; "
                    f"found {len(main_calls)}"
                )
            logical_steps = [int(row["logical_step"]) for row in main_calls]
            if logical_steps != list(range(1, MAIN_CALL_COUNT + 1)):
                raise ValueError(
                    f"Unexpected main-call logical steps for {scenario_id}"
                )
            prompts = [int(row["full_input_tokens"]) for row in main_calls]
            positions = [
                int(row["logical_step"])
                for row in calls
                if row.get("call_kind") == "compaction"
                and _truthy(row.get("compaction_event"))
            ]
            if positions != sorted(positions):
                raise ValueError(
                    f"Compaction positions are not ordered for {scenario_id}"
                )
            provider_cost = _finite_float(
                scenario["provider_cost_usd"], "provider_cost_usd"
            )
            trajectories.append(
                {
                    "model": model,
                    "strategy_id": strategy_id,
                    "source_contrast_id": contrast_id,
                    "source_scenario_id": scenario_id,
                    "source_role": role,
                    "main_call_count": len(prompts),
                    "compaction_count": len(positions),
                    "compaction_positions": positions,
                    "prompt_sequence_tokens": prompts,
                    "minimum_prompt_tokens": min(prompts),
                    "mean_prompt_tokens": sum(prompts) / len(prompts),
                    "maximum_prompt_tokens": max(prompts),
                    "provider_cost_per_attempt_usd": provider_cost,
                }
            )
    return trajectories, {
        "scenario-results.csv": sha256_file(scenario_path),
        "call-ledger.csv": sha256_file(ledger_path),
    }


def build_parameter_settings() -> list[dict[str, Any]]:
    settings: list[dict[str, Any]] = []
    for onset in GENERIC_ONSETS:
        for beta in GENERIC_BETAS:
            for fidelity in FIDELITY_VALUES:
                for max_attempts in MAX_ATTEMPTS_VALUES:
                    for profile in EVIDENCE_PROFILES:
                        parameter_id = (
                            f"sensitivity-o{_slug_number(onset)}-b{_slug_number(beta)}-"
                            f"f{_slug_number(fidelity)}-k{max_attempts}-{profile}"
                        )
                        settings.append(
                            {
                                "parameter_set_id": parameter_id,
                                "design_role": "sensitivity",
                                "calibration_id": "generic-elasticity-grid",
                                "onset_tokens": onset,
                                "beta": beta,
                                "beta_provenance": "Assumed generic elasticity sensitivity value.",
                                "target_model_scope": "hypothetical-not-empirical-calibration",
                                "per_compaction_fidelity": fidelity,
                                "evidence_profile": profile,
                                "max_attempts": max_attempts,
                            }
                        )

    for calibration in CALIBRATED_PROXY_PROFILES:
        for fidelity in FIDELITY_VALUES:
            for max_attempts in MAX_ATTEMPTS_VALUES:
                for profile in EVIDENCE_PROFILES:
                    parameter_id = (
                        f"proxy-{calibration['calibration_id']}-"
                        f"f{_slug_number(fidelity)}-k{max_attempts}-{profile}"
                    )
                    settings.append(
                        {
                            "parameter_set_id": parameter_id,
                            "design_role": "historical_proxy_challenge",
                            "calibration_id": calibration["calibration_id"],
                            "onset_tokens": calibration["onset_tokens"],
                            "beta": calibration["beta"],
                            "beta_provenance": calibration["beta_provenance"],
                            "target_model_scope": "historical-proxy-not-gpt-5.6-calibration",
                            "per_compaction_fidelity": fidelity,
                            "evidence_profile": profile,
                            "max_attempts": max_attempts,
                        }
                    )

    settings.append(
        {
            "parameter_set_id": PRIMARY_PARAMETER_ID,
            "design_role": "primary",
            "calibration_id": "primary-half-odds-at-grow-trajectory",
            "onset_tokens": PRIMARY_ONSET_TOKENS,
            "beta": PRIMARY_BETA,
            "beta_provenance": (
                "Assumed so the grow-to-800k trajectory multiplies baseline odds "
                "by 0.5 when normalized excess AUC is 31/13."
            ),
            "target_model_scope": "hypothetical-not-empirical-calibration",
            "per_compaction_fidelity": 0.95,
            "evidence_profile": "uniform",
            "max_attempts": 3,
        }
    )
    if len({row["parameter_set_id"] for row in settings}) != len(settings):
        raise AssertionError("Parameter IDs are not unique")
    return settings


def _trajectory_metric_rows(
    trajectories: Sequence[Mapping[str, Any]], settings: Sequence[Mapping[str, Any]]
) -> tuple[list[dict[str, Any]], dict[tuple[str, str, float], dict[str, Any]]]:
    onsets = sorted({float(setting["onset_tokens"]) for setting in settings})
    rows: list[dict[str, Any]] = []
    lookup: dict[tuple[str, str, float], dict[str, Any]] = {}
    for trajectory in trajectories:
        prompts = trajectory["prompt_sequence_tokens"]
        for onset in onsets:
            excess_area = sum(max(float(value) - onset, 0.0) for value in prompts)
            auc = normalized_excess_auc(prompts, onset)
            row = {
                "trajectory_id": (
                    f"{trajectory['model']}-{trajectory['strategy_id']}-o{_slug_number(onset)}"
                ),
                "model": trajectory["model"],
                "strategy_id": trajectory["strategy_id"],
                "source_contrast_id": trajectory["source_contrast_id"],
                "source_scenario_id": trajectory["source_scenario_id"],
                "source_role": trajectory["source_role"],
                "main_call_count": trajectory["main_call_count"],
                "compaction_count": trajectory["compaction_count"],
                "compaction_positions_json": json.dumps(
                    trajectory["compaction_positions"], separators=(",", ":")
                ),
                "prompt_sequence_tokens_json": json.dumps(
                    prompts, separators=(",", ":")
                ),
                "minimum_prompt_tokens": trajectory["minimum_prompt_tokens"],
                "mean_prompt_tokens": trajectory["mean_prompt_tokens"],
                "maximum_prompt_tokens": trajectory["maximum_prompt_tokens"],
                "provider_cost_per_attempt_usd": trajectory[
                    "provider_cost_per_attempt_usd"
                ],
                "onset_tokens": onset,
                "excess_token_call_area": excess_area,
                "normalized_excess_auc": auc,
                "normalization_formula": "sum(max(prompt_i-onset,0))/(100000*main_call_count)",
                "source_type": SOURCE_TYPE,
            }
            rows.append(row)
            lookup[
                (str(trajectory["model"]), str(trajectory["strategy_id"]), onset)
            ] = row
    return rows, lookup


def _quality_rows(
    trajectories: Sequence[Mapping[str, Any]],
    settings: Sequence[Mapping[str, Any]],
    trajectory_lookup: Mapping[tuple[str, str, float], Mapping[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    stratum_rows: list[dict[str, Any]] = []
    aggregate_rows: list[dict[str, Any]] = []
    for setting in settings:
        onset = float(setting["onset_tokens"])
        for trajectory in trajectories:
            metric = trajectory_lookup[
                (trajectory["model"], trajectory["strategy_id"], onset)
            ]
            evidence_fidelity = effective_evidence_fidelity(
                MAIN_CALL_COUNT,
                trajectory["compaction_positions"],
                float(setting["per_compaction_fidelity"]),
                str(setting["evidence_profile"]),
            )
            common = {
                "parameter_set_id": setting["parameter_set_id"],
                "design_role": setting["design_role"],
                "model": trajectory["model"],
                "strategy_id": trajectory["strategy_id"],
                "source_scenario_id": trajectory["source_scenario_id"],
                "source_contrast_id": trajectory["source_contrast_id"],
                "source_role": trajectory["source_role"],
                "calibration_id": setting["calibration_id"],
                "onset_tokens": onset,
                "beta": setting["beta"],
                "beta_provenance": setting["beta_provenance"],
                "target_model_scope": setting["target_model_scope"],
                "per_compaction_fidelity": setting["per_compaction_fidelity"],
                "evidence_profile": setting["evidence_profile"],
                "max_attempts": setting["max_attempts"],
                "normalized_excess_auc": metric["normalized_excess_auc"],
                "effective_evidence_fidelity": evidence_fidelity,
            }
            weighted_p0 = 0.0
            weighted_single = 0.0
            weighted_completion = 0.0
            weighted_attempts = 0.0
            weighted_cost = 0.0
            cost_per_attempt = float(trajectory["provider_cost_per_attempt_usd"])
            for stratum in TASK_STRATA:
                weight = float(stratum["weight"])
                p0 = float(stratum["baseline_success_probability"])
                p_single = single_attempt_probability(
                    p0,
                    float(setting["beta"]),
                    float(metric["normalized_excess_auc"]),
                    evidence_fidelity,
                )
                completion, expected_attempts = capped_retry_metrics(
                    p_single, int(setting["max_attempts"])
                )
                assigned_cost = cost_per_attempt * expected_attempts
                row = dict(common)
                row.update(
                    {
                        "stratum_id": stratum["stratum_id"],
                        "stratum_weight": weight,
                        "baseline_success_probability": p0,
                        "single_attempt_success_probability": p_single,
                        "completion_probability": completion,
                        "expected_attempts": expected_attempts,
                        "provider_cost_per_attempt_usd": cost_per_attempt,
                        "weighted_completion_contribution": weight * completion,
                        "weighted_attempts_contribution": weight * expected_attempts,
                        "weighted_assigned_cost_contribution_usd": weight
                        * assigned_cost,
                        "source_type": SOURCE_TYPE,
                    }
                )
                stratum_rows.append(row)
                weighted_p0 += weight * p0
                weighted_single += weight * p_single
                weighted_completion += weight * completion
                weighted_attempts += weight * expected_attempts
                weighted_cost += weight * assigned_cost
            aggregate = dict(common)
            aggregate.update(
                {
                    "weighted_baseline_success_probability": weighted_p0,
                    "weighted_single_attempt_success_probability": weighted_single,
                    "completion_probability": weighted_completion,
                    "expected_attempts": weighted_attempts,
                    "provider_cost_per_attempt_usd": cost_per_attempt,
                    "provider_cost_per_assigned_session_usd": weighted_cost,
                    "provider_cost_per_successful_session_usd": (
                        weighted_cost / weighted_completion
                        if weighted_completion > 0.0
                        else None
                    ),
                    "completion_slo_target": COMPLETION_SLO,
                    "completion_slo_met": weighted_completion >= COMPLETION_SLO,
                    "source_type": SOURCE_TYPE,
                }
            )
            aggregate_rows.append(aggregate)
    return stratum_rows, aggregate_rows


def _dominance_status(
    baseline: Mapping[str, Any], comparison: Mapping[str, Any]
) -> str:
    base_completion = float(baseline["completion_probability"])
    comp_completion = float(comparison["completion_probability"])
    base_cost = float(baseline["provider_cost_per_assigned_session_usd"])
    comp_cost = float(comparison["provider_cost_per_assigned_session_usd"])
    if comp_completion >= base_completion and comp_cost <= base_cost:
        return "comparison_dominates_or_ties"
    if comp_completion <= base_completion and comp_cost >= base_cost:
        return "baseline_dominates_or_ties"
    return "cost_quality_tradeoff"


def _contrast_and_break_even_rows(
    aggregates: Sequence[Mapping[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    lookup = {
        (row["parameter_set_id"], row["model"], row["strategy_id"]): row
        for row in aggregates
    }
    parameter_model_keys = sorted(
        {(row["parameter_set_id"], row["model"]) for row in aggregates}
    )
    contrasts: list[dict[str, Any]] = []
    break_evens: list[dict[str, Any]] = []
    for parameter_id, model in parameter_model_keys:
        baseline = lookup[(parameter_id, model, "grow_to_800k")]
        for comparison_strategy in STRATEGY_SOURCES:
            if comparison_strategy == "grow_to_800k":
                continue
            comparison = lookup[(parameter_id, model, comparison_strategy)]
            contrast_id = f"{parameter_id}-{model}-{comparison_strategy}-vs-grow"
            completion_delta = float(comparison["completion_probability"]) - float(
                baseline["completion_probability"]
            )
            attempts_delta = float(comparison["expected_attempts"]) - float(
                baseline["expected_attempts"]
            )
            assigned_savings = float(
                baseline["provider_cost_per_assigned_session_usd"]
            ) - float(comparison["provider_cost_per_assigned_session_usd"])
            cost_success_delta = float(
                comparison["provider_cost_per_successful_session_usd"]
            ) - float(baseline["provider_cost_per_successful_session_usd"])
            contrast = {
                "quality_contrast_id": contrast_id,
                "parameter_set_id": parameter_id,
                "design_role": comparison["design_role"],
                "model": model,
                "baseline_strategy_id": "grow_to_800k",
                "comparison_strategy_id": comparison_strategy,
                "calibration_id": comparison["calibration_id"],
                "onset_tokens": comparison["onset_tokens"],
                "beta": comparison["beta"],
                "per_compaction_fidelity": comparison["per_compaction_fidelity"],
                "evidence_profile": comparison["evidence_profile"],
                "max_attempts": comparison["max_attempts"],
                "baseline_completion_probability": baseline["completion_probability"],
                "comparison_completion_probability": comparison[
                    "completion_probability"
                ],
                "delta_completion_probability_comparison_minus_baseline": completion_delta,
                "baseline_expected_attempts": baseline["expected_attempts"],
                "comparison_expected_attempts": comparison["expected_attempts"],
                "delta_expected_attempts_comparison_minus_baseline": attempts_delta,
                "baseline_provider_cost_per_assigned_session_usd": baseline[
                    "provider_cost_per_assigned_session_usd"
                ],
                "comparison_provider_cost_per_assigned_session_usd": comparison[
                    "provider_cost_per_assigned_session_usd"
                ],
                "provider_cost_savings_per_assigned_session_usd": assigned_savings,
                "baseline_provider_cost_per_successful_session_usd": baseline[
                    "provider_cost_per_successful_session_usd"
                ],
                "comparison_provider_cost_per_successful_session_usd": comparison[
                    "provider_cost_per_successful_session_usd"
                ],
                "delta_provider_cost_per_successful_session_usd": cost_success_delta,
                "baseline_completion_slo_met": baseline["completion_slo_met"],
                "comparison_completion_slo_met": comparison["completion_slo_met"],
                "dominance_status": _dominance_status(baseline, comparison),
                "source_type": SOURCE_TYPE,
            }
            contrasts.append(contrast)

            completion_loss = max(-completion_delta, 0.0)
            if assigned_savings > 0.0 and completion_loss > 0.0:
                break_even_loss = assigned_savings / completion_loss
                status = "identified_tradeoff"
                interpretation = (
                    "Compaction is economically preferred only if one additional unresolved "
                    "session is valued below this break-even loss."
                )
            elif assigned_savings >= 0.0 and completion_delta >= 0.0:
                break_even_loss = None
                status = "comparison_weakly_dominates"
                interpretation = (
                    "No positive quality-cost break-even is required under this model."
                )
            elif assigned_savings <= 0.0 and completion_delta <= 0.0:
                break_even_loss = None
                status = "baseline_weakly_dominates"
                interpretation = "The comparison is no cheaper and no more complete under this model."
            else:
                break_even_loss = None
                status = "comparison_costs_more_for_quality_gain"
                interpretation = (
                    "The comparison gains completion probability at higher provider cost; this "
                    "table does not impose a willingness-to-pay threshold."
                )
            break_evens.append(
                {
                    "break_even_id": f"break-even-{contrast_id}",
                    "quality_contrast_id": contrast_id,
                    "parameter_set_id": parameter_id,
                    "model": model,
                    "comparison_strategy_id": comparison_strategy,
                    "provider_cost_savings_per_assigned_session_usd": assigned_savings,
                    "completion_probability_loss": completion_loss,
                    "break_even_failure_loss_usd_per_incremental_unresolved_session": break_even_loss,
                    "break_even_status": status,
                    "interpretation": interpretation,
                    "source_type": SOURCE_TYPE,
                }
            )
    return contrasts, break_evens


def _scale_rows(aggregates: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for aggregate in aggregates:
        for assigned in SCALE_ASSIGNED_SESSIONS:
            completion = float(aggregate["completion_probability"])
            rows.append(
                {
                    "scale_result_id": (
                        f"{aggregate['parameter_set_id']}-{aggregate['model']}-"
                        f"{aggregate['strategy_id']}-n{assigned}"
                    ),
                    "parameter_set_id": aggregate["parameter_set_id"],
                    "design_role": aggregate["design_role"],
                    "model": aggregate["model"],
                    "strategy_id": aggregate["strategy_id"],
                    "calibration_id": aggregate["calibration_id"],
                    "onset_tokens": aggregate["onset_tokens"],
                    "beta": aggregate["beta"],
                    "per_compaction_fidelity": aggregate["per_compaction_fidelity"],
                    "evidence_profile": aggregate["evidence_profile"],
                    "max_attempts": aggregate["max_attempts"],
                    "assigned_sessions": assigned,
                    "expected_completed_sessions": assigned * completion,
                    "expected_unresolved_sessions": assigned * (1.0 - completion),
                    "expected_provider_spend_usd": assigned
                    * float(aggregate["provider_cost_per_assigned_session_usd"]),
                    "provider_cost_per_successful_session_usd": aggregate[
                        "provider_cost_per_successful_session_usd"
                    ],
                    "completion_probability": completion,
                    "source_type": SOURCE_TYPE,
                }
            )
    return rows


def _analytic_strategy_metrics(
    trajectory: Mapping[str, Any],
    *,
    onset_tokens: float,
    beta: float,
    per_compaction_fidelity: float,
    evidence_profile: str,
    max_attempts: int,
) -> dict[str, float]:
    exposure = normalized_excess_auc(trajectory["prompt_sequence_tokens"], onset_tokens)
    fidelity = effective_evidence_fidelity(
        MAIN_CALL_COUNT,
        trajectory["compaction_positions"],
        per_compaction_fidelity,
        evidence_profile,
    )
    completion = 0.0
    attempts = 0.0
    for stratum in TASK_STRATA:
        probability = single_attempt_probability(
            float(stratum["baseline_success_probability"]), beta, exposure, fidelity
        )
        stratum_completion, stratum_attempts = capped_retry_metrics(
            probability, max_attempts
        )
        completion += float(stratum["weight"]) * stratum_completion
        attempts += float(stratum["weight"]) * stratum_attempts
    assigned_cost = float(trajectory["provider_cost_per_attempt_usd"]) * attempts
    return {
        "completion_probability": completion,
        "expected_attempts": attempts,
        "provider_cost_per_assigned_session_usd": assigned_cost,
        "provider_cost_per_successful_session_usd": (
            assigned_cost / completion if completion > 0.0 else math.inf
        ),
    }


def _minimum_monotone_threshold(
    predicate: Any,
    lower: float,
    upper: float,
    *,
    tolerance: float = 1e-12,
    max_iterations: int = 100,
) -> tuple[float | None, str]:
    """Find the first false-to-true threshold on a closed monotone interval."""

    if lower > upper:
        raise ValueError("lower bound must not exceed upper bound")
    if predicate(lower):
        return lower, "already_satisfied_at_lower_bound"
    if not predicate(upper):
        return None, "not_reached_within_bounds"
    lo = lower
    hi = upper
    for _ in range(max_iterations):
        if hi - lo <= tolerance:
            break
        midpoint = (lo + hi) / 2.0
        if predicate(midpoint):
            hi = midpoint
        else:
            lo = midpoint
    return hi, "identified_by_bisection"


def _fidelity_boundary_rows(
    trajectories: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    trajectory_lookup = {
        (row["model"], row["strategy_id"]): row for row in trajectories
    }
    tolerance = 1e-12
    max_iterations = 100
    rows: list[dict[str, Any]] = []
    for model in MODELS:
        grow = trajectory_lookup[(model, "grow_to_800k")]
        for comparison_strategy in ("cap_200k_uncached", "cap_200k_cache_read"):
            compact = trajectory_lookup[(model, comparison_strategy)]

            def cost_predicate_for_fidelity(
                fidelity: float,
                *,
                compact_row: Mapping[str, Any] = compact,
                grow_row: Mapping[str, Any] = grow,
            ) -> bool:
                compact_metrics = _analytic_strategy_metrics(
                    compact_row,
                    onset_tokens=PRIMARY_ONSET_TOKENS,
                    beta=PRIMARY_BETA,
                    per_compaction_fidelity=fidelity,
                    evidence_profile="uniform",
                    max_attempts=3,
                )
                grow_metrics = _analytic_strategy_metrics(
                    grow_row,
                    onset_tokens=PRIMARY_ONSET_TOKENS,
                    beta=PRIMARY_BETA,
                    per_compaction_fidelity=fidelity,
                    evidence_profile="uniform",
                    max_attempts=3,
                )
                return (
                    compact_metrics["provider_cost_per_successful_session_usd"]
                    <= grow_metrics["provider_cost_per_successful_session_usd"]
                )

            def slo_predicate_for_fidelity(
                fidelity: float,
                *,
                compact_row: Mapping[str, Any] = compact,
            ) -> bool:
                compact_metrics = _analytic_strategy_metrics(
                    compact_row,
                    onset_tokens=PRIMARY_ONSET_TOKENS,
                    beta=PRIMARY_BETA,
                    per_compaction_fidelity=fidelity,
                    evidence_profile="uniform",
                    max_attempts=3,
                )
                return compact_metrics["completion_probability"] >= COMPLETION_SLO

            def cost_predicate_for_beta(
                beta: float,
                *,
                compact_row: Mapping[str, Any] = compact,
                grow_row: Mapping[str, Any] = grow,
            ) -> bool:
                compact_metrics = _analytic_strategy_metrics(
                    compact_row,
                    onset_tokens=PRIMARY_ONSET_TOKENS,
                    beta=beta,
                    per_compaction_fidelity=0.95,
                    evidence_profile="uniform",
                    max_attempts=3,
                )
                grow_metrics = _analytic_strategy_metrics(
                    grow_row,
                    onset_tokens=PRIMARY_ONSET_TOKENS,
                    beta=beta,
                    per_compaction_fidelity=0.95,
                    evidence_profile="uniform",
                    max_attempts=3,
                )
                return (
                    compact_metrics["provider_cost_per_successful_session_usd"]
                    <= grow_metrics["provider_cost_per_successful_session_usd"]
                )

            fidelity_cost, fidelity_cost_status = _minimum_monotone_threshold(
                cost_predicate_for_fidelity,
                0.0,
                1.0,
                tolerance=tolerance,
                max_iterations=max_iterations,
            )
            fidelity_slo, fidelity_slo_status = _minimum_monotone_threshold(
                slo_predicate_for_fidelity,
                0.0,
                1.0,
                tolerance=tolerance,
                max_iterations=max_iterations,
            )
            beta_cost, beta_cost_status = _minimum_monotone_threshold(
                cost_predicate_for_beta,
                0.0,
                10.0,
                tolerance=tolerance,
                max_iterations=max_iterations,
            )
            rows.append(
                {
                    "boundary_id": f"primary-{model}-{comparison_strategy}-vs-grow-boundaries",
                    "parameter_set_id": PRIMARY_PARAMETER_ID,
                    "model": model,
                    "baseline_strategy_id": "grow_to_800k",
                    "comparison_strategy_id": comparison_strategy,
                    "onset_tokens": PRIMARY_ONSET_TOKENS,
                    "evidence_profile": "uniform",
                    "max_attempts": 3,
                    "baseline_beta_for_fidelity_search": PRIMARY_BETA,
                    "fixed_fidelity_for_beta_search": 0.95,
                    "fidelity_search_lower_bound": 0.0,
                    "fidelity_search_upper_bound": 1.0,
                    "beta_search_lower_bound": 0.0,
                    "beta_search_upper_bound": 10.0,
                    "bisection_tolerance": tolerance,
                    "bisection_max_iterations": max_iterations,
                    "minimum_fidelity_cost_per_success_not_above_grow": fidelity_cost,
                    "minimum_fidelity_cost_status": fidelity_cost_status,
                    "minimum_fidelity_completion_slo": fidelity_slo,
                    "minimum_fidelity_completion_slo_status": fidelity_slo_status,
                    "minimum_beta_at_f095_cost_per_success_not_above_grow": beta_cost,
                    "minimum_beta_cost_status": beta_cost_status,
                    "grow_cost_per_attempt_usd": grow["provider_cost_per_attempt_usd"],
                    "comparison_cost_per_attempt_usd": compact[
                        "provider_cost_per_attempt_usd"
                    ],
                    "source_type": SOURCE_TYPE,
                }
            )
    return rows


def _choose_stratum(uniform: float) -> str:
    if uniform < 0.25:
        return "easy"
    if uniform < 0.75:
        return "typical"
    return "hard"


def _simulate_attempts(
    probability: float, uniforms: Sequence[float]
) -> tuple[int, int]:
    for attempt_index, uniform in enumerate(uniforms, start=1):
        if uniform < probability:
            return 1, attempt_index
    return 0, len(uniforms)


def _mc_pair(
    parameter_id: str,
    model: str,
    comparison_strategy: str,
    aggregates: Mapping[tuple[str, str, str], Mapping[str, Any]],
    strata: Mapping[tuple[str, str, str, str], Mapping[str, Any]],
    task_count: int,
    seed: int,
) -> dict[str, Any]:
    baseline = aggregates[(parameter_id, model, "grow_to_800k")]
    comparison = aggregates[(parameter_id, model, comparison_strategy)]
    max_attempts = int(baseline["max_attempts"])
    if max_attempts != int(comparison["max_attempts"]):
        raise ValueError("MC pair requires matching retry caps")
    p_baseline = {
        stratum["stratum_id"]: float(stratum["single_attempt_success_probability"])
        for key, stratum in strata.items()
        if key[:3] == (parameter_id, model, "grow_to_800k")
    }
    p_comparison = {
        stratum["stratum_id"]: float(stratum["single_attempt_success_probability"])
        for key, stratum in strata.items()
        if key[:3] == (parameter_id, model, comparison_strategy)
    }
    if set(p_baseline) != {"easy", "typical", "hard"} or set(p_comparison) != set(
        p_baseline
    ):
        raise ValueError("MC pair is missing task strata")
    cost_baseline = float(baseline["provider_cost_per_attempt_usd"])
    cost_comparison = float(comparison["provider_cost_per_attempt_usd"])

    rng = random.Random(seed)
    success_b = success_c = 0
    cost_sum_b = cost_sum_c = 0.0
    delta_completion_sum = 0.0
    delta_completion_sq = 0.0
    for _ in range(task_count):
        stratum_id = _choose_stratum(rng.random())
        uniforms = [rng.random() for _attempt in range(max_attempts)]
        completed_b, attempts_b = _simulate_attempts(p_baseline[stratum_id], uniforms)
        completed_c, attempts_c = _simulate_attempts(p_comparison[stratum_id], uniforms)
        success_b += completed_b
        success_c += completed_c
        cost_sum_b += attempts_b * cost_baseline
        cost_sum_c += attempts_c * cost_comparison
        delta = completed_c - completed_b
        delta_completion_sum += delta
        delta_completion_sq += delta * delta

    mean_completion_b = success_b / task_count
    mean_completion_c = success_c / task_count
    delta_completion = delta_completion_sum / task_count
    if task_count > 1:
        variance_delta_completion = (
            delta_completion_sq - task_count * delta_completion**2
        ) / (task_count - 1)
    else:
        variance_delta_completion = 0.0
    se_delta_completion = math.sqrt(max(variance_delta_completion, 0.0) / task_count)
    ratio_b = cost_sum_b / success_b if success_b else math.inf
    ratio_c = cost_sum_c / success_c if success_c else math.inf
    if not math.isfinite(ratio_b) or not math.isfinite(ratio_c):
        raise ValueError("MC sentinel produced zero successful sessions")

    # A deterministic second pass avoids raw task rows.  The paired delta-method
    # influence function yields an MCSE for the difference of two cost/success
    # ratio estimators while preserving the common-random-number coupling.
    rng = random.Random(seed)
    influence_sum = 0.0
    influence_sq = 0.0
    for _ in range(task_count):
        stratum_id = _choose_stratum(rng.random())
        uniforms = [rng.random() for _attempt in range(max_attempts)]
        completed_b, attempts_b = _simulate_attempts(p_baseline[stratum_id], uniforms)
        completed_c, attempts_c = _simulate_attempts(p_comparison[stratum_id], uniforms)
        item_cost_b = attempts_b * cost_baseline
        item_cost_c = attempts_c * cost_comparison
        influence_b = (item_cost_b - ratio_b * completed_b) / mean_completion_b
        influence_c = (item_cost_c - ratio_c * completed_c) / mean_completion_c
        influence = influence_c - influence_b
        influence_sum += influence
        influence_sq += influence * influence
    influence_mean = influence_sum / task_count
    if task_count > 1:
        influence_variance = (influence_sq - task_count * influence_mean**2) / (
            task_count - 1
        )
    else:
        influence_variance = 0.0
    se_cost_delta = math.sqrt(max(influence_variance, 0.0) / task_count)

    analytic_completion_delta = float(comparison["completion_probability"]) - float(
        baseline["completion_probability"]
    )
    analytic_cost_delta = float(
        comparison["provider_cost_per_successful_session_usd"]
    ) - float(baseline["provider_cost_per_successful_session_usd"])
    mc_cost_delta = ratio_c - ratio_b
    completion_low = delta_completion - NORMAL_95 * se_delta_completion
    completion_high = delta_completion + NORMAL_95 * se_delta_completion
    cost_low = mc_cost_delta - NORMAL_95 * se_cost_delta
    cost_high = mc_cost_delta + NORMAL_95 * se_cost_delta
    return {
        "monte_carlo_id": f"mc-{parameter_id}-{model}-{comparison_strategy}-vs-grow",
        "parameter_set_id": parameter_id,
        "model": model,
        "baseline_strategy_id": "grow_to_800k",
        "comparison_strategy_id": comparison_strategy,
        "task_count": task_count,
        "seed": seed,
        "rng": "python.random.Random-MT19937",
        "coupling": "paired-common-task-stratum-and-attempt-uniforms",
        "max_attempts": max_attempts,
        "analytic_baseline_completion_probability": baseline["completion_probability"],
        "analytic_comparison_completion_probability": comparison[
            "completion_probability"
        ],
        "analytic_delta_completion_probability": analytic_completion_delta,
        "mc_baseline_completion_probability": mean_completion_b,
        "mc_comparison_completion_probability": mean_completion_c,
        "mc_delta_completion_probability": delta_completion,
        "mcse_delta_completion_probability": se_delta_completion,
        "ci95_low_delta_completion_probability": completion_low,
        "ci95_high_delta_completion_probability": completion_high,
        "analytic_baseline_cost_per_successful_session_usd": baseline[
            "provider_cost_per_successful_session_usd"
        ],
        "analytic_comparison_cost_per_successful_session_usd": comparison[
            "provider_cost_per_successful_session_usd"
        ],
        "analytic_delta_cost_per_successful_session_usd": analytic_cost_delta,
        "mc_baseline_cost_per_successful_session_usd": ratio_b,
        "mc_comparison_cost_per_successful_session_usd": ratio_c,
        "mc_delta_cost_per_successful_session_usd": mc_cost_delta,
        "mcse_delta_cost_per_successful_session_usd": se_cost_delta,
        "ci95_low_delta_cost_per_successful_session_usd": cost_low,
        "ci95_high_delta_cost_per_successful_session_usd": cost_high,
        "completion_delta_analytic_inside_ci95": (
            completion_low <= analytic_completion_delta <= completion_high
        ),
        "cost_delta_analytic_inside_ci95": cost_low <= analytic_cost_delta <= cost_high,
        "source_type": SOURCE_TYPE,
    }


def _monte_carlo_rows(
    aggregates: Sequence[Mapping[str, Any]],
    stratum_rows: Sequence[Mapping[str, Any]],
    task_count: int,
    seed: int,
) -> list[dict[str, Any]]:
    if task_count <= 0:
        return []
    aggregate_lookup = {
        (row["parameter_set_id"], row["model"], row["strategy_id"]): row
        for row in aggregates
    }
    stratum_lookup = {
        (
            row["parameter_set_id"],
            row["model"],
            row["strategy_id"],
            row["stratum_id"],
        ): row
        for row in stratum_rows
    }
    sentinel_pairs = (
        ("luna", "cap_200k_uncached"),
        ("terra", "cap_200k_uncached"),
        ("sol", "cap_200k_uncached"),
        ("luna", "cap_200k_cache_read"),
        ("terra", "cap_pricing_threshold_uncached"),
        ("sol", "cap_pricing_threshold_uncached"),
    )
    return [
        _mc_pair(
            PRIMARY_PARAMETER_ID,
            model,
            strategy,
            aggregate_lookup,
            stratum_lookup,
            task_count,
            seed,
        )
        for model, strategy in sentinel_pairs
    ]


def _evidence_anchor_eligible(row: Mapping[str, str]) -> bool:
    if row.get("score_unit") != "proportion":
        return False
    if row.get("evidence_status") == "source-reported" and row.get(
        "numeric_precision"
    ) in {"exact", "rounded"}:
        return True
    # A pinned, row-level result recomputed exactly from a frozen source may be
    # used as an independently-derived anchor.  This admits the two Chroma
    # focused/full rows without admitting derived counts, p-values, approximate
    # chart readings, or tokenless paired statistics.
    return (
        row.get("evidence_status") == "independently-derived"
        and row.get("numeric_precision") == "exact"
        and row.get("source_location", "").lower().startswith("frozen ")
        and "commit" in row.get("source_location", "").lower()
    )


def _optional_finite_float(value: Any) -> float | None:
    if value is None or str(value).strip() == "":
        return None
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return None
    return parsed if math.isfinite(parsed) else None


def build_evidence_tables(
    evidence_rows: Sequence[Mapping[str, str]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Normalize evidence curves and log2-interpolate bracketed retention onsets.

    Approximate, inequality, count, p-value, and tokenless values remain visible
    but are not interpolation anchors.  Source-reported exact/rounded
    proportions and the explicitly approved exact, commit-pinned Chroma
    proportions may anchor a curve.  The function never extrapolates.
    """

    if not evidence_rows:
        return [], []
    missing = set(EVIDENCE_INPUT_COLUMNS) - set(evidence_rows[0])
    if missing:
        raise ValueError(f"Evidence CSV is missing required columns: {sorted(missing)}")
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for original in evidence_rows:
        row = {
            column: str(original.get(column, "")) for column in EVIDENCE_INPUT_COLUMNS
        }
        if not row["series_id"] or not row["evidence_id"]:
            raise ValueError("Evidence rows require series_id and evidence_id")
        grouped[row["series_id"]].append(row)

    curve_rows: list[dict[str, Any]] = []
    onset_rows: list[dict[str, Any]] = []
    for series_id in sorted(grouped):
        group = grouped[series_id]
        parsed: list[dict[str, Any]] = []
        for row in group:
            context = _optional_finite_float(row.get("context_tokens"))
            score = _optional_finite_float(row.get("score"))
            valid_context = context is not None and context > 0.0
            eligible = (
                _evidence_anchor_eligible(row)
                and valid_context
                and score is not None
                and 0.0 <= score <= 1.0
            )
            parsed.append(
                {
                    "context": context if valid_context else None,
                    "score": score,
                    "row": row,
                    "eligible": eligible,
                }
            )
        parsed.sort(
            key=lambda item: (
                item["context"] is None,
                item["context"] if item["context"] is not None else math.inf,
                item["row"]["evidence_id"],
            )
        )
        anchors = [item for item in parsed if item["eligible"]]
        if anchors:
            reference_context = anchors[0]["context"]
            reference_score = anchors[0]["score"]
            reference_row = anchors[0]["row"]
            if reference_score == 0.0:
                raise ValueError(f"Reference score is zero for series {series_id}")
        else:
            reference_context = reference_score = None
            reference_row = None
        anchor_curve: list[tuple[float, float, dict[str, str]]] = []
        for order, item in enumerate(parsed, start=1):
            context = item["context"]
            score = item["score"]
            row = item["row"]
            eligible = item["eligible"]
            retention = (
                score / reference_score
                if reference_score is not None
                and context is not None
                and score is not None
                and row.get("score_unit") == "proportion"
                else None
            )
            output = dict(row)
            output.update(
                {
                    "anchor_eligible": eligible,
                    "reference_evidence_id": (
                        reference_row["evidence_id"]
                        if reference_row is not None and context is not None
                        else None
                    ),
                    "reference_context_tokens": reference_context
                    if context is not None
                    else None,
                    "reference_score": reference_score if context is not None else None,
                    "retention": retention,
                    "curve_order": order,
                }
            )
            curve_rows.append(output)
            if eligible and retention is not None:
                anchor_curve.append((context, retention, row))

        metadata = anchors[0]["row"] if anchors else parsed[0]["row"]
        limitation_values = []
        for item in parsed:
            limitation = item["row"].get("limitations", "").strip()
            if limitation and limitation not in limitation_values:
                limitation_values.append(limitation)
        limitations = " | ".join(limitation_values)
        if len(anchor_curve) == 2 and any(
            item["row"].get("evidence_status") == "independently-derived"
            for item in anchors
        ):
            limitations = (
                "Two-point log2 interpolation over a mean-context contrast; the conditions may "
                "differ in retrieval burden as well as length. | " + limitations
            ).rstrip(" |")
        for threshold in RETENTION_THRESHOLDS:
            bracket = None
            for lower, upper in pairwise(anchor_curve):
                if lower[1] >= threshold and upper[1] < threshold:
                    bracket = (lower, upper)
                    break
            if bracket is None:
                status = "unidentifiable"
                interpolated = None
                lower = upper = None
            else:
                lower, upper = bracket
                log_lower = math.log2(lower[0])
                log_upper = math.log2(upper[0])
                fraction = (threshold - lower[1]) / (upper[1] - lower[1])
                interpolated = 2.0 ** (log_lower + fraction * (log_upper - log_lower))
                status = "interpolated"
            onset_rows.append(
                {
                    "evidence_onset_id": (
                        f"{series_id}-retention-{round(threshold * 100)}pct"
                    ),
                    "series_id": series_id,
                    "study": metadata.get("study", ""),
                    "model": metadata.get("model", ""),
                    "task": metadata.get("task", ""),
                    "metric": metadata.get("metric", ""),
                    "retention_threshold": threshold,
                    "threshold_status": status,
                    "interpolated_context_tokens": interpolated,
                    "lower_evidence_id": lower[2]["evidence_id"] if lower else None,
                    "upper_evidence_id": upper[2]["evidence_id"] if upper else None,
                    "lower_context_tokens": lower[0] if lower else None,
                    "upper_context_tokens": upper[0] if upper else None,
                    "lower_retention": lower[1] if lower else None,
                    "upper_retention": upper[1] if upper else None,
                    "interpolation_scale": "log2(context_tokens)",
                    "anchor_count": len(anchor_curve),
                    "target_model_scope": metadata.get("target_model_scope", ""),
                    "limitations": limitations,
                }
            )
    return curve_rows, onset_rows


def _load_evidence(
    path: Path | None,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, str]]:
    if path is None:
        return [], [], {}
    evidence_rows = _read_csv(path)
    curves, onsets = build_evidence_tables(evidence_rows)
    return curves, onsets, {path.name: sha256_file(path)}


def build_study(
    cost_bundle: Path,
    evidence_csv: Path | None = None,
    spec_json: Path | None = None,
    *,
    monte_carlo_tasks: int = MONTE_CARLO_TASKS,
    monte_carlo_seed: int = MONTE_CARLO_SEED,
) -> dict[str, Any]:
    cost_bundle = Path(cost_bundle)
    evidence_csv = Path(evidence_csv) if evidence_csv is not None else None
    spec_json = Path(spec_json) if spec_json is not None else None
    if spec_json is None and evidence_csv is not None:
        sibling_spec = evidence_csv.with_name("pi-context-rot-spec-20260904.json")
        if sibling_spec.is_file():
            spec_json = sibling_spec
    trajectories, input_hashes = _load_cost_trajectories(cost_bundle)
    settings = build_parameter_settings()
    trajectory_rows, trajectory_lookup = _trajectory_metric_rows(trajectories, settings)
    stratum_rows, aggregate_rows = _quality_rows(
        trajectories, settings, trajectory_lookup
    )
    contrast_rows, break_even_rows = _contrast_and_break_even_rows(aggregate_rows)
    scale_rows = _scale_rows(aggregate_rows)
    fidelity_boundaries = _fidelity_boundary_rows(trajectories)
    mc_rows = _monte_carlo_rows(
        aggregate_rows, stratum_rows, monte_carlo_tasks, monte_carlo_seed
    )
    evidence_curves, evidence_onsets, evidence_hashes = _load_evidence(evidence_csv)
    input_hashes.update(evidence_hashes)
    if spec_json is not None:
        if not spec_json.is_file():
            raise FileNotFoundError(spec_json)
        with spec_json.open("r", encoding="utf-8-sig") as handle:
            spec_value = json.load(handle)
        if not isinstance(spec_value, dict):
            raise ValueError("Context-rot preregistration spec must be a JSON object")
        input_hashes[spec_json.name] = sha256_file(spec_json)
    return {
        "trajectories": trajectory_rows,
        "strata": stratum_rows,
        "aggregates": aggregate_rows,
        "contrasts": contrast_rows,
        "break_evens": break_even_rows,
        "scales": scale_rows,
        "fidelity_boundaries": fidelity_boundaries,
        "monte_carlo": mc_rows,
        "evidence_curves": evidence_curves,
        "evidence_onsets": evidence_onsets,
        "parameter_settings": settings,
        "input_hashes": input_hashes,
        "evidence_input_name": evidence_csv.name if evidence_csv is not None else None,
        "spec_input_name": spec_json.name if spec_json is not None else None,
        "monte_carlo_tasks": monte_carlo_tasks,
        "monte_carlo_seed": monte_carlo_seed,
    }


def _table_dictionary() -> dict[str, Any]:
    tables = {
        "trajectory-metrics.csv": (
            "One strategy/model/onset trajectory derived from the cost ledger.",
            TRAJECTORY_COLUMNS,
        ),
        "quality-stratum-results.csv.gz": (
            "One parameter/model/strategy/task-stratum analytic quality result.",
            STRATUM_COLUMNS,
        ),
        "quality-aggregate-results.csv.gz": (
            "One parameter/model/strategy task-mix aggregate.",
            AGGREGATE_COLUMNS,
        ),
        "quality-contrast-results.csv.gz": (
            "One compact-strategy minus grow-strategy contrast at matched assumptions.",
            CONTRAST_COLUMNS,
        ),
        "break-even.csv.gz": (
            "One monetized unresolved-session break-even per quality contrast.",
            BREAK_EVEN_COLUMNS,
        ),
        "scale-results.csv.gz": (
            "One aggregate projected algebraically to 1,000 or 1,000,000 sessions.",
            SCALE_COLUMNS,
        ),
        "fidelity-boundaries.csv": (
            "One primary model/compact-strategy row with three analytic decision boundaries.",
            FIDELITY_BOUNDARY_COLUMNS,
        ),
        "monte-carlo-summary.csv": (
            "One paired common-random-number primary sentinel comparison; no raw tasks.",
            MONTE_CARLO_COLUMNS,
        ),
        "evidence-curves.csv": (
            "One authored evidence row with reference-normalized retention and anchor eligibility.",
            EVIDENCE_CURVE_COLUMNS,
        ),
        "evidence-onsets.csv": (
            "One evidence series/retention threshold with bracketed log2 interpolation or unidentifiable status.",
            EVIDENCE_ONSET_COLUMNS,
        ),
    }
    return {
        "schema_version": SCHEMA_VERSION,
        "missing_value": "Empty CSV field; no NA/NaN/sentinel encoding.",
        "tables": {
            filename: {
                "grain": grain,
                "storage": (
                    "gzip-compressed CSV with deterministic metadata"
                    if filename in GZIP_ARTIFACTS
                    else "plain UTF-8 CSV"
                ),
                "columns": [
                    {
                        "name": column,
                        "description": _column_description(column),
                    }
                    for column in columns
                ],
            }
            for filename, (grain, columns) in tables.items()
        },
    }


def _column_description(column: str) -> str:
    descriptions = {
        "normalized_excess_auc": (
            "Excess-context exposure in fixed 100k-token units per call: "
            "sum(max(prompt-onset,0))/(100000*n)."
        ),
        "effective_evidence_fidelity": (
            "Profile-weighted mean of f raised to subsequent compaction count."
        ),
        "completion_probability": "Task-mix probability of success within the capped attempts.",
        "expected_attempts": "Task-mix expected number of charged attempts, including the first.",
        "source_type": "Data classification; simulated for model-generated results.",
        "threshold_status": "interpolated when bracketed; otherwise unidentifiable.",
        "target_model_scope": "Whether evidence is historical proxy or hypothetical sensitivity only.",
    }
    if column in descriptions:
        return descriptions[column]
    return column.replace("_", " ").capitalize() + "."


def _explore_sql() -> str:
    return """-- DuckDB starter queries for the deterministic context-rot bundle.
CREATE OR REPLACE VIEW quality_aggregate AS
SELECT * FROM read_csv_auto('quality-aggregate-results.csv.gz', header=true);

CREATE OR REPLACE VIEW quality_strata AS
SELECT * FROM read_csv_auto('quality-stratum-results.csv.gz', header=true);

CREATE OR REPLACE VIEW quality_contrasts AS
SELECT * FROM read_csv_auto('quality-contrast-results.csv.gz', header=true);

CREATE OR REPLACE VIEW break_even AS
SELECT * FROM read_csv_auto('break-even.csv.gz', header=true);

CREATE OR REPLACE VIEW scaled_monthly AS
SELECT * FROM read_csv_auto('scale-results.csv.gz', header=true);

CREATE OR REPLACE VIEW primary_boundaries AS
SELECT * FROM read_csv_auto('fidelity-boundaries.csv', header=true);

-- Primary cost/quality frontier by model.
SELECT model, strategy_id, completion_probability,
       provider_cost_per_assigned_session_usd,
       provider_cost_per_successful_session_usd,
       completion_slo_met
FROM quality_aggregate
WHERE parameter_set_id = 'primary-onset-200k-half-odds-f095-k3-uniform'
ORDER BY model, provider_cost_per_assigned_session_usd;

-- Assumption cells where compacting beats grow on both completion and assigned cost.
SELECT model, comparison_strategy_id, COUNT(*) AS cells
FROM quality_contrasts
WHERE dominance_status = 'comparison_dominates_or_ties'
GROUP BY model, comparison_strategy_id
ORDER BY model, comparison_strategy_id;

-- One-million-session primary projection.
SELECT model, strategy_id, expected_completed_sessions,
       expected_unresolved_sessions, expected_provider_spend_usd
FROM scaled_monthly
WHERE parameter_set_id = 'primary-onset-200k-half-odds-f095-k3-uniform'
  AND assigned_sessions = 1000000
ORDER BY model, strategy_id;
"""


def _study_results(study: Mapping[str, Any]) -> dict[str, Any]:
    primary_aggregates = [
        row
        for row in study["aggregates"]
        if row["parameter_set_id"] == PRIMARY_PARAMETER_ID
    ]
    primary_contrasts = [
        row
        for row in study["contrasts"]
        if row["parameter_set_id"] == PRIMARY_PARAMETER_ID
    ]
    return {
        "schema_version": SCHEMA_VERSION,
        "study_id": STUDY_ID,
        "model_version": MODEL_VERSION,
        "source_type": SOURCE_TYPE,
        "execution_mode": "offline-statistical-simulation",
        "real_pi_or_copilot_or_model_calls": False,
        "claim_scope": "model-internal",
        "engine": "python-standard-library",
        "uncertainty_modes": ["deterministic-analytic", "paired-monte-carlo-sentinel"],
        "monte_carlo_uncertainty_scope": "conditional-on-declared-model-and-assumptions",
        "formulas": {
            "normalized_excess_auc": (
                "sum(max(prompt_i-onset,0))/(100000*main_call_count)"
            ),
            "single_attempt_probability": (
                "logistic(logit(p0)-beta*normalized_excess_auc+ln(effective_evidence_fidelity))"
            ),
            "effective_evidence_fidelity": (
                "weighted_mean_i(per_compaction_fidelity^count(compaction_position>=i))"
            ),
            "completion_probability": "1-(1-p_single)^max_attempts",
            "expected_attempts": "sum(j=0..max_attempts-1,(1-p_single)^j)",
            "cost_per_assigned": "provider_cost_per_attempt*expected_attempts",
            "cost_per_successful": "cost_per_assigned/completion_probability",
        },
        "task_mix": list(TASK_STRATA),
        "weighted_task_mix_baseline": sum(
            row["weight"] * row["baseline_success_probability"] for row in TASK_STRATA
        ),
        "strategies": {
            key: {"source_contrast_id": value[0], "source_role": value[1]}
            for key, value in STRATEGY_SOURCES.items()
        },
        "generic_sensitivity_grid": {
            "onset_tokens": list(GENERIC_ONSETS),
            "beta": list(GENERIC_BETAS),
            "per_compaction_fidelity": list(FIDELITY_VALUES),
            "max_attempts": list(MAX_ATTEMPTS_VALUES),
            "evidence_profile": list(EVIDENCE_PROFILES),
        },
        "historical_proxy_profiles": list(CALIBRATED_PROXY_PROFILES),
        "historical_proxy_scope": "historical-proxy-not-gpt-5.6-calibration",
        "primary_case": {
            "parameter_set_id": PRIMARY_PARAMETER_ID,
            "onset_tokens": PRIMARY_ONSET_TOKENS,
            "grow_normalized_excess_auc": PRIMARY_GROW_EXCESS_AUC,
            "beta": PRIMARY_BETA,
            "per_compaction_fidelity": 0.95,
            "max_attempts": 3,
            "evidence_profile": "uniform",
            "aggregates": primary_aggregates,
            "contrasts": primary_contrasts,
            "decision_boundaries": list(study["fidelity_boundaries"]),
        },
        "monte_carlo_design": {
            "task_count_per_sentinel": study["monte_carlo_tasks"],
            "seed": study["monte_carlo_seed"],
            "rng": "python.random.Random-MT19937",
            "coupling": "paired-common-task-stratum-and-attempt-uniforms",
            "raw_task_rows_retained": False,
        },
        "evidence_policy": {
            "eligible_anchors": [
                "source-reported proportion with exact or rounded precision",
                "independently-derived exact proportion from a frozen commit with context tokens",
            ],
            "interpolation": "linear retention between anchors on log2(context_tokens)",
            "extrapolation": "forbidden",
            "retention_thresholds": list(RETENTION_THRESHOLDS),
        },
        "row_counts": {
            "trajectory-metrics.csv": len(study["trajectories"]),
            "quality-stratum-results.csv.gz": len(study["strata"]),
            "quality-aggregate-results.csv.gz": len(study["aggregates"]),
            "quality-contrast-results.csv.gz": len(study["contrasts"]),
            "break-even.csv.gz": len(study["break_evens"]),
            "scale-results.csv.gz": len(study["scales"]),
            "fidelity-boundaries.csv": len(study["fidelity_boundaries"]),
            "monte-carlo-summary.csv": len(study["monte_carlo"]),
            "evidence-curves.csv": len(study["evidence_curves"]),
            "evidence-onsets.csv": len(study["evidence_onsets"]),
        },
        "input_hashes": study["input_hashes"],
        "limitations": [
            "The quality equation is a transparent hypothetical sensitivity model, not a GPT-5.6 estimate.",
            "Historical benchmark slopes involve other models and tasks and are challenge proxies only.",
            "Retry attempts are assumed independent conditional on task stratum and strategy in the analytic model.",
            "Compaction fidelity is assumed multiplicative and evidence-position weights are stylized.",
            "Provider cost inputs are inherited unchanged from the versioned offline cost bundle.",
            "Simulation can compare consequences under assumptions but cannot prove real-world context rot.",
        ],
    }


def _summary_markdown(
    study_results: Mapping[str, Any], evidence_onsets: Sequence[Mapping[str, Any]]
) -> str:
    primary = sorted(
        study_results["primary_case"]["aggregates"],
        key=lambda row: (row["model"], row["strategy_id"]),
    )
    lines = [
        "# Pi context-rot cost-quality sensitivity summary",
        "",
        (
            "This is an offline model-conditional simulation. It did not execute Pi, "
            "Copilot, or any model API. The quality mechanism is hypothetical; historical "
            "benchmark slopes are explicitly non-GPT-5.6 proxies."
        ),
        "",
        "## Primary case",
        "",
        (
            "The named primary case uses onset 200,000 tokens, beta = ln(2)/(31/13), "
            "per-compaction fidelity 0.95, uniform evidence positions, and at most three attempts."
        ),
        "",
        "| Model | Strategy | Cost/attempt (USD) | Completion | Cost/assigned (USD) | Cost/success (USD) | SLO >=95% |",
        "| --- | --- | ---: | ---: | ---: | ---: | --- |",
    ]
    for row in primary:
        lines.append(
            "| {model} | {strategy_id} | {attempt:.6f} | {completion:.6f} | "
            "{assigned:.6f} | {success:.6f} | {slo} |".format(
                model=row["model"],
                strategy_id=row["strategy_id"],
                attempt=float(row["provider_cost_per_attempt_usd"]),
                completion=float(row["completion_probability"]),
                assigned=float(row["provider_cost_per_assigned_session_usd"]),
                success=float(row["provider_cost_per_successful_session_usd"]),
                slo="yes" if row["completion_slo_met"] else "no",
            )
        )
    lines.extend(
        [
            "",
            "## Primary decision boundaries",
            "",
            (
                "`fidelity-boundaries.csv` reports, for every priced model and the "
                "uncached/cache-read 200k caps, the minimum per-compaction survival needed "
                "to beat grow on cost per successful session, the minimum survival needed "
                "to meet the 95% completion SLO, and the minimum context-rot beta at fixed "
                "f=0.95 needed to beat grow on cost per success. Each value is an exact "
                "analytic-model bisection over documented bounds."
            ),
            "",
            "## How to explore",
            "",
            (
                "Use `quality-contrast-results.csv.gz` for matched compact-minus-grow "
                "comparisons, `scale-results.csv.gz` for 1,000 and 1,000,000 assigned sessions, "
                "and `explore.sql` for starter DuckDB queries. `monte-carlo-summary.csv` "
                "checks a few primary analytic contrasts with paired common random numbers "
                "without retaining task-level rows."
            ),
            "",
            "## Evidence curves",
            "",
        ]
    )
    if evidence_onsets:
        identified = sum(
            row["threshold_status"] == "interpolated" for row in evidence_onsets
        )
        lines.append(
            f"The authored evidence input produced {len(evidence_onsets)} threshold rows; "
            f"{identified} are bracketed interpolations. Unbracketed thresholds are marked "
            "`unidentifiable`; none are extrapolated."
        )
    else:
        lines.append(
            "No authored evidence CSV was supplied. The evidence tables retain their schemas "
            "with zero rows; the simulator never fabricates or extrapolates evidence."
        )
    lines.extend(
        [
            "",
            "## Interpretation boundary",
            "",
            (
                "These results support or challenge strategies only under the declared "
                "equations and assumptions. External task-level validation is required before "
                "treating any quality or break-even result as a production forecast."
            ),
        ]
    )
    return "\n".join(lines) + "\n"


def write_bundle(output_dir: Path, study: Mapping[str, Any]) -> dict[str, Any]:
    output_dir = Path(output_dir)
    if output_dir.exists() and any(output_dir.iterdir()):
        raise FileExistsError(f"Output directory is not empty: {output_dir}")
    output_dir.mkdir(parents=True, exist_ok=True)

    csv_specs = (
        ("trajectory-metrics.csv", study["trajectories"], TRAJECTORY_COLUMNS),
        ("quality-stratum-results.csv.gz", study["strata"], STRATUM_COLUMNS),
        ("quality-aggregate-results.csv.gz", study["aggregates"], AGGREGATE_COLUMNS),
        ("quality-contrast-results.csv.gz", study["contrasts"], CONTRAST_COLUMNS),
        ("break-even.csv.gz", study["break_evens"], BREAK_EVEN_COLUMNS),
        ("scale-results.csv.gz", study["scales"], SCALE_COLUMNS),
        (
            "fidelity-boundaries.csv",
            study["fidelity_boundaries"],
            FIDELITY_BOUNDARY_COLUMNS,
        ),
        ("monte-carlo-summary.csv", study["monte_carlo"], MONTE_CARLO_COLUMNS),
        ("evidence-curves.csv", study["evidence_curves"], EVIDENCE_CURVE_COLUMNS),
        ("evidence-onsets.csv", study["evidence_onsets"], EVIDENCE_ONSET_COLUMNS),
    )
    row_counts: dict[str, int] = {}
    for filename, rows, columns in csv_specs:
        _write_csv(output_dir / filename, rows, columns)
        row_counts[filename] = len(rows)

    results = _study_results(study)
    _write_text(output_dir / "study-results.json", _json_text(results))
    _write_text(output_dir / "data-dictionary.json", _json_text(_table_dictionary()))
    _write_text(output_dir / "explore.sql", _explore_sql())
    _write_text(
        output_dir / "summary.md", _summary_markdown(results, study["evidence_onsets"])
    )

    artifact_names = [filename for filename, _rows, _columns in csv_specs] + [
        "study-results.json",
        "data-dictionary.json",
        "explore.sql",
        "summary.md",
    ]
    artifact_manifest = {}
    for filename in sorted(artifact_names):
        path = output_dir / filename
        metadata: dict[str, Any] = {
            "sha256": sha256_file(path),
            "bytes": path.stat().st_size,
            "rows": row_counts.get(filename),
        }
        if filename in GZIP_ARTIFACTS:
            logical_bytes = gzip.decompress(path.read_bytes())
            metadata.update(
                {
                    "uncompressed_sha256": hashlib.sha256(logical_bytes).hexdigest(),
                    "uncompressed_bytes": len(logical_bytes),
                    "compression": {
                        "format": "gzip",
                        "level": GZIP_COMPRESSION_LEVEL,
                        "mtime": 0,
                        "original_filename": "",
                        "python_version": platform.python_version(),
                        "zlib_build_version": zlib.ZLIB_VERSION,
                        "zlib_runtime_version": zlib.ZLIB_RUNTIME_VERSION,
                    },
                }
            )
        artifact_manifest[filename] = metadata
    manifest = {
        "schema_version": SCHEMA_VERSION,
        "study_id": STUDY_ID,
        "model_version": MODEL_VERSION,
        "engine": "python-standard-library",
        "source_type": SOURCE_TYPE,
        "execution_mode": "offline-statistical-simulation",
        "real_pi_or_copilot_or_model_calls": False,
        "monte_carlo_uncertainty_scope": "conditional-on-declared-model-and-assumptions",
        "reproducibility": "exact-within-python-and-zlib-runtime-for-analytic-seeded-mc-and-gzip",
        "input_files": {
            filename: {"sha256": digest}
            for filename, digest in sorted(study["input_hashes"].items())
        },
        "artifacts": artifact_manifest,
        "monte_carlo": {
            "task_count_per_sentinel": study["monte_carlo_tasks"],
            "seed": study["monte_carlo_seed"],
            "raw_task_rows_retained": False,
        },
    }
    _write_text(output_dir / "manifest.json", _json_text(manifest))
    checksum_names = sorted(artifact_names + ["manifest.json"])
    checksum_text = "".join(
        f"{sha256_file(output_dir / filename)}  {filename}\n"
        for filename in checksum_names
    )
    _write_text(output_dir / "checksums.sha256", checksum_text)
    return manifest


def run_and_write(
    cost_bundle: Path,
    output_dir: Path,
    evidence_csv: Path | None = None,
    spec_json: Path | None = None,
    *,
    monte_carlo_tasks: int = MONTE_CARLO_TASKS,
    monte_carlo_seed: int = MONTE_CARLO_SEED,
) -> dict[str, Any]:
    study = build_study(
        cost_bundle,
        evidence_csv,
        spec_json,
        monte_carlo_tasks=monte_carlo_tasks,
        monte_carlo_seed=monte_carlo_seed,
    )
    return write_bundle(output_dir, study)
