#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = ["PyYAML==6.0.2"]
# ///
"""Open the predeclared pilot gate once, only for an eligible frozen revision."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import yaml
from seal_technique_evolution import ROOT, REPO, org, read, sha, wsl


def exclusive(path,value):
    with path.open("x",encoding="utf-8") as out:json.dump(value,out,indent=2)


def main():
    comparison=read(ROOT / "revision-supplement.json")["comparison"]
    assert comparison["passed"] and read(ROOT / "run.json")["selectedWinner"]=="d"
    assert not (ROOT / "validation-release-ready.json").exists()
    study=ROOT / "study"
    candidate=ROOT / "inputs/d/svg-brief-design"
    shutil.copy2(ROOT / "run.json",ROOT / "generation-001-result.json")
    sources=[("candidate-d","candidate","lineage",candidate),
             ("realization-d","other","lineage",ROOT / "sealed-d"),
             ("first-population","evolution-report","development",ROOT / "generation-000-result.json"),
             ("final-population","evolution-report","development",ROOT / "generation-001-result.json"),
             ("development-decision","decision","development",ROOT / "revision-supplement.json")]
    for arm in ["b","c"]:
        sources.append(("native-"+arm,"native-job","development",ROOT / f"generation-000/candidates/{arm}/harbor-jobs/harbor-pop-g000-{arm}"))
    sources.append(("native-d","native-job","development",ROOT / "jobs/d"))
    for identity,kind,role,path in sources:
        org("record-evidence",study,"--stage-id","evolve","--evidence-id",identity,"--kind",kind,"--role",role,"--visibility","private","--path",path)
    org("transition",study,"--stage-id","evolve","--status","completed","--note","Complete native development selection passes the predeclared mean-gain and family-regression checks; no further mutation.")
    org("release-validation",study,"--selection-id","frozen-d","--selected-stage","evolve","--candidate-evidence",candidate)
    org("transition",study,"--stage-id","validate","--status","running")
    exclusive(ROOT / "validation-release-ready.json",{"passed":True,"selected":"d","development_gain":comparison["mean_gain"],"minimum_family_delta":comparison["family_delta_range"][0],"source_sha256":sha(ROOT / "revision-supplement.json"),"post_release_mutation_allowed":False})
    subprocess.run([sys.executable,str(Path(__file__).with_name("run_technique_revision.py")),"stage-validation"],check=True)
    configs={}
    for role,short in [("baseline","b"),("winner","w")]:
        matches=list((ROOT / "holdout/generation-001").glob(f"*/{role}/harbor-job.yaml"))
        assert len(matches)==1
        payload=yaml.safe_load(matches[0].read_text())
        payload.update(job_name=short,jobs_dir=wsl(ROOT / "private-jobs"))
        path=ROOT / f"private-{short}.json";exclusive(path,payload)
        configs[wsl(path)]=sha(path)
    exclusive(ROOT / "validation-launch.json",{"jobs":configs,"changes_from_native_staging":"Job name and output directory only, to retain proven short Windows/WSL artifact paths.","generation_calls":12,"retries":0})
    org("record-evidence",study,"--stage-id","validate","--evidence-id","private-launch","--kind","lock","--role","validation","--visibility","private","--path",ROOT / "validation-launch.json")
    print(json.dumps({"released":True,"candidate":"d","validation_cases":3,"attempts_per_arm":2,"total_generation_calls":12,"mutation_closed":True}))


if __name__=="__main__":main()
