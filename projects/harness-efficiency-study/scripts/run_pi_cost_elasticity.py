#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Generate the deterministic offline Pi-through-Copilot cost bundle."""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path

MODEL_PATH = Path(__file__).resolve().parents[1] / "src" / "pi_cost_elasticity.py"
SPEC = importlib.util.spec_from_file_location("pi_cost_elasticity", MODEL_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"could not load model from {MODEL_PATH}")
model = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = model
SPEC.loader.exec_module(model)


def _positive_integer(value: str) -> int:
    parsed = int(value)
    if parsed <= 0:
        raise argparse.ArgumentTypeError("volumes must be positive integers")
    return parsed


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Run deterministic token-cost arithmetic only. This command never "
            "calls Pi, Copilot, or a model API."
        )
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        required=True,
        help="Directory that will receive the CSV/JSON/SQL/Markdown bundle.",
    )
    parser.add_argument(
        "--volume",
        type=_positive_integer,
        action="append",
        dest="volumes",
        help=(
            "Algebraic execution volume. Repeat for multiple values. Defaults "
            "to 1,000 and 1,000,000."
        ),
    )
    parser.add_argument(
        "--model",
        choices=tuple(model.RATE_CARD),
        action="append",
        dest="models",
        help="Model to include. Repeat as needed; defaults to Luna, Terra, and Sol.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    volumes = tuple(args.volumes) if args.volumes else (1_000, 1_000_000)
    models = tuple(args.models) if args.models else tuple(model.RATE_CARD)
    bundle = model.simulate_all(volumes=volumes, models=models)
    manifest = model.write_bundle(args.output_dir, bundle)
    result = {
        "status": "ok",
        "execution_mode": "deterministic-offline-simulation",
        "real_pi_or_copilot_calls": False,
        "output_dir": str(args.output_dir.resolve()),
        "models": list(models),
        "volumes": list(volumes),
        "row_counts": manifest["row_counts"],
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
