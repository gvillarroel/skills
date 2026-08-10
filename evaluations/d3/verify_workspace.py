#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Run the independent D3 evaluator against one local workspace and contract."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

import verify_task


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("workspace", type=Path)
    parser.add_argument("contract", type=Path)
    parser.add_argument("log_dir", type=Path)
    parser.add_argument(
        "--summary-only",
        action="store_true",
        help="Print only the verdict, rewards, findings, and counterfactual count.",
    )
    args = parser.parse_args()
    contract = json.loads(args.contract.read_text(encoding="utf-8"))
    args.log_dir.mkdir(parents=True, exist_ok=True)
    if contract["route"] == "evaluation":
        result = verify_task.verify_evaluation(args.workspace, args.log_dir, contract)
    else:
        result = verify_task.verify_visual(args.workspace, args.log_dir, contract)
    output = result
    if args.summary_only:
        output = {
            "ok": result["ok"],
            "rewards": result["rewards"],
            "findings": result.get("findings", []),
            "counterfactual_replacements": result.get(
                "counterfactualReplacements", 0
            ),
        }
    print(json.dumps(output, indent=2, sort_keys=True))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
