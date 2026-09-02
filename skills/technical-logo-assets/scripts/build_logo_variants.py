#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Build and verify labeled SVG variants offline from pinned, in-bundle sources."""

from __future__ import annotations

import argparse
import json
import re
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path
from urllib.parse import quote

from logo_svg import (PERMISSIVE_LICENSES, SVG_NS, VARIANTS, digest, embedded_source,
                      inspect_vector, local_name, monochrome_root, normalize_color,
                      painted_variant, palette_kind, wrapped_variant)
from sync_normalized_logos import asset_directory, load_manifest, safe_asset_path


def compact_json(value: dict) -> bytes:
    return (json.dumps(value, ensure_ascii=False, separators=(",", ":")) + "\n").encode("utf-8")


def read_originals(directory: Path, manifest: dict) -> dict[str, bytes]:
    originals = {}
    for item in manifest["logos"]:
        payload = embedded_source(safe_asset_path(directory, item["assetPath"]).read_bytes())
        if digest(payload) != item["sourceSha256"]:
            raise ValueError(f"Original source hash mismatch: {item['id']}")
        inspect_vector(payload)
        originals[item["id"]] = payload
    return originals


def source_url(repository: str, commit: str, relative: str) -> str:
    return f"https://raw.githubusercontent.com/{repository.removeprefix('https://github.com/')}/{commit}/{quote(relative, safe='/')}"


def prepare_recipes(manifest: dict, originals: dict[str, bytes], sources: Path) -> tuple[dict, dict[str, bytes]]:
    recipes = {"schemaVersion": 1, "policyVersion": 1, "sources": {}, "logos": {}}
    snapshots: dict[str, bytes] = {}
    simple_path = sources / "simpleicons/data/simple-icons.json"
    simple_bytes = simple_path.read_bytes()
    simple_data = json.loads(simple_bytes)
    simple_by_title = {item["title"]: item for item in simple_data}
    simple_source = manifest["sources"]["simpleicons"]
    color_metadata = {"sourceUrl": source_url(simple_source["repository"], simple_source["commit"], "data/simple-icons.json"),
                      "sourceSha256": digest(simple_bytes), "field": "hex"}

    def snapshot(item: dict, path: Path, root: Path, source: dict) -> str:
        payload = path.read_bytes()
        inspect_vector(payload)
        sha = digest(payload)
        if sha == item["sourceSha256"]:
            return "original"
        relative = path.relative_to(root).as_posix()
        asset_path = f"sources/{sha}.source.svg"
        record = {"assetPath": asset_path, "sha256": sha, "sourceUrl": source_url(source["repository"], source["commit"], relative),
                  "sourceRepository": source["repository"], "sourceCommit": source["commit"], "sourcePath": relative,
                  "licenseId": source["licenseId"], "licenseUrl": source["licenseUrl"], "attribution": source["attribution"]}
        if sha in recipes["sources"] and recipes["sources"][sha]["licenseId"] != record["licenseId"]:
            raise ValueError("Identical alternate artwork has conflicting licenses")
        recipes["sources"].setdefault(sha, record)
        snapshots[asset_path] = payload
        return sha

    for item in manifest["logos"]:
        recipe = {"originalSha256": item["sourceSha256"], "colorSource": "original"}
        mono_candidates: list[tuple[Path, Path, dict]] = []
        if item["provider"] == "Devicon":
            root = sources / "devicon"
            source = manifest["sources"]["devicon"]
            path = root / item["sourcePath"]
            stem = re.sub(r"-(?:original|plain|line)(?:-wordmark)?$", "", path.stem)
            suffix = "-wordmark" if path.stem.endswith("-wordmark") else ""
            mono_candidates = [(path.with_name(f"{stem}-{mode}{suffix}.svg"), root, source) for mode in ("plain", "line")]
        elif item["provider"] == "Lobe Icons" or item["id"] in {"code-assistant-opencode", "code-assistant-gemini-cli"}:
            root = sources / "lobe-icons"
            source = manifest["sources"]["lobe-icons"]
            stem = {"code-assistant-opencode": "opencode", "code-assistant-gemini-cli": "geminicli"}.get(item["id"], Path(item["sourcePath"]).stem)
            stem = stem.removesuffix("-color")
            parent = root / "packages/static-svg/icons"
            color = parent / f"{stem}-color.svg"
            if color.is_file():
                recipe["colorSource"] = snapshot(item, color, root, source)
            mono_candidates = [(parent / f"{stem}{suffix}.svg", root, source) for suffix in ("", "-mono")]
        if item["provider"] == "Simple Icons":
            record = simple_by_title.get(item["title"])
            if not record or not re.fullmatch(r"[0-9A-Fa-f]{6}", record.get("hex", "")):
                raise ValueError(f"Missing exact-title brand color metadata: {item['id']}")
            recipe["brandColor"] = "#" + record["hex"].lower()
            recipe["brandColorSource"] = {**color_metadata, "title": record["title"]}
        for path, root, source in mono_candidates:
            if not path.is_file():
                continue
            try:
                monochrome_root(path.read_bytes())
            except ValueError:
                continue
            recipe["monochromeSource"] = snapshot(item, path, root, source)
            break
        if "monochromeSource" not in recipe:
            try:
                monochrome_root(originals[item["id"]])
                recipe["monochromeSource"] = "original"
            except ValueError:
                pass
        recipes["logos"][item["id"]] = recipe
    return recipes, snapshots


def read_snapshots(directory: Path, recipes: dict) -> dict[str, bytes]:
    snapshots = {}
    for sha, source in recipes["sources"].items():
        payload = safe_asset_path(directory, source["assetPath"]).read_bytes()
        if sha != source["sha256"] or digest(payload) != sha:
            raise ValueError(f"Alternate source hash mismatch: {source['assetPath']}")
        inspect_vector(payload)
        snapshots[source["assetPath"]] = payload
    return snapshots


def native_single_paint(payload: bytes) -> str | None:
    """Identify a genuinely unmodified all-black/all-white source for ND licenses."""
    try:
        root = monochrome_root(payload)
    except ValueError:
        return None
    paints: set[str] = set()

    def visit(node: ET.Element, fill: str = "#000000", stroke: str = "none", color: str = "#000000", clipped: bool = False) -> None:
        fill, stroke, color = node.get("fill", fill), node.get("stroke", stroke), node.get("color", color)
        clipped |= local_name(node.tag) == "clipPath"
        if local_name(node.tag) in {"path", "rect", "circle", "ellipse", "line", "polygon", "polyline", "use"} and not clipped:
            for paint in (fill, stroke):
                value = normalize_color(color if normalize_color(paint) == "currentcolor" else paint)
                if value not in {"none", "transparent"}:
                    paints.add(value)
        for child in node:
            visit(child, fill, stroke, color, clipped)

    visit(root)
    return next(iter(paints)) if len(paints) == 1 else None


def add_grayscale(payload: bytes, logo_id: str) -> bytes:
    """Filter the normalized vector at render size without double-padding its geometry."""
    root = ET.fromstring(payload)
    root.set("data-logo-variant", "grayscale")
    root.set("data-color-mode", "grayscale")
    root.find(f"{{{SVG_NS}}}title").text = root.find(f"{{{SVG_NS}}}title").text.rsplit(" — ", 1)[0] + " — grayscale"
    metadata = root.find(f"{{{SVG_NS}}}metadata")
    metadata.set("data-logo-variant", "grayscale")
    metadata.set("data-color-mode", "grayscale")
    filter_id = "gray-" + digest(logo_id.encode())[:16]
    defs = ET.SubElement(root, f"{{{SVG_NS}}}defs")
    effect = ET.SubElement(defs, f"{{{SVG_NS}}}filter", {"id": filter_id, "color-interpolation-filters": "sRGB"})
    ET.SubElement(effect, f"{{{SVG_NS}}}feColorMatrix", {"type": "saturate", "values": "0"})
    group = ET.SubElement(root, f"{{{SVG_NS}}}g", {"filter": f"url(#{filter_id})"})
    for node in list(root):
        if node is not group and local_name(node.tag) not in {"metadata", "title", "defs", "desc"}:
            root.remove(node)
            group.append(node)
    return ET.tostring(root, encoding="utf-8") + b"\n"


def render_catalog(directory: Path, manifest: dict, recipes: dict, originals: dict[str, bytes], snapshots: dict[str, bytes]) -> tuple[dict, dict[str, bytes]]:
    if recipes.get("schemaVersion") != 1 or recipes.get("policyVersion") != 1:
        raise ValueError("Unsupported variant recipe schema or policy")
    if set(recipes["logos"]) != {item["id"] for item in manifest["logos"]}:
        raise ValueError("Variant recipe IDs do not match the identity catalog")
    catalog = {"schemaVersion": 1, "policyVersion": 1, "logoCount": len(manifest["logos"]), "variantKinds": list(VARIANTS), "logos": []}
    files = {}
    coverage: Counter[str] = Counter()
    for item in manifest["logos"]:
        recipe = recipes["logos"][item["id"]]
        if recipe["originalSha256"] != item["sourceSha256"]:
            raise ValueError(f"Stale variant recipe: {item['id']}")
        row = {"id": item["id"], "defaultVariant": "color", "variants": {}, "unavailable": {}}

        def resolve(ref: str) -> tuple[bytes, dict]:
            if ref == "original":
                return originals[item["id"]], item
            record = recipes["sources"][ref]
            return snapshots[record["assetPath"]], record

        def add(kind: str, payload: bytes, ref: str, method: str, palette: str, source: dict) -> None:
            relative = item["assetPath"] if kind == "original" else str(Path(item["assetPath"]).with_suffix(f".{kind}.svg")).replace("\\", "/")
            inspect_vector(payload)
            files[relative] = payload
            row["variants"][kind] = {"assetPath": relative, "sha256": digest(payload), "sourceRef": ref,
                "sourceSha256": item["sourceSha256"] if ref == "original" else ref, "method": method,
                "paletteKind": palette, "licenseId": source["licenseId"], "recolorable": kind == "adaptive"}
            coverage[kind] += 1

        original_file = safe_asset_path(directory, item["assetPath"]).read_bytes()
        add("original", original_file, "original", "unmodified-source", palette_kind(originals[item["id"]]), item)
        color_ref = recipe["colorSource"]
        color_source, color_provenance = resolve(color_ref)
        color_item = {**item, "licenseId": color_provenance["licenseId"]}
        color_palette = palette_kind(color_source)
        if recipe.get("brandColor"):
            if color_provenance["licenseId"] not in PERMISSIVE_LICENSES or not re.fullmatch(r"#[0-9a-f]{6}", recipe["brandColor"]):
                raise ValueError("Brand color is invalid or not permitted by the source license")
            color_file = painted_variant(color_item, color_source, "color", recipe["brandColor"])
            color_method = "pinned-provider-brand-color"
            color_palette = "monochrome-original" if recipe["brandColor"] in {"#000000", "#ffffff"} else "single-brand-color"
        else:
            color_file = wrapped_variant(color_item, color_source)
            color_method = "unmodified-source" if color_ref == "original" else "upstream-color-source"
        add("color", color_file, color_ref, color_method, color_palette, color_provenance)
        if color_provenance["licenseId"] in PERMISSIVE_LICENSES:
            add("grayscale", add_grayscale(color_file, item["id"]), color_ref, "derived-vector-grayscale", "grayscale", color_provenance)
        else:
            row["unavailable"]["grayscale"] = "license-no-derivatives"
        mono_ref = recipe.get("monochromeSource")
        if mono_ref:
            mono_source, mono_provenance = resolve(mono_ref)
            mono_item = {**item, "licenseId": mono_provenance["licenseId"]}
            if mono_provenance["licenseId"] in PERMISSIVE_LICENSES:
                for kind, paint in (("mono-black", "#000000"), ("mono-white", "#ffffff"), ("adaptive", "currentColor")):
                    add(kind, painted_variant(mono_item, mono_source, kind, paint), mono_ref,
                        "derived-from-single-paint-source", "currentColor" if kind == "adaptive" else kind, mono_provenance)
            else:
                native = native_single_paint(mono_source)
                for kind, paint in (("mono-black", "#000000"), ("mono-white", "#ffffff"), ("adaptive", "currentColor")):
                    if native == paint and kind != "adaptive":
                        add(kind, wrapped_variant(mono_item, mono_source, kind), mono_ref, "unmodified-native-monochrome", kind, mono_provenance)
                    else:
                        row["unavailable"][kind] = "license-no-derivatives"
        else:
            reason = "license-no-derivatives" if item["licenseId"] not in PERMISSIVE_LICENSES else "no-safe-single-paint-source"
            row["unavailable"].update({kind: reason for kind in ("mono-black", "mono-white", "adaptive")})
        if set(row["variants"]) | set(row["unavailable"]) != set(VARIANTS):
            raise ValueError("Incomplete variant availability record")
        catalog["logos"].append(row)
    catalog["coverage"] = {kind: coverage[kind] for kind in VARIANTS}
    catalog["fileCount"] = len(files)
    catalog["sourceSnapshotCount"] = len(snapshots)
    return catalog, files


def validate_variants(directory: Path, manifest: dict) -> list[str]:
    try:
        recipes = json.loads((directory / "logo_variant_sources.json").read_text(encoding="utf-8"))
        actual = json.loads((directory / "logo_variants.json").read_text(encoding="utf-8"))
        originals = read_originals(directory, manifest)
        expected, files = render_catalog(directory, manifest, recipes, originals, read_snapshots(directory, recipes))
        errors = [] if actual == expected else ["logo_variants.json differs from verified source recipes"]
        for relative, payload in files.items():
            path = safe_asset_path(directory, relative)
            if not path.is_file() or path.read_bytes() != payload:
                errors.append(f"Missing or modified vector variant: {relative}")
        for row in actual["logos"]:
            for kind, record in row["variants"].items():
                root = ET.fromstring(files[record["assetPath"]])
                if root.get("data-logo-variant") != kind or root.get("data-logo-id") != row["id"] or root.get("data-vector-only") != "true":
                    errors.append(f"Incorrect SVG selection markers: {row['id']} / {kind}")
                if root.get("viewBox") != "0 0 256 256":
                    errors.append(f"Incorrect normalized viewport: {row['id']} / {kind}")
                if kind == "adaptive" and (root.get("data-recolorable") != "true" or any(local_name(node.tag) == "image" for node in root.iter())):
                    errors.append(f"Adaptive variant must be inline currentColor geometry: {row['id']}")
        return errors
    except (ValueError, KeyError, TypeError, OSError, ET.ParseError) as error:
        return [f"Variant validation failed: {error}"]


def write_changed(path: Path, payload: bytes) -> None:
    if path.is_file() and path.read_bytes() == payload:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(payload)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--assets", type=Path, default=asset_directory())
    parser.add_argument("--sources", type=Path, help="Maintenance only: import alternate SVGs from prepared, pinned provider directories")
    parser.add_argument("--check", action="store_true", help="Verify existing variants without writing")
    args = parser.parse_args()
    manifest = load_manifest(args.assets / "logo_manifest.json")
    if args.check:
        errors = validate_variants(args.assets, manifest)
        print(json.dumps({"ok": not errors, "errors": errors[:40]}))
        return int(bool(errors))
    originals = read_originals(args.assets, manifest)
    if args.sources:
        recipes, snapshots = prepare_recipes(manifest, originals, args.sources)
    else:
        recipes = json.loads((args.assets / "logo_variant_sources.json").read_text(encoding="utf-8"))
        snapshots = read_snapshots(args.assets, recipes)
    catalog, files = render_catalog(args.assets, manifest, recipes, originals, snapshots)
    for relative, payload in {**snapshots, **files}.items():
        write_changed(safe_asset_path(args.assets, relative), payload)
    write_changed(args.assets / "logo_variant_sources.json", compact_json(recipes))
    write_changed(args.assets / "logo_variants.json", compact_json(catalog))
    print(json.dumps({"ok": True, "logos": manifest["logoCount"], "coverage": catalog["coverage"], "files": len(files), "alternateSources": len(snapshots)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
