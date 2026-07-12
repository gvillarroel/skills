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
import json
import shutil
import sys
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path


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
    if payload.get("schemaVersion") != 2:
        raise ValueError("Expected logo manifest schemaVersion 2")
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
    else:
        request = urllib.request.Request(
            item["sourceUrl"], headers={"User-Agent": "plantuml-logo-bundle-sync"}
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
    width = normalization["width"]
    height = normalization["height"]
    padding = normalization["padding"]
    inner_width = width - 2 * padding
    inner_height = height - 2 * padding
    mime = "image/png" if item["sourceFormat"] == "png" else "image/svg+xml"
    encoded = base64.b64encode(payload).decode("ascii")
    title = item["title"].replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    return (
        f'<svg xmlns="{SVG_NS}" role="img" width="{width}" height="{height}" '
        f'viewBox="{normalization["viewBox"]}" preserveAspectRatio="{normalization["preserveAspectRatio"]}">'
        f"<title>{title}</title>"
        f'<metadata data-logo-id="{item["id"]}" data-provider="{item["provider"]}" '
        f'data-source-sha256="{item["sourceSha256"]}" data-license="{item["licenseId"]}" />'
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
        "Every source file is pinned to a repository commit and SHA-256 in `logo_manifest.json`. The normalized SVG is a 256×256 technical container. It embeds the original licensed artwork bytes unchanged and centers them with `preserveAspectRatio=\"xMidYMid meet\"`; this avoids stretching and preserves CC-BY-ND artwork as an unmodified contribution in a collective bundle.",
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
        lines.append(
            f"| {provider} | {counts.get(provider, 0)} | [{repository}@`{commit}`]({repository}/tree/{commit}) | [{source['licenseId']}]({source['licenseUrl']}) | {source['attribution']} |"
        )
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
            "- Do not alter artwork marked CC-BY-ND-2.0; resize only through the outer SVG viewport or the consuming diagram.",
            "- Treat Devicon's MIT grant as a copyright license, not a trademark license.",
            "",
        ]
    )
    return "\n".join(lines)


def sync(directory: Path, manifest: dict, overrides: dict[str, Path]) -> None:
    directory.mkdir(parents=True, exist_ok=True)
    expected = {item["assetPath"] for item in manifest["logos"]}
    for stale in directory.rglob("*.svg"):
        if stale.relative_to(directory).as_posix() not in expected:
            stale.unlink()
    for item in manifest["logos"]:
        payload = source_bytes(item, overrides)
        target = directory / item["assetPath"]
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(
            wrapped_svg(item, payload, manifest["normalization"]),
            encoding="utf-8",
            newline="\n",
        )
    (directory / "license_log.md").write_text(
        license_log(manifest), encoding="utf-8", newline="\n"
    )


def validate(directory: Path, manifest: dict) -> list[str]:
    errors: list[str] = []
    expected = {item["assetPath"] for item in manifest["logos"]}
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
    return errors


def export(source: Path, destination: Path, manifest: dict) -> None:
    errors = validate(source, manifest)
    if errors:
        raise ValueError("Bundled logo assets are invalid: " + "; ".join(errors[:20]))
    if destination.exists():
        for stale in destination.rglob("*.svg"):
            stale.unlink()
    destination.mkdir(parents=True, exist_ok=True)
    for item in manifest["logos"]:
        target = destination / item["assetPath"]
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source / item["assetPath"], target)
    shutil.copy2(source / "license_log.md", destination / "license_log.md")
    shutil.copy2(source / "logo_manifest.json", destination / "logo_manifest.json")
    if (destination / "licenses").exists():
        shutil.rmtree(destination / "licenses")
    shutil.copytree(source / "licenses", destination / "licenses")


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
