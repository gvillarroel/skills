#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

"""Challenge frozen context-rot retry assumptions without any model/API calls."""

from __future__ import annotations

import argparse
import csv
import hashlib
import itertools
import json
import math
from pathlib import Path


SOURCE_SHA256 = "edf0d43d7e4e797964be4616d2485e005e89d1fd7691cf2a5dde139d6a009cb2"


def persistent_retry(p: float, attempts: int, rho: float) -> tuple[float, float]:
    """Return completion and paid attempts for a within-stratum mixture."""
    if not 0 <= p <= 1 or not 0 <= rho <= 1 or type(attempts) is not int or attempts < 1:
        raise ValueError("Require probabilities in [0,1] and a positive integer attempt cap.")
    completion = rho * p + (1 - rho) * (1 - (1 - p) ** attempts)
    count = rho * (p + attempts * (1 - p)) + (1 - rho) * math.fsum(
        (1 - p) ** j for j in range(attempts)
    )
    return completion, count


def enumeration_oracles() -> int:
    """Independently enumerate every outcome sequence, including unused retries."""
    count = 0
    for p, rho, attempts in itertools.product(
        (0.0, 0.1, 0.5, 0.9, 1.0), (0.0, 0.1, 0.5, 1.0), (1, 2, 3, 4)
    ):
        complete, paid, mass = 0.0, 0.0, 0.0
        for sequence in itertools.product((0, 1), repeat=attempts):
            independent = math.prod(p if value else 1 - p for value in sequence)
            shared = p if all(sequence) else (1 - p if not any(sequence) else 0.0)
            probability = (1 - rho) * independent + rho * shared
            first_success = next((j + 1 for j, value in enumerate(sequence) if value), attempts)
            complete += probability * bool(any(sequence))
            paid += probability * first_success
            mass += probability
        actual_complete, actual_paid = persistent_retry(p, attempts, rho)
        if not all((
            math.isclose(mass, 1.0, abs_tol=1e-12),
            math.isclose(actual_complete, complete, abs_tol=1e-12),
            math.isclose(actual_paid, paid, abs_tol=1e-12),
        )):
            raise AssertionError(f"Retry enumeration mismatch at {(p, rho, attempts)}")
        count += 1
    return count


def run(source: Path, destination: Path) -> dict:
    payload = source.read_bytes()
    digest = hashlib.sha256(payload).hexdigest()
    if digest != SOURCE_SHA256:
        raise ValueError("Source differs from the frozen study; version the challenge before proceeding.")
    oracle_count = enumeration_oracles()
    original = json.loads(payload)
    strategies = {"grow_to_800k", "cap_200k_uncached"}
    aggregates = [
        row for row in original["primary_case"]["aggregates"]
        if row["model"] == "luna" and row["strategy_id"] in strategies
    ]
    if len(aggregates) != 2 or {row["strategy_id"] for row in aggregates} != strategies:
        raise ValueError("Expected exactly two frozen primary Luna strategies.")

    rows, boundaries = [], []
    for original_row in sorted(aggregates, key=lambda row: row["strategy_id"]):
        p = original_row["weighted_single_attempt_success_probability"]
        independent_completion = original_row["completion_probability"]
        independent_attempts = original_row["expected_attempts"]
        attempts = original_row["max_attempts"]
        target = original_row["completion_slo_target"]
        if attempts != 3:
            raise ValueError("This challenge is frozen to the original three-attempt policy.")
        # The mixture is linear: apply it to the already stratum-weighted endpoints.
        # Do not apply a nonlinear independent-retry transform to the average p.
        for rho in (0.0, 0.1, 0.25, 0.5, 1.0):
            completion = rho * p + (1 - rho) * independent_completion
            paid = rho * (p + attempts * (1 - p)) + (1 - rho) * independent_attempts
            spend = original_row["provider_cost_per_attempt_usd"] * paid
            rows.append({
                "case_id": f"retry-mixture-{original_row['strategy_id']}-rho-{rho:g}",
                "model": "luna",
                "strategy_id": original_row["strategy_id"],
                "rho": rho,
                "max_attempts": attempts,
                "single_attempt_success_probability": p,
                "completion_probability": completion,
                "completion_slo_target": target,
                "completion_slo_met": completion >= target,
                "expected_attempts": paid,
                "provider_cost_per_assigned_session_usd": spend,
                "provider_cost_per_successful_session_usd": spend / completion if completion else None,
                "source_type": "simulated",
            })
        boundaries.append({
            "strategy_id": original_row["strategy_id"],
            "maximum_rho_meeting_completion_slo": (
                (independent_completion - target) / (independent_completion - p)
                if p < target <= independent_completion else None
            ),
            "status": (
                "identified_by_linear_mixture" if p < target <= independent_completion
                else "already_below_target_at_independence" if independent_completion < target
                else "target_met_throughout_range"
            ),
        })

    result = {
        "review_id": "context-retry-structural-challenge-20260904",
        "analysis_mode": "offline-deterministic-structural-sensitivity",
        "source_name": source.name,
        "source_sha256": digest,
        "analysis_code_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "enumerated_oracle_cases_passed": oracle_count,
        "claim_scope": "conditional-on-frozen-quality-and-cost-inputs-and-mixture-mechanism",
        "interpretation": [
            "rho is assumed within-stratum correlation, not measured agent correlation.",
            "Single-attempt quality, cost, task mix, context, and three-attempt cap remain frozen.",
            "The frozen study's original outputs are unchanged; this is a separate exploratory challenge.",
            "Provider token value is not necessarily incremental cash after plan allowances.",
        ],
        "challenge_inventory": [
            {"case_id": "persistent-retry-mixture", "status": "tested", "values": [0, 0.1, 0.25, 0.5, 1], "evidence": "retry-mixture.csv"},
            {"case_id": "critical-fact-loss", "status": "deferred", "reason": "Requires declared critical-fact counts and dependence; average fidelity is not their estimate."},
            {"case_id": "peak-context-cliff", "status": "deferred", "reason": "Requires a separately parameterized rival exposure mechanism."},
            {"case_id": "retry-cache-or-prompt-change", "status": "deferred", "reason": "Requires a new conditional attempt-cost and recovery ledger."},
        ],
        "slo_boundaries": boundaries,
        "rows": rows,
    }
    destination.mkdir(parents=True, exist_ok=False)
    (destination / "retry-challenge.json").write_text(
        json.dumps(result, indent=2, allow_nan=False) + "\n", encoding="utf-8"
    )
    with (destination / "retry-mixture.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    return {"ok": True, "rows": len(rows), "enumerated_oracle_cases": oracle_count, "slo_boundaries": boundaries}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    args = parser.parse_args()
    print(json.dumps(run(args.source, args.output_dir), indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
