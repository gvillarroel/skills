#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

"""Validate the static contract of a synchronized standalone SVG composition."""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import json
import math
import re
import sys
from pathlib import Path
from typing import Any
import xml.etree.ElementTree as ET

sys.dont_write_bytecode = True

from scaffold_synchronized_svg import ID_RE, ROLE_SELECTOR_RE, initial_values, validate_plan
import navigation_contract as navigation

SVG_NS = "http://www.w3.org/2000/svg"
URL_REF_RE = re.compile(r"url\(\s*['\"]?#([^)'\"\s]+)['\"]?\s*\)")
REMOTE_RE = re.compile(
    r"(?i)https?://|(?<![\w:])//(?:[a-z0-9-]+\.)+[a-z]{2,}(?:[/:?#]|$)"
    r"|@import\s|\bfetch\s*\(|\bXMLHttpRequest\b|\bWebSocket\b"
)
PLACEHOLDER_RE = re.compile(r"(?i)\b(?:todo|placeholder|replace[- ]?me|lorem ipsum|tbd|structural scaffold)\b")
UNRESOLVED_TEXT_RE = re.compile(r"(?i)^(?:--|n/?a|nan|undefined|null|\{\{.*\}\}|\[\[.*\]\])$")
REQUIRED_RUNTIME_METHODS = {
    "getPlan",
    "getState",
    "setState",
    "applyScenario",
    "setFocus",
    "seek",
    "play",
    "pause",
    "reset",
    "snapshot",
    "serializeSnapshot",
}
REQUIRED_NAVIGATION_METHODS = {
    "getCamera",
    "setCamera",
    "navigateTo",
    "seekCamera",
    "fitOverview",
    "nextAnchor",
    "previousAnchor",
    "playCamera",
    "pauseCamera",
    "resetCamera",
}
GEOMETRY_CHANNELS = {"x", "y", "width", "height", "r", "opacity"}
TRANSLATE_RE = re.compile(
    r"^translate\(\s*([-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?)"
    r"(?:[\s,]+)([-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?)\s*\)$"
)
CONCEPT_TOKEN_RE = re.compile(r"var\(\s*--concept-([a-z0-9]+(?:-[a-z0-9]+)*)")
CONCEPT_COLOR_RE = re.compile(
    r"--concept-([a-z0-9]+(?:-[a-z0-9]+)*)\s*:\s*(#[0-9a-fA-F]{6})\s*;"
)
PATH_NUMBER_RE = re.compile(r"[-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?")


def orthogonal_segments(path_data: str) -> list[tuple[str, float, float, float]]:
    """Extract normalized horizontal/vertical segments from generated M/H/V paths."""

    x = y = None
    segments: list[tuple[str, float, float, float]] = []
    for command, payload in re.findall(r"([MHV])([^MHV]*)", path_data):
        numbers = [float(value) for value in PATH_NUMBER_RE.findall(payload)]
        if command == "M" and len(numbers) >= 2:
            x, y = numbers[0], numbers[1]
        elif command == "H" and x is not None and y is not None:
            for next_x in numbers:
                segments.append(("h", y, min(x, next_x), max(x, next_x)))
                x = next_x
        elif command == "V" and x is not None and y is not None:
            for next_y in numbers:
                segments.append(("v", x, min(y, next_y), max(y, next_y)))
                y = next_y
    return segments


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate a synchronized standalone SVG artifact.")
    parser.add_argument("svg", type=Path, help="SVG artifact to validate")
    parser.add_argument("--output", type=Path, help="Optional JSON report path")
    parser.add_argument("--json", action="store_true", help="Print the report as JSON")
    parser.add_argument("--allow-placeholders", action="store_true", help="Allow scaffold placeholder modules")
    parser.add_argument("--require-time-sync", action="store_true", help="Require a declared master timeline")
    parser.add_argument("--require-navigation", action="store_true", help="Require a navigable world contract")
    parser.add_argument("--min-navigation-regions", type=int, default=0)
    parser.add_argument("--min-anchor-depth", type=int, default=0)
    parser.add_argument("--min-world-detail-area-ratio", type=float, default=0.0)
    parser.add_argument("--min-distant-shared-sources", type=int, default=0)
    parser.add_argument("--min-modules", type=int, default=4)
    parser.add_argument("--min-asset-types", type=int, default=3)
    parser.add_argument("--min-renderer-families", type=int, default=0)
    parser.add_argument("--min-shared-sources", type=int, default=1)
    parser.add_argument("--min-modules-per-shared-source", type=int, default=2)
    parser.add_argument("--min-encodings-per-shared-source", type=int, default=2)
    return parser.parse_args()


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def classes(element: ET.Element) -> set[str]:
    return set(element.get("class", "").split())


def direct_child(root: ET.Element, tag: str) -> ET.Element | None:
    return next((child for child in root if local_name(child.tag) == tag), None)


def element_text(element: ET.Element | None) -> str:
    return "" if element is None else "".join(element.itertext()).strip()


def parse_view_box(raw: str | None) -> list[float] | None:
    if not raw:
        return None
    try:
        values = [float(item) for item in re.split(r"[\s,]+", raw.strip()) if item]
    except ValueError:
        return None
    if len(values) != 4 or values[2] <= 0 or values[3] <= 0 or any(not math.isfinite(item) for item in values):
        return None
    return values


def parse_translate(raw: str | None) -> tuple[float, float] | None:
    match = TRANSLATE_RE.fullmatch(raw or "")
    if not match:
        return None
    values = (float(match.group(1)), float(match.group(2)))
    return values if all(math.isfinite(value) for value in values) else None


def parse_finite(raw: str | None) -> float | None:
    try:
        value = float(raw) if raw is not None else math.nan
    except ValueError:
        return None
    return value if math.isfinite(value) else None


def parse_pair(raw: str | None) -> tuple[float, float] | None:
    if not raw:
        return None
    try:
        values = tuple(float(item) for item in re.split(r"[\s,]+", raw.strip()) if item)
    except ValueError:
        return None
    if len(values) != 2 or any(not math.isfinite(value) for value in values):
        return None
    return values


def role_from_selector(selector: str) -> str | None:
    match = ROLE_SELECTOR_RE.fullmatch(selector)
    return (match.group(1) or match.group(2)) if match else None


def descendants_by_role(module: ET.Element, role: str) -> list[ET.Element]:
    return [element for element in module.iter() if element.get("data-role") == role]


def visual_concept_tokens(element: ET.Element) -> set[str]:
    """Return canonical value tokens used by a bound target and descendants."""

    tokens: set[str] = set()
    for descendant in element.iter():
        for value in descendant.attrib.values():
            tokens.update(CONCEPT_TOKEN_RE.findall(str(value)))
    return tokens


def validate_visual_identity(
    plan: dict[str, Any],
    binding_records: list[dict[str, Any]],
    failures: list[str],
    details: dict[str, Any],
    *,
    enforce_rendered_color: bool,
) -> None:
    """Validate optional canonical identity declarations and safe inferred stability."""

    records_by_value: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in binding_records:
        records_by_value[record["value"]].append(record)

    inferred_inconsistencies = 0
    for value_id, records in sorted(records_by_value.items()):
        token_sets = {tuple(record["visualTokens"]) for record in records}
        if enforce_rendered_color and len(token_sets) > 1:
            inferred_inconsistencies += 1
            locations = [
                f"{record['module']}:{record['role']}={record['visualTokens'] or ['no-token']}"
                for record in records
            ]
            failures.append(
                f"canonical value {value_id!r} uses inconsistent visual concept tokens across bindings: "
                + ", ".join(locations)
            )

    identity = plan.get("identity")
    alias_groups = plan.get("identityAliases")
    if identity is None and alias_groups is None:
        details["identity"] = {
            "declared": False,
            "inferredValueCount": len(records_by_value),
            "inferredInconsistencyCount": inferred_inconsistencies,
        }
        return
    if identity is None or alias_groups is None:
        failures.append("identity and identityAliases must be declared together")
        details["identity"] = {"declared": True, "validShape": False}
        return
    if not isinstance(identity, dict) or not identity:
        failures.append("identity must be a non-empty object keyed by canonical identity id")
        details["identity"] = {"declared": True, "validShape": False}
        return
    if not isinstance(alias_groups, list) or not alias_groups:
        failures.append("identityAliases must be a non-empty array")
        details["identity"] = {"declared": True, "validShape": False}
        return

    source_ids = {item["id"] for item in plan.get("concepts", []) if isinstance(item, dict) and "id" in item}
    known_values = source_ids | {
        item["id"] for item in plan.get("derived", []) if isinstance(item, dict) and "id" in item
    }
    normalized_identity: dict[str, dict[str, Any]] = {}
    signatures: dict[tuple[str, tuple[str, ...]], str] = {}
    identities_by_color: dict[str, list[str]] = defaultdict(list)
    for identity_id, record in identity.items():
        if not isinstance(identity_id, str) or not ID_RE.fullmatch(identity_id):
            failures.append(f"identity key {identity_id!r} must be lowercase hyphen-case")
            continue
        if not isinstance(record, dict):
            failures.append(f"identity {identity_id!r} must be an object")
            continue
        color_token = record.get("colorToken")
        non_color = record.get("nonColor")
        if color_token not in known_values:
            failures.append(
                f"identity {identity_id!r} colorToken must name a canonical source or derived value; "
                f"received {color_token!r}"
            )
            continue
        if (
            not isinstance(non_color, list)
            or not non_color
            or any(not isinstance(cue, str) or not ID_RE.fullmatch(cue) for cue in non_color)
            or len(non_color) != len(set(non_color))
        ):
            failures.append(
                f"identity {identity_id!r} nonColor must be a non-empty unique list of lowercase role cues"
            )
            continue
        cues = tuple(sorted(non_color))
        signature = (color_token, cues)
        if signature in signatures:
            failures.append(
                f"identities {signatures[signature]!r} and {identity_id!r} have the same color/non-color signature; "
                "merge only true aliases or give them distinct cues"
            )
        else:
            signatures[signature] = identity_id
        normalized_identity[identity_id] = {"colorToken": color_token, "nonColor": set(cues)}
        identities_by_color[color_token].append(identity_id)

    aliases_by_value: dict[str, str] = {}
    declared_groups: set[str] = set()
    for index, group in enumerate(alias_groups):
        if not isinstance(group, dict):
            failures.append(f"identityAliases[{index}] must be an object")
            continue
        identity_id = group.get("identity")
        values = group.get("values")
        rationale = group.get("rationale")
        if identity_id not in identity:
            failures.append(f"identityAliases[{index}] references unknown identity {identity_id!r}")
            continue
        if identity_id in declared_groups:
            failures.append(f"identity {identity_id!r} has more than one identityAliases group")
        declared_groups.add(identity_id)
        if (
            not isinstance(values, list)
            or not values
            or any(not isinstance(value, str) for value in values)
            or len(values) != len(set(values))
        ):
            failures.append(f"identityAliases[{index}] values must be a non-empty unique string list")
            continue
        if not isinstance(rationale, str) or len(rationale.strip()) < 16:
            failures.append(f"identityAliases[{index}] needs a specific alias rationale")
        identity_words = set(str(identity_id).split("-"))
        for value_id in values:
            if value_id not in known_values:
                failures.append(f"identity {identity_id!r} aliases unknown value {value_id!r}")
                continue
            if value_id in aliases_by_value:
                failures.append(
                    f"value {value_id!r} is falsely aliased to both {aliases_by_value[value_id]!r} and {identity_id!r}"
                )
                continue
            aliases_by_value[value_id] = str(identity_id)
            if len(values) > 1 and not (identity_words & set(value_id.split("-"))):
                failures.append(
                    f"identity {identity_id!r} aliases {value_id!r} without a shared semantic id word; "
                    "split the identity or use clearer canonical IDs"
                )

    missing_groups = sorted(set(identity) - declared_groups)
    if missing_groups:
        failures.append(f"identities without identityAliases groups: {missing_groups}")
    bound_values = set(records_by_value)
    missing_values = sorted(bound_values - set(aliases_by_value))
    if missing_values:
        failures.append(f"bound values missing canonical identity aliases: {missing_values}")

    identity_binding_counts: Counter[str] = Counter()
    for value_id, records in sorted(records_by_value.items()):
        identity_id = aliases_by_value.get(value_id)
        specification = normalized_identity.get(identity_id or "")
        if specification is None:
            continue
        expected_token = specification["colorToken"]
        cues = specification["nonColor"]
        for record in records:
            identity_binding_counts[identity_id] += 1
            tokens = set(record["visualTokens"])
            if enforce_rendered_color and expected_token not in tokens:
                failures.append(
                    f"identity {identity_id!r} expects --concept-{expected_token}, but module "
                    f"{record['module']!r} role {record['role']!r} for {value_id!r} uses "
                    f"{sorted(tokens) or ['no concept token']}"
                )
            if not any(cue in record["role"].split("-") for cue in cues):
                failures.append(
                    f"identity {identity_id!r} requires a stable non-color role cue {sorted(cues)}, but module "
                    f"{record['module']!r} uses role {record['role']!r} for {value_id!r}"
                )

    shared_color_tokens = {
        token: sorted(ids) for token, ids in identities_by_color.items() if len(ids) > 1
    }
    for token, identity_ids in shared_color_tokens.items():
        cue_sets = [normalized_identity[item]["nonColor"] for item in identity_ids if item in normalized_identity]
        for first_index, first in enumerate(cue_sets):
            for second in cue_sets[first_index + 1 :]:
                if first & second:
                    failures.append(
                        f"identities sharing --concept-{token} also share non-color cues {sorted(first & second)}; "
                        "give distinct concepts disjoint cues"
                    )
    details["identity"] = {
        "declared": True,
        "canonicalIdentityCount": len(identity),
        "aliasedValueCount": len(aliases_by_value),
        "coveredBoundValueCount": len(bound_values & set(aliases_by_value)),
        "bindingCounts": dict(sorted(identity_binding_counts.items())),
        "sharedColorTokens": shared_color_tokens,
        "inferredInconsistencyCount": inferred_inconsistencies,
    }


def overlap_ratio(a: list[float], b: list[float]) -> float:
    ax, ay, aw, ah = a
    bx, by, bw, bh = b
    width = max(0.0, min(ax + aw, bx + bw) - max(ax, bx))
    height = max(0.0, min(ay + ah, by + bh) - max(ay, by))
    intersection = width * height
    return intersection / max(1.0, min(aw * ah, bw * bh))


def main() -> int:
    args = parse_args()
    failures: list[str] = []
    warnings: list[str] = []
    details: dict[str, Any] = {}
    svg_path = args.svg.resolve()
    output_path = args.output.resolve() if args.output else None

    if (
        args.min_modules < 1
        or args.min_asset_types < 1
        or args.min_renderer_families < 0
        or args.min_navigation_regions < 0
        or args.min_anchor_depth < 0
        or args.min_world_detail_area_ratio < 0
        or args.min_distant_shared_sources < 0
    ):
        failures.append("minimum counts must be positive")
    if output_path == svg_path:
        failures.append("validation report path must not overwrite the input SVG")
        output_path = None
    if not svg_path.is_file():
        failures.append(f"SVG file does not exist: {svg_path}")
        root = None
    else:
        try:
            root = ET.parse(svg_path).getroot()
        except (ET.ParseError, OSError) as exc:
            failures.append(f"SVG is not well-formed XML: {exc}")
            root = None

    plan: dict[str, Any] = {}
    all_elements: list[ET.Element] = []
    if root is not None:
        all_elements = list(root.iter())
        if local_name(root.tag) != "svg":
            failures.append("root element must be svg")
        if root.tag.startswith("{") and not root.tag.startswith(f"{{{SVG_NS}}}"):
            failures.append("root SVG namespace is not http://www.w3.org/2000/svg")
        title = direct_child(root, "title")
        desc = direct_child(root, "desc")
        if len(element_text(title)) < 3:
            failures.append("root SVG needs a non-empty direct title")
        if len(element_text(desc)) < 20:
            failures.append("root SVG needs a descriptive direct desc")
        if root.get("role") != "group":
            failures.append(
                "root SVG must use role='group'; atomic img/application roles hide synchronized descendants"
            )
        labelled_by = root.get("aria-labelledby", "").split()
        if not labelled_by:
            failures.append("root SVG needs aria-labelledby")
        described_by = root.get("aria-describedby", "").split()
        if not described_by:
            failures.append("root SVG needs aria-describedby")
        view_box = parse_view_box(root.get("viewBox"))
        if view_box is None:
            failures.append("root SVG needs a valid viewBox")
        details["viewBox"] = view_box

        metadata = next((element for element in all_elements if element.get("id") == "sync-composition-plan"), None)
        if metadata is None or local_name(metadata.tag) != "metadata":
            failures.append("missing metadata#sync-composition-plan")
        else:
            try:
                parsed = json.loads(element_text(metadata))
                if not isinstance(parsed, dict):
                    raise ValueError("metadata JSON root is not an object")
                validate_plan(parsed)
                plan = parsed
            except (json.JSONDecodeError, ValueError) as exc:
                plan = {}
                failures.append(f"embedded composition plan is invalid: {exc}")

        ids = [element.get("id") for element in all_elements if element.get("id")]
        duplicate_ids = sorted(item for item, count in Counter(ids).items() if count > 1)
        if duplicate_ids:
            failures.append(f"duplicate SVG ids: {duplicate_ids[:12]}")
        id_set = set(ids)
        for label_id in labelled_by:
            if label_id not in id_set:
                failures.append(f"aria-labelledby references missing id: {label_id}")
        for description_id in described_by:
            if description_id not in id_set:
                failures.append(f"aria-describedby references missing id: {description_id}")

        remote_hits: list[str] = []
        broken_refs: set[str] = set()
        for element in all_elements:
            for attr, raw_value in element.attrib.items():
                value = str(raw_value)
                if attr.rsplit("}", 1)[-1] in {"href", "src"}:
                    if value.startswith("#") and value[1:] not in id_set:
                        broken_refs.add(value[1:])
                    elif value and not value.startswith(("#", "data:")):
                        remote_hits.append(f"{local_name(element.tag)}@{attr}={value[:80]}")
                for ref_id in URL_REF_RE.findall(value):
                    if ref_id not in id_set:
                        broken_refs.add(ref_id)
                if REMOTE_RE.search(value):
                    remote_hits.append(f"{local_name(element.tag)}@{attr}={value[:80]}")
            if local_name(element.tag) in {"style", "script"}:
                content = element_text(element)
                if REMOTE_RE.search(content):
                    remote_hits.append(f"{local_name(element.tag)} text")
                for ref_id in URL_REF_RE.findall(content):
                    if ref_id not in id_set:
                        broken_refs.add(ref_id)
        if remote_hits:
            failures.append(f"external or network dependencies detected: {sorted(set(remote_hits))[:8]}")
        if broken_refs:
            failures.append(f"unresolved local SVG references: {sorted(broken_refs)[:12]}")

        style_text = "\n".join(element_text(element) for element in all_elements if local_name(element.tag) == "style")
        script_text = "\n".join(element_text(element) for element in all_elements if local_name(element.tag) == "script")
        if "font-family" not in style_text:
            failures.append("SVG style must declare an explicit font-family")
        if "prefers-reduced-motion" not in style_text:
            failures.append("SVG style must define a prefers-reduced-motion fallback")
        if ".svg-sync-ready" not in style_text or ".interactive-control" not in style_text:
            failures.append("interactive controls must be hidden until svg-sync-ready")
        if "window.svgSync" not in script_text:
            failures.append("embedded runtime must publish window.svgSync")
        missing_methods = sorted(method for method in REQUIRED_RUNTIME_METHODS if not re.search(rf"\b{re.escape(method)}\b", script_text))
        if missing_methods:
            failures.append(f"window.svgSync runtime is missing methods: {missing_methods}")
        if plan.get("navigation"):
            missing_navigation_methods = sorted(
                method
                for method in REQUIRED_NAVIGATION_METHODS
                if not re.search(rf"\b{re.escape(method)}\b", script_text)
            )
            if missing_navigation_methods:
                failures.append(
                    "window.svgSync navigation runtime is missing methods: "
                    f"{missing_navigation_methods}"
                )
            for token in ("svg-camera-change", "data-camera-revision", "data-camera-tier"):
                if token not in script_text:
                    failures.append(f"navigation runtime is missing camera marker {token!r}")
        for token in ("svg-sync-change", "data-sync-revision", "data-state-revision"):
            if token not in script_text:
                failures.append(f"runtime is missing atomic-update marker {token!r}")
        if any(local_name(element.tag) in {"animate", "animateMotion", "animateTransform", "set"} for element in all_elements):
            warnings.append("declarative SVG animation exists; verify it is driven by the master clock and cannot drift")

        placeholder_elements = [
            element for element in all_elements
            if element.get("data-placeholder") == "true"
            or bool(classes(element) & {"module-placeholder", "placeholder-mark", "placeholder-value"})
            or (local_name(element.tag) in {"text", "title", "desc"} and PLACEHOLDER_RE.search(element_text(element)))
        ]
        if placeholder_elements and not args.allow_placeholders:
            failures.append(f"artifact still contains {len(placeholder_elements)} placeholder markers or labels")
        details["placeholderCount"] = len(placeholder_elements)
        unresolved_text = sorted(
            {
                element_text(element)
                for element in all_elements
                if local_name(element.tag) == "text" and UNRESOLVED_TEXT_RE.fullmatch(element_text(element))
            }
        )
        if unresolved_text:
            failures.append(f"visible SVG text contains unresolved values: {unresolved_text}")

    binding_records: list[dict[str, Any]] = []
    influence: dict[str, Any] = {}
    if root is not None and plan:
        composition_id = plan["compositionId"]
        if root.get("data-composition-id") != composition_id:
            failures.append("root data-composition-id does not match the embedded plan")
        if root.get("id") != composition_id or not ID_RE.fullmatch(root.get("id", "")):
            failures.append("root id must be the stable compositionId")
        if root.get("data-plan-version") != str(plan["version"]):
            failures.append("root data-plan-version does not match the embedded plan")
        if not root.get("data-static-state"):
            failures.append("root needs data-static-state for the script-free fallback")
        provenance_nodes = [
            element for element in all_elements
            if local_name(element.tag) == "text" and "provenance" in classes(element)
        ]
        if len(provenance_nodes) != 1 or element_text(provenance_nodes[0]) != plan.get("provenance"):
            failures.append("root header must visibly render the exact plan.provenance note")
        root_view_box = parse_view_box(root.get("viewBox"))
        if root_view_box and any(abs(a - float(b)) > 1e-6 for a, b in zip(root_view_box, plan["viewBox"])):
            failures.append("root viewBox does not match plan.viewBox")

        modules = plan["modules"]
        focus_labels = {
            focus["id"]: focus["label"]
            for focus in plan.get("focusGroups", [])
        }
        if len(modules) < args.min_modules:
            failures.append(f"module count {len(modules)} is below required {args.min_modules}")
        asset_types = sorted({module["assetType"] for module in modules})
        if len(asset_types) < args.min_asset_types:
            failures.append(f"asset-type count {len(asset_types)} is below required {args.min_asset_types}")
        renderer_families = sorted(
            {
                element.get("data-renderer-family", "")
                for element in all_elements
                if element.get("data-renderer-family")
            }
        )
        if len(renderer_families) < args.min_renderer_families:
            failures.append(
                f"renderer-family count {len(renderer_families)} is below required "
                f"{args.min_renderer_families}"
            )
        claims = [module["claim"].strip().casefold() for module in modules]
        questions = [module["question"].strip().casefold() for module in modules]
        repeated_claims = sorted(item for item, count in Counter(claims).items() if count > 1)
        if repeated_claims:
            failures.append("module claims must be distinct")
        repeated_questions = sorted(item for item, count in Counter(questions).items() if count > 1)
        if repeated_questions:
            failures.append("module viewer questions must be distinct")
        for module in modules:
            asset_tokens = set(module["assetType"].lower().replace("_", "-").split("-"))
            if asset_tokens & {"network", "hierarchy", "tree", "graph", "node", "org"}:
                radius_values = [
                    binding["value"]
                    for binding in module["bindings"]
                    if binding.get("channel") == "r"
                ]
                if radius_values:
                    failures.append(
                        f"network module {module['id']!r} uses radius encoding for {radius_values}; "
                        "use equal-area topology nodes with exact synchronized text so node area does not "
                        "imply an unsupported quantitative comparison"
                    )

        dom_modules: dict[str, ET.Element] = {}
        for element in all_elements:
            module_id = element.get("data-module-id")
            if module_id:
                if module_id in dom_modules:
                    failures.append(f"duplicate DOM module group: {module_id}")
                dom_modules[module_id] = element
        planned_module_ids = {module["id"] for module in modules}
        if set(dom_modules) != planned_module_ids:
            missing = sorted(planned_module_ids - set(dom_modules))
            extra = sorted(set(dom_modules) - planned_module_ids)
            failures.append(f"DOM module set differs from plan; missing={missing}, extra={extra}")
        planned_reading_order = plan["layout"]["readingOrder"]
        if list(dom_modules) != planned_reading_order:
            failures.append(
                "DOM module order must exactly match layout.readingOrder so visual, keyboard, "
                "and assistive-technology traversal agree"
            )

        declared_relationships = plan.get("relationships", [])
        dom_relationships: dict[str, ET.Element] = {}
        for element in all_elements:
            relationship_id = element.get("data-relationship-id")
            if not relationship_id:
                continue
            if relationship_id in dom_relationships:
                failures.append(f"duplicate DOM relationship group: {relationship_id}")
            dom_relationships[relationship_id] = element
        planned_relationship_ids = {item["id"] for item in declared_relationships}
        if set(dom_relationships) != planned_relationship_ids:
            missing = sorted(planned_relationship_ids - set(dom_relationships))
            extra = sorted(set(dom_relationships) - planned_relationship_ids)
            failures.append(
                f"DOM relationship set differs from plan; missing={missing}, extra={extra}"
            )
        module_regions = {module["id"]: module["region"] for module in modules}
        incident_ports: dict[str, list[float]] = defaultdict(list)
        route_lanes: set[int] = set()
        routed_segments: list[tuple[str, tuple[str, float, float, float]]] = []
        for relationship_index, relationship in enumerate(declared_relationships):
            group = dom_relationships.get(relationship["id"])
            if group is None:
                continue
            expected_attributes = {
                "data-source-module": relationship["source"],
                "data-target-module": relationship["target"],
                "data-kind": relationship["kind"],
                "aria-label": relationship["label"],
            }
            for attribute, expected in expected_attributes.items():
                if group.get(attribute) != expected:
                    failures.append(
                        f"relationship {relationship['id']!r} {attribute} differs from the plan"
                    )
            source_port = group.get("data-source-port")
            target_port = group.get("data-target-port")
            route_lane = group.get("data-route-lane")
            for module_id, port, endpoint in (
                (relationship["source"], source_port, "source"),
                (relationship["target"], target_port, "target"),
            ):
                try:
                    port_value = float(str(port))
                except (TypeError, ValueError):
                    failures.append(
                        f"relationship {relationship['id']!r} {endpoint} port must be finite"
                    )
                    continue
                if not math.isfinite(port_value):
                    failures.append(
                        f"relationship {relationship['id']!r} {endpoint} port must be finite"
                    )
                    continue
                region = module_regions[module_id]
                maximum_offset = max(0.0, min(float(region[2]), float(region[3])) / 2.0 - 12.0)
                if abs(port_value) > maximum_offset + 1e-6:
                    failures.append(
                        f"relationship {relationship['id']!r} {endpoint} port {port_value} lies outside module {module_id!r}"
                    )
                if any(abs(port_value - existing) < 1e-6 for existing in incident_ports[module_id]):
                    failures.append(
                        f"relationship {relationship['id']!r} reuses incident port {port!r} on module {module_id!r}"
                    )
                elif any(abs(port_value - existing) < 15.0 - 1e-6 for existing in incident_ports[module_id]):
                    failures.append(
                        f"relationship {relationship['id']!r} incident port is too close to another marker on module {module_id!r}"
                    )
                incident_ports[module_id].append(port_value)
            try:
                route_lane_value = int(str(route_lane))
                route_lane_is_canonical = str(route_lane_value) == str(route_lane)
            except (TypeError, ValueError):
                route_lane_value = -1
                route_lane_is_canonical = False
            if (
                not route_lane_is_canonical
                or route_lane_value < 0
                or route_lane_value in route_lanes
                or route_lane_value != relationship_index
            ):
                failures.append(
                    f"relationship {relationship['id']!r} needs canonical deterministic route lane {relationship_index}"
                )
            else:
                route_lanes.add(route_lane_value)
            title = direct_child(group, "title")
            if element_text(title) != relationship["label"]:
                failures.append(
                    f"relationship {relationship['id']!r} needs a matching accessible title"
                )
            paths = [
                element
                for element in group.iter()
                if "relationship-path" in classes(element)
            ]
            if len(paths) != 1:
                failures.append(
                    f"relationship {relationship['id']!r} needs exactly one relationship path"
                )
            else:
                path = paths[0]
                if local_name(path.tag) != "path" or not path.get("d", "").strip():
                    failures.append(
                        f"relationship {relationship['id']!r} path must contain geometry"
                    )
                else:
                    routed_segments.extend(
                        (relationship["id"], segment)
                        for segment in orthogonal_segments(path.get("d", ""))
                    )
                marker = path.get("marker-end", "")
                if not marker.startswith("url(#") or not marker.endswith(")"):
                    failures.append(
                        f"relationship {relationship['id']!r} path needs a local arrow marker"
                    )
                elif marker[5:-1] in id_set:
                    marker_element = next(
                        (element for element in all_elements if element.get("id") == marker[5:-1]),
                        None,
                    )
                    if marker_element is None or marker_element.get("markerUnits") != "userSpaceOnUse":
                        failures.append(
                            f"relationship {relationship['id']!r} arrow marker must use stable userSpaceOnUse sizing"
                        )
            pulses = [
                element
                for element in group.iter()
                if element.get("data-relationship-pulse") == "true"
            ]
            if len(pulses) != 1 or local_name(pulses[0].tag) != "circle":
                failures.append(
                    f"relationship {relationship['id']!r} needs exactly one pulse circle"
                )
        key_items = {
            element.get("data-relationship-key-id"): element
            for element in all_elements
            if element.get("data-relationship-key-id")
        }
        if set(key_items) != planned_relationship_ids:
            failures.append(
                "visible relationship key must contain exactly one item per declared relationship"
            )
        for relationship in declared_relationships:
            key_item = key_items.get(relationship["id"])
            if key_item is None:
                continue
            if key_item.get("data-relationship-key-kind") != relationship["kind"]:
                failures.append(
                    f"relationship key {relationship['id']!r} kind differs from the plan"
                )
            if key_item.get("data-relationship-key-label") != relationship["label"]:
                failures.append(
                    f"relationship key {relationship['id']!r} label differs from the plan"
                )
            key_text = next(
                (
                    element_text(element)
                    for element in key_item.iter()
                    if "relationship-key-label" in classes(element)
                ),
                "",
            )
            expected_prefix = f"{relationship['kind']} · "
            visible_label = key_text[len(expected_prefix) :].removesuffix("…") if key_text.startswith(expected_prefix) else ""
            if not visible_label or not relationship["label"].startswith(visible_label):
                failures.append(
                    f"relationship key {relationship['id']!r} needs a truthful visible kind and label"
                )
        overlap_findings: list[str] = []
        for first_index, (first_id, first) in enumerate(routed_segments):
            for second_id, second in routed_segments[first_index + 1 :]:
                if first_id == second_id or first[0] != second[0] or abs(first[1] - second[1]) > 1e-6:
                    continue
                overlap = min(first[3], second[3]) - max(first[2], second[2])
                if overlap > 1.0:
                    overlap_findings.append(
                        f"{first_id!r}/{second_id!r} share {overlap:.2f}px of one route segment"
                    )
        if overlap_findings:
            failures.append(
                "relationship routes overlap without an explicit bundle: "
                + "; ".join(overlap_findings[:8])
            )

        try:
            source_values, derived_values = initial_values(plan)
            initial = {**source_values, **derived_values}
        except ValueError as exc:
            failures.append(f"initial semantic state cannot be computed: {exc}")
            initial = {}

        declared_targets: set[int] = set()
        accessible_binding_count = 0
        value_definitions = {
            item["id"]: item for item in [*plan["concepts"], *plan.get("derived", [])]
        }
        for module in modules:
            group = dom_modules.get(module["id"])
            if group is None:
                continue
            region_x, region_y, region_width, region_height = (
                float(item) for item in module["region"]
            )
            if "sync-module" not in classes(group):
                failures.append(f"module {module['id']!r} must use class sync-module")
            if group.get("role") != "group":
                failures.append(
                    f"module {module['id']!r} must use role='group' so bound descendants remain exposed"
                )
            if group.get("tabindex") is not None or group.get("data-module-focus-id") is not None:
                failures.append(
                    f"module {module['id']!r} must not act as its own focus control; use a separate button"
                )
            if group.get("data-asset-type") != module["assetType"]:
                failures.append(f"module {module['id']!r} data-asset-type differs from the plan")
            if not group.get("aria-labelledby") and direct_child(group, "title") is None:
                failures.append(f"module {module['id']!r} needs an accessible title")
            if not group.get("aria-describedby"):
                failures.append(f"module {module['id']!r} needs aria-describedby for its viewer question")
            for attribute in ("aria-labelledby", "aria-describedby"):
                for reference_id in group.get(attribute, "").split():
                    if reference_id not in id_set:
                        failures.append(
                            f"module {module['id']!r} {attribute} references missing id: {reference_id}"
                        )
            focus_controls = [
                element for element in group.iter()
                if element is not group and element.get("data-module-focus-id") is not None
            ]
            declared_focus = module.get("focusGroups", [])
            if declared_focus:
                actual_focus = [control.get("data-module-focus-id") for control in focus_controls]
                if actual_focus != declared_focus:
                    failures.append(
                        f"module {module['id']!r} focus controls target {actual_focus!r}; "
                        f"expected every membership {declared_focus!r}"
                    )
                visible_focus_labels: list[str] = []
                for control in focus_controls:
                    control_focus = control.get("data-module-focus-id")
                    if control.get("role") != "button" or control.get("tabindex") != "0":
                        failures.append(
                            f"module {module['id']!r} focus control must be a keyboard-reachable role='button'"
                        )
                    if control.get("aria-pressed") != "false":
                        failures.append(
                            f"module {module['id']!r} focus control must declare initial aria-pressed='false'"
                        )
                    if not control.get("aria-label"):
                        failures.append(
                            f"module {module['id']!r} focus control needs an accessible name"
                        )
                    elif focus_labels.get(control_focus, "").casefold() not in control.get(
                        "aria-label", ""
                    ).casefold():
                        failures.append(
                            f"module {module['id']!r} focus control name must include the declared focus label"
                        )
                    visible_label = next(
                        (
                            element_text(element)
                            for element in control.iter()
                            if local_name(element.tag) == "text"
                        ),
                        "",
                    )
                    if not visible_label:
                        failures.append(
                            f"module {module['id']!r} focus control needs a visible label"
                        )
                    visible_focus_labels.append(visible_label.casefold())
                    control_position = parse_translate(control.get("transform"))
                    control_rect = next(
                        (
                            element
                            for element in control
                            if local_name(element.tag) == "rect"
                        ),
                        None,
                    )
                    control_width = parse_finite(
                        control_rect.get("width") if control_rect is not None else None
                    )
                    control_x = control_position[0] if control_position is not None else math.nan
                    if (
                        control_width is None
                        or not math.isfinite(control_x)
                        or control_width <= 0
                        or control_x < -1e-6
                        or control_x + control_width > region_width + 1e-6
                    ):
                        failures.append(
                            f"module {module['id']!r} focus control lies outside its module bounds"
                        )
                if len(visible_focus_labels) != len(set(visible_focus_labels)):
                    failures.append(
                        f"module {module['id']!r} focus controls need distinct visible labels"
                    )
            elif focus_controls:
                failures.append(f"module {module['id']!r} has an undeclared focus control")
            translation = parse_translate(group.get("transform"))
            if translation is None or any(
                abs(actual - expected) > 1e-6
                for actual, expected in zip(translation or (math.nan, math.nan), (region_x, region_y))
            ):
                failures.append(f"module {module['id']!r} transform must match its planned region origin")
            frames = [
                child for child in group
                if isinstance(child.tag, str)
                and local_name(child.tag) == "rect"
                and "module-frame" in classes(child)
            ]
            if len(frames) != 1:
                failures.append(f"module {module['id']!r} needs exactly one direct module-frame rect")
            else:
                frame_width = parse_finite(frames[0].get("width"))
                frame_height = parse_finite(frames[0].get("height"))
                if frame_width is None or abs(frame_width - region_width) > 1e-6:
                    failures.append(f"module {module['id']!r} frame width differs from its planned region")
                if frame_height is None or abs(frame_height - region_height) > 1e-6:
                    failures.append(f"module {module['id']!r} frame height differs from its planned region")

            body_top = parse_finite(group.get("data-content-top"))
            bodies = [
                child for child in group
                if isinstance(child.tag, str)
                and child.get("data-module-content-for") == module["id"]
            ]
            if body_top is None or body_top < 0 or body_top >= region_height:
                failures.append(f"module {module['id']!r} has invalid data-content-top")
            if len(bodies) != 1:
                failures.append(f"module {module['id']!r} needs exactly one direct module-content body")
            elif body_top is not None:
                body = bodies[0]
                if "module-content" not in classes(body):
                    failures.append(f"module {module['id']!r} body must use class module-content")
                body_translation = parse_translate(body.get("transform"))
                if body_translation is None or any(
                    abs(actual - expected) > 1e-6
                    for actual, expected in zip(body_translation or (math.nan, math.nan), (0.0, body_top))
                ):
                    failures.append(f"module {module['id']!r} body transform must start at data-content-top")
                origin = parse_pair(body.get("data-content-origin"))
                if origin is None or abs(origin[0]) > 1e-6 or abs(origin[1] - body_top) > 1e-6:
                    failures.append(f"module {module['id']!r} body data-content-origin is invalid")
                body_width = parse_finite(body.get("data-content-width"))
                body_height = parse_finite(body.get("data-content-height"))
                if body_width is None or abs(body_width - region_width) > 1e-6:
                    failures.append(f"module {module['id']!r} body width differs from its planned region")
                if body_height is None or abs(body_height - (region_height - body_top)) > 1e-6:
                    failures.append(f"module {module['id']!r} body height differs from its planned region")
            for binding in module["bindings"]:
                role = role_from_selector(binding["selector"])
                if role is None:
                    failures.append(f"module {module['id']!r} uses an unsupported selector")
                    continue
                targets = descendants_by_role(group, role)
                if not targets:
                    failures.append(f"module {module['id']!r} selector {binding['selector']!r} matches no DOM target")
                    continue
                for target in targets:
                    declared_targets.add(id(target))
                    if target.get("data-bind") != binding["value"]:
                        failures.append(
                            f"module {module['id']!r} role {role!r} data-bind must equal {binding['value']!r}"
                        )
                    if target.get("data-channel") != binding["channel"]:
                        failures.append(
                            f"module {module['id']!r} role {role!r} data-channel must equal {binding['channel']!r}"
                        )
                    if target.get("data-sync-revision") is None:
                        failures.append(f"module {module['id']!r} role {role!r} lacks data-sync-revision")
                    raw_current = target.get("data-current-value")
                    if raw_current is None:
                        failures.append(f"module {module['id']!r} role {role!r} lacks data-current-value")
                    elif binding["value"] in initial:
                        try:
                            if abs(float(raw_current) - float(initial[binding["value"]])) > 1e-6:
                                failures.append(
                                    f"module {module['id']!r} role {role!r} static value disagrees with the initial scenario"
                                )
                        except ValueError:
                            failures.append(f"module {module['id']!r} role {role!r} data-current-value is not numeric")
                    if binding["channel"] == "text" and not element_text(target):
                        failures.append(f"module {module['id']!r} role {role!r} has blank static text")
                    if binding["channel"] in GEOMETRY_CHANNELS and target.get(binding["channel"]) is None:
                        failures.append(
                            f"module {module['id']!r} role {role!r} lacks static {binding['channel']} geometry"
                        )
                    if not args.allow_placeholders:
                        if target.get("role") not in {"img", "meter"}:
                            failures.append(
                                f"module {module['id']!r} role {role!r} must expose role='img' or role='meter'"
                            )
                        accessible_label = target.get("data-accessible-label") or ""
                        accessible_value = target.get("data-accessible-value") or ""
                        aria_label = target.get("aria-label") or ""
                        aria_value_text = target.get("aria-valuetext") or ""
                        expected_unit = str(value_definitions.get(binding["value"], {}).get("unit", ""))
                        if target.get("data-value-unit", "") != expected_unit:
                            failures.append(
                                f"module {module['id']!r} role {role!r} accessible unit differs from {expected_unit!r}"
                            )
                        if not accessible_label or not accessible_value or not aria_label:
                            failures.append(
                                f"module {module['id']!r} role {role!r} lacks a complete human-readable accessible value"
                            )
                        elif "-" in binding["value"] and binding["value"] in aria_label:
                            failures.append(
                                f"module {module['id']!r} role {role!r} exposes internal value ID in aria-label"
                            )
                        elif (
                            accessible_label not in aria_label
                            or accessible_value not in aria_label
                        ):
                            failures.append(
                                f"module {module['id']!r} role {role!r} accessible label/value are inconsistent"
                            )
                        else:
                            accessible_binding_count += 1
                        target_accessible_role = target.get("role")
                        if target_accessible_role == "img" and aria_value_text:
                            failures.append(
                                f"module {module['id']!r} role {role!r} puts aria-valuetext on role='img'; include the value in aria-label instead"
                            )
                        if target_accessible_role == "meter":
                            if aria_value_text != accessible_value:
                                failures.append(
                                    f"module {module['id']!r} role {role!r} meter aria-valuetext is inconsistent"
                                )
                            for attribute in ("aria-valuemin", "aria-valuemax", "aria-valuenow"):
                                if parse_finite(target.get(attribute)) is None:
                                    failures.append(
                                        f"module {module['id']!r} role {role!r} meter lacks numeric {attribute}"
                                    )
                        if direct_child(target, "title") is not None:
                            failures.append(
                                f"module {module['id']!r} role {role!r} has a redundant child title in addition to aria-label"
                            )
                    binding_records.append(
                        {
                            "module": module["id"],
                            "district": module.get("districtId"),
                            "assetType": module["assetType"],
                            "value": binding["value"],
                            "channel": binding["channel"],
                            "role": role,
                            "visualTokens": sorted(visual_concept_tokens(target)),
                        }
                    )
        orphan_targets = [
            element for element in all_elements
            if element.get("data-bind") is not None and id(element) not in declared_targets
        ]
        if orphan_targets:
            failures.append(f"found {len(orphan_targets)} DOM bindings not declared in the plan")

        derived_deps = {item["id"]: set(item["dependsOn"]) for item in plan.get("derived", [])}
        closure_cache: dict[str, set[str]] = {}

        def ancestors(value_id: str) -> set[str]:
            if value_id in closure_cache:
                return closure_cache[value_id]
            result = {value_id}
            for dependency in derived_deps.get(value_id, set()):
                result.update(ancestors(dependency))
            closure_cache[value_id] = result
            return result

        for source in plan["concepts"]:
            source_id = source["id"]
            influenced_records = [record for record in binding_records if source_id in ancestors(record["value"])]
            module_ids = sorted({record["module"] for record in influenced_records})
            district_ids = sorted(
                {
                    str(record["district"])
                    for record in influenced_records
                    if record.get("district")
                }
            )
            encodings = sorted({f"{record['assetType']}:{record['channel']}" for record in influenced_records})
            influence[source_id] = {
                "modules": module_ids,
                "moduleCount": len(module_ids),
                "districts": district_ids,
                "districtCount": len(district_ids),
                "values": sorted({record["value"] for record in influenced_records}),
                "encodings": encodings,
                "encodingCount": len(encodings),
            }
        shared_sources = [
            source_id for source_id, item in influence.items()
            if item["moduleCount"] >= args.min_modules_per_shared_source
            and item["encodingCount"] >= args.min_encodings_per_shared_source
        ]
        if len(shared_sources) < args.min_shared_sources:
            failures.append(
                f"only {len(shared_sources)} source concepts influence enough distinct modules/encodings; "
                f"required {args.min_shared_sources}"
            )
        details["sharedSources"] = sorted(shared_sources)
        distant_shared_sources = sorted(
            source_id
            for source_id, item in influence.items()
            if item.get("districtCount", 0) >= 2 and item["encodingCount"] >= 2
        )
        if len(distant_shared_sources) < args.min_distant_shared_sources:
            failures.append(
                f"only {len(distant_shared_sources)} source concepts propagate across at least two "
                f"districts with distinct encodings; required {args.min_distant_shared_sources}"
            )
        details["distantSharedSources"] = distant_shared_sources

        view_box = [
            float(item)
            for item in (
                plan.get("navigation", {}).get("worldBounds")
                if isinstance(plan.get("navigation"), dict)
                else plan["viewBox"]
            )
        ]
        vx, vy, vw, vh = view_box
        for module in modules:
            x, y, width, height = (float(item) for item in module["region"])
            if x < vx or y < vy or x + width > vx + vw or y + height > vy + vh:
                failures.append(f"module {module['id']!r} region escapes the viewBox")
        for index, first in enumerate(modules):
            for second in modules[index + 1 :]:
                ratio = overlap_ratio([float(item) for item in first["region"]], [float(item) for item in second["region"]])
                if ratio > 0.12:
                    warnings.append(
                        f"module regions {first['id']!r} and {second['id']!r} overlap by {ratio:.1%}; inspect intentional layering"
                    )

        navigation_plan = plan.get("navigation")
        if args.require_navigation and not isinstance(navigation_plan, dict):
            failures.append("navigation is required but the plan has no navigable world")
        if isinstance(navigation_plan, dict):
            anchors = navigation_plan["anchors"]
            anchor_by_id = {anchor["id"]: anchor for anchor in anchors}
            initial_anchor = anchor_by_id[navigation_plan["initialAnchorId"]]
            viewport_elements = [
                element
                for element in all_elements
                if element.get("id") == "composition-world-viewport"
            ]
            if len(viewport_elements) != 1:
                failures.append("navigable world needs exactly one composition-world-viewport")
            else:
                viewport_element = viewport_elements[0]
                if viewport_element.get("role") != "group" or not viewport_element.get("aria-label"):
                    failures.append("composition-world-viewport needs a named non-atomic group role")
                actual_camera = parse_view_box(viewport_element.get("viewBox"))
                expected_camera = [float(item) for item in initial_anchor["viewBox"]]
                if actual_camera is None or any(
                    abs(actual - expected) > 1e-6
                    for actual, expected in zip(actual_camera or [], expected_camera)
                ):
                    failures.append("world viewport initial camera differs from navigation.initialAnchorId")
            if root.get("data-world-mode") != "true":
                failures.append("navigable root needs data-world-mode='true'")
            if root.get("data-camera-anchor") != navigation_plan["initialAnchorId"]:
                failures.append("root initial data-camera-anchor differs from the plan")
            dom_anchor_ids = [
                element.get("data-nav-anchor-id")
                for element in all_elements
                if element.get("data-nav-anchor-id") is not None
            ]
            expected_anchor_ids = {anchor["id"] for anchor in anchors}
            if set(dom_anchor_ids) != expected_anchor_ids or len(dom_anchor_ids) != len(expected_anchor_ids):
                failures.append(
                    "DOM navigation anchors must resolve every plan anchor exactly once; "
                    f"expected={sorted(expected_anchor_ids)}, actual={sorted(dom_anchor_ids)}"
                )
            world = plan.get("world", {})
            districts = world.get("districts", []) if isinstance(world, dict) else []
            district_dom_ids = {
                element.get("data-district-id")
                for element in all_elements
                if "world-district" in classes(element)
            }
            expected_district_ids = {district["id"] for district in districts}
            if district_dom_ids != expected_district_ids:
                failures.append("DOM world districts differ from the plan")
            world_link_dom_ids = {
                element.get("data-world-link-id")
                for element in all_elements
                if element.get("data-world-link-id") is not None
            }
            expected_world_link_ids = {link["id"] for link in world.get("links", [])}
            if world_link_dom_ids != expected_world_link_ids:
                failures.append("DOM world district links differ from the plan")
            world_node_ids = [
                element.get("data-world-module-id")
                for element in all_elements
                if element.get("data-world-module-id") is not None
            ]
            expected_module_ids = {module["id"] for module in modules}
            if set(world_node_ids) != expected_module_ids or len(world_node_ids) != len(expected_module_ids):
                failures.append("world local-index nodes must represent every module exactly once")
            district_control_ids = {
                element.get("id")
                for element in all_elements
                if "district-nav-control" in classes(element)
            }
            expected_district_control_ids = {f"district-nav-{item['id']}" for item in districts}
            if district_control_ids != expected_district_control_ids:
                failures.append("world district hub controls need stable IDs for every district")
            module_control_targets = {
                element.get("data-nav-target")
                for element in all_elements
                if "world-module-nav-control" in classes(element)
            }
            if module_control_targets != {f"module-{module_id}" for module_id in expected_module_ids}:
                failures.append("world local-index controls must navigate to every module anchor")
            trunk_targets = [
                link["target"] for link in world.get("links", []) if link.get("treeRole") == "trunk"
            ]
            expected_trunk_targets = expected_district_ids - {world.get("rootDistrictId")}
            if len(trunk_targets) != len(set(trunk_targets)) or set(trunk_targets) != expected_trunk_targets:
                failures.append("world trunk links must reach every non-root district exactly once")
            world_link_groups = {
                element.get("data-world-link-id"): element
                for element in all_elements
                if element.get("data-world-link-id") is not None
            }
            for link in world.get("links", []):
                if link.get("treeRole") != "trunk":
                    continue
                group = world_link_groups.get(link["id"])
                chevron_count = (
                    len(
                        [
                            descendant
                            for descendant in group.iter()
                            if "world-link-chevron" in classes(descendant)
                        ]
                    )
                    if group is not None
                    else 0
                )
                if chevron_count != 2:
                    failures.append(
                        f"world trunk {link['id']!r} needs exactly two persistent direction chevrons"
                    )
            camera_actions = {
                element.get("data-camera-action")
                for element in all_elements
                if element.get("data-camera-action") is not None
            }
            expected_camera_actions = {"previous", "up", "next", "tour", "home"}
            if camera_actions != expected_camera_actions:
                failures.append(
                    "camera HUD controls must expose previous, up, next, tour, and home actions"
                )
            module_plan_by_id = {module["id"]: module for module in modules}
            expected_singleton_previews = sum(
                1
                for district in districts
                if len(district.get("moduleIds", [])) == 1
                and isinstance(
                    module_plan_by_id.get(district["moduleIds"][0], {}).get("diagram"),
                    dict,
                )
            )
            actual_singleton_previews = len(
                [
                    element
                    for element in all_elements
                    if "district-singleton-preview" in classes(element)
                ]
            )
            if actual_singleton_previews != expected_singleton_previews:
                failures.append(
                    "single-module structural districts need one district-level concept preview"
                )
            peer_anchor_sizes: dict[int, set[tuple[float, float]]] = {}
            district_by_id = {item["id"]: item for item in districts}
            for anchor in anchors:
                if anchor.get("kind") != "district" or anchor.get("targetId") == world.get("rootDistrictId"):
                    continue
                module_count = len(district_by_id[anchor["targetId"]]["moduleIds"])
                peer_anchor_sizes.setdefault(module_count, set()).add(
                    (round(float(anchor["viewBox"][2]), 6), round(float(anchor["viewBox"][3]), 6))
                )
            if any(len(sizes) != 1 for sizes in peer_anchor_sizes.values()):
                failures.append("peer districts with equal module counts must use one camera scale")
            if not any(element.get("data-navigation-hud") == "true" for element in all_elements):
                failures.append("navigable world needs a persistent navigation HUD")
            if not any(element.get("data-minimap-viewport") == "true" for element in all_elements):
                failures.append("navigable world needs a static minimap viewport indicator")
            maximum_depth = max(int(anchor.get("depth", 0)) for anchor in anchors)
            module_anchor_areas = [
                float(anchor["viewBox"][2]) * float(anchor["viewBox"][3])
                for anchor in anchors
                if anchor["kind"] == "module"
            ]
            world_area = float(navigation_plan["worldBounds"][2]) * float(
                navigation_plan["worldBounds"][3]
            )
            area_ratio = world_area / min(module_anchor_areas) if module_anchor_areas else 0.0
            if len(districts) < args.min_navigation_regions:
                failures.append(
                    f"navigation has {len(districts)} districts; required {args.min_navigation_regions}"
                )
            if maximum_depth < args.min_anchor_depth:
                failures.append(
                    f"navigation anchor depth is {maximum_depth}; required {args.min_anchor_depth}"
                )
            if area_ratio < args.min_world_detail_area_ratio:
                failures.append(
                    f"world/detail camera area ratio is {area_ratio:.2f}; "
                    f"required {args.min_world_detail_area_ratio:.2f}"
                )
            details["navigation"] = {
                "districtCount": len(districts),
                "anchorCount": len(anchors),
                "maximumAnchorDepth": maximum_depth,
                "worldDetailAreaRatio": area_ratio,
                "worldBounds": navigation_plan["worldBounds"],
                "routeStopCount": len(navigation_plan["route"]["stops"]),
                "routeDurationMs": navigation_plan["route"]["durationMs"],
                "worldNodeCount": len(world_node_ids),
                "trunkLinkCount": len(trunk_targets),
            }

        timeline = plan.get("timeline")
        sync_modes = set(plan.get("syncModes", []))
        if not {"semantic", "state", "focus"} <= sync_modes:
            failures.append("syncModes must include semantic, state, and focus")
        if timeline is not None and "time" not in sync_modes:
            failures.append("a declared timeline requires time in syncModes")
        if args.require_time_sync and timeline is None:
            failures.append("time synchronization is required but the plan timeline is null")

        for value_definition in [*plan["concepts"], *plan.get("derived", [])]:
            if f"--concept-{value_definition['id']}" not in style_text:
                failures.append(f"missing shared visual token --concept-{value_definition['id']}")

        validate_visual_identity(
            plan,
            binding_records,
            failures,
            details,
            enforce_rendered_color=not args.allow_placeholders,
        )
        physical_colors = {
            token: color.lower()
            for token, color in CONCEPT_COLOR_RE.findall(style_text)
        }
        identity = plan.get("identity")
        if isinstance(identity, dict):
            tokens = {
                str(record.get("colorToken"))
                for record in identity.values()
                if isinstance(record, dict) and isinstance(record.get("colorToken"), str)
            }
            by_physical: dict[str, list[str]] = defaultdict(list)
            for token in sorted(tokens):
                color = physical_colors.get(token)
                if color:
                    by_physical[color].append(token)
            collisions = {
                color: token_ids
                for color, token_ids in by_physical.items()
                if len(token_ids) > 1
            }
            if collisions:
                failures.append(
                    "distinct canonical color tokens resolve to identical physical colors: "
                    + json.dumps(collisions, sort_keys=True)
                )
            identity_details = details.get("identity")
            if isinstance(identity_details, dict):
                identity_details["physicalColorTokenCount"] = len(by_physical)
                identity_details["physicalColorCollisions"] = collisions

        details.update(
            {
                "compositionId": composition_id,
                "moduleCount": len(modules),
                "assetTypes": asset_types,
                "assetTypeCount": len(asset_types),
                "rendererFamilies": renderer_families,
                "rendererFamilyCount": len(renderer_families),
                "sourceConceptCount": len(plan["concepts"]),
                "derivedConceptCount": len(plan.get("derived", [])),
                "scenarioCount": len(plan["scenarios"]),
                "bindingCount": len(binding_records),
                "accessibleBindingCount": accessible_binding_count,
                "relationshipCount": len(declared_relationships),
                "timeline": timeline is not None,
                "navigableWorld": isinstance(plan.get("navigation"), dict),
            }
        )

    report = {
        "ok": not failures,
        "artifact": str(svg_path),
        "failures": failures,
        "warnings": warnings,
        "metrics": details,
        "sourceInfluence": influence,
    }
    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print(f"Synchronized SVG validation: {'PASS' if report['ok'] else 'FAIL'}")
        print(f"Artifact: {svg_path}")
        for failure in failures:
            print(f"FAIL: {failure}")
        for warning in warnings:
            print(f"WARN: {warning}")
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
