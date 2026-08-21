#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Validate a generated fresh D3 Pareto dataset without disclosing tasks."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

import build_harbor_dataset as base


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("dataset_root", type=Path)
    parser.add_argument(
        "--prior-dataset-root",
        type=Path,
        action="append",
        required=True,
        help="Prior frozen dataset root; repeat for every earlier cohort.",
    )
    return parser.parse_args()


def instruction_hashes(root: Path) -> set[str]:
    return {
        hashlib.sha256(path.read_bytes()).hexdigest()
        for path in root.rglob("instruction.md")
    }


def main() -> int:
    args = parse_args()
    root = args.dataset_root.resolve()
    prior_roots = [path.resolve() for path in args.prior_dataset_root]
    manifest = json.loads((root / "dataset-manifest.json").read_text(encoding="utf-8"))
    failures: list[str] = []
    expected_counts = {"validation": 4, "holdout": 4}
    run_key = hashlib.sha256(manifest["runId"].encode("utf-8")).hexdigest()[:10]
    expected_prefixes = {"validation": f"val-{run_key}-", "holdout": f"hold-{run_key}-"}
    if manifest["stats"]["splitCounts"] != expected_counts:
        failures.append("split counts differ from the frozen manifest")
    for split, expected in expected_counts.items():
        task_dirs = sorted(path for path in (root / split).iterdir() if path.is_dir())
        if len(task_dirs) != expected:
            failures.append(f"{split} task count is {len(task_dirs)}, expected {expected}")
        if base.tree_digest(root / split) != manifest["splitDigests"][split]:
            failures.append(f"{split} tree digest drifted")
        routes: set[str] = set()
        for task in task_dirs:
            if not task.name.startswith(expected_prefixes[split]):
                failures.append(f"{split} task ID is not namespaced by runId")
            contract = json.loads((task / "tests" / "contract.json").read_text(encoding="utf-8"))
            instruction = (task / "instruction.md").read_text(encoding="utf-8")
            routes.add(contract["route"])
            if contract["taskId"] != task.name:
                failures.append(f"{split} task ID mismatch")
            if "bundleProfile" not in contract or "bundleProfile" not in instruction:
                failures.append(f"{split} task omits the bundle profile")
            if contract["route"] != "evaluation" and "paintContract" not in instruction:
                failures.append(f"{split} visual task omits its paint contract")
            if not (task / "tests" / "verify_pareto_task.py").is_file():
                failures.append(f"{split} task omits the Pareto verifier")
            if "verify_pareto_task.py" not in (task / "tests" / "test.sh").read_text(encoding="utf-8"):
                failures.append(f"{split} task does not execute the Pareto verifier")
        if routes != {"visualization", "logo", "recomposition", "evaluation"}:
            failures.append(f"{split} route coverage is incomplete")
    prior_hashes = set().union(*(instruction_hashes(prior) for prior in prior_roots))
    if instruction_hashes(root) & prior_hashes:
        failures.append("new instruction content overlaps the prior frozen dataset")
    if manifest.get("priorDatasetCount", 1) != len(prior_roots):
        failures.append("prior dataset count differs from the frozen manifest")
    for split in ("validation", "holdout"):
        config = (root / f"{split}-job.yaml").read_text(encoding="utf-8")
        if "skill_source_dir:" in config:
            failures.append(f"{split} job primes a second environment skill copy")
        if "n_attempts: 2" not in config:
            failures.append(f"{split} job attempt count drifted")
    if failures:
        print(json.dumps({"ok": False, "failureCount": len(failures), "failures": failures}, indent=2))
        return 1
    print(
        json.dumps(
            {
                "ok": True,
                "splitCounts": expected_counts,
                "priorInstructionOverlap": 0,
                "holdoutContentDisclosed": False,
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
