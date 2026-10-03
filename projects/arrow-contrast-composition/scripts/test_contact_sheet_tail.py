#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["Pillow>=11,<13"]
# ///
"""Regress real last-frame extraction for dense and low-fps native MP4 clips."""
import json
import subprocess
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "projects/arrow-contrast-composition/artifacts/contact-sheet-tail"
OUT.mkdir(parents=True, exist_ok=True)
cases = []
for rate, duration, counts in [(12, 2, [6, 12, 30]), (2, 2, [6, 30]), (.5, 4, [6])]:
    video = OUT / f"clip-{rate}fps.mp4"
    encode = ["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i",
              f"testsrc2=size=320x180:rate={rate}:duration={duration}", "-c:v", "libx264", "-pix_fmt", "yuv420p", str(video)]
    subprocess.run(encode, check=True, capture_output=True)
    probe = json.loads(subprocess.check_output(["ffprobe", "-v", "error", "-select_streams", "v:0",
        "-show_frames", "-show_entries", "frame=best_effort_timestamp_time", "-of", "json", str(video)], text=True))
    last_pts = max(float(frame["best_effort_timestamp_time"]) for frame in probe["frames"])
    for count in counts:
        ident = f"{rate}fps-{count}-samples"
        sheet, manifest = OUT / (ident + ".png"), OUT / (ident + ".json")
        command = ["uv", "run", "--script", "skills/video/scripts/make_video_contact_sheet.py", "--video", str(video),
            "--output", str(sheet), "--manifest", str(manifest), "--samples", str(count), "--columns", "3", "--thumb-width", "160", "--label-times"]
        result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
        assert result.returncode == 0, (ident, result.stderr)
        report = json.loads(manifest.read_text())
        assert report["passed"] and report["sheet"]["tiles"] == count and report["samples"] == count
        assert report["frameIntervalSeconds"] >= 1 / rate - 1e-10
        assert max(report["seekTimes"]) <= last_pts, (ident, last_pts, report["seekTimes"])
        assert all(seek <= requested for seek, requested in zip(report["seekTimes"], report["sampleTimes"]))
        image = Image.open(sheet)
        assert image.size == (report["sheet"]["width"], report["sheet"]["height"])
        assert min(report["metrics"]["tileColorBuckets"]) > 20 and min(report["metrics"]["tileNonbackgroundRatios"]) > .1
        cases.append({"id": ident, "command": command, "sourceLastFramePts": last_pts,
            "seekTimes": report["seekTimes"], "nativeFrames": len(probe["frames"]), "tileCount": count, "passed": True})

bad = OUT / "unreadable.mp4"
bad.write_text("Not a video", encoding="utf-8")
result = subprocess.run(["uv", "run", "--script", "skills/video/scripts/make_video_contact_sheet.py", "--video", str(bad),
    "--output", str(OUT / "unreadable.png")], cwd=ROOT, text=True, capture_output=True)
assert result.returncode != 0 and not (OUT / "unreadable.png").exists()
cases.append({"id": "unreadable-input-refused", "exitCode": result.returncode, "reason": result.stderr, "passed": True})
(OUT / "results.json").write_text(json.dumps({"passed": True, "cases": cases}, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"passed": True, "cases": len(cases), "clips": 3, "sampledFrames": 90}))
