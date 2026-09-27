#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Run the isolated composition cases with a recorded model exception."""

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[2]
CASES = {
    "d3": {
        "contract": ["flow.html", "flow.svg", "decision.json"],
        "naturalistic": ["process.html", "process.svg", "decision.json"],
        "boundary": ["boundary.html", "boundary.svg", "decision.json"],
        "generalization": ["dashboard/index.html", "dashboard/data.js", "dashboard/styles.css", "dashboard.svg"],
    },
    "threejs": {
        "contract": ["scene.html", "validation.json"],
        "naturalistic": ["signal.html", "validation.json"],
        "boundary": ["extended.html", "validation.json"],
        "generalization": ["workers.html", "validation.json"],
    },
}


def run_case(task):
    library, case, repetition, cohort = task
    skill = "d3" if library == "d3" else "threejs-animated-3d"
    run_id = f"{library}-compact-{case}-20260927-{cohort}-{repetition}"
    command = ["uv", "run", "--script", "scripts/run-pi-skill-eval.py", skill,
               "--prompt-file", f"evaluations/pi-prompts/{library}-compact-{case}.md",
               "--model", "openai-codex/gpt-5.6-luna", "--thinking", "medium",
               "--mode", "json", "--strict", "--timeout-seconds", "600", "--run-id", run_id]
    for output in CASES[library][case]:
        command.extend(["--expect-output", output])
    if case == "contract":
        command.append("--require-exact-command-from-prompt")
    result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace")
    log = ROOT / "projects/library-composition/artifacts/pi-logs" / f"{run_id}.txt"
    log.parent.mkdir(parents=True, exist_ok=True)
    log.write_text(result.stdout + "\n" + result.stderr, encoding="utf-8")
    record = {"runId": run_id, "skill": skill, "case": case, "repetition": repetition,
              "exitCode": result.returncode, "command": command, "log": str(log.relative_to(ROOT))}
    print(json.dumps(record), flush=True)
    return record


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--cohort", required=True)
    parser.add_argument("--cases", nargs="+", default=list(CASES["d3"]))
    parser.add_argument("--libraries", nargs="+", default=list(CASES))
    args = parser.parse_args()
    tasks = [(lib, case, repeat, args.cohort) for lib in args.libraries for case in args.cases
             for repeat in range(1, (3 if case in {"naturalistic", "generalization"} else 1) + 1)]
    records = []
    with ThreadPoolExecutor(max_workers=2) as pool:
        for future in as_completed([pool.submit(run_case, task) for task in tasks]):
            records.append(future.result())
            target = ROOT / f"projects/library-composition/artifacts/pi-{args.cohort}.json"
            target.write_text(json.dumps(records, indent=2) + "\n", encoding="utf-8")
    raise SystemExit(1 if any(record["exitCode"] for record in records) else 0)
