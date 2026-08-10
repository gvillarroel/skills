#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Build a fresh D3 Pareto dataset with a newly sealed final holdout."""

from __future__ import annotations

import argparse
from collections import Counter
import copy
import hashlib
import json
from pathlib import Path
import re
import shutil
import sys
from typing import Any

import build_harbor_dataset as base


BUNDLE_PROFILE: dict[str, Any] = {
    "schemaVersion": 1,
    "semanticWeight": 0.9,
    "bundleWeight": 0.1,
    "metrics": {
        "runtimeFileCount": {"bestAtOrBelow": 310, "zeroAtOrAbove": 380},
        "runtimeBytes": {"bestAtOrBelow": 3_000_000, "zeroAtOrAbove": 4_200_000},
        "skillLines": {"bestAtOrBelow": 100, "zeroAtOrAbove": 220},
        "maxReferenceBytes": {"bestAtOrBelow": 32_000, "zeroAtOrAbove": 64_000},
        "orphanRootReferences": {"bestAtOrBelow": 0, "zeroAtOrAbove": 4},
    },
    "progressiveDisclosureWeights": {
        "skillLines": 0.5,
        "maxReferenceBytes": 0.25,
        "orphanRootReferences": 0.25,
    },
    "bundleEfficiencyWeights": {
        "runtimeFileCount": 0.45,
        "runtimeBytes": 0.2,
        "progressiveDisclosure": 0.35,
    },
    "policy": (
        "Score the immutable installed bundle on runtime file count, runtime bytes, "
        "SKILL.md lines, largest Markdown reference, and root references with no incoming "
        "route. Semantic task quality remains 90% of the primary reward; bundle efficiency "
        "is 10%. Acceptance examples and dependency/build directories are excluded."
    ),
}


def clone_base_task(source_id: str, *, split: str, task_id: str) -> base.TaskSpec:
    source = next(spec for spec in base.TASKS if spec.task_id == source_id)
    contract = copy.deepcopy(source.contract)
    contract["taskId"] = task_id
    return base.TaskSpec(
        split=split,
        task_id=task_id,
        instruction=source.instruction,
        contract=contract,
    )


NEW_TASKS = (
    base.TaskSpec(
        split="validation",
        task_id="val-standard-region-lollipops",
        instruction="""Create a horizontal D3 lollipop chart for incident counts by region.
Preserve this exact order and values: North = 14, South = 9, East = 17,
West = 11, unit `incidents`. Render four `stem` lines and four `dot` circles,
with visible region/value labels. Use colorset1, a short D3 reveal, keyboard
focus that exposes each value, pattern ID `d3-region-lollipops`, and route
`visualization`.""" + base.VISUAL_TAIL,
        contract={
            "schemaVersion": 1,
            "taskId": "val-standard-region-lollipops",
            "route": "visualization",
            "colorset": "colorset1",
            "requireExtended": False,
            "expectedPatternId": "d3-region-lollipops",
            "requiredTerms": ["North", "South", "East", "West", "14", "9", "17", "11", "incidents"],
            "orderedTerms": ["North", "South", "East", "West"],
            "tagMinimums": {"svg": 1, "title": 1, "desc": 1, "line": 4, "circle": 4, "text": 9},
            "classMinimums": {"stem": 4, "dot": 4},
            "requiredIds": ["region-lollipops"],
            "requiredAttributes": {"data-chart-kind": "lollipop"},
            "requiresAnimation": True,
            "requiresInteraction": True,
            "visualPalette": base.visual_profile("colorset1", ["primary"]),
        },
    ),
    base.TaskSpec(
        split="validation",
        task_id="val-extended-kaleidoscope-logo",
        instruction="""Create a parametric D3/SVG logo for the exact brand `Prism Arc`
with tagline `Many signals, one form`. I explicitly want the extended full-color
palette. Build twelve deterministic radial `wedge` paths using meaningful
colorset2 accent, warning, and special hues. Include one `logo-mark`, exact
brand/tagline text, a short settled reveal, pattern ID
`d3-logo-kaleidoscope-wedges`, and route `logo`.""" + base.VISUAL_TAIL,
        contract={
            "schemaVersion": 1,
            "taskId": "val-extended-kaleidoscope-logo",
            "route": "logo",
            "colorset": "colorset2",
            "requireExtended": True,
            "expectedPatternId": "d3-logo-kaleidoscope-wedges",
            "requiredTerms": ["Prism Arc", "Many signals, one form"],
            "orderedTerms": [],
            "tagMinimums": {"svg": 1, "title": 1, "desc": 1, "path": 12, "text": 2},
            "classMinimums": {"logo-mark": 1, "wedge": 12, "brand-text": 1, "tagline": 1},
            "requiredIds": ["prism-arc-logo"],
            "requiredAttributes": {"data-logo-pattern": "d3-logo-kaleidoscope-wedges"},
            "requiresAnimation": True,
            "requiresInteraction": False,
            "visualPalette": base.visual_profile("colorset2", ["accent", "warning", "special"], distinct=3),
        },
    ),
    base.TaskSpec(
        split="validation",
        task_id="val-flow-ingest-recomposition",
        instruction="""Recompose an ingest pipeline into a flow-spine D3/SVG composition.
Preserve four nodes in order: Capture, Normalize, Check, Publish. Preserve three
directed links and values: Capture→Normalize 9, Normalize→Check 7,
Check→Publish 5. Use literal classes `node` and `link`. The SVG ID and global
variant ID must both be `d3-composition-flow-ingest-pipeline`; expose source
example `ingest-pipeline`, base pattern `d3-ingest-pipeline`, composition `flow`,
and `data-layout="flow-spine"`. Use colorset1 and route `recomposition`.""" + base.VISUAL_TAIL,
        contract={
            "schemaVersion": 1,
            "taskId": "val-flow-ingest-recomposition",
            "route": "recomposition",
            "colorset": "colorset1",
            "requireExtended": False,
            "expectedPatternId": "d3-composition-flow-ingest-pipeline",
            "requiredTerms": ["Capture", "Normalize", "Check", "Publish", "9", "7", "5"],
            "orderedTerms": ["Capture", "Normalize", "Check", "Publish"],
            "tagMinimums": {"svg": 1, "title": 1, "desc": 1, "rect": 4, "path": 3, "text": 7},
            "classMinimums": {"node": 4, "link": 3},
            "requiredIds": ["d3-composition-flow-ingest-pipeline"],
            "requiredAttributes": {
                "data-composition-id": "flow",
                "data-example-id": "ingest-pipeline",
                "data-pattern-id": "d3-ingest-pipeline",
                "data-composition-pattern-id": "d3-composition-flow-ingest-pipeline",
                "data-layout": "flow-spine",
            },
            "requiresAnimation": False,
            "requiresInteraction": False,
            "visualPalette": base.visual_profile("colorset1", ["primary"]),
        },
    ),
    base.TaskSpec(
        split="holdout",
        task_id="hold-extended-capacity-sunburst",
        instruction="""Create an interactive D3 sunburst for a capacity budget. Preserve
the hierarchy and values exactly: Capacity = 100; Plan = 30 with Design = 12
and Review = 18; Build = 45 with Code = 25 and Test = 20; Run = 25. Render
exactly seven `segment` paths for the non-root nodes, label every node and value,
and expose focus interaction plus a short radial reveal. I explicitly want
colorset2 with materially visible accent, warning, success, and special groups.
Use pattern ID `d3-capacity-sunburst` and route `visualization`.""" + base.VISUAL_TAIL,
        contract={
            "schemaVersion": 1,
            "taskId": "hold-extended-capacity-sunburst",
            "route": "visualization",
            "colorset": "colorset2",
            "requireExtended": True,
            "expectedPatternId": "d3-capacity-sunburst",
            "requiredTerms": ["Capacity", "Plan", "Design", "Review", "Build", "Code", "Test", "Run", "100", "30", "12", "18", "45", "25", "20"],
            "orderedTerms": [],
            "tagMinimums": {"svg": 1, "title": 1, "desc": 1, "path": 7, "text": 15},
            "classMinimums": {"segment": 7},
            "requiredIds": ["capacity-sunburst"],
            "requiredAttributes": {"data-chart-kind": "sunburst"},
            "requiresAnimation": True,
            "requiresInteraction": True,
            "visualPalette": base.visual_profile("colorset2", ["accent", "warning", "success", "special"], distinct=4),
        },
    ),
    base.TaskSpec(
        split="holdout",
        task_id="hold-standard-superellipse-logo",
        instruction="""Create a deterministic D3/SVG identity for exact brand `Quiet Loop`
and tagline `Reliable by design`. Use the standard colorset1 palette. Build a
three-ring superellipse family as three `superellipse` paths inside one
`logo-mark`; preserve readable `brand-text` and `tagline`, add a short settled
path reveal, and avoid arbitrary or extended colors. Use SVG ID
`quiet-loop-logo`, pattern ID `d3-logo-superellipse-family`, and route `logo`.""" + base.VISUAL_TAIL,
        contract={
            "schemaVersion": 1,
            "taskId": "hold-standard-superellipse-logo",
            "route": "logo",
            "colorset": "colorset1",
            "requireExtended": False,
            "expectedPatternId": "d3-logo-superellipse-family",
            "requiredTerms": ["Quiet Loop", "Reliable by design"],
            "orderedTerms": [],
            "tagMinimums": {"svg": 1, "title": 1, "desc": 1, "path": 3, "text": 2},
            "classMinimums": {"logo-mark": 1, "superellipse": 3, "brand-text": 1, "tagline": 1},
            "requiredIds": ["quiet-loop-logo"],
            "requiredAttributes": {"data-logo-pattern": "d3-logo-superellipse-family"},
            "requiresAnimation": True,
            "requiresInteraction": False,
            "visualPalette": base.visual_profile("colorset1", ["primary"]),
        },
    ),
    base.TaskSpec(
        split="holdout",
        task_id="hold-diagonal-rollout-recomposition",
        instruction="""Recompose a rollout-risk chain into a diagonal armature while
preserving five nodes in order: Intake, Canary, Expand, Observe, Close. Preserve
four directed links with values 4, 3, 2, 1. Use literal classes `node` and
`link`. The SVG ID and variant ID must be
`d3-composition-diagonal-rollout-risks`; expose source example `rollout-risks`,
base pattern `d3-rollout-risks`, composition `diagonal`, and
`data-layout="diagonal"`. Use colorset1 and route `recomposition`.""" + base.VISUAL_TAIL,
        contract={
            "schemaVersion": 1,
            "taskId": "hold-diagonal-rollout-recomposition",
            "route": "recomposition",
            "colorset": "colorset1",
            "requireExtended": False,
            "expectedPatternId": "d3-composition-diagonal-rollout-risks",
            "requiredTerms": ["Intake", "Canary", "Expand", "Observe", "Close", "4", "3", "2", "1"],
            "orderedTerms": ["Intake", "Canary", "Expand", "Observe", "Close"],
            "tagMinimums": {"svg": 1, "title": 1, "desc": 1, "circle": 5, "path": 4, "text": 9},
            "classMinimums": {"node": 5, "link": 4},
            "requiredIds": ["d3-composition-diagonal-rollout-risks"],
            "requiredAttributes": {
                "data-composition-id": "diagonal",
                "data-example-id": "rollout-risks",
                "data-pattern-id": "d3-rollout-risks",
                "data-composition-pattern-id": "d3-composition-diagonal-rollout-risks",
                "data-layout": "diagonal",
            },
            "requiresAnimation": False,
            "requiresInteraction": False,
            "visualPalette": base.visual_profile("colorset1", ["primary"]),
        },
    ),
    base.TaskSpec(
        split="holdout",
        task_id="hold-balance-composition-audit",
        instruction="""Evaluate this visible SVG artifact as `balance-target.svg`:

```svg
<svg id="balance-target" viewBox="0 0 420 240" role="img">
  <title>Release decision board</title>
  <desc>Two large risks compete with one small approval state.</desc>
  <circle id="risk-a" cx="58" cy="60" r="42" fill="#9e1b32"/>
  <circle id="risk-b" cx="132" cy="82" r="38" fill="#ffccd5"/>
  <path id="decision-path" d="M96 74 L245 74 L390 210" fill="none" stroke="#333e48"/>
  <rect id="approval" x="374" y="194" width="38" height="38" fill="#e7e7e7"/>
  <text id="risk-label" x="38" y="64">release risk</text>
  <text id="approval-label" x="398" y="238">approve</text>
</svg>
```

Start exactly with `Artifact: balance-target.svg`. Address the visual-weight
imbalance between `#risk-a`, `#risk-b`, and `#approval`; the reading path of
`#decision-path`; clipping risk at `#approval-label`; label clearance, balance,
data integrity, and implementation-contract checks. Include
`Overall composition score: <integer>/100` and a `Validation` section. Use
colorset1, pattern ID `d3-composition-audit`, and route `evaluation`.""" + base.EVALUATION_TAIL,
        contract={
            "schemaVersion": 1,
            "taskId": "hold-balance-composition-audit",
            "route": "evaluation",
            "colorset": "colorset1",
            "expectedPatternId": "d3-composition-audit",
            "requiredTerms": [
                "Artifact: balance-target.svg", "#risk-a", "#risk-b", "#approval",
                "#decision-path", "#approval-label", "visual weight", "reading path",
                "label clearance", "balance", "data integrity", "implementation contract",
                "Validation",
            ],
            "patterns": [r"Overall composition score:\s*\d{1,3}/100"],
        },
    ),
)


TASKS = (
    clone_base_task("dev-standard-defect-bars", split="development", task_id="dev-standard-defect-bars"),
    clone_base_task("dev-extended-service-network", split="development", task_id="dev-extended-service-network"),
    clone_base_task("dev-standard-orbit-logo", split="development", task_id="dev-standard-orbit-logo"),
    clone_base_task("val-composition-clearance-audit", split="development", task_id="dev-composition-clearance-audit"),
    clone_base_task("val-radial-review-recomposition", split="development", task_id="dev-radial-review-recomposition"),
    *NEW_TASKS,
)


def with_profile(contract: dict[str, Any]) -> dict[str, Any]:
    updated = copy.deepcopy(contract)
    updated["bundleProfile"] = copy.deepcopy(BUNDLE_PROFILE)
    return updated


TASKS = tuple(
    base.TaskSpec(spec.split, spec.task_id, spec.instruction, with_profile(spec.contract))
    for spec in TASKS
)


def public_contract(contract: dict[str, Any]) -> dict[str, Any]:
    disclosed = base.public_contract(contract)
    disclosed["bundleProfile"] = contract["bundleProfile"]
    return disclosed


def render_instruction(spec: base.TaskSpec) -> str:
    disclosed = json.dumps(public_contract(spec.contract), indent=2, sort_keys=True)
    return (
        spec.instruction.strip()
        + "\n\n"
        + base.PUBLIC_CONTRACT_MARKER
        + "\n\n"
        + base.PUBLIC_CONTRACT_SEMANTICS
        + "\n\n```json\n"
        + disclosed
        + "\n```\n"
    )


def task_body(text: str) -> str:
    return text.split(base.PUBLIC_CONTRACT_MARKER, 1)[0].strip()


def validate_specs(burned_holdout_root: Path) -> dict[str, Any]:
    expected_counts = {"development": 5, "validation": 3, "holdout": 4}
    counts = Counter(spec.split for spec in TASKS)
    if dict(counts) != expected_counts:
        raise ValueError(f"Unexpected split counts: {dict(counts)}")
    ids = [spec.task_id for spec in TASKS]
    if len(ids) != len(set(ids)):
        raise ValueError("Task IDs must be unique")
    if any(not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", task_id) for task_id in ids):
        raise ValueError("Task IDs must use lowercase hyphen-case")
    visible_routes = {spec.contract["route"] for spec in TASKS if spec.split != "holdout"}
    holdout_routes = {spec.contract["route"] for spec in TASKS if spec.split == "holdout"}
    expected_routes = {"visualization", "logo", "recomposition", "evaluation"}
    if visible_routes != expected_routes or holdout_routes != expected_routes:
        raise ValueError("Optimizer-visible and holdout route coverage must both be complete")

    fingerprints = {
        hashlib.sha256(
            (spec.instruction + "\0" + json.dumps(spec.contract, sort_keys=True)).encode("utf-8")
        ).hexdigest()
        for spec in TASKS
    }
    if len(fingerprints) != len(TASKS):
        raise ValueError("Task content must be disjoint")

    if not burned_holdout_root.is_dir():
        raise ValueError(f"Burned holdout root is missing: {burned_holdout_root}")
    burned_ids = {path.name for path in burned_holdout_root.iterdir() if path.is_dir()}
    overlap_ids = sorted(set(ids) & burned_ids)
    burned_bodies = {
        hashlib.sha256(task_body((path / "instruction.md").read_text(encoding="utf-8")).encode("utf-8")).hexdigest()
        for path in burned_holdout_root.iterdir()
        if path.is_dir() and (path / "instruction.md").is_file()
    }
    new_bodies = {
        hashlib.sha256(task_body(spec.instruction).encode("utf-8")).hexdigest()
        for spec in TASKS
    }
    overlap_bodies = sorted(new_bodies & burned_bodies)
    if overlap_ids or overlap_bodies:
        raise ValueError(
            f"New dataset overlaps burned holdout: ids={len(overlap_ids)}, bodies={len(overlap_bodies)}"
        )
    return {
        "splitCounts": expected_counts,
        "colorsetCounts": dict(Counter(spec.contract["colorset"] for spec in TASKS)),
        "routeCounts": dict(Counter(spec.contract["route"] for spec in TASKS)),
        "taskCount": len(TASKS),
        "burnedHoldoutTaskIdOverlap": 0,
        "burnedHoldoutInstructionOverlap": 0,
    }


TEST_SH = """#!/usr/bin/env bash
set -o pipefail
python3 "$(dirname "$0")/verify_pareto_task.py"
"""


def write_task(root: Path, spec: base.TaskSpec, helper_root: Path) -> None:
    task_root = root / spec.split / spec.task_id
    (task_root / "environment").mkdir(parents=True)
    (task_root / "tests").mkdir(parents=True)
    (task_root / "instruction.md").write_text(render_instruction(spec), encoding="utf-8", newline="\n")
    (task_root / "task.toml").write_text(base.TASK_TOML, encoding="utf-8", newline="\n")
    (task_root / "environment" / ".gitkeep").write_text("", encoding="utf-8")
    (task_root / "tests" / "contract.json").write_text(
        json.dumps(spec.contract, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n"
    )
    (task_root / "tests" / "test.sh").write_text(TEST_SH, encoding="utf-8", newline="\n")
    for filename in (
        "verify_task.py",
        "verify_pareto_task.py",
        "visual_palette.py",
        "render_browser.js",
    ):
        shutil.copy2(helper_root / filename, task_root / "tests" / filename)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--burned-holdout-root", type=Path, required=True)
    parser.add_argument("--attempts", type=int, default=2)
    parser.add_argument("--concurrency", type=int, default=4)
    parser.add_argument("--model", default="gpt-5.3-codex-spark")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", args.run_id):
        raise SystemExit("--run-id must be lowercase hyphen-case")
    if args.attempts < 1 or args.concurrency < 1:
        raise SystemExit("--attempts and --concurrency must be positive")
    output_root = args.output_root.resolve()
    if output_root.exists() and any(output_root.iterdir()):
        raise SystemExit(f"Refusing non-empty output directory: {output_root}")
    output_root.mkdir(parents=True, exist_ok=True)
    helper_root = Path(__file__).resolve().parent
    repo_root = helper_root.parents[1]
    burned_root = args.burned_holdout_root.resolve()
    stats = validate_specs(burned_root)
    for spec in TASKS:
        write_task(output_root, spec, helper_root)
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
            )
        )
        for split in ("development", "validation", "holdout")
    }
    split_digests = {
        split: base.tree_digest(output_root / split)
        for split in ("development", "validation", "holdout")
    }
    manifest = {
        "schemaVersion": 3,
        "runId": args.run_id,
        "model": args.model,
        "attempts": args.attempts,
        "concurrency": args.concurrency,
        "stats": stats,
        "bundleProfile": BUNDLE_PROFILE,
        "splitDigests": split_digests,
        "jobConfigs": configs,
        "burnedHoldoutTreeDigest": base.tree_digest(burned_root),
        "holdoutPolicy": (
            "Register and seal before candidate materialization; never expose to Pareto "
            "reflection or validation selection; release once for the digest-frozen winner."
        ),
    }
    (output_root / "dataset-manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n"
    )
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
