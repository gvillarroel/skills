#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["psutil"]
# ///
"""List this audit's processes or stop explicitly named obsolete cohorts."""
import argparse
import json
from pathlib import Path

import psutil

parser = argparse.ArgumentParser()
parser.add_argument("--stop-revision", action="append", default=[])
parser.add_argument("--skill", default="all")
args = parser.parse_args()
root = Path(__file__).resolve().parents[3]
memory = psutil.virtual_memory()
print(json.dumps({"availableMemoryMb": round(memory.available / 1024**2),
                  "memoryUsedPercent": memory.percent, "processCount": len(psutil.pids())}))
matches = []
for process in psutil.process_iter(["pid", "ppid", "cmdline", "memory_info"]):
    try:
        command = process.info["cmdline"] or []
        joined = " ".join(command)
        if "run_root_cases.py" not in joined:
            continue
        index = next(i for i, arg in enumerate(command) if arg.endswith("run_root_cases.py"))
        script = Path(command[index])
        if not script.is_absolute():
            script = Path(process.cwd()) / script
        if script.resolve() != root / "projects/diagram-compactness/scripts/run_root_cases.py":
            continue
        revision = command[index + 1] if len(command) > index + 1 else "final"
        skill = command[index + 3] if len(command) > index + 3 else "all"
        if args.skill != "all" and args.skill != skill:
            continue
        matches.append((process, revision))
        print(json.dumps({"pid": process.pid, "parent": process.ppid(), "revision": revision, "skill": skill,
                          "rssMb": round(process.memory_info().rss / 1024**2, 1),
                          "children": len(process.children(recursive=True))}))
    except (psutil.Error, StopIteration):
        continue
for process, revision in matches:
    if revision not in args.stop_revision or not process.is_running():
        continue
    try:
        children = process.children(recursive=True)
        for child in reversed(children):
            try:
                child.terminate()
            except psutil.Error:
                pass
        process.terminate()
        print(json.dumps({"stoppedObsoleteRevision": revision, "pid": process.pid,
                          "retainedRunArtifacts": True}))
    except psutil.Error as exc:
        print(json.dumps({"pid": process.pid, "error": str(exc)}))
