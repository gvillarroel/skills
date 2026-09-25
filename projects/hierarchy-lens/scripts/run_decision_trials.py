#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Launch fresh strict decision-composition cohorts with exact output contracts."""

import argparse
import os
import subprocess
from pathlib import Path

parser=argparse.ArgumentParser()
parser.add_argument("case",choices=["contract","naturalistic","generalization","boundary"])
parser.add_argument("--revision",default="v2",help="Fresh cohort identifier, retained in every run ID")
args=parser.parse_args()
root=Path(__file__).resolve().parents[3]
os.environ["PLAYWRIGHT_BROWSERS_PATH"]=str(root/"projects/hierarchy-lens/artifacts/browser-cache")
case=args.case
prompt="hierarchy-lens-boundary" if case=="boundary" else "hierarchy-decisions-"+case
count={"contract":73,"naturalistic":430,"generalization":8}.get(case)
folder="results" if case=="generalization" else "deliverables"
stem={"contract":"map","naturalistic":"organization","generalization":"portfolio"}.get(case)
outputs=["review.json","review.md"] if case=="boundary" else [f"{folder}/{stem}.html",f"{folder}/{'source' if case=='contract' else stem}.json",f"{folder}/build.json",f"{folder}/audit.json",f"{folder}/overview.png"]
fields=["review.json::canBuild=false"] if case=="boundary" else [f"{folder}/build.json::nodes={count}",f"{folder}/build.json::decisions={count}",f"{folder}/build.json::view=decision",f"{folder}/build.json::minPixelsPerRecord={1 if case=='generalization' else 4}",f"{folder}/build.json::maxPixelsPerRecord={1 if case=='generalization' else 4}",f"{folder}/audit.json::ok=true"]
if case in {"naturalistic","generalization"}:
    fields += [f"{folder}/build.json::composition.priority.direction=descending",f"{folder}/build.json::composition.eligibility={'parent' if case=='generalization' else 'generation'}"]
if case=="generalization":
    fields += [f"{folder}/build.json::composition.weights.{key}={value}" for key,value in {"parent":4,"affinity":3,"compactness":2,"radial":1}.items()]
    fields.append(f"{folder}/build.json::composition.frontierWindow=2")
failed=False
for trial in range(1,4 if case in {"naturalistic","generalization"} else 2):
    command=["uv","run","--script","scripts/run-pi-skill-eval.py","hierarchy-lens","--prompt-file",f"evaluations/pi-prompts/{prompt}.md","--model","openai-codex/gpt-5.6-luna","--mode","json","--strict","--run-id",f"hierarchy-decisions-{case}-20260925-luna-{args.revision}-{trial}","--timeout-seconds","300"]
    for output in outputs:command.extend(["--expect-output",output])
    for field in fields:command.extend(["--expect-output-json-field",field])
    if case=="contract":command.append("--require-exact-command-from-prompt")
    result=subprocess.run(command,cwd=root)
    failed |= result.returncode!=0
raise SystemExit(1 if failed else 0)
