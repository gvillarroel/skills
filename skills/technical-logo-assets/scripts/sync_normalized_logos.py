#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Generate, export, and validate the manifest-driven normalized SVG logo bundle."""

from __future__ import annotations

import argparse
import base64
import hashlib
import html
import io
import json
import shutil
import sys
import urllib.request
import xml.etree.ElementTree as ET
import zipfile
from functools import lru_cache
from pathlib import Path

from logo_svg import inspect_vector


SVG_NS = "http://www.w3.org/2000/svg"
XLINK_NS = "http://www.w3.org/1999/xlink"
MINIMUM_LOGOS = 400
REQUIRED_PROVIDERS = {
    "AWS",
    "GCP",
    "Devicon",
    "Simple Icons",
    "Font Awesome Brands",
    "Ollama",
    "Pi Coding Agent",
    "OpenCode",
    "Cline",
    "Roo Code",
    "Continue",
    "Aider",
    "Goose",
    "OpenHands",
    "SWE-agent",
    "Qwen Code",
    "Oh My Pi",
    "Gemini CLI",
    "Lobe Icons",
}
LICENSE_FILES = {
    "Apache-2.0": "Apache-2.0.txt",
    "BSD-3-Clause": "BSD-3-Clause.txt",
    "CC0-1.0": "CC0-1.0.txt",
    "CC-BY-3.0": "CC-BY-3.0.txt",
    "CC-BY-4.0": "CC-BY-4.0.txt",
    "CC-BY-ND-2.0": "CC-BY-ND-2.0.txt",
    "MIT": "MIT.txt",
}


def skill_root() -> Path:
    return Path(__file__).resolve().parents[1]


def asset_directory() -> Path:
    return skill_root() / "assets" / "logos"


def manifest_path() -> Path:
    return asset_directory() / "logo_manifest.json"


def load_manifest(path: Path | None = None) -> dict:
    target = path or manifest_path()
    payload = json.loads(target.read_text(encoding="utf-8"))
    if payload.get("schemaVersion") != 3 or payload.get("vectorOnly") is not True:
        raise ValueError("Expected vector-only logo manifest schemaVersion 3")
    logos = payload.get("logos", [])
    if payload.get("logoCount") != len(logos) or len(logos) < MINIMUM_LOGOS:
        raise ValueError(f"Logo manifest must contain at least {MINIMUM_LOGOS} entries")
    ids = [item["id"] for item in logos]
    if len(ids) != len(set(ids)):
        raise ValueError("Logo manifest IDs must be unique")
    providers = {item["provider"] for item in logos}
    if not REQUIRED_PROVIDERS.issubset(providers):
        raise ValueError(f"Logo manifest must contain providers {sorted(REQUIRED_PROVIDERS)}")
    return payload


EXTRA_MANIFESTS = ("vector_source_lock.json", "logo_variants.json", "logo_variant_sources.json")


def safe_asset_path(directory: Path, relative: str) -> Path:
    path = Path(relative)
    if path.is_absolute() or ".." in path.parts or "\\" in relative:
        raise ValueError(f"Unsafe asset path: {relative}")
    target = (directory / path).resolve()
    if not target.is_relative_to(directory.resolve()):
        raise ValueError(f"Asset escapes the catalog: {relative}")
    return target


def registered_paths(directory: Path, manifest: dict) -> set[str]:
    paths = {item["assetPath"] for item in manifest["logos"]}
    variants_path = directory / "logo_variants.json"
    if variants_path.is_file():
        variants = json.loads(variants_path.read_text(encoding="utf-8"))
        paths.update(variant["assetPath"] for row in variants["logos"] for variant in row["variants"].values())
    recipes_path = directory / "logo_variant_sources.json"
    if recipes_path.is_file():
        recipes = json.loads(recipes_path.read_text(encoding="utf-8"))
        paths.update(source["assetPath"] for source in recipes["sources"].values())
    for relative in paths:
        safe_asset_path(directory, relative)
    return paths


@lru_cache(maxsize=4)
def archive_bytes(url: str, expected_sha256: str) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": "technical-logo-assets-sync"})
    with urllib.request.urlopen(request, timeout=60) as response:
        payload = response.read()
    if hashlib.sha256(payload).hexdigest() != expected_sha256:
        raise ValueError("Source archive SHA-256 mismatch")
    return payload


def parse_source_overrides(values: list[str]) -> dict[str, Path]:
    result: dict[str, Path] = {}
    for value in values:
        if "=" not in value:
            raise ValueError("--source must use provider=directory")
        provider, directory = value.split("=", 1)
        result[provider.lower()] = Path(directory)
    return result


def source_bytes(item: dict, overrides: dict[str, Path]) -> bytes:
    key = item["provider"].lower()
    if key in overrides:
        payload = (overrides[key] / item["sourcePath"]).read_bytes()
    elif item.get("sourceArchiveMember"):
        archive = archive_bytes(item["sourceUrl"], item["sourceArchiveSha256"])
        with zipfile.ZipFile(io.BytesIO(archive)) as bundle:
            payload = bundle.read(item["sourceArchiveMember"])
    else:
        request = urllib.request.Request(
            item["sourceUrl"], headers={"User-Agent": "technical-logo-assets-sync"}
        )
        with urllib.request.urlopen(request, timeout=45) as response:
            payload = response.read()
    digest = hashlib.sha256(payload).hexdigest()
    if digest != item["sourceSha256"]:
        raise ValueError(
            f"SHA-256 mismatch for {item['id']}: expected {item['sourceSha256']}, got {digest}"
        )
    return payload


def wrapped_svg(item: dict, payload: bytes, normalization: dict) -> str:
    if item["sourceFormat"] != "svg":
        raise ValueError("Raster-backed SVG wrappers are forbidden; supply a true vector source")
    inspect_vector(payload)
    width = normalization["width"]
    height = normalization["height"]
    padding = normalization["padding"]
    inner_width = width - 2 * padding
    inner_height = height - 2 * padding
    mime = "image/svg+xml"
    encoded = base64.b64encode(payload).decode("ascii")
    title = item["title"].replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    return (
        f'<svg xmlns="{SVG_NS}" role="img" width="{width}" height="{height}" '
        f'viewBox="{normalization["viewBox"]}" preserveAspectRatio="{normalization["preserveAspectRatio"]}" '
        f'data-logo-id="{html.escape(item["id"], quote=True)}" data-logo-variant="original" data-vector-only="true" data-recolorable="false">'
        f"<title>{title}</title>"
        f'<metadata data-logo-id="{item["id"]}" data-provider="{item["provider"]}" '
        f'data-source-sha256="{item["sourceSha256"]}" data-license="{item["licenseId"]}" '
        f'data-logo-variant="original" data-vector-only="true" />'
        f'<image x="{padding}" y="{padding}" width="{inner_width}" height="{inner_height}" '
        f'preserveAspectRatio="xMidYMid meet" href="data:{mime};base64,{encoded}" />'
        "</svg>\n"
    )


def license_log(manifest: dict) -> str:
    counts: dict[str, int] = {}
    for item in manifest["logos"]:
        counts[item["provider"]] = counts.get(item["provider"], 0) + 1
    lines = [
        "# Logo asset license log",
        "",
        f"This bundle contains **{manifest['logoCount']} unique technical logos**: "
        + ", ".join(f"{provider} {count}" for provider, count in sorted(counts.items()))
        + ".",
        "",
        "Every original source is pinned to a repository commit or release archive and a SHA-256 in `logo_manifest.json`. All original wrappers embed actual vector SVG bytes, never PNG/JPEG pixels, and use a 256×256 viewport with centered meet scaling. Release archives have both archive and member hashes. Historical artwork is explicitly marked; a verified source identity does not imply that the mark is the owner's latest branding.",
        "",
        "Variant filenames and SVG metadata distinguish original, color, grayscale, mono-black, mono-white, and adaptive. `logo_variants.json` records exact availability, hashes, transformation methods, and source IDs. `logo_variant_sources.json` records alternate-source attribution and licensing. Files in `sources/` are internal unmodified source snapshots, not normalized selection targets. Derived variants are not represented as owner-approved artwork. No modified CC-BY-ND variants are generated.",
        "",
        "Copyright licenses do not grant trademark rights or imply endorsement. Use marks truthfully, follow current owner brand policies, and obtain additional permission when a planned use goes beyond referential technical diagrams.",
        "",
        "## Source collections",
        "",
        "| Provider | Count | Repository and pinned commit | License | Attribution |",
        "| --- | ---: | --- | --- | --- |",
    ]
    for key, source in manifest["sources"].items():
        provider = source["provider"]
        repository = source["repository"]
        commit = source["commit"]
        count = sum(item["sourceRepository"] == repository and item["sourceCommit"] == commit for item in manifest["logos"])
        link = f"{repository}/tree/{commit}" if repository.startswith("https://github.com/") else repository
        lines.append(f"| {provider} | {count} | [{repository}@`{commit}`]({link}) | [{source['licenseId']}]({source['licenseUrl']}) | {source['attribution']} |")
    lines.extend(
        [
            "",
            "## Per-logo provenance",
            "",
        "| File | Title | Provider/category | License | Original pinned source | Artwork source | Guidelines | Source SHA-256 |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
        ]
    )
    for item in manifest["logos"]:
        lines.append(
            f"| `{item['assetPath']}` | {item['title']} | {item['provider']} / {item['category']} | [{item['licenseId']}]({item['licenseUrl']}) | [source]({item['sourceUrl']}) | {item.get('originalSource') or 'Not supplied'} | {item.get('guidelines') or 'Not supplied'} | `{item['sourceSha256']}` |"
        )
    lines.extend(
        [
            "",
            "## Redistribution requirements",
            "",
            "- Keep this file and `logo_manifest.json` with exported assets.",
            "- Keep the complete source license texts in `licenses/`.",
            "- Keep `logo_variants.json` and `logo_variant_sources.json` with exported variants; they distinguish derived artwork and source-specific attribution.",
            "- Do not alter artwork marked CC-BY-ND-2.0; resize only through the outer SVG viewport or the consuming diagram.",
            "- Treat Devicon's MIT grant as a copyright license, not a trademark license.",
            "",
        ]
    )
    return "\n".join(lines)


def sync(directory: Path, manifest: dict, overrides: dict[str, Path]) -> None:
    directory.mkdir(parents=True, exist_ok=True)
    # Preserve unknown files. Validation reports stale inventory instead of deleting it.
    for item in manifest["logos"]:
        payload = source_bytes(item, overrides)
        target = safe_asset_path(directory, item["assetPath"])
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(
            wrapped_svg(item, payload, manifest["normalization"]),
            encoding="utf-8",
            newline="\n",
        )
    (directory / "license_log.md").write_text(
        license_log(manifest), encoding="utf-8", newline="\n"
    )
    if directory.resolve() != asset_directory().resolve():
        original_paths = {item["assetPath"] for item in manifest["logos"]}
        for relative in registered_paths(asset_directory(), manifest) - original_paths:
            target = safe_asset_path(directory, relative)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(safe_asset_path(asset_directory(), relative), target)
        for name in EXTRA_MANIFESTS + ("logo_manifest.json",):
            if (asset_directory() / name).is_file():
                shutil.copy2(asset_directory() / name, directory / name)
        shutil.copytree(asset_directory() / "licenses", directory / "licenses", dirs_exist_ok=True)


def validate(directory: Path, manifest: dict) -> list[str]:
    errors: list[str] = []
    try:
        expected = registered_paths(directory, manifest)
    except (ValueError, KeyError, TypeError) as error:
        return [str(error)]
    actual = {path.relative_to(directory).as_posix() for path in directory.rglob("*.svg")}
    if actual != expected:
        errors.append(
            f"SVG inventory mismatch: expected {len(expected)}, got {len(actual)}; missing={len(expected-actual)}, extra={len(actual-expected)}"
        )
    normalization = manifest["normalization"]
    for item in manifest["logos"]:
        path = directory / item["assetPath"]
        if not path.is_file():
            continue
        try:
            root = ET.parse(path).getroot()
        except ET.ParseError as error:
            errors.append(f"{path.name}: invalid XML: {error}")
            continue
        required = {
            "width": str(normalization["width"]),
            "height": str(normalization["height"]),
            "viewBox": normalization["viewBox"],
            "preserveAspectRatio": normalization["preserveAspectRatio"],
        }
        for attribute, expected_value in required.items():
            if root.get(attribute) != expected_value:
                errors.append(f"{path.name}: invalid {attribute}")
        metadata = root.find(f"{{{SVG_NS}}}metadata")
        image = root.find(f"{{{SVG_NS}}}image")
        title = root.find(f"{{{SVG_NS}}}title")
        if metadata is None or metadata.get("data-logo-id") != item["id"]:
            errors.append(f"{path.name}: invalid metadata")
        if title is None or title.text != item["title"]:
            errors.append(f"{path.name}: invalid title")
        if image is None:
            errors.append(f"{path.name}: missing embedded source image")
            continue
        href = image.get("href") or image.get(f"{{{XLINK_NS}}}href") or ""
        try:
            encoded = href.split(";base64,", 1)[1]
            embedded = base64.b64decode(encoded, validate=True)
        except (IndexError, ValueError):
            errors.append(f"{path.name}: invalid embedded data URI")
            continue
        if hashlib.sha256(embedded).hexdigest() != item["sourceSha256"]:
            errors.append(f"{path.name}: embedded source SHA-256 mismatch")
        if item.get("sourceFormat") != "svg" or item.get("vectorOnly") is not True:
            errors.append(f"{path.name}: source is not declared vector-only")
        try:
            inspect_vector(path.read_bytes())
        except ValueError as error:
            errors.append(f"{path.name}: {error}")
        if root.get("data-logo-variant") != "original" or root.get("data-vector-only") != "true":
            errors.append(f"{path.name}: original variant markers are missing")
        for attribute, value in {"x": "16", "y": "16", "width": "224", "height": "224", "preserveAspectRatio": "xMidYMid meet"}.items():
            if image.get(attribute) != value:
                errors.append(f"{path.name}: invalid normalized image {attribute}")
    log = directory / "license_log.md"
    if not log.is_file() or log.read_text(encoding="utf-8") != license_log(manifest):
        errors.append("license_log.md is missing or out of sync")
    licenses = directory / "licenses"
    required_license_files = {
        LICENSE_FILES[item["licenseId"]]
        for item in manifest["logos"]
        if item["licenseId"] in LICENSE_FILES
    }
    for name in required_license_files:
        if not (licenses / name).is_file():
            errors.append(f"licenses/{name} is missing")
    if manifest.get("schemaVersion") == 3:
        from build_logo_variants import validate_variants
        errors.extend(validate_variants(directory, manifest))
    return errors


def export(source: Path, destination: Path, manifest: dict) -> None:
    errors = validate(source, manifest)
    if errors:
        raise ValueError("Bundled logo assets are invalid: " + "; ".join(errors[:20]))
    source, destination = source.resolve(), destination.resolve()
    if source == destination or source.is_relative_to(destination) or destination.is_relative_to(source):
        raise ValueError("Export destination must be separate from the source bundle")
    if destination.exists() and any(destination.iterdir()):
        raise ValueError("Export destination must be new or empty; no existing files were removed")
    destination.mkdir(parents=True, exist_ok=True)
    for relative in registered_paths(source, manifest):
        target = safe_asset_path(destination, relative)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(safe_asset_path(source, relative), target)
    shutil.copy2(source / "license_log.md", destination / "license_log.md")
    shutil.copy2(source / "logo_manifest.json", destination / "logo_manifest.json")
    shutil.copytree(source / "licenses", destination / "licenses")
    for name in EXTRA_MANIFESTS:
        if (source / name).is_file():
            shutil.copy2(source / name, destination / name)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--output", type=Path, default=asset_directory())
    parser.add_argument("--export", type=Path)
    parser.add_argument(
        "--source",
        action="append",
        default=[],
        metavar="PROVIDER=DIRECTORY",
        help="Read pinned source files from a local clone instead of the network",
    )
    args = parser.parse_args()
    manifest = load_manifest()
    overrides = parse_source_overrides(args.source)
    if args.export:
        export(asset_directory(), args.export, manifest)
        errors = validate(args.export, manifest)
        output = args.export
    else:
        if not args.check:
            sync(args.output, manifest, overrides)
        errors = validate(args.output, manifest)
        output = args.output
    if errors:
        for error in errors[:100]:
            print(f"ERROR: {error}", file=sys.stderr)
        if len(errors) > 100:
            print(f"ERROR: {len(errors)-100} additional errors omitted", file=sys.stderr)
        return 1
    print(f"Validated {manifest['logoCount']} normalized SVG logos in {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
