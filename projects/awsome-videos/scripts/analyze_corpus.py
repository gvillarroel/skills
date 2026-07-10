#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["pillow>=10.0.0"]
# ///
"""Analyze the local Awesome/Fireship corpus and build compact reference assets."""

from __future__ import annotations

import argparse
import json
import math
import re
import statistics
import subprocess
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont


TIMESTAMP_RE = re.compile(r"(\d\d):(\d\d):(\d\d)\.(\d\d\d)\s+-->\s+(\d\d):(\d\d):(\d\d)\.(\d\d\d)")
HTML_RE = re.compile(r"<[^>]+>")
WORD_RE = re.compile(r"[A-Za-z][A-Za-z0-9'+-]*")


@dataclass
class CorpusPaths:
    metadata_dir: Path
    downloads_dir: Path
    frames_dir: Path
    reports_dir: Path


def run_json(command: list[str]) -> dict[str, Any]:
    result = subprocess.run(command, check=True, text=True, capture_output=True)
    return json.loads(result.stdout)


def load_manifest(path: Path, source: str) -> list[dict[str, Any]]:
    rows = json.loads(path.read_text(encoding="utf-8"))
    for row in rows:
        row["source"] = source
    return rows


def seconds_from_timestamp(match: re.Match[str], offset: int) -> float:
    hours, minutes, seconds, millis = [int(match.group(offset + i)) for i in range(4)]
    return hours * 3600 + minutes * 60 + seconds + millis / 1000


def parse_vtt(path: Path | None) -> dict[str, Any]:
    if not path or not path.exists():
        return {"cue_count": 0, "word_count": 0, "words_per_minute": 0.0, "sample_text": ""}
    text = path.read_text(encoding="utf-8", errors="ignore")
    cue_count = 0
    active_seconds = 0.0
    spoken_lines: list[str] = []
    previous_line = ""
    for block in re.split(r"\n\s*\n", text):
        timestamp = TIMESTAMP_RE.search(block)
        if not timestamp:
            continue
        cue_count += 1
        start = seconds_from_timestamp(timestamp, 1)
        end = seconds_from_timestamp(timestamp, 5)
        duration = max(0.0, end - start)
        if duration < 0.05:
            continue
        active_seconds += duration
        raw_lines = [
            line
            for line in block.splitlines()
            if "-->" not in line and not line.startswith(("WEBVTT", "Kind:", "Language:"))
        ]
        timed_lines = [line for line in raw_lines if "<00:" in line or "<c>" in line]
        source_lines = timed_lines or raw_lines
        cue_lines: list[str] = []
        for line in source_lines:
            clean = HTML_RE.sub("", line).strip()
            if clean:
                cue_lines.append(clean)
        if cue_lines and previous_line and cue_lines[0] == previous_line:
            cue_lines = cue_lines[1:]
        cue_text = " ".join(cue_lines).strip()
        if cue_text and cue_text != previous_line:
            spoken_lines.append(cue_text)
            previous_line = cue_text
    words = WORD_RE.findall(" ".join(spoken_lines))
    minutes = active_seconds / 60 if active_seconds else 0
    return {
        "cue_count": cue_count,
        "word_count": len(words),
        "words_per_minute": round(len(words) / minutes, 1) if minutes else 0.0,
        "sample_text": " ".join(words[:70]),
    }


def index_downloads(downloads_dir: Path) -> dict[str, dict[str, Path]]:
    index: dict[str, dict[str, Path]] = defaultdict(dict)
    for path in downloads_dir.rglob("*"):
        if not path.is_file():
            continue
        match = re.search(r"-([A-Za-z0-9_-]{11})-", path.name)
        if not match:
            continue
        video_id = match.group(1)
        suffix = path.suffix.lower()
        if suffix == ".mp4":
            index[video_id]["video"] = path
        elif suffix == ".jpg":
            index[video_id]["thumbnail"] = path
        elif suffix == ".vtt":
            if ".en-US." in path.name:
                index[video_id]["vtt"] = path
            elif ".en." in path.name and "vtt" not in index[video_id]:
                index[video_id]["vtt"] = path
            elif ".en-orig." in path.name and "vtt" not in index[video_id]:
                index[video_id]["vtt"] = path
    return index


def probe_video(path: Path) -> dict[str, Any]:
    data = run_json(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration:stream=width,height,avg_frame_rate",
            "-of",
            "json",
            str(path),
        ]
    )
    stream = next((s for s in data.get("streams", []) if s.get("width")), {})
    duration = float(data.get("format", {}).get("duration") or 0)
    return {
        "duration": duration,
        "width": stream.get("width"),
        "height": stream.get("height"),
        "avg_frame_rate": stream.get("avg_frame_rate"),
    }


def raw_video_metrics(path: Path, sample_fps: float = 1.0, width: int = 80, height: int = 45) -> dict[str, Any]:
    frame_size = width * height * 3
    command = [
        "ffmpeg",
        "-hide_banner",
        "-loglevel",
        "error",
        "-i",
        str(path),
        "-vf",
        f"fps={sample_fps},scale={width}:{height},format=rgb24",
        "-an",
        "-f",
        "rawvideo",
        "-",
    ]
    process = subprocess.Popen(command, stdout=subprocess.PIPE)
    assert process.stdout is not None
    previous: bytes | None = None
    frame_count = 0
    diffs: list[float] = []
    brightness_values: list[float] = []
    colorfulness_values: list[float] = []
    red_bias = 0
    blue_bias = 0
    green_bias = 0
    dark_frames = 0

    while True:
        frame = process.stdout.read(frame_size)
        if len(frame) < frame_size:
            break
        frame_count += 1
        total_luma = 0.0
        rg_values: list[float] = []
        yb_values: list[float] = []
        red_total = green_total = blue_total = 0
        for i in range(0, frame_size, 3):
            r, g, b = frame[i], frame[i + 1], frame[i + 2]
            red_total += r
            green_total += g
            blue_total += b
            total_luma += 0.2126 * r + 0.7152 * g + 0.0722 * b
            rg_values.append(float(r - g))
            yb_values.append(float(((r + g) / 2) - b))
        pixel_count = width * height
        brightness = total_luma / pixel_count
        brightness_values.append(brightness)
        if brightness < 65:
            dark_frames += 1
        if red_total > blue_total * 1.12 and red_total > green_total * 1.05:
            red_bias += 1
        elif blue_total > red_total * 1.12 and blue_total > green_total * 1.05:
            blue_bias += 1
        elif green_total > red_total * 1.08 and green_total > blue_total * 1.08:
            green_bias += 1
        rg_std = statistics.pstdev(rg_values) if len(rg_values) > 1 else 0.0
        yb_std = statistics.pstdev(yb_values) if len(yb_values) > 1 else 0.0
        rg_mean = statistics.fmean(rg_values)
        yb_mean = statistics.fmean(yb_values)
        colorfulness_values.append(math.sqrt(rg_std**2 + yb_std**2) + 0.3 * math.sqrt(rg_mean**2 + yb_mean**2))
        if previous is not None:
            diff = sum(abs(a - b) for a, b in zip(frame, previous)) / (frame_size * 255)
            diffs.append(diff)
        previous = frame
    process.stdout.close()
    return_code = process.wait()
    if return_code != 0:
        raise RuntimeError(f"ffmpeg failed for {path}")

    diff_mean = statistics.fmean(diffs) if diffs else 0.0
    diff_p95 = quantile(diffs, 0.95)
    cut_threshold = max(0.18, diff_mean * 2.4)
    cut_count = sum(1 for value in diffs if value >= cut_threshold)
    minutes = max(frame_count / (sample_fps * 60), 1 / 60)
    dominant_bias = max(
        [("red", red_bias), ("blue", blue_bias), ("green", green_bias), ("neutral", frame_count - red_bias - blue_bias - green_bias)],
        key=lambda item: item[1],
    )[0]
    return {
        "sampled_frames": frame_count,
        "diff_mean": round(diff_mean, 4),
        "diff_p95": round(diff_p95, 4),
        "cut_proxy_count": cut_count,
        "cut_proxy_per_minute": round(cut_count / minutes, 2),
        "brightness_mean": round(statistics.fmean(brightness_values), 1) if brightness_values else 0.0,
        "dark_frame_ratio": round(dark_frames / frame_count, 3) if frame_count else 0.0,
        "colorfulness_mean": round(statistics.fmean(colorfulness_values), 1) if colorfulness_values else 0.0,
        "dominant_color_bias": dominant_bias,
    }


def quantile(values: list[float], q: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    idx = min(len(ordered) - 1, max(0, int(round((len(ordered) - 1) * q))))
    return ordered[idx]


def classify_video(row: dict[str, Any], metrics: dict[str, Any], transcript: dict[str, Any]) -> dict[str, str]:
    title = (row.get("title") or "").lower()
    description = (row.get("description") or "").lower()
    text = f"{title} {description}"
    duration = float(row.get("duration") or metrics.get("duration") or 0)
    cut_rate = metrics.get("cut_proxy_per_minute", 0.0)
    colorfulness = metrics.get("colorfulness_mean", 0.0)
    wpm = transcript.get("words_per_minute", 0.0)

    if any(term in text for term in ["100 seconds", "in 100 seconds", "explained"]):
        video_type = "compressed explainer"
    elif any(term in text for term in ["news", "weird", "happened", "released", "dead", "breaking"]):
        video_type = "trend/news commentary"
    elif any(term in text for term in ["i tried", "i built", "i read", "how i", "vibe coding"]):
        video_type = "experiment/editorial"
    elif any(term in text for term in ["course", "tutorial", "learn", "build", "guide"]):
        video_type = "tutorial/overview"
    else:
        video_type = "opinionated tech explainer"

    if cut_rate >= 8:
        transition_profile = "rapid hard cuts and inserts"
    elif cut_rate >= 4:
        transition_profile = "steady jump cuts with visual punctuations"
    else:
        transition_profile = "longer screen-recording or talking-head beats"

    if colorfulness >= 62:
        visual_style = "meme-rich saturated montage"
    elif metrics.get("dark_frame_ratio", 0.0) > 0.35:
        visual_style = "dark UI/code/editorial palette"
    elif metrics.get("dominant_color_bias") in {"red", "blue", "green"}:
        visual_style = f"{metrics.get('dominant_color_bias')} accent UI montage"
    else:
        visual_style = "neutral UI/code montage"

    if wpm >= 190:
        script_style = "very dense voiceover, joke/claim every beat"
    elif wpm >= 155:
        script_style = "fast explanatory narration"
    else:
        script_style = "measured tutorial narration"

    if duration <= 240:
        pacing = "short burst"
    elif duration <= 540:
        pacing = "standard short-form essay"
    else:
        pacing = "extended essay/tutorial"

    return {
        "video_type": video_type,
        "transition_profile": transition_profile,
        "visual_style": visual_style,
        "script_style": script_style,
        "pacing": pacing,
    }


def slug(value: str) -> str:
    value = re.sub(r"[^a-zA-Z0-9]+", "-", value.strip().lower())
    return value.strip("-")[:64] or "video"


def extract_example_frames(video_path: Path, output_dir: Path, duration: float) -> list[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    times = [duration * ratio for ratio in (0.06, 0.18, 0.34, 0.52, 0.70, 0.88)]
    frames: list[Path] = []
    for index, timestamp in enumerate(times, 1):
        target = output_dir / f"frame-{index:02d}.jpg"
        if target.exists():
            frames.append(target)
            continue
        subprocess.run(
            [
                "ffmpeg",
                "-hide_banner",
                "-loglevel",
                "error",
                "-ss",
                f"{max(0, timestamp):.2f}",
                "-i",
                str(video_path),
                "-frames:v",
                "1",
                "-vf",
                "scale=320:180",
                "-q:v",
                "3",
                str(target),
            ],
            check=True,
        )
        frames.append(target)
    return frames


def make_contact_sheet(frame_sets: list[tuple[str, list[Path]]], output_path: Path) -> None:
    cell_w, cell_h = 320, 180
    label_h = 34
    cols = 3
    rows = math.ceil(len(frame_sets) / cols)
    sheet = Image.new("RGB", (cols * cell_w, rows * (cell_h + label_h)), "#111111")
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.load_default()
    for idx, (label, frames) in enumerate(frame_sets):
        if not frames:
            continue
        frame = Image.open(frames[min(2, len(frames) - 1)]).convert("RGB")
        x = (idx % cols) * cell_w
        y = (idx // cols) * (cell_h + label_h)
        sheet.paste(frame, (x, y))
        draw.rectangle([x, y + cell_h, x + cell_w, y + cell_h + label_h], fill="#1d1d1d")
        draw.text((x + 8, y + cell_h + 9), label[:48], fill="#f2f2f2", font=font)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(output_path, quality=86)


def choose_examples(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    examples: list[dict[str, Any]] = []
    by_channel: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        by_channel[row["source"]].append(row)
    for channel, items in by_channel.items():
        examples.append(max(items, key=lambda r: r["visual_metrics"]["cut_proxy_per_minute"]))
        examples.append(max(items, key=lambda r: r["visual_metrics"]["colorfulness_mean"]))
        examples.append(max(items, key=lambda r: r["transcript"]["words_per_minute"]))
        examples.append(max(items, key=lambda r: r["duration"] or 0))
    deduped = []
    seen = set()
    for row in examples:
        if row["id"] not in seen:
            seen.add(row["id"])
            deduped.append(row)
    return deduped[:10]


def aggregate(rows: list[dict[str, Any]]) -> dict[str, Any]:
    summary: dict[str, Any] = {
        "total_videos": len(rows),
        "channels": {},
        "types": Counter(r["classification"]["video_type"] for r in rows),
        "visual_styles": Counter(r["classification"]["visual_style"] for r in rows),
        "transition_profiles": Counter(r["classification"]["transition_profile"] for r in rows),
        "script_styles": Counter(r["classification"]["script_style"] for r in rows),
    }
    for channel, items in defaultdict(list, {k: [r for r in rows if r["source"] == k] for k in {r["source"] for r in rows}}).items():
        summary["channels"][channel] = {
            "count": len(items),
            "duration_min_total": round(sum((r["duration"] or 0) for r in items) / 60, 1),
            "median_duration_sec": round(statistics.median(r["duration"] or 0 for r in items), 1),
            "median_cut_proxy_per_min": round(statistics.median(r["visual_metrics"]["cut_proxy_per_minute"] for r in items), 2),
            "median_words_per_min": round(statistics.median(r["transcript"]["words_per_minute"] for r in items), 1),
            "top_terms": top_terms(items),
        }
    for key in ("types", "visual_styles", "transition_profiles", "script_styles"):
        summary[key] = dict(summary[key].most_common())
    return summary


def top_terms(rows: list[dict[str, Any]]) -> list[tuple[str, int]]:
    stop = {
        "the",
        "and",
        "for",
        "with",
        "that",
        "this",
        "you",
        "your",
        "are",
        "but",
        "from",
        "into",
        "have",
        "has",
        "just",
        "new",
        "now",
        "why",
        "how",
        "what",
        "video",
    }
    counter: Counter[str] = Counter()
    for row in rows:
        words = WORD_RE.findall(f"{row.get('title', '')} {row.get('description', '')}".lower())
        counter.update(word for word in words if len(word) > 2 and word not in stop)
    return counter.most_common(18)


def write_markdown(summary: dict[str, Any], examples: list[dict[str, Any]], output_path: Path) -> None:
    lines = [
        "# Awesome/Fireship Corpus Analysis",
        "",
        "Window: 2025-07-06 through 2026-07-06 inclusive.",
        "",
        f"Public videos analyzed: {summary['total_videos']}.",
        "",
        "## Channel Metrics",
        "",
        "| Channel | Videos | Minutes | Median duration | Median cuts/min | Median WPM |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for channel, data in sorted(summary["channels"].items()):
        lines.append(
            f"| {channel} | {data['count']} | {data['duration_min_total']} | {data['median_duration_sec']}s | "
            f"{data['median_cut_proxy_per_min']} | {data['median_words_per_min']} |"
        )
    lines += [
        "",
        "## Distribution",
        "",
        "Video types: " + "; ".join(f"{k} ({v})" for k, v in summary["types"].items()),
        "",
        "Transition profiles: " + "; ".join(f"{k} ({v})" for k, v in summary["transition_profiles"].items()),
        "",
        "Script styles: " + "; ".join(f"{k} ({v})" for k, v in summary["script_styles"].items()),
        "",
        "## Example Contact Sheet",
        "",
        "![Representative frames](../frames/contact-sheets/representative-examples.jpg)",
        "",
        "## Representative Examples",
        "",
    ]
    for row in examples:
        vm = row["visual_metrics"]
        tr = row["transcript"]
        lines.extend(
            [
                f"### {row['source']}: {row['title']}",
                "",
                f"- URL: {row['url']}",
                f"- Date: {row['upload_date']}; duration: {row['duration_string']}",
                f"- Type: {row['classification']['video_type']}; visual: {row['classification']['visual_style']}",
                f"- Transitions: {row['classification']['transition_profile']} ({vm['cut_proxy_per_minute']} cut proxies/min)",
                f"- Script: {row['classification']['script_style']} ({tr['words_per_minute']} WPM)",
                "",
            ]
        )
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def analyze(paths: CorpusPaths) -> None:
    rows = load_manifest(paths.metadata_dir / "awesome-manifest.json", "awesome") + load_manifest(
        paths.metadata_dir / "fireship-manifest.json", "fireship"
    )
    downloads = index_downloads(paths.downloads_dir)
    analyzed: list[dict[str, Any]] = []
    for idx, row in enumerate(rows, 1):
        video_id = row["id"]
        assets = downloads.get(video_id, {})
        video_path = assets.get("video")
        if not video_path:
            print(f"missing video for {video_id}")
            continue
        safe_title = (row.get("title") or "").encode("ascii", "replace").decode("ascii")
        print(f"[{idx:03d}/{len(rows)}] {row['source']} {video_id} {safe_title}", flush=True)
        probe = probe_video(video_path)
        transcript = parse_vtt(assets.get("vtt"))
        visual_metrics = raw_video_metrics(video_path)
        duration = row.get("duration") or probe.get("duration")
        if duration and transcript.get("word_count"):
            transcript["words_per_minute"] = round(transcript["word_count"] / (float(duration) / 60), 1)
        row.update(
            {
                "video_path": str(video_path),
                "thumbnail_path": str(assets.get("thumbnail", "")),
                "vtt_path": str(assets.get("vtt", "")),
                "duration": duration,
                "probe": probe,
                "transcript": transcript,
                "visual_metrics": visual_metrics,
            }
        )
        row["classification"] = classify_video(row, visual_metrics, transcript)
        analyzed.append(row)

    paths.reports_dir.mkdir(parents=True, exist_ok=True)
    (paths.reports_dir / "corpus-analysis.json").write_text(json.dumps(analyzed, indent=2, ensure_ascii=False), encoding="utf-8")
    summary = aggregate(analyzed)
    (paths.reports_dir / "corpus-summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")

    examples = choose_examples(analyzed)
    frame_sets: list[tuple[str, list[Path]]] = []
    for row in examples:
        video_path = Path(row["video_path"])
        label = f"{row['source']} | {row['classification']['video_type']}"
        frame_dir = paths.frames_dir / row["source"] / f"{row['upload_date']}-{row['id']}-{slug(row['title'])}"
        frames = extract_example_frames(video_path, frame_dir, float(row["duration"] or row["probe"]["duration"] or 0))
        row["example_frame_dir"] = str(frame_dir)
        frame_sets.append((label, frames))
    make_contact_sheet(frame_sets, paths.frames_dir / "contact-sheets" / "representative-examples.jpg")
    write_markdown(summary, examples, paths.reports_dir / "corpus-analysis.md")
    (paths.reports_dir / "representative-examples.json").write_text(json.dumps(examples, indent=2, ensure_ascii=False), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--metadata-dir", default="projects/awsome-videos/artifacts/metadata")
    parser.add_argument("--downloads-dir", default="projects/awsome-videos/artifacts/downloads")
    parser.add_argument("--frames-dir", default="projects/awsome-videos/artifacts/frames")
    parser.add_argument("--reports-dir", default="projects/awsome-videos/artifacts/reports")
    args = parser.parse_args()
    analyze(
        CorpusPaths(
            metadata_dir=Path(args.metadata_dir),
            downloads_dir=Path(args.downloads_dir),
            frames_dir=Path(args.frames_dir),
            reports_dir=Path(args.reports_dir),
        )
    )


if __name__ == "__main__":
    main()
