#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "numpy>=2.0",
#   "opencv-python-headless>=4.10",
#   "pillow>=11.0",
# ]
# ///
"""Build the deterministic 300-pattern Pages acceptance gallery."""

from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import importlib.util
import json
import os
from pathlib import Path
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
sys.dont_write_bytecode = True


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load module: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


vectorizer = load_module("vectorize_art", SCRIPT_DIR / "vectorize_art.py")
validator = load_module("validate_art_svg", SCRIPT_DIR / "validate_art_svg.py")


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


def relative_path(path: Path) -> Path:
    return Path(os.path.relpath(path.resolve(), Path.cwd().resolve()))


def svg_geometry_record(svg: Path) -> dict[str, Any]:
    root = ET.fromstring(svg.read_text(encoding="utf-8"))
    paths = [
        element.get("d", "")
        for element in root.iter()
        if element.tag.rsplit("}", 1)[-1] == "path"
    ]
    if not paths or any(not path for path in paths):
        raise RuntimeError(f"SVG has missing path data: {svg}")
    return {
        "geometrySha256": sha256_json(
            {"viewBox": root.get("viewBox", ""), "paths": paths}
        ),
        "pathSignatures": [
            hashlib.sha256(path.encode("utf-8")).hexdigest() for path in paths
        ],
    }


def normalize_report_paths(
    report: dict[str, Any],
    *,
    input_path: Path,
    output_path: Path,
) -> dict[str, Any]:
    normalized = dict(report)
    normalized["input"] = relative_path(input_path).as_posix()
    normalized["output"] = relative_path(output_path).as_posix()
    return normalized


def load_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"Cannot read JSON {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise RuntimeError(f"Expected a JSON object: {path}")
    return payload


def halton(index: int, base: int) -> float:
    if index < 1 or base < 2:
        raise RuntimeError("Halton index/base is invalid")
    result = 0.0
    fraction = 1.0
    value = index
    while value:
        fraction /= base
        result += fraction * (value % base)
        value //= base
    return result


def ranged(
    family: dict[str, Any],
    key: str,
    sequence_index: int,
    base: int,
    *,
    digits: int,
) -> float:
    values = family.get(key)
    if (
        not isinstance(values, list)
        or len(values) != 2
        or not all(isinstance(value, (int, float)) for value in values)
    ):
        raise RuntimeError(f"Family {family.get('id')} has invalid {key}")
    low, high = float(values[0]), float(values[1])
    if low > high:
        raise RuntimeError(f"Family {family.get('id')} reverses {key}")
    return round(low + (high - low) * halton(sequence_index, base), digits)


def integer_range(
    family: dict[str, Any],
    key: str,
    sequence_index: int,
    base: int,
) -> int:
    return int(round(ranged(family, key, sequence_index, base, digits=6)))


def validate_spec(spec: dict[str, Any]) -> list[dict[str, Any]]:
    if spec.get("schemaVersion") != 2:
        raise RuntimeError("Gallery spec schemaVersion must be 2")
    if spec.get("pageId") != "vectorize-art-patterns":
        raise RuntimeError("Gallery spec pageId is incorrect")
    families = spec.get("families")
    if not isinstance(families, list) or len(families) != EXPECTED_FAMILY_COUNT:
        raise RuntimeError(
            f"Gallery spec must contain {EXPECTED_FAMILY_COUNT} families"
        )
    if spec.get("targetPatternCount") != EXPECTED_PATTERN_COUNT:
        raise RuntimeError("Gallery spec targetPatternCount must be 300")
    if spec.get("patternsPerFamily") != 20:
        raise RuntimeError("Gallery spec patternsPerFamily must be 20")
    family_ids: set[str] = set()
    total = 0
    for family in families:
        if not isinstance(family, dict):
            raise RuntimeError("Every gallery family must be an object")
        family_id = family.get("id")
        if not isinstance(family_id, str) or not vectorizer.PATTERN_ID_RE.fullmatch(
            family_id
        ):
            raise RuntimeError(f"Invalid gallery family ID: {family_id!r}")
        if family_id in family_ids:
            raise RuntimeError(f"Duplicate gallery family ID: {family_id}")
        family_ids.add(family_id)
        if family.get("count") != 20:
            raise RuntimeError(f"Family {family_id} must contain 20 patterns")
        if family.get("mode") not in vectorizer.MODE_DEFAULTS:
            raise RuntimeError(f"Family {family_id} has an invalid mode")
        if not isinstance(family.get("paletteMethods"), list) or not family[
            "paletteMethods"
        ]:
            raise RuntimeError(f"Family {family_id} has no palette methods")
        if not isinstance(family.get("minPaths"), int) or family["minPaths"] < 1:
            raise RuntimeError(f"Family {family_id} has invalid minPaths")
        total += int(family["count"])
    if total != EXPECTED_PATTERN_COUNT:
        raise RuntimeError(f"Gallery spec expands to {total}, expected 300")
    return families


def recipe_for(
    family: dict[str, Any],
    *,
    family_index: int,
    item_index: int,
    ordinal: int,
) -> dict[str, Any]:
    sequence_index = ordinal + 1
    colorset = "colorset1" if ordinal % 2 == 0 else "colorset2"
    variant = "cs1" if colorset == "colorset1" else "cs2"
    item_number = item_index + 1
    family_id = str(family["id"])
    pattern_id = f"vectorize-{family_id}-{item_number:02d}-{variant}"
    seed = (family_index + 1) * 100_003 + item_number * 7_919
    palette_methods = [str(value) for value in family["paletteMethods"]]
    return {
        "id": pattern_id,
        "exampleId": f"{family_id}-{item_number:02d}",
        "ordinal": ordinal + 1,
        "familyId": family_id,
        "familyTitle": str(family["title"]),
        "title": f"{family['title']} {item_number:02d}",
        "description": str(family["description"]),
        "sourceId": str(family["sourceId"]),
        "mode": str(family["mode"]),
        "tile": "none",
        "colorset": colorset,
        "variant": variant,
        "variationSeed": seed,
        "colors": integer_range(family, "colors", sequence_index, 3),
        "smoothing": ranged(
            family, "smoothing", sequence_index, 5, digits=3
        ),
        "detail": ranged(family, "detail", sequence_index, 7, digits=3),
        "minArea": ranged(
            family, "minArea", sequence_index, 11, digits=2
        ),
        "maxDimension": integer_range(
            family, "maxDimension", sequence_index, 13
        ),
        "cropScale": ranged(
            family, "cropScale", sequence_index, 17, digits=4
        ),
        "cropX": round(halton(sequence_index + family_index * 23, 19), 4),
        "cropY": round(halton(sequence_index + family_index * 29, 23), 4),
        "rotation": ranged(
            family, "rotation", sequence_index, 29, digits=3
        ),
        "flowStrength": ranged(
            family, "flowStrength", sequence_index, 31, digits=3
        ),
        "flowFrequency": ranged(
            family, "flowFrequency", sequence_index, 37, digits=3
        ),
        "outline": ranged(family, "outline", sequence_index, 41, digits=3),
        "paletteMethod": palette_methods[
            (item_index + family_index) % len(palette_methods)
        ],
        "minPaths": int(family["minPaths"]),
    }


def remove_stale(directory: Path, expected: set[str], suffix: str) -> list[str]:
    resolved = directory.resolve()
    removed: list[str] = []
    for path in directory.glob(f"*{suffix}"):
        if path.parent.resolve() != resolved:
            raise RuntimeError(f"Refusing to remove a file outside {directory}")
        if path.name not in expected:
            path.unlink()
            removed.append(path.name)
    return sorted(removed)


def build_gallery(example_root: Path) -> dict[str, Any]:
    spec = load_json(example_root / "gallery-spec.json")
    families = validate_spec(spec)
    source_manifest_path = SKILL_ROOT / "assets" / "base-images" / "manifest.json"
    source_manifest = load_json(source_manifest_path)
    source_records = {
        item["id"]: item
        for item in source_manifest.get("assets", [])
        if isinstance(item, dict) and isinstance(item.get("id"), str)
    }
    output_dir = example_root / "svgs"
    report_dir = example_root / "reports"
    output_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)

    entries: list[dict[str, Any]] = []
    geometry_owners: dict[str, str] = {}
    path_owners: dict[str, str] = {}
    composition_owners: dict[str, str] = {}
    ordinal = 0
    for family_index, family in enumerate(families):
        source_id = str(family["sourceId"])
        source = source_records.get(source_id)
        if source is None:
            raise RuntimeError(f"Unknown sourceId in gallery spec: {source_id}")
        source_path = SKILL_ROOT / "assets" / "base-images" / source["filename"]
        for item_index in range(int(family["count"])):
            recipe = recipe_for(
                family,
                family_index=family_index,
                item_index=item_index,
                ordinal=ordinal,
            )
            pattern_id = str(recipe["id"])
            svg_path = output_dir / f"{pattern_id}.svg"
            report_path = report_dir / f"{pattern_id}.json"
            colorset = str(recipe["colorset"])
            argv = [
                str(relative_path(source_path)),
                str(relative_path(svg_path)),
                "--mode",
                str(recipe["mode"]),
                "--tile",
                "none",
                "--max-dimension",
                str(recipe["maxDimension"]),
                "--min-area",
                str(recipe["minArea"]),
                "--colors",
                str(recipe["colors"]),
                "--smoothing",
                str(recipe["smoothing"]),
                "--detail",
                str(recipe["detail"]),
                "--outline",
                str(recipe["outline"]),
                "--palette-method",
                str(recipe["paletteMethod"]),
                "--pattern-id",
                pattern_id,
                "--title",
                f"{recipe['title']} — {colorset.title()}",
                "--description",
                (
                    f"{recipe['description']} Unique collection member "
                    f"{recipe['ordinal']} of {EXPECTED_PATTERN_COUNT}."
                ),
                "--colorset",
                colorset,
                "--variation-seed",
                str(recipe["variationSeed"]),
                "--crop-scale",
                str(recipe["cropScale"]),
                "--crop-x",
                str(recipe["cropX"]),
                "--crop-y",
                str(recipe["cropY"]),
                "--rotation",
                str(recipe["rotation"]),
                "--flow-strength",
                str(recipe["flowStrength"]),
                "--flow-frequency",
                str(recipe["flowFrequency"]),
                "--source-manifest",
                str(relative_path(source_manifest_path)),
                "--source-id",
                source_id,
                "--report",
                str(relative_path(report_path)),
            ]
            args = vectorizer.apply_mode_defaults(
                vectorizer.build_parser().parse_args(argv)
            )
            report = normalize_report_paths(
                vectorizer.vectorize(args),
                input_path=source_path,
                output_path=svg_path,
            )
            vectorizer.atomic_write_json(report_path, report)
            validation_args = validator.build_parser().parse_args(
                [
                    str(svg_path),
                    "--report",
                    str(report_path),
                    "--expected-pattern-id",
                    pattern_id,
                    "--expected-mode",
                    str(recipe["mode"]),
                    "--expected-tile",
                    "none",
                    "--expected-colorset",
                    colorset,
                    "--expected-variation-seed",
                    str(recipe["variationSeed"]),
                    "--min-paths",
                    str(recipe["minPaths"]),
                ]
            )
            inspection = validator.validate_against_args(
                validator.inspect_svg(svg_path),
                validation_args,
            )
            if inspection["pattern_element_count"] or inspection["use_element_count"]:
                raise RuntimeError(
                    f"Collection member reuses SVG elements: {pattern_id}"
                )

            geometry = svg_geometry_record(svg_path)
            geometry_digest = str(geometry["geometrySha256"])
            previous_geometry = geometry_owners.get(geometry_digest)
            if previous_geometry:
                raise RuntimeError(
                    f"Geometry reused by {previous_geometry} and {pattern_id}"
                )
            geometry_owners[geometry_digest] = pattern_id
            for signature in geometry["pathSignatures"]:
                previous_path = path_owners.get(signature)
                if previous_path:
                    raise RuntimeError(
                        f"Path data reused by {previous_path} and {pattern_id}"
                    )
                path_owners[signature] = pattern_id
            composition_digest = str(report["composition_sha256"])
            previous_composition = composition_owners.get(composition_digest)
            if previous_composition:
                raise RuntimeError(
                    "Raster composition reused by "
                    f"{previous_composition} and {pattern_id}"
                )
            composition_owners[composition_digest] = pattern_id

            entries.append(
                {
                    "id": pattern_id,
                    "exampleId": recipe["exampleId"],
                    "ordinal": recipe["ordinal"],
                    "familyId": recipe["familyId"],
                    "familyTitle": recipe["familyTitle"],
                    "variant": recipe["variant"],
                    "colorset": colorset,
                    "colorsetLabel": (
                        "Colorset 1"
                        if colorset == "colorset1"
                        else "Colorset 2"
                    ),
                    "title": recipe["title"],
                    "description": recipe["description"],
                    "mode": recipe["mode"],
                    "tile": "none",
                    "svg": f"svgs/{pattern_id}.svg",
                    "report": f"reports/{pattern_id}.json",
                    "sha256": report["output_sha256"],
                    "geometrySha256": geometry_digest,
                    "pathSignatures": geometry["pathSignatures"],
                    "compositionSha256": composition_digest,
                    "bytes": report["output_bytes"],
                    "pathCount": report["path_count"],
                    "contourCount": report["contour_count"],
                    "pointCount": report["point_count"],
                    "palette": report["palette"],
                    "visibleColorTokens": inspection["visible_color_tokens"],
                    "variationSeed": recipe["variationSeed"],
                    "parameters": {
                        key: recipe[key]
                        for key in (
                            "colors",
                            "smoothing",
                            "detail",
                            "minArea",
                            "maxDimension",
                            "cropScale",
                            "cropX",
                            "cropY",
                            "rotation",
                            "flowStrength",
                            "flowFrequency",
                            "outline",
                            "paletteMethod",
                        )
                    },
                    "sourceId": source_id,
                    "sourceTitle": source["title"],
                    "creator": source["creator"],
                    "sourcePage": source["source_page"],
                    "license": source["license"],
                    "licenseUrl": source["license_url"],
                }
            )
            ordinal += 1
            if ordinal % 25 == 0:
                print(
                    f"Generated {ordinal}/{EXPECTED_PATTERN_COUNT} unique patterns.",
                    file=sys.stderr,
                    flush=True,
                )

    if len(entries) != EXPECTED_PATTERN_COUNT:
        raise RuntimeError(
            f"Generated {len(entries)} patterns, expected {EXPECTED_PATTERN_COUNT}"
        )
    expected_svgs = {f"{entry['id']}.svg" for entry in entries}
    expected_reports = {f"{entry['id']}.json" for entry in entries}
    removed_svgs = remove_stale(output_dir, expected_svgs, ".svg")
    removed_reports = remove_stale(report_dir, expected_reports, ".json")
    actual_svgs = {path.name for path in output_dir.glob("*.svg")}
    actual_reports = {path.name for path in report_dir.glob("*.json")}
    if actual_svgs != expected_svgs:
        raise RuntimeError(
            f"SVG inventory mismatch: {sorted(actual_svgs ^ expected_svgs)}"
        )
    if actual_reports != expected_reports:
        raise RuntimeError(
            f"Report inventory mismatch: {sorted(actual_reports ^ expected_reports)}"
        )

    colorset_contract = vectorizer.load_colorset_contract()
    colorset_counts = Counter(str(entry["colorset"]) for entry in entries)
    mode_counts = Counter(str(entry["mode"]) for entry in entries)
    source_counts = Counter(str(entry["sourceId"]) for entry in entries)
    family_summaries = []
    for family in families:
        family_entries = [
            entry for entry in entries if entry["familyId"] == family["id"]
        ]
        family_summaries.append(
            {
                "id": family["id"],
                "title": family["title"],
                "description": family["description"],
                "mode": family["mode"],
                "sourceId": family["sourceId"],
                "patternCount": len(family_entries),
                "colorsetCounts": dict(
                    sorted(
                        Counter(
                            str(entry["colorset"]) for entry in family_entries
                        ).items()
                    )
                ),
            }
        )
    catalog_fingerprint = sha256_json(
        [
            {
                "id": entry["id"],
                "geometrySha256": entry["geometrySha256"],
                "pathSignatures": entry["pathSignatures"],
                "compositionSha256": entry["compositionSha256"],
            }
            for entry in entries
        ]
    )
    manifest = {
        "schemaVersion": 2,
        "pageId": "vectorize-art-patterns",
        "namespace": "vectorize",
        "title": "300 Unique Vectorized Art Patterns",
        "description": (
            "Three hundred non-geometric abstract and Cubist-derived SVG "
            "patterns with no reused path data or complete geometry."
        ),
        "generatedBy": "scripts/build_example_gallery.py",
        "sourceManifest": "assets/base-images/manifest.json",
        "colorsetContractSha256": sha256_path(
            vectorizer.DEFAULT_COLORSET_CONTRACT
        ),
        "colorsets": {
            name: {
                "name": colorset_contract["colorsets"][name]["name"],
                "allowed": colorset_contract["colorsets"][name]["allowed"],
            }
            for name in vectorizer.COLORSET_NAMES
        },
        "patternCount": len(entries),
        "familyCount": len(families),
        "uniqueGeometryCount": len(geometry_owners),
        "uniquePathCount": len(path_owners),
        "uniqueCompositionCount": len(composition_owners),
        "colorsetCounts": dict(sorted(colorset_counts.items())),
        "modeCounts": dict(sorted(mode_counts.items())),
        "sourceCounts": dict(sorted(source_counts.items())),
        "catalogFingerprint": catalog_fingerprint,
        "uniquenessContract": {
            "canonicalPatternCount": EXPECTED_PATTERN_COUNT,
            "completeGeometryReuseAllowed": False,
            "pathDataReuseAllowed": False,
            "compositionReuseAllowed": False,
            "svgUseElementsAllowed": False,
            "tileMode": "none",
        },
        "families": family_summaries,
        "patterns": entries,
    }
    vectorizer.atomic_write_json(example_root / "manifest.json", manifest)
    return {
        "ok": True,
        "example_root": str(example_root),
        "family_count": len(families),
        "pattern_count": len(entries),
        "colorset_counts": dict(sorted(colorset_counts.items())),
        "mode_counts": dict(sorted(mode_counts.items())),
        "unique_geometry_count": len(geometry_owners),
        "unique_path_count": len(path_owners),
        "unique_composition_count": len(composition_owners),
        "catalog_fingerprint": catalog_fingerprint,
        "removed_stale_svg_count": len(removed_svgs),
        "removed_stale_report_count": len(removed_reports),
        "manifest_sha256": sha256_path(example_root / "manifest.json"),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build the 300-pattern vectorize-art-patterns gallery."
    )
    parser.add_argument(
        "--example-root",
        type=Path,
        default=DEFAULT_EXAMPLE_ROOT,
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    result = build_gallery(args.example_root.resolve())
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
