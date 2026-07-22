#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

from __future__ import annotations

import argparse
from fractions import Fraction
import json
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

from plan_metro_pattern_mix import build_report as build_metro_pattern_mix_report


PATTERN_MIX_SCRIPT = Path(__file__).with_name("plan_metro_pattern_mix.py")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Derive and run build_standalone_explainer.py from a prompt that lists exact video package paths."
    )
    parser.add_argument("--prompt", required=True, type=Path)
    parser.add_argument("--manifest", type=Path, help="Optional JSON report path.")
    parser.add_argument("--dry-run", action="store_true", help="Print derived command without running it.")
    parser.add_argument("--state-manifest", type=Path, help="Optional render-state checker JSON report path.")
    parser.add_argument("--state-expect", action="append", default=[], help="Forwarded KEY=VALUE expectation for check_html_render_state.py.")
    parser.add_argument("--state-expect-final", action="append", default=[], help="Forwarded final KEY=VALUE expectation for check_html_render_state.py.")
    parser.add_argument("--state-expect-contains", action="append", default=[], help="Forwarded KEY=VALUE containment expectation for check_html_render_state.py.")
    parser.add_argument("--state-expect-transition", action="append", default=[], help="Forwarded KEY=FROM->TO transition expectation for check_html_render_state.py.")
    parser.add_argument("--state-expect-monotonic", action="append", default=[], help="Forwarded KEY=MODE monotonic-state expectation for check_html_render_state.py.")
    parser.add_argument("--state-min-distinct", action="append", default=[], help="Forwarded KEY=COUNT distinct-state expectation for check_html_render_state.py.")
    parser.add_argument("--state-samples", type=int, default=6, help="Number of render-state samples when --state-manifest is used.")
    parser.add_argument("--metro-style-manifest", type=Path, help="Optional Metro tonal style audit JSON report path.")
    parser.add_argument("--metro-composition-manifest", type=Path, help="Optional Metro composition audit JSON report path.")
    parser.add_argument("--metro-rendered-frame-manifest", type=Path, help="Optional Metro rendered-frame audit JSON report path.")
    parser.add_argument("--metro-mute-test-manifest", type=Path, help="Optional Metro mute-test audit JSON report path.")
    parser.add_argument("--metro-audit-suite-manifest", type=Path, help="Optional Metro audit-suite JSON report path.")
    parser.add_argument("--metro-video-composition-manifest", type=Path, help="Optional encoded-MP4 Metro composition audit JSON report path.")
    return parser.parse_args()


def read_prompt(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(path)
    return path.read_text(encoding="utf-8")


def clean_value(value: str) -> str:
    return value.strip().strip("`").strip()


def clean_label_value(value: str) -> str:
    return clean_value(value).rstrip(".").strip()


def is_safe_workspace_path(value: str, *, marker: str | None = None) -> bool:
    normalized = value.strip().replace("\\", "/")
    if not normalized or normalized.startswith(("/", "//")) or re.match(r"^[A-Za-z]:/", normalized):
        return False
    if ".." in Path(normalized).parts:
        return False
    return marker is None or marker in normalized


def extract_label(text: str, label: str, default: str = "") -> str:
    match = re.search(rf"^{re.escape(label)}:\s*(.+?)\s*$", text, flags=re.MULTILINE | re.IGNORECASE)
    return clean_label_value(match.group(1)) if match else default


def extract_required_paths(text: str) -> list[str]:
    paths = []
    in_required_block = False
    for raw in text.splitlines():
        line = raw.strip()
        if re.match(r"Required exact .*outputs:", line, flags=re.IGNORECASE):
            in_required_block = True
            continue
        if in_required_block and line and not line.startswith("- "):
            break
        if not in_required_block or not line.startswith("- "):
            continue
        values = re.findall(r"`([^`]+)`", line) or [line[2:]]
        for value in values:
            value = value.strip().replace("\\", "/")
            if is_safe_workspace_path(value) and any(marker in value for marker in ("/source/", "/src/", "/artifacts/")):
                paths.append(value)
    return list(dict.fromkeys(paths))


def extract_manifest_path(text: str) -> Path | None:
    patterns = [
        r"(?:prompt-contract\s+build\s+report|wrapper\s+report|build\s+report).*?\bto\s+`([^`]+\.json)`",
        r"(?:prompt-contract\s+build\s+report|wrapper\s+report|build\s+report).*?\bat\s+`?([^\s`]+\.json)`?",
        r"`([^`]*prompt-contract-build\.json)`",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE | re.DOTALL)
        if match:
            value = clean_value(match.group(1)).replace("\\", "/")
            if is_safe_workspace_path(value, marker="/artifacts/"):
                return Path(value)
    return None


def extract_state_manifest_path(text: str) -> Path | None:
    patterns = [
        r"`([^`]*render-state[^`]*\.json)`",
        r"`([^`]*browser-state[^`]*\.json)`",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            value = clean_value(match.group(1)).replace("\\", "/")
            if is_safe_workspace_path(value, marker="/artifacts/"):
                return Path(value)
    return None


def extract_named_json_path(text: str, names: list[str]) -> Path | None:
    lowered_names = [re.escape(name) for name in names]
    name_pattern = "|".join(lowered_names)
    patterns = [
        rf"`([^`]*(?:{name_pattern})[^`]*\.json)`",
        rf"(?:{name_pattern}).*?\bto\s+`([^`]+\.json)`",
        rf"(?:{name_pattern}).*?\bat\s+`?([^\s`]+\.json)`?",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE | re.DOTALL)
        if match:
            value = clean_value(match.group(1)).replace("\\", "/")
            if is_safe_workspace_path(value, marker="/artifacts/"):
                return Path(value)
    return None


def derive_project_root(paths: list[str]) -> str:
    candidates = []
    for path in paths:
        for marker in ("/source/", "/src/", "/artifacts/"):
            if marker in path:
                candidates.append(path.split(marker, 1)[0])
                break
    unique = sorted(set(candidates))
    if len(unique) != 1:
        raise ValueError(f"Could not derive one project root from paths: {unique}")
    return unique[0]


def derive_output_id(paths: list[str]) -> str:
    mp4_paths = [
        path
        for path in paths
        if "/artifacts/video-renders/draft/videos/" in path and path.endswith(".mp4")
    ]
    if len(mp4_paths) != 1:
        raise ValueError(f"Expected one draft MP4 output path, got {mp4_paths}")
    return Path(mp4_paths[0]).stem


def extract_pattern(text: str) -> str:
    match = re.search(r"Use the `([^`]+)` scaffold", text, flags=re.IGNORECASE)
    if match:
        return clean_value(match.group(1))
    lowered = text.lower()
    if any(term in lowered for term in ("skill-tree-route", "skill tree route", "passive route", "passive tree route", "build route", "tree route", "pathing", "travel nodes", "respec checkpoint", "route planner", "route map")):
        return "skill-tree-route"
    if any(term in lowered for term in ("path of exile", "skill-tree", "skill tree", "keystone", "atlas")):
        return "skill-tree"
    if any(term in lowered for term in ("state-machine", "state machine", "lifecycle", "workflow state", "guarded transition", "rollback", "compensation", "terminal state")):
        return "state-machine"
    if any(term in lowered for term in ("evidence-ladder", "evidence ladder", "evidence hierarchy", "research evidence", "source confidence", "confidence ladder", "counterevidence", "claim support", "source gap", "recommendation confidence")):
        return "evidence-ladder"
    if any(term in lowered for term in ("comparison-matrix", "comparison matrix", "decision matrix", "scorecard", "compare", "versus", "tradeoff lens", "recommended option", "guardrail")):
        return "comparison-matrix"
    if any(term in lowered for term in ("causal-loop", "causal loop", "feedback loop", "reinforcing loop", "balancing loop", "delayed effect", "side effect", "intervention", "leverage point", "root cause")):
        return "causal-loop"
    if any(term in lowered for term in ("phase-timeline", "phase timeline", "timeline", "milestone", "roadmap", "release plan", "incident timeline", "chronology")):
        return "phase-timeline"
    if any(term in lowered for term in ("metric-dashboard", "metric dashboard", "kpi", "slo", "service level", "threshold", "trend", "forecast", "anomaly", "burn rate", "error budget")):
        return "metric-dashboard"
    if any(term in lowered for term in ("layered-architecture", "layered architecture", "architecture layer", "layer stack", "system layers", "cross-cutting concern", "observability layer", "rollout gate", "platform layer")):
        return "layered-architecture"
    if any(term in lowered for term in ("data-lineage", "data lineage", "lineage graph", "lineage map", "data pipeline", "etl", "elt", "source to consumer", "source-to-consumer", "quality gate", "schema check", "freshness window", "drift monitor", "drift alert")):
        return "data-lineage"
    if any(term in lowered for term in ("sequence-trace", "sequence trace", "distributed trace", "request trace", "trace span", "span waterfall", "latency budget", "critical path", "service call")):
        return "sequence-trace"
    if any(term in lowered for term in ("sankey-flow", "sankey flow", "sankey", "conversion flow", "conversion funnel", "flow split", "flow merge", "dropoff", "drop-off", "value stream", "loss stream")):
        return "sankey-flow"
    if any(term in lowered for term in ("swimlane-handoff", "swimlane handoff", "swimlane", "handoff map", "handoff workflow", "process handoff", "sla", "rework loop", "escalation", "approval lane", "role lane")):
        return "swimlane-handoff"
    if any(term in lowered for term in ("risk-bowtie", "risk bowtie", "bowtie", "bow-tie", "barrier analysis", "hazard", "top event", "preventive barrier", "mitigative barrier", "degraded barrier", "risk control")):
        return "risk-bowtie"
    if any(term in lowered for term in ("scenario-tree", "scenario tree", "decision tree", "branching scenario", "probability branch", "scenario branch", "expected value", "upside scenario", "downside scenario", "fallback scenario")):
        return "scenario-tree"
    if any(term in lowered for term in ("dependency-map", "dependency map", "dependency graph", "dependency", "dag", "blocked by", "bottleneck", "cutover", "fallback path", "migration dependency")):
        return "dependency-map"
    if any(term in lowered for term in ("systems-flow", "queue", "retry", "dead-letter", "feedback", "worker")):
        return "systems-flow"
    return "auto"


def extract_format(text: str) -> tuple[float, int, int, int]:
    match = re.search(
        r"Use\s+([0-9]+(?:\.[0-9]+)?)\s+seconds,\s+([0-9]+)\s+fps,\s+and\s+([0-9]+)x([0-9]+)",
        text,
        flags=re.IGNORECASE,
    )
    if not match:
        return 12.0, 12, 1280, 720
    return float(match.group(1)), int(match.group(2)), int(match.group(3)), int(match.group(4))


def extract_bullets_after(text: str, heading: str) -> list[str]:
    start = re.search(re.escape(heading), text, flags=re.IGNORECASE)
    if not start:
        return []
    tail = text[start.end() :]
    lines = []
    for raw in tail.splitlines():
        line = raw.strip()
        if not line:
            if lines:
                break
            continue
        if line.endswith(":") and lines:
            break
        if line.startswith("- "):
            lines.append(clean_value(line[2:]))
        elif lines:
            break
    return lines


def extract_bullets_after_any(text: str, headings: list[str]) -> list[str]:
    for heading in headings:
        values = extract_bullets_after(text, heading)
        if values:
            return values
    return []


def derived_contract(prompt_text: str) -> dict[str, object]:
    paths = extract_required_paths(prompt_text)
    project_root = derive_project_root(paths)
    output_id = derive_output_id(paths)
    duration, fps, width, height = extract_format(prompt_text)
    facts = extract_bullets_after(prompt_text, "Preserve these source facts")
    anchors = extract_bullets_after(prompt_text, "Preserve these visual anchors")
    node_labels = extract_bullets_after_any(prompt_text, ["Preserve these causal variables", "Preserve these node labels"])
    decision_options = extract_bullets_after_any(prompt_text, ["Preserve these decision options", "Preserve these option labels"])
    decision_criteria = extract_bullets_after_any(prompt_text, ["Preserve these decision criteria", "Preserve these criterion labels"])
    state_labels = extract_bullets_after_any(prompt_text, ["Preserve these lifecycle states", "Preserve these state labels"])
    guard_labels = extract_bullets_after_any(prompt_text, ["Preserve these transition guards", "Preserve these guard labels"])
    system_labels = extract_bullets_after_any(prompt_text, ["Preserve these system components", "Preserve these system labels"])
    tree_labels = extract_bullets_after_any(prompt_text, ["Preserve these tree nodes", "Preserve these tree labels"])
    meter_labels = extract_bullets_after_any(prompt_text, ["Preserve these strategy meters", "Preserve these meter labels"])
    route_labels = extract_bullets_after(prompt_text, "Preserve these route labels")
    checkpoint_labels = extract_bullets_after(prompt_text, "Preserve these checkpoint labels")
    phase_labels = extract_bullets_after_any(prompt_text, ["Preserve these timeline phases", "Preserve these phase labels"])
    metric_labels = extract_bullets_after(prompt_text, "Preserve these metric labels")
    threshold_labels = extract_bullets_after(prompt_text, "Preserve these threshold labels")
    dependency_labels = extract_bullets_after(prompt_text, "Preserve these dependency labels")
    cluster_labels = extract_bullets_after_any(prompt_text, ["Preserve these dependency clusters", "Preserve these cluster labels"])
    trace_labels = extract_bullets_after(prompt_text, "Preserve these trace labels")
    flow_labels = extract_bullets_after(prompt_text, "Preserve these flow labels")
    lane_labels = extract_bullets_after(prompt_text, "Preserve these lane labels")
    handoff_labels = extract_bullets_after(prompt_text, "Preserve these handoff labels")
    threat_labels = extract_bullets_after(prompt_text, "Preserve these threat labels")
    barrier_labels = extract_bullets_after(prompt_text, "Preserve these barrier labels")
    consequence_labels = extract_bullets_after(prompt_text, "Preserve these consequence labels")
    scenario_labels = extract_bullets_after(prompt_text, "Preserve these scenario labels")
    probability_labels = extract_bullets_after(prompt_text, "Preserve these probability labels")
    claim_labels = extract_bullets_after(prompt_text, "Preserve these claim labels")
    evidence_labels = extract_bullets_after(prompt_text, "Preserve these evidence labels")
    layer_labels = extract_bullets_after(prompt_text, "Preserve these layer labels")
    concern_labels = extract_bullets_after(prompt_text, "Preserve these concern labels")
    lineage_labels = extract_bullets_after(prompt_text, "Preserve these lineage labels")
    quality_labels = extract_bullets_after(prompt_text, "Preserve these quality labels")
    if not facts:
        raise ValueError("No source facts found under 'Preserve these source facts'.")
    return {
        "projectRoot": project_root,
        "outputId": output_id,
        "title": extract_label(prompt_text, "Video title", "Standalone Explainer"),
        "topic": extract_label(prompt_text, "Topic", "topic explainer"),
        "checkedDate": extract_label(prompt_text, "Checked date", "unknown"),
        "pattern": extract_pattern(prompt_text),
        "duration": duration,
        "fps": fps,
        "width": width,
        "height": height,
        "facts": facts,
        "anchors": anchors,
        "nodeLabels": node_labels,
        "decisionOptions": decision_options,
        "decisionCriteria": decision_criteria,
        "stateLabels": state_labels,
        "guardLabels": guard_labels,
        "systemLabels": system_labels,
        "treeLabels": tree_labels,
        "meterLabels": meter_labels,
        "routeLabels": route_labels,
        "checkpointLabels": checkpoint_labels,
        "phaseLabels": phase_labels,
        "metricLabels": metric_labels,
        "thresholdLabels": threshold_labels,
        "dependencyLabels": dependency_labels,
        "clusterLabels": cluster_labels,
        "traceLabels": trace_labels,
        "flowLabels": flow_labels,
        "laneLabels": lane_labels,
        "handoffLabels": handoff_labels,
        "threatLabels": threat_labels,
        "barrierLabels": barrier_labels,
        "consequenceLabels": consequence_labels,
        "scenarioLabels": scenario_labels,
        "probabilityLabels": probability_labels,
        "claimLabels": claim_labels,
        "evidenceLabels": evidence_labels,
        "layerLabels": layer_labels,
        "concernLabels": concern_labels,
        "lineageLabels": lineage_labels,
        "qualityLabels": quality_labels,
        "requiredPaths": paths,
    }


def prompt_requires_pattern_mix(text: str) -> bool:
    lowered = text.lower()
    triggers = [
        "metro minimal tonal motion",
        "complex",
        "dynamic",
        "information-dense",
        "visual density",
        "low-text",
        "more visual",
        "not following the design",
        "not aligned with the design",
        "no esta siguiendo",
        "no está siguiendo",
        "boxes plus labels",
        "cajas",
        "megacanvas",
        "camera movement",
        "masonry",
        "strict-grid",
        "colorset1",
        "grayscale hierarchy",
        "niveles de grises",
    ]
    return any(trigger in lowered for trigger in triggers)


def derive_metro_pattern_mix(prompt_text: str, contract: dict[str, object]) -> dict[str, object] | None:
    if not prompt_requires_pattern_mix(prompt_text):
        return None
    args = argparse.Namespace(
        prompt_file=None,
        text=None,
        output=None,
        min_patterns=6,
        min_patterns_used=3,
        min_functional_zones=5,
        min_motion_systems=4,
        min_camera_events=3,
        require_anchor=[],
    )
    report = build_metro_pattern_mix_report("prompt", prompt_text, args)
    selected = report.get("selected") if isinstance(report, dict) else {}
    helper_pattern = ""
    if isinstance(selected, dict):
        helper_pattern = str(selected.get("helperPattern") or selected.get("suggestedScaffoldPattern") or "")
    contract_pattern = str(contract.get("pattern") or "")
    if helper_pattern and contract_pattern == "auto":
        contract["pattern"] = helper_pattern
        report["wrapperApplied"] = {
            "script": PATTERN_MIX_SCRIPT.name,
            "patternWasAuto": True,
            "helperPattern": helper_pattern,
        }
    else:
        if isinstance(selected, dict) and contract_pattern and contract_pattern != "auto":
            original_helper = str(selected.get("helperPattern") or "")
            if original_helper != contract_pattern:
                selected["helperPattern"] = contract_pattern
                selected["helperOverrideReason"] = (
                    f"Prompt contract explicitly requested {contract_pattern}; "
                    f"planner suggestion remains in suggestedScaffoldPattern."
                )
                wrapper_hints = report.get("wrapperHints")
                if isinstance(wrapper_hints, dict):
                    wrapper_hints["scaffoldPattern"] = contract_pattern
        report["wrapperApplied"] = {
            "script": PATTERN_MIX_SCRIPT.name,
            "patternWasAuto": False,
            "helperPattern": contract_pattern,
        }
    return report


def compact_metro_pattern_mix(report: object) -> object:
    if not isinstance(report, dict):
        return report
    compact_keys = [
        "passed",
        "source",
        "selected",
        "patternCounts",
        "patternIdsNamed",
        "patternsUsedInBeats",
        "functionalZones",
        "semanticMotionSystems",
        "cameraPath",
        "transitionContracts",
        "masonryContract",
        "antiPatternRisks",
        "textBudget",
        "metroConstraints",
        "wrapperHints",
        "wrapperApplied",
        "findings",
    ]
    return {key: report[key] for key in compact_keys if key in report}


def build_command(contract: dict[str, object]) -> list[str]:
    uv = shutil.which("uv")
    if not uv:
        raise RuntimeError("uv is required but was not found on PATH.")
    helper = Path(__file__).with_name("build_standalone_explainer.py")
    cmd = [
        uv,
        "run",
        "--script",
        str(helper),
        "--project-root",
        str(contract["projectRoot"]),
        "--title",
        str(contract["title"]),
        "--topic",
        str(contract["topic"]),
        "--output-id",
        str(contract["outputId"]),
        "--pattern",
        str(contract["pattern"]),
        "--checked-date",
        str(contract["checkedDate"]),
        "--duration",
        str(contract["duration"]),
        "--fps",
        str(contract["fps"]),
        "--width",
        str(contract["width"]),
        "--height",
        str(contract["height"]),
        "--edge-style",
        "square",
    ]
    if contract.get("masonryLayoutRequired") is True:
        cmd.append("--masonry-layout")
    for fact in contract["facts"]:
        cmd.extend(["--fact", str(fact)])
    for anchor in contract["anchors"]:
        cmd.extend(["--anchor", str(anchor)])
    for label in contract.get("nodeLabels", []):
        cmd.extend(["--node-label", str(label)])
    for label in contract.get("decisionOptions", []):
        cmd.extend(["--option-label", str(label)])
    for label in contract.get("decisionCriteria", []):
        cmd.extend(["--criterion-label", str(label)])
    for label in contract.get("stateLabels", []):
        cmd.extend(["--state-label", str(label)])
    for label in contract.get("guardLabels", []):
        cmd.extend(["--guard-label", str(label)])
    for label in contract.get("systemLabels", []):
        cmd.extend(["--system-label", str(label)])
    for label in contract.get("treeLabels", []):
        cmd.extend(["--tree-label", str(label)])
    for label in contract.get("meterLabels", []):
        cmd.extend(["--meter-label", str(label)])
    for label in contract.get("routeLabels", []):
        cmd.extend(["--route-label", str(label)])
    for label in contract.get("checkpointLabels", []):
        cmd.extend(["--checkpoint-label", str(label)])
    for label in contract.get("phaseLabels", []):
        cmd.extend(["--phase-label", str(label)])
    for label in contract.get("metricLabels", []):
        cmd.extend(["--metric-label", str(label)])
    for label in contract.get("thresholdLabels", []):
        cmd.extend(["--threshold-label", str(label)])
    for label in contract.get("dependencyLabels", []):
        cmd.extend(["--dependency-label", str(label)])
    for label in contract.get("clusterLabels", []):
        cmd.extend(["--cluster-label", str(label)])
    for label in contract.get("traceLabels", []):
        cmd.extend(["--trace-label", str(label)])
    for label in contract.get("flowLabels", []):
        cmd.extend(["--flow-label", str(label)])
    for label in contract.get("laneLabels", []):
        cmd.extend(["--lane-label", str(label)])
    for label in contract.get("handoffLabels", []):
        cmd.extend(["--handoff-label", str(label)])
    for label in contract.get("threatLabels", []):
        cmd.extend(["--threat-label", str(label)])
    for label in contract.get("barrierLabels", []):
        cmd.extend(["--barrier-label", str(label)])
    for label in contract.get("consequenceLabels", []):
        cmd.extend(["--consequence-label", str(label)])
    for label in contract.get("scenarioLabels", []):
        cmd.extend(["--scenario-label", str(label)])
    for label in contract.get("probabilityLabels", []):
        cmd.extend(["--probability-label", str(label)])
    for label in contract.get("claimLabels", []):
        cmd.extend(["--claim-label", str(label)])
    for label in contract.get("evidenceLabels", []):
        cmd.extend(["--evidence-label", str(label)])
    for label in contract.get("layerLabels", []):
        cmd.extend(["--layer-label", str(label)])
    for label in contract.get("concernLabels", []):
        cmd.extend(["--concern-label", str(label)])
    for label in contract.get("lineageLabels", []):
        cmd.extend(["--lineage-label", str(label)])
    for label in contract.get("qualityLabels", []):
        cmd.extend(["--quality-label", str(label)])
    return cmd


def configure_state_defaults(args: argparse.Namespace, prompt_text: str, contract: dict[str, object]) -> None:
    if not args.state_manifest:
        args.state_manifest = extract_state_manifest_path(prompt_text)
    if not args.state_manifest and (prompt_requires_pattern_mix(prompt_text) or prompt_requires_metro_audits(prompt_text)):
        args.state_manifest = default_review_manifest(contract, "render-state-check.json")
    if not args.state_manifest:
        return
    if args.state_expect or args.state_expect_final or args.state_expect_contains or args.state_expect_transition or args.state_expect_monotonic or args.state_min_distinct:
        return
    pattern = str(contract["pattern"])
    contract_values = [
        prompt_text,
        contract.get("title"),
        contract.get("topic"),
        *(contract.get("anchors") or []),
        *(contract.get("systemLabels") or []),
    ]
    harness_haystack = " ".join(str(value) for value in contract_values if value is not None).lower()
    plugin_requested = (
        pattern == "swimlane-handoff"
        and (
            "what is a harness plugin" in harness_haystack
            or sum(
                1
                for signal in (
                    "harness plugin",
                    "plugin_bundle_cube",
                    "packaged harness behavior",
                    "installable unit",
                    "distribution mechanism",
                    "marketplace",
                    "allowlist",
                    "npm",
                    "versioning",
                    "govern",
                    "noisy plugin",
                    "github plugin manifest",
                    "claude marketplace",
                    "opencode runtime",
                    "package-install",
                )
                if signal in harness_haystack
            )
            >= 2
        )
    )
    ai_alternatives_requested = (
        pattern == "swimlane-handoff"
        and (
            "what ai alternatives we have" in harness_haystack
            or sum(
                1
                for signal in (
                    "ai alternatives",
                    "atlassian rovo",
                    "gemini app",
                    "github copilot",
                    "claude desktop",
                    "claude code",
                    "workflow gravity",
                    "home base",
                    "comparison_grid",
                    "radar chart",
                    "credit_meter",
                    "use-case selector",
                )
                if signal in harness_haystack
            )
            >= 3
        )
    )
    skill_requested = (
        pattern == "systems-flow"
        and "skill tree" not in harness_haystack
        and "skill-tree" not in harness_haystack
        and "path of exile" not in harness_haystack
        and (
            "what is a skill" in harness_haystack
            or sum(
                1
                for signal in (
                    "skill_card_stack",
                    "skill.md",
                    "progressive disclosure",
                    "long prompt wall",
                    "cost meter",
                    "cost line",
                    "tool badges",
                    "deploy-preview",
                    "bloated",
                    "mini novels",
                    "reusable workflow",
                    "on-demand reusable workflow",
                )
                if signal in harness_haystack
            )
            >= 2
        )
    )
    hook_requested = (
        pattern == "systems-flow"
        and "harness plugin" not in harness_haystack
        and (
            "what is a harness hook" in harness_haystack
            or sum(
                1
                for signal in (
                    "event_timeline",
                    "lifecycle events",
                    "lifecycle boundaries",
                    "shield_gate",
                    "pretooluse",
                    "before tool use",
                    "permission request",
                    "compaction",
                    "notification",
                    "github hook",
                    "claude event",
                    "opencode event",
                    "block dangerous",
                    "bash command",
                    "filter log",
                    "preprocessing",
                    "token savings",
                    "speed-vs-cost",
                    "hooks = lifecycle controls",
                )
                if signal in harness_haystack
            )
            >= 2
        )
    )
    harness_requested = (
        pattern == "systems-flow"
        and "harness hook" not in harness_haystack
        and "harness plugin" not in harness_haystack
        and (
            "what is a harness" in harness_haystack
            or sum(
                1
                for signal in (
                    "comparison_grid",
                    "runtime stack",
                    "runtime wrapper",
                    "engine icon",
                    "vehicle dashboard",
                    "same model",
                    "different shells",
                    "three-column harness",
                    "credit_meter",
                    "use-case matrix",
                    "selection path",
                )
                if signal in harness_haystack
            )
            >= 2
        )
    )
    pattern_transitions = {
        "systems-flow": ["retryVisible=true", "deadLetterVisible=true", "feedbackVisible=true"],
        "skill-tree": ["keystoneVisible=true", "atlasVisible=true"],
        "skill-tree-route": ["damageClusterVisible=true", "defenseClusterVisible=true", "attributeBridgeVisible=true", "keystoneTradeoffVisible=true", "respecVisible=true", "lateClusterVisible=true"],
        "state-machine": ["rollbackVisible=true", "compensationVisible=true", "terminalVisible=true"],
        "comparison-matrix": ["scoreShiftVisible=true", "tradeoffVisible=true", "recommendationVisible=true", "guardrailVisible=true"],
        "causal-loop": ["loopVisible=true", "delayVisible=true", "amplifierVisible=true", "dampingVisible=true", "sideEffectVisible=true", "interventionVisible=true"],
        "phase-timeline": ["riskVisible=true", "gateVisible=true", "handoffVisible=true", "finalVisible=true"],
        "metric-dashboard": ["trendVisible=true", "thresholdVisible=true", "anomalyVisible=true", "forecastVisible=true", "decisionVisible=true"],
        "dependency-map": ["riskVisible=true", "bottleneckVisible=true", "cutoverVisible=true", "fallbackVisible=true"],
        "sequence-trace": ["criticalPathVisible=true", "latencyBudgetVisible=true", "retryVisible=true", "fallbackVisible=true", "responseVisible=true"],
        "sankey-flow": ["splitVisible=true", "lossVisible=true", "bottleneckVisible=true", "mergeVisible=true", "outputVisible=true"],
        "swimlane-handoff": ["slaVisible=true", "reworkVisible=true", "approvalVisible=true", "escalationVisible=true", "completeVisible=true"],
        "risk-bowtie": ["preventiveVisible=true", "topEventVisible=true", "mitigativeVisible=true", "consequenceVisible=true", "degradedVisible=true", "actionVisible=true"],
        "scenario-tree": ["probabilityVisible=true", "riskVisible=true", "upsideVisible=true", "decisionVisible=true", "fallbackVisible=true", "outcomeVisible=true"],
        "evidence-ladder": ["claimVisible=true", "counterEvidenceVisible=true", "gapVisible=true", "confidenceVisible=true", "recommendationVisible=true"],
        "layered-architecture": ["crossCuttingVisible=true", "failurePathVisible=true", "observabilityVisible=true", "rolloutVisible=true"],
        "data-lineage": ["transformVisible=true", "qualityGateVisible=true", "driftVisible=true", "consumerVisible=true", "rollbackVisible=true"],
    }
    args.state_expect = [f"visualPattern={pattern}"] if pattern != "auto" else []
    args.state_expect_transition = [
        item.replace("=true", "=false->true") for item in pattern_transitions.get(pattern, [])
    ]
    args.state_expect_final = [item for item in pattern_transitions.get(pattern, [])]
    args.state_expect_monotonic = ["visibleMechanismCount=nondecreasing"]
    args.state_min_distinct = ["visibleMechanismCount=4"]
    if ai_alternatives_requested:
        args.state_expect_transition = [
            "comparisonGridVisible=false->true",
            "rovoWorkspaceVisible=false->true",
            "geminiWorkspaceVisible=false->true",
            "copilotWorkspaceVisible=false->true",
            "claudeWorkspaceVisible=false->true",
            "quadrantMapVisible=false->true",
            "workflowSelectorVisible=false->true",
            "selectedWorkflowPathVisible=false->true",
            "guardrailWrapVisible=false->true",
            "observabilityWrapVisible=false->true",
        ]
        args.state_expect_final = [
            "comparisonGridVisible=true",
            "rovoWorkspaceVisible=true",
            "geminiWorkspaceVisible=true",
            "copilotWorkspaceVisible=true",
            "claudeWorkspaceVisible=true",
            "platformHomeBaseCount=4",
            "radarAxisCount=5",
            "quadrantMapVisible=true",
            "costMeterCount=4",
            "costMeterLevel=4",
            "workflowSelectorVisible=true",
            "selectedWorkflowPathVisible=true",
            "guardrailWrapVisible=true",
            "observabilityWrapVisible=true",
            "visibleMechanismCount=10",
            "visibleZoneCount=5",
        ]
        args.state_expect_monotonic = [
            "visibleMechanismCount=nondecreasing",
            "platformHomeBaseCount=nondecreasing",
            "radarAxisCount=nondecreasing",
            "costMeterCount=nondecreasing",
            "costMeterLevel=nondecreasing",
        ]
        args.state_min_distinct = [
            "visibleMechanismCount=5",
            "platformHomeBaseCount=3",
            "radarAxisCount=3",
            "costMeterCount=3",
            "costMeterLevel=3",
            "activeZoneId=3",
            "cameraScale=2",
        ]
    elif plugin_requested:
        args.state_expect_transition = [
            "pluginBundleCubeVisible=false->true",
            "bundleOpenedVisible=false->true",
            "githubManifestCardVisible=false->true",
            "claudeMarketplaceGateVisible=false->true",
            "opencodeNpmRuntimeDropVisible=false->true",
            "teamInstallFanoutVisible=false->true",
            "versionUpgradeVisible=false->true",
            "governanceGateVisible=false->true",
            "goodBadPluginSplitVisible=false->true",
            "noisyPluginRiskVisible=false->true",
            "packageInstallVisible=false->true",
            "packagedBehaviorStampVisible=false->true",
        ]
        args.state_expect_final = [
            "pluginBundleCubeVisible=true",
            "bundleOpenedVisible=true",
            "githubManifestCardVisible=true",
            "claudeMarketplaceGateVisible=true",
            "opencodeNpmRuntimeDropVisible=true",
            "teamInstallFanoutVisible=true",
            "versionUpgradeVisible=true",
            "governanceGateVisible=true",
            "goodBadPluginSplitVisible=true",
            "noisyPluginRiskVisible=true",
            "packageInstallVisible=true",
            "packagedBehaviorStampVisible=true",
            "bundleBlockCount=9",
            "bundleModuleCount=5",
            "providerSurfaceCount=3",
            "installFanoutCount=6",
            "versionLevel=4",
            "noisyToolCount=6",
            "costMeterLevel=4",
            "visibleMechanismCount=10",
            "visibleZoneCount=5",
        ]
        args.state_expect_monotonic = [
            "visibleMechanismCount=nondecreasing",
            "bundleBlockCount=nondecreasing",
            "bundleModuleCount=nondecreasing",
            "providerSurfaceCount=nondecreasing",
            "installFanoutCount=nondecreasing",
            "versionLevel=nondecreasing",
            "noisyToolCount=nondecreasing",
            "costMeterLevel=nondecreasing",
        ]
        args.state_min_distinct = [
            "visibleMechanismCount=5",
            "bundleBlockCount=3",
            "bundleModuleCount=3",
            "installFanoutCount=3",
            "versionLevel=3",
            "noisyToolCount=3",
            "costMeterLevel=3",
            "activeZoneId=3",
            "cameraScale=2",
        ]
    elif skill_requested:
        args.state_expect_transition = [
            "skillCardStackVisible=false->true",
            "promptWallCollapsed=false->true",
            "folderStructuresAligned=false->true",
            "progressiveDisclosureVisible=false->true",
            "skillActivationVisible=false->true",
            "exampleSkillCardsVisible=false->true",
            "toolBadgesAttached=false->true",
            "scriptBlockVisible=false->true",
            "bloatedSkillTrimmed=false->true",
            "finalWorkflowStampVisible=false->true",
        ]
        args.state_expect_final = [
            "skillCardStackVisible=true",
            "skillManifestVisible=true",
            "frontmatterContractVisible=true",
            "triggerSurfaceVisible=true",
            "promptWallCollapsed=true",
            "folderStructuresAligned=true",
            "progressiveDisclosureVisible=true",
            "skillActivationVisible=true",
            "exampleSkillCardsVisible=true",
            "toolBadgesAttached=true",
            "scriptBlockVisible=true",
            "bloatedSkillTrimmed=true",
            "finalWorkflowStampVisible=true",
            "resourceBundleVisible=true",
            "validationHarnessVisible=true",
            "readSurfaceVisible=true",
            "skillFileLayerCount=4",
            "triggerExampleCount=5",
            "resourceModuleCount=4",
            "validationStageLevel=5",
            "readSurfaceLevel=4",
            "costMeterLevel=4",
            "visibleMechanismCount=10",
            "visibleZoneCount=5",
        ]
        args.state_expect_monotonic = [
            "visibleMechanismCount=nondecreasing",
            "skillFileLayerCount=nondecreasing",
            "triggerExampleCount=nondecreasing",
            "resourceModuleCount=nondecreasing",
            "validationStageLevel=nondecreasing",
            "readSurfaceLevel=nondecreasing",
            "costMeterLevel=nondecreasing",
        ]
        args.state_min_distinct = [
            "visibleMechanismCount=5",
            "skillFileLayerCount=3",
            "triggerExampleCount=3",
            "resourceModuleCount=3",
            "validationStageLevel=3",
            "readSurfaceLevel=3",
            "costMeterLevel=3",
            "activeZoneId=3",
            "cameraScale=2",
        ]
    elif hook_requested:
        args.state_expect_transition = [
            "shieldGateOverlayVisible=false->true",
            "githubHookBadgesVisible=false->true",
            "claudeEventCloudVisible=false->true",
            "opencodeEventListVisible=false->true",
            "hookJobCascadeVisible=false->true",
            "commandBlockPathVisible=false->true",
            "logFilterPathVisible=false->true",
            "tokenSavingsCounterVisible=false->true",
            "costLatencyTradeoffVisible=false->true",
            "lifecycleRuleStampVisible=false->true",
        ]
        args.state_expect_final = [
            "eventTimelineVisible=true",
            "shieldGateOverlayVisible=true",
            "githubHookBadgesVisible=true",
            "claudeEventCloudVisible=true",
            "opencodeEventListVisible=true",
            "hookJobCascadeVisible=true",
            "commandBlockPathVisible=true",
            "logFilterPathVisible=true",
            "tokenSavingsCounterVisible=true",
            "costLatencyTradeoffVisible=true",
            "lifecycleRuleStampVisible=true",
            "activeHookEventCount=8",
            "providerLaneCount=3",
            "policyTokenCount=6",
            "tokenSavingsLevel=6",
            "latencyCostLevel=5",
            "visibleMechanismCount=9",
            "visibleZoneCount=5",
        ]
        args.state_expect_monotonic = [
            "visibleMechanismCount=nondecreasing",
            "activeHookEventCount=nondecreasing",
            "policyTokenCount=nondecreasing",
            "tokenSavingsLevel=nondecreasing",
            "latencyCostLevel=nondecreasing",
        ]
        args.state_min_distinct = [
            "visibleMechanismCount=5",
            "activeHookEventCount=3",
            "policyTokenCount=3",
            "tokenSavingsLevel=3",
            "latencyCostLevel=3",
            "activeZoneId=3",
            "cameraScale=2",
        ]
    elif harness_requested:
        args.state_expect_transition = [
            "runtimeStackVisible=false->true",
            "engineCoreVisible=false->true",
            "dashboardControlsVisible=false->true",
            "modelBadgeShared=false->true",
            "threeHarnessShellsVisible=false->true",
            "creditMeterRising=false->true",
            "featureGridMuted=false->true",
            "useCaseMatrixActive=false->true",
            "selectionPathHighlighted=false->true",
            "agentLoopRingVisible=false->true",
        ]
        args.state_expect_final = [
            "comparisonGridVisible=true",
            "runtimeStackVisible=true",
            "engineCoreVisible=true",
            "dashboardControlsVisible=true",
            "modelBadgeShared=true",
            "sameModelShellCount=3",
            "shellCopilotVisible=true",
            "shellClaudeCodeVisible=true",
            "shellOpenCodeVisible=true",
            "threeHarnessShellsVisible=true",
            "toolCountLevel=6",
            "creditMeterLevel=5",
            "creditMeterRising=true",
            "featureGridMuted=true",
            "useCaseMatrixActive=true",
            "selectionPathHighlighted=true",
            "agentLoopRingVisible=true",
            "visibleMechanismCount=10",
            "visibleZoneCount=5",
        ]
        args.state_expect_monotonic = [
            "visibleMechanismCount=nondecreasing",
            "layersAssembling=nondecreasing",
            "toolCountLevel=nondecreasing",
            "creditMeterLevel=nondecreasing",
        ]
        args.state_min_distinct = [
            "visibleMechanismCount=5",
            "layersAssembling=3",
            "toolCountLevel=3",
            "creditMeterLevel=3",
            "activeZoneId=3",
            "cameraScale=2",
        ]
    elif pattern == "systems-flow":
        args.state_expect_final.extend(["queueSlots=8", "visibleMechanismCount=6"])
        args.state_expect_monotonic.append("queueSlots=nondecreasing")
        args.state_min_distinct = [
            item for item in args.state_min_distinct if not str(item).startswith("visibleMechanismCount=")
        ]
        args.state_min_distinct.extend(["visibleMechanismCount=5", "queueSlots=3"])
    if pattern == "skill-tree":
        args.state_expect_final.append("routeCount=5")
        args.state_expect_monotonic.append("routeCount=nondecreasing")
        args.state_min_distinct.append("routeCount=3")
    if pattern == "skill-tree-route":
        args.state_expect_final.extend(["activeRouteNodeCount=8", "visibleMechanismCount=7"])
        args.state_expect_monotonic.append("activeRouteNodeCount=nondecreasing")
        args.state_min_distinct = [
            item for item in args.state_min_distinct if not str(item).startswith("visibleMechanismCount=")
        ]
        args.state_min_distinct.extend(["visibleMechanismCount=5", "activeRouteNodeCount=4"])
    if pattern == "comparison-matrix":
        args.state_expect_final.append("criteriaRevealed=4")
        args.state_expect_monotonic.append("criteriaRevealed=nondecreasing")
        args.state_min_distinct.append("criteriaRevealed=3")
    if pattern == "causal-loop":
        args.state_expect_final.append("visibleMechanismCount=6")
        args.state_min_distinct = [
            item for item in args.state_min_distinct if not str(item).startswith("visibleMechanismCount=")
        ]
        args.state_min_distinct.append("visibleMechanismCount=5")
    if pattern == "state-machine":
        args.state_expect_final.append("activeState=5")
        args.state_expect_monotonic.append("activeState=nondecreasing")
        args.state_min_distinct.append("activeState=4")
    if pattern == "phase-timeline":
        args.state_expect_final.append("activePhase=5")
        args.state_expect_monotonic.append("activePhase=nondecreasing")
        args.state_min_distinct.append("activePhase=4")
    if pattern == "dependency-map":
        args.state_expect_final.append("edgeCount=7")
        args.state_expect_monotonic.append("edgeCount=nondecreasing")
        args.state_min_distinct.append("edgeCount=4")
    if pattern == "sequence-trace":
        args.state_expect_final.append("activeSpanCount=7")
        args.state_expect_monotonic.append("activeSpanCount=nondecreasing")
        args.state_min_distinct.append("activeSpanCount=4")
    if pattern == "sankey-flow":
        args.state_expect_final.extend(["activeFlowCount=7", "visibleMechanismCount=6"])
        args.state_expect_monotonic.append("activeFlowCount=nondecreasing")
        args.state_min_distinct = [
            item for item in args.state_min_distinct if not str(item).startswith("visibleMechanismCount=")
        ]
        args.state_min_distinct.extend(["visibleMechanismCount=5", "activeFlowCount=4"])
    if pattern == "swimlane-handoff" and not plugin_requested and not ai_alternatives_requested:
        args.state_expect_final.extend(["activeHandoffCount=8", "visibleMechanismCount=6"])
        args.state_expect_monotonic.append("activeHandoffCount=nondecreasing")
        args.state_min_distinct = [
            item for item in args.state_min_distinct if not str(item).startswith("visibleMechanismCount=")
        ]
        args.state_min_distinct.extend(["visibleMechanismCount=5", "activeHandoffCount=4"])
    if pattern == "risk-bowtie":
        args.state_expect_final.extend(["activeThreatCount=4", "visibleMechanismCount=7"])
        args.state_expect_monotonic.append("activeThreatCount=nondecreasing")
        args.state_min_distinct = [
            item for item in args.state_min_distinct if not str(item).startswith("visibleMechanismCount=")
        ]
        args.state_min_distinct.extend(["visibleMechanismCount=5", "activeThreatCount=3"])
    if pattern == "scenario-tree":
        args.state_expect_final.extend(["activeScenarioCount=7", "visibleMechanismCount=7"])
        args.state_expect_monotonic.append("activeScenarioCount=nondecreasing")
        args.state_min_distinct = [
            item for item in args.state_min_distinct if not str(item).startswith("visibleMechanismCount=")
        ]
        args.state_min_distinct.extend(["visibleMechanismCount=5", "activeScenarioCount=4"])
    if pattern == "evidence-ladder":
        args.state_expect_final.extend(["activeEvidenceCount=6", "visibleMechanismCount=6"])
        args.state_expect_monotonic.append("activeEvidenceCount=nondecreasing")
        args.state_min_distinct = [
            item for item in args.state_min_distinct if not str(item).startswith("visibleMechanismCount=")
        ]
        args.state_min_distinct.extend(["visibleMechanismCount=5", "activeEvidenceCount=4"])
    if pattern == "layered-architecture":
        args.state_expect_final.extend(["activeLayerCount=6", "visibleMechanismCount=6"])
        args.state_expect_monotonic.append("activeLayerCount=nondecreasing")
        args.state_min_distinct = [
            item for item in args.state_min_distinct if not str(item).startswith("visibleMechanismCount=")
        ]
        args.state_min_distinct.extend(["visibleMechanismCount=5", "activeLayerCount=4"])
    if pattern == "data-lineage":
        args.state_expect_final.extend(["activeLineageCount=6", "visibleMechanismCount=6"])
        args.state_expect_monotonic.append("activeLineageCount=nondecreasing")
        args.state_min_distinct = [
            item for item in args.state_min_distinct if not str(item).startswith("visibleMechanismCount=")
        ]
        args.state_min_distinct.extend(["visibleMechanismCount=5", "activeLineageCount=4"])
    if prompt_requires_pattern_mix(prompt_text) or prompt_requires_metro_audits(prompt_text):
        args.state_expect_final.append("visibleZoneCount=5")
        args.state_min_distinct.extend(["activeZoneId=3", "cameraScale=2"])
    label_fields = [
        ("causalLabels", "nodeLabels"),
        ("decisionOptions", "decisionOptions"),
        ("decisionCriteria", "decisionCriteria"),
        ("stateLabels", "stateLabels"),
        ("guardLabels", "guardLabels"),
        ("systemLabels", "systemLabels"),
        ("treeLabels", "treeLabels"),
        ("meterLabels", "meterLabels"),
        ("routeLabels", "routeLabels"),
        ("checkpointLabels", "checkpointLabels"),
        ("phaseLabels", "phaseLabels"),
        ("metricLabels", "metricLabels"),
        ("thresholdLabels", "thresholdLabels"),
        ("dependencyLabels", "dependencyLabels"),
        ("clusterLabels", "clusterLabels"),
        ("traceLabels", "traceLabels"),
        ("flowLabels", "flowLabels"),
        ("laneLabels", "laneLabels"),
        ("handoffLabels", "handoffLabels"),
        ("threatLabels", "threatLabels"),
        ("barrierLabels", "barrierLabels"),
        ("consequenceLabels", "consequenceLabels"),
        ("scenarioLabels", "scenarioLabels"),
        ("probabilityLabels", "probabilityLabels"),
        ("claimLabels", "claimLabels"),
        ("evidenceLabels", "evidenceLabels"),
        ("layerLabels", "layerLabels"),
        ("concernLabels", "concernLabels"),
        ("lineageLabels", "lineageLabels"),
        ("qualityLabels", "qualityLabels"),
    ]
    contains: list[str] = []
    for state_key, contract_key in label_fields:
        labels = [str(label) for label in contract.get(contract_key, []) if str(label).strip()]
        if not labels:
            continue
        picks = [labels[0]]
        if labels[-1] != labels[0]:
            picks.append(labels[-1])
        contains.extend(f"{state_key}={label}" for label in picks)
    args.state_expect_contains = contains


def verify_outputs(contract: dict[str, object], pending_manifest: Path | None = None) -> list[dict[str, object]]:
    findings: list[dict[str, object]] = []
    pending_manifest_posix = pending_manifest.as_posix() if pending_manifest else None
    for raw in contract["requiredPaths"]:
        path = Path(str(raw))
        if pending_manifest_posix and path.as_posix() == pending_manifest_posix:
            continue
        if not path.exists():
            findings.append({"code": "missing", "path": str(raw), "message": "Required path does not exist."})
        elif path.is_file() and path.stat().st_size <= 0:
            findings.append({"code": "empty", "path": str(raw), "message": "Required file is empty."})
    contact_manifest = (
        Path(str(contract["projectRoot"]))
        / "artifacts"
        / "video-renders"
        / "draft"
        / "review"
        / f"{contract['outputId']}-contact-sheet.json"
    )
    if contact_manifest.exists():
        try:
            data = json.loads(contact_manifest.read_text(encoding="utf-8"))
            if data.get("passed") is not True:
                findings.append({"code": "contact-sheet-not-passed", "path": contact_manifest.as_posix(), "message": "Expected passed=true."})
        except json.JSONDecodeError as exc:
            findings.append({"code": "invalid-contact-json", "path": contact_manifest.as_posix(), "message": str(exc)})
    else:
        findings.append({"code": "missing-contact-json", "path": contact_manifest.as_posix(), "message": "Contact-sheet manifest missing."})
    return findings


def contact_sheet_manifest_path(contract: dict[str, object]) -> Path:
    return (
        Path(str(contract["projectRoot"]))
        / "artifacts"
        / "video-renders"
        / "draft"
        / "review"
        / f"{contract['outputId']}-contact-sheet.json"
    )


def summarize_contact_sheet(contract: dict[str, object]) -> dict[str, object]:
    path = contact_sheet_manifest_path(contract)
    report: dict[str, object] = {
        "checked": path.as_posix(),
        "exists": path.exists(),
        "passed": None,
    }
    if not path.exists():
        return report
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        report["readError"] = str(exc)
        return report
    metrics = data.get("metrics") if isinstance(data.get("metrics"), dict) else {}
    sample_times = data.get("sampleTimes") if isinstance(data.get("sampleTimes"), list) else []
    color_buckets = metrics.get("tileColorBuckets") if isinstance(metrics.get("tileColorBuckets"), list) else []
    nonbackground = (
        metrics.get("tileNonbackgroundRatios")
        if isinstance(metrics.get("tileNonbackgroundRatios"), list)
        else []
    )
    consecutive_change = (
        metrics.get("consecutiveChangeRatios")
        if isinstance(metrics.get("consecutiveChangeRatios"), list)
        else []
    )

    def tile_summary(index: int) -> dict[str, object]:
        tile: dict[str, object] = {"index": index}
        if 0 <= index < len(sample_times):
            tile["seconds"] = sample_times[index]
        if 0 <= index < len(color_buckets):
            tile["colorBuckets"] = color_buckets[index]
        if 0 <= index < len(nonbackground):
            tile["nonbackgroundRatio"] = nonbackground[index]
        if 0 <= index < len(consecutive_change):
            tile["changeToNextRatio"] = consecutive_change[index]
        if 0 < index <= len(consecutive_change):
            tile["changeFromPreviousRatio"] = consecutive_change[index - 1]
        return tile

    def opening_tile_assessment() -> dict[str, object]:
        assessment: dict[str, object] = {"weak": False, "flags": []}
        if not color_buckets and not nonbackground:
            return assessment
        flags: list[str] = []
        median_colors = metrics.get("medianTileColorBuckets")
        median_nonbackground = metrics.get("medianTileNonbackgroundRatio")
        if color_buckets and isinstance(median_colors, (int, float)) and median_colors > 0:
            color_ratio = float(color_buckets[0]) / float(median_colors)
            assessment["colorBucketRatioToMedian"] = color_ratio
            if color_ratio < 0.35:
                flags.append("low-color-diversity-vs-median")
        if nonbackground and isinstance(median_nonbackground, (int, float)) and median_nonbackground > 0:
            nonbackground_ratio = float(nonbackground[0]) / float(median_nonbackground)
            assessment["nonbackgroundRatioToMedian"] = nonbackground_ratio
            if nonbackground_ratio < 0.60:
                flags.append("low-nonbackground-vs-median")
        assessment["weak"] = bool(flags)
        assessment["flags"] = flags
        return assessment

    final_index = max(len(color_buckets), len(nonbackground), len(sample_times)) - 1
    report.update(
        {
            "passed": data.get("passed"),
            "samples": data.get("samples"),
            "sampleTimes": sample_times,
            "sheet": data.get("sheet"),
            "metrics": {
                "tileColorBuckets": color_buckets,
                "minTileColorBuckets": metrics.get("minTileColorBuckets"),
                "medianTileColorBuckets": metrics.get("medianTileColorBuckets"),
                "tileNonbackgroundRatios": nonbackground,
                "minTileNonbackgroundRatio": metrics.get("minTileNonbackgroundRatio"),
                "medianTileNonbackgroundRatio": metrics.get("medianTileNonbackgroundRatio"),
                "consecutiveChangeRatios": consecutive_change,
                "minConsecutiveChangeRatio": metrics.get("minConsecutiveChangeRatio"),
                "maxConsecutiveChangeRatio": metrics.get("maxConsecutiveChangeRatio"),
                "changingPairs": metrics.get("changingPairs"),
                "lowChangePairs": metrics.get("lowChangePairs"),
            },
            "openingTile": tile_summary(0) if final_index >= 0 else None,
            "finalTile": tile_summary(final_index) if final_index >= 0 else None,
            "openingTileAssessment": opening_tile_assessment(),
            "findings": data.get("findings"),
        }
    )
    return report


def verify_source_preservation(contract: dict[str, object], findings: list[dict[str, object]]) -> dict[str, object]:
    source_paths = [
        Path(str(raw))
        for raw in contract["requiredPaths"]
        if str(raw).replace("\\", "/").endswith("/source/source-package.json")
    ]
    report: dict[str, object] = {
        "checked": source_paths[0].as_posix() if source_paths else None,
        "expectedFacts": len(contract["facts"]),
        "expectedAnchors": len(contract["anchors"]),
        "expectedNodeLabels": len(contract.get("nodeLabels", [])),
        "expectedDecisionOptions": len(contract.get("decisionOptions", [])),
        "expectedDecisionCriteria": len(contract.get("decisionCriteria", [])),
        "expectedStateLabels": len(contract.get("stateLabels", [])),
        "expectedGuardLabels": len(contract.get("guardLabels", [])),
        "expectedSystemLabels": len(contract.get("systemLabels", [])),
        "expectedTreeLabels": len(contract.get("treeLabels", [])),
        "expectedMeterLabels": len(contract.get("meterLabels", [])),
        "expectedRouteLabels": len(contract.get("routeLabels", [])),
        "expectedCheckpointLabels": len(contract.get("checkpointLabels", [])),
        "expectedPhaseLabels": len(contract.get("phaseLabels", [])),
        "expectedMetricLabels": len(contract.get("metricLabels", [])),
        "expectedThresholdLabels": len(contract.get("thresholdLabels", [])),
        "expectedDependencyLabels": len(contract.get("dependencyLabels", [])),
        "expectedClusterLabels": len(contract.get("clusterLabels", [])),
        "expectedTraceLabels": len(contract.get("traceLabels", [])),
        "expectedFlowLabels": len(contract.get("flowLabels", [])),
        "expectedLaneLabels": len(contract.get("laneLabels", [])),
        "expectedHandoffLabels": len(contract.get("handoffLabels", [])),
        "expectedThreatLabels": len(contract.get("threatLabels", [])),
        "expectedBarrierLabels": len(contract.get("barrierLabels", [])),
        "expectedConsequenceLabels": len(contract.get("consequenceLabels", [])),
        "expectedScenarioLabels": len(contract.get("scenarioLabels", [])),
        "expectedProbabilityLabels": len(contract.get("probabilityLabels", [])),
        "expectedClaimLabels": len(contract.get("claimLabels", [])),
        "expectedEvidenceLabels": len(contract.get("evidenceLabels", [])),
        "expectedLayerLabels": len(contract.get("layerLabels", [])),
        "expectedConcernLabels": len(contract.get("concernLabels", [])),
        "expectedLineageLabels": len(contract.get("lineageLabels", [])),
        "expectedQualityLabels": len(contract.get("qualityLabels", [])),
        "missingFacts": [],
        "missingAnchors": [],
        "missingNodeLabels": [],
        "missingDecisionOptions": [],
        "missingDecisionCriteria": [],
        "missingStateLabels": [],
        "missingGuardLabels": [],
        "missingSystemLabels": [],
        "missingTreeLabels": [],
        "missingMeterLabels": [],
        "missingRouteLabels": [],
        "missingCheckpointLabels": [],
        "missingPhaseLabels": [],
        "missingMetricLabels": [],
        "missingThresholdLabels": [],
        "missingDependencyLabels": [],
        "missingClusterLabels": [],
        "missingTraceLabels": [],
        "missingFlowLabels": [],
        "missingLaneLabels": [],
        "missingHandoffLabels": [],
        "missingThreatLabels": [],
        "missingBarrierLabels": [],
        "missingConsequenceLabels": [],
        "missingScenarioLabels": [],
        "missingProbabilityLabels": [],
        "missingClaimLabels": [],
        "missingEvidenceLabels": [],
        "missingLayerLabels": [],
        "missingConcernLabels": [],
        "missingLineageLabels": [],
        "missingQualityLabels": [],
    }
    if len(source_paths) != 1:
        findings.append({
            "code": "source-package-path-count",
            "path": "requiredPaths",
            "message": f"Expected one source-package.json path, got {len(source_paths)}.",
        })
        return report
    source_path = source_paths[0]
    if not source_path.exists():
        return report
    try:
        data = json.loads(source_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        findings.append({"code": "invalid-source-package-json", "path": source_path.as_posix(), "message": str(exc)})
        return report
    source_facts = data.get("sourceFacts") if isinstance(data.get("sourceFacts"), list) else []
    strategy_anchors = data.get("strategyAnchors") if isinstance(data.get("strategyAnchors"), list) else []
    causal_labels = data.get("causalLabels") if isinstance(data.get("causalLabels"), list) else []
    decision_options = data.get("decisionOptions") if isinstance(data.get("decisionOptions"), list) else []
    decision_criteria = data.get("decisionCriteria") if isinstance(data.get("decisionCriteria"), list) else []
    state_labels = data.get("stateLabels") if isinstance(data.get("stateLabels"), list) else []
    guard_labels = data.get("guardLabels") if isinstance(data.get("guardLabels"), list) else []
    system_labels = data.get("systemLabels") if isinstance(data.get("systemLabels"), list) else []
    tree_labels = data.get("treeLabels") if isinstance(data.get("treeLabels"), list) else []
    meter_labels = data.get("meterLabels") if isinstance(data.get("meterLabels"), list) else []
    route_labels = data.get("routeLabels") if isinstance(data.get("routeLabels"), list) else []
    checkpoint_labels = data.get("checkpointLabels") if isinstance(data.get("checkpointLabels"), list) else []
    phase_labels = data.get("phaseLabels") if isinstance(data.get("phaseLabels"), list) else []
    metric_labels = data.get("metricLabels") if isinstance(data.get("metricLabels"), list) else []
    threshold_labels = data.get("thresholdLabels") if isinstance(data.get("thresholdLabels"), list) else []
    dependency_labels = data.get("dependencyLabels") if isinstance(data.get("dependencyLabels"), list) else []
    cluster_labels = data.get("clusterLabels") if isinstance(data.get("clusterLabels"), list) else []
    trace_labels = data.get("traceLabels") if isinstance(data.get("traceLabels"), list) else []
    flow_labels = data.get("flowLabels") if isinstance(data.get("flowLabels"), list) else []
    lane_labels = data.get("laneLabels") if isinstance(data.get("laneLabels"), list) else []
    handoff_labels = data.get("handoffLabels") if isinstance(data.get("handoffLabels"), list) else []
    threat_labels = data.get("threatLabels") if isinstance(data.get("threatLabels"), list) else []
    barrier_labels = data.get("barrierLabels") if isinstance(data.get("barrierLabels"), list) else []
    consequence_labels = data.get("consequenceLabels") if isinstance(data.get("consequenceLabels"), list) else []
    scenario_labels = data.get("scenarioLabels") if isinstance(data.get("scenarioLabels"), list) else []
    probability_labels = data.get("probabilityLabels") if isinstance(data.get("probabilityLabels"), list) else []
    claim_labels = data.get("claimLabels") if isinstance(data.get("claimLabels"), list) else []
    evidence_labels = data.get("evidenceLabels") if isinstance(data.get("evidenceLabels"), list) else []
    layer_labels = data.get("layerLabels") if isinstance(data.get("layerLabels"), list) else []
    concern_labels = data.get("concernLabels") if isinstance(data.get("concernLabels"), list) else []
    lineage_labels = data.get("lineageLabels") if isinstance(data.get("lineageLabels"), list) else []
    quality_labels = data.get("qualityLabels") if isinstance(data.get("qualityLabels"), list) else []
    fact_set = {str(item) for item in source_facts}
    anchor_set = {str(item) for item in strategy_anchors}
    label_set = {str(item) for item in causal_labels}
    option_set = {str(item) for item in decision_options}
    criterion_set = {str(item) for item in decision_criteria}
    state_set = {str(item) for item in state_labels}
    guard_set = {str(item) for item in guard_labels}
    system_set = {str(item) for item in system_labels}
    tree_set = {str(item) for item in tree_labels}
    meter_set = {str(item) for item in meter_labels}
    route_set = {str(item) for item in route_labels}
    checkpoint_set = {str(item) for item in checkpoint_labels}
    phase_set = {str(item) for item in phase_labels}
    metric_set = {str(item) for item in metric_labels}
    threshold_set = {str(item) for item in threshold_labels}
    dependency_set = {str(item) for item in dependency_labels}
    cluster_set = {str(item) for item in cluster_labels}
    trace_set = {str(item) for item in trace_labels}
    flow_set = {str(item) for item in flow_labels}
    lane_set = {str(item) for item in lane_labels}
    handoff_set = {str(item) for item in handoff_labels}
    threat_set = {str(item) for item in threat_labels}
    barrier_set = {str(item) for item in barrier_labels}
    consequence_set = {str(item) for item in consequence_labels}
    scenario_set = {str(item) for item in scenario_labels}
    probability_set = {str(item) for item in probability_labels}
    claim_set = {str(item) for item in claim_labels}
    evidence_set = {str(item) for item in evidence_labels}
    layer_set = {str(item) for item in layer_labels}
    concern_set = {str(item) for item in concern_labels}
    lineage_set = {str(item) for item in lineage_labels}
    quality_set = {str(item) for item in quality_labels}
    missing_facts = [str(fact) for fact in contract["facts"] if str(fact) not in fact_set]
    missing_anchors = [str(anchor) for anchor in contract["anchors"] if str(anchor) not in anchor_set]
    missing_labels = [str(label) for label in contract.get("nodeLabels", []) if str(label) not in label_set]
    missing_options = [str(label) for label in contract.get("decisionOptions", []) if str(label) not in option_set]
    missing_criteria = [str(label) for label in contract.get("decisionCriteria", []) if str(label) not in criterion_set]
    missing_states = [str(label) for label in contract.get("stateLabels", []) if str(label) not in state_set]
    missing_guards = [str(label) for label in contract.get("guardLabels", []) if str(label) not in guard_set]
    missing_systems = [str(label) for label in contract.get("systemLabels", []) if str(label) not in system_set]
    missing_tree = [str(label) for label in contract.get("treeLabels", []) if str(label) not in tree_set]
    missing_meter = [str(label) for label in contract.get("meterLabels", []) if str(label) not in meter_set]
    missing_route = [str(label) for label in contract.get("routeLabels", []) if str(label) not in route_set]
    missing_checkpoint = [str(label) for label in contract.get("checkpointLabels", []) if str(label) not in checkpoint_set]
    missing_phase = [str(label) for label in contract.get("phaseLabels", []) if str(label) not in phase_set]
    missing_metric = [str(label) for label in contract.get("metricLabels", []) if str(label) not in metric_set]
    missing_threshold = [str(label) for label in contract.get("thresholdLabels", []) if str(label) not in threshold_set]
    missing_dependency = [str(label) for label in contract.get("dependencyLabels", []) if str(label) not in dependency_set]
    missing_cluster = [str(label) for label in contract.get("clusterLabels", []) if str(label) not in cluster_set]
    missing_trace = [str(label) for label in contract.get("traceLabels", []) if str(label) not in trace_set]
    missing_flow = [str(label) for label in contract.get("flowLabels", []) if str(label) not in flow_set]
    missing_lane = [str(label) for label in contract.get("laneLabels", []) if str(label) not in lane_set]
    missing_handoff = [str(label) for label in contract.get("handoffLabels", []) if str(label) not in handoff_set]
    missing_threat = [str(label) for label in contract.get("threatLabels", []) if str(label) not in threat_set]
    missing_barrier = [str(label) for label in contract.get("barrierLabels", []) if str(label) not in barrier_set]
    missing_consequence = [str(label) for label in contract.get("consequenceLabels", []) if str(label) not in consequence_set]
    missing_scenario = [str(label) for label in contract.get("scenarioLabels", []) if str(label) not in scenario_set]
    missing_probability = [str(label) for label in contract.get("probabilityLabels", []) if str(label) not in probability_set]
    missing_claim = [str(label) for label in contract.get("claimLabels", []) if str(label) not in claim_set]
    missing_evidence = [str(label) for label in contract.get("evidenceLabels", []) if str(label) not in evidence_set]
    missing_layer = [str(label) for label in contract.get("layerLabels", []) if str(label) not in layer_set]
    missing_concern = [str(label) for label in contract.get("concernLabels", []) if str(label) not in concern_set]
    missing_lineage = [str(label) for label in contract.get("lineageLabels", []) if str(label) not in lineage_set]
    missing_quality = [str(label) for label in contract.get("qualityLabels", []) if str(label) not in quality_set]
    report["actualFacts"] = len(source_facts)
    report["actualAnchors"] = len(strategy_anchors)
    report["actualNodeLabels"] = len(causal_labels)
    report["actualDecisionOptions"] = len(decision_options)
    report["actualDecisionCriteria"] = len(decision_criteria)
    report["actualStateLabels"] = len(state_labels)
    report["actualGuardLabels"] = len(guard_labels)
    report["actualSystemLabels"] = len(system_labels)
    report["actualTreeLabels"] = len(tree_labels)
    report["actualMeterLabels"] = len(meter_labels)
    report["actualRouteLabels"] = len(route_labels)
    report["actualCheckpointLabels"] = len(checkpoint_labels)
    report["actualPhaseLabels"] = len(phase_labels)
    report["actualMetricLabels"] = len(metric_labels)
    report["actualThresholdLabels"] = len(threshold_labels)
    report["actualDependencyLabels"] = len(dependency_labels)
    report["actualClusterLabels"] = len(cluster_labels)
    report["actualTraceLabels"] = len(trace_labels)
    report["actualFlowLabels"] = len(flow_labels)
    report["actualLaneLabels"] = len(lane_labels)
    report["actualHandoffLabels"] = len(handoff_labels)
    report["actualThreatLabels"] = len(threat_labels)
    report["actualBarrierLabels"] = len(barrier_labels)
    report["actualConsequenceLabels"] = len(consequence_labels)
    report["actualScenarioLabels"] = len(scenario_labels)
    report["actualProbabilityLabels"] = len(probability_labels)
    report["actualClaimLabels"] = len(claim_labels)
    report["actualEvidenceLabels"] = len(evidence_labels)
    report["actualLayerLabels"] = len(layer_labels)
    report["actualConcernLabels"] = len(concern_labels)
    report["actualLineageLabels"] = len(lineage_labels)
    report["actualQualityLabels"] = len(quality_labels)
    report["missingFacts"] = missing_facts
    report["missingAnchors"] = missing_anchors
    report["missingNodeLabels"] = missing_labels
    report["missingDecisionOptions"] = missing_options
    report["missingDecisionCriteria"] = missing_criteria
    report["missingStateLabels"] = missing_states
    report["missingGuardLabels"] = missing_guards
    report["missingSystemLabels"] = missing_systems
    report["missingTreeLabels"] = missing_tree
    report["missingMeterLabels"] = missing_meter
    report["missingRouteLabels"] = missing_route
    report["missingCheckpointLabels"] = missing_checkpoint
    report["missingPhaseLabels"] = missing_phase
    report["missingMetricLabels"] = missing_metric
    report["missingThresholdLabels"] = missing_threshold
    report["missingDependencyLabels"] = missing_dependency
    report["missingClusterLabels"] = missing_cluster
    report["missingTraceLabels"] = missing_trace
    report["missingFlowLabels"] = missing_flow
    report["missingLaneLabels"] = missing_lane
    report["missingHandoffLabels"] = missing_handoff
    report["missingThreatLabels"] = missing_threat
    report["missingBarrierLabels"] = missing_barrier
    report["missingConsequenceLabels"] = missing_consequence
    report["missingScenarioLabels"] = missing_scenario
    report["missingProbabilityLabels"] = missing_probability
    report["missingClaimLabels"] = missing_claim
    report["missingEvidenceLabels"] = missing_evidence
    report["missingLayerLabels"] = missing_layer
    report["missingConcernLabels"] = missing_concern
    report["missingLineageLabels"] = missing_lineage
    report["missingQualityLabels"] = missing_quality
    for fact in missing_facts:
        findings.append({"code": "missing-source-fact", "path": source_path.as_posix(), "message": fact})
    for anchor in missing_anchors:
        findings.append({"code": "missing-strategy-anchor", "path": source_path.as_posix(), "message": anchor})
    for label in missing_labels:
        findings.append({"code": "missing-causal-label", "path": source_path.as_posix(), "message": label})
    for label in missing_options:
        findings.append({"code": "missing-decision-option", "path": source_path.as_posix(), "message": label})
    for label in missing_criteria:
        findings.append({"code": "missing-decision-criterion", "path": source_path.as_posix(), "message": label})
    for label in missing_states:
        findings.append({"code": "missing-state-label", "path": source_path.as_posix(), "message": label})
    for label in missing_guards:
        findings.append({"code": "missing-guard-label", "path": source_path.as_posix(), "message": label})
    for label in missing_systems:
        findings.append({"code": "missing-system-label", "path": source_path.as_posix(), "message": label})
    for label in missing_tree:
        findings.append({"code": "missing-tree-label", "path": source_path.as_posix(), "message": label})
    for label in missing_meter:
        findings.append({"code": "missing-meter-label", "path": source_path.as_posix(), "message": label})
    for label in missing_route:
        findings.append({"code": "missing-route-label", "path": source_path.as_posix(), "message": label})
    for label in missing_checkpoint:
        findings.append({"code": "missing-checkpoint-label", "path": source_path.as_posix(), "message": label})
    for label in missing_phase:
        findings.append({"code": "missing-phase-label", "path": source_path.as_posix(), "message": label})
    for label in missing_metric:
        findings.append({"code": "missing-metric-label", "path": source_path.as_posix(), "message": label})
    for label in missing_threshold:
        findings.append({"code": "missing-threshold-label", "path": source_path.as_posix(), "message": label})
    for label in missing_dependency:
        findings.append({"code": "missing-dependency-label", "path": source_path.as_posix(), "message": label})
    for label in missing_cluster:
        findings.append({"code": "missing-cluster-label", "path": source_path.as_posix(), "message": label})
    for label in missing_trace:
        findings.append({"code": "missing-trace-label", "path": source_path.as_posix(), "message": label})
    for label in missing_flow:
        findings.append({"code": "missing-flow-label", "path": source_path.as_posix(), "message": label})
    for label in missing_lane:
        findings.append({"code": "missing-lane-label", "path": source_path.as_posix(), "message": label})
    for label in missing_handoff:
        findings.append({"code": "missing-handoff-label", "path": source_path.as_posix(), "message": label})
    for label in missing_threat:
        findings.append({"code": "missing-threat-label", "path": source_path.as_posix(), "message": label})
    for label in missing_barrier:
        findings.append({"code": "missing-barrier-label", "path": source_path.as_posix(), "message": label})
    for label in missing_consequence:
        findings.append({"code": "missing-consequence-label", "path": source_path.as_posix(), "message": label})
    for label in missing_scenario:
        findings.append({"code": "missing-scenario-label", "path": source_path.as_posix(), "message": label})
    for label in missing_probability:
        findings.append({"code": "missing-probability-label", "path": source_path.as_posix(), "message": label})
    for label in missing_claim:
        findings.append({"code": "missing-claim-label", "path": source_path.as_posix(), "message": label})
    for label in missing_evidence:
        findings.append({"code": "missing-evidence-label", "path": source_path.as_posix(), "message": label})
    for label in missing_layer:
        findings.append({"code": "missing-layer-label", "path": source_path.as_posix(), "message": label})
    for label in missing_concern:
        findings.append({"code": "missing-concern-label", "path": source_path.as_posix(), "message": label})
    for label in missing_lineage:
        findings.append({"code": "missing-lineage-label", "path": source_path.as_posix(), "message": label})
    for label in missing_quality:
        findings.append({"code": "missing-quality-label", "path": source_path.as_posix(), "message": label})
    return report


def probe_video(video: Path) -> dict[str, object]:
    exe = shutil.which("ffprobe")
    if not exe:
        raise RuntimeError("ffprobe is required for media checks but was not found on PATH.")
    result = subprocess.run(
        [
            exe,
            "-v",
            "error",
            "-select_streams",
            "v:0",
            "-show_entries",
            "stream=width,height,r_frame_rate,duration",
            "-show_entries",
            "format=duration",
            "-of",
            "json",
            str(video),
        ],
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "ffprobe failed.")
    return json.loads(result.stdout)


def rational_to_float(value: object) -> float | None:
    if not isinstance(value, str) or not value:
        return None
    try:
        return float(Fraction(value))
    except (ValueError, ZeroDivisionError):
        return None


def verify_media(contract: dict[str, object], findings: list[dict[str, object]]) -> dict[str, object]:
    expected = {
        "duration": float(contract["duration"]),
        "fps": float(contract["fps"]),
        "width": int(contract["width"]),
        "height": int(contract["height"]),
    }
    video_paths = [
        Path(str(raw))
        for raw in contract["requiredPaths"]
        if Path(str(raw)).suffix.lower() in {".mp4", ".webm", ".mov", ".m4v"}
    ]
    media: dict[str, object] = {"expected": expected, "checked": None, "actual": None}
    if len(video_paths) != 1:
        findings.append({
            "code": "media-video-path-count",
            "path": "requiredPaths",
            "message": f"Expected one video path for media checks, got {len(video_paths)}.",
        })
        return media
    video = video_paths[0]
    media["checked"] = video.as_posix()
    if not video.exists():
        return media
    try:
        data = probe_video(video)
    except RuntimeError as exc:
        findings.append({"code": "media-probe-failed", "path": video.as_posix(), "message": str(exc)})
        return media
    stream = (data.get("streams") or [{}])[0]
    fmt = data.get("format") if isinstance(data.get("format"), dict) else {}
    actual_duration = float(fmt.get("duration") or stream.get("duration") or 0)
    actual_fps = rational_to_float(stream.get("r_frame_rate"))
    actual = {
        "duration": actual_duration,
        "fps": actual_fps,
        "width": stream.get("width"),
        "height": stream.get("height"),
    }
    media["actual"] = actual
    if abs(actual_duration - expected["duration"]) > 0.5:
        findings.append({
            "code": "media-duration-mismatch",
            "path": video.as_posix(),
            "message": f"Expected about {expected['duration']}s, got {actual_duration:.3f}s.",
        })
    if actual_fps is None or abs(actual_fps - expected["fps"]) > 0.2:
        findings.append({
            "code": "media-fps-mismatch",
            "path": video.as_posix(),
            "message": f"Expected about {expected['fps']} fps, got {actual_fps}.",
        })
    if actual["width"] != expected["width"]:
        findings.append({
            "code": "media-width-mismatch",
            "path": video.as_posix(),
            "message": f"Expected width {expected['width']}, got {actual['width']}.",
        })
    if actual["height"] != expected["height"]:
        findings.append({
            "code": "media-height-mismatch",
            "path": video.as_posix(),
            "message": f"Expected height {expected['height']}, got {actual['height']}.",
        })
    return media


def run_state_check(contract: dict[str, object], args: argparse.Namespace, findings: list[dict[str, object]]) -> dict[str, object] | None:
    if not args.state_manifest:
        return None
    uv = shutil.which("uv")
    if not uv:
        findings.append({"code": "state-check-uv-missing", "path": args.state_manifest.as_posix(), "message": "uv is required for render-state checks."})
        return {"ran": False, "manifest": args.state_manifest.as_posix(), "passed": False}
    script = Path(__file__).with_name("check_html_render_state.py")
    html = Path(str(contract["projectRoot"])) / "src" / "index.html"
    cmd = [
        uv,
        "run",
        "--script",
        str(script),
        "--html",
        html.as_posix(),
        "--video-id",
        str(contract["outputId"]),
        "--duration",
        str(contract["duration"]),
        "--samples",
        str(args.state_samples),
        "--width",
        str(contract["width"]),
        "--height",
        str(contract["height"]),
        "--manifest",
        args.state_manifest.as_posix(),
    ]
    for item in args.state_expect:
        cmd.extend(["--expect-state", str(item)])
    for item in args.state_expect_final:
        cmd.extend(["--expect-state-final", str(item)])
    for item in args.state_expect_contains:
        cmd.extend(["--expect-state-contains", str(item)])
    for item in args.state_expect_transition:
        cmd.extend(["--expect-state-transition", str(item)])
    for item in args.state_expect_monotonic:
        cmd.extend(["--expect-state-monotonic", str(item)])
    for item in args.state_min_distinct:
        cmd.extend(["--min-distinct-state", str(item)])
    result = subprocess.run(cmd, text=True, capture_output=True, check=False)
    report: dict[str, object] = {
        "ran": True,
        "manifest": args.state_manifest.as_posix(),
        "command": cmd,
        "returnCode": result.returncode,
        "stdoutTail": result.stdout[-1000:],
        "stderrTail": result.stderr[-1000:],
        "passed": result.returncode == 0,
    }
    if args.state_manifest.exists():
        try:
            state_data = json.loads(args.state_manifest.read_text(encoding="utf-8"))
            report["manifestPassed"] = state_data.get("passed")
            report["stateSummary"] = state_data.get("stateSummary")
            report["stateFindings"] = state_data.get("findings")
        except json.JSONDecodeError as exc:
            report["manifestReadError"] = str(exc)
    if result.returncode != 0:
        findings.append({
            "code": "state-check-failed",
            "path": args.state_manifest.as_posix(),
            "message": f"Render-state checker exited {result.returncode}.",
        })
    return report


def run_metro_audit_suite(
    contract: dict[str, object],
    *,
    style_manifest: Path | None,
    composition_manifest: Path | None,
    rendered_frame_manifest: Path | None,
    mute_test_manifest: Path | None,
    suite_manifest: Path | None,
    findings: list[dict[str, object]],
) -> dict[str, object] | None:
    if not any([style_manifest, composition_manifest, rendered_frame_manifest, mute_test_manifest, suite_manifest]):
        return None
    default_dir = (
        suite_manifest.parent
        if suite_manifest
        else next(
            path.parent
            for path in (style_manifest, composition_manifest, rendered_frame_manifest, mute_test_manifest)
            if path is not None
        )
    )
    style_manifest = style_manifest or default_dir / "metro-style-audit.json"
    composition_manifest = composition_manifest or default_dir / "metro-composition-audit.json"
    rendered_frame_manifest = rendered_frame_manifest or default_dir / "metro-rendered-frame-audit.json"
    mute_test_manifest = mute_test_manifest or default_dir / "metro-mute-test-audit.json"
    suite_manifest = suite_manifest or default_dir / "metro-audit-suite.json"
    uv = shutil.which("uv")
    if not uv:
        findings.append({"code": "metro-audit-suite-uv-missing", "path": "", "message": "uv is required for audit checks."})
        return {"ran": False, "passed": False}
    script = Path(__file__).with_name("run_metro_audit_suite.py")
    root = Path(str(contract["projectRoot"]))
    html = root / "src" / "index.html"
    source_package = root / "source" / "source-package.json"
    cmd = [
        uv,
        "run",
        "--script",
        str(script),
        "--html",
        html.as_posix(),
        "--source-package",
        source_package.as_posix(),
    ]
    cmd.extend(["--style-output", style_manifest.as_posix()])
    cmd.extend(["--composition-output", composition_manifest.as_posix()])
    cmd.extend(["--rendered-frame-output", rendered_frame_manifest.as_posix()])
    cmd.extend(["--mute-test-output", mute_test_manifest.as_posix()])
    cmd.extend(["--output", suite_manifest.as_posix()])
    cmd.append("--no-install-browser")
    cmd.extend(["--audit-timeout-seconds", "240"])
    cmd.extend(["--mute-test-samples", "4"])
    suite_start_time = time.time()
    try:
        result = subprocess.run(cmd, text=True, capture_output=True, check=False, timeout=360)
    except subprocess.TimeoutExpired as exc:
        report = {
            "ran": True,
            "manifest": suite_manifest.as_posix() if suite_manifest else None,
            "command": cmd,
            "returnCode": None,
            "stdoutTail": (exc.stdout or "")[-1000:] if isinstance(exc.stdout, str) else "",
            "stderrTail": (exc.stderr or "")[-1000:] if isinstance(exc.stderr, str) else "",
            "timedOut": True,
            "passed": False,
        }
        if suite_manifest and suite_manifest.exists():
            try:
                loaded = json.loads(suite_manifest.read_text(encoding="utf-8"))
                manifest_is_fresh = suite_manifest.stat().st_mtime >= suite_start_time - 1.0
                if isinstance(loaded, dict):
                    report["manifestPassed"] = loaded.get("passed")
                    report["manifestFresh"] = manifest_is_fresh
                    report["findings"] = loaded.get("findings")
                    report["styleAudit"] = loaded.get("styleAudit")
                    report["compositionAudit"] = loaded.get("compositionAudit")
                    report["renderedFrameAudit"] = loaded.get("renderedFrameAudit")
                    report["muteTestAudit"] = loaded.get("muteTestAudit")
                    if manifest_is_fresh and loaded.get("passed") is True:
                        report["passed"] = True
                        report["acceptedFreshManifestAfterTimeout"] = True
                        return report
            except (json.JSONDecodeError, OSError) as manifest_exc:
                report["manifestReadError"] = str(manifest_exc)
        findings.append(
            {
                "code": "metro-audit-suite-timeout",
                "path": suite_manifest.as_posix() if suite_manifest else "",
                "message": "run_metro_audit_suite.py exceeded the wrapper timeout.",
            }
        )
        return report
    report: dict[str, object] = {
        "ran": True,
        "manifest": suite_manifest.as_posix() if suite_manifest else None,
        "command": cmd,
        "returnCode": result.returncode,
        "stdoutTail": result.stdout[-1000:],
        "stderrTail": result.stderr[-1000:],
        "passed": result.returncode == 0,
    }
    data: dict[str, object] | None = None
    if suite_manifest and suite_manifest.exists():
        try:
            loaded = json.loads(suite_manifest.read_text(encoding="utf-8"))
            if isinstance(loaded, dict):
                data = loaded
                report["manifestPassed"] = loaded.get("passed")
                report["findings"] = loaded.get("findings")
                report["styleAudit"] = loaded.get("styleAudit")
                report["compositionAudit"] = loaded.get("compositionAudit")
                report["renderedFrameAudit"] = loaded.get("renderedFrameAudit")
                report["muteTestAudit"] = loaded.get("muteTestAudit")
                report["passed"] = result.returncode == 0 and loaded.get("passed") is True
            else:
                report["manifestReadError"] = "Suite manifest root is not an object."
                report["passed"] = False
        except json.JSONDecodeError as exc:
            report["manifestReadError"] = str(exc)
            report["passed"] = False
    if data is None and result.stdout.strip():
        try:
            loaded = json.loads(result.stdout)
            if isinstance(loaded, dict):
                data = loaded
                report["styleAudit"] = loaded.get("styleAudit")
                report["compositionAudit"] = loaded.get("compositionAudit")
                report["renderedFrameAudit"] = loaded.get("renderedFrameAudit")
                report["muteTestAudit"] = loaded.get("muteTestAudit")
                report["findings"] = loaded.get("findings")
                report["passed"] = result.returncode == 0 and loaded.get("passed") is True
        except json.JSONDecodeError:
            pass
    if result.returncode != 0 or report.get("passed") is not True:
        findings.append(
            {
                "code": "metro-audit-suite-failed",
                "path": suite_manifest.as_posix() if suite_manifest else "",
                "message": f"run_metro_audit_suite.py exited {result.returncode}.",
            }
        )
    return report


def run_metro_video_composition_audit(
    contract: dict[str, object],
    *,
    manifest: Path | None,
    findings: list[dict[str, object]],
) -> dict[str, object] | None:
    if not manifest:
        return None
    uv = shutil.which("uv")
    if not uv:
        findings.append({"code": "metro-video-composition-uv-missing", "path": manifest.as_posix(), "message": "uv is required for MP4 composition checks."})
        return {"ran": False, "manifest": manifest.as_posix(), "passed": False}
    script = Path(__file__).with_name("audit_metro_video_composition.py")
    video = (
        Path(str(contract["projectRoot"]))
        / "artifacts"
        / "video-renders"
        / "draft"
        / "videos"
        / f"{contract['outputId']}.mp4"
    )
    cmd = [
        uv,
        "run",
        "--script",
        str(script),
        "--video",
        video.as_posix(),
        "--report",
        manifest.as_posix(),
    ]
    result = subprocess.run(cmd, text=True, capture_output=True, check=False)
    report: dict[str, object] = {
        "ran": True,
        "manifest": manifest.as_posix(),
        "command": cmd,
        "returnCode": result.returncode,
        "stdoutTail": result.stdout[-1000:],
        "stderrTail": result.stderr[-1000:],
        "passed": result.returncode == 0,
    }
    if manifest.exists():
        try:
            loaded = json.loads(manifest.read_text(encoding="utf-8"))
            if isinstance(loaded, dict):
                report["manifestPassed"] = loaded.get("passed")
                report["summary"] = loaded.get("summary")
                report["findings"] = loaded.get("findings")
                report["passed"] = result.returncode == 0 and loaded.get("passed") is True
            else:
                report["manifestReadError"] = "MP4 composition manifest root is not an object."
                report["passed"] = False
        except json.JSONDecodeError as exc:
            report["manifestReadError"] = str(exc)
            report["passed"] = False
    if report.get("passed") is not True:
        findings.append(
            {
                "code": "metro-video-composition-audit-failed",
                "path": manifest.as_posix(),
                "message": f"audit_metro_video_composition.py exited {result.returncode}.",
            }
        )
    return report


def compact_audit_report(report: object) -> object:
    if not isinstance(report, dict):
        return report
    keys = [
        "ran",
        "code",
        "manifest",
        "returnCode",
        "passed",
        "manifestPassed",
        "findings",
        "manifestMissing",
        "manifestReadError",
        "timedOut",
    ]
    compact = {key: report[key] for key in keys if key in report}
    if report.get("passed") is not True:
        for key in ("command", "stdoutTail", "stderrTail"):
            if key in report:
                compact[key] = report[key]
    return compact


def compact_metro_audit_suite(report: object) -> object:
    if not isinstance(report, dict):
        return report
    compact = compact_audit_report(report)
    if not isinstance(compact, dict):
        return compact
    for source_key, target_key in (
        ("styleAudit", "styleAudit"),
        ("compositionAudit", "compositionAudit"),
        ("renderedFrameAudit", "renderedFrameAudit"),
        ("muteTestAudit", "muteTestAudit"),
    ):
        if source_key in report:
            compact[target_key] = compact_audit_report(report[source_key])
    return compact


def prompt_requires_metro_audits(prompt_text: str) -> bool:
    lowered = prompt_text.lower()
    triggers = [
        "metro",
        "hard-edge",
        "hard edge",
        "square-edge",
        "square edge",
        "strict-grid",
        "strict grid",
        "no padding",
        "zero padding",
        "without padding",
        "sin padding",
        "grayscale",
        "grey scale",
        "gray scale",
        "gray levels",
        "grayscale levels",
        "niveles de grises",
        "megacanvas",
        "masonry",
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
        "bordes no deben tener redondeo",
        "no-rounded",
        "0-radius",
    ]
    return any(trigger in lowered for trigger in triggers)


def default_review_manifest(contract: dict[str, object], filename: str) -> Path:
    return Path(str(contract["projectRoot"])) / "artifacts" / "reviews" / filename


def main() -> int:
    args = parse_args()
    prompt_text = read_prompt(args.prompt)
    manifest_path = args.manifest or extract_manifest_path(prompt_text)
    contract = derived_contract(prompt_text)
    metro_pattern_mix = derive_metro_pattern_mix(prompt_text, contract)
    if isinstance(metro_pattern_mix, dict):
        masonry_contract = metro_pattern_mix.get("masonryContract")
        if isinstance(masonry_contract, dict) and masonry_contract.get("required") is True:
            contract["masonryLayoutRequired"] = True
    metro_style_manifest = args.metro_style_manifest or extract_named_json_path(prompt_text, ["metro-style-audit", "style audit", "tonal audit"])
    metro_composition_manifest = args.metro_composition_manifest or extract_named_json_path(prompt_text, ["metro-composition-audit", "composition audit", "metro composition"])
    metro_rendered_frame_manifest = args.metro_rendered_frame_manifest or extract_named_json_path(
        prompt_text,
        ["metro-rendered-frame-audit", "rendered-frame audit", "rendered frame audit", "frame audit"],
    )
    metro_mute_test_manifest = args.metro_mute_test_manifest or extract_named_json_path(
        prompt_text,
        ["metro-mute-test-audit", "mute-test audit", "mute test audit", "text-dependence audit", "text dependence audit"],
    )
    metro_audit_suite_manifest = args.metro_audit_suite_manifest or extract_named_json_path(
        prompt_text,
        ["metro-audit-suite", "metro audit suite", "audit suite"],
    )
    metro_video_composition_manifest = args.metro_video_composition_manifest or extract_named_json_path(
        prompt_text,
        ["metro-video-composition-audit", "video composition audit", "mp4 composition audit"],
    )
    if prompt_requires_metro_audits(prompt_text):
        metro_style_manifest = metro_style_manifest or default_review_manifest(contract, "metro-style-audit.json")
        metro_composition_manifest = metro_composition_manifest or default_review_manifest(contract, "metro-composition-audit.json")
        metro_rendered_frame_manifest = metro_rendered_frame_manifest or default_review_manifest(contract, "metro-rendered-frame-audit.json")
        metro_mute_test_manifest = metro_mute_test_manifest or default_review_manifest(contract, "metro-mute-test-audit.json")
        metro_audit_suite_manifest = metro_audit_suite_manifest or default_review_manifest(contract, "metro-audit-suite.json")
        metro_video_composition_manifest = metro_video_composition_manifest or default_review_manifest(contract, "metro-video-composition-audit.json")
    configure_state_defaults(args, prompt_text, contract)
    cmd = build_command(contract)
    result_info: dict[str, object] = {
        "prompt": args.prompt.as_posix(),
        "contract": contract,
        "manifest": manifest_path.as_posix() if manifest_path else None,
        "metroStyleManifest": metro_style_manifest.as_posix() if metro_style_manifest else None,
        "metroCompositionManifest": metro_composition_manifest.as_posix() if metro_composition_manifest else None,
        "metroRenderedFrameManifest": metro_rendered_frame_manifest.as_posix() if metro_rendered_frame_manifest else None,
        "metroMuteTestManifest": metro_mute_test_manifest.as_posix() if metro_mute_test_manifest else None,
        "metroAuditSuiteManifest": metro_audit_suite_manifest.as_posix() if metro_audit_suite_manifest else None,
        "metroVideoCompositionManifest": metro_video_composition_manifest.as_posix() if metro_video_composition_manifest else None,
        "metroPatternMix": compact_metro_pattern_mix(metro_pattern_mix),
        "command": cmd,
        "ran": not args.dry_run,
        "findings": [],
        "passed": False,
    }
    if args.dry_run:
        result_info["passed"] = True
    else:
        result = subprocess.run(cmd, text=True, capture_output=True, check=False)
        result_info["returnCode"] = result.returncode
        result_info["stdoutTail"] = result.stdout[-4000:]
        result_info["stderrTail"] = result.stderr[-4000:]
        findings: list[dict[str, object]] = []
        if isinstance(metro_pattern_mix, dict) and metro_pattern_mix.get("passed") is not True:
            findings.append({
                "code": "metro-pattern-mix-failed",
                "path": PATTERN_MIX_SCRIPT.name,
                "message": "Metro pattern mix did not satisfy pattern, zone, motion, camera, or anchor requirements.",
            })
        metro_suite = run_metro_audit_suite(
            contract,
            style_manifest=metro_style_manifest,
            composition_manifest=metro_composition_manifest,
            rendered_frame_manifest=metro_rendered_frame_manifest,
            mute_test_manifest=metro_mute_test_manifest,
            suite_manifest=metro_audit_suite_manifest,
            findings=findings,
        )
        result_info["metroAuditSuite"] = compact_metro_audit_suite(metro_suite)
        result_info["metroStyleAudit"] = (
            compact_audit_report(metro_suite.get("styleAudit"))
            if isinstance(metro_suite, dict)
            else None
        )
        result_info["metroCompositionAudit"] = (
            compact_audit_report(metro_suite.get("compositionAudit"))
            if isinstance(metro_suite, dict)
            else None
        )
        result_info["metroRenderedFrameAudit"] = (
            compact_audit_report(metro_suite.get("renderedFrameAudit"))
            if isinstance(metro_suite, dict)
            else None
        )
        result_info["metroMuteTestAudit"] = (
            compact_audit_report(metro_suite.get("muteTestAudit"))
            if isinstance(metro_suite, dict)
            else None
        )
        result_info["metroVideoCompositionAudit"] = compact_audit_report(
            run_metro_video_composition_audit(
                contract,
                manifest=metro_video_composition_manifest,
                findings=findings,
            )
        )
        result_info["stateCheck"] = run_state_check(contract, args, findings)
        findings.extend(verify_outputs(contract, manifest_path))
        result_info["sourcePreservation"] = verify_source_preservation(contract, findings)
        result_info["media"] = verify_media(contract, findings)
        contact_summary = summarize_contact_sheet(contract)
        result_info["contactSheet"] = contact_summary
        opening_assessment = (
            contact_summary.get("openingTileAssessment")
            if isinstance(contact_summary.get("openingTileAssessment"), dict)
            else {}
        )
        if opening_assessment.get("weak") is True:
            findings.append({
                "code": "weak-opening-tile",
                "path": str(contact_summary.get("checked")),
                "message": f"Opening tile assessment failed: {', '.join(str(flag) for flag in opening_assessment.get('flags', [])) or 'weak opening tile'}.",
            })
        if result.returncode != 0:
            findings.append({"code": "builder-failed", "path": str(args.prompt), "message": f"Builder exited {result.returncode}."})
        result_info["findings"] = findings
        result_info["passed"] = not findings
    if manifest_path:
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        manifest_path.write_text(json.dumps(result_info, indent=2), encoding="utf-8")
    print(json.dumps(result_info, indent=2))
    return 0 if result_info["passed"] else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"build_from_prompt_contract.py: {exc}", file=sys.stderr)
        raise SystemExit(2)
