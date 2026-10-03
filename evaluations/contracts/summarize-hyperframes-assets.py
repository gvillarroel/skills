#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Run: uv run --script evaluations/contracts/summarize-hyperframes-assets.py --output <summary.json>."""
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig")) if path.is_file() else None


def classify(result, independent, manual):
    if not result["passed"]:
        if not result["gates"].get("events"): return "agent-workflow"
        return "agent-output"
    if independent is not None and not independent["ok"]: return "independent-contract"
    if manual is not None and not manual.get("ok"): return "visual-semantic"
    if independent is None or manual is None: return "review-pending"
    return "pass"


def main():
    parser=argparse.ArgumentParser();parser.add_argument("--output",required=True);args=parser.parse_args()
    runs=[]
    for folder in sorted((ROOT/"evaluations/runs").glob("20261002-hyperframes-*-luna6-*")):
        if not ("hyperframes-assets-" in folder.name or "hyperframes-vehicle-assets-" in folder.name): continue
        manifest=read(folder/"run-manifest.json");result=read(folder/"evaluation-result.json")
        if not manifest or not result: continue
        events=read(folder/"event-check.json") or {};independent=read(folder/"independent.json");manual=read(folder/"manual.json")
        runs.append({"id":folder.name,"payload":manifest["skill"],"requestedModel":manifest.get("model",manifest.get("pi",{}).get("model")),
                     "observedModels":events.get("observedModels",[]),"thinking":manifest.get("pi",{}).get("thinking"),"strict":result,
                     "failureClassification":classify(result,independent,manual),
                     "toolFindings":events.get("findings",[]),"independent":None if independent is None else {"ok":independent["ok"],"findings":independent.get("findings",[])},
                     "manual":manual,"jointPass":bool(result["passed"] and independent and independent["ok"] and manual and manual.get("ok")),
                     "evidenceDirectory":str(folder.relative_to(ROOT)).replace("\\","/")})
    groups={}
    for run in runs:
        case="vehicle" if "vehicle-assets" in run["id"] else "inlet"
        key=(case,run["payload"]["payloadSha256"])
        group=groups.setdefault(key,{"case":case,"payloadSha256":key[1],"runs":[],"strictPasses":0,"independentPasses":0,"manualPasses":0,"jointPasses":0})
        group["runs"].append(run["id"]);group["strictPasses"]+=int(run["strict"]["passed"])
        group["independentPasses"]+=int(bool(run["independent"] and run["independent"]["ok"]))
        group["manualPasses"]+=int(bool(run["manual"] and run["manual"].get("ok")))
        group["jointPasses"]+=int(run["jointPass"])
    report={"schemaVersion":1,"date":"2026-10-02","skill":"hyperframes-explainer","modelPolicy":"Develop with gpt-6.1-sol; validate with gpt-6-luna. No Sol substitution for a failed Luna gate.",
            "attempts":len(runs),"cohorts":list(groups.values()),"runs":runs,
            "evidencePolicy":"Retain failed attempts. Strict, independent and manual checks must pass jointly on the same frozen payload."}
    output=Path(args.output).resolve();output.parent.mkdir(parents=True,exist_ok=True);output.write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"output":str(output),"attempts":len(runs),"cohorts":len(groups)}))


if __name__=="__main__":main()
