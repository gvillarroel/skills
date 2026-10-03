#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""Apply the frozen combined gate, preserve all evidence, and install only a pass."""
from datetime import datetime, timezone
import json
from pathlib import Path
import shutil
import statistics
import subprocess
import sys
from inspect_technique_evolution import collect, describe
from seal_technique_evolution import REPO, ROOT, PRIOR, IMAGE, org, read, sha, wsl


def exclusive(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open("x",encoding="utf-8") as out:json.dump(value,out,indent=2)


def files(root):
    return {p.relative_to(root).as_posix():sha(p) for p in root.rglob("*") if p.is_file() and "__pycache__" not in p.parts}


def main():
    assert (ROOT / "validation-started.json").exists()
    a=collect(ROOT / "private-jobs/b",6);b=collect(ROOT / "private-jobs/w",6)
    comparison=describe(a,b)
    native=read(ROOT / "run.json")
    native_pass=native["holdout"].get("promoted") is True
    passed=comparison["passed"] and native_pass
    decision={"passed":passed,"native_gate":native["holdout"],"comparison":comparison,"trial_audit":{"baseline":a,"winner":b},
        "candidate":"d","candidate_files":files(ROOT / "inputs/d/svg-brief-design"),"post_gate_mutations":0,
        "protocol_sha256":sha(ROOT / "protocol.json"),"native_run_sha256":sha(ROOT / "run.json"),
        "status":"accepted-pilot" if passed else "baseline-retained","validation_retired":True}
    exclusive(ROOT / "validation-decision.json",decision)
    study=ROOT / "study"
    for name,path,kind,role in [("native-private-b",ROOT / "private-jobs/b","native-job","validation"),
                                ("native-private-w",ROOT / "private-jobs/w","native-job","validation"),
                                ("private-native-report",ROOT / "validation-report/final-report.json","final-report","validation"),
                                ("combined-private-decision",ROOT / "validation-decision.json","decision","validation")]:
        org("record-evidence",study,"--stage-id","validate","--evidence-id",name,"--kind",kind,"--role",role,"--visibility","private","--path",path)
    org("transition",study,"--stage-id","validate","--status","completed","--note","Mandatory gate complete; decision follows frozen native selection plus predeclared family-regression bound.")
    org("add-stage",study,"--stage-id","disposition","--kind","promotion","--owner-skill","harbor-organize-evaluations","--depends-on","validate")
    org("transition",study,"--stage-id","disposition","--status","running")
    if passed:
        target=REPO / "skills/svg-brief-design"
        assert files(target)==files(ROOT / "inputs/b/svg-brief-design"),"Preserve concurrent user changes"
        for relative in decision["candidate_files"]:
            destination=target / relative;destination.parent.mkdir(parents=True,exist_ok=True)
            shutil.copy2(ROOT / "inputs/d/svg-brief-design" / relative,destination)
        assert files(target)==decision["candidate_files"]
        subprocess.run([sys.executable,str(REPO / "scripts/sync-local-skills.py"),"--source",str(target),"--destination",str(REPO / ".agents/skills/svg-brief-design")],check=True)
        assert files(REPO / ".agents/skills/svg-brief-design")==decision["candidate_files"]
    else:
        assert files(REPO / "skills/svg-brief-design")==files(ROOT / "inputs/b/svg-brief-design")
    disposition={"accepted":passed,"canonical_updated":passed,"installed_updated":passed,"candidate":"d","canonical_files":files(REPO / "skills/svg-brief-design"),"validation_retired":True,"new_mutations_require_fresh_study":True}
    exclusive(ROOT / "installation.json",disposition)
    org("record-evidence",study,"--stage-id","disposition","--evidence-id","installation","--kind","decision","--role","decision","--visibility","private","--path",ROOT / "installation.json")
    org("transition",study,"--stage-id","disposition","--status","completed")
    # Repair the active future templates while retaining the historical files.
    runtime_dir=REPO / "projects/svg-brief-design/evaluation/runtime-v6.3"
    runtime_dir.mkdir(exist_ok=False)
    active=REPO / "projects/svg-brief-design/evaluation/active-evaluator.json"
    shutil.copy2(active,ROOT / "active-before-runtime-fix.json")
    value=read(active)
    for filename,key in [("future-job.json","future_job"),("future-baseline-job.json","future_baseline_job")]:
        config=read(PRIOR / filename)
        config["environment"]={"import_path":"procedural_environment:ProceduralEnvironment","delete":True,"kwargs":{"agent_image":IMAGE,"source_agent_image":IMAGE}}
        config["jobs_dir"]="/mnt/c/Users/villa/dev/skills/evaluations/runs/svt-future/jobs"
        if key=="future_job" and passed:config["agents"][0]["skills"]=[wsl(ROOT / "inputs/d/svg-brief-design")]
        path=runtime_dir / filename;exclusive(path,config)
        value["harbor"][key]=path.relative_to(REPO).as_posix()
    value["runtime_configuration_patch"]={"date":"2026-09-26","change":"Existing ProceduralEnvironment supplies required source/effective image attributes; both immutable image IDs are identical. Scoring bundle and 6.3 quality rules unchanged.","verified_native_trials":48,"evolution_report":"evaluations/svg-brief-design/construction-20260926.md"}
    active.write_text(json.dumps(value,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    dev=read(ROOT / "revision-supplement.json")["comparison"]
    all_jobs=[ROOT / f"generation-000/candidates/{x}/harbor-jobs/harbor-pop-g000-{x}" for x in ["b","c"]]+[ROOT / "jobs/d",ROOT / "private-jobs/b",ROOT / "private-jobs/w"]
    jev=[];observers=[];generator=[]
    for job in all_jobs:
        for p in job.glob("*/verifier/provider-response-*.json"):jev.append(read(p))
        for p in job.glob("*/verifier/critic/receipt.json"):observers.append(read(p))
        for p in job.glob("*/result.json"):generator.append(read(p))
    usage=[r["agent_result"] for r in generator if r.get("agent_result")]
    compact={"status":decision["status"],"installed":passed,
        "development":{"baseline":dev["baseline_mean"],"candidate":dev["candidate_mean"],"gain":dev["mean_gain"],"families":dev["families"],"bootstrap":dev["descriptive_family_bootstrap_95_percentile"],"candidate_trials":12},
        "validation":{k:comparison[k] for k in ["complete_evaluable","baseline_mean","candidate_mean","mean_gain","family_delta_range","descriptive_family_bootstrap_95_percentile","passed"] if k in comparison},
        "calls":{"generation":len(generator),"visual_observer":len(observers),"jev":len(jev),"independent_curator":1,"semantic_retries":0},
        "usage":{"generator_input_tokens":sum(x.get("n_input_tokens") or 0 for x in usage),"generator_cached_input_tokens":sum(x.get("n_cache_tokens") or 0 for x in usage),"generator_output_tokens":sum(x.get("n_output_tokens") or 0 for x in usage),"generator_coverage":len(usage),"generator_cost_usd":None,"jev_cost_usd":sum(x["usage"]["cost"] for x in jev),"jev_input_tokens":sum(x["usage"]["input_tokens"] for x in jev),"jev_output_tokens":sum(x["usage"]["output_tokens"] for x in jev),"observer_cost_usd":None,"observer_reported_total_tokens":sum(x.get("usage",{}).get("totalTokens",0) for x in observers)},
        "quality_screen":{"threshold":.9,"development_baseline_passes":sum(r["reward"].get("technique_quality",0)>=.9 for r in read(ROOT / "revision-supplement.json")["trial_audit"]["b"]),"development_candidate_passes":sum(r["reward"].get("technique_quality",0)>=.9 for r in read(ROOT / "revision-supplement.json")["trial_audit"]["d"]),"validation_baseline_passes":sum(r["reward"].get("technique_quality",0)>=.9 for r in a),"validation_candidate_passes":sum(r["reward"].get("technique_quality",0)>=.9 for r in b)},
        "candidate_files":decision["candidate_files"],"constraints":{"purchased_artwork_in_skill":False,"pixel_similarity_reward":False,"same_frozen_quality_rules":True,"validation_families":3,"unforced_skill_discovery_tested":False},
        "evidence":{"protocol_sha256":sha(ROOT / "protocol.json"),"validation_decision_sha256":sha(ROOT / "validation-decision.json"),"installation_sha256":sha(ROOT / "installation.json")}}
    exclusive(REPO / "evaluations/svg-brief-design/construction-20260926.json",compact)
    print(json.dumps({"accepted":passed,"installed":passed,"development_gain":dev["mean_gain"],"validation":compact["validation"],"calls":compact["calls"],"jev_cost_usd":compact["usage"]["jev_cost_usd"]},indent=2))


if __name__=="__main__":main()
