#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "playwright>=1.49.0",
# ]
# ///

from __future__ import annotations

import argparse
import glob
import json
import math
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import sync_playwright


DEFAULT_OUTPUT_DIR = Path("projects/animated-svg-to-gif/artifacts/gifs")
DEFAULT_FPS = 24.0
DEFAULT_SCALE = 2.0
DEFAULT_MAX_WIDTH = 1280
DEFAULT_MAX_HEIGHT = 1280
DEFAULT_FALLBACK_DURATION = 4.0
DEFAULT_TAIL_PADDING = 0.35
DEFAULT_BACKGROUND = "#ffffff"
EXCLUDE_PARTS = {".git", "node_modules", "__pycache__", ".venv", "output"}


@dataclass
class SvgMetrics:
    width: int
    height: int
    viewbox_width: float
    viewbox_height: float
    inferred_duration: float


@dataclass
class ConversionResult:
    input: str
    output: str
    css_width: int
    css_height: int
    pixel_width: int
    pixel_height: int
    device_scale_factor: float
    fps: float
    duration_seconds: float
    frame_count: int
    colors: int
    dither: str
    manifest: str


def main() -> int:
    args = parse_args()
    ffmpeg = require_executable("ffmpeg")
    require_executable("ffprobe", required=False)

    inputs = discover_inputs(args.inputs, include_static=args.include_static)
    if not inputs:
        raise SystemExit("No SVG inputs were found.")
    if args.output and len(inputs) != 1:
        raise SystemExit("--output can only be used with exactly one input SVG.")

    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    results: list[ConversionResult] = []
    with sync_playwright() as playwright:
        browser = launch_browser(playwright, args)
        try:
            for source in inputs:
                result = convert_one(source.resolve(), output_dir, ffmpeg, browser, args)
                results.append(result)
        finally:
            browser.close()

    run_manifest = output_dir / "conversion-manifest.json"
    run_manifest.write_text(
        json.dumps(
            {
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "item_count": len(results),
                "items": [asdict(item) for item in results],
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print(f"Converted {len(results)} SVG file(s).")
    print(f"Manifest: {run_manifest}")
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Convert animated SVG files to high-quality GIFs using Chromium frame capture and ffmpeg palettes."
    )
    parser.add_argument("inputs", nargs="+", type=Path, help="SVG file(s), glob(s), or directories to convert.")
    parser.add_argument("-o", "--output", type=Path, help="GIF output path for a single input.")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR, help="Directory for batch GIF outputs.")
    parser.add_argument("--duration", type=float, help="Override animation duration in seconds.")
    parser.add_argument("--fallback-duration", type=float, default=DEFAULT_FALLBACK_DURATION)
    parser.add_argument("--tail-padding", type=float, default=DEFAULT_TAIL_PADDING)
    parser.add_argument("--fps", type=float, default=DEFAULT_FPS)
    parser.add_argument("--width", type=int, help="CSS pixel output width before device scaling.")
    parser.add_argument("--height", type=int, help="CSS pixel output height before device scaling.")
    parser.add_argument("--max-width", type=int, default=DEFAULT_MAX_WIDTH)
    parser.add_argument("--max-height", type=int, default=DEFAULT_MAX_HEIGHT)
    parser.add_argument("--scale", type=float, default=DEFAULT_SCALE, help="Browser device scale factor.")
    parser.add_argument("--background", default=DEFAULT_BACKGROUND)
    parser.add_argument("--colors", type=int, default=256)
    parser.add_argument("--stats-mode", default="full", choices=["full", "diff", "single"])
    parser.add_argument("--dither", default="sierra2_4a")
    parser.add_argument("--diff-mode", default="rectangle", choices=["rectangle", "none"])
    parser.add_argument("--loop", type=int, default=0, help="GIF loop count; 0 means infinite.")
    parser.add_argument("--include-static", action="store_true", help="Include SVGs that do not look animated.")
    parser.add_argument("--keep-frames", action="store_true", help="Keep captured PNG frames beside the GIF.")
    parser.add_argument("--install-browser", action="store_true", help="Install Playwright Chromium if launch fails.")
    parser.add_argument("--browser-channel", help="Use an installed browser channel such as chrome or msedge.")
    parser.add_argument("--browser-executable", type=Path, help="Path to a Chromium-compatible browser executable.")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    if args.fps <= 0:
        raise SystemExit("--fps must be greater than zero.")
    if args.scale <= 0:
        raise SystemExit("--scale must be greater than zero.")
    if args.duration is not None and args.duration <= 0:
        raise SystemExit("--duration must be greater than zero.")
    if args.colors < 2 or args.colors > 256:
        raise SystemExit("--colors must be between 2 and 256.")
    return args


def discover_inputs(raw_inputs: list[Path], include_static: bool) -> list[Path]:
    discovered: list[Path] = []
    for item in raw_inputs:
        matches: list[Path]
        item_text = str(item)
        explicit_file = not any(mark in item_text for mark in "*?[]") and not item.is_dir()
        if any(mark in item_text for mark in "*?[]"):
            matches = sorted(Path(match) for match in glob.glob(item_text, recursive=True))
        elif item.is_dir():
            matches = sorted(path for path in item.rglob("*.svg") if not is_excluded(path))
        else:
            matches = [item]

        for match in matches:
            if not match.exists() or not match.is_file():
                continue
            if match.suffix.lower() != ".svg":
                continue
            if include_static or looks_animated(match):
                discovered.append(match)
            elif explicit_file:
                print(f"Skipped static-looking SVG: {match} (pass --include-static to force conversion)")

    return sorted(dict.fromkeys(path.resolve() for path in discovered))


def is_excluded(path: Path) -> bool:
    return any(part in EXCLUDE_PARTS for part in path.parts)


def looks_animated(path: Path) -> bool:
    if path.name.lower().endswith(".animated.svg"):
        return True
    try:
        sample = path.read_text(encoding="utf-8", errors="ignore")[:250_000].lower()
    except OSError:
        return False
    return any(token in sample for token in ("@keyframes", "<animate", "animation:", "data-animated"))


def convert_one(source: Path, output_dir: Path, ffmpeg: str, browser: Any, args: argparse.Namespace) -> ConversionResult:
    svg_text = source.read_text(encoding="utf-8")
    metrics = inspect_svg(svg_text, args)
    output_path = args.output.resolve() if args.output else output_dir / f"{safe_stem(source)}.gif"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    duration = args.duration if args.duration is not None else metrics.inferred_duration
    frame_count = max(2, int(math.ceil(duration * args.fps)))

    keep_dir = output_path.with_suffix(".frames")
    frame_dir_obj: tempfile.TemporaryDirectory[str] | None = None
    if args.keep_frames:
        if keep_dir.exists():
            shutil.rmtree(keep_dir)
        frame_dir = keep_dir
        frame_dir.mkdir(parents=True)
    else:
        frame_dir_obj = tempfile.TemporaryDirectory(prefix=f"{output_path.stem}-frames-", dir=output_path.parent)
        frame_dir = Path(frame_dir_obj.name)

    try:
        capture_frames(source, svg_text, frame_dir, metrics, duration, frame_count, browser, args)
        encode_gif(frame_dir, output_path, ffmpeg, args)
    finally:
        if frame_dir_obj is not None:
            frame_dir_obj.cleanup()

    item_manifest = output_path.with_suffix(".manifest.json")
    result = ConversionResult(
        input=str(source),
        output=str(output_path),
        css_width=metrics.width,
        css_height=metrics.height,
        pixel_width=int(round(metrics.width * args.scale)),
        pixel_height=int(round(metrics.height * args.scale)),
        device_scale_factor=args.scale,
        fps=args.fps,
        duration_seconds=duration,
        frame_count=frame_count,
        colors=args.colors,
        dither=args.dither,
        manifest=str(item_manifest),
    )
    item_manifest.write_text(json.dumps(asdict(result), indent=2) + "\n", encoding="utf-8")
    print(
        f"Converted: {source} -> {output_path} "
        f"(css {metrics.width}x{metrics.height}, output {result.pixel_width}x{result.pixel_height}, {frame_count} frames)"
    )
    return result


def inspect_svg(svg_text: str, args: argparse.Namespace) -> SvgMetrics:
    viewbox_width, viewbox_height = parse_viewbox(svg_text)
    if viewbox_width <= 0 or viewbox_height <= 0:
        parsed_width, parsed_height = parse_svg_size(svg_text)
        viewbox_width = parsed_width or 800.0
        viewbox_height = parsed_height or 600.0

    width, height = fit_dimensions(viewbox_width, viewbox_height, args)
    duration = infer_duration(svg_text, args)
    return SvgMetrics(
        width=width,
        height=height,
        viewbox_width=viewbox_width,
        viewbox_height=viewbox_height,
        inferred_duration=duration,
    )


def parse_viewbox(svg_text: str) -> tuple[float, float]:
    match = re.search(r"\bviewBox\s*=\s*['\"]([^'\"]+)['\"]", svg_text, re.IGNORECASE)
    if not match:
        return 0.0, 0.0
    numbers = re.findall(r"[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?", match.group(1))
    if len(numbers) != 4:
        return 0.0, 0.0
    return abs(float(numbers[2])), abs(float(numbers[3]))


def parse_svg_size(svg_text: str) -> tuple[float | None, float | None]:
    root = re.search(r"<svg\b([^>]*)>", svg_text, re.IGNORECASE | re.DOTALL)
    if not root:
        return None, None
    attrs = root.group(1)
    return parse_length_attr(attrs, "width"), parse_length_attr(attrs, "height")


def parse_length_attr(attrs: str, name: str) -> float | None:
    match = re.search(rf"\b{name}\s*=\s*['\"]([^'\"]+)['\"]", attrs, re.IGNORECASE)
    if not match:
        return None
    length = re.match(r"\s*([-+]?\d*\.?\d+)", match.group(1))
    if not length:
        return None
    return float(length.group(1))


def fit_dimensions(viewbox_width: float, viewbox_height: float, args: argparse.Namespace) -> tuple[int, int]:
    ratio = viewbox_height / viewbox_width if viewbox_width else 1.0
    if args.width and args.height:
        width, height = args.width, args.height
    elif args.width:
        width, height = args.width, int(round(args.width * ratio))
    elif args.height:
        width, height = int(round(args.height / ratio)), args.height
    else:
        width, height = int(round(viewbox_width)), int(round(viewbox_height))
        limits = []
        if args.max_width and width > args.max_width:
            limits.append(args.max_width / width)
        if args.max_height and height > args.max_height:
            limits.append(args.max_height / height)
        if limits:
            scale = min(limits)
            width = int(round(width * scale))
            height = int(round(height * scale))
    return max(1, width), max(1, height)


def infer_duration(svg_text: str, args: argparse.Namespace) -> float:
    if args.duration is not None:
        return args.duration

    candidates: list[float] = []
    for style in re.findall(r"\bstyle\s*=\s*(['\"])(.*?)\1", svg_text, re.IGNORECASE | re.DOTALL):
        style_text = style[1]
        delay = css_time(style_text, "--am-delay") or css_time(style_text, "animation-delay") or 0.0
        duration = css_time(style_text, "--am-duration") or css_time(style_text, "animation-duration")
        if duration:
            candidates.append(delay + duration)

    for tag in re.findall(r"<animate(?:Transform|Motion)?\b[^>]*>", svg_text, re.IGNORECASE):
        duration = attr_time(tag, "dur")
        begin = attr_time(tag, "begin") or 0.0
        if duration:
            candidates.append(begin + duration)

    if candidates:
        inferred = max(candidates) + max(0.0, args.tail_padding)
    else:
        inferred = args.fallback_duration
    return max(0.1, inferred)


def css_time(style_text: str, property_name: str) -> float | None:
    match = re.search(
        rf"{re.escape(property_name)}\s*:\s*([-+]?\d*\.?\d+)\s*(ms|s)\b",
        style_text,
        re.IGNORECASE,
    )
    if not match:
        return None
    return to_seconds(float(match.group(1)), match.group(2))


def attr_time(tag: str, attr_name: str) -> float | None:
    match = re.search(rf"\b{attr_name}\s*=\s*['\"]([^'\"]+)['\"]", tag, re.IGNORECASE)
    if not match:
        return None
    time_match = re.search(r"([-+]?\d*\.?\d+)\s*(ms|s)\b", match.group(1), re.IGNORECASE)
    if not time_match:
        return None
    return to_seconds(float(time_match.group(1)), time_match.group(2))


def to_seconds(value: float, unit: str) -> float:
    return value / 1000.0 if unit.lower() == "ms" else value


def capture_frames(
    source: Path,
    svg_text: str,
    frame_dir: Path,
    metrics: SvgMetrics,
    duration: float,
    frame_count: int,
    browser: Any,
    args: argparse.Namespace,
) -> None:
    context = browser.new_context(
        viewport={"width": metrics.width, "height": metrics.height},
        device_scale_factor=args.scale,
        locale="en-US",
    )
    page = context.new_page()
    try:
        page.set_content(build_html(source, svg_text, metrics, args), wait_until="load")
        page.locator("#stage svg").wait_for(state="attached", timeout=10_000)
        page.evaluate("() => document.fonts ? document.fonts.ready : Promise.resolve()")

        for index in range(frame_count):
            seconds = min(index / args.fps, duration)
            page.evaluate(
                """async (seconds) => {
                    const svg = document.querySelector('#stage svg');
                    if (svg && typeof svg.pauseAnimations === 'function') {
                      svg.pauseAnimations();
                    }
                    if (svg && typeof svg.setCurrentTime === 'function') {
                      try { svg.setCurrentTime(seconds); } catch (error) {}
                    }
                    const animations = document.getAnimations ? document.getAnimations() : [];
                    for (const animation of animations) {
                      try {
                        animation.pause();
                        animation.currentTime = seconds * 1000;
                      } catch (error) {}
                    }
                    await new Promise((resolve) => requestAnimationFrame(resolve));
                    await new Promise((resolve) => requestAnimationFrame(resolve));
                }""",
                seconds,
            )
            frame_path = frame_dir / f"frame_{index:05d}.png"
            page.locator("#stage").screenshot(path=str(frame_path))
            if args.verbose and (index == 0 or index == frame_count - 1 or index % 24 == 0):
                print(f"  captured frame {index + 1}/{frame_count}")
    finally:
        context.close()


def build_html(source: Path, svg_text: str, metrics: SvgMetrics, args: argparse.Namespace) -> str:
    cleaned_svg = clean_svg_for_inline_html(svg_text)
    base_href = source.parent.resolve().as_uri() + "/"
    return f"""<!doctype html>
<html>
<head>
<meta charset="utf-8">
<base href="{base_href}">
<style>
html, body {{
  width: {metrics.width}px;
  height: {metrics.height}px;
  margin: 0;
  padding: 0;
  overflow: hidden;
  background: {args.background};
}}
#stage {{
  width: {metrics.width}px;
  height: {metrics.height}px;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  background: {args.background};
}}
#stage > svg {{
  width: 100% !important;
  height: 100% !important;
  max-width: none !important;
  display: block;
  background: {args.background};
  text-rendering: geometricPrecision;
}}
</style>
</head>
<body>
<div id="stage">{cleaned_svg}</div>
</body>
</html>"""


def clean_svg_for_inline_html(svg_text: str) -> str:
    cleaned = re.sub(r"^\s*<\?xml[^>]*>\s*", "", svg_text, flags=re.IGNORECASE)
    cleaned = re.sub(r"^\s*<!DOCTYPE[^>]*>\s*", "", cleaned, flags=re.IGNORECASE | re.DOTALL)
    return cleaned.strip()


def encode_gif(frame_dir: Path, output_path: Path, ffmpeg: str, args: argparse.Namespace) -> None:
    pattern = str((frame_dir / "frame_%05d.png").resolve())
    palette = frame_dir / "palette.png"
    palette_filter = f"palettegen=max_colors={args.colors}:stats_mode={args.stats_mode}"
    paletteuse_filter = f"paletteuse=dither={args.dither}:diff_mode={args.diff_mode}"

    run_command(
        [
            ffmpeg,
            "-y",
            "-hide_banner",
            "-loglevel",
            "error",
            "-framerate",
            format_float(args.fps),
            "-i",
            pattern,
            "-vf",
            palette_filter,
            str(palette.resolve()),
        ]
    )
    run_command(
        [
            ffmpeg,
            "-y",
            "-hide_banner",
            "-loglevel",
            "error",
            "-framerate",
            format_float(args.fps),
            "-i",
            pattern,
            "-i",
            str(palette.resolve()),
            "-lavfi",
            paletteuse_filter,
            "-loop",
            str(args.loop),
            str(output_path.resolve()),
        ]
    )


def launch_browser(playwright: Any, args: argparse.Namespace) -> Any:
    launch_options: dict[str, Any] = {"headless": True}
    if args.browser_channel:
        launch_options["channel"] = args.browser_channel
    if args.browser_executable:
        launch_options["executable_path"] = str(args.browser_executable.resolve())

    try:
        return playwright.chromium.launch(**launch_options)
    except PlaywrightError as error:
        if args.install_browser and not args.browser_channel and not args.browser_executable:
            print("Installing Playwright Chromium browser...")
            run_command([sys.executable, "-m", "playwright", "install", "chromium"])
            return playwright.chromium.launch(**launch_options)
        message = (
            "Could not launch Chromium. Re-run with --install-browser, or pass "
            "--browser-channel chrome/msedge or --browser-executable."
        )
        raise SystemExit(f"{message}\nOriginal error: {error}") from error


def require_executable(name: str, required: bool = True) -> str:
    found = shutil.which(name)
    if found:
        return found
    if required:
        raise SystemExit(f"Required executable not found on PATH: {name}")
    return name


def run_command(command: list[str]) -> None:
    completed = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    if completed.returncode != 0:
        raise SystemExit(f"Command failed ({completed.returncode}): {' '.join(command)}\n{completed.stdout}")


def safe_stem(path: Path) -> str:
    name = path.name
    if name.lower().endswith(".animated.svg"):
        name = name[: -len(".animated.svg")]
    else:
        name = path.stem
    safe = re.sub(r"[^a-zA-Z0-9._-]+", "-", name).strip("-")
    return safe or "animated-svg"


def format_float(value: float) -> str:
    return f"{value:g}"


if __name__ == "__main__":
    raise SystemExit(main())
