#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Run support renderer regressions with workspace-local scratch and logs."""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import json
import os
import subprocess

ROOT = Path(__file__).resolve().parents[3]
ARTIFACTS = ROOT / "projects/colorset-audit/artifacts"
TEMP = ARTIFACTS / "tmp"
TEMP.mkdir(parents=True, exist_ok=True)
environment = dict(os.environ, TEMP=str(TEMP), TMP=str(TEMP))
paths = [
    "scripts/test-colorsets.py",
    "skills/animated-svg-to-gif/scripts/test_capture_colorset.py",
    "skills/animated-svg-to-gif/scripts/test_convert_animated_svg_to_gif.py",
    "skills/asciinema-real-command-video/scripts/test_asciinema_command_video.py",
    "skills/asciinema-real-command-video/scripts/test_terminal_colorsets.py",
    "skills/one-bit-dither-svg/scripts/test_stylize_svg.py",
    "skills/one-bit-dither-svg/scripts/test_stylize_animated_image.py",
    "skills/pixel-art-image-video/scripts/test_pixel_art.py",
    "skills/harbor-author-evaluation-datasets/scripts/test_consolidate_harbor_reports.py",
    "skills/technical-logo-assets/scripts/test_logo_variants.py",
    *[f"skills/{skill}/scripts/test_asset_io.py" for skill in ("ambientcg-material-search", "iconify-icon-search", "kenney-asset-search", "pexels-media-search", "polyhaven-asset-search")],
    *[f"skills/{skill}/scripts/test_{provider}.py" for skill, provider in (("ambientcg-material-search", "ambientcg"), ("iconify-icon-search", "iconify"), ("kenney-asset-search", "kenney"), ("pexels-media-search", "pexels"), ("polyhaven-asset-search", "polyhaven"), ("destockd-video-search", "destockd"))],
]


def run(path):
    result = subprocess.run(["uv", "run", "--script", path], cwd=ROOT, env=environment, text=True, encoding="utf-8", errors="replace", capture_output=True)
    output = ARTIFACTS / "reviews" / (path.replace("/", "--") + ".log")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(result.stdout + result.stderr, encoding="utf-8")
    row = {"command": f"uv run --script {path}", "exitCode": result.returncode, "log": output.relative_to(ROOT).as_posix()}
    print(("PASS" if result.returncode == 0 else "FAIL") + " " + path, flush=True)
    if result.returncode:
        print(result.stderr[-1400:], flush=True)
    return row


with ThreadPoolExecutor(max_workers=3) as pool:
    rows = list(pool.map(run, paths))
target = ARTIFACTS / "data/support-tests.json"
target.parent.mkdir(parents=True, exist_ok=True)
target.write_text(json.dumps({"ok": all(row["exitCode"] == 0 for row in rows), "checks": rows}, indent=2) + "\n", encoding="utf-8")
raise SystemExit(0 if all(row["exitCode"] == 0 for row in rows) else 1)
