#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = ["resvg-py==0.2.6", "Pillow==11.3.0", "numpy==2.2.6", "defusedxml==0.7.1", "PyYAML==6.0.2"]
# ///
"""Run append-only SVG evolution phases with a three-rejection plateau rule.

Native Harbor owns execution and ranking. This adapter only binds frozen
inputs, realizes reviewed mutations, and applies declared family-loss gates.
"""
import asyncio
import contextlib
import copy
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

from seal_technique_evolution import REPO, REALIZER, org, read, sha, wsl
from inspect_technique_evolution import collect, describe


def put(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as handle:
        json.dump(value, handle, indent=2, ensure_ascii=False)


def digest(path):
    return json.loads(subprocess.check_output(
        [sys.executable, str(REALIZER), "digest", str(path)]))["treeSha256"]


def campaign_root(root):
    binding = root / "campaign-binding.json"
    if not binding.exists():
        return REPO / "evaluations/runs/svg-continuation-20260926"
    name = read(binding)["campaign"]
    assert name and Path(name).name == name and name not in {".", ".."}
    return REPO / "evaluations/runs" / name


def record_attempt(root, arm, accepted, evidence):
    campaign = campaign_root(root)
    events = sorted((campaign / "events").glob("*.json"))
    previous = read(events[-1]) if events else {"failure_streak":0,"accepted_improvements":0}
    assert not any(read(p)["phase"]==root.name and read(p)["candidate"]==arm for p in events)
    event = {"sequence":len(events)+1,"phase":root.name,"candidate":arm,
        "accepted":accepted,"failure_streak":0 if accepted else previous["failure_streak"]+1,
        "accepted_improvements":previous["accepted_improvements"]+int(accepted),
        "evidence":str(evidence),"evidence_sha256":sha(evidence),
        "previous_event_sha256":sha(events[-1]) if events else None}
    put(campaign / f"events/{len(events)+1:03d}.json",event)
    return event


def compare_development(root, arm, baseline, candidate):
    """Use native semantic-zero evidence, with an additional visual-gain guard.

    A candidate still needs complete, error-free qualification. One specifically
    audited baseline command misuse is an attributable semantic failure, not an
    external failure or missing judge score. Preserve every raw row in receipts.
    Native Harbor already assigns it reward zero; do not retry it or rescore it.
    """
    failed = [r for r in baseline if r["exception"]]
    normalized = copy.deepcopy(baseline)
    for row in normalized:
        if not row["exception"]:
            continue
        exception = row["exception"]
        trace = root / "jobs/b" / row["trial"] / "agent/pi.txt"
        events = []
        for line in trace.read_text(encoding="utf-8").splitlines():
            try: events.append(json.loads(line))
            except ValueError: pass
        failures = [e for e in events if e.get("type")=="tool_execution_end" and e.get("isError")]
        known_misuses = ["Cannot build scaffold: Unsupported detail attribute",
                        "Cannot build scaffold: stroke must be between 0.2 and 40",
                        "ls: cannot access '/logs/artifacts/deliverable': No such file or directory",
                        "ENOENT: no such file or directory, access '/harbor/skills/svg-brief-design/references/purpose-and-construction.md'"]
        attributable = (exception["exception_message"]=="Pi tool error" and len(failures)==1
                        and any(message in json.dumps(failures[0]) for message in known_misuses))
        if not attributable:
            return {"complete_evaluable":False,"passed":False,"reason":"Unclassified baseline failure requires audit; no invented reward."}
        # These normalized copies are only inputs to the existing aggregation;
        # they are never serialized as native artifact-valid or execution facts.
        row.update(exception=None,input_isolated=True,skill_unchanged=True,
                   reward={"technique_quality":0.0,"artifact_valid":1})
    candidate_normalized = copy.deepcopy(candidate)
    candidate_failures = []
    for row in candidate_normalized:
        if not row["exception"]:
            continue
        trace = root / f"jobs/{arm}" / row["trial"] / "agent/pi.txt"
        events = []
        for line in trace.read_text(encoding="utf-8").splitlines():
            try: events.append(json.loads(line))
            except ValueError: pass
        failures = [e for e in events if e.get("type")=="tool_execution_end" and e.get("isError")]
        known = ["/bin/bash: line 1: rg: command not found",
                 "Cannot build scaffold: stroke must be between 0.2 and 40",
                 "ls: cannot access '/logs/artifacts/deliverable': No such file or directory",
                 "content: must have required properties content",
                 "Cannot render SVG: SVG renders empty",
                 "Cannot build scaffold: Unsupported detail attribute",
                 "ENOENT: no such file or directory, access '/harbor/skills/svg-brief-design/references/purpose-and-construction.md'"]
        if not (row["exception"]["exception_message"]=="Pi tool error" and failures
                and all(any(message in json.dumps(e) for message in known) for e in failures)):
            return {"complete_evaluable":False,"passed":False,"reason":"Unclassified candidate failure requires audit."}
        candidate_failures.append({"trial":row["trial"],"native_effective_reward":0,
            "reason":"Audited agent-side command, tool argument, filename or empty-artifact failure; original record retained."})
        row.update(exception=None,input_isolated=True,skill_unchanged=True,
                   reward={"technique_quality":0.0,"artifact_valid":1})
    result = describe(normalized,candidate_normalized)
    result["candidate_attributable_failures"] = candidate_failures
    result["baseline_attributable_failures"] = [{"trial":r["trial"],"native_effective_reward":0,
        "reason":"Audited agent-side argument or absent-path command misuse; original failure retained."} for r in failed]
    affected = {r["task"] for r in failed}
    sensitivity = describe([r for r in baseline if r["task"] not in affected],
                           [r for r in candidate_normalized if r["task"] not in affected])
    result["unaffected_family_visual_guard"] = sensitivity
    result["passed"] &= sensitivity["passed"] and not candidate_failures
    result["guard_note"] = "Additional conservative requirement: two-point gain and bounded family loss also on all unaffected families. Failure-derived gains alone cannot pass. Attributable errors, when present, remain disqualifying for candidate selection; private gates still require both arms error-free."
    return result


def realize(root, arm):
    assert not (root / "validation-release-ready.json").exists()
    assert len(list((root / "inputs").glob("*/svg-brief-design"))) <= read(root / "protocol.json")["budget"]["max_candidates"]
    events = sorted((campaign_root(root) / "events").glob("*.json"))
    assert not events or read(events[-1])["failure_streak"] < 3
    plan = read(root / f"mutation-{arm}.json")
    parent = root / "inputs/b/svg-brief-design"
    config = read(REPO / "evaluations/runs/svt1/realize-d.json")
    r = config["realization"]
    r.update(id=root.name+"-"+arm, candidateId=arm, parentSkill=str(parent),
             expectedParentTreeSha256=digest(parent),
             workspaceDir=str(root / ("workspace-"+arm)),
             outputDir=str(root / ("sealed-"+arm)))
    r["operator"] = {"operatorId":plan["operator"], "instruction":plan["hypothesis"],
                     "origin":"public-development-reflection", "parentOperatorIds":[]}
    r["allowedChanges"] = list(plan["files"])
    if plan.get("validation_commands"):
        r["validationCommands"] = plan["validation_commands"]
    evidence = [root / f"mutation-{arm}.json",
                REPO / "evaluations/runs/svt1/revision-supplement.json"]
    evidence += [root / p for p in plan.get("development_evidence", [])]
    r["developmentEvidence"] = [{"id":f"dev-{i}","role":"development",
        "path":str(p),"sha256":"sha256:"+sha(p)} for i,p in enumerate(evidence)]
    config_path = root / f"realization-{arm}.json"
    put(config_path, config)
    subprocess.run([sys.executable,str(REALIZER),"prepare",str(config_path)],check=True)
    candidate = root / f"workspace-{arm}/candidate/skills/svg-brief-design"
    for relative, edits in plan["files"].items():
        target = candidate / relative
        content = target.read_text(encoding="utf-8") if target.exists() else ""
        for edit in edits:
            if "replace" in edit:
                assert content.count(edit["replace"]) == 1
                content = content.replace(edit["replace"],edit["with"],1)
            else:
                content += edit["append"]
        target.parent.mkdir(parents=True,exist_ok=True)
        target.write_text(content,encoding="utf-8",newline="\n")
    for mode in ["seal","verify"]:
        subprocess.run([sys.executable,str(REALIZER),mode,str(config_path)],check=True)
    shutil.copytree(root / f"sealed-{arm}/candidate/skills/svg-brief-design",
                    root / f"inputs/{arm}/svg-brief-design")


def arguments(root, arms, generation):
    argv = ["--job-template",str(root / "templates/development.json"),
            "--baseline","b","--generation",str(generation),
            "--reward-key","technique_quality","--pass-threshold","0",
            "--minimum-development-pass-rate","1","--required-reward","artifact_valid=1",
            "--minimum-holdout-gain",".02","--allow-task-regressions",
            "--output",str(root)]
    for arm in ["b"]+arms:
        argv += ["--candidate",arm+"="+str(root / f"inputs/{arm}/svg-brief-design")]
    return argv


async def live(path):
    from harbor.job import Job
    from harbor.models.job.config import JobConfig
    config = JobConfig.model_validate_json(path.read_text())
    assert config.n_attempts == 2 and config.n_concurrent_trials == 3
    assert config.retry.max_retries == 0
    await (await Job.create(config)).run()


def remote(root, mode, arm):
    os.environ["OPENROUTER_API_KEY"] = json.load(sys.stdin)["key"]
    os.environ["FOX_PI_AUTH"] = "/mnt/c/Users/villa/.pi/agent/auth.json"
    os.environ["PYTHONDONTWRITEBYTECODE"] = "1"
    sys.dont_write_bytecode = True
    sys.path.insert(0,str(REPO / "evaluations/runs/svgq2/python-deps"))
    from evaluate_svg_jev import validate_bundle
    validate_bundle(root / "evaluator")
    for name, expected in read(root / "protocol.json")["helper_sha256"].items():
        assert sha(Path(__file__).parent / name) == expected
    arms = sorted(p.parent.name for p in (root / "inputs").glob("*/svg-brief-design") if p.parent.name != "b")
    argv = arguments(root,arms,len(arms)-1)
    if mode in {"analyze","stage-gate","finish-gate"}:
        argv += ["--analyze-only"]
        for a in ["b"]+arms:
            argv += ["--job",a+"="+str(root / f"jobs/{a}")]
    if mode in {"stage-gate","finish-gate"}:
        assert read(root / "validation-release-ready.json")["passed"]
        argv += ["--holdout-template",str(root / "templates/validation.json")]
    if mode == "finish-gate":
        argv += ["--holdout-job","baseline="+str(root / "private-jobs/b"),
                 "--holdout-job","winner="+str(root / "private-jobs/w")]
    if mode in {"doctor","dry-run"}: argv += ["--"+mode]
    log = root / f"{mode}-{arm}"
    with log.with_suffix(".stdout.txt").open("x") as out, log.with_suffix(".stderr.txt").open("x") as err:
        with contextlib.redirect_stdout(out),contextlib.redirect_stderr(err):
            if mode == "run":
                assert not (root / "validation-release-ready.json").exists()
                put(root / f"started-{arm}.json",{"at":datetime.now(timezone.utc).isoformat(),
                    "job_sha256":sha(root / f"job-{arm}.json"),"entrypoint_sha256":sha(__file__),"generation_calls":12,"retries":0})
                asyncio.run(live(root / f"job-{arm}.json"))
                code = 0
            elif mode == "gate-run":
                assert read(root / "validation-release-ready.json")["passed"]
                put(root / "gate-started.json",{"at":datetime.now(timezone.utc).isoformat(),"generation_calls":12,"retries":0})
                async def gate():
                    for short in ["b","w"]: await live(root / f"private-{short}.json")
                asyncio.run(gate()); code = 0
            else:
                import run_procedural_population
                sys.argv = ["population"]+argv
                code = run_procedural_population.main()
    print(json.dumps({"mode":mode,"arm":arm,"exit_code":code}),flush=True)
    return code


def main():
    mode, phase = sys.argv[1:3]
    arm = sys.argv[3] if len(sys.argv)>3 else "b"
    assert phase.startswith("svt") and phase[3:].isdigit()
    root = REPO / "evaluations/runs" / phase
    if sys.platform != "win32": return remote(root,mode,arm)
    if mode == "curate":
        import prepare_technique_evolution as preparation
        previous = [REPO / "evaluations/runs/svt1"]
        previous += [p for p in root.parent.glob("svt[0-9]*") if p != root and p.name != "svt1" and (p / "gate-started.json").exists()]
        preparation.curate(root, previous, samples_per_pack=6); return 0
    if mode == "seal":
        import seal_technique_evolution as sealing
        sealing.main(root,REPO / "skills/svg-brief-design",3,False); return 0
    if mode == "realize": realize(root,arm); return 0
    if mode == "status":
        print(json.dumps({p.name:{"trials":len(collect(p)),"finished":(p / "result.json").exists() and bool(read(p / "result.json").get("finished_at")),
            "errors":sum(bool(r["exception"]) for r in collect(p))} for p in (root / "jobs").glob("*") if p.is_dir()})); return 0
    if mode == "decision":
        a,b = collect(root / "jobs/b",12),collect(root / f"jobs/{arm}",12)
        result = compare_development(root,arm,a,b)
        native = read(root / "run.json")
        result["native_selected_winner"] = native["selectedWinner"]
        result["passed"] &= native["selectedWinner"]==arm
        put(root / f"decision-{arm}.json",{"comparison":result,"trial_audit":{"b":a,arm:b},
            "native_run_sha256":sha(root / "run.json"),"protocol_sha256":sha(root / "protocol.json")})
        shutil.copy2(root / "run.json",root / f"native-{arm}.json")
        if result["complete_evaluable"] and not result["passed"]:
            event = record_attempt(root,arm,False,root / f"decision-{arm}.json")
            print(json.dumps({"failure_streak":event["failure_streak"]}))
        print(json.dumps(result,indent=2)); return 0
    if mode == "release":
        import yaml
        comparison = read(root / f"decision-{arm}.json")["comparison"]
        assert comparison["passed"] and read(root / "run.json")["selectedWinner"]==arm
        candidate = root / f"inputs/{arm}/svg-brief-design"
        for name,kind,role,path in [
            ("selected-candidate","candidate","lineage",candidate),
            ("sealed-realization","other","lineage",root / f"sealed-{arm}"),
            ("development-decision","decision","development",root / f"decision-{arm}.json"),
            ("native-selection","evolution-report","development",root / f"native-{arm}.json")]:
            org("record-evidence",root / "study","--stage-id","evolve","--evidence-id",name,
                "--kind",kind,"--role",role,"--visibility","private","--path",path)
        org("transition",root / "study","--stage-id","evolve","--status","completed")
        org("release-validation",root / "study","--selection-id","frozen-"+arm,
            "--selected-stage","evolve","--candidate-evidence",candidate)
        org("transition",root / "study","--stage-id","validate","--status","running")
        put(root / "validation-release-ready.json",{"passed":True,"selected":arm,
            "tree":digest(candidate),"mutation_closed":True})
        subprocess.run([sys.executable,__file__,"stage-gate",phase,arm],check=True)
        for role,short in [("baseline","b"),("winner","w")]:
            paths = list((root / "holdout").glob(f"generation-*/attempt-*/{role}/harbor-job.yaml"))
            assert len(paths)==1
            config = yaml.safe_load(paths[0].read_text())
            config.update(job_name=short,jobs_dir=wsl(root / "private-jobs"))
            put(root / f"private-{short}.json",config)
        print(json.dumps({"released":arm,"calls":12,"mutation_closed":True})); return 0
    if mode == "run":
        config = read(root / "templates/development.json")
        config.update(job_name=arm,jobs_dir=wsl(root / "jobs"))
        config["agents"][0]["skills"] = [wsl(root / f"inputs/{arm}/svg-brief-design")]
        put(root / f"job-{arm}.json",config)
    result = subprocess.run(["wsl","-e","/home/villa/.local/share/uv/tools/harbor/bin/python",wsl(__file__),mode,phase,arm],
        input=json.dumps({"key":os.environ["OPENROUTER_API_KEY"]}),text=True,encoding="utf-8")
    return result.returncode


if __name__ == "__main__": raise SystemExit(main())
