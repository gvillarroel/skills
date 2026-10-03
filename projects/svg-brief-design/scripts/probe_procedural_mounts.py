#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""Reproduce short/deep artifact bind-mount visibility without model calls."""
import json
from pathlib import Path
import subprocess
from datetime import datetime, timezone

REPO = Path(__file__).resolve().parents[3]
ROOT = REPO / "evaluations/runs/svg-brief-design-procedural-20260926"
IMAGE = "sha256:1c1ac1dfdc903a9f3a64f4a3a75be7ab883a94647edac0045105d89674b4cbf8"


def main():
    paths = [REPO / "evaluations/runs/svg-mount-probe-short/artifacts",
             ROOT / "mount-probe/generation-000/candidates/baseline/harbor-jobs/harbor-pop-g000-baseline/vector-018--99a8559203bfe19b__probe000/artifacts/logs/artifacts"]
    rows = []
    for target in paths:
        target.mkdir(parents=True, exist_ok=False)
        command = ["docker", "run", "--rm", "--network", "none", "--mount", f"type=bind,source={target},target=/logs/artifacts", IMAGE,
                   "python", "-c", "from pathlib import Path; import time; Path('/logs/artifacts/probe.txt').write_text('probe'); print('ready',flush=True); time.sleep(3)"]
        with subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True) as process:
            ready = process.stdout.readline().strip()
            try:
                observed = (target / "probe.txt").read_text()
                status = {"visible": observed == "probe"}
            except OSError as error:
                status = {"visible": False, "errno": error.errno, "error": str(error)}
            _, stderr = process.communicate(timeout=15)
        rows.append({"path": str(target), "length": len(str(target)), "ready": ready,
                     "exit_code": process.returncode, "stderr": stderr, **status})
    result = {"recorded_at": datetime.now(timezone.utc).isoformat(), "harbor_calls": 0, "model_calls": 0, "rows": rows}
    with (ROOT / "artifact-mount-probe.json").open("x") as handle:
        json.dump(result, handle, indent=2)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
