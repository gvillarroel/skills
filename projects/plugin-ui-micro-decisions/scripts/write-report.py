#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Write compact micro-decision evidence with explicit continuation boundaries."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PROJECT = ROOT / "projects/plugin-ui-micro-decisions"
NAMES = ["desktop-plugin-ui", "desktop-chat-plugin-ui", "code-native-plugin-ui", "pi-extension-ui", "codex-plugin-ui", "chatgpt-desktop-plugin-ui", "gemini-enterprise-ui"]

def read(path):
    return json.loads(path.read_text(encoding="utf-8"))

def main():
    suites = {}
    for label, relative in {"browserAndSdk": "artifacts/reviews/browser/compact-final/review.json", "piTerminal": "artifacts/reviews/target-hosts/pi-micro-final/review.json", "codexPackage": "artifacts/reviews/codex/micro-final/review.json"}.items():
        p = PROJECT / relative
        d = read(p)
        suites[label] = {"passed": d["passed"], "checks": len(d["checks"]), "version": d.get("version"), "report": p.relative_to(ROOT).as_posix(), "scope": d["scope"]}
    forwards = []
    sources = [PROJECT / p for p in ["decision.mjs", "server.mjs", "web/index.html", "web/styles.css", "web/app.mjs", "web/bridge.mjs", "pi/taxonomy-choice.ts"]]
    for name in NAMES:
        run_id = f"20261112-micro-ui-{name}-sol-1"
        run = ROOT / "evaluations/runs" / run_id
        result, event, trace = read(run / "evaluation-result.json"), read(run / "event-check.json"), read(run / "trace-summary.json")
        plan = read(run / "workspace/micro-plan.json")
        words = len((run / "workspace/review.md").read_text(encoding="utf-8").split())
        shape = set(plan) == {"question", "visibleElements", "optionalEvidence", "resultContract", "hostAdapter", "verification"} and words <= 400
        if not shape:
            raise ValueError(f"Independent artifact shape check failed: {name}")
        forwards.append({"skill": name, "runId": run_id, "strictPassed": result["passed"], "eventPassed": event["passed"], "tracePassed": trace["passed"], "artifactShapePassed": shape, "reviewWords": words, "model": "openai-codex/gpt-6.1-sol", "thinking": "medium", "durationSeconds": result["durationSeconds"], "scope": "Single contract case; no live-host paint or model-continuation claim."})
        sources.extend(ROOT / f"skills/{name}/{p}" for p in ["SKILL.md", "agents/openai.yaml", "references/micro-decisions.md", "references/complex-workspaces.md", "references/rich-interfaces.md"])
    sources.append(ROOT / "skills/pi-extension-ui/assets/templates/pi-command/micro-choice.ts")
    screenshots = [{"path": p.relative_to(ROOT).as_posix(), "sha256": hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted((PROJECT / "artifacts/reviews").rglob("*")) if p.suffix.lower() in {".png", ".jpg"}]
    report = {
        "schemaVersion": 1, "date": "2026-11-12", "purpose": "Correct the default from broad workspaces to one decision-relevant agent micro UI.",
        "decision": {"id": "ontology-alignment-parent", "options": ["knowledge-modeling", "data-integration"], "independentQuestions": 1, "globalNavigationElements": 0, "outcomes": ["selected", "deferred"], "editsTaxonomy": False, "synthetic": True},
        "suites": suites, "forwards": forwards,
        "visualReview": {"browser": "Inspected wide and 542px local-tree comparisons. Removed duplicated parent labels; one heading, two comparable alternatives, relevant reasons and optional scope evidence remain. Actual IAB 542x767 captured undecided, selected and returned states.", "terminal": "Inspected actual Pi 80x32 and 60x16 captures. Native accent marks active option, warning marks unresolved concept, success marks selected receipt, and muted/dim marks context. Weight, circles, checks, separators and tree connectors also encode state. Evidence returns to the same pending choice; Escape defers without a placement.", "continuation": "Real SDK iframe calls the actual MCP server, updates future model context then receives one controlled-host ui/message acknowledgement. Actual IAB is a standalone local example. Native Pi command records a model-visible result without a new turn. No stock host live model continuation was executed."},
        "retainedFailure": {"report": "artifacts/reviews/target-hosts/pi-micro-1/review.json", "classification": "evaluator", "cause": "Selected placement wrapped Data and integration across terminal rows; corrected whitespace-aware assertion. Visual/source output was correct."},
        "hostLimits": ["New MCP server not installed in personal Claude Chat configuration.", "Claude Code login/Desktop Code gates remain; native Mod paint not newly accepted.", "Current IAB is in Codex mode; no stock ChatGPT inline paint claim.", "No registered Gemini Enterprise agent supplied; catalog/A2A guidance is not a host-rendering result."],
        "sourceSha256": {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in sources}, "screenshots": screenshots,
    }
    target = ROOT / "evaluations/desktop-plugin-ui/micro-decisions-20261112.json"
    target.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"suites": suites, "strictForwards": sum(r["strictPassed"] for r in forwards), "screenshots": len(screenshots)}))

if __name__ == "__main__":
    main()
