#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright>=1.45.0"]
# ///

from __future__ import annotations

import argparse
import contextlib
import http.server
import json
import random
import shutil
import socket
import subprocess
import sys
import tempfile
import threading
from functools import partial
from pathlib import Path

from playwright.sync_api import sync_playwright


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Capture a deterministic HTML renderConceptFrame video with Chromium and ffmpeg.")
    parser.add_argument("--html", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--video-id", required=True)
    parser.add_argument("--duration", required=True, type=float)
    parser.add_argument("--fps", required=True, type=int)
    parser.add_argument("--width", required=True, type=int)
    parser.add_argument("--height", required=True, type=int)
    parser.add_argument("--selector", default="#stage")
    parser.add_argument("--device-scale-factor", type=float, default=1.0)
    parser.add_argument("--crf", default="18")
    parser.add_argument("--preset", default="veryfast")
    parser.add_argument("--manifest", type=Path)
    parser.add_argument("--keep-frames", action="store_true")
    parser.add_argument("--frame-dir", type=Path)
    parser.add_argument(
        "--expect-state",
        action="append",
        default=[],
        help="Expected top-level render state value in KEY=VALUE form. Repeat as needed.",
    )
    parser.add_argument(
        "--expect-state-final",
        action="append",
        default=[],
        help="Expected final captured top-level render state value in KEY=VALUE form. Repeat as needed.",
    )
    parser.add_argument(
        "--expect-state-transition",
        action="append",
        default=[],
        help="Expected first-to-final top-level render state transition in KEY=FROM->TO form. Repeat as needed.",
    )
    parser.add_argument(
        "--expect-state-monotonic",
        action="append",
        default=[],
        help="Expected numeric state monotonicity in KEY=nondecreasing|nonincreasing|increasing|decreasing form. Repeat as needed.",
    )
    parser.add_argument(
        "--min-distinct-state",
        action="append",
        default=[],
        help="Minimum distinct top-level render state values in KEY=COUNT form. Repeat as needed.",
    )
    return parser.parse_args()


def free_port() -> int:
    for _ in range(100):
        port = random.randint(49152, 65535)
        with contextlib.closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
            try:
                sock.bind(("127.0.0.1", port))
            except OSError:
                continue
        return port
    raise RuntimeError("Could not find a free high localhost port")


class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format: str, *args: object) -> None:
        return


@contextlib.contextmanager
def serve_directory(directory: Path):
    port = free_port()
    handler = partial(QuietHandler, directory=str(directory))
    server = http.server.ThreadingHTTPServer(("127.0.0.1", port), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{port}"
    finally:
        server.shutdown()
        thread.join(timeout=5)
        server.server_close()


def run_ffmpeg(frame_dir: Path, args: argparse.Namespace) -> None:
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        raise RuntimeError("ffmpeg is required but was not found on PATH.")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        ffmpeg,
        "-y",
        "-framerate",
        str(args.fps),
        "-i",
        str(frame_dir / "frame-%06d.png"),
        "-an",
        "-c:v",
        "libx264",
        "-pix_fmt",
        "yuv420p",
        "-preset",
        args.preset,
        "-crf",
        args.crf,
        "-movflags",
        "+faststart",
        str(args.output),
    ]
    result = subprocess.run(cmd, text=True, capture_output=True, check=False)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "ffmpeg failed.")


def capture_frames(frame_dir: Path, args: argparse.Namespace) -> list[dict[str, object]]:
    html = args.html.resolve()
    if not html.exists():
        raise FileNotFoundError(html)
    frame_dir.mkdir(parents=True, exist_ok=True)
    frame_count = max(1, round(args.duration * args.fps))
    states: list[dict[str, object]] = []
    with serve_directory(html.parent) as base_url:
        url = f"{base_url}/{html.name}"
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            try:
                page = browser.new_page(
                    viewport={"width": args.width, "height": args.height},
                    device_scale_factor=args.device_scale_factor,
                )
                page.goto(url, wait_until="networkidle")
                page.wait_for_selector(args.selector, state="visible", timeout=10_000)
                page.evaluate("document.fonts && document.fonts.ready")
                target = page.locator(args.selector)
                for frame in range(frame_count):
                    seconds = frame / args.fps
                    state = page.evaluate(
                        """({ videoId, seconds }) => {
                            if (typeof window.renderConceptFrame !== "function") {
                                throw new Error("window.renderConceptFrame is not defined");
                            }
                            return window.renderConceptFrame(videoId, seconds, { capture: true });
                        }""",
                        {"videoId": args.video_id, "seconds": seconds},
                    )
                    states.append({"frame": frame, "seconds": seconds, "state": state})
                    target.screenshot(path=str(frame_dir / f"frame-{frame:06d}.png"), animations="disabled")
            finally:
                browser.close()
    return states


def state_summary(states: list[dict[str, object]]) -> dict[str, object]:
    values: dict[str, list[object]] = {}
    for item in states:
        state = item.get("state")
        if not isinstance(state, dict):
            continue
        for key, value in state.items():
            values.setdefault(key, []).append(value)
    summary: dict[str, object] = {}
    for key, items in values.items():
        distinct = sorted({json.dumps(value, sort_keys=True) for value in items})
        numeric = [float(value) for value in items if isinstance(value, int | float)]
        entry: dict[str, object] = {
            "count": len(items),
            "distinctCount": len(distinct),
            "distinctValues": distinct[:12],
        }
        if numeric:
            entry["min"] = min(numeric)
            entry["max"] = max(numeric)
        summary[key] = entry
    return summary


def parse_key_value(raw: str) -> tuple[str, str]:
    if "=" not in raw:
        raise ValueError(f"Expected KEY=VALUE, got {raw!r}")
    key, value = raw.split("=", 1)
    if not key:
        raise ValueError(f"Expected non-empty KEY in {raw!r}")
    return key, value


def parse_transition(raw: str) -> tuple[str, str, str]:
    key, value = parse_key_value(raw)
    if "->" not in value:
        raise ValueError(f"Expected KEY=FROM->TO, got {raw!r}")
    start, end = value.split("->", 1)
    start = start.strip()
    end = end.strip()
    if not start or not end:
        raise ValueError(f"Expected non-empty transition values in {raw!r}")
    return key, start, end


def expected_value_candidates(expected: str) -> set[str]:
    candidates = {expected}
    try:
        candidates.add(str(json.loads(expected)))
    except json.JSONDecodeError:
        pass
    lowered = expected.lower()
    if lowered == "true":
        candidates.add("True")
    elif lowered == "false":
        candidates.add("False")
    elif lowered == "null":
        candidates.add("None")
    return candidates


def value_matches_expected(value: object, expected: str) -> bool:
    if str(value) in expected_value_candidates(expected):
        return True
    if isinstance(value, str) and value == expected:
        return True
    return False


def state_values(states: list[dict[str, object]], key: str) -> list[object]:
    values: list[object] = []
    for item in states:
        state = item.get("state")
        if isinstance(state, dict) and key in state:
            values.append(state[key])
    return values


def numeric_values(values: list[object]) -> list[float] | None:
    converted: list[float] = []
    for value in values:
        if not isinstance(value, int | float | bool):
            return None
        converted.append(float(value))
    return converted


def is_monotonic(values: list[float], mode: str) -> bool:
    pairs = zip(values, values[1:])
    if mode in {"nondecreasing", "non-decreasing"}:
        return all(left <= right for left, right in pairs)
    if mode in {"nonincreasing", "non-increasing"}:
        return all(left >= right for left, right in pairs)
    if mode == "increasing":
        return all(left < right for left, right in pairs)
    if mode == "decreasing":
        return all(left > right for left, right in pairs)
    raise ValueError(f"Unsupported monotonic mode {mode!r}")


def build_findings(summary: dict[str, object], states: list[dict[str, object]], args: argparse.Namespace) -> list[dict[str, object]]:
    findings: list[dict[str, object]] = []

    def add(code: str, message: str) -> None:
        findings.append({"code": code, "severity": "error", "message": message})

    for raw in args.expect_state:
        key, expected = parse_key_value(raw)
        entry = summary.get(key)
        if not isinstance(entry, dict):
            add("missing-state-key", f"Expected render state key {key!r}, but it was not returned.")
            continue
        values = [str(json.loads(value)) for value in entry.get("distinctValues", [])]
        if not expected_value_candidates(expected).intersection(values):
            add("unexpected-state-value", f"Expected render state {key}={expected!r}, got {sorted(values)}.")

    for raw in args.expect_state_final:
        key, expected = parse_key_value(raw)
        values = state_values(states, key)
        if not values:
            add("missing-state-key", f"Expected final render state key {key!r}, but it was not returned.")
            continue
        actual = values[-1]
        if not value_matches_expected(actual, expected):
            add("unexpected-final-state-value", f"Expected final render state {key}={expected!r}, got {actual!r}.")

    for raw in args.expect_state_transition:
        key, start, end = parse_transition(raw)
        values = state_values(states, key)
        if not values:
            add("missing-state-key", f"Expected transition render state key {key!r}, but it was not returned.")
            continue
        actual_start = values[0]
        actual_end = values[-1]
        if not value_matches_expected(actual_start, start):
            add("unexpected-initial-state-value", f"Expected initial render state {key}={start!r}, got {actual_start!r}.")
        if not value_matches_expected(actual_end, end):
            add("unexpected-final-state-value", f"Expected final render state {key}={end!r}, got {actual_end!r}.")

    for raw in args.expect_state_monotonic:
        key, mode = parse_key_value(raw)
        values = state_values(states, key)
        if not values:
            add("missing-state-key", f"Expected monotonic render state key {key!r}, but it was not returned.")
            continue
        numbers = numeric_values(values)
        if numbers is None:
            add("non-numeric-state-value", f"Expected numeric render state key {key!r} for monotonic check, got {values[:6]!r}.")
            continue
        if not is_monotonic(numbers, mode):
            add("state-not-monotonic", f"Expected render state key {key!r} to be {mode}, got {numbers[:12]}.")

    for raw in args.min_distinct_state:
        key, raw_count = parse_key_value(raw)
        try:
            required = int(raw_count)
        except ValueError as exc:
            raise ValueError(f"Expected integer count in {raw!r}") from exc
        entry = summary.get(key)
        if not isinstance(entry, dict):
            add("missing-state-key", f"Expected render state key {key!r}, but it was not returned.")
            continue
        actual = int(entry.get("distinctCount", 0))
        if actual < required:
            add("state-not-changing", f"Expected at least {required} distinct values for state key {key!r}, got {actual}.")
    return findings


def main() -> int:
    args = parse_args()
    if args.duration <= 0:
        print("--duration must be positive", file=sys.stderr)
        return 2
    if args.fps <= 0:
        print("--fps must be positive", file=sys.stderr)
        return 2

    temp_dir: tempfile.TemporaryDirectory[str] | None = None
    if args.frame_dir:
        frame_dir = args.frame_dir
    else:
        temp_dir = tempfile.TemporaryDirectory(prefix="html-video-frames-")
        frame_dir = Path(temp_dir.name)

    try:
        states = capture_frames(frame_dir, args)
        run_ffmpeg(frame_dir, args)
        summary = state_summary(states)
        findings = build_findings(summary, states, args)
        manifest = {
            "html": args.html.as_posix(),
            "output": args.output.as_posix(),
            "videoId": args.video_id,
            "durationSeconds": args.duration,
            "fps": args.fps,
            "width": args.width,
            "height": args.height,
            "frameCount": len(states),
            "selector": args.selector,
            "deviceScaleFactor": args.device_scale_factor,
            "stateSummary": summary,
            "findings": findings,
            "passed": not findings,
            "statesSample": states[:3] + states[-3:] if len(states) > 6 else states,
            "framesKept": bool(args.keep_frames or args.frame_dir),
            "frameDir": frame_dir.as_posix() if args.keep_frames or args.frame_dir else None,
        }
        if args.manifest:
            args.manifest.parent.mkdir(parents=True, exist_ok=True)
            args.manifest.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
        print(json.dumps(manifest, indent=2))
        return 0 if not findings else 1
    finally:
        if temp_dir and not args.keep_frames:
            temp_dir.cleanup()


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"capture_html_video.py: {exc}", file=sys.stderr)
        raise SystemExit(1)
