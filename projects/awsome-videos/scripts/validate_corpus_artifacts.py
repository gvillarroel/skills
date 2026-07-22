#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Validate the local Awesome/Fireship corpus artifacts against the skill assets."""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from datetime import date
import hashlib
import json
from pathlib import Path
import re
import sys
from typing import Any


sys.dont_write_bytecode = True

DEFAULT_PROJECT = Path(__file__).resolve().parents[1]
DEFAULT_REPO = DEFAULT_PROJECT.parents[1]
DEFAULT_SKILL = DEFAULT_REPO / "skills" / "awsome-videos"

CHANNELS = {
    "Awesome": {
        "source": "awesome",
        "handle": "@awesome-coding",
        "manifest": "awesome-manifest.json",
        "downloadDir": "@awesome-coding",
        "framesDir": "awesome",
    },
    "Fireship": {
        "source": "fireship",
        "handle": "@Fireship",
        "manifest": "fireship-manifest.json",
        "downloadDir": "@Fireship",
        "framesDir": "fireship",
    },
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate local awsome-videos corpus artifacts.")
    parser.add_argument("--project-dir", type=Path, default=DEFAULT_PROJECT)
    parser.add_argument("--skill-dir", type=Path, default=DEFAULT_SKILL)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--json", action="store_true")
    return parser.parse_args()


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def nested_get(data: dict[str, Any], dotted: str) -> Any:
    current: Any = data
    for part in dotted.split("."):
        if not isinstance(current, dict) or part not in current:
            return None
        current = current[part]
    return current


def parse_date(value: Any) -> date | None:
    if not isinstance(value, str):
        return None
    try:
        if re.fullmatch(r"\d{8}", value):
            return date.fromisoformat(f"{value[:4]}-{value[4:6]}-{value[6:8]}")
        return date.fromisoformat(value)
    except ValueError:
        return None


def extract_id(path: Path) -> str | None:
    match = re.match(r"^\d{8}-(.{11})(?:-|\.|$)", path.name)
    return match.group(1) if match else None


def ids_by_extension(root: Path) -> dict[str, set[str]]:
    by_ext: dict[str, set[str]] = defaultdict(set)
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        video_id = extract_id(path)
        if video_id:
            by_ext[path.suffix.lower()].add(video_id)
    return by_ext


def count_files(root: Path, suffix: str) -> int:
    return sum(1 for path in root.rglob(f"*{suffix}") if path.is_file())


def summarize_entries(entries: list[dict[str, Any]]) -> dict[str, Any]:
    channel_counts = Counter(str(entry.get("channel")) for entry in entries)
    availability_counts = Counter(str(entry.get("availability")) for entry in entries)
    ids = [str(entry.get("id")) for entry in entries if isinstance(entry.get("id"), str)]
    return {
        "count": len(entries),
        "channelCounts": dict(sorted(channel_counts.items())),
        "availabilityCounts": dict(sorted(availability_counts.items())),
        "uniqueIds": len(set(ids)),
        "duplicateIds": sorted({video_id for video_id in ids if ids.count(video_id) > 1}),
    }


def skill_sources_info(skill_dir: Path, failures: list[str]) -> dict[str, Any]:
    path = skill_dir / "assets" / "reference" / "corpus-sources.json"
    if not path.exists():
        failures.append(f"skill corpus sources missing: {path}")
        return {"path": str(path), "exists": False}
    data = load_json(path)
    entries = data.get("entries") if isinstance(data, dict) else []
    if not isinstance(entries, list):
        failures.append("skill corpus sources entries is missing or not a list")
        entries = []
    typed_entries = [entry for entry in entries if isinstance(entry, dict)]
    canonical_ids = [f"{entry.get('channel')}:{entry.get('id')}" for entry in typed_entries]
    actual_hash = hashlib.sha256("\n".join(canonical_ids).encode("utf-8")).hexdigest()
    expected_hash = data.get("sourceIdSha256") if isinstance(data, dict) else None
    if actual_hash != expected_hash:
        failures.append(f"sourceIdSha256 mismatch: expected {expected_hash!r}, recomputed {actual_hash!r}")
    summary = summarize_entries(typed_entries)
    if summary["count"] != 181:
        failures.append(f"skill corpus source count expected 181, found {summary['count']}")
    if summary["channelCounts"].get("Awesome") != 105:
        failures.append("skill corpus source Awesome count expected 105")
    if summary["channelCounts"].get("Fireship") != 76:
        failures.append("skill corpus source Fireship count expected 76")
    if summary["availabilityCounts"] != {"public": 181}:
        failures.append(f"skill corpus source availability expected all public, found {summary['availabilityCounts']}")
    if summary["duplicateIds"]:
        failures.append("skill corpus duplicate ids: " + ", ".join(summary["duplicateIds"]))
    start = parse_date(nested_get(data, "analysisWindow.startDate")) if isinstance(data, dict) else None
    end = parse_date(nested_get(data, "analysisWindow.endDate")) if isinstance(data, dict) else None
    if start != date(2025, 7, 6) or end != date(2026, 7, 6):
        failures.append("skill corpus analysis window must be 2025-07-06 through 2026-07-06")
    out_of_window = [
        str(entry.get("id"))
        for entry in typed_entries
        if (upload := parse_date(entry.get("uploadDate"))) is None or start is None or end is None or not (start <= upload <= end)
    ]
    if out_of_window:
        failures.append("skill corpus entries outside window: " + ", ".join(out_of_window[:20]))
    return {
        "path": str(path),
        "exists": True,
        **summary,
        "sourceIdSha256": actual_hash,
        "analysisWindow": {"start": str(start), "end": str(end)},
        "entries": typed_entries,
    }


def skill_summary_info(skill_dir: Path, failures: list[str]) -> dict[str, Any]:
    path = skill_dir / "assets" / "reference" / "corpus-summary.json"
    if not path.exists():
        failures.append(f"skill corpus summary missing: {path}")
        return {"path": str(path), "exists": False}
    data = load_json(path)
    expected_values = {
        "scope.totalPublicVideos": 181,
        "sourceManifest.totalEntries": 181,
        "artifactCounts.localLowResolutionMp4": 181,
        "artifactCounts.thumbnails": 181,
        "artifactCounts.englishVttFiles": 528,
        "representativeExamples.count": 8,
        "audioProfile.representativeExamples": 8,
        "audioProfile.nearContinuousAudio": True,
    }
    mismatches: dict[str, dict[str, Any]] = {}
    for dotted, expected in expected_values.items():
        actual = nested_get(data, dotted)
        if actual != expected:
            mismatches[dotted] = {"expected": expected, "actual": actual}
    if mismatches:
        failures.append("skill corpus summary mismatches: " + ", ".join(mismatches))
    return {
        "path": str(path),
        "exists": True,
        "mismatches": mismatches,
        "artifactCounts": data.get("artifactCounts") if isinstance(data, dict) else None,
        "audioProfile": data.get("audioProfile") if isinstance(data, dict) else None,
    }


def local_manifest_info(project_dir: Path, skill_entries: list[dict[str, Any]], failures: list[str]) -> dict[str, Any]:
    metadata_dir = project_dir / "artifacts" / "metadata"
    downloads_dir = project_dir / "artifacts" / "downloads"
    info: dict[str, Any] = {}
    skill_ids_by_channel = {
        channel: {str(entry.get("id")) for entry in skill_entries if entry.get("channel") == channel}
        for channel in CHANNELS
    }
    for channel, config in CHANNELS.items():
        manifest_path = metadata_dir / str(config["manifest"])
        if not manifest_path.exists():
            failures.append(f"local manifest missing for {channel}: {manifest_path}")
            info[channel] = {"manifest": str(manifest_path), "exists": False}
            continue
        entries = load_json(manifest_path)
        if not isinstance(entries, list):
            failures.append(f"local manifest for {channel} is not a list")
            entries = []
        typed_entries = [entry for entry in entries if isinstance(entry, dict)]
        local_ids = {str(entry.get("id")) for entry in typed_entries if isinstance(entry.get("id"), str)}
        expected_ids = skill_ids_by_channel[channel]
        missing_from_local = sorted(expected_ids - local_ids)
        extra_local = sorted(local_ids - expected_ids)
        if missing_from_local:
            failures.append(f"{channel} local manifest missing skill ids: " + ", ".join(missing_from_local[:20]))
        if extra_local:
            failures.append(f"{channel} local manifest has ids not in skill sources: " + ", ".join(extra_local[:20]))
        bad_availability = [str(entry.get("id")) for entry in typed_entries if entry.get("availability") != "public"]
        if bad_availability:
            failures.append(f"{channel} local manifest non-public entries: " + ", ".join(bad_availability[:20]))
        bad_window = [
            str(entry.get("id"))
            for entry in typed_entries
            if (upload := parse_date(entry.get("upload_date"))) is None
            or not (date(2025, 7, 6) <= upload <= date(2026, 7, 6))
        ]
        if bad_window:
            failures.append(f"{channel} local manifest entries outside window: " + ", ".join(bad_window[:20]))

        download_root = downloads_dir / str(config["downloadDir"])
        ids_by_ext = ids_by_extension(download_root)
        missing_mp4 = sorted(expected_ids - ids_by_ext.get(".mp4", set()))
        missing_jpg = sorted(expected_ids - ids_by_ext.get(".jpg", set()))
        missing_vtt = sorted(expected_ids - ids_by_ext.get(".vtt", set()))
        if missing_mp4:
            failures.append(f"{channel} missing MP4 ids: " + ", ".join(missing_mp4[:20]))
        if missing_jpg:
            failures.append(f"{channel} missing thumbnail ids: " + ", ".join(missing_jpg[:20]))
        if missing_vtt:
            failures.append(f"{channel} missing VTT ids: " + ", ".join(missing_vtt[:20]))

        info[channel] = {
            "manifest": str(manifest_path),
            "manifestCount": len(typed_entries),
            "expectedSkillIds": len(expected_ids),
            "missingFromLocalManifest": missing_from_local,
            "extraLocalManifestIds": extra_local,
            "downloadDir": str(download_root),
            "mp4Files": count_files(download_root, ".mp4"),
            "jpgFiles": count_files(download_root, ".jpg"),
            "vttFiles": count_files(download_root, ".vtt"),
            "mp4Ids": len(ids_by_ext.get(".mp4", set())),
            "jpgIds": len(ids_by_ext.get(".jpg", set())),
            "vttIds": len(ids_by_ext.get(".vtt", set())),
            "missingMp4Ids": missing_mp4,
            "missingThumbnailIds": missing_jpg,
            "missingVttIds": missing_vtt,
        }
    return info


def processing_info(project_dir: Path, failures: list[str]) -> dict[str, Any]:
    repo_dir = project_dir.parents[1]
    reports_dir = project_dir / "artifacts" / "reports"
    frames_dir = project_dir / "artifacts" / "frames"
    analysis_path = reports_dir / "corpus-analysis.json"
    representative_path = reports_dir / "representative-examples.json"
    audio_path = reports_dir / "audio-silence-representative.json"
    contact_sheet = frames_dir / "contact-sheets" / "representative-examples.jpg"
    info: dict[str, Any] = {}

    if not analysis_path.exists():
        failures.append(f"corpus analysis missing: {analysis_path}")
    else:
        analysis = load_json(analysis_path)
        if not isinstance(analysis, list):
            failures.append("corpus analysis root is not a list")
            analysis = []
        classification_count = sum(1 for item in analysis if isinstance(item, dict) and item.get("classification"))
        visual_metrics_count = sum(1 for item in analysis if isinstance(item, dict) and item.get("visual_metrics"))
        transcript_count = sum(1 for item in analysis if isinstance(item, dict) and item.get("transcript"))
        if len(analysis) != 181:
            failures.append(f"corpus analysis expected 181 rows, found {len(analysis)}")
        if classification_count != 181:
            failures.append(f"corpus analysis classifications expected 181, found {classification_count}")
        if visual_metrics_count != 181:
            failures.append(f"corpus analysis visual metrics expected 181, found {visual_metrics_count}")
        if transcript_count != 181:
            failures.append(f"corpus analysis transcripts expected 181, found {transcript_count}")
        info["analysis"] = {
            "path": str(analysis_path),
            "rows": len(analysis),
            "classificationRows": classification_count,
            "visualMetricRows": visual_metrics_count,
            "transcriptRows": transcript_count,
        }

    if not representative_path.exists():
        failures.append(f"representative examples missing: {representative_path}")
    else:
        representatives = load_json(representative_path)
        if not isinstance(representatives, list):
            failures.append("representative examples root is not a list")
            representatives = []
        source_counts = Counter(str(item.get("source")) for item in representatives if isinstance(item, dict))
        missing_paths: list[str] = []
        for item in representatives:
            if not isinstance(item, dict):
                continue
            for key in ["video_path", "thumbnail_path", "vtt_path", "example_frame_dir"]:
                raw = item.get(key)
                if isinstance(raw, str) and not (repo_dir / raw).exists() and not Path(raw).exists():
                    missing_paths.append(f"{item.get('id')}:{key}")
        if len(representatives) != 8:
            failures.append(f"representative examples expected 8, found {len(representatives)}")
        if source_counts.get("awesome") != 4 or source_counts.get("fireship") != 4:
            failures.append(f"representative examples expected 4 per source, found {dict(source_counts)}")
        if missing_paths:
            failures.append("representative examples missing referenced paths: " + ", ".join(missing_paths[:20]))
        info["representativeExamples"] = {
            "path": str(representative_path),
            "count": len(representatives),
            "sourceCounts": dict(source_counts),
            "missingReferencedPaths": missing_paths,
        }

    if not audio_path.exists():
        failures.append(f"audio silence report missing: {audio_path}")
    else:
        audio = load_json(audio_path)
        if not isinstance(audio, list):
            failures.append("audio silence report root is not a list")
            audio = []
        source_counts = Counter(str(item.get("source")) for item in audio if isinstance(item, dict))
        if len(audio) != 8:
            failures.append(f"audio silence report expected 8 rows, found {len(audio)}")
        if source_counts.get("awesome") != 4 or source_counts.get("fireship") != 4:
            failures.append(f"audio silence report expected 4 per source, found {dict(source_counts)}")
        info["audioSilence"] = {
            "path": str(audio_path),
            "count": len(audio),
            "sourceCounts": dict(source_counts),
        }

    frame_dirs = [path for path in (frames_dir / "awesome").glob("*") if path.is_dir()] + [
        path for path in (frames_dir / "fireship").glob("*") if path.is_dir()
    ]
    frame_jpg_count = count_files(frames_dir, ".jpg")
    if len(frame_dirs) < 8:
        failures.append(f"expected at least 8 representative frame directories, found {len(frame_dirs)}")
    if frame_jpg_count < 49:
        failures.append(f"expected at least 49 frame/contact-sheet JPG files, found {frame_jpg_count}")
    if not contact_sheet.exists() or contact_sheet.stat().st_size < 10000:
        failures.append(f"representative contact sheet missing or too small: {contact_sheet}")
    info["frames"] = {
        "frameDirectories": len(frame_dirs),
        "jpgFiles": frame_jpg_count,
        "contactSheet": str(contact_sheet),
        "contactSheetBytes": contact_sheet.stat().st_size if contact_sheet.exists() else 0,
    }
    return info


def build_result(project_dir: Path, skill_dir: Path) -> dict[str, Any]:
    failures: list[str] = []
    warnings: list[str] = []
    skill_sources = skill_sources_info(skill_dir, failures)
    skill_summary = skill_summary_info(skill_dir, failures)
    skill_entries = skill_sources.get("entries", []) if isinstance(skill_sources.get("entries"), list) else []
    local_manifests = local_manifest_info(project_dir, skill_entries, failures)
    processing = processing_info(project_dir, failures)

    total_mp4 = sum(int(info.get("mp4Files", 0)) for info in local_manifests.values() if isinstance(info, dict))
    total_jpg = sum(int(info.get("jpgFiles", 0)) for info in local_manifests.values() if isinstance(info, dict))
    total_vtt = sum(int(info.get("vttFiles", 0)) for info in local_manifests.values() if isinstance(info, dict))
    if total_mp4 != 181:
        failures.append(f"downloaded MP4 count expected 181, found {total_mp4}")
    if total_jpg != 181:
        failures.append(f"downloaded thumbnail JPG count expected 181, found {total_jpg}")
    if total_vtt != 528:
        failures.append(f"downloaded VTT count expected 528, found {total_vtt}")

    return {
        "ok": not failures,
        "projectDir": str(project_dir),
        "skillDir": str(skill_dir),
        "totals": {
            "downloadedMp4": total_mp4,
            "downloadedThumbnails": total_jpg,
            "downloadedVtt": total_vtt,
        },
        "skillSources": {key: value for key, value in skill_sources.items() if key != "entries"},
        "skillSummary": skill_summary,
        "localManifests": local_manifests,
        "processing": processing,
        "failures": failures,
        "warnings": warnings,
    }


def main() -> int:
    args = parse_args()
    result = build_result(args.project_dir, args.skill_dir)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8", newline="\n")
    if args.json:
        print(json.dumps(result, indent=2))
    elif result["ok"]:
        totals = result["totals"]
        print(
            "PASS awsome-videos corpus artifacts: "
            f"{totals['downloadedMp4']} MP4, {totals['downloadedThumbnails']} thumbnails, "
            f"{totals['downloadedVtt']} VTT files"
        )
    else:
        print("FAIL awsome-videos corpus artifacts")
        for failure in result["failures"]:
            print(f"- {failure}")
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
