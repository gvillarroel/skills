#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "numpy>=2.0",
#   "opencv-python-headless>=4.10",
#   "pillow>=11.0",
# ]
# ///
"""Run deterministic and adversarial smoke tests for the art vectorizer."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import sys
import tempfile
from typing import Any

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


vectorizer = load_module("vectorize_art", SCRIPT_DIR / "vectorize_art.py")
validator = load_module("validate_art_svg", SCRIPT_DIR / "validate_art_svg.py")
asset_validator = load_module(
    "validate_open_assets", SCRIPT_DIR / "validate_open_assets.py"
)
fetcher = load_module("fetch_open_image", SCRIPT_DIR / "fetch_open_image.py")


def sha256_path(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def make_fixture(path: Path) -> None:
    width, height = 240, 180
    image = Image.new("RGB", (width, height), "#eee2c7")
    draw = ImageDraw.Draw(image)
    upper: list[tuple[int, int]] = []
    lower: list[tuple[int, int]] = []
    for x in range(width):
        center = 62 + 17 * math.sin(x / 21.0) + 7 * math.sin(x / 7.0)
        upper.append((x, int(center - 22)))
        lower.append((x, int(center + 24)))
    draw.polygon(upper + list(reversed(lower)), fill="#395f76")
    draw.ellipse((48, 72, 142, 162), fill="#bd6b51")
    draw.ellipse((82, 92, 178, 176), fill="#e0b84f")
    for offset in range(-18, 19, 6):
        points = [
            (
                x,
                int(128 + offset + 12 * math.sin((x + offset * 2) / 15.0)),
            )
            for x in range(width)
        ]
        draw.line(points, fill="#383431", width=2)
    image.save(path, format="PNG")


def write_manifest(path: Path, image_path: Path, license_name: str) -> None:
    with Image.open(image_path) as image:
        width, height = image.size
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
                "id": "synthetic-organic-fixture",
                "filename": image_path.name,
                "provider": "local-test",
                "provider_id": "synthetic-organic-fixture",
                "title": "Synthetic organic fixture",
                "creator": "vectorize-art-patterns test suite",
                "date": "2026",
                "metadata_api_url": "https://example.invalid/api/synthetic-fixture",
                "original_url": "https://example.invalid/synthetic-fixture.png",
                "download_url": "https://example.invalid/synthetic-fixture.png",
                "retrieved_at": "2026-01-01T00:00:00+00:00",
                "license": license_name,
                "license_url": "https://creativecommons.org/publicdomain/mark/1.0/",
                "usage_terms": "Public domain",
                "source_page": "https://example.invalid/synthetic-fixture",
                "attribution": "Deterministic local test fixture",
                "attribution_required": False,
                "share_alike": False,
                "restrictions": "",
                "transformation_allowed": True,
                "mime": "image/png",
                "width": width,
                "height": height,
                "bytes": image_path.stat().st_size,
                "sha256": sha256_path(image_path),
            }
        ],
    }
    path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def run_vectorizer(
    workspace: Path,
    manifest: Path,
    mode: str,
    tile: str,
    colorset: str | None,
    suffix: str = "",
) -> tuple[Path, dict[str, Any]]:
    output = workspace / f"{mode}-{tile}{suffix}.svg"
    report = workspace / f"{mode}-{tile}{suffix}.json"
    pattern_id = f"test-{mode}-{tile}-{colorset or 'source'}"
    argv = [
        str(workspace / "source.png"),
        str(output),
        "--mode",
        mode,
        "--tile",
        tile,
        "--max-dimension",
        "240",
        "--min-area",
        "8",
        "--pattern-id",
        pattern_id,
        "--source-manifest",
        str(manifest),
        "--source-id",
        "synthetic-organic-fixture",
        "--report",
        str(report),
    ]
    if colorset:
        argv.extend(["--colorset", colorset])
    args = vectorizer.apply_mode_defaults(vectorizer.build_parser().parse_args(argv))
    vector_report = vectorizer.vectorize(args)
    validation_args = validator.build_parser().parse_args(
        [
            str(output),
            "--report",
            str(report),
            "--expected-pattern-id",
            pattern_id,
            "--expected-mode",
            mode,
            "--expected-tile",
            tile,
            "--expected-colorset",
            colorset or "source",
            *(["--require-pattern"] if tile != "none" else []),
        ]
    )
    validation = validator.validate_against_args(
        validator.inspect_svg(output), validation_args
    )
    if not validation["ok"]:
        raise RuntimeError(f"Validation failed for {mode}/{tile}")
    if colorset:
        contract = vectorizer.load_colorset_contract()
        allowed = set(contract["colorsets"][colorset]["allowed"])
        unexpected = sorted(set(vector_report["palette"]) - allowed)
        if unexpected:
            raise RuntimeError(
                f"{colorset} output used disallowed colors: {unexpected}"
            )
        if validation["unexpected_color_tokens"]:
            raise RuntimeError(
                f"{colorset} validator reported unexpected color tokens"
            )
    return output, vector_report


def assert_rejected_license(workspace: Path, image: Path) -> None:
    bad_manifest = workspace / "bad-manifest.json"
    write_manifest(bad_manifest, image, "CC-BY-ND-4.0")
    try:
        vectorizer.validate_rights(
            input_path=image,
            source_manifest=bad_manifest,
            source_id="synthetic-organic-fixture",
            rights_basis=None,
            source_url=None,
        )
    except vectorizer.VectorizeError:
        return
    raise RuntimeError("NoDerivatives manifest was not rejected")


def assert_asset_manifest_checks(workspace: Path, manifest: Path) -> None:
    validation = asset_validator.inspect_manifest(manifest)
    if not validation["ok"] or validation["asset_count"] != 1:
        raise RuntimeError("Valid open-image manifest did not pass validation")

    tampered_manifest = workspace / "tampered-manifest.json"
    payload = json.loads(manifest.read_text(encoding="utf-8"))
    payload["assets"][0]["sha256"] = "0" * 64
    tampered_manifest.write_text(
        json.dumps(payload, indent=2) + "\n",
        encoding="utf-8",
    )
    try:
        asset_validator.inspect_manifest(tampered_manifest)
    except asset_validator.AssetValidationError:
        pass
    else:
        raise RuntimeError("Tampered base-image hash was not rejected")

    for license_name, license_url in (
        ("CC BY-NC 4.0", "https://creativecommons.org/licenses/by-nc/4.0/"),
        ("CC BY-ND 4.0", "https://creativecommons.org/licenses/by-nd/4.0/"),
    ):
        try:
            fetcher.canonical_license(license_name, license_url, license_name)
        except fetcher.FetchError:
            continue
        raise RuntimeError(f"Restricted license was not rejected: {license_name}")


def assert_user_owned_path(workspace: Path) -> None:
    output = workspace / "user-owned-organic.svg"
    report_path = workspace / "user-owned-organic.json"
    args = vectorizer.apply_mode_defaults(
        vectorizer.build_parser().parse_args(
            [
                str(workspace / "source.png"),
                str(output),
                "--mode",
                "organic",
                "--max-dimension",
                "200",
                "--min-area",
                "8",
                "--pattern-id",
                "test-user-owned-organic",
                "--rights-basis",
                "user-owned",
                "--report",
                str(report_path),
            ]
        )
    )
    report = vectorizer.vectorize(args)
    if report.get("rights", {}).get("basis") != "user-owned":
        raise RuntimeError("User-owned rights basis was not preserved")
    validation_args = validator.build_parser().parse_args(
        [
            str(output),
            "--report",
            str(report_path),
            "--expected-pattern-id",
            "test-user-owned-organic",
            "--expected-mode",
            "organic",
            "--expected-tile",
            "none",
        ]
    )
    validator.validate_against_args(validator.inspect_svg(output), validation_args)


def run_tests() -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="vectorize-art-patterns-") as temp:
        workspace = Path(temp)
        source = workspace / "source.png"
        manifest = workspace / "manifest.json"
        make_fixture(source)
        write_manifest(manifest, source, "Public-Domain")

        cases = [
            ("organic", "mirror", "colorset1"),
            ("ink", "none", "colorset2"),
            ("stain", "repeat", "colorset2"),
            ("collage", "none", "colorset1"),
        ]
        results: list[dict[str, Any]] = []
        for mode, tile, colorset in cases:
            output, report = run_vectorizer(
                workspace, manifest, mode, tile, colorset
            )
            results.append(
                {
                    "mode": mode,
                    "tile": tile,
                    "colorset": colorset,
                    "sha256": sha256_path(output),
                    "palette": report["palette"],
                    "path_count": report["path_count"],
                    "contour_count": report["contour_count"],
                }
            )

        first, _ = run_vectorizer(
            workspace,
            manifest,
            "organic",
            "mirror",
            "colorset1",
            "-determinism-a",
        )
        second, _ = run_vectorizer(
            workspace,
            manifest,
            "organic",
            "mirror",
            "colorset1",
            "-determinism-b",
        )
        if first.read_bytes() != second.read_bytes():
            raise RuntimeError("Identical vectorization inputs were not deterministic")
        assert_rejected_license(workspace, source)
        assert_asset_manifest_checks(workspace, manifest)
        assert_user_owned_path(workspace)

        return {
            "ok": True,
            "cases": results,
            "deterministic_repeat": True,
            "no_derivatives_rejected": True,
            "tampered_asset_rejected": True,
            "noncommercial_rejected": True,
            "user_owned_path": True,
            "colorset1_safe": True,
            "colorset2_safe": True,
        }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run deterministic vectorize-art-patterns smoke tests."
    )
    parser.add_argument("--json", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    result = run_tests()
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(
            "PASS: 4 modes, two colorsets, deterministic repeat, rights "
            "rejection, and asset-integrity checks"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
