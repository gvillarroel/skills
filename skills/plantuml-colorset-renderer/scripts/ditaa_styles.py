#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["pillow>=11.0"]
# ///
"""Style supported native Ditaa rasters from their unchanged ASCII geometry.

The native 1.2026.6 parser supports only cRGB tags. They are temporary render
seeds, not delivery colors. Accept disjoint +---+ / | | boxes with optional
{io}, {s}, or {d} glyphs; reject geometry that cannot be identified safely.
"""
from __future__ import annotations

from collections import deque
import re
from pathlib import Path

from palette_paints import COLORSETS, nearest, readable_text, rgb, solid_colors, solid_style

COLOR_TAG = re.compile(r"c[A-Fa-f0-9]{3}(?![A-Fa-f0-9])")
GLYPH_TAG = re.compile(r"\{([^}]+)\}")
TOP = re.compile(r"\+[-+]+\+")
SUPPORTED_GLYPHS = {"io", "s", "d"}


def _seed(fill: str) -> str:
    return "c" + "".join(f"{max(0, min(15, round(channel / 17))):X}" for channel in rgb(fill))


def _body_lines(source: str) -> tuple[list[str], int, int, float]:
    lines = source.splitlines()
    starts = [index for index, line in enumerate(lines) if re.match(r"(?i)^\s*@startditaa\b", line)]
    ends = [index for index, line in enumerate(lines) if re.match(r"(?i)^\s*@endditaa\b", line)]
    if len(starts) != 1 or len(ends) != 1 or ends[0] <= starts[0]:
        raise ValueError("Ditaa styling requires exactly one @startditaa/@endditaa block.")
    start, end = starts[0], ends[0]
    body = lines[start + 1:end]
    if not body or any("\t" in line for line in body):
        raise ValueError("Ditaa styling requires non-empty ASCII rows without tabs.")
    indent = min(len(line) - len(line.lstrip(" ")) for line in body)
    body = [line[indent:] for line in body]
    scale_match = re.search(r"\bscale=([\d.]+)", lines[start])
    scale = float(scale_match.group(1)) if scale_match else 1.0
    if not .1 <= scale <= 10:
        raise ValueError("Ditaa styling supports scale values from 0.1 through 10.")
    return body, start, end, scale


def prepare_ditaa_source(source: str, colorset: str = "colorset1") -> tuple[str, dict]:
    """Add shadow-free native seed tags only in proven free interior cells."""
    if colorset not in COLORSETS:
        raise ValueError("Unknown Ditaa colorset: " + colorset)
    body, start, end, scale = _body_lines(source)
    if any(re.search(r"c[A-Fa-f0-9]{6}\b", row) for row in body):
        raise ValueError("Native Ditaa accepts three-digit cRGB colors; six-digit tags would corrupt text and geometry.")
    width = max(map(len, body))
    grid = [line.ljust(width) for line in body]
    boxes = []
    consumed_tops = set()
    for top, row in enumerate(grid):
        for match in TOP.finditer(row):
            left, right = match.start(), match.end() - 1
            if (top, left, right) in consumed_tops:
                continue
            bottom = None
            for y in range(top + 1, len(grid)):
                line = grid[y]
                if line[left] == "+" and line[right] == "+" and re.fullmatch(r"[-+]+", line[left + 1:right]):
                    bottom = y
                    break
                if line[left] != "|" or line[right] != "|":
                    break
            if bottom is None or bottom - top < 2:
                continue
            consumed_tops.add((bottom, left, right))
            interior = "\n".join(grid[y][left + 1:right] for y in range(top + 1, bottom))
            glyphs = GLYPH_TAG.findall(interior)
            if len(glyphs) > 1 or any(glyph not in SUPPORTED_GLYPHS for glyph in glyphs):
                raise ValueError("Ditaa styling supports one optional {io}, {s}, or {d} glyph per box.")
            if any(character in interior for character in "+|/\\"):
                raise ValueError("Ditaa styling requires disjoint boxes without nested boundaries or internal divider lines.")
            for previous in boxes:
                if max(left, previous["left"]) <= min(right, previous["right"]) and max(top, previous["top"]) <= min(bottom, previous["bottom"]):
                    raise ValueError("Ditaa styling does not support overlapping boxes or shared border cells.")
            supplied = COLOR_TAG.findall(interior)
            if len(supplied) > 1:
                raise ValueError("Ditaa styling supports at most one native cRGB color tag per box.")
            index = len(boxes)
            if index >= len(solid_colors(colorset)):
                raise ValueError("Ditaa has exhausted the unique solid fills in this colorset; split the diagram or use a native SVG family for outline overflow.")
            target = solid_style(index, colorset)["fill"]
            # Native 1.2026.6 recognizes uppercase A-F; lowercase hex remains
            # visible text. Normalize this four-cell markup without moving it.
            tag = "c" + supplied[0][1:].upper() if supplied else _seed(target)
            native = "#" + "".join(character * 2 for character in tag[1:]).lower()
            if supplied:
                target = native if native in COLORSETS[colorset]["allowed"] else nearest(native, colorset)
                if target == "#ffffff":
                    # A white source seed cannot remain a visible borderless node
                    # on this renderer's white canvas.
                    target = solid_style(index, colorset)["fill"]
            tag_position = None
            if supplied:
                for y in range(top + 1, bottom):
                    color_match = COLOR_TAG.search(grid[y][left + 1:right])
                    if color_match:
                        x = left + 1 + color_match.start()
                        grid[y] = grid[y][:x] + tag + grid[y][x + 4:]
                        tag_position = [x, y]
                        break
            else:
                # Prefer a markup row, keeping labels and every boundary cell intact.
                candidates = list(range(top + 1, bottom))
                candidates.sort(key=lambda y: (not bool(GLYPH_TAG.search(grid[y][left + 1:right])), y))
                for y in candidates:
                    for free in re.finditer(r" {4,}", grid[y][left + 1:right]):
                        x = left + 1 + free.start()
                        if x == left + 1:
                            x += 1
                        if x + 4 <= left + 1 + free.end():
                            grid[y] = grid[y][:x] + tag + grid[y][x + 4:]
                            tag_position = [x, y]
                            break
                    if tag_position:
                        break
                if tag_position is None:
                    raise ValueError("Ditaa box needs four free interior spaces for a native color tag; add an empty interior row without moving connectors.")
            boxes.append({"left": left, "right": right, "top": top, "bottom": bottom, "glyph": glyphs[0] if glyphs else None,
                          "nativeColor": native, "fill": target, "text": readable_text(target), "tagPosition": tag_position,
                          "explicitColor": bool(supplied), "categoryIndex": index})
    if not boxes:
        raise ValueError("Ditaa styling requires at least one supported closed +---+ / | | box.")
    accepted_borders = {(box[side], box["left"], box["right"]) for box in boxes for side in ("top", "bottom")}
    for y, row in enumerate(grid):
        for candidate in re.finditer(r"\+[+\-.:=]+\+", row):
            if (y, candidate.start(), candidate.end() - 1) not in accepted_borders:
                raise ValueError("Ditaa styling found an unsupported or unclosed box boundary; every box must satisfy the supported disjoint box contract.")
    # Reject unhandled boundary geometry instead of styling only part of a diagram.
    for y, row in enumerate(grid):
        for x, character in enumerate(row):
            if character in "/\\" and not any(box["left"] < x < box["right"] and box["top"] < y < box["bottom"] for box in boxes):
                raise ValueError("Ditaa automatic styling does not support rounded/sloped ASCII borders; use the supported box contract.")
    original = source.splitlines()
    directive = original[start]
    if not re.search(r"(?:^|\s)(?:-S|--no-shadows)(?:\s|$|,)", directive):
        directive += " -S"
    indent = min(len(line) - len(line.lstrip(" ")) for line in original[start + 1:end])
    prepared = original[:start] + [directive] + [" " * indent + row[:max(len(body[y]), len(row.rstrip()))] for y, row in enumerate(grid)] + original[end:]
    plan = {"schemaVersion": 1, "colorset": colorset, "grid": grid, "width": width, "height": len(grid), "scale": scale, "boxes": boxes}
    return "\n".join(prepared) + "\n", plan


def _canvas_mask(pixels, width: int, height: int) -> bytearray:
    """Find white canvas connected to the image edge, excluding white glyphs."""
    result = bytearray(width * height)
    queue = deque()
    for x in range(width):
        queue.extend((x, (height - 1) * width + x))
    for y in range(height):
        queue.extend((y * width, y * width + width - 1))
    while queue:
        index = queue.popleft()
        if result[index] or pixels[index] != (255, 255, 255):
            continue
        result[index] = 1
        x, y = index % width, index // width
        if x: queue.append(index - 1)
        if x + 1 < width: queue.append(index + 1)
        if y: queue.append(index - width)
        if y + 1 < height: queue.append(index + width)
    return result


def _connector_mask(plan: dict, width: int, height: int, cell_width: float, cell_height: float) -> bytearray:
    mask = bytearray(width * height)
    for y, row in enumerate(plan["grid"]):
        for x, char in enumerate(row):
            if char not in "-|<>^vV:=*":
                continue
            if any(box["left"] <= x <= box["right"] and box["top"] <= y <= box["bottom"] for box in plan["boxes"]):
                continue
            x0, x1 = max(0, round((x + 1.5) * cell_width)), min(width, round((x + 3.5) * cell_width) + 1)
            y0, y1 = max(0, round((y + 1.5) * cell_height)), min(height, round((y + 3.5) * cell_height) + 1)
            for py in range(y0, y1):
                mask[py * width + x0:py * width + x1] = b"\1" * (x1 - x0)
    return mask


def _canvas_distance(canvas: bytearray, width: int, height: int, radius: int) -> bytearray:
    """Measure a bounded eight-neighbor distance from the exterior canvas."""
    distance = bytearray([radius + 1]) * len(canvas)
    queue = deque()
    for index, outside in enumerate(canvas):
        if outside:
            distance[index] = 0
            queue.append(index)
    while queue:
        index = queue.popleft()
        next_distance = distance[index] + 1
        if next_distance > radius:
            continue
        x, y = index % width, index // width
        for yy in range(max(0, y - 1), min(height, y + 2)):
            for xx in range(max(0, x - 1), min(width, x + 2)):
                neighbor = yy * width + xx
                if next_distance < distance[neighbor]:
                    distance[neighbor] = next_distance
                    queue.append(neighbor)
    return distance


def finish_ditaa_png(path: Path | str, plan: dict) -> dict:
    """Repaint proven native box regions while keeping unfilled drawing intact."""
    from PIL import Image
    path = Path(path)
    with Image.open(path) as input_image:
        image = input_image.convert("RGB")
    width, height = image.size
    expected_width = (plan["width"] + 4) * 10 * plan["scale"]
    expected_height = (plan["height"] + 4) * 14 * plan["scale"]
    if abs(width - expected_width) > 2 or abs(height - expected_height) > 2:
        raise ValueError("Ditaa native raster dimensions do not match the source-backed cell contract; preserve output and inspect the native renderer.")
    cell_width, cell_height = width / (plan["width"] + 4), height / (plan["height"] + 4)
    pixels = list(image.get_flattened_data() if hasattr(image, "get_flattened_data") else image.getdata())
    canvas = _canvas_mask(pixels, width, height)
    connectors = _connector_mask(plan, width, height, cell_width, cell_height)
    contour_radius = max(2, round(plan["scale"] * 2))
    exterior_distance = _canvas_distance(canvas, width, height, contour_radius)
    painted = contours = 0
    for box in plan["boxes"]:
        native, fill, foreground = rgb(box["nativeColor"]), rgb(box["fill"]), rgb(box["text"])
        # Half-cell margins include native IO slopes and cylinder/document curves.
        x0, x1 = max(0, round((box["left"] + 2) * cell_width) - contour_radius), min(width, round((box["right"] + 3) * cell_width) + contour_radius)
        y0, y1 = max(0, round((box["top"] + 2) * cell_height) - contour_radius), min(height, round((box["bottom"] + 3) * cell_height) + contour_radius)
        seeds = sum(pixels[y * width + x] == native and not canvas[y * width + x] for y in range(y0, y1) for x in range(x0, x1))
        if seeds < max(8, (x1 - x0) * (y1 - y0) * .12):
            raise ValueError("Ditaa fill region cannot be matched safely to its native color seed; preserve output and inspect this box.")
        for y in range(y0, y1):
            for x in range(x0, x1):
                index = y * width + x
                if canvas[index]:
                    continue
                pixel = pixels[index]
                if pixel == native:
                    pixels[index] = fill
                    painted += 1
                    continue
                neighbors = [yy * width + xx for yy in range(max(0, y - contour_radius), min(height, y + contour_radius + 1)) for xx in range(max(0, x - contour_radius), min(width, x + contour_radius + 1))]
                if connectors[index] and exterior_distance[index] <= contour_radius:
                    # Preserve the relation where it crosses the exterior edge;
                    # its portion inside a glyph receives the readable foreground.
                    continue
                if not connectors[index] and exterior_distance[index] <= contour_radius and any(pixels[neighbor] == native or pixels[neighbor] == fill for neighbor in neighbors):
                    # Only an external contour adjacent to its own fill is decorative.
                    pixels[index] = fill
                    contours += 1
                    continue
                # Native text and internal symbol strokes may be black or white.
                # Preserve their coverage while choosing exact contrast on final fill.
                candidates = []
                for old_foreground in [(0, 0, 0), (255, 255, 255)]:
                    denominator = sum((a - b) ** 2 for a, b in zip(old_foreground, native))
                    if not denominator:
                        continue
                    coverage = max(0, min(1, sum((p - n) * (f - n) for p, n, f in zip(pixel, native, old_foreground)) / denominator))
                    error = sum((p - (n + coverage * (f - n))) ** 2 for p, n, f in zip(pixel, native, old_foreground))
                    candidates.append((error, coverage))
                if candidates:
                    error, coverage = min(candidates)
                    if error <= 16:
                        pixels[index] = tuple(round(a + coverage * (b - a)) for a, b in zip(fill, foreground))
    image.putdata(pixels)
    allowed = COLORSETS[plan["colorset"]]["allowed"]
    palette = Image.new("P", (1, 1))
    channels = [channel for color in allowed for channel in rgb(color)]
    palette.putpalette(channels + channels[:3] * (256 - len(allowed)))
    image.quantize(palette=palette, dither=Image.Dither.NONE).convert("RGB").save(path)
    return {"styledBoxes": len(plan["boxes"]), "paintedFillPixels": painted, "removedContourPixels": contours, "sourceBacked": True, "shadowsDisabled": True}
