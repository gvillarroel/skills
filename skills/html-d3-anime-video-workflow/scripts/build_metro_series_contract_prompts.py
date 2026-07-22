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
import unicodedata
from pathlib import Path
from typing import Any

from compile_metro_design_profile import DEFAULT_PROFILE, load_design_profile, profile_prompt_contract
from plan_metro_video_series import build_series_report, markdown_video_sections, slugify


SCRIPT_ID = "build_metro_series_contract_prompts"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Generate exact-output Metro video prompt contracts for a multi-video source, "
            "including full Metro audits, MP4 composition audit, and semantic-density audit commands."
        )
    )
    parser.add_argument("--source", required=True, type=Path, help="Markdown source with ### video modules.")
    parser.add_argument(
        "--design-profile",
        type=Path,
        default=DEFAULT_PROFILE,
        help="Compiled Metro design profile embedded into every generated prompt.",
    )
    parser.add_argument("--output-dir", required=True, type=Path, help="Directory for generated prompt files and manifest.")
    parser.add_argument("--project-root", required=True, type=Path, help="Project root used inside generated prompt paths.")
    parser.add_argument("--checked-date", default="2026-07-05")
    parser.add_argument("--duration", type=float, default=120.0)
    parser.add_argument("--fps", type=int, default=30)
    parser.add_argument("--width", type=int, default=1280)
    parser.add_argument("--height", type=int, default=720)
    parser.add_argument("--limit", type=int, default=0, help="Optional maximum number of modules to emit.")
    parser.add_argument("--manifest", type=Path, help="Optional manifest path. Defaults to output-dir/metro-series-contract-prompts.json.")
    parser.add_argument("--min-helper-diversity", type=int, default=4)
    parser.add_argument("--min-primary-diversity", type=int, default=6)
    parser.add_argument("--min-reusable-d3-patterns", type=int, default=8)
    return parser.parse_args()


def strip_citations(text: str) -> str:
    text = re.sub(r"cite[^]*", "", text)
    return re.sub(r"\s+", " ", text).strip()


def section_after(body: str, heading: str) -> str:
    pattern = re.compile(rf"^####\s+{re.escape(heading)}\s*$", flags=re.IGNORECASE | re.MULTILINE)
    match = pattern.search(body)
    if not match:
        return ""
    next_heading = re.search(r"^####\s+", body[match.end() :], flags=re.MULTILINE)
    end = match.end() + next_heading.start() if next_heading else len(body)
    return body[match.end() : end].strip()


def executive_facts(body: str, limit: int = 8) -> list[str]:
    summary = strip_citations(section_after(body, "Executive summary"))
    if not summary:
        return []
    parts = re.split(r"(?<=[.!?])\s+", summary)
    facts = [part.strip(" -") for part in parts if len(part.strip()) > 24]
    return facts[:limit]


def table_rows(block: str) -> list[tuple[str, str, str]]:
    rows: list[tuple[str, str, str]] = []
    for line in block.splitlines():
        stripped = line.strip()
        if not stripped.startswith("|") or "---" in stripped:
            continue
        cells = [strip_citations(cell.strip()) for cell in stripped.strip("|").split("|")]
        if len(cells) < 3 or cells[0].lower() == "time":
            continue
        rows.append((cells[0], cells[1], cells[2]))
    return rows


def timed_beats(body: str, limit: int = 10) -> list[str]:
    rows = table_rows(section_after(body, "Timed narration and visuals"))
    beats: list[str] = []
    for time_range, narration, visual in rows[:limit]:
        narration = narration.strip().strip("“”\"")
        visual = visual.strip()
        beats.append(f"{time_range}: {narration} Visual contract: {visual}")
    return beats


def code_spans(text: str) -> list[str]:
    return [match.group(1).strip() for match in re.finditer(r"`([^`]+)`", text) if match.group(1).strip()]


def bold_spans(text: str) -> list[str]:
    return [match.group(1).strip() for match in re.finditer(r"\*\*([^*]+)\*\*", text) if match.group(1).strip()]


def ascii_contract_text(value: str) -> str:
    text = str(value or "")
    replacements = {
        "→": "->",
        "←": "<-",
        "↔": "<->",
        "–": "-",
        "—": "-",
        "“": '"',
        "”": '"',
        "‘": "'",
        "’": "'",
        "…": "...",
        "≠": "!=",
        "≤": "<=",
        "≥": ">=",
    }
    for source, target in replacements.items():
        text = text.replace(source, target)
    text = text.replace("`", "")
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    return re.sub(r"\s+", " ", text).strip(" .")


def shot_plan_terms(body: str, limit: int = 10) -> list[str]:
    block = section_after(body, "Shot and animation plan")
    terms: list[str] = []
    for line in block.splitlines():
        stripped = strip_citations(line.strip())
        if not stripped.startswith("- "):
            continue
        value = stripped[2:].strip()
        value = re.sub(r"^Reuse\s+", "", value, flags=re.IGNORECASE)
        value = re.split(r";|,", value)[0].strip(". ")
        value = ascii_contract_text(value)
        if value:
            terms.append(value)
    return terms[:limit]


def unique(values: list[str], limit: int) -> list[str]:
    seen: set[str] = set()
    output: list[str] = []
    for value in values:
        compact = ascii_contract_text(value)
        if not compact:
            continue
        key = compact.lower()
        if key in seen:
            continue
        seen.add(key)
        output.append(compact)
        if len(output) >= limit:
            break
    return output


def visual_anchors(section: dict[str, str], report: dict[str, Any]) -> list[str]:
    text = section["text"]
    selected = report.get("selected") if isinstance(report.get("selected"), dict) else {}
    pattern_values = [
        str(selected.get("primaryPattern") or ""),
        str(selected.get("secondaryPattern") or ""),
        *[str(item) for item in selected.get("supportPatterns", []) if item],
    ]
    anchors = code_spans(text) + bold_spans(section_after(text, "Timed narration and visuals")) + shot_plan_terms(text)
    anchors.extend(pattern_values)
    anchors.extend(["masonry wall", "megacanvas zones", "camera reframe", "zero internal padding", "grayscale hierarchy"])
    return unique(anchors, 18)


def label_section_for_pattern(pattern: str, anchors: list[str]) -> tuple[str, list[str]]:
    picked = unique(anchors, 8)
    if pattern == "risk-bowtie":
        return "Preserve these threat labels", picked[:4]
    if pattern == "swimlane-handoff":
        return "Preserve these handoff labels", picked[:8]
    if pattern == "sankey-flow":
        return "Preserve these flow labels", picked[:8]
    if pattern == "metric-dashboard":
        return "Preserve these metric labels", picked[:5]
    if pattern == "comparison-matrix":
        return "Preserve these decision criteria", picked[:4]
    if pattern == "dependency-map":
        return "Preserve these dependency labels", picked[:8]
    if pattern == "sequence-trace":
        return "Preserve these trace labels", picked[:8]
    if pattern == "scenario-tree":
        return "Preserve these scenario labels", picked[:7]
    if pattern == "evidence-ladder":
        return "Preserve these evidence labels", picked[:6]
    if pattern == "layered-architecture":
        return "Preserve these layer labels", picked[:6]
    if pattern == "data-lineage":
        return "Preserve these lineage labels", picked[:6]
    if pattern == "state-machine":
        return "Preserve these lifecycle states", picked[:6]
    if pattern == "phase-timeline":
        return "Preserve these timeline phases", picked[:6]
    return "Preserve these system labels", picked[:10]


def fmt_duration(value: float) -> str:
    return str(int(value)) if float(value).is_integer() else f"{value:.2f}".rstrip("0").rstrip(".")


def scaffold_paths(project: Path, output_id: str) -> list[str]:
    base = project.as_posix()
    return [
        f"{base}/source/source-package.json",
        f"{base}/source/production-notes.md",
        f"{base}/src/index.html",
        f"{base}/src/render.mjs",
        f"{base}/artifacts/video-renders/draft/videos/{output_id}.mp4",
        f"{base}/artifacts/video-renders/draft/review/{output_id}-contact-sheet.jpg",
        f"{base}/artifacts/video-renders/draft/review/{output_id}-contact-sheet.json",
        f"{base}/artifacts/reviews/self-review.md",
        f"{base}/artifacts/reviews/prompt-contract-build.json",
        f"{base}/artifacts/reviews/render-state-check.json",
        f"{base}/artifacts/reviews/metro-style-audit.json",
        f"{base}/artifacts/reviews/metro-composition-audit.json",
        f"{base}/artifacts/reviews/metro-rendered-frame-audit.json",
        f"{base}/artifacts/reviews/metro-mute-test-audit.json",
        f"{base}/artifacts/reviews/metro-video-composition-audit.json",
        f"{base}/artifacts/reviews/metro-audit-suite.json",
    ]


def final_validation_paths(project: Path) -> list[str]:
    base = project.as_posix()
    return [f"{base}/artifacts/reviews/metro-semantic-density-audit.json"]


def wrapper_command(project: Path) -> str:
    base = project.as_posix()
    return (
        "uv run --script skills/html-d3-anime-video-workflow/scripts/build_from_prompt_contract.py "
        "--prompt ../prompt.md "
        f"--manifest {base}/artifacts/reviews/prompt-contract-build.json "
        f"--state-manifest {base}/artifacts/reviews/render-state-check.json "
        f"--metro-style-manifest {base}/artifacts/reviews/metro-style-audit.json "
        f"--metro-composition-manifest {base}/artifacts/reviews/metro-composition-audit.json "
        f"--metro-rendered-frame-manifest {base}/artifacts/reviews/metro-rendered-frame-audit.json "
        f"--metro-mute-test-manifest {base}/artifacts/reviews/metro-mute-test-audit.json "
        f"--metro-video-composition-manifest {base}/artifacts/reviews/metro-video-composition-audit.json "
        f"--metro-audit-suite-manifest {base}/artifacts/reviews/metro-audit-suite.json"
    )


def semantic_command(project: Path, output_id: str) -> str:
    base = project.as_posix()
    return (
        "uv run --script skills/html-d3-anime-video-workflow/scripts/audit_metro_semantic_density.py "
        f"--wrapper-report {base}/artifacts/reviews/prompt-contract-build.json "
        f"--state-manifest {base}/artifacts/reviews/render-state-check.json "
        f"--contact-sheet-manifest {base}/artifacts/video-renders/draft/review/{output_id}-contact-sheet.json "
        f"--metro-audit-suite {base}/artifacts/reviews/metro-audit-suite.json "
        f"--metro-mute-test-audit {base}/artifacts/reviews/metro-mute-test-audit.json "
        f"--metro-video-composition-audit {base}/artifacts/reviews/metro-video-composition-audit.json "
        f"--output {base}/artifacts/reviews/metro-semantic-density-audit.json"
    )


def render_prompt(
    index: int,
    section: dict[str, str],
    report: dict[str, Any],
    args: argparse.Namespace,
    style_contract: str,
) -> tuple[str, dict[str, Any]]:
    output_id = slugify(section["title"])
    project = args.project_root / output_id
    selected = report.get("selected") if isinstance(report.get("selected"), dict) else {}
    helper_pattern = str(selected.get("helperPattern") or "auto")
    primary_pattern = str(selected.get("primaryPattern") or "")
    secondary_pattern = str(selected.get("secondaryPattern") or "")
    support_patterns = [str(item) for item in selected.get("supportPatterns", []) if item]
    anchors = visual_anchors(section, report)
    facts = executive_facts(section["text"])
    beats = timed_beats(section["text"])
    if not facts:
        facts = [strip_citations(section["title"])]
    label_heading, labels = label_section_for_pattern(helper_pattern, anchors)
    required_scaffold_paths = scaffold_paths(project, output_id)
    required_final_paths = final_validation_paths(project)
    prompt = [
        "First action: read this prompt at `../prompt.md`. Then run the exact commands below from the isolated workspace root. Do not list directories, do not read helper source, do not run manual verification scripts, do not ask questions, and do not stop before the second command exits successfully.",
        "",
        "```bash",
        wrapper_command(project),
        "```",
        "",
        "```bash",
        semantic_command(project, output_id),
        "```",
        "",
        "Task: create a deterministic standalone HTML+D3/Anime.js explainer video package for the video module described below.",
        "",
        f"Use the `{helper_pattern}` scaffold. Use {fmt_duration(args.duration)} seconds, {args.fps} fps, and {args.width}x{args.height}.",
        "",
        f"Topic: {section['title']}.",
        f"Video title: {section['title']}.",
        f"Checked date: {args.checked_date}.",
        "",
        style_contract.rstrip(),
        "",
        "Pattern brief:",
        "",
        f"- Primary reusable pattern: `{primary_pattern}`.",
        f"- Secondary reusable pattern: `{secondary_pattern}`.",
        f"- Support patterns: {', '.join(f'`{item}`' for item in support_patterns) or '`none`'}.",
        f"- Helper pattern: `{helper_pattern}`.",
        "- The helper scaffold is only the runnable base; the final composition must visibly use the pattern brief, masonry armature, zone map, camera path, transition contracts, and low-text gray hierarchy.",
        "",
        "Required exact scaffold outputs:",
        "",
    ]
    prompt.extend(f"- `{path}`" for path in required_scaffold_paths)
    prompt.extend(["", "Additional final validation reports after the second command:", ""])
    prompt.extend(f"- `{path}`" for path in required_final_paths)
    prompt.extend(["", "Preserve these source facts:", ""])
    prompt.extend(f"- {fact}" for fact in facts)
    prompt.extend(["", "Preserve these timed narration beats as the production timing contract:", ""])
    prompt.extend(f"- {beat}" for beat in beats)
    prompt.extend(["", "Preserve these visual anchors:", ""])
    prompt.extend(f"- {anchor}" for anchor in anchors)
    prompt.extend(["", f"{label_heading}:", ""])
    prompt.extend(f"- {label}" for label in labels)
    prompt.extend(
        [
            "",
            "After the commands finish, read only the final `metro-semantic-density-audit.json`, report whether `passed` is true, and stop. The harness checks exact output paths, wrapper report fields, contact-sheet manifest, media properties, source preservation, render-state check, Metro audit suite, MP4 composition audit, mute-test audit, and semantic-density audit. Keep generated task files under the requested project directory; do not write into the copied skill directory.",
            "",
        ]
    )
    metadata = {
        "index": index,
        "id": output_id,
        "title": section["title"],
        "prompt": None,
        "projectRoot": project.as_posix(),
        "outputId": output_id,
        "helperPattern": helper_pattern,
        "primaryPattern": primary_pattern,
        "secondaryPattern": secondary_pattern,
        "supportPatterns": support_patterns,
        "masonryContract": report.get("masonryContract") if isinstance(report.get("masonryContract"), dict) else {},
        "requiredScaffoldOutputs": required_scaffold_paths,
        "requiredFinalOutputs": required_final_paths,
        "requiredOutputs": [*required_scaffold_paths, *required_final_paths],
        "commands": [wrapper_command(project), semantic_command(project, output_id)],
    }
    return "\n".join(prompt), metadata


def design_repair_text(sections: list[dict[str, str]], style_contract: str) -> str:
    return "\n\n".join(f"{section['text']}\n\n#### Design repair contract\n\n{style_contract}" for section in sections)


def section_design_repair_text(section: dict[str, str], style_contract: str) -> str:
    return f"{section['text']}\n\n#### Design repair contract\n\n{style_contract}"


def main() -> int:
    args = parse_args()
    design_profile = load_design_profile(args.design_profile)
    style_contract = profile_prompt_contract(design_profile)
    text = args.source.read_text(encoding="utf-8")
    sections = markdown_video_sections(text)
    if args.limit > 0:
        sections = sections[: args.limit]
    if not sections:
        print(f"No timed video modules found in {args.source}", file=sys.stderr)
        return 2
    series_args = argparse.Namespace(
        min_videos=min(4, len(sections)),
        min_helper_diversity=min(args.min_helper_diversity, max(1, len(sections))),
        min_primary_diversity=min(args.min_primary_diversity, max(1, len(sections))),
        min_reusable_d3_patterns=min(args.min_reusable_d3_patterns, max(1, len(sections))),
        max_same_helper_run=2,
        min_patterns=6,
        min_patterns_used=3,
        min_functional_zones=5,
        min_motion_systems=4,
        min_camera_events=3,
    )
    source_name = args.source.as_posix()
    repair_text = design_repair_text(sections, style_contract)
    series = build_series_report(f"{source_name}#design-repair", repair_text, series_args)
    modules_by_id = {str(module.get("id")): module for module in series.get("modules", []) if isinstance(module, dict)}
    full_reports = []
    # Rebuild per-section reports with the same planner defaults because the compact series manifest intentionally omits full zone data.
    from plan_metro_pattern_mix import build_report

    planner_args = argparse.Namespace(
        min_patterns=6,
        min_patterns_used=3,
        min_functional_zones=5,
        min_motion_systems=4,
        min_camera_events=3,
        require_anchor=[],
    )
    args.output_dir.mkdir(parents=True, exist_ok=True)
    prompt_records: list[dict[str, Any]] = []
    for index, section in enumerate(sections, start=1):
        report = build_report(
            f"{source_name}#{section['id']}#design-repair",
            section_design_repair_text(section, style_contract),
            planner_args,
        )
        full_reports.append(report)
        prompt_text, metadata = render_prompt(index, section, report, args, style_contract)
        prompt_path = args.output_dir / f"{index:02d}-{metadata['id']}.md"
        prompt_path.write_text(prompt_text, encoding="utf-8")
        metadata["prompt"] = prompt_path.as_posix()
        compact_module = modules_by_id.get(str(metadata["id"]))
        if compact_module:
            metadata["seriesModule"] = compact_module
        prompt_records.append(metadata)

    manifest_path = args.manifest or (args.output_dir / "metro-series-contract-prompts.json")
    manifest = {
        "passed": bool(series.get("passed")),
        "source": source_name,
        "outputDir": args.output_dir.as_posix(),
        "projectRoot": args.project_root.as_posix(),
        "checkedDate": args.checked_date,
        "designProfile": {
            "path": args.design_profile.as_posix(),
            "profileId": design_profile.get("profileId"),
            "profileVersion": design_profile.get("profileVersion"),
            "profileSha256": design_profile.get("profileSha256"),
            "sourceDigests": {
                key: value.get("sha256")
                for key, value in design_profile.get("sources", {}).items()
                if isinstance(value, dict)
            },
        },
        "format": {"duration": args.duration, "fps": args.fps, "width": args.width, "height": args.height},
        "series": series,
        "prompts": prompt_records,
        "findings": series.get("findings") if isinstance(series.get("findings"), list) else [],
    }
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(json.dumps({"manifest": manifest_path.as_posix(), "prompts": len(prompt_records), "passed": manifest["passed"]}, indent=2))
    return 0 if manifest["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
