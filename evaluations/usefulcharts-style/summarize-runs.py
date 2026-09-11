#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Retain compact outcomes and read-surface evidence for every poster skill trial."""

import argparse
import hashlib
import json
from pathlib import Path


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runs",type=Path,required=True)
    parser.add_argument("--output",type=Path,required=True)
    args=parser.parse_args();rows=[]
    for run in sorted(args.runs.glob("usefulcharts-*")):
        result_file=run/"evaluation-result.json"
        if not result_file.exists():continue
        result=json.loads(result_file.read_text(encoding="utf-8"))
        manifest=json.loads((run/"run-manifest.json").read_text(encoding="utf-8"))
        events=json.loads((run/"event-check.json").read_text(encoding="utf-8"))
        calls=events.get("calls",[])
        errors=[];provider_errors=[]
        for line in (run/"events.jsonl").read_text(encoding="utf-8").splitlines():
            event=json.loads(line)
            if event.get("type")=="tool_execution_end" and event.get("isError"):
                errors.extend(block.get("text","")[:1500] for block in event.get("result",{}).get("content",[]) if block.get("type")=="text")
            if event.get("type")=="message_end" and event.get("message",{}).get("errorMessage"):
                provider_errors.append(event["message"]["errorMessage"])
        ambient_git=any("git status" in (c.get("command") or "") for c in calls)
        rows.append({"run_id":run.name,"harness_passed":result["passed"],"reviewed_isolation_passed":not ambient_git,
            "duration_seconds":result["durationSeconds"],"gates":result["gates"],"model":manifest["pi"]["model"],
            "skill":manifest["skill"],"observed_models":events.get("observedModels"),"tool_error_count":sum(bool(c.get("isError")) for c in calls),
            "tool_errors":errors,"provider_errors":provider_errors,"ambient_git_status":ambient_git,
            "read_paths":sorted({c["path"] for c in calls if c.get("tool")=="read" and c.get("path")}),
            "events_sha256":hashlib.sha256((run/"events.jsonl").read_bytes()).hexdigest()})
    report={"date":"2026-09-11","skill":"usefulcharts-style","trials":rows,"count":len(rows),
        "note":"Harness success is not a visual or release pass. Review independent content checks, images, and isolation separately."}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"trials":len(rows),"harness_passes":sum(r["harness_passed"] for r in rows),"provider_blocked":sum(bool(r["provider_errors"]) for r in rows)}))


if __name__=="__main__":
    main()
