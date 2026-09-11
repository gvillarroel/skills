#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Run a metadata-only routing control without forced skill loading."""

import argparse
import hashlib
import importlib.util
import json
import subprocess
from pathlib import Path


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-id",default="usefulcharts-routing-20260911-spark-1")
    args=parser.parse_args()
    root=Path(__file__).resolve().parents[2]
    spec=importlib.util.spec_from_file_location("pi_eval",root/"scripts/run-pi-skill-eval.py")
    harness=importlib.util.module_from_spec(spec);spec.loader.exec_module(harness)
    run=root/"evaluations/runs"/args.run_id
    workspace=run/"workspace";workspace.mkdir(parents=True,exist_ok=False)
    metadata={}
    for name in ("usefulcharts-style","mermaid","d3"):
        header=(root/"skills"/name/"SKILL.md").read_text(encoding="utf-8").split("---",2)[1]
        description=next(line.split(":",1)[1].strip() for line in header.splitlines() if line.startswith("description:"))
        metadata[name]=description
    questions={
        "q1":"Create a UsefulCharts-like wall poster of a royal genealogy, including marriages and uncertain parentage.",
        "q2":"Compare three civilizations on one vertical year scale with colored interval ribbons and compact historical annotations.",
        "q3":"Draw an original educational poster showing the branching history of scientific schools, with category-colored families and influence arrows.",
        "q4":"Write a small Mermaid sequence diagram of a browser calling an API and receiving JSON.",
        "q5":"Build an interactive D3 scatterplot of a CSV dataset with brushing and linked histograms.",
        "q6":"Explain in one sentence what a great-grandparent is; no chart or artifact is needed.",
        "q7":"Turn these institution splits and mergers into a dense chronological lineage poster in the UsefulCharts visual tradition.",
        "q8":"Correct the spelling in this paragraph without changing its meaning; do not create a visual.",
    }
    expected={"q1":"usefulcharts-style","q2":"usefulcharts-style","q3":"usefulcharts-style","q4":"mermaid","q5":"d3","q6":"none","q7":"usefulcharts-style","q8":"none"}
    prompt="Choose the single best skill for each request using only the descriptions below. Use 'none' when none is appropriate. Do not perform the requests or read any skill files. Write routing.json in the workspace as a JSON mapping of each question ID to one exact skill name.\n\nDescriptions:\n"+json.dumps(metadata,indent=2)+"\n\nRequests:\n"+json.dumps(questions,indent=2)
    (run/"prompt.md").write_text(prompt,encoding="utf-8")
    command=[*harness.pi_command_prefix(),"--model","openai-codex/gpt-5.3-codex-spark","--thinking","high","--mode","json","--no-context-files","--no-extensions","--no-skills","--no-prompt-templates","--no-themes","--no-session","--print","Read ../prompt.md first and complete its metadata-only classification. Do not inspect any other location."]
    with (run/"events.jsonl").open("w",encoding="utf-8") as out,(run/"stderr.txt").open("w",encoding="utf-8") as err:
        result=subprocess.run(command,cwd=workspace,stdout=out,stderr=err,timeout=180)
    actual=json.loads((workspace/"routing.json").read_text(encoding="utf-8"))
    observed=harness.collect_observed_models(run/"events.jsonl")
    correct=sum(actual.get(k)==v for k,v in expected.items())
    report={"status":"pass" if correct==len(expected) and result.returncode==0 and observed==[{"provider":"openai-codex","model":"gpt-5.3-codex-spark"}] else "fail",
        "correct":correct,"total":len(expected),"expected":expected,"actual":actual,"observed_models":observed,
        "forced_skill":False,"metadata_only":True,"scope":"Classification of eight supplied requests; not an end-to-end Codex discovery test.",
        "command":command,"sha256":hashlib.sha256((workspace/"routing.json").read_bytes()).hexdigest()}
    (run/"routing-review.json").write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(report))
    return 0 if report["status"]=="pass" else 1


if __name__=="__main__":
    raise SystemExit(main())
