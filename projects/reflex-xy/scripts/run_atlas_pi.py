#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Run the prospectively declared eight-attempt XY atlas cohort, at most two at once."""
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import time

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "projects/reflex-xy/artifacts/atlas-pi"
PLAN = json.loads((OUT / "plan.json").read_text(encoding="utf-8"))
FROZEN = json.loads((OUT / "runtime-freeze.json").read_text(encoding="utf-8"))["digest"]


def run(attempt):
    run_id = attempt["run_id"]
    command = ["uv", "run", "--script", "scripts/run-pi-skill-eval.py", "reflex-xy",
               "--prompt-file", attempt["prompt"], "--model", PLAN["model"],
               "--mode", "json", "--strict", "--run-id", run_id,
               "--timeout-seconds", "900"]
    for artifact in attempt["outputs"]:
        command += ["--expect-output", artifact]
    if attempt["case"] == "contract":
        command += ["--require-exact-command-from-prompt",
                    "--expect-output-json-field", "results/repair.json::repairedPaths=1",
                    "--expect-output-json-field", "results/repair.json::validSvgXml=true"]
    print(f"START {run_id}", flush=True)
    started = time.monotonic()
    execution = subprocess.run(command, cwd=ROOT, capture_output=True, text=True,
                               encoding="utf-8", errors="replace")
    log_dir = OUT / "harness"
    log_dir.mkdir(exist_ok=True)
    (log_dir / f"{run_id}.stdout.txt").write_text(execution.stdout, encoding="utf-8")
    (log_dir / f"{run_id}.stderr.txt").write_text(execution.stderr, encoding="utf-8")
    result = {**attempt, "command": command, "returncode": execution.returncode,
              "elapsed_seconds": round(time.monotonic() - started, 2)}
    manifest_path = ROOT / "evaluations/runs" / run_id / "run-manifest.json"
    if manifest_path.is_file():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        result["payload_sha256"] = manifest["skill"]["payloadSha256"]
        result["frozen_digest_matches"] = result["payload_sha256"] == FROZEN
    else:
        result["frozen_digest_matches"] = False
    (log_dir / f"{run_id}.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(f"DONE {run_id} exit={execution.returncode} frozen={result['frozen_digest_matches']}", flush=True)
    return result


if __name__ == "__main__":
    if len(PLAN["attempts"]) != 8 or PLAN["concurrency"] != 2:
        raise ValueError("The frozen cohort must contain exactly eight attempts and concurrency two")
    existing = [a["run_id"] for a in PLAN["attempts"] if (ROOT / "evaluations/runs" / a["run_id"]).exists()]
    if existing:
        raise ValueError(f"Refusing to replace retained attempt directories: {existing}")
    results = []
    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = [executor.submit(run, attempt) for attempt in PLAN["attempts"]]
        for future in as_completed(futures):
            results.append(future.result())
            (OUT / "harness-progress.json").write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
    (OUT / "harness-results.json").write_text(json.dumps({"completed_at_utc": datetime.now(timezone.utc).isoformat(), "attempts": results}, indent=2) + "\n", encoding="utf-8")
