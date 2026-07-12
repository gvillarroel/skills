#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

"""Shared deterministic geometry for navigable synchronized SVG worlds."""

from __future__ import annotations

import math
import sys
from typing import Any


sys.dont_write_bytecode = True


class NavigationError(ValueError):
    """Describe an invalid navigation contract."""


def finite_number(value: Any, label: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise NavigationError(f"{label} must be numeric")
    number = float(value)
    if not math.isfinite(number):
        raise NavigationError(f"{label} must be finite")
    return number


def rect(value: Any, label: str) -> list[float]:
    if not isinstance(value, list) or len(value) != 4:
        raise NavigationError(f"{label} must be [x, y, width, height]")
    result = [finite_number(item, f"{label}[{index}]") for index, item in enumerate(value)]
    if result[2] <= 0 or result[3] <= 0:
        raise NavigationError(f"{label} needs positive width and height")
    return result


def contains(outer: list[float], inner: list[float], tolerance: float = 1e-6) -> bool:
    ox, oy, ow, oh = outer
    ix, iy, iw, ih = inner
    return (
        ix >= ox - tolerance
        and iy >= oy - tolerance
        and ix + iw <= ox + ow + tolerance
        and iy + ih <= oy + oh + tolerance
    )


def intersection_ratio(first: list[float], second: list[float]) -> float:
    ax, ay, aw, ah = first
    bx, by, bw, bh = second
    left = max(ax, bx)
    top = max(ay, by)
    right = min(ax + aw, bx + bw)
    bottom = min(ay + ah, by + bh)
    if right <= left or bottom <= top:
        return 0.0
    return (right - left) * (bottom - top) / (bw * bh)


def fit_aspect(
    value: list[float],
    aspect: float,
    *,
    padding: float = 0.0,
    bounds: list[float] | None = None,
) -> list[float]:
    """Expand a rectangle to one aspect ratio without clipping its target."""

    x, y, width, height = rect(value, "camera target")
    target_aspect = finite_number(aspect, "camera aspect")
    pad = finite_number(padding, "camera padding")
    if target_aspect <= 0 or pad < 0:
        raise NavigationError("camera aspect must be positive and padding nonnegative")
    x -= pad
    y -= pad
    width += pad * 2
    height += pad * 2
    current = width / height
    if current < target_aspect:
        expanded = height * target_aspect
        x -= (expanded - width) / 2
        width = expanded
    elif current > target_aspect:
        expanded = width / target_aspect
        y -= (expanded - height) / 2
        height = expanded
    result = [x, y, width, height]
    if bounds is None:
        return result
    world = rect(bounds, "world bounds")
    if width > world[2] + 1e-6 or height > world[3] + 1e-6:
        return list(world)
    result[0] = min(max(result[0], world[0]), world[0] + world[2] - result[2])
    result[1] = min(max(result[1], world[1]), world[1] + world[3] - result[3])
    return result


def camera_transform(camera: list[float], viewport: list[float]) -> str:
    """Return an SVG transform that maps one world camera into the fixed viewport."""

    cx, cy, cw, ch = rect(camera, "camera")
    vx, vy, vw, vh = rect(viewport, "viewport")
    scale_x = vw / cw
    scale_y = vh / ch
    if abs(scale_x - scale_y) > max(scale_x, scale_y) * 1e-6:
        raise NavigationError("camera and viewport must share one aspect ratio")
    scale = (scale_x + scale_y) / 2
    tx = vx - cx * scale
    ty = vy - cy * scale
    return f"matrix({scale:.12g} 0 0 {scale:.12g} {tx:.12g} {ty:.12g})"


def smoothstep(value: float) -> float:
    clamped = min(max(finite_number(value, "progress"), 0.0), 1.0)
    return clamped * clamped * (3 - 2 * clamped)


def interpolate_camera(first: list[float], second: list[float], progress: float) -> list[float]:
    """Interpolate center linearly and zoom logarithmically for perceptual continuity."""

    ax, ay, aw, ah = rect(first, "first camera")
    bx, by, bw, bh = rect(second, "second camera")
    t = smoothstep(progress)
    center_x = (ax + aw / 2) + ((bx + bw / 2) - (ax + aw / 2)) * t
    center_y = (ay + ah / 2) + ((by + bh / 2) - (ay + ah / 2)) * t
    width = math.exp(math.log(aw) + (math.log(bw) - math.log(aw)) * t)
    height = math.exp(math.log(ah) + (math.log(bh) - math.log(ah)) * t)
    return [center_x - width / 2, center_y - height / 2, width, height]


def validate_navigation(plan: dict[str, Any]) -> None:
    """Validate the compiled anchor tree, route, and fixed-camera geometry."""

    navigation = plan.get("navigation")
    if navigation is None:
        return
    if not isinstance(navigation, dict):
        raise NavigationError("navigation must be an object")
    viewport = rect(navigation.get("viewport"), "navigation.viewport")
    world = rect(navigation.get("worldBounds"), "navigation.worldBounds")
    viewport_aspect = viewport[2] / viewport[3]
    anchors = navigation.get("anchors")
    if not isinstance(anchors, list) or len(anchors) < 2:
        raise NavigationError("navigation.anchors must contain an overview and detail anchors")
    by_id: dict[str, dict[str, Any]] = {}
    root_ids: list[str] = []
    module_coverage: set[str] = set()
    for index, anchor in enumerate(anchors):
        if not isinstance(anchor, dict):
            raise NavigationError(f"navigation.anchors[{index}] must be an object")
        anchor_id = anchor.get("id")
        if not isinstance(anchor_id, str) or not anchor_id or anchor_id in by_id:
            raise NavigationError(f"navigation anchor id is missing or duplicated: {anchor_id!r}")
        camera = rect(anchor.get("viewBox"), f"navigation anchor {anchor_id!r} viewBox")
        if abs(camera[2] / camera[3] - viewport_aspect) > 1e-6:
            raise NavigationError(f"navigation anchor {anchor_id!r} does not match viewport aspect")
        if not contains(world, camera):
            raise NavigationError(f"navigation anchor {anchor_id!r} escapes worldBounds")
        parent_id = anchor.get("parentId")
        if parent_id is None:
            root_ids.append(anchor_id)
        elif not isinstance(parent_id, str):
            raise NavigationError(f"navigation anchor {anchor_id!r} parentId must be a string or null")
        modules = anchor.get("moduleIds", [])
        if not isinstance(modules, list) or any(not isinstance(item, str) for item in modules):
            raise NavigationError(f"navigation anchor {anchor_id!r} moduleIds must be an array of ids")
        module_coverage.update(modules)
        by_id[anchor_id] = anchor
    if len(root_ids) != 1:
        raise NavigationError("navigation anchors need exactly one root")
    for anchor_id, anchor in by_id.items():
        parent_id = anchor.get("parentId")
        if parent_id is not None and parent_id not in by_id:
            raise NavigationError(f"navigation anchor {anchor_id!r} references unknown parent {parent_id!r}")
        seen: set[str] = set()
        cursor: str | None = anchor_id
        while cursor is not None:
            if cursor in seen:
                raise NavigationError(f"navigation anchor tree contains a cycle at {cursor!r}")
            seen.add(cursor)
            cursor = by_id[cursor].get("parentId")
    plan_modules = {item["id"] for item in plan.get("modules", []) if isinstance(item, dict)}
    if module_coverage != plan_modules:
        missing = sorted(plan_modules - module_coverage)
        extra = sorted(module_coverage - plan_modules)
        raise NavigationError(f"navigation module coverage differs from plan; missing={missing}, extra={extra}")
    initial = navigation.get("initialAnchorId")
    if initial not in by_id:
        raise NavigationError("navigation.initialAnchorId must name a declared anchor")
    route = navigation.get("route")
    if not isinstance(route, dict):
        raise NavigationError("navigation.route must be an object")
    duration = finite_number(route.get("durationMs"), "navigation.route.durationMs")
    if duration <= 0:
        raise NavigationError("navigation.route.durationMs must be positive")
    stops = route.get("stops")
    if not isinstance(stops, list) or not stops:
        raise NavigationError("navigation.route.stops must be a non-empty array")
    cursor = 0.0
    stop_ids: set[str] = set()
    covered_anchors: set[str] = set()
    for index, stop in enumerate(stops):
        if not isinstance(stop, dict):
            raise NavigationError(f"navigation.route.stops[{index}] must be an object")
        stop_id = stop.get("id")
        if not isinstance(stop_id, str) or not stop_id or stop_id in stop_ids:
            raise NavigationError(f"navigation route stop id is missing or duplicated: {stop_id!r}")
        stop_ids.add(stop_id)
        anchor_id = stop.get("anchorId")
        if anchor_id not in by_id:
            raise NavigationError(f"navigation route stop {stop_id!r} references an unknown anchor")
        covered_anchors.add(str(anchor_id))
        start = finite_number(stop.get("startMs"), f"navigation route stop {stop_id!r} startMs")
        arrival = finite_number(stop.get("arrivalMs"), f"navigation route stop {stop_id!r} arrivalMs")
        end = finite_number(stop.get("endMs"), f"navigation route stop {stop_id!r} endMs")
        if abs(start - cursor) > 1e-6 or not start <= arrival <= end or end <= start:
            raise NavigationError(f"navigation route stop {stop_id!r} must be contiguous and ordered")
        cursor = end
    if abs(cursor - duration) > 1e-6:
        raise NavigationError("navigation route stops must cover durationMs exactly")
    required = {item["id"] for item in anchors if item.get("requiredForTour")}
    missing_required = sorted(required - covered_anchors)
    if missing_required:
        raise NavigationError(f"navigation route misses required anchors: {missing_required}")
