#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "Pillow>=11.0.0",
#   "playwright>=1.52.0",
# ]
# ///

"""Rasterize any visible D3/page element and rebuild it as portable dithered SVG."""

from __future__ import annotations

import argparse
import io
import json
import math
import re
import socket
import sys
from pathlib import Path
from typing import Iterable, Sequence
from urllib.parse import urlparse
from xml.sax.saxutils import escape, quoteattr

from PIL import Image
from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import sync_playwright


DEFAULT_PALETTE = "#000000,#333e48,#9e1b32,#ffffff"
BAYER_MATRICES = {
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


def install_windows_socketpair_workaround() -> None:
    """Avoid a rare CPython fallback deadlock before Playwright starts on Windows."""
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


def parse_viewport(value: str) -> tuple[int, int]:
    match = re.fullmatch(r"(\d+)x(\d+)", value.strip().lower())
    if not match:
        raise argparse.ArgumentTypeError("viewport must use WIDTHxHEIGHT, for example 1280x720")
    width, height = (int(part) for part in match.groups())
    if width < 100 or height < 100:
        raise argparse.ArgumentTypeError("viewport dimensions must be at least 100 pixels")
    return width, height


def parse_hex_color(value: str) -> tuple[int, int, int]:
    token = value.strip().lower()
    if re.fullmatch(r"#[0-9a-f]{3}", token):
        token = "#" + "".join(character * 2 for character in token[1:])
    if not re.fullmatch(r"#[0-9a-f]{6}", token):
        raise argparse.ArgumentTypeError(f"palette colors must be #RGB or #RRGGBB; received {value!r}")
    return tuple(int(token[index : index + 2], 16) for index in (1, 3, 5))


def parse_palette(value: str) -> tuple[tuple[int, int, int], ...]:
    colors = tuple(parse_hex_color(item) for item in value.split(",") if item.strip())
    if not 2 <= len(colors) <= 16:
        raise argparse.ArgumentTypeError("palette must contain between 2 and 16 comma-separated colors")
    if len(set(colors)) != len(colors):
        raise argparse.ArgumentTypeError("palette colors must be unique")
    return colors


def color_hex(color: Sequence[int]) -> str:
    return "#" + "".join(f"{channel:02x}" for channel in color)


def source_to_url(source: str) -> str:
    if re.match(r"^https?://", source) or source.startswith("file://"):
        return source
    path = Path(source).expanduser().resolve()
    if not path.exists():
        raise SystemExit(f"Input not found: {path}")
    return path.as_uri()


def source_label(source: str) -> str:
    if re.match(r"^https?://", source):
        parsed = urlparse(source)
        return f"{parsed.netloc}{parsed.path}" or parsed.netloc
    if source.startswith("file://"):
        return Path(urlparse(source).path).name or "local-file"
    return Path(source).name or "local-input"


def nearest_palette_index(rgb: Sequence[float], palette: Sequence[Sequence[int]]) -> int:
    red, green, blue = rgb
    return min(
        range(len(palette)),
        key=lambda index: (
            0.299 * (red - palette[index][0]) ** 2
            + 0.587 * (green - palette[index][1]) ** 2
            + 0.114 * (blue - palette[index][2]) ** 2
        ),
    )


def ordered_dither(
    pixels: Sequence[Sequence[Sequence[float]]],
    palette: Sequence[Sequence[int]],
    matrix_size: int,
    strength: float,
) -> list[list[int]]:
    matrix = BAYER_MATRICES[matrix_size]
    divisor = matrix_size * matrix_size
    output: list[list[int]] = []
    for y, row in enumerate(pixels):
        output_row = []
        for x, rgb in enumerate(row):
            threshold = ((matrix[y % matrix_size][x % matrix_size] + 0.5) / divisor) - 0.5
            delta = threshold * 255 * strength
            adjusted = tuple(max(0, min(255, channel + delta)) for channel in rgb)
            output_row.append(nearest_palette_index(adjusted, palette))
        output.append(output_row)
    return output


def diffusion_dither(
    pixels: Sequence[Sequence[Sequence[float]]],
    palette: Sequence[Sequence[int]],
    algorithm: str,
) -> list[list[int]]:
    work = [[list(pixel) for pixel in row] for row in pixels]
    height = len(work)
    width = len(work[0]) if height else 0
    output = [[0] * width for _ in range(height)]
    if algorithm == "floyd-steinberg":
        neighbors = ((1, 0, 7 / 16), (-1, 1, 3 / 16), (0, 1, 5 / 16), (1, 1, 1 / 16))
    else:
        neighbors = ((1, 0, 1 / 8), (2, 0, 1 / 8), (-1, 1, 1 / 8), (0, 1, 1 / 8), (1, 1, 1 / 8), (0, 2, 1 / 8))

    for y in range(height):
        for x in range(width):
            current = tuple(max(0, min(255, channel)) for channel in work[y][x])
            palette_index = nearest_palette_index(current, palette)
            output[y][x] = palette_index
            target = palette[palette_index]
            error = tuple(current[channel] - target[channel] for channel in range(3))
            for dx, dy, weight in neighbors:
                nx, ny = x + dx, y + dy
                if 0 <= nx < width and 0 <= ny < height:
                    for channel in range(3):
                        work[ny][nx][channel] += error[channel] * weight
    return output


def quantize_grid(
    pixels: Sequence[Sequence[Sequence[float]]],
    palette: Sequence[Sequence[int]],
    algorithm: str,
    matrix_size: int,
    ordered_strength: float,
) -> list[list[int]]:
    if algorithm == "ordered":
        return ordered_dither(pixels, palette, matrix_size, ordered_strength)
    if algorithm in {"floyd-steinberg", "atkinson"}:
        return diffusion_dither(pixels, palette, algorithm)
    return [[nearest_palette_index(pixel, palette) for pixel in row] for row in pixels]


def raster_grid(image: Image.Image, cell_size: int) -> tuple[list[list[tuple[int, int, int]]], list[list[int]]]:
    image = image.convert("RGBA")
    grid_width = math.ceil(image.width / cell_size)
    grid_height = math.ceil(image.height / cell_size)
    sampled = image.resize((grid_width, grid_height), Image.Resampling.BOX)
    getter = getattr(sampled, "get_flattened_data", sampled.getdata)
    values = list(getter())
    pixels: list[list[tuple[int, int, int]]] = []
    alphas: list[list[int]] = []
    for y in range(grid_height):
        row = values[y * grid_width : (y + 1) * grid_width]
        pixels.append([(red, green, blue) for red, green, blue, _ in row])
        alphas.append([alpha for _, _, _, alpha in row])
    return pixels, alphas


def iter_runs(indices: Sequence[Sequence[int]], alphas: Sequence[Sequence[int]], alpha_threshold: int) -> Iterable[tuple[int, int, int, int]]:
    for y, row in enumerate(indices):
        x = 0
        while x < len(row):
            if alphas[y][x] < alpha_threshold:
                x += 1
                continue
            palette_index = row[x]
            end = x + 1
            while end < len(row) and row[end] == palette_index and alphas[y][end] >= alpha_threshold:
                end += 1
            yield x, y, end - x, palette_index
            x = end


def build_svg(
    *,
    width: int,
    height: int,
    cell_size: int,
    indices: Sequence[Sequence[int]],
    alphas: Sequence[Sequence[int]],
    palette: Sequence[Sequence[int]],
    alpha_threshold: int,
    algorithm: str,
    matrix_size: int,
    source: str,
    selector: str,
    title: str,
    animate: bool,
    duration: float,
) -> tuple[str, int]:
    palette_tokens = tuple(color_hex(color) for color in palette)
    runs = list(iter_runs(indices, alphas, alpha_threshold))
    if not runs:
        raise SystemExit("Dithering produced no visible pixels; lower --alpha-threshold or choose another selector")

    metadata = {
        "data-dither-algorithm": algorithm,
        "data-dither-matrix-size": str(matrix_size if algorithm == "ordered" else 0),
        "data-dither-cell-size": str(cell_size),
        "data-dither-palette": ",".join(palette_tokens),
        "data-source": source,
        "data-source-selector": selector,
        "data-grid-width": str(len(indices[0]) if indices else 0),
        "data-grid-height": str(len(indices)),
        "data-run-count": str(len(runs)),
    }
    attributes = " ".join(f"{key}={quoteattr(value)}" for key, value in metadata.items())
    description = (
        f"A {width} by {height} pixel source rebuilt as {len(runs)} run-length-compressed "
        f"dither marks using {algorithm} and the palette {', '.join(palette_tokens)}."
    )
    clip_reference = ' clip-path="url(#dither-reveal)"' if animate else ""
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}" role="img" {attributes}>',
        f"  <title>{escape(title)}</title>",
        f"  <desc>{escape(description)}</desc>",
        "  <style>.dither-raster{shape-rendering:crispEdges}.dither-run{vector-effect:non-scaling-stroke}</style>",
    ]
    if animate:
        lines.extend(
            [
                "  <defs>",
                '    <clipPath id="dither-reveal">',
                f'      <rect width="{width}" height="{height}">',
                f'        <animate attributeName="width" from="0" to="{width}" dur="{duration:g}s" begin="0s" fill="freeze" />',
                "      </rect>",
                "    </clipPath>",
                "  </defs>",
            ]
        )
    lines.append(f'  <g class="dither-raster"{clip_reference}>')
    for x, y, length, palette_index in runs:
        pixel_x = x * cell_size
        pixel_y = y * cell_size
        run_width = min(length * cell_size, width - pixel_x)
        run_height = min(cell_size, height - pixel_y)
        lines.append(
            f'    <rect class="dither-run" data-palette-index="{palette_index}" '
            f'x="{pixel_x}" y="{pixel_y}" width="{run_width}" height="{run_height}" fill="{palette_tokens[palette_index]}" />'
        )
    lines.extend(["  </g>", "</svg>", ""])
    return "\n".join(lines), len(runs)


def build_preview(
    indices: Sequence[Sequence[int]],
    alphas: Sequence[Sequence[int]],
    palette: Sequence[Sequence[int]],
    width: int,
    height: int,
    alpha_threshold: int,
) -> Image.Image:
    grid_height = len(indices)
    grid_width = len(indices[0]) if grid_height else 0
    preview = Image.new("RGBA", (grid_width, grid_height), (0, 0, 0, 0))
    preview.putdata(
        [
            (*palette[indices[y][x]], 255 if alphas[y][x] >= alpha_threshold else 0)
            for y in range(grid_height)
            for x in range(grid_width)
        ]
    )
    return preview.resize((width, height), Image.Resampling.NEAREST)


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", help="HTML, SVG, image, file URL, or HTTP URL to capture")
    parser.add_argument("-o", "--output", type=Path, required=True, help="Exact output path for the portable SVG")
    parser.add_argument(
        "--selector",
        default="svg, canvas, img, [data-dither-source]",
        help="Visible source element; defaults to the first SVG, canvas, image, or data-dither-source element",
    )
    parser.add_argument("--algorithm", choices=("ordered", "floyd-steinberg", "atkinson", "nearest"), default="ordered")
    parser.add_argument("--palette", type=parse_palette, default=parse_palette(DEFAULT_PALETTE))
    parser.add_argument("--cell-size", type=int, default=4, help="Output dither-cell size in captured CSS pixels")
    parser.add_argument("--matrix-size", type=int, choices=tuple(BAYER_MATRICES), default=4, help="Bayer matrix size for ordered dithering")
    parser.add_argument("--ordered-strength", type=float, default=0.72, help="Ordered-threshold perturbation strength from 0 to 2")
    parser.add_argument("--alpha-threshold", type=int, default=24, help="Skip cells below this 0-255 alpha value")
    parser.add_argument("--title", default="Dithered visualization")
    parser.add_argument("--animate", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--duration", type=float, default=1.35, help="Reveal duration in seconds")
    parser.add_argument("--wait-ms", type=int, default=1200, help="Extra render time before capture")
    parser.add_argument("--timeout-ms", type=int, default=30000)
    parser.add_argument("--viewport", type=parse_viewport, default=parse_viewport("1280x720"))
    parser.add_argument("--wait-until", choices=("load", "domcontentloaded", "networkidle"), default="load")
    parser.add_argument("--preview-png", type=Path, help="Optional nearest-neighbor PNG preview")
    parser.add_argument("--json-report", type=Path, help="Optional machine-readable validation report")
    parser.add_argument("--ignore-console-errors", action="store_true")
    args = parser.parse_args()
    if args.output.suffix.lower() != ".svg":
        parser.error("--output must end in .svg")
    if args.cell_size < 1 or args.cell_size > 64:
        parser.error("--cell-size must be between 1 and 64")
    if not 0 <= args.ordered_strength <= 2:
        parser.error("--ordered-strength must be between 0 and 2")
    if not 0 <= args.alpha_threshold <= 255:
        parser.error("--alpha-threshold must be between 0 and 255")
    if args.duration <= 0:
        parser.error("--duration must be positive")
    return args


def main() -> int:
    args = parse_args()
    url = source_to_url(args.input)
    width, height = args.viewport
    console_errors: list[str] = []
    page_errors: list[str] = []
    install_windows_socketpair_workaround()

    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch()
            page = browser.new_page(viewport={"width": width, "height": height}, device_scale_factor=1)
            page.on("console", lambda message: console_errors.append(message.text) if message.type == "error" else None)
            page.on("pageerror", lambda error: page_errors.append(str(error)))
            page.goto(url, wait_until=args.wait_until, timeout=args.timeout_ms)
            page.wait_for_timeout(max(args.wait_ms, 0))
            locator = page.locator(args.selector).first
            locator.wait_for(state="visible", timeout=args.timeout_ms)
            box = locator.bounding_box()
            if not box or box["width"] <= 0 or box["height"] <= 0:
                raise SystemExit("Selected element has no visible rendered box")
            screenshot = locator.screenshot(animations="disabled", caret="hide", omit_background=True)
            browser.close()
    except PlaywrightError as error:
        print(f"[ERROR] Playwright failed: {error}", file=sys.stderr)
        print("Install Chromium for Playwright if needed, then rerun the command.", file=sys.stderr)
        return 1

    if (console_errors or page_errors) and not args.ignore_console_errors:
        print("[ERROR] Browser reported errors before capture:", file=sys.stderr)
        for item in console_errors + page_errors:
            print(f"- {item}", file=sys.stderr)
        return 1

    image = Image.open(io.BytesIO(screenshot)).convert("RGBA")
    pixels, alphas = raster_grid(image, args.cell_size)
    indices = quantize_grid(pixels, args.palette, args.algorithm, args.matrix_size, args.ordered_strength)
    markup, run_count = build_svg(
        width=image.width,
        height=image.height,
        cell_size=args.cell_size,
        indices=indices,
        alphas=alphas,
        palette=args.palette,
        alpha_threshold=args.alpha_threshold,
        algorithm=args.algorithm,
        matrix_size=args.matrix_size,
        source=source_label(args.input),
        selector=args.selector,
        title=args.title,
        animate=args.animate,
        duration=args.duration,
    )
    write_text(args.output.resolve(), markup)

    if args.preview_png:
        args.preview_png.parent.mkdir(parents=True, exist_ok=True)
        build_preview(
            indices,
            alphas,
            args.palette,
            image.width,
            image.height,
            args.alpha_threshold,
        ).save(args.preview_png.resolve())

    report = {
        "ok": True,
        "output": str(args.output.resolve()),
        "source": source_label(args.input),
        "selector": args.selector,
        "algorithm": args.algorithm,
        "matrixSize": args.matrix_size if args.algorithm == "ordered" else None,
        "cellSize": args.cell_size,
        "palette": [color_hex(color) for color in args.palette],
        "sourceWidth": image.width,
        "sourceHeight": image.height,
        "gridWidth": len(indices[0]),
        "gridHeight": len(indices),
        "runCount": run_count,
        "animated": args.animate,
        "consoleErrors": console_errors,
        "pageErrors": page_errors,
    }
    if args.preview_png:
        report["preview"] = str(args.preview_png.resolve())
    if args.json_report:
        write_text(args.json_report.resolve(), json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
