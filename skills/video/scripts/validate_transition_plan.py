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


REQUIRED_TRANSITION_FIELDS = {
    "id",
    "fromScene",
    "toScene",
    "start",
    "duration",
    "family",
    "surprise",
    "outgoingState",
    "bridgeAction",
    "incomingState",
    "compositionShift",
    "colorShift",
    "cameraShift",
    "spaceShift",
    "validationChecks",
}
KNOWN_FAMILIES = {
    "match cut",
    "match cut axis",
    "persistent object",
    "persistent object flight",
    "camera move",
    "camera parallax move",
    "color handoff",
    "color state wash",
    "object color cover",
    "full-screen color card",
    "spatial portal",
    "spatial portal reveal",
    "morph",
    "morph continuity",
    "interrupt",
    "interrupt gate snap",
    "static anchor sweep",
    "extreme zoom reframe",
    "depth stack reveal",
    "negative space cut",
    "hard cut",
}
SEMANTIC_TRANSITION_FIELDS = {
    "semanticPurpose",
    "stateChange",
    "attentionHandoff",
    "styleContinuity",
    "alignmentRule",
    "edgeRule",
    "genericMotionRejected",
    "validationFrames",
}
ZERO_PADDING_FIELDS = {"boxPaddingRule"}
GRAYSCALE_HIERARCHY_FIELDS = {"grayscaleHierarchyRule"}
STRUCTURED_CHECK_FIELDS = {"method", "target", "passCriterion"}
VALIDATION_FRAME_TARGET_FIELDS = {"target", "passCriterion"}
SQUARE_EDGE_MARKERS = ("square", "0-radius", "zero-radius", "hard edge", "hard-edge", "rectangular")
ALIGNMENT_MARKERS = ("grid", "axis", "baseline", "orthogonal", "align", "row", "column")
ZERO_PADDING_MARKERS = ("internalpaddingpx 0", "internal padding 0", "0px internal padding", "zero", "no internal padding", "flush", "content flush")
PADDING_KEYS = {"internalpaddingpx", "paddingpx", "boxpaddingpx", "padding"}
ROUNDING_PATTERNS = (
    r"\brounded\b",
    r"\bpill\b",
    r"\bblob\b",
    r"\bsoft[- ]edge\b",
    r"\bborder[- ]radius\b",
    r"\bcorner[- ]radius\b",
    r"\bradius\s+[1-9]\d*(?:\.\d+)?\b",
)


def fail(message: str) -> None:
    print(f"Transition plan validation failed: {message}", file=sys.stderr)
    raise SystemExit(1)


def load_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        fail(f"{path} is not valid JSON: {error}")
    if not isinstance(data, dict):
        fail("plan root must be a JSON object")
    return data


def contains_text(value: Any, needle: str) -> bool:
    if isinstance(value, str):
        return needle.lower() in value.lower()
    if isinstance(value, dict):
        return any(contains_text(child, needle) for child in value.values())
    if isinstance(value, list):
        return any(contains_text(child, needle) for child in value)
    return False


def _non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _parse_hex_gray(value: Any) -> tuple[int, int, int] | None:
    if not isinstance(value, str) or len(value.strip()) != 7 or not value.strip().startswith("#"):
        return None
    raw = value.strip()[1:]
    try:
        rgb = tuple(int(raw[idx : idx + 2], 16) for idx in (0, 2, 4))
    except ValueError:
        return None
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
            if str(key).lower() in PADDING_KEYS:
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


def _has_forbidden_rounding(text: str) -> bool:
    lowered = text.lower()
    if "source-native only" in lowered:
        return False
    normalized = lowered.replace("0-radius", "").replace("zero-radius", "")
    return any(re.search(pattern, normalized) for pattern in ROUNDING_PATTERNS)


def _extract_gray_scale(value: Any) -> list[tuple[int, int, str]]:
    levels: list[tuple[int, int, str]] = []
    if isinstance(value, dict):
        raw_items = value.get("levels") if isinstance(value.get("levels"), list) else list(value.values())
    elif isinstance(value, list):
        raw_items = value
    else:
        raw_items = []
    for index, item in enumerate(raw_items):
        if not isinstance(item, dict):
            continue
        raw_level = item.get("level", index)
        if not isinstance(raw_level, int):
            continue
        gray_value = item.get("grayHex") or item.get("hex")
        rgb = _parse_hex_gray(gray_value)
        if rgb is not None:
            levels.append((raw_level, rgb[0], str(gray_value).lower()))
    return levels


def _validate_gray_scale(owner: str, value: Any) -> None:
    levels = _extract_gray_scale(value)
    if len(levels) < 3:
        fail(f"{owner} grayscale hierarchy must contain at least three structured gray levels")
    if len({level for level, _, _ in levels}) != len(levels):
        fail(f"{owner} grayscale hierarchy levels must be distinct")
    if len({hex_value for _, _, hex_value in levels}) != len(levels):
        fail(f"{owner} grayscale hierarchy grayHex values must be distinct")
    ordered = sorted(levels)
    values = [gray for _, gray, _ in ordered]
    increasing = all(a < b for a, b in zip(values, values[1:]))
    decreasing = all(a > b for a, b in zip(values, values[1:]))
    if not (increasing or decreasing):
        fail(f"{owner} grayscale hierarchy gray values must be monotonic by level")


def validate_transition(
    transition: Any,
    index: int,
    *,
    require_semantic_fields: bool,
    require_square_edge_style: bool,
    require_zero_box_padding: bool,
    require_grayscale_hierarchy: bool,
    persistent_name: str | None,
) -> None:
    if not isinstance(transition, dict):
        fail(f"transition {index} must be an object")

    missing = sorted(REQUIRED_TRANSITION_FIELDS - set(transition))
    if missing:
        fail(f"transition {index} is missing fields: {', '.join(missing)}")

    for field in REQUIRED_TRANSITION_FIELDS - {"validationChecks", "start", "duration"}:
        value = transition.get(field)
        if not isinstance(value, str) or not value.strip():
            fail(f"transition {transition.get('id', index)} field '{field}' must be a non-empty string")

    family = str(transition.get("family", "")).strip().lower()
    if family not in KNOWN_FAMILIES:
        fail(
            f"transition {transition.get('id', index)} family {transition.get('family')!r} "
            "is not in the known transition family set"
        )

    if require_semantic_fields:
        missing = sorted(SEMANTIC_TRANSITION_FIELDS - set(transition))
        if missing:
            fail(f"transition {transition.get('id', index)} is missing semantic fields: {', '.join(missing)}")
        for field in SEMANTIC_TRANSITION_FIELDS - {"validationFrames"}:
            if not _non_empty_string(transition.get(field)):
                fail(f"transition {transition.get('id', index)} field '{field}' must be a non-empty string")
        rejection = str(transition.get("genericMotionRejected", "")).strip()
        if len(rejection) < 20 or rejection.lower() in {"yes", "true", "generic motion rejected"}:
            fail(
                f"transition {transition.get('id', index)} genericMotionRejected must explain why a generic slide, pan, pulse, or wipe is wrong"
            )
        if persistent_name:
            persistent_terms = [term for term in re.split(r"\s+", persistent_name.lower()) if len(term) >= 3]
            transition_text = " ".join(
                str(transition.get(field, "")).lower()
                for field in ("outgoingState", "bridgeAction", "incomingState", "attentionHandoff")
            )
            if persistent_terms and not any(term in transition_text for term in persistent_terms):
                fail(
                    f"transition {transition.get('id', index)} must reference persistentElement.name in outgoingState, bridgeAction, incomingState, or attentionHandoff"
                )

    if require_zero_box_padding:
        missing = sorted(ZERO_PADDING_FIELDS - set(transition))
        if missing:
            fail(f"transition {transition.get('id', index)} is missing zero-padding fields: {', '.join(missing)}")
        rule_text = str(transition.get("boxPaddingRule", "")).lower()
        if not any(marker in rule_text for marker in ZERO_PADDING_MARKERS):
            fail(
                f"transition {transition.get('id', index)} boxPaddingRule must explicitly require zero/no internal padding or flush-to-bounds boxes"
            )
        for padding_error in _find_positive_padding(transition):
            fail(
                f"transition {transition.get('id', index)} positive padding is not allowed under zero-padding mode: {padding_error}"
            )

    if require_grayscale_hierarchy:
        missing = sorted(GRAYSCALE_HIERARCHY_FIELDS - set(transition))
        if missing:
            fail(f"transition {transition.get('id', index)} is missing grayscale hierarchy fields: {', '.join(missing)}")
        scale = transition.get("grayscaleHierarchy") or transition.get("grayscaleHierarchyScale")
        if scale is None:
            fail(
                f"transition {transition.get('id', index)} must provide structured grayscaleHierarchy or grayscaleHierarchyScale"
            )
        _validate_gray_scale(f"transition {transition.get('id', index)}", scale)

    for field in ("start", "duration"):
        value = transition.get(field)
        if not isinstance(value, (int, float)) or value < 0:
            fail(f"transition {transition.get('id', index)} field '{field}' must be a non-negative number")
    if transition["duration"] <= 0:
        fail(f"transition {transition.get('id', index)} duration must be positive")

    checks = transition.get("validationChecks")
    if not isinstance(checks, list) or not checks:
        fail(f"transition {transition.get('id', index)} validationChecks must be a non-empty list")
    for check_index, check in enumerate(checks, start=1):
        if isinstance(check, str) and check.strip():
            continue
        if isinstance(check, dict) and all(_non_empty_string(check.get(field)) for field in STRUCTURED_CHECK_FIELDS):
            continue
        fail(
            f"transition {transition.get('id', index)} validation check {check_index} must be a non-empty string or an object with method, target, and passCriterion"
        )

    validation_frames = transition.get("validationFrames")
    if require_semantic_fields:
        if not isinstance(validation_frames, list) or not validation_frames:
            fail(f"transition {transition.get('id', index)} validationFrames must be a non-empty list")
        for frame_index, frame in enumerate(validation_frames, start=1):
            if not isinstance(frame, dict):
                fail(f"transition {transition.get('id', index)} validation frame {frame_index} must be an object")
            has_time = _non_empty_string(frame.get("time")) or _non_empty_string(frame.get("timestamp"))
            if not has_time:
                fail(f"transition {transition.get('id', index)} validation frame {frame_index} needs time or timestamp")
            for field in VALIDATION_FRAME_TARGET_FIELDS:
                if not _non_empty_string(frame.get(field)):
                    fail(f"transition {transition.get('id', index)} validation frame {frame_index} missing '{field}'")

    if require_square_edge_style:
        for field in ("styleContinuity", "alignmentRule", "edgeRule"):
            if not _non_empty_string(transition.get(field)):
                fail(f"transition {transition.get('id', index)} field '{field}' is required for square-edge style")
        alignment_text = str(transition.get("alignmentRule", "")).lower()
        edge_text = str(transition.get("edgeRule", "")).lower()
        if not any(marker in alignment_text for marker in ALIGNMENT_MARKERS):
            fail(
                f"transition {transition.get('id', index)} alignmentRule must mention a grid, axis, baseline, row, column, or alignment rule"
            )
        if not any(marker in edge_text for marker in SQUARE_EDGE_MARKERS):
            fail(
                f"transition {transition.get('id', index)} edgeRule must mention square, rectangular, hard-edge, or 0-radius geometry"
            )
        square_text = "\n".join(str(transition.get(field, "")) for field in ("styleContinuity", "alignmentRule", "edgeRule"))
        if _has_forbidden_rounding(square_text):
            fail(
                f"transition {transition.get('id', index)} square-edge fields must not allow rounded, pill, soft-edge, blob, or positive-radius geometry"
            )

    if transition["fromScene"] == transition["toScene"]:
        fail(f"transition {transition.get('id', index)} fromScene and toScene must differ")


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a scene transition plan JSON file.")
    parser.add_argument("--plan", type=Path, required=True, help="Path to transition-plan.json.")
    parser.add_argument("--expect-transitions", type=int, default=None, help="Expected transition count.")
    parser.add_argument("--expect-persistent-name", default=None, help="Expected exact persistentElement.name.")
    parser.add_argument(
        "--expect-chain",
        default=None,
        help="Comma-separated exact scene ID chain. Requires transitions to connect adjacent IDs in order.",
    )
    parser.add_argument("--require-anchor", action="append", default=[], help="Text that must appear in the plan.")
    parser.add_argument("--forbid", action="append", default=[], help="Text that must not appear in the plan.")
    parser.add_argument(
        "--require-semantic-fields",
        action="store_true",
        help="Require semantic purpose, state change, attention handoff, style continuity, alignment, edge, generic-motion rejection, and validation frames.",
    )
    parser.add_argument(
        "--require-square-edge-style",
        action="store_true",
        help="Require alignment and edge rules suitable for square, hard-edge transition styles.",
    )
    parser.add_argument(
        "--require-zero-box-padding",
        action="store_true",
        help="Require transitions to preserve zero internal box padding or flush-to-bounds box geometry.",
    )
    parser.add_argument(
        "--require-grayscale-hierarchy",
        action="store_true",
        help="Require transitions to preserve structured grayscale hierarchy levels rather than hue-only hierarchy.",
    )
    args = parser.parse_args()

    plan = load_json(args.plan)

    if plan.get("version") != 1:
        fail("version must be 1")
    if not isinstance(plan.get("videoId"), str) or not plan["videoId"].strip():
        fail("videoId must be a non-empty string")

    persistent = plan.get("persistentElement")
    if not isinstance(persistent, dict):
        fail("persistentElement must be an object")
    for field in ("name", "role", "states"):
        if field not in persistent:
            fail(f"persistentElement is missing '{field}'")
    if not isinstance(persistent["name"], str) or not persistent["name"].strip():
        fail("persistentElement.name must be a non-empty string")
    if args.expect_persistent_name is not None and persistent["name"] != args.expect_persistent_name:
        fail(
            "persistentElement.name "
            f"{persistent['name']!r} does not match expected {args.expect_persistent_name!r}"
        )
    if not isinstance(persistent["role"], str) or not persistent["role"].strip():
        fail("persistentElement.role must be a non-empty string")
    if not isinstance(persistent["states"], list) or len(persistent["states"]) < 2:
        fail("persistentElement.states must contain at least two states")

    transitions = plan.get("transitions")
    if not isinstance(transitions, list) or not transitions:
        fail("transitions must be a non-empty list")
    if args.expect_transitions is not None and len(transitions) != args.expect_transitions:
        fail(f"expected {args.expect_transitions} transitions, found {len(transitions)}")
    if args.expect_chain:
        chain = [item.strip() for item in args.expect_chain.split(",") if item.strip()]
        if len(chain) < 2:
            fail("--expect-chain must contain at least two scene IDs")
        expected_pairs = list(zip(chain, chain[1:]))
        if len(transitions) != len(expected_pairs):
            fail(f"expected chain implies {len(expected_pairs)} transitions, found {len(transitions)}")

    seen_ids: set[str] = set()
    previous_start = -1.0
    for index, transition in enumerate(transitions, start=1):
        validate_transition(
            transition,
            index,
            require_semantic_fields=args.require_semantic_fields,
            require_square_edge_style=args.require_square_edge_style,
            require_zero_box_padding=args.require_zero_box_padding,
            require_grayscale_hierarchy=args.require_grayscale_hierarchy,
            persistent_name=persistent["name"],
        )
        transition_id = transition["id"]
        if transition_id in seen_ids:
            fail(f"duplicate transition id: {transition_id}")
        seen_ids.add(transition_id)
        if transition["start"] < previous_start:
            fail("transitions must be sorted by nondecreasing start time")
        previous_start = transition["start"]
        if args.expect_chain:
            expected_from, expected_to = expected_pairs[index - 1]
            if transition["fromScene"] != expected_from or transition["toScene"] != expected_to:
                fail(
                    f"transition {transition_id} should connect "
                    f"{expected_from!r} -> {expected_to!r}, found "
                    f"{transition['fromScene']!r} -> {transition['toScene']!r}"
                )

    for anchor in args.require_anchor:
        if not contains_text(plan, anchor):
            fail(f"required anchor not found: {anchor}")
    for forbidden in args.forbid:
        if contains_text(plan, forbidden):
            fail(f"forbidden text found: {forbidden}")

    print("Transition plan validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
