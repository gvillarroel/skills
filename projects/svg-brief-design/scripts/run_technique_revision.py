#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = ["harbor==0.18.0", "PyYAML>=6,<7"]
# ///
"""Run one declared revision and analyze all original native development jobs."""
import asyncio
import contextlib
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

REPO=Path(__file__).resolve().parents[3]
ROOT=REPO / "evaluations/runs/svt1"


def read(p):return json.loads(Path(p).read_text(encoding="utf-8-sig"))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,v):
    with Path(p).open("x",encoding="utf-8") as f:json.dump(v,f,indent=2)
def wsl(p):return "/mnt/c/"+Path(p).resolve().as_posix()[3:]


def arguments():
    argv=read(ROOT / "generation-000-argv.json")
    argv[argv.index("--generation")+1]="1"
    argv += ["--candidate","d="+str(ROOT / "inputs/d/svg-brief-design"),"--analyze-only"]
    for a in ["b","c"]:argv += ["--job",a+"="+str(ROOT / f"generation-000/candidates/{a}/harbor-jobs/harbor-pop-g000-{a}")]
    return argv+["--job","d="+str(ROOT / "jobs/d")]


async def live(path):
    from harbor.job import Job
    from harbor.models.job.config import JobConfig
    config=JobConfig.model_validate_json(path.read_text())
    assert config.n_attempts==2 and config.n_concurrent_trials==3 and config.retry.max_retries==0
    job=await Job.create(config);await job.run()


def main():
    mode=sys.argv[1]
    assert mode in {"run","analyze","stage-validation","private-run","finish-validation"}
    if sys.platform=="win32":
        if mode=="run":
            config=read(ROOT / "templates/development.json")
            config.update(job_name="d",jobs_dir=wsl(ROOT / "jobs"))
            config["agents"][0]["skills"]=[wsl(ROOT / "inputs/d/svg-brief-design")]
            write(ROOT / "d-job.json",config)
        result=subprocess.run(["wsl","-e","/home/villa/.local/share/uv/tools/harbor/bin/python",wsl(__file__),mode],input=json.dumps({"key":os.environ["OPENROUTER_API_KEY"]}),text=True,encoding="utf-8")
        return result.returncode
    os.environ["OPENROUTER_API_KEY"]=json.load(sys.stdin)["key"]
    os.environ["FOX_PI_AUTH"]="/mnt/c/Users/villa/.pi/agent/auth.json"
    os.environ["PYTHONDONTWRITEBYTECODE"]="1";sys.dont_write_bytecode=True
    sys.path.insert(0,str(REPO / "evaluations/runs/svgq2/python-deps"))
    from evaluate_svg_jev import validate_bundle
    validate_bundle(ROOT / "evaluator")
    protocol=read(ROOT / "protocol.json")
    for name,expected in protocol["helper_sha256"].items():assert sha(Path(__file__).parent / name)==expected
    if mode=="run":
        assert not (ROOT / "validation-release-ready.json").exists()
        write(ROOT / "d-started.json",{"at":datetime.now(timezone.utc).isoformat(),"job_sha256":sha(ROOT / "d-job.json"),"entrypoint_sha256":sha(__file__),"generation_calls":12,"retries":0})
    with (ROOT / ("revision-"+mode+".stdout.txt")).open("x") as out,(ROOT / ("revision-"+mode+".stderr.txt")).open("x") as err:
        with contextlib.redirect_stdout(out),contextlib.redirect_stderr(err):
            if mode=="run":
                asyncio.run(live(ROOT / "d-job.json"));code=0
            elif mode=="private-run":
                assert read(ROOT / "validation-release-ready.json")["passed"]
                release=read(ROOT / "validation-launch.json")
                write(ROOT / "validation-started.json",{"at":datetime.now(timezone.utc).isoformat(),"generation_calls":12,"retries":0,"launch_sha256":sha(ROOT / "validation-launch.json")})
                async def gate():
                    for path,expected in release["jobs"].items():
                        p=Path(path);assert sha(p)==expected
                        await live(p)
                asyncio.run(gate());code=0
            else:
                import run_procedural_population
                argv=arguments()
                if mode in {"stage-validation","finish-validation"}:
                    assert read(ROOT / "validation-release-ready.json")["passed"]
                    argv += ["--holdout-template",str(ROOT / "templates/validation.json")]
                if mode=="finish-validation":
                    argv += ["--holdout-job","baseline="+str(ROOT / "private-jobs/b"),"--holdout-job","winner="+str(ROOT / "private-jobs/w")]
                sys.argv=["population"]+argv;code=run_procedural_population.main()
    print(json.dumps({"mode":mode,"exit_code":code}),flush=True)
    return code


if __name__=="__main__":raise SystemExit(main())
