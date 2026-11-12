#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Write a compact evidence inventory without copying raw host/profile data."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PROJECT = ROOT / "projects/plugin-ui-complex-workbenches"
NAMES = ["desktop-plugin-ui", "desktop-chat-plugin-ui", "code-native-plugin-ui", "pi-extension-ui", "codex-plugin-ui", "chatgpt-desktop-plugin-ui", "gemini-enterprise-ui"]

def read(path):
    return json.loads(path.read_text(encoding="utf-8"))

def main():
    suites = {}
    sources = [PROJECT / p for p in ["model.mjs", "server.mjs", "web/index.html", "web/styles.css", "web/app.mjs", "web/bridge.mjs", "pi/incident.ts"]]
    for label, relative in {
        "browserAndMcp": "artifacts/reviews/browser/sandbox-form-fix/review.json",
        "piTerminal": "artifacts/reviews/target-hosts/pi-complex-verified/review.json",
        "codexPackage": "artifacts/reviews/codex/complex-final/review.json",
    }.items():
        path = PROJECT / relative
        report = read(path)
        suites[label] = {"passed": report["passed"], "checks": len(report["checks"]), "version": report.get("version"), "report": path.relative_to(ROOT).as_posix(), "scope": report["scope"]}
    forwards = []
    for name in NAMES:
        run_id = f"20261112-complex-ui-{name}-sol-1"
        run = ROOT / "evaluations/runs" / run_id
        result, events, trace = read(run / "evaluation-result.json"), read(run / "event-check.json"), read(run / "trace-summary.json")
        workspace = run / "workspace"
        acceptance = workspace / "acceptance.json"
        review = workspace / "review.md"
        document = read(acceptance)
        words = len(review.read_text(encoding="utf-8").split())
        shape = set(document) == {"host", "dataContract", "views", "actionContract", "validation"} and words <= 550
        if not shape:
            raise ValueError(f"Contract artifacts failed independent shape review: {name}")
        forwards.append({"skill": name, "runId": run_id, "strictPassed": result["passed"], "eventPassed": events["passed"], "artifactShapePassed": shape, "reviewWords": words, "model": "openai-codex/gpt-6.1-sol", "thinking": "medium", "durationSeconds": result["durationSeconds"], "scope": "Contract/planning forward only; not live-host UI acceptance.", "traceKeys": sorted(trace)})
        sources.extend([ROOT / f"skills/{name}/SKILL.md", ROOT / f"skills/{name}/references/complex-workspaces.md"])
    screenshots = [{"path": p.relative_to(ROOT).as_posix(), "sha256": hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted((PROJECT / "artifacts/reviews").rglob("*")) if p.suffix.lower() in {".png", ".jpg"}]
    report = {
        "schemaVersion": 1, "date": "2026-11-12", "dataset": {"services": 96, "edges": 205, "scheduledSamples": 9216, "cadenceMinutes": 15, "timezone": "UTC", "synthetic": True},
        "suites": suites, "forwards": forwards,
        "manualReview": {"integratedBrowser": "Observed visible version-1/version-2 conflict; fresh review applied plan-1 once at version 3, then read authoritative browser-local state. Captured at actual allocated panel width. This was the standalone sandbox, not inline MCP App paint.", "screenshotsInspected": ["wide investigation", "542px full-page investigation", "fleet matrix", "review conflict", "actual Pi 80x32 matrix", "actual Pi 60x16 values", "actual integrated-browser conflict and acknowledgement"], "repairs": ["Bound neighborhood by measured per-column capacity", "Collapsed secondary directory on narrow panels", "Explicit full-day matrix context with active-window outline", "End-of-day axis label 24:00", "Repeated terminal time scope, units and legend; corrected hour-column alignment", "Replaced sandbox-blocked form submit with explicit action and constraint validation", "Bound idempotency to normalized payload and rechecked after await", "Added authoritative-state reconciliation control"]},
        "retainedFailures": [
            {"path": "artifacts/reviews/browser/review.json", "classification": "evaluator", "cause": "Pointer brush target was offscreen; fixed harness scrolling before real input."},
            {"path": "artifacts/reviews/browser/bridge-final/review.json", "classification": "artifact-and-evaluator", "cause": "Strict sandbox blocked ambient HTML form submission; explicit app action repaired it. Fixture also navigates to reset the previous document realm and its observer."},
            {"path": "artifacts/reviews/target-hosts/pi-complex-final/review.json", "classification": "evaluator", "cause": "Old literal legend assertion after the visible threshold wording changed; source unchanged for verified rerun."},
        ],
        "hostLimits": {"claudeDesktopChat": "New Incident Analysis server not added to personal configuration; previous installed XY evidence remains separate.", "claudeCode": "Earlier CLI login/Desktop Code onboarding gates remain; no new pane acceptance.", "chatgptDesktop": "Actual integrated-browser surface observed in current Codex mode; no new stock ChatGPT inline component acceptance.", "geminiEnterprise": "No registered target agent supplied; earlier configured-project API-disabled result remains bounded to that project. No cloud configuration changed."},
        "sourceSha256": {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in sources}, "screenshots": screenshots,
    }
    target = ROOT / "evaluations/desktop-plugin-ui/complex-workbenches-20261112.json"
    target.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"suites": suites, "strictForwards": sum(r["strictPassed"] for r in forwards), "screenshots": len(screenshots)}))

if __name__ == "__main__":
    main()
