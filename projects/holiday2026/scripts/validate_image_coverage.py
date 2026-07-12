#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["pillow>=11.0.0"]
# ///
"""Validate source-image coverage and build eight-scene review sheets."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageStat


PROJECT = Path(__file__).resolve().parents[1]
PACKAGES = PROJECT / "video-packages"
HOLD_TIMES = [3, 9, 15, 21, 27, 33, 39, 45]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def font(size: int, bold: bool = False):
    path = Path("C:/Windows/Fonts/segoeuib.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf")
    return ImageFont.truetype(str(path), size) if path.exists() else ImageFont.load_default()


def hold_sheet(video: Path, output: Path) -> dict:
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="holiday2026-holds-") as temp_dir:
        temp = Path(temp_dir)
        frames: list[Path] = []
        for index, timestamp in enumerate(HOLD_TIMES, start=1):
            frame = temp / f"hold-{index:02d}.png"
            subprocess.run(
                ["ffmpeg", "-y", "-loglevel", "error", "-ss", str(timestamp), "-i", str(video), "-frames:v", "1", "-vf", "scale=640:360", str(frame)],
                check=True,
            )
            frames.append(frame)
        sheet = Image.new("RGB", (1280, 800), "#F6F3EE")
        draw = ImageDraw.Draw(sheet)
        for index, frame in enumerate(frames):
            with Image.open(frame) as raw:
                image = raw.convert("RGB")
            col = index % 2
            row = index // 2
            x = col * 640
            y = row * 200
            thumb = image.resize((640, 180), Image.Resampling.LANCZOS)
            sheet.paste(thumb, (x, y))
            draw.rectangle((x, y + 180, x + 640, y + 200), fill="#FFFCF8")
            draw.text((x + 10, y + 181), f"s{index + 1:02d} • {HOLD_TIMES[index]}s", font=font(14, True), fill="#263238")
        sheet.save(output, format="JPEG", quality=91, optimize=True)
    sample = sheet.resize((320, 200)).convert("L")
    return {
        "path": str(output),
        "sha256": sha256(output),
        "width": sheet.width,
        "height": sheet.height,
        "luminanceStddev": round(float(ImageStat.Stat(sample).stddev[0]), 3),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--require-video", action="store_true")
    parser.add_argument("--min-strong", type=int, default=6)
    parser.add_argument("--min-scene-coverage", type=float, default=0.75)
    args = parser.parse_args()

    categories = json.loads((PROJECT / "source" / "categories.json").read_text(encoding="utf-8"))
    failures: list[str] = []
    rows: list[dict] = []
    for category in categories:
        slug = category["video_slug"]
        package = PACKAGES / slug
        acquisition_path = package / "artifacts" / "source-images" / "source-image-acquisition.json"
        manifest_path = package / "source" / "asset-manifest.json"
        row_failures: list[str] = []
        acquisition = json.loads(acquisition_path.read_text(encoding="utf-8")) if acquisition_path.exists() else {}
        manifest = json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.exists() else {}
        strong = int(acquisition.get("strongImageCount", 0))
        unique = int(acquisition.get("uniqueImageHashes", 0))
        if strong < args.min_strong:
            row_failures.append(f"only {strong} strong source images")
        if unique < args.min_strong:
            row_failures.append(f"only {unique} unique source image hashes")

        assets = manifest.get("assets", [])
        image_scenes = 0
        primary_photo_scenes = 0
        embedded_counts: list[int] = []
        for index, asset in enumerate(assets, start=1):
            embedded = asset.get("origin", {}).get("embeddedSources", [])
            embedded_counts.append(len(embedded))
            if embedded:
                image_scenes += 1
            if index in {2, 3, 4, 5, 7} and embedded:
                primary_photo_scenes += 1
            output = package / asset.get("output", "")
            if not output.exists() or output.stat().st_size == 0:
                row_failures.append(f"missing asset output for {asset.get('id')}")
        coverage = image_scenes / 8
        primary_coverage = primary_photo_scenes / 8
        if coverage < args.min_scene_coverage:
            row_failures.append(f"source image scene coverage {coverage:.3f} is too low")
        if primary_coverage < 0.625:
            row_failures.append(f"primary photo scene coverage {primary_coverage:.3f} is too low")

        video = PROJECT / "artifacts" / "videos" / f"{slug}.mp4"
        sheet = None
        if args.require_video:
            if not video.exists():
                row_failures.append("missing final video")
            else:
                sheet = hold_sheet(video, package / "artifacts" / "reviews" / "hold-sheet-8-scenes.jpg")
                if sheet["luminanceStddev"] < 12:
                    row_failures.append("eight-scene hold sheet has low visual variance")

        row = {
            "videoSlug": slug,
            "ok": not row_failures,
            "failures": row_failures,
            "strongImageCount": strong,
            "fallbackCount": int(acquisition.get("fallbackCount", 0)),
            "uniqueSourceImageHashes": unique,
            "assetCount": len(assets),
            "embeddedSourceCounts": embedded_counts,
            "sourceImageSceneCoverage": round(coverage, 4),
            "primaryPhotoSceneCoverage": round(primary_coverage, 4),
            "sourceImageRuntimeCoverage": round(coverage, 4),
            "holdSheet": sheet,
        }
        rows.append(row)
        failures.extend(f"{slug}: {message}" for message in row_failures)

    report = {
        "schemaVersion": 1,
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "ok": not failures,
        "failures": failures,
        "categoryCount": len(rows),
        "validatedCategoryCount": sum(1 for row in rows if row["ok"]),
        "minimumStrongImagesPerCategory": args.min_strong,
        "minimumSceneCoverage": args.min_scene_coverage,
        "videos": rows,
    }
    output = PROJECT / "artifacts" / "reviews" / "image-coverage-series-validation.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
