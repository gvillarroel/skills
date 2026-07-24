#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "Pillow>=11.0,<13",
# ]
# ///
"""Validate open-image files against their provenance manifest."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys
from typing import Any
from urllib.parse import urlparse

from PIL import Image, UnidentifiedImageError


ASSET_ID_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
ALLOWED_LICENSES = {"Public-Domain", "CC0-1.0"}
ALLOWED_PREFIXES = ("CC-BY-", "CC-BY-SA-")
FORBIDDEN_LICENSE_TOKENS = ("-ND", "-NC")
MIME_BY_FORMAT = {
    "JPEG": "image/jpeg",
    "PNG": "image/png",
    "WEBP": "image/webp",
    "TIFF": "image/tiff",
}


class AssetValidationError(RuntimeError):
    """Raised when a base image or its rights record is invalid."""


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def license_allows_derivatives(value: str) -> bool:
    upper = value.upper()
    if any(token in upper for token in FORBIDDEN_LICENSE_TOKENS):
        return False
    return value in ALLOWED_LICENSES or value.startswith(ALLOWED_PREFIXES)


def require_https(value: Any, field: str, asset_id: str) -> str:
    if not isinstance(value, str) or urlparse(value).scheme != "https":
        raise AssetValidationError(
            f"{asset_id}: {field} must be an absolute HTTPS URL"
        )
    return value


def resolve_asset_path(manifest: Path, filename: Any, asset_id: str) -> Path:
    if not isinstance(filename, str) or not filename:
        raise AssetValidationError(f"{asset_id}: filename is missing")
    if Path(filename).name != filename:
        raise AssetValidationError(
            f"{asset_id}: filename must not contain directories"
        )
    base = manifest.parent.resolve()
    candidate = (base / filename).resolve()
    if candidate.parent != base:
        raise AssetValidationError(f"{asset_id}: filename escapes the asset folder")
    return candidate


def inspect_asset(manifest: Path, entry: dict[str, Any]) -> dict[str, Any]:
    asset_id = entry.get("id")
    if not isinstance(asset_id, str) or not ASSET_ID_RE.fullmatch(asset_id):
        raise AssetValidationError(
            "Every asset id must use lowercase hyphen-case"
        )
    path = resolve_asset_path(manifest, entry.get("filename"), asset_id)
    if not path.is_file():
        raise AssetValidationError(f"{asset_id}: image does not exist: {path}")

    license_name = entry.get("license")
    if not isinstance(license_name, str) or not license_allows_derivatives(
        license_name
    ):
        raise AssetValidationError(
            f"{asset_id}: license does not allow this transformation: "
            f"{license_name!r}"
        )
    if entry.get("transformation_allowed") is not True:
        raise AssetValidationError(
            f"{asset_id}: transformation_allowed must be true"
        )
    restrictions = entry.get("restrictions")
    if not isinstance(restrictions, str) or restrictions.strip():
        raise AssetValidationError(
            f"{asset_id}: restrictions must be present and empty"
        )
    require_https(entry.get("source_page"), "source_page", asset_id)
    require_https(entry.get("metadata_api_url"), "metadata_api_url", asset_id)
    require_https(entry.get("original_url"), "original_url", asset_id)
    require_https(entry.get("download_url"), "download_url", asset_id)
    require_https(entry.get("license_url"), "license_url", asset_id)
    for field in (
        "provider",
        "provider_id",
        "title",
        "creator",
        "date",
        "retrieved_at",
        "attribution",
    ):
        value = entry.get(field)
        if not isinstance(value, str) or not value.strip():
            raise AssetValidationError(f"{asset_id}: {field} is missing")
    if license_name.startswith("CC-BY-") and entry.get(
        "attribution_required"
    ) is not True:
        raise AssetValidationError(
            f"{asset_id}: CC BY material must require attribution"
        )
    if license_name.startswith("CC-BY-SA-") and entry.get("share_alike") is not True:
        raise AssetValidationError(
            f"{asset_id}: CC BY-SA material must retain ShareAlike"
        )

    expected_sha = entry.get("sha256")
    if not isinstance(expected_sha, str) or not SHA256_RE.fullmatch(expected_sha):
        raise AssetValidationError(f"{asset_id}: sha256 is malformed")
    actual_sha = sha256_path(path)
    if actual_sha != expected_sha:
        raise AssetValidationError(
            f"{asset_id}: SHA-256 mismatch ({actual_sha} != {expected_sha})"
        )
    actual_bytes = path.stat().st_size
    if entry.get("bytes") != actual_bytes:
        raise AssetValidationError(
            f"{asset_id}: byte count mismatch "
            f"({actual_bytes} != {entry.get('bytes')})"
        )

    try:
        with Image.open(path) as image:
            image.verify()
        with Image.open(path) as image:
            width, height = image.size
            detected_mime = MIME_BY_FORMAT.get(image.format or "", "")
    except (OSError, UnidentifiedImageError) as exc:
        raise AssetValidationError(
            f"{asset_id}: image cannot be decoded: {exc}"
        ) from exc
    if entry.get("width") != width or entry.get("height") != height:
        raise AssetValidationError(
            f"{asset_id}: dimensions mismatch "
            f"({width}x{height} != {entry.get('width')}x{entry.get('height')})"
        )
    if not detected_mime or entry.get("mime") != detected_mime:
        raise AssetValidationError(
            f"{asset_id}: MIME mismatch "
            f"({detected_mime!r} != {entry.get('mime')!r})"
        )

    return {
        "id": asset_id,
        "filename": path.name,
        "sha256": actual_sha,
        "bytes": actual_bytes,
        "width": width,
        "height": height,
        "mime": detected_mime,
        "license": license_name,
        "provider": entry.get("provider", ""),
    }


def inspect_manifest(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise AssetValidationError(f"Manifest does not exist: {path}")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise AssetValidationError(f"Cannot read manifest JSON: {exc}") from exc
    if payload.get("schema_version") != 1:
        raise AssetValidationError("Manifest schema_version must be 1")
    entries = payload.get("assets")
    if not isinstance(entries, list) or not entries:
        raise AssetValidationError("Manifest assets must be a nonempty array")

    results: list[dict[str, Any]] = []
    ids: set[str] = set()
    filenames: set[str] = set()
    for entry in entries:
        if not isinstance(entry, dict):
            raise AssetValidationError("Every asset entry must be an object")
        result = inspect_asset(path, entry)
        if result["id"] in ids:
            raise AssetValidationError(f"Duplicate asset id: {result['id']}")
        if result["filename"] in filenames:
            raise AssetValidationError(
                f"Duplicate asset filename: {result['filename']}"
            )
        ids.add(result["id"])
        filenames.add(result["filename"])
        results.append(result)
    return {
        "schema_version": 1,
        "ok": True,
        "manifest": str(path),
        "asset_count": len(results),
        "assets": results,
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
        description="Validate openly licensed base images and their manifest."
    )
    parser.add_argument("manifest", type=Path)
    parser.add_argument(
        "--output-report",
        type=Path,
        help="Optionally write this validation result as deterministic JSON.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    result = inspect_manifest(args.manifest.resolve())
    if args.output_report:
        write_json_atomic(args.output_report.resolve(), result)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AssetValidationError as exc:
        print(f"[vectorize-art-patterns] ERROR: {exc}", file=sys.stderr)
        raise SystemExit(2)
