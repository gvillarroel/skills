#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = ["harbor==0.18.0"]
# ///
"""Execute the single predeclared development revision, without semantic retries."""
import asyncio
import contextlib
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from harbor.job import Job
from harbor.models.job.config import JobConfig
from prepare_procedural_study import hashes, write

ROOT = Path(__file__).resolve().parents[3] / "evaluations/runs/svp3"


async def main():
    assert not (ROOT / "holdout").exists(), "Private gate already staged or opened"
    assert (ROOT / "run.json").is_file(), "Complete the first generation before the revision"
    seal = json.loads((ROOT / "q-mutation.json").read_text())
    assert hashes(ROOT / "inputs/q/svg-brief-design") == seal["child_files"]
    assert hashlib.sha256((ROOT / "q-job.json").read_bytes()).hexdigest() == seal["native_job_sha256"]
    config = JobConfig.model_validate_json((ROOT / "q-job.json").read_text())
    assert config.n_attempts == 3 and config.n_concurrent_trials == 3 and config.retry.max_retries == 0
    write(ROOT / "q-started.json", {"started_at": datetime.now(timezone.utc).isoformat(), "mutation_sha256": hashlib.sha256((ROOT / "q-mutation.json").read_bytes()).hexdigest(), "runner_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(), "max_calls": 18})
    print("Starting the 18-trial renderer-entrypoint revision", flush=True)
    with (ROOT / "q.stdout.txt").open("w") as out, (ROOT / "q.stderr.txt").open("w") as err:
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            job = await Job.create(config)
            await job.run()
    print(json.dumps({"complete": True, "native_job": str(ROOT / "jobs/q")}))


if __name__ == "__main__":
    asyncio.run(main())
