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
from collections import deque
from pathlib import Path
from typing import Any

from PIL import Image


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Audit encoded Metro MP4 frames for distributed visual composition, "
            "low text-like pressure, strong opening density, and spatial state change."
        )
    )
    parser.add_argument("--video", required=True, type=Path)
    parser.add_argument("--report", required=True, type=Path)
    parser.add_argument("--samples", type=int, default=6)
    parser.add_argument("--scale-width", type=int, default=426)
    parser.add_argument("--grid-columns", type=int, default=8)
    parser.add_argument("--grid-rows", type=int, default=4)
    parser.add_argument("--min-grid-coverage", type=float, default=0.62)
    parser.add_argument("--min-median-grid-coverage", type=float, default=0.72)
    parser.add_argument("--min-quadrants-with-content", type=int, default=4)
    parser.add_argument("--min-opening-grid-coverage-ratio", type=float, default=0.65)
    parser.add_argument("--min-spatial-change-pairs", type=int, default=3)
    parser.add_argument("--min-cell-change-count", type=int, default=8)
    parser.add_argument("--min-cell-change-mean", type=float, default=0.045)
    parser.add_argument("--max-title-band-dominance", type=float, default=3.0)
    parser.add_argument("--max-text-like-component-area-ratio", type=float, default=0.12)
    parser.add_argument("--max-red-area-ratio", type=float, default=0.14)
    return parser.parse_args()


def thresholds(args: argparse.Namespace) -> dict[str, Any]:
    return {
        "minGridCoverage": args.min_grid_coverage,
        "minMedianGridCoverage": args.min_median_grid_coverage,
        "minQuadrantsWithContent": args.min_quadrants_with_content,
        "minOpeningGridCoverageRatio": args.min_opening_grid_coverage_ratio,
        "minSpatialChangePairs": args.min_spatial_change_pairs,
        "minCellChangeCount": args.min_cell_change_count,
        "minCellChangeMean": args.min_cell_change_mean,
        "maxTitleBandDominance": args.max_title_band_dominance,
        "maxTextLikeComponentAreaRatio": args.max_text_like_component_area_ratio,
        "maxRedAreaRatio": args.max_red_area_ratio,
    }


def write_failure_report(args: argparse.Namespace, code: str, message: str) -> None:
    report = {
        "video": args.video.as_posix(),
        "durationSeconds": None,
        "sampleTimes": [],
        "samples": 0,
        "thresholds": thresholds(args),
        "frames": [],
        "spatialChanges": [],
        "summary": {
            "minGridCoverage": 0.0,
            "medianGridCoverage": 0.0,
            "minQuadrantsWithContent": 0,
            "openingGridCoverageRatio": 0.0,
            "spatialChangingPairs": 0,
            "maxTitleBandDominance": 0.0,
            "maxTextLikeComponentAreaRatio": 0.0,
            "maxRedAreaRatio": 0.0,
            "medianRedAreaRatio": 0.0,
            "maxMeanCellChange": 0.0,
            "maxChangedCells": 0,
        },
        "findings": [{"code": code, "severity": "error", "message": message}],
        "passed": False,
    }
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2), encoding="utf-8")


def run_command(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, text=True, capture_output=True, check=False)


def require_tool(name: str) -> str:
    exe = shutil.which(name)
    if not exe:
        raise RuntimeError(f"{name} is required but was not found on PATH.")
    return exe


def video_duration(video: Path) -> float:
    ffprobe = require_tool("ffprobe")
    result = run_command(
        [
            ffprobe,
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
    tail_guard = min(0.25, duration / max(samples * 4, 1))
    last_time = max(0.0, duration - tail_guard)
    return [last_time * index / (samples - 1) for index in range(samples)]


def extract_frame(video: Path, timestamp: float, output: Path, width: int) -> None:
    ffmpeg = require_tool("ffmpeg")
    result = run_command(
        [
            ffmpeg,
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


def image_pixels(img: Image.Image):
    if hasattr(img, "get_flattened_data"):
        return img.get_flattened_data()
    return img.getdata()


def background_color(img: Image.Image) -> tuple[int, int, int]:
    rgb = img.convert("RGB")
    w, h = rgb.size
    samples = [
        rgb.getpixel((0, 0)),
        rgb.getpixel((w - 1, 0)),
        rgb.getpixel((0, h - 1)),
        rgb.getpixel((w - 1, h - 1)),
    ]
    return tuple(int(statistics.median(pixel[channel] for pixel in samples)) for channel in range(3))


def content_mask(img: Image.Image, bg: tuple[int, int, int]) -> list[bool]:
    mask: list[bool] = []
    for pixel in image_pixels(img.convert("RGB")):
        distance = abs(pixel[0] - bg[0]) + abs(pixel[1] - bg[1]) + abs(pixel[2] - bg[2])
        mask.append(distance > 18)
    return mask


def dark_mask(img: Image.Image, bg: tuple[int, int, int]) -> list[bool]:
    bg_luminance = sum(bg) / 3
    mask: list[bool] = []
    for r, g, b in image_pixels(img.convert("RGB")):
        luminance = (r + g + b) / 3
        brand_red_or_dark = r > 120 and g < 95 and b < 125
        mask.append(luminance < bg_luminance - 45 or brand_red_or_dark)
    return mask


def grid_scores(mask: list[bool], width: int, height: int, columns: int, rows: int) -> list[float]:
    scores: list[float] = []
    for row in range(rows):
        for col in range(columns):
            x0 = width * col // columns
            x1 = width * (col + 1) // columns
            y0 = height * row // rows
            y1 = height * (row + 1) // rows
            count = 0
            total = max(1, (x1 - x0) * (y1 - y0))
            for y in range(y0, y1):
                base = y * width
                for x in range(x0, x1):
                    count += 1 if mask[base + x] else 0
            scores.append(count / total)
    return scores


def quadrant_scores(grid: list[float], columns: int, rows: int) -> list[float]:
    values: list[float] = []
    half_columns = columns // 2
    half_rows = rows // 2
    for qy in range(2):
        for qx in range(2):
            cells: list[float] = []
            for row in range(qy * half_rows, (qy + 1) * half_rows):
                for col in range(qx * half_columns, (qx + 1) * half_columns):
                    cells.append(grid[row * columns + col])
            values.append(sum(cells) / len(cells) if cells else 0.0)
    return values


def band_ratio(mask: list[bool], width: int, height: int, start: int, stop: int) -> float:
    y0 = max(0, min(height, start))
    y1 = max(0, min(height, stop))
    if y1 <= y0:
        return 0.0
    count = 0
    for y in range(y0, y1):
        base = y * width
        for x in range(width):
            count += 1 if mask[base + x] else 0
    return count / ((y1 - y0) * width)


def small_dark_component_area_ratio(dark: list[bool], content: list[bool], width: int, height: int) -> float:
    seen = [False] * len(dark)
    small_area = 0
    content_area = max(1, sum(1 for value in content if value))
    for start, value in enumerate(dark):
        if not value or seen[start]:
            continue
        queue: deque[int] = deque([start])
        seen[start] = True
        area = 0
        min_x = width
        max_x = 0
        min_y = height
        max_y = 0
        while queue:
            index = queue.popleft()
            x = index % width
            y = index // width
            area += 1
            min_x = min(min_x, x)
            max_x = max(max_x, x)
            min_y = min(min_y, y)
            max_y = max(max_y, y)
            for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                if 0 <= nx < width and 0 <= ny < height:
                    next_index = ny * width + nx
                    if dark[next_index] and not seen[next_index]:
                        seen[next_index] = True
                        queue.append(next_index)
        box_w = max_x - min_x + 1
        box_h = max_y - min_y + 1
        if 3 <= area <= 260 and box_w <= 72 and box_h <= 28:
            small_area += area
    return small_area / content_area


def is_red_family(pixel: tuple[int, int, int]) -> bool:
    r, g, b = pixel
    saturated_red = r >= 120 and g <= 115 and b <= 135 and r - max(g, b) >= 32
    pale_red = r >= 215 and 145 <= g <= 225 and 150 <= b <= 230 and r - g >= 24 and r - b >= 12
    return saturated_red or pale_red


def red_area_ratio(img: Image.Image) -> float:
    rgb = img.convert("RGB")
    pixels = list(image_pixels(rgb))
    if not pixels:
        return 0.0
    red_pixels = sum(1 for pixel in pixels if is_red_family(pixel))
    return red_pixels / len(pixels)


def frame_metrics(path: Path, args: argparse.Namespace) -> dict[str, Any]:
    img = Image.open(path).convert("RGB")
    width, height = img.size
    bg = background_color(img)
    content = content_mask(img, bg)
    dark = dark_mask(img, bg)
    grid = grid_scores(content, width, height, args.grid_columns, args.grid_rows)
    occupied_cells = sum(1 for score in grid if score >= 0.025)
    coverage = occupied_cells / max(1, args.grid_columns * args.grid_rows)
    quadrants = quadrant_scores(grid, args.grid_columns, args.grid_rows)
    quadrant_count = sum(1 for score in quadrants if score >= 0.04)
    top = band_ratio(content, width, height, 0, height // 6)
    bottom = band_ratio(content, width, height, height - height // 6, height)
    middle = band_ratio(content, width, height, height // 3, (2 * height) // 3)
    total = sum(1 for value in content if value) / max(1, width * height)
    band_dominance = max(top, bottom) / max(total, 0.0001)
    return {
        "width": width,
        "height": height,
        "background": bg,
        "gridScores": grid,
        "gridCoverage": coverage,
        "occupiedCells": occupied_cells,
        "quadrantScores": quadrants,
        "quadrantsWithContent": quadrant_count,
        "nonbackgroundRatio": total,
        "topBandRatio": top,
        "bottomBandRatio": bottom,
        "middleBandRatio": middle,
        "titleBandDominance": band_dominance,
        "textLikeComponentAreaRatio": small_dark_component_area_ratio(dark, content, width, height),
        "redAreaRatio": red_area_ratio(img),
    }


def spatial_changes(frames: list[dict[str, Any]], args: argparse.Namespace) -> list[dict[str, Any]]:
    changes: list[dict[str, Any]] = []
    for before, after in zip(frames, frames[1:]):
        before_grid = before["gridScores"]
        after_grid = after["gridScores"]
        cell_diffs = [abs(float(a) - float(b)) for a, b in zip(before_grid, after_grid)]
        changes.append(
            {
                "meanCellChange": sum(cell_diffs) / len(cell_diffs) if cell_diffs else 0.0,
                "changedCells": sum(1 for value in cell_diffs if value >= args.min_cell_change_mean),
            }
        )
    return changes


def build_findings(report: dict[str, Any], args: argparse.Namespace) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []

    def add(code: str, message: str, **extra: Any) -> None:
        findings.append({"code": code, "severity": "error", "message": message, **extra})

    summary = report["summary"]
    if summary["minGridCoverage"] < args.min_grid_coverage:
        add(
            "contact-sheet-slide-like-composition",
            "Encoded MP4 frames do not occupy enough of the modular grid to read as a Metro megacanvas.",
            actualGridCoverage=summary["minGridCoverage"],
        )
        add(
            "mp4-weak-grid-coverage",
            f"Expected every sampled frame grid coverage >= {args.min_grid_coverage}.",
            actual=summary["minGridCoverage"],
        )
    if summary["medianGridCoverage"] < args.min_median_grid_coverage:
        add(
            "mp4-weak-median-grid-coverage",
            f"Expected median sampled frame grid coverage >= {args.min_median_grid_coverage}.",
            actual=summary["medianGridCoverage"],
        )
    if summary["minQuadrantsWithContent"] < args.min_quadrants_with_content:
        add(
            "contact-sheet-slide-like-composition",
            "Encoded MP4 frames do not distribute meaningful content across the frame quadrants.",
            actualQuadrants=summary["minQuadrantsWithContent"],
        )
        add(
            "mp4-weak-quadrant-coverage",
            f"Expected every sampled frame to occupy at least {args.min_quadrants_with_content} quadrants.",
            actual=summary["minQuadrantsWithContent"],
        )
    if summary["openingGridCoverageRatio"] < args.min_opening_grid_coverage_ratio:
        add(
            "mp4-weak-opening-composition",
            f"Expected opening grid coverage ratio >= {args.min_opening_grid_coverage_ratio}.",
            actual=summary["openingGridCoverageRatio"],
        )
    if summary["spatialChangingPairs"] < args.min_spatial_change_pairs:
        add(
            "contact-sheet-slide-like-composition",
            "Encoded MP4 frames do not show enough distributed spatial progression between sampled tiles.",
            actualSpatialChangingPairs=summary["spatialChangingPairs"],
        )
        add(
            "mp4-weak-spatial-progression",
            f"Expected at least {args.min_spatial_change_pairs} adjacent pairs with distributed cell changes.",
            actual=summary["spatialChangingPairs"],
        )
    if summary["maxTitleBandDominance"] > args.max_title_band_dominance:
        add(
            "contact-sheet-slide-like-composition",
            "Encoded MP4 frames concentrate too much content in a title/caption band.",
            actualTitleBandDominance=summary["maxTitleBandDominance"],
        )
        add(
            "mp4-title-band-dominance",
            f"Expected title/caption band dominance <= {args.max_title_band_dominance}.",
            actual=summary["maxTitleBandDominance"],
        )
    if summary["maxTextLikeComponentAreaRatio"] > args.max_text_like_component_area_ratio:
        add(
            "mp4-text-like-component-pressure",
            f"Expected text-like small component area ratio <= {args.max_text_like_component_area_ratio}.",
            actual=summary["maxTextLikeComponentAreaRatio"],
        )
    if summary["maxRedAreaRatio"] > args.max_red_area_ratio:
        add(
            "mp4-red-area-too-dominant",
            f"Expected red-family pixel area ratio <= {args.max_red_area_ratio}.",
            actual=summary["maxRedAreaRatio"],
        )
    return findings


def summarize(frames: list[dict[str, Any]], changes: list[dict[str, Any]], args: argparse.Namespace) -> dict[str, Any]:
    grid_coverages = [float(item["gridCoverage"]) for item in frames]
    quadrants = [int(item["quadrantsWithContent"]) for item in frames]
    title_bands = [float(item["titleBandDominance"]) for item in frames]
    text_pressure = [float(item["textLikeComponentAreaRatio"]) for item in frames]
    red_area = [float(item["redAreaRatio"]) for item in frames]
    spatial_changing = [
        item
        for item in changes
        if item["changedCells"] >= args.min_cell_change_count and item["meanCellChange"] >= args.min_cell_change_mean
    ]
    opening_ratio = grid_coverages[0] / max(statistics.median(grid_coverages), 0.0001) if grid_coverages else 0.0
    return {
        "minGridCoverage": min(grid_coverages, default=0.0),
        "medianGridCoverage": statistics.median(grid_coverages) if grid_coverages else 0.0,
        "minQuadrantsWithContent": min(quadrants, default=0),
        "openingGridCoverageRatio": opening_ratio,
        "spatialChangingPairs": len(spatial_changing),
        "maxTitleBandDominance": max(title_bands, default=0.0),
        "maxTextLikeComponentAreaRatio": max(text_pressure, default=0.0),
        "maxRedAreaRatio": max(red_area, default=0.0),
        "medianRedAreaRatio": statistics.median(red_area) if red_area else 0.0,
        "maxMeanCellChange": max((float(item["meanCellChange"]) for item in changes), default=0.0),
        "maxChangedCells": max((int(item["changedCells"]) for item in changes), default=0),
    }


def main() -> int:
    args = parse_args()
    try:
        if not args.video.exists():
            message = f"Missing video: {args.video}"
            print(message, file=sys.stderr)
            write_failure_report(args, "mp4-missing-video", message)
            print(json.dumps({"report": args.report.as_posix(), "passed": False}, indent=2))
            return 2
        duration = video_duration(args.video)
        times = sample_times(duration, args.samples)
        with tempfile.TemporaryDirectory(prefix="metro-video-composition-") as temp:
            temp_dir = Path(temp)
            frame_paths: list[Path] = []
            for index, timestamp in enumerate(times):
                path = temp_dir / f"frame-{index:03d}.png"
                extract_frame(args.video, timestamp, path, args.scale_width)
                frame_paths.append(path)
            frames = [frame_metrics(path, args) for path in frame_paths]
    except Exception as exc:
        message = str(exc)
        print(f"audit_metro_video_composition.py: {message}", file=sys.stderr)
        write_failure_report(args, "mp4-composition-audit-error", message)
        print(json.dumps({"report": args.report.as_posix(), "passed": False}, indent=2))
        return 2
    changes = spatial_changes(frames, args)
    report: dict[str, Any] = {
        "video": args.video.as_posix(),
        "durationSeconds": duration,
        "sampleTimes": times,
        "samples": len(times),
        "thresholds": thresholds(args),
        "frames": frames,
        "spatialChanges": changes,
    }
    report["summary"] = summarize(frames, changes, args)
    report["findings"] = build_findings(report, args)
    report["passed"] = not report["findings"]
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({"report": args.report.as_posix(), "passed": report["passed"]}, indent=2))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
