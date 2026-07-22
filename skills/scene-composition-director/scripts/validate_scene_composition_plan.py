#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Validate scene composition JSON plans."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


DEFAULT_FORBIDDEN = ["gsap", "ScrollTrigger", "TweenMax", "TimelineMax"]
REQUIRED_SCENE_FIELDS = [
    "id",
    "sceneJob",
    "viewerTask",
    "compositionChoice",
    "choiceRationale",
    "focal",
    "roles",
    "armature",
    "layout",
    "hierarchy",
    "safeZones",
    "depthLayers",
    "motionPhases",
    "validationChecks",
]
STRICT_ALIGNMENT_FIELDS = ["alignmentGrid", "armatureAnchors", "objectBounds"]
SQUARE_EDGE_FIELDS = ["edgePolicy", "cornerPolicy"]
VALIDATION_CONTRACT_FIELDS = ["validationContract"]
VALIDATION_CHECK_FIELDS = ["method", "target", "passCriterion"]
SQUARE_EDGE_MARKERS = ["square", "0-radius", "zero-radius", "hard edge", "hard-edge", "rectangular"]
ALIGNMENT_MARKERS = ["grid", "axis", "baseline", "row", "column", "modular", "orthogonal", "align"]
PADDING_KEYS = {"internalpaddingpx", "paddingpx", "boxpaddingpx", "padding"}
ROUNDING_PATTERNS = [
    r"\brounded\b",
    r"\bpill\b",
    r"\bblob\b",
    r"\bsoft[- ]edge\b",
    r"\bborder[- ]radius\b",
    r"\bcorner[- ]radius\b",
    r"\bradius\s+[1-9]\d*(?:\.\d+)?\b",
]
ZERO_PADDING_FIELDS = ["boxInteriorPolicy", "boxModel"]
GRAY_HIERARCHY_FIELDS = ["grayscaleHierarchy"]


def _flatten_text(value: Any) -> str:
    if isinstance(value, dict):
        return "\n".join(f"{k}: {_flatten_text(v)}" for k, v in value.items())
    if isinstance(value, list):
        return "\n".join(_flatten_text(item) for item in value)
    if value is None:
        return ""
    return str(value)


def _is_empty(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, str):
        return not value.strip()
    if isinstance(value, (list, dict)):
        return len(value) == 0
    return False


def _parse_hex_gray(value: Any) -> tuple[int, int, int] | None:
    if not isinstance(value, str):
        return None
    match = re.fullmatch(r"#([0-9a-fA-F]{6})", value.strip())
    if not match:
        return None
    raw = match.group(1)
    rgb = tuple(int(raw[idx : idx + 2], 16) for idx in (0, 2, 4))
    if rgb[0] != rgb[1] or rgb[1] != rgb[2]:
        return None
    return rgb


def _as_number(value: Any) -> float | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        match = re.fullmatch(r"\s*(-?\d+(?:\.\d+)?)\s*(?:px)?\s*", value)
        if match:
            return float(match.group(1))
    return None


def _find_positive_padding(value: Any, path: str = "root") -> list[str]:
    errors: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            child_path = f"{path}.{key}"
            key_text = str(key).lower()
            if key_text in PADDING_KEYS:
                numeric = _as_number(child)
                if numeric is not None and numeric > 0:
                    errors.append(f"{child_path} is positive ({child!r})")
            errors.extend(_find_positive_padding(child, child_path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            errors.extend(_find_positive_padding(child, f"{path}[{index}]"))
    elif isinstance(value, str):
        text = value.lower()
        if "padding" in text and re.search(r"\b[1-9]\d*(?:\.\d+)?\s*px\b", text):
            errors.append(f"{path} contains positive padding text ({value!r})")
    return errors


def _find_internal_padding(value: Any) -> Any:
    if isinstance(value, dict):
        for key, child in value.items():
            if str(key).lower() in PADDING_KEYS:
                return child
            found = _find_internal_padding(child)
            if found is not None:
                return found
    if isinstance(value, list):
        for child in value:
            found = _find_internal_padding(child)
            if found is not None:
                return found
    return None


def _has_zero_padding_policy(scene: dict[str, Any]) -> bool:
    box_model = scene.get("boxModel")
    if not isinstance(box_model, dict):
        return False
    return _as_number(box_model.get("internalPaddingPx")) == 0 and box_model.get("contentFlushToBounds") is True


def _has_forbidden_rounding(text: str) -> bool:
    lowered = text.lower()
    if "source-native only" in lowered:
        return False
    normalized = lowered.replace("0-radius", "").replace("zero-radius", "")
    return any(re.search(pattern, normalized) for pattern in ROUNDING_PATTERNS)


def _validate_strict_alignment(scene_id: str, scene: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    alignment_text = _flatten_text(scene.get("alignmentGrid")).lower()
    if not any(marker in alignment_text for marker in ALIGNMENT_MARKERS):
        errors.append(
            f"{scene_id}: alignmentGrid must mention a concrete grid, axis, baseline, row, column, modular, orthogonal, or alignment rule"
        )
    anchors = scene.get("armatureAnchors")
    if not isinstance(anchors, list) or len([item for item in anchors if not _is_empty(item)]) < 2:
        errors.append(f"{scene_id}: armatureAnchors must contain at least two anchors")
    bounds = scene.get("objectBounds")
    if not isinstance(bounds, list) or not bounds:
        errors.append(f"{scene_id}: objectBounds must be a non-empty list of structured objects")
        return errors
    for bound_index, bound in enumerate(bounds, start=1):
        if not isinstance(bound, dict):
            errors.append(f"{scene_id}: objectBounds item {bound_index} must be an object")
            continue
        if _is_empty(bound.get("id")):
            errors.append(f"{scene_id}: objectBounds item {bound_index} missing 'id'")
        has_numeric_bounds = all(_as_number(bound.get(field)) is not None for field in ("x", "y", "width", "height"))
        has_structured_location = any(not _is_empty(bound.get(field)) for field in ("zone", "anchor", "clearance"))
        if not (has_numeric_bounds or has_structured_location):
            errors.append(
                f"{scene_id}: objectBounds item {bound_index} needs x/y/width/height or zone/anchor/clearance fields"
            )
    return errors


def _validate_gray_hierarchy(scene_id: str, value: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(value, list) or len(value) < 3:
        return [f"{scene_id}: grayscaleHierarchy must contain at least 3 structured levels"]
    levels: list[tuple[int, int, str]] = []
    for index, item in enumerate(value, start=1):
        if not isinstance(item, dict):
            errors.append(f"{scene_id}: grayscaleHierarchy item {index} must be an object")
            continue
        if _is_empty(item.get("role")):
            errors.append(f"{scene_id}: grayscaleHierarchy item {index} missing 'role'")
        raw_level = item.get("level")
        if not isinstance(raw_level, int):
            errors.append(f"{scene_id}: grayscaleHierarchy item {index} missing integer 'level'")
            continue
        gray_value = item.get("grayHex") or item.get("hex")
        rgb = _parse_hex_gray(gray_value)
        if rgb is None:
            errors.append(
                f"{scene_id}: grayscaleHierarchy item {index} must use a #RRGGBB grayHex where R=G=B"
            )
            continue
        levels.append((raw_level, rgb[0], str(gray_value).lower()))
    if len({level for level, _, _ in levels}) != len(levels):
        errors.append(f"{scene_id}: grayscaleHierarchy levels must be distinct")
    if len({hex_value for _, _, hex_value in levels}) != len(levels):
        errors.append(f"{scene_id}: grayscaleHierarchy grayHex values must be distinct")
    ordered = sorted(levels)
    if len(ordered) >= 2:
        values = [gray for _, gray, _ in ordered]
        increasing = all(a < b for a, b in zip(values, values[1:]))
        decreasing = all(a > b for a, b in zip(values, values[1:]))
        if not (increasing or decreasing):
            errors.append(f"{scene_id}: grayscaleHierarchy gray values must be monotonic by level")
    return errors


def load_plan(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"{path} is not valid JSON: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError("Plan root must be a JSON object")
    return data


def validate_plan(
    plan: dict[str, Any],
    *,
    expect_scenes: int | None,
    min_scenes: int | None,
    require_anchors: list[str],
    forbidden: list[str],
    allow_held_scenes: bool,
    require_strict_alignment: bool,
    require_square_edges: bool,
    require_validation_contract: bool,
    require_zero_box_padding: bool,
    require_grayscale_hierarchy: bool,
) -> list[str]:
    errors: list[str] = []
    text = _flatten_text(plan)

    scenes = plan.get("scenes")
    if not isinstance(scenes, list) or not scenes:
        errors.append("Plan must contain a non-empty 'scenes' list")
        scenes = []

    if expect_scenes is not None and len(scenes) != expect_scenes:
        errors.append(f"Expected {expect_scenes} scenes, found {len(scenes)}")
    if min_scenes is not None and len(scenes) < min_scenes:
        errors.append(f"Expected at least {min_scenes} scenes, found {len(scenes)}")

    for anchor in require_anchors:
        if anchor not in text:
            errors.append(f"Missing required anchor: {anchor}")

    for term in forbidden:
        pattern = re.compile(re.escape(term), re.IGNORECASE)
        if pattern.search(text):
            errors.append(f"Forbidden term appears in plan: {term}")

    seen_ids: set[str] = set()
    for index, scene in enumerate(scenes, start=1):
        if not isinstance(scene, dict):
            errors.append(f"Scene {index} must be an object")
            continue

        scene_id = str(scene.get("id") or f"scene-{index}")
        if scene_id in seen_ids:
            errors.append(f"Duplicate scene id: {scene_id}")
        seen_ids.add(scene_id)

        for field in REQUIRED_SCENE_FIELDS:
            if field not in scene or _is_empty(scene[field]):
                errors.append(f"{scene_id}: missing or empty field '{field}'")

        if require_strict_alignment:
            for field in STRICT_ALIGNMENT_FIELDS:
                if field not in scene or _is_empty(scene[field]):
                    errors.append(f"{scene_id}: missing or empty strict-alignment field '{field}'")
            errors.extend(_validate_strict_alignment(scene_id, scene))

        if require_square_edges:
            for field in SQUARE_EDGE_FIELDS:
                if field not in scene or _is_empty(scene[field]):
                    errors.append(f"{scene_id}: missing or empty square-edge field '{field}'")
            edge_text = _flatten_text({field: scene.get(field) for field in SQUARE_EDGE_FIELDS}).lower()
            if not any(marker in edge_text for marker in SQUARE_EDGE_MARKERS):
                errors.append(
                    f"{scene_id}: edge/corner policy must explicitly require square, rectangular, hard-edge, or 0-radius geometry"
                )
            if _has_forbidden_rounding(edge_text):
                errors.append(
                    f"{scene_id}: edge/corner policy must not allow rounded, pill, soft-edge, blob, or positive-radius geometry"
                )

        if require_validation_contract:
            for field in VALIDATION_CONTRACT_FIELDS:
                if field not in scene or _is_empty(scene[field]):
                    errors.append(f"{scene_id}: missing or empty validation-contract field '{field}'")

        if require_zero_box_padding:
            for field in ZERO_PADDING_FIELDS:
                if field not in scene or _is_empty(scene[field]):
                    errors.append(f"{scene_id}: missing or empty zero-padding field '{field}'")
            if not _has_zero_padding_policy(scene):
                errors.append(
                    f"{scene_id}: boxModel must explicitly set internalPaddingPx to 0 and contentFlushToBounds to true"
                )
            for padding_error in _find_positive_padding(scene):
                errors.append(f"{scene_id}: positive padding is not allowed under zero-padding mode: {padding_error}")

        if require_grayscale_hierarchy:
            for field in GRAY_HIERARCHY_FIELDS:
                if field not in scene or _is_empty(scene[field]):
                    errors.append(f"{scene_id}: missing or empty grayscale hierarchy field '{field}'")
            if "grayscaleHierarchy" in scene:
                errors.extend(_validate_gray_hierarchy(scene_id, scene["grayscaleHierarchy"]))

        depth_layers = scene.get("depthLayers")
        if isinstance(depth_layers, list) and len(depth_layers) < 3:
            errors.append(f"{scene_id}: depthLayers should contain at least 3 layers")

        motion_phases = scene.get("motionPhases")
        held = str(scene.get("sceneJob", "")).lower().find("held") >= 0 or str(
            scene.get("compositionChoice", "")
        ).lower().find("held") >= 0
        if isinstance(motion_phases, list):
            if not motion_phases:
                errors.append(f"{scene_id}: motionPhases must not be empty")
            if len(motion_phases) < 2 and not (allow_held_scenes and held):
                errors.append(
                    f"{scene_id}: motionPhases should include more than one phase unless it is a deliberate held read"
                )
            for phase_index, phase in enumerate(motion_phases, start=1):
                if not isinstance(phase, dict):
                    errors.append(f"{scene_id}: motion phase {phase_index} must be an object")
                    continue
                for phase_field in ["name", "cue", "visualChange", "motionVerb"]:
                    if _is_empty(phase.get(phase_field)):
                        errors.append(
                            f"{scene_id}: motion phase {phase_index} missing '{phase_field}'"
                        )

        checks = scene.get("validationChecks")
        if isinstance(checks, list) and len(checks) < 2:
            errors.append(f"{scene_id}: validationChecks should contain at least 2 checks")
        if require_validation_contract and isinstance(checks, list):
            for check_index, check in enumerate(checks, start=1):
                if not isinstance(check, dict):
                    errors.append(f"{scene_id}: validation check {check_index} must be an object")
                    continue
                for check_field in VALIDATION_CHECK_FIELDS:
                    if _is_empty(check.get(check_field)):
                        errors.append(
                            f"{scene_id}: validation check {check_index} missing '{check_field}'"
                        )

        rationale = str(scene.get("choiceRationale", ""))
        if len(rationale.strip()) < 30:
            errors.append(f"{scene_id}: choiceRationale is too short to explain the choice")

    return errors


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate a scene composition JSON plan.")
    parser.add_argument("--plan", required=True, type=Path, help="Path to composition-plan.json")
    parser.add_argument("--expect-scenes", type=int, help="Require an exact scene count")
    parser.add_argument("--min-scenes", type=int, help="Require at least this many scenes")
    parser.add_argument(
        "--require-anchor",
        action="append",
        default=[],
        help="Literal string that must appear in the plan; repeat as needed",
    )
    parser.add_argument(
        "--forbid",
        action="append",
        default=[],
        help="Forbidden term; defaults also include GSAP-related terms",
    )
    parser.add_argument(
        "--allow-gsap",
        action="store_true",
        help="Do not apply the default GSAP-related forbidden terms",
    )
    parser.add_argument(
        "--allow-held-scenes",
        action="store_true",
        help="Allow deliberate held scenes to have a single motion phase",
    )
    parser.add_argument(
        "--require-strict-alignment",
        action="store_true",
        help="Require alignmentGrid, armatureAnchors, and objectBounds on each scene",
    )
    parser.add_argument(
        "--require-square-edges",
        action="store_true",
        help="Require edgePolicy and cornerPolicy to specify square, hard-edge, or 0-radius geometry",
    )
    parser.add_argument(
        "--require-validation-contract",
        action="store_true",
        help="Require validationContract and structured validationChecks with method, target, and passCriterion",
    )
    parser.add_argument(
        "--require-zero-box-padding",
        action="store_true",
        help="Require boxInteriorPolicy, boxModel, and explicit internalPaddingPx 0 or flush-to-bounds language.",
    )
    parser.add_argument(
        "--require-grayscale-hierarchy",
        action="store_true",
        help="Require structured grayscaleHierarchy levels with distinct monotonic grayscale hex values.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    plan = load_plan(args.plan)
    forbidden = list(args.forbid)
    if not args.allow_gsap:
        forbidden.extend(DEFAULT_FORBIDDEN)

    errors = validate_plan(
        plan,
        expect_scenes=args.expect_scenes,
        min_scenes=args.min_scenes,
        require_anchors=args.require_anchor,
        forbidden=forbidden,
        allow_held_scenes=args.allow_held_scenes,
        require_strict_alignment=args.require_strict_alignment,
        require_square_edges=args.require_square_edges,
        require_validation_contract=args.require_validation_contract,
        require_zero_box_padding=args.require_zero_box_padding,
        require_grayscale_hierarchy=args.require_grayscale_hierarchy,
    )
    if errors:
        print("Scene composition plan validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print(f"Scene composition plan OK: {len(plan.get('scenes', []))} scene(s) validated.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
