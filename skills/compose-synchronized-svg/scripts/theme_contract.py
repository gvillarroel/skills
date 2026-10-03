#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Small, dependency-free color theme contract for synchronized SVGs."""

from __future__ import annotations

import re
from typing import Mapping, Sequence
from palette_contract import nearest_color, require_color


_HEX = re.compile(r"^#[0-9a-fA-F]{6}$")
_ROLES = ("canvas", "surface", "ink", "muted", "line", "accent", "focus", "warning", "danger")
_PRESETS = {"colorset1", "colorset2", "editorial", "classic"}
_EDITORIAL = {"canvas": "#f7f7f7", "surface": "#ffffff", "ink": "#333e48", "muted": "#696969", "line": "#cfcfcf", "accent": "#9e1b32", "focus": "#6d1222", "warning": "#4f4f4f", "danger": "#9e1b32"}
_CLASSIC = {**_EDITORIAL, "accent": "#007298", "focus": "#004d66", "warning": "#994a00"}
PALETTE = ["#9e1b32", "#007298", "#994a00", "#45842a", "#652f6c", "#98700c", "#333e48", "#004d66", "#6d1222", "#294d19", "#431f47", "#9e00b3", "#e8002a", "#828282", "#696969", "#4f4f4f", "#363636", "#1c1c1c", "#000000"]
RED_NEUTRAL = ["#9e1b32", "#333e48", "#6d1222", "#828282", "#e8002a", "#696969", "#4f4f4f", "#363636", "#1c1c1c", "#000000"]

def color_for_index(index: int) -> str:
    if index < 0:
        raise ValueError("theme validation failure: color index must be nonnegative")
    return PALETTE[index % len(PALETTE)]


def contrast_ratio(hex_a: str, hex_b: str) -> float:
    """Return the standard sRGB relative-luminance contrast ratio."""
    if not isinstance(hex_a, str) or not isinstance(hex_b, str) or not _HEX.fullmatch(hex_a) or not _HEX.fullmatch(hex_b):
        raise ValueError("theme validation failure: contrast colors must be opaque six-digit hex strings")

    def luminance(value: str) -> float:
        channels = [int(value[i:i + 2], 16) / 255 for i in (1, 3, 5)]
        channels = [c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in channels]
        return 0.2126 * channels[0] + 0.7152 * channels[1] + 0.0722 * channels[2]

    first, second = luminance(hex_a), luminance(hex_b)
    light, dark = max(first, second), min(first, second)
    return (light + 0.05) / (dark + 0.05)


def _fail(message: str) -> None:
    raise ValueError(f"theme validation failure: {message}")


def mix_color(foreground: str, background: str, alpha: float) -> str:
    """Composite opaque sRGB colors, matching generated opaque CSS tint tokens."""
    _color(foreground, "foreground")
    _color(background, "background")
    if not 0 <= alpha <= 1:
        _fail("color alpha must be in 0..1")
    channels = [round(int(foreground[i:i + 2], 16) * alpha +
                      int(background[i:i + 2], 16) * (1 - alpha)) for i in (1, 3, 5)]
    return "#{:02x}{:02x}{:02x}".format(*channels)


def readable_text(backgrounds: Sequence[str], preferred: Sequence[str] = ()) -> str:
    """Choose a foreground against every actual background; preserve a passing preference."""
    if not backgrounds:
        _fail("text needs at least one known background")
    for color in [*preferred, "#000000", "#ffffff"]:
        if min(contrast_ratio(color, base) for base in backgrounds) >= 4.5:
            return color.lower()
    _fail("text has no common readable foreground; use an opaque label surface")


def safe_surface_tint(colors: Mapping[str, str], tint: str, amount: float, colorset: str = "colorset2") -> str:
    """Keep a decorative tint only as strong as the panel's foreground roles allow."""
    foregrounds = [colors[key] for key in ("ink", "muted", "accent", "warning", "danger")]
    for step in range(101):
        background = nearest_color(mix_color(tint, colors["surface"], amount * (1 - step / 100)), colorset)
        if all(contrast_ratio(color, background) >= 4.5 for color in foregrounds):
            return background
    _fail("surface tint has no readable text pairing")


def derived_theme_colors(theme: Mapping) -> dict[str, str]:
    """Generate text/background pairs without changing any caller-owned paint color."""
    colors = theme["colors"]
    colorset = "colorset1" if theme["preset"] in {"editorial", "colorset1"} else "colorset2"
    derived = {
        "surface-subtle": safe_surface_tint(colors, colors["accent"], 0.05, colorset),
        "accent-soft": safe_surface_tint(colors, colors["accent"], 0.12, colorset),
        "warning-soft": safe_surface_tint(colors, colors["warning"], 0.12, colorset),
        "danger-soft": safe_surface_tint(colors, colors["danger"], 0.08, colorset),
    }
    backgrounds = [colors["canvas"], colors["surface"], *derived.values()]
    for root, color in theme["conceptColors"].items():
        derived[f"text-value-{root}"] = readable_text(backgrounds, [color, colors["ink"]])
        derived[f"surface-value-{root}"] = safe_surface_tint(colors, color, 0.18, colorset)
    inverse = readable_text([colors["ink"]], [colors["surface"], colors["canvas"]])
    secondary = nearest_color(mix_color(colors["ink"], inverse, 0.22), colorset)
    derived["on-ink"] = inverse
    derived["on-ink-muted"] = readable_text([colors["ink"]], [secondary, inverse])
    return derived


def _color(value: object, where: str) -> str:
    if not isinstance(value, str) or not _HEX.fullmatch(value):
        _fail(f"{where} must be an opaque six-digit hex string")
    return value.lower()


def _editorial_token(index: int) -> str:
    return RED_NEUTRAL[index % len(RED_NEUTRAL)]


def resolve_theme(raw: object, value_ids: Sequence[str], token_map: Mapping[str, str] | None = None, *, default_preset: str = "editorial") -> dict:
    """Validate and resolve a theme, preserving valid caller colors byte-for-byte after case normalization."""
    if not isinstance(default_preset, str) or default_preset not in _PRESETS:
        _fail(f"unknown preset {default_preset!r}")
    if raw is None:
        raw = {}
    if not isinstance(raw, dict):
        _fail("theme must be null or an object")
    unknown = set(raw) - {"preset", "colors", "conceptColors"}
    if unknown:
        _fail(f"unknown theme field(s): {', '.join(sorted(map(str, unknown)))}")
    preset = raw.get("preset", default_preset)
    if not isinstance(preset, str) or preset not in _PRESETS:
        _fail(f"unknown preset {preset!r}")
    colorset = "colorset1" if preset in {"editorial", "colorset1"} else "colorset2"
    colors = dict(_EDITORIAL if colorset == "colorset1" else _CLASSIC)
    supplied = raw.get("colors", {})
    if not isinstance(supplied, dict):
        _fail("colors must be an object")
    unknown_roles = set(supplied) - set(_ROLES)
    if unknown_roles:
        _fail(f"unknown color role(s): {', '.join(sorted(map(str, unknown_roles)))}")
    for role, value in supplied.items():
        colors[role] = _color(value, f"colors.{role}")
        require_color(colors[role], colorset)

    if not isinstance(value_ids, Sequence) or isinstance(value_ids, (str, bytes)):
        _fail("value_ids must be an ordered sequence")
    if any(not isinstance(v, str) or not v for v in value_ids) or len(set(value_ids)) != len(value_ids):
        _fail("value_ids must contain unique non-empty strings")
    if token_map is None:
        mapping = {v: v for v in value_ids}
    else:
        if not isinstance(token_map, Mapping):
            _fail("token_map must be an object mapping every value ID exactly once")
        mapping = dict(token_map)
        if set(mapping) != set(value_ids):
            _fail("token_map must map every value ID exactly once")
    roots: list[str] = []
    for value_id in value_ids:
        root = mapping[value_id]
        if not isinstance(root, str) or not root:
            _fail(f"token_map root for {value_id!r} must be a non-empty string")
        if root not in value_ids:
            _fail(f"token_map root {root!r} for {value_id!r} is not a canonical value ID")
        if root not in roots:
            roots.append(root)
    supplied_concepts = raw.get("conceptColors", {})
    if not isinstance(supplied_concepts, dict):
        _fail("conceptColors must be an object")
    for key, value in supplied_concepts.items():
        if key not in roots:
            root = mapping.get(key)
            suffix = f"; {key!r} is an alias owned by root {root!r}" if root else ""
            _fail(f"concept color key {key!r} is not a root token{suffix}")
    concepts = {}
    for index, root in enumerate(roots):
        concepts[root] = _color(supplied_concepts[root], f"conceptColors.{root}") if root in supplied_concepts else (color_for_index(index) if colorset == "colorset2" else _editorial_token(index))
        require_color(concepts[root], colorset)
    for role in ("ink", "muted", "accent", "warning", "danger"):
        if min(contrast_ratio(colors[role], base) for base in (colors["canvas"], colors["surface"])) < 4.5:
            _fail(f"colors.{role} has insufficient contrast against canvas and surface")
    for role in ("focus",):
        if min(contrast_ratio(colors[role], base) for base in (colors["canvas"], colors["surface"])) < 3:
            _fail(f"colors.{role} has insufficient contrast against canvas and surface")
    for root, value in concepts.items():
        if min(contrast_ratio(value, base) for base in (colors["canvas"], colors["surface"])) < 3:
            _fail(f"conceptColors.{root} has insufficient contrast against canvas and surface")
    return {"preset": preset, "colors": colors, "conceptColors": concepts}
