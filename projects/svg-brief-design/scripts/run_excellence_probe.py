#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = ["harbor==0.18.0", "resvg-py==0.2.6", "Pillow==11.3.0", "numpy==2.2.6", "defusedxml==0.7.1"]
# ///
"""Run one native Oracle control to verify the new evaluator integration."""
import asyncio
import argparse
import contextlib
import hashlib
import json
from pathlib import Path
from harbor.job import Job
from harbor.models.job.config import JobConfig

ROOT = Path(__file__).resolve().parents[3]/"evaluations/runs/svgq2"


async def main(config_name="probe-job.json", seal_name="harbor-integration-lock.json", tag="probe"):
    seal = json.loads((ROOT/seal_name).read_text())
    for filename, field in [(config_name, "probe_job_sha256"), ("future-job.json", "future_job_sha256")]:
        if hashlib.sha256((ROOT/filename).read_bytes()).hexdigest() != seal[field]:
            raise ValueError("Native job changed after its integration freeze")
    adapter = Path(__file__).with_name("harbor_svg_excellence.py")
    if hashlib.sha256(adapter.read_bytes()).hexdigest() != seal["adapter_sha256"]:
        raise ValueError("Verifier adapter changed")
    config = JobConfig.model_validate_json((ROOT/config_name).read_text())
    assert config.n_attempts == 1 and config.retry.max_retries == 0
    with (ROOT/(tag+"-started.json")).open("x") as handle:
        json.dump({"agent": "oracle", "purpose": "Evaluator integration, not a new Luna generation trial", "model_calls": {"observer": 1, "judge": 1}}, handle)
    with (ROOT/(tag+".stdout.txt")).open("x") as stdout, (ROOT/(tag+".stderr.txt")).open("x") as stderr:
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            job = await Job.create(config)
            await job.run()
    result_path = ROOT/"jobs"/config.job_name/"result.json"
    result = json.loads(result_path.read_text())
    print(json.dumps({"native_result": str(result_path), "stats": result["stats"]}))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default="probe-job.json")
    parser.add_argument("--seal", default="harbor-integration-lock.json")
    parser.add_argument("--tag", default="probe")
    args = parser.parse_args()
    asyncio.run(main(args.config, args.seal, args.tag))
