#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = ["resvg-py==0.2.6", "Pillow==11.3.0", "numpy==2.2.6", "defusedxml==0.7.1"]
# ///
"""Freeze only passing technique calibration, run one native control, then activate."""
import argparse
import asyncio
import contextlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

if sys.platform != "win32":
    sys.path.insert(0,str(Path(__file__).resolve().parents[3] / "evaluations/runs/svgq2/python-deps"))

from svg_excellence import REPO, read, sha, write
from prepare_excellence_harbor import wsl

ROOT = REPO / "evaluations/runs/svg-technique-v6.3"
CONFIG = REPO / "projects/svg-brief-design/evaluation/technique-v6.3"
PRIOR = REPO / "evaluations/runs/svg-art-v5"


def freeze():
    result = read(ROOT / "results.json")
    if not result["passed"] or result["accepted_cases"] != 36:
        raise ValueError("Technique calibration failed; no integration or activation")
    bundle = ROOT / "frozen/evaluator"
    shutil.copytree(PRIOR / "frozen/evaluator",bundle,ignore=shutil.ignore_patterns("lock.json","__pycache__"))
    source = REPO / "projects/svg-brief-design/scripts"
    for name in ["svg_technique_review.py","svg_technique_score.py","harbor_svg_technique.py"]:
        shutil.copy2(source / name,bundle / "scripts" / name)
    for path in CONFIG.glob("*"):
        if path.is_file(): shutil.copy2(path,bundle / path.name)
    amendment = ROOT / "external-observation-amendment.json"
    if amendment.exists(): shutil.copy2(amendment,bundle / amendment.name)
    shutil.copy2(ROOT / "inheritance.json",bundle / "calibration-inheritance.json")
    registry = read(bundle / "anchor-registry.json")
    from svg_technique_review import profile_for_task, INTROS
    for name,spec in registry.items(): spec["profile"] = profile_for_task(name)
    (bundle / "anchor-registry.json").write_text(json.dumps(registry,indent=2),encoding="utf-8")
    write(bundle / "lock.json",{"version":"6.3.0","files":{p.relative_to(bundle).as_posix():sha(p.read_bytes()) for p in sorted(bundle.rglob("*")) if p.is_file()},"observed_models":result["observed_models"],"checks":result["checks"],"results_sha256":sha((ROOT / "results.json").read_bytes()),"scope":"Purpose-specific public development calibration; editorial oscillation brief repaired. Not independent skill improvement.","anchor_boundary":"Purchased artwork is host-evaluator-only and never enters skill or generator mounts."})
    ds = ROOT / "ds"
    shutil.copytree(REPO / "evaluations/runs/svgq2/ds",ds)
    for folder in ds.iterdir():
        profile = profile_for_task(folder.name)
        instruction = folder / "instruction.md"
        text = instruction.read_text(encoding="utf-8")
        if profile=="vintage-print-diagram":
            if "oscilación periódica" not in text: raise ValueError("Expected generation brief mismatch absent")
            text = text.replace("oscilación periódica","oscilación")
        instruction.write_text(INTROS[profile]+" "+text,encoding="utf-8",newline="\n")
        (folder / "tests/test.sh").write_text('#!/bin/sh\necho "Use the frozen host-only SvgTechniqueVerifier." >&2\nexit 2\n',encoding="utf-8",newline="\n")
        toml = folder / "task.toml"
        toml.write_text(toml.read_text().replace("technical-excellence-v3","purpose-technique-v6.3").replace("timeout_sec = 360","timeout_sec = 600"),encoding="utf-8",newline="\n")
        contract_path = folder / "tests/request-contract.json"
        contract = read(contract_path)
        if "full_marks" in contract: contract["brief_fulfillment"] = contract.pop("full_marks")
        contract["use_profile"] = profile
        contract["quality_target"] = "Technique serves the declared purpose: evaluated through anonymous located visual evidence; not likeness to reference geometry."
        if profile=="vintage-print-diagram":
            contract["brief"] = text.split("\n\n")[0]
            contract["subject"] = "Editorial vintage oscillation illustration; no constant-period or measurement fidelity requirement."
            contract["brief_fulfillment"] = "Oscillating trace, axes and small reference letters; substantial coherent print character and economical notation."
        contract_path.write_text(json.dumps(contract,indent=2),encoding="utf-8")
        write(folder / "tests/quality-anchor.json",registry[folder.name])
    verifier = {"import_path":"harbor_svg_technique:SvgTechniqueVerifier","kwargs":{"evaluator_bundle":wsl(bundle),"evaluator_lock_sha256":sha((bundle / "lock.json").read_bytes())}}
    for filename,jobname in [("future-job.json","future-technique-v6.3"),("future-baseline-job.json","future-baseline-technique-v6.3")]:
        future = read(REPO / "evaluations/runs/svgq2" / filename)
        future.update(job_name=jobname,jobs_dir=wsl(ROOT / "jobs"),verifier=verifier)
        future["datasets"][0]["path"] = wsl(ds)
        write(ROOT / filename,future)
    probe = ROOT / "probe/hud"
    shutil.copytree(PRIOR / "probe/hud",probe)
    instruction = (probe / "instruction.md").read_text(encoding="utf-8")
    from svg_curated_pairs import INTRO
    if not instruction.startswith(INTRO+" "): raise ValueError("Unexpected probe introduction")
    (probe / "instruction.md").write_text(INTROS["compact-hud"]+instruction[len(INTRO):],encoding="utf-8",newline="\n")
    (probe / "tests/quality-anchor.json").write_text(json.dumps(registry["synthetic-hud"],indent=2),encoding="utf-8")
    future = read(ROOT / "future-job.json")
    job = future | {"job_name":"native-technique-v6.3-probe","n_attempts":1,"n_concurrent_trials":1,"agents":[{"name":"oracle"}],"datasets":[{"path":wsl(ROOT / "probe"),"task_names":["hud"]}]}
    write(ROOT / "probe-job.json",job)
    write(ROOT / "integration-lock.json",{"adapter_sha256":sha((source / "harbor_svg_technique.py").read_bytes()),"jobs":{name:sha((ROOT / name).read_bytes()) for name in ["future-job.json","future-baseline-job.json","probe-job.json"]},"probe_calls":{"observer":1,"jev":1},"native_acceptance":{"completed":1,"errors":0,"retries":0,"identical_render_hashes":True,"overall":"parity","score_between":[85,95],"signed_margin_absolute_max":.1,"review_recommended":False}})
    print("Frozen passing technique evaluator and matched future jobs.")


async def native_run():
    from harbor.job import Job
    from harbor.models.job.config import JobConfig
    lock = read(ROOT / "integration-lock.json")
    for name,expected in lock["jobs"].items():
        if sha((ROOT / name).read_bytes()) != expected: raise ValueError("Job changed")
        JobConfig.model_validate_json((ROOT / name).read_text())
    if sha(Path(__file__).with_name("harbor_svg_technique.py").read_bytes()) != lock["adapter_sha256"]: raise ValueError("Adapter changed")
    config = JobConfig.model_validate_json((ROOT / "probe-job.json").read_text())
    assert config.n_attempts == 1 and config.retry.max_retries == 0
    write(ROOT / "probe-started.json",{"observer_calls":1,"jev_calls":1,"retries":0,"agent":"oracle"})
    with (ROOT / "probe.stdout.txt").open("x") as stdout,(ROOT / "probe.stderr.txt").open("x") as stderr:
        with contextlib.redirect_stdout(stdout),contextlib.redirect_stderr(stderr):
            job = await Job.create(config); await job.run()
    result = read(ROOT / "jobs" / config.job_name / "result.json")
    print(json.dumps({"stats":result["stats"]}))


def run():
    if sys.platform == "win32":
        process = subprocess.run(["wsl","-e","/home/villa/.local/share/uv/tools/harbor/bin/python",wsl(Path(__file__)),"run"],input=json.dumps({"key":os.environ["OPENROUTER_API_KEY"]}),capture_output=True,text=True,encoding="utf-8",timeout=900)
        sys.stdout.write(process.stdout);sys.stderr.write(process.stderr)
        if process.returncode: raise SystemExit(process.returncode)
    else:
        os.environ["OPENROUTER_API_KEY"] = json.load(sys.stdin)["key"]
        os.environ["FOX_PI_AUTH"] = "/mnt/c/Users/villa/.pi/agent/auth.json"
        sys.dont_write_bytecode = True; os.environ["PYTHONDONTWRITEBYTECODE"] = "1"
        sys.path.insert(0,str(REPO / "evaluations/runs/svgq2/python-deps"))
        asyncio.run(native_run())


def activate():
    from evaluate_svg_jev import validate_bundle
    result = read(ROOT / "results.json")
    if not result["passed"]: raise ValueError("Failed calibration")
    bundle = ROOT / "frozen/evaluator"; validate_bundle(bundle)
    native_path = ROOT / "jobs/native-technique-v6.3-probe/result.json"
    native = read(native_path)
    if native["stats"]["n_completed_trials"]!=1 or native["stats"]["n_errored_trials"] or native["stats"]["n_retries"]: raise ValueError("Native control failed")
    trial = next(native_path.parent.glob("hud__*/verifier")); metrics = read(trial / "metrics.json")
    if sha((trial / "candidate.png").read_bytes())!=sha((trial / "anchor.png").read_bytes()) or metrics["choices"]["overall"]!="parity" or not 85<=metrics["score_100"]<=95 or abs(metrics["signed_technique_margin"])>.1 or metrics["review_recommended"]: raise ValueError("Visible identity not scored as confident parity")
    frozen = REPO / "evaluations/runs/svp3/inputs/q/svg-brief-design"
    hashes = {p.relative_to(frozen).as_posix():sha(p.read_bytes()) for p in frozen.rglob("*") if p.is_file() and "__pycache__" not in p.parts}
    for prefix in [REPO / "skills/svg-brief-design",REPO / ".agents/skills/svg-brief-design"]:
        for relative,expected in hashes.items():
            if sha((prefix / relative).read_bytes())!=expected: raise ValueError("Skill changed")
    active = REPO / "projects/svg-brief-design/evaluation/active-evaluator.json"
    previous = CONFIG / "previous-active-v5.2.json"
    if previous.exists(): raise ValueError("Activation already recorded")
    shutil.copy2(active,previous)
    value = read(active)
    value.update(version="6.3.0",status="active-development-calibration",primary_reward="technique_quality",evaluator_bundle=bundle.relative_to(REPO).as_posix(),lock_sha256=sha((bundle / "lock.json").read_bytes()),scope="Purpose-specific calibration on 18 unchanged public outputs plus controls; editorial oscillation brief repaired to remove unsupported constant-period requirement. No private validation, new generation or skill improvement claimed.",report="evaluations/svg-brief-design/technique-20260926.md",uncertainty="Expected coded utility over native Score levels, with normalized rounded probabilities and separate confidence. Insufficient evidence or unknown subject gives no reward. Overall preference and signed margin remain separate.",pass_meaning="Expected utility at least 90 under the declared purpose profile; parity=90 only for pure parity probability. This is a development threshold, not an absolute aesthetic grade.")
    value["harbor"] = {"import_path":"harbor_svg_technique:SvgTechniqueVerifier","future_job":(ROOT / "future-job.json").relative_to(REPO).as_posix(),"future_baseline_job":(ROOT / "future-baseline-job.json").relative_to(REPO).as_posix(),"rewardKey":"technique_quality","requiredRewards":{"artifact_valid":1.0},"passThreshold":.9}
    value["generation_contract"] = "Same short purpose-specific introduction for baseline and skill; descriptions, source SVGs, quality scores and quality anchors stay outside the generator."
    active.write_text(json.dumps(value,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    write(ROOT / "activation.json",{"active_config_sha256":sha(active.read_bytes()),"previous_config_sha256":sha(previous.read_bytes()),"evaluator_lock_sha256":sha((bundle / "lock.json").read_bytes()),"native_result_sha256":sha(native_path.read_bytes()),"unchanged_skill_files":hashes,"native_score":metrics["score_100"],"native_margin":metrics["signed_technique_margin"]})
    print("Activated development evaluator 6.3; all eight skill files unchanged.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode",choices=["freeze","run","activate"])
    args = parser.parse_args()
    {"freeze":freeze,"run":run,"activate":activate}[args.mode]()
