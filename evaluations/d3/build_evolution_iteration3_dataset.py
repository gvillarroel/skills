#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Build fresh randomized D3 train, validation, and sealed holdout cohorts."""

from __future__ import annotations

import argparse
from collections import Counter
import copy
from dataclasses import replace
import hashlib
import json
from pathlib import Path
import re
import sys

import build_harbor_dataset as base
import build_pareto_iteration2_dataset as randomized


SPLITS = ("train", "validation", "holdout")
EXPECTED_ROUTES = {"visualization", "logo", "recomposition", "evaluation"}

# Iteration 2 awarded the maximum file-count score at 310 files, while the
# released runtime already contained 309. This frozen policy creates measurable
# headroom for the requested compaction without allowing bundle size to outweigh
# semantic quality.
BUNDLE_PROFILE: dict[str, object] = copy.deepcopy(randomized.BUNDLE_PROFILE)
BUNDLE_PROFILE["metrics"] = copy.deepcopy(BUNDLE_PROFILE["metrics"])
BUNDLE_PROFILE["metrics"]["runtimeFileCount"] = {
    "bestAtOrBelow": 280,
    "zeroAtOrAbove": 380,
}
BUNDLE_PROFILE["metrics"]["runtimeBytes"] = {
    "bestAtOrBelow": 2_900_000,
    "zeroAtOrAbove": 4_200_000,
}
BUNDLE_PROFILE["policy"] = (
    "Score the immutable installed bundle on runtime file count, runtime bytes, "
    "SKILL.md lines, largest Markdown reference, and root references with no incoming "
    "route. Semantic task quality remains 90% of the primary reward; bundle efficiency "
    "is 10%. The file-count target is deliberately below the 309-file iteration-2 "
    "baseline so safe consolidation earns measurable credit. Acceptance examples and "
    "dependency/build directories are excluded."
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument(
        "--prior-dataset-root",
        type=Path,
        action="append",
        required=True,
        help="Prior frozen dataset root; repeat for every earlier cohort.",
    )
    parser.add_argument("--attempts", type=int, default=2)
    parser.add_argument("--concurrency", type=int, default=4)
    parser.add_argument("--model", default="gpt-5.3-codex-spark")
    return parser.parse_args()


def fingerprint(spec: base.TaskSpec) -> str:
    payload = spec.instruction + "\0" + json.dumps(spec.contract, sort_keys=True)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def remap_split(specs: list[base.TaskSpec], split: str) -> list[base.TaskSpec]:
    return [replace(spec, split=split) for spec in specs]


def retarget_profile(spec: base.TaskSpec) -> base.TaskSpec:
    contract = copy.deepcopy(spec.contract)
    contract["bundleProfile"] = copy.deepcopy(BUNDLE_PROFILE)
    return replace(spec, contract=contract)


def build_specs(run_key: str) -> tuple[list[base.TaskSpec], dict[str, str]]:
    train_raw, train_nonce = randomized.randomized_specs(
        split="validation",
        task_prefix=f"train-{run_key}",
        visibility_label="Development",
    )
    validation, validation_nonce = randomized.randomized_specs(
        split="validation",
        task_prefix=f"val-{run_key}",
        visibility_label="Validation",
    )
    holdout, holdout_nonce = randomized.randomized_specs(
        split="holdout",
        task_prefix=f"hold-{run_key}",
        visibility_label="Hidden",
    )
    return (
        [
            *map(retarget_profile, remap_split(train_raw, "train")),
            *map(retarget_profile, validation),
            *map(retarget_profile, holdout),
        ],
        {
            "train": train_nonce,
            "validation": validation_nonce,
            "holdout": holdout_nonce,
        },
    )


def validate_specs(specs: list[base.TaskSpec]) -> dict[str, object]:
    counts = Counter(spec.split for spec in specs)
    expected_counts = {split: 4 for split in SPLITS}
    if dict(counts) != expected_counts:
        raise ValueError(f"Unexpected split counts: {dict(counts)}")
    ids = [spec.task_id for spec in specs]
    if len(ids) != len(set(ids)):
        raise ValueError("Task IDs must be unique")
    if any(not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", task_id) for task_id in ids):
        raise ValueError("Task IDs must be lowercase hyphen-case")
    fingerprints = [fingerprint(spec) for spec in specs]
    if len(fingerprints) != len(set(fingerprints)):
        raise ValueError("Task content must be disjoint")
    for split in SPLITS:
        routes = {spec.contract["route"] for spec in specs if spec.split == split}
        if routes != EXPECTED_ROUTES:
            raise ValueError(f"{split} route coverage is incomplete: {sorted(routes)}")
        for spec in (item for item in specs if item.split == split):
            if spec.contract.get("taskId") != spec.task_id:
                raise ValueError(f"Contract taskId mismatch: {spec.task_id}")
    return {
        "splitCounts": expected_counts,
        "routeCounts": dict(Counter(spec.contract["route"] for spec in specs)),
        "colorsetCounts": dict(Counter(spec.contract["colorset"] for spec in specs)),
    }


def main() -> int:
    args = parse_args()
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", args.run_id):
        raise SystemExit("--run-id must be lowercase hyphen-case")
    if args.attempts < 1 or args.concurrency < 1:
        raise SystemExit("--attempts and --concurrency must be positive")

    output_root = args.output_root.resolve()
    prior_roots = [path.resolve() for path in args.prior_dataset_root]
    if output_root.exists() and any(output_root.iterdir()):
        raise SystemExit(f"Refusing non-empty output directory: {output_root}")
    if len(prior_roots) != len(set(prior_roots)):
        raise SystemExit("--prior-dataset-root values must be unique")
    for prior_root in prior_roots:
        if not prior_root.is_dir():
            raise SystemExit(f"Prior frozen dataset is missing: {prior_root}")

    helper_root = Path(__file__).resolve().parent
    repo_root = helper_root.parents[1]
    run_key = hashlib.sha256(args.run_id.encode("utf-8")).hexdigest()[:10]
    specs, nonce_digests = build_specs(run_key)
    stats = validate_specs(specs)

    output_root.mkdir(parents=True, exist_ok=True)
    for spec in specs:
        randomized.write_task(output_root, spec, helper_root)

    prior_hashes = set().union(
        *(randomized.instruction_hashes(root) for root in prior_roots)
    )
    split_hashes = {
        split: randomized.instruction_hashes(output_root / split) for split in SPLITS
    }
    new_hashes = set().union(*split_hashes.values())
    prior_overlap = new_hashes & prior_hashes
    split_sets = list(split_hashes.values())
    cross_split_overlap = sum(
        len(left & right)
        for index, left in enumerate(split_sets)
        for right in split_sets[index + 1 :]
    )
    if prior_overlap:
        raise SystemExit("Fresh dataset instruction overlap detected")
    if cross_split_overlap:
        raise SystemExit("Fresh dataset splits overlap each other")

    configs = {
        split: str(
            base.write_job_config(
                output_root,
                repo_root,
                split,
                args.run_id,
                args.attempts,
                args.concurrency,
                args.model,
                repo_root / "skills" / "d3",
                prime_environment_skill=False,
            )
        )
        for split in SPLITS
    }
    manifest = {
        "schemaVersion": 1,
        "runId": args.run_id,
        "attempts": args.attempts,
        "concurrency": args.concurrency,
        "model": args.model,
        "bundleProfile": BUNDLE_PROFILE,
        "stats": stats,
        "splitDigests": {
            split: base.tree_digest(output_root / split) for split in SPLITS
        },
        "priorInstructionOverlap": len(prior_overlap),
        "crossSplitInstructionOverlap": cross_split_overlap,
        "priorDatasetCount": len(prior_roots),
        "nonceSha256": nonce_digests,
        "holdoutPolicy": (
            "Generated with cryptographic randomness before candidate mutation; exact holdout "
            "content must remain absent from reflection and validation selection. Release only "
            "after the candidate SKILL.md and unchanged runtime bundle are digest-frozen."
        ),
        "jobConfigs": configs,
    }
    (output_root / "dataset-manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(
        json.dumps(
            {
                "outputRoot": str(output_root),
                "splitCounts": stats["splitCounts"],
                "splitDigests": manifest["splitDigests"],
                "priorInstructionOverlap": len(prior_overlap),
                "crossSplitInstructionOverlap": cross_split_overlap,
                "nonceSha256": nonce_digests,
                "holdoutContentDisclosed": False,
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
