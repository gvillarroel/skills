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
"""Run deterministic, palette, geometry-lock, and rights tests for VTracer."""

from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
from typing import Any
import xml.etree.ElementTree as ET

from PIL import Image, ImageDraw


SCRIPT_DIR = Path(__file__).resolve().parent
sys.dont_write_bytecode = True


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load module: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


vectorizer = load_module(
    "vectorize_with_vtracer", SCRIPT_DIR / "vectorize_with_vtracer.py"
)


def sha256_path(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def create_source(path: Path) -> None:
    image = Image.new("RGB", (180, 140), "#eee2c7")
    draw = ImageDraw.Draw(image)
    draw.polygon(
        [(4, 85), (42, 18), (84, 58), (124, 12), (176, 76), (146, 136), (28, 128)],
        fill="#335f79",
    )
    draw.ellipse((28, 36, 112, 118), fill="#bc5f46")
    draw.ellipse((82, 52, 166, 132), fill="#d9ac3c")
    draw.line([(8, 22), (172, 112)], fill="#262626", width=7)
    image.save(path)


def write_manifest(
    path: Path,
    source: Path,
    *,
    license_name: str = "CC0-1.0",
    transformation_allowed: bool = True,
) -> None:
    payload = {
        "schema_version": 1,
        "policy": {
            "allowed_licenses": [
                "Public-Domain",
                "CC0-1.0",
                "CC-BY-*",
                "CC-BY-SA-*",
            ]
        },
        "assets": [
            {
                "id": "synthetic-vtracer-source",
                "filename": source.name,
                "provider": "local-test",
                "provider_id": "synthetic-vtracer-source",
                "title": "Synthetic VTracer source",
                "creator": "vectorize-art-patterns test suite",
                "date": "2026",
                "metadata_api_url": "https://example.invalid/api/source",
                "original_url": "https://example.invalid/source.png",
                "download_url": "https://example.invalid/source.png",
                "retrieved_at": "2026-01-01T00:00:00+00:00",
                "license": license_name,
                "license_url": "https://creativecommons.org/publicdomain/zero/1.0/",
                "usage_terms": "Synthetic test fixture",
                "source_page": "https://example.invalid/source",
                "attribution": "Synthetic test fixture",
                "attribution_required": False,
                "share_alike": False,
                "restrictions": "",
                "transformation_allowed": transformation_allowed,
                "mime": "image/png",
                "width": 180,
                "height": 140,
                "bytes": source.stat().st_size,
                "sha256": sha256_path(source),
            }
        ],
    }
    path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def trace(
    source: Path,
    manifest: Path,
    output: Path,
    colorset: str,
) -> dict[str, Any]:
    pattern_id = f"synthetic-vtracer-{'cs1' if colorset == 'colorset1' else 'cs2'}"
    args = vectorizer.build_parser().parse_args(
        [
            str(source),
            str(output),
            "--mode",
            "collage",
            "--colorset",
            colorset,
            "--colors",
            "7",
            "--max-dimension",
            "180",
            "--filter-speckle",
            "4",
            "--pattern-id",
            pattern_id,
            "--source-manifest",
            str(manifest),
            "--source-id",
            "synthetic-vtracer-source",
            "--report",
            str(output.with_suffix(".json")),
        ]
    )
    return vectorizer.vectorize(args)


def inspect(path: Path) -> tuple[list[str], set[str]]:
    root = ET.parse(path).getroot()
    geometry: list[str] = []
    fills: set[str] = set()
    for element in root.iter():
        if element.tag.rsplit("}", 1)[-1] == "path":
            geometry.append(element.get("d", "").strip())
        fill = element.get("fill")
        if fill and fill.startswith("#"):
            fills.add(fill.lower())
    return geometry, fills


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="vtracer-skill-test-") as directory:
        workspace = Path(directory)
        source = workspace / "source.png"
        manifest = workspace / "manifest.json"
        create_source(source)
        write_manifest(manifest, source)

        cs1_path = workspace / "cs1.svg"
        cs2_path = workspace / "cs2.svg"
        cs1_report = trace(source, manifest, cs1_path, "colorset1")
        first_hash = sha256_path(cs1_path)
        repeat_report = trace(source, manifest, cs1_path, "colorset1")
        if first_hash != sha256_path(cs1_path):
            raise AssertionError("VTracer output is not byte-deterministic")
        cs2_report = trace(source, manifest, cs2_path, "colorset2")

        cs1_geometry, cs1_fills = inspect(cs1_path)
        cs2_geometry, cs2_fills = inspect(cs2_path)
        if not cs1_geometry or cs1_geometry != cs2_geometry:
            raise AssertionError("Colorset pair changed traced geometry")
        if cs1_report["composition_sha256"] != cs2_report["composition_sha256"]:
            raise AssertionError("Colorset pair changed source composition")
        if cs1_report["output_sha256"] != repeat_report["output_sha256"]:
            raise AssertionError("Deterministic report hashes differ")
        if "#9e1b32" not in cs1_fills or "#007298" not in cs2_fills:
            raise AssertionError("Required Colorset anchor is absent")

        contract = vectorizer.VA.load_colorset_contract()["colorsets"]
        for colorset, fills in (
            ("colorset1", cs1_fills),
            ("colorset2", cs2_fills),
        ):
            allowed = {value.lower() for value in contract[colorset]["allowed"]}
            if fills - allowed:
                raise AssertionError(f"{colorset} emitted disallowed fills")

        write_manifest(
            manifest,
            source,
            license_name="CC-BY-ND-4.0",
            transformation_allowed=False,
        )
        try:
            trace(source, manifest, workspace / "rejected.svg", "colorset1")
        except vectorizer.VA.VectorizeError:
            pass
        else:
            raise AssertionError("Restricted source license was not rejected")

        print(
            json.dumps(
                {
                    "ok": True,
                    "pathCount": len(cs1_geometry),
                    "geometryLocked": True,
                    "deterministic": True,
                    "rightsRejected": True,
                },
                indent=2,
            )
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
