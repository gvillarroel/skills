#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "Pillow>=11.0.0",
#   "playwright>=1.52.0",
# ]
# ///

"""Restyle a local image or video as palette-controlled, nearest-neighbor pixel art."""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import math
import re
import shutil
import socket
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from typing import Any, Sequence

from PIL import Image, ImageDraw, ImageEnhance, ImageFont, ImageOps, UnidentifiedImageError
from colorset_contract import colors as colorset_colors, nearest as nearest_token, tokens as colorset_tokens
from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import Route, sync_playwright


Color = tuple[int, int, int]
MAX_DIMENSION = 4096
MAX_OUTPUT_PIXEL_FRAMES = 300_000_000
PROFILES: dict[str, tuple[int, int]] = {
    "chunky": (8, 16),
    "balanced": (5, 24),
    "detailed": (3, 32),
    "manual": (5, 24),
}
PRESET_PALETTES: dict[str, tuple[str, ...]] = {
    "forest4": ("#1c1c1c", "#294d19", "#45842a", "#dbffcc"),
    "sunset8": (
        "#431f47", "#652f6c", "#6d1222", "#9e1b32",
        "#e77204", "#ff9633", "#ffd332", "#fff4cc",
    ),
}
BAYER4 = ((0, 8, 2, 10), (12, 4, 14, 6), (3, 11, 1, 9), (15, 7, 13, 5))


@dataclass(frozen=True)
class SourceInfo:
    kind: str
    format: str
    width: int
    height: int
    duration: float | None = None
    fps: float | None = None
    audio: bool = False


def parse_color(value: str) -> Color:
    token = value.strip().lower()
    if re.fullmatch(r"#[0-9a-f]{3}", token):
        token = "#" + "".join(character * 2 for character in token[1:])
    if not re.fullmatch(r"#[0-9a-f]{6}", token):
        raise argparse.ArgumentTypeError(f"Expected #RGB or #RRGGBB color, received {value!r}")
    return tuple(int(token[index : index + 2], 16) for index in (1, 3, 5))  # type: ignore[return-value]


def color_hex(color: Color) -> str:
    return "#" + "".join(f"{channel:02x}" for channel in color)


def run(command: list[str], label: str) -> subprocess.CompletedProcess[bytes]:
    try:
        result = subprocess.run(command, capture_output=True, check=False)
    except OSError as error:
        raise SystemExit(f"Cannot run {label}: {error}") from error
    if result.returncode != 0:
        details = result.stderr.decode("utf-8", errors="replace").strip()
        raise SystemExit(f"{label} failed:\n{details or f'exit code {result.returncode}'}")
    return result


def parse_svg_dimension(value: str | None) -> float | None:
    if not value:
        return None
    match = re.fullmatch(r"\s*(\d+(?:\.\d+)?)\s*(?:px|pt|pc|mm|cm|in)?\s*", value, re.IGNORECASE)
    if not match:
        return None
    number = float(match.group(1))
    return number if number > 0 else None


def inspect_svg(path: Path) -> SourceInfo | None:
    try:
        root = ET.parse(path).getroot()
    except (ET.ParseError, UnicodeError):
        return None
    except OSError as error:
        raise SystemExit(f"Cannot read source image: {error}") from error
    if root.tag.rsplit("}", 1)[-1] != "svg":
        return None
    view_box = root.get("viewBox")
    if view_box:
        parts = [part for part in re.split(r"[\s,]+", view_box.strip()) if part]
        if len(parts) == 4:
            try:
                width, height = float(parts[2]), float(parts[3])
                if width > 0 and height > 0:
                    return SourceInfo("svg", "SVG", round(width), round(height))
            except ValueError:
                pass
    width = parse_svg_dimension(root.get("width"))
    height = parse_svg_dimension(root.get("height"))
    if width and height:
        return SourceInfo("svg", "SVG", round(width), round(height))
    raise SystemExit("SVG source needs a positive viewBox or numeric width and height")


def inspect_raster(path: Path) -> SourceInfo | None:
    try:
        with Image.open(path) as image:
            oriented = ImageOps.exif_transpose(image)
            width, height = oriented.size
            if width <= 0 or height <= 0:
                raise SystemExit("Source image has invalid dimensions")
            return SourceInfo("raster", (image.format or "RASTER").upper(), width, height)
    except (UnidentifiedImageError, OSError):
        return None


def inspect_motion(path: Path, ffprobe: str | None) -> SourceInfo:
    if not ffprobe:
        raise SystemExit("ffprobe is required to inspect a video source")
    output = run(
        [ffprobe, "-v", "error", "-show_streams", "-show_format", "-of", "json", str(path)],
        "ffprobe source inspection",
    ).stdout
    try:
        data = json.loads(output)
        streams = data.get("streams", [])
        video = next(stream for stream in streams if stream.get("codec_type") == "video")
    except (ValueError, StopIteration, TypeError) as error:
        raise SystemExit(f"No decodable video stream found in {path}") from error
    width, height = int(video.get("width", 0)), int(video.get("height", 0))
    if width <= 0 or height <= 0:
        raise SystemExit("Source video has invalid dimensions")
    raw_duration = video.get("duration") or data.get("format", {}).get("duration")
    try:
        duration = float(raw_duration) if raw_duration not in (None, "N/A") else None
    except (TypeError, ValueError):
        duration = None
    raw_fps = video.get("avg_frame_rate") or video.get("r_frame_rate") or "0/1"
    try:
        fps = float(Fraction(raw_fps))
    except (ValueError, ZeroDivisionError):
        fps = None
    return SourceInfo(
        "video",
        str(video.get("codec_name") or "VIDEO").upper(),
        width,
        height,
        duration,
        fps if fps and fps > 0 else None,
        any(stream.get("codec_type") == "audio" for stream in streams),
    )


def inspect_source(path: Path, ffprobe: str | None, *, motion: bool) -> SourceInfo:
    if motion:
        if inspect_svg(path) is not None:
            raise SystemExit("Animated SVG is not a direct motion input here; use a video/GIF source or render SVG motion first")
        return inspect_motion(path, ffprobe)
    return inspect_svg(path) or inspect_raster(path) or inspect_motion(path, ffprobe)


def resolve_dimensions(source: SourceInfo, width: int | None, height: int | None, pixel_size: int) -> tuple[int, int, int, int]:
    if width is None and height is None:
        width, height = source.width, source.height
    elif width is None:
        width = round(height * source.width / source.height)  # type: ignore[operator]
    elif height is None:
        height = round(width * source.height / source.width)
    assert width is not None and height is not None
    if not 32 <= width <= MAX_DIMENSION or not 32 <= height <= MAX_DIMENSION:
        raise SystemExit(f"Output width and height must each be between 32 and {MAX_DIMENSION}")
    logical_width = max(1, math.ceil(width / pixel_size))
    logical_height = max(1, math.ceil(height / pixel_size))
    return width, height, logical_width, logical_height


def windows_socketpair_workaround() -> None:
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


def render_svg(path: Path, size: tuple[int, int], timeout_ms: int) -> Image.Image:
    width, height = size
    source_url = path.resolve().as_uri()
    blocked: list[str] = []
    page_errors: list[str] = []
    windows_socketpair_workaround()

    def route_request(route: Route) -> None:
        url = route.request.url
        if url == source_url or url.startswith(("data:", "blob:", "about:")):
            route.continue_()
        else:
            blocked.append(url)
            route.abort()

    try:
        with sync_playwright() as playwright:
            browser = None
            failures: list[str] = []
            for label, options in (
                ("bundled Chromium", {}),
                ("Microsoft Edge", {"channel": "msedge"}),
                ("Google Chrome", {"channel": "chrome"}),
            ):
                try:
                    browser = playwright.chromium.launch(**options)
                    break
                except PlaywrightError as error:
                    failures.append(f"{label}: {error}")
            if browser is None:
                raise SystemExit("No compatible Chromium browser could be launched. Install Playwright Chromium.\n" + "\n".join(failures))
            context = browser.new_context(
                viewport={"width": min(width + 32, MAX_DIMENSION), "height": min(height + 32, MAX_DIMENSION)},
                device_scale_factor=1,
                java_script_enabled=False,
            )
            context.route("**/*", route_request)
            page = context.new_page()
            page.on("pageerror", lambda error: page_errors.append(str(error)))
            page.goto(source_url, wait_until="load", timeout=timeout_ms)
            svg = page.locator("svg").first
            svg.wait_for(state="visible", timeout=timeout_ms)
            svg.evaluate(
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
            screenshot = svg.screenshot(animations="disabled", caret="hide", omit_background=True, timeout=timeout_ms)
            context.close()
            browser.close()
    except PlaywrightError as error:
        raise SystemExit(f"Chromium failed while rendering SVG: {error}") from error
    if blocked:
        raise SystemExit("SVG requested blocked external resources; embed them first:\n" + "\n".join(sorted(set(blocked))[:10]))
    if page_errors:
        raise SystemExit("SVG browser errors:\n" + "\n".join(page_errors))
    with Image.open(io.BytesIO(screenshot)) as image:
        result = image.convert("RGBA").copy()
    if result.size != size:
        raise SystemExit(f"Rendered SVG size {result.size} did not match requested {size}")
    return result


def load_still(
    path: Path,
    source: SourceInfo,
    size: tuple[int, int],
    *,
    start: float,
    ffmpeg: str,
    timeout_ms: int,
    exact_colors: bool = False,
) -> Image.Image:
    if source.kind == "svg":
        return render_svg(path, size, timeout_ms)
    if source.kind == "raster":
        try:
            with Image.open(path) as image:
                frame = ImageOps.exif_transpose(image).convert("RGBA")
                return frame if exact_colors else frame.resize(size, Image.Resampling.LANCZOS, reducing_gap=3.0)
        except (UnidentifiedImageError, OSError) as error:
            raise SystemExit(f"Cannot decode raster image: {error}") from error
    command = [ffmpeg, "-hide_banner", "-loglevel", "error", "-ss", f"{start:g}", "-i", str(path), "-frames:v", "1"]
    if not exact_colors:
        command.extend(["-vf", f"scale={size[0]}:{size[1]}:flags=lanczos"])
    command.extend(["-f", "image2pipe", "-vcodec", "png", "pipe:1"])
    result = run(command, "video still extraction")
    try:
        with Image.open(io.BytesIO(result.stdout)) as image:
            return image.convert("RGBA").copy()
    except (UnidentifiedImageError, OSError) as error:
        raise SystemExit(f"Could not decode extracted video frame: {error}") from error


def enhanced_logical(image: Image.Image, size: tuple[int, int], background: Color, contrast: float, saturation: float) -> tuple[Image.Image, Image.Image]:
    source = image.convert("RGBA").resize(size, Image.Resampling.BOX)
    alpha = source.getchannel("A")
    opaque = Image.new("RGBA", size, (*background, 255))
    opaque.alpha_composite(source)
    rgb = opaque.convert("RGB")
    if contrast != 1:
        rgb = ImageEnhance.Contrast(rgb).enhance(contrast)
    if saturation != 1:
        rgb = ImageEnhance.Color(rgb).enhance(saturation)
    return rgb, alpha


def bayer_perturb(image: Image.Image, strength: float) -> Image.Image:
    if strength <= 0:
        return image
    result = image.copy()
    pixels = result.load()
    for y in range(result.height):
        for x in range(result.width):
            offset = ((BAYER4[y % 4][x % 4] + 0.5) / 16 - 0.5) * 64 * strength
            red, green, blue = pixels[x, y]
            pixels[x, y] = tuple(max(0, min(255, round(channel + offset))) for channel in (red, green, blue))
    return result


def adaptive_palette(frames: Sequence[Image.Image], colors: int) -> list[Color]:
    if not frames:
        raise SystemExit("Cannot fit a palette without source frames")
    columns = min(4, len(frames))
    rows = math.ceil(len(frames) / columns)
    sample = Image.new("RGB", (columns * 96, rows * 96), (0, 0, 0))
    for index, frame in enumerate(frames):
        thumbnail = frame.convert("RGB").resize((96, 96), Image.Resampling.BOX)
        sample.paste(thumbnail, ((index % columns) * 96, (index // columns) * 96))
    quantized = sample.quantize(colors=colors, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    values = quantized.getpalette() or []
    used = sorted(quantized.getcolors(maxcolors=256) or [], key=lambda pair: (-pair[0], pair[1]))
    palette: list[Color] = []
    for _, index in used:
        candidate = tuple(values[index * 3 : index * 3 + 3])
        if len(candidate) == 3 and candidate not in palette:
            palette.append(candidate)  # type: ignore[arg-type]
    return palette or [(0, 0, 0)]


def build_palette_image(colors: Sequence[Color]) -> Image.Image:
    if not colors or len(colors) > 256:
        raise SystemExit("Palette must contain 1–256 colors")
    fill = colors[-1]
    flattened = [channel for color in (*colors, *((fill,) * (256 - len(colors)))) for channel in color]
    image = Image.new("P", (1, 1))
    image.putpalette(flattened)
    return image


def quantize_frame(
    rgb: Image.Image,
    palette_image: Image.Image,
    *,
    dither: str,
    dither_strength: float,
) -> Image.Image:
    working = bayer_perturb(rgb, dither_strength) if dither == "bayer4" else rgb
    method = Image.Dither.FLOYDSTEINBERG if dither == "floyd" else Image.Dither.NONE
    return working.quantize(palette=palette_image, dither=method).convert("RGB")


def upscale(
    logical: Image.Image,
    size: tuple[int, int],
    *,
    alpha: Image.Image | None = None,
    alpha_threshold: int = 128,
) -> Image.Image:
    expanded = logical.resize(size, Image.Resampling.NEAREST)
    if alpha is None:
        return expanded
    mask = alpha.point(lambda value: 255 if value >= alpha_threshold else 0)
    expanded.putalpha(mask.resize(size, Image.Resampling.NEAREST))
    return expanded


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def fit_palette(frames: Sequence[Image.Image], args: argparse.Namespace) -> list[Color]:
    mode = getattr(args, "colorset", "colorset1")
    if args.palette in {"colorset1", "colorset2"}:
        return list(colorset_colors(args.palette))
    if args.palette == "custom":
        return list(dict.fromkeys(args.color))
    if args.palette in PRESET_PALETTES:
        return [parse_color(value) for value in PRESET_PALETTES[args.palette]]
    fitted = adaptive_palette(frames, args.colors)
    return list(dict.fromkeys(nearest_token(color, mode) for color in fitted))


def convert_still(args: argparse.Namespace, source: SourceInfo, size: tuple[int, int], logical_size: tuple[int, int]) -> dict[str, Any]:
    image = load_still(
        args.input, source, size, start=args.start, ffmpeg=args.ffmpeg, timeout_ms=args.timeout_ms,
        exact_colors=args.palette == "preserve",
    )
    if args.palette == "preserve":
        sampled = image.convert("RGBA").resize(logical_size, Image.Resampling.NEAREST)
        logical, alpha = sampled.convert("RGB"), sampled.getchannel("A")
        colors = None
    else:
        rgb, alpha = enhanced_logical(image, logical_size, args.background, args.contrast, args.saturation)
        colors = fit_palette([rgb], args)
        logical = quantize_frame(rgb, build_palette_image(colors), dither=args.dither, dither_strength=args.dither_strength)
    preserve = args.alpha == "preserve" and alpha.getextrema() != (255, 255)
    output = upscale(logical, size, alpha=alpha if preserve else None, alpha_threshold=args.alpha_threshold)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    if args.output.suffix.lower() == ".webp":
        output.save(args.output, format="WEBP", lossless=True, method=6)
    else:
        output.save(args.output, format="PNG", optimize=True)
    return {
        "palette": [color_hex(color) for color in colors] if colors is not None else None,
        "alphaPreserved": preserve,
        "motion": None,
    }


def source_timeline(source: SourceInfo, args: argparse.Namespace) -> tuple[float, int, float]:
    if source.duration is None and args.duration is None:
        raise SystemExit("Source duration is unavailable; set --duration explicitly")
    remaining = None if source.duration is None else source.duration - args.start
    duration = args.duration if args.duration is not None else remaining
    if duration is None or duration <= 0:
        raise SystemExit("Selected video duration must be positive")
    if remaining is not None and args.duration is not None and duration > remaining + 0.02:
        raise SystemExit("--start plus --duration extends beyond the source duration")
    if duration > 120:
        raise SystemExit("Video output is limited to 120 seconds per run; select a shorter --duration")
    frame_count = max(2, round(duration * args.fps))
    if frame_count > args.max_frames:
        raise SystemExit(
            f"Requested output needs {frame_count} frames, above --max-frames={args.max_frames}; "
            "lower duration or fps"
        )
    return duration, frame_count, frame_count / args.fps


def extract_motion_frames(args: argparse.Namespace, directory: Path, logical_size: tuple[int, int], duration: float) -> list[Path]:
    pattern = directory / "source-%06d.png"
    scale = f"scale={logical_size[0]}:{logical_size[1]}:flags=neighbor"
    filters = f"fps={args.fps:g},format=rgb24,{scale}" if args.palette == "preserve" else f"fps={args.fps:g},scale={logical_size[0]}:{logical_size[1]}:flags=area,format=rgb24"
    run(
        [
            args.ffmpeg, "-hide_banner", "-loglevel", "error", "-y",
            "-ss", f"{args.start:g}", "-i", str(args.input), "-t", f"{duration:g}",
            "-vf", filters,
            "-start_number", "0", str(pattern),
        ],
        "video frame extraction",
    )
    paths = sorted(directory.glob("source-*.png"))
    if len(paths) < 2:
        raise SystemExit("The selected source interval yielded fewer than two frames")
    if len(paths) > args.max_frames:
        raise SystemExit(f"Decoded {len(paths)} frames, above --max-frames={args.max_frames}")
    return paths


def contact_sheet(frame_paths: Sequence[Path], output: Path) -> None:
    positions = sorted({round(index * (len(frame_paths) - 1) / 11) for index in range(12)})
    with Image.open(frame_paths[0]) as first:
        thumb_width = min(320, first.width)
        thumb_height = round(thumb_width * first.height / first.width)
    sheet = Image.new("RGB", (thumb_width * 4, (thumb_height + 27) * 3), (247, 247, 247))
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.load_default(size=14)
    for item, frame_index in enumerate(positions):
        with Image.open(frame_paths[frame_index]) as frame:
            thumb = frame.convert("RGB").resize((thumb_width, thumb_height), Image.Resampling.NEAREST)
        left = (item % 4) * thumb_width
        top = (item // 4) * (thumb_height + 27)
        sheet.paste(thumb, (left, top))
        draw.text((left + 8, top + thumb_height + 5), f"frame {frame_index + 1:03d}", fill=(51, 62, 72), font=font)
    output.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(output)


def encode_gif(args: argparse.Namespace, directory: Path) -> None:
    frame_pattern = str(directory / "pixel-%06d.png")
    palette_path = str(directory / "gif-palette.png")
    run(
        [
            args.ffmpeg, "-hide_banner", "-loglevel", "error", "-y",
            "-framerate", f"{args.fps:g}", "-i", frame_pattern,
            "-vf", "palettegen=reserve_transparent=0:stats_mode=full",
            palette_path,
        ],
        "GIF palette generation",
    )
    run(
        [
            args.ffmpeg, "-hide_banner", "-loglevel", "error", "-y",
            "-framerate", f"{args.fps:g}", "-i", frame_pattern, "-i", palette_path,
            "-lavfi", "paletteuse=dither=none:diff_mode=rectangle",
            "-loop", str(args.loop), str(args.output),
        ],
        "GIF encoding",
    )


def encode_mp4(args: argparse.Namespace, directory: Path, *, source_audio: bool, duration: float) -> bool:
    frame_pattern = str(directory / "pixel-%06d.png")
    include_audio = source_audio and args.audio == "keep"
    command = [
        args.ffmpeg, "-hide_banner", "-loglevel", "error", "-y",
        "-framerate", f"{args.fps:g}", "-i", frame_pattern,
    ]
    if include_audio:
        command.extend(["-ss", f"{args.start:g}", "-i", str(args.input)])
    command.extend(["-map", "0:v:0"])
    if include_audio:
        command.extend(["-map", "1:a:0", "-c:a", "aac", "-b:a", "192k"])
    else:
        command.append("-an")
    command.extend(
        [
            "-c:v", "libx264", "-preset", "medium", "-crf", "16",
            "-pix_fmt", "yuv420p", "-movflags", "+faststart",
            "-t", f"{duration:.6f}", str(args.output),
        ]
    )
    run(command, "MP4 encoding")
    return include_audio


def encode_mkv(args: argparse.Namespace, directory: Path, *, source_audio: bool, duration: float) -> bool:
    frame_pattern = str(directory / "pixel-%06d.png")
    include_audio = source_audio and args.audio == "keep"
    command = [
        args.ffmpeg, "-hide_banner", "-loglevel", "error", "-y",
        "-framerate", f"{args.fps:g}", "-i", frame_pattern,
    ]
    if include_audio:
        command.extend(["-ss", f"{args.start:g}", "-i", str(args.input)])
    command.extend(["-map", "0:v:0"])
    if include_audio:
        command.extend(["-map", "1:a:0", "-c:a", "flac"])
    else:
        command.append("-an")
    command.extend(["-c:v", "ffv1", "-level", "3", "-pix_fmt", "bgr0", "-t", f"{duration:.6f}", str(args.output)])
    run(command, "lossless MKV encoding")
    return include_audio


def convert_motion(args: argparse.Namespace, source: SourceInfo, size: tuple[int, int], logical_size: tuple[int, int]) -> dict[str, Any]:
    duration, predicted_frames, _ = source_timeline(source, args)
    if size[0] * size[1] * predicted_frames > MAX_OUTPUT_PIXEL_FRAMES:
        raise SystemExit(
            "Requested video exceeds the output-pixel safety budget; lower dimensions, fps, or duration"
        )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="pixel-art-video-") as temporary:
        directory = Path(temporary)
        source_paths = extract_motion_frames(args, directory, logical_size, duration)
        if args.palette == "preserve":
            colors = None
            palette_image = None
        else:
            sample_positions = sorted({round(index * (len(source_paths) - 1) / max(1, min(16, len(source_paths)) - 1)) for index in range(min(16, len(source_paths)))})
            samples: list[Image.Image] = []
            for position in sample_positions:
                with Image.open(source_paths[position]) as image:
                    rgb = image.convert("RGB")
                if args.contrast != 1:
                    rgb = ImageEnhance.Contrast(rgb).enhance(args.contrast)
                if args.saturation != 1:
                    rgb = ImageEnhance.Color(rgb).enhance(args.saturation)
                samples.append(rgb)
            colors = fit_palette(samples, args)
            palette_image = build_palette_image(colors)
        output_paths: list[Path] = []
        for index, source_path in enumerate(source_paths):
            with Image.open(source_path) as image:
                rgb = image.convert("RGB")
            if args.contrast != 1:
                rgb = ImageEnhance.Contrast(rgb).enhance(args.contrast)
            if args.saturation != 1:
                rgb = ImageEnhance.Color(rgb).enhance(args.saturation)
            logical = rgb if palette_image is None else quantize_frame(rgb, palette_image, dither=args.dither, dither_strength=args.dither_strength)
            output = upscale(logical, size)
            output_path = directory / f"pixel-{index:06d}.png"
            output.save(output_path)
            output_paths.append(output_path)
        if args.contact_sheet:
            contact_sheet(output_paths, args.contact_sheet)
        if args.output.suffix.lower() == ".gif":
            encode_gif(args, directory)
            audio_kept = False
        elif args.output.suffix.lower() == ".mkv":
            audio_kept = encode_mkv(args, directory, source_audio=source.audio, duration=len(output_paths) / args.fps)
        else:
            audio_kept = encode_mp4(args, directory, source_audio=source.audio, duration=len(output_paths) / args.fps)
    return {
        "palette": [color_hex(color) for color in colors] if colors is not None else None,
        "alphaPreserved": False,
        "motion": {
            "fps": args.fps,
            "frameCount": len(output_paths),
            "durationSeconds": round(len(output_paths) / args.fps, 6),
            "sourceSelectionSeconds": duration,
            "startSeconds": args.start,
            "sourceAudio": source.audio,
            "audioKept": audio_kept,
            "loop": args.loop if args.output.suffix.lower() == ".gif" else None,
        },
    }


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="Local raster/SVG image, video, or animated raster")
    parser.add_argument("-o", "--output", type=Path, required=True, help="Exact .png, .webp, .mp4, .gif, or .mkv output path")
    parser.add_argument("--quality-profile", choices=tuple(PROFILES), default="balanced")
    parser.add_argument("--width", type=int, help="Output width; defaults to source width")
    parser.add_argument("--height", type=int, help="Output height; defaults to source aspect ratio")
    parser.add_argument("--pixel-size", type=int, help="Approximate output pixels per logical pixel")
    parser.add_argument("--palette", choices=("colorset1", "colorset2", "adaptive", "forest4", "sunset8", "custom", "preserve"), default="colorset1")
    parser.add_argument("--colorset", choices=("colorset1", "colorset2"), help="Active authored-paint contract; fixed legacy presets select colorset2")
    parser.add_argument("--color", type=parse_color, action="append", default=[], help="Repeat for custom palette entries")
    parser.add_argument("--colors", type=int, help="Adaptive palette color count")
    parser.add_argument("--dither", choices=("none", "bayer4", "floyd"), default="none")
    parser.add_argument("--dither-strength", type=float, default=0.5, help="Bayer perturbation strength")
    parser.add_argument("--contrast", type=float, help="Defaults to 1.08, or 1 in preserve mode")
    parser.add_argument("--saturation", type=float, help="Defaults to 1.10, or 1 in preserve mode")
    parser.add_argument("--background", type=parse_color, default=(255, 255, 255))
    parser.add_argument("--alpha", choices=("preserve", "flatten"), default="preserve", help="Static output only")
    parser.add_argument("--alpha-threshold", type=int, default=128, help="Static alpha cutoff at the logical-pixel grid")
    parser.add_argument("--fps", type=float, default=12.0, help="Animated output frame rate")
    parser.add_argument("--start", type=float, default=0.0, help="Start offset for video input")
    parser.add_argument("--duration", type=float, help="Selected video duration; defaults to remaining source")
    parser.add_argument("--max-frames", type=int, default=600)
    parser.add_argument("--audio", choices=("keep", "drop"), default="keep", help="MP4/MKV output only")
    parser.add_argument("--loop", type=int, default=0, help="GIF loop count; 0 means infinite")
    parser.add_argument("--contact-sheet", type=Path, help="Optional animation review PNG")
    parser.add_argument("--json-report", type=Path)
    parser.add_argument("--ffmpeg", default=shutil.which("ffmpeg"), help="ffmpeg executable")
    parser.add_argument("--ffprobe", default=shutil.which("ffprobe"), help="ffprobe executable")
    parser.add_argument("--timeout-ms", type=int, default=30000, help="SVG browser timeout")
    args = parser.parse_args(argv)
    inferred = "colorset2" if args.palette in {"colorset2", "forest4", "sunset8"} else "colorset1"
    if args.colorset and args.palette in {"colorset1", "colorset2", "forest4", "sunset8"} and args.colorset != inferred:
        parser.error("--colorset conflicts with the selected fixed palette")
    args.colorset = args.colorset or inferred
    if args.palette != "preserve":
        allowed = set(colorset_colors(args.colorset))
        if args.background not in allowed or any(color not in allowed for color in args.color):
            parser.error("Authored background/custom colors must belong to the active colorset")
    if not args.input.is_file():
        parser.error(f"Input not found: {args.input}")
    if args.output.suffix.lower() not in {".png", ".webp", ".mp4", ".gif", ".mkv"}:
        parser.error("--output must end in .png, .webp, .mp4, .gif, or .mkv")
    if args.output.resolve() == args.input.resolve():
        parser.error("--output must not overwrite the source")
    if args.contact_sheet and args.contact_sheet.suffix.lower() != ".png":
        parser.error("--contact-sheet must end in .png")
    if args.json_report and args.json_report.suffix.lower() != ".json":
        parser.error("--json-report must end in .json")
    paths = [path.resolve() for path in (args.output, args.contact_sheet, args.json_report) if path]
    if len(paths) != len(set(paths)) or args.input.resolve() in paths:
        parser.error("Output, contact sheet, and report paths must be distinct from one another and the input")
    if args.palette == "custom" and not 2 <= len(set(args.color)) <= 64:
        parser.error("custom palette requires 2–64 distinct --color values")
    if args.palette != "custom" and args.color:
        parser.error("--color is valid only with --palette custom")
    if args.palette != "adaptive" and args.colors is not None:
        parser.error("--colors is valid only with --palette adaptive")
    if args.palette == "preserve":
        if args.output.suffix.lower() not in {".png", ".webp", ".mkv"}:
            parser.error("--palette preserve requires lossless PNG/WebP stills or FFV1 MKV motion; MP4 and GIF change RGB colors")
        if args.dither != "none" or args.alpha == "flatten":
            parser.error("--palette preserve cannot dither or flatten alpha because those operations change source colors")
        if args.contrast not in (None, 1.0) or args.saturation not in (None, 1.0):
            parser.error("--palette preserve requires --contrast 1 and --saturation 1")
    args.contrast = 1.0 if args.palette == "preserve" else 1.08 if args.contrast is None else args.contrast
    args.saturation = 1.0 if args.palette == "preserve" else 1.10 if args.saturation is None else args.saturation
    default_pixel, default_colors = PROFILES[args.quality_profile]
    args.pixel_size = default_pixel if args.pixel_size is None else args.pixel_size
    args.colors = default_colors if args.colors is None else args.colors
    if not 1 <= args.pixel_size <= 32:
        parser.error("--pixel-size must be between 1 and 32")
    if not 2 <= args.colors <= 64:
        parser.error("--colors must be between 2 and 64")
    if not 0 <= args.dither_strength <= 2:
        parser.error("--dither-strength must be between 0 and 2")
    if not 0.25 <= args.contrast <= 3 or not 0 <= args.saturation <= 3:
        parser.error("--contrast must be 0.25–3 and --saturation must be 0–3")
    if not 0 <= args.alpha_threshold <= 255:
        parser.error("--alpha-threshold must be between 0 and 255")
    if not 1 <= args.fps <= 60:
        parser.error("--fps must be between 1 and 60")
    if args.start < 0 or (args.duration is not None and not 0.1 <= args.duration <= 120):
        parser.error("--start must be nonnegative and --duration must be 0.1–120 seconds")
    if not 2 <= args.max_frames <= 5000:
        parser.error("--max-frames must be between 2 and 5000")
    if not 0 <= args.loop <= 65535:
        parser.error("--loop must be between 0 and 65535")
    if not 1000 <= args.timeout_ms <= 120000:
        parser.error("--timeout-ms must be between 1000 and 120000")
    if args.output.suffix.lower() in {".mp4", ".gif", ".mkv"} and (not args.ffmpeg or not args.ffprobe):
        parser.error("ffmpeg and ffprobe are required for animated output")
    if args.output.suffix.lower() in {".png", ".webp"} and args.contact_sheet:
        parser.error("--contact-sheet is only for animated output")
    return args


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    motion = args.output.suffix.lower() in {".mp4", ".gif", ".mkv"}
    source = inspect_source(args.input, args.ffprobe, motion=motion)
    if motion and source.kind != "video":
        raise SystemExit("Animated output needs a video, GIF, APNG, or other decodable motion source")
    if source.kind == "video" and not args.ffmpeg:
        raise SystemExit("ffmpeg is required for a video source")
    size = resolve_dimensions(source, args.width, args.height, args.pixel_size)
    output_size = size[:2]
    logical_size = size[2:]
    result = convert_motion(args, source, output_size, logical_size) if motion else convert_still(args, source, output_size, logical_size)
    if not args.output.is_file() or args.output.stat().st_size == 0:
        raise SystemExit("Output was not created or is empty")
    report: dict[str, Any] = {
        "ok": True,
        "schema": "pixel-art-image-video/v1",
        "output": str(args.output.resolve()),
        "sha256": sha256_file(args.output),
        "source": {
            "path": str(args.input.resolve()),
            "sha256": sha256_file(args.input),
            "kind": source.kind,
            "format": source.format,
            "width": source.width,
            "height": source.height,
            "durationSeconds": source.duration,
            "audio": source.audio,
        },
        "render": {
            "width": output_size[0],
            "height": output_size[1],
            "logicalWidth": logical_size[0],
            "logicalHeight": logical_size[1],
            "pixelSize": args.pixel_size,
            "qualityProfile": args.quality_profile,
            "paletteMode": args.palette,
            "colorset": args.colorset if args.palette != "preserve" else None,
            "paintScope": "source-fidelity" if args.palette == "preserve" else "authored",
            "palette": result["palette"],
            "paletteSize": len(result["palette"]) if result["palette"] is not None else None,
            "sourceColorsExact": args.palette == "preserve",
            "sourceStartSeconds": args.start,
            "alphaThreshold": args.alpha_threshold,
            "dither": args.dither,
            "ditherStrength": args.dither_strength if args.dither == "bayer4" else None,
            "contrast": args.contrast,
            "saturation": args.saturation,
            "alphaPreserved": result["alphaPreserved"],
        },
        "motion": result["motion"],
        "contactSheet": str(args.contact_sheet.resolve()) if args.contact_sheet else None,
    }
    if args.json_report:
        write_json(args.json_report, report)
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
