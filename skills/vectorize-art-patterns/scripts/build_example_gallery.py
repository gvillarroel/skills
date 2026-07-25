#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11,<3.14"
# dependencies = [
#   "numpy>=2.0",
#   "opencv-python-headless>=4.10",
#   "pillow>=11.0",
#   "vtracer==0.6.15",
# ]
# ///
"""Build the 30-work, 60-variant open-masterpiece Pages gallery."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import shutil
import sys
from typing import Any
import xml.etree.ElementTree as ET


SKILL_ROOT = Path(__file__).resolve().parents[1]
FIXTURE_ROOT = (
    SKILL_ROOT / "assets" / "examples" / "vectorize-art-patterns"
)
SPEC_PATH = FIXTURE_ROOT / "gallery-spec.json"
SOURCE_MANIFEST_PATH = SKILL_ROOT / "assets" / "base-images" / "manifest.json"
VECTORIZE_VTRACER_PATH = Path(__file__).with_name("vectorize_with_vtracer.py")
EXPECTED_ARTWORK_COUNT = 30
EXPECTED_VARIANT_COUNT = 60
COLORSET_SUFFIXES = {"colorset1": "cs1", "colorset2": "cs2"}


class BuildError(RuntimeError):
    """Raised when the gallery cannot be built safely."""


def load_module(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise BuildError(f"Cannot load gallery dependency: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


VT = load_module(VECTORIZE_VTRACER_PATH, "vectorize_with_vtracer_gallery")
VA = VT.VA


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise BuildError(f"Cannot read JSON {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise BuildError(f"Expected a JSON object: {path}")
    return payload


def validate_spec(spec: dict[str, Any]) -> list[dict[str, Any]]:
    if spec.get("schemaVersion") != 3:
        raise BuildError("Gallery spec must use schemaVersion 3")
    artworks = spec.get("artworks")
    if not isinstance(artworks, list) or len(artworks) != EXPECTED_ARTWORK_COUNT:
        raise BuildError(
            f"Gallery spec must contain {EXPECTED_ARTWORK_COUNT} artworks"
        )
    if spec.get("artworkCount") != EXPECTED_ARTWORK_COUNT:
        raise BuildError("Gallery spec artworkCount does not match the artwork list")
    if spec.get("variantCount") != EXPECTED_VARIANT_COUNT:
        raise BuildError("Gallery spec variantCount must be 60")
    if spec.get("colorsets") != ["colorset1", "colorset2"]:
        raise BuildError("Gallery spec must define colorset1 and colorset2")

    seen: set[str] = set()
    for artwork in artworks:
        if not isinstance(artwork, dict):
            raise BuildError("Every artwork spec must be an object")
        source_id = str(artwork.get("id", ""))
        if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", source_id):
            raise BuildError(f"Invalid artwork/source ID: {source_id}")
        if source_id in seen:
            raise BuildError(f"Repeated source ID in gallery spec: {source_id}")
        seen.add(source_id)
        if artwork.get("mode") not in {"organic", "ink", "stain", "collage"}:
            raise BuildError(f"Unsupported mode for {source_id}")
        if artwork.get("paletteMethod") not in {"median-cut", "max-coverage"}:
            raise BuildError(f"Unsupported palette method for {source_id}")
        if not isinstance(artwork.get("genre"), str) or not artwork["genre"]:
            raise BuildError(f"Missing genre for {source_id}")
    return artworks


def source_records() -> tuple[dict[str, dict[str, Any]], dict[str, Any]]:
    manifest = read_json(SOURCE_MANIFEST_PATH)
    if manifest.get("schema_version") != 1:
        raise BuildError("Unsupported base-image manifest")
    assets = manifest.get("assets")
    if not isinstance(assets, list):
        raise BuildError("Base-image manifest is missing assets")
    records = {
        str(asset["id"]): asset
        for asset in assets
        if isinstance(asset, dict) and asset.get("id")
    }
    return records, manifest


def reset_generated_directory(path: Path) -> None:
    fixture = FIXTURE_ROOT.resolve()
    target = path.resolve()
    if target.parent != fixture:
        raise BuildError(f"Refusing to reset a path outside the fixture: {target}")
    if target.exists():
        shutil.rmtree(target)
    target.mkdir(parents=True)


def path_geometry(path: Path) -> tuple[str, int]:
    try:
        root = ET.parse(path).getroot()
    except (OSError, ET.ParseError) as exc:
        raise BuildError(f"Cannot inspect generated SVG {path}: {exc}") from exc
    path_data = [
        element.get("d", "").strip()
        for element in root.iter()
        if element.tag.rsplit("}", 1)[-1] == "path"
    ]
    if not path_data or any(not value for value in path_data):
        raise BuildError(f"Generated SVG has empty path data: {path}")
    digest = hashlib.sha256("\n".join(path_data).encode("utf-8")).hexdigest()
    return digest, len(path_data)


def inventory_digest(paths: list[Path]) -> str:
    digest = hashlib.sha256()
    for path in sorted(paths, key=lambda item: item.as_posix()):
        relative = path.relative_to(FIXTURE_ROOT).as_posix()
        digest.update(relative.encode("utf-8"))
        digest.update(b"\0")
        digest.update(bytes.fromhex(sha256_path(path)))
    return digest.hexdigest()


def build() -> dict[str, Any]:
    spec = read_json(SPEC_PATH)
    artwork_specs = validate_spec(spec)
    sources, _source_manifest = source_records()
    missing = [artwork["id"] for artwork in artwork_specs if artwork["id"] not in sources]
    if missing:
        raise BuildError(f"Gallery sources are missing from the manifest: {missing}")

    svg_root = FIXTURE_ROOT / "svgs"
    report_root = FIXTURE_ROOT / "reports"
    reset_generated_directory(svg_root)
    reset_generated_directory(report_root)

    default_max_dimension = int(spec.get("defaultMaxDimension", 560))
    generated_paths: list[Path] = []
    artwork_entries: list[dict[str, Any]] = []
    global_geometry_hashes: set[str] = set()
    variant_count = 0

    for artwork_spec in artwork_specs:
        source_id = str(artwork_spec["id"])
        source = sources[source_id]
        source_path = SOURCE_MANIFEST_PATH.parent / str(source["filename"])
        if not source_path.is_file():
            raise BuildError(f"Gallery source file is missing: {source_path}")
        title = str(
            artwork_spec.get("displayTitle")
            or source.get("title")
            or source_id.replace("-", " ").title()
        )
        creator = str(source.get("creator") or "Unknown creator")
        variants: dict[str, Any] = {}
        pair_geometry: str | None = None
        pair_composition: str | None = None

        for colorset_name, suffix in COLORSET_SUFFIXES.items():
            pattern_id = f"vectorize-{source_id}-{suffix}"
            svg_path = svg_root / f"{pattern_id}.svg"
            report_path = report_root / f"{pattern_id}.json"
            args = argparse.Namespace(
                input=source_path,
                output=svg_path,
                mode=str(artwork_spec["mode"]),
                colorset=colorset_name,
                colors=int(artwork_spec["colors"]),
                smoothing=float(artwork_spec["smoothing"]),
                palette_method=str(artwork_spec["paletteMethod"]),
                max_dimension=int(
                    artwork_spec.get("maxDimension", default_max_dimension)
                ),
                filter_speckle=int(artwork_spec["filterSpeckle"]),
                curve_mode="spline",
                pattern_id=pattern_id,
                title=f"{title} — {colorset_name}",
                description=(
                    f"Editable {colorset_name} VTracer reinterpretation of "
                    f"{title} by {creator}, derived from a verified open image."
                ),
                report=report_path,
                source_manifest=SOURCE_MANIFEST_PATH,
                source_id=source_id,
                rights_basis=None,
                source_url=None,
            )
            report = VT.vectorize(args)
            report["input"] = f"assets/base-images/{source['filename']}"
            report["output"] = f"svgs/{svg_path.name}"
            VA.atomic_write_json(report_path, report)
            geometry_sha256, path_count = path_geometry(svg_path)
            if pair_geometry is None:
                pair_geometry = geometry_sha256
                pair_composition = str(report["composition_sha256"])
            elif geometry_sha256 != pair_geometry:
                raise BuildError(f"Colorset pair changed geometry for {source_id}")
            elif str(report["composition_sha256"]) != pair_composition:
                raise BuildError(f"Colorset pair changed composition for {source_id}")
            variants[colorset_name] = {
                "patternId": pattern_id,
                "file": f"svgs/{svg_path.name}",
                "report": f"reports/{report_path.name}",
                "sha256": str(report["output_sha256"]),
                "bytes": int(report["output_bytes"]),
                "pathCount": path_count,
                "palette": report["palette"],
            }
            generated_paths.extend((svg_path, report_path))
            variant_count += 1

        if pair_geometry in global_geometry_hashes:
            raise BuildError(f"Two source artworks produced the same geometry: {source_id}")
        global_geometry_hashes.add(str(pair_geometry))
        artwork_entries.append(
            {
                "id": source_id,
                "genre": artwork_spec["genre"],
                "mode": artwork_spec["mode"],
                "title": title,
                "creator": creator,
                "date": source.get("date", ""),
                "sourceId": source_id,
                "sourcePage": source.get("source_page", ""),
                "provider": source.get("provider", ""),
                "license": source.get("license", ""),
                "licenseUrl": source.get("license_url", ""),
                "sourceSha256": source.get("sha256", ""),
                "geometrySha256": pair_geometry,
                "compositionSha256": pair_composition,
                "parameters": {
                    "colors": artwork_spec["colors"],
                    "smoothing": artwork_spec["smoothing"],
                    "paletteMethod": artwork_spec["paletteMethod"],
                    "filterSpeckle": artwork_spec["filterSpeckle"],
                    "maxDimension": artwork_spec.get(
                        "maxDimension", default_max_dimension
                    ),
                },
                "variants": variants,
            }
        )

    if variant_count != EXPECTED_VARIANT_COUNT:
        raise BuildError(
            f"Built {variant_count} variants, expected {EXPECTED_VARIANT_COUNT}"
        )

    manifest = {
        "schemaVersion": 3,
        "pageId": spec["pageId"],
        "title": spec["title"],
        "description": (
            "Thirty distinct open-source or public-domain artworks, each traced "
            "once and painted as geometry-locked Colorset 1 and Colorset 2 SVGs."
        ),
        "generator": "vectorize_with_vtracer.py",
        "backend": "vtracer-0.6.15",
        "artworkCount": len(artwork_entries),
        "variantCount": variant_count,
        "uniqueSourceCount": len({entry["sourceSha256"] for entry in artwork_entries}),
        "geometryLockedPairCount": len(artwork_entries),
        "sourceManifest": "assets/base-images/manifest.json",
        "sourceManifestSha256": sha256_path(SOURCE_MANIFEST_PATH),
        "paletteContractSha256": VA.sha256_path(VA.DEFAULT_COLORSET_CONTRACT),
        "inventorySha256": inventory_digest(generated_paths),
        "genres": sorted({str(entry["genre"]) for entry in artwork_entries}),
        "artworks": artwork_entries,
    }
    manifest_path = FIXTURE_ROOT / "manifest.json"
    VA.atomic_write_json(manifest_path, manifest)
    return manifest


def build_parser() -> argparse.ArgumentParser:
    return argparse.ArgumentParser(
        description="Build the open-masterpiece vectorized art gallery."
    )


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    build_parser().parse_args(argv)
    manifest = build()
    print(
        json.dumps(
            {
                "ok": True,
                "pageId": manifest["pageId"],
                "artworkCount": manifest["artworkCount"],
                "variantCount": manifest["variantCount"],
                "uniqueSourceCount": manifest["uniqueSourceCount"],
                "inventorySha256": manifest["inventorySha256"],
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (BuildError, VT.VTracerError, VA.VectorizeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(2)
