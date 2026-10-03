#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""Measure host mount visibility at declared candidate path lengths without inference."""
import json
from pathlib import Path
import subprocess

REPO = Path(__file__).resolve().parents[3]
ROOT = REPO / "evaluations/runs/svp3"
IMAGE = "sha256:1c1ac1dfdc903a9f3a64f4a3a75be7ab883a94647edac0045105d89674b4cbf8"

if __name__ == "__main__":
    ROOT.mkdir(exist_ok=False)
    rows = []
    for length in (160, 180, 200):
        base = str(ROOT / "probe")
        target = Path(base + "x" * (length-len(base)))
        target.mkdir()
        code = "from pathlib import Path; import time; Path('/logs/artifacts/probe.txt').write_text('probe'); print('ready',flush=True); time.sleep(1)"
        with subprocess.Popen(["docker", "run", "--rm", "--network", "none", "--mount", f"type=bind,source={target},target=/logs/artifacts", IMAGE, "python", "-c", code], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True) as process:
            ready = process.stdout.readline().strip()
            try:
                status = {"passed": ready == "ready" and (target / "probe.txt").read_text() == "probe"}
            except OSError as error:
                status = {"passed": False, "errno": error.errno}
            _, stderr = process.communicate(timeout=15)
        rows.append({"length": length, "path": str(target), "exit_code": process.returncode, "stderr": stderr, **status})
    result = {"rows": rows, "harbor_calls": 0, "model_calls": 0}
    with (ROOT / "path-length-probe.json").open("x") as handle:
        json.dump(result, handle, indent=2)
    print(json.dumps(result, indent=2))
