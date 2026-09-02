#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Review an MP4 for basic deterministic video quality gates.")
    parser.add_argument("--video", required=True, type=Path)
    parser.add_argument("--report", required=True, type=Path)
    parser.add_argument("--expect-width", type=int)
    parser.add_argument("--expect-height", type=int)
    parser.add_argument("--expect-duration", type=float)
    parser.add_argument("--duration-tolerance", type=float, default=0.25)
    parser.add_argument("--expect-fps", type=float)
    parser.add_argument("--min-size-bytes", type=int, default=4096)
    parser.add_argument("--black-duration", type=float, default=0.30)
    parser.add_argument("--freeze-duration", type=float, default=1.50)
    parser.add_argument("--freeze-noise", type=float, default=0.0001)
    parser.add_argument("--fail-on-black", action="store_true", default=True)
    parser.add_argument("--fail-on-freeze", action="store_true", default=True)
    return parser.parse_args()


def run_command(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, text=True, capture_output=True, check=False)


def parse_rate(value: str | None) -> float | None:
    if not value:
        return None
    if "/" in value:
        numerator, denominator = value.split("/", 1)
        try:
            den = float(denominator)
            return float(numerator) / den if den else None
        except ValueError:
            return None
    try:
        return float(value)
    except ValueError:
        return None


def ffprobe(video: Path) -> dict[str, object]:
    exe = shutil.which("ffprobe")
    if not exe:
        raise RuntimeError("ffprobe is required but was not found on PATH.")
    result = run_command(
        [
            exe,
            "-v",
            "error",
            "-select_streams",
            "v:0",
            "-show_entries",
            "stream=width,height,r_frame_rate,avg_frame_rate,nb_frames,duration",
            "-show_entries",
            "format=duration,size",
            "-of",
            "json",
            str(video),
        ]
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "ffprobe failed.")
    return json.loads(result.stdout)


def ffmpeg_filter_text(video: Path, filter_arg: str) -> str:
    exe = shutil.which("ffmpeg")
    if not exe:
        return ""
    result = run_command([exe, "-hide_banner", "-i", str(video), "-vf", filter_arg, "-an", "-f", "null", "-"])
    return result.stderr or ""


def parse_black_events(text: str) -> list[dict[str, float]]:
    events: list[dict[str, float]] = []
    regex = re.compile(
        r"black_start:(?P<start>[0-9.]+)\s+black_end:(?P<end>[0-9.]+)\s+black_duration:(?P<duration>[0-9.]+)"
    )
    for match in regex.finditer(text):
        events.append({key: float(value) for key, value in match.groupdict().items()})
    return events


def parse_freeze_events(text: str, video_duration: float) -> list[dict[str, float]]:
    events: list[dict[str, float]] = []
    current: dict[str, float] | None = None
    for line in text.splitlines():
        start = re.search(r"freeze_start:\s*(?P<value>[0-9.]+)", line)
        if start:
            current = {"start": float(start.group("value"))}
        duration = re.search(r"freeze_duration:\s*(?P<value>[0-9.]+)", line)
        if duration and current is not None:
            current["duration"] = float(duration.group("value"))
        end = re.search(r"freeze_end:\s*(?P<value>[0-9.]+)", line)
        if end and current is not None:
            current["end"] = float(end.group("value"))
            current.setdefault("duration", current["end"] - current["start"])
            events.append(current)
            current = None
    if current is not None:
        current["end"] = video_duration
        current["duration"] = max(0.0, video_duration - current["start"])
        events.append(current)
    return events


def collect_metrics(video: Path, args: argparse.Namespace) -> dict[str, object]:
    probe = ffprobe(video)
    stream = (probe.get("streams") or [{}])[0] if isinstance(probe.get("streams"), list) else {}
    fmt = probe.get("format") if isinstance(probe.get("format"), dict) else {}
    duration = float(fmt.get("duration") or stream.get("duration") or 0)
    fps = parse_rate(str(stream.get("avg_frame_rate") or stream.get("r_frame_rate") or ""))
    size = int(fmt.get("size") or video.stat().st_size)
    black_events = parse_black_events(ffmpeg_filter_text(video, f"blackdetect=d={args.black_duration}:pix_th=0.10"))
    freeze_events = parse_freeze_events(
        ffmpeg_filter_text(video, f"freezedetect=n={args.freeze_noise}:d={args.freeze_duration}"),
        duration,
    )
    return {
        "path": video.as_posix(),
        "exists": video.exists(),
        "sizeBytes": size,
        "width": stream.get("width"),
        "height": stream.get("height"),
        "durationSeconds": duration,
        "fps": fps,
        "frameRateRaw": stream.get("r_frame_rate"),
        "frameCount": stream.get("nb_frames"),
        "blackEvents": black_events,
        "freezeEvents": freeze_events,
    }


def build_findings(metrics: dict[str, object], args: argparse.Namespace) -> list[dict[str, object]]:
    findings: list[dict[str, object]] = []

    def add(code: str, severity: str, message: str) -> None:
        findings.append({"code": code, "severity": severity, "message": message})

    if not metrics["exists"]:
        add("missing-video", "error", "Video file does not exist.")
        return findings
    if int(metrics["sizeBytes"]) < args.min_size_bytes:
        add("small-file", "error", f"Video is smaller than {args.min_size_bytes} bytes.")
    if args.expect_width is not None and metrics["width"] != args.expect_width:
        add("width", "error", f"Expected width {args.expect_width}, got {metrics['width']}.")
    if args.expect_height is not None and metrics["height"] != args.expect_height:
        add("height", "error", f"Expected height {args.expect_height}, got {metrics['height']}.")
    if args.expect_duration is not None:
        delta = abs(float(metrics["durationSeconds"]) - args.expect_duration)
        if delta > args.duration_tolerance:
            add("duration", "error", f"Expected duration {args.expect_duration}s +/- {args.duration_tolerance}s, got {metrics['durationSeconds']}s.")
    if args.expect_fps is not None and metrics["fps"] is not None:
        if abs(float(metrics["fps"]) - args.expect_fps) > 0.05:
            add("fps", "error", f"Expected fps {args.expect_fps}, got {metrics['fps']}.")
    if args.fail_on_black and metrics["blackEvents"]:
        add("black-frame", "error", f"Detected black-frame spans: {metrics['blackEvents']}.")
    if args.fail_on_freeze and metrics["freezeEvents"]:
        add("freeze", "error", f"Detected freeze spans: {metrics['freezeEvents']}.")
    return findings


def main() -> int:
    args = parse_args()
    metrics = collect_metrics(args.video, args)
    findings = build_findings(metrics, args)
    report = {
        "video": metrics,
        "expectations": {
            "width": args.expect_width,
            "height": args.expect_height,
            "durationSeconds": args.expect_duration,
            "durationToleranceSeconds": args.duration_tolerance,
            "fps": args.expect_fps,
            "minSizeBytes": args.min_size_bytes,
            "blackDurationSeconds": args.black_duration,
            "freezeDurationSeconds": args.freeze_duration,
            "freezeNoise": args.freeze_noise,
        },
        "findings": findings,
        "passed": not any(item["severity"] == "error" for item in findings),
    }
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({"report": args.report.as_posix(), "passed": report["passed"]}, indent=2))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"review_video_quality.py: {exc}", file=sys.stderr)
        raise SystemExit(2)
