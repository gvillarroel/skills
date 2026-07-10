#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Validate an awsome-videos production brief."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


TIME_RANGE_RES = [
    re.compile(
        r"\b(?:\d{1,2}:)?\d{1,2}:\d{2}\s*(?:-|to|through|->)\s*(?:\d{1,2}:)?\d{1,2}:\d{2}\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"\b\d{1,3}(?:\.\d+)?\s*s\s*(?:-|to|through|->)\s*\d{1,3}(?:\.\d+)?\s*s\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"\b\d{1,3}(?:\.\d+)?\s*(?:-|to|through|->)\s*\d{1,3}(?:\.\d+)?\s*s\b",
        re.IGNORECASE,
    ),
]

CHECKS = {
    "title_or_promise": ["title", "promise", "premise", "thesis"],
    "audience": ["audience", "viewer", "prerequisite", "assumption"],
    "hook": ["hook", "cold open", "opening", "first 5", "first five"],
    "script": ["script", "narration", "voiceover", "line", "beat"],
    "visuals": ["visual", "shot", "frame", "screen", "code", "ui", "image", "diagram"],
    "animation": ["animation", "motion", "zoom", "pan", "scroll", "overlay", "highlight"],
    "transitions": ["transition", "hard cut", "jump cut", "match cut", "wipe", "morph", "glitch", "smash cut"],
    "audio": ["audio", "music", "sfx", "sound", "bed", "whoosh", "hit", "riser", "duck"],
    "assets": ["asset", "source", "screenshot", "logo", "clip", "thumbnail", "diagram"],
    "evaluation": ["evaluate", "validation", "checklist", "expected", "pass", "review"],
}

REQUIRED_BEAT_COLUMNS = {
    "time": ["time", "timestamp", "range"],
    "script": ["script", "purpose", "voiceover", "narration", "beat"],
    "visual": ["visual", "shot", "frame", "screen"],
    "animation": ["animation", "motion"],
    "transition": ["transition", "cut"],
    "audio": ["audio", "music", "sfx", "sound"],
}

GENERIC_FIELD_VALUES = {
    "script": {"more", "beat", "script", "narration", "voiceover", "explain"},
    "visual": {"text", "visual", "image", "screen", "slide", "show text", "graphic"},
    "animation": {"fade", "animation", "motion", "move", "none", "static"},
    "transition": {"cut", "transition", "none"},
    "audio": {"music", "audio", "sound", "sfx", "bed", "none"},
}

REQUIRED_LABELED_FIELDS = [
    "Promise",
    "Audience",
    "Format",
    "Runtime",
    "Cold-open line",
    "First visual",
    "Audio cue",
]

MIN_WORD_LABELED_FIELDS = {
    "Cold-open line": 5,
    "First visual": 5,
    "Audio cue": 4,
}

MIN_VOICEOVER_WORDS = 5

GENERIC_VOICEOVER_PHRASES = [
    "open with the claim",
    "name the consequence",
    "define the concept",
    "one compressed sentence",
    "show the first mechanism step",
    "show the state change",
    "prove the practical output",
    "contrast the failure path",
    "controlled path",
    "give the rule of thumb",
    "viewers can reuse",
    "callback to the hook",
    "close on the practical rule",
    "explain the topic",
    "explain the concept",
    "talk about the topic",
    "describe the concept",
]

GENERIC_VOICEOVER_PATTERNS = [
    re.compile(r"\bthis (?:beat|part|section|video) (?:explains|shows|covers)\b", re.IGNORECASE),
    re.compile(r"\b(?:in|with) (?:a )?(?:clear|simple|basic) (?:and )?(?:clear|simple|basic)? ?way\b", re.IGNORECASE),
]

SPECIFIC_SINGLE_WORD_VALUES = {
    "script": {"definition", "claim", "proof", "output", "contrast", "warning", "callback", "hook"},
    "animation": {"pan", "zoom", "scroll", "trace", "highlight"},
    "transition": {"wipe", "glitch"},
    "audio": {"whoosh", "riser", "dropout", "stinger", "hit", "tail", "tick"},
}

SOURCE_SECTION_TERMS = [
    "visual source plan",
    "assets",
    "assets and sources",
    "source plan",
]

SOURCE_LINK_LABEL_RE = re.compile(
    r"^[ \t]*(?:[-*+][ \t]*)?(?:\*\*)?(?:source links?|sources?|references?|citations?)(?:\*\*)?[ \t]*:[ \t]*(?:\*\*)?[ \t]*(.*)$",
    re.IGNORECASE,
)

SOURCE_LINK_RE = re.compile(
    r"\b(?:https?://|www\.)[^\s)<>\"]+|\b(?:[A-Za-z0-9-]+\.)+(?:com|org|net|dev|io|ai|gov|edu|cloud|app)\b[^\s)<>\"]*",
    re.IGNORECASE,
)

GENERIC_SOURCE_LINK_VALUES = [
    "official docs",
    "primary sources",
    "source page",
    "docs page",
    "documentation",
    "screenshots",
]


def count_terms(text: str, terms: list[str]) -> int:
    return sum(1 for term in terms if term in text)


def find_time_ranges(text: str) -> list[str]:
    ranges: list[str] = []
    seen: set[str] = set()
    for pattern in TIME_RANGE_RES:
        for match in pattern.findall(text):
            normalized = re.sub(r"\s+", "", match.lower())
            if normalized not in seen:
                seen.add(normalized)
                ranges.append(match)
    return ranges


def split_markdown_row(line: str) -> list[str]:
    stripped = line.strip()
    if not stripped.startswith("|") or not stripped.endswith("|"):
        return []
    return [cell.strip() for cell in stripped.strip("|").split("|")]


def is_separator_row(cells: list[str]) -> bool:
    return bool(cells) and all(re.fullmatch(r":?-{3,}:?", cell.strip()) for cell in cells)


def find_column(headers: list[str], terms: list[str], *, reject_id_column: bool = False) -> int | None:
    lowered = [header.lower() for header in headers]
    for index, header in enumerate(lowered):
        if reject_id_column and re.search(r"\bid\b", header):
            continue
        if any(term in header for term in terms):
            return index
    return None


def normalize_cell(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip().lower())


def is_specific_cell(role: str, value: str) -> bool:
    normalized = normalize_cell(value)
    if not normalized:
        return False
    if normalized in GENERIC_FIELD_VALUES.get(role, set()):
        return False
    if normalized in SPECIFIC_SINGLE_WORD_VALUES.get(role, set()):
        return True
    if role != "transition" and len(re.findall(r"[a-z0-9]+", normalized)) < 2:
        return False
    return True


def extract_labeled_value(text: str, label: str) -> str:
    pattern = re.compile(
        rf"^[ \t]*(?:[-*+][ \t]*)?(?:\*\*)?{re.escape(label)}(?:\*\*)?[ \t]*:[ \t]*(?:\*\*)?[ \t]*(.*)$",
        flags=re.IGNORECASE | re.MULTILINE,
    )
    match = pattern.search(text)
    if not match:
        return ""
    return re.sub(r"\*\*$", "", match.group(1).strip()).strip()


def validate_labeled_fields(text: str) -> dict[str, object]:
    missing: list[str] = []
    thin: list[str] = []
    values: dict[str, str] = {}
    for label in REQUIRED_LABELED_FIELDS:
        value = extract_labeled_value(text, label)
        values[label] = value
        if not value:
            missing.append(label)
            continue
        min_words = MIN_WORD_LABELED_FIELDS.get(label)
        if min_words is not None and len(re.findall(r"[A-Za-z0-9]+", value)) < min_words:
            thin.append(label)
    failures: list[str] = []
    if missing:
        failures.append("missing labeled field values: " + ", ".join(missing))
    if thin:
        failures.append("labeled field values are too thin: " + ", ".join(thin))
    return {
        "ok": not failures,
        "failures": failures,
        "missing": missing,
        "thin": thin,
        "values": values,
    }


def validate_timed_beat_table(text: str, min_beats: int) -> dict[str, object]:
    lines = text.splitlines()
    rows: list[dict[str, str]] = []
    missing_fields: list[str] = []
    generic_fields: list[str] = []
    found_required_table = False

    for index, line in enumerate(lines):
        headers = split_markdown_row(line)
        if not headers:
            continue
        next_cells = split_markdown_row(lines[index + 1]) if index + 1 < len(lines) else []
        if not is_separator_row(next_cells):
            continue

        column_indexes = {
            name: find_column(headers, terms, reject_id_column=name == "script")
            for name, terms in REQUIRED_BEAT_COLUMNS.items()
        }
        if any(value is None for value in column_indexes.values()):
            continue

        found_required_table = True
        row_index = index + 2
        while row_index < len(lines):
            cells = split_markdown_row(lines[row_index])
            if not cells or is_separator_row(cells):
                break
            row: dict[str, str] = {}
            for role, column in column_indexes.items():
                assert column is not None
                row[role] = cells[column] if column < len(cells) else ""
            rows.append(row)
            row_index += 1

    for row_number, row in enumerate(rows, start=1):
        if not find_time_ranges(row.get("time", "")):
            missing_fields.append(f"row {row_number} time")
        for role in ["script", "visual", "animation", "transition", "audio"]:
            value = row.get(role, "")
            if not value.strip():
                missing_fields.append(f"row {row_number} {role}")
            elif not is_specific_cell(role, value):
                generic_fields.append(f"row {row_number} {role}: {value}")

    failures: list[str] = []
    if not found_required_table:
        failures.append("missing timed beat table with time, script, visual, animation, transition, and audio columns")
    elif len(rows) < min_beats:
        failures.append(f"timed beat table needs at least {min_beats} rows, found {len(rows)}")
    if missing_fields:
        failures.append("timed beat table has missing fields: " + ", ".join(missing_fields[:8]))
    if generic_fields:
        failures.append("timed beat table has generic fields: " + ", ".join(generic_fields[:8]))

    return {
        "ok": not failures,
        "failures": failures,
        "table_rows": len(rows),
        "missing_fields": missing_fields,
        "generic_fields": generic_fields,
    }


def extract_voiceover_section(text: str) -> str:
    lines = text.splitlines()
    start: int | None = None
    for index, line in enumerate(lines):
        heading = line.strip().lower()
        if not heading.startswith("#"):
            continue
        if "style" in heading:
            continue
        if any(term in heading for term in ["voiceover", "narration draft", "spoken script", "script draft"]):
            start = index + 1
            break
    if start is None:
        return ""
    end = len(lines)
    for index in range(start, len(lines)):
        if re.match(r"^#{2,6}\s+\S", lines[index]):
            end = index
            break
    return "\n".join(lines[start:end]).strip()


def clean_voiceover_line(line: str) -> str:
    stripped = line.strip()
    if not stripped or is_separator_row(split_markdown_row(stripped)):
        return ""
    cells = split_markdown_row(stripped)
    if cells:
        stripped = " ".join(cells[1:] if len(cells) > 1 else cells)
    stripped = re.sub(r"^\s*(?:[-*+]|\d+[.)])\s*", "", stripped)
    for pattern in TIME_RANGE_RES:
        stripped = pattern.sub("", stripped, count=1)
    stripped = stripped.lstrip(":- \t")
    stripped = re.sub(r"\s+", " ", stripped).strip()
    return stripped


def normalize_voiceover_for_comparison(line: str) -> str:
    return " ".join(re.findall(r"[a-z0-9]+", line.lower()))


def find_generic_voiceover_lines(lines: list[str]) -> list[str]:
    generic: list[str] = []
    for index, line in enumerate(lines, start=1):
        normalized = normalize_voiceover_for_comparison(line)
        if any(phrase in normalized for phrase in GENERIC_VOICEOVER_PHRASES):
            generic.append(f"line {index}")
            continue
        if any(pattern.search(line) for pattern in GENERIC_VOICEOVER_PATTERNS):
            generic.append(f"line {index}")
    return generic


def find_duplicate_voiceover_lines(lines: list[str]) -> list[str]:
    seen: dict[str, int] = {}
    duplicates: list[str] = []
    for index, line in enumerate(lines, start=1):
        normalized = normalize_voiceover_for_comparison(line)
        if not normalized:
            continue
        previous = seen.get(normalized)
        if previous is not None:
            duplicates.append(f"line {index} duplicates line {previous}")
        else:
            seen[normalized] = index
    return duplicates


def validate_voiceover(text: str, required: bool, min_lines: int) -> dict[str, object]:
    section = extract_voiceover_section(text)
    lines = [clean_voiceover_line(line) for line in section.splitlines()] if section else []
    lines = [line for line in lines if line]
    thin = [
        f"line {index}"
        for index, line in enumerate(lines, start=1)
        if len(re.findall(r"[A-Za-z0-9]+", line)) < MIN_VOICEOVER_WORDS
    ]
    generic = find_generic_voiceover_lines(lines)
    duplicates = find_duplicate_voiceover_lines(lines)
    failures: list[str] = []
    if required and not section:
        failures.append("missing voiceover draft section")
    if required and len(lines) < min_lines:
        failures.append(f"voiceover draft needs at least {min_lines} lines, found {len(lines)}")
    if required and thin:
        failures.append("voiceover draft lines are too thin: " + ", ".join(thin[:8]))
    if required and generic:
        failures.append("voiceover draft lines are generic placeholders: " + ", ".join(generic[:8]))
    if required and duplicates:
        failures.append("voiceover draft repeats lines: " + ", ".join(duplicates[:8]))
    return {
        "ok": not failures,
        "failures": failures,
        "required": required,
        "line_count": len(lines),
        "thin_lines": thin,
        "generic_lines": generic,
        "duplicate_lines": duplicates,
        "section_present": bool(section),
    }


def extract_named_sections(text: str, heading_terms: list[str]) -> list[str]:
    lines = text.splitlines()
    sections: list[str] = []
    start: int | None = None
    start_level = 0
    for index, line in enumerate(lines):
        match = re.match(r"^(#{1,6})\s+(.+?)\s*$", line)
        if not match:
            continue
        level = len(match.group(1))
        heading = match.group(2).strip().lower()
        if start is not None and level <= start_level:
            sections.append("\n".join(lines[start:index]).strip())
            start = None
            start_level = 0
        if any(term in heading for term in heading_terms):
            start = index + 1
            start_level = level
    if start is not None:
        sections.append("\n".join(lines[start:]).strip())
    return [section for section in sections if section]


def extract_source_link_values(text: str) -> tuple[list[str], bool]:
    values: list[str] = []
    label_present = False
    lines = text.splitlines()
    for index, line in enumerate(lines):
        match = SOURCE_LINK_LABEL_RE.match(line)
        if not match:
            continue
        label_present = True
        value_parts = [match.group(1).strip()]
        row = index + 1
        while row < len(lines):
            continuation = lines[row]
            if not continuation.strip():
                break
            if re.match(r"^\s{2,}(?:[-*+]\s*)?\S", continuation) and SOURCE_LINK_RE.search(continuation):
                value_parts.append(continuation.strip())
                row += 1
                continue
            if re.match(r"^\s*(?:[-*+]\s*)?[A-Za-z][A-Za-z /-]{1,40}:\s*", continuation):
                break
            if re.match(r"^\s{2,}(?:[-*+]\s*)?\S", continuation):
                value_parts.append(continuation.strip())
                row += 1
                continue
            break
        value = " ".join(part for part in value_parts if part).strip()
        if value:
            values.append(value)
    return values, label_present


def normalize_source_link(link: str) -> str:
    return link.rstrip(".,;:")


def find_source_links(values: list[str]) -> list[str]:
    seen: set[str] = set()
    links: list[str] = []
    for value in values:
        for match in SOURCE_LINK_RE.finditer(value):
            link = normalize_source_link(match.group(0))
            normalized = link.lower()
            if normalized not in seen:
                seen.add(normalized)
                links.append(link)
    return links


def validate_source_links(text: str, required: bool) -> dict[str, object]:
    sections = extract_named_sections(text, SOURCE_SECTION_TERMS)
    scoped_text = "\n".join(sections) if sections else text
    values, label_present = extract_source_link_values(scoped_text)
    links = find_source_links(values)
    generic_values = [
        value
        for value in values
        if not find_source_links([value])
        and any(phrase in value.lower() for phrase in GENERIC_SOURCE_LINK_VALUES)
    ]
    failures: list[str] = []
    if required and not sections and not label_present:
        failures.append("missing visual source plan or source links section")
    if required and not label_present:
        failures.append("missing source links label")
    if required and not links:
        failures.append("source links need at least one concrete URL or domain")
    if required and generic_values:
        failures.append("source links include generic placeholders without concrete URLs or domains")
    return {
        "ok": not failures,
        "failures": failures,
        "required": required,
        "section_present": bool(sections),
        "label_present": label_present,
        "values": values,
        "generic_values": generic_values,
        "links": links,
        "link_count": len(links),
    }


def validate(
    text: str,
    min_beats: int,
    require_voiceover: bool = False,
    min_voiceover_lines: int | None = None,
    require_source_links: bool = False,
) -> dict[str, object]:
    normalized = text.lower()
    time_ranges = find_time_ranges(text)
    missing = [name for name, terms in CHECKS.items() if count_terms(normalized, terms) == 0]
    transition_hits = count_terms(normalized, CHECKS["transitions"])
    audio_hits = count_terms(normalized, CHECKS["audio"])
    visual_hits = count_terms(normalized, CHECKS["visuals"])
    animation_hits = count_terms(normalized, CHECKS["animation"])
    labeled_fields = validate_labeled_fields(text)
    beat_table = validate_timed_beat_table(text, min_beats)
    voiceover = validate_voiceover(text, require_voiceover, min_voiceover_lines or min_beats)
    source_links = validate_source_links(text, require_source_links)
    failures: list[str] = []

    if len(time_ranges) < min_beats:
        failures.append(f"expected at least {min_beats} timed beats, found {len(time_ranges)}")
    if missing:
        failures.append("missing coverage: " + ", ".join(missing))
    if transition_hits < 2:
        failures.append("transition plan is too thin")
    if audio_hits < 2:
        failures.append("audio/music/SFX plan is too thin")
    if visual_hits < 3 or animation_hits < 2:
        failures.append("visual or animation plan is too thin")
    failures.extend(str(failure) for failure in labeled_fields["failures"])
    failures.extend(str(failure) for failure in beat_table["failures"])
    failures.extend(str(failure) for failure in voiceover["failures"])
    failures.extend(str(failure) for failure in source_links["failures"])

    return {
        "ok": not failures,
        "failures": failures,
        "time_ranges": len(time_ranges),
        "beat_table_rows": beat_table["table_rows"],
        "beat_table_missing_fields": beat_table["missing_fields"],
        "beat_table_generic_fields": beat_table["generic_fields"],
        "labeled_field_missing": labeled_fields["missing"],
        "labeled_field_thin": labeled_fields["thin"],
        "labeled_field_values": labeled_fields["values"],
        "voiceover_required": voiceover["required"],
        "voiceover_section_present": voiceover["section_present"],
        "voiceover_line_count": voiceover["line_count"],
        "voiceover_thin_lines": voiceover["thin_lines"],
        "voiceover_generic_lines": voiceover["generic_lines"],
        "voiceover_duplicate_lines": voiceover["duplicate_lines"],
        "source_links_required": source_links["required"],
        "source_link_section_present": source_links["section_present"],
        "source_link_label_present": source_links["label_present"],
        "source_link_count": source_links["link_count"],
        "source_links": source_links["links"],
        "source_link_generic_values": source_links["generic_values"],
        "source_link_failures": source_links["failures"],
        "transition_hits": transition_hits,
        "audio_hits": audio_hits,
        "visual_hits": visual_hits,
        "animation_hits": animation_hits,
        "missing": missing,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate an awsome-videos brief.")
    parser.add_argument("brief", type=Path)
    parser.add_argument("--min-beats", type=int, default=8)
    parser.add_argument("--require-voiceover", action="store_true")
    parser.add_argument("--min-voiceover-lines", type=int)
    parser.add_argument("--require-source-links", action="store_true")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    args = parser.parse_args()

    if not args.brief.exists():
        print(f"FAIL awsome-videos brief: file not found: {args.brief}", file=sys.stderr)
        return 2

    text = args.brief.read_text(encoding="utf-8", errors="ignore")
    result = validate(
        text,
        args.min_beats,
        args.require_voiceover,
        args.min_voiceover_lines,
        args.require_source_links,
    )
    if args.json:
        print(json.dumps(result, indent=2))
    elif result["ok"]:
        print(
            "PASS awsome-videos brief: "
            f"{result['time_ranges']} timed beats, "
            f"{result['transition_hits']} transition cues, "
            f"{result['audio_hits']} audio cues, "
            f"{result['source_link_count']} source links"
        )
    else:
        print("FAIL awsome-videos brief")
        for failure in result["failures"]:
            print(f"- {failure}")
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
