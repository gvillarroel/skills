#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

from __future__ import annotations

import argparse
from fractions import Fraction
import json
import shutil
import subprocess
import sys
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Check exact video workflow outputs for existence, JSON pass flags, and literal anchors.")
    parser.add_argument("paths", nargs="*", type=Path, help="Compatibility form for required non-empty paths.")
    parser.add_argument("--require", action="append", default=[], type=Path, help="Required non-empty path. Repeat as needed.")
    parser.add_argument("--require-json-passed", action="append", default=[], type=Path, help="JSON file whose top-level passed field must be true.")
    parser.add_argument(
        "--require-text",
        action="append",
        nargs="+",
        default=[],
        help="Text assertion in PATH::LITERAL form. Extra tokens are joined so unquoted literals with spaces still work.",
    )
    parser.add_argument("--required-anchors", nargs="+", default=[], help="Literal anchors that must appear in at least one text output.")
    parser.add_argument("--anchor-search-path", action="append", default=[], type=Path, help="Text file to search for --required-anchors. Defaults to all required text-like paths.")
    parser.add_argument("--duration", "--expect-duration", dest="expect_duration", type=float, help="Expected video duration in seconds.")
    parser.add_argument("--fps", "--expect-fps", dest="expect_fps", type=float, help="Expected video frame rate.")
    parser.add_argument("--width", "--expect-width", dest="expect_width", type=int, help="Expected video width.")
    parser.add_argument("--height", "--expect-height", dest="expect_height", type=int, help="Expected video height.")
    parser.add_argument("--report", type=Path)
    return parser.parse_args()


def add_finding(findings: list[dict[str, object]], code: str, path: Path | str, message: str) -> None:
    findings.append({"code": code, "path": str(path), "message": message})


def check_required(paths: list[Path], findings: list[dict[str, object]]) -> None:
    for path in paths:
        if not path.exists():
            add_finding(findings, "missing", path, "Required path does not exist.")
            continue
        if path.is_file() and path.stat().st_size <= 0:
            add_finding(findings, "empty", path, "Required file is empty.")


def check_json_passed(paths: list[Path], findings: list[dict[str, object]]) -> None:
    for path in paths:
        if not path.exists():
            add_finding(findings, "missing-json", path, "Required JSON report does not exist.")
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            add_finding(findings, "invalid-json", path, f"JSON parse failed: {exc}")
            continue
        if data.get("passed") is not True:
            add_finding(findings, "json-not-passed", path, "Expected top-level passed field to be true.")


def check_text(assertions: list[str], findings: list[dict[str, object]]) -> None:
    for assertion in assertions:
        if "::" not in assertion:
            add_finding(findings, "invalid-text-assertion", assertion, "Use PATH::LITERAL format.")
            continue
        raw_path, literal = assertion.split("::", 1)
        path = Path(raw_path)
        if not path.exists():
            add_finding(findings, "missing-text-file", path, "Text assertion file does not exist.")
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        if literal not in text:
            add_finding(findings, "missing-literal", path, f"Missing literal: {literal}")


def normalize_text_assertions(raw_assertions: list[list[str]]) -> list[str]:
    return [" ".join(parts) for parts in raw_assertions]


def unique_paths(paths: list[Path]) -> list[Path]:
    seen: set[str] = set()
    unique: list[Path] = []
    for path in paths:
        key = path.as_posix()
        if key not in seen:
            seen.add(key)
            unique.append(path)
    return unique


def text_like_paths(required_paths: list[Path], explicit_paths: list[Path]) -> list[Path]:
    if explicit_paths:
        return explicit_paths
    suffixes = {".json", ".md", ".html", ".mjs", ".js", ".txt", ".yaml", ".yml"}
    return [path for path in required_paths if path.suffix.lower() in suffixes]


def check_required_anchors(anchors: list[str], search_paths: list[Path], findings: list[dict[str, object]]) -> None:
    if not anchors:
        return
    corpus: list[tuple[Path, str]] = []
    for path in search_paths:
        if not path.exists():
            add_finding(findings, "missing-anchor-search-file", path, "Anchor search file does not exist.")
            continue
        if not path.is_file():
            continue
        corpus.append((path, path.read_text(encoding="utf-8", errors="replace")))
    for anchor in anchors:
        if not any(anchor in text for _, text in corpus):
            add_finding(findings, "missing-anchor", "required-anchors", f"Missing anchor in searched text outputs: {anchor}")


def probe_video(video: Path) -> dict[str, object]:
    exe = shutil.which("ffprobe")
    if not exe:
        raise RuntimeError("ffprobe is required for video expectation checks but was not found on PATH.")
    result = subprocess.run(
        [
            exe,
            "-v",
            "error",
            "-select_streams",
            "v:0",
            "-show_entries",
            "stream=width,height,r_frame_rate,duration",
            "-show_entries",
            "format=duration",
            "-of",
            "json",
            str(video),
        ],
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "ffprobe failed.")
    return json.loads(result.stdout)


def rational_to_float(value: object) -> float | None:
    if not isinstance(value, str) or not value:
        return None
    try:
        return float(Fraction(value))
    except (ValueError, ZeroDivisionError):
        return None


def check_video_expectations(paths: list[Path], args: argparse.Namespace, findings: list[dict[str, object]]) -> dict[str, object]:
    expectations = {
        "duration": args.expect_duration,
        "fps": args.expect_fps,
        "width": args.expect_width,
        "height": args.expect_height,
    }
    if all(value is None for value in expectations.values()):
        return {}
    videos = [path for path in paths if path.suffix.lower() in {".mp4", ".webm", ".mov", ".m4v"}]
    if not videos:
        add_finding(findings, "missing-video-for-expectations", "video", "No video path was supplied for media expectation checks.")
        return {"expectations": expectations, "checked": None}
    video = videos[0]
    try:
        data = probe_video(video)
    except RuntimeError as exc:
        add_finding(findings, "video-probe-failed", video, str(exc))
        return {"expectations": expectations, "checked": video.as_posix()}
    stream = (data.get("streams") or [{}])[0]
    fmt = data.get("format") if isinstance(data.get("format"), dict) else {}
    actual_duration = float(fmt.get("duration") or stream.get("duration") or 0)
    actual_fps = rational_to_float(stream.get("r_frame_rate"))
    actual = {
        "duration": actual_duration,
        "fps": actual_fps,
        "width": stream.get("width"),
        "height": stream.get("height"),
    }
    if args.expect_duration is not None and abs(actual_duration - args.expect_duration) > 0.5:
        add_finding(findings, "duration-mismatch", video, f"Expected about {args.expect_duration}s, got {actual_duration:.3f}s.")
    if args.expect_fps is not None and (actual_fps is None or abs(actual_fps - args.expect_fps) > 0.2):
        add_finding(findings, "fps-mismatch", video, f"Expected about {args.expect_fps} fps, got {actual_fps}.")
    if args.expect_width is not None and actual["width"] != args.expect_width:
        add_finding(findings, "width-mismatch", video, f"Expected width {args.expect_width}, got {actual['width']}.")
    if args.expect_height is not None and actual["height"] != args.expect_height:
        add_finding(findings, "height-mismatch", video, f"Expected height {args.expect_height}, got {actual['height']}.")
    return {"expectations": expectations, "checked": video.as_posix(), "actual": actual}


def main() -> int:
    args = parse_args()
    findings: list[dict[str, object]] = []
    required_paths = unique_paths([*args.require, *args.paths])
    text_assertions = normalize_text_assertions(args.require_text)
    check_required(required_paths, findings)
    check_json_passed(args.require_json_passed, findings)
    check_text(text_assertions, findings)
    check_required_anchors(args.required_anchors, text_like_paths(required_paths, args.anchor_search_path), findings)
    media = check_video_expectations(required_paths, args, findings)
    report = {
        "required": [path.as_posix() for path in required_paths],
        "jsonPassed": [path.as_posix() for path in args.require_json_passed],
        "textAssertions": text_assertions,
        "requiredAnchors": args.required_anchors,
        "anchorSearchPaths": [path.as_posix() for path in text_like_paths(required_paths, args.anchor_search_path)],
        "media": media,
        "findings": findings,
        "passed": not findings,
    }
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"check_video_outputs.py: {exc}", file=sys.stderr)
        raise SystemExit(2)
