#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Measure palette colors that are actually painted in Mermaid PNG renders."""

from __future__ import annotations

import colorsys
import struct
import zlib
from dataclasses import dataclass
from pathlib import Path


COLOR_GROUPS = {
    "primary": ("#9e1b32", "#6d1222", "#ffccd5", "#e8002a"),
    "accent": ("#007298", "#cdf3ff"),
    "warning": ("#e77204", "#ffe5cc"),
    "success": ("#45842a", "#dbffcc"),
    "info": ("#00ace6",),
    "special": ("#652f6c", "#f9ccff"),
}

COLORSET_GROUPS = {
    "colorset1": ("primary",),
    "colorset2": ("accent", "warning", "success", "info", "special"),
}

COUNTERFACTUAL_COLORS = {
    "#9e1b32": "#10f020",
    "#6d1222": "#20e0f0",
    "#ffccd5": "#7020f0",
    "#e8002a": "#f0e010",
    "#007298": "#ff00aa",
    "#cdf3ff": "#4a00ff",
    "#e77204": "#00ff66",
    "#ffe5cc": "#0066ff",
    "#45842a": "#ffcc00",
    "#dbffcc": "#2200ff",
    "#00ace6": "#ff0066",
    "#652f6c": "#00ffcc",
    "#f9ccff": "#006600",
}


@dataclass(frozen=True)
class Raster:
    width: int
    height: int
    rgba: bytes


def _paeth(left: int, up: int, upper_left: int) -> int:
    estimate = left + up - upper_left
    left_distance = abs(estimate - left)
    up_distance = abs(estimate - up)
    upper_left_distance = abs(estimate - upper_left)
    if left_distance <= up_distance and left_distance <= upper_left_distance:
        return left
    if up_distance <= upper_left_distance:
        return up
    return upper_left


def read_png(path: Path) -> Raster:
    """Decode a non-interlaced, 8-bit PNG using only the standard library."""

    payload = path.read_bytes()
    if not payload.startswith(b"\x89PNG\r\n\x1a\n"):
        raise ValueError(f"Not a PNG file: {path}")

    position = 8
    ihdr: bytes | None = None
    palette: bytes | None = None
    transparency = b""
    compressed = bytearray()
    while position < len(payload):
        if position + 12 > len(payload):
            raise ValueError("Truncated PNG chunk")
        length = struct.unpack(">I", payload[position : position + 4])[0]
        kind = payload[position + 4 : position + 8]
        data_start = position + 8
        data_end = data_start + length
        crc_end = data_end + 4
        if crc_end > len(payload):
            raise ValueError("Truncated PNG chunk payload")
        data = payload[data_start:data_end]
        expected_crc = struct.unpack(">I", payload[data_end:crc_end])[0]
        actual_crc = zlib.crc32(kind + data) & 0xFFFFFFFF
        if actual_crc != expected_crc:
            raise ValueError(f"PNG CRC mismatch in {kind.decode('ascii', errors='replace')}")
        if kind == b"IHDR":
            ihdr = data
        elif kind == b"PLTE":
            palette = data
        elif kind == b"tRNS":
            transparency = data
        elif kind == b"IDAT":
            compressed.extend(data)
        elif kind == b"IEND":
            break
        position = crc_end

    if ihdr is None or len(ihdr) != 13:
        raise ValueError("PNG is missing a valid IHDR chunk")
    width, height, bit_depth, color_type, compression, filter_method, interlace = struct.unpack(
        ">IIBBBBB", ihdr
    )
    if not width or not height:
        raise ValueError("PNG dimensions must be positive")
    if bit_depth != 8 or compression != 0 or filter_method != 0 or interlace != 0:
        raise ValueError("Only non-interlaced 8-bit PNG images are supported")

    channels_by_type = {0: 1, 2: 3, 3: 1, 4: 2, 6: 4}
    if color_type not in channels_by_type:
        raise ValueError(f"Unsupported PNG color type: {color_type}")
    channels = channels_by_type[color_type]
    stride = width * channels
    raw = zlib.decompress(bytes(compressed))
    expected_size = height * (stride + 1)
    if len(raw) != expected_size:
        raise ValueError(f"Unexpected PNG payload size: {len(raw)} != {expected_size}")

    decoded_rows: list[bytes] = []
    previous = bytes(stride)
    cursor = 0
    for _ in range(height):
        filter_type = raw[cursor]
        cursor += 1
        encoded = raw[cursor : cursor + stride]
        cursor += stride
        decoded = bytearray(stride)
        for index, value in enumerate(encoded):
            left = decoded[index - channels] if index >= channels else 0
            up = previous[index]
            upper_left = previous[index - channels] if index >= channels else 0
            if filter_type == 0:
                predictor = 0
            elif filter_type == 1:
                predictor = left
            elif filter_type == 2:
                predictor = up
            elif filter_type == 3:
                predictor = (left + up) // 2
            elif filter_type == 4:
                predictor = _paeth(left, up, upper_left)
            else:
                raise ValueError(f"Unsupported PNG filter: {filter_type}")
            decoded[index] = (value + predictor) & 0xFF
        row = bytes(decoded)
        decoded_rows.append(row)
        previous = row

    rgba = bytearray()
    transparent_gray = struct.unpack(">H", transparency)[0] if color_type == 0 and len(transparency) >= 2 else None
    transparent_rgb = struct.unpack(">HHH", transparency[:6]) if color_type == 2 and len(transparency) >= 6 else None
    for row in decoded_rows:
        if color_type == 6:
            rgba.extend(row)
        elif color_type == 4:
            for index in range(0, len(row), 2):
                gray, alpha = row[index : index + 2]
                rgba.extend((gray, gray, gray, alpha))
        elif color_type == 2:
            for index in range(0, len(row), 3):
                red, green, blue = row[index : index + 3]
                alpha = 0 if transparent_rgb == (red, green, blue) else 255
                rgba.extend((red, green, blue, alpha))
        elif color_type == 0:
            for gray in row:
                alpha = 0 if transparent_gray == gray else 255
                rgba.extend((gray, gray, gray, alpha))
        else:
            if palette is None or len(palette) % 3:
                raise ValueError("Indexed PNG is missing a valid palette")
            for palette_index in row:
                offset = palette_index * 3
                if offset + 3 > len(palette):
                    raise ValueError("Indexed PNG references a missing palette entry")
                red, green, blue = palette[offset : offset + 3]
                alpha = transparency[palette_index] if palette_index < len(transparency) else 255
                rgba.extend((red, green, blue, alpha))

    return Raster(width=width, height=height, rgba=bytes(rgba))


def _rgb(hex_color: str) -> tuple[int, int, int]:
    return tuple(bytes.fromhex(hex_color.removeprefix("#")))  # type: ignore[return-value]


def _lighten_rgb(hex_color: str, amount: float) -> tuple[int, int, int]:
    red, green, blue = (channel / 255.0 for channel in _rgb(hex_color))
    hue, lightness, saturation = colorsys.rgb_to_hls(red, green, blue)
    lightness = min(1.0, lightness + amount / 100.0)
    adjusted = colorsys.hls_to_rgb(hue, lightness, saturation)
    return tuple(round(channel * 255) for channel in adjusted)


def _token_candidates(tokens: tuple[str, ...]) -> dict[str, tuple[int, int, int]]:
    candidates: dict[str, tuple[int, int, int]] = {}
    for token in tokens:
        candidates[token] = _rgb(token)
        # Mermaid 11.16.0 Kanban paints each reachable cScale color through
        # khroma lighten(color, 10). Keep the canonical token as the reporting
        # identity while accepting that renderer-owned visible transformation.
        candidates[f"{token}@lighten10"] = _lighten_rgb(token, 10)
    return candidates


def _canonical_token(candidate: str) -> str:
    return candidate.split("@", 1)[0]


def _signature_tokens(colorset: str) -> tuple[str, ...]:
    try:
        groups = COLORSET_GROUPS[colorset]
    except KeyError as error:
        raise ValueError(f"Unknown colorset: {colorset}") from error
    return tuple(color for group in groups for color in COLOR_GROUPS[group])


def make_counterfactual_source(source: str, colorset: str) -> tuple[str, int]:
    """Replace palette-signature declarations with sentinel colors."""

    replacements = {color.casefold(): COUNTERFACTUAL_COLORS[color] for color in _signature_tokens(colorset)}
    chunks: list[str] = []
    replacement_count = 0
    cursor = 0
    import re

    for match in re.finditer(r"#[0-9a-fA-F]{6}", source):
        chunks.append(source[cursor : match.start()])
        original = match.group(0)
        replacement = replacements.get(original.casefold())
        if replacement is None:
            chunks.append(original)
        else:
            chunks.append(replacement)
            replacement_count += 1
        cursor = match.end()
    chunks.append(source[cursor:])
    return "".join(chunks), replacement_count


def _nearest_token(
    red: int,
    green: int,
    blue: int,
    candidates: dict[str, tuple[int, int, int]],
    tolerance: int,
) -> str | None:
    best: tuple[int, str] | None = None
    for token, (expected_red, expected_green, expected_blue) in candidates.items():
        distance = max(
            abs(red - expected_red),
            abs(green - expected_green),
            abs(blue - expected_blue),
        )
        if distance <= tolerance and (best is None or distance < best[0]):
            best = (distance, token)
    return best[1] if best else None


def analyze_visible_palette(
    raster: Raster,
    colorset: str,
    *,
    required_groups: tuple[str, ...],
    min_distinct_colors: int,
    min_pixels_per_color: float,
    min_palette_pixels: float,
    min_palette_ratio: float,
    tolerance: int = 6,
) -> dict[str, object]:
    expected_tokens = _signature_tokens(colorset)
    expected_rgb = _token_candidates(expected_tokens)
    forbidden_tokens = _signature_tokens("colorset2") if colorset == "colorset1" else ()
    forbidden_rgb = _token_candidates(forbidden_tokens)
    token_pixels = {token: 0.0 for token in expected_tokens}
    forbidden_pixels = {token: 0.0 for token in forbidden_tokens}
    painted_pixels = 0.0

    rgba = raster.rgba
    for index in range(0, len(rgba), 4):
        red, green, blue, alpha = rgba[index : index + 4]
        if alpha < 8:
            continue
        weight = alpha / 255.0
        painted_pixels += weight
        candidate = _nearest_token(red, green, blue, expected_rgb, tolerance)
        if candidate is not None:
            token_pixels[_canonical_token(candidate)] += weight
            continue
        # Forbidden palette tokens must be exact. Browser font anti-aliasing can
        # create a few near-matching fringe pixels even when the SVG never
        # declares the forbidden color; real fills and strokes retain exact
        # full-opacity token pixels after rasterization.
        forbidden_candidate = _nearest_token(red, green, blue, forbidden_rgb, 0)
        if forbidden_candidate is not None:
            forbidden_pixels[_canonical_token(forbidden_candidate)] += weight

    visible_tokens = sorted(
        token for token, count in token_pixels.items() if count >= min_pixels_per_color
    )
    palette_pixels = sum(token_pixels.values())
    palette_ratio = palette_pixels / painted_pixels if painted_pixels else 0.0
    group_pixels = {
        group: sum(token_pixels.get(token, 0.0) for token in COLOR_GROUPS[group])
        for group in COLORSET_GROUPS[colorset]
    }
    required_groups_missing = sorted(
        group
        for group in required_groups
        if group not in group_pixels or group_pixels[group] < min_pixels_per_color
    )
    unexpected_token_pixels = {
        token: count
        for token, count in forbidden_pixels.items()
        if count >= min_pixels_per_color
    }
    unexpected_pixels = sum(unexpected_token_pixels.values())
    ok = bool(
        painted_pixels > 0
        and len(visible_tokens) >= min_distinct_colors
        and palette_pixels >= min_palette_pixels
        and palette_ratio >= min_palette_ratio
        and not required_groups_missing
        and (colorset != "colorset1" or not unexpected_token_pixels)
    )
    return {
        "ok": ok,
        "width": raster.width,
        "height": raster.height,
        "effectivePaintedPixels": round(painted_pixels, 3),
        "effectivePalettePixels": round(palette_pixels, 3),
        "paletteCoverageRatio": round(palette_ratio, 6),
        "visibleDistinctColors": len(visible_tokens),
        "visibleTokens": visible_tokens,
        "tokenEffectivePixels": {
            token: round(count, 3) for token, count in token_pixels.items() if count >= 0.5
        },
        "groupEffectivePixels": {
            group: round(count, 3) for group, count in group_pixels.items()
        },
        "missingRequiredGroups": required_groups_missing,
        "unexpectedExtendedEffectivePixels": round(unexpected_pixels, 3),
        "unexpectedExtendedTokenPixels": {
            token: round(count, 3)
            for token, count in unexpected_token_pixels.items()
        },
    }


def compare_rasters(actual: Raster, counterfactual: Raster, *, tolerance: int = 8) -> dict[str, object]:
    if (actual.width, actual.height) != (counterfactual.width, counterfactual.height):
        return {
            "dimensionsMatch": False,
            "effectiveDifferentPixels": 0.0,
            "differenceRatio": 0.0,
        }

    effective_different = 0.0
    effective_union = 0.0
    for index in range(0, len(actual.rgba), 4):
        actual_red, actual_green, actual_blue, actual_alpha = actual.rgba[index : index + 4]
        other_red, other_green, other_blue, other_alpha = counterfactual.rgba[index : index + 4]
        union_weight = max(actual_alpha, other_alpha) / 255.0
        effective_union += union_weight

        actual_composite = (
            (actual_red * actual_alpha + 255 * (255 - actual_alpha) + 127) // 255,
            (actual_green * actual_alpha + 255 * (255 - actual_alpha) + 127) // 255,
            (actual_blue * actual_alpha + 255 * (255 - actual_alpha) + 127) // 255,
        )
        other_composite = (
            (other_red * other_alpha + 255 * (255 - other_alpha) + 127) // 255,
            (other_green * other_alpha + 255 * (255 - other_alpha) + 127) // 255,
            (other_blue * other_alpha + 255 * (255 - other_alpha) + 127) // 255,
        )
        if max(abs(left - right) for left, right in zip(actual_composite, other_composite)) > tolerance:
            effective_different += union_weight

    difference_ratio = effective_different / effective_union if effective_union else 0.0
    return {
        "dimensionsMatch": True,
        "effectiveDifferentPixels": round(effective_different, 3),
        "differenceRatio": round(difference_ratio, 6),
    }


def evaluate_visual_palette(
    actual_png: Path,
    counterfactual_png: Path,
    colorset: str,
    visual_contract: dict[str, object],
) -> dict[str, object]:
    actual = read_png(actual_png)
    counterfactual = read_png(counterfactual_png)
    palette = analyze_visible_palette(
        actual,
        colorset,
        required_groups=tuple(str(group) for group in visual_contract.get("requiredGroups", [])),
        min_distinct_colors=int(visual_contract.get("minDistinctColors", 1)),
        min_pixels_per_color=float(visual_contract.get("minPixelsPerColor", 24.0)),
        min_palette_pixels=float(visual_contract.get("minPaletteEffectivePixels", 64.0)),
        min_palette_ratio=float(visual_contract.get("minPaletteCoverageRatio", 0.001)),
    )
    influence = compare_rasters(actual, counterfactual)
    influence_ok = bool(
        influence["dimensionsMatch"]
        and float(influence["effectiveDifferentPixels"])
        >= float(visual_contract.get("minInfluenceEffectivePixels", 32.0))
        and float(influence["differenceRatio"])
        >= float(visual_contract.get("minInfluenceRatio", 0.0005))
    )
    return {
        "ok": bool(palette["ok"] and influence_ok),
        "palette": palette,
        "influence": {**influence, "ok": influence_ok},
        "contract": visual_contract,
    }
