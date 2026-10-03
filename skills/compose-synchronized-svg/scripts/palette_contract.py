#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Finite authored-paint contract; imported source media stays producer-owned."""
import json
import re
from pathlib import Path

COLORSETS = json.loads((Path(__file__).resolve().parent.parent / "assets/palettes/colorsets.json").read_text(encoding="utf-8"))["colorsets"]

def require_color(value, colorset="colorset2"):
    if not isinstance(value, str) or value.lower() not in COLORSETS[colorset]["allowed"]:
        raise ValueError(f"Authored color {value!r} must be an exact {colorset} token")
    return value.lower()

def nearest_color(value, colorset="colorset2"):
    """Snap an intentional generated tint to the selected finite token set."""
    channels = [int(value[i:i + 2], 16) for i in (1, 3, 5)]
    return min(COLORSETS[colorset]["allowed"], key=lambda c: sum((x - int(c[i:i + 2], 16)) ** 2 for x, i in zip(channels, (1, 3, 5))))


SVG_PAINT_ATTRIBUTES = {"fill", "stroke", "color", "stop-color", "flood-color", "lighting-color"}


def require_svg_paint(value, colorset):
    """Check authored fragment paints while retaining local references and inheritance."""
    text = value.strip().lower()
    if text in {"none", "inherit", "transparent", "currentcolor", "context-fill", "context-stroke"}:
        return text
    variable = re.fullmatch(r"var\(--[a-z0-9-]+(?:,\s*(.+))?\)", text)
    if variable:
        if variable.group(1):
            require_svg_paint(variable.group(1), colorset)
        return text
    if re.fullmatch(r"url\(['\"]?#[a-z0-9_-]+['\"]?\)", text):
        return text
    text = {"black": "#000000", "white": "#ffffff"}.get(text, text)
    if re.fullmatch(r"#[0-9a-f]{3,4}", text):
        text = "#" + "".join(channel * 2 for channel in text[1:4])
    elif re.fullmatch(r"#[0-9a-f]{8}", text):
        text = text[:7]
    return require_color(text, colorset)
