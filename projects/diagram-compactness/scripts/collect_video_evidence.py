#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Collect final strict execution and independent native video scene evidence."""
import json
from pathlib import Path
import subprocess
import sys
import xml.etree.ElementTree as ET

root=Path(__file__).resolve().parents[3]
revision=sys.argv[1] if len(sys.argv)>1 else "sol-semantic-final"
rows=[]
for case in ["contract","natural-1","natural-2","natural-3"]:
    run_id=f"compact-video-20261004-{revision}-{case}"
    run=root/"evaluations/runs"/run_id
    manifest=json.loads((run/"run-manifest.json").read_text())
    result=json.loads((run/"evaluation-result.json").read_text())
    command=["uv","run","--script",str(root/"scripts/summarize-pi-json-events.py"),
        str(run/"events.jsonl"),"--require-model","gpt-5.6-sol","--fail-on-invalid-json","--fail-on-tool-error"]
    events=subprocess.run(command,cwd=root,capture_output=True,text=True,encoding="utf-8")
    summary=json.loads(events.stdout)
    scene=json.loads((run/"workspace/source/scene-contract.json").read_text())
    independent_path=root/"projects/diagram-compactness/artifacts/reviews/video"/run_id/"independent-scene.json"
    independent=json.loads(independent_path.read_text())
    expected_labels=sorted("".join(label.itertext()) for element in scene["elements"]
        for label in ET.parse(run/"workspace"/element["src"]).iter("{http://www.w3.org/2000/svg}text"))
    full_labels=all(sorted(t["text"] for t in state["geometry"]["texts"])==expected_labels
        for state in independent["samples"])
    held=independent["heldArrowAudit"]
    visual=(independent["labelGeometryPass"] and independent["motionGeometryPass"] and full_labels
        and held["headCount"]==len(scene["interactions"]) and not held["issues"])
    rows.append({"run":run_id,"case":case,"model":manifest["pi"]["model"],
        "payloadSha256":manifest["skill"]["payloadSha256"],"strict":result,
        "summaryExitCode":events.returncode,"observedModels":summary["models"],
        "eventFindings":summary["findings"],"runtimeReadPaths":summary["readPaths"],
        "independent":{"passed":visual,"labels":expected_labels,"fullLabels":full_labels,
            "sampleCount":len(independent["samples"]),"labelGeometryPass":independent["labelGeometryPass"],
            "motionGeometryPass":independent["motionGeometryPass"],"heldHeadCount":held["headCount"],
            "heldShaftCount":held["shaftCount"],"minimumArrowContrast":min(r["minimum"] for r in held["records"]),
            "minimumTokenClearance":min(s["geometry"]["minimumTokenClearance"] for s in independent["samples"] if s["geometry"]["minimumTokenClearance"] is not None),
            "pageErrors":independent["pageErrors"],"evidence":independent_path.relative_to(root).as_posix()}})
out=root/"evaluations/diagram-compactness"/f"video-{revision}-20261004.json"
out.write_text(json.dumps({"skill":"video","revision":revision,"rows":rows},indent=2)+"\n",encoding="utf-8")
print(json.dumps({"digests":sorted({r["payloadSha256"] for r in rows}),
    "cases":[{"case":r["case"],"strict":r["strict"]["passed"],"events":r["summaryExitCode"]==0,
        "independent":r["independent"]["passed"]} for r in rows],"evidence":str(out)}))
