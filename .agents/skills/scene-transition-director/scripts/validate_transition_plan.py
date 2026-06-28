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


def validate_transition(transition: Any, index: int) -> None:
    if not isinstance(transition, dict):
        fail(f"transition {index} must be an object")

    missing = sorted(REQUIRED_TRANSITION_FIELDS - set(transition))
    if missing:
        fail(f"transition {index} is missing fields: {', '.join(missing)}")

    for field in REQUIRED_TRANSITION_FIELDS - {"validationChecks", "start", "duration"}:
        value = transition.get(field)
        if not isinstance(value, str) or not value.strip():
            fail(f"transition {transition.get('id', index)} field '{field}' must be a non-empty string")

    for field in ("start", "duration"):
        value = transition.get(field)
        if not isinstance(value, (int, float)) or value < 0:
            fail(f"transition {transition.get('id', index)} field '{field}' must be a non-negative number")
    if transition["duration"] <= 0:
        fail(f"transition {transition.get('id', index)} duration must be positive")

    checks = transition.get("validationChecks")
    if not isinstance(checks, list) or not checks:
        fail(f"transition {transition.get('id', index)} validationChecks must be a non-empty list")
    if not all(isinstance(check, str) and check.strip() for check in checks):
        fail(f"transition {transition.get('id', index)} validationChecks must contain non-empty strings")

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
        validate_transition(transition, index)
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
