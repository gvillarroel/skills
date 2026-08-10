#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

"""Build the standalone D3 logo texture atlas acceptance page."""

from __future__ import annotations

import argparse
import html
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any


SKILL_ROOT = Path(__file__).resolve().parents[1]
ASSETS = SKILL_ROOT / "assets"
MANIFEST_PATH = ASSETS / "catalog" / "logo-manifest.json"
PALETTES_PATH = ASSETS / "palettes" / "colorsets.json"
ENGINE_PATH = ASSETS / "templates" / "logo-engine.js"
TEMPLATE_PATH = ASSETS / "templates" / "texture-gallery.html"
D3_RUNTIME_PATH = ASSETS / "vendor" / "d3.v7.9.0.min.js"
EXPECTED_TEXTURE_COUNT = 40
ID_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise SystemExit(f"Could not load {path}: {error}") from error
    if not isinstance(value, dict):
        raise SystemExit(f"Expected a JSON object: {path}")
    return value


def json_for_script(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")


def validate_textures(manifest: dict[str, Any]) -> list[dict[str, Any]]:
    textures = manifest.get("textures")
    if not isinstance(textures, list):
        raise SystemExit("Manifest textures must be an array.")
    if len(textures) != EXPECTED_TEXTURE_COUNT:
        raise SystemExit(
            f"Texture gallery requires {EXPECTED_TEXTURE_COUNT} manifest textures; found {len(textures)}."
        )

    ids: list[str] = []
    signatures: list[str] = []
    normalized: list[dict[str, Any]] = []
    for index, value in enumerate(textures, start=1):
        if not isinstance(value, dict):
            raise SystemExit(f"Texture record {index} must be an object.")
        texture_id = value.get("id")
        label = value.get("label")
        signature = value.get("geometrySignature")
        family = value.get("family", "uncategorized")
        description = value.get("description")
        if not isinstance(texture_id, str) or not ID_RE.fullmatch(texture_id):
            raise SystemExit(f"Texture record {index} has an invalid canonical ID: {texture_id!r}")
        if not texture_id.startswith("d3-logo-"):
            raise SystemExit(f"Texture ID must use the d3-logo namespace: {texture_id}")
        if not isinstance(label, str) or not label.strip():
            raise SystemExit(f"Texture {texture_id} must have a visible label.")
        if not isinstance(signature, str) or not ID_RE.fullmatch(signature):
            raise SystemExit(f"Texture {texture_id} has an invalid geometry signature: {signature!r}")
        if not isinstance(family, str) or not ID_RE.fullmatch(family):
            raise SystemExit(f"Texture {texture_id} has an invalid family: {family!r}")
        if not isinstance(description, str) or not description.strip():
            raise SystemExit(f"Texture {texture_id} must have a non-empty description.")
        ids.append(texture_id)
        signatures.append(signature)
        normalized.append({**value, "family": family})

    duplicate_ids = sorted(key for key, count in Counter(ids).items() if count > 1)
    duplicate_signatures = sorted(key for key, count in Counter(signatures).items() if count > 1)
    if duplicate_ids:
        raise SystemExit(f"Duplicate texture IDs: {', '.join(duplicate_ids)}")
    if duplicate_signatures:
        raise SystemExit(f"Duplicate texture geometry signatures: {', '.join(duplicate_signatures)}")
    return normalized


def texture_cards_html(textures: list[dict[str, Any]]) -> str:
    cards: list[str] = []
    for texture in textures:
        texture_id = str(texture["id"])
        slug = texture_id.removeprefix("d3-logo-")
        label = str(texture["label"])
        signature = str(texture["geometrySignature"])
        family = str(texture["family"])
        description = str(texture["description"])
        escaped_id = html.escape(texture_id, quote=True)
        escaped_slug = html.escape(slug, quote=True)
        escaped_label = html.escape(label)
        escaped_label_attr = html.escape(label, quote=True)
        escaped_signature = html.escape(signature, quote=True)
        escaped_family = html.escape(family, quote=True)
        escaped_description = html.escape(description)
        cards.append(
            f'''      <article class="texture-card" id="{escaped_id}" data-example-id="{escaped_slug}" data-pattern-id="{escaped_id}" data-texture-id="{escaped_id}" data-geometry-signature="{escaped_signature}" data-texture-family="{escaped_family}" data-render-state="pending">
        <div class="texture-swatch"><svg id="{escaped_slug}-swatch" data-texture-swatch="{escaped_id}" viewBox="0 0 480 270" role="img" aria-labelledby="{escaped_slug}-label {escaped_slug}-id"></svg></div>
        <div class="texture-copy">
          <h3 id="{escaped_slug}-label">{escaped_label}</h3>
          <a class="texture-id-link" href="#{escaped_id}" aria-label="Link to {escaped_label_attr}"><code class="texture-id" id="{escaped_slug}-id">{escaped_id}</code></a>
          <p class="texture-description">{escaped_description}</p>
          <div class="texture-meta"><span>{escaped_family}</span><span>{escaped_signature}</span></div>
        </div>
      </article>'''
        )
    return "\n".join(cards)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build the standalone D3 logo texture atlas.")
    parser.add_argument("--output", type=Path, required=True, help="Exact output HTML path")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if args.output.suffix.lower() not in {".html", ".htm"}:
        raise SystemExit("--output must end in .html or .htm")

    manifest = load_json(MANIFEST_PATH)
    palettes = load_json(PALETTES_PATH)
    textures = validate_textures(manifest)
    colorsets = palettes.get("colorsets")
    if not isinstance(colorsets, dict) or set(colorsets) != {"colorset1", "colorset2"}:
        raise SystemExit("Palette catalog must contain exactly colorset1 and colorset2.")

    template = TEMPLATE_PATH.read_text(encoding="utf-8")
    engine = ENGINE_PATH.read_text(encoding="utf-8")
    d3_runtime = D3_RUNTIME_PATH.read_text(encoding="utf-8")
    if "renderTexture" not in engine:
        raise SystemExit("The bundled logo engine does not expose renderTexture yet.")
    if not d3_runtime.strip():
        raise SystemExit("The bundled D3 7.9.0 runtime is empty.")

    embedded_manifest = {**manifest, "textures": textures, "d3Version": "7.9.0"}
    replacements = {
        "__D3_LOGO_TEXTURE_COUNT__": str(len(textures)),
        "__D3_LOGO_TEXTURE_CARDS_HTML__": texture_cards_html(textures),
        "__D3_LOGO_TEXTURE_MANIFEST_JSON__": json_for_script(embedded_manifest),
        "__D3_LOGO_TEXTURE_PALETTES_JSON__": json_for_script(palettes),
        "__D3_LOGO_TEXTURE_RUNTIME_JS__": d3_runtime.replace("</script", "<\\/script"),
        "__D3_LOGO_TEXTURE_ENGINE_JS__": engine.replace("</script", "<\\/script"),
    }
    output_html = template
    for marker, replacement in replacements.items():
        count = output_html.count(marker)
        if count != 1:
            raise SystemExit(f"Template marker {marker} occurred {count} times; expected exactly once.")
        output_html = output_html.replace(marker, replacement)
    remaining = sorted(set(re.findall(r"__D3_LOGO_TEXTURE_[A-Z0-9_]+__", output_html)))
    if remaining:
        raise SystemExit(f"Unreplaced texture-gallery markers: {', '.join(remaining)}")

    output = args.output.expanduser().resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(output_html, encoding="utf-8", newline="\n")
    result = {
        "ok": True,
        "output": str(output),
        "pageId": "d3-logo-textures",
        "textureCount": len(textures),
        "patternCount": len(manifest.get("patterns", [])),
        "compositionCount": len(manifest.get("compositions", [])),
        "colorsets": sorted(colorsets),
        "standalone": True,
        "embeddedD3Version": "7.9.0",
        "bytes": output.stat().st_size,
    }
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
