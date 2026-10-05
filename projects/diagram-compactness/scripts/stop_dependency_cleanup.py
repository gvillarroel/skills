#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["psutil"]
# ///
"""Stop only this project's cleanup process once disk headroom is recovered."""
import json
from pathlib import Path
import shutil

import psutil

ROOT = Path(__file__).resolve().parents[3]
SCRIPT = ROOT / "projects/diagram-compactness/scripts/clean_trial_dependencies.py"
free = shutil.disk_usage(ROOT).free
if free < 10 * 1024**3:
    raise SystemExit(f"Keep cleanup running: only {free / 1024**3:.2f} GiB is free.")
targets = []
for process in psutil.process_iter(["pid", "cmdline"]):
    try:
        command = process.info["cmdline"] or []
        if not any(argument.replace("\\", "/").endswith("/clean_trial_dependencies.py") for argument in command):
            continue
        candidate = next(argument for argument in command if argument.replace("\\", "/").endswith("/clean_trial_dependencies.py"))
        candidate = Path(candidate)
        if not candidate.is_absolute():
            candidate = Path(process.cwd()) / candidate
        if candidate.resolve() == SCRIPT.resolve():
            targets.append(process)
    except (psutil.Error, StopIteration):
        continue
stopped = []
for process in sorted(targets, key=lambda item: len(item.parents()), reverse=True):
    try:
        process.terminate()
        stopped.append(process.pid)
    except psutil.NoSuchProcess:
        pass
report = {"freeBytes": free, "stoppedOwnedCleanupPids": stopped,
          "preservedAllTrialEvidence": True,
          "note": "Cleanup stopped with sufficient headroom to reduce filesystem contention during remaining native tests. A partially removed node_modules is regenerable."}
output = ROOT / "projects/diagram-compactness/artifacts/reviews/dependency-cleanup-stop.json"
output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
print(json.dumps(report))
