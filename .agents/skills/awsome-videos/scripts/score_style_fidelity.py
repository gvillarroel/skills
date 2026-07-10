#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Score whether a brief follows the distilled Awesome/Fireship style patterns."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any


sys.dont_write_bytecode = True

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
DEFAULT_SUMMARY = SKILL_DIR / "assets" / "reference" / "corpus-summary.json"

if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import check_video_brief  # noqa: E402
import score_video_readiness  # noqa: E402


def sha256_file(path: Path | None) -> str | None:
    if path is None or not path.is_file():
        return None
    return hashlib.sha256(path.read_bytes()).hexdigest()


STYLE_CATEGORIES = [
    "format_pacing",
    "hook_claim",
    "source_proof",
    "visual_atoms",
    "animation_atoms",
    "transition_punctuation",
    "audio_roles",
    "script_moves",
]

VISUAL_TERMS = [
    "logo",
    "title anchor",
    "ui",
    "screenshot",
    "docs",
    "github",
    "terminal",
    "dashboard",
    "browser",
    "code",
    "diagram",
    "article",
    "meme",
    "source proof",
]

ANIMATION_TERMS = [
    "punch-in",
    "zoom",
    "pan",
    "highlight",
    "sweep",
    "stack build",
    "split-screen",
    "counter",
    "ticker",
    "trace",
    "scroll",
    "overlay",
    "pop",
    "smash",
]

TRANSITION_TERMS = [
    "hard cut",
    "jump cut",
    "match cut",
    "glitch",
    "wipe",
    "snap zoom",
    "smash cut",
    "title reset",
    "insert",
]

TRANSITION_PURPOSE_TERMS = [
    "proof",
    "claim",
    "joke",
    "reversal",
    "state change",
    "warning",
    "callback",
    "contrast",
    "section",
]

AUDIO_ROLE_TERMS = [
    "voiceover",
    "narration",
    "background bed",
    "bed",
    "duck",
    "hit",
    "stinger",
    "whoosh",
    "tick",
    "riser",
    "dropout",
    "low impact",
    "tail",
    "sfx",
]

SCRIPT_MOVE_TERMS = [
    "claim",
    "context",
    "contrast",
    "define",
    "definition",
    "prove",
    "proof",
    "reset",
    "joke",
    "warning",
    "callback",
    "limitation",
    "tradeoff",
    "rule",
    "payoff",
]

SLOW_GENERIC_STYLE_TERMS = [
    "fade",
    "dissolve",
    "gentle reveal",
    "soft ambient",
    "whiteboard",
    "slide",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Score Awesome/Fireship style fidelity for a video brief.")
    parser.add_argument("--brief", required=True, type=Path)
    parser.add_argument("--pattern-blueprint", type=Path)
    parser.add_argument("--summary", type=Path, default=DEFAULT_SUMMARY)
    parser.add_argument("--min-score", type=int, default=12)
    parser.add_argument("--require-voiceover", action="store_true")
    parser.add_argument("--require-source-links", action="store_true")
    parser.add_argument("--require-pattern-blueprint", action="store_true")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--json", action="store_true")
    return parser.parse_args()


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def load_json(path: Path | None, warnings: list[str], label: str) -> dict[str, Any] | None:
    if path is None:
        return None
    if not path.exists():
        warnings.append(f"{label} not found: {path}")
        return None
    try:
        data = json.loads(read_text(path))
    except json.JSONDecodeError as exc:
        warnings.append(f"{label} is not valid JSON: {exc}")
        return None
    return data if isinstance(data, dict) else None


def count_terms(text: str, terms: list[str]) -> int:
    return sum(1 for term in terms if term in text)


def category(score: int, evidence: list[str], fix: str) -> dict[str, Any]:
    return {"score": max(0, min(2, score)), "evidence": evidence, "fix": fix}


def score_format_pacing(text: str, brief_result: dict[str, Any]) -> dict[str, Any]:
    beats = int(brief_result.get("beat_table_rows") or brief_result.get("time_ranges") or 0)
    has_fast_format = any(term in text for term in ["compressed explainer", "100 seconds", "fast", "rapid"])
    immediate_hook = score_video_readiness.find_immediate_hook_range(text)
    evidence = [f"{beats} timed beats"]
    if has_fast_format:
        evidence.append("fast/compressed format language")
    if immediate_hook:
        evidence.append(f"first beat resolves by {immediate_hook[1]:g}s")
    score = 2 if beats >= 8 and has_fast_format and immediate_hook else 1 if beats >= 8 and (has_fast_format or immediate_hook) else 0
    return category(score, evidence, "Declare a compressed/fast format and open with an immediate 0:00-0:06 hook beat.")


def score_hook_claim(text: str) -> dict[str, Any]:
    has_hook = any(term in text for term in ["hook", "cold-open", "cold open"])
    has_claim = any(term in text for term in ["claim", "contradiction", "proof", "payoff", "promise"])
    immediate_hook = score_video_readiness.find_immediate_hook_range(text)
    evidence: list[str] = []
    if has_hook:
        evidence.append("hook language")
    if has_claim:
        evidence.append("claim/proof/payoff language")
    if immediate_hook:
        evidence.append(f"immediate hook {immediate_hook[0]:g}-{immediate_hook[1]:g}s")
    score = 2 if has_hook and has_claim and immediate_hook else 1 if has_hook and (has_claim or immediate_hook) else 0
    return category(score, evidence, "Start with a claim, contradiction, proof visual, or payoff in the first beat.")


def score_source_proof(text: str, brief_result: dict[str, Any]) -> dict[str, Any]:
    source_hits = count_terms(text, VISUAL_TERMS)
    source_links = int(brief_result.get("source_link_count") or 0)
    evidence = [f"{source_hits} source/visual proof terms"]
    if source_links:
        evidence.append(f"{source_links} concrete source links")
    score = 2 if source_hits >= 6 or source_links >= 2 else 1 if source_hits >= 3 or source_links >= 1 else 0
    return category(score, evidence, "Bind major beats to code, UI, docs, terminal output, diagrams, screenshots, or concrete source links.")


def score_term_category(text: str, terms: list[str], label: str, strong: int, partial: int, fix: str) -> dict[str, Any]:
    hits = count_terms(text, terms)
    score = 2 if hits >= strong else 1 if hits >= partial else 0
    return category(score, [f"{hits} {label} terms"], fix)


def score_transition_punctuation(text: str) -> dict[str, Any]:
    transition_hits = count_terms(text, TRANSITION_TERMS)
    purpose_hits = count_terms(text, TRANSITION_PURPOSE_TERMS)
    score = 2 if transition_hits >= 4 and purpose_hits >= 3 else 1 if transition_hits >= 2 and purpose_hits >= 1 else 0
    return category(
        score,
        [f"{transition_hits} transition terms", f"{purpose_hits} transition-purpose terms"],
        "Use cuts, zooms, inserts, or wipes as punctuation for proof, joke, warning, callback, or state change beats.",
    )


def score_script_moves(text: str) -> dict[str, Any]:
    hits = count_terms(text, SCRIPT_MOVE_TERMS)
    has_callback = "callback" in text
    score = 2 if hits >= 7 and has_callback else 1 if hits >= 4 else 0
    evidence = [f"{hits} script-move terms"]
    if has_callback:
        evidence.append("callback present")
    return category(score, evidence, "Use claim, define, prove, contrast, warning, tradeoff, and callback moves.")


def blueprint_info(path: Path | None, warnings: list[str]) -> dict[str, Any] | None:
    data = load_json(path, warnings, "pattern blueprint")
    if data is None:
        return None
    arrays = {
        key: len(data.get(key, [])) if isinstance(data.get(key), list) else 0
        for key in ["visualSources", "animationAtoms", "transitionTypes", "audioRoles", "scriptMoves", "beatGuidance"]
    }
    return {
        "ok": data.get("ok"),
        "selectedFormat": data.get("selectedFormat"),
        "arrays": arrays,
    }


def apply_blueprint_bonus(categories: dict[str, dict[str, Any]], blueprint: dict[str, Any] | None) -> list[str]:
    bonuses: list[str] = []
    if not blueprint or blueprint.get("ok") is not True:
        return bonuses
    arrays = blueprint.get("arrays", {})
    blueprint_checks = [
        ("visual_atoms", "visualSources"),
        ("animation_atoms", "animationAtoms"),
        ("transition_punctuation", "transitionTypes"),
        ("audio_roles", "audioRoles"),
        ("script_moves", "scriptMoves"),
    ]
    for category_name, array_name in blueprint_checks:
        count = int(arrays.get(array_name, 0))
        if count >= 3 and categories[category_name]["score"] < 2:
            categories[category_name]["score"] += 1
            categories[category_name]["evidence"].append(f"pattern blueprint has {count} {array_name}")
            bonuses.append(f"{category_name}:{array_name}")
    if int(arrays.get("beatGuidance", 0)) >= 8 and categories["format_pacing"]["score"] < 2:
        categories["format_pacing"]["score"] += 1
        categories["format_pacing"]["evidence"].append("pattern blueprint has 8+ beatGuidance rows")
        bonuses.append("format_pacing:beatGuidance")
    return bonuses


def style_penalties(text: str, brief_result: dict[str, Any]) -> list[str]:
    penalties: list[str] = []
    generic_fields = brief_result.get("beat_table_generic_fields") or []
    if generic_fields:
        penalties.append("generic beat-table fields")
    if brief_result.get("voiceover_generic_lines"):
        penalties.append("generic voiceover lines")
    if brief_result.get("voiceover_duplicate_lines"):
        penalties.append("repeated voiceover lines")
    slow_hits = count_terms(text, SLOW_GENERIC_STYLE_TERMS)
    hard_cut_hits = count_terms(text, ["hard cut", "jump cut", "punch-in", "smash", "snap zoom"])
    if slow_hits >= 4 and hard_cut_hits == 0:
        penalties.append("slow generic presentation vocabulary without fast-cut counterweight")
    return penalties


def score(args: argparse.Namespace) -> dict[str, Any]:
    warnings: list[str] = []
    failures: list[str] = []
    if not args.brief.exists():
        return {
            "ok": False,
            "failures": [f"brief not found: {args.brief}"],
            "warnings": warnings,
        }

    brief_text = read_text(args.brief)
    lowered = brief_text.lower()
    brief_result = check_video_brief.validate(
        brief_text,
        min_beats=8,
        require_voiceover=args.require_voiceover,
        require_source_links=args.require_source_links,
    )
    blueprint = blueprint_info(args.pattern_blueprint, warnings)
    if args.require_pattern_blueprint and blueprint is None:
        failures.append("pattern blueprint is required")
    elif args.require_pattern_blueprint and blueprint.get("ok") is not True:
        failures.append("pattern blueprint ok is not true")

    categories = {
        "format_pacing": score_format_pacing(lowered, brief_result),
        "hook_claim": score_hook_claim(lowered),
        "source_proof": score_source_proof(lowered, brief_result),
        "visual_atoms": score_term_category(
            lowered,
            VISUAL_TERMS,
            "visual/source atom",
            6,
            3,
            "Use corpus visual atoms such as logo/title anchor, UI proof, code proof, diagram proof, screenshots, or article inserts.",
        ),
        "animation_atoms": score_term_category(
            lowered,
            ANIMATION_TERMS,
            "animation atom",
            5,
            3,
            "Name concrete motion atoms such as punch-in zoom, highlight sweep, stack build, split-screen, trace, pan, or overlay.",
        ),
        "transition_punctuation": score_transition_punctuation(lowered),
        "audio_roles": score_term_category(
            lowered,
            AUDIO_ROLE_TERMS,
            "audio role",
            7,
            4,
            "Specify voiceover, bed, ducking, hits, whooshes, ticks, risers, dropouts, impacts, and final tail by timing.",
        ),
        "script_moves": score_script_moves(lowered),
    }
    bonuses = apply_blueprint_bonus(categories, blueprint)
    penalties = style_penalties(lowered, brief_result)
    raw_score = sum(int(item["score"]) for item in categories.values())
    penalty_points = len(penalties)
    final_score = max(0, raw_score - penalty_points)
    weak_categories = [name for name, item in categories.items() if int(item["score"]) < 2]

    if brief_result.get("failures"):
        failures.extend(f"brief: {failure}" for failure in brief_result["failures"])
    if final_score < args.min_score:
        failures.append(f"style fidelity score below threshold: {final_score} < {args.min_score}")
    if penalties:
        failures.append("style penalties: " + ", ".join(penalties))

    return {
        "ok": not failures,
        "score": final_score,
        "rawScore": raw_score,
        "maxScore": 16,
        "minScore": args.min_score,
        "penaltyPoints": penalty_points,
        "penalties": penalties,
        "weakCategories": weak_categories,
        "categories": categories,
        "brief": {
            "ok": brief_result.get("ok"),
            "beatRows": brief_result.get("beat_table_rows"),
            "voiceoverLineCount": brief_result.get("voiceover_line_count"),
            "sourceLinkCount": brief_result.get("source_link_count"),
            "failures": brief_result.get("failures"),
        },
        "patternBlueprint": blueprint,
        "inputDigests": {
            "briefSha256": sha256_file(args.brief),
            "patternBlueprintSha256": sha256_file(args.pattern_blueprint),
            "corpusSummarySha256": sha256_file(DEFAULT_SUMMARY),
        },
        "blueprintBonuses": bonuses,
        "failures": failures,
        "warnings": warnings,
    }


def main() -> int:
    args = parse_args()
    result = score(args)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8", newline="\n")
    if args.json:
        print(json.dumps(result, indent=2))
    elif result["ok"]:
        print(f"PASS awsome-videos style fidelity: {result['score']}/{result['maxScore']}")
    else:
        print("FAIL awsome-videos style fidelity")
        for failure in result["failures"]:
            print(f"- {failure}")
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
