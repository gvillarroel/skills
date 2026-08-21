#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""Collect stable MP4 deliverables from one or more Harbor jobs."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--job-root", action="append", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    return parser.parse_args()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def probe_video(path: Path) -> dict[str, object]:
    executable = shutil.which("ffprobe") or shutil.which("ffprobe.exe")
    if not executable:
        raise SystemExit("ffprobe or ffprobe.exe is required")
    completed = subprocess.run(
        [
            executable,
            "-v",
            "error",
            "-select_streams",
            "v:0",
            "-show_entries",
            "stream=codec_name,pix_fmt,width,height,avg_frame_rate:format=duration",
            "-of",
            "json",
            str(path),
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
        timeout=120,
    )
    if completed.returncode != 0:
        raise SystemExit(f"ffprobe failed for {path}: {completed.stderr}")
    return json.loads(completed.stdout)


def main() -> int:
    args = parse_arguments()
    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    entries: list[dict[str, object]] = []
    seen: set[str] = set()
    for job_root_value in args.job_root:
        job_root = job_root_value.resolve()
        for trial in sorted(path for path in job_root.iterdir() if path.is_dir()):
            task_id = trial.name.split("__", 1)[0]
            result_path = trial / "result.json"
            if result_path.is_file():
                try:
                    trial_result = json.loads(result_path.read_text(encoding="utf-8"))
                except (OSError, json.JSONDecodeError):
                    trial_result = {}
                if isinstance(trial_result, dict) and isinstance(
                    trial_result.get("task_name"), str
                ):
                    task_id = trial_result["task_name"]
            if task_id in seen:
                raise SystemExit(f"Duplicate task ID across jobs: {task_id}")
            source = trial / "artifacts" / "deliverables" / "session.mp4"
            if not source.is_file():
                raise SystemExit(f"Collected MP4 is missing for {task_id}: {source}")
            destination = output_dir / f"{task_id}.mp4"
            shutil.copy2(source, destination)
            probe = probe_video(destination)
            stream = (probe.get("streams") or [{}])[0]
            format_info = probe.get("format") or {}
            entries.append(
                {
                    "taskId": task_id,
                    "file": destination.name,
                    "bytes": destination.stat().st_size,
                    "sha256": sha256_file(destination),
                    "codec": stream.get("codec_name"),
                    "pixelFormat": stream.get("pix_fmt"),
                    "width": stream.get("width"),
                    "height": stream.get("height"),
                    "frameRate": stream.get("avg_frame_rate"),
                    "durationSeconds": float(format_info.get("duration") or 0.0),
                    "sourceJob": job_root.name,
                }
            )
            seen.add(task_id)
    manifest = {"schemaVersion": 1, "videoCount": len(entries), "videos": entries}
    (output_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
