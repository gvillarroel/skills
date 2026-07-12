#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

"""Compile a compact synchronized-composition brief into a complete v1 plan."""

from __future__ import annotations

import argparse
import copy
import hashlib
import itertools
import json
import math
import os
from pathlib import Path
import sys
import tempfile
from typing import Any


sys.dont_write_bytecode = True

import scaffold_synchronized_svg as scaffold  # noqa: E402
import navigation_contract as navigation  # noqa: E402


VIEW_BOX = [0, 0, 1600, 1000]
SAFE_AREA = [48, 128, 1504, 824]
MEGACANVAS_VIEW_BOX = [0, 0, 2400, 1800]
MEGACANVAS_SAFE_AREA = [48, 128, 2304, 1624]
GAP = 24
MIN_MODULES = 6
MAX_MODULES = 16
WORLD_MIN_MODULES = 12
WORLD_MAX_MODULES = 48
WORLD_ASPECT_RATIO = 16 / 9
WORLD_NAVIGATION_VIEWPORT = [0, 120, 1600, 900]
WORLD_HEADER_HEIGHT = 260
WORLD_FOOTER_HEIGHT = 360
WORLD_MARGIN = 180
WORLD_DISTRICT_GAP = 520
WORLD_MODULE_WIDTH = 680
WORLD_HEAVY_MODULE_WIDTH = 780
WORLD_MODULE_HEIGHT = 500
WORLD_HEAVY_MODULE_HEIGHT = 540
WORLD_DISTRICT_PALETTE = (
    "#7c3aed",
    "#0891b2",
    "#2563eb",
    "#16a34a",
    "#db2777",
    "#ea580c",
    "#0f766e",
    "#9333ea",
    "#b45309",
)


class BriefError(ValueError):
    """Describe an invalid compact brief."""


class DuplicateKeyError(BriefError):
    """Reject ambiguous JSON objects before a parser can overwrite a value."""


def unique_json_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    """Build one JSON object while preserving the invariant that keys are unique."""

    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise DuplicateKeyError(f"brief contains duplicate JSON object key: {key!r}")
        result[key] = value
    return result


class JsonArgumentParser(argparse.ArgumentParser):
    """Keep argument failures machine-readable for automation."""

    def error(self, message: str) -> None:
        print(json.dumps({"ok": False, "error": f"argument error: {message}"}, indent=2))
        raise SystemExit(2)


def parse_args() -> argparse.Namespace:
    parser = JsonArgumentParser(
        description="Compile a compact synchronized-SVG brief into a validated v1 composition plan."
    )
    parser.add_argument("--brief", required=True, type=Path, help="Compact brief JSON")
    parser.add_argument("--output", required=True, type=Path, help="Exact plan JSON output path")
    parser.add_argument("--force", action="store_true", help="Replace an existing output plan")
    parser.add_argument("--json", action="store_true", help="Print a JSON result")
    # Keep one observed harmless typo machine-readable and atomic without
    # advertising it as a second public spelling. Normal-use instructions
    # still require the literal --json switch.
    parser.add_argument("--js", dest="json", action="store_true", help=argparse.SUPPRESS)
    return parser.parse_args()


def load_brief(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise BriefError(f"brief file does not exist: {path}")
    try:
        value = json.loads(
            path.read_text(encoding="utf-8"),
            object_pairs_hook=unique_json_object,
        )
    except json.JSONDecodeError as exc:
        raise BriefError(f"brief is not valid JSON: {exc}") from exc
    if not isinstance(value, dict):
        raise BriefError("brief root must be a JSON object")
    return value


def require_text(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise BriefError(f"{label} must be a non-empty string")
    return value.strip()


def require_id(value: Any, label: str) -> str:
    try:
        return scaffold.require_id(value, label)
    except ValueError as exc:
        raise BriefError(str(exc)) from exc


def finite_number(value: Any, label: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise BriefError(f"{label} must be a finite number")
    result = float(value)
    if not math.isfinite(result):
        raise BriefError(f"{label} must be a finite number")
    return result


def clean_number(value: float) -> int | float:
    """Preserve canonical numeric truth while keeping exact integers compact."""

    value = float(value)
    if value == 0.0:
        return 0
    if value.is_integer():
        return int(value)
    return value


def reconciliation_tolerance(values: list[float]) -> float:
    """Return an operation-scale tolerance without a unit-dependent floor."""

    magnitudes = [abs(float(value)) for value in values]
    if any(not math.isfinite(value) for value in magnitudes):
        raise BriefError("flow reconciliation values must remain finite")
    scale = max(magnitudes, default=0.0)
    operations = max(1, len(values))
    tolerance = max(
        math.ulp(scale) * 64 * operations,
        sys.float_info.epsilon * scale * 64 * operations,
        math.ulp(0.0),
    )
    if not math.isfinite(tolerance):
        raise BriefError("flow reconciliation tolerance overflowed")
    return tolerance


def flow_reconciliation(source_value: float, branch_values: list[float]) -> tuple[bool, float]:
    """Check one algebraic flow split without allowing overflow to look conserved."""

    source_value = float(source_value)
    normalized_branches = [float(value) for value in branch_values]
    branch_total = 0.0
    for branch_value in normalized_branches:
        branch_total += branch_value
    tolerance = reconciliation_tolerance([source_value, *normalized_branches])
    difference = source_value - branch_total
    reconciles = (
        math.isfinite(branch_total)
        and math.isfinite(difference)
        and abs(difference) <= tolerance
    )
    return reconciles, branch_total


def additive_reference_coefficients(node: Any) -> dict[str, int] | None:
    """Return signed reference counts for a pure additive expression."""

    if isinstance(node, (int, float)) and not isinstance(node, bool):
        return {}
    if not isinstance(node, dict):
        return None
    if set(node) == {"ref"} and isinstance(node.get("ref"), str):
        return {str(node["ref"]): 1}
    operation = node.get("op")
    arguments = node.get("args")
    if operation not in {"add", "subtract"} or not isinstance(arguments, list):
        return None

    coefficients: dict[str, int] = {}
    for index, argument in enumerate(arguments):
        nested = additive_reference_coefficients(argument)
        if nested is None:
            return None
        direction = -1 if operation == "subtract" and index > 0 else 1
        for value_id, coefficient in nested.items():
            coefficients[value_id] = coefficients.get(value_id, 0) + direction * coefficient
    return {value_id: coefficient for value_id, coefficient in coefficients.items() if coefficient}


def reject_partition_double_counts(
    module_id: str,
    source_id: str,
    branch_ids: list[str],
    computations: dict[str, Any],
) -> None:
    """Reject a derived rollup that adds a conserved total to one of its parts."""

    for derived_id, computation in computations.items():
        coefficients = additive_reference_coefficients(computation)
        if not coefficients:
            continue
        source_coefficient = coefficients.get(source_id, 0)
        if not source_coefficient:
            continue
        duplicated_branches = [
            branch_id
            for branch_id in branch_ids
            if source_coefficient * coefficients.get(branch_id, 0) > 0
        ]
        if duplicated_branches:
            raise BriefError(
                f"derived value {derived_id!r} double-counts conserved partition {module_id!r}: "
                f"conserved total {source_id!r} is added as a peer of its own branch(es) "
                f"{duplicated_branches}. Use either the total or mutually exclusive branches; "
                "a reconciliation check may subtract branches from the total"
            )


def module_partition_contracts(
    values: list[str],
    computations: dict[str, Any],
    units: dict[str, str],
) -> list[tuple[str, list[str]]]:
    """Infer exact additive or residual partitions selected in one module."""

    selected = set(values)
    contracts: list[tuple[str, list[str]]] = []
    for value_id in values:
        node = computations.get(value_id)
        if not isinstance(node, dict) or not isinstance(node.get("args"), list):
            continue
        operation = node.get("op")
        arguments = node["args"]
        if len(arguments) < 2 or any(
            not isinstance(argument, dict)
            or set(argument) != {"ref"}
            or not isinstance(argument.get("ref"), str)
            for argument in arguments
        ):
            continue
        references = [str(argument["ref"]) for argument in arguments]
        if operation == "add":
            total_id = value_id
            branch_ids = references
        elif operation == "subtract":
            total_id = references[0]
            branch_ids = [*references[1:], value_id]
        else:
            continue
        contract_values = [total_id, *branch_ids]
        if (
            set(contract_values) <= selected
            and len(set(contract_values)) == len(contract_values)
            and len({units[item] for item in contract_values}) == 1
        ):
            contracts.append((total_id, branch_ids))
    return contracts


def direct_refs(node: Any, known: set[str], label: str) -> set[str]:
    try:
        return scaffold.validate_compute(node, known, label)
    except ValueError as exc:
        raise BriefError(str(exc)) from exc


def direct_divisor_sources(node: Any, source_ids: set[str]) -> set[str]:
    if not isinstance(node, dict):
        return set()
    refs: set[str] = set()
    args = node.get("args")
    if node.get("op") == "divide" and isinstance(args, list) and len(args) == 2:
        denominator = args[1]
        if isinstance(denominator, dict) and set(denominator) == {"ref"}:
            ref = denominator["ref"]
            if ref in source_ids:
                refs.add(ref)
    if isinstance(args, list):
        for argument in args:
            refs.update(direct_divisor_sources(argument, source_ids))
    return refs


def topological_order(
    source_ids: set[str], derived: list[dict[str, Any]]
) -> list[str]:
    derived_ids = {item["id"] for item in derived}
    remaining = {
        item["id"]: {ref for ref in item["dependsOn"] if ref in derived_ids}
        for item in derived
    }
    resolved = set(source_ids)
    order: list[str] = []
    while remaining:
        ready = sorted(item_id for item_id, dependencies in remaining.items() if dependencies <= resolved)
        if not ready:
            raise BriefError("derived dependency graph contains a cycle")
        for item_id in ready:
            order.append(item_id)
            resolved.add(item_id)
            del remaining[item_id]
    return order


def normalize_divisor_domains(
    concepts: list[dict[str, Any]],
    derived: list[dict[str, Any]],
    scenarios_raw: list[Any],
    timeline_raw: Any,
) -> list[dict[str, Any]]:
    """Exclude exact zero only for source concepts used as direct divisors."""

    source_ids = {item["id"] for item in concepts}
    required: set[str] = set()
    for item in derived:
        required.update(direct_divisor_sources(item["compute"], source_ids))
    normalizations: list[dict[str, Any]] = []
    for concept in concepts:
        concept_id = concept["id"]
        if concept_id not in required:
            continue
        low, high = (float(item) for item in concept["domain"])
        if not low <= 0 <= high:
            continue
        observed = [float(concept["default"])]
        for index, scenario in enumerate(scenarios_raw):
            if not isinstance(scenario, dict):
                raise BriefError(f"scenarios[{index}] must be an object")
            values = scenario.get("values")
            if isinstance(values, dict) and concept_id in values:
                observed.append(finite_number(values[concept_id], f"scenarios[{index}].values.{concept_id}"))
        if isinstance(timeline_raw, dict) and isinstance(timeline_raw.get("phases"), list):
            for index, phase in enumerate(timeline_raw["phases"]):
                if not isinstance(phase, dict):
                    continue
                values = phase.get("values")
                if isinstance(values, dict) and concept_id in values:
                    observed.append(
                        finite_number(
                            values[concept_id],
                            f"timeline.phases[{index}].values.{concept_id}",
                        )
                    )
        if any(value == 0 for value in observed):
            raise BriefError(
                f"source divisor {concept_id!r} has a zero default, scenario, or timeline value; "
                "provide a legal non-zero value"
            )
        signs = {1 if value > 0 else -1 for value in observed}
        if len(signs) != 1:
            raise BriefError(
                f"source divisor {concept_id!r} crosses zero across default/scenario states; use one legal sign"
            )
        span = high - low
        smallest_observed = min(abs(value) for value in observed)
        epsilon = max(
            abs(float(concept["default"])) * 0.05,
            span * 0.01,
            smallest_observed * 0.5,
            1e-9,
        )
        epsilon = min(epsilon, smallest_observed)
        old_domain = list(concept["domain"])
        if 1 in signs:
            new_domain = [clean_number(epsilon), clean_number(high)]
        else:
            new_domain = [clean_number(low), clean_number(-epsilon)]
        if float(new_domain[0]) >= float(new_domain[1]):
            raise BriefError(f"could not normalize divisor domain for {concept_id!r}")
        concept["domain"] = new_domain
        normalizations.append(
            {
                "sourceId": concept_id,
                "oldDomain": old_domain,
                "newDomain": new_domain,
                "reason": "Direct division requires a legal source domain that excludes exact zero.",
            }
        )
    return normalizations


def compile_concepts(raw: Any) -> list[dict[str, Any]]:
    if not isinstance(raw, list) or not raw:
        raise BriefError("concepts must be a non-empty array")
    result: list[dict[str, Any]] = []
    seen: set[str] = set()
    for index, item in enumerate(raw):
        if not isinstance(item, dict):
            raise BriefError(f"concepts[{index}] must be an object")
        concept_id = require_id(item.get("id"), f"concepts[{index}].id")
        if concept_id in seen:
            raise BriefError(f"duplicate concept id: {concept_id}")
        seen.add(concept_id)
        default = finite_number(item.get("default"), f"concept {concept_id!r} default")
        domain = item.get("domain")
        if not isinstance(domain, list) or len(domain) != 2:
            raise BriefError(f"concept {concept_id!r} domain must be [low, high]")
        low = finite_number(domain[0], f"concept {concept_id!r} domain[0]")
        high = finite_number(domain[1], f"concept {concept_id!r} domain[1]")
        if low >= high or not low <= default <= high:
            raise BriefError(f"concept {concept_id!r} has an invalid domain/default")
        interpolation = item.get("interpolation", "linear")
        if interpolation not in {"linear", "step"}:
            raise BriefError(f"concept {concept_id!r} interpolation must be linear or step")
        result.append(
            {
                "id": concept_id,
                "label": require_text(item.get("label"), f"concept {concept_id!r} label"),
                "unit": require_text(item.get("unit"), f"concept {concept_id!r} unit"),
                "type": "number",
                "interpolation": interpolation,
                "default": clean_number(default),
                "domain": [clean_number(low), clean_number(high)],
            }
        )
    return result


def compile_derived(raw: Any, source_ids: set[str]) -> list[dict[str, Any]]:
    if raw is None:
        return []
    if not isinstance(raw, list):
        raise BriefError("derived must be an array")
    pending_ids: set[str] = set()
    for index, item in enumerate(raw):
        if not isinstance(item, dict):
            raise BriefError(f"derived[{index}] must be an object")
        item_id = require_id(item.get("id"), f"derived[{index}].id")
        if item_id in source_ids or item_id in pending_ids:
            raise BriefError(f"duplicate derived id: {item_id}")
        pending_ids.add(item_id)
    known = source_ids | pending_ids
    result: list[dict[str, Any]] = []
    for index, item in enumerate(raw):
        item_id = item["id"]
        compute = copy.deepcopy(item.get("compute"))
        refs = direct_refs(compute, known, f"derived[{index}].compute")
        compiled = {
            "id": item_id,
            "label": require_text(item.get("label"), f"derived {item_id!r} label"),
            "unit": require_text(item.get("unit"), f"derived {item_id!r} unit"),
            "type": "number",
            "dependsOn": sorted(refs),
            "compute": compute,
        }
        if item.get("colorSource") is not None:
            color_source = require_id(item["colorSource"], f"derived {item_id!r} colorSource")
            if color_source not in known:
                raise BriefError(
                    f"derived {item_id!r} colorSource must name a canonical source or derived value"
                )
            compiled["colorSource"] = color_source
        result.append(compiled)
    topological_order(source_ids, result)
    return result


def compile_scenarios(raw: Any, concepts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if not isinstance(raw, list) or not raw:
        raise BriefError("scenarios must be a non-empty array")
    domains = {item["id"]: (float(item["domain"][0]), float(item["domain"][1])) for item in concepts}
    result: list[dict[str, Any]] = []
    seen: set[str] = set()
    for index, item in enumerate(raw):
        if not isinstance(item, dict):
            raise BriefError(f"scenarios[{index}] must be an object")
        scenario_id = require_id(item.get("id"), f"scenarios[{index}].id")
        if scenario_id in seen:
            raise BriefError(f"duplicate scenario id: {scenario_id}")
        seen.add(scenario_id)
        values = item.get("values")
        if not isinstance(values, dict) or not values:
            raise BriefError(f"scenario {scenario_id!r} values must be a non-empty object")
        compiled_values: dict[str, int | float] = {}
        for value_id in sorted(values):
            if value_id not in domains:
                raise BriefError(f"scenario {scenario_id!r} contains non-source value {value_id!r}")
            value = finite_number(values[value_id], f"scenario {scenario_id!r} value {value_id!r}")
            low, high = domains[value_id]
            if not low <= value <= high:
                raise BriefError(
                    f"scenario {scenario_id!r} value {value_id!r} is outside its legal domain"
                )
            compiled_values[value_id] = clean_number(value)
        result.append(
            {
                "id": scenario_id,
                "label": require_text(
                    item.get("label", scenario_id.replace("-", " ").title()),
                    f"scenario {scenario_id!r} label",
                ),
                "values": compiled_values,
            }
        )
    return result


def interval_for_node(node: Any, intervals: dict[str, tuple[float, float]]) -> tuple[float, float]:
    if isinstance(node, (int, float)) and not isinstance(node, bool):
        value = float(node)
        return value, value
    if "ref" in node:
        return intervals[node["ref"]]
    op = node["op"]
    args = [interval_for_node(argument, intervals) for argument in node["args"]]
    if op == "add":
        return sum(item[0] for item in args), sum(item[1] for item in args)
    if op == "subtract":
        return (
            args[0][0] - sum(item[1] for item in args[1:]),
            args[0][1] - sum(item[0] for item in args[1:]),
        )
    if op == "multiply":
        low, high = args[0]
        for next_low, next_high in args[1:]:
            products = (low * next_low, low * next_high, high * next_low, high * next_high)
            low, high = min(products), max(products)
        return low, high
    if op == "divide":
        denominator = args[1]
        if denominator[0] <= 0 <= denominator[1]:
            raise BriefError("a derived division denominator can still reach zero")
        quotients = (
            args[0][0] / denominator[0],
            args[0][0] / denominator[1],
            args[0][1] / denominator[0],
            args[0][1] / denominator[1],
        )
        return min(quotients), max(quotients)
    if op == "min":
        return min(item[0] for item in args), min(item[1] for item in args)
    if op == "max":
        return max(item[0] for item in args), max(item[1] for item in args)
    if op == "clamp":
        value, low_limit, high_limit = args
        low_bound = min(low_limit[0], low_limit[1])
        high_bound = max(high_limit[0], high_limit[1])
        return max(value[0], low_bound), min(value[1], high_bound)
    if op == "round":
        padding = 0.5
        if len(args) == 2 and args[1][0] == args[1][1]:
            padding = 0.5 * (10 ** -int(args[1][0]))
        return args[0][0] - padding, args[0][1] + padding
    raise BriefError(f"unsupported computation operation {op!r}")


def value_intervals(
    concepts: list[dict[str, Any]], derived: list[dict[str, Any]]
) -> dict[str, tuple[float, float]]:
    intervals = {
        item["id"]: (float(item["domain"][0]), float(item["domain"][1]))
        for item in concepts
    }
    by_id = {item["id"]: item for item in derived}
    for item_id in topological_order(set(intervals), derived):
        low, high = interval_for_node(by_id[item_id]["compute"], intervals)
        if not math.isfinite(low) or not math.isfinite(high):
            raise BriefError(f"derived value {item_id!r} has a non-finite legal envelope")
        if low > high:
            low, high = high, low
        if low == high:
            padding = max(abs(low) * 0.1, 1.0)
            low, high = low - padding, high + padding
        intervals[item_id] = (low, high)
    return intervals


def sampled_value_states(
    concepts: list[dict[str, Any]],
    derived: list[dict[str, Any]],
    scenarios: list[dict[str, Any]],
) -> list[tuple[str, dict[str, float]]]:
    """Resolve defaults and named scenarios for cross-value semantic checks."""

    defaults = {item["id"]: float(item["default"]) for item in concepts}

    def resolve(patch: dict[str, Any]) -> dict[str, float]:
        values = dict(defaults)
        values.update({value_id: float(value) for value_id, value in patch.items()})
        pending = {item["id"]: item for item in derived}
        while pending:
            progressed = False
            for value_id, item in list(pending.items()):
                if set(item["dependsOn"]) <= set(values):
                    values[value_id] = scaffold.eval_node(item["compute"], values)
                    del pending[value_id]
                    progressed = True
            if not progressed:  # pragma: no cover - compile_derived rejects cycles
                raise BriefError("could not resolve sampled derived values")
        return values

    states = [("defaults", resolve({}))]
    states.extend(
        (f"scenario {scenario['id']!r}", resolve(scenario["values"]))
        for scenario in scenarios
    )
    return states


def family_for(asset_type: str) -> str:
    tokens = set(asset_type.lower().replace("_", "-").split("-"))
    text = asset_type.lower()
    if "waterfall" in tokens or "waterfall" in text:
        return "waterfall"
    if tokens & {"bar", "bars", "column", "histogram", "stacked"}:
        return "bar"
    if tokens & {"line", "area", "time", "timeline", "spark", "trend", "series"}:
        return "line"
    if tokens & {"flow", "sankey", "process", "funnel", "journey", "pipeline"}:
        return "flow"
    if tokens & {"gauge", "bullet", "capacity", "meter", "progress", "dial"}:
        return "gauge"
    if tokens & {"map", "spatial", "geo", "geographic", "choropleth", "topology"}:
        return "spatial"
    if tokens & {"table", "matrix", "heatmap", "grid", "reconciliation"}:
        return "table"
    if tokens & {"network", "hierarchy", "tree", "graph", "node", "org"}:
        return "network"
    return "fallback"


def value_format(unit: str) -> dict[str, Any]:
    if unit == "fraction":
        return {"style": "percent", "maximumFractionDigits": 1}
    if "/" in unit:
        prefix = unit.split("/", 1)[0]
        if len(prefix) == 3 and prefix.isalpha() and prefix.upper() == prefix:
            return {"style": "currency", "currency": prefix, "maximumFractionDigits": 0}
    return {"style": "decimal", "maximumFractionDigits": 2, "suffix": f" {unit}"}


def transform_for(domain: tuple[float, float], target: list[float]) -> dict[str, Any]:
    low, high = domain
    if low == high:
        high = low + max(abs(low) * 0.1, 1.0)
    return {
        "op": "linear",
        "domain": [clean_number(low), clean_number(high)],
        "range": [clean_number(target[0]), clean_number(target[1])],
        "clamp": True,
    }


def unique_cues(value_ids: list[str]) -> dict[str, str]:
    tokens_by_value = {value_id: value_id.split("-") for value_id in value_ids}
    counts: dict[str, int] = {}
    for tokens in tokens_by_value.values():
        for token in set(tokens):
            counts[token] = counts.get(token, 0) + 1
    result: dict[str, str] = {}
    used: set[str] = set()
    for index, value_id in enumerate(value_ids, start=1):
        candidates = [token for token in tokens_by_value[value_id] if counts[token] == 1 and token not in used]
        cue = max(candidates, key=lambda token: (len(token), token)) if candidates else f"cue{index:02d}"
        used.add(cue)
        result[value_id] = cue
    return result


def identity_color_tokens(
    concepts: list[dict[str, Any]], derived: list[dict[str, Any]]
) -> dict[str, str]:
    """Infer scale-preserving aliases and validate deliberate color ancestry."""

    source_order = [item["id"] for item in concepts]
    source_set = set(source_order)
    derived_by_id = {item["id"]: item for item in derived}

    def canonical_ancestry(value_id: str) -> set[str]:
        if value_id in source_set:
            return set()
        result: set[str] = set()
        pending = list(derived_by_id[value_id]["dependsOn"])
        while pending:
            dependency = pending.pop()
            if dependency in result:
                continue
            result.add(dependency)
            if dependency in derived_by_id:
                pending.extend(derived_by_id[dependency]["dependsOn"])
        return result

    def scale_reference(node: Any) -> str | None:
        if isinstance(node, dict) and set(node) == {"ref"}:
            return str(node["ref"])
        if not isinstance(node, dict) or set(node) != {"op", "args"}:
            return None
        op = node.get("op")
        args = node.get("args")
        if not isinstance(args, list):
            return None
        if op == "multiply":
            refs = [scale_reference(arg) for arg in args if isinstance(arg, dict)]
            if any(ref is None for ref in refs) or any(
                not isinstance(arg, (int, float)) and not isinstance(arg, dict) for arg in args
            ):
                return None
            concrete = [ref for ref in refs if ref is not None]
            return concrete[0] if len(concrete) == 1 else None
        if op in {"divide", "round"} and args:
            reference = scale_reference(args[0])
            if reference is None or any(
                isinstance(arg, bool) or not isinstance(arg, (int, float)) for arg in args[1:]
            ):
                return None
            return reference
        return None

    result = {value_id: value_id for value_id in source_order}
    order = topological_order(source_set, list(derived_by_id.values()))
    for value_id in order:
        item = derived_by_id[value_id]
        preferred = item.get("colorSource") or scale_reference(item.get("compute"))
        if preferred is None:
            result[value_id] = value_id
            continue
        if preferred not in canonical_ancestry(value_id):
            raise BriefError(
                f"derived {value_id!r} colorSource {preferred!r} is not a semantic ancestor in the canonical DAG"
            )
        result[value_id] = result[str(preferred)]
    return result


def binding_channel(
    family: str,
    asset_type: str,
    index: int,
    value_id: str,
    unit: str,
    domain: tuple[float, float],
) -> tuple[str, dict[str, Any] | None]:
    magnitude_domain = (min(0.0, domain[0]), max(0.0, domain[1]))
    if family == "table":
        return "text", None
    if family == "waterfall":
        return "height", transform_for(magnitude_domain, [0, 180])
    if family == "bar":
        return "width", transform_for(magnitude_domain, [0, 240])
    if family == "line":
        return "y", transform_for(domain, [100, 0])
    if family == "flow":
        if domain[0] < 0 and index > 0:
            return "text", None
        return "width", transform_for(magnitude_domain, [0, 180])
    if family == "gauge":
        radial = any(token in asset_type.lower() for token in ("radial", "dial", "gauge"))
        if index == 0 and radial:
            return (
                "transform",
                {
                    "op": "rotate",
                    "domain": [clean_number(domain[0]), clean_number(domain[1])],
                    "range": [-180, 0],
                    "center": [240, 190],
                    "clamp": True,
                },
            )
        if index == 0:
            target_asset = any(token in asset_type.lower() for token in ("bullet", "progress"))
            if target_asset and unit in {"fraction", "percent", "%"}:
                target = 1.0 if unit == "fraction" else 100.0
                display_domain = (
                    0.0,
                    max(target, min(domain[1], target * 1.5)),
                )
                return "width", transform_for(display_domain, [0, 390])
            return "width", transform_for(magnitude_domain, [0, 390])
        return "text", None
    if family == "spatial":
        if index == 0:
            return "x", transform_for(domain, [30, 280])
        if index == 1:
            return "y", transform_for(domain, [30, 180])
        return "opacity", transform_for(domain, [0.2, 1])
    if family == "network":
        # Compact network modules are topological overviews.  Keep node areas
        # equal and bind exact text so unlike units never imply a shared scale.
        return "text", None
    return "width", transform_for(magnitude_domain, [0, 240])


def dependency_closure(value_id: str, dependencies: dict[str, set[str]]) -> set[str]:
    result: set[str] = set()
    pending = list(dependencies.get(value_id, set()))
    while pending:
        dependency = pending.pop()
        if dependency in result:
            continue
        result.add(dependency)
        pending.extend(dependencies.get(dependency, set()))
    return result


def leading_subtract_ref(node: Any) -> str | None:
    current = node
    while isinstance(current, dict) and current.get("op") == "subtract":
        args = current.get("args")
        if not isinstance(args, list) or len(args) < 2:
            return None
        current = args[0]
    if isinstance(current, dict) and set(current) == {"ref"} and isinstance(current["ref"], str):
        return current["ref"]
    return None


def infer_flow_values(
    values: list[str],
    computations: dict[str, Any],
    units: dict[str, str],
) -> list[str]:
    """Put a credible conserved source first, adding an omitted minuend when safe."""

    source: str | None = None
    for value_id in values:
        source_ref = leading_subtract_ref(computations.get(value_id))
        if source_ref is not None and source_ref in units and units[source_ref] == units[value_id]:
            source = source_ref
            break
    if source is None:
        selected = set(values)
        for value_id in values:
            node = computations.get(value_id)
            if not isinstance(node, dict) or node.get("op") != "add":
                continue
            refs = {
                argument["ref"]
                for argument in node.get("args", [])
                if isinstance(argument, dict) and set(argument) == {"ref"}
            }
            if len(refs & selected) >= 2:
                source = value_id
                break
    if source is None:
        return values
    return [source, *[value_id for value_id in values if value_id != source]]


def compile_structural_diagram(
    raw: Any,
    *,
    module_id: str,
    values: list[str],
    known_values: set[str],
) -> dict[str, Any] | None:
    """Compile qualitative parent/prerequisite topology without inventing arithmetic."""

    if raw is None:
        return None
    if not isinstance(raw, dict):
        raise BriefError(f"module {module_id!r} diagram must be an object")
    nodes_raw = raw.get("nodes")
    links_raw = raw.get("links")
    if not isinstance(nodes_raw, list) or not 2 <= len(nodes_raw) <= 18:
        raise BriefError(f"module {module_id!r} diagram.nodes must contain 2 to 18 nodes")
    if not isinstance(links_raw, list) or not 1 <= len(links_raw) <= 32:
        raise BriefError(f"module {module_id!r} diagram.links must contain 1 to 32 links")
    node_ids: set[str] = set()
    nodes: list[dict[str, Any]] = []
    bound_values: set[str] = set()
    for index, node in enumerate(nodes_raw):
        if not isinstance(node, dict):
            raise BriefError(f"module {module_id!r} diagram.nodes[{index}] must be an object")
        node_id = require_id(node.get("id"), f"module {module_id!r} diagram node {index} id")
        if node_id in node_ids:
            raise BriefError(f"module {module_id!r} repeats diagram node id {node_id!r}")
        node_ids.add(node_id)
        kind = node.get("kind", "leaf")
        if kind not in {"root", "notable", "merge", "gate", "leaf", "evidence"}:
            raise BriefError(
                f"module {module_id!r} diagram node {node_id!r} kind must be root, notable, "
                "merge, gate, leaf, or evidence"
            )
        compiled_node: dict[str, Any] = {
            "id": node_id,
            "label": require_text(
                node.get("label"), f"module {module_id!r} diagram node {node_id!r} label"
            ),
            "kind": kind,
        }
        bind = node.get("bind")
        if bind is not None:
            bind = require_id(bind, f"module {module_id!r} diagram node {node_id!r} bind")
            if bind not in known_values or bind not in values:
                raise BriefError(
                    f"module {module_id!r} diagram node {node_id!r} bind {bind!r} must name "
                    "one of the module's declared values"
                )
            if bind in bound_values:
                raise BriefError(
                    f"module {module_id!r} structural diagram binds value {bind!r} more than once; "
                    "use one canonical bound node and qualitative descendants"
                )
            compiled_node["bind"] = bind
            bound_values.add(bind)
        if node.get("note") is not None:
            compiled_node["note"] = require_text(
                node.get("note"), f"module {module_id!r} diagram node {node_id!r} note"
            )
        nodes.append(compiled_node)
    links: list[dict[str, Any]] = []
    link_ids: set[str] = set()
    adjacency: dict[str, set[str]] = {node_id: set() for node_id in node_ids}
    for index, link in enumerate(links_raw):
        if not isinstance(link, dict):
            raise BriefError(f"module {module_id!r} diagram.links[{index}] must be an object")
        link_id = require_id(link.get("id"), f"module {module_id!r} diagram link {index} id")
        if link_id in link_ids:
            raise BriefError(f"module {module_id!r} repeats diagram link id {link_id!r}")
        link_ids.add(link_id)
        source = require_id(link.get("source"), f"module {module_id!r} diagram link source")
        target = require_id(link.get("target"), f"module {module_id!r} diagram link target")
        if source == target or source not in node_ids or target not in node_ids:
            raise BriefError(
                f"module {module_id!r} diagram link {link_id!r} must connect two declared nodes"
            )
        kind = link.get("kind", "prerequisite")
        if kind not in {"parent", "prerequisite", "dependency", "flow", "feedback"}:
            raise BriefError(
                f"module {module_id!r} diagram link {link_id!r} has unsupported kind {kind!r}"
            )
        compiled_link: dict[str, Any] = {
            "id": link_id,
            "source": source,
            "target": target,
            "kind": kind,
        }
        if link.get("label") is not None:
            compiled_link["label"] = require_text(
                link.get("label"), f"module {module_id!r} diagram link {link_id!r} label"
            )
        links.append(compiled_link)
        adjacency[source].add(target)
        adjacency[target].add(source)
    visited: set[str] = set()
    pending = [nodes[0]["id"]]
    while pending:
        node_id = pending.pop()
        if node_id in visited:
            continue
        visited.add(node_id)
        pending.extend(sorted(adjacency[node_id] - visited))
    if visited != node_ids:
        raise BriefError(
            f"module {module_id!r} structural diagram must be connected; isolated node(s): "
            f"{sorted(node_ids - visited)}"
        )
    missing_bindings = sorted(set(values) - bound_values)
    if missing_bindings:
        raise BriefError(
            f"module {module_id!r} structural diagram must bind every declared value to at least "
            f"one node; missing value(s): {missing_bindings}"
        )
    layout = raw.get("layout", "tree")
    if layout not in {"tree", "radial", "lanes"}:
        raise BriefError(
            f"module {module_id!r} diagram.layout must be tree, radial, or lanes"
        )
    return {
        "layout": layout,
        "nodes": nodes,
        "links": links,
    }


def compile_module_shells(
    raw: Any,
    known_values: set[str],
    labels: dict[str, str],
    units: dict[str, str],
    intervals: dict[str, tuple[float, float]],
    dependencies: dict[str, set[str]],
    computations: dict[str, Any],
    cues: dict[str, str],
    value_states: list[tuple[str, dict[str, float]]],
    *,
    minimum_modules: int = MIN_MODULES,
    maximum_modules: int = MAX_MODULES,
) -> list[dict[str, Any]]:
    if not isinstance(raw, list) or not minimum_modules <= len(raw) <= maximum_modules:
        raise BriefError(
            f"modules must contain {minimum_modules} to {maximum_modules} items"
        )
    result: list[dict[str, Any]] = []
    seen: set[str] = set()
    source_ids = known_values - set(computations)
    sampled_envelopes: dict[str, tuple[float, float]] = {}

    def semantic_envelope(value_id: str) -> tuple[float, float]:
        """Tighten sign checks by evaluating correlated source-domain corners."""

        if value_id in sampled_envelopes:
            return sampled_envelopes[value_id]
        if value_id in source_ids:
            sampled_envelopes[value_id] = intervals[value_id]
            return intervals[value_id]
        required_sources: set[str] = set()
        pending = [value_id]
        while pending:
            current = pending.pop()
            for dependency in dependencies.get(current, set()):
                if dependency in source_ids:
                    required_sources.add(dependency)
                else:
                    pending.append(dependency)
        if len(required_sources) > 12:
            sampled_envelopes[value_id] = intervals[value_id]
            return intervals[value_id]
        ordered_sources = sorted(required_sources)
        observed: list[float] = []

        def resolve(current: str, state: dict[str, float]) -> float:
            if current in state:
                return state[current]
            for dependency in dependencies.get(current, set()):
                resolve(dependency, state)
            state[current] = float(scaffold.eval_node(computations[current], state))
            return state[current]

        endpoints = [intervals[source_id] for source_id in ordered_sources]
        for corner in itertools.product(*endpoints):
            state = dict(zip(ordered_sources, (float(value) for value in corner)))
            observed.append(resolve(value_id, state))
        envelope = (min(observed), max(observed)) if observed else intervals[value_id]
        sampled_envelopes[value_id] = envelope
        return envelope

    for index, item in enumerate(raw):
        if not isinstance(item, dict):
            raise BriefError(f"modules[{index}] must be an object")
        module_id = require_id(item.get("id"), f"modules[{index}].id")
        if module_id in seen:
            raise BriefError(f"duplicate module id: {module_id}")
        seen.add(module_id)
        asset_type = require_id(item.get("assetType"), f"module {module_id!r} assetType")
        values = item.get("values")
        if (
            not isinstance(values, list)
            or not values
            or any(not isinstance(value, str) for value in values)
            or len(values) != len(set(values))
        ):
            raise BriefError(f"module {module_id!r} values must be a non-empty unique list")
        unknown = [value for value in values if value not in known_values]
        if unknown:
            raise BriefError(f"module {module_id!r} references unknown values: {unknown}")
        values = list(values)
        family = family_for(asset_type)
        if family == "fallback":
            raise BriefError(
                f"module {module_id!r} assetType {asset_type!r} does not select a supported "
                "renderer family. Include a semantic family token for bar, flow/sankey, "
                "gauge/bullet/progress, line/timeline, network/graph, spatial/map, "
                "table/matrix, or waterfall"
            )
        structural_diagram = compile_structural_diagram(
            item.get("diagram"),
            module_id=module_id,
            values=values,
            known_values=known_values,
        )
        if structural_diagram is not None and family != "network":
            raise BriefError(
                f"module {module_id!r} diagram is valid only with a network/graph/tree assetType"
            )
        for partition_total, partition_branches in module_partition_contracts(
            values,
            computations,
            units,
        ):
            reject_partition_double_counts(
                module_id,
                partition_total,
                partition_branches,
                computations,
            )
        if family == "bar" and "stack" in asset_type:
            selected = set(values)
            claim_text = " ".join(
                (
                    str(item.get("question", "")),
                    str(item.get("claim", "")),
                )
            ).lower().replace("-", " ")
            candidates: list[str] = []
            declared_total = item.get("stackTotal")
            if isinstance(declared_total, str) and declared_total in known_values:
                candidates.append(declared_total)
            else:
                for candidate in sorted(known_values):
                    label_phrase = labels[candidate].lower().replace("-", " ")
                    id_phrase = candidate.replace("-", " ")
                    if label_phrase in claim_text or id_phrase in claim_text:
                        candidates.append(candidate)
            for candidate in candidates:
                if candidate in selected:
                    continue
                represented_parts = dependency_closure(candidate, dependencies) & selected
                if len(represented_parts) >= 2:
                    values.append(candidate)
                    selected.add(candidate)
        if family == "flow":
            values = infer_flow_values(values, computations, units)
            flow_units = {units[value_id] for value_id in values}
            if len(flow_units) != 1:
                raise BriefError(
                    f"module {module_id!r} flow values must share one unit; found {sorted(flow_units)}"
                )
            if len(values) < 2:
                raise BriefError(f"module {module_id!r} flow needs one source and at least one branch")
            source_id = values[0]
            branch_ids = values[1:]
            reject_partition_double_counts(
                module_id,
                source_id,
                branch_ids,
                computations,
            )
            for state_label, state in value_states:
                source_value = float(state[source_id])
                branch_values = [float(state[value_id]) for value_id in branch_ids]
                reconciles, branch_total = flow_reconciliation(source_value, branch_values)
                if not reconciles:
                    raise BriefError(
                        f"module {module_id!r} flow does not conserve {units[source_id]!r} in "
                        f"{state_label}: source {source_id!r}={clean_number(source_value)} but "
                        f"branches {branch_ids} sum to {clean_number(branch_total)}. Put the "
                        "conserved total first and include only mutually exclusive branches, or "
                        "use a table/network for nonconserving comparisons"
                    )
        if family == "network" and structural_diagram is None and not any(
            dependency in values
            for value_id in values
            for dependency in dependencies.get(value_id, set())
        ):
            raise BriefError(
                f"module {module_id!r} selects a network asset but its values contain no declared "
                "dependency edge; include related source/derived values or choose a non-network asset"
            )
        if family == "network" and structural_diagram is None:
            selected_values = set(values)
            missing_direct_parents = [
                (value_id, sorted(dependencies.get(value_id, set()) - selected_values))
                for value_id in values
                if value_id in computations
                and dependencies.get(value_id, set()) - selected_values
            ]
            if missing_direct_parents:
                value_id, missing = missing_direct_parents[0]
                raise BriefError(
                    f"module {module_id!r} network selects derived node {value_id!r} but omits "
                    f"direct parent node(s) {missing}. Include every direct parent needed to "
                    "reconstruct each visible derived node, or remove that derived endpoint"
                )
            missing_bridges: list[tuple[str, str, list[str]]] = []
            for value_id in values:
                for dependency in sorted(dependencies.get(value_id, set())):
                    if dependency in selected_values:
                        continue
                    hidden_ancestors = sorted(
                        ({dependency} | dependency_closure(dependency, dependencies))
                        & selected_values
                    )
                    if hidden_ancestors:
                        missing_bridges.append((value_id, dependency, hidden_ancestors))
            if missing_bridges:
                value_id, bridge_id, ancestors = missing_bridges[0]
                raise BriefError(
                    f"module {module_id!r} network selects transitive dependency pair(s) "
                    f"{ancestors} -> {value_id!r} but omits intermediate node {bridge_id!r}. "
                    "Include every dependency bridge needed by the visible claim, or remove the "
                    "transitive endpoints and choose a different asset"
                )
        radial = family == "gauge" and any(
            token in asset_type.lower() for token in ("radial", "dial", "gauge")
        )
        if radial:
            invalid_unit = next(
                (
                    value_id
                    for value_id in values
                    if units[value_id] not in {"fraction", "percent", "%"}
                ),
                None,
            )
            if invalid_unit is not None:
                raise BriefError(
                    f"module {module_id!r} uses a radial gauge for {invalid_unit!r} with unit "
                    f"{units[invalid_unit]!r}; generated radial gauges require a bounded "
                    "fraction or percentage-point value"
                )
            invalid_fraction = next(
                (
                    value_id
                    for value_id in values
                    if units[value_id] == "fraction"
                    and (intervals[value_id][0] < 0 or intervals[value_id][1] > 1)
                ),
                None,
            )
            if invalid_fraction is not None:
                low, high = intervals[invalid_fraction]
                raise BriefError(
                    f"module {module_id!r} uses a radial gauge for fraction {invalid_fraction!r} "
                    f"with legal envelope [{clean_number(low)}, {clean_number(high)}]; use a "
                    "bullet/progress asset with a 100% target or clamp the radial measure to [0, 1]"
                )
            invalid_percent = next(
                (
                    value_id
                    for value_id in values
                    if units[value_id] in {"percent", "%"}
                    and (intervals[value_id][0] < 0 or intervals[value_id][1] > 100)
                ),
                None,
            )
            if invalid_percent is not None:
                low, high = intervals[invalid_percent]
                raise BriefError(
                    f"module {module_id!r} uses a radial gauge for percentage-point value "
                    f"{invalid_percent!r} with legal envelope [{clean_number(low)}, "
                    f"{clean_number(high)}]; use a bullet/progress asset when the value can "
                    "exceed 100%"
                )
        stack_total = item.get("stackTotal")
        stack_rollups: set[str] = set()
        is_stack = family == "bar" and "stack" in asset_type
        if is_stack:
            selected_values = set(values)
            stack_rollups = {
                value_id
                for value_id in values
                if dependency_closure(value_id, dependencies) & (selected_values - {value_id})
            }
            if stack_total is None and stack_rollups:
                stack_total = max(
                    stack_rollups,
                    key=lambda value_id: (
                        len(dependency_closure(value_id, dependencies) & selected_values),
                        values.index(value_id),
                    ),
                )
            primitive_stack_parts = [
                value_id
                for value_id in values
                if value_id not in stack_rollups and value_id != stack_total
            ]
            negative_part = next(
                (
                    value_id
                    for value_id in primitive_stack_parts
                    if semantic_envelope(value_id)[0] < 0
                ),
                None,
            )
            if negative_part is not None:
                low, high = semantic_envelope(negative_part)
                raise BriefError(
                    f"module {module_id!r} stacked part {negative_part!r} has legal envelope "
                    f"[{clean_number(low)}, {clean_number(high)}]; generated stacks require "
                    "nonnegative mutually exclusive parts"
                )
        shared_stack_domain: tuple[float, float] | None = None
        if stack_total is not None:
            stack_total = require_id(stack_total, f"module {module_id!r} stackTotal")
            if family != "bar" or "stack" not in asset_type:
                raise BriefError(
                    f"module {module_id!r} stackTotal is valid only for a stacked bar asset"
                )
            if stack_total not in known_values:
                raise BriefError(
                    f"module {module_id!r} stackTotal references unknown value {stack_total!r}"
                )
            if is_stack:
                stack_units = {units[value_id] for value_id in values}
                stack_units.add(units[stack_total])
                if len(stack_units) != 1:
                    raise BriefError(
                        f"module {module_id!r} stacked parts and stackTotal must share one unit; "
                        f"found {sorted(stack_units)}"
                    )
            if semantic_envelope(stack_total)[0] < 0:
                low, high = semantic_envelope(stack_total)
                raise BriefError(
                    f"module {module_id!r} stackTotal {stack_total!r} has legal envelope "
                    f"[{clean_number(low)}, {clean_number(high)}]; generated stack totals must stay nonnegative"
                )
            # A part-to-whole stack is always measured from canonical zero,
            # even when the total's credible legal domain has a positive
            # lower bound. Reusing that lower bound would map zero outside
            # the visible range and force the composer to reject the plan.
            shared_stack_domain = (0.0, intervals[stack_total][1])
        shared_bar_domain: tuple[float, float] | None = None
        if family == "bar" and not is_stack:
            bar_units = {units[value_id] for value_id in values}
            if len(bar_units) != 1:
                raise BriefError(
                    f"module {module_id!r} comparative bars must share one unit; found "
                    f"{sorted(bar_units)}"
                )
            negative_value = next(
                (
                    value_id
                    for value_id in values
                    if semantic_envelope(value_id)[0] < 0
                ),
                None,
            )
            if negative_value is not None:
                low, high = semantic_envelope(negative_value)
                raise BriefError(
                    f"module {module_id!r} comparative bar value {negative_value!r} has legal envelope "
                    f"[{clean_number(low)}, {clean_number(high)}]; generated comparative bars require "
                    "nonnegative values on one zero baseline. Use a flow or table asset until an "
                    "explicit diverging-bar renderer is available"
                )
            shared_bar_domain = (
                0.0,
                max(1.0, *(semantic_envelope(value_id)[1] for value_id in values)),
            )
        waterfall_extent = None
        if family == "waterfall":
            if len(values) < 2:
                raise BriefError(
                    f"module {module_id!r} waterfall needs an opening total and ending balance"
                )
            waterfall_units = {units[value_id] for value_id in values}
            if len(waterfall_units) != 1:
                raise BriefError(
                    f"module {module_id!r} waterfall values must share one unit; found "
                    f"{sorted(waterfall_units)}"
                )
            for endpoint in (values[0], values[-1]):
                low, high = semantic_envelope(endpoint)
                if low < 0:
                    raise BriefError(
                        f"module {module_id!r} waterfall endpoint {endpoint!r} has legal envelope "
                        f"[{clean_number(low)}, {clean_number(high)}]; opening and ending totals must stay nonnegative"
                    )
            for deduction in values[1:-1]:
                low, high = semantic_envelope(deduction)
                if low < 0 and high > 0:
                    raise BriefError(
                        f"module {module_id!r} waterfall deduction {deduction!r} crosses zero over "
                        f"[{clean_number(low)}, {clean_number(high)}]; use a sign-stable deduction or another asset"
                    )
            waterfall_extent = max(
                1.0,
                *(
                    max(abs(float(intervals[value_id][0])), abs(float(intervals[value_id][1])))
                    for value_id in values
                ),
            )
        bindings: list[dict[str, Any]] = []
        for binding_index, value_id in enumerate(values):
            domain = shared_stack_domain or shared_bar_domain or intervals[value_id]
            if is_stack and (value_id in stack_rollups or value_id == stack_total):
                channel, transform = "text", None
            elif family == "waterfall" and waterfall_extent is not None:
                raw_low, raw_high = intervals[value_id]
                if raw_high <= 0:
                    transform = transform_for((-waterfall_extent, 0.0), [180, 0])
                else:
                    transform = transform_for((0.0, waterfall_extent), [0, 180])
                channel = "height"
            else:
                channel, transform = binding_channel(
                    family, asset_type, binding_index, value_id, units[value_id], domain
                )
            cue = cues[value_id]
            role = value_id if cue in value_id.split("-") else f"{value_id}-{cue}"
            if family == "flow" and channel == "text" and "residual" not in role.split("-"):
                role = f"{role}-residual"
            role = f"{role}-{channel}"
            binding: dict[str, Any] = {
                "selector": f"[data-role='{role}']",
                "value": value_id,
                "channel": channel,
                "label": labels[value_id],
                "format": value_format(units[value_id]),
            }
            if transform is not None:
                binding["transform"] = transform
            bindings.append(binding)
        if family == "gauge" and len(values) == 1:
            value_id = values[0]
            cue = cues[value_id]
            readout_role = value_id if cue in value_id.split("-") else f"{value_id}-{cue}"
            bindings.append(
                {
                    "selector": f"[data-role='{readout_role}-readout-text']",
                    "value": value_id,
                    "channel": "text",
                    "label": labels[value_id],
                    "format": value_format(units[value_id]),
                }
            )
        compiled_module = {
                "id": module_id,
                "assetType": asset_type,
                "question": require_text(item.get("question"), f"module {module_id!r} question"),
                "claim": require_text(item.get("claim"), f"module {module_id!r} claim"),
                "navigationLabel": (
                    require_text(item.get("navigationLabel"), f"module {module_id!r} navigationLabel")
                    if item.get("navigationLabel") is not None
                    else module_id.replace("-", " ").title()
                ),
                "selectionRationale": require_text(
                    item.get("selectionRationale"),
                    f"module {module_id!r} selectionRationale",
                ),
                "rejectedAlternative": require_text(
                    item.get("rejectedAlternative"),
                    f"module {module_id!r} rejectedAlternative",
                ),
                # Top-level focusGroups is the sole authoring authority. The compiler
                # fills this derived field after all groups have been validated.
                "focusGroups": [],
                "bindings": bindings,
                "_heavy": family in {"flow", "network", "spatial"} or (family == "table" and len(values) > 4),
            }
        if stack_total is not None:
            compiled_module["stackTotal"] = stack_total
        if structural_diagram is not None:
            compiled_module["diagram"] = structural_diagram
        result.append(compiled_module)
    return result


def row_regions(
    y: float,
    height: float,
    count: int,
    *,
    asymmetric: bool,
    safe_area: list[int],
    weights: list[float] | None = None,
) -> list[list[int | float]]:
    _, _, safe_width, _ = safe_area
    available = safe_width - GAP * (count - 1)
    effective_weights = list(weights) if weights is not None else [1.0] * count
    if len(effective_weights) != count or any(weight <= 0 for weight in effective_weights):
        raise BriefError("layout row weights must be positive and match the row size")
    if weights is None and asymmetric and count >= 2:
        effective_weights[0] = 2.0
    unit = available / sum(effective_weights)
    regions: list[list[int | float]] = []
    cursor = float(safe_area[0])
    for index, weight in enumerate(effective_weights):
        x_value = round(cursor, 6)
        width = round(unit * weight, 6)
        if index == count - 1:
            width = round(safe_area[0] + safe_width - x_value, 6)
        regions.append(
            [clean_number(x_value), clean_number(round(y, 6)), clean_number(width), clean_number(round(height, 6))]
        )
        cursor = x_value + width + GAP
    return regions


def assign_layout(modules: list[dict[str, Any]], safe_area: list[int]) -> list[str]:
    count = len(modules)
    if count <= 6:
        row_counts = [3, count - 3]
    elif count == 7:
        row_counts = [3, 4]
    elif count == 8:
        row_counts = [4, 4]
    elif count <= 12:
        base, remainder = divmod(count, 3)
        row_counts = [base + (1 if index < remainder else 0) for index in range(3)]
    else:
        base, remainder = divmod(count, 4)
        row_counts = [base + (1 if index < remainder else 0) for index in range(4)]
    row_count = len(row_counts)
    row_height = (safe_area[3] - GAP * (row_count - 1)) / row_count
    slots: list[list[int | float]] = []
    y = float(safe_area[1])
    module_offset = 0
    for row_index, item_count in enumerate(row_counts):
        row_modules = modules[module_offset : module_offset + item_count]
        if count > 12:
            row_weights = [1.0] * item_count
        else:
            row_weights = [1.6 if module.get("_heavy") else 1.0 for module in row_modules]
            if row_index == 0 and item_count >= 2 and all(weight == 1.0 for weight in row_weights):
                row_weights[0] = 1.6
        slots.extend(
            row_regions(
                y,
                row_height,
                item_count,
                asymmetric=False,
                safe_area=safe_area,
                weights=row_weights,
            )
        )
        y += row_height + GAP
        module_offset += item_count

    for module, region in zip(modules, slots, strict=True):
        module.pop("_heavy")
        module["region"] = region
    return [module["id"] for module in modules]


def bounds_for_regions(regions: list[list[float]], padding: float = 0.0) -> list[float]:
    left = min(region[0] for region in regions) - padding
    top = min(region[1] for region in regions) - padding
    right = max(region[0] + region[2] for region in regions) + padding
    bottom = max(region[1] + region[3] for region in regions) + padding
    return [left, top, right - left, bottom - top]


def world_module_size(module: dict[str, Any]) -> tuple[float, float]:
    if module.get("_heavy"):
        return float(WORLD_HEAVY_MODULE_WIDTH), float(WORLD_HEAVY_MODULE_HEIGHT)
    return float(WORLD_MODULE_WIDTH), float(WORLD_MODULE_HEIGHT)


def local_district_regions(
    modules: list[dict[str, Any]],
    armature: str,
) -> tuple[dict[str, list[float]], list[float]]:
    """Place local diagrams around one district hub before global projection."""

    if armature not in {"radial", "branch", "lanes", "orbit"}:
        raise BriefError(
            f"district localArmature {armature!r} must be radial, branch, lanes, or orbit"
        )
    count = len(modules)
    if not 1 <= count <= 8:
        raise BriefError("each world district must contain 1 to 8 local diagram modules")
    sizes = [world_module_size(module) for module in modules]
    centers: list[tuple[float, float]] = []
    if count == 1:
        centers = [(0.0, 0.0)]
    elif armature == "radial":
        centers.append((0.0, 0.0))
        orbit_count = count - 1
        radius_x = max(960.0, 285.0 * orbit_count)
        radius_y = max(720.0, 210.0 * orbit_count)
        for index in range(orbit_count):
            angle = -math.pi / 2 + 2 * math.pi * index / orbit_count
            centers.append((radius_x * math.cos(angle), radius_y * math.sin(angle)))
    elif armature == "orbit":
        radius_x = max(1000.0, 245.0 * count)
        radius_y = max(760.0, 185.0 * count)
        for index in range(count):
            angle = -math.pi / 2 + 2 * math.pi * index / count
            centers.append((radius_x * math.cos(angle), radius_y * math.sin(angle)))
    elif armature == "branch":
        centers.append((-980.0, 0.0))
        remaining = count - 1
        columns = 2 if remaining > 3 else 1
        rows = math.ceil(remaining / columns)
        for index in range(remaining):
            column = index // rows
            row = index % rows
            x = 180.0 + column * 900.0
            y = (row - (rows - 1) / 2) * 660.0
            centers.append((x, y))
    else:
        columns = min(3, max(2, math.ceil(math.sqrt(count))))
        rows = math.ceil(count / columns)
        for index in range(count):
            column = index % columns
            row = index // columns
            x = (column - (columns - 1) / 2) * 860.0
            y = (row - (rows - 1) / 2) * 640.0
            centers.append((x, y))
    regions: dict[str, list[float]] = {}
    for module, (width, height), (center_x, center_y) in zip(
        modules, sizes, centers, strict=True
    ):
        regions[module["id"]] = [
            center_x - width / 2,
            center_y - height / 2,
            width,
            height,
        ]
    bounds = bounds_for_regions(list(regions.values()), padding=220.0)
    return regions, bounds


def compile_world_links(
    raw: Any,
    district_ids: set[str],
) -> list[dict[str, Any]]:
    if not isinstance(raw, list) or not raw:
        raise BriefError("world.links must be a non-empty array")
    if len(raw) > 28:
        raise BriefError("world.links supports at most 28 explanatory district routes")
    result: list[dict[str, Any]] = []
    seen: set[str] = set()
    seen_edges: set[tuple[str, str, str]] = set()
    for index, item in enumerate(raw):
        if not isinstance(item, dict):
            raise BriefError(f"world.links[{index}] must be an object")
        link_id = require_id(item.get("id"), f"world.links[{index}].id")
        if link_id in seen:
            raise BriefError(f"duplicate world link id: {link_id}")
        seen.add(link_id)
        source = require_id(item.get("source"), f"world link {link_id!r} source")
        target = require_id(item.get("target"), f"world link {link_id!r} target")
        if source == target or source not in district_ids or target not in district_ids:
            raise BriefError(
                f"world link {link_id!r} must connect two distinct declared districts"
            )
        kind = item.get("kind", "dependency")
        if kind not in {"flow", "dependency", "feedback"}:
            raise BriefError(
                f"world link {link_id!r} kind must be flow, dependency, or feedback"
            )
        edge = (source, target, str(kind))
        if edge in seen_edges:
            raise BriefError(
                f"duplicate world link endpoints and kind: {source!r} -> {target!r} ({kind})"
            )
        seen_edges.add(edge)
        result.append(
            {
                "id": link_id,
                "source": source,
                "target": target,
                "kind": kind,
                "label": require_text(item.get("label"), f"world link {link_id!r} label"),
            }
        )
    return result


def district_depths(
    root_id: str,
    district_ids: set[str],
    links: list[dict[str, Any]],
) -> dict[str, int]:
    outgoing: dict[str, list[str]] = {district_id: [] for district_id in district_ids}
    for link in links:
        if link["kind"] != "feedback":
            outgoing[link["source"]].append(link["target"])
    depths = {root_id: 0}
    pending = [root_id]
    while pending:
        source = pending.pop(0)
        for target in outgoing[source]:
            candidate = depths[source] + 1
            if target not in depths or candidate < depths[target]:
                depths[target] = candidate
                pending.append(target)
    missing = sorted(district_ids - set(depths))
    if missing:
        raise BriefError(
            "every world district must be reachable from rootDistrictId through a directed "
            f"non-feedback link; unreachable district(s): {missing}"
        )
    return depths


def assign_world_tree_roles(
    root_id: str,
    district_ids: set[str],
    links: list[dict[str, Any]],
) -> None:
    """Mark one readable spanning-tree trunk per non-root district."""

    outgoing: dict[str, list[dict[str, Any]]] = {
        district_id: [] for district_id in district_ids
    }
    for link in links:
        link["treeRole"] = "feedback" if link["kind"] == "feedback" else "crosslink"
        if link["kind"] != "feedback":
            outgoing[link["source"]].append(link)
    reached = {root_id}
    pending = [root_id]
    while pending:
        source = pending.pop(0)
        for link in outgoing[source]:
            target = link["target"]
            if target in reached:
                continue
            link["treeRole"] = "trunk"
            reached.add(target)
            pending.append(target)
    missing = sorted(district_ids - reached)
    if missing:  # district_depths normally reports this first; retain a local invariant.
        raise BriefError(f"world spanning tree cannot reach district(s): {missing}")


def radial_district_centers(
    districts: list[dict[str, Any]],
    depths: dict[str, int],
    links: list[dict[str, Any]],
) -> dict[str, tuple[float, float]]:
    """Place one semantic root at center and all other districts on a readable ring.

    Causal depth remains metadata and link meaning. Projecting every causal depth
    onto a new radius creates an enormous sparse spiral for long systems, which
    defeats the explorable-world overview.
    """

    centers: dict[str, tuple[float, float]] = {}
    root_id = next(item["id"] for item in districts if depths[item["id"]] == 0)
    centers[root_id] = (0.0, 0.0)
    ring_by_id = {district["id"]: district for district in districts if district["id"] != root_id}
    declaration_order = list(ring_by_id)
    adjacency: dict[str, list[str]] = {district_id: [] for district_id in declaration_order}
    root_children: list[str] = []
    for link in links:
        if link.get("treeRole") != "trunk":
            continue
        source = str(link["source"])
        target = str(link["target"])
        if source == root_id:
            root_children.append(target)
        elif source in adjacency and target in adjacency:
            adjacency[source].append(target)
            adjacency[target].append(source)

    ordered_ids: list[str] = []
    remaining = set(declaration_order)
    if all(len(neighbors) <= 2 for neighbors in adjacency.values()):
        while remaining:
            endpoints = [
                district_id
                for district_id in declaration_order
                if district_id in remaining
                and len([item for item in adjacency[district_id] if item in remaining]) <= 1
            ]
            current = endpoints[0] if endpoints else next(
                district_id for district_id in declaration_order if district_id in remaining
            )
            previous: str | None = None
            while current in remaining:
                ordered_ids.append(current)
                remaining.remove(current)
                candidates = [
                    item for item in adjacency[current] if item in remaining and item != previous
                ]
                if not candidates:
                    break
                previous, current = current, candidates[0]
    else:
        children: dict[str, list[str]] = {district_id: [] for district_id in [root_id, *declaration_order]}
        for link in links:
            if link.get("treeRole") == "trunk":
                children[str(link["source"])].append(str(link["target"]))

        def visit(district_id: str) -> None:
            if district_id in ring_by_id and district_id not in ordered_ids:
                ordered_ids.append(district_id)
            for child_id in children.get(district_id, []):
                visit(child_id)

        visit(root_id)
        ordered_ids.extend(item for item in declaration_order if item not in ordered_ids)

    first_root_child = next((item for item in root_children if item in ordered_ids), None)
    if first_root_child is not None:
        pivot = ordered_ids.index(first_root_child)
        ordered_ids = ordered_ids[pivot:] + ordered_ids[:pivot]
    ring = [ring_by_id[district_id] for district_id in ordered_ids]
    maximum_extent = max(
        max(float(item["_localBounds"][2]), float(item["_localBounds"][3]))
        for item in districts
    )
    count = len(ring)
    circumference_radius = (
        (maximum_extent + WORLD_DISTRICT_GAP) * max(1, count) / (2 * math.pi)
    )
    radius = max(4300.0, circumference_radius)
    for index, district in enumerate(ring):
        angle = -math.pi / 2 + 2 * math.pi * index / max(1, count)
        centers[district["id"]] = (
            radius * math.cos(angle),
            radius * 0.78 * math.sin(angle),
        )
    if root_id not in centers:  # pragma: no cover - defensive clarity
        raise BriefError("world root district could not be positioned")
    return centers


def genealogical_district_centers(
    districts: list[dict[str, Any]],
    depths: dict[str, int],
) -> dict[str, tuple[float, float]]:
    by_depth: dict[int, list[dict[str, Any]]] = {}
    for district in districts:
        by_depth.setdefault(depths[district["id"]], []).append(district)
    maximum_width = max(float(item["_localBounds"][2]) for item in districts)
    maximum_height = max(float(item["_localBounds"][3]) for item in districts)
    maximum_rows = max(len(items) for items in by_depth.values())
    centers: dict[str, tuple[float, float]] = {}
    for depth, level in sorted(by_depth.items()):
        for index, district in enumerate(level):
            centers[district["id"]] = (
                depth * (maximum_width + WORLD_DISTRICT_GAP),
                (index - (len(level) - 1) / 2) * (maximum_height + WORLD_DISTRICT_GAP),
            )
    if maximum_rows == 1:
        return centers
    return centers


def clean_rect(value: list[float]) -> list[int | float]:
    return [clean_number(round(item, 6)) for item in value]


def target_anchor_id(target: str, district_ids: set[str], module_ids: set[str]) -> str:
    if target == "world":
        return "world"
    if target in district_ids:
        return f"district-{target}"
    if target in module_ids:
        return f"module-{target}"
    if target.startswith("district-") and target.removeprefix("district-") in district_ids:
        return target
    if target.startswith("module-") and target.removeprefix("module-") in module_ids:
        return target
    raise BriefError(f"navigation target {target!r} is not world, a district, or a module")


def compile_navigation(
    raw: Any,
    *,
    view_box: list[int],
    world_bounds: list[float],
    districts: list[dict[str, Any]],
    modules: list[dict[str, Any]],
    focus_ids: set[str],
    root_district_id: str,
) -> dict[str, Any]:
    if not isinstance(raw, dict):
        raise BriefError("world.navigation must be an object")
    district_ids = {item["id"] for item in districts}
    module_ids = {item["id"] for item in modules}
    viewport = list(WORLD_NAVIGATION_VIEWPORT)
    aspect = float(viewport[2]) / float(viewport[3])
    anchors: list[dict[str, Any]] = [
        {
            "id": "world",
            "label": "Whole atlas",
            "kind": "world",
            "targetId": "world",
            "parentId": None,
            "depth": 0,
            "zoomTier": "world",
            "moduleIds": [module["id"] for module in modules],
            "requiredForTour": True,
            "viewBox": clean_rect(world_bounds),
        }
    ]
    district_cameras = {
        district["id"]: navigation.fit_aspect(
            [float(item) for item in district["bounds"]],
            aspect,
            padding=140.0,
            bounds=world_bounds,
        )
        for district in districts
    }
    peer_groups: dict[int, list[dict[str, Any]]] = {}
    for district in districts:
        if district["id"] != root_district_id:
            peer_groups.setdefault(len(district["moduleIds"]), []).append(district)
    for peer_districts in peer_groups.values():
        peer_width = max(float(district_cameras[item["id"]][2]) for item in peer_districts)
        peer_height = peer_width / aspect
        for district in peer_districts:
            camera = district_cameras[district["id"]]
            center_x = float(camera[0]) + float(camera[2]) / 2
            center_y = float(camera[1]) + float(camera[3]) / 2
            district_cameras[district["id"]] = navigation.fit_aspect(
                [center_x - peer_width / 2, center_y - peer_height / 2, peer_width, peer_height],
                aspect,
                bounds=world_bounds,
            )
    for district in districts:
        camera = district_cameras[district["id"]]
        anchors.append(
            {
                "id": f"district-{district['id']}",
                "label": district["label"],
                "kind": "district",
                "targetId": district["id"],
                "parentId": "world",
                "depth": 1,
                "zoomTier": "district",
                "moduleIds": list(district["moduleIds"]),
                "requiredForTour": bool(district.get("requiredForTour", True)),
                "viewBox": clean_rect(camera),
            }
        )
    district_by_module = {
        module_id: district["id"]
        for district in districts
        for module_id in district["moduleIds"]
    }
    for module in modules:
        camera = navigation.fit_aspect(
            [float(item) for item in module["region"]],
            aspect,
            padding=90.0,
            bounds=world_bounds,
        )
        anchors.append(
            {
                "id": f"module-{module['id']}",
                "label": module["navigationLabel"],
                "kind": "module",
                "targetId": module["id"],
                "parentId": f"district-{district_by_module[module['id']]}",
                "depth": 2,
                "zoomTier": "module",
                "moduleIds": [module["id"]],
                "requiredForTour": False,
                "viewBox": clean_rect(camera),
            }
        )
    initial_target = require_id(raw.get("initialTarget", "world"), "world.navigation.initialTarget")
    initial_anchor = target_anchor_id(initial_target, district_ids, module_ids)
    route_raw = raw.get("route")
    if not isinstance(route_raw, dict):
        raise BriefError("world.navigation.route must be an object")
    stops_raw = route_raw.get("stops")
    if not isinstance(stops_raw, list) or not stops_raw:
        raise BriefError("world.navigation.route.stops must be a non-empty array")
    stops: list[dict[str, Any]] = []
    seen_stops: set[str] = set()
    cursor = 0.0
    previous_anchor = initial_anchor
    for index, stop in enumerate(stops_raw):
        if not isinstance(stop, dict):
            raise BriefError(f"world.navigation.route.stops[{index}] must be an object")
        stop_id = require_id(stop.get("id"), f"world navigation stop {index} id")
        if stop_id in seen_stops:
            raise BriefError(f"duplicate world navigation stop id: {stop_id}")
        seen_stops.add(stop_id)
        target = require_id(stop.get("target"), f"world navigation stop {stop_id!r} target")
        anchor_id = target_anchor_id(target, district_ids, module_ids)
        travel = finite_number(
            stop.get("travelMs", 0 if index == 0 else 1600),
            f"world navigation stop {stop_id!r} travelMs",
        )
        hold = finite_number(
            stop.get("holdMs", 2400),
            f"world navigation stop {stop_id!r} holdMs",
        )
        if travel < 0 or hold <= 0:
            raise BriefError(
                f"world navigation stop {stop_id!r} needs nonnegative travelMs and positive holdMs"
            )
        focus_id = stop.get("focusId")
        if focus_id is not None and focus_id not in focus_ids:
            raise BriefError(
                f"world navigation stop {stop_id!r} references unknown focus group {focus_id!r}"
            )
        arrival = cursor + travel
        end = arrival + hold
        compiled_stop: dict[str, Any] = {
            "id": stop_id,
            "label": require_text(
                stop.get("label", stop_id.replace("-", " ").title()),
                f"world navigation stop {stop_id!r} label",
            ),
            "fromAnchorId": previous_anchor,
            "anchorId": anchor_id,
            "startMs": clean_number(cursor),
            "arrivalMs": clean_number(arrival),
            "endMs": clean_number(end),
            "travelMs": clean_number(travel),
            "holdMs": clean_number(hold),
        }
        if focus_id is not None:
            compiled_stop["focusId"] = focus_id
        if stop.get("handoff") is not None:
            compiled_stop["handoff"] = require_text(
                stop.get("handoff"), f"world navigation stop {stop_id!r} handoff"
            )
        stops.append(compiled_stop)
        cursor = end
        previous_anchor = anchor_id
    loop = route_raw.get("loop", False)
    autoplay = route_raw.get("autoplay", False)
    if not isinstance(loop, bool) or not isinstance(autoplay, bool):
        raise BriefError("world.navigation.route loop and autoplay must be booleans")
    if loop and stops[-1]["anchorId"] != initial_anchor:
        raise BriefError(
            "a looping world navigation route must end at its initial anchor for a clean seam"
        )
    return {
        "version": 1,
        "viewport": viewport,
        "worldBounds": clean_rect(world_bounds),
        "initialAnchorId": initial_anchor,
        "anchors": anchors,
        "semanticZoom": [
            {"id": "world", "maximumWidthRatio": 1.0},
            {"id": "district", "maximumWidthRatio": 0.42},
            {"id": "module", "maximumWidthRatio": 0.16},
        ],
        "route": {
            "durationMs": clean_number(cursor),
            "loop": loop,
            "autoplay": autoplay,
            "stops": stops,
        },
    }


def compile_world_layout(
    raw: Any,
    modules: list[dict[str, Any]],
    focus_ids: set[str],
) -> tuple[
    dict[str, Any],
    dict[str, Any],
    list[int],
    list[int | float],
    list[str],
]:
    if not isinstance(raw, dict):
        raise BriefError("world must be an object")
    mode = raw.get("mode", "navigable-atlas")
    if mode != "navigable-atlas":
        raise BriefError("world.mode must equal navigable-atlas")
    armature = require_id(raw.get("armature"), "world.armature")
    if armature not in {"radial-skill-tree", "genealogical-tree", "constellation-map"}:
        raise BriefError(
            "world.armature must be radial-skill-tree, genealogical-tree, or constellation-map"
        )
    districts_raw = raw.get("districts")
    if not isinstance(districts_raw, list) or not 4 <= len(districts_raw) <= 12:
        raise BriefError("world.districts must contain 4 to 12 districts")
    module_by_id = {module["id"]: module for module in modules}
    module_ids = set(module_by_id)
    districts: list[dict[str, Any]] = []
    district_ids: set[str] = set()
    covered_modules: set[str] = set()
    for index, item in enumerate(districts_raw):
        if not isinstance(item, dict):
            raise BriefError(f"world.districts[{index}] must be an object")
        district_id = require_id(item.get("id"), f"world.districts[{index}].id")
        if district_id in district_ids or district_id in module_ids:
            raise BriefError(
                f"world district id {district_id!r} must be unique and distinct from module ids"
            )
        district_ids.add(district_id)
        assigned = item.get("moduleIds")
        if (
            not isinstance(assigned, list)
            or not assigned
            or any(not isinstance(module_id, str) for module_id in assigned)
            or len(assigned) != len(set(assigned))
        ):
            raise BriefError(
                f"world district {district_id!r} moduleIds must be a non-empty unique list"
            )
        unknown = set(assigned) - module_ids
        repeated = set(assigned) & covered_modules
        if unknown or repeated:
            raise BriefError(
                f"world district {district_id!r} module assignment is invalid; "
                f"unknown={sorted(unknown)}, repeated={sorted(repeated)}"
            )
        covered_modules.update(assigned)
        local_armature = item.get("localArmature", "radial")
        local_modules = [module_by_id[module_id] for module_id in assigned]
        local_regions, local_bounds = local_district_regions(local_modules, str(local_armature))
        districts.append(
            {
                "id": district_id,
                "label": require_text(item.get("label"), f"world district {district_id!r} label"),
                "summary": require_text(
                    item.get("summary"), f"world district {district_id!r} summary"
                ),
                "role": require_text(
                    item.get("role", "Linked local diagrams"),
                    f"world district {district_id!r} role",
                ),
                "localArmature": local_armature,
                "moduleIds": list(assigned),
                "requiredForTour": bool(item.get("requiredForTour", True)),
                "accent": WORLD_DISTRICT_PALETTE[index % len(WORLD_DISTRICT_PALETTE)],
                "_localRegions": local_regions,
                "_localBounds": local_bounds,
            }
        )
    if covered_modules != module_ids:
        raise BriefError(
            "world districts must assign every module exactly once; "
            f"unassigned module(s): {sorted(module_ids - covered_modules)}"
        )
    root_id = require_id(raw.get("rootDistrictId"), "world.rootDistrictId")
    if root_id not in district_ids:
        raise BriefError("world.rootDistrictId must name a declared district")
    links = compile_world_links(raw.get("links"), district_ids)
    depths = district_depths(root_id, district_ids, links)
    assign_world_tree_roles(root_id, district_ids, links)
    if armature == "genealogical-tree":
        centers = genealogical_district_centers(districts, depths)
    else:
        centers = radial_district_centers(districts, depths, links)
    projected_regions: list[list[float]] = []
    for district in districts:
        center_x, center_y = centers[district["id"]]
        local_bounds = district["_localBounds"]
        offset_x = center_x - (local_bounds[0] + local_bounds[2] / 2)
        offset_y = center_y - (local_bounds[1] + local_bounds[3] / 2)
        district_regions: list[list[float]] = []
        for module_id in district["moduleIds"]:
            local = district["_localRegions"][module_id]
            projected = [local[0] + offset_x, local[1] + offset_y, local[2], local[3]]
            module = module_by_id[module_id]
            module.pop("_heavy", None)
            module["region"] = projected
            module["districtId"] = district["id"]
            module["districtAccent"] = district["accent"]
            district_regions.append(projected)
            projected_regions.append(projected)
        district["bounds"] = bounds_for_regions(district_regions, padding=210.0)
        district["center"] = [center_x, center_y]
    content_bounds = bounds_for_regions(
        [district["bounds"] for district in districts], padding=float(WORLD_MARGIN)
    )
    world_width = content_bounds[2]
    world_height = content_bounds[3]
    if world_width / world_height < WORLD_ASPECT_RATIO:
        world_width = world_height * WORLD_ASPECT_RATIO
    else:
        world_height = world_width / WORLD_ASPECT_RATIO
    shift_x = -content_bounds[0] + (world_width - content_bounds[2]) / 2
    shift_y = -content_bounds[1] + (world_height - content_bounds[3]) / 2
    for module in modules:
        module["region"][0] += shift_x
        module["region"][1] += shift_y
        module["region"] = clean_rect(module["region"])
    for district in districts:
        district["bounds"][0] += shift_x
        district["bounds"][1] += shift_y
        district["center"][0] += shift_x
        district["center"][1] += shift_y
        district["bounds"] = clean_rect(district["bounds"])
        district["center"] = [clean_number(round(item, 6)) for item in district["center"]]
        district.pop("_localRegions", None)
        district.pop("_localBounds", None)
    world_height_units = max(9, math.ceil(world_height / 9.0) * 9)
    world_width_units = world_height_units * 16 // 9
    world_bounds = [0.0, 0.0, float(world_width_units), float(world_height_units)]
    view_box = [0, 0, 1920, 1080]
    navigation_plan = compile_navigation(
        raw.get("navigation"),
        view_box=view_box,
        world_bounds=world_bounds,
        districts=districts,
        modules=modules,
        focus_ids=focus_ids,
        root_district_id=root_id,
    )
    world_plan = {
        "mode": mode,
        "armature": armature,
        "rootDistrictId": root_id,
        "bounds": clean_rect(world_bounds),
        "districts": districts,
        "links": links,
    }
    reading_order = [
        module_id
        for district in districts
        for module_id in district["moduleIds"]
    ]
    navigation.validate_navigation(
        {
            "navigation": navigation_plan,
            "modules": modules,
        }
    )
    return world_plan, navigation_plan, view_box, clean_rect(world_bounds), reading_order


def compile_focus_groups(raw: Any, module_ids: set[str]) -> list[dict[str, Any]]:
    if raw is None:
        return []
    if not isinstance(raw, list):
        raise BriefError("focusGroups must be an array")
    result: list[dict[str, Any]] = []
    seen: set[str] = set()
    for index, item in enumerate(raw):
        if not isinstance(item, dict):
            raise BriefError(f"focusGroups[{index}] must be an object")
        focus_id = require_id(item.get("id"), f"focusGroups[{index}].id")
        if focus_id in seen:
            raise BriefError(f"duplicate focus group id: {focus_id}")
        seen.add(focus_id)
        values = item.get("moduleIds")
        if (
            not isinstance(values, list)
            or not values
            or any(not isinstance(module_id, str) for module_id in values)
            or len(values) != len(set(values))
        ):
            raise BriefError(f"focus group {focus_id!r} moduleIds must be a non-empty unique list")
        if not set(values) <= module_ids:
            raise BriefError(f"focus group {focus_id!r} references unknown modules")
        result.append(
            {
                "id": focus_id,
                "label": require_text(
                    item.get("label", focus_id.replace("-", " ").title()),
                    f"focus group {focus_id!r} label",
                ),
                "moduleIds": list(values),
            }
        )
    return result


def compile_relationships(raw: Any, module_ids: set[str]) -> list[dict[str, Any]]:
    if raw is None:
        return []
    if not isinstance(raw, list):
        raise BriefError("relationships must be an array")
    result: list[dict[str, Any]] = []
    seen: set[str] = set()
    seen_edges: set[tuple[str, str, str]] = set()
    for index, item in enumerate(raw):
        if not isinstance(item, dict):
            raise BriefError(f"relationships[{index}] must be an object")
        relationship_id = require_id(item.get("id"), f"relationships[{index}].id")
        if relationship_id in seen:
            raise BriefError(f"duplicate relationship id: {relationship_id}")
        seen.add(relationship_id)
        source = require_id(item.get("source"), f"relationship {relationship_id!r} source")
        target = require_id(item.get("target"), f"relationship {relationship_id!r} target")
        if source not in module_ids or target not in module_ids or source == target:
            raise BriefError(
                f"relationship {relationship_id!r} must connect two distinct declared modules"
            )
        kind = item.get("kind", "flow")
        if kind not in {"flow", "dependency", "feedback"}:
            raise BriefError(
                f"relationship {relationship_id!r} kind must be flow, dependency, or feedback"
            )
        edge_key = (source, target, kind)
        if edge_key in seen_edges:
            raise BriefError(
                f"duplicate relationship endpoints and kind: {source!r} -> {target!r} ({kind})"
            )
        seen_edges.add(edge_key)
        result.append(
            {
                "id": relationship_id,
                "source": source,
                "target": target,
                "kind": kind,
                "label": require_text(item.get("label"), f"relationship {relationship_id!r} label"),
            }
        )
    return result


def compile_timeline(
    raw: Any,
    focus_ids: set[str],
    source_domains: dict[str, tuple[float, float]],
    scenario_ids: set[str],
) -> dict[str, Any] | None:
    if raw is None:
        return None
    if not isinstance(raw, dict):
        raise BriefError("timeline must be an object")
    phases = raw.get("phases")
    if not isinstance(phases, list) or not phases:
        raise BriefError("timeline phases must be a non-empty array")
    duration = finite_number(raw.get("durationMs", len(phases) * 3000), "timeline.durationMs")
    if duration <= 0:
        raise BriefError("timeline.durationMs must be positive")
    explicit = all(
        isinstance(phase, dict) and "startMs" in phase and "endMs" in phase for phase in phases
    )
    result: list[dict[str, Any]] = []
    cursor = 0.0
    phase_ids: set[str] = set()
    for index, phase in enumerate(phases):
        if not isinstance(phase, dict):
            raise BriefError(f"timeline.phases[{index}] must be an object")
        phase_id = require_id(phase.get("id"), f"timeline.phases[{index}].id")
        if phase_id in phase_ids:
            raise BriefError(f"duplicate timeline phase id: {phase_id}")
        phase_ids.add(phase_id)
        if explicit:
            start = finite_number(phase.get("startMs"), f"timeline phase {phase_id!r} startMs")
            end = finite_number(phase.get("endMs"), f"timeline phase {phase_id!r} endMs")
            if start != cursor or end <= start:
                raise BriefError(f"timeline phase {phase_id!r} must be ordered and contiguous")
        else:
            start = duration * index / len(phases)
            end = duration * (index + 1) / len(phases)
        focus_id = phase.get("focusId")
        if focus_id is not None and (
            not isinstance(focus_id, str) or focus_id not in focus_ids
        ):
            raise BriefError(f"timeline phase {phase_id!r} references unknown focus group")
        values = phase.get("values", {})
        if not isinstance(values, dict) or not set(values) <= set(source_domains):
            raise BriefError(f"timeline phase {phase_id!r} values must contain source concepts only")
        compiled_values: dict[str, int | float] = {}
        for value_id, raw_value in sorted(values.items()):
            value = finite_number(raw_value, f"timeline phase {phase_id!r} value {value_id!r}")
            low, high = source_domains[value_id]
            if not low <= value <= high:
                raise BriefError(
                    f"timeline phase {phase_id!r} value {value_id!r} is outside its legal domain"
                )
            compiled_values[value_id] = clean_number(value)
        compiled: dict[str, Any] = {
            "id": phase_id,
            "label": require_text(
                phase.get("label", phase_id.replace("-", " ").title()),
                f"timeline phase {phase_id!r} label",
            ),
            "startMs": clean_number(start),
            "endMs": clean_number(end),
            "values": compiled_values,
        }
        if focus_id is not None:
            compiled["focusId"] = focus_id
        result.append(compiled)
        cursor = end
    if explicit and cursor != duration:
        raise BriefError("timeline phases must cover durationMs exactly")
    loop = raw.get("loop", True)
    if not isinstance(loop, bool):
        raise BriefError("timeline.loop must be a boolean")
    interpolation = raw.get("interpolation", "step")
    if interpolation not in {"step", "linear", "smooth"}:
        raise BriefError("timeline.interpolation must be step, linear, or smooth")
    autoplay = raw.get("autoplay", False)
    if not isinstance(autoplay, bool):
        raise BriefError("timeline.autoplay must be a boolean")
    base_scenario = raw.get("baseScenario")
    if base_scenario is not None and (
        not isinstance(base_scenario, str) or base_scenario not in scenario_ids
    ):
        raise BriefError("timeline.baseScenario must name a declared scenario")
    compiled_timeline: dict[str, Any] = {
        "durationMs": clean_number(duration),
        "loop": loop,
        "interpolation": interpolation,
        "autoplay": autoplay,
        "phases": result,
    }
    if base_scenario is not None:
        compiled_timeline["baseScenario"] = base_scenario
    return compiled_timeline


def compile_brief(brief: dict[str, Any]) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    composition_id = require_id(brief.get("compositionId"), "compositionId")
    title = require_text(brief.get("title"), "title")
    provenance = require_text(brief.get("provenance"), "provenance")
    concepts = compile_concepts(copy.deepcopy(brief.get("concepts")))
    source_ids = {item["id"] for item in concepts}
    derived = compile_derived(brief.get("derived", []), source_ids)
    scenarios_raw = brief.get("scenarios")
    if not isinstance(scenarios_raw, list) or not scenarios_raw:
        raise BriefError("scenarios must be a non-empty array")
    normalizations = normalize_divisor_domains(
        concepts,
        derived,
        scenarios_raw,
        brief.get("timeline"),
    )
    scenarios = compile_scenarios(scenarios_raw, concepts)
    initial_scenario = brief.get("initialScenario", scenarios[0]["id"])
    if initial_scenario not in {item["id"] for item in scenarios}:
        raise BriefError("initialScenario must name a declared scenario")
    intervals = value_intervals(concepts, derived)
    value_ids = [item["id"] for item in concepts] + [item["id"] for item in derived]
    cues = unique_cues(value_ids)
    labels = {item["id"]: item["label"] for item in [*concepts, *derived]}
    units = {item["id"]: item["unit"] for item in [*concepts, *derived]}
    dependencies = {
        item["id"]: set(item.get("dependsOn", []))
        for item in [*concepts, *derived]
    }
    computations = {item["id"]: item["compute"] for item in derived}
    value_states = sampled_value_states(concepts, derived, scenarios)
    for value_id in value_ids:
        semantic_words = set(value_id.split("-")) | set(labels[value_id].lower().replace("/", " ").split())
        low, high = intervals[value_id]
        if units[value_id] == "fraction" and "utilization" in semantic_words and (
            low < 0 or high > 1
        ):
            raise BriefError(
                f"value {value_id!r} is named utilization but its legal envelope is "
                f"[{clean_number(low)}, {clean_number(high)}]; clamp it to [0, 1] or rename it "
                "as demand-to-capacity/load ratio so overload above 100% is not mislabeled"
            )
    module_raw = brief.get("modules")
    if not isinstance(module_raw, list):
        raise BriefError("modules must be an array")
    raw_module_ids = {
        require_id(item.get("id"), f"modules[{index}].id")
        for index, item in enumerate(module_raw)
        if isinstance(item, dict)
    }
    if len(raw_module_ids) != len(module_raw):
        raise BriefError("every module must be an object with a unique id")
    focus_groups = compile_focus_groups(brief.get("focusGroups", []), raw_module_ids)
    relationships = compile_relationships(brief.get("relationships", []), raw_module_ids)
    focus_ids = {item["id"] for item in focus_groups}
    world_raw = brief.get("world")
    world_mode = world_raw is not None
    modules = compile_module_shells(
        module_raw,
        set(value_ids),
        labels,
        units,
        intervals,
        dependencies,
        computations,
        cues,
        value_states,
        minimum_modules=WORLD_MIN_MODULES if world_mode else MIN_MODULES,
        maximum_modules=WORLD_MAX_MODULES if world_mode else MAX_MODULES,
    )
    directly_visible_values = {
        binding["value"]
        for module in modules
        for binding in module["bindings"]
    }
    unbound_sources = sorted(source_ids - directly_visible_values)
    if unbound_sources:
        raise BriefError(
            "every source concept must be visibly bound in at least one module; "
            f"unbound source concept(s): {unbound_sources}"
        )
    for module in modules:
        expected_focus = [
            focus["id"]
            for focus in focus_groups
            if module["id"] in focus["moduleIds"]
        ]
        module["focusGroups"] = expected_focus
    world_plan: dict[str, Any] | None = None
    navigation_plan: dict[str, Any] | None = None
    if world_mode:
        (
            world_plan,
            navigation_plan,
            view_box,
            safe_area,
            reading_order,
        ) = compile_world_layout(world_raw, modules, focus_ids)
    else:
        megacanvas = len(modules) > 12
        view_box = MEGACANVAS_VIEW_BOX if megacanvas else VIEW_BOX
        safe_area = MEGACANVAS_SAFE_AREA if megacanvas else SAFE_AREA
        reading_order = assign_layout(modules, safe_area)
    source_domains = {
        item["id"]: (float(item["domain"][0]), float(item["domain"][1]))
        for item in concepts
    }
    timeline = compile_timeline(
        brief.get("timeline"),
        focus_ids,
        source_domains,
        {item["id"] for item in scenarios},
    )
    color_tokens = identity_color_tokens(concepts, derived)
    values_by_token: dict[str, list[str]] = {}
    for value_id in value_ids:
        values_by_token.setdefault(color_tokens[value_id], []).append(value_id)
    identity: dict[str, dict[str, Any]] = {}
    aliases: list[dict[str, Any]] = []
    for token, grouped_values in values_by_token.items():
        common_words = set(grouped_values[0].split("-"))
        for value_id in grouped_values[1:]:
            common_words &= set(value_id.split("-"))
        if len(grouped_values) > 1 and common_words:
            identity_id = token
            stable_cue = max(common_words, key=lambda word: (len(word), word))
            identity[identity_id] = {"colorToken": token, "nonColor": [stable_cue]}
            aliases.append(
                {
                    "identity": identity_id,
                    "values": list(grouped_values),
                    "rationale": (
                        f"These scaled or unit-converted {stable_cue} values preserve one semantic identity "
                        f"and canonical color token {token}."
                    ),
                }
            )
            continue
        for value_id in grouped_values:
            identity[value_id] = {"colorToken": token, "nonColor": [cues[value_id]]}
            aliases.append(
                {
                    "identity": value_id,
                    "values": [value_id],
                    "rationale": (
                        f"The value {value_id} retains its own role cue and canonical color token {token}."
                    ),
                }
            )
    plan: dict[str, Any] = {
        "version": 1,
        "compositionId": composition_id,
        "title": title,
        "provenance": provenance,
        "locale": require_text(brief.get("locale", "en-US"), "locale"),
        "viewBox": view_box,
        "initialScenario": initial_scenario,
        "syncModes": ["semantic", "state", "focus"]
        + (["time"] if timeline else [])
        + (["navigation"] if navigation_plan else []),
        "identity": identity,
        "identityAliases": aliases,
        "layout": {
            "armature": require_text(brief.get("armature"), "armature"),
            "safeArea": safe_area,
            "gap": GAP,
            "readingOrder": reading_order,
        },
        "concepts": concepts,
        "derived": derived,
        "scenarios": scenarios,
        "modules": modules,
        "relationships": relationships,
        "focusGroups": focus_groups,
        "timeline": timeline,
    }
    if world_plan is not None and navigation_plan is not None:
        plan["world"] = world_plan
        plan["navigation"] = navigation_plan
    if "subtitle" in brief:
        plan["subtitle"] = require_text(brief["subtitle"], "subtitle")
    try:
        scaffold.validate_plan(plan)
    except ValueError as exc:
        raise BriefError(f"compiled plan failed v1 validation: {exc}") from exc
    return plan, normalizations


def write_atomic(path: Path, payload: bytes, force: bool) -> None:
    if path.exists() and not force:
        raise BriefError(f"output already exists: {path}; rerun with --force to replace it")
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="wb", prefix=f".{path.name}.", suffix=".tmp", dir=path.parent, delete=False
        ) as stream:
            temporary = Path(stream.name)
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if temporary is not None and temporary.exists():
            temporary.unlink()


def main() -> int:
    args = parse_args()
    try:
        brief_path = args.brief.resolve()
        output_path = args.output.resolve()
        if brief_path == output_path:
            raise BriefError("output must differ from the input brief; the compiler never mutates its brief")
        brief = load_brief(brief_path)
        plan, normalizations = compile_brief(brief)
        payload = (json.dumps(plan, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
        write_atomic(output_path, payload, args.force)
        result = {
            "ok": True,
            "brief": str(brief_path),
            "output": str(output_path),
            "sha256": hashlib.sha256(payload).hexdigest(),
            "moduleCount": len(plan["modules"]),
            "normalizations": normalizations,
        }
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"Compiled {len(plan['modules'])} modules to {output_path}")
        return 0
    except (BriefError, OSError) as exc:
        result = {"ok": False, "error": str(exc)}
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
