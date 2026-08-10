#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Build the frozen unified-D3 Harbor datasets and native job configs."""

from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import re
import shutil
import sys
from typing import Any


TASK_TOML = """version = "1.0"

[metadata]

[verifier]
timeout_sec = 180.0

[agent]
timeout_sec = 900.0

[environment]
build_timeout_sec = 60.0
"""

TEST_SH = """#!/usr/bin/env bash
set -o pipefail
python3 "$(dirname "$0")/verify_task.py"
"""

VISUAL_TAIL = """

Use the installed `d3` skill. Work only inside this Harbor task workspace and
the installed skill. Do not inspect repository paths, prior trials, evaluator
tests, or network resources. Treat the installed skill as read-only.
Read `/app/.agents/skills/d3/SKILL.md` first; this is the only evaluated skill
bundle and the only skill path you may inspect.

Create exactly these two non-empty files:

- `deliverables/visual.html`
- `deliverables/decision.json`

`visual.html` must be self-contained and offline, use actual D3 calls, expose
`data-renderer="d3"`, include one rendered SVG with a stable viewBox, title,
description, stable IDs/classes, and active palette metadata. Embed any runtime
or data it needs; do not use a CDN or other network dependency. The evaluator
will load the HTML in Chromium and inspect the settled DOM and pixels.

`decision.json` must contain one JSON object with `route`, `colorset`,
`patternId`, and a concise non-empty `reason`. Record exactly the route and
colorset requested by this task. Keep every supplied label, value, unit, order,
count, and relationship literal. Do not create screenshots or evaluator
reports.
"""

EVALUATION_TAIL = """

Use the installed `d3` skill. Work only inside this Harbor task workspace and
the installed skill. Do not inspect repository paths, prior trials, evaluator
tests, or network resources. Treat the installed skill as read-only.
Read `/app/.agents/skills/d3/SKILL.md` first; this is the only evaluated skill
bundle and the only skill path you may inspect.

Create exactly these two non-empty files:

- `deliverables/evaluation.md`
- `deliverables/decision.json`

Start the report with the exact artifact identifier requested below. Give
traceable selector-specific findings, separate composition issues from
implementation-contract issues, preserve the supplied data semantics, report
one reconciled overall score out of 100, and include concrete validation or
browser checks. `decision.json` must contain one JSON object with `route`,
`colorset`, `patternId`, and a concise non-empty `reason`.
"""

PUBLIC_CONTRACT_FIELDS = (
    "route",
    "colorset",
    "expectedPatternId",
    "requiredTerms",
    "orderedTerms",
    "tagMinimums",
    "classMinimums",
    "requiredIds",
    "requiredAttributes",
    "requiresAnimation",
    "requiresInteraction",
    "patterns",
)

PUBLIC_CONTRACT_MARKER = "Public acceptance contract (every field is a task requirement):"
PUBLIC_CONTRACT_SEMANTICS = (
    "Minimum maps mean at least the stated rendered count. Every required ID must "
    "appear. Attribute scalars are exact values; an attribute array lists allowed "
    "alternatives, so choose exactly one array member and do not join members. "
    "Ordered terms must appear in the stated order. Paint must use literal tokens "
    "from the active colorset only: do not use rgb(), rgba(), hsl(), hsla(), gradients, "
    "color-mix(), or arbitrary colors. Required palette groups must materially affect "
    "visible rendered pixels."
)


@dataclass(frozen=True)
class TaskSpec:
    split: str
    task_id: str
    instruction: str
    contract: dict[str, Any]


def visual_profile(colorset: str, groups: list[str], *, distinct: int = 1) -> dict[str, Any]:
    return {
        "requiredGroups": groups,
        "minDistinctColors": distinct,
        "minPixelsPerColor": 24.0,
        "minPaletteEffectivePixels": 96.0,
        "minPaletteCoverageRatio": 0.0005,
        "minInfluenceEffectivePixels": 64.0,
        "minInfluenceRatio": 0.0005,
    }


TASKS = (
    TaskSpec(
        split="development",
        task_id="dev-standard-defect-bars",
        instruction="""Create a vertical D3 bar chart for escaped defects by release train.
Keep the input order and make every label, value, and unit visible: Alpha = 12,
Beta = 19, Gamma = 7, Delta = 15, unit `escaped defects`. Use the standard
palette, with colorset1 red as the primary bar color and neutral supporting
structure. Render exactly four `data-mark` bars. Add a short D3 load transition
and a keyboard-accessible hover/focus value interaction. Use the stable pattern
ID `d3-escaped-defect-bars` and record route `visualization`.""" + VISUAL_TAIL,
        contract={
            "schemaVersion": 1,
            "taskId": "dev-standard-defect-bars",
            "route": "visualization",
            "colorset": "colorset1",
            "requireExtended": False,
            "expectedPatternId": "d3-escaped-defect-bars",
            "requiredTerms": ["Alpha", "Beta", "Gamma", "Delta", "12", "19", "7", "15", "escaped defects"],
            "orderedTerms": ["Alpha", "Beta", "Gamma", "Delta"],
            "tagMinimums": {"svg": 1, "title": 1, "desc": 1, "rect": 4, "text": 9},
            "classMinimums": {"data-mark": 4},
            "requiredIds": ["defect-chart"],
            "requiredAttributes": {"data-chart-kind": "bar"},
            "requiresAnimation": True,
            "requiresInteraction": True,
            "visualPalette": visual_profile("colorset1", ["primary"]),
        },
    ),
    TaskSpec(
        split="development",
        task_id="dev-extended-service-network",
        instruction="""Create an interactive D3 service-dependency network with exactly five
nodes in this order: Gateway, Queue, Worker A, Worker B, Store. Render exactly
six directed links: Gateway→Queue, Queue→Worker A, Queue→Worker B, Worker A→Store,
Worker B→Store, and Store→Queue. I explicitly want the extended full-color
palette. Use colorset2 semantic hues: blue Gateway, orange Queue, green workers,
and purple Store, while keeping labels readable. Use D3 force or deterministic
pre-ticked placement, visible arrow direction, drag or focus interaction, and a
short link/node reveal. Use pattern ID `d3-service-dependency-network` and route
`visualization`.""" + VISUAL_TAIL,
        contract={
            "schemaVersion": 1,
            "taskId": "dev-extended-service-network",
            "route": "visualization",
            "colorset": "colorset2",
            "requireExtended": True,
            "expectedPatternId": "d3-service-dependency-network",
            "requiredTerms": ["Gateway", "Queue", "Worker A", "Worker B", "Store"],
            "orderedTerms": [],
            "tagMinimums": {"svg": 1, "title": 1, "desc": 1, "circle": 5, "line": 6, "text": 5},
            "classMinimums": {"node": 5, "link": 6},
            "requiredIds": ["service-network"],
            "requiredAttributes": {"data-layout": ["force", "pre-ticked-force"]},
            "requiresAnimation": True,
            "requiresInteraction": True,
            "visualPalette": visual_profile("colorset2", ["accent", "warning", "success", "special"], distinct=4),
        },
    ),
    TaskSpec(
        split="development",
        task_id="dev-standard-orbit-logo",
        instruction="""Create a deterministic D3/SVG identity mark for brand text `Northstar Lab`
and tagline `Signals made clear`. Use a clear type-orbit construction with one
dominant orbit, a readable brand line, and a separate tagline. The request does
not ask for extended color, so use colorset1. Keep the brand readable at small
size, expose classes `logo-mark`, `orbit`, `brand-text`, and `tagline`, and use
pattern ID `d3-logo-type-orbit`. Record route `logo`.""" + VISUAL_TAIL,
        contract={
            "schemaVersion": 1,
            "taskId": "dev-standard-orbit-logo",
            "route": "logo",
            "colorset": "colorset1",
            "requireExtended": False,
            "expectedPatternId": "d3-logo-type-orbit",
            "requiredTerms": ["Northstar Lab", "Signals made clear"],
            "orderedTerms": ["Northstar Lab", "Signals made clear"],
            "tagMinimums": {"svg": 1, "title": 1, "desc": 1, "circle": 1, "text": 2},
            "classMinimums": {"logo-mark": 1, "orbit": 1, "brand-text": 1, "tagline": 1},
            "requiredIds": ["northstar-logo"],
            "requiredAttributes": {"data-logo-pattern": "d3-logo-type-orbit"},
            "requiresAnimation": False,
            "requiresInteraction": False,
            "visualPalette": visual_profile("colorset1", ["primary"]),
        },
    ),
    TaskSpec(
        split="validation",
        task_id="val-radial-review-recomposition",
        instruction="""Recompose the source process `Intake → Review → Approve → Archive` into a
radial D3/SVG armature. Preserve all four nodes, all three directed links, and
the link weights in order: Intake→Review = 8, Review→Approve = 5,
Approve→Archive = 3. Use colorset1. The rendered source nodes must use class
`source-node`; links must use `source-link`. Expose source pattern ID
`d3-review-flow`, composition ID `radial`, and variant ID
`d3-composition-radial-review-flow` as data attributes. Use the variant ID as
the decision pattern ID and record route `recomposition`.""" + VISUAL_TAIL,
        contract={
            "schemaVersion": 1,
            "taskId": "val-radial-review-recomposition",
            "route": "recomposition",
            "colorset": "colorset1",
            "requireExtended": False,
            "expectedPatternId": "d3-composition-radial-review-flow",
            "requiredTerms": ["Intake", "Review", "Approve", "Archive", "8", "5", "3"],
            "orderedTerms": [],
            "tagMinimums": {"svg": 1, "title": 1, "desc": 1, "circle": 4, "path": 3, "text": 7},
            "classMinimums": {"source-node": 4, "source-link": 3},
            "requiredIds": ["review-recomposition"],
            "requiredAttributes": {
                "data-composition-id": "radial",
                "data-pattern-id": "d3-review-flow",
                "data-composition-pattern-id": "d3-composition-radial-review-flow",
            },
            "requiresAnimation": False,
            "requiresInteraction": False,
            "visualPalette": visual_profile("colorset1", ["primary"]),
        },
    ),
    TaskSpec(
        split="validation",
        task_id="val-composition-clearance-audit",
        instruction="""Evaluate this visible SVG artifact as `audit-target.svg`:

```svg
<svg id="audit-target" viewBox="0 0 400 220" role="img">
  <title>Queue latency topology</title>
  <desc>Three queues connected left to right.</desc>
  <path id="link-forward" d="M45 50 L185 50 L355 180" fill="none" stroke="#9e1b32"/>
  <circle id="node-hot" cx="45" cy="50" r="30" fill="#ffccd5"/>
  <circle id="node-mid" cx="185" cy="50" r="20" fill="#cfcfcf"/>
  <circle id="node-cold" cx="355" cy="180" r="18" fill="#e7e7e7"/>
  <text id="label-hot" x="45" y="50">critical queue</text>
  <text id="label-cold" x="398" y="184">archive queue</text>
</svg>
```

Identify selector-specific problems. The report must address the collision
between `#label-hot` and `#node-hot`, clipping risk at `#label-cold`, the unclear
reading path/direction of `#link-forward`, label clearance, balance, data
integrity, and implementation-contract checks. Start exactly with
`Artifact: audit-target.svg`, include `Overall composition score: <integer>/100`,
and include a `Validation` section. Use colorset1, pattern ID
`d3-composition-audit`, and route `evaluation`.""" + EVALUATION_TAIL,
        contract={
            "schemaVersion": 1,
            "taskId": "val-composition-clearance-audit",
            "route": "evaluation",
            "colorset": "colorset1",
            "expectedPatternId": "d3-composition-audit",
            "requiredTerms": [
                "Artifact: audit-target.svg", "#label-hot", "#node-hot", "#label-cold",
                "#link-forward", "label clearance", "reading path", "balance",
                "data integrity", "implementation contract", "Validation",
            ],
            "patterns": [r"Overall composition score:\s*\d{1,3}/100"],
        },
    ),
    TaskSpec(
        split="holdout",
        task_id="hold-standard-throughput-slope",
        instruction="""Create a D3 slopegraph comparing Q1 and Q2 throughput in `requests/s`.
Preserve these three series and values: Core 42→55, Edge 31→46, Mobile 27→39.
Keep the series order Core, Edge, Mobile; render exactly three `series` paths
and six `point` marks with direct endpoint labels. Use the standard colorset1
palette with red for the changing series and neutral structure. Include a short
D3 line/point reveal, pattern ID `d3-throughput-slopegraph`, route
`visualization`, and no extended colors.""" + VISUAL_TAIL,
        contract={
            "schemaVersion": 1,
            "taskId": "hold-standard-throughput-slope",
            "route": "visualization",
            "colorset": "colorset1",
            "requireExtended": False,
            "expectedPatternId": "d3-throughput-slopegraph",
            "requiredTerms": ["Core", "Edge", "Mobile", "Q1", "Q2", "42", "55", "31", "46", "27", "39", "requests/s"],
            "orderedTerms": ["Core", "Edge", "Mobile"],
            "tagMinimums": {"svg": 1, "title": 1, "desc": 1, "path": 3, "circle": 6, "text": 12},
            "classMinimums": {"series": 3, "point": 6},
            "requiredIds": ["throughput-slopegraph"],
            "requiredAttributes": {"data-chart-kind": "slopegraph"},
            "requiresAnimation": True,
            "requiresInteraction": False,
            "visualPalette": visual_profile("colorset1", ["primary"]),
        },
    ),
    TaskSpec(
        split="holdout",
        task_id="hold-extended-channel-flow",
        instruction="""Create a self-contained D3 flow view for request routing. I explicitly
want extended full-color styling. Render seven `flow-node` nodes: Web, Mobile,
Partner, Cache, Compute, Reject, and Total. Render nine `flow-link` paths with
these literal amounts: Web→Cache 30, Web→Compute 15, Web→Reject 3,
Mobile→Cache 18, Mobile→Compute 10, Mobile→Reject 4, Partner→Cache 7,
Partner→Compute 5, Partner→Reject 8. Show all names and values. Use colorset2
with blue channel nodes, orange Compute, green Cache, and purple/red Reject;
animate link flow with D3 while preserving a truthful final state. Use pattern
ID `d3-channel-routing-flow` and route `visualization`.""" + VISUAL_TAIL,
        contract={
            "schemaVersion": 1,
            "taskId": "hold-extended-channel-flow",
            "route": "visualization",
            "colorset": "colorset2",
            "requireExtended": True,
            "expectedPatternId": "d3-channel-routing-flow",
            "requiredTerms": ["Web", "Mobile", "Partner", "Cache", "Compute", "Reject", "Total", "30", "15", "3", "18", "10", "4", "7", "5", "8"],
            "orderedTerms": [],
            "tagMinimums": {"svg": 1, "title": 1, "desc": 1, "path": 9, "rect": 7, "text": 16},
            "classMinimums": {"flow-node": 7, "flow-link": 9},
            "requiredIds": ["channel-flow"],
            "requiredAttributes": {"data-chart-kind": ["flow", "alluvial", "sankey"]},
            "requiresAnimation": True,
            "requiresInteraction": False,
            "visualPalette": visual_profile("colorset2", ["accent", "warning", "success", "special"], distinct=4),
        },
    ),
    TaskSpec(
        split="holdout",
        task_id="hold-extended-orbit-network-logo",
        instruction="""Create a D3/SVG seal for brand text `Atlas Forge` with tagline
`Build with signal`. I explicitly request the extended multicolor palette.
Use the canonical orbit-network mechanism with one central brand, at least
three `orbit-node` marks, at least three `orbit-link` connectors, separate
`brand-text` and `tagline` elements, and meaningful blue/orange/green/purple
roles. Keep text readable and the final mark deterministic. Use colorset2,
pattern ID `d3-logo-orbit-network`, and route `logo`.""" + VISUAL_TAIL,
        contract={
            "schemaVersion": 1,
            "taskId": "hold-extended-orbit-network-logo",
            "route": "logo",
            "colorset": "colorset2",
            "requireExtended": True,
            "expectedPatternId": "d3-logo-orbit-network",
            "requiredTerms": ["Atlas Forge", "Build with signal"],
            "orderedTerms": ["Atlas Forge", "Build with signal"],
            "tagMinimums": {"svg": 1, "title": 1, "desc": 1, "circle": 4, "path": 3, "text": 2},
            "classMinimums": {"logo-mark": 1, "orbit-node": 3, "orbit-link": 3, "brand-text": 1, "tagline": 1},
            "requiredIds": ["atlas-forge-logo"],
            "requiredAttributes": {"data-logo-pattern": "d3-logo-orbit-network"},
            "requiresAnimation": False,
            "requiresInteraction": False,
            "visualPalette": visual_profile("colorset2", ["accent", "warning", "success", "special"], distinct=4),
        },
    ),
    TaskSpec(
        split="holdout",
        task_id="hold-grid-release-recomposition",
        instruction="""Recompose the directed source chain Discover→Design→Build→Verify→Release
into a modular-grid D3/SVG armature. Preserve all five labels, all four links,
and their durations in order: 2d, 3d, 5d, 2d. Use colorset1. Render five
`source-node` marks and four `source-link` connectors. Expose source pattern ID
`d3-release-flow`, composition ID `modular-grid`, and variant ID
`d3-composition-modular-grid-release-flow` as data attributes. Use that variant
ID as the decision pattern ID and record route `recomposition`.""" + VISUAL_TAIL,
        contract={
            "schemaVersion": 1,
            "taskId": "hold-grid-release-recomposition",
            "route": "recomposition",
            "colorset": "colorset1",
            "requireExtended": False,
            "expectedPatternId": "d3-composition-modular-grid-release-flow",
            "requiredTerms": ["Discover", "Design", "Build", "Verify", "Release", "2d", "3d", "5d"],
            "orderedTerms": ["Discover", "Design", "Build", "Verify", "Release"],
            "tagMinimums": {"svg": 1, "title": 1, "desc": 1, "rect": 5, "path": 4, "text": 9},
            "classMinimums": {"source-node": 5, "source-link": 4},
            "requiredIds": ["release-recomposition"],
            "requiredAttributes": {
                "data-composition-id": "modular-grid",
                "data-pattern-id": "d3-release-flow",
                "data-composition-pattern-id": "d3-composition-modular-grid-release-flow",
            },
            "requiresAnimation": False,
            "requiresInteraction": False,
            "visualPalette": visual_profile("colorset1", ["primary"]),
        },
    ),
    TaskSpec(
        split="holdout",
        task_id="hold-label-lane-composition-audit",
        instruction="""Evaluate this visible SVG artifact as `latency-lanes.svg`:

```svg
<svg id="latency-lanes" viewBox="0 0 420 240" role="img">
  <title>Latency percentiles</title>
  <desc>Three percentile lines with a right-side legend.</desc>
  <path id="series-p50" d="M20 170 L210 150 L390 130" fill="none" stroke="#333e48"/>
  <path id="series-p95" d="M20 115 L210 75 L390 35" fill="none" stroke="#9e1b32"/>
  <text id="label-p95" x="210" y="75">p95 critical 480 ms</text>
  <text id="legend-critical" x="385" y="238">critical threshold</text>
  <line id="leader-p95" x1="210" y1="75" x2="210" y2="75" stroke="#9e1b32"/>
</svg>
```

Identify selector-specific problems. Address the occlusion of `#label-p95` over
`#series-p95`, clipped `#legend-critical`, zero-length `#leader-p95`, label-lane
clearance, reading path, balance, data integrity, and implementation-contract
checks. Start exactly with `Artifact: latency-lanes.svg`, include
`Overall composition score: <integer>/100`, and include a `Validation` section.
Use colorset1, pattern ID `d3-composition-audit`, and route `evaluation`.""" + EVALUATION_TAIL,
        contract={
            "schemaVersion": 1,
            "taskId": "hold-label-lane-composition-audit",
            "route": "evaluation",
            "colorset": "colorset1",
            "expectedPatternId": "d3-composition-audit",
            "requiredTerms": [
                "Artifact: latency-lanes.svg", "#label-p95", "#series-p95",
                "#legend-critical", "#leader-p95", "label-lane", "reading path",
                "balance", "data integrity", "implementation contract", "Validation",
            ],
            "patterns": [r"Overall composition score:\s*\d{1,3}/100"],
        },
    ),
)


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def public_contract(contract: dict[str, Any]) -> dict[str, Any]:
    """Return every verifier-enforced literal and structural requirement."""
    disclosed = {
        field: contract[field]
        for field in PUBLIC_CONTRACT_FIELDS
        if field in contract
    }
    if "visualPalette" in contract:
        disclosed["paintContract"] = {
            "literalActiveColorsetTokensOnly": True,
            "forbidFunctionalColorSyntax": True,
            "requireExtendedToken": bool(contract.get("requireExtended")),
            "requiredGroups": contract["visualPalette"]["requiredGroups"],
            "minDistinctVisibleColors": contract["visualPalette"]["minDistinctColors"],
            "requireVisiblePaletteInfluence": True,
        }
    return disclosed


def render_instruction(spec: TaskSpec) -> str:
    """Make verifier-visible requirements observable to the evaluated agent."""
    disclosed = json.dumps(public_contract(spec.contract), indent=2, sort_keys=True)
    return (
        spec.instruction.strip()
        + "\n\n"
        + PUBLIC_CONTRACT_MARKER
        + "\n\n"
        + PUBLIC_CONTRACT_SEMANTICS
        + "\n\n```json\n"
        + disclosed
        + "\n```\n"
    )


def tree_digest(root: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(item for item in root.rglob("*") if item.is_file()):
        relative = path.relative_to(root).as_posix()
        payload = path.read_bytes()
        digest.update(relative.encode("utf-8"))
        digest.update(b"\0")
        digest.update(str(len(payload)).encode("ascii"))
        digest.update(b"\0")
        digest.update(hashlib.sha256(payload).digest())
    return digest.hexdigest()


def validate_specs() -> dict[str, Any]:
    expected_counts = {"development": 3, "validation": 2, "holdout": 5}
    counts = Counter(spec.split for spec in TASKS)
    if dict(counts) != expected_counts:
        raise ValueError(f"Unexpected split counts: {dict(counts)}")
    task_ids = [spec.task_id for spec in TASKS]
    if len(task_ids) != len(set(task_ids)):
        raise ValueError("Task IDs must be unique")
    if any(not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", task_id) for task_id in task_ids):
        raise ValueError("Task IDs must be lowercase hyphen-case")
    fingerprints = []
    for spec in TASKS:
        if spec.contract.get("taskId") != spec.task_id:
            raise ValueError(f"Contract taskId mismatch: {spec.task_id}")
        if spec.contract.get("route") not in {"visualization", "logo", "recomposition", "evaluation"}:
            raise ValueError(f"Unknown route: {spec.task_id}")
        if spec.contract.get("colorset") not in {"colorset1", "colorset2"}:
            raise ValueError(f"Unknown colorset: {spec.task_id}")
        fingerprint = sha256_bytes(
            (spec.instruction + "\0" + json.dumps(spec.contract, sort_keys=True)).encode("utf-8")
        )
        fingerprints.append(fingerprint)
    if len(fingerprints) != len(set(fingerprints)):
        raise ValueError("Task content must be disjoint")
    holdout_routes = {spec.contract["route"] for spec in TASKS if spec.split == "holdout"}
    if holdout_routes != {"visualization", "logo", "recomposition", "evaluation"}:
        raise ValueError(f"Holdout route coverage is incomplete: {sorted(holdout_routes)}")
    visible_routes = {spec.contract["route"] for spec in TASKS if spec.split != "holdout"}
    if visible_routes != holdout_routes:
        raise ValueError("Optimizer-visible and holdout route coverage must match")
    return {
        "splitCounts": expected_counts,
        "colorsetCounts": dict(Counter(spec.contract["colorset"] for spec in TASKS)),
        "routeCounts": dict(Counter(spec.contract["route"] for spec in TASKS)),
        "taskCount": len(TASKS),
    }


def write_task(root: Path, spec: TaskSpec, helper_root: Path) -> None:
    task_root = root / spec.split / spec.task_id
    (task_root / "environment").mkdir(parents=True)
    (task_root / "tests").mkdir(parents=True)
    (task_root / "instruction.md").write_text(
        render_instruction(spec), encoding="utf-8", newline="\n"
    )
    (task_root / "task.toml").write_text(TASK_TOML, encoding="utf-8", newline="\n")
    (task_root / "environment" / ".gitkeep").write_text("", encoding="utf-8")
    (task_root / "tests" / "contract.json").write_text(
        json.dumps(spec.contract, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n"
    )
    (task_root / "tests" / "test.sh").write_text(TEST_SH, encoding="utf-8", newline="\n")
    for filename in ("verify_task.py", "visual_palette.py", "render_browser.js"):
        shutil.copy2(helper_root / filename, task_root / "tests" / filename)


def quoted(value: str | Path) -> str:
    return json.dumps(str(value).replace("\\", "/"))


def write_job_config(
    output_root: Path,
    repo_root: Path,
    split: str,
    run_id: str,
    attempts: int,
    concurrency: int,
    model: str,
    skill_source: Path | None = None,
    config_path: Path | None = None,
    job_name: str | None = None,
) -> Path:
    config_path = config_path or output_root / f"{split}-job.yaml"
    job_name = job_name or f"{run_id}-{split}-spark"
    skill_source = (skill_source or repo_root / "skills" / "d3").resolve()
    config = f"""job_name: {quoted(job_name)}
jobs_dir: {quoted(output_root / 'jobs')}
n_attempts: {attempts}
n_concurrent_trials: {concurrency}
quiet: true
retry:
  max_retries: 0
environment:
  import_path: "evaluations.d3.harbor_wsl_environment:WorkspaceWSLEnvironment"
  delete: true
  cpu_enforcement_policy: ignore
  memory_enforcement_policy: ignore
  kwargs:
    shared_cache_dir: {quoted(repo_root / 'evaluations' / 'runs' / 'harbor-shared-cache')}
    skill_source_dir: {quoted(skill_source)}
agents:
  - name: codex
    model_name: {quoted(model)}
    skills:
      - {quoted(skill_source)}
    kwargs:
      version: "0.147.0"
      reasoning_effort: "medium"
      reasoning_summary: concise
      web_search: disabled
    env:
      CODEX_FORCE_AUTH_JSON: "true"
datasets:
  - path: {quoted(output_root / split)}
artifacts:
  - source: "/app/deliverables"
    destination: "deliverables"
"""
    config_path.write_text(config, encoding="utf-8", newline="\n")
    return config_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--run-id", required=True, help="Stable lowercase run identifier.")
    parser.add_argument("--attempts", type=int, default=3)
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
    stats = validate_specs()
    for spec in TASKS:
        write_task(output_root, spec, helper_root)
    configs = {
        split: str(
            write_job_config(
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
        split: tree_digest(output_root / split)
        for split in ("development", "validation", "holdout")
    }
    manifest = {
        "schemaVersion": 2,
        "runId": args.run_id,
        "model": args.model,
        "attempts": args.attempts,
        "concurrency": args.concurrency,
        "stats": stats,
        "splitDigests": split_digests,
        "jobConfigs": configs,
        "holdoutPolicy": "Register before execution; do not execute or inspect until the selected skill bundle is digest-bound and holdout is released once.",
    }
    (output_root / "dataset-manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n"
    )
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
