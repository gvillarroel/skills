#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""Run the sealed native Harbor probe through the existing WSL runtime."""
import asyncio
import contextlib
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

REPO=Path(__file__).resolve().parents[3]
ROOT=REPO/"evaluations/runs/svg-art-v4"


async def execute_native():
    from harbor.job import Job
    from harbor.models.job.config import JobConfig
    lock=json.loads((ROOT/"integration-lock.json").read_text(encoding="utf-8"))
    for name,expected in lock["jobs"].items():
        if hashlib.sha256((ROOT/name).read_bytes()).hexdigest()!=expected:raise ValueError("Native job drift")
    adapter=Path(__file__).with_name("harbor_svg_art_direction.py")
    if hashlib.sha256(adapter.read_bytes()).hexdigest()!=lock["adapter_sha256"]:raise ValueError("Adapter drift")
    config=JobConfig.model_validate_json((ROOT/"probe-job.json").read_text(encoding="utf-8"))
    assert config.n_attempts==1 and config.retry.max_retries==0
    with (ROOT/"probe-started.json").open("x") as f:json.dump({"agent":"oracle","observer_calls":1,"jev_calls":1,"new_generation_calls":0},f)
    with (ROOT/"probe.stdout.txt").open("x") as stdout,(ROOT/"probe.stderr.txt").open("x") as stderr:
        with contextlib.redirect_stdout(stdout),contextlib.redirect_stderr(stderr):
            job=await Job.create(config);await job.run()
    result=json.loads((ROOT/"jobs"/config.job_name/"result.json").read_text(encoding="utf-8"))
    print(json.dumps({"result":str(ROOT/"jobs"/config.job_name/"result.json"),"stats":result["stats"]}))


def main():
    if sys.platform=="win32":
        script="/mnt/c/Users/villa/dev/skills/projects/svg-brief-design/scripts/run_art_direction_probe.py"
        credentials={"openrouter":os.environ["OPENROUTER_API_KEY"],"auth_path":"/mnt/c/Users/villa/.pi/agent/auth.json"}
        p=subprocess.run(["wsl","-e","/home/villa/.local/share/uv/tools/harbor/bin/python",script],input=json.dumps(credentials),capture_output=True,text=True,encoding="utf-8",timeout=900)
        sys.stdout.write(p.stdout);sys.stderr.write(p.stderr);raise SystemExit(p.returncode)
    supplied=json.load(sys.stdin)
    os.environ["OPENROUTER_API_KEY"]=supplied["openrouter"]
    os.environ["FOX_PI_AUTH"]=supplied["auth_path"]
    os.environ["PYTHONDONTWRITEBYTECODE"]="1"
    sys.dont_write_bytecode=True
    sys.path.insert(0,str(REPO/"evaluations/runs/svgq2/python-deps"))
    sys.path.insert(0,str(Path(__file__).parent))
    asyncio.run(execute_native())


if __name__=="__main__":main()
