#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["pillow>=10.0.0"]
# ///
"""Validate an awsome-videos MP4 artifact and optional review reports."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from fractions import Fraction
from pathlib import Path
from typing import Any

from PIL import Image, ImageStat


def sha256_file(path: Path | None) -> str | None:
    if path is None or not path.is_file():
        return None
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate_video_binding(
    data: dict[str, Any],
    label: str,
    video: Path,
) -> list[str]:
    failures: list[str] = []
    raw_video = data.get("video")
    if not isinstance(raw_video, str) or not raw_video.strip():
        failures.append(f"{label} video path is missing")
    elif Path(raw_video).resolve() != video.resolve():
        failures.append(f"{label} video path does not match the validated MP4")
    expected_digest = sha256_file(video)
    if data.get("videoSha256") != expected_digest:
        failures.append(f"{label} videoSha256 is stale or does not match the validated MP4")
    return failures


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


def resolve_tool(name: str) -> str | None:
    tool = shutil.which(name)
    if tool:
        return tool
    for candidate in common_tool_paths(name):
        if candidate.is_file():
            return str(candidate)
    return None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate an awsome-videos video artifact.")
    parser.add_argument("video", type=Path)
    parser.add_argument("--expect-width", type=int)
    parser.add_argument("--expect-height", type=int)
    parser.add_argument("--expect-fps", type=float)
    parser.add_argument("--fps-tolerance", type=float, default=0.2)
    parser.add_argument("--expect-duration", type=float)
    parser.add_argument("--duration-tolerance", type=float, default=1.0)
    parser.add_argument("--min-duration", type=float)
    parser.add_argument("--max-duration", type=float)
    parser.add_argument("--min-size-bytes", type=int, default=100_000)
    parser.add_argument("--require-audio", action="store_true")
    parser.add_argument("--audio-report", type=Path)
    parser.add_argument("--require-audio-report", action="store_true")
    parser.add_argument("--require-final-audio", action="store_true")
    parser.add_argument("--skip-audio-level-check", action="store_true")
    parser.add_argument("--min-mean-volume-db", type=float, default=-55.0)
    parser.add_argument("--min-max-volume-db", type=float, default=-45.0)
    parser.add_argument("--contact-sheet", type=Path)
    parser.add_argument("--min-contact-sheet-width", type=int, default=320)
    parser.add_argument("--min-contact-sheet-height", type=int, default=180)
    parser.add_argument("--min-contact-sheet-stddev", type=float, default=4.0)
    parser.add_argument("--min-contact-sheet-colors", type=int, default=32)
    parser.add_argument("--quality-report", type=Path)
    parser.add_argument("--motion-report", type=Path)
    parser.add_argument("--capture-manifest", type=Path)
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    return parser.parse_args()


def run_ffprobe(video: Path) -> dict[str, Any]:
    ffprobe = resolve_tool("ffprobe")
    if not ffprobe:
        raise RuntimeError("ffprobe is required but was not found on PATH or common install locations.")
    cmd = [
        ffprobe,
        "-v",
        "error",
        "-show_entries",
        "format=duration,size:stream=index,codec_type,codec_name,width,height,avg_frame_rate,duration",
        "-of",
        "json",
        str(video),
    ]
    result = subprocess.run(cmd, text=True, capture_output=True, check=False)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "ffprobe failed.")
    return json.loads(result.stdout)


def run_volumedetect(video: Path) -> str:
    ffmpeg = resolve_tool("ffmpeg")
    if not ffmpeg:
        raise RuntimeError("ffmpeg is required for audio level checks but was not found on PATH or common install locations.")
    null_output = "NUL" if os.name == "nt" else "/dev/null"
    cmd = [
        ffmpeg,
        "-hide_banner",
        "-nostats",
        "-i",
        str(video),
        "-map",
        "0:a:0",
        "-af",
        "volumedetect",
        "-vn",
        "-sn",
        "-dn",
        "-f",
        "null",
        null_output,
    ]
    result = subprocess.run(cmd, text=True, capture_output=True, check=False)
    output = f"{result.stdout}\n{result.stderr}"
    if result.returncode != 0:
        raise RuntimeError(output.strip() or "ffmpeg volumedetect failed.")
    return output


def parse_volumedetect(output: str) -> dict[str, Any]:
    def match_float(label: str) -> float | None:
        match = re.search(rf"{re.escape(label)}:\s*(-?(?:\d+(?:\.\d+)?|inf))\s*dB", output, flags=re.IGNORECASE)
        if not match:
            return None
        value = match.group(1).lower()
        if value == "-inf":
            return -999.0
        if value == "inf":
            return 999.0
        return float(value)

    return {
        "meanVolumeDb": match_float("mean_volume"),
        "maxVolumeDb": match_float("max_volume"),
    }


def validate_audio_levels(video: Path, min_mean_volume_db: float, min_max_volume_db: float) -> dict[str, Any]:
    output = run_volumedetect(video)
    levels = parse_volumedetect(output)
    failures: list[str] = []
    mean_volume = levels.get("meanVolumeDb")
    max_volume = levels.get("maxVolumeDb")
    if mean_volume is None:
        failures.append("audio mean_volume was not reported by ffmpeg volumedetect")
    elif mean_volume < min_mean_volume_db:
        failures.append(f"audio mean_volume too low: {mean_volume:.2f} dB < {min_mean_volume_db:.2f} dB")
    if max_volume is None:
        failures.append("audio max_volume was not reported by ffmpeg volumedetect")
    elif max_volume < min_max_volume_db:
        failures.append(f"audio max_volume too low: {max_volume:.2f} dB < {min_max_volume_db:.2f} dB")
    return {
        "ok": not failures,
        "failures": failures,
        "meanVolumeDb": mean_volume,
        "maxVolumeDb": max_volume,
        "minMeanVolumeDb": min_mean_volume_db,
        "minMaxVolumeDb": min_max_volume_db,
    }


def parse_float(value: Any) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def parse_fps(value: Any) -> float | None:
    if not value or value == "0/0":
        return None
    try:
        return float(Fraction(str(value)))
    except (ValueError, ZeroDivisionError):
        return parse_float(value)


def load_json_report(path: Path, label: str) -> tuple[dict[str, Any] | None, list[str]]:
    failures: list[str] = []
    if not path.exists():
        return None, [f"{label} not found: {path}"]
    try:
        data = json.loads(path.read_text(encoding="utf-8", errors="ignore"))
    except json.JSONDecodeError as exc:
        return None, [f"{label} is not valid JSON: {exc}"]
    passed = data.get("passed")
    ok = data.get("ok")
    if passed is not True and ok is not True:
        failures.append(f"{label} does not report passed=true or ok=true")
    return data, failures


def validate_contact_sheet(
    path: Path,
    *,
    min_width: int,
    min_height: int,
    min_stddev: float,
    min_colors: int,
) -> dict[str, Any]:
    failures: list[str] = []
    if not path.exists():
        return {"ok": False, "failures": [f"contact sheet not found: {path}"]}
    size_bytes = path.stat().st_size
    if size_bytes < 1_000:
        failures.append(f"contact sheet is too small: {path}")
    try:
        with Image.open(path) as raw_image:
            image = raw_image.convert("RGB")
    except Exception as exc:
        return {"ok": False, "failures": [f"contact sheet could not be opened: {exc}"]}

    width, height = image.size
    if width < min_width:
        failures.append(f"contact sheet width too small: {width}px < {min_width}px")
    if height < min_height:
        failures.append(f"contact sheet height too small: {height}px < {min_height}px")

    sample_width = min(320, width)
    sample_height = max(1, round(height * sample_width / max(width, 1)))
    sample = image.resize((sample_width, sample_height)).convert("RGB")
    luminance = sample.convert("L")
    stddev = float(ImageStat.Stat(luminance).stddev[0])
    if stddev < min_stddev:
        failures.append(f"contact sheet luminance variation too low: {stddev:.2f} < {min_stddev:.2f}")
    colors = sample.getcolors(maxcolors=sample_width * sample_height + 1)
    color_count = len(colors) if colors is not None else sample_width * sample_height
    if color_count < min_colors:
        failures.append(f"contact sheet color diversity too low: {color_count} < {min_colors}")

    return {
        "ok": not failures,
        "failures": failures,
        "path": str(path),
        "sizeBytes": size_bytes,
        "width": width,
        "height": height,
        "sampleWidth": sample_width,
        "sampleHeight": sample_height,
        "luminanceStddev": stddev,
        "colorCount": color_count,
        "minWidth": min_width,
        "minHeight": min_height,
        "minLuminanceStddev": min_stddev,
        "minColorCount": min_colors,
    }


def validate(args: argparse.Namespace) -> dict[str, Any]:
    failures: list[str] = []
    warnings: list[str] = []
    reports: dict[str, Any] = {}

    if not args.video.exists():
        return {
            "ok": False,
            "failures": [f"video not found: {args.video}"],
            "warnings": [],
        }

    if args.video.stat().st_size < args.min_size_bytes:
        failures.append(
            f"video is too small: {args.video.stat().st_size} bytes < {args.min_size_bytes} bytes"
        )
    video_sha256 = sha256_file(args.video)

    try:
        probe = run_ffprobe(args.video)
    except RuntimeError as exc:
        return {
            "ok": False,
            "failures": [str(exc)],
            "warnings": [],
        }

    streams = probe.get("streams", [])
    video_streams = [stream for stream in streams if stream.get("codec_type") == "video"]
    audio_streams = [stream for stream in streams if stream.get("codec_type") == "audio"]
    if not video_streams:
        failures.append("no video stream found")
        video_stream: dict[str, Any] = {}
    else:
        video_stream = video_streams[0]

    if args.require_audio and not audio_streams:
        failures.append("audio stream is required but was not found")
    elif args.require_audio and audio_streams and not getattr(args, "skip_audio_level_check", False):
        try:
            audio_level = validate_audio_levels(
                args.video,
                float(getattr(args, "min_mean_volume_db", -55.0)),
                float(getattr(args, "min_max_volume_db", -45.0)),
            )
            reports["audio_level"] = audio_level
            failures.extend(audio_level.get("failures", []))
        except RuntimeError as exc:
            failures.append(str(exc))

    audio_report_path = getattr(args, "audio_report", None)
    require_audio_report = bool(getattr(args, "require_audio_report", False))
    require_final_audio = bool(getattr(args, "require_final_audio", False))
    audio_report: dict[str, Any] | None = None
    if audio_report_path is not None:
        audio_report, report_failures = load_json_report(audio_report_path, "audio_report")
        failures.extend(report_failures)
        if audio_report is not None:
            failures.extend(validate_video_binding(audio_report, "audio_report", args.video))
            reports["audio_report"] = {
                "path": str(audio_report_path),
                "ok": audio_report.get("ok"),
                "mode": audio_report.get("mode"),
                "placeholderAudio": audio_report.get("placeholderAudio"),
                "finalAudioReady": audio_report.get("finalAudioReady"),
                "finalAudioDurationOk": audio_report.get("finalAudioDurationOk"),
                "sourceDurationSeconds": audio_report.get("sourceDurationSeconds"),
                "expectedDurationSeconds": audio_report.get("expectedDurationSeconds"),
                "needsFinalAudio": audio_report.get("needsFinalAudio"),
                "videoSha256": audio_report.get("videoSha256"),
            }
    elif require_audio_report or require_final_audio:
        failures.append("audio report is required but was not supplied")
    if require_final_audio:
        if audio_report is None:
            failures.append("final audio readiness cannot be proven without audio report")
        else:
            if audio_report.get("finalAudioReady") is not True or audio_report.get("placeholderAudio") is True:
                failures.append("final audio is required but audio report indicates placeholder or unfinished audio")
            if audio_report.get("finalAudioDurationOk") is not True:
                failures.append("final audio is required but audio report does not prove duration coverage")
            source_path_raw = audio_report.get("source")
            source_path = Path(source_path_raw) if isinstance(source_path_raw, str) else None
            if source_path is None or not source_path.is_file():
                failures.append("final audio source file is missing or unreadable")
            elif audio_report.get("sourceSha256") != sha256_file(source_path):
                failures.append("final audio sourceSha256 is stale or invalid")

    width = video_stream.get("width")
    height = video_stream.get("height")
    fps = parse_fps(video_stream.get("avg_frame_rate"))
    duration = parse_float(probe.get("format", {}).get("duration"))
    if duration is None:
        duration = parse_float(video_stream.get("duration"))
    size = parse_float(probe.get("format", {}).get("size"))

    if args.expect_width is not None and width != args.expect_width:
        failures.append(f"expected width {args.expect_width}, got {width}")
    if args.expect_height is not None and height != args.expect_height:
        failures.append(f"expected height {args.expect_height}, got {height}")
    if args.expect_fps is not None:
        if fps is None:
            failures.append("expected fps but avg_frame_rate was unavailable")
        elif abs(fps - args.expect_fps) > args.fps_tolerance:
            failures.append(f"expected fps {args.expect_fps}, got {fps:.3f}")
    if args.expect_duration is not None:
        if duration is None:
            failures.append("expected duration but duration was unavailable")
        elif abs(duration - args.expect_duration) > args.duration_tolerance:
            failures.append(f"expected duration {args.expect_duration}s, got {duration:.3f}s")
    if args.min_duration is not None and duration is not None and duration < args.min_duration:
        failures.append(f"expected duration >= {args.min_duration}s, got {duration:.3f}s")
    if args.max_duration is not None and duration is not None and duration > args.max_duration:
        failures.append(f"expected duration <= {args.max_duration}s, got {duration:.3f}s")

    if args.contact_sheet:
        contact_sheet = validate_contact_sheet(
            args.contact_sheet,
            min_width=getattr(args, "min_contact_sheet_width", 320),
            min_height=getattr(args, "min_contact_sheet_height", 180),
            min_stddev=getattr(args, "min_contact_sheet_stddev", 4.0),
            min_colors=getattr(args, "min_contact_sheet_colors", 32),
        )
        reports["contact_sheet"] = contact_sheet
        failures.extend(contact_sheet.get("failures", []))

    loaded_auxiliary_reports: dict[str, dict[str, Any]] = {}
    for label, path in [
        ("quality_report", args.quality_report),
        ("motion_report", args.motion_report),
        ("capture_manifest", args.capture_manifest),
    ]:
        if path is None:
            continue
        data, report_failures = load_json_report(path, label)
        failures.extend(report_failures)
        if data is not None:
            loaded_auxiliary_reports[label] = data
            failures.extend(validate_video_binding(data, label, args.video))
            reports[label] = {
                "path": str(path),
                "passed": data.get("passed"),
                "ok": data.get("ok"),
                "findings": data.get("findings", []),
                "videoSha256": data.get("videoSha256"),
            }

    capture_manifest = loaded_auxiliary_reports.get("capture_manifest")
    if capture_manifest is not None:
        contact_contract = capture_manifest.get("contactSheet")
        if args.contact_sheet:
            if not isinstance(contact_contract, dict):
                failures.append("capture_manifest contactSheet contract is missing")
            else:
                raw_contact = contact_contract.get("path")
                if not isinstance(raw_contact, str) or Path(raw_contact).resolve() != args.contact_sheet.resolve():
                    failures.append("capture_manifest contactSheet path does not match the supplied contact sheet")
                if contact_contract.get("sha256") != sha256_file(args.contact_sheet):
                    failures.append("capture_manifest contactSheet sha256 is stale or invalid")
        report_digests = capture_manifest.get("reportSha256s")
        expected_report_digests = {
            "audioReport": sha256_file(audio_report_path),
            "qualityReport": sha256_file(args.quality_report),
            "motionReport": sha256_file(args.motion_report),
        }
        if not isinstance(report_digests, dict):
            failures.append("capture_manifest reportSha256s is missing")
        else:
            for report_name, expected_digest in expected_report_digests.items():
                if expected_digest is not None and report_digests.get(report_name) != expected_digest:
                    failures.append(f"capture_manifest {report_name} sha256 is stale or invalid")

    if not args.contact_sheet:
        warnings.append("no contact sheet supplied; automated stream checks cannot prove visual legibility")

    return {
        "ok": not failures,
        "failures": failures,
        "warnings": warnings,
        "video": str(args.video),
        "videoSha256": video_sha256,
        "streams": {
            "video": len(video_streams),
            "audio": len(audio_streams),
            "videoCodec": video_stream.get("codec_name"),
            "audioCodecs": [stream.get("codec_name") for stream in audio_streams],
        },
        "properties": {
            "width": width,
            "height": height,
            "fps": fps,
            "durationSeconds": duration,
            "sizeBytes": int(size) if size is not None else None,
        },
        "reports": reports,
    }


def main() -> int:
    args = parse_args()
    result = validate(args)
    if args.json:
        print(json.dumps(result, indent=2))
    elif result["ok"]:
        props = result.get("properties", {})
        streams = result.get("streams", {})
        fps_text = f"{props.get('fps'):.2f}" if isinstance(props.get("fps"), int | float) else "unknown"
        duration_text = (
            f"{props.get('durationSeconds'):.2f}"
            if isinstance(props.get("durationSeconds"), int | float)
            else "unknown"
        )
        print(
            "PASS awsome-videos video: "
            f"{props.get('width')}x{props.get('height')}, "
            f"{fps_text} fps, "
            f"{duration_text}s, "
            f"audio={'yes' if streams.get('audio') else 'no'}"
        )
        for warning in result.get("warnings", []):
            print(f"WARN {warning}")
    else:
        print("FAIL awsome-videos video")
        for failure in result["failures"]:
            print(f"- {failure}")
        for warning in result.get("warnings", []):
            print(f"WARN {warning}")
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
