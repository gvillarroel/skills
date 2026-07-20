#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

"""Deterministic numerical cores for layered procedural SVG patterns.

The module intentionally returns semantic geometry and sampled solver states,
not SVG markup.  Renderers can therefore choose their own timing, styling, and
layer composition without changing the canonical numerical state digest.
"""

from __future__ import annotations

import argparse
import hashlib
import heapq
import json
import math
import random
import sys
import time
from collections.abc import Iterable
from typing import Any


for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(encoding="utf-8", errors="backslashreplace")


ALGORITHMS = (
    "delaunay-alpha-persistence",
    "lower-star-join-tree",
    "entropic-sinkhorn-transport",
    "fast-marching-eikonal",
    "jones-inspired-physarum",
    "stam-stable-fluid",
)

# Values outside [0, 1] by no more than this amount are treated as harmless
# floating-point roundoff.  They are still counted as clamps in telemetry.
DYE_BOUND_TOLERANCE = 1e-8

DEFAULTS: tuple[dict[str, int | float], ...] = (
    {"point_count": 18, "frame_count": 7},
    {"grid_columns": 26, "grid_rows": 16, "frame_count": 7},
    {"site_count": 9, "epsilon": 0.08, "minimum_iterations": 80, "frame_count": 7},
    {
        "grid_columns": 30,
        "grid_rows": 18,
        "frame_count": 7,
        "speed_modulation": 0.45,
    },
    {"agent_count": 90, "steps": 120, "frame_count": 7, "sensor_offset": 4.0},
    {
        "grid_columns": 20,
        "grid_rows": 12,
        "steps": 48,
        "frame_count": 7,
        "viscosity": 0.001,
    },
)

_INTEGER_LIMITS: tuple[dict[str, tuple[int, int]], ...] = (
    {"point_count": (8, 80), "frame_count": (2, 24)},
    {
        "grid_columns": (8, 80),
        "grid_rows": (8, 60),
        "frame_count": (2, 24),
    },
    {
        "site_count": (2, 32),
        "minimum_iterations": (8, 500),
        "frame_count": (2, 24),
    },
    {
        "grid_columns": (8, 100),
        "grid_rows": (8, 80),
        "frame_count": (2, 24),
    },
    {
        "agent_count": (8, 400),
        "steps": (8, 400),
        "frame_count": (2, 24),
    },
    {
        "grid_columns": (8, 60),
        "grid_rows": (8, 48),
        "steps": (8, 180),
        "frame_count": (2, 24),
    },
)

_FLOAT_LIMITS: tuple[dict[str, tuple[float, float]], ...] = (
    {},
    {},
    {"epsilon": (0.005, 1.0)},
    {"speed_modulation": (0.0, 0.75)},
    {"sensor_offset": (2.0, 6.0)},
    {"viscosity": (0.0, 0.05)},
)


def _validated_parameters(variant: int, supplied: dict[str, object]) -> dict[str, int | float]:
    if not isinstance(supplied, dict):
        raise TypeError("parameters must be a dictionary")
    unknown = sorted(set(supplied) - set(DEFAULTS[variant]))
    if unknown:
        raise ValueError(f"unsupported parameters for variant {variant}: {', '.join(unknown)}")
    values: dict[str, int | float] = dict(DEFAULTS[variant])
    values.update(supplied)  # type: ignore[arg-type]
    for key, (minimum, maximum) in _INTEGER_LIMITS[variant].items():
        value = values[key]
        if isinstance(value, bool) or not isinstance(value, int):
            raise TypeError(f"{key} must be an integer")
        if not minimum <= value <= maximum:
            raise ValueError(f"{key} must be in [{minimum}, {maximum}]")
    for key, (minimum, maximum) in _FLOAT_LIMITS[variant].items():
        value = values[key]
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise TypeError(f"{key} must be numeric")
        numeric = float(value)
        if not math.isfinite(numeric) or not minimum <= numeric <= maximum:
            raise ValueError(f"{key} must be finite and in [{minimum}, {maximum}]")
        values[key] = numeric
    return values


def _clean(value: Any, *, significant_precision: bool = False) -> Any:
    """Quantize floats and recursively establish a portable canonical state."""

    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("solver produced a nonfinite value")
        # Sinkhorn reconstruction evidence needs significant-digit precision:
        # its Gibbs entries can be far below 1e-8 while still contributing
        # finite transported mass after diagonal scaling.  Other public solver
        # fields retain the compact eight-decimal canonical representation.
        rounded = (
            float(format(value, ".15g"))
            if significant_precision
            else round(value, 8)
        )
        return 0.0 if rounded == 0.0 else rounded
    if isinstance(value, dict):
        return {
            str(key): _clean(
                item,
                significant_precision=(
                    significant_precision or str(key) == "sinkhornScalingEvidence"
                ),
            )
            for key, item in value.items()
        }
    if isinstance(value, (list, tuple)):
        return [
            _clean(item, significant_precision=significant_precision)
            for item in value
        ]
    if value is None or isinstance(value, (str, int, bool)):
        return value
    raise TypeError(f"solver produced unsupported value type: {type(value).__name__}")


def _digest(payload: dict[str, object]) -> str:
    encoded = json.dumps(
        payload,
        ensure_ascii=True,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _frame_steps(total_steps: int, frame_count: int) -> list[int]:
    return [round(index * total_steps / (frame_count - 1)) for index in range(frame_count)]


def _weighted_event_thresholds(
    event_values: list[float], frame_count: int, initial_value: float
) -> list[float]:
    """Select monotone thresholds by cumulative event rank.

    Repeated values form one atomic filtration event.  When there are enough
    distinct events, each returned post-initial threshold advances to a new
    event while weighted ranks spread simplex activations across the frames.
    """

    ordered = sorted(value for value in event_values if value > initial_value + 1e-14)
    if not ordered:
        return [initial_value] * frame_count
    groups: list[tuple[float, int]] = []
    for value in ordered:
        if groups and abs(value - groups[-1][0]) <= 1e-14:
            groups[-1] = (groups[-1][0], groups[-1][1] + 1)
        else:
            groups.append((value, 1))
    slots = frame_count - 1
    total_events = len(ordered)
    thresholds = [initial_value]
    previous_index = -1
    for slot in range(1, slots + 1):
        target_rank = math.ceil(total_events * slot / slots)
        cumulative = 0
        weighted_index = len(groups) - 1
        for index, (_, count) in enumerate(groups):
            cumulative += count
            if cumulative >= target_rank:
                weighted_index = index
                break
        if len(groups) >= slots:
            minimum_index = previous_index + 1
            maximum_index = len(groups) - (slots - slot) - 1
            selected_index = min(maximum_index, max(minimum_index, weighted_index))
        else:
            selected_index = round((slot - 1) * (len(groups) - 1) / max(1, slots - 1))
        thresholds.append(groups[selected_index][0])
        previous_index = selected_index
    thresholds[-1] = groups[-1][0]
    return thresholds


def _unique_rank_thresholds(event_values: list[float], frame_count: int) -> list[float]:
    """Sample sorted unique critical values by rank, preserving both endpoints."""

    unique = sorted(set(event_values))
    if not unique:
        return [0.0] * frame_count
    if frame_count == 1:
        return [unique[-1]]
    return [
        unique[round(index * (len(unique) - 1) / (frame_count - 1))]
        for index in range(frame_count)
    ]


def _supplemented_lower_star_levels(
    critical_values: list[float], sample_values: list[float], frame_count: int
) -> list[float]:
    """Preserve critical levels and fill rank gaps with lower-star events."""

    critical = sorted(set(critical_values))
    if len(critical) >= frame_count:
        return _unique_rank_thresholds(critical, frame_count)
    universe = sorted(set(sample_values) | set(critical))
    index_by_value = {value: index for index, value in enumerate(universe)}
    selected = {index_by_value[value] for value in critical}
    while len(selected) < frame_count:
        ordered = sorted(selected)
        gaps = [
            (right - left - 1, left, right)
            for left, right in zip(ordered, ordered[1:])
            if right - left > 1
        ]
        if not gaps:
            break
        _, left, right = max(gaps, key=lambda item: (item[0], -item[1]))
        selected.add((left + right) // 2)
    if len(selected) < frame_count:
        for index in range(len(universe)):
            selected.add(index)
            if len(selected) == frame_count:
                break
    return [universe[index] for index in sorted(selected)]


class _UnionFind:
    def __init__(self, count: int) -> None:
        self.parent = list(range(count))
        self.rank = [0] * count

    def find(self, item: int) -> int:
        root = item
        while self.parent[root] != root:
            root = self.parent[root]
        while self.parent[item] != item:
            parent = self.parent[item]
            self.parent[item] = root
            item = parent
        return root

    def union(self, left: int, right: int) -> int:
        a = self.find(left)
        b = self.find(right)
        if a == b:
            return a
        if self.rank[a] < self.rank[b] or (self.rank[a] == self.rank[b] and a > b):
            a, b = b, a
        self.parent[b] = a
        if self.rank[a] == self.rank[b]:
            self.rank[a] += 1
        return a


def _circumcircle(
    a: tuple[float, float], b: tuple[float, float], c: tuple[float, float]
) -> tuple[float, float, float]:
    ax, ay = a
    bx, by = b
    cx, cy = c
    divisor = 2.0 * (ax * (by - cy) + bx * (cy - ay) + cx * (ay - by))
    if abs(divisor) < 1e-14:
        return 0.0, 0.0, math.inf
    aa = ax * ax + ay * ay
    bb = bx * bx + by * by
    cc = cx * cx + cy * cy
    ux = (aa * (by - cy) + bb * (cy - ay) + cc * (ay - by)) / divisor
    uy = (aa * (cx - bx) + bb * (ax - cx) + cc * (bx - ax)) / divisor
    radius_squared = (ux - ax) ** 2 + (uy - ay) ** 2
    return ux, uy, radius_squared


def _orient_triangle(
    triangle: tuple[int, int, int], points: list[tuple[float, float]]
) -> tuple[int, int, int]:
    a, b, c = triangle
    cross = (
        (points[b][0] - points[a][0]) * (points[c][1] - points[a][1])
        - (points[b][1] - points[a][1]) * (points[c][0] - points[a][0])
    )
    return triangle if cross > 0.0 else (a, c, b)


def _delaunay(points: list[tuple[float, float]]) -> list[tuple[int, int, int]]:
    count = len(points)
    work = list(points) + [(-16.0, -10.0), (16.0, -10.0), (0.0, 18.0)]
    triangles: list[tuple[int, int, int]] = [(count, count + 1, count + 2)]
    for point_id in range(count):
        px, py = work[point_id]
        bad: list[tuple[int, int, int]] = []
        for triangle in triangles:
            ux, uy, radius_squared = _circumcircle(*(work[index] for index in triangle))
            if (px - ux) ** 2 + (py - uy) ** 2 <= radius_squared + 1e-12:
                bad.append(triangle)
        boundary_counts: dict[tuple[int, int], int] = {}
        for a, b, c in bad:
            for edge in ((a, b), (b, c), (c, a)):
                key = tuple(sorted(edge))
                boundary_counts[key] = boundary_counts.get(key, 0) + 1
        bad_set = set(bad)
        triangles = [triangle for triangle in triangles if triangle not in bad_set]
        for edge in sorted(key for key, occurrences in boundary_counts.items() if occurrences == 1):
            triangles.append(_orient_triangle((edge[0], edge[1], point_id), work))
    result = {
        tuple(sorted(triangle))
        for triangle in triangles
        if all(vertex < count for vertex in triangle)
    }
    return sorted(result)


def _components(
    count: int, edges: Iterable[tuple[int, int]], active: set[int] | None = None
) -> tuple[list[int], int]:
    enabled = set(range(count)) if active is None else active
    union_find = _UnionFind(count)
    for left, right in edges:
        if left in enabled and right in enabled:
            union_find.union(left, right)
    roots = {item: union_find.find(item) for item in enabled}
    representatives: dict[int, int] = {}
    for item, root in roots.items():
        representatives[root] = min(representatives.get(root, item), item)
    labels = [-1] * count
    for item, root in roots.items():
        labels[item] = representatives[root]
    return labels, len(set(labels[item] for item in enabled))


def _alpha_persistence(
    seed: int, parameters: dict[str, int | float]
) -> tuple[dict[str, object], list[dict[str, object]], int, dict[str, object]]:
    point_count = int(parameters["point_count"])
    frame_count = int(parameters["frame_count"])
    rng = random.Random(seed ^ 0xA17FA)
    points: list[tuple[float, float]] = []
    attempts = 0
    while len(points) < point_count and attempts < point_count * 300:
        attempts += 1
        candidate = (0.06 + 0.88 * rng.random(), 0.07 + 0.86 * rng.random())
        if all((candidate[0] - x) ** 2 + (candidate[1] - y) ** 2 > 0.0012 for x, y in points):
            points.append(candidate)
    if len(points) != point_count:
        raise RuntimeError("could not generate a nondegenerate point set")

    faces = _delaunay(points)
    edge_faces: dict[tuple[int, int], list[int]] = {}
    face_alpha: list[float] = []
    for face_id, (a, b, c) in enumerate(faces):
        _, _, radius_squared = _circumcircle(points[a], points[b], points[c])
        face_alpha.append(math.sqrt(radius_squared))
        for edge in ((a, b), (b, c), (a, c)):
            edge_faces.setdefault(tuple(sorted(edge)), []).append(face_id)
    edges = sorted(edge_faces)
    edge_alpha: list[float] = []
    for left, right in edges:
        midpoint = (
            0.5 * (points[left][0] + points[right][0]),
            0.5 * (points[left][1] + points[right][1]),
        )
        radius_squared = 0.25 * (
            (points[left][0] - points[right][0]) ** 2
            + (points[left][1] - points[right][1]) ** 2
        )
        gabriel = all(
            item in (left, right)
            or (point[0] - midpoint[0]) ** 2 + (point[1] - midpoint[1]) ** 2
            >= radius_squared - 1e-12
            for item, point in enumerate(points)
        )
        alpha = math.sqrt(radius_squared) if gabriel else min(
            face_alpha[face_id] for face_id in edge_faces[(left, right)]
        )
        edge_alpha.append(alpha)

    simplices: list[tuple[float, int, tuple[int, ...], str]] = []
    simplices.extend((0.0, 0, (item,), f"v{item}") for item in range(point_count))
    simplices.extend(
        (edge_alpha[index], 1, edge, f"e{edge[0]}-{edge[1]}")
        for index, edge in enumerate(edges)
    )
    simplices.extend(
        (face_alpha[index], 2, face, f"f{face[0]}-{face[1]}-{face[2]}")
        for index, face in enumerate(faces)
    )
    simplices.sort(key=lambda item: (item[0], item[1], item[2]))
    simplex_index = {(dimension, vertices): index for index, (_, dimension, vertices, _) in enumerate(simplices)}
    reduced: list[set[int]] = []
    pivot_column: dict[int, int] = {}
    creators: set[int] = set()
    pairs: list[dict[str, object]] = []
    for column_id, (alpha, dimension, vertices, simplex_id) in enumerate(simplices):
        if dimension == 0:
            column: set[int] = set()
        elif dimension == 1:
            column = {simplex_index[(0, (vertex,))] for vertex in vertices}
        else:
            a, b, c = vertices
            column = {
                simplex_index[(1, tuple(sorted(edge)))]
                for edge in ((a, b), (a, c), (b, c))
            }
        while column and max(column) in pivot_column:
            column ^= reduced[pivot_column[max(column)]]
        if not column:
            creators.add(column_id)
        else:
            birth_column = max(column)
            pivot_column[birth_column] = column_id
            birth_alpha, birth_dimension, _, birth_id = simplices[birth_column]
            pairs.append(
                {
                    "dimension": birth_dimension,
                    "birth": birth_alpha,
                    "death": alpha,
                    "lifetime": alpha - birth_alpha,
                    "birthSimplex": birth_id,
                    "deathSimplex": simplex_id,
                }
            )
        reduced.append(column)
    paired_births = set(pivot_column)
    for birth_column in sorted(creators - paired_births):
        birth_alpha, birth_dimension, _, birth_id = simplices[birth_column]
        pairs.append(
            {
                "dimension": birth_dimension,
                "birth": birth_alpha,
                "death": None,
                "lifetime": None,
                "birthSimplex": birth_id,
                "deathSimplex": None,
            }
        )
    pairs.sort(
        key=lambda item: (
            int(item["dimension"]),
            float(item["birth"]),
            math.inf if item["death"] is None else float(item["death"]),
            str(item["birthSimplex"]),
        )
    )

    filtration_events = edge_alpha + face_alpha
    thresholds = _weighted_event_thresholds(filtration_events, frame_count, 0.0)
    frames: list[dict[str, object]] = []
    face_closure_errors = 0
    euler_residual_max = 0
    component_betti_errors = 0
    for frame_id in range(frame_count):
        phase = frame_id / (frame_count - 1)
        threshold = thresholds[frame_id]
        active_edge_indices = [index for index, value in enumerate(edge_alpha) if value <= threshold + 1e-12]
        active_face_indices = [index for index, value in enumerate(face_alpha) if value <= threshold + 1e-12]
        active_edges = [edges[index] for index in active_edge_indices]
        active_edge_set = set(active_edges)
        for face_id in active_face_indices:
            a, b, c = faces[face_id]
            for edge in ((a, b), (a, c), (b, c)):
                if tuple(sorted(edge)) not in active_edge_set:
                    face_closure_errors += 1
        component_labels, component_count = _components(point_count, active_edges)
        euler = point_count - len(active_edges) + len(active_face_indices)
        betti = [
            sum(
                int(pair["dimension"]) == dimension
                and float(pair["birth"]) <= threshold + 1e-12
                and (pair["death"] is None or threshold < float(pair["death"]) - 1e-12)
                for pair in pairs
            )
            for dimension in range(3)
        ]
        component_betti_errors += int(betti[0] != component_count)
        residual = abs(euler - (betti[0] - betti[1] + betti[2]))
        euler_residual_max = max(euler_residual_max, residual)
        frames.append(
            {
                "index": frame_id,
                "phase": phase,
                "alpha": threshold,
                "activeEdgeIds": [f"e{edges[index][0]}-{edges[index][1]}" for index in active_edge_indices],
                "activeFaceIds": [
                    f"f{faces[index][0]}-{faces[index][1]}-{faces[index][2]}"
                    for index in active_face_indices
                ],
                "componentByPoint": component_labels,
                "betti": betti,
                "euler": euler,
                "activeSimplexCount": point_count
                + len(active_edge_indices)
                + len(active_face_indices),
            }
        )

    face_incidence = [len(edge_faces[edge]) for edge in edges]
    final_euler = point_count - len(edges) + len(faces)
    negative_lifetimes = sum(
        1
        for pair in pairs
        if pair["lifetime"] is not None and float(pair["lifetime"]) < -1e-12
    )
    simplex_counts = [int(frame["activeSimplexCount"]) for frame in frames]
    simplex_deltas = [
        simplex_counts[index] - simplex_counts[index - 1]
        for index in range(1, len(simplex_counts))
    ]
    metrics: dict[str, object] = {
        "pointCount": point_count,
        "edgeCount": len(edges),
        "faceCount": len(faces),
        "finitePersistencePairs": sum(pair["death"] is not None for pair in pairs),
        "infinitePersistencePairs": sum(pair["death"] is None for pair in pairs),
        "alpha.faceClosureErrors": face_closure_errors,
        "alpha.eulerResidualMax": euler_residual_max,
        "alpha.componentBettiErrors": component_betti_errors,
        "alpha.negativeLifetimes": negative_lifetimes,
        "finalDiskEuler": final_euler,
        "alpha.nonmanifoldEdgeCount": sum(incidence > 2 for incidence in face_incidence),
        "alpha.distinctFrameStates": len(set(simplex_counts)),
        "alpha.stagnantTransitions": sum(delta <= 0 for delta in simplex_deltas),
        "alpha.minimumSimplexDelta": min(simplex_deltas, default=0),
    }
    geometry: dict[str, object] = {
        "coordinateSpace": "normalized",
        "points": [
            {"id": index, "x": point[0], "y": point[1]} for index, point in enumerate(points)
        ],
        "delaunayEdges": [
            {"id": f"e{edge[0]}-{edge[1]}", "a": edge[0], "b": edge[1], "alpha": edge_alpha[index]}
            for index, edge in enumerate(edges)
        ],
        "delaunayFaces": [
            {
                "id": f"f{face[0]}-{face[1]}-{face[2]}",
                "vertices": list(face),
                "alpha": face_alpha[index],
            }
            for index, face in enumerate(faces)
        ],
        "persistenceIntervals": pairs,
    }
    midpoint = 0.5 * (frame_count - 1)
    static_index = max(
        range(frame_count),
        key=lambda index: (
            int(frames[index]["betti"][1]),  # type: ignore[index]
            -abs(index - midpoint),
            -index,
        ),
    )
    metrics["alpha.staticFrameIndex"] = static_index
    metrics["alpha.staticFrameBeta1"] = int(frames[static_index]["betti"][1])  # type: ignore[index]
    return geometry, frames, static_index, metrics


def _grid_triangles(columns: int, rows: int) -> list[tuple[int, int, int]]:
    triangles: list[tuple[int, int, int]] = []
    for row in range(rows - 1):
        for column in range(columns - 1):
            a = row * columns + column
            b = a + 1
            c = a + columns
            d = c + 1
            if (row + column) % 2 == 0:
                triangles.extend(((a, b, d), (a, d, c)))
            else:
                triangles.extend(((a, b, c), (b, d, c)))
    return triangles


def _join_adjacency(
    sample_count: int, triangles: list[tuple[int, int, int]]
) -> list[set[int]]:
    adjacency: list[set[int]] = [set() for _ in range(sample_count)]
    for a, b, c in triangles:
        for left, right in ((a, b), (a, c), (b, c)):
            adjacency[left].add(right)
            adjacency[right].add(left)
    return adjacency


def _audit_join_component_accounting(
    values: list[float],
    triangles: list[tuple[int, int, int]],
    merge_events: list[dict[str, object]],
) -> int:
    """Replay lower-star connectivity independently and audit merge records."""

    adjacency = _join_adjacency(len(values), triangles)
    order = sorted(range(len(values)), key=lambda item: (values[item], item))
    union_find = _UnionFind(len(values))
    active: set[int] = set()
    events_by_sample: dict[int, list[dict[str, object]]] = {}
    errors = 0
    for event in merge_events:
        sample = event.get("sample")
        if isinstance(sample, bool) or not isinstance(sample, int) or not 0 <= sample < len(values):
            errors += 1
            continue
        events_by_sample.setdefault(sample, []).append(event)

    for sample in order:
        before_count = len({union_find.find(vertex) for vertex in active})
        neighbor_roots = {
            union_find.find(neighbor) for neighbor in adjacency[sample] if neighbor in active
        }
        expected_merge = len(neighbor_roots) >= 2
        events = events_by_sample.get(sample, [])
        if len(events) != int(expected_merge):
            errors += abs(len(events) - int(expected_merge))
        event = events[0] if events else None
        if event is not None and expected_merge:
            if int(event.get("componentsBefore", -1)) != before_count:
                errors += 1
            inputs = event.get("inputComponents")
            if not isinstance(inputs, list):
                errors += 1
                input_roots: set[int] = set()
            else:
                input_roots = set()
                for component in inputs:
                    if (
                        isinstance(component, bool)
                        or not isinstance(component, int)
                        or component not in active
                    ):
                        errors += 1
                    else:
                        input_roots.add(union_find.find(component))
                if len(inputs) != len(input_roots) or input_roots != neighbor_roots:
                    errors += 1
            survivor = event.get("survivingComponent")
            if (
                isinstance(survivor, bool)
                or not isinstance(survivor, int)
                or survivor not in active
                or union_find.find(survivor) not in neighbor_roots
            ):
                errors += 1

        active.add(sample)
        for neighbor in sorted(adjacency[sample]):
            if neighbor in active:
                union_find.union(sample, neighbor)
        after_count = len({union_find.find(vertex) for vertex in active})
        expected_after = before_count + 1 if not neighbor_roots else before_count - len(neighbor_roots) + 1
        if after_count != expected_after:
            errors += 1
        if event is not None and expected_merge:
            if int(event.get("componentsAfter", -1)) != after_count:
                errors += 1

    errors += sum(len(events) for sample, events in events_by_sample.items() if sample not in active)
    return errors


def _audit_join_tree_structure(
    nodes: list[dict[str, object]], arcs: list[dict[str, object]]
) -> dict[str, int]:
    """Audit tree connectivity, cycles, and one-parent cardinality."""

    node_ids = [str(node.get("id")) for node in nodes]
    node_index = {node_id: index for index, node_id in enumerate(node_ids)}
    root_ids = {str(node.get("id")) for node in nodes if node.get("type") == "root-maximum"}
    outgoing = {node_id: 0 for node_id in node_ids}
    union_find = _UnionFind(len(nodes))
    cycle_count = 0
    parent_errors = abs(len(root_ids) - 1)
    for arc in arcs:
        child = str(arc.get("from"))
        parent = str(arc.get("to"))
        if child not in node_index or parent not in node_index:
            parent_errors += 1
            continue
        outgoing[child] += 1
        left = node_index[child]
        right = node_index[parent]
        if union_find.find(left) == union_find.find(right):
            cycle_count += 1
        else:
            union_find.union(left, right)
    for node_id in node_ids:
        expected = 0 if node_id in root_ids else 1
        parent_errors += int(outgoing[node_id] != expected)
    component_count = len({union_find.find(index) for index in range(len(nodes))}) if nodes else 0
    disconnected_errors = max(0, component_count - 1)
    return {
        "cycleCount": cycle_count,
        "disconnectedComponentErrors": disconnected_errors,
        "parentCardinalityErrors": parent_errors,
        "treeStructureErrors": cycle_count + disconnected_errors + parent_errors,
    }


def _contour_segments(
    points: list[tuple[float, float]],
    triangles: list[tuple[int, int, int]],
    values: list[float],
    level: float,
) -> list[dict[str, list[float]]]:
    segments: list[dict[str, list[float]]] = []
    for triangle in triangles:
        intersections: list[tuple[float, float]] = []
        for left, right in (
            (triangle[0], triangle[1]),
            (triangle[1], triangle[2]),
            (triangle[2], triangle[0]),
        ):
            left_value = values[left]
            right_value = values[right]
            if not (min(left_value, right_value) <= level <= max(left_value, right_value)):
                continue
            if abs(right_value - left_value) < 1e-14:
                continue
            factor = (level - left_value) / (right_value - left_value)
            if -1e-12 <= factor <= 1.0 + 1e-12:
                x = points[left][0] + factor * (points[right][0] - points[left][0])
                y = points[left][1] + factor * (points[right][1] - points[left][1])
                candidate = (x, y)
                if all((x - old[0]) ** 2 + (y - old[1]) ** 2 > 1e-18 for old in intersections):
                    intersections.append(candidate)
        if len(intersections) >= 2:
            intersections.sort()
            segments.append(
                {"a": [intersections[0][0], intersections[0][1]], "b": [intersections[-1][0], intersections[-1][1]]}
            )
    return segments


def _lower_star_join_tree(
    seed: int, parameters: dict[str, int | float]
) -> tuple[dict[str, object], list[dict[str, object]], int, dict[str, object]]:
    columns = int(parameters["grid_columns"])
    rows = int(parameters["grid_rows"])
    frame_count = int(parameters["frame_count"])
    rng = random.Random(seed ^ 0xC0170A)
    well_bases = ((0.22, 0.28, 1.15, 0.018), (0.72, 0.31, 0.95, 0.026), (0.48, 0.77, 0.78, 0.022))
    wells = [
        (
            base_x + (rng.random() - 0.5) * 0.07,
            base_y + (rng.random() - 0.5) * 0.07,
            amplitude * (0.88 + 0.24 * rng.random()),
            spread * (0.85 + 0.30 * rng.random()),
        )
        for base_x, base_y, amplitude, spread in well_bases
    ]
    hill_x = 0.49 + (rng.random() - 0.5) * 0.06
    hill_y = 0.49 + (rng.random() - 0.5) * 0.06
    hill_amplitude = 0.62 * (0.88 + 0.24 * rng.random())
    hill_spread = 0.032 * (0.85 + 0.30 * rng.random())
    oscillation_amplitude = 0.13 + 0.06 * rng.random()
    oscillation_phase_x = 2.0 * math.pi * rng.random()
    oscillation_phase_y = 2.0 * math.pi * rng.random()
    points: list[tuple[float, float]] = []
    values: list[float] = []
    for row in range(rows):
        y = row / (rows - 1)
        for column in range(columns):
            x = column / (columns - 1)
            points.append((x, y))
            field = -sum(
                amplitude * math.exp(-((x - center_x) ** 2 + (y - center_y) ** 2) / spread)
                for center_x, center_y, amplitude, spread in wells
            )
            field += hill_amplitude * math.exp(
                -((x - hill_x) ** 2 + (y - hill_y) ** 2) / hill_spread
            )
            field += oscillation_amplitude * math.sin(
                3.0 * math.pi * x + oscillation_phase_x
            ) * math.cos(2.0 * math.pi * y + oscillation_phase_y)
            field += 0.12 * x + 1e-8 * rng.random()
            values.append(field)
    triangles = _grid_triangles(columns, rows)
    adjacency = _join_adjacency(len(points), triangles)

    order = sorted(range(len(points)), key=lambda item: (values[item], item))
    parent = list(range(len(points)))
    active: set[int] = set()
    birth_sample: dict[int, int] = {}
    current_node: dict[int, str] = {}
    nodes: list[dict[str, object]] = []
    arcs: list[dict[str, object]] = []
    merge_events: list[dict[str, object]] = []
    active_component_count = 0

    def find(item: int) -> int:
        while parent[item] != item:
            parent[item] = parent[parent[item]]
            item = parent[item]
        return item

    for sample in order:
        lower_roots = sorted({find(neighbor) for neighbor in adjacency[sample] if neighbor in active})
        active.add(sample)
        if not lower_roots:
            node_id = f"minimum-{sample}"
            nodes.append({"id": node_id, "type": "minimum", "sample": sample, "value": values[sample]})
            birth_sample[sample] = sample
            current_node[sample] = node_id
            active_component_count += 1
            continue
        if len(lower_roots) == 1:
            root = lower_roots[0]
            parent[sample] = root
            continue
        node_id = f"saddle-{sample}"
        nodes.append({"id": node_id, "type": "merge-saddle", "sample": sample, "value": values[sample]})
        input_nodes = sorted({current_node[root] for root in lower_roots})
        for child in input_nodes:
            arcs.append({"id": f"arc-{len(arcs)}", "from": child, "to": node_id})
        elder = min(lower_roots, key=lambda root: (values[birth_sample[root]], birth_sample[root]))
        components_before = active_component_count
        active_component_count -= len(lower_roots) - 1
        event = {
            "id": f"merge-{len(merge_events)}",
            "sample": sample,
            "value": values[sample],
            "inputComponents": lower_roots,
            "survivingComponent": elder,
            "componentsBefore": components_before,
            "componentsAfter": active_component_count,
        }
        merge_events.append(event)
        for root in lower_roots:
            if root != elder:
                parent[root] = elder
        parent[sample] = elder
        current_node[elder] = node_id

    final_roots = sorted({find(sample) for sample in active})
    maximum_sample = max(order, key=lambda item: (values[item], item))
    root_node = f"root-{maximum_sample}"
    nodes.append({"id": root_node, "type": "root-maximum", "sample": maximum_sample, "value": values[maximum_sample]})
    for component in final_roots:
        child = current_node[component]
        if child != root_node:
            arcs.append({"id": f"arc-{len(arcs)}", "from": child, "to": root_node})

    node_by_id = {str(node["id"]): node for node in nodes}
    event_order_errors = sum(
        float(node_by_id[str(arc["from"])]["value"])
        > float(node_by_id[str(arc["to"])]["value"]) + 1e-12
        for arc in arcs
    )
    component_accounting_errors = _audit_join_component_accounting(
        values, triangles, merge_events
    )
    structure_audit = _audit_join_tree_structure(nodes, arcs)

    critical_values = [float(node["value"]) for node in nodes]
    levels = _supplemented_lower_star_levels(
        critical_values, values, frame_count
    )
    frames: list[dict[str, object]] = []
    for frame_id in range(frame_count):
        phase = frame_id / (frame_count - 1)
        level = levels[frame_id]
        active_samples = {sample for sample, value in enumerate(values) if value <= level + 1e-12}
        active_edges = {
            tuple(sorted((sample, neighbor)))
            for sample in active_samples
            for neighbor in adjacency[sample]
            if neighbor in active_samples
        }
        labels, _ = _components(len(points), active_edges, active_samples)
        visible_nodes = [str(node["id"]) for node in nodes if float(node["value"]) <= level + 1e-12]
        visible_node_set = set(visible_nodes)
        visible_arcs = [
            str(arc["id"])
            for arc in arcs
            if str(arc["from"]) in visible_node_set and str(arc["to"]) in visible_node_set
        ]
        frames.append(
            {
                "index": frame_id,
                "phase": phase,
                "level": level,
                "activeSampleIds": sorted(active_samples),
                "componentBySample": labels,
                "contourSegments": _contour_segments(points, triangles, values, level),
                "visibleTreeNodeIds": visible_nodes,
                "visibleTreeArcIds": visible_arcs,
            }
        )

    frame_signatures = [
        (
            len(frame["activeSampleIds"]),  # type: ignore[arg-type]
            tuple(frame["visibleTreeNodeIds"]),  # type: ignore[arg-type]
            tuple(frame["visibleTreeArcIds"]),  # type: ignore[arg-type]
        )
        for frame in frames
    ]
    metrics: dict[str, object] = {
        "sampleCount": len(points),
        "triangleCount": len(triangles),
        "criticalNodeCount": len(nodes),
        "mergeEventCount": len(merge_events),
        "joinTree.treeStructureErrors": structure_audit["treeStructureErrors"],
        "joinTree.cycleCount": structure_audit["cycleCount"],
        "joinTree.disconnectedComponentErrors": structure_audit[
            "disconnectedComponentErrors"
        ],
        "joinTree.parentCardinalityErrors": structure_audit[
            "parentCardinalityErrors"
        ],
        "joinTree.eventOrderErrors": event_order_errors,
        "joinTree.componentAccountingErrors": component_accounting_errors,
        "joinTree.distinctFrameStates": len(set(frame_signatures)),
        "joinTree.stagnantTransitions": sum(
            frame_signatures[index] == frame_signatures[index - 1]
            for index in range(1, len(frame_signatures))
        ),
        "joinTree.criticalLevelFrameCount": sum(level in set(critical_values) for level in levels),
        "joinTree.supplementedLevelFrameCount": sum(
            level not in set(critical_values) for level in levels
        ),
        "finalComponentCount": len(final_roots),
    }
    geometry: dict[str, object] = {
        "coordinateSpace": "normalized",
        "columns": columns,
        "rows": rows,
        "samples": [
            {
                "id": sample,
                "column": sample % columns,
                "row": sample // columns,
                "x": points[sample][0],
                "y": points[sample][1],
                "value": values[sample],
            }
            for sample in range(len(points))
        ],
        "triangles": [list(triangle) for triangle in triangles],
        "joinTree": {"nodes": nodes, "arcs": arcs, "mergeEvents": merge_events},
    }
    return geometry, frames, frame_count // 2, metrics


def _sinkhorn_transport(
    seed: int, parameters: dict[str, int | float]
) -> tuple[dict[str, object], list[dict[str, object]], int, dict[str, object]]:
    site_count = int(parameters["site_count"])
    epsilon = float(parameters["epsilon"])
    minimum_iterations = int(parameters["minimum_iterations"])
    frame_count = int(parameters["frame_count"])
    rng = random.Random(seed ^ 0x517A0)
    sources = [
        {"id": index, "x": 0.08 + 0.32 * rng.random(), "y": 0.08 + 0.84 * rng.random()}
        for index in range(site_count)
    ]
    targets = [
        {"id": index, "x": 0.60 + 0.32 * rng.random(), "y": 0.08 + 0.84 * rng.random()}
        for index in range(site_count)
    ]
    source_mass = [0.3 + rng.random() for _ in range(site_count)]
    target_mass = [0.3 + rng.random() for _ in range(site_count)]
    source_total = sum(source_mass)
    target_total = sum(target_mass)
    source_mass = [value / source_total for value in source_mass]
    target_mass = [value / target_total for value in target_mass]
    cost = [
        [
            (float(source["x"]) - float(target["x"])) ** 2
            + (float(source["y"]) - float(target["y"])) ** 2
            for target in targets
        ]
        for source in sources
    ]
    kernel = [[math.exp(-value / epsilon) for value in row] for row in cost]
    u = [1.0] * site_count
    v = [1.0] * site_count
    scaling_states: list[tuple[list[float], list[float]]] = [(list(u), list(v))]
    residual_history: list[dict[str, object]] = []
    checkpoints = set(
        _frame_steps(minimum_iterations, min(frame_count, minimum_iterations + 1))[1:]
    )
    maximum_iterations = min(
        2000, max(minimum_iterations + 8, minimum_iterations * 8)
    )
    convergence_tolerance = 1e-7
    actual_iterations = maximum_iterations

    def plan_from_scalings(
        row_scaling: list[float], column_scaling: list[float]
    ) -> list[list[float]]:
        return [
            [
                row_scaling[row] * kernel[row][column] * column_scaling[column]
                for column in range(site_count)
            ]
            for row in range(site_count)
        ]

    def plan_residuals(plan_snapshot: list[list[float]]) -> tuple[float, float, float]:
        maximum_row_error = max(
            abs(sum(plan_snapshot[row]) - source_mass[row])
            for row in range(site_count)
        )
        maximum_column_error = max(
            abs(
                sum(plan_snapshot[row][column] for row in range(site_count))
                - target_mass[column]
            )
            for column in range(site_count)
        )
        mass_error = abs(sum(sum(row) for row in plan_snapshot) - 1.0)
        return maximum_row_error, maximum_column_error, mass_error

    for iteration in range(1, maximum_iterations + 1):
        for row in range(site_count):
            denominator = sum(kernel[row][column] * v[column] for column in range(site_count))
            u[row] = source_mass[row] / max(denominator, 1e-300)
        for column in range(site_count):
            denominator = sum(kernel[row][column] * u[row] for row in range(site_count))
            v[column] = target_mass[column] / max(denominator, 1e-300)
        scaling_states.append((list(u), list(v)))
        measure_residual = iteration in checkpoints or (
            iteration >= minimum_iterations
            and (
                (iteration - minimum_iterations) % 4 == 0
                or iteration == maximum_iterations
            )
        )
        if measure_residual:
            plan_snapshot = plan_from_scalings(u, v)
            row_error, column_error, mass_error = plan_residuals(plan_snapshot)
            residual_history.append(
                {
                    "iteration": iteration,
                    "maxRowError": row_error,
                    "maxColumnError": column_error,
                    "massError": mass_error,
                }
            )
            if (
                iteration >= minimum_iterations
                and row_error <= convergence_tolerance
                and column_error <= convergence_tolerance
            ):
                actual_iterations = iteration
                break
    plan = plan_from_scalings(u, v)
    row_error, column_error, mass_error = plan_residuals(plan)
    checkpoint_count = min(frame_count, actual_iterations + 1)
    checkpoint_iterations = _frame_steps(actual_iterations, checkpoint_count)
    scaling_checkpoints: list[dict[str, object]] = []
    residual_by_iteration = {
        int(record["iteration"]): record for record in residual_history
    }
    for iteration in checkpoint_iterations:
        checkpoint_u, checkpoint_v = scaling_states[iteration]
        checkpoint_plan = plan_from_scalings(checkpoint_u, checkpoint_v)
        checkpoint_row_error, checkpoint_column_error, checkpoint_mass_error = (
            plan_residuals(checkpoint_plan)
        )
        scaling_checkpoints.append(
            {
                "iteration": iteration,
                "u": checkpoint_u,
                "v": checkpoint_v,
                "maxRowError": checkpoint_row_error,
                "maxColumnError": checkpoint_column_error,
                "massError": checkpoint_mass_error,
            }
        )
        residual_by_iteration.setdefault(
            iteration,
            {
                "iteration": iteration,
                "maxRowError": checkpoint_row_error,
                "maxColumnError": checkpoint_column_error,
                "massError": checkpoint_mass_error,
            },
        )
    residual_history = [
        residual_by_iteration[iteration]
        for iteration in sorted(residual_by_iteration)
        if iteration <= actual_iterations
    ]
    frames: list[dict[str, object]] = []
    for frame_id in range(frame_count):
        phase = frame_id / (frame_count - 1)
        checkpoint_index = round(
            frame_id * (len(scaling_checkpoints) - 1) / (frame_count - 1)
        )
        checkpoint = scaling_checkpoints[checkpoint_index]
        links: list[dict[str, object]] = []
        for row, source in enumerate(sources):
            for column, target in enumerate(targets):
                links.append(
                    {
                        "source": row,
                        "target": column,
                        "mass": plan[row][column],
                        "x": (1.0 - phase) * float(source["x"]) + phase * float(target["x"]),
                        "y": (1.0 - phase) * float(source["y"]) + phase * float(target["y"]),
                    }
                )
        frames.append(
            {
                "index": frame_id,
                "phase": phase,
                "sinkhornCheckpointIndex": checkpoint_index,
                "sinkhornIteration": checkpoint["iteration"],
                "links": links,
                "sourceMass": source_mass,
                "targetMass": target_mass,
            }
        )
    metrics: dict[str, object] = {
        "transport.maxRowError": row_error,
        "transport.maxColumnError": column_error,
        "transport.massError": mass_error,
        "transport.scalingReconstructionMaxError": max(
            abs(
                plan[row][column]
                - u[row] * kernel[row][column] * v[column]
            )
            for row in range(site_count)
            for column in range(site_count)
        ),
        "negativeEntryCount": sum(value < -1e-15 for row in plan for value in row),
        "scalingCheckpointCount": len(scaling_checkpoints),
        "residualSampleCount": len(residual_history),
        "iterations": actual_iterations,
    }
    geometry: dict[str, object] = {
        "coordinateSpace": "normalized",
        "sources": [dict(site, mass=source_mass[index]) for index, site in enumerate(sources)],
        "targets": [dict(site, mass=target_mass[index]) for index, site in enumerate(targets)],
        "costMatrix": cost,
        "gibbsKernel": kernel,
        "plan": plan,
        "residualHistory": residual_history,
        "sinkhornScalingEvidence": {
            "precision": "15-significant-decimal-digits",
            "sourceMass": source_mass,
            "targetMass": target_mass,
            "kernel": kernel,
            "u": list(u),
            "v": list(v),
            "checkpoints": scaling_checkpoints,
            "convergenceTolerance": convergence_tolerance,
        },
    }
    return geometry, frames, frame_count // 2, metrics


def _upwind_arrival(
    cell: int,
    columns: int,
    rows: int,
    speed: list[float],
    arrivals: list[float],
    accepted: list[bool],
) -> float:
    column = cell % columns
    row = cell // columns
    horizontal = [
        arrivals[row * columns + neighbor]
        for neighbor in (column - 1, column + 1)
        if 0 <= neighbor < columns and accepted[row * columns + neighbor]
    ]
    vertical = [
        arrivals[neighbor * columns + column]
        for neighbor in (row - 1, row + 1)
        if 0 <= neighbor < rows and accepted[neighbor * columns + column]
    ]
    a = min(horizontal, default=math.inf)
    b = min(vertical, default=math.inf)
    hx = 1.0 / (columns - 1)
    hy = 1.0 / (rows - 1)
    inverse_speed = 1.0 / speed[cell]
    candidates: list[float] = []
    if math.isfinite(a):
        candidates.append(a + hx * inverse_speed)
    if math.isfinite(b):
        candidates.append(b + hy * inverse_speed)
    if math.isfinite(a) and math.isfinite(b):
        coefficient_a = 1.0 / (hx * hx) + 1.0 / (hy * hy)
        coefficient_b = -2.0 * (a / (hx * hx) + b / (hy * hy))
        coefficient_c = a * a / (hx * hx) + b * b / (hy * hy) - inverse_speed**2
        discriminant = max(0.0, coefficient_b * coefficient_b - 4.0 * coefficient_a * coefficient_c)
        root = (-coefficient_b + math.sqrt(discriminant)) / (2.0 * coefficient_a)
        if root >= max(a, b) - 1e-12:
            candidates.append(root)
    return min(candidates, default=math.inf)


def _fast_marching_run(
    columns: int,
    rows: int,
    speed: list[float],
    source: int,
    *,
    capture_times: list[float] | None,
) -> tuple[list[float], list[tuple[int, float]], list[dict[str, object]]]:
    """Run Fast Marching and snapshot the real heap at requested times."""

    count = columns * rows
    arrivals = [math.inf] * count
    accepted = [False] * count
    arrivals[source] = 0.0
    heap: list[tuple[float, int]] = [(0.0, source)]
    order: list[tuple[int, float]] = []
    trial_states: list[dict[str, object]] = []
    requested_times = list(capture_times or [])
    capture_index = 0

    def capture_state(capture_time: float) -> None:
        trial_by_cell: dict[int, float] = {}
        stale_entry_count = 0
        for trial_time, trial_cell in heap:
            if (
                accepted[trial_cell]
                or abs(trial_time - arrivals[trial_cell]) > 1e-14
            ):
                stale_entry_count += 1
                continue
            trial_by_cell[trial_cell] = trial_time
        trial_cell_ids = sorted(trial_by_cell)
        trial_states.append(
            {
                "captureTime": capture_time,
                "acceptedCount": len(order),
                "acceptedTime": order[-1][1] if order else None,
                "acceptedCellIds": [
                    cell for cell, is_accepted in enumerate(accepted) if is_accepted
                ],
                "trialCellIds": trial_cell_ids,
                "trialArrivalTimes": [
                    trial_by_cell[trial_cell] for trial_cell in trial_cell_ids
                ],
                "heapEntryCount": len(heap),
                "staleHeapEntryCount": stale_entry_count,
            }
        )

    while heap or capture_index < len(requested_times):
        while heap:
            value, cell = heap[0]
            if accepted[cell] or value > arrivals[cell] + 1e-14:
                heapq.heappop(heap)
            else:
                break
        next_arrival = heap[0][0] if heap else math.inf
        if (
            capture_index < len(requested_times)
            and requested_times[capture_index] < next_arrival - 1e-12
        ):
            capture_state(requested_times[capture_index])
            capture_index += 1
            continue
        if not heap:
            break
        value, cell = heapq.heappop(heap)
        accepted[cell] = True
        order.append((cell, value))
        column = cell % columns
        row = cell // columns
        neighbors = []
        if column > 0:
            neighbors.append(cell - 1)
        if column + 1 < columns:
            neighbors.append(cell + 1)
        if row > 0:
            neighbors.append(cell - columns)
        if row + 1 < rows:
            neighbors.append(cell + columns)
        for neighbor in neighbors:
            if accepted[neighbor]:
                continue
            candidate = _upwind_arrival(neighbor, columns, rows, speed, arrivals, accepted)
            if candidate + 1e-14 < arrivals[neighbor]:
                arrivals[neighbor] = candidate
                heapq.heappush(heap, (candidate, neighbor))
    return arrivals, order, trial_states


def _fast_marching_solve(
    columns: int, rows: int, speed: list[float], source: int
) -> tuple[list[float], list[tuple[int, float]]]:
    """Preserve the compact solver API for callers that do not need heap strata."""

    arrivals, order, _ = _fast_marching_run(
        columns,
        rows,
        speed,
        source,
        capture_times=None,
    )
    return arrivals, order


def _fast_marching(
    seed: int, parameters: dict[str, int | float]
) -> tuple[dict[str, object], list[dict[str, object]], int, dict[str, object]]:
    columns = int(parameters["grid_columns"])
    rows = int(parameters["grid_rows"])
    frame_count = int(parameters["frame_count"])
    speed_modulation = float(parameters["speed_modulation"])
    rng = random.Random(seed ^ 0xF45A71)
    phase_offset = 2.0 * math.pi * rng.random()
    cross_phase = 2.0 * math.pi * rng.random()
    channel_center = 0.25 + 0.50 * rng.random()
    channel_sign = -1.0 if rng.random() < 0.5 else 1.0
    speed: list[float] = []
    points: list[tuple[float, float]] = []
    for row in range(rows):
        y = row / (rows - 1)
        for column in range(columns):
            x = column / (columns - 1)
            points.append((x, y))
            modulation = 0.54 * math.sin(2.0 * math.pi * x + phase_offset) * math.cos(
                math.pi * y + 0.25 * cross_phase
            )
            modulation += 0.20 * math.sin(2.0 * math.pi * y + cross_phase)
            modulation += channel_sign * 0.20 * math.exp(
                -((x - channel_center) ** 2 + (y - 0.5) ** 2) / 0.055
            )
            speed.append(max(0.25, 1.0 + speed_modulation * modulation))
    source_column = max(1, columns // 5)
    source_row = rows // 2
    source = source_row * columns + source_column
    arrivals, accepted_order = _fast_marching_solve(columns, rows, speed, source)
    control, _ = _fast_marching_solve(columns, rows, [1.0] * len(speed), source)
    source_x, source_y = points[source]
    analytic_error = max(
        abs(value - math.hypot(points[cell][0] - source_x, points[cell][1] - source_y))
        for cell, value in enumerate(control)
    )
    order_errors = sum(
        accepted_order[index][1] + 1e-12 < accepted_order[index - 1][1]
        for index in range(1, len(accepted_order))
    )
    finite_arrivals = [value for value in arrivals if math.isfinite(value)]
    maximum = max(finite_arrivals)
    frame_times = [
        maximum * frame_id / (frame_count - 1)
        for frame_id in range(frame_count)
    ]
    traced_arrivals, traced_order, trial_states = _fast_marching_run(
        columns,
        rows,
        speed,
        source,
        capture_times=frame_times,
    )
    if traced_arrivals != arrivals or traced_order != accepted_order:
        raise RuntimeError("Fast Marching heap trace diverged from the canonical solve")
    triangles = _grid_triangles(columns, rows)
    frames: list[dict[str, object]] = []
    for frame_id, trial_state in enumerate(trial_states):
        phase = frame_id / (frame_count - 1)
        threshold = frame_times[frame_id]
        accepted_prefix = trial_state["acceptedCellIds"]
        trial_cell_ids = trial_state["trialCellIds"]
        trial_arrival_times = trial_state["trialArrivalTimes"]
        assert isinstance(accepted_prefix, list)
        assert isinstance(trial_cell_ids, list)
        assert isinstance(trial_arrival_times, list)
        frames.append(
            {
                "index": frame_id,
                "phase": phase,
                "time": threshold,
                "acceptedCellIds": sorted(accepted_prefix),
                "trialCellIds": list(trial_cell_ids),
                "trialArrivalTimes": list(trial_arrival_times),
                "trialHeapEntryCount": trial_state["heapEntryCount"],
                "trialStaleHeapEntryCount": trial_state["staleHeapEntryCount"],
                "frontSegments": _contour_segments(points, triangles, arrivals, threshold),
            }
        )
    trial_disjoint_errors = 0
    trial_finite_errors = 0
    trial_causality_errors = 0
    trial_capture_errors = 0
    for frame in frames:
        threshold = float(frame["time"])
        accepted_ids = frame["acceptedCellIds"]
        trial_cell_ids = frame["trialCellIds"]
        trial_arrival_times = frame["trialArrivalTimes"]
        assert isinstance(accepted_ids, list)
        assert isinstance(trial_cell_ids, list)
        assert isinstance(trial_arrival_times, list)
        accepted_set = {int(cell) for cell in accepted_ids}
        trial_set = {int(cell) for cell in trial_cell_ids}
        if (
            len(accepted_set) != len(accepted_ids)
            or len(trial_set) != len(trial_cell_ids)
            or accepted_set & trial_set
        ):
            trial_disjoint_errors += 1
        if len(trial_cell_ids) != len(trial_arrival_times):
            trial_capture_errors += 1
            continue
        expected_accepted = {
            cell
            for cell, arrival in enumerate(arrivals)
            if arrival <= threshold + 1e-12
        }
        if accepted_set != expected_accepted:
            trial_capture_errors += 1
        for trial_cell, tentative_time in zip(
            trial_cell_ids, trial_arrival_times, strict=True
        ):
            cell = int(trial_cell)
            tentative = float(tentative_time)
            if not math.isfinite(tentative):
                trial_finite_errors += 1
                continue
            if (
                tentative + 1e-12 < threshold
                or tentative + 1e-12 < arrivals[cell]
            ):
                trial_causality_errors += 1
            column = cell % columns
            row = cell // columns
            neighbors = []
            if column > 0:
                neighbors.append(cell - 1)
            if column + 1 < columns:
                neighbors.append(cell + 1)
            if row > 0:
                neighbors.append(cell - columns)
            if row + 1 < rows:
                neighbors.append(cell + columns)
            if not any(neighbor in accepted_set for neighbor in neighbors):
                trial_causality_errors += 1
        if len(accepted_set) < len(arrivals) and not trial_set:
            trial_capture_errors += 1
    trial_state_errors = (
        trial_disjoint_errors
        + trial_finite_errors
        + trial_causality_errors
        + trial_capture_errors
    )
    metrics: dict[str, object] = {
        "front.acceptedOrderErrors": order_errors,
        "front.analyticMaxError": analytic_error,
        "front.unreachableTargets": sum(not math.isfinite(value) for value in arrivals),
        "front.trialStateErrors": trial_state_errors,
        "front.trialDisjointErrors": trial_disjoint_errors,
        "front.trialFiniteErrors": trial_finite_errors,
        "front.trialCausalityErrors": trial_causality_errors,
        "front.trialCaptureErrors": trial_capture_errors,
        "acceptedCount": len(accepted_order),
        "maxArrivalTime": maximum,
        "minSpeed": min(speed),
        "maxSpeed": max(speed),
    }
    geometry: dict[str, object] = {
        "coordinateSpace": "normalized",
        "columns": columns,
        "rows": rows,
        "source": {"id": source, "column": source_column, "row": source_row, "x": source_x, "y": source_y},
        "speedField": speed,
        "arrivalTimes": arrivals,
        "acceptedOrder": [{"cell": cell, "time": value} for cell, value in accepted_order],
    }
    return geometry, frames, frame_count // 2, metrics


def _bilinear(field: list[float], columns: int, rows: int, x: float, y: float) -> float:
    x = min(columns - 1.001, max(0.0, x))
    y = min(rows - 1.001, max(0.0, y))
    x0 = int(x)
    y0 = int(y)
    x1 = min(columns - 1, x0 + 1)
    y1 = min(rows - 1, y0 + 1)
    tx = x - x0
    ty = y - y0
    return (
        field[y0 * columns + x0] * (1.0 - tx) * (1.0 - ty)
        + field[y0 * columns + x1] * tx * (1.0 - ty)
        + field[y1 * columns + x0] * (1.0 - tx) * ty
        + field[y1 * columns + x1] * tx * ty
    )


def _network_site_evidence(
    network_field: list[float],
    columns: int,
    rows: int,
    nutrient_sites: tuple[tuple[float, float], ...],
) -> tuple[
    float,
    list[int],
    list[int],
    list[dict[str, object]],
    list[list[int]],
    int | None,
]:
    """Threshold one network field and extract sparse audited site paths.

    The predecessor tree uses one deterministic active cell nearest the central
    inoculum. One shortest path is retained for each connected nutrient site;
    the union of those paths is a compact, visibly connected backbone.
    """

    maximum = max(network_field, default=0.0)
    if maximum <= 0.0:
        return 0.0, [], [], [], [], None
    threshold = max(0.025, 0.04 * maximum)
    active = {cell for cell, value in enumerate(network_field) if value >= threshold}
    site_radius_squared = 4.0**2

    def cells_near(x: float, y: float) -> set[int]:
        center_x = x * (columns - 1)
        center_y = y * (rows - 1)
        return {
            cell
            for cell in active
            if (cell % columns - center_x) ** 2 + (cell // columns - center_y) ** 2
            <= site_radius_squared
        }

    site_cells = [cells_near(site_x, site_y) for site_x, site_y in nutrient_sites]
    reached = [site_id for site_id, nearby in enumerate(site_cells) if nearby]
    inoculum_x = 0.5 * (columns - 1)
    inoculum_y = 0.5 * (rows - 1)
    inoculum_cells = sorted(
        cell
        for cell in active
        if (cell % columns - inoculum_x) ** 2 + (cell // columns - inoculum_y) ** 2
        <= site_radius_squared
    )
    frontier = (
        [
            min(
                inoculum_cells,
                key=lambda cell: (
                    (cell % columns - inoculum_x) ** 2
                    + (cell // columns - inoculum_y) ** 2,
                    cell,
                ),
            )
        ]
        if inoculum_cells
        else []
    )
    root_cell = frontier[0] if frontier else None
    connected = set(frontier)
    predecessor: dict[int, int | None] = {cell: None for cell in frontier}
    distance = {cell: 0 for cell in frontier}
    cursor = 0
    while cursor < len(frontier):
        cell = frontier[cursor]
        cursor += 1
        column = cell % columns
        row = cell // columns
        for neighbor_row in range(max(0, row - 1), min(rows, row + 2)):
            for neighbor_column in range(max(0, column - 1), min(columns, column + 2)):
                neighbor = neighbor_row * columns + neighbor_column
                if neighbor in active and neighbor not in connected:
                    connected.add(neighbor)
                    predecessor[neighbor] = cell
                    distance[neighbor] = distance[cell] + 1
                    frontier.append(neighbor)
    connected_sites = [
        site_id for site_id, nearby in enumerate(site_cells) if nearby & connected
    ]
    network_paths: list[dict[str, object]] = []
    network_edges: set[tuple[int, int]] = set()
    for site_id in connected_sites:
        site_x, site_y = nutrient_sites[site_id]
        center_x = site_x * (columns - 1)
        center_y = site_y * (rows - 1)
        target = min(
            site_cells[site_id] & connected,
            key=lambda cell: (
                (cell % columns - center_x) ** 2 + (cell // columns - center_y) ** 2,
                distance[cell],
                cell,
            ),
        )
        path = [target]
        while predecessor[path[-1]] is not None:
            parent = predecessor[path[-1]]
            assert parent is not None
            path.append(parent)
        path.reverse()
        network_paths.append({"nutrientSiteId": site_id, "cellIds": path})
        network_edges.update(zip(path, path[1:]))
    return (
        threshold,
        reached,
        connected_sites,
        network_paths,
        [list(edge) for edge in sorted(network_edges)],
        root_cell,
    )


def _audit_network_backbone(
    network_paths: list[dict[str, object]],
    network_edges: list[list[int]],
    connected_sites: list[int],
    columns: int,
    expected_root: int | None,
) -> int:
    """Count structural errors in the sparse rooted Physarum backbone."""

    errors = 0
    if not connected_sites:
        return int(bool(network_paths)) + int(bool(network_edges))
    path_by_site: dict[int, list[int]] = {}
    expected_edges: set[tuple[int, int]] = set()
    roots: set[int] = set()
    for record in network_paths:
        site_id = int(record["nutrientSiteId"])
        cells = [int(cell) for cell in record["cellIds"]]  # type: ignore[index]
        if site_id in path_by_site or not cells:
            errors += 1
            continue
        path_by_site[site_id] = cells
        roots.add(cells[0])
        for left, right in zip(cells, cells[1:]):
            column_delta = abs(left % columns - right % columns)
            row_delta = abs(left // columns - right // columns)
            if max(column_delta, row_delta) != 1:
                errors += 1
            expected_edges.add((left, right))
    errors += len(set(connected_sites) ^ set(path_by_site))
    if expected_root is None or roots != {expected_root}:
        errors += max(1, len(roots ^ ({expected_root} if expected_root is not None else set())))
    actual_edges = {(int(edge[0]), int(edge[1])) for edge in network_edges if len(edge) == 2}
    errors += len(actual_edges ^ expected_edges)
    if len(actual_edges) != len(network_edges):
        errors += len(network_edges) - len(actual_edges)
    if roots:
        adjacency: dict[int, set[int]] = {}
        for left, right in actual_edges:
            adjacency.setdefault(left, set()).add(right)
            adjacency.setdefault(right, set()).add(left)
        reached = set(roots)
        frontier = list(roots)
        while frontier:
            cell = frontier.pop()
            for neighbor in adjacency.get(cell, set()):
                if neighbor not in reached:
                    reached.add(neighbor)
                    frontier.append(neighbor)
        errors += sum(cell not in reached for cells in path_by_site.values() for cell in cells)
    return errors


def _physarum(
    seed: int, parameters: dict[str, int | float]
) -> tuple[dict[str, object], list[dict[str, object]], int, dict[str, object]]:
    agent_count = int(parameters["agent_count"])
    steps = int(parameters["steps"])
    frame_count = int(parameters["frame_count"])
    sensor_offset = float(parameters["sensor_offset"])
    columns = 48
    rows = 30
    rng = random.Random(seed ^ 0x9A75A)
    nutrient_base: list[float] = []
    nutrient_sites = ((0.18, 0.22), (0.80, 0.20), (0.22, 0.78), (0.79, 0.76), (0.50, 0.10))
    for row in range(rows):
        y = row / (rows - 1)
        for column in range(columns):
            x = column / (columns - 1)
            nutrient_base.append(
                min(
                    1.0,
                    sum(math.exp(-((x - sx) ** 2 + (y - sy) ** 2) / 0.009) for sx, sy in nutrient_sites),
                )
            )
    nutrient = list(nutrient_base)
    trail = [0.0] * (columns * rows)
    network_field = [0.0] * len(trail)
    target_cells = [cell for cell, value in enumerate(nutrient_base) if value >= 0.55]
    deposition_counts = [0] * len(trail)
    agents: list[list[float]] = []
    agent_targets: list[int] = []
    for agent_id in range(agent_count):
        target_site = agent_id % len(nutrient_sites)
        target_x = nutrient_sites[target_site][0] * (columns - 1)
        target_y = nutrient_sites[target_site][1] * (rows - 1)
        angle = math.atan2(target_y - 0.5 * (rows - 1), target_x - 0.5 * (columns - 1))
        angle += (rng.random() - 0.5) * 0.16
        radius = 0.6 + 1.2 * rng.random()
        x = 0.5 * (columns - 1) + radius * math.cos(angle)
        y = 0.5 * (rows - 1) + radius * math.sin(angle)
        heading = (angle + (rng.random() - 0.5) * 0.14) % (2.0 * math.pi)
        agents.append([x, y, heading])
        agent_targets.append(target_site)
    capture_steps = set(_frame_steps(steps, frame_count))
    frames: list[dict[str, object]] = []
    out_of_bounds = 0
    sensor_angle = math.pi / 4.0
    turn_angle = math.pi / 5.0
    guidance_steps = max(1, steps // 3)
    burn_in_steps = max(1, steps // 5)

    def capture(step: int, deposited_trail: list[float]) -> None:
        (
            network_threshold,
            reached_sites,
            connected_sites,
            network_paths,
            network_edges,
            network_root,
        ) = _network_site_evidence(network_field, columns, rows, nutrient_sites)
        if step < burn_in_steps:
            reached_sites = []
            connected_sites = []
            network_paths = []
            network_edges = []
            network_root = None
        frames.append(
            {
                "index": len(frames),
                "phase": step / steps,
                "step": step,
                "agents": [
                    {"x": agent[0], "y": agent[1], "heading": agent[2]} for agent in agents
                ],
                "depositedTrailField": list(deposited_trail),
                "trailField": list(trail),
                "networkField": list(network_field),
                "networkThreshold": network_threshold,
                "reachedNutrientSiteIds": reached_sites,
                "connectedNutrientSiteIds": connected_sites,
                "networkPaths": network_paths,
                "networkEdges": network_edges,
                "networkRootCellId": network_root,
                "nutrientField": list(nutrient),
                "depositedTargetCellIds": [
                    cell for cell in target_cells if deposition_counts[cell] > 0
                ],
            }
        )

    capture(0, list(trail))
    for step in range(1, steps + 1):
        for agent_id, agent in enumerate(agents):
            x, y, heading = agent
            signals = []
            for offset_angle in (-sensor_angle, 0.0, sensor_angle):
                sensor_x = x + sensor_offset * math.cos(heading + offset_angle)
                sensor_y = y + sensor_offset * math.sin(heading + offset_angle)
                signal = _bilinear(trail, columns, rows, sensor_x, sensor_y)
                signal += 2.2 * _bilinear(nutrient, columns, rows, sensor_x, sensor_y)
                signals.append(signal)
            left, forward, right = signals
            if forward >= left and forward >= right:
                turn = 0.0
            elif left > right:
                turn = -turn_angle
            elif right > left:
                turn = turn_angle
            else:
                turn = turn_angle if rng.random() >= 0.5 else -turn_angle
            if step <= guidance_steps:
                target_site = nutrient_sites[agent_targets[agent_id]]
                desired = math.atan2(
                    target_site[1] * (rows - 1) - y,
                    target_site[0] * (columns - 1) - x,
                )
                heading_error = (desired - heading + math.pi) % (2.0 * math.pi) - math.pi
                guided_turn = max(-0.16, min(0.16, heading_error))
                turn = 0.20 * turn + guided_turn
            heading = (heading + turn + (rng.random() - 0.5) * 0.08) % (2.0 * math.pi)
            x += math.cos(heading)
            y += math.sin(heading)
            if x < 0.5 or x > columns - 1.5:
                x = min(columns - 1.5, max(0.5, x))
                heading = (math.pi - heading) % (2.0 * math.pi)
            if y < 0.5 or y > rows - 1.5:
                y = min(rows - 1.5, max(0.5, y))
                heading = (-heading) % (2.0 * math.pi)
            agent[:] = [x, y, heading]
            if not (0.0 <= x < columns and 0.0 <= y < rows):
                out_of_bounds += 1
            cell = int(round(y)) * columns + int(round(x))
            cell = min(len(trail) - 1, max(0, cell))
            deposition_counts[cell] += 1
            trail[cell] += 1.25
            nutrient[cell] = max(0.0, nutrient[cell] - 0.008)

        deposited_trail = list(trail)
        diffused = [0.0] * len(trail)
        for row in range(rows):
            for column in range(columns):
                cell = row * columns + column
                neighbors = [
                    trail[neighbor_row * columns + neighbor_column]
                    for neighbor_row in range(max(0, row - 1), min(rows, row + 2))
                    for neighbor_column in range(max(0, column - 1), min(columns, column + 2))
                ]
                diffused[cell] = (0.72 * trail[cell] + 0.28 * sum(neighbors) / len(neighbors)) * 0.965
        trail = diffused
        for cell in range(len(nutrient)):
            nutrient[cell] += 0.0025 * (nutrient_base[cell] - nutrient[cell])
            network_field[cell] = max(0.998 * network_field[cell], trail[cell])
        if step in capture_steps:
            capture(step, deposited_trail)

    nonfinite_count = sum(
        not math.isfinite(value)
        for value in trail
        + nutrient
        + network_field
        + [coordinate for agent in agents for coordinate in agent]
    )
    covered_cells = sum(deposition_counts[cell] > 0 for cell in target_cells)
    (
        network_threshold,
        reached_sites,
        connected_sites,
        network_paths,
        network_edges,
        network_root,
    ) = _network_site_evidence(network_field, columns, rows, nutrient_sites)
    network_backbone_errors = _audit_network_backbone(
        network_paths, network_edges, connected_sites, columns, network_root
    )
    metrics: dict[str, object] = {
        "physarum.nonfiniteCount": nonfinite_count,
        "physarum.outOfBounds": out_of_bounds,
        "physarum.nutrientCoverage": covered_cells / max(1, len(target_cells)),
        "physarum.nutrientSiteReach": len(reached_sites) / len(nutrient_sites),
        "physarum.networkConnectedSiteReach": len(connected_sites) / len(nutrient_sites),
        "physarum.networkBackboneErrors": network_backbone_errors,
        "networkThreshold": network_threshold,
        "reachedSiteCount": len(reached_sites),
        "connectedSiteCount": len(connected_sites),
        "networkPathCount": len(network_paths),
        "networkBackboneEdgeCount": len(network_edges),
        "networkRootCellId": network_root,
        "networkBurnInSteps": burn_in_steps,
        "trailMass": sum(trail),
        "agentCount": agent_count,
        "steps": steps,
    }
    geometry: dict[str, object] = {
        "coordinateSpace": "grid",
        "columns": columns,
        "rows": rows,
        "nutrientField": nutrient_base,
        "nutrientTargetCellIds": target_cells,
        "nutrientSites": [{"x": x * (columns - 1), "y": y * (rows - 1)} for x, y in nutrient_sites],
        "model": {
            "base": "Jones-inspired three-sensor agent and diffusing trail model",
            "adaptations": [
                "central inoculum with stratified outward headings",
                "bounded one-third-horizon nutrient-directed guidance",
                "bounded nutrient coupling and consumption",
                "decayed cumulative network field for extraction",
                "thresholded site reach and inoculum-connected site audit",
                "predecessor-extracted sparse auditable network backbone",
            ],
            "burnInSteps": burn_in_steps,
            "guidanceSteps": guidance_steps,
        },
    }
    return geometry, frames, len(frames) - 1, metrics


def _fluid_set_boundary(boundary: int, field: list[float], columns: int, rows: int) -> None:
    stride = columns + 2
    for row in range(1, rows + 1):
        field[row * stride] = -field[row * stride + 1] if boundary == 1 else field[row * stride + 1]
        field[row * stride + columns + 1] = (
            -field[row * stride + columns] if boundary == 1 else field[row * stride + columns]
        )
    for column in range(1, columns + 1):
        field[column] = -field[stride + column] if boundary == 2 else field[stride + column]
        field[(rows + 1) * stride + column] = (
            -field[rows * stride + column] if boundary == 2 else field[rows * stride + column]
        )
    field[0] = 0.5 * (field[1] + field[stride])
    field[columns + 1] = 0.5 * (field[columns] + field[stride + columns + 1])
    field[(rows + 1) * stride] = 0.5 * (field[rows * stride] + field[(rows + 1) * stride + 1])
    field[(rows + 2) * stride - 1] = 0.5 * (
        field[(rows + 1) * stride + columns] + field[rows * stride + columns + 1]
    )


def _fluid_diffuse(
    boundary: int,
    source: list[float],
    diffusion: float,
    delta_time: float,
    columns: int,
    rows: int,
    iterations: int = 18,
) -> list[float]:
    stride = columns + 2
    result = list(source)
    ax = delta_time * diffusion * columns * columns
    ay = delta_time * diffusion * rows * rows
    denominator = 1.0 + 2.0 * (ax + ay)
    for _ in range(iterations):
        for row in range(1, rows + 1):
            for column in range(1, columns + 1):
                cell = row * stride + column
                result[cell] = (
                    source[cell]
                    + ax * (result[cell - 1] + result[cell + 1])
                    + ay * (result[cell - stride] + result[cell + stride])
                ) / denominator
        _fluid_set_boundary(boundary, result, columns, rows)
    return result


def _fluid_advect(
    boundary: int,
    source: list[float],
    velocity_x: list[float],
    velocity_y: list[float],
    delta_time: float,
    columns: int,
    rows: int,
) -> list[float]:
    stride = columns + 2
    result = [0.0] * len(source)
    for row in range(1, rows + 1):
        for column in range(1, columns + 1):
            cell = row * stride + column
            x = min(columns + 0.5, max(0.5, column - delta_time * columns * velocity_x[cell]))
            y = min(rows + 0.5, max(0.5, row - delta_time * rows * velocity_y[cell]))
            x0 = int(math.floor(x))
            x1 = x0 + 1
            y0 = int(math.floor(y))
            y1 = y0 + 1
            sx = x - x0
            sy = y - y0
            result[cell] = (
                (1.0 - sx) * ((1.0 - sy) * source[y0 * stride + x0] + sy * source[y1 * stride + x0])
                + sx * ((1.0 - sy) * source[y0 * stride + x1] + sy * source[y1 * stride + x1])
            )
    _fluid_set_boundary(boundary, result, columns, rows)
    return result


def _fluid_project(
    velocity_x: list[float], velocity_y: list[float], columns: int, rows: int, iterations: int = 32
) -> tuple[list[float], list[float], list[float]]:
    stride = columns + 2
    hx = 1.0 / columns
    hy = 1.0 / rows
    inv_hx2 = 1.0 / (hx * hx)
    inv_hy2 = 1.0 / (hy * hy)
    denominator = 2.0 * (inv_hx2 + inv_hy2)
    divergence = [0.0] * len(velocity_x)
    pressure = [0.0] * len(velocity_x)
    for row in range(1, rows + 1):
        for column in range(1, columns + 1):
            cell = row * stride + column
            divergence[cell] = (
                (velocity_x[cell + 1] - velocity_x[cell - 1]) / (2.0 * hx)
                + (velocity_y[cell + stride] - velocity_y[cell - stride]) / (2.0 * hy)
            )
    _fluid_set_boundary(0, divergence, columns, rows)
    _fluid_set_boundary(0, pressure, columns, rows)
    for _ in range(iterations):
        for row in range(1, rows + 1):
            for column in range(1, columns + 1):
                cell = row * stride + column
                pressure[cell] = (
                    inv_hx2 * (pressure[cell - 1] + pressure[cell + 1])
                    + inv_hy2 * (pressure[cell - stride] + pressure[cell + stride])
                    - divergence[cell]
                ) / denominator
        _fluid_set_boundary(0, pressure, columns, rows)
    projected_x = list(velocity_x)
    projected_y = list(velocity_y)
    for row in range(1, rows + 1):
        for column in range(1, columns + 1):
            cell = row * stride + column
            projected_x[cell] -= (pressure[cell + 1] - pressure[cell - 1]) / (2.0 * hx)
            projected_y[cell] -= (pressure[cell + stride] - pressure[cell - stride]) / (2.0 * hy)
    _fluid_set_boundary(1, projected_x, columns, rows)
    _fluid_set_boundary(2, projected_y, columns, rows)
    residual = [0.0] * len(velocity_x)
    for row in range(1, rows + 1):
        for column in range(1, columns + 1):
            cell = row * stride + column
            residual[cell] = (
                (projected_x[cell + 1] - projected_x[cell - 1]) / (2.0 * hx)
                + (projected_y[cell + stride] - projected_y[cell - stride]) / (2.0 * hy)
            )
    return projected_x, projected_y, residual


def _fluid_divergence_field(
    velocity_x: list[float], velocity_y: list[float], columns: int, rows: int
) -> list[float]:
    """Measure collocated velocity divergence without modifying the field."""

    stride = columns + 2
    hx = 1.0 / columns
    hy = 1.0 / rows
    divergence = [0.0] * len(velocity_x)
    for row in range(1, rows + 1):
        for column in range(1, columns + 1):
            cell = row * stride + column
            divergence[cell] = (
                (velocity_x[cell + 1] - velocity_x[cell - 1]) / (2.0 * hx)
                + (velocity_y[cell + stride] - velocity_y[cell - stride]) / (2.0 * hy)
            )
    return divergence


def _audit_dye_value(value: float) -> tuple[float, int, int, float, int]:
    """Audit a raw dye concentration before returning its bounded value.

    Return ``(bounded, bound_error, clamp, excursion, nonfinite)``.  A bound
    error is an excursion beyond ``DYE_BOUND_TOLERANCE``; clamp telemetry also
    records smaller roundoff corrections.  Nonfinite values are detected before
    sanitization and reported separately instead of being hidden by min/max.
    """

    if not math.isfinite(value):
        return 0.0, 0, 1, 0.0, 1
    excursion = max(0.0, -value, value - 1.0)
    return (
        min(1.0, max(0.0, value)),
        int(excursion > DYE_BOUND_TOLERANCE),
        int(excursion > 0.0),
        excursion,
        0,
    )


def _stable_fluid(
    seed: int, parameters: dict[str, int | float]
) -> tuple[dict[str, object], list[dict[str, object]], int, dict[str, object]]:
    columns = int(parameters["grid_columns"])
    rows = int(parameters["grid_rows"])
    steps = int(parameters["steps"])
    frame_count = int(parameters["frame_count"])
    viscosity = float(parameters["viscosity"])
    stride = columns + 2
    size = (columns + 2) * (rows + 2)
    velocity_x = [0.0] * size
    velocity_y = [0.0] * size
    dye = [0.0] * size
    delta_time = 0.075
    capture_steps = set(_frame_steps(steps, frame_count))
    frames: list[dict[str, object]] = []
    maximum_divergence = 0.0
    maximum_preprojection_divergence = 0.0
    projection_residual_ratio_max = 0.0
    projection_reduction_errors = 0
    dye_bounds_errors = 0
    dye_clamp_count = 0
    maximum_dye_excursion = 0.0
    preclamp_nonfinite_count = 0
    rng = random.Random(seed ^ 0xF10D5A)
    phase = 2.0 * math.pi * rng.random()
    orbit_x = 0.07 + 0.06 * rng.random()
    orbit_y = 0.09 + 0.07 * rng.random()
    swirl_strength = 0.35 + 0.14 * rng.random()
    jet_strength = 0.32 + 0.13 * rng.random()
    inlet_offset = rng.randrange(rows)

    def capture(
        step: int,
        advected_x: list[float],
        advected_y: list[float],
        advected_divergence: list[float],
        projected_divergence: list[float],
        force_center: tuple[float, float],
        inlet_row: int,
    ) -> None:
        advected_vectors: list[dict[str, object]] = []
        projected_vectors: list[dict[str, object]] = []
        for row in range(1, rows + 1, 2):
            for column in range(1, columns + 1, 2):
                cell = row * stride + column
                advected_vectors.append(
                    {"x": column - 0.5, "y": row - 0.5, "u": advected_x[cell], "v": advected_y[cell]}
                )
                projected_vectors.append(
                    {"x": column - 0.5, "y": row - 0.5, "u": velocity_x[cell], "v": velocity_y[cell]}
                )
        frames.append(
            {
                "index": len(frames),
                "phase": step / steps,
                "step": step,
                "forceCenter": {"x": force_center[0], "y": force_center[1]},
                "inletRow": inlet_row - 1,
                "inletColumn": 1,
                "velocity": projected_vectors,
                "advectedVelocity": advected_vectors,
                "projectedVelocity": projected_vectors,
                "dyeField": [
                    dye[row * stride + column]
                    for row in range(1, rows + 1)
                    for column in range(1, columns + 1)
                ],
                "advectedDivergenceField": [
                    advected_divergence[row * stride + column]
                    for row in range(1, rows + 1)
                    for column in range(1, columns + 1)
                ],
                "divergenceField": [
                    projected_divergence[row * stride + column]
                    for row in range(1, rows + 1)
                    for column in range(1, columns + 1)
                ],
            }
        )

    zero_field = [0.0] * size
    initial_center = (
        0.48 + orbit_x * math.cos(phase),
        0.50 + orbit_y * math.sin(phase),
    )
    capture(
        0,
        zero_field,
        zero_field,
        zero_field,
        zero_field,
        initial_center,
        1 + inlet_offset % rows,
    )
    for step in range(1, steps + 1):
        force_x = [0.0] * size
        force_y = [0.0] * size
        dye_source = [0.0] * size
        clock = 2.0 * math.pi * step / steps + phase
        center_x = 0.48 + orbit_x * math.cos(clock)
        center_y = 0.50 + orbit_y * math.sin(clock)
        for row in range(1, rows + 1):
            y = (row - 0.5) / rows
            for column in range(1, columns + 1):
                x = (column - 0.5) / columns
                cell = row * stride + column
                dx = x - center_x
                dy = y - center_y
                envelope = math.exp(-(dx * dx + dy * dy) / 0.025)
                force_x[cell] = -swirl_strength * dy * envelope + 0.07 * envelope
                force_y[cell] = swirl_strength * dx * envelope
        inlet_row = 1 + (inlet_offset + step * 3 // 7) % rows
        for offset in (-1, 0, 1):
            row = min(rows, max(1, inlet_row + offset))
            cell = row * stride + 2
            dye_source[cell] = 5.5 * (1.0 - 0.22 * abs(offset))
            force_x[cell] += jet_strength
        for cell in range(size):
            velocity_x[cell] += delta_time * force_x[cell]
            velocity_y[cell] += delta_time * force_y[cell]
            injection_fraction = min(1.0, delta_time * dye_source[cell])
            dye[cell] += (1.0 - dye[cell]) * injection_fraction
        diffused_x = _fluid_diffuse(1, velocity_x, viscosity, delta_time, columns, rows)
        diffused_y = _fluid_diffuse(2, velocity_y, viscosity, delta_time, columns, rows)
        diffused_x, diffused_y, _ = _fluid_project(diffused_x, diffused_y, columns, rows)
        advected_x = _fluid_advect(1, diffused_x, diffused_x, diffused_y, delta_time, columns, rows)
        advected_y = _fluid_advect(2, diffused_y, diffused_x, diffused_y, delta_time, columns, rows)
        advected_divergence = _fluid_divergence_field(
            advected_x, advected_y, columns, rows
        )
        velocity_x = advected_x
        velocity_y = advected_y
        velocity_x, velocity_y, divergence = _fluid_project(velocity_x, velocity_y, columns, rows)
        # Reproject the collocated field to suppress the residual introduced by
        # semi-Lagrangian interpolation and wall boundary reconstruction.  The
        # pressure iteration count grows with grid resolution because the
        # spectral radius of the discrete Poisson solve approaches one.
        reprojection_count = max(19, max(columns, rows) - 10)
        for _ in range(reprojection_count):
            velocity_x, velocity_y, divergence = _fluid_project(
                velocity_x, velocity_y, columns, rows
            )
        preprojection_max = max(abs(value) for value in advected_divergence)
        postprojection_max = max(abs(value) for value in divergence)
        maximum_preprojection_divergence = max(
            maximum_preprojection_divergence, preprojection_max
        )
        maximum_divergence = max(maximum_divergence, postprojection_max)
        if preprojection_max > 1e-14:
            projection_residual_ratio_max = max(
                projection_residual_ratio_max,
                postprojection_max / preprojection_max,
            )
        if postprojection_max > preprojection_max + 1e-10:
            projection_reduction_errors += 1
        dye_diffused = _fluid_diffuse(0, dye, 0.00035, delta_time, columns, rows)
        dye = _fluid_advect(0, dye_diffused, velocity_x, velocity_y, delta_time, columns, rows)
        for row in range(1, rows + 1):
            for column in range(1, columns + 1):
                cell = row * stride + column
                raw_dye = dye[cell] * 0.994
                (
                    dye[cell],
                    bound_error,
                    clamp,
                    excursion,
                    nonfinite,
                ) = _audit_dye_value(raw_dye)
                dye_bounds_errors += bound_error
                dye_clamp_count += clamp
                maximum_dye_excursion = max(maximum_dye_excursion, excursion)
                preclamp_nonfinite_count += nonfinite
        if step in capture_steps:
            capture(
                step,
                advected_x,
                advected_y,
                advected_divergence,
                divergence,
                (center_x, center_y),
                inlet_row,
            )

    all_values = velocity_x + velocity_y + dye
    nonfinite_count = preclamp_nonfinite_count + sum(
        not math.isfinite(value) for value in all_values
    )
    metrics: dict[str, object] = {
        "fluid.nonfiniteCount": nonfinite_count,
        "fluid.maxDivergence": maximum_divergence,
        "preProjectionMaxDivergence": maximum_preprojection_divergence,
        "projectionResidualRatioMax": projection_residual_ratio_max,
        "projectionReductionErrors": projection_reduction_errors,
        "fluid.dyeBoundsErrors": dye_bounds_errors,
        "dyeClampCount": dye_clamp_count,
        "maxDyeExcursion": maximum_dye_excursion,
        "preClampNonfiniteCount": preclamp_nonfinite_count,
        "dyeBoundTolerance": DYE_BOUND_TOLERANCE,
        "dyeMass": sum(dye),
        "kineticEnergy": 0.5 * sum(x * x + y * y for x, y in zip(velocity_x, velocity_y, strict=True)),
        "steps": steps,
    }
    geometry: dict[str, object] = {
        "coordinateSpace": "grid",
        "columns": columns,
        "rows": rows,
        "timeStep": delta_time,
        "sourceProgram": {
            "phase": phase,
            "orbitX": orbit_x,
            "orbitY": orbit_y,
            "swirlStrength": swirl_strength,
            "jetStrength": jet_strength,
            "inletOffset": inlet_offset,
        },
    }
    return geometry, frames, len(frames) - 1, metrics


_SOLVERS = (
    _alpha_persistence,
    _lower_star_join_tree,
    _sinkhorn_transport,
    _fast_marching,
    _physarum,
    _stable_fluid,
)


def compute_multistrata(
    variant: int,
    seed: int,
    width: int,
    height: int,
    parameters: dict[str, object],
) -> dict[str, object]:
    """Compute one deterministic semantic animation state.

    Variants 0 through 5 select alpha persistence, lower-star join trees,
    Sinkhorn transport, Fast Marching, Physarum, and stable fluids respectively.
    The returned digest covers solver state but no renderer duration or styling.
    """

    if isinstance(variant, bool) or not isinstance(variant, int) or not 0 <= variant < len(_SOLVERS):
        raise ValueError("variant must be an integer in [0, 5]")
    if isinstance(seed, bool) or not isinstance(seed, int):
        raise TypeError("seed must be an integer")
    for name, value in (("width", width), ("height", height)):
        if isinstance(value, bool) or not isinstance(value, int):
            raise TypeError(f"{name} must be an integer")
        if not 64 <= value <= 8192:
            raise ValueError(f"{name} must be in [64, 8192]")
    normalized_parameters = _validated_parameters(variant, parameters)
    geometry, frames, static_index, metrics = _SOLVERS[variant](seed, normalized_parameters)
    payload: dict[str, object] = {
        "schemaVersion": 1,
        "variant": variant,
        "algorithm": ALGORITHMS[variant],
        "seed": seed,
        "width": width,
        "height": height,
        "parameters": normalized_parameters,
        "geometry": geometry,
        "frames": frames,
        "staticFrame": frames[static_index],
        "metrics": metrics,
    }
    canonical = _clean(payload)
    solver_state = {
        key: value for key, value in canonical.items() if key not in {"width", "height"}
    }
    state_digest = _digest(solver_state)
    canonical["stateHash"] = state_digest
    canonical["stateDigest"] = state_digest
    return canonical


def _nonfinite_paths(value: object, path: str = "root") -> list[str]:
    failures: list[str] = []
    if isinstance(value, float) and not math.isfinite(value):
        failures.append(path)
    elif isinstance(value, dict):
        for key, item in value.items():
            failures.extend(_nonfinite_paths(item, f"{path}.{key}"))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            failures.extend(_nonfinite_paths(item, f"{path}[{index}]"))
    return failures


def run_self_test() -> dict[str, object]:
    """Exercise all default solvers and report deterministic invariant checks."""

    results: list[dict[str, object]] = []
    failures: list[str] = []
    for variant, algorithm in enumerate(ALGORITHMS):
        started = time.perf_counter()
        first = compute_multistrata(variant, 104729, 960, 600, {})
        second = compute_multistrata(variant, 104729, 960, 600, {})
        boundary_checks: list[dict[str, object]] = []
        metrics = first["metrics"]
        assert isinstance(metrics, dict)
        if first["stateDigest"] != second["stateDigest"]:
            failures.append(f"variant {variant}: repeated state digest mismatch")
        if len(str(first["stateDigest"])) != 64:
            failures.append(f"variant {variant}: state digest is not 64 hexadecimal characters")
        for path in _nonfinite_paths(first):
            failures.append(f"variant {variant}: nonfinite value at {path}")
        if variant == 0:
            alternate_viewport = compute_multistrata(0, 104729, 1280, 720, {})
            if first["stateDigest"] != alternate_viewport["stateDigest"]:
                failures.append("variant 0: solver-state digest depends on unused viewport dimensions")
            for key in (
                "alpha.faceClosureErrors",
                "alpha.eulerResidualMax",
                "alpha.componentBettiErrors",
                "alpha.negativeLifetimes",
                "alpha.nonmanifoldEdgeCount",
            ):
                if float(metrics[key]) != 0.0:
                    failures.append(f"variant 0: {key} must be zero")
            if int(metrics["finalDiskEuler"]) != 1:
                failures.append("variant 0: the final planar triangulation must have Euler characteristic one")
            if (
                int(metrics["alpha.distinctFrameStates"]) != len(first["frames"])  # type: ignore[arg-type]
                or int(metrics["alpha.stagnantTransitions"]) != 0
                or int(metrics["alpha.minimumSimplexDelta"]) <= 0
            ):
                failures.append("variant 0: event-rank filtration frames are not consequential")
            alpha_frames = first["frames"]
            assert isinstance(alpha_frames, list) and alpha_frames
            if any(
                float(alpha_frames[index]["alpha"]) <= float(alpha_frames[index - 1]["alpha"])
                for index in range(1, len(alpha_frames))
            ):
                failures.append("variant 0: filtration thresholds are not strictly progressive")
            maximum_beta_one = max(int(frame["betti"][1]) for frame in alpha_frames)
            static_frame = first["staticFrame"]
            assert isinstance(static_frame, dict)
            if int(static_frame["betti"][1]) != maximum_beta_one:  # type: ignore[index]
                failures.append("variant 0: static frame does not maximize beta-one activity")
            alpha_boundary_cases: tuple[tuple[str, int, dict[str, object]], ...] = (
                ("minimum-points-seed-23", 23, {"point_count": 8, "frame_count": 7}),
                ("minimum-points-seed-24", 24, {"point_count": 8, "frame_count": 7}),
                ("dense-seed-81", 81, {"point_count": 30, "frame_count": 9}),
            )
            for case_name, case_seed, case_parameters in alpha_boundary_cases:
                boundary = compute_multistrata(0, case_seed, 960, 600, case_parameters)
                boundary_metrics = boundary["metrics"]
                assert isinstance(boundary_metrics, dict)
                boundary_checks.append(
                    {
                        "case": case_name,
                        "stateDigest": boundary["stateDigest"],
                        "metrics": {
                            key: boundary_metrics[key]
                            for key in (
                                "alpha.distinctFrameStates",
                                "alpha.stagnantTransitions",
                                "alpha.minimumSimplexDelta",
                                "alpha.staticFrameBeta1",
                            )
                        },
                    }
                )
                if (
                    int(boundary_metrics["alpha.distinctFrameStates"])
                    != int(case_parameters["frame_count"])
                    or int(boundary_metrics["alpha.stagnantTransitions"]) != 0
                    or int(boundary_metrics["alpha.minimumSimplexDelta"]) <= 0
                ):
                    failures.append(f"variant 0 {case_name}: filtration staging regressed")
        elif variant == 1:
            for key in (
                "joinTree.treeStructureErrors",
                "joinTree.eventOrderErrors",
                "joinTree.componentAccountingErrors",
            ):
                if float(metrics[key]) != 0.0:
                    failures.append(f"variant 1: {key} must be zero")
            if int(metrics["finalComponentCount"]) != 1 or int(metrics["mergeEventCount"]) < 1:
                failures.append("variant 1: expected one final component and at least one merge event")
            if (
                int(metrics["joinTree.distinctFrameStates"]) != len(first["frames"])  # type: ignore[arg-type]
                or int(metrics["joinTree.stagnantTransitions"]) != 0
            ):
                failures.append("variant 1: critical-value frames are not distinct")
            join_geometry = first["geometry"]
            assert isinstance(join_geometry, dict)
            samples = join_geometry["samples"]
            triangles_raw = join_geometry["triangles"]
            join_tree = join_geometry["joinTree"]
            assert isinstance(samples, list) and isinstance(triangles_raw, list)
            assert isinstance(join_tree, dict)
            join_values = [float(sample["value"]) for sample in samples]
            join_triangles = [tuple(int(vertex) for vertex in triangle) for triangle in triangles_raw]
            join_nodes = [dict(node) for node in join_tree["nodes"]]  # type: ignore[index]
            join_arcs = [dict(arc) for arc in join_tree["arcs"]]  # type: ignore[index]
            join_events = [dict(event) for event in join_tree["mergeEvents"]]  # type: ignore[index]
            if _audit_join_component_accounting(join_values, join_triangles, join_events) != 0:
                failures.append("variant 1: independent connectivity replay rejected the join tree")
            corrupted_events = [dict(event) for event in join_events]
            if corrupted_events:
                corrupted_events[0]["componentsAfter"] = int(
                    corrupted_events[0]["componentsAfter"]
                ) + 1
                if _audit_join_component_accounting(
                    join_values, join_triangles, corrupted_events
                ) == 0:
                    failures.append("variant 1: accounting mutation was not detected")
            if join_arcs and join_nodes:
                orphan_arcs = [dict(arc) for arc in join_arcs[1:]]
                multiple_parent_arcs = [dict(arc) for arc in join_arcs]
                duplicate_arc = dict(join_arcs[0])
                duplicate_arc["id"] = "mutation-multiple-parent"
                multiple_parent_arcs.append(duplicate_arc)
                root_id = next(
                    str(node["id"])
                    for node in join_nodes
                    if node.get("type") == "root-maximum"
                )
                nonroot_id = next(
                    str(node["id"])
                    for node in join_nodes
                    if node.get("type") != "root-maximum"
                )
                cycle_arcs = [dict(arc) for arc in join_arcs]
                cycle_arcs.append(
                    {"id": "mutation-cycle", "from": root_id, "to": nonroot_id}
                )
                for mutation_name, mutated_arcs in (
                    ("orphan", orphan_arcs),
                    ("multiple-parent", multiple_parent_arcs),
                    ("cycle", cycle_arcs),
                ):
                    if _audit_join_tree_structure(join_nodes, mutated_arcs)[
                        "treeStructureErrors"
                    ] == 0:
                        failures.append(
                            f"variant 1: {mutation_name} structure mutation was not detected"
                        )
            adjacent = compute_multistrata(1, 104730, 960, 600, {})
            adjacent_geometry = adjacent["geometry"]
            assert isinstance(adjacent_geometry, dict)
            adjacent_samples = adjacent_geometry["samples"]
            assert isinstance(adjacent_samples, list)
            join_seed_delta = max(
                abs(float(left["value"]) - float(right["value"]))
                for left, right in zip(samples, adjacent_samples, strict=True)
            )
            boundary_checks.append(
                {
                    "case": "adjacent-seed-semantic-delta",
                    "stateDigest": adjacent["stateDigest"],
                    "metrics": {"maxScalarDelta": join_seed_delta},
                }
            )
            if join_seed_delta < 0.02:
                failures.append("variant 1: adjacent seeds do not materially change the scalar field")
            for boundary_seed in (-98, -23, 0, 23, 81):
                staged = compute_multistrata(
                    1,
                    boundary_seed,
                    960,
                    600,
                    {"grid_columns": 18, "grid_rows": 12, "frame_count": 9},
                )
                staged_metrics = staged["metrics"]
                assert isinstance(staged_metrics, dict)
                if (
                    int(staged_metrics["joinTree.distinctFrameStates"]) != 9
                    or int(staged_metrics["joinTree.stagnantTransitions"]) != 0
                ):
                    failures.append(
                        f"variant 1 seed {boundary_seed}: lower-star frame supplementation failed"
                    )
            boundary_checks.append(
                {
                    "case": "lower-star-level-supplement-seeds",
                    "stateDigest": staged["stateDigest"],
                    "metrics": {"seedCount": 5, "frameCount": 9},
                }
            )
        elif variant == 2:
            if max(
                float(metrics["transport.maxRowError"]),
                float(metrics["transport.maxColumnError"]),
                float(metrics["transport.massError"]),
            ) > 2e-5:
                failures.append("variant 2: Sinkhorn marginal residual exceeds 2e-5")
            if int(metrics["negativeEntryCount"]) != 0:
                failures.append("variant 2: transport plan contains a negative entry")
            transport_geometry = first["geometry"]
            assert isinstance(transport_geometry, dict)
            cost_matrix = transport_geometry.get("costMatrix")
            gibbs_kernel = transport_geometry.get("gibbsKernel")
            site_count = int(first["parameters"]["site_count"])  # type: ignore[index]
            epsilon = float(first["parameters"]["epsilon"])  # type: ignore[index]
            if (
                not isinstance(cost_matrix, list)
                or not isinstance(gibbs_kernel, list)
                or len(cost_matrix) != site_count
                or len(gibbs_kernel) != site_count
            ):
                failures.append("variant 2: Gibbs kernel shape does not match the transport sites")
            else:
                kernel_errors = 0
                for cost_row, kernel_row in zip(cost_matrix, gibbs_kernel, strict=True):
                    if (
                        not isinstance(cost_row, list)
                        or not isinstance(kernel_row, list)
                        or len(cost_row) != site_count
                        or len(kernel_row) != site_count
                    ):
                        kernel_errors += 1
                        continue
                    for cost_value, kernel_value in zip(cost_row, kernel_row, strict=True):
                        expected = math.exp(-float(cost_value) / epsilon)
                        if float(kernel_value) < 0.0 or abs(float(kernel_value) - expected) > 1e-7:
                            kernel_errors += 1
                if kernel_errors:
                    failures.append(
                        f"variant 2: Gibbs kernel has {kernel_errors} value or shape errors"
                    )

            def audit_sinkhorn_scaling_evidence(
                payload: dict[str, object], case_name: str
            ) -> None:
                payload_geometry = payload["geometry"]
                payload_metrics = payload["metrics"]
                payload_frames = payload["frames"]
                assert isinstance(payload_geometry, dict)
                assert isinstance(payload_metrics, dict)
                assert isinstance(payload_frames, list)
                evidence = payload_geometry.get("sinkhornScalingEvidence")
                final_plan = payload_geometry.get("plan")
                history = payload_geometry.get("residualHistory")
                if (
                    not isinstance(evidence, dict)
                    or not isinstance(final_plan, list)
                    or not isinstance(history, list)
                ):
                    failures.append(
                        f"variant 2 {case_name}: scaling evidence schema is missing"
                    )
                    return
                count = int(payload["parameters"]["site_count"])  # type: ignore[index]
                evidence_kernel = evidence.get("kernel")
                final_u = evidence.get("u")
                final_v = evidence.get("v")
                source_weights = evidence.get("sourceMass")
                target_weights = evidence.get("targetMass")
                scaling_checkpoints = evidence.get("checkpoints")
                vectors = (final_u, final_v, source_weights, target_weights)
                if (
                    not isinstance(evidence_kernel, list)
                    or not isinstance(scaling_checkpoints, list)
                    or any(not isinstance(vector, list) for vector in vectors)
                    or any(len(vector) != count for vector in vectors)  # type: ignore[arg-type]
                    or len(evidence_kernel) != count
                    or len(final_plan) != count
                ):
                    failures.append(
                        f"variant 2 {case_name}: scaling evidence dimensions are invalid"
                    )
                    return
                assert isinstance(final_u, list) and isinstance(final_v, list)
                assert isinstance(source_weights, list) and isinstance(target_weights, list)
                reconstruction_errors = 0
                reconstructed_final: list[list[float]] = []
                for row in range(count):
                    kernel_row = evidence_kernel[row]
                    plan_row = final_plan[row]
                    if (
                        not isinstance(kernel_row, list)
                        or not isinstance(plan_row, list)
                        or len(kernel_row) != count
                        or len(plan_row) != count
                    ):
                        reconstruction_errors += 1
                        continue
                    reconstructed_row: list[float] = []
                    for column in range(count):
                        values = (
                            float(final_u[row]),
                            float(kernel_row[column]),
                            float(final_v[column]),
                            float(plan_row[column]),
                        )
                        if (
                            not all(math.isfinite(value) for value in values)
                            or values[0] <= 0.0
                            or values[1] <= 0.0
                            or values[2] <= 0.0
                            or values[3] < 0.0
                        ):
                            reconstruction_errors += 1
                        reconstructed_row.append(values[0] * values[1] * values[2])
                    reconstructed_final.append(reconstructed_row)
                if len(reconstructed_final) == count:
                    maximum_reconstruction_error = max(
                        abs(reconstructed_final[row][column] - float(final_plan[row][column]))
                        for row in range(count)
                        for column in range(count)
                    )
                    if maximum_reconstruction_error > 1e-7:
                        reconstruction_errors += 1
                if reconstruction_errors:
                    failures.append(
                        f"variant 2 {case_name}: final P=diag(u)Kdiag(v) evidence has "
                        f"{reconstruction_errors} errors"
                    )
                expected_checkpoint_count = int(
                    payload_metrics["scalingCheckpointCount"]
                )
                checkpoint_iterations: list[int] = []
                checkpoint_errors = 0
                for checkpoint in scaling_checkpoints:
                    if not isinstance(checkpoint, dict):
                        checkpoint_errors += 1
                        continue
                    checkpoint_u = checkpoint.get("u")
                    checkpoint_v = checkpoint.get("v")
                    if (
                        not isinstance(checkpoint_u, list)
                        or not isinstance(checkpoint_v, list)
                        or len(checkpoint_u) != count
                        or len(checkpoint_v) != count
                    ):
                        checkpoint_errors += 1
                        continue
                    iteration = int(checkpoint.get("iteration", -1))
                    checkpoint_iterations.append(iteration)
                    if not all(
                        math.isfinite(float(value)) and float(value) > 0.0
                        for value in checkpoint_u + checkpoint_v
                    ):
                        checkpoint_errors += 1
                        continue
                    checkpoint_plan = [
                        [
                            float(checkpoint_u[row])
                            * float(evidence_kernel[row][column])
                            * float(checkpoint_v[column])
                            for column in range(count)
                        ]
                        for row in range(count)
                    ]
                    observed_row_error = max(
                        abs(sum(checkpoint_plan[row]) - float(source_weights[row]))
                        for row in range(count)
                    )
                    observed_column_error = max(
                        abs(
                            sum(checkpoint_plan[row][column] for row in range(count))
                            - float(target_weights[column])
                        )
                        for column in range(count)
                    )
                    observed_mass_error = abs(
                        sum(sum(row) for row in checkpoint_plan) - 1.0
                    )
                    if (
                        abs(observed_row_error - float(checkpoint["maxRowError"])) > 1e-10
                        or abs(
                            observed_column_error
                            - float(checkpoint["maxColumnError"])
                        )
                        > 1e-10
                        or abs(observed_mass_error - float(checkpoint["massError"]))
                        > 1e-10
                    ):
                        checkpoint_errors += 1
                if (
                    len(scaling_checkpoints) != expected_checkpoint_count
                    or not checkpoint_iterations
                    or checkpoint_iterations[0] != 0
                    or checkpoint_iterations[-1] != int(payload_metrics["iterations"])
                    or any(
                        right <= left
                        for left, right in zip(
                            checkpoint_iterations, checkpoint_iterations[1:]
                        )
                    )
                ):
                    checkpoint_errors += 1
                history_iterations: list[int] = []
                for record in history:
                    if not isinstance(record, dict):
                        checkpoint_errors += 1
                        continue
                    history_iterations.append(int(record.get("iteration", -1)))
                    for key in ("maxRowError", "maxColumnError", "massError"):
                        value = float(record.get(key, math.nan))
                        if not math.isfinite(value) or value < 0.0:
                            checkpoint_errors += 1
                if (
                    history_iterations != sorted(set(history_iterations))
                    or not set(checkpoint_iterations) <= set(history_iterations)
                    or len(history) != int(payload_metrics["residualSampleCount"])
                ):
                    checkpoint_errors += 1
                reference_link_signature: list[tuple[int, int, float]] | None = None
                for frame in payload_frames:
                    assert isinstance(frame, dict)
                    checkpoint_index = int(frame.get("sinkhornCheckpointIndex", -1))
                    if not 0 <= checkpoint_index < len(scaling_checkpoints):
                        checkpoint_errors += 1
                        continue
                    checkpoint = scaling_checkpoints[checkpoint_index]
                    assert isinstance(checkpoint, dict)
                    if int(frame.get("sinkhornIteration", -1)) != int(
                        checkpoint["iteration"]
                    ):
                        checkpoint_errors += 1
                    links = frame.get("links")
                    if not isinstance(links, list) or len(links) != count * count:
                        checkpoint_errors += 1
                        continue
                    link_signature: list[tuple[int, int, float]] = []
                    observed_pairs: set[tuple[int, int]] = set()
                    for link in links:
                        if not isinstance(link, dict):
                            checkpoint_errors += 1
                            continue
                        source_id = int(link.get("source", -1))
                        target_id = int(link.get("target", -1))
                        link_mass = float(link.get("mass", math.nan))
                        if (
                            not 0 <= source_id < count
                            or not 0 <= target_id < count
                            or not math.isfinite(link_mass)
                            or abs(
                                link_mass
                                - float(final_plan[source_id][target_id])
                            )
                            > 1e-12
                        ):
                            checkpoint_errors += 1
                        observed_pairs.add((source_id, target_id))
                        link_signature.append((source_id, target_id, link_mass))
                    if len(observed_pairs) != count * count:
                        checkpoint_errors += 1
                    if reference_link_signature is None:
                        reference_link_signature = link_signature
                    elif link_signature != reference_link_signature:
                        checkpoint_errors += 1
                if checkpoint_errors:
                    failures.append(
                        f"variant 2 {case_name}: checkpoint/residual history has "
                        f"{checkpoint_errors} errors"
                    )

            audit_sinkhorn_scaling_evidence(first, "default")
            sinkhorn_corner = compute_multistrata(
                2,
                81,
                960,
                600,
                {
                    "site_count": 14,
                    "epsilon": 0.03,
                    "minimum_iterations": 40,
                    "frame_count": 5,
                },
            )
            sinkhorn_corner_metrics = sinkhorn_corner["metrics"]
            assert isinstance(sinkhorn_corner_metrics, dict)
            boundary_checks.append(
                {
                    "case": "low-epsilon-seed-81",
                    "stateDigest": sinkhorn_corner["stateDigest"],
                    "metrics": {
                        key: sinkhorn_corner_metrics[key]
                        for key in (
                            "transport.maxRowError",
                            "transport.maxColumnError",
                            "transport.massError",
                            "iterations",
                        )
                    },
                }
            )
            if max(
                float(sinkhorn_corner_metrics["transport.maxRowError"]),
                float(sinkhorn_corner_metrics["transport.maxColumnError"]),
                float(sinkhorn_corner_metrics["transport.massError"]),
            ) > 1e-4:
                failures.append("variant 2 seed 81: refined marginal residual exceeds 1e-4")
            if not 40 < int(sinkhorn_corner_metrics["iterations"]) <= 320:
                failures.append("variant 2 seed 81: bounded continuation was not exercised correctly")
            audit_sinkhorn_scaling_evidence(sinkhorn_corner, "seed 81")
            for path in _nonfinite_paths(sinkhorn_corner):
                failures.append(f"variant 2 seed 81: nonfinite value at {path}")
        elif variant == 3:
            if (
                int(metrics["front.acceptedOrderErrors"]) != 0
                or int(metrics["front.unreachableTargets"]) != 0
                or int(metrics["front.trialStateErrors"]) != 0
            ):
                failures.append("variant 3: Fast Marching acceptance/trial invariant failed")
            if float(metrics["front.analyticMaxError"]) > 0.12:
                failures.append("variant 3: constant-speed analytic error exceeds 0.12")
            adjacent = compute_multistrata(3, 104730, 960, 600, {})
            front_geometry = first["geometry"]
            adjacent_geometry = adjacent["geometry"]
            assert isinstance(front_geometry, dict) and isinstance(adjacent_geometry, dict)
            front_frames = first["frames"]
            assert isinstance(front_frames, list) and front_frames
            arrival_times = front_geometry.get("arrivalTimes")
            source_record = front_geometry.get("source")
            front_columns = int(front_geometry["columns"])
            front_rows = int(front_geometry["rows"])
            trial_audit_errors = 0
            if not isinstance(arrival_times, list) or not isinstance(source_record, dict):
                trial_audit_errors += 1
            else:
                for frame in front_frames:
                    assert isinstance(frame, dict)
                    accepted_ids = frame.get("acceptedCellIds")
                    trial_ids = frame.get("trialCellIds")
                    tentative_times = frame.get("trialArrivalTimes")
                    if (
                        not isinstance(accepted_ids, list)
                        or not isinstance(trial_ids, list)
                        or not isinstance(tentative_times, list)
                        or len(trial_ids) != len(tentative_times)
                    ):
                        trial_audit_errors += 1
                        continue
                    accepted_set = {int(cell) for cell in accepted_ids}
                    trial_set = {int(cell) for cell in trial_ids}
                    threshold = float(frame["time"])
                    if (
                        accepted_ids != sorted(accepted_ids)
                        or trial_ids != sorted(trial_ids)
                        or len(accepted_set) != len(accepted_ids)
                        or len(trial_set) != len(trial_ids)
                        or accepted_set & trial_set
                        or int(frame["trialHeapEntryCount"])
                        != len(trial_ids) + int(frame["trialStaleHeapEntryCount"])
                    ):
                        trial_audit_errors += 1
                    expected_accepted = {
                        cell
                        for cell, arrival in enumerate(arrival_times)
                        if float(arrival) <= threshold + 5e-8
                    }
                    if accepted_set != expected_accepted:
                        trial_audit_errors += 1
                    for trial_cell, tentative_time in zip(
                        trial_ids, tentative_times, strict=True
                    ):
                        cell = int(trial_cell)
                        tentative = float(tentative_time)
                        if (
                            not 0 <= cell < len(arrival_times)
                            or not math.isfinite(tentative)
                            or tentative + 5e-8 < threshold
                            or tentative + 5e-8 < float(arrival_times[cell])
                        ):
                            trial_audit_errors += 1
                            continue
                        column = cell % front_columns
                        row = cell // front_columns
                        neighbors = []
                        if column > 0:
                            neighbors.append(cell - 1)
                        if column + 1 < front_columns:
                            neighbors.append(cell + 1)
                        if row > 0:
                            neighbors.append(cell - front_columns)
                        if row + 1 < front_rows:
                            neighbors.append(cell + front_columns)
                        if not any(neighbor in accepted_set for neighbor in neighbors):
                            trial_audit_errors += 1
                    if len(accepted_set) < len(arrival_times) and not trial_set:
                        trial_audit_errors += 1
                initial_accepted = front_frames[0]["acceptedCellIds"]
                final_accepted = front_frames[-1]["acceptedCellIds"]
                if (
                    initial_accepted != [int(source_record["id"])]
                    or len(final_accepted) != len(arrival_times)
                    or front_frames[-1]["trialCellIds"]
                ):
                    trial_audit_errors += 1
            if trial_audit_errors:
                failures.append(
                    f"variant 3: serialized heap trial states have "
                    f"{trial_audit_errors} audit errors"
                )
            speed_delta = max(
                abs(float(left) - float(right))
                for left, right in zip(
                    front_geometry["speedField"],  # type: ignore[arg-type]
                    adjacent_geometry["speedField"],  # type: ignore[arg-type]
                    strict=True,
                )
            )
            boundary_checks.append(
                {
                    "case": "adjacent-seed-semantic-delta",
                    "stateDigest": adjacent["stateDigest"],
                    "metrics": {"maxSpeedFieldDelta": speed_delta},
                }
            )
            if speed_delta < 0.02:
                failures.append("variant 3: adjacent seeds do not materially change the speed field")
        elif variant == 4:
            if (
                int(metrics["physarum.nonfiniteCount"]) != 0
                or int(metrics["physarum.outOfBounds"]) != 0
            ):
                failures.append("variant 4: Physarum finite-domain invariant failed")
            if not 0.0 <= float(metrics["physarum.nutrientCoverage"]) <= 1.0:
                failures.append("variant 4: nutrient coverage is outside [0, 1]")
            if float(metrics["physarum.networkConnectedSiteReach"]) < 0.8:
                failures.append("variant 4: default network reaches fewer than four of five sites")
            if int(metrics["physarum.networkBackboneErrors"]) != 0:
                failures.append("variant 4: default rooted backbone is structurally invalid")
            generator_style = first
            generator_metrics = generator_style["metrics"]
            assert isinstance(generator_metrics, dict)
            boundary_checks.append(
                {
                    "case": "generator-float-sensor-offset",
                    "stateDigest": generator_style["stateDigest"],
                    "metrics": {
                        key: generator_metrics[key]
                        for key in (
                            "physarum.nonfiniteCount",
                            "physarum.outOfBounds",
                            "physarum.nutrientCoverage",
                            "physarum.networkConnectedSiteReach",
                            "physarum.networkBackboneErrors",
                        )
                    },
                }
            )
            if float(generator_style["parameters"]["sensor_offset"]) != 4.0:  # type: ignore[index]
                failures.append("variant 4: generator-style float sensor_offset was not preserved")
            for path in _nonfinite_paths(generator_style):
                failures.append(f"variant 4 generator float: nonfinite value at {path}")
            physarum_corner_parameters: dict[str, object] = {
                "agent_count": 60,
                "steps": 80,
                "frame_count": 5,
                "sensor_offset": 2.0,
            }
            for corner_seed in (23, -23):
                physarum_corner = compute_multistrata(
                    4, corner_seed, 960, 600, physarum_corner_parameters
                )
                physarum_corner_metrics = physarum_corner["metrics"]
                assert isinstance(physarum_corner_metrics, dict)
                boundary_checks.append(
                    {
                        "case": f"low-budget-seed-{corner_seed}",
                        "stateDigest": physarum_corner["stateDigest"],
                        "metrics": {
                            key: physarum_corner_metrics[key]
                            for key in (
                                "physarum.nonfiniteCount",
                                "physarum.outOfBounds",
                                "physarum.nutrientCoverage",
                                "physarum.nutrientSiteReach",
                                "physarum.networkConnectedSiteReach",
                                "physarum.networkBackboneErrors",
                            )
                        },
                    }
                )
                if (
                    int(physarum_corner_metrics["physarum.nonfiniteCount"]) != 0
                    or int(physarum_corner_metrics["physarum.outOfBounds"]) != 0
                ):
                    failures.append(
                        f"variant 4 seed {corner_seed}: low-budget finite-domain invariant failed"
                    )
                if float(
                    physarum_corner_metrics["physarum.networkConnectedSiteReach"]
                ) < 0.8:
                    failures.append(
                        f"variant 4 seed {corner_seed}: network connects fewer than four sites"
                    )
                if int(physarum_corner_metrics["physarum.networkBackboneErrors"]) != 0:
                    failures.append(
                        f"variant 4 seed {corner_seed}: rooted backbone is structurally invalid"
                    )
                corner_geometry = physarum_corner["geometry"]
                corner_frames = physarum_corner["frames"]
                assert isinstance(corner_geometry, dict)
                assert isinstance(corner_frames, list) and corner_frames
                target_cell_ids = corner_geometry.get("nutrientTargetCellIds")
                initial_frame = corner_frames[0]
                final_frame = corner_frames[-1]
                assert isinstance(initial_frame, dict) and isinstance(final_frame, dict)
                initial_deposits = initial_frame.get("depositedTargetCellIds")
                final_deposits = final_frame.get("depositedTargetCellIds")
                initial_trail = initial_frame.get("trailField")
                initial_deposited_trail = initial_frame.get("depositedTrailField")
                initial_network = initial_frame.get("networkField")
                initial_agents = initial_frame.get("agents")
                initial_paths = initial_frame.get("networkPaths")
                initial_edges = initial_frame.get("networkEdges")
                if (
                    not isinstance(target_cell_ids, list)
                    or not isinstance(initial_deposits, list)
                    or not isinstance(final_deposits, list)
                    or not isinstance(initial_trail, list)
                    or not isinstance(initial_deposited_trail, list)
                    or not isinstance(initial_network, list)
                    or not isinstance(initial_agents, list)
                    or not isinstance(initial_paths, list)
                    or not isinstance(initial_edges, list)
                ):
                    failures.append(
                        f"variant 4 seed {corner_seed}: deposition evidence schema is incomplete"
                    )
                else:
                    if (
                        initial_deposits
                        or any(float(value) != 0.0 for value in initial_trail)
                        or any(float(value) != 0.0 for value in initial_deposited_trail)
                        or any(float(value) != 0.0 for value in initial_network)
                        or initial_paths
                        or initial_edges
                        or initial_frame.get("reachedNutrientSiteIds")
                        or initial_frame.get("connectedNutrientSiteIds")
                        or initial_frame.get("networkRootCellId") is not None
                        or float(initial_frame.get("networkThreshold", -1.0)) != 0.0
                    ):
                        failures.append(
                            f"variant 4 seed {corner_seed}: initialization was pre-counted as coverage"
                        )
                    if any(
                        math.hypot(
                            float(agent["x"]) - 23.5,
                            float(agent["y"]) - 14.5,
                        )
                        > 2.0
                        for agent in initial_agents
                    ):
                        failures.append(
                            f"variant 4 seed {corner_seed}: agents were not centrally inoculated"
                        )
                    target_set = {int(cell) for cell in target_cell_ids}
                    final_set = {int(cell) for cell in final_deposits}
                    if not final_set <= target_set or len(final_set) != len(final_deposits):
                        failures.append(
                            f"variant 4 seed {corner_seed}: final deposition evidence is invalid"
                        )
                    evidence_coverage = len(final_set) / max(1, len(target_set))
                    if abs(
                        evidence_coverage
                        - float(physarum_corner_metrics["physarum.nutrientCoverage"])
                    ) > 1e-8:
                        failures.append(
                            f"variant 4 seed {corner_seed}: coverage does not match deposition evidence"
                        )
                    nutrient_sites_raw = corner_geometry.get("nutrientSites")
                    if not isinstance(nutrient_sites_raw, list):
                        failures.append(
                            f"variant 4 seed {corner_seed}: nutrient-site geometry is missing"
                        )
                    else:
                        normalized_sites = tuple(
                            (
                                float(site["x"]) / 47.0,
                                float(site["y"]) / 29.0,
                            )
                            for site in nutrient_sites_raw
                        )
                        final_network = final_frame.get("networkField")
                        if not isinstance(final_network, list):
                            failures.append(
                                f"variant 4 seed {corner_seed}: final network field is missing"
                            )
                        else:
                            (
                                threshold,
                                reached,
                                connected,
                                network_paths,
                                network_edges,
                                network_root,
                            ) = _network_site_evidence(
                                [float(value) for value in final_network],
                                48,
                                30,
                                normalized_sites,
                            )
                            if (
                                reached != final_frame.get("reachedNutrientSiteIds")
                                or connected != final_frame.get("connectedNutrientSiteIds")
                                or network_paths != final_frame.get("networkPaths")
                                or network_edges != final_frame.get("networkEdges")
                                or network_root != final_frame.get("networkRootCellId")
                                or abs(threshold - float(final_frame["networkThreshold"])) > 1e-8
                                or len(connected) / len(normalized_sites)
                                != float(
                                    physarum_corner_metrics[
                                        "physarum.networkConnectedSiteReach"
                                    ]
                                )
                            ):
                                failures.append(
                                    f"variant 4 seed {corner_seed}: network evidence audit disagrees"
                                )
                            observed_paths = final_frame.get("networkPaths")
                            observed_edges = final_frame.get("networkEdges")
                            if not isinstance(observed_paths, list) or not isinstance(
                                observed_edges, list
                            ):
                                failures.append(
                                    f"variant 4 seed {corner_seed}: sparse backbone schema is missing"
                                )
                            else:
                                path_edges: set[tuple[int, int]] = set()
                                path_site_ids: list[int] = []
                                backbone_errors = 0
                                for record in observed_paths:
                                    if not isinstance(record, dict):
                                        backbone_errors += 1
                                        continue
                                    site_id = int(record.get("nutrientSiteId", -1))
                                    cells = record.get("cellIds")
                                    if not isinstance(cells, list) or not cells:
                                        backbone_errors += 1
                                        continue
                                    cell_ids = [int(cell) for cell in cells]
                                    path_site_ids.append(site_id)
                                    first_cell = cell_ids[0]
                                    last_cell = cell_ids[-1]
                                    if (
                                        site_id not in connected
                                        or (first_cell % 48 - 23.5) ** 2
                                        + (first_cell // 48 - 14.5) ** 2
                                        > 16.0
                                        or not 0 <= last_cell < len(final_network)
                                    ):
                                        backbone_errors += 1
                                    else:
                                        site_x, site_y = normalized_sites[site_id]
                                        if (
                                            last_cell % 48 - site_x * 47.0
                                        ) ** 2 + (
                                            last_cell // 48 - site_y * 29.0
                                        ) ** 2 > 16.0:
                                            backbone_errors += 1
                                    if len(set(cell_ids)) != len(cell_ids):
                                        backbone_errors += 1
                                    for cell in cell_ids:
                                        if (
                                            not 0 <= cell < len(final_network)
                                            or float(final_network[cell]) + 1e-12 < threshold
                                        ):
                                            backbone_errors += 1
                                    for source, target in zip(cell_ids, cell_ids[1:]):
                                        if (
                                            abs(source % 48 - target % 48) > 1
                                            or abs(source // 48 - target // 48) > 1
                                        ):
                                            backbone_errors += 1
                                        path_edges.add((source, target))
                                try:
                                    observed_edge_set = {
                                        (int(edge[0]), int(edge[1])) for edge in observed_edges
                                    }
                                except (IndexError, TypeError, ValueError):
                                    observed_edge_set = set()
                                    backbone_errors += 1
                                if (
                                    path_site_ids != connected
                                    or observed_edge_set != path_edges
                                    or len(observed_edge_set) != len(observed_edges)
                                    or int(physarum_corner_metrics["networkPathCount"])
                                    != len(observed_paths)
                                    or int(
                                        physarum_corner_metrics["networkBackboneEdgeCount"]
                                    )
                                    != len(observed_edges)
                                ):
                                    backbone_errors += 1
                                if backbone_errors:
                                    failures.append(
                                        f"variant 4 seed {corner_seed}: sparse backbone failed "
                                        f"{backbone_errors} structural audits"
                                    )
                                if observed_edges:
                                    corrupted_edges = [list(edge) for edge in observed_edges]
                                    corrupted_edges[0] = [
                                        int(corrupted_edges[0][0]),
                                        int(corrupted_edges[0][1]) + 2,
                                    ]
                                    if (
                                        _audit_network_backbone(
                                            observed_paths,
                                            corrupted_edges,
                                            connected,
                                            48,
                                            network_root,
                                        )
                                        == 0
                                    ):
                                        failures.append(
                                            f"variant 4 seed {corner_seed}: backbone mutation escaped audit"
                                        )
                                if network_root is not None and (
                                    _audit_network_backbone(
                                        observed_paths,
                                        observed_edges,
                                        connected,
                                        48,
                                        network_root + 1,
                                    )
                                    == 0
                                ):
                                    failures.append(
                                        f"variant 4 seed {corner_seed}: root mutation escaped audit"
                                    )
                    connected_progression = [
                        len(frame["connectedNutrientSiteIds"]) for frame in corner_frames
                    ]
                    if connected_progression[0] != 0 or connected_progression[-1] < 4:
                        failures.append(
                            f"variant 4 seed {corner_seed}: site-connectivity progression is missing"
                        )
                    if not any(
                        any(
                            abs(float(before) - float(after)) > 1e-8
                            for before, after in zip(
                                frame["depositedTrailField"],
                                frame["trailField"],
                                strict=True,
                            )
                        )
                        for frame in corner_frames[1:]
                    ):
                        failures.append(
                            f"variant 4 seed {corner_seed}: deposited and diffused trail strata are identical"
                        )
                for path in _nonfinite_paths(physarum_corner):
                    failures.append(
                        f"variant 4 seed {corner_seed}: nonfinite value at {path}"
                    )
        else:
            if (
                int(metrics["fluid.nonfiniteCount"]) != 0
                or int(metrics["fluid.dyeBoundsErrors"]) != 0
            ):
                failures.append("variant 5: fluid finite/dye-bound invariant failed")
            if float(metrics["fluid.maxDivergence"]) > 0.08:
                failures.append("variant 5: projected velocity divergence exceeds 0.08")
            if (
                int(metrics["projectionReductionErrors"]) != 0
                or float(metrics["preProjectionMaxDivergence"])
                <= float(metrics["fluid.maxDivergence"])
                or not 0.0 <= float(metrics["projectionResidualRatioMax"]) <= 0.35
            ):
                failures.append(
                    "variant 5: pressure projection did not reduce divergence below the 0.35 ratio gate"
                )
            fluid_frames = first["frames"]
            assert isinstance(fluid_frames, list) and fluid_frames
            fluid_geometry = first["geometry"]
            assert isinstance(fluid_geometry, dict)
            source_program = fluid_geometry.get("sourceProgram")
            if not isinstance(source_program, dict):
                failures.append("variant 5: seeded source program is missing")
            else:
                phase = float(source_program["phase"])
                orbit_x = float(source_program["orbitX"])
                orbit_y = float(source_program["orbitY"])
                inlet_offset = int(source_program["inletOffset"])
                fluid_steps = int(first["parameters"]["steps"])  # type: ignore[index]
                fluid_rows = int(fluid_geometry["rows"])
                for frame in fluid_frames:
                    step = int(frame["step"])
                    clock = 2.0 * math.pi * step / fluid_steps + phase
                    force_center = frame.get("forceCenter")
                    if (
                        not isinstance(force_center, dict)
                        or abs(float(force_center["x"]) - (0.48 + orbit_x * math.cos(clock)))
                        > 5e-8
                        or abs(float(force_center["y"]) - (0.50 + orbit_y * math.sin(clock)))
                        > 5e-8
                        or int(frame.get("inletRow", -1))
                        != (inlet_offset + step * 3 // 7) % fluid_rows
                        or int(frame.get("inletColumn", -1)) != 1
                    ):
                        failures.append(
                            f"variant 5: frame {frame.get('index')} source evidence disagrees "
                            "with the seeded source program"
                        )
            if not any(
                max(abs(float(value)) for value in frame["advectedDivergenceField"])
                > max(abs(float(value)) for value in frame["divergenceField"]) + 1e-10
                for frame in fluid_frames[1:]
            ):
                failures.append("variant 5: captured pre/post projection strata are not distinct")
            if (
                int(metrics["dyeClampCount"]) != 0
                or int(metrics["preClampNonfiniteCount"]) != 0
                or float(metrics["maxDyeExcursion"]) > DYE_BOUND_TOLERANCE
            ):
                failures.append("variant 5: default dye required a pre-clamp correction")
            high_probe = _audit_dye_value(1.25)
            roundoff_probe = _audit_dye_value(1.0 + 0.5 * DYE_BOUND_TOLERANCE)
            nonfinite_probe = _audit_dye_value(math.nan)
            if high_probe != (1.0, 1, 1, 0.25, 0):
                failures.append("variant 5: pre-clamp high-bound probe was not detected")
            if not (
                roundoff_probe[0] == 1.0
                and roundoff_probe[1] == 0
                and roundoff_probe[2] == 1
                and 0.0 < roundoff_probe[3] <= DYE_BOUND_TOLERANCE
                and roundoff_probe[4] == 0
            ):
                failures.append("variant 5: dye roundoff-tolerance probe failed")
            if nonfinite_probe != (0.0, 0, 1, 0.0, 1):
                failures.append("variant 5: pre-clamp nonfinite probe was not detected")
            adjacent_probe_parameters: dict[str, object] = {
                "grid_columns": 14,
                "grid_rows": 8,
                "steps": 24,
                "frame_count": 3,
            }
            baseline_probe = compute_multistrata(
                5, 104729, 960, 600, adjacent_probe_parameters
            )
            adjacent = compute_multistrata(
                5, 104730, 960, 600, adjacent_probe_parameters
            )
            baseline_probe_frames = baseline_probe["frames"]
            adjacent_frames = adjacent["frames"]
            assert isinstance(baseline_probe_frames, list) and baseline_probe_frames
            assert isinstance(adjacent_frames, list) and adjacent_frames
            dye_seed_delta = max(
                abs(float(left) - float(right))
                for left, right in zip(
                    baseline_probe_frames[-1]["dyeField"],
                    adjacent_frames[-1]["dyeField"],
                    strict=True,
                )
            )
            boundary_checks.append(
                {
                    "case": "adjacent-seed-semantic-delta",
                    "stateDigest": adjacent["stateDigest"],
                    "metrics": {"maxDyeFieldDelta": dye_seed_delta},
                }
            )
            if dye_seed_delta < 0.01:
                failures.append("variant 5: adjacent seeds do not materially change the dye field")
            fluid_boundary_cases: tuple[tuple[str, dict[str, object]], ...] = (
                (
                    "grid-columns-26",
                    {"grid_columns": 26, "steps": 24, "frame_count": 3},
                ),
                (
                    "zero-viscosity",
                    {"viscosity": 0.0, "steps": 24, "frame_count": 3},
                ),
                (
                    "grid-columns-26-zero-viscosity",
                    {
                        "grid_columns": 26,
                        "viscosity": 0.0,
                        "steps": 24,
                        "frame_count": 3,
                    },
                ),
                (
                    "long-run-high-viscosity",
                    {
                        "grid_columns": 8,
                        "grid_rows": 8,
                        "steps": 120,
                        "frame_count": 3,
                        "viscosity": 0.05,
                    },
                ),
            )
            for case_name, case_parameters in fluid_boundary_cases:
                boundary = compute_multistrata(5, 104729, 960, 600, case_parameters)
                boundary_metrics = boundary["metrics"]
                assert isinstance(boundary_metrics, dict)
                boundary_checks.append(
                    {
                        "case": case_name,
                        "stateDigest": boundary["stateDigest"],
                        "metrics": {
                            key: boundary_metrics[key]
                            for key in (
                                "fluid.nonfiniteCount",
                                "fluid.maxDivergence",
                                "fluid.dyeBoundsErrors",
                                "dyeClampCount",
                                "maxDyeExcursion",
                                "preClampNonfiniteCount",
                                "preProjectionMaxDivergence",
                                "projectionResidualRatioMax",
                                "projectionReductionErrors",
                            )
                        },
                    }
                )
                for path in _nonfinite_paths(boundary):
                    failures.append(f"variant 5 {case_name}: nonfinite value at {path}")
                if (
                    int(boundary_metrics["fluid.nonfiniteCount"]) != 0
                    or int(boundary_metrics["fluid.dyeBoundsErrors"]) != 0
                ):
                    failures.append(f"variant 5 {case_name}: finite/dye-bound invariant failed")
                if float(boundary_metrics["fluid.maxDivergence"]) > 0.08:
                    failures.append(f"variant 5 {case_name}: projected divergence exceeds 0.08")
                if (
                    int(boundary_metrics["projectionReductionErrors"]) != 0
                    or float(boundary_metrics["preProjectionMaxDivergence"])
                    <= float(boundary_metrics["fluid.maxDivergence"])
                    or not 0.0
                    <= float(boundary_metrics["projectionResidualRatioMax"])
                    <= 0.35
                ):
                    failures.append(
                        f"variant 5 {case_name}: projection residual ratio exceeds 0.35"
                    )
                if (
                    int(boundary_metrics["dyeClampCount"]) != 0
                    or int(boundary_metrics["preClampNonfiniteCount"]) != 0
                    or float(boundary_metrics["maxDyeExcursion"]) > DYE_BOUND_TOLERANCE
                ):
                    failures.append(
                        f"variant 5 {case_name}: valid run relied on dye clamping"
                    )
        elapsed = time.perf_counter() - started
        result: dict[str, object] = {
            "variant": variant,
            "algorithm": algorithm,
            "stateDigest": first["stateDigest"],
            "elapsedSeconds": elapsed,
            "metrics": metrics,
        }
        if boundary_checks:
            result["boundaryCases"] = boundary_checks
        results.append(result)
    return {"ok": not failures, "variants": results, "failures": failures}


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true", help="exercise all six numerical cores")
    parser.add_argument("--json", action="store_true", help="emit the self-test report as JSON")
    args = parser.parse_args(argv)
    if not args.self_test:
        parser.error("--self-test is required when running this module as a script")
    return args


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    try:
        report = run_self_test()
    except Exception as error:  # A CLI self-test must turn any solver failure into a nonzero exit.
        report = {"ok": False, "variants": [], "failures": [f"{type(error).__name__}: {error}"]}
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True, allow_nan=False))
    else:
        for result in report["variants"]:
            print(
                f"PASS variant {result['variant']} {result['algorithm']} "
                f"{result['stateDigest']} ({result['elapsedSeconds']:.3f}s)"
            )
        for failure in report["failures"]:
            print(f"FAIL {failure}", file=sys.stderr)
    return 0 if bool(report["ok"]) else 1


if __name__ == "__main__":
    raise SystemExit(main())
