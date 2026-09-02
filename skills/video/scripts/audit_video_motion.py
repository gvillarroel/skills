#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["pillow>=10.0.0"]
# ///

from __future__ import annotations

import argparse
import json
import shutil
import statistics
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image, ImageChops, ImageStat


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit sampled video frames for nonblank content, color diversity, and visible motion.")
    parser.add_argument("--video", required=True, type=Path)
    parser.add_argument("--report", required=True, type=Path)
    parser.add_argument("--sample-fps", type=float, default=1.0)
    parser.add_argument("--scale-width", type=int, default=320)
    parser.add_argument("--min-samples", type=int, default=4)
    parser.add_argument("--min-color-buckets", type=int, default=12)
    parser.add_argument("--min-nonbackground-ratio", type=float, default=0.015)
    parser.add_argument("--min-changing-pairs", type=int, default=2)
    parser.add_argument("--min-changed-pixel-ratio", type=float, default=0.002)
    parser.add_argument("--min-mean-absolute-diff", type=float, default=0.25)
    return parser.parse_args()


def run_ffmpeg_extract(video: Path, frame_dir: Path, sample_fps: float, scale_width: int) -> None:
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        raise RuntimeError("ffmpeg is required but was not found on PATH.")
    frame_dir.mkdir(parents=True, exist_ok=True)
    vf = f"fps={sample_fps},scale={scale_width}:-1"
    result = subprocess.run(
        [
            ffmpeg,
            "-y",
            "-i",
            str(video),
            "-vf",
            vf,
            str(frame_dir / "sample-%04d.png"),
        ],
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "ffmpeg frame extraction failed.")


def color_bucket_count(img: Image.Image) -> int:
    rgb = img.convert("RGB")
    buckets: set[tuple[int, int, int]] = set()
    for r, g, b in image_pixels(rgb):
        buckets.add((r // 32, g // 32, b // 32))
    return len(buckets)


def image_pixels(img: Image.Image):
    if hasattr(img, "get_flattened_data"):
        return img.get_flattened_data()
    return img.getdata()


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


def frame_diff(a: Image.Image, b: Image.Image, changed_threshold: int) -> dict[str, float]:
    a_rgb = a.convert("RGB")
    b_rgb = b.convert("RGB")
    diff = ImageChops.difference(a_rgb, b_rgb)
    stat = ImageStat.Stat(diff)
    mean_abs = sum(stat.mean) / len(stat.mean)
    changed = 0
    total = diff.width * diff.height
    for r, g, b in image_pixels(diff):
        if r + g + b > changed_threshold:
            changed += 1
    return {
        "meanAbsoluteDiff": mean_abs,
        "changedPixelRatio": changed / total if total else 0.0,
    }


def collect_metrics(frame_dir: Path, args: argparse.Namespace) -> dict[str, object]:
    frames = sorted(frame_dir.glob("sample-*.png"))
    images = [Image.open(path).convert("RGB") for path in frames]
    color_counts = [color_bucket_count(img) for img in images]
    nonbg = [nonbackground_ratio(img) for img in images]
    diffs = [
        frame_diff(a, b, changed_threshold=18)
        for a, b in zip(images, images[1:])
    ]
    changing_pairs = [
        item
        for item in diffs
        if item["changedPixelRatio"] >= args.min_changed_pixel_ratio
        and item["meanAbsoluteDiff"] >= args.min_mean_absolute_diff
    ]
    return {
        "sampleCount": len(frames),
        "frameFiles": [path.name for path in frames],
        "maxColorBuckets": max(color_counts) if color_counts else 0,
        "medianColorBuckets": statistics.median(color_counts) if color_counts else 0,
        "medianNonbackgroundRatio": statistics.median(nonbg) if nonbg else 0.0,
        "maxNonbackgroundRatio": max(nonbg) if nonbg else 0.0,
        "diffs": diffs,
        "changingPairs": len(changing_pairs),
        "maxChangedPixelRatio": max((item["changedPixelRatio"] for item in diffs), default=0.0),
        "maxMeanAbsoluteDiff": max((item["meanAbsoluteDiff"] for item in diffs), default=0.0),
    }


def build_findings(metrics: dict[str, object], args: argparse.Namespace) -> list[dict[str, object]]:
    findings: list[dict[str, object]] = []

    def add(code: str, message: str) -> None:
        findings.append({"code": code, "severity": "error", "message": message})

    if metrics["sampleCount"] < args.min_samples:
        add("sample-count", f"Expected at least {args.min_samples} sampled frames, got {metrics['sampleCount']}.")
    if metrics["maxColorBuckets"] < args.min_color_buckets:
        add("color-diversity", f"Expected at least {args.min_color_buckets} color buckets, got {metrics['maxColorBuckets']}.")
    if metrics["medianNonbackgroundRatio"] < args.min_nonbackground_ratio:
        add(
            "nonbackground-ratio",
            f"Expected median nonbackground ratio >= {args.min_nonbackground_ratio}, got {metrics['medianNonbackgroundRatio']}.",
        )
    if metrics["changingPairs"] < args.min_changing_pairs:
        add(
            "motion",
            f"Expected at least {args.min_changing_pairs} changing sampled frame pairs, got {metrics['changingPairs']}.",
        )
    return findings


def main() -> int:
    args = parse_args()
    if not args.video.exists():
        print(f"Missing video: {args.video}", file=sys.stderr)
        return 2
    with tempfile.TemporaryDirectory(prefix="video-motion-audit-") as temp:
        frame_dir = Path(temp)
        run_ffmpeg_extract(args.video, frame_dir, args.sample_fps, args.scale_width)
        metrics = collect_metrics(frame_dir, args)
    findings = build_findings(metrics, args)
    report = {
        "video": args.video.as_posix(),
        "sampleFps": args.sample_fps,
        "scaleWidth": args.scale_width,
        "thresholds": {
            "minSamples": args.min_samples,
            "minColorBuckets": args.min_color_buckets,
            "minNonbackgroundRatio": args.min_nonbackground_ratio,
            "minChangingPairs": args.min_changing_pairs,
            "minChangedPixelRatio": args.min_changed_pixel_ratio,
            "minMeanAbsoluteDiff": args.min_mean_absolute_diff,
        },
        "metrics": metrics,
        "findings": findings,
        "passed": not findings,
    }
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({"report": args.report.as_posix(), "passed": report["passed"]}, indent=2))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"audit_video_motion.py: {exc}", file=sys.stderr)
        raise SystemExit(2)
