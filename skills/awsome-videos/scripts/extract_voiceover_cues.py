#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Extract timed voiceover cues from an awsome-videos brief."""

from __future__ import annotations

import argparse
import csv
import io
import json
import re
import sys
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True

TIME_TOKEN_RE = r"(?:\d{1,2}:)?\d{1,2}:\d{2}|\d+(?:\.\d+)?s?"
TIME_RANGE_RE = re.compile(
    rf"(?P<start>{TIME_TOKEN_RE})\s*(?:->|-|to|through)\s*(?P<end>{TIME_TOKEN_RE})",
    re.IGNORECASE,
)
CUE_LINE_RE = re.compile(
    rf"^\s*(?:[-*+]\s*)?(?P<start>{TIME_TOKEN_RE})\s*(?:->|-|to|through)\s*"
    rf"(?P<end>{TIME_TOKEN_RE})\s*(?:[:|]\s*)?(?P<text>.+?)\s*$",
    re.IGNORECASE,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Extract timed voiceover cues from a production brief.")
    parser.add_argument("brief", type=Path)
    parser.add_argument("--format", choices=["json", "srt", "csv"], default="json")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--min-cues", type=int, default=1)
    parser.add_argument("--expect-duration", type=float)
    parser.add_argument("--duration-tolerance", type=float, default=1.0)
    parser.add_argument("--cue-time-tolerance", type=float, default=0.05)
    parser.add_argument("--require-beat-match", action="store_true")
    parser.add_argument("--allow-overlap", action="store_true")
    parser.add_argument("--json", action="store_true", help="Alias for --format json.")
    return parser.parse_args()


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def extract_heading_section(text: str, heading_terms: list[str]) -> str:
    lines = text.splitlines()
    start: int | None = None
    level = 0
    for index, line in enumerate(lines):
        match = re.match(r"^(#{2,6})\s+(.+?)\s*$", line)
        if not match:
            continue
        heading = match.group(2).strip().lower()
        if any(term in heading for term in heading_terms):
            start = index + 1
            level = len(match.group(1))
            break
    if start is None:
        return ""

    end = len(lines)
    for index in range(start, len(lines)):
        match = re.match(r"^(#{2,6})\s+(.+?)\s*$", lines[index])
        if match and len(match.group(1)) <= level:
            end = index
            break
    return "\n".join(lines[start:end]).strip()


def parse_time_seconds(value: str) -> float:
    raw = value.strip().lower().rstrip("s")
    if ":" not in raw:
        return float(raw)
    parts = [float(part) for part in raw.split(":")]
    if len(parts) == 2:
        minutes, seconds = parts
        return minutes * 60 + seconds
    if len(parts) == 3:
        hours, minutes, seconds = parts
        return hours * 3600 + minutes * 60 + seconds
    raise ValueError(f"unsupported time value: {value}")


def clean_spoken_text(text: str) -> str:
    text = re.sub(r"\s+", " ", text).strip()
    text = re.sub(r"^\*\*(.*?)\*\*$", r"\1", text)
    return text


def split_markdown_row(line: str) -> list[str]:
    stripped = line.strip()
    if not stripped.startswith("|") or not stripped.endswith("|"):
        return []
    return [cell.strip() for cell in stripped.strip("|").split("|")]


def is_separator_row(cells: list[str]) -> bool:
    return bool(cells) and all(re.fullmatch(r":?-{3,}:?", cell.strip()) for cell in cells)


def find_column(headers: list[str], terms: list[str]) -> int | None:
    lowered = [header.lower() for header in headers]
    for index, header in enumerate(lowered):
        if any(term in header for term in terms):
            return index
    return None


def parse_time_range(value: str) -> dict[str, Any] | None:
    match = TIME_RANGE_RE.search(value)
    if not match:
        return None
    start = match.group("start")
    end = match.group("end")
    return {
        "start": start,
        "end": end,
        "startSeconds": parse_time_seconds(start),
        "endSeconds": parse_time_seconds(end),
    }


def extract_beat_ranges(text: str) -> list[dict[str, Any]]:
    lines = text.splitlines()
    beat_ranges: list[dict[str, Any]] = []
    for index, line in enumerate(lines):
        headers = split_markdown_row(line)
        if not headers:
            continue
        next_cells = split_markdown_row(lines[index + 1]) if index + 1 < len(lines) else []
        if not is_separator_row(next_cells):
            continue
        time_column = find_column(headers, ["time", "timestamp", "range"])
        script_column = find_column(headers, ["script", "purpose", "voiceover", "narration", "beat"])
        if time_column is None or script_column is None:
            continue
        row_index = index + 2
        while row_index < len(lines):
            cells = split_markdown_row(lines[row_index])
            if not cells or is_separator_row(cells):
                break
            value = cells[time_column] if time_column < len(cells) else ""
            parsed = parse_time_range(value)
            if parsed:
                parsed["index"] = len(beat_ranges) + 1
                parsed["raw"] = value
                beat_ranges.append(parsed)
            row_index += 1
        if beat_ranges:
            break
    return beat_ranges


def extract_cues(text: str) -> dict[str, Any]:
    section = extract_heading_section(text, ["voiceover", "narration draft", "spoken script", "script draft"])
    cues: list[dict[str, Any]] = []
    unparsed_lines: list[str] = []
    if section:
        for raw_line in section.splitlines():
            line = raw_line.strip()
            if not line:
                continue
            match = CUE_LINE_RE.match(line)
            if not match:
                unparsed_lines.append(line)
                continue
            start_seconds = parse_time_seconds(match.group("start"))
            end_seconds = parse_time_seconds(match.group("end"))
            cue_text = clean_spoken_text(match.group("text"))
            cues.append(
                {
                    "index": len(cues) + 1,
                    "start": match.group("start"),
                    "end": match.group("end"),
                    "startSeconds": start_seconds,
                    "endSeconds": end_seconds,
                    "durationSeconds": round(end_seconds - start_seconds, 3),
                    "text": cue_text,
                    "wordCount": len(re.findall(r"\b[\w'-]+\b", cue_text)),
                }
            )
    return {
        "sectionPresent": bool(section),
        "cues": cues,
        "unparsedLines": unparsed_lines,
    }


def validate_cues(
    cues: list[dict[str, Any]],
    unparsed_lines: list[str],
    beat_ranges: list[dict[str, Any]],
    min_cues: int,
    expect_duration: float | None,
    duration_tolerance: float,
    cue_time_tolerance: float,
    require_beat_match: bool,
    allow_overlap: bool,
) -> tuple[list[str], list[str], list[str]]:
    failures: list[str] = []
    warnings: list[str] = []
    beat_cue_mismatches: list[str] = []
    if len(cues) < min_cues:
        failures.append(f"expected at least {min_cues} voiceover cues, found {len(cues)}")
    if unparsed_lines:
        failures.append("unparsed voiceover cue lines: " + "; ".join(unparsed_lines[:5]))
    if require_beat_match:
        if not beat_ranges:
            failures.append("no timed beat table ranges found for voiceover cue matching")
        elif len(beat_ranges) != len(cues):
            failures.append(f"voiceover cue count {len(cues)} does not match timed beat count {len(beat_ranges)}")

    previous_end = -1.0
    for cue in cues:
        start = float(cue["startSeconds"])
        end = float(cue["endSeconds"])
        if end <= start:
            failures.append(f"cue {cue['index']} has non-positive duration")
        if not allow_overlap and start < previous_end:
            failures.append(f"cue {cue['index']} overlaps the previous cue")
        if cue["wordCount"] < 3:
            warnings.append(f"cue {cue['index']} is very short")
        previous_end = max(previous_end, end)

    if require_beat_match and beat_ranges and cues:
        for cue, beat in zip(cues, beat_ranges):
            start_delta = abs(float(cue["startSeconds"]) - float(beat["startSeconds"]))
            end_delta = abs(float(cue["endSeconds"]) - float(beat["endSeconds"]))
            if start_delta > cue_time_tolerance or end_delta > cue_time_tolerance:
                beat_cue_mismatches.append(
                    f"cue {cue['index']} {cue['start']}-{cue['end']} does not match "
                    f"beat {beat['index']} {beat['start']}-{beat['end']}"
                )
        if beat_cue_mismatches:
            failures.append("voiceover cues do not match timed beats: " + "; ".join(beat_cue_mismatches[:5]))

    if expect_duration is not None and cues:
        final_end = float(cues[-1]["endSeconds"])
        delta = abs(final_end - expect_duration)
        if delta > duration_tolerance:
            failures.append(
                f"voiceover final cue ends at {final_end:g}s, expected {expect_duration:g}s "
                f"+/- {duration_tolerance:g}s"
            )
    return failures, warnings, beat_cue_mismatches


def format_timestamp(seconds: float) -> str:
    milliseconds = int(round(seconds * 1000))
    hours, remainder = divmod(milliseconds, 3_600_000)
    minutes, remainder = divmod(remainder, 60_000)
    secs, millis = divmod(remainder, 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def render_srt(cues: list[dict[str, Any]]) -> str:
    blocks = []
    for cue in cues:
        blocks.append(
            "\n".join(
                [
                    str(cue["index"]),
                    f"{format_timestamp(cue['startSeconds'])} --> {format_timestamp(cue['endSeconds'])}",
                    cue["text"],
                ]
            )
        )
    return "\n\n".join(blocks) + ("\n" if blocks else "")


def render_csv(cues: list[dict[str, Any]]) -> str:
    output = io.StringIO()
    writer = csv.DictWriter(
        output,
        fieldnames=["index", "start", "end", "startSeconds", "endSeconds", "durationSeconds", "wordCount", "text"],
        lineterminator="\n",
    )
    writer.writeheader()
    writer.writerows(cues)
    return output.getvalue()


def build_result(args: argparse.Namespace) -> dict[str, Any]:
    text = read_text(args.brief)
    extracted = extract_cues(text)
    beat_ranges = extract_beat_ranges(text)
    cues = extracted["cues"]
    failures, warnings, beat_cue_mismatches = validate_cues(
        cues,
        extracted["unparsedLines"],
        beat_ranges,
        args.min_cues,
        args.expect_duration,
        args.duration_tolerance,
        args.cue_time_tolerance,
        args.require_beat_match,
        args.allow_overlap,
    )
    return {
        "ok": not failures,
        "source": str(args.brief),
        "sectionPresent": extracted["sectionPresent"],
        "cueCount": len(cues),
        "beatCount": len(beat_ranges),
        "beatMatchRequired": args.require_beat_match,
        "beatCueMismatches": beat_cue_mismatches,
        "finalCueEndSeconds": cues[-1]["endSeconds"] if cues else None,
        "coveredDurationSeconds": round(sum(float(cue["durationSeconds"]) for cue in cues), 3),
        "unparsedLines": extracted["unparsedLines"],
        "failures": failures,
        "warnings": warnings,
        "cues": cues,
    }


def write_output(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")


def main() -> int:
    args = parse_args()
    if args.json:
        args.format = "json"
    result = build_result(args)
    if args.format == "json":
        content = json.dumps(result, indent=2) + "\n"
    elif args.format == "srt":
        content = render_srt(result["cues"])
    else:
        content = render_csv(result["cues"])

    if args.output:
        write_output(args.output, content)
        print(
            f"{'PASS' if result['ok'] else 'FAIL'} awsome-videos voiceover cues: "
            f"{result['cueCount']} cues -> {args.output}"
        )
    else:
        print(content, end="")
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
