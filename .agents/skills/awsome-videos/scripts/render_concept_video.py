#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["pillow>=10.0.0", "playwright>=1.45.0"]
# ///
"""Render a deterministic awsome-videos HTML concept renderer to MP4."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import shutil
import subprocess
import sys
import tempfile
from statistics import median
from pathlib import Path
from typing import Any

from PIL import Image, ImageChops, ImageStat

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import extract_voiceover_cues  # noqa: E402


def sha256_file(path: Path | None) -> str | None:
    if path is None or not path.is_file():
        return None
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render an awsome-videos HTML renderer to MP4.")
    parser.add_argument("html", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--video-id")
    parser.add_argument("--duration", type=float, default=70.0)
    parser.add_argument("--fps", type=float, default=30.0)
    parser.add_argument(
        "--capture-fps",
        type=float,
        help="Screenshot capture rate before encoding. Defaults to --fps; use a lower value for faster renders while keeping the final MP4 fps.",
    )
    parser.add_argument("--width", type=int, default=1280)
    parser.add_argument("--height", type=int, default=720)
    parser.add_argument("--brief", type=Path, help="Brief whose timed beats should be sampled in the render-state report.")
    parser.add_argument("--require-all-brief-beats", action="store_true")
    parser.add_argument("--brief-beat-sample-position", type=float, default=0.5)
    parser.add_argument("--frame-dir", type=Path)
    parser.add_argument("--contact-sheet", type=Path)
    parser.add_argument("--quality-report", type=Path)
    parser.add_argument("--motion-report", type=Path)
    parser.add_argument("--capture-manifest", type=Path)
    parser.add_argument("--render-state-report", type=Path)
    parser.add_argument("--audio-report", type=Path)
    parser.add_argument("--motion-sample-fps", type=float, default=1.0)
    parser.add_argument("--motion-scale-width", type=int, default=320)
    parser.add_argument("--audio", choices=["sine", "silent", "none"], default="sine")
    parser.add_argument("--audio-file", type=Path, help="Mux a final narration/music/SFX file instead of generated validation audio.")
    parser.add_argument("--final-audio-duration-tolerance", type=float, default=1.0)
    parser.add_argument("--sine-frequency", type=int, default=220)
    parser.add_argument("--sine-volume", type=float, default=0.045)
    parser.add_argument("--video-bitrate", default="2400k")
    parser.add_argument("--preset", default="veryfast")
    parser.add_argument("--crf", type=int, default=20)
    parser.add_argument("--keep-frames", action="store_true")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--install-browser", action="store_true")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    return parser.parse_args()


def run(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, text=True, capture_output=True, check=False)


def common_tool_paths(name: str) -> list[Path]:
    paths: list[Path] = []
    for env_name in [name.upper(), f"{name.upper()}_PATH"]:
        raw = os.environ.get(env_name)
        if raw:
            paths.append(Path(raw))
    home = Path.home()
    username = os.environ.get("USER") or os.environ.get("USERNAME")
    executable_names = [name, f"{name}.exe"] if not name.endswith(".exe") else [name]
    for executable in executable_names:
        paths.extend(
            [
                home / "AppData" / "Local" / "Microsoft" / "WinGet" / "Links" / executable,
                Path("C:/ProgramData/chocolatey/bin") / executable,
                Path("C:/ffmpeg/bin") / executable,
            ]
        )
    if username:
        for executable in executable_names:
            paths.extend(
                [
                    Path("/mnt/c/Users") / username / "AppData" / "Local" / "Microsoft" / "WinGet" / "Links" / executable,
                    Path("/mnt/c/ProgramData/chocolatey/bin") / executable,
                    Path("/mnt/c/ffmpeg/bin") / executable,
                ]
            )
    return paths


def require_tool(name: str) -> str:
    tool = shutil.which(name)
    if tool:
        return tool
    for candidate in common_tool_paths(name):
        if candidate.is_file():
            return str(candidate)
    raise RuntimeError(f"{name} is required but was not found on PATH or common install locations.")


def install_chromium() -> None:
    result = run([sys.executable, "-m", "playwright", "install", "chromium"])
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "playwright chromium install failed")


def safe_time(index: int, fps: float, duration: float) -> float:
    return min(index / fps, max(0.0, duration - 0.001))


def effective_capture_fps(args: argparse.Namespace) -> float:
    return float(args.capture_fps if args.capture_fps is not None else args.fps)


def capture_frame_count(duration: float, capture_fps: float) -> int:
    return max(1, int(math.ceil(duration * capture_fps)))


def sample_indices(frame_count: int, samples: int = 6) -> list[int]:
    if frame_count <= 0:
        return []
    if frame_count <= samples:
        return list(range(frame_count))
    return sorted({round(i * (frame_count - 1) / (samples - 1)) for i in range(samples)})


def brief_beat_sample_times(brief: Path | None, duration: float, sample_position: float) -> dict[str, Any]:
    if brief is None:
        return {
            "briefBeatCount": 0,
            "expectedBriefBeats": [],
            "briefBeatRanges": [],
            "sampledBriefTimes": [],
            "failures": [],
        }
    if not brief.exists():
        return {
            "briefBeatCount": 0,
            "expectedBriefBeats": [],
            "briefBeatRanges": [],
            "sampledBriefTimes": [],
            "failures": [f"brief not found: {brief}"],
        }
    text = brief.read_text(encoding="utf-8")
    ranges = extract_voiceover_cues.extract_beat_ranges(text)
    failures: list[str] = []
    if not ranges:
        failures.append("brief has no timed beat ranges to sample")
    position = max(0.05, min(0.95, sample_position))
    times: list[float] = []
    for item in ranges:
        start = float(item["startSeconds"])
        end = float(item["endSeconds"])
        if end <= start:
            failures.append(f"brief beat {item.get('index')} has non-positive duration: {item.get('raw')}")
            continue
        at = start + ((end - start) * position)
        at = min(max(0.0, at), max(0.0, duration - 0.001), max(start, end - 0.001))
        times.append(round(at, 3))
    return {
        "briefBeatCount": len(ranges),
        "expectedBriefBeats": [item.get("index") for item in ranges],
        "briefBeatRanges": ranges,
        "sampledBriefTimes": times,
        "failures": failures,
    }


def beat_coverage(states: list[dict[str, Any]], expected_beats: list[Any]) -> dict[str, Any]:
    expected = [int(item) for item in expected_beats if isinstance(item, int)]
    sampled: set[int] = set()
    for sample in states:
        state = sample.get("state") or {}
        active = state.get("activeBeat") if isinstance(state, dict) else None
        try:
            sampled.add(int(active))
        except (TypeError, ValueError):
            continue
    missing = [beat for beat in expected if beat not in sampled]
    return {
        "briefBeatCoverageOk": bool(expected) and not missing,
        "expectedBriefBeats": expected,
        "sampledBriefBeats": sorted(sampled),
        "missingBriefBeats": missing,
    }


def launch_browser(playwright: Any, install_browser: bool) -> Any:
    try:
        return playwright.chromium.launch(headless=True, timeout=15_000)
    except Exception:  # noqa: BLE001
        if not install_browser:
            raise
        install_chromium()
        return playwright.chromium.launch(headless=True, timeout=15_000)


def capture_frames(args: argparse.Namespace, frame_dir: Path) -> dict[str, Any]:
    from playwright.sync_api import sync_playwright

    if not args.html.exists():
        raise FileNotFoundError(args.html)

    capture_fps = effective_capture_fps(args)
    frame_count = capture_frame_count(args.duration, capture_fps)
    states: list[dict[str, Any]] = []
    brief_samples = brief_beat_sample_times(args.brief, args.duration, args.brief_beat_sample_position)
    if args.require_all_brief_beats and brief_samples.get("failures"):
        raise RuntimeError("; ".join(str(failure) for failure in brief_samples["failures"]))
    sampled = set(sample_indices(frame_count, samples=8))
    for at in brief_samples.get("sampledBriefTimes", []):
        sampled.add(max(0, min(frame_count - 1, round(float(at) * capture_fps))))
    frame_dir.mkdir(parents=True, exist_ok=True)
    for old_frame in frame_dir.glob("frame_*.png"):
        old_frame.unlink()

    with sync_playwright() as playwright:
        browser = launch_browser(playwright, args.install_browser)
        page = browser.new_page(viewport={"width": args.width, "height": args.height})
        page.add_init_script("window.AWSOME_VIDEO_TEST_MODE = true;")
        page.goto(args.html.resolve().as_uri(), wait_until="load")
        has_function = page.evaluate("typeof window.renderConceptFrame === 'function'")
        if not has_function:
            raise RuntimeError("window.renderConceptFrame is not defined")

        for index in range(frame_count):
            at = safe_time(index, capture_fps, args.duration)
            state = page.evaluate(
                """([videoId, seconds, duration]) => {
                  const requestedVideoId = videoId || undefined;
                  return window.renderConceptFrame(requestedVideoId, seconds, { duration });
                }""",
                [args.video_id, at, args.duration],
            )
            frame_path = frame_dir / f"frame_{index:06d}.png"
            page.screenshot(path=str(frame_path), full_page=False)
            if index in sampled:
                states.append({"frame": index, "time": at, "state": state, "path": str(frame_path)})
        browser.close()

    return {
        "frameCount": frame_count,
        "fps": args.fps,
        "captureFps": capture_fps,
        "durationSeconds": args.duration,
        "width": args.width,
        "height": args.height,
        "frameDir": str(frame_dir),
        "sampledStates": states,
        "briefBeatCount": brief_samples.get("briefBeatCount", 0),
        "expectedBriefBeats": brief_samples.get("expectedBriefBeats", []),
        "sampledBriefTimes": brief_samples.get("sampledBriefTimes", []),
        "briefBeatFailures": brief_samples.get("failures", []),
    }


def encode_video(args: argparse.Namespace, frame_dir: Path, capture_fps: float) -> list[str]:
    ffmpeg = require_tool("ffmpeg")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    if args.output.exists() and not args.force:
        raise FileExistsError(f"output exists; pass --force to overwrite: {args.output}")
    if args.audio_file and not args.audio_file.exists():
        raise FileNotFoundError(f"audio file not found: {args.audio_file}")

    base_cmd = [
        ffmpeg,
        "-y",
        "-framerate",
        f"{capture_fps:g}",
        "-i",
        str(frame_dir / "frame_%06d.png"),
    ]
    audio_filter = None
    if args.audio_file:
        base_cmd.extend(["-i", str(args.audio_file)])
    elif args.audio == "sine":
        base_cmd.extend(
            [
                "-f",
                "lavfi",
                "-i",
                f"sine=frequency={args.sine_frequency}:sample_rate=48000:duration={args.duration:g}",
            ]
        )
        audio_filter = f"volume={args.sine_volume:g}"
    elif args.audio == "silent":
        base_cmd.extend(
            [
                "-f",
                "lavfi",
                "-i",
                f"anullsrc=channel_layout=stereo:sample_rate=48000",
                "-t",
                f"{args.duration:g}",
            ]
        )

    cmd = [
        *base_cmd,
        "-c:v",
        "libx264",
        "-preset",
        args.preset,
        "-crf",
        str(args.crf),
        "-b:v",
        args.video_bitrate,
        "-r",
        f"{args.fps:g}",
        "-pix_fmt",
        "yuv420p",
    ]
    if args.audio_file or args.audio != "none":
        if audio_filter:
            cmd.extend(["-filter:a", audio_filter])
        cmd.extend(["-c:a", "aac", "-shortest"])
    cmd.append(str(args.output))

    result = run(cmd)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "ffmpeg failed")
    return cmd


def probe_media_duration(path: Path) -> float | None:
    ffprobe = require_tool("ffprobe")
    result = run(
        [
            ffprobe,
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(path),
        ]
    )
    if result.returncode != 0:
        return None
    try:
        return float(result.stdout.strip())
    except ValueError:
        return None


def build_audio_report(args: argparse.Namespace, output: Path | None) -> dict[str, Any]:
    expected_duration = float(getattr(args, "duration", 0.0) or 0.0)
    duration_tolerance = float(getattr(args, "final_audio_duration_tolerance", 1.0))
    source_duration: float | None = None
    if args.audio_file:
        mode = "file"
        source = str(args.audio_file)
        placeholder = False
        has_audio_stream = True
        source_size = args.audio_file.stat().st_size if args.audio_file.exists() else 0
        source_duration = probe_media_duration(args.audio_file) if args.audio_file.exists() else None
    else:
        mode = args.audio
        source = {
            "sine": "generated sine validation tone",
            "silent": "generated silent AAC validation track",
            "none": "no audio stream",
        }[args.audio]
        placeholder = args.audio in {"sine", "silent"}
        has_audio_stream = args.audio != "none"
        source_size = None
        source_duration = expected_duration if args.audio in {"sine", "silent"} else None
    duration_delta = (
        round(source_duration - expected_duration, 3)
        if source_duration is not None and expected_duration > 0
        else None
    )
    duration_ok = (
        source_duration is not None
        and expected_duration > 0
        and source_duration >= max(0.0, expected_duration - duration_tolerance)
    )
    final_ready = mode == "file" and has_audio_stream and not placeholder and duration_ok
    report = {
        "ok": True,
        "mode": mode,
        "source": source,
        "sourceSizeBytes": source_size,
        "sourceDurationSeconds": round(source_duration, 3) if source_duration is not None else None,
        "expectedDurationSeconds": expected_duration,
        "durationToleranceSeconds": duration_tolerance,
        "durationDeltaSeconds": duration_delta,
        "finalAudioDurationOk": duration_ok,
        "hasAudioStream": has_audio_stream,
        "placeholderAudio": placeholder,
        "finalAudioReady": final_ready,
        "needsFinalAudio": not final_ready,
        "video": str(args.output),
        "videoSha256": sha256_file(args.output),
        "sourceSha256": sha256_file(args.audio_file) if args.audio_file else None,
    }
    if output:
        write_json(output, report)
    return report


def analyze_image(path: Path) -> dict[str, Any]:
    with Image.open(path) as image:
        rgb = image.convert("RGB")
        stat = ImageStat.Stat(rgb)
        extrema = rgb.getextrema()
        means = stat.mean
        stddev = stat.stddev
        return {
            "path": str(path),
            "size": list(rgb.size),
            "meanLuma": round(sum(means) / 3, 3),
            "meanStddev": round(sum(stddev) / 3, 3),
            "extrema": extrema,
        }


def build_contact_sheet(sample_paths: list[Path], output: Path, columns: int = 3) -> dict[str, Any]:
    if not sample_paths:
        raise RuntimeError("no sample frames available for contact sheet")
    output.parent.mkdir(parents=True, exist_ok=True)
    thumb_w = 426
    thumb_h = 240
    rows = math.ceil(len(sample_paths) / columns)
    sheet = Image.new("RGB", (thumb_w * columns, thumb_h * rows), (5, 7, 10))
    for index, path in enumerate(sample_paths):
        with Image.open(path) as image:
            thumb = image.convert("RGB").resize((thumb_w, thumb_h), Image.Resampling.LANCZOS)
        x = (index % columns) * thumb_w
        y = (index // columns) * thumb_h
        sheet.paste(thumb, (x, y))
    sheet.save(output, quality=88)
    return {"path": str(output), "frames": len(sample_paths), "size": list(sheet.size)}


def write_json(path: Path | None, data: dict[str, Any]) -> None:
    if path is None:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8", newline="\n")


def build_quality_report(
    sample_paths: list[Path],
    output: Path | None,
    *,
    video_path: Path,
) -> dict[str, Any]:
    findings: list[str] = []
    analyses = [analyze_image(path) for path in sample_paths]
    if not analyses:
        findings.append("no sampled frames were analyzed")
    for item in analyses:
        if item["meanLuma"] < 3:
            findings.append(f"sample frame appears black: {item['path']}")
        if item["meanStddev"] < 2:
            findings.append(f"sample frame has very low visual variation: {item['path']}")
    report = {
        "passed": not findings,
        "ok": not findings,
        "findings": findings,
        "sampleCount": len(analyses),
        "samples": analyses,
        "video": str(video_path),
        "videoSha256": sha256_file(video_path),
    }
    write_json(output, report)
    return report


def scaled_rgb(path: Path, scale_width: int) -> Image.Image:
    with Image.open(path) as image:
        rgb = image.convert("RGB")
        width, height = rgb.size
        target_width = max(32, min(width, scale_width))
        target_height = max(1, round(height * (target_width / width)))
        return rgb.resize((target_width, target_height), Image.Resampling.BILINEAR)


def color_bucket_count(image: Image.Image) -> tuple[int, float]:
    quantized = image.quantize(colors=64, method=Image.Quantize.MEDIANCUT)
    colors = quantized.getcolors(maxcolors=65_536) or []
    total = image.size[0] * image.size[1]
    dominant = max((count for count, _ in colors), default=total)
    nonbackground_ratio = 1.0 - (dominant / total if total else 1.0)
    return len(colors), nonbackground_ratio


def motion_sample_indices(frame_count: int, fps: float, sample_fps: float) -> list[int]:
    if frame_count <= 0:
        return []
    interval = max(1, round(fps / max(0.1, sample_fps)))
    indices = list(range(0, frame_count, interval))
    if indices[-1] != frame_count - 1:
        indices.append(frame_count - 1)
    return indices


def build_motion_report(
    frame_dir: Path,
    frame_count: int,
    fps: float,
    duration: float,
    output: Path | None,
    *,
    video_path: Path,
    sample_fps: float,
    scale_width: int,
) -> dict[str, Any] | None:
    if output is None:
        return None

    thresholds = {
        "minSamples": 20,
        "minColorBuckets": 8,
        "minNonbackgroundRatio": 0.01,
        "minChangingPairs": 8,
        "minChangedPixelRatio": 0.001,
        "minMeanAbsoluteDiff": 0.2,
        "minSubtleChangingPairs": 12,
        "minSubtleChangedPixelRatio": 0.00035,
        "minSubtleMeanAbsoluteDiff": 0.04,
        "pixelDeltaThreshold": 8,
    }
    indices = motion_sample_indices(frame_count, fps, sample_fps)
    sample_names: list[str] = []
    color_buckets: list[int] = []
    nonbackground_ratios: list[float] = []
    diffs: list[dict[str, float]] = []
    previous_gray: Image.Image | None = None

    for index in indices:
        frame_path = frame_dir / f"frame_{index:06d}.png"
        if not frame_path.exists():
            continue
        sample_names.append(frame_path.name)
        image = scaled_rgb(frame_path, scale_width)
        buckets, nonbackground_ratio = color_bucket_count(image)
        color_buckets.append(buckets)
        nonbackground_ratios.append(nonbackground_ratio)
        gray = image.convert("L")
        if previous_gray is not None:
            diff = ImageChops.difference(previous_gray, gray)
            histogram = diff.histogram()
            total_pixels = diff.size[0] * diff.size[1]
            changed_pixels = sum(
                count for value, count in enumerate(histogram) if value >= thresholds["pixelDeltaThreshold"]
            )
            stat = ImageStat.Stat(diff)
            diffs.append(
                {
                    "meanAbsoluteDiff": round(float(stat.mean[0]), 6),
                    "changedPixelRatio": round(changed_pixels / total_pixels if total_pixels else 0.0, 6),
                }
            )
        previous_gray = gray

    changing_pairs = sum(
        1
        for item in diffs
        if item["changedPixelRatio"] >= thresholds["minChangedPixelRatio"]
        and item["meanAbsoluteDiff"] >= thresholds["minMeanAbsoluteDiff"]
    )
    subtle_changing_pairs = sum(
        1
        for item in diffs
        if item["changedPixelRatio"] >= thresholds["minSubtleChangedPixelRatio"]
        and item["meanAbsoluteDiff"] >= thresholds["minSubtleMeanAbsoluteDiff"]
    )
    metrics = {
        "sampleCount": len(sample_names),
        "frameFiles": sample_names,
        "maxColorBuckets": max(color_buckets, default=0),
        "medianColorBuckets": median(color_buckets) if color_buckets else 0,
        "medianNonbackgroundRatio": median(nonbackground_ratios) if nonbackground_ratios else 0,
        "maxNonbackgroundRatio": max(nonbackground_ratios, default=0),
        "diffs": diffs,
        "changingPairs": changing_pairs,
        "subtleChangingPairs": subtle_changing_pairs,
        "maxChangedPixelRatio": max((item["changedPixelRatio"] for item in diffs), default=0),
        "maxMeanAbsoluteDiff": max((item["meanAbsoluteDiff"] for item in diffs), default=0),
    }
    available_pairs = max(0, metrics["sampleCount"] - 1)
    effective_thresholds = {
        **thresholds,
        "minSamples": min(thresholds["minSamples"], max(6, math.floor(duration * sample_fps * 0.8))),
        "minChangingPairs": min(thresholds["minChangingPairs"], max(3, math.ceil(available_pairs * 0.18))),
        "minSubtleChangingPairs": min(
            thresholds["minSubtleChangingPairs"],
            max(4, math.ceil(available_pairs * 0.35)),
        ),
    }
    findings: list[str] = []
    if metrics["sampleCount"] < effective_thresholds["minSamples"]:
        findings.append(f"too few motion samples: {metrics['sampleCount']} < {effective_thresholds['minSamples']}")
    if metrics["maxColorBuckets"] < thresholds["minColorBuckets"]:
        findings.append(
            f"low color/shape variety: maxColorBuckets {metrics['maxColorBuckets']} < {thresholds['minColorBuckets']}"
        )
    if metrics["medianNonbackgroundRatio"] < thresholds["minNonbackgroundRatio"]:
        findings.append(
            "low non-background coverage: "
            f"medianNonbackgroundRatio {metrics['medianNonbackgroundRatio']:.6f} "
            f"< {thresholds['minNonbackgroundRatio']}"
        )
    if (
        metrics["changingPairs"] < effective_thresholds["minChangingPairs"]
        and metrics["subtleChangingPairs"] < effective_thresholds["minSubtleChangingPairs"]
    ):
        findings.append(
            "too few changing frame pairs: "
            f"{metrics['changingPairs']} strong < {effective_thresholds['minChangingPairs']} and "
            f"{metrics['subtleChangingPairs']} subtle < {effective_thresholds['minSubtleChangingPairs']}"
        )

    report = {
        "video": str(video_path),
        "videoSha256": sha256_file(video_path),
        "report": str(output),
        "sampleFps": sample_fps,
        "scaleWidth": scale_width,
        "durationSeconds": duration,
        "thresholds": thresholds,
        "effectiveThresholds": effective_thresholds,
        "metrics": metrics,
        "findings": findings,
        "passed": not findings,
        "ok": not findings,
    }
    write_json(output, report)
    return report


def render(args: argparse.Namespace) -> dict[str, Any]:
    ffmpeg = require_tool("ffmpeg")
    require_tool("ffprobe")
    if args.output.exists() and not args.force:
        raise FileExistsError(f"output exists; pass --force to overwrite: {args.output}")
    if args.duration <= 0:
        raise ValueError("--duration must be positive")
    if args.fps <= 0:
        raise ValueError("--fps must be positive")
    capture_fps = effective_capture_fps(args)
    if capture_fps <= 0:
        raise ValueError("--capture-fps must be positive")

    if args.frame_dir:
        auto_temp = False
        frame_dir = args.frame_dir
        temp_context = None
    elif args.keep_frames:
        auto_temp = False
        frame_dir = args.output.parent / "frames" / args.output.stem
        temp_context = None
    else:
        auto_temp = True
        temp_context = tempfile.TemporaryDirectory(prefix="awsome-video-frames-")
        frame_dir = Path(temp_context.name)
    try:
        capture = capture_frames(args, frame_dir)
        ffmpeg_cmd = encode_video(args, frame_dir, capture_fps)
        audio_report = build_audio_report(args, args.audio_report)
        frame_count = capture["frameCount"]
        sampled_indices = sample_indices(frame_count, samples=6)
        sample_paths = [frame_dir / f"frame_{index:06d}.png" for index in sampled_indices]
        contact = build_contact_sheet(sample_paths, args.contact_sheet, columns=3) if args.contact_sheet else None
        quality = build_quality_report(sample_paths, args.quality_report, video_path=args.output)
        motion = build_motion_report(
            frame_dir,
            frame_count,
            capture_fps,
            args.duration,
            args.motion_report,
            video_path=args.output,
            sample_fps=args.motion_sample_fps,
            scale_width=args.motion_scale_width,
        )
        unique_beats = sorted(
            {
                sample.get("state", {}).get("activeBeat")
                for sample in capture.get("sampledStates", [])
                if sample.get("state")
            }
        )
        coverage = beat_coverage(capture.get("sampledStates", []), capture.get("expectedBriefBeats", []))
        render_state = {
            "ok": bool(unique_beats) and (not args.require_all_brief_beats or coverage["briefBeatCoverageOk"]),
            "failures": [] if unique_beats else ["no render states were sampled"],
            "warnings": [],
            "states": capture.get("sampledStates", []),
            "uniqueBeats": unique_beats,
            "briefBeatCount": capture.get("briefBeatCount", 0),
            "sampledBriefTimes": capture.get("sampledBriefTimes", []),
            **coverage,
        }
        if args.require_all_brief_beats and coverage["missingBriefBeats"]:
            render_state["failures"].append(
                "renderer missing activeBeat coverage for brief beats: "
                + ", ".join(str(item) for item in coverage["missingBriefBeats"])
            )
        if args.require_all_brief_beats and not coverage["expectedBriefBeats"]:
            render_state["ok"] = False
            render_state["failures"].append("renderer beat coverage was required but no expected brief beats were found")
        write_json(args.render_state_report, render_state)
        manifest = {
            "ok": quality["ok"] and render_state["ok"] and (motion is None or motion["ok"]),
            "html": str(args.html),
            "video": str(args.output),
            "videoSha256": sha256_file(args.output),
            "htmlSha256": sha256_file(args.html),
            "durationSeconds": args.duration,
            "fps": args.fps,
            "captureFps": capture_fps,
            "width": args.width,
            "height": args.height,
            "frameCount": frame_count,
            "capturedFrameCount": frame_count,
            "audio": audio_report["mode"],
            "audioReport": str(args.audio_report) if args.audio_report else None,
            "audioFinalReady": audio_report["finalAudioReady"],
            "audioPlaceholder": audio_report["placeholderAudio"],
            "ffmpeg": ffmpeg,
            "ffmpegCommand": ffmpeg_cmd,
            "contactSheet": contact,
            "qualityReport": str(args.quality_report) if args.quality_report else None,
            "motionReport": str(args.motion_report) if args.motion_report else None,
            "renderStateReport": str(args.render_state_report) if args.render_state_report else None,
            "uniqueBeats": unique_beats,
            "keptFrames": (not auto_temp) or args.keep_frames,
            "frameDir": str(frame_dir) if ((not auto_temp) or args.keep_frames) else None,
        }
        if isinstance(manifest.get("contactSheet"), dict) and args.contact_sheet:
            manifest["contactSheet"]["sha256"] = sha256_file(args.contact_sheet)
        manifest["reportSha256s"] = {
            "audioReport": sha256_file(args.audio_report),
            "qualityReport": sha256_file(args.quality_report),
            "motionReport": sha256_file(args.motion_report),
            "renderStateReport": sha256_file(args.render_state_report),
        }
        write_json(args.capture_manifest, manifest)
        return manifest
    finally:
        if temp_context and not args.keep_frames:
            temp_context.cleanup()


def main() -> int:
    args = parse_args()
    try:
        result = render(args)
        ok = bool(result.get("ok"))
        if args.json:
            print(json.dumps(result, indent=2))
        elif ok:
            print(
                "PASS awsome-videos render: "
                f"{result.get('video')} ({result.get('frameCount')} frames at {result.get('fps')} fps)"
            )
        else:
            print("FAIL awsome-videos render")
            print(json.dumps(result, indent=2))
        return 0 if ok else 1
    except Exception as exc:  # noqa: BLE001
        result = {"ok": False, "failures": [str(exc)]}
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print("FAIL awsome-videos render")
            print(f"- {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
