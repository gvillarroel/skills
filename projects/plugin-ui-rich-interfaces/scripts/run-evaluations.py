#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Run isolated rich-interface skill cases and retain every attempt."""
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
import argparse
import hashlib
import json
import shutil
import subprocess
import time

ROOT = Path(__file__).resolve().parents[3]
PROJECT = ROOT / "projects/plugin-ui-rich-interfaces"
MODEL = "openai-codex/gpt-6.1-sol"


def run(case, attempt):
    identifier = f'20261112-rich-ui-{case["skill"]}-{case["case"]}-{attempt}'
    argv = [shutil.which("uv"), "run", "--script", "scripts/run-pi-skill-eval.py", case["skill"],
            "--prompt-file", case["prompt"], "--mode", "json", "--strict", "--model", MODEL,
            "--thinking", "medium", "--run-id", identifier, "--timeout-seconds", "480"]
    if case["case"] == "contract":
        argv.append("--require-exact-command-from-prompt")
    for artifact in case["expected"]:
        argv.extend(["--expect-output", artifact])
    started = time.monotonic()
    result = subprocess.run(argv, cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace")
    directory = PROJECT / "artifacts/evaluations"
    (directory / f"{identifier}.log").write_text(result.stdout + result.stderr, encoding="utf-8")
    row = {**case, "run_id": identifier, "model": MODEL, "thinking": "medium", "command": argv[3:],
           "exit_code": result.returncode, "seconds": round(time.monotonic() - started, 3)}
    print(json.dumps({"run_id": identifier, "exit_code": result.returncode, "seconds": row["seconds"]}), flush=True)
    return row


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--attempt", default="sol-1")
    parser.add_argument("--case", action="append")
    parser.add_argument("--skill", action="append")
    parser.add_argument("--workers", type=int, default=3)
    args = parser.parse_args()
    cases = json.loads((PROJECT / "evaluation-cases.json").read_text(encoding="utf-8"))
    cases = [case for case in cases if (not args.case or case["case"] in args.case) and (not args.skill or case["skill"] in args.skill)]
    directory = PROJECT / "artifacts/evaluations"
    directory.mkdir(parents=True, exist_ok=True)
    subjects = {}
    for skill in sorted({case["skill"] for case in cases}):
        bundle = ROOT / "skills" / skill
        subjects[skill] = {p.relative_to(bundle).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(bundle.rglob("*")) if p.is_file() and not any(part in {"__pycache__", "node_modules", "dist"} for part in p.relative_to(bundle).parts)}
    (directory / f"subjects-{args.attempt}.json").write_text(json.dumps(subjects, indent=2) + "\n", encoding="utf-8")
    rows = []
    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        pending = [executor.submit(run, case, args.attempt) for case in cases]
        for future in as_completed(pending):
            rows.append(future.result())
            (directory / f"results-{args.attempt}.json").write_text(json.dumps(rows, indent=2) + "\n", encoding="utf-8")
    return int(any(row["exit_code"] for row in rows))


if __name__ == "__main__":
    raise SystemExit(main())
