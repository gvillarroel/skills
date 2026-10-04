#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Dispatch explicitly selected, frozen standalone priority cases and retain results."""
from __future__ import annotations
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
spec = importlib.util.spec_from_file_location("priority_harness", ROOT / "scripts/run-pi-skill-eval.py")
HARNESS = importlib.util.module_from_spec(spec)
spec.loader.exec_module(HARNESS)


def runtime_snapshot(skill):
    source = ROOT / "skills" / skill
    complete = HARNESS.snapshot_tree(source)
    return {path: value for path, value in complete.items() if not any(part in HARNESS.COPY_IGNORE for part in Path(path).parts) and not path.startswith("assets/examples/")}


def run_case(skill, kind, attempt, case, config, cohort):
    run_id = f"20261004-cs1-priority-{skill}-{kind}-{cohort}-{attempt}"
    run = ROOT / "evaluations/runs" / run_id
    if run.exists():
        raise RuntimeError(f"Refusing to reuse existing run directory: {run_id}")
    snapshot = runtime_snapshot(skill)
    prompt_path = HERE / case["prompt"]
    prompt_digest = hashlib.sha256(prompt_path.read_bytes()).hexdigest()
    command = ["uv", "run", "--script", "scripts/run-pi-skill-eval.py", skill,
               "--prompt-file", str(HERE / case["prompt"]), "--model", config["model"],
               "--thinking", config["thinking"], "--mode", "json", "--strict", "--run-id", run_id,
               "--timeout-seconds", "900"]
    if kind == "contract":
        command.append("--require-exact-command-from-prompt")
    for output in case["outputs"]:
        command += ["--expect-output", output]
    env = os.environ.copy()
    normal_tool_shim = ROOT / "projects/visual-asset-composition/artifacts/tools"
    env["PATH"] = str(normal_tool_shim) + os.pathsep + env.get("PATH", "")
    started = subprocess.run(command, cwd=ROOT, env=env, capture_output=True, text=True, encoding="utf-8", errors="replace", check=False)
    if not run.is_dir():
        run.mkdir(parents=True)
    (run / "dispatch.stdout.txt").write_text(started.stdout, encoding="utf-8")
    (run / "dispatch.stderr.txt").write_text(started.stderr, encoding="utf-8")
    payload = HARNESS.snapshot_digest(snapshot)
    after = runtime_snapshot(skill)
    result = {"runId": run_id, "skill": skill, "case": kind, "attempt": attempt,
              "model": config["model"], "thinking": config["thinking"], "command": command,
              "promptSha256": prompt_digest,
              "promptUnchangedDuringDispatch": hashlib.sha256(prompt_path.read_bytes()).hexdigest() == prompt_digest,
              "sourcePayloadSha256": payload, "sourcePayloadFileCount": len(snapshot),
              "sourcePayloadUnchanged": snapshot == after, "dispatchExitCode": started.returncode,
              "runResult": None, "artifactCheckExitCode": None,
              "failureClassification": None}
    manifest_path = run / "run-manifest.json"
    if manifest_path.is_file():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        result["copiedPayloadSha256"] = manifest["skill"]["payloadSha256"]
        result["copyMatchesFrozenSource"] = result["copiedPayloadSha256"] == payload
    evaluation_path = run / "evaluation-result.json"
    if evaluation_path.is_file():
        result["runResult"] = json.loads(evaluation_path.read_text(encoding="utf-8"))
    if started.returncode == 0:
        check = subprocess.run(["uv", "run", "--script", str(HERE / "validate_artifacts.py"), run_id], cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace", check=False)
        result["artifactCheckExitCode"] = check.returncode
        (run / "artifact-validator.stdout.txt").write_text(check.stdout, encoding="utf-8")
        (run / "artifact-validator.stderr.txt").write_text(check.stderr, encoding="utf-8")
    else:
        events_path = run / "events.jsonl"
        events = events_path.read_text(encoding="utf-8", errors="replace") if events_path.is_file() else ""
        if any(token in events.lower() for token in ("not supported", "unsupported model", "usage limit", "quota", "rate limit")):
            result["failureClassification"] = "infrastructure"
        else:
            result["failureClassification"] = "agent-or-skill-pending-review"
    result["strictArtifactPassed"] = (started.returncode == 0 and result["artifactCheckExitCode"] == 0 and result["sourcePayloadUnchanged"] and result.get("copyMatchesFrozenSource") is True and result["promptUnchangedDuringDispatch"])
    (run / "priority-dispatch.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: result[key] for key in ("runId", "dispatchExitCode", "artifactCheckExitCode", "sourcePayloadSha256", "strictArtifactPassed", "failureClassification")}), flush=True)
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--skills", nargs="+", required=True)
    parser.add_argument("--cases", nargs="+", choices=("contract", "naturalistic"), default=["contract"])
    parser.add_argument("--cohort", required=True)
    parser.add_argument("--workers", type=int, default=3)
    parser.add_argument("--dispatch", action="store_true")
    args = parser.parse_args()
    definitions = json.loads((HERE / "cases.json").read_text(encoding="utf-8"))
    jobs = [(skill, kind, attempt, definitions[skill][kind], definitions[skill], args.cohort)
            for skill in args.skills for kind in args.cases if kind in definitions[skill]
            for attempt in range(1, definitions[skill][kind]["repetitions"] + 1)]
    if not args.dispatch:
        print(json.dumps({"plannedRuns": len(jobs), "cohort": args.cohort, "dispatched": False}))
        return 0
    if not 1 <= args.workers <= 3:
        parser.error("workers must be between one and three")
    results = []
    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        pending = [executor.submit(run_case, *job) for job in jobs]
        for future in as_completed(pending):
            results.append(future.result())
            output = HERE / f"dispatch-{args.cohort}.json"
            output.write_text(json.dumps({"schemaVersion": 1, "cohort": args.cohort, "plannedRunCount": len(jobs), "completedRunCount": len(results), "results": sorted(results, key=lambda row: row["runId"])}, indent=2) + "\n", encoding="utf-8")
    print(f"Retained {len(results)} isolated results in dispatch-{args.cohort}.json.")
    return 0 if all(result["strictArtifactPassed"] for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
