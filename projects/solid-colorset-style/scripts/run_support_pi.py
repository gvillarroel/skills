#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Run supplementary support-style contracts with exact artifact paths."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import json
import os
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[3]
ART = ROOT / "projects/solid-colorset-style/artifacts"
TEMP = ART / "tmp"
TEMP.mkdir(parents=True, exist_ok=True)
ENV = dict(os.environ, TEMP=str(TEMP), TMP=str(TEMP))
CASES = {
    **{name: ["preview.html", "candidates.json"] for name in (
        "ambientcg-material-search", "iconify-icon-search", "kenney-asset-search", "pexels-media-search", "polyhaven-asset-search", "destockd-video-search")},
    "animated-svg-to-gif": ["pulse.animated.svg", "pulse.gif"],
    "asciinema-real-command-video": ["sample.cast", "themed.cast", "theme.json"],
    "technical-logo-assets": ["logo.svg", "logo.provenance.json", "logo.license.txt"],
    "harbor-author-evaluation-datasets": ["comparison/comparison-report.json", "comparison/comparison-report.md", "comparison/quality-comparison.svg", "comparison/resource-comparison.svg", "comparison/efficiency-frontier.svg"],
    "pixel-art-image-video": ["source.svg", "pixel.png", "pixel.json", "extended.webp", "extended.json"],
    "one-bit-dither-svg": ["source.svg", "regional.svg", "regional.png", "regional.json", "extended.svg", "extended.png", "extended.json"],
}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skill", action="append")
    parser.add_argument("--attempt", default="1")
    args = parser.parse_args()

    def run(skill):
        run_id = f"20261003-solid-{skill}-support-{args.attempt}"
        command = ["uv", "run", "--script", "scripts/run-pi-skill-eval.py", skill, "--prompt-file", f"evaluations/pi-prompts/colorset-{skill}.md", "--model", "openai-codex/gpt-5.6-luna", "--mode", "json", "--strict", "--run-id", run_id, "--timeout-seconds", "600"]
        for output in CASES[skill]:
            command.extend(["--expect-output", output])
        result = subprocess.run(command, cwd=ROOT, env=ENV, capture_output=True, text=True, encoding="utf-8", errors="replace")
        logs = ART / "reviews"
        logs.mkdir(parents=True, exist_ok=True)
        (logs / (run_id + ".log")).write_text(result.stdout + result.stderr, encoding="utf-8")
        print(("PASS " if result.returncode == 0 else "FAIL ") + run_id, flush=True)
        return {"skill": skill, "runId": run_id, "model": "gpt-5.6-luna", "command": command, "exitCode": result.returncode, "outputs": CASES[skill]}

    skills = args.skill or list(CASES)
    with ThreadPoolExecutor(max_workers=2) as pool:
        rows = list(pool.map(run, skills))
    directory = ROOT / "evaluations/solid-colorset-style"
    directory.mkdir(parents=True, exist_ok=True)
    target = directory / ("support-pi-20261003-" + args.attempt + ".json")
    target.write_text(json.dumps(rows, indent=2) + "\n", encoding="utf-8")
    raise SystemExit(0 if all(row["exitCode"] == 0 for row in rows) else 1)


if __name__ == "__main__":
    main()
