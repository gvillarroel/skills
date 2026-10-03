#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Validate or normalize SVG paint values against the bundled colorsets."""
from __future__ import annotations
import colorsys
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path

COLORSETS = json.loads((Path(__file__).resolve().parent.parent / "assets/palettes/colorsets.json").read_text(encoding="utf-8"))["colorsets"]
PAINT_KEYS = {"fill", "stroke", "color", "background", "background-color", "border-color", "stop-color", "flood-color", "lighting-color", "outline-color", "text-decoration-color", "marker-color", "filter", "box-shadow", "text-shadow", "border", "border-top", "border-right", "border-bottom", "border-left", "outline", "background-image"}
DECLARATION = re.compile(r"(?P<key>[-\w]+)\s*:\s*(?P<value>[^;}]+)")
NAMES = json.loads((Path(__file__).resolve().parent.parent / "assets/palettes/css-named-colors.json").read_text(encoding="utf-8"))
TOKEN = re.compile(r"#[0-9a-fA-F]{3,8}\b|(?:rgba?|hsla?)\([^)]*\)|\b(?:" + "|".join(NAMES) + r")\b", re.I)

def canonical(token: str) -> str:
    token = token.lower()
    if token in NAMES:
        return NAMES[token]
    if token.startswith("#"):
        raw = token[1:]
        if len(raw) in {3, 4}:
            raw = "".join(c * 2 for c in raw)
        return "#" + raw[:6]
    values = re.findall(r"[-+]?(?:\d*\.)?\d+%?", token)
    if token.startswith("hsl"):
        rgb = colorsys.hls_to_rgb(float(values[0]) / 360 % 1, float(values[2].rstrip("%")) / 100, float(values[1].rstrip("%")) / 100)
        return "#" + "".join(f"{round(c * 255):02x}" for c in rgb)
    return "#" + "".join(f"{round(float(c.rstrip('%')) * (2.55 if c.endswith('%') else 1)):02x}" for c in values[:3])

def rgb(token: str) -> tuple[int, int, int]:
    return tuple(int(token[i:i+2], 16) for i in (1, 3, 5))

def nearest(token: str, colorset: str) -> str:
    original = rgb(token)
    return min(COLORSETS[colorset]["allowed"], key=lambda value: sum((a-b)**2 for a,b in zip(original, rgb(value))))

def svg_paints(root: ET.Element, colorset: str, *, normalize: bool = False) -> dict[str, str]:
    allowed = set(COLORSETS[colorset]["allowed"])
    changes: dict[str, str] = {}
    def rewrite(value: str) -> str:
        def replace(match: re.Match[str]) -> str:
            token = match.group()
            base = canonical(token)
            if base in allowed:
                return token
            mapped = nearest(base, colorset)
            changes[base] = mapped
            if not normalize:
                return token
            # Preserve paint alpha; opacity is a compositing operation, not a new base color.
            values = re.findall(r"[-+]?(?:\d*\.)?\d+%?", token)
            if token.lower().startswith(("rgba", "hsla")) and len(values) == 4:
                return f"rgba({','.join(str(v) for v in rgb(mapped))},{values[3]})"
            if token.startswith("#") and len(token) == 9:
                return mapped + token[-2:]
            if token.startswith("#") and len(token) == 5:
                return mapped + token[-1] * 2
            return mapped
        # Gradient/filter references are identities, never paint tokens.
        parts = re.split(r'(url\([^)]*\))', value, flags=re.I)
        rewritten = ''.join(part if part.lower().startswith('url(') else TOKEN.sub(replace,part) for part in parts)
        scrubbed = re.sub(r'url\([^)]*\)|var\([^)]*\)', '', value, flags=re.I).strip()
        if scrubbed and (re.fullmatch(r'[a-z]+', scrubbed, re.I) and scrubbed.lower() not in NAMES and scrubbed.lower() not in {'none','transparent','inherit','initial','unset','revert','currentcolor','context-fill','context-stroke'} or re.search(r'\b(?:oklch|oklab|lab|lch|hwb|color|color-mix)\(',scrubbed,re.I)):
            changes['unsupported-paint:'+scrubbed] = 'requires explicit selected palette token'
            if normalize:
                raise ValueError('Unsupported paint requires an explicit selected palette token: '+scrubbed)
        return rewritten
    def css(text: str) -> str:
        def replace(match: re.Match[str]) -> str:
            if match.group("key").lower() not in PAINT_KEYS and not match.group("key").startswith("--"):
                return match.group()
            return match.group("key") + ":" + rewrite(match.group("value"))
        return DECLARATION.sub(replace, text)
    for element in root.iter():
        local = element.tag.rsplit('}',1)[-1]
        for key, value in list(element.attrib.items()):
            if local in {'animate','animateTransform','animateMotion','set'} and key == 'fill':
                continue
            if key.lower() in PAINT_KEYS:
                updated = rewrite(value)
            elif local in {'animate','set'} and element.get('attributeName') in PAINT_KEYS and key in {'values','from','to','by'}:
                updated = ';'.join(rewrite(part) for part in value.split(';'))
            elif key.lower() == "style":
                updated = css(value)
            else:
                continue
            if normalize:
                element.set(key, updated)
        if element.tag.rsplit("}", 1)[-1] == "style" and element.text:
            updated = css(element.text)
            if normalize:
                element.text = updated
    return changes

def require_svg_palette(root: ET.Element, colorset: str | None = None) -> str:
    candidates = [colorset] if colorset else list(COLORSETS)
    findings = {name: svg_paints(root, name) for name in candidates}
    for name, outside in findings.items():
        if not outside:
            return name
    raise ValueError("SVG paints are outside the bundled colorsets: " + json.dumps(findings, sort_keys=True) + ". Restyle the editable source before animation.")
