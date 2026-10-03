#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Preserve every completed attempt, strict gates, provenance and read surfaces."""
import argparse
import json
import subprocess
from pathlib import Path


def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig")) if path.is_file() else None


def compact_grade(grade):
    if grade is None:
        return None
    result = {key: grade[key] for key in ["ok", "case", "findings", "checks", "changedGeometry", "screenshot"] if key in grade}
    if "observations" in grade:
        result["observationCount"] = len(grade["observations"])
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[2]
    rows = []
    for run in sorted((root / "evaluations/runs").glob("20261002-hyperframes-explainer-*")):
        result = read(run / "evaluation-result.json")
        manifest = read(run / "run-manifest.json")
        if not result:
            if (run / "result.json").is_file():
                route = read(run / "result.json")
                rows.append({"run": run.name, "kind": "routing", "passed": route["ok"], "checks": f"{route['passed']}/{route['total']}"})
            else:
                rows.append({"run": run.name, "pending": True,
                             "createdAtUtc": manifest.get("createdAtUtc") if manifest else None,
                             "model": manifest["pi"]["model"] if manifest else None,
                             "payloadSha256": manifest["skill"]["payloadSha256"] if manifest else None})
            continue
        events = read(run / "event-check.json") or {}
        model = manifest["pi"]["model"].split("/")[-1]
        summary_path = run / "read-surface.json"
        command = ["uv", "run", "--script", str(root / "scripts/summarize-pi-json-events.py"), str(run / "events.jsonl"),
                   "--output", str(summary_path), "--require-model", model, "--require-tool-call", "--fail-on-invalid-json", "--fail-on-tool-error"]
        trace = subprocess.run(command, cwd=root, capture_output=True, text=True)
        summary = read(summary_path) or {}
        findings = events.get("findings", [])
        classification = None
        if not result["passed"]:
            classification = "infrastructure" if model == "gpt-5.3-codex-spark" else "harness" if result.get("timedOut") or any(f.get("code") == "no-fenced-command-in-prompt" for f in findings) else "agent"
        rows.append({"run": run.name, "passed": result["passed"], "failureClassification": classification,
                     "createdAtUtc": manifest["createdAtUtc"],
                     "model": manifest["pi"]["model"], "payloadSha256": manifest["skill"]["payloadSha256"],
                     "durationSeconds": result.get("durationSeconds"), "timedOut": result.get("timedOut", False), "gates": result.get("gates", {}),
                     "requiredOutputs": manifest["expectedOutputs"], "eventFindings": findings,
                     "tracePassed": trace.returncode == 0, "observedModels": summary.get("models", {}),
                     "readPaths": [r["path"] for r in summary.get("readPaths", [])],
                     "totalReadResultBytes": summary.get("totalReadResultBytes"),
                     "toolErrors": [c for c in events.get("calls", []) if c["isError"]],
                     "independent": compact_grade(read(run / "independent.json")),
                     "independentReport": f"evaluations/runs/{run.name}/independent.json" if (run / "independent.json").is_file() else None,
                     "manual": read(run / "manual.json")})
    release = {}
    for case in ["naturalistic", "generalization"]:
        attempts = [r for r in rows if f"release-{case}-" in r["run"]]
        latest = max(attempts, key=lambda r: r.get("createdAtUtc") or "") if attempts else {}
        trials = [r for r in attempts if r.get("payloadSha256") == latest.get("payloadSha256") and r.get("model") == latest.get("model")]
        complete = [r for r in trials if not r.get("pending")]
        passed = [r for r in complete if r.get("passed") and (r.get("independent") or {}).get("ok")]
        joint = [r for r in passed if (r.get("manual") or {}).get("ok")]
        release[case] = {"payloadSha256": latest.get("payloadSha256"), "model": latest.get("model"), "runs": [r["run"] for r in trials],
                         "allRecordedAttempts": len(attempts), "complete": len(complete), "total": len(trials), "strictAndIndependentPasses": len(passed),
                         "jointPasses": len(joint), "thresholdMet": len(complete) >= 3 and len(joint) >= 2}
    output = (root / args.output).resolve(); output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps({"skill": "hyperframes-explainer", "date": "2026-10-02", "releaseCohorts": release, "runs": rows}, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(output), "runs": len(rows), "releaseCohorts": release}))


if __name__ == "__main__":
    main()
