#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parents[1]


PATTERNS = [
    {"pattern": "skill-tree", "states": ["routeCount", "keystoneVisible", "atlasVisible"], "labels": [("treeLabels", "tree nodes", "--tree-label"), ("meterLabels", "strategy meters", "--meter-label")]},
    {"pattern": "skill-tree-route", "states": ["activeRouteNodeCount", "damageClusterVisible", "lateClusterVisible"], "labels": [("routeLabels", "route labels", "--route-label"), ("checkpointLabels", "checkpoint labels", "--checkpoint-label")]},
    {"pattern": "systems-flow", "states": ["queueSlots", "retryVisible", "deadLetterVisible", "feedbackVisible"], "labels": [("systemLabels", "system components", "--system-label")]},
    {"pattern": "state-machine", "states": ["activeState", "rollbackVisible", "compensationVisible", "terminalVisible"], "labels": [("stateLabels", "lifecycle states", "--state-label"), ("guardLabels", "transition guards", "--guard-label")]},
    {"pattern": "comparison-matrix", "states": ["criteriaRevealed", "recommendationVisible", "guardrailVisible"], "labels": [("decisionOptions", "decision options", "--option-label"), ("decisionCriteria", "decision criteria", "--criterion-label")]},
    {"pattern": "causal-loop", "states": ["loopVisible", "sideEffectVisible", "interventionVisible"], "labels": [("causalLabels", "causal variables", "--node-label", "NodeLabels")]},
    {"pattern": "phase-timeline", "states": ["activePhase", "riskVisible", "handoffVisible"], "labels": [("phaseLabels", "timeline phases", "--phase-label")]},
    {"pattern": "metric-dashboard", "states": ["trendVisible", "thresholdVisible", "forecastVisible"], "labels": [("metricLabels", "metric labels", "--metric-label"), ("thresholdLabels", "threshold labels", "--threshold-label")]},
    {"pattern": "dependency-map", "states": ["edgeCount", "bottleneckVisible", "cutoverVisible"], "labels": [("dependencyLabels", "dependency labels", "--dependency-label"), ("clusterLabels", "dependency clusters", "--cluster-label")]},
    {"pattern": "sequence-trace", "states": ["activeSpanCount", "criticalPathVisible", "responseVisible"], "labels": [("traceLabels", "trace labels", "--trace-label")]},
    {"pattern": "sankey-flow", "states": ["activeFlowCount", "splitVisible", "outputVisible"], "labels": [("flowLabels", "flow labels", "--flow-label")]},
    {"pattern": "swimlane-handoff", "states": ["activeHandoffCount", "slaVisible", "completeVisible"], "labels": [("laneLabels", "lane labels", "--lane-label"), ("handoffLabels", "handoff labels", "--handoff-label")]},
    {"pattern": "risk-bowtie", "states": ["activeThreatCount", "preventiveVisible", "actionVisible"], "labels": [("threatLabels", "threat labels", "--threat-label"), ("barrierLabels", "barrier labels", "--barrier-label"), ("consequenceLabels", "consequence labels", "--consequence-label")]},
    {"pattern": "scenario-tree", "states": ["activeScenarioCount", "probabilityVisible", "outcomeVisible"], "labels": [("scenarioLabels", "scenario labels", "--scenario-label"), ("probabilityLabels", "probability labels", "--probability-label")]},
    {"pattern": "evidence-ladder", "states": ["activeEvidenceCount", "counterEvidenceVisible", "recommendationVisible"], "labels": [("claimLabels", "claim labels", "--claim-label"), ("evidenceLabels", "evidence labels", "--evidence-label")]},
    {"pattern": "layered-architecture", "states": ["activeLayerCount", "crossCuttingVisible", "rolloutVisible"], "labels": [("layerLabels", "layer labels", "--layer-label"), ("concernLabels", "concern labels", "--concern-label")]},
    {"pattern": "data-lineage", "states": ["activeLineageCount", "qualityGateVisible", "rollbackVisible"], "labels": [("lineageLabels", "lineage labels", "--lineage-label"), ("qualityLabels", "quality labels", "--quality-label")]},
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Check standalone helper pattern wiring across scripts and references.")
    parser.add_argument("--output", type=Path, help="Optional JSON report path.")
    return parser.parse_args()


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def display_key(source_key: str) -> str:
    return source_key[0].upper() + source_key[1:]


def add_finding(findings: list[dict[str, str]], pattern: str, code: str, path: str, token: str) -> None:
    findings.append({"pattern": pattern, "code": code, "path": path, "token": token})


def python_function_block(source: str, function_name: str) -> str:
    match = re.search(rf"^def {re.escape(function_name)}\(", source, flags=re.MULTILINE)
    if not match:
        return ""
    next_match = re.search(r"^def \w+\(", source[match.end() :], flags=re.MULTILINE)
    end = match.end() + next_match.start() if next_match else len(source)
    return source[match.start() : end]


def js_visual_pattern_block(source: str, pattern: str) -> str:
    marker = f'if (PACKAGE.visualPattern === "{pattern}")'
    start = source.find(marker)
    if start < 0:
        return ""
    next_match = re.search(r'\n      if \(PACKAGE\.visualPattern === "', source[start + len(marker) :])
    end = start + len(marker) + next_match.start() if next_match else len(source)
    return source[start:end]


def main() -> int:
    args = parse_args()
    helper_path = SKILL_DIR / "scripts" / "build_standalone_explainer.py"
    wrapper_path = SKILL_DIR / "scripts" / "build_from_prompt_contract.py"
    audit_suite_path = SKILL_DIR / "scripts" / "run_metro_audit_suite.py"
    tonal_audit_path = SKILL_DIR / "scripts" / "audit_metro_tonal_style.py"
    video_composition_audit_path = SKILL_DIR / "scripts" / "audit_metro_video_composition.py"
    composition_audit_path = SKILL_DIR / "scripts" / "audit_metro_composition.py"
    rendered_frame_audit_path = SKILL_DIR / "scripts" / "audit_metro_rendered_frames.py"
    semantic_density_path = SKILL_DIR / "scripts" / "audit_metro_semantic_density.py"
    audit_fixture_path = SKILL_DIR / "scripts" / "validate_metro_audit_fixtures.py"
    pattern_smoke_path = SKILL_DIR / "scripts" / "validate_metro_pattern_smoke.py"
    pattern_mix_path = SKILL_DIR / "scripts" / "plan_metro_pattern_mix.py"
    series_plan_path = SKILL_DIR / "scripts" / "plan_metro_video_series.py"
    series_contract_path = SKILL_DIR / "scripts" / "build_metro_series_contract_prompts.py"
    skill_path = SKILL_DIR / "SKILL.md"
    contract_path = SKILL_DIR / "references" / "standalone-helper-contract.md"
    loop_path = SKILL_DIR / "references" / "production-loop.md"
    density_path = SKILL_DIR / "references" / "visual-density-pattern-bank.md"
    helper = read(helper_path)
    wrapper = read(wrapper_path)
    audit_suite = read(audit_suite_path)
    tonal_audit = read(tonal_audit_path)
    video_composition_audit = read(video_composition_audit_path)
    composition_audit = read(composition_audit_path)
    rendered_frame_audit = read(rendered_frame_audit_path)
    semantic_density = read(semantic_density_path)
    audit_fixture = read(audit_fixture_path)
    pattern_smoke = read(pattern_smoke_path)
    pattern_mix = read(pattern_mix_path)
    series_plan = read(series_plan_path)
    series_contract = read(series_contract_path)
    skill = read(skill_path)
    contract = read(contract_path)
    loop = read(loop_path)
    density = read(density_path)
    combined_docs = "\n".join([skill, contract, loop, density])
    findings: list[dict[str, str]] = []

    for item in PATTERNS:
        pattern = str(item["pattern"])
        if f'"{pattern}"' not in helper:
            add_finding(findings, pattern, "missing-helper-pattern", helper_path.as_posix(), pattern)
        if f'"{pattern}"' not in wrapper:
            add_finding(findings, pattern, "missing-wrapper-pattern", wrapper_path.as_posix(), pattern)
        if f"--pattern {pattern}" not in combined_docs and f"`{pattern}`" not in combined_docs:
            add_finding(findings, pattern, "missing-doc-pattern", "skill-docs", pattern)
        if pattern != "skill-tree" and f'PACKAGE.visualPattern === "{pattern}"' not in helper:
            add_finding(findings, pattern, "missing-html-render-branch", helper_path.as_posix(), pattern)
        if pattern != "skill-tree" and not re.search(rf"if pattern == \"{re.escape(pattern)}\"", helper):
            add_finding(findings, pattern, "missing-pillow-render-branch", helper_path.as_posix(), pattern)
        for state_key in item["states"]:
            if state_key not in helper:
                add_finding(findings, pattern, "missing-helper-state", helper_path.as_posix(), state_key)
            if state_key not in wrapper:
                add_finding(findings, pattern, "missing-wrapper-state-default", wrapper_path.as_posix(), state_key)
        for label_item in item["labels"]:
            source_key, heading, flag = label_item[:3]
            key_suffix = label_item[3] if len(label_item) > 3 else display_key(source_key)
            if source_key not in helper:
                add_finding(findings, pattern, "missing-helper-label-key", helper_path.as_posix(), source_key)
            if source_key not in wrapper:
                add_finding(findings, pattern, "missing-wrapper-label-key", wrapper_path.as_posix(), source_key)
            if flag not in helper or flag not in wrapper:
                add_finding(findings, pattern, "missing-label-flag", "helper-or-wrapper", flag)
            if f"Preserve these {heading}" not in wrapper:
                add_finding(findings, pattern, "missing-wrapper-heading", wrapper_path.as_posix(), heading)
            if f"Preserve these {heading}" not in contract:
                add_finding(findings, pattern, "missing-contract-heading", contract_path.as_posix(), heading)
            for prefix in ("expected", "actual", "missing"):
                token = f"{prefix}{key_suffix}"
                if token not in wrapper:
                    add_finding(findings, pattern, "missing-source-preservation-field", wrapper_path.as_posix(), token)

    policy_checks = [
        ("global", "missing-helper-zero-padding-policy", helper_path.as_posix(), "BOX_PADDING_POLICY"),
        ("global", "missing-helper-gray-levels", helper_path.as_posix(), "GRAY_LEVELS"),
        ("global", "missing-helper-zero-padding-normalizer", helper_path.as_posix(), "normalize_html_zero_padding_rects"),
        ("global", "missing-helper-runtime-rect-normalizer", helper_path.as_posix(), "normalizeSvgAttrs"),
        ("global", "missing-helper-runtime-grid-snap", helper_path.as_posix(), "snapToGrid"),
        ("global", "missing-helper-gray-level-metadata", helper_path.as_posix(), "data-gray-levels"),
        ("global", "missing-helper-zero-padding-geometry-hooks", helper_path.as_posix(), "data-fill-for"),
        ("global", "missing-helper-visual-zones", helper_path.as_posix(), "visualZones"),
        ("global", "missing-helper-zone-dom-id", helper_path.as_posix(), "data-zone-id"),
        ("global", "missing-helper-zone-dom-role", helper_path.as_posix(), "data-zone-role"),
        ("global", "missing-helper-visible-zone-state", helper_path.as_posix(), "visibleZoneCount"),
        ("global", "missing-helper-active-zone-state", helper_path.as_posix(), "activeZoneId"),
        ("global", "missing-helper-semantic-bindings", helper_path.as_posix(), "semanticBindings"),
        ("global", "missing-helper-source-anchor-coverage", helper_path.as_posix(), "sourceAnchorCoverage"),
        ("global", "missing-helper-dom-source-anchor", helper_path.as_posix(), "data-source-anchor"),
        ("global", "missing-helper-dom-source-anchor-json", helper_path.as_posix(), "data-source-anchor-json"),
        ("global", "missing-helper-active-source-anchors", helper_path.as_posix(), "activeSourceAnchors"),
        ("global", "missing-helper-layer-gray-fills", helper_path.as_posix(), "layer_gray_fills"),
        ("global", "missing-html-layer-gray-fills", helper_path.as_posix(), "layerGrayFills"),
        ("global", "missing-wrapper-auto-metro-audits", wrapper_path.as_posix(), "prompt_requires_metro_audits"),
        ("global", "missing-wrapper-default-style-audit", wrapper_path.as_posix(), "metro-style-audit.json"),
        ("global", "missing-wrapper-default-composition-audit", wrapper_path.as_posix(), "metro-composition-audit.json"),
        ("global", "missing-wrapper-default-rendered-frame-audit", wrapper_path.as_posix(), "metro-rendered-frame-audit.json"),
        ("global", "missing-wrapper-default-audit-suite", wrapper_path.as_posix(), "metro-audit-suite.json"),
        ("global", "missing-wrapper-default-video-composition-audit", wrapper_path.as_posix(), "metro-video-composition-audit.json"),
        ("global", "missing-wrapper-metro-audit-suite", wrapper_path.as_posix(), "run_metro_audit_suite"),
        ("global", "missing-wrapper-fresh-timeout-manifest-gate", wrapper_path.as_posix(), "acceptedFreshManifestAfterTimeout"),
        ("global", "missing-wrapper-timeout-manifest-freshness", wrapper_path.as_posix(), "manifest_is_fresh"),
        ("global", "missing-wrapper-video-composition-audit", wrapper_path.as_posix(), "audit_metro_video_composition.py"),
        ("global", "missing-wrapper-video-composition-report", wrapper_path.as_posix(), "metroVideoCompositionAudit"),
        ("global", "missing-video-composition-audit-script", video_composition_audit_path.as_posix(), "contact-sheet-slide-like-composition"),
        ("global", "missing-video-composition-grid-gate", video_composition_audit_path.as_posix(), "mp4-weak-grid-coverage"),
        ("global", "missing-video-composition-quadrant-gate", video_composition_audit_path.as_posix(), "mp4-weak-quadrant-coverage"),
        ("global", "missing-video-composition-progression-gate", video_composition_audit_path.as_posix(), "mp4-weak-spatial-progression"),
        ("global", "missing-video-composition-text-pressure-gate", video_composition_audit_path.as_posix(), "mp4-text-like-component-pressure"),
        ("global", "missing-video-composition-red-area-gate", video_composition_audit_path.as_posix(), "mp4-red-area-too-dominant"),
        ("global", "missing-video-composition-red-area-report", video_composition_audit_path.as_posix(), "maxRedAreaRatio"),
        ("global", "missing-video-composition-missing-video-report", video_composition_audit_path.as_posix(), "mp4-missing-video"),
        ("global", "missing-tonal-open-sans-gate", tonal_audit_path.as_posix(), "wrong-metro-font-stack"),
        ("global", "missing-tonal-font-report", tonal_audit_path.as_posix(), "fontFamilies"),
        ("global", "missing-metro-audit-suite-style", audit_suite_path.as_posix(), "audit_metro_tonal_style.py"),
        ("global", "missing-metro-audit-suite-composition", audit_suite_path.as_posix(), "audit_metro_composition.py"),
        ("global", "missing-metro-audit-suite-rendered-frame", audit_suite_path.as_posix(), "audit_metro_rendered_frames.py"),
        ("global", "missing-metro-audit-suite-default-outputs", audit_suite_path.as_posix(), "fill_default_outputs"),
        ("global", "missing-metro-audit-suite-rendered-failure-retry", audit_suite_path.as_posix(), "retryAfterFailure"),
        ("global", "missing-metro-audit-suite-bounded-mute-flag", audit_suite_path.as_posix(), "--mute-test-samples"),
        ("global", "missing-metro-audit-suite-bounded-mute-forwarding", audit_suite_path.as_posix(), "--samples"),
        ("global", "missing-metro-audit-suite-bounded-mute-report", audit_suite_path.as_posix(), "muteTestSamples"),
        ("global", "missing-composition-padding-audit", composition_audit_path.as_posix(), "extract_padding_signals"),
        ("global", "missing-composition-visible-gray-audit", composition_audit_path.as_posix(), "rect_fill_expressions"),
        ("global", "missing-composition-rounded-line-audit", composition_audit_path.as_posix(), "extract_rounded_line_signals"),
        ("global", "missing-composition-dynamic-rounded-audit", composition_audit_path.as_posix(), "rx-dynamic-object"),
        ("global", "missing-composition-dynamic-rect-audit", composition_audit_path.as_posix(), "runtimeRectNormalizer"),
        ("global", "missing-composition-selected-pattern-audit", composition_audit_path.as_posix(), "selected_pattern_scope"),
        ("global", "missing-composition-gray-spread-audit", composition_audit_path.as_posix(), "selectedPatternGrayLuminanceSpread"),
        ("global", "missing-wrapper-composition-source-package", audit_suite_path.as_posix(), "audit_metro_composition.py"),
        ("global", "missing-rendered-frame-chromium-audit", rendered_frame_audit_path.as_posix(), "sample_rendered_frames"),
        ("global", "missing-rendered-frame-grid-audit", rendered_frame_audit_path.as_posix(), "rendered-offgrid-rect-edges"),
        ("global", "missing-rendered-frame-shared-edge-audit", rendered_frame_audit_path.as_posix(), "rendered-weak-shared-edge-composition"),
        ("global", "missing-rendered-frame-gray-audit", rendered_frame_audit_path.as_posix(), "rendered-insufficient-gray-hierarchy"),
        ("global", "missing-rendered-frame-final-gray-audit", rendered_frame_audit_path.as_posix(), "rendered-final-insufficient-gray-hierarchy"),
        ("global", "missing-rendered-frame-median-gray-audit", rendered_frame_audit_path.as_posix(), "rendered-median-insufficient-gray-hierarchy"),
        ("global", "missing-rendered-frame-gray-sample-ratio", rendered_frame_audit_path.as_posix(), "min_gray_sample_pass_ratio"),
        ("global", "missing-rendered-frame-red-area-audit", rendered_frame_audit_path.as_posix(), "rendered-red-rect-area-too-high"),
        ("global", "missing-rendered-frame-red-area-report", rendered_frame_audit_path.as_posix(), "maxRedRectAreaRatio"),
        ("global", "missing-rendered-frame-zero-padding-geometry", rendered_frame_audit_path.as_posix(), "rendered-internal-padding-geometry"),
        ("global", "missing-rendered-frame-zero-padding-checks", rendered_frame_audit_path.as_posix(), "zero_padding_geometry_checks"),
        ("global", "missing-rendered-frame-untagged-inset-padding", rendered_frame_audit_path.as_posix(), "rendered-untagged-inset-rect-padding"),
        ("global", "missing-rendered-frame-untagged-inset-checks", rendered_frame_audit_path.as_posix(), "untagged_inset_rect_checks"),
        ("global", "missing-rendered-frame-padded-module-checks", rendered_frame_audit_path.as_posix(), "padded_module_interior_checks"),
        ("global", "missing-rendered-frame-padded-module-finding", rendered_frame_audit_path.as_posix(), "rendered-padded-module-interiors"),
        ("global", "missing-rendered-frame-padding-coverage-finding", rendered_frame_audit_path.as_posix(), "rendered-padding-detector-no-coverage"),
        ("global", "missing-rendered-frame-padded-module-report", rendered_frame_audit_path.as_posix(), "paddedModuleInteriorViolationCount"),
        ("global", "missing-rendered-frame-zone-marker-audit", rendered_frame_audit_path.as_posix(), "zoneElementCount"),
        ("global", "missing-rendered-frame-source-anchor-audit", rendered_frame_audit_path.as_posix(), "dataSourceAnchor"),
        ("global", "missing-rendered-frame-source-anchor-json-audit", rendered_frame_audit_path.as_posix(), "dataSourceAnchorJson"),
        ("global", "missing-rendered-frame-semantic-glyph-audit", rendered_frame_audit_path.as_posix(), "dataSemanticGlyph"),
        ("global", "missing-rendered-frame-semantic-glyph-report", rendered_frame_audit_path.as_posix(), "maxSemanticGlyphCount"),
        ("global", "missing-rendered-frame-source-anchor-report", rendered_frame_audit_path.as_posix(), "sourceAnchors"),
        ("global", "missing-rendered-frame-zone-finding", rendered_frame_audit_path.as_posix(), "rendered-too-few-zone-elements"),
        ("global", "missing-rendered-frame-masonry-attrs", rendered_frame_audit_path.as_posix(), "dataMasonryModule"),
        ("global", "missing-rendered-frame-masonry-module-finding", rendered_frame_audit_path.as_posix(), "rendered-missing-masonry-modules"),
        ("global", "missing-rendered-frame-masonry-size-finding", rendered_frame_audit_path.as_posix(), "rendered-weak-masonry-size-variety"),
        ("global", "missing-rendered-frame-masonry-construction-finding", rendered_frame_audit_path.as_posix(), "rendered-static-masonry-construction"),
        ("global", "missing-rendered-frame-masonry-growth-finding", rendered_frame_audit_path.as_posix(), "rendered-weak-masonry-construction-growth"),
        ("global", "missing-rendered-frame-masonry-text-count-finding", rendered_frame_audit_path.as_posix(), "rendered-masonry-too-many-text-elements"),
        ("global", "missing-rendered-frame-masonry-text-character-finding", rendered_frame_audit_path.as_posix(), "rendered-masonry-too-many-text-characters"),
        ("global", "missing-rendered-frame-masonry-count-report", rendered_frame_audit_path.as_posix(), "masonryModuleCounts"),
        ("global", "missing-rendered-frame-text-area-audit", rendered_frame_audit_path.as_posix(), "rendered-text-area-too-high"),
        ("global", "missing-rendered-frame-dominant-text-audit", rendered_frame_audit_path.as_posix(), "rendered-dominant-text-box"),
        ("global", "missing-rendered-frame-mark-to-text-audit", rendered_frame_audit_path.as_posix(), "weak-rendered-mark-to-text-density"),
        ("global", "missing-rendered-frame-title-band-audit", rendered_frame_audit_path.as_posix(), "rendered-title-band-text"),
        ("global", "missing-rendered-frame-ellipsis-audit", rendered_frame_audit_path.as_posix(), "rendered-ellipsized-text"),
        ("global", "missing-semantic-density-ellipsis-gate", semantic_density_path.as_posix(), "max_rendered_ellipsized_text_count"),
        ("global", "missing-wrapper-rendered-frame-source-package", audit_suite_path.as_posix(), "audit_metro_rendered_frames.py"),
        ("global", "missing-semantic-density-pattern-mix-gate", semantic_density_path.as_posix(), "pattern_mix_findings"),
        ("global", "missing-semantic-density-pattern-mix-required", semantic_density_path.as_posix(), "require_metro_pattern_mix"),
        ("global", "missing-semantic-density-helper-match", semantic_density_path.as_posix(), "metro-pattern-mix-helper-mismatch"),
        ("global", "missing-semantic-density-mix-zone-gate", semantic_density_path.as_posix(), "too-few-mix-functional-zones"),
        ("global", "missing-semantic-density-mix-motion-gate", semantic_density_path.as_posix(), "too-few-mix-motion-systems"),
        ("global", "missing-semantic-density-mix-camera-gate", semantic_density_path.as_posix(), "too-few-mix-camera-events"),
        ("global", "missing-semantic-density-mix-transition-gate", semantic_density_path.as_posix(), "too-few-mix-transition-contracts"),
        ("global", "missing-semantic-density-mix-transition-type-gate", semantic_density_path.as_posix(), "too-few-mix-transition-types"),
        ("global", "missing-semantic-density-modular-transition-gate", semantic_density_path.as_posix(), "missing-modular-transition-type"),
        ("global", "missing-semantic-density-masonry-contract-gate", semantic_density_path.as_posix(), "masonryContract"),
        ("global", "missing-semantic-density-masonry-pattern-gate", semantic_density_path.as_posix(), "missing-required-masonry-pattern"),
        ("global", "missing-semantic-density-masonry-transition-gate", semantic_density_path.as_posix(), "missing-required-masonry-transition"),
        ("global", "missing-semantic-density-rendered-masonry-module-gate", semantic_density_path.as_posix(), "too-few-rendered-masonry-modules"),
        ("global", "missing-semantic-density-rendered-masonry-size-gate", semantic_density_path.as_posix(), "weak-rendered-masonry-size-variety"),
        ("global", "missing-semantic-density-rendered-masonry-construction-gate", semantic_density_path.as_posix(), "missing-rendered-masonry-construction"),
        ("global", "missing-semantic-density-rendered-masonry-growth-gate", semantic_density_path.as_posix(), "weak-rendered-masonry-construction-growth"),
        ("global", "missing-semantic-density-rendered-masonry-text-gate", semantic_density_path.as_posix(), "rendered-masonry-too-text-led"),
        ("global", "missing-semantic-density-continuity-gate", semantic_density_path.as_posix(), "continuity_findings"),
        ("global", "missing-semantic-density-continuity-path-finding", semantic_density_path.as_posix(), "weak-zone-continuity-path"),
        ("global", "missing-semantic-density-camera-zone-coupling-finding", semantic_density_path.as_posix(), "weak-camera-zone-coupling"),
        ("global", "missing-semantic-density-camera-travel-gate", semantic_density_path.as_posix(), "weak-camera-travel"),
        ("global", "missing-semantic-density-camera-zoom-gate", semantic_density_path.as_posix(), "weak-camera-zoom-depth"),
        ("global", "missing-semantic-density-mix-risk-gate", semantic_density_path.as_posix(), "missing-mix-anti-pattern-risks"),
        ("global", "missing-semantic-density-mix-padding-gate", semantic_density_path.as_posix(), "mix-internal-padding-not-zero"),
        ("global", "missing-semantic-density-source-zone-gate", semantic_density_path.as_posix(), "too-few-source-visual-zones"),
        ("global", "missing-semantic-density-render-state-zone-gate", semantic_density_path.as_posix(), "too-few-render-state-visible-zones"),
        ("global", "missing-semantic-density-active-zone-gate", semantic_density_path.as_posix(), "weak-active-zone-progression"),
        ("global", "missing-semantic-density-rendered-zone-gate", semantic_density_path.as_posix(), "too-few-rendered-zone-elements"),
        ("global", "missing-semantic-density-binding-gate", semantic_density_path.as_posix(), "semantic_binding_findings"),
        ("global", "missing-semantic-density-binding-coverage-finding", semantic_density_path.as_posix(), "semantic-binding-coverage-too-low"),
        ("global", "missing-semantic-density-source-anchor-coverage", semantic_density_path.as_posix(), "sourceAnchorVisualBindingCoverage"),
        ("global", "missing-semantic-density-active-source-anchor-gate", semantic_density_path.as_posix(), "activeSourceAnchors"),
        ("global", "missing-semantic-density-state-evidence-gate", semantic_density_path.as_posix(), "missing-state-evidence-for-mix"),
        ("global", "missing-semantic-density-contact-evidence-gate", semantic_density_path.as_posix(), "missing-contact-evidence-for-mix"),
        ("global", "missing-semantic-density-rendered-evidence-gate", semantic_density_path.as_posix(), "missing-rendered-frame-evidence-for-mix"),
        ("global", "missing-semantic-density-video-composition-gate", semantic_density_path.as_posix(), "video_composition_findings"),
        ("global", "missing-semantic-density-video-composition-required", semantic_density_path.as_posix(), "missing-mp4-composition-evidence-for-mix"),
        ("global", "missing-semantic-density-video-composition-evidence", semantic_density_path.as_posix(), "mp4CompositionAudit"),
        ("global", "missing-semantic-density-mp4-red-area-gate", semantic_density_path.as_posix(), "mp4-red-area-too-dominant"),
        ("global", "missing-semantic-density-mp4-red-area-report", semantic_density_path.as_posix(), "maxMp4RedAreaRatio"),
        ("global", "missing-semantic-density-video-composition-suite-sibling", semantic_density_path.as_posix(), "suite_path.with_name"),
        ("global", "missing-metro-fixture-script", audit_fixture_path.as_posix(), "rendered-padding-geometry-fails"),
        ("global", "missing-metro-fixture-untagged-inset", audit_fixture_path.as_posix(), "rendered-untagged-inset-padding-fails"),
        ("global", "missing-metro-fixture-no-stroke-inset", audit_fixture_path.as_posix(), "rendered-no-stroke-untagged-inset-fails"),
        ("global", "missing-metro-fixture-small-inset", audit_fixture_path.as_posix(), "rendered-small-inset-padding-fails"),
        ("global", "missing-metro-fixture-transformed-offgrid", audit_fixture_path.as_posix(), "rendered-transformed-offgrid-fails"),
        ("global", "missing-metro-fixture-css-rounded", audit_fixture_path.as_posix(), "rendered-css-rounded-fails"),
        ("global", "missing-metro-fixture-tonal-font", audit_fixture_path.as_posix(), "tonal-wrong-font-fails"),
        ("global", "missing-metro-fixture-dynamic-rounded", audit_fixture_path.as_posix(), "composition-dynamic-rounded-fails"),
        ("global", "missing-metro-fixture-tiny-gray-swatches", audit_fixture_path.as_posix(), "rendered-tiny-gray-swatches-fails"),
        ("global", "missing-metro-fixture-weak-gray", audit_fixture_path.as_posix(), "rendered-weak-gray-fails"),
        ("global", "missing-metro-fixture-title-band", audit_fixture_path.as_posix(), "rendered-title-band-text-fails"),
        ("global", "missing-metro-fixture-text-area", audit_fixture_path.as_posix(), "rendered-text-area-fails"),
        ("global", "missing-metro-fixture-dominant-text-box", audit_fixture_path.as_posix(), "rendered-dominant-text-box-fails"),
        ("global", "missing-metro-fixture-mark-to-text-density", audit_fixture_path.as_posix(), "rendered-mark-to-text-density-fails"),
        ("global", "missing-metro-fixture-ellipsized-text", audit_fixture_path.as_posix(), "rendered-ellipsized-text-fails"),
        ("global", "missing-metro-fixture-red-dominant-surface", audit_fixture_path.as_posix(), "rendered-red-dominant-surface-fails"),
        ("global", "missing-metro-fixture-video-red-dominant", audit_fixture_path.as_posix(), "mp4-composition-red-dominant-fails"),
        ("global", "missing-metro-fixture-video-missing-report", audit_fixture_path.as_posix(), "mp4-composition-missing-video-writes-report"),
        ("global", "missing-metro-fixture-suite-output-only", audit_fixture_path.as_posix(), "suite-output-only-derives-children"),
        ("global", "missing-metro-fixture-masonry-good", audit_fixture_path.as_posix(), "semantic-masonry-contract-good-passes"),
        ("global", "missing-metro-fixture-masonry-pattern-negative", audit_fixture_path.as_posix(), "semantic-masonry-missing-pattern-fails"),
        ("global", "missing-metro-fixture-masonry-transition-negative", audit_fixture_path.as_posix(), "semantic-masonry-missing-transition-fails"),
        ("global", "missing-metro-fixture-masonry-flag-negative", audit_fixture_path.as_posix(), "semantic-masonry-false-pattern-flag-fails"),
        ("global", "missing-metro-fixture-source-anchor-map", audit_fixture_path.as_posix(), "semantic-source-anchor-map-good-passes"),
        ("global", "missing-metro-fixture-role-scramble", audit_fixture_path.as_posix(), "semantic-density-role-scramble-fails"),
        ("global", "missing-metro-fixture-rendered-masonry-good", audit_fixture_path.as_posix(), "rendered-masonry-good-passes"),
        ("global", "missing-metro-fixture-rendered-masonry-negative", audit_fixture_path.as_posix(), "rendered-masonry-missing-modules-fails"),
        ("global", "missing-metro-pattern-smoke-script", pattern_smoke_path.as_posix(), "PATTERNS"),
        ("global", "missing-metro-pattern-smoke-suite-call", pattern_smoke_path.as_posix(), "run_metro_audit_suite.py"),
        ("global", "missing-metro-pattern-smoke-aggregate-metrics", pattern_smoke_path.as_posix(), "aggregateMetrics"),
        ("global", "missing-metro-pattern-smoke-masonry-flag", pattern_smoke_path.as_posix(), "--masonry-layout"),
        ("global", "missing-metro-pattern-smoke-masonry-metrics", pattern_smoke_path.as_posix(), "patternsWithWeakMasonry"),
        ("global", "missing-metro-pattern-smoke-masonry-module-count", pattern_smoke_path.as_posix(), "minMaxMasonryModuleCount"),
        ("global", "missing-metro-pattern-smoke-semantic-glyph-count", pattern_smoke_path.as_posix(), "minMaxSemanticGlyphCount"),
        ("global", "missing-metro-pattern-mix-script", pattern_mix_path.as_posix(), "CATALOG"),
        ("global", "missing-metro-pattern-mix-helper-pattern", pattern_mix_path.as_posix(), "helperPattern"),
        ("global", "missing-metro-pattern-mix-functional-zones", pattern_mix_path.as_posix(), "functionalZones"),
        ("global", "missing-metro-pattern-mix-motion-systems", pattern_mix_path.as_posix(), "semanticMotionSystems"),
        ("global", "missing-metro-pattern-mix-camera-path", pattern_mix_path.as_posix(), "cameraPath"),
        ("global", "missing-metro-pattern-mix-transition-contracts", pattern_mix_path.as_posix(), "transitionContracts"),
        ("global", "missing-metro-pattern-mix-masonry-pattern", pattern_mix_path.as_posix(), "masonry-wall"),
        ("global", "missing-metro-pattern-mix-masonry-transition", pattern_mix_path.as_posix(), "masonry-construction"),
        ("global", "missing-metro-pattern-mix-masonry-contract", pattern_mix_path.as_posix(), "masonryContract"),
        ("global", "missing-metro-pattern-mix-d3-patterns", pattern_mix_path.as_posix(), "reusableD3PatternIds"),
        ("global", "missing-metro-pattern-mix-circuit-pattern", pattern_mix_path.as_posix(), "d3-pattern-circuit-signal-traces"),
        ("global", "missing-metro-pattern-mix-queue-pattern", pattern_mix_path.as_posix(), "d3-pattern-critical-queue-backpressure"),
        ("global", "missing-metro-pattern-mix-anti-pattern-risks", pattern_mix_path.as_posix(), "antiPatternRisks"),
        ("global", "missing-metro-series-plan-script", series_plan_path.as_posix(), "plan_metro_video_series"),
        ("global", "missing-metro-series-module-parser", series_plan_path.as_posix(), "markdown_video_sections"),
        ("global", "missing-metro-series-helper-diversity", series_plan_path.as_posix(), "helperDiversity"),
        ("global", "missing-metro-series-primary-diversity", series_plan_path.as_posix(), "primaryPatternDiversity"),
        ("global", "missing-metro-series-d3-diversity", series_plan_path.as_posix(), "reusableD3PatternCount"),
        ("global", "missing-metro-series-repeated-helper-gate", series_plan_path.as_posix(), "series-repeated-helper-run-too-long"),
        ("global", "missing-metro-series-collapse-gate", series_plan_path.as_posix(), "series-collapsed-to-systems-flow"),
        ("global", "missing-metro-series-contract-script", series_contract_path.as_posix(), "build_metro_series_contract_prompts"),
        ("global", "missing-metro-series-contract-wrapper-command", series_contract_path.as_posix(), "build_from_prompt_contract.py"),
        ("global", "missing-metro-series-contract-semantic-command", series_contract_path.as_posix(), "audit_metro_semantic_density.py"),
        ("global", "missing-metro-series-contract-mp4-composition", series_contract_path.as_posix(), "metro-video-composition-audit.json"),
        ("global", "missing-metro-series-contract-final-output-separation", series_contract_path.as_posix(), "Additional final validation reports after the second command"),
        ("global", "missing-wrapper-pattern-mix-integration", wrapper_path.as_posix(), "plan_metro_pattern_mix.py"),
        ("global", "missing-wrapper-pattern-mix-report", wrapper_path.as_posix(), "metroPatternMix"),
        ("global", "missing-wrapper-pattern-mix-constraints", wrapper_path.as_posix(), "metroConstraints"),
        ("global", "missing-wrapper-pattern-mix-masonry-contract", wrapper_path.as_posix(), "masonryContract"),
        ("global", "missing-wrapper-masonry-layout-flag", wrapper_path.as_posix(), "masonryLayoutRequired"),
        ("global", "missing-helper-masonry-layout-flag", helper_path.as_posix(), "--masonry-layout"),
        ("global", "missing-helper-masonry-modules", helper_path.as_posix(), "masonryModules"),
        ("global", "missing-helper-masonry-render-attrs", helper_path.as_posix(), "data-masonry-module"),
        ("global", "missing-helper-masonry-construction-render", helper_path.as_posix(), "data-masonry-phase"),
        ("global", "missing-helper-generic-masonry-renderer", helper_path.as_posix(), "render_generic_masonry_frame"),
        ("global", "missing-helper-probability-evaluation-routing", helper_path.as_posix(), "probability_evaluation_requested"),
        ("global", "missing-helper-probability-evaluation-motifs", helper_path.as_posix(), "draw_probability_evaluation_motifs"),
        ("global", "missing-helper-passn-grid-motif", helper_path.as_posix(), "pass@N"),
        ("global", "missing-helper-agent-loop-routing", helper_path.as_posix(), "agent_loop_requested"),
        ("global", "missing-helper-agent-loop-renderer", helper_path.as_posix(), "render_agent_loop_masonry_frame"),
        ("global", "missing-helper-agent-loop-state", helper_path.as_posix(), "agentLoopRingVisible"),
        ("global", "missing-semantic-density-agent-loop-gate", semantic_density_path.as_posix(), "agent_loop_motif_findings"),
        ("global", "missing-semantic-density-agent-environment-gate", semantic_density_path.as_posix(), "weak-agent-environment-state-progression"),
        ("global", "missing-helper-hook-routing", helper_path.as_posix(), "hook_requested"),
        ("global", "missing-helper-hook-renderer", helper_path.as_posix(), "render_hook_masonry_frame"),
        ("global", "missing-helper-hook-event-state", helper_path.as_posix(), "eventTimelineVisible"),
        ("global", "missing-helper-hook-shield-state", helper_path.as_posix(), "shieldGateOverlayVisible"),
        ("global", "missing-semantic-density-hook-gate", semantic_density_path.as_posix(), "hook_motif_findings"),
        ("global", "missing-semantic-density-hook-savings-gate", semantic_density_path.as_posix(), "weak-hook-token-savings-progression"),
        ("global", "missing-density-hook-contract-doc", density_path.as_posix(), "event_timeline"),
        ("global", "missing-helper-harness-routing", helper_path.as_posix(), "harness_requested"),
        ("global", "missing-helper-harness-renderer", helper_path.as_posix(), "render_harness_masonry_frame"),
        ("global", "missing-helper-harness-comparison-state", helper_path.as_posix(), "comparisonGridVisible"),
        ("global", "missing-helper-harness-runtime-state", helper_path.as_posix(), "runtimeStackVisible"),
        ("global", "missing-helper-harness-credit-meter-state", helper_path.as_posix(), "creditMeterLevel"),
        ("global", "missing-helper-harness-selection-state", helper_path.as_posix(), "selectionPathHighlighted"),
        ("global", "missing-semantic-density-harness-gate", semantic_density_path.as_posix(), "harness_motif_findings"),
        ("global", "missing-semantic-density-harness-credit-gate", semantic_density_path.as_posix(), "weak-harness-credit-meter-progression"),
        ("global", "missing-density-harness-contract-doc", density_path.as_posix(), "engine-to-dashboard"),
        ("global", "missing-skill-harness-contract-doc", skill_path.as_posix(), "comparison_grid"),
        ("global", "missing-helper-plugin-routing", helper_path.as_posix(), "plugin_requested"),
        ("global", "missing-helper-plugin-renderer", helper_path.as_posix(), "render_plugin_masonry_frame"),
        ("global", "missing-helper-plugin-bundle-state", helper_path.as_posix(), "pluginBundleCubeVisible"),
        ("global", "missing-helper-plugin-module-state", helper_path.as_posix(), "bundleModuleCount"),
        ("global", "missing-helper-plugin-marketplace-state", helper_path.as_posix(), "claudeMarketplaceGateVisible"),
        ("global", "missing-helper-plugin-npm-state", helper_path.as_posix(), "opencodeNpmRuntimeDropVisible"),
        ("global", "missing-semantic-density-plugin-gate", semantic_density_path.as_posix(), "plugin_motif_findings"),
        ("global", "missing-semantic-density-plugin-cost-gate", semantic_density_path.as_posix(), "weak-plugin-cost-meter-progression"),
        ("global", "missing-density-plugin-contract-doc", density_path.as_posix(), "plugin_bundle_cube"),
        ("global", "missing-skill-plugin-contract-doc", skill_path.as_posix(), "packaged harness behavior"),
        ("global", "missing-helper-ai-alternatives-routing", helper_path.as_posix(), "ai_alternatives_requested"),
        ("global", "missing-helper-ai-alternatives-renderer", helper_path.as_posix(), "render_ai_alternatives_masonry_frame"),
        ("global", "missing-helper-ai-alternatives-anchors", helper_path.as_posix(), "ai_alternatives_anchor_groups"),
        ("global", "missing-helper-ai-alternatives-selector-state", helper_path.as_posix(), "workflowSelectorVisible"),
        ("global", "missing-helper-ai-alternatives-path-state", helper_path.as_posix(), "selectedWorkflowPathVisible"),
        ("global", "missing-wrapper-ai-alternatives-routing", wrapper_path.as_posix(), "ai_alternatives_requested"),
        ("global", "missing-semantic-density-ai-alternatives-gate", semantic_density_path.as_posix(), "ai_alternatives_motif_findings"),
        ("global", "missing-semantic-density-ai-alternatives-cost-gate", semantic_density_path.as_posix(), "weak-ai-cost-meter-level-progression"),
        ("global", "missing-semantic-density-ai-alternatives-red-gate", semantic_density_path.as_posix(), "ai-alternatives-red-area-too-dominant"),
        ("global", "missing-density-ai-alternatives-contract-doc", density_path.as_posix(), "workflow gravity"),
        ("global", "missing-skill-ai-alternatives-contract-doc", skill_path.as_posix(), "Atlassian Rovo"),
        ("global", "missing-helper-skill-routing", helper_path.as_posix(), "skill_package_requested"),
        ("global", "missing-helper-skill-renderer", helper_path.as_posix(), "render_skill_package_masonry_frame"),
        ("global", "missing-helper-skill-card-state", helper_path.as_posix(), "skillCardStackVisible"),
        ("global", "missing-helper-skill-resource-state", helper_path.as_posix(), "resourceBundleVisible"),
        ("global", "missing-helper-skill-validation-state", helper_path.as_posix(), "validationHarnessVisible"),
        ("global", "missing-helper-skill-read-state", helper_path.as_posix(), "readSurfaceVisible"),
        ("global", "missing-wrapper-skill-routing", wrapper_path.as_posix(), "skill_requested"),
        ("global", "missing-wrapper-skill-state", wrapper_path.as_posix(), "skillCardStackVisible"),
        ("global", "missing-semantic-density-skill-gate", semantic_density_path.as_posix(), "skill_motif_findings"),
        ("global", "missing-semantic-density-skill-validation-gate", semantic_density_path.as_posix(), "weak-skill-validation-progression"),
        ("global", "missing-density-skill-contract-doc", density_path.as_posix(), "skill_card_stack"),
        ("global", "missing-density-skill-progressive-disclosure-doc", density_path.as_posix(), "progressive disclosure"),
        ("global", "missing-skill-skill-contract-doc", skill_path.as_posix(), "long prompt wall"),
        ("global", "missing-helper-guardrail-routing", helper_path.as_posix(), "guardrail_requested"),
        ("global", "missing-helper-guardrail-renderer", helper_path.as_posix(), "render_guardrail_masonry_frame"),
        ("global", "missing-helper-guardrail-state", helper_path.as_posix(), "guardrailShieldGateVisible"),
        ("global", "missing-helper-guardrail-input-gate-state", helper_path.as_posix(), "inputGateVisible"),
        ("global", "missing-helper-guardrail-policy-matrix-state", helper_path.as_posix(), "policyMatrixVisible"),
        ("global", "missing-helper-guardrail-zero-padding-attrs", helper_path.as_posix(), "data-padding-policy"),
        ("global", "missing-helper-guardrail-transition-attrs", helper_path.as_posix(), "data-transition-type"),
        ("global", "missing-helper-guardrail-mechanism-attrs", helper_path.as_posix(), "data-mechanism-id"),
        ("global", "missing-semantic-density-guardrail-gate", semantic_density_path.as_posix(), "guardrail_motif_findings"),
        ("global", "missing-semantic-density-guardrail-risk-score-gate", semantic_density_path.as_posix(), "weak-guardrail-risk-score-progression"),
        ("global", "missing-density-guardrail-contract-doc", density_path.as_posix(), "shield_gate"),
        ("global", "missing-skill-guardrail-contract-doc", skill_path.as_posix(), "risk_score"),
        ("global", "missing-helper-generic-masonry-pattern-set", helper_path.as_posix(), "MASONRY_GENERIC_RENDER_PATTERNS"),
        ("global", "missing-html-masonry-label-suppression", helper_path.as_posix(), "if (masonryRequired) return null"),
        ("global", "missing-helper-masonry-pillow-render", helper_path.as_posix(), "low_text_masonry = bool(args.masonry_layout)"),
        ("global", "missing-helper-masonry-pillow-opening-density", helper_path.as_posix(), "reveal_start + clamp(p) * (len(MASONRY_MODULE_BOUNDS) - reveal_start)"),
        ("global", "missing-helper-masonry-pillow-label-suppression", helper_path.as_posix(), '"" if low_text_masonry else "job"'),
        ("global", "missing-skill-fixture-validation-doc", skill_path.as_posix(), "validate_metro_audit_fixtures.py"),
        ("global", "missing-skill-pattern-smoke-doc", skill_path.as_posix(), "validate_metro_pattern_smoke.py"),
        ("global", "missing-skill-pattern-mix-doc", skill_path.as_posix(), "plan_metro_pattern_mix.py"),
        ("global", "missing-skill-series-plan-doc", skill_path.as_posix(), "plan_metro_video_series.py"),
        ("global", "missing-skill-series-contract-doc", skill_path.as_posix(), "build_metro_series_contract_prompts.py"),
        ("global", "missing-loop-fixture-validation-doc", loop_path.as_posix(), "validate_metro_audit_fixtures.py"),
        ("global", "missing-loop-pattern-smoke-doc", loop_path.as_posix(), "validate_metro_pattern_smoke.py"),
        ("global", "missing-loop-pattern-mix-doc", loop_path.as_posix(), "plan_metro_pattern_mix.py"),
        ("global", "missing-loop-series-contract-doc", loop_path.as_posix(), "build_metro_series_contract_prompts.py"),
        ("global", "missing-density-pattern-mix-doc", density_path.as_posix(), "Scripted Pattern Mix Gate"),
        ("global", "missing-density-series-plan-doc", density_path.as_posix(), "Series Pattern Diversity Gate"),
        ("global", "missing-density-series-contract-doc", density_path.as_posix(), "build_metro_series_contract_prompts.py"),
        ("global", "missing-density-visual-anchor-contract-doc", density_path.as_posix(), "probability_bars"),
        ("global", "missing-density-agent-loop-contract-doc", density_path.as_posix(), "agent_loop_ring"),
        ("global", "missing-density-helper-pattern-doc", density_path.as_posix(), "selected.helperPattern"),
        ("global", "missing-density-source-anchor-binding-doc", density_path.as_posix(), "sourceAnchorVisualBindingCoverage"),
        ("global", "missing-contract-pattern-mix-doc", contract_path.as_posix(), "metroPatternMix"),
        ("global", "missing-contract-series-plan-doc", contract_path.as_posix(), "plan_metro_video_series.py"),
        ("global", "missing-contract-series-contract-doc", contract_path.as_posix(), "build_metro_series_contract_prompts.py"),
        ("global", "missing-contract-helper-pattern-doc", contract_path.as_posix(), "selected.helperPattern"),
        ("global", "missing-contract-semantic-binding-doc", contract_path.as_posix(), "semanticBindings"),
        ("global", "missing-contract-source-anchor-doc", contract_path.as_posix(), "data-source-anchor"),
        ("global", "missing-skill-zero-padding-doc", skill_path.as_posix(), "no internal box padding"),
        ("global", "missing-skill-gray-doc", skill_path.as_posix(), "distinct grayscale levels"),
        ("global", "missing-skill-visual-anchor-contract-doc", skill_path.as_posix(), "probability_bars"),
        ("global", "missing-skill-agent-loop-contract-doc", skill_path.as_posix(), "agent_loop_ring"),
        ("global", "missing-skill-no-read-suite-source", skill_path.as_posix(), "do not open the wrapper, suite, audit, or checker source"),
        ("global", "missing-skill-no-repeat-checker", skill_path.as_posix(), "do not run or inspect `check_video_outputs.py` again"),
        ("global", "missing-contract-padding-doc", contract_path.as_posix(), "zero internal box-padding"),
        ("global", "missing-contract-gray-doc", contract_path.as_posix(), "grayscale hierarchy"),
        ("global", "missing-contract-mute-test-doc", contract_path.as_posix(), "metro-mute-test-audit.json"),
        ("global", "missing-contract-video-composition-doc", contract_path.as_posix(), "metro-video-composition-audit.json"),
        ("global", "missing-contract-bounded-mute-doc", contract_path.as_posix(), "bounded four-sample mute test"),
        ("global", "missing-contract-compact-mute-acceptance", contract_path.as_posix(), "metroMuteTestAudit"),
        ("global", "missing-contract-no-read-suite-source", contract_path.as_posix(), "do not open helper, wrapper, suite, audit, or checker script source"),
        ("global", "missing-contract-compact-wrapper-acceptance", contract_path.as_posix(), "accept those results without reading child manifests or script sources"),
        ("global", "missing-loop-padding-doc", loop_path.as_posix(), "zero internal"),
        ("global", "missing-loop-gray-doc", loop_path.as_posix(), "grayscale"),
        ("global", "missing-loop-video-composition-doc", loop_path.as_posix(), "metro-video-composition-audit.json"),
        ("global", "missing-loop-bounded-mute-doc", loop_path.as_posix(), "bounded four-sample mute test"),
    ]
    content_by_path = {
        helper_path.as_posix(): helper,
        wrapper_path.as_posix(): wrapper,
        audit_suite_path.as_posix(): audit_suite,
        tonal_audit_path.as_posix(): tonal_audit,
        video_composition_audit_path.as_posix(): video_composition_audit,
        composition_audit_path.as_posix(): composition_audit,
        rendered_frame_audit_path.as_posix(): rendered_frame_audit,
        semantic_density_path.as_posix(): semantic_density,
        audit_fixture_path.as_posix(): audit_fixture,
        pattern_smoke_path.as_posix(): pattern_smoke,
        pattern_mix_path.as_posix(): pattern_mix,
        series_plan_path.as_posix(): series_plan,
        series_contract_path.as_posix(): series_contract,
        skill_path.as_posix(): skill,
        contract_path.as_posix(): contract,
        loop_path.as_posix(): loop,
        density_path.as_posix(): density,
    }
    for pattern, code, path, token in policy_checks:
        if token not in content_by_path[path]:
            add_finding(findings, pattern, code, path, token)

    forbidden_tokens = [
        (
            "global",
            "rendered-frame-source-anchor-truncation",
            rendered_frame_audit_path.as_posix(),
            "source_anchors[:",
        ),
        (
            "global",
            "rendered-frame-semantic-binding-truncation",
            rendered_frame_audit_path.as_posix(),
            "semantic_bindings[:",
        ),
    ]
    for pattern, code, path, token in forbidden_tokens:
        if token in content_by_path[path]:
            add_finding(findings, pattern, code, path, token)

    low_text_masonry_branches = [
        ("metric-dashboard", "render_metric_dashboard_frame"),
        ("sankey-flow", "render_sankey_flow_frame"),
    ]
    for pattern, function_name in low_text_masonry_branches:
        pillow_block = python_function_block(helper, function_name)
        if "low_text_masonry" not in pillow_block:
            add_finding(findings, pattern, "missing-pillow-low-text-masonry-gate", helper_path.as_posix(), function_name)
        if "if not low_text_masonry" not in pillow_block:
            add_finding(findings, pattern, "missing-pillow-masonry-text-suppression", helper_path.as_posix(), function_name)
        if "draw_masonry_megacanvas_base" not in pillow_block:
            add_finding(findings, pattern, "missing-pillow-masonry-megacanvas-base", helper_path.as_posix(), function_name)
        js_block = js_visual_pattern_block(helper, pattern)
        if "masonryRequired" not in js_block:
            add_finding(findings, pattern, "missing-js-masonry-required-gate", helper_path.as_posix(), pattern)
        if "if (!masonryRequired)" not in js_block:
            add_finding(findings, pattern, "missing-js-masonry-text-suppression", helper_path.as_posix(), pattern)

    legacy_padding_patterns = [
        ("legacy-rect-x-inset", r'el\("rect",\s*\{[^\n}]*x:\s*(?:x|d\[0\])\s*\+'),
        ("legacy-rect-y-inset", r'el\("rect",\s*\{[^\n}]*y:\s*(?:y|d\[1\])\s*\+'),
        ("legacy-progress-inner-width", r"width:\s*(?:98|128|132|158|172|188|198|202|208|238)\s*\*\s*ease"),
        ("legacy-padded-meter-label", r"label\((?:x|d\[0\])\s*\+\s*(?:14|16)"),
        ("legacy-internal-blueprint-dots", r"(?i)blueprint_?colors?"),
        ("legacy-pillow-x1-inset", r"\bx1\s*\+\s*(?:14|16|18|20|24|28|32)\b"),
        ("legacy-pillow-y1-inset", r"\by1\s*\+\s*(?:14|16|18|20|24|28|32)\b"),
        ("legacy-pillow-y2-inset", r"\by2\s*-\s*(?:14|16|18|20|24|28|32|42)\b"),
    ]
    for code, pattern in legacy_padding_patterns:
        if re.search(pattern, helper):
            add_finding(findings, "global", code, helper_path.as_posix(), pattern)

    report = {
        "passed": not findings,
        "patternsChecked": len(PATTERNS),
        "findings": findings,
    }
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if not findings else 1


if __name__ == "__main__":
    raise SystemExit(main())
