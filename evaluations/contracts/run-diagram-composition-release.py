#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Run a fixed fresh isolated release cohort and retain every outcome."""

import argparse
import concurrent.futures
import json
import subprocess
from pathlib import Path


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--prefix", required=True)
    ap.add_argument("--workers", type=int, default=3)
    ap.add_argument("--transfer-only", action="store_true")
    ap.add_argument("--naturalistic-only", action="store_true")
    ap.add_argument("--boundary-only", action="store_true")
    args = ap.parse_args()
    root = Path(__file__).resolve().parents[2]
    cases = [("contract", 1), ("naturalistic", 1), ("generalization", 1),
             ("naturalistic", 2), ("generalization", 2), ("boundary", 1),
             ("naturalistic", 3), ("generalization", 3)]
    if args.transfer_only:
        cases = [("transfer", i) for i in range(1,4)]
    if args.naturalistic_only:
        cases = [("naturalistic", i) for i in range(1,4)]
    if args.boundary_only:
        cases = [("boundary", i) for i in range(1,4)]
    records = []

    def one(case):
        name, repeat = case
        run_id = f"{args.prefix}-{name}-{repeat}"
        command = ["uv", "run", "--script", "scripts/run-pi-skill-eval.py", "diagram-composition",
            "--prompt-file", f"evaluations/pi-prompts/diagram-composition-{name}.md",
            "--model", "openai-codex/gpt-5.6-luna", "--mode", "json", "--strict",
            "--run-id", run_id, "--timeout-seconds", "900"]
        for output in ("plan.json", "figure.svg", "report.json", "audit.json", "preview.png", "review.md"):
            command += ["--expect-output", "out/" + output]
        command += ["--expect-output-json-field", "out/audit.json::ok=true"]
        print(f"Starting {run_id}", flush=True)
        result = subprocess.run(command, cwd=root, capture_output=True, text=True, encoding="utf-8", errors="replace")
        run_path = root / "evaluations" / "runs" / run_id
        run_path.mkdir(parents=True, exist_ok=True)
        (run_path / "orchestrator.log").write_text(result.stdout + result.stderr, encoding="utf-8")
        record = {"case": name, "repetition": repeat, "runId": run_id,
                  "command": command, "exitCode": result.returncode}
        print(f"Completed {run_id}: exit {result.returncode}", flush=True)
        return record

    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
        for future in concurrent.futures.as_completed([pool.submit(one, case) for case in cases]):
            records.append(future.result())
    output = root / "evaluations" / "runs" / f"{args.prefix}-cohort.json"
    output.write_text(json.dumps(sorted(records, key=lambda r: r["runId"]), indent=2) + "\n", encoding="utf-8")
    print(f"Saved all {len(records)} outcomes to {output}")
    raise SystemExit(0 if all(r["exitCode"] == 0 for r in records) else 1)


if __name__ == "__main__":
    main()
