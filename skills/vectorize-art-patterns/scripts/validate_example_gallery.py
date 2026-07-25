#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "pillow>=11.0",
# ]
# ///
"""Validate the 30-work, geometry-locked open-masterpiece gallery."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
import sys
from typing import Any
import xml.etree.ElementTree as ET

from PIL import Image


SKILL_ROOT = Path(__file__).resolve().parents[1]
FIXTURE_ROOT = SKILL_ROOT / "assets" / "examples" / "vectorize-art-patterns"
MANIFEST_PATH = FIXTURE_ROOT / "manifest.json"
SPEC_PATH = FIXTURE_ROOT / "gallery-spec.json"
SOURCE_MANIFEST_PATH = SKILL_ROOT / "assets" / "base-images" / "manifest.json"
PALETTE_PATH = SKILL_ROOT / "assets" / "palettes" / "colorsets.json"
EXPECTED_ARTWORK_COUNT = 30
EXPECTED_VARIANT_COUNT = 60
EXPECTED_COLORSETS = ("colorset1", "colorset2")
EXPECTED_ANCHORS = {"colorset1": "#9e1b32", "colorset2": "#007298"}
ALLOWED_LICENSE_PREFIXES = ("Public-Domain", "CC0-", "CC-BY-", "CC-BY-SA-")
PATTERN_ID_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
HEX_COLOR_RE = re.compile(r"^#[0-9a-f]{6}$")


class ValidationError(RuntimeError):
    """Raised when the published fixture breaks its collection contract."""


def read_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValidationError(f"Cannot read JSON {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise ValidationError(f"Expected a JSON object: {path}")
    return payload


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def direct_child_text(root: ET.Element, name: str) -> str:
    for child in root:
        if child.tag.rsplit("}", 1)[-1] == name:
            return (child.text or "").strip()
    return ""


def geometry_from_svg(path: Path) -> dict[str, Any]:
    try:
        raw = path.read_text(encoding="utf-8")
        root = ET.fromstring(raw)
    except (OSError, UnicodeDecodeError, ET.ParseError) as exc:
        raise ValidationError(f"Cannot parse SVG {path}: {exc}") from exc
    paths: list[str] = []
    fills: set[str] = set()
    forbidden: list[str] = []
    external_references: list[str] = []
    for element in root.iter():
        name = element.tag.rsplit("}", 1)[-1]
        if name in {"image", "script", "foreignObject", "use", "pattern"}:
            forbidden.append(name)
        if name == "path":
            data = element.get("d", "").strip()
            if not data or not re.match(r"^[Mm]\s*[-+\d.]", data):
                raise ValidationError(f"Invalid path data in {path}")
            paths.append(data)
        fill = element.get("fill")
        if fill and HEX_COLOR_RE.fullmatch(fill.lower()):
            fills.add(fill.lower())
        for attribute, value in element.attrib.items():
            if attribute.rsplit("}", 1)[-1] == "href" and not value.startswith("#"):
                external_references.append(value)
    if forbidden:
        raise ValidationError(f"Forbidden SVG elements in {path}: {sorted(set(forbidden))}")
    if external_references:
        raise ValidationError(f"External references in {path}: {external_references[:3]}")
    if not paths:
        raise ValidationError(f"SVG has no editable paths: {path}")
    title = direct_child_text(root, "title")
    description = direct_child_text(root, "desc")
    metadata_text = direct_child_text(root, "metadata")
    if not title or not description or not metadata_text:
        raise ValidationError(f"SVG accessibility/provenance is incomplete: {path}")
    try:
        metadata = json.loads(metadata_text)
    except json.JSONDecodeError as exc:
        raise ValidationError(f"SVG metadata is invalid JSON in {path}") from exc
    geometry = hashlib.sha256("\n".join(paths).encode("utf-8")).hexdigest()
    return {
        "root": root,
        "metadata": metadata,
        "geometrySha256": geometry,
        "pathCount": len(paths),
        "fills": fills,
        "bytes": len(raw.encode("utf-8")),
    }


def difference_hash(path: Path) -> int:
    with Image.open(path) as image:
        grayscale = image.convert("L").resize((9, 8), Image.Resampling.LANCZOS)
        pixels = list(grayscale.get_flattened_data())
    result = 0
    for row in range(8):
        for column in range(8):
            left = pixels[row * 9 + column]
            right = pixels[row * 9 + column + 1]
            result = (result << 1) | int(left > right)
    return result


def hamming_distance(first: int, second: int) -> int:
    return (first ^ second).bit_count()


def inventory_digest(paths: list[Path]) -> str:
    digest = hashlib.sha256()
    for path in sorted(paths, key=lambda item: item.as_posix()):
        relative = path.relative_to(FIXTURE_ROOT).as_posix()
        digest.update(relative.encode("utf-8"))
        digest.update(b"\0")
        digest.update(bytes.fromhex(sha256_path(path)))
    return digest.hexdigest()


def validate() -> dict[str, Any]:
    manifest = read_json(MANIFEST_PATH)
    spec = read_json(SPEC_PATH)
    sources_manifest = read_json(SOURCE_MANIFEST_PATH)
    palette_contract = read_json(PALETTE_PATH)
    if manifest.get("schemaVersion") != 3 or spec.get("schemaVersion") != 3:
        raise ValidationError("Gallery manifest and spec must use schemaVersion 3")
    if manifest.get("pageId") != "vectorize-art-patterns":
        raise ValidationError("Gallery manifest has the wrong stable page ID")
    if (
        manifest.get("artworkCount") != EXPECTED_ARTWORK_COUNT
        or manifest.get("variantCount") != EXPECTED_VARIANT_COUNT
    ):
        raise ValidationError("Gallery count metadata is incorrect")
    artworks = manifest.get("artworks")
    if not isinstance(artworks, list) or len(artworks) != EXPECTED_ARTWORK_COUNT:
        raise ValidationError("Gallery manifest must contain exactly 30 artworks")
    spec_artworks = spec.get("artworks")
    if not isinstance(spec_artworks, list):
        raise ValidationError("Gallery spec is missing artworks")
    spec_ids = [str(item.get("id")) for item in spec_artworks if isinstance(item, dict)]
    manifest_ids = [str(item.get("id")) for item in artworks if isinstance(item, dict)]
    if spec_ids != manifest_ids:
        raise ValidationError("Gallery spec and manifest artwork order/IDs differ")
    if len(set(manifest_ids)) != EXPECTED_ARTWORK_COUNT:
        raise ValidationError("Every gallery artwork must use a distinct source ID")

    source_assets = sources_manifest.get("assets")
    if not isinstance(source_assets, list):
        raise ValidationError("Base-image manifest is missing assets")
    source_by_id = {
        str(asset["id"]): asset
        for asset in source_assets
        if isinstance(asset, dict) and asset.get("id")
    }
    colorsets = palette_contract.get("colorsets")
    if not isinstance(colorsets, dict):
        raise ValidationError("Colorset contract is malformed")
    allowed_by_colorset = {
        name: {str(value).lower() for value in colorsets[name]["allowed"]}
        for name in EXPECTED_COLORSETS
    }

    page = (FIXTURE_ROOT / "index.html").read_text(encoding="utf-8")
    script = (FIXTURE_ROOT / "gallery.js").read_text(encoding="utf-8")
    styles = (FIXTURE_ROOT / "gallery.css").read_text(encoding="utf-8")
    for marker in (
        'data-pattern-page-id="vectorize-art-patterns"',
        "Thirty sources.",
        'id="gallery"',
        'id="artwork-template"',
        'data-colorset="colorset1"',
        'data-colorset="colorset2"',
    ):
        if marker not in page:
            raise ValidationError(f"Gallery page is missing marker: {marker}")
    if "manifest.json" not in script or "manifest.artworkCount !== 30" not in script:
        raise ValidationError("Gallery JavaScript does not enforce manifest counts")
    for token in ("#9e1b32", "#007298", "#e77204", "#45842a", "#652f6c"):
        if token not in styles:
            raise ValidationError(f"Gallery CSS is missing colorset token {token}")

    expected_svg_files: set[str] = set()
    expected_report_files: set[str] = set()
    generated_paths: list[Path] = []
    pattern_ids: set[str] = set()
    source_hashes: set[str] = set()
    geometry_hashes: set[str] = set()
    creators: set[str] = set()
    providers: set[str] = set()
    source_hash_values: dict[str, int] = {}
    max_svg_bytes = 0
    max_path_count = 0
    variants_validated = 0

    for artwork in artworks:
        if not isinstance(artwork, dict):
            raise ValidationError("Every manifest artwork must be an object")
        source_id = str(artwork.get("sourceId", ""))
        source = source_by_id.get(source_id)
        if source is None:
            raise ValidationError(f"Unknown source ID: {source_id}")
        if artwork.get("sourceSha256") != source.get("sha256"):
            raise ValidationError(f"Source SHA-256 mismatch for {source_id}")
        source_sha256 = str(source.get("sha256", ""))
        if source_sha256 in source_hashes:
            raise ValidationError(f"Repeated source image hash: {source_id}")
        source_hashes.add(source_sha256)
        source_path = SOURCE_MANIFEST_PATH.parent / str(source.get("filename", ""))
        if not source_path.is_file() or sha256_path(source_path) != source_sha256:
            raise ValidationError(f"Source file/hash mismatch: {source_id}")
        license_name = str(source.get("license", ""))
        if not license_name.startswith(ALLOWED_LICENSE_PREFIXES):
            raise ValidationError(f"Derivative-unsafe source license: {source_id}")
        if source.get("transformation_allowed") is not True:
            raise ValidationError(f"Source does not explicitly allow transformation: {source_id}")
        creators.add(str(artwork.get("creator", "")))
        providers.add(str(artwork.get("provider", "")))
        source_hash_values[source_id] = difference_hash(source_path)

        variants = artwork.get("variants")
        if not isinstance(variants, dict) or set(variants) != set(EXPECTED_COLORSETS):
            raise ValidationError(f"Artwork does not have one variant per colorset: {source_id}")
        pair_geometry: str | None = None
        pair_composition: str | None = None
        for colorset_name in EXPECTED_COLORSETS:
            variant = variants[colorset_name]
            pattern_id = str(variant.get("patternId", ""))
            if not PATTERN_ID_RE.fullmatch(pattern_id) or len(pattern_id) > 64:
                raise ValidationError(f"Invalid pattern ID: {pattern_id}")
            if pattern_id in pattern_ids:
                raise ValidationError(f"Repeated pattern ID: {pattern_id}")
            pattern_ids.add(pattern_id)
            expected_suffix = "-cs1" if colorset_name == "colorset1" else "-cs2"
            if not pattern_id.endswith(expected_suffix):
                raise ValidationError(f"Pattern ID has the wrong colorset suffix: {pattern_id}")

            svg_relative = str(variant.get("file", ""))
            report_relative = str(variant.get("report", ""))
            if svg_relative != f"svgs/{pattern_id}.svg":
                raise ValidationError(f"Unexpected SVG path for {pattern_id}")
            if report_relative != f"reports/{pattern_id}.json":
                raise ValidationError(f"Unexpected report path for {pattern_id}")
            expected_svg_files.add(svg_relative)
            expected_report_files.add(report_relative)
            svg_path = FIXTURE_ROOT / svg_relative
            report_path = FIXTURE_ROOT / report_relative
            if not svg_path.is_file() or not report_path.is_file():
                raise ValidationError(f"Missing generated pair for {pattern_id}")
            generated_paths.extend((svg_path, report_path))
            if sha256_path(svg_path) != variant.get("sha256"):
                raise ValidationError(f"SVG hash mismatch for {pattern_id}")
            if svg_path.stat().st_size != variant.get("bytes"):
                raise ValidationError(f"SVG byte count mismatch for {pattern_id}")
            if svg_path.stat().st_size > 2_000_000:
                raise ValidationError(f"SVG exceeds the 2 MB quality ceiling: {pattern_id}")

            inspected = geometry_from_svg(svg_path)
            root = inspected["root"]
            metadata = inspected["metadata"]
            if root.get("data-pattern-id") != pattern_id:
                raise ValidationError(f"Root pattern ID mismatch for {pattern_id}")
            if root.get("data-colorset") != colorset_name:
                raise ValidationError(f"Root colorset mismatch for {pattern_id}")
            if root.get("data-vectorizer") != "vtracer-0.6.15":
                raise ValidationError(f"Missing VTracer backend marker for {pattern_id}")
            if root.get("data-source-sha256") != source_sha256:
                raise ValidationError(f"Root source hash mismatch for {pattern_id}")
            if metadata.get("source", {}).get("source_id") != source_id:
                raise ValidationError(f"Embedded source ID mismatch for {pattern_id}")
            if metadata.get("source", {}).get("license") != license_name:
                raise ValidationError(f"Embedded license mismatch for {pattern_id}")
            if metadata.get("pipeline", {}).get("backend") != "vtracer-0.6.15":
                raise ValidationError(f"Embedded backend mismatch for {pattern_id}")
            if metadata.get("pipeline", {}).get("colorset") != colorset_name:
                raise ValidationError(f"Embedded colorset mismatch for {pattern_id}")
            unexpected = inspected["fills"] - allowed_by_colorset[colorset_name]
            if unexpected:
                raise ValidationError(f"Disallowed palette tokens in {pattern_id}: {sorted(unexpected)}")
            if EXPECTED_ANCHORS[colorset_name] not in inspected["fills"]:
                raise ValidationError(f"Colorset anchor is missing from {pattern_id}")
            if inspected["pathCount"] != variant.get("pathCount"):
                raise ValidationError(f"Path count mismatch for {pattern_id}")
            if inspected["pathCount"] > 1000:
                raise ValidationError(f"SVG has excessive path count: {pattern_id}")
            if inspected["geometrySha256"] != artwork.get("geometrySha256"):
                raise ValidationError(f"Geometry hash mismatch for {pattern_id}")

            report = read_json(report_path)
            if report.get("pattern_id") != pattern_id:
                raise ValidationError(f"Report pattern ID mismatch for {pattern_id}")
            if report.get("output_sha256") != variant.get("sha256"):
                raise ValidationError(f"Report output hash mismatch for {pattern_id}")
            if report.get("input_sha256") != source_sha256:
                raise ValidationError(f"Report source hash mismatch for {pattern_id}")
            if report.get("path_count") != inspected["pathCount"]:
                raise ValidationError(f"Report path count mismatch for {pattern_id}")
            if report.get("backend") != "vtracer-0.6.15":
                raise ValidationError(f"Report backend mismatch for {pattern_id}")
            composition = str(report.get("composition_sha256", ""))
            if pair_geometry is None:
                pair_geometry = inspected["geometrySha256"]
                pair_composition = composition
            elif inspected["geometrySha256"] != pair_geometry:
                raise ValidationError(f"Colorset pair changed geometry for {source_id}")
            elif composition != pair_composition:
                raise ValidationError(f"Colorset pair changed composition for {source_id}")

            max_svg_bytes = max(max_svg_bytes, inspected["bytes"])
            max_path_count = max(max_path_count, inspected["pathCount"])
            variants_validated += 1

        if pair_geometry in geometry_hashes:
            raise ValidationError(f"Two different source artworks share geometry: {source_id}")
        geometry_hashes.add(str(pair_geometry))
        if artwork.get("compositionSha256") != pair_composition:
            raise ValidationError(f"Manifest composition hash mismatch for {source_id}")

    actual_svg_files = {
        path.relative_to(FIXTURE_ROOT).as_posix()
        for path in (FIXTURE_ROOT / "svgs").glob("*.svg")
    }
    actual_report_files = {
        path.relative_to(FIXTURE_ROOT).as_posix()
        for path in (FIXTURE_ROOT / "reports").glob("*.json")
    }
    if actual_svg_files != expected_svg_files:
        raise ValidationError("SVG directory contains missing or stale files")
    if actual_report_files != expected_report_files:
        raise ValidationError("Report directory contains missing or stale files")
    if len(creators) < 25:
        raise ValidationError(f"Artist diversity is too low: {len(creators)} distinct creators")
    if len(providers) < 2:
        raise ValidationError("Gallery must use at least two open-image providers")

    perceptual_pairs: list[tuple[int, str, str]] = []
    source_items = sorted(source_hash_values.items())
    for index, (first_id, first_hash) in enumerate(source_items):
        for second_id, second_hash in source_items[index + 1 :]:
            perceptual_pairs.append(
                (hamming_distance(first_hash, second_hash), first_id, second_id)
            )
    minimum_distance, nearest_first, nearest_second = min(perceptual_pairs)
    if minimum_distance < 5:
        raise ValidationError(
            "Source corpus contains a likely near-duplicate pair: "
            f"{nearest_first}, {nearest_second} (dHash distance {minimum_distance})"
        )

    if manifest.get("uniqueSourceCount") != len(source_hashes):
        raise ValidationError("Manifest uniqueSourceCount is incorrect")
    if manifest.get("geometryLockedPairCount") != len(geometry_hashes):
        raise ValidationError("Manifest geometryLockedPairCount is incorrect")
    if manifest.get("sourceManifestSha256") != sha256_path(SOURCE_MANIFEST_PATH):
        raise ValidationError("Manifest source-manifest hash is stale")
    if manifest.get("paletteContractSha256") != sha256_path(PALETTE_PATH):
        raise ValidationError("Manifest palette-contract hash is stale")
    actual_inventory = inventory_digest(generated_paths)
    if manifest.get("inventorySha256") != actual_inventory:
        raise ValidationError("Manifest inventory hash is stale")

    return {
        "schemaVersion": 1,
        "status": "pass",
        "pageId": manifest["pageId"],
        "artworkCount": len(artworks),
        "variantCount": variants_validated,
        "uniqueSourceCount": len(source_hashes),
        "distinctCreatorCount": len(creators),
        "providerCount": len(providers),
        "geometryLockedPairCount": len(geometry_hashes),
        "minimumSourceDHashDistance": minimum_distance,
        "nearestSourcePair": [nearest_first, nearest_second],
        "maxSvgBytes": max_svg_bytes,
        "maxPathCount": max_path_count,
        "inventorySha256": actual_inventory,
    }


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    result = validate()
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ValidationError as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(2)
