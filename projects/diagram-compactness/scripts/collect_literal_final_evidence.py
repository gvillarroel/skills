#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Retain bounded evidence from completed literal-caption consumer cohorts."""
from pathlib import Path
import json
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
skill = sys.argv[1]
revision = sys.argv[2] if len(sys.argv) > 2 else "sol-literal-final"
case_filter = sys.argv[3] if len(sys.argv) > 3 else "all"
rows = []
for case in ["contract", "natural-1", "natural-2", "natural-3"]:
    if case_filter != "all" and not case.startswith(case_filter):
        continue
    name = f"compact-{skill}-20261004-{revision}-{case}"
    run = ROOT / "evaluations/runs" / name
    manifest = json.loads((run / "run-manifest.json").read_text(encoding="utf-8"))
    result = json.loads((run / "evaluation-result.json").read_text(encoding="utf-8"))
    summary_command = ["uv", "run", "--script", str(ROOT / "scripts/summarize-pi-json-events.py"), str(run / "events.jsonl"), "--require-model", "gpt-5.6-sol", "--fail-on-invalid-json", "--fail-on-tool-error"]
    process = subprocess.run(summary_command, cwd=ROOT, capture_output=True, text=True, encoding="utf-8")
    (run / "independent-event-summary.json").write_text(process.stdout, encoding="utf-8")
    events = json.loads(process.stdout)
    review_folder = ROOT / "projects/diagram-compactness/artifacts/reviews" / name
    independent = review_folder / ("independent-deck" if skill == "slidev-echarts" and case.startswith("natural") else "independent-native") / "browser.json"
    browser = json.loads(independent.read_text(encoding="utf-8")) if independent.exists() else None
    compact_browser = None
    if browser:
        compact_browser = {"ok": browser["ok"], "pageErrors": browser["pageErrors"], "findings": browser.get("findings", []), "states": []}
        for state in browser["states"]:
            graphs = state.get("graphs", [state])
            compact_browser["states"].append({"state": state["state"], "kind": state.get("kind"), "viewport": state.get("viewport"), "graphs": [{"width": graph.get("width", graph.get("bounds", {}).get("width")), "height": graph.get("height", graph.get("bounds", {}).get("height")), "nodeCount": len(graph["nodes"]), "headCount": len(graph["heads"]), "minimumHeadGap": min((head["gap"] for head in graph["heads"]), default=None), "labels": [label["text"] for label in graph["labels"]], "fontSizes": sorted({label["fontSize"] for label in graph["labels"]}), "textOverlaps": graph["textOverlaps"]} for graph in graphs]})
    live_path = review_folder / "independent-native/live-option-browser.json"
    live = json.loads(live_path.read_text(encoding="utf-8")) if live_path.exists() else None
    compact_live = None
    if live:
        compact_live = {"ok": live["ok"], "pageErrors": live["pageErrors"], "findings": live["findings"], "states": [{"state": state["state"], "helper": state["helper"], "repeat": state["repeat"], "graphs": [{"nodeCount": len(graph["nodes"]), "headCount": len(graph["heads"]), "labels": [label["text"] for label in graph["labels"]], "minimumHeadGap": min((head["gap"] for head in graph["heads"]), default=None), "textOverlaps": graph["textOverlaps"]} for graph in state["graphs"]]} for state in live["states"]]}
    manual_path = independent.with_name("manual-review.json")
    manual = json.loads(manual_path.read_text(encoding="utf-8")) if manual_path.exists() else None
    rows.append({"run": name, "case": case, "payloadSha256": manifest["skill"]["payloadSha256"], "model": manifest["pi"]["model"], "strict": result, "eventSummaryExitCode": process.returncode, "observedModels": events["models"], "eventFindings": events["findings"], "runtimeReadPaths": events["readPaths"], "independentBrowser": compact_browser, "independentBrowserPath": independent.relative_to(ROOT).as_posix(), "independentLiveOption": compact_live})
    if manual is not None:
        rows[-1]["independentManualVisualReview"] = manual
        rows[-1]["jointPass"] = bool(result["passed"] and browser and browser["ok"] and manual["passed"] and (live is None or live["ok"]))
out = ROOT / "evaluations/diagram-compactness" / f"{skill}-{revision}-20261004.json"
out.write_text(json.dumps({"skill": skill, "revision": revision, "rows": rows}, indent=2), encoding="utf-8")
print(json.dumps({"skill": skill, "digests": sorted({row["payloadSha256"] for row in rows}), "cases": [{"case": row["case"], "strict": row["strict"]["passed"], "eventSummary": row["eventSummaryExitCode"] == 0, "independentBrowser": row["independentBrowser"].get("ok") if row["independentBrowser"] else None, "independentManualVisual": row.get("independentManualVisualReview", {}).get("passed"), "jointPass": row.get("jointPass")} for row in rows], "evidence": str(out)}))
