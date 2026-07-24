#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "numpy>=2.0",
#   "opencv-python-headless>=4.10",
#   "pillow>=11.0",
# ]
# ///
"""Build the deterministic colorset1/colorset2 Pages acceptance gallery."""

from __future__ import annotations

import argparse
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


def relative_path(path: Path) -> Path:
    return Path(os.path.relpath(path.resolve(), Path.cwd().resolve()))


def geometry_sha256(svg: Path) -> str:
    root = ET.fromstring(svg.read_text(encoding="utf-8"))
    paths = [
        element.get("d", "")
        for element in root.iter()
        if element.tag.rsplit("}", 1)[-1] == "path"
    ]
    payload = {
        "viewBox": root.get("viewBox", ""),
        "paths": paths,
    }
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


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


def build_gallery(example_root: Path) -> dict[str, Any]:
    spec_path = example_root / "gallery-spec.json"
    spec = load_json(spec_path)
    if spec.get("schemaVersion") != 1:
        raise RuntimeError("Gallery spec schemaVersion must be 1")
    base_patterns = spec.get("patterns")
    if not isinstance(base_patterns, list) or len(base_patterns) != 4:
        raise RuntimeError("Gallery spec must contain exactly four base patterns")

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
    variants = (("cs1", "colorset1"), ("cs2", "colorset2"))
    for base in base_patterns:
        source_id = str(base["sourceId"])
        source = source_records.get(source_id)
        if source is None:
            raise RuntimeError(f"Unknown sourceId in gallery spec: {source_id}")
        source_path = SKILL_ROOT / "assets" / "base-images" / source["filename"]
        pair_geometry: set[str] = set()
        for variant, colorset in variants:
            pattern_id = f"{base['idBase']}-{variant}"
            svg_path = output_dir / f"{pattern_id}.svg"
            report_path = report_dir / f"{pattern_id}.json"
            title = f"{base['title']} — {colorset.title()}"
            description = (
                f"{base['description']} Recolored with the canonical "
                f"{colorset} palette."
            )
            argv = [
                str(relative_path(source_path)),
                str(relative_path(svg_path)),
                "--mode",
                str(base["mode"]),
                "--tile",
                str(base["tile"]),
                "--max-dimension",
                str(base["maxDimension"]),
                "--min-area",
                str(base["minArea"]),
                "--pattern-id",
                pattern_id,
                "--title",
                title,
                "--description",
                description,
                "--colorset",
                colorset,
                "--source-manifest",
                str(relative_path(source_manifest_path)),
                "--source-id",
                source_id,
                "--report",
                str(relative_path(report_path)),
            ]
            for key, option in (
                ("colors", "--colors"),
                ("smoothing", "--smoothing"),
                ("detail", "--detail"),
                ("outline", "--outline"),
            ):
                if key in base:
                    argv.extend([option, str(base[key])])
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
                    str(base["mode"]),
                    "--expected-tile",
                    str(base["tile"]),
                    "--expected-colorset",
                    colorset,
                    "--min-paths",
                    str(base["minPaths"]),
                    *(["--require-pattern"] if base["tile"] != "none" else []),
                ]
            )
            validation = validator.validate_against_args(
                validator.inspect_svg(svg_path),
                validation_args,
            )
            geometry_digest = geometry_sha256(svg_path)
            pair_geometry.add(geometry_digest)
            entries.append(
                {
                    "id": pattern_id,
                    "exampleId": base["slug"],
                    "variant": variant,
                    "colorset": colorset,
                    "colorsetLabel": "Colorset 1"
                    if colorset == "colorset1"
                    else "Colorset 2",
                    "title": base["title"],
                    "description": base["description"],
                    "mode": base["mode"],
                    "tile": base["tile"],
                    "svg": f"svgs/{pattern_id}.svg",
                    "report": f"reports/{pattern_id}.json",
                    "sha256": report["output_sha256"],
                    "geometrySha256": geometry_digest,
                    "bytes": report["output_bytes"],
                    "pathCount": report["path_count"],
                    "contourCount": report["contour_count"],
                    "pointCount": report["point_count"],
                    "palette": report["palette"],
                    "visibleColorTokens": validation["visible_color_tokens"],
                    "sourceId": source_id,
                    "sourceTitle": source["title"],
                    "creator": source["creator"],
                    "sourcePage": source["source_page"],
                    "license": source["license"],
                    "licenseUrl": source["license_url"],
                }
            )
        if len(pair_geometry) != 1:
            raise RuntimeError(
                f"Colorset variants changed geometry for {base['idBase']}"
            )

    expected_svgs = {f"{entry['id']}.svg" for entry in entries}
    expected_reports = {f"{entry['id']}.json" for entry in entries}
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
    manifest = {
        "schemaVersion": 1,
        "pageId": "vectorize-art-patterns",
        "namespace": "vectorize",
        "title": "Vectorized Art Patterns",
        "description": (
            "Open-source artwork simplified into editable SVG and paired "
            "across canonical colorset1 and colorset2 palettes."
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
        "basePatternCount": len(base_patterns),
        "patternCount": len(entries),
        "patterns": entries,
    }
    vectorizer.atomic_write_json(example_root / "manifest.json", manifest)
    return {
        "ok": True,
        "example_root": str(example_root),
        "base_pattern_count": len(base_patterns),
        "pattern_count": len(entries),
        "colorset1_count": sum(
            entry["colorset"] == "colorset1" for entry in entries
        ),
        "colorset2_count": sum(
            entry["colorset"] == "colorset2" for entry in entries
        ),
        "manifest_sha256": sha256_path(example_root / "manifest.json"),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build the vectorize-art-patterns Pages acceptance gallery."
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
