#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Run the same placement engine used by the offline browser composer."""

import json
import shutil
import subprocess
from pathlib import Path


def decision_layout(data, config, cell_pixels=2, seed=73021):
    executable = shutil.which("node")
    if executable is None:
        raise ValueError("Decision view requires Node.js to build; the generated HTML works offline without it")
    engine = Path(__file__).resolve().parent.parent / "assets/templates/decision-engine.js"
    command = "const e=require(process.argv[1]),fs=require('fs'),p=JSON.parse(fs.readFileSync(0,'utf8'));try{process.stdout.write(JSON.stringify(e.compose(p.data,p.config,p.cellPixels,p.seed)));}catch(error){process.stderr.write(error.message);process.exitCode=1;}"
    try:
        result = subprocess.run([executable, "-e", command, str(engine)],
                                input=json.dumps({"data":data,"config":config,"cellPixels":cell_pixels,"seed":seed}),
                                capture_output=True, text=True, encoding="utf-8", timeout=120)
    except subprocess.TimeoutExpired as error:
        raise ValueError("Decision composition exceeded the 120-second build limit") from error
    if result.returncode:
        raise ValueError(result.stderr.strip())
    return json.loads(result.stdout)


def demo_composition(source):
    """An explicit, editable demonstration order; never infer real-world importance."""
    categories = next(d["categories"] for d in source["dimensions"] if d["key"] == "role")
    return {"priority":{"key":"role","order":categories[:]},"affinity":"role","eligibility":"generation",
            "weights":{"parent":2,"affinity":6,"compactness":2,"radial":1},"frontierWindow":4}
