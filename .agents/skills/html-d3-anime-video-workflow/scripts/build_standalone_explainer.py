#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["pillow>=10.0.0"]
# ///

from __future__ import annotations

import argparse
import json
import math
import re
import shutil
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


SCRIPT_PATH = Path(__file__).resolve()
PALETTE = {
    "paper": "#f7f7f7",
    "ink": "#333e48",
    "muted": "#696969",
    "line": "#cfcfcf",
    "gray0": "#ffffff",
    "gray1": "#f7f7f7",
    "gray2": "#e7e7e7",
    "gray3": "#cfcfcf",
    "gray4": "#9c9c9c",
    "gray5": "#696969",
    "route": "#9e1b32",
    "damage": "#e8002a",
    "defense": "#4f4f4f",
    "attribute": "#6d1222",
    "tradeoff": "#e8002a",
    "atlas": "#828282",
    "gold": "#6d1222",
}

EDGE_STYLE = "square"
METRO_GRID = 4.0
BOX_PADDING_POLICY = "zero"
GRAY_LEVELS = [
    PALETTE["gray0"],
    PALETTE["gray1"],
    PALETTE["gray2"],
    PALETTE["gray3"],
    PALETTE["gray4"],
    PALETTE["gray5"],
]
METRO_ZONE_BOUNDS = [
    {"x": 44, "y": 96, "width": 304, "height": 248},
    {"x": 44, "y": 344, "width": 304, "height": 260},
    {"x": 348, "y": 96, "width": 520, "height": 508},
    {"x": 868, "y": 96, "width": 368, "height": 248},
    {"x": 868, "y": 344, "width": 368, "height": 260},
]
MASONRY_ZONE_BOUNDS = [
    {"x": 48, "y": 88, "width": 280, "height": 300},
    {"x": 48, "y": 388, "width": 400, "height": 280},
    {"x": 448, "y": 88, "width": 400, "height": 580},
    {"x": 848, "y": 88, "width": 344, "height": 580},
    {"x": 1192, "y": 88, "width": 360, "height": 580},
]
MASONRY_MODULE_BOUNDS = [
    {"x": 48, "y": 88, "width": 280, "height": 300, "zoneIndex": 0, "grayLevel": 3},
    {"x": 48, "y": 388, "width": 180, "height": 280, "zoneIndex": 1, "grayLevel": 2},
    {"x": 228, "y": 388, "width": 220, "height": 280, "zoneIndex": 1, "grayLevel": 1},
    {"x": 448, "y": 88, "width": 220, "height": 180, "zoneIndex": 2, "grayLevel": 4},
    {"x": 668, "y": 88, "width": 180, "height": 300, "zoneIndex": 2, "grayLevel": 2},
    {"x": 448, "y": 268, "width": 400, "height": 400, "zoneIndex": 2, "grayLevel": 1},
    {"x": 848, "y": 88, "width": 344, "height": 300, "zoneIndex": 3, "grayLevel": 3},
    {"x": 848, "y": 388, "width": 172, "height": 280, "zoneIndex": 3, "grayLevel": 1},
    {"x": 1020, "y": 388, "width": 172, "height": 280, "zoneIndex": 3, "grayLevel": 2},
    {"x": 1192, "y": 88, "width": 360, "height": 244, "zoneIndex": 4, "grayLevel": 4},
    {"x": 1192, "y": 332, "width": 172, "height": 336, "zoneIndex": 4, "grayLevel": 2},
    {"x": 1364, "y": 332, "width": 188, "height": 336, "zoneIndex": 4, "grayLevel": 3},
]


def snap_value(value: float, grid: float = METRO_GRID) -> float:
    if grid <= 0:
        return value
    return round(value / grid) * grid


def snap_box_to_grid(box: tuple[float, float, float, float]) -> tuple[float, float, float, float]:
    x1, y1, x2, y2 = box
    return (
        snap_value(x1),
        snap_value(y1),
        snap_value(x2),
        snap_value(y2),
    )


def snap_html_rects_to_grid(html: str) -> str:
    rect_pattern = re.compile(
        r"x:\s*(-?\d+(?:\.\d+)?)\s*,\s*y:\s*(-?\d+(?:\.\d+)?)\s*,\s*width:\s*(-?\d+(?:\.\d+)?)\s*,\s*height:\s*(-?\d+(?:\.\d+)?)"
    )

    def replace(match: re.Match[str]) -> str:
        x = float(match.group(1))
        y = float(match.group(2))
        width = float(match.group(3))
        height = float(match.group(4))
        x2 = x + width
        y2 = y + height
        sx = snap_value(x)
        sy = snap_value(y)
        sw = max(METRO_GRID, snap_value(x2) - sx)
        sh = max(METRO_GRID, snap_value(y2) - sy)
        return f"x: {sx:g}, y: {sy:g}, width: {sw:g}, height: {sh:g}"

    return rect_pattern.sub(replace, html)


def normalize_html_zero_padding_rects(html: str) -> str:
    rect_call = re.compile(r'el\("rect",\s*\{(?P<attrs>.*?)\}\);', re.DOTALL)

    def normalize_attrs(match: re.Match[str]) -> str:
        attrs = match.group("attrs")
        attrs = re.sub(r"\bx:\s*([^,\n{}]+?)\s*\+\s*(?:8|10|12|14|16|18|20|24|28|32)\b", r"x: \1", attrs)
        attrs = re.sub(r"\by:\s*([^,\n{}]+?)\s*\+\s*(?:8|10|12|14|16|18|20|24|28|32|36|38|40|48)\b", r"y: \1", attrs)
        attrs = re.sub(r"\bwidth:\s*([^,\n{}]+?)\s*-\s*(?:16|20|24|28|32|36|40|48|64)\b", r"width: \1", attrs)
        attrs = re.sub(r"\bheight:\s*([^,\n{}]+?)\s*-\s*(?:16|20|24|28|32|36|40|48|64)\b", r"height: \1", attrs)
        return f'el("rect", {{{attrs}}});'

    return rect_call.sub(normalize_attrs, html)


def normalize_html_rect_gray_levels(html: str) -> str:
    rect_call = re.compile(r'el\("rect",\s*\{(?P<attrs>.*?)\}\);', re.DOTALL)
    replacements = {
        '"#fff"': "grayLevel(1)",
        '"#ffffff"': "grayLevel(1)",
        '"#f7f7f7"': "grayLevel(1)",
        '"#e7e7e7"': "grayLevel(2)",
        '"#cfcfcf"': "grayLevel(3)",
        '"#9c9c9c"': "grayLevel(4)",
        '"#696969"': "grayLevel(5)",
        "palette.paper": "grayLevel(1)",
        "palette.line": "grayLevel(3)",
    }

    def normalize_attrs(match: re.Match[str]) -> str:
        attrs = match.group("attrs")
        fill_match = re.search(r"\bfill:\s*([^,\n{}]+(?:\?[^,\n{}]+:[^,\n{}]+)?)", attrs)
        if not fill_match:
            return match.group(0)
        fill_expr = fill_match.group(1)
        normalized = fill_expr
        for old, new in replacements.items():
            normalized = normalized.replace(old, new)
        attrs = attrs[: fill_match.start(1)] + normalized + attrs[fill_match.end(1) :]
        return f'el("rect", {{{attrs}}});'

    return rect_call.sub(normalize_attrs, html)


def normalize_render_frame_gray_color_literals(html: str) -> str:
    start = html.find("function renderConceptFrame")
    end = html.find("window.renderConceptFrame", start)
    if start < 0 or end < 0:
        return html
    replacements = {
        '"#fff"': "grayLevel(1)",
        '"#ffffff"': "grayLevel(1)",
        '"#f7f7f7"': "grayLevel(1)",
        '"#e7e7e7"': "grayLevel(2)",
        '"#cfcfcf"': "grayLevel(3)",
        '"#ccd6e3"': "grayLevel(3)",
        '"#ffccd5"': "grayLevel(4)",
        '"#9c9c9c"': "grayLevel(4)",
        '"#696969"': "grayLevel(5)",
    }
    scope = html[start:end]
    for literal, gray in replacements.items():
        scope = scope.replace(literal, gray)
    return html[:start] + scope + html[end:]


def gray_level(level: int) -> str:
    return GRAY_LEVELS[max(0, min(len(GRAY_LEVELS) - 1, level))]


def is_red_surface_fill(fill: str | None) -> bool:
    if fill is None:
        return False
    return str(fill).strip().lower() in {
        PALETTE["route"].lower(),
        PALETTE["attribute"].lower(),
        PALETTE["damage"].lower(),
        PALETTE["tradeoff"].lower(),
        "#ffccd5",
        "#e8002a",
        "#6d1222",
    }


def tonal_surface_fill(fill: str, box: tuple[float, float, float, float]) -> str:
    width = max(0.0, float(box[2]) - float(box[0]))
    height = max(0.0, float(box[3]) - float(box[1]))
    if width * height < 1800 or not is_red_surface_fill(fill):
        return fill
    raw = str(fill).strip().lower()
    if raw == "#ffccd5":
        return gray_level(2)
    if raw in {PALETTE["damage"].lower(), PALETTE["tradeoff"].lower(), "#e8002a"}:
        return gray_level(4)
    return gray_level(5)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build a small deterministic standalone explainer video package."
    )
    parser.add_argument("--project-root", required=True, type=Path)
    parser.add_argument("--title", default="Path of Exile 2 Skill Tree Strategy")
    parser.add_argument("--topic", default="Path of Exile 2")
    parser.add_argument("--output-id", default="poe2-skill-tree-strategy")
    parser.add_argument(
        "--pattern",
        choices=["auto", "skill-tree", "skill-tree-route", "systems-flow", "state-machine", "comparison-matrix", "causal-loop", "phase-timeline", "metric-dashboard", "dependency-map", "sequence-trace", "sankey-flow", "swimlane-handoff", "risk-bowtie", "scenario-tree", "evidence-ladder", "layered-architecture", "data-lineage"],
        default="auto",
        help="Visual scaffold pattern. auto routes route/pathing tree prompts to skill-tree-route, Path of Exile prompts to skill-tree, lifecycle prompts to state-machine, comparison prompts to comparison-matrix, causal prompts to causal-loop, timeline prompts to phase-timeline, metric prompts to metric-dashboard, dependency prompts to dependency-map, trace prompts to sequence-trace, sankey/conversion prompts to sankey-flow, swimlane/handoff prompts to swimlane-handoff, bowtie risk prompts to risk-bowtie, scenario prompts to scenario-tree, evidence prompts to evidence-ladder, layered architecture prompts to layered-architecture, data lineage prompts to data-lineage, and reliability prompts to systems-flow.",
    )
    parser.add_argument("--checked-date", default="July 4, 2026")
    parser.add_argument("--audience", default="general technical viewers")
    parser.add_argument("--duration", type=float, default=20.0)
    parser.add_argument("--fps", type=int, default=12)
    parser.add_argument("--width", type=int, default=1280)
    parser.add_argument("--height", type=int, default=720)
    parser.add_argument(
        "--edge-style",
        choices=["square", "soft"],
        default="square",
        help="Rectangle edge style. Use square for Metro Minimal Tonal Motion and other strict-grid videos.",
    )
    parser.add_argument(
        "--masonry-layout",
        action="store_true",
        help="Render a measurable flush Masonry megacanvas foundation for Metro design-rejection prompts.",
    )
    parser.add_argument(
        "--fact",
        action="append",
        default=[],
        help="Source fact to preserve. Repeat for every supplied fact.",
    )
    parser.add_argument(
        "--anchor",
        action="append",
        default=[],
        help="Viewer-facing strategy or visual anchor to include. Repeat as needed.",
    )
    parser.add_argument(
        "--source-url",
        action="append",
        default=[],
        help="Source URL or citation label to store in the source package.",
    )
    parser.add_argument(
        "--node-label",
        action="append",
        default=[],
        help="Pattern-specific node or variable label to render. For causal-loop, pass trigger, pressure, behavior, outcome, side-effect, and intervention labels in order.",
    )
    parser.add_argument(
        "--option-label",
        action="append",
        default=[],
        help="Option label to render for comparison-matrix scaffolds. Pass up to three labels in column order.",
    )
    parser.add_argument(
        "--criterion-label",
        action="append",
        default=[],
        help="Criterion label to render for comparison-matrix scaffolds. Pass up to four labels in row order.",
    )
    parser.add_argument(
        "--state-label",
        action="append",
        default=[],
        help="State label to render for state-machine scaffolds. Pass up to six labels in lifecycle order.",
    )
    parser.add_argument(
        "--guard-label",
        action="append",
        default=[],
        help="Guard label to render for state-machine scaffolds. Pass up to three labels in guard-panel order.",
    )
    parser.add_argument(
        "--system-label",
        action="append",
        default=[],
        help="Component label to render for systems-flow scaffolds. Pass up to eleven labels in intake, bus, queue, worker, store, control, metric, and throttle order.",
    )
    parser.add_argument(
        "--tree-label",
        action="append",
        default=[],
        help="Node label to render for skill-tree scaffolds. Pass up to eleven labels in route, branch, keystone, and Atlas order.",
    )
    parser.add_argument(
        "--meter-label",
        action="append",
        default=[],
        help="Meter label to render for skill-tree scaffolds. Pass up to three labels for damage, defense, and attribute/gear meters.",
    )
    parser.add_argument(
        "--route-label",
        action="append",
        default=[],
        help="Route label to render for skill-tree-route scaffolds. Pass up to eight labels for origin, travel, clusters, bridge, keystone, respec, and late plan.",
    )
    parser.add_argument(
        "--checkpoint-label",
        action="append",
        default=[],
        help="Checkpoint label to render for skill-tree-route scaffolds. Pass up to five labels for build checkpoints or review gates.",
    )
    parser.add_argument(
        "--phase-label",
        action="append",
        default=[],
        help="Phase label to render for phase-timeline scaffolds. Pass up to six labels in chronological order.",
    )
    parser.add_argument(
        "--metric-label",
        action="append",
        default=[],
        help="Metric label to render for metric-dashboard scaffolds. Pass up to five labels for primary, input, output, quality, and risk metrics.",
    )
    parser.add_argument(
        "--threshold-label",
        action="append",
        default=[],
        help="Threshold label to render for metric-dashboard scaffolds. Pass up to three labels for healthy, warning, and action thresholds.",
    )
    parser.add_argument(
        "--dependency-label",
        action="append",
        default=[],
        help="Dependency label to render for dependency-map scaffolds. Pass up to eight labels in dependency graph order.",
    )
    parser.add_argument(
        "--cluster-label",
        action="append",
        default=[],
        help="Cluster label to render for dependency-map scaffolds. Pass up to three labels for source, integration, and release clusters.",
    )
    parser.add_argument(
        "--trace-label",
        action="append",
        default=[],
        help="Service or span label to render for sequence-trace scaffolds. Pass up to eight labels in request path order.",
    )
    parser.add_argument(
        "--flow-label",
        action="append",
        default=[],
        help="Flow label to render for sankey-flow scaffolds. Pass up to eight labels for input, split streams, loss, transforms, merge, bottleneck, and output.",
    )
    parser.add_argument(
        "--lane-label",
        action="append",
        default=[],
        help="Lane label to render for swimlane-handoff scaffolds. Pass up to four labels for owner or team lanes.",
    )
    parser.add_argument(
        "--handoff-label",
        action="append",
        default=[],
        help="Handoff label to render for swimlane-handoff scaffolds. Pass up to eight labels in process order.",
    )
    parser.add_argument(
        "--threat-label",
        action="append",
        default=[],
        help="Threat label to render for risk-bowtie scaffolds. Pass up to four labels.",
    )
    parser.add_argument(
        "--barrier-label",
        action="append",
        default=[],
        help="Barrier label to render for risk-bowtie scaffolds. Pass up to six labels: three preventive then three mitigative.",
    )
    parser.add_argument(
        "--consequence-label",
        action="append",
        default=[],
        help="Consequence label to render for risk-bowtie scaffolds. Pass up to four labels.",
    )
    parser.add_argument(
        "--scenario-label",
        action="append",
        default=[],
        help="Scenario label to render for scenario-tree scaffolds. Pass up to seven labels for root, branches, and outcomes.",
    )
    parser.add_argument(
        "--probability-label",
        action="append",
        default=[],
        help="Probability label to render for scenario-tree scaffolds. Pass up to four labels for branch probabilities or weights.",
    )
    parser.add_argument(
        "--claim-label",
        action="append",
        default=[],
        help="Claim label to render for evidence-ladder scaffolds. Pass up to four labels for claim, baseline, counterclaim, and recommendation.",
    )
    parser.add_argument(
        "--evidence-label",
        action="append",
        default=[],
        help="Evidence label to render for evidence-ladder scaffolds. Pass up to six labels for evidence tiers, counterevidence, source gap, and decision evidence.",
    )
    parser.add_argument(
        "--layer-label",
        action="append",
        default=[],
        help="Layer label to render for layered-architecture scaffolds. Pass up to six labels in top-to-bottom layer order.",
    )
    parser.add_argument(
        "--concern-label",
        action="append",
        default=[],
        help="Concern label to render for layered-architecture scaffolds. Pass up to four labels for cross-cutting, failure, observability, and rollout concerns.",
    )
    parser.add_argument(
        "--lineage-label",
        action="append",
        default=[],
        help="Lineage label to render for data-lineage scaffolds. Pass up to six labels from source through consumer.",
    )
    parser.add_argument(
        "--quality-label",
        action="append",
        default=[],
        help="Quality label to render for data-lineage scaffolds. Pass up to four labels for schema, freshness, drift, and rollback controls.",
    )
    return parser.parse_args()


def hex_to_rgb(value: str) -> tuple[int, int, int]:
    value = value.lstrip("#")
    return int(value[0:2], 16), int(value[2:4], 16), int(value[4:6], 16)


def clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, value))


def ease(value: float) -> float:
    value = clamp(value)
    return value * value * (3 - 2 * value)


def metro_camera_pose(second: float, duration: float, exploratory: bool = False) -> tuple[int, int, float]:
    progress = second / duration if duration > 0 else 0.0
    if exploratory:
        poses = [
            (0.00, 0.0, 0.0, 1.00),
            (0.12, -72.0, -8.0, 1.15),
            (0.30, -220.0, -28.0, 1.48),
            (0.50, -470.0, -36.0, 1.62),
            (0.70, -650.0, -24.0, 1.58),
            (0.88, -420.0, 0.0, 1.44),
            (1.00, -120.0, 0.0, 1.12),
        ]
        previous = poses[0]
        current = poses[-1]
        for index in range(1, len(poses)):
            if progress <= poses[index][0]:
                previous = poses[index - 1]
                current = poses[index]
                break
        span = max(0.001, current[0] - previous[0])
        blend = ease((progress - previous[0]) / span)
        x = previous[1] + (current[1] - previous[1]) * blend
        y = previous[2] + (current[2] - previous[2]) * blend
        scale = previous[3] + (current[3] - previous[3]) * blend
        return int(snap_value(x)), int(snap_value(y)), round(scale, 3)
    inspect = ease((progress - 0.08) / 0.18)
    handoff = ease((progress - 0.36) / 0.22)
    settle = ease((progress - 0.72) / 0.20)
    x = int(snap_value(-16 * inspect + 24 * handoff - 8 * settle))
    y = int(snap_value(-8 * inspect + 16 * handoff - 8 * settle))
    scale = max(1.0, 1 + 0.10 * inspect + 0.05 * handoff - 0.06 * settle)
    return x, y, scale


def apply_metro_camera(img: Image.Image, second: float, args: argparse.Namespace) -> Image.Image:
    if bool(getattr(args, "masonry_layout", False)) and ai_alternatives_requested(args):
        progress = second / args.duration if args.duration > 0 else 0.0
        poses = [
            (0.00, 0.0, 0.0, 1.00),
            (0.16, 20.0, -8.0, 1.22),
            (0.38, -210.0, -32.0, 1.48),
            (0.60, -470.0, -24.0, 1.58),
            (0.80, -640.0, 8.0, 1.50),
            (1.00, -240.0, 0.0, 1.15),
        ]
        previous = poses[0]
        current = poses[-1]
        for index in range(1, len(poses)):
            if progress <= poses[index][0]:
                previous = poses[index - 1]
                current = poses[index]
                break
        span = max(0.001, current[0] - previous[0])
        blend = ease((progress - previous[0]) / span)
        x = int(snap_value(previous[1] + (current[1] - previous[1]) * blend))
        y = int(snap_value(previous[2] + (current[2] - previous[2]) * blend))
        scale = round(previous[3] + (current[3] - previous[3]) * blend, 3)
    else:
        x, y, scale = metro_camera_pose(second, args.duration, bool(getattr(args, "masonry_layout", False)))
    output_w = int(args.width)
    output_h = int(args.height)
    width, height = img.size
    if abs(scale - 1.0) <= 0.01 and x == 0 and y == 0 and (width, height) == (output_w, output_h):
        return img
    viewport_w = min(width, max(1, round(output_w / scale)))
    viewport_h = min(height, max(1, round(output_h / scale)))
    center_x = output_w / 2 - x
    center_y = output_h / 2 - y
    left = round(center_x - viewport_w / 2)
    top = round(center_y - viewport_h / 2)
    left = max(0, min(width - viewport_w, left))
    top = max(0, min(height - viewport_h, top))
    crop = img.crop((left, top, left + viewport_w, top + viewport_h))
    return crop.resize((output_w, output_h), Image.Resampling.BICUBIC)


def compact_label(value: str, limit: int = 22) -> str:
    cleaned = " ".join(str(value).strip().split())
    return cleaned


def cleaned_labels(values: list[str] | None) -> list[str]:
    return [" ".join(str(label).strip().split()) for label in (values or []) if str(label).strip()]


def labels_with_supplied_extras(defaults: list[str], values: list[str] | None) -> list[str]:
    supplied = cleaned_labels(values)
    if not supplied:
        return defaults[:]
    labels = defaults[:]
    for idx, label in enumerate(supplied[: len(labels)]):
        labels[idx] = label
    labels.extend(supplied[len(labels) :])
    return labels


def causal_labels(args: argparse.Namespace) -> list[str]:
    defaults = ["trigger", "pressure", "behavior", "outcome", "side effect", "intervention"]
    return labels_with_supplied_extras(defaults, args.node_label)


def comparison_labels(args: argparse.Namespace) -> tuple[list[str], list[str]]:
    option_defaults = ["fast path", "balanced", "safe path"]
    criterion_defaults = ["time", "quality", "risk", "cost"]
    return labels_with_supplied_extras(option_defaults, args.option_label), labels_with_supplied_extras(criterion_defaults, args.criterion_label)


def state_machine_labels(args: argparse.Namespace) -> tuple[list[str], list[str]]:
    state_defaults = ["received", "validated", "authorized", "executing", "committed", "done"]
    guard_defaults = ["schema guard", "policy guard", "capacity guard"]
    return labels_with_supplied_extras(state_defaults, args.state_label), labels_with_supplied_extras(guard_defaults, args.guard_label)


def systems_flow_labels(args: argparse.Namespace) -> list[str]:
    defaults = [
        "source",
        "event",
        "signal",
        "bus",
        "bounded queue",
        "worker pool",
        "DB",
        "retry policy",
        "dead-letter",
        "throughput",
        "throttle",
    ]
    return labels_with_supplied_extras(defaults, args.system_label)


def skill_tree_labels(args: argparse.Namespace) -> tuple[list[str], list[str]]:
    node_defaults = [
        "start",
        "small",
        "notable",
        "damage",
        "defense",
        "attr",
        "gear",
        "tradeoff",
        "boss",
        "points",
        "late game",
    ]
    meter_defaults = ["damage plan", "defense check", "attribute fit"]
    return labels_with_supplied_extras(node_defaults, args.tree_label), labels_with_supplied_extras(meter_defaults, args.meter_label)


def skill_tree_route_labels(args: argparse.Namespace) -> tuple[list[str], list[str]]:
    route_defaults = [
        "class start",
        "travel nodes",
        "damage cluster",
        "defense cluster",
        "attribute bridge",
        "keystone tradeoff",
        "respec checkpoint",
        "late specialization",
    ]
    checkpoint_defaults = [
        "identity lock",
        "damage floor",
        "defense layer",
        "gear fit",
        "respec review",
    ]
    return labels_with_supplied_extras(route_defaults, args.route_label), labels_with_supplied_extras(checkpoint_defaults, args.checkpoint_label)


def phase_timeline_labels(args: argparse.Namespace) -> list[str]:
    defaults = ["intake", "scope", "build", "review", "validate", "publish"]
    return labels_with_supplied_extras(defaults, args.phase_label)


def metric_dashboard_labels(args: argparse.Namespace) -> tuple[list[str], list[str]]:
    metric_defaults = ["north star", "input rate", "output rate", "quality", "risk"]
    threshold_defaults = ["healthy band", "warning line", "action line"]
    return labels_with_supplied_extras(metric_defaults, args.metric_label), labels_with_supplied_extras(threshold_defaults, args.threshold_label)


def dependency_map_labels(args: argparse.Namespace) -> tuple[list[str], list[str]]:
    dependency_defaults = [
        "source feed",
        "identity",
        "normalizer",
        "policy check",
        "data contract",
        "integration",
        "release gate",
        "fallback path",
    ]
    cluster_defaults = ["sources", "integration layer", "release boundary"]
    return labels_with_supplied_extras(dependency_defaults, args.dependency_label), labels_with_supplied_extras(cluster_defaults, args.cluster_label)


def sequence_trace_labels(args: argparse.Namespace) -> list[str]:
    defaults = [
        "client request",
        "edge gateway",
        "auth span",
        "inventory span",
        "payment span",
        "database",
        "fallback cache",
        "response",
    ]
    return labels_with_supplied_extras(defaults, args.trace_label)


def sankey_flow_labels(args: argparse.Namespace) -> list[str]:
    defaults = [
        "raw input",
        "accepted stream",
        "filtered loss",
        "transform A",
        "transform B",
        "merged value",
        "bottleneck",
        "final output",
    ]
    return labels_with_supplied_extras(defaults, args.flow_label)


def swimlane_handoff_labels(args: argparse.Namespace) -> tuple[list[str], list[str]]:
    lane_defaults = ["requester", "intake", "review", "delivery"]
    handoff_defaults = [
        "request",
        "triage",
        "analysis",
        "approval",
        "rework",
        "escalation",
        "release",
        "complete",
    ]
    return labels_with_supplied_extras(lane_defaults, args.lane_label), labels_with_supplied_extras(handoff_defaults, args.handoff_label)


def risk_bowtie_labels(args: argparse.Namespace) -> tuple[list[str], list[str], list[str]]:
    threat_defaults = ["threat A", "threat B", "threat C", "threat D"]
    barrier_defaults = [
        "detect",
        "validate",
        "isolate",
        "contain",
        "recover",
        "learn",
    ]
    consequence_defaults = ["impact A", "impact B", "impact C", "impact D"]
    return (
        labels_with_supplied_extras(threat_defaults, args.threat_label),
        labels_with_supplied_extras(barrier_defaults, args.barrier_label),
        labels_with_supplied_extras(consequence_defaults, args.consequence_label),
    )


def scenario_tree_labels(args: argparse.Namespace) -> tuple[list[str], list[str]]:
    scenario_defaults = [
        "decision point",
        "base case",
        "upside branch",
        "downside branch",
        "steady outcome",
        "growth outcome",
        "fallback outcome",
    ]
    probability_defaults = ["likely", "upside", "downside", "fallback"]
    return labels_with_supplied_extras(scenario_defaults, args.scenario_label), labels_with_supplied_extras(probability_defaults, args.probability_label)


def evidence_ladder_labels(args: argparse.Namespace) -> tuple[list[str], list[str]]:
    claim_defaults = [
        "working claim",
        "baseline reading",
        "counterclaim",
        "recommendation",
    ]
    evidence_defaults = [
        "source A",
        "source B",
        "data check",
        "expert review",
        "counterevidence",
        "source gap",
    ]
    return labels_with_supplied_extras(claim_defaults, args.claim_label), labels_with_supplied_extras(evidence_defaults, args.evidence_label)


def layered_architecture_labels(args: argparse.Namespace) -> tuple[list[str], list[str]]:
    layer_defaults = [
        "client",
        "edge/API",
        "application",
        "domain service",
        "data layer",
        "platform",
    ]
    concern_defaults = ["security policy", "failure route", "observability", "rollout gate"]
    return labels_with_supplied_extras(layer_defaults, args.layer_label), labels_with_supplied_extras(concern_defaults, args.concern_label)


def data_lineage_labels(args: argparse.Namespace) -> tuple[list[str], list[str]]:
    lineage_defaults = [
        "raw source",
        "ingest stream",
        "bronze table",
        "silver transform",
        "feature view",
        "consumer surface",
    ]
    quality_defaults = ["schema check", "freshness window", "drift alert", "rollback plan"]
    return labels_with_supplied_extras(lineage_defaults, args.lineage_label), labels_with_supplied_extras(quality_defaults, args.quality_label)


def selected_pattern(args: argparse.Namespace) -> str:
    if args.pattern != "auto":
        return args.pattern
    searchable = " ".join(
        [
            args.title,
            args.topic,
            " ".join(args.fact or []),
            " ".join(args.anchor or []),
        ]
    ).lower()
    skill_tree_route_terms = ("skill-tree-route", "skill tree route", "passive route", "passive tree route", "build route", "tree route", "pathing", "travel nodes", "respec checkpoint", "route planner", "route map")
    if any(term in searchable for term in skill_tree_route_terms):
        return "skill-tree-route"
    skill_tree_terms = ("path of exile", "skill tree", "passive tree", "atlas", "keystone")
    if any(term in searchable for term in skill_tree_terms):
        return "skill-tree"
    harness_terms = (
        "what is a harness",
        "harness shell",
        "runtime wrapper",
        "runtime stack",
        "model picker",
        "engine icon",
        "vehicle dashboard",
        "same model",
        "different shells",
        "comparison_grid",
        "credit_meter",
    )
    if any(term in searchable for term in harness_terms):
        return "systems-flow"
    guardrail_terms = ("guardrail", "shield_gate", "model armor", "input / output / action", "risk_score", "human approval", "policy matrix")
    if any(term in searchable for term in guardrail_terms):
        return "risk-bowtie"
    state_machine_terms = ("state machine", "state-machine", "lifecycle", "workflow state", "guard", "rollback", "compensation", "terminal state")
    if any(term in searchable for term in state_machine_terms):
        return "state-machine"
    evidence_terms = ("evidence ladder", "evidence-ladder", "evidence hierarchy", "research evidence", "source confidence", "confidence ladder", "counterevidence", "claim support", "source gap", "recommendation confidence")
    if any(term in searchable for term in evidence_terms):
        return "evidence-ladder"
    comparison_terms = ("comparison", "compare", "versus", "vs.", "vs ", "tradeoff", "decision matrix", "scorecard", "criteria", "recommendation", "choose between")
    if any(term in searchable for term in comparison_terms):
        return "comparison-matrix"
    causal_terms = ("causal loop", "causal-loop", "feedback loop", "reinforcing loop", "balancing loop", "delayed effect", "side effect", "intervention", "root cause", "cause and effect")
    if any(term in searchable for term in causal_terms):
        return "causal-loop"
    timeline_terms = ("phase timeline", "phase-timeline", "timeline", "milestone", "roadmap", "release plan", "incident timeline", "chronology")
    if any(term in searchable for term in timeline_terms):
        return "phase-timeline"
    metric_terms = ("metric dashboard", "metric-dashboard", "kpi", "slo", "service level", "threshold", "trend", "forecast", "anomaly", "burn rate", "error budget")
    if any(term in searchable for term in metric_terms):
        return "metric-dashboard"
    layered_terms = ("layered architecture", "layered-architecture", "architecture layer", "layer stack", "system layers", "cross-cutting concern", "observability layer", "rollout gate", "platform layer")
    if any(term in searchable for term in layered_terms):
        return "layered-architecture"
    data_lineage_terms = ("data lineage", "data-lineage", "lineage graph", "lineage map", "data pipeline", "etl", "elt", "source to consumer", "source-to-consumer", "quality gate", "schema check", "freshness window", "drift monitor", "drift alert")
    if any(term in searchable for term in data_lineage_terms):
        return "data-lineage"
    trace_terms = ("sequence trace", "sequence-trace", "distributed trace", "request trace", "trace span", "span waterfall", "latency budget", "critical path", "service call")
    if any(term in searchable for term in trace_terms):
        return "sequence-trace"
    sankey_terms = ("sankey", "sankey-flow", "sankey flow", "flow split", "flow merge", "conversion flow", "conversion funnel", "dropoff", "drop-off", "value stream", "loss stream")
    if any(term in searchable for term in sankey_terms):
        return "sankey-flow"
    swimlane_terms = ("swimlane", "swimlane-handoff", "handoff", "handoff map", "handoff workflow", "process handoff", "sla", "rework loop", "escalation", "approval lane", "role lane")
    if any(term in searchable for term in swimlane_terms):
        return "swimlane-handoff"
    bowtie_terms = ("risk bowtie", "risk-bowtie", "bowtie", "bow-tie", "barrier analysis", "hazard", "top event", "preventive barrier", "mitigative barrier", "degraded barrier", "risk control")
    if any(term in searchable for term in bowtie_terms):
        return "risk-bowtie"
    scenario_terms = ("scenario tree", "scenario-tree", "decision tree", "branching scenario", "probability branch", "scenario branch", "expected value", "upside scenario", "downside scenario", "fallback scenario")
    if any(term in searchable for term in scenario_terms):
        return "scenario-tree"
    dependency_terms = ("dependency map", "dependency-map", "dependency graph", "dependency", "dag", "blocked by", "bottleneck", "cutover", "fallback path", "migration dependency")
    if any(term in searchable for term in dependency_terms):
        return "dependency-map"
    return "systems-flow"


def load_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        Path("C:/Windows/Fonts/segoeuib.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf"),
        Path("C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf"),
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
    ]
    for candidate in candidates:
        if candidate.exists():
            return ImageFont.truetype(str(candidate), size)
    return ImageFont.load_default()


def text(
    draw: ImageDraw.ImageDraw,
    xy: tuple[float, float],
    value: str,
    font: ImageFont.ImageFont,
    fill: str = PALETTE["ink"],
    anchor: str = "mm",
    stroke_width: int = 0,
    stroke_fill: str | None = None,
) -> None:
    draw.text(
        xy,
        value,
        font=font,
        fill=hex_to_rgb(fill),
        anchor=anchor,
        stroke_width=stroke_width,
        stroke_fill=hex_to_rgb(stroke_fill) if stroke_fill else None,
    )


def rounded_rect(
    draw: ImageDraw.ImageDraw,
    box: tuple[float, float, float, float],
    fill: str,
    outline: str | None = None,
    width: int = 2,
    radius: int = 10,
) -> None:
    if EDGE_STYLE == "square":
        box = snap_box_to_grid(box)
        radius = 0
    fill = tonal_surface_fill(fill, box)
    draw.rounded_rectangle(
        box,
        radius=radius,
        fill=hex_to_rgb(fill),
        outline=hex_to_rgb(outline) if outline else None,
        width=width,
    )


def draw_metro_megacanvas_base(draw: ImageDraw.ImageDraw, active_index: int = 0) -> None:
    zone_levels = [1, 2, 3, 4, 2]
    active = max(0, min(len(METRO_ZONE_BOUNDS) - 1, active_index))
    for index, bounds in enumerate(METRO_ZONE_BOUNDS):
        level = zone_levels[index % len(zone_levels)] + (1 if index == active else 0)
        rounded_rect(
            draw,
            (
                bounds["x"],
                bounds["y"],
                bounds["x"] + bounds["width"],
                bounds["y"] + bounds["height"],
            ),
            gray_level(min(level, len(GRAY_LEVELS) - 2)),
            None,
            radius=0,
        )
    rounded_rect(draw, (44, 604, 1236, 636), gray_level(5), None, radius=0)
    rounded_rect(draw, (348, 96, 360, 604), gray_level(5), None, radius=0)
    rounded_rect(draw, (868, 96, 880, 604), gray_level(5), None, radius=0)


def node_positions(width: int, height: int) -> dict[str, tuple[int, int]]:
    scale_x = width / 1280
    scale_y = height / 720

    def pt(x: int, y: int) -> tuple[int, int]:
        return round(x * scale_x), round(y * scale_y)

    return {
        "start": pt(145, 360),
        "a1": pt(255, 335),
        "a2": pt(360, 300),
        "damage": pt(500, 245),
        "defense": pt(500, 430),
        "attr1": pt(655, 330),
        "attr2": pt(790, 330),
        "keystone": pt(920, 330),
        "atlas1": pt(1060, 250),
        "atlas2": pt(1150, 340),
        "atlas3": pt(1060, 430),
    }


def draw_polyline(
    draw: ImageDraw.ImageDraw,
    points: list[tuple[int, int]],
    color: str,
    width: int,
    progress: float,
) -> None:
    if len(points) < 2 or progress <= 0:
        return
    progress = clamp(progress)
    lengths = []
    total = 0.0
    for a, b in zip(points, points[1:]):
        length = math.dist(a, b)
        lengths.append(length)
        total += length
    remaining = total * progress
    for idx, (a, b) in enumerate(zip(points, points[1:])):
        length = lengths[idx]
        if remaining <= 0:
            break
        if remaining >= length:
            draw.line([a, b], fill=hex_to_rgb(color), width=width)
        else:
            ratio = remaining / length
            end = (round(a[0] + (b[0] - a[0]) * ratio), round(a[1] + (b[1] - a[1]) * ratio))
            draw.line([a, end], fill=hex_to_rgb(color), width=width)
        remaining -= length


def draw_node(
    draw: ImageDraw.ImageDraw,
    xy: tuple[int, int],
    label: str,
    color: str,
    active: float,
    fonts: dict[str, ImageFont.ImageFont],
    shape: str = "circle",
    ghost_label: bool = False,
) -> None:
    x, y = xy
    active = clamp(active)
    radius = round(18 + 8 * active)
    fill = "#ffffff"
    outline = color if active > 0.08 else PALETTE["line"]
    if shape == "diamond":
        pts = [(x, y - radius - 8), (x + radius + 8, y), (x, y + radius + 8), (x - radius - 8, y)]
        draw.polygon(pts, fill=hex_to_rgb(fill), outline=hex_to_rgb(outline))
        if active > 0.2:
            draw.line([pts[0], pts[1], pts[2], pts[3], pts[0]], fill=hex_to_rgb(color), width=4)
    else:
        draw.ellipse(
            (x - radius, y - radius, x + radius, y + radius),
            fill=hex_to_rgb(fill),
            outline=hex_to_rgb(outline),
            width=4 if active > 0.08 else 2,
        )
    if active > 0.12:
        text(draw, (x, y + radius + 20), label, fonts.get("label", fonts["small"]), PALETTE["ink"], "mm", 3, "#ffffff")
    elif ghost_label:
        text(draw, (x, y + radius + 20), label, fonts.get("label", fonts["small"]), PALETTE["muted"], "mm", 3, "#ffffff")


def draw_meter(
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    label: str,
    progress: float,
    color: str,
    fonts: dict[str, ImageFont.ImageFont],
) -> None:
    x1, y1, x2, y2 = box
    rounded_rect(draw, box, gray_level(3), PALETTE["line"], radius=8)
    fill_width = (x2 - x1) * clamp(progress)
    if fill_width > 4:
        rounded_rect(draw, (x1, y1, x1 + fill_width, y2), gray_level(5), None, radius=0)
        cap_width = min(8, fill_width)
        draw.rectangle((x1 + fill_width - cap_width, y1, x1 + fill_width, y2), fill=hex_to_rgb(color))
    text(draw, ((x1 + x2) / 2, (y1 + y2) / 2 + 5), label, fonts["small"], PALETTE["ink"], "mm", 2, "#ffffff")


def render_skill_tree_frame(
    second: float,
    args: argparse.Namespace,
    fonts: dict[str, ImageFont.ImageFont],
) -> Image.Image:
    width, height = args.width, args.height
    img = Image.new("RGB", (width, height), hex_to_rgb(PALETTE["paper"]))
    draw = ImageDraw.Draw(img)
    p = second / args.duration
    pos = node_positions(width, height)
    node_labels, meter_labels = skill_tree_labels(args)

    # Header and stable source note.

    # Concept bands.
    rounded_rect(draw, (60, 115, 990, 610), "#ffffff", "#cfcfcf", radius=14)
    rounded_rect(draw, (1015, 115, 1218, 610), "#e7e7e7", "#9c9c9c", radius=14)
    text(draw, (1050, 146), "ATLAS LAYER", fonts["small"], PALETTE["atlas"], "lm")
    text(draw, (88, 146), "CHARACTER TREE", fonts["small"], PALETTE["muted"], "lm")

    # Base network.
    base_edges = [
        ("start", "a1"),
        ("a1", "a2"),
        ("a2", "damage"),
        ("a2", "defense"),
        ("a2", "attr1"),
        ("attr1", "attr2"),
        ("attr2", "keystone"),
        ("atlas1", "atlas2"),
        ("atlas2", "atlas3"),
    ]
    for a, b in base_edges:
        draw.line([pos[a], pos[b]], fill=hex_to_rgb(PALETTE["line"]), width=3)

    # Attribute highway.
    highway_y = pos["attr1"][1]
    for x in range(pos["attr1"][0] - 80, pos["attr2"][0] + 82, 24):
        draw.line([(x, highway_y + 48), (x + 10, highway_y + 48)], fill=hex_to_rgb(PALETTE["attribute"]), width=3)
    text(draw, (pos["attr1"][0] + 70, highway_y + 76), "attribute highway", fonts.get("label", fonts["small"]), PALETTE["attribute"], "mm", 3, "#ffffff")

    route_points = [pos["start"], pos["a1"], pos["a2"], pos["attr1"], pos["attr2"], pos["keystone"]]
    draw_polyline(draw, route_points, PALETTE["route"], 8, ease((p - 0.04) / 0.28))
    draw_polyline(draw, [pos["a2"], pos["damage"]], PALETTE["damage"], 7, ease((p - 0.24) / 0.18))
    draw_polyline(draw, [pos["a2"], pos["defense"]], PALETTE["defense"], 7, ease((p - 0.34) / 0.18))
    draw_polyline(draw, [pos["atlas1"], pos["atlas2"], pos["atlas3"]], PALETTE["atlas"], 7, ease((p - 0.78) / 0.16))

    # Nodes and activation timing.
    activations = {
        "start": ease((p - 0.02) / 0.08),
        "a1": ease((p - 0.10) / 0.08),
        "a2": ease((p - 0.18) / 0.08),
        "damage": ease((p - 0.30) / 0.10),
        "defense": ease((p - 0.40) / 0.10),
        "attr1": ease((p - 0.48) / 0.08),
        "attr2": ease((p - 0.54) / 0.08),
        "keystone": ease((p - 0.62) / 0.10),
        "atlas1": ease((p - 0.78) / 0.08),
        "atlas2": ease((p - 0.84) / 0.08),
        "atlas3": ease((p - 0.90) / 0.08),
    }
    labels = {
        "start": compact_label(node_labels[0], 12),
        "a1": compact_label(node_labels[1], 12),
        "a2": compact_label(node_labels[2], 12),
        "damage": compact_label(node_labels[3], 12),
        "defense": compact_label(node_labels[4], 12),
        "attr1": compact_label(node_labels[5], 12),
        "attr2": compact_label(node_labels[6], 12),
        "keystone": compact_label(node_labels[7], 12),
        "atlas1": compact_label(node_labels[8], 12),
        "atlas2": compact_label(node_labels[9], 12),
        "atlas3": compact_label(node_labels[10], 12),
    }
    colors = {
        "start": PALETTE["route"],
        "a1": PALETTE["route"],
        "a2": PALETTE["route"],
        "damage": PALETTE["damage"],
        "defense": PALETTE["defense"],
        "attr1": PALETTE["attribute"],
        "attr2": PALETTE["attribute"],
        "keystone": PALETTE["tradeoff"],
        "atlas1": PALETTE["atlas"],
        "atlas2": PALETTE["atlas"],
        "atlas3": PALETTE["atlas"],
    }
    for key in labels:
        draw_node(
            draw,
            pos[key],
            labels[key],
            colors[key],
            activations[key],
            fonts,
            "diamond" if key == "keystone" else "circle",
        )

    # Moving skill token.
    token_progress = ease((p - 0.02) / 0.30)
    route_len = len(route_points) - 1
    segment_float = token_progress * route_len
    segment = min(route_len - 1, int(segment_float))
    local = segment_float - segment
    a = route_points[segment]
    b = route_points[segment + 1]
    tx = round(a[0] + (b[0] - a[0]) * local)
    ty = round(a[1] + (b[1] - a[1]) * local)
    draw.ellipse((tx - 10, ty - 10, tx + 10, ty + 10), fill=hex_to_rgb(PALETTE["gold"]))
    if p < 0.38:
        text(draw, (tx, ty - 28), "skill first", fonts.get("label", fonts["small"]), PALETTE["gold"], "mm", 3, "#ffffff")

    # Meters and tradeoff panel.
    draw_meter(draw, (120, 520, 360, 585), compact_label(meter_labels[0], 17), ease((p - 0.30) / 0.20), PALETTE["damage"], fonts)
    draw_meter(draw, (390, 520, 630, 585), compact_label(meter_labels[1], 17), ease((p - 0.42) / 0.20), PALETTE["defense"], fonts)
    draw_meter(draw, (660, 520, 900, 585), compact_label(meter_labels[2], 17), ease((p - 0.52) / 0.20), PALETTE["attribute"], fonts)

    trade_alpha = ease((p - 0.62) / 0.12)
    if trade_alpha > 0.05:
        rounded_rect(draw, (800, 175, 960, 235), "#ffccd5", PALETTE["tradeoff"], radius=10)
        text(draw, (880, 197), "KEYSTONE", fonts["small"], PALETTE["tradeoff"], "mm")
        text(draw, (880, 219), "power + cost", fonts["small"], PALETTE["ink"], "mm")

    # Atlas layer separation.
    if p > 0.76:
        text(draw, (1118, 520), "separate late-game tree", fonts.get("label", fonts["small"]), PALETTE["atlas"], "mm", 3, "#e7e7e7")
        text(draw, (1118, 548), "do not mix with build path", fonts["small"], PALETTE["muted"], "mm", 2, "#e7e7e7")

    # Footer beat.
    beats = [
        (0.00, "Pick the active skill and playstyle first."),
        (0.28, "Spend passives where they support damage and survival."),
        (0.52, "Use attribute travel only when it unlocks gear or gems."),
        (0.70, "Treat keystones as tradeoffs, not free power."),
        (0.84, "Keep Atlas passives as a separate endgame layer."),
    ]
    current = beats[0][1]
    for threshold, beat in beats:
        if p >= threshold:
            current = beat

    return img


def draw_packet(
    draw: ImageDraw.ImageDraw,
    xy: tuple[float, float],
    color: str,
    active: float,
    label: str,
    fonts: dict[str, ImageFont.ImageFont],
) -> None:
    if active <= 0:
        return
    x, y = xy
    radius = 12 + 4 * clamp(active)
    draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=hex_to_rgb(color))
    if active > 0.35 and label:
        text(draw, (x, y - 26), label, fonts.get("tiny", fonts["small"]), color, "mm")


def point_on_polyline(points: list[tuple[float, float]], progress: float) -> tuple[float, float]:
    progress = clamp(progress)
    if len(points) == 1:
        return points[0]
    lengths: list[float] = []
    total = 0.0
    for start, end in zip(points, points[1:]):
        length = math.dist(start, end)
        lengths.append(length)
        total += length
    if total <= 0:
        return points[-1]
    target = total * progress
    for idx, (start, end) in enumerate(zip(points, points[1:])):
        length = lengths[idx]
        if target <= length:
            local = 0 if length == 0 else target / length
            return (
                start[0] + (end[0] - start[0]) * local,
                start[1] + (end[1] - start[1]) * local,
            )
        target -= length
    return points[-1]


def draw_masonry_megacanvas_base(
    draw: ImageDraw.ImageDraw,
    second: float,
    args: argparse.Namespace,
) -> None:
    width, height = args.width, args.height
    sx = width / 1280
    sy = height / 720

    def box(x1: float, y1: float, x2: float, y2: float) -> tuple[int, int, int, int]:
        return round(x1 * sx), round(y1 * sy), round(x2 * sx), round(y2 * sy)

    p = second / args.duration
    rounded_rect(draw, box(48, 668, 1552, 700), gray_level(5), None, radius=0)
    for spine_x in (448, 848, 1192):
        rounded_rect(draw, box(spine_x, 88, spine_x + 12, 668), gray_level(5), None, radius=0)
    active_zone = max(0, min(4, int(clamp(p) * 5)))
    reveal_start = min(9.0, float(len(MASONRY_MODULE_BOUNDS)))
    reveal_amount = reveal_start + clamp(p) * (len(MASONRY_MODULE_BOUNDS) - reveal_start)
    entry_vectors = [(-96, 0), (0, -80), (112, 0), (0, 96)]
    for index, module in enumerate(MASONRY_MODULE_BOUNDS):
        phase = reveal_amount - index
        if phase <= 0.05:
            continue
        fit = ease(phase)
        offset_x, offset_y = entry_vectors[index % len(entry_vectors)]
        x = float(module["x"]) + offset_x * (1 - fit)
        y = float(module["y"]) + offset_y * (1 - fit)
        level = int(module.get("grayLevel", 2))
        zone_index = int(module.get("zoneIndex", index % 5))
        fill_level = min(len(GRAY_LEVELS) - 2, level + (1 if zone_index == active_zone else 0))
        rounded_rect(
            draw,
            box(x, y, x + float(module["width"]), y + float(module["height"])),
            gray_level(fill_level),
            PALETTE["route"] if zone_index == active_zone else gray_level(5),
            width=3 if zone_index == active_zone else 1,
            radius=0,
        )
    flow_offset = clamp(p) * 420
    for index in range(32):
        x = 64 + ((index * 96 + flow_offset) % 1432)
        y = 636 + (index % 2) * 18
        fill = gray_level(5 if index % 5 == active_zone else 3 + (index % 2))
        rounded_rect(draw, box(x, y, x + 52, y + 14), fill, None, radius=0)
        if index % 11 == active_zone:
            rounded_rect(draw, box(x, y, x + 8, y + 14), PALETTE["route"], None, radius=0)
    for spine_index, spine_x in enumerate((448, 848, 1192)):
        for tick in range(4):
            y = 112 + ((tick * 132 + flow_offset + spine_index * 48) % 520)
            fill = gray_level(5 if tick == active_zone % 4 else 3)
            rounded_rect(draw, box(spine_x - 4, y, spine_x + 20, y + 32), fill, None, radius=0)
    scan_x = 48 + ((clamp(p) * 1504) % 1504)
    rounded_rect(draw, box(scan_x, 88, scan_x + 72, 668), gray_level(0), None, radius=0)
    for stripe in range(0, 72, 16):
        rounded_rect(draw, box(scan_x + stripe, 88, scan_x + stripe + 8, 668), gray_level(5 if stripe % 32 == 0 else 3), None, radius=0)
    for segment in range(12):
        y = 104 + segment * 44
        rounded_rect(draw, box(scan_x + 12, y, scan_x + 60, y + 12), gray_level(5 if segment % 3 == active_zone % 3 else 2), None, radius=0)


MASONRY_GENERIC_RENDER_PATTERNS = {
    "metric-dashboard",
    "sankey-flow",
    "skill-tree",
    "skill-tree-route",
    "state-machine",
    "comparison-matrix",
    "causal-loop",
    "phase-timeline",
    "dependency-map",
    "sequence-trace",
    "swimlane-handoff",
    "risk-bowtie",
    "scenario-tree",
    "evidence-ladder",
    "layered-architecture",
    "data-lineage",
}


def probability_evaluation_requested(args: argparse.Namespace) -> bool:
    haystack = " ".join(
        str(value)
        for value in [
            getattr(args, "title", ""),
            getattr(args, "topic", ""),
            *(getattr(args, "anchor", None) or []),
            *(getattr(args, "fact", None) or []),
        ]
    ).lower()
    exact_signals = [
        "probability_bars",
        "passn_grid",
        "pass@n",
        "pass at n",
        "test_runner",
        "judge model",
        "rubric",
        "log probability",
        "logprobs",
        "logit bias",
    ]
    signal_count = sum(1 for signal in exact_signals if signal in haystack)
    return signal_count >= 2 or ("probabilit" in haystack and "evaluation" in haystack)


def agent_loop_requested(args: argparse.Namespace) -> bool:
    haystack = " ".join(
        str(value)
        for value in [
            getattr(args, "title", ""),
            getattr(args, "topic", ""),
            *(getattr(args, "anchor", None) or []),
            *(getattr(args, "fact", None) or []),
            *(getattr(args, "system_label", None) or []),
        ]
    ).lower()
    exact_signals = [
        "agent_loop_ring",
        "context_window_box",
        "model + tools + state + loop",
        "fixed workflow",
        "adaptive agent",
        "approval checkpoint",
        "environment changes",
        "context panes",
    ]
    signal_count = sum(1 for signal in exact_signals if signal in haystack)
    return signal_count >= 2 or ("what is an agent" in haystack and "loop" in haystack)


def skill_package_requested(args: argparse.Namespace) -> bool:
    values = [
        getattr(args, "title", ""),
        getattr(args, "topic", ""),
        *(getattr(args, "anchor", None) or []),
        *(getattr(args, "fact", None) or []),
        *(getattr(args, "system_label", None) or []),
    ]
    haystack = " ".join(str(value) for value in values).lower()
    if "skill tree" in haystack or "skill-tree" in haystack or "path of exile" in haystack:
        return False
    exact_signals = [
        "what is a skill",
        "skill_card_stack",
        "skill.md",
        "progressive disclosure",
        "long prompt wall",
        "cost meter",
        "cost line",
        "tool badges",
        "script",
        "bloated",
        "mini novels",
        "deploy-preview",
        "reusable workflow",
        "on-demand reusable workflow",
    ]
    signal_count = sum(1 for signal in exact_signals if signal in haystack)
    return signal_count >= 2 or "what is a skill" in haystack


def guardrail_requested(args: argparse.Namespace) -> bool:
    haystack = " ".join(
        str(value)
        for value in [
            getattr(args, "title", ""),
            getattr(args, "topic", ""),
            *(getattr(args, "anchor", None) or []),
            *(getattr(args, "fact", None) or []),
            *(getattr(args, "threat_label", None) or []),
            *(getattr(args, "barrier_label", None) or []),
            *(getattr(args, "consequence_label", None) or []),
        ]
    ).lower()
    if skill_package_requested(args):
        return False
    exact_signals = [
        "shield_gate",
        "agent_loop_ring",
        "input / output / action",
        "input gate",
        "output gate",
        "action gate",
        "prompt bubble",
        "hard gate",
        "model armor",
        "risk_score",
        "human approval",
        "policy matrix",
        "secret",
        "destructive command",
        "deploy",
        "block",
        "redact",
        "route",
        "escalate",
    ]
    signal_count = sum(1 for signal in exact_signals if signal in haystack)
    return signal_count >= 2 or "what is a guardrail" in haystack or ("guardrail" in haystack and "policy" in haystack)


def harness_requested(args: argparse.Namespace) -> bool:
    values = [
        getattr(args, "title", ""),
        getattr(args, "topic", ""),
        *(getattr(args, "anchor", None) or []),
        *(getattr(args, "fact", None) or []),
        *(getattr(args, "system_label", None) or []),
    ]
    haystack = " ".join(str(value) for value in values).lower()
    title_topic = " ".join(str(value) for value in [getattr(args, "title", ""), getattr(args, "topic", "")]).lower()
    if skill_package_requested(args):
        return False
    if "harness hook" in title_topic or "harness plugin" in title_topic:
        return False
    exact_signals = [
        "comparison_grid",
        "runtime stack",
        "runtime wrapper",
        "instruction layers",
        "default tools",
        "permissions",
        "model picker",
        "execution loop",
        "approvals",
        "memory behavior",
        "logging",
        "engine icon",
        "vehicle dashboard",
        "same model",
        "different shells",
        "three-column harness",
        "github copilot",
        "claude code",
        "opencode",
        "credit_meter",
        "feature grid",
        "use-case matrix",
        "selection path",
    ]
    signal_count = sum(1 for signal in exact_signals if signal in haystack)
    plain_harness = "what is a harness" in title_topic and "hook" not in title_topic and "plugin" not in title_topic
    return signal_count >= 2 or plain_harness


def plugin_requested(args: argparse.Namespace) -> bool:
    values = [
        getattr(args, "title", ""),
        getattr(args, "topic", ""),
        *(getattr(args, "anchor", None) or []),
        *(getattr(args, "fact", None) or []),
        *(getattr(args, "lane_label", None) or []),
        *(getattr(args, "handoff_label", None) or []),
    ]
    haystack = " ".join(str(value) for value in values).lower()
    exact_signals = [
        "harness plugin",
        "plugin_bundle_cube",
        "packaged harness behavior",
        "distribution mechanism",
        "installable unit",
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
    signal_count = sum(1 for signal in exact_signals if signal in haystack)
    return signal_count >= 2 or "what is a harness plugin" in haystack


def ai_alternatives_requested(args: argparse.Namespace) -> bool:
    values = [
        getattr(args, "title", ""),
        getattr(args, "topic", ""),
        *(getattr(args, "anchor", None) or []),
        *(getattr(args, "fact", None) or []),
        *(getattr(args, "lane_label", None) or []),
        *(getattr(args, "handoff_label", None) or []),
        *(getattr(args, "system_label", None) or []),
    ]
    haystack = " ".join(str(value) for value in values).lower()
    title_topic = " ".join(str(value) for value in [getattr(args, "title", ""), getattr(args, "topic", "")]).lower()
    if "harness plugin" in title_topic:
        return False
    if "what ai alternatives we have" in haystack or "ai alternatives" in haystack:
        return True
    exact_signals = [
        "atlassian rovo",
        "gemini app",
        "github copilot",
        "claude desktop",
        "claude code",
    ]
    ai_specific_signals = [
        "atlassian rovo",
        "gemini app",
        "claude desktop",
        "workflow gravity",
        "home base",
        "radar chart",
        "use-case selector",
    ]
    return (
        sum(1 for signal in exact_signals if signal in haystack) >= 2
        and sum(1 for signal in ai_specific_signals if signal in haystack) >= 2
    )


def hook_requested(args: argparse.Namespace) -> bool:
    values = [
        getattr(args, "title", ""),
        getattr(args, "topic", ""),
        *(getattr(args, "anchor", None) or []),
        *(getattr(args, "fact", None) or []),
        *(getattr(args, "system_label", None) or []),
    ]
    haystack = " ".join(str(value) for value in values).lower()
    title_topic = " ".join(str(value) for value in [getattr(args, "title", ""), getattr(args, "topic", "")]).lower()
    if skill_package_requested(args):
        return False
    if "what is an agent" in title_topic:
        return False
    if "harness plugin" in haystack:
        return False
    exact_signals = [
        "harness hook",
        "event_timeline",
        "lifecycle events",
        "lifecycle boundaries",
        "shield_gate",
        "pretooluse",
        "before tool use",
        "after tool use",
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
        "token-savings",
        "token savings",
        "speed-vs-cost",
        "cost slider",
        "hooks = lifecycle controls",
    ]
    signal_count = sum(1 for signal in exact_signals if signal in haystack)
    return signal_count >= 2 or "what is a harness hook" in haystack


def hook_anchor_groups(values: list[str]) -> list[list[str]]:
    groups: list[list[str]] = [[] for _ in range(5)]
    fallback_index = 0
    for value in values:
        text_value = str(value).lower()
        if "event_timeline" in text_value or "lifecycle" in text_value or "session" in text_value or "prompt submit" in text_value or "tool call" in text_value or "stop" in text_value or "event node" in text_value:
            groups[0].append(value)
        elif "shield_gate" in text_value or "guardrail" in text_value or "policy" in text_value or "pretooluse" in text_value or "before tool" in text_value or "bash" in text_value or "rm -rf" in text_value or "kubectl delete" in text_value or "terraform destroy" in text_value or "deny" in text_value:
            groups[1].append(value)
        elif "github" in text_value or "claude" in text_value or "opencode" in text_value or "shell command" in text_value or "http endpoint" in text_value or "llm prompt" in text_value or "plugin event" in text_value:
            groups[2].append(value)
        elif "formatting" in text_value or "validation" in text_value or "secret" in text_value or "audit logging" in text_value or "notification" in text_value or "filter" in text_value or "preprocess" in text_value or "narrowing" in text_value or "context" in text_value:
            groups[3].append(value)
        elif "cost" in text_value or "latency" in text_value or "delay" in text_value or "token" in text_value or "speed" in text_value or "lifecycle controls" in text_value or "hooks =" in text_value:
            groups[4].append(value)
        else:
            groups[fallback_index % len(groups)].append(value)
            fallback_index += 1
    return groups


def render_generic_masonry_frame(
    second: float,
    args: argparse.Namespace,
    fonts: dict[str, ImageFont.ImageFont],
    pattern: str,
) -> Image.Image:
    width, height = args.width, args.height
    sx = width / 1280
    sy = height / 720

    def pt(x: float, y: float) -> tuple[int, int]:
        return round(x * sx), round(y * sy)

    def box(x1: float, y1: float, x2: float, y2: float) -> tuple[int, int, int, int]:
        return round(x1 * sx), round(y1 * sy), round(x2 * sx), round(y2 * sy)

    canvas_width = round(width * 1.5)
    img = Image.new("RGB", (canvas_width, height), hex_to_rgb(PALETTE["paper"]))
    draw = ImageDraw.Draw(img)
    p = clamp(second / max(args.duration, 0.001))
    draw_masonry_megacanvas_base(draw, second, args)

    pattern_index = [
        "metric-dashboard",
        "sankey-flow",
        "skill-tree",
        "skill-tree-route",
        "state-machine",
        "comparison-matrix",
        "causal-loop",
        "phase-timeline",
        "dependency-map",
        "sequence-trace",
        "swimlane-handoff",
        "risk-bowtie",
        "scenario-tree",
        "evidence-ladder",
        "layered-architecture",
        "data-lineage",
    ].index(pattern) if pattern in MASONRY_GENERIC_RENDER_PATTERNS else 0
    active_step = min(7, int(ease((p - 0.06) / 0.72) * 8))
    accent_cycle = [PALETTE["route"], PALETTE["damage"], PALETTE["defense"], PALETTE["attribute"], PALETTE["tradeoff"], PALETTE["atlas"]]
    accent = accent_cycle[pattern_index % len(accent_cycle)]
    secondary = accent_cycle[(pattern_index + 2) % len(accent_cycle)]
    alert = accent_cycle[(pattern_index + 3) % len(accent_cycle)]
    motif_text = " ".join(
        str(value)
        for value in [
            getattr(args, "title", ""),
            getattr(args, "topic", ""),
            *(getattr(args, "anchor", None) or []),
            *(getattr(args, "fact", None) or []),
            *(getattr(args, "dependency_label", None) or []),
            *(getattr(args, "system_label", None) or []),
        ]
    ).lower()
    mcp_protocol_requested = any(
        signal in motif_text
        for signal in [
            "what is an mcp",
            "model context protocol",
            "mcp_bus",
            "mcp server",
            "tools / resources / prompts",
            "tools resources prompts",
            "registry",
            "allowlist",
            "client and server",
            "tool surface",
        ]
    )

    def draw_grid_surface(origin_x: int, origin_y: int, columns: int, rows: int, cell: int, active: int) -> None:
        for row in range(rows):
            for col in range(columns):
                level = 1 + ((row * 2 + col + pattern_index) % 5)
                fill = gray_level(level)
                if col + row <= active:
                    fill = accent if (row + col + pattern_index) % 4 == 0 else gray_level(min(level + 1, 6))
                rounded_rect(
                    draw,
                    box(origin_x + col * cell, origin_y + row * cell, origin_x + col * cell + cell - 4, origin_y + row * cell + cell - 4),
                    fill,
                    None,
                    radius=0,
                )

    def draw_bar_stack(origin_x: int, origin_y: int, count: int, active: int) -> None:
        for index in range(count):
            y = origin_y + index * 34
            base_w = 84 + ((index * 29 + pattern_index * 17) % 160)
            progress = ease((p - 0.08 - index * 0.035) / 0.34)
            width_px = 40 + base_w * (0.35 + 0.65 * progress)
            fill = accent if index <= active and index % 3 == 0 else secondary if index <= active else gray_level(3 + index % 3)
            rounded_rect(draw, box(origin_x, y, origin_x + width_px, y + 22), fill, None, radius=0)
            rounded_rect(draw, box(origin_x + width_px + 8, y, origin_x + width_px + 44, y + 22), gray_level(2 + index % 4), None, radius=0)

    def draw_evidence_floor(active: int) -> None:
        for row in range(2):
            for col in range(8):
                x = 104 + col * 52
                y = 536 + row * 48
                index = row * 8 + col
                fill = gray_level(2 + ((index + pattern_index) % 4))
                if index <= active + 5:
                    fill = accent if index % 5 == 0 else gray_level(4 + (index % 2))
                rounded_rect(draw, box(x, y, x + 44, y + 36), fill, None, radius=0)
        for index in range(4):
            x = 584 + index * 116
            height_px = 44 + ((index + pattern_index) % 3) * 24
            active_fill = secondary if index <= max(0, active - 2) else gray_level(3 + index % 3)
            rounded_rect(draw, box(x, 616 - height_px, x + 88, 616), active_fill, None, radius=0)
            rounded_rect(draw, box(x, 624, x + 88, 640), gray_level(4), None, radius=0)
        for index in range(5):
            x = 1072 + (index % 2) * 108
            y = 520 + (index // 2) * 48
            width_px = 76 + (index % 2) * 28
            fill = alert if index <= max(0, active - 3) and index % 2 == 0 else gray_level(2 + index % 4)
            rounded_rect(draw, box(x, y, x + width_px, y + 32), fill, None, radius=0)

    def draw_mcp_protocol_bus(active: int) -> None:
        token_level = max(4, min(16, int(ease((p - 0.04) / 0.34) * 17)))
        matrix_level = max(8, min(40, int(ease((p - 0.12) / 0.48) * 41)))
        stack_level = max(2, min(8, int(ease((p - 0.22) / 0.42) * 9)))
        meter_level = max(1, min(5, int(ease((p - 0.34) / 0.38) * 6)))
        gate_level = max(1, min(4, int(ease((p - 0.48) / 0.32) * 5)))
        evidence_level = max(10, min(60, int(ease((p - 0.08) / 0.72) * 61)))

        surfaces = [
            (80, 104, 292, 260, gray_level(2)),
            (404, 96, 420, 308, gray_level(1)),
            (884, 104, 304, 278, gray_level(3)),
            (1220, 112, 300, 240, gray_level(2)),
            (84, 432, 468, 150, gray_level(1)),
            (604, 456, 468, 128, gray_level(2)),
        ]
        for x, y, w, h, fill in surfaces:
            rounded_rect(draw, box(x, y, x + w, y + h), fill, gray_level(5), width=1, radius=0)

        traces = [
            [(84, 112), (360, 112), (444, 180)],
            [(404, 360), (744, 360), (900, 252)],
            [(948, 132), (1216, 188), (1456, 188)],
            [(104, 612), (552, 612), (760, 548), (1000, 548)],
            [(180, 252), (520, 252), (916, 252), (1432, 252)],
        ]
        for index, points in enumerate(traces):
            draw_polyline(draw, [pt(x, y) for x, y in points], gray_level(5), 2 if index < 4 else 8, 1)

        for index in range(16):
            row = index // 8
            col = index % 8
            active_token = index < token_level
            x = 108 + col * 32
            y = 136 + row * 54
            fill = gray_level(3 + ((index + row) % 6)) if active_token else gray_level(1 + (index % 5))
            rounded_rect(draw, box(x, y, x + 26, y + 38), fill, gray_level(5), width=1, radius=0)
            if active_token and index % 6 == 0:
                rounded_rect(draw, box(x, y, x + 4, y + 38), PALETTE["route"], None, radius=0)
            if active_token and index % 7 == 3:
                rounded_rect(draw, box(x + 22, y, x + 26, y + 38), gray_level(8), None, radius=0)

        for row in range(5):
            for col in range(8):
                index = row * 8 + col
                active_cell = index < matrix_level
                strong = active_cell and (row == col % 5 or (row + col) % 7 == 0)
                fill = gray_level(6) if strong else gray_level(2 + ((row + col) % 7)) if active_cell else gray_level(1)
                rounded_rect(draw, box(428 + col * 48, 122 + row * 42, 468 + col * 48, 154 + row * 42), fill, None, radius=0)
                if strong and (row + col) % 3 == 0:
                    rounded_rect(draw, box(428 + col * 48, 122 + row * 42, 434 + col * 48, 154 + row * 42), PALETTE["attribute"], None, radius=0)

        for layer in range(8):
            y = 128 + layer * 30
            active_layer = layer < stack_level
            layer_width = 228 - layer * 10
            fill = gray_level(5 + (layer % 3)) if active_layer else gray_level(2 + (layer % 5))
            rounded_rect(draw, box(916, y, 916 + layer_width, y + 22), fill, None, radius=0)
            if active_layer and layer % 2 == 0:
                rounded_rect(draw, box(916 + layer_width - 8, y, 916 + layer_width, y + 22), PALETTE["route"], None, radius=0)

        for index in range(4):
            x = 1248 + index * 62
            active_gate = index < gate_level
            rounded_rect(draw, box(x, 142, x + 46, 222), gray_level(6 if active_gate else 2 + index), gray_level(5), width=1, radius=0)
            if active_gate:
                rounded_rect(draw, box(x, 142, x + 8, 222), PALETTE["route"], None, radius=0)
            rounded_rect(draw, box(x, 248, x + 46, 302), gray_level(5 if active_gate and index >= 2 else 2 + ((index + 1) % 5)), gray_level(5), width=1, radius=0)

        for index in range(6):
            x = 524 + index * 72
            fill = gray_level(6 if index < gate_level + 2 else 3 + (index % 4))
            port_y2 = 326
            rounded_rect(draw, box(x, 292, x + 44, port_y2), fill, gray_level(5), width=1, radius=0)
            if index < gate_level + 1:
                rounded_rect(draw, box(x, 292, x + 6, port_y2), PALETTE["attribute"], None, radius=0)

        route_segments = [
            ([(342, 246), (428, 246), (520, 246)], ease((p - 0.08) / 0.20), PALETTE["attribute"], 6),
            ([(780, 246), (916, 216), (1188, 216)], ease((p - 0.32) / 0.22), PALETTE["attribute"], 6),
            ([(1188, 216), (1248, 182), (1488, 182)], ease((p - 0.50) / 0.22), PALETTE["attribute"], 5),
            ([(358, 546), (604, 520), (1032, 520)], ease((p - 0.62) / 0.22), PALETTE["attribute"], 5),
        ]
        for points, progress, color, width_px in route_segments:
            draw_polyline(draw, [pt(x, y) for x, y in points], color, width_px, progress)

        for index in range(5):
            x = 120 + index * 78
            rounded_rect(draw, box(x, 472, x + 58, 546), gray_level(2 + (index % 4)), gray_level(5), width=1, radius=0)
            filled = 74 * (meter_level / 5 if index < meter_level else 0)
            if filled > 0:
                rounded_rect(draw, box(x, 546 - filled, x + 58, 546), gray_level(6), None, radius=0)
                rounded_rect(draw, box(x, 546 - filled, x + 58, 552 - filled), PALETTE["route"], None, radius=0)

        for row in range(3):
            for col in range(8):
                index = row * 8 + col
                active_cell = index < evidence_level // 2
                fill = gray_level(3 + ((row + col) % 6)) if active_cell else gray_level(1 + ((row + col) % 5))
                x = 632 + col * 48
                y = 480 + row * 30
                rounded_rect(draw, box(x, y, x + 38, y + 22), fill, None, radius=0)
                if active_cell and index % 7 == 0:
                    rounded_rect(draw, box(x, y, x + 6, y + 22), PALETTE["attribute"], None, radius=0)

        for row in range(2):
            for col in range(20):
                index = row * 20 + col
                active_cell = index < evidence_level
                x = 64 + col * 72
                y = 640 + row * 28
                fill = gray_level(2 + (index % 7)) if active_cell else gray_level(1)
                rounded_rect(draw, box(x, y, x + 58, y + 20), fill, None, radius=0)
                if active_cell and index % 13 == 0:
                    rounded_rect(draw, box(x, y, x + 6, y + 20), PALETTE["attribute"], None, radius=0)

    def draw_probability_evaluation_motifs(active: int) -> None:
        # Source-specific glyphs for the LLM probabilities/evaluation module:
        # distribution bars, context shift, pass@N samples, tests, and judge/rubric.
        shift = ease((p - 0.12) / 0.38)
        sample = ease((p - 0.42) / 0.28)
        verify = ease((p - 0.58) / 0.25)
        judge = ease((p - 0.72) / 0.22)

        # Token stream and blinking cursor.
        for index in range(12):
            x = 92 + index * 34
            y = 116 + (index % 2) * 32
            fill = gray_level(2 + (index % 4))
            if index <= 3 + active:
                fill = accent if index % 5 == 0 else gray_level(5 - (index % 3))
            rounded_rect(draw, box(x, y, x + 28, y + 24), fill, None, radius=0)
        cursor_x = 92 + min(11, 3 + active) * 34 + 32
        rounded_rect(draw, box(cursor_x, 112, cursor_x + 8, 176), PALETTE["route"], None, radius=0)

        # Probability bars: poor context shifts into rich context without labels.
        for row in range(6):
            poor_w = 64 + ((row * 41 + 20) % 148)
            rich_w = 52 + ((5 - row) * 47 + 30) % 168
            width_px = poor_w * (1 - shift) + rich_w * shift
            fill = accent if row in {1, 4} else gray_level(3 + (row % 3))
            if row == 2 and shift > 0.52:
                fill = PALETTE["attribute"]
            y = 216 + row * 34
            rounded_rect(draw, box(104, y, 104 + width_px, y + 22), fill, None, radius=0)
            rounded_rect(draw, box(104 + width_px + 8, y, 388, y + 22), gray_level(2), None, radius=0)

        # Two context matrices: sparse prompt on the left, richer context on the right.
        for grid_index, origin_x in enumerate((500, 696)):
            for row in range(5):
                for col in range(5):
                    index = row * 5 + col
                    activated = index <= active * 3 + grid_index * 4
                    fill = gray_level(1 + ((row + col + grid_index) % 5))
                    if activated and ((row + col + grid_index) % 4 == 0):
                        fill = accent if grid_index else gray_level(5)
                    rounded_rect(
                        draw,
                        box(origin_x + col * 32, 132 + row * 32, origin_x + col * 32 + 28, 132 + row * 32 + 28),
                        fill,
                        None,
                        radius=0,
                    )
        draw_polyline(draw, [pt(660, 212), pt(692, 212)], PALETTE["route"], 5, shift)

        # pass@N grid: several samples fail, one late sample becomes the selected pass.
        for row in range(2):
            for col in range(6):
                index = row * 6 + col
                x = 488 + col * 46
                y = 360 + row * 46
                revealed = sample * 12 > index
                fill = gray_level(2 + (index % 4))
                if revealed and index == 9:
                    fill = PALETTE["route"]
                elif revealed and index in {2, 5, 7}:
                    fill = PALETTE["tradeoff"]
                elif revealed:
                    fill = gray_level(5)
                rounded_rect(draw, box(x, y, x + 36, y + 36), fill, gray_level(5), width=1, radius=0)

        # Programmatic checks and judge/rubric cards.
        for row in range(6):
            y = 196 + row * 42
            width_px = 56 + row * 22 + verify * (88 - row * 6)
            fill = PALETTE["route"] if row == 4 and verify > 0.35 else gray_level(3 + row % 3)
            if row in {1, 3} and verify > 0.55:
                fill = PALETTE["tradeoff"]
            rounded_rect(draw, box(1028, y, 1028 + width_px, y + 24), fill, None, radius=0)
            rounded_rect(draw, box(1180, y, 1220, y + 24), gray_level(5 if row == 4 and verify > 0.35 else 2), None, radius=0)
        for card in range(3):
            x = 1016 + card * 78
            h = 56 + card * 22
            fill = PALETTE["attribute"] if card == 1 and judge > 0.35 else gray_level(2 + card)
            rounded_rect(draw, box(x, 496 - h, x + 64, 496), fill, gray_level(5), width=1, radius=0)
            rounded_rect(draw, box(x, 508, x + 64 * judge, 524), PALETTE["route"] if card == 1 else gray_level(5), None, radius=0)

        # Evaluation loop and source-bound evidence floor.
        path = [(300, 150), (500, 212), (600, 380), (760, 380), (1030, 300), (1112, 472)]
        for index, (start, end) in enumerate(zip(path, path[1:])):
            draw.line([pt(*start), pt(*end)], fill=hex_to_rgb(gray_level(5)), width=3)
            if index <= active:
                draw_polyline(draw, [pt(*start), pt(*end)], PALETTE["route"] if index % 2 == 0 else PALETTE["attribute"], 6, 1)
        for index, (x, y) in enumerate(path):
            fill = PALETTE["route"] if index <= active and index % 3 == 0 else gray_level(2 + index % 4)
            rounded_rect(draw, box(x - 20, y - 20, x + 20, y + 20), fill, gray_level(5), width=1, radius=0)
        draw_evidence_floor(active)

    def draw_network(nodes: list[tuple[int, int]], active: int, branching: bool = False) -> None:
        for index, (start, end) in enumerate(zip(nodes, nodes[1:])):
            draw.line([pt(*start), pt(*end)], fill=hex_to_rgb(gray_level(5)), width=3)
            if index < active:
                draw_polyline(draw, [pt(*start), pt(*end)], accent if index % 2 == 0 else secondary, 7, 1)
        if branching and len(nodes) >= 4:
            branches = [
                (nodes[1], (nodes[1][0] + 96, nodes[1][1] - 96)),
                (nodes[2], (nodes[2][0] + 112, nodes[2][1] + 100)),
                (nodes[-2], (nodes[-2][0] + 124, nodes[-2][1] - 72)),
            ]
            for index, (start, end) in enumerate(branches):
                draw.line([pt(*start), pt(*end)], fill=hex_to_rgb(gray_level(5)), width=3)
                if active > index + 2:
                    draw_polyline(draw, [pt(*start), pt(*end)], alert if index == 1 else secondary, 6, 1)
        for index, (x, y) in enumerate(nodes):
            active_node = index <= active
            fill = accent if active_node and index % 4 == 0 else gray_level(2 + (index % 4))
            outline = secondary if active_node else gray_level(5)
            rounded_rect(draw, box(x - 24, y - 24, x + 24, y + 24), fill, outline, width=3 if active_node else 1, radius=0)

    if pattern == "comparison-matrix" and probability_evaluation_requested(args):
        draw_probability_evaluation_motifs(active_step)
    elif pattern in {"comparison-matrix", "evidence-ladder", "layered-architecture"}:
        draw_grid_surface(92, 124, 9, 5, 48, active_step)
        draw_grid_surface(620, 148, 7, 6, 40, max(1, active_step - 1))
        draw_bar_stack(1050, 180, 9, active_step)
        draw.line([pt(544, 156), pt(1016, 512)], fill=hex_to_rgb(accent), width=5)
        draw_evidence_floor(active_step)
    elif pattern in {"state-machine", "phase-timeline", "sequence-trace"}:
        lane_ys = [168, 236, 304, 372, 440, 508]
        for index, y in enumerate(lane_ys):
            rounded_rect(draw, box(92, y - 18, 1128, y + 18), gray_level(1 + index % 5), None, radius=0)
            filled_w = 140 + ease((p - 0.06 - index * 0.045) / 0.42) * (820 - index * 48)
            fill = accent if index % 2 == 0 else secondary
            rounded_rect(draw, box(92, y - 18, 92 + filled_w, y + 18), fill if index <= active_step else gray_level(4), None, radius=0)
        draw_network([(120, 580), (300, 540), (480, 580), (660, 540), (840, 580), (1040, 520)], max(1, active_step - 1), True)
    elif pattern == "swimlane-handoff":
        for lane in range(5):
            y = 132 + lane * 88
            rounded_rect(draw, box(92, y, 1268, y + 64), gray_level(1 + lane % 5), None, radius=0)
            draw_bar_stack(116 + lane * 32, y + 18, 1, active_step)
        path = [(132, 164), (318, 252), (512, 340), (732, 252), (948, 428), (1176, 516)]
        draw_network(path, active_step, True)
    elif pattern in {"risk-bowtie", "scenario-tree"}:
        center = (704, 340)
        left_nodes = [(180, 204), (180, 300), (180, 396), (180, 492)]
        right_nodes = [(1220, 204), (1220, 300), (1220, 396), (1220, 492)]
        rounded_rect(draw, box(center[0] - 56, center[1] - 56, center[0] + 56, center[1] + 56), alert, gray_level(6), width=4, radius=0)
        for index, node in enumerate(left_nodes + right_nodes):
            fill = gray_level(2 + index % 4)
            rounded_rect(draw, box(node[0] - 44, node[1] - 24, node[0] + 44, node[1] + 24), fill, accent if index <= active_step else gray_level(5), width=3, radius=0)
            target = center if index < 4 else center
            draw.line([pt(*node), pt(*target)], fill=hex_to_rgb(gray_level(5)), width=3)
            if index <= active_step:
                draw_polyline(draw, [pt(*node), pt(*target)], accent if index < 4 else secondary, 6, 1)
        draw_grid_surface(404, 548, 8, 2, 32, active_step)
    elif pattern == "dependency-map" and mcp_protocol_requested:
        draw_mcp_protocol_bus(active_step)
    elif pattern == "data-lineage":
        path = [(120, 250), (300, 250), (480, 250), (660, 250), (840, 250), (1040, 250)]
        draw_network(path, active_step, False)
        for index, (x, _) in enumerate(path):
            draw_grid_surface(x - 44, 360 + (index % 2) * 72, 3, 3, 28, max(0, active_step - index))
        draw_bar_stack(1120, 392, 5, active_step)
    else:
        nodes = [(128, 352), (272, 300), (424, 252), (600, 332), (780, 300), (960, 252), (1144, 344)]
        draw_network(nodes, active_step, True)
        draw_grid_surface(1000, 432, 7, 4, 36, active_step)
        draw_bar_stack(116, 472, 5, active_step)

    for index, module in enumerate(MASONRY_MODULE_BOUNDS[::2][:8]):
        if index > active_step:
            continue
        x = int(module["x"]) + 12
        y = int(module["y"]) + 10
        width_px = max(24, int(module["width"]) - 24)
        height_px = min(24, max(12, int(module["height"]) // 5))
        fill = accent if index % 3 == 0 else gray_level(5 - index % 3)
        rounded_rect(draw, box(x, y, x + width_px * ease((p - index * 0.05) / 0.32), y + height_px), fill, None, radius=0)

    return img


def render_agent_loop_masonry_frame(
    second: float,
    args: argparse.Namespace,
    fonts: dict[str, ImageFont.ImageFont],
) -> Image.Image:
    width, height = args.width, args.height
    sx = width / 1280
    sy = height / 720

    def pt(x: float, y: float) -> tuple[int, int]:
        return round(x * sx), round(y * sy)

    def box(x1: float, y1: float, x2: float, y2: float) -> tuple[int, int, int, int]:
        return round(x1 * sx), round(y1 * sy), round(x2 * sx), round(y2 * sy)

    canvas_width = round(width * 1.5)
    img = Image.new("RGB", (canvas_width, height), hex_to_rgb(PALETTE["paper"]))
    draw = ImageDraw.Draw(img)
    p = clamp(second / max(args.duration, 0.001))
    active = min(7, int(ease((p - 0.05) / 0.76) * 8))
    draw_masonry_megacanvas_base(draw, second, args)

    def module_rect(x: float, y: float, w: float, h: float, fill: str, stroke: str | None = None, width_px: int = 1) -> None:
        rounded_rect(draw, box(x, y, x + w, y + h), fill, stroke, width=width_px, radius=0)

    def angular_path(points: list[tuple[float, float]], fill: str, width_px: int, progress: float = 1.0) -> None:
        int_points = [pt(x, y) for x, y in points]
        draw_polyline(draw, int_points, fill, width_px, progress)

    # Context window: stacked panes feeding the agent loop.
    for index in range(5):
        x = 96 + index * 24
        y = 112 + index * 22
        w = 244 - index * 28
        h = 188 - index * 18
        fill = gray_level(1 + (index % 5))
        module_rect(x, y, w, h, fill, gray_level(5), 1)
        if index <= active:
            module_rect(x, y, 8, h, PALETTE["route"] if index % 2 == 0 else gray_level(5), None, 1)
    for row in range(4):
        for col in range(4):
            cell_on = active >= row + col
            fill = PALETTE["route"] if cell_on and (row + col) % 4 == 0 else gray_level(2 + ((row + col) % 4))
            module_rect(120 + col * 44, 352 + row * 34, 34, 24, fill, None)

    # Agent loop ring: observe -> act -> check -> continue as hard-edge stations.
    loop_points = [(600, 156), (790, 270), (738, 464), (520, 476), (420, 300), (600, 156)]
    for start, end in zip(loop_points, loop_points[1:]):
        draw.line([pt(*start), pt(*end)], fill=hex_to_rgb(gray_level(5)), width=4)
    segment_progress = ease((p - 0.10) / 0.54)
    angular_path(loop_points, PALETTE["route"], 8, segment_progress)
    station_fills = [PALETTE["route"], gray_level(4), PALETTE["attribute"], gray_level(3), PALETTE["tradeoff"]]
    for index, (x, y) in enumerate(loop_points[:-1]):
        station_active = active >= index
        fill = station_fills[index] if station_active else gray_level(2 + index % 4)
        module_rect(x - 38, y - 34, 76, 68, fill, gray_level(6), 2 if station_active else 1)
        inner = 18 + (index % 3) * 8
        module_rect(x - 22, y - 8, inner, 16, gray_level(1 + index % 4), None)
        module_rect(x + 4, y - 8, 26, 16, gray_level(4), None)
    packet = point_on_polyline([pt(x, y) for x, y in loop_points], segment_progress)
    module_rect(packet[0] / sx - 12, packet[1] / sy - 12, 24, 24, PALETTE["gold"], gray_level(6), 1)

    # Model core plus tools/state blocks inside and around the ring.
    module_rect(566, 280, 132, 104, gray_level(1), PALETTE["route"], 3)
    for row in range(3):
        for col in range(3):
            fill = PALETTE["route"] if active >= 2 and (row + col) % 3 == 0 else gray_level(2 + ((row + col) % 4))
            module_rect(586 + col * 32, 300 + row * 24, 24, 16, fill, None)
    tool_positions = [(498, 208), (742, 198), (842, 368), (652, 530), (404, 410), (404, 226)]
    for index, (x, y) in enumerate(tool_positions):
        fill = PALETTE["attribute"] if active >= index + 1 and index % 2 == 0 else gray_level(2 + index % 4)
        module_rect(x, y, 40, 40, fill, gray_level(5), 1)
        module_rect(x + 8, y + 8, 24, 8, gray_level(1 + index % 4), None)
        module_rect(x + 8, y + 24, 24, 8, gray_level(4), None)

    # Environment surfaces mutate: repo/browser/ticket/docs/database as changing grids.
    env_origins = [(934, 112), (1112, 112), (934, 268), (1112, 268), (1024, 436)]
    for index, (x, y) in enumerate(env_origins):
        module_rect(x, y, 132, 104, gray_level(1 + index % 5), gray_level(5), 1)
        for row in range(3):
            for col in range(4):
                reveal = ease((p - 0.18 - index * 0.05 - (row + col) * 0.018) / 0.18)
                fill = PALETTE["damage"] if reveal > 0.62 and (row + col + index) % 5 == 0 else gray_level(2 + ((row * 2 + col + index) % 4))
                module_rect(x + 12 + col * 26, y + 14 + row * 24, 18, 14, fill, None)
        if index <= active:
            angular_path([(698, 332), (846 + index * 18, 332), (846 + index * 18, y + 52), (x, y + 52)], PALETTE["route"] if index % 2 == 0 else PALETTE["attribute"], 4, 1)

    # Fixed workflow lane versus adaptive agent lane.
    lane_y = 608
    for index in range(5):
        x = 116 + index * 96
        fill = PALETTE["route"] if index <= min(active, 4) else gray_level(3)
        module_rect(x, lane_y - 30, 58, 44, fill, gray_level(5), 1)
        if index > 0:
            draw.line([pt(x - 38, lane_y - 8), pt(x, lane_y - 8)], fill=hex_to_rgb(gray_level(5)), width=3)
    adaptive_path = [(672, 602), (768, 560), (880, 608), (1016, 566), (1136, 610), (1224, 554), (1328, 610)]
    for start, end in zip(adaptive_path, adaptive_path[1:]):
        draw.line([pt(*start), pt(*end)], fill=hex_to_rgb(gray_level(5)), width=3)
    angular_path(adaptive_path, PALETTE["attribute"], 6, ease((p - 0.48) / 0.34))
    for index, (x, y) in enumerate(adaptive_path):
        fill = PALETTE["attribute"] if active >= index else gray_level(2 + index % 4)
        module_rect(x - 24, y - 22, 48, 44, fill, gray_level(5), 1)
    branch_x, branch_y = adaptive_path[2]
    angular_path([(branch_x, branch_y), (934, 664), (1090, 664)], PALETTE["tradeoff"], 5, ease((p - 0.60) / 0.20))

    # Approval checkpoint and final Model+Tools+State+Loop badge as non-text geometry.
    approval_on = p > 0.68
    module_rect(1390, 252, 112, 120, PALETTE["tradeoff"] if approval_on else gray_level(3), gray_level(6), 2)
    module_rect(1414, 284, 64, 16, gray_level(1), None)
    module_rect(1426, 316, 40, 36, gray_level(5 if approval_on else 2), None)
    for index in range(4):
        x = 1332 + index * 74
        fill = PALETTE["route"] if p > 0.78 and index == 3 else gray_level(2 + index)
        module_rect(x, 448, 60, 60, fill, gray_level(5), 1)
        module_rect(x + 10, 462, 40, 8, gray_level(1 + index % 4), None)
        module_rect(x + 10, 482, 40, 8, gray_level(5), None)

    # Source-bound evidence floor keeps all quadrants semantically occupied.
    for row in range(2):
        for col in range(14):
            index = row * 14 + col
            x = 64 + col * 52
            y = 656 + row * 32
            fill = PALETTE["route"] if index <= active * 3 and index % 7 == 0 else gray_level(2 + index % 4)
            module_rect(x, y, 42, 22, fill, None)
    return img


def render_hook_masonry_frame(
    second: float,
    args: argparse.Namespace,
    fonts: dict[str, ImageFont.ImageFont],
) -> Image.Image:
    width, height = args.width, args.height
    sx = width / 1280
    sy = height / 720

    def pt(x: float, y: float) -> tuple[int, int]:
        return round(x * sx), round(y * sy)

    def box(x1: float, y1: float, x2: float, y2: float) -> tuple[int, int, int, int]:
        return round(x1 * sx), round(y1 * sy), round(x2 * sx), round(y2 * sy)

    canvas_width = round(width * 1.5)
    img = Image.new("RGB", (canvas_width, height), hex_to_rgb(PALETTE["paper"]))
    draw = ImageDraw.Draw(img)
    p = clamp(second / max(args.duration, 0.001))
    active = min(9, int(ease((p - 0.04) / 0.78) * 10))
    draw_masonry_megacanvas_base(draw, second, args)

    def module_rect(x: float, y: float, w: float, h: float, fill: str, stroke: str | None = None, width_px: int = 1) -> None:
        bounds = box(x, y, x + max(1, w), y + max(1, h))
        if fill == "none":
            if stroke:
                draw.rectangle(bounds, outline=hex_to_rgb(stroke), width=width_px)
            return
        rounded_rect(draw, bounds, fill, stroke, width=width_px, radius=0)

    def angular_path(points: list[tuple[float, float]], fill: str, width_px: int, progress: float = 1.0) -> None:
        draw_polyline(draw, [pt(x, y) for x, y in points], fill, width_px, progress)

    # Lifecycle event timeline: event nodes light up before hooks intercept them.
    timeline_y = 160
    event_nodes = [(104 + index * 92, timeline_y + (24 if index % 2 else 0)) for index in range(8)]
    for index in range(len(event_nodes) - 1):
        angular_path([event_nodes[index], event_nodes[index + 1]], gray_level(5), 3, 1)
        if index < active:
            angular_path([event_nodes[index], event_nodes[index + 1]], PALETTE["route"], 3, ease((p - 0.05 - index * 0.045) / 0.12))
    for index, (x, y) in enumerate(event_nodes):
        node_active = index <= active
        fill = gray_level(2 + index % 4)
        module_rect(x - 22, y - 20, 44, 40, fill, gray_level(5), 1)
        if node_active:
            module_rect(x - 22, y - 20, 8, 40, PALETTE["route"], None)
        module_rect(x - 22, y - 20, 12, 40, gray_level(1 + index % 4), None)
    pulse_index = min(len(event_nodes) - 2, active)
    pulse = point_on_polyline([event_nodes[pulse_index], event_nodes[pulse_index + 1]], ease((p * 8) % 1))
    module_rect(pulse[0] - 10, pulse[1] - 10, 20, 20, gray_level(5), gray_level(6), 1)

    # Shield gate overlays the timeline and converts passive lifecycle into active control.
    shield_on = p > 0.16
    gate_close = ease((p - 0.16) / 0.20)
    module_rect(428, 96, 28, 188, gray_level(5 if shield_on else 4), gray_level(6), 1)
    module_rect(792, 96, 28, 188, gray_level(5 if shield_on else 4), gray_level(6), 1)
    if shield_on:
        module_rect(428, 96, 4, 188, PALETTE["damage"], None)
        module_rect(816, 96, 4, 188, PALETTE["damage"], None)
    module_rect(456, 96, 336 * gate_close, 8, gray_level(5), None)
    module_rect(456, 276, 336 * gate_close, 8, gray_level(5), None)
    loop_points = [(520, 132), (704, 132), (756, 196), (664, 264), (520, 236), (480, 176), (520, 132)]
    for start, end in zip(loop_points, loop_points[1:]):
        draw.line([pt(*start), pt(*end)], fill=hex_to_rgb(gray_level(5)), width=3)
    angular_path(loop_points, PALETTE["route"], 3, ease((p - 0.18) / 0.36))

    # Provider surfaces show three hook/event systems without product text.
    provider_on = p > 0.26
    for index, x in enumerate([940, 1116, 1292]):
        module_rect(x, 104, 144, 220, gray_level(1 + index), gray_level(5), 1)
        if index == 0:
            for row in range(5):
                row_active = provider_on and row <= active - 2
                fill = gray_level(2 + row % 4)
                module_rect(x, 104 + row * 44, 144, 44, fill, None)
                if row_active:
                    module_rect(x, 104 + row * 44, 8, 44, PALETTE["route"], None)
                module_rect(x, 104 + row * 44, 16, 44, gray_level(5), None)
        elif index == 1:
            cloud = [(x + 72, 136), (x + 116, 176), (x + 100, 244), (x + 44, 254), (x + 24, 188), (x + 72, 136)]
            cloud_cells = [
                (x, 104, 72, 72),
                (x + 72, 104, 72, 72),
                (x, 176, 72, 72),
                (x + 72, 176, 72, 72),
                (x, 248, 72, 76),
                (x + 72, 248, 72, 76),
            ]
            for cell_index, (cx, cy, cw, ch) in enumerate(cloud_cells):
                cell_fill = gray_level(5) if p > 0.36 and cell_index in {1, 2, 4} else gray_level(2 + cell_index % 4)
                module_rect(cx, cy, cw, ch, cell_fill, gray_level(5), 1)
            angular_path(cloud, PALETTE["attribute"], 3, ease((p - 0.30) / 0.28))
        else:
            row_y = 104
            for row in range(6):
                row_active = p > 0.38 and row <= active - 3
                fill = gray_level(2 + row % 4)
                row_h = 40 if row == 5 else 36
                module_rect(x, row_y, 144, row_h, fill, gray_level(5), 1)
                if row_active:
                    module_rect(x, row_y, 8, row_h, PALETTE["route"], None)
                module_rect(x + 132, row_y, 12, row_h, gray_level(5), None)
                row_y += row_h

    # Bash pre-tool hook blocks destructive commands while safe flow continues.
    block_on = p > 0.44
    for row in range(5):
        for col in range(6):
            cell_blocked = block_on and row == 2 and col >= 2
            fill = gray_level(2 + (row + col) % 4)
            module_rect(96 + col * 42, 420 + row * 30, 34, 20, fill, None)
            if cell_blocked:
                module_rect(96 + col * 42, 420 + row * 30, 34, 6, PALETTE["damage"], None)
    module_rect(388, 400, 48, 176, gray_level(5 if block_on else 4), gray_level(6), 1)
    if block_on:
        module_rect(428, 400, 8, 176, PALETTE["damage"], None)
    for index in range(3):
        x = 468 + index * 72
        module_rect(x, 430, 54, 54, gray_level(5 if block_on else 3), gray_level(5), 1)
        if block_on:
            module_rect(x, 430, 54, 8, PALETTE["damage"], None)
        module_rect(x, 504, 54, 18, gray_level(5), None)
    angular_path([(316, 480), (388, 480), (436, 480)], PALETTE["damage"], 4, ease((p - 0.44) / 0.16))
    angular_path([(436, 548), (516, 596), (660, 596)], PALETTE["route"], 3, ease((p - 0.58) / 0.18))

    # Filtering/preprocessing shrinks noisy output before it reaches the model.
    filter_on = p > 0.54
    for row in range(6):
        for col in range(8):
            fill = gray_level(5) if filter_on and (row + col) % 5 == 0 else gray_level(2 + (row + col) % 4)
            module_rect(680 + col * 28, 408 + row * 22, 20, 14, fill, None)
    module_rect(936, 410, 34, 136, gray_level(5) if filter_on else gray_level(4), gray_level(6), 1)
    reduced = min(6, int(ease((p - 0.56) / 0.22) * 7))
    for index in range(6):
        bar_active = index < reduced
        module_rect(1008 + index * 32, 430, 24, 76, gray_level(5 if bar_active else 3 + index % 3), gray_level(5), 1)
        if bar_active:
            module_rect(1008 + index * 32, 430, 8, 76, PALETTE["route"], None)
    for row in range(4):
        for col in range(5):
            cell_active = filter_on and row == col % 4
            fill = gray_level(2 + (row + col) % 4)
            module_rect(744 + col * 32, 562 + row * 24, 24, 18, fill, None)
            if cell_active:
                module_rect(744 + col * 32, 562 + row * 24, 6, 18, PALETTE["route"], None)

    # Typical hook jobs cascade across lanes: format, validate, secret, audit, notify, shrink.
    cascade_on = p > 0.62
    for lane in range(6):
        x = 1188 + lane * 60
        y = 392 + lane * 24
        lane_active = cascade_on and lane <= active - 4
        fill = gray_level(2 + lane % 4)
        module_rect(x, y, 52, 48, fill, gray_level(5), 1)
        if lane_active:
            module_rect(x, y, 8, 48, PALETTE["route"], None)
        module_rect(x, y + 40, 52, 8, gray_level(5), None)
        if lane > 0:
            angular_path([(x - 36, y + 24), (x, y + 24)], gray_level(5), 3, 1)

    # Cost and latency: preprocessing can lower tokens, but slow hooks add delay.
    savings_level = min(6, int(ease((p - 0.66) / 0.24) * 7))
    latency_level = min(5, int(ease((p - 0.70) / 0.22) * 6))
    module_rect(1516, 404, 264, 46, gray_level(3), gray_level(5), 1)
    savings_width = 264 * (savings_level / 6)
    module_rect(1516, 404, savings_width, 46, gray_level(5), None)
    if savings_width > 0:
        module_rect(1516 + max(0, savings_width - 8), 404, min(8, savings_width), 46, PALETTE["route"], None)
    module_rect(1516, 480, 264, 46, gray_level(3), gray_level(5), 1)
    latency_width = 264 * (latency_level / 5)
    module_rect(1516, 480, latency_width, 46, gray_level(5 if latency_level >= 4 else 4), None)
    if latency_width > 0:
        module_rect(1516 + max(0, latency_width - 8), 480, min(8, latency_width), 46, PALETTE["damage"] if latency_level >= 4 else PALETTE["attribute"], None)
    for mark in range(7):
        module_rect(1516 + mark * 44, 542, 8, 32, gray_level(5), None)
    slider_x = 1516 + 44 * latency_level
    module_rect(slider_x, 588, 40, 48, gray_level(5), gray_level(6), 1)
    module_rect(slider_x, 588, 8, 48, PALETTE["damage"] if latency_level >= 4 else PALETTE["route"], None)

    # Final lifecycle-control stamp as visual geometry, not text.
    if p > 0.82:
        module_rect(112, 608, 352, 56, gray_level(5), gray_level(6), 1)
        for index in range(4):
            fill = gray_level(5 if index in {0, 2} else 2 + index)
            module_rect(112 + index * 88, 608, 88, 56, fill, gray_level(6), 1)
            if index in {0, 2}:
                module_rect(112 + index * 88, 608, 8, 56, PALETTE["route"], None)
        angular_path([(464, 636), (584, 636), (660, 596)], PALETTE["route"], 6, ease((p - 0.82) / 0.14))

    # Source-bound evidence floor keeps all quadrants active after camera crops.
    for row in range(2):
        for col in range(24):
            index = row * 24 + col
            x = 64 + col * 64
            y = 652 + row * 24
            route_cell = index <= active * 4 and index % 9 == 0
            attribute_cell = index % 13 == 0 and p > 0.60
            fill = gray_level(2 + index % 4)
            module_rect(x, y, 52, 16, fill, None)
            if route_cell or attribute_cell:
                module_rect(x, y, 6, 16, PALETTE["attribute"] if attribute_cell else PALETTE["route"], None)
    return img


def render_harness_masonry_frame(
    second: float,
    args: argparse.Namespace,
    fonts: dict[str, ImageFont.ImageFont],
) -> Image.Image:
    width, height = args.width, args.height
    sx = width / 1280
    sy = height / 720

    def pt(x: float, y: float) -> tuple[int, int]:
        return round(x * sx), round(y * sy)

    def box(x1: float, y1: float, x2: float, y2: float) -> tuple[int, int, int, int]:
        return round(x1 * sx), round(y1 * sy), round(x2 * sx), round(y2 * sy)

    canvas_width = round(width * 1.5)
    img = Image.new("RGB", (canvas_width, height), hex_to_rgb(PALETTE["paper"]))
    draw = ImageDraw.Draw(img)
    p = clamp(second / max(args.duration, 0.001))
    active = min(8, int(ease((p - 0.04) / 0.78) * 9))
    draw_masonry_megacanvas_base(draw, second, args)

    def module_rect(x: float, y: float, w: float, h: float, fill: str, stroke: str | None = None, width_px: int = 1) -> None:
        rounded_rect(draw, box(x, y, x + w, y + h), fill, stroke, width=width_px, radius=0)

    def angular_path(points: list[tuple[float, float]], fill: str, width_px: int, progress: float = 1.0) -> None:
        draw_polyline(draw, [pt(x, y) for x, y in points], fill, width_px, progress)

    # Comparison grid opens the megacanvas and selects one runtime cell.
    grid_x, grid_y = 96, 112
    selected_col = min(3, int(ease((p - 0.06) / 0.20) * 4))
    selected_row = min(3, int(ease((p - 0.12) / 0.22) * 4))
    for row in range(4):
        for col in range(4):
            cell_active = row <= selected_row and col <= selected_col
            fill = PALETTE["route"] if row == selected_row and col == selected_col and p > 0.18 else gray_level(2 + ((row + col) % 4))
            if cell_active and (row + col) % 5 == 0:
                fill = PALETTE["attribute"]
            module_rect(grid_x + col * 54, grid_y + row * 46, 46, 38, fill, gray_level(5), 1)
            module_rect(grid_x + col * 54 + 8, grid_y + row * 46 + 10, 30, 6, gray_level(1 + (row + col) % 4), None)
            module_rect(grid_x + col * 54 + 8, grid_y + row * 46 + 24, 30, 6, gray_level(5), None)
    selected_x = grid_x + selected_col * 54 + 23
    selected_y = grid_y + selected_row * 46 + 19
    angular_path([(selected_x, selected_y), (360, 220), (492, 220)], PALETTE["route"], 6, ease((p - 0.16) / 0.20))

    # Runtime stack assembles as hard layers around the model core.
    stack_x, stack_y = 500, 108
    layer_count = min(7, int(ease((p - 0.18) / 0.34) * 8))
    for index in range(7):
        y = stack_y + index * 54
        fill = PALETTE["route"] if index < layer_count and index in {1, 4} else gray_level(1 + index % 5)
        module_rect(stack_x + index * 10, y, 300 - index * 18, 42, fill, gray_level(5), 1)
        module_rect(stack_x + index * 10, y, 8, 42, gray_level(5), None)
        for slot in range(4):
            slot_fill = PALETTE["attribute"] if index < layer_count and slot <= index % 4 else gray_level(2 + slot % 4)
            module_rect(stack_x + 42 + slot * 50, y + 12, 34, 16, slot_fill, None)

    # Engine core morphs into a dashboard/control surface.
    engine_on = p > 0.22
    module_rect(620, 284, 108, 92, PALETTE["route"] if engine_on else gray_level(3), gray_level(6), 3)
    for col in range(3):
        module_rect(638 + col * 26, 300, 18, 54, gray_level(1 + col), None)
    dashboard_on = p > 0.30
    for index, (x, y) in enumerate([(748, 256), (804, 256), (776, 312), (834, 312)]):
        fill = PALETTE["attribute"] if dashboard_on and index % 2 == 0 else gray_level(2 + index)
        module_rect(x, y, 44, 40, fill, gray_level(5), 1)
        module_rect(x + 10, y + 14, 24, 8, gray_level(5), None)
    control_path = [(674, 330), (728, 330), (748, 276), (804, 276), (834, 332)]
    angular_path(control_path, PALETTE["route"], 5, ease((p - 0.24) / 0.24))

    # Agent loop ring shows the harness controls repeated execution, not only one call.
    ring_points = [(616, 460), (716, 426), (822, 466), (786, 548), (654, 558), (590, 510), (616, 460)]
    for start, end in zip(ring_points, ring_points[1:]):
        draw.line([pt(*start), pt(*end)], fill=hex_to_rgb(gray_level(5)), width=3)
    angular_path(ring_points, PALETTE["attribute"], 6, ease((p - 0.34) / 0.34))
    for index, (x, y) in enumerate(ring_points[:-1]):
        fill = PALETTE["attribute"] if active >= index + 2 else gray_level(2 + index % 4)
        module_rect(x - 20, y - 18, 40, 36, fill, gray_level(5), 1)

    # Same model badge drops into three different harness shells.
    shell_origins = [(928, 108), (1112, 108), (1296, 108)]
    model_drop = ease((p - 0.38) / 0.20)
    for shell_index, (x, y) in enumerate(shell_origins):
        shell_fill = gray_level(1 + shell_index)
        module_rect(x, y, 152, 220, shell_fill, gray_level(5), 1)
        badge_y = y + 22 + (1 - model_drop) * -80
        module_rect(x + 54, badge_y, 44, 44, PALETTE["route"], gray_level(6), 2)
        # Distinct defaults for Copilot, Claude Code, and OpenCode without product labels.
        if shell_index == 0:
            for row in range(5):
                fill = PALETTE["route"] if row <= active - 4 else gray_level(2 + row % 4)
                module_rect(x + 20, y + 92 + row * 22, 112, 14, fill, None)
            module_rect(x + 20, y + 190, 112 * ease((p - 0.52) / 0.22), 16, PALETTE["attribute"], None)
        elif shell_index == 1:
            loop = [(x + 46, y + 116), (x + 86, y + 94), (x + 124, y + 124), (x + 92, y + 168), (x + 46, y + 154), (x + 46, y + 116)]
            angular_path(loop, PALETTE["attribute"], 4, ease((p - 0.46) / 0.24))
            for bx, by in [(x + 22, y + 170), (x + 62, y + 170), (x + 102, y + 170), (x + 62, y + 124)]:
                module_rect(bx, by, 28, 24, gray_level(4), gray_level(5), 1)
        else:
            module_rect(x + 24, y + 94, 104, 28, PALETTE["attribute"] if p > 0.50 else gray_level(3), gray_level(5), 1)
            for row in range(3):
                for col in range(3):
                    fill = PALETTE["route"] if p > 0.54 and row == col else gray_level(2 + (row + col) % 4)
                    module_rect(x + 28 + col * 34, y + 144 + row * 22, 24, 16, fill, None)

    # Tool/context/retry growth drives the cost meter.
    cost_x, cost_y = 932, 408
    tool_count = min(6, int(ease((p - 0.52) / 0.22) * 7))
    for index in range(6):
        fill = PALETTE["route"] if index < tool_count else gray_level(3 + index % 3)
        module_rect(cost_x + index * 34, cost_y, 26, 58, fill, gray_level(5), 1)
    meter_level = min(5, int(ease((p - 0.42) / 0.38) * 6))
    module_rect(cost_x, cost_y + 88, 244, 42, gray_level(3), gray_level(5), 1)
    module_rect(cost_x, cost_y + 88, 244 * (meter_level / 5), 42, PALETTE["damage"] if meter_level >= 4 else PALETTE["attribute"], None)
    for mark in range(6):
        module_rect(cost_x + mark * 48, cost_y + 138, 8, 30, gray_level(5), None)

    # Feature grid mutes behind a use-case matrix, then a selection path reappears.
    matrix_x, matrix_y = 1212, 408
    for row in range(4):
        for col in range(5):
            base = gray_level(2 + ((row + col) % 4))
            fill = base if p < 0.70 else gray_level(2)
            if p > 0.74 and (row, col) in {(0, 1), (1, 2), (2, 3), (3, 4)}:
                fill = PALETTE["route"] if p > 0.82 else PALETTE["attribute"]
            module_rect(matrix_x + col * 52, matrix_y + row * 42, 44, 34, fill, gray_level(5), 1)
    selection_path = [(1234, 425), (1286, 467), (1338, 509), (1390, 551)]
    angular_path(selection_path, PALETTE["route"], 7, ease((p - 0.80) / 0.16))

    # Source-bound evidence floor keeps the frame visually occupied without captions.
    for row in range(2):
        for col in range(22):
            index = row * 22 + col
            x = 64 + col * 64
            y = 648 + row * 26
            fill = PALETTE["route"] if index <= active * 4 and index % 8 == 0 else gray_level(2 + index % 4)
            if index % 11 == 0 and p > 0.60:
                fill = PALETTE["attribute"]
            module_rect(x, y, 52, 18, fill, None)
    return img


def render_ai_alternatives_masonry_frame(
    second: float,
    args: argparse.Namespace,
    fonts: dict[str, ImageFont.ImageFont],
) -> Image.Image:
    width, height = args.width, args.height
    sx = width / 1280
    sy = height / 720

    def pt(x: float, y: float) -> tuple[int, int]:
        return round(x * sx), round(y * sy)

    def box(x1: float, y1: float, x2: float, y2: float) -> tuple[int, int, int, int]:
        return round(x1 * sx), round(y1 * sy), round(x2 * sx), round(y2 * sy)

    canvas_width = round(width * 1.5)
    img = Image.new("RGB", (canvas_width, height), hex_to_rgb(PALETTE["paper"]))
    draw = ImageDraw.Draw(img)
    p = clamp(second / max(args.duration, 0.001))
    active = min(10, int(ease((p - 0.04) / 0.78) * 11))
    draw_masonry_megacanvas_base(draw, second, args)

    def module_rect(x: float, y: float, w: float, h: float, fill: str, stroke: str | None = None, width_px: int = 1) -> None:
        bounds = box(x, y, x + max(1, w), y + max(1, h))
        if fill == "none":
            if stroke:
                draw.rectangle(bounds, outline=hex_to_rgb(stroke), width=width_px)
            return
        rounded_rect(draw, bounds, fill, stroke, width=width_px, radius=0)

    def angular_path(points: list[tuple[float, float]], fill: str, width_px: int, progress: float = 1.0) -> None:
        draw_polyline(draw, [pt(x, y) for x, y in points], fill, width_px, progress)

    # Four alternatives share one hard-edged comparison surface instead of four cards.
    grid_x, grid_y = 80, 108
    column_w, row_h = 92, 56
    platform_count = min(4, int(ease((p - 0.08) / 0.30) * 5))
    for col in range(4):
        for row in range(4):
            fill = gray_level(1 + ((row + col) % 5))
            if col < platform_count and row == 0:
                fill = gray_level(5)
            if col < platform_count and row == 3:
                fill = gray_level(3 + (col % 3))
            module_rect(grid_x + col * column_w, grid_y + row * row_h, column_w, row_h, fill, gray_level(5), 1)
            stripe_fill = PALETTE["route"] if col < platform_count and row == 3 and p > 0.58 else gray_level(5)
            module_rect(grid_x + col * column_w, grid_y + row * row_h, 8, row_h, stripe_fill, None)
    module_rect(grid_x, grid_y, column_w * 4, row_h * 4, "none", gray_level(5), 2)

    # Platform home bases are visual signatures for natural workspaces, not product cards.
    home_x, home_y = 520, 100
    home_specs = [
        (home_x, home_y, 168, 132),
        (home_x + 168, home_y, 184, 132),
        (home_x, home_y + 132, 168, 148),
        (home_x + 168, home_y + 132, 184, 148),
    ]
    def workspace_signature(index: int, x: float, y: float, w: float, h: float, visible: bool) -> None:
        if index == 0:
            module_rect(x, y, 24, h, gray_level(5), None)
            module_rect(x + 24, y, w - 24, 36, gray_level(3), gray_level(5), 1)
            for row in range(3):
                band_y = y + 36 + row * 32
                module_rect(x + 24, band_y, 72, 32, gray_level(1 + row), gray_level(5), 1)
                module_rect(x + 96, band_y, w - 96, 32, gray_level(2 + row), gray_level(5), 1)
            module_rect(x + 24, y + h - 8, (w - 24) * ease((p - 0.16) / 0.30), 8, PALETTE["route"] if visible else gray_level(4), None)
        elif index == 1:
            module_rect(x, y, w / 2, h / 2, gray_level(1), gray_level(5), 1)
            module_rect(x + w / 2, y, w / 2, h / 2, gray_level(3), gray_level(5), 1)
            module_rect(x, y + h / 2, w / 2, h / 2, gray_level(4), gray_level(5), 1)
            module_rect(x + w / 2, y + h / 2, w / 2, h / 2, gray_level(2), gray_level(5), 1)
            module_rect(x + w / 2 - 8, y, 16, h, gray_level(5), None)
            module_rect(x, y + h / 2 - 8, w, 16, gray_level(5), None)
            if visible and p > 0.34:
                module_rect(x + w - 12, y, 12, h, PALETTE["route"], None)
        elif index == 2:
            module_rect(x, y, 36, h, gray_level(5), None)
            module_rect(x + 36, y, w - 36, 24, gray_level(3), gray_level(5), 1)
            rows = 5
            for row in range(rows):
                row_y = y + 24 + row * ((h - 24) / rows)
                fill = gray_level(1 + ((row + 1) % 5))
                module_rect(x + 36, row_y, w - 36, (h - 24) / rows, fill, gray_level(5), 1)
                if visible and row in {1, 3}:
                    module_rect(x + 36, row_y, (w - 36) * ease((p - 0.32) / 0.32), 8, PALETTE["route"], None)
            angular_path([(x + 36, y + h - 28), (x + 88, y + h - 56), (x + 136, y + h - 24)], PALETTE["route"], 4, ease((p - 0.36) / 0.26))
        else:
            module_rect(x, y, w, 48, gray_level(5), gray_level(6), 1)
            for row in range(3):
                module_rect(x, y + 48 + row * 28, w * (0.64 + row * 0.10), 28, gray_level(2 + row), gray_level(5), 1)
            module_rect(x + w / 2, y + 48, w / 2, h - 48, gray_level(1), gray_level(5), 1)
            loop = [(x + 112, y + 92), (x + 152, y + 76), (x + 172, y + 112), (x + 132, y + 140), (x + 96, y + 124), (x + 112, y + 92)]
            angular_path(loop, PALETTE["route"], 4, ease((p - 0.42) / 0.28))

    for index, (x, y, w, h) in enumerate(home_specs):
        visible = index < platform_count
        workspace_signature(index, x, y, w, h, visible)
    for index, (_, y, _, h) in enumerate(home_specs):
        start = (grid_x + column_w * index + column_w, grid_y + row_h * 2)
        end = (home_x + (index % 2) * 168, y + h / 2)
        angular_path([start, (start[0] + 56, start[1]), (end[0], end[1])], PALETTE["route"], 4, ease((p - 0.18 - index * 0.04) / 0.18))

    # Fit map: radar axes become quadrants, using gray hierarchy plus sparse red risk.
    radar_cx, radar_cy = 1000, 238
    axis_count = min(5, int(ease((p - 0.28) / 0.30) * 6))
    for index in range(5):
        angle = -1.5708 + index * 1.2566
        end_x = radar_cx + round(132 * math.cos(angle) / 4) * 4
        end_y = radar_cy + round(108 * math.sin(angle) / 4) * 4
        angular_path([(radar_cx, radar_cy), (end_x, end_y)], gray_level(5), 3, 1)
        module_rect(end_x - 20, end_y - 16, 40, 32, gray_level(5 if index < axis_count else 3), gray_level(5), 1)
    if axis_count >= 5:
        points = [(radar_cx, radar_cy - 84), (radar_cx + 100, radar_cy - 24), (radar_cx + 68, radar_cy + 80), (radar_cx - 68, radar_cy + 76), (radar_cx - 108, radar_cy - 20), (radar_cx, radar_cy - 84)]
        angular_path(points, PALETTE["route"], 4, ease((p - 0.44) / 0.16))
    quad_x, quad_y = 1220, 116
    for row in range(2):
        for col in range(2):
            index = row * 2 + col
            fill = gray_level(2 + index) if p > 0.48 else gray_level(1 + index)
            module_rect(quad_x + col * 144, quad_y + row * 112, 144, 112, fill, gray_level(5), 1)
            if p > 0.58 and index == 2:
                module_rect(quad_x + col * 144, quad_y + row * 112, 8, 112, PALETTE["route"], None)
    module_rect(quad_x, quad_y + 112, 292, 10, gray_level(5), None)
    module_rect(quad_x + 144, quad_y, 8, 224, gray_level(5), None)

    # Pricing/credit meters use fills declared by geometry, not inset bars.
    meter_x, meter_y = 80, 420
    meter_count = min(4, int(ease((p - 0.28) / 0.58) * 5))
    meter_level = min(4, int(ease((p - 0.30) / 0.56) * 5))
    for index in range(4):
        x = meter_x + index * 176
        module_rect(x, meter_y, 152, 52, gray_level(3), gray_level(5), 1)
        fill_width = 152 * (meter_level / 4 if index < meter_count else 0)
        module_rect(x, meter_y, fill_width, 52, gray_level(5), None)
        if index < meter_count and meter_level >= 3:
            module_rect(x + max(0, fill_width - 8), meter_y, 8, 52, PALETTE["route"], None)
        module_rect(x, meter_y + 52, 152, 28, gray_level(5 if index < meter_count else 3), None)

    # Workflow gravity routes to one selected home, then governance wraps it.
    selector_x, selector_y = 920, 480
    for row in range(3):
        for col in range(4):
            index = row * 4 + col
            fill = gray_level(2 + ((row + col) % 4))
            if p > 0.72 and index in {1, 6, 10}:
                fill = gray_level(5)
            if p > 0.76 and index in {3, 11}:
                fill = gray_level(4)
            module_rect(selector_x + col * 76, selector_y + row * 48, 68, 40, fill, gray_level(5), 1)
            if p > 0.78 and index in {1, 6, 10}:
                module_rect(selector_x + col * 76, selector_y + row * 48, 8, 40, PALETTE["route"], None)
    selected_path = [(selector_x + 38, selector_y + 20), (selector_x + 190, selector_y + 68), (home_x + 260, home_y + 198)]
    angular_path(selected_path, PALETTE["route"], 5, ease((p - 0.78) / 0.16))
    wrap_on = p > 0.82
    for row, y in enumerate((442, 494, 546)):
        module_rect(1260, y, 292, 52, gray_level(2 + row), gray_level(6), 1)
        if wrap_on:
            module_rect(1260, y, 8, 52, PALETTE["route"], None)

    # Evidence floor occupies the lower band without fake text rows.
    for row in range(3):
        for col in range(24):
            index = row * 24 + col
            fill = gray_level(2 + ((index + row) % 4))
            module_rect(64 + col * 64, 628 + row * 24, 52, 20, fill, None)
            if index <= active * 5 and index % 9 == 0:
                module_rect(64 + col * 64, 628 + row * 24, 8, 20, PALETTE["route"], None)
    return img


def render_plugin_masonry_frame(
    second: float,
    args: argparse.Namespace,
    fonts: dict[str, ImageFont.ImageFont],
) -> Image.Image:
    width, height = args.width, args.height
    sx = width / 1280
    sy = height / 720

    def pt(x: float, y: float) -> tuple[int, int]:
        return round(x * sx), round(y * sy)

    def box(x1: float, y1: float, x2: float, y2: float) -> tuple[int, int, int, int]:
        return round(x1 * sx), round(y1 * sy), round(x2 * sx), round(y2 * sy)

    canvas_width = round(width * 1.5)
    img = Image.new("RGB", (canvas_width, height), hex_to_rgb(PALETTE["paper"]))
    draw = ImageDraw.Draw(img)
    p = clamp(second / max(args.duration, 0.001))
    active = min(9, int(ease((p - 0.04) / 0.78) * 10))
    draw_masonry_megacanvas_base(draw, second, args)

    def module_rect(x: float, y: float, w: float, h: float, fill: str, stroke: str | None = None, width_px: int = 1) -> None:
        rounded_rect(draw, box(x, y, x + max(1, w), y + max(1, h)), fill, stroke, width=width_px, radius=0)

    def angular_path(points: list[tuple[float, float]], fill: str, width_px: int, progress: float = 1.0) -> None:
        draw_polyline(draw, [pt(x, y) for x, y in points], fill, width_px, progress)

    for trace_points in (
        [(80, 96), (312, 96), (420, 132)],
        [(360, 324), (740, 324), (820, 252)],
        [(820, 636), (1144, 636), (1216, 596)],
        [(1184, 420), (1500, 420), (1576, 468)],
    ):
        angular_path(trace_points, gray_level(5), 2, 1.0)

    # Installable plugin bundle: small capability blocks snap into one square-edged pack.
    block_count = min(9, int(ease((p - 0.02) / 0.24) * 10))
    bundle_x, bundle_y = 112, 128
    for index in range(9):
        col = index % 3
        row = index // 3
        entry_shift = max(0, 1 - ease((p - 0.02 - index * 0.018) / 0.12))
        x = bundle_x + col * 64 - 72 * entry_shift
        y = bundle_y + row * 56 + (40 if index % 2 else -40) * entry_shift
        fill = PALETTE["route"] if index < block_count and index in {0, 4, 8} else gray_level(2 + index % 4)
        module_rect(x, y, 56, 48, fill, gray_level(5), 1)
        module_rect(x, y, 10, 48, gray_level(5), None)
        module_rect(x + 18, y + 16, 26, 8, gray_level(1 + index % 4), None)
    pack_outline_on = p > 0.10
    draw.rectangle(
        box(104, 120, 312, 304),
        outline=hex_to_rgb(PALETTE["route"] if pack_outline_on else gray_level(5)),
        width=4 if pack_outline_on else 1,
    )
    angular_path([(312, 212), (420, 212), (468, 220)], PALETTE["route"], 6, ease((p - 0.18) / 0.16))

    # Open bundle: detachable modules remain flush to the pack boundary.
    opened = p > 0.18
    module_rect(468, 112, 272, 184, gray_level(1), gray_level(5), 1)
    module_rect(468 - 52 * ease((p - 0.18) / 0.18), 112, 52, 184, PALETTE["route"] if opened else gray_level(3), gray_level(5), 1)
    module_rect(688 + 52 * ease((p - 0.18) / 0.18), 112, 52, 184, gray_level(5), gray_level(6), 1)
    module_count = min(5, int(ease((p - 0.22) / 0.24) * 6))
    module_specs = [(500, 140, 64, 52), (580, 140, 84, 52), (500, 208, 72, 52), (592, 208, 72, 52), (676, 172, 44, 80)]
    for index, (x, y, w, h) in enumerate(module_specs):
        fill = PALETTE["route"] if index < module_count and index in {0, 3} else PALETTE["attribute"] if index < module_count and index == 4 else gray_level(2 + index % 4)
        module_rect(x, y, w, h, fill, gray_level(5), 1)
        module_rect(x, y, 8, h, gray_level(5), None)
        module_rect(x + 16, y + 16, max(16, w - 32), 8, gray_level(1 + index % 4), None)

    # Provider package surfaces: manifest, marketplace allowlist, and npm/runtime drop.
    provider_x = 880
    provider_on = p > 0.32
    for surface_index, y in enumerate((108, 284, 460)):
        module_rect(provider_x, y, 264, 132, gray_level(1 + surface_index), gray_level(5), 1)
        module_rect(provider_x, y, 16, 132, [PALETTE["route"], PALETTE["damage"], PALETTE["attribute"]][surface_index] if provider_on else gray_level(5), None)
    for row in range(5):
        width_px = 172 - row * 18
        fill = PALETTE["route"] if provider_on and row in {1, 3} else gray_level(2 + row % 4)
        module_rect(provider_x + 40, 132 + row * 18, width_px, 12, fill, None)
        module_rect(provider_x + 224, 130 + row * 18, 20, 16, gray_level(5 if provider_on and row in {1, 3} else 3), None)
    gate_close = ease((p - 0.40) / 0.20)
    module_rect(provider_x + 42, 318, 148, 44, gray_level(2), gray_level(5), 1)
    module_rect(provider_x + 208, 300, 28, 96, PALETTE["damage"] if p > 0.40 else gray_level(4), gray_level(6), 1)
    module_rect(provider_x + 42, 318, 166 * gate_close, 12, PALETTE["attribute"], None)
    module_rect(provider_x + 42, 350, 166 * gate_close, 12, PALETTE["attribute"], None)
    drop = ease((p - 0.50) / 0.22)
    module_rect(provider_x + 70, 420 + 92 * drop, 76, 52, PALETTE["route"] if p > 0.50 else gray_level(3), gray_level(5), 1)
    module_rect(provider_x + 48, 538, 184, 42, gray_level(3), gray_level(5), 1)
    module_rect(provider_x + 48, 538, 184 * drop, 42, PALETTE["attribute"], None)

    # Governance: one approved pack fans out to teams while version arrows update it.
    gov_x, gov_y = 1220, 116
    fanout_on = p > 0.60
    install_count = min(6, int(ease((p - 0.60) / 0.22) * 7))
    module_rect(gov_x, gov_y, 128, 112, PALETTE["route"] if fanout_on else gray_level(3), gray_level(6), 2)
    for index in range(6):
        x = gov_x + 204 + (index % 3) * 88
        y = gov_y + (index // 3) * 88
        fill = PALETTE["route"] if index < install_count else gray_level(2 + index % 4)
        module_rect(x, y, 56, 48, fill, gray_level(5), 1)
        if fanout_on:
            angular_path([(gov_x + 128, gov_y + 56), (x, y + 24)], PALETTE["route"] if index < install_count else gray_level(5), 3, ease((p - 0.60 - index * 0.02) / 0.12))
    version_level = min(4, int(ease((p - 0.66) / 0.22) * 5))
    for index in range(4):
        y = gov_y + 228 + index * 42
        fill = PALETTE["attribute"] if index < version_level else gray_level(2 + index)
        module_rect(gov_x, y, 220, 26, fill, gray_level(5), 1)
        angular_path([(gov_x + 236, y + 13), (gov_x + 300, y + 13)], fill, 4, ease((p - 0.66 - index * 0.035) / 0.12))
    module_rect(gov_x + 324, gov_y + 220, 36, 210, PALETTE["damage"] if p > 0.56 else gray_level(4), gray_level(6), 1)
    for slot in range(5):
        module_rect(gov_x + 332, gov_y + 238 + slot * 36, 20, 24, PALETTE["route"] if slot < version_level else gray_level(2 + slot), None)

    # Cost/risk split: efficient defaults stay narrow; noisy plugin spreads everywhere.
    split_x, split_y = 1216, 468
    good_bad_on = p > 0.72
    module_rect(split_x, split_y, 148, 132, gray_level(2), gray_level(5), 1)
    module_rect(split_x + 188, split_y, 148, 132, "#ffccd5" if good_bad_on else gray_level(2), PALETTE["damage"] if good_bad_on else gray_level(5), 1)
    for index in range(5):
        module_rect(split_x + 20, split_y + 20 + index * 20, 78 - index * 8, 10, PALETTE["route"] if good_bad_on and index < 3 else gray_level(3 + index % 3), None)
    noisy_level = min(6, int(ease((p - 0.64) / 0.32) * 7))
    for row in range(3):
        for col in range(3):
            index = row * 3 + col
            fill = PALETTE["damage"] if index < noisy_level else gray_level(2 + index % 4)
            module_rect(split_x + 208 + col * 36, split_y + 18 + row * 32, 28, 24, fill, None)
    cost_level = min(4, int(ease((p - 0.64) / 0.32) * 5))
    module_rect(split_x + 20, split_y + 152, 316, 36, gray_level(3), gray_level(5), 1)
    module_rect(split_x + 20, split_y + 152, 316 * (cost_level / 4), 36, PALETTE["damage"] if cost_level >= 3 else PALETTE["attribute"], None)

    # Final install stamp reuses the same pack geometry, now entering the runtime.
    if p > 0.84:
        module_rect(420, 556, 180, 64, gray_level(5), gray_level(6), 1)
        for index in range(4):
            module_rect(420 + index * 45, 556, 45, 64, PALETTE["route"] if index in {0, 2} else gray_level(2 + index), gray_level(6), 1)
        angular_path([(600, 588), (712, 588), (776, 540), (860, 540)], PALETTE["route"], 7, ease((p - 0.84) / 0.14))
        module_rect(860, 508, 172, 72, gray_level(1), PALETTE["route"], 3)

    # Dense but quiet floor marks keep the mute-test readable without captions.
    for row in range(2):
        for col in range(24):
            index = row * 24 + col
            x = 64 + col * 64
            y = 652 + row * 24
            fill = PALETTE["route"] if index <= active * 4 and index % 8 == 0 else gray_level(2 + index % 4)
            if index % 13 == 0 and p > 0.62:
                fill = PALETTE["attribute"]
            if index % 17 == 0 and p > 0.74:
                fill = PALETTE["damage"]
            module_rect(x, y, 52, 16, fill, None)
    return img


def render_guardrail_masonry_frame(
    second: float,
    args: argparse.Namespace,
    fonts: dict[str, ImageFont.ImageFont],
) -> Image.Image:
    width, height = args.width, args.height
    sx = width / 1280
    sy = height / 720

    def pt(x: float, y: float) -> tuple[int, int]:
        return round(x * sx), round(y * sy)

    def box(x1: float, y1: float, x2: float, y2: float) -> tuple[int, int, int, int]:
        return round(x1 * sx), round(y1 * sy), round(x2 * sx), round(y2 * sy)

    canvas_width = round(width * 1.5)
    img = Image.new("RGB", (canvas_width, height), hex_to_rgb(PALETTE["paper"]))
    draw = ImageDraw.Draw(img)
    p = clamp(second / max(args.duration, 0.001))
    active = min(8, int(ease((p - 0.04) / 0.78) * 9))
    draw_masonry_megacanvas_base(draw, second, args)

    def module_rect(x: float, y: float, w: float, h: float, fill: str, stroke: str | None = None, width_px: int = 1) -> None:
        rounded_rect(draw, box(x, y, x + w, y + h), fill, stroke, width=width_px, radius=0)

    def angular_path(points: list[tuple[float, float]], fill: str, width_px: int, progress: float = 1.0) -> None:
        draw_polyline(draw, [pt(x, y) for x, y in points], fill, width_px, progress)

    # Agent loop under a hard shield gate.
    loop_points = [(540, 164), (700, 164), (784, 316), (700, 468), (540, 468), (456, 316), (540, 164)]
    for start, end in zip(loop_points, loop_points[1:]):
        draw.line([pt(*start), pt(*end)], fill=hex_to_rgb(gray_level(5)), width=4)
    angular_path(loop_points, PALETTE["route"], 3, ease((p - 0.06) / 0.40))
    for index, (x, y) in enumerate(loop_points[:-1]):
        fill = gray_level(5) if index <= active and index % 3 == 0 else gray_level(2 + index % 4)
        module_rect(x - 30, y - 28, 60, 56, fill, gray_level(5), 1)
        if index <= active and index % 3 == 0:
            module_rect(x - 30, y - 28, 5, 56, PALETTE["route"], None)
        module_rect(x - 16, y - 4, 32, 8, gray_level(1 + index % 4), None)
    module_rect(584, 268, 112, 96, gray_level(1), gray_level(5), 1)
    for row in range(3):
        for col in range(3):
            fill = gray_level(5) if active >= 2 and (row + col) % 3 == 0 else gray_level(2 + ((row + col) % 4))
            module_rect(604 + col * 26, 288 + row * 22, 18, 14, fill, None)
            if active >= 2 and (row + col) % 3 == 0:
                module_rect(604 + col * 26, 288 + row * 22, 4, 14, PALETTE["route"], None)

    gate_close = ease((p - 0.08) / 0.22)
    left_gate_x = 424 + 56 * (1 - gate_close)
    right_gate_x = 828 - 56 * (1 - gate_close)
    module_rect(left_gate_x, 116, 28, 408, gray_level(5), gray_level(6), 1)
    module_rect(right_gate_x, 116, 28, 408, gray_level(5), gray_level(6), 1)
    module_rect(left_gate_x, 116, 4, 408, PALETTE["damage"], None)
    module_rect(right_gate_x + 24, 116, 4, 408, PALETTE["damage"], None)
    module_rect(424, 116, 432 * gate_close, 8, gray_level(5), None)
    module_rect(424, 516, 432 * gate_close, 8, gray_level(5), None)
    for index in range(4):
        module_rect(524 + index * 52, 230 + (index % 2) * 122, 40, 40, gray_level(2 + index), gray_level(5), 1)

    # Three inspection gates: input, output, and action.
    gate_ys = [164, 292, 420]
    for index, y in enumerate(gate_ys):
        gate_on = active >= index + 2
        lane_color = [PALETTE["route"], PALETTE["attribute"], PALETTE["damage"]][index]
        lane_fill = [gray_level(5), gray_level(4), gray_level(5)][index]
        module_rect(96, y - 34, 140, 68, gray_level(1 + index), gray_level(5), 1)
        for col in range(4):
            cell_active = gate_on and col <= active - index - 1
            fill = lane_fill if cell_active else gray_level(2 + (col + index) % 4)
            module_rect(112 + col * 28, y - 14, 22, 28, fill, None)
            if cell_active:
                module_rect(112 + col * 28, y - 14, 6, 28, lane_color, None)
        module_rect(280, y - 46, 44, 92, lane_fill if gate_on else gray_level(3), gray_level(6), 1)
        if gate_on:
            module_rect(280, y - 46, 8, 92, lane_color, None)
        module_rect(324, y - 10, 120, 20, gray_level(5), None)
        if gate_on:
            angular_path([(324, y), (452, y), (456, 316)], lane_color, 3, 1)

    # Prompt suggestion versus hard policy gate.
    module_rect(104, 540, 160, 76, gray_level(2), gray_level(5), 1)
    for row in range(3):
        module_rect(120, 554 + row * 18, 92 + row * 18, 8, gray_level(4), None)
    policy_active = p > 0.28
    module_rect(304, 536, 36, 92, gray_level(5 if policy_active else 4), gray_level(6), 1)
    if policy_active:
        module_rect(304, 536, 8, 92, PALETTE["damage"], None)
    redact_active = p > 0.36
    module_rect(348, 562, 112, 36, gray_level(5 if redact_active else 3), None)
    if redact_active:
        module_rect(348, 562, 8, 36, PALETTE["route"], None)

    # Model Armor-like filters and risk score use only colorset1 gray/red levels.
    lane_start_y = 128
    filter_progress = ease((p - 0.28) / 0.32)
    for row in range(4):
        y = lane_start_y + row * 58
        width_px = 82 + filter_progress * (220 - row * 18)
        row_blocked = row in (0, 3) and p > 0.44
        fill = gray_level(5 if row_blocked else 2 + row)
        module_rect(932, y, width_px, 34, fill, None)
        if row_blocked:
            module_rect(932 + max(0, width_px - 8), y, min(8, width_px), 34, PALETTE["damage"], None)
        module_rect(1168, y, 44, 34, gray_level(5 if row in (0, 3) and p > 0.44 else 3), None)
        angular_path([(856, 316), (904, y + 16), (932, y + 16)], PALETTE["route"] if row % 2 == 0 else PALETTE["attribute"], 3, filter_progress)
    module_rect(930, 400, 300, 64, gray_level(3), gray_level(5), 1)
    risk_width = 300 * ease((p - 0.34) / 0.34)
    risk_high = risk_width > 185
    module_rect(930, 400, risk_width, 64, gray_level(5 if risk_high else 4), None)
    if risk_width > 0:
        module_rect(930 + max(0, risk_width - 8), 400, min(8, risk_width), 64, PALETTE["damage"] if risk_high else PALETTE["attribute"], None)
    for index in range(5):
        token_active = index <= active - 3
        module_rect(940 + index * 54, 478, 44, 34, gray_level(5 if token_active else 2 + index % 4), None)
        if token_active:
            module_rect(940 + index * 54, 478, 8, 34, PALETTE["damage"], None)

    # Policy matrix plus explicit block/redact/route/escalate outcomes.
    matrix_x, matrix_y = 1316, 104
    for row in range(3):
        for col in range(3):
            score = row * 3 + col
            fill = gray_level(2 + (score % 4))
            if p > 0.42 and score in (2, 4):
                fill = PALETTE["attribute"]
            high_risk_cell = p > 0.50 and score in (6, 7, 8)
            if high_risk_cell:
                fill = gray_level(5)
            module_rect(matrix_x + col * 56, matrix_y + row * 56, 52, 52, fill, gray_level(5), 1)
            if high_risk_cell:
                module_rect(matrix_x + col * 56, matrix_y + row * 56, 8, 52, PALETTE["damage"], None)
    outcome_y = 312
    for index in range(4):
        outcome_active = active >= index + 4
        accent = [PALETTE["damage"], PALETTE["route"], PALETTE["attribute"], gray_level(5)][index]
        fill = gray_level(5 if outcome_active else 2 + index)
        module_rect(1272 + index * 92, outcome_y, 76, 58, fill, gray_level(5), 1)
        if outcome_active and index < 3:
            module_rect(1272 + index * 92, outcome_y, 8, 58, accent, None)
        module_rect(1284 + index * 92, outcome_y + 14, 52, 8, gray_level(1 + index % 4), None)
        module_rect(1284 + index * 92, outcome_y + 34, 52, 8, gray_level(5), None)

    # Human approval over protected code-assistant actions.
    approval_on = p > 0.62
    module_rect(1280, 424, 224, 150, gray_level(5 if approval_on else 3), gray_level(6), 1)
    if approval_on:
        module_rect(1280, 424, 6, 150, PALETTE["attribute"], None)
    module_rect(1304, 448, 176, 20, gray_level(1), None)
    module_rect(1304, 484, 68, 54, gray_level(5 if approval_on else 2), None)
    module_rect(1392, 484, 64, 54, gray_level(5) if p > 0.74 else gray_level(2), None)
    if p > 0.74:
        module_rect(1392, 484, 6, 54, PALETTE["route"], None)
    for index, (x, y) in enumerate([(1544, 432), (1624, 432), (1704, 432)]):
        risk_active = p > 0.56 + index * 0.06
        fill = gray_level(5 if risk_active else 2 + index)
        module_rect(x, y, 64, 72, fill, gray_level(5), 1)
        if risk_active:
            module_rect(x, y, 8, 72, PALETTE["damage"], None)
        module_rect(x + 12, y + 14, 40, 10, gray_level(1 + index % 4), None)
        module_rect(x + 12, y + 38, 40, 10, gray_level(5), None)

    # Positive path passes while blocked path terminates; scale shows safety versus friction.
    angular_path([(940, 612), (1096, 612), (1248, 612)], PALETTE["route"], 4, ease((p - 0.68) / 0.18))
    angular_path([(940, 652), (1076, 652), (1076, 628)], PALETTE["damage"], 4, ease((p - 0.50) / 0.20))
    stop_active = p > 0.50
    module_rect(1060, 620, 52, 52, gray_level(5 if stop_active else 3), gray_level(6), 1)
    if stop_active:
        module_rect(1060, 620, 8, 52, PALETTE["damage"], None)
    scale_x, scale_y = 1492, 612
    module_rect(scale_x, scale_y, 240, 12, gray_level(5), None)
    module_rect(scale_x + 112, scale_y - 54, 16, 108, gray_level(6), None)
    left_h = 46 + 30 * ease((p - 0.76) / 0.16)
    right_h = 74 - 24 * ease((p - 0.76) / 0.16)
    module_rect(scale_x + 20, scale_y - left_h, 76, left_h, gray_level(5), None)
    module_rect(scale_x + 20, scale_y - left_h, 8, left_h, PALETTE["route"], None)
    module_rect(scale_x + 144, scale_y - right_h, 76, right_h, gray_level(5), None)
    module_rect(scale_x + 144, scale_y - right_h, 8, right_h, PALETTE["damage"], None)

    # Source-bound evidence floor keeps the bottom half occupied without labels.
    for row in range(2):
        for col in range(16):
            index = row * 16 + col
            route_cell = index <= active * 3 and index % 7 == 0
            damage_cell = index in (6, 13, 21) and p > 0.55
            fill = gray_level(2 + index % 4)
            module_rect(64 + col * 48, 656 + row * 32, 38, 22, fill, None)
            if route_cell or damage_cell:
                module_rect(64 + col * 48, 656 + row * 32, 6, 22, PALETTE["damage"] if damage_cell else PALETTE["route"], None)
    return img


def render_skill_package_masonry_frame(
    second: float,
    args: argparse.Namespace,
    fonts: dict[str, ImageFont.ImageFont],
) -> Image.Image:
    width, height = args.width, args.height
    sx = width / 1280
    sy = height / 720

    def pt(x: float, y: float) -> tuple[int, int]:
        return round(x * sx), round(y * sy)

    def box(x1: float, y1: float, x2: float, y2: float) -> tuple[int, int, int, int]:
        return round(x1 * sx), round(y1 * sy), round(x2 * sx), round(y2 * sy)

    canvas_width = round(width * 1.5)
    img = Image.new("RGB", (canvas_width, height), hex_to_rgb(PALETTE["paper"]))
    draw = ImageDraw.Draw(img)
    p = clamp(second / max(args.duration, 0.001))
    draw_masonry_megacanvas_base(draw, second, args)

    def module_rect(x: float, y: float, w: float, h: float, fill: str, stroke: str | None = None, width_px: int = 1) -> None:
        rounded_rect(draw, box(x, y, x + max(1, w), y + max(1, h)), fill, stroke, width=width_px, radius=0)

    def angular_path(points: list[tuple[float, float]], fill: str, width_px: int, progress: float = 1.0) -> None:
        draw_polyline(draw, [pt(x, y) for x, y in points], fill, width_px, progress)

    # Skill card stack: a reusable capability fans open only when invoked.
    card_count = min(7, int(ease((p - 0.03) / 0.20) * 8))
    for index in range(7):
        x = 92 + index * 24
        y = 120 + index * 18
        card_active = index < card_count and index in {0, 3, 6}
        fill = gray_level(5 if card_active else 2 + index % 4)
        draw.rectangle(box(x, y, x + 168, y + 104), outline=hex_to_rgb(gray_level(5)), width=1)
        module_rect(x, y, 16, 104, gray_level(5), None)
        if card_active:
            module_rect(x, y, 8, 104, PALETTE["route"], None)
        for row in range(4):
            band_fill = fill if row == 0 and index < card_count else gray_level(1 + (row + index) % 4)
            module_rect(x, y + row * 26, max(44, 168 - row * 18), 24, band_fill, None)
            if row == 0 and card_active:
                module_rect(x, y + row * 26, 8, 24, PALETTE["route"], None)

    # Long prompt wall collapses into one scoped skill card.
    collapse = ease((p - 0.16) / 0.24)
    prompt_strips = max(1, 12 - int(collapse * 11))
    for row in range(12):
        strip_w = 280 - row * 10
        x = 432 - 236 * collapse
        y = 96 + row * 24 + (6 - row) * 6 * collapse
        trimmed_strip = row >= prompt_strips and p > 0.26
        fill = gray_level(5 if trimmed_strip else 2 + row % 4)
        module_rect(x, y, max(44, strip_w * (1 - 0.54 * collapse)), 14, fill, None)
        if trimmed_strip:
            module_rect(x, y, 6, 14, PALETTE["damage"], None)
    module_rect(448, 412, 232, 92, gray_level(1), gray_level(5), 1)
    scoped_active = collapse > 0.72
    scoped_width = 232 * collapse
    module_rect(448, 412, scoped_width, 92, gray_level(5 if scoped_active else 3), None)
    if scoped_active and scoped_width > 0:
        module_rect(448 + max(0, scoped_width - 8), 412, min(8, scoped_width), 92, PALETTE["route"], None)
    angular_path([(304, 236), (408, 292), (448, 458)], PALETTE["route"], 6, collapse)

    # Compatible folder structures align around SKILL.md, scripts, references, and assets.
    folder_on = p > 0.34
    for group in range(3):
        x = 820 + group * 180
        module_rect(x, 108, 136, 228, gray_level(1 + group), gray_level(5), 1)
        for row in range(5):
            y = 108 + row * 44
            row_active = folder_on and row in {0, 2}
            fill = gray_level(5 if row_active else 2 + (row + group) % 4)
            module_rect(x, y, 104 - row * 8, 28, fill, gray_level(5), 1)
            if row_active:
                module_rect(x, y, 6, 28, PALETTE["route"], None)
            module_rect(x + 104, y, 32, 28, gray_level(3 + (row + group) % 3), gray_level(5), 1)
            angular_path([(x + 104, y + 28), (x + 104, y + 40), (x + 136, y + 40)], gray_level(5), 2, 1)

    # Progressive disclosure: meter remains flat until the selected skill activates.
    activation = ease((p - 0.36) / 0.48)
    cost_level = min(4, int(activation * 5))
    module_rect(860, 420, 360, 48, gray_level(3), gray_level(5), 1)
    cost_width = 360 * (cost_level / 4)
    module_rect(860, 420, cost_width, 48, gray_level(5 if cost_level >= 4 else 4), None)
    if cost_width > 0:
        module_rect(860 + max(0, cost_width - 8), 420, min(8, cost_width), 48, PALETTE["route"] if cost_level >= 4 else PALETTE["attribute"], None)
    for mark in range(5):
        module_rect(868 + mark * 70, 484, 10, 40, gray_level(5), None)
    activation_on = activation > 0.15
    module_rect(772, 400, 52, 120, gray_level(5 if activation_on else 3), gray_level(6), 1)
    if activation_on:
        module_rect(772, 400, 8, 120, PALETTE["route"], None)
    angular_path([(680, 458), (772, 458), (860, 444)], PALETTE["route"], 6, activation)

    # Example skills, tool badges, and scripts snap onto the active workflow.
    example_count = min(5, int(ease((p - 0.46) / 0.36) * 6))
    for index in range(5):
        x = 1280 + (index % 3) * 84
        y = 108 + (index // 3) * 88
        example_active = index < example_count and index % 2 == 0
        fill = gray_level(5 if example_active else 2 + index % 4)
        module_rect(x, y, 64, 64, fill, gray_level(5), 1)
        if example_active:
            module_rect(x, y, 8, 64, PALETTE["route"], None)
        module_rect(x, y + 52, 64, 12, gray_level(5), None)
    badge_count = min(6, int(ease((p - 0.64) / 0.20) * 7))
    for index in range(6):
        fill = gray_level(5) if index < badge_count else gray_level(2 + index % 4)
        module_rect(1268 + index * 44, 340, 32, 40, fill, gray_level(5), 1)
        if index < badge_count:
            module_rect(1268 + index * 44, 340, 5, 40, PALETTE["attribute"], None)
    script_count = min(4, int(ease((p - 0.66) / 0.18) * 5))
    for row in range(4):
        script_active = row < script_count
        fill = gray_level(5 if script_active else 2 + row)
        module_rect(1276, 416 + row * 34, 240 - row * 32, 18, fill, None)
        if script_active:
            module_rect(1276, 416 + row * 34, 6, 18, PALETTE["route"], None)
    read_level = min(4, int(ease((p - 0.54) / 0.34) * 5))
    for index in range(4):
        fill = gray_level(5) if index < read_level else gray_level(2 + index)
        module_rect(1572 + index * 36, 416, 28, 88, fill, gray_level(5), 1)
        if index < read_level:
            module_rect(1572 + index * 36, 416, 5, 88, PALETTE["attribute"], None)

    # Bloated skill gets trimmed into a scoped reusable workflow.
    trim = ease((p - 0.72) / 0.20)
    module_rect(1516, 112, 232, 296, gray_level(2), gray_level(5), 1)
    for row in range(12):
        w = 176 - (row % 4) * 20
        trim_line_active = trim > 0.45 and row > 7
        module_rect(1516, 112 + row * 24, w * (1 - 0.58 * trim), 20, gray_level(5 if trim_line_active else 3 + row % 3), None)
        if trim_line_active:
            module_rect(1516, 112 + row * 24, 6, 20, PALETTE["damage"], None)
    module_rect(1516 + 172 * trim, 112, 28, 296, gray_level(5), gray_level(6), 1)
    module_rect(1516 + 172 * trim, 112, 4, 296, PALETTE["damage"], None)
    workflow_active = trim > 0.70
    module_rect(1516, 448, 184, 76, gray_level(5 if workflow_active else 3), gray_level(6), 1)
    if workflow_active:
        module_rect(1516, 448, 8, 76, PALETTE["route"], None)

    final_on = p > 0.84
    if final_on:
        module_rect(420, 572, 360, 64, gray_level(5), gray_level(6), 1)
        for index in range(6):
            stamp_active = index in {0, 5}
            module_rect(420 + index * 60, 572, 60, 64, gray_level(5 if stamp_active else 2 + index % 4), gray_level(6), 1)
            if stamp_active:
                module_rect(420 + index * 60, 572, 8, 64, PALETTE["route"], None)
        angular_path([(780, 604), (944, 604), (1108, 560), (1280, 560)], PALETTE["route"], 7, ease((p - 0.84) / 0.14))

    for row in range(2):
        for col in range(24):
            index = row * 24 + col
            route_cell = index <= int(ease((p - 0.12) / 0.66) * 46) and index % 8 == 0
            attribute_cell = index % 13 == 0 and p > 0.58
            damage_cell = index % 17 == 0 and p > 0.74
            fill = gray_level(2 + index % 4)
            module_rect(64 + col * 64, 652 + row * 24, 52, 16, fill, None)
            if route_cell or attribute_cell or damage_cell:
                accent = PALETTE["damage"] if damage_cell else PALETTE["attribute"] if attribute_cell else PALETTE["route"]
                module_rect(64 + col * 64, 652 + row * 24, 6, 16, accent, None)
    return img


def render_systems_flow_frame(
    second: float,
    args: argparse.Namespace,
    fonts: dict[str, ImageFont.ImageFont],
) -> Image.Image:
    width, height = args.width, args.height
    sx = width / 1280
    sy = height / 720

    def pt(x: float, y: float) -> tuple[int, int]:
        return round(x * sx), round(y * sy)

    def box(x1: float, y1: float, x2: float, y2: float) -> tuple[int, int, int, int]:
        return round(x1 * sx), round(y1 * sy), round(x2 * sx), round(y2 * sy)

    low_text_masonry = bool(args.masonry_layout)
    canvas_width = round(width * 1.5) if low_text_masonry else width
    img = Image.new("RGB", (canvas_width, height), hex_to_rgb(PALETTE["paper"]))
    draw = ImageDraw.Draw(img)
    p = second / args.duration

    if low_text_masonry and skill_package_requested(args):
        return render_skill_package_masonry_frame(second, args, fonts)

    if low_text_masonry and harness_requested(args):
        return render_harness_masonry_frame(second, args, fonts)

    if low_text_masonry and hook_requested(args):
        return render_hook_masonry_frame(second, args, fonts)

    if low_text_masonry and agent_loop_requested(args):
        return render_agent_loop_masonry_frame(second, args, fonts)

    if low_text_masonry:
        draw_masonry_megacanvas_base(draw, second, args)
    else:
        rounded_rect(draw, box(55, 112, 360, 602), "#ffffff", "#cfcfcf", radius=14)
        rounded_rect(draw, box(390, 112, 895, 602), "#ffffff", "#cfcfcf", radius=14)
        rounded_rect(draw, box(925, 112, 1225, 602), "#ffffff", "#cfcfcf", radius=14)
        text(draw, pt(84, 145), "INTAKE", fonts["small"], PALETTE["muted"], "lm")
        text(draw, pt(420, 145), "PIPELINE", fonts["small"], PALETTE["muted"], "lm")
        text(draw, pt(955, 145), "CONTROL", fonts["small"], PALETTE["muted"], "lm")

    system_labels = systems_flow_labels(args)

    # Intake sources and event bus.
    for idx, (x, y, label, color) in enumerate(
        [
            (135, 245, compact_label(system_labels[0], 14), PALETTE["route"]),
            (135, 350, compact_label(system_labels[1], 14), PALETTE["damage"]),
            (135, 455, compact_label(system_labels[2], 14), PALETTE["attribute"]),
        ]
    ):
        active = ease((p - 0.04 - idx * 0.07) / 0.12)
        source_fill = gray_level(2 + idx) if low_text_masonry else "#ffffff"
        rounded_rect(draw, box(x - 64, y - 32, x + 64, y + 32), source_fill, color if active > 0.1 else PALETTE["line"], radius=0 if low_text_masonry else 12)
        if low_text_masonry:
            rounded_rect(draw, box(x - 64, y - 32, x - 56, y + 32), color if active > 0.1 else PALETTE["line"], None, radius=0)
            rounded_rect(draw, box(x + 56, y - 32, x + 64, y + 32), gray_level(4), None, radius=0)
        else:
            text(draw, pt(x, y + 2), label, fonts["small"], PALETTE["ink"], "mm")

    bus = box(226, 214, 322, 486)
    rounded_rect(draw, bus, "#e7e7e7", PALETTE["route"], radius=0 if low_text_masonry else 16)
    if low_text_masonry:
        rounded_rect(draw, box(226, 214, 234, 486), PALETTE["route"], None, radius=0)
        rounded_rect(draw, box(314, 214, 322, 486), gray_level(4), None, radius=0)
    else:
        text(draw, pt(274, 350), compact_label(system_labels[3], 12), fonts["small"], PALETTE["route"], "mm")

    # Pipeline components.
    queue_box = box(440, 235, 570, 465)
    rounded_rect(draw, queue_box, gray_level(1) if low_text_masonry else "#ffffff", PALETTE["line"], radius=0 if low_text_masonry else 14)
    if not low_text_masonry:
        text(draw, pt(505, 205), compact_label(system_labels[4], 18), fonts["small"], PALETTE["ink"], "mm")
    filled_slots = min(7, max(0, int(ease((p - 0.18) / 0.32) * 8)))
    for idx in range(8):
        slot_y = 248 + idx * 25
        fill = PALETTE["route"] if idx < filled_slots else "#cfcfcf"
        rounded_rect(draw, box(458, slot_y, 552, slot_y + 15), fill, None, radius=0)

    worker_active = ease((p - 0.38) / 0.24)
    for idx, y in enumerate([262, 350, 438]):
        pulse = 0.5 + 0.5 * math.sin((p * 18 + idx) * math.pi)
        outline = PALETTE["defense"] if worker_active > 0.2 else PALETTE["line"]
        rounded_rect(draw, box(625, y - 34, 805, y + 34), "#e7e7e7", outline, width=3, radius=0 if low_text_masonry else 14)
        if low_text_masonry:
            rounded_rect(draw, box(625, y - 34, 633, y + 34), outline, None, radius=0)
            rounded_rect(draw, box(797, y - 34, 805, y + 34), gray_level(4), None, radius=0)
        else:
            text(draw, pt(715, y - 6), f"{compact_label(system_labels[5], 14)} {idx + 1}", fonts["small"], PALETTE["ink"], "mm")
        if worker_active > 0.2:
            draw.ellipse(
                box(764 - 8 * pulse, y + 10 - 8 * pulse, 764 + 8 * pulse, y + 10 + 8 * pulse),
                fill=hex_to_rgb(PALETTE["defense"]),
            )

    rounded_rect(draw, box(810, 304, 912, 396), "#ffccd5", PALETTE["damage"], radius=0 if low_text_masonry else 14)
    if low_text_masonry:
        rounded_rect(draw, box(810, 304, 818, 396), PALETTE["damage"], None, radius=0)
        rounded_rect(draw, box(904, 304, 912, 396), gray_level(4), None, radius=0)
    else:
        text(draw, pt(861, 350), compact_label(system_labels[6], 13), fonts["small"], PALETTE["damage"], "mm")

    # Control plane.
    rounded_rect(draw, box(970, 185, 1180, 255), "#ffccd5", PALETTE["tradeoff"], radius=0 if low_text_masonry else 12)
    if not low_text_masonry:
        text(draw, pt(1075, 211), compact_label(system_labels[7], 18), fonts["small"], PALETTE["tradeoff"], "mm")
        text(draw, pt(1075, 235), "backoff + cap", fonts["small"], PALETTE["ink"], "mm")
    rounded_rect(draw, box(970, 300, 1180, 370), "#ffccd5", PALETTE["tradeoff"], radius=0 if low_text_masonry else 12)
    if not low_text_masonry:
        text(draw, pt(1075, 326), compact_label(system_labels[8], 18), fonts["small"], PALETTE["tradeoff"], "mm")
        text(draw, pt(1075, 350), "inspect later", fonts["small"], PALETTE["ink"], "mm")
    rounded_rect(draw, box(970, 420, 1180, 535), gray_level(1) if low_text_masonry else "#ffffff", PALETTE["line"], radius=0 if low_text_masonry else 12)
    if not low_text_masonry:
        text(draw, pt(1075, 448), compact_label(system_labels[9], 18), fonts["small"], PALETTE["ink"], "mm")
    metric_points: list[tuple[int, int]] = []
    for idx in range(12):
        x = 995 + idx * 14
        y = 504 - (28 + 22 * math.sin(idx * 0.62 + p * 3.0) + 16 * ease((p - 0.45) / 0.25))
        metric_points.append(pt(x, y))
    if len(metric_points) > 1:
        draw.line(metric_points, fill=hex_to_rgb(PALETTE["route"]), width=4)

    if low_text_masonry:
        board_x = 1212
        active_cols = max(1, min(8, int(ease((p - 0.44) / 0.30) * 8)))
        for row in range(5):
            for col in range(8):
                level = 1 + ((row + col) % 4)
                fill = PALETTE["route"] if col < active_cols and row in (1, 3) else gray_level(level)
                rounded_rect(draw, box(board_x + col * 36, 124 + row * 36, board_x + col * 36 + 28, 152 + row * 36), fill, None, radius=0)
        for row, y in enumerate((392, 432, 472, 512, 552, 592)):
            bar_w = 56 + int(ease((p - 0.52 - row * 0.035) / 0.18) * (180 - row * 16))
            rounded_rect(draw, box(1212, y, 1212 + bar_w, y + 18), PALETTE["damage"] if row in (1, 4) else gray_level(4), None, radius=0)
        for row in range(3):
            for col in range(4):
                cell_on = ease((p - 0.50 - (row + col) * 0.025) / 0.16) > 0.35
                fill = PALETTE["damage"] if cell_on and (row + col) % 3 == 0 else (gray_level(5) if cell_on else gray_level(3))
                rounded_rect(draw, box(1416 + col * 32, 488 + row * 32, 1440 + col * 32, 512 + row * 32), fill, None, radius=0)

    # Main and branch paths.
    main_path = [pt(199, 350), pt(274, 350), pt(440, 350), pt(570, 350), pt(625, 350), pt(805, 350), pt(861, 350)]
    retry_path = [pt(805, 350), pt(925, 220), pt(970, 220)]
    dlq_path = [pt(805, 350), pt(925, 335), pt(970, 335)]
    feedback_path = [pt(1075, 420), pt(1075, 575), pt(270, 575), pt(270, 486)]
    draw_polyline(draw, main_path, PALETTE["line"], 4, 1)
    draw_polyline(draw, retry_path, PALETTE["line"], 3, 1)
    draw_polyline(draw, dlq_path, PALETTE["line"], 3, 1)
    draw_polyline(draw, feedback_path, PALETTE["line"], 3, 1)
    draw_polyline(draw, main_path, PALETTE["route"], 7, ease((p - 0.08) / 0.45))
    draw_polyline(draw, retry_path, PALETTE["damage"], 5, ease((p - 0.55) / 0.18))
    draw_polyline(draw, dlq_path, PALETTE["tradeoff"], 5, ease((p - 0.66) / 0.16))
    draw_polyline(draw, feedback_path, PALETTE["attribute"], 5, ease((p - 0.72) / 0.20))

    if p > 0.72:
        rounded_rect(draw, box(206, 500, 342, 588), "#e7e7e7", PALETTE["attribute"], width=3, radius=0 if low_text_masonry else 14)
        for y in (526, 546, 566):
            draw.line([pt(228, y), pt(320, y)], fill=hex_to_rgb(PALETTE["attribute"]), width=4)
        if not low_text_masonry:
            text(draw, pt(274, 514), compact_label(system_labels[10], 17), fonts["small"], PALETTE["attribute"], "mm")

    packet = point_on_polyline(main_path, ease((p - 0.08) / 0.45))
    draw_packet(draw, packet, PALETTE["gold"], 1, "" if low_text_masonry else "job", fonts)
    if p > 0.55:
        draw_packet(draw, point_on_polyline(retry_path, ease((p - 0.55) / 0.18)), PALETTE["damage"], 1, "" if low_text_masonry else "retry", fonts)
    if p > 0.66:
        draw_packet(draw, point_on_polyline(dlq_path, ease((p - 0.66) / 0.16)), PALETTE["tradeoff"], 1, "" if low_text_masonry else "fail", fonts)
    if p > 0.72:
        draw_packet(draw, point_on_polyline(feedback_path, ease((p - 0.72) / 0.20)), PALETTE["attribute"], 1, "" if low_text_masonry else "limit", fonts)

    # Bottom beat, with text limited to a short silent-draft cue.
    beats = [
        (0.00, "Events enter one shared contract."),
        (0.22, "Queue pressure becomes visible before workers saturate."),
        (0.43, "Workers transform jobs while metrics move."),
        (0.58, "Retry is a branch with a cap, not an invisible loop."),
        (0.74, "Feedback limits intake before the system fails."),
    ]
    current = beats[0][1]
    for threshold, beat in beats:
        if p >= threshold:
            current = beat

    return img


def render_state_machine_frame(
    second: float,
    args: argparse.Namespace,
    fonts: dict[str, ImageFont.ImageFont],
) -> Image.Image:
    width, height = args.width, args.height
    img = Image.new("RGB", (width, height), hex_to_rgb(PALETTE["paper"]))
    draw = ImageDraw.Draw(img)
    p = max(0.0, min(1.0, second / args.duration))
    active_zone = min(4, int(p * 5))
    draw_metro_megacanvas_base(draw, active_zone)

    state_labels, guard_labels = state_machine_labels(args)
    text(draw, (64, 128), "states", fonts["tiny"], PALETTE["muted"], "lm")
    text(draw, (368, 128), "guards", fonts["tiny"], PALETTE["muted"], "lm")
    text(draw, (888, 128), "terminal", fonts["tiny"], PALETTE["muted"], "lm")
    text(draw, (368, 468), "recovery", fonts["tiny"], PALETTE["tradeoff"], "lm")

    state_boxes = [
        (72, 232, 148, 68),
        (228, 232, 148, 68),
        (384, 232, 148, 68),
        (540, 232, 148, 68),
        (696, 232, 148, 68),
        (912, 232, 176, 68),
    ]
    states = [
        (compact_label(state_labels[0], 16), state_boxes[0], PALETTE["route"]),
        (compact_label(state_labels[1], 16), state_boxes[1], PALETTE["route"]),
        (compact_label(state_labels[2], 16), state_boxes[2], PALETTE["attribute"]),
        (compact_label(state_labels[3], 16), state_boxes[3], PALETTE["defense"]),
        (compact_label(state_labels[4], 16), state_boxes[4], PALETTE["defense"]),
        (compact_label(state_labels[5], 16), state_boxes[5], PALETTE["atlas"]),
    ]
    state_progress = ease((p - 0.04) / 0.50)
    active_index = min(len(states) - 1, int(state_progress * len(states)))

    main_points = [(x + w // 2, y + h // 2) for _, (x, y, w, h), _ in states]
    for a, b in zip(main_points, main_points[1:]):
        draw.line([a, b], fill=hex_to_rgb(PALETTE["line"]), width=5)
    draw_polyline(draw, main_points, PALETTE["route"], 9, state_progress)

    guard_specs = [
        (384, compact_label(guard_labels[0], 14), ease((p - 0.14) / 0.12)),
        (552, compact_label(guard_labels[1], 14), ease((p - 0.28) / 0.12)),
        (720, compact_label(guard_labels[2], 14), ease((p - 0.42) / 0.12)),
    ]
    for x, label, active in guard_specs:
        y = 160
        fill = gray_level(3 if active > 0.15 else 2)
        rounded_rect(draw, (x - 64, y - 24, x + 64, y + 24), fill, PALETTE["attribute"] if active > 0.15 else PALETTE["line"], radius=0)
        text(draw, (x, y + 2), label, fonts["small"], PALETTE["attribute"] if active > 0.15 else PALETTE["muted"], "mm")
        if active > 0.45:
            draw.line([(x, y + 24), (x, 232)], fill=hex_to_rgb(PALETTE["attribute"]), width=3)

    for idx, (label, (x, y, w, h), color) in enumerate(states):
        active = ease((p - 0.06 - idx * 0.08) / 0.10)
        fill = gray_level(2 if active < 0.55 else 3)
        outline = color if active > 0.1 else PALETTE["line"]
        rounded_rect(draw, (x, y, x + w, y + h), fill, outline, width=4 if active > 0.1 else 2, radius=0)
        text(draw, (x + w / 2, y + h / 2 + 4), label, fonts.get("label", fonts["small"]), PALETTE["ink"], "mm", 2, gray_level(1))
        if idx == active_index and p < 0.72:
            draw.ellipse((x + w / 2 - 10, y - 32, x + w / 2 + 10, y - 12), fill=hex_to_rgb(PALETTE["gold"]))

    rollback_visible = p > 0.58
    compensation_visible = p > 0.70
    terminal_visible = p > 0.82
    recovery_points = [(612, 300), (612, 528), (456, 528), (300, 528), (300, 300)]
    for a, b in zip(recovery_points, recovery_points[1:]):
        draw.line([a, b], fill=hex_to_rgb(PALETTE["line"]), width=4)
    if rollback_visible:
        draw_polyline(draw, recovery_points[:3], PALETTE["damage"], 7, ease((p - 0.58) / 0.18))
        rounded_rect(draw, (612, 488, 756, 552), "#ffccd5", PALETTE["damage"], width=3, radius=0)
        text(draw, (684, 514), "rollback", fonts.get("label", fonts["small"]), PALETTE["damage"], "mm", 2, gray_level(1))
        text(draw, (684, 536), "undo side effect", fonts["small"], PALETTE["ink"], "mm")
    if compensation_visible:
        draw_polyline(draw, recovery_points[1:], PALETTE["tradeoff"], 7, ease((p - 0.70) / 0.20))
        rounded_rect(draw, (432, 488, 576, 552), "#ffccd5", PALETTE["tradeoff"], width=3, radius=0)
        text(draw, (504, 514), "compensate", fonts.get("label", fonts["small"]), PALETTE["tradeoff"], "mm", 2, gray_level(1))
        text(draw, (504, 536), "restore invariant", fonts["small"], PALETTE["ink"], "mm")
    if terminal_visible:
        rounded_rect(draw, (904, 456, 1176, 556), gray_level(4), PALETTE["atlas"], width=3, radius=0)
        text(draw, (1040, 492), "terminal states", fonts.get("label", fonts["small"]), PALETTE["atlas"], "mm", 2, gray_level(1))
        text(draw, (1040, 524), "done or parked", fonts["small"], PALETTE["ink"], "mm")

    token = point_on_polyline(main_points, state_progress)
    draw.ellipse((token[0] - 13, token[1] - 13, token[0] + 13, token[1] + 13), fill=hex_to_rgb(PALETTE["gold"]))
    if rollback_visible:
        rollback_token = point_on_polyline(recovery_points, ease((p - 0.58) / 0.32))
        draw.ellipse((rollback_token[0] - 10, rollback_token[1] - 10, rollback_token[0] + 10, rollback_token[1] + 10), fill=hex_to_rgb(PALETTE["tradeoff"]))

    draw_meter(draw, (72, 452, 248, 552), "coverage", state_progress, PALETTE["route"], fonts)
    draw_meter(draw, (904, 344, 1080, 432), "guard pass", ease((p - 0.20) / 0.42), PALETTE["attribute"], fonts)

    return img


def render_comparison_matrix_frame(
    second: float,
    args: argparse.Namespace,
    fonts: dict[str, ImageFont.ImageFont],
) -> Image.Image:
    width, height = args.width, args.height
    img = Image.new("RGB", (width, height), hex_to_rgb(PALETTE["paper"]))
    draw = ImageDraw.Draw(img)
    p = second / args.duration


    rounded_rect(draw, (55, 112, 1220, 606), "#ffffff", "#cfcfcf", radius=14)
    text(draw, (88, 145), "OPTIONS", fonts["small"], PALETTE["muted"], "lm")
    text(draw, (88, 260), "CRITERIA", fonts["small"], PALETTE["muted"], "lm")
    text(draw, (930, 145), "DECISION", fonts["small"], PALETTE["muted"], "lm")

    option_labels, criterion_labels = comparison_labels(args)
    options = [
        (compact_label(option_labels[0], 18), PALETTE["route"], 0.78),
        (compact_label(option_labels[1], 18), PALETTE["defense"], 0.88),
        (compact_label(option_labels[2], 18), PALETTE["attribute"], 0.70),
    ]
    criteria = [
        (compact_label(criterion_labels[0], 16), [0.92, 0.72, 0.45], PALETTE["route"]),
        (compact_label(criterion_labels[1], 16), [0.52, 0.86, 0.90], PALETTE["defense"]),
        (compact_label(criterion_labels[2], 16), [0.38, 0.72, 0.94], PALETTE["tradeoff"]),
        (compact_label(criterion_labels[3], 16), [0.82, 0.64, 0.48], PALETTE["damage"]),
    ]
    option_reveal = ease((p - 0.04) / 0.16)
    criteria_revealed = min(len(criteria), int(ease((p - 0.20) / 0.35) * (len(criteria) + 0.999)))
    score_shift_visible = p > 0.48
    tradeoff_visible = p > 0.62
    recommendation_visible = p > 0.76
    guardrail_visible = p > 0.86

    option_xs = [335, 555, 775]
    for idx, ((label, color, score), x) in enumerate(zip(options, option_xs)):
        active = ease((p - 0.05 - idx * 0.06) / 0.12)
        rounded_rect(draw, (x - 88, 150, x + 88, 225), "#ffffff", color if active > 0.1 else PALETTE["line"], width=3, radius=16)
        text(draw, (x, 177), label, fonts.get("label", fonts["small"]), PALETTE["ink"], "mm", 3, "#ffffff")
        text(draw, (x, 202), f"{round(score * 100)}%", fonts["small"], color, "mm", 2, "#ffffff")
        if active > 0.8:
            draw.ellipse((x - 8, 232, x + 8, 248), fill=hex_to_rgb(color))

    grid_left = 250
    row_top = 290
    row_h = 58
    for x in (250, 430, 650, 850):
        draw.line([(x, 250), (x, 522)], fill=hex_to_rgb(PALETTE["line"]), width=2)
    for y in (260, 318, 376, 434, 492):
        draw.line([(grid_left, y), (850, y)], fill=hex_to_rgb(PALETTE["line"]), width=2)
    for c_idx, (criterion, values, color) in enumerate(criteria):
        y = row_top + c_idx * row_h
        row_active = c_idx < criteria_revealed
        rounded_rect(draw, (92, y - 22, 205, y + 22), "#ffffff", color if row_active else PALETTE["line"], radius=10)
        text(draw, (148, y + 2), criterion, fonts["small"], PALETTE["ink"], "mm", 2, "#ffffff")
        for o_idx, value in enumerate(values):
            x = option_xs[o_idx]
            rounded_rect(draw, (x - 74, y - 15, x + 74, y + 15), "#cfcfcf", None, radius=7)
            fill = 0 if not row_active else value * ease((p - 0.20 - c_idx * 0.07) / 0.22)
            if fill > 0.02:
                rounded_rect(draw, (x - 74, y - 15, x - 74 + 148 * fill, y + 15), color, None, radius=7)
            if row_active and score_shift_visible and o_idx == 1:
                draw.ellipse((x + 84, y - 8, x + 100, y + 8), fill=hex_to_rgb(PALETTE["gold"]))
        if c_idx < len(criteria) - 1:
            draw.line([(grid_left, y + 29), (850, y + 29)], fill=hex_to_rgb("#edf2f7"), width=2)

    if tradeoff_visible:
        rounded_rect(draw, (910, 205, 1165, 315), "#ffccd5", PALETTE["damage"], width=3, radius=16)
        text(draw, (1038, 232), "tradeoff lens", fonts.get("label", fonts["small"]), PALETTE["damage"], "mm", 3, "#ffffff")
        text(draw, (1038, 260), "speed gains can raise risk", fonts["small"], PALETTE["ink"], "mm")
        draw.line([(940, 288), (1134, 288)], fill=hex_to_rgb(PALETTE["damage"]), width=5)
        draw.polygon([(1134, 288), (1118, 280), (1118, 296)], fill=hex_to_rgb(PALETTE["damage"]))
    if recommendation_visible:
        rounded_rect(draw, (910, 350, 1165, 445), "#e7e7e7", PALETTE["defense"], width=4, radius=16)
        text(draw, (1038, 377), "recommended", fonts.get("label", fonts["small"]), PALETTE["defense"], "mm", 3, "#ffffff")
        text(draw, (1038, 405), f"{compact_label(option_labels[1], 18)} wins", fonts["body"], PALETTE["ink"], "mm")
        draw.line([(555, 225), (1010, 350)], fill=hex_to_rgb(PALETTE["defense"]), width=5)
    if guardrail_visible:
        rounded_rect(draw, (910, 480, 1165, 555), "#e7e7e7", PALETTE["attribute"], width=3, radius=16)
        text(draw, (1038, 505), "guardrail", fonts.get("label", fonts["small"]), PALETTE["attribute"], "mm", 3, "#ffffff")
        text(draw, (1038, 530), "reject if risk spikes", fonts["small"], PALETTE["ink"], "mm")

    token_y = 250 + ease((p - 0.18) / 0.54) * 240
    draw.ellipse((842, token_y - 11, 864, token_y + 11), fill=hex_to_rgb(PALETTE["gold"]))
    draw.line([(852, 250), (852, 492)], fill=hex_to_rgb(PALETTE["gold"]), width=3)

    beats = [
        (0.00, "Compare options against the same criteria."),
        (0.24, "Scores reveal where each option actually differs."),
        (0.48, "A tradeoff lens explains why the top score shifts."),
        (0.70, "Recommendation appears only after criteria are visible."),
        (0.86, "Guardrails keep the decision from becoming a blind ranking."),
    ]
    current = beats[0][1]
    for threshold, beat in beats:
        if p >= threshold:
            current = beat

    return img


def render_causal_loop_frame(
    second: float,
    args: argparse.Namespace,
    fonts: dict[str, ImageFont.ImageFont],
) -> Image.Image:
    width, height = args.width, args.height
    img = Image.new("RGB", (width, height), hex_to_rgb(PALETTE["paper"]))
    draw = ImageDraw.Draw(img)
    p = second / args.duration


    rounded_rect(draw, (55, 112, 1220, 606), "#ffffff", "#cfcfcf", radius=14)
    text(draw, (88, 145), "CAUSE MAP", fonts["small"], PALETTE["muted"], "lm")
    text(draw, (915, 145), "INTERVENTION", fonts["small"], PALETTE["muted"], "lm")
    labels = [compact_label(label, 22) for label in causal_labels(args)]

    nodes = [
        (labels[0], (210, 310), PALETTE["route"]),
        (labels[1], (430, 210), PALETTE["damage"]),
        (labels[2], (645, 310), PALETTE["defense"]),
        (labels[3], (430, 430), PALETTE["atlas"]),
    ]
    loop_points = [(230, 286), (390, 210), (430, 210), (610, 286), (645, 310), (478, 430), (430, 430), (242, 338), (210, 310)]
    balancing_points = [(645, 310), (760, 260), (825, 340), (720, 430), (478, 430)]
    side_effect_points = [(645, 310), (790, 470), (920, 470)]
    intervention_points = [(1000, 400), (845, 340), (720, 430)]

    loop_visible = p > 0.10
    delay_visible = p > 0.34
    amplifier_visible = p > 0.48
    damping_visible = p > 0.60
    side_effect_visible = p > 0.72
    intervention_visible = p > 0.84

    draw_polyline(draw, loop_points, PALETTE["line"], 4, 1)
    draw_polyline(draw, balancing_points, PALETTE["line"], 4, 1)
    draw_polyline(draw, side_effect_points, PALETTE["line"], 4, 1)
    draw_polyline(draw, loop_points, PALETTE["route"], 8, ease((p - 0.10) / 0.38))
    if damping_visible:
        draw_polyline(draw, balancing_points, PALETTE["defense"], 7, ease((p - 0.60) / 0.18))
    if side_effect_visible:
        draw_polyline(draw, side_effect_points, PALETTE["tradeoff"], 7, ease((p - 0.72) / 0.14))
    if intervention_visible:
        draw_polyline(draw, intervention_points, PALETTE["attribute"], 7, ease((p - 0.84) / 0.12))

    for idx, (label, xy, color) in enumerate(nodes):
        active = ease((p - 0.04 - idx * 0.10) / 0.18)
        rounded_rect(draw, (xy[0] - 78, xy[1] - 36, xy[0] + 78, xy[1] + 36), "#ffffff", color if active > 0.1 else PALETTE["line"], width=3, radius=18)
        text(draw, (xy[0], xy[1] + 4), label, fonts.get("label", fonts["small"]), PALETTE["ink"], "mm", 3, "#ffffff")
        if active > 0.7:
            draw.ellipse((xy[0] - 9, xy[1] - 58, xy[0] + 9, xy[1] - 40), fill=hex_to_rgb(color))

    if delay_visible:
        rounded_rect(draw, (500, 150, 615, 215), "#ffccd5", PALETTE["damage"], width=3, radius=14)
        text(draw, (558, 176), "delay", fonts.get("label", fonts["small"]), PALETTE["damage"], "mm", 3, "#ffffff")
        text(draw, (558, 198), "effect lags", fonts["small"], PALETTE["ink"], "mm")
        draw.line([(515, 220), (600, 260)], fill=hex_to_rgb(PALETTE["damage"]), width=4)

    if amplifier_visible:
        rounded_rect(draw, (92, 475, 305, 555), "#e7e7e7", PALETTE["route"], width=3, radius=16)
        text(draw, (198, 502), "reinforcing loop", fonts.get("label", fonts["small"]), PALETTE["route"], "mm", 3, "#ffffff")
        text(draw, (198, 528), "amplifies pressure", fonts["small"], PALETTE["ink"], "mm")
        draw.line([(256, 528), (286, 528)], fill=hex_to_rgb(PALETTE["route"]), width=4)
        draw.polygon([(286, 528), (274, 522), (274, 534)], fill=hex_to_rgb(PALETTE["route"]))

    if damping_visible:
        rounded_rect(draw, (760, 255, 895, 425), "#e7e7e7", PALETTE["defense"], width=3, radius=18)
        text(draw, (828, 286), "balancing", fonts.get("label", fonts["small"]), PALETTE["defense"], "mm", 3, "#ffffff")
        text(draw, (828, 312), "constraint", fonts["small"], PALETTE["ink"], "mm")
        draw.line([(790, 365), (865, 365)], fill=hex_to_rgb(PALETTE["defense"]), width=6)

    if side_effect_visible:
        rounded_rect(draw, (920, 430, 1135, 515), "#ffccd5", PALETTE["tradeoff"], width=3, radius=18)
        text(draw, (1028, 458), labels[4], fonts.get("label", fonts["small"]), PALETTE["tradeoff"], "mm", 3, "#ffffff")
        text(draw, (1028, 485), "new pressure appears", fonts["small"], PALETTE["ink"], "mm")

    if intervention_visible:
        rounded_rect(draw, (940, 205, 1165, 340), "#e7e7e7", PALETTE["attribute"], width=4, radius=18)
        text(draw, (1052, 236), labels[5], fonts.get("label", fonts["small"]), PALETTE["attribute"], "mm", 3, "#ffffff")
        text(draw, (1052, 264), "break the loop at leverage", fonts["small"], PALETTE["ink"], "mm")
        draw.line([(982, 300), (1120, 300)], fill=hex_to_rgb(PALETTE["attribute"]), width=5)
        draw.polygon([(1120, 300), (1104, 292), (1104, 308)], fill=hex_to_rgb(PALETTE["attribute"]))

    if loop_visible:
        token = point_on_polyline(loop_points, ease((p - 0.10) / 0.50))
        draw.ellipse((token[0] - 12, token[1] - 12, token[0] + 12, token[1] + 12), fill=hex_to_rgb(PALETTE["gold"]))
    if side_effect_visible:
        token = point_on_polyline(side_effect_points, ease((p - 0.72) / 0.16))
        draw.ellipse((token[0] - 10, token[1] - 10, token[0] + 10, token[1] + 10), fill=hex_to_rgb(PALETTE["tradeoff"]))

    draw_meter(draw, (325, 515, 455, 580), "pressure", ease((p - 0.18) / 0.52), PALETTE["damage"], fonts)
    draw_meter(draw, (485, 515, 615, 580), "delay", ease((p - 0.34) / 0.38), PALETTE["gold"], fonts)
    draw_meter(draw, (645, 515, 775, 580), "leverage", ease((p - 0.78) / 0.18), PALETTE["attribute"], fonts)

    beats = [
        (0.00, "Start with the cause chain, not a generic timeline."),
        (0.22, "Delays explain why the effect appears late."),
        (0.46, "Reinforcing loops amplify the original pressure."),
        (0.62, "Balancing loops constrain runaway behavior."),
        (0.78, "Side effects create a second pressure source."),
        (0.88, "Intervene at leverage, not at the loudest symptom."),
    ]
    current = beats[0][1]
    for threshold, beat in beats:
        if p >= threshold:
            current = beat

    return img


def render_phase_timeline_frame(
    second: float,
    args: argparse.Namespace,
    fonts: dict[str, ImageFont.ImageFont],
) -> Image.Image:
    width, height = args.width, args.height
    img = Image.new("RGB", (width, height), hex_to_rgb(PALETTE["paper"]))
    draw = ImageDraw.Draw(img)
    p = second / args.duration
    labels = phase_timeline_labels(args)


    rounded_rect(draw, (55, 112, 1225, 608), "#ffffff", "#cfcfcf", radius=14)
    rounded_rect(draw, (88, 182, 1192, 390), "#ffffff", "#cfcfcf", radius=14)
    rounded_rect(draw, (138, 430, 1115, 575), "#ffccd5", "#cfcfcf", radius=14)
    text(draw, (92, 145), "PHASE TIMELINE", fonts["small"], PALETTE["muted"], "lm")
    text(draw, (162, 458), "RISK, GATE, AND HANDOFF", fonts["small"], PALETTE["tradeoff"], "lm")

    x_positions = [150, 340, 530, 720, 910, 1100]
    phase_points = [(x, 300) for x in x_positions]
    progress = ease((p - 0.04) / 0.58)
    active_phase = min(len(phase_points) - 1, int(progress * len(phase_points)))
    for a, b in zip(phase_points, phase_points[1:]):
        draw.line([a, b], fill=hex_to_rgb(PALETTE["line"]), width=5)
    draw_polyline(draw, phase_points, PALETTE["route"], 9, progress)

    palette_cycle = [PALETTE["route"], PALETTE["attribute"], PALETTE["defense"], PALETTE["tradeoff"], PALETTE["damage"], PALETTE["atlas"]]
    for idx, ((x, y), label, color) in enumerate(zip(phase_points, labels, palette_cycle)):
        active = ease((p - 0.04 - idx * 0.08) / 0.12)
        fill = "#ffffff" if active < 0.95 else "#e7e7e7"
        outline = color if active > 0.1 else PALETTE["line"]
        rounded_rect(draw, (x - 72, y - 36, x + 72, y + 36), fill, outline, width=4 if active > 0.1 else 2, radius=16)
        text(draw, (x, y + 4), compact_label(label, 16), fonts.get("label", fonts["small"]), PALETTE["ink"], "mm", 3, "#ffffff")
        if idx == active_phase and p < 0.86:
            draw.ellipse((x - 10, y - 60, x + 10, y - 40), fill=hex_to_rgb(PALETTE["gold"]))

    risk_visible = p > 0.28
    gate_visible = p > 0.46
    handoff_visible = p > 0.66
    final_visible = p > 0.84
    if risk_visible:
        draw_polyline(draw, [(340, 336), (340, 505), (530, 505)], PALETTE["damage"], 7, ease((p - 0.28) / 0.18))
        rounded_rect(draw, (260, 482, 420, 548), "#ffccd5", PALETTE["damage"], width=3, radius=14)
        text(draw, (340, 509), "risk scan", fonts.get("label", fonts["small"]), PALETTE["damage"], "mm", 3, "#ffffff")
        text(draw, (340, 530), "surface blockers", fonts["small"], PALETTE["ink"], "mm")
    if gate_visible:
        rounded_rect(draw, (640, 178, 800, 238), "#e7e7e7", PALETTE["attribute"], width=3, radius=14)
        text(draw, (720, 202), "decision gate", fonts.get("label", fonts["small"]), PALETTE["attribute"], "mm", 3, "#ffffff")
        text(draw, (720, 224), "pass or revise", fonts["small"], PALETTE["ink"], "mm")
        draw.line([(720, 238), (720, 264)], fill=hex_to_rgb(PALETTE["attribute"]), width=4)
    if handoff_visible:
        handoff = [(720, 336), (790, 512), (910, 512), (910, 336)]
        for a, b in zip(handoff, handoff[1:]):
            draw.line([a, b], fill=hex_to_rgb(PALETTE["line"]), width=4)
        draw_polyline(draw, handoff, PALETTE["tradeoff"], 7, ease((p - 0.66) / 0.20))
        rounded_rect(draw, (820, 482, 1000, 548), "#ffccd5", PALETTE["tradeoff"], width=3, radius=14)
        text(draw, (910, 509), "handoff", fonts.get("label", fonts["small"]), PALETTE["tradeoff"], "mm", 3, "#ffffff")
        text(draw, (910, 530), "carry constraints", fonts["small"], PALETTE["ink"], "mm")
    if final_visible:
        rounded_rect(draw, (1005, 452, 1092, 552), "#e7e7e7", PALETTE["atlas"], width=3, radius=16)
        text(draw, (1048, 488), "release", fonts.get("label", fonts["small"]), PALETTE["atlas"], "mm", 3, "#ffffff")
        text(draw, (1048, 516), "notes", fonts["small"], PALETTE["ink"], "mm")

    draw_meter(draw, (150, 198, 310, 263), "source lock", ease((p - 0.06) / 0.20), PALETTE["route"], fonts)
    draw_meter(draw, (910, 198, 1070, 263), "quality gate", ease((p - 0.46) / 0.24), PALETTE["defense"], fonts)
    if progress > 0.08:
        token = point_on_polyline(phase_points, progress)
        draw.ellipse((token[0] - 13, token[1] - 13, token[0] + 13, token[1] + 13), fill=hex_to_rgb(PALETTE["gold"]))

    beats = [
        (0.00, "Start with a source-locked intake phase."),
        (0.22, "Scope and build phases expose risks early."),
        (0.44, "A decision gate separates review from validation."),
        (0.66, "Handoffs carry constraints into the next phase."),
        (0.84, "The release phase publishes only after gates pass."),
    ]
    current = beats[0][1]
    for threshold, beat in beats:
        if p >= threshold:
            current = beat

    return img


def render_metric_dashboard_frame(
    second: float,
    args: argparse.Namespace,
    fonts: dict[str, ImageFont.ImageFont],
) -> Image.Image:
    width, height = args.width, args.height
    low_text_masonry = bool(getattr(args, "masonry_layout", False))
    canvas_width = round(width * 1.5) if low_text_masonry else width
    img = Image.new("RGB", (canvas_width, height), hex_to_rgb(PALETTE["paper"]))
    draw = ImageDraw.Draw(img)
    p = second / args.duration
    metric_labels, threshold_labels = metric_dashboard_labels(args)
    metrics = [compact_label(label, 18) for label in metric_labels]
    thresholds = [compact_label(label, 18) for label in threshold_labels]
    panel_radius = 0 if low_text_masonry else 14
    card_radius = 0 if low_text_masonry else 12


    if low_text_masonry:
        draw_masonry_megacanvas_base(draw, second, args)
    else:
        rounded_rect(draw, (55, 112, 800, 602), "#ffffff", "#cfcfcf", radius=panel_radius)
        rounded_rect(draw, (835, 112, 1220, 602), "#ffffff", "#cfcfcf", radius=panel_radius)
        draw.rectangle((55, 568, 1220, 602), fill=hex_to_rgb(gray_level(5)))
        draw.rectangle((800, 112, 832, 568), fill=hex_to_rgb(gray_level(4)))
        draw.rectangle((1192, 112, 1220, 568), fill=hex_to_rgb(gray_level(5)))
        text(draw, (88, 145), "TREND, THRESHOLDS, AND FORECAST", fonts["small"], PALETTE["muted"], "lm")
        text(draw, (865, 145), "DECISION CONTEXT", fonts["small"], PALETTE["muted"], "lm")

    chart = (115, 190, 760, 520)
    if low_text_masonry:
        density_level = min(84, int(ease((p - 0.04) / 0.72) * 85))
        for row in range(6):
            for col in range(10):
                index = row * 10 + col
                active = index < density_level
                x = chart[0] + 26 + col * 42
                y = chart[1] + 26 + row * 28
                fill = gray_level(2 + ((row + col) % 4)) if active else gray_level(1)
                draw.rectangle((x, y, x + 32, y + 20), fill=hex_to_rgb(fill))
                if active and (row == col % 6 or index % 17 == 0):
                    draw.rectangle((x, y, x + 6, y + 20), fill=hex_to_rgb(PALETTE["route"]))
        for index in range(14):
            active = index < int(density_level / 4) + 2
            x = 86 + index * 28
            y = 132 + (index % 3) * 22
            fill = gray_level(3 + (index % 3)) if active else gray_level(1 + (index % 4))
            draw.rectangle((x, y, x + 22, y + 16), fill=hex_to_rgb(fill))
            if active and index % 5 == 0:
                draw.rectangle((x, y, x + 6, y + 16), fill=hex_to_rgb(PALETTE["route"]))
        for row in range(5):
            y = 124 + row * 28
            bar_width = 96 + row * 38 + ease((p - 0.20 - row * 0.04) / 0.22) * 92
            draw.rectangle((892, y, 892 + bar_width, y + 20), fill=hex_to_rgb(gray_level(2 + (row % 4))))
            if row < int(ease((p - 0.24) / 0.42) * 6):
                draw.rectangle((892, y, 898, y + 20), fill=hex_to_rgb(PALETTE["route"]))
        for row in range(2):
            for col in range(30):
                index = row * 30 + col
                active = index < int(density_level * 0.72)
                x = 64 + col * 50
                y = 640 + row * 28
                fill = gray_level(2 + (index % 4)) if active else gray_level(1)
                draw.rectangle((x, y, x + 40, y + 18), fill=hex_to_rgb(fill))
                if active and index % 12 == 0:
                    draw.rectangle((x, y, x + 6, y + 18), fill=hex_to_rgb(PALETTE["route"]))
    for idx in range(5):
        y = chart[1] + idx * (chart[3] - chart[1]) / 4
        draw.line([(chart[0], y), (chart[2], y)], fill=hex_to_rgb("#cfcfcf"), width=2)
    draw.line([(chart[0], chart[3]), (chart[2], chart[3])], fill=hex_to_rgb(PALETTE["line"]), width=3)
    draw.line([(chart[0], chart[1]), (chart[0], chart[3])], fill=hex_to_rgb(PALETTE["line"]), width=3)

    healthy_y = 330
    warning_y = 395
    action_y = 455
    trend_visible = ease((p - 0.05) / 0.42) > 0.04
    threshold_visible = p > 0.18
    anomaly_visible = p > 0.56
    forecast_visible = p > 0.72
    decision_visible = p > 0.84
    trend_progress = ease((p - 0.05) / 0.42)
    if threshold_visible:
        draw.rectangle((chart[0], healthy_y - 26, chart[2], warning_y - 7), fill=hex_to_rgb("#e7e7e7"))
        draw.line([(chart[0], healthy_y), (chart[2], healthy_y)], fill=hex_to_rgb(PALETTE["defense"]), width=4)
        draw.line([(chart[0], warning_y), (chart[2], warning_y)], fill=hex_to_rgb(PALETTE["gold"]), width=4)
        draw.line([(chart[0], action_y), (chart[2], action_y)], fill=hex_to_rgb(PALETTE["tradeoff"]), width=4)
        if not low_text_masonry:
            text(draw, (chart[2] - 8, healthy_y - 10), thresholds[0], fonts["tiny"], PALETTE["defense"], "rm", 3, "#ffffff")
            text(draw, (chart[2] - 8, warning_y - 10), thresholds[1], fonts["tiny"], PALETTE["gold"], "rm", 3, "#ffffff")
            text(draw, (chart[2] - 8, action_y - 10), thresholds[2], fonts["tiny"], PALETTE["tradeoff"], "rm", 3, "#ffffff")

    points = [(145, 472), (230, 448), (315, 438), (400, 402), (485, 422), (570, 366), (655, 334), (740, 300)]
    reveal_segments = max(0, min(len(points) - 1, int(trend_progress * (len(points) - 1))))
    for idx in range(reveal_segments):
        draw.line([points[idx], points[idx + 1]], fill=hex_to_rgb(PALETTE["route"]), width=4)
    if 0 < trend_progress < 1:
        idx = min(len(points) - 2, reveal_segments)
        ratio = trend_progress * (len(points) - 1) - idx
        a, b = points[idx], points[idx + 1]
        partial = (round(a[0] + (b[0] - a[0]) * ratio), round(a[1] + (b[1] - a[1]) * ratio))
        draw.line([a, partial], fill=hex_to_rgb(PALETTE["route"]), width=4)
    active_point_count = max(1, min(len(points), int(trend_progress * len(points)) + 1))
    for idx, point in enumerate(points[:active_point_count]):
        outline = PALETTE["route"] if idx != 4 else PALETTE["damage"]
        draw.ellipse((point[0] - 7, point[1] - 7, point[0] + 7, point[1] + 7), fill=hex_to_rgb(gray_level(5)), outline=hex_to_rgb(outline), width=3)
    if anomaly_visible:
        anomaly = points[4]
        draw.ellipse((anomaly[0] - 30, anomaly[1] - 30, anomaly[0] + 30, anomaly[1] + 30), outline=hex_to_rgb(PALETTE["damage"]), width=5)
        rounded_rect(draw, (425, 225, 595, 285), gray_level(2), PALETTE["damage"], radius=card_radius)
        if not low_text_masonry:
            text(draw, (510, 249), "anomaly", fonts["small"], PALETTE["damage"], "mm")
            text(draw, (510, 274), metrics[4], fonts["tiny"], PALETTE["ink"], "mm")
    if forecast_visible:
        cone = [(740, 300), (790, 260), (790, 360), (740, 300)]
        draw.polygon(cone, fill=hex_to_rgb("#e7e7e7"))
        draw.line([(740, 300), (790, 260)], fill=hex_to_rgb(PALETTE["atlas"]), width=3)
        draw.line([(740, 300), (790, 360)], fill=hex_to_rgb(PALETTE["atlas"]), width=3)
        if not low_text_masonry:
            text(draw, (720, 244), "forecast cone", fonts["tiny"], PALETTE["atlas"], "mm", 3, "#ffffff")

    card_specs = [
        (865, 178, 320, 82, metrics[0], "north star", PALETTE["route"], 0.78 + 0.12 * ease((p - 0.08) / 0.45), 0.02),
        (865, 278, 150, 82, metrics[1], "input", PALETTE["damage"], 0.55 + 0.25 * ease((p - 0.18) / 0.35), 0.18),
        (1035, 278, 150, 82, metrics[2], "output", PALETTE["defense"], 0.48 + 0.30 * ease((p - 0.30) / 0.35), 0.30),
        (865, 378, 150, 82, metrics[3], "quality", PALETTE["attribute"], 0.64 + 0.20 * ease((p - 0.44) / 0.30), 0.44),
        (1035, 378, 150, 82, metrics[4], "risk", PALETTE["tradeoff"], 0.38 + 0.32 * ease((p - 0.56) / 0.25), 0.56),
    ]
    for x1, y1, w, h, name, role, color, value, reveal_at in card_specs:
        if p + 0.02 < reveal_at:
            continue
        rounded_rect(draw, (x1, y1, x1 + w, y1 + h), gray_level(3), color if p > 0.16 else PALETTE["line"], radius=card_radius)
        fill_width = w * clamp(value)
        if fill_width > 0:
            draw.rectangle((x1, y1, x1 + fill_width, y1 + h), fill=hex_to_rgb(gray_level(5)))
            cap_width = min(8, fill_width)
            draw.rectangle((x1 + fill_width - cap_width, y1, x1 + fill_width, y1 + h), fill=hex_to_rgb(color))
        if not low_text_masonry:
            text(draw, (x1 + w / 2, y1 + h / 2 - 8), compact_label(name, 20), fonts["small"], PALETTE["ink"], "mm", 3, "#ffffff")
            text(draw, (x1 + w / 2, y1 + h / 2 + 20), role, fonts["tiny"], PALETTE["ink"], "mm", 2, "#ffffff")
    if decision_visible:
        rounded_rect(draw, (865, 492, 1185, 564), "#e7e7e7", PALETTE["defense"], radius=card_radius)
        if not low_text_masonry:
            text(draw, (1025, 518), "decision window open", fonts["small"], PALETTE["defense"], "mm")
            text(draw, (1025, 545), "act when forecast crosses threshold", fonts["tiny"], PALETTE["ink"], "mm")

    beats = [
        "Start with the metric that owns the decision.",
        "Thresholds turn a chart into an operating rule.",
        "Anomalies need a named risk, not just a red dot.",
        "Forecasts show where the trend will cross the line.",
        "The decision appears only after evidence is visible.",
    ]
    beat_index = max(0, min(len(beats) - 1, int(p * len(beats))))
    current = beats[beat_index]
    return img


def render_dependency_map_frame(
    second: float,
    args: argparse.Namespace,
    fonts: dict[str, ImageFont.ImageFont],
) -> Image.Image:
    width, height = args.width, args.height
    low_text_masonry = bool(getattr(args, "masonry_layout", False))
    img = Image.new("RGB", (width, height), hex_to_rgb(PALETTE["paper"]))
    draw = ImageDraw.Draw(img)
    p = second / args.duration
    dependency_labels, cluster_labels = dependency_map_labels(args)
    deps = [compact_label(label, 18) for label in dependency_labels]
    clusters = [compact_label(label, 20) for label in cluster_labels]
    panel_radius = 0 if low_text_masonry else 14
    callout_radius = 0 if low_text_masonry else 14


    cluster_frames = [
        (55, 112, 365, 592, PALETTE["route"]),
        (395, 112, 855, 592, PALETTE["defense"]),
        (885, 112, 1220, 592, PALETTE["attribute"]),
    ]
    for x1, y1, x2, y2, accent in cluster_frames:
        rounded_rect(draw, (x1, y1, x2, y2), "#ffffff", "#cfcfcf", radius=panel_radius)
        rounded_rect(draw, (x1, y1, x2, y1 + 12), accent, None, radius=0)
    if low_text_masonry:
        density_level = max(42, min(72, int(ease((p - 0.04) / 0.70) * 73)))

        def cap_fill(index: int) -> str:
            return [PALETTE["route"], PALETTE["attribute"], PALETTE["damage"]][index % 3]

        protocol_level = max(24, min(42, int(ease((p - 0.02) / 0.34) * 43)))
        for row in range(3):
            for col in range(14):
                index = row * 14 + col
                active = index < protocol_level
                x = 420 + col * 28
                y = 136 + row * 20
                fill = gray_level(2 + ((row * 2 + col) % 7)) if active else gray_level(1)
                draw.rectangle((x, y, x + 24, y + 16), fill=hex_to_rgb(fill))
                if active and index % 10 == 0:
                    draw.rectangle((x, y, x + 4, y + 16), fill=hex_to_rgb(cap_fill(index)))
                if active and index % 13 == 5:
                    draw.rectangle((x + 20, y, x + 24, y + 16), fill=hex_to_rgb(gray_level(8)))
        for row in range(5):
            for col in range(10):
                index = row * 10 + col
                active = index < density_level
                x = 92 + col * 28
                y = 472 + row * 22
                fill = gray_level(2 + ((row + col) % 6)) if active else gray_level(1)
                draw.rectangle((x, y, x + 20, y + 16), fill=hex_to_rgb(fill))
                if active and index % 7 == 0:
                    draw.rectangle((x, y, x + 6, y + 16), fill=hex_to_rgb(cap_fill(index)))
                if active and index % 11 == 4:
                    draw.rectangle((x + 16, y, x + 20, y + 16), fill=hex_to_rgb(gray_level(8)))
        for row in range(4):
            for col in range(8):
                index = row * 8 + col
                active = index < int(density_level * 0.7)
                x = 902 + col * 34
                y = 342 + row * 26
                fill = gray_level(2 + ((index + row) % 6)) if active else gray_level(1)
                draw.rectangle((x, y, x + 26, y + 20), fill=hex_to_rgb(fill))
                if active and (row == col % 4 or index % 7 == 0):
                    draw.rectangle((x, y, x + 6, y + 20), fill=hex_to_rgb(cap_fill(index + row)))
                if active and index % 9 == 3:
                    draw.rectangle((x + 22, y, x + 26, y + 20), fill=hex_to_rgb(gray_level(8)))
        for col in range(24):
            active = col < int(density_level / 2)
            x = 64 + col * 58
            fill = gray_level(2 + (col % 6)) if active else gray_level(1)
            draw.rectangle((x, 650, x + 48, 668), fill=hex_to_rgb(fill))
            if active and col % 6 == 0:
                draw.rectangle((x, 650, x + 6, 668), fill=hex_to_rgb(cap_fill(col)))
            if active and col % 8 == 3:
                draw.rectangle((x + 42, 650, x + 48, 668), fill=hex_to_rgb(gray_level(8)))
    else:
        text(draw, (82, 145), clusters[0].upper(), fonts["small"], PALETTE["muted"], "lm")
        text(draw, (425, 145), clusters[1].upper(), fonts["small"], PALETTE["muted"], "lm")
        text(draw, (915, 145), clusters[2].upper(), fonts["small"], PALETTE["muted"], "lm")

    nodes = [
        (170, 245, deps[0], PALETTE["route"]),
        (170, 410, deps[1], PALETTE["attribute"]),
        (470, 325, deps[2], PALETTE["route"]),
        (640, 235, deps[3], PALETTE["damage"]),
        (640, 420, deps[4], PALETTE["defense"]),
        (805, 325, deps[5], PALETTE["atlas"]),
        (1025, 270, deps[6], PALETTE["tradeoff"]),
        (1025, 450, deps[7], PALETTE["gold"]),
    ]
    edges = [(0, 2), (1, 2), (2, 3), (2, 4), (3, 5), (4, 5), (5, 6)]
    edge_progress = ease((p - 0.06) / 0.46)
    risk_visible = p > 0.46
    bottleneck_visible = p > 0.58
    cutover_visible = p > 0.72
    fallback_visible = p > 0.84

    for left, right in edges:
        a = nodes[left]
        b = nodes[right]
        draw.line([(a[0], a[1]), (b[0], b[1])], fill=hex_to_rgb(PALETTE["line"]), width=4)
    for idx, (left, right) in enumerate(edges):
        a = nodes[left]
        b = nodes[right]
        segment_progress = clamp(edge_progress * len(edges) - idx)
        draw_polyline(draw, [(a[0], a[1]), (b[0], b[1])], PALETTE["route"], 7, segment_progress)

    if fallback_visible:
        draw.line([(nodes[5][0], nodes[5][1]), (nodes[7][0], nodes[7][1])], fill=hex_to_rgb(PALETTE["line"]), width=4)
        draw_polyline(draw, [(nodes[5][0], nodes[5][1]), (nodes[7][0], nodes[7][1])], PALETTE["gold"], 7, ease((p - 0.84) / 0.12))
    for idx, (x, y, label, color) in enumerate(nodes):
        active = ease((p - 0.04 - idx * 0.055) / 0.12)
        shape = "diamond" if idx in {3, 6} else "circle"
        halo_radius = 28 if shape == "circle" else 34
        if shape == "diamond":
            halo = [(x, y - halo_radius), (x + halo_radius, y), (x, y + halo_radius), (x - halo_radius, y)]
            draw.line([*halo, halo[0]], fill=hex_to_rgb(color), width=3)
        else:
            draw.ellipse((x - halo_radius, y - halo_radius, x + halo_radius, y + halo_radius), outline=hex_to_rgb(color), width=3)
        draw_node(draw, (x, y), label, color, active, fonts, shape=shape, ghost_label=not low_text_masonry)

    if risk_visible:
        rounded_rect(draw, (520, 500, 740, 565), gray_level(2), PALETTE["damage"], radius=callout_radius)
        if not low_text_masonry:
            text(draw, (630, 525), "risk edge", fonts["small"], PALETTE["damage"], "mm", 3, "#ffffff")
            text(draw, (630, 548), "unblocks only after policy", fonts["tiny"], PALETTE["ink"], "mm")
        draw.line([(640, 455), (640, 500)], fill=hex_to_rgb(PALETTE["damage"]), width=5)
    if bottleneck_visible:
        rounded_rect(draw, (705, 178, 845, 238), gray_level(2), PALETTE["tradeoff"], radius=callout_radius)
        if not low_text_masonry:
            text(draw, (775, 202), "bottleneck", fonts["small"], PALETTE["tradeoff"], "mm", 3, "#ffffff")
            text(draw, (775, 224), deps[5], fonts["tiny"], PALETTE["ink"], "mm")
        draw.ellipse((785, 305, 825, 345), outline=hex_to_rgb(PALETTE["tradeoff"]), width=5)
    if cutover_visible:
        rounded_rect(draw, (930, 170, 1160, 225), "#e7e7e7", PALETTE["attribute"], radius=callout_radius)
        if not low_text_masonry:
            text(draw, (1045, 193), "cutover gate", fonts["small"], PALETTE["attribute"], "mm", 3, "#ffffff")
            text(draw, (1045, 214), "release waits for upstream proof", fonts["tiny"], PALETTE["ink"], "mm")
        draw.line([(930, 270), (1160, 270)], fill=hex_to_rgb(PALETTE["attribute"]), width=5)
    if fallback_visible:
        rounded_rect(draw, (920, 502, 1168, 562), "#e7e7e7", PALETTE["gold"], radius=callout_radius)
        if not low_text_masonry:
            text(draw, (1044, 526), "fallback armed", fonts["small"], PALETTE["gold"], "mm", 3, "#ffffff")
            text(draw, (1044, 548), "late safety route is explicit", fonts["tiny"], PALETTE["ink"], "mm")

    edge_count = min(len(edges), int(edge_progress * len(edges) + 0.999))
    visible_mechanism_count = [edge_count >= 4, risk_visible, bottleneck_visible, cutover_visible, fallback_visible].count(True)
    draw_meter(draw, (90, 520, 300, 585), "dependency proof", edge_progress, PALETTE["route"], fonts)
    draw_meter(draw, (655, 560, 865, 625), "risk surfaced", ease((p - 0.46) / 0.18), PALETTE["damage"], fonts)
    draw_meter(draw, (900, 560, 1180, 625), "release readiness", ease((p - 0.72) / 0.20), PALETTE["defense"], fonts)

    beats = [
        "Map dependencies before promising a release.",
        "Shared prerequisites converge into the integration layer.",
        "Risk edges and bottlenecks need their own visual path.",
        "Cutover waits for upstream proof, not calendar optimism.",
        "Fallback is a late safety route, not an afterthought.",
    ]
    beat_index = max(0, min(len(beats) - 1, int(p * len(beats))))
    return img


def render_sequence_trace_frame(
    second: float,
    args: argparse.Namespace,
    fonts: dict[str, ImageFont.ImageFont],
) -> Image.Image:
    width, height = args.width, args.height
    img = Image.new("RGB", (width, height), hex_to_rgb(PALETTE["paper"]))
    draw = ImageDraw.Draw(img)
    p = second / args.duration
    labels = [compact_label(label, 18) for label in sequence_trace_labels(args)]
    lane_y = [160, 220, 280, 340, 400, 460, 520]
    x0, x1 = 245, 1135

    rounded_rect(draw, (55, 112, 1220, 585), "#ffffff", "#cfcfcf", radius=14)
    text(draw, (78, 132), "TRACE WATERFALL", fonts["small"], PALETTE["muted"], "lm")
    text(draw, (960, 132), "latency budget", fonts["small"], PALETTE["muted"], "lm")
    draw.line([(x0, 132), (x1, 132)], fill=hex_to_rgb(PALETTE["line"]), width=3)
    for idx, tick in enumerate([0, 120, 240, 360, 480]):
        tx = x0 + idx * (x1 - x0) / 4
        draw.line([(tx, 126), (tx, 138)], fill=hex_to_rgb(PALETTE["line"]), width=2)
        text(draw, (tx, 112), f"{tick}ms", fonts["tiny"], PALETTE["muted"], "mm")

    for idx, y in enumerate(lane_y):
        draw.line([(x0, y), (x1, y)], fill=hex_to_rgb("#cfcfcf"), width=2)
        text(draw, (90, y + 6), labels[idx], fonts["small"], PALETTE["ink"], "lm", 3, "#ffffff")

    spans = [
        (0, 0.04, 0.92, PALETTE["route"], "request"),
        (1, 0.10, 0.30, PALETTE["route"], "edge"),
        (2, 0.22, 0.42, PALETTE["attribute"], "auth"),
        (3, 0.36, 0.62, PALETTE["atlas"], "inventory"),
        (4, 0.50, 0.70, PALETTE["damage"], "payment"),
        (5, 0.62, 0.82, PALETTE["tradeoff"], "db wait"),
        (6, 0.76, 0.92, PALETTE["gold"], "fallback"),
    ]
    active_span_count = 0
    for lane, start, end, color, label in spans:
        y = lane_y[lane]
        sx = x0 + start * (x1 - x0)
        ex = x0 + end * (x1 - x0)
        rounded_rect(draw, (sx, y - 15, ex, y + 15), "#ffffff", "#cfcfcf", radius=10)
        progress = ease((p - start) / max(0.01, end - start))
        if progress > 0:
            active_span_count += 1
            rounded_rect(draw, (sx, y - 15, sx + (ex - sx) * progress, y + 15), "#e7e7e7", color, radius=10)
        text(draw, ((sx + ex) / 2, y + 5), label, fonts["small"], PALETTE["ink"], "mm", 3, "#ffffff")

    for lane, start, _, color, _ in spans[1:6]:
        hx = x0 + start * (x1 - x0)
        draw.line([(hx, lane_y[lane - 1] + 18), (hx, lane_y[lane] - 18)], fill=hex_to_rgb(color), width=3)
        draw.ellipse((hx - 5, lane_y[lane] - 5, hx + 5, lane_y[lane] + 5), fill=hex_to_rgb(color))

    critical_visible = p > 0.46
    latency_budget_visible = p > 0.56
    retry_visible = p > 0.66
    fallback_visible = p > 0.78
    response_visible = p > 0.88
    if critical_visible:
        rounded_rect(draw, (505, 370, 942, 487), "#ffccd5", PALETTE["tradeoff"], radius=16)
        text(draw, (724, 392), "critical path", fonts["small"], PALETTE["tradeoff"], "mm", 3, "#ffffff")
        text(draw, (724, 418), f"{labels[3]} -> {labels[5]}", fonts["small"], PALETTE["ink"], "mm")
        draw.line([(612, 360), (790, 448)], fill=hex_to_rgb(PALETTE["tradeoff"]), width=4)
    if latency_budget_visible:
        draw_meter(draw, (930, 155, 1170, 222), "budget used", ease((p - 0.56) / 0.18), PALETTE["damage"], fonts)
    if retry_visible:
        rounded_rect(draw, (770, 226, 1030, 286), "#ffccd5", PALETTE["damage"], radius=14)
        text(draw, (900, 249), "retry branch", fonts["small"], PALETTE["damage"], "mm", 3, "#ffffff")
        text(draw, (900, 271), "slow span triggers retry", fonts["tiny"], PALETTE["ink"], "mm")
        draw.arc((720, 206, 1045, 356), 15, 168, fill=hex_to_rgb(PALETTE["damage"]), width=5)
    if fallback_visible:
        rounded_rect(draw, (785, 500, 1080, 568), "#e7e7e7", PALETTE["gold"], radius=14)
        text(draw, (932, 524), "fallback cache", fonts["small"], PALETTE["gold"], "mm", 3, "#ffffff")
        text(draw, (932, 548), labels[6], fonts["tiny"], PALETTE["ink"], "mm")
    if response_visible:
        rounded_rect(draw, (984, 590, 1190, 625), "#e7e7e7", PALETTE["defense"], radius=12)
        text(draw, (1087, 613), f"{labels[7]} returned", fonts["small"], PALETTE["defense"], "mm", 3, "#ffffff")

    visible_mechanism_count = [active_span_count >= 4, critical_visible, latency_budget_visible, retry_visible, fallback_visible, response_visible].count(True)
    draw_meter(draw, (90, 592, 335, 657), "spans revealed", active_span_count / len(spans), PALETTE["route"], fonts)
    draw_meter(draw, (360, 592, 605, 657), "critical path", ease((p - 0.46) / 0.16), PALETTE["tradeoff"], fonts)
    draw_meter(draw, (630, 592, 875, 657), "fallback readiness", ease((p - 0.78) / 0.14), PALETTE["gold"], fonts)
    beats = [
        "Trace the request before judging the service.",
        "Each span owns a visible slice of latency.",
        "The critical path is a route, not a guess.",
        "Retry and fallback should appear as separate branches.",
        "The response only lands after the budget story is visible.",
    ]
    beat_index = max(0, min(len(beats) - 1, int(p * len(beats))))
    rounded_rect(draw, (60, 665, 1220, 707), PALETTE["ink"], None, radius=12)
    return img


def render_sankey_flow_frame(
    second: float,
    args: argparse.Namespace,
    fonts: dict[str, ImageFont.ImageFont],
) -> Image.Image:
    width, height = args.width, args.height
    low_text_masonry = bool(getattr(args, "masonry_layout", False))
    canvas_width = round(width * 1.5) if low_text_masonry else width
    img = Image.new("RGB", (canvas_width, height), hex_to_rgb(PALETTE["paper"]))
    draw = ImageDraw.Draw(img)
    p = second / args.duration
    labels = [compact_label(label, 18) for label in sankey_flow_labels(args)]
    node_radius = 0 if low_text_masonry else 16
    callout_radius = 0 if low_text_masonry else 14

    if low_text_masonry:
        draw_masonry_megacanvas_base(draw, second, args)
        density_level = min(72, int(ease((p - 0.08) / 0.70) * 73))
        for row in range(6):
            for col in range(12):
                index = row * 12 + col
                active = index < density_level
                x = 78 + col * 40
                y = 124 + row * 26
                fill = gray_level(2 + ((row + col) % 4)) if active else gray_level(1)
                draw.rectangle((x, y, x + 30, y + 18), fill=hex_to_rgb(fill))
                if active and index % 11 == 0:
                    draw.rectangle((x, y, x + 6, y + 18), fill=hex_to_rgb(PALETTE["route"]))
        for col in range(4):
            x = 918 + col * 74
            meter_level = min(5, int(ease((p - 0.30 - col * 0.04) / 0.34) * 6))
            draw.rectangle((x, 404, x + 54, 518), fill=hex_to_rgb(gray_level(2 + col)))
            for level in range(5):
                active = level < meter_level
                y = 492 - level * 18
                draw.rectangle((x + 8, y, x + 46, y + 14), fill=hex_to_rgb(gray_level(5 if active else 3)))
                if active and level == meter_level - 1:
                    draw.rectangle((x + 8, y, x + 46, y + 6), fill=hex_to_rgb(PALETTE["route"]))
        for row in range(2):
            for col in range(28):
                index = row * 28 + col
                active = index < int(density_level * 0.75)
                x = 64 + col * 54
                y = 640 + row * 28
                fill = gray_level(2 + (index % 4)) if active else gray_level(1)
                draw.rectangle((x, y, x + 44, y + 18), fill=hex_to_rgb(fill))
                if active and index % 10 == 0:
                    draw.rectangle((x, y, x + 6, y + 18), fill=hex_to_rgb(PALETTE["route"]))
    else:
        rounded_rect(draw, (55, 112, 1220, 602), "#ffffff", "#cfcfcf", radius=14)
        text(draw, (88, 145), "SPLIT, LOSS, MERGE, AND OUTPUT", fonts["small"], PALETTE["muted"], "lm")

    nodes = [
        (130, 320, labels[0], PALETTE["route"], "#e7e7e7"),
        (340, 235, labels[1], PALETTE["defense"], "#e7e7e7"),
        (340, 435, labels[2], PALETTE["tradeoff"], gray_level(2)),
        (570, 215, labels[3], PALETTE["route"], "#e7e7e7"),
        (570, 365, labels[4], PALETTE["attribute"], "#e7e7e7"),
        (790, 300, labels[6], PALETTE["damage"], gray_level(3)),
        (1048, 320, labels[7], PALETTE["atlas"], "#e7e7e7"),
    ]
    flows = [
        ([(190, 320), (265, 275), (340, 235)], PALETTE["route"], 18),
        ([(190, 320), (265, 390), (340, 435)], PALETTE["tradeoff"], 12),
        ([(402, 235), (485, 215), (570, 215)], PALETTE["defense"], 15),
        ([(402, 435), (485, 365), (570, 365)], PALETTE["attribute"], 11),
        ([(632, 215), (710, 252), (790, 300)], PALETTE["route"], 14),
        ([(632, 365), (710, 335), (790, 300)], PALETTE["attribute"], 11),
        ([(852, 300), (950, 320), (1048, 320)], PALETTE["atlas"], 18),
    ]
    flow_progress = ease((p - 0.06) / 0.62)
    split_visible = p > 0.20
    loss_visible = p > 0.34
    bottleneck_visible = p > 0.56
    merge_visible = p > 0.66
    output_visible = p > 0.82

    for points, _, base_width in flows:
        draw_polyline(draw, points, PALETTE["line"], max(4, base_width - 4), 1)
    for idx, (points, color, band_width) in enumerate(flows):
        segment_progress = clamp(flow_progress * len(flows) - idx)
        red_family = {PALETTE["route"], PALETTE["attribute"], PALETTE["damage"], PALETTE["tradeoff"]}
        body_color = gray_level(6) if color in red_family else color
        draw_polyline(draw, points, body_color, max(4, band_width - 6), segment_progress)
        draw_polyline(draw, points, color, 3, segment_progress)
        if segment_progress > 0.12:
            token = point_on_polyline(points, segment_progress)
            draw.ellipse((token[0] - 8, token[1] - 8, token[0] + 8, token[1] + 8), fill=hex_to_rgb(PALETTE["gold"]))

    for x, y, label, color, fill in nodes:
        rounded_rect(draw, (x - 62, y - 34, x + 62, y + 34), fill, color, width=3, radius=node_radius)
        if low_text_masonry:
            draw.rectangle((x - 62, y - 34, x - 54, y + 34), fill=hex_to_rgb(color))
            draw.rectangle((x + 54, y - 34, x + 62, y + 34), fill=hex_to_rgb(gray_level(4)))
        else:
            text(draw, (x, y + 4), label, fonts.get("label", fonts["small"]), PALETTE["ink"], "mm", 3, "#ffffff")

    if split_visible:
        rounded_rect(draw, (235, 155, 445, 205), "#ffffff", PALETTE["route"], width=3, radius=callout_radius)
        if not low_text_masonry:
            text(draw, (340, 185), "split preserves value", fonts["small"], PALETTE["route"], "mm", 3, "#ffffff")
    if loss_visible:
        rounded_rect(draw, (235, 505, 445, 558), gray_level(2), PALETTE["tradeoff"], width=3, radius=callout_radius)
        if not low_text_masonry:
            text(draw, (340, 528), "loss is explicit", fonts["small"], PALETTE["tradeoff"], "mm", 3, "#ffffff")
            text(draw, (340, 548), labels[2], fonts["tiny"], PALETTE["ink"], "mm")
    if bottleneck_visible:
        rounded_rect(draw, (710, 170, 880, 238), gray_level(3), PALETTE["damage"], width=4, radius=node_radius)
        if not low_text_masonry:
            text(draw, (795, 197), "bottleneck", fonts["small"], PALETTE["damage"], "mm", 3, "#ffffff")
            text(draw, (795, 220), "limits merged flow", fonts["tiny"], PALETTE["ink"], "mm")
        draw.ellipse((760, 270, 820, 330), outline=hex_to_rgb(PALETTE["damage"]), width=5)
    if merge_visible:
        rounded_rect(draw, (645, 468, 895, 540), "#e7e7e7", PALETTE["defense"], width=3, radius=callout_radius)
        if not low_text_masonry:
            text(draw, (770, 495), labels[5], fonts["small"], PALETTE["defense"], "mm", 3, "#ffffff")
            text(draw, (770, 518), "streams recombine", fonts["tiny"], PALETTE["ink"], "mm")
    if output_visible:
        rounded_rect(draw, (932, 442, 1165, 535), "#e7e7e7", PALETTE["atlas"], width=4, radius=node_radius)
        if not low_text_masonry:
            text(draw, (1048, 474), "final output", fonts["small"], PALETTE["atlas"], "mm", 3, "#ffffff")
            text(draw, (1048, 501), labels[7], fonts["small"], PALETTE["ink"], "mm")

    if low_text_masonry:
        for meter_box, value, color in [
            ((86, 500, 268, 570), flow_progress, PALETTE["route"]),
            ((496, 500, 678, 570), ease((p - 0.26) / 0.45), PALETTE["defense"]),
            ((930, 182, 1165, 252), ease((p - 0.70) / 0.22), PALETTE["atlas"]),
        ]:
            x1, y1, x2, y2 = meter_box
            draw.rectangle(meter_box, fill=hex_to_rgb(gray_level(3)), outline=hex_to_rgb(PALETTE["line"]), width=2)
            fill_width = (x2 - x1) * clamp(value)
            if fill_width > 4:
                draw.rectangle((x1, y1, x1 + fill_width, y2), fill=hex_to_rgb(gray_level(5)))
                cap_width = min(8, fill_width)
                draw.rectangle((x1 + fill_width - cap_width, y1, x1 + fill_width, y2), fill=hex_to_rgb(color))
    else:
        draw_meter(draw, (86, 500, 268, 570), "input volume", flow_progress, PALETTE["route"], fonts)
        draw_meter(draw, (496, 500, 678, 570), "retained value", ease((p - 0.26) / 0.45), PALETTE["defense"], fonts)
        draw_meter(draw, (930, 182, 1165, 252), "output readiness", ease((p - 0.70) / 0.22), PALETTE["atlas"], fonts)

    beats = [
        "Start with one input stream.",
        "Split value from loss instead of hiding it.",
        "Transform streams before judging output.",
        "Merged flow can still be bottlenecked.",
        "Output appears only after loss and merge are visible.",
    ]
    beat_index = max(0, min(len(beats) - 1, int(p * len(beats))))
    return img


def render_swimlane_handoff_frame(
    second: float,
    args: argparse.Namespace,
    fonts: dict[str, ImageFont.ImageFont],
) -> Image.Image:
    img = Image.new("RGB", (args.width, args.height), PALETTE["paper"])
    draw = ImageDraw.Draw(img)
    p = clamp(second / max(args.duration, 0.001))
    lanes, handoffs = swimlane_handoff_labels(args)
    lane_y = [150, 265, 380, 495]
    lane_colors = ["#e7e7e7", "#e7e7e7", "#e7e7e7", "#e7e7e7"]
    lane_strokes = [PALETTE["route"], PALETTE["defense"], PALETTE["attribute"], PALETTE["atlas"]]

    rounded_rect(draw, (36, 116, 1244, 594), "#ffffff", "#cfcfcf", width=2, radius=16)

    for idx, y in enumerate(lane_y):
        rounded_rect(draw, (64, y - 38, 1216, y + 38), lane_colors[idx], "#cfcfcf", width=1, radius=14)
        text(draw, (92, y), compact_label(lanes[idx], 18), fonts["small"], lane_strokes[idx], "lm", 3, "#ffffff")
        draw.line((170, y - 36, 170, y + 36), fill=hex_to_rgb("#cfcfcf"), width=2)

    positions = [
        (230, lane_y[0], 0),
        (365, lane_y[1], 1),
        (505, lane_y[1], 1),
        (645, lane_y[2], 2),
        (505, lane_y[1] + 70, 1),
        (785, lane_y[2], 2),
        (935, lane_y[3], 3),
        (1085, lane_y[3], 3),
    ]
    handoff_progress = ease((p - 0.06) / 0.58)
    active_handoff_count = min(len(positions), int(math.floor(handoff_progress * len(positions) + 0.999)))
    sla_visible = p > 0.24
    rework_visible = p > 0.40
    approval_visible = p > 0.52
    escalation_visible = p > 0.67
    complete_visible = p > 0.82

    path_pairs = [(0, 1), (1, 2), (2, 3), (3, 6), (6, 7)]
    for start, end in path_pairs:
        active = active_handoff_count > end
        color = PALETTE["route"] if active else PALETTE["line"]
        x1, y1, _ = positions[start]
        x2, y2, _ = positions[end]
        draw_polyline(draw, [(x1 + 54, y1), ((x1 + x2) / 2, y1), ((x1 + x2) / 2, y2), (x2 - 54, y2)], color, 5 if active else 3, 1)

    if rework_visible:
        draw_polyline(draw, [(645, lane_y[2] + 38), (610, lane_y[2] + 92), (505, lane_y[1] + 104), (505, lane_y[1] + 40)], PALETTE["tradeoff"], 6, 1)
        rounded_rect(draw, (418, lane_y[1] + 88, 592, lane_y[1] + 142), "#ffccd5", PALETTE["tradeoff"], width=3, radius=14)
        text(draw, (505, lane_y[1] + 114), "rework loop", fonts["small"], PALETTE["tradeoff"], "mm", 3, "#ffffff")

    for idx, (x, y, lane_idx) in enumerate(positions):
        active = idx < active_handoff_count
        stroke = lane_strokes[lane_idx] if active else "#cfcfcf"
        fill = "#ffffff" if active else "#e7e7e7"
        rounded_rect(draw, (x - 56, y - 28, x + 56, y + 28), fill, stroke, width=3 if active else 2, radius=14)
        text(draw, (x, y + 1), compact_label(handoffs[idx], 15), fonts["tiny"], PALETTE["ink"], "mm", 3, "#ffffff")
        if active:
            draw.ellipse((x - 63, y - 35, x - 45, y - 17), fill=hex_to_rgb(stroke))

    if sla_visible:
        draw_meter(draw, (884, 142, 1156, 212), "SLA pressure", ease((p - 0.20) / 0.34), PALETTE["damage"], fonts)
        rounded_rect(draw, (720, 130, 852, 182), "#ffccd5", PALETTE["damage"], width=3, radius=12)
        text(draw, (786, 156), "SLA gate", fonts["small"], PALETTE["damage"], "mm", 3, "#ffffff")
    if approval_visible:
        diamond = [(645, lane_y[2] - 54), (692, lane_y[2]), (645, lane_y[2] + 54), (598, lane_y[2])]
        draw.polygon(diamond, fill=hex_to_rgb("#ffccd5"), outline=hex_to_rgb(PALETTE["damage"]))
        draw.line(diamond + [diamond[0]], fill=hex_to_rgb(PALETTE["damage"]), width=4)
        text(draw, (645, lane_y[2]), "approval", fonts["small"], PALETTE["damage"], "mm", 3, "#ffffff")
    if escalation_visible:
        draw_polyline(draw, [(785, lane_y[2] - 38), (820, lane_y[1] - 54), (950, lane_y[1] - 54), (1010, lane_y[2] - 20)], PALETTE["tradeoff"], 6, 1)
        rounded_rect(draw, (872, lane_y[1] - 88, 1055, lane_y[1] - 28), "#ffccd5", PALETTE["tradeoff"], width=3, radius=14)
        text(draw, (964, lane_y[1] - 58), "escalation path", fonts["small"], PALETTE["tradeoff"], "mm", 3, "#ffffff")
    if complete_visible:
        rounded_rect(draw, (1020, 548, 1194, 586), "#e7e7e7", PALETTE["defense"], width=3, radius=12)
        text(draw, (1107, 568), "completed handoff", fonts["small"], PALETTE["defense"], "mm", 3, "#ffffff")

    beats = [
        "Start with a named requester and intake lane.",
        "Each handoff moves across an owner boundary.",
        "SLA pressure becomes visible before approval.",
        "Rework and escalation are explicit routes.",
        "Completion only appears after release ownership is clear.",
    ]
    beat_index = max(0, min(len(beats) - 1, int(p * len(beats))))
    return img


def render_risk_bowtie_frame(
    second: float,
    args: argparse.Namespace,
    fonts: dict[str, ImageFont.ImageFont],
) -> Image.Image:
    img = Image.new("RGB", (args.width, args.height), PALETTE["paper"])
    draw = ImageDraw.Draw(img)
    p = clamp(second / max(args.duration, 0.001))
    threats, barriers, consequences = risk_bowtie_labels(args)
    threat_points = [(142, 170), (142, 270), (142, 370), (142, 470)]
    preventive_points = [(380, 225), (380, 330), (380, 435)]
    mitigative_points = [(900, 225), (900, 330), (900, 435)]
    consequence_points = [(1130, 170), (1130, 270), (1130, 370), (1130, 470)]
    top_event = (640, 330)

    active_threat_count = min(len(threat_points), int(math.floor(ease((p - 0.05) / 0.45) * len(threat_points) + 0.999)))
    preventive_visible = p > 0.18
    top_event_visible = p > 0.32
    mitigative_visible = p > 0.48
    consequence_visible = p > 0.62
    degraded_visible = p > 0.74
    action_visible = p > 0.84

    rounded_rect(draw, (44, 112, 1236, 592), "#ffffff", "#cfcfcf", width=2, radius=16)
    text(draw, (120, 138), "THREATS", fonts["tiny"], PALETTE["muted"], "mm")
    text(draw, (380, 138), "PREVENT", fonts["tiny"], PALETTE["muted"], "mm")
    text(draw, (640, 138), "TOP EVENT", fonts["tiny"], PALETTE["muted"], "mm")
    text(draw, (900, 138), "MITIGATE", fonts["tiny"], PALETTE["muted"], "mm")
    text(draw, (1130, 138), "CONSEQUENCES", fonts["tiny"], PALETTE["muted"], "mm")

    for point in threat_points:
        for barrier in preventive_points:
            draw_polyline(draw, [point, barrier], PALETTE["line"], 2, 1)
    for barrier in preventive_points:
        draw_polyline(draw, [barrier, top_event], PALETTE["line"], 3, 1)
    for barrier in mitigative_points:
        draw_polyline(draw, [top_event, barrier], PALETTE["line"], 3, 1)
    for barrier in mitigative_points:
        for point in consequence_points:
            draw_polyline(draw, [barrier, point], PALETTE["line"], 2, 1)

    for idx, (x, y) in enumerate(threat_points):
        active = idx < active_threat_count
        rounded_rect(draw, (x - 78, y - 28, x + 78, y + 28), "#ffccd5" if active else "#e7e7e7", PALETTE["damage"] if active else "#ccd6e3", width=3 if active else 2, radius=14)
        text(draw, (x, y + 4), compact_label(threats[idx], 18), fonts["tiny"], PALETTE["ink"], "mm", 3, "#ffffff")

    for idx, (x, y) in enumerate(preventive_points):
        active = preventive_visible
        rounded_rect(draw, (x - 82, y - 30, x + 82, y + 30), "#e7e7e7" if active else "#e7e7e7", PALETTE["route"] if active else "#ccd6e3", width=3 if active else 2, radius=14)
        text(draw, (x, y + 5), compact_label(barriers[idx], 18), fonts["small"], PALETTE["ink"], "mm", 3, "#ffffff")
    if top_event_visible:
        diamond = [(640, 260), (705, 330), (640, 400), (575, 330)]
        draw.polygon(diamond, fill=hex_to_rgb("#ffccd5"), outline=hex_to_rgb(PALETTE["tradeoff"]))
        draw.line(diamond + [diamond[0]], fill=hex_to_rgb(PALETTE["tradeoff"]), width=5)
        text(draw, top_event, "top event", fonts["body"], PALETTE["tradeoff"], "mm", 3, "#ffffff")
    else:
        draw.polygon([(640, 280), (690, 330), (640, 380), (590, 330)], fill=hex_to_rgb("#e7e7e7"), outline=hex_to_rgb("#ccd6e3"))

    for idx, (x, y) in enumerate(mitigative_points):
        active = mitigative_visible
        rounded_rect(draw, (x - 82, y - 30, x + 82, y + 30), "#e7e7e7" if active else "#e7e7e7", PALETTE["defense"] if active else "#ccd6e3", width=3 if active else 2, radius=14)
        text(draw, (x, y + 5), compact_label(barriers[idx + 3], 18), fonts["small"], PALETTE["ink"], "mm", 3, "#ffffff")

    for idx, (x, y) in enumerate(consequence_points):
        active = consequence_visible
        rounded_rect(draw, (x - 82, y - 28, x + 82, y + 28), "#ffccd5" if active else "#e7e7e7", PALETTE["damage"] if active else "#ccd6e3", width=3 if active else 2, radius=14)
        text(draw, (x, y + 4), compact_label(consequences[idx], 18), fonts["tiny"], PALETTE["ink"], "mm", 3, "#ffffff")

    if active_threat_count >= 3:
        for idx, point in enumerate(threat_points[:active_threat_count]):
            draw_polyline(draw, [point, preventive_points[min(idx, 2)]], PALETTE["damage"], 5, 1)
    if preventive_visible:
        for barrier in preventive_points:
            draw_polyline(draw, [barrier, top_event], PALETTE["route"], 5, 1)
    if mitigative_visible:
        for barrier in mitigative_points:
            draw_polyline(draw, [top_event, barrier], PALETTE["defense"], 5, 1)
    if consequence_visible:
        for idx, point in enumerate(consequence_points):
            draw_polyline(draw, [mitigative_points[min(idx, 2)], point], PALETTE["damage"], 4, 1)
    if degraded_visible:
        rounded_rect(draw, (485, 475, 795, 545), "#ffccd5", PALETTE["damage"], width=4, radius=16)
        text(draw, (640, 500), "degraded barrier", fonts["small"], PALETTE["damage"], "mm", 3, "#ffffff")
        text(draw, (640, 523), "control gap stays visible", fonts["tiny"], PALETTE["ink"], "mm")
    if action_visible:
        rounded_rect(draw, (470, 176, 810, 230), "#e7e7e7", PALETTE["atlas"], width=4, radius=16)
        text(draw, (640, 204), "action: repair the weakest barrier", fonts["small"], PALETTE["atlas"], "mm", 3, "#ffffff")

    draw_meter(draw, (80, 515, 285, 575), "threat pressure", ease((p - 0.06) / 0.42), PALETTE["damage"], fonts)
    draw_meter(draw, (990, 515, 1200, 575), "residual risk", 1 - ease((p - 0.58) / 0.32), PALETTE["tradeoff"], fonts)
    beats = [
        "Name the threats before judging controls.",
        "Preventive barriers sit before the top event.",
        "Mitigations reduce consequences after the event.",
        "Degraded barriers keep the control gap visible.",
        "Action targets the weakest barrier, not the symptom.",
    ]
    beat_index = max(0, min(len(beats) - 1, int(p * len(beats))))
    return img


def render_scenario_tree_frame(
    second: float,
    args: argparse.Namespace,
    fonts: dict[str, ImageFont.ImageFont],
) -> Image.Image:
    img = Image.new("RGB", (args.width, args.height), PALETTE["paper"])
    draw = ImageDraw.Draw(img)
    p = clamp(second / max(args.duration, 0.001))
    scenarios, probabilities = scenario_tree_labels(args)
    root = (150, 330)
    branches = [(395, 205), (395, 330), (395, 455)]
    outcomes = [(690, 165), (690, 265), (690, 395), (690, 505)]
    decision = (1020, 330)
    fallback = (1018, 502)
    active_scenario_count = min(7, int(math.floor(ease((p - 0.05) / 0.55) * 7 + 0.999)))
    probability_visible = p > 0.20
    risk_visible = p > 0.35
    upside_visible = p > 0.50
    decision_visible = p > 0.64
    fallback_visible = p > 0.76
    outcome_visible = p > 0.86

    rounded_rect(draw, (44, 112, 1236, 592), "#ffffff", "#cfcfcf", width=2, radius=16)
    text(draw, (150, 138), "DECISION", fonts["tiny"], PALETTE["muted"], "mm")
    text(draw, (395, 138), "SCENARIOS", fonts["tiny"], PALETTE["muted"], "mm")
    text(draw, (690, 138), "OUTCOMES", fonts["tiny"], PALETTE["muted"], "mm")
    text(draw, (1020, 138), "CHOICE", fonts["tiny"], PALETTE["muted"], "mm")

    def node(center: tuple[int, int], label: str, color: str, fill: str, active: bool = True, w: int = 170) -> None:
        x, y = center
        rounded_rect(draw, (x - w // 2, y - 30, x + w // 2, y + 30), fill if active else "#e7e7e7", color if active else "#ccd6e3", width=3 if active else 2, radius=16)
        text(draw, (x, y + 5), compact_label(label, 18), fonts["small"], PALETTE["ink"], "mm", 3, "#ffffff")

    node(root, scenarios[0], PALETTE["route"], "#e7e7e7", True, 178)
    for idx, point in enumerate(branches):
        active = idx + 1 < active_scenario_count
        draw_polyline(draw, [root, point], PALETTE["route"] if active else PALETTE["line"], 5 if active else 3, 1)
        node(point, scenarios[idx + 1], [PALETTE["defense"], PALETTE["attribute"], PALETTE["damage"]][idx], ["#e7e7e7", "#e7e7e7", "#ffccd5"][idx], active, 178)
        if probability_visible:
            label_positions = [(278, 245), (278, 318), (278, 408)]
            lx, ly = label_positions[idx]
            rounded_rect(draw, (lx - 72, ly - 17, lx + 72, ly + 17), "#ffffff", "#cfcfcf", width=2, radius=10)
            text(draw, (lx, ly + 4), probabilities[idx], fonts["tiny"], PALETTE["ink"], "mm", 3, "#ffffff")

    outcome_links = [(branches[0], outcomes[0]), (branches[0], outcomes[1]), (branches[1], outcomes[2]), (branches[2], outcomes[3])]
    for idx, (start, end) in enumerate(outcome_links):
        active = idx + 4 < active_scenario_count
        draw_polyline(draw, [start, end], PALETTE["route"] if active else PALETTE["line"], 5 if active else 3, 1)
        node(end, scenarios[min(idx + 3, 6)], [PALETTE["defense"], PALETTE["route"], PALETTE["attribute"], PALETTE["damage"]][idx], ["#e7e7e7", "#e7e7e7", "#e7e7e7", "#ffccd5"][idx], active, 180)

    if risk_visible:
        rounded_rect(draw, (790, 420, 945, 478), "#ffccd5", PALETTE["damage"], width=3, radius=14)
        text(draw, (868, 448), "risk branch", fonts["small"], PALETTE["damage"], "mm", 3, "#ffffff")
    if upside_visible:
        rounded_rect(draw, (790, 184, 950, 242), "#e7e7e7", PALETTE["defense"], width=3, radius=14)
        text(draw, (870, 212), "upside branch", fonts["small"], PALETTE["defense"], "mm", 3, "#ffffff")
    if decision_visible:
        node(decision, "decision gate", PALETTE["atlas"], "#e7e7e7", True, 190)
        for point in outcomes[:3]:
            draw_polyline(draw, [point, decision], PALETTE["atlas"], 5, 1)
    if fallback_visible:
        node(fallback, probabilities[3], PALETTE["gold"], "#e7e7e7", True, 190)
        draw_polyline(draw, [outcomes[3], fallback], PALETTE["gold"], 5, 1)
    if outcome_visible:
        rounded_rect(draw, (930, 548, 1198, 586), "#e7e7e7", PALETTE["defense"], width=3, radius=12)
        text(draw, (1064, 568), "selected outcome is source-aware", fonts["small"], PALETTE["defense"], "mm", 3, "#ffffff")

    draw_meter(draw, (70, 520, 290, 575), "uncertainty", 1 - ease((p - 0.58) / 0.32), PALETTE["damage"], fonts)
    draw_meter(draw, (505, 520, 735, 575), "evidence weight", ease((p - 0.20) / 0.45), PALETTE["route"], fonts)
    visible_mechanism_count = [active_scenario_count >= 4, probability_visible, risk_visible, upside_visible, decision_visible, fallback_visible, outcome_visible].count(True)
    beats = [
        "Start with one decision point.",
        "Branch into base, upside, and downside scenarios.",
        "Probabilities and evidence weights appear before choice.",
        "Fallback stays visible as an alternate route.",
        "Outcome is selected only after branches are visible.",
    ]
    beat_index = max(0, min(len(beats) - 1, int(p * len(beats))))
    return img


def render_skill_tree_route_frame(
    second: float,
    args: argparse.Namespace,
    fonts: dict[str, ImageFont.ImageFont],
) -> Image.Image:
    img = Image.new("RGB", (args.width, args.height), PALETTE["paper"])
    draw = ImageDraw.Draw(img)
    p = clamp(second / max(args.duration, 0.001))
    route_labels, checkpoint_labels = skill_tree_route_labels(args)
    route_points = [
        (128, 345),
        (255, 318),
        (385, 292),
        (535, 245),
        (680, 328),
        (825, 328),
        (965, 295),
        (1100, 245),
    ]
    active_route_node_count = min(
        len(route_points),
        int(math.floor(ease((p - 0.04) / 0.54) * len(route_points) + 0.999)),
    )
    damage_cluster_visible = p > 0.22
    defense_cluster_visible = p > 0.34
    attribute_bridge_visible = p > 0.48
    keystone_tradeoff_visible = p > 0.62
    respec_visible = p > 0.74
    late_cluster_visible = p > 0.86

    rounded_rect(draw, (44, 112, 1236, 592), "#ffffff", "#cfcfcf", width=2, radius=16)
    text(draw, (112, 140), "ROUTE PLAN", fonts["tiny"], PALETTE["muted"], "mm")
    text(draw, (520, 140), "CLUSTERS", fonts["tiny"], PALETTE["muted"], "mm")
    text(draw, (830, 140), "TRADEOFFS", fonts["tiny"], PALETTE["muted"], "mm")
    text(draw, (1100, 140), "LATE PLAN", fonts["tiny"], PALETTE["muted"], "mm")

    for a, b in zip(route_points, route_points[1:]):
        draw_polyline(draw, [a, b], PALETTE["line"], 4, 1)
    for idx, (a, b) in enumerate(zip(route_points, route_points[1:])):
        if idx < max(0, active_route_node_count - 1):
            draw_polyline(draw, [a, b], PALETTE["route"], 8, 1)

    node_colors = [
        PALETTE["route"],
        PALETTE["route"],
        PALETTE["damage"],
        PALETTE["damage"],
        PALETTE["attribute"],
        PALETTE["tradeoff"],
        PALETTE["gold"],
        PALETTE["atlas"],
    ]
    for idx, point in enumerate(route_points):
        active = 1.0 if idx < active_route_node_count else 0.0
        shape = "diamond" if idx == 5 else "circle"
        draw_node(draw, point, compact_label(route_labels[idx], 13), node_colors[idx], active, fonts, shape, ghost_label=True)

    if damage_cluster_visible:
        damage_nodes = [(345, 185), (478, 170), (575, 205)]
        draw_polyline(draw, [route_points[2], damage_nodes[0], damage_nodes[1], damage_nodes[2]], PALETTE["damage"], 7, 1)
        for x, y in damage_nodes:
            draw.ellipse((x - 15, y - 15, x + 15, y + 15), fill=hex_to_rgb("#ffffff"), outline=hex_to_rgb(PALETTE["damage"]), width=4)
        rounded_rect(draw, (414, 132, 596, 184), "#ffccd5", PALETTE["damage"], width=3, radius=14)
        text(draw, (505, 160), compact_label(route_labels[2], 18), fonts["small"], PALETTE["damage"], "mm", 3, "#ffffff")
        draw_meter(draw, (690, 178, 920, 236), "damage threshold", ease((p - 0.22) / 0.24), PALETTE["damage"], fonts)

    if defense_cluster_visible:
        defense_nodes = [(368, 430), (510, 480), (642, 438)]
        draw_polyline(draw, [route_points[2], defense_nodes[0], defense_nodes[1], defense_nodes[2]], PALETTE["defense"], 7, 1)
        for x, y in defense_nodes:
            draw.ellipse((x - 15, y - 15, x + 15, y + 15), fill=hex_to_rgb("#ffffff"), outline=hex_to_rgb(PALETTE["defense"]), width=4)
        rounded_rect(draw, (414, 456, 600, 508), "#e7e7e7", PALETTE["defense"], width=3, radius=14)
        text(draw, (507, 484), compact_label(route_labels[3], 18), fonts["small"], PALETTE["defense"], "mm", 3, "#ffffff")
        draw_meter(draw, (724, 438, 954, 496), "defense layer", ease((p - 0.34) / 0.24), PALETTE["defense"], fonts)

    if attribute_bridge_visible:
        rounded_rect(draw, (604, 292, 758, 365), "#e7e7e7", PALETTE["attribute"], width=4, radius=18)
        text(draw, (681, 322), "attribute bridge", fonts["small"], PALETTE["attribute"], "mm", 3, "#ffffff")
        text(draw, (681, 346), compact_label(route_labels[4], 18), fonts["tiny"], PALETTE["ink"], "mm")

    if keystone_tradeoff_visible:
        diamond = [(825, 254), (888, 328), (825, 402), (762, 328)]
        draw.polygon(diamond, fill=hex_to_rgb("#ffccd5"), outline=hex_to_rgb(PALETTE["tradeoff"]))
        draw.line(diamond + [diamond[0]], fill=hex_to_rgb(PALETTE["tradeoff"]), width=5)
        text(draw, (825, 318), "keystone", fonts["small"], PALETTE["tradeoff"], "mm", 3, "#ffffff")
        text(draw, (825, 342), compact_label(route_labels[5], 17), fonts["tiny"], PALETTE["ink"], "mm")
        draw_meter(draw, (928, 362, 1168, 420), "tradeoff cost", ease((p - 0.62) / 0.20), PALETTE["tradeoff"], fonts)

    if respec_visible:
        respec_path = [route_points[5], (930, 450), (760, 526), (520, 525)]
        draw_polyline(draw, respec_path, PALETTE["gold"], 6, 1)
        text(draw, (875, 474), "respec route", fonts["small"], PALETTE["gold"], "mm", 3, "#ffffff")
        text(draw, (875, 496), compact_label(route_labels[6], 18), fonts["tiny"], PALETTE["ink"], "mm", 3, "#ffffff")

    if late_cluster_visible:
        late_nodes = [(1050, 205), (1160, 285), (1070, 395)]
        draw_polyline(draw, [route_points[7], late_nodes[1], late_nodes[2]], PALETTE["atlas"], 7, 1)
        for x, y in late_nodes:
            draw.ellipse((x - 15, y - 15, x + 15, y + 15), fill=hex_to_rgb("#ffffff"), outline=hex_to_rgb(PALETTE["atlas"]), width=4)
        rounded_rect(draw, (990, 456, 1200, 520), "#e7e7e7", PALETTE["atlas"], width=4, radius=16)
        text(draw, (1095, 482), "late specialization", fonts["small"], PALETTE["atlas"], "mm", 3, "#ffffff")
        text(draw, (1095, 505), "kept separate from core path", fonts["tiny"], PALETTE["ink"], "mm")

    checkpoint_y = 570
    for idx, label_value in enumerate(checkpoint_labels):
        x = 150 + idx * 230
        active = p > 0.16 + idx * 0.14
        rounded_rect(
            draw,
            (x - 92, checkpoint_y - 28, x + 92, checkpoint_y + 18),
            "#ffffff" if active else "#e7e7e7",
            PALETTE["route"] if active else "#ccd6e3",
            width=3 if active else 2,
            radius=13,
        )
        text(draw, (x, checkpoint_y - 2), compact_label(label_value, 19), fonts["tiny"], PALETTE["ink"], "mm", 3, "#ffffff")

    visible_mechanism_count = [
        active_route_node_count >= 4,
        damage_cluster_visible,
        defense_cluster_visible,
        attribute_bridge_visible,
        keystone_tradeoff_visible,
        respec_visible,
        late_cluster_visible,
    ].count(True)
    beats = [
        "Lock the playstyle before spending travel nodes.",
        "Damage and defense clusters should be evaluated separately.",
        "Attribute bridges are costs, not free progress.",
        "Keystones are tradeoffs that need a respec checkpoint.",
        "Late specialization stays separate from the core route.",
    ]
    beat_index = max(0, min(len(beats) - 1, int(p * len(beats))))
    return img


def render_evidence_ladder_frame(
    second: float,
    args: argparse.Namespace,
    fonts: dict[str, ImageFont.ImageFont],
) -> Image.Image:
    img = Image.new("RGB", (args.width, args.height), PALETTE["paper"])
    draw = ImageDraw.Draw(img)
    p = clamp(second / max(args.duration, 0.001))
    claim_labels, evidence_labels = evidence_ladder_labels(args)
    claim_visible = p > 0.08
    active_evidence_count = min(6, int(math.floor(ease((p - 0.10) / 0.58) * 6 + 0.999)))
    counter_evidence_visible = p > 0.42
    gap_visible = p > 0.56
    confidence_visible = p > 0.68
    recommendation_visible = p > 0.82

    rounded_rect(draw, (44, 112, 1236, 592), "#ffffff", "#cfcfcf", width=2, radius=16)
    text(draw, (185, 140), "CLAIM", fonts["tiny"], PALETTE["muted"], "mm")
    text(draw, (560, 140), "EVIDENCE LADDER", fonts["tiny"], PALETTE["muted"], "mm")
    text(draw, (845, 140), "COUNTERWEIGHT", fonts["tiny"], PALETTE["muted"], "mm")
    text(draw, (1080, 140), "DECISION", fonts["tiny"], PALETTE["muted"], "mm")

    claim_box = (72, 216, 300, 322)
    rounded_rect(draw, claim_box, "#e7e7e7", PALETTE["route"] if claim_visible else "#cfcfcf", width=4 if claim_visible else 2, radius=18)
    text(draw, (186, 252), compact_label(claim_labels[0], 22), fonts["small"], PALETTE["ink"], "mm", 3, "#ffffff")
    text(draw, (186, 285), compact_label(claim_labels[1], 22), fonts["tiny"], PALETTE["muted"], "mm", 3, "#ffffff")

    ladder_points = [(430, 500), (500, 420), (570, 340), (640, 260)]
    for a, b in zip(ladder_points, ladder_points[1:]):
        draw_polyline(draw, [a, b], PALETTE["line"], 4, 1)
    active_ladder_segments = min(3, max(0, active_evidence_count - 1))
    for idx, (a, b) in enumerate(zip(ladder_points, ladder_points[1:])):
        if idx < active_ladder_segments:
            draw_polyline(draw, [a, b], PALETTE["route"], 7, 1)

    for idx, point in enumerate(ladder_points):
        active = idx < active_evidence_count
        x, y = point
        rounded_rect(draw, (x - 86, y - 28, x + 86, y + 28), "#ffffff" if active else "#e7e7e7", PALETTE["route"] if active else "#cfcfcf", width=3 if active else 2, radius=15)
        text(draw, (x, y + 5), compact_label(evidence_labels[idx], 18), fonts["tiny"], PALETTE["ink"], "mm", 3, "#ffffff")

    if claim_visible:
        draw_polyline(draw, [(300, 270), (372, 340), ladder_points[0]], PALETTE["route"], 5, 1)
    if not counter_evidence_visible:
        rounded_rect(draw, (760, 260, 950, 332), "#ffffff", "#cfcfcf", width=2, radius=16)
        text(draw, (855, 298), "counterweight", fonts["tiny"], PALETTE["muted"], "mm")
    if counter_evidence_visible:
        rounded_rect(draw, (760, 260, 950, 332), "#ffccd5", PALETTE["damage"], width=4, radius=16)
        text(draw, (855, 288), compact_label(evidence_labels[4], 20), fonts["small"], PALETTE["damage"], "mm", 3, "#ffffff")
        text(draw, (855, 312), compact_label(claim_labels[2], 20), fonts["tiny"], PALETTE["ink"], "mm")
        draw_polyline(draw, [ladder_points[2], (720, 328), (760, 296)], PALETTE["damage"], 6, 1)
    if not gap_visible:
        rounded_rect(draw, (760, 425, 950, 505), "#e7e7e7", "#cfcfcf", width=2, radius=16)
        text(draw, (855, 466), "source gap", fonts["tiny"], PALETTE["muted"], "mm")
    if gap_visible:
        rounded_rect(draw, (760, 425, 950, 505), "#e7e7e7", PALETTE["gold"], width=4, radius=16)
        text(draw, (855, 456), "source gap", fonts["small"], PALETTE["gold"], "mm", 3, "#ffffff")
        text(draw, (855, 482), compact_label(evidence_labels[5], 20), fonts["tiny"], PALETTE["ink"], "mm")
        draw_polyline(draw, [ladder_points[0], (700, 470), (760, 466)], PALETTE["gold"], 6, 1)
    if not confidence_visible:
        rounded_rect(draw, (1000, 228, 1190, 290), "#e7e7e7", "#cfcfcf", width=2, radius=10)
        text(draw, (1095, 262), "confidence", fonts["tiny"], PALETTE["muted"], "mm")
        rounded_rect(draw, (1000, 310, 1190, 372), "#e7e7e7", "#ffccd5", width=2, radius=10)
        text(draw, (1095, 344), "uncertainty", fonts["tiny"], PALETTE["muted"], "mm")
    if confidence_visible:
        draw_meter(draw, (1000, 228, 1190, 290), "confidence", ease((p - 0.58) / 0.28), PALETTE["defense"], fonts)
        draw_meter(draw, (1000, 310, 1190, 372), "uncertainty", 1 - ease((p - 0.58) / 0.28), PALETTE["damage"], fonts)
    if recommendation_visible:
        rounded_rect(draw, (990, 438, 1202, 520), "#e7e7e7", PALETTE["defense"], width=4, radius=18)
        text(draw, (1096, 468), compact_label(claim_labels[3], 22), fonts["small"], PALETTE["defense"], "mm", 3, "#ffffff")
        text(draw, (1096, 494), "recommend after evidence", fonts["tiny"], PALETTE["ink"], "mm")

    visible_mechanism_count = [
        claim_visible,
        active_evidence_count >= 4,
        counter_evidence_visible,
        gap_visible,
        confidence_visible,
        recommendation_visible,
    ].count(True)
    beats = [
        "State the claim before scoring the sources.",
        "Evidence rises in tiers, not as a flat list.",
        "Counterevidence stays visible beside support.",
        "Source gaps lower confidence before recommendation.",
        "Recommendation arrives only after confidence is explicit.",
    ]
    beat_index = max(0, min(len(beats) - 1, int(p * len(beats))))
    return img


def render_layered_architecture_frame(
    second: float,
    args: argparse.Namespace,
    fonts: dict[str, ImageFont.ImageFont],
) -> Image.Image:
    img = Image.new("RGB", (args.width, args.height), PALETTE["paper"])
    draw = ImageDraw.Draw(img)
    p = clamp(second / max(args.duration, 0.001))
    layer_labels, concern_labels = layered_architecture_labels(args)
    active_layer_count = min(6, int(math.floor(ease((p - 0.07) / 0.55) * 6 + 0.999)))
    cross_cutting_visible = p > 0.28
    failure_path_visible = p > 0.46
    observability_visible = p > 0.62
    rollout_visible = p > 0.80

    rounded_rect(draw, (44, 112, 1236, 592), "#ffffff", "#cfcfcf", width=2, radius=16)
    text(draw, (185, 140), "REQUEST PATH", fonts["tiny"], PALETTE["muted"], "mm")
    text(draw, (562, 140), "LAYERS", fonts["tiny"], PALETTE["muted"], "mm")
    text(draw, (930, 140), "CROSS-CUTTING", fonts["tiny"], PALETTE["muted"], "mm")

    layer_gray_fills = [gray_level(1), gray_level(2), gray_level(3), gray_level(2), gray_level(3), gray_level(4)]
    layer_gray_strokes = [gray_level(3), gray_level(3), gray_level(4), gray_level(4), gray_level(5), gray_level(5)]
    layer_boxes = []
    for idx, label_value in enumerate(layer_labels):
        y = 178 + idx * 62
        active = idx < active_layer_count
        fill = layer_gray_fills[idx % len(layer_gray_fills)]
        stroke = PALETTE["route"] if idx < 2 else PALETTE["defense"] if idx < 4 else PALETTE["atlas"]
        ghost_stroke = layer_gray_strokes[idx % len(layer_gray_strokes)]
        rounded_rect(draw, (320, y, 780, y + 48), fill, stroke if active else ghost_stroke, width=3 if active else 2, radius=14)
        text(draw, (550, y + 29), compact_label(label_value, 30), fonts["small"], PALETTE["ink"], "mm", 3, "#ffffff")
        layer_boxes.append((320, y, 780, y + 48, stroke))

    path_x = 185
    for idx, (_, y1, _, y2, _) in enumerate(layer_boxes):
        center = (path_x, (y1 + y2) // 2)
        active = idx < active_layer_count
        draw.ellipse((center[0] - 18, center[1] - 18, center[0] + 18, center[1] + 18), fill=hex_to_rgb("#ffffff"), outline=hex_to_rgb(PALETTE["route"] if active else "#cfcfcf"), width=4 if active else 2)
        if idx > 0:
            prev_y = (layer_boxes[idx - 1][1] + layer_boxes[idx - 1][3]) // 2
            draw_polyline(draw, [(path_x, prev_y + 18), (path_x, center[1] - 18)], PALETTE["route"] if active else PALETTE["line"], 5 if active else 3, 1)
    if active_layer_count:
        draw_polyline(draw, [(203, (layer_boxes[min(active_layer_count - 1, 5)][1] + layer_boxes[min(active_layer_count - 1, 5)][3]) // 2), (320, (layer_boxes[min(active_layer_count - 1, 5)][1] + layer_boxes[min(active_layer_count - 1, 5)][3]) // 2)], PALETTE["route"], 5, 1)

    if not cross_cutting_visible:
        rounded_rect(draw, (840, 180, 1135, 238), "#e7e7e7", "#cfcfcf", width=2, radius=16)
        text(draw, (988, 210), "cross-cutting policy", fonts["tiny"], PALETTE["muted"], "mm")
    if cross_cutting_visible:
        rounded_rect(draw, (840, 180, 1135, 238), "#e7e7e7", PALETTE["attribute"], width=4, radius=16)
        text(draw, (988, 210), compact_label(concern_labels[0], 28), fonts["small"], PALETTE["attribute"], "mm", 3, "#ffffff")
        draw_polyline(draw, [(838, 210), (782, 210), (782, 500), (838, 500)], PALETTE["attribute"], 5, 1)
    if not failure_path_visible:
        rounded_rect(draw, (838, 278, 1135, 338), "#ffccd5", "#cfcfcf", width=2, radius=16)
        text(draw, (986, 308), "failure route", fonts["tiny"], PALETTE["muted"], "mm")
    if failure_path_visible:
        rounded_rect(draw, (838, 278, 1135, 338), "#ffccd5", PALETTE["damage"], width=4, radius=16)
        text(draw, (986, 308), compact_label(concern_labels[1], 28), fonts["small"], PALETTE["damage"], "mm", 3, "#ffffff")
        draw_polyline(draw, [(780, 326), (835, 308)], PALETTE["damage"], 6, 1)
    if not observability_visible:
        rounded_rect(draw, (838, 378, 1135, 438), "#e7e7e7", "#cfcfcf", width=2, radius=16)
        text(draw, (986, 408), "observability", fonts["tiny"], PALETTE["muted"], "mm")
    if observability_visible:
        rounded_rect(draw, (838, 378, 1135, 438), "#e7e7e7", PALETTE["atlas"], width=4, radius=16)
        text(draw, (986, 408), compact_label(concern_labels[2], 28), fonts["small"], PALETTE["atlas"], "mm", 3, "#ffffff")
        draw_meter(draw, (875, 452, 1110, 510), "signal coverage", ease((p - 0.62) / 0.20), PALETTE["atlas"], fonts)
    if not rollout_visible:
        rounded_rect(draw, (838, 528, 1135, 574), "#e7e7e7", "#cfcfcf", width=2, radius=16)
        text(draw, (986, 555), "rollout gate", fonts["tiny"], PALETTE["muted"], "mm")
    if rollout_visible:
        rounded_rect(draw, (838, 528, 1135, 574), "#e7e7e7", PALETTE["defense"], width=4, radius=16)
        text(draw, (986, 555), compact_label(concern_labels[3], 28), fonts["small"], PALETTE["defense"], "mm", 3, "#ffffff")

    visible_mechanism_count = [
        active_layer_count >= 4,
        active_layer_count == 6,
        cross_cutting_visible,
        failure_path_visible,
        observability_visible,
        rollout_visible,
    ].count(True)
    beats = [
        "Separate layers before explaining movement.",
        "The request path should prove which layer owns work.",
        "Cross-cutting policies span layers without becoming a layer.",
        "Failure and observability routes stay outside the happy path.",
        "Rollout appears after the layered contract is visible.",
    ]
    beat_index = max(0, min(len(beats) - 1, int(p * len(beats))))
    return img


def render_data_lineage_frame(
    second: float,
    args: argparse.Namespace,
    fonts: dict[str, ImageFont.ImageFont],
) -> Image.Image:
    img = Image.new("RGB", (args.width, args.height), PALETTE["paper"])
    draw = ImageDraw.Draw(img)
    p = clamp(second / max(args.duration, 0.001))
    lineage_labels, quality_labels = data_lineage_labels(args)
    active_lineage_count = min(6, int(math.floor(ease((p - 0.06) / 0.58) * 6 + 0.999)))
    transform_visible = p > 0.24
    quality_gate_visible = p > 0.38
    drift_visible = p > 0.54
    consumer_visible = p > 0.70
    rollback_visible = p > 0.84

    rounded_rect(draw, (44, 112, 1236, 592), "#ffffff", "#cfcfcf", width=2, radius=16)
    text(draw, (150, 140), "SOURCE", fonts["tiny"], PALETTE["muted"], "mm")
    text(draw, (604, 140), "LINEAGE PATH", fonts["tiny"], PALETTE["muted"], "mm")
    text(draw, (456, 322), "QUALITY GATE", fonts["tiny"], PALETTE["muted"], "mm")
    text(draw, (918, 322), "OPERATIONS", fonts["tiny"], PALETTE["muted"], "mm")

    node_boxes = []
    node_colors = [
        (PALETTE["route"], gray_level(1), gray_level(3)),
        (PALETTE["route"], gray_level(2), gray_level(3)),
        (PALETTE["defense"], gray_level(2), gray_level(4)),
        (PALETTE["defense"], gray_level(3), gray_level(4)),
        (PALETTE["atlas"], gray_level(3), gray_level(5)),
        (PALETTE["atlas"], gray_level(4), gray_level(5)),
    ]
    for idx, label_value in enumerate(lineage_labels):
        x = 82 + idx * 178
        active = idx < active_lineage_count
        stroke, fill, ghost_stroke = node_colors[idx]
        rounded_rect(draw, (x, 192, x + 138, 270), fill, stroke if active else ghost_stroke, width=4 if active else 2, radius=18)
        text(draw, (x + 69, 237), compact_label(label_value, 18), fonts["small"], PALETTE["ink"], "mm", 3, "#ffffff")
        node_boxes.append((x, 192, x + 138, 270, stroke))

    for idx in range(len(node_boxes) - 1):
        x1, y1, x2, y2, _ = node_boxes[idx]
        nx1, ny1, nx2, ny2, _ = node_boxes[idx + 1]
        active_edge = idx < max(0, active_lineage_count - 1)
        y = (y1 + y2) // 2
        draw_polyline(draw, [(x2, y), (nx1, y)], PALETTE["route"] if active_edge else PALETTE["line"], 6 if active_edge else 3, 1)
    if active_lineage_count:
        packet_idx = min(active_lineage_count - 1, len(node_boxes) - 1)
        x1, y1, x2, y2, _ = node_boxes[packet_idx]
        draw.ellipse((x1 + 56, y1 - 16, x1 + 82, y1 + 10), fill=hex_to_rgb(PALETTE["gold"]), outline=hex_to_rgb("#ffffff"), width=3)

    if not transform_visible:
        rounded_rect(draw, (414, 150, 668, 178), "#e7e7e7", "#cfcfcf", width=2, radius=14)
        text(draw, (541, 167), "transform rule", fonts["tiny"], PALETTE["muted"], "mm")
    if transform_visible:
        rounded_rect(draw, (414, 150, 668, 178), "#e7e7e7", PALETTE["attribute"], width=3, radius=14)
        text(draw, (541, 167), "transform rule", fonts["tiny"], PALETTE["attribute"], "mm")
        draw_polyline(draw, [(496, 178), (496, 192)], PALETTE["attribute"], 4, 1)
        draw_polyline(draw, [(592, 178), (592, 192)], PALETTE["attribute"], 4, 1)

    if not quality_gate_visible:
        rounded_rect(draw, (248, 342, 662, 456), gray_level(1), "#cfcfcf", width=2, radius=18)
        text(draw, (455, 384), "quality checks pending", fonts["small"], PALETTE["muted"], "mm")
    if quality_gate_visible:
        draw_meter(draw, (248, 342, 455, 456), compact_label(quality_labels[0], 18), ease((p - 0.38) / 0.18), PALETTE["route"], fonts)
        draw_meter(draw, (455, 342, 662, 456), compact_label(quality_labels[1], 18), ease((p - 0.42) / 0.18), PALETTE["defense"], fonts)

    if not drift_visible:
        rounded_rect(draw, (724, 342, 1136, 394), "#ffccd5", "#cfcfcf", width=2, radius=18)
        text(draw, (930, 371), "drift monitor", fonts["small"], PALETTE["muted"], "mm")
    if drift_visible:
        rounded_rect(draw, (724, 342, 1136, 394), "#ffccd5", PALETTE["damage"], width=4, radius=18)
        text(draw, (884, 371), compact_label(quality_labels[2], 22), fonts["small"], PALETTE["damage"], "mm", 3, "#ffffff")
        draw_polyline(draw, [(994, 374), (1048, 354), (1110, 378)], PALETTE["damage"], 5, ease((p - 0.54) / 0.18))

    if not consumer_visible:
        rounded_rect(draw, (724, 424, 1136, 500), "#e7e7e7", "#cfcfcf", width=2, radius=18)
        text(draw, (930, 466), "consumer contract", fonts["small"], PALETTE["muted"], "mm")
    if consumer_visible:
        rounded_rect(draw, (724, 424, 1136, 500), "#e7e7e7", PALETTE["atlas"], width=4, radius=18)
        text(draw, (930, 454), compact_label(lineage_labels[-1], 28), fonts["small"], PALETTE["atlas"], "mm", 3, "#ffffff")
        text(draw, (930, 482), "ready after lineage + checks", fonts["tiny"], PALETTE["muted"], "mm")
        draw_polyline(draw, [(1042, 270), (1042, 424)], PALETTE["atlas"], 5, 1)

    if not rollback_visible:
        rounded_rect(draw, (248, 500, 662, 568), "#ffccd5", "#cfcfcf", width=2, radius=18)
        text(draw, (455, 539), "rollback route", fonts["small"], PALETTE["muted"], "mm")
    if rollback_visible:
        rounded_rect(draw, (248, 500, 662, 568), "#ffccd5", PALETTE["tradeoff"], width=4, radius=18)
        text(draw, (455, 539), compact_label(quality_labels[3], 26), fonts["small"], PALETTE["tradeoff"], "mm", 3, "#ffffff")
        draw_polyline(draw, [(620, 500), (620, 480), (260, 480), (260, 270)], PALETTE["tradeoff"], 5, ease((p - 0.84) / 0.12))

    visible_mechanism_count = [
        active_lineage_count >= 2,
        transform_visible,
        quality_gate_visible,
        drift_visible,
        consumer_visible,
        rollback_visible,
    ].count(True)
    beats = [
        "Start with source-to-consumer lineage, not a generic pipeline.",
        "Transform rules appear before quality is trusted.",
        "Quality gates separate schema and freshness checks.",
        "Drift and consumers stay visible outside the transform path.",
        "Rollback appears only after downstream risk is visible.",
    ]
    beat_index = max(0, min(len(beats) - 1, int(p * len(beats))))
    return img


def render_frame(
    second: float,
    args: argparse.Namespace,
    fonts: dict[str, ImageFont.ImageFont],
) -> Image.Image:
    pattern = selected_pattern(args)
    if bool(getattr(args, "masonry_layout", False)) and pattern == "swimlane-handoff" and ai_alternatives_requested(args):
        frame = render_ai_alternatives_masonry_frame(second, args, fonts)
    elif bool(getattr(args, "masonry_layout", False)) and pattern == "swimlane-handoff" and plugin_requested(args):
        frame = render_plugin_masonry_frame(second, args, fonts)
    elif bool(getattr(args, "masonry_layout", False)) and pattern == "risk-bowtie" and guardrail_requested(args):
        frame = render_guardrail_masonry_frame(second, args, fonts)
    elif bool(getattr(args, "masonry_layout", False)) and pattern in MASONRY_GENERIC_RENDER_PATTERNS:
        frame = render_generic_masonry_frame(second, args, fonts, pattern)
    elif pattern == "systems-flow":
        frame = render_systems_flow_frame(second, args, fonts)
    elif pattern == "state-machine":
        frame = render_state_machine_frame(second, args, fonts)
    elif pattern == "comparison-matrix":
        frame = render_comparison_matrix_frame(second, args, fonts)
    elif pattern == "causal-loop":
        frame = render_causal_loop_frame(second, args, fonts)
    elif pattern == "phase-timeline":
        frame = render_phase_timeline_frame(second, args, fonts)
    elif pattern == "metric-dashboard":
        frame = render_metric_dashboard_frame(second, args, fonts)
    elif pattern == "dependency-map":
        frame = render_dependency_map_frame(second, args, fonts)
    elif pattern == "sequence-trace":
        frame = render_sequence_trace_frame(second, args, fonts)
    elif pattern == "sankey-flow":
        frame = render_sankey_flow_frame(second, args, fonts)
    elif pattern == "swimlane-handoff":
        frame = render_swimlane_handoff_frame(second, args, fonts)
    elif pattern == "risk-bowtie":
        frame = render_risk_bowtie_frame(second, args, fonts)
    elif pattern == "scenario-tree":
        frame = render_scenario_tree_frame(second, args, fonts)
    elif pattern == "skill-tree-route":
        frame = render_skill_tree_route_frame(second, args, fonts)
    elif pattern == "evidence-ladder":
        frame = render_evidence_ladder_frame(second, args, fonts)
    elif pattern == "layered-architecture":
        frame = render_layered_architecture_frame(second, args, fonts)
    elif pattern == "data-lineage":
        frame = render_data_lineage_frame(second, args, fonts)
    else:
        frame = render_skill_tree_frame(second, args, fonts)
    return apply_metro_camera(frame, second, args)


def build_paths(project_root: Path, output_id: str) -> dict[str, Path]:
    return {
        "source_package": project_root / "source" / "source-package.json",
        "production_notes": project_root / "source" / "production-notes.md",
        "html": project_root / "src" / "index.html",
        "render_js": project_root / "src" / "render.mjs",
        "video": project_root / "artifacts" / "video-renders" / "draft" / "videos" / f"{output_id}.mp4",
        "review": project_root / "artifacts" / "reviews" / "self-review.md",
        "contact_sheet": project_root / "artifacts" / "video-renders" / "draft" / "review" / f"{output_id}-contact-sheet.jpg",
        "contact_sheet_manifest": project_root / "artifacts" / "video-renders" / "draft" / "review" / f"{output_id}-contact-sheet.json",
    }


def distribute_anchor_groups(values: list[str], group_count: int) -> list[list[str]]:
    groups: list[list[str]] = [[] for _ in range(max(1, group_count))]
    cleaned = [str(value).strip() for value in values if str(value).strip()]
    for index, value in enumerate(cleaned):
        groups[index % len(groups)].append(value)
    return groups


def agent_loop_anchor_groups(values: list[str]) -> list[list[str]]:
    groups: list[list[str]] = [[] for _ in range(5)]
    fallback_index = 0
    for value in [str(item).strip() for item in values if str(item).strip()]:
        text_value = value.lower()
        if "context_window" in text_value or "context" in text_value or "pane" in text_value:
            groups[1].append(value)
        elif "environment" in text_value or "repo" in text_value or "browser" in text_value or "database" in text_value:
            groups[2].append(value)
        elif "fixed workflow" in text_value or "adaptive agent" in text_value or "flow-token" in text_value or "swimlane" in text_value:
            groups[3].append(value)
        elif "approval" in text_value or "model + tools + state + loop" in text_value or "badge" in text_value or "guardrail" in text_value or "mcp" in text_value:
            groups[4].append(value)
        elif "agent_loop" in text_value or "agent loop" in text_value or "loop" in text_value:
            groups[0].append(value)
        else:
            groups[fallback_index % len(groups)].append(value)
            fallback_index += 1
    return groups


def guardrail_anchor_groups(values: list[str]) -> list[list[str]]:
    groups: list[list[str]] = [[] for _ in range(5)]
    fallback_index = 0
    for value in [str(item).strip() for item in values if str(item).strip()]:
        text_value = value.lower()
        if "shield_gate" in text_value or "agent_loop" in text_value or "agent loop" in text_value or "control layer" in text_value:
            groups[0].append(value)
        elif "input" in text_value or "output" in text_value or "action" in text_value or "tool call" in text_value:
            groups[1].append(value)
        elif "prompt bubble" in text_value or "hard gate" in text_value or "model armor" in text_value or "risk_score" in text_value or "risk score" in text_value or "block" in text_value or "redact" in text_value or "route" in text_value or "escalate" in text_value:
            groups[2].append(value)
        elif "approval" in text_value or "deploy" in text_value or ".env" in text_value or "rm" in text_value or "secret" in text_value or "destructive" in text_value or "write_prod" in text_value:
            groups[3].append(value)
        elif "policy matrix" in text_value or "green-yellow-red" in text_value or "safety" in text_value or "friction" in text_value or "positive case" in text_value or "blocked case" in text_value or "policy checks" in text_value:
            groups[4].append(value)
        else:
            groups[fallback_index % len(groups)].append(value)
            fallback_index += 1
    return groups


def harness_anchor_groups(values: list[str]) -> list[list[str]]:
    groups: list[list[str]] = [[] for _ in range(5)]
    fallback_index = 0
    for value in [str(item).strip() for item in values if str(item).strip()]:
        text_value = value.lower()
        if "comparison_grid" in text_value or "comparison grid" in text_value or "comparison matrix" in text_value or "selection path" in text_value:
            groups[0].append(value)
        elif "runtime stack" in text_value or "runtime wrapper" in text_value or "instruction" in text_value or "permission" in text_value or "logging" in text_value or "memory" in text_value or "approval" in text_value:
            groups[1].append(value)
        elif "engine" in text_value or "dashboard" in text_value or "same model" in text_value or "different shell" in text_value or "model badge" in text_value:
            groups[2].append(value)
        elif "github" in text_value or "copilot" in text_value or "claude" in text_value or "opencode" in text_value or "three-column" in text_value or "provider" in text_value or "agent_loop" in text_value or "agent loop" in text_value:
            groups[3].append(value)
        elif "credit_meter" in text_value or "credit meter" in text_value or "cost" in text_value or "spend" in text_value or "tool count" in text_value or "feature grid" in text_value or "use-case matrix" in text_value or "budget" in text_value:
            groups[4].append(value)
        else:
            groups[fallback_index % len(groups)].append(value)
            fallback_index += 1
    return groups


def plugin_anchor_groups(values: list[str]) -> list[list[str]]:
    groups: list[list[str]] = [[] for _ in range(5)]
    fallback_index = 0
    for value in [str(item).strip() for item in values if str(item).strip()]:
        text_value = value.lower()
        if "plugin_bundle_cube" in text_value or "bundle" in text_value or "installable" in text_value or "package" in text_value:
            groups[0].append(value)
        elif "skill" in text_value or "hook" in text_value or "mcp" in text_value or "agent" in text_value or "tool" in text_value or "contains" in text_value:
            groups[1].append(value)
        elif "github" in text_value or "claude" in text_value or "opencode" in text_value or "manifest" in text_value or "npm" in text_value or "runtime" in text_value:
            groups[2].append(value)
        elif "marketplace" in text_value or "allowlist" in text_value or "govern" in text_value or "version" in text_value or "upgrade" in text_value or "team" in text_value:
            groups[3].append(value)
        elif "noisy" in text_value or "cost" in text_value or "context" in text_value or "expensive" in text_value or "policy" in text_value or "behavior" in text_value:
            groups[4].append(value)
        else:
            groups[fallback_index % len(groups)].append(value)
            fallback_index += 1
    return groups


def ai_alternatives_anchor_groups(values: list[str]) -> list[list[str]]:
    groups: list[list[str]] = [[] for _ in range(5)]
    fallback_index = 0
    for value in [str(item).strip() for item in values if str(item).strip()]:
        text_value = value.lower()
        if "comparison_grid" in text_value or "four-column" in text_value or "four alternatives" in text_value:
            groups[0].append(value)
        elif "rovo" in text_value or "gemini" in text_value or "copilot" in text_value or "claude" in text_value or "workspace" in text_value or "home base" in text_value:
            groups[1].append(value)
        elif "radar" in text_value or "knowledge" in text_value or "coding" in text_value or "extensibility" in text_value or "budget" in text_value or "quadrant" in text_value:
            groups[2].append(value)
        elif "credit_meter" in text_value or "cost" in text_value or "pricing" in text_value or "subscription" in text_value or "credits" in text_value:
            groups[3].append(value)
        elif "choose by workflow gravity" in text_value or "selector" in text_value or "guardrail" in text_value or "permissions" in text_value or "observability" in text_value:
            groups[4].append(value)
        else:
            groups[fallback_index % len(groups)].append(value)
            fallback_index += 1
    return groups


def skill_package_anchor_groups(values: list[str]) -> list[list[str]]:
    groups: list[list[str]] = [[] for _ in range(5)]
    fallback_index = 0
    for value in [str(item).strip() for item in values if str(item).strip()]:
        text_value = value.lower()
        if "skill_card_stack" in text_value or "skill card" in text_value or "skill.md" in text_value or "deploy-preview" in text_value:
            groups[0].append(value)
        elif "long prompt" in text_value or "prompt wall" in text_value or "giant" in text_value or "mini novel" in text_value or "bloated" in text_value or "trim" in text_value:
            groups[1].append(value)
        elif "github" in text_value or "claude" in text_value or "opencode" in text_value or "folder" in text_value or "scripts" in text_value or "references" in text_value or "assets" in text_value:
            groups[2].append(value)
        elif "progressive disclosure" in text_value or "cost" in text_value or "token" in text_value or "only when" in text_value or "activates" in text_value or "relevant" in text_value:
            groups[3].append(value)
        elif "tool" in text_value or "script" in text_value or "checklist" in text_value or "debug" in text_value or "architecture" in text_value or "onboarding" in text_value or "workflow" in text_value:
            groups[4].append(value)
        else:
            groups[fallback_index % len(groups)].append(value)
            fallback_index += 1
    return groups


def visual_zones(
    pattern: str,
    *,
    masonry: bool = False,
    anchors: list[str] | None = None,
    motif: str | None = None,
) -> list[dict[str, object]]:
    default_roles = [
        ("orientation", "opening anchor plane"),
        ("primary-system", "main mechanism plane"),
        ("secondary-system", "support mechanism plane"),
        ("control-risk", "control and risk plane"),
        ("evidence-feedback", "evidence and feedback plane"),
    ]
    role_map = {
        "systems-flow": [
            ("intake", "input contract zone"),
            ("pipeline", "queue and transform zone"),
            ("control", "retry and failure-control zone"),
            ("feedback", "throughput feedback zone"),
            ("transaction", "active transaction path zone"),
        ],
        "comparison-matrix": [
            ("options", "option column zone"),
            ("criteria", "criteria row zone"),
            ("scores", "score evidence zone"),
            ("tradeoff", "tradeoff and guardrail zone"),
            ("decision", "recommendation zone"),
        ],
        "sankey-flow": [
            ("input", "input volume zone"),
            ("split", "split and loss zone"),
            ("transform", "parallel transform zone"),
            ("merge", "merge bottleneck zone"),
            ("output", "output contract zone"),
        ],
    }
    roles = role_map.get(pattern, default_roles)
    if pattern == "systems-flow" and motif == "agent-loop":
        roles = [
            ("agent-loop", "observe-act-check-continue loop zone"),
            ("context", "stacked context window zone"),
            ("environment", "mutable environment surface zone"),
            ("workflow-contrast", "fixed workflow versus adaptive agent zone"),
            ("approval-badge", "approval checkpoint and model-tools-state-loop badge zone"),
        ]
    if pattern == "systems-flow" and motif == "harness-runtime":
        roles = [
            ("comparison-grid", "harness comparison grid and selected cell zone"),
            ("runtime-stack", "instruction tools permissions loop logging stack zone"),
            ("engine-dashboard", "same model engine-to-dashboard control morph zone"),
            ("harness-shells", "same model inside Copilot Claude Code and OpenCode shells zone"),
            ("cost-selection", "credit meter feature-fit matrix and selected path zone"),
        ]
    if pattern == "systems-flow" and motif == "hook-lifecycle":
        roles = [
            ("hook-events", "event timeline and moving lifecycle pulse zone"),
            ("policy-gate", "shield gate and dangerous command interception zone"),
            ("provider-events", "GitHub Claude Code and OpenCode hook event surfaces zone"),
            ("preprocess-jobs", "format validate secret audit notify and context-filter jobs zone"),
            ("cost-boundary", "token savings latency cost and lifecycle-control boundary zone"),
        ]
    if pattern == "systems-flow" and motif == "skill-package":
        roles = [
            ("skill-card-stack", "reusable SKILL.md card stack and activation zone"),
            ("prompt-collapse", "long prompt wall collapsing into scoped skill card zone"),
            ("compatible-folders", "GitHub Claude and OpenCode folder structures zone"),
            ("progressive-cost", "progressive disclosure token cost meter zone"),
            ("repeatable-tools", "example skills tool badges script blocks trim and workflow stamp zone"),
        ]
    if pattern == "swimlane-handoff" and motif == "plugin-bundle":
        roles = [
            ("plugin-bundle", "installable bundle cube assembly zone"),
            ("plugin-modules", "detachable skills hooks MCP agents tools module zone"),
            ("plugin-provider-surfaces", "GitHub manifest Claude marketplace and OpenCode npm runtime zone"),
            ("plugin-governance", "allowlist version upgrade and team install governance zone"),
            ("plugin-cost-risk", "good plugin versus noisy plugin cost risk zone"),
        ]
    if pattern == "swimlane-handoff" and motif == "ai-alternatives":
        roles = [
            ("alternatives-grid", "four alternative comparison grid zone"),
            ("workspace-homes", "Rovo Gemini Copilot Claude home-base workspace zone"),
            ("fit-radar", "knowledge productivity coding research radar and quadrant zone"),
            ("pricing-meters", "subscription credit API and local cost meter zone"),
            ("workflow-selector", "workflow-gravity selector guardrail permission observability zone"),
        ]
    if pattern == "risk-bowtie" and motif == "guardrail-gate":
        roles = [
            ("shield-agent", "shield gate over agent loop zone"),
            ("inspection-gates", "input output action inspection gate zone"),
            ("policy-outcomes", "risk score and block redact route escalate zone"),
            ("approval-actions", "human approval and protected action zone"),
            ("policy-matrix", "policy matrix and safety friction balance zone"),
        ]
    zones: list[dict[str, object]] = []
    bounds_source = MASONRY_ZONE_BOUNDS if masonry else METRO_ZONE_BOUNDS
    if pattern == "systems-flow" and motif == "agent-loop":
        anchor_groups = agent_loop_anchor_groups(anchors or [])
    elif pattern == "systems-flow" and motif == "harness-runtime":
        anchor_groups = harness_anchor_groups(anchors or [])
    elif pattern == "systems-flow" and motif == "skill-package":
        anchor_groups = skill_package_anchor_groups(anchors or [])
    elif pattern == "systems-flow" and motif == "hook-lifecycle":
        anchor_groups = hook_anchor_groups(anchors or [])
    elif pattern == "swimlane-handoff" and motif == "plugin-bundle":
        anchor_groups = plugin_anchor_groups(anchors or [])
    elif pattern == "swimlane-handoff" and motif == "ai-alternatives":
        anchor_groups = ai_alternatives_anchor_groups(anchors or [])
    elif pattern == "risk-bowtie" and motif == "guardrail-gate":
        anchor_groups = guardrail_anchor_groups(anchors or [])
    else:
        anchor_groups = distribute_anchor_groups(anchors or [], len(roles))
    for index, (name, role) in enumerate(roles):
        zones.append(
            {
                "id": f"{pattern}-{name}-zone",
                "role": role,
                "bounds": bounds_source[index],
                "grayLevel": [1, 2, 3, 4, 2][index],
                "sourceAnchors": anchor_groups[index],
                "boxModel": {
                    "cornerRadius": 0,
                    "internalPaddingPx": 0,
                    "gridPx": int(METRO_GRID),
                },
            }
        )
    return zones


def visual_mechanism_anchor_map(mechanisms: list[str], anchors: list[str]) -> list[dict[str, object]]:
    anchor_groups = distribute_anchor_groups(anchors, len(mechanisms))
    return [
        {
            "id": f"mechanism-{index + 1:02d}",
            "mechanism": mechanism,
            "sourceAnchors": anchor_groups[index],
        }
        for index, mechanism in enumerate(mechanisms)
    ]


def binding_state_keys(pattern: str) -> list[str]:
    return {
        "systems-flow": ["queueSlots", "retryVisible", "deadLetterVisible", "feedbackVisible", "workerActive"],
        "skill-tree": ["routeCount", "keystoneVisible", "atlasVisible"],
        "skill-tree-route": ["activeRouteNodeCount", "damageClusterVisible", "defenseClusterVisible", "attributeBridgeVisible", "keystoneTradeoffVisible", "respecVisible", "lateClusterVisible"],
        "state-machine": ["activeState", "rollbackVisible", "compensationVisible", "terminalVisible"],
        "comparison-matrix": ["criteriaRevealed", "scoreShiftVisible", "tradeoffVisible", "recommendationVisible", "guardrailVisible"],
        "causal-loop": ["loopVisible", "delayVisible", "amplifierVisible", "dampingVisible", "sideEffectVisible", "interventionVisible"],
        "phase-timeline": ["activePhase", "riskVisible", "gateVisible", "handoffVisible", "finalVisible"],
        "metric-dashboard": ["activeMetric", "trendVisible", "thresholdVisible", "anomalyVisible", "forecastVisible", "decisionVisible"],
        "dependency-map": ["edgeCount", "riskVisible", "bottleneckVisible", "cutoverVisible", "fallbackVisible"],
        "sequence-trace": ["activeSpanCount", "criticalPathVisible", "latencyBudgetVisible", "retryVisible", "fallbackVisible", "responseVisible"],
        "sankey-flow": ["activeFlowCount", "splitVisible", "lossVisible", "bottleneckVisible", "mergeVisible", "outputVisible"],
        "swimlane-handoff": ["activeHandoffCount", "slaVisible", "reworkVisible", "approvalVisible", "escalationVisible", "completeVisible"],
        "risk-bowtie": ["activeThreatCount", "preventiveVisible", "topEventVisible", "mitigativeVisible", "consequenceVisible", "degradedVisible", "actionVisible"],
        "scenario-tree": ["activeScenarioCount", "probabilityVisible", "riskVisible", "upsideVisible", "decisionVisible", "fallbackVisible", "outcomeVisible"],
        "evidence-ladder": ["activeEvidenceCount", "claimVisible", "counterEvidenceVisible", "gapVisible", "confidenceVisible", "recommendationVisible"],
        "layered-architecture": ["activeLayerCount", "crossCuttingVisible", "failurePathVisible", "observabilityVisible", "rolloutVisible"],
        "data-lineage": ["activeLineageCount", "transformVisible", "qualityGateVisible", "driftVisible", "consumerVisible", "rollbackVisible"],
    }.get(pattern, ["visibleMechanismCount"])


def semantic_bindings(
    pattern: str,
    anchors: list[str],
    zones: list[dict[str, object]],
    mechanism_anchors: list[dict[str, object]],
    state_keys_override: list[str] | None = None,
) -> list[dict[str, object]]:
    state_keys = state_keys_override or binding_state_keys(pattern)
    zone_count = max(1, len(zones))
    mechanism_count = max(1, len(mechanism_anchors))
    bindings: list[dict[str, object]] = []

    def matching_item(items: list[dict[str, object]], anchor: str, fallback_index: int) -> dict[str, object]:
        for item in items:
            source_anchors = item.get("sourceAnchors") if isinstance(item, dict) else None
            if isinstance(source_anchors, list) and anchor in {str(value).strip() for value in source_anchors}:
                return item
        return items[fallback_index % max(1, len(items))]

    for index, anchor in enumerate(str(value).strip() for value in anchors if str(value).strip()):
        zone = matching_item(zones, anchor, index)
        mechanism = matching_item(mechanism_anchors, anchor, index)
        mechanism_id = str(mechanism.get("id") or f"mechanism-{(index % mechanism_count) + 1:02d}")
        bindings.append(
            {
                "id": f"binding-{index + 1:02d}",
                "sourceAnchor": anchor,
                "zoneId": zone.get("id"),
                "zoneRole": zone.get("role"),
                "mechanismId": mechanism_id,
                "mechanism": mechanism.get("mechanism"),
                "stateKey": state_keys[index % len(state_keys)],
                "visualRole": "data-bearing-zone",
            }
        )
    return bindings


def source_anchor_coverage(
    anchors: list[str],
    zones: list[dict[str, object]],
    mechanism_anchors: list[dict[str, object]],
) -> dict[str, object]:
    expected = [str(anchor).strip() for anchor in anchors if str(anchor).strip()]
    expected_set = set(expected)

    def collect(items: list[dict[str, object]]) -> set[str]:
        covered: set[str] = set()
        for item in items:
            raw_values = item.get("sourceAnchors") if isinstance(item, dict) else None
            if isinstance(raw_values, list):
                covered.update(str(value).strip() for value in raw_values if str(value).strip())
        return covered

    zone_covered = collect(zones)
    mechanism_covered = collect(mechanism_anchors)
    all_covered = zone_covered | mechanism_covered
    return {
        "expectedCount": len(expected_set),
        "zoneCoveredCount": len(expected_set & zone_covered),
        "mechanismCoveredCount": len(expected_set & mechanism_covered),
        "coveredCount": len(expected_set & all_covered),
        "uncoveredAnchors": sorted(expected_set - all_covered),
        "zoneUncoveredAnchors": sorted(expected_set - zone_covered),
        "mechanismUncoveredAnchors": sorted(expected_set - mechanism_covered),
    }


def masonry_modules() -> list[dict[str, object]]:
    modules: list[dict[str, object]] = []
    for index, module in enumerate(MASONRY_MODULE_BOUNDS):
        modules.append(
            {
                "id": f"masonry-module-{index + 1:02d}",
                "bounds": {key: module[key] for key in ("x", "y", "width", "height")},
                "zoneIndex": module["zoneIndex"],
                "grayLevel": module["grayLevel"],
            }
        )
    return modules


def source_package(args: argparse.Namespace, paths: dict[str, Path]) -> dict[str, object]:
    pattern = selected_pattern(args)
    if pattern == "skill-tree-route":
        default_anchors = [
            "class start",
            "travel-node cost",
            "damage cluster",
            "defense cluster",
            "attribute bridge",
            "keystone tradeoff",
            "respec checkpoint",
            "late specialization",
        ]
        mechanisms = [
            "the main route grows from origin through travel nodes before branch clusters are judged",
            "damage and defense clusters reveal as separate side branches instead of one generic upgrade path",
            "attribute bridge, keystone tradeoff, and respec checkpoint reveal as distinct cost controls",
            "late specialization stays visually separated from the core route so progression layers do not collapse together",
        ]
    elif pattern == "systems-flow":
        default_anchors = [
            "intake sources",
            "event bus",
            "bounded queue",
            "worker pool",
            "retry branch",
            "dead-letter path",
            "throughput metric",
            "feedback limit",
        ]
        mechanisms = [
            "event packets route from sources through a bus into a bounded queue",
            "queue slots fill while worker nodes pulse to show transformation capacity",
            "retry and dead-letter branches split failed work into explicit control paths",
            "throughput and feedback-control layers move separately from the main packet path",
        ]
        if hook_requested(args):
            default_anchors = [
                "event_timeline lights up lifecycle event nodes",
                "shield_gate overlays the event timeline",
                "GitHub hook badges for session prompt tool call and stop events",
                "Claude event cloud around the loop",
                "OpenCode vertical plugin event list",
                "PreToolUse Bash command block for rm -rf kubectl delete terraform destroy",
                "log filter and preprocessing path shrinks context before the model",
                "format validation secret protection audit logging notifications jobs cascade",
                "token-savings counter and speed-vs-cost slider",
                "hooks = lifecycle controls final stamp",
                "flow-tokens attention-matrix-tiles swimlane-handoff risk-bowtie circuit-signal-traces",
            ]
            mechanisms = [
                "event timeline lights lifecycle nodes while one pulse moves through session prompt tool-call permission compaction notification and stop boundaries",
                "shield gate overlays the timeline and converts passive lifecycle events into active executable policy",
                "GitHub Claude Code and OpenCode surfaces show comparable hook/event lanes without becoming feature cards",
                "one PreToolUse command path blocks destructive Bash actions while another filter path shrinks noisy logs before model context",
                "token savings and latency cost meters move in opposite directions before a lifecycle-control boundary closes the lesson",
            ]
        elif harness_requested(args):
            default_anchors = [
                "comparison_grid",
                "runtime stack",
                "engine icon morphs into vehicle dashboard",
                "same model badge in three different harness shells",
                "three-column harness cards",
                "credit_meter",
                "feature grid fades behind use-case matrix",
                "highlighted selection path",
                "agent_loop_ring",
                "instruction tools permissions loop logging layers",
            ]
            mechanisms = [
                "comparison grid zooms into one runtime stack cell before the shell mechanics appear",
                "runtime layers assemble around the model while the engine core becomes dashboard controls",
                "the same model badge drops into three distinct harness shells with different defaults",
                "tool count, context, retries, and loop depth drive a rising credit meter",
                "feature grid mutes behind a use-case matrix and a selected path closes the comparison",
            ]
        elif skill_package_requested(args):
            default_anchors = [
                "skill_card_stack fans open only when relevant",
                "long prompt wall shrinks into one scoped SKILL.md card",
                "GitHub Claude and OpenCode SKILL.md folder structures align",
                "progressive disclosure cost meter stays flat until activation",
                "deploy debug architecture onboarding and codebase map skill cards cycle",
                "tool badges and script blocks snap onto the active skill card",
                "bloated mini novel skill is trimmed into a sharp task-scoped workflow",
                "Skill = on-demand reusable workflow final stamp",
                "flow-tokens layered-architecture swimlane-handoff masonry-wall token-boxes-to-context-window circuit-signal-traces",
            ]
            mechanisms = [
                "skill_card_stack fans open from reusable SKILL.md cards only when the task needs them",
                "a long prompt wall collapses into one scoped skill card to show reusable task packaging",
                "GitHub Claude and OpenCode-compatible folder structures align around SKILL.md scripts references and assets",
                "progressive disclosure keeps the cost meter flat until activation then loads only the needed procedure",
                "example skill cards, tool badges, script blocks, trimming, and final workflow stamp show repeatable safe execution",
            ]
        elif agent_loop_requested(args):
            default_anchors = [
                "agent_loop_ring",
                "context_window_box",
                "Model + Tools + State + Loop",
                "environment changes",
                "fixed workflow lane",
                "adaptive agent lane",
                "approval checkpoint",
                "tool action loop",
            ]
            mechanisms = [
                "agent loop ring cycles observe, act, check, and continue as the reusable visual identity",
                "stacked context panes feed model state before actions leave the loop",
                "environment surfaces mutate across repo, browser, ticket, docs, and database blocks",
                "a fixed workflow lane stays linear while an adaptive agent lane replans through a fork",
                "approval checkpoint and Model + Tools + State + Loop modules close the system",
            ]
    elif pattern == "state-machine":
        default_anchors = [
            "lifecycle states",
            "guarded transition",
            "schema guard",
            "policy guard",
            "execution state",
            "rollback path",
            "compensation path",
            "terminal state",
        ]
        mechanisms = [
            "state cards activate in order along a deterministic lifecycle path",
            "guard panels become visible before state transitions commit",
            "rollback and compensation route away from the main success path",
            "terminal-state panel separates done work from parked or failed work",
        ]
    elif pattern == "comparison-matrix":
        default_anchors = [
            "option set",
            "shared criteria",
            "score bars",
            "score shift",
            "tradeoff lens",
            "recommended option",
            "risk guardrail",
            "decision rationale",
        ]
        mechanisms = [
            "options reveal first so every later score has a stable column",
            "criteria rows fill with per-option score bars to show comparable evidence",
            "score-shift markers and tradeoff lens explain why the ranking changes",
            "recommendation and guardrail panels appear only after criteria are visible",
        ]
    elif pattern == "causal-loop":
        default_anchors = [
            "cause chain",
            "reinforcing loop",
            "delayed effect",
            "balancing loop",
            "side effect",
            "pressure metric",
            "leverage point",
            "intervention",
        ]
        mechanisms = [
            "cause nodes reveal before loop motion so directionality is clear",
            "reinforcing and balancing paths use separate routes and colors",
            "delay, side-effect, and pressure meters appear as distinct explanatory mechanisms",
            "intervention appears only after the loop and side effect are visible",
        ]
    elif pattern == "phase-timeline":
        default_anchors = [
            "source-locked intake",
            "ordered phase cards",
            "risk scan lane",
            "decision gate",
            "handoff path",
            "release milestone",
            "moving phase token",
            "separate quality gate",
        ]
        mechanisms = [
            "phase cards reveal from left to right while a token marks current progress",
            "risk lane appears below the timeline before the decision gate opens",
            "handoff route carries constraints from review into validation",
            "release milestone appears only after the gate and handoff mechanisms are visible",
        ]
    elif pattern == "metric-dashboard":
        default_anchors = [
            "primary metric",
            "trend line",
            "healthy band",
            "warning threshold",
            "action threshold",
            "anomaly marker",
            "forecast cone",
            "decision window",
        ]
        mechanisms = [
            "trend line reveals before any interpretation panel appears",
            "healthy, warning, and action thresholds convert the chart into an operating rule",
            "anomaly marker names the risk metric instead of relying on color alone",
            "forecast cone and decision panel appear late so action follows evidence",
        ]
    elif pattern == "dependency-map":
        default_anchors = [
            "dependency graph",
            "cluster boundary",
            "shared prerequisite",
            "risk edge",
            "bottleneck",
            "cutover gate",
            "fallback path",
            "release readiness",
        ]
        mechanisms = [
            "source dependencies converge into an integration layer before release is allowed",
            "risk edge and bottleneck callouts appear as separate mechanisms instead of generic warnings",
            "cutover gate waits for upstream proof before the release path is highlighted",
            "fallback path appears late as an explicit safety route rather than a text-only caveat",
        ]
    elif pattern == "sequence-trace":
        default_anchors = [
            "trace waterfall",
            "service lane",
            "span duration",
            "handoff marker",
            "critical path",
            "latency budget",
            "retry branch",
            "fallback response",
        ]
        mechanisms = [
            "service lanes stay fixed while span bars reveal the request path over time",
            "handoff markers connect parent and child spans instead of relying on isolated bars",
            "critical path, latency budget, retry, fallback, and response appear as separate mechanisms",
            "the response lands only after the trace has exposed where the latency was spent",
        ]
    elif pattern == "sankey-flow":
        default_anchors = [
            "input stream",
            "split branch",
            "loss branch",
            "transform lanes",
            "merge point",
            "bottleneck",
            "retained value meter",
            "final output",
        ]
        mechanisms = [
            "one input stream splits into retained value and explicit loss branches",
            "parallel transform lanes carry separate portions of the value flow",
            "merge and bottleneck states appear before final output readiness",
            "input, retained value, and output readiness meters progress separately",
        ]
    elif pattern == "swimlane-handoff":
        if ai_alternatives_requested(args):
            default_anchors = [
                "comparison_grid with one strong icon per platform",
                "Atlassian Rovo anchored to Jira Confluence organizational knowledge workspace",
                "Gemini App anchored to Google personal productivity workspace",
                "GitHub Copilot anchored to IDE GitHub coding harness workspace",
                "Claude Desktop Code anchored to desktop terminal research coding workspace",
                "shared radar chart for knowledge personal productivity coding extensibility budgetability",
                "one axis turns into four use-case quadrants",
                "credit_meter relabeled for Rovo credits Gemini subscription Copilot AI credits Claude subscription API",
                "Choose by workflow gravity final use-case selector",
                "guardrails permissions observability wrap the selected workflow home",
                "swimlane-handoff inline-bar-table circuit-signal-traces masonry-wall flow-tokens dependency-map",
            ]
            mechanisms = [
                "four-column comparison grid activates as a single modular surface instead of four separate cards",
                "Rovo Gemini Copilot and Claude home-base zones connect to their natural workspace blocks through circuit traces",
                "knowledge productivity coding research and budgetability axes form a shared radar/quadrant fit map",
                "four cost meters rise with distinct pricing models before the selected path is allowed to move",
                "workflow-gravity selector routes to one home base and then passes through guardrail permission observability blocks",
            ]
        elif plugin_requested(args):
            default_anchors = [
                "plugin_bundle_cube assembles from smaller installable blocks",
                "detachable runtime modules reveal skills hooks MCP config agent-profile and tools",
                "GitHub plugin manifest card with agents skills hooks and MCP configuration",
                "Claude marketplace lane with allowlist governance gate",
                "OpenCode npm package drops into runtime event surface",
                "team-wide install fanout standardizes approved behavior",
                "versioning and upgrade arrows govern the same plugin pack",
                "good plugin versus noisy plugin split exposes cost and context risk",
                "Plugin = packaged harness behavior final package-install stamp",
                "flow-tokens circuit-signal-traces masonry-wall risk-bowtie dependency-map",
            ]
            mechanisms = [
                "plugin bundle cube assembles from flush rectangular capability blocks before opening into detachable modules",
                "provider packaging surfaces show GitHub manifest Claude marketplace allowlist and OpenCode npm runtime as comparable hard-edge lanes",
                "allowlist gate version arrows and team install fanout convert distribution into governance rather than a copied-file setup",
                "good plugin and noisy plugin split show efficient defaults versus context/tool cost spread before the final packaged-behavior install stamp",
            ]
        else:
            default_anchors = [
                "owner lanes",
                "request intake",
                "handoff path",
                "SLA pressure",
                "approval gate",
                "rework loop",
                "escalation path",
                "completion lane",
            ]
            mechanisms = [
                "named owner lanes stay fixed while the work item moves across responsibility boundaries",
                "handoff steps activate in order so ownership transfer is visible rather than implied",
                "SLA, approval, rework, and escalation states appear as separate routes and gates",
                "completion appears only after release ownership and exceptional paths are visible",
            ]
    elif pattern == "risk-bowtie":
        if guardrail_requested(args):
            default_anchors = [
                "shield_gate around the agent_loop_ring",
                "Input / Output / Action inspection gates",
                "prompt bubble versus hard policy gate",
                "Model Armor filter lanes",
                "risk_score bar",
                "block redact route escalate outcomes",
                "human approval modal over deploy action",
                ".env rm deploy protected action tiles",
                "safety versus friction balance",
                "policy matrix",
                "positive case path",
                "blocked case path",
            ]
            mechanisms = [
                "a hard shield gate closes over the agent loop before policy decisions appear",
                "input, output, and action gates inspect separate streams instead of collapsing into one warning",
                "risk score, Model Armor lanes, and block-redact-route-escalate outcomes convert policy into state changes",
                "human approval pauses protected deploy, secret, and destructive-command actions before continuation",
                "policy matrix and safety-friction balance remain visible so strictness and false-positive cost are separate",
            ]
        else:
            default_anchors = [
                "threat set",
                "preventive barriers",
                "top event",
                "mitigative barriers",
                "consequence set",
                "degraded barrier",
                "residual risk meter",
                "repair action",
            ]
            mechanisms = [
                "threats converge through preventive barriers before the top event can occur",
                "the top event separates prevention from mitigation so control timing is visible",
                "mitigative barriers reduce consequences after the event instead of pretending prevention already worked",
                "degraded barrier and repair action appear late so the control gap is auditable",
            ]
    elif pattern == "scenario-tree":
        default_anchors = [
            "decision point",
            "scenario branches",
            "probability labels",
            "evidence weight",
            "upside branch",
            "risk branch",
            "fallback route",
            "selected outcome",
        ]
        mechanisms = [
            "one decision point branches into base, upside, and downside scenarios",
            "probability labels and evidence-weight meter appear before the decision gate",
            "risk, upside, fallback, and final selected outcome appear as distinct routes",
            "the selected outcome appears only after scenario branches and fallback are visible",
        ]
    elif pattern == "evidence-ladder":
        default_anchors = [
            "working claim",
            "evidence tiers",
            "source support",
            "counterevidence",
            "source gap",
            "confidence meter",
            "uncertainty meter",
            "recommendation",
        ]
        mechanisms = [
            "the working claim appears before evidence is scored so the viewer knows what is being tested",
            "evidence tiers climb in order instead of appearing as a flat source list",
            "counterevidence and source gaps remain visible as separate checks against overconfidence",
            "confidence and recommendation appear only after support, counterweight, and gap states are visible",
        ]
    elif pattern == "layered-architecture":
        default_anchors = [
            "layer stack",
            "request path",
            "ownership boundary",
            "cross-cutting policy",
            "failure route",
            "observability",
            "rollout gate",
            "platform layer",
        ]
        mechanisms = [
            "layers activate in order so ownership boundaries are visible before cross-cutting concerns appear",
            "the request path descends through the stack instead of treating architecture as a static diagram",
            "cross-cutting policy, failure route, and observability stay separate from the happy path",
            "rollout gate appears only after all layers and operational routes are visible",
        ]
    elif pattern == "data-lineage":
        default_anchors = [
            "raw source",
            "lineage path",
            "transform rule",
            "quality gate",
            "freshness check",
            "drift monitor",
            "consumer contract",
            "rollback route",
        ]
        mechanisms = [
            "lineage nodes activate from source to consumer so provenance is visible before trust claims",
            "transform rules appear before the quality gate so derived data is not treated as raw input",
            "schema and freshness checks stay separate from drift and consumer readiness",
            "rollback appears only after downstream drift or consumer risk is visible",
        ]
    else:
        default_anchors = [
            "start location",
            "travel path",
            "attribute highway",
            "small passive cluster",
            "notable node",
            "keystone tradeoff",
            "defensive checkpoint",
            "optional specialization layer",
        ]
        mechanisms = [
            "route growth from start location through the character tree",
            "damage, defense, and attribute meters filling as checkpoints",
            "keystone tradeoff diamond switching into focus",
            "Atlas layer drawn as a separated late-game specialization tree",
        ]
    anchors = args.anchor or default_anchors
    facts = args.fact or [
        "No prompt facts were passed with --fact; treat this as a draft source package with missing source-fact detail.",
    ]
    motif = None
    if pattern == "systems-flow" and skill_package_requested(args):
        motif = "skill-package"
    elif pattern == "systems-flow" and hook_requested(args):
        motif = "hook-lifecycle"
    elif pattern == "systems-flow" and harness_requested(args):
        motif = "harness-runtime"
    elif pattern == "systems-flow" and agent_loop_requested(args):
        motif = "agent-loop"
    elif pattern == "swimlane-handoff" and ai_alternatives_requested(args):
        motif = "ai-alternatives"
    elif pattern == "swimlane-handoff" and plugin_requested(args):
        motif = "plugin-bundle"
    elif pattern == "risk-bowtie" and guardrail_requested(args):
        motif = "guardrail-gate"
    zones = visual_zones(pattern, masonry=args.masonry_layout, anchors=anchors, motif=motif)
    mechanism_anchors = visual_mechanism_anchor_map(mechanisms, anchors)
    if motif == "hook-lifecycle":
        grouped_anchors = hook_anchor_groups(anchors)
        for index, mechanism_anchor in enumerate(mechanism_anchors):
            mechanism_anchor["sourceAnchors"] = grouped_anchors[index % len(grouped_anchors)]
    elif motif == "harness-runtime":
        grouped_anchors = harness_anchor_groups(anchors)
        for index, mechanism_anchor in enumerate(mechanism_anchors):
            mechanism_anchor["sourceAnchors"] = grouped_anchors[index % len(grouped_anchors)]
    elif motif == "skill-package":
        grouped_anchors = skill_package_anchor_groups(anchors)
        for index, mechanism_anchor in enumerate(mechanism_anchors):
            mechanism_anchor["sourceAnchors"] = grouped_anchors[index % len(grouped_anchors)]
    elif motif == "plugin-bundle":
        grouped_anchors = plugin_anchor_groups(anchors)
        for index, mechanism_anchor in enumerate(mechanism_anchors):
            mechanism_anchor["sourceAnchors"] = grouped_anchors[index % len(grouped_anchors)]
    elif motif == "ai-alternatives":
        grouped_anchors = ai_alternatives_anchor_groups(anchors)
        for index, mechanism_anchor in enumerate(mechanism_anchors):
            mechanism_anchor["sourceAnchors"] = grouped_anchors[index % len(grouped_anchors)]
    elif motif == "agent-loop":
        grouped_anchors = agent_loop_anchor_groups(anchors)
        for index, mechanism_anchor in enumerate(mechanism_anchors):
            mechanism_anchor["sourceAnchors"] = grouped_anchors[index % len(grouped_anchors)]
    elif motif == "guardrail-gate":
        grouped_anchors = guardrail_anchor_groups(anchors)
        for index, mechanism_anchor in enumerate(mechanism_anchors):
            mechanism_anchor["sourceAnchors"] = grouped_anchors[index % len(grouped_anchors)]
    binding_state_keys_override = None
    if motif == "hook-lifecycle":
        binding_state_keys_override = [
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
            "activeHookEventCount",
            "providerLaneCount",
            "policyTokenCount",
            "tokenSavingsLevel",
            "latencyCostLevel",
        ]
    elif motif == "harness-runtime":
        binding_state_keys_override = [
            "comparisonGridVisible",
            "runtimeStackVisible",
            "engineCoreVisible",
            "dashboardControlsVisible",
            "layersAssembling",
            "modelBadgeShared",
            "sameModelShellCount",
            "threeHarnessShellsVisible",
            "toolCountLevel",
            "creditMeterLevel",
            "featureGridMuted",
            "useCaseMatrixActive",
            "selectionPathHighlighted",
            "agentLoopRingVisible",
        ]
    elif motif == "skill-package":
        binding_state_keys_override = [
            "skillCardStackVisible",
            "promptWallCollapsed",
            "folderStructuresAligned",
            "progressiveDisclosureVisible",
            "skillActivationVisible",
            "exampleSkillCardsVisible",
            "toolBadgesAttached",
            "scriptBlockVisible",
            "bloatedSkillTrimmed",
            "finalWorkflowStampVisible",
            "costMeterLevel",
            "resourceModuleCount",
            "validationStageLevel",
            "readSurfaceLevel",
        ]
    elif motif == "plugin-bundle":
        binding_state_keys_override = [
            "pluginBundleCubeVisible",
            "bundleOpenedVisible",
            "bundleModuleCount",
            "githubManifestCardVisible",
            "claudeMarketplaceGateVisible",
            "opencodeNpmRuntimeDropVisible",
            "teamInstallFanoutVisible",
            "installFanoutCount",
            "versionUpgradeVisible",
            "governanceGateVisible",
            "goodBadPluginSplitVisible",
            "noisyPluginRiskVisible",
            "costMeterLevel",
            "packagedBehaviorStampVisible",
        ]
    elif motif == "ai-alternatives":
        binding_state_keys_override = [
            "comparisonGridVisible",
            "platformHomeBaseCount",
            "rovoWorkspaceVisible",
            "geminiWorkspaceVisible",
            "copilotWorkspaceVisible",
            "claudeWorkspaceVisible",
            "radarAxisCount",
            "quadrantMapVisible",
            "costMeterCount",
            "costMeterLevel",
            "workflowSelectorVisible",
            "selectedWorkflowPathVisible",
            "guardrailWrapVisible",
            "observabilityWrapVisible",
        ]
    elif motif == "agent-loop":
        binding_state_keys_override = [
            "agentLoopRingVisible",
            "contextPaneCount",
            "environmentState",
            "toolActionLoopVisible",
            "fixedWorkflowLaneVisible",
            "adaptiveAgentLaneVisible",
            "approvalCheckpointVisible",
            "modelToolsStateLoopBadgeVisible",
        ]
    if motif == "guardrail-gate":
        binding_state_keys_override = [
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
            "secretRiskActive",
            "destructiveCommandRiskActive",
            "deployRiskActive",
            "safetyFrictionBalanceVisible",
        ]
    bindings = semantic_bindings(pattern, anchors, zones, mechanism_anchors, binding_state_keys_override)
    return {
        "title": args.title,
        "topic": args.topic,
        "checkedDate": args.checked_date,
        "audience": args.audience,
        "route": "topic-explainer",
        "visualPattern": pattern,
        "visualZones": zones,
        "masonryLayout": {
            "required": bool(args.masonry_layout),
            "moduleCount": len(MASONRY_MODULE_BOUNDS) if args.masonry_layout else 0,
            "transitionType": "masonry-construction" if args.masonry_layout else None,
        },
        "masonryModules": masonry_modules() if args.masonry_layout else [],
        "durationSeconds": args.duration,
        "format": {"width": args.width, "height": args.height, "fps": args.fps},
        "outputId": args.output_id,
        "outputVideo": str(paths["video"].as_posix()),
        "sourceFacts": facts,
        "sourceUrls": args.source_url,
        "treeLabels": skill_tree_labels(args)[0] if pattern == "skill-tree" else [],
        "meterLabels": skill_tree_labels(args)[1] if pattern == "skill-tree" else [],
        "routeLabels": skill_tree_route_labels(args)[0] if pattern == "skill-tree-route" else [],
        "checkpointLabels": skill_tree_route_labels(args)[1] if pattern == "skill-tree-route" else [],
        "phaseLabels": phase_timeline_labels(args) if pattern == "phase-timeline" else [],
        "metricLabels": metric_dashboard_labels(args)[0] if pattern == "metric-dashboard" else [],
        "thresholdLabels": metric_dashboard_labels(args)[1] if pattern == "metric-dashboard" else [],
        "dependencyLabels": dependency_map_labels(args)[0] if pattern == "dependency-map" else [],
        "clusterLabels": dependency_map_labels(args)[1] if pattern == "dependency-map" else [],
        "traceLabels": sequence_trace_labels(args) if pattern == "sequence-trace" else [],
        "flowLabels": sankey_flow_labels(args) if pattern == "sankey-flow" else [],
        "laneLabels": swimlane_handoff_labels(args)[0] if pattern == "swimlane-handoff" else [],
        "handoffLabels": swimlane_handoff_labels(args)[1] if pattern == "swimlane-handoff" else [],
        "threatLabels": risk_bowtie_labels(args)[0] if pattern == "risk-bowtie" else [],
        "barrierLabels": risk_bowtie_labels(args)[1] if pattern == "risk-bowtie" else [],
        "consequenceLabels": risk_bowtie_labels(args)[2] if pattern == "risk-bowtie" else [],
        "scenarioLabels": scenario_tree_labels(args)[0] if pattern == "scenario-tree" else [],
        "probabilityLabels": scenario_tree_labels(args)[1] if pattern == "scenario-tree" else [],
        "claimLabels": evidence_ladder_labels(args)[0] if pattern == "evidence-ladder" else [],
        "evidenceLabels": evidence_ladder_labels(args)[1] if pattern == "evidence-ladder" else [],
        "layerLabels": layered_architecture_labels(args)[0] if pattern == "layered-architecture" else [],
        "concernLabels": layered_architecture_labels(args)[1] if pattern == "layered-architecture" else [],
        "lineageLabels": data_lineage_labels(args)[0] if pattern == "data-lineage" else [],
        "qualityLabels": data_lineage_labels(args)[1] if pattern == "data-lineage" else [],
        "systemLabels": systems_flow_labels(args) if pattern == "systems-flow" else [],
        "strategyAnchors": anchors,
        "semanticBindings": bindings,
        "visualMechanismAnchors": mechanism_anchors,
        "sourceAnchorCoverage": source_anchor_coverage(anchors, zones, mechanism_anchors),
        "causalLabels": causal_labels(args) if pattern == "causal-loop" else [],
        "decisionOptions": comparison_labels(args)[0] if pattern == "comparison-matrix" else [],
        "decisionCriteria": comparison_labels(args)[1] if pattern == "comparison-matrix" else [],
        "stateLabels": state_machine_labels(args)[0] if pattern == "state-machine" else [],
        "guardLabels": state_machine_labels(args)[1] if pattern == "state-machine" else [],
        "missingFacts": [] if args.fact else ["Exact prompt facts were not supplied to the helper command."],
        "visualMechanisms": mechanisms,
        "visualPolicy": {
            "edgeStyle": args.edge_style,
            "boxInteriorPolicy": BOX_PADDING_POLICY,
            "internalPaddingPx": 0,
            "contentFlushToBounds": True,
            "grayLevels": [
                {"level": idx, "hex": value, "role": role}
                for idx, (value, role) in enumerate(
                    zip(
                        GRAY_LEVELS,
                        [
                            "foreground panel",
                            "paper field",
                            "secondary level",
                            "inactive structure",
                            "tertiary level",
                            "muted labels",
                        ],
                    )
                )
            ],
        },
    }


def write_json(path: Path, data: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def write_notes(args: argparse.Namespace, paths: dict[str, Path], package: dict[str, object]) -> None:
    paths["production_notes"].parent.mkdir(parents=True, exist_ok=True)
    facts = "\n".join(f"- {fact}" for fact in package["sourceFacts"])
    anchors = "\n".join(f"- {anchor}" for anchor in package["strategyAnchors"])
    if package["visualPattern"] == "skill-tree-route":
        claim = f"a good {args.topic} explainer should show route order, travel-node cost, branch clusters, attribute bridges, keystone tradeoffs, respec checkpoints, and late specialization as separate mechanisms."
        mechanic = "a planned path grows from the class start, branches into damage and defense clusters, crosses an attribute bridge, then exposes keystone cost, respec review, and late specialization only after the core path is visible."
        candidates = "skill-tree route map, radial constellation, and checklist ledger."
        rejected = "a checklist ledger would list priorities but hide the spatial pathing and travel-node cost that make tree decisions meaningful."
        chosen = "skill-tree-route map with main route growth, side clusters, bridge cost, keystone tradeoff, respec checkpoint, and separated late plan."
        vocabulary = "brand red means primary route; status red means risk or tradeoff; dark red means checkpoints; dark gray means stable structure; mid gray means secondary layers."
        narration = "exact node names, patch-specific balance, and best-build claims are omitted unless supplied as source facts; the scaffold focuses on route reasoning."
    elif package["visualPattern"] == "systems-flow":
        if hook_requested(args):
            claim = f"a good {args.topic} explainer should show hooks as lifecycle interception points where runtime events become enforceable policy, preprocessing, and cost tradeoffs."
            mechanic = "a lifecycle event pulse moves through timeline nodes, a shield gate overlays execution, provider event surfaces expose comparable hook systems, one Bash path is blocked while another log path is filtered, and savings versus latency meters settle into a lifecycle-control boundary."
            candidates = "hook lifecycle megacanvas, generic systems-flow pipeline, and provider feature comparison table."
            rejected = "a generic systems-flow pipeline would show work movement but hide the hook-specific timing: session, prompt, tool, permission, compaction, notification, stop, blocking, filtering, and cost/latency boundaries."
            chosen = "hook lifecycle megacanvas with event_timeline, shield_gate overlay, GitHub hook badges, Claude event cloud, OpenCode event list, PreToolUse command block, log-filter path, hook-job cascade, token-savings counter, speed-vs-cost slider, and lifecycle-controls stamp."
            vocabulary = "brand red marks active event and safe preprocessing flow; status red marks blocked dangerous command and latency risk; dark red marks executable policy and filter gates; gray levels separate timeline, policy, provider surfaces, preprocessing jobs, and cost boundary. Colorset2 is not used because colorset1 gray hierarchy plus red state marks separates all Hook roles."
            narration = "vendor event names, code details, and exact hook job labels stay in narration or source facts; the frame carries lifecycle interception and cost mechanics without explanatory text."
        elif harness_requested(args):
            claim = f"a good {args.topic} explainer should show the harness as the runtime shell that changes controls, defaults, cost, and behavior around the same model."
            mechanic = "a comparison grid selects one runtime cell, layers assemble around the model, the engine core becomes dashboard controls, the same model enters three different harness shells, and cost rises as defaults add tools, context, retries, and loop depth."
            candidates = "harness runtime megacanvas, generic systems-flow pipeline, and feature comparison table."
            rejected = "a generic systems-flow pipeline would show work movement but hide the model-versus-harness distinction, the same-model-different-shell mechanic, and cost/control defaults."
            chosen = "harness runtime megacanvas with comparison_grid, runtime stack, engine-to-dashboard morph, same model badge in Copilot/Claude Code/OpenCode shells, credit_meter, muted feature grid, active use-case matrix, and highlighted selection path."
            vocabulary = "brand red marks selected runtime paths and shared model identity; dark red marks control/default emphasis; status red marks rising cost pressure; gray levels separate comparison surface, runtime layers, shell boundaries, controls, inactive defaults, and active selection. Colorset2 is not used because colorset1 gray hierarchy plus red state marks separates the required roles."
            narration = "vendor names, exact plan features, and detailed selection criteria stay in narration or source facts; the frame carries runtime structure and selection mechanics without explanatory text."
        elif skill_package_requested(args):
            claim = f"a good {args.topic} explainer should show a skill as on-demand reusable workflow packaging, not as a static prompt or generic pipeline."
            mechanic = "skill cards fan open only when invoked, a long prompt wall collapses into one scoped SKILL.md package, compatible folder structures align, a progressive disclosure cost meter stays flat until activation, examples and tool/script modules attach, and an oversized mini-novel skill is trimmed into a reusable workflow stamp."
            candidates = "skill-package megacanvas, generic systems-flow pipeline, and feature card gallery."
            rejected = "a generic systems-flow pipeline would show queue movement but hide the skill-specific mechanic: reusable instructions, scripts, references, and assets stay available without loading every session."
            chosen = "skill-package megacanvas with skill_card_stack, long prompt wall collapse, SKILL.md-compatible folder structures, progressive disclosure cost meter, deploy/debug/architecture/onboarding/codebase-map example cards, tool badges, script blocks, read-surface levels, bloated skill trimming, and on-demand reusable workflow stamp."
            vocabulary = "brand red marks the selected reusable workflow and activation route; status red marks trimmed bloat or cost risk; dark red marks hard gates; gray levels separate cards, folder surfaces, resource modules, validation blocks, read surfaces, and evidence floor. Colorset2 is not used because colorset1 gray hierarchy plus red state marks separates all Skill roles."
            narration = "vendor names, exact markdown syntax, and the final definition stay in narration or source facts; the frame carries reusable packaging, progressive disclosure, activation, and trimming mechanics without explanatory text."
        else:
            claim = f"a good {args.topic} explainer should show how work moves, where pressure accumulates, where failures branch, and how feedback protects the system."
            mechanic = "a job packet moves through intake, bus, queue, workers, storage, retry, dead-letter, metrics, and feedback-control layers."
            candidates = "pipeline map, state machine, and incident timeline."
            rejected = "a plain timeline would show order but hide pressure, branching, and capacity constraints."
            chosen = "systems-flow map with explicit queue pressure, worker capacity, failure branches, and feedback throttle."
            vocabulary = "brand red means accepted work; status red means retry or failed work; dark red means feedback control; dark gray means active transformation; stacked gray slots mean bounded capacity."
            narration = "implementation details, exact vendor names, and operational thresholds are omitted unless supplied as source facts."
    elif package["visualPattern"] == "state-machine":
        claim = f"a good {args.topic} explainer should show states, transition guards, rollback, compensation, and terminal outcomes as separate mechanisms."
        mechanic = "one work item advances through state cards while guard panels validate transitions and an explicit recovery lane handles rollback and compensation."
        candidates = "state-machine diagram, sequence diagram, and checklist timeline."
        rejected = "a checklist timeline would show progress but hide invalid transitions, recovery routes, and terminal-state separation."
        chosen = "state-machine map with guarded transitions, success path, recovery lane, and terminal-state panel."
        vocabulary = "brand red means lifecycle progress; dark red means transition guards; dark gray means successful execution; status red means rollback or compensation; mid gray means terminal states."
        narration = "implementation-specific state names and exact retry limits are omitted unless supplied as source facts."
    elif package["visualPattern"] == "comparison-matrix":
        claim = f"a good {args.topic} explainer should compare options against shared criteria, expose tradeoffs, and delay recommendation until evidence is visible."
        mechanic = "option columns stay fixed while criteria rows fill, score-shift markers explain changing preference, and recommendation plus guardrail panels appear after the comparison is legible."
        candidates = "decision matrix, ranking podium, and pros/cons ledger."
        rejected = "a ranking podium would show a winner but hide which criteria changed the decision."
        chosen = "comparison matrix with shared criteria rows, per-option score bars, tradeoff lens, recommendation, and guardrail."
        vocabulary = "brand red means the selected option or score movement; dark gray means quality balance; status red means cost or risk; dark red means guardrail; black marks the decision cursor."
        narration = "exact scores and weighting can be explained in narration or source notes unless the prompt supplies them."
    elif package["visualPattern"] == "causal-loop":
        claim = f"a good {args.topic} explainer should show cause direction, delay, amplification, balancing constraint, side effect, and leverage point as separate mechanisms."
        mechanic = "a signal travels through cause nodes, exposes a delayed effect, branches into balancing and side-effect paths, and then an intervention targets the leverage point."
        candidates = "causal-loop map, timeline, and root-cause fishbone."
        rejected = "a timeline would show order but hide reinforcing feedback, balancing constraint, and side-effect pressure."
        chosen = "causal-loop map with reinforcing path, delayed effect, balancing route, side-effect branch, pressure meters, and final intervention."
        vocabulary = "brand red means primary causal flow; status red means pressure, delay, or side effect; dark gray means balancing constraint; dark red means intervention; black marks the moving causal signal."
        narration = "exact causal strength, time constants, and intervention costs are omitted unless supplied as source facts."
    elif package["visualPattern"] == "phase-timeline":
        claim = f"a good {args.topic} explainer should show the ordered phases, risk surfacing, decision gate, handoff, and release milestone as separate visual mechanisms."
        mechanic = "a phase token moves across ordered cards while risk, gate, handoff, and release layers appear at different moments."
        candidates = "phase timeline, state machine, and systems-flow map."
        rejected = "a state machine would show valid transitions but underplay calendar order, milestones, and handoff timing."
        chosen = "phase timeline with source-locked phases, risk lane, decision gate, handoff route, and final release milestone."
        vocabulary = "brand red means phase progress; status red means surfaced risk; dark red means decision gate; dark gray means handoff constraints; mid gray means release; black marks the current phase."
        narration = "exact dates and owners are omitted unless supplied as source facts; the scaffold focuses on sequence and gate mechanics."
    elif package["visualPattern"] == "metric-dashboard":
        claim = f"a good {args.topic} explainer should show the metric owner, threshold rule, anomaly, forecast, and decision window as separate visual mechanisms."
        mechanic = "a primary trend line reveals first, threshold bands convert the trend into an operating rule, an anomaly highlights risk, and a forecast cone opens the decision window."
        candidates = "metric dashboard, comparison matrix, and phase timeline."
        rejected = "a comparison matrix would rank choices but hide when a metric crosses an operational threshold."
        chosen = "metric dashboard with trend, threshold bands, anomaly marker, forecast cone, and late decision panel."
        vocabulary = "brand red means primary metric trend; dark gray means healthy range; dark red means warning; status red means action risk; mid gray means forecast; black means quality context."
        narration = "exact metric values, statistical confidence, and alert thresholds should come from source facts when available; otherwise the scaffold stays schematic."
    elif package["visualPattern"] == "dependency-map":
        claim = f"a good {args.topic} explainer should show dependency direction, shared prerequisites, bottlenecks, cutover gates, and fallback routes as separate visual mechanisms."
        mechanic = "source nodes converge into an integration layer, risk and bottleneck callouts appear on the dependency path, and release waits for cutover proof before fallback is armed."
        candidates = "dependency map, phase timeline, and risk matrix."
        rejected = "a phase timeline would show order but hide shared prerequisites, cross-cluster dependencies, and fallback routing."
        chosen = "dependency map with cluster boundaries, converging edges, risk edge, bottleneck, cutover gate, fallback path, and readiness meter."
        vocabulary = "brand red means dependency proof; dark red means cross-system prerequisites; status red means risk or bottleneck; mid gray means integration; black means fallback; dark gray means release readiness."
        narration = "exact owners, lead times, and dependency weights should come from source facts when available; otherwise the scaffold stays schematic."
    elif package["visualPattern"] == "sequence-trace":
        claim = f"a good {args.topic} explainer should show request order, span duration, critical path, latency budget, retry, fallback, and final response as separate visual mechanisms."
        mechanic = "fixed service lanes hold a trace waterfall while child-span handoffs, critical path, retry, fallback, and response panels appear only after the relevant span is visible."
        candidates = "sequence trace, systems-flow map, and metric dashboard."
        rejected = "a systems-flow map would show components but hide exact request order, parent-child spans, and latency ownership."
        chosen = "sequence trace with service lanes, span bars, handoff markers, critical-path callout, latency-budget panel, retry branch, fallback cache, and returned response."
        vocabulary = "brand red means request progress; dark red means authorization; mid gray means inventory; status red means latency risk; black means fallback; dark gray means returned response."
        narration = "exact span durations, trace IDs, percentiles, and error rates should come from source facts when available; otherwise the scaffold stays schematic."
    elif package["visualPattern"] == "sankey-flow":
        claim = f"a good {args.topic} explainer should show how value splits, where loss exits, where streams transform, where they merge, and what bottleneck limits final output."
        mechanic = "one input band splits into retained and loss branches, parallel transforms recombine through a bottleneck, and final output appears after loss and merge states are visible."
        candidates = "sankey flow, funnel chart, and systems-flow map."
        rejected = "a funnel chart would show dropoff but hide parallel transformations, recombination, and bottleneck ownership."
        chosen = "sankey-flow map with split branch, loss branch, parallel transform lanes, merge point, bottleneck, and final output readiness."
        vocabulary = "brand red means input value; dark gray means retained value; status red means explicit loss or bottleneck; dark red means transform; mid gray means output; black marks moving flow packets."
        narration = "exact proportions and measured losses should come from source facts when available; otherwise the scaffold stays schematic."
    elif package["visualPattern"] == "swimlane-handoff":
        if ai_alternatives_requested(args):
            claim = f"a good {args.topic} explainer should show each assistant as a different workflow home, not as a feature-list card or generic brand comparison."
            mechanic = "a four-column comparison grid activates first, each platform anchors to its natural workspace, a shared fit radar turns into quadrants, pricing meters rise underneath, and a workflow-gravity selector routes through guardrail, permission, and observability blocks."
            candidates = "workflow-gravity megacanvas, generic feature table, and product-logo carousel."
            rejected = "a generic feature table would preserve platform names but hide the central choice mechanic: match the assistant to where context, approvals, and work already live."
            chosen = "AI alternatives megacanvas with comparison_grid, Rovo/Gemini/Copilot/Claude workspace anchors, shared radar/quadrant fit map, four cost meters, selected workflow path, and guardrail/permission/observability wrapper."
            vocabulary = "brand red marks the selected workflow path and primary flow; status red marks cost or governance pressure; dark red marks approval and permission boundaries; gray levels separate platform homes, fit axes, pricing models, selector state, and governance wrap. Colorset2 is not used because colorset1 gray hierarchy plus red state marks separates the required roles."
            narration = "plan names, vendor details, and exact pricing caveats stay in narration or source facts; the frame carries workflow gravity, fit, cost, and governance mechanics without explanatory text."
        elif plugin_requested(args):
            claim = f"a good {args.topic} explainer should show a plugin as an installable, versioned, governed bundle of reusable harness behavior, not as an extension icon or generic handoff chart."
            mechanic = "a plugin_bundle_cube assembles from smaller blocks, opens into detachable skills/hooks/MCP/agent/tool modules, passes through provider packaging surfaces, fans out to teams through governance/version gates, then contrasts efficient defaults with noisy context/tool spread before the package-install stamp."
            candidates = "plugin-bundle megacanvas, generic swimlane handoff, and provider feature table."
            rejected = "a generic swimlane would show ownership transfer but hide the actual plugin idea: packaging runtime capabilities into one installable unit that can be shared, versioned, and governed."
            chosen = "plugin-bundle megacanvas with detachable modules, GitHub manifest surface, Claude marketplace allowlist gate, OpenCode npm/runtime drop, team install fanout, versioning arrows, good/noisy plugin split, and packaged harness behavior stamp."
            vocabulary = "brand red marks the installable bundle and approved package-install flow; status red marks allowlist gates and noisy-plugin risk; dark red marks governance controls; gray levels separate bundle, module, provider, governance, and cost/risk hierarchy. Colorset2 is not used because colorset1 gray hierarchy plus red state marks separates the required roles."
            narration = "provider names and exact package syntax stay in narration or source facts; the frame carries distribution, governance, versioning, install, and cost mechanics without explanatory text."
        else:
            claim = f"a good {args.topic} explainer should show who owns each step, when work crosses lanes, where SLA pressure builds, and how rework or escalation changes the route."
            mechanic = "fixed owner lanes hold a moving work item while handoff steps activate in sequence, then SLA, approval, rework, escalation, and completion states appear as separate mechanisms."
            candidates = "swimlane handoff, state machine, and phase timeline."
            rejected = "a state machine would show state transitions but hide ownership boundaries; a timeline would show order but hide rework and escalation routes."
            chosen = "swimlane-handoff map with owner lanes, sequential handoff steps, SLA pressure, approval gate, rework loop, escalation path, and completion lane."
            vocabulary = "brand red means intake ownership; dark gray means analysis or delivery work; dark red means review ownership; status red means SLA, approval, rework, or escalation risk; mid gray means completion."
            narration = "exact owners, service-level targets, queue ages, and escalation policies should come from source facts when available; otherwise the scaffold stays schematic."
    elif package["visualPattern"] == "risk-bowtie":
        if guardrail_requested(args):
            claim = f"a good {args.topic} explainer should show enforceable policy acting around an agent loop through input, output, and action gates."
            mechanic = "prompt, output, and tool-call packets hit separate gates; a shield closes around the agent loop, risk score and policy matrix activate outcomes, and human approval pauses protected actions."
            candidates = "guardrail gate megacanvas, generic risk bowtie, and state-machine lifecycle."
            rejected = "a generic risk bowtie would show threats and consequences but hide the specific guardrail mechanic: inspect, block, redact, route, escalate, approve, or continue."
            chosen = "guardrail gate megacanvas with shield_gate around agent_loop_ring, three inspection gates, risk score, Model Armor-style lanes, policy outcome tiles, human approval modal, protected action tiles, and safety-friction balance."
            vocabulary = "brand red means allowed or primary policy flow; status red means blocked or high-risk paths; dark red means hard policy enforcement; grays separate background, zones, modules, connectors, inactive marks, and active marks. Colorset2 is not used; the requested green-yellow-red policy matrix is encoded with colorset1 gray, dark red, and status red because hue is not needed for state separation."
            narration = "vendor details, exact threshold names, and final policy copy stay in narration or source facts; the frame carries the policy mechanics without explanatory text."
        else:
            claim = f"a good {args.topic} explainer should show threats, preventive barriers, the top event, mitigative barriers, consequences, degraded controls, and repair action as separate mechanisms."
            mechanic = "threats converge through preventive barriers into a top event, then mitigative barriers reduce consequences while degraded controls and repair action expose the control gap."
            candidates = "risk bowtie, causal loop, and dependency map."
            rejected = "a causal loop would show influence but blur whether a control prevents the event or mitigates consequences after the event."
            chosen = "risk-bowtie map with threat set, preventive barriers, top event, mitigative barriers, consequences, degraded barrier, residual risk, and repair action."
            vocabulary = "status red means threats, consequences, and degraded control gaps; brand red means preventive control; dark gray means mitigative control; dark red means repair action."
            narration = "exact likelihood, severity, control owners, and assurance evidence should come from source facts when available; otherwise the scaffold stays schematic."
    elif package["visualPattern"] == "scenario-tree":
        claim = f"a good {args.topic} explainer should show how a decision branches into plausible scenarios, where probability or evidence belongs, and when fallback changes the selected outcome."
        mechanic = "one decision point branches into base, upside, and downside routes; probabilities and evidence appear before the decision gate, then fallback and outcome are revealed late."
        candidates = "scenario tree, comparison matrix, and phase timeline."
        rejected = "a comparison matrix would rank options but hide downstream branches, fallback route, and conditional outcomes."
        chosen = "scenario-tree map with decision root, scenario branches, probability labels, evidence weight, upside/risk branches, fallback route, and selected outcome."
        vocabulary = "brand red means main scenario evidence; dark gray means upside; status red means downside risk; dark red means fallback; mid gray means selected outcome."
        narration = "exact probabilities, payoff values, and confidence intervals should come from source facts when available; otherwise the scaffold stays schematic."
    elif package["visualPattern"] == "evidence-ladder":
        claim = f"a good {args.topic} explainer should show what claim is being tested, which evidence supports it, what counterevidence exists, where source gaps remain, and why the confidence level justifies the recommendation."
        mechanic = "a working claim connects into ascending evidence tiers, then counterevidence and source gaps lower or qualify confidence before a recommendation appears."
        candidates = "evidence ladder, scorecard matrix, and source timeline."
        rejected = "a scorecard matrix would compare sources but hide the order from claim to support, counterweight, uncertainty, and recommendation."
        chosen = "evidence-ladder map with claim card, tiered evidence, counterevidence, source-gap callout, confidence and uncertainty meters, and delayed recommendation."
        vocabulary = "brand red means supporting evidence; status red means counterevidence or uncertainty; dark red means source gap; dark gray means confidence-backed recommendation."
        narration = "exact source citations, confidence values, and methodology caveats should come from source facts when available; otherwise the scaffold stays schematic."
    elif package["visualPattern"] == "layered-architecture":
        claim = f"a good {args.topic} explainer should show layer ownership, request movement, cross-cutting policy, failure routing, observability, and rollout separately."
        mechanic = "a request descends through owned layers while cross-cutting policy, failure, observability, and rollout mechanisms appear outside the happy path."
        candidates = "layered architecture stack, systems flow, and dependency map."
        rejected = "a systems-flow map would show work movement but blur stable layer boundaries and cross-cutting concerns."
        chosen = "layered-architecture stack with request path, layer activation, policy band, failure route, observability panel, and rollout gate."
        vocabulary = "brand red means request path; dark gray means active layers; dark red means cross-cutting policy; status red means failure route; mid gray means observability and rollout readiness."
        narration = "exact owners, protocols, SLOs, and deployment policy should come from source facts when available; otherwise the scaffold stays schematic."
    elif package["visualPattern"] == "data-lineage":
        claim = f"a good {args.topic} explainer should show source provenance, transform ownership, quality gates, drift monitoring, consumer readiness, and rollback separately."
        mechanic = "data moves from source through lineage nodes while transform rules, quality checks, drift monitoring, consumer contract, and rollback route appear as distinct mechanisms."
        candidates = "data-lineage map, systems flow, and dependency map."
        rejected = "a systems-flow map would show work movement but hide provenance, derived-data trust checks, and downstream consumer contracts."
        chosen = "data-lineage map with source-to-consumer path, transform rule, quality gate, drift monitor, consumer contract, and rollback route."
        vocabulary = "brand red means source lineage; dark gray means trusted transform; dark red means transform rule; status red means drift or rollback risk; mid gray means consumer readiness; black marks moving data packets."
        narration = "exact datasets, owners, freshness targets, schema versions, and drift thresholds should come from source facts when available; otherwise the scaffold stays schematic."
    else:
        claim = "a good Path of Exile 2 passive route starts from a skill plan, branches into damage and defense, checks attributes, treats keystones as tradeoffs, and keeps Atlas passives separate."
        mechanic = "a planned route grows from the start node, validates build needs at checkpoints, and then separates character-tree decisions from endgame Atlas specialization."
        candidates = "route map, ledger, and radial constellation."
        rejected = "a ledger would show accumulation but not spatial pathing, which is the core mechanic of a passive tree."
        chosen = "route map with checkpoint meters and a separated late-game side layer."
        vocabulary = "brand red route means main build path; status red means damage or risk; dark gray means defense; dark red means attributes and gear fit; red diamond means keystone tradeoff; mid-gray side network means Atlas layer."
        narration = "exact node names, patch-specific balance, and best-build claims are omitted from frames and should be handled in narration or notes only."
    content = f"""# Production Notes

## Source Facts

{facts}

## Visual Metaphor Decision

- Visual pattern: {package["visualPattern"]}.
- Concept claim: {claim}
- Mechanic: {mechanic}
- Candidate metaphors: {candidates}
- Rejected alternative: {rejected}
- Chosen metaphor: {chosen}
- Visual vocabulary: {vocabulary}
- Narration split: {narration}

## Strategy Anchors

{anchors}

## Render Command

```powershell
uv run --script <skill-root>/scripts/build_standalone_explainer.py --project-root {args.project_root.as_posix()} --title "{args.title}" --output-id {args.output_id} --pattern {args.pattern}
```
"""
    paths["production_notes"].write_text(content, encoding="utf-8")


def js_string(value: str) -> str:
    return json.dumps(value)


def write_html(args: argparse.Namespace, paths: dict[str, Path], package: dict[str, object]) -> None:
    paths["html"].parent.mkdir(parents=True, exist_ok=True)
    data = json.dumps(package, indent=2)
    html = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{args.title}</title>
  <style>
    html, body {{ margin: 0; background: {PALETTE["paper"]}; font-family: 'Open Sans', Arial, sans-serif; }}
    #stage {{ width: {args.width}px; height: {args.height}px; display: block; background: {PALETTE["paper"]}; }}
    text {{ paint-order: stroke; stroke: {PALETTE["paper"]}; stroke-width: 4px; }}
  </style>
</head>
<body>
  <svg id="stage" viewBox="0 0 {args.width} {args.height}" role="img" aria-label={js_string(args.title)} data-edge-style={js_string(args.edge_style)} data-box-interior-policy={js_string(BOX_PADDING_POLICY)} data-internal-padding-px="0" data-gray-levels={js_string(",".join(GRAY_LEVELS))}></svg>
  <script>
    const PACKAGE = {data};
    const NS = "http://www.w3.org/2000/svg";
    const palette = {json.dumps(PALETTE)};
    const stage = document.getElementById("stage");
    let currentParent = stage;
    function clamp(v) {{ return Math.max(0, Math.min(1, v)); }}
    function ease(v) {{ v = clamp(v); return v * v * (3 - 2 * v); }}
    const grayLevels = PACKAGE.visualPolicy?.grayLevels?.map((d) => d.hex) || {json.dumps(GRAY_LEVELS)};
    function grayLevel(index) {{ return grayLevels[Math.max(0, Math.min(grayLevels.length - 1, index))]; }}
    const redSurfaceFills = new Set([palette.route, palette.damage, palette.attribute, palette.tradeoff, "#9e1b32", "#e8002a", "#6d1222", "#ffccd5"].map((value) => String(value).toLowerCase()));
    function isRedSurfaceFill(fill) {{
      return redSurfaceFills.has(String(fill || "").trim().toLowerCase());
    }}
    function tonalSurfaceFill(fill, rectWidth, rectHeight, grayIndex = 5) {{
      const w = Math.abs(Number(rectWidth) || 0);
      const h = Math.abs(Number(rectHeight) || 0);
      if (isRedSurfaceFill(fill) && w * h >= 1100 && Math.min(w, h) > 10) return grayLevel(grayIndex);
      return fill;
    }}
    const squareEdge = (stage.getAttribute?.("data-edge-style") || stage.dataset?.edgeStyle) === "square";
    const metroGrid = {METRO_GRID:g};
    function snapToGrid(value) {{
      if (!Number.isFinite(value) || metroGrid <= 0) return value;
      return Math.round(value / metroGrid) * metroGrid;
    }}
    const sourceZones = Array.isArray(PACKAGE.visualZones) ? PACKAGE.visualZones : [];
    const semanticBindings = Array.isArray(PACKAGE.semanticBindings) ? PACKAGE.semanticBindings : [];
    const masonryModules = Array.isArray(PACKAGE.masonryModules) ? PACKAGE.masonryModules : [];
    const masonryRequired = Boolean(PACKAGE.masonryLayout?.required) && masonryModules.length > 0;
    function zoneSourceAnchors(index) {{
      const zone = sourceZones[index] || {{}};
      const values = Array.isArray(zone.sourceAnchors) ? zone.sourceAnchors : [];
      return values.map((value) => String(value || "").trim()).filter(Boolean);
    }}
    function zoneBindingIds(index) {{
      const zone = sourceZones[index] || {{}};
      const zoneId = zone.id || `zone-${{index + 1}}`;
      return semanticBindings
        .filter((binding) => binding && binding.zoneId === zoneId)
        .map((binding) => String(binding.id || "").trim())
        .filter(Boolean);
    }}
    function zoneAttrs(index) {{
      const zone = sourceZones[index] || {{}};
      const anchors = zoneSourceAnchors(index);
      const bindings = zoneBindingIds(index);
      return {{
        "data-zone-id": zone.id || `zone-${{index + 1}}`,
        "data-zone-role": zone.role || "functional-zone",
        "data-zone-index": String(index),
        "data-source-anchor": anchors.join("|"),
        "data-source-anchor-json": JSON.stringify(anchors),
        "data-source-anchor-count": String(anchors.length),
        "data-semantic-binding": bindings.join("|"),
        "data-semantic-binding-json": JSON.stringify(bindings),
      }};
    }}
    function zoneBounds(index, fallback) {{
      const zone = sourceZones[index] || {{}};
      const bounds = zone.bounds || {{}};
      return {{
        x: Number.isFinite(Number(bounds.x)) ? Number(bounds.x) : fallback.x,
        y: Number.isFinite(Number(bounds.y)) ? Number(bounds.y) : fallback.y,
        width: Number.isFinite(Number(bounds.width)) ? Number(bounds.width) : fallback.width,
        height: Number.isFinite(Number(bounds.height)) ? Number(bounds.height) : fallback.height,
      }};
    }}
    function metroZoneFillLevel(index, activeIndex = 0) {{
      const zone = sourceZones[index] || {{}};
      const rawLevel = Number(zone.grayLevel);
      const fallbackLevels = [1, 2, 3, 4, 2];
      const baseLevel = Number.isFinite(rawLevel) ? rawLevel : fallbackLevels[index % fallbackLevels.length];
      return Math.max(1, Math.min(grayLevels.length - 2, baseLevel + (index === activeIndex ? 1 : 0)));
    }}
    function zoneState(activeIndex = 0) {{
      const count = Math.max(5, sourceZones.length || 5);
      const clamped = Math.max(0, Math.min(count - 1, Math.floor(Number(activeIndex) || 0)));
      const zone = sourceZones[clamped] || {{}};
      const anchors = zoneSourceAnchors(clamped);
      const bindings = zoneBindingIds(clamped);
      return {{
        visibleZoneCount: count,
        activeZoneId: zone.id || `zone-${{clamped + 1}}`,
        activeZoneRole: zone.role || "functional-zone",
        activeSourceAnchors: anchors,
        activeSemanticBindings: bindings,
      }};
    }}
    function masonryEntryVector(index) {{
      const vectors = [
        {{ x: -96, y: 0 }},
        {{ x: 0, y: -80 }},
        {{ x: 112, y: 0 }},
        {{ x: 0, y: 96 }},
      ];
      return vectors[index % vectors.length];
    }}
    function bindingZoneIndex(binding, fallbackIndex = 0) {{
      const zoneId = binding?.zoneId;
      const found = sourceZones.findIndex((zone) => zone && zone.id === zoneId);
      if (found >= 0) return found;
      return fallbackIndex % Math.max(1, sourceZones.length || 1);
    }}
    function bindingAttrs(binding, bindingIndex, zoneIndex, active) {{
      const anchor = String(binding?.sourceAnchor || "").trim();
      const bindingId = String(binding?.id || `binding-${{bindingIndex + 1}}`).trim();
      const zone = sourceZones[zoneIndex] || {{}};
      return {{
        "data-semantic-glyph": "true",
        "data-zone-id": zone.id || `zone-${{zoneIndex + 1}}`,
        "data-zone-role": zone.role || "functional-zone",
        "data-zone-index": String(zoneIndex),
        "data-zone-active": active ? "true" : "false",
        "data-source-anchor": anchor,
        "data-source-anchor-json": JSON.stringify(anchor ? [anchor] : []),
        "data-source-anchor-count": anchor ? "1" : "0",
        "data-semantic-binding": bindingId,
        "data-semantic-binding-json": JSON.stringify(bindingId ? [bindingId] : []),
      }};
    }}
    function semanticGlyphKind(anchor) {{
      const text = String(anchor || "").toLowerCase();
      if (/agent_loop|agent loop|context_window|context window|adaptive agent|fixed workflow|environment changes|model [+] tools [+] state [+] loop/.test(text)) return "agent";
      if (/auth|lock|approval|permission|policy|registry|allowlist/.test(text)) return "shield";
      if (/cost|credit|billing|spend|meter|api/.test(text)) return "meter";
      if (/tool|resource|prompt/.test(text)) return "triple";
      if (/bus|protocol|mcp|client|server|port|integration/.test(text)) return "bus";
      if (/risk|bowtie|barrier|failure|attack|surface/.test(text)) return "bowtie";
      if (/circuit|signal|trace/.test(text)) return "trace";
      if (/flow|token|passenger/.test(text)) return "tokens";
      if (/dependency|map|spaghetti|connector/.test(text)) return "nodes";
      if (/json|server|oauth|tools/.test(text)) return "code";
      return "matrix";
    }}
    function drawSemanticGlyph(kind, x, y, size, fill, stroke, attrs, opacity) {{
      const common = {{ rx: 0, fill, stroke, "stroke-width": 1, "fill-opacity": opacity.toFixed(3), "stroke-opacity": Math.min(0.88, opacity + 0.18).toFixed(3), ...attrs }};
      const rect = (gx, gy, width, height, extra = {{}}) => el("rect", {{ x: gx, y: gy, width, height, ...common, ...extra }});
      if (kind === "agent") {{
        [[6, 0], [13, 6], [6, 13], [0, 6]].forEach(([dx, dy]) => rect(x + dx, y + dy, 5, 5));
        el("polyline", {{ points: `${{x + 8}},${{y + 2}} ${{x + 16}},${{y + 8}} ${{x + 8}},${{y + 16}} ${{x}},${{y + 8}} ${{x + 8}},${{y + 2}}`, fill: "none", stroke, "stroke-width": 1, "stroke-linecap": "butt", "stroke-linejoin": "miter", "stroke-opacity": opacity.toFixed(3), ...attrs }});
        return;
      }}
      if (kind === "shield") {{
        rect(x, y, size, size);
        el("rect", {{ x, y, width: size, height: 4, rx: 0, fill: stroke, stroke: "none", "fill-opacity": Math.min(1, opacity + 0.15).toFixed(3), ...attrs }});
        return;
      }}
      if (kind === "meter") {{
        for (let index = 0; index < 3; index++) {{
          const h = 4 + index * 4;
          rect(x + index * 6, y + size - h, 4, h);
        }}
        return;
      }}
      if (kind === "triple") {{
        [[0, 0], [8, 0], [4, 8]].forEach(([dx, dy]) => rect(x + dx, y + dy, 6, 6));
        return;
      }}
      if (kind === "bus") {{
        rect(x, y + 6, size + 8, 4);
        [0, 8, 16].forEach((dx) => rect(x + dx, y, 4, size));
        return;
      }}
      if (kind === "bowtie") {{
        rect(x, y + 2, 6, 10);
        rect(x + 10, y + 2, 6, 10);
        rect(x + 6, y + 6, 4, 2, {{ fill: stroke, stroke: "none", "fill-opacity": opacity.toFixed(3), ...attrs }});
        return;
      }}
      if (kind === "trace") {{
        rect(x, y, 4, 4);
        rect(x + 4, y, 12, 4);
        rect(x + 12, y, 4, 12);
        return;
      }}
      if (kind === "tokens") {{
        [0, 6, 12].forEach((dx) => rect(x + dx, y + (dx === 6 ? 6 : 0), 5, 5));
        return;
      }}
      if (kind === "nodes") {{
        [[0, 2], [9, 0], [16, 9]].forEach(([dx, dy]) => rect(x + dx, y + dy, 5, 5));
        el("line", {{ x1: x + 5, y1: y + 4, x2: x + 9, y2: y + 2, stroke, "stroke-width": 1, "stroke-opacity": opacity.toFixed(3), ...attrs }});
        el("line", {{ x1: x + 14, y1: y + 5, x2: x + 16, y2: y + 10, stroke, "stroke-width": 1, "stroke-opacity": opacity.toFixed(3), ...attrs }});
        return;
      }}
      if (kind === "code") {{
        for (let row = 0; row < 3; row++) {{
          rect(x, y + row * 5, row === 1 ? 16 : 10, 3);
        }}
        return;
      }}
      for (let row = 0; row < 2; row++) {{
        for (let col = 0; col < 2; col++) {{
          rect(x + col * 7, y + row * 7, 5, 5);
        }}
      }}
    }}
    function drawMasonrySemanticGlyphs(activeIndex = 0, progress = 0) {{
      if (!masonryRequired || semanticBindings.length === 0) return;
      const revealStart = Math.min(8, masonryModules.length);
      const revealAmount = masonryModules.length > 0 ? revealStart + clamp(Number(progress) || 0) * (masonryModules.length - revealStart) : 0;
      const zoneFirstModule = new Map();
      masonryModules.forEach((module, index) => {{
        const zoneIndex = Number.isFinite(Number(module?.zoneIndex)) ? Number(module.zoneIndex) : index % Math.max(1, sourceZones.length || 1);
        if (!zoneFirstModule.has(zoneIndex)) zoneFirstModule.set(zoneIndex, index);
      }});
      const zoneSlots = new Map();
      semanticBindings.forEach((binding, bindingIndex) => {{
        const zoneIndex = bindingZoneIndex(binding, bindingIndex);
        const firstModule = zoneFirstModule.has(zoneIndex) ? zoneFirstModule.get(zoneIndex) : 0;
        const phase = revealAmount - firstModule;
        if (phase <= 0.05) return;
        const slot = zoneSlots.get(zoneIndex) || 0;
        zoneSlots.set(zoneIndex, slot + 1);
        const bounds = zoneBounds(zoneIndex, {{ x: 56 + zoneIndex * 180, y: 96, width: 160, height: 140 }});
        const colCount = Math.max(2, Math.floor(Math.max(40, bounds.width) / 24));
        const x = snapToGrid(bounds.x + (slot % colCount) * 20);
        const y = snapToGrid(bounds.y + Math.floor(slot / colCount) * 20);
        const active = zoneIndex === activeIndex;
        const opacity = Math.min(0.92, 0.26 + ease(Math.min(1, phase)) * (active ? 0.58 : 0.38));
        const attrs = bindingAttrs(binding, bindingIndex, zoneIndex, active);
        const kind = semanticGlyphKind(binding?.sourceAnchor);
        const fill = active ? grayLevel(5) : grayLevel((bindingIndex % 3) + 2);
        const stroke = active ? palette.route : grayLevel(5);
        drawSemanticGlyph(kind, x, y, 12, fill, stroke, attrs, opacity);
      }});
    }}
    function drawMasonryWall(activeIndex = 0, progress = 0) {{
      const active = Math.max(0, Math.floor(Number(activeIndex) || 0));
      const revealProgress = clamp(Number(progress) || 0);
      const revealStart = Math.min(8, masonryModules.length);
      const revealAmount = masonryModules.length > 0 ? revealStart + revealProgress * (masonryModules.length - revealStart) : 0;
      for (let index = 0; index < masonryModules.length; index++) {{
        const module = masonryModules[index] || {{}};
        const phase = revealAmount - index;
        if (phase <= 0.05) continue;
        const fit = ease(phase);
        const vector = masonryEntryVector(index);
        const bounds = module.bounds || {{}};
        const zoneIndex = Number.isFinite(Number(module.zoneIndex)) ? Number(module.zoneIndex) : index % Math.max(1, sourceZones.length || 1);
        const level = Math.max(1, Math.min(grayLevels.length - 2, Number(module.grayLevel) || metroZoneFillLevel(zoneIndex, active)));
        const isActive = zoneIndex === active;
        const x = (Number(bounds.x) || 0) + vector.x * (1 - fit);
        const y = (Number(bounds.y) || 0) + vector.y * (1 - fit);
        const width = Number(bounds.width) || 4;
        const height = Number(bounds.height) || 4;
        const fill = grayLevel(isActive ? Math.min(level + 1, grayLevels.length - 2) : level);
        const moduleBoxId = `masonry-wall-module-${{index}}`;
        el("rect", {{
          x,
          y,
          width,
          height,
          rx: 0,
          fill,
          stroke: "none",
          "fill-opacity": clamp(phase),
          "data-fill-for": moduleBoxId,
          "data-fill-axis": "all",
          "data-padding-policy": "zero-verified",
        }});
        el("rect", {{
          x,
          y,
          width,
          height,
          rx: 0,
          fill,
          stroke: isActive ? palette.route : grayLevel(5),
          "stroke-width": isActive ? 3 : 1,
          "fill-opacity": clamp(phase),
          "data-box-id": moduleBoxId,
          "data-masonry-module": "true",
          "data-masonry-wall": "true",
          "data-masonry-order": String(index),
          "data-masonry-phase": phase >= 1 ? "fitted" : "entering",
          "data-masonry-fit": fit.toFixed(3),
          "data-zone-active": isActive ? "true" : "false",
          ...zoneAttrs(zoneIndex),
        }});
      }}
    }}
    function drawMetroMegacanvasBase(activeIndex = 0, progress = 0) {{
      const defaults = [
        {{ x: 44, y: 96, width: 304, height: 248 }},
        {{ x: 44, y: 344, width: 304, height: 260 }},
        {{ x: 348, y: 96, width: 520, height: 508 }},
        {{ x: 868, y: 96, width: 368, height: 248 }},
        {{ x: 868, y: 344, width: 368, height: 260 }},
      ];
      const count = Math.max(5, sourceZones.length || 5);
      const active = Math.max(0, Math.min(count - 1, Math.floor(Number(activeIndex) || 0)));
      if (masonryRequired) {{
        el("rect", {{ x: 48, y: 668, width: 1504, height: 32, rx: 0, fill: grayLevel(5), stroke: "none" }});
        [448, 848, 1192].forEach(x => el("rect", {{ x, y: 88, width: 12, height: 580, rx: 0, fill: grayLevel(5), stroke: "none" }}));
        drawMasonryWall(active, progress);
        const flowOffset = clamp(progress) * 420;
        for (let index = 0; index < 32; index++) {{
          const x = 64 + ((index * 96 + flowOffset) % 1432);
          const y = 636 + (index % 2) * 18;
          const fill = grayLevel(index % 5 === active ? 5 : 3 + (index % 2));
          el("rect", {{ x, y, width: 52, height: 14, rx: 0, fill, stroke: "none", "data-masonry-module": "true", "data-semantic-glyph": "true", "data-transition-type": "evidence-flow" }});
          if (index % 11 === active) {{
            el("rect", {{ x, y, width: 8, height: 14, rx: 0, fill: palette.route, stroke: "none", "data-masonry-module": "true", "data-semantic-glyph": "true", "data-transition-type": "evidence-flow" }});
          }}
        }}
        [448, 848, 1192].forEach((spineX, spineIndex) => {{
          for (let tick = 0; tick < 4; tick++) {{
            const y = 112 + ((tick * 132 + flowOffset + spineIndex * 48) % 520);
            el("rect", {{ x: spineX - 4, y, width: 24, height: 32, rx: 0, fill: grayLevel(tick === active % 4 ? 5 : 3), stroke: "none", "data-masonry-module": "true", "data-semantic-glyph": "true", "data-transition-type": "evidence-flow" }});
          }}
        }});
        const scanX = 48 + ((clamp(progress) * 1504) % 1504);
        el("rect", {{ x: scanX, y: 88, width: 72, height: 580, rx: 0, fill: grayLevel(0), stroke: "none", "fill-opacity": 0.46, "data-masonry-module": "true", "data-semantic-glyph": "true", "data-transition-type": "surface-scan" }});
        for (let stripe = 0; stripe < 72; stripe += 16) {{
          el("rect", {{ x: scanX + stripe, y: 88, width: 8, height: 580, rx: 0, fill: grayLevel(stripe % 32 === 0 ? 5 : 3), stroke: "none", "fill-opacity": 0.66, "data-masonry-module": "true", "data-semantic-glyph": "true", "data-transition-type": "surface-scan" }});
        }}
        for (let segment = 0; segment < 12; segment++) {{
          const y = 104 + segment * 44;
          el("rect", {{ x: scanX + 12, y, width: 48, height: 12, rx: 0, fill: grayLevel(segment % 3 === active % 3 ? 5 : 2), stroke: "none", "fill-opacity": 0.72, "data-masonry-module": "true", "data-semantic-glyph": "true", "data-transition-type": "surface-scan" }});
        }}
        drawMasonrySemanticGlyphs(active, progress);
        return;
      }}
      el("rect", {{ x: 44, y: 604, width: 1192, height: 32, rx: 0, fill: grayLevel(5), stroke: "none" }});
      el("rect", {{ x: 348, y: 96, width: 12, height: 508, rx: 0, fill: grayLevel(5), stroke: "none" }});
      el("rect", {{ x: 868, y: 96, width: 12, height: 508, rx: 0, fill: grayLevel(5), stroke: "none" }});
      for (let index = 0; index < count; index++) {{
        const bounds = zoneBounds(index, defaults[index % defaults.length]);
        const level = metroZoneFillLevel(index, active);
        el("rect", {{
          x: bounds.x,
          y: bounds.y,
          width: bounds.width,
          height: bounds.height,
          rx: 0,
          fill: grayLevel(level),
          stroke: "none",
          "data-zone-foundation": "true",
          "data-zone-active": index === active ? "true" : "false",
          ...zoneAttrs(index),
        }});
      }}
    }}
    function drawSourceZones(activeIndex = 0) {{
      const defaults = [
        {{ x: 44, y: 96, width: 304, height: 248 }},
        {{ x: 44, y: 344, width: 304, height: 260 }},
        {{ x: 348, y: 96, width: 520, height: 508 }},
        {{ x: 868, y: 96, width: 368, height: 248 }},
        {{ x: 868, y: 344, width: 368, height: 260 }},
      ];
      const count = Math.max(5, sourceZones.length || 5);
      const active = Math.max(0, Math.min(count - 1, Math.floor(Number(activeIndex) || 0)));
      for (let index = 0; index < count; index++) {{
        const bounds = zoneBounds(index, defaults[index % defaults.length]);
        const isActive = index === active;
        el("rect", {{
          x: bounds.x,
          y: bounds.y,
          width: bounds.width,
          height: bounds.height,
          rx: 0,
          fill: "none",
          stroke: grayLevel(isActive ? 4 : 3),
          "stroke-width": isActive ? 3 : 1,
          "stroke-opacity": isActive ? 0.55 : 0.24,
          "pointer-events": "none",
          "data-padding-exempt": "zone-evidence-outline",
          "data-zone-active": isActive ? "true" : "false",
          ...zoneAttrs(index),
        }});
      }}
    }}
    function numericAttr(value) {{
      if (typeof value === "number") return value;
      if (typeof value === "string" && value.trim() !== "") {{
        const parsed = Number(value);
        return Number.isFinite(parsed) ? parsed : NaN;
      }}
      return NaN;
    }}
    function normalizeSvgAttrs(name, attrs = {{}}) {{
      const normalized = {{ ...attrs }};
      if (!squareEdge) return normalized;
      if (name === "rect") {{
        const x = numericAttr(normalized.x);
        const y = numericAttr(normalized.y);
        const width = numericAttr(normalized.width);
        const height = numericAttr(normalized.height);
        if (Number.isFinite(x) && Number.isFinite(width)) {{
          const snappedX = snapToGrid(x);
          normalized.x = snappedX;
          normalized.width = Math.max(metroGrid, snapToGrid(x + width) - snappedX);
        }}
        if (Number.isFinite(y) && Number.isFinite(height)) {{
          const snappedY = snapToGrid(y);
          normalized.y = snappedY;
          normalized.height = Math.max(metroGrid, snapToGrid(y + height) - snappedY);
        }}
        normalized.rx = 0;
        normalized.ry = 0;
      }}
      if (name === "line" || name === "polyline" || name === "path") {{
        normalized["stroke-linecap"] = "butt";
        normalized["stroke-linejoin"] = "miter";
      }}
      return normalized;
    }}
    function rectMetrics(node, index) {{
      const x = numericAttr(node.getAttribute("x"));
      const y = numericAttr(node.getAttribute("y"));
      const width = numericAttr(node.getAttribute("width"));
      const height = numericAttr(node.getAttribute("height"));
      if (![x, y, width, height].every(Number.isFinite) || width <= 0 || height <= 0) return null;
      return {{ node, index, x, y, width, height, area: width * height }};
    }}
    function setRectMetrics(item, x, y, width, height) {{
      const sx = snapToGrid(x);
      const sy = snapToGrid(y);
      const sw = Math.max(metroGrid, snapToGrid(x + width) - sx);
      const sh = Math.max(metroGrid, snapToGrid(y + height) - sy);
      item.node.setAttribute("x", sx);
      item.node.setAttribute("y", sy);
      item.node.setAttribute("width", sw);
      item.node.setAttribute("height", sh);
      item.node.setAttribute("rx", 0);
      item.node.setAttribute("ry", 0);
      item.node.setAttribute("data-zone-boundary", item.node.getAttribute("data-zone-boundary") || "flush");
      item.node.setAttribute("data-padding-policy", item.node.getAttribute("data-padding-policy") || "zero-verified");
    }}
    function enforceFlushMasonryInteriors() {{
      if (!masonryRequired || !squareEdge) return;
      const minOffset = 3.5;
      const minSize = 12;
      const minParentSize = minSize * 3;
      for (let pass = 0; pass < 6; pass++) {{
        const rects = Array.from(stage.querySelectorAll("rect"))
          .map((node, index) => rectMetrics(node, index))
          .filter(Boolean);
        const changes = [];
        for (const child of rects) {{
          if (child.node.getAttribute("data-fill-for")) continue;
          if ((child.node.getAttribute("data-masonry-module") || "").toLowerCase() === "true") continue;
          if ((child.node.getAttribute("data-padding-exempt") || "") === "zone-evidence-outline") continue;
          if (Math.min(child.width, child.height) < minSize) continue;
          let chosen = null;
          for (const parent of rects) {{
            if (parent === child) continue;
            if (parent.node.getAttribute("data-fill-for")) continue;
            if ((parent.node.getAttribute("data-padding-exempt") || "") === "zone-evidence-outline") continue;
            const parentIsMasonryModule = (parent.node.getAttribute("data-masonry-module") || "").toLowerCase() === "true";
            const parentIsZone = Boolean(parent.node.getAttribute("data-zone-id") || parent.node.getAttribute("data-box-id"));
            if (!parentIsMasonryModule && !parentIsZone) continue;
            if (parent.index > child.index) continue;
            if (parent.area <= child.area || Math.min(parent.width, parent.height) < minParentSize) continue;
            const offsets = {{
              left: child.x - parent.x,
              top: child.y - parent.y,
              right: parent.x + parent.width - (child.x + child.width),
              bottom: parent.y + parent.height - (child.y + child.height),
            }};
            if (Object.values(offsets).some((value) => value < minOffset)) continue;
            const areaRatio = child.area / parent.area;
            if ((child.node.getAttribute("data-semantic-glyph") || "").toLowerCase() === "true" && areaRatio < 0.035) continue;
            const score = (parentIsMasonryModule ? 2 : 1) * parent.area;
            if (!chosen || score > chosen.score) chosen = {{ parent, offsets, score }};
          }}
          if (!chosen) continue;
          const ordered = Object.entries(chosen.offsets).sort((a, b) => a[1] - b[1]);
          const edge = ordered[0][0];
          let x = child.x;
          let y = child.y;
          let width = child.width;
          let height = child.height;
          if (edge === "left") {{
            width += chosen.offsets.left;
            x = chosen.parent.x;
          }} else if (edge === "right") {{
            width += chosen.offsets.right;
          }} else if (edge === "top") {{
            height += chosen.offsets.top;
            y = chosen.parent.y;
          }} else {{
            height += chosen.offsets.bottom;
          }}
          changes.push({{ child, x, y, width, height }});
        }}
        if (changes.length === 0) break;
        changes.forEach((change) => setRectMetrics(change.child, change.x, change.y, change.width, change.height));
      }}
    }}
    function cameraPose(progress) {{
      const t = clamp(progress);
      if (masonryRequired) {{
        const cameraMotifText = [
          PACKAGE.title,
          PACKAGE.topic,
          ...(PACKAGE.strategyAnchors || []),
          ...(PACKAGE.sourceFacts || []),
          ...(PACKAGE.visualMechanisms || []),
        ].join(" ").toLowerCase();
        const aiAlternativesCamera = /what ai alternatives we have|ai alternatives|atlassian rovo|gemini app|github copilot|claude desktop|claude code|workflow gravity|comparison_grid|credit_meter/.test(cameraMotifText);
        const poses = aiAlternativesCamera ? [
          [0.00, 0, 0, 1.00],
          [0.16, 20, -8, 1.22],
          [0.38, -210, -32, 1.48],
          [0.60, -470, -24, 1.58],
          [0.80, -640, 8, 1.50],
          [1.00, -240, 0, 1.15],
        ] : [
          [0.00, 0, 0, 1.00],
          [0.12, -72, -8, 1.15],
          [0.30, -220, -28, 1.48],
          [0.50, -470, -36, 1.62],
          [0.70, -650, -24, 1.58],
          [0.88, -420, 0, 1.44],
          [1.00, -120, 0, 1.12],
        ];
        let previous = poses[0];
        let next = poses[poses.length - 1];
        for (let index = 1; index < poses.length; index++) {{
          if (t <= poses[index][0]) {{
            previous = poses[index - 1];
            next = poses[index];
            break;
          }}
        }}
        const span = Math.max(0.001, next[0] - previous[0]);
        const blend = ease((t - previous[0]) / span);
        const x = snapToGrid(previous[1] + (next[1] - previous[1]) * blend);
        const y = snapToGrid(previous[2] + (next[2] - previous[2]) * blend);
        const scale = Number((previous[3] + (next[3] - previous[3]) * blend).toFixed(3));
        return {{ x, y, scale, moving: Math.abs(x) > 0.1 || Math.abs(y) > 0.1 || Math.abs(scale - 1) > 0.01 }};
      }}
      const inspect = ease((t - 0.08) / 0.18);
      const handoff = ease((t - 0.36) / 0.22);
      const settle = ease((t - 0.72) / 0.20);
      const scale = Number((1 + 0.10 * inspect + 0.05 * handoff - 0.06 * settle).toFixed(3));
      const x = snapToGrid(-16 * inspect + 24 * handoff - 8 * settle);
      const y = snapToGrid(-8 * inspect + 16 * handoff - 8 * settle);
      return {{ x, y, scale, moving: Math.abs(x) > 0.1 || Math.abs(y) > 0.1 || Math.abs(scale - 1) > 0.01 }};
    }}
    function beginCamera(progress) {{
      const camera = cameraPose(progress);
      const layer = document.createElementNS(NS, "g");
      layer.setAttribute("id", "camera-layer");
      layer.setAttribute("data-camera-x", camera.x);
      layer.setAttribute("data-camera-y", camera.y);
      layer.setAttribute("data-camera-scale", camera.scale);
      layer.setAttribute("transform", `translate(640 360) scale(${{camera.scale}}) translate(${{-640 + camera.x}} ${{-360 + camera.y}})`);
      stage.appendChild(layer);
      currentParent = layer;
      return camera;
    }}
    function withCameraState(state, camera) {{
      return {{ ...state, cameraX: camera.x, cameraY: camera.y, cameraScale: camera.scale, cameraMoving: camera.moving }};
    }}
    function el(name, attrs) {{
      attrs = normalizeSvgAttrs(name, attrs);
      const node = document.createElementNS(NS, name);
      for (const [key, value] of Object.entries(attrs || {{}})) node.setAttribute(key, value);
      (currentParent || stage).appendChild(node);
      return node;
    }}
    function label(x, y, value, size = 20, fill = palette.ink, anchor = "middle", extra = {{}}) {{
      if (masonryRequired) return null;
      el("text", {{ x, y, "font-size": size, "font-weight": 650, "text-anchor": anchor, fill, ...extra }}).textContent = value;
    }}
    function circle(x, y, r, fill, stroke, w = 3) {{ el("circle", {{ cx: x, cy: y, r, fill, stroke, "stroke-width": w }}); }}
    function line(x1, y1, x2, y2, stroke, w = 4) {{ el("line", {{ x1, y1, x2, y2, stroke, "stroke-width": w, "stroke-linecap": "butt" }}); }}
    function renderConceptFrame(videoId, seconds, options = {{}}) {{
      currentParent = stage;
      stage.replaceChildren();
      const safeSeconds = Math.abs(seconds) < 1e-9 ? 0 : seconds;
      const p = seconds / {args.duration};
      el("rect", {{ x: 0, y: 0, width: {args.width}, height: {args.height}, fill: palette.paper }});
      const camera = beginCamera(p);
      drawMetroMegacanvasBase(Math.floor(clamp(p) * 5), p);
      if (PACKAGE.visualPattern === "systems-flow") {{
        const component = (x, y, w, h, name, stroke = palette.line, fill = grayLevel(1)) => {{
          el("rect", {{ x, y, width: w, height: h, rx: 0, fill, stroke, "stroke-width": 2 }});
          if (masonryRequired) {{
            const rightBandX = x + w - 8;
            el("rect", {{ x, y, width: 8, height: h, rx: 0, fill: stroke === "none" ? grayLevel(4) : stroke, stroke: "none" }});
            el("rect", {{ x: rightBandX, y, width: 8, height: h, rx: 0, fill: grayLevel(4), stroke: "none" }});
          }} else {{
            label(x + w / 2, y + h / 2 + 6, name, 18, palette.ink);
          }}
        }};
        const compactText = (value, limit = 16) => {{
          const text = String(value ?? "").trim().replace(/\\s+/g, " ");
          return text;
        }};
        const packet = (x, y, fill, name) => {{
          circle(x, y, 12, fill, fill, 2);
          if (!masonryRequired) label(x, y - 24, name, 14, fill);
        }};
        const sourceSystems = PACKAGE.systemLabels?.length ? PACKAGE.systemLabels : ["source","event","signal","bus","bounded queue","worker pool","DB","retry policy","dead-letter","throughput","throttle"];
        const systemNames = [
          compactText(sourceSystems[0], 14),
          compactText(sourceSystems[1], 14),
          compactText(sourceSystems[2], 14),
          compactText(sourceSystems[3], 12),
          compactText(sourceSystems[4], 18),
          compactText(sourceSystems[5], 14),
          compactText(sourceSystems[6], 13),
          compactText(sourceSystems[7], 18),
          compactText(sourceSystems[8], 18),
          compactText(sourceSystems[9], 18),
          compactText(sourceSystems[10], 17),
        ];
        const agentMotifText = [...sourceSystems, ...(PACKAGE.strategyAnchors || [])].join(" ").toLowerCase();
        const agentMotifRequested = /agent_loop_ring|context_window_box|adaptive agent|fixed workflow|model [+] tools [+] state [+] loop|approval checkpoint/.test(agentMotifText);
        const harnessMotifText = [...sourceSystems, ...(PACKAGE.strategyAnchors || []), PACKAGE.title || "", PACKAGE.topic || ""].join(" ").toLowerCase();
        const hookMotifRequested = /harness hook|event_timeline|lifecycle events|lifecycle boundaries|shield_gate|pretooluse|before tool use|permission request|compaction|notification|github hook|claude event|opencode event|block dangerous|bash command|filter log|preprocessing|token savings|speed-vs-cost|hooks = lifecycle controls/.test(harnessMotifText);
        const skillMotifRequested = !/skill-tree|skill tree|path of exile/.test(harnessMotifText) && /what is a skill|skill_card_stack|skill[.]md|progressive disclosure|long prompt wall|cost meter|cost line|tool badges|deploy-preview|bloated|mini novels|reusable workflow|on-demand reusable workflow/.test(harnessMotifText);
        if (masonryRequired && skillMotifRequested) {{
          let skillRectCounter = 0;
          const sRect = (x, y, width, height, fill, stroke = "none", strokeWidth = 1, extra = {{}}) => {{
            const contract = extra["data-box-id"] || extra["data-fill-for"] || extra["data-zone-id"] ? {{}} : {{ "data-box-id": "skill-independent-module-" + (++skillRectCounter) }};
            el("rect", {{ x, y, width, height, rx: 0, fill: tonalSurfaceFill(fill, width, height), stroke, "stroke-width": strokeWidth, "data-zone-boundary": "flush", "data-padding-policy": "zero-verified", ...contract, ...extra }});
          }};
          const sLine = (points, stroke, strokeWidth = 4, progress = 1, extra = {{}}) => {{
            if (progress <= 0) return;
            const visible = [];
            const safe = clamp(progress);
            const target = safe * (points.length - 1);
            for (let index = 0; index < points.length - 1; index++) {{
              const local = clamp(target - index);
              if (local <= 0) break;
              const a = points[index], b = points[index + 1];
              if (visible.length === 0) visible.push(a);
              visible.push([a[0] + (b[0] - a[0]) * local, a[1] + (b[1] - a[1]) * local]);
              if (local < 1) break;
            }}
            if (visible.length < 2) return;
            el("polyline", {{ points: visible.map(([x, y]) => x + "," + y).join(" "), fill: "none", stroke, "stroke-width": strokeWidth, "stroke-linecap": "butt", "stroke-linejoin": "miter", ...extra }});
          }};
          const sAttrs = (zoneIndex, motif, extra = {{}}) => ({{
            ...zoneAttrs(zoneIndex),
            "data-skill-motif": motif,
            "data-mechanism-id": motif,
            ...extra,
          }});
          const skillCardStackVisible = p > 0.03;
          const skillManifestVisible = skillCardStackVisible;
          const skillFileLayerCount = Math.min(4, Math.floor(ease((p - 0.04) / 0.22) * 5));
          const promptWallCollapsed = p > 0.22;
          const folderStructuresAligned = p > 0.34;
          const frontmatterContractVisible = folderStructuresAligned;
          const triggerSurfaceVisible = p > 0.40;
          const progressiveDisclosureVisible = p > 0.46;
          const skillActivationVisible = p > 0.52;
          const exampleSkillCardsVisible = p > 0.50;
          const triggerExampleCount = Math.min(5, Math.floor(ease((p - 0.46) / 0.36) * 6));
          const toolBadgesAttached = p > 0.64;
          const scriptBlockVisible = p > 0.66;
          const resourceBundleVisible = p > 0.64;
          const resourceModuleCount = Math.min(4, Math.floor(ease((p - 0.62) / 0.22) * 5));
          const validationHarnessVisible = p > 0.68;
          const validationStageLevel = Math.min(5, Math.floor(ease((p - 0.68) / 0.22) * 6));
          const readSurfaceVisible = p > 0.54;
          const readSurfaceLevel = Math.min(4, Math.floor(ease((p - 0.54) / 0.34) * 5));
          const bloatedSkillTrimmed = p > 0.76;
          const finalWorkflowStampVisible = p > 0.84;
          const costMeterLevel = Math.min(4, Math.floor(ease((p - 0.36) / 0.48) * 5));

          [
            [[80, 92], [316, 92], [420, 156]],
            [[352, 332], [704, 332], [780, 412]],
            [[808, 600], [1220, 600], [1312, 520]],
            [[1260, 388], [1612, 388], [1732, 456]],
          ].forEach((points, index) => sLine(points, grayLevel(5), 2, 1, sAttrs(index % 5, "skill-baseline-trace", {{ "data-transition-type": "circuit-signal-trace", "data-transition-id": "skill-baseline-trace-" + index, "data-baseline-trace": "true" }})));

          for (let index = 0; index < 7; index++) {{
            const x = 92 + index * 24;
            const y = 120 + index * 18;
            const cardActive = index < Math.min(7, skillFileLayerCount + 3) && [0, 3, 6].includes(index);
            const fill = cardActive ? grayLevel(5) : grayLevel(2 + (index % 4));
            sRect(x, y, 168, 104, "none", grayLevel(5), 1, sAttrs(0, "skill-card-stack", {{ "data-transition-type": "masonry-construction", "data-transition-id": "skill-card-stack-fan" }}));
            sRect(x, y, 16, 104, grayLevel(5), "none", 1, sAttrs(0, "skill-card-stack-edge"));
            if (cardActive) sRect(x, y, 8, 104, palette.route, "none", 1, sAttrs(0, "skill-card-stack-active-edge"));
            for (let row = 0; row < 4; row++) {{
              const bandFill = row === 0 && index < Math.min(7, skillFileLayerCount + 3) ? fill : grayLevel(1 + ((row + index) % 4));
              sRect(x + 16, y + row * 26, Math.max(28, 152 - row * 18), 24, bandFill, "none", 1, sAttrs(0, "skill-card-stack-mark"));
            }}
          }}

          const collapse = ease((p - 0.16) / 0.24);
          const promptStripCount = Math.max(1, 12 - Math.floor(collapse * 11));
          for (let row = 0; row < 12; row++) {{
            const stripW = 280 - row * 10;
            const x = 432 - 236 * collapse;
            const y = 96 + row * 24 + (6 - row) * 6 * collapse;
            const stripTrimmed = row >= promptStripCount && p > 0.26;
            const fill = stripTrimmed ? grayLevel(5) : grayLevel(2 + (row % 4));
            sRect(x, y, Math.max(44, stripW * (1 - 0.54 * collapse)), 14, fill, "none", 1, sAttrs(1, "long-prompt-wall-collapse", {{ "data-transition-type": "tile-morph", "data-transition-id": "prompt-wall-to-skill-card", "data-transition-phase": promptWallCollapsed ? "fitted" : "entering" }}));
            if (stripTrimmed) sRect(x, y, 6, 14, palette.damage, "none", 1, sAttrs(1, "long-prompt-wall-trim-edge"));
          }}
          sRect(448, 412, 232, 92, grayLevel(1), grayLevel(5), 1, sAttrs(1, "scoped-skill-card", {{ "data-box-id": "skill-scoped-card-box" }}));
          const scopedWidth = 232 * collapse;
          sRect(448, 412, scopedWidth, 92, collapse > 0.72 ? grayLevel(5) : grayLevel(3), "none", 1, sAttrs(1, "scoped-skill-card-fill", {{ "data-fill-for": "skill-scoped-card-box", "data-fill-axis": "x-progress" }}));
          if (collapse > 0.72 && scopedWidth > 0) sRect(448 + Math.max(0, scopedWidth - 8), 412, Math.min(8, scopedWidth), 92, palette.route, "none", 1, sAttrs(1, "scoped-skill-card-active-cap"));
          sLine([[304, 236], [408, 292], [448, 458]], palette.route, 6, collapse, sAttrs(1, "prompt-wall-to-card-route", {{ "data-transition-type": "tile-morph", "data-transition-id": "prompt-wall-to-skill-card", "data-preserved-geometry-id": "long-prompt-wall" }}));

          for (let group = 0; group < 3; group++) {{
            const x = 820 + group * 180;
            sRect(x, 108, 136, 228, grayLevel(1 + group), grayLevel(5), 1, sAttrs(2, "compatible-folder-structure"));
            for (let row = 0; row < 5; row++) {{
              const y = 108 + row * 44;
              const rowActive = folderStructuresAligned && [0, 2].includes(row);
              const fill = rowActive ? grayLevel(5) : grayLevel(2 + ((row + group) % 4));
              sRect(x, y, 104 - row * 8, 28, fill, grayLevel(5), 1, sAttrs(2, "skill-md-folder-node", {{ "data-transition-type": "surface-wipe", "data-transition-id": "skill-folder-align" }}));
              if (rowActive) sRect(x, y, 6, 28, palette.route, "none", 1, sAttrs(2, "skill-md-folder-active-edge"));
              sRect(x + 104, y, 32, 28, grayLevel(3 + ((row + group) % 3)), grayLevel(5), 1, sAttrs(2, "skill-md-folder-terminal"));
              sLine([[x + 104, y + 28], [x + 104, y + 40], [x + 136, y + 40]], grayLevel(5), 2, 1, sAttrs(2, "skill-folder-tree-edge"));
            }}
          }}

          sRect(860, 420, 360, 48, grayLevel(3), grayLevel(5), 1, sAttrs(3, "progressive-disclosure-cost-meter", {{ "data-box-id": "skill-cost-meter-box" }}));
          const skillCostWidth = 360 * (costMeterLevel / 4);
          sRect(860, 420, skillCostWidth, 48, costMeterLevel >= 4 ? grayLevel(5) : grayLevel(4), "none", 1, sAttrs(3, "progressive-disclosure-cost-fill", {{ "data-fill-for": "skill-cost-meter-box", "data-fill-axis": "x-progress" }}));
          if (skillCostWidth > 0) sRect(860 + Math.max(0, skillCostWidth - 8), 420, Math.min(8, skillCostWidth), 48, costMeterLevel >= 4 ? palette.route : palette.attribute, "none", 1, sAttrs(3, "progressive-disclosure-cost-cap"));
          for (let mark = 0; mark < 5; mark++) sRect(868 + mark * 70, 484, 10, 40, grayLevel(5), "none", 1, sAttrs(3, "cost-meter-scale-mark"));
          sRect(772, 400, 52, 120, skillActivationVisible ? grayLevel(5) : grayLevel(3), grayLevel(6), 1, sAttrs(3, "skill-activation-gate", {{ "data-transition-type": "surface-wipe", "data-transition-id": "skill-activation-gate" }}));
          if (skillActivationVisible) sRect(772, 400, 8, 120, palette.route, "none", 1, sAttrs(3, "skill-activation-gate-edge"));
          sLine([[680, 458], [772, 458], [860, 444]], palette.route, 6, ease((p - 0.46) / 0.24), sAttrs(3, "skill-activation-route", {{ "data-transition-type": "flow-token-route", "data-transition-id": "skill-loads-when-relevant" }}));

          for (let index = 0; index < 5; index++) {{
            const x = 1280 + (index % 3) * 84;
            const y = 108 + Math.floor(index / 3) * 88;
            const exampleActive = index < triggerExampleCount && index % 2 === 0;
            const fill = exampleActive ? grayLevel(5) : grayLevel(2 + (index % 4));
            sRect(x, y, 64, 64, fill, grayLevel(5), 1, sAttrs(4, "example-skill-card-cycle"));
            if (exampleActive) sRect(x, y, 8, 64, palette.route, "none", 1, sAttrs(4, "example-skill-card-active-edge"));
            sRect(x, y + 52, 64, 12, grayLevel(5), "none", 1, sAttrs(4, "example-skill-card-edge"));
          }}
          for (let index = 0; index < 6; index++) sRect(1268 + index * 44, 340, 32, 40, index < Math.min(6, resourceModuleCount + 2) ? palette.attribute : grayLevel(2 + (index % 4)), grayLevel(5), 1, sAttrs(4, "tool-badge-snap"));
          for (let row = 0; row < 4; row++) {{
            const scriptActive = row < validationStageLevel;
            sRect(1276, 416 + row * 34, 240 - row * 32, 18, scriptActive ? grayLevel(5) : grayLevel(2 + row), "none", 1, sAttrs(4, "script-validation-runner"));
            if (scriptActive) sRect(1276, 416 + row * 34, 6, 18, palette.route, "none", 1, sAttrs(4, "script-validation-runner-edge"));
          }}
          for (let index = 0; index < 4; index++) sRect(1572 + index * 36, 416, 28, 88, index < readSurfaceLevel ? palette.attribute : grayLevel(2 + index), grayLevel(5), 1, sAttrs(4, "read-surface-level"));

          const trim = ease((p - 0.72) / 0.20);
          sRect(1516, 112, 232, 296, grayLevel(2), grayLevel(5), 1, sAttrs(4, "bloated-skill-card"));
          for (let row = 0; row < 12; row++) {{
            const w = 176 - (row % 4) * 20;
            const trimLineActive = trim > 0.45 && row > 7;
            sRect(1516, 112 + row * 24, w * (1 - 0.58 * trim), 20, trimLineActive ? grayLevel(5) : grayLevel(3 + (row % 3)), "none", 1, sAttrs(4, "bloated-skill-trim-lines", {{ "data-transition-type": "masked-reframe", "data-transition-id": "bloated-skill-trim" }}));
            if (trimLineActive) sRect(1516, 112 + row * 24, 6, 20, palette.damage, "none", 1, sAttrs(4, "bloated-skill-trim-line-edge"));
          }}
          sRect(1516 + 172 * trim, 112, 28, 296, grayLevel(5), grayLevel(6), 1, sAttrs(4, "bloated-skill-trim-blade"));
          sRect(1516 + 172 * trim, 112, 8, 296, palette.damage, "none", 1, sAttrs(4, "bloated-skill-trim-blade-edge"));
          sRect(1516, 448, 184, 76, trim > 0.70 ? grayLevel(5) : grayLevel(3), grayLevel(6), 1, sAttrs(4, "sharp-task-scoped-workflow"));
          if (trim > 0.70) sRect(1516, 448, 8, 76, palette.route, "none", 1, sAttrs(4, "sharp-task-scoped-workflow-edge"));

          if (finalWorkflowStampVisible) {{
            sRect(420, 572, 360, 64, grayLevel(5), grayLevel(6), 1, sAttrs(4, "final-workflow-stamp"));
            for (let index = 0; index < 6; index++) {{
              const stampActive = [0, 5].includes(index);
              sRect(420 + index * 60, 572, 60, 64, stampActive ? grayLevel(5) : grayLevel(2 + (index % 4)), grayLevel(6), 1, sAttrs(4, "final-workflow-stamp-state"));
              if (stampActive) sRect(420 + index * 60, 572, 8, 64, palette.route, "none", 1, sAttrs(4, "final-workflow-stamp-active-edge"));
            }}
            sLine([[780, 604], [944, 604], [1108, 560], [1280, 560]], palette.route, 7, ease((p - 0.84) / 0.14), sAttrs(4, "workflow-reuse-route", {{ "data-transition-type": "flow-token-route", "data-transition-id": "skill-workflow-reuse-route" }}));
          }}
          for (let row = 0; row < 2; row++) {{
            for (let col = 0; col < 24; col++) {{
              const index = row * 24 + col;
              const routeCell = index <= Math.floor(ease((p - 0.12) / 0.66) * 46) && index % 8 === 0;
              const attributeCell = index % 13 === 0 && p > 0.58;
              const damageCell = index % 17 === 0 && p > 0.74;
              let fill = grayLevel(2 + (index % 4));
              sRect(64 + col * 64, 652 + row * 24, 52, 16, fill, "none", 1, sAttrs(index % 5, "skill-evidence-floor"));
              if (routeCell || attributeCell || damageCell) sRect(64 + col * 64, 652 + row * 24, 6, 16, damageCell ? palette.damage : attributeCell ? palette.attribute : palette.route, "none", 1, sAttrs(index % 5, "skill-evidence-floor-accent"));
            }}
          }}
          const visibleMechanismCount = [skillCardStackVisible, promptWallCollapsed, folderStructuresAligned, progressiveDisclosureVisible, skillActivationVisible, exampleSkillCardsVisible, toolBadgesAttached, scriptBlockVisible, bloatedSkillTrimmed, finalWorkflowStampVisible].filter(Boolean).length;
          const beatIndex = Math.max(0, Math.min(4, Math.floor(p * 5)));
          return withCameraState({{ videoId, seconds: safeSeconds, beat: beatIndex, sourceFacts: PACKAGE.sourceFacts.length, visualPattern: PACKAGE.visualPattern, systemLabels: sourceSystems, skillCardStackVisible, skillManifestVisible, frontmatterContractVisible, triggerSurfaceVisible, promptWallCollapsed, folderStructuresAligned, progressiveDisclosureVisible, skillActivationVisible, exampleSkillCardsVisible, toolBadgesAttached, scriptBlockVisible, bloatedSkillTrimmed, finalWorkflowStampVisible, resourceBundleVisible, validationHarnessVisible, readSurfaceVisible, skillFileLayerCount, triggerExampleCount, resourceModuleCount, validationStageLevel, readSurfaceLevel, costMeterLevel, visibleMechanismCount }}, camera);
        }}
        if (masonryRequired && hookMotifRequested) {{
          let hookRectCounter = 0;
          const hRect = (x, y, width, height, fill, stroke = "none", strokeWidth = 1, extra = {{}}) => {{
            const hasBoxContract = extra["data-box-id"] || extra["data-fill-for"] || extra["data-zone-id"];
            const boxContract = hasBoxContract ? {{}} : {{ "data-box-id": `hook-independent-module-${{++hookRectCounter}}` }};
            el("rect", {{ x, y, width, height, rx: 0, fill: tonalSurfaceFill(fill, width, height), stroke, "stroke-width": strokeWidth, "data-zone-boundary": "flush", "data-padding-policy": "zero-verified", ...boxContract, ...extra }});
          }};
          const hLine = (points, stroke, strokeWidth = 4, progress = 1, extra = {{}}) => {{
            if (progress <= 0) return;
            const visible = [];
            const safe = clamp(progress);
            const target = safe * (points.length - 1);
            for (let index = 0; index < points.length - 1; index++) {{
              const local = clamp(target - index);
              if (local <= 0) break;
              const a = points[index], b = points[index + 1];
              if (visible.length === 0) visible.push(a);
              visible.push([a[0] + (b[0] - a[0]) * local, a[1] + (b[1] - a[1]) * local]);
              if (local < 1) break;
            }}
            if (visible.length < 2) return;
            el("polyline", {{ points: visible.map(([x, y]) => `${{x}},${{y}}`).join(" "), fill: "none", stroke, "stroke-width": strokeWidth, "stroke-linecap": "butt", "stroke-linejoin": "miter", ...extra }});
          }};
          const activeHookEventCount = Math.min(8, Math.floor(ease((p - 0.04) / 0.48) * 8 + 0.999));
          const eventTimelineVisible = true;
          const shieldGateOverlayVisible = p > 0.16;
          const githubHookBadgesVisible = p > 0.26;
          const claudeEventCloudVisible = p > 0.32;
          const opencodeEventListVisible = p > 0.38;
          const commandBlockPathVisible = p > 0.44;
          const logFilterPathVisible = p > 0.54;
          const hookJobCascadeVisible = p > 0.62;
          const tokenSavingsCounterVisible = p > 0.66;
          const costLatencyTradeoffVisible = p > 0.70;
          const lifecycleRuleStampVisible = p > 0.82;
          const providerLaneCount = [githubHookBadgesVisible, claudeEventCloudVisible, opencodeEventListVisible].filter(Boolean).length;
          const policyTokenCount = Math.min(6, Math.floor(ease((p - 0.44) / 0.28) * 6 + 0.999));
          const tokenSavingsLevel = Math.min(6, Math.floor(ease((p - 0.66) / 0.24) * 7));
          const latencyCostLevel = Math.min(5, Math.floor(ease((p - 0.70) / 0.22) * 6));
          const eventNodes = Array.from({{ length: 8 }}, (_, index) => [104 + index * 92, 160 + (index % 2 ? 24 : 0)]);
          eventNodes.slice(0, -1).forEach((point, index) => {{
            hLine([point, eventNodes[index + 1]], grayLevel(5), 3, 1, {{ "data-hook-motif": "event-timeline", "data-mechanism-id": "hook-event-timeline", "data-source-anchor-json": JSON.stringify(["event_timeline lights up lifecycle event nodes"]) }});
            if (index < activeHookEventCount - 1) hLine([point, eventNodes[index + 1]], palette.route, 6, 1, {{ "data-hook-motif": "event-timeline", "data-transition-type": "circuit-signal-trace", "data-transition-id": "hook-lifecycle-pulse", "data-transition-phase": "active", "data-preserved-geometry-id": "event_timeline" }});
          }});
          eventNodes.forEach(([x, y], index) => {{
            const eventNodeId = `hook-event-node-${{index}}`;
            const eventNodeActive = index < activeHookEventCount;
            hRect(x - 22, y - 20, 44, 40, eventNodeActive ? grayLevel(5) : grayLevel(2 + (index % 4)), grayLevel(5), 1, {{ "data-box-id": eventNodeId, "data-hook-motif": "event-timeline", "data-mechanism-id": "hook-event-timeline", "data-source-anchor-json": JSON.stringify(["event_timeline lights up lifecycle event nodes"]) }});
            if (eventNodeActive) hRect(x - 22, y - 20, 8, 40, palette.route, "none", 1, {{ "data-box-id": `${{eventNodeId}}-active-edge`, "data-hook-motif": "event-timeline", "data-mechanism-id": "hook-event-active-edge" }});
            hRect(x - 22, y - 20, 12, 40, grayLevel(1 + (index % 4)), "none", 1, {{ "data-box-id": `${{eventNodeId}}-state-glyph`, "data-hook-motif": "event-timeline", "data-mechanism-id": "hook-event-state-glyph" }});
          }});
          const gateClose = ease((p - 0.16) / 0.20);
          hRect(428, 96, 28, 188, shieldGateOverlayVisible ? grayLevel(5) : grayLevel(4), grayLevel(6), 1, {{ "data-hook-motif": "shield-gate-overlay", "data-mechanism-id": "hook-shield-gate", "data-source-anchor-json": JSON.stringify(["shield_gate overlays the event timeline"]) }});
          hRect(792, 96, 28, 188, shieldGateOverlayVisible ? grayLevel(5) : grayLevel(4), grayLevel(6), 1, {{ "data-hook-motif": "shield-gate-overlay", "data-mechanism-id": "hook-shield-gate" }});
          if (shieldGateOverlayVisible) {{
            hRect(428, 96, 8, 188, palette.damage, "none", 1, {{ "data-hook-motif": "shield-gate-overlay", "data-mechanism-id": "hook-shield-gate-accent" }});
            hRect(812, 96, 8, 188, palette.damage, "none", 1, {{ "data-hook-motif": "shield-gate-overlay", "data-mechanism-id": "hook-shield-gate-accent" }});
          }}
          hRect(456, 96, 336 * gateClose, 16, palette.attribute, "none", 1, {{ "data-hook-motif": "shield-gate-overlay", "data-transition-type": "surface-wipe", "data-transition-id": "hook-shield-close", "data-transition-phase": shieldGateOverlayVisible ? "active" : "entering", "data-preserved-geometry-id": "event_timeline" }});
          hRect(456, 268, 336 * gateClose, 16, palette.attribute, "none", 1, {{ "data-hook-motif": "shield-gate-overlay", "data-transition-type": "surface-wipe", "data-transition-id": "hook-shield-close", "data-transition-phase": shieldGateOverlayVisible ? "active" : "entering", "data-preserved-geometry-id": "event_timeline" }});
          const loopPoints = [[520,132],[704,132],[756,196],[664,264],[520,236],[480,176],[520,132]];
          loopPoints.slice(0, -1).forEach((point, index) => hLine([point, loopPoints[index + 1]], index < activeHookEventCount - 1 ? palette.route : grayLevel(5), index < activeHookEventCount - 1 ? 6 : 3, 1, {{ "data-hook-motif": "shield-gate-overlay", "data-mechanism-id": "hook-runtime-loop" }}));
          [[940, 104, "github-hook-badges"], [1116, 104, "claude-event-cloud"], [1292, 104, "opencode-event-list"]].forEach(([x, y, motif], providerIndex) => {{
            const providerVisible = providerIndex === 0 ? githubHookBadgesVisible : providerIndex === 1 ? claudeEventCloudVisible : opencodeEventListVisible;
            const providerBoxId = `hook-provider-surface-${{providerIndex}}`;
            hRect(x, y, 144, 220, grayLevel(1 + providerIndex), grayLevel(5), 1, {{ "data-box-id": providerBoxId, "data-hook-motif": motif, "data-mechanism-id": "hook-provider-events", "data-source-anchor-json": JSON.stringify(["GitHub hook badges for session prompt tool call and stop events", "Claude event cloud around the loop", "OpenCode vertical plugin event list"]) }});
            if (providerIndex === 0) {{
              for (let row = 0; row < 5; row++) {{
                const rowActive = providerVisible && row <= activeHookEventCount - 3;
                hRect(x, y + row * 44, 144, 44, rowActive ? grayLevel(5) : grayLevel(2 + row % 4), "none", 1, {{ "data-box-id": `${{providerBoxId}}-badge-${{row}}`, "data-hook-motif": motif, "data-mechanism-id": "github-hook-badge" }});
                if (rowActive) hRect(x, y + row * 44, 8, 44, palette.route, "none", 1, {{ "data-box-id": `${{providerBoxId}}-badge-${{row}}-active-edge`, "data-hook-motif": motif, "data-mechanism-id": "github-hook-badge-active-edge" }});
                hRect(x, y + row * 44, 16, 44, grayLevel(5), "none", 1, {{ "data-box-id": `${{providerBoxId}}-badge-${{row}}-event-edge`, "data-hook-motif": motif, "data-mechanism-id": "github-hook-badge-edge" }});
              }}
            }} else if (providerIndex === 1) {{
              const cloud = [[x+72,136],[x+116,176],[x+100,244],[x+44,254],[x+24,188],[x+72,136]];
              [[x, y, 72, 72], [x + 72, y, 72, 72], [x, y + 72, 72, 72], [x + 72, y + 72, 72, 72], [x, y + 144, 72, 76], [x + 72, y + 144, 72, 76]].forEach(([cx, cy, cw, ch], cloudIndex) => {{
                const cellFill = providerVisible && [1, 2, 4].includes(cloudIndex) ? palette.attribute : grayLevel(2 + cloudIndex % 4);
                hRect(cx, cy, cw, ch, cellFill, grayLevel(5), 1, {{ "data-box-id": `${{providerBoxId}}-cloud-cell-${{cloudIndex}}`, "data-hook-motif": motif, "data-mechanism-id": "claude-event-cloud-cell" }});
              }});
              hLine(cloud, providerVisible ? palette.attribute : grayLevel(5), 5, ease((p - 0.30) / 0.28), {{ "data-hook-motif": motif, "data-transition-type": "masked-reframe", "data-transition-id": "claude-event-cloud-expand" }});
            }} else {{
              let rowY = y;
              for (let row = 0; row < 6; row++) {{
                const rowHeight = row === 5 ? 40 : 36;
                const rowActive = providerVisible && row <= activeHookEventCount - 4;
                hRect(x, rowY, 144, rowHeight, rowActive ? grayLevel(5) : grayLevel(2 + row % 4), grayLevel(5), 1, {{ "data-box-id": `${{providerBoxId}}-event-row-${{row}}`, "data-hook-motif": motif, "data-mechanism-id": "opencode-event-row" }});
                if (rowActive) hRect(x, rowY, 8, rowHeight, palette.route, "none", 1, {{ "data-box-id": `${{providerBoxId}}-event-row-${{row}}-active-edge`, "data-hook-motif": motif, "data-mechanism-id": "opencode-event-active-edge" }});
                hRect(x + 132, rowY, 12, rowHeight, grayLevel(5), "none", 1, {{ "data-box-id": `${{providerBoxId}}-event-row-${{row}}-edge`, "data-hook-motif": motif, "data-mechanism-id": "opencode-event-edge" }});
                rowY += rowHeight;
              }}
            }}
          }});
          for (let row = 0; row < 5; row++) {{
            for (let col = 0; col < 6; col++) {{
              const commandCellBlocked = commandBlockPathVisible && row === 2 && col >= 2;
              hRect(96 + col * 42, 420 + row * 30, 34, 20, commandCellBlocked ? grayLevel(5) : grayLevel(2 + ((row + col) % 4)), "none", 1, {{ "data-hook-motif": "pretooluse-command-block", "data-mechanism-id": "hook-command-block", "data-source-anchor-json": JSON.stringify(["PreToolUse Bash command block for rm -rf kubectl delete terraform destroy"]) }});
              if (commandCellBlocked) hRect(96 + col * 42, 420 + row * 30, 34, 6, palette.damage, "none", 1, {{ "data-hook-motif": "pretooluse-command-block", "data-mechanism-id": "hook-command-block-cap" }});
            }}
          }}
          hRect(388, 400, 48, 176, commandBlockPathVisible ? grayLevel(5) : grayLevel(4), grayLevel(6), 1, {{ "data-hook-motif": "pretooluse-command-block", "data-mechanism-id": "hook-command-block" }});
          if (commandBlockPathVisible) hRect(428, 400, 8, 176, palette.damage, "none", 1, {{ "data-hook-motif": "pretooluse-command-block", "data-mechanism-id": "hook-command-block-edge" }});
          for (let index = 0; index < 3; index++) {{
            const tokenBlocked = index < policyTokenCount / 2;
            hRect(468 + index * 72, 430, 54, 54, tokenBlocked ? grayLevel(5) : grayLevel(3), grayLevel(5), 1, {{ "data-hook-motif": "pretooluse-command-block", "data-mechanism-id": "hook-command-block" }});
            if (tokenBlocked) hRect(468 + index * 72, 430, 54, 8, palette.damage, "none", 1, {{ "data-hook-motif": "pretooluse-command-block", "data-mechanism-id": "hook-command-block-token-cap" }});
          }}
          hLine([[316,480],[388,480],[436,480]], palette.damage, 6, ease((p - 0.44) / 0.16), {{ "data-hook-motif": "pretooluse-command-block", "data-transition-type": "interrupt-gate-snap", "data-transition-id": "hook-command-deny", "data-preserved-geometry-id": "event-pulse" }});
          hLine([[436,548],[516,596],[660,596]], palette.route, 5, ease((p - 0.58) / 0.18), {{ "data-hook-motif": "pretooluse-command-block", "data-transition-type": "flow-token-route", "data-transition-id": "safe-command-continue" }});
          for (let row = 0; row < 6; row++) {{
            for (let col = 0; col < 8; col++) {{
              hRect(680 + col * 28, 408 + row * 22, 20, 14, logFilterPathVisible && (row + col) % 5 === 0 ? palette.attribute : grayLevel(2 + ((row + col) % 4)), "none", 1, {{ "data-hook-motif": "log-filter-path", "data-mechanism-id": "hook-log-filter", "data-source-anchor-json": JSON.stringify(["log filter and preprocessing path shrinks context before the model"]) }});
            }}
          }}
          hRect(936, 410, 34, 136, logFilterPathVisible ? palette.attribute : grayLevel(4), grayLevel(6), 1, {{ "data-hook-motif": "log-filter-path", "data-mechanism-id": "hook-log-filter" }});
          for (let index = 0; index < 6; index++) {{
            const tokenBarActive = index < tokenSavingsLevel;
            hRect(1008 + index * 32, 430, 24, 76, tokenBarActive ? grayLevel(5) : grayLevel(3 + index % 3), grayLevel(5), 1, {{ "data-hook-motif": "token-savings-counter", "data-mechanism-id": "hook-token-savings", "data-source-anchor-json": JSON.stringify(["token-savings counter and speed-vs-cost slider"]) }});
            if (tokenBarActive) hRect(1008 + index * 32, 430, 8, 76, palette.route, "none", 1, {{ "data-hook-motif": "token-savings-counter", "data-mechanism-id": "hook-token-savings-edge" }});
          }}
          for (let lane = 0; lane < 6; lane++) {{
            const x = 1188 + lane * 60;
            const y = 392 + lane * 24;
            const laneActive = hookJobCascadeVisible && lane <= activeHookEventCount - 4;
            hRect(x, y, 52, 48, laneActive ? grayLevel(5) : grayLevel(2 + lane % 4), grayLevel(5), 1, {{ "data-hook-motif": "hook-job-cascade", "data-mechanism-id": "hook-job-cascade", "data-source-anchor-json": JSON.stringify(["format validation secret protection audit logging notifications jobs cascade"]) }});
            if (laneActive) hRect(x, y, 8, 48, palette.route, "none", 1, {{ "data-hook-motif": "hook-job-cascade", "data-mechanism-id": "hook-job-cascade-edge-active" }});
            hRect(x, y + 40, 52, 8, grayLevel(5), "none", 1, {{ "data-hook-motif": "hook-job-cascade", "data-mechanism-id": "hook-job-cascade-edge" }});
          }}
          hRect(1516, 404, 264, 46, grayLevel(3), grayLevel(5), 1, {{ "data-box-id": "hook-token-savings-meter-box", "data-hook-motif": "token-savings-counter", "data-mechanism-id": "hook-cost-boundary" }});
          const tokenSavingsWidth = 264 * (tokenSavingsLevel / 6);
          hRect(1516, 404, tokenSavingsWidth, 46, grayLevel(5), "none", 1, {{ "data-fill-for": "hook-token-savings-meter-box", "data-fill-axis": "x-progress", "data-hook-motif": "token-savings-counter", "data-mechanism-id": "hook-token-savings-fill" }});
          if (tokenSavingsWidth > 0) hRect(1516 + Math.max(0, tokenSavingsWidth - 8), 404, Math.min(8, tokenSavingsWidth), 46, palette.route, "none", 1, {{ "data-hook-motif": "token-savings-counter", "data-mechanism-id": "hook-token-savings-cap" }});
          hRect(1516, 480, 264, 46, grayLevel(3), grayLevel(5), 1, {{ "data-box-id": "hook-speed-cost-meter-box", "data-hook-motif": "speed-cost-slider", "data-mechanism-id": "hook-cost-boundary", "data-source-anchor-json": JSON.stringify(["token-savings counter and speed-vs-cost slider"]) }});
          const latencyCostWidth = 264 * (latencyCostLevel / 5);
          hRect(1516, 480, latencyCostWidth, 46, latencyCostLevel >= 4 ? grayLevel(5) : grayLevel(4), "none", 1, {{ "data-fill-for": "hook-speed-cost-meter-box", "data-fill-axis": "x-progress", "data-hook-motif": "speed-cost-slider", "data-mechanism-id": "hook-speed-cost-fill" }});
          if (latencyCostWidth > 0) hRect(1516 + Math.max(0, latencyCostWidth - 8), 480, Math.min(8, latencyCostWidth), 46, latencyCostLevel >= 4 ? palette.damage : palette.attribute, "none", 1, {{ "data-hook-motif": "speed-cost-slider", "data-mechanism-id": "hook-speed-cost-cap" }});
          for (let mark = 0; mark < 7; mark++) hRect(1516 + mark * 44, 542, 8, 32, grayLevel(5), "none", 1, {{ "data-hook-motif": "speed-cost-slider", "data-mechanism-id": "hook-slider-scale-mark" }});
          hRect(1516 + 44 * latencyCostLevel, 588, 40, 48, grayLevel(5), grayLevel(6), 1, {{ "data-hook-motif": "speed-cost-slider", "data-transition-type": "tile-morph", "data-transition-id": "speed-cost-slider" }});
          hRect(1516 + 44 * latencyCostLevel, 588, 8, 48, latencyCostLevel >= 4 ? palette.damage : palette.route, "none", 1, {{ "data-hook-motif": "speed-cost-slider", "data-transition-type": "tile-morph", "data-transition-id": "speed-cost-slider-accent" }});
          if (lifecycleRuleStampVisible) {{
            hRect(112, 608, 352, 56, grayLevel(5), grayLevel(6), 1, {{ "data-hook-motif": "lifecycle-controls-stamp", "data-mechanism-id": "hook-lifecycle-controls", "data-source-anchor-json": JSON.stringify(["hooks = lifecycle controls final stamp"]) }});
            for (let index = 0; index < 4; index++) {{
              const stampActive = index % 2 === 0;
              hRect(112 + index * 88, 608, 88, 56, stampActive ? grayLevel(5) : grayLevel(2 + index), grayLevel(6), 1, {{ "data-hook-motif": "lifecycle-controls-stamp", "data-mechanism-id": "hook-lifecycle-stamp-state" }});
              if (stampActive) hRect(112 + index * 88, 608, 8, 56, palette.route, "none", 1, {{ "data-hook-motif": "lifecycle-controls-stamp", "data-mechanism-id": "hook-lifecycle-stamp-edge" }});
            }}
            hLine([[464,636],[584,636],[660,596]], palette.route, 6, ease((p - 0.82) / 0.14), {{ "data-hook-motif": "lifecycle-controls-stamp", "data-transition-type": "surface-wipe", "data-transition-id": "hook-final-boundary" }});
          }}
          for (let row = 0; row < 2; row++) {{
            for (let col = 0; col < 24; col++) {{
              const index = row * 24 + col;
              const routeCell = index <= activeHookEventCount * 4 && index % 9 === 0;
              const attributeCell = index % 13 === 0 && p > 0.60;
              const fill = grayLevel(2 + index % 4);
              hRect(64 + col * 64, 652 + row * 24, 52, 16, fill);
              if (routeCell || attributeCell) hRect(64 + col * 64, 652 + row * 24, 6, 16, attributeCell ? palette.attribute : palette.route, "none", 1, {{ "data-hook-motif": "hook-evidence-floor-accent" }});
            }}
          }}
          const visibleMechanismCount = [eventTimelineVisible, shieldGateOverlayVisible, providerLaneCount >= 3, commandBlockPathVisible, logFilterPathVisible, hookJobCascadeVisible, tokenSavingsCounterVisible, costLatencyTradeoffVisible, lifecycleRuleStampVisible].filter(Boolean).length;
          const beatIndex = Math.max(0, Math.min(4, Math.floor(p * 5)));
          return withCameraState({{ videoId, seconds: safeSeconds, beat: beatIndex, sourceFacts: PACKAGE.sourceFacts.length, visualPattern: PACKAGE.visualPattern, systemLabels: sourceSystems, eventTimelineVisible, shieldGateOverlayVisible, githubHookBadgesVisible, claudeEventCloudVisible, opencodeEventListVisible, hookJobCascadeVisible, commandBlockPathVisible, logFilterPathVisible, tokenSavingsCounterVisible, costLatencyTradeoffVisible, lifecycleRuleStampVisible, activeHookEventCount, providerLaneCount, policyTokenCount, tokenSavingsLevel, latencyCostLevel, visibleMechanismCount }}, camera);
        }}
        const harnessMotifRequested = !/harness hook|harness plugin/.test(harnessMotifText) && /what is a harness|comparison_grid|runtime stack|runtime wrapper|engine icon|vehicle dashboard|same model|different shell|three-column harness|credit_meter|use-case matrix|selection path/.test(harnessMotifText);
        if (masonryRequired && harnessMotifRequested) {{
          const rect = (x, y, width, height, fill, stroke = "none", strokeWidth = 1, extra = {{}}) => {{
            el("rect", {{ x, y, width, height, rx: 0, fill: tonalSurfaceFill(fill, width, height), stroke, "stroke-width": strokeWidth, ...extra }});
          }};
          const poly = (points, stroke, strokeWidth = 4, opacity = 1, extra = {{}}) => {{
            el("polyline", {{ points: points.map((point) => point[0] + "," + point[1]).join(" "), fill: "none", stroke, "stroke-width": strokeWidth, "stroke-linecap": "butt", "stroke-linejoin": "miter", opacity, ...extra }});
          }};
          const selectedCol = Math.min(3, Math.floor(ease((p - 0.06) / 0.20) * 4));
          const selectedRow = Math.min(3, Math.floor(ease((p - 0.12) / 0.22) * 4));
          const gridX = 96;
          const gridY = 112;
          for (let row = 0; row < 4; row++) {{
            for (let col = 0; col < 4; col++) {{
              const selected = row === selectedRow && col === selectedCol && p > 0.18;
              const fill = selected ? palette.route : ((row + col) % 5 === 0 && p > 0.12 ? palette.attribute : grayLevel(2 + ((row + col) % 4)));
              rect(gridX + col * 54, gridY + row * 46, 46, 38, fill, grayLevel(5), 1, {{
                "data-harness-motif": "comparison-grid",
                "data-source-anchor-json": JSON.stringify(["comparison_grid"]),
                "data-mechanism-id": "harness-comparison-grid",
                "data-semantic-role": "mechanism-mark",
              }});
              rect(gridX + col * 54 + 8, gridY + row * 46 + 10, 30, 6, grayLevel(1 + ((row + col) % 4)));
              rect(gridX + col * 54 + 8, gridY + row * 46 + 24, 30, 6, grayLevel(5));
            }}
          }}
          const selectedX = gridX + selectedCol * 54 + 23;
          const selectedY = gridY + selectedRow * 46 + 19;
          poly([[selectedX, selectedY], [360, 220], [492, 220]], palette.route, 6, ease((p - 0.16) / 0.20), {{
            "data-harness-motif": "grid-to-stack-path",
            "data-source-anchor-json": JSON.stringify(["comparison_grid", "runtime stack"]),
            "data-transition-type": "masked-reframe",
            "data-transition-id": "harness-grid-to-stack",
            "data-transition-phase": p > 0.24 ? "fitted" : "entering",
            "data-preserved-geometry-id": "comparison-grid-selected-cell",
          }});

          const layerCount = Math.min(7, Math.floor(ease((p - 0.18) / 0.34) * 8));
          for (let index = 0; index < 7; index++) {{
            const y = 108 + index * 54;
            const fill = index < layerCount && (index === 1 || index === 4) ? palette.route : grayLevel(1 + (index % 5));
            rect(500 + index * 10, y, 300 - index * 18, 42, fill, grayLevel(5), 1, {{
              "data-harness-motif": "runtime-stack-layer",
              "data-source-anchor-json": JSON.stringify(["runtime stack", "instruction tools permissions loop logging layers"]),
              "data-mechanism-id": "harness-runtime-stack",
              "data-zone-boundary": "flush",
              "data-padding-policy": "zero-verified",
            }});
            rect(500 + index * 10, y, 8, 42, grayLevel(5));
            for (let slot = 0; slot < 4; slot++) {{
              const slotFill = index < layerCount && slot <= index % 4 ? palette.attribute : grayLevel(2 + (slot % 4));
              rect(542 + index * 10 + slot * 50, y + 12, 34, 16, slotFill);
            }}
          }}

          const engineCoreVisible = p > 0.22;
          rect(620, 284, 108, 92, engineCoreVisible ? palette.route : grayLevel(3), grayLevel(6), 3, {{
            "data-harness-motif": "engine-core",
            "data-source-anchor-json": JSON.stringify(["engine icon morphs into vehicle dashboard"]),
            "data-mechanism-id": "harness-engine-dashboard",
          }});
          for (let col = 0; col < 3; col++) rect(638 + col * 26, 300, 18, 54, grayLevel(1 + col));
          const dashboardControlsVisible = p > 0.30;
          [[748, 256], [804, 256], [776, 312], [834, 312]].forEach((point, index) => {{
            const fill = dashboardControlsVisible && index % 2 === 0 ? palette.attribute : grayLevel(2 + index);
            rect(point[0], point[1], 44, 40, fill, grayLevel(5), 1, {{
              "data-harness-motif": "dashboard-controls",
              "data-source-anchor-json": JSON.stringify(["vehicle dashboard"]),
              "data-mechanism-id": "harness-engine-dashboard",
            }});
            rect(point[0] + 10, point[1] + 14, 24, 8, grayLevel(5));
          }});
          poly([[674, 330], [728, 330], [748, 276], [804, 276], [834, 332]], palette.route, 5, ease((p - 0.24) / 0.24), {{
            "data-transition-type": "tile-morph",
            "data-transition-id": "harness-engine-dashboard-morph",
            "data-transition-phase": dashboardControlsVisible ? "fitted" : "entering",
            "data-preserved-geometry-id": "shared-model-core",
          }});

          const ringPoints = [[616, 460], [716, 426], [822, 466], [786, 548], [654, 558], [590, 510], [616, 460]];
          ringPoints.slice(0, -1).forEach((point, index) => {{
            poly([point, ringPoints[index + 1]], grayLevel(5), 3);
            if (index < Math.floor(ease((p - 0.34) / 0.34) * 6)) poly([point, ringPoints[index + 1]], palette.attribute, 6, 1, {{
              "data-harness-motif": "agent-loop-ring",
              "data-source-anchor-json": JSON.stringify(["agent_loop_ring"]),
              "data-mechanism-id": "harness-loop-control",
            }});
          }});
          ringPoints.slice(0, -1).forEach((point, index) => rect(point[0] - 20, point[1] - 18, 40, 36, p > 0.34 + index * 0.04 ? palette.attribute : grayLevel(2 + (index % 4)), grayLevel(5), 1));

          const shellOrigins = [[928, 108], [1112, 108], [1296, 108]];
          const modelDrop = ease((p - 0.38) / 0.20);
          shellOrigins.forEach((origin, shellIndex) => {{
            const x = origin[0];
            const y = origin[1];
            rect(x, y, 152, 220, grayLevel(1 + shellIndex), grayLevel(5), 1, {{
              "data-harness-motif": ["copilot-shell", "claude-code-shell", "opencode-shell"][shellIndex],
              "data-source-anchor-json": JSON.stringify(["same model badge in three different harness shells", "three-column harness cards"]),
              "data-mechanism-id": "harness-shell-compare",
            }});
            rect(x + 54, y + 22 + (1 - modelDrop) * -80, 44, 44, palette.route, grayLevel(6), 2, {{
              "data-harness-motif": "same-model-badge",
              "data-source-anchor-json": JSON.stringify(["same model badge in three different harness shells"]),
              "data-preserved-geometry-id": "same-model-badge",
            }});
            if (shellIndex === 0) {{
              for (let row = 0; row < 5; row++) rect(x + 20, y + 92 + row * 22, 112, 14, row <= Math.floor(ease((p - 0.46) / 0.22) * 5) ? palette.route : grayLevel(2 + (row % 4)));
              rect(x + 20, y + 190, 112 * ease((p - 0.52) / 0.22), 16, palette.attribute);
            }} else if (shellIndex === 1) {{
              const loop = [[x + 46, y + 116], [x + 86, y + 94], [x + 124, y + 124], [x + 92, y + 168], [x + 46, y + 154], [x + 46, y + 116]];
              loop.slice(0, -1).forEach((point, index) => poly([point, loop[index + 1]], index < Math.floor(ease((p - 0.46) / 0.24) * 5) ? palette.attribute : grayLevel(5), 4));
              [[x + 22, y + 170], [x + 62, y + 170], [x + 102, y + 170], [x + 62, y + 124]].forEach((point) => rect(point[0], point[1], 28, 24, grayLevel(4), grayLevel(5), 1));
            }} else {{
              rect(x + 24, y + 94, 104, 28, p > 0.50 ? palette.attribute : grayLevel(3), grayLevel(5), 1);
              for (let row = 0; row < 3; row++) {{
                for (let col = 0; col < 3; col++) {{
                  rect(x + 28 + col * 34, y + 144 + row * 22, 24, 16, p > 0.54 && row === col ? palette.route : grayLevel(2 + ((row + col) % 4)));
                }}
              }}
            }}
          }});

          const toolCountLevel = Math.min(6, Math.floor(ease((p - 0.52) / 0.22) * 7));
          for (let index = 0; index < 6; index++) rect(932 + index * 34, 408, 26, 58, index < toolCountLevel ? palette.route : grayLevel(3 + (index % 3)), grayLevel(5), 1, {{
            "data-harness-motif": "tool-count",
            "data-source-anchor-json": JSON.stringify(["credit_meter", "default tools"]),
            "data-mechanism-id": "harness-cost-meter",
          }});
          const creditMeterLevel = Math.min(5, Math.floor(ease((p - 0.42) / 0.38) * 6));
          rect(932, 496, 244, 42, grayLevel(3), grayLevel(5), 1, {{
            "data-harness-motif": "credit-meter",
            "data-source-anchor-json": JSON.stringify(["credit_meter"]),
            "data-mechanism-id": "harness-cost-meter",
          }});
          rect(932, 496, 244 * (creditMeterLevel / 5), 42, creditMeterLevel >= 4 ? palette.damage : palette.attribute);
          for (let mark = 0; mark < 6; mark++) rect(932 + mark * 48, 548, 8, 30, grayLevel(5));

          const featureGridMuted = p > 0.70;
          const useCaseMatrixActive = p > 0.74;
          for (let row = 0; row < 4; row++) {{
            for (let col = 0; col < 5; col++) {{
              let fill = featureGridMuted ? grayLevel(2) : grayLevel(2 + ((row + col) % 4));
              if (useCaseMatrixActive && ((row === 0 && col === 1) || (row === 1 && col === 2) || (row === 2 && col === 3) || (row === 3 && col === 4))) fill = p > 0.82 ? palette.route : palette.attribute;
              rect(1212 + col * 52, 408 + row * 42, 44, 34, fill, grayLevel(5), 1, {{
                "data-harness-motif": "fit-matrix",
                "data-source-anchor-json": JSON.stringify(["feature grid fades behind use-case matrix", "highlighted selection path"]),
                "data-mechanism-id": "harness-selection-matrix",
              }});
            }}
          }}
          const selectionPathHighlighted = p > 0.82;
          poly([[1234, 425], [1286, 467], [1338, 509], [1390, 551]], palette.route, 7, ease((p - 0.80) / 0.16), {{
            "data-harness-motif": "selection-path",
            "data-source-anchor-json": JSON.stringify(["highlighted selection path"]),
            "data-transition-type": "surface-wipe",
            "data-transition-id": "harness-selection-path",
            "data-transition-phase": selectionPathHighlighted ? "fitted" : "entering",
          }});

          for (let row = 0; row < 2; row++) {{
            for (let col = 0; col < 22; col++) {{
              const index = row * 22 + col;
              const fill = index <= Math.floor(ease((p - 0.16) / 0.60) * 44) && index % 8 === 0 ? palette.route : (index % 11 === 0 && p > 0.60 ? palette.attribute : grayLevel(2 + (index % 4)));
              rect(64 + col * 64, 648 + row * 26, 52, 18, fill);
            }}
          }}
          const comparisonGridVisible = true;
          const runtimeStackVisible = layerCount >= 2;
          const layersAssembling = layerCount;
          const modelBadgeShared = modelDrop > 0.25;
          const sameModelShellCount = modelDrop > 0.75 ? 3 : Math.floor(modelDrop * 4);
          const shellCopilotVisible = sameModelShellCount >= 1;
          const shellClaudeCodeVisible = sameModelShellCount >= 2;
          const shellOpenCodeVisible = sameModelShellCount >= 3;
          const threeHarnessShellsVisible = sameModelShellCount >= 3;
          const agentLoopRingVisible = p > 0.34;
          const creditMeterRising = creditMeterLevel >= 2;
          const visibleMechanismCount = [comparisonGridVisible, runtimeStackVisible, engineCoreVisible, dashboardControlsVisible, threeHarnessShellsVisible, creditMeterRising, featureGridMuted, useCaseMatrixActive, selectionPathHighlighted, agentLoopRingVisible].filter(Boolean).length;
          const beatIndex = Math.max(0, Math.min(4, Math.floor(p * 5)));
          return withCameraState({{ videoId, seconds: safeSeconds, beat: beatIndex, sourceFacts: PACKAGE.sourceFacts.length, visualPattern: PACKAGE.visualPattern, systemLabels: sourceSystems, comparisonGridVisible, runtimeStackVisible, engineCoreVisible, dashboardControlsVisible, layersAssembling, modelBadgeShared, sameModelShellCount, shellCopilotVisible, shellClaudeCodeVisible, shellOpenCodeVisible, threeHarnessShellsVisible, toolCountLevel, creditMeterLevel, creditMeterRising, featureGridMuted, useCaseMatrixActive, selectionPathHighlighted, agentLoopRingVisible, visibleMechanismCount }}, camera);
        }}
        if (masonryRequired && agentMotifRequested) {{
          const rect = (x, y, width, height, fill, stroke = "none", strokeWidth = 1, extra = {{}}) => {{
            el("rect", {{ x, y, width, height, rx: 0, fill: tonalSurfaceFill(fill, width, height), stroke, "stroke-width": strokeWidth, ...extra }});
          }};
          const poly = (points, stroke, strokeWidth = 4, opacity = 1, extra = {{}}) => {{
            el("polyline", {{ points: points.map(([x, y]) => `${{x}},${{y}}`).join(" "), fill: "none", stroke, "stroke-width": strokeWidth, "stroke-linecap": "butt", "stroke-linejoin": "miter", opacity, ...extra }});
          }};
          const contextPaneCount = Math.max(0, Math.min(5, Math.floor(ease((p - 0.04) / 0.26) * 6)));
          for (let index = 0; index < 5; index++) {{
            const active = index < contextPaneCount;
            const x = 96 + index * 24;
            const y = 112 + index * 22;
            const width = 244 - index * 28;
            const height = 188 - index * 18;
            rect(x, y, width, height, grayLevel(1 + (index % 5)), grayLevel(5), 1, {{
              "data-agent-motif": "context-pane",
              "data-source-anchor-json": JSON.stringify(["context_window_box"]),
            }});
            rect(x, y, 8, height, active ? (index % 2 === 0 ? palette.route : grayLevel(5)) : grayLevel(3));
          }}
          for (let row = 0; row < 4; row++) {{
            for (let col = 0; col < 4; col++) {{
              const on = row + col < contextPaneCount + 2;
              const fill = on && (row + col) % 4 === 0 ? palette.route : grayLevel(2 + ((row + col) % 4));
              rect(120 + col * 44, 352 + row * 34, 34, 24, fill);
            }}
          }}

          const loopPoints = [[600, 156], [790, 270], [738, 464], [520, 476], [420, 300], [600, 156]];
          const loopProgress = ease((p - 0.10) / 0.54);
          const loopActiveSegments = Math.floor(loopProgress * (loopPoints.length - 1) + 0.001);
          for (let index = 0; index < loopPoints.length - 1; index++) {{
            poly([loopPoints[index], loopPoints[index + 1]], grayLevel(5), 4);
            if (index < loopActiveSegments) poly([loopPoints[index], loopPoints[index + 1]], palette.route, 8);
          }}
          loopPoints.slice(0, -1).forEach(([x, y], index) => {{
            const active = loopProgress * 5 >= index;
            const fill = active ? [palette.route, grayLevel(4), palette.attribute, grayLevel(3), palette.tradeoff][index] : grayLevel(2 + index % 4);
            rect(x - 38, y - 34, 76, 68, fill, grayLevel(6), active ? 2 : 1, {{
              "data-agent-motif": "agent-loop-station",
              "data-source-anchor-json": JSON.stringify(["agent_loop_ring"]),
            }});
            rect(x - 22, y - 8, 18 + (index % 3) * 8, 16, grayLevel(1 + index % 4));
            rect(x + 4, y - 8, 26, 16, grayLevel(4));
          }});
          const packetIndex = Math.min(loopPoints.length - 2, loopActiveSegments);
          const packetStart = loopPoints[packetIndex];
          const packetEnd = loopPoints[packetIndex + 1];
          const local = Math.max(0, Math.min(1, loopProgress * (loopPoints.length - 1) - packetIndex));
          rect(packetStart[0] + (packetEnd[0] - packetStart[0]) * local - 12, packetStart[1] + (packetEnd[1] - packetStart[1]) * local - 12, 24, 24, palette.gold, grayLevel(6), 1);

          rect(566, 280, 132, 104, grayLevel(1), palette.route, 3, {{
            "data-agent-motif": "model-tools-state-loop",
            "data-source-anchor-json": JSON.stringify(["Model + Tools + State + Loop"]),
          }});
          for (let row = 0; row < 3; row++) {{
            for (let col = 0; col < 3; col++) {{
              const fill = p > 0.24 && (row + col) % 3 === 0 ? palette.route : grayLevel(2 + ((row + col) % 4));
              rect(586 + col * 32, 300 + row * 24, 24, 16, fill);
            }}
          }}
          [[498, 208], [742, 198], [842, 368], [652, 530], [404, 410], [404, 226]].forEach(([x, y], index) => {{
            const active = p > 0.22 + index * 0.055;
            const fill = active && index % 2 === 0 ? palette.attribute : grayLevel(2 + index % 4);
            rect(x, y, 40, 40, fill, grayLevel(5), 1, {{
              "data-agent-motif": "tool-action",
              "data-source-anchor-json": JSON.stringify(["tool action loop"]),
            }});
            rect(x + 8, y + 8, 24, 8, grayLevel(1 + index % 4));
            rect(x + 8, y + 24, 24, 8, grayLevel(4));
          }});

          const environmentIndex = Math.max(0, Math.min(4, Math.floor(ease((p - 0.24) / 0.48) * 5)));
          const environmentStates = ["repo", "browser", "ticket", "docs", "database"];
          [[934,112], [1112,112], [934,268], [1112,268], [1024,436]].forEach(([x, y], index) => {{
            const active = index <= environmentIndex;
            rect(x, y, 132, 104, grayLevel(1 + index % 5), grayLevel(5), 1, {{
              "data-agent-motif": "environment-surface",
              "data-source-anchor-json": JSON.stringify(["environment changes"]),
              "data-environment-state": environmentStates[index],
            }});
            for (let row = 0; row < 3; row++) {{
              for (let col = 0; col < 4; col++) {{
                const reveal = ease((p - 0.18 - index * 0.05 - (row + col) * 0.018) / 0.18);
                const fill = reveal > 0.62 && (row + col + index) % 5 === 0 ? palette.damage : grayLevel(2 + ((row * 2 + col + index) % 4));
                rect(x + 12 + col * 26, y + 14 + row * 24, 18, 14, fill);
              }}
            }}
            if (active) poly([[698, 332], [846 + index * 18, 332], [846 + index * 18, y + 52], [x, y + 52]], index % 2 === 0 ? palette.route : palette.attribute, 4);
          }});

          for (let index = 0; index < 5; index++) {{
            const x = 116 + index * 96;
            const active = p > 0.34 + index * 0.045;
            rect(x, 578, 58, 44, active ? palette.route : grayLevel(3), grayLevel(5), 1, {{
              "data-agent-motif": "fixed-workflow-lane",
              "data-source-anchor-json": JSON.stringify(["fixed workflow lane"]),
            }});
            if (index > 0) poly([[x - 38, 600], [x, 600]], grayLevel(5), 3);
          }}
          const adaptivePath = [[672, 602], [768, 560], [880, 608], [1016, 566], [1136, 610], [1224, 554], [1328, 610]];
          adaptivePath.slice(0, -1).forEach((point, index) => {{
            poly([point, adaptivePath[index + 1]], index < Math.floor(ease((p - 0.48) / 0.34) * 6) ? palette.attribute : grayLevel(5), index < 2 ? 6 : 4);
          }});
          adaptivePath.forEach(([x, y], index) => {{
            rect(x - 24, y - 22, 48, 44, p > 0.46 + index * 0.04 ? palette.attribute : grayLevel(2 + index % 4), grayLevel(5), 1, {{
              "data-agent-motif": "adaptive-agent-lane",
              "data-source-anchor-json": JSON.stringify(["adaptive agent lane"]),
            }});
          }});
          if (p > 0.60) poly([[880, 608], [934, 664], [1090, 664]], palette.tradeoff, 5);

          const approvalCheckpointVisible = p > 0.68;
          rect(1390, 252, 112, 120, approvalCheckpointVisible ? palette.tradeoff : grayLevel(3), grayLevel(6), 2, {{
            "data-agent-motif": "approval-checkpoint",
            "data-source-anchor-json": JSON.stringify(["approval checkpoint"]),
          }});
          rect(1414, 284, 64, 16, grayLevel(1));
          rect(1426, 316, 40, 36, approvalCheckpointVisible ? grayLevel(5) : grayLevel(2));
          const modelToolsStateLoopBadgeVisible = p > 0.78;
          for (let index = 0; index < 4; index++) {{
            const x = 1332 + index * 74;
            rect(x, 448, 60, 60, modelToolsStateLoopBadgeVisible && index === 3 ? palette.route : grayLevel(2 + index), grayLevel(5), 1, {{
              "data-agent-motif": "model-tools-state-loop-badge",
              "data-source-anchor-json": JSON.stringify(["Model + Tools + State + Loop"]),
            }});
            rect(x + 10, 462, 40, 8, grayLevel(1 + index % 4));
            rect(x + 10, 482, 40, 8, grayLevel(5));
          }}

          for (let row = 0; row < 2; row++) {{
            for (let col = 0; col < 14; col++) {{
              const index = row * 14 + col;
              const fill = index <= Math.floor(ease((p - 0.16) / 0.60) * 28) && index % 7 === 0 ? palette.route : grayLevel(2 + index % 4);
              rect(64 + col * 52, 656 + row * 32, 42, 22, fill);
            }}
          }}
          const agentLoopRingVisible = p > 0.08;
          const toolActionLoopVisible = p > 0.28;
          const fixedWorkflowLaneVisible = p > 0.34;
          const adaptiveAgentLaneVisible = p > 0.48;
          const queueSlots = Math.floor(ease((p - 0.14) / 0.38) * 8);
          const workerActive = toolActionLoopVisible;
          const retryVisible = adaptiveAgentLaneVisible;
          const deadLetterVisible = approvalCheckpointVisible;
          const feedbackVisible = modelToolsStateLoopBadgeVisible;
          const workflowContrastVisible = fixedWorkflowLaneVisible && adaptiveAgentLaneVisible;
          const closureVisible = approvalCheckpointVisible && modelToolsStateLoopBadgeVisible;
          const visibleMechanismCount = [agentLoopRingVisible, contextPaneCount >= 3, environmentIndex >= 2, toolActionLoopVisible, workflowContrastVisible, closureVisible].filter(Boolean).length;
          const beatIndex = Math.max(0, Math.min(4, Math.floor(p * 5)));
          return withCameraState({{ videoId, seconds: safeSeconds, beat: beatIndex, sourceFacts: PACKAGE.sourceFacts.length, visualPattern: PACKAGE.visualPattern, systemLabels: sourceSystems, queueSlots, workerActive, retryVisible, deadLetterVisible, feedbackVisible, visibleMechanismCount, agentLoopRingVisible, contextPaneCount, environmentState: environmentStates[environmentIndex], environmentSurfaceCount: environmentIndex + 1, toolActionLoopVisible, fixedWorkflowLaneVisible, adaptiveAgentLaneVisible, approvalCheckpointVisible, modelToolsStateLoopBadgeVisible }}, camera);
        }}
        const denseMotifText = [...sourceSystems, ...(PACKAGE.strategyAnchors || []), ...(PACKAGE.sourceFacts || []), PACKAGE.title || "", PACKAGE.topic || ""].join(" ").toLowerCase();
        const llmConceptRequested = /what is an llm|large language model|token_stream|context_window_box|transformer|autoregressive|parameter|gpu_rack|next token/.test(denseMotifText);
        const billingConceptRequested = /llm billing|billing|credit_meter|ai credit|token cost|api cost|subscription|local gpu|pricing|cost meter/.test(denseMotifText);
        const mcpConceptRequested = /what is an mcp|model context protocol|mcp_bus|mcp server|tools resources prompts|tools \\/ resources \\/ prompts|registry|allowlist|client and server|tool surface/.test(denseMotifText);
        if (masonryRequired && (llmConceptRequested || billingConceptRequested || mcpConceptRequested)) {{
          let denseRectCounter = 0;
          const motifId = billingConceptRequested ? "billing-cost-map" : mcpConceptRequested ? "mcp-protocol-bus" : "llm-token-transformer-map";
          const dAttrs = (zoneIndex, mechanismId, extra = {{}}) => ({{
            ...zoneAttrs(zoneIndex),
            "data-dense-systems-motif": motifId,
            "data-mechanism-id": mechanismId,
            ...extra,
          }});
          const dRect = (x, y, width, height, fill, stroke = "none", strokeWidth = 1, extra = {{}}) => {{
            const hasBoxContract = extra["data-box-id"] || extra["data-fill-for"] || extra["data-zone-id"] || extra["data-masonry-module"];
            const boxContract = hasBoxContract ? {{}} : {{ "data-box-id": `dense-systems-module-${{++denseRectCounter}}` }};
            el("rect", {{ x, y, width, height, rx: 0, fill: tonalSurfaceFill(fill, width, height), stroke, "stroke-width": strokeWidth, "data-zone-boundary": "flush", "data-padding-policy": "zero-verified", ...boxContract, ...extra }});
          }};
          const dLine = (points, stroke, strokeWidth = 4, progress = 1, extra = {{}}) => {{
            if (progress <= 0) return;
            const visible = [];
            const safe = clamp(progress);
            const target = safe * (points.length - 1);
            for (let index = 0; index < points.length - 1; index++) {{
              const local = clamp(target - index);
              if (local <= 0) break;
              const a = points[index], b = points[index + 1];
              if (visible.length === 0) visible.push(a);
              visible.push([a[0] + (b[0] - a[0]) * local, a[1] + (b[1] - a[1]) * local]);
              if (local < 1) break;
            }}
            if (visible.length < 2) return;
            el("polyline", {{ points: visible.map(([x, y]) => `${{x}},${{y}}`).join(" "), fill: "none", stroke, "stroke-width": strokeWidth, "stroke-linecap": "butt", "stroke-linejoin": "miter", ...extra }});
          }};

          const tokenLevel = Math.min(24, Math.floor(ease((p - 0.04) / 0.34) * 25));
          const matrixLevel = Math.min(80, Math.floor(ease((p - 0.16) / 0.42) * 81));
          const stackLevel = Math.min(8, Math.floor(ease((p - 0.28) / 0.34) * 9));
          const meterLevel = Math.min(5, Math.floor(ease((p - 0.40) / 0.34) * 6));
          const gateLevel = Math.min(4, Math.floor(ease((p - 0.54) / 0.28) * 5));
          const evidenceLevel = Math.min(60, Math.floor(ease((p - 0.10) / 0.72) * 61));

          [
            [[84, 112], [360, 112], [444, 180]],
            [[404, 360], [744, 360], [900, 252]],
            [[948, 132], [1216, 188], [1456, 188]],
            [[104, 612], [552, 612], [760, 548], [1000, 548]],
          ].forEach((points, index) => dLine(points, grayLevel(5), 2, 1, dAttrs(index % 5, "dense-baseline-trace", {{ "data-transition-type": "circuit-signal-trace", "data-transition-id": `dense-baseline-${{index}}`, "data-baseline-trace": "true" }})));

          dRect(80, 104, 292, 260, grayLevel(2), grayLevel(5), 1, dAttrs(0, "dense-input-surface", {{ "data-masonry-module": "true" }}));
          dRect(404, 96, 420, 308, grayLevel(1), grayLevel(5), 1, dAttrs(1, "dense-matrix-surface", {{ "data-masonry-module": "true" }}));
          dRect(884, 104, 304, 278, grayLevel(3), grayLevel(5), 1, dAttrs(2, "dense-stack-surface", {{ "data-masonry-module": "true" }}));
          dRect(1220, 112, 300, 240, grayLevel(2), grayLevel(5), 1, dAttrs(3, "dense-policy-surface", {{ "data-masonry-module": "true" }}));
          dRect(84, 432, 468, 150, grayLevel(1), grayLevel(5), 1, dAttrs(4, "dense-meter-surface", {{ "data-masonry-module": "true" }}));
          dRect(604, 456, 468, 128, grayLevel(2), grayLevel(5), 1, dAttrs(4, "dense-feedback-surface", {{ "data-masonry-module": "true" }}));

          for (let index = 0; index < 24; index++) {{
            const row = Math.floor(index / 8);
            const col = index % 8;
            const active = index < tokenLevel;
            const x = 108 + col * 30;
            const y = 132 + row * 42;
            const fill = active ? grayLevel(4 + ((index + row) % 2)) : grayLevel(1 + (index % 4));
            dRect(x, y, 22, 30, fill, grayLevel(5), 1, dAttrs(0, "dense-token-stream", {{ "data-masonry-module": "true" }}));
            if (active && index % 6 === 0) dRect(x, y, 6, 30, palette.route, "none", 1, dAttrs(0, "dense-token-state-cap", {{ "data-masonry-module": "true", "data-semantic-glyph": "true" }}));
          }}
          for (let row = 0; row < 8; row++) {{
            for (let col = 0; col < 10; col++) {{
              const index = row * 10 + col;
              const active = index < matrixLevel;
              const strong = active && ((row === col % 8) || (row + col) % 11 === 0);
              const fill = strong ? grayLevel(5) : active ? grayLevel(2 + ((row + col) % 4)) : grayLevel(1);
              dRect(428 + col * 36, 122 + row * 30, 28, 22, fill, "none", 1, dAttrs(1, "dense-attention-or-tool-matrix", {{ "data-masonry-module": "true" }}));
              if (strong && (row + col) % 3 === 0) dRect(428 + col * 36, 122 + row * 30, 6, 22, palette.route, "none", 1, dAttrs(1, "dense-matrix-state-cap", {{ "data-masonry-module": "true", "data-semantic-glyph": "true" }}));
            }}
          }}
          for (let layer = 0; layer < 8; layer++) {{
            const y = 128 + layer * 30;
            const active = layer < stackLevel;
            const width = billingConceptRequested ? 168 + layer * 8 : mcpConceptRequested ? 228 - layer * 10 : 248 - layer * 12;
            dRect(916, y, width, 22, active ? grayLevel(5 - (layer % 2)) : grayLevel(2 + (layer % 4)), "none", 1, dAttrs(2, "dense-layer-stack", {{ "data-masonry-module": "true" }}));
            if (active && layer % 2 === 0) dRect(916 + width - 8, y, 8, 22, palette.route, "none", 1, dAttrs(2, "dense-layer-active-edge", {{ "data-masonry-module": "true", "data-semantic-glyph": "true" }}));
          }}
          for (let index = 0; index < 4; index++) {{
            const x = 1248 + index * 62;
            const active = index < gateLevel;
            dRect(x, 142, 46, 80, active ? grayLevel(5) : grayLevel(2 + index), grayLevel(5), 1, dAttrs(3, "dense-gate-column", {{ "data-masonry-module": "true" }}));
            if (active) dRect(x, 142, 8, 80, palette.route, "none", 1, dAttrs(3, "dense-gate-state-edge", {{ "data-masonry-module": "true", "data-semantic-glyph": "true" }}));
            dRect(x, 248, 46, 54, active && index >= 2 ? grayLevel(5) : grayLevel(2 + ((index + 1) % 4)), grayLevel(5), 1, dAttrs(3, "dense-policy-cell", {{ "data-masonry-module": "true" }}));
          }}
          for (let index = 0; index < 5; index++) {{
            const x = 120 + index * 78;
            const boxId = `dense-meter-${{index}}`;
            dRect(x, 472, 58, 74, grayLevel(2 + (index % 3)), grayLevel(5), 1, dAttrs(4, "dense-meter-shell", {{ "data-box-id": boxId }}));
            const filled = 74 * (index < meterLevel ? (meterLevel / 5) : 0);
            dRect(x, 472 + 74 - filled, 58, filled, grayLevel(5), "none", 1, dAttrs(4, "dense-meter-fill", {{ "data-fill-for": boxId, "data-fill-axis": "y-progress" }}));
            if (filled > 0) dRect(x, 472 + 74 - filled, 58, 6, palette.route, "none", 1, dAttrs(4, "dense-meter-state-cap", {{ "data-masonry-module": "true", "data-semantic-glyph": "true" }}));
          }}
          for (let row = 0; row < 3; row++) {{
            for (let col = 0; col < 8; col++) {{
              const index = row * 8 + col;
              const active = index < Math.floor(evidenceLevel / 2);
              dRect(632 + col * 48, 480 + row * 30, 38, 22, active ? grayLevel(3 + ((row + col) % 3)) : grayLevel(1 + ((row + col) % 4)), "none", 1, dAttrs(4, "dense-feedback-grid", {{ "data-masonry-module": "true" }}));
              if (active && index % 7 === 0) dRect(632 + col * 48, 480 + row * 30, 6, 22, palette.route, "none", 1, dAttrs(4, "dense-feedback-state-cap", {{ "data-masonry-module": "true", "data-semantic-glyph": "true" }}));
            }}
          }}
          for (let row = 0; row < 2; row++) {{
            for (let col = 0; col < 30; col++) {{
              const index = row * 30 + col;
              const active = index < evidenceLevel;
              dRect(64 + col * 50, 640 + row * 28, 40, 18, active ? grayLevel(2 + (index % 4)) : grayLevel(1), "none", 1, dAttrs(index % 5, "dense-evidence-floor", {{ "data-masonry-module": "true" }}));
              if (active && index % 13 === 0) dRect(64 + col * 50, 640 + row * 28, 6, 18, palette.route, "none", 1, dAttrs(index % 5, "dense-evidence-floor-cap", {{ "data-masonry-module": "true", "data-semantic-glyph": "true" }}));
            }}
          }}

          const routeColor = billingConceptRequested ? palette.route : mcpConceptRequested ? palette.attribute : palette.route;
          dLine([[342, 246], [428, 246], [520, 246]], routeColor, 6, ease((p - 0.08) / 0.20), dAttrs(0, "dense-primary-route", {{ "data-transition-type": "flow-token-route", "data-transition-id": "dense-primary-route" }}));
          dLine([[780, 246], [916, 216], [1188, 216]], routeColor, 6, ease((p - 0.32) / 0.22), dAttrs(2, "dense-stack-route", {{ "data-transition-type": "flow-token-route", "data-transition-id": "dense-stack-route" }}));
          dLine([[1188, 216], [1248, 182], [1488, 182]], routeColor, 5, ease((p - 0.50) / 0.22), dAttrs(3, "dense-policy-route", {{ "data-transition-type": "flow-token-route", "data-transition-id": "dense-policy-route" }}));
          dLine([[358, 546], [604, 520], [1032, 520]], routeColor, 5, ease((p - 0.62) / 0.22), dAttrs(4, "dense-feedback-route", {{ "data-transition-type": "flow-token-route", "data-transition-id": "dense-feedback-route" }}));

          if (billingConceptRequested) {{
            dRect(1324, 280, 168, 28, grayLevel(5), "none", 1, dAttrs(3, "billing-subscription-band", {{ "data-masonry-module": "true" }}));
            dRect(1324, 316, 132, 28, grayLevel(4), "none", 1, dAttrs(3, "billing-api-band", {{ "data-masonry-module": "true" }}));
            dRect(1324, 352, 96, 28, grayLevel(3), "none", 1, dAttrs(3, "billing-local-band", {{ "data-masonry-module": "true" }}));
          }} else if (mcpConceptRequested) {{
            dLine([[180, 252], [520, 252], [916, 252], [1432, 252]], grayLevel(5), 8, 1, dAttrs(1, "mcp-bus-spine", {{ "data-transition-type": "surface-wipe", "data-transition-id": "mcp-bus-spine" }}));
            for (let index = 0; index < 6; index++) {{
              const x = 524 + index * 72;
              dRect(x, 292, 44, 34, index < gateLevel + 2 ? grayLevel(5) : grayLevel(3), grayLevel(5), 1, dAttrs(1, "mcp-tool-resource-prompt-port", {{ "data-masonry-module": "true" }}));
            }}
          }} else {{
            for (let index = 0; index < 6; index++) {{
              const x = 130 + index * 30;
              const h = 22 + index * 12;
              dRect(x, 306 - h, 22, h, index < stackLevel ? grayLevel(5) : grayLevel(3), "none", 1, dAttrs(0, "llm-probability-bars", {{ "data-masonry-module": "true" }}));
              if (index === Math.min(5, meterLevel)) dRect(x, 306 - h, 22, 6, palette.route, "none", 1, dAttrs(0, "llm-selected-token-cap", {{ "data-masonry-module": "true", "data-semantic-glyph": "true" }}));
            }}
          }}

          const queueSlots = tokenLevel;
          const workerActive = stackLevel >= 4;
          const retryVisible = gateLevel >= 2;
          const deadLetterVisible = gateLevel >= 4;
          const feedbackVisible = meterLevel >= 4;
          const visibleMechanismCount = [tokenLevel >= 16, matrixLevel >= 48, stackLevel >= 6, meterLevel >= 4, gateLevel >= 3, evidenceLevel >= 36].filter(Boolean).length;
          const beatIndex = Math.max(0, Math.min(4, Math.floor(p * 5)));
          return withCameraState({{ videoId, seconds: safeSeconds, beat: beatIndex, sourceFacts: PACKAGE.sourceFacts.length, visualPattern: PACKAGE.visualPattern, systemLabels: sourceSystems, queueSlots, workerActive, retryVisible, deadLetterVisible, feedbackVisible, visibleMechanismCount, denseSystemsMotif: motifId, tokenLevel, matrixLevel, stackLevel, meterLevel, gateLevel, evidenceLevel, llmConceptVisible: llmConceptRequested, billingConceptVisible: billingConceptRequested, mcpConceptVisible: mcpConceptRequested }}, camera);
        }}
        if (!masonryRequired) {{
          el("rect", {{ x: 55, y: 112, width: 305, height: 490, rx: 0, fill: grayLevel(0), stroke: "none" }});
          el("rect", {{ x: 390, y: 112, width: 505, height: 490, rx: 0, fill: grayLevel(1), stroke: "none" }});
          el("rect", {{ x: 925, y: 112, width: 300, height: 490, rx: 0, fill: grayLevel(2), stroke: "none" }});
        }}
        if (!masonryRequired) {{
          label(84, 145, "INTAKE", 15, palette.muted, "start");
          label(420, 145, "PIPELINE", 15, palette.muted, "start");
          label(955, 145, "CONTROL", 15, palette.muted, "start");
        }}
        component(71, 222, 128, 64, systemNames[0], palette.route, grayLevel(0));
        component(71, 327, 128, 64, systemNames[1], palette.damage, grayLevel(2));
        component(71, 432, 128, 64, systemNames[2], palette.attribute, grayLevel(2));
        component(226, 214, 96, 272, systemNames[3], palette.route, grayLevel(3));
        component(440, 235, 130, 230, systemNames[4], "none", grayLevel(1));
        for (let i = 0; i < 8; i++) {{
          const filled = i < Math.floor(ease((p - 0.18) / 0.32) * 8);
          el("rect", {{ x: 440, y: 244 + i * 28, width: 128, height: 20, rx: 0, fill: filled ? grayLevel(5) : grayLevel(4) }});
          if (filled) el("rect", {{ x: 440, y: 244 + i * 28, width: 8, height: 20, rx: 0, fill: palette.route, stroke: "none" }});
        }}
        [262, 350, 438].forEach((y, idx) => component(625, y - 34, 180, 68, `${{systemNames[5]}} ${{idx + 1}}`, ease((p - 0.38) / 0.24) > 0.2 ? palette.defense : palette.line, grayLevel(2)));
        component(810, 304, 102, 92, systemNames[6], palette.damage, grayLevel(2));
        component(970, 185, 210, 70, systemNames[7], palette.damage, grayLevel(2));
        component(970, 300, 210, 70, systemNames[8], palette.tradeoff, grayLevel(2));
        component(970, 420, 210, 115, systemNames[9], palette.route, grayLevel(0));
        if (masonryRequired) {{
          const activeCols = Math.max(1, Math.min(8, Math.floor(ease((p - 0.44) / 0.30) * 8)));
          for (let row = 0; row < 5; row++) {{
            for (let col = 0; col < 8; col++) {{
              const level = 1 + ((row + col) % 4);
              const fill = col < activeCols && (row === 1 || row === 3) ? grayLevel(5) : grayLevel(level);
              el("rect", {{ x: 1212 + col * 36, y: 124 + row * 36, width: 28, height: 28, rx: 0, fill, stroke: "none" }});
              if (col < activeCols && (row === 1 || row === 3) && col % 3 === 0) el("rect", {{ x: 1212 + col * 36, y: 124 + row * 36, width: 6, height: 28, rx: 0, fill: palette.route, stroke: "none" }});
            }}
          }}
          [392, 432, 472, 512, 552, 592].forEach((y, row) => {{
            const barWidth = 56 + ease((p - 0.52 - row * 0.035) / 0.18) * (180 - row * 16);
            el("rect", {{ x: 1212, y, width: barWidth, height: 18, rx: 0, fill: row === 1 || row === 4 ? grayLevel(5) : grayLevel(4), stroke: "none" }});
            if (row === 1 || row === 4) el("rect", {{ x: 1212, y, width: 6, height: 18, rx: 0, fill: palette.route, stroke: "none" }});
          }});
          for (let row = 0; row < 3; row++) {{
            for (let col = 0; col < 4; col++) {{
              const cellOn = ease((p - 0.50 - (row + col) * 0.025) / 0.16) > 0.35;
              const fill = cellOn ? grayLevel((row + col) % 3 === 0 ? 5 : 4) : grayLevel(3);
              el("rect", {{ x: 1416 + col * 32, y: 488 + row * 32, width: 24, height: 24, rx: 0, fill, stroke: "none" }});
              if (cellOn && (row + col) % 3 === 0) el("rect", {{ x: 1416 + col * 32, y: 488 + row * 32, width: 6, height: 24, rx: 0, fill: palette.route, stroke: "none" }});
            }}
          }}
        }}
        line(199,350,274,350,palette.line,4); line(274,350,440,350,palette.line,4); line(570,350,625,350,palette.line,4); line(805,350,861,350,palette.line,4);
        line(805,350,970,220,palette.line,3); line(805,350,970,335,palette.line,3); line(1075,420,1075,575,palette.line,3); line(1075,575,270,575,palette.line,3);
        const mainProgress = ease((p - 0.08) / 0.45);
        const queueSlots = Math.floor(ease((p - 0.18) / 0.32) * 8);
        const workerActive = ease((p - 0.38) / 0.24) > 0.2;
        const retryVisible = p > 0.55;
        const deadLetterVisible = p > 0.66;
        const feedbackVisible = p > 0.72;
        const visibleMechanismCount = [mainProgress > 0.12, queueSlots > 0, workerActive, retryVisible, deadLetterVisible, feedbackVisible].filter(Boolean).length;
        line(180,350,274,350,palette.route, mainProgress > 0.12 ? 7 : 0);
        line(274,350,440,350,palette.route, mainProgress > 0.28 ? 7 : 0);
        line(570,350,625,350,palette.route, mainProgress > 0.56 ? 7 : 0);
        line(805,350,861,350,palette.route, mainProgress > 0.82 ? 7 : 0);
        if (feedbackVisible) {{
          el("rect", {{ x: 206, y: 500, width: 136, height: 88, rx: 0, fill: grayLevel(4), stroke: palette.attribute, "stroke-width": 3 }});
          [526, 546, 566].forEach(y => line(228, y, 320, y, palette.attribute, 4));
          if (!masonryRequired) label(274, 514, systemNames[10], 15, palette.attribute);
        }}
        const x = 199 + Math.min(1, mainProgress) * 662;
        packet(x, 350, palette.gold, "job");
        if (retryVisible) packet(805 + ease((p - 0.55) / 0.18) * 165, 350 - ease((p - 0.55) / 0.18) * 130, palette.damage, "retry");
        if (deadLetterVisible) packet(805 + ease((p - 0.66) / 0.16) * 165, 350 - ease((p - 0.66) / 0.16) * 15, palette.tradeoff, "fail");
        if (feedbackVisible) packet(1075 - ease((p - 0.72) / 0.20) * 805, 575, palette.attribute, "limit");
        const beats = ["Events enter one shared contract.", "Queue pressure becomes visible.", "Workers transform jobs.", "Retry and dead-letter are explicit branches.", "Feedback limits intake before failure."];
        const beatIndex = Math.max(0, Math.min(beats.length - 1, Math.floor(p * beats.length)));
        return withCameraState({{ videoId, seconds: safeSeconds, beat: beatIndex, sourceFacts: PACKAGE.sourceFacts.length, visualPattern: PACKAGE.visualPattern, systemLabels: sourceSystems, queueSlots, workerActive, retryVisible, deadLetterVisible, feedbackVisible, visibleMechanismCount }}, camera);
      }}
      if (PACKAGE.visualPattern === "state-machine") {{
        const component = (x, y, w, h, name, stroke = palette.line, fill = grayLevel(2), labelColor = palette.ink) => {{
          el("rect", {{ x, y, width: w, height: h, rx: 0, fill, stroke, "stroke-width": 3 }});
          label(x + w / 2, y + h / 2 + 6, name, 18, labelColor);
        }};
        const compactText = (value, limit = 16) => {{
          const text = String(value ?? "").trim().replace(/\\s+/g, " ");
          return text;
        }};
        label(64, 128, "states", 13, palette.muted, "start");
        label(368, 128, "guards", 13, palette.muted, "start");
        label(888, 128, "terminal", 13, palette.muted, "start");
        label(368, 468, "recovery", 13, palette.tradeoff, "start");
        const sourceStates = PACKAGE.stateLabels?.length ? PACKAGE.stateLabels : ["received","validated","authorized","executing","committed","done"];
        const sourceGuards = PACKAGE.guardLabels?.length ? PACKAGE.guardLabels : ["schema guard","policy guard","capacity guard"];
        const stateNames = sourceStates.map((value) => compactText(value, 16));
        const guardNames = sourceGuards.map((value) => compactText(value, 14));
        const states = [
          [72,232,148,68,stateNames[0],palette.route],
          [228,232,148,68,stateNames[1],palette.route],
          [384,232,148,68,stateNames[2],palette.attribute],
          [540,232,148,68,stateNames[3],palette.defense],
          [696,232,148,68,stateNames[4],palette.defense],
          [912,232,176,68,stateNames[5],palette.atlas],
        ];
        const stateProgress = ease((p - 0.04) / 0.50);
        const activeState = Math.min(states.length - 1, Math.floor(stateProgress * states.length));
        const mid = (d) => [d[0] + d[2] / 2, d[1] + d[3] / 2];
        for (let i = 0; i < states.length - 1; i++) {{
          const a = mid(states[i]);
          const b = mid(states[i + 1]);
          line(a[0], a[1], b[0], b[1], palette.line, 5);
          if (stateProgress * (states.length - 1) > i) line(a[0], a[1], b[0], b[1], palette.route, 9);
        }}
        [[guardNames[0],384,ease((p - 0.14)/0.12)],[guardNames[1],552,ease((p - 0.28)/0.12)],[guardNames[2],720,ease((p - 0.42)/0.12)]].forEach(g => {{
          component(g[1] - 64, 136, 128, 48, g[0], g[2] > 0.15 ? palette.attribute : palette.line, g[2] > 0.15 ? grayLevel(3) : grayLevel(2));
          if (g[2] > 0.45) line(g[1],184,g[1],232,palette.attribute,3);
        }});
        states.forEach((d, i) => {{
          const active = ease((p - 0.06 - i * 0.08) / 0.10);
          component(d[0], d[1], d[2], d[3], d[4], active > 0.1 ? d[5] : palette.line, active > 0.55 ? grayLevel(3) : grayLevel(2));
          if (i === activeState && p < 0.72) circle(d[0] + d[2] / 2, d[1] - 22, 10, palette.gold, palette.gold, 2);
        }});
        const rollbackVisible = p > 0.58;
        const compensationVisible = p > 0.70;
        const terminalVisible = p > 0.82;
        line(612,300,612,528,palette.line,4); line(612,528,456,528,palette.line,4); line(456,528,300,528,palette.line,4); line(300,528,300,300,palette.line,4);
        if (rollbackVisible) {{
          line(612,300,612,528,palette.damage,7); line(612,528,456,528,palette.damage,7);
          component(612,488,144,64,"rollback",palette.damage,"#ffccd5");
        }}
        if (compensationVisible) {{
          line(456,528,300,528,palette.tradeoff,7); line(300,528,300,300,palette.tradeoff,7);
          component(432,488,144,64,"compensate",palette.tradeoff,"#ffccd5");
        }}
        if (terminalVisible) component(904,456,272,100,"terminal states",palette.atlas,grayLevel(4));
        const activeMid = mid(states[activeState]);
        const tokenX = 146 + Math.min(1, stateProgress) * 854;
        circle(tokenX, activeMid[1], 13, palette.gold, palette.gold, 2);
        el("rect", {{ x: 72, y: 452, width: 176, height: 100, rx: 0, fill: grayLevel(4), stroke: palette.route, "stroke-width": 3 }});
        el("rect", {{ x: 72, y: 452, width: 176 * stateProgress, height: 100, rx: 0, fill: palette.route, stroke: "none" }});
        label(160, 506, "coverage", 15, palette.ink);
        el("rect", {{ x: 904, y: 344, width: 176, height: 88, rx: 0, fill: grayLevel(5), stroke: palette.attribute, "stroke-width": 3 }});
        el("rect", {{ x: 904, y: 344, width: 176 * ease((p - 0.20) / 0.42), height: 88, rx: 0, fill: palette.attribute, stroke: "none" }});
        label(992, 392, "guard pass", 15, palette.ink);
        const beats = ["A lifecycle is states plus guarded transitions.", "Separate guards explain why a transition can fail.", "Execution is a state, not a hidden middle.", "Rollback and compensation are explicit paths.", "Terminal states separate done work from parked work."];
        const beatIndex = Math.max(0, Math.min(beats.length - 1, Math.floor(p * beats.length)));
        const visibleMechanismCount = [stateProgress > 0.2, stateProgress > 0.55, rollbackVisible, compensationVisible, terminalVisible].filter(Boolean).length;
        return withCameraState({{ videoId, seconds: safeSeconds, beat: beatIndex, sourceFacts: PACKAGE.sourceFacts.length, visualPattern: PACKAGE.visualPattern, stateLabels: sourceStates, guardLabels: sourceGuards, activeState, rollbackVisible, compensationVisible, terminalVisible, visibleMechanismCount }}, camera);
      }}
      if (PACKAGE.visualPattern === "comparison-matrix") {{
        const component = (x, y, w, h, name, stroke = palette.line, fill = "#fff") => {{
          el("rect", {{ x, y, width: w, height: h, rx: 0, fill, stroke, "stroke-width": 3 }});
          label(x + w / 2, y + h / 2 + 6, name, 18, palette.ink);
        }};
        el("rect", {{ x: 55, y: 112, width: 1165, height: 494, rx: 0, fill: "#fff", stroke: "#cfcfcf" }});
        [
          [55, 112, 260, 494, grayLevel(0)],
          [315, 112, 540, 494, grayLevel(1)],
          [855, 112, 365, 494, grayLevel(2)],
          [1188, 112, 32, 494, grayLevel(5)],
        ].forEach(([x, y, width, height, fill]) => el("rect", {{ x, y, width, height, rx: 0, fill, stroke: "none" }}));
        label(88, 145, "OPTIONS", 15, palette.muted, "start");
        label(88, 260, "CRITERIA", 15, palette.muted, "start");
        label(930, 145, "DECISION", 15, palette.muted, "start");
        const compactText = (value, limit = 18) => {{
          const text = String(value ?? "").trim().replace(/\\s+/g, " ");
          return text;
        }};
        const sourceOptions = PACKAGE.decisionOptions?.length ? PACKAGE.decisionOptions : ["fast path","balanced","safe path"];
        const sourceCriteria = PACKAGE.decisionCriteria?.length ? PACKAGE.decisionCriteria : ["time","quality","risk","cost"];
        const optionNames = sourceOptions.map((value) => compactText(value, 18));
        const criterionNames = sourceCriteria.map((value) => compactText(value, 16));
        const options = [[335,optionNames[0],palette.route,78],[555,optionNames[1],palette.defense,88],[775,optionNames[2],palette.attribute,70]];
        const criteria = [[criterionNames[0],[0.92,0.72,0.45],palette.route],[criterionNames[1],[0.52,0.86,0.90],palette.defense],[criterionNames[2],[0.38,0.72,0.94],palette.tradeoff],[criterionNames[3],[0.82,0.64,0.48],palette.damage]];
        options.forEach((d, i) => {{
          const active = ease((p - 0.05 - i * 0.06) / 0.12);
          component(d[0] - 88, 150, 176, 75, d[1], active > 0.1 ? d[2] : palette.line, "#ffffff");
          label(d[0], 202, `${{d[3]}}%`, 15, d[2]);
        }});
        const criteriaRevealed = Math.min(criteria.length, Math.floor(ease((p - 0.20) / 0.35) * (criteria.length + 0.999)));
        [250, 430, 650, 850].forEach(x => line(x,250,x,522,palette.line,2));
        [260, 318, 376, 434, 492].forEach(y => line(250,y,850,y,palette.line,2));
        criteria.forEach((row, r) => {{
          const y = 290 + r * 58;
          const rowActive = r < criteriaRevealed;
          component(92, y - 22, 113, 44, row[0], rowActive ? row[2] : palette.line, "#ffffff");
          row[1].forEach((v, o) => {{
            const x = options[o][0];
            el("rect", {{ x: x - 74, y: y - 15, width: 148, height: 30, rx: 0, fill: "#cfcfcf" }});
            const fill = rowActive ? v * ease((p - 0.20 - r * 0.07) / 0.22) : 0;
            if (fill > 0.02) el("rect", {{ x: x - 74, y: y - 15, width: 148 * fill, height: 30, rx: 0, fill: row[2] }});
            if (rowActive && p > 0.48 && o === 1) circle(x + 92, y, 8, palette.gold, palette.gold, 2);
          }});
        }});
        const scoreShiftVisible = p > 0.48;
        const tradeoffVisible = p > 0.62;
        const recommendationVisible = p > 0.76;
        const guardrailVisible = p > 0.86;
        if (tradeoffVisible) {{
          component(910,205,255,110,"tradeoff lens",palette.damage,"#ffccd5");
          label(1038,260,"speed gains can raise risk",16,palette.ink);
        }}
        if (recommendationVisible) {{
          component(910,350,255,95,"recommended",palette.defense,"#e7e7e7");
          label(1038,405,`${{optionNames[1]}} wins`,22,palette.ink);
          line(555,225,1010,350,palette.defense,5);
        }}
        if (guardrailVisible) {{
          component(910,480,255,75,"guardrail",palette.attribute,"#e7e7e7");
          label(1038,530,"reject if risk spikes",16,palette.ink);
        }}
        const cursorY = 250 + ease((p - 0.18) / 0.54) * 240;
        line(852,250,852,492,palette.gold,3);
        circle(852,cursorY,11,palette.gold,palette.gold,2);
        const beats = ["Compare options against the same criteria.", "Scores reveal where each option actually differs.", "A tradeoff lens explains why the top score shifts.", "Recommendation appears only after criteria are visible.", "Guardrails keep the decision from becoming a blind ranking."];
        const beatIndex = Math.max(0, Math.min(beats.length - 1, Math.floor(p * beats.length)));
        const visibleMechanismCount = [criteriaRevealed >= 2, scoreShiftVisible, tradeoffVisible, recommendationVisible, guardrailVisible].filter(Boolean).length;
        return {{ videoId, seconds: safeSeconds, beat: beatIndex, sourceFacts: PACKAGE.sourceFacts.length, visualPattern: PACKAGE.visualPattern, decisionOptions: sourceOptions, decisionCriteria: sourceCriteria, optionCount: 3, criteriaRevealed, scoreShiftVisible, tradeoffVisible, recommendationVisible, guardrailVisible, visibleMechanismCount }};
      }}
      if (PACKAGE.visualPattern === "causal-loop") {{
        const component = (x, y, w, h, nameText, stroke = palette.line, fill = "#fff") => {{
          el("rect", {{ x, y, width: w, height: h, rx: 0, fill, stroke, "stroke-width": 3 }});
          label(x + w / 2, y + h / 2 + 6, nameText, 18, palette.ink);
        }};
        const route = (points, color, width = 4, opacity = 1) => el("polyline", {{
          points: points.map((d) => d.join(",")).join(" "),
          fill: "none",
          stroke: color,
          "stroke-width": width,
          "stroke-linecap": "butt",
          "stroke-linejoin": "miter",
          opacity
        }});
        const meter = (x, y, nameText, value, color) => {{
          const width = 130;
          const height = 65;
          el("rect", {{ x, y, width, height, rx: 0, fill: grayLevel(3), stroke: palette.line }});
          const filled = Math.max(0, Math.min(width, width * ease(value)));
          if (filled > 0) el("rect", {{ x, y, width: filled, height, rx: 0, fill: color }});
          label(x + width / 2, y + height / 2 + 5, nameText, 15, palette.ink);
        }};
        el("rect", {{ x: 55, y: 112, width: 1165, height: 494, rx: 0, fill: "#fff", stroke: "#cfcfcf" }});
        [
          [55, 112, 360, 494, grayLevel(0)],
          [415, 112, 340, 494, grayLevel(1)],
          [755, 112, 465, 494, grayLevel(2)],
          [55, 556, 1165, 50, grayLevel(5)],
        ].forEach(([x, y, width, height, fill]) => el("rect", {{ x, y, width, height, rx: 0, fill, stroke: "none" }}));
        label(88, 145, "CAUSE MAP", 15, palette.muted, "start");
        label(915, 145, "INTERVENTION", 15, palette.muted, "start");
        const compactText = (value, limit = 22) => {{
          const text = String(value ?? "").trim().replace(/\\s+/g, " ");
          return text;
        }};
        const sourceCausalLabels = PACKAGE.causalLabels?.length ? PACKAGE.causalLabels : ["trigger","pressure","behavior","outcome","side effect","intervention"];
        const causalLabels = sourceCausalLabels.map((value) => compactText(value));
        const loopPoints = [[230,286],[390,210],[430,210],[610,286],[645,310],[478,430],[430,430],[242,338],[210,310]];
        const balancingPoints = [[645,310],[760,260],[825,340],[720,430],[478,430]];
        const sideEffectPoints = [[645,310],[790,470],[920,470]];
        const interventionPoints = [[1000,400],[845,340],[720,430]];
        const loopVisible = p > 0.10;
        const delayVisible = p > 0.34;
        const amplifierVisible = p > 0.48;
        const dampingVisible = p > 0.60;
        const sideEffectVisible = p > 0.72;
        const interventionVisible = p > 0.84;
        route(loopPoints, palette.line, 4, 1);
        route(balancingPoints, palette.line, 4, 1);
        route(sideEffectPoints, palette.line, 4, 1);
        if (loopVisible) route(loopPoints, palette.route, 8, ease((p - 0.10) / 0.38));
        if (dampingVisible) route(balancingPoints, palette.defense, 7, ease((p - 0.60) / 0.18));
        if (sideEffectVisible) route(sideEffectPoints, palette.tradeoff, 7, ease((p - 0.72) / 0.14));
        if (interventionVisible) route(interventionPoints, palette.attribute, 7, ease((p - 0.84) / 0.12));
        [[causalLabels[0],210,310,palette.route],[causalLabels[1],430,210,palette.damage],[causalLabels[2],645,310,palette.defense],[causalLabels[3],430,430,palette.atlas]].forEach((d, i) => {{
          const active = ease((p - 0.04 - i * 0.10) / 0.18);
          component(d[1] - 78, d[2] - 36, 156, 72, d[0], active > 0.1 ? d[3] : palette.line, "#ffffff");
          if (active > 0.7) circle(d[1], d[2] - 50, 9, d[3], d[3], 2);
        }});
        if (delayVisible) {{
          component(500,150,115,65,"delay",palette.damage,"#ffccd5");
          label(558,198,"effect lags",15,palette.ink);
          line(515,220,600,260,palette.damage,4);
        }}
        if (amplifierVisible) {{
          component(92,475,213,80,"reinforcing loop",palette.route,"#e7e7e7");
          label(198,528,"amplifies pressure",15,palette.ink);
          line(256,528,286,528,palette.route,4);
        }}
        if (dampingVisible) {{
          component(760,255,135,170,"balancing",palette.defense,"#e7e7e7");
          label(828,312,"constraint",15,palette.ink);
          line(790,365,865,365,palette.defense,6);
        }}
        if (sideEffectVisible) {{
          component(920,430,215,85,causalLabels[4],palette.tradeoff,"#ffccd5");
          label(1028,485,"new pressure appears",15,palette.ink);
        }}
        if (interventionVisible) {{
          component(940,205,225,135,causalLabels[5],palette.attribute,"#e7e7e7");
          label(1052,264,"break loop at leverage",15,palette.ink);
          line(982,300,1120,300,palette.attribute,5);
        }}
        const cursor = loopPoints[Math.min(loopPoints.length - 1, Math.floor(ease((p - 0.10) / 0.50) * (loopPoints.length - 1)))];
        if (loopVisible) circle(cursor[0], cursor[1], 12, palette.gold, palette.gold, 2);
        meter(325,515,"pressure",ease((p - 0.18) / 0.52),palette.damage);
        meter(485,515,"delay",ease((p - 0.34) / 0.38),palette.gold);
        meter(645,515,"leverage",ease((p - 0.78) / 0.18),palette.attribute);
        const beats = ["Start with the cause chain, not a generic timeline.", "Delays explain why the effect appears late.", "Reinforcing loops amplify the original pressure.", "Balancing loops constrain runaway behavior.", "Side effects create a second pressure source.", "Intervene at leverage, not at the loudest symptom."];
        const beatIndex = Math.max(0, Math.min(beats.length - 1, Math.floor(p * beats.length)));
        const visibleMechanismCount = [loopVisible, delayVisible, amplifierVisible, dampingVisible, sideEffectVisible, interventionVisible].filter(Boolean).length;
        return {{ videoId, seconds: safeSeconds, beat: beatIndex, sourceFacts: PACKAGE.sourceFacts.length, visualPattern: PACKAGE.visualPattern, causalLabels: sourceCausalLabels, loopVisible, delayVisible, amplifierVisible, dampingVisible, sideEffectVisible, interventionVisible, visibleMechanismCount }};
      }}
      if (PACKAGE.visualPattern === "phase-timeline") {{
        const component = (x, y, w, h, nameText, stroke = palette.line, fill = "#fff") => {{
          el("rect", {{ x, y, width: w, height: h, rx: 0, fill, stroke, "stroke-width": 3 }});
          label(x + w / 2, y + h / 2 + 6, nameText, 18, palette.ink);
        }};
        const compactText = (value, limit = 16) => {{
          const text = String(value ?? "").trim().replace(/\\s+/g, " ");
          return text;
        }};
        const sourcePhaseLabels = PACKAGE.phaseLabels?.length ? PACKAGE.phaseLabels : ["intake","scope","build","review","validate","publish"];
        const phaseLabels = sourcePhaseLabels.map((value) => compactText(value, 16));
        el("rect", {{ x: 55, y: 112, width: 1170, height: 496, rx: 0, fill: "#fff", stroke: "none" }});
        el("rect", {{ x: 88, y: 182, width: 1104, height: 208, rx: 0, fill: "#ffffff", stroke: "none" }});
        el("rect", {{ x: 138, y: 430, width: 977, height: 145, rx: 0, fill: "#ffccd5", stroke: "none" }});
        label(92, 145, "PHASE TIMELINE", 15, palette.muted, "start");
        label(162, 458, "RISK, GATE, AND HANDOFF", 15, palette.tradeoff, "start");
        const phasePoints = [[150,300],[340,300],[530,300],[720,300],[910,300],[1100,300]];
        const progress = ease((p - 0.04) / 0.58);
        const activePhase = Math.min(phasePoints.length - 1, Math.floor(progress * phasePoints.length));
        for (let i = 0; i < phasePoints.length - 1; i++) line(phasePoints[i][0], phasePoints[i][1], phasePoints[i + 1][0], phasePoints[i + 1][1], palette.line, 5);
        for (let i = 0; i < phasePoints.length - 1; i++) if (progress * (phasePoints.length - 1) > i) line(phasePoints[i][0], phasePoints[i][1], phasePoints[i + 1][0], phasePoints[i + 1][1], palette.route, 9);
        const colors = [palette.route,palette.attribute,palette.defense,palette.tradeoff,palette.damage,palette.atlas];
        phasePoints.forEach((point, i) => {{
          const active = ease((p - 0.04 - i * 0.08) / 0.12);
          component(point[0] - 72, point[1] - 36, 144, 72, phaseLabels[i], active > 0.1 ? colors[i] : palette.line, active > 0.95 ? "#e7e7e7" : "#fff");
          if (i === activePhase && p < 0.86) circle(point[0], point[1] - 50, 10, palette.gold, palette.gold, 2);
        }});
        const riskVisible = p > 0.28;
        const gateVisible = p > 0.46;
        const handoffVisible = p > 0.66;
        const finalVisible = p > 0.84;
        if (riskVisible) {{
          line(340,336,340,505,palette.damage,7); line(340,505,530,505,palette.damage,7);
          component(260,482,160,66,"risk scan",palette.damage,"#ffccd5");
          label(340,532,"surface blockers",15,palette.ink);
        }}
        if (gateVisible) {{
          component(640,178,160,60,"decision gate",palette.attribute,"#e7e7e7");
          label(720,226,"pass or revise",15,palette.ink);
          line(720,238,720,264,palette.attribute,4);
        }}
        if (handoffVisible) {{
          line(720,336,790,512,palette.tradeoff,7); line(790,512,910,512,palette.tradeoff,7); line(910,512,910,336,palette.tradeoff,7);
          component(820,482,180,66,"handoff",palette.tradeoff,"#ffccd5");
          label(910,532,"carry constraints",15,palette.ink);
        }}
        if (finalVisible) component(1005,452,87,100,"release notes",palette.atlas,"#e7e7e7");
        const miniMeter = (x, y, nameText, value, color) => {{
          const width = 160;
          const height = 65;
          el("rect", {{ x, y, width, height, rx: 0, fill: grayLevel(3), stroke: palette.line }});
          const filled = Math.max(0, Math.min(width, width * ease(value)));
          if (filled > 0) el("rect", {{ x, y, width: filled, height, rx: 0, fill: color }});
          label(x + width / 2, y + height / 2 + 5, nameText, 15, palette.ink);
        }};
        miniMeter(150,198,"source lock",ease((p - 0.06) / 0.20),palette.route);
        miniMeter(910,198,"quality gate",ease((p - 0.46) / 0.24),palette.defense);
        const tokenX = 150 + Math.min(1, progress) * 950;
        if (progress > 0.08) circle(tokenX, 300, 13, palette.gold, palette.gold, 2);
        const beats = ["Start with a source-locked intake phase.", "Scope and build phases expose risks early.", "A decision gate separates review from validation.", "Handoffs carry constraints into the next phase.", "The release phase publishes only after gates pass."];
        const beatIndex = Math.max(0, Math.min(beats.length - 1, Math.floor(p * beats.length)));
        const visibleMechanismCount = [progress > 0.2, riskVisible, gateVisible, handoffVisible, finalVisible].filter(Boolean).length;
        return {{ videoId, seconds: safeSeconds, beat: beatIndex, sourceFacts: PACKAGE.sourceFacts.length, visualPattern: PACKAGE.visualPattern, phaseLabels: sourcePhaseLabels, activePhase, riskVisible, gateVisible, handoffVisible, finalVisible, visibleMechanismCount }};
      }}
      if (PACKAGE.visualPattern === "metric-dashboard") {{
        const component = (x, y, w, h, nameText, stroke = palette.line, fill = "#fff") => {{
          el("rect", {{ x, y, width: w, height: h, rx: 0, fill, stroke, "stroke-width": 3 }});
          if (masonryRequired) {{
            const rightBandX = x + w - 8;
            el("rect", {{ x, y, width: 8, height: h, rx: 0, fill: stroke === "none" ? grayLevel(4) : stroke, stroke: "none" }});
            el("rect", {{ x: rightBandX, y, width: 8, height: h, rx: 0, fill: grayLevel(4), stroke: "none" }});
          }} else {{
            label(x + w / 2, y + h / 2 + 6, nameText, 18, palette.ink);
          }}
        }};
        const compactText = (value, limit = 18) => {{
          const text = String(value ?? "").trim().replace(/\\s+/g, " ");
          return text;
        }};
        const sourceMetrics = PACKAGE.metricLabels?.length ? PACKAGE.metricLabels : ["north star","input rate","output rate","quality","risk"];
        const sourceThresholds = PACKAGE.thresholdLabels?.length ? PACKAGE.thresholdLabels : ["healthy band","warning line","action line"];
        const metricNames = sourceMetrics.map((value) => compactText(value, 18));
        const thresholdNames = sourceThresholds.map((value) => compactText(value, 18));
        if (!masonryRequired) {{
          el("rect", {{ x: 55, y: 112, width: 800, height: 490, rx: 0, fill: "#fff", stroke: "none" }});
          el("rect", {{ x: 835, y: 112, width: 385, height: 490, rx: 0, fill: "#fff", stroke: "none" }});
          el("rect", {{ x: 55, y: 568, width: 1165, height: 34, rx: 0, fill: grayLevel(5), stroke: "none" }});
          el("rect", {{ x: 800, y: 112, width: 32, height: 456, rx: 0, fill: grayLevel(4), stroke: "none" }});
          el("rect", {{ x: 1192, y: 112, width: 28, height: 456, rx: 0, fill: grayLevel(5), stroke: "none" }});
          label(88, 145, "TREND, THRESHOLDS, AND FORECAST", 15, palette.muted, "start");
          label(865, 145, "DECISION CONTEXT", 15, palette.muted, "start");
        }}
        const chart = {{ x1: 115, y1: 190, x2: 760, y2: 520 }};
        if (masonryRequired) {{
          let metricTileCounter = 0;
          const metricTileAttrs = (mechanismId, extra = {{}}) => ({{
            "data-box-id": `metric-density-tile-${{++metricTileCounter}}`,
            "data-masonry-module": "true",
            "data-zone-boundary": "flush",
            "data-padding-policy": "zero-verified",
            "data-mechanism-id": mechanismId,
            ...extra,
          }});
          const metricTile = (x, y, width, height, fill, mechanismId, extra = {{}}) => {{
            el("rect", {{ x, y, width, height, rx: 0, fill: tonalSurfaceFill(fill, width, height), stroke: "none", ...metricTileAttrs(mechanismId, extra) }});
          }};
          const metricDensityLevel = Math.min(84, Math.floor(ease((p - 0.04) / 0.72) * 85));
          for (let row = 0; row < 6; row++) {{
            for (let col = 0; col < 10; col++) {{
              const index = row * 10 + col;
              const active = index < metricDensityLevel;
              const x = chart.x1 + 26 + col * 42;
              const y = chart.y1 + 26 + row * 28;
              const fill = active ? grayLevel(2 + ((row + col) % 4)) : grayLevel(1);
              metricTile(x, y, 32, 20, fill, "metric-attention-density-grid");
              if (active && (row === col % 6 || index % 17 === 0)) {{
                metricTile(x, y, 6, 20, palette.route, "metric-attention-density-cap", {{ "data-semantic-glyph": "true" }});
              }}
            }}
          }}
          for (let index = 0; index < 14; index++) {{
            const active = index < Math.floor(metricDensityLevel / 4) + 2;
            const x = 86 + index * 28;
            const y = 132 + (index % 3) * 22;
            metricTile(x, y, 22, 16, active ? grayLevel(3 + (index % 3)) : grayLevel(1 + (index % 4)), "metric-token-strip");
            if (active && index % 5 === 0) metricTile(x, y, 6, 16, palette.route, "metric-token-strip-cap", {{ "data-semantic-glyph": "true" }});
          }}
          for (let row = 0; row < 5; row++) {{
            const y = 124 + row * 28;
            const width = 96 + row * 38 + ease((p - 0.20 - row * 0.04) / 0.22) * 92;
            metricTile(892, y, width, 20, grayLevel(2 + (row % 4)), "metric-right-density-bars");
            if (row < Math.floor(ease((p - 0.24) / 0.42) * 6)) metricTile(892, y, 6, 20, palette.route, "metric-right-density-cap", {{ "data-semantic-glyph": "true" }});
          }}
          for (let row = 0; row < 2; row++) {{
            for (let col = 0; col < 30; col++) {{
              const index = row * 30 + col;
              const active = index < Math.floor(metricDensityLevel * 0.72);
              const x = 64 + col * 50;
              const y = 640 + row * 28;
              metricTile(x, y, 40, 18, active ? grayLevel(2 + (index % 4)) : grayLevel(1), "metric-evidence-floor");
              if (active && index % 12 === 0) metricTile(x, y, 6, 18, palette.route, "metric-evidence-floor-cap", {{ "data-semantic-glyph": "true" }});
            }}
          }}
        }}
        for (let i = 0; i < 5; i++) {{
          const y = chart.y1 + i * (chart.y2 - chart.y1) / 4;
          line(chart.x1, y, chart.x2, y, "#cfcfcf", 2);
        }}
        line(chart.x1, chart.y2, chart.x2, chart.y2, palette.line, 3);
        line(chart.x1, chart.y1, chart.x1, chart.y2, palette.line, 3);
        const trendVisible = ease((p - 0.05) / 0.42) > 0.04;
        const thresholdVisible = p > 0.18;
        const anomalyVisible = p > 0.56;
        const forecastVisible = p > 0.72;
        const decisionVisible = p > 0.84;
        const trendProgress = ease((p - 0.05) / 0.42);
        if (thresholdVisible) {{
          el("rect", {{ x: chart.x1, y: 304, width: chart.x2 - chart.x1, height: 84, fill: "#e7e7e7" }});
          line(chart.x1,330,chart.x2,330,palette.defense,4);
          line(chart.x1,395,chart.x2,395,palette.gold,4);
          line(chart.x1,455,chart.x2,455,palette.tradeoff,4);
          if (!masonryRequired) {{
            label(chart.x2 - 8, 320, thresholdNames[0], 14, palette.defense, "end");
            label(chart.x2 - 8, 385, thresholdNames[1], 14, palette.gold, "end");
            label(chart.x2 - 8, 445, thresholdNames[2], 14, palette.tradeoff, "end");
          }}
        }}
        const points = [[145,472],[230,448],[315,438],[400,402],[485,422],[570,366],[655,334],[740,300]];
        const revealed = Math.max(0, Math.min(points.length - 1, Math.floor(trendProgress * (points.length - 1))));
        for (let i = 0; i < revealed; i++) line(points[i][0], points[i][1], points[i + 1][0], points[i + 1][1], palette.route, 4);
        if (trendProgress > 0 && trendProgress < 1) {{
          const i = Math.min(points.length - 2, revealed);
          const ratio = trendProgress * (points.length - 1) - i;
          const a = points[i], b = points[i + 1];
          line(a[0], a[1], a[0] + (b[0] - a[0]) * ratio, a[1] + (b[1] - a[1]) * ratio, palette.route, 4);
        }}
        const activeTrendPoint = Math.max(0, Math.min(points.length - 1, Math.floor(trendProgress * points.length)));
        points.slice(0, activeTrendPoint + 1).forEach((d, i) => circle(d[0], d[1], 7, grayLevel(5), i === 4 ? palette.damage : palette.route, 3));
        if (anomalyVisible) {{
          circle(485,422,30,"none",palette.damage,5);
          component(425,225,170,60,"anomaly",palette.damage,grayLevel(2));
          if (!masonryRequired) label(510,274,metricNames[4],14,palette.ink);
        }}
        if (forecastVisible) {{
          el("polygon", {{ points: "740,300 790,260 790,360", fill: "#e7e7e7", opacity: 0.9 }});
          line(740,300,790,260,palette.atlas,3);
          line(740,300,790,360,palette.atlas,3);
          if (!masonryRequired) label(720,244,"forecast cone",14,palette.atlas);
        }}
        const cards = [
          [865,178,320,82,metricNames[0],"north star",palette.route,0.78 + 0.12 * ease((p - 0.08) / 0.45),0.02],
          [865,278,150,82,metricNames[1],"input",palette.damage,0.55 + 0.25 * ease((p - 0.18) / 0.35),0.18],
          [1035,278,150,82,metricNames[2],"output",palette.defense,0.48 + 0.30 * ease((p - 0.30) / 0.35),0.30],
          [865,378,150,82,metricNames[3],"quality",palette.attribute,0.64 + 0.20 * ease((p - 0.44) / 0.30),0.44],
          [1035,378,150,82,metricNames[4],"risk",palette.tradeoff,0.38 + 0.32 * ease((p - 0.56) / 0.25),0.56],
        ];
        const activeMetric = cards.filter((d) => p + 0.02 >= d[8]).length;
        cards.forEach((d) => {{
          if (p + 0.02 < d[8]) return;
          el("rect", {{ x: d[0], y: d[1], width: d[2], height: d[3], rx: 0, fill: grayLevel(3), stroke: p > 0.16 ? d[6] : palette.line, "stroke-width": 2 }});
          const filled = Math.max(0, Math.min(d[2], d[2] * clamp(d[7])));
          if (filled > 0) {{
            el("rect", {{ x: d[0], y: d[1], width: filled, height: d[3], rx: 0, fill: grayLevel(5) }});
            const capX = d[0] + Math.max(0, filled - 8);
            el("rect", {{ x: capX, y: d[1], width: Math.min(8, filled), height: d[3], rx: 0, fill: d[6], stroke: "none" }});
          }}
          if (!masonryRequired) {{
            label(d[0] + d[2] / 2, d[1] + 32, d[4], 15, palette.ink);
            label(d[0] + d[2] / 2, d[1] + 62, d[5], 13, palette.ink);
          }}
        }});
        if (decisionVisible) {{
          component(865,492,320,72,"decision window open",palette.defense,"#e7e7e7");
          if (!masonryRequired) label(1025,545,"act when forecast crosses threshold",14,palette.ink);
        }}
        const beats = ["Start with the metric that owns the decision.", "Thresholds turn a chart into an operating rule.", "Anomalies need a named risk, not just a red dot.", "Forecasts show where the trend will cross the line.", "The decision appears only after evidence is visible."];
        const beatIndex = Math.max(0, Math.min(beats.length - 1, Math.floor(p * beats.length)));
        const visibleMechanismCount = [trendVisible, thresholdVisible, anomalyVisible, forecastVisible, decisionVisible].filter(Boolean).length;
        return {{ videoId, seconds: safeSeconds, beat: beatIndex, sourceFacts: PACKAGE.sourceFacts.length, visualPattern: PACKAGE.visualPattern, metricLabels: sourceMetrics, thresholdLabels: sourceThresholds, activeMetric, trendVisible, thresholdVisible, anomalyVisible, forecastVisible, decisionVisible, visibleMechanismCount }};
      }}
      if (PACKAGE.visualPattern === "dependency-map") {{
        const compactText = (value, limit = 18) => {{
          const text = String(value ?? "").trim().replace(/\\s+/g, " ");
          return text;
        }};
        const sourceDependencies = PACKAGE.dependencyLabels?.length ? PACKAGE.dependencyLabels : ["source feed","identity","normalizer","policy check","data contract","integration","release gate","fallback path"];
        const sourceClusters = PACKAGE.clusterLabels?.length ? PACKAGE.clusterLabels : ["sources","integration layer","release boundary"];
        const deps = sourceDependencies.map((value) => compactText(value, 18));
        const clusters = sourceClusters.map((value) => compactText(value, 20));
        const component = (x, y, w, h, nameText, stroke = palette.line, fill = "#fff") => {{
          el("rect", {{ x, y, width: w, height: h, rx: 0, fill, stroke, "stroke-width": 3 }});
          label(x + w / 2, y + h / 2 + 6, nameText, 17, palette.ink);
        }};
        const clusterFrames = [
          [55,112,310,480,palette.route],
          [395,112,460,480,palette.defense],
          [885,112,335,480,palette.attribute],
        ];
        const clusterFills = [grayLevel(0), grayLevel(1), grayLevel(2)];
        const clusterLevelFills = [grayLevel(3), grayLevel(4), grayLevel(5)];
        const clusterLevelStrips = [[349,112,16,480], [839,112,16,480], [1204,112,16,480]];
        clusterFrames.forEach(([x, y, w, h, accent], idx) => {{
          el("rect", {{ x, y, width: w, height: h, rx: 0, fill: clusterFills[idx], stroke: "none" }});
          el("rect", {{ x, y, width: w, height: 12, rx: 0, fill: accent }});
          const [stripX, stripY, stripW, stripH] = clusterLevelStrips[idx];
          el("rect", {{ x: stripX, y: stripY, width: stripW, height: stripH, rx: 0, fill: clusterLevelFills[idx], stroke: "none" }});
        }});
        if (masonryRequired) {{
          let dependencyTileCounter = 0;
          const depTileAttrs = (mechanismId, extra = {{}}) => ({{
            "data-box-id": `dependency-density-tile-${{++dependencyTileCounter}}`,
            "data-masonry-module": "true",
            "data-zone-boundary": "flush",
            "data-padding-policy": "zero-verified",
            "data-mechanism-id": mechanismId,
            ...extra,
          }});
          const depTile = (x, y, width, height, fill, mechanismId, extra = {{}}) => {{
            el("rect", {{ x, y, width, height, rx: 0, fill: tonalSurfaceFill(fill, width, height), stroke: "none", ...depTileAttrs(mechanismId, extra) }});
          }};
          const dependencyDensityLevel = Math.max(42, Math.min(72, Math.floor(ease((p - 0.04) / 0.70) * 73)));
          const dependencyCapFill = (index) => index % 3 === 0 ? palette.route : index % 3 === 1 ? palette.attribute : palette.damage;
          for (let row = 0; row < 5; row++) {{
            for (let col = 0; col < 10; col++) {{
              const index = row * 10 + col;
              const active = index < dependencyDensityLevel;
              const x = 92 + col * 28;
              const y = 472 + row * 22;
              depTile(x, y, 20, 16, active ? grayLevel(2 + ((row + col) % 4)) : grayLevel(1), "dependency-source-ledger");
              if (active && index % 7 === 0) depTile(x, y, 6, 16, dependencyCapFill(index), "dependency-source-ledger-cap", {{ "data-semantic-glyph": "true" }});
            }}
          }}
          for (let row = 0; row < 4; row++) {{
            for (let col = 0; col < 8; col++) {{
              const index = row * 8 + col;
              const active = index < Math.floor(dependencyDensityLevel * 0.7);
              const x = 902 + col * 34;
              const y = 342 + row * 26;
              depTile(x, y, 26, 20, active ? grayLevel(2 + ((index + row) % 4)) : grayLevel(1), "dependency-policy-matrix");
              if (active && (row === col % 4 || index % 7 === 0)) depTile(x, y, 6, 20, dependencyCapFill(index + row), "dependency-policy-matrix-cap", {{ "data-semantic-glyph": "true" }});
            }}
          }}
          for (let col = 0; col < 24; col++) {{
            const active = col < Math.floor(dependencyDensityLevel / 2);
            depTile(64 + col * 58, 650, 48, 18, active ? grayLevel(2 + (col % 4)) : grayLevel(1), "dependency-evidence-floor");
            if (active && col % 6 === 0) depTile(64 + col * 58, 650, 6, 18, dependencyCapFill(col), "dependency-evidence-floor-cap", {{ "data-semantic-glyph": "true" }});
          }}
        }}
        label(82, 145, clusters[0].toUpperCase(), 15, palette.muted, "start");
        label(425, 145, clusters[1].toUpperCase(), 15, palette.muted, "start");
        label(915, 145, clusters[2].toUpperCase(), 15, palette.muted, "start");
        const nodes = [
          [170,245,deps[0],palette.route],
          [170,410,deps[1],palette.attribute],
          [470,325,deps[2],palette.route],
          [640,235,deps[3],palette.damage],
          [640,420,deps[4],palette.defense],
          [805,325,deps[5],palette.atlas],
          [1025,270,deps[6],palette.tradeoff],
          [1025,450,deps[7],palette.gold],
        ];
        const edges = [[0,2],[1,2],[2,3],[2,4],[3,5],[4,5],[5,6]];
        const edgeProgress = ease((p - 0.06) / 0.46);
        const riskVisible = p > 0.46;
        const bottleneckVisible = p > 0.58;
        const cutoverVisible = p > 0.72;
        const fallbackVisible = p > 0.84;
        edges.forEach(([left, right]) => line(nodes[left][0], nodes[left][1], nodes[right][0], nodes[right][1], palette.line, 4));
        edges.forEach(([left, right], idx) => {{
          const seg = clamp(edgeProgress * edges.length - idx);
          if (seg <= 0) return;
          const a = nodes[left], b = nodes[right];
          line(a[0], a[1], a[0] + (b[0] - a[0]) * seg, a[1] + (b[1] - a[1]) * seg, palette.route, 7);
        }});
        if (fallbackVisible) {{
          line(nodes[5][0], nodes[5][1], nodes[7][0], nodes[7][1], palette.line, 4);
          const seg = ease((p - 0.84) / 0.12);
          line(nodes[5][0], nodes[5][1], nodes[5][0] + (nodes[7][0] - nodes[5][0]) * seg, nodes[5][1] + (nodes[7][1] - nodes[5][1]) * seg, palette.gold, 7);
        }}
        nodes.forEach((d, idx) => {{
          const active = ease((p - 0.04 - idx * 0.055) / 0.12);
          const r = 18 + 8 * active;
          const fill = "#fff";
          const stroke = active > 0.08 ? d[3] : palette.line;
          if (idx === 3 || idx === 6) {{
            const hr = 34;
            el("polygon", {{ points: `${{d[0]}},${{d[1]-hr}} ${{d[0]+hr}},${{d[1]}} ${{d[0]}},${{d[1]+hr}} ${{d[0]-hr}},${{d[1]}}`, fill: "none", stroke: d[3], "stroke-width": 3 }});
            el("polygon", {{ points: `${{d[0]}},${{d[1]-r-8}} ${{d[0]+r+8}},${{d[1]}} ${{d[0]}},${{d[1]+r+8}} ${{d[0]-r-8}},${{d[1]}}`, fill, stroke, "stroke-width": active > 0.08 ? 4 : 2 }});
          }} else {{
            circle(d[0], d[1], 28, "none", d[3], 3);
            circle(d[0], d[1], r, fill, stroke, active > 0.08 ? 4 : 2);
          }}
          label(d[0], d[1] + r + 22, d[2], 16, active > 0.12 ? palette.ink : palette.muted, "middle", {{ opacity: active > 0.12 ? 1 : 0.58 }});
        }});
        if (riskVisible) {{
          component(520,500,220,65,"risk edge",palette.damage,"#ffccd5");
          label(630,548,"unblocks after policy",14,palette.ink);
          line(640,455,640,500,palette.damage,5);
        }}
        if (bottleneckVisible) {{
          component(705,178,140,60,"bottleneck",palette.tradeoff,"#ffccd5");
          label(775,224,deps[5],14,palette.ink);
          el("circle", {{ cx: 805, cy: 325, r: 30, fill: "none", stroke: palette.tradeoff, "stroke-width": 5 }});
        }}
        if (cutoverVisible) {{
          component(930,170,230,55,"cutover gate",palette.attribute,"#e7e7e7");
          label(1045,214,"wait for upstream proof",14,palette.ink);
          line(930,270,1160,270,palette.attribute,5);
        }}
        if (fallbackVisible) {{
          component(920,502,248,60,"fallback armed",palette.gold,"#e7e7e7");
          label(1044,548,"late safety route explicit",14,palette.ink);
        }}
        const edgeCount = Math.min(edges.length, Math.floor(edgeProgress * edges.length + 0.999));
        const visibleMechanismCount = [edgeCount >= 4, riskVisible, bottleneckVisible, cutoverVisible, fallbackVisible].filter(Boolean).length;
        const beats = ["Map dependencies before promising a release.", "Shared prerequisites converge into integration.", "Risk edges and bottlenecks need a visual path.", "Cutover waits for upstream proof.", "Fallback is a late safety route, not an afterthought."];
        const beatIndex = Math.max(0, Math.min(beats.length - 1, Math.floor(p * beats.length)));
        return {{ videoId, seconds: safeSeconds, beat: beatIndex, sourceFacts: PACKAGE.sourceFacts.length, visualPattern: PACKAGE.visualPattern, dependencyLabels: sourceDependencies, clusterLabels: sourceClusters, edgeCount, riskVisible, bottleneckVisible, cutoverVisible, fallbackVisible, visibleMechanismCount }};
      }}
      if (PACKAGE.visualPattern === "sequence-trace") {{
        const compactText = (value, limit = 18) => {{
          const text = String(value ?? "").trim().replace(/\\s+/g, " ");
          return text;
        }};
        const sourceTraceLabels = PACKAGE.traceLabels?.length ? PACKAGE.traceLabels : ["client request","edge gateway","auth span","inventory span","payment span","database","fallback cache","response"];
        const traceLabels = sourceTraceLabels.map((value) => compactText(value, 18));
        const component = (x, y, w, h, nameText, stroke = palette.line, fill = "#fff") => {{
          el("rect", {{ x, y, width: w, height: h, rx: 0, fill, stroke, "stroke-width": 3 }});
          label(x + w / 2, y + h / 2 + 6, nameText, 17, palette.ink);
        }};
        const laneY = [160,220,280,340,400,460,520];
        const x0 = 245, x1 = 1135;
        el("rect", {{ x: 55, y: 112, width: 1165, height: 473, rx: 0, fill: "#fff", stroke: "none" }});
        label(78,132,"TRACE WATERFALL",15,palette.muted,"start");
        label(960,132,"latency budget",15,palette.muted,"start");
        const laneFills = [grayLevel(0), grayLevel(1), grayLevel(2), grayLevel(3), grayLevel(4), grayLevel(2), grayLevel(5)];
        laneY.forEach((y, idx) => {{
          el("rect", {{ x: x0, y: y - 20, width: x1 - x0, height: 40, rx: 0, fill: laneFills[idx], stroke: "none" }});
        }});
        line(x0,132,x1,132,palette.line,3);
        [0,120,240,360,480].forEach((tick, idx) => {{
          const tx = x0 + idx * (x1 - x0) / 4;
          line(tx,126,tx,138,palette.line,2);
          label(tx,112,`${{tick}}ms`,12,palette.muted);
        }});
        laneY.forEach((y, idx) => {{
          line(x0,y,x1,y,"#cfcfcf",2);
          label(90,y + 6,traceLabels[idx],15,palette.ink,"start");
        }});
        const spans = [
          [0,0.04,0.92,palette.route,"request"],
          [1,0.10,0.30,palette.route,"edge"],
          [2,0.22,0.42,palette.attribute,"auth"],
          [3,0.36,0.62,palette.atlas,"inventory"],
          [4,0.50,0.70,palette.damage,"payment"],
          [5,0.62,0.82,palette.tradeoff,"db wait"],
          [6,0.76,0.92,palette.gold,"fallback"],
        ];
        let activeSpanCount = 0;
        spans.forEach(([lane, start, end, color, nameText]) => {{
          const y = laneY[lane];
          const sx = x0 + start * (x1 - x0);
          const ex = x0 + end * (x1 - x0);
          el("rect", {{ x: sx, y: y - 15, width: ex - sx, height: 30, rx: 0, fill: "#ffffff", stroke: "#cfcfcf" }});
          const progress = ease((p - start) / Math.max(0.01, end - start));
          if (progress > 0) {{
            activeSpanCount += 1;
            el("rect", {{ x: sx, y: y - 15, width: (ex - sx) * progress, height: 30, rx: 0, fill: "#e7e7e7", stroke: color, "stroke-width": 3 }});
          }}
          label((sx + ex) / 2, y + 5, nameText, 15, palette.ink);
        }});
        spans.slice(1, 6).forEach(([lane, start, , color]) => {{
          const hx = x0 + start * (x1 - x0);
          line(hx, laneY[lane - 1] + 18, hx, laneY[lane] - 18, color, 3);
          circle(hx, laneY[lane], 5, color, color, 1);
        }});
        const criticalPathVisible = p > 0.46;
        const latencyBudgetVisible = p > 0.56;
        const retryVisible = p > 0.66;
        const fallbackVisible = p > 0.78;
        const responseVisible = p > 0.88;
        if (criticalPathVisible) {{
          el("rect", {{ x: 505, y: 370, width: 437, height: 117, rx: 0, fill: "#ffccd5", stroke: palette.tradeoff, "stroke-width": 3 }});
          label(724,392,"critical path",15,palette.tradeoff);
          label(724,418,`${{traceLabels[3]}} -> ${{traceLabels[5]}}`,15,palette.ink);
          line(612,360,790,448,palette.tradeoff,4);
        }}
        if (latencyBudgetVisible) {{
          component(930,155,240,67,"budget used",palette.damage,"#ffccd5");
        }}
        if (retryVisible) {{
          component(770,226,260,60,"retry branch",palette.damage,"#ffccd5");
          label(900,271,"slow span triggers retry",14,palette.ink);
          el("path", {{ d: "M720 276 C815 190 980 220 1045 300", fill: "none", stroke: palette.damage, "stroke-width": 5, "stroke-linecap": "butt" }});
        }}
        if (fallbackVisible) {{
          component(785,500,295,68,"fallback cache",palette.gold,"#e7e7e7");
          label(932,548,traceLabels[6],14,palette.ink);
        }}
        if (responseVisible) {{
          component(984,590,206,35,`${{traceLabels[7]}} returned`,palette.defense,"#e7e7e7");
        }}
        const visibleMechanismCount = [activeSpanCount >= 4, criticalPathVisible, latencyBudgetVisible, retryVisible, fallbackVisible, responseVisible].filter(Boolean).length;
        const beats = ["Trace the request before judging the service.", "Each span owns a visible slice of latency.", "The critical path is a route, not a guess.", "Retry and fallback should appear as separate branches.", "The response only lands after the budget story is visible."];
        const beatIndex = Math.max(0, Math.min(beats.length - 1, Math.floor(p * beats.length)));
        el("rect", {{ x: 60, y: 665, width: 1160, height: 42, rx: 0, fill: palette.ink }});
        return {{ videoId, seconds: safeSeconds, beat: beatIndex, sourceFacts: PACKAGE.sourceFacts.length, visualPattern: PACKAGE.visualPattern, traceLabels: sourceTraceLabels, activeSpanCount, criticalPathVisible, latencyBudgetVisible, retryVisible, fallbackVisible, responseVisible, visibleMechanismCount }};
      }}
      if (PACKAGE.visualPattern === "sankey-flow") {{
        const compactText = (value, limit = 18) => {{
          const text = String(value ?? "").trim().replace(/\\s+/g, " ");
          return text;
        }};
        const route = (points, color, width, opacity = 1) => el("polyline", {{
          points: points.map((d) => d.join(",")).join(" "),
          fill: "none",
          stroke: color,
          "stroke-width": width,
          "stroke-linecap": "butt",
          "stroke-linejoin": "miter",
          opacity
        }});
        const flowBodyColor = (color) => {{
          if ([palette.route, palette.attribute, palette.damage, palette.tradeoff].includes(color)) return grayLevel(6);
          return color;
        }};
        const pointOn = (points, progress) => {{
          const safe = Math.max(0, Math.min(1, progress));
          let total = 0;
          const lengths = [];
          for (let i = 0; i < points.length - 1; i++) {{
            const [x1, y1] = points[i];
            const [x2, y2] = points[i + 1];
            const length = Math.hypot(x2 - x1, y2 - y1);
            lengths.push(length);
            total += length;
          }}
          let target = total * safe;
          for (let i = 0; i < lengths.length; i++) {{
            const [x1, y1] = points[i];
            const [x2, y2] = points[i + 1];
            if (target <= lengths[i] || i === lengths.length - 1) {{
              const ratio = lengths[i] ? target / lengths[i] : 0;
              return [x1 + (x2 - x1) * ratio, y1 + (y2 - y1) * ratio];
            }}
            target -= lengths[i];
          }}
          return points[points.length - 1];
        }};
        const node = (x, y, name, stroke, fill = "#fff") => {{
          el("rect", {{ x: x - 62, y: y - 34, width: 124, height: 68, rx: 0, fill, stroke, "stroke-width": 3 }});
          if (masonryRequired) {{
            const leftBandX = x - 62;
            const rightBandX = x + 54;
            el("rect", {{ x: leftBandX, y: y - 34, width: 8, height: 68, rx: 0, fill: stroke, stroke: "none" }});
            el("rect", {{ x: rightBandX, y: y - 34, width: 8, height: 68, rx: 0, fill: grayLevel(4), stroke: "none" }});
          }} else {{
            label(x, y + 5, name, 17, palette.ink);
          }}
        }};
        if (!masonryRequired) {{
          el("rect", {{ x: 55, y: 112, width: 1165, height: 490, rx: 0, fill: "#fff", stroke: "#cfcfcf" }});
          label(88, 145, "SPLIT, LOSS, MERGE, AND OUTPUT", 15, palette.muted, "start");
        }}
        const sourceFlowLabels = PACKAGE.flowLabels?.length ? PACKAGE.flowLabels : ["raw input", "accepted stream", "filtered loss", "transform A", "transform B", "merged value", "bottleneck", "final output"];
        const flowLabels = sourceFlowLabels.map((value) => compactText(value, 18));
        if (masonryRequired) {{
          let sankeyTileCounter = 0;
          const sankeyTileAttrs = (mechanismId, extra = {{}}) => ({{
            "data-box-id": `sankey-density-tile-${{++sankeyTileCounter}}`,
            "data-masonry-module": "true",
            "data-zone-boundary": "flush",
            "data-padding-policy": "zero-verified",
            "data-mechanism-id": mechanismId,
            ...extra,
          }});
          const sankeyTile = (x, y, width, height, fill, mechanismId, extra = {{}}) => {{
            el("rect", {{ x, y, width, height, rx: 0, fill: tonalSurfaceFill(fill, width, height), stroke: "none", ...sankeyTileAttrs(mechanismId, extra) }});
          }};
          const sankeyDensityLevel = Math.min(72, Math.floor(ease((p - 0.08) / 0.70) * 73));
          for (let row = 0; row < 6; row++) {{
            for (let col = 0; col < 12; col++) {{
              const index = row * 12 + col;
              const active = index < sankeyDensityLevel;
              const x = 78 + col * 40;
              const y = 124 + row * 26;
              sankeyTile(x, y, 30, 18, active ? grayLevel(2 + ((row + col) % 4)) : grayLevel(1), "sankey-input-density-grid");
              if (active && index % 11 === 0) sankeyTile(x, y, 6, 18, palette.route, "sankey-input-density-cap", {{ "data-semantic-glyph": "true" }});
            }}
          }}
          for (let col = 0; col < 4; col++) {{
            const x = 918 + col * 74;
            const meterLevel = Math.min(5, Math.floor(ease((p - 0.30 - col * 0.04) / 0.34) * 6));
            sankeyTile(x, 404, 54, 114, grayLevel(2 + col), "sankey-cost-column-shell");
            for (let level = 0; level < 5; level++) {{
              const active = level < meterLevel;
              const y = 492 - level * 18;
              sankeyTile(x + 8, y, 38, 14, active ? grayLevel(5) : grayLevel(3), "sankey-cost-column-segment");
              if (active && level === meterLevel - 1) sankeyTile(x + 8, y, 38, 6, palette.route, "sankey-cost-column-cap", {{ "data-semantic-glyph": "true" }});
            }}
          }}
          for (let row = 0; row < 2; row++) {{
            for (let col = 0; col < 28; col++) {{
              const index = row * 28 + col;
              const active = index < Math.floor(sankeyDensityLevel * 0.75);
              const x = 64 + col * 54;
              const y = 640 + row * 28;
              sankeyTile(x, y, 44, 18, active ? grayLevel(2 + (index % 4)) : grayLevel(1), "sankey-evidence-floor");
              if (active && index % 10 === 0) sankeyTile(x, y, 6, 18, palette.route, "sankey-evidence-floor-cap", {{ "data-semantic-glyph": "true" }});
            }}
          }}
        }}
        const flows = [
          [[[190,320],[265,275],[340,235]], palette.route, 18],
          [[[190,320],[265,390],[340,435]], palette.tradeoff, 12],
          [[[402,235],[485,215],[570,215]], palette.defense, 15],
          [[[402,435],[485,365],[570,365]], palette.attribute, 11],
          [[[632,215],[710,252],[790,300]], palette.route, 14],
          [[[632,365],[710,335],[790,300]], palette.attribute, 11],
          [[[852,300],[950,320],[1048,320]], palette.atlas, 18],
        ];
        const flowProgress = ease((p - 0.06) / 0.62);
        const activeFlowCount = Math.min(flows.length, Math.floor(flowProgress * flows.length + 0.999));
        const splitVisible = p > 0.20;
        const lossVisible = p > 0.34;
        const bottleneckVisible = p > 0.56;
        const mergeVisible = p > 0.66;
        const outputVisible = p > 0.82;
        flows.forEach(([points, color, width]) => route(points, palette.line, Math.max(4, width - 4), 1));
        flows.forEach(([points, color, width], idx) => {{
          const segmentProgress = Math.max(0, Math.min(1, flowProgress * flows.length - idx));
          if (segmentProgress > 0) {{
            route(points, flowBodyColor(color), Math.max(4, width - 6), Math.max(0.28, segmentProgress));
            route(points, color, 3, Math.max(0.35, segmentProgress));
            const token = pointOn(points, segmentProgress);
            circle(token[0], token[1], 8, palette.gold, palette.gold, 2);
          }}
        }});
        [
          [130, 320, flowLabels[0], palette.route, "#e7e7e7"],
          [340, 235, flowLabels[1], palette.defense, "#e7e7e7"],
          [340, 435, flowLabels[2], palette.tradeoff, grayLevel(2)],
          [570, 215, flowLabels[3], palette.route, "#e7e7e7"],
          [570, 365, flowLabels[4], palette.attribute, "#e7e7e7"],
          [790, 300, flowLabels[6], palette.damage, grayLevel(3)],
          [1048, 320, flowLabels[7], palette.atlas, "#e7e7e7"],
        ].forEach((d) => node(d[0], d[1], d[2], d[3], d[4]));
        if (splitVisible) {{
          node(340, 180, "split preserves value", palette.route, "#ffffff");
        }}
        if (lossVisible) {{
          node(340, 530, "loss is explicit", palette.tradeoff, grayLevel(2));
          if (!masonryRequired) label(340, 558, flowLabels[2], 14, palette.ink);
        }}
        if (bottleneckVisible) {{
          node(795, 205, "bottleneck", palette.damage, grayLevel(3));
          if (!masonryRequired) label(795, 234, "limits merged flow", 14, palette.ink);
          el("ellipse", {{ cx: 790, cy: 300, rx: 32, ry: 32, fill: "none", stroke: palette.damage, "stroke-width": 5 }});
        }}
        if (mergeVisible) {{
          node(770, 500, flowLabels[5], palette.defense, "#e7e7e7");
          if (!masonryRequired) label(770, 528, "streams recombine", 14, palette.ink);
        }}
        if (outputVisible) {{
          node(1048, 485, "final output", palette.atlas, "#e7e7e7");
          if (!masonryRequired) label(1048, 514, flowLabels[7], 16, palette.ink);
        }}
        const meter = (x, y, name, value, color) => {{
          const width = 190;
          const height = 66;
          el("rect", {{ x, y, width, height, rx: 0, fill: grayLevel(3), stroke: palette.line }});
          const filled = Math.max(0, Math.min(width, width * ease(value)));
          if (filled > 0) {{
            el("rect", {{ x, y, width: filled, height, rx: 0, fill: grayLevel(5) }});
            const capX = x + Math.max(0, filled - 8);
            el("rect", {{ x: capX, y, width: Math.min(8, filled), height, rx: 0, fill: color, stroke: "none" }});
          }}
          if (!masonryRequired) label(x + width / 2, y + height / 2 + 5, name, 15, palette.ink);
        }};
        meter(86, 500, "input volume", flowProgress, palette.route);
        meter(496, 500, "retained value", ease((p - 0.26) / 0.45), palette.defense);
        meter(930, 182, "output readiness", ease((p - 0.70) / 0.22), palette.atlas);
        const visibleMechanismCount = [activeFlowCount >= 3, splitVisible, lossVisible, bottleneckVisible, mergeVisible, outputVisible].filter(Boolean).length;
        const beats = ["Start with one input stream.", "Split value from loss instead of hiding it.", "Transform streams before judging output.", "Merged flow can still be bottlenecked.", "Output appears only after loss and merge are visible."];
        const beatIndex = Math.max(0, Math.min(beats.length - 1, Math.floor(p * beats.length)));
        return {{ videoId, seconds: safeSeconds, beat: beatIndex, sourceFacts: PACKAGE.sourceFacts.length, visualPattern: PACKAGE.visualPattern, flowLabels: sourceFlowLabels, activeFlowCount, splitVisible, lossVisible, bottleneckVisible, mergeVisible, outputVisible, visibleMechanismCount }};
      }}
      if (PACKAGE.visualPattern === "swimlane-handoff") {{
        const compactText = (value, limit = 16) => {{
          const text = String(value ?? "").trim().replace(/\\s+/g, " ");
          return text;
        }};
        const pluginMotifText = [
          PACKAGE.title,
          PACKAGE.topic,
          ...(PACKAGE.strategyAnchors || []),
          ...(PACKAGE.sourceFacts || []),
          ...(PACKAGE.visualMechanisms || []),
        ].join(" ").toLowerCase();
        const pluginMotifRequested = /harness plugin|plugin_bundle_cube|packaged harness behavior|installable unit|marketplace|allowlist|npm package|opencode runtime|noisy plugin|versioning|team-wide install/.test(pluginMotifText);
        const aiPlatformSignalCount = ["atlassian rovo", "gemini app", "github copilot", "claude desktop", "claude code"].filter((signal) => pluginMotifText.includes(signal)).length;
        const aiSpecificSignalCount = ["atlassian rovo", "gemini app", "claude desktop", "workflow gravity", "home base", "radar chart", "use-case selector"].filter((signal) => pluginMotifText.includes(signal)).length;
        const aiAlternativesMotifRequested = !pluginMotifRequested && (/what ai alternatives we have|ai alternatives/.test(pluginMotifText) || (aiPlatformSignalCount >= 2 && aiSpecificSignalCount >= 2));
        if (masonryRequired && aiAlternativesMotifRequested) {{
          let aiRectCounter = 0;
          const aRect = (x, y, width, height, fill, stroke = "none", strokeWidth = 1, extra = {{}}) => {{
            const hasBoxContract = extra["data-box-id"] || extra["data-fill-for"] || extra["data-zone-id"] || extra["data-masonry-module"];
            const boxContract = hasBoxContract ? {{}} : {{ "data-box-id": `ai-alt-independent-module-${{++aiRectCounter}}` }};
            el("rect", {{ x, y, width, height, rx: 0, fill: tonalSurfaceFill(fill, width, height), stroke, "stroke-width": strokeWidth, "data-zone-boundary": "flush", "data-padding-policy": "zero-verified", ...boxContract, ...extra }});
          }};
          const aLine = (points, stroke, strokeWidth = 4, progress = 1, extra = {{}}) => {{
            if (progress <= 0) return;
            const visible = [];
            const safe = clamp(progress);
            const target = safe * (points.length - 1);
            for (let index = 0; index < points.length - 1; index++) {{
              const local = clamp(target - index);
              if (local <= 0) break;
              const a = points[index], b = points[index + 1];
              if (visible.length === 0) visible.push(a);
              visible.push([a[0] + (b[0] - a[0]) * local, a[1] + (b[1] - a[1]) * local]);
              if (local < 1) break;
            }}
            if (visible.length < 2) return;
            el("polyline", {{ points: visible.map(([x, y]) => `${{x}},${{y}}`).join(" "), fill: "none", stroke, "stroke-width": strokeWidth, "stroke-linecap": "butt", "stroke-linejoin": "miter", ...extra }});
          }};
          const anchoredAttrs = (zoneIndex, anchors, mechanismId, extra = {{}}) => ({{
            ...zoneAttrs(zoneIndex),
            "data-source-anchor": anchors.join("|"),
            "data-source-anchor-json": JSON.stringify(anchors),
            "data-source-anchor-count": String(anchors.length),
            "data-ai-alternatives-motif": mechanismId,
            "data-mechanism-id": mechanismId,
            ...extra,
          }});
          const comparisonAnchors = ["comparison_grid with one strong icon per platform", "four alternatives share one modular comparison surface"];
          const workspaceAnchors = ["Atlassian Rovo anchored to Jira Confluence organizational knowledge workspace", "Gemini App anchored to Google personal productivity workspace", "GitHub Copilot anchored to IDE GitHub coding harness workspace", "Claude Desktop Code anchored to desktop terminal research coding workspace"];
          const fitAnchors = ["shared radar chart for knowledge personal productivity coding extensibility budgetability", "one axis turns into four use-case quadrants"];
          const costAnchors = ["credit_meter relabeled for Rovo credits Gemini subscription Copilot AI credits Claude subscription API"];
          const selectorAnchors = ["Choose by workflow gravity final use-case selector", "guardrails permissions observability wrap the selected workflow home"];

          const comparisonGridVisible = p > 0.03;
          const platformHomeBaseCount = Math.min(4, Math.floor(ease((p - 0.08) / 0.30) * 5));
          const rovoWorkspaceVisible = platformHomeBaseCount >= 1;
          const geminiWorkspaceVisible = platformHomeBaseCount >= 2;
          const copilotWorkspaceVisible = platformHomeBaseCount >= 3;
          const claudeWorkspaceVisible = platformHomeBaseCount >= 4;
          const radarAxisCount = Math.min(5, Math.floor(ease((p - 0.28) / 0.30) * 6));
          const quadrantMapVisible = p > 0.48;
          const costMeterCount = Math.min(4, Math.floor(ease((p - 0.28) / 0.58) * 5));
          const costMeterLevel = Math.min(4, Math.floor(ease((p - 0.30) / 0.56) * 5));
          const workflowSelectorVisible = p > 0.68;
          const selectedWorkflowPathVisible = p > 0.78;
          const guardrailWrapVisible = p > 0.82;
          const observabilityWrapVisible = p > 0.86;

          [
            [0, comparisonAnchors, "ai-comparison-trace", [[84, 92], [352, 92], [448, 148]]],
            [1, workspaceAnchors, "ai-workspace-trace", [[404, 344], [712, 344], [872, 252]]],
            [2, fitAnchors, "ai-fit-trace", [[944, 104], [1144, 180], [1228, 228]]],
            [3, costAnchors, "ai-cost-trace", [[96, 616], [540, 616], [796, 542]]],
            [4, selectorAnchors, "ai-selector-trace", [[916, 636], [1276, 636], [1420, 560]]],
          ].forEach(([zoneIndex, anchors, traceId, points]) => {{
            aLine(points, grayLevel(5), 2, 1, anchoredAttrs(zoneIndex, anchors, traceId, {{ "data-transition-type": "circuit-signal-trace", "data-transition-id": traceId, "data-baseline-trace": "true" }}));
          }});

          const gridX = 80;
          const gridY = 108;
          const columnW = 92;
          const rowH = 56;
          for (let col = 0; col < 4; col++) {{
            for (let row = 0; row < 4; row++) {{
              let fill = grayLevel(1 + ((row + col) % 5));
              if (col < platformHomeBaseCount && row === 0) fill = grayLevel(5);
              if (col < platformHomeBaseCount && row === 3) fill = grayLevel(3 + (col % 3));
              aRect(gridX + col * columnW, gridY + row * rowH, columnW, rowH, fill, grayLevel(5), 1, anchoredAttrs(0, comparisonAnchors, "comparison_grid", {{ "data-masonry-module": "true", "data-transition-type": "masonry-construction", "data-transition-id": "ai-alternatives-comparison-grid" }}));
              const stripeFill = col < platformHomeBaseCount && row === 3 && p > 0.58 ? palette.route : grayLevel(5);
              aRect(gridX + col * columnW, gridY + row * rowH, 8, rowH, stripeFill, "none", 1, anchoredAttrs(0, comparisonAnchors, "platform-state-stripe", {{ "data-masonry-module": "true" }}));
            }}
          }}
          aRect(gridX, gridY, columnW * 4, rowH * 4, "none", grayLevel(5), 2, anchoredAttrs(0, comparisonAnchors, "comparison_grid-frame"));

          const homeX = 520;
          const homeY = 100;
          const homes = [
            [homeX, homeY, 168, 132, "rovo-workspace-home"],
            [homeX + 168, homeY, 184, 132, "gemini-workspace-home"],
            [homeX, homeY + 132, 168, 148, "copilot-workspace-home"],
            [homeX + 168, homeY + 132, 184, 148, "claude-workspace-home"],
          ];
          const workspaceSignature = (index, x, y, width, height, visible, id) => {{
            const attrs = (suffix, extra = {{}}) => anchoredAttrs(1, workspaceAnchors, `${{id}}-${{suffix}}`, {{ "data-masonry-module": "true", "data-transition-type": "tile-morph", "data-transition-id": "ai-workspace-home-bases", ...extra }});
            if (index === 0) {{
              aRect(x, y, 24, height, grayLevel(5), "none", 1, attrs("knowledge-spine"));
              aRect(x + 24, y, width - 24, 36, grayLevel(3), grayLevel(5), 1, attrs("suite-band"));
              for (let row = 0; row < 3; row++) {{
                const bandY = y + 36 + row * 32;
                aRect(x + 24, bandY, 72, 32, grayLevel(1 + row), grayLevel(5), 1, attrs(`knowledge-cell-a-${{row}}`));
                aRect(x + 96, bandY, width - 96, 32, grayLevel(2 + row), grayLevel(5), 1, attrs(`knowledge-cell-b-${{row}}`));
              }}
              aRect(x + 24, y + height - 8, (width - 24) * ease((p - 0.16) / 0.30), 8, visible ? palette.route : grayLevel(4), "none", 1, attrs("state-edge", {{ "data-semantic-glyph": "true" }}));
            }} else if (index === 1) {{
              aRect(x, y, width / 2, height / 2, grayLevel(1), grayLevel(5), 1, attrs("quadrant-a"));
              aRect(x + width / 2, y, width / 2, height / 2, grayLevel(3), grayLevel(5), 1, attrs("quadrant-b"));
              aRect(x, y + height / 2, width / 2, height / 2, grayLevel(4), grayLevel(5), 1, attrs("quadrant-c"));
              aRect(x + width / 2, y + height / 2, width / 2, height / 2, grayLevel(2), grayLevel(5), 1, attrs("quadrant-d"));
              aRect(x + width / 2 - 8, y, 16, height, grayLevel(5), "none", 1, attrs("cross-vertical"));
              aRect(x, y + height / 2 - 8, width, 16, grayLevel(5), "none", 1, attrs("cross-horizontal"));
              if (visible && p > 0.34) aRect(x + width - 12, y, 12, height, palette.route, "none", 1, attrs("state-edge", {{ "data-semantic-glyph": "true" }}));
            }} else if (index === 2) {{
              aRect(x, y, 36, height, grayLevel(5), "none", 1, attrs("repo-spine"));
              aRect(x + 36, y, width - 36, 24, grayLevel(3), grayLevel(5), 1, attrs("ide-toolbar"));
              for (let row = 0; row < 5; row++) {{
                const rowY = y + 24 + row * ((height - 24) / 5);
                aRect(x + 36, rowY, width - 36, (height - 24) / 5, grayLevel(1 + ((row + 1) % 5)), grayLevel(5), 1, attrs(`code-lane-${{row}}`));
                if (visible && [1, 3].includes(row)) aRect(x + 36, rowY, (width - 36) * ease((p - 0.32) / 0.32), 8, palette.route, "none", 1, attrs(`active-code-lane-${{row}}`, {{ "data-semantic-glyph": "true" }}));
              }}
              aLine([[x + 36, y + height - 28], [x + 88, y + height - 56], [x + 136, y + height - 24]], palette.route, 4, ease((p - 0.36) / 0.26), anchoredAttrs(1, workspaceAnchors, `${{id}}-branch-route`, {{ "data-transition-type": "flow-token-route", "data-transition-id": "copilot-branch-route" }}));
            }} else {{
              aRect(x, y, width, 48, grayLevel(5), grayLevel(6), 1, attrs("terminal-band"));
              for (let row = 0; row < 3; row++) {{
                aRect(x, y + 48 + row * 28, width * (0.64 + row * 0.10), 28, grayLevel(2 + row), grayLevel(5), 1, attrs(`command-row-${{row}}`));
              }}
              aRect(x + width / 2, y + 48, width / 2, height - 48, grayLevel(1), grayLevel(5), 1, attrs("research-pane"));
              aLine([[x + 112, y + 92], [x + 152, y + 76], [x + 172, y + 112], [x + 132, y + 140], [x + 96, y + 124], [x + 112, y + 92]], palette.route, 4, ease((p - 0.42) / 0.28), anchoredAttrs(1, workspaceAnchors, `${{id}}-loop-route`, {{ "data-transition-type": "circuit-signal-trace", "data-transition-id": "claude-workspace-loop" }}));
            }}
          }};
          homes.forEach(([x, y, width, height, id], index) => {{
            const visible = index < platformHomeBaseCount;
            workspaceSignature(index, x, y, width, height, visible, id);
            const start = [gridX + columnW * index + columnW, gridY + rowH * 2];
            const end = [x, y + height / 2];
            aLine([start, [start[0] + 56, start[1]], end], palette.route, 4, ease((p - 0.18 - index * 0.04) / 0.18), {{ "data-transition-type": "flow-token-route", "data-transition-id": "ai-platform-homebase-route", "data-preserved-geometry-id": "comparison_grid" }});
          }});

          const radarCx = 1000;
          const radarCy = 238;
          for (let index = 0; index < 5; index++) {{
            const angle = -1.5708 + index * 1.2566;
            const endX = radarCx + Math.round((132 * Math.cos(angle)) / 4) * 4;
            const endY = radarCy + Math.round((108 * Math.sin(angle)) / 4) * 4;
            aLine([[radarCx, radarCy], [endX, endY]], grayLevel(5), 3, 1, anchoredAttrs(2, fitAnchors, "fit-radar-axis", {{ "data-transition-type": "circuit-signal-trace", "data-transition-id": "ai-fit-radar-axis" }}));
            aRect(endX - 20, endY - 16, 40, 32, index < radarAxisCount ? grayLevel(5) : grayLevel(3), grayLevel(5), 1, anchoredAttrs(2, fitAnchors, "fit-radar-axis-node", {{ "data-masonry-module": "true" }}));
          }}
          if (radarAxisCount >= 5) {{
            const radarPoints = [[radarCx, radarCy - 84], [radarCx + 100, radarCy - 24], [radarCx + 68, radarCy + 80], [radarCx - 68, radarCy + 76], [radarCx - 108, radarCy - 20], [radarCx, radarCy - 84]];
            aLine(radarPoints, palette.route, 4, ease((p - 0.44) / 0.16), anchoredAttrs(2, fitAnchors, "radar-fit-polygon", {{ "data-transition-type": "surface-wipe", "data-transition-id": "ai-radar-fit-polygon" }}));
          }}
          const quadX = 1220;
          const quadY = 116;
          for (let row = 0; row < 2; row++) {{
            for (let col = 0; col < 2; col++) {{
              const index = row * 2 + col;
              const fill = quadrantMapVisible ? grayLevel(2 + index) : grayLevel(1 + index);
              aRect(quadX + col * 144, quadY + row * 112, 144, 112, fill, grayLevel(5), 1, anchoredAttrs(2, fitAnchors, "use-case-quadrant-map", {{ "data-masonry-module": "true" }}));
              if (quadrantMapVisible && index === 2) aRect(quadX + col * 144, quadY + row * 112, 8, 112, palette.route, "none", 1, anchoredAttrs(2, fitAnchors, "use-case-selected-edge", {{ "data-masonry-module": "true", "data-semantic-glyph": "true" }}));
            }}
          }}
          aRect(quadX, quadY + 112, 288, 8, grayLevel(5), "none", 1, anchoredAttrs(2, fitAnchors, "quadrant-crossbar", {{ "data-masonry-module": "true" }}));
          aRect(quadX + 144, quadY, 8, 224, grayLevel(5), "none", 1, anchoredAttrs(2, fitAnchors, "quadrant-crossbar", {{ "data-masonry-module": "true" }}));

          const meterX = 80;
          const meterY = 420;
          for (let index = 0; index < 4; index++) {{
            const x = meterX + index * 176;
            const boxId = `ai-cost-meter-${{index}}`;
            aRect(x, meterY, 152, 52, grayLevel(3), grayLevel(5), 1, anchoredAttrs(3, costAnchors, "credit_meter", {{ "data-box-id": boxId }}));
            const filledWidth = 152 * (index < costMeterCount ? costMeterLevel / 4 : 0);
            aRect(x, meterY, filledWidth, 52, grayLevel(5), "none", 1, anchoredAttrs(3, costAnchors, "credit_meter-fill", {{ "data-fill-for": boxId, "data-fill-axis": "x-progress" }}));
            if (index < costMeterCount && costMeterLevel >= 3) aRect(x + Math.max(0, filledWidth - 8), meterY, 8, 52, palette.route, "none", 1, anchoredAttrs(3, costAnchors, "credit-meter-state-cap", {{ "data-masonry-module": "true", "data-semantic-glyph": "true" }}));
            aRect(x, meterY + 52, 152, 28, grayLevel(index < costMeterCount ? 5 : 3), "none", 1, anchoredAttrs(3, costAnchors, "credit-meter-bottom-band", {{ "data-masonry-module": "true" }}));
          }}

          const selectorX = 920;
          const selectorY = 480;
          for (let row = 0; row < 3; row++) {{
            for (let col = 0; col < 4; col++) {{
              const index = row * 4 + col;
              let fill = grayLevel(2 + ((row + col) % 4));
              if (workflowSelectorVisible && [1, 6, 10].includes(index)) fill = grayLevel(5);
              if (workflowSelectorVisible && [3, 11].includes(index)) fill = grayLevel(4);
              aRect(selectorX + col * 76, selectorY + row * 48, 68, 40, fill, grayLevel(5), 1, anchoredAttrs(4, selectorAnchors, "workflow-gravity-selector", {{ "data-masonry-module": "true" }}));
              if (workflowSelectorVisible && [1, 6, 10].includes(index)) aRect(selectorX + col * 76, selectorY + row * 48, 8, 40, palette.route, "none", 1, anchoredAttrs(4, selectorAnchors, "workflow-gravity-selected-edge", {{ "data-masonry-module": "true", "data-semantic-glyph": "true" }}));
            }}
          }}
          aLine([[selectorX + 38, selectorY + 20], [selectorX + 190, selectorY + 68], [homeX + 260, homeY + 198]], palette.route, 5, selectedWorkflowPathVisible ? ease((p - 0.78) / 0.16) : 0, {{ "data-transition-type": "flow-token-route", "data-transition-id": "selected-workflow-gravity-path", "data-preserved-geometry-id": "workflow-gravity-selector" }});
          [[442, "guardrail-permission-wrap"], [494, "guardrail-permission-wrap"], [546, "observability-wrap"]].forEach(([y, id], row) => {{
            const visible = row < 2 ? guardrailWrapVisible : observabilityWrapVisible;
            aRect(1260, y, 292, 52, grayLevel(2 + row), grayLevel(6), 1, anchoredAttrs(4, selectorAnchors, id, {{ "data-masonry-module": "true" }}));
            if (visible) aRect(1260, y, 8, 52, palette.route, "none", 1, anchoredAttrs(4, selectorAnchors, `${{id}}-state-edge`, {{ "data-masonry-module": "true", "data-semantic-glyph": "true" }}));
          }});

          for (let row = 0; row < 3; row++) {{
            for (let col = 0; col < 24; col++) {{
              const index = row * 24 + col;
              const fill = grayLevel(2 + ((index + row) % 4));
              aRect(64 + col * 64, 628 + row * 24, 52, 20, fill, "none", 1, anchoredAttrs(index % 5, [...comparisonAnchors, ...workspaceAnchors, ...fitAnchors, ...costAnchors, ...selectorAnchors], "ai-alternatives-evidence-floor", {{ "data-masonry-module": "true" }}));
              if (index <= Math.floor(ease((p - 0.10) / 0.70) * 55) && index % 9 === 0) aRect(64 + col * 64, 628 + row * 24, 8, 20, palette.route, "none", 1, anchoredAttrs(index % 5, [...comparisonAnchors, ...workspaceAnchors, ...fitAnchors, ...costAnchors, ...selectorAnchors], "ai-alternatives-evidence-state-edge", {{ "data-masonry-module": "true", "data-semantic-glyph": "true" }}));
            }}
          }}

          const visibleMechanismCount = [comparisonGridVisible, platformHomeBaseCount >= 4, radarAxisCount >= 5, quadrantMapVisible, costMeterCount >= 4, costMeterLevel >= 4, workflowSelectorVisible, selectedWorkflowPathVisible, guardrailWrapVisible, observabilityWrapVisible].filter(Boolean).length;
          const beatIndex = Math.max(0, Math.min(4, Math.floor(p * 5)));
          return withCameraState({{ videoId, seconds: safeSeconds, beat: beatIndex, sourceFacts: PACKAGE.sourceFacts.length, visualPattern: PACKAGE.visualPattern, laneLabels: PACKAGE.laneLabels || [], handoffLabels: PACKAGE.handoffLabels || [], comparisonGridVisible, platformHomeBaseCount, rovoWorkspaceVisible, geminiWorkspaceVisible, copilotWorkspaceVisible, claudeWorkspaceVisible, radarAxisCount, quadrantMapVisible, costMeterCount, costMeterLevel, workflowSelectorVisible, selectedWorkflowPathVisible, guardrailWrapVisible, observabilityWrapVisible, visibleMechanismCount }}, camera);
        }}
        if (masonryRequired && pluginMotifRequested) {{
          let pluginRectCounter = 0;
          const pRect = (x, y, width, height, fill, stroke = "none", strokeWidth = 1, extra = {{}}) => {{
            const hasBoxContract = extra["data-box-id"] || extra["data-fill-for"] || extra["data-zone-id"] || extra["data-masonry-module"];
            const boxContract = hasBoxContract ? {{}} : {{ "data-box-id": `plugin-independent-module-${{++pluginRectCounter}}` }};
            el("rect", {{ x, y, width, height, rx: 0, fill: tonalSurfaceFill(fill, width, height), stroke, "stroke-width": strokeWidth, "data-zone-boundary": "flush", "data-padding-policy": "zero-verified", ...boxContract, ...extra }});
          }};
          const pLine = (points, stroke, strokeWidth = 4, progress = 1, extra = {{}}) => {{
            if (progress <= 0) return;
            const visible = [];
            const safe = clamp(progress);
            const target = safe * (points.length - 1);
            for (let index = 0; index < points.length - 1; index++) {{
              const local = clamp(target - index);
              if (local <= 0) break;
              const a = points[index], b = points[index + 1];
              if (visible.length === 0) visible.push(a);
              visible.push([a[0] + (b[0] - a[0]) * local, a[1] + (b[1] - a[1]) * local]);
              if (local < 1) break;
            }}
            if (visible.length < 2) return;
            el("polyline", {{ points: visible.map(([x, y]) => `${{x}},${{y}}`).join(" "), fill: "none", stroke, "stroke-width": strokeWidth, "stroke-linecap": "butt", "stroke-linejoin": "miter", ...extra }});
          }};
          const anchoredAttrs = (zoneIndex, anchors, mechanismId, extra = {{}}) => ({{
            ...zoneAttrs(zoneIndex),
            "data-source-anchor": anchors.join("|"),
            "data-source-anchor-json": JSON.stringify(anchors),
            "data-source-anchor-count": String(anchors.length),
            "data-plugin-motif": mechanismId,
            "data-mechanism-id": mechanismId,
            ...extra,
          }});
          const pluginBundleCubeVisible = p > 0.03;
          const bundleBlockCount = Math.min(9, Math.floor(ease((p - 0.03) / 0.24) * 10));
          const bundleOpenedVisible = p > 0.18;
          const bundleModuleCount = Math.min(5, Math.floor(ease((p - 0.22) / 0.24) * 6));
          const githubManifestCardVisible = p > 0.32;
          const claudeMarketplaceGateVisible = p > 0.42;
          const opencodeNpmRuntimeDropVisible = p > 0.52;
          const providerSurfaceCount = [githubManifestCardVisible, claudeMarketplaceGateVisible, opencodeNpmRuntimeDropVisible].filter(Boolean).length;
          const teamInstallFanoutVisible = p > 0.60;
          const installFanoutCount = Math.min(6, Math.floor(ease((p - 0.60) / 0.22) * 7));
          const versionUpgradeVisible = p > 0.66;
          const versionLevel = Math.min(4, Math.floor(ease((p - 0.66) / 0.22) * 5));
          const governanceGateVisible = p > 0.56;
          const goodBadPluginSplitVisible = p > 0.72;
          const noisyPluginRiskVisible = p > 0.66;
          const noisyToolCount = Math.min(6, Math.floor(ease((p - 0.64) / 0.32) * 7));
          const costMeterLevel = Math.min(4, Math.floor(ease((p - 0.64) / 0.32) * 5));
          const packageInstallVisible = p > 0.84;
          const packagedBehaviorStampVisible = p > 0.86;

          const bundleAnchors = ["plugin_bundle_cube assembles from smaller installable blocks", "Plugin = packaged harness behavior final package-install stamp"];
          const moduleAnchors = ["detachable runtime modules reveal skills hooks MCP config agent-profile and tools"];
          const providerAnchors = ["GitHub plugin manifest card with agents skills hooks and MCP configuration", "Claude marketplace lane with allowlist governance gate", "OpenCode npm package drops into runtime event surface"];
          const governanceAnchors = ["team-wide install fanout standardizes approved behavior", "versioning and upgrade arrows govern the same plugin pack"];
          const riskAnchors = ["good plugin versus noisy plugin split exposes cost and context risk", "flow-tokens circuit-signal-traces masonry-wall risk-bowtie dependency-map"];

          [
            [0, bundleAnchors, "plugin-baseline-bundle-trace", [[80, 96], [312, 96], [420, 132]]],
            [1, moduleAnchors, "plugin-baseline-module-trace", [[360, 324], [740, 324], [820, 252]]],
            [2, providerAnchors, "plugin-baseline-provider-trace", [[820, 636], [1144, 636], [1216, 596]]],
            [3, governanceAnchors, "plugin-baseline-governance-trace", [[1184, 420], [1500, 420], [1576, 468]]],
          ].forEach(([zoneIndex, anchors, traceId, points]) => {{
            pLine(points, grayLevel(5), 2, 1, anchoredAttrs(zoneIndex, anchors, traceId, {{ "data-transition-type": "circuit-signal-trace", "data-transition-id": traceId, "data-baseline-trace": "true" }}));
          }});

          const bundleX = 112;
          const bundleY = 128;
          for (let index = 0; index < 9; index++) {{
            const col = index % 3;
            const row = Math.floor(index / 3);
            const entry = 1 - ease((p - 0.03 - index * 0.018) / 0.12);
            const x = bundleX + col * 64 - 72 * Math.max(0, entry);
            const y = bundleY + row * 56 + (index % 2 ? 40 : -40) * Math.max(0, entry);
            let fill = index < bundleBlockCount && [0, 4, 8].includes(index) ? palette.route : grayLevel(2 + (index % 4));
            if (index < bundleBlockCount && index === 5) fill = palette.attribute;
            pRect(x, y, 56, 48, fill, grayLevel(5), 1, anchoredAttrs(0, bundleAnchors, "plugin_bundle_cube", {{ "data-transition-type": "masonry-construction", "data-transition-id": "plugin-bundle-assembly", "data-transition-phase": index < bundleBlockCount ? "fitted" : "entering" }}));
            pRect(x, y, 10, 48, grayLevel(5), "none", 1, anchoredAttrs(0, bundleAnchors, "plugin_bundle_cube-edge"));
            pRect(x + 18, y + 16, 26, 8, grayLevel(1 + (index % 4)), "none", 1, anchoredAttrs(0, bundleAnchors, "plugin_bundle_cube-mark"));
          }}
          pRect(104, 120, 208, 184, "none", pluginBundleCubeVisible ? palette.route : grayLevel(5), pluginBundleCubeVisible ? 4 : 1, anchoredAttrs(0, bundleAnchors, "plugin_bundle_cube-frame"));
          pLine([[312, 212], [420, 212], [468, 220]], palette.route, 6, ease((p - 0.18) / 0.16), {{ "data-transition-type": "flow-token-route", "data-transition-id": "bundle-to-open-pack", "data-preserved-geometry-id": "plugin_bundle_cube" }});

          pRect(468, 112, 272, 184, grayLevel(1), grayLevel(5), 1, anchoredAttrs(1, moduleAnchors, "detachable_runtime_modules"));
          pRect(468 - 52 * ease((p - 0.18) / 0.18), 112, 52, 184, bundleOpenedVisible ? palette.route : grayLevel(3), grayLevel(5), 1, anchoredAttrs(1, moduleAnchors, "bundle-open-left", {{ "data-transition-type": "tile-morph", "data-transition-id": "bundle-opens" }}));
          pRect(688 + 52 * ease((p - 0.18) / 0.18), 112, 52, 184, grayLevel(5), grayLevel(6), 1, anchoredAttrs(1, moduleAnchors, "bundle-open-right", {{ "data-transition-type": "tile-morph", "data-transition-id": "bundle-opens" }}));
          [[500, 140, 64, 52], [580, 140, 84, 52], [500, 208, 72, 52], [592, 208, 72, 52], [676, 172, 44, 80]].forEach(([x, y, width, height], index) => {{
            let fill = index < bundleModuleCount && [0, 3].includes(index) ? palette.route : index < bundleModuleCount && index === 4 ? palette.attribute : grayLevel(2 + (index % 4));
            pRect(x, y, width, height, fill, grayLevel(5), 1, anchoredAttrs(1, moduleAnchors, "detachable_runtime_modules", {{ "data-transition-type": "tile-morph", "data-transition-id": "bundle-module-reveal" }}));
            pRect(x, y, 8, height, grayLevel(5), "none", 1, anchoredAttrs(1, moduleAnchors, "detachable-module-edge"));
            pRect(x + 16, y + 16, Math.max(16, width - 32), 8, grayLevel(1 + (index % 4)), "none", 1, anchoredAttrs(1, moduleAnchors, "detachable-module-mark"));
          }});

          const providerX = 880;
          [108, 284, 460].forEach((y, surfaceIndex) => {{
            pRect(providerX, y, 264, 132, grayLevel(1 + surfaceIndex), grayLevel(5), 1, anchoredAttrs(2, providerAnchors, "provider_package_surfaces"));
            const edgeFill = [palette.route, palette.damage, palette.attribute][surfaceIndex];
            pRect(providerX, y, 16, 132, providerSurfaceCount > surfaceIndex ? edgeFill : grayLevel(5), "none", 1, anchoredAttrs(2, providerAnchors, "provider-surface-edge"));
          }});
          for (let row = 0; row < 5; row++) {{
            const width = 172 - row * 18;
            const fill = githubManifestCardVisible && [1, 3].includes(row) ? palette.route : grayLevel(2 + (row % 4));
            pRect(providerX + 40, 132 + row * 18, width, 12, fill, "none", 1, anchoredAttrs(2, [providerAnchors[0]], "github_manifest_card"));
            pRect(providerX + 224, 130 + row * 18, 20, 16, grayLevel(githubManifestCardVisible && [1, 3].includes(row) ? 5 : 3), "none", 1, anchoredAttrs(2, [providerAnchors[0]], "github_manifest_check"));
          }}
          const gateClose = ease((p - 0.42) / 0.20);
          pRect(providerX + 42, 318, 148, 44, grayLevel(2), grayLevel(5), 1, anchoredAttrs(2, [providerAnchors[1]], "claude_marketplace_lane"));
          pRect(providerX + 208, 300, 28, 96, claudeMarketplaceGateVisible ? palette.damage : grayLevel(4), grayLevel(6), 1, anchoredAttrs(2, [providerAnchors[1]], "claude_allowlist_gate"));
          pRect(providerX + 42, 318, 166 * gateClose, 12, palette.attribute, "none", 1, anchoredAttrs(2, [providerAnchors[1]], "marketplace_allowlist_wipe", {{ "data-transition-type": "surface-wipe", "data-transition-id": "plugin-allowlist-gate" }}));
          pRect(providerX + 42, 350, 166 * gateClose, 12, palette.attribute, "none", 1, anchoredAttrs(2, [providerAnchors[1]], "marketplace_allowlist_wipe", {{ "data-transition-type": "surface-wipe", "data-transition-id": "plugin-allowlist-gate" }}));
          const drop = ease((p - 0.52) / 0.22);
          pRect(providerX + 70, 420 + 92 * drop, 76, 52, opencodeNpmRuntimeDropVisible ? palette.route : grayLevel(3), grayLevel(5), 1, anchoredAttrs(2, [providerAnchors[2]], "opencode_npm_package_drop", {{ "data-transition-type": "flow-token-route", "data-transition-id": "npm-package-drop" }}));
          pRect(providerX + 48, 538, 184, 42, grayLevel(3), grayLevel(5), 1, anchoredAttrs(2, [providerAnchors[2]], "opencode_runtime_slot"));
          pRect(providerX + 48, 538, 184 * drop, 42, palette.attribute, "none", 1, anchoredAttrs(2, [providerAnchors[2]], "opencode_runtime_fill"));

          const govX = 1220;
          const govY = 116;
          pRect(govX, govY, 128, 112, teamInstallFanoutVisible ? palette.route : grayLevel(3), grayLevel(6), 2, anchoredAttrs(3, governanceAnchors, "team_install_versioning"));
          for (let index = 0; index < 6; index++) {{
            const x = govX + 204 + (index % 3) * 88;
            const y = govY + Math.floor(index / 3) * 88;
            const fill = index < installFanoutCount ? palette.route : grayLevel(2 + (index % 4));
            pRect(x, y, 56, 48, fill, grayLevel(5), 1, anchoredAttrs(3, [governanceAnchors[0]], "team_install_fanout"));
            pLine([[govX + 128, govY + 56], [x, y + 24]], index < installFanoutCount ? palette.route : grayLevel(5), 3, ease((p - 0.60 - index * 0.02) / 0.12), {{ "data-transition-type": "flow-token-route", "data-transition-id": "team-install-fanout" }});
          }}
          for (let index = 0; index < 4; index++) {{
            const y = govY + 228 + index * 42;
            const fill = index < versionLevel ? palette.attribute : grayLevel(2 + index);
            pRect(govX, y, 220, 26, fill, grayLevel(5), 1, anchoredAttrs(3, [governanceAnchors[1]], "versioning_upgrade_arrows"));
            pLine([[govX + 236, y + 13], [govX + 300, y + 13]], fill, 4, ease((p - 0.66 - index * 0.035) / 0.12), {{ "data-transition-type": "circuit-signal-trace", "data-transition-id": "plugin-version-upgrade" }});
          }}
          pRect(govX + 324, govY + 220, 36, 210, governanceGateVisible ? palette.damage : grayLevel(4), grayLevel(6), 1, anchoredAttrs(3, governanceAnchors, "governance_gate"));
          for (let slot = 0; slot < 5; slot++) {{
            pRect(govX + 332, govY + 238 + slot * 36, 20, 24, slot < versionLevel ? palette.route : grayLevel(2 + slot), "none", 1, anchoredAttrs(3, governanceAnchors, "governance_gate_state"));
          }}

          const splitX = 1216;
          const splitY = 468;
          pRect(splitX, splitY, 148, 132, grayLevel(2), grayLevel(5), 1, anchoredAttrs(4, riskAnchors, "good_bad_plugin_split"));
          pRect(splitX + 188, splitY, 148, 132, goodBadPluginSplitVisible ? "#ffccd5" : grayLevel(2), goodBadPluginSplitVisible ? palette.damage : grayLevel(5), 1, anchoredAttrs(4, riskAnchors, "noisy_plugin_risk"));
          for (let index = 0; index < 5; index++) {{
            pRect(splitX + 20, splitY + 20 + index * 20, 78 - index * 8, 10, goodBadPluginSplitVisible && index < 3 ? palette.route : grayLevel(3 + (index % 3)), "none", 1, anchoredAttrs(4, [riskAnchors[0]], "efficient-defaults-lane"));
          }}
          for (let row = 0; row < 3; row++) {{
            for (let col = 0; col < 3; col++) {{
              const index = row * 3 + col;
              const fill = index < noisyToolCount ? palette.damage : grayLevel(2 + (index % 4));
              pRect(splitX + 208 + col * 36, splitY + 18 + row * 32, 28, 24, fill, "none", 1, anchoredAttrs(4, [riskAnchors[0]], "noisy-tool-spread"));
            }}
          }}
          pRect(splitX + 20, splitY + 152, 316, 36, grayLevel(3), grayLevel(5), 1, anchoredAttrs(4, riskAnchors, "cost-meter"));
          pRect(splitX + 20, splitY + 152, 316 * (costMeterLevel / 4), 36, costMeterLevel >= 3 ? palette.damage : palette.attribute, "none", 1, anchoredAttrs(4, riskAnchors, "cost-meter-fill"));

          if (packageInstallVisible) {{
            pRect(420, 556, 180, 64, grayLevel(5), grayLevel(6), 1, anchoredAttrs(0, bundleAnchors, "packaged_behavior_stamp"));
            for (let index = 0; index < 4; index++) {{
              pRect(420 + index * 45, 556, 45, 64, [0, 2].includes(index) ? palette.route : grayLevel(2 + index), grayLevel(6), 1, anchoredAttrs(0, bundleAnchors, "packaged_behavior_stamp-state"));
            }}
            pLine([[600, 588], [712, 588], [776, 540], [860, 540]], palette.route, 7, ease((p - 0.84) / 0.14), {{ "data-transition-type": "flow-token-route", "data-transition-id": "package-install-reuse" }});
            pRect(860, 508, 172, 72, grayLevel(1), palette.route, 3, anchoredAttrs(0, bundleAnchors, "package_install_runtime"));
          }}
          for (let row = 0; row < 2; row++) {{
            for (let col = 0; col < 24; col++) {{
              const index = row * 24 + col;
              let fill = index <= Math.floor(ease((p - 0.18) / 0.58) * 42) && index % 8 === 0 ? palette.route : grayLevel(2 + (index % 4));
              if (index % 13 === 0 && p > 0.62) fill = palette.attribute;
              if (index % 17 === 0 && p > 0.74) fill = palette.damage;
              pRect(64 + col * 64, 652 + row * 24, 52, 16, fill, "none", 1, anchoredAttrs(index % 5, [...bundleAnchors, ...moduleAnchors, ...providerAnchors, ...governanceAnchors, ...riskAnchors], "plugin-evidence-floor"));
            }}
          }}
          const visibleMechanismCount = [pluginBundleCubeVisible, bundleOpenedVisible, providerSurfaceCount >= 3, teamInstallFanoutVisible, versionUpgradeVisible, governanceGateVisible, goodBadPluginSplitVisible, noisyPluginRiskVisible, packageInstallVisible, packagedBehaviorStampVisible].filter(Boolean).length;
          const beatIndex = Math.max(0, Math.min(4, Math.floor(p * 5)));
          return withCameraState({{ videoId, seconds: safeSeconds, beat: beatIndex, sourceFacts: PACKAGE.sourceFacts.length, visualPattern: PACKAGE.visualPattern, laneLabels: PACKAGE.laneLabels || [], handoffLabels: PACKAGE.handoffLabels || [], pluginBundleCubeVisible, bundleBlockCount, bundleOpenedVisible, bundleModuleCount, githubManifestCardVisible, claudeMarketplaceGateVisible, opencodeNpmRuntimeDropVisible, providerSurfaceCount, teamInstallFanoutVisible, installFanoutCount, versionUpgradeVisible, versionLevel, governanceGateVisible, goodBadPluginSplitVisible, noisyPluginRiskVisible, noisyToolCount, costMeterLevel, packageInstallVisible, packagedBehaviorStampVisible, visibleMechanismCount }}, camera);
        }}
        const sourceLaneLabels = PACKAGE.laneLabels?.length ? PACKAGE.laneLabels : ["requester", "intake", "review", "delivery"];
        const sourceHandoffLabels = PACKAGE.handoffLabels?.length ? PACKAGE.handoffLabels : ["request", "triage", "analysis", "approval", "rework", "escalation", "release", "complete"];
        const laneLabels = sourceLaneLabels.map((value) => compactText(value, 18));
        const handoffLabels = sourceHandoffLabels.map((value) => compactText(value, 15));
        el("rect", {{ x: 36, y: 116, width: 1208, height: 478, rx: 0, fill: "#fff", stroke: "none", "stroke-width": 2, "data-masonry-module": "true", "data-box-id": "swimlane-generic-base" }});
        el("rect", {{ x: 36, y: 116, width: 1208, height: 478, rx: 0, fill: "#fff", stroke: "none", "data-fill-for": "swimlane-generic-base", "data-fill-axis": "full-module" }});
        const laneY = [150, 265, 380, 495];
        const laneColors = ["#e7e7e7", "#e7e7e7", "#e7e7e7", "#e7e7e7"];
        const laneStrokes = [palette.route, palette.defense, palette.attribute, palette.atlas];
        el("rect", {{ x: 36, y: 116, width: 40, height: 478, rx: 0, fill: grayLevel(5), stroke: "none", "data-masonry-module": "true" }});
        laneY.forEach((y, idx) => {{
          el("rect", {{ x: 64, y: y - 38, width: 1152, height: 76, rx: 0, fill: laneColors[idx], stroke: "none", "data-masonry-module": "true" }});
          el("rect", {{ x: 1192, y: y - 38, width: 24, height: 76, rx: 0, fill: grayLevel(idx + 2), stroke: "none", "data-masonry-module": "true" }});
          label(92, y + 5, laneLabels[idx], 16, laneStrokes[idx], "start");
          line(170, y - 36, 170, y + 36, "#cfcfcf", 2);
        }});
        const positions = [
          [230, laneY[0], 0],
          [365, laneY[1], 1],
          [505, laneY[1], 1],
          [645, laneY[2], 2],
          [505, laneY[1] + 70, 1],
          [785, laneY[2], 2],
          [935, laneY[3], 3],
          [1085, laneY[3], 3],
        ];
        const handoffProgress = ease((p - 0.06) / 0.58);
        const activeHandoffCount = Math.min(positions.length, Math.floor(handoffProgress * positions.length + 0.999));
        const slaVisible = p > 0.24;
        const reworkVisible = p > 0.40;
        const approvalVisible = p > 0.52;
        const escalationVisible = p > 0.67;
        const completeVisible = p > 0.82;
        const polyline = (points, stroke, width = 4) => {{
          el("polyline", {{ points: points.map((d) => d.join(",")).join(" "), fill: "none", stroke, "stroke-width": width, "stroke-linecap": "butt", "stroke-linejoin": "miter" }});
        }};
        [[0, 1], [1, 2], [2, 3], [3, 6], [6, 7]].forEach(([start, end]) => {{
          const active = activeHandoffCount > end;
          const [x1, y1] = positions[start];
          const [x2, y2] = positions[end];
          polyline([[x1 + 54, y1], [(x1 + x2) / 2, y1], [(x1 + x2) / 2, y2], [x2 - 54, y2]], active ? palette.route : palette.line, active ? 5 : 3);
        }});
        const node = (x, y, labelValue, stroke, active) => {{
          el("rect", {{ x: x - 56, y: y - 28, width: 112, height: 56, rx: 0, fill: active ? "#fff" : "#e7e7e7", stroke: active ? stroke : "#cfcfcf", "stroke-width": active ? 3 : 2, "data-masonry-module": "true" }});
          label(x, y + 5, labelValue, 14, palette.ink);
          if (active) el("circle", {{ cx: x - 54, cy: y - 26, r: 8, fill: stroke }});
        }};
        positions.forEach(([x, y, lane], idx) => node(x, y, handoffLabels[idx], laneStrokes[lane], idx < activeHandoffCount));
        if (reworkVisible) {{
          polyline([[645, laneY[2] + 38], [610, laneY[2] + 92], [505, laneY[1] + 104], [505, laneY[1] + 40]], palette.tradeoff, 6);
          el("rect", {{ x: 418, y: laneY[1] + 88, width: 174, height: 54, rx: 0, fill: "#ffccd5", stroke: palette.tradeoff, "stroke-width": 3, "data-masonry-module": "true" }});
          label(505, laneY[1] + 120, "rework loop", 16, palette.tradeoff);
        }}
        if (slaVisible) {{
          const width = 272;
          const height = 70;
          const filled = Math.max(0, Math.min(width, width * ease((p - 0.20) / 0.34)));
          el("rect", {{ x: 884, y: 142, width, height, rx: 0, fill: grayLevel(3), stroke: palette.line, "data-masonry-module": "true" }});
          if (filled > 0) el("rect", {{ x: 884, y: 142, width: filled, height, rx: 0, fill: palette.damage }});
          label(884 + width / 2, 142 + height / 2 + 5, "SLA pressure", 15, palette.ink);
          el("rect", {{ x: 720, y: 130, width: 132, height: 52, rx: 0, fill: "#ffccd5", stroke: palette.damage, "stroke-width": 3, "data-masonry-module": "true" }});
          label(786, 162, "SLA gate", 16, palette.damage);
        }}
        if (approvalVisible) {{
          el("polygon", {{ points: "645,326 692,380 645,434 598,380", fill: "#ffccd5", stroke: palette.damage, "stroke-width": 4 }});
          label(645, 386, "approval", 16, palette.damage);
        }}
        if (escalationVisible) {{
          polyline([[785, laneY[2] - 38], [820, laneY[1] - 54], [950, laneY[1] - 54], [1010, laneY[2] - 20]], palette.tradeoff, 6);
          el("rect", {{ x: 872, y: laneY[1] - 88, width: 183, height: 60, rx: 0, fill: "#ffccd5", stroke: palette.tradeoff, "stroke-width": 3, "data-masonry-module": "true" }});
          label(964, laneY[1] - 52, "escalation path", 16, palette.tradeoff);
        }}
        if (completeVisible) {{
          el("rect", {{ x: 1020, y: 548, width: 174, height: 38, rx: 0, fill: "#e7e7e7", stroke: palette.defense, "stroke-width": 3, "data-masonry-module": "true" }});
          label(1107, 572, "completed handoff", 16, palette.defense);
        }}
        const visibleMechanismCount = [activeHandoffCount >= 4, slaVisible, reworkVisible, approvalVisible, escalationVisible, completeVisible].filter(Boolean).length;
        const beats = ["Start with a named requester and intake lane.", "Each handoff moves across an owner boundary.", "SLA pressure becomes visible before approval.", "Rework and escalation are explicit routes.", "Completion only appears after release ownership is clear."];
        const beatIndex = Math.max(0, Math.min(beats.length - 1, Math.floor(p * beats.length)));
        return {{ videoId, seconds: safeSeconds, beat: beatIndex, sourceFacts: PACKAGE.sourceFacts.length, visualPattern: PACKAGE.visualPattern, laneLabels: sourceLaneLabels, handoffLabels: sourceHandoffLabels, activeHandoffCount, slaVisible, reworkVisible, approvalVisible, escalationVisible, completeVisible, visibleMechanismCount }};
      }}
      if (PACKAGE.visualPattern === "risk-bowtie") {{
        const compactText = (value, limit = 18) => {{
          const text = String(value ?? "").trim().replace(/\\s+/g, " ");
          return text;
        }};
        const sourceThreatLabels = PACKAGE.threatLabels?.length ? PACKAGE.threatLabels : ["threat A", "threat B", "threat C", "threat D"];
        const sourceBarrierLabels = PACKAGE.barrierLabels?.length ? PACKAGE.barrierLabels : ["detect", "validate", "isolate", "contain", "recover", "learn"];
        const sourceConsequenceLabels = PACKAGE.consequenceLabels?.length ? PACKAGE.consequenceLabels : ["impact A", "impact B", "impact C", "impact D"];
        const guardrailMotifText = [
          PACKAGE.title,
          PACKAGE.topic,
          ...(PACKAGE.strategyAnchors || []),
          ...sourceThreatLabels,
          ...sourceBarrierLabels,
          ...sourceConsequenceLabels,
        ].join(" ").toLowerCase();
        const guardrailMotifRequested = /shield_gate|agent_loop_ring|input\\s*\\/\\s*output\\s*\\/\\s*action|model armor|risk_score|human approval|policy matrix|guardrail/.test(guardrailMotifText);
        if (masonryRequired && guardrailMotifRequested) {{
          const gRect = (x, y, width, height, fill, stroke = "none", strokeWidth = 1, extra = {{}}) => {{
            el("rect", {{ x, y, width, height, rx: 0, fill: tonalSurfaceFill(fill, width, height), stroke, "stroke-width": strokeWidth, "data-zone-boundary": "flush", "data-padding-policy": "zero-verified", ...extra }});
          }};
          const gLine = (points, stroke, strokeWidth = 4, progress = 1, extra = {{}}) => {{
            if (progress <= 0) return;
            const safe = clamp(progress);
            const visible = points.map(([x, y]) => [x, y]);
            if (safe < 1 && points.length > 1) {{
              const end = points[Math.max(1, Math.floor((points.length - 1) * safe))];
              visible.splice(Math.max(2, visible.length - 1), visible.length, end);
            }}
            el("polyline", {{ points: visible.map(([x, y]) => `${{x}},${{y}}`).join(" "), fill: "none", stroke, "stroke-width": strokeWidth, "stroke-linecap": "butt", "stroke-linejoin": "miter", ...extra }});
          }};
          const stateProgress = ease((p - 0.04) / 0.78);
          const activeThreatCount = Math.min(4, Math.floor(ease((p - 0.08) / 0.48) * 4 + 0.999));
          const guardrailShieldGateVisible = p > 0.06;
          const inputGateVisible = p > 0.14;
          const outputGateVisible = p > 0.22;
          const actionGateVisible = p > 0.30;
          const promptInspectionActive = p > 0.18;
          const outputInspectionActive = p > 0.26;
          const toolCallInspectionActive = p > 0.34;
          const riskScoreVisible = p > 0.34;
          const riskScoreLevel = Math.min(4, Math.floor(ease((p - 0.34) / 0.34) * 5));
          const policyMatrixVisible = p > 0.42;
          const blockStateActive = p > 0.50;
          const redactStateActive = p > 0.38;
          const routeStateActive = p > 0.46;
          const escalateStateActive = p > 0.58;
          const humanApprovalRequired = p > 0.62;
          const positiveCasePasses = p > 0.72;
          const blockedCaseStops = p > 0.50;
          const secretRiskActive = p > 0.56;
          const destructiveCommandRiskActive = p > 0.62;
          const deployRiskActive = p > 0.66;
          const safetyFrictionBalanceVisible = p > 0.78;
          const preventiveVisible = inputGateVisible && outputGateVisible;
          const topEventVisible = guardrailShieldGateVisible;
          const mitigativeVisible = policyMatrixVisible;
          const consequenceVisible = blockedCaseStops;
          const degradedVisible = secretRiskActive || destructiveCommandRiskActive || deployRiskActive;
          const actionVisible = humanApprovalRequired;

          const loop = [[540,164],[700,164],[784,316],[700,468],[540,468],[456,316],[540,164]];
          loop.slice(0, -1).forEach((point, index) => gLine([point, loop[index + 1]], grayLevel(5), 4, 1, {{ "data-mechanism-id": "agent_loop_ring", "data-semantic-role": "connector" }}));
          gLine(loop, palette.route, 8, ease((p - 0.06) / 0.40), {{ "data-mechanism-id": "agent_loop_ring", "data-semantic-role": "mechanism-mark", "data-source-anchor-json": JSON.stringify(["agent_loop_ring"]) }});
          loop.slice(0, -1).forEach(([x, y], index) => {{
            const loopNodeActive = index <= activeThreatCount + 1 && index % 3 === 0;
            const fill = loopNodeActive ? grayLevel(5) : grayLevel(2 + index % 4);
            gRect(x - 30, y - 28, 60, 56, fill, grayLevel(5), 1, {{ "data-mechanism-id": "agent_loop_ring", "data-semantic-role": "state-mark" }});
            if (loopNodeActive) gRect(x - 30, y - 28, 8, 56, palette.route, "none", 1, {{ "data-mechanism-id": "agent_loop_ring_active_edge", "data-semantic-role": "state-mark" }});
          }});
          gRect(584, 268, 112, 96, grayLevel(1), palette.route, 3, {{ "data-mechanism-id": "agent_core", "data-semantic-role": "mechanism-mark" }});
          for (let row = 0; row < 3; row++) {{
            for (let col = 0; col < 3; col++) {{
              const cellActive = row + col <= activeThreatCount;
              const fill = cellActive ? grayLevel(5) : grayLevel(2 + ((row + col) % 4));
              gRect(604 + col * 26, 288 + row * 22, 18, 14, fill, "none", 1, {{ "data-mechanism-id": "agent_core", "data-semantic-role": "state-mark" }});
              if (cellActive) gRect(604 + col * 26, 288 + row * 22, 5, 14, palette.route, "none", 1, {{ "data-mechanism-id": "agent_core_active_edge", "data-semantic-role": "state-mark" }});
            }}
          }}

          const gateClose = ease((p - 0.08) / 0.22);
          const shieldLeftX = 424 + 56 * (1 - gateClose);
          const shieldRightX = 828 - 56 * (1 - gateClose);
          gRect(shieldLeftX, 116, 28, 408, grayLevel(5), grayLevel(5), 1, {{ "data-mechanism-id": "shield_gate", "data-semantic-role": "mechanism-mark", "data-source-anchor-json": JSON.stringify(["shield_gate around the agent_loop_ring"]) }});
          gRect(shieldRightX, 116, 28, 408, grayLevel(5), grayLevel(5), 1, {{ "data-mechanism-id": "shield_gate", "data-semantic-role": "mechanism-mark" }});
          gRect(shieldLeftX, 116, 8, 408, palette.damage, "none", 1, {{ "data-mechanism-id": "shield_gate_accent", "data-semantic-role": "state-mark" }});
          gRect(shieldRightX + 20, 116, 8, 408, palette.damage, "none", 1, {{ "data-mechanism-id": "shield_gate_accent", "data-semantic-role": "state-mark" }});
          gRect(424, 116, 432 * gateClose, 20, palette.attribute, "none", 1, {{ "data-transition-id": "shield-close", "data-transition-type": "surface-wipe", "data-transition-phase": guardrailShieldGateVisible ? "active" : "entering", "data-preserved-geometry-id": "agent-loop-ring" }});
          gRect(424, 504, 432 * gateClose, 20, palette.attribute, "none", 1, {{ "data-transition-id": "shield-close", "data-transition-type": "surface-wipe", "data-transition-phase": guardrailShieldGateVisible ? "active" : "entering", "data-preserved-geometry-id": "agent-loop-ring" }});

          [[164, inputGateVisible, palette.route, "input_gate"], [292, outputGateVisible, palette.attribute, "output_gate"], [420, actionGateVisible, palette.damage, "action_gate"]].forEach(([y, visible, color, id], index) => {{
            gRect(96, y - 34, 140, 68, grayLevel(1 + index), grayLevel(5), 1, {{ "data-mechanism-id": id, "data-semantic-role": "mechanism-mark" }});
            const gateFill = visible ? grayLevel(5) : grayLevel(3);
            for (let col = 0; col < 4; col++) {{
              const gateCellActive = visible && col <= activeThreatCount;
              const fill = gateCellActive ? grayLevel(5) : grayLevel(2 + (col + index) % 4);
              gRect(112 + col * 28, y - 14, 22, 28, fill, "none", 1, {{ "data-mechanism-id": id, "data-semantic-role": "state-mark" }});
              if (gateCellActive) gRect(112 + col * 28, y - 14, 6, 28, color, "none", 1, {{ "data-mechanism-id": id + "_active_edge", "data-semantic-role": "state-mark" }});
            }}
            gRect(280, y - 46, 44, 92, gateFill, grayLevel(6), 1, {{ "data-mechanism-id": id, "data-semantic-role": "mechanism-mark" }});
            if (visible) gRect(280, y - 46, 8, 92, color, "none", 1, {{ "data-mechanism-id": id + "_active_gate_edge", "data-semantic-role": "state-mark" }});
            gRect(324, y - 10, 120, 20, grayLevel(5), "none", 1, {{ "data-mechanism-id": id, "data-semantic-role": "connector" }});
            if (visible) gLine([[324, y], [452, y], [456, 316]], color, 5, 1, {{ "data-mechanism-id": id, "data-semantic-role": "connector" }});
          }});

          gRect(104, 540, 160, 76, grayLevel(2), grayLevel(5), 1, {{ "data-mechanism-id": "prompt_bubble", "data-semantic-role": "mechanism-mark" }});
          for (let row = 0; row < 3; row++) gRect(120, 554 + row * 18, 92 + row * 18, 8, grayLevel(4), "none", 1, {{ "data-mechanism-id": "prompt_bubble", "data-semantic-role": "state-mark" }});
          gRect(304, 536, 36, 92, promptInspectionActive ? grayLevel(5) : grayLevel(4), grayLevel(6), 1, {{ "data-mechanism-id": "hard_policy_gate", "data-semantic-role": "mechanism-mark" }});
          if (promptInspectionActive) gRect(304, 536, 8, 92, palette.damage, "none", 1, {{ "data-mechanism-id": "hard_policy_gate_accent", "data-semantic-role": "state-mark" }});
          gRect(348, 562, 112, 36, redactStateActive ? grayLevel(5) : grayLevel(3), "none", 1, {{ "data-mechanism-id": "redaction_mask", "data-semantic-role": "state-mark" }});
          if (redactStateActive) gRect(348, 562, 8, 36, palette.route, "none", 1, {{ "data-mechanism-id": "redaction_mask_accent", "data-semantic-role": "state-mark" }});

          for (let row = 0; row < 4; row++) {{
            const y = 128 + row * 58;
            const width = 82 + ease((p - 0.28) / 0.32) * (220 - row * 18);
            const laneBlocked = row % 3 === 0 && blockStateActive;
            const fill = laneBlocked ? grayLevel(5) : grayLevel(2 + row);
            gRect(932, y, width, 34, fill, "none", 1, {{ "data-mechanism-id": "model_armor_filter_lanes", "data-semantic-role": "state-mark" }});
            if (laneBlocked) gRect(932 + Math.max(0, width - 8), y, Math.min(8, width), 34, palette.damage, "none", 1, {{ "data-mechanism-id": "model_armor_filter_lane_cap", "data-semantic-role": "state-mark" }});
            gRect(1168, y, 44, 34, grayLevel(row % 3 === 0 && blockStateActive ? 5 : 3), "none", 1, {{ "data-mechanism-id": "model_armor_filter_lanes", "data-semantic-role": "state-mark" }});
            gLine([[856,316],[904,y + 16],[932,y + 16]], row % 2 === 0 ? palette.route : palette.attribute, 4, ease((p - 0.28) / 0.32), {{ "data-mechanism-id": "model_armor_filter_lanes", "data-semantic-role": "connector" }});
          }}
          gRect(930, 400, 300, 64, grayLevel(3), grayLevel(5), 1, {{ "data-box-id": "guardrail-risk-score", "data-mechanism-id": "risk_score_bar", "data-semantic-role": "mechanism-mark" }});
          const riskWidth = 300 * ease((p - 0.34) / 0.34);
          if (riskScoreVisible) {{
            const riskHigh = riskWidth > 185;
            gRect(930, 400, riskWidth, 64, riskHigh ? grayLevel(5) : grayLevel(4), "none", 1, {{ "data-fill-for": "guardrail-risk-score", "data-fill-axis": "x-progress", "data-mechanism-id": "risk_score_bar", "data-semantic-role": "state-mark" }});
            if (riskWidth > 0) gRect(930 + Math.max(0, riskWidth - 8), 400, Math.min(8, riskWidth), 64, riskHigh ? palette.damage : palette.attribute, "none", 1, {{ "data-mechanism-id": "risk_score_bar_cap", "data-semantic-role": "state-mark" }});
          }}

          for (let row = 0; row < 3; row++) {{
            for (let col = 0; col < 3; col++) {{
              const score = row * 3 + col;
              let fill = grayLevel(2 + (score % 4));
              if (policyMatrixVisible && [2, 4].includes(score)) fill = palette.attribute;
              const matrixBlocked = policyMatrixVisible && [6, 7, 8].includes(score);
              if (matrixBlocked) fill = grayLevel(5);
              gRect(1316 + col * 56, 104 + row * 56, 52, 52, fill, grayLevel(5), 1, {{ "data-mechanism-id": "policy_matrix", "data-semantic-role": "state-mark" }});
              if (matrixBlocked) gRect(1316 + col * 56, 104 + row * 56, 8, 52, palette.damage, "none", 1, {{ "data-mechanism-id": "policy_matrix_blocked_edge", "data-semantic-role": "state-mark" }});
            }}
          }}
          [blockStateActive, redactStateActive, routeStateActive, escalateStateActive].forEach((visible, index) => {{
            const fills = [palette.damage, palette.route, palette.attribute, grayLevel(5)];
            gRect(1272 + index * 92, 312, 76, 58, visible ? grayLevel(5) : grayLevel(2 + index), grayLevel(5), 1, {{ "data-mechanism-id": "policy_outcome_tiles", "data-semantic-role": "state-mark" }});
            if (visible && index < 3) gRect(1272 + index * 92, 312, 8, 58, fills[index], "none", 1, {{ "data-mechanism-id": "policy_outcome_tile_edge", "data-semantic-role": "state-mark" }});
            gRect(1284 + index * 92, 326, 52, 8, grayLevel(1 + index % 4), "none");
            gRect(1284 + index * 92, 346, 52, 8, grayLevel(5), "none");
          }});

          gRect(1280, 424, 224, 150, humanApprovalRequired ? palette.tradeoff : grayLevel(3), grayLevel(6), 2, {{ "data-mechanism-id": "human_approval_modal", "data-semantic-role": "mechanism-mark" }});
          gRect(1304, 448, 176, 20, grayLevel(1), "none");
          gRect(1304, 484, 68, 54, humanApprovalRequired ? grayLevel(5) : grayLevel(2), "none");
          gRect(1392, 484, 64, 54, positiveCasePasses ? palette.route : grayLevel(2), "none");
          [secretRiskActive, destructiveCommandRiskActive, deployRiskActive].forEach((visible, index) => {{
            const x = 1544 + index * 80;
            gRect(x, 432, 64, 72, visible ? grayLevel(5) : grayLevel(2 + index), grayLevel(5), 1, {{ "data-mechanism-id": "protected_action_tile", "data-semantic-role": "state-mark" }});
            if (visible) gRect(x, 432, 8, 72, palette.damage, "none", 1, {{ "data-mechanism-id": "protected_action_tile_risk_edge", "data-semantic-role": "state-mark" }});
            gRect(x + 12, 446, 40, 10, grayLevel(1 + index % 4), "none");
            gRect(x + 12, 470, 40, 10, grayLevel(5), "none");
          }});

          gLine([[940,612],[1096,612],[1248,612]], palette.route, 7, positiveCasePasses ? 1 : 0, {{ "data-mechanism-id": "positive_case_path", "data-semantic-role": "connector" }});
          gLine([[940,652],[1076,652],[1076,628]], palette.damage, 7, blockedCaseStops ? 1 : 0, {{ "data-mechanism-id": "blocked_case_path", "data-semantic-role": "connector" }});
          if (blockedCaseStops) {{
            gRect(1060, 620, 52, 52, grayLevel(5), grayLevel(6), 1, {{ "data-mechanism-id": "block_stop_bar", "data-semantic-role": "state-mark" }});
            gRect(1060, 620, 8, 52, palette.damage, "none", 1, {{ "data-mechanism-id": "block_stop_bar_accent", "data-semantic-role": "state-mark" }});
          }}
          gRect(1492, 612, 240, 12, grayLevel(5), "none", 1, {{ "data-mechanism-id": "safety_friction_scale", "data-semantic-role": "mechanism-mark" }});
          gRect(1604, 558, 16, 108, grayLevel(6), "none", 1, {{ "data-mechanism-id": "safety_friction_scale", "data-semantic-role": "mechanism-mark" }});
          const leftH = 46 + 30 * ease((p - 0.76) / 0.16);
          const rightH = 74 - 24 * ease((p - 0.76) / 0.16);
          gRect(1512, 612 - leftH, 76, leftH, grayLevel(5), "none", 1, {{ "data-mechanism-id": "safety_friction_scale", "data-semantic-role": "state-mark" }});
          gRect(1512, 612 - leftH, 8, leftH, palette.route, "none", 1, {{ "data-mechanism-id": "safety_friction_scale_pass_edge", "data-semantic-role": "state-mark" }});
          gRect(1636, 612 - rightH, 76, rightH, grayLevel(5), "none", 1, {{ "data-mechanism-id": "safety_friction_scale", "data-semantic-role": "state-mark" }});
          gRect(1636, 612 - rightH, 8, rightH, palette.damage, "none", 1, {{ "data-mechanism-id": "safety_friction_scale_stop_edge", "data-semantic-role": "state-mark" }});

          const visibleMechanismCount = [
            guardrailShieldGateVisible,
            inputGateVisible && outputGateVisible && actionGateVisible,
            riskScoreVisible,
            policyMatrixVisible,
            blockStateActive && redactStateActive && routeStateActive,
            humanApprovalRequired,
            safetyFrictionBalanceVisible,
          ].filter(Boolean).length;
          const beatIndex = Math.max(0, Math.min(4, Math.floor(p * 5)));
          return {{ videoId, seconds: safeSeconds, beat: beatIndex, sourceFacts: PACKAGE.sourceFacts.length, visualPattern: PACKAGE.visualPattern, threatLabels: sourceThreatLabels, barrierLabels: sourceBarrierLabels, consequenceLabels: sourceConsequenceLabels, activeThreatCount, preventiveVisible, topEventVisible, mitigativeVisible, consequenceVisible, degradedVisible, actionVisible, guardrailShieldGateVisible, inputGateVisible, outputGateVisible, actionGateVisible, promptInspectionActive, outputInspectionActive, toolCallInspectionActive, riskScoreVisible, riskScoreLevel, policyMatrixVisible, blockStateActive, redactStateActive, routeStateActive, escalateStateActive, humanApprovalRequired, positiveCasePasses, blockedCaseStops, secretRiskActive, destructiveCommandRiskActive, deployRiskActive, safetyFrictionBalanceVisible, visibleMechanismCount }};
        }}
        const threatLabels = sourceThreatLabels.map((value) => compactText(value, 18));
        const barrierLabels = sourceBarrierLabels.map((value) => compactText(value, 18));
        const consequenceLabels = sourceConsequenceLabels.map((value) => compactText(value, 18));
        const threatPoints = [[142, 170], [142, 270], [142, 370], [142, 470]];
        const preventivePoints = [[380, 225], [380, 330], [380, 435]];
        const mitigativePoints = [[900, 225], [900, 330], [900, 435]];
        const consequencePoints = [[1130, 170], [1130, 270], [1130, 370], [1130, 470]];
        const topEvent = [640, 330];
        const activeThreatCount = Math.min(threatPoints.length, Math.floor(ease((p - 0.05) / 0.45) * threatPoints.length + 0.999));
        const preventiveVisible = p > 0.18;
        const topEventVisible = p > 0.32;
        const mitigativeVisible = p > 0.48;
        const consequenceVisible = p > 0.62;
        const degradedVisible = p > 0.74;
        const actionVisible = p > 0.84;
        const polyline = (points, stroke, width = 4) => {{
          el("polyline", {{ points: points.map((d) => d.join(",")).join(" "), fill: "none", stroke, "stroke-width": width, "stroke-linecap": "butt", "stroke-linejoin": "miter" }});
        }};
        const box = (x, y, w, h, labelValue, stroke, fill, size = 15) => {{
          el("rect", {{ x: x - w / 2, y: y - h / 2, width: w, height: h, rx: 0, fill, stroke, "stroke-width": 3 }});
          label(x, y + 5, labelValue, size, palette.ink);
        }};
        el("rect", {{ x: 44, y: 112, width: 1192, height: 480, rx: 0, fill: "#fff", stroke: "#cfcfcf", "stroke-width": 2 }});
        label(120, 138, "THREATS", 14, palette.muted);
        label(380, 138, "PREVENT", 14, palette.muted);
        label(640, 138, "TOP EVENT", 14, palette.muted);
        label(900, 138, "MITIGATE", 14, palette.muted);
        label(1130, 138, "CONSEQUENCES", 14, palette.muted);
        threatPoints.forEach((point) => preventivePoints.forEach((barrier) => polyline([point, barrier], palette.line, 2)));
        preventivePoints.forEach((barrier) => polyline([barrier, topEvent], palette.line, 3));
        mitigativePoints.forEach((barrier) => polyline([topEvent, barrier], palette.line, 3));
        mitigativePoints.forEach((barrier) => consequencePoints.forEach((point) => polyline([barrier, point], palette.line, 2)));
        threatPoints.forEach(([x, y], idx) => {{
          const active = idx < activeThreatCount;
          box(x, y, 156, 56, threatLabels[idx], active ? palette.damage : "#ccd6e3", active ? "#ffccd5" : "#e7e7e7", 14);
        }});
        preventivePoints.forEach(([x, y], idx) => box(x, y, 164, 60, barrierLabels[idx], preventiveVisible ? palette.route : "#ccd6e3", preventiveVisible ? "#e7e7e7" : "#e7e7e7", 16));
        if (topEventVisible) {{
          el("polygon", {{ points: "640,260 705,330 640,400 575,330", fill: "#ffccd5", stroke: palette.tradeoff, "stroke-width": 5 }});
          label(640, 336, "top event", 22, palette.tradeoff);
        }} else {{
          el("polygon", {{ points: "640,280 690,330 640,380 590,330", fill: "#e7e7e7", stroke: "#ccd6e3", "stroke-width": 3 }});
        }}
        mitigativePoints.forEach(([x, y], idx) => box(x, y, 164, 60, barrierLabels[idx + 3], mitigativeVisible ? palette.defense : "#ccd6e3", mitigativeVisible ? "#e7e7e7" : "#e7e7e7", 16));
        consequencePoints.forEach(([x, y], idx) => box(x, y, 164, 56, consequenceLabels[idx], consequenceVisible ? palette.damage : "#ccd6e3", consequenceVisible ? "#ffccd5" : "#e7e7e7", 14));
        if (activeThreatCount >= 3) threatPoints.slice(0, activeThreatCount).forEach((point, idx) => polyline([point, preventivePoints[Math.min(idx, 2)]], palette.damage, 5));
        if (preventiveVisible) preventivePoints.forEach((barrier) => polyline([barrier, topEvent], palette.route, 5));
        if (mitigativeVisible) mitigativePoints.forEach((barrier) => polyline([topEvent, barrier], palette.defense, 5));
        if (consequenceVisible) consequencePoints.forEach((point, idx) => polyline([mitigativePoints[Math.min(idx, 2)], point], palette.damage, 4));
        if (degradedVisible) {{
          el("rect", {{ x: 485, y: 475, width: 310, height: 70, rx: 0, fill: "#ffccd5", stroke: palette.damage, "stroke-width": 4 }});
          label(640, 503, "degraded barrier", 16, palette.damage);
          label(640, 526, "control gap stays visible", 14, palette.ink);
        }}
        if (actionVisible) {{
          el("rect", {{ x: 470, y: 176, width: 340, height: 54, rx: 0, fill: "#e7e7e7", stroke: palette.atlas, "stroke-width": 4 }});
          label(640, 208, "action: repair weakest barrier", 16, palette.atlas);
        }}
        const meter = (x, y, name, value, color) => {{
          const width = 205;
          const height = 60;
          el("rect", {{ x, y, width, height, rx: 0, fill: grayLevel(3), stroke: palette.line }});
          const filled = Math.max(0, Math.min(width, width * ease(value)));
          if (filled > 0) el("rect", {{ x, y, width: filled, height, rx: 0, fill: color }});
          label(x + width / 2, y + height / 2 + 5, name, 15, palette.ink);
        }};
        meter(80, 515, "threat pressure", ease((p - 0.06) / 0.42), palette.damage);
        meter(990, 515, "residual risk", 1 - ease((p - 0.58) / 0.32), palette.tradeoff);
        const visibleMechanismCount = [activeThreatCount >= 3, preventiveVisible, topEventVisible, mitigativeVisible, consequenceVisible, degradedVisible, actionVisible].filter(Boolean).length;
        const beats = ["Name the threats before judging controls.", "Preventive barriers sit before the top event.", "Mitigations reduce consequences after the event.", "Degraded barriers keep the control gap visible.", "Action targets the weakest barrier, not the symptom."];
        const beatIndex = Math.max(0, Math.min(beats.length - 1, Math.floor(p * beats.length)));
        return {{ videoId, seconds: safeSeconds, beat: beatIndex, sourceFacts: PACKAGE.sourceFacts.length, visualPattern: PACKAGE.visualPattern, threatLabels: sourceThreatLabels, barrierLabels: sourceBarrierLabels, consequenceLabels: sourceConsequenceLabels, activeThreatCount, preventiveVisible, topEventVisible, mitigativeVisible, consequenceVisible, degradedVisible, actionVisible, visibleMechanismCount }};
      }}
      if (PACKAGE.visualPattern === "scenario-tree") {{
        const compactText = (value, limit = 18) => {{
          const text = String(value ?? "").trim().replace(/\\s+/g, " ");
          return text;
        }};
        const sourceScenarioLabels = PACKAGE.scenarioLabels?.length ? PACKAGE.scenarioLabels : ["decision point", "base case", "upside branch", "downside branch", "steady outcome", "growth outcome", "fallback outcome"];
        const sourceProbabilityLabels = PACKAGE.probabilityLabels?.length ? PACKAGE.probabilityLabels : ["likely", "upside", "downside", "fallback"];
        const scenarioLabels = sourceScenarioLabels.map((value) => compactText(value, 18));
        const probabilityLabels = sourceProbabilityLabels.map((value) => compactText(value, 16));
        const root = [150, 330];
        const branches = [[395, 205], [395, 330], [395, 455]];
        const outcomes = [[690, 165], [690, 265], [690, 395], [690, 505]];
        const decision = [1020, 330];
        const fallback = [1018, 502];
        const activeScenarioCount = Math.min(7, Math.floor(ease((p - 0.05) / 0.55) * 7 + 0.999));
        const probabilityVisible = p > 0.20;
        const riskVisible = p > 0.35;
        const upsideVisible = p > 0.50;
        const decisionVisible = p > 0.64;
        const fallbackVisible = p > 0.76;
        const outcomeVisible = p > 0.86;
        const polyline = (points, stroke, width = 4) => {{
          el("polyline", {{ points: points.map((d) => d.join(",")).join(" "), fill: "none", stroke, "stroke-width": width, "stroke-linecap": "butt", "stroke-linejoin": "miter" }});
        }};
        const node = ([x, y], labelValue, stroke, fill, active = true, width = 176) => {{
          el("rect", {{ x: x - width / 2, y: y - 30, width, height: 60, rx: 0, fill: active ? fill : "#e7e7e7", stroke: active ? stroke : "#ccd6e3", "stroke-width": active ? 3 : 2 }});
          label(x, y + 5, labelValue, 16, palette.ink);
        }};
        el("rect", {{ x: 44, y: 112, width: 1192, height: 480, rx: 0, fill: "#fff", stroke: "#cfcfcf", "stroke-width": 2 }});
        label(150, 138, "DECISION", 14, palette.muted);
        label(395, 138, "SCENARIOS", 14, palette.muted);
        label(690, 138, "OUTCOMES", 14, palette.muted);
        label(1020, 138, "CHOICE", 14, palette.muted);
        node(root, scenarioLabels[0], palette.route, "#e7e7e7", true, 178);
        branches.forEach((point, idx) => {{
          const active = idx + 1 < activeScenarioCount;
          polyline([root, point], active ? palette.route : palette.line, active ? 5 : 3);
          node(point, scenarioLabels[idx + 1], [palette.defense, palette.attribute, palette.damage][idx], ["#e7e7e7", "#e7e7e7", "#ffccd5"][idx], active, 178);
          if (probabilityVisible) {{
            const labelPositions = [[278, 245], [278, 318], [278, 408]];
            const [lx, ly] = labelPositions[idx];
            el("rect", {{ x: lx - 72, y: ly - 17, width: 144, height: 34, rx: 0, fill: "#fff", stroke: "#cfcfcf", "stroke-width": 2 }});
            label(lx, ly + 5, probabilityLabels[idx], 14, palette.ink);
          }}
        }});
        const outcomeLinks = [[branches[0], outcomes[0]], [branches[0], outcomes[1]], [branches[1], outcomes[2]], [branches[2], outcomes[3]]];
        outcomeLinks.forEach(([start, end], idx) => {{
          const active = idx + 4 < activeScenarioCount;
          polyline([start, end], active ? palette.route : palette.line, active ? 5 : 3);
          node(end, scenarioLabels[Math.min(idx + 3, 6)], [palette.defense, palette.route, palette.attribute, palette.damage][idx], ["#e7e7e7", "#e7e7e7", "#e7e7e7", "#ffccd5"][idx], active, 180);
        }});
        if (riskVisible) {{
          el("rect", {{ x: 790, y: 420, width: 155, height: 58, rx: 0, fill: "#ffccd5", stroke: palette.damage, "stroke-width": 3 }});
          label(868, 452, "risk branch", 16, palette.damage);
        }}
        if (upsideVisible) {{
          el("rect", {{ x: 790, y: 184, width: 160, height: 58, rx: 0, fill: "#e7e7e7", stroke: palette.defense, "stroke-width": 3 }});
          label(870, 216, "upside branch", 16, palette.defense);
        }}
        if (decisionVisible) {{
          node(decision, "decision gate", palette.atlas, "#e7e7e7", true, 190);
          outcomes.slice(0, 3).forEach((point) => polyline([point, decision], palette.atlas, 5));
        }}
        if (fallbackVisible) {{
          node(fallback, probabilityLabels[3], palette.gold, "#e7e7e7", true, 190);
          polyline([outcomes[3], fallback], palette.gold, 5);
        }}
        if (outcomeVisible) {{
          el("rect", {{ x: 930, y: 548, width: 268, height: 38, rx: 0, fill: "#e7e7e7", stroke: palette.defense, "stroke-width": 3 }});
          label(1064, 572, "selected outcome is source-aware", 16, palette.defense);
        }}
        const meter = (x, y, name, value, color) => {{
          const width = 220;
          const height = 55;
          el("rect", {{ x, y, width, height, rx: 0, fill: grayLevel(3), stroke: palette.line }});
          const filled = Math.max(0, Math.min(width, width * ease(value)));
          if (filled > 0) el("rect", {{ x, y, width: filled, height, rx: 0, fill: color }});
          label(x + width / 2, y + height / 2 + 5, name, 15, palette.ink);
        }};
        meter(70, 520, "uncertainty", 1 - ease((p - 0.58) / 0.32), palette.damage);
        meter(505, 520, "evidence weight", ease((p - 0.20) / 0.45), palette.route);
        const visibleMechanismCount = [activeScenarioCount >= 4, probabilityVisible, riskVisible, upsideVisible, decisionVisible, fallbackVisible, outcomeVisible].filter(Boolean).length;
        const beats = ["Start with one decision point.", "Branch into base, upside, and downside scenarios.", "Probabilities and evidence weights appear before choice.", "Fallback stays visible as an alternate route.", "Outcome is selected only after branches are visible."];
        const beatIndex = Math.max(0, Math.min(beats.length - 1, Math.floor(p * beats.length)));
        return {{ videoId, seconds: safeSeconds, beat: beatIndex, sourceFacts: PACKAGE.sourceFacts.length, visualPattern: PACKAGE.visualPattern, scenarioLabels: sourceScenarioLabels, probabilityLabels: sourceProbabilityLabels, activeScenarioCount, probabilityVisible, riskVisible, upsideVisible, decisionVisible, fallbackVisible, outcomeVisible, visibleMechanismCount }};
      }}
      if (PACKAGE.visualPattern === "layered-architecture") {{
        const compactText = (value, limit = 24) => {{
          const text = String(value ?? "").trim().replace(/\\s+/g, " ");
          return text;
        }};
        const sourceLayerLabels = PACKAGE.layerLabels?.length ? PACKAGE.layerLabels : ["client","edge/API","application","domain service","data layer","platform"];
        const sourceConcernLabels = PACKAGE.concernLabels?.length ? PACKAGE.concernLabels : ["security policy","failure route","observability","rollout gate"];
        const layerLabels = sourceLayerLabels.map((value) => compactText(value, 30));
        const concernLabels = sourceConcernLabels.map((value) => compactText(value, 28));
        const layerGrayFills = [grayLevel(1), grayLevel(2), grayLevel(3), grayLevel(2), grayLevel(3), grayLevel(4)];
        const layerGhostStrokes = [grayLevel(3), grayLevel(3), grayLevel(4), grayLevel(4), grayLevel(5), grayLevel(5)];
        const activeLayerCount = Math.min(6, Math.floor(ease((p - 0.07) / 0.55) * 6 + 0.999));
        const crossCuttingVisible = p > 0.28;
        const failurePathVisible = p > 0.46;
        const observabilityVisible = p > 0.62;
        const rolloutVisible = p > 0.80;
        const polyline = (points, stroke, width = 4) => {{
          el("polyline", {{ points: points.map((d) => d.join(",")).join(" "), fill: "none", stroke, "stroke-width": width, "stroke-linecap": "butt", "stroke-linejoin": "miter" }});
        }};
        const meter = (x, y, name, value, color) => {{
          const width = 235;
          const height = 58;
          const boxId = `layered-meter-${{String(name).toLowerCase().replace(/[^a-z0-9]+/g, "-")}}`;
          el("rect", {{ x, y, width, height, rx: 0, fill: grayLevel(3), stroke: palette.line, "data-box-id": boxId }});
          const filled = Math.max(0, Math.min(width, width * ease(value)));
          if (filled > 0) el("rect", {{ x, y, width: filled, height, rx: 0, fill: color, "data-fill-for": boxId, "data-fill-axis": "x-progress" }});
          label(x + width / 2, y + height / 2 + 5, name, 15, palette.ink);
        }};
        el("rect", {{ x: 44, y: 112, width: 1192, height: 480, rx: 0, fill: "#fff", stroke: "#cfcfcf", "stroke-width": 2 }});
        label(185, 140, "REQUEST PATH", 14, palette.muted);
        label(562, 140, "LAYERS", 14, palette.muted);
        label(930, 140, "CROSS-CUTTING", 14, palette.muted);
        const layerBoxes = [];
        layerLabels.forEach((textValue, idx) => {{
          const y = 178 + idx * 62;
          const active = idx < activeLayerCount;
          const fill = layerGrayFills[idx % layerGrayFills.length];
          const stroke = idx < 2 ? palette.route : idx < 4 ? palette.defense : palette.atlas;
          const ghostStroke = layerGhostStrokes[idx % layerGhostStrokes.length];
          el("rect", {{ x: 320, y, width: 460, height: 48, rx: 0, fill, stroke: active ? stroke : ghostStroke, "stroke-width": active ? 3 : 2, "data-box-id": `layer-${{idx}}` }});
          label(550, y + 29, textValue, 16, palette.ink);
          layerBoxes.push([320, y, 780, y + 48, stroke]);
        }});
        const pathX = 185;
        layerBoxes.forEach((box, idx) => {{
          const cy = (box[1] + box[3]) / 2;
          const active = idx < activeLayerCount;
          circle(pathX, cy, 18, "#fff", active ? palette.route : "#cfcfcf", active ? 4 : 2);
          if (idx > 0) {{
            const prevY = (layerBoxes[idx - 1][1] + layerBoxes[idx - 1][3]) / 2;
            polyline([[pathX, prevY + 18], [pathX, cy - 18]], active ? palette.route : palette.line, active ? 5 : 3);
          }}
        }});
        if (activeLayerCount) {{
          const idx = Math.min(activeLayerCount - 1, 5);
          const cy = (layerBoxes[idx][1] + layerBoxes[idx][3]) / 2;
          polyline([[203, cy], [320, cy]], palette.route, 5);
        }}
        if (!crossCuttingVisible) {{
          el("rect", {{ x: 840, y: 180, width: 295, height: 58, rx: 0, fill: "#e7e7e7", stroke: "#cfcfcf", "stroke-width": 2 }});
          label(988, 214, "cross-cutting policy", 14, palette.muted);
        }}
        if (crossCuttingVisible) {{
          el("rect", {{ x: 840, y: 180, width: 295, height: 58, rx: 0, fill: "#e7e7e7", stroke: palette.attribute, "stroke-width": 4 }});
          label(988, 214, concernLabels[0], 16, palette.attribute);
          polyline([[838, 210], [782, 210], [782, 500], [838, 500]], palette.attribute, 5);
        }}
        if (!failurePathVisible) {{
          el("rect", {{ x: 838, y: 278, width: 297, height: 60, rx: 0, fill: "#ffccd5", stroke: "#cfcfcf", "stroke-width": 2 }});
          label(986, 312, "failure route", 14, palette.muted);
        }}
        if (failurePathVisible) {{
          el("rect", {{ x: 838, y: 278, width: 297, height: 60, rx: 0, fill: "#ffccd5", stroke: palette.damage, "stroke-width": 4 }});
          label(986, 312, concernLabels[1], 16, palette.damage);
          polyline([[780, 326], [835, 308]], palette.damage, 6);
        }}
        if (!observabilityVisible) {{
          el("rect", {{ x: 838, y: 378, width: 297, height: 60, rx: 0, fill: "#e7e7e7", stroke: "#cfcfcf", "stroke-width": 2 }});
          label(986, 412, "observability", 14, palette.muted);
        }}
        if (observabilityVisible) {{
          el("rect", {{ x: 838, y: 378, width: 297, height: 60, rx: 0, fill: "#e7e7e7", stroke: palette.atlas, "stroke-width": 4 }});
          label(986, 412, concernLabels[2], 16, palette.atlas);
          meter(875, 452, "signal coverage", ease((p - 0.62) / 0.20), palette.atlas);
        }}
        if (!rolloutVisible) {{
          el("rect", {{ x: 838, y: 528, width: 297, height: 46, rx: 0, fill: "#e7e7e7", stroke: "#cfcfcf", "stroke-width": 2 }});
          label(986, 556, "rollout gate", 14, palette.muted);
        }}
        if (rolloutVisible) {{
          el("rect", {{ x: 838, y: 528, width: 297, height: 46, rx: 0, fill: "#e7e7e7", stroke: palette.defense, "stroke-width": 4 }});
          label(986, 556, concernLabels[3], 16, palette.defense);
        }}
        const visibleMechanismCount = [activeLayerCount >= 4, activeLayerCount === 6, crossCuttingVisible, failurePathVisible, observabilityVisible, rolloutVisible].filter(Boolean).length;
        const beats = ["Separate layers before explaining movement.", "The request path should prove which layer owns work.", "Cross-cutting policies span layers without becoming a layer.", "Failure and observability routes stay outside the happy path.", "Rollout appears after the layered contract is visible."];
        const beatIndex = Math.max(0, Math.min(beats.length - 1, Math.floor(p * beats.length)));
        return {{ videoId, seconds: safeSeconds, beat: beatIndex, sourceFacts: PACKAGE.sourceFacts.length, visualPattern: PACKAGE.visualPattern, layerLabels: sourceLayerLabels, concernLabels: sourceConcernLabels, activeLayerCount, crossCuttingVisible, failurePathVisible, observabilityVisible, rolloutVisible, visibleMechanismCount }};
      }}
      if (PACKAGE.visualPattern === "data-lineage") {{
        const compactText = (value, limit = 22) => {{
          const text = String(value ?? "").trim().replace(/\\s+/g, " ");
          return text;
        }};
        const sourceLineageLabels = PACKAGE.lineageLabels?.length ? PACKAGE.lineageLabels : ["raw source","ingest stream","bronze table","silver transform","feature view","consumer surface"];
        const sourceQualityLabels = PACKAGE.qualityLabels?.length ? PACKAGE.qualityLabels : ["schema check","freshness window","drift alert","rollback plan"];
        const lineageLabels = sourceLineageLabels.map((value) => compactText(value, 18));
        const qualityLabels = sourceQualityLabels.map((value) => compactText(value, 18));
        const activeLineageCount = Math.min(6, Math.floor(ease((p - 0.06) / 0.58) * 6 + 0.999));
        const transformVisible = p > 0.24;
        const qualityGateVisible = p > 0.38;
        const driftVisible = p > 0.54;
        const consumerVisible = p > 0.70;
        const rollbackVisible = p > 0.84;
        const polyline = (points, stroke, width = 4) => {{
          el("polyline", {{ points: points.map((d) => d.join(",")).join(" "), fill: "none", stroke, "stroke-width": width, "stroke-linecap": "butt", "stroke-linejoin": "miter" }});
        }};
        const meter = (x, y, name, value, color, width = 162, height = 60) => {{
          el("rect", {{ x, y, width, height, rx: 0, fill: grayLevel(3), stroke: palette.line }});
          const filled = Math.max(0, Math.min(width, width * ease(value)));
          if (filled > 0) el("rect", {{ x, y, width: filled, height, rx: 0, fill: color }});
          label(x + width / 2, y + height / 2 + 5, name, 14, palette.ink);
        }};
        el("rect", {{ x: 44, y: 112, width: 1192, height: 480, rx: 0, fill: "#fff", stroke: "#cfcfcf", "stroke-width": 2 }});
        label(150, 140, "SOURCE", 14, palette.muted);
        label(604, 140, "LINEAGE PATH", 14, palette.muted);
        label(456, 322, "QUALITY GATE", 14, palette.muted);
        label(918, 322, "OPERATIONS", 14, palette.muted);
        const nodeColors = [
          [palette.route, grayLevel(1), grayLevel(3)],
          [palette.route, grayLevel(2), grayLevel(3)],
          [palette.defense, grayLevel(2), grayLevel(4)],
          [palette.defense, grayLevel(3), grayLevel(4)],
          [palette.atlas, grayLevel(3), grayLevel(5)],
          [palette.atlas, grayLevel(4), grayLevel(5)],
        ];
        const nodeBoxes = [];
        lineageLabels.forEach((textValue, idx) => {{
          const x = 82 + idx * 178;
          const active = idx < activeLineageCount;
          const [stroke, fill, ghostStroke] = nodeColors[idx];
          el("rect", {{ x, y: 192, width: 138, height: 78, rx: 0, fill, stroke: active ? stroke : ghostStroke, "stroke-width": active ? 4 : 2 }});
          label(x + 69, 239, textValue, 15, palette.ink);
          nodeBoxes.push([x, 192, x + 138, 270, stroke]);
        }});
        for (let idx = 0; idx < nodeBoxes.length - 1; idx += 1) {{
          const box = nodeBoxes[idx];
          const nextBox = nodeBoxes[idx + 1];
          const activeEdge = idx < Math.max(0, activeLineageCount - 1);
          const y = (box[1] + box[3]) / 2;
          polyline([[box[2], y], [nextBox[0], y]], activeEdge ? palette.route : palette.line, activeEdge ? 6 : 3);
        }}
        if (activeLineageCount) {{
          const box = nodeBoxes[Math.min(activeLineageCount - 1, nodeBoxes.length - 1)];
          circle(box[0] + 69, box[1] - 3, 13, palette.gold, "#fff", 3);
        }}
        if (!transformVisible) {{
          el("rect", {{ x: 414, y: 150, width: 254, height: 28, rx: 0, fill: "#e7e7e7", stroke: "#cfcfcf", "stroke-width": 2 }});
          label(541, 168, "transform rule", 14, palette.muted);
        }}
        if (transformVisible) {{
          el("rect", {{ x: 414, y: 150, width: 254, height: 28, rx: 0, fill: "#e7e7e7", stroke: palette.attribute, "stroke-width": 3 }});
          label(541, 168, "transform rule", 14, palette.attribute);
          polyline([[496,178],[496,192]], palette.attribute, 4);
          polyline([[592,178],[592,192]], palette.attribute, 4);
        }}
        if (!qualityGateVisible) {{
          el("rect", {{ x: 248, y: 342, width: 414, height: 114, rx: 0, fill: grayLevel(1), stroke: "#cfcfcf", "stroke-width": 2 }});
          label(455, 386, "quality checks pending", 16, palette.muted);
        }}
        if (qualityGateVisible) {{
          meter(248, 342, qualityLabels[0], ease((p - 0.38) / 0.18), palette.route, 207, 114);
          meter(455, 342, qualityLabels[1], ease((p - 0.42) / 0.18), palette.defense, 207, 114);
        }}
        if (!driftVisible) {{
          el("rect", {{ x: 724, y: 342, width: 412, height: 52, rx: 0, fill: "#ffccd5", stroke: "#cfcfcf", "stroke-width": 2 }});
          label(930, 372, "drift monitor", 16, palette.muted);
        }}
        if (driftVisible) {{
          el("rect", {{ x: 724, y: 342, width: 412, height: 52, rx: 0, fill: "#ffccd5", stroke: palette.damage, "stroke-width": 4 }});
          label(884, 372, qualityLabels[2], 16, palette.damage);
          polyline([[994,374],[1048,354],[1110,378]], palette.damage, 5);
        }}
        if (!consumerVisible) {{
          el("rect", {{ x: 724, y: 424, width: 412, height: 76, rx: 0, fill: "#e7e7e7", stroke: "#cfcfcf", "stroke-width": 2 }});
          label(930, 466, "consumer contract", 16, palette.muted);
        }}
        if (consumerVisible) {{
          el("rect", {{ x: 724, y: 424, width: 412, height: 76, rx: 0, fill: "#e7e7e7", stroke: palette.atlas, "stroke-width": 4 }});
          label(930, 454, compactText(sourceLineageLabels[sourceLineageLabels.length - 1], 28), 16, palette.atlas);
          label(930, 482, "ready after lineage + checks", 14, palette.muted);
          polyline([[1042,270],[1042,424]], palette.atlas, 5);
        }}
        if (!rollbackVisible) {{
          el("rect", {{ x: 248, y: 500, width: 414, height: 68, rx: 0, fill: "#ffccd5", stroke: "#cfcfcf", "stroke-width": 2 }});
          label(455, 540, "rollback route", 16, palette.muted);
        }}
        if (rollbackVisible) {{
          el("rect", {{ x: 248, y: 500, width: 414, height: 68, rx: 0, fill: "#ffccd5", stroke: palette.tradeoff, "stroke-width": 4 }});
          label(455, 540, compactText(sourceQualityLabels[3], 26), 16, palette.tradeoff);
          polyline([[620,500],[620,480],[260,480],[260,270]], palette.tradeoff, 5);
        }}
        const visibleMechanismCount = [activeLineageCount >= 2, transformVisible, qualityGateVisible, driftVisible, consumerVisible, rollbackVisible].filter(Boolean).length;
        const beats = ["Start with source-to-consumer lineage, not a generic pipeline.", "Transform rules appear before quality is trusted.", "Quality gates separate schema and freshness checks.", "Drift and consumers stay visible outside the transform path.", "Rollback appears only after downstream risk is visible."];
        const beatIndex = Math.max(0, Math.min(beats.length - 1, Math.floor(p * beats.length)));
        return {{ videoId, seconds: safeSeconds, beat: beatIndex, sourceFacts: PACKAGE.sourceFacts.length, visualPattern: PACKAGE.visualPattern, lineageLabels: sourceLineageLabels, qualityLabels: sourceQualityLabels, activeLineageCount, transformVisible, qualityGateVisible, driftVisible, consumerVisible, rollbackVisible, visibleMechanismCount }};
      }}
      if (PACKAGE.visualPattern === "evidence-ladder") {{
        const compactText = (value, limit = 19) => {{
          const text = String(value ?? "").trim().replace(/\\s+/g, " ");
          return text;
        }};
        const sourceClaimLabels = PACKAGE.claimLabels?.length ? PACKAGE.claimLabels : ["working claim","baseline reading","counterclaim","recommendation"];
        const sourceEvidenceLabels = PACKAGE.evidenceLabels?.length ? PACKAGE.evidenceLabels : ["source A","source B","data check","expert review","counterevidence","source gap"];
        const claimLabels = sourceClaimLabels.map((value) => compactText(value, 22));
        const evidenceLabels = sourceEvidenceLabels.map((value) => compactText(value, 19));
        const claimVisible = p > 0.08;
        const activeEvidenceCount = Math.min(6, Math.floor(ease((p - 0.10) / 0.58) * 6 + 0.999));
        const counterEvidenceVisible = p > 0.42;
        const gapVisible = p > 0.56;
        const confidenceVisible = p > 0.68;
        const recommendationVisible = p > 0.82;
        const polyline = (points, stroke, width = 4) => {{
          el("polyline", {{ points: points.map((d) => d.join(",")).join(" "), fill: "none", stroke, "stroke-width": width, "stroke-linecap": "butt", "stroke-linejoin": "miter" }});
        }};
        const meter = (x, y, name, value, color) => {{
          const width = 190;
          const height = 62;
          el("rect", {{ x, y, width, height, rx: 0, fill: grayLevel(3), stroke: palette.line }});
          const filled = Math.max(0, Math.min(width, width * ease(value)));
          if (filled > 0) el("rect", {{ x, y, width: filled, height, rx: 0, fill: color }});
          label(x + width / 2, y + height / 2 + 5, name, 15, palette.ink);
        }};
        el("rect", {{ x: 44, y: 112, width: 1192, height: 480, rx: 0, fill: "#fff", stroke: "none", "stroke-width": 2 }});
        [
          [44, 112, 280, 480, grayLevel(0)],
          [324, 112, 376, 480, grayLevel(1)],
          [700, 112, 280, 480, grayLevel(2)],
          [980, 112, 256, 480, grayLevel(4)],
        ].forEach(([x, y, w, h, fill]) => {{
          el("rect", {{ x, y, width: w, height: h, rx: 0, fill, stroke: "none" }});
        }});
        label(185, 140, "CLAIM", 14, palette.muted);
        label(560, 140, "EVIDENCE LADDER", 14, palette.muted);
        label(845, 140, "COUNTERWEIGHT", 14, palette.muted);
        label(1080, 140, "DECISION", 14, palette.muted);
        el("rect", {{ x: 72, y: 216, width: 228, height: 106, rx: 0, fill: "#e7e7e7", stroke: claimVisible ? palette.route : "#cfcfcf", "stroke-width": claimVisible ? 4 : 2 }});
        label(186, 254, claimLabels[0], 16, palette.ink);
        label(186, 286, claimLabels[1], 14, palette.muted);
        const ladderPoints = [[430,500],[500,420],[570,340],[640,260]];
        for (let i = 0; i < ladderPoints.length - 1; i++) {{
          polyline([ladderPoints[i], ladderPoints[i + 1]], palette.line, 4);
          if (i < Math.min(3, Math.max(0, activeEvidenceCount - 1))) polyline([ladderPoints[i], ladderPoints[i + 1]], palette.route, 7);
        }}
        ladderPoints.forEach(([x, y], idx) => {{
          const active = idx < activeEvidenceCount;
          el("rect", {{ x: x - 86, y: y - 28, width: 172, height: 56, rx: 0, fill: active ? "#ffffff" : "#e7e7e7", stroke: active ? palette.route : "#cfcfcf", "stroke-width": active ? 3 : 2 }});
          label(x, y + 5, evidenceLabels[idx], 14, palette.ink);
        }});
        if (claimVisible) polyline([[300,270],[372,340],ladderPoints[0]], palette.route, 5);
        if (!counterEvidenceVisible) {{
          el("rect", {{ x: 760, y: 260, width: 190, height: 72, rx: 0, fill: "#ffffff", stroke: "#cfcfcf", "stroke-width": 2 }});
          label(855, 302, "counterweight", 14, palette.muted);
        }}
        if (counterEvidenceVisible) {{
          el("rect", {{ x: 760, y: 260, width: 190, height: 72, rx: 0, fill: "#ffccd5", stroke: palette.damage, "stroke-width": 4 }});
          label(855, 292, evidenceLabels[4], 16, palette.damage);
          label(855, 316, claimLabels[2], 14, palette.ink);
          polyline([ladderPoints[2], [720,328], [760,296]], palette.damage, 6);
        }}
        if (!gapVisible) {{
          el("rect", {{ x: 760, y: 425, width: 190, height: 80, rx: 0, fill: "#e7e7e7", stroke: "#cfcfcf", "stroke-width": 2 }});
          label(855, 470, "source gap", 14, palette.muted);
        }}
        if (gapVisible) {{
          el("rect", {{ x: 760, y: 425, width: 190, height: 80, rx: 0, fill: "#e7e7e7", stroke: palette.gold, "stroke-width": 4 }});
          label(855, 458, "source gap", 16, palette.gold);
          label(855, 484, evidenceLabels[5], 14, palette.ink);
          polyline([ladderPoints[0], [700,470], [760,466]], palette.gold, 6);
        }}
        if (!confidenceVisible) {{
          el("rect", {{ x: 1000, y: 228, width: 190, height: 62, rx: 0, fill: "#e7e7e7", stroke: "#cfcfcf", "stroke-width": 2 }});
          label(1095, 264, "confidence", 14, palette.muted);
          el("rect", {{ x: 1000, y: 310, width: 190, height: 62, rx: 0, fill: "#e7e7e7", stroke: "#ffccd5", "stroke-width": 2 }});
          label(1095, 346, "uncertainty", 14, palette.muted);
        }}
        if (confidenceVisible) {{
          meter(1000, 228, "confidence", ease((p - 0.58) / 0.28), palette.defense);
          meter(1000, 310, "uncertainty", 1 - ease((p - 0.58) / 0.28), palette.damage);
        }}
        if (recommendationVisible) {{
          el("rect", {{ x: 990, y: 438, width: 212, height: 82, rx: 0, fill: "#e7e7e7", stroke: palette.defense, "stroke-width": 4 }});
          label(1096, 470, claimLabels[3], 16, palette.defense);
          label(1096, 496, "recommend after evidence", 14, palette.ink);
        }}
        const visibleMechanismCount = [claimVisible, activeEvidenceCount >= 4, counterEvidenceVisible, gapVisible, confidenceVisible, recommendationVisible].filter(Boolean).length;
        const beats = ["State the claim before scoring the sources.", "Evidence rises in tiers, not as a flat list.", "Counterevidence stays visible beside support.", "Source gaps lower confidence before recommendation.", "Recommendation arrives only after confidence is explicit."];
        const beatIndex = Math.max(0, Math.min(beats.length - 1, Math.floor(p * beats.length)));
        return {{ videoId, seconds: safeSeconds, beat: beatIndex, sourceFacts: PACKAGE.sourceFacts.length, visualPattern: PACKAGE.visualPattern, claimLabels: sourceClaimLabels, evidenceLabels: sourceEvidenceLabels, activeEvidenceCount, claimVisible, counterEvidenceVisible, gapVisible, confidenceVisible, recommendationVisible, visibleMechanismCount }};
      }}
      if (PACKAGE.visualPattern === "skill-tree-route") {{
        const compactText = (value, limit = 15) => {{
          const text = String(value ?? "").trim().replace(/\\s+/g, " ");
          return text;
        }};
        const sourceRouteLabels = PACKAGE.routeLabels?.length ? PACKAGE.routeLabels : ["class start","travel nodes","damage cluster","defense cluster","attribute bridge","keystone tradeoff","respec checkpoint","late specialization"];
        const sourceCheckpointLabels = PACKAGE.checkpointLabels?.length ? PACKAGE.checkpointLabels : ["identity lock","damage floor","defense layer","gear fit","respec review"];
        const routeLabels = sourceRouteLabels.map((value) => compactText(value, 15));
        const checkpointLabels = sourceCheckpointLabels.map((value) => compactText(value, 18));
        const routePoints = [[128,345],[255,318],[385,292],[535,245],[680,328],[825,328],[965,295],[1100,245]];
        const routeProgress = ease((p - 0.04) / 0.54);
        const activeRouteNodeCount = Math.min(routePoints.length, Math.floor(routeProgress * routePoints.length + 0.999));
        const damageClusterVisible = p > 0.22;
        const defenseClusterVisible = p > 0.34;
        const attributeBridgeVisible = p > 0.48;
        const keystoneTradeoffVisible = p > 0.62;
        const respecVisible = p > 0.74;
        const lateClusterVisible = p > 0.86;
        const polyline = (points, stroke, width = 4) => {{
          el("polyline", {{ points: points.map((d) => d.join(",")).join(" "), fill: "none", stroke, "stroke-width": width, "stroke-linecap": "butt", "stroke-linejoin": "miter" }});
        }};
        const node = ([x, y], textValue, stroke, active = true, shape = "circle") => {{
          if (shape === "diamond") {{
            const points = `${{x}},${{y - 36}} ${{x + 43}},${{y}} ${{x}},${{y + 36}} ${{x - 43}},${{y}}`;
            el("polygon", {{ points, fill: active ? "#fff" : "#e7e7e7", stroke: active ? stroke : palette.line, "stroke-width": active ? 4 : 2 }});
          }} else {{
            circle(x, y, active ? 26 : 20, "#fff", active ? stroke : palette.line, active ? 4 : 2);
          }}
          label(x, y + 52, textValue, 14, active ? palette.ink : palette.muted);
        }};
        const meter = (x, y, name, value, color) => {{
          const width = 230;
          const height = 58;
          el("rect", {{ x, y, width, height, rx: 0, fill: grayLevel(3), stroke: palette.line }});
          const filled = Math.max(0, Math.min(width, width * ease(value)));
          if (filled > 0) el("rect", {{ x, y, width: filled, height, rx: 0, fill: color }});
          label(x + width / 2, y + height / 2 + 5, name, 15, palette.ink);
        }};
        el("rect", {{ x: 44, y: 112, width: 1192, height: 480, rx: 0, fill: "#fff", stroke: "#cfcfcf", "stroke-width": 2 }});
        label(112, 140, "ROUTE PLAN", 14, palette.muted);
        label(520, 140, "CLUSTERS", 14, palette.muted);
        label(830, 140, "TRADEOFFS", 14, palette.muted);
        label(1100, 140, "LATE PLAN", 14, palette.muted);
        for (let i = 0; i < routePoints.length - 1; i++) {{
          polyline([routePoints[i], routePoints[i + 1]], palette.line, 4);
          if (i < Math.max(0, activeRouteNodeCount - 1)) polyline([routePoints[i], routePoints[i + 1]], palette.route, 8);
        }}
        const nodeColors = [palette.route, palette.route, palette.damage, palette.damage, palette.attribute, palette.tradeoff, palette.gold, palette.atlas];
        routePoints.forEach((point, idx) => node(point, routeLabels[idx], nodeColors[idx], idx < activeRouteNodeCount, idx === 5 ? "diamond" : "circle"));
        if (damageClusterVisible) {{
          const damageNodes = [[345,185],[478,170],[575,205]];
          polyline([routePoints[2], ...damageNodes], palette.damage, 7);
          damageNodes.forEach(([x, y]) => circle(x, y, 15, "#fff", palette.damage, 4));
          el("rect", {{ x: 414, y: 132, width: 182, height: 52, rx: 0, fill: "#ffccd5", stroke: palette.damage, "stroke-width": 3 }});
          label(505, 164, routeLabels[2], 16, palette.damage);
          meter(690, 178, "damage threshold", ease((p - 0.22) / 0.24), palette.damage);
        }}
        if (defenseClusterVisible) {{
          const defenseNodes = [[368,430],[510,480],[642,438]];
          polyline([routePoints[2], ...defenseNodes], palette.defense, 7);
          defenseNodes.forEach(([x, y]) => circle(x, y, 15, "#fff", palette.defense, 4));
          el("rect", {{ x: 414, y: 456, width: 186, height: 52, rx: 0, fill: "#e7e7e7", stroke: palette.defense, "stroke-width": 3 }});
          label(507, 488, routeLabels[3], 16, palette.defense);
          meter(724, 438, "defense layer", ease((p - 0.34) / 0.24), palette.defense);
        }}
        if (attributeBridgeVisible) {{
          el("rect", {{ x: 604, y: 292, width: 154, height: 73, rx: 0, fill: "#e7e7e7", stroke: palette.attribute, "stroke-width": 4 }});
          label(681, 324, "attribute bridge", 16, palette.attribute);
          label(681, 348, routeLabels[4], 14, palette.ink);
        }}
        if (keystoneTradeoffVisible) {{
          el("polygon", {{ points: "825,254 888,328 825,402 762,328", fill: "#ffccd5", stroke: palette.tradeoff, "stroke-width": 5 }});
          label(825, 318, "keystone", 16, palette.tradeoff);
          label(825, 342, routeLabels[5], 14, palette.ink);
          meter(928, 362, "tradeoff cost", ease((p - 0.62) / 0.20), palette.tradeoff);
        }}
        if (respecVisible) {{
          polyline([routePoints[5], [930,450], [760,526], [520,525]], palette.gold, 6);
          label(875, 478, "respec route", 16, palette.gold);
          label(875, 500, routeLabels[6], 14, palette.ink);
        }}
        if (lateClusterVisible) {{
          const lateNodes = [[1050,205],[1160,285],[1070,395]];
          polyline([routePoints[7], lateNodes[1], lateNodes[2]], palette.atlas, 7);
          lateNodes.forEach(([x, y]) => circle(x, y, 15, "#fff", palette.atlas, 4));
          el("rect", {{ x: 990, y: 456, width: 210, height: 64, rx: 0, fill: "#e7e7e7", stroke: palette.atlas, "stroke-width": 4 }});
          label(1095, 482, "late specialization", 16, palette.atlas);
          label(1095, 505, "kept separate", 14, palette.ink);
        }}
        checkpointLabels.forEach((textValue, idx) => {{
          const x = 150 + idx * 230;
          const active = p > 0.16 + idx * 0.14;
          el("rect", {{ x: x - 92, y: 542, width: 184, height: 46, rx: 0, fill: active ? "#ffffff" : "#e7e7e7", stroke: active ? palette.route : "#ccd6e3", "stroke-width": active ? 3 : 2 }});
          label(x, 572, textValue, 14, palette.ink);
        }});
        const visibleMechanismCount = [activeRouteNodeCount >= 4, damageClusterVisible, defenseClusterVisible, attributeBridgeVisible, keystoneTradeoffVisible, respecVisible, lateClusterVisible].filter(Boolean).length;
        const beats = ["Lock the playstyle before spending travel nodes.", "Damage and defense clusters should be evaluated separately.", "Attribute bridges are costs, not free progress.", "Keystones are tradeoffs that need a respec checkpoint.", "Late specialization stays separate from the core route."];
        const beatIndex = Math.max(0, Math.min(beats.length - 1, Math.floor(p * beats.length)));
        return {{ videoId, seconds: safeSeconds, beat: beatIndex, sourceFacts: PACKAGE.sourceFacts.length, visualPattern: PACKAGE.visualPattern, routeLabels: sourceRouteLabels, checkpointLabels: sourceCheckpointLabels, activeRouteNodeCount, damageClusterVisible, defenseClusterVisible, attributeBridgeVisible, keystoneTradeoffVisible, respecVisible, lateClusterVisible, visibleMechanismCount }};
      }}
      if (PACKAGE.visualPattern === "skill-tree") {{
      el("rect", {{ x: 60, y: 115, width: 930, height: 495, rx: 0, fill: "#ffffff", stroke: "#cfcfcf" }});
      el("rect", {{ x: 1015, y: 115, width: 203, height: 495, rx: 0, fill: "#e7e7e7", stroke: "#9c9c9c" }});
      const compactText = (value, limit = 12) => {{
        const text = String(value ?? "").trim().replace(/\\s+/g, " ");
        return text;
      }};
      const sourceTreeLabels = PACKAGE.treeLabels?.length ? PACKAGE.treeLabels : ["start","small","notable","damage","defense","attr","gear","tradeoff","boss","points","late game"];
      const sourceMeterLabels = PACKAGE.meterLabels?.length ? PACKAGE.meterLabels : ["damage plan","defense check","attribute fit"];
      const treeLabels = sourceTreeLabels.map((value) => compactText(value, 12));
      const meterLabels = sourceMeterLabels.map((value) => compactText(value, 17));
      const pts = [[145,360], [255,335], [360,300], [655,330], [790,330], [920,330]];
      for (let i = 0; i < pts.length - 1; i++) line(pts[i][0], pts[i][1], pts[i+1][0], pts[i+1][1], palette.line, 3);
      const routeCount = Math.floor(ease((p - 0.04) / 0.28) * (pts.length - 1));
      for (let i = 0; i < routeCount; i++) line(pts[i][0], pts[i][1], pts[i+1][0], pts[i+1][1], palette.route, 8);
      const damageBranchVisible = ease((p - 0.24) / 0.18) > 0.5;
      const defenseBranchVisible = ease((p - 0.34) / 0.18) > 0.5;
      const keystoneVisible = p > 0.62;
      const atlasVisible = p > 0.78;
      const visibleMechanismCount = [routeCount >= 4, damageBranchVisible, defenseBranchVisible, keystoneVisible, atlasVisible].filter(Boolean).length;
      line(360,300,500,245, damageBranchVisible ? palette.damage : palette.line, 7);
      line(360,300,500,430, defenseBranchVisible ? palette.defense : palette.line, 7);
      [[145,360,treeLabels[0],palette.route],[255,335,treeLabels[1],palette.route],[360,300,treeLabels[2],palette.route],[500,245,treeLabels[3],palette.damage],[500,430,treeLabels[4],palette.defense],[655,330,treeLabels[5],palette.attribute],[790,330,treeLabels[6],palette.attribute],[920,330,treeLabels[7],palette.tradeoff],[1060,250,treeLabels[8],palette.atlas],[1150,340,treeLabels[9],palette.atlas],[1060,430,treeLabels[10],palette.atlas]].forEach((d, i) => {{
        const active = ease((p - i * 0.075) / 0.12);
        circle(d[0], d[1], 18 + 8 * active, "#fff", active > 0.1 ? d[3] : palette.line, active > 0.1 ? 4 : 2);
        if (active > 0.3) label(d[0], d[1] + 48, d[2], 16, palette.ink);
      }});
      if (atlasVisible) {{ line(1060,250,1150,340,palette.atlas,7); line(1150,340,1060,430,palette.atlas,7); }}
      const skillMeterWidth = 240;
      const skillMeterHeight = 65;
      [[120,520,meterLabels[0],palette.damage,ease((p - 0.30) / 0.20)],[390,520,meterLabels[1],palette.defense,ease((p - 0.42) / 0.20)],[660,520,meterLabels[2],palette.attribute,ease((p - 0.52) / 0.20)]].forEach((d) => {{
        el("rect", {{ x: d[0], y: d[1], width: skillMeterWidth, height: skillMeterHeight, rx: 0, fill: grayLevel(3), stroke: palette.line }});
        const filled = Math.max(0, Math.min(skillMeterWidth, skillMeterWidth * ease(d[4])));
        if (filled > 0) el("rect", {{ x: d[0], y: d[1], width: filled, height: skillMeterHeight, rx: 0, fill: d[3] }});
        label(d[0] + skillMeterWidth / 2, d[1] + skillMeterHeight / 2 + 5, d[2], 16, palette.ink);
      }});
      const beats = ["Pick the active skill and playstyle first.", "Support damage and survival.", "Use attributes to unlock gear or gems.", "Keystones are tradeoffs.", "Atlas passives are separate late-game strategy."];
      const beat = beats[Math.min(beats.length - 1, Math.floor(p * beats.length))];
      return {{ videoId, seconds: safeSeconds, beat, sourceFacts: PACKAGE.sourceFacts.length, visualPattern: PACKAGE.visualPattern, treeLabels: sourceTreeLabels, meterLabels: sourceMeterLabels, routeCount, damageBranchVisible, defenseBranchVisible, keystoneVisible, atlasVisible, visibleMechanismCount }};
      }}
      return {{ videoId, seconds: safeSeconds, beat: 0, sourceFacts: PACKAGE.sourceFacts.length, visualPattern: PACKAGE.visualPattern, visibleMechanismCount: 0 }};
    }}
    const baseRenderConceptFrame = renderConceptFrame;
    window.renderConceptFrame = function(videoId, seconds, options = {{}}) {{
      const state = baseRenderConceptFrame(videoId, seconds, options) || {{}};
      const stateBeat = Number(state.beat);
      const progressBeat = Math.floor(clamp(Number(seconds || 0) / Number(PACKAGE.durationSeconds || {args.duration})) * 5);
      const activeIndex = Number.isFinite(stateBeat) ? stateBeat : progressBeat;
      drawSourceZones(activeIndex);
      enforceFlushMasonryInteriors();
      const cameraLayer = stage.querySelector("#camera-layer");
      const cameraX = Number(cameraLayer?.getAttribute("data-camera-x") || 0);
      const cameraY = Number(cameraLayer?.getAttribute("data-camera-y") || 0);
      const cameraScale = Number(cameraLayer?.getAttribute("data-camera-scale") || 1);
      const cameraMoving = Math.abs(cameraX) > 0.1 || Math.abs(cameraY) > 0.1 || Math.abs(cameraScale - 1) > 0.01;
      return {{ ...state, cameraX, cameraY, cameraScale, cameraMoving, ...zoneState(activeIndex) }};
    }};
    window.renderConceptFrame(PACKAGE.outputId, 0, {{ capture: false }});
  </script>
</body>
</html>
"""
    if args.edge_style == "square":
        html = re.sub(r'\brx:\s*\d+(?:\.\d+)?', 'rx: 0', html)
        html = re.sub(r'\bry:\s*\d+(?:\.\d+)?', 'ry: 0', html)
        html = re.sub(r'border-radius:\s*[^;"}]+', 'border-radius: 0', html)
        html = html.replace('"stroke-linecap": "butt"', '"stroke-linecap": "butt"')
        html = html.replace('"stroke-linejoin": "miter"', '"stroke-linejoin": "miter"')
        html = normalize_html_rect_gray_levels(html)
        html = normalize_render_frame_gray_color_literals(html)
        html = normalize_html_zero_padding_rects(html)
        html = snap_html_rects_to_grid(html)
    paths["html"].write_text(html, encoding="utf-8")


def write_render_js(args: argparse.Namespace, paths: dict[str, Path], package: dict[str, object]) -> None:
    facts_args: list[str] = []
    for fact in package["sourceFacts"]:
        facts_args.extend(["--fact", str(fact)])
    anchor_args: list[str] = []
    for anchor in package["strategyAnchors"]:
        anchor_args.extend(["--anchor", str(anchor)])
    source_args: list[str] = []
    for source in package["sourceUrls"]:
        source_args.extend(["--source-url", str(source)])
    node_label_args: list[str] = []
    for label in package.get("causalLabels", []):
        node_label_args.extend(["--node-label", str(label)])
    option_label_args: list[str] = []
    for label in package.get("decisionOptions", []):
        option_label_args.extend(["--option-label", str(label)])
    criterion_label_args: list[str] = []
    for label in package.get("decisionCriteria", []):
        criterion_label_args.extend(["--criterion-label", str(label)])
    system_label_args: list[str] = []
    for label in package.get("systemLabels", []):
        system_label_args.extend(["--system-label", str(label)])
    tree_label_args: list[str] = []
    for label in package.get("treeLabels", []):
        tree_label_args.extend(["--tree-label", str(label)])
    meter_label_args: list[str] = []
    for label in package.get("meterLabels", []):
        meter_label_args.extend(["--meter-label", str(label)])
    route_label_args: list[str] = []
    for label in package.get("routeLabels", []):
        route_label_args.extend(["--route-label", str(label)])
    checkpoint_label_args: list[str] = []
    for label in package.get("checkpointLabels", []):
        checkpoint_label_args.extend(["--checkpoint-label", str(label)])
    phase_label_args: list[str] = []
    for label in package.get("phaseLabels", []):
        phase_label_args.extend(["--phase-label", str(label)])
    metric_label_args: list[str] = []
    for label in package.get("metricLabels", []):
        metric_label_args.extend(["--metric-label", str(label)])
    threshold_label_args: list[str] = []
    for label in package.get("thresholdLabels", []):
        threshold_label_args.extend(["--threshold-label", str(label)])
    dependency_label_args: list[str] = []
    for label in package.get("dependencyLabels", []):
        dependency_label_args.extend(["--dependency-label", str(label)])
    cluster_label_args: list[str] = []
    for label in package.get("clusterLabels", []):
        cluster_label_args.extend(["--cluster-label", str(label)])
    trace_label_args: list[str] = []
    for label in package.get("traceLabels", []):
        trace_label_args.extend(["--trace-label", str(label)])
    flow_label_args: list[str] = []
    for label in package.get("flowLabels", []):
        flow_label_args.extend(["--flow-label", str(label)])
    lane_label_args: list[str] = []
    for label in package.get("laneLabels", []):
        lane_label_args.extend(["--lane-label", str(label)])
    handoff_label_args: list[str] = []
    for label in package.get("handoffLabels", []):
        handoff_label_args.extend(["--handoff-label", str(label)])
    threat_label_args: list[str] = []
    for label in package.get("threatLabels", []):
        threat_label_args.extend(["--threat-label", str(label)])
    barrier_label_args: list[str] = []
    for label in package.get("barrierLabels", []):
        barrier_label_args.extend(["--barrier-label", str(label)])
    consequence_label_args: list[str] = []
    for label in package.get("consequenceLabels", []):
        consequence_label_args.extend(["--consequence-label", str(label)])
    scenario_label_args: list[str] = []
    for label in package.get("scenarioLabels", []):
        scenario_label_args.extend(["--scenario-label", str(label)])
    probability_label_args: list[str] = []
    for label in package.get("probabilityLabels", []):
        probability_label_args.extend(["--probability-label", str(label)])
    claim_label_args: list[str] = []
    for label in package.get("claimLabels", []):
        claim_label_args.extend(["--claim-label", str(label)])
    evidence_label_args: list[str] = []
    for label in package.get("evidenceLabels", []):
        evidence_label_args.extend(["--evidence-label", str(label)])
    layer_label_args: list[str] = []
    for label in package.get("layerLabels", []):
        layer_label_args.extend(["--layer-label", str(label)])
    concern_label_args: list[str] = []
    for label in package.get("concernLabels", []):
        concern_label_args.extend(["--concern-label", str(label)])
    lineage_label_args: list[str] = []
    for label in package.get("lineageLabels", []):
        lineage_label_args.extend(["--lineage-label", str(label)])
    quality_label_args: list[str] = []
    for label in package.get("qualityLabels", []):
        quality_label_args.extend(["--quality-label", str(label)])
    state_label_args: list[str] = []
    for label in package.get("stateLabels", []):
        state_label_args.extend(["--state-label", str(label)])
    guard_label_args: list[str] = []
    for label in package.get("guardLabels", []):
        guard_label_args.extend(["--guard-label", str(label)])
    argv = [
        "run",
        "--script",
        SCRIPT_PATH.as_posix(),
        "--project-root",
        args.project_root.as_posix(),
        "--title",
        args.title,
        "--topic",
        args.topic,
        "--output-id",
        args.output_id,
        "--pattern",
        args.pattern,
        "--checked-date",
        args.checked_date,
        "--audience",
        args.audience,
        "--duration",
        str(args.duration),
        "--fps",
        str(args.fps),
        "--width",
        str(args.width),
        "--height",
        str(args.height),
        "--edge-style",
        args.edge_style,
        *(["--masonry-layout"] if args.masonry_layout else []),
        *facts_args,
        *anchor_args,
        *source_args,
        *node_label_args,
        *option_label_args,
        *criterion_label_args,
        *system_label_args,
        *tree_label_args,
        *meter_label_args,
        *route_label_args,
        *checkpoint_label_args,
        *phase_label_args,
        *metric_label_args,
        *threshold_label_args,
        *dependency_label_args,
        *cluster_label_args,
        *trace_label_args,
        *flow_label_args,
        *lane_label_args,
        *handoff_label_args,
        *threat_label_args,
        *barrier_label_args,
        *consequence_label_args,
        *scenario_label_args,
        *probability_label_args,
        *claim_label_args,
        *evidence_label_args,
        *layer_label_args,
        *concern_label_args,
        *lineage_label_args,
        *quality_label_args,
        *state_label_args,
        *guard_label_args,
    ]
    render_js = f"""#!/usr/bin/env node
import {{ spawnSync }} from "node:child_process";

const args = {json.dumps(argv, indent=2)};
const result = spawnSync("uv", args, {{ stdio: "inherit" }});
process.exit(result.status ?? 1);
"""
    paths["render_js"].write_text(render_js, encoding="utf-8")


def render_video(args: argparse.Namespace, paths: dict[str, Path]) -> None:
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        raise RuntimeError("ffmpeg is required to create the MP4, but it was not found on PATH.")
    paths["video"].parent.mkdir(parents=True, exist_ok=True)
    fonts = {
        "title": load_font(31, True),
        "body": load_font(25, True),
        "label": load_font(19, True),
        "small": load_font(17, True),
        "tiny": load_font(14, True),
    }
    frame_count = max(1, int(round(args.duration * args.fps)))
    cmd = [
        ffmpeg,
        "-y",
        "-f",
        "rawvideo",
        "-pix_fmt",
        "rgb24",
        "-s",
        f"{args.width}x{args.height}",
        "-r",
        str(args.fps),
        "-i",
        "-",
        "-an",
        "-c:v",
        "libx264",
        "-pix_fmt",
        "yuv420p",
        "-preset",
        "veryfast",
        "-crf",
        "20",
        "-movflags",
        "+faststart",
        str(paths["video"]),
    ]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    assert proc.stdin is not None
    try:
        for frame in range(frame_count):
            img = render_frame(frame / args.fps, args, fonts)
            proc.stdin.write(img.tobytes())
    finally:
        proc.stdin.close()
    stderr = proc.stderr.read().decode("utf-8", errors="replace") if proc.stderr else ""
    return_code = proc.wait()
    if return_code != 0:
        raise RuntimeError(f"ffmpeg failed with exit code {return_code}\n{stderr}")


def run_ffprobe(video: Path) -> dict[str, object]:
    ffprobe = shutil.which("ffprobe")
    if not ffprobe:
        return {"available": False}
    cmd = [
        ffprobe,
        "-v",
        "error",
        "-select_streams",
        "v:0",
        "-show_entries",
        "stream=width,height,r_frame_rate,nb_frames,duration",
        "-show_entries",
        "format=duration,size",
        "-of",
        "json",
        str(video),
    ]
    result = subprocess.run(cmd, text=True, capture_output=True, check=False)
    if result.returncode != 0:
        return {"available": True, "error": result.stderr.strip()}
    return json.loads(result.stdout)


def write_contact_sheet(paths: dict[str, Path]) -> bool:
    uv = shutil.which("uv")
    script = Path(__file__).with_name("make_video_contact_sheet.py")
    if not uv or not script.exists():
        return False
    paths["contact_sheet"].parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        uv,
        "run",
        "--script",
        str(script),
        "--video",
        str(paths["video"]),
        "--output",
        str(paths["contact_sheet"]),
        "--manifest",
        str(paths["contact_sheet_manifest"]),
        "--samples",
        "6",
        "--columns",
        "3",
        "--thumb-width",
        "426",
        "--label-times",
        "--min-tile-color-buckets",
        "12",
        "--min-tile-nonbackground-ratio",
        "0.015",
        "--min-consecutive-change-ratio",
        "0.002",
        "--min-changing-pairs",
        "2",
        "--max-low-change-pairs",
        "2",
    ]
    result = subprocess.run(cmd, text=True, capture_output=True, check=False)
    return (
        result.returncode == 0
        and paths["contact_sheet"].exists()
        and paths["contact_sheet_manifest"].exists()
    )


def write_review(args: argparse.Namespace, paths: dict[str, Path], probe: dict[str, object], contact_sheet: bool) -> None:
    paths["review"].parent.mkdir(parents=True, exist_ok=True)
    stream = (probe.get("streams") or [{}])[0] if isinstance(probe.get("streams"), list) else {}
    fmt = probe.get("format") if isinstance(probe.get("format"), dict) else {}
    duration = fmt.get("duration") or stream.get("duration") or args.duration
    size = fmt.get("size") or (paths["video"].stat().st_size if paths["video"].exists() else 0)
    pattern = selected_pattern(args)
    if pattern == "skill-tree-route":
        critique = """- Strength: the video separates main route growth, damage cluster, defense cluster, attribute bridge, keystone tradeoff, respec checkpoint, and late specialization into distinct mechanisms.
- Strength: route nodes activate before the side clusters, which makes travel-node cost visible before build rewards appear.
- Strength: the keystone is treated as a tradeoff and paired with a respec checkpoint instead of being framed as a generic reward.
- Strength: late specialization is spatially separated from the core route, preserving progression layers for game-tree, learning-path, or capability-map explainers.
- Defect: this draft uses schematic geometry rather than a captured game UI or exact graph layout, so final production should not present it as an exact passive tree.
- Defect: node distances and point costs are not quantitatively encoded unless supplied as source facts; final production should bind route length and checkpoint timing to source data.
- Defect: dense node names may need wrapping, callout sequencing, or a secondary legend in final delivery.
- Skill lesson: route-tree videos need path cost, side clusters, attribute bridges, keystone tradeoffs, respec checkpoints, and late specialization, not only highlighted nodes."""
    elif pattern == "systems-flow":
        if hook_requested(args):
            critique = """- Strength: the video renders Hook as lifecycle interception: event timeline, shield gate, provider event surfaces, command blocking, log filtering, and cost/latency tradeoff are separate mechanisms.
- Strength: source anchors are visible as low-text geometry instead of text cards: the dangerous Bash branch stops at a hard gate while a separate preprocessing path shrinks context.
- Strength: GitHub, Claude Code, and OpenCode are represented as different event surfaces, not as a generic three-column feature table.
- Strength: the final lifecycle-control boundary appears only after policy and preprocessing mechanics are visible, so the ending is a state consequence instead of a title card.
- Defect: this draft is schematic rather than a captured real hook configuration UI; final production can bind exact event names and hook config syntax if those are supplied.
- Defect: provider-specific capabilities are intentionally geometric and unlabeled to satisfy the low-text narration split.
- Defect: the helper renders with Pillow and ffmpeg rather than browser-captured SVG frames; use it as a validation scaffold, then rebuild advanced finals in the full HTML renderer.
- Skill lesson: Hook videos need lifecycle event timing, active policy interception, preprocessing, and cost/latency motion; a generic queue/retry systems-flow diagram is a design failure."""
        elif skill_package_requested(args):
            critique = """- Strength: the video renders Skill as reusable workflow packaging: skill card stack, prompt-wall collapse, compatible SKILL.md folder structures, progressive disclosure cost meter, examples, tool/script modules, read surface, trimming, and final workflow stamp are separate mechanisms.
- Strength: the long prompt wall becomes a scoped skill package instead of staying as a permanent prompt, which makes progressive disclosure visible without relying on captions.
- Strength: compatible provider folders and resource modules share a hard-edge grid, so scripts, references, assets, and validation read as a reusable bundle rather than unrelated cards.
- Strength: the cost/read surface progresses only after activation, making the token-cost point visible through meter motion and state changes.
- Defect: this draft is schematic rather than a captured real skill editor or marketplace UI; final production can bind exact SKILL.md syntax and provider affordances if those are supplied.
- Defect: provider differences are intentionally encoded with geometry and grayscale hierarchy rather than vendor-specific branding to keep the Metro style contract.
- Defect: the helper renders with Pillow and ffmpeg rather than browser-captured SVG frames; use it as a validation scaffold, then rebuild advanced finals in the full HTML renderer.
- Skill lesson: Skill videos need on-demand reusable packaging, prompt collapse, resource bundles, progressive disclosure, and trimming; a generic queue/retry systems-flow diagram is a design failure."""
        else:
            critique = """- Strength: the video has multiple coordinated motion systems: packet routing, queue fill, worker pulsing, retry/dead-letter branching, metrics, and feedback control.
- Strength: failures are visible as explicit branch paths instead of disappearing inside a generic processor box.
- Strength: queue pressure and throughput are separated, which helps the viewer understand capacity versus output.
- Strength: feedback control loops back to intake and closes a visible throttle gate, making the prevention mechanic visible rather than only labeling it.
- Defect: this draft is still a synthetic systems diagram; final production should replace generic component names with task-specific objects from the source package.
- Defect: the helper uses short labels for silent validation, but a narrated version should remove most text and let motion carry more of the explanation.
- Defect: the helper renders with Pillow and ffmpeg rather than browser-captured D3/Anime.js frames; use it as a validation scaffold, then rebuild advanced finals in the full HTML renderer.
- Skill lesson: advanced video validation needs at least three semantic motion systems, not one route plus a footer caption."""
    elif pattern == "state-machine":
        critique = """- Strength: the video separates lifecycle states from transition guards, so state changes are not implied by a generic progress bar.
- Strength: rollback and compensation use a dedicated recovery lane, making failure handling visible instead of hiding it behind a success path.
- Strength: the terminal-state panel separates completed work from parked or failed work, which helps lifecycle explainers avoid ambiguous endings.
- Strength: guard checks, state activation, recovery routing, and terminal-state reveal create multiple semantic motion systems for validation.
- Defect: this draft uses generic state names; final production should replace them with domain-specific states from the source package.
- Defect: recovery timing is schematic rather than derived from a real trace, so a final version should map exact failure triggers and compensation order.
- Defect: the helper renders with Pillow and ffmpeg rather than browser-captured SVG frames; use it as an isolated-validation scaffold, then replace with a richer HTML/D3 renderer for final production.
- Skill lesson: lifecycle videos need explicit recovery and terminal states, not just a left-to-right happy path."""
    elif pattern == "comparison-matrix":
        critique = """- Strength: the video compares options against shared criteria instead of declaring a winner before evidence is visible.
- Strength: score bars, score-shift markers, tradeoff lens, recommendation, and guardrail create separate semantic mechanisms.
- Strength: the recommendation appears late, after criteria rows have enough visual evidence to support it.
- Strength: the guardrail prevents the matrix from becoming a blind ranking and makes risk handling visible.
- Defect: the helper uses synthetic scores; final production should derive score values and weights from the source package.
- Defect: option names are generic unless the prompt supplies domain-specific alternatives, so a final version should replace them with real candidates.
- Defect: the helper renders with Pillow and ffmpeg rather than browser-captured SVG frames; use it as an isolated-validation scaffold, then replace with a richer HTML/D3 renderer for final production.
- Skill lesson: comparison videos need shared criteria and a visible guardrail, not only a ranking or pros/cons text."""
    elif pattern == "causal-loop":
        critique = """- Strength: the video separates cause chain, reinforcing loop, delayed effect, balancing constraint, side effect, and intervention into distinct mechanisms.
- Strength: the delayed-effect label appears before the side-effect branch, which prevents the loop from reading like a simple timeline.
- Strength: the intervention appears last, after the loop and side effect are visible, so the solution targets leverage rather than a symptom.
- Strength: pressure, delay, and leverage meters give reviewers quantitative-looking states without requiring exact source values.
- Defect: this draft uses generic causal nodes; final production should replace them with domain-specific variables from the source package.
- Defect: loop strength and delay duration are schematic; a final version should map real weights, time constants, or evidence if available.
- Defect: the helper renders with Pillow and ffmpeg rather than browser-captured SVG frames; use it as an isolated-validation scaffold, then replace with a richer HTML/D3 renderer for final production.
- Skill lesson: causal videos need delay, balancing, side effects, and leverage points, not just arrows between causes."""
    elif pattern == "phase-timeline":
        critique = """- Strength: the video separates phase cards, risk surfacing, decision gate, handoff route, and release milestone into distinct mechanisms.
- Strength: the current-phase token gives the viewer a stable read path through the chronology.
- Strength: risk and handoff appear below the main sequence, preventing the timeline from becoming a flat checklist.
- Defect: exact dates, owners, and dependencies are synthetic unless supplied as source facts; final production should bind those details to the source package.
- Defect: the helper uses compact labels and simple geometry; final videos should refine spacing and captions for longer phase names.
- Defect: the helper renders with Pillow and ffmpeg rather than browser-captured SVG frames; use it as an isolated-validation scaffold, then replace with a richer HTML/D3 renderer for final production.
- Skill lesson: timeline videos need gate, risk, and handoff motion in addition to ordered milestones."""
    elif pattern == "metric-dashboard":
        critique = """- Strength: the video separates trend reveal, threshold bands, anomaly marker, forecast cone, and decision window into distinct mechanisms.
- Strength: metric cards keep primary, input, output, quality, and risk signals visible without turning the frame into a text-only report.
- Strength: the decision panel appears after thresholds, anomaly, and forecast are visible, so action follows evidence.
- Defect: metric values are schematic unless supplied as source facts; final production should bind chart points and thresholds to real source data.
- Defect: uncertainty is shown as a simple cone, not a statistically derived confidence interval.
- Defect: the helper renders with Pillow and ffmpeg rather than browser-captured SVG frames; use it as an isolated-validation scaffold, then replace with a richer HTML/D3 renderer for final production.
- Skill lesson: metric videos need threshold and action mechanics, not only a line chart or KPI cards."""
    elif pattern == "dependency-map":
        critique = """- Strength: the video separates dependency graph, cluster boundaries, risk edge, bottleneck, cutover gate, fallback path, and release readiness into distinct mechanisms.
- Strength: source dependencies converge before the release gate appears, which prevents the story from reading like a flat checklist.
- Strength: the fallback path appears late as a safety route, not as a vague warning after the fact.
- Defect: dependency weights, owners, and lead times are schematic unless supplied as source facts; final production should bind those values to a real dependency register.
- Defect: the helper uses compact labels and simplified graph geometry; final videos should tune layout for dense dependency names and cyclic risks.
- Defect: the helper renders with Pillow and ffmpeg rather than browser-captured SVG frames; use it as an isolated-validation scaffold, then replace with a richer HTML/D3 renderer for final production.
- Skill lesson: dependency videos need risk, bottleneck, cutover, and fallback motion, not only connected nodes."""
    elif pattern == "sequence-trace":
        critique = """- Strength: the video separates service lanes, span bars, handoff markers, critical path, latency budget, retry branch, fallback, and returned response into distinct mechanisms.
- Strength: the trace waterfall makes latency ownership visible instead of turning the request path into a generic systems diagram.
- Strength: retry and fallback are drawn as late branches, so resilience behavior appears after the slow span is visible.
- Defect: span durations, trace IDs, percentiles, and error rates are schematic unless supplied as source facts; final production should bind them to real trace data.
- Defect: dense service names may need lane wrapping or a side legend in final delivery.
- Defect: the helper renders with Pillow and ffmpeg rather than browser-captured SVG frames; use it as an isolated-validation scaffold, then replace with a richer HTML/D3 renderer for final production.
- Skill lesson: trace videos need ordered spans, handoffs, latency budget, retry, and fallback, not only connected services."""
    elif pattern == "sankey-flow":
        critique = """- Strength: the video separates input, split, explicit loss, parallel transforms, merge, bottleneck, and final output into distinct mechanisms.
- Strength: loss exits as its own branch instead of being implied by a shrinking total, making dropoff auditable in the frame.
- Strength: merge and bottleneck states appear before output, so final value is not treated as an automatic consequence of input volume.
- Defect: band widths and proportions are schematic unless supplied as source facts; final production should bind widths to real measured values.
- Defect: dense domain labels may need larger lanes or external legends in final delivery.
- Defect: the helper renders with Pillow and ffmpeg rather than browser-captured SVG frames; use it as an isolated-validation scaffold, then replace with a richer HTML/D3 renderer for final production.
- Skill lesson: conversion videos need split, loss, transform, merge, bottleneck, and output mechanics, not only a funnel or static total."""
    elif pattern == "swimlane-handoff":
        if plugin_requested(args):
            critique = """- Strength: the video renders Harness Plugin as a packageable behavior bundle: plugin_bundle_cube assembly, detachable modules, provider packaging, governance, versioning, install fanout, and cost/noise split are separate mechanisms.
- Strength: GitHub, Claude, and OpenCode are represented as comparable package surfaces without turning the frame into a provider feature table.
- Strength: governance is visible as allowlist gates, version arrows, and team install fanout, so distribution reads as policy and standardization rather than copied local files.
- Strength: the final package-install stamp appears only after module contents, provider packaging, governance, and noisy-plugin risk are visible.
- Defect: this draft is schematic rather than a captured real marketplace or manifest UI; final production can bind exact schema names and docs snippets if supplied.
- Defect: provider-specific copy is intentionally suppressed to satisfy the low-text Metro contract.
- Defect: the helper renders with Pillow and ffmpeg rather than browser-captured SVG frames; use it as an isolated-validation scaffold, then rebuild advanced finals in the full HTML renderer.
- Skill lesson: Harness Plugin videos need package assembly, detachable runtime modules, provider package surfaces, governance/versioning, install fanout, and noisy-context cost risk; a generic swimlane-handoff diagram is a design failure."""
        else:
            critique = """- Strength: the video separates owner lanes, sequential handoff steps, SLA pressure, approval, rework, escalation, and completion into distinct mechanisms.
- Strength: work crosses lane boundaries visibly, so ownership transfer is not hidden inside a generic lifecycle state.
- Strength: rework and escalation appear as routes rather than after-the-fact warnings, making exception handling auditable.
- Defect: SLA thresholds, queue age, owner capacity, and escalation policy are schematic unless supplied as source facts; final production should bind those values to real workflow data.
- Defect: dense team or step names may need wider lanes, wrapping, or external legends in final delivery.
- Defect: the helper renders with Pillow and ffmpeg rather than browser-captured SVG frames; use it as an isolated-validation scaffold, then replace with a richer HTML/D3 renderer for final production.
- Skill lesson: workflow videos need ownership lanes, handoff motion, SLA pressure, rework, escalation, and completion, not only a state diagram or checklist."""
    elif pattern == "risk-bowtie":
        critique = """- Strength: the video separates threats, preventive barriers, top event, mitigative barriers, consequences, degraded controls, residual risk, and repair action into distinct mechanisms.
- Strength: prevention and mitigation sit on opposite sides of the top event, so controls are not treated as interchangeable labels.
- Strength: degraded barrier and repair action appear late, making assurance gaps visible instead of hiding them behind a completed diagram.
- Defect: threat likelihood, consequence severity, control effectiveness, and assurance evidence are schematic unless supplied as source facts; final production should bind them to real risk data.
- Defect: dense threat, barrier, or consequence labels may need wrapping or a larger bowtie canvas in final delivery.
- Defect: the helper renders with Pillow and ffmpeg rather than browser-captured SVG frames; use it as an isolated-validation scaffold, then replace with a richer HTML/D3 renderer for final production.
- Skill lesson: risk videos need prevention, top event, mitigation, consequence, degraded-control, and repair mechanics, not only a cause map or risk list."""
    elif pattern == "scenario-tree":
        critique = """- Strength: the video separates decision root, scenario branches, probabilities, evidence weight, upside, risk, fallback, decision gate, and selected outcome into distinct mechanisms.
- Strength: probabilities appear before the decision gate, so the choice follows branch evidence rather than a static recommendation.
- Strength: fallback remains visible as an alternate route, preventing the outcome from reading as a single happy path.
- Defect: probabilities, payoffs, confidence, and expected value are schematic unless supplied as source facts; final production should bind them to real scenario assumptions.
- Defect: dense scenario names may need wrapping or a larger tree canvas in final delivery.
- Defect: the helper renders with Pillow and ffmpeg rather than browser-captured SVG frames; use it as an isolated-validation scaffold, then replace with a richer HTML/D3 renderer for final production.
- Skill lesson: scenario videos need branching futures, probability/evidence, risk, upside, fallback, and outcome mechanics, not only a ranking matrix."""
    elif pattern == "evidence-ladder":
        critique = """- Strength: the video separates working claim, evidence tiers, counterevidence, source gap, confidence, uncertainty, and recommendation into distinct mechanisms.
- Strength: the recommendation appears after support, counterweight, and gap states, preventing a research video from becoming a premature conclusion.
- Strength: counterevidence and source gaps stay visible beside the support ladder, which makes uncertainty auditable instead of hiding it in narration.
- Defect: source citations, evidence weights, confidence values, and methodology caveats are schematic unless supplied as source facts; final production should bind them to real source material.
- Defect: dense source names may need a larger source ledger, wrapping, or voiceover-only naming in final delivery.
- Defect: the helper renders with Pillow and ffmpeg rather than browser-captured SVG frames; use it as an isolated-validation scaffold, then replace with a richer HTML/D3 renderer for final production.
- Skill lesson: research videos need claim, evidence tiers, counterevidence, source gaps, confidence, and recommendation timing, not only a flat bibliography or summary text."""
    elif pattern == "layered-architecture":
        critique = """- Strength: the video separates layer ownership, request path, cross-cutting policy, failure route, observability, and rollout gate into distinct mechanisms.
- Strength: layer activation happens before operational overlays, so cross-cutting concerns do not masquerade as normal layers.
- Strength: failure and observability routes sit outside the happy path, making operations visible without confusing request ownership.
- Defect: exact owners, protocols, SLOs, and deployment gates are schematic unless supplied as source facts; final production should bind them to a real architecture source package.
- Defect: dense layer names may need a wider stack, wrapping, or a side legend in final delivery.
- Defect: the helper renders with Pillow and ffmpeg rather than browser-captured SVG frames; use it as an isolated-validation scaffold, then replace with a richer HTML/D3 renderer for final production.
- Skill lesson: architecture videos need layer ownership, request path, cross-cutting policy, failure, observability, and rollout mechanics, not only stacked boxes."""
    elif pattern == "data-lineage":
        critique = """- Strength: the video separates source lineage, transform rule, quality gate, drift monitor, consumer contract, and rollback route into distinct mechanisms.
- Strength: quality checks appear after transform context, so trust does not look like an automatic property of data movement.
- Strength: drift and rollback sit outside the happy path, making operational risk visible instead of hiding it in narration.
- Defect: exact datasets, owners, schema versions, freshness SLOs, and drift thresholds are schematic unless supplied as source facts; final production should bind them to real lineage metadata.
- Defect: dense dataset or table names may need wider nodes, wrapping, or a side legend in final delivery.
- Defect: the helper renders with Pillow and ffmpeg rather than browser-captured SVG frames; use it as an isolated-validation scaffold, then replace with a richer HTML/D3 renderer for final production.
- Skill lesson: data-lineage videos need provenance, transform ownership, quality gates, drift, consumer readiness, and rollback mechanics, not only a pipeline arrow."""
    else:
        critique = """- Strength: the video uses route growth rather than a static tree, so the passive-path mechanic is visible.
- Strength: damage, defense, and attribute meters give the viewer separate checkpoints instead of one vague highlight.
- Strength: the Atlas layer is spatially separated, which protects the distinction between character passives and endgame specialization.
- Strength: the keystone is rendered as a tradeoff diamond, not as a generic reward node.
- Defect: this draft uses simplified synthetic tree geometry rather than captured game UI, so it should not be presented as an exact Path of Exile 2 tree.
- Defect: labels are intentionally short for a silent draft, but narrated delivery should remove or reduce several labels.
- Defect: the helper renders with Pillow and ffmpeg rather than browser-captured SVG frames; use it as an isolated-validation scaffold, then replace with a richer HTML/D3 renderer for final production.
- Skill lesson: isolated video tasks need an executable starter path. A prose-only workflow lets agents ask for optional details instead of producing the requested MP4."""
    review = f"""# Self Review

MP4 path: `{paths["video"].as_posix()}`

- Duration: {duration} seconds target, {args.duration} seconds requested.
- Resolution: {stream.get("width", args.width)}x{stream.get("height", args.height)}.
- Frame rate: {stream.get("r_frame_rate", f"{args.fps}/1")}.
- File size: {size} bytes.
- Visual pattern: {pattern}.
- Source facts preserved: {len(args.fact)}.
- Strategy anchors preserved: {len(args.anchor)}.
- Contact sheet: {"created at `" + paths["contact_sheet"].as_posix() + "` with manifest `" + paths["contact_sheet_manifest"].as_posix() + "`" if contact_sheet else "not created or did not pass the metric gate"}.
- Render command: `uv run --script <skill-root>/scripts/build_standalone_explainer.py --project-root {args.project_root.as_posix()} --title "{args.title}" --output-id {args.output_id} --pattern {args.pattern}`.

## Critique

{critique}
"""
    paths["review"].write_text(review, encoding="utf-8")


def main() -> int:
    global EDGE_STYLE
    args = parse_args()
    EDGE_STYLE = args.edge_style
    if args.duration <= 0:
        print("--duration must be positive", file=sys.stderr)
        return 2
    if args.fps <= 0:
        print("--fps must be positive", file=sys.stderr)
        return 2

    paths = build_paths(args.project_root, args.output_id)
    for path in paths.values():
        path.parent.mkdir(parents=True, exist_ok=True)

    package = source_package(args, paths)
    write_json(paths["source_package"], package)
    write_notes(args, paths, package)
    write_html(args, paths, package)
    write_render_js(args, paths, package)
    render_video(args, paths)
    probe = run_ffprobe(paths["video"])
    contact_sheet = write_contact_sheet(paths)
    write_review(args, paths, probe, contact_sheet)

    required = [
        paths["source_package"],
        paths["production_notes"],
        paths["html"],
        paths["render_js"],
        paths["video"],
        paths["review"],
    ]
    missing = [str(path) for path in required if not path.exists() or path.stat().st_size <= 0]
    if missing:
        print("Missing required outputs:\n" + "\n".join(missing), file=sys.stderr)
        return 3
    print(json.dumps({key: str(value) for key, value in paths.items()}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
