#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""Audit native trial evidence and report predeclared descriptive family deltas."""
from collections import defaultdict
import hashlib
import json
from pathlib import Path
import random
import statistics
import sys

REPO = Path(__file__).resolve().parents[3]
ROOT = REPO / "evaluations/runs/svt1"


def read(p): return json.loads(Path(p).read_text(encoding="utf-8-sig"))
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def collect(job, expected=None):
    rows=[]
    for path in sorted(job.glob("*/result.json")):
        data=read(path); trial=path.parent
        reward=(data.get("verifier_result") or {}).get("rewards") or {}
        metrics=read(trial / "verifier/metrics.json") if (trial / "verifier/metrics.json").exists() else {}
        events=[]
        trace=trial / "agent/pi.txt"
        if trace.exists():
            for line in trace.read_text(encoding="utf-8").splitlines():
                try: events.append(json.loads(line))
                except json.JSONDecodeError: pass
        calls=[e for e in events if e.get("type")=="tool_execution_start"]
        commands="\n".join(json.dumps(e.get("args",{})) for e in calls)
        previews=[e for e in calls if e.get("toolName")=="read" and ".png" in json.dumps(e.get("args",{})).lower()]
        inp=trial / "agent/skill-input-audit.json"; integrity=trial / "agent/skill-integrity.json"
        rows.append({"trial":trial.name,"task":data["task_name"],"task_checksum":data["task_checksum"],
            "result_sha256":sha(path),"reward":reward,"exception":data.get("exception_info"),
            "renderer_used":"scripts/render_svg.py" in commands,"preview_reads":len(previews),
            "construction_guide_read":"construction-decisions.md" in commands,
            "scaffold_used":"scripts/scaffold.py" in commands,
            "input_isolated":inp.exists() and read(inp).get("reference_absent") is True,
            "skill_unchanged":integrity.exists() and read(integrity).get("unchanged") is True,
            "review_recommended":metrics.get("review_recommended"),"overall":metrics.get("choices",{}).get("overall"),
            "candidate_side":metrics.get("candidate_side"),"signed_margin":metrics.get("signed_technique_margin"),
            "agent_result":data.get("agent_result"),"agent_execution":data.get("agent_execution"),
            "verifier_path":str(trial / "verifier")})
    if expected is not None:
        assert len(rows)==expected and read(job / "result.json")["finished_at"]
    return rows


def describe(a,b):
    by_task=defaultdict(dict)
    for label,rows in [("baseline",a),("candidate",b)]:
        for task in sorted({r["task"] for r in rows}):
            scores=[r["reward"].get("technique_quality") for r in rows if r["task"]==task]
            by_task[task][label]=statistics.mean(scores) if all(isinstance(x,(int,float)) for x in scores) else None
    valid=all(not r["exception"] and r["reward"].get("artifact_valid")==1 and r["input_isolated"] and r["skill_unchanged"] for r in a+b)
    if not valid or any(v.get("baseline") is None or v.get("candidate") is None for v in by_task.values()):
        return {"complete_evaluable":False,"families":dict(by_task),"passed":False}
    for value in by_task.values():value["delta"]=value["candidate"]-value["baseline"]
    deltas=[v["delta"] for v in by_task.values()]
    rng=random.Random(20260926)
    boot=sorted(statistics.mean(rng.choices(deltas,k=len(deltas))) for _ in range(10000))
    gain=statistics.mean(deltas)
    return {"complete_evaluable":True,"families":dict(by_task),"baseline_mean":statistics.mean(v["baseline"] for v in by_task.values()),
        "candidate_mean":statistics.mean(v["candidate"] for v in by_task.values()),"mean_gain":gain,
        "family_delta_range":[min(deltas),max(deltas)],"descriptive_family_bootstrap_95_percentile":[boot[250],boot[9749]],
        "bootstrap_limitation":"Few independent groups; descriptive uncertainty, not proof of population-wide gain.",
        "passed":gain>=.02 and min(deltas)>=-.08}


def main():
    mode=sys.argv[1] if len(sys.argv)>1 else "status"
    jobs={a:ROOT / f"generation-000/candidates/{a}/harbor-jobs/harbor-pop-g000-{a}" for a in ["b","c"]}
    if mode=="status":
        print(json.dumps({a:{"terminal_trials":len(collect(j)),"job_finished":(j / "result.json").exists() and bool(read(j / "result.json").get("finished_at")),
                               "errors":sum(bool(r["exception"]) for r in collect(j))} for a,j in jobs.items()}));return
    assert mode in {"development","revision"}
    candidate="d" if mode=="revision" else "c"
    if candidate=="d":jobs={"b":jobs["b"],"d":ROOT / "jobs/d"}
    rows={a:collect(j,12) for a,j in jobs.items()}
    comparison=describe(rows["b"],rows[candidate])
    native=read(ROOT / "run.json")
    comparison["native_selected_winner"]=native["selectedWinner"]
    comparison["passed"] &= native["selectedWinner"]==candidate
    value={"comparison":comparison,"native_ranking":native["ranking"],"trial_audit":rows,
           "native_run_sha256":sha(ROOT / "run.json"),"protocol_sha256":sha(ROOT / "protocol.json")}
    with (ROOT / ("revision-supplement.json" if candidate=="d" else "development-supplement.json")).open("x",encoding="utf-8") as out:json.dump(value,out,indent=2)
    print(json.dumps(comparison,indent=2))
    print(json.dumps({a:{"renderer":sum(r["renderer_used"] for r in rs),"preview":sum(r["preview_reads"]>0 for r in rs),"guide":sum(r["construction_guide_read"] for r in rs),"review":sum(bool(r["review_recommended"]) for r in rs)} for a,rs in rows.items()}))


if __name__=="__main__":main()
