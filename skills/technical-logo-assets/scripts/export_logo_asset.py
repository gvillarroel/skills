#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Export one exact logo variant with provenance; optionally bake an adaptive color."""

from __future__ import annotations

import argparse
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path

from logo_svg import SVG_NS, VARIANTS, digest, inspect_vector, normalize_color
from sync_normalized_logos import LICENSE_FILES, asset_directory, safe_asset_path


def prepare_export(directory: Path, logo_id: str, variant: str, color: str | None = None) -> tuple[bytes, dict, bytes]:
    manifest = json.loads((directory / "logo_manifest.json").read_text(encoding="utf-8"))
    item = next((row for row in manifest["logos"] if row["id"] == logo_id), None)
    if item is None:
        raise ValueError(f"Unknown exact logo ID: {logo_id}")
    catalog = json.loads((directory / "logo_variants.json").read_text(encoding="utf-8"))
    row = next(row for row in catalog["logos"] if row["id"] == logo_id)
    record = row["variants"].get(variant)
    if record is None:
        raise ValueError(f"{logo_id} / {variant} unavailable: {row['unavailable'].get(variant, 'unknown-variant')}; choose one of {', '.join(row['variants'])}")
    payload = safe_asset_path(directory, record["assetPath"]).read_bytes()
    if digest(payload) != record["sha256"]:
        raise ValueError("Selected SVG hash does not match the variant catalog")
    inspect_vector(payload)
    root = ET.fromstring(payload)
    if root.get("data-logo-id") != logo_id or root.get("data-logo-variant") != variant:
        raise ValueError("Selected SVG has incorrect identity or variant markers")
    if color is not None:
        if variant != "adaptive" or not record["recolorable"]:
            raise ValueError("--color requires an available adaptive variant; source artwork is never recolored in place")
        if not re.fullmatch(r"#[0-9A-Fa-f]{3}(?:[0-9A-Fa-f]{3})?", color):
            raise ValueError("Color must be a literal #RGB or #RRGGBB value")
        color = normalize_color(color)
        for node in root.iter():
            for key, value in list(node.attrib.items()):
                if value.lower() == "currentcolor" and key in {"fill", "stroke", "color"}:
                    node.set(key, color)
            if node is root or node.tag == f"{{{SVG_NS}}}metadata":
                node.set("data-logo-variant", "custom-color")
                node.set("data-color-mode", "fixed-custom-color")
                node.set("data-recolorable", "false")
                node.set("data-color-value", color)
        root.find(f"{{{SVG_NS}}}title").text = f"{item['title']} — custom-color {color}"
        payload = ET.tostring(root, encoding="utf-8") + b"\n"
        inspect_vector(payload)
    if record["sourceRef"] == "original":
        source = {key: item[key] for key in ("sourceUrl", "sourceSha256", "sourceRepository", "sourceCommit", "sourcePath", "licenseId", "licenseUrl", "attribution")}
        for key in ("originalSource", "guidelines", "sourceArchiveMember", "sourceArchiveSha256", "artworkStatus", "identityMatch", "sourceNameAlias"):
            if key in item:
                source[key] = item[key]
    else:
        recipes = json.loads((directory / "logo_variant_sources.json").read_text(encoding="utf-8"))
        source = dict(recipes["sources"][record["sourceRef"]])
        source.pop("assetPath", None)
        source["sourceSha256"] = source.pop("sha256")
    metadata = {"schemaVersion": 1, "id": logo_id, "title": item["title"], "requestedVariant": variant,
                "variant": "custom-color" if color is not None else variant, "vectorOnly": True,
                "recolorable": variant == "adaptive" and color is None, "color": color,
                "svgSha256": digest(payload), "catalogSvgSha256": record["sha256"], "method": record["method"],
                "source": source, "trademarkNotice": "Copyright licensing does not grant trademark rights or imply endorsement."}
    if record["method"] == "pinned-provider-brand-color":
        recipes = json.loads((directory / "logo_variant_sources.json").read_text(encoding="utf-8"))
        metadata["brandColorSource"] = recipes["logos"][logo_id]["brandColorSource"]
    if color is not None:
        metadata["method"] = "baked-currentColor-from-adaptive"
    license_bytes = (directory / "licenses" / LICENSE_FILES[record["licenseId"]]).read_bytes()
    return payload, metadata, license_bytes


def export_one(directory: Path, logo_id: str, variant: str, output: Path, color: str | None = None, overwrite: bool = False) -> dict:
    output = output.resolve()
    if output.suffix.lower() != ".svg":
        raise ValueError("Output must have an .svg extension")
    if output.is_relative_to(Path(__file__).resolve().parents[1]) or output.is_relative_to(directory.resolve()):
        raise ValueError("Export outside the read-only skill bundle")
    payload, metadata, license_bytes = prepare_export(directory, logo_id, variant, color)
    outputs = {output: payload,
               output.with_suffix(".provenance.json"): (json.dumps(metadata, indent=2, ensure_ascii=False) + "\n").encode("utf-8"),
               output.with_suffix(".license.txt"): license_bytes}
    for path, content in outputs.items():
        if path.exists() and (not path.is_file() or (path.read_bytes() != content and not overwrite)):
            raise ValueError(f"Refusing to overwrite existing file: {path}")
    output.parent.mkdir(parents=True, exist_ok=True)
    for path, content in outputs.items():
        if not path.is_file() or path.read_bytes() != content:
            path.write_bytes(content)
    return {"ok": True, "id": logo_id, "variant": metadata["variant"], "svg": str(output),
            "provenance": str(output.with_suffix('.provenance.json')), "license": str(output.with_suffix('.license.txt'))}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--id", required=True)
    parser.add_argument("--variant", choices=VARIANTS, default="color")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--color", help="Bake #RGB or #RRGGBB into an adaptive variant for external-image consumers")
    parser.add_argument("--overwrite", action="store_true", help="Explicitly replace the selected export and its sidecars")
    args = parser.parse_args()
    try:
        result = export_one(asset_directory(), args.id, args.variant, args.output, args.color, args.overwrite)
    except (ValueError, KeyError, OSError, ET.ParseError) as error:
        parser.error(str(error))
    print(json.dumps(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
