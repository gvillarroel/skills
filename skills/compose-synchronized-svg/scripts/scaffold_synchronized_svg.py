#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

"""Create a standalone SVG shell from a synchronized-composition plan."""

from __future__ import annotations

import argparse
import colorsys
import copy
from decimal import Decimal, ROUND_HALF_UP, localcontext
import html
import json
import math
import re
import sys
import textwrap
from pathlib import Path
from typing import Any


sys.dont_write_bytecode = True

import navigation_contract as navigation  # noqa: E402

ID_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
ROLE_SELECTOR_RE = re.compile(r"^\[data-role=(?:'([^']+)'|\"([^\"]+)\")\]$")
OPS = {"add", "subtract", "multiply", "divide", "min", "max", "clamp", "round"}
CHANNELS = {"text", "x", "y", "width", "height", "r", "path", "transform", "opacity", "class", "aria-value"}
PALETTE = [
    "#1d4ed8",
    "#0f766e",
    "#6d28d9",
    "#b45309",
    "#15803d",
    "#be123c",
    "#4338ca",
    "#0e7490",
    "#a21caf",
    "#92400e",
    "#3f6212",
    "#475569",
    "#9f1239",
    "#5b21b6",
    "#166534",
    "#155e75",
]


def color_for_index(index: int) -> str:
    """Return a deterministic, dark, non-wrapping canonical color."""

    if index < 0:
        raise ValueError("color index must be nonnegative")
    if index < len(PALETTE):
        return PALETTE[index]
    generated_index = index - len(PALETTE) + 1
    hue = (generated_index * 0.618033988749895) % 1.0
    saturation = 0.58 + 0.04 * (generated_index % 3)
    lightness = 0.31

    def channel_luminance(channel: float) -> float:
        return channel / 12.92 if channel <= 0.04045 else ((channel + 0.055) / 1.055) ** 2.4

    while True:
        red, green, blue = colorsys.hls_to_rgb(hue, lightness, saturation)
        luminance = (
            0.2126 * channel_luminance(red)
            + 0.7152 * channel_luminance(green)
            + 0.0722 * channel_luminance(blue)
        )
        if 1.05 / (luminance + 0.05) >= 4.5 or lightness <= 0.16:
            break
        lightness -= 0.01
    return "#{:02x}{:02x}{:02x}".format(
        round(red * 255),
        round(green * 255),
        round(blue * 255),
    )
LOCAL_MARK_BASE_Y = 24.0
QUESTION_BASE_Y = 50.0
QUESTION_LINE_HEIGHT = 14.0
CLAIM_BASE_Y = 74.0
CLAIM_LINE_HEIGHT = 20.0
HEADER_BODY_GAP = 32.0
MAX_QUESTION_LINES = 2
MAX_CLAIM_LINES = 3
ROLE_SUFFIXES = {"label", "segment", "step", "band", "bar", "mark", "value", "node", "point", "slice"}
ROLE_LABEL_ALIASES = {
    "gross": "Gross Cash",
    "net": "Net Cash",
    "living": "Living Costs",
    "residual": "Flexible Cash",
    "tax needle": "Tax Rate",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Create a valid, self-contained synchronized SVG scaffold. Replace every "
            "data-placeholder module before release, then run validate_synchronized_svg.py."
        )
    )
    parser.add_argument("--spec", required=True, type=Path, help="Composition plan JSON")
    parser.add_argument("--output", required=True, type=Path, help="Exact SVG output path")
    parser.add_argument(
        "--fragments-dir",
        type=Path,
        help="Optional directory for one small editable module fragment per planned module",
    )
    parser.add_argument("--force", action="store_true", help="Replace an existing output file")
    parser.add_argument("--json", action="store_true", help="Print a JSON result")
    return parser.parse_args()


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def short_label(value: str, limit: int) -> str:
    text = str(value).strip()
    if len(text) <= limit:
        return text
    return text[: max(1, limit - 1)].rstrip() + "…"


def fmt(value: float) -> str:
    if not math.isfinite(value):
        raise ValueError("non-finite numeric output")
    return f"{value:.6f}".rstrip("0").rstrip(".") or "0"


def canonical_number_text(value: float) -> str:
    """Serialize canonical state without applying geometry precision."""

    value = float(value)
    if not math.isfinite(value):
        raise ValueError("non-finite canonical numeric output")
    if value == 0.0:
        return "0"
    if value.is_integer():
        return str(int(value))
    return repr(value)


def scientific_decimal_text(value: Decimal, significant_digits: int = 6) -> str:
    """Format a nonzero Decimal like en-US Intl scientific notation."""

    absolute = abs(value)
    with localcontext() as context:
        context.prec = max(32, significant_digits + 4)
        exponent = absolute.adjusted()
        quantum = Decimal(1).scaleb(exponent - significant_digits + 1)
        rounded = absolute.quantize(quantum, rounding=ROUND_HALF_UP)
        exponent = rounded.adjusted()
        mantissa = rounded.scaleb(-exponent)
        text = format(mantissa, "f").rstrip("0").rstrip(".")
    return f"{text}E{exponent}"


def load_plan(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise ValueError(f"spec file does not exist: {path}")
    try:
        plan = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"spec is not valid JSON: {exc}") from exc
    if not isinstance(plan, dict):
        raise ValueError("spec root must be a JSON object")
    return plan


def require_id(value: Any, label: str) -> str:
    if not isinstance(value, str) or not ID_RE.fullmatch(value):
        raise ValueError(f"{label} must be lowercase hyphen-case")
    return value


def require_text(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label} must be a non-empty string")
    return value.strip()


def validate_compute(node: Any, known: set[str], label: str) -> set[str]:
    if isinstance(node, (int, float)) and not isinstance(node, bool):
        if not math.isfinite(float(node)):
            raise ValueError(f"{label} contains a non-finite literal")
        return set()
    if not isinstance(node, dict):
        raise ValueError(f"{label} must use numeric literals, ref nodes, or op nodes")
    if set(node) == {"ref"}:
        ref = require_id(node["ref"], f"{label}.ref")
        if ref not in known:
            raise ValueError(f"{label} references unknown value {ref!r}")
        return {ref}
    op = node.get("op")
    args = node.get("args")
    if op not in OPS or not isinstance(args, list):
        raise ValueError(f"{label} has an unsupported computation node")
    if op == "subtract" and len(args) < 2:
        raise ValueError(f"{label} operation 'subtract' requires at least two arguments")
    if op == "divide" and len(args) != 2:
        raise ValueError(f"{label} operation 'divide' requires two arguments")
    if op == "clamp" and len(args) != 3:
        raise ValueError(f"{label} operation 'clamp' requires three arguments")
    if op == "round" and len(args) not in {1, 2}:
        raise ValueError(f"{label} operation 'round' requires one or two arguments")
    if op in {"add", "multiply", "min", "max"} and not args:
        raise ValueError(f"{label} operation {op!r} requires at least one argument")
    refs: set[str] = set()
    for index, arg in enumerate(args):
        refs.update(validate_compute(arg, known, f"{label}.args[{index}]"))
    return refs


def direct_divisor_refs(node: Any) -> set[str]:
    """Return source-like refs used directly as division denominators."""

    if not isinstance(node, dict):
        return set()
    refs: set[str] = set()
    if node.get("op") == "divide" and isinstance(node.get("args"), list) and len(node["args"]) == 2:
        denominator = node["args"][1]
        if isinstance(denominator, dict) and set(denominator) == {"ref"}:
            refs.add(str(denominator["ref"]))
    for argument in node.get("args", []):
        refs.update(direct_divisor_refs(argument))
    return refs


def validate_plan(plan: dict[str, Any]) -> None:
    if plan.get("version") != 1:
        raise ValueError("version must equal 1")
    require_id(plan.get("compositionId"), "compositionId")
    if not isinstance(plan.get("title"), str) or not plan["title"].strip():
        raise ValueError("title must be a non-empty string")
    if "subtitle" in plan and (
        not isinstance(plan["subtitle"], str) or not plan["subtitle"].strip()
    ):
        raise ValueError("optional subtitle must be a non-empty string")
    if not isinstance(plan.get("provenance"), str) or not plan["provenance"].strip():
        raise ValueError("provenance must be a non-empty visible evidence note")
    if plan.get("locale", "en-US") != "en-US":
        raise ValueError(
            "locale must be 'en-US'; the literal script-free formatter intentionally supports "
            "one deterministic locale so fallback and Intl runtime text cannot disagree"
        )
    view_box = plan.get("viewBox")
    if (
        not isinstance(view_box, list)
        or len(view_box) != 4
        or any(not isinstance(item, (int, float)) or isinstance(item, bool) for item in view_box)
        or float(view_box[2]) <= 0
        or float(view_box[3]) <= 0
    ):
        raise ValueError("viewBox must be [x, y, width, height] with positive dimensions")

    concepts = plan.get("concepts")
    if not isinstance(concepts, list) or not concepts:
        raise ValueError("concepts must be a non-empty array")
    known: set[str] = set()
    source_domains: dict[str, tuple[float, float] | None] = {}
    for index, concept in enumerate(concepts):
        if not isinstance(concept, dict):
            raise ValueError(f"concepts[{index}] must be an object")
        concept_id = require_id(concept.get("id"), f"concepts[{index}].id")
        if concept_id in known:
            raise ValueError(f"duplicate concept id: {concept_id}")
        known.add(concept_id)
        default = concept.get("default")
        if not isinstance(default, (int, float)) or isinstance(default, bool) or not math.isfinite(float(default)):
            raise ValueError(f"concept {concept_id!r} needs a finite numeric default")
        domain = concept.get("domain")
        if domain is not None and (
            not isinstance(domain, list)
            or len(domain) != 2
            or any(not isinstance(item, (int, float)) or isinstance(item, bool) for item in domain)
            or float(domain[0]) >= float(domain[1])
            or not float(domain[0]) <= float(default) <= float(domain[1])
        ):
            raise ValueError(f"concept {concept_id!r} has an invalid domain/default")
        if concept.get("interpolation", "linear") not in {"linear", "step"}:
            raise ValueError(f"concept {concept_id!r} interpolation must be linear or step")
        source_domains[concept_id] = (
            (float(domain[0]), float(domain[1])) if isinstance(domain, list) else None
        )

    derived = plan.get("derived", [])
    if not isinstance(derived, list):
        raise ValueError("derived must be an array")
    pending_ids: set[str] = set()
    for index, item in enumerate(derived):
        if not isinstance(item, dict):
            raise ValueError(f"derived[{index}] must be an object")
        item_id = require_id(item.get("id"), f"derived[{index}].id")
        if item_id in known or item_id in pending_ids:
            raise ValueError(f"duplicate derived id: {item_id}")
        pending_ids.add(item_id)
    all_ids = known | pending_ids
    dependencies: dict[str, set[str]] = {}
    for index, item in enumerate(derived):
        item_id = item["id"]
        refs = validate_compute(item.get("compute"), all_ids, f"derived[{index}].compute")
        for divisor_id in sorted(direct_divisor_refs(item.get("compute")) & known):
            divisor_domain = source_domains[divisor_id]
            if divisor_domain is None or divisor_domain[0] <= 0 <= divisor_domain[1]:
                raise ValueError(
                    f"derived value {item_id!r} divides by source {divisor_id!r}; "
                    "that source needs an explicit legal domain that excludes zero"
                )
        declared = item.get("dependsOn")
        if not isinstance(declared, list) or set(declared) != refs or len(declared) != len(set(declared)):
            raise ValueError(f"derived value {item_id!r} dependsOn must exactly match direct ref leaves")
        dependencies[item_id] = {ref for ref in refs if ref in pending_ids}
    remaining = dict(dependencies)
    resolved = set(known)
    while remaining:
        ready = sorted(item_id for item_id, deps in remaining.items() if deps <= resolved)
        if not ready:
            raise ValueError("derived dependency graph contains a cycle")
        for item_id in ready:
            resolved.add(item_id)
            del remaining[item_id]

    scenarios = plan.get("scenarios")
    if not isinstance(scenarios, list) or not scenarios:
        raise ValueError("scenarios must be a non-empty array")
    scenario_ids: set[str] = set()
    for index, scenario in enumerate(scenarios):
        scenario_id = require_id(scenario.get("id") if isinstance(scenario, dict) else None, f"scenarios[{index}].id")
        if scenario_id in scenario_ids:
            raise ValueError(f"duplicate scenario id: {scenario_id}")
        scenario_ids.add(scenario_id)
        values = scenario.get("values")
        if not isinstance(values, dict) or not values:
            raise ValueError(f"scenario {scenario_id!r} values must be a non-empty object")
        unknown = set(values) - known
        if unknown:
            raise ValueError(f"scenario {scenario_id!r} contains non-source values: {sorted(unknown)}")
    if plan.get("initialScenario") not in scenario_ids:
        raise ValueError("initialScenario must name a declared scenario")

    modules = plan.get("modules")
    if not isinstance(modules, list) or not modules:
        raise ValueError("modules must be a non-empty array")
    module_ids: set[str] = set()
    for index, module in enumerate(modules):
        if not isinstance(module, dict):
            raise ValueError(f"modules[{index}] must be an object")
        module_id = require_id(module.get("id"), f"modules[{index}].id")
        if module_id in module_ids:
            raise ValueError(f"duplicate module id: {module_id}")
        module_ids.add(module_id)
        require_id(module.get("assetType"), f"module {module_id!r} assetType")
        region = module.get("region")
        if (
            not isinstance(region, list)
            or len(region) != 4
            or any(not isinstance(item, (int, float)) or isinstance(item, bool) for item in region)
            or float(region[2]) <= 0
            or float(region[3]) <= 0
        ):
            raise ValueError(f"module {module_id!r} region must be [x, y, width, height]")
        if not isinstance(module.get("claim"), str) or not module["claim"].strip():
            raise ValueError(f"module {module_id!r} needs a claim")
        if not isinstance(module.get("question"), str) or not module["question"].strip():
            raise ValueError(f"module {module_id!r} needs a viewer question")
        for decision_field in ("selectionRationale", "rejectedAlternative"):
            decision = module.get(decision_field)
            if not isinstance(decision, str) or len(decision.strip()) < 12:
                raise ValueError(f"module {module_id!r} needs a specific {decision_field}")
        bindings = module.get("bindings")
        if not isinstance(bindings, list) or not bindings:
            raise ValueError(f"module {module_id!r} needs at least one binding")
        roles: set[tuple[str, str]] = set()
        for binding_index, binding in enumerate(bindings):
            if not isinstance(binding, dict):
                raise ValueError(f"module {module_id!r} binding {binding_index} must be an object")
            if binding.get("value") not in all_ids:
                raise ValueError(f"module {module_id!r} binding {binding_index} uses an unknown value")
            selector = binding.get("selector")
            match = ROLE_SELECTOR_RE.fullmatch(selector) if isinstance(selector, str) else None
            if not match:
                raise ValueError(
                    f"module {module_id!r} binding {binding_index} selector must be a local [data-role='...'] selector"
                )
            role = match.group(1) or match.group(2)
            channel = binding.get("channel")
            if channel not in CHANNELS:
                raise ValueError(f"module {module_id!r} binding {binding_index} has unsupported channel {channel!r}")
            if (role, channel) in roles:
                raise ValueError(f"module {module_id!r} repeats role/channel {role!r}/{channel!r}")
            roles.add((role, channel))
        diagram = module.get("diagram")
        if diagram is not None:
            if not isinstance(diagram, dict) or diagram.get("layout") not in {
                "tree",
                "radial",
                "lanes",
            }:
                raise ValueError(
                    f"module {module_id!r} diagram needs a tree, radial, or lanes layout"
                )
            nodes = diagram.get("nodes")
            links = diagram.get("links")
            if not isinstance(nodes, list) or len(nodes) < 2 or not isinstance(links, list) or not links:
                raise ValueError(
                    f"module {module_id!r} diagram needs at least two nodes and one link"
                )
            node_ids: set[str] = set()
            bound_values: set[str] = set()
            for node_index, node in enumerate(nodes):
                node_id = require_id(
                    node.get("id") if isinstance(node, dict) else None,
                    f"module {module_id!r} diagram.nodes[{node_index}].id",
                )
                if node_id in node_ids:
                    raise ValueError(
                        f"module {module_id!r} repeats diagram node id {node_id!r}"
                    )
                node_ids.add(node_id)
                require_text(node.get("label"), f"module {module_id!r} diagram node label")
                if node.get("bind") is not None:
                    if node["bind"] not in all_ids:
                        raise ValueError(
                            f"module {module_id!r} diagram node {node_id!r} binds an unknown value"
                        )
                    bound_values.add(str(node["bind"]))
            for link_index, link in enumerate(links):
                if not isinstance(link, dict):
                    raise ValueError(
                        f"module {module_id!r} diagram.links[{link_index}] must be an object"
                    )
                source = link.get("source")
                target = link.get("target")
                if source == target or source not in node_ids or target not in node_ids:
                    raise ValueError(
                        f"module {module_id!r} diagram link must connect distinct declared nodes"
                    )
            bound_module_values = {binding["value"] for binding in bindings}
            if bound_values != bound_module_values:
                raise ValueError(
                    f"module {module_id!r} structural diagram bound values differ from its bindings"
                )

    relationships = plan.get("relationships", [])
    if not isinstance(relationships, list):
        raise ValueError("relationships must be an array")
    if len(relationships) > 18:
        raise ValueError(
            "relationships supports at most 18 visible routes; reduce the graph to the explanatory spine"
        )
    relationship_ids: set[str] = set()
    relationship_edges: set[tuple[str, str, str]] = set()
    for index, relationship in enumerate(relationships):
        if not isinstance(relationship, dict):
            raise ValueError(f"relationships[{index}] must be an object")
        relationship_id = require_id(
            relationship.get("id"), f"relationships[{index}].id"
        )
        if relationship_id in relationship_ids:
            raise ValueError(f"duplicate relationship id: {relationship_id}")
        relationship_ids.add(relationship_id)
        source = relationship.get("source")
        target = relationship.get("target")
        if source not in module_ids or target not in module_ids or source == target:
            raise ValueError(
                f"relationship {relationship_id!r} must connect distinct declared modules"
            )
        kind = relationship.get("kind", "flow")
        if kind not in {"flow", "dependency", "feedback"}:
            raise ValueError(f"relationship {relationship_id!r} has an unsupported kind")
        require_text(relationship.get("label"), f"relationship {relationship_id!r} label")
        edge_key = (str(source), str(target), str(kind))
        if edge_key in relationship_edges:
            raise ValueError(
                f"duplicate relationship endpoints and kind: {source!r} -> {target!r} ({kind})"
            )
        relationship_edges.add(edge_key)

    layout = plan.get("layout")
    if not isinstance(layout, dict):
        raise ValueError("layout must be an object")
    require_id(layout.get("armature"), "layout.armature")
    safe_area = layout.get("safeArea")
    if (
        not isinstance(safe_area, list)
        or len(safe_area) != 4
        or any(not isinstance(item, (int, float)) or isinstance(item, bool) for item in safe_area)
        or float(safe_area[2]) <= 0
        or float(safe_area[3]) <= 0
    ):
        raise ValueError("layout.safeArea must be [x, y, width, height]")
    reading_order = layout.get("readingOrder")
    if not isinstance(reading_order, list) or len(reading_order) != len(module_ids) or set(reading_order) != module_ids:
        raise ValueError("layout.readingOrder must contain every module id exactly once")
    vx, vy, vw, vh = (float(item) for item in view_box)
    sx, sy, sw, sh = (float(item) for item in safe_area)
    navigation_plan = plan.get("navigation")
    containment = (
        navigation.rect(navigation_plan.get("worldBounds"), "navigation.worldBounds")
        if isinstance(navigation_plan, dict)
        else [vx, vy, vw, vh]
    )
    cx, cy, cw, ch = containment
    if sx < cx or sy < cy or sx + sw > cx + cw or sy + sh > cy + ch:
        raise ValueError(
            "layout.safeArea must stay inside navigation.worldBounds"
            if navigation_plan is not None
            else "layout.safeArea must stay inside viewBox"
        )
    for module in modules:
        mx, my, mw, mh = (float(item) for item in module["region"])
        if mx < sx or my < sy or mx + mw > sx + sw or my + mh > sy + sh:
            raise ValueError(f"module {module['id']!r} region must stay inside layout.safeArea")

    focus_groups = plan.get("focusGroups", [])
    if not isinstance(focus_groups, list):
        raise ValueError("focusGroups must be an array")
    focus_ids: set[str] = set()
    expected_focus_by_module: dict[str, list[str]] = {module_id: [] for module_id in module_ids}
    for index, focus in enumerate(focus_groups):
        focus_id = require_id(focus.get("id") if isinstance(focus, dict) else None, f"focusGroups[{index}].id")
        if focus_id in focus_ids:
            raise ValueError(f"duplicate focus group id: {focus_id}")
        focus_ids.add(focus_id)
        if not isinstance(focus.get("moduleIds"), list) or not set(focus["moduleIds"]) <= module_ids:
            raise ValueError(f"focus group {focus_id!r} references unknown modules")
        for module_id in focus["moduleIds"]:
            expected_focus_by_module[module_id].append(focus_id)
    for module in modules:
        module_id = module["id"]
        expected_focus = expected_focus_by_module[module_id]
        if module.get("focusGroups", []) != expected_focus:
            raise ValueError(
                f"module {module_id!r} focusGroups must exactly match top-level membership {expected_focus!r}"
            )
        if len(expected_focus) > 4:
            raise ValueError(
                f"module {module_id!r} belongs to {len(expected_focus)} focus groups; use at most four discoverable stories"
            )

    world = plan.get("world")
    if (world is None) != (navigation_plan is None):
        raise ValueError("world and navigation must either both be present or both be absent")
    if world is not None:
        if not isinstance(world, dict) or world.get("mode") != "navigable-atlas":
            raise ValueError("world.mode must equal navigable-atlas")
        if "navigation" not in plan.get("syncModes", []):
            raise ValueError("a world plan requires navigation in syncModes")
        navigation.validate_navigation(plan)
        viewport = navigation.rect(navigation_plan.get("viewport"), "navigation.viewport")
        if not navigation.contains([vx, vy, vw, vh], viewport):
            raise ValueError("navigation.viewport must stay inside the root viewBox")
        districts = world.get("districts")
        links = world.get("links")
        if not isinstance(districts, list) or len(districts) < 4:
            raise ValueError("world needs at least four districts")
        if not isinstance(links, list) or not links:
            raise ValueError("world needs a non-empty district link graph")
        district_ids: set[str] = set()
        district_modules: set[str] = set()
        for index, district in enumerate(districts):
            district_id = require_id(
                district.get("id") if isinstance(district, dict) else None,
                f"world.districts[{index}].id",
            )
            if district_id in district_ids:
                raise ValueError(f"duplicate world district id: {district_id}")
            district_ids.add(district_id)
            district_bounds = navigation.rect(
                district.get("bounds"), f"world district {district_id!r} bounds"
            )
            if not navigation.contains(containment, district_bounds):
                raise ValueError(f"world district {district_id!r} escapes worldBounds")
            assigned = district.get("moduleIds")
            if not isinstance(assigned, list) or not assigned or not set(assigned) <= module_ids:
                raise ValueError(f"world district {district_id!r} references unknown modules")
            if district_modules & set(assigned):
                raise ValueError("world districts must not share modules")
            district_modules.update(assigned)
        if district_modules != module_ids:
            raise ValueError("world districts must assign every module exactly once")
        if world.get("rootDistrictId") not in district_ids:
            raise ValueError("world.rootDistrictId must name a declared district")
        for module in modules:
            if module.get("districtId") not in district_ids:
                raise ValueError(f"world module {module['id']!r} needs a declared districtId")
        trunk_targets: list[str] = []
        for index, link in enumerate(links):
            if not isinstance(link, dict):
                raise ValueError(f"world.links[{index}] must be an object")
            if (
                link.get("source") not in district_ids
                or link.get("target") not in district_ids
                or link.get("source") == link.get("target")
            ):
                raise ValueError("world links must connect distinct declared districts")
            expected_roles = {"feedback"} if link.get("kind") == "feedback" else {"trunk", "crosslink"}
            if link.get("treeRole") not in expected_roles:
                raise ValueError(
                    f"world link {link.get('id')!r} has invalid treeRole {link.get('treeRole')!r}"
                )
            if link.get("treeRole") == "trunk":
                trunk_targets.append(str(link["target"]))
        expected_trunk_targets = district_ids - {str(world["rootDistrictId"])}
        if len(trunk_targets) != len(set(trunk_targets)) or set(trunk_targets) != expected_trunk_targets:
            raise ValueError("world trunk links must reach every non-root district exactly once")
        for stop in navigation_plan["route"]["stops"]:
            if stop.get("focusId") is not None and stop.get("focusId") not in focus_ids:
                raise ValueError(
                    f"navigation route stop {stop['id']!r} references an unknown focus group"
                )

    timeline = plan.get("timeline")
    if timeline is not None:
        if not isinstance(timeline, dict) or not isinstance(timeline.get("durationMs"), (int, float)):
            raise ValueError("timeline needs a numeric durationMs")
        duration = float(timeline["durationMs"])
        if duration <= 0:
            raise ValueError("timeline durationMs must be positive")
        if timeline.get("interpolation", "step") not in {"step", "linear", "smooth"}:
            raise ValueError("timeline interpolation must be step, linear, or smooth")
        if not isinstance(timeline.get("autoplay", False), bool):
            raise ValueError("timeline autoplay must be a boolean")
        if timeline.get("baseScenario") is not None and timeline.get("baseScenario") not in scenario_ids:
            raise ValueError("timeline baseScenario must name a declared scenario")
        phases = timeline.get("phases")
        if not isinstance(phases, list) or not phases:
            raise ValueError("timeline phases must be a non-empty array")
        cursor = 0.0
        for index, phase in enumerate(phases):
            phase_id = require_id(phase.get("id") if isinstance(phase, dict) else None, f"timeline.phases[{index}].id")
            start = phase.get("startMs")
            end = phase.get("endMs")
            if not isinstance(start, (int, float)) or not isinstance(end, (int, float)) or start != cursor or end <= start:
                raise ValueError(f"timeline phase {phase_id!r} must be ordered, contiguous, and positive")
            if phase.get("focusId") is not None and phase.get("focusId") not in focus_ids:
                raise ValueError(f"timeline phase {phase_id!r} references an unknown focus group")
            values = phase.get("values", {})
            if not isinstance(values, dict) or not set(values) <= known:
                raise ValueError(f"timeline phase {phase_id!r} values must contain source concepts only")
            cursor = float(end)
        if cursor != duration:
            raise ValueError("timeline phases must cover durationMs exactly")


def eval_node(node: Any, values: dict[str, float]) -> float:
    if isinstance(node, (int, float)) and not isinstance(node, bool):
        return float(node)
    if "ref" in node:
        return float(values[node["ref"]])
    op = node["op"]
    args = [eval_node(arg, values) for arg in node["args"]]
    if op == "add":
        result = 0.0
        for value in args:
            result += value
    elif op == "subtract":
        remainder = 0.0
        for value in args[1:]:
            remainder += value
        result = args[0] - remainder
    elif op == "multiply":
        result = 1.0
        for value in args:
            result *= value
    elif op == "divide":
        if args[1] == 0:
            raise ValueError("derived computation divides by zero")
        result = args[0] / args[1]
    elif op == "min":
        result = min(args)
    elif op == "max":
        result = max(args)
    elif op == "clamp":
        result = min(max(args[0], args[1]), args[2])
    elif op == "round":
        digits = int(args[1]) if len(args) == 2 else 0
        factor = 10.0**digits
        result = math.floor((args[0] + sys.float_info.epsilon) * factor + 0.5) / factor
        if result == 0.0:
            result = 0.0
    else:  # pragma: no cover - guarded by validation
        raise ValueError(f"unsupported operation: {op}")
    if not math.isfinite(result):
        raise ValueError("derived computation produced a non-finite result")
    return result


def initial_values(plan: dict[str, Any]) -> tuple[dict[str, float], dict[str, float]]:
    source = {item["id"]: float(item["default"]) for item in plan["concepts"]}
    scenario = next(item for item in plan["scenarios"] if item["id"] == plan["initialScenario"])
    source.update({key: float(value) for key, value in scenario["values"].items()})
    all_values = dict(source)
    pending = {item["id"]: item for item in plan.get("derived", [])}
    derived: dict[str, float] = {}
    while pending:
        progressed = False
        for item_id, item in list(pending.items()):
            if set(item["dependsOn"]) <= set(all_values):
                value = eval_node(item["compute"], all_values)
                all_values[item_id] = value
                derived[item_id] = value
                del pending[item_id]
                progressed = True
        if not progressed:  # pragma: no cover - guarded by validation
            raise ValueError("could not resolve derived values")
    return source, derived


def transformed_value(value: float, transform: Any) -> float | str:
    if transform is None:
        return value
    if not isinstance(transform, dict):
        raise ValueError("binding transform must be an object")
    op = transform.get("op")
    if op == "linear":
        domain = transform.get("domain")
        target = transform.get("range")
        if not isinstance(domain, list) or len(domain) != 2 or not isinstance(target, list) or len(target) != 2:
            raise ValueError("linear transform needs two-value domain and range")
        t = (value - float(domain[0])) / (float(domain[1]) - float(domain[0]))
        if transform.get("clamp"):
            t = min(max(t, 0.0), 1.0)
        return float(target[0]) + t * (float(target[1]) - float(target[0]))
    if op == "rotate":
        domain = transform.get("domain")
        target = transform.get("range")
        center = transform.get("center", [0, 0])
        if not isinstance(domain, list) or len(domain) != 2 or not isinstance(target, list) or len(target) != 2:
            raise ValueError("rotate transform needs two-value domain and range")
        t = (value - float(domain[0])) / (float(domain[1]) - float(domain[0]))
        if transform.get("clamp"):
            t = min(max(t, 0.0), 1.0)
        angle = float(target[0]) + t * (float(target[1]) - float(target[0]))
        return f"rotate({fmt(angle)} {fmt(float(center[0]))} {fmt(float(center[1]))})"
    if op in {None, "identity"}:
        return value
    raise ValueError(f"unsupported binding transform: {op!r}")


def format_value(value: float, format_spec: Any, locale: str) -> str:
    if locale != "en-US":
        raise ValueError("literal formatting supports only the validated en-US locale")
    if not isinstance(format_spec, dict):
        return canonical_number_text(value)
    style = format_spec.get("style", "decimal")
    default_digits = 2 if style == "currency" else (0 if style == "percent" else 3)
    digits = int(format_spec.get("maximumFractionDigits", default_digits))
    if not 0 <= digits <= 20:
        raise ValueError("maximumFractionDigits must be between 0 and 20")
    default_minimum = min(2, digits) if style == "currency" else 0
    minimum_digits = int(format_spec.get("minimumFractionDigits", default_minimum))
    if not 0 <= minimum_digits <= digits:
        raise ValueError("minimumFractionDigits must be between zero and maximumFractionDigits")
    suffix = str(format_spec.get("suffix", ""))
    decimal_value = Decimal(str(value))
    if style == "percent":
        decimal_value *= Decimal(100)
    quantum = Decimal(1).scaleb(-digits)
    rounded = decimal_value.quantize(quantum, rounding=ROUND_HALF_UP)
    if decimal_value != 0 and rounded == 0:
        scientific = scientific_decimal_text(decimal_value)
        negative = decimal_value.is_signed()
        sign = "-" if negative else ""
        if style == "currency":
            currency = str(format_spec.get("currency", "USD"))
            symbols = {
                "USD": "$",
                "EUR": "€",
                "GBP": "£",
                "JPY": "¥",
                "CNY": "CN¥",
                "CAD": "CA$",
                "AUD": "A$",
            }
            symbol = symbols.get(currency, f"{currency}\u00a0")
            return f"{sign}{symbol}{scientific}{suffix}"
        if style == "percent":
            return f"{sign}{scientific}%{suffix}"
        return f"{sign}{scientific}{suffix}"
    negative = rounded.is_signed() and rounded != 0
    rendered = f"{abs(rounded):,.{digits}f}"
    if "." in rendered and digits > minimum_digits:
        integer, fraction = rendered.split(".", 1)
        while len(fraction) > minimum_digits and fraction.endswith("0"):
            fraction = fraction[:-1]
        rendered = integer if not fraction else f"{integer}.{fraction}"
    if style == "currency":
        currency = str(format_spec.get("currency", "USD"))
        symbols = {
            "USD": "$",
            "EUR": "€",
            "GBP": "£",
            "JPY": "¥",
            "CNY": "CN¥",
            "CAD": "CA$",
            "AUD": "A$",
        }
        symbol = symbols.get(currency, f"{currency}\u00a0")
        sign = "-" if negative else ""
        return f"{sign}{symbol}{rendered}{suffix}"
    if style == "percent":
        sign = "-" if negative else ""
        return f"{sign}{rendered}%{suffix}"
    sign = "-" if negative else ""
    return f"{sign}{rendered}{suffix}"


def role_for(selector: str) -> str:
    match = ROLE_SELECTOR_RE.fullmatch(selector)
    if not match:  # pragma: no cover - guarded by validation
        raise ValueError(f"unsupported selector: {selector}")
    return match.group(1) or match.group(2)


def humanize_role(role: str) -> str:
    """Turn a binding role into concise viewer-facing copy."""

    tokens = [token for token in re.split(r"[-_\s]+", role.strip().lower()) if token]
    while len(tokens) > 1 and tokens[-1] in ROLE_SUFFIXES:
        tokens.pop()
    if not tokens:
        return "Value"
    phrase = " ".join(tokens)
    return ROLE_LABEL_ALIASES.get(phrase, phrase.title())


def wrap_claim(text: str, width: float) -> list[str]:
    max_chars = max(24, min(74, int(width / 8.6)))
    return textwrap.wrap(text, width=max_chars, break_long_words=False) or [text]


def wrap_question(text: str, width: float) -> list[str]:
    max_chars = max(28, min(96, int(width / 6.2)))
    return textwrap.wrap(text, width=max_chars, break_long_words=False) or [text]


def copy_content_top(question_count: int, claim_count: int) -> float:
    return (
        CLAIM_BASE_Y
        + QUESTION_LINE_HEIGHT * (question_count - 1)
        + CLAIM_LINE_HEIGHT * (claim_count - 1)
        + HEADER_BODY_GAP
    )


def ellipsize_wrapped_lines(lines: list[str], count: int) -> tuple[list[str], bool]:
    """Return an explicit, width-neutral truncation when not every line fits."""

    selected = list(lines[:count])
    truncated = count < len(lines)
    if truncated:
        final_line = selected[-1].rstrip()
        if final_line.endswith("..."):
            final_line = final_line[:-3].rstrip()
        elif final_line.endswith("…"):
            final_line = final_line[:-1].rstrip()
        elif len(final_line) > 1:
            final_line = final_line[:-1].rstrip()
        selected[-1] = f"{final_line}…" if final_line else "…"
    return selected, truncated


def module_copy_layout(
    module: dict[str, Any],
) -> tuple[list[str], list[str], bool, bool, float, float, float]:
    """Fit header copy within the stable body-shell boundary."""

    _, _, width, height = (float(item) for item in module["region"])
    all_claim_lines = wrap_claim(module["claim"], width - 48)
    all_question_lines = wrap_question(module["question"], width - 48)
    # These limits are the exact public body-shell contract reconstructed by
    # replace_svg_module.py. Keeping them here prevents a header change from
    # invalidating deterministic fragment replacement. Copy beyond the bound is
    # never dropped silently: the final visible line receives an ellipsis and
    # module_markup exposes the full source string to assistive technology.
    question_count = min(len(all_question_lines), MAX_QUESTION_LINES)
    claim_count = min(len(all_claim_lines), MAX_CLAIM_LINES)

    question_lines, question_truncated = ellipsize_wrapped_lines(all_question_lines, question_count)
    claim_lines, claim_truncated = ellipsize_wrapped_lines(all_claim_lines, claim_count)
    content_top = copy_content_top(len(question_lines), len(claim_lines))
    content_height = height - content_top
    if content_height <= 0:
        raise ValueError(f"module {module['id']!r} has no positive content body below its question and claim")
    return (
        claim_lines,
        question_lines,
        claim_truncated,
        question_truncated,
        content_top,
        width,
        content_height,
    )


def module_content_geometry(module: dict[str, Any]) -> tuple[list[str], list[str], float, float, float]:
    """Return wrapped copy and the module-local body rectangle."""

    claim_lines, question_lines, _, _, content_top, width, content_height = module_copy_layout(module)
    return claim_lines, question_lines, content_top, width, content_height


def mark_markup(
    module: dict[str, Any],
    binding: dict[str, Any],
    index: int,
    values: dict[str, float],
    locale: str,
    base_y: float,
) -> str:
    role = role_for(binding["selector"])
    channel = binding["channel"]
    raw = values[binding["value"]]
    rendered = transformed_value(raw, binding.get("transform"))
    y = base_y + index * 30
    common = (
        f'id="{esc(module["id"])}-{esc(role)}-{index}" data-role="{esc(role)}" '
        f'data-bind="{esc(binding["value"])}" data-channel="{esc(channel)}" '
        f'data-current-value="{esc(canonical_number_text(raw))}" data-sync-revision="0"'
    )
    label = esc(humanize_role(role))
    if channel == "text":
        text = esc(format_value(raw, binding.get("format"), locale))
        return f'<text {common} class="placeholder-value" x="28" y="{fmt(y)}">{label}: {text}</text>'
    if channel == "width":
        width = max(1.0, float(rendered))
        return f'<rect {common} class="placeholder-mark" x="28" y="{fmt(y - 14)}" width="{fmt(width)}" height="14"><title>{label}</title></rect>'
    if channel == "height":
        height = max(1.0, float(rendered))
        return f'<rect {common} class="placeholder-mark" x="28" y="{fmt(y - min(height, 24))}" width="18" height="{fmt(height)}"><title>{label}</title></rect>'
    if channel == "r":
        radius = max(1.0, float(rendered))
        return f'<circle {common} class="placeholder-mark" cx="48" cy="{fmt(y - 5)}" r="{fmt(radius)}"><title>{label}</title></circle>'
    if channel == "transform":
        return f'<g {common} class="placeholder-mark" transform="{esc(rendered)}"><line x1="28" y1="{fmt(y)}" x2="88" y2="{fmt(y)}" stroke-width="5"/></g>'
    if channel == "opacity":
        return f'<circle {common} class="placeholder-mark" cx="48" cy="{fmt(y - 5)}" r="12" opacity="{esc(fmt(float(rendered)))}"><title>{label}</title></circle>'
    if channel in {"x", "y"}:
        fixed = "y" if channel == "x" else "x"
        fixed_value = y if channel == "x" else 48
        return f'<circle {common} class="placeholder-mark" {channel}="{esc(fmt(float(rendered)))}" {fixed}="{fmt(fixed_value)}" r="9"><title>{label}</title></circle>'
    if channel == "path":
        return f'<path {common} class="placeholder-mark" d="M28 {fmt(y)} H128"><title>{label}</title></path>'
    if channel == "class":
        return f'<g {common} class="placeholder-mark"><circle cx="48" cy="{fmt(y - 5)}" r="10"/><title>{label}</title></g>'
    if channel == "aria-value":
        return f'<g {common} class="placeholder-mark" role="meter" aria-valuenow="{esc(canonical_number_text(raw))}"><rect x="28" y="{fmt(y - 14)}" width="100" height="14"/><title>{label}</title></g>'
    return f'<g {common} class="placeholder-mark"><title>{label}</title></g>'


def module_markup(
    module: dict[str, Any],
    values: dict[str, float],
    locale: str,
    focus_labels: dict[str, str] | None = None,
) -> str:
    x, y, width, height = (float(item) for item in module["region"])
    (
        lines,
        question_lines,
        claim_truncated,
        question_truncated,
        content_top,
        content_width,
        content_height,
    ) = module_copy_layout(module)
    question_accessible = f' aria-label="{esc(module["question"])}"' if question_truncated else ""
    claim_accessible = f' aria-label="{esc(module["claim"])}"' if claim_truncated else ""
    question = [
        f'<text class="module-question" x="24" y="{fmt(QUESTION_BASE_Y)}"{question_accessible}>'
        f'{esc(question_lines[0])}'
    ]
    for line in question_lines[1:]:
        question.append(f'<tspan x="24" dy="{fmt(QUESTION_LINE_HEIGHT)}">{esc(line)}</tspan>')
    question.append("</text>")
    claim_y = CLAIM_BASE_Y + QUESTION_LINE_HEIGHT * (len(question_lines) - 1)
    claim = [f'<text class="module-claim" x="24" y="{fmt(claim_y)}"{claim_accessible}>{esc(lines[0])}']
    for index, line in enumerate(lines[1:], start=1):
        claim.append(f'<tspan x="24" dy="{fmt(CLAIM_LINE_HEIGHT)}">{esc(line)}</tspan>')
    claim.append("</text>")
    marks = [
        mark_markup(module, binding, index, values, locale, LOCAL_MARK_BASE_Y)
        for index, binding in enumerate(module["bindings"])
    ]
    kicker_label = module["assetType"].replace("-", " ").upper()
    kicker_display = kicker_label
    focus = " ".join(module.get("focusGroups", []))
    focus_ids = list(module.get("focusGroups", []))
    focus_controls: list[str] = []
    if focus_ids:
        control_gap = 4.0
        reserved_kicker = 72.0
        minimum_control_width = max(28.0, 52.0 - 8.0 * len(focus_ids))
        available_controls = width - reserved_kicker - 18.0 - control_gap * (len(focus_ids) - 1)
        maximum_control_width = 104.0 if len(focus_ids) <= 2 else 74.0
        control_width = min(
            maximum_control_width,
            max(minimum_control_width, available_controls / len(focus_ids)),
        )
        total_width = len(focus_ids) * control_width + (len(focus_ids) - 1) * control_gap
        control_start = width - total_width - 18.0
        kicker_limit = max(4, int(max(24.0, control_start - 32.0) / 6.2))
        kicker_display = short_label(kicker_label, kicker_limit)
        focus_words = {
            focus_id: (focus_labels or {}).get(
                focus_id,
                focus_id.replace("-", " ").title(),
            ).split()
            for focus_id in focus_ids
        }
        word_counts: dict[str, int] = {}
        for words in focus_words.values():
            for word in {word.casefold() for word in words}:
                word_counts[word] = word_counts.get(word, 0) + 1
        for index, focus_id in enumerate(focus_ids):
            focus_label = (focus_labels or {}).get(
                focus_id,
                focus_id.replace("-", " ").title(),
            )
            words = focus_words[focus_id]
            visible_word = next(
                (word for word in words if word_counts.get(word.casefold()) == 1),
                focus_id.split("-")[-1].title(),
            )
            visible_label = short_label(
                visible_word,
                max(3, int((control_width - 12.0) / 5.5)),
            )
            control_x = control_start + index * (control_width + control_gap)
            focus_controls.append(
                f'<g id="module-focus-toggle-{esc(module["id"])}-{esc(focus_id)}" '
                f'class="interactive-control module-focus-control" '
                f'data-module-focus-id="{esc(focus_id)}" '
                f'transform="translate({fmt(control_x)} 12)" tabindex="0" role="button" '
                f'aria-label="Toggle {esc(focus_label)} focus for {esc(module["claim"])}" '
                f'aria-pressed="false">'
                f'<rect width="{fmt(control_width)}" height="22" rx="11"/>'
                f'<text x="{fmt(control_width / 2)}" y="15" text-anchor="middle">'
                f'{esc(visible_label)}</text></g>'
            )
    focus_control = "".join(focus_controls)
    module_id = esc(module["id"])
    district_id = esc(str(module.get("districtId", "")))
    district_accent = esc(str(module.get("districtAccent", "#2563eb")))
    navigation_anchor = (
        f' data-nav-anchor-id="module-{module_id}"' if module.get("districtId") else ""
    )
    question_markup = "".join(question)
    claim_markup = "".join(claim)
    marks_markup = "\n      ".join(marks)
    return f'''<!-- sync-module-start:{module_id} -->
<g id="module-{module_id}" class="sync-module" transform="translate({fmt(x)} {fmt(y)})"
   data-module-id="{module_id}" data-asset-type="{esc(module["assetType"])}"
   data-district-id="{district_id}"{navigation_anchor}
   style="--district-accent: {district_accent};"
   data-focus-group="{esc(focus)}" data-placeholder="true"
   data-content-top="{fmt(content_top)}"
   role="group"
   aria-labelledby="module-title-{module_id}" aria-describedby="module-question-full-{module_id}">
  <title id="module-title-{module_id}">{esc(module["claim"])}</title>
  <desc id="module-question-full-{module_id}">{esc(module["question"])}</desc>
  <rect class="module-frame" width="{fmt(width)}" height="{fmt(height)}"/>
  {focus_control}
  <text class="module-kicker" x="24" y="30" aria-label="{esc(kicker_label)}">{esc(kicker_display)}</text>
  {question_markup}
  {claim_markup}
  <!-- sync-content-start:{module_id} -->
  <g class="module-content module-placeholder" transform="translate(0 {fmt(content_top)})"
     data-module-content-for="{module_id}" data-content-origin="0 {fmt(content_top)}"
     data-content-width="{fmt(content_width)}" data-content-height="{fmt(content_height)}"
     aria-label="Structural placeholder for {esc(module["assetType"])}">
      {marks_markup}
  </g>
  <!-- sync-content-end:{module_id} -->
</g>
<!-- sync-module-end:{module_id} -->'''


def focus_region_markup(plan: dict[str, Any]) -> tuple[str, str]:
    """Render honest contiguous focus regions in background and label layers.

    Labels use an opaque cartographic plaque and render after relationship paths.
    This keeps region names legible without pretending a connector clears text when
    it merely happens to be painted underneath it.
    """

    modules = {item["id"]: item for item in plan["modules"]}
    all_modules = list(plan["modules"])
    fills = ("#dbeafe", "#dcfce7", "#fef3c7", "#f3e8ff")
    strokes = ("#93c5fd", "#86efac", "#fcd34d", "#d8b4fe")
    backgrounds: list[str] = []
    labels: list[str] = []
    seen_geometry: set[tuple[float, float, float, float]] = set()
    for index, focus in enumerate(plan.get("focusGroups", [])):
        selected = [modules[module_id] for module_id in focus.get("moduleIds", []) if module_id in modules]
        if len(selected) < 2:
            continue
        regions = [[float(value) for value in module["region"]] for module in selected]
        same_row = len({round(region[1], 6) for region in regions}) == 1 and len(
            {round(region[3], 6) for region in regions}
        ) == 1
        same_column = len({round(region[0], 6) for region in regions}) == 1 and len(
            {round(region[2], 6) for region in regions}
        ) == 1
        if not (same_row or same_column):
            continue
        left = min(region[0] for region in regions)
        top = min(region[1] for region in regions)
        right = max(region[0] + region[2] for region in regions)
        bottom = max(region[1] + region[3] for region in regions)
        selected_ids = {module["id"] for module in selected}
        outsider_inside = False
        for module in all_modules:
            if module["id"] in selected_ids:
                continue
            x, y, width, height = (float(value) for value in module["region"])
            center_x, center_y = x + width / 2, y + height / 2
            if left <= center_x <= right and top <= center_y <= bottom:
                outsider_inside = True
                break
        if outsider_inside:
            continue
        geometry_key = tuple(round(value, 4) for value in (left, top, right, bottom))
        if geometry_key in seen_geometry:
            continue
        seen_geometry.add(geometry_key)
        padding = 8.0
        region_id = require_id(focus["id"], "focus region id")
        label = str(focus.get("label", region_id.replace("-", " ").title()))
        full_label_text = label.upper()
        label_x = left + 8.0
        # Fill the inter-row gutter without touching either module row. For the
        # first row this also leaves a clean gap below the master timeline.
        label_y = top - 8.0
        # Inter 10 px uppercase plus 0.1em tracking. Overestimate slightly so the
        # opaque plaque fully covers the browser-measured text box on fallback fonts.
        # Budget for wide uppercase and fallback glyphs, including 0.1em tracking.
        # The browser audit still verifies the exact rendered bounds.
        label_advance_budget = 11.5
        max_label_chars = max(
            8,
            int(max(60.0, right - label_x - 8.0) / label_advance_budget),
        )
        label_text = full_label_text
        if len(label_text) > max_label_chars:
            label_text = label_text[: max(1, max_label_chars - 1)].rstrip() + "…"
        plaque_width = max(36.0, len(label_text) * label_advance_budget + 16.0)
        backgrounds.append(
            f'<rect class="focus-region" data-focus-region="{esc(region_id)}" '
            f'x="{fmt(left - padding)}" y="{fmt(top - padding)}" '
            f'width="{fmt(right - left + 2 * padding)}" '
            f'height="{fmt(bottom - top + 2 * padding)}" fill="{fills[index % len(fills)]}" '
            f'fill-opacity="0.34" stroke="{strokes[index % len(strokes)]}" stroke-width="1" rx="12"/>'
        )
        labels.append(
            f'<g class="focus-region-label-group" data-focus-label-for="{esc(region_id)}">'
            f'<title>Focus region: {esc(full_label_text)}</title>'
            f'<rect class="focus-region-label-plaque" x="{fmt(label_x - 8.0)}" '
            f'y="{fmt(label_y - 15.0)}" width="{fmt(plaque_width)}" height="22" rx="3"/>'
            f'<text class="focus-region-label" data-clearance-mask="true" '
            f'x="{fmt(label_x)}" y="{fmt(label_y)}">{esc(label_text)}</text></g>'
        )
    if not backgrounds:
        return "", ""
    background_markup = (
        '<g id="composition-focus-regions" aria-hidden="true" pointer-events="none">'
        + "".join(backgrounds)
        + "</g>"
    )
    label_markup = (
        '<g id="composition-focus-region-labels" aria-hidden="true" pointer-events="none">'
        + "".join(labels)
        + "</g>"
    )
    return background_markup, label_markup


def fragment_markup(module: dict[str, Any], values: dict[str, float], locale: str) -> str:
    _, _, content_top, content_width, content_height = module_content_geometry(module)
    marks = [
        mark_markup(module, binding, index, values, locale, LOCAL_MARK_BASE_Y)
        for index, binding in enumerate(module["bindings"])
    ]
    marks_markup = "\n  ".join(marks)
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<g xmlns="http://www.w3.org/2000/svg" class="module-content"
   transform="translate(0 {fmt(content_top)})"
   data-module-content-for="{esc(module['id'])}" data-content-origin="0 {fmt(content_top)}"
   data-content-width="{fmt(content_width)}" data-content-height="{fmt(content_height)}"
   data-placeholder="true">
  <title>Editable content fragment for {esc(module['id'])}</title>
  <!-- Replace the generic marks with the selected {esc(module['assetType'])} geometry. -->
  <!-- Preserve every data-role, data-bind, data-channel, data-current-value, and data-sync-revision contract. -->
  <!-- Remove data-placeholder="true" from this root only after the visual is complete. -->
  {marks_markup}
</g>
'''


def button_markup(
    control_id: str,
    label: str,
    x: float,
    y: float,
    width: float,
    attributes: str,
) -> str:
    return (
        f'<g id="{esc(control_id)}" class="interactive-control control-button" transform="translate({fmt(x)} {fmt(y)})" '
        f'tabindex="0" role="button" {attributes}>'
        f'<rect width="{fmt(width)}" height="30"/><text x="{fmt(width / 2)}" y="20" text-anchor="middle">{esc(label)}</text></g>'
    )


def relationship_markup(plan: dict[str, Any]) -> str:
    relationships = plan.get("relationships", [])
    if not relationships:
        return ""
    modules = {module["id"]: module for module in plan["modules"]}
    marker_id = f"{plan['compositionId']}--relationship-arrow"
    parts = [
        '<g id="composition-relationships" class="composition-relationships" '
        'aria-label="Causal and feedback relationships">',
        f'<defs><marker id="{esc(marker_id)}" viewBox="0 0 8 8" refX="7" refY="4" '
        'markerWidth="8" markerHeight="8" markerUnits="userSpaceOnUse" orient="auto"><path d="M0 0 L8 4 L0 8 Z" '
        'fill="context-stroke"/></marker></defs>',
    ]
    safe_x = float(plan["layout"]["safeArea"][0])
    safe_right = safe_x + float(plan["layout"]["safeArea"][2])
    route_bounds = (
        plan.get("navigation", {}).get("worldBounds")
        if isinstance(plan.get("navigation"), dict)
        else plan["viewBox"]
    )
    root_x, root_y, root_width, root_height = (float(value) for value in route_bounds)
    root_right = root_x + root_width
    declared_gap = float(plan["layout"].get("gap", 24))
    key_columns = min(6, max(3, math.ceil(len(relationships) / 3)))
    key_rows = math.ceil(len(relationships) / key_columns)
    key_cell_width = (root_width - 96.0) / key_columns
    key_start_y = root_y + root_height - (key_rows - 1) * 14.0 - 8.0
    key_plaque_top = key_start_y - 11.0
    incident_ids: dict[str, list[str]] = {module_id: [] for module_id in modules}
    for relationship in relationships:
        incident_ids[relationship["source"]].append(relationship["id"])
        incident_ids[relationship["target"]].append(relationship["id"])
    for values in incident_ids.values():
        values.sort()
    module_order = {module["id"]: index for index, module in enumerate(plan["modules"])}
    module_order_midpoint = (len(module_order) - 1) / 2.0

    def port_offset(module_id: str, relationship_id: str) -> float:
        values = incident_ids[module_id]
        if len(values) <= 1:
            local_offset = 0.0
        else:
            index = values.index(relationship_id)
            local_offset = (index - (len(values) - 1) / 2) * 18.0
        # Shift every port on one module by the same small reading-order bias.
        # Local marker spacing remains exactly 18px, while vertically aligned
        # modules cannot emit collinear entry/exit arms into the same row gap.
        module_bias = (module_order[module_id] - module_order_midpoint) * 1.5
        return local_offset + module_bias

    relationship_count = max(1, len(relationships))

    def lane_fraction(lane: int) -> float:
        """Return a unique deterministic fraction for every declared route."""

        return (lane + 1.0) / (relationship_count + 1.0)

    def gap_lane_offset(lane: int) -> float:
        """Distribute route lanes across the usable row-gap band without reuse."""

        usable = max(2.0, declared_gap - 3.0)
        return 1.0 + usable * lane_fraction(lane)

    def lower_gap_lane(boundary_y: float, lane: int) -> float:
        """Keep cross-row routes in the lower, label-free band of a row gap."""

        return boundary_y - gap_lane_offset(lane)

    def above_row_lane(boundary_y: float, lane: int) -> float:
        """Allocate unique feedback lanes above a row without post-allocation clamping."""

        first_lane = max(root_y + 8.0, 112.0)
        last_lane = max(first_lane, boundary_y - 1.0)
        return first_lane + (last_lane - first_lane) * lane_fraction(lane)

    def outer_lane_x(use_right: bool, lane: int) -> float:
        """Allocate unique side-gutter lanes while remaining inside the viewBox."""

        if use_right:
            available = max(2.0, root_right - safe_right - 12.0)
            return min(root_right - 8.0, safe_right + 4.0 + available * lane_fraction(lane))
        available = max(2.0, safe_x - root_x - 12.0)
        return max(root_x + 8.0, safe_x - 4.0 - available * lane_fraction(lane))

    def below_last_row_lane(boundary_y: float, lane: int) -> float:
        """Stay in the real band between the final row and relationship key."""

        first_lane = boundary_y + 1.0
        last_lane = max(first_lane, key_plaque_top - 3.0)
        return first_lane + (last_lane - first_lane) * lane_fraction(lane)

    for relationship_index, relationship in enumerate(relationships):
        route_lane = relationship_index
        raw_relationship_id = relationship["id"]
        source = modules[relationship["source"]]["region"]
        target = modules[relationship["target"]]["region"]
        sx, sy, sw, sh = (float(value) for value in source)
        tx, ty, tw, th = (float(value) for value in target)
        source_port = port_offset(relationship["source"], raw_relationship_id)
        target_port = port_offset(relationship["target"], raw_relationship_id)
        source_center_x = sx + sw / 2 + source_port
        target_center_x = tx + tw / 2 + target_port
        source_center_y = sy + sh / 2 + source_port
        target_center_y = ty + th / 2 + target_port
        kind = relationship.get("kind", "flow")
        if kind == "feedback":
            gap_offset = gap_lane_offset(route_lane)
            if abs(sy - ty) < 1e-6:
                lane_y = above_row_lane(sy, route_lane)
                path = (
                    f"M{fmt(source_center_x)} {fmt(sy)} V{fmt(lane_y)} "
                    f"H{fmt(target_center_x)} V{fmt(ty)}"
                )
            elif ty > sy:
                use_right = (source_center_x + target_center_x) / 2 >= (safe_x + safe_right) / 2
                outer_x = outer_lane_x(use_right, route_lane)
                source_lane_y = sy + sh + gap_offset
                target_lane_y = lower_gap_lane(ty, route_lane)
                path = (
                    f"M{fmt(source_center_x)} {fmt(sy + sh)} V{fmt(source_lane_y)} "
                    f"H{fmt(outer_x)} V{fmt(target_lane_y)} "
                    f"H{fmt(target_center_x)} V{fmt(ty)}"
                )
            else:
                use_right = (source_center_x + target_center_x) / 2 >= (safe_x + safe_right) / 2
                outer_x = outer_lane_x(use_right, route_lane)
                source_lane_y = lower_gap_lane(sy, route_lane)
                target_lane_y = ty + th + gap_offset
                path = (
                    f"M{fmt(source_center_x)} {fmt(sy)} V{fmt(source_lane_y)} "
                    f"H{fmt(outer_x)} V{fmt(target_lane_y)} "
                    f"H{fmt(target_center_x)} V{fmt(ty + th)}"
                )
        elif abs(sy - ty) < 1e-6:
            if tx >= sx:
                start_x, end_x = sx + sw, tx
            else:
                start_x, end_x = sx, tx + tw
            between_left, between_right = sorted((start_x, end_x))
            blocked = any(
                module["id"] not in {relationship["source"], relationship["target"]}
                and abs(float(module["region"][1]) - sy) < 1e-6
                and between_left
                < float(module["region"][0]) + float(module["region"][2]) / 2
                < between_right
                for module in plan["modules"]
            )
            if blocked:
                lower_rows = [
                    float(module["region"][1])
                    for module in plan["modules"]
                    if float(module["region"][1]) > sy + 1e-6
                ]
                bottom_band = key_plaque_top - (sy + sh)
                if not lower_rows and bottom_band < 8.0:
                    lane_y = lower_gap_lane(sy, route_lane)
                    path = (
                        f"M{fmt(source_center_x)} {fmt(sy)} V{fmt(lane_y)} "
                        f"H{fmt(target_center_x)} V{fmt(ty)}"
                    )
                else:
                    lane_y = (
                        lower_gap_lane(min(lower_rows), route_lane)
                        if lower_rows
                        else below_last_row_lane(sy + sh, route_lane)
                    )
                    path = (
                        f"M{fmt(source_center_x)} {fmt(sy + sh)} V{fmt(lane_y)} "
                        f"H{fmt(target_center_x)} V{fmt(ty + th)}"
                    )
            else:
                middle_x = between_left + (between_right - between_left) * lane_fraction(route_lane)
                path = (
                    f"M{fmt(start_x)} {fmt(source_center_y)} H{fmt(middle_x)} "
                    f"V{fmt(target_center_y)} H{fmt(end_x)}"
                )
        elif ty > sy:
            if ty - (sy + sh) <= declared_gap + 1e-6:
                start_x = source_center_x
                end_x = target_center_x
                middle_y = lower_gap_lane(ty, route_lane)
                path = (
                    f"M{fmt(start_x)} {fmt(sy + sh)} V{fmt(middle_y)} "
                    f"H{fmt(end_x)} V{fmt(ty)}"
                )
            else:
                gap_offset = gap_lane_offset(route_lane)
                outer_x = outer_lane_x(False, route_lane)
                path = (
                    f"M{fmt(source_center_x)} {fmt(sy + sh)} V{fmt(sy + sh + gap_offset)} "
                    f"H{fmt(outer_x)} V{fmt(ty - gap_offset)} "
                    f"H{fmt(target_center_x)} V{fmt(ty)}"
                )
        else:
            if sy - (ty + th) <= declared_gap + 1e-6:
                start_x = source_center_x
                end_x = target_center_x
                middle_y = lower_gap_lane(sy, route_lane)
                path = (
                    f"M{fmt(start_x)} {fmt(sy)} V{fmt(middle_y)} "
                    f"H{fmt(end_x)} V{fmt(ty + th)}"
                )
            else:
                gap_offset = gap_lane_offset(route_lane)
                outer_x = outer_lane_x(False, route_lane)
                path = (
                    f"M{fmt(source_center_x)} {fmt(sy)} V{fmt(sy - gap_offset)} "
                    f"H{fmt(outer_x)} V{fmt(ty + th + gap_offset)} "
                    f"H{fmt(target_center_x)} V{fmt(ty + th)}"
                )
        relationship_id = esc(raw_relationship_id)
        dash = (
            ' stroke-dasharray="8 7"'
            if kind == "feedback"
            else (' stroke-dasharray="3 4"' if kind == "dependency" else "")
        )
        parts.append(
            f'<g data-relationship-id="{relationship_id}" data-kind="{esc(kind)}" '
            f'data-source-module="{esc(relationship["source"])}" '
            f'data-target-module="{esc(relationship["target"])}" '
            f'data-source-port="{fmt(source_port)}" data-target-port="{fmt(target_port)}" '
            f'data-route-lane="{route_lane}" '
            f'aria-label="{esc(relationship["label"])}">'
            f'<title>{esc(relationship["label"])}</title>'
            f'<path id="relationship-{relationship_id}" class="relationship-path" d="{path}" '
            f'fill="none" stroke="#526176" stroke-width="2"{dash} '
            f'marker-end="url(#{esc(marker_id)})"/>'
            f'<circle class="relationship-pulse" data-relationship-pulse="true" r="5" '
            f'fill="#2563eb" opacity="0"/></g>'
        )
    columns = key_columns
    rows = key_rows
    cell_width = key_cell_width
    parts.append('<g id="composition-relationship-key" class="relationship-key" aria-hidden="true">')
    parts.append(
        f'<rect class="relationship-key-plaque" x="{fmt(root_x + 40.0)}" '
        f'y="{fmt(key_start_y - 11.0)}" width="{fmt(root_width - 80.0)}" '
        f'height="{fmt(rows * 14.0 + 5.0)}" rx="5"/>'
    )
    for index, relationship in enumerate(relationships):
        row, column = divmod(index, columns)
        x = root_x + 48.0 + column * cell_width
        y = key_start_y + row * 14.0
        kind = relationship.get("kind", "flow")
        dash = (
            ' stroke-dasharray="8 7"'
            if kind == "feedback"
            else (' stroke-dasharray="3 4"' if kind == "dependency" else "")
        )
        label_limit = max(12, int((cell_width - 76.0) / 5.4))
        label = str(relationship["label"])
        if len(label) > label_limit:
            label = label[: max(1, label_limit - 1)].rstrip() + "…"
        parts.append(
            f'<g data-relationship-key-id="{esc(relationship["id"])}" '
            f'data-relationship-key-kind="{esc(kind)}" '
            f'data-relationship-key-label="{esc(relationship["label"])}">'
            f'<title>{esc(kind)} relationship: {esc(relationship["label"])}</title>'
            f'<line x1="{fmt(x)}" y1="{fmt(y - 3)}" x2="{fmt(x + 20)}" y2="{fmt(y - 3)}" '
            f'stroke="{"#8a4b08" if kind == "feedback" else "#526176"}" stroke-width="2"{dash}/>'
            f'<text class="relationship-key-label" x="{fmt(x + 26)}" y="{fmt(y)}">'
            f'{esc(kind)} · {esc(label)}</text></g>'
        )
    parts.append("</g>")
    parts.append("</g>")
    return "".join(parts)


def world_markup(plan: dict[str, Any]) -> str:
    world = plan.get("world")
    if not isinstance(world, dict):
        return ""
    bounds = [float(item) for item in world["bounds"]]
    district_by_id = {item["id"]: item for item in world["districts"]}
    module_by_id = {item["id"]: item for item in plan["modules"]}
    marker_id = f"{plan['compositionId']}--world-arrow"
    parts = [
        '<g id="composition-world-map" data-world-map="true" '
        f'data-world-armature="{esc(world["armature"])}" aria-label="Navigable diagram world">',
        '<defs>',
        f'<pattern id="{esc(plan["compositionId"])}--world-grid" width="160" height="160" '
        'patternUnits="userSpaceOnUse"><circle cx="8" cy="8" r="2.4" fill="#94a3b8" '
        'fill-opacity="0.25"/></pattern>',
        f'<marker id="{esc(marker_id)}" viewBox="0 0 10 10" refX="8.5" refY="5" '
        'markerWidth="6" markerHeight="6" orient="auto-start-reverse">'
        '<path d="M1 1 L9 5 L1 9 Z" fill="context-stroke"/></marker>',
        '</defs>',
        f'<rect class="world-field" x="{fmt(bounds[0])}" y="{fmt(bounds[1])}" '
        f'width="{fmt(bounds[2])}" height="{fmt(bounds[3])}" '
        f'fill="url(#{esc(plan["compositionId"])}--world-grid)"/>',
        '<g id="world-district-links" class="world-district-links" '
        'aria-label="District lineage and dependency routes">',
    ]
    for link in world["links"]:
        source = district_by_id[link["source"]]
        target = district_by_id[link["target"]]
        sx, sy = (float(item) for item in source["center"])
        tx, ty = (float(item) for item in target["center"])
        dx = tx - sx
        dy = ty - sy
        bend = 0.17 if link["kind"] != "feedback" else -0.28
        normal_x = -dy * bend
        normal_y = dx * bend
        c1x = sx + dx * 0.34 + normal_x
        c1y = sy + dy * 0.34 + normal_y
        c2x = sx + dx * 0.66 + normal_x
        c2y = sy + dy * 0.66 + normal_y
        path = (
            f"M{fmt(sx)} {fmt(sy)} C{fmt(c1x)} {fmt(c1y)} "
            f"{fmt(c2x)} {fmt(c2y)} {fmt(tx)} {fmt(ty)}"
        )
        chevrons: list[str] = []
        if link["treeRole"] == "trunk":
            for progress in (0.50, 0.70):
                inverse = 1.0 - progress
                chevron_x = (
                    inverse**3 * sx
                    + 3.0 * inverse**2 * progress * c1x
                    + 3.0 * inverse * progress**2 * c2x
                    + progress**3 * tx
                )
                chevron_y = (
                    inverse**3 * sy
                    + 3.0 * inverse**2 * progress * c1y
                    + 3.0 * inverse * progress**2 * c2y
                    + progress**3 * ty
                )
                tangent_x = (
                    3.0 * inverse**2 * (c1x - sx)
                    + 6.0 * inverse * progress * (c2x - c1x)
                    + 3.0 * progress**2 * (tx - c2x)
                )
                tangent_y = (
                    3.0 * inverse**2 * (c1y - sy)
                    + 6.0 * inverse * progress * (c2y - c1y)
                    + 3.0 * progress**2 * (ty - c2y)
                )
                angle = math.degrees(math.atan2(tangent_y, tangent_x))
                chevrons.append(
                    f'<path class="world-link-chevron" d="M-28 -24 L0 0 L-28 24" '
                    f'transform="translate({fmt(chevron_x)} {fmt(chevron_y)}) rotate({fmt(angle)})"/>'
                )
        label_x = (sx + tx) / 2 + normal_x * 0.72
        label_y = (sy + ty) / 2 + normal_y * 0.72
        dash = (
            ' stroke-dasharray="18 12"'
            if link["kind"] == "feedback"
            else (
                ' stroke-dasharray="7 9"'
                if link["kind"] == "dependency" and link["treeRole"] != "trunk"
                else ""
            )
        )
        parts.append(
            f'<g id="world-link-{esc(link["id"])}" '
            f'class="world-link {"world-link-primary" if link["treeRole"] == "trunk" else "world-link-secondary"}" '
            f'data-world-link-id="{esc(link["id"])}" data-kind="{esc(link["kind"])}" '
            f'data-tree-role="{esc(link["treeRole"])}" '
            'data-route-active="false" data-route-traveling="false" '
            f'data-source-district="{esc(link["source"])}" '
            f'data-target-district="{esc(link["target"])}">'
            f'<title>{esc(link["label"])}</title>'
            f'<path class="world-link-halo" d="{path}"/>'
            f'<path class="world-link-path" d="{path}" marker-end="url(#{esc(marker_id)})"{dash}/>'
            f'<g class="world-link-chevrons">{"".join(chevrons)}</g>'
            f'<g class="world-link-label" transform="translate({fmt(label_x)} {fmt(label_y)})">'
            f'<rect x="-410" y="-70" width="820" height="140" rx="70"/>'
            f'<text text-anchor="middle" y="27">{esc(short_label(link["label"], 34))}</text>'
            '</g></g>'
        )
    parts.append('</g><g id="world-districts" class="world-districts">')
    for district in world["districts"]:
        x, y, width, height = (float(item) for item in district["bounds"])
        center_x, center_y = (float(item) for item in district["center"])
        label_x = x + 72
        label_y = y + 112
        summary_lines = textwrap.wrap(str(district["summary"]), width=58)[:2]
        summary = [
            f'<text class="district-summary" x="{fmt(label_x)}" y="{fmt(label_y + 64)}">'
            f'{esc(summary_lines[0]) if summary_lines else ""}'
        ]
        for line in summary_lines[1:]:
            summary.append(f'<tspan x="{fmt(label_x)}" dy="38">{esc(line)}</tspan>')
        summary.append('</text>')
        local_branch_parts = [
            f'<g class="world-local-branches" data-local-branches-for="{esc(district["id"])}" '
            'aria-label="Local diagram branches">'
        ]
        local_node_parts = [
            f'<g class="world-local-nodes" data-local-nodes-for="{esc(district["id"])}">'
        ]
        module_layouts: list[tuple[str, dict[str, Any], float, float]] = []
        for module_id in district["moduleIds"]:
            module = module_by_id[module_id]
            mx, my, mw, mh = (float(value) for value in module["region"])
            node_x = mx + mw / 2
            node_y = my + mh / 2
            module_layouts.append((module_id, module, node_x, node_y))
        local_armature = str(district["localArmature"])
        if local_armature == "orbit" and len(module_layouts) > 1:
            radius_x = max(abs(item[2] - center_x) for item in module_layouts)
            radius_y = max(abs(item[3] - center_y) for item in module_layouts)
            local_branch_parts.append(
                f'<ellipse class="world-local-branch world-local-orbit-ring" '
                f'cx="{fmt(center_x)}" cy="{fmt(center_y)}" rx="{fmt(radius_x)}" ry="{fmt(radius_y)}"/>'
            )
        for module_index, (module_id, module, node_x, node_y) in enumerate(module_layouts, start=1):
            local_path: str | None = None
            if local_armature == "branch" and module_index > 1:
                source_x, source_y = module_layouts[0][2], module_layouts[0][3]
                dx = node_x - source_x
                dy = node_y - source_y
                normal_x = -dy * (0.08 if module_index % 2 else -0.08)
                normal_y = dx * (0.08 if module_index % 2 else -0.08)
                local_path = (
                    f'M{fmt(source_x)} {fmt(source_y)} '
                    f'C{fmt(source_x + dx * 0.32 + normal_x)} {fmt(source_y + dy * 0.32 + normal_y)} '
                    f'{fmt(source_x + dx * 0.72 + normal_x)} {fmt(source_y + dy * 0.72 + normal_y)} '
                    f'{fmt(node_x)} {fmt(node_y)}'
                )
            elif local_armature == "lanes" and module_index > 1:
                source_x, source_y = module_layouts[module_index - 2][2], module_layouts[module_index - 2][3]
                midpoint_x = (source_x + node_x) / 2.0
                local_path = (
                    f'M{fmt(source_x)} {fmt(source_y)} H{fmt(midpoint_x)} '
                    f'V{fmt(node_y)} H{fmt(node_x)}'
                )
            elif local_armature == "radial" and module_index > 1:
                source_x, source_y = module_layouts[0][2], module_layouts[0][3]
                dx = node_x - source_x
                dy = node_y - source_y
                bend = 0.10 if module_index % 2 else -0.10
                normal_x = -dy * bend
                normal_y = dx * bend
                local_path = (
                    f'M{fmt(source_x)} {fmt(source_y)} '
                    f'C{fmt(source_x + dx * 0.30 + normal_x)} {fmt(source_y + dy * 0.30 + normal_y)} '
                    f'{fmt(source_x + dx * 0.72 + normal_x)} {fmt(source_y + dy * 0.72 + normal_y)} '
                    f'{fmt(node_x)} {fmt(node_y)}'
                )
            if local_path is not None:
                local_branch_parts.append(
                    f'<path class="world-local-branch {"world-local-root-branch" if module_index == 2 else ""}" '
                    f'd="{local_path}" data-local-module-id="{esc(module_id)}"/>'
                )
            wrapped_label = textwrap.wrap(
                str(module.get("navigationLabel", module_id.replace("-", " ").title())),
                width=22,
                break_long_words=False,
            )[:2]
            if not wrapped_label:
                wrapped_label = [module_id.replace("-", " ").title()]
            single_module_district = len(district["moduleIds"]) == 1
            node_halo_radius = 92.0 if single_module_district else 62.0
            node_core_radius = 62.0 if single_module_district else 42.0
            node_hit_radius = 108.0 if single_module_district else 76.0
            node_label_y = node_y + node_halo_radius + 16.0
            label_width = max(
                260.0,
                min(680.0, max(len(line) for line in wrapped_label) * 24.0 + 72.0),
            )
            label_height = 76.0 + max(0, len(wrapped_label) - 1) * 38.0
            label_markup = [
                f'<rect class="world-module-node-label-plaque" '
                f'x="{fmt(node_x - label_width / 2)}" y="{fmt(node_label_y - 48)}" '
                f'width="{fmt(label_width)}" height="{fmt(label_height)}" rx="{fmt(label_height / 2)}"/>',
                f'<text class="world-module-node-label" x="{fmt(node_x)}" y="{fmt(node_label_y)}" '
                'text-anchor="middle">'
            ]
            for line_index, line in enumerate(wrapped_label):
                label_markup.append(
                    f'<tspan x="{fmt(node_x)}" dy="{0 if line_index == 0 else 34}">{esc(line)}</tspan>'
                )
            label_markup.append('</text>')
            singleton_preview_markup = ""
            diagram = module.get("diagram")
            if single_module_district and isinstance(diagram, dict):
                preview_nodes = [
                    item
                    for item in diagram.get("nodes", [])
                    if item.get("kind") != "root"
                ][:12]
                preview_parts = [
                    '<g class="district-singleton-preview" aria-hidden="true">'
                ]
                inner_count = max(1, len(preview_nodes) // 2)
                for preview_index, preview_node in enumerate(preview_nodes):
                    inner = preview_index < inner_count
                    ring_index = preview_index if inner else preview_index - inner_count
                    ring_count = inner_count if inner else len(preview_nodes) - inner_count
                    angle = (
                        -math.pi / 2
                        + 2 * math.pi * ring_index / max(1, ring_count)
                        + (0.0 if inner else math.pi / max(2, ring_count))
                    )
                    radius_x = 300.0 if inner else 500.0
                    radius_y = 180.0 if inner else 315.0
                    preview_x = node_x + radius_x * math.cos(angle)
                    preview_y = node_y + radius_y * math.sin(angle)
                    vector_x = preview_x - node_x
                    vector_y = preview_y - node_y
                    distance = max(1.0, math.hypot(vector_x, vector_y))
                    end_x = preview_x - vector_x / distance * 32.0
                    end_y = preview_y - vector_y / distance * 32.0
                    preview_parts.append(
                        f'<line class="district-singleton-preview-branch" '
                        f'x1="{fmt(node_x)}" y1="{fmt(node_y)}" '
                        f'x2="{fmt(end_x)}" y2="{fmt(end_y)}"/>'
                        f'<circle class="district-singleton-preview-node" '
                        f'cx="{fmt(preview_x)}" cy="{fmt(preview_y)}" r="26"/>'
                    )
                    preview_lines = textwrap.wrap(
                        str(preview_node.get("label", preview_node.get("id", "Concept"))),
                        width=19,
                        break_long_words=False,
                    ) or [str(preview_node.get("label", "Concept"))]
                    preview_parts.append(
                        f'<text class="district-singleton-preview-label" '
                        f'x="{fmt(preview_x)}" y="{fmt(preview_y + 52)}" text-anchor="middle">'
                    )
                    for preview_line_index, preview_line in enumerate(preview_lines):
                        preview_parts.append(
                            f'<tspan x="{fmt(preview_x)}" '
                            f'dy="{0 if preview_line_index == 0 else 27}">{esc(preview_line)}</tspan>'
                        )
                    preview_parts.append('</text>')
                preview_parts.append('</g>')
                singleton_preview_markup = "".join(preview_parts)
            local_node_parts.append(
                f'<g id="world-module-node-{esc(module_id)}" class="world-module-node" '
                f'data-world-module-id="{esc(module_id)}" data-world-node-district="{esc(district["id"])}" '
                f'data-local-root="{str(module_index == 1).lower()}" '
                f'style="--district-accent: {esc(district["accent"])};">'
                f'{singleton_preview_markup}'
                f'<circle class="world-module-node-halo" cx="{fmt(node_x)}" cy="{fmt(node_y)}" r="{fmt(node_halo_radius)}"/>'
                f'<circle class="world-module-node-core" cx="{fmt(node_x)}" cy="{fmt(node_y)}" r="{fmt(node_core_radius)}"/>'
                f'<text class="world-module-node-index" x="{fmt(node_x)}" y="{fmt(node_y + 13)}" '
                f'text-anchor="middle">{esc(str(module_index).zfill(2))}</text>'
                f'{"".join(label_markup)}'
                f'<g id="module-nav-{esc(module_id)}" class="interactive-control world-module-nav-control" '
                f'data-nav-target="module-{esc(module_id)}" role="button" tabindex="-1" '
                f'aria-label="Open local diagram: {esc(module["question"])}">'
                f'<circle cx="{fmt(node_x)}" cy="{fmt(node_y)}" r="{fmt(node_hit_radius)}"/></g>'
                '</g>'
            )
        local_branch_parts.append('</g>')
        local_node_parts.append('</g>')
        is_root_district = district["id"] == world["rootDistrictId"]
        hub_halo_radius = 168.0 if is_root_district else 118.0
        hub_radius = 98.0 if is_root_district else 72.0
        hub_hit_radius = 186.0 if is_root_district else 132.0
        world_label_y = center_y - hub_halo_radius - 84.0
        world_label_width = max(
            760.0,
            min(1540.0, len(str(district["label"])) * 84.0 + 180.0),
        )
        parts.append(
            f'<g id="district-{esc(district["id"])}" class="world-district" '
            f'data-district-id="{esc(district["id"])}" '
            f'data-nav-anchor-id="district-{esc(district["id"])}" '
            f'data-local-armature="{esc(district["localArmature"])}" '
            f'data-world-root="{str(is_root_district).lower()}" '
            f'data-single-module="{str(len(district["moduleIds"]) == 1).lower()}" '
            f'style="--district-accent: {esc(district["accent"])};">'
            f'<title>{esc(district["label"])}: {esc(district["summary"])}</title>'
            f'<rect class="district-field" x="{fmt(x)}" y="{fmt(y)}" '
            f'width="{fmt(width)}" height="{fmt(height)}" rx="180"/>'
            f'{"".join(local_branch_parts)}'
            f'{"".join(local_node_parts)}'
            f'<circle class="district-hub-halo" cx="{fmt(center_x)}" cy="{fmt(center_y)}" r="{fmt(hub_halo_radius)}"/>'
            f'<circle class="district-hub" cx="{fmt(center_x)}" cy="{fmt(center_y)}" r="{fmt(hub_radius)}"/>'
            f'<text class="district-index" x="{fmt(center_x)}" y="{fmt(center_y + 17)}" '
            f'text-anchor="middle">{esc(str(world["districts"].index(district) + 1).zfill(2))}</text>'
            f'<text class="district-title district-title-detail" x="{fmt(label_x)}" y="{fmt(label_y)}">'
            f'{esc(district["label"])}</text>'
            f'<rect class="district-title-world-plaque" '
            f'x="{fmt(center_x - world_label_width / 2)}" y="{fmt(world_label_y - 116)}" '
            f'width="{fmt(world_label_width)}" height="158" rx="79"/>'
            f'<text class="district-title district-title-world" x="{fmt(center_x)}" '
            f'y="{fmt(world_label_y)}" text-anchor="middle">{esc(district["label"])}</text>'
            f'{"".join(summary)}'
            f'<g id="district-nav-{esc(district["id"])}" class="interactive-control district-nav-control" '
            f'data-nav-target="district-{esc(district["id"])}" role="button" tabindex="0" '
            f'aria-label="Open district: {esc(district["label"])}" '
            f'><circle cx="{fmt(center_x)}" cy="{fmt(center_y)}" r="{fmt(hub_hit_radius)}"/></g>'
            '</g>'
        )
    parts.append('</g></g>')
    return "".join(parts)


def navigation_hud_markup(plan: dict[str, Any]) -> str:
    navigation_plan = plan.get("navigation")
    world = plan.get("world")
    if not isinstance(navigation_plan, dict) or not isinstance(world, dict):
        return ""
    _, _, world_width, world_height = (float(item) for item in navigation_plan["worldBounds"])
    map_x, map_y, map_width, map_height = 1620.0, 690.0, 280.0, 157.5
    parts = [
        '<g id="navigation-hud" class="navigation-hud" data-navigation-hud="true" '
        'aria-label="Spatial navigation and minimap">',
        '<rect class="navigation-hud-panel" x="1620" y="140" width="280" height="520" rx="24"/>',
        '<text class="navigation-eyebrow" x="1644" y="180">CAMERA ROUTE</text>',
        '<text class="navigation-current-label" data-navigation-current-label="true" '
        'x="1644" y="210">WORLD</text>',
        '<text class="navigation-current-tier" data-navigation-current-tier="true" '
        'x="1644" y="276">WORLD · topology</text>',
        '<text class="navigation-handoff" data-navigation-handoff="true" '
        'x="1644" y="528">SELECT A BRANCH OR PLAY THE TOUR</text>',
        '<text class="navigation-help" x="1644" y="600">DRAG TO PAN · WHEEL TO ZOOM</text>',
        '<text class="navigation-help" x="1644" y="626">HOME OR 0 RETURNS TO WORLD</text>',
    ]
    controls = (
        ("previous", "PREV", 1644.0, 300.0, 112.0),
        ("up", "UP", 1766.0, 300.0, 112.0),
        ("next", "NEXT", 1644.0, 372.0, 112.0),
        ("tour", "TOUR", 1766.0, 372.0, 112.0),
        ("home", "WORLD", 1644.0, 444.0, 234.0),
    )
    for action, label, x, y, control_width in controls:
        parts.append(
            f'<g id="camera-control-{action}" class="interactive-control navigation-control" '
            f'data-camera-action="{action}" '
            f'role="button" tabindex="0" aria-label="{esc(label.title())} camera view" '
            f'transform="translate({fmt(x)} {fmt(y)})"><rect width="{fmt(control_width)}" height="54" rx="18"/>'
            f'<text x="{fmt(control_width / 2)}" y="34" text-anchor="middle">{label}</text></g>'
        )
    parts.extend(
        [
            f'<g id="navigation-minimap" class="navigation-minimap" '
            f'transform="translate({fmt(map_x)} {fmt(map_y)})" '
            f'data-world-width="{fmt(world_width)}" data-world-height="{fmt(world_height)}">',
            f'<rect class="minimap-field" width="{fmt(map_width)}" height="{fmt(map_height)}" rx="16"/>',
        ]
    )
    for district in world["districts"]:
        x, y, width, height = (float(item) for item in district["bounds"])
        parts.append(
            f'<rect class="minimap-district" data-minimap-district="{esc(district["id"])}" '
            f'x="{fmt(x / world_width * map_width)}" y="{fmt(y / world_height * map_height)}" '
            f'width="{fmt(width / world_width * map_width)}" '
            f'height="{fmt(height / world_height * map_height)}" '
            f'style="--district-accent: {esc(district["accent"])};"/>'
        )
    parts.append(
        '<rect class="minimap-viewport" data-minimap-viewport="true" '
        f'x="0" y="0" width="{fmt(map_width)}" height="{fmt(map_height)}" rx="4"/>'
        '</g></g>'
    )
    return "".join(parts)


RUNTIME_JS = r"""
(function () {
  "use strict";
  const root = document.documentElement;
  const metadata = document.getElementById("sync-composition-plan");
  const plan = JSON.parse(metadata.textContent);
  const sourceDefs = new Map(plan.concepts.map((item) => [item.id, item]));
  const derivedDefs = new Map((plan.derived || []).map((item) => [item.id, item]));
  const scenarios = new Map(plan.scenarios.map((item) => [item.id, item]));
  const modules = new Map(plan.modules.map((item) => [item.id, item]));
  const focusGroups = new Map((plan.focusGroups || []).map((item) => [item.id, item]));
  const navigationPlan = plan.navigation || null;
  const navigationAnchors = new Map(
    navigationPlan ? navigationPlan.anchors.map((item) => [item.id, item]) : []
  );
  const worldViewport = document.getElementById("composition-world-viewport");
  const reduceMotion = matchMedia("(prefers-reduced-motion: reduce)").matches;
  let sourceValues = Object.fromEntries(plan.concepts.map((item) => [item.id, Number(item.default)]));
  let derivedValues = {};
  let scenarioId = null;
  let focusId = null;
  let timeMs = 0;
  let phaseId = null;
  let phaseProgress = 0;
  let revision = 0;
  let playing = false;
  let animationTimer = null;
  let playStartedAt = 0;
  let playStartedTime = 0;
  let cameraViewBox = navigationPlan
    ? [...navigationAnchors.get(navigationPlan.initialAnchorId).viewBox]
    : null;
  let cameraAnchorId = navigationPlan ? navigationPlan.initialAnchorId : null;
  let cameraTier = navigationPlan ? "world" : null;
  let cameraRevision = 0;
  let cameraTimeMs = 0;
  let cameraStopId = null;
  let cameraPlaying = false;
  let cameraTimer = null;
  let cameraPlayStartedAt = 0;
  let cameraPlayStartedTime = 0;

  function clone(value) { return JSON.parse(JSON.stringify(value)); }
  function stable(value) {
    if (Array.isArray(value)) return value.map(stable);
    if (value && typeof value === "object") {
      return Object.fromEntries(Object.keys(value).sort().map((key) => [key, stable(value[key])]));
    }
    return value;
  }
  function sortedObject(value) {
    return Object.fromEntries(Object.keys(value).sort().map((key) => [key, value[key]]));
  }
  function numeric(value, label) {
    const number = Number(value);
    if (!Number.isFinite(number)) throw new Error(label + " must be finite");
    return number;
  }
  function evalNode(node, values) {
    if (typeof node === "number") return numeric(node, "literal");
    if (node && Object.keys(node).length === 1 && "ref" in node) {
      if (!(node.ref in values)) throw new Error("unresolved ref: " + node.ref);
      return numeric(values[node.ref], node.ref);
    }
    if (!node || !Array.isArray(node.args)) throw new Error("invalid compute node");
    const args = node.args.map((arg) => evalNode(arg, values));
    let result;
    if (node.op === "add") result = args.reduce((sum, value) => sum + value, 0);
    else if (node.op === "subtract") result = args[0] - args.slice(1).reduce((sum, value) => sum + value, 0);
    else if (node.op === "multiply") result = args.reduce((product, value) => product * value, 1);
    else if (node.op === "divide") {
      if (args[1] === 0) throw new Error("division by zero");
      result = args[0] / args[1];
    } else if (node.op === "min") result = Math.min(...args);
    else if (node.op === "max") result = Math.max(...args);
    else if (node.op === "clamp") result = Math.min(Math.max(args[0], args[1]), args[2]);
    else if (node.op === "round") {
      const places = args.length > 1 ? Math.trunc(args[1]) : 0;
      const factor = 10 ** places;
      result = Math.round((args[0] + Number.EPSILON) * factor) / factor;
    } else throw new Error("unsupported op: " + node.op);
    return numeric(result, "derived result");
  }
  function computeDerived(nextSource) {
    const values = {...nextSource};
    const nextDerived = {};
    const pending = new Map(derivedDefs);
    while (pending.size) {
      let progressed = false;
      for (const [id, item] of [...pending]) {
        if ((item.dependsOn || []).every((dep) => dep in values)) {
          const result = evalNode(item.compute, values);
          values[id] = result;
          nextDerived[id] = result;
          pending.delete(id);
          progressed = true;
        }
      }
      if (!progressed) throw new Error("derived dependency cycle or missing reference");
    }
    return nextDerived;
  }
  function validatePatch(patch, base = sourceValues) {
    if (!patch || typeof patch !== "object" || Array.isArray(patch)) throw new Error("state patch must be an object");
    const next = {...base};
    for (const [id, raw] of Object.entries(patch)) {
      const def = sourceDefs.get(id);
      if (!def) throw new Error("unknown or derived concept: " + id);
      const value = numeric(raw, id);
      if (Array.isArray(def.domain) && (value < def.domain[0] || value > def.domain[1])) {
        throw new Error(id + " is outside its domain");
      }
      next[id] = value;
    }
    return next;
  }
  function applyTransform(value, transform) {
    if (!transform || transform.op === "identity") return value;
    if (transform.op === "linear" || transform.op === "rotate") {
      const domain = transform.domain;
      const range = transform.range;
      let t = (value - domain[0]) / (domain[1] - domain[0]);
      if (transform.clamp) t = Math.min(Math.max(t, 0), 1);
      const mapped = range[0] + t * (range[1] - range[0]);
      if (transform.op === "rotate") {
        const center = transform.center || [0, 0];
        return `rotate(${mapped} ${center[0]} ${center[1]})`;
      }
      return mapped;
    }
    throw new Error("unsupported binding transform: " + transform.op);
  }
  function formatValue(value, format) {
    const displayValue = value === 0 ? 0 : value;
    if (!format) return String(displayValue);
    const options = {...format};
    const suffix = typeof options.suffix === "string" ? options.suffix : "";
    delete options.suffix;
    const style = options.style || "decimal";
    const currencySymbols = {USD: "$", EUR: "€", GBP: "£", JPY: "¥", CNY: "CN¥", CAD: "CA$", AUD: "A$"};
    const digits = Number.isInteger(options.maximumFractionDigits)
      ? options.maximumFractionDigits
      : (style === "currency" ? 2 : (style === "percent" ? 0 : 3));
    if (!Number.isInteger(options.maximumFractionDigits)) options.maximumFractionDigits = digits;
    if (!Number.isInteger(options.minimumFractionDigits)) {
      options.minimumFractionDigits = style === "currency" ? Math.min(2, digits) : 0;
    }
    if (style === "currency" && !currencySymbols[String(options.currency || "USD")] && !options.currencyDisplay) {
      options.currencyDisplay = "code";
    }
    const scaled = style === "percent" ? displayValue * 100 : displayValue;
    const roundsToZero = displayValue !== 0 && Math.abs(scaled) < 0.5 * (10 ** -digits);
    if (roundsToZero) {
      const [rawMantissa, rawExponent] = Math.abs(scaled).toExponential(5).split("e");
      const mantissa = rawMantissa.replace(/(?:\.0+|(?<=[0-9])0+)$/, "").replace(/\.$/, "");
      const scientific = `${mantissa}E${Number(rawExponent)}`;
      const sign = scaled < 0 ? "-" : "";
      if (style === "currency") {
        const currency = String(options.currency || "USD");
        const symbol = currencySymbols[currency] || `${currency}\u00a0`;
        return `${sign}${symbol}${scientific}${suffix}`;
      }
      if (style === "percent") return `${sign}${scientific}%${suffix}`;
      return `${sign}${scientific}${suffix}`;
    }
    return new Intl.NumberFormat(plan.locale || "en-US", options).format(displayValue) + suffix;
  }
  function formatAccessibleValue(value, binding, unit) {
    let format = binding.format ? {...binding.format} : null;
    const currencyUnit = /^([A-Z]{3})\/(.+)$/.exec(unit || "");
    if (!format && currencyUnit) {
      format = {
        style: "currency",
        currency: currencyUnit[1],
        maximumFractionDigits: Number.isInteger(value) ? 0 : 2
      };
    }
    if (!format && unit === "fraction") {
      format = {style: "percent", maximumFractionDigits: 1};
    }
    const formatted = formatValue(value, format);
    if (currencyUnit) {
      const period = {
        year: "per year", month: "per month", week: "per week",
        day: "per day", hour: "per hour"
      }[currencyUnit[2]] || `per ${currencyUnit[2]}`;
      return `${formatted} ${period}`;
    }
    if (format && typeof format.suffix === "string" && format.suffix) return formatted;
    if (unit && unit !== "fraction" && !(format && format.style === "currency")) {
      return `${formatted} ${unit}`;
    }
    return formatted;
  }
  function renderBinding(element, binding, value) {
    const rendered = applyTransform(value, binding.transform);
    if (binding.channel === "text") element.textContent = formatValue(value, binding.format);
    else if (["x", "y", "width", "height", "r", "path", "transform", "opacity"].includes(binding.channel)) {
      element.setAttribute(binding.channel === "path" ? "d" : binding.channel, String(rendered));
    } else if (binding.channel === "class") element.setAttribute("data-sync-class", String(rendered));
    else if (binding.channel === "aria-value") element.setAttribute("aria-valuenow", String(value));
    element.setAttribute("data-current-value", String(value));
    element.setAttribute("data-sync-revision", String(revision));
    const definition = sourceDefs.get(binding.value) || derivedDefs.get(binding.value) || {};
    const unit = element.dataset.valueUnit || definition.unit || "";
    const label = element.dataset.accessibleLabel || definition.label || binding.value;
    const accessibleValue = formatAccessibleValue(value, binding, unit);
    element.setAttribute("data-accessible-label", label);
    element.setAttribute("data-value-unit", unit);
    element.setAttribute("data-accessible-value", accessibleValue);
    element.setAttribute("aria-label", `${label}: ${accessibleValue}`);
    if (element.getAttribute("role") === "meter") {
      element.setAttribute("aria-valuenow", String(value));
      element.setAttribute("aria-valuetext", accessibleValue);
    }
    element.style.setProperty("--sync-value", String(value));
    element.style.setProperty("--sync-rendered", String(rendered));
  }
  function layoutRenderedValue(item) {
    const mark = item.querySelector("[data-bind]");
    if (!mark) throw new Error("layout item is missing its canonical binding target");
    const raw = mark.style.getPropertyValue("--sync-rendered") ||
      mark.getAttribute(mark.dataset.channel || "width") || "0";
    return Math.max(0, numeric(raw, "layout rendered value"));
  }
  function layoutCanonicalMagnitude(item) {
    const mark = item.querySelector("[data-bind]");
    if (!mark) throw new Error("layout item is missing its canonical binding target");
    return Math.abs(numeric(mark.dataset.currentValue || "0", "layout canonical value"));
  }
  function layoutStack(plot) {
    const scale = numeric(plot.dataset.layoutScale, "stack scale");
    const y = numeric(plot.dataset.layoutY, "stack y");
    const start = numeric(plot.dataset.layoutX, "stack x");
    const maxSpan = numeric(plot.dataset.layoutMaxSpan, "stack max span");
    let cursor = start;
    for (const item of plot.querySelectorAll('[data-sync-layout-item="stack"]')) {
      const value = layoutRenderedValue(item);
      const remaining = Math.max(0, start + maxSpan - cursor);
      const drawn = Math.min(remaining, value * scale);
      const effectiveScale = value !== 0 ? drawn / value : 0;
      item.setAttribute("transform", `translate(${cursor} ${y}) scale(${effectiveScale} 1)`);
      // Ignore only serialization noise below a quarter pixel; visible clipping is blocking.
      item.setAttribute("data-visual-clamped", String(drawn + 0.25 < value * scale));
      cursor += drawn;
    }
  }
  function layoutWaterfall(plot) {
    const scale = numeric(plot.dataset.layoutScale, "waterfall scale");
    const baseline = numeric(plot.dataset.layoutBaseline, "waterfall baseline");
    const plotTop = numeric(plot.dataset.layoutTop, "waterfall top");
    const maxValue = numeric(plot.dataset.layoutMaxValue, "waterfall max value");
    const items = [...plot.querySelectorAll('[data-sync-layout-item="waterfall"]')]
      .sort((a, b) => Number(a.dataset.layoutIndex) - Number(b.dataset.layoutIndex));
    let level = 0;
    items.forEach((item, index) => {
      const value = layoutCanonicalMagnitude(item);
      const mark = item.querySelector("[data-bind]");
      const renderedExtent = layoutRenderedValue(item);
      const x = numeric(item.dataset.layoutX, "waterfall x");
      const isFinal = index === items.length - 1;
      let barTop;
      let visible;
      if (index === 0) {
        visible = Math.min(value, maxValue);
        level = visible;
        barTop = baseline - visible * scale;
        const effectiveScale = renderedExtent !== 0 ? scale * visible / renderedExtent : 0;
        item.setAttribute("transform", `translate(${x} ${baseline}) scale(1 ${-effectiveScale})`);
      } else if (isFinal) {
        visible = Math.min(value, maxValue);
        barTop = baseline - visible * scale;
        const effectiveScale = renderedExtent !== 0 ? scale * visible / renderedExtent : 0;
        item.setAttribute("transform", `translate(${x} ${baseline}) scale(1 ${-effectiveScale})`);
      } else {
        visible = Math.min(value, maxValue, level);
        barTop = baseline - level * scale;
        const effectiveScale = renderedExtent !== 0 ? scale * visible / renderedExtent : 0;
        item.setAttribute("transform", `translate(${x} ${baseline - level * scale}) scale(1 ${effectiveScale})`);
        level = Math.max(0, level - visible);
      }
      // Keep the bound height canonical; cumulative geometry belongs to the wrapper.
      item.setAttribute("data-visual-clamped", String(visible + 1e-6 < value));
      const connector = plot.querySelector(`[data-sync-layout-connector="${index}"]`);
      if (connector) {
        const connectorY = baseline - level * scale;
        connector.setAttribute("y1", String(connectorY));
        connector.setAttribute("y2", String(connectorY));
      }
      const signedLabel = plot.querySelector(`[data-waterfall-signed-index="${index}"]`);
      if (signedLabel && mark) {
        const readable = mark.dataset.accessibleValue || String(mark.dataset.currentValue || value);
        const magnitude = readable.replace(/^[+−-]/, "");
        const sign = signedLabel.dataset.waterfallSign;
        signedLabel.textContent = sign === "plus" ? `+${magnitude}` :
          (sign === "minus" ? `−${magnitude}` : readable);
        signedLabel.setAttribute("y", String(Math.max(plotTop + 12, barTop - 7)));
      }
    });
  }
  function layoutFlow(plot, group) {
    const sourceLabel = plot.querySelector("[data-flow-source-label]");
    const sourceMark = plot.querySelector("[data-flow-source-bound] [data-bind]");
    if (sourceLabel && sourceMark) {
      const base = sourceLabel.dataset.baseLabel || "Source";
      const value = sourceMark.dataset.accessibleValue || sourceMark.dataset.currentValue || "";
      sourceLabel.textContent = value ? `${base} · ${value}` : base;
    }
    for (const item of plot.querySelectorAll('[data-sync-layout-item="flow"]')) {
      const role = item.dataset.layoutBoundRole;
      const mark = group.querySelector(`[data-role="${CSS.escape(role)}"]`);
      if (!mark) throw new Error("flow layout is missing binding target: " + role);
      const rendered = numeric(mark.style.getPropertyValue("--sync-rendered") || "0", "flow rendered value");
      const rawValue = numeric(mark.dataset.currentValue || "0", "flow canonical value");
      const scaled = Math.abs(rendered) * numeric(item.dataset.layoutValueScale, "flow value scale");
      const minimum = numeric(item.dataset.layoutMinStroke, "flow minimum stroke");
      const maximum = numeric(item.dataset.layoutMaxStroke, "flow maximum stroke");
      const thickness = rawValue === 0
        ? 0
        : Math.min(maximum, Math.max(minimum, scaled * numeric(item.dataset.layoutStrokeScale, "flow stroke scale")));
      const path = item.querySelector("[data-sync-flow-path]");
      if (!path) throw new Error("flow layout item is missing its branch path");
      path.setAttribute("stroke-width", String(thickness));
      const negative = rawValue < 0;
      const direction = thickness === 0 ? "zero" : (negative ? "reverse" : "forward");
      item.setAttribute("data-flow-direction", direction);
      path.setAttribute("d", negative ? item.dataset.flowReversePath : item.dataset.flowForwardPath);
      if (negative) {
        path.setAttribute("stroke-dasharray", "7 5");
        path.setAttribute("marker-end", plot.dataset.flowReverseMarker);
      } else {
        path.removeAttribute("stroke-dasharray");
        path.removeAttribute("marker-end");
      }
      item.setAttribute("data-current-flow-thickness", String(thickness));
      const valueLabel = item.querySelector("[data-flow-value-label]");
      if (valueLabel) {
        valueLabel.textContent = mark.dataset.accessibleValue || mark.dataset.currentValue || "";
      }
      const signLabel = item.querySelector("[data-flow-sign-label]");
      if (signLabel) signLabel.textContent = negative ? "DEFICIT" : "";
    }
  }
  function layoutModule(group) {
    group.querySelectorAll('[data-sync-layout="stack"]').forEach(layoutStack);
    group.querySelectorAll('[data-sync-layout="waterfall"]').forEach(layoutWaterfall);
    group.querySelectorAll('[data-sync-layout="flow"]').forEach((plot) => layoutFlow(plot, group));
  }
  function normalizedCamera(raw) {
    if (!navigationPlan) throw new Error("navigation is not declared");
    if (!Array.isArray(raw) || raw.length !== 4) throw new Error("camera must be [x, y, width, height]");
    let [x, y, width, height] = raw.map((value) => numeric(value, "camera value"));
    if (width <= 0 || height <= 0) throw new Error("camera dimensions must be positive");
    const [worldX, worldY, worldWidth, worldHeight] = navigationPlan.worldBounds.map(Number);
    const viewportAspect = Number(navigationPlan.viewport[2]) / Number(navigationPlan.viewport[3]);
    if (Math.abs(width / height - viewportAspect) > 1e-6) {
      throw new Error("camera aspect must match the fixed viewport");
    }
    const moduleWidths = navigationPlan.anchors
      .filter((anchor) => anchor.kind === "module")
      .map((anchor) => Number(anchor.viewBox[2]));
    const minimumWidth = Math.max(80, Math.min(...moduleWidths) * 0.55);
    width = Math.min(Math.max(width, minimumWidth), worldWidth);
    height = width / viewportAspect;
    if (height > worldHeight) {
      height = worldHeight;
      width = height * viewportAspect;
    }
    x = Math.min(Math.max(x, worldX), worldX + worldWidth - width);
    y = Math.min(Math.max(y, worldY), worldY + worldHeight - height);
    return [x, y, width, height];
  }
  function cameraEqual(first, second) {
    return Boolean(first && second && first.every((value, index) => Math.abs(value - second[index]) <= 1e-7));
  }
  function cameraZoomTier(camera) {
    if (!navigationPlan) return null;
    const ratio = camera[2] / Number(navigationPlan.worldBounds[2]);
    const thresholds = Object.fromEntries(
      navigationPlan.semanticZoom.map((item) => [item.id, Number(item.maximumWidthRatio)])
    );
    if (ratio <= thresholds.module) return "module";
    if (ratio <= thresholds.district) return "district";
    return "world";
  }
  function cameraSnapshot() {
    return {
      version: 1,
      compositionId: plan.compositionId,
      revision: cameraRevision,
      anchorId: cameraAnchorId,
      viewBox: cameraViewBox ? [...cameraViewBox] : null,
      tier: cameraTier,
      timeMs: cameraTimeMs,
      stopId: cameraStopId,
      playing: cameraPlaying,
      motion: reduceMotion ? "reduced" : "full"
    };
  }
  function updateCameraHud() {
    if (!navigationPlan || !cameraViewBox || !worldViewport) return;
    worldViewport.setAttribute("viewBox", cameraViewBox.join(" "));
    root.setAttribute("data-camera-anchor", cameraAnchorId || "");
    root.setAttribute("data-camera-tier", cameraTier || "");
    root.setAttribute("data-camera-revision", String(cameraRevision));
    root.setAttribute("data-camera-time-ms", String(cameraTimeMs));
    root.setAttribute("data-camera-stop-id", cameraStopId || "");
    const anchor = cameraAnchorId ? navigationAnchors.get(cameraAnchorId) : null;
    const stop = cameraStopId
      ? navigationPlan.route.stops.find((item) => item.id === cameraStopId)
      : null;
    const label = root.querySelector("[data-navigation-current-label]");
    if (label) {
      const breadcrumb = ["WORLD"];
      if (anchor?.kind === "district") breadcrumb.push(anchor.label);
      else if (anchor?.kind === "module") {
        const parent = navigationAnchors.get(anchor.parentId);
        if (parent?.label) breadcrumb.push(parent.label);
        breadcrumb.push(anchor.label);
      } else if (!anchor && stop?.label) breadcrumb.push(stop.label);
      const fullLabel = breadcrumb.join(" › ");
      const lines = [""];
      for (const word of fullLabel.split(/\s+/).filter(Boolean)) {
        const candidate = `${lines.at(-1)} ${word}`.trim();
        if (candidate.length <= 28 || !lines.at(-1)) lines[lines.length - 1] = candidate;
        else lines.push(word);
      }
      label.replaceChildren();
      lines.slice(0, 3).forEach((line, index) => {
        const tspan = document.createElementNS(label.namespaceURI, "tspan");
        tspan.setAttribute("x", "1644");
        tspan.setAttribute("dy", index === 0 ? "0" : "22");
        tspan.textContent = line;
        label.appendChild(tspan);
      });
      label.setAttribute("aria-label", fullLabel);
    }
    const tier = root.querySelector("[data-navigation-current-tier]");
    if (tier) {
      const tierCopy = {
        world: "WORLD · topology",
        district: "DISTRICT · local index",
        module: "MODULE · complete diagram"
      }[cameraTier] || "FREE CAMERA · manual view";
      tier.textContent = tierCopy;
    }
    const handoff = root.querySelector("[data-navigation-handoff]");
    if (handoff) {
      const fullHandoff = stop?.handoff || (anchor ? `Explore ${anchor.label}` : "Free camera navigation");
      const handoffLines = [""];
      for (const word of fullHandoff.split(/\s+/).filter(Boolean)) {
        const candidate = `${handoffLines.at(-1)} ${word}`.trim();
        if (candidate.length <= 34 || !handoffLines.at(-1)) handoffLines[handoffLines.length - 1] = candidate;
        else handoffLines.push(word);
      }
      handoff.replaceChildren();
      handoffLines.slice(0, 3).forEach((line, index) => {
        const tspan = document.createElementNS(handoff.namespaceURI, "tspan");
        tspan.setAttribute("x", "1644");
        tspan.setAttribute("dy", index === 0 ? "0" : "17");
        tspan.textContent = line;
        handoff.appendChild(tspan);
      });
      handoff.setAttribute("aria-label", fullHandoff);
    }
    const upControl = root.querySelector('[data-camera-action="up"]');
    if (upControl) {
      const upText = upControl.querySelector("text");
      const hasParent = anchor?.kind === "module" || anchor?.kind === "district";
      const upLabel = anchor?.kind === "module" ? "DISTRICT" : "WORLD";
      if (upText) upText.textContent = hasParent ? upLabel : "UP";
      upControl.setAttribute("aria-label", anchor?.kind === "module"
        ? "Return to parent district"
        : (anchor?.kind === "district" ? "Return to world overview" : "Already at world overview"));
      upControl.setAttribute("aria-disabled", String(!hasParent));
      upControl.setAttribute("tabindex", hasParent ? "0" : "-1");
    }
    const minimap = root.querySelector("[data-minimap-viewport]");
    if (minimap) {
      const field = minimap.parentElement.querySelector(".minimap-field");
      const mapWidth = Number(field?.getAttribute("width")) || 320;
      const mapHeight = Number(field?.getAttribute("height")) || 180;
      const [worldX, worldY, worldWidth, worldHeight] = navigationPlan.worldBounds.map(Number);
      minimap.setAttribute("x", String((cameraViewBox[0] - worldX) / worldWidth * mapWidth));
      minimap.setAttribute("y", String((cameraViewBox[1] - worldY) / worldHeight * mapHeight));
      minimap.setAttribute("width", String(cameraViewBox[2] / worldWidth * mapWidth));
      minimap.setAttribute("height", String(cameraViewBox[3] / worldHeight * mapHeight));
    }
    const intersectsCamera = (region) => {
      const [mx, my, mw, mh] = region.map(Number);
      const [cx, cy, cw, ch] = cameraViewBox;
      return mx + mw > cx && my + mh > cy && mx < cx + cw && my < cy + ch;
    };
    let activeDistrictId = null;
    if (anchor?.kind === "district") activeDistrictId = anchor.targetId;
    else if (anchor?.kind === "module") activeDistrictId = String(anchor.parentId || "").replace(/^district-/, "");
    const districtForAnchor = (item) => {
      if (!item || item.kind === "world") return null;
      if (item.kind === "district") return item.targetId;
      if (item.kind === "module") return String(item.parentId || "").replace(/^district-/, "");
      return null;
    };
    const routeFromDistrict = districtForAnchor(
      stop ? navigationAnchors.get(stop.fromAnchorId) : null
    );
    const routeTargetDistrict = districtForAnchor(
      stop ? navigationAnchors.get(stop.anchorId) : anchor
    ) || activeDistrictId;
    root.querySelectorAll("[data-world-link-id]").forEach((link) => {
      const exactRoute = Boolean(
        routeFromDistrict && routeTargetDistrict &&
        link.dataset.sourceDistrict === routeFromDistrict &&
        link.dataset.targetDistrict === routeTargetDistrict
      );
      const incomingTrunk = Boolean(
        !routeFromDistrict && routeTargetDistrict &&
        link.dataset.targetDistrict === routeTargetDistrict &&
        link.dataset.treeRole === "trunk"
      );
      link.setAttribute("data-route-active", String(exactRoute || incomingTrunk));
      link.setAttribute("data-route-traveling", String(exactRoute && !cameraAnchorId));
    });
    for (const district of plan.world?.districts || []) {
      const active = activeDistrictId
        ? district.id === activeDistrictId
        : (cameraTier === "world" || intersectsCamera(district.bounds));
      const group = root.querySelector(`#district-${CSS.escape(district.id)}`);
      if (group) group.setAttribute("data-camera-active", String(active));
      const control = group?.querySelector(":scope > .district-nav-control");
      if (control) control.setAttribute("tabindex", cameraTier === "world" ? "0" : "-1");
    }
    for (const module of plan.modules) {
      const group = root.querySelector(`[data-module-id="${CSS.escape(module.id)}"]`);
      if (!group) continue;
      const visible = intersectsCamera(module.region);
      const active = anchor?.kind === "module"
        ? module.id === anchor.targetId
        : (anchor?.kind === "district" ? anchor.moduleIds.includes(module.id) : visible);
      group.setAttribute("data-camera-active", String(Boolean(active)));
      for (const control of group.querySelectorAll("[data-module-focus-id]")) {
        control.setAttribute("tabindex", cameraTier === "module" && active && visible ? "0" : "-1");
      }
      const node = root.querySelector(`[data-world-module-id="${CSS.escape(module.id)}"]`);
      if (node) {
        node.setAttribute("data-camera-active", String(Boolean(active)));
        const control = node.querySelector("[data-nav-target]");
        if (control) {
          const nodeDistrict = node.getAttribute("data-world-node-district");
          control.setAttribute(
            "tabindex",
            cameraTier === "district" && nodeDistrict === activeDistrictId ? "0" : "-1"
          );
        }
      }
    }
  }
  function emitCamera() {
    const detail = cameraSnapshot();
    root.dispatchEvent(new CustomEvent("svg-camera-change", {detail}));
    return detail;
  }
  function commitCamera(raw, anchorId = null, time = cameraTimeMs, stopId = cameraStopId, emit = true) {
    if (!navigationPlan) return cameraSnapshot();
    const next = normalizedCamera(raw);
    const nextTier = anchorId && navigationAnchors.has(anchorId)
      ? navigationAnchors.get(anchorId).zoomTier
      : cameraZoomTier(next);
    const changed = !cameraEqual(next, cameraViewBox) || anchorId !== cameraAnchorId ||
      time !== cameraTimeMs || stopId !== cameraStopId;
    if (!changed) return cameraSnapshot();
    cameraViewBox = next;
    cameraAnchorId = anchorId;
    cameraTier = nextTier;
    cameraTimeMs = time;
    cameraStopId = stopId;
    cameraRevision += 1;
    updateCameraHud();
    return emit ? emitCamera() : cameraSnapshot();
  }
  function updateNavigationHash(anchorId) {
    if (!anchorId || typeof history === "undefined") return;
    try {
      const url = new URL(window.location.href);
      url.hash = `view=${encodeURIComponent(anchorId)}`;
      history.replaceState({svgAnchor: anchorId}, "", url);
    } catch (_) { /* local SVG viewers may not expose writable history */ }
  }
  function navigateTo(anchorId, options = {}) {
    if (!navigationPlan) return cameraSnapshot();
    const anchor = navigationAnchors.get(anchorId);
    if (!anchor) throw new Error("unknown navigation anchor: " + anchorId);
    pauseCamera();
    const snapshot = commitCamera(anchor.viewBox, anchor.id, cameraTimeMs, null);
    if (options.updateHash !== false) updateNavigationHash(anchor.id);
    return snapshot;
  }
  function setCamera(raw) {
    pauseCamera();
    return commitCamera(raw, null, cameraTimeMs, null);
  }
  function fitOverview(options = {}) {
    if (!navigationPlan) return cameraSnapshot();
    return navigateTo("world", options);
  }
  function interpolateCamera(first, second, progress) {
    const clamped = Math.min(Math.max(progress, 0), 1);
    const eased = clamped * clamped * (3 - 2 * clamped);
    const firstCenter = [first[0] + first[2] / 2, first[1] + first[3] / 2];
    const secondCenter = [second[0] + second[2] / 2, second[1] + second[3] / 2];
    const centerX = firstCenter[0] + (secondCenter[0] - firstCenter[0]) * eased;
    const centerY = firstCenter[1] + (secondCenter[1] - firstCenter[1]) * eased;
    const width = Math.exp(Math.log(first[2]) + (Math.log(second[2]) - Math.log(first[2])) * eased);
    const height = Math.exp(Math.log(first[3]) + (Math.log(second[3]) - Math.log(first[3])) * eased);
    return [centerX - width / 2, centerY - height / 2, width, height];
  }
  function routeStopAt(time) {
    const stops = navigationPlan.route.stops;
    if (time === Number(navigationPlan.route.durationMs)) return stops.at(-1);
    return stops.find((stop) => time >= Number(stop.startMs) && time < Number(stop.endMs)) || stops.at(-1);
  }
  function seekCamera(rawMs) {
    if (!navigationPlan) return cameraSnapshot();
    let nextTime = numeric(rawMs, "camera timeMs");
    const duration = Number(navigationPlan.route.durationMs);
    if (navigationPlan.route.loop && nextTime > 0 && nextTime >= duration) nextTime %= duration;
    nextTime = Math.min(Math.max(nextTime, 0), duration);
    const stop = routeStopAt(nextTime);
    const from = navigationAnchors.get(stop.fromAnchorId);
    const target = navigationAnchors.get(stop.anchorId);
    const travel = Number(stop.arrivalMs) - Number(stop.startMs);
    const progress = travel <= 0 ? 1 : Math.min(Math.max((nextTime - Number(stop.startMs)) / travel, 0), 1);
    const camera = progress >= 1
      ? target.viewBox
      : interpolateCamera(from.viewBox, target.viewBox, progress);
    return commitCamera(camera, progress >= 1 ? target.id : null, nextTime, stop.id);
  }
  function cameraRouteAnchors() {
    return [...new Set(navigationPlan.route.stops.map((stop) => stop.anchorId))];
  }
  function adjacentAnchor(direction) {
    if (!navigationPlan) return cameraSnapshot();
    const anchors = cameraRouteAnchors();
    const currentIndex = Math.max(0, anchors.indexOf(cameraAnchorId));
    const nextIndex = Math.min(Math.max(currentIndex + direction, 0), anchors.length - 1);
    return navigateTo(anchors[nextIndex]);
  }
  function updateCameraPlaybackControl() {
    const control = root.querySelector('[data-camera-action="tour"]');
    if (!control) return;
    const disabled = !navigationPlan || reduceMotion;
    const text = control.querySelector("text");
    if (text) text.textContent = disabled ? "CUTS" : (cameraPlaying ? "PAUSE" : "TOUR");
    control.setAttribute("aria-label", disabled
      ? "Camera autoplay disabled by reduced motion preference"
      : (cameraPlaying ? "Pause camera tour" : "Play camera tour"));
    control.setAttribute("aria-pressed", String(!disabled && cameraPlaying));
    control.setAttribute("aria-disabled", String(disabled));
    control.setAttribute("tabindex", disabled ? "-1" : "0");
  }
  function cameraTick(now) {
    if (!cameraPlaying || !navigationPlan) return;
    const duration = Number(navigationPlan.route.durationMs);
    const raw = cameraPlayStartedTime + (now - cameraPlayStartedAt);
    seekCamera(navigationPlan.route.loop ? raw % duration : Math.min(raw, duration));
    if (!navigationPlan.route.loop && raw >= duration) { pauseCamera(); return; }
    cameraTimer = window.setTimeout(() => cameraTick(performance.now()), 33);
  }
  function playCamera() {
    if (!navigationPlan || reduceMotion || cameraPlaying) {
      updateCameraPlaybackControl();
      return cameraSnapshot();
    }
    cameraPlaying = true;
    cameraPlayStartedAt = performance.now();
    cameraPlayStartedTime = cameraTimeMs;
    cameraTimer = window.setTimeout(() => cameraTick(performance.now()), 0);
    updateCameraPlaybackControl();
    return cameraSnapshot();
  }
  function pauseCamera() {
    cameraPlaying = false;
    if (cameraTimer !== null) window.clearTimeout(cameraTimer);
    cameraTimer = null;
    updateCameraPlaybackControl();
    return cameraSnapshot();
  }
  function resetCamera() {
    pauseCamera();
    cameraTimeMs = 0;
    return navigateTo(navigationPlan.initialAnchorId);
  }
  function renderAll(changedValues = null) {
    const values = {...sourceValues, ...derivedValues};
    for (const module of plan.modules) {
      const group = root.querySelector(`[data-module-id="${CSS.escape(module.id)}"]`);
      if (!group) throw new Error("missing module DOM: " + module.id);
      for (const binding of module.bindings) {
        if (changedValues && !changedValues.has(binding.value)) continue;
        const elements = group.querySelectorAll(binding.selector);
        if (!elements.length) throw new Error("missing binding target: " + module.id + " " + binding.selector);
        elements.forEach((element) => renderBinding(element, binding, values[binding.value]));
      }
      layoutModule(group);
    }
    const focusedModules = focusId && focusGroups.has(focusId) ? new Set(focusGroups.get(focusId).moduleIds) : null;
    root.querySelectorAll("[data-module-id]").forEach((group) => {
      group.setAttribute("data-focused", focusedModules ? String(focusedModules.has(group.dataset.moduleId)) : "true");
    });
    root.querySelectorAll("[data-module-focus-id]").forEach((control) => {
      control.setAttribute("aria-pressed", String(Boolean(focusId && control.dataset.moduleFocusId === focusId)));
    });
    root.querySelectorAll("[data-relationship-id]").forEach((relationship, index) => {
      const source = relationship.dataset.sourceModule;
      const target = relationship.dataset.targetModule;
      const active = Boolean(focusedModules && (
        focusedModules.size === 1
          ? (focusedModules.has(source) || focusedModules.has(target))
          : (focusedModules.has(source) && focusedModules.has(target))
      ));
      relationship.setAttribute("data-active", String(active));
      const path = relationship.querySelector(".relationship-path");
      const pulse = relationship.querySelector("[data-relationship-pulse]");
      if (!path || !pulse) return;
      const length = path.getTotalLength();
      const progress = Math.min(Math.max(phaseProgress, 0), 1);
      const point = path.getPointAtLength(length * progress);
      pulse.setAttribute("cx", String(point.x));
      pulse.setAttribute("cy", String(point.y));
      pulse.setAttribute("opacity", active && Boolean(plan.timeline) && !reduceMotion ? "1" : "0");
      pulse.setAttribute("data-pulse-index", String(index));
    });
    root.setAttribute("data-focus-id", focusId || "");
    root.setAttribute("data-current-scenario", scenarioId || "custom");
    root.setAttribute("data-time-ms", String(timeMs));
    root.setAttribute("data-phase-id", phaseId || "");
    root.setAttribute("data-phase-progress", String(phaseProgress));
    const timelineRail = root.querySelector("[data-timeline-rail]");
    if (timelineRail && plan.timeline) {
      const duration = Number(plan.timeline.durationMs) || 1;
      const cycleProgress = Math.min(Math.max(timeMs / duration, 0), 1);
      const trackWidth = Number(timelineRail.dataset.trackWidth) || 0;
      const progressMark = timelineRail.querySelector("[data-timeline-progress]");
      if (progressMark) progressMark.setAttribute("width", String(trackWidth * cycleProgress));
      const phaseLabel = timelineRail.querySelector("[data-timeline-label]");
      if (phaseLabel) {
        const phase = phaseId
          ? plan.timeline.phases.find((item) => item.id === phaseId)
          : null;
        const scenario = scenarioId ? scenarios.get(scenarioId) : null;
        const readable = phase
          ? (phase.label || phase.id.replace(/-/g, " ").replace(/\b\w/g, (letter) => letter.toUpperCase()))
          : (scenario ? scenario.label : "Timeline ready");
        phaseLabel.textContent = phase
          ? `${readable} · ${Math.round(phaseProgress * 100)}% phase`
          : `${readable} · scenario`;
      }
      timelineRail.setAttribute("aria-valuenow", String(timeMs));
      timelineRail.setAttribute(
        "aria-valuetext",
        `${phaseId || "timeline"}, ${Math.round(cycleProgress * 100)} percent`
      );
    }
    root.setAttribute("data-state-revision", String(revision));
    root.querySelectorAll("[data-action='scenario']").forEach((control) => {
      control.setAttribute("aria-pressed", String(control.dataset.scenarioId === scenarioId));
    });
  }
  function currentState() {
    return {sourceValues: sortedObject(sourceValues), derivedValues: sortedObject(derivedValues)};
  }
  function snapshot() {
    return {
      version: 1,
      compositionId: plan.compositionId,
      revision,
      scenarioId,
      sourceValues: sortedObject(sourceValues),
      derivedValues: sortedObject(derivedValues),
      focusId,
      timeMs,
      phaseId,
      phaseProgress,
      motion: reduceMotion ? "reduced" : "full"
    };
  }
  function serializeSnapshot() { return JSON.stringify(stable(snapshot())); }
  function emit() {
    const detail = snapshot();
    root.dispatchEvent(new CustomEvent("svg-sync-change", {detail}));
    return detail;
  }
  function semanticEqual(nextSource, nextScenario, nextFocus, nextTime, nextPhase) {
    return JSON.stringify(sortedObject(nextSource)) === JSON.stringify(sortedObject(sourceValues)) &&
      nextScenario === scenarioId && nextFocus === focusId && nextTime === timeMs && nextPhase === phaseId;
  }
  function commit(nextSource, nextScenario, nextFocus, nextTime, nextPhase) {
    const nextDerived = computeDerived(nextSource);
    if (semanticEqual(nextSource, nextScenario, nextFocus, nextTime, nextPhase)) return snapshot();
    const changedValues = new Set();
    for (const [id, value] of Object.entries(nextSource)) {
      if (sourceValues[id] !== value) changedValues.add(id);
    }
    for (const [id, value] of Object.entries(nextDerived)) {
      if (derivedValues[id] !== value) changedValues.add(id);
    }
    sourceValues = nextSource;
    derivedValues = nextDerived;
    scenarioId = nextScenario;
    focusId = nextFocus;
    timeMs = nextTime;
    phaseId = nextPhase;
    revision += 1;
    renderAll(changedValues);
    return emit();
  }
  function setState(patch) {
    const next = validatePatch(patch);
    return commit(next, null, focusId, timeMs, phaseId);
  }
  function applyScenario(id) {
    const scenario = scenarios.get(id);
    if (!scenario) throw new Error("unknown scenario: " + id);
    const defaults = Object.fromEntries(plan.concepts.map((item) => [item.id, Number(item.default)]));
    const next = validatePatch.call(null, {...defaults, ...scenario.values});
    return commit(next, id, focusId, timeMs, phaseId);
  }
  function setFocus(id) {
    if (id !== null && !focusGroups.has(id)) throw new Error("unknown focus group: " + id);
    return commit({...sourceValues}, scenarioId, id, timeMs, phaseId);
  }
  function phaseAt(ms) {
    if (!plan.timeline) return null;
    if (plan.timeline.loop && ms === plan.timeline.durationMs) return plan.timeline.phases[0];
    if (ms === plan.timeline.durationMs) return plan.timeline.phases.at(-1);
    return plan.timeline.phases.find((phase) => ms >= phase.startMs && ms < phase.endMs) || plan.timeline.phases.at(-1);
  }
  function timelineBaseline() {
    const defaults = Object.fromEntries(plan.concepts.map((item) => [item.id, Number(item.default)]));
    const timelineBaseScenarioId = plan.timeline && plan.timeline.baseScenario
      ? plan.timeline.baseScenario
      : plan.initialScenario;
    const timelineBaseScenario = scenarios.get(timelineBaseScenarioId);
    return validatePatch(
      timelineBaseScenario ? timelineBaseScenario.values : {},
      defaults
    );
  }
  function phaseTarget(phase, baseline) {
    return validatePatch(phase && phase.values ? phase.values : {}, baseline);
  }
  function easeTimeline(value) {
    const clamped = Math.min(Math.max(value, 0), 1);
    const mode = plan.timeline && plan.timeline.interpolation
      ? plan.timeline.interpolation
      : "step";
    if (mode === "step") return 1;
    if (mode === "linear") return clamped;
    return clamped * clamped * (3 - 2 * clamped);
  }
  function timelineSample(ms) {
    const phase = phaseAt(ms);
    const phases = plan.timeline.phases;
    const index = Math.max(0, phases.indexOf(phase));
    const baseline = timelineBaseline();
    const startSource = index === 0 ? baseline : phaseTarget(phases[index - 1], baseline);
    const endSource = phaseTarget(phase, baseline);
    const span = Math.max(1, Number(phase.endMs) - Number(phase.startMs));
    const rawProgress = ms === plan.timeline.durationMs
      ? 1
      : (ms - Number(phase.startMs)) / span;
    const eased = easeTimeline(rawProgress);
    const globalMode = plan.timeline && plan.timeline.interpolation
      ? plan.timeline.interpolation
      : "step";
    const source = {};
    for (const id of sourceDefs.keys()) {
      const definition = sourceDefs.get(id);
      const mix = globalMode === "step" || (definition && definition.interpolation === "step")
        ? 1
        : eased;
      source[id] = startSource[id] + (endSource[id] - startSource[id]) * mix;
    }
    return {
      source,
      phase,
      progress: Math.min(Math.max(rawProgress, 0), 1),
      easedProgress: eased
    };
  }
  function seek(rawMs) {
    if (!plan.timeline) return snapshot();
    let nextTime = numeric(rawMs, "timeMs");
    const duration = plan.timeline.durationMs;
    if (plan.timeline.loop && nextTime > 0 && nextTime >= duration) nextTime %= duration;
    nextTime = Math.min(Math.max(nextTime, 0), duration);
    const sample = timelineSample(nextTime);
    phaseProgress = sample.progress;
    return commit(
      sample.source,
      null,
      sample.phase && sample.phase.focusId ? sample.phase.focusId : null,
      nextTime,
      sample.phase ? sample.phase.id : null
    );
  }
  function tick(now) {
    if (!playing || !plan.timeline) return;
    const elapsed = now - playStartedAt;
    const raw = playStartedTime + elapsed;
    seek(plan.timeline.loop ? raw % plan.timeline.durationMs : Math.min(raw, plan.timeline.durationMs));
    if (!plan.timeline.loop && raw >= plan.timeline.durationMs) { pause(); return; }
    animationTimer = window.setTimeout(() => tick(performance.now()), 33);
  }
  function updatePlaybackControl() {
    const control = root.querySelector('[data-action="play"]');
    if (!control) return;
    const text = control.querySelector("text");
    const disabled = !plan.timeline || reduceMotion;
    const visibleLabel = disabled ? "Motion disabled" : (playing ? "Pause" : "Play");
    const accessibleLabel = disabled
      ? "Timeline playback disabled by reduced motion preference"
      : (playing ? "Pause the master timeline" : "Play the master timeline");
    if (text) text.textContent = visibleLabel;
    control.setAttribute("aria-label", accessibleLabel);
    control.setAttribute("aria-pressed", String(!disabled && playing));
    control.setAttribute("aria-disabled", String(disabled));
    control.setAttribute("tabindex", disabled ? "-1" : "0");
  }
  function play() {
    if (!plan.timeline || reduceMotion || playing) { updatePlaybackControl(); return snapshot(); }
    playing = true;
    playStartedAt = performance.now();
    playStartedTime = timeMs;
    animationTimer = window.setTimeout(() => tick(performance.now()), 0);
    updatePlaybackControl();
    return snapshot();
  }
  function pause() {
    playing = false;
    if (animationTimer !== null) window.clearTimeout(animationTimer);
    animationTimer = null;
    updatePlaybackControl();
    return snapshot();
  }
  function reset() {
    pause();
    phaseProgress = 0;
    const scenario = scenarios.get(plan.initialScenario);
    const defaults = Object.fromEntries(plan.concepts.map((item) => [item.id, Number(item.default)]));
    const next = validatePatch({...defaults, ...scenario.values});
    return commit(next, scenario.id, null, 0, null);
  }
  function activate(control) {
    if (control.getAttribute("aria-disabled") === "true") return;
    const action = control.dataset.action;
    if (action === "scenario") {
      pause();
      phaseProgress = 0;
      applyScenario(control.dataset.scenarioId);
    }
    else if (action === "play") playing ? pause() : play();
    else if (action === "reset") reset();
  }
  root.querySelectorAll("[data-action]").forEach((control) => {
    control.addEventListener("click", () => activate(control));
    control.addEventListener("keydown", (event) => {
      if (event.key === "Enter" || event.key === " ") { event.preventDefault(); activate(control); }
    });
  });
  root.querySelectorAll("[data-module-focus-id]").forEach((control) => {
    const toggleModuleFocus = () => {
      pause();
      const requested = control.dataset.moduleFocusId || null;
      setFocus(focusId === requested ? null : requested);
    };
    control.addEventListener("click", toggleModuleFocus);
    control.addEventListener("keydown", (event) => {
      if (event.key === "Enter" || event.key === " ") {
        event.preventDefault();
        toggleModuleFocus();
      }
    });
  });
  const timelineRail = root.querySelector("[data-timeline-rail]");
  if (timelineRail && plan.timeline) {
    const seekFromPointer = (event) => {
      const matrix = root.getScreenCTM();
      if (!matrix) return;
      const point = root.createSVGPoint();
      point.x = event.clientX;
      point.y = event.clientY;
      const local = point.matrixTransform(matrix.inverse());
      const x = Number(timelineRail.dataset.trackX) || 0;
      const width = Number(timelineRail.dataset.trackWidth) || 1;
      const ratio = Math.min(Math.max((local.x - x) / width, 0), 1);
      pause();
      seek(ratio * plan.timeline.durationMs);
    };
    timelineRail.addEventListener("pointerdown", seekFromPointer);
    timelineRail.addEventListener("keydown", (event) => {
      if (!["ArrowLeft", "ArrowRight", "Home", "End"].includes(event.key)) return;
      event.preventDefault();
      pause();
      if (event.key === "Home") seek(0);
      else if (event.key === "End") seek(plan.timeline.durationMs);
      else seek(timeMs + (event.key === "ArrowRight" ? 1 : -1) * plan.timeline.durationMs / 100);
    });
  }
  function activateCameraControl(control) {
    const target = control.dataset.navTarget;
    if (target) { navigateTo(target); return; }
    const action = control.dataset.cameraAction;
    if (action === "previous") adjacentAnchor(-1);
    else if (action === "next") adjacentAnchor(1);
    else if (action === "up") {
      const anchor = cameraAnchorId ? navigationAnchors.get(cameraAnchorId) : null;
      if (anchor?.kind === "module" && navigationAnchors.has(anchor.parentId)) navigateTo(anchor.parentId);
      else fitOverview();
    }
    else if (action === "home") fitOverview();
    else if (action === "tour") cameraPlaying ? pauseCamera() : playCamera();
  }
  root.querySelectorAll("[data-camera-action], [data-nav-target]").forEach((control) => {
    control.addEventListener("click", (event) => {
      event.stopPropagation();
      activateCameraControl(control);
    });
    control.addEventListener("keydown", (event) => {
      if (event.key === "Enter" || event.key === " ") {
        event.preventDefault();
        event.stopPropagation();
        activateCameraControl(control);
      }
    });
  });
  if (worldViewport && navigationPlan) {
    let drag = null;
    worldViewport.addEventListener("pointerdown", (event) => {
      if (event.button !== 0 || event.target.closest("[role='button'], [role='slider']")) return;
      pauseCamera();
      drag = {pointerId: event.pointerId, x: event.clientX, y: event.clientY, camera: [...cameraViewBox]};
      worldViewport.setPointerCapture(event.pointerId);
      event.preventDefault();
    });
    worldViewport.addEventListener("pointermove", (event) => {
      if (!drag || drag.pointerId !== event.pointerId) return;
      const box = worldViewport.getBoundingClientRect();
      if (!box.width || !box.height) return;
      const dx = (event.clientX - drag.x) * drag.camera[2] / box.width;
      const dy = (event.clientY - drag.y) * drag.camera[3] / box.height;
      commitCamera(
        [drag.camera[0] - dx, drag.camera[1] - dy, drag.camera[2], drag.camera[3]],
        null,
        cameraTimeMs,
        null
      );
    });
    const endDrag = (event) => {
      if (!drag || drag.pointerId !== event.pointerId) return;
      if (worldViewport.hasPointerCapture(event.pointerId)) worldViewport.releasePointerCapture(event.pointerId);
      drag = null;
    };
    worldViewport.addEventListener("pointerup", endDrag);
    worldViewport.addEventListener("pointercancel", endDrag);
    worldViewport.addEventListener("wheel", (event) => {
      pauseCamera();
      const box = worldViewport.getBoundingClientRect();
      if (!box.width || !box.height) return;
      const ratioX = Math.min(Math.max((event.clientX - box.left) / box.width, 0), 1);
      const ratioY = Math.min(Math.max((event.clientY - box.top) / box.height, 0), 1);
      const worldX = cameraViewBox[0] + ratioX * cameraViewBox[2];
      const worldY = cameraViewBox[1] + ratioY * cameraViewBox[3];
      const scale = Math.exp(Math.min(Math.max(event.deltaY * 0.0015, -0.7), 0.7));
      const width = cameraViewBox[2] * scale;
      const height = cameraViewBox[3] * scale;
      commitCamera(
        [worldX - ratioX * width, worldY - ratioY * height, width, height],
        null,
        cameraTimeMs,
        null
      );
      event.preventDefault();
    }, {passive: false});
  }
  root.addEventListener("keydown", (event) => {
    if (event.key === "Escape") { pause(); pauseCamera(); setFocus(null); }
    if (navigationPlan && !event.defaultPrevented) {
      const panX = cameraViewBox[2] * 0.08;
      const panY = cameraViewBox[3] * 0.08;
      if (event.key === "Home" || event.key === "0") { event.preventDefault(); fitOverview(); }
      else if (event.key === "+" || event.key === "=") {
        event.preventDefault();
        const width = cameraViewBox[2] / 1.35;
        const height = cameraViewBox[3] / 1.35;
        setCamera([
          cameraViewBox[0] + (cameraViewBox[2] - width) / 2,
          cameraViewBox[1] + (cameraViewBox[3] - height) / 2,
          width,
          height
        ]);
      } else if (event.key === "-" || event.key === "_") {
        event.preventDefault();
        const width = cameraViewBox[2] * 1.35;
        const height = cameraViewBox[3] * 1.35;
        setCamera([
          cameraViewBox[0] - (width - cameraViewBox[2]) / 2,
          cameraViewBox[1] - (height - cameraViewBox[3]) / 2,
          width,
          height
        ]);
      } else if (["ArrowLeft", "ArrowRight", "ArrowUp", "ArrowDown"].includes(event.key) &&
          !event.target.closest("[role='slider'], [role='button']")) {
        event.preventDefault();
        setCamera([
          cameraViewBox[0] + (event.key === "ArrowLeft" ? -panX : (event.key === "ArrowRight" ? panX : 0)),
          cameraViewBox[1] + (event.key === "ArrowUp" ? -panY : (event.key === "ArrowDown" ? panY : 0)),
          cameraViewBox[2],
          cameraViewBox[3]
        ]);
      }
    }
    if ((event.key === "r" || event.key === "R") && !event.defaultPrevented) {
      reset();
      if (navigationPlan) resetCamera();
      if (plan.timeline && !reduceMotion) play();
    }
  });
  const initial = scenarios.get(plan.initialScenario);
  sourceValues = validatePatch(initial.values);
  derivedValues = computeDerived(sourceValues);
  scenarioId = initial.id;
  renderAll();
  if (navigationPlan) {
    let requestedAnchor = navigationPlan.initialAnchorId;
    try {
      const decoded = decodeURIComponent(window.location.hash.replace(/^#/, ""));
      const candidate = decoded.startsWith("view=") ? decoded.slice(5) : decoded;
      if (navigationAnchors.has(candidate)) requestedAnchor = candidate;
    } catch (_) { /* malformed hashes fall back to the overview */ }
    const initialCameraAnchor = navigationAnchors.get(requestedAnchor);
    cameraViewBox = normalizedCamera(initialCameraAnchor.viewBox);
    cameraAnchorId = initialCameraAnchor.id;
    cameraTier = initialCameraAnchor.zoomTier;
    cameraTimeMs = 0;
    cameraStopId = null;
    updateCameraHud();
    window.addEventListener("hashchange", () => {
      try {
        const decoded = decodeURIComponent(window.location.hash.replace(/^#/, ""));
        const candidate = decoded.startsWith("view=") ? decoded.slice(5) : decoded;
        navigateTo(navigationAnchors.has(candidate) ? candidate : navigationPlan.initialAnchorId, {updateHash: false});
      } catch (_) {
        navigateTo(navigationPlan.initialAnchorId, {updateHash: false});
      }
    });
  }
  root.classList.add("svg-sync-ready");
  root.setAttribute("data-sync-ready", "true");
  updatePlaybackControl();
  updateCameraPlaybackControl();
  const ready = Promise.resolve();
  window.svgSync = Object.freeze({
    version: "1.0", ready,
    getPlan: () => clone(plan),
    getState: () => clone(currentState()),
    setState, applyScenario, setFocus, seek, play, pause, reset,
    getCamera: () => clone(cameraSnapshot()),
    setCamera, navigateTo, seekCamera, fitOverview,
    nextAnchor: () => adjacentAnchor(1),
    previousAnchor: () => adjacentAnchor(-1),
    playCamera, pauseCamera, resetCamera,
    snapshot: () => clone(snapshot()),
    serializeSnapshot
  });
  if (plan.timeline && plan.timeline.autoplay && !reduceMotion) {
    seek(0);
    const startAutoplay = () => { if (!playing) play(); };
    if (document.readyState === "complete") startAutoplay();
    else window.addEventListener("load", startAutoplay, {once: true});
  }
  if (navigationPlan && navigationPlan.route.autoplay && !reduceMotion) {
    seekCamera(0);
    const startCameraAutoplay = () => { if (!cameraPlaying) playCamera(); };
    if (document.readyState === "complete") startCameraAutoplay();
    else window.addEventListener("load", startCameraAutoplay, {once: true});
  }
})();
"""


def build_svg(plan: dict[str, Any]) -> str:
    source, derived = initial_values(plan)
    values = {**source, **derived}
    _, _, width, height = (float(item) for item in plan["viewBox"])
    locale = str(plan.get("locale", "en-US"))
    metadata = json.dumps(plan, ensure_ascii=False, separators=(",", ":")).replace("]]>", "]]\\u003e")
    canonical_values = [*plan["concepts"], *plan.get("derived", [])]
    concept_tokens = "\n".join(
        f"      --concept-{item['id']}: {color_for_index(index)};"
        for index, item in enumerate(canonical_values)
    )
    style = f"""
    :root {{
      --canvas: #f5f7fb; --surface: #ffffff; --ink: #172033; --muted: #637087;
      --line: #d6dce8; --accent: #2563eb; --focus: #f59e0b;
{concept_tokens}
    }}
    * {{ box-sizing: border-box; }}
    text {{ font-family: Inter, ui-sans-serif, system-ui, -apple-system, "Segoe UI", sans-serif; fill: var(--ink); }}
    .canvas {{ fill: var(--canvas); }}
    .title {{ font-size: 28px; font-weight: 760; letter-spacing: -0.02em; }}
    .subtitle {{ font-size: 13px; fill: var(--muted); }}
    .provenance {{ font-size: 10.5px; fill: var(--muted); letter-spacing: 0.02em; }}
    .focus-region-label-plaque {{ fill: var(--canvas); fill-opacity: 1; }}
    .focus-region-label {{ font-size: 10px; font-weight: 760; letter-spacing: 0.1em; fill: #475569; }}
    .module-frame {{ fill: var(--surface); fill-opacity: 0.5; stroke: transparent; stroke-width: 1.5; rx: 8; }}
    .module-kicker {{ font-size: 10px; font-weight: 760; letter-spacing: 0.12em; fill: var(--accent); }}
    .module-question {{ font-size: 11px; fill: var(--muted); }}
    .module-claim {{ font-size: 14px; font-weight: 620; }}
    .module-content text {{ font-size: 11px; }}
    .module-placeholder {{ opacity: 0.78; }}
    .placeholder-mark {{ fill: color-mix(in srgb, var(--accent) 24%, white); stroke: var(--accent); stroke-width: 1.5; }}
    .placeholder-value {{ font-size: 12px; fill: var(--muted); }}
    .sync-module .module-frame, .sync-module .module-content :is(path, rect, line, circle, ellipse, polygon, polyline) {{ transition: filter 180ms ease; }}
    .module-focus-control {{ cursor: pointer; outline: none; }}
    .module-focus-control rect {{ fill: #eef3fb; stroke: #8ba0bf; stroke-width: 1.25; }}
    .module-focus-control text {{ font-size: 9.5px; font-weight: 720; fill: #334155; pointer-events: none; }}
    .module-focus-control:focus rect, .module-focus-control[aria-pressed="true"] rect {{ fill: #dbeafe; stroke: var(--accent); stroke-width: 2.5; }}
    [data-focus-id]:not([data-focus-id=""]) .sync-module[data-focused="false"] .module-frame,
    [data-focus-id]:not([data-focus-id=""]) .sync-module[data-focused="false"] .module-content :is(path, rect, line, circle, ellipse, polygon, polyline) {{ filter: opacity(48%) saturate(58%); }}
    .control-button {{ cursor: pointer; outline: none; }}
    .control-button rect {{ fill: var(--surface); stroke: var(--line); rx: 8; }}
    .control-button text {{ font-size: 11px; font-weight: 650; pointer-events: none; }}
    .control-button[aria-pressed="true"] rect, .control-button:focus rect {{ stroke: var(--accent); stroke-width: 2.5; }}
    .control-button[aria-disabled="true"] {{ cursor: not-allowed; }}
    .control-button[aria-disabled="true"] rect {{ fill: #eef1f6; stroke: #c9d0dc; }}
    .interactive-control {{ display: none; }}
    .svg-sync-ready .interactive-control {{ display: inline; }}
    .timeline-track {{ fill: #dbe3f0; }}
    .timeline-progress {{ fill: var(--accent); }}
    .timeline-label {{ font-size: 10px; font-weight: 650; fill: #475569; }}
    .timeline-scrubber:focus .timeline-track {{ stroke: var(--accent); stroke-width: 2; }}
    .composition-relationships {{ pointer-events: none; }}
    .relationship-path {{ vector-effect: non-scaling-stroke; opacity: 0.86; transition: opacity 180ms ease, stroke 180ms ease, stroke-width 180ms ease; }}
    .relationship-key-plaque {{ fill: var(--canvas); fill-opacity: 0.96; }}
    .relationship-key-label {{ font-size: 9.25px; font-weight: 620; fill: #475569; }}
    [data-relationship-id][data-kind="feedback"] .relationship-path {{ stroke: #8a4b08; }}
    [data-relationship-id][data-active="true"] .relationship-path {{ stroke: var(--accent); stroke-width: 3.5; opacity: 0.96; }}
    [data-relationship-id][data-kind="feedback"][data-active="true"] .relationship-path {{ stroke: #b45309; stroke-width: 4; }}
    .relationship-pulse {{ pointer-events: none; filter: drop-shadow(0 0 4px color-mix(in srgb, var(--accent) 70%, transparent)); }}
    #composition-world-viewport {{ touch-action: none; cursor: grab; }}
    #composition-world-viewport:active {{ cursor: grabbing; }}
    .world-field {{ fill: #f2f3fa; }}
    .world-district-links {{ pointer-events: none; }}
    .world-link-halo {{ fill: none; stroke: #f8fafc; stroke-width: 16; vector-effect: non-scaling-stroke; opacity: 0.94; }}
    .world-link-path {{ fill: none; stroke: #53627a; stroke-width: 3; vector-effect: non-scaling-stroke; opacity: 0.52; }}
    .world-link-primary .world-link-path {{ stroke-width: 5.5; opacity: 0.92; }}
    .world-link-primary .world-link-halo {{ stroke-width: 15; opacity: 0.98; }}
    .world-link-secondary .world-link-halo {{ stroke-width: 11; opacity: 0.72; }}
    .world-link[data-kind="feedback"] .world-link-path {{ stroke: #b45309; }}
    .world-link-chevrons {{ pointer-events: none; }}
    .world-link-chevron {{ fill: none; stroke: #53627a; stroke-width: 8; stroke-linecap: round; stroke-linejoin: round; vector-effect: non-scaling-stroke; }}
    .world-link[data-route-traveling="true"] .world-link-path {{ stroke: var(--accent); stroke-width: 9; opacity: 1; }}
    .world-link[data-route-traveling="true"] .world-link-halo {{ stroke-width: 22; opacity: 1; }}
    .world-link[data-route-traveling="true"] .world-link-chevron {{ stroke: var(--accent); stroke-width: 11; }}
    .world-link-label rect {{ fill: #f8fafc; fill-opacity: 0.96; stroke: #cbd5e1; stroke-width: 1.5; vector-effect: non-scaling-stroke; }}
    .world-link-label text {{ font-size: 72px; font-weight: 760; fill: #334155; }}
    .world-local-branches {{ pointer-events: none; }}
    .world-local-branch {{ fill: none; stroke: var(--district-accent); stroke-width: 3.5; stroke-opacity: 0.68; vector-effect: non-scaling-stroke; }}
    .world-local-root-branch {{ stroke-width: 5.5; stroke-opacity: 0.9; }}
    .world-local-orbit-ring {{ stroke-dasharray: 18 14; stroke-width: 5; }}
    .world-district[data-local-armature="lanes"] .world-local-branch {{ stroke-linejoin: round; stroke-width: 5; }}
    .world-district[data-local-armature="branch"] .world-local-root-branch {{ stroke-width: 7; }}
    .world-module-node-halo {{ fill: color-mix(in srgb, var(--district-accent) 14%, transparent); stroke: var(--district-accent); stroke-width: 4; stroke-opacity: 0.64; vector-effect: non-scaling-stroke; }}
    .world-module-node-core {{ fill: #ffffff; stroke: var(--district-accent); stroke-width: 4; vector-effect: non-scaling-stroke; }}
    .world-module-node[data-local-root="true"] .world-module-node-halo {{ stroke-width: 6; }}
    .world-module-node-index {{ font-size: 40px; font-weight: 840; fill: var(--district-accent); }}
    .world-module-node-label-plaque {{ fill: #ffffff; fill-opacity: 0.94; stroke: color-mix(in srgb, var(--district-accent) 42%, #cbd5e1); stroke-width: 2; vector-effect: non-scaling-stroke; }}
    .world-module-node-label {{ font-size: 42px; font-weight: 740; fill: #273449; }}
    .district-singleton-preview {{ opacity: 0; pointer-events: none; }}
    .district-singleton-preview-branch {{ stroke: var(--district-accent); stroke-width: 3; stroke-opacity: 0.42; vector-effect: non-scaling-stroke; }}
    .district-singleton-preview-node {{ fill: #ffffff; stroke: var(--district-accent); stroke-width: 3; vector-effect: non-scaling-stroke; }}
    .district-singleton-preview-label {{ font-size: 24px; font-weight: 680; fill: #475569; paint-order: stroke; stroke: #ffffff; stroke-width: 6; stroke-linejoin: round; }}
    .world-module-nav-control {{ outline: none; cursor: pointer; }}
    .world-module-nav-control circle {{ fill: transparent; stroke: transparent; stroke-width: 5; vector-effect: non-scaling-stroke; }}
    .world-module-nav-control:focus circle {{ stroke: var(--district-accent); }}
    .district-field {{ fill: color-mix(in srgb, var(--district-accent) 8%, white); stroke: color-mix(in srgb, var(--district-accent) 72%, #334155); stroke-width: 3; vector-effect: non-scaling-stroke; }}
    .district-hub-halo {{ fill: color-mix(in srgb, var(--district-accent) 12%, transparent); stroke: var(--district-accent); stroke-width: 4; vector-effect: non-scaling-stroke; pointer-events: none; }}
    .district-hub {{ fill: #ffffff; stroke: var(--district-accent); stroke-width: 5; vector-effect: non-scaling-stroke; pointer-events: none; }}
    .world-district[data-world-root="true"] .district-hub-halo {{ stroke-width: 9; }}
    .world-district[data-world-root="true"] .district-hub {{ stroke-width: 8; }}
    .district-index {{ font-size: 42px; font-weight: 820; fill: var(--district-accent); }}
    .district-title {{ font-size: 96px; font-weight: 820; letter-spacing: -0.035em; fill: color-mix(in srgb, var(--district-accent) 78%, #172033); }}
    .district-title-world-plaque {{ opacity: 0; fill: #ffffff; fill-opacity: 0.94; stroke: color-mix(in srgb, var(--district-accent) 58%, #cbd5e1); stroke-width: 3; vector-effect: non-scaling-stroke; }}
    .district-title-world {{ opacity: 0; font-size: 118px; paint-order: stroke; stroke: #ffffff; stroke-width: 10; stroke-linejoin: round; }}
    .district-summary {{ font-size: 34px; font-weight: 580; fill: #475569; }}
    .district-nav-control {{ outline: none; cursor: pointer; }}
    .district-nav-control circle {{ fill: transparent; stroke: transparent; stroke-width: 7; vector-effect: non-scaling-stroke; }}
    .district-nav-control:focus circle {{ stroke: var(--district-accent); }}
    [data-world-mode="true"] .sync-module .module-frame {{ fill-opacity: 0.86; stroke: var(--district-accent); stroke-width: 2; vector-effect: non-scaling-stroke; rx: 24; }}
    [data-world-mode="true"] .sync-module {{ filter: drop-shadow(0 10px 18px rgb(15 23 42 / 0.12)); }}
    .svg-sync-ready[data-world-mode="true"][data-camera-tier="world"] .district-field {{ opacity: 0; }}
    .svg-sync-ready[data-world-mode="true"][data-camera-tier="world"] :is(.district-title-detail, .district-summary, .world-module-node-label, .world-module-node-label-plaque, .district-singleton-preview) {{ opacity: 0; pointer-events: none; }}
    .svg-sync-ready[data-world-mode="true"][data-camera-tier="world"] :is(.district-title-world, .district-title-world-plaque) {{ opacity: 1; }}
    .svg-sync-ready[data-world-mode="true"][data-camera-tier="world"] .world-link-secondary:not([data-kind="feedback"]) {{ opacity: 0.07; }}
    .svg-sync-ready[data-world-mode="true"][data-camera-tier="world"] .world-link-secondary[data-kind="feedback"] {{ opacity: 0.14; }}
    .svg-sync-ready[data-world-mode="true"][data-camera-tier="world"] .world-link-label {{ opacity: 0; }}
    .svg-sync-ready[data-world-mode="true"][data-camera-tier="world"] .world-local-branch {{ stroke-opacity: 0.46; }}
    .svg-sync-ready[data-world-mode="true"][data-camera-tier="world"] .sync-module > .module-frame {{ fill-opacity: 0; stroke-opacity: 0; pointer-events: none; }}
    .svg-sync-ready[data-world-mode="true"][data-camera-tier="world"] .sync-module > :is(.module-kicker, .module-question, .module-claim, .module-content, .module-focus-control) {{ opacity: 0; pointer-events: none; }}
    .svg-sync-ready[data-world-mode="true"][data-camera-tier="district"] .world-link {{ opacity: 0.08; }}
    .svg-sync-ready[data-world-mode="true"][data-camera-tier="district"] .world-link-label {{ opacity: 0; }}
    .svg-sync-ready[data-world-mode="true"][data-camera-tier="district"] :is(.district-title-world, .district-title-world-plaque) {{ opacity: 0; }}
    .svg-sync-ready[data-world-mode="true"][data-camera-tier="district"] .world-district[data-camera-active="true"] .district-singleton-preview {{ opacity: 1; }}
    .svg-sync-ready[data-world-mode="true"][data-camera-tier="district"] :is(.district-hub, .district-hub-halo, .district-index, .district-nav-control) {{ opacity: 0; pointer-events: none; }}
    .svg-sync-ready[data-world-mode="true"][data-camera-tier="district"] .world-district[data-camera-active="false"] {{ opacity: 0.025; pointer-events: none; }}
    .svg-sync-ready[data-world-mode="true"][data-camera-tier="district"] .sync-module > .module-frame {{ fill-opacity: 0; stroke-opacity: 0; pointer-events: none; }}
    .svg-sync-ready[data-world-mode="true"][data-camera-tier="district"] .sync-module > :is(.module-kicker, .module-question, .module-claim, .module-content, .module-focus-control) {{ opacity: 0; pointer-events: none; }}
    .svg-sync-ready[data-world-mode="true"][data-camera-tier="module"] :is(.world-link, .world-local-branches, .world-local-nodes, .district-summary, .district-title, .district-hub, .district-hub-halo, .district-field, .district-nav-control) {{ opacity: 0; pointer-events: none; }}
    .svg-sync-ready[data-world-mode="true"][data-camera-tier="module"] .sync-module[data-camera-active="false"] > :is(.module-frame, .module-kicker, .module-question, .module-claim, .module-content, .module-focus-control) {{ opacity: 0; pointer-events: none; }}
    .svg-sync-ready[data-world-mode="true"][data-camera-tier="module"] .sync-module[data-camera-active="true"] > :is(.module-frame, .module-kicker, .module-question, .module-claim, .module-content, .module-focus-control) {{ opacity: 1; }}
    .svg-sync-ready[data-world-mode="true"][data-camera-tier="module"] .sync-module[data-camera-active="true"] {{ filter: drop-shadow(0 18px 32px rgb(15 23 42 / 0.18)); }}
    .svg-sync-ready[data-world-mode="true"]:is([data-camera-tier="world"], [data-camera-tier="district"]) .world-link[data-route-traveling="true"] {{ opacity: 1; }}
    .svg-sync-ready[data-world-mode="true"]:is([data-camera-tier="world"], [data-camera-tier="district"]) .world-link[data-route-traveling="true"] .world-link-label {{ opacity: 1; }}
    .header-plaque {{ fill: #f8fafc; fill-opacity: 0.94; stroke: #d6dce8; stroke-width: 1; }}
    .navigation-hud-panel {{ fill: #111827; fill-opacity: 0.94; stroke: #334155; stroke-width: 1.5; }}
    .navigation-eyebrow {{ font-size: 11px; font-weight: 780; letter-spacing: 0.14em; fill: #93c5fd; }}
    .navigation-current-label {{ font-size: 14.5px; font-weight: 760; fill: #f8fafc; }}
    .navigation-current-tier {{ font-size: 11px; font-weight: 640; letter-spacing: 0.08em; fill: #94a3b8; }}
    .navigation-handoff {{ font-size: 11.5px; font-weight: 650; fill: #cbd5e1; }}
    .navigation-help {{ font-size: 9.5px; font-weight: 650; letter-spacing: 0.04em; fill: #94a3b8; }}
    .navigation-control {{ outline: none; cursor: pointer; }}
    .navigation-control rect {{ fill: #1e293b; stroke: #64748b; stroke-width: 1.5; }}
    .navigation-control text {{ font-size: 13px; font-weight: 780; fill: #f8fafc; pointer-events: none; }}
    .navigation-control:focus rect, .navigation-control[aria-pressed="true"] rect {{ stroke: #60a5fa; stroke-width: 3; }}
    .navigation-control[aria-disabled="true"] {{ opacity: 0.52; cursor: not-allowed; }}
    .minimap-field {{ fill: #0f172a; fill-opacity: 0.92; stroke: #64748b; stroke-width: 1.5; }}
    .minimap-district {{ fill: var(--district-accent); fill-opacity: 0.38; stroke: var(--district-accent); stroke-width: 1; }}
    .minimap-viewport {{ fill: #f8fafc; fill-opacity: 0.08; stroke: #f8fafc; stroke-width: 2.5; vector-effect: non-scaling-stroke; }}
    svg:not(.svg-sync-ready) .navigation-hud {{ display: none; }}
    @media (prefers-reduced-motion: reduce) {{
      *, .sync-module {{ animation: none !important; transition: none !important; scroll-behavior: auto !important; }}
    }}
    """.strip()

    controls: list[str] = []
    button_width = 180.0
    gap = 8.0
    total = min(len(plan["scenarios"]), 4) * (button_width + gap)
    start_x = max(48.0, width - total - 48.0)
    for index, scenario in enumerate(plan["scenarios"][:4]):
        controls.append(
            button_markup(
                f'control-scenario-{scenario["id"]}',
                scenario["label"],
                start_x + index * (button_width + gap),
                28,
                button_width,
                f'data-action="scenario" data-scenario-id="{esc(scenario["id"])}" aria-label="Apply scenario: {esc(scenario["label"])}" aria-pressed="false"',
            )
        )
    if plan.get("timeline"):
        controls.append(
            button_markup("control-play", "Play", max(48.0, width - 280.0), 66, 112, 'data-action="play" aria-label="Play the master timeline" aria-pressed="false" aria-disabled="false"')
        )
    controls.append(button_markup("control-reset", "Reset", max(168.0, width - 160.0), 66, 112, 'data-action="reset" aria-label="Reset composition state"'))

    timeline_markup = ""
    if plan.get("timeline"):
        track_x = 48.0
        track_width = min(760.0, max(280.0, width * 0.44))
        duration = float(plan["timeline"]["durationMs"])
        timeline_markup = (
            f'<g id="timeline-scrubber" class="interactive-control timeline-scrubber" '
            f'data-timeline-rail="true" data-track-x="{fmt(track_x)}" '
            f'data-track-width="{fmt(track_width)}" role="slider" tabindex="0" '
            f'aria-label="Master timeline" aria-valuemin="0" aria-valuemax="{fmt(duration)}" '
            f'aria-valuenow="0" aria-valuetext="Start of loop">'
            f'<rect class="timeline-track" x="{fmt(track_x)}" y="96" '
            f'width="{fmt(track_width)}" height="6" rx="3"/>'
            f'<rect class="timeline-progress" data-timeline-progress="true" x="{fmt(track_x)}" '
            f'y="96" width="0" height="6" rx="3"/>'
            f'<text class="timeline-label" data-timeline-label="true" '
            f'x="{fmt(track_x + track_width + 14)}" y="102">Timeline ready</text></g>'
        )

    modules_by_id = {module["id"]: module for module in plan["modules"]}
    focus_labels = {
        focus["id"]: focus["label"]
        for focus in plan.get("focusGroups", [])
    }
    modules = "\n".join(
        module_markup(modules_by_id[module_id], values, locale, focus_labels)
        for module_id in plan["layout"]["readingOrder"]
    )
    focus_regions, focus_region_labels = focus_region_markup(plan)
    relationships = relationship_markup(plan)
    world = world_markup(plan)
    navigation_hud = navigation_hud_markup(plan)
    navigation_plan = plan.get("navigation")
    description = (
        f"A synchronized SVG composition with {len(plan['modules'])} related visual modules. "
        "The initial scenario is fully visible without scripts; interactive controls appear when the embedded runtime is ready."
    )
    root_x, root_y, root_width, root_height = plan["viewBox"]
    if isinstance(navigation_plan, dict):
        initial_anchor = next(
            anchor
            for anchor in navigation_plan["anchors"]
            if anchor["id"] == navigation_plan["initialAnchorId"]
        )
        initial_camera = " ".join(fmt(float(item)) for item in initial_anchor["viewBox"])
        viewport_x, viewport_y, viewport_width, viewport_height = (
            float(item) for item in navigation_plan["viewport"]
        )
        world_bounds_text = " ".join(
            fmt(float(item)) for item in navigation_plan["worldBounds"]
        )
        composition_body = (
            f'<svg id="composition-world-viewport" class="composition-world-viewport" '
            f'x="{fmt(viewport_x)}" y="{fmt(viewport_y)}" '
            f'width="{fmt(viewport_width)}" height="{fmt(viewport_height)}" '
            f'viewBox="{initial_camera}" preserveAspectRatio="xMidYMid meet" '
            f'overflow="hidden" role="group" aria-label="Navigable world viewport" '
            f'data-world-bounds="{world_bounds_text}" data-nav-anchor-id="world">'
            f'<g id="composition-world">{world}{focus_regions}{relationships}'
            f'{focus_region_labels}<g id="composition-modules">{modules}</g></g></svg>'
        )
        header_plaque = (
            f'<rect class="header-plaque" x="20" y="16" '
            f'width="{fmt(float(root_width) - 40)}" height="104" rx="20"/>'
        )
        root_navigation_attributes = (
            f' data-world-mode="true" data-camera-anchor="{esc(initial_anchor["id"])}" '
            f'data-camera-tier="{esc(initial_anchor["zoomTier"])}" data-camera-revision="0" '
            'data-camera-time-ms="0" data-camera-stop-id="" tabindex="0"'
        )
    else:
        composition_body = (
            f'{focus_regions}{relationships}{focus_region_labels}'
            f'<g id="composition-modules">{modules}</g>'
        )
        header_plaque = ""
        root_navigation_attributes = ' data-world-mode="false"'
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" id="{esc(plan['compositionId'])}" viewBox="{fmt(float(root_x))} {fmt(float(root_y))} {fmt(float(root_width))} {fmt(float(root_height))}" width="100%" height="100%" preserveAspectRatio="xMidYMid meet" role="group" aria-labelledby="composition-title" aria-describedby="composition-desc" data-composition-id="{esc(plan['compositionId'])}" data-plan-version="1" data-sync-ready="false" data-static-state="{esc(plan['initialScenario'])}" data-state-revision="0"{root_navigation_attributes}>
  <title id="composition-title">{esc(plan['title'])}</title>
  <desc id="composition-desc">{esc(description)}</desc>
  <metadata id="sync-composition-plan"><![CDATA[{metadata}]]></metadata>
  <defs><style><![CDATA[{style}]]></style></defs>
  <rect class="canvas" x="{fmt(float(root_x))}" y="{fmt(float(root_y))}" width="{fmt(float(root_width))}" height="{fmt(float(root_height))}"/>
  {composition_body}
  <g id="composition-header" aria-label="Composition header">
    {header_plaque}
    <text class="title" x="48" y="44">{esc(plan['title'])}</text>
    <text class="subtitle" x="48" y="70">Synchronized semantic megacanvas · structural scaffold</text>
    <text class="provenance" x="48" y="91">{esc(plan['provenance'])}</text>
    {''.join(controls)}
    {timeline_markup}
  </g>
  {navigation_hud}
  <script><![CDATA[{RUNTIME_JS}]]></script>
</svg>
'''


def main() -> int:
    args = parse_args()
    try:
        spec_path = args.spec.resolve()
        plan = load_plan(args.spec)
        validate_plan(plan)
        output = args.output.resolve()
        if output == spec_path:
            raise ValueError("scaffold output path must not overwrite the input plan")
        if output.exists() and not args.force:
            raise ValueError(f"output already exists; pass --force to replace it: {output}")
        fragments_dir = args.fragments_dir.resolve() if args.fragments_dir else None
        fragment_outputs: list[Path] = []
        if fragments_dir is not None:
            fragment_outputs = [fragments_dir / f"{module['id']}.svg" for module in plan["modules"]]
            if any(path.resolve() in {spec_path, output} for path in fragment_outputs):
                raise ValueError("fragment paths must not overwrite the input plan or scaffold SVG")
            conflicts = [path for path in fragment_outputs if path.exists()]
            if conflicts and not args.force:
                raise ValueError(
                    f"fragment output already exists; pass --force to replace it: {conflicts[0]}"
                )
        output.parent.mkdir(parents=True, exist_ok=True)
        svg = build_svg(copy.deepcopy(plan))
        output.write_text(svg, encoding="utf-8", newline="\n")
        if fragments_dir is not None:
            fragments_dir.mkdir(parents=True, exist_ok=True)
            source_values, derived_values = initial_values(plan)
            values = {**source_values, **derived_values}
            locale = str(plan.get("locale", "en-US"))
            for module, path in zip(plan["modules"], fragment_outputs):
                path.write_text(fragment_markup(module, values, locale), encoding="utf-8", newline="\n")
        result = {
            "ok": True,
            "output": str(output),
            "compositionId": plan["compositionId"],
            "moduleCount": len(plan["modules"]),
            "sourceConceptCount": len(plan["concepts"]),
            "derivedConceptCount": len(plan.get("derived", [])),
            "containsPlaceholders": True,
            "fragmentsDirectory": str(fragments_dir) if fragments_dir else None,
            "fragmentCount": len(fragment_outputs),
        }
    except (OSError, ValueError) as exc:
        result = {"ok": False, "error": str(exc)}
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"Scaffold failed: {exc}", file=sys.stderr)
        return 1
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"Created synchronized SVG scaffold: {result['output']}")
        print("Replace every data-placeholder module before release, then run the validator.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
