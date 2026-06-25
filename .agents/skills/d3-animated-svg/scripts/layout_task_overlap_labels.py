#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

"""Generate a deterministic saturated task-overlap label layout.

The gallery uses the generated JavaScript data file directly so the dense
example can be audited without running a browser-time label solver.
"""

from __future__ import annotations

import argparse
import json
import math
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Any


SKILL_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = (
    SKILL_ROOT
    / "assets"
    / "examples"
    / "d3-animated-svg"
    / "task-overlap-layouts.js"
)

WIDTH = 560
HEIGHT = 420
LABEL_FONT_SIZE = 7.8
LABEL_PADDING_X = 13.0
LABEL_TEXT_PADDING_X = 4.6
LABEL_ROW_START = 38.5
LABEL_ROW_STEP = 14.0
LABEL_ROW_COUNT = 25
MAX_LABEL_WIDTH = 88.0
DOT_MIN_DISTANCE = 4.8
TASK_COUNT = 100
SEED = 20260624

SCOPE_CODES = {
    "backlog": "BL",
    "ux": "UX",
    "api": "API",
    "security": "SEC",
    "docs": "DOC",
    "data": "DATA",
    "qa": "QA",
    "release": "REL",
    "ops": "OPS",
}

SCOPE_TERMS = {
    "backlog": "intake",
    "ux": "copy",
    "api": "schema",
    "security": "auth",
    "docs": "guide",
    "data": "seed",
    "qa": "smoke",
    "release": "cutover",
    "ops": "runbook",
}


CIRCLES: list[dict[str, Any]] = [
    {
        "id": "backlog",
        "label": "Backlog",
        "cx": 150,
        "cy": 135,
        "r": 74,
        "fill": "blueHighlight",
        "stroke": "blue",
        "lx": 82,
        "ly": 58,
    },
    {
        "id": "ux",
        "label": "UX",
        "cx": 232,
        "cy": 100,
        "r": 66,
        "fill": "orangeHighlight",
        "stroke": "orange",
        "lx": 218,
        "ly": 42,
    },
    {
        "id": "api",
        "label": "API",
        "cx": 326,
        "cy": 135,
        "r": 76,
        "fill": "greenHighlight",
        "stroke": "green",
        "lx": 344,
        "ly": 58,
    },
    {
        "id": "security",
        "label": "Security",
        "cx": 414,
        "cy": 100,
        "r": 58,
        "fill": "redHighlight",
        "stroke": "red",
        "lx": 416,
        "ly": 42,
    },
    {
        "id": "docs",
        "label": "Docs",
        "cx": 96,
        "cy": 215,
        "r": 62,
        "fill": "purpleHighlight",
        "stroke": "purple",
        "lx": 48,
        "ly": 167,
    },
    {
        "id": "data",
        "label": "Data",
        "cx": 232,
        "cy": 206,
        "r": 86,
        "fill": "yellowHighlight",
        "stroke": "yellowHover",
        "lx": 214,
        "ly": 204,
    },
    {
        "id": "qa",
        "label": "QA",
        "cx": 344,
        "cy": 228,
        "r": 74,
        "fill": "blueHighlight",
        "stroke": "blueHover",
        "lx": 378,
        "ly": 214,
    },
    {
        "id": "release",
        "label": "Release",
        "cx": 160,
        "cy": 280,
        "r": 68,
        "fill": "greenHighlight",
        "stroke": "greenHover",
        "lx": 102,
        "ly": 346,
    },
    {
        "id": "ops",
        "label": "Ops",
        "cx": 420,
        "cy": 290,
        "r": 60,
        "fill": "orangeHighlight",
        "stroke": "orangeHover",
        "lx": 444,
        "ly": 356,
    },
]


@dataclass(frozen=True)
class LabelSlot:
    x: float
    y: float
    lane: int
    side: str


def estimate_text_width(text: str, font_size: float = LABEL_FONT_SIZE) -> float:
    """Conservative SVG text-width estimate for Open Sans-like labels."""
    total = 0.0
    for char in text:
        if char in "MW@#%":
            total += 0.92
        elif char in "ABCDEFGHKNOPQRSTUVWXYZ0123456789":
            total += 0.68
        elif char in "ilI.,:;!|":
            total += 0.34
        elif char == " ":
            total += 0.32
        else:
            total += 0.56
    return total * font_size


def label_height(font_size: float) -> float:
    return round(font_size + 4.2, 2)


def label_width(label: str, font_size: float) -> float:
    return round(max(28.0, estimate_text_width(label, font_size) + LABEL_PADDING_X), 2)


def task_label_spec(task_id: str, memberships: list[str], index: int) -> dict[str, Any]:
    primary = memberships[0]
    secondary = memberships[1] if len(memberships) > 1 else primary
    long_label = f"{task_id} {SCOPE_TERMS[primary]} {SCOPE_TERMS[secondary]}"
    medium_label = f"{task_id} {SCOPE_TERMS[primary]}"
    code_label = f"{task_id} {SCOPE_CODES[primary]}"

    if index % 4 == 0:
        label = long_label
        font_size = 6.6
        bucket = "long"
    elif index % 3 == 0:
        label = medium_label
        font_size = 7.2
        bucket = "medium"
    elif index % 5 == 0:
        label = code_label
        font_size = 7.8
        bucket = "medium"
    else:
        label = task_id
        font_size = 8.4
        bucket = "short"

    width = label_width(label, font_size)
    if width > MAX_LABEL_WIDTH:
        raise RuntimeError(f"Label is too wide for the lane contract: {label!r} => {width}")

    return {
        "label": label,
        "labelFontSize": font_size,
        "labelHeight": label_height(font_size),
        "labelWidth": width,
        "labelLengthBucket": bucket,
        "labelTextPaddingX": LABEL_TEXT_PADDING_X,
    }


def memberships_for_point(x: float, y: float) -> list[str]:
    memberships = []
    for circle in CIRCLES:
        if (x - circle["cx"]) ** 2 + (y - circle["cy"]) ** 2 <= circle["r"] ** 2:
            memberships.append(circle["id"])
    return memberships


def generate_candidates(seed: int) -> list[tuple[float, float, list[str]]]:
    rng = random.Random(seed)
    candidates: list[tuple[float, float, list[str]]] = []
    for _ in range(24_000):
        x = rng.uniform(42, 510)
        y = rng.uniform(48, 352)
        memberships = memberships_for_point(x, y)
        if memberships:
            candidates.append((x, y, memberships))
    rng.shuffle(candidates)
    return candidates


def far_enough(x: float, y: float, selected: list[dict[str, Any]]) -> bool:
    min_distance_sq = DOT_MIN_DISTANCE * DOT_MIN_DISTANCE
    return all((x - item["x"]) ** 2 + (y - item["y"]) ** 2 >= min_distance_sq for item in selected)


def select_tasks(seed: int, task_count: int) -> list[dict[str, Any]]:
    if task_count != 100:
        raise ValueError("This gallery fixture currently expects exactly 100 tasks.")

    candidates = generate_candidates(seed)
    selected: list[dict[str, Any]] = []
    quota = {1: 36, 2: 36, 3: 28}

    # Guarantee a visible single-scope baseline for every circle before filling density quotas.
    for circle in CIRCLES:
        picked = 0
        for x, y, memberships in candidates:
            if picked >= 4:
                break
            if memberships == [circle["id"]] and far_enough(x, y, selected):
                selected.append({"x": x, "y": y, "memberships": memberships})
                quota[1] -= 1
                picked += 1
        if picked < 4:
            raise RuntimeError(f"Could not place four single-scope tasks for {circle['id']}")

    for bucket in (3, 2, 1):
        for x, y, memberships in candidates:
            if quota[bucket] <= 0:
                break
            if min(len(memberships), 3) == bucket and far_enough(x, y, selected):
                selected.append({"x": x, "y": y, "memberships": memberships})
                quota[bucket] -= 1

    if len(selected) != task_count or any(quota.values()):
        raise RuntimeError(f"Could not satisfy task quotas: selected={len(selected)} quota={quota}")

    selected.sort(key=lambda item: (item["y"], item["x"]))
    for index, task in enumerate(selected, start=1):
        task["id"] = f"T{index:03d}"
        task["membershipCount"] = len(task["memberships"])
        task.update(task_label_spec(task["id"], task["memberships"], index))
    return selected


def label_slots() -> list[LabelSlot]:
    rows = [LABEL_ROW_START + index * LABEL_ROW_STEP for index in range(LABEL_ROW_COUNT)]
    lanes = [
        ("left", 20, 0),
        ("left", 112, 1),
        ("right", 340, 2),
        ("right", 432, 3),
    ]
    return [LabelSlot(x=x, y=y, lane=lane, side=side) for side, x, lane in lanes for y in rows]


def box_for(task: dict[str, Any], slot: LabelSlot) -> dict[str, float]:
    return {
        "x0": slot.x,
        "y0": slot.y,
        "x1": slot.x + task["labelWidth"],
        "y1": slot.y + task["labelHeight"],
        "w": task["labelWidth"],
        "h": task["labelHeight"],
    }


def preferred_side(task: dict[str, Any]) -> str:
    return "left" if task["x"] < WIDTH / 2 else "right"


def slot_cost(task: dict[str, Any], slot: LabelSlot) -> float:
    box = box_for(task, slot)
    cx = (box["x0"] + box["x1"]) / 2
    cy = (box["y0"] + box["y1"]) / 2
    distance = math.hypot(cx - task["x"], cy - task["y"])
    side_penalty = 90 if slot.side != preferred_side(task) else 0
    inner_lane = slot.lane in (2, 3)
    outer_lane = slot.lane in (0, 5)
    centrality = 1 - min(1, math.hypot(task["x"] - 280, task["y"] - 210) / 250)
    lane_penalty = (0 if inner_lane else 13 if outer_lane else 7) * centrality
    vertical_penalty = abs(cy - task["y"]) * 0.12
    return distance + side_penalty + lane_penalty + vertical_penalty


def assign_slots(tasks: list[dict[str, Any]], seed: int) -> None:
    slots = label_slots()
    used: set[int] = set()
    ordered = sorted(
        range(len(tasks)),
        key=lambda idx: (
            -min(3, tasks[idx]["membershipCount"]),
            math.hypot(tasks[idx]["x"] - 280, tasks[idx]["y"] - 210),
        ),
    )
    assignment: dict[int, int] = {}
    for task_index in ordered:
        available = [slot_index for slot_index in range(len(slots)) if slot_index not in used]
        best_slot = min(available, key=lambda slot_index: slot_cost(tasks[task_index], slots[slot_index]))
        assignment[task_index] = best_slot
        used.add(best_slot)

    rng = random.Random(seed + 101)
    current = sum(slot_cost(tasks[task_index], slots[slot_index]) for task_index, slot_index in assignment.items())
    task_indices = list(range(len(tasks)))
    for iteration in range(30_000):
        a, b = rng.sample(task_indices, 2)
        old_a = assignment[a]
        old_b = assignment[b]
        before = slot_cost(tasks[a], slots[old_a]) + slot_cost(tasks[b], slots[old_b])
        after = slot_cost(tasks[a], slots[old_b]) + slot_cost(tasks[b], slots[old_a])
        temperature = 18 * (0.99955**iteration) + 0.03
        if after < before or math.exp((before - after) / temperature) > rng.random():
            assignment[a] = old_b
            assignment[b] = old_a
            current += after - before

    for task_index, slot_index in assignment.items():
        slot = slots[slot_index]
        tasks[task_index]["labelX"] = round(slot.x, 2)
        tasks[task_index]["labelY"] = round(slot.y, 2)
        tasks[task_index]["labelLane"] = slot.lane
        tasks[task_index]["labelSide"] = slot.side


def overlap_count(tasks: list[dict[str, Any]], pad: float = 1.0) -> int:
    count = 0
    boxes = [
        {
            "x0": task["labelX"],
            "y0": task["labelY"],
            "x1": task["labelX"] + task["labelWidth"],
            "y1": task["labelY"] + task["labelHeight"],
        }
        for task in tasks
    ]
    for index, a in enumerate(boxes):
        for b in boxes[index + 1 :]:
            if not (
                a["x1"] + pad <= b["x0"]
                or a["x0"] - pad >= b["x1"]
                or a["y1"] + pad <= b["y0"]
                or a["y0"] - pad >= b["y1"]
            ):
                count += 1
    return count


def rounded_task(task: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": task["id"],
        "label": task["label"],
        "x": round(task["x"], 2),
        "y": round(task["y"], 2),
        "memberships": task["memberships"],
        "membershipCount": task["membershipCount"],
        "labelX": task["labelX"],
        "labelY": task["labelY"],
        "labelWidth": task["labelWidth"],
        "labelHeight": task["labelHeight"],
        "labelFontSize": task["labelFontSize"],
        "labelLengthBucket": task["labelLengthBucket"],
        "labelTextPaddingX": task["labelTextPaddingX"],
        "labelLane": task["labelLane"],
        "labelSide": task["labelSide"],
    }


def build_payload(seed: int, task_count: int) -> dict[str, Any]:
    tasks = select_tasks(seed, task_count)
    assign_slots(tasks, seed)
    overlaps = overlap_count(tasks)
    if overlaps:
        raise RuntimeError(f"Generated label layout still has {overlaps} overlaps")

    buckets: dict[str, int] = {"1": 0, "2": 0, "3+": 0}
    for task in tasks:
        key = "3+" if task["membershipCount"] >= 3 else str(task["membershipCount"])
        buckets[key] += 1
    length_buckets = {"short": 0, "medium": 0, "long": 0}
    for task in tasks:
        length_buckets[task["labelLengthBucket"]] += 1
    font_sizes = [task["labelFontSize"] for task in tasks]
    label_heights = [task["labelHeight"] for task in tasks]
    longest_label = max(tasks, key=lambda task: len(task["label"]))["label"]

    return {
        "saturated": {
            "id": "asymmetric-task-overlap-saturated",
            "patternId": "d3-pattern-asymmetric-task-overlap-saturated",
            "labelAlgorithm": "candidate-slot-anneal",
            "seed": seed,
            "circleCount": len(CIRCLES),
            "targetCount": task_count,
            "labelOverlapCount": overlaps,
            "membershipBuckets": buckets,
            "labelLengthBuckets": length_buckets,
            "labelFontSize": LABEL_FONT_SIZE,
            "labelFontRange": {"min": min(font_sizes), "max": max(font_sizes)},
            "labelHeightRange": {"min": min(label_heights), "max": max(label_heights)},
            "maxLabelWidth": MAX_LABEL_WIDTH,
            "longestLabel": longest_label,
            "dotRadius": 2.25,
            "circles": CIRCLES,
            "tasks": [rounded_task(task) for task in tasks],
        }
    }


def write_js(payload: dict[str, Any], output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    data = json.dumps(payload, indent=2, sort_keys=False)
    output.write_text(
        "// Generated by .agents/skills/d3-animated-svg/scripts/layout_task_overlap_labels.py\n"
        "// Edit the generator, then rerun it instead of hand-editing this file.\n"
        f"window.D3_TASK_OVERLAP_LAYOUTS = {data};\n",
        encoding="utf-8",
        newline="\n",
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--seed", type=int, default=SEED)
    parser.add_argument("--task-count", type=int, default=TASK_COUNT)
    parser.add_argument("--dry-run", action="store_true", help="Validate and print a summary without writing output.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = build_payload(args.seed, args.task_count)
    saturated = payload["saturated"]
    if not args.dry_run:
        write_js(payload, args.output)
    print(
        "Generated saturated task-overlap layout: "
        f"{saturated['targetCount']} tasks, {saturated['circleCount']} circles, "
        f"{saturated['labelOverlapCount']} label overlaps, "
        f"buckets={saturated['membershipBuckets']}, "
        f"label_buckets={saturated['labelLengthBuckets']}, "
        f"font_range={saturated['labelFontRange']}"
    )
    if not args.dry_run:
        print(f"Output: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
