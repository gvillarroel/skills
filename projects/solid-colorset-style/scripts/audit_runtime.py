#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Bind final standalone skill payloads to strict, exact-output runtime evidence."""
from concurrent.futures import ThreadPoolExecutor
import importlib.util
import json
import os
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[3]
SPEC = importlib.util.spec_from_file_location("pi_runner", ROOT / "scripts/run-pi-skill-eval.py")
RUNNER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(RUNNER)
OUT = ROOT / "evaluations/solid-colorset-style"
ART = ROOT / "projects/solid-colorset-style/artifacts"


def runtime_snapshot(source):
    snapshot = {}
    for directory, children, files in os.walk(source):
        relative = Path(directory).relative_to(source)
        children[:] = [name for name in children if name not in RUNNER.COPY_IGNORE and relative / name not in RUNNER.RUNTIME_EXCLUDED_DIRS]
        for name in files:
            path = Path(directory) / name
            if name in RUNNER.COPY_IGNORE or path.suffix.lower() in RUNNER.SNAPSHOT_IGNORED_SUFFIXES:
                continue
            snapshot[path.relative_to(source).as_posix()] = {"sizeBytes": path.stat().st_size, "sha256": RUNNER.sha256_file(path)}
    return RUNNER.snapshot_digest(snapshot), len(snapshot)


def main():
    attempts = []
    for run in sorted((ROOT / "evaluations/runs").iterdir()):
        if "solid" not in run.name or "20261003" not in run.name:
            continue
        if not (run / "run-manifest.json").is_file() or not (run / "evaluation-result.json").is_file():
            continue
        manifest = json.loads((run / "run-manifest.json").read_text())
        result = json.loads((run / "evaluation-result.json").read_text())
        attempts.append({"runId": run.name, "skill": manifest["skill"]["name"], "passed": result["passed"], "model": manifest["pi"]["model"], "payloadSha256": manifest["skill"]["payloadSha256"], "startedAtUtc": result["startedAtUtc"], "gates": result["gates"], "strict": manifest["eventPolicy"]["strict"], "command": manifest["command"], "resultPath": f"evaluations/runs/{run.name}/evaluation-result.json"})
    inventory = json.loads((ROOT / "evaluations/colorset-audit/coverage.json").read_text())
    selected, failures = [], []
    for row in inventory["skills"]:
        if row["scope"] == "nonvisual":
            continue
        digest, count = runtime_snapshot(ROOT / "skills" / row["skill"])
        matches = [run for run in attempts if run["skill"] == row["skill"] and run["passed"] and run["payloadSha256"] == digest and run["strict"] is True and all(run["gates"].get(key) is True for key in ("events", "artifacts", "skillIntegrity"))]
        if not matches:
            failures.append({"skill": row["skill"], "currentPayloadSha256": digest, "error": "No strict exact-output run matches the final payload"})
            continue
        run = dict(max(matches, key=lambda item: item["startedAtUtc"]), runtimeFileCount=count, currentRuntimeMatches=True)
        run["outputs"] = json.loads((ROOT / f"evaluations/runs/{run['runId']}/artifact-check.json").read_text())["outputs"]
        workspace = ROOT / "evaluations/runs" / run["runId"] / "workspace"
        for output in run["outputs"]:
            artifact = (workspace / output["path"]).resolve()
            if (not artifact.is_relative_to(workspace.resolve()) or not artifact.is_file()
                    or artifact.stat().st_size != output["sizeBytes"]
                    or RUNNER.sha256_file(artifact) != output["sha256"]):
                failures.append({"runId": run["runId"], "artifact": output["path"],
                                 "error": "Accepted artifact no longer matches sealed bytes"})
        run["artifactBytesRechecked"] = True
        selected.append(run)

    def summarize(row):
        model = row["model"].split("/")[-1]
        command = ["uv", "run", "--script", "scripts/summarize-pi-json-events.py", f"evaluations/runs/{row['runId']}/events.jsonl", "--require-model", model, "--fail-on-invalid-json", "--fail-on-tool-error"]
        result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace")
        path = ART / "reviews" / (row["runId"] + "-trace.json")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(result.stdout + result.stderr, encoding="utf-8")
        return {"runId": row["runId"], "exitCode": result.returncode, "command": command, "log": path.relative_to(ROOT).as_posix()}

    with ThreadPoolExecutor(max_workers=3) as pool:
        summaries = list(pool.map(summarize, selected))
    failures.extend(item for item in summaries if item["exitCode"])
    report = {"date": "2026-10-03", "passed": not failures and len(selected) == 30, "selectedRuns": selected, "traceSummaries": summaries, "retainedAttempts": attempts, "failures": failures, "scope": "Supplementary presentation regression for all 30 authored-output bundles. Earlier broader release cohorts and nonvisual data/source fidelity boundaries remain unchanged."}
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "final-runtime-20261003.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"passed": report["passed"], "matchingRuntimes": len(selected), "retainedAttempts": len(attempts), "failures": failures}, indent=2))
    raise SystemExit(0 if report["passed"] else 1)


if __name__ == "__main__":
    main()
