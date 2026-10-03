#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""Check a path longer than the successor's longest expected mounted output."""
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[3] / "evaluations/runs/svp2"

if __name__ == "__main__":
    image = json.loads((ROOT / "protocol.json").read_text())["runtime"]["agent_image"]
    target = ROOT / "preflight-long/generation-000/candidates/procedural-v1/harbor-jobs/harbor-pop-g000-procedural-v1/vector-030--d3c57e0c21dbede0__probe000/artifacts/logs/artifacts"
    target.mkdir(parents=True, exist_ok=False)
    code = "from pathlib import Path; import time; Path('/logs/artifacts/probe.txt').write_text('probe'); print('ready',flush=True); time.sleep(2)"
    with subprocess.Popen(["docker", "run", "--rm", "--network", "none", "--mount", f"type=bind,source={target},target=/logs/artifacts", image, "python", "-c", code], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True) as process:
        ready = process.stdout.readline().strip()
        try:
            passed = ready == "ready" and (target / "probe.txt").read_text() == "probe"
            failure = None
        except OSError as error:
            passed, failure = False, str(error)
        _, stderr = process.communicate(timeout=15)
    result = {"passed": passed and process.returncode == 0, "path_length": len(str(target)), "path": str(target), "error": failure, "stderr": stderr, "model_calls": 0, "harbor_calls": 0}
    with (ROOT / "mount-readiness.json").open("x") as handle:
        json.dump(result, handle, indent=2)
    print(json.dumps(result))
    assert result["passed"]
