#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "Pillow>=11.0.0",
#   "playwright>=1.52.0",
# ]
# ///

"""Transform an animated SVG or raster image into an optimized one-bit GIF."""

from __future__ import annotations

import argparse
import bisect
import collections
import hashlib
import importlib.util
import io
import json
import math
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Sequence

from PIL import Image, ImageDraw, ImageFont, ImageOps, UnidentifiedImageError


def load_static_engine() -> Any:
    """Load the sibling static engine without requiring the skill to be installed as a package."""
    module_path = Path(__file__).with_name("stylize_svg.py")
    spec = importlib.util.spec_from_file_location("one_bit_dither_static_engine", module_path)
    if spec is None or spec.loader is None:
        raise SystemExit(f"Cannot load the static dithering engine: {module_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    previous_bytecode_setting = sys.dont_write_bytecode
    sys.dont_write_bytecode = True
    try:
        # A shipped skill may be mounted read-only; importing the sibling must not create __pycache__.
        spec.loader.exec_module(module)
    finally:
        sys.dont_write_bytecode = previous_bytecode_setting
    return module


ENGINE = load_static_engine()
Color = tuple[int, int, int]
MAX_OUTPUT_FRAMES = 600
SUPPORTED_DITHERS = ("sierra2_4a", "floyd_steinberg", "bayer", "none")


@dataclass(frozen=True)
class AnimationSource:
    frames: tuple[Image.Image, ...]
    durations_ms: tuple[int, ...]
    loop: int
    kind: str
    format: str
    width: int
    height: int

    @property
    def frame_count(self) -> int:
        return len(self.frames)

    @property
    def duration_ms(self) -> int:
        return sum(self.durations_ms)


def normalized_duration(value: object, default_ms: int = 100) -> int:
    """Return a positive GIF-compatible source-frame duration."""
    try:
        duration = int(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        duration = default_ms
    return max(10, duration)


def load_animation(path: Path) -> AnimationSource:
    """Decode all composited frames and preserve the source frame timing."""
    try:
        with Image.open(path) as image:
            frame_count = max(1, int(getattr(image, "n_frames", 1)))
            if frame_count < 2:
                raise SystemExit(
                    f"Animated conversion needs at least two frames; {path.name} has {frame_count}. "
                    "Use stylize_svg.py for a static image."
                )
            source_format = (image.format or path.suffix.lstrip(".") or "RASTER").upper()
            loop = max(0, int(image.info.get("loop", 0) or 0))
            frames: list[Image.Image] = []
            durations: list[int] = []
            for frame_index in range(frame_count):
                image.seek(frame_index)
                # Pillow presents animated GIF/WebP/APNG frames composited onto the logical canvas.
                frame = ImageOps.exif_transpose(image).convert("RGBA").copy()
                frames.append(frame)
                durations.append(normalized_duration(image.info.get("duration")))
            width, height = frames[0].size
            if width <= 0 or height <= 0:
                raise SystemExit("Input animation has invalid dimensions")
            if any(frame.size != (width, height) for frame in frames):
                raise SystemExit("Input animation frames do not share one logical canvas size")
            return AnimationSource(tuple(frames), tuple(durations), loop, "raster", source_format, width, height)
    except (UnidentifiedImageError, OSError) as error:
        raise SystemExit(f"Pillow could not decode animated raster input {path}: {error}") from error


def resolve_output_size(source: Any, width: int, height: int | None) -> tuple[int, int]:
    if not 32 <= width <= ENGINE.MAX_RENDER_DIMENSION:
        raise SystemExit(f"--render-width must be between 32 and {ENGINE.MAX_RENDER_DIMENSION}")
    if height is None:
        height = max(32, round(width * source.height / source.width))
    if not 32 <= height <= ENGINE.MAX_RENDER_DIMENSION:
        raise SystemExit(f"--render-height must be between 32 and {ENGINE.MAX_RENDER_DIMENSION}")
    return width, height


def output_frame_count(duration_seconds: float, fps: float, max_frames: int) -> int:
    """Return a bounded frame count for a constant-rate output timeline."""
    count = max(2, round(duration_seconds * fps))
    if count > max_frames:
        raise SystemExit(
            f"Requested timeline would create {count} frames, above --max-frames={max_frames}. "
            "Lower --fps or --duration-seconds, or raise the explicit safety limit."
        )
    return count


def distributed_durations(total_ms: int, frame_count: int) -> tuple[int, ...]:
    """Distribute an exact positive duration across captured source frames."""
    if total_ms < frame_count:
        raise SystemExit("Animation duration is too short for the requested frame count")
    base, remainder = divmod(total_ms, frame_count)
    return tuple(base + (1 if index < remainder else 0) for index in range(frame_count))


def capture_svg_animation(
    path: Path,
    *,
    source_info: Any,
    size: tuple[int, int],
    fps: float,
    duration_seconds: float,
    max_frames: int,
    timeout_ms: int,
) -> AnimationSource:
    """Sample CSS and SMIL animation at deterministic browser timeline positions."""
    width, height = size
    frame_count = output_frame_count(duration_seconds, fps, max_frames)
    source_url = path.resolve().as_uri()
    blocked_urls: list[str] = []
    console_errors: list[str] = []
    page_errors: list[str] = []
    screenshots: list[bytes] = []
    ENGINE.install_windows_socketpair_workaround()

    def route_request(route: Any) -> None:
        url = route.request.url
        if url == source_url or url.startswith(("data:", "blob:", "about:")):
            route.continue_()
            return
        blocked_urls.append(url)
        route.abort()

    try:
        with ENGINE.sync_playwright() as playwright:
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
                except ENGINE.PlaywrightError as launch_error:
                    launch_errors.append(f"{label}: {launch_error}")
            if browser is None:
                raise SystemExit(
                    "No compatible Chromium browser could be launched. Install one with "
                    "`uv run --with playwright playwright install chromium`, then retry.\n"
                    + "\n".join(launch_errors)
                )
            context = browser.new_context(
                viewport={
                    "width": min(width + 32, ENGINE.MAX_RENDER_DIMENSION),
                    "height": min(height + 32, ENGINE.MAX_RENDER_DIMENSION),
                },
                device_scale_factor=1,
                # Playwright evaluation still works while authored SVG scripts and event handlers do not.
                java_script_enabled=False,
                locale="en-US",
            )
            context.route("**/*", route_request)
            page = context.new_page()
            page.on("console", lambda message: console_errors.append(message.text) if message.type == "error" else None)
            page.on("pageerror", lambda error: page_errors.append(str(error)))
            page.goto(source_url, wait_until="load", timeout=timeout_ms)
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
            page.evaluate("() => document.fonts ? document.fonts.ready : Promise.resolve()")
            for frame_index in range(frame_count):
                milliseconds = frame_index * 1000 / fps
                locator.evaluate(
                    """(element, milliseconds) => {
                        if (typeof element.pauseAnimations === 'function') {
                            element.pauseAnimations();
                        }
                        if (typeof element.setCurrentTime === 'function') {
                            element.setCurrentTime(milliseconds / 1000);
                        }
                        for (const animation of document.getAnimations()) {
                            animation.pause();
                            animation.currentTime = milliseconds;
                        }
                    }""",
                    milliseconds,
                )
                screenshots.append(locator.screenshot(caret="hide", omit_background=True, timeout=timeout_ms))
            context.close()
            browser.close()
    except ENGINE.PlaywrightError as error:
        raise SystemExit(
            "Chromium failed while sampling the animated SVG. Install it with "
            "`uv run --with playwright playwright install chromium`, then retry. "
            f"Playwright reported: {error}"
        ) from error

    if blocked_urls:
        unique_urls = sorted(set(blocked_urls))
        rendered = "\n".join(f"- {url}" for url in unique_urls[:10])
        suffix = "\n- ..." if len(unique_urls) > 10 else ""
        raise SystemExit(f"Input SVG requested blocked external resources:\n{rendered}{suffix}\nEmbed them and retry.")
    if page_errors:
        raise SystemExit("Browser page errors occurred while sampling the SVG:\n" + "\n".join(f"- {item}" for item in page_errors))
    if console_errors:
        raise SystemExit(
            "Browser console errors occurred while sampling the SVG:\n" + "\n".join(f"- {item}" for item in console_errors)
        )

    frames: list[Image.Image] = []
    for screenshot in screenshots:
        with Image.open(io.BytesIO(screenshot)) as image:
            frame = image.convert("RGBA").copy()
        if frame.size != size:
            raise SystemExit(
                f"Captured SVG frame size {frame.width}x{frame.height} did not match requested {width}x{height}"
            )
        frames.append(frame)
    durations = distributed_durations(round(duration_seconds * 1000), frame_count)
    return AnimationSource(
        tuple(frames),
        durations,
        0,
        "svg",
        "SVG",
        int(source_info.width),
        int(source_info.height),
    )


def composite_and_resize(frame: Image.Image, size: tuple[int, int], background: Color) -> Image.Image:
    canvas = Image.new("RGBA", frame.size, (*background, 255))
    canvas.alpha_composite(frame)
    if canvas.size != size:
        canvas = canvas.resize(size, Image.Resampling.LANCZOS, reducing_gap=3.0)
    return canvas


def build_timeline(
    source: AnimationSource,
    *,
    fps: float,
    duration_seconds: float | None,
    max_frames: int,
) -> tuple[list[int], float]:
    """Sample a variable-duration source onto a constant-rate GIF timeline."""
    output_duration_ms = source.duration_ms if duration_seconds is None else round(duration_seconds * 1000)
    if output_duration_ms <= 0:
        raise SystemExit("Animation duration must be positive")
    output_count = output_frame_count(output_duration_ms / 1000, fps, max_frames)

    boundaries: list[int] = []
    elapsed = 0
    for duration in source.durations_ms:
        elapsed += duration
        boundaries.append(elapsed)
    frame_period_ms = 1000 / fps
    indices: list[int] = []
    for output_index in range(output_count):
        # Sample at each output frame's midpoint. Wrap when an explicit duration spans source loops.
        source_time = ((output_index + 0.5) * frame_period_ms) % source.duration_ms
        indices.append(min(source.frame_count - 1, bisect.bisect_right(boundaries, source_time)))
    return indices, output_count / fps


def build_global_region_palette(
    grids: dict[int, tuple[list[list[Color]], list[list[int]]]],
    *,
    alpha_threshold: int,
    requested_colors: int,
) -> list[Color]:
    """Choose one animation-wide palette so regional colors do not flicker between frames."""
    histogram: collections.Counter[Color] = collections.Counter()
    for pixels, alphas in grids.values():
        for y, row in enumerate(pixels):
            for x, color in enumerate(row):
                if alphas[y][x] >= alpha_threshold:
                    histogram[color] += 1
    if not histogram:
        raise SystemExit("The animation contains no cells above --alpha-threshold")
    return ENGINE.select_region_palette(dict(histogram), min(requested_colors, len(histogram)))


def assign_global_regions(
    pixels: Sequence[Sequence[Color]],
    alphas: Sequence[Sequence[int]],
    *,
    alpha_threshold: int,
    region_colors: Sequence[Color],
) -> list[list[int]]:
    features = [ENGINE.oklab_feature(color) for color in region_colors]
    visible_colors = {
        color
        for y, row in enumerate(pixels)
        for x, color in enumerate(row)
        if alphas[y][x] >= alpha_threshold
    }
    color_assignments = {
        color: min(
            range(len(region_colors)),
            key=lambda index: (
                ENGINE.feature_distance_squared(ENGINE.oklab_feature(color), features[index]),
                index,
            ),
        )
        for color in visible_colors
    }
    assignments = [[-1 for _ in row] for row in pixels]
    for y, row in enumerate(pixels):
        for x, color in enumerate(row):
            if alphas[y][x] >= alpha_threshold:
                assignments[y][x] = color_assignments[color]
    return assignments


def render_stylized_frames(
    source: AnimationSource,
    selected_indices: Sequence[int],
    *,
    size: tuple[int, int],
    background: Color,
    cell_size: int,
    mode: str,
    matrix_size: int,
    contrast: float,
    alpha_threshold: int,
    custom_color: Color | None,
    requested_region_colors: int,
    colorset: str = "colorset1",
) -> tuple[dict[int, Image.Image], list[Color], list[dict[str, object]]]:
    """Render only unique selected source frames and reuse them on the output timeline."""
    unique_indices = sorted(set(selected_indices))
    sampled_grids: dict[int, tuple[list[list[Color]], list[list[int]]]] = {}
    for source_index in unique_indices:
        rendered = composite_and_resize(source.frames[source_index], size, background)
        sampled_grids[source_index] = ENGINE.raster_grid(rendered, cell_size)

    region_colors: list[Color] | None = None
    if mode == "regional":
        region_colors = build_global_region_palette(
            sampled_grids,
            alpha_threshold=alpha_threshold,
            requested_colors=requested_region_colors,
        )

    output_frames: dict[int, Image.Image] = {}
    palette: list[Color] = []
    region_metadata: list[dict[str, object]] = []
    for source_index in unique_indices:
        pixels, alphas = sampled_grids[source_index]
        assignments = None
        if region_colors is not None:
            assignments = assign_global_regions(
                pixels,
                alphas,
                alpha_threshold=alpha_threshold,
                region_colors=region_colors,
            )
        grid, paints, region_pairs = ENGINE.build_paint_grid(
            pixels,
            alphas,
            mode=mode,
            matrix_size=matrix_size,
            contrast=contrast,
            alpha_threshold=alpha_threshold,
            custom_color=custom_color,
            region_assignments=assignments,
            region_colors=region_colors,
            colorset=colorset,
        )
        preview = ENGINE.build_preview(
            width=size[0],
            height=size[1],
            cell_size=cell_size,
            grid=grid,
            paints=paints,
        )
        # GIF output is intentionally opaque. Transparency is flattened before dithering.
        opaque = Image.new("RGB", size, background)
        opaque.paste(preview, mask=preview.getchannel("A"))
        output_frames[source_index] = opaque
        if not palette:
            palette = ENGINE.unique_palette(paints)
        if not region_metadata and region_pairs:
            region_metadata = [
                {
                    "index": index,
                    "color": ENGINE.color_hex(pair.color),
                    "companion": ENGINE.color_hex(pair.companion),
                    "contrastRatio": round(pair.contrast_ratio, 4),
                }
                for index, pair in enumerate(region_pairs)
            ]
    return output_frames, palette, region_metadata


def ffmpeg_version(ffmpeg: str) -> str:
    result = subprocess.run(
        [ffmpeg, "-version"],
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    return result.stdout.splitlines()[0].strip()


def run_ffmpeg(command: list[str], label: str) -> None:
    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if result.returncode != 0:
        details = (result.stderr or result.stdout).strip()
        raise SystemExit(f"ffmpeg {label} failed:\n{details}")


def encode_gif(
    frame_directory: Path,
    output: Path,
    *,
    fps: float,
    colors: int,
    dither: str,
    loop: int,
    ffmpeg: str,
) -> None:
    """Encode with a palette generated from the whole animation."""
    input_pattern = str(frame_directory / "frame-%06d.png")
    palette_path = frame_directory / "palette.png"
    # Frames are flattened onto an opaque background, so every palette slot can carry a visible tone.
    palette_filter = f"palettegen=max_colors={colors}:reserve_transparent=0:stats_mode=full"
    run_ffmpeg(
        [
            ffmpeg,
            "-hide_banner",
            "-loglevel",
            "error",
            "-y",
            "-framerate",
            f"{fps:g}",
            "-i",
            input_pattern,
            "-vf",
            palette_filter,
            str(palette_path),
        ],
        "palette generation",
    )
    palette_use = f"paletteuse=dither={dither}:diff_mode=rectangle"
    output.parent.mkdir(parents=True, exist_ok=True)
    run_ffmpeg(
        [
            ffmpeg,
            "-hide_banner",
            "-loglevel",
            "error",
            "-y",
            "-framerate",
            f"{fps:g}",
            "-i",
            input_pattern,
            "-i",
            str(palette_path),
            "-lavfi",
            palette_use,
            "-loop",
            str(loop),
            str(output),
        ],
        "GIF encoding",
    )


def create_contact_sheet(
    frames: Sequence[Image.Image],
    output: Path,
    *,
    source_indices: Sequence[int],
    columns: int = 4,
    samples: int = 12,
) -> None:
    sample_count = min(samples, len(frames))
    positions = sorted({round(index * (len(frames) - 1) / max(1, sample_count - 1)) for index in range(sample_count)})
    thumb_width = min(320, frames[0].width)
    thumb_height = round(thumb_width * frames[0].height / frames[0].width)
    label_height = 28
    rows = math.ceil(len(positions) / columns)
    sheet = Image.new("RGB", (columns * thumb_width, rows * (thumb_height + label_height)), (247, 247, 247))
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.load_default(size=14)
    for item_index, timeline_index in enumerate(positions):
        column = item_index % columns
        row = item_index // columns
        left = column * thumb_width
        top = row * (thumb_height + label_height)
        thumb = frames[timeline_index].resize((thumb_width, thumb_height), Image.Resampling.NEAREST)
        sheet.paste(thumb, (left, top))
        label = f"out {timeline_index + 1:03d} · src {source_indices[timeline_index] + 1:03d}"
        draw.text((left + 8, top + thumb_height + 6), label, fill=(51, 62, 72), font=font)
    output.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(output)


def inspect_output(path: Path) -> dict[str, object]:
    try:
        with Image.open(path) as image:
            frame_count = max(1, int(getattr(image, "n_frames", 1)))
            durations: list[int] = []
            colors: set[Color] = set()
            for frame_index in range(frame_count):
                image.seek(frame_index)
                durations.append(normalized_duration(image.info.get("duration")))
                converted = image.convert("RGB")
                counted = converted.getcolors(maxcolors=1 << 24)
                if counted is not None:
                    colors.update(color for _, color in counted)
            return {
                "format": image.format,
                "width": image.width,
                "height": image.height,
                "frameCount": frame_count,
                "durationMs": sum(durations),
                "loop": int(image.info.get("loop", 0) or 0),
                "paletteColors": [ENGINE.color_hex(color) for color in sorted(colors)],
                "paletteColorCount": len(colors),
            }
    except (UnidentifiedImageError, OSError) as error:
        raise SystemExit(f"Encoded GIF could not be inspected: {error}") from error


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="Animated SVG, GIF, WebP, APNG, or other Pillow-decoded raster")
    parser.add_argument("-o", "--output", type=Path, required=True, help="Exact .gif output path")
    parser.add_argument("--mode", choices=ENGINE.MODES, required=True)
    parser.add_argument(
        "--quality-profile",
        choices=tuple(ENGINE.QUALITY_PROFILES),
        default="balanced",
        help="Density baseline; explicit render and dither flags override individual values",
    )
    parser.add_argument("--color", type=ENGINE.parse_hex_color, help="Custom mode ink color")
    parser.add_argument("--colorset", choices=("colorset1", "colorset2"), default="colorset1")
    parser.add_argument("--region-colors", type=int, help="Animation-wide source-color region count")
    parser.add_argument("--render-width", type=int, help="Output width; detailed defaults to 1280")
    parser.add_argument("--render-height", type=int, help="Optional exact output height")
    parser.add_argument("--cell-size", type=int, help="Output pixels represented by one ordered-dither cell")
    parser.add_argument("--matrix-size", type=int, choices=tuple(ENGINE.BAYER_MATRICES))
    parser.add_argument("--contrast", type=float)
    parser.add_argument("--alpha-threshold", type=int, default=24)
    parser.add_argument("--background", type=ENGINE.parse_hex_color, default=ENGINE.WHITE)
    parser.add_argument("--fps", type=float, default=12.0, help="Constant output rate used to resample source timing")
    parser.add_argument(
        "--duration-seconds",
        type=float,
        help="Required SVG capture window; optional raster trim/repeat duration (defaults to one source cycle)",
    )
    parser.add_argument("--timeout-ms", type=int, default=30000, help="Browser timeout for animated SVG capture")
    parser.add_argument("--loop", type=int, default=0, help="GIF loop count; 0 means infinite")
    parser.add_argument("--max-frames", type=int, default=MAX_OUTPUT_FRAMES, help="Explicit output-frame safety limit")
    parser.add_argument("--colors", type=int, default=256, help="Maximum ffmpeg palette size")
    parser.add_argument("--dither", choices=SUPPORTED_DITHERS, default="sierra2_4a")
    parser.add_argument("--ffmpeg", help="ffmpeg executable; defaults to PATH lookup")
    parser.add_argument("--contact-sheet", type=Path, help="Optional PNG visual-review sheet")
    parser.add_argument("--json-report", type=Path, help="Optional conversion manifest")
    args = parser.parse_args(argv)
    allowed = set(ENGINE.colorset_colors(args.colorset))
    if args.background not in allowed or (args.color is not None and args.color not in allowed):
        parser.error("Authored background/custom ink must belong to --colorset")

    quality = ENGINE.resolve_quality_settings(
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
        parser.error(f"input animation not found: {args.input}")
    if args.output.suffix.lower() != ".gif":
        parser.error("--output must end in .gif")
    if args.output.resolve() == args.input.resolve():
        parser.error("--output must not overwrite the input animation")
    if args.contact_sheet and args.contact_sheet.suffix.lower() != ".png":
        parser.error("--contact-sheet must end in .png")
    if args.json_report and args.json_report.suffix.lower() != ".json":
        parser.error("--json-report must end in .json")
    if args.mode == "custom" and args.color is None:
        parser.error("custom mode requires --color")
    if args.mode != "custom" and args.color is not None:
        parser.error("--color is valid only in custom mode")
    if args.color == ENGINE.WHITE:
        parser.error("custom mode color cannot be white")
    if not 2 <= args.region_colors <= 32:
        parser.error("--region-colors must be between 2 and 32")
    if not 1 <= args.cell_size <= 64:
        parser.error("--cell-size must be between 1 and 64")
    if not 0.25 <= args.contrast <= 4:
        parser.error("--contrast must be between 0.25 and 4")
    if not 0 <= args.alpha_threshold <= 255:
        parser.error("--alpha-threshold must be between 0 and 255")
    if not 1 <= args.fps <= 60:
        parser.error("--fps must be between 1 and 60")
    if args.duration_seconds is not None and not 0.1 <= args.duration_seconds <= 120:
        parser.error("--duration-seconds must be between 0.1 and 120")
    if not 1000 <= args.timeout_ms <= 120000:
        parser.error("--timeout-ms must be between 1000 and 120000")
    if not 0 <= args.loop <= 65535:
        parser.error("--loop must be between 0 and 65535")
    if not 2 <= args.max_frames <= 5000:
        parser.error("--max-frames must be between 2 and 5000")
    if not 2 <= args.colors <= 256:
        parser.error("--colors must be between 2 and 256")
    return args


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    source_info = ENGINE.inspect_source(args.input, 0)
    width, height = resolve_output_size(source_info, args.render_width, args.render_height)
    if source_info.kind == "svg":
        if args.duration_seconds is None:
            raise SystemExit("Animated SVG input requires --duration-seconds to define the browser capture window")
        source = capture_svg_animation(
            args.input,
            source_info=source_info,
            size=(width, height),
            fps=args.fps,
            duration_seconds=args.duration_seconds,
            max_frames=args.max_frames,
            timeout_ms=args.timeout_ms,
        )
        selected_indices = list(range(source.frame_count))
        timeline_duration = source.frame_count / args.fps
    else:
        source = load_animation(args.input)
        # Pillow may resolve orientation or a logical animation canvas differently from the probe.
        width, height = resolve_output_size(source, args.render_width, args.render_height)
        selected_indices, timeline_duration = build_timeline(
            source,
            fps=args.fps,
            duration_seconds=args.duration_seconds,
            max_frames=args.max_frames,
        )
    rendered_by_source, palette, regions = render_stylized_frames(
        source,
        selected_indices,
        size=(width, height),
        background=args.background,
        cell_size=args.cell_size,
        mode=args.mode,
        matrix_size=args.matrix_size,
        contrast=args.contrast,
        alpha_threshold=args.alpha_threshold,
        custom_color=args.color,
        requested_region_colors=args.region_colors,
        colorset=args.colorset,
    )
    timeline_frames = [rendered_by_source[index] for index in selected_indices]

    ffmpeg = args.ffmpeg or shutil.which("ffmpeg")
    if not ffmpeg:
        raise SystemExit("ffmpeg is required for palette-optimized GIF encoding but was not found on PATH")
    output_path = args.output.resolve()
    with tempfile.TemporaryDirectory(prefix="one-bit-dither-gif-") as temporary:
        frame_directory = Path(temporary)
        for frame_index, frame in enumerate(timeline_frames):
            frame.save(frame_directory / f"frame-{frame_index:06d}.png", optimize=False)
        encode_gif(
            frame_directory,
            output_path,
            fps=args.fps,
            colors=args.colors,
            dither=args.dither,
            loop=args.loop,
            ffmpeg=ffmpeg,
        )

    contact_path: Path | None = None
    if args.contact_sheet:
        contact_path = args.contact_sheet.resolve()
        create_contact_sheet(timeline_frames, contact_path, source_indices=selected_indices)

    output_probe = inspect_output(output_path)
    report: dict[str, object] = {
        "ok": True,
        "schema": "one-bit-dither-gif/v1",
        "colorset": args.colorset,
        "output": str(output_path),
        "contactSheet": str(contact_path) if contact_path else None,
        "sha256": hashlib.sha256(output_path.read_bytes()).hexdigest(),
        "source": {
            "path": str(args.input.resolve()),
            "kind": source.kind,
            "format": source.format,
            "width": source.width,
            "height": source.height,
            "frameCount": source.frame_count,
            "durationMs": source.duration_ms,
            "loop": source.loop,
        },
        "mode": args.mode,
        "qualityProfile": args.quality_profile,
        "render": {
            "width": width,
            "height": height,
            "fps": args.fps,
            "frameCount": len(timeline_frames),
            "durationSeconds": round(timeline_duration, 6),
            "captureMethod": "browser-timeline" if source.kind == "svg" else "decoded-raster-timeline",
            "cellSize": args.cell_size,
            "matrixSize": args.matrix_size,
            "contrast": args.contrast,
            "alphaThreshold": args.alpha_threshold,
            "background": ENGINE.color_hex(args.background),
        },
        "palette": [ENGINE.color_hex(color) for color in palette],
        "regions": regions,
        "encoding": {
            "encoder": ffmpeg_version(ffmpeg),
            "maxColors": args.colors,
            "dither": args.dither,
            "loop": args.loop,
        },
        "probe": output_probe,
    }
    if args.json_report:
        report_path = args.json_report.resolve()
        write_json(report_path, report)
        report["report"] = str(report_path)
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
