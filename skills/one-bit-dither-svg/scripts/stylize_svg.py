#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "Pillow>=11.0.0",
#   "playwright>=1.52.0",
# ]
# ///

"""Rebuild a local SVG or raster image as a self-contained dithered pixel SVG."""

from __future__ import annotations

import argparse
import collections
from colorset_contract import colors as colorset_colors, nearest as nearest_token
import io
import json
import math
import re
import socket
import sys
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence
from xml.sax.saxutils import escape, quoteattr

from PIL import Image, ImageDraw, ImageOps, UnidentifiedImageError
from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import Route, sync_playwright


Color = tuple[int, int, int]
BLACK: Color = (0, 0, 0)
WHITE: Color = (255, 255, 255)
MODES = ("original", "custom", "regional")
QUALITY_PROFILES: dict[str, dict[str, int | float]] = {
    "manual": {
        "render_width": 768,
        "cell_size": 4,
        "matrix_size": 4,
        "contrast": 1.15,
        "region_colors": 8,
    },
    "compact": {
        "render_width": 768,
        "cell_size": 5,
        "matrix_size": 4,
        "contrast": 1.25,
        "region_colors": 6,
    },
    "balanced": {
        "render_width": 960,
        "cell_size": 3,
        "matrix_size": 4,
        "contrast": 1.15,
        "region_colors": 8,
    },
    "detailed": {
        "render_width": 1280,
        "cell_size": 2,
        "matrix_size": 4,
        "contrast": 1.05,
        "region_colors": 12,
    },
}
MAX_RENDER_DIMENSION = 4096
BAYER_MATRICES: dict[int, tuple[tuple[int, ...], ...]] = {
    2: ((0, 2), (3, 1)),
    4: (
        (0, 8, 2, 10),
        (12, 4, 14, 6),
        (3, 11, 1, 9),
        (15, 7, 13, 5),
    ),
    8: (
        (0, 32, 8, 40, 2, 34, 10, 42),
        (48, 16, 56, 24, 50, 18, 58, 26),
        (12, 44, 4, 36, 14, 46, 6, 38),
        (60, 28, 52, 20, 62, 30, 54, 22),
        (3, 35, 11, 43, 1, 33, 9, 41),
        (51, 19, 59, 27, 49, 17, 57, 25),
        (15, 47, 7, 39, 13, 45, 5, 37),
        (63, 31, 55, 23, 61, 29, 53, 21),
    ),
}


@dataclass(frozen=True)
class Paint:
    color: Color
    role: str
    region_index: int | None = None


@dataclass(frozen=True)
class RegionPair:
    color: Color
    companion: Color
    contrast_ratio: float


@dataclass(frozen=True)
class SourceInfo:
    kind: str
    format: str
    frame_index: int
    frame_count: int
    width: int
    height: int

    @property
    def aspect_ratio(self) -> float:
        return self.width / self.height


def install_windows_socketpair_workaround() -> None:
    """Avoid a rare CPython socketpair fallback deadlock before Playwright starts."""
    if sys.platform != "win32":
        return

    def loopback_socketpair(
        family: int = socket.AF_INET,
        socket_type: int = socket.SOCK_STREAM,
        protocol: int = 0,
    ) -> tuple[socket.socket, socket.socket]:
        if family not in {socket.AF_INET, socket.AF_INET6} or socket_type != socket.SOCK_STREAM or protocol != 0:
            raise ValueError("The Windows loopback socket pair supports only TCP over IPv4 or IPv6")
        host = "127.0.0.1" if family == socket.AF_INET else "::1"
        listener = socket.socket(family, socket_type, protocol)
        client = socket.socket(family, socket_type, protocol)
        server: socket.socket | None = None
        try:
            listener.bind((host, 0))
            listener.listen(1)
            client.settimeout(5)
            client.connect(listener.getsockname())
            client.settimeout(None)
            server, _ = listener.accept()
            return server, client
        except Exception:
            if server is not None:
                server.close()
            client.close()
            raise
        finally:
            listener.close()

    socket.socketpair = loopback_socketpair


def parse_hex_color(value: str) -> Color:
    token = value.strip().lower()
    if re.fullmatch(r"#[0-9a-f]{3}", token):
        token = "#" + "".join(character * 2 for character in token[1:])
    if not re.fullmatch(r"#[0-9a-f]{6}", token):
        raise argparse.ArgumentTypeError(f"color must be #RGB or #RRGGBB; received {value!r}")
    return tuple(int(token[index : index + 2], 16) for index in (1, 3, 5))  # type: ignore[return-value]


def resolve_quality_settings(
    profile: str,
    *,
    render_width: int | None = None,
    cell_size: int | None = None,
    matrix_size: int | None = None,
    contrast: float | None = None,
    region_colors: int | None = None,
) -> dict[str, int | float]:
    """Resolve a named quality baseline while preserving explicit overrides."""
    if profile not in QUALITY_PROFILES:
        raise ValueError(f"Unknown quality profile: {profile}")
    baseline = QUALITY_PROFILES[profile]
    return {
        "render_width": baseline["render_width"] if render_width is None else render_width,
        "cell_size": baseline["cell_size"] if cell_size is None else cell_size,
        "matrix_size": baseline["matrix_size"] if matrix_size is None else matrix_size,
        "contrast": baseline["contrast"] if contrast is None else contrast,
        "region_colors": baseline["region_colors"] if region_colors is None else region_colors,
    }


def color_hex(color: Sequence[int]) -> str:
    return "#" + "".join(f"{channel:02x}" for channel in color)


def clamp(value: float, minimum: float = 0.0, maximum: float = 1.0) -> float:
    return max(minimum, min(maximum, value))


def perceived_luminance(color: Sequence[int]) -> float:
    red, green, blue = (channel / 255 for channel in color)
    return 0.2126 * red + 0.7152 * green + 0.0722 * blue


def relative_luminance(color: Sequence[int]) -> float:
    def linearize(channel: int) -> float:
        value = channel / 255
        return value / 12.92 if value <= 0.04045 else ((value + 0.055) / 1.055) ** 2.4

    red, green, blue = (linearize(channel) for channel in color)
    return 0.2126 * red + 0.7152 * green + 0.0722 * blue


def contrast_ratio(first: Sequence[int], second: Sequence[int]) -> float:
    first_luminance = relative_luminance(first)
    second_luminance = relative_luminance(second)
    lighter = max(first_luminance, second_luminance)
    darker = min(first_luminance, second_luminance)
    return (lighter + 0.05) / (darker + 0.05)


def oklab_feature(color: Color) -> tuple[float, float, float]:
    """Return a chroma-emphasized OKLab feature for perceptual clustering."""
    linear = []
    for channel in color:
        value = channel / 255
        linear.append(value / 12.92 if value <= 0.04045 else ((value + 0.055) / 1.055) ** 2.4)
    red, green, blue = linear
    l_value = 0.4122214708 * red + 0.5363325363 * green + 0.0514459929 * blue
    m_value = 0.2119034982 * red + 0.6806995451 * green + 0.1073969566 * blue
    s_value = 0.0883024619 * red + 0.2817188376 * green + 0.6299787005 * blue
    l_root = math.copysign(abs(l_value) ** (1 / 3), l_value)
    m_root = math.copysign(abs(m_value) ** (1 / 3), m_value)
    s_root = math.copysign(abs(s_value) ** (1 / 3), s_value)
    lightness = 0.2104542553 * l_root + 0.7936177850 * m_root - 0.0040720468 * s_root
    a_value = 1.9779984951 * l_root - 2.4285922050 * m_root + 0.4505937099 * s_root
    b_value = 0.0259040371 * l_root + 0.7827717662 * m_root - 0.8086757660 * s_root
    return lightness, a_value * 1.5, b_value * 1.5


def feature_distance_squared(first: Sequence[float], second: Sequence[float]) -> float:
    return sum((left - right) ** 2 for left, right in zip(first, second, strict=True))


def select_region_palette(histogram: dict[Color, int], requested_colors: int) -> list[Color]:
    """Choose deterministic source-color medoids without erasing small chromatic zones."""
    colors = sorted(histogram)
    if len(colors) <= requested_colors:
        return colors
    features = {color: oklab_feature(color) for color in colors}

    def chroma(color: Color) -> float:
        _, a_value, b_value = features[color]
        return math.hypot(a_value, b_value)

    first = max(
        colors,
        key=lambda color: (
            math.sqrt(histogram[color]) * (1 + 1.5 * min(chroma(color), 0.5)),
            color,
        ),
    )
    centers = [first]
    while len(centers) < requested_colors:
        candidate = max(
            (color for color in colors if color not in centers),
            key=lambda color: (
                min(feature_distance_squared(features[color], features[center]) for center in centers)
                * (histogram[color] ** 0.25)
                * (1 + 4 * min(chroma(color), 0.5)),
                color,
            ),
        )
        centers.append(candidate)

    for _ in range(8):
        clusters: list[list[Color]] = [[] for _ in centers]
        for color in colors:
            nearest = min(
                range(len(centers)),
                key=lambda index: (feature_distance_squared(features[color], features[centers[index]]), index),
            )
            clusters[nearest].append(color)
        updated: list[Color] = []
        for index, cluster in enumerate(clusters):
            if not cluster:
                updated.append(centers[index])
                continue
            weighted_features = [0.0, 0.0, 0.0]
            weight_total = 0.0
            for color in cluster:
                weight = math.sqrt(histogram[color]) * (1 + 1.5 * min(chroma(color), 0.5))
                weight_total += weight
                for component in range(3):
                    weighted_features[component] += features[color][component] * weight
            target = tuple(component / weight_total for component in weighted_features)
            medoid = min(
                cluster,
                key=lambda color: (
                    feature_distance_squared(features[color], target),
                    -histogram[color],
                    color,
                ),
            )
            updated.append(medoid)
        if updated == centers:
            break
        centers = updated
    return centers


def choose_companion(color: Color) -> RegionPair:
    black_ratio = contrast_ratio(color, BLACK)
    white_ratio = contrast_ratio(color, WHITE)
    if white_ratio > black_ratio:
        return RegionPair(color=color, companion=WHITE, contrast_ratio=white_ratio)
    return RegionPair(color=color, companion=BLACK, contrast_ratio=black_ratio)


def parse_numeric_dimension(value: str | None) -> float | None:
    if not value:
        return None
    match = re.fullmatch(r"\s*([0-9]+(?:\.[0-9]+)?)\s*(?:px|pt|pc|mm|cm|in)?\s*", value, re.IGNORECASE)
    if not match:
        return None
    number = float(match.group(1))
    return number if number > 0 else None


def inspect_svg_source(path: Path, root: ET.Element | None = None) -> SourceInfo:
    try:
        if root is None:
            root = ET.parse(path).getroot()
    except (ET.ParseError, OSError) as error:
        raise SystemExit(f"Cannot parse input SVG: {error}") from error
    if root.tag.rsplit("}", 1)[-1] != "svg":
        raise SystemExit("Input XML root must be <svg>")

    view_box = root.get("viewBox")
    if view_box:
        parts = [part for part in re.split(r"[\s,]+", view_box.strip()) if part]
        if len(parts) == 4:
            try:
                width = float(parts[2])
                height = float(parts[3])
                if width > 0 and height > 0:
                    return SourceInfo("svg", "SVG", 0, 1, max(1, round(width)), max(1, round(height)))
            except ValueError:
                pass

    width = parse_numeric_dimension(root.get("width"))
    height = parse_numeric_dimension(root.get("height"))
    if width and height:
        return SourceInfo("svg", "SVG", 0, 1, max(1, round(width)), max(1, round(height)))
    raise SystemExit("Input SVG needs a positive viewBox or numeric width and height")


def inspect_raster_source(path: Path, frame_index: int) -> SourceInfo:
    try:
        with Image.open(path) as image:
            frame_count = max(1, int(getattr(image, "n_frames", 1)))
            if not 0 <= frame_index < frame_count:
                raise SystemExit(
                    f"--frame must be between 0 and {frame_count - 1} for {path.name}; received {frame_index}"
                )
            image.seek(frame_index)
            oriented = ImageOps.exif_transpose(image)
            width, height = oriented.size
            if width <= 0 or height <= 0:
                raise SystemExit("Input raster image has invalid dimensions")
            format_name = (image.format or path.suffix.lstrip(".") or "RASTER").upper()
            return SourceInfo("raster", format_name, frame_index, frame_count, width, height)
    except (UnidentifiedImageError, OSError) as error:
        raise SystemExit(
            f"Unsupported or unreadable image: {path}. Supply an SVG or a raster format decoded by Pillow. "
            f"Pillow reported: {error}"
        ) from error


def inspect_source(path: Path, frame_index: int = 0) -> SourceInfo:
    if frame_index < 0:
        raise SystemExit("--frame must be nonnegative")
    try:
        root = ET.parse(path).getroot()
    except (ET.ParseError, UnicodeError):
        root = None
    except OSError as error:
        raise SystemExit(f"Cannot read input image: {error}") from error
    if root is not None and root.tag.rsplit("}", 1)[-1] == "svg":
        if frame_index != 0:
            raise SystemExit("SVG inputs have one settled frame; --frame must be 0")
        return inspect_svg_source(path, root)
    return inspect_raster_source(path, frame_index)


def source_aspect_ratio(path: Path, frame_index: int = 0) -> float:
    return inspect_source(path, frame_index).aspect_ratio


def resolve_render_size(
    path: Path,
    render_width: int,
    render_height: int | None,
    frame_index: int = 0,
    source_info: SourceInfo | None = None,
) -> tuple[int, int]:
    if not 32 <= render_width <= MAX_RENDER_DIMENSION:
        raise SystemExit(f"--render-width must be between 32 and {MAX_RENDER_DIMENSION}")
    if render_height is None:
        aspect_ratio = (source_info or inspect_source(path, frame_index)).aspect_ratio
        render_height = max(32, round(render_width / aspect_ratio))
    if not 32 <= render_height <= MAX_RENDER_DIMENSION:
        raise SystemExit(f"--render-height must be between 32 and {MAX_RENDER_DIMENSION}")
    return render_width, render_height


def render_svg(path: Path, width: int, height: int, timeout_ms: int) -> Image.Image:
    blocked_urls: list[str] = []
    console_errors: list[str] = []
    page_errors: list[str] = []
    install_windows_socketpair_workaround()

    def route_request(route: Route) -> None:
        url = route.request.url
        if url.startswith(("file:", "data:", "blob:", "about:")):
            route.continue_()
            return
        blocked_urls.append(url)
        route.abort()

    try:
        with sync_playwright() as playwright:
            browser = None
            launch_errors: list[str] = []
            for label, options in (
                ("bundled Chromium", {}),
                ("Microsoft Edge", {"channel": "msedge"}),
                ("Google Chrome", {"channel": "chrome"}),
            ):
                try:
                    browser = playwright.chromium.launch(**options)
                    break
                except PlaywrightError as launch_error:
                    launch_errors.append(f"{label}: {launch_error}")
            if browser is None:
                raise SystemExit(
                    "No compatible Chromium browser could be launched. Install one with "
                    "`uv run --with playwright playwright install chromium`, then retry.\n"
                    + "\n".join(launch_errors)
                )
            context = browser.new_context(
                viewport={"width": min(width + 32, MAX_RENDER_DIMENSION), "height": min(height + 32, MAX_RENDER_DIMENSION)},
                device_scale_factor=1,
                java_script_enabled=False,
            )
            context.route("**/*", route_request)
            page = context.new_page()
            page.on("console", lambda message: console_errors.append(message.text) if message.type == "error" else None)
            page.on("pageerror", lambda error: page_errors.append(str(error)))
            page.goto(path.resolve().as_uri(), wait_until="load", timeout=timeout_ms)
            locator = page.locator("svg").first
            locator.wait_for(state="visible", timeout=timeout_ms)
            locator.evaluate(
                """(element, size) => {
                    element.setAttribute('width', String(size.width));
                    element.setAttribute('height', String(size.height));
                    element.style.width = `${size.width}px`;
                    element.style.height = `${size.height}px`;
                    element.style.maxWidth = 'none';
                    element.style.maxHeight = 'none';
                }""",
                {"width": width, "height": height},
            )
            screenshot = locator.screenshot(animations="disabled", caret="hide", omit_background=True)
            context.close()
            browser.close()
    except PlaywrightError as error:
        raise SystemExit(
            "Chromium failed while rendering the SVG. Install it with "
            "`uv run --with playwright playwright install chromium`, then retry. "
            f"Playwright reported: {error}"
        ) from error

    if blocked_urls:
        unique_urls = sorted(set(blocked_urls))
        rendered = "\n".join(f"- {url}" for url in unique_urls[:10])
        suffix = "\n- ..." if len(unique_urls) > 10 else ""
        raise SystemExit(f"Input SVG requested blocked external resources:\n{rendered}{suffix}\nEmbed them and retry.")
    if page_errors:
        raise SystemExit("Browser page errors occurred while rendering:\n" + "\n".join(f"- {item}" for item in page_errors))
    if console_errors:
        raise SystemExit("Browser console errors occurred while rendering:\n" + "\n".join(f"- {item}" for item in console_errors))

    image = Image.open(io.BytesIO(screenshot)).convert("RGBA")
    if image.size != (width, height):
        raise SystemExit(f"Rendered SVG size {image.width}x{image.height} did not match requested {width}x{height}")
    return image


def render_raster(path: Path, width: int, height: int, frame_index: int = 0) -> Image.Image:
    try:
        with Image.open(path) as image:
            frame_count = max(1, int(getattr(image, "n_frames", 1)))
            if not 0 <= frame_index < frame_count:
                raise SystemExit(
                    f"--frame must be between 0 and {frame_count - 1} for {path.name}; received {frame_index}"
                )
            image.seek(frame_index)
            oriented = ImageOps.exif_transpose(image).convert("RGBA")
            if oriented.size == (width, height):
                return oriented.copy()
            return oriented.resize((width, height), Image.Resampling.LANCZOS, reducing_gap=3.0)
    except (UnidentifiedImageError, OSError) as error:
        raise SystemExit(f"Pillow could not decode raster input {path}: {error}") from error


def render_source(
    path: Path,
    width: int,
    height: int,
    timeout_ms: int,
    source_info: SourceInfo,
) -> Image.Image:
    if source_info.kind == "svg":
        return render_svg(path, width, height, timeout_ms)
    return render_raster(path, width, height, source_info.frame_index)


def raster_grid(image: Image.Image, cell_size: int) -> tuple[list[list[Color]], list[list[int]]]:
    image = image.convert("RGBA")
    grid_width = math.ceil(image.width / cell_size)
    grid_height = math.ceil(image.height / cell_size)
    sampled = image.resize((grid_width, grid_height), Image.Resampling.BOX)
    getter = getattr(sampled, "get_flattened_data", sampled.getdata)
    values = list(getter())
    pixels: list[list[Color]] = []
    alphas: list[list[int]] = []
    for y in range(grid_height):
        row = values[y * grid_width : (y + 1) * grid_width]
        pixels.append([(red, green, blue) for red, green, blue, _ in row])
        alphas.append([alpha for _, _, _, alpha in row])
    return pixels, alphas


def quantize_regions(
    pixels: Sequence[Sequence[Color]],
    alphas: Sequence[Sequence[int]],
    alpha_threshold: int,
    requested_colors: int,
) -> tuple[list[list[int]], list[Color]]:
    visible_positions: list[tuple[int, int]] = []
    visible_colors: list[Color] = []
    for y, row in enumerate(pixels):
        for x, color in enumerate(row):
            if alphas[y][x] >= alpha_threshold:
                visible_positions.append((x, y))
                visible_colors.append(color)
    if not visible_colors:
        raise SystemExit("The rendered image contains no cells above --alpha-threshold")

    histogram = dict(collections.Counter(visible_colors))
    region_colors = select_region_palette(histogram, min(requested_colors, len(histogram)))
    region_features = [oklab_feature(color) for color in region_colors]
    color_assignments = {
        color: min(
            range(len(region_colors)),
            key=lambda index: (feature_distance_squared(oklab_feature(color), region_features[index]), index),
        )
        for color in histogram
    }
    assignments = [[-1 for _ in row] for row in pixels]
    for (x, y), color in zip(visible_positions, visible_colors, strict=True):
        assignments[y][x] = color_assignments[color]
    return assignments, region_colors


def ordered_threshold(x: int, y: int, matrix_size: int) -> float:
    matrix = BAYER_MATRICES[matrix_size]
    return (matrix[y % matrix_size][x % matrix_size] + 0.5) / (matrix_size * matrix_size)


def toned_luminance(color: Color, contrast: float) -> float:
    luminance = perceived_luminance(color)
    return clamp((luminance - 0.5) * contrast + 0.5)


def build_paint_grid(
    pixels: Sequence[Sequence[Color]],
    alphas: Sequence[Sequence[int]],
    *,
    mode: str,
    matrix_size: int,
    contrast: float,
    alpha_threshold: int,
    custom_color: Color | None = None,
    region_assignments: Sequence[Sequence[int]] | None = None,
    region_colors: Sequence[Color] | None = None,
    colorset: str = "colorset1",
) -> tuple[list[list[int]], list[Paint], list[RegionPair]]:
    if mode not in MODES:
        raise ValueError(f"Unsupported mode: {mode}")

    grid = [[-1 for _ in row] for row in pixels]
    if mode in {"original", "custom"}:
        dark = BLACK if mode == "original" else custom_color
        if dark is None:
            raise ValueError("custom mode requires custom_color")
        if dark not in colorset_colors(colorset):
            raise ValueError("Custom ink must belong to the active colorset")
        paints = [Paint(dark, "ink"), Paint(WHITE, "paper")]
        for y, row in enumerate(pixels):
            for x, color in enumerate(row):
                if alphas[y][x] < alpha_threshold:
                    continue
                is_light = toned_luminance(color, contrast) >= ordered_threshold(x, y, matrix_size)
                grid[y][x] = 1 if is_light else 0
        return grid, paints, []

    if region_assignments is None or region_colors is None:
        raise ValueError("regional mode requires region assignments and colors")
    region_pairs = [choose_companion(nearest_token(color, colorset)) for color in region_colors]
    paints: list[Paint] = []
    for region_index, pair in enumerate(region_pairs):
        paints.append(Paint(pair.color, "source-color", region_index))
        paints.append(Paint(pair.companion, "companion", region_index))

    for y, row in enumerate(pixels):
        for x, color in enumerate(row):
            if alphas[y][x] < alpha_threshold:
                continue
            region_index = region_assignments[y][x]
            if not 0 <= region_index < len(region_pairs):
                raise ValueError(f"Missing regional assignment at cell ({x}, {y})")
            pair = region_pairs[region_index]
            is_light = toned_luminance(color, contrast) >= ordered_threshold(x, y, matrix_size)
            if pair.companion == WHITE:
                use_companion = is_light
            else:
                use_companion = not is_light
            grid[y][x] = region_index * 2 + (1 if use_companion else 0)
    return grid, paints, region_pairs


def iter_runs(grid: Sequence[Sequence[int]]) -> list[tuple[int, int, int, int]]:
    runs: list[tuple[int, int, int, int]] = []
    for y, row in enumerate(grid):
        x = 0
        while x < len(row):
            paint_index = row[x]
            if paint_index < 0:
                x += 1
                continue
            end = x + 1
            while end < len(row) and row[end] == paint_index:
                end += 1
            runs.append((x, y, end - x, paint_index))
            x = end
    return runs


def unique_palette(paints: Sequence[Paint]) -> list[Color]:
    colors: list[Color] = []
    for paint in paints:
        if paint.color not in colors:
            colors.append(paint.color)
    return colors


def build_svg(
    *,
    width: int,
    height: int,
    cell_size: int,
    grid: Sequence[Sequence[int]],
    paints: Sequence[Paint],
    mode: str,
    matrix_size: int,
    contrast: float,
    alpha_threshold: int,
    source_name: str,
    title: str,
    custom_color: Color | None,
    region_pairs: Sequence[RegionPair],
    quality_profile: str = "manual",
    source_info: SourceInfo | None = None,
) -> tuple[str, dict[str, object]]:
    source_info = source_info or SourceInfo("svg", "SVG", 0, 1, width, height)
    runs = iter_runs(grid)
    if not runs:
        raise SystemExit("Dithering produced no visible marks; lower --alpha-threshold or inspect the source image")
    palette = unique_palette(paints)
    grid_height = len(grid)
    grid_width = len(grid[0]) if grid_height else 0
    regions = [
        {
            "index": index,
            "color": color_hex(pair.color),
            "companion": color_hex(pair.companion),
            "contrastRatio": round(pair.contrast_ratio, 4),
        }
        for index, pair in enumerate(region_pairs)
    ]
    metadata: dict[str, object] = {
        "schema": "one-bit-dither-svg/v1",
        "mode": mode,
        "colorset": "colorset1" if set(palette) <= set(colorset_colors("colorset1")) else "colorset2",
        "qualityProfile": quality_profile,
        "source": source_name,
        "sourceKind": source_info.kind,
        "sourceFormat": source_info.format,
        "sourceFrame": source_info.frame_index,
        "sourceFrameCount": source_info.frame_count,
        "sourceSize": {"width": source_info.width, "height": source_info.height},
        "render": {
            "width": width,
            "height": height,
            "gridWidth": grid_width,
            "gridHeight": grid_height,
        },
        "dither": {
            "family": "ordered-bayer",
            "matrixSize": matrix_size,
            "cellSize": cell_size,
            "contrast": contrast,
            "alphaThreshold": alpha_threshold,
        },
        "palette": [color_hex(color) for color in palette],
        "customColor": color_hex(custom_color) if custom_color else None,
        "regionalQuantizer": "weighted-oklab-medoids" if mode == "regional" else None,
        "regions": regions,
        "runCount": len(runs),
    }
    attributes = {
        "data-colorset": str(metadata["colorset"]),
        "data-one-bit-dither-version": "1",
        "data-mode": mode,
        "data-quality-profile": quality_profile,
        "data-source-kind": source_info.kind,
        "data-source-format": source_info.format,
        "data-source-frame": str(source_info.frame_index),
        "data-source-frame-count": str(source_info.frame_count),
        "data-dither-family": "ordered-bayer",
        "data-matrix-size": str(matrix_size),
        "data-cell-size": str(cell_size),
        "data-contrast": f"{contrast:g}",
        "data-alpha-threshold": str(alpha_threshold),
        "data-render-width": str(width),
        "data-render-height": str(height),
        "data-grid-width": str(grid_width),
        "data-grid-height": str(grid_height),
        "data-run-count": str(len(runs)),
        "data-region-count": str(len(region_pairs)),
        "data-palette": ",".join(color_hex(color) for color in palette),
        "data-source": source_name,
    }
    if custom_color is not None:
        attributes["data-custom-color"] = color_hex(custom_color)
    attribute_markup = " ".join(f"{key}={quoteattr(value)}" for key, value in attributes.items())
    if mode == "regional":
        mode_description = f"{len(region_pairs)} source-color regions, each paired with black or white"
    elif mode == "custom":
        mode_description = f"custom ink {color_hex(custom_color or BLACK)} and white"
    else:
        mode_description = "black and white"
    description = (
        f"A {width} by {height} rendered source image rebuilt as {len(runs)} crisp rectangle runs using "
        f"a {matrix_size} by {matrix_size} ordered Bayer dither in {mode} mode: {mode_description}."
    )
    metadata_json = json.dumps(metadata, ensure_ascii=True, separators=(",", ":"))
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}" role="img" {attribute_markup}>',
        f"  <title>{escape(title)}</title>",
        f"  <desc>{escape(description)}</desc>",
        f'  <metadata id="one-bit-dither-metadata" type="application/json">{escape(metadata_json)}</metadata>',
        "  <style>.dither-raster{shape-rendering:crispEdges}.dither-run{stroke:none}</style>",
        '  <g class="dither-raster">',
    ]
    for x, y, length, paint_index in runs:
        paint = paints[paint_index]
        pixel_x = x * cell_size
        pixel_y = y * cell_size
        run_width = min(length * cell_size, width - pixel_x)
        run_height = min(cell_size, height - pixel_y)
        region_attribute = "" if paint.region_index is None else f' data-region-index="{paint.region_index}"'
        lines.append(
            f'    <rect class="dither-run" data-paint-index="{paint_index}" data-role="{paint.role}"'
            f'{region_attribute} x="{pixel_x}" y="{pixel_y}" width="{run_width}" height="{run_height}" '
            f'fill="{color_hex(paint.color)}" />'
        )
    lines.extend(["  </g>", "</svg>", ""])
    return "\n".join(lines), metadata


def build_preview(
    *,
    width: int,
    height: int,
    cell_size: int,
    grid: Sequence[Sequence[int]],
    paints: Sequence[Paint],
) -> Image.Image:
    preview = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(preview)
    for x, y, length, paint_index in iter_runs(grid):
        left = x * cell_size
        top = y * cell_size
        right = min(width, (x + length) * cell_size) - 1
        bottom = min(height, (y + 1) * cell_size) - 1
        draw.rectangle((left, top, right, bottom), fill=(*paints[paint_index].color, 255))
    return preview


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="Local SVG or Pillow-decodable raster image to transform")
    parser.add_argument("-o", "--output", type=Path, required=True, help="Exact output path for the stylized SVG")
    parser.add_argument("--mode", choices=MODES, required=True)
    parser.add_argument("--colorset", choices=("colorset1", "colorset2"), default="colorset1")
    parser.add_argument(
        "--quality-profile",
        choices=tuple(QUALITY_PROFILES),
        default="manual",
        help="Named density baseline; explicit tuning flags override individual profile values",
    )
    parser.add_argument("--color", type=parse_hex_color, help="Custom mode ink color as #RGB or #RRGGBB")
    parser.add_argument("--region-colors", type=int, help="Requested representative colors in regional mode")
    parser.add_argument("--render-width", type=int, help="Browser render width before cell sampling")
    parser.add_argument("--render-height", type=int, help="Optional browser render height; defaults to the source aspect ratio")
    parser.add_argument("--cell-size", type=int, help="Rendered pixels represented by each dither cell")
    parser.add_argument("--matrix-size", type=int, choices=tuple(BAYER_MATRICES))
    parser.add_argument("--contrast", type=float, help="Luminance contrast around the midpoint")
    parser.add_argument("--alpha-threshold", type=int, default=24, help="Omit sampled cells below this 0-255 alpha")
    parser.add_argument("--frame", type=int, default=0, help="Zero-based frame for GIF, animated WebP, or TIFF input")
    parser.add_argument("--timeout-ms", type=int, default=30000, help="Browser timeout for SVG input")
    parser.add_argument("--title", help="Accessible SVG title; defaults to the source filename and mode")
    parser.add_argument("--preview-png", type=Path, help="Optional pixel-faithful PNG preview")
    parser.add_argument("--json-report", type=Path, help="Optional machine-readable conversion report")
    args = parser.parse_args(argv)
    if args.color is not None and args.color not in colorset_colors(args.colorset):
        parser.error("Custom ink must belong to --colorset; select colorset2 for extended tokens")

    quality = resolve_quality_settings(
        args.quality_profile,
        render_width=args.render_width,
        cell_size=args.cell_size,
        matrix_size=args.matrix_size,
        contrast=args.contrast,
        region_colors=args.region_colors,
    )
    args.render_width = int(quality["render_width"])
    args.cell_size = int(quality["cell_size"])
    args.matrix_size = int(quality["matrix_size"])
    args.contrast = float(quality["contrast"])
    args.region_colors = int(quality["region_colors"])

    if not args.input.is_file():
        parser.error(f"input image not found: {args.input}")
    if args.output.suffix.lower() != ".svg":
        parser.error("--output must end in .svg")
    if args.output.resolve() == args.input.resolve():
        parser.error("--output must not overwrite the input SVG")
    if args.preview_png and args.preview_png.suffix.lower() != ".png":
        parser.error("--preview-png must end in .png")
    if args.json_report and args.json_report.suffix.lower() != ".json":
        parser.error("--json-report must end in .json")
    if args.mode == "custom" and args.color is None:
        parser.error("custom mode requires --color")
    if args.mode != "custom" and args.color is not None:
        parser.error("--color is valid only in custom mode")
    if args.color == WHITE:
        parser.error("custom mode color cannot be white because both output tones would be identical")
    if not 2 <= args.region_colors <= 32:
        parser.error("--region-colors must be between 2 and 32")
    if not 1 <= args.cell_size <= 64:
        parser.error("--cell-size must be between 1 and 64")
    if not 0.25 <= args.contrast <= 4:
        parser.error("--contrast must be between 0.25 and 4")
    if not 0 <= args.alpha_threshold <= 255:
        parser.error("--alpha-threshold must be between 0 and 255")
    if args.frame < 0:
        parser.error("--frame must be nonnegative")
    if args.timeout_ms <= 0:
        parser.error("--timeout-ms must be positive")
    return args


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    source_info = inspect_source(args.input, args.frame)
    width, height = resolve_render_size(
        args.input,
        args.render_width,
        args.render_height,
        args.frame,
        source_info,
    )
    rendered = render_source(args.input, width, height, args.timeout_ms, source_info)
    pixels, alphas = raster_grid(rendered, args.cell_size)

    region_assignments: list[list[int]] | None = None
    region_colors: list[Color] | None = None
    if args.mode == "regional":
        region_assignments, region_colors = quantize_regions(
            pixels,
            alphas,
            args.alpha_threshold,
            args.region_colors,
        )
    grid, paints, region_pairs = build_paint_grid(
        pixels,
        alphas,
        mode=args.mode,
        matrix_size=args.matrix_size,
        contrast=args.contrast,
        alpha_threshold=args.alpha_threshold,
        custom_color=args.color,
        region_assignments=region_assignments,
        region_colors=region_colors,
        colorset=args.colorset,
    )
    title = args.title or f"{args.input.stem} — {args.mode} one-bit dither"
    markup, metadata = build_svg(
        width=width,
        height=height,
        cell_size=args.cell_size,
        grid=grid,
        paints=paints,
        mode=args.mode,
        matrix_size=args.matrix_size,
        contrast=args.contrast,
        alpha_threshold=args.alpha_threshold,
        source_name=args.input.name,
        title=title,
        custom_color=args.color,
        region_pairs=region_pairs,
        quality_profile=args.quality_profile,
        source_info=source_info,
    )
    output_path = args.output.resolve()
    write_text(output_path, markup)

    preview_path: Path | None = None
    if args.preview_png:
        preview_path = args.preview_png.resolve()
        preview_path.parent.mkdir(parents=True, exist_ok=True)
        build_preview(
            width=width,
            height=height,
            cell_size=args.cell_size,
            grid=grid,
            paints=paints,
        ).save(preview_path)

    report: dict[str, object] = {
        "ok": True,
        "output": str(output_path),
        "preview": str(preview_path) if preview_path else None,
        **metadata,
    }
    if args.json_report:
        report_path = args.json_report.resolve()
        write_text(report_path, json.dumps(report, indent=2, ensure_ascii=False) + "\n")
        report["report"] = str(report_path)
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
