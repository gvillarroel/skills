#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


COLORS = {
    "primaryRed": "#9e1b32",
    "darkRed": "#6d1222",
    "statusRed": "#e8002a",
    "neutralText": "#333e48",
    "white": "#ffffff",
    "gray100": "#e7e7e7",
    "gray200": "#cfcfcf",
    "gray400": "#9c9c9c",
    "gray600": "#696969",
    "gray800": "#363636",
    "gray900": "#1c1c1c",
}

HELPER_SCAFFOLDS = {
    "skill-tree",
    "skill-tree-route",
    "systems-flow",
    "state-machine",
    "comparison-matrix",
    "causal-loop",
    "phase-timeline",
    "metric-dashboard",
    "dependency-map",
    "sequence-trace",
    "sankey-flow",
    "swimlane-handoff",
    "risk-bowtie",
    "scenario-tree",
    "evidence-ladder",
    "layered-architecture",
    "data-lineage",
}


CATALOG: list[dict[str, Any]] = [
    {
        "id": "circuit-signal-traces",
        "family": "networks-routes",
        "scaffold": "dependency-map",
        "armature": "orthogonal circuit board",
        "keywords": ["mcp", "tool", "plugin", "connector", "server", "client", "handshake", "reroute", "fault", "permission"],
        "marks": ["orthogonal traces", "port blocks", "signal packets", "fault gates"],
        "motions": ["signal trace", "handshake pulse", "fault isolation", "fallback reroute"],
        "d3PatternIds": ["d3-pattern-circuit-signal-traces"],
    },
    {
        "id": "critical-queue-backpressure",
        "family": "systems-resilience",
        "scaffold": "systems-flow",
        "armature": "bounded queue wall",
        "keywords": ["queue", "backpressure", "retry", "dead-letter", "worker", "throttle", "overload", "harness", "agent"],
        "marks": ["queue slots", "producer gates", "consumer lanes", "shed path"],
        "motions": ["queue fill", "throttle gate", "load shed", "recovery drain"],
        "d3PatternIds": ["d3-pattern-critical-queue-backpressure"],
    },
    {
        "id": "critical-cache-stampede",
        "family": "systems-resilience",
        "scaffold": "systems-flow",
        "armature": "origin shield map",
        "keywords": ["cache", "stampede", "hot key", "single-flight", "stale", "origin", "shield", "ttl"],
        "marks": ["fan-out requests", "single-flight lock", "stale path", "origin shield"],
        "motions": ["miss storm", "lock collapse", "stale response", "origin recovery"],
        "d3PatternIds": ["d3-pattern-critical-cache-stampede"],
    },
    {
        "id": "critical-dependency-blast-radius",
        "family": "networks-routes",
        "scaffold": "dependency-map",
        "armature": "dependency ring map",
        "keywords": ["dependency", "integration", "blast radius", "failover", "impact", "risk", "cutover", "fallback"],
        "marks": ["dependency rings", "impact surfaces", "critical links", "failover routes"],
        "motions": ["blast wave", "impact reveal", "critical route draw", "failover switch"],
        "d3PatternIds": ["d3-pattern-critical-dependency-blast-radius"],
    },
    {
        "id": "critical-bowtie-barrier",
        "family": "risk-evidence",
        "scaffold": "risk-bowtie",
        "armature": "balanced bowtie",
        "keywords": ["guardrail", "risk", "barrier", "threat", "mitigation", "policy", "control", "safety"],
        "marks": ["threat lanes", "preventive barriers", "top event", "mitigative barriers"],
        "motions": ["threat converge", "barrier activation", "top event lock", "mitigation route"],
        "d3PatternIds": ["d3-pattern-critical-bowtie-barrier"],
    },
    {
        "id": "moe-router-capacity",
        "family": "ai-token-mechanics",
        "scaffold": "systems-flow",
        "armature": "expert capacity grid",
        "keywords": ["moe", "expert", "router", "capacity", "overflow", "dropped token", "model"],
        "marks": ["expert slots", "router gates", "capacity bars", "overflow bins"],
        "motions": ["route dispatch", "capacity fill", "overflow shed"],
        "d3PatternIds": ["d3-pattern-moe-router-capacity"],
    },
    {
        "id": "document-token-extraction-buckets",
        "family": "risk-evidence",
        "scaffold": "evidence-ladder",
        "armature": "source-to-buckets grid",
        "keywords": ["document", "grounding", "source", "evidence", "extract", "quality", "citation", "retrieval"],
        "marks": ["source blocks", "scan lanes", "evidence buckets", "quality totals"],
        "motions": ["source scan", "block extraction", "bucket split", "quality tally"],
        "d3PatternIds": ["d3-pattern-document-token-extraction-buckets"],
    },
    {
        "id": "adjacency-matrix",
        "family": "networks-routes",
        "scaffold": "dependency-map",
        "armature": "matrix wall",
        "keywords": ["relationship", "pairwise", "matrix", "dependency", "tool", "permission", "connector", "integration"],
        "marks": ["matrix cells", "row bands", "column bands", "active intersections"],
        "motions": ["cell activation", "row sweep", "column compare"],
        "d3PatternIds": ["d3-pattern-adjacency-matrix"],
    },
    {
        "id": "attention-matrix-tiles",
        "family": "ai-token-mechanics",
        "scaffold": "comparison-matrix",
        "armature": "matrix wall",
        "keywords": ["attention", "token", "transformer", "probability", "logprob", "model", "llm", "context"],
        "marks": ["matrix cells", "head bands", "mask lanes", "activation blocks"],
        "motions": ["cell activation", "head sweep", "mask reveal"],
        "d3PatternIds": ["d3-pattern-attention-matrix-tiles"],
    },
    {
        "id": "token-boxes-to-context-window",
        "family": "ai-token-mechanics",
        "scaffold": "data-lineage",
        "armature": "flow spine",
        "keywords": ["token", "context", "window", "prompt", "sequence", "generation"],
        "marks": ["token groups", "address slots", "context cells", "append path"],
        "motions": ["token split", "slot fill", "append loop"],
        "d3PatternIds": ["d3-pattern-token-boxes-to-context-window", "d3-pattern-context-window-matrix"],
    },
    {
        "id": "qkv-projection-flow",
        "family": "ai-token-mechanics",
        "scaffold": "systems-flow",
        "armature": "flow spine",
        "keywords": ["query", "key", "value", "attention", "transformer", "projection"],
        "marks": ["projection lanes", "three streams", "join nodes"],
        "motions": ["lane split", "route draw", "stream merge"],
    },
    {
        "id": "matmul-tile-accumulation",
        "family": "ai-token-mechanics",
        "scaffold": "metric-dashboard",
        "armature": "matrix wall",
        "keywords": ["gpu", "parameter", "compute", "matrix", "parallel", "inference", "training"],
        "marks": ["compute tiles", "partial sums", "output cells"],
        "motions": ["tile sweep", "partial accumulation", "output assembly"],
        "d3PatternIds": ["d3-pattern-matmul-tile-accumulation"],
    },
    {
        "id": "kv-cache-growth",
        "family": "ai-token-mechanics",
        "scaffold": "data-lineage",
        "armature": "matrix wall",
        "keywords": ["cache", "kv", "memory", "context", "inference", "latency"],
        "marks": ["cache pages", "append slots", "eviction bands"],
        "motions": ["page allocation", "cache append", "pressure shift"],
        "d3PatternIds": ["d3-pattern-paged-kv-cache"],
    },
    {
        "id": "flow-tokens",
        "family": "flow-and-handoff",
        "scaffold": "systems-flow",
        "armature": "flow spine",
        "keywords": ["flow", "pipeline", "agent", "tool", "workflow", "request", "action", "handoff", "mcp"],
        "marks": ["packets", "route rails", "branch gates", "state sinks"],
        "motions": ["packet route", "branch split", "feedback loop"],
    },
    {
        "id": "sankey-flow",
        "family": "flow-and-handoff",
        "scaffold": "sankey-flow",
        "armature": "flow spine",
        "keywords": ["billing", "cost", "conversion", "allocation", "credits", "tokens in", "tokens out", "pricing"],
        "marks": ["weighted bands", "loss branch", "merge node", "output meter"],
        "motions": ["band split", "loss reveal", "bottleneck pulse"],
        "d3PatternIds": ["d3-pattern-sankey", "d3-pattern-parallel-sets"],
    },
    {
        "id": "swimlane-handoff",
        "family": "flow-and-handoff",
        "scaffold": "swimlane-handoff",
        "armature": "lane grid",
        "keywords": ["team", "owner", "approval", "handoff", "harness", "hook", "plugin", "workflow", "agent"],
        "marks": ["owner lanes", "handoff packet", "approval gate", "rework loop"],
        "motions": ["lane handoff", "sla pressure", "escalation branch"],
    },
    {
        "id": "metric-dashboard",
        "family": "dense-operations",
        "scaffold": "metric-dashboard",
        "armature": "masonry wall",
        "keywords": ["metric", "slo", "billing", "cost", "latency", "observability", "threshold", "evaluation"],
        "marks": ["metric bands", "threshold rails", "forecast cells", "decision gate"],
        "motions": ["trend draw", "threshold crossing", "forecast reveal"],
    },
    {
        "id": "inline-bar-table",
        "family": "dense-operations",
        "scaffold": "comparison-matrix",
        "armature": "matrix wall",
        "keywords": ["compare", "cost", "pricing", "plan", "alternative", "model", "credits", "subscription"],
        "marks": ["rows", "embedded bars", "rank cells", "selected row"],
        "motions": ["row reveal", "bar fill", "rank reorder"],
    },
    {
        "id": "dependency-map",
        "family": "networks-routes",
        "scaffold": "dependency-map",
        "armature": "cluster map",
        "keywords": ["dependency", "mcp", "integration", "plugin", "connector", "architecture", "tool", "permission"],
        "marks": ["cluster surfaces", "dependency edges", "risk route", "fallback path"],
        "motions": ["edge draw", "bottleneck reveal", "fallback route"],
    },
    {
        "id": "sequence-trace",
        "family": "networks-routes",
        "scaffold": "sequence-trace",
        "armature": "lane grid",
        "keywords": ["trace", "observability", "latency", "span", "request", "retry", "fallback", "tool call"],
        "marks": ["service lanes", "span bars", "critical path", "retry branch"],
        "motions": ["span growth", "critical-path highlight", "response return"],
    },
    {
        "id": "layered-architecture",
        "family": "networks-routes",
        "scaffold": "layered-architecture",
        "armature": "layer stack",
        "keywords": ["architecture", "instruction", "layer", "policy", "permission", "governance", "harness", "agent"],
        "marks": ["layers", "cross-cutting rail", "failure path", "rollout gate"],
        "motions": ["layer activation", "cross-cut draw", "failure route"],
    },
    {
        "id": "risk-bowtie",
        "family": "risk-evidence",
        "scaffold": "risk-bowtie",
        "armature": "balanced bowtie",
        "keywords": ["risk", "guardrail", "safety", "policy", "permission", "security", "governance", "failure"],
        "marks": ["threats", "barriers", "top event", "consequences"],
        "motions": ["barrier activation", "degraded control", "repair action"],
    },
    {
        "id": "evidence-ladder",
        "family": "risk-evidence",
        "scaffold": "evidence-ladder",
        "armature": "vertical ladder",
        "keywords": ["evaluation", "evidence", "judge", "benchmark", "pass", "quality", "claim", "confidence"],
        "marks": ["claim tier", "evidence rows", "counterevidence", "confidence rail"],
        "motions": ["tier reveal", "counterweight", "confidence rise"],
    },
    {
        "id": "scenario-tree",
        "family": "risk-evidence",
        "scaffold": "scenario-tree",
        "armature": "branching tree",
        "keywords": ["scenario", "decision", "alternative", "probability", "choice", "tradeoff", "future"],
        "marks": ["decision root", "branches", "probability cells", "selected route"],
        "motions": ["branch growth", "risk/upside split", "decision gate"],
    },
    {
        "id": "masonry-wall",
        "family": "modular-composition",
        "scaffold": "comparison-matrix",
        "armature": "masonry wall",
        "keywords": ["module", "skill", "plugin", "feature", "alternative", "concept", "collection", "dashboard"],
        "marks": ["different-size modules", "flush gutters", "role surfaces", "state cells"],
        "motions": ["block construction", "tile morph", "surface wipe"],
    },
]


FALLBACK_IDS = [
    "flow-tokens",
    "metric-dashboard",
    "dependency-map",
    "masonry-wall",
    "inline-bar-table",
    "risk-bowtie",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Plan a Metro visual-density pattern mix from prompt text.")
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--prompt-file", type=Path, help="Prompt, script, or topic source file.")
    source.add_argument("--text", help="Prompt or topic text.")
    parser.add_argument("--output", type=Path, help="JSON report path. Prints JSON when omitted.")
    parser.add_argument("--min-patterns", type=int, default=6)
    parser.add_argument("--min-patterns-used", type=int, default=3)
    parser.add_argument("--min-functional-zones", type=int, default=5)
    parser.add_argument("--min-motion-systems", type=int, default=4)
    parser.add_argument("--min-camera-events", type=int, default=3)
    parser.add_argument("--require-anchor", action="append", default=[], help="Literal source anchor expected in the input or selected output.")
    return parser.parse_args()


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower()).strip()


def requires_masonry_contract(normalized: str) -> bool:
    return any(
        phrase in normalized
        for phrase in (
            "masonry",
            "metro minimal",
            "megacanvas",
            "modular map",
            "not following the design",
            "not aligned with the design",
            "design rejection",
            "no esta siguiendo",
            "no está siguiendo",
            "no sigue",
            "no usan la estetica",
            "no usas la estética",
            "cajas",
            "sin padding",
            "no padding",
            "niveles de grises",
        )
    )


def read_source(args: argparse.Namespace) -> tuple[str, str]:
    if args.prompt_file:
        return args.prompt_file.as_posix(), args.prompt_file.read_text(encoding="utf-8")
    return "inline-text", str(args.text or "")


def score_item(item: dict[str, Any], normalized: str) -> int:
    score = 0
    for keyword in item["keywords"]:
        key = str(keyword).lower()
        if key in normalized:
            score += 4 if " " in key else 2
    family = str(item["family"])
    if family == "ai-token-mechanics" and any(word in normalized for word in ("llm", "model", "token", "context", "gpu")):
        score += 2
    if family == "risk-evidence" and any(word in normalized for word in ("guardrail", "policy", "risk", "evaluation")):
        score += 2
    if family == "flow-and-handoff" and any(word in normalized for word in ("agent", "tool", "workflow", "mcp")):
        score += 2
    return score


def select_patterns(text: str, minimum: int) -> list[dict[str, Any]]:
    normalized = normalize(text)
    scored = sorted(
        ((score_item(item, normalized), index, item) for index, item in enumerate(CATALOG)),
        key=lambda entry: (-entry[0], entry[1]),
    )
    selected: list[dict[str, Any]] = [item for score, _, item in scored if score > 0]
    by_id = {item["id"]: item for item in CATALOG}
    needs_masonry = requires_masonry_contract(normalized)
    if needs_masonry:
        selected = [item for item in selected if item["id"] != "masonry-wall"]
        selected.insert(min(3, len(selected)), by_id["masonry-wall"])
    for pattern_id in FALLBACK_IDS:
        if len(selected) >= minimum:
            break
        item = by_id[pattern_id]
        if item not in selected:
            selected.append(item)
    return selected[: max(minimum, 6)]


def compact_pattern(item: dict[str, Any]) -> dict[str, Any]:
    compact = {
        "id": item["id"],
        "family": item["family"],
        "scaffold": item["scaffold"],
        "armature": item["armature"],
        "marks": item["marks"],
        "motions": item["motions"],
    }
    if item.get("d3PatternIds"):
        compact["d3PatternIds"] = item["d3PatternIds"]
    return compact


def anti_pattern_risks(text: str) -> list[dict[str, Any]]:
    normalized = normalize(text)
    risks = [
        {
            "id": "boxes-plus-labels",
            "risk": "Output reads as labeled boxes instead of an information-dense visual system.",
            "avoidWith": ["functional zones", "encoded marks", "semantic motion systems"],
        },
        {
            "id": "title-led-slide",
            "risk": "Frame depends on a title, caption, or paragraph band to explain the concept.",
            "avoidWith": ["local object labels only", "mute-test mechanics", "camera exploration"],
        },
        {
            "id": "padded-rounded-cards",
            "risk": "Metro surface uses padded cards, pills, rounded corners, or inset panels.",
            "avoidWith": ["0-radius geometry", "zero internal padding", "external gutters"],
        },
        {
            "id": "weak-gray-hierarchy",
            "risk": "One gray surface dominates and hierarchy is not encoded with distinct gray levels.",
            "avoidWith": ["gray100/200/400/600/800/900 roles", "area-weighted hierarchy"],
        },
        {
            "id": "generic-transition",
            "risk": "Transitions are fades or pulses rather than camera, block, mask, or tile movement.",
            "avoidWith": ["zoom/pan", "tile morph", "masked reframe", "surface wipe"],
        },
    ]
    if "dashboard" in normalized and "not a dashboard" not in normalized:
        risks.append(
            {
                "id": "static-dashboard",
                "risk": "A dashboard cue can become static KPI cards without mechanism progression.",
                "avoidWith": ["threshold crossing", "trend draw", "forecast reveal", "decision gate"],
            }
        )
    return risks


def zone_for(index: int, item: dict[str, Any]) -> dict[str, Any]:
    roles = ["overview", "primary mechanism", "secondary metric", "risk or exception", "evidence or detail", "transition target"]
    gray_roles = ["gray100 background", "gray200 surface", "gray400 module", "gray600 connector", "gray800 active mark", "gray900 high emphasis"]
    return {
        "id": f"zone-{index + 1:02d}",
        "role": roles[index % len(roles)],
        "pattern": item["id"],
        "armature": item["armature"],
        "visualMarks": item["marks"][:3],
        "motion": item["motions"][0],
        "grayRole": gray_roles[index % len(gray_roles)],
        "boxModel": {"cornerRadius": 0, "internalPaddingPx": 0, "gridPx": 4},
    }


def transition_for(index: int, item: dict[str, Any]) -> dict[str, Any]:
    transition_types = ["camera-pan", "tile-morph", "masked-reframe", "expanding-block", "surface-wipe"]
    motion_text = " ".join(str(motion).lower() for motion in item["motions"])
    if item["id"] == "masonry-wall" or item["armature"] == "masonry wall":
        transition_type = "masonry-construction"
    elif "surface wipe" in motion_text:
        transition_type = "surface-wipe"
    elif "tile morph" in motion_text:
        transition_type = "tile-morph"
    elif "mask" in motion_text:
        transition_type = "masked-reframe"
    elif "block" in motion_text:
        transition_type = "expanding-block"
    else:
        transition_type = transition_types[index % len(transition_types)]
    return {
        "id": f"transition-{index + 1:02d}",
        "type": transition_type,
        "fromZone": f"zone-{index + 1:02d}",
        "toZone": f"zone-{index + 2:02d}",
        "preservedGeometry": item["armature"],
        "stateChange": item["motions"][0],
    }


def explicit_helper_scaffold(text: str) -> str | None:
    match = re.search(r"Use the `([^`]+)` scaffold", text, flags=re.IGNORECASE)
    if not match:
        return None
    scaffold = str(match.group(1)).strip().lower()
    return scaffold if scaffold in HELPER_SCAFFOLDS else None


def build_report(source_name: str, text: str, args: argparse.Namespace) -> dict[str, Any]:
    selected = select_patterns(text, args.min_patterns)
    used = selected[: max(args.min_patterns_used, 3)]
    zones = [zone_for(index, item) for index, item in enumerate(selected[: max(args.min_functional_zones, 5)])]
    camera_path = [
        {"time": "early", "event": "overview-to-primary", "motion": "zoom-in", "targetZone": "zone-02"},
        {"time": "middle", "event": "primary-to-secondary", "motion": "pan", "targetZone": "zone-03"},
        {"time": "late", "event": "exception-or-evidence", "motion": "masked-reframe", "targetZone": "zone-04"},
        {"time": "final", "event": "system-overview", "motion": "zoom-out", "targetZone": "zone-01"},
    ]
    semantic_motion = []
    for item in selected[: max(args.min_motion_systems, 4)]:
        semantic_motion.append(
            {
                "pattern": item["id"],
                "system": item["motions"][0],
                "meaning": f"{item['family']} state change",
                "nonTextEvidence": item["marks"][:2],
            }
        )
    transition_items = list(selected[:3])
    masonry_item = next((item for item in selected if item["id"] == "masonry-wall"), None)
    if masonry_item is not None and all(item["id"] != "masonry-wall" for item in transition_items):
        transition_items[-1] = masonry_item
    transitions = [transition_for(index, item) for index, item in enumerate(transition_items)]
    selected_ids = [str(item["id"]) for item in selected]
    used_ids = [str(item["id"]) for item in used]
    reusable_d3_ids = list(
        dict.fromkeys(
            str(pattern_id)
            for item in selected
            for pattern_id in (item.get("d3PatternIds") or [])
            if pattern_id
        )
    )
    input_probe = normalize(text)
    masonry_required = requires_masonry_contract(input_probe)
    masonry_included = "masonry-wall" in selected_ids
    masonry_transition_included = any(transition.get("type") == "masonry-construction" for transition in transitions)
    output_probe = normalize(json.dumps({"patterns": selected_ids, "zones": zones}, ensure_ascii=True))

    findings: list[dict[str, Any]] = []
    if len(selected_ids) < args.min_patterns:
        findings.append({"code": "too-few-patterns", "minimum": args.min_patterns, "actual": len(selected_ids)})
    if len(used_ids) < args.min_patterns_used:
        findings.append({"code": "too-few-used-patterns", "minimum": args.min_patterns_used, "actual": len(used_ids)})
    if len(zones) < args.min_functional_zones:
        findings.append({"code": "too-few-functional-zones", "minimum": args.min_functional_zones, "actual": len(zones)})
    if len(semantic_motion) < args.min_motion_systems:
        findings.append({"code": "too-few-motion-systems", "minimum": args.min_motion_systems, "actual": len(semantic_motion)})
    if len(camera_path) < args.min_camera_events:
        findings.append({"code": "too-few-camera-events", "minimum": args.min_camera_events, "actual": len(camera_path)})
    for anchor in args.require_anchor:
        if normalize(anchor) not in input_probe and normalize(anchor) not in output_probe:
            findings.append({"code": "missing-required-anchor", "anchor": anchor})

    primary = selected[0]
    secondary = selected[1] if len(selected) > 1 else selected[0]
    support = selected[2:6]
    planner_scaffold = str(primary["scaffold"])
    helper_scaffold = explicit_helper_scaffold(text) or planner_scaffold
    helper_reason = "Prompt explicitly requested this helper scaffold." if helper_scaffold != planner_scaffold else "Planner selected this helper scaffold from the strongest density pattern."
    return {
        "passed": not findings,
        "source": source_name,
        "selected": {
            "helperPattern": helper_scaffold,
            "primaryPattern": primary["id"],
            "secondaryPattern": secondary["id"],
            "supportPatterns": [item["id"] for item in support],
            "suggestedScaffoldPattern": planner_scaffold,
            "armature": primary["armature"],
            "selectionReason": "Use the helper scaffold for first runnable output, then apply the density patterns, zones, camera path, and transition contracts as the design brief.",
            "helperSelectionReason": helper_reason,
        },
        "patternCounts": {
            "patternIdsNamed": len(selected_ids),
            "patternsUsed": len(used_ids),
            "functionalZones": len(zones),
            "semanticMotionSystems": len(semantic_motion),
            "cameraEvents": len(camera_path),
        },
        "patternIdsNamed": selected_ids,
        "reusableD3PatternIds": reusable_d3_ids,
        "patternsUsedInBeats": used_ids,
        "patternDetails": [compact_pattern(item) for item in selected],
        "functionalZones": zones,
        "semanticMotionSystems": semantic_motion,
        "cameraPath": camera_path,
        "transitionContracts": transitions,
        "masonryContract": {
            "required": masonry_required,
            "patternIncluded": masonry_included,
            "transitionIncluded": masonry_transition_included,
        },
        "antiPatternRisks": anti_pattern_risks(text),
        "textBudget": {
            "visibleTextRole": "functional-labels-only",
            "forbidden": ["title bands", "subtitles", "captions", "paragraph explanations", "date bands"],
            "muteTest": "Viewer should infer the mechanism from marks, state changes, camera movement, and gray hierarchy before reading labels.",
        },
        "metroConstraints": {
            "colorset": "colorset1",
            "palette": COLORS,
            "cornerRadius": 0,
            "internalBoxPaddingPx": 0,
            "gridPx": 4,
            "minimumGrayLevels": 4,
            "useColorset2OnlyWithReason": True,
        },
        "wrapperHints": {
            "scaffoldPattern": helper_scaffold,
            "stateEvidence": ["visibleMechanismCount", "cameraX", "cameraY", "cameraMoving"],
            "auditReports": [
                "render-state-check.json",
                "metro-style-audit.json",
                "metro-composition-audit.json",
                "metro-rendered-frame-audit.json",
                "metro-mute-test-audit.json",
                "metro-video-composition-audit.json",
                "metro-audit-suite.json",
                "metro-semantic-density-audit.json",
            ],
        },
        "findings": findings,
    }


def main() -> int:
    args = parse_args()
    source_name, text = read_source(args)
    report = build_report(source_name, text, args)
    rendered = json.dumps(report, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered)
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
