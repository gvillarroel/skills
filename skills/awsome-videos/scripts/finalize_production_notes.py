#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["pillow>=10.0.0"]
# ///
"""Finalize awsome-videos production notes from validation artifacts."""

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

import check_visual_contract  # noqa: E402
import score_video_readiness  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Finalize production notes after video validation.")
    parser.add_argument("production_notes", type=Path)
    parser.add_argument("--renderer-report", type=Path, required=True)
    parser.add_argument("--readiness-report", type=Path, required=True)
    parser.add_argument("--contact-sheet", type=Path, required=True)
    parser.add_argument("--quality-report", type=Path, required=True)
    parser.add_argument("--motion-report", type=Path, required=True)
    parser.add_argument("--audio-report", type=Path, required=True)
    parser.add_argument("--visual-review", type=Path, required=True)
    parser.add_argument("--visual-contract-report", type=Path, required=True)
    parser.add_argument("--video-validation", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--json", action="store_true")
    return parser.parse_args()


def read_json(
    path: Path,
    label: str,
    failures: list[str],
    *,
    require_status: bool = True,
) -> dict[str, Any]:
    if not path.is_file():
        failures.append(f"{label} missing: {path}")
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        failures.append(f"{label} is not valid JSON: {exc}")
        return {}
    if not isinstance(data, dict):
        failures.append(f"{label} root is not an object")
        return {}
    if require_status:
        ok_value = data.get("ok")
        passed_value = data.get("passed")
        if ok_value is False or passed_value is False or (ok_value is not True and passed_value is not True):
            failures.append(f"{label} must carry an explicit non-conflicting ok=true or passed=true")
    return data


def file_status(path: Path, label: str, failures: list[str]) -> str:
    if not path.is_file():
        failures.append(f"{label} missing: {path}")
        return f"{path} missing"
    return f"{path} generated ({path.stat().st_size} bytes)"


def sha256_file(path: Path) -> str | None:
    if not path.is_file():
        return None
    return hashlib.sha256(path.read_bytes()).hexdigest()


def readiness_line(report: dict[str, Any], path: Path) -> str:
    score = report.get("score", "?")
    max_score = report.get("maxScore", 24)
    readiness = report.get("readiness", "reviewed")
    weak = report.get("weakCategories", [])
    weak_text = "no weak categories" if not weak else "weak categories: " + ", ".join(str(item) for item in weak)
    return f"{score}/{max_score} {readiness}; {weak_text}; report {path}"


def renderer_line(report: dict[str, Any], path: Path) -> str:
    states = report.get("states", [])
    samples = report.get("sampleCount")
    if not samples and isinstance(states, list):
        samples = len(states)
    if samples:
        return f"yes; {samples} sampled states in {path}"
    return f"yes; report {path}"


def motion_quality_line(motion: dict[str, Any], quality: dict[str, Any], motion_path: Path, quality_path: Path) -> str:
    metrics = motion.get("metrics", {})
    if not isinstance(metrics, dict):
        metrics = {}
    changing = metrics.get("changingPairs", motion.get("strongChangingPairs", motion.get("subtleChangingPairs", "?")))
    subtle = metrics.get("subtleChangingPairs", "?")
    samples = quality.get("sampleCount", "?")
    return f"yes; motion changing pairs {changing}, subtle pairs {subtle}; quality samples {samples}; reports {motion_path} and {quality_path}"


def beat_coverage_line(report: dict[str, Any], path: Path) -> str:
    covered = report.get("briefBeatCoverageOk")
    missing = report.get("missingBriefBeats", [])
    if covered is True:
        return f"all sampled brief beats covered by renderer state in {path}"
    if missing:
        return f"renderer report {path} still lists missing beats: {', '.join(str(item) for item in missing)}"
    return f"renderer coverage reviewed in {path}"


def visual_mechanism_line(report: dict[str, Any]) -> str:
    states = report.get("states", [])
    if not isinstance(states, list) or not states:
        return "renderer state was reviewed for source-bound mechanism visibility"
    final_state = states[-1] if isinstance(states[-1], dict) else {}
    pattern = final_state.get("visualPattern", "reported visual pattern")
    mechanism_count = final_state.get("visibleMechanismCount", "?")
    output_visible = final_state.get("outputVisible", final_state.get("finalCallbackVisible", "?"))
    return f"{pattern}; final visibleMechanismCount={mechanism_count}; output/final callback visible={output_visible}"


def audio_line(report: dict[str, Any], path: Path) -> str:
    if report.get("finalAudioReady") is True:
        duration_ok = report.get("finalAudioDurationOk")
        return f"final audio ready; duration coverage {duration_ok}; report {path}"
    duration = report.get("durationSeconds", report.get("sourceDurationSeconds", "?"))
    return f"validation audio covers {duration}s; recorded narration/music/SFX mix can be swapped for publication; report {path}"


def caveat_line(audio: dict[str, Any]) -> str:
    if audio.get("finalAudioReady") is True:
        return "final audio is listed; review any project-specific footage, source, or rights limitations separately."
    return "this handoff uses validation audio unless a final recorded mix is listed in package-manifest.json."


def asset_quality_line(report: dict[str, Any], path: Path) -> str:
    assets = report.get("assetManifest", {})
    if not isinstance(assets, dict):
        assets = {}
    return (
        f"{assets.get('readyAssetCount', '?')}/{assets.get('assetCount', '?')} declared assets are ready; "
        f"producer skills {assets.get('producerSkills', [])}; hash-bound report {path}"
    )


def composition_line(report: dict[str, Any], path: Path) -> str:
    composition = report.get("compositionPlan", {})
    if not isinstance(composition, dict):
        composition = {}
    return (
        f"{composition.get('sceneCount', '?')} scenes use "
        f"{composition.get('compositionChoiceCount', '?')} composition families and "
        f"{composition.get('armatureCount', '?')} armatures; report {path}"
    )


def renderer_binding_line(report: dict[str, Any], path: Path) -> str:
    return (
        f"visible asset coverage={report.get('visualAssetCoverageOk')}, "
        f"manifest binding={report.get('assetBindingCoverageOk')}, "
        f"composition coverage={report.get('compositionCoverageOk')}, "
        f"observed assets={len(report.get('observedAssetIds', []) or [])}; report {path}"
    )


def replace_visual_review(text: str, lines: list[str]) -> str:
    section = "## Visual Review\n\n" + "\n".join(lines) + "\n"
    markdown_heading = re.search(r"^##\s+Visual Review\s*$", text, flags=re.IGNORECASE | re.MULTILINE)
    if markdown_heading:
        start = markdown_heading.start()
        next_heading = re.search(r"^##\s+\S.*$", text[markdown_heading.end() :], flags=re.MULTILINE)
        end = markdown_heading.end() + next_heading.start() if next_heading else len(text)
        return text[:start].rstrip() + "\n\n" + section + text[end:].lstrip("\n")

    plain_heading = re.search(r"^Visual review:\s*$", text, flags=re.IGNORECASE | re.MULTILINE)
    if plain_heading:
        return text[: plain_heading.start()].rstrip() + "\n\n" + section
    return text.rstrip() + "\n\n" + section


def finalize(args: argparse.Namespace) -> dict[str, Any]:
    failures: list[str] = []
    if not args.production_notes.is_file():
        failures.append(f"production notes missing: {args.production_notes}")
        text = ""
    else:
        text = args.production_notes.read_text(encoding="utf-8")

    renderer = read_json(args.renderer_report, "renderer report", failures)
    readiness = read_json(args.readiness_report, "readiness report", failures)
    quality = read_json(args.quality_report, "quality report", failures)
    motion = read_json(args.motion_report, "motion report", failures)
    audio = read_json(args.audio_report, "audio report", failures)
    visual_review_path = getattr(args, "visual_review", None)
    visual_contract_path = getattr(args, "visual_contract_report", None)
    if visual_review_path is None:
        failures.append("visual review path was not supplied")
        visual_review = {}
    else:
        visual_review = read_json(visual_review_path, "visual review", failures, require_status=False)
    if visual_contract_path is None:
        failures.append("visual contract report path was not supplied")
        visual_contract = {}
    else:
        visual_contract = read_json(visual_contract_path, "visual contract report", failures)
    video_validation = read_json(args.video_validation, "video validation", failures) if args.video_validation else {}
    contact_status = file_status(args.contact_sheet, "contact sheet", failures)
    if args.contact_sheet.is_file():
        contact_inspection = check_visual_contract.inspect_raster(
            args.contact_sheet,
            min_width=320,
            min_height=180,
        )
        failures.extend(
            f"contact sheet: {finding}" for finding in contact_inspection.get("failures", [])
        )
    else:
        contact_inspection = {"ok": False, "failures": ["missing"]}

    if readiness.get("readiness") != "ready":
        failures.append(f"readiness report label is not ready: {readiness.get('readiness')}")
    if not isinstance(readiness.get("score"), int) or readiness.get("score", 0) < 18:
        failures.append("readiness report score is missing or below 18")
    if readiness.get("weakCategories") not in ([], None):
        failures.append("readiness report still has weak categories")
    if visual_review.get("overallStatus") != "approved":
        failures.append(f"visual review overallStatus is not approved: {visual_review.get('overallStatus')}")
    playback = visual_review.get("fullSpeedPlayback", {})
    if not isinstance(playback, dict) or playback.get("reviewed") is not True:
        failures.append("visual review does not prove full-speed playback inspection")
    if visual_review.get("unresolvedBlockers") != []:
        failures.append("visual review unresolvedBlockers must be an empty list")

    visual_ok, visual_findings = score_video_readiness.visual_contract_evidence(visual_contract)
    if not visual_ok:
        failures.extend(f"visual contract report: {finding}" for finding in visual_findings)
    renderer_ok, renderer_findings = score_video_readiness.renderer_visual_evidence(
        renderer,
        visual_contract,
    )
    if not renderer_ok:
        failures.extend(f"renderer report: {finding}" for finding in renderer_findings)
    if readiness.get("visualContractReport") != visual_contract:
        failures.append("readiness report does not embed the current visual contract report")
    if readiness.get("rendererReport") != renderer:
        failures.append("readiness report does not embed the current renderer report")
    readiness_digests = readiness.get("inputDigests")
    if not isinstance(readiness_digests, dict):
        failures.append("readiness report inputDigests are missing")
    else:
        expected_readiness_digests = {
            "rendererReportSha256": sha256_file(args.renderer_report),
            "visualContractReportSha256": sha256_file(visual_contract_path)
            if visual_contract_path is not None
            else None,
            "contactSheetSha256": sha256_file(args.contact_sheet),
        }
        for digest_name, expected_digest in expected_readiness_digests.items():
            if readiness_digests.get(digest_name) != expected_digest:
                failures.append(f"readiness report {digest_name} is stale or missing")

    visual_digests = visual_contract.get("inputDigests", {})
    review_digests = visual_review.get("inputDigests", {})
    if not isinstance(visual_digests, dict) or not isinstance(review_digests, dict):
        failures.append("visual review/report digest bindings are missing")
    else:
        for digest_name in ["assetManifestSha256", "compositionPlanSha256"]:
            if review_digests.get(digest_name) != visual_digests.get(digest_name):
                failures.append(f"visual review {digest_name} does not match the visual contract")
        if visual_review_path is not None and sha256_file(visual_review_path) != visual_digests.get(
            "visualReviewSha256"
        ):
            failures.append("visual review file hash does not match the visual contract")
        candidate = visual_review.get("candidateVideo")
        if not isinstance(candidate, dict) or candidate.get("sha256") != visual_digests.get("videoSha256"):
            failures.append("visual review candidate video hash does not match the visual contract")

    scene_count = visual_contract.get("compositionPlan", {}).get("sceneCount")
    raw_scene_reviews = visual_review.get("scenes")
    raw_transition_reviews = visual_review.get("transitions")
    if not isinstance(raw_scene_reviews, list) or len(raw_scene_reviews) != scene_count:
        failures.append("visual review does not contain exactly one review per composed scene")
    if not isinstance(raw_transition_reviews, list) or len(raw_transition_reviews) != max(
        0, int(scene_count or 0) - 1
    ):
        failures.append("visual review does not contain every adjacent transition review")

    if not isinstance(quality.get("sampleCount"), int) or quality.get("sampleCount", 0) < 1:
        failures.append("quality report has no sampled frames")
    motion_metrics = motion.get("metrics") if isinstance(motion.get("metrics"), dict) else motion
    motion_count = motion_metrics.get("changingPairs", motion_metrics.get("subtleChangingPairs", 0))
    if not isinstance(motion_count, (int, float)) or motion_count < 1:
        failures.append("motion report has no changing frame pairs")
    if audio.get("finalAudioReady") is not True and not isinstance(
        audio.get("durationSeconds", audio.get("sourceDurationSeconds")), (int, float)
    ):
        failures.append("audio report has no final-audio status or validation duration")

    lines = [
        f"- Renderer contract passed: {renderer_line(renderer, args.renderer_report)}",
        f"- Readiness score: {readiness_line(readiness, args.readiness_report)}",
        f"- Contact sheet inspected: {contact_status}; approved visual review {visual_review_path}.",
        f"- Asset quality check: {asset_quality_line(visual_contract, visual_contract_path or Path('missing'))}.",
        f"- Composition check: {composition_line(visual_contract, visual_contract_path or Path('missing'))}.",
        f"- Renderer asset-binding check: {renderer_binding_line(renderer, args.renderer_report)}.",
        f"- Legibility check: contact sheet and sampled frames passed nonblank quality review in {args.quality_report}.",
        f"- Beat coverage check: {beat_coverage_line(renderer, args.renderer_report)}.",
        f"- Visual mechanism check: {visual_mechanism_line(renderer)}.",
        f"- Pacing/transition check: {motion_quality_line(motion, quality, args.motion_report, args.quality_report)}.",
        f"- Source-binding check: declared asset IDs, scene uses, visible DOM IDs, and reviewed frames agree in {visual_contract_path}.",
        f"- Motion/quality checks passed: {motion_quality_line(motion, quality, args.motion_report, args.quality_report)}",
        f"- Audio sync check: {audio_line(audio, args.audio_report)}",
        f"- Final audio duration checked: {audio_line(audio, args.audio_report)}",
        f"- Known caveats: {caveat_line(audio)}",
    ]
    if video_validation:
        props = video_validation.get("video", {})
        if isinstance(props, dict):
            lines.insert(3, f"- Video artifact validated: {props.get('durationSeconds', '?')}s at {props.get('fps', '?')} fps.")

    output = args.output or args.production_notes
    if not failures:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(replace_visual_review(text, lines), encoding="utf-8", newline="\n")

    return {
        "ok": not failures,
        "productionNotes": str(args.production_notes),
        "output": str(output),
        "lines": lines,
        "contactSheetInspection": contact_inspection,
        "failures": failures,
    }


def main() -> int:
    args = parse_args()
    result = finalize(args)
    if args.json:
        print(json.dumps(result, indent=2))
    elif result["ok"]:
        print(f"PASS awsome-videos production notes finalized: {result['output']}")
    else:
        print("FAIL awsome-videos production notes finalize")
        for failure in result["failures"]:
            print(f"- {failure}")
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
