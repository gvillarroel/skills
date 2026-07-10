#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Create a deterministic HTML wireframe from an awsome-videos brief."""

from __future__ import annotations

import argparse
import html
import json
import re
from pathlib import Path
from typing import Any


SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
TEMPLATE = SKILL_DIR / "assets" / "templates" / "concept-renderer-template.html"

TIME_RE = re.compile(
    r"(?P<start>(?:\d+:)?\d{1,2}(?:\.\d+)?)\s*(?:-|to|–|—)\s*(?P<end>(?:\d+:)?\d{1,2}(?:\.\d+)?)"
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create a deterministic awsome-videos HTML concept renderer.")
    parser.add_argument("brief", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--title")
    parser.add_argument("--video-id")
    parser.add_argument("--duration", help="Duration in seconds or M:SS. Defaults to the brief runtime or final beat end.")
    parser.add_argument("--width", type=int, default=1280)
    parser.add_argument("--height", type=int, default=720)
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    return parser.parse_args()


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "concept-video"


def seconds(value: str) -> float:
    text = value.strip().lower()
    time_match = re.search(r"(?:\d+:)?\d{1,3}(?:\.\d+)?", text)
    if not time_match:
        raise ValueError(f"could not parse duration: {value}")
    token = time_match.group(0)
    if ":" in token:
        parts = [float(part) for part in token.split(":")]
        total = 0.0
        for part in parts:
            total = total * 60 + part
        return total
    return float(token)


def parse_time_range(value: str) -> tuple[float, float] | None:
    match = TIME_RE.search(value)
    if not match:
        return None
    start = seconds(match.group("start"))
    end = seconds(match.group("end"))
    if end <= start:
        end = start + 5
    return start, end


def extract_line_value(text: str, label: str) -> str:
    match = re.search(rf"^{re.escape(label)}:\s*(.+)$", text, flags=re.IGNORECASE | re.MULTILINE)
    return match.group(1).strip() if match else ""


def extract_title(text: str, fallback: str = "Concept Explainer") -> str:
    match = re.search(r"^#\s+(.+)$", text, flags=re.MULTILINE)
    if match:
        title = match.group(1).strip()
        if title and title != "<Title>":
            return title
    return fallback


def split_markdown_row(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def normalize_cell(value: str, fallback: str) -> str:
    clean = re.sub(r"<[^>]+>", "", value).strip()
    clean = re.sub(r"\s+", " ", clean)
    return clean or fallback


def pattern_for(purpose: str, visual: str) -> str:
    text = f"{purpose} {visual}".lower()
    if any(term in text for term in ["warning", "limitation", "failure", "tradeoff", "bad"]):
        return "warning-contrast"
    if any(term in text for term in ["code", "terminal", "snippet", "api"]):
        return "code-proof"
    if any(term in text for term in ["output", "result", "callback"]):
        return "output-callback"
    if any(term in text for term in ["diagram", "state", "mechanism", "flow"]):
        return "mechanism-trace"
    if any(term in text for term in ["source", "screenshot", "docs", "ui"]):
        return "source-proof"
    return "source-bound-mechanism"


def default_beats(duration: float) -> list[dict[str, Any]]:
    edges = [0, 5, 12, 20, 30, 40, 50, 62, duration]
    labels = [
        ("Claim or contradiction", "Logo plus proof visual", "Smash reveal", "Hard cut", "Hit plus bed"),
        ("Definition", "Diagram or source screenshot", "Punch-in", "Punch-in", "Voiceover duck"),
        ("Input enters", "Source surface", "Trace", "Match cut", "Tick accents"),
        ("Core mechanism", "State machine", "Build", "Hard cut", "Whoosh"),
        ("Output appears", "Result surface", "Pop", "Jump cut", "Light hit"),
        ("Contrast", "Good path versus bad path", "Split screen", "Smash cut", "Riser"),
        ("Limitation", "Warning proof", "Glitch", "Dropout", "Low impact"),
        ("Callback", "Full mechanism summary", "Zoom out", "Final cut", "Final tail"),
    ]
    beats: list[dict[str, Any]] = []
    for index, (purpose, visual, animation, transition, audio) in enumerate(labels):
        start = edges[index]
        end = max(start + 1, edges[index + 1])
        beats.append(
            {
                "start": start,
                "end": end,
                "purpose": purpose,
                "visual": visual,
                "animation": animation,
                "transition": transition,
                "audio": audio,
                "pattern": pattern_for(purpose, visual),
            }
        )
    return beats


def parse_beats(text: str, fallback_duration: float) -> list[dict[str, Any]]:
    beats: list[dict[str, Any]] = []
    for line in text.splitlines():
        if not line.strip().startswith("|"):
            continue
        cells = split_markdown_row(line)
        if len(cells) < 6 or cells[0].lower() in {"time", "---"}:
            continue
        time_range = parse_time_range(cells[0])
        if not time_range:
            continue
        start, end = time_range
        purpose = normalize_cell(cells[1], "Explain the next claim")
        visual = normalize_cell(cells[2], "Source-bound visual")
        animation = normalize_cell(cells[3], "Visible state change")
        transition = normalize_cell(cells[4], "Hard cut")
        audio = normalize_cell(cells[5], "Voiceover with bed")
        beats.append(
            {
                "start": start,
                "end": end,
                "purpose": purpose,
                "visual": visual,
                "animation": animation,
                "transition": transition,
                "audio": audio,
                "pattern": pattern_for(purpose, visual),
            }
        )
    return beats or default_beats(fallback_duration)


def infer_duration(text: str, beats: list[dict[str, Any]], requested: str | None) -> float:
    if requested:
        return seconds(requested)
    runtime = extract_line_value(text, "Runtime")
    if runtime:
        match = re.search(r"(?:\d+:)?\d{1,3}(?:\.\d+)?", runtime)
        if match:
            return seconds(match.group(0))
    if beats:
        return max(float(beat["end"]) for beat in beats)
    return 70.0


def render_html(
    brief_text: str,
    *,
    title: str | None = None,
    video_id: str | None = None,
    duration: str | None = None,
    width: int = 1280,
    height: int = 720,
) -> tuple[str, dict[str, Any]]:
    base_title = title or extract_title(brief_text)
    fallback_duration = seconds(duration) if duration else 70.0
    beats = parse_beats(brief_text, fallback_duration)
    duration_seconds = infer_duration(brief_text, beats, duration)
    if beats and beats[-1]["end"] < duration_seconds:
        beats[-1]["end"] = duration_seconds
    promise = extract_line_value(brief_text, "Promise") or "Explain the mechanism with proof, motion, and a practical rule."
    rendered = TEMPLATE.read_text(encoding="utf-8")
    replacements = {
        "__TITLE__": html.escape(base_title),
        "__VIDEO_ID__": html.escape(video_id or slugify(base_title)),
        "__DURATION__": f"{duration_seconds:g}",
        "__WIDTH__": str(width),
        "__HEIGHT__": str(height),
        "__PROMISE__": html.escape(promise),
        "__BEATS_JSON__": json.dumps(beats, ensure_ascii=True),
    }
    for old, new in replacements.items():
        rendered = rendered.replace(old, new)
    metadata = {
        "rendererMode": "wireframe",
        "finalPackageEligible": False,
        "title": base_title,
        "videoId": video_id or slugify(base_title),
        "durationSeconds": duration_seconds,
        "width": width,
        "height": height,
        "beats": len(beats),
        "patterns": sorted({str(beat["pattern"]) for beat in beats}),
    }
    return rendered, metadata


def create_renderer(args: argparse.Namespace) -> dict[str, Any]:
    if not args.brief.exists():
        raise FileNotFoundError(args.brief)
    if args.output.exists() and not args.force:
        return {
            "ok": True,
            "written": None,
            "skipped": str(args.output),
            "reason": "output exists; pass --force to overwrite",
        }
    brief_text = args.brief.read_text(encoding="utf-8", errors="ignore")
    rendered, metadata = render_html(
        brief_text,
        title=args.title,
        video_id=args.video_id,
        duration=args.duration,
        width=args.width,
        height=args.height,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(rendered, encoding="utf-8", newline="\n")
    return {
        "ok": True,
        "written": str(args.output),
        "skipped": None,
        "metadata": metadata,
    }


def main() -> int:
    args = parse_args()
    result = create_renderer(args)
    if args.json:
        print(json.dumps(result, indent=2))
    elif result.get("written"):
        meta = result.get("metadata", {})
        print(f"PASS awsome-videos renderer: {result['written']} ({meta.get('beats')} beats)")
    else:
        print(f"PASS awsome-videos renderer: skipped {result.get('skipped')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
