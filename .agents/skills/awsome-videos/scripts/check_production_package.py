#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["pillow>=10.0.0", "playwright>=1.45.0"]
# ///
"""Validate an awsome-videos production package."""

from __future__ import annotations

import argparse
from io import BytesIO
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

from PIL import Image, ImageChops, ImageStat

sys.dont_write_bytecode = True

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import check_video_artifact  # noqa: E402
import check_video_brief  # noqa: E402
import check_renderer_contract  # noqa: E402
import check_visual_contract  # noqa: E402
import score_video_readiness  # noqa: E402

PRODUCTION_NOTE_REQUIRED_SCRIPTS = [
    "check_video_brief.py",
    "render_concept_video.py",
    "check_video_artifact.py",
    "score_video_readiness.py",
    "score_style_fidelity.py",
    "check_production_package.py",
]

PRODUCTION_NOTE_REQUIRED_COMMAND_TERMS: dict[str, list[str]] = {
    "check_video_brief.py": [
        "--require-voiceover",
    ],
    "render_concept_video.py": [
        "--brief",
        "--require-all-brief-beats",
        "--contact-sheet",
        "--quality-report",
        "--motion-report",
        "--capture-manifest",
        "--render-state-report",
        "--audio-report",
        "--capture-fps",
    ],
    "check_video_artifact.py": [
        "--require-audio",
        "--audio-report",
        "--require-audio-report",
        "--contact-sheet",
        "--quality-report",
        "--motion-report",
        "--capture-manifest",
    ],
    "score_video_readiness.py": [
        "--require-voiceover",
        "--renderer-report",
        "--quality-report",
        "--motion-report",
        "--capture-manifest",
        "--audio-report",
        "--contact-sheet",
        "--output",
    ],
    "score_style_fidelity.py": [
        "--brief",
        "--pattern-blueprint",
        "--require-voiceover",
        "--require-pattern-blueprint",
        "--output",
    ],
    "check_production_package.py": [
        "--require-voiceover",
        "--production-notes",
        "--package-manifest",
        "--min-readiness-score",
        "--style-fidelity-report",
        "--min-style-fidelity-score",
        "--contact-sheet",
        "--quality-report",
        "--motion-report",
        "--capture-manifest",
        "--audio-report",
        "--require-audio-report",
        "--require-production-notes",
        "--require-package-manifest",
        "--require-style-fidelity-report",
        "--require-renderer-beat-coverage",
        "--require-contact-sheet",
        "--require-motion-report",
    ],
}

FINAL_AUDIO_COMMAND_TERMS: dict[str, list[str]] = {
    "render_concept_video.py": [
        "--audio-file",
    ],
    "check_video_artifact.py": [
        "--require-final-audio",
    ],
    "score_video_readiness.py": [
        "--require-final-audio",
    ],
    "check_production_package.py": [
        "--require-final-audio",
    ],
}

FINAL_REVIEW_STALE_RE = re.compile(
    r"\b(?:pending|tbd|todo|not run|not validated|needs validation|replace synthetic|unfinished)\b",
    re.IGNORECASE,
)

FINAL_REVIEW_REQUIRED_TERMS: dict[str, list[str]] = {
    "legibility check": ["legibility check"],
    "beat coverage check": ["beat coverage check"],
    "visual mechanism check": ["visual mechanism check"],
    "pacing/transition check": ["pacing/transition check", "pacing check", "transition check"],
    "source-binding check": ["source-binding check", "source binding check"],
    "audio sync check": ["audio sync check"],
    "known caveats": ["known caveats"],
    "asset quality check": ["asset quality check"],
    "composition check": ["composition check"],
    "renderer asset-binding check": ["renderer asset-binding check", "renderer asset binding check"],
}

THIN_FINAL_REVIEW_VALUES = {"ok", "yes", "done", "passed", "n/a", "none", "clear"}

SCAFFOLD_TEMPLATE = SCRIPT_DIR.parent / "assets" / "templates" / "concept-renderer-template.html"
SCAFFOLD_SIGNATURES = {
    "safe-shell": 'class="safe"',
    "topline": 'class="topline"',
    "beat-card": 'class="beat-card"',
    "source-surface": 'id="sourcesurface"',
    "transition-surface": 'id="transitionsurface"',
    "warning-surface": 'id="warningsurface"',
    "core-ring": 'class="core-ring"',
    "source-input-label": "source / input",
    "output-rule-label": "output / rule",
    "starter-kicker": "fast technical explainer",
    "pick-beat": "function pickbeat",
    "set-visible": "function setvisible",
    "starter-beats-global": "awsome_video_beats",
    "wireframe-mode": 'renderermode: "wireframe"',
    "empty-active-assets": "activeassetids: []",
    "empty-source-assets": "sourceproofassetids: []",
}
RENDERER_LIVE_COMPARISON_FIELDS = [
    "ok",
    "briefBeatCoverageOk",
    "expectedBriefBeats",
    "sampledBriefBeats",
    "missingBriefBeats",
    "uniqueBeats",
    "visualAssetCoverageOk",
    "assetBindingCoverageOk",
    "compositionCoverageOk",
    "expectedAssetIds",
    "observedAssetIds",
    "missingAssetIds",
    "unknownAssetIds",
    "expectedCompositionIds",
    "observedCompositionIds",
    "missingCompositionIds",
    "unknownCompositionIds",
    "missingCompositionObjectIds",
    "rendererSha256",
    "assetManifestSha256",
    "compositionPlanSha256",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate an awsome-videos production package.")
    parser.add_argument("--brief", required=True, type=Path)
    parser.add_argument("--video", required=True, type=Path)
    parser.add_argument("--design-note", type=Path)
    parser.add_argument("--production-notes", type=Path)
    parser.add_argument("--package-manifest", type=Path)
    parser.add_argument("--pattern-blueprint", type=Path)
    parser.add_argument("--asset-manifest", type=Path)
    parser.add_argument("--composition-plan", type=Path)
    parser.add_argument("--visual-review", type=Path)
    parser.add_argument("--visual-contract-report", type=Path)
    parser.add_argument("--renderer", type=Path)
    parser.add_argument("--contact-sheet", type=Path)
    parser.add_argument("--quality-report", type=Path)
    parser.add_argument("--motion-report", type=Path)
    parser.add_argument("--capture-manifest", type=Path)
    parser.add_argument("--audio-report", type=Path)
    parser.add_argument("--renderer-report", type=Path)
    parser.add_argument("--readiness-report", type=Path)
    parser.add_argument("--style-fidelity-report", type=Path)
    parser.add_argument("--min-beats", type=int, default=8)
    parser.add_argument("--require-voiceover", action="store_true")
    parser.add_argument("--min-voiceover-lines", type=int)
    parser.add_argument("--require-source-links", action="store_true")
    parser.add_argument("--expect-width", type=int)
    parser.add_argument("--expect-height", type=int)
    parser.add_argument("--expect-fps", type=float)
    parser.add_argument("--fps-tolerance", type=float, default=0.2)
    parser.add_argument("--expect-duration", type=float)
    parser.add_argument("--duration-tolerance", type=float, default=1.0)
    parser.add_argument("--min-duration", type=float)
    parser.add_argument("--max-duration", type=float)
    parser.add_argument("--min-size-bytes", type=int, default=100_000)
    parser.add_argument("--require-audio", action="store_true")
    parser.add_argument("--require-audio-report", action="store_true")
    parser.add_argument("--require-final-audio", action="store_true")
    parser.add_argument("--skip-audio-level-check", action="store_true")
    parser.add_argument("--min-mean-volume-db", type=float, default=-55.0)
    parser.add_argument("--min-max-volume-db", type=float, default=-45.0)
    parser.add_argument("--min-contact-sheet-width", type=int, default=320)
    parser.add_argument("--min-contact-sheet-height", type=int, default=180)
    parser.add_argument("--min-contact-sheet-stddev", type=float, default=4.0)
    parser.add_argument("--min-contact-sheet-colors", type=int, default=32)
    parser.add_argument("--require-design-note", action="store_true")
    parser.add_argument("--require-production-notes", action="store_true")
    parser.add_argument("--require-package-manifest", action="store_true")
    parser.add_argument("--require-pattern-blueprint", action="store_true")
    parser.add_argument("--require-visual-contract", action="store_true")
    parser.add_argument("--require-ready-assets", action="store_true")
    parser.add_argument("--require-specialist-routing", action="store_true")
    parser.add_argument("--require-source-routing", action="store_true")
    parser.add_argument("--require-reviewed-scenes", action="store_true")
    parser.add_argument("--require-renderer", action="store_true")
    parser.add_argument("--forbid-scaffold-renderer", action="store_true")
    parser.add_argument("--require-contact-sheet", action="store_true")
    parser.add_argument("--require-motion-report", action="store_true")
    parser.add_argument("--require-renderer-report", action="store_true")
    parser.add_argument("--require-renderer-beat-coverage", action="store_true")
    parser.add_argument("--require-renderer-visual-coverage", action="store_true")
    parser.add_argument("--require-readiness-report", action="store_true")
    parser.add_argument("--require-style-fidelity-report", action="store_true")
    parser.add_argument("--require-final-review-notes", action="store_true")
    parser.add_argument("--min-readiness-score", type=int, default=18)
    parser.add_argument("--min-style-fidelity-score", type=int, default=12)
    parser.add_argument("--allow-weak-readiness", action="store_true")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    return parser.parse_args()


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def require_file(path: Path | None, label: str, failures: list[str], warnings: list[str], required: bool) -> dict[str, Any] | None:
    if path is None:
        if required:
            failures.append(f"{label} is required but was not supplied")
        else:
            warnings.append(f"{label} was not supplied")
        return None
    if not path.exists():
        failures.append(f"{label} not found: {path}")
        return None
    if not path.is_file():
        failures.append(f"{label} is not a file: {path}")
        return None
    return {"path": str(path), "sizeBytes": path.stat().st_size}


def validate_design_note(path: Path | None, failures: list[str], warnings: list[str], required: bool) -> dict[str, Any] | None:
    info = require_file(path, "design note", failures, warnings, required)
    if info is None or path is None or not path.exists():
        return info
    text = read_text(path).lower()
    required_terms = {
        "concept claim": ["concept claim", "claim"],
        "visual metaphor": ["visual metaphor", "metaphor"],
        "visual vocabulary": ["visual vocabulary", "vocabulary"],
        "timing contract": ["timing contract", "timing"],
    }
    missing = [
        label
        for label, terms in required_terms.items()
        if not any(term in text for term in terms)
    ]
    if missing:
        failures.append("design note missing coverage: " + ", ".join(missing))
    info["missing"] = missing
    return info


def validate_text_contract(
    path: Path | None,
    label: str,
    required_terms: dict[str, list[str]],
    failures: list[str],
    warnings: list[str],
    required: bool,
) -> dict[str, Any] | None:
    info = require_file(path, label, failures, warnings, required)
    if info is None or path is None or not path.exists():
        return info
    text = read_text(path).lower()
    missing = [
        name
        for name, terms in required_terms.items()
        if not any(term in text for term in terms)
    ]
    if missing:
        failures.append(f"{label} missing coverage: " + ", ".join(missing))
    info["missing"] = missing
    return info


def extract_uv_commands(text: str) -> list[str]:
    blocks = re.findall(r"```(?:[a-zA-Z0-9_-]+)?\s*\n(.*?)```", text, flags=re.DOTALL)
    sources = blocks or [text]
    commands: list[str] = []
    for source in sources:
        for raw_line in source.splitlines():
            line = raw_line.strip()
            if line.startswith("uv run --script "):
                commands.append(line)
    return commands


def command_for_script(commands: list[str], script_name: str) -> str:
    return next((command for command in commands if script_name in command), "")


def validate_production_notes_command_contract(
    text: str,
    expected_duration: float | None = None,
    require_final_audio: bool = False,
    require_final_review_notes: bool = False,
    require_pattern_blueprint: bool = False,
    require_source_links: bool = False,
) -> dict[str, Any]:
    failures: list[str] = []
    normalized_text = text.replace("\\", "/")
    lowered = normalized_text.lower()
    commands = extract_uv_commands(normalized_text)
    joined_commands = "\n".join(commands)

    unresolved_placeholders = sorted(set(re.findall(r"\{\{[^}]+\}\}", text)))
    if unresolved_placeholders:
        failures.append("unresolved placeholders: " + ", ".join(unresolved_placeholders))

    forbidden_paths = (
        [".agents/skills/awsome-videos"]
        if re.search(r"(?<![./])\.agents/skills/awsome-videos", lowered)
        else []
    )
    if forbidden_paths:
        failures.append("non-portable skill paths: " + ", ".join(forbidden_paths))

    cwd_terms = ["command working directory: project root", "source/", "src/", "artifacts/"]
    missing_cwd_terms = [term for term in cwd_terms if term not in lowered]
    if missing_cwd_terms:
        failures.append("missing command working directory terms: " + ", ".join(missing_cwd_terms))

    required_scripts = list(PRODUCTION_NOTE_REQUIRED_SCRIPTS)
    if require_pattern_blueprint:
        required_scripts.append("select_video_patterns.py")
    missing_scripts = [script for script in required_scripts if script not in joined_commands]
    if not commands:
        failures.append("no uv run --script commands found")
    if missing_scripts:
        failures.append("missing validation commands: " + ", ".join(missing_scripts))

    missing_command_terms: dict[str, list[str]] = {}
    command_terms = dict(PRODUCTION_NOTE_REQUIRED_COMMAND_TERMS)
    if require_pattern_blueprint:
        command_terms["select_video_patterns.py"] = [
            "--output source/pattern-blueprint.json",
            "--json",
        ]
    for script, terms in command_terms.items():
        command = command_for_script(commands, script)
        missing = [term for term in terms if term not in command]
        if missing:
            missing_command_terms[script] = missing
    if missing_command_terms:
        formatted = "; ".join(f"{script}: {', '.join(terms)}" for script, terms in missing_command_terms.items())
        failures.append("missing command terms: " + formatted)

    missing_final_audio_command_terms: dict[str, list[str]] = {}
    if require_final_audio:
        for script, terms in FINAL_AUDIO_COMMAND_TERMS.items():
            command = command_for_script(commands, script)
            missing = [term for term in terms if term not in command]
            if missing:
                missing_final_audio_command_terms[script] = missing
    if missing_final_audio_command_terms:
        formatted = "; ".join(
            f"{script}: {', '.join(terms)}" for script, terms in missing_final_audio_command_terms.items()
        )
        failures.append("missing final-audio command terms: " + formatted)

    missing_final_review_command_terms: dict[str, list[str]] = {}
    if require_final_review_notes:
        command = command_for_script(commands, "check_production_package.py")
        missing = [term for term in ["--require-final-review-notes"] if term not in command]
        if missing:
            missing_final_review_command_terms["check_production_package.py"] = missing
            failures.append("missing final-review command terms: check_production_package.py: " + ", ".join(missing))

    missing_source_link_command_terms: dict[str, list[str]] = {}
    if require_source_links:
        source_link_command_checks = {
            "check_video_brief.py": ["--require-source-links"],
            "score_style_fidelity.py": ["--require-source-links"],
            "score_video_readiness.py": ["--require-source-links"],
            "check_production_package.py": ["--require-source-links"],
        }
        for script, terms in source_link_command_checks.items():
            command = command_for_script(commands, script)
            missing = [term for term in terms if term not in command]
            if missing:
                missing_source_link_command_terms[script] = missing
    if missing_source_link_command_terms:
        formatted = "; ".join(
            f"{script}: {', '.join(terms)}" for script, terms in missing_source_link_command_terms.items()
        )
        failures.append("missing source-link command terms: " + formatted)

    missing_duration_terms: list[str] = []
    if expected_duration is not None:
        duration = f"{expected_duration:g}"
        duration_checks = [
            ("render_concept_video.py", f"--duration {duration}"),
            ("check_video_artifact.py", f"--expect-duration {duration}"),
            ("check_video_artifact.py", "--duration-tolerance"),
            ("check_production_package.py", f"--expect-duration {duration}"),
            ("check_production_package.py", "--duration-tolerance"),
        ]
        for script, term in duration_checks:
            command = command_for_script(commands, script)
            if term not in command:
                missing_duration_terms.append(f"{script}: {term}")
    if missing_duration_terms:
        failures.append("missing duration terms: " + "; ".join(missing_duration_terms))

    return {
        "ok": not failures,
        "commands": commands,
        "commandCount": len(commands),
        "missingScripts": missing_scripts,
        "missingCommandTerms": missing_command_terms,
        "missingFinalAudioCommandTerms": missing_final_audio_command_terms,
        "missingFinalReviewCommandTerms": missing_final_review_command_terms,
        "missingSourceLinkCommandTerms": missing_source_link_command_terms,
        "missingDurationTerms": missing_duration_terms,
        "unresolvedPlaceholders": unresolved_placeholders,
        "forbiddenPaths": forbidden_paths,
        "missingCwdTerms": missing_cwd_terms,
        "requireFinalAudio": require_final_audio,
        "requireFinalReviewNotes": require_final_review_notes,
        "requirePatternBlueprint": require_pattern_blueprint,
        "requireSourceLinks": require_source_links,
        "failures": failures,
    }


def extract_markdown_section(text: str, heading: str) -> str:
    lines = text.splitlines()
    start: int | None = None
    level = 0
    for index, line in enumerate(lines):
        match = re.match(r"^(#{2,6})\s+(.+?)\s*$", line)
        if match and match.group(2).strip().lower() == heading.lower():
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


def validate_final_review_notes(text: str) -> dict[str, Any]:
    section = extract_markdown_section(text, "Visual review") or text
    lowered = section.lower()
    stale_lines = [
        line.strip()
        for line in section.splitlines()
        if line.strip() and FINAL_REVIEW_STALE_RE.search(line)
    ]
    missing_terms = [
        label
        for label, terms in FINAL_REVIEW_REQUIRED_TERMS.items()
        if not any(term in lowered for term in terms)
    ]
    thin_checks: list[str] = []
    for label, terms in FINAL_REVIEW_REQUIRED_TERMS.items():
        line_match = None
        for term in terms:
            pattern = rf"^\s*[-*]?\s*{re.escape(term)}\s*:\s*(.+?)\s*$"
            line_match = re.search(pattern, section, flags=re.IGNORECASE | re.MULTILINE)
            if line_match:
                break
        if not line_match:
            continue
        value = line_match.group(1).strip()
        normalized_value = re.sub(r"[\s.]+", " ", value.lower()).strip()
        if len(value) < 16 or normalized_value in THIN_FINAL_REVIEW_VALUES:
            thin_checks.append(label)
    failures = []
    if stale_lines:
        failures.append("final review notes contain unresolved status: " + "; ".join(stale_lines[:5]))
    if missing_terms:
        failures.append("final review notes missing structured checks: " + ", ".join(missing_terms))
    if thin_checks:
        failures.append("final review notes have thin structured checks: " + ", ".join(thin_checks))
    return {
        "ok": not failures,
        "staleLines": stale_lines,
        "missingStructuredChecks": missing_terms,
        "thinStructuredChecks": thin_checks,
        "failures": failures,
    }


def validate_production_notes(
    path: Path | None,
    failures: list[str],
    warnings: list[str],
    required: bool,
    expected_duration: float | None = None,
    require_final_audio: bool = False,
    require_final_review_notes: bool = False,
    require_pattern_blueprint: bool = False,
    require_source_links: bool = False,
) -> dict[str, Any] | None:
    required_sections = {
        "concept claim": ["concept claim"],
        "visual metaphor": ["chosen visual metaphor", "visual metaphor"],
        "production files": ["production files", "final mp4", "contact sheet", "motion report"],
        "render state contract": ["render state contract", "activebeat", "visiblemechanismcount"],
        "validation commands": ["validation commands", "check_video_brief.py", "check_production_package.py"],
        "command working directory": ["command working directory", "project root", "source/", "artifacts/"],
        "visual review": ["visual review", "contact sheet inspected"],
    }
    if require_pattern_blueprint:
        required_sections["pattern blueprint"] = ["pattern blueprint", "source/pattern-blueprint.json"]
    info = validate_text_contract(
        path,
        "production notes",
        required_sections,
        failures,
        warnings,
        required,
    )
    if info is None or path is None or not path.exists():
        return info
    text = read_text(path)
    command_contract = validate_production_notes_command_contract(
        text,
        expected_duration,
        require_final_audio,
        require_final_review_notes,
        require_pattern_blueprint,
        require_source_links,
    )
    if not command_contract["ok"]:
        failures.extend(f"production notes command contract: {failure}" for failure in command_contract["failures"])
    info["commandContract"] = command_contract
    if require_final_review_notes:
        final_review = validate_final_review_notes(text)
        if not final_review["ok"]:
            failures.extend(f"production notes final review: {failure}" for failure in final_review["failures"])
        info["finalReview"] = final_review
    return info


def validate_package_manifest(
    path: Path | None,
    failures: list[str],
    warnings: list[str],
    required: bool,
    require_final_audio: bool = False,
    require_final_review_notes: bool = False,
    require_pattern_blueprint: bool = False,
    require_style_fidelity_report: bool = False,
    require_source_links: bool = False,
    require_visual_contract: bool = False,
    expected_artifacts: dict[str, Path | None] | None = None,
) -> dict[str, Any] | None:
    info = require_file(path, "package manifest", failures, warnings, required)
    if info is None or path is None or not path.exists():
        return info
    try:
        data = json.loads(read_text(path))
    except json.JSONDecodeError as exc:
        failures.append(f"package manifest is not valid JSON: {exc}")
        return info
    if not isinstance(data, dict):
        failures.append("package manifest root is not an object")
        return info

    paths = data.get("paths")
    commands = data.get("commands")
    if not isinstance(paths, dict):
        failures.append("package manifest paths is missing or not an object")
        paths = {}
    if not isinstance(commands, dict):
        failures.append("package manifest commands is missing or not an object")
        commands = {}

    required_paths = [
        "brief",
        "designNote",
        "productionNotes",
        "renderer",
        "storyboard",
        "video",
        "contactSheet",
        "rendererValidation",
        "qualityReport",
        "motionReport",
        "captureManifest",
        "audioReport",
        "readinessScore",
        "styleFidelity",
        "packageValidation",
    ]
    if require_final_audio:
        required_paths.append("finalAudio")
    if require_pattern_blueprint:
        required_paths.extend(["patternBlueprintJson", "patternBlueprintMarkdown"])
    if require_visual_contract:
        required_paths.extend(
            [
                "sourcePackage",
                "shotContract",
                "assetManifest",
                "compositionPlan",
                "transitionPlan",
                "visualReview",
                "visualContractValidation",
            ]
        )
    required_commands = [
        "briefValidation",
        "rendererValidation",
        "renderVideo",
        "videoValidation",
        "scoreReadiness",
        "styleFidelity",
        "packageValidation",
    ]
    if require_pattern_blueprint:
        required_commands.append("selectPatterns")
    if require_visual_contract:
        required_commands.append("visualContractValidation")
    missing_paths = [name for name in required_paths if not paths.get(name)]
    missing_commands = [name for name in required_commands if not commands.get(name)]
    if missing_paths:
        failures.append("package manifest missing paths: " + ", ".join(missing_paths))
    if missing_commands:
        failures.append("package manifest missing commands: " + ", ".join(missing_commands))

    package_root = path.parent.parent.resolve()
    if expected_artifacts:
        for manifest_name, artifact_path in expected_artifacts.items():
            if artifact_path is None:
                continue
            resolved_artifact = artifact_path.resolve()
            try:
                expected_relative = resolved_artifact.relative_to(package_root).as_posix()
            except ValueError:
                failures.append(f"CLI artifact {manifest_name} is outside the package root: {artifact_path}")
                continue
            declared_path = Path(str(paths.get(manifest_name, ""))).as_posix()
            if declared_path != expected_relative:
                failures.append(
                    f"package manifest paths.{manifest_name} does not match the CLI artifact"
                )

    contracts = data.get("contracts")
    toolchain = data.get("toolchain")
    if require_visual_contract:
        if not isinstance(contracts, dict):
            failures.append("package manifest contracts is missing or not an object")
            contracts = {}
        expected_contracts = {
            "sourcePackage": paths.get("sourcePackage"),
            "shotContract": paths.get("shotContract"),
            "assetManifest": paths.get("assetManifest"),
            "compositionPlan": paths.get("compositionPlan"),
            "transitionPlan": paths.get("transitionPlan"),
            "visualReview": paths.get("visualReview"),
            "validationReport": paths.get("visualContractValidation"),
        }
        mismatched_contracts = [
            name for name, expected in expected_contracts.items() if not expected or contracts.get(name) != expected
        ]
        if mismatched_contracts:
            failures.append("package manifest contracts disagree with paths: " + ", ".join(mismatched_contracts))
        if not isinstance(toolchain, list) or not toolchain:
            failures.append("package manifest toolchain is missing or empty")
        for contract_name, raw_contract_path in expected_contracts.items():
            if not raw_contract_path:
                continue
            candidate = Path(str(raw_contract_path))
            if candidate.is_absolute() or candidate.drive:
                failures.append(f"package manifest {contract_name} path must be project-root-relative")
                continue
            resolved = (package_root / candidate).resolve()
            try:
                resolved.relative_to(package_root)
            except ValueError:
                failures.append(f"package manifest {contract_name} path escapes the project root")
                continue
            if not resolved.is_file():
                failures.append(f"package manifest {contract_name} file missing: {raw_contract_path}")
        asset_manifest_raw = paths.get("assetManifest")
        if asset_manifest_raw:
            raw_asset_path = Path(str(asset_manifest_raw))
            asset_manifest_candidate = (package_root / raw_asset_path).resolve()
            asset_manifest_safe = not raw_asset_path.is_absolute() and not raw_asset_path.drive
            if asset_manifest_safe:
                try:
                    asset_manifest_candidate.relative_to(package_root)
                except ValueError:
                    asset_manifest_safe = False
            if asset_manifest_safe and asset_manifest_candidate.is_file():
                try:
                    manifest_asset_data = json.loads(read_text(asset_manifest_candidate))
                except json.JSONDecodeError as exc:
                    failures.append(f"package asset manifest is not valid JSON: {exc}")
                else:
                    manifest_toolchain = (
                        manifest_asset_data.get("skillRouting")
                        if isinstance(manifest_asset_data, dict)
                        else None
                    )
                    if toolchain != manifest_toolchain:
                        failures.append("package manifest toolchain is stale or differs from asset manifest skillRouting")

    final_audio_path = str(paths.get("finalAudio", "")) if isinstance(paths, dict) else ""
    final_audio_exists: bool | None = None
    if require_final_audio and final_audio_path:
        final_audio_candidate = Path(final_audio_path)
        if final_audio_candidate.is_absolute():
            final_audio_exists = final_audio_candidate.is_file()
            failures.append("package manifest finalAudio path must be project-root-relative")
        else:
            package_root = path.parent.parent
            final_audio_exists = (package_root / final_audio_candidate).is_file()
            if not final_audio_exists:
                failures.append("package manifest finalAudio file missing: " + final_audio_path)

    style_fidelity_path = str(paths.get("styleFidelity", "")) if isinstance(paths, dict) else ""
    style_fidelity_exists: bool | None = None
    if require_style_fidelity_report and style_fidelity_path:
        style_fidelity_candidate = Path(style_fidelity_path)
        if style_fidelity_candidate.is_absolute():
            style_fidelity_exists = style_fidelity_candidate.is_file()
            failures.append("package manifest styleFidelity path must be project-root-relative")
        else:
            package_root = path.parent.parent
            style_fidelity_exists = (package_root / style_fidelity_candidate).is_file()
            if not style_fidelity_exists:
                failures.append("package manifest styleFidelity file missing: " + style_fidelity_path)

    package_command = str(commands.get("packageValidation", ""))
    renderer_command = str(commands.get("rendererValidation", ""))
    render_command = str(commands.get("renderVideo", ""))
    readiness_command = str(commands.get("scoreReadiness", ""))
    style_command = str(commands.get("styleFidelity", ""))
    renderer_command_required_terms = [
        "check_renderer_contract.py",
        "--brief",
        "--require-all-brief-beats",
        "--output",
    ]
    missing_renderer_command_terms = [
        term for term in renderer_command_required_terms if term not in renderer_command
    ]
    if missing_renderer_command_terms:
        failures.append(
            "package manifest rendererValidation command missing: "
            + ", ".join(missing_renderer_command_terms)
        )
    render_command_required_terms = [
        "render_concept_video.py",
        "--brief",
        "--require-all-brief-beats",
        "--capture-fps",
        "--render-state-report",
        "--contact-sheet",
        "--motion-report",
    ]
    missing_render_command_terms = [
        term for term in render_command_required_terms if term not in render_command
    ]
    if missing_render_command_terms:
        failures.append(
            "package manifest renderVideo command missing: "
            + ", ".join(missing_render_command_terms)
        )
    command_required_terms = [
        "--production-notes",
        "--package-manifest",
        "--motion-report",
        "--audio-report",
        "--require-audio-report",
        "--require-voiceover",
        "--require-production-notes",
        "--require-package-manifest",
        "--require-motion-report",
        "--min-readiness-score",
        "--expect-duration",
        "--duration-tolerance",
        "--style-fidelity-report",
        "--min-style-fidelity-score",
        "--require-renderer-beat-coverage",
    ]
    if require_style_fidelity_report:
        command_required_terms.append("--require-style-fidelity-report")
    missing_command_terms = [term for term in command_required_terms if term not in package_command]
    if missing_command_terms:
        failures.append("package manifest packageValidation command missing: " + ", ".join(missing_command_terms))
    readiness_command_required_terms = [
        "--require-voiceover",
        "--renderer-report",
        "--quality-report",
        "--motion-report",
        "--capture-manifest",
        "--audio-report",
        "--contact-sheet",
        "--output",
    ]
    missing_readiness_command_terms = [
        term for term in readiness_command_required_terms if term not in readiness_command
    ]
    if missing_readiness_command_terms:
        failures.append(
            "package manifest scoreReadiness command missing: "
            + ", ".join(missing_readiness_command_terms)
        )
    style_command_required_terms = [
        "score_style_fidelity.py",
        "--brief",
        "--pattern-blueprint",
        "--require-voiceover",
        "--require-pattern-blueprint",
        "--output",
    ]
    missing_style_command_terms = [term for term in style_command_required_terms if term not in style_command]
    if missing_style_command_terms:
        failures.append(
            "package manifest styleFidelity command missing: "
            + ", ".join(missing_style_command_terms)
        )

    missing_source_link_command_terms: dict[str, list[str]] = {}
    if require_source_links:
        source_link_command_checks = {
            "briefValidation": ["--require-source-links"],
            "scoreReadiness": ["--require-source-links"],
            "styleFidelity": ["--require-source-links"],
            "packageValidation": ["--require-source-links"],
        }
        for command_name, terms in source_link_command_checks.items():
            command = str(commands.get(command_name, ""))
            missing = [term for term in terms if term not in command]
            if missing:
                missing_source_link_command_terms[command_name] = missing
    if missing_source_link_command_terms:
        formatted = "; ".join(
            f"{command}: {', '.join(terms)}" for command, terms in missing_source_link_command_terms.items()
        )
        failures.append("package manifest source-link command terms missing: " + formatted)

    missing_final_audio_command_terms: dict[str, list[str]] = {}
    if require_final_audio:
        final_audio_command_checks = {
            "renderVideo": ["--audio-file"],
            "videoValidation": ["--require-final-audio"],
            "scoreReadiness": ["--require-final-audio"],
            "packageValidation": ["--require-final-audio"],
        }
        for command_name, terms in final_audio_command_checks.items():
            command = str(commands.get(command_name, ""))
            missing = [term for term in terms if term not in command]
            if missing:
                missing_final_audio_command_terms[command_name] = missing
    if missing_final_audio_command_terms:
        formatted = "; ".join(
            f"{command}: {', '.join(terms)}" for command, terms in missing_final_audio_command_terms.items()
        )
        failures.append("package manifest final-audio command terms missing: " + formatted)

    missing_final_review_command_terms: dict[str, list[str]] = {}
    if require_final_review_notes:
        command = str(commands.get("packageValidation", ""))
        missing = [term for term in ["--require-final-review-notes"] if term not in command]
        if missing:
            missing_final_review_command_terms["packageValidation"] = missing
            failures.append("package manifest final-review command terms missing: packageValidation: " + ", ".join(missing))

    missing_pattern_command_terms: dict[str, list[str]] = {}
    if require_pattern_blueprint:
        pattern_checks = {
            "selectPatterns": [
                "select_video_patterns.py",
                "--output",
                "source/pattern-blueprint.json",
                "--json",
            ],
            "packageValidation": [
                "--pattern-blueprint",
                "source/pattern-blueprint.json",
                "--require-pattern-blueprint",
            ],
        }
        for command_name, terms in pattern_checks.items():
            command = str(commands.get(command_name, ""))
            missing = [term for term in terms if term not in command]
            if missing:
                missing_pattern_command_terms[command_name] = missing
        if missing_pattern_command_terms:
            formatted = "; ".join(
                f"{command}: {', '.join(terms)}" for command, terms in missing_pattern_command_terms.items()
            )
            failures.append("package manifest pattern-blueprint command terms missing: " + formatted)

    info["paths"] = sorted(paths) if isinstance(paths, dict) else []
    info["commands"] = sorted(commands) if isinstance(commands, dict) else []
    info["missingPaths"] = missing_paths
    info["missingCommands"] = missing_commands
    info["missingPackageCommandTerms"] = missing_command_terms
    info["missingRendererCommandTerms"] = missing_renderer_command_terms
    info["missingRenderCommandTerms"] = missing_render_command_terms
    info["missingReadinessCommandTerms"] = missing_readiness_command_terms
    info["missingStyleCommandTerms"] = missing_style_command_terms
    info["missingFinalAudioCommandTerms"] = missing_final_audio_command_terms
    info["missingFinalReviewCommandTerms"] = missing_final_review_command_terms
    info["missingPatternBlueprintCommandTerms"] = missing_pattern_command_terms
    info["missingSourceLinkCommandTerms"] = missing_source_link_command_terms
    info["contracts"] = contracts if isinstance(contracts, dict) else None
    info["toolchainStages"] = len(toolchain) if isinstance(toolchain, list) else 0
    info["requireFinalAudio"] = require_final_audio
    info["requireFinalReviewNotes"] = require_final_review_notes
    info["requirePatternBlueprint"] = require_pattern_blueprint
    info["requireStyleFidelityReport"] = require_style_fidelity_report
    info["requireSourceLinks"] = require_source_links
    info["finalAudioPath"] = final_audio_path
    info["finalAudioExists"] = final_audio_exists
    info["styleFidelityPath"] = style_fidelity_path
    info["styleFidelityExists"] = style_fidelity_exists
    return info


def scaffold_token_shingles(text: str, width: int = 5) -> set[tuple[str, ...]]:
    cleaned = re.sub(r"<!--.*?-->", " ", text, flags=re.DOTALL)
    cleaned = re.sub(r"awsome_scaffold_wireframe", " ", cleaned, flags=re.IGNORECASE)
    tokens = re.findall(r"[a-z_][a-z0-9_-]{1,}|#[0-9a-f]{3,8}", cleaned.lower())
    if len(tokens) < width:
        return set()
    return {tuple(tokens[index : index + width]) for index in range(len(tokens) - width + 1)}


def scaffold_similarity(text: str) -> dict[str, Any]:
    lower = re.sub(r"\s+", " ", text.lower())
    explicit_marker = "awsome_scaffold_wireframe" in lower
    matched_signatures = sorted(
        label for label, signature in SCAFFOLD_SIGNATURES.items() if signature in lower
    )
    template_containment = 0.0
    if SCAFFOLD_TEMPLATE.is_file():
        template_shingles = scaffold_token_shingles(read_text(SCAFFOLD_TEMPLATE))
        candidate_shingles = scaffold_token_shingles(text)
        if template_shingles:
            template_containment = len(template_shingles & candidate_shingles) / len(template_shingles)
    signature_count = len(matched_signatures)
    markerless_match = (
        (template_containment >= 0.58 and signature_count >= 5)
        or (template_containment >= 0.42 and signature_count >= 9)
        or signature_count >= 13
    )
    return {
        "isScaffold": explicit_marker or markerless_match,
        "explicitMarker": explicit_marker,
        "markerlessMatch": markerless_match,
        "templateContainment": round(template_containment, 6),
        "signatureCount": signature_count,
        "matchedSignatures": matched_signatures,
    }


def validate_renderer(
    path: Path | None,
    failures: list[str],
    warnings: list[str],
    required: bool,
    forbid_scaffold: bool = False,
) -> dict[str, Any] | None:
    info = require_file(path, "renderer/storyboard", failures, warnings, required)
    if info is None or path is None or not path.exists():
        return info
    suffix = path.suffix.lower()
    text_suffixes = {".html", ".js", ".mjs", ".ts", ".tsx", ".jsx", ".md", ".json", ".py"}
    if suffix in text_suffixes:
        text = read_text(path)
        lower = text.lower()
        signals = [
            "renderconceptframe",
            "timed beat",
            "storyboard",
            "scene",
            "shot",
        ]
        if not any(signal in lower for signal in signals):
            warnings.append("renderer/storyboard lacks common deterministic render or storyboard signals")
        scaffold = scaffold_similarity(text)
        scaffold_marker = scaffold.get("isScaffold") is True
        if info is not None:
            info["scaffoldWireframe"] = scaffold_marker
            info["scaffoldSimilarity"] = scaffold
        if forbid_scaffold and scaffold_marker:
            if scaffold.get("explicitMarker") is True:
                failures.append("renderer is still the AWSOME_SCAFFOLD_WIREFRAME starter")
            else:
                failures.append(
                    "renderer remains structurally similar to the scaffold wireframe after its marker was removed "
                    f"(template containment {scaffold.get('templateContainment')}, "
                    f"{scaffold.get('signatureCount')} starter signatures)"
                )
    return info


def validate_json_report(
    path: Path | None,
    label: str,
    failures: list[str],
    warnings: list[str],
    required: bool,
    *,
    require_renderer_beat_coverage: bool = False,
    require_renderer_visual_coverage: bool = False,
    expected_input_digests: dict[str, str | None] | None = None,
) -> dict[str, Any] | None:
    info = require_file(path, label, failures, warnings, required)
    if info is None or path is None or not path.exists():
        return info
    try:
        data = json.loads(read_text(path))
    except json.JSONDecodeError as exc:
        failures.append(f"{label} is not valid JSON: {exc}")
        return info
    ok_value = data.get("ok")
    passed_value = data.get("passed")
    if ok_value is False or passed_value is False:
        failures.append(f"{label} reports failure")
    if ok_value is None and passed_value is None:
        warnings.append(f"{label} does not include ok/passed status")
    info["ok"] = ok_value
    info["passed"] = passed_value
    if "score" in data:
        info["score"] = data.get("score")
    if "readiness" in data:
        info["readiness"] = data.get("readiness")
    if "states" in data:
        info["states"] = len(data.get("states") or [])
    if "uniqueBeats" in data:
        info["uniqueBeats"] = len(data.get("uniqueBeats") or [])
    if require_renderer_beat_coverage:
        coverage_ok = data.get("briefBeatCoverageOk")
        missing_beats = data.get("missingBriefBeats")
        expected_beats = data.get("expectedBriefBeats")
        info["briefBeatCoverageOk"] = coverage_ok
        info["missingBriefBeats"] = missing_beats
        info["expectedBriefBeats"] = expected_beats
        if coverage_ok is not True:
            failures.append(f"{label} does not prove all brief beats were sampled")
        if missing_beats:
            failures.append(f"{label} missing brief beat coverage: " + ", ".join(str(item) for item in missing_beats))
    if require_renderer_visual_coverage:
        if ok_value is not True and passed_value is not True:
            failures.append(f"{label} must carry ok=true or passed=true for final visual coverage")
        asset_coverage = data.get("visualAssetCoverageOk")
        binding_coverage = data.get("assetBindingCoverageOk")
        composition_coverage = data.get("compositionCoverageOk")
        missing_assets = data.get("missingAssetIds")
        missing_compositions = data.get("missingCompositionIds")
        info["visualAssetCoverageOk"] = asset_coverage
        info["assetBindingCoverageOk"] = binding_coverage
        info["compositionCoverageOk"] = composition_coverage
        info["missingAssetIds"] = missing_assets
        info["missingCompositionIds"] = missing_compositions
        if asset_coverage is not True:
            failures.append(f"{label} does not prove visible asset ID coverage")
        if binding_coverage is not True:
            failures.append(f"{label} does not prove manifest-bound asset loading")
        if composition_coverage is not True:
            failures.append(f"{label} does not prove visible composition ID coverage")
        if missing_assets:
            failures.append(f"{label} missing visible assets: " + ", ".join(str(item) for item in missing_assets))
        if missing_compositions:
            failures.append(
                f"{label} missing visible compositions: "
                + ", ".join(str(item) for item in missing_compositions)
            )
        expected_assets = data.get("expectedAssetIds")
        observed_assets = data.get("observedAssetIds")
        expected_compositions = data.get("expectedCompositionIds")
        observed_compositions = data.get("observedCompositionIds")
        missing_objects = data.get("missingCompositionObjectIds")
        if not isinstance(expected_assets, list) or not expected_assets:
            failures.append(f"{label} expectedAssetIds is missing or empty")
        elif not isinstance(observed_assets, list) or set(observed_assets) != set(expected_assets):
            failures.append(f"{label} observedAssetIds does not exactly cover expectedAssetIds")
        if not isinstance(expected_compositions, list) or not expected_compositions:
            failures.append(f"{label} expectedCompositionIds is missing or empty")
        elif not isinstance(observed_compositions, list) or set(observed_compositions) != set(expected_compositions):
            failures.append(
                f"{label} observedCompositionIds does not exactly cover expectedCompositionIds"
            )
        if not isinstance(missing_objects, list) or missing_objects:
            failures.append(f"{label} does not prove complete composition object coverage")
        if expected_input_digests:
            for digest_name, expected_digest in expected_input_digests.items():
                info[digest_name] = data.get(digest_name)
                if expected_digest is not None and data.get(digest_name) != expected_digest:
                    failures.append(f"{label} has stale or missing {digest_name}")
    return info


def validate_visual_contract_report(
    path: Path | None,
    current_result: dict[str, Any],
    failures: list[str],
    warnings: list[str],
    required: bool,
) -> dict[str, Any] | None:
    info = require_file(path, "visual contract report", failures, warnings, required)
    if info is None or path is None or not path.exists():
        return info
    try:
        data = json.loads(read_text(path))
    except json.JSONDecodeError as exc:
        failures.append(f"visual contract report is not valid JSON: {exc}")
        return info
    if not isinstance(data, dict):
        failures.append("visual contract report root is not an object")
        return info
    if data.get("schemaVersion") != 1:
        failures.append("visual contract report schemaVersion must be 1")
    if data.get("ok") is not True:
        failures.append("visual contract report ok is not true")
    expected_digests = current_result.get("inputDigests", {})
    report_digests = data.get("inputDigests")
    if not isinstance(report_digests, dict) or report_digests != expected_digests:
        failures.append("visual contract report inputDigests are stale or do not match current inputs")
    for section, count_field in [("assetManifest", "assetCount"), ("compositionPlan", "sceneCount")]:
        value = data.get(section)
        if not isinstance(value, dict) or not isinstance(value.get(count_field), int) or value.get(count_field, 0) < 1:
            failures.append(f"visual contract report {section}.{count_field} is missing or invalid")
    info["ok"] = data.get("ok")
    info["schemaVersion"] = data.get("schemaVersion")
    info["inputDigests"] = report_digests
    return info


def validate_pattern_blueprint(path: Path | None, failures: list[str], warnings: list[str], required: bool) -> dict[str, Any] | None:
    info = require_file(path, "pattern blueprint", failures, warnings, required)
    if info is None or path is None or not path.exists():
        return info
    try:
        data = json.loads(read_text(path))
    except json.JSONDecodeError as exc:
        failures.append(f"pattern blueprint is not valid JSON: {exc}")
        return info
    if not isinstance(data, dict):
        failures.append("pattern blueprint root is not an object")
        return info
    required_arrays = [
        "visualSources",
        "animationAtoms",
        "transitionTypes",
        "audioRoles",
        "scriptMoves",
        "beatGuidance",
    ]
    missing_fields = [field for field in ["ok", "selectedFormat", "videoType", *required_arrays] if field not in data]
    thin_arrays = [
        field
        for field in required_arrays
        if not isinstance(data.get(field), list) or len(data.get(field, [])) < (8 if field == "beatGuidance" else 3)
    ]
    if data.get("ok") is not True:
        failures.append("pattern blueprint ok is not true")
    if not isinstance(data.get("selectedFormat"), str) or not data.get("selectedFormat"):
        failures.append("pattern blueprint selectedFormat is missing")
    if missing_fields:
        failures.append("pattern blueprint missing fields: " + ", ".join(missing_fields))
    if thin_arrays:
        failures.append("pattern blueprint thin arrays: " + ", ".join(thin_arrays))
    info["ok"] = data.get("ok")
    info["selectedFormat"] = data.get("selectedFormat")
    info["beatGuidanceRows"] = len(data.get("beatGuidance", [])) if isinstance(data.get("beatGuidance"), list) else 0
    info["missingFields"] = missing_fields
    info["thinArrays"] = thin_arrays
    return info


def validate_readiness_report(
    path: Path | None,
    failures: list[str],
    warnings: list[str],
    required: bool,
    min_score: int,
    allow_weak: bool,
    expected_input_digests: dict[str, str | None] | None = None,
) -> dict[str, Any] | None:
    info = validate_json_report(path, "readiness report", failures, warnings, required)
    if info is None or path is None or not path.exists():
        return info
    try:
        data = json.loads(read_text(path))
    except json.JSONDecodeError:
        return info

    score = data.get("score")
    readiness = data.get("readiness")
    weak_categories = data.get("weakCategories", [])
    if not isinstance(weak_categories, list):
        weak_categories = []

    if not isinstance(score, (int, float)):
        failures.append("readiness report score is missing or not numeric")
    elif score < min_score:
        failures.append(f"readiness report score below threshold: {score:g} < {min_score:g}")
    if readiness != "ready":
        failures.append(f"readiness report label is not ready: {readiness}")
    if weak_categories and not allow_weak:
        failures.append("readiness report has weak categories: " + ", ".join(str(item) for item in weak_categories))

    if data.get("maxScore") != len(score_video_readiness.CATEGORIES) * 3:
        failures.append("readiness report maxScore is missing or invalid")
    categories = data.get("categories")
    if not isinstance(categories, dict) or set(categories) != set(score_video_readiness.CATEGORIES):
        failures.append("readiness report categories are missing or incomplete")
    else:
        category_scores = [
            item.get("score") if isinstance(item, dict) else None for item in categories.values()
        ]
        if not all(isinstance(value, int) and 0 <= value <= 3 for value in category_scores):
            failures.append("readiness report category scores are invalid")
        elif sum(category_scores) != score:
            failures.append("readiness report score does not equal its category scores")
        if not all(
            isinstance(item, dict) and isinstance(item.get("evidence"), list) and item.get("evidence")
            for item in categories.values()
        ):
            failures.append("readiness report categories lack concrete evidence")
    visual_ok, visual_findings = score_video_readiness.visual_contract_evidence(
        data.get("visualContractReport")
    )
    if not visual_ok:
        failures.append("readiness report visual evidence is incomplete: " + "; ".join(visual_findings))
    renderer_ok, renderer_findings = score_video_readiness.renderer_visual_evidence(
        data.get("rendererReport"),
        data.get("visualContractReport"),
    )
    if not renderer_ok:
        failures.append("readiness report renderer evidence is incomplete: " + "; ".join(renderer_findings))
    if expected_input_digests is not None and data.get("inputDigests") != expected_input_digests:
        failures.append("readiness report inputDigests are stale or do not match current package artifacts")

    info["minReadinessScoreRequired"] = min_score
    info["weakCategories"] = weak_categories
    info["allowWeakReadiness"] = allow_weak
    return info


def validate_style_fidelity_report(
    path: Path | None,
    failures: list[str],
    warnings: list[str],
    required: bool,
    min_score: int,
    expected_input_digests: dict[str, str | None] | None = None,
) -> dict[str, Any] | None:
    info = validate_json_report(path, "style fidelity report", failures, warnings, required)
    if info is None or path is None or not path.exists():
        return info
    try:
        data = json.loads(read_text(path))
    except json.JSONDecodeError:
        return info

    score = data.get("score")
    penalties = data.get("penalties", [])
    weak_categories = data.get("weakCategories", [])
    if not isinstance(penalties, list):
        penalties = []
    if not isinstance(weak_categories, list):
        weak_categories = []

    if not isinstance(score, (int, float)):
        failures.append("style fidelity report score is missing or not numeric")
    elif score < min_score:
        failures.append(f"style fidelity report score below threshold: {score:g} < {min_score:g}")
    if penalties:
        failures.append("style fidelity report has penalties: " + ", ".join(str(item) for item in penalties))
    if expected_input_digests is not None and data.get("inputDigests") != expected_input_digests:
        failures.append("style fidelity report inputDigests are stale or do not match current sources")

    info["minStyleFidelityScoreRequired"] = min_score
    info["penalties"] = penalties
    info["weakCategories"] = weak_categories
    return info


def build_artifact_args(args: argparse.Namespace) -> argparse.Namespace:
    return argparse.Namespace(
        video=args.video,
        expect_width=args.expect_width,
        expect_height=args.expect_height,
        expect_fps=args.expect_fps,
        fps_tolerance=args.fps_tolerance,
        expect_duration=args.expect_duration,
        duration_tolerance=args.duration_tolerance,
        min_duration=args.min_duration,
        max_duration=args.max_duration,
        min_size_bytes=args.min_size_bytes,
        require_audio=args.require_audio,
        audio_report=args.audio_report,
        require_audio_report=args.require_audio_report,
        require_final_audio=args.require_final_audio,
        skip_audio_level_check=args.skip_audio_level_check,
        min_mean_volume_db=args.min_mean_volume_db,
        min_max_volume_db=args.min_max_volume_db,
        min_contact_sheet_width=args.min_contact_sheet_width,
        min_contact_sheet_height=args.min_contact_sheet_height,
        min_contact_sheet_stddev=args.min_contact_sheet_stddev,
        min_contact_sheet_colors=args.min_contact_sheet_colors,
        contact_sheet=args.contact_sheet,
        quality_report=args.quality_report,
        motion_report=args.motion_report,
        capture_manifest=args.capture_manifest,
        json=True,
    )


def build_visual_contract_args(args: argparse.Namespace) -> argparse.Namespace | None:
    if args.asset_manifest is None or args.composition_plan is None:
        return None
    if args.package_manifest is not None:
        project_root = args.package_manifest.parent.parent
    else:
        project_root = args.asset_manifest.parent.parent
    return argparse.Namespace(
        asset_manifest=args.asset_manifest,
        composition_plan=args.composition_plan,
        visual_review=args.visual_review,
        video=args.video,
        brief=args.brief,
        project_root=project_root,
        min_assets=args.min_beats,
        min_scenes=args.min_beats,
        require_ready_assets=args.require_ready_assets,
        require_specialist_routing=args.require_specialist_routing,
        require_source_routing=args.require_source_routing,
        require_reviewed_scenes=args.require_reviewed_scenes,
        output=None,
        json=True,
    )


def load_json_object(path: Path | None) -> dict[str, Any] | None:
    if path is None or not path.is_file():
        return None
    try:
        data = json.loads(read_text(path))
    except json.JSONDecodeError:
        return None
    return data if isinstance(data, dict) else None


def compare_renderer_frame_to_video(
    video: Path,
    timestamp: float,
    screenshot: Path,
    *,
    video_duration: float,
    video_fps: float,
    max_mean_difference: float = 0.04,
) -> dict[str, Any]:
    ffmpeg = check_video_artifact.resolve_tool("ffmpeg")
    if not ffmpeg:
        return {"ok": False, "failures": ["ffmpeg is required for renderer-to-video pixel binding"]}
    frame_interval = 1.0 / max(1.0, video_fps)
    seek_timestamp = min(max(0.0, timestamp), max(0.0, video_duration - frame_interval))
    try:
        completed = subprocess.run(
            [
                ffmpeg,
                "-v",
                "error",
                "-ss",
                f"{seek_timestamp:.3f}",
                "-i",
                str(video),
                "-frames:v",
                "1",
                "-f",
                "image2pipe",
                "-vcodec",
                "png",
                "pipe:1",
            ],
            capture_output=True,
            check=False,
            timeout=15,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {"ok": False, "failures": [f"ffmpeg frame extraction failed: {exc}"]}
    if completed.returncode != 0 or not completed.stdout:
        detail = completed.stderr.decode("utf-8", errors="ignore").strip()
        return {
            "ok": False,
            "failures": [f"ffmpeg could not extract candidate frame at {seek_timestamp:.3f}s: {detail}"],
        }
    try:
        with Image.open(BytesIO(completed.stdout)) as raw_video:
            video_frame = raw_video.convert("RGB").resize((160, 90))
        with Image.open(screenshot) as raw_screenshot:
            renderer_frame = raw_screenshot.convert("RGB").resize((160, 90))
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "failures": [f"renderer/video frame comparison failed: {exc}"]}
    difference = ImageChops.difference(video_frame, renderer_frame)
    mean_difference = sum(ImageStat.Stat(difference).mean) / (3 * 255)
    ok = mean_difference <= max_mean_difference
    return {
        "ok": ok,
        "failures": []
        if ok
        else [
            f"renderer frame does not match candidate video at {timestamp:.3f}s "
            f"(seek {seek_timestamp:.3f}s): mean difference {mean_difference:.4f} "
            f"> {max_mean_difference:.4f}"
        ],
        "timestamp": timestamp,
        "seekTimestamp": seek_timestamp,
        "meanDifference": mean_difference,
        "maxMeanDifference": max_mean_difference,
    }


def live_renderer_contract(
    args: argparse.Namespace,
    video_result: dict[str, Any],
    failures: list[str],
) -> tuple[dict[str, Any], dict[str, Any] | None]:
    required_inputs = {
        "renderer": args.renderer,
        "renderer report": args.renderer_report,
        "asset manifest": args.asset_manifest,
        "composition plan": args.composition_plan,
        "brief": args.brief,
        "video": args.video,
    }
    missing = [label for label, path in required_inputs.items() if path is None or not path.is_file()]
    if missing:
        failures.append("live renderer validation is missing current inputs: " + ", ".join(missing))
        return {"ok": False, "missingInputs": missing}, None
    assert args.renderer is not None
    if args.renderer.suffix.lower() not in {".html", ".htm"}:
        failures.append(
            "live renderer visual coverage currently requires an HTML renderer; "
            f"got {args.renderer.suffix or '<no extension>'}"
        )
        return {"ok": False, "unsupportedRenderer": str(args.renderer)}, None

    properties = video_result.get("properties", {}) if isinstance(video_result, dict) else {}
    duration = getattr(args, "expect_duration", None) or properties.get("durationSeconds") or 70.0
    width = getattr(args, "expect_width", None) or properties.get("width") or 1280
    height = getattr(args, "expect_height", None) or properties.get("height") or 720
    fps = getattr(args, "expect_fps", None) or properties.get("fps") or 30.0
    try:
        duration = float(duration)
        width = int(width)
        height = int(height)
        fps = float(fps)
    except (TypeError, ValueError):
        failures.append("live renderer validation could not determine numeric duration/width/height")
        return {"ok": False, "invalidGeometry": True}, None

    with tempfile.TemporaryDirectory(prefix="awsome-package-renderer-") as temp_dir:
        screenshot_dir = Path(temp_dir) / "screenshots"
        live = check_renderer_contract.sample_renderer(
            argparse.Namespace(
                html=args.renderer,
                video_id=None,
                duration=duration,
                width=width,
                height=height,
                brief=args.brief,
                asset_manifest=args.asset_manifest,
                composition_plan=args.composition_plan,
                require_visual_ids=True,
                require_all_brief_beats=True,
                brief_beat_sample_position=0.5,
                times=None,
                min_unique_beats=4,
                min_screenshot_stddev=4.0,
                min_screenshot_colors=32,
                screenshot_dir=screenshot_dir,
                output=None,
                install_browser=False,
                json=True,
            )
        )
        pixel_matches: list[dict[str, Any]] = []
        for analysis in live.get("screenshotAnalyses", []):
            if not isinstance(analysis, dict):
                continue
            screenshot = analysis.get("path")
            timestamp = analysis.get("time")
            if not isinstance(screenshot, str) or not isinstance(timestamp, (int, float)):
                continue
            screenshot_path = Path(screenshot)
            if not screenshot_path.is_file():
                continue
            match = compare_renderer_frame_to_video(
                args.video,
                float(timestamp),
                screenshot_path,
                video_duration=duration,
                video_fps=fps,
                max_mean_difference=0.04,
            )
            pixel_matches.append(match)

    expected_pixel_matches = len(live.get("screenshotAnalyses", []))
    pixel_ok = bool(pixel_matches) and len(pixel_matches) == expected_pixel_matches and all(
        match.get("ok") is True for match in pixel_matches
    )
    live["candidateVideoPixelCoverageOk"] = pixel_ok
    live["candidateVideoFrameMatches"] = pixel_matches
    if not pixel_ok:
        pixel_failures = [
            finding
            for match in pixel_matches
            for finding in match.get("failures", [])
            if isinstance(finding, str)
        ]
        detail = "; ".join(pixel_failures[:3]) or (
            f"only {len(pixel_matches)} of {expected_pixel_matches} sampled renderer frames were comparable"
        )
        live.setdefault("failures", []).append("renderer pixels are not bound to the candidate MP4: " + detail)
        live["ok"] = False

    for finding in live.get("failures", []):
        failures.append(f"live renderer contract: {finding}")

    stored = load_json_object(args.renderer_report)
    mismatched_fields: list[str] = []
    if stored is None:
        failures.append("stored renderer report cannot be compared with the live renderer result")
    else:
        mismatched_fields = [
            field for field in RENDERER_LIVE_COMPARISON_FIELDS if stored.get(field) != live.get(field)
        ]
        if mismatched_fields:
            failures.append(
                "stored renderer report differs from the live renderer contract for: "
                + ", ".join(mismatched_fields)
            )

    summary = {
        "ok": live.get("ok") is True and pixel_ok and not mismatched_fields,
        "sampleCount": len(live.get("states", [])),
        "candidateVideoPixelCoverageOk": pixel_ok,
        "candidateVideoFrameMatches": pixel_matches,
        "storedReportMatches": not mismatched_fields and stored is not None,
        "mismatchedStoredFields": mismatched_fields,
        "criticalFields": {field: live.get(field) for field in RENDERER_LIVE_COMPARISON_FIELDS},
    }
    return summary, live


def recompute_readiness(
    args: argparse.Namespace,
    failures: list[str],
) -> dict[str, Any]:
    if args.readiness_report is None or not args.readiness_report.is_file():
        failures.append("readiness recomputation requires the current readiness report")
        return {"ok": False, "missingReadinessReport": True}
    live = score_video_readiness.score(
        argparse.Namespace(
            brief=args.brief,
            video=args.video,
            video_validation=None,
            package_validation=None,
            renderer_report=args.renderer_report,
            renderer=args.renderer,
            asset_manifest=args.asset_manifest,
            composition_plan=args.composition_plan,
            visual_review=args.visual_review,
            visual_contract_report=args.visual_contract_report,
            require_visual_contract_report=bool(
                args.require_visual_contract or args.require_renderer_visual_coverage
            ),
            quality_report=args.quality_report,
            motion_report=args.motion_report,
            capture_manifest=args.capture_manifest,
            audio_report=args.audio_report,
            require_final_audio=args.require_final_audio,
            contact_sheet=args.contact_sheet,
            require_voiceover=args.require_voiceover,
            min_voiceover_lines=args.min_voiceover_lines,
            require_source_links=args.require_source_links,
            min_ready_score=args.min_readiness_score,
            output=None,
            json=True,
        )
    )
    stored = load_json_object(args.readiness_report)
    matches = stored == live
    if live.get("ok") is not True:
        failures.append(
            "live readiness recomputation failed: "
            + "; ".join(str(item) for item in live.get("failures", []))
        )
    if not matches:
        differing = sorted(
            key
            for key in set((stored or {}).keys()) | set(live.keys())
            if (stored or {}).get(key) != live.get(key)
        )
        failures.append(
            "stored readiness report differs from a live recomputation for: "
            + ", ".join(differing)
        )
    return {
        "ok": live.get("ok") is True and matches,
        "storedReportMatches": matches,
        "readiness": live.get("readiness"),
        "score": live.get("score"),
        "weakCategories": live.get("weakCategories"),
        "failures": live.get("failures", []),
    }


def validate(args: argparse.Namespace) -> dict[str, Any]:
    failures: list[str] = []
    warnings: list[str] = []

    if args.require_visual_contract:
        missing_visual_flags = [
            flag
            for flag, enabled in [
                ("--require-ready-assets", args.require_ready_assets),
                ("--require-specialist-routing", args.require_specialist_routing),
                ("--require-source-routing", args.require_source_routing),
                ("--require-reviewed-scenes", args.require_reviewed_scenes),
                ("--require-renderer-visual-coverage", args.require_renderer_visual_coverage),
                ("--forbid-scaffold-renderer", args.forbid_scaffold_renderer),
            ]
            if not enabled
        ]
        if missing_visual_flags:
            failures.append(
                "--require-visual-contract also requires final visual gates: "
                + ", ".join(missing_visual_flags)
            )

    if not args.brief.exists():
        brief_result: dict[str, Any] = {
            "ok": False,
            "failures": [f"brief not found: {args.brief}"],
        }
        failures.extend(brief_result["failures"])
    else:
        brief_result = check_video_brief.validate(
            read_text(args.brief),
            args.min_beats,
            args.require_voiceover,
            args.min_voiceover_lines,
            getattr(args, "require_source_links", False),
        )
        failures.extend(f"brief: {failure}" for failure in brief_result.get("failures", []))

    video_result = check_video_artifact.validate(build_artifact_args(args))
    failures.extend(f"video: {failure}" for failure in video_result.get("failures", []))
    warnings.extend(f"video: {warning}" for warning in video_result.get("warnings", []))

    visual_args = build_visual_contract_args(args)
    if visual_args is None:
        visual_contract_result: dict[str, Any] = {
            "ok": False,
            "failures": ["asset manifest and composition plan were not both supplied"],
            "warnings": [],
        }
        if args.require_visual_contract:
            failures.extend(f"visual contract: {item}" for item in visual_contract_result["failures"])
        else:
            warnings.append("visual contract inputs were not supplied")
    else:
        visual_contract_result = check_visual_contract.validate(visual_args)
        failures.extend(f"visual contract: {item}" for item in visual_contract_result.get("failures", []))
        warnings.extend(f"visual contract: {item}" for item in visual_contract_result.get("warnings", []))

    live_renderer_result: dict[str, Any] | None = None
    if bool(getattr(args, "require_renderer_visual_coverage", False)) or bool(
        getattr(args, "require_readiness_report", False)
    ):
        live_renderer_result, _live_renderer_full = live_renderer_contract(args, video_result, failures)

    live_readiness_result: dict[str, Any] | None = None
    if bool(getattr(args, "require_readiness_report", False)):
        live_readiness_result = recompute_readiness(args, failures)

    package: dict[str, Any] = {
        "brief": {"path": str(args.brief), "exists": args.brief.exists()},
        "designNote": validate_design_note(args.design_note, failures, warnings, args.require_design_note),
        "productionNotes": validate_production_notes(
            args.production_notes,
            failures,
            warnings,
            args.require_production_notes,
            args.expect_duration,
            args.require_final_audio,
            args.require_final_review_notes,
            args.require_pattern_blueprint,
            args.require_source_links,
        ),
        "packageManifest": validate_package_manifest(
            args.package_manifest,
            failures,
            warnings,
            args.require_package_manifest,
            args.require_final_audio,
            args.require_final_review_notes,
            args.require_pattern_blueprint,
            args.require_style_fidelity_report,
            args.require_source_links,
            args.require_visual_contract,
            {
                "brief": args.brief,
                "designNote": args.design_note,
                "productionNotes": args.production_notes,
                "patternBlueprintJson": args.pattern_blueprint,
                "assetManifest": args.asset_manifest,
                "compositionPlan": args.composition_plan,
                "visualReview": args.visual_review,
                "visualContractValidation": args.visual_contract_report,
                "renderer": args.renderer,
                "rendererValidation": args.renderer_report,
                "video": args.video,
                "contactSheet": args.contact_sheet,
                "qualityReport": args.quality_report,
                "motionReport": args.motion_report,
                "captureManifest": args.capture_manifest,
                "audioReport": args.audio_report,
                "readinessScore": args.readiness_report,
                "styleFidelity": args.style_fidelity_report,
            },
        ),
        "patternBlueprint": validate_pattern_blueprint(
            args.pattern_blueprint,
            failures,
            warnings,
            args.require_pattern_blueprint,
        ),
        "visualContract": visual_contract_result,
        "visualContractReport": validate_visual_contract_report(
            args.visual_contract_report,
            visual_contract_result,
            failures,
            warnings,
            args.require_visual_contract,
        ),
        "renderer": validate_renderer(
            args.renderer,
            failures,
            warnings,
            args.require_renderer,
            args.forbid_scaffold_renderer,
        ),
        "rendererReport": validate_json_report(
            args.renderer_report,
            "renderer contract report",
            failures,
            warnings,
            args.require_renderer_report,
            require_renderer_beat_coverage=args.require_renderer_beat_coverage,
            require_renderer_visual_coverage=args.require_renderer_visual_coverage,
            expected_input_digests={
                "rendererSha256": check_visual_contract.sha256_file(args.renderer) if args.renderer else None,
                "assetManifestSha256": (
                    check_visual_contract.sha256_file(args.asset_manifest) if args.asset_manifest else None
                ),
                "compositionPlanSha256": (
                    check_visual_contract.sha256_file(args.composition_plan) if args.composition_plan else None
                ),
            }
            if args.require_renderer_visual_coverage
            else None,
        ),
        "liveRendererContract": live_renderer_result,
        "readinessReport": validate_readiness_report(
            args.readiness_report,
            failures,
            warnings,
            args.require_readiness_report,
            args.min_readiness_score,
            args.allow_weak_readiness,
            {
                "briefSha256": check_visual_contract.sha256_file(args.brief),
                "videoSha256": check_visual_contract.sha256_file(args.video) if args.video else None,
                "rendererSha256": check_visual_contract.sha256_file(args.renderer) if args.renderer else None,
                "rendererReportSha256": (
                    check_visual_contract.sha256_file(args.renderer_report) if args.renderer_report else None
                ),
                "visualContractReportSha256": (
                    check_visual_contract.sha256_file(args.visual_contract_report)
                    if args.visual_contract_report
                    else None
                ),
                "contactSheetSha256": (
                    check_visual_contract.sha256_file(args.contact_sheet) if args.contact_sheet else None
                ),
            },
        ),
        "liveReadiness": live_readiness_result,
        "styleFidelityReport": validate_style_fidelity_report(
            args.style_fidelity_report,
            failures,
            warnings,
            args.require_style_fidelity_report,
            args.min_style_fidelity_score,
            {
                "briefSha256": check_visual_contract.sha256_file(args.brief),
                "patternBlueprintSha256": (
                    check_visual_contract.sha256_file(args.pattern_blueprint)
                    if args.pattern_blueprint
                    else None
                ),
                "corpusSummarySha256": check_visual_contract.sha256_file(
                    SCRIPT_DIR.parent / "assets" / "reference" / "corpus-summary.json"
                ),
            },
        ),
        "contactSheet": require_file(
            args.contact_sheet,
            "contact sheet",
            failures,
            warnings,
            args.require_contact_sheet,
        ),
        "motionReport": validate_json_report(
            args.motion_report,
            "motion report",
            failures,
            warnings,
            args.require_motion_report,
        ),
        "audioReport": validate_json_report(
            args.audio_report,
            "audio report",
            failures,
            warnings,
            args.require_audio_report or args.require_final_audio,
        ),
    }

    return {
        "ok": not failures,
        "failures": failures,
        "warnings": warnings,
        "brief": brief_result,
        "video": video_result,
        "package": package,
    }


def main() -> int:
    args = parse_args()
    result = validate(args)
    if args.json:
        print(json.dumps(result, indent=2))
    elif result["ok"]:
        brief = result.get("brief", {})
        video_props = result.get("video", {}).get("properties", {})
        print(
            "PASS awsome-videos package: "
            f"{brief.get('time_ranges')} timed beats, "
            f"{video_props.get('width')}x{video_props.get('height')}, "
            f"{video_props.get('durationSeconds')}s"
        )
        for warning in result.get("warnings", []):
            print(f"WARN {warning}")
    else:
        print("FAIL awsome-videos package")
        for failure in result["failures"]:
            print(f"- {failure}")
        for warning in result.get("warnings", []):
            print(f"WARN {warning}")
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
