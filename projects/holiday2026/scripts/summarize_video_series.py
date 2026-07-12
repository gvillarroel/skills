#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Build the authoritative Holiday 2026 video-series delivery report."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def ffprobe(path: Path) -> dict:
    result = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration,size:stream=index,codec_type,codec_name,width,height,r_frame_rate,sample_rate,channels,bit_rate",
            "-of",
            "json",
            str(path),
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode:
        return {"ok": False, "error": result.stderr.strip()}
    payload = json.loads(result.stdout)
    streams = payload.get("streams", [])
    video = next((item for item in streams if item.get("codec_type") == "video"), {})
    audio = next((item for item in streams if item.get("codec_type") == "audio"), {})
    rate = video.get("r_frame_rate", "0/1")
    numerator, denominator = (float(value) for value in rate.split("/", 1))
    fps = numerator / denominator if denominator else 0.0
    return {
        "ok": True,
        "durationSeconds": float(payload.get("format", {}).get("duration", 0)),
        "sizeBytes": int(payload.get("format", {}).get("size", 0)),
        "width": int(video.get("width", 0)),
        "height": int(video.get("height", 0)),
        "fps": fps,
        "videoCodec": video.get("codec_name"),
        "audioCodec": audio.get("codec_name"),
        "audioSampleRate": int(audio.get("sample_rate", 0) or 0),
        "audioChannels": int(audio.get("channels", 0) or 0),
        "audioBitRate": int(audio.get("bit_rate", 0) or 0),
        "hasVideo": bool(video),
        "hasAudio": bool(audio),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--project-root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
    )
    args = parser.parse_args()
    root = args.project_root.resolve()
    output = (
        args.output.resolve()
        if args.output
        else root / "artifacts" / "reviews" / "video-series-final-validation.json"
    )

    categories = json.loads((root / "source" / "categories.json").read_text(encoding="utf-8"))
    ranked = json.loads((root / "artifacts" / "data" / "ranked-places.json").read_text(encoding="utf-8"))
    selected_counts: dict[str, int] = {}
    ranked_by_category: dict[str, list[dict]] = {}
    for item in ranked:
        selected_counts[item["category_id"]] = selected_counts.get(item["category_id"], 0) + 1
        if item.get("selected"):
            ranked_by_category.setdefault(item["category_id"], []).append(item)
    for items in ranked_by_category.values():
        items.sort(key=lambda item: int(item.get("rank") or 9999))

    failures: list[str] = []
    rows: list[dict] = []
    for category in categories:
        slug = category["video_slug"]
        package_root = root / "video-packages" / slug
        package_report_path = package_root / "artifacts" / "reviews" / "package-validation.json"
        package_video = package_root / "artifacts" / "videos" / f"{slug}.mp4"
        delivery_video = root / "artifacts" / "videos" / f"{slug}.mp4"
        contact_sheet = package_root / "artifacts" / "reviews" / "contact-sheet.jpg"
        renderer_path = package_root / "src" / "index.html"
        asset_manifest_path = package_root / "source" / "asset-manifest.json"
        audio_report_path = package_root / "artifacts" / "audio" / "neural-audio-build-report.json"
        acquisition_path = package_root / "artifacts" / "source-images" / "source-image-acquisition.json"
        hold_sheet = package_root / "artifacts" / "reviews" / "hold-sheet-8-scenes.jpg"

        row_failures: list[str] = []
        report = None
        if package_report_path.exists():
            try:
                report = json.loads(package_report_path.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError) as exc:
                row_failures.append(f"invalid package report: {exc}")
        else:
            row_failures.append("missing package report")

        for label, path in (
            ("package video", package_video),
            ("delivery video", delivery_video),
            ("contact sheet", contact_sheet),
        ):
            if not path.exists() or path.stat().st_size == 0:
                row_failures.append(f"missing or empty {label}")

        media = ffprobe(delivery_video) if delivery_video.exists() else {"ok": False}
        if media.get("ok"):
            checks = {
                "duration": math.isclose(media["durationSeconds"], 48.0, abs_tol=0.7),
                "dimensions": media["width"] == 1280 and media["height"] == 720,
                "frame rate": math.isclose(media["fps"], 30.0, abs_tol=0.01),
                "video codec": media["videoCodec"] == "h264",
                "audio codec": media["audioCodec"] == "aac",
                "audio stream": media["hasAudio"],
                "audio sample rate": media["audioSampleRate"] == 48000,
                "audio channels": media["audioChannels"] == 2,
            }
            row_failures.extend(f"invalid {label}" for label, ok in checks.items() if not ok)
        else:
            row_failures.append("ffprobe failed")

        package_hash = sha256(package_video) if package_video.exists() else None
        delivery_hash = sha256(delivery_video) if delivery_video.exists() else None
        reported_hash = report.get("video", {}).get("videoSha256") if report else None
        if package_hash and delivery_hash and package_hash != delivery_hash:
            row_failures.append("delivery video differs from package video")
        if reported_hash and delivery_hash and reported_hash != delivery_hash:
            row_failures.append("delivery video differs from validated report hash")
        if report and not report.get("ok"):
            row_failures.append("package validation did not pass")

        audio_report = {}
        if audio_report_path.exists():
            try:
                audio_report = json.loads(audio_report_path.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError) as exc:
                row_failures.append(f"invalid neural audio report: {exc}")
        else:
            row_failures.append("missing neural audio report")
        if audio_report:
            integrated_lufs = float(audio_report.get("measured", {}).get("input_i", 99))
            true_peak = float(audio_report.get("measured", {}).get("input_tp", 99))
            tempos = [float(cue.get("tempo", 99)) for cue in audio_report.get("cues", [])]
            audio_checks = {
                "neural audio report": bool(audio_report.get("ok")),
                "neural voice model": audio_report.get("voiceModel") == "VoxCPM2",
                "mix sample rate": int(audio_report.get("sampleRate", 0)) == 48000,
                "mix channels": int(audio_report.get("channels", 0)) == 2,
                "integrated loudness": math.isclose(integrated_lufs, -16.0, abs_tol=0.6),
                "true peak": true_peak <= -1.35,
                "speech tempo": bool(tempos) and max(tempos) <= 1.18,
                "long silences": not audio_report.get("silencesOverOneSecond", []),
            }
            row_failures.extend(f"invalid {label}" for label, ok in audio_checks.items() if not ok)

        acquisition = {}
        if acquisition_path.exists():
            try:
                acquisition = json.loads(acquisition_path.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError) as exc:
                row_failures.append(f"invalid source-image acquisition report: {exc}")
        else:
            row_failures.append("missing source-image acquisition report")
        if acquisition:
            if int(acquisition.get("strongImageCount", 0)) < 6:
                row_failures.append("fewer than six strong source images")
            if int(acquisition.get("uniqueImageHashes", 0)) < 6:
                row_failures.append("fewer than six unique source images")
        source_image_bindings: list[dict] = []
        category_items = ranked_by_category.get(category["id"], [])
        acquired_images = {int(item.get("rank", 0)): item for item in acquisition.get("images", [])}
        for rank in range(1, 9):
            if len(category_items) < rank:
                row_failures.append(f"missing ranked item {rank} for image identity check")
                continue
            expected = category_items[rank - 1]
            acquired = acquired_images.get(rank, {})
            binding = {
                "rank": rank,
                "expectedItemId": expected.get("id"),
                "actualItemId": acquired.get("itemId"),
                "expectedName": expected.get("name"),
                "actualName": acquired.get("name"),
                "status": acquired.get("status"),
                "identityMatches": (
                    acquired.get("itemId") == expected.get("id")
                    and acquired.get("name") == expected.get("name")
                    and int(acquired.get("rank") or -1) == rank
                ),
            }
            source_image_bindings.append(binding)
            if not binding["identityMatches"]:
                row_failures.append(f"rank {rank} source image identity mismatch")
        if not hold_sheet.exists() or hold_sheet.stat().st_size == 0:
            row_failures.append("missing eight-scene hold sheet")

        semantic_bindings: list[dict] = []
        if renderer_path.exists() and asset_manifest_path.exists():
            renderer_text = renderer_path.read_text(encoding="utf-8")
            match = re.search(r"const SCENES=(\[.*?\]);\r?\n", renderer_text, re.DOTALL)
            try:
                scenes = json.loads(match.group(1)) if match else []
                assets = {
                    item["id"]: item
                    for item in json.loads(asset_manifest_path.read_text(encoding="utf-8"))["assets"]
                }
                for rank in range(1, 4):
                    scene = scenes[rank]
                    expected = category_items[rank - 1]
                    asset = assets[scene["assetId"]]
                    acquired = acquired_images.get(rank, {})
                    actual_url = asset.get("origin", {}).get("uri", "")
                    source_status = acquired.get("status")
                    expected_page_url = acquired.get("pageUrl") or ""
                    expected_fallback_uri = f"project-dataset:{category['id']}:{scene['assetId']}"
                    source_matches = (
                        source_status == "strong"
                        and bool(actual_url)
                        and expected_page_url.rstrip("/") == actual_url.rstrip("/")
                    ) or (
                        source_status == "fallback"
                        and actual_url == expected_fallback_uri
                    )
                    binding = {
                        "rank": rank,
                        "assetId": scene["assetId"],
                        "expectedName": expected["name"],
                        "visibleTitle": scene.get("title"),
                        "titleMatches": scene.get("title") == expected["name"],
                        "expectedSourceUrl": expected_page_url,
                        "assetSourceUrl": actual_url,
                        "sourceStatus": source_status,
                        "sourceNameMatches": acquired.get("name") == expected["name"],
                        "sourceMatches": source_matches,
                        "fallbackSourceBound": source_status == "fallback" and actual_url == expected_fallback_uri,
                    }
                    semantic_bindings.append(binding)
                    if (
                        not binding["titleMatches"]
                        or not binding["sourceMatches"]
                        or not binding["sourceNameMatches"]
                        or binding["sourceStatus"] not in {"strong", "fallback"}
                    ):
                        row_failures.append(f"rank {rank} source image/title binding mismatch")
            except (IndexError, KeyError, TypeError, json.JSONDecodeError) as exc:
                row_failures.append(f"cannot validate source image/title bindings: {exc}")
        else:
            row_failures.append("missing renderer or asset manifest for semantic binding check")

        selected = selected_counts.get(category["id"], 0)
        if selected <= 0 or selected > 50:
            row_failures.append(f"invalid selected count: {selected}")

        rows.append(
            {
                "order": category["order"],
                "categoryId": category["id"],
                "categoryName": category["name"],
                "videoSlug": slug,
                "selectedCount": selected,
                "ok": not row_failures,
                "failures": row_failures,
                "deliveryVideo": str(delivery_video),
                "contactSheet": str(contact_sheet),
                "sha256": delivery_hash,
                "media": media,
                "audio": {
                    "voiceModel": audio_report.get("voiceModel"),
                    "integratedLufs": audio_report.get("measured", {}).get("input_i"),
                    "truePeakDbtp": audio_report.get("measured", {}).get("input_tp"),
                    "maxTempo": max((float(cue.get("tempo", 0)) for cue in audio_report.get("cues", [])), default=None),
                },
                "images": {
                    "strongImageCount": acquisition.get("strongImageCount"),
                    "fallbackCount": acquisition.get("fallbackCount"),
                    "uniqueImageHashes": acquisition.get("uniqueImageHashes"),
                    "holdSheet": str(hold_sheet),
                    "sourceImageBindings": source_image_bindings,
                },
                "semanticBindings": semantic_bindings,
                "packageReadinessScore": (
                    report.get("package", {}).get("readinessReport", {}).get("score") if report else None
                ),
                "packageStyleScore": (
                    report.get("package", {}).get("styleFidelityReport", {}).get("score") if report else None
                ),
            }
        )
        failures.extend(f"{slug}: {message}" for message in row_failures)

    workbook = root / "artifacts" / "documents" / "holiday2026-family-guide.xlsx"
    if not workbook.exists() or workbook.stat().st_size == 0:
        failures.append("missing or empty workbook")

    series_validation: dict[str, dict] = {}
    for label, path in (
        ("audio", root / "artifacts" / "reviews" / "neural-audio-series-validation.json"),
        ("images", root / "artifacts" / "reviews" / "image-coverage-series-validation.json"),
    ):
        if not path.exists():
            failures.append(f"missing {label} series validation")
            series_validation[label] = {"ok": False, "path": str(path)}
            continue
        try:
            report_payload = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as exc:
            failures.append(f"invalid {label} series validation: {exc}")
            series_validation[label] = {"ok": False, "path": str(path)}
            continue
        if not report_payload.get("ok"):
            failures.append(f"{label} series validation did not pass")
        if int(report_payload.get("categoryCount", 0)) != len(categories):
            failures.append(f"{label} series validation category count mismatch")
        series_validation[label] = {
            "ok": bool(report_payload.get("ok")),
            "categoryCount": report_payload.get("categoryCount"),
            "path": str(path),
        }

    payload = {
        "schemaVersion": 1,
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "ok": not failures,
        "failures": failures,
        "projectRoot": str(root),
        "workbook": str(workbook),
        "categoryCount": len(categories),
        "selectedOptionCount": sum(selected_counts.values()),
        "validatedVideoCount": sum(1 for row in rows if row["ok"]),
        "expectedVideoCount": len(categories),
        "seriesValidation": series_validation,
        "videos": rows,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2))
    return 0 if payload["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
