#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Run final exact-output color contracts with retained isolated evidence."""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import os
import subprocess
import json
import argparse

ROOT = Path(__file__).resolve().parents[3]
ART = ROOT / "projects/colorset-audit/artifacts"
TEMP = ART / "tmp"
TEMP.mkdir(parents=True, exist_ok=True)
ENV = dict(os.environ, TEMP=str(TEMP), TMP=str(TEMP))
CASES = [
    ("pexels-media-search", "2", ["preview.html", "candidates.json"]),
    ("asciinema-real-command-video", "2", ["sample.cast", "themed.cast", "theme.json"]),
    ("animated-svg-to-gif", "luna-1", ["pulse.animated.svg", "pulse.gif"]),
    ("destockd-video-search", "1", ["candidates.json", "preview.html"]),
    ("technical-logo-assets", "1", ["logo.svg", "logo.provenance.json", "logo.license.txt"]),
    ("harbor-author-evaluation-datasets", "1", ["comparison/comparison-report.json", "comparison/comparison-report.md", "comparison/quality-comparison.svg", "comparison/resource-comparison.svg", "comparison/efficiency-frontier.svg"]),
    ("iconify-icon-search", "2", ["preview.html", "candidates.json"]),
    ("ambientcg-material-search", "final", ["preview.html", "candidates.json"]),
    ("kenney-asset-search", "final", ["preview.html", "candidates.json"]),
    ("polyhaven-asset-search", "final", ["preview.html", "candidates.json"]),
]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--skill", action="append")
parser.add_argument("--suffix")
args = parser.parse_args()
CASES = [case for case in CASES if not args.skill or case[0] in args.skill]

def run(case):
    skill, suffix, outputs = case
    suffix = args.suffix or suffix
    run_id = f"20261002-colorset-{skill}-{suffix}"
    argv = ["uv", "run", "--script", "scripts/run-pi-skill-eval.py", skill, "--prompt-file", f"evaluations/pi-prompts/colorset-{skill}.md", "--model", "openai-codex/gpt-5.6-luna", "--mode", "json", "--strict", "--run-id", run_id, "--timeout-seconds", "600"]
    for output in outputs:
        argv += ["--expect-output", output]
    result = subprocess.run(argv, cwd=ROOT, env=ENV, text=True, encoding="utf-8", errors="replace", capture_output=True)
    log = ART / "reviews" / (run_id + ".log")
    log.parent.mkdir(parents=True, exist_ok=True)
    log.write_text(result.stdout + result.stderr, encoding="utf-8")
    print(("PASS " if result.returncode == 0 else "FAIL ") + run_id, flush=True)
    return {"runId": run_id, "skill": skill, "model": "gpt-5.6-luna", "exitCode": result.returncode, "command": argv, "outputs": outputs}

with ThreadPoolExecutor(max_workers=2) as pool:
    rows = list(pool.map(run, CASES))
target = ART / ("data/final-support-pi" + ("-" + args.suffix if args.suffix else "") + ".json")
target.parent.mkdir(parents=True, exist_ok=True)
target.write_text(json.dumps(rows, indent=2) + "\n", encoding="utf-8")
raise SystemExit(0 if all(row["exitCode"] == 0 for row in rows) else 1)
