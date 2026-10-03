#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Retain compact evidence for every member of the fixed Luna cohort."""

import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[3]
LOCAL = ROOT / "projects/svg-text-contrast/artifacts"
DESTINATION = ROOT / "evaluations/compose-synchronized-svg/text-contrast-20260904"


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    cohort = read(LOCAL / "luna-cohort.json")
    DESTINATION.mkdir(parents=True, exist_ok=True)
    runs = []
    for row in cohort:
        directory = ROOT / "evaluations/runs" / row["runId"]
        result = read(directory / "evaluation-result.json")
        manifest = read(directory / "run-manifest.json")
        trace = DESTINATION / f'{row["case"]}-read-surface.json'
        command = ["uv", "run", "--script", "scripts/summarize-pi-json-events.py", str(directory / "events.jsonl"),
                   "--output", str(trace), "--require-model", "gpt-5.6-luna", "--require-tool-call",
                   "--fail-on-invalid-json", "--fail-on-tool-error", "--require-read", "../prompt.md",
                   "--forbid-read-regex", r"(?i)(^|[\\/])assets[\\/]examples([\\/]|$)"]
        with (LOCAL / f'{row["case"]}-trace-review.log').open("w", encoding="utf-8") as log:
            summarized = subprocess.run(command, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT, check=False)
        outputs = directory / "workspace/outputs"
        authoring_findings = []
        for line in (directory / "events.jsonl").read_text(encoding="utf-8").splitlines():
            event = json.loads(line)
            if event.get("type") == "tool_execution_end":
                for item in event.get("result", {}).get("content", []):
                    if item.get("type") == "text":
                        authoring_findings.extend(re.findall(r'"finding":\s*"((?:[^"\\]|\\.)*)"', item.get("text", "")))
        reports = {}
        for path in outputs.rglob("*.json"):
            if path.name in {"browser.json", "static.json", "preflight.json"}:
                report = read(path)
                reports[path.relative_to(outputs).as_posix()] = {
                    "ok": report.get("ok"), "finding": report.get("finding"),
                    "textContrast": {k: v for k, v in report.get("metrics", {}).items() if k.startswith("textContrast")}}
        runs.append({**row, "result": result, "skillIntegrity": read(directory / "skill-integrity-check.json"),
                     "expectedAuthoringFindings": authoring_findings,
                     "prompt": manifest.get("prompt"), "reports": reports, "traceExitCode": summarized.returncode,
                     "traceUsage": read(trace).get("usageTotals"), "artifactHashes": {
                         path.relative_to(outputs).as_posix(): digest(path) for path in outputs.rglob("*") if path.is_file()}})
    cases = []
    for name in ("world-light", "near-threshold", "compact-dark", "light-mark"):
        browser = read(LOCAL / name / "browser-after.json")
        cases.append({"case": name, "ok": browser["ok"], "checkSummary": browser["checkSummary"],
                      "textContrast": {k: v for k, v in browser["metrics"].items() if k.startswith("textContrast")},
                      "hashes": {file: digest(LOCAL / name / file) for file in ("brief.json", "plan.json", "before.svg", "after.svg")}})
    record = {"date": "2026-09-04", "model": "openai-codex/gpt-5.6-luna", "runs": runs,
              "independentLunaChecks": read(LOCAL / "luna-independent.json"),
              "controlledInitialViews": read(LOCAL / "case-results.json"), "controlledFullAudits": cases,
              "baselineSources": {path.name: digest(path) for path in (LOCAL / "before").glob("*.py")},
              "comparisonBrowser": read(LOCAL / "comparison-browser.json")}
    (DESTINATION / "results.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    for source, target in (("luna-review.md", "discovery-review.md"), ("final-review.md", "final-visual-review.md"), ("final-review.json", "final-visual-review.json")):
        shutil.copyfile(LOCAL / source, DESTINATION / target)
    print(json.dumps({"runs": len(runs), "passed": sum(row["result"]["passed"] for row in runs), "path": str(DESTINATION)}))


if __name__ == "__main__":
    main()
