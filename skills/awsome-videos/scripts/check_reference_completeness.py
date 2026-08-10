#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Check that the main awsome-videos reference covers the required source material."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import date
from pathlib import Path
from typing import Any


sys.dont_write_bytecode = True

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
DEFAULT_REFERENCE = SKILL_DIR / "references" / "awesome-fireship-patterns.md"
DEFAULT_PLAYBOOK = SKILL_DIR / "references" / "video-production-playbook.md"
DEFAULT_RUBRIC = SKILL_DIR / "references" / "evaluation-rubric.md"
DEFAULT_COMMANDS = SKILL_DIR / "references" / "command-contracts.md"
DEFAULT_VISUAL_WORKFLOW = SKILL_DIR / "references" / "visual-asset-composition-workflow.md"
DEFAULT_SKILL = SKILL_DIR / "SKILL.md"
DEFAULT_OPENAI_YAML = SKILL_DIR / "agents" / "openai.yaml"
DEFAULT_BRIEF_TEMPLATE = SKILL_DIR / "assets" / "templates" / "brief-template.md"
DEFAULT_IMAGE = SKILL_DIR / "assets" / "reference" / "representative-examples.jpg"
DEFAULT_SUMMARY = SKILL_DIR / "assets" / "reference" / "corpus-summary.json"
DEFAULT_SOURCES = SKILL_DIR / "assets" / "reference" / "corpus-sources.json"
PORTABLE_SKILL_ENV = "$env:AWSOME_VIDEOS_SKILL"
FORBIDDEN_RUNTIME_DOC_PATHS = ["skills/awsome-videos", "skills\\awsome-videos"]

REQUIRED_GROUPS: dict[str, list[str]] = {
    "corpus_provenance": [
        "2025-07-06",
        "2026-07-06",
        "181 public videos",
        "105 Awesome",
        "76 Fireship",
        "Members-only",
    ],
    "example_image": [
        "representative-examples.jpg",
        "Representative Awesome and Fireship frames",
    ],
    "corpus_summary_asset": [
        "assets/reference/corpus-summary.json",
        "assets/reference/corpus-sources.json",
        "machine-readable corpus summary",
        "patternTaxonomy",
        "artifactAudit",
        "source manifest",
    ],
    "video_types": [
        "opinionated tech explainer",
        "trend/news commentary",
        "tutorial/overview",
        "compressed explainer",
        "60-160 seconds",
    ],
    "visual_animation_patterns": [
        "Logo/title anchor",
        "UI proof",
        "Code proof",
        "Diagram proof",
        "Punch-in zoom",
        "Highlight sweep",
        "Stack build",
    ],
    "transition_patterns": [
        "hard cut",
        "punch-in",
        "match cut",
        "glitch",
        "proof point",
    ],
    "audio_patterns": [
        "audioProfile",
        "median 0.0035",
        "Background bed",
        "Hit/stinger",
        "Whoosh/tick",
        "Riser",
        "duck",
    ],
    "script_patterns": [
        "Open with a claim",
        "contrast pairs",
        "reset line",
        "callback",
        "voiceover placeholders",
        "repeated filler",
    ],
    "simple_commands": [
        "command-contracts.md",
        "check_runtime_tools.py",
        "--require-render-tools",
        "PASS awsome-videos runtime preflight",
        "check_video_brief.py",
        "select_video_patterns.py",
        "selectedFormat",
        "beatGuidance",
        "pattern-blueprint.json",
        "--require-pattern-blueprint",
        "--require-voiceover",
        "--require-source-links",
        "source_link_count",
        "scaffold_production_package.py",
        "extract_voiceover_cues.py",
        "voiceover-cues.json",
        "--require-beat-match",
        "cueCount",
        "beatCueMismatches",
        "create_concept_renderer.py",
        "check_renderer_contract.py",
        "nonblank screenshot samples",
        "render_concept_video.py",
        "--capture-fps",
        "--require-all-brief-beats",
        "briefBeatCoverageOk",
        "--motion-report",
        "motion-report.json",
        "audio-report.json",
        "--require-audio-report",
        "--require-final-audio",
        "paths.finalAudio",
        "finalAudioDurationOk",
        "missingFinalAudioCommandTerms",
        "sourceDurationSeconds",
        "--final-audio-duration-tolerance",
        "nonblank contact sheet",
        "score_style_fidelity.py",
        "style-fidelity.json",
        "--style-fidelity-report",
        "--require-style-fidelity-report",
        "--min-style-fidelity-score",
        "PASS awsome-videos style fidelity",
        "penalties",
        "score_video_readiness.py",
        "--min-readiness-score",
        "weakCategories",
        "--require-final-review-notes",
        "Legibility check",
        "Beat coverage check",
        "Visual mechanism check",
        "Pacing/transition check",
        "Source-binding check",
        "Audio sync check",
        "--require-renderer-beat-coverage",
        "check_production_package.py",
        "check_reference_completeness.py",
    ],
    "expected_outputs": [
        "PASS awsome-videos brief",
        "PASS awsome-videos pattern blueprint",
        "PASS awsome-videos style fidelity",
        '"ok": true',
        "score at least 12/16",
        "score at least 18/24",
        "PASS awsome-videos package",
        "PASS awsome-videos reference",
    ],
}


EXPECTED_SUMMARY_VALUES: dict[str, Any] = {
    "analysisWindow.startDate": "2025-07-06",
    "analysisWindow.endDate": "2026-07-06",
    "analysisWindow.inclusive": True,
    "scope.totalPublicVideos": 181,
    "artifactCounts.localLowResolutionMp4": 181,
    "artifactCounts.thumbnails": 181,
    "artifactCounts.englishVttFiles": 528,
    "artifactCounts.representativeFrameJpegs": 48,
    "artifactCounts.representativeContactSheets": 1,
    "artifactAudit.date": "2026-07-07",
    "artifactAudit.status": "passed",
    "artifactAudit.downloadedMp4": 181,
    "artifactAudit.downloadedThumbnails": 181,
    "artifactAudit.downloadedVtt": 528,
    "artifactAudit.analysisRows": 181,
    "artifactAudit.classificationRows": 181,
    "artifactAudit.visualMetricRows": 181,
    "artifactAudit.transcriptRows": 181,
    "artifactAudit.representativeExamples": 8,
    "artifactAudit.audioSilenceExamples": 8,
    "artifactAudit.representativeFrameDirectories": 8,
    "artifactAudit.frameJpgFiles": 49,
    "artifactAudit.missingReferencedPaths": 0,
    "artifactAudit.failures": 0,
    "artifactAudit.warnings": 0,
    "representativeExamples.count": 8,
    "sourceManifest.path": "assets/reference/corpus-sources.json",
    "sourceManifest.totalEntries": 181,
    "sourceManifest.channelCounts.Awesome": 105,
    "sourceManifest.channelCounts.Fireship": 76,
    "sourceManifest.sourceIdSha256": "3ba23e8ab3df28ba6f4a2ef894ee69a932812a8b8fc74097dd1b7ea4f422bd5e",
    "audioProfile.representativeExamples": 8,
    "audioProfile.medianSilenceRatio": 0.0035,
    "audioProfile.maxSilenceRatio": 0.041,
    "audioProfile.nearContinuousAudio": True,
}

EXPECTED_DISTRIBUTION_TOTALS = {
    "distributions.videoTypes": 181,
    "distributions.transitionProfiles": 181,
    "distributions.visualStyles": 181,
    "distributions.scriptStyles": 181,
}

REQUIRED_TAXONOMY_NAMES = {
    "patternTaxonomy.videoTypes": [
        "compressed explainer",
        "trend/news commentary",
        "tutorial/overview",
        "deep walkthrough",
    ],
    "patternTaxonomy.visualSources": [
        "logo/title anchor",
        "UI proof",
        "code proof",
        "diagram proof",
        "human/context insert",
        "meme/editorial insert",
    ],
    "patternTaxonomy.animationAtoms": [
        "punch-in zoom",
        "fast pan",
        "highlight sweep",
        "stack build",
        "split-screen contrast",
        "counter/ticker",
        "diagram trace",
    ],
    "patternTaxonomy.transitionTypes": [
        "hard cut",
        "punch-in",
        "match cut",
        "glitch/wipe",
        "snap zoom",
        "title reset",
    ],
    "patternTaxonomy.audioRoles": [
        "background bed",
        "hit/stinger",
        "whoosh/tick",
        "low impact",
        "riser",
        "dropout",
        "final tail",
    ],
    "patternTaxonomy.scriptMoves": [
        "claim hook",
        "one-sentence context",
        "contrast pair",
        "reset line",
        "technical joke",
        "warning beat",
        "callback",
    ],
}

REQUIRED_COMMAND_CONTRACT_TERMS = [
    "check_video_brief.py",
    "--require-voiceover",
    "--require-source-links",
    "extract_voiceover_cues.py",
    "--require-beat-match",
    "check_video_artifact.py",
    "--require-audio-report",
    "--require-final-audio",
    "check_production_package.py",
    "--require-final-review-notes",
    "--require-renderer-beat-coverage",
    "--min-readiness-score",
    "--style-fidelity-report",
    "--require-style-fidelity-report",
    "--min-style-fidelity-score",
    "scaffold_production_package.py",
    "select_video_patterns.py",
    "create_concept_renderer.py",
    "check_renderer_contract.py",
    "check_visual_contract.py",
    "--require-ready-assets",
    "--require-reviewed-scenes",
    "--require-visual-ids",
    "--forbid-scaffold-renderer",
    "render_concept_video.py",
    "--capture-fps",
    "--require-all-brief-beats",
    "briefBeatCoverageOk",
    "--motion-report",
    "score_video_readiness.py",
    "score_style_fidelity.py",
    "PASS awsome-videos style fidelity",
    "finalize_production_notes.py",
    "test_validators.py",
    "check_reference_completeness.py",
    "check_runtime_tools.py",
    "--require-render-tools",
    "PASS awsome-videos runtime preflight",
    "PASS awsome-videos brief",
    "PASS awsome-videos video",
    "PASS awsome-videos package",
    '"ok": true',
    "finalAudioDurationOk",
    "beatCueMismatches",
    "weakCategories",
]


def contains_all(text: str, phrases: list[str]) -> list[str]:
    lowered = text.lower()
    return [phrase for phrase in phrases if phrase.lower() not in lowered]


def fenced_code_blocks(text: str) -> list[str]:
    matches = re.finditer(
        r"(?P<fence>```|~~~)[a-zA-Z0-9_-]*\n(?P<body>.*?)(?P=fence)",
        text,
        flags=re.DOTALL,
    )
    return [match.group("body") for match in matches]


def check_playbook_contracts(reference_text: str, playbook: Path, skill: Path) -> dict[str, Any]:
    failures: list[str] = []
    if not playbook.exists():
        return {
            "ok": False,
            "path": str(playbook),
            "skillPath": str(skill),
            "failures": [f"playbook not found: {playbook}"],
        }

    playbook_text = playbook.read_text(encoding="utf-8")
    skill_text = skill.read_text(encoding="utf-8") if skill.exists() else ""
    for label, text in {
        "reference": reference_text,
        "skill": skill_text,
    }.items():
        if "60-160 seconds" not in text:
            failures.append(f"{label} compressed explainer timing is missing 60-160 seconds")
        if "Target 90-160 seconds." in text or "`compressed explainer`: 90-160 seconds" in text:
            failures.append(f"{label} still uses stale 90-160-only compressed explainer timing")

    sequence_text = playbook_text.split("## Project Layout", 1)[0]
    numbers = [int(match.group(1)) for match in re.finditer(r"^(\d+)\. ", sequence_text, flags=re.MULTILINE)]
    expected_numbers = list(range(1, 17))
    if numbers != expected_numbers:
        failures.append(f"production sequence numbering expected {expected_numbers}, found {numbers}")

    invalid_video_flags: list[str] = []
    for block in fenced_code_blocks(playbook_text):
        if "check_video_artifact.py" in block and "--min-readiness-score" in block:
            invalid_video_flags.append("--min-readiness-score")
    if invalid_video_flags:
        failures.append("check_video_artifact.py examples include invalid flags: " + ", ".join(sorted(set(invalid_video_flags))))

    required_style_terms = [
        "score_style_fidelity.py",
        "--pattern-blueprint",
        "--require-pattern-blueprint",
        "--style-fidelity-report",
        "--require-style-fidelity-report",
        "--min-style-fidelity-score",
        "style-fidelity.json",
        "--capture-fps",
        "--require-all-brief-beats",
        "--require-renderer-beat-coverage",
        "briefBeatCoverageOk",
    ]
    missing_style_terms = contains_all(playbook_text, required_style_terms)
    if missing_style_terms:
        failures.append("playbook missing style-fidelity gate terms: " + ", ".join(missing_style_terms))

    return {
        "ok": not failures,
        "path": str(playbook),
        "skillPath": str(skill),
        "sequenceNumbers": numbers,
        "expectedSequenceNumbers": expected_numbers,
        "missingStyleFidelityTerms": missing_style_terms,
        "failures": failures,
    }


def check_portable_command_docs(paths: dict[str, Path]) -> dict[str, Any]:
    failures: list[str] = []
    files: dict[str, dict[str, Any]] = {}

    for label, path in paths.items():
        if not path.exists():
            failures.append(f"{label} not found: {path}")
            files[label] = {"path": str(path), "exists": False}
            continue

        text = path.read_text(encoding="utf-8")
        normalized = text.replace("\\", "/")
        forbidden_lines = [
            line_number
            for line_number, line in enumerate(normalized.splitlines(), start=1)
            if any(forbidden.replace("\\", "/") in line for forbidden in FORBIDDEN_RUNTIME_DOC_PATHS)
        ]
        command_blocks = [block for block in fenced_code_blocks(text) if "uv run --script" in block]
        command_blocks_missing_env = [
            index + 1
            for index, block in enumerate(command_blocks)
            if PORTABLE_SKILL_ENV not in block and "{{SKILL_PATH}}" not in block
        ]
        command_lines_missing_env = [
            line_number
            for line_number, line in enumerate(text.splitlines(), start=1)
            if "uv run --script" in line and PORTABLE_SKILL_ENV not in line and "{{SKILL_PATH}}" not in line
        ]
        env_mentions = text.count(PORTABLE_SKILL_ENV)

        if forbidden_lines:
            failures.append(
                f"{label} has non-portable awsome-videos command path on lines: "
                + ", ".join(str(line) for line in forbidden_lines[:8])
            )
        if command_blocks_missing_env:
            failures.append(
                f"{label} has uv script command blocks without {PORTABLE_SKILL_ENV}: "
                + ", ".join(str(index) for index in command_blocks_missing_env[:8])
            )
        if command_lines_missing_env:
            failures.append(
                f"{label} has uv script command lines without {PORTABLE_SKILL_ENV}: "
                + ", ".join(str(line) for line in command_lines_missing_env[:8])
            )

        files[label] = {
            "path": str(path),
            "exists": True,
            "commandBlockCount": len(command_blocks),
            "commandBlocksMissingEnv": command_blocks_missing_env,
            "commandLinesMissingEnv": command_lines_missing_env,
            "envMentions": env_mentions,
            "forbiddenLines": forbidden_lines,
        }

    skill_info = files.get("skill", {})
    if skill_info.get("exists"):
        required_skill_mentions = 2 if int(skill_info.get("commandBlockCount", 0)) else 1
        if int(skill_info.get("envMentions", 0)) < required_skill_mentions:
            failures.append(f"skill does not define and use {PORTABLE_SKILL_ENV} clearly")

    return {
        "ok": not failures,
        "envVariable": PORTABLE_SKILL_ENV,
        "files": files,
        "failures": failures,
    }


def check_command_contracts(commands: Path, max_bytes: int = 10000) -> dict[str, Any]:
    failures: list[str] = []
    if not commands.exists():
        return {
            "ok": False,
            "path": str(commands),
            "bytes": 0,
            "failures": [f"command contracts reference not found: {commands}"],
        }

    text = commands.read_text(encoding="utf-8")
    byte_count = len(text.encode("utf-8"))
    missing = contains_all(text, REQUIRED_COMMAND_CONTRACT_TERMS)
    command_blocks = [block for block in fenced_code_blocks(text) if "uv run --script" in block]
    envless_blocks = [
        index + 1
        for index, block in enumerate(command_blocks)
        if PORTABLE_SKILL_ENV not in block and "{{SKILL_PATH}}" not in block
    ]

    if missing:
        failures.append("command contracts missing: " + ", ".join(missing))
    if len(command_blocks) < 8:
        failures.append(f"command contracts expected at least 8 uv command blocks, found {len(command_blocks)}")
    if envless_blocks:
        failures.append(
            f"command contracts have uv command blocks without {PORTABLE_SKILL_ENV}: "
            + ", ".join(str(index) for index in envless_blocks)
        )
    if byte_count > max_bytes:
        failures.append(f"command contracts reference is too large: {byte_count} > {max_bytes} bytes")

    return {
        "ok": not failures,
        "path": str(commands),
        "bytes": byte_count,
        "commandBlockCount": len(command_blocks),
        "commandBlocksMissingEnv": envless_blocks,
        "missing": missing,
        "maxBytes": max_bytes,
        "failures": failures,
    }


def check_visual_workflow_reference(path: Path, max_bytes: int = 10000) -> dict[str, Any]:
    failures: list[str] = []
    if not path.is_file():
        return {"ok": False, "path": str(path), "bytes": 0, "failures": [f"visual workflow missing: {path}"]}
    text = path.read_text(encoding="utf-8")
    byte_count = len(text.encode("utf-8"))
    required = [
        "source-to-video-director",
        "scene-composition-director",
        "scene-transition-director",
        "imagegen",
        "d3",
        "mermaid",
        "html-d3-anime-video-workflow",
        "source/asset-manifest.json",
        "source/composition-plan.json",
        "artifacts/reviews/visual-review.json",
        "skillRouting",
        "outputPaths",
        "proof",
        "armatureAnchors",
        "validationContract",
        "assetManifestSha256",
        "data-asset-src",
        "data-asset-sha256",
        "ffmpeg",
        "SHA-256",
        "wireframe",
        "correction",
        "isolated",
    ]
    missing = contains_all(text, required)
    if missing:
        failures.append("visual workflow missing terms: " + ", ".join(missing))
    if byte_count > max_bytes:
        failures.append(f"visual workflow is too large for progressive disclosure: {byte_count} > {max_bytes} bytes")
    return {
        "ok": not failures,
        "path": str(path),
        "bytes": byte_count,
        "missing": missing,
        "maxBytes": max_bytes,
        "failures": failures,
    }


def reference_command_lines(text: str) -> list[str]:
    lines: list[str] = []
    for block in fenced_code_blocks(text):
        for raw_line in block.splitlines():
            line = raw_line.strip()
            if "uv run --script" in line:
                lines.append(re.sub(r"\s+", " ", line))
    return lines


def check_reference_command_contracts(text: str) -> dict[str, Any]:
    requirements = {
        "check_renderer_contract.py": [
            "--brief",
            "--require-all-brief-beats",
            "--asset-manifest",
            "--composition-plan",
            "--require-visual-ids",
            "--screenshot-dir",
            "--output",
        ],
        "render_concept_video.py": [
            "--brief",
            "--require-all-brief-beats",
            "--capture-fps",
            "--render-state-report",
            "--motion-report",
            "--audio-report",
        ],
        "check_visual_contract.py": [
            "--asset-manifest",
            "--composition-plan",
            "--visual-review",
            "--video",
            "--require-ready-assets",
            "--require-specialist-routing",
            "--require-source-routing",
            "--require-reviewed-scenes",
            "--output",
        ],
        "score_style_fidelity.py": [
            "--pattern-blueprint",
            "--require-pattern-blueprint",
            "--require-source-links",
            "--output",
        ],
        "score_video_readiness.py": [
            "--renderer-report",
            "--asset-manifest",
            "--composition-plan",
            "--visual-review",
            "--visual-contract-report",
            "--require-visual-contract-report",
            "--require-source-links",
            "--output",
        ],
        "check_production_package.py": [
            "--require-source-links",
            "--asset-manifest",
            "--composition-plan",
            "--visual-review",
            "--visual-contract-report",
            "--require-visual-contract",
            "--require-ready-assets",
            "--require-specialist-routing",
            "--require-source-routing",
            "--require-reviewed-scenes",
            "--forbid-scaffold-renderer",
            "--require-renderer-beat-coverage",
            "--require-renderer-visual-coverage",
            "--require-style-fidelity-report",
            "--require-final-review-notes",
            "--require-motion-report",
        ],
    }
    lines = reference_command_lines(text)
    failures: list[str] = []
    missing_by_script: dict[str, list[str]] = {}
    matched_commands: dict[str, str] = {}

    for script, terms in requirements.items():
        matches = [line for line in lines if script in line]
        passing = [line for line in matches if all(term in line for term in terms)]
        if passing:
            matched_commands[script] = passing[0]
            missing_by_script[script] = []
            continue
        missing = terms if not matches else [term for term in terms if not any(term in line for line in matches)]
        missing_by_script[script] = missing
        failures.append(f"reference command for {script} missing required terms: {', '.join(missing)}")

    return {
        "ok": not failures,
        "commandLineCount": len(lines),
        "missingByScript": missing_by_script,
        "matchedCommands": matched_commands,
        "failures": failures,
    }


def extract_interface_value(text: str, key: str) -> str | None:
    match = re.search(rf"^\s{{2}}{re.escape(key)}:\s*\"([^\"]*)\"\s*$", text, flags=re.MULTILINE)
    return match.group(1) if match else None


def check_openai_yaml_metadata(path: Path) -> dict[str, Any]:
    failures: list[str] = []
    if not path.exists():
        return {
            "ok": False,
            "path": str(path),
            "failures": [f"agents/openai.yaml not found: {path}"],
        }

    text = path.read_text(encoding="utf-8")
    display_name = extract_interface_value(text, "display_name")
    short_description = extract_interface_value(text, "short_description")
    default_prompt = extract_interface_value(text, "default_prompt")

    if "interface:" not in text:
        failures.append("agents/openai.yaml is missing interface mapping")
    if not display_name:
        failures.append("interface.display_name missing or not quoted")
    elif "Awesome" not in display_name or "Fireship" not in display_name:
        failures.append("interface.display_name should name the Awesome/Fireship corpus")

    if not short_description:
        failures.append("interface.short_description missing or not quoted")
    else:
        length = len(short_description)
        if not 25 <= length <= 64:
            failures.append(f"interface.short_description should be 25 to 64 characters, found {length}")
        if "tech explainer" not in short_description.lower():
            failures.append("interface.short_description should mention tech explainers")

    if not default_prompt:
        failures.append("interface.default_prompt missing or not quoted")
    else:
        required_prompt_terms = ["$awsome-videos", "production-ready", "timed brief", "MP4", "validation reports"]
        missing_terms = [term for term in required_prompt_terms if term.lower() not in default_prompt.lower()]
        if missing_terms:
            failures.append("interface.default_prompt missing terms: " + ", ".join(missing_terms))

    return {
        "ok": not failures,
        "path": str(path),
        "displayName": display_name,
        "shortDescription": short_description,
        "shortDescriptionLength": len(short_description) if short_description else 0,
        "defaultPrompt": default_prompt,
        "failures": failures,
    }


def nested_get(data: dict[str, Any], dotted: str) -> Any:
    current: Any = data
    for part in dotted.split("."):
        if not isinstance(current, dict) or part not in current:
            return None
        current = current[part]
    return current


def read_json(path: Path) -> tuple[dict[str, Any] | None, list[str]]:
    if not path.exists():
        return None, [f"corpus summary not found: {path}"]
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return None, [f"corpus summary is not valid JSON: {exc}"]
    if not isinstance(data, dict):
        return None, ["corpus summary root is not an object"]
    return data, []


def named_items(data: Any) -> list[str]:
    if not isinstance(data, list):
        return []
    names: list[str] = []
    for item in data:
        if isinstance(item, dict) and isinstance(item.get("name"), str):
            names.append(item["name"])
    return names


def check_pattern_taxonomy(data: dict[str, Any]) -> dict[str, Any]:
    failures: list[str] = []
    groups: dict[str, dict[str, Any]] = {}

    for dotted, required_names in REQUIRED_TAXONOMY_NAMES.items():
        items = nested_get(data, dotted)
        names = named_items(items)
        missing = [name for name in required_names if name not in names]
        thin_items: list[str] = []
        if isinstance(items, list):
            for item in items:
                if not isinstance(item, dict):
                    continue
                name = item.get("name")
                detail_keys = [key for key in item if key != "name" and str(item.get(key, "")).strip()]
                if isinstance(name, str) and len(detail_keys) < 1:
                    thin_items.append(name)
        else:
            failures.append(f"{dotted} is missing or not a list")

        if missing:
            failures.append(f"{dotted} missing names: {', '.join(missing)}")
        if thin_items:
            failures.append(f"{dotted} has items without usage detail: {', '.join(thin_items)}")
        groups[dotted] = {
            "ok": not missing and not thin_items and isinstance(items, list),
            "count": len(names),
            "names": names,
            "missing": missing,
            "thinItems": thin_items,
        }

    return {
        "ok": not failures,
        "groups": groups,
        "failures": failures,
    }


def parse_iso_date(value: Any) -> date | None:
    if not isinstance(value, str):
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


def check_corpus_sources(sources: Path, summary_data: dict[str, Any] | None = None) -> dict[str, Any]:
    failures: list[str] = []
    data, load_failures = read_json(sources)
    if data is None:
        return {
            "ok": False,
            "path": str(sources),
            "bytes": sources.stat().st_size if sources.exists() else 0,
            "failures": load_failures,
        }

    entries = data.get("entries")
    if not isinstance(entries, list):
        entries = []
        failures.append("entries is missing or not a list")

    start = parse_iso_date(nested_get(data, "analysisWindow.startDate"))
    end = parse_iso_date(nested_get(data, "analysisWindow.endDate"))
    if start != date(2025, 7, 6):
        failures.append(f"analysisWindow.startDate expected 2025-07-06, found {nested_get(data, 'analysisWindow.startDate')!r}")
    if end != date(2026, 7, 6):
        failures.append(f"analysisWindow.endDate expected 2026-07-06, found {nested_get(data, 'analysisWindow.endDate')!r}")
    if nested_get(data, "analysisWindow.inclusive") is not True:
        failures.append("analysisWindow.inclusive expected true")

    ids: list[str] = []
    canonical_ids: list[str] = []
    channel_counts: dict[str, int] = {}
    out_of_window: list[str] = []
    bad_urls: list[str] = []
    non_public: list[str] = []
    missing_fields: list[str] = []

    for index, entry in enumerate(entries):
        if not isinstance(entry, dict):
            failures.append(f"entry {index} is not an object")
            continue
        channel = entry.get("channel")
        video_id = entry.get("id")
        upload_date = parse_iso_date(entry.get("uploadDate"))
        url = entry.get("url")
        availability = entry.get("availability")
        title = entry.get("title")
        duration = entry.get("durationSeconds")

        for field, value in [
            ("channel", channel),
            ("id", video_id),
            ("title", title),
            ("uploadDate", upload_date),
            ("durationSeconds", duration),
            ("url", url),
            ("availability", availability),
        ]:
            if value in (None, ""):
                missing_fields.append(f"{index}:{field}")
        if not isinstance(channel, str) or channel not in {"Awesome", "Fireship"}:
            failures.append(f"entry {index} has unexpected channel {channel!r}")
            continue
        if not isinstance(video_id, str) or not re.fullmatch(r"[-_A-Za-z0-9]{11}", video_id):
            failures.append(f"entry {index} has invalid video id {video_id!r}")
            continue
        if upload_date is None or start is None or end is None or not (start <= upload_date <= end):
            out_of_window.append(video_id)
        if not isinstance(url, str) or url != f"https://www.youtube.com/watch?v={video_id}":
            bad_urls.append(video_id)
        if availability != "public":
            non_public.append(video_id)
        if not isinstance(duration, int) or duration <= 0:
            failures.append(f"entry {index} has invalid durationSeconds {duration!r}")
        if not isinstance(title, str) or len(title.strip()) < 3:
            failures.append(f"entry {index} has missing or thin title")
        ids.append(video_id)
        canonical_ids.append(f"{channel}:{video_id}")
        channel_counts[channel] = channel_counts.get(channel, 0) + 1

    duplicates = sorted({video_id for video_id in ids if ids.count(video_id) > 1})
    if duplicates:
        failures.append("duplicate video ids: " + ", ".join(duplicates))
    if missing_fields:
        failures.append("source entries missing fields: " + ", ".join(missing_fields[:20]))
    if out_of_window:
        failures.append("source entries outside analysis window: " + ", ".join(out_of_window[:20]))
    if bad_urls:
        failures.append("source entries with unexpected YouTube URLs: " + ", ".join(bad_urls[:20]))
    if non_public:
        failures.append("source entries not marked public: " + ", ".join(non_public[:20]))

    expected_counts = {"Awesome": 105, "Fireship": 76}
    if len(entries) != 181:
        failures.append(f"source entries expected 181, found {len(entries)}")
    for channel, expected in expected_counts.items():
        if channel_counts.get(channel) != expected:
            failures.append(f"source entries for {channel} expected {expected}, found {channel_counts.get(channel)}")

    actual_hash = hashlib.sha256("\n".join(canonical_ids).encode("utf-8")).hexdigest()
    expected_hash = data.get("sourceIdSha256")
    if actual_hash != expected_hash:
        failures.append(f"sourceIdSha256 expected {expected_hash!r}, recomputed {actual_hash!r}")

    if summary_data is not None:
        if nested_get(summary_data, "sourceManifest.totalEntries") != len(entries):
            failures.append("summary sourceManifest.totalEntries differs from source entries")
        if nested_get(summary_data, "sourceManifest.channelCounts.Awesome") != channel_counts.get("Awesome"):
            failures.append("summary sourceManifest Awesome count differs from source entries")
        if nested_get(summary_data, "sourceManifest.channelCounts.Fireship") != channel_counts.get("Fireship"):
            failures.append("summary sourceManifest Fireship count differs from source entries")
        if nested_get(summary_data, "sourceManifest.sourceIdSha256") != actual_hash:
            failures.append("summary sourceManifest.sourceIdSha256 differs from source entries")

    return {
        "ok": not failures,
        "path": str(sources),
        "bytes": sources.stat().st_size,
        "entryCount": len(entries),
        "channelCounts": channel_counts,
        "sourceIdSha256": actual_hash,
        "firstUploadDate": min((entry.get("uploadDate") for entry in entries if isinstance(entry, dict)), default=None),
        "lastUploadDate": max((entry.get("uploadDate") for entry in entries if isinstance(entry, dict)), default=None),
        "failures": failures,
    }


def markdown_image_links(text: str) -> list[dict[str, str]]:
    links: list[dict[str, str]] = []
    pattern = re.compile(r"!\[([^\]]+)\]\(([^)]+)\)")
    for match in pattern.finditer(text):
        links.append({"alt": match.group(1).strip(), "target": match.group(2).strip()})
    return links


def check_reference_image_link(text: str, reference: Path, image: Path) -> dict[str, Any]:
    links = markdown_image_links(text)
    expected = image.resolve()
    matching_links: list[dict[str, str]] = []
    failures: list[str] = []

    for link in links:
        target = link["target"].split("#", 1)[0].split("?", 1)[0]
        if re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", target):
            continue
        resolved = (reference.parent / target).resolve()
        if resolved == expected:
            matching_links.append(link)

    if not matching_links:
        failures.append(f"reference does not embed the representative image link: {image.name}")
    else:
        has_alt = any("Representative Awesome and Fireship frames" in link["alt"] for link in matching_links)
        if not has_alt:
            failures.append("representative image link is missing the expected alt text")

    return {
        "ok": not failures,
        "links": links,
        "matchingLinks": matching_links,
        "expectedImage": str(image),
        "failures": failures,
    }


def check_corpus_summary(summary: Path) -> dict[str, Any]:
    failures: list[str] = []
    data, load_failures = read_json(summary)
    if data is None:
        return {
            "ok": False,
            "path": str(summary),
            "bytes": summary.stat().st_size if summary.exists() else 0,
            "failures": load_failures,
        }

    for dotted, expected in EXPECTED_SUMMARY_VALUES.items():
        actual = nested_get(data, dotted)
        if actual != expected:
            failures.append(f"{dotted} expected {expected!r}, found {actual!r}")

    audio_profile = nested_get(data, "audioProfile")
    audio_info: dict[str, Any] = {}
    if not isinstance(audio_profile, dict):
        failures.append("audioProfile is missing or not an object")
    else:
        audio_info = {
            "representativeExamples": audio_profile.get("representativeExamples"),
            "medianSilenceRatio": audio_profile.get("medianSilenceRatio"),
            "maxSilenceRatio": audio_profile.get("maxSilenceRatio"),
            "nearContinuousAudio": audio_profile.get("nearContinuousAudio"),
        }

    channels = nested_get(data, "scope.channels")
    if not isinstance(channels, list):
        failures.append("scope.channels is missing or not a list")
    else:
        channel_counts = {item.get("handle"): item.get("publicVideos") for item in channels if isinstance(item, dict)}
        if channel_counts.get("@awesome-coding") != 105:
            failures.append("@awesome-coding publicVideos expected 105")
        if channel_counts.get("@Fireship") != 76:
            failures.append("@Fireship publicVideos expected 76")

    for dotted, expected_total in EXPECTED_DISTRIBUTION_TOTALS.items():
        distribution = nested_get(data, dotted)
        if not isinstance(distribution, dict):
            failures.append(f"{dotted} is missing or not an object")
            continue
        total = sum(value for value in distribution.values() if isinstance(value, int))
        if total != expected_total:
            failures.append(f"{dotted} total expected {expected_total}, found {total}")

    taxonomy_info = check_pattern_taxonomy(data)
    if not taxonomy_info["ok"]:
        failures.extend(taxonomy_info["failures"])

    return {
        "ok": not failures,
        "path": str(summary),
        "bytes": summary.stat().st_size,
        "audioProfile": audio_info,
        "artifactAudit": nested_get(data, "artifactAudit"),
        "contactSheet": nested_get(data, "representativeExamples.contactSheet"),
        "sourceManifest": nested_get(data, "sourceManifest"),
        "patternTaxonomy": taxonomy_info,
        "failures": failures,
    }


def parse_channel_table(text: str) -> dict[str, dict[str, float]]:
    rows: dict[str, dict[str, float]] = {}
    pattern = re.compile(
        r"^\|\s*(Awesome|Fireship)\s*\|\s*(\d+)\s*\|\s*([0-9.]+)\s*\|\s*([0-9.]+)s\s*\|\s*([0-9.]+)\s+cuts/min\s*\|\s*([0-9.]+)\s+WPM\s*\|$",
        re.IGNORECASE | re.MULTILINE,
    )
    for match in pattern.finditer(text):
        name = match.group(1).lower()
        rows[name] = {
            "count": float(match.group(2)),
            "durationMinutesTotal": float(match.group(3)),
            "medianDurationSeconds": float(match.group(4)),
            "medianCutProxyPerMinute": float(match.group(5)),
            "medianWordsPerMinute": float(match.group(6)),
        }
    return rows


def parse_distribution_line(text: str, label: str, expected_keys: list[str] | None = None) -> dict[str, int]:
    match = re.search(rf"^- {re.escape(label)}:\s*(.+)$", text, flags=re.IGNORECASE | re.MULTILINE)
    if not match:
        return {}
    line = match.group(1).strip().rstrip(".")
    if expected_keys:
        values: dict[str, int] = {}
        for key in expected_keys:
            key_match = re.search(rf"{re.escape(key)}\s+(\d+)(?:,|$)", line)
            if key_match:
                values[key] = int(key_match.group(1))
        return values
    values: dict[str, int] = {}
    for part in line.split(","):
        item = part.strip().rstrip(".")
        item_match = re.match(r"(.+?)\s+(\d+)$", item)
        if item_match:
            values[item_match.group(1).strip()] = int(item_match.group(2))
    return values


def compare_float(actual: float | None, expected: float | None, tolerance: float) -> bool:
    return actual is not None and expected is not None and abs(actual - expected) <= tolerance


def check_markdown_summary_consistency(text: str, summary: Path) -> dict[str, Any]:
    failures: list[str] = []
    data, load_failures = read_json(summary)
    if data is None:
        return {"ok": False, "failures": load_failures}

    channels = parse_channel_table(text)
    expected_channels = nested_get(data, "scope.channels")
    metrics = nested_get(data, "channelMetrics")
    if not isinstance(expected_channels, list) or not isinstance(metrics, dict):
        failures.append("summary is missing scope.channels or channelMetrics")
    else:
        for item in expected_channels:
            if not isinstance(item, dict):
                continue
            name = str(item.get("name", "")).lower()
            row = channels.get(name)
            metric = metrics.get(name)
            if not row:
                failures.append(f"reference is missing channel table row for {name}")
                continue
            if not isinstance(metric, dict):
                failures.append(f"summary is missing channelMetrics.{name}")
                continue
            if int(row["count"]) != item.get("publicVideos"):
                failures.append(f"{name} table count differs from summary")
            numeric_checks = [
                ("durationMinutesTotal", 0.05),
                ("medianDurationSeconds", 0.5),
                ("medianCutProxyPerMinute", 0.01),
                ("medianWordsPerMinute", 0.5),
            ]
            for field, tolerance in numeric_checks:
                if not compare_float(row.get(field), float(metric.get(field)), tolerance):
                    failures.append(f"{name} table {field} differs from summary")

    distribution_labels = {
        "Video types": "distributions.videoTypes",
        "Transitions": "distributions.transitionProfiles",
        "Visual style": "distributions.visualStyles",
        "Script style": "distributions.scriptStyles",
    }
    for label, dotted in distribution_labels.items():
        expected = nested_get(data, dotted)
        if not isinstance(expected, dict):
            failures.append(f"summary is missing {dotted}")
            continue
        actual = parse_distribution_line(text, label, list(expected))
        if actual != expected:
            failures.append(f"reference {label} distribution differs from summary")

    total = nested_get(data, "scope.totalPublicVideos")
    if isinstance(total, int):
        for label, dotted in distribution_labels.items():
            expected = nested_get(data, dotted)
            if isinstance(expected, dict) and sum(value for value in expected.values() if isinstance(value, int)) != total:
                failures.append(f"summary {dotted} does not total {total}")

    return {
        "ok": not failures,
        "failures": failures,
        "channelRows": sorted(channels),
        "distributionLabels": sorted(distribution_labels),
    }


def check_reference(
    reference: Path,
    image: Path,
    min_image_bytes: int,
    summary: Path | None = None,
    sources: Path | None = None,
) -> dict[str, Any]:
    failures: list[str] = []
    warnings: list[str] = []
    summary_path = summary or DEFAULT_SUMMARY
    sources_path = sources or DEFAULT_SOURCES

    if not reference.exists():
        return {
            "ok": False,
            "reference": str(reference),
            "image": str(image),
            "summary": str(summary_path),
            "sources": str(sources_path),
            "referenceBytes": 0,
            "failures": [f"reference file not found: {reference}"],
            "warnings": warnings,
            "groups": {},
        }

    text = reference.read_text(encoding="utf-8")
    byte_count = len(text.encode("utf-8"))
    groups: dict[str, dict[str, Any]] = {}
    for group, phrases in REQUIRED_GROUPS.items():
        missing = contains_all(text, phrases)
        groups[group] = {"ok": not missing, "missing": missing, "required": phrases}
        if missing:
            failures.append(f"{group} missing: {', '.join(missing)}")

    if not image.exists():
        failures.append(f"example image not found: {image}")
        image_info: dict[str, Any] = {"exists": False, "bytes": 0}
    else:
        image_bytes = image.stat().st_size
        image_info = {"exists": True, "bytes": image_bytes}
        if image_bytes < min_image_bytes:
            failures.append(f"example image is too small: {image_bytes} bytes")

    image_link_info = check_reference_image_link(text, reference, image)
    if not image_link_info["ok"]:
        failures.extend(image_link_info["failures"])

    summary_info = check_corpus_summary(summary_path)
    if not summary_info["ok"]:
        failures.extend(summary_info["failures"])
    if summary_info.get("contactSheet") != image.name:
        failures.append(
            f"representativeExamples.contactSheet expected {image.name!r}, found {summary_info.get('contactSheet')!r}"
        )
    summary_data, _summary_load_failures = read_json(summary_path)
    source_info = check_corpus_sources(sources_path, summary_data)
    if not source_info["ok"]:
        failures.extend(source_info["failures"])
    consistency_info = check_markdown_summary_consistency(text, summary_path)
    if not consistency_info["ok"]:
        failures.extend(consistency_info["failures"])
    playbook_info = check_playbook_contracts(text, DEFAULT_PLAYBOOK, DEFAULT_SKILL)
    if not playbook_info["ok"]:
        failures.extend(playbook_info["failures"])
    command_contracts_info = check_command_contracts(DEFAULT_COMMANDS)
    if not command_contracts_info["ok"]:
        failures.extend(command_contracts_info["failures"])
    visual_workflow_info = check_visual_workflow_reference(DEFAULT_VISUAL_WORKFLOW)
    if not visual_workflow_info["ok"]:
        failures.extend(visual_workflow_info["failures"])
    openai_yaml_info = check_openai_yaml_metadata(DEFAULT_OPENAI_YAML)
    if not openai_yaml_info["ok"]:
        failures.extend(openai_yaml_info["failures"])
    portable_docs_info = check_portable_command_docs(
        {
            "skill": DEFAULT_SKILL,
            "reference": reference,
            "playbook": DEFAULT_PLAYBOOK,
            "rubric": DEFAULT_RUBRIC,
            "commandContracts": DEFAULT_COMMANDS,
            "visualWorkflow": DEFAULT_VISUAL_WORKFLOW,
            "briefTemplate": DEFAULT_BRIEF_TEMPLATE,
        }
    )
    if not portable_docs_info["ok"]:
        failures.extend(portable_docs_info["failures"])
    reference_command_info = check_reference_command_contracts(text)
    if not reference_command_info["ok"]:
        failures.extend(reference_command_info["failures"])

    if byte_count > 15000:
        warnings.append(f"reference is getting large: {byte_count} bytes")
    if source_info.get("bytes", 0) > 50000:
        warnings.append(f"source manifest is getting large: {source_info.get('bytes')} bytes")

    return {
        "ok": not failures,
        "reference": str(reference),
        "image": str(image),
        "summary": str(summary_path),
        "sources": str(sources_path),
        "imageInfo": image_info,
        "summaryInfo": summary_info,
        "sourceInfo": source_info,
        "consistencyInfo": consistency_info,
        "imageLinkInfo": image_link_info,
        "playbookInfo": playbook_info,
        "commandContractsInfo": command_contracts_info,
        "visualWorkflowInfo": visual_workflow_info,
        "referenceCommandInfo": reference_command_info,
        "openaiYamlInfo": openai_yaml_info,
        "portableCommandDocsInfo": portable_docs_info,
        "referenceBytes": byte_count,
        "failures": failures,
        "warnings": warnings,
        "groups": groups,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Check awsome-videos reference completeness.")
    parser.add_argument("--reference", type=Path, default=DEFAULT_REFERENCE)
    parser.add_argument("--image", type=Path, default=DEFAULT_IMAGE)
    parser.add_argument("--summary", type=Path, default=DEFAULT_SUMMARY)
    parser.add_argument("--sources", type=Path, default=DEFAULT_SOURCES)
    parser.add_argument("--min-image-bytes", type=int, default=10000)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    result = check_reference(args.reference, args.image, args.min_image_bytes, args.summary, args.sources)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8", newline="\n")

    if args.json:
        print(json.dumps(result, indent=2))
    elif result["ok"]:
        print(f"PASS awsome-videos reference: {len(REQUIRED_GROUPS)} groups, image, corpus summary, and playbook contracts present")
    else:
        print("FAIL awsome-videos reference")
        for failure in result["failures"]:
            print(f"- {failure}")
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
