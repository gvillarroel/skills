#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Validate a frozen D3 evolution dataset without disclosing holdout content."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

import build_harbor_dataset as base


SPLITS = ("train", "validation", "holdout")
EXPECTED_ROUTES = {"visualization", "logo", "recomposition", "evaluation"}


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
    expected_counts = {split: 4 for split in SPLITS}
    run_key = hashlib.sha256(manifest["runId"].encode("utf-8")).hexdigest()[:10]
    prefixes = {
        "train": f"train-{run_key}-",
        "validation": f"val-{run_key}-",
        "holdout": f"hold-{run_key}-",
    }

    if manifest["stats"]["splitCounts"] != expected_counts:
        failures.append("split counts differ from the frozen manifest")
    split_instruction_hashes: dict[str, set[str]] = {}
    for split in SPLITS:
        split_root = root / split
        task_dirs = sorted(path for path in split_root.iterdir() if path.is_dir())
        if len(task_dirs) != 4:
            failures.append(f"{split} task count is {len(task_dirs)}, expected 4")
        if base.tree_digest(split_root) != manifest["splitDigests"][split]:
            failures.append(f"{split} tree digest drifted")
        routes: set[str] = set()
        for task in task_dirs:
            if not task.name.startswith(prefixes[split]):
                failures.append(f"{split} task ID is not namespaced by runId")
            contract = json.loads(
                (task / "tests" / "contract.json").read_text(encoding="utf-8")
            )
            routes.add(contract["route"])
            if contract["taskId"] != task.name:
                failures.append(f"{split} task ID mismatch")
            if "bundleProfile" not in contract:
                failures.append(f"{split} task omits the bundle profile")
            elif contract["bundleProfile"] != manifest["bundleProfile"]:
                failures.append(f"{split} task bundle profile differs from the manifest")
            if not (task / "tests" / "verify_pareto_task.py").is_file():
                failures.append(f"{split} task omits the Pareto verifier")
            if "verify_pareto_task.py" not in (
                task / "tests" / "test.sh"
            ).read_text(encoding="utf-8"):
                failures.append(f"{split} task does not execute the Pareto verifier")
        if routes != EXPECTED_ROUTES:
            failures.append(f"{split} route coverage is incomplete")
        split_instruction_hashes[split] = instruction_hashes(split_root)

    for index, split in enumerate(SPLITS):
        for other in SPLITS[index + 1 :]:
            if split_instruction_hashes[split] & split_instruction_hashes[other]:
                failures.append(f"{split} overlaps {other}")
    prior_hashes = set().union(*(instruction_hashes(prior) for prior in prior_roots))
    if instruction_hashes(root) & prior_hashes:
        failures.append("new instruction content overlaps a prior frozen dataset")
    if manifest.get("priorDatasetCount") != len(prior_roots):
        failures.append("prior dataset count differs from the frozen manifest")
    if manifest.get("priorInstructionOverlap") != 0:
        failures.append("manifest records prior instruction overlap")
    if manifest.get("crossSplitInstructionOverlap") != 0:
        failures.append("manifest records cross-split instruction overlap")

    if failures:
        print(json.dumps({"ok": False, "failures": failures}, indent=2))
        return 1
    print(
        json.dumps(
            {
                "ok": True,
                "splitCounts": expected_counts,
                "priorInstructionOverlap": 0,
                "crossSplitInstructionOverlap": 0,
                "holdoutContentDisclosed": False,
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
