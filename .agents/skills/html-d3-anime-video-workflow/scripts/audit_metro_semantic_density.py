#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


STATIC_STATE_KEYS = {
    "videoId",
    "seconds",
    "beat",
    "sourceFacts",
    "visualPattern",
}
CAMERA_STATE_KEYS = {
    "cameraX",
    "cameraY",
    "cameraScale",
    "cameraMoving",
}
MODULAR_TRANSITION_TYPES = {
    "block-expansion",
    "expanding-block",
    "masked-reframe",
    "masonry-construction",
    "surface-wipe",
    "tile-morph",
}


def read_json(path: Path | None, code: str) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    if path is None:
        return {}, []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return {}, [{"code": f"{code}-read-failed", "path": str(path), "error": str(exc)}]
    if not isinstance(data, dict):
        return {}, [{"code": f"{code}-not-object", "path": str(path)}]
    return data, []


def nested(data: dict[str, Any], path: str) -> Any:
    current: Any = data
    for part in path.split("."):
        if not isinstance(current, dict) or part not in current:
            return None
        current = current[part]
    return current


def optional_path(value: Any) -> Path | None:
    if isinstance(value, str) and value.strip():
        return Path(value)
    return None


def derive_source_package_path(wrapper: dict[str, Any]) -> Path | None:
    for value in nested(wrapper, "contract.requiredPaths") or []:
        if isinstance(value, str) and value.replace("\\", "/").endswith("/source/source-package.json"):
            return Path(value)
    return optional_path(nested(wrapper, "sourcePreservation.checked"))


def derive_rendered_frame_audit_path(wrapper: dict[str, Any], metro: dict[str, Any]) -> Path | None:
    for value in (
        nested(wrapper, "metroRenderedFrameAudit.manifest"),
        nested(wrapper, "metroAuditSuite.renderedFrameAudit.manifest"),
        nested(metro, "renderedFrameAudit.manifest"),
    ):
        path = optional_path(value)
        if path is not None:
            return path
    return None


def derive_mute_test_audit_path(wrapper: dict[str, Any], metro: dict[str, Any]) -> Path | None:
    for value in (
        nested(wrapper, "metroMuteTestAudit.manifest"),
        nested(wrapper, "metroAuditSuite.muteTestAudit.manifest"),
        nested(metro, "muteTestAudit.manifest"),
    ):
        path = optional_path(value)
        if path is not None:
            return path
    return None


def derive_video_composition_audit_path(
    wrapper: dict[str, Any],
    metro: dict[str, Any] | None = None,
    suite_path: Path | None = None,
) -> Path | None:
    for value in (
        nested(wrapper, "metroVideoCompositionAudit.manifest"),
        wrapper.get("metroVideoCompositionManifest"),
        nested(metro or {}, "videoCompositionAudit.manifest"),
        nested(metro or {}, "metroVideoCompositionAudit.manifest"),
    ):
        path = optional_path(value)
        if path is not None:
            return path
    if suite_path is not None:
        return suite_path.with_name("metro-video-composition-audit.json")
    return None


def bool_passed(value: Any) -> bool:
    return value is True


def summary_entry(summary: dict[str, Any], key: str) -> dict[str, Any]:
    entry = summary.get(key)
    return entry if isinstance(entry, dict) else {}


def numeric_value(entry: dict[str, Any], key: str, default: float = 0.0) -> float:
    value = entry.get(key)
    if isinstance(value, (int, float, bool)):
        return float(value)
    return default


def distinct_count(summary: dict[str, Any], key: str) -> int:
    return int(numeric_value(summary_entry(summary, key), "distinctCount"))


def max_value(summary: dict[str, Any], key: str) -> float:
    return numeric_value(summary_entry(summary, key), "max")


def state_summary(wrapper: dict[str, Any], state_manifest: dict[str, Any]) -> dict[str, Any]:
    for candidate in (
        state_manifest.get("stateSummary"),
        nested(wrapper, "stateCheck.stateSummary"),
    ):
        if isinstance(candidate, dict):
            return candidate
    return {}


def state_samples(wrapper: dict[str, Any], state_manifest: dict[str, Any]) -> list[dict[str, Any]]:
    for candidate in (
        state_manifest.get("statesSample"),
        nested(wrapper, "stateCheck.statesSample"),
    ):
        if isinstance(candidate, list):
            return [item for item in candidate if isinstance(item, dict)]
    return []


def contact_report(wrapper: dict[str, Any], contact_manifest: dict[str, Any]) -> dict[str, Any]:
    wrapper_contact = wrapper.get("contactSheet")
    wrapper_contact = wrapper_contact if isinstance(wrapper_contact, dict) else {}
    if not contact_manifest:
        return wrapper_contact
    merged = dict(contact_manifest)
    for key in ("openingTile", "finalTile", "openingTileAssessment"):
        if key not in merged and key in wrapper_contact:
            merged[key] = wrapper_contact[key]
    if "samples" not in merged and "samples" in wrapper_contact:
        merged["samples"] = wrapper_contact["samples"]
    return merged


def dynamic_state_keys(summary: dict[str, Any]) -> list[str]:
    keys: list[str] = []
    for key, entry in summary.items():
        if key in STATIC_STATE_KEYS or key in CAMERA_STATE_KEYS:
            continue
        if key.endswith("Labels") or key.endswith("labels"):
            continue
        if not isinstance(entry, dict):
            continue
        if numeric_value(entry, "distinctCount") >= 2:
            keys.append(key)
    return sorted(keys)


def camera_evidence(summary: dict[str, Any]) -> dict[str, Any]:
    x_entry = summary_entry(summary, "cameraX")
    y_entry = summary_entry(summary, "cameraY")
    scale_entry = summary_entry(summary, "cameraScale")
    x_min = numeric_value(x_entry, "min")
    x_max = numeric_value(x_entry, "max")
    y_min = numeric_value(y_entry, "min")
    y_max = numeric_value(y_entry, "max")
    scale_min = numeric_value(scale_entry, "min")
    scale_max = numeric_value(scale_entry, "max")
    return {
        "cameraMovingDistinct": distinct_count(summary, "cameraMoving"),
        "cameraMovingMax": max_value(summary, "cameraMoving"),
        "cameraXDistinct": distinct_count(summary, "cameraX"),
        "cameraYDistinct": distinct_count(summary, "cameraY"),
        "cameraScaleDistinct": distinct_count(summary, "cameraScale"),
        "cameraXRange": x_max - x_min,
        "cameraYRange": y_max - y_min,
        "cameraScaleMin": scale_min,
        "cameraScaleMax": scale_max,
        "cameraScaleRange": scale_max - scale_min,
    }


def contact_metrics(contact: dict[str, Any]) -> dict[str, Any]:
    metrics = contact.get("metrics")
    return metrics if isinstance(metrics, dict) else {}


def list_at(data: dict[str, Any], key: str) -> list[Any]:
    value = data.get(key)
    return value if isinstance(value, list) else []


def count_or_list_length(data: dict[str, Any], count_key: str, list_key: str) -> int:
    counts = data.get("patternCounts")
    if isinstance(counts, dict) and isinstance(counts.get(count_key), (int, float)):
        return int(counts[count_key])
    return len(list_at(data, list_key))


def numeric_contract_value(value: Any, default: float = 0.0) -> float:
    if isinstance(value, (int, float, bool)):
        return float(value)
    if isinstance(value, str):
        try:
            return float(value)
        except ValueError:
            return default
    return default


def normalized_token(value: Any) -> str:
    return " ".join(str(value or "").strip().lower().split())


def normalized_tokens(values: Any) -> set[str]:
    if not isinstance(values, list):
        return set()
    return {token for token in (normalized_token(value) for value in values) if token}


def source_anchor_values(source_package: dict[str, Any]) -> list[str]:
    anchors = source_package.get("strategyAnchors")
    return [str(anchor).strip() for anchor in anchors if str(anchor).strip()] if isinstance(anchors, list) else []


def source_anchor_set(source_package: dict[str, Any]) -> set[str]:
    return normalized_tokens(source_anchor_values(source_package))


def bindings_from_source_package(source_package: dict[str, Any]) -> list[dict[str, Any]]:
    bindings = source_package.get("semanticBindings")
    return [item for item in bindings if isinstance(item, dict)] if isinstance(bindings, list) else []


def anchor_set_from_bindings(bindings: list[dict[str, Any]]) -> set[str]:
    return {
        token
        for token in (normalized_token(binding.get("sourceAnchor")) for binding in bindings)
        if token
    }


def anchors_from_render_state_samples(samples: list[dict[str, Any]]) -> set[str]:
    anchors: set[str] = set()
    for sample in samples:
        state = sample.get("state") if isinstance(sample.get("state"), dict) else sample
        values = state.get("activeSourceAnchors")
        if isinstance(values, list):
            anchors.update(normalized_tokens(values))
        elif isinstance(values, str):
            anchors.add(normalized_token(values))
    anchors.discard("")
    return anchors


def pattern_mix_findings(
    pattern_mix: dict[str, Any],
    wrapper: dict[str, Any],
    source_package: dict[str, Any],
    args: argparse.Namespace,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    if not pattern_mix:
        if args.require_metro_pattern_mix:
            return [{"code": "missing-metro-pattern-mix", "path": "wrapper.metroPatternMix"}], {}
        return [], {}

    findings: list[dict[str, Any]] = []
    selected = pattern_mix.get("selected")
    selected = selected if isinstance(selected, dict) else {}
    helper_pattern = selected.get("helperPattern") or selected.get("suggestedScaffoldPattern")
    rendered_pattern = source_package.get("visualPattern") or nested(wrapper, "contract.pattern")

    if not bool_passed(pattern_mix.get("passed")):
        findings.append({"code": "metro-pattern-mix-not-passing", "actual": pattern_mix.get("passed")})
    if helper_pattern and rendered_pattern and helper_pattern != rendered_pattern:
        findings.append(
            {
                "code": "metro-pattern-mix-helper-mismatch",
                "helperPattern": helper_pattern,
                "renderedPattern": rendered_pattern,
            }
        )

    pattern_count = count_or_list_length(pattern_mix, "patternIdsNamed", "patternIdsNamed")
    used_count = count_or_list_length(pattern_mix, "patternsUsed", "patternsUsedInBeats")
    zones = list_at(pattern_mix, "functionalZones")
    motion_systems = list_at(pattern_mix, "semanticMotionSystems")
    camera_path = list_at(pattern_mix, "cameraPath")
    transitions = list_at(pattern_mix, "transitionContracts")
    risks = list_at(pattern_mix, "antiPatternRisks")
    pattern_ids = list_at(pattern_mix, "patternIdsNamed")
    pattern_id_set = {str(item) for item in pattern_ids if item is not None}
    pattern_evidence = set(pattern_id_set)
    for key in ("helperPattern", "suggestedScaffoldPattern", "primaryPattern", "secondaryPattern"):
        value = selected.get(key)
        if value:
            pattern_evidence.add(str(value))
    support_patterns = selected.get("supportPatterns")
    if isinstance(support_patterns, list):
        pattern_evidence.update(str(item) for item in support_patterns if item)
    for item in list_at(pattern_mix, "patternsUsedInBeats"):
        if isinstance(item, dict):
            for key in ("id", "pattern", "patternId"):
                value = item.get(key)
                if value:
                    pattern_evidence.add(str(value))
        elif item:
            pattern_evidence.add(str(item))
    for item in list_at(pattern_mix, "patternDetails"):
        if isinstance(item, dict):
            value = item.get("id")
            if value:
                pattern_evidence.add(str(value))
    zone_patterns = {
        str(zone.get("pattern"))
        for zone in zones
        if isinstance(zone, dict) and zone.get("pattern")
    }
    pattern_evidence.update(zone_patterns)
    zone_armatures = {
        str(zone.get("armature"))
        for zone in zones
        if isinstance(zone, dict) and zone.get("armature")
    }

    if pattern_count < args.min_mix_patterns:
        findings.append({"code": "too-few-mix-patterns", "minimum": args.min_mix_patterns, "actual": pattern_count})
    if used_count < args.min_mix_used_patterns:
        findings.append({"code": "too-few-mix-used-patterns", "minimum": args.min_mix_used_patterns, "actual": used_count})
    if len(zones) < args.min_mix_functional_zones:
        findings.append({"code": "too-few-mix-functional-zones", "minimum": args.min_mix_functional_zones, "actual": len(zones)})
    if len(motion_systems) < args.min_mix_motion_systems:
        findings.append({"code": "too-few-mix-motion-systems", "minimum": args.min_mix_motion_systems, "actual": len(motion_systems)})
    if len(camera_path) < args.min_mix_camera_events:
        findings.append({"code": "too-few-mix-camera-events", "minimum": args.min_mix_camera_events, "actual": len(camera_path)})
    if len(transitions) < args.min_mix_transitions:
        findings.append({"code": "too-few-mix-transition-contracts", "minimum": args.min_mix_transitions, "actual": len(transitions)})

    required_risks = set(args.require_mix_anti_pattern_risk or [])
    risk_ids = {str(item.get("id")) for item in risks if isinstance(item, dict)}
    missing_risks = sorted(required_risks - risk_ids)
    if missing_risks:
        findings.append({"code": "missing-mix-anti-pattern-risks", "missingRisks": missing_risks})

    zone_box_failures: list[dict[str, Any]] = []
    for zone in zones:
        if not isinstance(zone, dict):
            continue
        box = zone.get("boxModel")
        box = box if isinstance(box, dict) else {}
        if box.get("cornerRadius") not in (0, 0.0, "0", "0.0") or box.get("internalPaddingPx") not in (0, 0.0, "0", "0.0") or box.get("gridPx") not in (4, 4.0, "4", "4.0"):
            zone_box_failures.append({"zone": zone.get("id"), "boxModel": box})
    if zone_box_failures:
        findings.append({"code": "mix-zone-box-model-violations", "violations": zone_box_failures})

    constraints = pattern_mix.get("metroConstraints")
    constraints = constraints if isinstance(constraints, dict) else {}
    if constraints.get("cornerRadius") not in (0, 0.0, "0", "0.0"):
        findings.append({"code": "mix-corner-radius-not-zero", "actual": constraints.get("cornerRadius")})
    if constraints.get("internalBoxPaddingPx") not in (0, 0.0, "0", "0.0"):
        findings.append({"code": "mix-internal-padding-not-zero", "actual": constraints.get("internalBoxPaddingPx")})
    if numeric_contract_value(constraints.get("minimumGrayLevels")) < args.min_source_gray_levels:
        findings.append({"code": "mix-weak-gray-hierarchy-contract", "actual": constraints.get("minimumGrayLevels")})

    text_budget = pattern_mix.get("textBudget")
    text_budget = text_budget if isinstance(text_budget, dict) else {}
    if text_budget.get("visibleTextRole") != "functional-labels-only":
        findings.append({"code": "mix-text-budget-not-functional-labels-only", "actual": text_budget.get("visibleTextRole")})

    transition_types = [item.get("type") for item in transitions if isinstance(item, dict)]
    distinct_transition_types = {str(item) for item in transition_types if item}
    modular_transition_types = sorted(distinct_transition_types & MODULAR_TRANSITION_TYPES)
    masonry_contract = pattern_mix.get("masonryContract")
    masonry_contract = masonry_contract if isinstance(masonry_contract, dict) else {}
    masonry_required = bool(masonry_contract.get("required"))
    masonry_pattern_included = bool(
        masonry_contract.get("patternIncluded") is True
        and (
            "masonry-wall" in pattern_evidence
            or "masonry wall" in zone_armatures
        )
    )
    masonry_transition_included = bool(
        masonry_contract.get("transitionIncluded") is True
        and "masonry-construction" in distinct_transition_types
    )
    if len(distinct_transition_types) < args.min_mix_transition_types:
        findings.append(
            {
                "code": "too-few-mix-transition-types",
                "minimum": args.min_mix_transition_types,
                "actual": len(distinct_transition_types),
                "transitionTypes": sorted(distinct_transition_types),
            }
        )
    if args.require_modular_transition and not modular_transition_types:
        findings.append(
            {
                "code": "missing-modular-transition-type",
                "allowedTypes": sorted(MODULAR_TRANSITION_TYPES),
                "transitionTypes": sorted(distinct_transition_types),
            }
        )
    if masonry_required and not masonry_pattern_included:
        findings.append(
            {
                "code": "missing-required-masonry-pattern",
                "required": True,
                "contractPatternIncluded": masonry_contract.get("patternIncluded"),
                "patternEvidence": sorted(pattern_evidence),
                "zonePatterns": sorted(zone_patterns),
                "zoneArmatures": sorted(zone_armatures),
            }
        )
    if masonry_required and not masonry_transition_included:
        findings.append(
            {
                "code": "missing-required-masonry-transition",
                "required": True,
                "contractTransitionIncluded": masonry_contract.get("transitionIncluded"),
                "transitionTypes": sorted(distinct_transition_types),
            }
        )
    evidence = {
        "passed": pattern_mix.get("passed"),
        "helperPattern": helper_pattern,
        "renderedPattern": rendered_pattern,
        "primaryPattern": selected.get("primaryPattern"),
        "secondaryPattern": selected.get("secondaryPattern"),
        "patternIdsNamed": pattern_count,
        "patternsUsed": used_count,
        "functionalZones": len(zones),
        "semanticMotionSystems": len(motion_systems),
        "cameraEvents": len(camera_path),
        "transitionContracts": len(transitions),
        "transitionTypes": transition_types,
        "distinctTransitionTypeCount": len(distinct_transition_types),
        "modularTransitionTypes": modular_transition_types,
        "masonryContract": {
            "required": masonry_required,
            "contractPatternIncluded": masonry_contract.get("patternIncluded"),
            "contractTransitionIncluded": masonry_contract.get("transitionIncluded"),
            "patternIncluded": masonry_pattern_included,
            "transitionIncluded": masonry_transition_included,
            "patternEvidence": sorted(pattern_evidence),
        },
        "antiPatternRisks": sorted(risk_ids),
        "zoneBoxModelViolations": zone_box_failures,
    }
    return findings, evidence


def append_pass_findings(wrapper: dict[str, Any], state: dict[str, Any], contact: dict[str, Any], metro: dict[str, Any]) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []

    if wrapper and not bool_passed(wrapper.get("passed")):
        findings.append({"code": "wrapper-not-passing", "path": "wrapper.passed", "actual": wrapper.get("passed")})
    if state and not bool_passed(state.get("passed")):
        findings.append({"code": "state-manifest-not-passing", "path": "state.passed", "actual": state.get("passed")})
    if contact and not bool_passed(contact.get("passed")):
        findings.append({"code": "contact-sheet-not-passing", "path": "contact.passed", "actual": contact.get("passed")})
    if metro and not bool_passed(metro.get("passed")):
        findings.append({"code": "metro-suite-not-passing", "path": "metro.passed", "actual": metro.get("passed")})

    wrapper_state_passed = nested(wrapper, "stateCheck.passed")
    if wrapper_state_passed is not None and not bool_passed(wrapper_state_passed):
        findings.append({"code": "wrapper-state-check-not-passing", "path": "wrapper.stateCheck.passed", "actual": wrapper_state_passed})
    wrapper_metro_passed = nested(wrapper, "metroAuditSuite.passed")
    if wrapper_metro_passed is not None and not bool_passed(wrapper_metro_passed):
        findings.append({"code": "wrapper-metro-suite-not-passing", "path": "wrapper.metroAuditSuite.passed", "actual": wrapper_metro_passed})
    wrapper_contact_passed = nested(wrapper, "contactSheet.passed")
    if wrapper_contact_passed is not None and not bool_passed(wrapper_contact_passed):
        findings.append({"code": "wrapper-contact-sheet-not-passing", "path": "wrapper.contactSheet.passed", "actual": wrapper_contact_passed})

    missing_facts = nested(wrapper, "sourcePreservation.missingFacts")
    missing_anchors = nested(wrapper, "sourcePreservation.missingAnchors")
    if isinstance(missing_facts, list) and missing_facts:
        findings.append({"code": "missing-source-facts", "missingFacts": missing_facts})
    if isinstance(missing_anchors, list) and missing_anchors:
        findings.append({"code": "missing-source-anchors", "missingAnchors": missing_anchors})

    return findings


def source_package_findings(source_package: dict[str, Any], args: argparse.Namespace) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    if not source_package:
        return [], {}

    findings: list[dict[str, Any]] = []
    mechanisms = source_package.get("visualMechanisms")
    anchors = source_package.get("strategyAnchors")
    zones = source_package.get("visualZones")
    policy = source_package.get("visualPolicy")
    policy = policy if isinstance(policy, dict) else {}
    gray_levels = policy.get("grayLevels")
    expected_anchor_set = source_anchor_set(source_package)
    bindings = bindings_from_source_package(source_package)
    binding_anchor_set = anchor_set_from_bindings(bindings)

    mechanism_count = len(mechanisms) if isinstance(mechanisms, list) else 0
    anchor_count = len(anchors) if isinstance(anchors, list) else 0
    zones = zones if isinstance(zones, list) else []
    zone_count = len(zones)
    gray_level_count = len(gray_levels) if isinstance(gray_levels, list) else 0

    if mechanism_count < args.min_source_visual_mechanisms:
        findings.append({"code": "too-few-source-visual-mechanisms", "minimum": args.min_source_visual_mechanisms, "actual": mechanism_count})
    if anchor_count < args.min_source_anchors:
        findings.append({"code": "too-few-source-anchors", "minimum": args.min_source_anchors, "actual": anchor_count})
    if zone_count < args.min_source_visual_zones:
        findings.append({"code": "too-few-source-visual-zones", "minimum": args.min_source_visual_zones, "actual": zone_count})
    if policy.get("edgeStyle") != "square":
        findings.append({"code": "source-edge-style-not-square", "actual": policy.get("edgeStyle")})
    if policy.get("boxInteriorPolicy") != "zero":
        findings.append({"code": "source-box-interior-policy-not-zero", "actual": policy.get("boxInteriorPolicy")})
    if policy.get("internalPaddingPx") not in (0, 0.0, "0", "0.0"):
        findings.append({"code": "source-internal-padding-not-zero", "actual": policy.get("internalPaddingPx")})
    if gray_level_count < args.min_source_gray_levels:
        findings.append({"code": "too-few-source-gray-levels", "minimum": args.min_source_gray_levels, "actual": gray_level_count})

    zone_box_failures: list[dict[str, Any]] = []
    unanchored_zones: list[str] = []
    zone_anchor_set: set[str] = set()
    zone_ids: list[str] = []
    for zone in zones:
        if not isinstance(zone, dict):
            continue
        if isinstance(zone.get("id"), str):
            zone_ids.append(str(zone["id"]))
        zone_anchors = normalized_tokens(zone.get("sourceAnchors"))
        zone_anchor_set.update(zone_anchors)
        if args.require_source_anchor_map and not zone_anchors:
            unanchored_zones.append(str(zone.get("id") or zone.get("role") or "unknown-zone"))
        box = zone.get("boxModel")
        box = box if isinstance(box, dict) else {}
        if box.get("cornerRadius") not in (0, 0.0, "0", "0.0") or box.get("internalPaddingPx") not in (0, 0.0, "0", "0.0") or box.get("gridPx") not in (4, 4.0, "4", "4.0"):
            zone_box_failures.append({"zone": zone.get("id"), "boxModel": box})
    if zone_box_failures:
        findings.append({"code": "source-zone-box-model-violations", "violations": zone_box_failures})
    if unanchored_zones:
        findings.append({"code": "source-zones-missing-anchor-bindings", "zones": unanchored_zones[:12]})

    invalid_bindings = [
        binding
        for binding in bindings
        if not binding.get("sourceAnchor") or not binding.get("zoneId") or not binding.get("mechanismId") or not binding.get("stateKey")
    ]
    if args.require_source_anchor_map and not bindings:
        findings.append({"code": "missing-semantic-bindings", "path": "source-package.semanticBindings"})
    if invalid_bindings:
        findings.append({"code": "invalid-semantic-bindings", "count": len(invalid_bindings), "samples": invalid_bindings[:5]})
    zone_anchor_coverage_ratio = (len(expected_anchor_set & zone_anchor_set) / len(expected_anchor_set)) if expected_anchor_set else 1.0
    binding_anchor_coverage_ratio = (len(expected_anchor_set & binding_anchor_set) / len(expected_anchor_set)) if expected_anchor_set else 1.0
    anchored_zone_ratio = ((zone_count - len(unanchored_zones)) / zone_count) if zone_count else 1.0
    if args.require_source_anchor_map and zone_anchor_coverage_ratio < args.min_source_zone_anchor_coverage_ratio:
        findings.append(
            {
                "code": "source-zone-anchor-coverage-too-low",
                "minimum": args.min_source_zone_anchor_coverage_ratio,
                "actual": zone_anchor_coverage_ratio,
                "missingAnchors": sorted(expected_anchor_set - zone_anchor_set)[:12],
            }
        )
    if args.require_source_anchor_map and binding_anchor_coverage_ratio < args.min_source_binding_anchor_coverage_ratio:
        findings.append(
            {
                "code": "source-binding-anchor-coverage-too-low",
                "minimum": args.min_source_binding_anchor_coverage_ratio,
                "actual": binding_anchor_coverage_ratio,
                "missingAnchors": sorted(expected_anchor_set - binding_anchor_set)[:12],
            }
        )
    if args.require_source_anchor_map and anchored_zone_ratio < args.min_source_anchored_zone_ratio:
        findings.append(
            {
                "code": "source-anchored-zone-ratio-too-low",
                "minimum": args.min_source_anchored_zone_ratio,
                "actual": anchored_zone_ratio,
            }
        )

    evidence = {
        "visualPattern": source_package.get("visualPattern"),
        "visualMechanismCount": mechanism_count,
        "strategyAnchorCount": anchor_count,
        "visualZoneCount": zone_count,
        "visualZoneIds": zone_ids[:12],
        "zoneBoxModelViolations": zone_box_failures,
        "sourceAnchorBinding": {
            "semanticBindingCount": len(bindings),
            "expectedAnchorCount": len(expected_anchor_set),
            "zoneAnchorCoverageRatio": zone_anchor_coverage_ratio,
            "bindingAnchorCoverageRatio": binding_anchor_coverage_ratio,
            "anchoredZoneRatio": anchored_zone_ratio,
            "unanchoredZones": unanchored_zones[:12],
        },
        "visualPolicy": {
            "edgeStyle": policy.get("edgeStyle"),
            "boxInteriorPolicy": policy.get("boxInteriorPolicy"),
            "internalPaddingPx": policy.get("internalPaddingPx"),
            "grayLevelCount": gray_level_count,
        },
    }
    return findings, evidence


def rendered_frame_findings(
    rendered: dict[str, Any],
    args: argparse.Namespace,
    *,
    masonry_required: bool = False,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    if not rendered:
        return [], {}

    findings: list[dict[str, Any]] = []
    samples = rendered.get("samples")
    samples = samples if isinstance(samples, list) else []
    rect_counts = [item.get("rectCount") for item in samples if isinstance(item, dict) and isinstance(item.get("rectCount"), (int, float))]
    line_counts = [item.get("lineLikeCount") for item in samples if isinstance(item, dict) and isinstance(item.get("lineLikeCount"), (int, float))]
    gray_counts = [item.get("grayLevelCount") for item in samples if isinstance(item, dict) and isinstance(item.get("grayLevelCount"), (int, float))]

    def number(key: str, default: float = 0.0) -> float:
        value = rendered.get(key)
        return float(value) if isinstance(value, (int, float, bool)) else default

    if not bool_passed(rendered.get("passed")):
        findings.append({"code": "rendered-frame-audit-not-passing", "actual": rendered.get("passed")})
    if number("rectEdgeCount") < args.min_rendered_rect_edges:
        findings.append({"code": "too-few-rendered-rect-edges", "minimum": args.min_rendered_rect_edges, "actual": number("rectEdgeCount")})
    if number("minSharedEdgeRatio") < args.min_rendered_shared_edge_ratio:
        findings.append({"code": "weak-rendered-shared-edge-ratio", "minimum": args.min_rendered_shared_edge_ratio, "actual": number("minSharedEdgeRatio")})
    if number("offgridRatio") > args.max_rendered_offgrid_ratio:
        findings.append({"code": "rendered-offgrid-ratio-too-high", "maximum": args.max_rendered_offgrid_ratio, "actual": number("offgridRatio")})
    if number("medianGrayLevelCount") < args.min_rendered_median_gray_levels:
        findings.append({"code": "weak-rendered-median-gray-levels", "minimum": args.min_rendered_median_gray_levels, "actual": number("medianGrayLevelCount")})
    if number("finalGrayLevelCount") < args.min_rendered_final_gray_levels:
        findings.append({"code": "weak-rendered-final-gray-levels", "minimum": args.min_rendered_final_gray_levels, "actual": number("finalGrayLevelCount")})
    if number("graySamplePassRatio") < args.min_rendered_gray_sample_pass_ratio:
        findings.append({"code": "weak-rendered-gray-sample-pass-ratio", "minimum": args.min_rendered_gray_sample_pass_ratio, "actual": number("graySamplePassRatio")})
    if number("maxRenderedInternalPaddingPx") > args.max_rendered_internal_padding_px:
        findings.append({"code": "rendered-internal-padding-too-high", "maximum": args.max_rendered_internal_padding_px, "actual": number("maxRenderedInternalPaddingPx")})
    if number("medianTextAreaRatio") > args.max_rendered_median_text_area_ratio:
        findings.append(
            {
                "code": "rendered-text-area-too-high",
                "maximum": args.max_rendered_median_text_area_ratio,
                "actual": number("medianTextAreaRatio"),
            }
        )
    if number("maxLargestTextBoxAreaRatio") > args.max_rendered_largest_text_box_area_ratio:
        findings.append(
            {
                "code": "rendered-dominant-text-box",
                "maximum": args.max_rendered_largest_text_box_area_ratio,
                "actual": number("maxLargestTextBoxAreaRatio"),
            }
        )
    if number("medianMarkToTextRatio") < args.min_rendered_median_mark_to_text_ratio:
        findings.append(
            {
                "code": "weak-rendered-mark-to-text-density",
                "minimum": args.min_rendered_median_mark_to_text_ratio,
                "actual": number("medianMarkToTextRatio"),
            }
        )
    if number("titleBandTextCount") > args.max_rendered_title_band_text_count:
        findings.append(
            {
                "code": "rendered-title-band-text",
                "maximum": args.max_rendered_title_band_text_count,
                "actual": number("titleBandTextCount"),
            }
        )
    if number("ellipsizedTextCount") > args.max_rendered_ellipsized_text_count:
        findings.append(
            {
                "code": "rendered-ellipsized-text",
                "maximum": args.max_rendered_ellipsized_text_count,
                "actual": number("ellipsizedTextCount"),
            }
        )
    if number("zeroPaddingGeometryViolationCount") > 0:
        findings.append({"code": "rendered-zero-padding-violations", "actual": number("zeroPaddingGeometryViolationCount")})
    if number("untaggedInsetRectViolationCount") > 0:
        findings.append({"code": "rendered-untagged-inset-violations", "actual": number("untaggedInsetRectViolationCount")})
    if number("paddedModuleInteriorViolationCount") > 0:
        findings.append({"code": "rendered-padded-module-interiors", "actual": number("paddedModuleInteriorViolationCount")})
    if number("maxZoneElementCount") < args.min_rendered_zone_elements:
        findings.append(
            {
                "code": "too-few-rendered-zone-elements",
                "minimum": args.min_rendered_zone_elements,
                "actual": number("maxZoneElementCount"),
            }
        )
    if number("maxZoneIdCount") < args.min_rendered_zone_elements:
        findings.append(
            {
                "code": "too-few-rendered-zone-ids",
                "minimum": args.min_rendered_zone_elements,
                "actual": number("maxZoneIdCount"),
            }
        )
    if masonry_required and number("maxMasonryModuleCount") < 6:
        findings.append(
            {
                "code": "too-few-rendered-masonry-modules",
                "minimum": 6,
                "actual": number("maxMasonryModuleCount"),
            }
        )
    if masonry_required and number("maxMasonrySizeCount") < 4:
        findings.append(
            {
                "code": "weak-rendered-masonry-size-variety",
                "minimum": 4,
                "actual": number("maxMasonrySizeCount"),
            }
        )
    if masonry_required and number("maxMasonryAreaRatio") < 0.35:
        findings.append(
            {
                "code": "rendered-masonry-area-too-small",
                "minimum": 0.35,
                "actual": number("maxMasonryAreaRatio"),
            }
        )
    if masonry_required and number("masonryModuleCountDistinct") < 3:
        findings.append(
            {
                "code": "missing-rendered-masonry-construction",
                "minimum": 3,
                "actual": number("masonryModuleCountDistinct"),
            }
        )
    if masonry_required and number("masonryModuleCountRange") < 4:
        findings.append(
            {
                "code": "weak-rendered-masonry-construction-growth",
                "minimum": 4,
                "actual": number("masonryModuleCountRange"),
            }
        )
    if masonry_required and rendered.get("masonryModuleCountNondecreasing") is False:
        findings.append({"code": "rendered-masonry-construction-regression"})
    if masonry_required and number("maxTextElementCount") > 6:
        findings.append(
            {
                "code": "rendered-masonry-too-text-led",
                "maximumTextElements": 6,
                "actual": number("maxTextElementCount"),
            }
        )
    if masonry_required and number("maxTextCharacterCount") > 80:
        findings.append(
            {
                "code": "rendered-masonry-too-many-text-characters",
                "maximumTextCharacters": 80,
                "actual": number("maxTextCharacterCount"),
            }
        )
    if rect_counts and min(rect_counts) < args.min_rendered_sample_rects:
        findings.append({"code": "too-few-rendered-sample-rects", "minimum": args.min_rendered_sample_rects, "actualMin": min(rect_counts)})
    if line_counts and min(line_counts) < args.min_rendered_sample_lines:
        findings.append({"code": "too-few-rendered-sample-lines", "minimum": args.min_rendered_sample_lines, "actualMin": min(line_counts)})

    evidence = {
        "rectEdgeCount": number("rectEdgeCount"),
        "minSharedEdgeRatio": number("minSharedEdgeRatio"),
        "offgridRatio": number("offgridRatio"),
        "medianGrayLevelCount": number("medianGrayLevelCount"),
        "finalGrayLevelCount": number("finalGrayLevelCount"),
        "graySamplePassRatio": number("graySamplePassRatio"),
        "maxRenderedInternalPaddingPx": number("maxRenderedInternalPaddingPx"),
        "maxRedRectAreaRatio": number("maxRedRectAreaRatio"),
        "medianRedRectAreaRatio": number("medianRedRectAreaRatio"),
        "medianTextAreaRatio": number("medianTextAreaRatio"),
        "maxLargestTextBoxAreaRatio": number("maxLargestTextBoxAreaRatio"),
        "medianMarkToTextRatio": number("medianMarkToTextRatio"),
        "maxTextElementCount": number("maxTextElementCount"),
        "maxTextCharacterCount": number("maxTextCharacterCount"),
        "titleBandTextCount": number("titleBandTextCount"),
        "ellipsizedTextCount": number("ellipsizedTextCount"),
        "zeroPaddingGeometryViolationCount": number("zeroPaddingGeometryViolationCount"),
        "untaggedInsetRectViolationCount": number("untaggedInsetRectViolationCount"),
        "paddedModuleInteriorViolationCount": number("paddedModuleInteriorViolationCount"),
        "maxZoneElementCount": number("maxZoneElementCount"),
        "maxZoneIdCount": number("maxZoneIdCount"),
        "maxActiveZoneCount": number("maxActiveZoneCount"),
        "sourceAnchorCount": number("sourceAnchorCount"),
        "sourceAnchors": rendered.get("sourceAnchors"),
        "semanticBindingCount": number("semanticBindingCount"),
        "semanticBindings": rendered.get("semanticBindings"),
        "masonryRequired": masonry_required,
        "maxMasonryModuleCount": number("maxMasonryModuleCount"),
        "minMasonryModuleCount": number("minMasonryModuleCount"),
        "masonryModuleCountRange": number("masonryModuleCountRange"),
        "masonryModuleCountDistinct": number("masonryModuleCountDistinct"),
        "masonryModuleCountNondecreasing": rendered.get("masonryModuleCountNondecreasing"),
        "masonryModuleCounts": rendered.get("masonryModuleCounts"),
        "maxMasonrySizeCount": number("maxMasonrySizeCount"),
        "maxMasonryAreaRatio": number("maxMasonryAreaRatio"),
        "sampleCount": len(samples),
        "minSampleRectCount": min(rect_counts) if rect_counts else None,
        "minSampleLineLikeCount": min(line_counts) if line_counts else None,
        "minSampleGrayLevelCount": min(gray_counts) if gray_counts else None,
    }
    return findings, evidence


def mute_test_findings(mute: dict[str, Any], args: argparse.Namespace) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    if not mute:
        return [], {}

    findings: list[dict[str, Any]] = []

    def number(key: str, default: float = 0.0) -> float:
        value = mute.get(key)
        return float(value) if isinstance(value, (int, float, bool)) else default

    if not bool_passed(mute.get("passed")):
        findings.append({"code": "mute-test-audit-not-passing", "actual": mute.get("passed")})
    if number("hiddenChangingPairs") < args.min_mute_hidden_changing_pairs:
        findings.append(
            {
                "code": "mute-test-hidden-motion-too-weak",
                "minimum": args.min_mute_hidden_changing_pairs,
                "actual": number("hiddenChangingPairs"),
            }
        )
    if number("medianHiddenChangeRatio") < args.min_mute_median_hidden_change_ratio:
        findings.append(
            {
                "code": "mute-test-hidden-change-ratio-too-low",
                "minimum": args.min_mute_median_hidden_change_ratio,
                "actual": number("medianHiddenChangeRatio"),
            }
        )
    if number("medianHiddenToFullChangeRatio") < args.min_mute_hidden_to_full_change_ratio:
        findings.append(
            {
                "code": "mute-test-text-carries-motion",
                "minimum": args.min_mute_hidden_to_full_change_ratio,
                "actual": number("medianHiddenToFullChangeRatio"),
            }
        )
    if number("medianHiddenNonbackgroundRatio") < args.min_mute_hidden_nonbackground_ratio:
        findings.append(
            {
                "code": "mute-test-hidden-visual-area-too-low",
                "minimum": args.min_mute_hidden_nonbackground_ratio,
                "actual": number("medianHiddenNonbackgroundRatio"),
            }
        )
    if number("medianHiddenMarkCount") < args.min_mute_hidden_mark_count:
        findings.append(
            {
                "code": "mute-test-too-few-hidden-marks",
                "minimum": args.min_mute_hidden_mark_count,
                "actual": number("medianHiddenMarkCount"),
            }
        )
    if number("maxHiddenZoneElementCount") < args.min_mute_hidden_zone_elements:
        findings.append(
            {
                "code": "mute-test-too-few-zone-elements",
                "minimum": args.min_mute_hidden_zone_elements,
                "actual": number("maxHiddenZoneElementCount"),
            }
        )
    if number("medianHiddenGrayLevelCount") < args.min_mute_hidden_gray_levels:
        findings.append(
            {
                "code": "mute-test-weak-hidden-gray-hierarchy",
                "minimum": args.min_mute_hidden_gray_levels,
                "actual": number("medianHiddenGrayLevelCount"),
            }
        )

    evidence = {
        "hiddenChangingPairs": number("hiddenChangingPairs"),
        "medianHiddenChangeRatio": number("medianHiddenChangeRatio"),
        "medianHiddenToFullChangeRatio": number("medianHiddenToFullChangeRatio"),
        "medianHiddenNonbackgroundRatio": number("medianHiddenNonbackgroundRatio"),
        "minHiddenColorBuckets": number("minHiddenColorBuckets"),
        "medianHiddenMarkCount": number("medianHiddenMarkCount"),
        "maxHiddenZoneElementCount": number("maxHiddenZoneElementCount"),
        "medianHiddenGrayLevelCount": number("medianHiddenGrayLevelCount"),
        "sampleCount": len(mute.get("samples")) if isinstance(mute.get("samples"), list) else None,
    }
    return findings, evidence


def video_composition_findings(video_composition: dict[str, Any], args: argparse.Namespace) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    summary = video_composition.get("summary")
    summary = summary if isinstance(summary, dict) else {}

    def number(key: str, default: float = 0.0) -> float:
        return numeric_contract_value(summary.get(key), default)

    if not video_composition:
        findings.append({"code": "missing-mp4-composition-audit"})
        return findings, {}
    if video_composition.get("passed") is not True:
        findings.append({"code": "mp4-composition-audit-not-passing", "actual": video_composition.get("passed")})
    if number("minGridCoverage") < args.min_mp4_grid_coverage:
        findings.append(
            {
                "code": "mp4-weak-grid-coverage",
                "minimum": args.min_mp4_grid_coverage,
                "actual": number("minGridCoverage"),
            }
        )
    if number("medianGridCoverage") < args.min_mp4_median_grid_coverage:
        findings.append(
            {
                "code": "mp4-weak-median-grid-coverage",
                "minimum": args.min_mp4_median_grid_coverage,
                "actual": number("medianGridCoverage"),
            }
        )
    if number("minQuadrantsWithContent") < args.min_mp4_quadrants_with_content:
        findings.append(
            {
                "code": "mp4-weak-quadrant-coverage",
                "minimum": args.min_mp4_quadrants_with_content,
                "actual": number("minQuadrantsWithContent"),
            }
        )
    if number("openingGridCoverageRatio") < args.min_mp4_opening_grid_coverage_ratio:
        findings.append(
            {
                "code": "mp4-weak-opening-composition",
                "minimum": args.min_mp4_opening_grid_coverage_ratio,
                "actual": number("openingGridCoverageRatio"),
            }
        )
    if number("spatialChangingPairs") < args.min_mp4_spatial_change_pairs:
        findings.append(
            {
                "code": "mp4-weak-spatial-progression",
                "minimum": args.min_mp4_spatial_change_pairs,
                "actual": number("spatialChangingPairs"),
            }
        )
    if number("maxTextLikeComponentAreaRatio") > args.max_mp4_text_like_component_area_ratio:
        findings.append(
            {
                "code": "mp4-text-like-component-pressure",
                "maximum": args.max_mp4_text_like_component_area_ratio,
                "actual": number("maxTextLikeComponentAreaRatio"),
            }
        )
    if number("maxRedAreaRatio") > args.max_mp4_red_area_ratio:
        findings.append(
            {
                "code": "mp4-red-area-too-dominant",
                "maximum": args.max_mp4_red_area_ratio,
                "actual": number("maxRedAreaRatio"),
            }
        )
    evidence = {
        "minGridCoverage": number("minGridCoverage"),
        "medianGridCoverage": number("medianGridCoverage"),
        "minQuadrantsWithContent": number("minQuadrantsWithContent"),
        "openingGridCoverageRatio": number("openingGridCoverageRatio"),
        "spatialChangingPairs": number("spatialChangingPairs"),
        "maxTitleBandDominance": number("maxTitleBandDominance"),
        "maxTextLikeComponentAreaRatio": number("maxTextLikeComponentAreaRatio"),
        "maxRedAreaRatio": number("maxRedAreaRatio"),
        "medianRedAreaRatio": number("medianRedAreaRatio"),
    }
    return findings, evidence


def continuity_findings(
    samples: list[dict[str, Any]],
    pattern_mix: dict[str, Any],
    args: argparse.Namespace,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    if not samples:
        return [{"code": "missing-state-sample-continuity", "path": "state.statesSample"}], {}

    ordered = sorted(samples, key=lambda item: numeric_contract_value(item.get("seconds"), 0.0))
    states: list[dict[str, Any]] = []
    for item in ordered:
        state = item.get("state")
        if isinstance(state, dict):
            states.append(state)

    findings: list[dict[str, Any]] = []
    if len(states) < args.min_continuity_samples:
        findings.append({"code": "too-few-continuity-samples", "minimum": args.min_continuity_samples, "actual": len(states)})

    zone_sequence = [str(state.get("activeZoneId")) for state in states if state.get("activeZoneId") not in (None, "")]
    beat_sequence = [state.get("beat") for state in states]
    camera_sequence = [
        (
            numeric_contract_value(state.get("cameraX"), 0.0),
            numeric_contract_value(state.get("cameraY"), 0.0),
            numeric_contract_value(state.get("cameraScale"), 1.0),
        )
        for state in states
    ]
    mechanism_sequence = [numeric_contract_value(state.get("visibleMechanismCount"), 0.0) for state in states]

    zone_adjacent_changes = 0
    beat_adjacent_changes = 0
    camera_adjacent_changes = 0
    zone_camera_coupled_changes = 0
    for index in range(1, len(states)):
        zone_changed = index < len(zone_sequence) and zone_sequence[index] != zone_sequence[index - 1]
        beat_changed = beat_sequence[index] != beat_sequence[index - 1]
        previous_camera = camera_sequence[index - 1]
        current_camera = camera_sequence[index]
        camera_delta = (
            abs(current_camera[0] - previous_camera[0]),
            abs(current_camera[1] - previous_camera[1]),
            abs(current_camera[2] - previous_camera[2]),
        )
        camera_changed = (
            camera_delta[0] >= args.min_continuity_camera_delta_px
            or camera_delta[1] >= args.min_continuity_camera_delta_px
            or camera_delta[2] >= args.min_continuity_camera_scale_delta
        )
        if zone_changed:
            zone_adjacent_changes += 1
        if beat_changed:
            beat_adjacent_changes += 1
        if camera_changed:
            camera_adjacent_changes += 1
        if zone_changed and camera_changed:
            zone_camera_coupled_changes += 1

    transitions = list_at(pattern_mix, "transitionContracts") if pattern_mix else []
    transition_count = len(transitions)
    required_zone_changes = max(args.min_continuity_zone_changes, min(transition_count, args.min_mix_transitions))
    required_coupled_changes = max(args.min_continuity_camera_coupled_changes, min(transition_count, args.min_mix_transitions))
    if zone_adjacent_changes < required_zone_changes:
        findings.append(
            {
                "code": "weak-zone-continuity-path",
                "minimumAdjacentZoneChanges": required_zone_changes,
                "actualAdjacentZoneChanges": zone_adjacent_changes,
                "activeZoneSequence": zone_sequence,
            }
        )
    if zone_camera_coupled_changes < required_coupled_changes:
        findings.append(
            {
                "code": "weak-camera-zone-coupling",
                "minimumCoupledChanges": required_coupled_changes,
                "actualCoupledChanges": zone_camera_coupled_changes,
                "cameraAdjacentChanges": camera_adjacent_changes,
                "activeZoneSequence": zone_sequence,
            }
        )

    evidence = {
        "sampleCount": len(states),
        "activeZoneSequence": zone_sequence,
        "beatSequence": beat_sequence,
        "visibleMechanismSequence": mechanism_sequence,
        "adjacentZoneChanges": zone_adjacent_changes,
        "adjacentBeatChanges": beat_adjacent_changes,
        "cameraAdjacentChanges": camera_adjacent_changes,
        "zoneCameraCoupledChanges": zone_camera_coupled_changes,
        "transitionContractCount": transition_count,
        "transitionCoverageRatio": zone_adjacent_changes / max(transition_count, 1),
        "cameraCouplingRatio": zone_camera_coupled_changes / max(zone_adjacent_changes, 1),
    }
    return findings, evidence


def semantic_binding_findings(
    source_package: dict[str, Any],
    rendered: dict[str, Any],
    samples: list[dict[str, Any]],
    args: argparse.Namespace,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    if not args.require_source_anchor_map:
        return [], {}
    expected = source_anchor_set(source_package)
    if not expected:
        return [], {}
    bindings = bindings_from_source_package(source_package)
    binding_anchors = anchor_set_from_bindings(bindings)
    rendered_anchors = normalized_tokens(rendered.get("sourceAnchors"))
    state_anchors = anchors_from_render_state_samples(samples)
    bound_everywhere = expected & binding_anchors & rendered_anchors & state_anchors
    rendered_coverage = len(expected & rendered_anchors) / len(expected)
    state_coverage = len(expected & state_anchors) / len(expected)
    binding_coverage = len(expected & binding_anchors) / len(expected)
    visual_binding_coverage = len(bound_everywhere) / len(expected)
    findings: list[dict[str, Any]] = []
    if rendered_coverage < args.min_rendered_source_anchor_coverage_ratio:
        findings.append(
            {
                "code": "rendered-source-anchor-coverage-too-low",
                "minimum": args.min_rendered_source_anchor_coverage_ratio,
                "actual": rendered_coverage,
                "missingAnchors": sorted(expected - rendered_anchors)[:12],
            }
        )
    if state_coverage < args.min_state_source_anchor_coverage_ratio:
        findings.append(
            {
                "code": "state-source-anchor-coverage-too-low",
                "minimum": args.min_state_source_anchor_coverage_ratio,
                "actual": state_coverage,
                "missingAnchors": sorted(expected - state_anchors)[:12],
            }
        )
    if visual_binding_coverage < args.min_source_anchor_visual_binding_coverage_ratio:
        findings.append(
            {
                "code": "semantic-binding-coverage-too-low",
                "minimum": args.min_source_anchor_visual_binding_coverage_ratio,
                "actual": visual_binding_coverage,
                "missingAnchors": sorted(expected - bound_everywhere)[:12],
            }
        )
    evidence = {
        "expectedAnchorCount": len(expected),
        "semanticBindingCount": len(bindings),
        "bindingCoverageRatio": binding_coverage,
        "renderedCoverageRatio": rendered_coverage,
        "stateCoverageRatio": state_coverage,
        "sourceAnchorVisualBindingCoverage": visual_binding_coverage,
        "boundEverywhereCount": len(bound_everywhere),
        "expectedAnchors": sorted(expected)[:20],
        "renderedAnchors": sorted(rendered_anchors)[:20],
        "stateAnchors": sorted(state_anchors)[:20],
    }
    return findings, evidence


def agent_loop_motif_requested(source_package: dict[str, Any]) -> bool:
    anchors = source_anchor_values(source_package)
    values = [
        source_package.get("title"),
        source_package.get("topic"),
        *(anchors or []),
        *(source_package.get("systemLabels") or []),
    ]
    haystack = " ".join(str(value) for value in values if value is not None).lower()
    signals = [
        "agent_loop_ring",
        "context_window_box",
        "model + tools + state + loop",
        "fixed workflow",
        "adaptive agent",
        "approval checkpoint",
        "environment changes",
    ]
    return sum(1 for signal in signals if signal in haystack) >= 2


def sample_sequence(samples: list[dict[str, Any]], key: str) -> list[Any]:
    values: list[Any] = []
    for sample in samples:
        if key in sample:
            values.append(sample.get(key))
            continue
        nested_state = sample.get("state")
        if isinstance(nested_state, dict) and key in nested_state:
            values.append(nested_state.get(key))
    return values


def agent_loop_motif_findings(
    summary: dict[str, Any],
    samples: list[dict[str, Any]],
    source_package: dict[str, Any],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    if not agent_loop_motif_requested(source_package):
        return [], {}
    findings: list[dict[str, Any]] = []
    required_flags = [
        "agentLoopRingVisible",
        "toolActionLoopVisible",
        "fixedWorkflowLaneVisible",
        "adaptiveAgentLaneVisible",
        "approvalCheckpointVisible",
        "modelToolsStateLoopBadgeVisible",
    ]
    flag_evidence: dict[str, Any] = {}
    for key in required_flags:
        actual = max_value(summary, key)
        flag_evidence[key] = {
            "max": actual,
            "sequence": sample_sequence(samples, key),
        }
        if actual < 1:
            findings.append({"code": "missing-agent-loop-motif-state", "stateKey": key})

    context_pane_max = max_value(summary, "contextPaneCount")
    environment_surface_max = max_value(summary, "environmentSurfaceCount")
    environment_distinct = distinct_count(summary, "environmentState")
    if context_pane_max < 4:
        findings.append(
            {
                "code": "too-few-agent-context-panes",
                "minimumMax": 4,
                "actualMax": context_pane_max,
            }
        )
    if environment_surface_max < 4:
        findings.append(
            {
                "code": "too-few-agent-environment-surfaces",
                "minimumMax": 4,
                "actualMax": environment_surface_max,
            }
        )
    if environment_distinct < 3:
        findings.append(
            {
                "code": "weak-agent-environment-state-progression",
                "minimumDistinct": 3,
                "actualDistinct": environment_distinct,
            }
        )
    evidence = {
        "requested": True,
        "flags": flag_evidence,
        "contextPaneCountMax": context_pane_max,
        "contextPaneCountSequence": sample_sequence(samples, "contextPaneCount"),
        "environmentSurfaceCountMax": environment_surface_max,
        "environmentStateDistinct": environment_distinct,
        "environmentStateSequence": sample_sequence(samples, "environmentState"),
    }
    return findings, evidence


def guardrail_motif_requested(source_package: dict[str, Any]) -> bool:
    anchors = source_anchor_values(source_package)
    values = [
        source_package.get("title"),
        source_package.get("topic"),
        *(anchors or []),
        *(source_package.get("threatLabels") or []),
        *(source_package.get("barrierLabels") or []),
        *(source_package.get("consequenceLabels") or []),
    ]
    haystack = " ".join(str(value) for value in values if value is not None).lower()
    if "what is a guardrail" in haystack or "model armor" in haystack:
        return True
    # Do not let a generic "active guardrails" narration phrase in a Hook video
    # activate the full guardrail contract. Require concrete gate/risk motifs.
    strong_signals = [
        "input / output / action",
        "input gate",
        "output gate",
        "action gate",
        "risk_score",
        "risk score",
        "human approval",
        "policy matrix",
        "protected .env",
        "destructive",
        "deploy action",
        "safety-versus-friction",
        "safety friction",
    ]
    return sum(1 for signal in strong_signals if signal in haystack) >= 2


def harness_motif_requested(source_package: dict[str, Any]) -> bool:
    anchors = source_anchor_values(source_package)
    values = [
        source_package.get("title"),
        source_package.get("topic"),
        *(anchors or []),
        *(source_package.get("systemLabels") or []),
    ]
    haystack = " ".join(str(value) for value in values if value is not None).lower()
    if "harness hook" in haystack or "harness plugin" in haystack:
        return False
    if (
        "what ai alternatives we have" in haystack
        or "ai alternatives" in haystack
        or sum(
            1
            for signal in (
                "atlassian rovo",
                "gemini app",
                "github copilot",
                "claude desktop",
                "claude code",
                "workflow gravity",
                "home base",
                "use-case selector",
            )
            if signal in haystack
        )
        >= 2
    ):
        return False
    signals = [
        "comparison_grid",
        "runtime stack",
        "runtime wrapper",
        "engine icon",
        "vehicle dashboard",
        "same model",
        "different shells",
        "three-column harness",
        "credit_meter",
        "feature grid",
        "use-case matrix",
        "selection path",
        "what is a harness",
    ]
    return sum(1 for signal in signals if signal in haystack) >= 2 or "what is a harness" in haystack


def hook_motif_requested(source_package: dict[str, Any]) -> bool:
    anchors = source_anchor_values(source_package)
    values = [
        source_package.get("title"),
        source_package.get("topic"),
        *(anchors or []),
        *(source_package.get("systemLabels") or []),
    ]
    haystack = " ".join(str(value) for value in values if value is not None).lower()
    if "harness plugin" in haystack:
        return False
    signals = [
        "harness hook",
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
    ]
    return sum(1 for signal in signals if signal in haystack) >= 2 or "what is a harness hook" in haystack


def plugin_motif_requested(source_package: dict[str, Any]) -> bool:
    anchors = source_anchor_values(source_package)
    values = [
        source_package.get("title"),
        source_package.get("topic"),
        *(anchors or []),
        *(source_package.get("laneLabels") or []),
        *(source_package.get("handoffLabels") or []),
    ]
    haystack = " ".join(str(value) for value in values if value is not None).lower()
    signals = [
        "harness plugin",
        "plugin_bundle_cube",
        "packaged harness behavior",
        "installable unit",
        "distribution mechanism",
        "marketplace",
        "allowlist",
        "npm",
        "version",
        "govern",
        "noisy plugin",
        "github plugin manifest",
        "claude marketplace",
        "opencode runtime",
        "package-install",
    ]
    return sum(1 for signal in signals if signal in haystack) >= 2 or "what is a harness plugin" in haystack


def ai_alternatives_motif_requested(source_package: dict[str, Any]) -> bool:
    anchors = source_anchor_values(source_package)
    values = [
        source_package.get("title"),
        source_package.get("topic"),
        *(anchors or []),
        *(source_package.get("laneLabels") or []),
        *(source_package.get("handoffLabels") or []),
        *(source_package.get("systemLabels") or []),
        *(source_package.get("visualMechanisms") or []),
    ]
    haystack = " ".join(str(value) for value in values if value is not None).lower()
    signals = [
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
    ]
    return sum(1 for signal in signals if signal in haystack) >= 3 or "what ai alternatives we have" in haystack


def skill_motif_requested(source_package: dict[str, Any]) -> bool:
    anchors = source_anchor_values(source_package)
    values = [
        source_package.get("title"),
        source_package.get("topic"),
        *(anchors or []),
        *(source_package.get("systemLabels") or []),
        *(source_package.get("visualMechanisms") or []),
    ]
    haystack = " ".join(str(value) for value in values if value is not None).lower()
    if "skill-tree" in haystack or "skill tree" in haystack or "path of exile" in haystack:
        return False
    signals = [
        "what is a skill",
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
    ]
    return sum(1 for signal in signals if signal in haystack) >= 2 or "what is a skill" in haystack


def skill_motif_findings(
    summary: dict[str, Any],
    samples: list[dict[str, Any]],
    source_package: dict[str, Any],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    if not skill_motif_requested(source_package):
        return [], {}
    findings: list[dict[str, Any]] = []
    required_flags = [
        "skillCardStackVisible",
        "skillManifestVisible",
        "frontmatterContractVisible",
        "triggerSurfaceVisible",
        "promptWallCollapsed",
        "folderStructuresAligned",
        "progressiveDisclosureVisible",
        "skillActivationVisible",
        "exampleSkillCardsVisible",
        "toolBadgesAttached",
        "scriptBlockVisible",
        "bloatedSkillTrimmed",
        "finalWorkflowStampVisible",
        "resourceBundleVisible",
        "validationHarnessVisible",
        "readSurfaceVisible",
    ]
    flag_evidence: dict[str, Any] = {}
    for key in required_flags:
        actual = max_value(summary, key)
        flag_evidence[key] = {
            "max": actual,
            "sequence": sample_sequence(samples, key),
        }
        if actual < 1:
            findings.append({"code": "missing-skill-motif-state", "stateKey": key})

    skill_file_layer_max = max_value(summary, "skillFileLayerCount")
    trigger_example_max = max_value(summary, "triggerExampleCount")
    resource_module_max = max_value(summary, "resourceModuleCount")
    validation_stage_max = max_value(summary, "validationStageLevel")
    read_surface_max = max_value(summary, "readSurfaceLevel")
    cost_meter_max = max_value(summary, "costMeterLevel")
    skill_file_layer_distinct = distinct_count(summary, "skillFileLayerCount")
    trigger_example_distinct = distinct_count(summary, "triggerExampleCount")
    resource_module_distinct = distinct_count(summary, "resourceModuleCount")
    validation_stage_distinct = distinct_count(summary, "validationStageLevel")
    read_surface_distinct = distinct_count(summary, "readSurfaceLevel")
    cost_meter_distinct = distinct_count(summary, "costMeterLevel")

    if skill_file_layer_max < 4:
        findings.append({"code": "too-few-skill-file-layers", "minimumMax": 4, "actualMax": skill_file_layer_max})
    if trigger_example_max < 5:
        findings.append({"code": "too-few-skill-trigger-examples", "minimumMax": 5, "actualMax": trigger_example_max})
    if resource_module_max < 4:
        findings.append({"code": "too-few-skill-resource-modules", "minimumMax": 4, "actualMax": resource_module_max})
    if validation_stage_max < 5:
        findings.append({"code": "weak-skill-validation-stage-level", "minimumMax": 5, "actualMax": validation_stage_max})
    if read_surface_max < 4:
        findings.append({"code": "weak-skill-read-surface-level", "minimumMax": 4, "actualMax": read_surface_max})
    if cost_meter_max < 4:
        findings.append({"code": "weak-skill-cost-meter-level", "minimumMax": 4, "actualMax": cost_meter_max})
    if skill_file_layer_distinct < 3:
        findings.append({"code": "weak-skill-file-layer-progression", "minimumDistinct": 3, "actualDistinct": skill_file_layer_distinct})
    if trigger_example_distinct < 3:
        findings.append({"code": "weak-skill-trigger-example-progression", "minimumDistinct": 3, "actualDistinct": trigger_example_distinct})
    if resource_module_distinct < 3:
        findings.append({"code": "weak-skill-resource-module-progression", "minimumDistinct": 3, "actualDistinct": resource_module_distinct})
    if validation_stage_distinct < 3:
        findings.append({"code": "weak-skill-validation-progression", "minimumDistinct": 3, "actualDistinct": validation_stage_distinct})
    if read_surface_distinct < 3:
        findings.append({"code": "weak-skill-read-surface-progression", "minimumDistinct": 3, "actualDistinct": read_surface_distinct})
    if cost_meter_distinct < 3:
        findings.append({"code": "weak-skill-cost-meter-progression", "minimumDistinct": 3, "actualDistinct": cost_meter_distinct})

    evidence = {
        "requested": True,
        "flags": flag_evidence,
        "skillFileLayerCountMax": skill_file_layer_max,
        "skillFileLayerCountDistinct": skill_file_layer_distinct,
        "skillFileLayerCountSequence": sample_sequence(samples, "skillFileLayerCount"),
        "triggerExampleCountMax": trigger_example_max,
        "triggerExampleCountDistinct": trigger_example_distinct,
        "triggerExampleCountSequence": sample_sequence(samples, "triggerExampleCount"),
        "resourceModuleCountMax": resource_module_max,
        "resourceModuleCountDistinct": resource_module_distinct,
        "resourceModuleCountSequence": sample_sequence(samples, "resourceModuleCount"),
        "validationStageLevelMax": validation_stage_max,
        "validationStageLevelDistinct": validation_stage_distinct,
        "validationStageLevelSequence": sample_sequence(samples, "validationStageLevel"),
        "readSurfaceLevelMax": read_surface_max,
        "readSurfaceLevelDistinct": read_surface_distinct,
        "readSurfaceLevelSequence": sample_sequence(samples, "readSurfaceLevel"),
        "costMeterLevelMax": cost_meter_max,
        "costMeterLevelDistinct": cost_meter_distinct,
        "costMeterLevelSequence": sample_sequence(samples, "costMeterLevel"),
    }
    return findings, evidence


def hook_motif_findings(
    summary: dict[str, Any],
    samples: list[dict[str, Any]],
    source_package: dict[str, Any],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    if not hook_motif_requested(source_package):
        return [], {}
    findings: list[dict[str, Any]] = []
    required_flags = [
        "eventTimelineVisible",
        "shieldGateOverlayVisible",
        "githubHookBadgesVisible",
        "claudeEventCloudVisible",
        "opencodeEventListVisible",
        "hookJobCascadeVisible",
        "commandBlockPathVisible",
        "logFilterPathVisible",
        "tokenSavingsCounterVisible",
        "costLatencyTradeoffVisible",
        "lifecycleRuleStampVisible",
    ]
    flag_evidence: dict[str, Any] = {}
    for key in required_flags:
        actual = max_value(summary, key)
        flag_evidence[key] = {
            "max": actual,
            "sequence": sample_sequence(samples, key),
        }
        if actual < 1:
            findings.append({"code": "missing-hook-motif-state", "stateKey": key})

    event_count_max = max_value(summary, "activeHookEventCount")
    provider_count_max = max_value(summary, "providerLaneCount")
    policy_token_max = max_value(summary, "policyTokenCount")
    token_savings_max = max_value(summary, "tokenSavingsLevel")
    latency_cost_max = max_value(summary, "latencyCostLevel")
    event_count_distinct = distinct_count(summary, "activeHookEventCount")
    policy_token_distinct = distinct_count(summary, "policyTokenCount")
    token_savings_distinct = distinct_count(summary, "tokenSavingsLevel")
    latency_cost_distinct = distinct_count(summary, "latencyCostLevel")

    if event_count_max < 8:
        findings.append({"code": "too-few-hook-lifecycle-events", "minimumMax": 8, "actualMax": event_count_max})
    if provider_count_max < 3:
        findings.append({"code": "too-few-hook-provider-lanes", "minimumMax": 3, "actualMax": provider_count_max})
    if policy_token_max < 5:
        findings.append({"code": "too-few-hook-policy-tokens", "minimumMax": 5, "actualMax": policy_token_max})
    if token_savings_max < 4:
        findings.append({"code": "weak-hook-token-savings-level", "minimumMax": 4, "actualMax": token_savings_max})
    if latency_cost_max < 3:
        findings.append({"code": "weak-hook-latency-cost-level", "minimumMax": 3, "actualMax": latency_cost_max})
    if event_count_distinct < 3:
        findings.append({"code": "weak-hook-event-progression", "minimumDistinct": 3, "actualDistinct": event_count_distinct})
    if policy_token_distinct < 3:
        findings.append({"code": "weak-hook-policy-token-progression", "minimumDistinct": 3, "actualDistinct": policy_token_distinct})
    if token_savings_distinct < 3:
        findings.append({"code": "weak-hook-token-savings-progression", "minimumDistinct": 3, "actualDistinct": token_savings_distinct})
    if latency_cost_distinct < 3:
        findings.append({"code": "weak-hook-latency-cost-progression", "minimumDistinct": 3, "actualDistinct": latency_cost_distinct})

    evidence = {
        "requested": True,
        "flags": flag_evidence,
        "activeHookEventCountMax": event_count_max,
        "activeHookEventCountDistinct": event_count_distinct,
        "activeHookEventCountSequence": sample_sequence(samples, "activeHookEventCount"),
        "providerLaneCountMax": provider_count_max,
        "providerLaneCountSequence": sample_sequence(samples, "providerLaneCount"),
        "policyTokenCountMax": policy_token_max,
        "policyTokenCountDistinct": policy_token_distinct,
        "policyTokenCountSequence": sample_sequence(samples, "policyTokenCount"),
        "tokenSavingsLevelMax": token_savings_max,
        "tokenSavingsLevelDistinct": token_savings_distinct,
        "tokenSavingsLevelSequence": sample_sequence(samples, "tokenSavingsLevel"),
        "latencyCostLevelMax": latency_cost_max,
        "latencyCostLevelDistinct": latency_cost_distinct,
        "latencyCostLevelSequence": sample_sequence(samples, "latencyCostLevel"),
    }
    return findings, evidence


def ai_alternatives_motif_findings(
    summary: dict[str, Any],
    samples: list[dict[str, Any]],
    source_package: dict[str, Any],
    rendered: dict[str, Any],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    if not ai_alternatives_motif_requested(source_package):
        return [], {}
    findings: list[dict[str, Any]] = []
    required_flags = [
        "comparisonGridVisible",
        "rovoWorkspaceVisible",
        "geminiWorkspaceVisible",
        "copilotWorkspaceVisible",
        "claudeWorkspaceVisible",
        "quadrantMapVisible",
        "workflowSelectorVisible",
        "selectedWorkflowPathVisible",
        "guardrailWrapVisible",
        "observabilityWrapVisible",
    ]
    flag_evidence: dict[str, Any] = {}
    for key in required_flags:
        actual = max_value(summary, key)
        flag_evidence[key] = {
            "max": actual,
            "sequence": sample_sequence(samples, key),
        }
        if actual < 1:
            findings.append({"code": "missing-ai-alternatives-motif-state", "stateKey": key})

    platform_home_max = max_value(summary, "platformHomeBaseCount")
    radar_axis_max = max_value(summary, "radarAxisCount")
    cost_meter_count_max = max_value(summary, "costMeterCount")
    cost_meter_level_max = max_value(summary, "costMeterLevel")
    platform_home_distinct = distinct_count(summary, "platformHomeBaseCount")
    radar_axis_distinct = distinct_count(summary, "radarAxisCount")
    cost_meter_count_distinct = distinct_count(summary, "costMeterCount")
    cost_meter_level_distinct = distinct_count(summary, "costMeterLevel")
    max_red_rect_area_ratio = numeric_contract_value(rendered.get("maxRedRectAreaRatio"), 0.0)
    median_red_rect_area_ratio = numeric_contract_value(rendered.get("medianRedRectAreaRatio"), 0.0)

    if platform_home_max < 4:
        findings.append({"code": "too-few-ai-platform-home-bases", "minimumMax": 4, "actualMax": platform_home_max})
    if radar_axis_max < 5:
        findings.append({"code": "too-few-ai-fit-radar-axes", "minimumMax": 5, "actualMax": radar_axis_max})
    if cost_meter_count_max < 4:
        findings.append({"code": "too-few-ai-cost-meters", "minimumMax": 4, "actualMax": cost_meter_count_max})
    if cost_meter_level_max < 4:
        findings.append({"code": "weak-ai-cost-meter-level", "minimumMax": 4, "actualMax": cost_meter_level_max})
    if platform_home_distinct < 3:
        findings.append({"code": "weak-ai-home-base-progression", "minimumDistinct": 3, "actualDistinct": platform_home_distinct})
    if radar_axis_distinct < 3:
        findings.append({"code": "weak-ai-radar-axis-progression", "minimumDistinct": 3, "actualDistinct": radar_axis_distinct})
    if cost_meter_count_distinct < 3:
        findings.append({"code": "weak-ai-cost-meter-count-progression", "minimumDistinct": 3, "actualDistinct": cost_meter_count_distinct})
    if cost_meter_level_distinct < 3:
        findings.append({"code": "weak-ai-cost-meter-level-progression", "minimumDistinct": 3, "actualDistinct": cost_meter_level_distinct})
    if max_red_rect_area_ratio > 0.10:
        findings.append(
            {
                "code": "ai-alternatives-red-area-too-dominant",
                "maximum": 0.10,
                "actual": max_red_rect_area_ratio,
            }
        )

    evidence = {
        "requested": True,
        "flags": flag_evidence,
        "platformHomeBaseCountMax": platform_home_max,
        "platformHomeBaseCountDistinct": platform_home_distinct,
        "platformHomeBaseCountSequence": sample_sequence(samples, "platformHomeBaseCount"),
        "radarAxisCountMax": radar_axis_max,
        "radarAxisCountDistinct": radar_axis_distinct,
        "radarAxisCountSequence": sample_sequence(samples, "radarAxisCount"),
        "costMeterCountMax": cost_meter_count_max,
        "costMeterCountDistinct": cost_meter_count_distinct,
        "costMeterCountSequence": sample_sequence(samples, "costMeterCount"),
        "costMeterLevelMax": cost_meter_level_max,
        "costMeterLevelDistinct": cost_meter_level_distinct,
        "costMeterLevelSequence": sample_sequence(samples, "costMeterLevel"),
        "maxRedRectAreaRatio": max_red_rect_area_ratio,
        "medianRedRectAreaRatio": median_red_rect_area_ratio,
    }
    return findings, evidence


def plugin_motif_findings(
    summary: dict[str, Any],
    samples: list[dict[str, Any]],
    source_package: dict[str, Any],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    if not plugin_motif_requested(source_package):
        return [], {}
    findings: list[dict[str, Any]] = []
    required_flags = [
        "pluginBundleCubeVisible",
        "bundleOpenedVisible",
        "githubManifestCardVisible",
        "claudeMarketplaceGateVisible",
        "opencodeNpmRuntimeDropVisible",
        "teamInstallFanoutVisible",
        "versionUpgradeVisible",
        "governanceGateVisible",
        "goodBadPluginSplitVisible",
        "noisyPluginRiskVisible",
        "packageInstallVisible",
        "packagedBehaviorStampVisible",
    ]
    flag_evidence: dict[str, Any] = {}
    for key in required_flags:
        actual = max_value(summary, key)
        flag_evidence[key] = {
            "max": actual,
            "sequence": sample_sequence(samples, key),
        }
        if actual < 1:
            findings.append({"code": "missing-plugin-motif-state", "stateKey": key})

    bundle_block_max = max_value(summary, "bundleBlockCount")
    bundle_module_max = max_value(summary, "bundleModuleCount")
    provider_surface_max = max_value(summary, "providerSurfaceCount")
    install_fanout_max = max_value(summary, "installFanoutCount")
    version_level_max = max_value(summary, "versionLevel")
    noisy_tool_max = max_value(summary, "noisyToolCount")
    cost_meter_max = max_value(summary, "costMeterLevel")
    bundle_block_distinct = distinct_count(summary, "bundleBlockCount")
    bundle_module_distinct = distinct_count(summary, "bundleModuleCount")
    install_fanout_distinct = distinct_count(summary, "installFanoutCount")
    version_level_distinct = distinct_count(summary, "versionLevel")
    noisy_tool_distinct = distinct_count(summary, "noisyToolCount")
    cost_meter_distinct = distinct_count(summary, "costMeterLevel")

    if bundle_block_max < 8:
        findings.append({"code": "too-few-plugin-bundle-blocks", "minimumMax": 8, "actualMax": bundle_block_max})
    if bundle_module_max < 4:
        findings.append({"code": "too-few-plugin-detachable-modules", "minimumMax": 4, "actualMax": bundle_module_max})
    if provider_surface_max < 3:
        findings.append({"code": "too-few-plugin-provider-surfaces", "minimumMax": 3, "actualMax": provider_surface_max})
    if install_fanout_max < 5:
        findings.append({"code": "too-few-plugin-team-installs", "minimumMax": 5, "actualMax": install_fanout_max})
    if version_level_max < 4:
        findings.append({"code": "weak-plugin-version-upgrade-level", "minimumMax": 4, "actualMax": version_level_max})
    if noisy_tool_max < 5:
        findings.append({"code": "weak-plugin-noisy-tool-spread", "minimumMax": 5, "actualMax": noisy_tool_max})
    if cost_meter_max < 4:
        findings.append({"code": "weak-plugin-cost-risk-meter", "minimumMax": 4, "actualMax": cost_meter_max})
    if bundle_block_distinct < 3:
        findings.append({"code": "weak-plugin-bundle-assembly-progression", "minimumDistinct": 3, "actualDistinct": bundle_block_distinct})
    if bundle_module_distinct < 3:
        findings.append({"code": "weak-plugin-module-reveal-progression", "minimumDistinct": 3, "actualDistinct": bundle_module_distinct})
    if install_fanout_distinct < 3:
        findings.append({"code": "weak-plugin-install-fanout-progression", "minimumDistinct": 3, "actualDistinct": install_fanout_distinct})
    if version_level_distinct < 3:
        findings.append({"code": "weak-plugin-version-progression", "minimumDistinct": 3, "actualDistinct": version_level_distinct})
    if noisy_tool_distinct < 3:
        findings.append({"code": "weak-plugin-noisy-risk-progression", "minimumDistinct": 3, "actualDistinct": noisy_tool_distinct})
    if cost_meter_distinct < 3:
        findings.append({"code": "weak-plugin-cost-meter-progression", "minimumDistinct": 3, "actualDistinct": cost_meter_distinct})

    evidence = {
        "requested": True,
        "flags": flag_evidence,
        "bundleBlockCountMax": bundle_block_max,
        "bundleBlockCountDistinct": bundle_block_distinct,
        "bundleBlockCountSequence": sample_sequence(samples, "bundleBlockCount"),
        "bundleModuleCountMax": bundle_module_max,
        "bundleModuleCountDistinct": bundle_module_distinct,
        "bundleModuleCountSequence": sample_sequence(samples, "bundleModuleCount"),
        "providerSurfaceCountMax": provider_surface_max,
        "providerSurfaceCountSequence": sample_sequence(samples, "providerSurfaceCount"),
        "installFanoutCountMax": install_fanout_max,
        "installFanoutCountDistinct": install_fanout_distinct,
        "installFanoutCountSequence": sample_sequence(samples, "installFanoutCount"),
        "versionLevelMax": version_level_max,
        "versionLevelDistinct": version_level_distinct,
        "versionLevelSequence": sample_sequence(samples, "versionLevel"),
        "noisyToolCountMax": noisy_tool_max,
        "noisyToolCountDistinct": noisy_tool_distinct,
        "noisyToolCountSequence": sample_sequence(samples, "noisyToolCount"),
        "costMeterLevelMax": cost_meter_max,
        "costMeterLevelDistinct": cost_meter_distinct,
        "costMeterLevelSequence": sample_sequence(samples, "costMeterLevel"),
    }
    return findings, evidence


def harness_motif_findings(
    summary: dict[str, Any],
    samples: list[dict[str, Any]],
    source_package: dict[str, Any],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    if not harness_motif_requested(source_package):
        return [], {}
    findings: list[dict[str, Any]] = []
    required_flags = [
        "comparisonGridVisible",
        "runtimeStackVisible",
        "engineCoreVisible",
        "dashboardControlsVisible",
        "modelBadgeShared",
        "shellCopilotVisible",
        "shellClaudeCodeVisible",
        "shellOpenCodeVisible",
        "threeHarnessShellsVisible",
        "creditMeterRising",
        "featureGridMuted",
        "useCaseMatrixActive",
        "selectionPathHighlighted",
        "agentLoopRingVisible",
    ]
    flag_evidence: dict[str, Any] = {}
    for key in required_flags:
        actual = max_value(summary, key)
        flag_evidence[key] = {
            "max": actual,
            "sequence": sample_sequence(samples, key),
        }
        if actual < 1:
            findings.append({"code": "missing-harness-motif-state", "stateKey": key})

    layers_max = max_value(summary, "layersAssembling")
    shell_count_max = max_value(summary, "sameModelShellCount")
    tool_count_max = max_value(summary, "toolCountLevel")
    credit_level_max = max_value(summary, "creditMeterLevel")
    credit_level_distinct = distinct_count(summary, "creditMeterLevel")
    tool_count_distinct = distinct_count(summary, "toolCountLevel")
    if layers_max < 6:
        findings.append({"code": "too-few-harness-runtime-layers", "minimumMax": 6, "actualMax": layers_max})
    if shell_count_max < 3:
        findings.append({"code": "too-few-harness-shells", "minimumMax": 3, "actualMax": shell_count_max})
    if tool_count_max < 4:
        findings.append({"code": "too-few-harness-tool-count-levels", "minimumMax": 4, "actualMax": tool_count_max})
    if credit_level_max < 3:
        findings.append({"code": "weak-harness-credit-meter-level", "minimumMax": 3, "actualMax": credit_level_max})
    if credit_level_distinct < 3:
        findings.append({"code": "weak-harness-credit-meter-progression", "minimumDistinct": 3, "actualDistinct": credit_level_distinct})
    if tool_count_distinct < 3:
        findings.append({"code": "weak-harness-tool-count-progression", "minimumDistinct": 3, "actualDistinct": tool_count_distinct})

    evidence = {
        "requested": True,
        "flags": flag_evidence,
        "layersAssemblingMax": layers_max,
        "layersAssemblingSequence": sample_sequence(samples, "layersAssembling"),
        "sameModelShellCountMax": shell_count_max,
        "sameModelShellCountSequence": sample_sequence(samples, "sameModelShellCount"),
        "toolCountLevelMax": tool_count_max,
        "toolCountLevelDistinct": tool_count_distinct,
        "toolCountLevelSequence": sample_sequence(samples, "toolCountLevel"),
        "creditMeterLevelMax": credit_level_max,
        "creditMeterLevelDistinct": credit_level_distinct,
        "creditMeterLevelSequence": sample_sequence(samples, "creditMeterLevel"),
    }
    return findings, evidence


def guardrail_motif_findings(
    summary: dict[str, Any],
    samples: list[dict[str, Any]],
    source_package: dict[str, Any],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    if not guardrail_motif_requested(source_package):
        return [], {}
    findings: list[dict[str, Any]] = []
    required_flags = [
        "guardrailShieldGateVisible",
        "inputGateVisible",
        "outputGateVisible",
        "actionGateVisible",
        "promptInspectionActive",
        "outputInspectionActive",
        "toolCallInspectionActive",
        "riskScoreVisible",
        "policyMatrixVisible",
        "blockStateActive",
        "redactStateActive",
        "routeStateActive",
        "escalateStateActive",
        "humanApprovalRequired",
        "positiveCasePasses",
        "blockedCaseStops",
        "safetyFrictionBalanceVisible",
    ]
    flag_evidence: dict[str, Any] = {}
    for key in required_flags:
        actual = max_value(summary, key)
        flag_evidence[key] = {
            "max": actual,
            "sequence": sample_sequence(samples, key),
        }
        if actual < 1:
            findings.append({"code": "missing-guardrail-motif-state", "stateKey": key})

    risk_level_max = max_value(summary, "riskScoreLevel")
    risk_level_distinct = distinct_count(summary, "riskScoreLevel")
    if risk_level_max < 3:
        findings.append(
            {
                "code": "weak-guardrail-risk-score-level",
                "minimumMax": 3,
                "actualMax": risk_level_max,
            }
        )
    if risk_level_distinct < 3:
        findings.append(
            {
                "code": "weak-guardrail-risk-score-progression",
                "minimumDistinct": 3,
                "actualDistinct": risk_level_distinct,
            }
        )

    protected_flags = ["secretRiskActive", "destructiveCommandRiskActive", "deployRiskActive"]
    protected_evidence = {key: {"max": max_value(summary, key), "sequence": sample_sequence(samples, key)} for key in protected_flags}
    if sum(1 for key in protected_flags if max_value(summary, key) >= 1) < 3:
        findings.append({"code": "too-few-guardrail-protected-action-states", "required": protected_flags, "evidence": protected_evidence})

    evidence = {
        "requested": True,
        "flags": flag_evidence,
        "riskScoreLevelMax": risk_level_max,
        "riskScoreLevelDistinct": risk_level_distinct,
        "riskScoreLevelSequence": sample_sequence(samples, "riskScoreLevel"),
        "protectedActionFlags": protected_evidence,
    }
    return findings, evidence


def build_findings(
    args: argparse.Namespace,
    wrapper: dict[str, Any],
    state: dict[str, Any],
    contact: dict[str, Any],
    metro: dict[str, Any],
    source_package: dict[str, Any],
    rendered: dict[str, Any],
    mute: dict[str, Any],
    video_composition: dict[str, Any],
    pattern_mix: dict[str, Any],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    findings = append_pass_findings(wrapper, state, contact, metro)
    summary = state_summary(wrapper, state)
    samples = state_samples(wrapper, state)
    contact = contact_report(wrapper, contact)
    metrics = contact_metrics(contact)
    dynamic_keys = dynamic_state_keys(summary)
    camera = camera_evidence(summary)
    mechanism_entry = summary_entry(summary, "visibleMechanismCount")
    zone_entry = summary_entry(summary, "visibleZoneCount")

    if args.require_metro_pattern_mix:
        if not wrapper:
            findings.append({"code": "missing-wrapper-evidence-for-mix"})
        if not summary:
            findings.append({"code": "missing-state-evidence-for-mix"})
        if not contact:
            findings.append({"code": "missing-contact-evidence-for-mix"})
        if contact and not metrics:
            findings.append({"code": "missing-contact-metrics-for-mix"})
        if not metro:
            findings.append({"code": "missing-metro-audit-suite-evidence-for-mix"})
        if not source_package:
            findings.append({"code": "missing-source-package-evidence-for-mix"})
        if not rendered:
            findings.append({"code": "missing-rendered-frame-evidence-for-mix"})
        if not mute:
            findings.append({"code": "missing-mute-test-evidence-for-mix"})
        if not video_composition:
            findings.append({"code": "missing-mp4-composition-evidence-for-mix"})

    mechanism_distinct = int(numeric_value(mechanism_entry, "distinctCount"))
    mechanism_max = numeric_value(mechanism_entry, "max")
    visible_zone_max = numeric_value(zone_entry, "max")
    active_zone_distinct = distinct_count(summary, "activeZoneId")
    if mechanism_distinct < args.min_mechanism_distinct:
        findings.append(
            {
                "code": "weak-mechanism-progression",
                "minimumDistinct": args.min_mechanism_distinct,
                "actualDistinct": mechanism_distinct,
            }
        )
    if mechanism_max < args.min_mechanism_max:
        findings.append(
            {
                "code": "too-few-visible-mechanisms",
                "minimumMax": args.min_mechanism_max,
                "actualMax": mechanism_max,
            }
        )

    if visible_zone_max < args.min_state_visible_zones:
        findings.append(
            {
                "code": "too-few-render-state-visible-zones",
                "minimumMax": args.min_state_visible_zones,
                "actualMax": visible_zone_max,
            }
        )
    if active_zone_distinct < args.min_active_zone_distinct:
        findings.append(
            {
                "code": "weak-active-zone-progression",
                "minimumDistinct": args.min_active_zone_distinct,
                "actualDistinct": active_zone_distinct,
            }
        )

    if len(dynamic_keys) < args.min_dynamic_state_keys:
        findings.append(
            {
                "code": "too-few-dynamic-state-keys",
                "minimum": args.min_dynamic_state_keys,
                "actual": len(dynamic_keys),
                "dynamicStateKeys": dynamic_keys,
            }
        )

    if args.require_camera_motion:
        has_camera_motion = (
            camera["cameraMovingDistinct"] >= 2
            and camera["cameraMovingMax"] >= 1
        ) or camera["cameraXDistinct"] >= args.min_camera_distinct or camera["cameraYDistinct"] >= args.min_camera_distinct
        if not has_camera_motion:
            findings.append(
                {
                    "code": "missing-camera-motion",
                    "minimumCameraDistinct": args.min_camera_distinct,
                    "camera": camera,
                }
            )
        if camera["cameraScaleDistinct"] < args.min_camera_scale_distinct:
            findings.append(
                {
                    "code": "missing-camera-scale-reframe",
                    "minimumCameraScaleDistinct": args.min_camera_scale_distinct,
                    "camera": camera,
                }
            )
        if max(camera["cameraXRange"], camera["cameraYRange"]) < args.min_camera_travel_px:
            findings.append(
                {
                    "code": "weak-camera-travel",
                    "minimumRangePx": args.min_camera_travel_px,
                    "camera": camera,
                }
            )
        if camera["cameraScaleMax"] < args.min_camera_scale_max:
            findings.append(
                {
                    "code": "weak-camera-zoom-depth",
                    "minimumScaleMax": args.min_camera_scale_max,
                    "camera": camera,
                }
            )

    if int(contact.get("samples", 0) or 0) < args.min_contact_samples:
        findings.append({"code": "too-few-contact-samples", "minimum": args.min_contact_samples, "actual": contact.get("samples")})
    if int(metrics.get("changingPairs", 0) or 0) < args.min_changing_pairs:
        findings.append({"code": "too-few-changing-frame-pairs", "minimum": args.min_changing_pairs, "actual": metrics.get("changingPairs")})
    if int(metrics.get("lowChangePairs", 0) or 0) > args.max_low_change_pairs:
        findings.append({"code": "too-many-low-change-frame-pairs", "maximum": args.max_low_change_pairs, "actual": metrics.get("lowChangePairs")})
    if float(metrics.get("minTileColorBuckets", 0.0) or 0.0) < args.min_tile_color_buckets:
        findings.append({"code": "weak-contact-color-diversity", "minimum": args.min_tile_color_buckets, "actual": metrics.get("minTileColorBuckets")})
    if float(metrics.get("medianTileNonbackgroundRatio", 0.0) or 0.0) < args.min_median_nonbackground_ratio:
        findings.append(
            {
                "code": "weak-contact-nonbackground-area",
                "minimum": args.min_median_nonbackground_ratio,
                "actual": metrics.get("medianTileNonbackgroundRatio"),
            }
        )

    opening = contact.get("openingTileAssessment")
    if isinstance(opening, dict) and opening.get("weak") is True:
        findings.append({"code": "weak-opening-tile", "openingTileAssessment": opening})

    evidence = {
        "visibleMechanismCount": {
            "distinctCount": mechanism_distinct,
            "max": mechanism_max,
        },
        "renderState": {
            "visibleZoneCountMax": visible_zone_max,
            "activeZoneDistinct": active_zone_distinct,
        },
        "dynamicStateKeys": dynamic_keys,
        "camera": camera,
        "contactSheet": {
            "samples": contact.get("samples"),
            "changingPairs": metrics.get("changingPairs"),
            "lowChangePairs": metrics.get("lowChangePairs"),
            "minTileColorBuckets": metrics.get("minTileColorBuckets"),
            "medianTileNonbackgroundRatio": metrics.get("medianTileNonbackgroundRatio"),
            "openingTileWeak": opening.get("weak") if isinstance(opening, dict) else None,
        },
    }
    pattern_mix_specific_findings, pattern_mix_evidence = pattern_mix_findings(pattern_mix, wrapper, source_package, args)
    masonry_required = False
    masonry_contract_evidence = pattern_mix_evidence.get("masonryContract") if isinstance(pattern_mix_evidence, dict) else None
    if isinstance(masonry_contract_evidence, dict):
        masonry_required = masonry_contract_evidence.get("required") is True
    source_findings, source_evidence = source_package_findings(source_package, args)
    rendered_findings, rendered_evidence = rendered_frame_findings(rendered, args, masonry_required=masonry_required)
    mute_findings, mute_evidence = mute_test_findings(mute, args)
    video_composition_specific_findings, video_composition_evidence = video_composition_findings(video_composition, args)
    continuity_specific_findings, continuity_evidence = continuity_findings(samples, pattern_mix, args)
    semantic_binding_specific_findings, semantic_binding_evidence = semantic_binding_findings(source_package, rendered, samples, args)
    agent_loop_specific_findings, agent_loop_evidence = agent_loop_motif_findings(summary, samples, source_package)
    skill_specific_findings, skill_evidence = skill_motif_findings(summary, samples, source_package)
    hook_specific_findings, hook_evidence = hook_motif_findings(summary, samples, source_package)
    ai_alternatives_specific_findings, ai_alternatives_evidence = ai_alternatives_motif_findings(summary, samples, source_package, rendered)
    plugin_specific_findings, plugin_evidence = plugin_motif_findings(summary, samples, source_package)
    harness_specific_findings, harness_evidence = harness_motif_findings(summary, samples, source_package)
    guardrail_specific_findings, guardrail_evidence = guardrail_motif_findings(summary, samples, source_package)
    findings.extend(source_findings)
    findings.extend(rendered_findings)
    findings.extend(mute_findings)
    findings.extend(video_composition_specific_findings)
    findings.extend(continuity_specific_findings)
    findings.extend(semantic_binding_specific_findings)
    findings.extend(agent_loop_specific_findings)
    findings.extend(skill_specific_findings)
    findings.extend(hook_specific_findings)
    findings.extend(ai_alternatives_specific_findings)
    findings.extend(plugin_specific_findings)
    findings.extend(harness_specific_findings)
    findings.extend(guardrail_specific_findings)
    findings.extend(pattern_mix_specific_findings)
    if source_evidence:
        evidence["sourcePackage"] = source_evidence
    if rendered_evidence:
        evidence["renderedFrameAudit"] = rendered_evidence
    if mute_evidence:
        evidence["muteTestAudit"] = mute_evidence
    if video_composition_evidence:
        evidence["mp4CompositionAudit"] = video_composition_evidence
    if continuity_evidence:
        evidence["continuityPath"] = continuity_evidence
    if semantic_binding_evidence:
        evidence["semanticBindings"] = semantic_binding_evidence
    if agent_loop_evidence:
        evidence["agentLoopMotif"] = agent_loop_evidence
    if skill_evidence:
        evidence["skillMotif"] = skill_evidence
    if hook_evidence:
        evidence["hookMotif"] = hook_evidence
    if ai_alternatives_evidence:
        evidence["aiAlternativesMotif"] = ai_alternatives_evidence
    if plugin_evidence:
        evidence["pluginMotif"] = plugin_evidence
    if harness_evidence:
        evidence["harnessMotif"] = harness_evidence
    if guardrail_evidence:
        evidence["guardrailMotif"] = guardrail_evidence
    if pattern_mix_evidence:
        evidence["metroPatternMix"] = pattern_mix_evidence
    return findings, evidence


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit Metro video reports for semantic density, camera movement, and real frame variation.")
    parser.add_argument("--wrapper-report", type=Path, help="Path to prompt-contract-build.json.")
    parser.add_argument("--state-manifest", type=Path, help="Path to render-state-check.json.")
    parser.add_argument("--contact-sheet-manifest", type=Path, help="Path to contact-sheet manifest JSON.")
    parser.add_argument("--metro-audit-suite", type=Path, help="Path to metro-audit-suite.json.")
    parser.add_argument("--metro-pattern-mix", type=Path, help="Path to metro-pattern-mix.json. Uses wrapper.metroPatternMix when omitted.")
    parser.add_argument("--source-package", type=Path, help="Path to source-package.json. Derived from wrapper when omitted.")
    parser.add_argument("--metro-rendered-frame-audit", type=Path, help="Path to metro-rendered-frame-audit.json. Derived from wrapper/suite when omitted.")
    parser.add_argument("--metro-mute-test-audit", type=Path, help="Path to metro-mute-test-audit.json. Derived from wrapper/suite when omitted.")
    parser.add_argument("--metro-video-composition-audit", type=Path, help="Path to metro-video-composition-audit.json. Derived from wrapper when omitted.")
    parser.add_argument("--output", "--report", dest="output", required=True, type=Path)
    parser.add_argument("--min-mechanism-distinct", type=int, default=5)
    parser.add_argument("--min-mechanism-max", type=float, default=5)
    parser.add_argument("--min-dynamic-state-keys", type=int, default=4)
    parser.add_argument("--require-camera-motion", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--min-camera-distinct", type=int, default=3)
    parser.add_argument("--min-camera-scale-distinct", type=int, default=2)
    parser.add_argument("--min-camera-travel-px", type=float, default=96.0)
    parser.add_argument("--min-camera-scale-max", type=float, default=1.3)
    parser.add_argument("--min-contact-samples", type=int, default=6)
    parser.add_argument("--min-changing-pairs", type=int, default=4)
    parser.add_argument("--max-low-change-pairs", type=int, default=1)
    parser.add_argument("--min-tile-color-buckets", type=int, default=24)
    parser.add_argument("--min-median-nonbackground-ratio", type=float, default=0.08)
    parser.add_argument("--min-source-visual-mechanisms", type=int, default=3)
    parser.add_argument("--min-source-anchors", type=int, default=4)
    parser.add_argument("--min-source-visual-zones", type=int, default=5)
    parser.add_argument("--min-source-gray-levels", type=int, default=4)
    parser.add_argument("--require-source-anchor-map", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--min-source-zone-anchor-coverage-ratio", type=float, default=1.0)
    parser.add_argument("--min-source-binding-anchor-coverage-ratio", type=float, default=1.0)
    parser.add_argument("--min-source-anchored-zone-ratio", type=float, default=1.0)
    parser.add_argument("--min-rendered-source-anchor-coverage-ratio", type=float, default=1.0)
    parser.add_argument("--min-state-source-anchor-coverage-ratio", type=float, default=1.0)
    parser.add_argument("--min-source-anchor-visual-binding-coverage-ratio", type=float, default=1.0)
    parser.add_argument("--min-state-visible-zones", type=int, default=5)
    parser.add_argument("--min-active-zone-distinct", type=int, default=3)
    parser.add_argument("--min-rendered-rect-edges", type=int, default=96)
    parser.add_argument("--min-rendered-shared-edge-ratio", type=float, default=0.5)
    parser.add_argument("--max-rendered-offgrid-ratio", type=float, default=0.02)
    parser.add_argument("--min-rendered-median-gray-levels", type=int, default=4)
    parser.add_argument("--min-rendered-final-gray-levels", type=int, default=4)
    parser.add_argument("--min-rendered-gray-sample-pass-ratio", type=float, default=0.5)
    parser.add_argument("--max-rendered-internal-padding-px", type=float, default=0.5)
    parser.add_argument("--min-rendered-sample-rects", type=int, default=12)
    parser.add_argument("--min-rendered-sample-lines", type=int, default=4)
    parser.add_argument("--min-rendered-zone-elements", type=int, default=5)
    parser.add_argument("--max-rendered-median-text-area-ratio", type=float, default=0.14)
    parser.add_argument("--max-rendered-largest-text-box-area-ratio", type=float, default=0.08)
    parser.add_argument("--min-rendered-median-mark-to-text-ratio", type=float, default=1.5)
    parser.add_argument("--max-rendered-title-band-text-count", type=int, default=0)
    parser.add_argument("--max-rendered-ellipsized-text-count", type=int, default=0)
    parser.add_argument("--min-mute-hidden-changing-pairs", type=int, default=3)
    parser.add_argument("--min-mute-median-hidden-change-ratio", type=float, default=0.0012)
    parser.add_argument("--min-mute-hidden-to-full-change-ratio", type=float, default=0.35)
    parser.add_argument("--min-mute-hidden-nonbackground-ratio", type=float, default=0.08)
    parser.add_argument("--min-mute-hidden-mark-count", type=int, default=24)
    parser.add_argument("--min-mute-hidden-zone-elements", type=int, default=5)
    parser.add_argument("--min-mute-hidden-gray-levels", type=int, default=4)
    parser.add_argument("--min-mp4-grid-coverage", type=float, default=0.62)
    parser.add_argument("--min-mp4-median-grid-coverage", type=float, default=0.72)
    parser.add_argument("--min-mp4-quadrants-with-content", type=int, default=4)
    parser.add_argument("--min-mp4-opening-grid-coverage-ratio", type=float, default=0.65)
    parser.add_argument("--min-mp4-spatial-change-pairs", type=int, default=3)
    parser.add_argument("--max-mp4-text-like-component-area-ratio", type=float, default=0.12)
    parser.add_argument("--max-mp4-red-area-ratio", type=float, default=0.14)
    parser.add_argument("--require-metro-pattern-mix", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--min-mix-patterns", type=int, default=6)
    parser.add_argument("--min-mix-used-patterns", type=int, default=3)
    parser.add_argument("--min-mix-functional-zones", type=int, default=5)
    parser.add_argument("--min-mix-motion-systems", type=int, default=4)
    parser.add_argument("--min-mix-camera-events", type=int, default=3)
    parser.add_argument("--min-mix-transitions", type=int, default=3)
    parser.add_argument("--min-mix-transition-types", type=int, default=2)
    parser.add_argument("--require-modular-transition", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--min-continuity-samples", type=int, default=6)
    parser.add_argument("--min-continuity-zone-changes", type=int, default=3)
    parser.add_argument("--min-continuity-camera-coupled-changes", type=int, default=3)
    parser.add_argument("--min-continuity-camera-delta-px", type=float, default=2.0)
    parser.add_argument("--min-continuity-camera-scale-delta", type=float, default=0.01)
    parser.add_argument(
        "--require-mix-anti-pattern-risk",
        action="append",
        default=["boxes-plus-labels", "title-led-slide", "padded-rounded-cards", "weak-gray-hierarchy", "generic-transition"],
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    wrapper, wrapper_findings = read_json(args.wrapper_report, "wrapper-report")
    state, state_findings = read_json(args.state_manifest, "state-manifest")
    contact, contact_findings = read_json(args.contact_sheet_manifest, "contact-sheet-manifest")
    metro, metro_findings = read_json(args.metro_audit_suite, "metro-audit-suite")
    source_path = args.source_package or derive_source_package_path(wrapper)
    rendered_path = args.metro_rendered_frame_audit or derive_rendered_frame_audit_path(wrapper, metro)
    mute_path = args.metro_mute_test_audit or derive_mute_test_audit_path(wrapper, metro)
    video_composition_path = args.metro_video_composition_audit or derive_video_composition_audit_path(
        wrapper,
        metro,
        args.metro_audit_suite,
    )
    source_package, source_package_read_findings = read_json(source_path, "source-package")
    rendered, rendered_read_findings = read_json(rendered_path, "metro-rendered-frame-audit")
    mute, mute_read_findings = read_json(mute_path, "metro-mute-test-audit")
    video_composition, video_composition_read_findings = read_json(video_composition_path, "metro-video-composition-audit")
    if args.metro_pattern_mix:
        pattern_mix, pattern_mix_read_findings = read_json(args.metro_pattern_mix, "metro-pattern-mix")
    else:
        embedded_mix = wrapper.get("metroPatternMix")
        pattern_mix = embedded_mix if isinstance(embedded_mix, dict) else {}
        pattern_mix_read_findings = []

    findings = (
        wrapper_findings
        + state_findings
        + contact_findings
        + metro_findings
        + source_package_read_findings
        + rendered_read_findings
        + mute_read_findings
        + video_composition_read_findings
        + pattern_mix_read_findings
    )
    density_findings, evidence = build_findings(args, wrapper, state, contact, metro, source_package, rendered, mute, video_composition, pattern_mix)
    findings.extend(density_findings)

    report = {
        "passed": not findings,
        "inputs": {
            "wrapperReport": str(args.wrapper_report) if args.wrapper_report else None,
            "stateManifest": str(args.state_manifest) if args.state_manifest else None,
            "contactSheetManifest": str(args.contact_sheet_manifest) if args.contact_sheet_manifest else None,
            "metroAuditSuite": str(args.metro_audit_suite) if args.metro_audit_suite else None,
            "metroPatternMix": str(args.metro_pattern_mix) if args.metro_pattern_mix else "wrapper.metroPatternMix",
            "sourcePackage": str(source_path) if source_path else None,
            "metroRenderedFrameAudit": str(rendered_path) if rendered_path else None,
            "metroMuteTestAudit": str(mute_path) if mute_path else None,
            "metroVideoCompositionAudit": str(video_composition_path) if video_composition_path else None,
        },
        "thresholds": {
            "minMechanismDistinct": args.min_mechanism_distinct,
            "minMechanismMax": args.min_mechanism_max,
            "minDynamicStateKeys": args.min_dynamic_state_keys,
            "requireCameraMotion": args.require_camera_motion,
            "minCameraDistinct": args.min_camera_distinct,
            "minCameraTravelPx": args.min_camera_travel_px,
            "minCameraScaleMax": args.min_camera_scale_max,
            "minContactSamples": args.min_contact_samples,
            "minChangingPairs": args.min_changing_pairs,
            "maxLowChangePairs": args.max_low_change_pairs,
            "minTileColorBuckets": args.min_tile_color_buckets,
            "minMedianNonbackgroundRatio": args.min_median_nonbackground_ratio,
            "minSourceVisualMechanisms": args.min_source_visual_mechanisms,
            "minSourceAnchors": args.min_source_anchors,
            "minSourceVisualZones": args.min_source_visual_zones,
            "minSourceGrayLevels": args.min_source_gray_levels,
            "requireSourceAnchorMap": args.require_source_anchor_map,
            "minSourceZoneAnchorCoverageRatio": args.min_source_zone_anchor_coverage_ratio,
            "minSourceBindingAnchorCoverageRatio": args.min_source_binding_anchor_coverage_ratio,
            "minSourceAnchoredZoneRatio": args.min_source_anchored_zone_ratio,
            "minRenderedSourceAnchorCoverageRatio": args.min_rendered_source_anchor_coverage_ratio,
            "minStateSourceAnchorCoverageRatio": args.min_state_source_anchor_coverage_ratio,
            "minSourceAnchorVisualBindingCoverageRatio": args.min_source_anchor_visual_binding_coverage_ratio,
            "minStateVisibleZones": args.min_state_visible_zones,
            "minActiveZoneDistinct": args.min_active_zone_distinct,
            "minRenderedRectEdges": args.min_rendered_rect_edges,
            "minRenderedSharedEdgeRatio": args.min_rendered_shared_edge_ratio,
            "maxRenderedOffgridRatio": args.max_rendered_offgrid_ratio,
            "minRenderedMedianGrayLevels": args.min_rendered_median_gray_levels,
            "minRenderedFinalGrayLevels": args.min_rendered_final_gray_levels,
            "minRenderedGraySamplePassRatio": args.min_rendered_gray_sample_pass_ratio,
            "maxRenderedInternalPaddingPx": args.max_rendered_internal_padding_px,
            "minRenderedSampleRects": args.min_rendered_sample_rects,
            "minRenderedSampleLines": args.min_rendered_sample_lines,
            "minRenderedZoneElements": args.min_rendered_zone_elements,
            "maxRenderedMedianTextAreaRatio": args.max_rendered_median_text_area_ratio,
            "maxRenderedLargestTextBoxAreaRatio": args.max_rendered_largest_text_box_area_ratio,
            "minRenderedMedianMarkToTextRatio": args.min_rendered_median_mark_to_text_ratio,
            "maxRenderedTitleBandTextCount": args.max_rendered_title_band_text_count,
            "maxRenderedEllipsizedTextCount": args.max_rendered_ellipsized_text_count,
            "minMuteHiddenChangingPairs": args.min_mute_hidden_changing_pairs,
            "minMuteMedianHiddenChangeRatio": args.min_mute_median_hidden_change_ratio,
            "minMuteHiddenToFullChangeRatio": args.min_mute_hidden_to_full_change_ratio,
            "minMuteHiddenNonbackgroundRatio": args.min_mute_hidden_nonbackground_ratio,
            "minMuteHiddenMarkCount": args.min_mute_hidden_mark_count,
            "minMuteHiddenZoneElements": args.min_mute_hidden_zone_elements,
            "minMuteHiddenGrayLevels": args.min_mute_hidden_gray_levels,
            "minMp4GridCoverage": args.min_mp4_grid_coverage,
            "minMp4MedianGridCoverage": args.min_mp4_median_grid_coverage,
            "minMp4QuadrantsWithContent": args.min_mp4_quadrants_with_content,
            "minMp4OpeningGridCoverageRatio": args.min_mp4_opening_grid_coverage_ratio,
            "minMp4SpatialChangePairs": args.min_mp4_spatial_change_pairs,
            "maxMp4TextLikeComponentAreaRatio": args.max_mp4_text_like_component_area_ratio,
            "maxMp4RedAreaRatio": args.max_mp4_red_area_ratio,
            "requireMetroPatternMix": args.require_metro_pattern_mix,
            "minMixPatterns": args.min_mix_patterns,
            "minMixUsedPatterns": args.min_mix_used_patterns,
            "minMixFunctionalZones": args.min_mix_functional_zones,
            "minMixMotionSystems": args.min_mix_motion_systems,
            "minMixCameraEvents": args.min_mix_camera_events,
            "minMixTransitions": args.min_mix_transitions,
            "minMixTransitionTypes": args.min_mix_transition_types,
            "requireModularTransition": args.require_modular_transition,
            "minContinuitySamples": args.min_continuity_samples,
            "minContinuityZoneChanges": args.min_continuity_zone_changes,
            "minContinuityCameraCoupledChanges": args.min_continuity_camera_coupled_changes,
            "minContinuityCameraDeltaPx": args.min_continuity_camera_delta_px,
            "minContinuityCameraScaleDelta": args.min_continuity_camera_scale_delta,
            "requireMixAntiPatternRisk": args.require_mix_anti_pattern_risk,
        },
        "evidence": evidence,
        "findings": findings,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    if findings:
        print(f"Metro semantic density audit failed: {args.output}", file=sys.stderr)
        return 1
    print(f"Metro semantic density audit passed: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
