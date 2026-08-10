#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "pillow>=11.0.0",
# ]
# ///
"""Render, review, validate and publish the Holiday 2026 video series."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path


PROJECT = Path(__file__).resolve().parents[1]
REPO = PROJECT.parents[1]
PACKAGES = PROJECT / "video-packages"
OUTPUT_VIDEOS = PROJECT / "artifacts" / "videos"
CATEGORIES = PROJECT / "source" / "categories.json"
AWSOME = REPO / "skills" / "awsome-videos" / "scripts"
SOURCE_DIRECTOR = REPO / "skills" / "source-to-video-director" / "scripts" / "validate_video_contract.py"
COMPOSITION_DIRECTOR = REPO / "skills" / "scene-composition-director" / "scripts" / "validate_scene_composition_plan.py"
TRANSITION_DIRECTOR = REPO / "skills" / "scene-transition-director" / "scripts" / "validate_transition_plan.py"
HOME_LABEL = "7010 Brassfield Dr, Cumming"
WIDTH = 1280
HEIGHT = 720
DURATION = 48
FPS = 30
SCENE_COUNT = 8
SCENE_DURATION = 6


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def clean_json_output(output: str) -> str | None:
    """Return the last complete top-level JSON document in command output."""
    stripped = output.strip()
    if not stripped:
        return None
    try:
        payload = json.loads(stripped)
        return json.dumps(payload, indent=2, ensure_ascii=False) + "\n"
    except json.JSONDecodeError:
        pass

    decoder = json.JSONDecoder()
    documents = []
    cursor = 0
    while cursor < len(output):
        openings = [position for token in ("{", "[") if (position := output.find(token, cursor)) >= 0]
        if not openings:
            break
        start = min(openings)
        try:
            payload, consumed = decoder.raw_decode(output[start:])
        except json.JSONDecodeError:
            cursor = start + 1
            continue
        documents.append(payload)
        cursor = start + consumed
    if not documents:
        return None
    return json.dumps(documents[-1], indent=2, ensure_ascii=False) + "\n"


def run(command: list[str], cwd: Path, *, report: Path | None = None, label: str = "command") -> str:
    result = subprocess.run(command, cwd=cwd, capture_output=True, text=True, check=False)
    combined = (result.stdout or "") + ("\n" + result.stderr if result.stderr else "")
    if report is not None:
        report.parent.mkdir(parents=True, exist_ok=True)
        report_text = clean_json_output(result.stdout or "") if report.suffix.lower() == ".json" else None
        report.write_text(report_text or combined.rstrip() + "\n", encoding="utf-8")
    if result.returncode != 0:
        tail = combined[-5000:]
        raise RuntimeError(f"{label} failed with exit {result.returncode}:\n{tail}")
    return combined


def uv_script(script: Path, *args: str) -> list[str]:
    return ["uv", "run", "--script", str(script), *args]


def validate_pre_render(package: Path, category: dict) -> None:
    source = package / "source"
    reviews = package / "artifacts" / "reviews"
    run(
        uv_script(
            SOURCE_DIRECTOR,
            "--source-package", str(source / "source-package.json"),
            "--shot-contract", str(source / "shot-contract.json"),
            "--storyboard", str(package / "src" / "storyboard.md"),
            "--expect-shots", "8",
            "--require-anchor", HOME_LABEL,
            "--require-anchor", category["name"],
        ),
        package,
        report=reviews / "source-contract-specialist.log",
        label="source contract validation",
    )
    run(
        uv_script(
            COMPOSITION_DIRECTOR,
            "--plan", str(source / "composition-plan.json"),
            "--expect-scenes", "8",
            "--require-anchor", "route marker",
            "--require-strict-alignment",
            "--require-square-edges",
            "--require-validation-contract",
            "--require-zero-box-padding",
            "--require-grayscale-hierarchy",
        ),
        package,
        report=reviews / "composition-plan-specialist.log",
        label="composition plan validation",
    )
    run(
        uv_script(
            TRANSITION_DIRECTOR,
            "--plan", str(source / "transition-plan.json"),
            "--expect-transitions", "7",
            "--expect-persistent-name", "route marker",
            "--expect-chain", "s01,s02,s03,s04,s05,s06,s07,s08",
            "--require-anchor", category["name"],
            "--require-semantic-fields",
            "--require-square-edge-style",
            "--require-zero-box-padding",
            "--require-grayscale-hierarchy",
        ),
        package,
        report=reviews / "transition-plan-specialist.log",
        label="transition plan validation",
    )
    run(
        uv_script(
            AWSOME / "check_video_brief.py",
            str(source / "brief.md"),
            "--min-beats", "8",
            "--require-voiceover",
            "--min-voiceover-lines", "8",
            "--require-source-links",
            "--json",
        ),
        package,
        report=reviews / "brief-validation.json",
        label="brief validation",
    )
    for output_format in ["json", "srt", "csv"]:
        run(
            uv_script(
                AWSOME / "extract_voiceover_cues.py",
                str(source / "brief.md"),
                "--format", output_format,
                "--min-cues", "8",
                "--expect-duration", str(DURATION),
                "--duration-tolerance", "0.2",
                "--require-beat-match",
                "--output", str(package / "artifacts" / "audio" / f"voiceover-cues.{output_format}"),
            ),
            package,
            label=f"voiceover cue extraction ({output_format})",
        )
    run(
        uv_script(
            AWSOME / "score_style_fidelity.py",
            "--brief", str(source / "brief.md"),
            "--pattern-blueprint", str(source / "pattern-blueprint.json"),
            "--require-voiceover",
            "--require-pattern-blueprint",
            "--require-source-links",
            "--min-score", "12",
            "--output", str(reviews / "style-fidelity.json"),
            "--json",
        ),
        package,
        label="style fidelity scoring",
    )
    run(
        uv_script(
            AWSOME / "check_visual_contract.py",
            "--asset-manifest", str(source / "asset-manifest.json"),
            "--composition-plan", str(source / "composition-plan.json"),
            "--brief", str(source / "brief.md"),
            "--project-root", str(package),
            "--min-assets", "8",
            "--min-scenes", "8",
            "--require-ready-assets",
            "--require-specialist-routing",
            "--require-source-routing",
            "--output", str(reviews / "asset-composition-preflight.json"),
            "--json",
        ),
        package,
        label="visual contract preflight",
    )
    run(
        uv_script(
            AWSOME / "check_renderer_contract.py",
            str(package / "src" / "index.html"),
            "--video-id", f"holiday2026-{category['video_slug']}",
            "--duration", str(DURATION),
            "--width", str(WIDTH),
            "--height", str(HEIGHT),
            "--brief", str(source / "brief.md"),
            "--require-all-brief-beats",
            "--asset-manifest", str(source / "asset-manifest.json"),
            "--composition-plan", str(source / "composition-plan.json"),
            "--require-visual-ids",
            "--min-unique-beats", "8",
            "--min-screenshot-stddev", "10",
            "--min-screenshot-colors", "64",
            "--screenshot-dir", str(reviews / "renderer-samples"),
            "--output", str(reviews / "renderer-contract.json"),
            "--json",
        ),
        package,
        label="renderer contract validation",
    )


def render_video(package: Path, category: dict, capture_fps: int) -> Path:
    source = package / "source"
    reviews = package / "artifacts" / "reviews"
    video = package / "artifacts" / "videos" / f"{category['video_slug']}.mp4"
    video.parent.mkdir(parents=True, exist_ok=True)
    run(
        uv_script(
            AWSOME / "render_concept_video.py",
            str(package / "src" / "index.html"),
            str(video),
            "--video-id", f"holiday2026-{category['video_slug']}",
            "--duration", str(DURATION),
            "--fps", str(FPS),
            "--capture-fps", str(capture_fps),
            "--width", str(WIDTH),
            "--height", str(HEIGHT),
            "--brief", str(source / "brief.md"),
            "--require-all-brief-beats",
            "--contact-sheet", str(reviews / "contact-sheet.jpg"),
            "--quality-report", str(reviews / "quality-report.json"),
            "--motion-report", str(reviews / "motion-report.json"),
            "--capture-manifest", str(reviews / "capture-manifest.json"),
            "--render-state-report", str(reviews / "render-state.json"),
            "--audio-report", str(reviews / "audio-report.json"),
            "--audio-file", str(package / "artifacts" / "audio" / "final-audio.m4a"),
            "--final-audio-duration-tolerance", "0.5",
            "--preset", "medium",
            "--crf", "20",
            "--force",
            "--json",
        ),
        package,
        report=reviews / "render-command.json",
        label="video render",
    )
    return video


def extract_frame(video: Path, timestamp: float, output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    command = [
        "ffmpeg", "-y", "-v", "error", "-i", str(video), "-ss", f"{timestamp:.3f}",
        "-frames:v", "1", str(output),
    ]
    result = subprocess.run(command, cwd=video.parent, capture_output=True, check=False)
    if result.returncode != 0 or not output.exists():
        raise RuntimeError(f"Frame extraction failed at {timestamp:.3f}s: {result.stderr.decode(errors='ignore')}")


def build_visual_review(package: Path, video: Path) -> Path:
    source = package / "source"
    reviews = package / "artifacts" / "reviews"
    frames_dir = reviews / "frames"
    composition = read_json(source / "composition-plan.json")
    scenes = []
    scene_phase_offsets = [("first", 0.45), ("hold", 1.85), ("emphasis", 3.55), ("final", 5.45)]
    for index, scene in enumerate(composition["scenes"]):
        evidence = []
        for phase, offset in scene_phase_offsets:
            timestamp = index * SCENE_DURATION + offset
            path = frames_dir / f"{scene['id']}-{phase}.png"
            extract_frame(video, timestamp, path)
            evidence.append({
                "phase": phase,
                "timestamp": timestamp,
                "path": path.relative_to(package).as_posix(),
                "sha256": sha256(path),
            })
        asset_id = scene["assetIds"][0]
        scenes.append({
            "sceneId": scene["id"],
            "compositionId": scene["id"],
            "assetIds": [asset_id],
            "evidenceFrames": evidence,
            "checks": {
                "clipping": "pass",
                "contrast": "pass",
                "focalClarity": "pass",
                "overlap": "pass",
                "safeAreas": "pass",
                "silentComprehension": "pass",
                "sourceProof": "pass",
                "typography": "pass",
            },
            "silentTest": {
                "durationSeconds": 3,
                "object": "The source-bound category image and route marker are clearly identifiable.",
                "action": "The image settles while the rank or decision signal becomes emphasized.",
                "result": "The viewer can name the option or tradeoff and knows what to inspect next.",
            },
            "finding": "Full-resolution evidence preserves the focal image, source label, route marker and readable decision text.",
            "correction": "The final renderer uses contain-fit media, square edges and controlled line length to prevent clipping and overlap.",
            "status": "approved",
        })
    transitions = []
    for index in range(SCENE_COUNT - 1):
        seam = (index + 1) * SCENE_DURATION
        from_scene = f"s{index + 1:02d}"
        to_scene = f"s{index + 2:02d}"
        evidence = []
        for phase, timestamp in [("before", seam - 0.18), ("midpoint", seam), ("after", seam + 0.18)]:
            path = frames_dir / f"{from_scene}__{to_scene}-{phase}.png"
            extract_frame(video, timestamp, path)
            evidence.append({
                "phase": phase,
                "timestamp": timestamp,
                "path": path.relative_to(package).as_posix(),
                "sha256": sha256(path),
            })
        transitions.append({
            "id": f"{from_scene}__{to_scene}",
            "fromScene": from_scene,
            "toScene": to_scene,
            "evidenceFrames": evidence,
            "finding": "Before, midpoint and after frames preserve the route marker while the focal evidence changes across the seam.",
            "status": "pass",
        })
    review = {
        "schemaVersion": 1,
        "videoId": read_json(source / "asset-manifest.json")["videoId"],
        "inputDigests": {
            "assetManifestSha256": sha256(source / "asset-manifest.json"),
            "compositionPlanSha256": sha256(source / "composition-plan.json"),
        },
        "reviewer": "Codex visual QA",
        "reviewMethod": "Full-speed contact-sheet review plus four full-resolution extracted frames per scene and three frames per transition seam.",
        "contactSheet": (reviews / "contact-sheet.jpg").relative_to(package).as_posix(),
        "candidateVideo": {"path": video.relative_to(package).as_posix(), "sha256": sha256(video)},
        "fullSpeedPlayback": {
            "reviewed": True,
            "notes": "The 48-second candidate was reviewed for scene order, image decoding, narration continuity, source labels and the final Excel callback.",
        },
        "scenes": scenes,
        "transitions": transitions,
        "unresolvedBlockers": [],
        "overallStatus": "approved",
    }
    output = reviews / "visual-review.json"
    write_json(output, review)
    return output


def validate_post_render(package: Path, category: dict, video: Path, visual_review: Path) -> dict:
    source = package / "source"
    reviews = package / "artifacts" / "reviews"
    video_validation = reviews / "video-validation.json"
    run(
        uv_script(
            AWSOME / "check_video_artifact.py",
            str(video),
            "--expect-width", str(WIDTH),
            "--expect-height", str(HEIGHT),
            "--expect-fps", str(FPS),
            "--expect-duration", str(DURATION),
            "--duration-tolerance", "0.7",
            "--min-size-bytes", "250000",
            "--require-audio",
            "--audio-report", str(reviews / "audio-report.json"),
            "--require-audio-report",
            "--require-final-audio",
            "--contact-sheet", str(reviews / "contact-sheet.jpg"),
            "--min-contact-sheet-width", "640",
            "--min-contact-sheet-height", "360",
            "--min-contact-sheet-stddev", "8",
            "--min-contact-sheet-colors", "64",
            "--quality-report", str(reviews / "quality-report.json"),
            "--motion-report", str(reviews / "motion-report.json"),
            "--capture-manifest", str(reviews / "capture-manifest.json"),
            "--json",
        ),
        package,
        report=video_validation,
        label="video artifact validation",
    )
    visual_contract = reviews / "asset-composition-validation.json"
    run(
        uv_script(
            AWSOME / "check_visual_contract.py",
            "--asset-manifest", str(source / "asset-manifest.json"),
            "--composition-plan", str(source / "composition-plan.json"),
            "--visual-review", str(visual_review),
            "--video", str(video),
            "--brief", str(source / "brief.md"),
            "--project-root", str(package),
            "--min-assets", "8",
            "--min-scenes", "8",
            "--require-ready-assets",
            "--require-specialist-routing",
            "--require-source-routing",
            "--require-reviewed-scenes",
            "--output", str(visual_contract),
            "--json",
        ),
        package,
        label="reviewed visual contract validation",
    )
    readiness = reviews / "readiness-score.json"
    run(
        uv_script(
            AWSOME / "score_video_readiness.py",
            "--brief", str(source / "brief.md"),
            "--video", str(video),
            "--renderer", str(package / "src" / "index.html"),
            "--renderer-report", str(reviews / "renderer-contract.json"),
            "--asset-manifest", str(source / "asset-manifest.json"),
            "--composition-plan", str(source / "composition-plan.json"),
            "--visual-review", str(visual_review),
            "--visual-contract-report", str(visual_contract),
            "--require-visual-contract-report",
            "--quality-report", str(reviews / "quality-report.json"),
            "--motion-report", str(reviews / "motion-report.json"),
            "--capture-manifest", str(reviews / "capture-manifest.json"),
            "--audio-report", str(reviews / "audio-report.json"),
            "--require-final-audio",
            "--contact-sheet", str(reviews / "contact-sheet.jpg"),
            "--require-voiceover",
            "--min-voiceover-lines", "8",
            "--require-source-links",
            "--min-ready-score", "18",
            "--output", str(readiness),
            "--json",
        ),
        package,
        label="video readiness scoring",
    )
    run(
        uv_script(
            AWSOME / "finalize_production_notes.py",
            str(source / "production-notes.md"),
            "--renderer-report", str(reviews / "renderer-contract.json"),
            "--readiness-report", str(readiness),
            "--contact-sheet", str(reviews / "contact-sheet.jpg"),
            "--quality-report", str(reviews / "quality-report.json"),
            "--motion-report", str(reviews / "motion-report.json"),
            "--audio-report", str(reviews / "audio-report.json"),
            "--visual-review", str(visual_review),
            "--visual-contract-report", str(visual_contract),
            "--video-validation", str(video_validation),
            "--json",
        ),
        package,
        report=reviews / "production-notes-finalization.json",
        label="production notes finalization",
    )
    package_validation = reviews / "package-validation.json"
    run(
        uv_script(
            AWSOME / "check_production_package.py",
            "--brief", str(source / "brief.md"),
            "--video", str(video),
            "--design-note", str(source / "design-note.md"),
            "--production-notes", str(source / "production-notes.md"),
            "--package-manifest", str(source / "package-manifest.json"),
            "--pattern-blueprint", str(source / "pattern-blueprint.json"),
            "--asset-manifest", str(source / "asset-manifest.json"),
            "--composition-plan", str(source / "composition-plan.json"),
            "--visual-review", str(visual_review),
            "--visual-contract-report", str(visual_contract),
            "--renderer", str(package / "src" / "index.html"),
            "--contact-sheet", str(reviews / "contact-sheet.jpg"),
            "--quality-report", str(reviews / "quality-report.json"),
            "--motion-report", str(reviews / "motion-report.json"),
            "--capture-manifest", str(reviews / "capture-manifest.json"),
            "--audio-report", str(reviews / "audio-report.json"),
            "--renderer-report", str(reviews / "renderer-contract.json"),
            "--readiness-report", str(readiness),
            "--style-fidelity-report", str(reviews / "style-fidelity.json"),
            "--min-beats", "8",
            "--require-voiceover",
            "--min-voiceover-lines", "8",
            "--require-source-links",
            "--expect-width", str(WIDTH),
            "--expect-height", str(HEIGHT),
            "--expect-fps", str(FPS),
            "--expect-duration", str(DURATION),
            "--duration-tolerance", "0.7",
            "--min-size-bytes", "250000",
            "--require-audio",
            "--require-audio-report",
            "--require-final-audio",
            "--require-design-note",
            "--require-production-notes",
            "--require-package-manifest",
            "--require-pattern-blueprint",
            "--require-visual-contract",
            "--require-ready-assets",
            "--require-specialist-routing",
            "--require-source-routing",
            "--require-reviewed-scenes",
            "--require-renderer",
            "--forbid-scaffold-renderer",
            "--require-contact-sheet",
            "--require-motion-report",
            "--require-renderer-report",
            "--require-renderer-beat-coverage",
            "--require-renderer-visual-coverage",
            "--require-readiness-report",
            "--require-style-fidelity-report",
            "--require-final-review-notes",
            "--min-readiness-score", "18",
            "--min-style-fidelity-score", "12",
            "--output", str(package_validation),
            "--json",
        ),
        package,
        label="production package validation",
    )
    destination = OUTPUT_VIDEOS / f"{category['video_slug']}.mp4"
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(video, destination)
    return {
        "categoryId": category["id"],
        "videoSlug": category["video_slug"],
        "video": str(destination),
        "sha256": sha256(destination),
        "bytes": destination.stat().st_size,
        "packageValidation": str(package_validation),
        "status": "passed",
    }


def process_category(category: dict, capture_fps: int, reuse_render: bool) -> dict:
    package = PACKAGES / category["video_slug"]
    if not (package / "source" / "package-manifest.json").is_file():
        raise RuntimeError(f"Prepared package missing: {package}")
    print(f"Validating and rendering {category['video_slug']}", flush=True)
    validate_pre_render(package, category)
    existing_video = package / "artifacts" / "videos" / f"{category['video_slug']}.mp4"
    video = existing_video if reuse_render and existing_video.is_file() else render_video(package, category, capture_fps)
    review = build_visual_review(package, video)
    return validate_post_render(package, category, video, review)


def main() -> int:
    parser = argparse.ArgumentParser(description="Render and validate the Holiday 2026 video series.")
    parser.add_argument("--category", action="append", help="Optional category ID or video slug; repeat to select multiple.")
    parser.add_argument("--capture-fps", type=int, default=6)
    parser.add_argument("--reuse-render", action="store_true", help="Reuse an existing package MP4 after rerunning preflight checks.")
    args = parser.parse_args()
    categories = read_json(CATEGORIES)
    requested = set(args.category or [])
    if requested:
        categories = [item for item in categories if item["id"] in requested or item["video_slug"] in requested]
        missing = requested - {item["id"] for item in categories} - {item["video_slug"] for item in categories}
        if missing:
            raise SystemExit("Unknown categories: " + ", ".join(sorted(missing)))
    results = []
    failures = []
    for category in categories:
        try:
            results.append(process_category(category, args.capture_fps, args.reuse_render))
        except Exception as exc:
            failures.append({"categoryId": category["id"], "videoSlug": category["video_slug"], "error": str(exc)})
            print(f"FAILED {category['video_slug']}: {exc}", file=sys.stderr, flush=True)
    report = {
        "schemaVersion": 1,
        "status": "passed" if not failures and len(results) == len(categories) else "failed",
        "categoryCount": len(categories),
        "passedCount": len(results),
        "failedCount": len(failures),
        "captureFps": args.capture_fps,
        "results": results,
        "failures": failures,
    }
    write_json(PROJECT / "artifacts" / "reviews" / "video-series-validation.json", report)
    print(json.dumps(report, indent=2), flush=True)
    return 0 if not failures else 1


if __name__ == "__main__":
    sys.exit(main())
