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
