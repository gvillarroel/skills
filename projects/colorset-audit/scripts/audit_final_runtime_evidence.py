#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Freeze every current visual runtime against an accepted strict trace."""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import importlib.util
import json
import os
import subprocess

ROOT = Path(__file__).resolve().parents[3]
SPEC = importlib.util.spec_from_file_location("pi_runner", ROOT / "scripts/run-pi-skill-eval.py")
RUNNER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(RUNNER)
OUT = ROOT / "evaluations/colorset-audit"
ART = ROOT / "projects/colorset-audit/artifacts"


def runtime_snapshot(source):
    snapshot = {}
    for directory, children, files in os.walk(source):
        relative_directory = Path(directory).relative_to(source)
        children[:] = [name for name in children if name not in RUNNER.COPY_IGNORE and relative_directory / name not in RUNNER.RUNTIME_EXCLUDED_DIRS]
        for name in files:
            path = Path(directory) / name
            if name in RUNNER.COPY_IGNORE or path.suffix.lower() in RUNNER.SNAPSHOT_IGNORED_SUFFIXES:
                continue
            snapshot[path.relative_to(source).as_posix()] = {"sizeBytes": path.stat().st_size, "sha256": RUNNER.sha256_file(path)}
    return RUNNER.snapshot_digest(snapshot), len(snapshot)


attempts = []
for run in sorted((ROOT / "evaluations/runs").iterdir()):
    if "colorset" not in run.name or "20261002" not in run.name:
        continue
    if not (run / "run-manifest.json").is_file() or not (run / "evaluation-result.json").is_file():
        continue
    manifest = json.loads((run / "run-manifest.json").read_text())
    result = json.loads((run / "evaluation-result.json").read_text())
    attempts.append({"runId": run.name, "skill": manifest["skill"]["name"], "startedAtUtc": result["startedAtUtc"], "passed": result["passed"], "model": manifest["pi"]["model"], "payloadSha256": manifest["skill"]["payloadSha256"], "gates": result["gates"], "resultPath": f"evaluations/runs/{run.name}/evaluation-result.json"})
inventory = json.loads((OUT / "coverage.json").read_text())
selected, failures = [], []
for skill in inventory["skills"]:
    if skill["scope"] == "nonvisual":
        continue
    digest, count = runtime_snapshot(ROOT / "skills" / skill["skill"])
    matches = [run for run in attempts if run["skill"] == skill["skill"] and run["passed"] and run["payloadSha256"] == digest]
    if not matches:
        failures.append({"skill": skill["skill"], "currentPayloadSha256": digest, "error": "No accepted strict run matches current runtime bytes"})
        continue
    row = max(matches, key=lambda run: run["startedAtUtc"])
    row = dict(row, currentRuntimeMatches=True, runtimeFileCount=count)
    artifact = json.loads((ROOT / f"evaluations/runs/{row['runId']}/artifact-check.json").read_text())
    row["outputs"] = artifact["outputs"]
    manifest = json.loads((ROOT / f"evaluations/runs/{row['runId']}/run-manifest.json").read_text())
    row["isolatedCommand"] = manifest["command"]
    selected.append(row)


def summarize(row):
    model = row["model"].split("/")[-1]
    argv = ["uv", "run", "--script", "scripts/summarize-pi-json-events.py", f"evaluations/runs/{row['runId']}/events.jsonl", "--require-model", model, "--fail-on-invalid-json", "--fail-on-tool-error"]
    result = subprocess.run(argv, cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace")
    path = ART / "reviews" / (row["runId"] + "-event-summary.log")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(result.stdout + result.stderr, encoding="utf-8")
    return {"runId": row["runId"], "exitCode": result.returncode, "command": argv}


with ThreadPoolExecutor(max_workers=3) as pool:
    summaries = list(pool.map(summarize, selected))
failures.extend(row for row in summaries if row["exitCode"])
report = {"schemaVersion": 1, "date": "2026-10-02", "passed": not failures and len(selected) == 30, "visualSkillCount": len(selected), "selectedRuns": selected, "traceSummaries": summaries, "retainedAttempts": attempts, "failures": failures, "limits": "One supplemental colorset case per current runtime; previous release cohorts and broader skill validation statuses remain unchanged. Four bundles have no authored painter; simulation live-Pi prohibition respected."}
(OUT / "final-runtime-20261002.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"passed": report["passed"], "currentVisualRuntimes": len(selected), "retainedAttempts": len(attempts), "failures": failures}, indent=2))
raise SystemExit(0 if report["passed"] else 1)
