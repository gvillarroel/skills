#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

"""Compose a finished standalone SVG from a synchronized-composition plan.

The script deliberately uses the sibling scaffold and module-replacement tools
as its trusted write path. It generates small deterministic module fragments,
validates every binding contract during replacement, and publishes the exact
output path only after every placeholder has been removed.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import stat
import sys
import tempfile
import time
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path
from types import SimpleNamespace
from typing import Any


sys.dont_write_bytecode = True

import replace_svg_module as replacer  # noqa: E402
import scaffold_synchronized_svg as scaffold  # noqa: E402


SVG_NS = "http://www.w3.org/2000/svg"
class CompositionError(ValueError):
    """Describe a deterministic composition failure."""


class JsonArgumentParser(argparse.ArgumentParser):
    """Emit command-line errors in the same shape as runtime JSON errors."""

    def error(self, message: str) -> None:
        print(json.dumps({"ok": False, "error": f"argument error: {message}"}, indent=2))
        raise SystemExit(2)


@dataclass(frozen=True)
class BindingInfo:
    """Resolved static state and visual identity for one planned binding."""

    index: int
    binding: dict[str, Any]
    role: str
    value_id: str
    channel: str
    raw: float
    rendered: float | str
    color: str
    unit: str
    domain: tuple[float, float] | None
    accessible_value: str


def parse_args() -> argparse.Namespace:
    parser = JsonArgumentParser(
        description=(
            "Create a final no-placeholder synchronized SVG using deterministic "
            "asset-family renderers."
        )
    )
    parser.add_argument("--spec", required=True, type=Path, help="Composition plan JSON")
    parser.add_argument("--output", required=True, type=Path, help="Exact final SVG path")
    parser.add_argument("--report", type=Path, help="Optional JSON composition report")
    parser.add_argument("--force", action="store_true", help="Replace existing output files")
    parser.add_argument("--json", action="store_true", help="Print the result as JSON")
    return parser.parse_args()


def family_for(asset_type: str) -> str:
    """Map an open-ended asset type to a stable visual grammar."""

    tokens = set(asset_type.lower().replace("_", "-").split("-"))
    text = asset_type.lower()
    if tokens & {"waterfall"} or "waterfall" in text:
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


def esc(value: object) -> str:
    return scaffold.esc(value)


def fmt(value: float) -> str:
    return scaffold.fmt(float(value))


def positive_scale(numerator: float, denominator: float, *, conservative: bool = False) -> float:
    """Return a finite positive ratio without imposing a unit-dependent floor.

    SVG scale factors routinely fall below one thousandth when canonical values
    use large physical units.  An absolute floor would silently change the
    visual domain and can clamp otherwise legal states.  Keep the true ratio;
    for cumulative layouts, nudge it downward by one representable float so
    serialization noise cannot push the final mark beyond its plot span.
    """

    numerator = float(numerator)
    denominator = float(denominator)
    if not math.isfinite(numerator) or not math.isfinite(denominator):
        raise CompositionError("scale inputs must be finite")
    if numerator <= 0 or denominator <= 0:
        raise CompositionError("scale inputs must be positive")
    scale = numerator / denominator
    if conservative:
        scale = math.nextafter(scale, 0.0)
    if not math.isfinite(scale) or scale <= 0:
        raise CompositionError("scale ratio must remain finite and positive")
    return scale


def fmt_scale(value: float) -> str:
    """Serialize scale factors with enough significant digits for large units."""

    value = float(value)
    if not math.isfinite(value):
        raise CompositionError("serialized scale must be finite")
    return f"{value:.15g}"


def short_label(value: str, limit: int = 24) -> str:
    label = value.replace("-", " ").strip()
    if len(label) <= limit:
        return label
    return label[: max(1, limit - 1)].rstrip() + "…"


def role_label(role: str, limit: int = 24) -> str:
    label = scaffold.humanize_role(role)
    if label == "Flexible":
        label = "Flexible Cash"
    if len(label) <= limit:
        return label
    return label[: max(1, limit - 1)].rstrip() + "…"


def binding_label(info: BindingInfo, limit: int = 24) -> str:
    """Return project-facing copy without exposing selector or channel tokens."""

    declared = info.binding.get("label")
    if isinstance(declared, str) and declared.strip():
        return short_label(declared.strip(), limit)
    return role_label(info.role, limit)


def table_binding_label(info: BindingInfo, limit: int = 24) -> str:
    """Keep recurring annual/monthly measures distinguishable in exact tables."""

    declared = info.binding.get("label")
    base = (
        declared.strip()
        if isinstance(declared, str) and declared.strip()
        else role_label(info.role, max(limit, 48))
    )
    period = info.unit.rsplit("/", 1)[1].lower() if "/" in info.unit else ""
    prefix = {
        "year": "Annual",
        "month": "Monthly",
        "week": "Weekly",
        "day": "Daily",
        "hour": "Hourly",
    }.get(period)
    if prefix and prefix.lower() not in base.lower():
        base = f"{prefix} {base}"
    return short_label(base, limit)


def source_color_map(plan: dict[str, Any]) -> dict[str, str]:
    all_ids = [item["id"] for item in [*plan["concepts"], *plan.get("derived", [])]]
    token_index = {value_id: index for index, value_id in enumerate(all_ids)}
    result: dict[str, str] = {
        value_id: (
            f"var(--concept-{value_id}, "
            f"{scaffold.color_for_index(index)})"
        )
        for index, value_id in enumerate(all_ids)
    }
    identity = plan.get("identity", {})
    aliases = plan.get("identityAliases", [])
    if isinstance(identity, dict) and isinstance(aliases, list):
        for alias in aliases:
            if not isinstance(alias, dict) or not isinstance(alias.get("values"), list):
                continue
            definition = identity.get(alias.get("identity"))
            token = definition.get("colorToken") if isinstance(definition, dict) else None
            if token not in token_index:
                continue
            fallback = scaffold.color_for_index(token_index[token])
            for value_id in alias["values"]:
                if value_id in result:
                    result[value_id] = f"var(--concept-{token}, {fallback})"
    return result


def accessible_value_text(
    raw: float,
    binding: dict[str, Any],
    unit: str,
    locale: str,
) -> str:
    """Format one canonical numeric value for assistive technology."""

    display_raw = 0.0 if float(raw) == 0.0 else float(raw)
    declared_format = binding.get("format")
    effective_format = declared_format
    currency_period: str | None = None
    if "/" in unit:
        prefix, period = unit.split("/", 1)
        if len(prefix) == 3 and prefix.isalpha() and prefix.upper() == prefix:
            currency_period = period
            if not isinstance(effective_format, dict):
                effective_format = {
                    "style": "currency",
                    "currency": prefix,
                    "maximumFractionDigits": 2 if not display_raw.is_integer() else 0,
                }
    if unit == "fraction" and not isinstance(effective_format, dict):
        effective_format = {
            "style": "percent",
            "maximumFractionDigits": 0 if float(display_raw * 100).is_integer() else 1,
        }
    formatted = scaffold.format_value(display_raw, effective_format, locale)
    if currency_period:
        spoken_period = {
            "year": "per year",
            "month": "per month",
            "week": "per week",
            "day": "per day",
            "hour": "per hour",
        }.get(currency_period, f"per {currency_period}")
        return f"{formatted} {spoken_period}"
    if isinstance(effective_format, dict) and effective_format.get("suffix"):
        return formatted
    if unit and unit != "fraction" and not (
        isinstance(effective_format, dict) and effective_format.get("style") == "currency"
    ):
        return f"{formatted} {unit}"
    return formatted


def binding_infos(
    plan: dict[str, Any],
    module: dict[str, Any],
    values: dict[str, float],
    colors: dict[str, str],
) -> list[BindingInfo]:
    roles: set[str] = set()
    infos: list[BindingInfo] = []
    value_definitions = {
        item["id"]: item for item in [*plan["concepts"], *plan.get("derived", [])]
    }
    for index, binding in enumerate(module["bindings"]):
        role = scaffold.role_for(binding["selector"])
        if role in roles:
            raise CompositionError(
                f"module {module['id']!r} repeats data-role {role!r}; "
                "safe fragment replacement requires one role per binding"
            )
        roles.add(role)
        value_id = binding["value"]
        raw = float(values[value_id])
        rendered = scaffold.transformed_value(raw, binding.get("transform"))
        definition = value_definitions[value_id]
        unit = str(definition.get("unit", ""))
        raw_domain = definition.get("domain")
        if isinstance(binding.get("transform"), dict):
            raw_domain = binding["transform"].get("domain", raw_domain)
        domain = None
        if isinstance(raw_domain, list) and len(raw_domain) == 2:
            first, second = float(raw_domain[0]), float(raw_domain[1])
            domain = (min(first, second), max(first, second))
        infos.append(
            BindingInfo(
                index=index,
                binding=binding,
                role=role,
                value_id=value_id,
                channel=binding["channel"],
                raw=raw,
                rendered=rendered,
                color=colors[value_id],
                unit=unit,
                domain=domain,
                accessible_value=accessible_value_text(
                    raw,
                    binding,
                    unit,
                    str(plan.get("locale", "en-US")),
                ),
            )
        )
    return infos


def common_attributes(module_id: str, info: BindingInfo, *, kind: str = "mark") -> str:
    accessible_label = binding_label(info, 36)
    accessible_role = "meter" if info.channel == "aria-value" else "img"
    range_attributes = ""
    if accessible_role == "meter":
        low, high = info.domain or (min(0.0, info.raw), max(1.0, info.raw))
        range_attributes = (
            f' aria-valuemin="{esc(scaffold.canonical_number_text(low))}" '
            f'aria-valuemax="{esc(scaffold.canonical_number_text(high))}" '
            f'aria-valuenow="{esc(scaffold.canonical_number_text(info.raw))}" '
            f'aria-valuetext="{esc(info.accessible_value)}"'
        )
    return (
        f'id="{esc(module_id)}-{esc(info.role)}-binding" '
        f'class="sync-bound-{esc(kind)}" data-role="{esc(info.role)}" '
        f'role="{accessible_role}" '
        f'data-bind="{esc(info.value_id)}" data-channel="{esc(info.channel)}" '
        f'data-current-value="{esc(scaffold.canonical_number_text(info.raw))}" data-sync-revision="0" '
        f'data-accessible-label="{esc(accessible_label)}" data-value-unit="{esc(info.unit)}" '
        f'data-accessible-value="{esc(info.accessible_value)}" '
        f'aria-label="{esc(accessible_label)}: {esc(info.accessible_value)}"'
        f'{range_attributes}'
    )


def numeric_range(info: BindingInfo, plan: dict[str, Any]) -> tuple[float, float]:
    transform = info.binding.get("transform")
    if isinstance(transform, dict) and transform.get("op") in {"linear", "rotate"}:
        target = transform.get("range")
        if isinstance(target, list) and len(target) == 2:
            first, second = float(target[0]), float(target[1])
            return (min(first, second), max(first, second))
    source = next((item for item in plan["concepts"] if item["id"] == info.value_id), None)
    if source and isinstance(source.get("domain"), list) and len(source["domain"]) == 2:
        first, second = float(source["domain"][0]), float(source["domain"][1])
        return (min(first, second), max(first, second))
    rendered = float(info.rendered) if isinstance(info.rendered, (int, float)) else info.raw
    spread = max(abs(rendered), 1.0)
    return (min(0.0, rendered - spread), max(1.0, rendered + spread))


def max_positive_extent(info: BindingInfo, plan: dict[str, Any]) -> float:
    low, high = numeric_range(info, plan)
    rendered = float(info.rendered) if isinstance(info.rendered, (int, float)) else info.raw
    return max(1.0, abs(low), abs(high), abs(rendered))


def rendered_units_per_raw(info: BindingInfo) -> float:
    transform = info.binding.get("transform")
    if isinstance(transform, dict) and transform.get("op") == "linear":
        domain = transform.get("domain")
        target = transform.get("range")
        if isinstance(domain, list) and len(domain) == 2 and isinstance(target, list) and len(target) == 2:
            domain_span = float(domain[1]) - float(domain[0])
            if domain_span:
                return abs((float(target[1]) - float(target[0])) / domain_span)
    return 1.0


def scenario_value_states(plan: dict[str, Any]) -> list[dict[str, float]]:
    states: list[dict[str, float]] = []
    for scenario in plan["scenarios"]:
        values = {item["id"]: float(item["default"]) for item in plan["concepts"]}
        values.update({key: float(value) for key, value in scenario["values"].items()})
        pending = {item["id"]: item for item in plan.get("derived", [])}
        while pending:
            progressed = False
            for value_id, item in list(pending.items()):
                if set(item["dependsOn"]) <= set(values):
                    values[value_id] = scaffold.eval_node(item["compute"], values)
                    del pending[value_id]
                    progressed = True
            if not progressed:
                raise CompositionError("could not resolve a declared scenario for renderer scaling")
        states.append(values)
    return states


def scenario_raw_extent(plan: dict[str, Any], infos: list[BindingInfo]) -> float:
    """Return one shared canonical magnitude scale for a reconciled module."""

    extent = 1.0
    for info in infos:
        extent = max(extent, abs(float(info.raw)))
        transform = info.binding.get("transform")
        domain = transform.get("domain") if isinstance(transform, dict) else None
        if isinstance(domain, list) and len(domain) == 2:
            extent = max(extent, abs(float(domain[0])), abs(float(domain[1])))
    for values in scenario_value_states(plan):
        for info in infos:
            extent = max(extent, abs(float(values[info.value_id])))
    return max(1.0, extent)


def validate_waterfall_scale(module_id: str, infos: list[BindingInfo]) -> None:
    units = {info.unit for info in infos}
    if len(units) > 1:
        raise CompositionError(
            f"waterfall module {module_id!r} must use one canonical unit; received {sorted(units)}"
        )
    slopes: list[float] = []
    for info in infos:
        transform = info.binding.get("transform")
        if not isinstance(transform, dict) or transform.get("op") != "linear":
            raise CompositionError(
                f"waterfall module {module_id!r} binding {info.role!r} needs a shared linear magnitude transform"
            )
        domain = transform.get("domain")
        target = transform.get("range")
        if not (
            isinstance(domain, list)
            and len(domain) == 2
            and isinstance(target, list)
            and len(target) == 2
        ):
            raise CompositionError(
                f"waterfall module {module_id!r} binding {info.role!r} has an invalid transform"
            )
        zero = scaffold.transformed_value(0.0, transform)
        if not isinstance(zero, (int, float)) or abs(float(zero)) > 1e-7:
            raise CompositionError(
                f"waterfall module {module_id!r} binding {info.role!r} must map canonical zero to visual zero"
            )
        span = float(domain[1]) - float(domain[0])
        if span == 0.0:
            raise CompositionError(
                f"waterfall module {module_id!r} binding {info.role!r} has a zero transform span"
            )
        slopes.append(abs((float(target[1]) - float(target[0])) / span))
    if slopes and max(slopes) - min(slopes) > max(slopes) * 1e-7:
        raise CompositionError(
            f"waterfall module {module_id!r} bindings must use one shared absolute scale"
        )


def validate_bar_scale(
    plan: dict[str, Any], module: dict[str, Any], infos: list[BindingInfo]
) -> None:
    """Require honest one-unit, zero-based geometry for comparative bars."""

    if not infos:
        return
    module_id = module["id"]
    units = {info.unit for info in infos}
    if len(units) != 1:
        raise CompositionError(
            f"comparative bar module {module_id!r} must use one canonical unit"
        )
    transforms = [info.binding.get("transform") for info in infos]
    if any(
        not isinstance(transform, dict) or transform.get("op") != "linear"
        for transform in transforms
    ):
        raise CompositionError(
            f"comparative bar module {module_id!r} needs shared linear transforms"
        )
    signatures = {
        (
            tuple(float(value) for value in transform.get("domain", [])),
            tuple(float(value) for value in transform.get("range", [])),
        )
        for transform in transforms
        if isinstance(transform, dict)
    }
    if len(signatures) != 1 or any(
        len(domain) != 2 or len(target) != 2
        for domain, target in signatures
    ):
        raise CompositionError(
            f"comparative bar module {module_id!r} bindings must use one shared scale"
        )
    domain, _target = next(iter(signatures))
    zero = scaffold.transformed_value(0.0, transforms[0])
    if domain[0] < 0 or not isinstance(zero, (int, float)) or abs(float(zero)) > 1e-7:
        raise CompositionError(
            f"comparative bar module {module_id!r} must map canonical zero to visual zero"
        )
    for values in scenario_value_states(plan):
        if any(float(values[info.value_id]) < 0 for info in infos):
            raise CompositionError(
                f"comparative bar module {module_id!r} cannot encode negative scenario values "
                "without a diverging-bar renderer"
            )


def validate_stack_scale(
    plan: dict[str, Any], module: dict[str, Any], infos: list[BindingInfo]
) -> str:
    module_id = module["id"]
    total_id = module.get("stackTotal")
    if not isinstance(total_id, str):
        raise CompositionError(
            f"stacked module {module_id!r} needs stackTotal for an inspectable reconciliation"
        )
    units = {info.unit for info in infos}
    if len(units) != 1:
        raise CompositionError(
            f"stacked module {module_id!r} parts must use one canonical unit"
        )
    transforms = [info.binding.get("transform") for info in infos]
    if not transforms or any(
        not isinstance(transform, dict) or transform.get("op") != "linear"
        for transform in transforms
    ):
        raise CompositionError(
            f"stacked module {module_id!r} parts need shared linear transforms"
        )
    signatures = {
        (
            tuple(float(value) for value in transform.get("domain", [])),
            tuple(float(value) for value in transform.get("range", [])),
        )
        for transform in transforms
        if isinstance(transform, dict)
    }
    if len(signatures) != 1 or any(len(domain) != 2 or len(target) != 2 for domain, target in signatures):
        raise CompositionError(
            f"stacked module {module_id!r} parts must use one shared zero-anchored scale"
        )
    domain, _target = next(iter(signatures))
    if abs(scaffold.transformed_value(0.0, transforms[0])) > 1e-7 or domain[0] < 0:
        raise CompositionError(
            f"stacked module {module_id!r} parts must map canonical zero to visual zero"
        )
    for values in scenario_value_states(plan):
        part_values = [float(values[info.value_id]) for info in infos]
        if any(value < 0 for value in part_values):
            raise CompositionError(
                f"stacked module {module_id!r} contains a negative part in a named scenario"
            )
        expected_total = float(values[total_id])
        tolerance = max(1e-7, abs(expected_total) * 1e-7)
        if abs(sum(part_values) - expected_total) > tolerance:
            raise CompositionError(
                f"stacked module {module_id!r} parts do not reconcile to stackTotal {total_id!r}"
            )
    return total_id


def render_text_binding(
    module_id: str,
    info: BindingInfo,
    x: float,
    y: float,
    anchor: str = "end",
    *,
    font_size: float = 11.0,
) -> str:
    value = scaffold.format_value(info.raw, info.binding.get("format"), "en-US")
    return (
        f'<text {common_attributes(module_id, info, kind="value")} x="{fmt(x)}" y="{fmt(y)}" '
        f'text-anchor="{anchor}" font-size="{fmt(font_size)}" font-weight="720" fill="{esc(info.color)}">'
        f'{esc(value)}</text>'
    )


def render_mark(
    plan: dict[str, Any],
    module_id: str,
    info: BindingInfo,
    box: tuple[float, float, float, float],
    *,
    vertical: bool = False,
) -> str:
    """Render one contract target inside a transform-safe local box."""

    x, y, width, height = box
    width = max(8.0, width)
    height = max(8.0, height)
    common = common_attributes(module_id, info)
    color = esc(info.color)
    channel = info.channel
    rendered = info.rendered

    if channel == "width":
        extent = max_positive_extent(info, plan)
        scale = positive_scale(width - 2, extent)
        initial = max(0.0, float(rendered))
        bar_height = min(18.0, max(8.0, height * 0.48))
        bar_y = y + (height - bar_height) / 2
        return (
            f'<g transform="translate({fmt(x + 1)} {fmt(bar_y)}) scale({fmt_scale(scale)} 1)">'
            f'<rect {common} x="0" y="0" width="{fmt(initial)}" height="{fmt(bar_height)}" '
            f'fill="{color}" fill-opacity="0.86" rx="3"/></g>'
        )

    if channel == "height":
        extent = max_positive_extent(info, plan)
        scale = positive_scale(height - 2, extent)
        initial = max(0.5, float(rendered))
        column_width = min(width * 0.62, 28.0)
        column_x = x + (width - column_width) / 2
        if vertical:
            return (
                f'<g transform="translate({fmt(column_x)} {fmt(y + height - 1)}) scale(1 {fmt_scale(-scale)})">'
                f'<rect {common} x="0" y="0" width="{fmt(column_width)}" height="{fmt(initial)}" '
                f'fill="{color}" fill-opacity="0.86" rx="2"/></g>'
            )
        return (
            f'<g transform="translate({fmt(column_x)} {fmt(y + 1)}) scale(1 {fmt_scale(scale)})">'
            f'<rect {common} x="0" y="0" width="{fmt(column_width)}" height="{fmt(initial)}" '
            f'fill="{color}" fill-opacity="0.86" rx="2"/></g>'
        )

    if channel == "r":
        extent = max_positive_extent(info, plan)
        radius_limit = max(3.0, min(width, height) * 0.36)
        scale = positive_scale(radius_limit, extent)
        initial = max(0.5, float(rendered))
        return (
            f'<g transform="translate({fmt(x + width / 2)} {fmt(y + height / 2)}) '
            f'scale({fmt_scale(scale)})"><circle {common} cx="0" cy="0" r="{fmt(initial)}" '
            f'fill="{color}" fill-opacity="0.82" stroke="{color}" stroke-width="2"/></g>'
        )

    if channel in {"x", "y"}:
        low, high = numeric_range(info, plan)
        span = max(1e-9, high - low)
        initial = float(rendered)
        if channel == "x":
            scale = positive_scale(width - 12, span)
            marker_extent = max(0.01, 4.0 / scale)
            translate_x = x + 6 - low * scale
            return (
                f'<g transform="translate({fmt(translate_x)} {fmt(y + height / 2)}) scale({fmt_scale(scale)} 1)">'
                f'<rect {common} x="{fmt(initial)}" y="-5" width="{fmt(marker_extent)}" height="10" rx="0.5" '
                f'fill="{color}" stroke="#ffffff" stroke-width="2" vector-effect="non-scaling-stroke"/></g>'
            )
        scale = positive_scale(height - 12, span)
        marker_extent = max(0.01, 4.0 / scale)
        translate_y = y + 6 - low * scale
        return (
            f'<g transform="translate({fmt(x + width / 2)} {fmt(translate_y)}) scale(1 {fmt_scale(scale)})">'
            f'<rect {common} x="-5" y="{fmt(initial)}" width="10" height="{fmt(marker_extent)}" rx="0.5" '
            f'fill="{color}" stroke="#ffffff" stroke-width="2" vector-effect="non-scaling-stroke"/></g>'
        )

    if channel == "transform":
        transform = info.binding.get("transform")
        center = transform.get("center", [0, 0]) if isinstance(transform, dict) else [0, 0]
        cx, cy = float(center[0]), float(center[1])
        target_x, target_y = x + width / 2, y + height / 2
        dx, dy = target_x - cx, target_y - cy
        length = max(8.0, min(width, height) * 0.34)
        transform_value = str(rendered)
        return (
            f'<g transform="translate({fmt(dx)} {fmt(dy)})"><g {common} '
            f'transform="{esc(transform_value)}">'
            f'<line x1="{fmt(cx)}" y1="{fmt(cy)}" x2="{fmt(cx + length)}" y2="{fmt(cy)}" '
            f'stroke="{color}" stroke-width="5" stroke-linecap="round"/>'
            f'<circle cx="{fmt(cx)}" cy="{fmt(cy)}" r="6" fill="{color}"/></g></g>'
        )

    if channel == "opacity":
        initial = min(1.0, max(0.0, float(rendered)))
        return (
            f'<rect {common} x="{fmt(x + width * 0.12)}" y="{fmt(y + height * 0.16)}" '
            f'width="{fmt(width * 0.76)}" height="{fmt(height * 0.68)}" opacity="{fmt(initial)}" '
            f'fill="{color}" rx="6"/>'
        )

    if channel == "class":
        return (
            f'<g {common} data-sync-class="{esc(rendered)}"><rect x="{fmt(x + width * 0.12)}" '
            f'y="{fmt(y + height * 0.16)}" width="{fmt(width * 0.76)}" '
            f'height="{fmt(height * 0.68)}" fill="{color}" fill-opacity="0.8" rx="6"/></g>'
        )

    if channel == "aria-value":
        return (
            f'<g {common}><rect '
            f'x="{fmt(x + width * 0.12)}" y="{fmt(y + height * 0.32)}" '
            f'width="{fmt(width * 0.76)}" height="{fmt(height * 0.36)}" '
            f'fill="{color}" fill-opacity="0.82" rx="5"/></g>'
        )

    if channel == "path":
        # The current state contract carries a numeric value; keep a valid static
        # fallback path while the shared runtime owns subsequent d updates.
        path = f"M{fmt(x + 2)} {fmt(y + height * 0.72)} Q{fmt(x + width / 2)} {fmt(y)} {fmt(x + width - 2)} {fmt(y + height * 0.28)}"
        return (
            f'<path {common} d="{path}" fill="none" stroke="{color}" stroke-width="4" '
            f'stroke-linecap="round" opacity="0.01"/>'
        )

    return (
        f'<rect {common} x="{fmt(x + 2)}" y="{fmt(y + 2)}" width="{fmt(width - 4)}" '
        f'height="{fmt(height - 4)}" fill="{color}" fill-opacity="0.75" rx="6"/>'
    )


def split_body(
    module: dict[str, Any], infos: list[BindingInfo]
) -> tuple[float, float, float, list[BindingInfo], list[BindingInfo]]:
    width = float(module["region"][2])
    content_height = float(scaffold.module_content_geometry(module)[4])
    top = 8.0
    bottom = max(top + 18.0, content_height - 10.0)
    text_infos = [info for info in infos if info.channel == "text"]
    mark_infos = [info for info in infos if info.channel != "text"]
    if text_infos and mark_infos:
        rows = math.ceil(len(text_infos) / (2 if width >= 280 else 1))
        rail_height = min(max(34.0, rows * 34.0), max(34.0, (bottom - top) * 0.42))
        visual_bottom = max(top + 22, bottom - rail_height - 8)
    elif text_infos:
        visual_bottom = top
    else:
        visual_bottom = bottom
    return top, visual_bottom, bottom, mark_infos, text_infos


def render_text_rail(
    module_id: str,
    text_infos: list[BindingInfo],
    width: float,
    top: float,
    bottom: float,
    *,
    table: bool = False,
) -> str:
    if not text_infos:
        return ""
    left, right = 22.0, width - 22.0
    available = max(20.0, bottom - top)
    base_columns = 2 if width >= (260 if table else 280) and len(text_infos) > 1 else 1
    max_columns = max(1, min(3, int((right - left) // 150.0), len(text_infos)))
    needed_columns = max(1, math.ceil(len(text_infos) * 30.0 / available))
    columns = min(max_columns, max(base_columns, needed_columns))
    rows = math.ceil(len(text_infos) / columns)
    cell_width = (right - left) / columns
    row_height = available / rows
    parts = [
        f'<g id="{esc(module_id)}-value-rail" class="value-rail">',
        f'<line x1="{fmt(left)}" y1="{fmt(top)}" x2="{fmt(right)}" y2="{fmt(top)}" stroke="#d6dce8"/>',
    ]
    for index, info in enumerate(text_infos):
        row, column = divmod(index, columns)
        cell_left = left + column * cell_width
        cell_right = cell_left + cell_width
        cell_top = top + row * row_height
        label_offset = min(11.0, max(8.0, row_height * 0.32))
        label_y = cell_top + label_offset
        value_y = min(cell_top + row_height - 3.0, label_y + 13.0)
        label_limit = max(10, min(34, int(cell_width / 6.4)))
        visible_label = (
            table_binding_label(info, label_limit)
            if table
            else binding_label(info, label_limit)
        )
        parts.append(
            f'<text x="{fmt(cell_left + 4)}" y="{fmt(label_y)}" '
            f'font-size="{9 if row_height < 30 else 10}" '
            f'letter-spacing="0.04em" fill="#637087" aria-hidden="true">'
            f'{esc(visible_label)}</text>'
        )
        parts.append(render_text_binding(module_id, info, cell_right - 5, value_y))
        if column > 0:
            parts.append(
                f'<line x1="{fmt(cell_left)}" y1="{fmt(cell_top + 5)}" x2="{fmt(cell_left)}" '
                f'y2="{fmt(min(bottom, cell_top + row_height - 3))}" stroke="#e5e9f1"/>'
            )
    parts.append("</g>")
    return "".join(parts)


def render_stacked_bar_family(
    plan: dict[str, Any], module: dict[str, Any], infos: list[BindingInfo]
) -> str:
    module_id = module["id"]
    width = float(module["region"][2])
    top, visual_bottom, bottom, marks, texts = split_body(module, infos)
    stack_marks = [info for info in marks if info.channel == "width"]
    other_marks = [info for info in marks if info.channel != "width"]
    if not stack_marks:
        return render_bar_family(plan, {**module, "assetType": "bar-chart"}, infos)
    stack_total_id = validate_stack_scale(plan, module, stack_marks)

    left, right = 24.0, width - 24.0
    plot_width = max(20.0, right - left)
    available_height = max(40.0, visual_bottom - top)
    stack_y = top + max(28.0, available_height * 0.32)
    stack_height = min(64.0, max(32.0, available_height * 0.24))
    domains: list[tuple[float, float]] = []
    ranges: list[tuple[float, float]] = []
    for info in stack_marks:
        transform = info.binding.get("transform")
        domain = transform.get("domain") if isinstance(transform, dict) else None
        target = transform.get("range") if isinstance(transform, dict) else None
        if isinstance(domain, list) and len(domain) == 2 and isinstance(target, list) and len(target) == 2:
            domains.append((float(domain[0]), float(domain[1])))
            ranges.append((float(target[0]), float(target[1])))
    common_scale = (
        len(domains) == len(stack_marks)
        and len(set(domains)) == 1
        and len(set(ranges)) == 1
    )
    extent = (
        max(abs(ranges[0][0]), abs(ranges[0][1]), 1.0)
        if common_scale
        else sum(max_positive_extent(info, plan) for info in stack_marks)
    )
    # Serialize the available span first, then round the shared scale downward to
    # the same six-decimal SVG precision. This prevents the last reconciled part
    # from being falsely marked as clamped by independent attribute rounding.
    layout_max_span = float(fmt(plot_width - 2))
    scale = positive_scale(layout_max_span, max(1.0, extent), conservative=True)
    raw_ceiling = 0.0
    ceiling_known = True
    if common_scale:
        raw_ceiling = max(domains[0])
    else:
        for info in stack_marks:
            transform = info.binding.get("transform")
            domain = transform.get("domain") if isinstance(transform, dict) else None
            if not isinstance(domain, list) or len(domain) != 2:
                ceiling_known = False
                break
            raw_ceiling += max(float(domain[0]), float(domain[1]))
    if ceiling_known:
        ceiling_format = (
            texts[0].binding.get("format")
            if texts
            else stack_marks[0].binding.get("format")
        )
        ceiling_copy = f"Ceiling {scaffold.format_value(raw_ceiling, ceiling_format, plan.get('locale', 'en-US'))}"
    else:
        ceiling_copy = f"Rendered ceiling {fmt(extent)}"
    cursor = left + 1
    parts = [
        f'<g id="{esc(module_id)}-stack-plot" class="asset-stack-plot" data-sync-layout="stack" '
        f'data-stack-total="{esc(stack_total_id)}" '
        f'data-layout-x="{fmt(left + 1)}" data-layout-y="{fmt(stack_y)}" data-layout-scale="{fmt_scale(scale)}" '
        f'data-layout-max-span="{fmt(layout_max_span)}">',
        f'<text x="{fmt(left)}" y="{fmt(stack_y - 12)}" font-size="10" fill="#637087" '
        f'aria-hidden="true">Absolute scale</text>',
        f'<text x="{fmt(right)}" y="{fmt(stack_y - 12)}" text-anchor="end" font-size="10" '
        f'fill="#637087" aria-hidden="true">{esc(ceiling_copy)}</text>',
        f'<rect x="{fmt(left)}" y="{fmt(stack_y)}" width="{fmt(plot_width)}" height="{fmt(stack_height)}" '
        f'fill="#e8edf5" stroke="#d6dce8" rx="4"/>',
    ]
    legend_y = min(visual_bottom - 9, stack_y + stack_height + 30)
    legend_cell = plot_width / len(stack_marks)
    for index, info in enumerate(stack_marks):
        initial = max(0.0, float(info.rendered))
        remaining = max(0.0, left + plot_width - 1 - cursor)
        drawn = min(remaining, initial * scale)
        effective_scale = drawn / initial if initial != 0 else scale
        clamped = drawn + 0.25 < initial * scale
        parts.append(
            f'<g data-sync-layout-item="stack" data-visual-clamped="{str(clamped).lower()}" '
            f'transform="translate({fmt(cursor)} {fmt(stack_y)}) scale({fmt_scale(effective_scale)} 1)">'
            f'<rect {common_attributes(module_id, info)} x="0" y="0" width="{fmt(initial)}" '
            f'height="{fmt(stack_height)}" fill="{esc(info.color)}" fill-opacity="0.9"/></g>'
        )
        cursor += drawn
        legend_x = left + index * legend_cell
        parts.extend(
            [
                f'<rect x="{fmt(legend_x)}" y="{fmt(legend_y - 9)}" width="10" height="10" '
                f'fill="{esc(info.color)}" rx="2"/>',
                f'<text x="{fmt(legend_x + 15)}" y="{fmt(legend_y)}" font-size="10" fill="#637087" '
                f'aria-hidden="true">{esc(binding_label(info, 22))}</text>',
            ]
        )
    if other_marks:
        cell_width = plot_width / len(other_marks)
        lane_top = min(visual_bottom - 24, legend_y + 12)
        for index, info in enumerate(other_marks):
            parts.append(
                render_mark(plan, module_id, info, (left + index * cell_width, lane_top, cell_width, 22))
            )
    parts.append("</g>")
    parts.append(render_text_rail(module_id, texts, width, visual_bottom + 8, bottom))
    return "".join(parts)


def render_bar_family(
    plan: dict[str, Any], module: dict[str, Any], infos: list[BindingInfo]
) -> str:
    if "stack" in module["assetType"].lower():
        return render_stacked_bar_family(plan, module, infos)
    module_id = module["id"]
    width = float(module["region"][2])
    top, visual_bottom, bottom, marks, texts = split_body(module, infos)
    validate_bar_scale(plan, module, marks)
    parts = [
        f'<g id="{esc(module_id)}-bar-plot" class="asset-bar-plot" '
        'data-sync-layout="bar-comparison">'
    ]
    if marks:
        plot_left, plot_right = 24.0, width - 24.0
        available_height = max(18.0, visual_bottom - top)
        available_width = max(24.0, plot_right - plot_left)
        max_columns = max(1, min(3, int(available_width // 150.0)))
        columns = min(
            max_columns,
            max(1, math.ceil(len(marks) * 26.0 / available_height)),
        )
        rows = math.ceil(len(marks) / columns)
        column_gap = 12.0 if columns > 1 else 0.0
        cell_width = (available_width - column_gap * (columns - 1)) / columns
        row_height = available_height / rows
        for index, info in enumerate(marks):
            row, column = divmod(index, columns)
            cell_left = plot_left + column * (cell_width + column_gap)
            row_top = top + row * row_height
            label_offset = min(10.0, max(8.0, row_height * 0.32))
            label_y = row_top + label_offset
            mark_offset = min(max(12.0, label_offset + 4.0), max(12.0, row_height - 8.0))
            mark_y = row_top + mark_offset
            mark_height = max(6.0, min(14.0, row_height - mark_offset - 2.0))
            label_limit = max(12, min(28, int(cell_width / 6.2)))
            parts.extend(
                [
                    f'<text x="{fmt(cell_left)}" y="{fmt(label_y)}" font-size="{9 if row_height < 30 else 10}" '
                    f'fill="#637087" aria-hidden="true">{esc(binding_label(info, label_limit))}</text>',
                    f'<rect x="{fmt(cell_left)}" y="{fmt(mark_y)}" width="{fmt(cell_width)}" '
                    f'height="{fmt(mark_height)}" fill="#e8edf5" rx="3"/>',
                    render_mark(
                        plan,
                        module_id,
                        info,
                        (cell_left, mark_y, cell_width, mark_height),
                    ),
                ]
            )
    parts.append("</g>")
    rail_top = visual_bottom + 8 if marks else top
    parts.append(render_text_rail(module_id, texts, width, rail_top, bottom))
    return "".join(parts)


def render_waterfall_family(
    plan: dict[str, Any], module: dict[str, Any], infos: list[BindingInfo]
) -> str:
    module_id = module["id"]
    width = float(module["region"][2])
    top, visual_bottom, bottom, marks, texts = split_body(module, infos)
    height_marks = [info for info in marks if info.channel == "height"]
    other_marks = [info for info in marks if info.channel != "height"]
    left, right = 22.0, width - 22.0
    validate_waterfall_scale(module_id, height_marks)
    baseline = max(top + 20, visual_bottom - 5)
    plot_height = max(18.0, baseline - top - 6)
    extent = scenario_raw_extent(plan, height_marks) * 1.08
    scale = positive_scale(plot_height - 2, extent)
    max_visual_value = max(0.0, (baseline - top - 2) / scale)
    parts = [
        f'<g id="{esc(module_id)}-waterfall-plot" class="asset-waterfall-plot" '
        f'data-sync-layout="waterfall" data-layout-baseline="{fmt(baseline)}" '
        f'data-layout-scale="{fmt_scale(scale)}" data-layout-top="{fmt(top)}" '
        f'data-layout-max-value="{fmt(max_visual_value)}">',
        f'<line x1="{fmt(left)}" y1="{fmt(baseline)}" x2="{fmt(right)}" y2="{fmt(baseline)}" stroke="#aeb8c8"/>',
    ]
    if height_marks:
        column_width = (right - left) / len(height_marks)
        bar_width = min(34.0, max(18.0, column_width * 0.42))
        positions = [left + index * column_width + (column_width - bar_width) / 2 for index in range(len(height_marks))]
        level = 0.0
        for index, info in enumerate(height_marks):
            initial = abs(float(info.raw))
            rendered_extent = abs(float(info.rendered))
            is_total = index == 0 or index == len(height_marks) - 1
            if index == 0:
                visible = min(initial, max_visual_value)
                level = visible
                bar_top = baseline - visible * scale
                effective_scale = (
                    scale * visible / rendered_extent
                    if rendered_extent != 0
                    else 0.0
                )
                transform = (
                    f"translate({fmt(positions[index])} {fmt(baseline)}) "
                    f"scale(1 {fmt_scale(-effective_scale)})"
                )
            elif is_total:
                visible = min(initial, max_visual_value)
                bar_top = baseline - visible * scale
                effective_scale = (
                    scale * visible / rendered_extent
                    if rendered_extent != 0
                    else 0.0
                )
                transform = (
                    f"translate({fmt(positions[index])} {fmt(baseline)}) "
                    f"scale(1 {fmt_scale(-effective_scale)})"
                )
            else:
                visible = min(initial, max_visual_value, level)
                bar_top = baseline - level * scale
                effective_scale = (
                    scale * visible / rendered_extent
                    if rendered_extent != 0
                    else 0.0
                )
                transform = (
                    f"translate({fmt(positions[index])} {fmt(baseline - level * scale)}) "
                    f"scale(1 {fmt_scale(effective_scale)})"
                )
                level = max(0.0, level - visible)
            clamped = visible + 1e-6 < initial
            parts.append(
                f'<g data-sync-layout-item="waterfall" data-layout-x="{fmt(positions[index])}" '
                f'data-layout-index="{index}" data-visual-clamped="{str(clamped).lower()}" transform="{transform}">'
                f'<rect {common_attributes(module_id, info)} x="0" y="0" width="{fmt(bar_width)}" '
                f'height="{fmt(max(0.0, rendered_extent))}" fill="{esc(info.color)}" fill-opacity="0.9" rx="2"/></g>'
            )
            if index < len(height_marks) - 1:
                connector_y = baseline - level * scale
                parts.append(
                    f'<line data-sync-layout-connector="{index}" x1="{fmt(positions[index] + bar_width)}" '
                    f'y1="{fmt(connector_y)}" x2="{fmt(positions[index + 1])}" y2="{fmt(connector_y)}" '
                    f'stroke="#9aa6b8" stroke-width="1.5"/>'
                )
            waterfall_label = binding_label(info, 19 if not is_total else 16)
            if index > 0 and not is_total:
                waterfall_label = f"{waterfall_label} ↓"
            parts.append(
                f'<text x="{fmt(positions[index] + bar_width / 2)}" y="{fmt(baseline + 13)}" '
                f'text-anchor="middle" font-size="10" fill="#637087" aria-hidden="true">'
                f'{esc(waterfall_label)}</text>'
            )
            sign_kind = "plus" if index == 0 else ("total" if is_total else "minus")
            magnitude = scaffold.format_value(
                abs(info.raw), info.binding.get("format"), plan.get("locale", "en-US")
            )
            signed_copy = f"+{magnitude}" if sign_kind == "plus" else (
                f"−{magnitude}" if sign_kind == "minus" else info.accessible_value
            )
            parts.append(
                f'<text data-waterfall-signed-index="{index}" data-waterfall-sign="{sign_kind}" '
                f'x="{fmt(positions[index] + bar_width / 2)}" '
                f'y="{fmt(max(top + 12, bar_top - 7))}" '
                f'text-anchor="middle" font-size="10" font-weight="700" fill="#334155" '
                f'aria-hidden="true">{esc(signed_copy)}</text>'
            )
    if other_marks:
        cell_width = (right - left) / len(other_marks)
        for index, info in enumerate(other_marks):
            parts.append(render_mark(plan, module_id, info, (left + index * cell_width, top, cell_width, 18)))
    parts.append("</g>")
    rail_top = visual_bottom + 8 if marks else top
    parts.append(render_text_rail(module_id, texts, width, rail_top, bottom))
    return "".join(parts)


def render_line_family(
    plan: dict[str, Any], module: dict[str, Any], infos: list[BindingInfo]
) -> str:
    module_id = module["id"]
    width = float(module["region"][2])
    top, visual_bottom, bottom, marks, texts = split_body(module, infos)
    left, right = 24.0, width - 24.0
    height = max(24.0, visual_bottom - top)
    mid = top + height * 0.48
    asset = module["assetType"].lower()
    extra_layers: list[str] = []
    if "arrival" in asset:
        path = (
            f"M{fmt(left)} {fmt(top + height * 0.8)} "
            f"C{fmt(left + (right-left)*0.18)} {fmt(top + height*0.78)} "
            f"{fmt(left + (right-left)*0.28)} {fmt(top + height*0.62)} "
            f"{fmt(left + (right-left)*0.42)} {fmt(top + height*0.6)} "
            f"S{fmt(left + (right-left)*0.62)} {fmt(top + height*0.2)} "
            f"{fmt(right)} {fmt(top + height*0.2)}"
        )
        extra_layers.append(
            f'<text x="{fmt(left)}" y="{fmt(top + 12)}" font-size="9" fill="#637087" '
            'aria-hidden="true">demand burst</text>'
        )
    elif "response" in asset or "token" in asset:
        step = (right - left) / 6
        path = (
            f"M{fmt(left)} {fmt(top + height * 0.82)} "
            f"H{fmt(left + step)} V{fmt(top + height * 0.7)} "
            f"H{fmt(left + step*2)} V{fmt(top + height * 0.58)} "
            f"H{fmt(left + step*3)} V{fmt(top + height * 0.45)} "
            f"H{fmt(left + step*4)} V{fmt(top + height * 0.32)} "
            f"H{fmt(left + step*5)} V{fmt(top + height * 0.22)} H{fmt(right)}"
        )
        extra_layers.append(
            f'<text x="{fmt(left)}" y="{fmt(top + 12)}" font-size="9" fill="#637087" '
            'aria-hidden="true">token emission</text>'
        )
    elif "slo" in asset or "threshold" in asset:
        threshold_y = top + height * 0.36
        path = (
            f"M{fmt(left)} {fmt(top + height * 0.72)} "
            f"C{fmt(left + (right-left)*0.24)} {fmt(top + height*0.68)} "
            f"{fmt(left + (right-left)*0.46)} {fmt(top + height*0.5)} "
            f"{fmt(left + (right-left)*0.62)} {fmt(top + height*0.56)} "
            f"S{fmt(right - (right-left)*0.16)} {fmt(top + height*0.2)} {fmt(right)} {fmt(top + height*0.24)}"
        )
        extra_layers.extend(
            [
                f'<rect x="{fmt(left)}" y="{fmt(top)}" width="{fmt(right-left)}" '
                f'height="{fmt(threshold_y-top)}" fill="#fff1f2" opacity="0.7"/>',
                f'<path d="M{fmt(left)} {fmt(threshold_y)} H{fmt(right)}" stroke="#be123c" '
                'stroke-width="1.5" stroke-dasharray="5 4"/>',
                f'<text x="{fmt(right)}" y="{fmt(threshold_y-5)}" text-anchor="end" font-size="9" '
                'fill="#9f1239" aria-hidden="true">SLO threshold</text>',
            ]
        )
    else:
        path = (
            f"M{fmt(left)} {fmt(top + height * 0.74)} "
            f"C{fmt(left + (right-left)*0.2)} {fmt(top + height*0.2)} "
            f"{fmt(left + (right-left)*0.42)} {fmt(top + height*0.82)} "
            f"{fmt(left + (right-left)*0.6)} {fmt(mid)} "
            f"S{fmt(right - (right-left)*0.12)} {fmt(top + height*0.18)} {fmt(right)} {fmt(top + height*0.28)}"
        )
    parts = [
        f'<g id="{esc(module_id)}-line-plot" class="asset-line-plot">',
        f'<path d="M{fmt(left)} {fmt(visual_bottom)} H{fmt(right)}" stroke="#d6dce8"/>',
        *extra_layers,
        f'<path d="{path}" fill="none" stroke="#94a3b8" stroke-width="2.5"/>',
    ]
    if marks:
        cell_width = (right - left) / len(marks)
        for index, info in enumerate(marks):
            parts.append(
                render_mark(
                    plan,
                    module_id,
                    info,
                    (left + index * cell_width + 2, top + 5, cell_width - 4, height - 10),
                )
            )
    parts.append("</g>")
    parts.append(render_text_rail(module_id, texts, width, visual_bottom + 8 if marks else top, bottom))
    return "".join(parts)


def render_flow_family(
    plan: dict[str, Any], module: dict[str, Any], infos: list[BindingInfo]
) -> str:
    module_id = module["id"]
    width = float(module["region"][2])
    top, visual_bottom, bottom, marks, texts = split_body(module, infos)
    left, right = 26.0, width - 26.0
    source_x = left + min(54.0, (right - left) * 0.12)
    source_info = marks[0] if marks else None
    branch_marks = marks[1:] if source_info is not None else []
    residual_texts = [info for info in texts if "residual" in info.role or "flex" in info.role]
    branches = [*branch_marks, *residual_texts]
    if not branches and source_info is not None:
        branches = [source_info]
        source_info = None
    flow_top = top + (28.0 if source_info is not None else 0.0)
    flow_height = max(24.0, visual_bottom - flow_top)
    flow_center_y = flow_top + flow_height / 2
    source_node_width = max(22.0, source_x - left)
    branch_unit_scale = rendered_units_per_raw(branch_marks[0]) if branch_marks else 1.0
    branch_extent = max((max_positive_extent(info, plan) for info in branch_marks), default=1.0)
    lane_height = flow_height / max(1, len(branches))
    max_stroke = max(7.0, min(28.0, lane_height * 0.42))
    stroke_scale = positive_scale(max_stroke, branch_extent)
    branch_specs: list[tuple[BindingInfo, float, float, bool]] = []
    for info in branches:
        value_scale = 1.0 if info.channel != "text" else branch_unit_scale
        signed_rendered = float(info.rendered) if info.channel != "text" else info.raw * value_scale
        magnitude = abs(signed_rendered)
        is_zero = info.raw == 0.0
        thickness = 0.0 if is_zero else min(max_stroke, max(2.5, magnitude * stroke_scale))
        branch_specs.append((info, value_scale, thickness, info.raw < 0.0))
    total_thickness = sum(item[2] for item in branch_specs)
    source_node_height = max(18.0, total_thickness)
    source_node_y = flow_center_y - source_node_height / 2
    reverse_marker_id = f"{module_id}-flow-reverse-arrow"
    source_base_label = binding_label(source_info, 22) if source_info else "Source"
    source_copy = (
        f"{source_base_label} · {source_info.accessible_value}"
        if source_info is not None
        else source_base_label
    )
    parts = [
        f'<g id="{esc(module_id)}-flow-plot" class="asset-flow-plot" data-sync-layout="flow" '
        f'data-flow-center-y="{fmt(flow_center_y)}" data-flow-source-x="{fmt(source_x)}" '
        f'data-flow-label-min-y="{fmt(top + 10)}" '
        f'data-flow-reverse-marker="url(#{esc(reverse_marker_id)})">',
        f'<defs><marker id="{esc(reverse_marker_id)}" viewBox="0 0 8 8" refX="7" refY="4" '
        f'markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0 L8 4 L0 8 Z" '
        f'fill="context-stroke"/></marker></defs>',
        f'<text data-flow-source-label="true" data-base-label="{esc(source_base_label)}" x="{fmt(left)}" '
        f'y="{fmt(max(top + 10, source_node_y - 8))}" font-size="10" font-weight="650" '
        f'fill="#475569" aria-hidden="true">{esc(source_copy)}</text>',
        f'<g data-flow-source="true"><rect data-flow-source-frame="true" x="{fmt(left)}" y="{fmt(source_node_y)}" '
        f'width="{fmt(source_node_width)}" height="{fmt(source_node_height)}" fill="#dbe4f1" rx="7"/>',
    ]
    if source_info is not None:
        if source_info.channel == "width":
            source_scale = positive_scale(
                source_node_width - 8, max_positive_extent(source_info, plan)
            )
            parts.append(
                f'<g data-flow-source-bound="true" data-layout-x="{fmt(left + 4)}" '
                f'data-layout-scale="{fmt_scale(source_scale)}" transform="translate({fmt(left + 4)} {fmt(flow_center_y)}) '
                f'scale({fmt_scale(source_scale)} 1)"><rect {common_attributes(module_id, source_info)} x="0" y="-5" '
                f'width="{fmt(max(0.5, float(source_info.rendered)))}" height="10" fill="{esc(source_info.color)}" '
                f'fill-opacity="0.9" rx="2"/></g>'
            )
        else:
            parts.append(render_mark(plan, module_id, source_info, (left + 2, source_node_y + 2, source_node_width - 4, source_node_height - 4)))
    parts.append("</g>")
    source_cursor = flow_center_y - total_thickness / 2
    for index, (info, value_scale, thickness, is_negative) in enumerate(branch_specs):
        center_y = flow_top + (index + 0.5) * lane_height
        source_start_y = source_cursor + thickness / 2
        source_cursor += thickness
        destination_x = right - min(112.0, (right - left) * 0.19)
        destination_height = max(28.0, lane_height * 0.4)
        destination_y = center_y - destination_height / 2
        destination_width = right - destination_x
        control_one_x = source_x + (right - left) * 0.18
        control_two_x = destination_x - (right - left) * 0.18
        forward_path = (
            f'M{fmt(source_x)} {fmt(source_start_y)} C{fmt(control_one_x)} '
            f'{fmt(source_start_y)} {fmt(control_two_x)} {fmt(center_y)} '
            f'{fmt(destination_x)} {fmt(center_y)}'
        )
        reverse_path = (
            f'M{fmt(destination_x)} {fmt(center_y)} C{fmt(control_two_x)} {fmt(center_y)} '
            f'{fmt(control_one_x)} {fmt(source_start_y)} {fmt(source_x)} {fmt(source_start_y)}'
        )
        direction = "zero" if thickness == 0 else ("reverse" if is_negative else "forward")
        negative_path_attrs = (
            f' stroke-dasharray="7 5" marker-end="url(#{esc(reverse_marker_id)})"'
            if is_negative
            else ""
        )
        parts.extend(
            [
                f'<g data-sync-layout-item="flow" data-layout-bound-role="{esc(info.role)}" '
                f'data-layout-value-scale="{fmt_scale(value_scale)}" data-layout-stroke-scale="{fmt_scale(stroke_scale)}" '
                f'data-layout-min-stroke="2.5" data-layout-max-stroke="{fmt(max_stroke)}" '
                f'data-flow-control-one-x="{fmt(control_one_x)}" data-flow-control-two-x="{fmt(control_two_x)}" '
                f'data-flow-destination-x="{fmt(destination_x)}" data-flow-destination-y="{fmt(center_y)}" '
                f'data-flow-forward-path="{forward_path}" data-flow-reverse-path="{reverse_path}" '
                f'data-flow-direction="{direction}">',
                f'<path d="{reverse_path if is_negative else forward_path}" data-sync-flow-path="{index}" fill="none" '
                f'stroke="{esc(info.color)}" stroke-opacity="0.44" stroke-width="{fmt(thickness)}" '
                f'stroke-linecap="round"{negative_path_attrs}/>',
                f'<rect x="{fmt(destination_x)}" y="{fmt(destination_y)}" '
                f'width="{fmt(destination_width)}" height="{fmt(destination_height)}" fill="#edf1f7" rx="5"/>',
                f'<rect x="{fmt(destination_x + 3)}" y="{fmt(destination_y + 3)}" width="12" '
                f'height="{fmt(destination_height - 6)}" fill="{esc(info.color)}" fill-opacity="0.18" rx="3"/>',
            ]
        )
        if info.channel != "text":
            parts.append(
                render_mark(
                    plan,
                    module_id,
                    info,
                    (destination_x + 4, destination_y + 4, 10, destination_height - 8),
                )
            )
        parts.extend(
            [
                f'<text data-flow-branch-label="true" data-base-label="{esc(binding_label(info, 20))}" '
                f'x="{fmt(destination_x + 20)}" y="{fmt(center_y - 1)}" '
                f'font-size="10" font-weight="650" fill="#475569" '
                f'aria-hidden="true">{esc(binding_label(info, 20))}</text>',
                f'<text data-flow-value-label="true" data-flow-value-role="{esc(info.role)}" '
                f'x="{fmt(destination_x + 20)}" y="{fmt(center_y + 12)}" font-size="10" '
                f'font-weight="650" fill="#334155" aria-hidden="true">{esc(info.accessible_value)}</text>',
                f'<text data-flow-sign-label="true" x="{fmt(destination_x + 20)}" y="{fmt(center_y + 24)}" '
                f'font-size="10" font-weight="700" fill="#9f1239" aria-hidden="true">'
                f'{"DEFICIT" if is_negative else ""}</text>',
                "</g>",
            ]
        )
    parts.append("</g>")
    parts.append(render_text_rail(module_id, texts, width, visual_bottom + 8 if marks else top, bottom))
    return "".join(parts)


def percentage_semantics(info: BindingInfo) -> tuple[float, float] | None:
    """Return the raw 100% target and display multiplier for percentage units."""

    if info.unit == "fraction":
        return (1.0, 100.0)
    if info.unit in {"percent", "%"}:
        return (100.0, 1.0)
    return None


def percentage_label(value: float, multiplier: float) -> str:
    scaled = float(value) * multiplier
    digits = 0 if abs(scaled - round(scaled)) < 1e-9 else 1
    return f"{scaled:.{digits}f}%"


def percent_target_x(
    plan: dict[str, Any], info: BindingInfo, left: float, right: float
) -> float | None:
    semantics = percentage_semantics(info)
    if semantics is None:
        return None
    target, _ = semantics
    transform = info.binding.get("transform")
    if not isinstance(transform, dict) or transform.get("op") != "linear":
        return None
    domain = transform.get("domain")
    target_range = transform.get("range")
    if not isinstance(domain, list) or len(domain) != 2 or not isinstance(target_range, list) or len(target_range) != 2:
        return None
    first, second = float(domain[0]), float(domain[1])
    if first == second or target < min(first, second) or target > max(first, second):
        return None
    t = (target - first) / (second - first)
    rendered = float(target_range[0]) + t * (float(target_range[1]) - float(target_range[0]))
    extent = max_positive_extent(info, plan)
    scale = positive_scale(right - left - 2, extent)
    position = left + 1 + rendered * scale
    return min(max(position, left + 1), right - 1)


def render_gauge_family(
    plan: dict[str, Any], module: dict[str, Any], infos: list[BindingInfo]
) -> str:
    module_id = module["id"]
    width = float(module["region"][2])
    top, visual_bottom, bottom, marks, texts = split_body(module, infos)
    left, right = 24.0, width - 24.0
    plot_height = max(28.0, visual_bottom - top)
    transform_marks = [info for info in marks if info.channel == "transform"]
    other_marks = [info for info in marks if info.channel != "transform"]
    target_assets = {"bullet", "progress"}
    show_percent_target = any(token in module["assetType"].lower() for token in target_assets)
    progress_info = next((info for info in other_marks if info.channel == "width"), None) if show_percent_target else None
    progress_domain = None
    progress_multiplier = None
    if progress_info is not None:
        transform = progress_info.binding.get("transform")
        domain = transform.get("domain") if isinstance(transform, dict) else None
        semantics = percentage_semantics(progress_info)
        if isinstance(domain, list) and len(domain) == 2 and semantics is not None:
            target, progress_multiplier = semantics
            if min(float(domain[0]), float(domain[1])) <= target <= max(float(domain[0]), float(domain[1])):
                progress_domain = [float(domain[0]), float(domain[1])]
    progress_attrs = (
        f' data-sync-layout="progress" data-layout-bound-role="{esc(progress_info.role)}" '
        f'data-layout-target-value="{fmt(1.0 if progress_info.unit == "fraction" else 100.0)}" '
        f'data-layout-max-value="{fmt(max(progress_domain) if progress_domain is not None else 0.0)}"'
        if progress_info is not None and progress_domain is not None
        else ""
    )
    parts = [f'<g id="{esc(module_id)}-gauge-plot" class="asset-gauge-plot"{progress_attrs}>']
    if transform_marks:
        for info in transform_marks:
            transform = info.binding.get("transform")
            domain = transform.get("domain") if isinstance(transform, dict) else None
            target_range = transform.get("range") if isinstance(transform, dict) else None
            valid_semicircle = (
                isinstance(transform, dict)
                and transform.get("op") == "rotate"
                and isinstance(domain, list)
                and len(domain) == 2
                and float(domain[0]) < float(domain[1])
                and isinstance(target_range, list)
                and len(target_range) == 2
                and abs((float(target_range[1]) - float(target_range[0])) - 180.0) < 1e-9
                and abs((float(target_range[0]) % 360.0) - 180.0) < 1e-9
                and abs(float(target_range[1]) % 360.0) < 1e-9
            )
            if not valid_semicircle:
                raise CompositionError(
                    f"module {module_id!r} renders a left-to-right semicircle; transform binding "
                    f"{info.role!r} must use an increasing domain and rotate range [-180, 0] "
                    "(or the equivalent [180, 360])"
                )
        center_x = (left + right) / 2
        center_y = top + plot_height * 0.9
        radius = max(22.0, min((right-left)*0.36, plot_height*0.86))
        parts.extend(
            [
                f'<path d="M{fmt(center_x-radius)} {fmt(center_y)} A{fmt(radius)} {fmt(radius)} 0 0 1 '
                f'{fmt(center_x+radius)} {fmt(center_y)}" fill="none" stroke="#dbe2ec" stroke-width="10" '
                f'stroke-linecap="round"/>',
                f'<path d="M{fmt(center_x-radius)} {fmt(center_y)} A{fmt(radius)} {fmt(radius)} 0 0 1 '
                f'{fmt(center_x+radius)} {fmt(center_y)}" fill="none" stroke="#94a3b8" stroke-width="2" '
                f'stroke-dasharray="2 8"/>',
            ]
        )
        for info in transform_marks:
            transform = info.binding.get("transform")
            center = transform.get("center", [0, 0]) if isinstance(transform, dict) else [0, 0]
            cx, cy = float(center[0]), float(center[1])
            dx, dy = center_x - cx, center_y - cy
            needle_length = radius * 0.78
            parts.append(
                f'<g transform="translate({fmt(dx)} {fmt(dy)})"><g {common_attributes(module_id, info)} '
                f'transform="{esc(info.rendered)}"><line x1="{fmt(cx)}" y1="{fmt(cy)}" '
                f'x2="{fmt(cx + needle_length)}" y2="{fmt(cy)}" stroke="{esc(info.color)}" '
                f'stroke-width="5" stroke-linecap="round"/><circle cx="{fmt(cx)}" cy="{fmt(cy)}" '
                f'r="6" fill="{esc(info.color)}"/></g></g>'
            )
        first_transform = transform_marks[0].binding.get("transform")
        domain = first_transform.get("domain") if isinstance(first_transform, dict) else None
        if isinstance(domain, list) and len(domain) == 2:
            semantics = percentage_semantics(transform_marks[0])
            multiplier = semantics[1] if semantics is not None else 1.0
            parts.extend(
                [
                    f'<text x="{fmt(center_x - radius)}" y="{fmt(center_y + 16)}" font-size="10" '
                    f'fill="#637087">{esc(percentage_label(float(domain[0]), multiplier))}</text>',
                    f'<text x="{fmt(center_x + radius)}" y="{fmt(center_y + 16)}" text-anchor="end" '
                    f'font-size="10" fill="#637087">{esc(percentage_label(float(domain[1]), multiplier))}</text>',
                ]
            )
    if other_marks:
        lane_top = top if not transform_marks else top + plot_height * 0.74
        lane_height = max(14.0, (visual_bottom - lane_top) / len(other_marks))
        for index, info in enumerate(other_marks):
            y = lane_top + index * lane_height
            track_y = y + lane_height * 0.25
            track_height = max(8.0, lane_height * 0.5)
            parts.append(
                f'<rect x="{fmt(left)}" y="{fmt(track_y)}" width="{fmt(right-left)}" '
                f'height="{fmt(track_height)}" fill="#e8edf5" rx="4"/>'
            )
            parts.append(
                render_mark(plan, module_id, info, (left, y, right-left, lane_height))
            )
            target_x = percent_target_x(plan, info, left, right) if show_percent_target and info.channel == "width" else None
            if target_x is not None:
                parts.extend(
                    [
                        f'<line class="percent-target-marker" data-target-ratio="1" '
                        f'x1="{fmt(target_x)}" y1="{fmt(track_y - 5)}" x2="{fmt(target_x)}" '
                        f'y2="{fmt(track_y + track_height + 5)}" stroke="#b45309" stroke-width="2" '
                        f'aria-label="100% target"/>',
                        f'<text x="{fmt(target_x)}" y="{fmt(max(top + 8, track_y - 8))}" text-anchor="middle" '
                        f'font-size="10" font-weight="650" fill="#92400e" aria-hidden="true">100% target</text>',
                    ]
                )
                if progress_domain is not None and progress_multiplier is not None:
                    readout_y = min(visual_bottom - 2, track_y + track_height + 14)
                    current_copy = f"{percentage_label(info.raw, progress_multiplier)} current"
                    maximum_copy = f"{percentage_label(max(progress_domain), progress_multiplier)} max"
                    parts.extend(
                        [
                            f'<text data-progress-current="true" x="{fmt(left)}" y="{fmt(readout_y)}" '
                            f'font-size="10" font-weight="650" fill="#475569">{esc(current_copy)}</text>',
                            f'<text x="{fmt(right)}" y="{fmt(readout_y)}" text-anchor="end" font-size="10" '
                            f'fill="#637087">{esc(maximum_copy)}</text>',
                        ]
                    )
    parts.append("</g>")
    parts.append(render_text_rail(module_id, texts, width, visual_bottom + 8 if marks else top, bottom))
    return "".join(parts)


def render_spatial_family(
    plan: dict[str, Any], module: dict[str, Any], infos: list[BindingInfo]
) -> str:
    module_id = module["id"]
    width = float(module["region"][2])
    top, visual_bottom, bottom, marks, texts = split_body(module, infos)
    left, right = 24.0, width - 24.0
    plot_height = max(28.0, visual_bottom - top)
    parts = [f'<g id="{esc(module_id)}-spatial-plot" class="asset-spatial-plot">']
    asset = module["assetType"].lower()
    if "gpu" in asset or "fabric" in asset:
        hub_x = (left + right) / 2
        hub_y = top + plot_height / 2
        node_width = min(74.0, (right - left) * 0.2)
        node_height = min(46.0, plot_height * 0.24)
        nodes = [
            (left + 8.0, top + 8.0, "g1"),
            (right - node_width - 8.0, top + 8.0, "g2"),
            (left + 8.0, visual_bottom - node_height - 8.0, "g3"),
            (right - node_width - 8.0, visual_bottom - node_height - 8.0, "g4"),
        ]
        for node_x, node_y, label in nodes:
            parts.append(
                f'<line x1="{fmt(hub_x)}" y1="{fmt(hub_y)}" '
                f'x2="{fmt(node_x + node_width/2)}" y2="{fmt(node_y + node_height/2)}" '
                'stroke="#b8c5d8" stroke-width="2"/>'
            )
            parts.append(
                f'<rect x="{fmt(node_x)}" y="{fmt(node_y)}" width="{fmt(node_width)}" '
                f'height="{fmt(node_height)}" fill="{("#dbeafe" if label == "g3" else "#e8edf5")}" '
                f'stroke="{("#2563eb" if label == "g3" else "#cbd5e1")}" rx="5"/>'
            )
            parts.append(
                f'<text x="{fmt(node_x + node_width/2)}" y="{fmt(node_y + node_height/2 + 4)}" '
                f'text-anchor="middle" font-size="10" font-weight="700" fill="#475569" '
                f'aria-hidden="true">{label}</text>'
            )
        parts.extend(
            [
                f'<circle cx="{fmt(hub_x)}" cy="{fmt(hub_y)}" r="15" fill="#64748b"/>',
                f'<text x="{fmt(hub_x)}" y="{fmt(hub_y + 31)}" text-anchor="middle" '
                'font-size="9" fill="#637087" aria-hidden="true">batch router</text>',
            ]
        )
    else:
        columns, rows = 5, 3
        cell_width, cell_height = (right-left)/columns, plot_height/rows
        for row in range(rows):
            for column in range(columns):
                inset = 2 + ((row + column) % 2)
                parts.append(
                    f'<rect x="{fmt(left+column*cell_width+inset)}" y="{fmt(top+row*cell_height+inset)}" '
                    f'width="{fmt(cell_width-inset*2)}" height="{fmt(cell_height-inset*2)}" '
                    f'fill="{("#e2e8f0" if (row+column)%3 else "#d5deeb")}" rx="5"/>'
                )
    if marks:
        cell = (right-left)/len(marks)
        for index, info in enumerate(marks):
            parts.append(render_mark(plan, module_id, info, (left+index*cell, top, cell, plot_height)))
    parts.append("</g>")
    parts.append(render_text_rail(module_id, texts, width, visual_bottom + 8 if marks else top, bottom))
    return "".join(parts)


def render_table_family(
    plan: dict[str, Any], module: dict[str, Any], infos: list[BindingInfo]
) -> str:
    module_id = module["id"]
    width = float(module["region"][2])
    top, _visual_bottom, bottom, marks, texts = split_body(module, infos)
    parts = [f'<g id="{esc(module_id)}-table-plot" class="asset-table-plot">']
    asset = module["assetType"].lower()
    parts.append(
        f'<rect x="22" y="{fmt(top)}" width="{fmt(width-44)}" height="{fmt(max(18.0,bottom-top))}" '
        f'fill="#f8fafc" stroke="#e2e8f0" rx="6"/>'
    )
    if "attention" in asset:
        field_left = 28.0
        field_top = top + 8.0
        field_width = width - 56.0
        field_height = max(54.0, (bottom - top) * 0.52)
        columns = 10
        rows = 6
        cell_width = field_width / columns
        cell_height = field_height / rows
        for row in range(rows):
            for column in range(columns):
                distance = abs(column - (row * 1.45 + 1.0))
                opacity = max(0.1, min(0.9, 0.88 - distance * 0.12))
                parts.append(
                    f'<rect x="{fmt(field_left + column * cell_width + 1)}" '
                    f'y="{fmt(field_top + row * cell_height + 1)}" '
                    f'width="{fmt(max(1.0, cell_width - 2))}" '
                    f'height="{fmt(max(1.0, cell_height - 2))}" fill="#2563eb" '
                    f'fill-opacity="{fmt(opacity)}" rx="1"/>'
                )
        parts.append(
            f'<text x="{fmt(field_left)}" y="{fmt(field_top - 1)}" font-size="9" '
            'fill="#637087" aria-hidden="true">prompt → evidence attention</text>'
        )
        rail_top = field_top + field_height + 7.0
        parts.append(render_text_rail(module_id, texts, width, rail_top, bottom, table=True))
        parts.append("</g>")
        return "".join(parts)
    if "context" in asset:
        field_left = 28.0
        field_top = top + 8.0
        field_width = width - 56.0
        field_height = max(50.0, (bottom - top) * 0.5)
        columns = 12
        rows = 3
        cell_width = field_width / columns
        cell_height = field_height / rows
        for row in range(rows):
            for column in range(columns):
                index = row * columns + column
                fill = "#2563eb" if index < 8 else ("#7c3aed" if index < 16 else "#e2e8f0")
                opacity = 0.78 if index < 16 else 1.0
                parts.append(
                    f'<rect x="{fmt(field_left + column * cell_width + 1)}" '
                    f'y="{fmt(field_top + row * cell_height + 1)}" '
                    f'width="{fmt(max(1.0, cell_width - 2))}" '
                    f'height="{fmt(max(1.0, cell_height - 2))}" fill="{fill}" '
                    f'fill-opacity="{fmt(opacity)}" rx="1"/>'
                )
        parts.append(
            f'<text x="{fmt(field_left)}" y="{fmt(field_top - 1)}" font-size="9" '
            'fill="#637087" aria-hidden="true">prompt · retrieved · free capacity</text>'
        )
        rail_top = field_top + field_height + 7.0
        parts.append(render_text_rail(module_id, texts, width, rail_top, bottom, table=True))
        parts.append("</g>")
        return "".join(parts)
    if marks:
        mark_height = min(28.0, max(16.0, (bottom-top)*0.25))
        cell = (width-48)/len(marks)
        for index, info in enumerate(marks):
            parts.append(render_mark(plan, module_id, info, (24+index*cell, top+4, cell-2, mark_height)))
        rail_top = top + mark_height + 7
    else:
        rail_top = top + 2
    parts.append(render_text_rail(module_id, texts, width, rail_top, bottom, table=True))
    parts.append("</g>")
    return "".join(parts)


def render_network_family(
    plan: dict[str, Any], module: dict[str, Any], infos: list[BindingInfo]
) -> str:
    module_id = module["id"]
    width = float(module["region"][2])
    top, visual_bottom, bottom, marks, texts = split_body(module, infos)
    left, right = 26.0, width - 26.0
    plot_height = max(28.0, visual_bottom - top)
    center_x, center_y = (left+right)/2, top+plot_height/2
    parts = [f'<g id="{esc(module_id)}-network-plot" class="asset-network-plot">']
    if texts and not marks:
        # A compact network is a dependency overview, not a shared quantitative
        # scale. Equal-area cards plus exact readouts avoid comparing unlike
        # units, while edges come only from the declared derived-value DAG.
        content_height = float(scaffold.module_content_geometry(module)[4])
        order = {info.value_id: index for index, info in enumerate(texts)}
        included = set(order)
        derived_by_id = {item["id"]: item for item in plan.get("derived", [])}
        dependencies = {
            value_id: [
                dependency
                for dependency in derived_by_id.get(value_id, {}).get("dependsOn", [])
                if dependency in included
            ]
            for value_id in included
        }
        edges = [
            (dependency, value_id)
            for value_id in included
            for dependency in dependencies[value_id]
        ]
        if not edges:
            raise CompositionError(
                f"network module {module_id!r} has no declared dependency edge among its values"
            )

        depth_cache: dict[str, int] = {}

        def depth(value_id: str) -> int:
            if value_id in depth_cache:
                return depth_cache[value_id]
            parents = dependencies[value_id]
            result = 0 if not parents else 1 + max(depth(parent) for parent in parents)
            depth_cache[value_id] = result
            return result

        levels: dict[int, list[BindingInfo]] = {}
        for info in texts:
            levels.setdefault(depth(info.value_id), []).append(info)
        level_ids = sorted(levels)
        left_edge, right_edge = 22.0, width - 22.0
        top_edge, bottom_edge = 8.0, max(68.0, content_height - 10.0)
        available_width = right_edge - left_edge
        available_height = bottom_edge - top_edge
        column_count = len(level_ids)
        horizontal_gap = min(22.0, max(8.0, available_width * 0.03))
        card_width = min(
            188.0,
            max(1.0, (available_width - horizontal_gap * (column_count - 1)) / column_count),
        )
        max_rows = max(len(levels[level_id]) for level_id in level_ids)
        vertical_gap = min(9.0, max(3.0, available_height * 0.025))
        card_height = min(
            58.0,
            max(1.0, (available_height - vertical_gap * (max_rows - 1)) / max_rows),
        )
        if column_count == 1:
            column_centers = [(left_edge + right_edge) / 2]
        else:
            first_center = left_edge + card_width / 2
            last_center = right_edge - card_width / 2
            column_centers = [
                first_center + (last_center - first_center) * index / (column_count - 1)
                for index in range(column_count)
            ]
        positions: dict[str, tuple[float, float]] = {}
        for column_index, level_id in enumerate(level_ids):
            level_infos = sorted(levels[level_id], key=lambda info: order[info.value_id])
            level_height = len(level_infos) * card_height + (len(level_infos) - 1) * vertical_gap
            start_y = top_edge + (available_height - level_height) / 2
            for row_index, info in enumerate(level_infos):
                positions[info.value_id] = (
                    column_centers[column_index] - card_width / 2,
                    start_y + row_index * (card_height + vertical_gap),
                )

        marker_id = f"{module_id}-dependency-arrow"
        parts.append(
            f'<defs><marker id="{esc(marker_id)}" viewBox="0 0 8 8" refX="7" refY="4" '
            'markerWidth="6" markerHeight="6" orient="auto-start-reverse">'
            '<path d="M0 0 L8 4 L0 8 Z" fill="#526176"/></marker></defs>'
        )
        for source_id, target_id in sorted(edges, key=lambda edge: (order[edge[1]], order[edge[0]])):
            source_x, source_y = positions[source_id]
            target_x, target_y = positions[target_id]
            x1 = source_x + card_width
            y1 = source_y + card_height / 2
            x2 = target_x
            y2 = target_y + card_height / 2
            control = (x1 + x2) / 2
            parts.append(
                f'<path d="M{fmt(x1)} {fmt(y1)} C{fmt(control)} {fmt(y1)} '
                f'{fmt(control)} {fmt(y2)} {fmt(x2)} {fmt(y2)}" fill="none" '
                f'stroke="#526176" stroke-width="1.8" marker-end="url(#{esc(marker_id)})" '
                f'data-dependency-edge="{esc(source_id)}:{esc(target_id)}"/>'
            )
        for info in texts:
            x, y = positions[info.value_id]
            dense = card_height < 42.0
            label_y = y + min(16.0, max(8.0, card_height * 0.34))
            value_y = y + min(card_height - 4.0, max(18.0, card_height * 0.76))
            label_limit = max(8, min(24, int(card_width / 6.0)))
            parts.append(
                f'<rect x="{fmt(x)}" y="{fmt(y)}" width="{fmt(card_width)}" '
                f'height="{fmt(card_height)}" fill="#ffffff" stroke="{esc(info.color)}" '
                'stroke-width="2" rx="8"/>'
            )
            parts.append(
                f'<text x="{fmt(x + card_width / 2)}" y="{fmt(label_y)}" '
                f'text-anchor="middle" font-size="{8 if dense else 10}" fill="#475569" aria-hidden="true">'
                f'{esc(binding_label(info, label_limit))}</text>'
            )
            parts.append(
                render_text_binding(
                    module_id,
                    info,
                    x + card_width / 2,
                    value_y,
                    anchor="middle",
                    font_size=9.0 if dense else 11.0,
                )
            )
        parts.append("</g>")
        return "".join(parts)
    if marks:
        cell = (right-left)/len(marks)
        for index in range(len(marks)):
            px = left + (index + 0.5) * cell
            parts.append(
                f'<line x1="{fmt(center_x)}" y1="{fmt(center_y)}" x2="{fmt(px)}" y2="{fmt(center_y)}" '
                f'stroke="#cbd5e1" stroke-width="2"/>'
            )
    else:
        parts.append(
            f'<circle cx="{fmt(center_x)}" cy="{fmt(center_y)}" r="38" fill="none" '
            f'stroke="#cbd5e1" stroke-width="2" stroke-dasharray="5 5"/>'
        )
    parts.append(f'<circle cx="{fmt(center_x)}" cy="{fmt(center_y)}" r="10" fill="#94a3b8"/>')
    if marks:
        for index, info in enumerate(marks):
            parts.append(render_mark(plan, module_id, info, (left+index*cell, top, cell, plot_height)))
            parts.append(
                f'<text x="{fmt(left + (index + 0.5) * cell)}" '
                f'y="{fmt(center_y + min(68.0, plot_height * 0.28))}" '
                f'text-anchor="middle" font-size="10" fill="#475569" aria-hidden="true">'
                f'{esc(binding_label(info, 22))}</text>'
            )
    parts.append("</g>")
    parts.append(render_text_rail(module_id, texts, width, visual_bottom + 8 if marks else top, bottom))
    return "".join(parts)


def render_fallback_family(
    plan: dict[str, Any], module: dict[str, Any], infos: list[BindingInfo]
) -> str:
    module_id = module["id"]
    width = float(module["region"][2])
    top, visual_bottom, bottom, marks, texts = split_body(module, infos)
    left, right = 24.0, width - 24.0
    parts = [f'<g id="{esc(module_id)}-facet-plot" class="asset-facet-plot">']
    if marks:
        columns = 2 if len(marks) > 1 else 1
        rows = math.ceil(len(marks)/columns)
        cell_width, cell_height = (right-left)/columns, max(16.0,(visual_bottom-top)/rows)
        for index, info in enumerate(marks):
            row, column = divmod(index, columns)
            x, y = left+column*cell_width, top+row*cell_height
            parts.append(
                f'<rect x="{fmt(x+2)}" y="{fmt(y+2)}" width="{fmt(cell_width-4)}" '
                f'height="{fmt(cell_height-4)}" fill="#f1f5f9" stroke="#e2e8f0" rx="7"/>'
            )
            parts.append(render_mark(plan, module_id, info, (x+6,y+6,cell_width-12,cell_height-12)))
    parts.append("</g>")
    parts.append(render_text_rail(module_id, texts, width, visual_bottom + 8 if marks else top, bottom))
    return "".join(parts)


RENDERERS = {
    "bar": render_bar_family,
    "waterfall": render_waterfall_family,
    "line": render_line_family,
    "flow": render_flow_family,
    "gauge": render_gauge_family,
    "spatial": render_spatial_family,
    "table": render_table_family,
    "network": render_network_family,
    "fallback": render_fallback_family,
}


def module_fragment(
    plan: dict[str, Any],
    module: dict[str, Any],
    values: dict[str, float],
    colors: dict[str, str],
) -> tuple[str, str]:
    family = family_for(module["assetType"])
    infos = binding_infos(plan, module, values, colors)
    body = RENDERERS[family](plan, module, infos)
    module_id = module["id"]
    _, _, top, body_width, body_height = scaffold.module_content_geometry(module)
    fragment = (
        f'<g xmlns="{SVG_NS}" class="module-content" transform="translate(0 {fmt(top)})" '
        f'data-module-content-for="{esc(module_id)}" data-content-origin="0 {fmt(top)}" '
        f'data-content-width="{fmt(body_width)}" data-content-height="{fmt(body_height)}" '
        f'data-renderer-family="{esc(family)}" '
        f'aria-label="{esc(module["assetType"].replace("-", " "))} visualization">'
        f'<title>{esc(module["assetType"].replace("-", " ").title())} for {esc(short_label(module_id, 40))}</title>'
        f'<g id="{esc(module_id)}-content" class="asset-{family}">{body}</g></g>\n'
    )
    return family, fragment


def local_name(name: str) -> str:
    return name.rsplit("}", 1)[-1]


def verify_finished_svg(path: Path, expected_modules: int) -> None:
    try:
        root = ET.fromstring(path.read_bytes())
    except ET.ParseError as exc:
        raise CompositionError(f"finished SVG is not well-formed XML: {exc}") from exc
    if local_name(root.tag) != "svg":
        raise CompositionError("finished document root is not SVG")
    modules = [
        element
        for element in root.iter()
        if isinstance(element.tag, str) and element.get("data-module-id") is not None
    ]
    if len(modules) != expected_modules:
        raise CompositionError(
            f"finished SVG has {len(modules)} modules; expected {expected_modules}"
        )
    leftovers: list[str] = []
    forbidden_classes = {"module-placeholder", "placeholder-mark", "placeholder-value"}
    for element in root.iter():
        if not isinstance(element.tag, str):
            continue
        if element.get("data-placeholder") is not None:
            leftovers.append(element.get("id") or local_name(element.tag))
        if set(element.get("class", "").split()) & forbidden_classes:
            leftovers.append(element.get("id") or element.get("class", ""))
    if leftovers:
        raise CompositionError(f"finished SVG still contains placeholder artifacts: {leftovers[:8]}")


def check_destinations(args: argparse.Namespace) -> tuple[Path, Path | None]:
    spec = args.spec.resolve()
    output = args.output.resolve()
    report = args.report.resolve() if args.report else None
    if output == spec:
        raise CompositionError("--output must not overwrite --spec")
    if report is not None and report in {spec, output}:
        raise CompositionError("--report must differ from --spec and --output")
    conflicts = [path for path in (output, report) if path is not None and path.exists()]
    if conflicts and not args.force:
        raise CompositionError(f"destination already exists; pass --force to replace it: {conflicts[0]}")
    return output, report


def is_transient_access_error(error: OSError) -> bool:
    return (
        isinstance(error, PermissionError)
        or getattr(error, "winerror", None) in {5, 32}
        or getattr(error, "errno", None) in {1, 13}
    )


def retry_transient_access(
    operation: Any,
    label: str,
    *,
    attempts: int = 6,
    initial_delay: float = 0.025,
    sleep_func: Any = None,
) -> Any:
    """Retry only access-sharing failures; every operation must be atomic or idempotent."""

    if attempts < 1:
        raise ValueError("retry attempts must be positive")
    sleeper = time.sleep if sleep_func is None else sleep_func
    for attempt in range(attempts):
        try:
            return operation()
        except OSError as exc:
            if not is_transient_access_error(exc) or attempt + 1 >= attempts:
                raise
            sleeper(initial_delay * (attempt + 1))
    raise CompositionError(f"{label} retry loop ended unexpectedly")  # pragma: no cover


def atomic_write_with_retry(path: Path, data: bytes, mode: int) -> None:
    retry_transient_access(
        lambda: replacer.atomic_write(path, data, mode),
        f"atomic write for {path}",
    )


def replace_with_retry(
    source: Path,
    destination: Path,
    *,
    attempts: int = 6,
    initial_delay: float = 0.025,
    replace_func: Any = None,
    sleep_func: Any = None,
) -> None:
    replace_operation = os.replace if replace_func is None else replace_func
    retry_transient_access(
        lambda: replace_operation(source, destination),
        f"promotion to {destination}",
        attempts=attempts,
        initial_delay=initial_delay,
        sleep_func=sleep_func,
    )


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    data = (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("utf-8")
    mode = path.stat().st_mode if path.exists() else stat.S_IFREG | 0o644
    atomic_write_with_retry(path, data, mode)


COMPOSER_LAYOUT_RUNTIME = r'''  function layoutFlow(plot, group) {
    const sourceLabel = plot.querySelector("[data-flow-source-label]");
    const sourceMark = plot.querySelector("[data-flow-source-bound] [data-bind]");
    if (sourceLabel && sourceMark) {
      const base = sourceLabel.dataset.baseLabel || "Source";
      const value = sourceMark.dataset.accessibleValue || sourceMark.dataset.currentValue || "";
      sourceLabel.textContent = value ? `${base} · ${value}` : base;
    }
    const items = [...plot.querySelectorAll('[data-sync-layout-item="flow"]')];
    const branchStates = items.map((item) => {
      const role = item.dataset.layoutBoundRole;
      const mark = group.querySelector(`[data-role="${CSS.escape(role)}"]`);
      if (!mark) throw new Error("flow layout is missing binding target: " + role);
      const rendered = numeric(mark.style.getPropertyValue("--sync-rendered") || "0", "flow rendered value");
      const rawValue = numeric(mark.dataset.currentValue || "0", "flow canonical value");
      const scaled = Math.abs(rendered) * numeric(item.dataset.layoutValueScale, "flow value scale");
      const minimum = numeric(item.dataset.layoutMinStroke, "flow minimum stroke");
      const maximum = numeric(item.dataset.layoutMaxStroke, "flow maximum stroke");
      const zero = rawValue === 0;
      const thickness = zero
        ? 0
        : Math.min(maximum, Math.max(minimum, scaled * numeric(item.dataset.layoutStrokeScale, "flow stroke scale")));
      const path = item.querySelector("[data-sync-flow-path]");
      if (!path) throw new Error("flow layout item is missing its branch path");
      path.setAttribute("stroke-width", String(thickness));
      item.setAttribute("data-current-flow-thickness", String(thickness));
      item.setAttribute("data-flow-direction", zero ? "zero" : (rawValue < 0 ? "reverse" : "forward"));
      return {thickness, negative: !zero && rawValue < 0};
    });
    const thicknesses = branchStates.map((state) => state.thickness);
    const centerY = numeric(plot.dataset.flowCenterY, "flow center y");
    const sourceX = numeric(plot.dataset.flowSourceX, "flow source x");
    const total = thicknesses.reduce((sum, value) => sum + value, 0);
    const sourceHeight = Math.max(18, total);
    const sourceFrame = plot.querySelector("[data-flow-source-frame]");
    if (sourceFrame) {
      sourceFrame.setAttribute("y", String(centerY - sourceHeight / 2));
      sourceFrame.setAttribute("height", String(sourceHeight));
    }
    if (sourceLabel) {
      const minimumY = numeric(plot.dataset.flowLabelMinY, "flow label minimum y");
      sourceLabel.setAttribute("y", String(Math.max(minimumY, centerY - sourceHeight / 2 - 8)));
    }
    const sourceBound = plot.querySelector("[data-flow-source-bound]");
    if (sourceBound) {
      const x = numeric(sourceBound.dataset.layoutX, "flow source bound x");
      const scale = numeric(sourceBound.dataset.layoutScale, "flow source bound scale");
      sourceBound.setAttribute("transform", `translate(${x} ${centerY}) scale(${scale} 1)`);
    }
    let cursor = centerY - total / 2;
    items.forEach((item, index) => {
      const startY = cursor + thicknesses[index] / 2;
      cursor += thicknesses[index];
      const controlOneX = numeric(item.dataset.flowControlOneX, "flow control one x");
      const controlTwoX = numeric(item.dataset.flowControlTwoX, "flow control two x");
      const destinationX = numeric(item.dataset.flowDestinationX, "flow destination x");
      const destinationY = numeric(item.dataset.flowDestinationY, "flow destination y");
      const path = item.querySelector("[data-sync-flow-path]");
      if (branchStates[index].negative) {
        path.setAttribute(
          "d",
          `M${destinationX} ${destinationY} C${controlTwoX} ${destinationY} ${controlOneX} ${startY} ${sourceX} ${startY}`
        );
        path.setAttribute("stroke-dasharray", "7 5");
        path.setAttribute("marker-end", plot.dataset.flowReverseMarker);
      } else {
        path.setAttribute(
          "d",
          `M${sourceX} ${startY} C${controlOneX} ${startY} ${controlTwoX} ${destinationY} ${destinationX} ${destinationY}`
        );
        path.removeAttribute("stroke-dasharray");
        path.removeAttribute("marker-end");
      }
      const valueLabel = item.querySelector("[data-flow-value-label]");
      if (valueLabel) {
        const role = item.dataset.layoutBoundRole;
        const mark = group.querySelector(`[data-role="${CSS.escape(role)}"]`);
        valueLabel.textContent = mark?.dataset.accessibleValue || mark?.dataset.currentValue || "";
      }
      const signLabel = item.querySelector("[data-flow-sign-label]");
      if (signLabel) signLabel.textContent = branchStates[index].negative ? "DEFICIT" : "";
    });
  }
  function layoutProgress(plot, group) {
    const role = plot.dataset.layoutBoundRole;
    const mark = group.querySelector(`[data-role="${CSS.escape(role)}"]`);
    const readout = plot.querySelector("[data-progress-current]");
    if (!mark || !readout) throw new Error("progress layout is missing its binding or readout");
    const value = numeric(mark.style.getPropertyValue("--sync-value") || mark.dataset.currentValue, "progress value");
    const multiplier = mark.dataset.valueUnit === "percent" || mark.dataset.valueUnit === "%" ? 1 : 100;
    const percent = Math.round(value * multiplier * 10) / 10;
    readout.textContent = `${percent}% current`;
  }
  function layoutModule(group) {
    group.querySelectorAll('[data-sync-layout="stack"]').forEach(layoutStack);
    group.querySelectorAll('[data-sync-layout="waterfall"]').forEach(layoutWaterfall);
    group.querySelectorAll('[data-sync-layout="flow"]').forEach((plot) => layoutFlow(plot, group));
    group.querySelectorAll('[data-sync-layout="progress"]').forEach((plot) => layoutProgress(plot, group));
  }
'''


def finished_scaffold(plan: dict[str, Any]) -> bytes:
    """Promote the scaffold-owned status subtitle to final-deliverable copy."""

    draft = scaffold.build_svg(plan)
    source = "Synchronized semantic megacanvas · structural scaffold"
    requested = plan.get("subtitle")
    if requested is not None and (not isinstance(requested, str) or not requested.strip()):
        raise CompositionError("optional subtitle must be a non-empty string")
    target = requested.strip() if isinstance(requested, str) else (
        f"{len(plan['modules'])} coordinated views · {len(plan['scenarios'])} scenarios · one canonical state"
    )
    if draft.count(source) != 1:
        raise CompositionError("scaffold status subtitle contract changed unexpectedly")
    draft = draft.replace(source, scaffold.esc(target), 1)
    runtime_start = draft.find("  function layoutFlow(plot, group) {")
    runtime_end = draft.find("  function renderAll(changedValues = null) {", runtime_start)
    if runtime_start < 0 or runtime_end < 0:
        raise CompositionError("scaffold runtime layout hook contract changed unexpectedly")
    draft = draft[:runtime_start] + COMPOSER_LAYOUT_RUNTIME + draft[runtime_end:]
    return draft.encode("utf-8")


def compose(args: argparse.Namespace) -> dict[str, Any]:
    plan = scaffold.load_plan(args.spec)
    scaffold.validate_plan(plan)
    output, report_path = check_destinations(args)
    output.parent.mkdir(parents=True, exist_ok=True)
    if report_path is not None:
        report_path.parent.mkdir(parents=True, exist_ok=True)

    source, derived = scaffold.initial_values(plan)
    values = {**source, **derived}
    colors = source_color_map(plan)
    module_reports: list[dict[str, Any]] = []

    temporary_svg: Path | None = None
    try:
        descriptor, temporary_name = tempfile.mkstemp(
            prefix=f".{output.stem}-compose-", suffix=".svg", dir=output.parent
        )
        os.close(descriptor)
        temporary_svg = Path(temporary_name)
        scaffold_bytes = finished_scaffold(plan)
        atomic_write_with_retry(temporary_svg, scaffold_bytes, stat.S_IFREG | 0o644)

        with tempfile.TemporaryDirectory(prefix="sync-fragments-", dir=output.parent) as temp_directory:
            fragment_directory = Path(temp_directory)
            for module in plan["modules"]:
                family, fragment = module_fragment(plan, module, values, colors)
                fragment_path = fragment_directory / f"{module['id']}.svg"
                atomic_write_with_retry(
                    fragment_path,
                    fragment.encode("utf-8"),
                    stat.S_IFREG | 0o644,
                )
                replacement = retry_transient_access(
                    lambda module=module, fragment_path=fragment_path: replacer.replace(
                        SimpleNamespace(
                            module=module["id"],
                            svg=temporary_svg,
                            fragment=fragment_path,
                            in_place=True,
                            output=None,
                        )
                    ),
                    f"module replacement for {module['id']}",
                )
                module_reports.append(
                    {
                        "moduleId": module["id"],
                        "assetType": module["assetType"],
                        "family": family,
                        "bindingCount": replacement["bindingCount"],
                        "fragmentBytes": replacement["fragmentBytes"],
                    }
                )

        verify_finished_svg(temporary_svg, len(plan["modules"]))
        if output.exists() and not args.force:
            raise CompositionError(f"destination appeared during composition: {output}")
        replace_with_retry(temporary_svg, output)
        temporary_svg = None

        result = {
            "ok": True,
            "output": str(output),
            "report": str(report_path) if report_path else None,
            "compositionId": plan["compositionId"],
            "moduleCount": len(plan["modules"]),
            "sourceConceptCount": len(plan["concepts"]),
            "derivedConceptCount": len(plan.get("derived", [])),
            "bindingCount": sum(len(module["bindings"]) for module in plan["modules"]),
            "containsPlaceholders": False,
            "standalone": True,
            "outputBytes": output.stat().st_size,
            "modules": module_reports,
        }
        if report_path is not None:
            atomic_json(report_path, result)
        return result
    finally:
        if temporary_svg is not None:
            temporary_svg.unlink(missing_ok=True)


def main() -> int:
    args = parse_args()
    try:
        result = compose(args)
    except (OSError, ValueError, replacer.ReplacementError) as exc:
        result = {"ok": False, "error": str(exc)}
        if args.json:
            print(json.dumps(result, indent=2, sort_keys=True))
        else:
            print(f"Composition failed: {exc}", file=sys.stderr)
        return 1
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(f"Created final synchronized SVG: {result['output']}")
        if result["report"]:
            print(f"Wrote composition report: {result['report']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
