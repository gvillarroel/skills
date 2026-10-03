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


def text_on_fill(fill, colorset="colorset2"):
    """Select pure black or white by the actual opaque fill's WCAG contrast."""
    return COLORSETS[colorset]["textOnFill"][require_color(fill, colorset)]

def solid_colors(colorset="colorset2", canvas="#f7f7f7"):
    """Exhaust every unique palette solid before introducing outline variants."""
    return [paint for paint in COLORSETS[colorset]["solidSequence"] if paint != canvas.lower()]

def relative_luminance(fill):
    """Compute WCAG sRGB relative luminance for an opaque palette token."""
    channels = [int(fill[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    linear = [c / 12.92 if c <= .04045 else ((c + .055) / 1.055) ** 2.4 for c in channels]
    return sum(c * weight for c, weight in zip(linear, (.2126, .7152, .0722)))

def contrast_ratio(first, second):
    luminances = sorted((relative_luminance(first), relative_luminance(second)))
    return (luminances[1] + .05) / (luminances[0] + .05)

def category_style(index, colorset="colorset2", canvas="#f7f7f7"):
    """Exhaust solids before finite contrast-safe border/dash/width variants."""
    if not isinstance(index, int) or index < 0:
        raise ValueError("Category index must be a nonnegative integer")
    solids = solid_colors(colorset, canvas)
    fill = solids[index % len(solids)]
    cycle = index // len(solids)
    style = {"fill": fill, "text": text_on_fill(fill, colorset), "stroke": "none",
             "strokeWidth": 0, "dash": "", "overflow": False,
             "overflowExhausted": False}
    if cycle:
        borders = [paint for paint in COLORSETS[colorset]["allowed"]
                   if paint != fill and contrast_ratio(paint, fill) >= 3]
        # Border colors vary first, then three dash types, then widths 1..3.
        # The finite pool eventually repeats; labels/symbols/split views must
        # distinguish identities beyond it rather than growing border width.
        phase = cycle - 1
        style.update(stroke=borders[phase % len(borders)],
                     strokeWidth=1 + (phase // (3 * len(borders))) % 3,
                     dash=("", "6 3", "2 3")[(phase // len(borders)) % 3],
                     overflow=True, overflowExhausted=phase >= 9 * len(borders))
    return style
