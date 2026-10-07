#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Validate a bounded offline Lucid Standard Import shape-property catalog.

Run: uv run --script scripts/native_catalog.py --type table
No network, account access, semantic inference, or service-render verification.
"""

from __future__ import annotations

import argparse
from copy import deepcopy
from functools import lru_cache
import html
import json
import math
from pathlib import Path
import re
import sys


CATALOG_PATH = Path(__file__).resolve().parent.parent / "references" / "native-shapes.json"
COLOR_PATTERN = re.compile(r"#(?:[0-9A-Fa-f]{3}|[0-9A-Fa-f]{4}|[0-9A-Fa-f]{6}|[0-9A-Fa-f]{8})\Z")


@lru_cache(maxsize=1)
def _catalog() -> dict:
    with CATALOG_PATH.open(encoding="utf-8") as stream:
        return json.load(stream)


def catalog_metadata() -> dict:
    """Return compact source and coverage metadata without the full payload."""
    catalog = _catalog()
    return {
        "schema_version": catalog["schema_version"],
        "observed_date": catalog["observed_date"],
        "source_urls": catalog["source_urls"],
        "native_type_count": len(catalog["types"]),
        "cloud_class_count": sum(len(lib["shape_classes"]) + len(lib["container_classes"])
                                 for lib in catalog["cloud_libraries"].values()),
        "service_verification": "not-tested",
    }


def spec(type_name: str) -> dict:
    """Return an independent spec, resolving explicit aliases only."""
    catalog = _catalog()
    if not isinstance(type_name, str):
        raise ValueError("Native type must be a string")
    alias = catalog["aliases"].get(type_name)
    actual = alias["actual_type"] if alias else type_name
    if actual not in catalog["types"]:
        route = catalog["unsupported_types"].get(type_name, {}).get("route")
        suffix = f"; preferred route: {route}" if route else "; inspect the documented catalog instead of inventing a type"
        raise ValueError(f"Unsupported native type {type_name!r}{suffix}")
    result = deepcopy(catalog["types"][actual])
    result["input_type"] = type_name
    if alias:
        result["alias"] = deepcopy(alias)
    return result


def native_type(type_name: str) -> str:
    """Return the exact emitted vendor type; ellipse is an explicit circle alias."""
    return spec(type_name)["actual_type"]


def cloud_class(class_name: str) -> dict:
    """Resolve a literal documented class with its shape/container kind."""
    if not isinstance(class_name, str):
        raise ValueError("className must be a string")
    catalog = _catalog()
    if class_name in catalog["cloud_conflicts"]:
        raise ValueError(f"className {class_name!r} requires verification: {catalog['cloud_conflicts'][class_name]['reason']}")
    for library_id, library in catalog["cloud_libraries"].items():
        for collection, type_name in (("shape_classes", "namedShape"), ("container_classes", "namedContainer")):
            if class_name in library[collection]:
                return {"className": class_name, "type": type_name, "library": library_id,
                        "provider": library["provider"], "revision": library["revision"],
                        "source_urls": deepcopy(library["source_urls"])}
    raise ValueError(f"Unsupported className {class_name!r}; use an exact verified catalog name, not a synthesized name")


def _number(value: object, label: str, rule: dict | None = None) -> int | float:
    rule = rule or {}
    if type(value) not in (int, float):
        raise ValueError(f"{label} must be a finite number, not a boolean or string")
    try:
        finite = math.isfinite(value)
    except OverflowError:
        finite = False
    if not finite:
        raise ValueError(f"{label} must be finite")
    if rule.get("integer") and value != int(value):
        raise ValueError(f"{label} must be an integer")
    if "minimum" in rule and value < rule["minimum"]:
        raise ValueError(f"{label} must be at least {rule['minimum']}")
    if "exclusive_minimum" in rule and value <= rule["exclusive_minimum"]:
        raise ValueError(f"{label} must be greater than {rule['exclusive_minimum']}")
    if "maximum" in rule and value > rule["maximum"]:
        raise ValueError(f"{label} must be at most {rule['maximum']}")
    return value


def _object(value: object, label: str, properties: dict, required: list[str]) -> dict:
    if not isinstance(value, dict):
        raise ValueError(f"{label} must be an object")
    if any(not isinstance(key, str) for key in value):
        raise ValueError(f"{label} property names must be strings")
    extra = set(value) - set(properties)
    missing = set(required) - set(value)
    if extra:
        raise ValueError(f"{label} has unsupported properties: {', '.join(sorted(extra))}")
    if missing:
        raise ValueError(f"{label} is missing required properties: {', '.join(sorted(missing))}")
    return value


def _validate_rule(value: object, rule: dict, label: str, type_name: str) -> object:
    kind = rule["kind"]
    if kind == "number":
        return _number(value, label, rule)
    if kind == "boolean":
        if type(value) is not bool:
            raise ValueError(f"{label} must be a boolean")
    elif kind == "string":
        if not isinstance(value, str):
            raise ValueError(f"{label} must be a string")
        if "enum" in rule and value not in rule["enum"]:
            raise ValueError(f"{label} must be one of: {', '.join(rule['enum'])}")
    elif kind == "color":
        if not isinstance(value, str) or not COLOR_PATTERN.fullmatch(value):
            raise ValueError(f"{label} must be an RGB or RGBA hexadecimal color")
    elif kind == "cloud_class":
        resolved = cloud_class(value)
        if resolved["type"] != type_name:
            raise ValueError(f"{label} {value!r} belongs to {resolved['type']}, not {type_name}")
    elif kind == "object":
        fields = rule["properties"]
        _object(value, label, fields, rule.get("required", []))
        for field, nested in value.items():
            _validate_rule(nested, fields[field], f"{label}.{field}", type_name)
    elif kind == "array":
        if not isinstance(value, list):
            raise ValueError(f"{label} must be an array")
        if len(value) < rule.get("min_items", 0) or len(value) > rule.get("max_items", math.inf):
            raise ValueError(f"{label} has an unsupported item count")
        for index, nested in enumerate(value):
            _validate_rule(nested, rule["items"], f"{label}[{index}]", type_name)
    else:
        raise ValueError(f"Catalog rule {kind!r} is unsupported")
    return value


def _near(left: float, right: float) -> bool:
    try:
        return math.isclose(left, right, rel_tol=1e-9, abs_tol=1e-7)
    except OverflowError:
        return False


def _validate_polygon(vertices: list[dict]) -> None:
    points = [(vertex["x"], vertex["y"]) for vertex in vertices]
    if len(set(points)) < 3:
        raise ValueError("flexiblePolygon must have at least three distinct vertices")
    if any(points[index] == points[(index + 1) % len(points)] for index in range(len(points))):
        raise ValueError("flexiblePolygon cannot have duplicate adjacent vertices, including a repeated closing vertex")
    area_twice = sum(points[index][0] * points[(index + 1) % len(points)][1]
                     - points[(index + 1) % len(points)][0] * points[index][1]
                     for index in range(len(points)))
    if abs(area_twice) <= 1e-12:
        raise ValueError("flexiblePolygon must enclose a nonzero area")
    def cross(a, b, c):
        return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])
    def on_segment(a, b, p):
        return abs(cross(a, b, p)) <= 1e-12 and min(a[0], b[0]) - 1e-12 <= p[0] <= max(a[0], b[0]) + 1e-12 and min(a[1], b[1]) - 1e-12 <= p[1] <= max(a[1], b[1]) + 1e-12
    for left in range(len(points)):
        a, b = points[left], points[(left + 1) % len(points)]
        for right in range(left + 1, len(points)):
            if right == left + 1 or (left == 0 and right == len(points) - 1):
                continue
            c, d = points[right], points[(right + 1) % len(points)]
            crosses = ((cross(a, b, c) > 1e-12 and cross(a, b, d) < -1e-12) or
                       (cross(a, b, c) < -1e-12 and cross(a, b, d) > 1e-12)) and (
                       (cross(c, d, a) > 1e-12 and cross(c, d, b) < -1e-12) or
                       (cross(c, d, a) < -1e-12 and cross(c, d, b) > 1e-12))
            if crosses or any((on_segment(a, b, c), on_segment(a, b, d), on_segment(c, d, a), on_segment(c, d, b))):
                raise ValueError("flexiblePolygon self-intersects or touches a nonadjacent edge; use explicit artwork or normalize the outline")


def _validate_lanes(type_name: str, properties: dict, width: float, height: float) -> None:
    vertical = properties.get("vertical", True)
    extent = width if vertical else height
    lane_total = sum(lane["width"] for lane in properties["lanes"])
    if not _near(lane_total, extent):
        axis = "width" if vertical else "height"
        raise ValueError(f"{type_name}.lanes widths must sum to bounding-box {axis} ({extent}); received {lane_total}")
    if type_name == "swimLanes":
        perpendicular_extent = height if vertical else width
        if properties["titleBar"]["height"] >= perpendicular_extent:
            raise ValueError("swimLanes.titleBar.height must leave positive lane content space")


def _validate_table(properties: dict, width: float, height: float) -> None:
    rows, cols = int(properties["rowCount"]), int(properties["colCount"])
    spans: list[tuple[int, int, int, int]] = []
    for index, cell in enumerate(properties["cells"]):
        left, top = int(cell["xPosition"]), int(cell["yPosition"])
        right = left + int(cell.get("mergeCellsRight", 0))
        bottom = top + int(cell.get("mergeCellsDown", 0))
        if right >= cols or bottom >= rows:
            raise ValueError(f"table.cells[{index}] or its merge lies outside the table grid")
        spans.append((top, bottom, left, right))
    active: list[tuple[int, int, int, int]] = []
    for span in sorted(spans):
        top, _, left, right = span
        active = [other for other in active if other[1] >= top]
        if any(left <= other[3] and right >= other[2] for other in active):
            raise ValueError("table cells or merged regions overlap")
        active.append(span)
    for field, count, extent in (("userSpecifiedRows", rows, height), ("userSpecifiedCols", cols, width)):
        dimensions = properties.get(field, [])
        indices = [int(dimension["index"]) for dimension in dimensions]
        if any(index >= count for index in indices):
            raise ValueError(f"table.{field} contains an index outside the grid")
        if len(indices) != len(set(indices)):
            raise ValueError(f"table.{field} contains duplicate indices")
        total = sum(dimension["size"] for dimension in dimensions)
        if len(dimensions) == count:
            if not _near(total, extent):
                raise ValueError(f"table.{field} sizes must match the bounding-box dimension when every index is specified")
        elif total >= extent:
            raise ValueError(f"table.{field} sizes must leave positive space for unspecified indices")


def validate_properties(type_name: str, properties: object, width: float, height: float) -> dict:
    """Validate unique vendor properties, preserving raw literal labels in a copy.

    Common shape fields are validated by the caller. No defaults are injected,
    no labels or geometric features are assigned semantic roles, and no arbitrary
    vendor properties are passed through. Call format_properties before emission.
    """
    shape_spec = spec(type_name)
    actual = shape_spec["actual_type"]
    _number(width, "shape width", {"exclusive_minimum": 0})
    _number(height, "shape height", {"exclusive_minimum": 0})
    fields = shape_spec["properties"]
    _object(properties, f"{type_name}.properties", fields, shape_spec["required_properties"])
    for field, value in properties.items():
        _validate_rule(value, fields[field], f"{type_name}.{field}", actual)
    if actual in ("swimLanes", "bpmnPool"):
        _validate_lanes(actual, properties, width, height)
    elif actual == "table":
        _validate_table(properties, width, height)
    elif actual == "flexiblePolygon":
        _validate_polygon(properties["vertices"])
    return deepcopy(properties)


def _format_rule(value: object, rule: dict) -> object:
    if rule.get("text"):
        return html.escape(value, quote=True).replace("\n", "<br/>")
    if rule["kind"] == "object":
        return {field: _format_rule(nested, rule["properties"][field]) for field, nested in value.items()}
    if rule["kind"] == "array":
        return [_format_rule(nested, rule["items"]) for nested in value]
    return deepcopy(value)


def format_properties(type_name: str, validated_properties: dict) -> dict:
    """Escape only known literal-label fields for vendor emission; never enums/IDs."""
    fields = spec(type_name)["properties"]
    _object(validated_properties, f"{type_name}.properties", fields, spec(type_name)["required_properties"])
    return {field: _format_rule(value, fields[field]) for field, value in validated_properties.items()}


def check_catalog() -> dict:
    """Check source metadata, rules, and exact cloud-class kind uniqueness."""
    catalog = _catalog()
    if catalog["schema_version"] != 1 or not catalog["observed_date"]:
        raise ValueError("Unsupported or undated catalog")
    seen: set[str] = set()
    for type_name, shape_spec in catalog["types"].items():
        if shape_spec["actual_type"] != type_name or not shape_spec["source_urls"]:
            raise ValueError(f"Catalog type {type_name!r} has inconsistent identity or missing sources")
        if not set(shape_spec["required_properties"]).issubset(shape_spec["properties"]):
            raise ValueError(f"Catalog type {type_name!r} requires an undefined property")
    for library in catalog["cloud_libraries"].values():
        if not library["source_urls"]:
            raise ValueError("Cloud library is missing primary sources")
        for class_name in library["shape_classes"] + library["container_classes"]:
            if class_name in seen or class_name in catalog["cloud_conflicts"]:
                raise ValueError(f"Cloud class {class_name!r} is duplicated or unresolved")
            seen.add(class_name)
    for alias in catalog["aliases"]:
        native_type(alias)
    return catalog_metadata()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    choice = parser.add_mutually_exclusive_group()
    choice.add_argument("--type", help="Print the compact contract for one native type")
    choice.add_argument("--cloud-class", help="Resolve one exact documented cloud class")
    choice.add_argument("--list", action="store_true", help="List supported types and coverage counts")
    choice.add_argument("--check", action="store_true", help="Validate catalog metadata and uniqueness")
    args = parser.parse_args()
    try:
        if args.type:
            output = spec(args.type)
        elif args.cloud_class:
            output = cloud_class(args.cloud_class)
        elif args.list:
            output = {**catalog_metadata(), "types": sorted(_catalog()["types"]), "aliases": _catalog()["aliases"]}
        else:
            output = check_catalog()
        print(json.dumps(output, ensure_ascii=False, indent=2, allow_nan=False))
        return 0
    except (ValueError, OSError) as error:
        print(f"Catalog error: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
