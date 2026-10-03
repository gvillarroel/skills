#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["resvg-py==0.2.6", "Pillow==11.3.0", "numpy==2.2.6", "defusedxml==0.7.1"]
# ///
"""Create new native public task/config versions; never modify old Harbor studies."""
import re
from pathlib import Path
from svg_excellence import CONFIG, REPO, host_path, read, sha, write
from prepare_excellence import controls

ROOT = REPO/"evaluations/runs/svgq2"


def wsl(path):
    text = str(path.resolve()).replace("\\", "/")
    return "/mnt/"+text[0].lower()+text[2:] if len(text)>1 and text[1] == ":" else text


def task(folder, instruction, contract, solution=None):
    (folder/"tests").mkdir(parents=True, exist_ok=False)
    (folder/"environment").mkdir()
    (folder/"instruction.md").write_text(instruction, encoding="utf-8")
    write(folder/"tests/request-contract.json", contract)
    (folder/"tests/test.sh").write_text('#!/bin/sh\necho "This task requires the frozen SvgExcellenceVerifier import path." >&2\nexit 2\n')
    (folder/"environment/Dockerfile").write_text('FROM fox-vector-agent:2.0.0\nWORKDIR /app\n')
    (folder/"task.toml").write_text('''schema_version = "1.3"
[metadata]
category = "graphics"
tags = ["svg", "technical-excellence-v3", "jev"]
[agent]
timeout_sec = 240
network_mode = "public"
[environment]
docker_image = "sha256:1c1ac1dfdc903a9f3a64f4a3a75be7ab883a94647edac0045105d89674b4cbf8"
cpus = 2
memory_mb = 2048
workdir = "/app"
[verifier]
timeout_sec = 360
environment_mode = "shared"
''')
    if solution:
        (folder/"solution").mkdir()
        target = re.search(r"`(/logs/artifacts/[^`]+\.svg)`", instruction).group(1)
        (folder/"solution/solve.sh").write_text('#!/bin/sh\nset -eu\nmkdir -p '+str(Path(target).parent).replace('\\','/')+"\ncat > '"+target+"' <<'SVG_EOF'\n"+solution+"\nSVG_EOF\n", newline="\n")


def main():
    contracts = read(CONFIG/"request-contracts.json")["contracts"]
    audit = read(REPO/"evaluations/runs/svp3/revision-review/audit.json")
    seen = set()
    for row in audit["records"]:
        name = row["task"]
        if name in seen:
            continue
        seen.add(name)
        result = read(host_path(row["native_result"]))
        source = host_path(result["config"]["task"]["path"])
        task(ROOT/"ds"/name, (source/"instruction.md").read_text(encoding="utf-8"), contracts[name])
    bundle = ROOT/"frozen-v3/evaluator"
    verifier = {"import_path": "harbor_svg_excellence:SvgExcellenceVerifier", "kwargs": {
        "evaluator_bundle": wsl(bundle), "evaluator_lock_sha256": sha((bundle/"lock.json").read_bytes())}}
    config = {"job_name": "future-technical-v3", "jobs_dir": wsl(ROOT/"jobs"), "n_attempts": 3, "n_concurrent_trials": 3,
              "retry": {"max_retries": 0}, "environment": {"type": "docker", "delete": True},
              "agents": [{"name": "pi-svg-procedural", "import_path": "pi_svg_procedural:PiSvgProcedural", "model_name": "openai-codex/gpt-6-luna", "skills": [wsl(REPO/"evaluations/runs/svp3/inputs/q/svg-brief-design")], "kwargs": {"version": "0.84.2"}}],
              "verifier": verifier, "datasets": [{"path": wsl(ROOT/"ds"), "task_names": sorted(seen)}]}
    write(ROOT/"future-job.json", config)
    control = next(row for row in controls() if row["name"] == "disk-large")
    task(ROOT/"probe/disk", control["request"]+" Save the SVG to `/logs/artifacts/deliverable/vector.svg`.", control["contract"], control["svg"])
    probe = config | {"job_name": "probe", "n_attempts": 1, "n_concurrent_trials": 1, "agents": [{"name": "oracle"}],
                      "datasets": [{"path": wsl(ROOT/"probe"), "task_names": ["disk"]}]}
    write(ROOT/"probe-job.json", probe)
    write(ROOT/"harbor-integration-lock.json", {"adapter_sha256": sha((REPO/"projects/svg-brief-design/scripts/harbor_svg_excellence.py").read_bytes()),
          "future_job_sha256": sha((ROOT/"future-job.json").read_bytes()), "probe_job_sha256": sha((ROOT/"probe-job.json").read_bytes()),
          "agent_credentials": "No evaluator credentials or observations enter the generation container. The custom verifier executes on the trusted host after generation.",
          "future_primary_reward": "technical_excellence"})
    print("Prepared six public tasks and a one-task native integration probe.")


if __name__ == "__main__":
    main()
