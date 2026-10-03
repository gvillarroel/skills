#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""Execute one native curated-art Oracle probe without exposing evaluator secrets."""
import asyncio
import contextlib
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

REPO=Path(__file__).resolve().parents[3]
ROOT=REPO/"evaluations/runs/svg-art-v5"


async def run():
    from harbor.job import Job
    from harbor.models.job.config import JobConfig
    lock=json.loads((ROOT/"integration-lock.json").read_text())
    for name,expected in lock["jobs"].items():
        if hashlib.sha256((ROOT/name).read_bytes()).hexdigest()!=expected:raise ValueError("Job changed")
    if hashlib.sha256(Path(__file__).with_name("harbor_svg_curated.py").read_bytes()).hexdigest()!=lock["adapter_sha256"]:raise ValueError("Adapter changed")
    config=JobConfig.model_validate_json((ROOT/"probe-job.json").read_text());assert config.n_attempts==1 and config.retry.max_retries==0
    with (ROOT/"probe-started.json").open("x") as f:json.dump({"observer_calls":1,"jev_calls":1,"agent":"oracle"},f)
    with (ROOT/"probe.stdout.txt").open("x") as stdout,(ROOT/"probe.stderr.txt").open("x") as stderr:
        with contextlib.redirect_stdout(stdout),contextlib.redirect_stderr(stderr):
            job=await Job.create(config);await job.run()
    result=json.loads((ROOT/"jobs"/config.job_name/"result.json").read_text())
    print(json.dumps({"stats":result["stats"],"result":str(ROOT/"jobs"/config.job_name/"result.json")}))


if __name__=="__main__":
    if sys.platform=="win32":
        p=subprocess.run(["wsl","-e","/home/villa/.local/share/uv/tools/harbor/bin/python","/mnt/c/Users/villa/dev/skills/projects/svg-brief-design/scripts/run_curated_probe.py"],input=json.dumps({"key":os.environ["OPENROUTER_API_KEY"]}),capture_output=True,text=True,encoding="utf-8",timeout=900)
        sys.stdout.write(p.stdout);sys.stderr.write(p.stderr);raise SystemExit(p.returncode)
    os.environ["OPENROUTER_API_KEY"]=json.load(sys.stdin)["key"];os.environ["FOX_PI_AUTH"]="/mnt/c/Users/villa/.pi/agent/auth.json"
    os.environ["PYTHONDONTWRITEBYTECODE"]="1";sys.dont_write_bytecode=True
    sys.path.insert(0,str(REPO/"evaluations/runs/svgq2/python-deps"));sys.path.insert(0,str(Path(__file__).parent))
    asyncio.run(run())
