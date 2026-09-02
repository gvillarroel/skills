#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Validate scene composition JSON plans."""

from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from pathlib import Path
from typing import Any


DEFAULT_FORBIDDEN = ["gsap", "ScrollTrigger", "TweenMax", "TimelineMax"]
REQUIRED_SCENE_FIELDS = [
    "id",
    "sceneJob",
    "viewerTask",
    "compositionChoice",
    "choiceRationale",
    "focal",
    "roles",
    "armature",
    "layout",
    "hierarchy",
    "safeZones",
    "depthLayers",
    "motionPhases",
    "validationChecks",
]
STRICT_ALIGNMENT_FIELDS = ["alignmentGrid", "armatureAnchors", "objectBounds"]
SQUARE_EDGE_FIELDS = ["edgePolicy", "cornerPolicy"]
VALIDATION_CONTRACT_FIELDS = ["validationContract"]
VALIDATION_CHECK_FIELDS = ["method", "target", "passCriterion"]
SQUARE_EDGE_MARKERS = ["square", "0-radius", "zero-radius", "hard edge", "hard-edge", "rectangular"]
ALIGNMENT_MARKERS = ["grid", "axis", "baseline", "row", "column", "modular", "orthogonal", "align"]
PADDING_KEYS = {"internalpaddingpx", "paddingpx", "boxpaddingpx", "padding"}
ROUNDING_PATTERNS = [
    r"\brounded\b",
    r"\bpill\b",
    r"\bblob\b",
    r"\bsoft[- ]edge\b",
    r"\bborder[- ]radius\b",
    r"\bcorner[- ]radius\b",
    r"\bradius\s+[1-9]\d*(?:\.\d+)?\b",
]
ZERO_PADDING_FIELDS = ["boxInteriorPolicy", "boxModel"]
GRAY_HIERARCHY_FIELDS = ["grayscaleHierarchy"]
CONTENT_BUDGET_MODES = {"editorial-overview", "faithful-zoned", "non-diagram"}
CONTENT_BUDGET_COUNT_FIELDS = [
    "plannedNodeCount",
    "plannedEdgeCount",
    "focalElementCount",
]
CONTENT_ACCOUNTING_LIST_FIELDS = [
    "sourceItems",
    "kept",
    "merged",
    "omitted",
    "movedToDetail",
]
CONTENT_TARGET_KINDS = {"scene", "detail-view", "artifact"}
CONTENT_EXTERNAL_TARGET_KINDS = {"detail-view", "artifact"}
CONTENT_ANNOTATION_KINDS = {"constraint", "fact", "quantity", "state", "unit"}
CONTENT_ENTITY_SUFFIXES = {
    "actor",
    "api",
    "application",
    "archive",
    "artifact",
    "client",
    "component",
    "database",
    "endpoint",
    "gateway",
    "pipeline",
    "producer",
    "queue",
    "reviewer",
    "schema",
    "server",
    "service",
    "stream",
    "system",
    "worker",
}
CONTENT_BUDGET_LIMITS = {
    "editorial-overview": {"nodes": 9, "edges": 12, "annotations": 4, "visible": 12},
    "faithful-zoned": {"nodes": 24, "edges": 32, "annotations": 8, "visible": 32},
    "non-diagram": {"nodes": 0, "edges": 0, "annotations": 12, "visible": 12},
}
CONTENT_VISIBLE_FIELDS = [
    "focal",
    "roles",
    "armature",
    "armatureAnchors",
    "objectBounds",
    "layout",
    "hierarchy",
    "sectionBounds",
    "cameraPath",
    "depthLayers",
    "motionPhases",
    "captionPlan",
    "functionalTextPolicy",
    "editorialTextPolicy",
    "textPolicy",
    "onScreenText",
    "labels",
    "callouts",
]
COUNT_WORDS = {
    "zero": 0,
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
    "six": 6,
    "seven": 7,
    "eight": 8,
    "nine": 9,
    "ten": 10,
    "eleven": 11,
    "twelve": 12,
    "thirteen": 13,
    "fourteen": 14,
    "fifteen": 15,
    "sixteen": 16,
    "seventeen": 17,
    "eighteen": 18,
    "nineteen": 19,
    "twenty": 20,
    "twenty-one": 21,
    "twenty-two": 22,
    "twenty-three": 23,
    "twenty-four": 24,
    "twenty-five": 25,
    "twenty-six": 26,
    "twenty-seven": 27,
    "twenty-eight": 28,
    "twenty-nine": 29,
    "thirty": 30,
    "thirty-one": 31,
    "thirty-two": 32,
}


def _flatten_text(value: Any) -> str:
    if isinstance(value, dict):
        return "\n".join(f"{k}: {_flatten_text(v)}" for k, v in value.items())
    if isinstance(value, list):
        return "\n".join(_flatten_text(item) for item in value)
    if value is None:
        return ""
    return str(value)


def _is_empty(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, str):
        return not value.strip()
    if isinstance(value, (list, dict)):
        return len(value) == 0
    return False


def _is_nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _parse_hex_gray(value: Any) -> tuple[int, int, int] | None:
    if not isinstance(value, str):
        return None
    match = re.fullmatch(r"#([0-9a-fA-F]{6})", value.strip())
    if not match:
        return None
    raw = match.group(1)
    rgb = tuple(int(raw[idx : idx + 2], 16) for idx in (0, 2, 4))
    if rgb[0] != rgb[1] or rgb[1] != rgb[2]:
        return None
    return rgb


def _as_number(value: Any) -> float | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        match = re.fullmatch(r"\s*(-?\d+(?:\.\d+)?)\s*(?:px)?\s*", value)
        if match:
            return float(match.group(1))
    return None


def _find_positive_padding(value: Any, path: str = "root") -> list[str]:
    errors: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            child_path = f"{path}.{key}"
            key_text = str(key).lower()
            if key_text in PADDING_KEYS:
                numeric = _as_number(child)
                if numeric is not None and numeric > 0:
                    errors.append(f"{child_path} is positive ({child!r})")
            errors.extend(_find_positive_padding(child, child_path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            errors.extend(_find_positive_padding(child, f"{path}[{index}]"))
    elif isinstance(value, str):
        text = value.lower()
        if "padding" in text and re.search(r"\b[1-9]\d*(?:\.\d+)?\s*px\b", text):
            errors.append(f"{path} contains positive padding text ({value!r})")
    return errors


def _find_internal_padding(value: Any) -> Any:
    if isinstance(value, dict):
        for key, child in value.items():
            if str(key).lower() in PADDING_KEYS:
                return child
            found = _find_internal_padding(child)
            if found is not None:
                return found
    if isinstance(value, list):
        for child in value:
            found = _find_internal_padding(child)
            if found is not None:
                return found
    return None


def _has_zero_padding_policy(scene: dict[str, Any]) -> bool:
    box_model = scene.get("boxModel")
    if not isinstance(box_model, dict):
        return False
    return _as_number(box_model.get("internalPaddingPx")) == 0 and box_model.get("contentFlushToBounds") is True


def _has_forbidden_rounding(text: str) -> bool:
    lowered = text.lower()
    if "source-native only" in lowered:
        return False
    normalized = lowered.replace("0-radius", "").replace("zero-radius", "")
    return any(re.search(pattern, normalized) for pattern in ROUNDING_PATTERNS)


def _validate_strict_alignment(scene_id: str, scene: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    alignment_text = _flatten_text(scene.get("alignmentGrid")).lower()
    if not any(marker in alignment_text for marker in ALIGNMENT_MARKERS):
        errors.append(
            f"{scene_id}: alignmentGrid must mention a concrete grid, axis, baseline, row, column, modular, orthogonal, or alignment rule"
        )
    anchors = scene.get("armatureAnchors")
    if not isinstance(anchors, list) or len([item for item in anchors if not _is_empty(item)]) < 2:
        errors.append(f"{scene_id}: armatureAnchors must contain at least two anchors")
    bounds = scene.get("objectBounds")
    if not isinstance(bounds, list) or not bounds:
        errors.append(f"{scene_id}: objectBounds must be a non-empty list of structured objects")
        return errors
    for bound_index, bound in enumerate(bounds, start=1):
        if not isinstance(bound, dict):
            errors.append(f"{scene_id}: objectBounds item {bound_index} must be an object")
            continue
        if _is_empty(bound.get("id")):
            errors.append(f"{scene_id}: objectBounds item {bound_index} missing 'id'")
        has_numeric_bounds = all(_as_number(bound.get(field)) is not None for field in ("x", "y", "width", "height"))
        has_structured_location = any(not _is_empty(bound.get(field)) for field in ("zone", "anchor", "clearance"))
        if not (has_numeric_bounds or has_structured_location):
            errors.append(
                f"{scene_id}: objectBounds item {bound_index} needs x/y/width/height or zone/anchor/clearance fields"
            )
    return errors


def _validate_gray_hierarchy(scene_id: str, value: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(value, list) or len(value) < 3:
        return [f"{scene_id}: grayscaleHierarchy must contain at least 3 structured levels"]
    levels: list[tuple[int, int, str]] = []
    for index, item in enumerate(value, start=1):
        if not isinstance(item, dict):
            errors.append(f"{scene_id}: grayscaleHierarchy item {index} must be an object")
            continue
        if _is_empty(item.get("role")):
            errors.append(f"{scene_id}: grayscaleHierarchy item {index} missing 'role'")
        raw_level = item.get("level")
        if not isinstance(raw_level, int):
            errors.append(f"{scene_id}: grayscaleHierarchy item {index} missing integer 'level'")
            continue
        gray_value = item.get("grayHex") or item.get("hex")
        rgb = _parse_hex_gray(gray_value)
        if rgb is None:
            errors.append(
                f"{scene_id}: grayscaleHierarchy item {index} must use a #RRGGBB grayHex where R=G=B"
            )
            continue
        levels.append((raw_level, rgb[0], str(gray_value).lower()))
    if len({level for level, _, _ in levels}) != len(levels):
        errors.append(f"{scene_id}: grayscaleHierarchy levels must be distinct")
    if len({hex_value for _, _, hex_value in levels}) != len(levels):
        errors.append(f"{scene_id}: grayscaleHierarchy grayHex values must be distinct")
    ordered = sorted(levels)
    if len(ordered) >= 2:
        values = [gray for _, gray, _ in ordered]
        increasing = all(a < b for a, b in zip(values, values[1:]))
        decreasing = all(a > b for a, b in zip(values, values[1:]))
        if not (increasing or decreasing):
            errors.append(f"{scene_id}: grayscaleHierarchy gray values must be monotonic by level")
    return errors


def _string_items(value: Any) -> list[str] | None:
    if not isinstance(value, list):
        return None
    items: list[str] = []
    for item in value:
        if not isinstance(item, str) or not item.strip():
            return None
        items.append(item.strip())
    return items


def _count_token(value: str) -> int:
    return int(value) if value.isdigit() else COUNT_WORDS[value.lower()]


def _validate_numeric_content_claims(
    scene_id: str,
    checks: Any,
    *,
    source_count: int,
    node_count: int,
    edge_count: int,
    focal_count: int,
) -> list[str]:
    if not isinstance(checks, list):
        return []
    number = r"\d+|" + "|".join(re.escape(word) for word in sorted(COUNT_WORDS, key=len, reverse=True))
    operator = (
        r"exactly|all|at\s+most|no\s+more\s+than|up\s+to|maximum(?:\s+of)?|"
        r"at\s+least|no\s+fewer\s+than|minimum(?:\s+of)?|fewer\s+than|"
        r"less\s+than|more\s+than|greater\s+than"
    )
    operator = (
        operator
        + r"|max(?:imum)?(?:\s+of)?|min(?:imum)?(?:\s+of)?"
    )
    contracts = (
        (r"(?:required\s+)?(?:source\s*items?|sourceItems)", source_count, "sourceItems"),
        (r"(?:nodes?|nodeItems)", node_count, "nodeItems"),
        (r"(?:edges?|relations?|edgeItems)", edge_count, "edgeItems"),
        (r"(?:focal\s+(?:elements?|items?)|focalItems)", focal_count, "focalItems"),
    )
    errors: list[str] = []
    for index, check in enumerate(checks, start=1):
        if not isinstance(check, dict):
            errors.append(f"{scene_id}: validationChecks item {index} must be an object under content-accounting mode")
            continue
        for field in VALIDATION_CHECK_FIELDS:
            if not _is_nonempty_string(check.get(field)):
                errors.append(
                    f"{scene_id}: validationChecks item {index} needs a non-empty string {field} under content-accounting mode"
                )
        text = str(check.get("passCriterion", ""))
        for unit, actual, label in contracts:
            patterns = (
                rf"\b(?:(?P<pre_operator>{operator})\s+)?(?P<count>{number})\s+"
                rf"(?P<unit>{unit})(?:\s+(?P<post_operator>{operator}))?\b",
                rf"\b(?P<unit>{unit})\s+(?:count\s*)?"
                rf"(?:(?:is|are|equals?|=|:)\s*)?"
                rf"(?:(?P<pre_operator>{operator})\s+)?(?P<count>{number})"
                rf"(?:\s+(?P<post_operator>{operator}))?\b",
            )
            seen_spans: set[tuple[int, int]] = set()
            for pattern in patterns:
                for match in re.finditer(pattern, text, re.IGNORECASE):
                    if match.span() in seen_spans:
                        continue
                    seen_spans.add(match.span())
                    claimed = _count_token(match.group("count"))
                    raw_operators = [
                        re.sub(r"\s+", " ", raw.casefold())
                        for raw in (match.group("pre_operator"), match.group("post_operator"))
                        if raw
                    ]

                    def operator_relation(raw: str) -> str:
                        if raw in {"exactly", "all"}:
                            return "exactly"
                        if raw in {
                            "at most", "no more than", "up to", "max", "maximum",
                            "max of", "maximum of",
                        }:
                            return "at most"
                        if raw in {
                            "at least", "no fewer than", "min", "minimum",
                            "min of", "minimum of",
                        }:
                            return "at least"
                        if raw in {"fewer than", "less than"}:
                            return "less than"
                        return "greater than"

                    relations = {operator_relation(raw) for raw in raw_operators}
                    if len(relations) > 1:
                        errors.append(
                            f"{scene_id}: validationChecks item {index} uses conflicting numeric "
                            f"operators for {claimed} {label}"
                        )
                        continue
                    relation = next(iter(relations), "exactly")
                    valid = {
                        "exactly": actual == claimed,
                        "at most": actual <= claimed,
                        "at least": actual >= claimed,
                        "less than": actual < claimed,
                        "greater than": actual > claimed,
                    }[relation]
                    if not valid:
                        errors.append(
                            f"{scene_id}: validationChecks item {index} claims {claimed} {label} "
                            f"with operator {relation}, but the structured contract contains {actual}"
                        )
    return errors


def _content_item_markers(item: str) -> list[str]:
    normalized = re.sub(
        r"\s+", " ", unicodedata.normalize("NFKC", item).casefold()
    ).strip()
    return [normalized] if normalized else []


def _annotation_looks_like_entity(item: str) -> bool:
    tokens = re.findall(r"[a-z0-9]+", item.casefold())
    if not tokens:
        return False
    suffix = tokens[-1]
    if suffix.endswith("s") and suffix[:-1] in CONTENT_ENTITY_SUFFIXES:
        suffix = suffix[:-1]
    return suffix in CONTENT_ENTITY_SUFFIXES


def _validate_content_accounting(scene_id: str, scene: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    budget = scene.get("contentBudget")
    accounting = scene.get("contentAccounting")
    mode: str | None = None
    node_items: list[str] = []
    focal_items: list[str] = []
    annotation_items: list[str] = []
    edge_count = 0

    if not isinstance(budget, dict):
        errors.append(f"{scene_id}: contentBudget must be an object")
    else:
        mode = budget.get("mode")
        if mode not in CONTENT_BUDGET_MODES:
            errors.append(
                f"{scene_id}: contentBudget.mode must be one of {sorted(CONTENT_BUDGET_MODES)}"
            )
        counts: dict[str, int] = {}
        for field in CONTENT_BUDGET_COUNT_FIELDS:
            value = budget.get(field)
            if isinstance(value, bool) or not isinstance(value, int) or value < 0:
                errors.append(f"{scene_id}: contentBudget.{field} must be a non-negative integer")
            else:
                counts[field] = value
        if not _is_nonempty_string(budget.get("overflowStrategy")):
            errors.append(f"{scene_id}: contentBudget.overflowStrategy must be a non-empty string")

        node_items_value = _string_items(budget.get("nodeItems"))
        if node_items_value is None:
            errors.append(f"{scene_id}: contentBudget.nodeItems must contain only non-empty strings")
        else:
            node_items = node_items_value
            if len(set(node_items)) != len(node_items):
                errors.append(f"{scene_id}: contentBudget.nodeItems must be unique")

        focal_items_value = _string_items(budget.get("focalItems"))
        if focal_items_value is None:
            errors.append(f"{scene_id}: contentBudget.focalItems must contain only non-empty strings")
        else:
            focal_items = focal_items_value
            if len(set(focal_items)) != len(focal_items):
                errors.append(f"{scene_id}: contentBudget.focalItems must be unique")

        edges = budget.get("edgeItems")
        if not isinstance(edges, list):
            errors.append(f"{scene_id}: contentBudget.edgeItems must be a list")
        else:
            edge_count = len(edges)
            seen_edges: set[tuple[str, str, str]] = set()
            for index, edge in enumerate(edges, start=1):
                if not isinstance(edge, dict):
                    errors.append(f"{scene_id}: contentBudget.edgeItems item {index} must be an object")
                    continue
                source = edge.get("from")
                target = edge.get("to")
                label = edge.get("label", "")
                if not _is_nonempty_string(source) or not _is_nonempty_string(target):
                    errors.append(
                        f"{scene_id}: contentBudget.edgeItems item {index} needs non-empty string from and to"
                    )
                    continue
                if "label" in edge and not _is_nonempty_string(label):
                    errors.append(
                        f"{scene_id}: contentBudget.edgeItems item {index} label must be a non-empty string when present"
                    )
                edge_key = (source.strip(), target.strip(), label.strip() if isinstance(label, str) else "")
                if edge_key in seen_edges:
                    errors.append(f"{scene_id}: contentBudget.edgeItems item {index} duplicates an earlier edge")
                seen_edges.add(edge_key)
                unknown_endpoints = sorted({source.strip(), target.strip()} - set(node_items))
                if unknown_endpoints:
                    errors.append(
                        f"{scene_id}: contentBudget.edgeItems item {index} references unknown nodeItems: "
                        + ", ".join(unknown_endpoints)
                    )

        annotations = budget.get("annotationItems")
        if not isinstance(annotations, list):
            errors.append(f"{scene_id}: contentBudget.annotationItems must be a list")
        else:
            for index, annotation in enumerate(annotations, start=1):
                if not isinstance(annotation, dict):
                    errors.append(
                        f"{scene_id}: contentBudget.annotationItems item {index} must be an object"
                    )
                    continue
                item = annotation.get("item")
                attached_to = annotation.get("attachedTo")
                annotation_kind = annotation.get("kind")
                if (
                    not _is_nonempty_string(item)
                    or not _is_nonempty_string(attached_to)
                    or annotation_kind not in CONTENT_ANNOTATION_KINDS
                ):
                    errors.append(
                        f"{scene_id}: contentBudget.annotationItems item {index} needs non-empty string item and "
                        f"attachedTo plus kind in {sorted(CONTENT_ANNOTATION_KINDS)}"
                    )
                    continue
                annotation_items.append(item.strip())
                if _annotation_looks_like_entity(item):
                    errors.append(
                        f"{scene_id}: contentBudget.annotationItems item {index} looks like an entity; "
                        "actors, services, systems, artifacts, and other entity nouns belong in nodeItems"
                    )
                if mode != "non-diagram" and attached_to.strip() not in node_items:
                    errors.append(
                        f"{scene_id}: contentBudget.annotationItems item {index} attaches to unknown nodeItem {attached_to.strip()!r}"
                    )
            if len(set(annotation_items)) != len(annotation_items):
                errors.append(f"{scene_id}: contentBudget.annotationItems item values must be unique")

        if counts.get("plannedNodeCount") != len(node_items):
            errors.append(
                f"{scene_id}: contentBudget.plannedNodeCount must equal len(nodeItems) ({len(node_items)})"
            )
        if counts.get("plannedEdgeCount") != edge_count:
            errors.append(
                f"{scene_id}: contentBudget.plannedEdgeCount must equal len(edgeItems) ({edge_count})"
            )
        if counts.get("focalElementCount") != len(focal_items):
            errors.append(
                f"{scene_id}: contentBudget.focalElementCount must equal len(focalItems) ({len(focal_items)})"
            )
        unknown_focal_items = sorted(set(focal_items) - set(node_items) - set(annotation_items))
        if unknown_focal_items:
            errors.append(
                f"{scene_id}: contentBudget.focalItems must be drawn nodeItems or visible annotationItems: "
                + ", ".join(unknown_focal_items)
            )
        overlap = sorted(set(node_items).intersection(annotation_items))
        if overlap:
            errors.append(
                f"{scene_id}: visible items cannot be both nodeItems and annotationItems: "
                + ", ".join(overlap)
            )
        limits = CONTENT_BUDGET_LIMITS.get(mode)
        if limits is not None:
            if len(annotation_items) > limits["annotations"]:
                errors.append(
                    f"{scene_id}: {mode} annotationItems must not exceed {limits['annotations']}"
                )
            visible_count = len(node_items) + len(annotation_items)
            if visible_count > limits["visible"]:
                errors.append(
                    f"{scene_id}: {mode} total visible nodeItems plus annotationItems must not exceed "
                    f"{limits['visible']} (found {visible_count})"
                )
        if counts.get("focalElementCount", 0) > 2:
            errors.append(f"{scene_id}: contentBudget.focalElementCount must not exceed 2")
        if mode == "editorial-overview":
            if counts.get("plannedNodeCount", 0) > 9:
                errors.append(f"{scene_id}: editorial-overview plannedNodeCount must not exceed 9")
            if counts.get("plannedEdgeCount", 0) > 12:
                errors.append(f"{scene_id}: editorial-overview plannedEdgeCount must not exceed 12")
        elif mode == "faithful-zoned":
            if counts.get("plannedNodeCount", 0) > 24:
                errors.append(f"{scene_id}: faithful-zoned plannedNodeCount must not exceed 24")
            if counts.get("plannedEdgeCount", 0) > 32:
                errors.append(f"{scene_id}: faithful-zoned plannedEdgeCount must not exceed 32")
        elif mode == "non-diagram":
            if counts.get("plannedNodeCount", 0) != 0 or counts.get("plannedEdgeCount", 0) != 0:
                errors.append(
                    f"{scene_id}: non-diagram mode must use plannedNodeCount 0 and plannedEdgeCount 0"
                )
            if node_items or edge_count:
                errors.append(
                    f"{scene_id}: non-diagram mode must use empty nodeItems and edgeItems"
                )

    if not isinstance(accounting, dict):
        errors.append(f"{scene_id}: contentAccounting must be an object")
        return errors
    for field in CONTENT_ACCOUNTING_LIST_FIELDS:
        if field not in accounting or not isinstance(accounting[field], list):
            errors.append(f"{scene_id}: contentAccounting.{field} must be a list")

    source_items = _string_items(accounting.get("sourceItems"))
    if source_items is None:
        errors.append(f"{scene_id}: contentAccounting.sourceItems must contain only non-empty strings")
        return errors
    if not source_items and mode != "non-diagram":
        errors.append(
            f"{scene_id}: contentAccounting.sourceItems may be empty only in non-diagram mode"
        )
    if len(set(source_items)) != len(source_items):
        errors.append(f"{scene_id}: contentAccounting.sourceItems must be unique")
    source_set = set(source_items)

    dispositions: list[tuple[str, str]] = []
    kept = _string_items(accounting.get("kept"))
    if kept is None:
        errors.append(f"{scene_id}: contentAccounting.kept must contain only non-empty strings")
        kept = []
    dispositions.extend(("kept", item) for item in kept)

    merged_outputs: list[str] = []
    merged = accounting.get("merged")
    if isinstance(merged, list):
        for index, record in enumerate(merged, start=1):
            if not isinstance(record, dict):
                errors.append(f"{scene_id}: contentAccounting.merged item {index} must be an object")
                continue
            merged_items = _string_items(record.get("sourceItems"))
            if merged_items is None or len(merged_items) < 2:
                errors.append(
                    f"{scene_id}: contentAccounting.merged item {index} needs at least two sourceItems"
                )
                merged_items = []
            if not _is_nonempty_string(record.get("into")) or not _is_nonempty_string(record.get("reason")):
                errors.append(
                    f"{scene_id}: contentAccounting.merged item {index} needs non-empty string into and reason"
                )
            else:
                merged_outputs.append(record["into"].strip())
            dispositions.extend(("merged", item) for item in merged_items)

    omitted = accounting.get("omitted")
    if isinstance(omitted, list):
        for index, record in enumerate(omitted, start=1):
            if not isinstance(record, dict) or not _is_nonempty_string(record.get("item")):
                errors.append(f"{scene_id}: contentAccounting.omitted item {index} needs a non-empty string item")
                continue
            if not _is_nonempty_string(record.get("reason")):
                errors.append(f"{scene_id}: contentAccounting.omitted item {index} needs a non-empty string reason")
            dispositions.append(("omitted", record["item"].strip()))

    moved = accounting.get("movedToDetail")
    if isinstance(moved, list):
        for index, record in enumerate(moved, start=1):
            if not isinstance(record, dict) or not _is_nonempty_string(record.get("item")):
                errors.append(
                    f"{scene_id}: contentAccounting.movedToDetail item {index} needs a non-empty string item"
                )
                continue
            target = record.get("target")
            valid_target = isinstance(target, dict)
            if valid_target:
                target_kind = target.get("kind")
                target_id = target.get("id")
                valid_target = target_kind in CONTENT_TARGET_KINDS and _is_nonempty_string(target_id)
            if not valid_target or not _is_nonempty_string(record.get("reason")):
                errors.append(
                    f"{scene_id}: contentAccounting.movedToDetail item {index} needs a target object "
                    f"with kind in {sorted(CONTENT_TARGET_KINDS)}, a non-empty string id, and a non-empty string reason"
                )
            dispositions.append(("movedToDetail", record["item"].strip()))

    disposition_counts: dict[str, int] = {}
    for _, item in dispositions:
        disposition_counts[item] = disposition_counts.get(item, 0) + 1
    duplicate_dispositions = sorted(
        item for item, count in disposition_counts.items() if count > 1
    )
    missing = sorted(source_set - set(disposition_counts))
    unknown = sorted(set(disposition_counts) - source_set)
    if duplicate_dispositions:
        errors.append(
            f"{scene_id}: source items have multiple dispositions: {', '.join(duplicate_dispositions)}"
        )
    if missing:
        errors.append(f"{scene_id}: source items are not accounted for: {', '.join(missing)}")
    if unknown:
        errors.append(f"{scene_id}: dispositions contain unknown source items: {', '.join(unknown)}")

    visible_items = set(kept).union(merged_outputs)
    budgeted_visible_items = set(node_items).union(annotation_items)
    missing_from_budget = sorted(visible_items - budgeted_visible_items)
    unknown_budget_items = sorted(budgeted_visible_items - visible_items)
    if missing_from_budget:
        errors.append(
            f"{scene_id}: kept and merged visible items missing from contentBudget count basis: "
            + ", ".join(missing_from_budget)
        )
    if unknown_budget_items:
        errors.append(
            f"{scene_id}: contentBudget count basis contains items that are not kept or merged outputs: "
            + ", ".join(unknown_budget_items)
        )

    hidden_dispositions: list[tuple[str, str]] = []
    if isinstance(omitted, list):
        hidden_dispositions.extend(
            ("omitted", record["item"].strip())
            for record in omitted
            if isinstance(record, dict) and _is_nonempty_string(record.get("item"))
        )
    if isinstance(moved, list):
        hidden_dispositions.extend(
            ("movedToDetail", record["item"].strip())
            for record in moved
            if isinstance(record, dict) and _is_nonempty_string(record.get("item"))
        )
    visible_text = re.sub(
        r"\s+",
        " ",
        unicodedata.normalize(
            "NFKC",
            _flatten_text(
                {field: scene.get(field) for field in CONTENT_VISIBLE_FIELDS if field in scene}
            ),
        ).casefold(),
    ).strip()
    for disposition, item in hidden_dispositions:
        matching_markers = [
            marker
            for marker in _content_item_markers(item)
            if re.search(rf"(?<!\w){re.escape(marker)}(?!\w)", visible_text)
        ]
        if matching_markers:
            errors.append(
                f"{scene_id}: {disposition} source item {item!r} still appears in visible-bearing scene fields "
                f"via {matching_markers[0]!r}"
            )

    parsed_source_anchors = _string_items(scene.get("sourceAnchors"))
    if parsed_source_anchors is None:
        errors.append(f"{scene_id}: sourceAnchors must be a list containing only non-empty strings")
        source_anchors: list[str] = []
    else:
        source_anchors = parsed_source_anchors
        if len(set(source_anchors)) != len(source_anchors):
            errors.append(f"{scene_id}: sourceAnchors must be unique")
    anchors_missing_from_ledger = sorted(set(source_anchors) - source_set)
    if anchors_missing_from_ledger:
        errors.append(
            f"{scene_id}: local source anchors must appear in contentAccounting.sourceItems: "
            + ", ".join(anchors_missing_from_ledger)
        )
    anchors_in_ledger = source_set.intersection(source_anchors)
    anchors_not_kept = sorted(anchors_in_ledger - set(kept))
    if anchors_not_kept:
        errors.append(
            f"{scene_id}: required source anchors present in sourceItems must be kept: {', '.join(anchors_not_kept)}"
        )
    errors.extend(
        _validate_numeric_content_claims(
            scene_id,
            scene.get("validationChecks"),
            source_count=len(source_items),
            node_count=len(node_items),
            edge_count=edge_count,
            focal_count=len(focal_items),
        )
    )
    return errors


def _validate_content_target_registry(
    plan: dict[str, Any], scene_ids: set[str]
) -> tuple[dict[tuple[str, str], set[str]], list[str]]:
    registry: dict[tuple[str, str], set[str]] = {}
    errors: list[str] = []
    targets = plan.get("contentTargets")
    if not isinstance(targets, list):
        return {}, ["Plan contentTargets must be a list under content-accounting mode"]
    for index, target in enumerate(targets, start=1):
        if not isinstance(target, dict):
            errors.append(f"contentTargets item {index} must be an object")
            continue
        kind = target.get("kind")
        target_id = target.get("id")
        receives = _string_items(target.get("receives"))
        if kind not in CONTENT_EXTERNAL_TARGET_KINDS or not _is_nonempty_string(target_id):
            errors.append(
                f"contentTargets item {index} needs kind in {sorted(CONTENT_EXTERNAL_TARGET_KINDS)} "
                "and a non-empty string id"
            )
            continue
        if receives is None or not receives:
            errors.append(f"contentTargets item {index} receives must contain unique non-empty strings")
            receives = []
        elif len(set(receives)) != len(receives):
            errors.append(f"contentTargets item {index} receives must be unique")
        key = (kind, target_id.strip())
        if key in registry:
            errors.append(f"Duplicate content target: {kind} {target_id.strip()!r}")
        registry[key] = set(receives)
        if kind == "artifact" and not _is_nonempty_string(target.get("path")):
            errors.append(f"contentTargets item {index} artifact needs a non-empty string path")
        if kind == "detail-view":
            owner_scene = target.get("ownerScene")
            if not _is_nonempty_string(owner_scene):
                errors.append(f"contentTargets item {index} detail-view needs a non-empty string ownerScene")
            elif owner_scene.strip() not in scene_ids:
                errors.append(
                    f"contentTargets item {index} detail-view ownerScene {owner_scene.strip()!r} is unknown"
                )
    return registry, errors


def _validate_cross_scene_content_moves(
    scenes: list[Any],
    require_anchors: list[str],
    declared_targets: dict[tuple[str, str], set[str]] | None = None,
) -> list[str]:
    errors: list[str] = []
    scene_entries = [
        (index, str(scene.get("id")), scene)
        for index, scene in enumerate(scenes)
        if isinstance(scene, dict) and not _is_empty(scene.get("id"))
    ]
    scene_by_id = {scene_id: scene for _, scene_id, scene in scene_entries}
    scene_index_by_id = {scene_id: index for index, scene_id, _ in scene_entries}
    all_source_items: set[str] = set()
    all_kept: set[str] = set()
    occurrences: dict[str, list[tuple[int, str, set[str]]]] = {}
    scene_moves: list[tuple[int, str, str, str]] = []
    external_deliveries: dict[tuple[str, str], list[str]] = {}

    for scene_index, scene_id, scene in scene_entries:
        accounting = scene.get("contentAccounting")
        if not isinstance(accounting, dict):
            continue
        source_items = _string_items(accounting.get("sourceItems")) or []
        kept = _string_items(accounting.get("kept")) or []
        all_source_items.update(source_items)
        all_kept.update(kept)

        dispositions: dict[str, set[str]] = {}
        for item in kept:
            dispositions.setdefault(item, set()).add("kept")
        merged = accounting.get("merged")
        if isinstance(merged, list):
            for record in merged:
                if not isinstance(record, dict):
                    continue
                for item in _string_items(record.get("sourceItems")) or []:
                    dispositions.setdefault(item, set()).add("merged")
        omitted = accounting.get("omitted")
        if isinstance(omitted, list):
            for record in omitted:
                if isinstance(record, dict) and _is_nonempty_string(record.get("item")):
                    dispositions.setdefault(record["item"].strip(), set()).add("omitted")
        moved = accounting.get("movedToDetail")
        if isinstance(moved, list):
            for record in moved:
                if isinstance(record, dict) and _is_nonempty_string(record.get("item")):
                    dispositions.setdefault(record["item"].strip(), set()).add("movedToDetail")
        for item in source_items:
            occurrences.setdefault(item, []).append(
                (scene_index, scene_id, dispositions.get(item, set()))
            )

        if not isinstance(moved, list):
            continue
        for index, record in enumerate(moved, start=1):
            if not isinstance(record, dict) or not _is_nonempty_string(record.get("item")):
                continue
            target = record.get("target")
            if not isinstance(target, dict):
                continue
            target_kind = target.get("kind")
            target_id = target.get("id")
            if target_kind not in CONTENT_TARGET_KINDS or not _is_nonempty_string(target_id):
                continue
            item = record["item"].strip()
            if target_kind != "scene":
                target_key = (target_kind, target_id.strip())
                external_deliveries.setdefault(target_key, []).append(item)
                receives = (declared_targets or {}).get(target_key)
                if receives is None:
                    errors.append(
                        f"{scene_id}: movedToDetail item {index} targets undeclared {target_kind} "
                        f"{target_id.strip()!r}"
                    )
                elif item not in receives:
                    errors.append(
                        f"{scene_id}: moved item {item!r} is absent from declared target "
                        f"{target_kind} {target_id.strip()!r} receives"
                    )
                continue
            scene_moves.append((scene_index, scene_id, item, target_id.strip()))
            target_scene = scene_by_id.get(target_id.strip())
            if target_scene is None:
                errors.append(
                    f"{scene_id}: movedToDetail item {index} targets unknown scene id {target_id.strip()!r}"
                )
                continue
            target_index = scene_index_by_id[target_id.strip()]
            if target_index <= scene_index:
                errors.append(
                    f"{scene_id}: moved item {item!r} must target a later scene, not {target_id.strip()!r}"
                )
            target_accounting = target_scene.get("contentAccounting")
            target_source_items = (
                _string_items(target_accounting.get("sourceItems"))
                if isinstance(target_accounting, dict)
                else None
            ) or []
            target_kept = (
                _string_items(target_accounting.get("kept"))
                if isinstance(target_accounting, dict)
                else None
            ) or []
            if item not in target_source_items:
                errors.append(
                    f"{scene_id}: moved item {item!r} must appear in target scene "
                    f"{target_id.strip()!r} sourceItems"
                )
            if item not in target_kept:
                errors.append(
                    f"{scene_id}: moved item {item!r} must be kept by target scene {target_id.strip()!r}"
                )

    for item, item_occurrences in sorted(occurrences.items()):
        if len(item_occurrences) == 1:
            continue
        ordered = sorted(item_occurrences, key=lambda occurrence: (occurrence[0], occurrence[1]))
        if len(ordered) != 2:
            errors.append(
                f"Source item {item!r} appears in {len(ordered)} scene ledgers; "
                "an item may repeat only once through one explicit forward scene move"
            )
            continue
        source_index, source_id, source_dispositions = ordered[0]
        target_index, target_id, target_dispositions = ordered[1]
        matching_moves = [
            move
            for move in scene_moves
            if move[1] == source_id and move[2] == item and move[3] == target_id
        ]
        all_item_moves = [move for move in scene_moves if move[2] == item]
        if (
            source_index >= target_index
            or source_dispositions != {"movedToDetail"}
            or target_dispositions != {"kept"}
            or len(matching_moves) != 1
            or len(all_item_moves) != 1
        ):
            errors.append(
                f"Source item {item!r} repeats across scenes without one exact forward move: "
                f"{source_id!r} must move it to later target {target_id!r}, which must keep it"
            )

    declared_targets = declared_targets or {}
    for target_key, declared_items in sorted(declared_targets.items()):
        delivered_items = external_deliveries.get(target_key, [])
        undelivered = sorted(declared_items - set(delivered_items))
        if undelivered:
            errors.append(
                f"Declared target {target_key[0]} {target_key[1]!r} lists receives items with no "
                "matching movedToDetail delivery: " + ", ".join(undelivered)
            )
        duplicate_deliveries = sorted(
            item for item in set(delivered_items) if delivered_items.count(item) > 1
        )
        if duplicate_deliveries:
            errors.append(
                f"Declared target {target_key[0]} {target_key[1]!r} receives duplicate deliveries: "
                + ", ".join(duplicate_deliveries)
            )

    unaccounted_required = sorted(
        anchor for anchor in require_anchors if anchor not in all_source_items
    )
    if unaccounted_required:
        errors.append(
            "Required anchors are absent from all contentAccounting.sourceItems ledgers: "
            + ", ".join(unaccounted_required)
        )

    missing_required = sorted(
        anchor
        for anchor in require_anchors
        if anchor in all_source_items and anchor not in all_kept
    )
    if missing_required:
        errors.append(
            "Required anchors present in content ledgers must be kept in at least one scene: "
            + ", ".join(missing_required)
        )
    return errors


def load_plan(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"{path} is not valid JSON: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError("Plan root must be a JSON object")
    return data


def validate_plan(
    plan: dict[str, Any],
    *,
    expect_scenes: int | None,
    min_scenes: int | None,
    require_anchors: list[str],
    forbidden: list[str],
    allow_held_scenes: bool,
    require_strict_alignment: bool,
    require_square_edges: bool,
    require_validation_contract: bool,
    require_zero_box_padding: bool,
    require_grayscale_hierarchy: bool,
    require_content_accounting: bool = False,
) -> list[str]:
    errors: list[str] = []
    text = _flatten_text(plan)

    scenes = plan.get("scenes")
    if not isinstance(scenes, list) or not scenes:
        errors.append("Plan must contain a non-empty 'scenes' list")
        scenes = []

    if expect_scenes is not None and len(scenes) != expect_scenes:
        errors.append(f"Expected {expect_scenes} scenes, found {len(scenes)}")
    if min_scenes is not None and len(scenes) < min_scenes:
        errors.append(f"Expected at least {min_scenes} scenes, found {len(scenes)}")

    for anchor in require_anchors:
        if anchor not in text:
            errors.append(f"Missing required anchor: {anchor}")

    for term in forbidden:
        pattern = re.compile(re.escape(term), re.IGNORECASE)
        if pattern.search(text):
            errors.append(f"Forbidden term appears in plan: {term}")

    seen_ids: set[str] = set()
    for index, scene in enumerate(scenes, start=1):
        if not isinstance(scene, dict):
            errors.append(f"Scene {index} must be an object")
            continue

        scene_id = str(scene.get("id") or f"scene-{index}")
        if scene_id in seen_ids:
            errors.append(f"Duplicate scene id: {scene_id}")
        seen_ids.add(scene_id)

        for field in REQUIRED_SCENE_FIELDS:
            if field not in scene or _is_empty(scene[field]):
                errors.append(f"{scene_id}: missing or empty field '{field}'")

        if require_strict_alignment:
            for field in STRICT_ALIGNMENT_FIELDS:
                if field not in scene or _is_empty(scene[field]):
                    errors.append(f"{scene_id}: missing or empty strict-alignment field '{field}'")
            errors.extend(_validate_strict_alignment(scene_id, scene))

        if require_square_edges:
            for field in SQUARE_EDGE_FIELDS:
                if field not in scene or _is_empty(scene[field]):
                    errors.append(f"{scene_id}: missing or empty square-edge field '{field}'")
            edge_text = _flatten_text({field: scene.get(field) for field in SQUARE_EDGE_FIELDS}).lower()
            if not any(marker in edge_text for marker in SQUARE_EDGE_MARKERS):
                errors.append(
                    f"{scene_id}: edge/corner policy must explicitly require square, rectangular, hard-edge, or 0-radius geometry"
                )
            if _has_forbidden_rounding(edge_text):
                errors.append(
                    f"{scene_id}: edge/corner policy must not allow rounded, pill, soft-edge, blob, or positive-radius geometry"
                )

        if require_validation_contract:
            for field in VALIDATION_CONTRACT_FIELDS:
                if field not in scene or _is_empty(scene[field]):
                    errors.append(f"{scene_id}: missing or empty validation-contract field '{field}'")

        if require_zero_box_padding:
            for field in ZERO_PADDING_FIELDS:
                if field not in scene or _is_empty(scene[field]):
                    errors.append(f"{scene_id}: missing or empty zero-padding field '{field}'")
            if not _has_zero_padding_policy(scene):
                errors.append(
                    f"{scene_id}: boxModel must explicitly set internalPaddingPx to 0 and contentFlushToBounds to true"
                )
            for padding_error in _find_positive_padding(scene):
                errors.append(f"{scene_id}: positive padding is not allowed under zero-padding mode: {padding_error}")

        if require_grayscale_hierarchy:
            for field in GRAY_HIERARCHY_FIELDS:
                if field not in scene or _is_empty(scene[field]):
                    errors.append(f"{scene_id}: missing or empty grayscale hierarchy field '{field}'")
            if "grayscaleHierarchy" in scene:
                errors.extend(_validate_gray_hierarchy(scene_id, scene["grayscaleHierarchy"]))

        if require_content_accounting:
            errors.extend(_validate_content_accounting(scene_id, scene))

        depth_layers = scene.get("depthLayers")
        if isinstance(depth_layers, list) and len(depth_layers) < 3:
            errors.append(f"{scene_id}: depthLayers should contain at least 3 layers")

        motion_phases = scene.get("motionPhases")
        held = str(scene.get("sceneJob", "")).lower().find("held") >= 0 or str(
            scene.get("compositionChoice", "")
        ).lower().find("held") >= 0
        if isinstance(motion_phases, list):
            if not motion_phases:
                errors.append(f"{scene_id}: motionPhases must not be empty")
            if len(motion_phases) < 2 and not (allow_held_scenes and held):
                errors.append(
                    f"{scene_id}: motionPhases should include more than one phase unless it is a deliberate held read"
                )
            for phase_index, phase in enumerate(motion_phases, start=1):
                if not isinstance(phase, dict):
                    errors.append(f"{scene_id}: motion phase {phase_index} must be an object")
                    continue
                for phase_field in ["name", "cue", "visualChange", "motionVerb"]:
                    if _is_empty(phase.get(phase_field)):
                        errors.append(
                            f"{scene_id}: motion phase {phase_index} missing '{phase_field}'"
                        )

        checks = scene.get("validationChecks")
        if isinstance(checks, list) and len(checks) < 2:
            errors.append(f"{scene_id}: validationChecks should contain at least 2 checks")
        if require_validation_contract and isinstance(checks, list):
            for check_index, check in enumerate(checks, start=1):
                if not isinstance(check, dict):
                    errors.append(f"{scene_id}: validation check {check_index} must be an object")
                    continue
                for check_field in VALIDATION_CHECK_FIELDS:
                    if _is_empty(check.get(check_field)):
                        errors.append(
                            f"{scene_id}: validation check {check_index} missing '{check_field}'"
                        )

        rationale = str(scene.get("choiceRationale", ""))
        if len(rationale.strip()) < 30:
            errors.append(f"{scene_id}: choiceRationale is too short to explain the choice")

    if require_content_accounting:
        video_direction = plan.get("videoDirection")
        plan_anchors: list[str] = []
        if not isinstance(video_direction, dict):
            errors.append("Plan must contain a videoDirection object under content-accounting mode")
        else:
            parsed_plan_anchors = _string_items(video_direction.get("sourceAnchors"))
            if parsed_plan_anchors is None:
                errors.append(
                    "videoDirection.sourceAnchors must be a list containing only non-empty strings"
                )
            else:
                plan_anchors = parsed_plan_anchors
                if len(set(plan_anchors)) != len(plan_anchors):
                    errors.append("videoDirection.sourceAnchors must be unique")
        plan_anchor_set = set(plan_anchors)
        missing_required_global = sorted(set(require_anchors) - plan_anchor_set)
        if missing_required_global:
            errors.append(
                "CLI required anchors must appear in videoDirection.sourceAnchors: "
                + ", ".join(missing_required_global)
            )

        all_local_anchors: set[str] = set()
        for scene in scenes:
            if not isinstance(scene, dict):
                continue
            local_anchors = _string_items(scene.get("sourceAnchors")) or []
            all_local_anchors.update(local_anchors)
            undeclared_local = sorted(set(local_anchors) - plan_anchor_set)
            if undeclared_local:
                errors.append(
                    f"{scene.get('id', 'unknown-scene')}: local sourceAnchors are absent from "
                    "videoDirection.sourceAnchors: "
                    + ", ".join(undeclared_local)
                )
        global_without_local = sorted(plan_anchor_set - all_local_anchors)
        if global_without_local:
            errors.append(
                "Global source anchors must appear in at least one scene.sourceAnchors list: "
                + ", ".join(global_without_local)
            )

        scene_ids = {
            str(scene.get("id"))
            for scene in scenes
            if isinstance(scene, dict) and _is_nonempty_string(scene.get("id"))
        }
        declared_targets, target_errors = _validate_content_target_registry(plan, scene_ids)
        errors.extend(target_errors)
        accounting_anchors = list(dict.fromkeys([*plan_anchors, *require_anchors]))
        errors.extend(
            _validate_cross_scene_content_moves(
                scenes,
                accounting_anchors,
                declared_targets,
            )
        )

    return errors


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate a scene composition JSON plan.")
    parser.add_argument("--plan", required=True, type=Path, help="Path to composition-plan.json")
    parser.add_argument("--expect-scenes", type=int, help="Require an exact scene count")
    parser.add_argument("--min-scenes", type=int, help="Require at least this many scenes")
    parser.add_argument(
        "--require-anchor",
        action="append",
        default=[],
        help="Literal string that must appear in the plan; repeat as needed",
    )
    parser.add_argument(
        "--forbid",
        action="append",
        default=[],
        help="Forbidden term; defaults also include GSAP-related terms",
    )
    parser.add_argument(
        "--allow-gsap",
        action="store_true",
        help="Do not apply the default GSAP-related forbidden terms",
    )
    parser.add_argument(
        "--allow-held-scenes",
        action="store_true",
        help="Allow deliberate held scenes to have a single motion phase",
    )
    parser.add_argument(
        "--require-strict-alignment",
        action="store_true",
        help="Require alignmentGrid, armatureAnchors, and objectBounds on each scene",
    )
    parser.add_argument(
        "--require-square-edges",
        action="store_true",
        help="Require edgePolicy and cornerPolicy to specify square, hard-edge, or 0-radius geometry",
    )
    parser.add_argument(
        "--require-validation-contract",
        action="store_true",
        help="Require validationContract and structured validationChecks with method, target, and passCriterion",
    )
    parser.add_argument(
        "--require-zero-box-padding",
        action="store_true",
        help="Require boxInteriorPolicy, boxModel, and explicit internalPaddingPx 0 or flush-to-bounds language.",
    )
    parser.add_argument(
        "--require-grayscale-hierarchy",
        action="store_true",
        help="Require structured grayscaleHierarchy levels with distinct monotonic grayscale hex values.",
    )
    parser.add_argument(
        "--require-content-accounting",
        action="store_true",
        help=(
            "Require a bounded contentBudget and exhaustive kept/merged/omitted/movedToDetail "
            "source accounting on every scene."
        ),
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    plan = load_plan(args.plan)
    forbidden = list(args.forbid)
    if not args.allow_gsap:
        forbidden.extend(DEFAULT_FORBIDDEN)

    errors = validate_plan(
        plan,
        expect_scenes=args.expect_scenes,
        min_scenes=args.min_scenes,
        require_anchors=args.require_anchor,
        forbidden=forbidden,
        allow_held_scenes=args.allow_held_scenes,
        require_strict_alignment=args.require_strict_alignment,
        require_square_edges=args.require_square_edges,
        require_validation_contract=args.require_validation_contract,
        require_zero_box_padding=args.require_zero_box_padding,
        require_grayscale_hierarchy=args.require_grayscale_hierarchy,
        require_content_accounting=args.require_content_accounting,
    )
    if errors:
        print("Scene composition plan validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print(f"Scene composition plan OK: {len(plan.get('scenes', []))} scene(s) validated.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
