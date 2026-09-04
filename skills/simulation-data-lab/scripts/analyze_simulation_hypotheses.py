#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

"""Calculate preregistered v1 scenario contrasts from a completed bundle."""

from __future__ import annotations

import argparse
import hashlib
import math
import statistics
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

from run_simulation_experiment import (
    OUTCOME_COLUMNS,
    RUN_COLUMNS,
    SCHEMA_VERSION,
    TOOL_VERSION,
    SimulationError,
    canonical_json_bytes,
    load_json,
    normalize_spec,
    read_csv,
    safe_bundle_path,
    sha256_file,
    utc_now,
)


ANALYZER_ID = "mean-difference-v1"
RESULT_STATUSES = {
    "supports-under-model",
    "challenges-under-model",
    "inconclusive-under-model",
    "not-identifiable-from-design",
}


def canonical_number(value: float) -> float:
    if not math.isfinite(value):
        raise SimulationError("hypothesis calculation produced a non-finite number")
    result = float(format(value, ".15g"))
    return 0.0 if result == 0.0 else result


def sample_variance(values: list[float], mean: float) -> float:
    if len(values) < 2:
        raise SimulationError("stochastic analysis requires at least two observations")
    return math.fsum((value - mean) ** 2 for value in values) / (len(values) - 1)


def point_status(
    operator: str,
    threshold: float,
    estimate: float,
    interval: dict[str, Any] | None,
) -> str:
    if interval is None:
        if operator == "ge":
            return "supports" if estimate >= threshold else "challenges"
        return "supports" if estimate <= threshold else "challenges"
    low = interval["low"]
    high = interval["high"]
    if operator == "ge":
        if low >= threshold:
            return "supports"
        if high < threshold:
            return "challenges"
    else:
        if high <= threshold:
            return "supports"
        if low > threshold:
            return "challenges"
    return "inconclusive"


def result_limitations(spec: dict[str, Any], hypothesis: dict[str, Any]) -> list[str]:
    assumptions = {
        item["assumptionId"]: item["statement"] for item in spec["assumptions"]
    }
    limitations = [
        f"Assumption {assumption_id}: {assumptions[assumption_id]}"
        for assumption_id in hypothesis["assumptionIds"]
    ]
    limitations.append("The conclusion is conditional on the implemented model and analyzed design range.")
    if hypothesis["externalValidationRequired"]:
        limitations.append("External empirical validation is required before applying the result to reality.")
    return sorted(set(limitations))


def outcome_index(
    outcomes: list[dict[str, str]], outcome_name: str
) -> dict[tuple[str, str], list[dict[str, str]]]:
    groups: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in outcomes:
        if row["outcome_name"] == outcome_name:
            groups[(row["design_point_id"], row["scenario_id"])].append(row)
    for rows in groups.values():
        rows.sort(key=lambda item: item["run_id"])
    return groups


def analyze_point(
    spec: dict[str, Any],
    hypothesis: dict[str, Any],
    design_point_id: str,
    role: str,
    outcomes: list[dict[str, str]],
    seeds_by_run: dict[str, int],
) -> dict[str, Any]:
    analysis = hypothesis["analysis"]
    baseline_id = analysis["baselineScenarioId"]
    comparison_id = analysis["comparisonScenarioId"]
    index = outcome_index(outcomes, hypothesis["outcome"])
    baseline_rows = index.get((design_point_id, baseline_id), [])
    comparison_rows = index.get((design_point_id, comparison_id), [])
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
        differences = []
        for coupling_id in sorted(baseline_by_coupling):
            baseline_row = baseline_by_coupling[coupling_id]
            comparison_row = comparison_by_coupling[coupling_id]
            if seeds_by_run[baseline_row["run_id"]] != seeds_by_run[comparison_row["run_id"]]:
                raise SimulationError("paired hypothesis has mismatched run seeds")
            differences.append(float(comparison_row["value"]) - float(baseline_row["value"]))
        complete_pairs = len(differences)
        estimate_raw = math.fsum(differences) / complete_pairs
        mcse_raw = math.sqrt(sample_variance(differences, estimate_raw) / complete_pairs)
        interval_method = "normal-wald-paired-v1"
    elif pairing == "independent":
        baseline_mean = math.fsum(baseline_values) / len(baseline_values)
        comparison_mean = math.fsum(comparison_values) / len(comparison_values)
        estimate_raw = comparison_mean - baseline_mean
        baseline_variance = sample_variance(baseline_values, baseline_mean)
        comparison_variance = sample_variance(comparison_values, comparison_mean)
        mcse_raw = math.sqrt(
            baseline_variance / len(baseline_values)
            + comparison_variance / len(comparison_values)
        )
        interval_method = "normal-wald-unpaired-v1"
    else:
        estimate_raw = comparison_values[0] - baseline_values[0]
        mcse_raw = 0.0
        interval_method = "none"

    estimate = canonical_number(estimate_raw)
    mcse = canonical_number(mcse_raw)
    interval: dict[str, Any] | None
    if spec["uncertaintyMode"] == "stochastic":
        level = analysis["intervalLevel"]
        z_value = statistics.NormalDist().inv_cdf(0.5 + level / 2)
        interval = {
            "level": level,
            "low": canonical_number(estimate_raw - z_value * mcse_raw),
            "high": canonical_number(estimate_raw + z_value * mcse_raw),
            "method": interval_method,
        }
    else:
        interval = None

    threshold = hypothesis["practicalThreshold"]
    return {
        "designPointId": design_point_id,
        "role": role,
        "status": point_status(threshold["operator"], threshold["value"], estimate, interval),
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


def decision_text(status: str, hypothesis_id: str) -> str:
    messages = {
        "supports-under-model": "Every primary and challenge design point meets the preregistered threshold.",
        "challenges-under-model": "At least one primary or challenge design point contradicts the preregistered threshold.",
        "inconclusive-under-model": "No design point contradicts the threshold, but at least one interval crosses it.",
        "not-identifiable-from-design": "The declared design cannot identify the requested contrast.",
    }
    return f"{hypothesis_id}: {messages[status]}"


def analyze_hypothesis(
    spec: dict[str, Any],
    hypothesis: dict[str, Any],
    outcomes: list[dict[str, str]],
    seeds_by_run: dict[str, int],
) -> dict[str, Any]:
    analysis = hypothesis["analysis"]
    limitations = result_limitations(spec, hypothesis)
    if analysis["kind"] == "not-identifiable":
        status = "not-identifiable-from-design"
        return {
            "hypothesisId": hypothesis["hypothesisId"],
            "status": status,
            "estimand": hypothesis["estimand"],
            "analysisMethod": analysis,
            "threshold": hypothesis["practicalThreshold"],
            "designPointResults": [],
            "decision": decision_text(status, hypothesis["hypothesisId"]),
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
        **{item: "primary" for item in analysis["primaryDesignPointIds"]},
        **{item: "challenge" for item in analysis["challengeDesignPointIds"]},
    }
    points = [
        analyze_point(spec, hypothesis, design_id, roles[design_id], outcomes, seeds_by_run)
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
        "decision": decision_text(status, hypothesis["hypothesisId"]),
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


def build_report(root: Path) -> dict[str, Any]:
    spec_value, _ = load_json(root / "experiment.json", "experiment.json")
    spec = normalize_spec(spec_value)
    manifest_value, _ = load_json(root / "execution-manifest.json", "execution-manifest.json")
    if not isinstance(manifest_value, dict) or manifest_value.get("status") != "complete":
        raise SimulationError("hypothesis analysis requires a complete execution manifest")
    runs = read_csv(root / "data/runs.csv", RUN_COLUMNS, "data/runs.csv")
    if any(row["status"] != "ok" for row in runs):
        raise SimulationError("hypothesis analysis requires every planned run to be valid")
    outcomes = read_csv(root / "data/outcomes.csv", OUTCOME_COLUMNS, "data/outcomes.csv")
    seeds_by_run = {row["run_id"]: int(row["seed"]) for row in runs}
    results = [
        analyze_hypothesis(spec, hypothesis, outcomes, seeds_by_run)
        for hypothesis in spec["hypotheses"]
    ]
    return {
        "schemaVersion": SCHEMA_VERSION,
        "toolVersion": TOOL_VERSION,
        "analyzer": ANALYZER_ID,
        "experimentId": spec["experimentId"],
        "analysisPhase": spec["phase"],
        "generatedAt": utc_now(),
        "inputHashes": {
            "normalizedSpec": hashlib.sha256(canonical_json_bytes(spec)).hexdigest(),
            "runs": sha256_file(root / "data/runs.csv"),
            "outcomes": sha256_file(root / "data/outcomes.csv"),
        },
        "results": results,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Calculate machine-readable hypothesis results from a complete simulation bundle."
    )
    parser.add_argument("--root", type=Path, required=True, help="simulation bundle root")
    parser.add_argument(
        "--output",
        default="analysis/hypothesis-results.json",
        help="fresh bundle-relative output path",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        root = args.root.resolve()
        if not root.is_dir():
            raise SimulationError("bundle root must be an existing directory")
        output_relative, output = safe_bundle_path(root, args.output, "analysis output path")
        if output_relative != "analysis/hypothesis-results.json":
            raise SimulationError("schema v1 analysis output must be analysis/hypothesis-results.json")
        if output.exists():
            raise SimulationError("analysis output already exists; choose a fresh experiment bundle")
        report = build_report(root)
        if not report["results"]:
            raise SimulationError("experiment has no declared hypotheses to analyze")
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_bytes(canonical_json_bytes(report))
        sys.stdout.buffer.write(
            canonical_json_bytes(
                {
                    "ok": True,
                    "output": output_relative,
                    "hypothesisStatuses": {
                        status: sum(1 for result in report["results"] if result["status"] == status)
                        for status in sorted(RESULT_STATUSES)
                        if any(result["status"] == status for result in report["results"])
                    },
                }
            )
        )
        return 0
    except SimulationError as error:
        print(f"error: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
