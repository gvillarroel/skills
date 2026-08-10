#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

"""Build a standalone D3 logo studio from the bundled catalogs and template."""

from __future__ import annotations

import argparse
import html
import json
import sys
from pathlib import Path
from typing import Any


SKILL_ROOT = Path(__file__).resolve().parents[1]
ASSETS = SKILL_ROOT / "assets"
MANIFEST_PATH = ASSETS / "catalog" / "logo-manifest.json"
PALETTES_PATH = ASSETS / "palettes" / "colorsets.json"
ENGINE_PATH = ASSETS / "templates" / "logo-engine.js"
TEMPLATE_PATH = ASSETS / "templates" / "logo-studio.html"
D3_RUNTIME_PATH = ASSETS / "vendor" / "d3.v7.9.0.min.js"
FONT_IDS = ("geometric", "humanist", "condensed", "editorial", "monospace")


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise SystemExit(f"Expected a JSON object: {path}")
    return value


def ids(records: list[dict[str, Any]]) -> tuple[str, ...]:
    return tuple(str(record["id"]) for record in records)


def json_for_script(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")


def bounded(value: float, lower: float, upper: float, name: str) -> float:
    if not lower <= value <= upper:
        raise argparse.ArgumentTypeError(f"{name} must be between {lower} and {upper}")
    return value


def build_parser(manifest: dict[str, Any], palettes: dict[str, Any]) -> argparse.ArgumentParser:
    pattern_ids = ids(manifest["patterns"])
    texture_ids = ids(manifest["textures"])
    colorset_ids = tuple(palettes["colorsets"])
    first = manifest["compositions"][0]

    parser = argparse.ArgumentParser(description="Build an adjustable D3/SVG logo studio.")
    parser.add_argument("--output", type=Path, required=True, help="Exact output HTML path")
    parser.add_argument(
        "--texture-gallery-url",
        default="d3-logo-textures.html",
        help="Optional URL for the texture-atlas link; defaults to a sibling HTML file",
    )
    parser.add_argument("--brand", default=first["brand"], help="Brand text, up to 32 characters")
    parser.add_argument("--tagline", default=first["tagline"], help="Optional tagline, up to 56 characters")
    parser.add_argument("--colorset", choices=colorset_ids, default=first["colorset"])
    parser.add_argument("--pattern", choices=pattern_ids, default=first["patternId"])
    parser.add_argument("--texture", choices=texture_ids, default=first["textureId"])
    parser.add_argument("--font", choices=FONT_IDS, default=first["font"])
    parser.add_argument("--density", type=float, default=float(first["density"]))
    parser.add_argument("--curvature", type=float, default=float(first["curvature"]))
    parser.add_argument("--scale", type=float, default=float(first["scale"]))
    parser.add_argument("--rotation", type=float, default=float(first["rotation"]))
    parser.add_argument("--texture-strength", type=float, default=float(first["textureStrength"]))
    parser.add_argument("--seed", type=int, default=int(first["seed"]))
    return parser


def main() -> int:
    manifest = load_json(MANIFEST_PATH)
    palettes = load_json(PALETTES_PATH)
    parser = build_parser(manifest, palettes)
    args = parser.parse_args()

    brand = args.brand
    tagline = args.tagline
    if not brand.strip():
        parser.error("--brand must contain visible text")
    if len(brand) > 32:
        parser.error("--brand must be 32 characters or fewer")
    if len(tagline) > 56:
        parser.error("--tagline must be 56 characters or fewer")

    density = bounded(args.density, 0.5, 1.6, "density")
    curvature = bounded(args.curvature, 0.0, 1.0, "curvature")
    scale = bounded(args.scale, 0.7, 1.25, "scale")
    rotation = bounded(args.rotation, -30.0, 30.0, "rotation")
    texture_strength = bounded(args.texture_strength, 0.0, 1.0, "texture strength")

    if args.output.suffix.lower() not in {".html", ".htm"}:
        parser.error("--output must end in .html or .htm")

    initial_config = {
        "compositionId": "d3-logo-live-studio",
        "exampleId": args.pattern.removeprefix("d3-logo-"),
        "patternId": args.pattern,
        "textureId": args.texture,
        "brand": brand,
        "tagline": tagline,
        "colorset": args.colorset,
        "font": args.font,
        "density": density,
        "curvature": curvature,
        "scale": scale,
        "rotation": rotation,
        "textureStrength": texture_strength,
        "seed": args.seed,
    }
    embedded_manifest = {
        **manifest,
        "d3Version": "7.9.0",
        "selectedColorset": args.colorset,
        "palettes": palettes["colorsets"],
        "initialConfig": initial_config,
    }

    template = TEMPLATE_PATH.read_text(encoding="utf-8")
    engine = ENGINE_PATH.read_text(encoding="utf-8")
    d3_runtime = D3_RUNTIME_PATH.read_text(encoding="utf-8")
    replacements = {
        "__D3_LOGO_MANIFEST_JSON__": json_for_script(embedded_manifest),
        "__D3_LOGO_PALETTE_JSON__": json_for_script(palettes),
        "__D3_LOGO_INITIAL_CONFIG_JSON__": json_for_script(initial_config),
        "__D3_LOGO_RUNTIME_JS__": d3_runtime.replace("</script", "<\\/script"),
        "__D3_LOGO_ENGINE_JS__": engine.replace("</script", "<\\/script"),
        "__D3_LOGO_COLORSET__": args.colorset,
        "__D3_LOGO_TEXTURE_GALLERY_URL__": html.escape(args.texture_gallery_url, quote=True),
    }
    output_html = template
    for marker, value in replacements.items():
        marker_count = output_html.count(marker)
        if marker_count != 1:
            raise SystemExit(f"Template marker {marker} occurred {marker_count} times; expected exactly once.")
        output_html = output_html.replace(marker, value)
    leftovers = [marker for marker in replacements if marker in output_html]
    if leftovers:
        raise SystemExit(f"Unreplaced template markers: {', '.join(leftovers)}")

    output = args.output.expanduser().resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(output_html, encoding="utf-8", newline="\n")

    result = {
        "ok": True,
        "output": str(output),
        "patternCount": len(manifest["patterns"]),
        "textureCount": len(manifest["textures"]),
        "compositionCount": len(manifest["compositions"]),
        "standalone": True,
        "embeddedD3Version": "7.9.0",
        "initialPattern": args.pattern,
        "initialExampleId": args.pattern.removeprefix("d3-logo-"),
        "initialTexture": args.texture,
        "initialColorset": args.colorset,
        "textureGalleryUrl": args.texture_gallery_url,
        "bytes": output.stat().st_size,
    }
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
