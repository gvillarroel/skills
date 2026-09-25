#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Collect release evidence without changing model workspaces or skill payloads."""

import json
import os
import subprocess
from pathlib import Path

root = Path.cwd().resolve()
runs = root / "evaluations/runs"
reviews = root / "projects/hierarchy-lens/artifacts/reviews"
destination = root / "evaluations/hierarchy-lens"
destination.mkdir(parents=True, exist_ok=True)
os.environ["PLAYWRIGHT_BROWSERS_PATH"] = str(root / "projects/hierarchy-lens/artifacts/browser-cache")
collected = []
for run in sorted(runs.glob("hierarchy-lens-*20260925*")):
    manifest_path, result_path = run / "run-manifest.json", run / "evaluation-result.json"
    if not manifest_path.exists() or not result_path.exists():
        continue
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    result = json.loads(result_path.read_text(encoding="utf-8"))
    model = manifest["pi"]["model"].split("/")[-1]
    trace_path = run / "read-surface.json"
    trace_command = ["uv", "run", "--script", "scripts/summarize-pi-json-events.py", str(run / "events.jsonl"),
                     "--require-model", model, "--fail-on-invalid-json", "--fail-on-tool-error", "--output", str(trace_path)]
    subprocess.run(trace_command, cwd=root, capture_output=True, check=False)
    trace = json.loads(trace_path.read_text(encoding="utf-8"))
    item = {"runId": run.name, "passed": result["passed"], "model": model,
            "gates": result["gates"], "seconds": result["durationSeconds"],
            "payloadSha256": manifest["skill"]["payloadSha256"],
            "readPaths": [row["path"] for row in trace["readPaths"]],
            "tracePassed": trace["passed"], "traceFindings": trace["findings"]}
    if "spark" in run.name:
        item["classification"] = "infrastructure: provider rejected Spark before its first tool call"
    elif not result["passed"]:
        item["classification"] = "agent: hand-authored synthetic team counts failed an assertion before recovery"
    if "-v2-" in run.name and result["passed"] and "boundary" not in run.name:
        folder = "results" if "generalization" in run.name else "deliverables"
        stem = "portfolio" if "generalization" in run.name else "organization" if "naturalistic" in run.name else "map"
        data_name = "source" if stem == "map" else stem
        base = run / "workspace" / folder
        command = ["uv", "run", "--script", "evaluations/contracts/check-hierarchy-lens.py", str(base / (data_name + ".json")), str(base / (stem + ".html"))]
        command += ["--portfolio"] if stem == "portfolio" else ["--count", "430" if stem == "organization" else "73"]
        oracle = subprocess.run(command, cwd=root, capture_output=True, text=True)
        item["sourceOraclePassed"] = oracle.returncode == 0
        audit_path = reviews / (run.name + "-independent.json")
        browser = subprocess.run(["uv", "run", "--script", "skills/hierarchy-lens/scripts/audit_explorer.py", str(base / (stem + ".html")), "--report", str(audit_path)], cwd=root, capture_output=True, text=True)
        item["independentBrowserPassed"] = browser.returncode == 0
        if browser.returncode or oracle.returncode:
            item["independentFailure"] = browser.stdout + browser.stderr + oracle.stdout + oracle.stderr
    collected.append(item)

groups = {}
for case in ["contract", "naturalistic", "generalization", "boundary"]:
    cohort = [r for r in collected if f"-v2-{case}-" in r["runId"]]
    groups[case] = {"runs": len(cohort), "passes": sum(r["passed"] and r["tracePassed"] and r.get("sourceOraclePassed", True) and r.get("independentBrowserPassed", True) for r in cohort)}
routing_path = runs / "hierarchy-lens-routing-20260925-luna-1/result.json"
routing = json.loads(routing_path.read_text(encoding="utf-8")) if routing_path.exists() else {"passed": False}
passed = groups["contract"]["passes"] == 1 and groups["boundary"]["passes"] == 1 and all(groups[c]["runs"] == 3 and groups[c]["passes"] >= 2 for c in ["naturalistic", "generalization"]) and routing["passed"]
summary = {"date": "2026-09-25", "passed": passed, "cohorts": groups, "routing": routing, "runs": collected}
(destination / "validation-20260925.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
print(json.dumps({key: value for key, value in summary.items() if key != "runs"}))
raise SystemExit(0 if passed else 1)
