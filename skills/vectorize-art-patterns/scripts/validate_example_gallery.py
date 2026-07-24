#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Validate the published 300-pattern vectorize-art-patterns gallery."""

from __future__ import annotations

import argparse
from collections import Counter
import hashlib
from html.parser import HTMLParser
import importlib.util
import json
from pathlib import Path
import re
import sys
from typing import Any
import xml.etree.ElementTree as ET


SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_ROOT = SCRIPT_DIR.parent
DEFAULT_EXAMPLE_ROOT = (
    SKILL_ROOT / "assets" / "examples" / "vectorize-art-patterns"
)
EXPECTED_PATTERN_COUNT = 300
EXPECTED_FAMILY_COUNT = 15
ID_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
SHA_RE = re.compile(r"^[0-9a-f]{64}$")
HEX_RE = re.compile(r"#[0-9a-fA-F]{6}")
sys.dont_write_bytecode = True


class GalleryValidationError(RuntimeError):
    """Raised when the published acceptance gallery violates its contract."""


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise GalleryValidationError(f"Cannot load module: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


validator = load_module("validate_art_svg", SCRIPT_DIR / "validate_art_svg.py")


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sha256_json(payload: Any) -> str:
    encoded = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise GalleryValidationError(f"Cannot read JSON {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise GalleryValidationError(f"Expected a JSON object: {path}")
    return payload


def resolve_inside(root: Path, relative: Any, field: str) -> Path:
    if not isinstance(relative, str) or not relative:
        raise GalleryValidationError(f"Manifest field {field} must be a path")
    candidate = (root / relative).resolve()
    try:
        candidate.relative_to(root.resolve())
    except ValueError as exc:
        raise GalleryValidationError(
            f"Manifest field {field} escapes the gallery root: {relative}"
        ) from exc
    if not candidate.is_file():
        raise GalleryValidationError(f"Manifest file is missing: {relative}")
    return candidate


def svg_geometry_record(svg: Path) -> dict[str, Any]:
    try:
        root = ET.fromstring(svg.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, ET.ParseError) as exc:
        raise GalleryValidationError(f"Cannot inspect SVG {svg}: {exc}") from exc
    paths = [
        element.get("d", "")
        for element in root.iter()
        if local_name(element.tag) == "path"
    ]
    metadata_element = next(
        (
            element
            for element in list(root)
            if local_name(element.tag) == "metadata"
        ),
        None,
    )
    try:
        metadata = json.loads(
            "".join(metadata_element.itertext()) if metadata_element is not None else ""
        )
    except json.JSONDecodeError as exc:
        raise GalleryValidationError(f"Invalid SVG metadata in {svg}: {exc}") from exc
    return {
        "geometrySha256": sha256_json(
            {"viewBox": root.get("viewBox", ""), "paths": paths}
        ),
        "pathSignatures": [
            hashlib.sha256(path.encode("utf-8")).hexdigest() for path in paths
        ],
        "pipeline": metadata.get("pipeline", {}),
    }


class GalleryParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.meta: dict[str, str] = {}
        self.body: dict[str, str | None] = {}
        self.id_counts: dict[str, int] = {}
        self.colorset_filters: set[str] = set()
        self.local_assets: set[str] = set()
        self.tag_counts: Counter[str] = Counter()

    def handle_starttag(
        self, tag: str, attrs: list[tuple[str, str | None]]
    ) -> None:
        self.tag_counts[tag] += 1
        values = dict(attrs)
        element_id = values.get("id")
        if element_id:
            self.id_counts[element_id] = self.id_counts.get(element_id, 0) + 1
        if tag == "meta" and values.get("name") and values.get("content"):
            self.meta[str(values["name"])] = str(values["content"])
        if tag == "body":
            self.body = values
        if tag == "button" and values.get("data-colorset-filter"):
            self.colorset_filters.add(str(values["data-colorset-filter"]))
        if tag == "link" and values.get("rel") == "stylesheet" and values.get("href"):
            self.local_assets.add(str(values["href"]))
        if tag == "script" and values.get("src"):
            self.local_assets.add(str(values["src"]))


def validate_page(
    example_root: Path,
    manifest: dict[str, Any],
) -> dict[str, Any]:
    index_path = example_root / "index.html"
    css_path = example_root / "gallery.css"
    js_path = example_root / "gallery.js"
    parser = GalleryParser()
    parser.feed(index_path.read_text(encoding="utf-8"))
    if parser.meta.get("example-id") != "vectorize-art-patterns":
        raise GalleryValidationError("Page example-id metadata is incorrect")
    if parser.meta.get("pattern-id") != "vectorize-art-patterns":
        raise GalleryValidationError("Page pattern-id metadata is incorrect")
    if parser.meta.get("pattern-page") != "true":
        raise GalleryValidationError("Page pattern-page metadata is missing")
    if parser.body.get("data-colorset") != "all":
        raise GalleryValidationError("Page default colorset filter must be all")
    if parser.colorset_filters != {"all", "colorset1", "colorset2"}:
        raise GalleryValidationError("Page colorset filters are incomplete")
    if parser.local_assets != {"gallery.css", "gallery.js"}:
        raise GalleryValidationError("Page local CSS/JS asset contract is incorrect")
    duplicates = sorted(
        element_id for element_id, count in parser.id_counts.items() if count != 1
    )
    if duplicates:
        raise GalleryValidationError(f"Duplicate page element IDs: {duplicates}")
    required_ids = {
        "filter-heading",
        "mode-filter",
        "family-filter",
        "pattern-search",
        "reset-filters",
        "visible-status",
        "pattern-gallery",
        "previous-page",
        "next-page",
        "page-number",
        "page-total",
        "pattern-card-template",
    }
    missing_ids = sorted(required_ids - set(parser.id_counts))
    if missing_ids:
        raise GalleryValidationError(f"Page controls are missing: {missing_ids}")
    if parser.tag_counts["template"] != 1:
        raise GalleryValidationError("Page must contain exactly one card template")

    union_allowed: set[str] = set()
    for name in ("colorset1", "colorset2"):
        colorset = manifest.get("colorsets", {}).get(name)
        if not isinstance(colorset, dict) or not isinstance(
            colorset.get("allowed"), list
        ):
            raise GalleryValidationError(f"Manifest is missing {name}")
        union_allowed.update(str(value).lower() for value in colorset["allowed"])
    source_text = "\n".join(
        path.read_text(encoding="utf-8")
        for path in (index_path, css_path, js_path)
    )
    unexpected_page_colors = sorted(
        {token.lower() for token in HEX_RE.findall(source_text)} - union_allowed
    )
    if unexpected_page_colors:
        raise GalleryValidationError(
            f"Gallery page uses colors outside both contracts: {unexpected_page_colors}"
        )
    js_text = js_path.read_text(encoding="utf-8")
    for required_snippet in (
        "const PAGE_SIZE = 24",
        'fetch("manifest.json")',
        "manifest.patternCount !== 300",
        "manifest.uniqueGeometryCount !== 300",
        "pathDataReuseAllowed !== false",
        "item.geometrySha256",
        "item.compositionSha256",
        "location.hash",
    ):
        if required_snippet not in js_text:
            raise GalleryValidationError(
                f"Gallery runtime contract is missing: {required_snippet}"
            )
    return {
        "page_size": 24,
        "required_control_count": len(required_ids),
        "page_color_token_count": len(
            {token.lower() for token in HEX_RE.findall(source_text)}
        ),
    }


def compare_parameters(
    pattern_id: str,
    entry: dict[str, Any],
    report: dict[str, Any],
    pipeline: dict[str, Any],
) -> None:
    parameters = entry.get("parameters")
    report_parameters = report.get("parameters")
    if not isinstance(parameters, dict) or not isinstance(report_parameters, dict):
        raise GalleryValidationError(f"Missing parameters for {pattern_id}")
    direct_pairs = {
        "colors": "colors",
        "smoothing": "smoothing",
        "detail": "detail",
        "minArea": "min_area",
        "maxDimension": "max_dimension",
        "outline": "outline",
        "paletteMethod": "palette_method",
    }
    for manifest_key, pipeline_key in direct_pairs.items():
        expected = parameters.get(manifest_key)
        if (
            report_parameters.get(pipeline_key) != expected
            or pipeline.get(pipeline_key) != expected
        ):
            raise GalleryValidationError(
                f"Parameter {manifest_key} mismatch for {pattern_id}"
            )
    variation = report_parameters.get("variation")
    pipeline_variation = pipeline.get("variation")
    if not isinstance(variation, dict) or not isinstance(pipeline_variation, dict):
        raise GalleryValidationError(f"Variation metadata missing for {pattern_id}")
    variation_pairs = {
        "cropScale": "crop_scale",
        "cropX": "crop_x",
        "cropY": "crop_y",
        "rotation": "rotation",
        "flowStrength": "flow_strength",
        "flowFrequency": "flow_frequency",
    }
    for manifest_key, variation_key in variation_pairs.items():
        expected = parameters.get(manifest_key)
        if (
            variation.get(variation_key) != expected
            or pipeline_variation.get(variation_key) != expected
        ):
            raise GalleryValidationError(
                f"Variation {manifest_key} mismatch for {pattern_id}"
            )


def validate_gallery(example_root: Path) -> dict[str, Any]:
    manifest_path = example_root / "manifest.json"
    manifest = load_json(manifest_path)
    if manifest.get("schemaVersion") != 2:
        raise GalleryValidationError("Manifest schemaVersion must be 2")
    if manifest.get("pageId") != "vectorize-art-patterns":
        raise GalleryValidationError("Manifest pageId is incorrect")
    if manifest.get("namespace") != "vectorize":
        raise GalleryValidationError("Manifest namespace must be vectorize")
    patterns = manifest.get("patterns")
    families = manifest.get("families")
    if not isinstance(patterns, list) or len(patterns) != EXPECTED_PATTERN_COUNT:
        raise GalleryValidationError("Manifest must contain exactly 300 patterns")
    if not isinstance(families, list) or len(families) != EXPECTED_FAMILY_COUNT:
        raise GalleryValidationError("Manifest must contain exactly 15 families")
    if (
        manifest.get("patternCount") != EXPECTED_PATTERN_COUNT
        or manifest.get("familyCount") != EXPECTED_FAMILY_COUNT
    ):
        raise GalleryValidationError("Manifest pattern/family counts are incorrect")
    expected_contract_sha = sha256_path(
        SKILL_ROOT / "assets" / "palettes" / "colorsets.json"
    )
    if manifest.get("colorsetContractSha256") != expected_contract_sha:
        raise GalleryValidationError("Manifest colorset contract hash is stale")
    expected_uniqueness = {
        "canonicalPatternCount": 300,
        "completeGeometryReuseAllowed": False,
        "pathDataReuseAllowed": False,
        "compositionReuseAllowed": False,
        "svgUseElementsAllowed": False,
        "tileMode": "none",
    }
    if manifest.get("uniquenessContract") != expected_uniqueness:
        raise GalleryValidationError("Manifest uniqueness contract is incomplete")
    page_result = validate_page(example_root, manifest)

    family_by_id: dict[str, dict[str, Any]] = {}
    for family in families:
        if not isinstance(family, dict):
            raise GalleryValidationError("Every family summary must be an object")
        family_id = family.get("id")
        if (
            not isinstance(family_id, str)
            or not ID_RE.fullmatch(family_id)
            or family_id in family_by_id
        ):
            raise GalleryValidationError(f"Invalid family ID: {family_id!r}")
        if family.get("patternCount") != 20:
            raise GalleryValidationError(f"Family {family_id} must contain 20 patterns")
        if family.get("colorsetCounts") != {
            "colorset1": 10,
            "colorset2": 10,
        }:
            raise GalleryValidationError(
                f"Family {family_id} colorset counts are incorrect"
            )
        family_by_id[family_id] = family

    ids: set[str] = set()
    example_ids: set[str] = set()
    ordinals: set[int] = set()
    output_hashes: set[str] = set()
    geometry_owners: dict[str, str] = {}
    path_owners: dict[str, str] = {}
    composition_owners: dict[str, str] = {}
    variation_seed_owners: dict[int, str] = {}
    expected_svgs: set[str] = set()
    expected_reports: set[str] = set()
    colorset_counts: Counter[str] = Counter()
    mode_counts: Counter[str] = Counter()
    source_counts: Counter[str] = Counter()
    family_counts: Counter[str] = Counter()
    loaded_tokens: set[str] = set()
    total_svg_bytes = 0

    for item in patterns:
        if not isinstance(item, dict):
            raise GalleryValidationError("Every manifest pattern must be an object")
        pattern_id = item.get("id")
        if (
            not isinstance(pattern_id, str)
            or not ID_RE.fullmatch(pattern_id)
            or not pattern_id.startswith("vectorize-")
            or len(pattern_id) > 64
        ):
            raise GalleryValidationError(f"Invalid pattern ID: {pattern_id!r}")
        if pattern_id in ids:
            raise GalleryValidationError(f"Duplicate manifest ID: {pattern_id}")
        ids.add(pattern_id)
        example_id = item.get("exampleId")
        if (
            not isinstance(example_id, str)
            or not ID_RE.fullmatch(example_id)
            or example_id in example_ids
        ):
            raise GalleryValidationError(
                f"Invalid or reused exampleId for {pattern_id}"
            )
        example_ids.add(example_id)
        ordinal = item.get("ordinal")
        if not isinstance(ordinal, int) or ordinal in ordinals:
            raise GalleryValidationError(f"Invalid ordinal for {pattern_id}")
        ordinals.add(ordinal)

        colorset = item.get("colorset")
        variant = item.get("variant")
        expected_variant = {
            "colorset1": "cs1",
            "colorset2": "cs2",
        }.get(colorset)
        if expected_variant is None or variant != expected_variant:
            raise GalleryValidationError(
                f"Colorset/variant mismatch for {pattern_id}"
            )
        if not pattern_id.endswith(f"-{variant}"):
            raise GalleryValidationError(
                f"Pattern ID variant suffix mismatch: {pattern_id}"
            )
        family_id = item.get("familyId")
        family = family_by_id.get(str(family_id))
        if family is None:
            raise GalleryValidationError(f"Unknown family for {pattern_id}")
        if (
            item.get("familyTitle") != family.get("title")
            or item.get("mode") != family.get("mode")
            or item.get("sourceId") != family.get("sourceId")
        ):
            raise GalleryValidationError(
                f"Family metadata mismatch for {pattern_id}"
            )
        if item.get("tile") != "none":
            raise GalleryValidationError(f"Collection member is tiled: {pattern_id}")

        svg = resolve_inside(example_root, item.get("svg"), "svg")
        report_path = resolve_inside(example_root, item.get("report"), "report")
        expected_svgs.add(svg.name)
        expected_reports.add(report_path.name)
        svg_hash = sha256_path(svg)
        if item.get("sha256") != svg_hash or svg_hash in output_hashes:
            raise GalleryValidationError(f"SVG hash mismatch/reuse: {pattern_id}")
        output_hashes.add(svg_hash)
        if item.get("bytes") != svg.stat().st_size:
            raise GalleryValidationError(f"SVG byte count mismatch: {pattern_id}")
        total_svg_bytes += svg.stat().st_size

        geometry = svg_geometry_record(svg)
        geometry_digest = item.get("geometrySha256")
        if (
            not isinstance(geometry_digest, str)
            or not SHA_RE.fullmatch(geometry_digest)
            or geometry_digest != geometry["geometrySha256"]
        ):
            raise GalleryValidationError(f"Geometry hash mismatch: {pattern_id}")
        previous_geometry = geometry_owners.get(geometry_digest)
        if previous_geometry:
            raise GalleryValidationError(
                f"Complete geometry reused by {previous_geometry} and {pattern_id}"
            )
        geometry_owners[geometry_digest] = pattern_id
        path_signatures = item.get("pathSignatures")
        if (
            not isinstance(path_signatures, list)
            or not path_signatures
            or path_signatures != geometry["pathSignatures"]
        ):
            raise GalleryValidationError(f"Path signatures mismatch: {pattern_id}")
        for signature in path_signatures:
            if not isinstance(signature, str) or not SHA_RE.fullmatch(signature):
                raise GalleryValidationError(
                    f"Invalid path signature for {pattern_id}"
                )
            previous_path = path_owners.get(signature)
            if previous_path:
                raise GalleryValidationError(
                    f"Path data reused by {previous_path} and {pattern_id}"
                )
            path_owners[signature] = pattern_id

        composition_digest = item.get("compositionSha256")
        if (
            not isinstance(composition_digest, str)
            or not SHA_RE.fullmatch(composition_digest)
        ):
            raise GalleryValidationError(
                f"Invalid composition hash for {pattern_id}"
            )
        previous_composition = composition_owners.get(composition_digest)
        if previous_composition:
            raise GalleryValidationError(
                f"Composition reused by {previous_composition} and {pattern_id}"
            )
        composition_owners[composition_digest] = pattern_id
        variation_seed = item.get("variationSeed")
        if not isinstance(variation_seed, int) or variation_seed < 0:
            raise GalleryValidationError(f"Invalid variation seed: {pattern_id}")
        previous_seed = variation_seed_owners.get(variation_seed)
        if previous_seed:
            raise GalleryValidationError(
                f"Variation seed reused by {previous_seed} and {pattern_id}"
            )
        variation_seed_owners[variation_seed] = pattern_id

        report = load_json(report_path)
        inspection = validator.inspect_svg(svg)
        if (
            inspection["pattern_id"] != pattern_id
            or inspection["colorset"] != colorset
            or inspection["tile"] != "none"
            or inspection["variation_seed"] != variation_seed
            or inspection["composition_sha256"] != composition_digest
            or inspection["pattern_element_count"] != 0
            or inspection["use_element_count"] != 0
            or inspection["unexpected_color_tokens"]
        ):
            raise GalleryValidationError(
                f"SVG uniqueness/structure validation failed: {pattern_id}"
            )
        comparisons = {
            "output_sha256": svg_hash,
            "pattern_id": pattern_id,
            "mode": item["mode"],
            "tile": "none",
            "colorset": colorset,
            "composition_sha256": composition_digest,
            "path_count": item["pathCount"],
            "contour_count": item["contourCount"],
            "point_count": item["pointCount"],
            "palette": item["palette"],
        }
        for key, expected in comparisons.items():
            if report.get(key) != expected:
                raise GalleryValidationError(
                    f"Report field {key} mismatch for {pattern_id}"
                )
        required_anchor = {
            "colorset1": "#9e1b32",
            "colorset2": "#007298",
        }[str(colorset)]
        if required_anchor not in {
            str(color).lower() for color in item.get("palette", [])
        }:
            raise GalleryValidationError(
                f"Required {colorset} anchor is not visible in {pattern_id}"
            )
        if report.get("variation", {}).get("seed") != variation_seed:
            raise GalleryValidationError(
                f"Report variation seed mismatch for {pattern_id}"
            )
        compare_parameters(pattern_id, item, report, geometry["pipeline"])
        if item.get("visibleColorTokens") != inspection["visible_color_tokens"]:
            raise GalleryValidationError(
                f"Visible color tokens mismatch for {pattern_id}"
            )
        loaded_tokens.update(inspection["visible_color_tokens"])
        colorset_counts[str(colorset)] += 1
        mode_counts[str(item["mode"])] += 1
        source_counts[str(item["sourceId"])] += 1
        family_counts[str(family_id)] += 1

    if ordinals != set(range(1, EXPECTED_PATTERN_COUNT + 1)):
        raise GalleryValidationError("Pattern ordinals must be exactly 1 through 300")
    if colorset_counts != Counter({"colorset1": 150, "colorset2": 150}):
        raise GalleryValidationError(f"Colorset counts are wrong: {colorset_counts}")
    if mode_counts != Counter(
        {"organic": 80, "stain": 80, "ink": 60, "collage": 80}
    ):
        raise GalleryValidationError(f"Mode counts are wrong: {mode_counts}")
    if set(family_counts) != set(family_by_id) or any(
        count != 20 for count in family_counts.values()
    ):
        raise GalleryValidationError(f"Family counts are wrong: {family_counts}")
    if any(
        family.get("patternCount") != family_counts[family_id]
        for family_id, family in family_by_id.items()
    ):
        raise GalleryValidationError("Family summaries do not match the patterns")

    aggregate_checks = {
        "colorsetCounts": dict(sorted(colorset_counts.items())),
        "modeCounts": dict(sorted(mode_counts.items())),
        "sourceCounts": dict(sorted(source_counts.items())),
        "uniqueGeometryCount": len(geometry_owners),
        "uniquePathCount": len(path_owners),
        "uniqueCompositionCount": len(composition_owners),
    }
    for key, expected in aggregate_checks.items():
        if manifest.get(key) != expected:
            raise GalleryValidationError(f"Manifest aggregate {key} is stale")
    fingerprint = sha256_json(
        [
            {
                "id": item["id"],
                "geometrySha256": item["geometrySha256"],
                "pathSignatures": item["pathSignatures"],
                "compositionSha256": item["compositionSha256"],
            }
            for item in patterns
        ]
    )
    if manifest.get("catalogFingerprint") != fingerprint:
        raise GalleryValidationError("Manifest catalog fingerprint is stale")

    actual_svgs = {
        path.name for path in (example_root / "svgs").glob("*.svg")
    }
    actual_reports = {
        path.name for path in (example_root / "reports").glob("*.json")
    }
    if actual_svgs != expected_svgs or actual_reports != expected_reports:
        raise GalleryValidationError("Published SVG/report inventory has stale files")

    return {
        "schema_version": 2,
        "ok": True,
        "page_id": "vectorize-art-patterns",
        "family_count": len(family_by_id),
        "pattern_count": len(ids),
        "colorset_counts": dict(sorted(colorset_counts.items())),
        "mode_counts": dict(sorted(mode_counts.items())),
        "source_counts": dict(sorted(source_counts.items())),
        "unique_output_hash_count": len(output_hashes),
        "unique_geometry_count": len(geometry_owners),
        "unique_path_count": len(path_owners),
        "unique_composition_count": len(composition_owners),
        "unique_variation_seed_count": len(variation_seed_owners),
        "visible_color_token_count": len(loaded_tokens),
        "total_svg_bytes": total_svg_bytes,
        "page_size": page_result["page_size"],
        "page_control_count": page_result["required_control_count"],
        "catalog_fingerprint": fingerprint,
        "manifest_sha256": sha256_path(manifest_path),
        "colorset_contract_sha256": expected_contract_sha,
    }


def write_json_atomic(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Validate the 300-pattern vectorize-art-patterns gallery."
    )
    parser.add_argument(
        "--example-root",
        type=Path,
        default=DEFAULT_EXAMPLE_ROOT,
    )
    parser.add_argument("--output-report", type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    result = validate_gallery(args.example_root.resolve())
    if args.output_report:
        write_json_atomic(args.output_report.resolve(), result)
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except GalleryValidationError as exc:
        print(f"[vectorize-art-patterns] ERROR: {exc}", file=sys.stderr)
        raise SystemExit(2)
