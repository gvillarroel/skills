#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

"""Validate the structural and palette contract of a one-bit-dither SVG."""

from __future__ import annotations

import argparse
from colorset_contract import tokens as colorset_tokens
import json
import math
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Sequence


MODES = ("original", "custom", "regional")
QUALITY_PROFILES = ("manual", "compact", "balanced", "detailed")
SOURCE_KINDS = ("svg", "raster")
BLACK = "#000000"
WHITE = "#ffffff"
REQUIRED_ROOT_ATTRIBUTES = (
    "data-one-bit-dither-version",
    "data-mode",
    "data-quality-profile",
    "data-source-kind",
    "data-source-format",
    "data-source-frame",
    "data-source-frame-count",
    "data-dither-family",
    "data-matrix-size",
    "data-cell-size",
    "data-contrast",
    "data-alpha-threshold",
    "data-render-width",
    "data-render-height",
    "data-grid-width",
    "data-grid-height",
    "data-run-count",
    "data-region-count",
    "data-palette",
    "data-source",
)


class ValidationFailure(ValueError):
    pass


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def normalize_hex(value: str) -> str:
    token = value.strip().lower()
    if re.fullmatch(r"#[0-9a-f]{3}", token):
        token = "#" + "".join(character * 2 for character in token[1:])
    if not re.fullmatch(r"#[0-9a-f]{6}", token):
        raise ValidationFailure(f"Invalid hex color: {value!r}")
    return token


def parse_color(value: str) -> tuple[int, int, int]:
    token = normalize_hex(value)
    return tuple(int(token[index : index + 2], 16) for index in (1, 3, 5))  # type: ignore[return-value]


def relative_luminance(color: Sequence[int]) -> float:
    def linearize(channel: int) -> float:
        value = channel / 255
        return value / 12.92 if value <= 0.04045 else ((value + 0.055) / 1.055) ** 2.4

    red, green, blue = (linearize(channel) for channel in color)
    return 0.2126 * red + 0.7152 * green + 0.0722 * blue


def contrast_ratio(first: Sequence[int], second: Sequence[int]) -> float:
    luminances = sorted((relative_luminance(first), relative_luminance(second)))
    return (luminances[1] + 0.05) / (luminances[0] + 0.05)


def expected_companion(color: str) -> str:
    parsed = parse_color(color)
    return WHITE if contrast_ratio(parsed, parse_color(WHITE)) > contrast_ratio(parsed, parse_color(BLACK)) else BLACK


def parse_positive_number(element: ET.Element, attribute: str) -> float:
    value = element.get(attribute)
    try:
        parsed = float(value or "")
    except ValueError as error:
        raise ValidationFailure(f"{attribute} must be numeric") from error
    if not math.isfinite(parsed) or parsed <= 0:
        raise ValidationFailure(f"{attribute} must be positive")
    return parsed


def parse_nonnegative_int(element: ET.Element, attribute: str) -> int:
    value = element.get(attribute)
    if value is None or not re.fullmatch(r"\d+", value):
        raise ValidationFailure(f"{attribute} must be a nonnegative integer")
    return int(value)


def parse_metadata(root: ET.Element) -> dict[str, object]:
    metadata_nodes = [node for node in root.iter() if local_name(node.tag) == "metadata" and node.get("id") == "one-bit-dither-metadata"]
    if len(metadata_nodes) != 1:
        raise ValidationFailure("Expected exactly one #one-bit-dither-metadata node")
    text = metadata_nodes[0].text or ""
    try:
        payload = json.loads(text)
    except json.JSONDecodeError as error:
        raise ValidationFailure(f"Embedded metadata is not valid JSON: {error}") from error
    if not isinstance(payload, dict):
        raise ValidationFailure("Embedded metadata must be a JSON object")
    return payload


def validate_svg(
    path: Path,
    *,
    expect_mode: str | None = None,
    expect_custom_color: str | None = None,
    expect_source_kind: str | None = None,
    expect_source_format: str | None = None,
    expect_source_frame: int | None = None,
) -> dict[str, object]:
    if not path.is_file():
        raise ValidationFailure(f"SVG not found: {path}")
    try:
        root = ET.parse(path).getroot()
    except ET.ParseError as error:
        raise ValidationFailure(f"Invalid XML: {error}") from error
    if local_name(root.tag) != "svg":
        raise ValidationFailure("Document root must be <svg>")

    missing = [attribute for attribute in REQUIRED_ROOT_ATTRIBUTES if root.get(attribute) is None]
    if missing:
        raise ValidationFailure("Missing root attributes: " + ", ".join(missing))
    if root.get("data-one-bit-dither-version") != "1":
        raise ValidationFailure("Unsupported data-one-bit-dither-version")
    if root.get("data-dither-family") != "ordered-bayer":
        raise ValidationFailure("data-dither-family must be ordered-bayer")

    mode = root.get("data-mode") or ""
    if mode not in MODES:
        raise ValidationFailure(f"Unknown mode: {mode!r}")
    if expect_mode and mode != expect_mode:
        raise ValidationFailure(f"Expected mode {expect_mode!r}, found {mode!r}")
    quality_profile = root.get("data-quality-profile") or ""
    if quality_profile not in QUALITY_PROFILES:
        raise ValidationFailure(f"Unknown quality profile: {quality_profile!r}")
    source = root.get("data-source") or ""
    if not source or Path(source).name != source or ":" in source or "\\" in source or "/" in source:
        raise ValidationFailure("data-source must contain only the source filename")
    source_kind = root.get("data-source-kind") or ""
    if source_kind not in SOURCE_KINDS:
        raise ValidationFailure(f"Unknown source kind: {source_kind!r}")
    source_format = (root.get("data-source-format") or "").upper()
    if not source_format or not re.fullmatch(r"[A-Z0-9][A-Z0-9._+-]*", source_format):
        raise ValidationFailure("data-source-format must be a compact uppercase format token")
    source_frame = parse_nonnegative_int(root, "data-source-frame")
    source_frame_count = parse_nonnegative_int(root, "data-source-frame-count")
    if source_frame_count <= 0 or source_frame >= source_frame_count:
        raise ValidationFailure("Source frame must be inside a positive frame count")
    if source_kind == "svg" and (source_format != "SVG" or source_frame != 0 or source_frame_count != 1):
        raise ValidationFailure("SVG source metadata must declare format SVG and one frame at index zero")
    if expect_source_kind and source_kind != expect_source_kind:
        raise ValidationFailure(f"Expected source kind {expect_source_kind!r}, found {source_kind!r}")
    if expect_source_format and source_format != expect_source_format.upper():
        raise ValidationFailure(f"Expected source format {expect_source_format.upper()!r}, found {source_format!r}")
    if expect_source_frame is not None and source_frame != expect_source_frame:
        raise ValidationFailure(f"Expected source frame {expect_source_frame}, found {source_frame}")

    width = parse_nonnegative_int(root, "data-render-width")
    height = parse_nonnegative_int(root, "data-render-height")
    grid_width = parse_nonnegative_int(root, "data-grid-width")
    grid_height = parse_nonnegative_int(root, "data-grid-height")
    run_count = parse_nonnegative_int(root, "data-run-count")
    region_count = parse_nonnegative_int(root, "data-region-count")
    matrix_size = parse_nonnegative_int(root, "data-matrix-size")
    cell_size = parse_nonnegative_int(root, "data-cell-size")
    if width <= 0 or height <= 0 or grid_width <= 0 or grid_height <= 0 or run_count <= 0 or cell_size <= 0:
        raise ValidationFailure("Render, grid, run, and cell counts must be positive")
    if matrix_size not in {2, 4, 8}:
        raise ValidationFailure("Matrix size must be 2, 4, or 8")
    expected_grid_width = math.ceil(width / cell_size)
    expected_grid_height = math.ceil(height / cell_size)
    if (grid_width, grid_height) != (expected_grid_width, expected_grid_height):
        raise ValidationFailure("Grid dimensions do not match render dimensions and cell size")

    view_box = root.get("viewBox", "").split()
    if view_box != ["0", "0", str(width), str(height)]:
        raise ValidationFailure("viewBox must match the declared render dimensions")
    if root.get("width") != str(width) or root.get("height") != str(height):
        raise ValidationFailure("Root width and height must match render metadata")

    forbidden = {"image", "script", "foreignObject", "iframe", "object", "embed"}
    forbidden_nodes = sorted({local_name(node.tag) for node in root.iter() if local_name(node.tag) in forbidden})
    if forbidden_nodes:
        raise ValidationFailure("Forbidden elements present: " + ", ".join(forbidden_nodes))
    for node in root.iter():
        for attribute, value in node.attrib.items():
            name = local_name(attribute)
            if name in {"href", "src"} and not value.startswith("#"):
                raise ValidationFailure(f"External or embedded reference is forbidden: {value!r}")

    titles = [node for node in root if local_name(node.tag) == "title" and (node.text or "").strip()]
    descriptions = [node for node in root if local_name(node.tag) == "desc" and (node.text or "").strip()]
    if len(titles) != 1 or len(descriptions) != 1:
        raise ValidationFailure("Expected one non-empty direct title and description")

    palette = [normalize_hex(item) for item in (root.get("data-palette") or "").split(",") if item]
    active = root.get("data-colorset")
    if active not in {"colorset1", "colorset2"} or not set(palette) <= set(colorset_tokens(active)):
        raise ValidationFailure("Dither paints must belong to the declared canonical colorset")
    if not palette or len(set(palette)) != len(palette):
        raise ValidationFailure("data-palette must contain unique hex colors")

    rects = [node for node in root.iter() if local_name(node.tag) == "rect" and "dither-run" in (node.get("class") or "").split()]
    if len(rects) != run_count:
        raise ValidationFailure(f"Declared run count {run_count} does not match {len(rects)} rects")
    roles: set[str] = set()
    used_colors: set[str] = set()
    for rect in rects:
        x = parse_positive_number(rect, "x") if rect.get("x") != "0" else 0.0
        y = parse_positive_number(rect, "y") if rect.get("y") != "0" else 0.0
        rect_width = parse_positive_number(rect, "width")
        rect_height = parse_positive_number(rect, "height")
        if x + rect_width > width + 1e-9 or y + rect_height > height + 1e-9:
            raise ValidationFailure("A dither run exceeds the declared viewBox")
        fill = normalize_hex(rect.get("fill") or "")
        if fill not in palette:
            raise ValidationFailure(f"Dither run fill {fill} is absent from data-palette")
        used_colors.add(fill)
        role = rect.get("data-role") or ""
        roles.add(role)
        if not re.fullmatch(r"\d+", rect.get("data-paint-index") or ""):
            raise ValidationFailure("Each dither run needs a nonnegative data-paint-index")

    metadata = parse_metadata(root)
    if metadata.get("schema") != "one-bit-dither-svg/v1" or metadata.get("mode") != mode:
        raise ValidationFailure("Embedded metadata schema or mode does not match the root")
    if metadata.get("qualityProfile") != quality_profile:
        raise ValidationFailure("Embedded qualityProfile does not match the root")
    if metadata.get("source") != source or metadata.get("runCount") != run_count:
        raise ValidationFailure("Embedded source or runCount does not match the root")
    if (
        metadata.get("sourceKind") != source_kind
        or metadata.get("sourceFormat") != source_format
        or metadata.get("sourceFrame") != source_frame
        or metadata.get("sourceFrameCount") != source_frame_count
    ):
        raise ValidationFailure("Embedded source kind, format, or frame metadata does not match the root")
    source_size = metadata.get("sourceSize")
    if not isinstance(source_size, dict):
        raise ValidationFailure("Embedded sourceSize must be an object")
    if not all(isinstance(source_size.get(axis), int) and source_size[axis] > 0 for axis in ("width", "height")):
        raise ValidationFailure("Embedded sourceSize must contain positive integer width and height")
    if metadata.get("palette") != palette:
        raise ValidationFailure("Embedded palette does not match data-palette")

    regions = metadata.get("regions")
    if not isinstance(regions, list):
        raise ValidationFailure("Embedded regions must be a list")
    if len(regions) != region_count:
        raise ValidationFailure("Embedded region count does not match the root")

    normalized_expected_custom = normalize_hex(expect_custom_color) if expect_custom_color else None
    if mode == "original":
        if palette != [BLACK, WHITE] or region_count != 0 or regions:
            raise ValidationFailure("Original mode must use exactly black and white with no regions")
        if roles - {"ink", "paper"}:
            raise ValidationFailure("Original mode contains unexpected paint roles")
        if root.get("data-custom-color") is not None or metadata.get("customColor") is not None:
            raise ValidationFailure("Original mode must not declare a custom color")
    elif mode == "custom":
        custom = normalize_hex(root.get("data-custom-color") or "")
        if custom == WHITE or palette != [custom, WHITE] or region_count != 0 or regions:
            raise ValidationFailure("Custom mode must use the declared custom color and white only")
        if roles - {"ink", "paper"}:
            raise ValidationFailure("Custom mode contains unexpected paint roles")
        if metadata.get("customColor") != custom:
            raise ValidationFailure("Embedded customColor does not match the root")
        if normalized_expected_custom and custom != normalized_expected_custom:
            raise ValidationFailure(f"Expected custom color {normalized_expected_custom}, found {custom}")
    else:
        if region_count <= 0 or root.get("data-custom-color") is not None or metadata.get("customColor") is not None:
            raise ValidationFailure("Regional mode needs regions and must not declare a custom color")
        if roles - {"source-color", "companion"}:
            raise ValidationFailure("Regional mode contains unexpected paint roles")
        expected_region_indices = set(range(region_count))
        described_indices: set[int] = set()
        region_contracts: dict[int, tuple[str, str]] = {}
        for raw_region in regions:
            if not isinstance(raw_region, dict):
                raise ValidationFailure("Each regional contract must be an object")
            index = raw_region.get("index")
            if not isinstance(index, int):
                raise ValidationFailure("Each regional contract needs an integer index")
            color = normalize_hex(str(raw_region.get("color", "")))
            companion = normalize_hex(str(raw_region.get("companion", "")))
            if companion != expected_companion(color):
                raise ValidationFailure(f"Region {index} uses the wrong black/white companion")
            if color not in palette or companion not in palette:
                raise ValidationFailure(f"Region {index} colors are absent from data-palette")
            described_indices.add(index)
            region_contracts[index] = (color, companion)
        if described_indices != expected_region_indices:
            raise ValidationFailure("Regional indices must be contiguous from zero")
        for rect in rects:
            region_token = rect.get("data-region-index") or ""
            if not re.fullmatch(r"\d+", region_token):
                raise ValidationFailure("Every regional run needs data-region-index")
            region_index = int(region_token)
            if region_index not in region_contracts:
                raise ValidationFailure(f"Unknown data-region-index {region_index}")
            fill = normalize_hex(rect.get("fill") or "")
            role = rect.get("data-role")
            expected_fill = region_contracts[region_index][0 if role == "source-color" else 1]
            if fill != expected_fill:
                raise ValidationFailure(f"Region {region_index} run fill does not match its role")

    return {
        "ok": True,
        "path": str(path.resolve()),
        "mode": mode,
        "qualityProfile": quality_profile,
        "sourceKind": source_kind,
        "sourceFormat": source_format,
        "sourceFrame": source_frame,
        "sourceFrameCount": source_frame_count,
        "render": {"width": width, "height": height},
        "grid": {"width": grid_width, "height": grid_height},
        "matrixSize": matrix_size,
        "cellSize": cell_size,
        "runCount": run_count,
        "regionCount": region_count,
        "palette": palette,
        "usedColors": sorted(used_colors),
        "forbiddenElementCount": 0,
    }


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("svg", type=Path)
    parser.add_argument("--expect-mode", choices=MODES)
    parser.add_argument("--expect-custom-color")
    parser.add_argument("--expect-source-kind", choices=SOURCE_KINDS)
    parser.add_argument("--expect-source-format")
    parser.add_argument("--expect-source-frame", type=int)
    parser.add_argument("--json-report", type=Path)
    args = parser.parse_args(argv)
    if args.expect_custom_color and args.expect_mode not in {None, "custom"}:
        parser.error("--expect-custom-color is valid only with custom mode")
    if args.expect_source_frame is not None and args.expect_source_frame < 0:
        parser.error("--expect-source-frame must be nonnegative")
    if args.json_report and args.json_report.suffix.lower() != ".json":
        parser.error("--json-report must end in .json")
    return args


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        report = validate_svg(
            args.svg,
            expect_mode=args.expect_mode,
            expect_custom_color=args.expect_custom_color,
            expect_source_kind=args.expect_source_kind,
            expect_source_format=args.expect_source_format,
            expect_source_frame=args.expect_source_frame,
        )
    except ValidationFailure as error:
        print(json.dumps({"ok": False, "error": str(error)}, indent=2), file=sys.stderr)
        return 1
    if args.json_report:
        args.json_report.parent.mkdir(parents=True, exist_ok=True)
        args.json_report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
