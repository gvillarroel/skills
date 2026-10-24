#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["xy==0.0.8"]
# ///
"""Canonical colorset helpers for XY 0.0.8; usable without the repository."""

from __future__ import annotations

from copy import deepcopy
import json
import math
from pathlib import Path
import re
from typing import Any, Iterable

__all__ = [
    "load_palette", "categorical_colors", "sequential_colors", "binned_colors",
    "text_on", "theme", "css", "legend_style",
]


def load_palette(name: str = "colorset1") -> dict[str, Any]:
    """Load an independent palette copy; reject misspelled names explicitly.

    For a portable source download, keep ``colorsets.json`` beside this module.
    The normal skill bundle keeps it in ``assets/palettes/``.
    """
    if name not in ("colorset1", "colorset2"):
        raise ValueError("Palette must be 'colorset1' or 'colorset2'")
    module = Path(__file__).resolve()
    adjacent = module.with_name("colorsets.json")
    bundled = module.parent.parent / "assets" / "palettes" / "colorsets.json"
    source = adjacent if adjacent.is_file() else bundled
    document = json.loads(source.read_text(encoding="utf-8"))
    return deepcopy(document["colorsets"][name])


def categorical_colors(
    name: str = "colorset1", count: int | None = None,
    background: str | None = None,
) -> list[str]:
    """Return canonical solids excluding the actual canvas, without cycling.

    Colorset1 allocates primary red, interleaved grays, white, then remaining
    reds/pink. Keep a stable category-to-index map across charts and facets.
    When all available colors are used, add a documented shape/dash/width
    channel rather than silently repeating an indistinguishable fill.
    """
    palette = load_palette(name)
    canvas = palette["roles"]["background"] if background is None else background
    if not isinstance(canvas, str):
        raise ValueError("Background must be a CSS hex color string")
    canvas = _hex(canvas)
    colors = [value for value in palette["solidSequence"] if value != canvas]
    if count is None:
        return colors
    if isinstance(count, bool) or not isinstance(count, int) or count < 0:
        raise ValueError("Category count must be a non-negative integer")
    if count > len(colors):
        raise ValueError(
            f"{name} has {len(colors)} usable solid colors on {canvas}; "
            "add an explicit secondary encoding after using all solids"
        )
    return colors[:count]


def sequential_colors(name: str = "colorset1") -> list[str]:
    """Return four exact ordered stops, from low to high magnitude.

    Passing these to ``colormap=`` creates a continuous interpolated ramp in XY.
    Use ``binned_colors`` with separate constant-color marks for exact paints.
    """
    load_palette(name)  # Validate even though the compact stop list is fixed.
    if name == "colorset1":
        return ["#e7e7e7", "#9c9c9c", "#9e1b32", "#6d1222"]
    return ["#cdf3ff", "#00ace6", "#007298", "#004d66"]


def binned_colors(
    values: Iterable[float], name: str = "colorset1", bins: int = 4,
    domain: tuple[float, float] | None = None,
) -> list[str | None]:
    """Map values into exact equal-width sequential paints without altering data.

    ``None`` marks NaN/infinity, which the caller should omit from geometry.
    An explicit finite increasing domain keeps bins stable across panels. Values
    outside it clamp to endpoint bins. A constant inferred domain uses the
    middle bin. The original numeric values remain the tooltip/data contract.
    """
    stops = sequential_colors(name)
    if isinstance(bins, bool) or not isinstance(bins, int) or not 2 <= bins <= len(stops):
        raise ValueError("Bins must be an integer from 2 to 4")
    selected = [stops[round(i * (len(stops) - 1) / (bins - 1))] for i in range(bins)]
    numbers = [float(value) for value in values]
    finite = [value for value in numbers if math.isfinite(value)]
    if domain is None:
        low, high = (min(finite), max(finite)) if finite else (0.0, 0.0)
    else:
        if len(domain) != 2:
            raise ValueError("Domain must contain two finite increasing numbers")
        low, high = map(float, domain)
        if not math.isfinite(low) or not math.isfinite(high) or high <= low:
            raise ValueError("Domain must contain two finite increasing numbers")
    output: list[str | None] = []
    for value in numbers:
        if not math.isfinite(value):
            output.append(None)
        elif high == low:
            output.append(selected[bins // 2])
        else:
            index = math.floor((value - low) / (high - low) * bins)
            output.append(selected[max(0, min(bins - 1, index))])
    return output


def _hex(value: str) -> str:
    if not isinstance(value, str) or re.fullmatch(r"#[0-9a-fA-F]{6}", value) is None:
        raise ValueError("Expected an opaque six-digit hex color, for example '#f7f7f7'")
    return value.lower()


def text_on(fill: str) -> str:
    """Choose the higher-contrast black/white text on an opaque hex fill."""
    paint = _hex(fill)
    channels = [int(paint[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    linear = [v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4 for v in channels]
    luminance = sum(c * w for c, w in zip(linear, (0.2126, 0.7152, 0.0722)))
    return "#000000" if (luminance + 0.05) / 0.05 >= 1.05 / (luminance + 0.05) else "#ffffff"


def _chrome_style(name: str) -> dict[str, str]:
    roles = load_palette(name)["roles"]
    return {
        "--xy-badge-text": "#000000", "--xy-badge-bg": roles["surface"],
        "--xy-badge-shadow": "none", "--xy-modebar-bg": roles["surface"],
        "--xy-modebar-menu-bg": roles["surface"], "--xy-modebar-hover": roles["quiet"],
        "--xy-modebar-focus": roles["primary"], "--xy-modebar-text": "#000000",
        "--xy-modebar-text-strong": "#000000", "--xy-modebar-text-soft": "#000000",
        "--xy-modebar-text-subtle": roles["muted"], "--xy-modebar-border": roles["line"],
        "--xy-modebar-separator": roles["line"], "--xy-modebar-active": roles["quiet"],
        "--xy-modebar-shadow": "none", "--xy-modebar-menu-shadow": "none",
        "--xy-modebar-button-shadow": "none", "--xy-selection": roles["primary"],
        "--xy-selection-fill": roles["accentSoft"],
    }


def legend_style(name: str = "colorset1", background: str | None = None) -> dict[str, str | int]:
    """Pass to ``xy.legend(style=...)`` to remove the native default gray frame."""
    roles = load_palette(name)["roles"]
    canvas = roles["background"] if background is None else _hex(background)
    # Native XY 0.0.8 draws a 1px frame even for border-width:0. An explicitly
    # transparent legend background is the shared public path that omits it.
    return {"background": "transparent", "color": text_on(canvas),
            "border-color": roles["line"], "border-width": 0}


def theme(
    name: str = "colorset1", background: str | None = None,
    *, style: dict[str, str | int | float] | None = None, **overrides: Any,
) -> Any:
    """Build a real public ``xy.theme`` with canonical series and chrome paints.

    Explicit caller overrides win; the caller owns their source-style contract.
    Use ``css(name)`` on HTML/Chromium exports to remove inherited tooltip shadow.
    """
    import xy

    roles = load_palette(name)["roles"]
    canvas = roles["background"] if background is None else _hex(background)
    tokens: dict[str, Any] = {
        "background": canvas, "plot_background": canvas,
        "grid_color": roles["line"], "axis_color": roles["muted"],
        "text_color": text_on(canvas), "crosshair_color": roles["muted"],
        "selection_color": roles["primary"], "selection_fill": roles["accentSoft"],
        "accent": roles["primary"], "annotation_text": text_on(canvas),
        "badge_bg": roles["surface"], "badge_text": "#000000",
        "counts": roles["primary"], "critical": roles["accent"], "focus": roles["primary"],
        "legend_bg": roles["surface"], "modebar_active": roles["quiet"],
        "modebar_bg": roles["surface"], "modebar_focus": roles["primary"],
        "tooltip_bg": "#1c1c1c", "tooltip_text": "#ffffff",
        "zoom_selection": roles["primary"], "zoom_selection_fill": roles["accentSoft"],
        "palette": categorical_colors(name, background=canvas),
    }
    tokens.update(overrides)
    root_style: dict[str, str | int | float] = _chrome_style(name)
    root_style.update(style or {})
    return xy.theme(style=root_style, **tokens)


def css(name: str = "colorset1") -> str:
    """Supplement public theme tokens for XY's DOM-only shadows/chrome variables.

    Pass to ``to_html(custom_css=...)`` and Chromium image export; native SVG
    ignores this CSS and uses the theme/mark/axis properties instead.
    """
    declarations = ";".join(f"{key}:{value}" for key, value in _chrome_style(name).items())
    return (
        f".xy{{{declarations}}}\n"
        '.xy [data-xy-slot="tooltip"]{box-shadow:none}\n'
        '.xy [data-xy-slot="modebar"] button:focus-visible{outline-offset:2px}\n'
    )


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--colorset", choices=("colorset1", "colorset2"), default="colorset1")
    args = parser.parse_args()
    print(json.dumps(load_palette(args.colorset), indent=2))
