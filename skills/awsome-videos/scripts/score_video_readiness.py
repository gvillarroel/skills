#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["pillow>=10.0.0"]
# ///
"""Score awsome-videos brief/package readiness against the bundled rubric."""

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
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import check_video_brief  # noqa: E402
import check_visual_contract  # noqa: E402


CATEGORIES = [
    "hook",
    "script_density",
    "visual_mechanism",
    "source_binding",
    "transitions",
    "audio_direction",
    "format_fit",
    "validation",
]

SCRIPT_MOVES = [
    "define",
    "definition",
    "prove",
    "proof",
    "contrast",
    "warning",
    "warn",
    "claim",
    "joke",
    "callback",
    "rule",
    "tradeoff",
    "limitation",
]

SOURCE_TERMS = [
    "screenshot",
    "source",
    "docs",
    "github",
    "terminal",
    "code",
    "ui",
    "dashboard",
    "browser",
    "logo",
    "article",
    "diagram",
]

MECHANISM_TERMS = [
    "mechanism",
    "state",
    "trace",
    "flow",
    "input",
    "output",
    "diagram",
    "system",
    "lifecycle",
    "pipeline",
    "comparison",
]

PLAN_MECHANISM_TERMS = [
    "b-tree",
    "query plan",
    "lookup path",
    "write path",
    "state change",
    "before/after",
    "terminal output",
    "diagram",
    "trace",
    "split-screen",
    "overlay",
    "flow",
]

AUDIO_TERMS = [
    "voiceover",
    "narration",
    "bed",
    "duck",
    "hit",
    "stinger",
    "tick",
    "whoosh",
    "riser",
    "dropout",
    "tail",
    "sfx",
]

HOOK_MAX_SECONDS = 6.0

TIME_RANGE_RE = re.compile(
    r"\b(?P<start>(?:\d{1,2}:)?\d{1,2}:\d{2}|\d{1,3}\s*s?)\s*(?:-|to|through|->)\s*(?P<end>(?:\d{1,2}:)?\d{1,2}:\d{2}|\d{1,3}\s*s?)\b",
    re.IGNORECASE,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Score awsome-videos readiness.")
    parser.add_argument("--brief", required=True, type=Path)
    parser.add_argument("--video", type=Path)
    parser.add_argument("--video-validation", type=Path)
    parser.add_argument("--package-validation", type=Path)
    parser.add_argument("--renderer-report", type=Path)
    parser.add_argument("--renderer", type=Path)
    parser.add_argument("--asset-manifest", type=Path)
    parser.add_argument("--composition-plan", type=Path)
    parser.add_argument("--visual-review", type=Path)
    parser.add_argument("--visual-contract-report", type=Path)
    parser.add_argument("--require-visual-contract-report", action="store_true")
    parser.add_argument("--quality-report", type=Path)
    parser.add_argument("--motion-report", type=Path)
    parser.add_argument("--capture-manifest", type=Path)
    parser.add_argument("--audio-report", type=Path)
    parser.add_argument("--require-final-audio", action="store_true")
    parser.add_argument("--contact-sheet", type=Path)
    parser.add_argument("--require-voiceover", action="store_true")
    parser.add_argument("--min-voiceover-lines", type=int)
    parser.add_argument("--require-source-links", action="store_true")
    parser.add_argument("--min-ready-score", type=int, default=18)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    return parser.parse_args()


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def sha256_path(path: Path | None) -> str | None:
    if path is None or not path.is_file():
        return None
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path | None, label: str, warnings: list[str]) -> dict[str, Any] | None:
    if path is None:
        return None
    if not path.exists():
        warnings.append(f"{label} not found: {path}")
        return None
    try:
        return json.loads(read_text(path))
    except json.JSONDecodeError as exc:
        warnings.append(f"{label} is not valid JSON: {exc}")
        return None


def count_any(text: str, terms: list[str]) -> int:
    return sum(1 for term in terms if term in text)


def category(score: int, evidence: list[str], fix: str = "") -> dict[str, Any]:
    return {"score": max(0, min(3, score)), "evidence": evidence, "fix": fix}


def parse_time_to_seconds(value: str) -> float | None:
    cleaned = value.strip().lower().replace(" ", "")
    if cleaned.endswith("s"):
        cleaned = cleaned[:-1]
    if ":" in cleaned:
        parts = cleaned.split(":")
        try:
            numbers = [float(part) for part in parts]
        except ValueError:
            return None
        if len(numbers) == 2:
            return numbers[0] * 60 + numbers[1]
        if len(numbers) == 3:
            return numbers[0] * 3600 + numbers[1] * 60 + numbers[2]
        return None
    try:
        return float(cleaned)
    except ValueError:
        return None


def find_immediate_hook_range(text: str) -> tuple[float, float] | None:
    for match in TIME_RANGE_RE.finditer(text):
        start = parse_time_to_seconds(match.group("start"))
        end = parse_time_to_seconds(match.group("end"))
        if start is None or end is None:
            continue
        if start <= 1.0 and 0 < end <= HOOK_MAX_SECONDS:
            return start, end
        if start <= 1.0:
            return None
    return None


def renderer_state_counts(renderer_report: dict[str, Any] | None) -> tuple[int, int]:
    if not renderer_report:
        return 0, 0

    entries = (
        renderer_report.get("states")
        or renderer_report.get("sampledStates")
        or renderer_report.get("statesSample")
        or []
    )
    states = len(entries) if isinstance(entries, list) else 0

    unique_beats_raw = renderer_report.get("uniqueBeats")
    if isinstance(unique_beats_raw, list):
        unique_beats = len({str(item) for item in unique_beats_raw})
    else:
        unique_beats = 0

    if unique_beats == 0 and isinstance(entries, list):
        beats: set[str] = set()
        for entry in entries:
            if not isinstance(entry, dict):
                continue
            state = entry.get("state") if isinstance(entry.get("state"), dict) else entry
            active = state.get("activeBeat") if isinstance(state, dict) else None
            if active is not None:
                beats.add(str(active))
        unique_beats = len(beats)

    summary = renderer_report.get("stateSummary")
    if isinstance(summary, dict):
        active_summary = summary.get("activeBeat")
        if isinstance(active_summary, dict):
            if isinstance(active_summary.get("count"), int):
                states = max(states, int(active_summary["count"]))
            if isinstance(active_summary.get("distinctCount"), int):
                unique_beats = max(unique_beats, int(active_summary["distinctCount"]))
            elif isinstance(active_summary.get("distinctValues"), list):
                unique_beats = max(unique_beats, len({str(item) for item in active_summary["distinctValues"]}))

    if states == 0 and isinstance(renderer_report.get("samples"), int):
        states = int(renderer_report["samples"])

    return states, unique_beats


def valid_sha256(value: Any) -> bool:
    return isinstance(value, str) and re.fullmatch(r"[0-9a-f]{64}", value) is not None


def visual_contract_evidence(report: dict[str, Any] | None) -> tuple[bool, list[str]]:
    findings: list[str] = []
    if not isinstance(report, dict) or report.get("schemaVersion") != 1 or report.get("ok") is not True:
        return False, ["visual contract is missing schemaVersion=1 or ok=true"]
    if report.get("failures") not in ([], None):
        findings.append("visual contract reports failures")
    digests = report.get("inputDigests")
    digest_names = [
        "assetManifestSha256",
        "compositionPlanSha256",
        "visualReviewSha256",
        "videoSha256",
    ]
    if not isinstance(digests, dict) or not all(valid_sha256(digests.get(name)) for name in digest_names):
        findings.append("visual contract input digests are incomplete")

    assets = report.get("assetManifest")
    asset_count = assets.get("assetCount") if isinstance(assets, dict) else None
    ready_count = assets.get("readyAssetCount") if isinstance(assets, dict) else None
    inspections = assets.get("inspections") if isinstance(assets, dict) else None
    if not isinstance(asset_count, int) or asset_count < 1 or ready_count != asset_count:
        findings.append("visual contract does not prove a positive fully-ready asset count")
    if not isinstance(inspections, dict) or len(inspections) != asset_count or not all(
        isinstance(item, dict) and item.get("ok") is True for item in inspections.values()
    ):
        findings.append("visual contract does not prove passing inspection for every asset")

    composition = report.get("compositionPlan")
    scene_count = composition.get("sceneCount") if isinstance(composition, dict) else None
    bounds = composition.get("bounds") if isinstance(composition, dict) else None
    if not isinstance(scene_count, int) or scene_count < 1:
        findings.append("visual contract does not prove a positive scene count")
    if not isinstance(bounds, dict) or len(bounds) != scene_count or not all(
        isinstance(item, dict)
        and isinstance(item.get("focalArea"), (int, float))
        and float(item["focalArea"]) >= 0.05
        for item in bounds.values()
    ):
        findings.append("visual contract composition bounds are incomplete")

    seams = report.get("seams")
    seam_failure_keys = [
        "missingManifestBeatIds",
        "missingCompositionBeatIds",
        "unknownManifestSceneIds",
        "unknownCompositionAssetIds",
        "orphanAssetIds",
        "scenesWithoutAssets",
        "inconsistentSceneAssetLinks",
        "briefBeatSceneMismatches",
        "briefTimingMismatches",
    ]
    if not isinstance(seams, dict) or any(seams.get(key) not in ([], None) for key in seam_failure_keys):
        findings.append("visual contract scene/beat/asset seams are incomplete")
    expected_beats = seams.get("expectedBeatIds") if isinstance(seams, dict) else None
    if not isinstance(expected_beats, list) or not isinstance(scene_count, int) or len(expected_beats) < scene_count:
        findings.append("visual contract expected beat coverage is incomplete")
    expected_scene_order = seams.get("expectedSceneOrder") if isinstance(seams, dict) else None
    actual_scene_order = seams.get("actualSceneOrder") if isinstance(seams, dict) else None
    if (
        not isinstance(expected_scene_order, list)
        or not isinstance(actual_scene_order, list)
        or expected_scene_order != actual_scene_order
        or not isinstance(scene_count, int)
        or len(expected_scene_order) != scene_count
    ):
        findings.append("visual contract scene order is incomplete")

    routing = report.get("skillRouting")
    route_count = routing.get("count") if isinstance(routing, dict) else None
    complete_count = routing.get("completeCount") if isinstance(routing, dict) else None
    skipped_count = routing.get("skippedCount") if isinstance(routing, dict) else None
    route_skills = routing.get("skills") if isinstance(routing, dict) else None
    required_route_skills = {
        "source-to-video-director",
        "scene-composition-director",
        "scene-transition-director",
    }
    if (
        not isinstance(route_count, int)
        or route_count < 4
        or not isinstance(complete_count, int)
        or not isinstance(skipped_count, int)
        or complete_count + skipped_count != route_count
        or not isinstance(route_skills, list)
        or not required_route_skills.issubset(set(route_skills))
    ):
        findings.append("visual contract skill routing evidence is incomplete")

    review = report.get("visualReview")
    if not isinstance(review, dict) or review.get("required") is not True:
        findings.append("visual contract does not require reviewed scenes")
    else:
        if review.get("overallStatus") != "approved":
            findings.append("visual review is not approved")
        if review.get("sceneReviewCount") != scene_count:
            findings.append("visual review does not cover every scene")
        scene_evidence_count = review.get("sceneEvidenceFrameCount")
        if (
            not isinstance(scene_evidence_count, int)
            or not isinstance(scene_count, int)
            or scene_evidence_count < scene_count * 4
        ):
            findings.append("visual review lacks first/hold/emphasis/final evidence for every scene")
        transition_count = review.get("transitionReviewCount")
        expected_transitions = max(0, int(scene_count or 0) - 1)
        if not isinstance(transition_count, int) or transition_count < expected_transitions:
            findings.append("visual review has too few transition reviews")
        transition_evidence_count = review.get("transitionEvidenceFrameCount")
        if not isinstance(transition_evidence_count, int) or transition_evidence_count < expected_transitions * 3:
            findings.append("visual review lacks before/midpoint/after transition evidence")
        frame_match_count = review.get("videoFrameMatchCount")
        expected_frame_matches = int(scene_count or 0) * 4 + expected_transitions * 3
        if not isinstance(frame_match_count, int) or frame_match_count < expected_frame_matches:
            findings.append("visual review evidence is not bound to candidate-video frames")
        frame_matches = review.get("videoFrameMatches")
        if not isinstance(frame_matches, list) or len(frame_matches) != frame_match_count or not all(
            isinstance(item, dict) and item.get("ok") is True for item in frame_matches
        ):
            findings.append("visual review candidate-video frame matches are incomplete or failing")
    return not findings, findings


def renderer_visual_evidence(
    renderer_report: dict[str, Any] | None,
    visual_contract: dict[str, Any] | None,
) -> tuple[bool, list[str]]:
    findings: list[str] = []
    visual_ok, visual_findings = visual_contract_evidence(visual_contract)
    if not visual_ok:
        findings.extend(visual_findings)
    if not isinstance(renderer_report, dict) or renderer_report.get("ok") is not True:
        return False, [*findings, "renderer report is missing ok=true"]
    if renderer_report.get("failures") not in ([], None):
        findings.append("renderer report contains failures")
    for field in ["visualAssetCoverageOk", "assetBindingCoverageOk", "compositionCoverageOk", "briefBeatCoverageOk"]:
        if renderer_report.get(field) is not True:
            findings.append(f"renderer report lacks {field}=true")
    expected_assets = renderer_report.get("expectedAssetIds")
    observed_assets = renderer_report.get("observedAssetIds")
    expected_compositions = renderer_report.get("expectedCompositionIds")
    observed_compositions = renderer_report.get("observedCompositionIds")
    if not isinstance(expected_assets, list) or not expected_assets or not isinstance(observed_assets, list) or set(
        observed_assets
    ) != set(expected_assets):
        findings.append("renderer expected/observed asset coverage is incomplete")
    if not isinstance(expected_compositions, list) or not expected_compositions or not isinstance(
        observed_compositions, list
    ) or set(observed_compositions) != set(expected_compositions):
        findings.append("renderer expected/observed composition coverage is incomplete")
    for field in ["missingAssetIds", "missingCompositionIds", "missingCompositionObjectIds", "missingBriefBeats"]:
        if renderer_report.get(field) not in ([], None):
            findings.append(f"renderer report contains {field}")
    digests = visual_contract.get("inputDigests", {}) if isinstance(visual_contract, dict) else {}
    for renderer_field, visual_field in [
        ("assetManifestSha256", "assetManifestSha256"),
        ("compositionPlanSha256", "compositionPlanSha256"),
    ]:
        if not valid_sha256(renderer_report.get(renderer_field)) or renderer_report.get(renderer_field) != digests.get(
            visual_field
        ):
            findings.append(f"renderer {renderer_field} is stale or unbound")
    if not valid_sha256(renderer_report.get("rendererSha256")):
        findings.append("renderer source hash is missing")
    states, unique_beats = renderer_state_counts(renderer_report)
    scene_count = (
        visual_contract.get("compositionPlan", {}).get("sceneCount")
        if isinstance(visual_contract, dict) and isinstance(visual_contract.get("compositionPlan"), dict)
        else 0
    )
    if not isinstance(scene_count, int) or scene_count < 1 or states < scene_count:
        findings.append("renderer state evidence does not cover every composed scene")
    if unique_beats < min(4, int(scene_count or 0)):
        findings.append("renderer unique beat evidence is too thin")
    return not findings, findings


def score_hook(text: str, brief_result: dict[str, Any]) -> dict[str, Any]:
    evidence: list[str] = []
    has_hook = count_any(text, ["hook", "cold-open", "cold open", "opening"]) > 0
    immediate_hook = find_immediate_hook_range(text)
    has_claim = count_any(text, ["claim", "contradiction", "payoff", "promise", "proof visual"]) > 0
    if immediate_hook:
        evidence.append(f"first timed beat starts immediately and resolves by {immediate_hook[1]:g}s")
    if has_hook:
        evidence.append("hook/cold-open language is present")
    if has_claim:
        evidence.append("claim, contradiction, payoff, or proof language is present")
    score = 3 if has_hook and immediate_hook and has_claim else 2 if has_hook and (immediate_hook or has_claim) else 1 if brief_result.get("time_ranges", 0) else 0
    return category(score, evidence, "Open with a visible claim plus proof in 0:00-0:05.")


def score_script_density(text: str, brief_result: dict[str, Any]) -> dict[str, Any]:
    beats = int(brief_result.get("time_ranges") or 0)
    moves = count_any(text, SCRIPT_MOVES)
    evidence = [f"{beats} timed beats", f"{moves} dense script move terms"]
    score = 3 if beats >= 8 and moves >= 7 else 2 if beats >= 8 and moves >= 4 else 1 if beats >= 4 else 0
    return category(score, evidence, "Make every beat define, prove, contrast, warn, joke, or callback.")


def score_visual_mechanism(
    text: str,
    renderer_report: dict[str, Any] | None,
    visual_contract: dict[str, Any] | None,
    finished: bool,
) -> dict[str, Any]:
    mechanism_hits = count_any(text, MECHANISM_TERMS)
    plan_mechanism_hits = count_any(text, PLAN_MECHANISM_TERMS)
    states, unique_beats = renderer_state_counts(renderer_report)
    evidence = [f"{mechanism_hits} mechanism terms", f"{plan_mechanism_hits} plan-mechanism terms"]
    if renderer_report:
        evidence.append(f"{states} renderer states")
        evidence.append(f"{unique_beats} unique sampled beats")
    visual_proof, proof_findings = renderer_visual_evidence(renderer_report, visual_contract)
    if visual_proof:
        composition = visual_contract.get("compositionPlan", {})
        evidence.append(
            f"validated visible asset IDs across {composition.get('sceneCount', '?')} composed scenes"
        )
    score = (
        3
        if mechanism_hits >= 6 and unique_beats >= 4
        else 2
        if (mechanism_hits >= 4 and (unique_beats >= 2 or states >= 4)) or (mechanism_hits >= 6 and plan_mechanism_hits >= 4)
        else 1
        if mechanism_hits >= 2
        else 0
    )
    if visual_proof:
        score = 3
    elif finished:
        score = min(score, 1)
        evidence.append("finished-video visual contract evidence is missing")
        if proof_findings:
            evidence.append("visual evidence gaps: " + "; ".join(proof_findings[:3]))
    return category(score, evidence, "Show the mechanism changing state without relying only on narration.")


def score_source_binding(
    text: str,
    brief_result: dict[str, Any],
    visual_contract: dict[str, Any] | None,
    finished: bool,
) -> dict[str, Any]:
    source_hits = count_any(text, SOURCE_TERMS)
    source_links = int(brief_result.get("source_link_count") or 0)
    has_asset_plan = count_any(text, ["visual source plan", "assets", "source links", "screenshots", "code/ui captures"]) >= 2
    evidence = [f"{source_hits} source-bound visual terms"]
    if source_links:
        evidence.append(f"{source_links} concrete source links")
    if has_asset_plan:
        evidence.append("asset/source plan is present")
    validated_assets, asset_findings = visual_contract_evidence(visual_contract)
    if validated_assets:
        evidence.append(
            f"{visual_contract.get('assetManifest', {}).get('assetCount')} ready assets have provenance and scene-use coverage"
        )
    score = (
        3
        if (source_hits >= 8 and has_asset_plan) or source_links >= 2
        else 2
        if source_hits >= 5 or source_links >= 1
        else 1
        if source_hits >= 2
        else 0
    )
    if validated_assets:
        score = 3
    elif finished:
        score = min(score, 1)
        evidence.append("finished-video asset provenance/use evidence is missing")
        if asset_findings:
            evidence.append("asset evidence gaps: " + "; ".join(asset_findings[:3]))
    return category(
        score,
        evidence,
        "Bind every major visual to code, UI, docs, screenshots, terminal output, diagrams, or concrete source links.",
    )


def score_transitions(text: str, brief_result: dict[str, Any]) -> dict[str, Any]:
    transition_hits = int(brief_result.get("transition_hits") or 0)
    idea_terms = count_any(text, ["idea", "proof point", "reversal", "section", "joke", "callback", "match cut"])
    evidence = [f"{transition_hits} transition cue terms", f"{idea_terms} transition-purpose terms"]
    score = 3 if transition_hits >= 5 and idea_terms >= 2 else 2 if transition_hits >= 3 else 1 if transition_hits >= 1 else 0
    return category(score, evidence, "Use each cut, zoom, wipe, or insert as punctuation for a new idea, proof, reversal, or joke.")


def score_audio(text: str, brief_result: dict[str, Any]) -> dict[str, Any]:
    audio_hits = int(brief_result.get("audio_hits") or 0)
    role_hits = count_any(text, AUDIO_TERMS)
    evidence = [f"{audio_hits} audio cue terms", f"{role_hits} named audio role terms"]
    score = 3 if audio_hits >= 6 and role_hits >= 6 else 2 if audio_hits >= 3 and role_hits >= 3 else 1 if audio_hits >= 1 else 0
    return category(score, evidence, "Specify bed, voiceover ducking, hits, ticks, risers, dropouts, and final tail by timing.")


def score_format_fit(text: str, brief_result: dict[str, Any], video_validation: dict[str, Any] | None) -> dict[str, Any]:
    beats = int(brief_result.get("time_ranges") or 0)
    has_format = count_any(text, ["format:", "compressed explainer", "trend/news", "tutorial", "deep walkthrough"]) > 0
    has_runtime = "runtime:" in text
    duration = None
    fps = None
    if video_validation:
        props = video_validation.get("properties") or {}
        duration = props.get("durationSeconds")
        fps = props.get("fps")
    evidence = [f"{beats} timed beats"]
    if has_format:
        evidence.append("format is declared")
    if has_runtime:
        evidence.append("runtime is declared")
    if duration is not None:
        evidence.append(f"video duration {duration}s")
    if fps is not None:
        evidence.append(f"video fps {fps}")
    video_ok = video_validation is None or video_validation.get("ok") is True
    score = 3 if beats >= 8 and has_format and has_runtime and video_ok else 2 if beats >= 8 and has_format else 1 if beats >= 4 else 0
    return category(score, evidence, "Declare the intended format/runtime and keep the beat count proportional to it.")


def report_ok(report: dict[str, Any] | None) -> bool:
    if not report:
        return False
    if report.get("ok") is False or report.get("passed") is False:
        return False
    return report.get("ok") is True or report.get("passed") is True


def score_validation(
    text: str,
    *,
    video_validation: dict[str, Any] | None,
    package_validation: dict[str, Any] | None,
    quality_report: dict[str, Any] | None,
    motion_report: dict[str, Any] | None,
    capture_manifest: dict[str, Any] | None,
    renderer_report: dict[str, Any] | None,
    visual_contract_report: dict[str, Any] | None,
    audio_report: dict[str, Any] | None,
    contact_sheet: Path | None,
    video: Path | None,
) -> dict[str, Any]:
    ok_reports = sum(
        1
        for report in [
            video_validation,
            package_validation,
            quality_report,
            motion_report,
            capture_manifest,
            audio_report,
        ]
        if report_ok(report)
    )
    visual_ok, _ = visual_contract_evidence(visual_contract_report)
    renderer_ok, _ = renderer_visual_evidence(renderer_report, visual_contract_report)
    ok_reports += int(visual_ok) + int(renderer_ok)
    contact_ok = contact_sheet is not None and contact_sheet.exists() and contact_sheet.stat().st_size > 1_000
    video_ok = video is not None and video.exists() and video.stat().st_size > 1_000
    command_terms = count_any(text, ["validate", "validation", "check_video", "expected", "pass"])
    plan_validation_terms = count_any(text, ["check_video_brief.py", "score_style_fidelity.py", "score_video_readiness.py", "json", "output"])
    evidence = [f"{ok_reports} ok/passed JSON reports", f"{command_terms} validation terms"]
    if plan_validation_terms:
        evidence.append(f"{plan_validation_terms} plan validation command terms")
    if contact_ok:
        evidence.append("contact sheet exists")
    if video_ok:
        evidence.append("video artifact exists")
    if audio_report:
        final_text = "final audio ready" if audio_report.get("finalAudioReady") is True else "audio needs final mix"
        evidence.append(final_text)
        if audio_report.get("sourceDurationSeconds") is not None:
            evidence.append(f"audio source duration {audio_report.get('sourceDurationSeconds')}s")
    score = (
        3
        if ok_reports >= 3 and contact_ok and video_ok
        else 2
        if (ok_reports >= 2 and (contact_ok or video_ok)) or (ok_reports == 0 and command_terms >= 2 and plan_validation_terms >= 3)
        else 1
        if ok_reports >= 1 or command_terms >= 2
        else 0
    )
    return category(score, evidence, "Run brief, renderer, video, package, audio, contact-sheet, motion, and quality checks before handoff.")


def readiness_label(total: int) -> str:
    if total >= 22:
        return "ready"
    if total >= 18:
        return "usable"
    if total >= 14:
        return "rewrite"
    return "not-ready"


def score(args: argparse.Namespace) -> dict[str, Any]:
    warnings: list[str] = []
    failures: list[str] = []
    if not args.brief.exists():
        return {"ok": False, "failures": [f"brief not found: {args.brief}"], "warnings": []}

    brief_text_raw = read_text(args.brief)
    text = brief_text_raw.lower()
    brief_result = check_video_brief.validate(
        brief_text_raw,
        min_beats=8,
        require_voiceover=bool(getattr(args, "require_voiceover", False)),
        min_voiceover_lines=getattr(args, "min_voiceover_lines", None),
        require_source_links=bool(getattr(args, "require_source_links", False)),
    )
    if not brief_result.get("ok"):
        failures.extend(f"brief: {item}" for item in brief_result.get("failures", []))

    video_validation = load_json(args.video_validation, "video validation", warnings)
    package_validation = load_json(args.package_validation, "package validation", warnings)
    renderer_report = load_json(args.renderer_report, "renderer report", warnings)
    visual_contract_report = load_json(
        getattr(args, "visual_contract_report", None),
        "visual contract report",
        warnings,
    )
    quality_report = load_json(args.quality_report, "quality report", warnings)
    motion_report = load_json(getattr(args, "motion_report", None), "motion report", warnings)
    capture_manifest = load_json(args.capture_manifest, "capture manifest", warnings)
    audio_report = load_json(getattr(args, "audio_report", None), "audio report", warnings)
    if getattr(args, "require_final_audio", False):
        if audio_report is None:
            failures.append("audio report is required when --require-final-audio is used")
        else:
            if audio_report.get("finalAudioReady") is not True or audio_report.get("placeholderAudio") is True:
                failures.append("final audio is required but audio report indicates placeholder or unfinished audio")
            if audio_report.get("finalAudioDurationOk") is not True:
                failures.append("final audio is required but audio report does not prove duration coverage")
    if getattr(args, "require_visual_contract_report", False):
        asset_manifest = getattr(args, "asset_manifest", None)
        composition_plan = getattr(args, "composition_plan", None)
        visual_review = getattr(args, "visual_review", None)
        renderer_path = getattr(args, "renderer", None)
        missing_inputs = [
            name
            for name, value in [
                ("--asset-manifest", asset_manifest),
                ("--composition-plan", composition_plan),
                ("--visual-review", visual_review),
                ("--video", args.video),
                ("--renderer", renderer_path),
            ]
            if value is None
        ]
        if missing_inputs:
            failures.append(
                "--require-visual-contract-report also requires current inputs: " + ", ".join(missing_inputs)
            )
        else:
            current_visual = check_visual_contract.validate(
                argparse.Namespace(
                    asset_manifest=asset_manifest,
                    composition_plan=composition_plan,
                    visual_review=visual_review,
                    video=args.video,
                    brief=args.brief,
                    project_root=asset_manifest.parent.parent,
                    min_assets=max(1, int(brief_result.get("beat_table_rows") or 1)),
                    min_scenes=max(1, int(brief_result.get("beat_table_rows") or 1)),
                    require_ready_assets=True,
                    require_specialist_routing=True,
                    require_source_routing=True,
                    require_reviewed_scenes=True,
                    output=None,
                    json=True,
                )
            )
            if current_visual.get("ok") is not True:
                failures.extend(
                    f"current visual contract: {finding}" for finding in current_visual.get("failures", [])
                )
            if visual_contract_report != current_visual:
                failures.append("visual contract report is stale or differs from current source artifacts")
            visual_contract_report = current_visual
            if renderer_report is None or renderer_report.get("rendererSha256") != sha256_path(renderer_path):
                failures.append("renderer report is stale or does not match the current renderer")
        visual_evidence_ok, visual_evidence_findings = visual_contract_evidence(visual_contract_report)
        if not visual_evidence_ok:
            failures.append(
                "a complete passing visual contract report is required: "
                + "; ".join(visual_evidence_findings)
            )

    finished = args.video is not None or getattr(args, "require_visual_contract_report", False)

    categories = {
        "hook": score_hook(text, brief_result),
        "script_density": score_script_density(text, brief_result),
        "visual_mechanism": score_visual_mechanism(text, renderer_report, visual_contract_report, finished),
        "source_binding": score_source_binding(text, brief_result, visual_contract_report, finished),
        "transitions": score_transitions(text, brief_result),
        "audio_direction": score_audio(text, brief_result),
        "format_fit": score_format_fit(text, brief_result, video_validation),
        "validation": score_validation(
            text,
            video_validation=video_validation,
            package_validation=package_validation,
            quality_report=quality_report,
            motion_report=motion_report,
            capture_manifest=capture_manifest,
            renderer_report=renderer_report,
            visual_contract_report=visual_contract_report,
            audio_report=audio_report,
            contact_sheet=args.contact_sheet,
            video=args.video,
        ),
    }
    total = sum(item["score"] for item in categories.values())
    weak = [name for name, item in categories.items() if item["score"] < 2]
    if weak:
        failures.append("weak categories: " + ", ".join(weak))
    ready = total >= args.min_ready_score and not weak and not failures
    result = {
        "ok": ready,
        "readiness": readiness_label(total),
        "score": total,
        "maxScore": len(CATEGORIES) * 3,
        "minReadyScore": args.min_ready_score,
        "categories": categories,
        "weakCategories": weak,
        "brief": brief_result,
        "audioReport": audio_report,
        "rendererReport": renderer_report,
        "visualContractReport": visual_contract_report,
        "inputDigests": {
            "briefSha256": sha256_path(args.brief),
            "videoSha256": sha256_path(args.video),
            "rendererSha256": sha256_path(getattr(args, "renderer", None)),
            "rendererReportSha256": sha256_path(args.renderer_report),
            "visualContractReportSha256": sha256_path(getattr(args, "visual_contract_report", None)),
            "contactSheetSha256": sha256_path(args.contact_sheet),
        },
        "failures": failures,
        "warnings": warnings,
    }
    return result


def main() -> int:
    args = parse_args()
    result = score(args)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8", newline="\n")
    if args.json:
        print(json.dumps(result, indent=2))
    elif result["ok"]:
        print(f"PASS awsome-videos readiness: {result['score']}/{result['maxScore']} ({result['readiness']})")
    else:
        print(f"FAIL awsome-videos readiness: {result.get('score', 0)}/{result.get('maxScore', 24)} ({result.get('readiness', 'not-ready')})")
        for failure in result.get("failures", []):
            print(f"- {failure}")
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
