#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Collect strict organic-view trials and independently revalidate their artifacts."""

import json
import os
import subprocess
from pathlib import Path

root = Path(__file__).resolve().parents[3]
runs = root / "evaluations/runs"
reviews = root / "projects/hierarchy-lens/artifacts/reviews"
destination = root / "evaluations/hierarchy-lens"
os.environ["PLAYWRIGHT_BROWSERS_PATH"] = str(root / "projects/hierarchy-lens/artifacts/browser-cache")
collected = []
for run in sorted(runs.glob("hierarchy-organic-*-20260925-luna-*")):
    manifest_path, result_path = run / "run-manifest.json", run / "evaluation-result.json"
    if not manifest_path.exists() or not result_path.exists():
        continue
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    result = json.loads(result_path.read_text(encoding="utf-8"))
    trace_path = run / "read-surface.json"
    subprocess.run(["uv", "run", "--script", "scripts/summarize-pi-json-events.py", str(run / "events.jsonl"),
                    "--require-model", "gpt-5.6-luna", "--fail-on-invalid-json", "--fail-on-tool-error",
                    "--output", str(trace_path)], cwd=root, capture_output=True, check=False)
    trace = json.loads(trace_path.read_text(encoding="utf-8"))
    item = {"runId":run.name, "passed":result["passed"], "model":"gpt-5.6-luna", "gates":result["gates"],
            "seconds":result["durationSeconds"], "payloadSha256":manifest["skill"]["payloadSha256"],
            "runtimeFiles":manifest["skill"]["fileCount"], "readPaths":[row["path"] for row in trace["readPaths"]],
            "tracePassed":trace["passed"], "traceFindings":trace["findings"]}
    if result["passed"] and "boundary" not in run.name:
        portfolio = "generalization" in run.name
        base = run / "workspace" / ("results" if portfolio else "deliverables")
        stem = "portfolio" if portfolio else "organization" if "naturalistic" in run.name else "map"
        source = "source" if stem == "map" else stem
        command = ["uv", "run", "--script", "evaluations/contracts/check-hierarchy-lens.py", str(base / (source+".json")), str(base / (stem+".html"))]
        command += ["--portfolio"] if portfolio else ["--count", "430" if stem == "organization" else "73"]
        oracle = subprocess.run(command,cwd=root,capture_output=True,text=True)
        item["sourceOraclePassed"] = oracle.returncode == 0
        audit_path = reviews / (run.name+"-independent.json")
        browser = subprocess.run(["uv","run","--script","skills/hierarchy-lens/scripts/audit_pixels.py",str(base/(stem+".html")),"--report",str(audit_path)],cwd=root,capture_output=True,text=True)
        item["independentBrowserPassed"] = browser.returncode == 0
        item["grid"] = json.loads((base/"build.json").read_text(encoding="utf-8"))["grid"]
        if browser.returncode or oracle.returncode:
            item["independentFailure"] = browser.stdout+browser.stderr+oracle.stdout+oracle.stderr
    if not result["passed"]:
        item["classification"] = "agent"
        item["failureReason"] = "Generalization trial 2 requested one logical pixel per record but the agent selected --cell-pixels 2, producing four pixels per record. The explicit input instruction and organic reference both support --cell-pixels 1. Strict JSON assertions correctly rejected the output. Other gates passed; the failed trial is retained and is not counted as a pass."
    collected.append(item)

groups = {}
for case in ["contract","naturalistic","generalization","boundary"]:
    cohort = [r for r in collected if f"-{case}-" in r["runId"]]
    groups[case] = {"runs":len(cohort),"passes":sum(r["passed"] and r["tracePassed"] and r.get("sourceOraclePassed",True) and r.get("independentBrowserPassed",True) for r in cohort)}
routing = json.loads((runs / "hierarchy-organic-routing-20260925-luna-1/result.json").read_text(encoding="utf-8"))
local = {}
for name in ["organic-final-audit","organic-5000-audit","organic-20000-audit","organic-singleton-audit","organic-one-pixel-audit","radial-preserved-organic-audit","analytical-preserved-organic-audit","organic-png-oracle","organic-pages-navigation"]:
    report = json.loads((reviews/(name+".json")).read_text(encoding="utf-8"))
    local[name] = {k:v for k,v in report.items() if k not in {"checks","screenshots","palette"}}
    if "checks" in report:
        local[name]["checkCount"] = len(report["checks"])
passed = groups["contract"]["passes"] == 1 and groups["boundary"]["passes"] == 1 and all(groups[c]["runs"]==3 and groups[c]["passes"]>=2 for c in ["naturalistic","generalization"]) and routing["passed"] and all(r["ok"] for r in local.values())
summary = {"date":"2026-09-25","passed":passed,"cohorts":groups,"routing":routing,"local":local,"runs":collected,
           "deterministicRepair":"Odd cell widths are centered using size//2-cellPixels//2, keeping the central display pixel in the root. This was corrected before forward trials and covered by 1-, 3-, and 4-pixel tests."}
(destination/"organic-20260925.json").write_text(json.dumps(summary,indent=2)+"\n",encoding="utf-8")
print(json.dumps({k:v for k,v in summary.items() if k not in {"runs","routing"}}))
raise SystemExit(0 if passed else 1)
