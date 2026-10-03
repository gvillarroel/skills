#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Apply the bundled palette to authored HTML/SVG paint without changing geometry."""
from functools import wraps
import json
from pathlib import Path
import re

CONTRACT = Path(__file__).resolve().parents[1] / "assets" / "palettes" / "colorsets.json"
HEX = re.compile(r"(?<![\w-])#([0-9a-fA-F]{6}|[0-9a-fA-F]{3})(?![0-9a-fA-F])\b")


def adapt_artifact(source, colorset="colorset1"):
    """Map authored paint only; embedded source raster bytes remain immutable."""
    palettes = json.loads(CONTRACT.read_text(encoding="utf-8"))["colorsets"]
    if colorset not in palettes:
        raise ValueError("Select colorset1 or colorset2")
    allowed = palettes[colorset]["allowed"]
    # Distinct extended semantic roles become stable red/neutral roles in cs1.
    fallback = {"#007298": "#333e48", "#004d66": "#1c1c1c", "#00ace6": "#828282",
                "#e77204": "#9e1b32", "#994a00": "#6d1222", "#ff9633": "#e8002a",
                "#45842a": "#4f4f4f", "#294d19": "#363636", "#36b300": "#696969",
                "#652f6c": "#6d1222", "#431f47": "#1c1c1c", "#9e00b3": "#9e1b32",
                "#f1c319": "#9c9c9c", "#98700c": "#696969", "#ffd332": "#b5b5b5"}
    for value in ("#cdf3ff", "#ffe5cc", "#dbffcc", "#f9ccff", "#fff4cc", "#ffccd5"):
        fallback[value] = "#e7e7e7"

    def token(match):
        # Hex-looking IDs are geometry references, not authored color values.
        prefix = source[max(0, match.start() - 80):match.start()]
        suffix = source[match.end():match.end() + 30]
        if (re.search(r"url\(\s*$", prefix, re.I)
                or re.search(r"\b(?:xlink:)?href\s*=\s*[\"']$", prefix, re.I)
                or re.match(r"\s*\{", suffix)):
            return match.group(0)
        value = match.group(1).lower()
        value = "#" + ("".join(ch * 2 for ch in value) if len(value) == 3 else value)
        if colorset == "colorset1" and value in fallback:
            return fallback[value]
        if value in allowed:
            return value
        rgb = tuple(int(value[i:i + 2], 16) for i in (1, 3, 5))
        return min(allowed, key=lambda candidate: sum((rgb[i] - int(candidate[1 + i * 2:3 + i * 2], 16)) ** 2 for i in range(3)))

    # These builders used decorative CSS drop shadows with arbitrary rgba
    # syntax. Removing the shadows leaves deterministic, readable flat paint.
    source = re.sub(r"filter:\s*drop-shadow\([^;]+;", "filter: none;", source)
    def alpha_paint(match):
        prop, red, green, blue, alpha = match.groups()
        base = "#" + ''.join(f'{int(channel):02x}' for channel in (red, green, blue))
        return f'{prop}: {base}; {prop}-opacity: {alpha};'
    source = re.sub(r"\b(fill|stroke):\s*rgba\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*,\s*([.\d]+)\s*\)\s*;", alpha_paint, source)
    source = HEX.sub(token, source)
    # A generated standalone builder has one active contract across UI and SVG.
    source = re.sub(r'\bdata-(?:colorset|color-set)=["\'](?:base|colorset[12])["\']', '', source)
    source = re.sub(r"<body\b", f'<body data-colorset="{colorset}"', source, count=1)
    source = re.sub(r"<svg\b", f'<svg data-colorset="{colorset}"', source)
    return source


def colorset_output(function):
    """Keep builders callable while making colorset1 their actual output default."""
    @wraps(function)
    def generate(*args, colorset="colorset1", **kwargs):
        return adapt_artifact(function(*args, **kwargs), colorset)
    return generate
