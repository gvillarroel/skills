#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Build fresh D3 validation and randomized sealed holdout cohorts."""

from __future__ import annotations

import argparse
from collections import Counter
import copy
import hashlib
import json
from pathlib import Path
import re
import secrets
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

PARETO_TEST_SH = """#!/usr/bin/env bash
set -o pipefail
python3 "$(dirname "$0")/verify_pareto_task.py"
"""


def with_profile(contract: dict[str, Any]) -> dict[str, Any]:
    updated = copy.deepcopy(contract)
    updated["bundleProfile"] = copy.deepcopy(BUNDLE_PROFILE)
    return updated


def public_contract(contract: dict[str, Any]) -> dict[str, Any]:
    disclosed = base.public_contract(contract)
    disclosed["bundleProfile"] = contract["bundleProfile"]
    if "visualPalette" in contract:
        disclosed["paintContract"] = {
            "forbidFunctionalColorSyntax": True,
            "literalActiveColorsetTokensOnly": True,
            "requiredGroups": contract["visualPalette"]["requiredGroups"],
            "minDistinctVisibleColors": contract["visualPalette"]["minDistinctColors"],
            "requireExtendedToken": bool(contract.get("requireExtended")),
            "requireVisiblePaletteInfluence": True,
        }
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


def visual_contract(
    *,
    task_id: str,
    route: str,
    colorset: str,
    pattern_id: str,
    required_terms: list[str],
    ordered_terms: list[str],
    tags: dict[str, int],
    classes: dict[str, int],
    required_id: str,
    attributes: dict[str, str],
    animation: bool,
    interaction: bool,
    groups: list[str],
    distinct: int = 1,
) -> dict[str, Any]:
    return with_profile(
        {
            "schemaVersion": 1,
            "taskId": task_id,
            "route": route,
            "colorset": colorset,
            "requireExtended": colorset == "colorset2",
            "expectedPatternId": pattern_id,
            "requiredTerms": required_terms,
            "orderedTerms": ordered_terms,
            "tagMinimums": tags,
            "classMinimums": classes,
            "requiredIds": [required_id],
            "requiredAttributes": attributes,
            "requiresAnimation": animation,
            "requiresInteraction": interaction,
            "visualPalette": base.visual_profile(colorset, groups, distinct=distinct),
        }
    )


def evaluation_contract(
    task_id: str,
    artifact: str,
    selectors: list[str],
) -> dict[str, Any]:
    return with_profile(
        {
            "schemaVersion": 1,
            "taskId": task_id,
            "route": "evaluation",
            "colorset": "colorset1",
            "expectedPatternId": "d3-composition-audit",
            "requiredTerms": [
                f"Artifact: {artifact}",
                *selectors,
                "label clearance",
                "reading path",
                "balance",
                "data integrity",
                "implementation contract",
                "Validation",
            ],
            "patterns": [r"Overall composition score:\s*\d{1,3}/100"],
        }
    )


def validation_specs() -> list[base.TaskSpec]:
    lollipop_id = "val2-standard-queue-lollipops"
    lollipop_labels = ["Gateway", "Parser", "Indexer", "Notifier", "Archive"]
    lollipop_values = [13, 8, 16, 11, 6]
    lollipop_terms = [
        item for pair in zip(lollipop_labels, map(str, lollipop_values), strict=True) for item in pair
    ] + ["queued items"]
    flow_id = "val2-flow-release-recomposition"
    flow_labels = ["Draft", "Review", "Stage", "Launch", "Observe"]
    flow_values = [11, 9, 6, 4]
    flow_terms = [*flow_labels, *map(str, flow_values)]
    logo_id = "val2-extended-radial-wedge-logo"
    audit_id = "val2-composition-lane-audit"
    artifact = "lane-audit.svg"
    selectors = ["#label-west", "#node-west", "#label-east", "#route-main"]
    return [
        base.TaskSpec(
            split="validation",
            task_id=lollipop_id,
            instruction=(
                "Create a horizontal D3 lollipop chart for queued items by service. "
                "Preserve this exact order and values: Gateway = 13, Parser = 8, "
                "Indexer = 16, Notifier = 11, Archive = 6, unit `queued items`. "
                "Render five `stem` lines and five `dot` circles with visible labels. "
                "Use colorset1, a short reveal, keyboard focus exposing each value, "
                "pattern ID `d3-queue-lollipops`, and route `visualization`."
                + base.VISUAL_TAIL
            ),
            contract=visual_contract(
                task_id=lollipop_id,
                route="visualization",
                colorset="colorset1",
                pattern_id="d3-queue-lollipops",
                required_terms=lollipop_terms,
                ordered_terms=lollipop_labels,
                tags={"svg": 1, "title": 1, "desc": 1, "line": 5, "circle": 5, "text": 11},
                classes={"stem": 5, "dot": 5},
                required_id="queue-lollipops",
                attributes={"data-chart-kind": "lollipop"},
                animation=True,
                interaction=True,
                groups=["primary"],
            ),
        ),
        base.TaskSpec(
            split="validation",
            task_id=flow_id,
            instruction=(
                "Recompose a release pipeline into a flow-spine D3/SVG composition. "
                "Preserve five nodes in order: Draft, Review, Stage, Launch, Observe. "
                "Preserve four directed links and values: Draft→Review 11, Review→Stage 9, "
                "Stage→Launch 6, Launch→Observe 4. Use literal classes `node` and `link`. "
                "Use SVG/global variant ID `d3-composition-flow-release-pipeline`, source "
                "example `release-pipeline`, base pattern `d3-release-pipeline`, composition "
                "`flow`, `data-layout=\"flow-spine\"`, colorset1, and route `recomposition`."
                + base.VISUAL_TAIL
            ),
            contract=visual_contract(
                task_id=flow_id,
                route="recomposition",
                colorset="colorset1",
                pattern_id="d3-composition-flow-release-pipeline",
                required_terms=flow_terms,
                ordered_terms=flow_labels,
                tags={"svg": 1, "title": 1, "desc": 1, "rect": 5, "path": 4, "text": 9},
                classes={"node": 5, "link": 4},
                required_id="d3-composition-flow-release-pipeline",
                attributes={
                    "data-composition-id": "flow",
                    "data-example-id": "release-pipeline",
                    "data-pattern-id": "d3-release-pipeline",
                    "data-composition-pattern-id": "d3-composition-flow-release-pipeline",
                    "data-layout": "flow-spine",
                },
                animation=False,
                interaction=False,
                groups=["primary"],
            ),
        ),
        base.TaskSpec(
            split="validation",
            task_id=logo_id,
            instruction=(
                "Create a parametric D3/SVG logo for exact brand `Aurora Grid` with tagline "
                "`Clarity around every signal`. Explicitly use the extended full-color palette. "
                "Build ten deterministic radial `wedge` paths using materially visible colorset2 "
                "accent, warning, success, and special hues. Include one `logo-mark`, exact text, "
                "a short settled reveal, pattern ID `d3-logo-radial-wedges`, and route `logo`."
                + base.VISUAL_TAIL
            ),
            contract=visual_contract(
                task_id=logo_id,
                route="logo",
                colorset="colorset2",
                pattern_id="d3-logo-radial-wedges",
                required_terms=["Aurora Grid", "Clarity around every signal"],
                ordered_terms=[],
                tags={"svg": 1, "title": 1, "desc": 1, "path": 10, "text": 2},
                classes={"logo-mark": 1, "wedge": 10, "brand-text": 1, "tagline": 1},
                required_id="aurora-grid-logo",
                attributes={"data-logo-pattern": "d3-logo-radial-wedges"},
                animation=True,
                interaction=False,
                groups=["accent", "warning", "success", "special"],
                distinct=4,
            ),
        ),
        base.TaskSpec(
            split="validation",
            task_id=audit_id,
            instruction=(
                "Evaluate this visible SVG artifact as `lane-audit.svg`:\n\n"
                "```svg\n<svg id=\"lane-audit\" viewBox=\"0 0 420 230\" role=\"img\">\n"
                "  <title>Deployment lane</title><desc>Three stages along one route.</desc>\n"
                "  <path id=\"route-main\" d=\"M28 42 L205 42 L394 198\" fill=\"none\" stroke=\"#9e1b32\"/>\n"
                "  <circle id=\"node-west\" cx=\"28\" cy=\"42\" r=\"26\" fill=\"#ffccd5\"/>\n"
                "  <circle id=\"node-mid\" cx=\"205\" cy=\"42\" r=\"18\" fill=\"#cfcfcf\"/>\n"
                "  <circle id=\"node-east\" cx=\"394\" cy=\"198\" r=\"17\" fill=\"#e7e7e7\"/>\n"
                "  <text id=\"label-west\" x=\"28\" y=\"42\">build queue</text>\n"
                "  <text id=\"label-east\" x=\"418\" y=\"202\">observe queue</text>\n</svg>\n```\n\n"
                "Identify selector-specific collision, clipping, reading-path, clearance, balance, "
                "data-integrity, and implementation-contract problems. Start exactly with "
                "`Artifact: lane-audit.svg`, include `Overall composition score: <integer>/100`, "
                "a `Validation` section, colorset1, pattern `d3-composition-audit`, and route `evaluation`."
                + base.EVALUATION_TAIL
            ),
            contract=evaluation_contract(audit_id, artifact, selectors),
        ),
    ]


def randomized_specs(
    *, split: str, task_prefix: str, visibility_label: str
) -> tuple[list[base.TaskSpec], str]:
    if split not in {"validation", "holdout"}:
        raise ValueError(f"Unsupported randomized split: {split}")
    chooser = secrets.SystemRandom()
    nonce = secrets.token_hex(6)
    service_pool = ["Relay", "Beacon", "Cache", "Ledger", "Vault", "Bridge", "Broker"]
    flow_pool = ["Receive", "Decode", "Classify", "Route", "Persist", "Confirm", "Observe"]
    brand_left = ["Cinder", "Lumen", "Vector", "Nimbus", "Mosaic", "Quarry"]
    brand_right = ["Loop", "Field", "Works", "Signal", "Arc", "Frame"]
    taglines = [
        "Shape every signal",
        "Patterns into motion",
        "Clarity through structure",
        "A system you can read",
    ]
    labels = chooser.sample(service_pool, 5)
    values = [chooser.randrange(5, 24) for _ in labels]
    flow_labels = chooser.sample(flow_pool, 5)
    flow_values = sorted(chooser.sample(range(4, 19), 4), reverse=True)
    wedge_count = chooser.randrange(9, 14)
    brand = f"{chooser.choice(brand_left)} {chooser.choice(brand_right)}"
    tagline = chooser.choice(taglines)
    namespace = visibility_label.casefold()
    visual_pattern = f"d3-{namespace}-{nonce}-lollipops"
    flow_pattern = f"d3-composition-flow-{namespace}-{nonce}"
    logo_pattern = f"d3-logo-{namespace}-{nonce}-wedges"
    visual_id = f"{namespace}-{nonce}-lollipops"
    logo_id = f"{namespace}-{nonce}-logo"
    flow_base = f"{namespace}-{nonce}-pipeline"
    flow_example = f"{namespace}-{nonce}-source"
    visual_terms = [item for pair in zip(labels, map(str, values), strict=True) for item in pair] + ["work items"]
    flow_terms = [*flow_labels, *map(str, flow_values)]
    link_text = ", ".join(
        f"{flow_labels[index]}→{flow_labels[index + 1]} {flow_values[index]}"
        for index in range(4)
    )
    item_text = ", ".join(f"{label} = {value}" for label, value in zip(labels, values, strict=True))
    audit_artifact = f"{namespace}-audit-{nonce}.svg"
    audit_selectors = [f"#label-a-{nonce}", f"#node-a-{nonce}", f"#label-b-{nonce}", f"#route-{nonce}"]
    lollipop_task_id = f"{task_prefix}-lollipop"
    flow_task_id = f"{task_prefix}-flow-recomposition"
    logo_task_id = f"{task_prefix}-wedge-logo"
    audit_task_id = f"{task_prefix}-composition-audit"
    specs = [
        base.TaskSpec(
            split=split,
            task_id=lollipop_task_id,
            instruction=(
                f"Create a horizontal D3 lollipop chart for work items by service. Preserve exact order and values: {item_text}, unit `work items`. "
                f"Render five `stem` lines and five `dot` circles with visible labels. Use colorset1, a short reveal, keyboard focus exposing each value, pattern ID `{visual_pattern}`, and route `visualization`."
                + base.VISUAL_TAIL
            ),
            contract=visual_contract(
                task_id=lollipop_task_id,
                route="visualization",
                colorset="colorset1",
                pattern_id=visual_pattern,
                required_terms=visual_terms,
                ordered_terms=labels,
                tags={"svg": 1, "title": 1, "desc": 1, "line": 5, "circle": 5, "text": 11},
                classes={"stem": 5, "dot": 5},
                required_id=visual_id,
                attributes={"data-chart-kind": "lollipop"},
                animation=True,
                interaction=True,
                groups=["primary"],
            ),
        ),
        base.TaskSpec(
            split=split,
            task_id=flow_task_id,
            instruction=(
                f"Recompose a pipeline into a flow-spine D3/SVG composition. Preserve five nodes in order: {', '.join(flow_labels)}. Preserve directed links and values: {link_text}. "
                f"Use classes `node` and `link`, SVG/global ID `{flow_pattern}`, source example `{flow_example}`, base pattern `d3-{flow_base}`, composition `flow`, `data-layout=\"flow-spine\"`, colorset1, and route `recomposition`."
                + base.VISUAL_TAIL
            ),
            contract=visual_contract(
                task_id=flow_task_id,
                route="recomposition",
                colorset="colorset1",
                pattern_id=flow_pattern,
                required_terms=flow_terms,
                ordered_terms=flow_labels,
                tags={"svg": 1, "title": 1, "desc": 1, "rect": 5, "path": 4, "text": 9},
                classes={"node": 5, "link": 4},
                required_id=flow_pattern,
                attributes={
                    "data-composition-id": "flow",
                    "data-example-id": flow_example,
                    "data-pattern-id": f"d3-{flow_base}",
                    "data-composition-pattern-id": flow_pattern,
                    "data-layout": "flow-spine",
                },
                animation=False,
                interaction=False,
                groups=["primary"],
            ),
        ),
        base.TaskSpec(
            split=split,
            task_id=logo_task_id,
            instruction=(
                f"Create a parametric D3/SVG logo for exact brand `{brand}` with tagline `{tagline}`. Explicitly use the extended full-color palette. Build {wedge_count} deterministic radial `wedge` paths using materially visible colorset2 accent, warning, success, and special hues. Include one `logo-mark`, exact text, a short settled reveal, pattern ID `{logo_pattern}`, and route `logo`."
                + base.VISUAL_TAIL
            ),
            contract=visual_contract(
                task_id=logo_task_id,
                route="logo",
                colorset="colorset2",
                pattern_id=logo_pattern,
                required_terms=[brand, tagline],
                ordered_terms=[],
                tags={"svg": 1, "title": 1, "desc": 1, "path": wedge_count, "text": 2},
                classes={"logo-mark": 1, "wedge": wedge_count, "brand-text": 1, "tagline": 1},
                required_id=logo_id,
                attributes={"data-logo-pattern": logo_pattern},
                animation=True,
                interaction=False,
                groups=["accent", "warning", "success", "special"],
                distinct=4,
            ),
        ),
        base.TaskSpec(
            split=split,
            task_id=audit_task_id,
            instruction=(
                f"Evaluate this visible SVG artifact as `{audit_artifact}`:\n\n```svg\n"
                f"<svg id=\"audit-{nonce}\" viewBox=\"0 0 410 225\" role=\"img\"><title>{visibility_label} route</title><desc>Three stages.</desc>"
                f"<path id=\"route-{nonce}\" d=\"M24 38 L198 38 L392 196\" fill=\"none\" stroke=\"#9e1b32\"/>"
                f"<circle id=\"node-a-{nonce}\" cx=\"24\" cy=\"38\" r=\"25\" fill=\"#ffccd5\"/>"
                f"<circle id=\"node-mid-{nonce}\" cx=\"198\" cy=\"38\" r=\"18\" fill=\"#cfcfcf\"/>"
                f"<circle id=\"node-b-{nonce}\" cx=\"392\" cy=\"196\" r=\"17\" fill=\"#e7e7e7\"/>"
                f"<text id=\"label-a-{nonce}\" x=\"24\" y=\"38\">entry lane</text>"
                f"<text id=\"label-b-{nonce}\" x=\"408\" y=\"200\">exit lane</text></svg>\n```\n\n"
                f"Identify selector-specific collision, clipping, reading-path, clearance, balance, data-integrity, and implementation-contract problems. Start exactly with `Artifact: {audit_artifact}`, include `Overall composition score: <integer>/100`, a `Validation` section, colorset1, pattern `d3-composition-audit`, and route `evaluation`."
                + base.EVALUATION_TAIL
            ),
            contract=evaluation_contract(audit_task_id, audit_artifact, audit_selectors),
        ),
    ]
    return specs, hashlib.sha256(nonce.encode("ascii")).hexdigest()


def write_task(root: Path, spec: base.TaskSpec, helper_root: Path) -> None:
    base.write_task(root, spec, helper_root)
    task_root = root / spec.split / spec.task_id
    (task_root / "instruction.md").write_text(
        render_instruction(spec), encoding="utf-8", newline="\n"
    )
    (task_root / "tests" / "test.sh").write_text(
        PARETO_TEST_SH, encoding="utf-8", newline="\n"
    )
    shutil.copy2(
        helper_root / "verify_pareto_task.py",
        task_root / "tests" / "verify_pareto_task.py",
    )


def instruction_hashes(root: Path) -> set[str]:
    return {
        hashlib.sha256(path.read_bytes()).hexdigest()
        for path in root.rglob("instruction.md")
    }


def validate_specs(specs: list[base.TaskSpec]) -> dict[str, Any]:
    counts = Counter(spec.split for spec in specs)
    if counts != {"validation": 4, "holdout": 4}:
        raise ValueError(f"Unexpected split counts: {dict(counts)}")
    ids = [spec.task_id for spec in specs]
    if len(ids) != len(set(ids)):
        raise ValueError("Task IDs must be unique")
    if any(not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", task_id) for task_id in ids):
        raise ValueError("Task IDs must be lowercase hyphen-case")
    for split in ("validation", "holdout"):
        routes = {spec.contract["route"] for spec in specs if spec.split == split}
        if routes != {"visualization", "logo", "recomposition", "evaluation"}:
            raise ValueError(f"{split} route coverage is incomplete: {sorted(routes)}")
    fingerprints = {
        hashlib.sha256(
            (spec.instruction + "\0" + json.dumps(spec.contract, sort_keys=True)).encode("utf-8")
        ).hexdigest()
        for spec in specs
    }
    if len(fingerprints) != len(specs):
        raise ValueError("Task content must be disjoint")
    return {
        "splitCounts": dict(counts),
        "routeCounts": dict(Counter(spec.contract["route"] for spec in specs)),
        "colorsetCounts": dict(Counter(spec.contract["colorset"] for spec in specs)),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument(
        "--prior-dataset-root",
        type=Path,
        action="append",
        required=True,
        help="Prior frozen dataset root; repeat to exclude overlap with every earlier cohort.",
    )
    parser.add_argument("--run-id", required=True)
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
    prior_roots = [path.resolve() for path in args.prior_dataset_root]
    if output_root.exists() and any(output_root.iterdir()):
        raise SystemExit(f"Refusing non-empty output directory: {output_root}")
    if len(prior_roots) != len(set(prior_roots)):
        raise SystemExit("--prior-dataset-root values must be unique")
    for prior_root in prior_roots:
        if not prior_root.is_dir():
            raise SystemExit(f"Prior frozen dataset is missing: {prior_root}")
    output_root.mkdir(parents=True, exist_ok=True)
    helper_root = Path(__file__).resolve().parent
    repo_root = helper_root.parents[1]
    run_key = hashlib.sha256(args.run_id.encode("utf-8")).hexdigest()[:10]
    validation, validation_nonce_digest = randomized_specs(
        split="validation", task_prefix=f"val-{run_key}", visibility_label="Fresh"
    )
    holdout, holdout_nonce_digest = randomized_specs(
        split="holdout", task_prefix=f"hold-{run_key}", visibility_label="Hidden"
    )
    specs = [*validation, *holdout]
    stats = validate_specs(specs)
    for spec in specs:
        write_task(output_root, spec, helper_root)
    old_hashes = set().union(*(instruction_hashes(root) for root in prior_roots))
    new_hashes = instruction_hashes(output_root)
    overlap = old_hashes & new_hashes
    if overlap:
        raise SystemExit("Fresh dataset instruction overlap detected")
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
        for split in ("validation", "holdout")
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
            split: base.tree_digest(output_root / split)
            for split in ("validation", "holdout")
        },
        "priorInstructionOverlap": len(overlap),
        "priorDatasetCount": len(prior_roots),
        "validationNonceSha256": validation_nonce_digest,
        "holdoutNonceSha256": holdout_nonce_digest,
        "holdoutPolicy": (
            "Generated with cryptographic randomness before candidate mutation; exact task "
            "content must remain unread and unreleased until one digest-frozen winner passes "
            "fresh validation. Holdout evidence may only decide final promotion."
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
                "priorInstructionOverlap": len(overlap),
                "validationNonceSha256": validation_nonce_digest,
                "holdoutNonceSha256": holdout_nonce_digest,
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
