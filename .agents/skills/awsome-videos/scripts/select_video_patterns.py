#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Select an Awesome/Fireship-style pattern blueprint for a video topic."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


sys.dont_write_bytecode = True

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
DEFAULT_SUMMARY = SKILL_DIR / "assets" / "reference" / "corpus-summary.json"


FORMAT_KEYWORDS = {
    "trend/news commentary": [
        "news",
        "release",
        "released",
        "launch",
        "lawsuit",
        "incident",
        "outage",
        "breach",
        "security",
        "funding",
        "acquisition",
        "drama",
        "regulation",
        "latest",
        "new ",
    ],
    "tutorial/overview": [
        "how to",
        "build",
        "tutorial",
        "guide",
        "learn",
        "setup",
        "from scratch",
        "step by step",
    ],
    "deep walkthrough": [
        "deep",
        "walkthrough",
        "full course",
        "complete build",
        "longform",
    ],
    "compressed explainer": [
        "what is",
        "what are",
        "explain",
        "100 seconds",
        "in 100",
        "primer",
        "intro",
    ],
}


TECH_MECHANISM_TERMS = [
    "api",
    "code",
    "sdk",
    "database",
    "sql",
    "server",
    "client",
    "model",
    "llm",
    "mcp",
    "agent",
    "runtime",
    "framework",
    "library",
    "protocol",
]

FLOW_TERMS = ["request", "response", "flow", "state", "lifecycle", "network", "pipeline", "token", "context"]
NUMBER_TERMS = ["cost", "price", "latency", "performance", "benchmark", "count", "million", "billion", "rate"]
WARNING_TERMS = ["security", "risk", "bug", "breach", "outage", "lawsuit", "failure", "limit", "cost", "lock-in"]
BASE_BEAT_WEIGHTS = [5, 10, 10, 10, 10, 10, 10, 5]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Select awsome-videos pattern guidance for a topic.")
    parser.add_argument("--title", required=True)
    parser.add_argument("--promise", default="")
    parser.add_argument("--format", dest="requested_format", default="")
    parser.add_argument("--runtime", default="1:10")
    parser.add_argument("--summary", type=Path, default=DEFAULT_SUMMARY)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--markdown", action="store_true")
    return parser.parse_args()


def load_summary(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("corpus summary root must be an object")
    return data


def taxonomy_by_name(summary: dict[str, Any], group: str) -> dict[str, dict[str, Any]]:
    items = summary.get("patternTaxonomy", {}).get(group, [])
    if not isinstance(items, list):
        return {}
    return {item["name"]: item for item in items if isinstance(item, dict) and isinstance(item.get("name"), str)}


def find_item(summary: dict[str, Any], group: str, name: str) -> dict[str, Any]:
    items = taxonomy_by_name(summary, group)
    if name not in items:
        raise KeyError(f"missing taxonomy item {group}.{name}")
    return items[name]


def text_blob(title: str, promise: str) -> str:
    return f"{title} {promise}".lower()


def infer_format(title: str, promise: str, requested: str, summary: dict[str, Any]) -> tuple[str, str]:
    available = taxonomy_by_name(summary, "videoTypes")
    requested_clean = requested.strip().lower()
    if requested_clean:
        for name in available:
            if name.lower() == requested_clean:
                return name, "explicit format request"
        raise ValueError(f"unknown format {requested!r}; expected one of: {', '.join(sorted(available))}")

    blob = text_blob(title, promise)
    for format_name in ["deep walkthrough", "trend/news commentary", "tutorial/overview", "compressed explainer"]:
        for keyword in FORMAT_KEYWORDS[format_name]:
            if keyword in blob:
                return format_name, f"matched keyword {keyword!r}"
    return "compressed explainer", "default one-concept explainer fit"


def has_any(blob: str, terms: list[str]) -> bool:
    return any(term in blob for term in terms)


def ordered_unique(names: list[str]) -> list[str]:
    result: list[str] = []
    for name in names:
        if name not in result:
            result.append(name)
    return result


def select_names(selected_format: str, title: str, promise: str) -> dict[str, list[str]]:
    blob = text_blob(title, promise)
    visual = ["logo/title anchor", "UI proof", "diagram proof"]
    if selected_format in {"tutorial/overview", "deep walkthrough"} or has_any(blob, TECH_MECHANISM_TERMS):
        visual.append("code proof")
    if selected_format == "trend/news commentary":
        visual.extend(["human/context insert", "meme/editorial insert"])
    elif selected_format == "compressed explainer":
        visual.append("meme/editorial insert")

    animation = ["punch-in zoom", "highlight sweep", "stack build"]
    if has_any(blob, FLOW_TERMS) or selected_format in {"compressed explainer", "tutorial/overview"}:
        animation.append("diagram trace")
    if has_any(blob, NUMBER_TERMS):
        animation.append("counter/ticker")
    if selected_format in {"trend/news commentary", "tutorial/overview"}:
        animation.append("split-screen contrast")
    if selected_format == "trend/news commentary":
        animation.append("fast pan")

    transitions = ["hard cut", "punch-in", "match cut", "snap zoom"]
    if selected_format in {"trend/news commentary", "deep walkthrough"} or has_any(blob, WARNING_TERMS):
        transitions.append("glitch/wipe")
    if selected_format == "deep walkthrough":
        transitions.append("title reset")

    audio = ["background bed", "hit/stinger", "whoosh/tick", "riser", "final tail"]
    if has_any(blob, WARNING_TERMS) or selected_format == "trend/news commentary":
        audio.extend(["low impact", "dropout"])

    script = ["claim hook", "one-sentence context", "contrast pair", "reset line", "warning beat", "callback"]
    if selected_format in {"compressed explainer", "trend/news commentary"}:
        script.append("technical joke")

    return {
        "visualSources": ordered_unique(visual),
        "animationAtoms": ordered_unique(animation),
        "transitionTypes": ordered_unique(transitions),
        "audioRoles": ordered_unique(audio),
        "scriptMoves": ordered_unique(script),
    }


def seconds(runtime: str) -> int:
    value = runtime.strip().lower()
    if re.fullmatch(r"\d+", value):
        return int(value)
    match = re.fullmatch(r"(\d+):(\d{1,2})", value)
    if match:
        return int(match.group(1)) * 60 + int(match.group(2))
    match = re.fullmatch(r"(\d+(?:\.\d+)?)\s*s(?:ec(?:onds?)?)?", value)
    if match:
        return int(round(float(match.group(1))))
    match = re.fullmatch(r"(\d+(?:\.\d+)?)\s*m(?:in(?:utes?)?)?", value)
    if match:
        return int(round(float(match.group(1)) * 60))
    raise ValueError(f"could not parse runtime {runtime!r}")


def compact_number(value: float) -> str:
    if abs(value - round(value)) < 0.001:
        return str(int(round(value)))
    return f"{value:.1f}".rstrip("0").rstrip(".")


def format_time(value: float) -> str:
    if abs(value - round(value)) >= 0.001:
        return f"{compact_number(value)}s"
    total = int(round(value))
    minutes, seconds_value = divmod(total, 60)
    return f"{minutes}:{seconds_value:02d}"


def allocate_beat_ranges(total_seconds: float, count: int) -> list[tuple[float, float]]:
    if count <= 0:
        return []
    if total_seconds <= 0:
        total_seconds = float(count)
    if total_seconds < count:
        duration = total_seconds / count
        edges = [round(duration * index, 3) for index in range(count + 1)]
        return [(edges[index], edges[index + 1]) for index in range(count)]

    total = int(round(total_seconds))
    weights = (BASE_BEAT_WEIGHTS * ((count // len(BASE_BEAT_WEIGHTS)) + 1))[:count]
    durations = [1] * count
    remaining = total - count
    shares = [remaining * weight / sum(weights) for weight in weights]
    extras = [int(share) for share in shares]
    for index, extra in enumerate(extras):
        durations[index] += extra
    leftover = remaining - sum(extras)
    order = sorted(range(count), key=lambda index: shares[index] - extras[index], reverse=True)
    for index in order[:leftover]:
        durations[index] += 1

    ranges: list[tuple[float, float]] = []
    cursor = 0
    for duration in durations:
        start = cursor
        cursor += duration
        ranges.append((float(start), float(cursor)))
    return ranges


def label_time(total_seconds: int, index: int, count: int) -> str:
    ranges = allocate_beat_ranges(float(total_seconds), count)
    start, end = ranges[index]
    return f"{format_time(start)}-{format_time(end)}"


def pattern_items(summary: dict[str, Any], group: str, names: list[str]) -> list[dict[str, Any]]:
    return [find_item(summary, group, name) for name in names]


def build_beats(total_seconds: int, selected: dict[str, list[str]]) -> list[dict[str, str]]:
    purposes = [
        "Cold claim and title anchor",
        "One-sentence definition",
        "Source proof",
        "Mechanism or state flow",
        "Concrete example",
        "Contrast or warning",
        "Reusable rule",
        "Callback and final tail",
    ]
    visuals = selected["visualSources"]
    animations = selected["animationAtoms"]
    transitions = selected["transitionTypes"]
    audio = selected["audioRoles"]
    beats: list[dict[str, str]] = []
    for index, purpose in enumerate(purposes):
        beats.append(
            {
                "time": label_time(total_seconds, index, len(purposes)),
                "purpose": purpose,
                "visualSource": visuals[index % len(visuals)],
                "animation": animations[index % len(animations)],
                "transition": transitions[index % len(transitions)],
                "audioRole": audio[index % len(audio)],
            }
        )
    return beats


def select_blueprint(args: argparse.Namespace) -> dict[str, Any]:
    summary = load_summary(args.summary)
    selected_format, rationale = infer_format(args.title, args.promise, args.requested_format, summary)
    selected_names = select_names(selected_format, args.title, args.promise)
    runtime_seconds = seconds(args.runtime)
    blueprint = {
        "ok": True,
        "title": args.title,
        "promise": args.promise,
        "selectedFormat": selected_format,
        "selectionRationale": rationale,
        "runtime": args.runtime,
        "runtimeSeconds": runtime_seconds,
        "corpusWindow": summary.get("analysisWindow"),
        "corpusCounts": {
            "totalPublicVideos": summary.get("scope", {}).get("totalPublicVideos"),
            "sourceManifest": summary.get("sourceManifest", {}),
        },
        "videoType": find_item(summary, "videoTypes", selected_format),
        "visualSources": pattern_items(summary, "visualSources", selected_names["visualSources"]),
        "animationAtoms": pattern_items(summary, "animationAtoms", selected_names["animationAtoms"]),
        "transitionTypes": pattern_items(summary, "transitionTypes", selected_names["transitionTypes"]),
        "audioRoles": pattern_items(summary, "audioRoles", selected_names["audioRoles"]),
        "scriptMoves": pattern_items(summary, "scriptMoves", selected_names["scriptMoves"]),
        "beatGuidance": build_beats(runtime_seconds, selected_names),
        "validationHints": [
            "Use check_video_brief.py --require-voiceover for the brief.",
            "Use --require-source-links for publishable source-backed claims.",
            "Use score_video_readiness.py and check_production_package.py before calling a finished video ready.",
        ],
    }
    return blueprint


def render_markdown(blueprint: dict[str, Any]) -> str:
    lines = [
        f"# Pattern Blueprint: {blueprint['title']}",
        "",
        f"Selected format: {blueprint['selectedFormat']} ({blueprint['selectionRationale']})",
        f"Runtime: {blueprint['runtime']} ({blueprint['runtimeSeconds']} seconds)",
        "",
        "## Video Type",
        f"- {blueprint['videoType']['name']}: {blueprint['videoType'].get('shape', '')}",
        "",
        "## Pattern Sets",
    ]
    for label, key in [
        ("Visual sources", "visualSources"),
        ("Animation atoms", "animationAtoms"),
        ("Transitions", "transitionTypes"),
        ("Audio roles", "audioRoles"),
        ("Script moves", "scriptMoves"),
    ]:
        lines.append(f"- {label}: " + ", ".join(item["name"] for item in blueprint[key]))
    lines.extend(["", "## Beat Guidance", "", "| Time | Purpose | Visual | Animation | Transition | Audio |", "| --- | --- | --- | --- | --- | --- |"])
    for beat in blueprint["beatGuidance"]:
        lines.append(
            f"| {beat['time']} | {beat['purpose']} | {beat['visualSource']} | {beat['animation']} | "
            f"{beat['transition']} | {beat['audioRole']} |"
        )
    lines.extend(["", "## Validation Hints"])
    for hint in blueprint["validationHints"]:
        lines.append(f"- {hint}")
    return "\n".join(lines) + "\n"


def main() -> int:
    args = parse_args()
    blueprint = select_blueprint(args)
    if args.markdown:
        output = render_markdown(blueprint)
    elif args.json:
        output = json.dumps(blueprint, indent=2) + "\n"
    else:
        output = (
            f"PASS awsome-videos pattern blueprint: {blueprint['selectedFormat']}, "
            f"{len(blueprint['beatGuidance'])} beats, "
            f"{len(blueprint['visualSources'])} visual sources\n"
        )
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(output, encoding="utf-8", newline="\n")
    else:
        print(output, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
