#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

"""Statically validate the standalone D3 logo texture atlas."""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from dataclasses import dataclass, field
from html.parser import HTMLParser
from pathlib import Path
from typing import Any


EXPECTED_TEXTURE_COUNT = 40
PAGE_ID = "d3-logo-textures"
ID_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
HEX_RE = re.compile(r"#[0-9A-Fa-f]{3,8}\b")
REQUIRED_DOM_IDS = {
    "texture-controls",
    "colorset",
    "density",
    "curvature",
    "texture-strength",
    "seed",
    "family",
    "texture-search",
    "reset-textures",
    "texture-gallery",
    "visible-count",
    "texture-total",
    "d3-logo-texture-manifest",
    "d3-logo-texture-palettes",
}


@dataclass
class ScriptRecord:
    attrs: dict[str, str]
    text: str = ""


@dataclass
class CardRecord:
    attrs: dict[str, str]
    visible_id_parts: list[str] = field(default_factory=list)
    visible_id_outside_svg: bool = True
    swatches: list[dict[str, str]] = field(default_factory=list)
    static_svg_text: list[str] = field(default_factory=list)

    @property
    def visible_id(self) -> str:
        return "".join(self.visible_id_parts).strip()


class GalleryParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.body: dict[str, str] | None = None
        self.meta: list[dict[str, str]] = []
        self.scripts: list[ScriptRecord] = []
        self.styles: list[str] = []
        self.ids: list[str] = []
        self.cards: list[CardRecord] = []
        self.resource_tags: list[tuple[str, dict[str, str]]] = []
        self._script: ScriptRecord | None = None
        self._style_parts: list[str] | None = None
        self._card: CardRecord | None = None
        self._texture_id_depth = 0
        self._svg_depth = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = {name: value or "" for name, value in attrs}
        element_id = attributes.get("id")
        if element_id:
            self.ids.append(element_id)
        if tag == "body" and self.body is None:
            self.body = attributes
        if tag == "meta":
            self.meta.append(attributes)
        if tag == "script":
            self._script = ScriptRecord(attributes)
        elif tag == "style":
            self._style_parts = []
        if tag in {"script", "link", "img", "image", "picture", "video", "canvas", "iframe", "object", "embed", "audio", "source"}:
            self.resource_tags.append((tag, attributes))

        classes = set(attributes.get("class", "").split())
        if tag == "article" and "texture-card" in classes:
            self._card = CardRecord(attributes)
        if self._card is not None and tag == "svg":
            self._svg_depth += 1
            if "data-texture-swatch" in attributes:
                self._card.swatches.append(attributes)
        if self._card is not None and tag == "code" and "texture-id" in classes:
            self._texture_id_depth += 1
            if self._svg_depth:
                self._card.visible_id_outside_svg = False

    def handle_endtag(self, tag: str) -> None:
        if tag == "script" and self._script is not None:
            self.scripts.append(self._script)
            self._script = None
        elif tag == "style" and self._style_parts is not None:
            self.styles.append("".join(self._style_parts))
            self._style_parts = None
        if self._card is not None and tag == "code" and self._texture_id_depth:
            self._texture_id_depth -= 1
        if self._card is not None and tag == "svg" and self._svg_depth:
            self._svg_depth -= 1
        if tag == "article" and self._card is not None:
            self.cards.append(self._card)
            self._card = None
            self._texture_id_depth = 0
            self._svg_depth = 0

    def handle_data(self, data: str) -> None:
        if self._script is not None:
            self._script.text += data
        if self._style_parts is not None:
            self._style_parts.append(data)
        if self._card is not None and self._texture_id_depth:
            self._card.visible_id_parts.append(data)
        if self._card is not None and self._svg_depth and data.strip():
            self._card.static_svg_text.append(data.strip())


def add(findings: list[str], message: str) -> None:
    findings.append(message)


def one_script(parser: GalleryParser, findings: list[str], **expected: str) -> ScriptRecord | None:
    matches = [script for script in parser.scripts if all(script.attrs.get(key) == value for key, value in expected.items())]
    label = ", ".join(f"{key}={value!r}" for key, value in expected.items())
    if len(matches) != 1:
        add(findings, f"Expected exactly one script with {label}; found {len(matches)}.")
        return None
    return matches[0]


def load_script_json(script: ScriptRecord | None, label: str, findings: list[str]) -> dict[str, Any]:
    if script is None:
        return {}
    try:
        value = json.loads(script.text)
    except json.JSONDecodeError as error:
        add(findings, f"{label} contains invalid JSON: {error}.")
        return {}
    if not isinstance(value, dict):
        add(findings, f"{label} must contain a JSON object.")
        return {}
    return value


def validate_page_metadata(parser: GalleryParser, findings: list[str]) -> None:
    body = parser.body
    if body is None:
        add(findings, "Page is missing a body element.")
        return
    for name, expected in {
        "data-example-id": PAGE_ID,
        "data-pattern-id": PAGE_ID,
        "data-pattern-page": "true",
        "data-texture-count": str(EXPECTED_TEXTURE_COUNT),
    }.items():
        if body.get(name) != expected:
            add(findings, f"Body {name} must equal {expected!r}; found {body.get(name)!r}.")

    meta_by_name: dict[str, list[str]] = {}
    for meta in parser.meta:
        name = meta.get("name")
        if name:
            meta_by_name.setdefault(name, []).append(meta.get("content", ""))
    for name, expected in {
        "example-id": PAGE_ID,
        "pattern-id": PAGE_ID,
        "pattern-page": "true",
    }.items():
        values = meta_by_name.get(name, [])
        if values != [expected]:
            add(findings, f"Meta {name} must occur once with content {expected!r}; found {values!r}.")

    id_counts = Counter(parser.ids)
    duplicate_dom_ids = sorted(element_id for element_id, count in id_counts.items() if count > 1)
    if duplicate_dom_ids:
        add(findings, f"Duplicate DOM IDs: {', '.join(duplicate_dom_ids[:20])}.")
    missing = sorted(REQUIRED_DOM_IDS - set(parser.ids))
    if missing:
        add(findings, f"Missing required DOM IDs: {', '.join(missing)}.")


def validate_manifest(manifest: dict[str, Any], findings: list[str]) -> list[dict[str, Any]]:
    textures = manifest.get("textures")
    if not isinstance(textures, list):
        add(findings, "Embedded manifest textures must be an array.")
        return []
    if len(textures) != EXPECTED_TEXTURE_COUNT:
        add(findings, f"Expected {EXPECTED_TEXTURE_COUNT} manifest textures, found {len(textures)}.")

    ids: list[str] = []
    signatures: list[str] = []
    valid: list[dict[str, Any]] = []
    for index, texture in enumerate(textures, start=1):
        if not isinstance(texture, dict):
            add(findings, f"Manifest texture {index} must be an object.")
            continue
        texture_id = texture.get("id")
        signature = texture.get("geometrySignature")
        family = texture.get("family", "uncategorized")
        label = texture.get("label")
        if not isinstance(texture_id, str) or not ID_RE.fullmatch(texture_id) or not texture_id.startswith("d3-logo-"):
            add(findings, f"Manifest texture {index} has invalid ID {texture_id!r}.")
            continue
        if not isinstance(signature, str) or not ID_RE.fullmatch(signature):
            add(findings, f"Texture {texture_id} has invalid geometry signature {signature!r}.")
        if not isinstance(family, str) or not ID_RE.fullmatch(family):
            add(findings, f"Texture {texture_id} has invalid family {family!r}.")
        if not isinstance(label, str) or not label.strip():
            add(findings, f"Texture {texture_id} is missing a visible label.")
        ids.append(texture_id)
        if isinstance(signature, str):
            signatures.append(signature)
        valid.append(texture)

    duplicates = sorted(key for key, count in Counter(ids).items() if count > 1)
    duplicate_signatures = sorted(key for key, count in Counter(signatures).items() if count > 1)
    if duplicates:
        add(findings, f"Duplicate manifest texture IDs: {', '.join(duplicates)}.")
    if duplicate_signatures:
        add(findings, f"Duplicate manifest geometry signatures: {', '.join(duplicate_signatures)}.")
    return valid


def validate_cards(cards: list[CardRecord], textures: list[dict[str, Any]], findings: list[str]) -> None:
    if len(cards) != EXPECTED_TEXTURE_COUNT:
        add(findings, f"Expected {EXPECTED_TEXTURE_COUNT} texture cards, found {len(cards)}.")
    expected_ids = [str(texture.get("id", "")) for texture in textures]
    observed_ids = [card.attrs.get("data-texture-id", "") for card in cards]
    if observed_ids != expected_ids:
        add(findings, "Texture card order and IDs do not exactly match the manifest.")
    if len(set(observed_ids)) != len(observed_ids):
        add(findings, "Texture cards contain duplicate canonical IDs.")

    by_id = {str(texture.get("id", "")): texture for texture in textures}
    for index, card in enumerate(cards, start=1):
        texture_id = card.attrs.get("data-texture-id", "")
        texture = by_id.get(texture_id)
        if texture is None:
            add(findings, f"Card {index} references unknown texture {texture_id!r}.")
            continue
        expected_slug = texture_id.removeprefix("d3-logo-")
        expected_signature = str(texture.get("geometrySignature", ""))
        expected_family = str(texture.get("family", "uncategorized"))
        for name, expected in {
            "id": texture_id,
            "data-example-id": expected_slug,
            "data-pattern-id": texture_id,
            "data-texture-id": texture_id,
            "data-geometry-signature": expected_signature,
            "data-texture-family": expected_family,
        }.items():
            if card.attrs.get(name) != expected:
                add(findings, f"Card {texture_id or index} {name} must equal {expected!r}; found {card.attrs.get(name)!r}.")
        if card.visible_id != texture_id:
            add(findings, f"Card {texture_id or index} visible ID must equal its canonical ID; found {card.visible_id!r}.")
        if not card.visible_id_outside_svg:
            add(findings, f"Card {texture_id or index} places its visible ID inside SVG.")
        if card.static_svg_text:
            add(findings, f"Card {texture_id or index} contains static SVG text instead of external HTML labels.")
        if len(card.swatches) != 1:
            add(findings, f"Card {texture_id or index} must contain exactly one data-texture-swatch SVG; found {len(card.swatches)}.")
        elif card.swatches[0].get("data-texture-swatch") != texture_id:
            add(findings, f"Card {texture_id} swatch marker does not match its texture ID.")


def renderer_ids(engine: str, findings: list[str]) -> list[str]:
    start_marker = "const TEXTURE_RENDERERS = {"
    end_marker = "function createTexture("
    start = engine.find(start_marker)
    end = engine.find(end_marker, start + len(start_marker)) if start >= 0 else -1
    if start < 0 or end < 0:
        add(findings, "Could not locate the texture renderer registry in the embedded engine.")
        return []
    values = re.findall(r'"(d3-logo-[a-z0-9-]+)"\s*:', engine[start:end])
    duplicates = sorted(key for key, count in Counter(values).items() if count > 1)
    if duplicates:
        add(findings, f"Duplicate embedded texture renderer IDs: {', '.join(duplicates)}.")
    return values


def validate_engine(engine: str, textures: list[dict[str, Any]], app_text: str, findings: list[str]) -> None:
    expected = [str(texture.get("id", "")) for texture in textures]
    renderers = renderer_ids(engine, findings)
    if renderers != expected:
        missing = sorted(set(expected) - set(renderers))
        extra = sorted(set(renderers) - set(expected))
        add(findings, f"Manifest/engine texture renderer parity failed; missing={missing}, extra={extra}, orderMatch={renderers == expected}.")
    if len(renderers) != EXPECTED_TEXTURE_COUNT:
        add(findings, f"Expected {EXPECTED_TEXTURE_COUNT} texture renderers, found {len(renderers)}.")
    if not re.search(r"\bfunction\s+renderTexture\s*\(", engine):
        add(findings, "Embedded engine must define renderTexture.")
    api_start = engine.find("const API = Object.freeze({")
    api_end = engine.find("});", api_start) if api_start >= 0 else -1
    if api_start < 0 or api_end < 0 or not re.search(r"\brenderTexture\b", engine[api_start:api_end]):
        add(findings, "Embedded engine API must export renderTexture.")
    if not re.search(r"\bengine\.renderTexture\s*\(", app_text):
        add(findings, "Gallery application must render swatches through D3LogoDesign.renderTexture.")


def validate_palettes(palettes: dict[str, Any], css: str, application: str, findings: list[str]) -> None:
    colorsets = palettes.get("colorsets")
    if not isinstance(colorsets, dict) or set(colorsets) != {"colorset1", "colorset2"}:
        add(findings, "Embedded palettes must contain exactly colorset1 and colorset2.")
        return
    allowed: set[str] = set()
    for colorset_id, colorset in colorsets.items():
        values = colorset.get("allowed") if isinstance(colorset, dict) else None
        if not isinstance(values, list) or not values:
            add(findings, f"Palette {colorset_id}.allowed must be a nonempty array.")
            continue
        for value in values:
            if not isinstance(value, str) or not re.fullmatch(r"#[0-9a-f]{6}", value):
                add(findings, f"Palette {colorset_id} contains an invalid token {value!r}.")
            else:
                allowed.add(value)

    css_hex = HEX_RE.findall(css)
    invalid_css_hex = sorted(set(value for value in css_hex if not re.fullmatch(r"#[0-9a-f]{6}", value)))
    leaked_css_hex = sorted(set(value.lower() for value in css_hex) - allowed)
    if invalid_css_hex:
        add(findings, f"CSS contains unsupported hex formats: {', '.join(invalid_css_hex)}.")
    if leaked_css_hex:
        add(findings, f"CSS contains colors outside colorset1/colorset2: {', '.join(leaked_css_hex)}.")
    if re.search(r"(?i)\b(?:rgb|rgba|hsl|hsla|lch|oklch)\s*\(", application):
        add(findings, "Gallery contains forbidden functional color syntax.")
    if re.search(r"(?i)\b(?:black|white|red|blue|green|orange|yellow|purple|gray|grey|transparent)\b", css):
        add(findings, "CSS contains a named color; use exact palette hex tokens instead.")


def validate_standalone(text: str, parser: GalleryParser, application: str, findings: list[str]) -> None:
    if re.search(r"__D3_LOGO_TEXTURE_[A-Z0-9_]+__", text):
        add(findings, "Gallery contains unreplaced build markers.")
    if re.search(r"(?i)(?:linear|radial|conic)-gradient\s*\(|<\s*(?:linearGradient|radialGradient)\b", application):
        add(findings, "Gallery contains forbidden gradient syntax.")
    if re.search(r"(?i)@import\b", "\n".join(parser.styles)):
        add(findings, "Gallery CSS contains a forbidden @import.")
    if re.search(r"(?i)<\s*(?:img|image|picture|video|canvas|iframe|object|embed|audio|source)\b", text):
        add(findings, "Gallery contains a forbidden raster, media, canvas, or embedded resource element.")
    for tag, attrs in parser.resource_tags:
        if tag in {"script", "link"} and (attrs.get("src") or attrs.get("href")):
            add(findings, f"Gallery contains an external {tag} resource reference.")
    for match in re.finditer(r"(?i)(?<![\w$])url\(([^)]*)\)", application):
        target = match.group(1).strip().strip("\"'").strip()
        if target and not target.startswith("#"):
            add(findings, f"Gallery contains a non-fragment URL reference: {target!r}.")
    if "window.D3LogoTextureGallery" not in application:
        add(findings, "Gallery application does not expose window.D3LogoTextureGallery.")
    if "hashchange" not in application or "window.location.hash" not in application:
        add(findings, "Gallery application does not implement direct-hash navigation.")


def main() -> int:
    arg_parser = argparse.ArgumentParser(description="Validate the standalone D3 logo texture atlas.")
    arg_parser.add_argument("input", type=Path, help="Generated texture gallery HTML")
    arg_parser.add_argument("--json-report", type=Path, help="Optional JSON report path")
    args = arg_parser.parse_args()

    findings: list[str] = []
    try:
        text = args.input.read_text(encoding="utf-8")
    except OSError as error:
        print(f"Texture gallery validation failed: {error}", file=sys.stderr)
        return 1
    parser = GalleryParser()
    try:
        parser.feed(text)
    except Exception as error:
        add(findings, f"Could not parse gallery HTML: {error}.")

    validate_page_metadata(parser, findings)
    manifest_script = one_script(parser, findings, id="d3-logo-texture-manifest", type="application/json")
    palette_script = one_script(parser, findings, id="d3-logo-texture-palettes", type="application/json")
    runtime_script = one_script(parser, findings, **{"data-runtime": "d3-7.9.0"})
    engine_script = one_script(parser, findings, **{"data-engine": "d3-logo-design"})
    manifest = load_script_json(manifest_script, "Texture manifest", findings)
    palettes = load_script_json(palette_script, "Texture palettes", findings)
    textures = validate_manifest(manifest, findings)
    validate_cards(parser.cards, textures, findings)

    app_scripts = [
        script.text
        for script in parser.scripts
        if script is not manifest_script and script is not palette_script and script is not runtime_script and script is not engine_script
    ]
    app_text = "\n".join(app_scripts)
    engine = engine_script.text if engine_script is not None else ""
    validate_engine(engine, textures, app_text, findings)
    css = "\n".join(parser.styles)
    application = "\n".join([css, engine, app_text])
    validate_palettes(palettes, css, application, findings)
    validate_standalone(text, parser, application, findings)

    report = {
        "ok": not findings,
        "input": str(args.input.resolve()),
        "pageId": PAGE_ID,
        "expectedTextureCount": EXPECTED_TEXTURE_COUNT,
        "manifestTextureCount": len(textures),
        "cardCount": len(parser.cards),
        "rendererCount": len(renderer_ids(engine, [])) if engine else 0,
        "standalone": not any("external" in finding.lower() for finding in findings),
        "findings": findings,
    }
    if args.json_report:
        output = args.json_report.expanduser().resolve()
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(report, indent=2), encoding="utf-8", newline="\n")
    print(json.dumps(report, indent=2))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
