#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

from plan_metro_pattern_mix import build_report


SCRIPT_ID = "plan_metro_video_series"
SKIP_TITLES = {
    "recommended additional modules",
    "references and limitations",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Plan per-video Metro pattern mixes for a multi-module source so a series does not collapse to one generic scaffold."
    )
    parser.add_argument("--prompt-file", required=True, type=Path, help="Markdown source containing multiple video modules.")
    parser.add_argument("--output", type=Path, help="JSON report path. Prints JSON when omitted.")
    parser.add_argument("--min-videos", type=int, default=4)
    parser.add_argument("--min-helper-diversity", type=int, default=4)
    parser.add_argument("--min-primary-diversity", type=int, default=6)
    parser.add_argument("--min-reusable-d3-patterns", type=int, default=8)
    parser.add_argument("--max-same-helper-run", type=int, default=2)
    parser.add_argument("--min-patterns", type=int, default=6)
    parser.add_argument("--min-patterns-used", type=int, default=3)
    parser.add_argument("--min-functional-zones", type=int, default=5)
    parser.add_argument("--min-motion-systems", type=int, default=4)
    parser.add_argument("--min-camera-events", type=int, default=3)
    return parser.parse_args()


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.strip().lower())
    return slug.strip("-") or "video"


def markdown_video_sections(text: str) -> list[dict[str, str]]:
    matches = list(re.finditer(r"^###\s+(.+?)\s*$", text, flags=re.MULTILINE))
    sections: list[dict[str, str]] = []
    for index, match in enumerate(matches):
        title = match.group(1).strip()
        if title.lower() in SKIP_TITLES:
            continue
        start = match.start()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        body = text[start:end].strip()
        if "#### Timed narration and visuals" not in body:
            continue
        sections.append({"id": slugify(title), "title": title, "text": body})
    return sections


def planner_args(args: argparse.Namespace) -> argparse.Namespace:
    return argparse.Namespace(
        min_patterns=args.min_patterns,
        min_patterns_used=args.min_patterns_used,
        min_functional_zones=args.min_functional_zones,
        min_motion_systems=args.min_motion_systems,
        min_camera_events=args.min_camera_events,
        require_anchor=[],
    )


def max_consecutive(values: list[str]) -> int:
    longest = 0
    current = 0
    previous = None
    for value in values:
        if value == previous:
            current += 1
        else:
            current = 1
            previous = value
        longest = max(longest, current)
    return longest


def compact_module(section: dict[str, str], report: dict[str, Any]) -> dict[str, Any]:
    selected = report.get("selected")
    selected = selected if isinstance(selected, dict) else {}
    pattern_ids = report.get("patternIdsNamed")
    reusable_d3 = report.get("reusableD3PatternIds")
    return {
        "id": section["id"],
        "title": section["title"],
        "passed": bool(report.get("passed")),
        "helperPattern": selected.get("helperPattern"),
        "primaryPattern": selected.get("primaryPattern"),
        "secondaryPattern": selected.get("secondaryPattern"),
        "supportPatterns": selected.get("supportPatterns") if isinstance(selected.get("supportPatterns"), list) else [],
        "armature": selected.get("armature"),
        "patternIdsNamed": pattern_ids if isinstance(pattern_ids, list) else [],
        "reusableD3PatternIds": reusable_d3 if isinstance(reusable_d3, list) else [],
        "masonryContract": report.get("masonryContract") if isinstance(report.get("masonryContract"), dict) else {},
        "antiPatternRiskIds": [
            str(item.get("id"))
            for item in (report.get("antiPatternRisks") if isinstance(report.get("antiPatternRisks"), list) else [])
            if isinstance(item, dict) and item.get("id")
        ],
        "findings": report.get("findings") if isinstance(report.get("findings"), list) else [],
    }


def build_series_report(source: str, text: str, args: argparse.Namespace) -> dict[str, Any]:
    sections = markdown_video_sections(text)
    base_args = planner_args(args)
    modules: list[dict[str, Any]] = []
    full_reports: list[dict[str, Any]] = []
    for section in sections:
        report = build_report(f"{source}#{section['id']}", section["text"], base_args)
        full_reports.append(report)
        modules.append(compact_module(section, report))

    helper_sequence = [str(module.get("helperPattern") or "") for module in modules]
    primary_sequence = [str(module.get("primaryPattern") or "") for module in modules]
    helper_diversity = len({value for value in helper_sequence if value})
    primary_diversity = len({value for value in primary_sequence if value})
    reusable_d3_ids = sorted(
        {
            str(pattern_id)
            for module in modules
            for pattern_id in module.get("reusableD3PatternIds", [])
            if pattern_id
        }
    )
    repeated_helper_run = max_consecutive(helper_sequence)
    generic_helpers = sum(1 for value in helper_sequence if value == "systems-flow")
    findings: list[dict[str, Any]] = []

    if len(modules) < args.min_videos:
        findings.append({"code": "too-few-video-modules", "minimum": args.min_videos, "actual": len(modules)})
    if helper_diversity < args.min_helper_diversity:
        findings.append({"code": "series-helper-diversity-too-low", "minimum": args.min_helper_diversity, "actual": helper_diversity})
    if primary_diversity < args.min_primary_diversity:
        findings.append({"code": "series-primary-pattern-diversity-too-low", "minimum": args.min_primary_diversity, "actual": primary_diversity})
    if len(reusable_d3_ids) < args.min_reusable_d3_patterns:
        findings.append({"code": "series-reusable-d3-diversity-too-low", "minimum": args.min_reusable_d3_patterns, "actual": len(reusable_d3_ids)})
    if repeated_helper_run > args.max_same_helper_run:
        findings.append({"code": "series-repeated-helper-run-too-long", "maximum": args.max_same_helper_run, "actual": repeated_helper_run})
    if generic_helpers == len(modules) and modules:
        findings.append({"code": "series-collapsed-to-systems-flow", "actual": generic_helpers})

    for module in modules:
        if not module["passed"]:
            findings.append({"code": "module-pattern-mix-failed", "module": module["id"], "findings": module["findings"]})

    return {
        "passed": not findings,
        "source": source,
        "moduleCount": len(modules),
        "metrics": {
            "helperDiversity": helper_diversity,
            "primaryPatternDiversity": primary_diversity,
            "reusableD3PatternCount": len(reusable_d3_ids),
            "maxSameHelperRun": repeated_helper_run,
            "systemsFlowHelperCount": generic_helpers,
        },
        "helperSequence": helper_sequence,
        "primaryPatternSequence": primary_sequence,
        "reusableD3PatternIds": reusable_d3_ids,
        "modules": modules,
        "thresholds": {
            "minVideos": args.min_videos,
            "minHelperDiversity": args.min_helper_diversity,
            "minPrimaryDiversity": args.min_primary_diversity,
            "minReusableD3Patterns": args.min_reusable_d3_patterns,
            "maxSameHelperRun": args.max_same_helper_run,
        },
        "findings": findings,
    }


def main() -> int:
    args = parse_args()
    text = args.prompt_file.read_text(encoding="utf-8")
    report = build_series_report(args.prompt_file.as_posix(), text, args)
    rendered = json.dumps(report, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered)
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
