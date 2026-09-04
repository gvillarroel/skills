#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Generate the offline Pi context-rot cost-quality sensitivity bundle."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
REPOSITORY_ROOT = PROJECT_ROOT.parents[1]
SOURCE_DIR = PROJECT_ROOT / "src"
if str(SOURCE_DIR) not in sys.path:
    sys.path.insert(0, str(SOURCE_DIR))

from pi_context_rot import (
    MONTE_CARLO_SEED,
    MONTE_CARLO_TASKS,
    run_and_write,
)

DEFAULT_COST_BUNDLE = (
    REPOSITORY_ROOT
    / "evaluations"
    / "harness-efficiency-study"
    / "20260904"
    / "pi-cost-elasticity"
)
DEFAULT_EVIDENCE_CSV = PROJECT_ROOT / "source" / "context-rot-evidence-20260904.csv"
DEFAULT_SPEC_JSON = PROJECT_ROOT / "source" / "pi-context-rot-spec-20260904.json"


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Generate a deterministic offline context-rot/cost simulation bundle. "
            "This command never calls Pi, Copilot, or a model API."
        )
    )
    parser.add_argument(
        "--cost-bundle",
        type=Path,
        default=DEFAULT_COST_BUNDLE,
        help="Directory containing versioned scenario-results.csv and call-ledger.csv.",
    )
    parser.add_argument(
        "--evidence-csv",
        type=Path,
        default=DEFAULT_EVIDENCE_CSV,
        help=(
            "Authored 19-column context-rot evidence CSV. Pass an empty string only through "
            "the Python API when no evidence file is available."
        ),
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        required=True,
        help="Fresh or empty output directory for the analysis-ready bundle.",
    )
    parser.add_argument(
        "--spec-json",
        type=Path,
        default=DEFAULT_SPEC_JSON,
        help="Frozen preregistration JSON whose SHA-256 is bound into the manifest.",
    )
    parser.add_argument(
        "--monte-carlo-tasks",
        type=int,
        default=MONTE_CARLO_TASKS,
        help="Hypothetical tasks per paired sentinel comparison (default: 200000).",
    )
    parser.add_argument(
        "--monte-carlo-seed",
        type=int,
        default=MONTE_CARLO_SEED,
        help="Explicit deterministic seed for paired sentinel checks.",
    )
    args = parser.parse_args(argv)
    if args.monte_carlo_tasks < 0:
        parser.error("--monte-carlo-tasks must be non-negative")
    return args


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    evidence_csv = args.evidence_csv
    if not evidence_csv.is_file():
        raise FileNotFoundError(f"Evidence CSV does not exist: {evidence_csv}")
    if not args.spec_json.is_file():
        raise FileNotFoundError(
            f"Preregistration JSON does not exist: {args.spec_json}"
        )
    manifest = run_and_write(
        args.cost_bundle,
        args.output_dir,
        evidence_csv,
        args.spec_json,
        monte_carlo_tasks=args.monte_carlo_tasks,
        monte_carlo_seed=args.monte_carlo_seed,
    )
    print(f"Wrote offline context-rot bundle: {args.output_dir.resolve()}")
    print(f"Artifacts hashed in manifest: {len(manifest['artifacts'])}")
    print("Real Pi/Copilot/model calls: false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
