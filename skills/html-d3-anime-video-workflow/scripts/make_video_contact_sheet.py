#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["pillow>=10.0.0"]
# ///

from __future__ import annotations

import argparse
import json
import math
import shutil
import statistics
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFont


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create a contact sheet from exact sampled MP4 frames without empty tile cells.")
    parser.add_argument("--video", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--manifest", type=Path)
    parser.add_argument("--samples", type=int, default=6)
    parser.add_argument("--columns", type=int, default=3)
    parser.add_argument("--thumb-width", type=int, default=426)
    parser.add_argument("--label-times", action="store_true")
    parser.add_argument("--background", default="#f6f8fb")
    parser.add_argument("--min-tile-color-buckets", type=int, default=0)
    parser.add_argument("--min-tile-nonbackground-ratio", type=float, default=0.0)
    parser.add_argument("--min-consecutive-change-ratio", type=float, default=0.0)
    parser.add_argument("--min-changing-pairs", type=int, default=0)
    parser.add_argument("--max-low-change-pairs", type=int)
    return parser.parse_args()


def run_command(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, text=True, capture_output=True, check=False)


def video_duration(video: Path) -> float:
    exe = shutil.which("ffprobe")
    if not exe:
        raise RuntimeError("ffprobe is required but was not found on PATH.")
    result = run_command(
        [
            exe,
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(video),
        ]
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "ffprobe failed.")
    return float(result.stdout.strip())


def sample_times(duration: float, samples: int) -> list[float]:
    if samples <= 0:
        raise ValueError("--samples must be positive")
    if samples == 1:
        return [0.0]
    # Include a near-final frame without sampling exact EOF; ffmpeg may return no frame at the tail.
    tail_guard = min(0.25, duration / max(samples * 4, 1))
    last_time = max(0.0, duration - tail_guard)
    return [last_time * index / (samples - 1) for index in range(samples)]


def extract_frame(video: Path, timestamp: float, output: Path, width: int) -> None:
    exe = shutil.which("ffmpeg")
    if not exe:
        raise RuntimeError("ffmpeg is required but was not found on PATH.")
    result = run_command(
        [
            exe,
            "-y",
            "-ss",
            f"{timestamp:.3f}",
            "-i",
            str(video),
            "-frames:v",
            "1",
            "-vf",
            f"scale={width}:-1",
            str(output),
        ]
    )
    if result.returncode != 0 or not output.exists():
        raise RuntimeError(result.stderr.strip() or f"Failed to extract frame at {timestamp:.3f}s.")


def parse_hex(value: str) -> tuple[int, int, int]:
    value = value.strip().lstrip("#")
    return int(value[0:2], 16), int(value[2:4], 16), int(value[4:6], 16)


def load_font(size: int) -> ImageFont.ImageFont:
    candidates = [
        Path("C:/Windows/Fonts/segoeui.ttf"),
        Path("C:/Windows/Fonts/arial.ttf"),
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
    ]
    for candidate in candidates:
        if candidate.exists():
            return ImageFont.truetype(str(candidate), size)
    return ImageFont.load_default()


def image_pixels(img: Image.Image):
    if hasattr(img, "get_flattened_data"):
        return img.get_flattened_data()
    return img.getdata()


def color_bucket_count(img: Image.Image) -> int:
    buckets: set[tuple[int, int, int]] = set()
    for r, g, b in image_pixels(img.convert("RGB")):
        buckets.add((r // 32, g // 32, b // 32))
    return len(buckets)


def nonbackground_ratio(img: Image.Image) -> float:
    rgb = img.convert("RGB")
    bg = rgb.getpixel((0, 0))
    threshold = 18
    changed = 0
    total = rgb.width * rgb.height
    for pixel in image_pixels(rgb):
        distance = abs(pixel[0] - bg[0]) + abs(pixel[1] - bg[1]) + abs(pixel[2] - bg[2])
        if distance > threshold:
            changed += 1
    return changed / total if total else 0.0


def changed_pixel_ratio(a: Image.Image, b: Image.Image) -> float:
    diff = ImageChops.difference(a.convert("RGB"), b.convert("RGB"))
    changed = 0
    total = diff.width * diff.height
    for r, g, b in image_pixels(diff):
        if r + g + b > 24:
            changed += 1
    return changed / total if total else 0.0


def analyze_frames(frame_paths: list[Path], min_consecutive_change_ratio: float) -> dict[str, object]:
    images = [Image.open(path).convert("RGB") for path in frame_paths]
    color_buckets = [color_bucket_count(img) for img in images]
    nonbackground = [nonbackground_ratio(img) for img in images]
    consecutive_change = [
        changed_pixel_ratio(a, b)
        for a, b in zip(images, images[1:])
    ]
    changing_pairs = [
        value
        for value in consecutive_change
        if value >= min_consecutive_change_ratio
    ]
    low_change_pairs = [
        value
        for value in consecutive_change
        if value < min_consecutive_change_ratio
    ]
    return {
        "tileColorBuckets": color_buckets,
        "minTileColorBuckets": min(color_buckets) if color_buckets else 0,
        "medianTileColorBuckets": statistics.median(color_buckets) if color_buckets else 0,
        "tileNonbackgroundRatios": nonbackground,
        "minTileNonbackgroundRatio": min(nonbackground) if nonbackground else 0.0,
        "medianTileNonbackgroundRatio": statistics.median(nonbackground) if nonbackground else 0.0,
        "consecutiveChangeRatios": consecutive_change,
        "changingPairs": len(changing_pairs),
        "lowChangePairs": len(low_change_pairs),
        "maxConsecutiveChangeRatio": max(consecutive_change, default=0.0),
        "minConsecutiveChangeRatio": min(consecutive_change, default=0.0),
    }


def build_sheet(frame_paths: list[Path], times: list[float], output: Path, columns: int, background: str, label_times: bool) -> dict[str, int]:
    if columns <= 0:
        raise ValueError("--columns must be positive")
    images = [Image.open(path).convert("RGB") for path in frame_paths]
    if not images:
        raise ValueError("No frames to compose.")
    thumb_w, thumb_h = images[0].size
    label_h = 24 if label_times else 0
    rows = math.ceil(len(images) / columns)
    sheet = Image.new("RGB", (columns * thumb_w, rows * (thumb_h + label_h)), parse_hex(background))
    draw = ImageDraw.Draw(sheet)
    font = load_font(14)
    for index, img in enumerate(images):
        col = index % columns
        row = index // columns
        x = col * thumb_w
        y = row * (thumb_h + label_h)
        sheet.paste(img, (x, y))
        if label_times:
            draw.rectangle((x, y + thumb_h, x + thumb_w, y + thumb_h + label_h), fill=(24, 32, 47))
            draw.text((x + 8, y + thumb_h + 5), f"{times[index]:.2f}s", fill=(255, 255, 255), font=font)
    output.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(output, quality=92)
    return {"width": sheet.width, "height": sheet.height, "rows": rows, "columns": columns, "tiles": len(images)}


def build_findings(sheet_info: dict[str, int], metrics: dict[str, object], args: argparse.Namespace, output_exists: bool) -> list[dict[str, object]]:
    findings: list[dict[str, object]] = []

    def add(code: str, message: str) -> None:
        findings.append({"code": code, "severity": "error", "message": message})

    if not output_exists:
        add("missing-output", f"Contact sheet was not created at {args.output}.")
    if sheet_info["tiles"] != args.samples:
        add("tile-count", f"Expected {args.samples} real sampled tiles, got {sheet_info['tiles']}.")
    if sheet_info["rows"] != math.ceil(args.samples / args.columns):
        add("sheet-geometry", "Contact sheet rows do not match the requested sample and column counts.")
    if args.min_tile_color_buckets and int(metrics["minTileColorBuckets"]) < args.min_tile_color_buckets:
        add(
            "tile-color-diversity",
            f"Expected every tile to have at least {args.min_tile_color_buckets} color buckets, got minimum {metrics['minTileColorBuckets']}.",
        )
    if args.min_tile_nonbackground_ratio and float(metrics["minTileNonbackgroundRatio"]) < args.min_tile_nonbackground_ratio:
        add(
            "tile-content",
            f"Expected every tile nonbackground ratio >= {args.min_tile_nonbackground_ratio}, got minimum {metrics['minTileNonbackgroundRatio']}.",
        )
    if args.min_changing_pairs and int(metrics["changingPairs"]) < args.min_changing_pairs:
        add(
            "contact-sheet-variation",
            f"Expected at least {args.min_changing_pairs} changing consecutive tile pairs, got {metrics['changingPairs']}.",
        )
    if args.max_low_change_pairs is not None and int(metrics["lowChangePairs"]) > args.max_low_change_pairs:
        add(
            "low-change-pairs",
            f"Expected at most {args.max_low_change_pairs} low-change consecutive tile pairs, got {metrics['lowChangePairs']}.",
        )
    return findings


def main() -> int:
    args = parse_args()
    if not args.video.exists():
        print(f"Missing video: {args.video}", file=sys.stderr)
        return 2
    duration = video_duration(args.video)
    times = sample_times(duration, args.samples)
    with tempfile.TemporaryDirectory(prefix="video-contact-sheet-") as temp:
        temp_dir = Path(temp)
        frame_paths = []
        for index, timestamp in enumerate(times):
            path = temp_dir / f"frame-{index:03d}.png"
            extract_frame(args.video, timestamp, path, args.thumb_width)
            frame_paths.append(path)
        metrics = analyze_frames(frame_paths, args.min_consecutive_change_ratio)
        sheet_info = build_sheet(frame_paths, times, args.output, args.columns, args.background, args.label_times)
    findings = build_findings(sheet_info, metrics, args, args.output.exists() and args.output.stat().st_size > 0)
    manifest = {
        "video": args.video.as_posix(),
        "output": args.output.as_posix(),
        "durationSeconds": duration,
        "sampleTimes": times,
        "samples": len(times),
        "sheet": sheet_info,
        "thresholds": {
            "minTileColorBuckets": args.min_tile_color_buckets,
            "minTileNonbackgroundRatio": args.min_tile_nonbackground_ratio,
            "minConsecutiveChangeRatio": args.min_consecutive_change_ratio,
            "minChangingPairs": args.min_changing_pairs,
            "maxLowChangePairs": args.max_low_change_pairs,
        },
        "metrics": metrics,
        "findings": findings,
        "passed": not findings,
    }
    if args.manifest:
        args.manifest.parent.mkdir(parents=True, exist_ok=True)
        args.manifest.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(json.dumps(manifest, indent=2))
    return 0 if manifest["passed"] else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"make_video_contact_sheet.py: {exc}", file=sys.stderr)
        raise SystemExit(2)
