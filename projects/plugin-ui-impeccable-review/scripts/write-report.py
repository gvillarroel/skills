#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Write scoped source-review and UI validation evidence."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PROJECT = ROOT / "projects/plugin-ui-impeccable-review"
NAMES = ["desktop-plugin-ui", "desktop-chat-plugin-ui", "code-native-plugin-ui", "pi-extension-ui", "codex-plugin-ui", "chatgpt-desktop-plugin-ui", "gemini-enterprise-ui"]

def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))

def main():
    snapshot = read(PROJECT / "artifacts/source/snapshot.json")
    sources = []
    for p in sorted((PROJECT / "artifacts/source/skill/reference").glob("*.md")):
        sources.append({"path": "skill/reference/" + p.name, "sha256": hashlib.sha256(p.read_bytes()).hexdigest()})
    suites = {}
    for name, p in {"functionalBrowserAndSdk": ROOT / "projects/plugin-ui-micro-decisions/artifacts/reviews/browser/impeccable-first/review.json", "targetedQuality": PROJECT / "artifacts/reviews/quality/review.json"}.items():
        d = read(p)
        suites[name] = {"passed": d["passed"], "checks": len(d["checks"]), "report": p.relative_to(ROOT).as_posix(), "scope": d["scope"]}
    forwards = []
    for name in NAMES:
        run_id = f"20261112-impeccable-ui-{name}-sol-2"
        run = ROOT / "evaluations/runs" / run_id
        result, event, trace = read(run / "evaluation-result.json"), read(run / "event-check.json"), read(run / "trace-summary.json")
        output = read(run / "workspace/quality-review.json")
        valid = set(output) == {"initialDesignReview", "priorityOrder", "targetedChanges", "mechanicalChecks", "hostBoundaries"}
        if not valid:
            raise ValueError(f"Contract shape failed: {name}")
        forwards.append({"skill": name, "runId": run_id, "strictPassed": result["passed"], "eventPassed": event["passed"], "tracePassed": trace["passed"], "artifactShapePassed": valid, "model": "openai-codex/gpt-6.1-sol", "thinking": "medium", "scope": "One contract case; no new actual-host support or deployment claim."})
    changed = [ROOT / f"skills/{name}/references/micro-decisions.md" for name in NAMES]
    changed += [ROOT / "projects/plugin-ui-micro-decisions/web" / p for p in ["app.mjs", "styles.css"]]
    report = {"schemaVersion": 1, "date": "2026-11-12", "upstream": {"repository": "https://github.com/pbakaus/impeccable", "commit": snapshot["commit"], "commitDate": snapshot["commitDate"], "sourceFiles": sources, "method": "Selective primary-source review, independent paraphrase and local checks. No formal upstream command/detector execution or code redistribution."}, "suites": suites, "forwards": forwards, "preflightFailures": {"count": 7, "modelStarted": False, "cause": "Expanded references passed 100 lines without a contents section. Added local contents navigation before the sol-2 runs.", "logs": "projects/plugin-ui-impeccable-review/artifacts/eval-<skill>.log"}, "manualReview": {"beforeMechanical": "Identified repeated action-color fill on diagram subjects, fixed-size reading text, ambiguous generic action copy, and overlapping pointer/focus frames.", "actualIntegratedBrowser": "Observed 542x767, browser-default 16px root, one question, no global navigation, subject outline and contextual Use Data integration action.", "limits": "Controlled SDK bridge and standalone IAB remain distinct from stock-host continuation. Native source is unchanged. 200% root-font scaling is not browser UI zoom."}, "sourceSha256": {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in changed}}
    target = ROOT / "evaluations/desktop-plugin-ui/impeccable-20261112.json"
    target.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"suites": suites, "strictForwards": sum(row["strictPassed"] for row in forwards)}))

if __name__ == "__main__":
    main()
