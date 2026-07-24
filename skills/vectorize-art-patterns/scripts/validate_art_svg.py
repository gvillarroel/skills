#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Validate the structural contract of an editable art-pattern SVG."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import re
import sys
from typing import Any
import xml.etree.ElementTree as ET


SVG_NS = "http://www.w3.org/2000/svg"
PATTERN_ID_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
HEX_COLOR_RE = re.compile(r"^#[0-9a-f]{6}$")
NUMBER_RE = re.compile(r"[-+]?(?:\d*\.\d+|\d+\.?)(?:[eE][-+]?\d+)?")
FORBIDDEN_TEXT = re.compile(r"\b(?:nan|inf|-inf)\b", re.IGNORECASE)
SKILL_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_COLORSET_CONTRACT = SKILL_ROOT / "assets" / "palettes" / "colorsets.json"
COLOR_ATTRIBUTES = {
    "color",
    "fill",
    "flood-color",
    "lighting-color",
    "stop-color",
    "stroke",
}


class ValidationError(RuntimeError):
    """Raised when an SVG violates the vector-art output contract."""


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_json_atomic(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)


def load_colorset(name: str) -> tuple[set[str], str]:
    try:
        payload = json.loads(DEFAULT_COLORSET_CONTRACT.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValidationError(f"Cannot read bundled colorset contract: {exc}") from exc
    colorset = payload.get("colorsets", {}).get(name)
    if payload.get("schemaVersion") != 1 or not isinstance(colorset, dict):
        raise ValidationError(f"Bundled colorset contract is missing {name}")
    allowed = colorset.get("allowed")
    if not isinstance(allowed, list) or not allowed:
        raise ValidationError(f"Bundled colorset {name} has no allowed tokens")
    normalized = {str(value).lower() for value in allowed}
    if len(normalized) != len(allowed) or any(
        not HEX_COLOR_RE.fullmatch(value) for value in normalized
    ):
        raise ValidationError(f"Bundled colorset {name} has invalid tokens")
    return normalized, sha256_path(DEFAULT_COLORSET_CONTRACT)


def parse_view_box(value: str) -> tuple[float, float, float, float]:
    numbers = [float(item) for item in NUMBER_RE.findall(value)]
    if len(numbers) != 4 or not all(math.isfinite(item) for item in numbers):
        raise ValidationError("Root viewBox must contain four finite numbers")
    if numbers[2] <= 0 or numbers[3] <= 0:
        raise ValidationError("Root viewBox width and height must be positive")
    return tuple(numbers)  # type: ignore[return-value]


def direct_child_text(root: ET.Element, name: str) -> str:
    for child in root:
        if local_name(child.tag) == name:
            return "".join(child.itertext()).strip()
    return ""


def inspect_svg(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise ValidationError(f"SVG does not exist: {path}")
    try:
        raw = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        raise ValidationError(f"Cannot read SVG as UTF-8: {exc}") from exc
    if FORBIDDEN_TEXT.search(raw):
        raise ValidationError("SVG contains NaN or Infinity")
    try:
        root = ET.fromstring(raw)
    except ET.ParseError as exc:
        raise ValidationError(f"Malformed SVG XML: {exc}") from exc
    if local_name(root.tag) != "svg":
        raise ValidationError("Root element must be <svg>")
    view_box = parse_view_box(root.get("viewBox", ""))
    title = direct_child_text(root, "title")
    description = direct_child_text(root, "desc")
    if not title or not description:
        raise ValidationError("SVG must contain nonempty direct <title> and <desc>")
    pattern_id = root.get("data-pattern-id", "")
    if not PATTERN_ID_RE.fullmatch(pattern_id):
        raise ValidationError("Root data-pattern-id must be lowercase hyphen-case")
    mode = root.get("data-mode", "")
    tile = root.get("data-tile", "")
    colorset = root.get("data-colorset", "source")
    variation_seed_text = root.get("data-variation-seed", "")
    if mode not in {"organic", "ink", "stain", "collage"}:
        raise ValidationError(f"Unsupported or missing data-mode: {mode}")
    if tile not in {"none", "repeat", "mirror"}:
        raise ValidationError(f"Unsupported or missing data-tile: {tile}")
    if colorset not in {"source", "colorset1", "colorset2"}:
        raise ValidationError(f"Unsupported data-colorset: {colorset}")
    if not re.fullmatch(r"\d{1,10}", variation_seed_text):
        raise ValidationError(
            "Root data-variation-seed must be a nonnegative integer"
        )
    variation_seed = int(variation_seed_text)
    if variation_seed > 2_147_483_647:
        raise ValidationError("Root data-variation-seed exceeds the supported range")
    source_sha256 = root.get("data-source-sha256", "")
    if not re.fullmatch(r"[0-9a-f]{64}", source_sha256):
        raise ValidationError("Root data-source-sha256 must be a lowercase SHA-256")

    counts: dict[str, int] = {}
    paths: list[ET.Element] = []
    external_references: list[str] = []
    visible_color_tokens: set[str] = set()
    invalid_color_values: set[str] = set()
    for element in root.iter():
        name = local_name(element.tag)
        counts[name] = counts.get(name, 0) + 1
        if name == "path":
            paths.append(element)
        for attribute, value in element.attrib.items():
            attribute_name = local_name(attribute)
            if attribute_name == "href" and not value.startswith("#"):
                external_references.append(value)
            if attribute_name in COLOR_ATTRIBUTES:
                normalized = value.strip().lower()
                if HEX_COLOR_RE.fullmatch(normalized):
                    visible_color_tokens.add(normalized)
                elif normalized not in {"none", "currentcolor", "inherit"} and not (
                    normalized.startswith("url(") and normalized.endswith(")")
                ):
                    invalid_color_values.add(value)
    if not paths:
        raise ValidationError("SVG must contain at least one editable <path>")
    if counts.get("image", 0):
        raise ValidationError("SVG must not wrap or embed the original raster image")
    if counts.get("script", 0) or counts.get("foreignObject", 0):
        raise ValidationError("SVG must not contain scripts or foreignObject content")
    if external_references:
        raise ValidationError(
            f"SVG contains external references: {external_references[:3]}"
        )

    command_count = 0
    path_bytes = 0
    fills: set[str] = set()
    for element in paths:
        data = element.get("d", "").strip()
        if not data or not re.match(r"^[Mm]\s*[-+\d.]", data):
            raise ValidationError("Every path must have valid path data beginning with M")
        if FORBIDDEN_TEXT.search(data):
            raise ValidationError("Path data contains NaN or Infinity")
        command_count += len(re.findall(r"[A-Za-z]", data))
        path_bytes += len(data.encode("utf-8"))
        fill = element.get("fill")
        if fill:
            fills.add(fill.lower())

    metadata_text = direct_child_text(root, "metadata")
    if not metadata_text:
        raise ValidationError("SVG must contain JSON provenance in <metadata>")
    try:
        metadata = json.loads(metadata_text)
    except json.JSONDecodeError as exc:
        raise ValidationError(f"SVG metadata is not valid JSON: {exc}") from exc
    if metadata.get("pattern_id") != pattern_id:
        raise ValidationError("Metadata pattern_id does not match root data-pattern-id")
    if metadata.get("pipeline", {}).get("mode") != mode:
        raise ValidationError("Metadata mode does not match root data-mode")
    if metadata.get("pipeline", {}).get("tile") != tile:
        raise ValidationError("Metadata tile does not match root data-tile")
    if metadata.get("pipeline", {}).get("colorset", "source") != colorset:
        raise ValidationError("Metadata colorset does not match root data-colorset")
    variation = metadata.get("pipeline", {}).get("variation")
    if not isinstance(variation, dict) or variation.get("seed") != variation_seed:
        raise ValidationError(
            "Metadata variation seed does not match root data-variation-seed"
        )
    composition_sha256 = str(variation.get("composition_sha256", ""))
    if not re.fullmatch(r"[0-9a-f]{64}", composition_sha256):
        raise ValidationError("Metadata composition SHA-256 is missing or invalid")
    if metadata.get("source", {}).get("input_sha256") != source_sha256:
        raise ValidationError("Metadata source SHA-256 does not match the root")
    palette_contract_sha256 = str(
        metadata.get("pipeline", {}).get("palette_contract_sha256", "")
    )
    unexpected_color_tokens: list[str] = []
    if colorset != "source":
        if invalid_color_values:
            raise ValidationError(
                f"Colorset SVG contains unsupported color values: "
                f"{sorted(invalid_color_values)}"
            )
        allowed, expected_contract_sha256 = load_colorset(colorset)
        unexpected_color_tokens = sorted(visible_color_tokens - allowed)
        if unexpected_color_tokens:
            raise ValidationError(
                f"SVG contains colors outside {colorset}: "
                f"{unexpected_color_tokens}"
            )
        if palette_contract_sha256 != expected_contract_sha256:
            raise ValidationError(
                "SVG palette contract SHA-256 does not match the bundled contract"
            )

    return {
        "schema_version": 1,
        "ok": True,
        "svg": str(path),
        "sha256": sha256_path(path),
        "pattern_id": pattern_id,
        "mode": mode,
        "tile": tile,
        "colorset": colorset,
        "variation_seed": variation_seed,
        "composition_sha256": composition_sha256,
        "palette_contract_sha256": palette_contract_sha256,
        "visible_color_tokens": sorted(visible_color_tokens),
        "unexpected_color_tokens": unexpected_color_tokens,
        "view_box": list(view_box),
        "path_count": len(paths),
        "path_command_count": command_count,
        "path_data_bytes": path_bytes,
        "fill_count": len(fills),
        "pattern_element_count": counts.get("pattern", 0),
        "use_element_count": counts.get("use", 0),
        "image_element_count": counts.get("image", 0),
        "script_element_count": counts.get("script", 0),
        "external_reference_count": len(external_references),
        "source_sha256": source_sha256,
        "rights_basis": metadata.get("source", {}).get("basis", ""),
        "license": metadata.get("source", {}).get("license", ""),
    }


def validate_against_args(
    result: dict[str, Any], args: argparse.Namespace
) -> dict[str, Any]:
    if args.expected_pattern_id and result["pattern_id"] != args.expected_pattern_id:
        raise ValidationError(
            f"Expected pattern ID {args.expected_pattern_id}, "
            f"found {result['pattern_id']}"
        )
    if args.expected_mode and result["mode"] != args.expected_mode:
        raise ValidationError(
            f"Expected mode {args.expected_mode}, found {result['mode']}"
        )
    if args.expected_tile and result["tile"] != args.expected_tile:
        raise ValidationError(
            f"Expected tile {args.expected_tile}, found {result['tile']}"
        )
    if args.expected_colorset and result["colorset"] != args.expected_colorset:
        raise ValidationError(
            f"Expected colorset {args.expected_colorset}, "
            f"found {result['colorset']}"
        )
    if (
        args.expected_variation_seed is not None
        and result["variation_seed"] != args.expected_variation_seed
    ):
        raise ValidationError(
            f"Expected variation seed {args.expected_variation_seed}, "
            f"found {result['variation_seed']}"
        )
    if args.require_pattern and result["pattern_element_count"] < 1:
        raise ValidationError("A tile pattern was required but no <pattern> exists")
    if result["path_count"] < args.min_paths:
        raise ValidationError(
            f"Expected at least {args.min_paths} paths, found {result['path_count']}"
        )
    if args.max_paths is not None and result["path_count"] > args.max_paths:
        raise ValidationError(
            f"Expected at most {args.max_paths} paths, found {result['path_count']}"
        )

    if args.report:
        try:
            report = json.loads(args.report.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise ValidationError(f"Cannot read vectorization report: {exc}") from exc
        comparisons = {
            "output_sha256": result["sha256"],
            "pattern_id": result["pattern_id"],
            "mode": result["mode"],
            "tile": result["tile"],
            "colorset": result["colorset"],
        }
        for key, expected in comparisons.items():
            if report.get(key) != expected:
                raise ValidationError(
                    f"Report field {key} does not match the SVG: "
                    f"{report.get(key)!r} != {expected!r}"
                )
        if report.get("path_count") != result["path_count"]:
            raise ValidationError("Report path_count does not match the SVG")
        result["report"] = str(args.report)
    return result


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Validate an editable SVG produced by vectorize-art-patterns."
    )
    parser.add_argument("svg", type=Path)
    parser.add_argument("--report", type=Path)
    parser.add_argument("--expected-pattern-id")
    parser.add_argument(
        "--expected-mode", choices=("organic", "ink", "stain", "collage")
    )
    parser.add_argument(
        "--expected-tile", choices=("none", "repeat", "mirror")
    )
    parser.add_argument(
        "--expected-colorset",
        choices=("source", "colorset1", "colorset2"),
    )
    parser.add_argument("--expected-variation-seed", type=int)
    parser.add_argument("--require-pattern", action="store_true")
    parser.add_argument("--min-paths", type=int, default=1)
    parser.add_argument("--max-paths", type=int)
    parser.add_argument(
        "--output-report",
        type=Path,
        help="Optionally write this validation result as deterministic JSON.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    result = validate_against_args(inspect_svg(args.svg.resolve()), args)
    if args.output_report:
        write_json_atomic(args.output_report.resolve(), result)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ValidationError as exc:
        print(f"[vectorize-art-patterns] ERROR: {exc}", file=sys.stderr)
        raise SystemExit(2)
