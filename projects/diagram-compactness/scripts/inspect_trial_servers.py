#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["psutil"]
# ///
"""Inspect or close only superseded trial servers in this audit workspace."""
import argparse
import json
from pathlib import Path
import re

import psutil

parser = argparse.ArgumentParser()
parser.add_argument("--close-superseded", action="store_true")
parser.add_argument("--close-run", action="append", default=[], help="Exact completed owned run whose server tree may be closed.")
args = parser.parse_args()
root = Path(__file__).resolve().parents[3]
runs = root / "evaluations/runs"
for proc in psutil.process_iter(["pid", "name", "cmdline", "memory_info"]):
    try:
        cwd = Path(proc.cwd()).resolve()
        if not cwd.is_relative_to(runs):
            continue
        run_id = cwd.relative_to(runs).parts[0]
        if not run_id.startswith("compact-") or "20261004" not in run_id:
            continue
        command = " ".join(proc.info["cmdline"] or [])
        if proc.info["name"].lower() not in {"node.exe", "chrome.exe", "headless_shell.exe"}:
            continue
        lower = command.lower()
        server = (proc.info["name"].lower() in {"chrome.exe","headless_shell.exe"} or
                  "slidev.mjs" in lower or ("npx-cli.js" in lower and " slidev" in lower) or
                  ("vite" in lower and "cli.js" in lower and "pi-coding-agent" not in lower))
        if not server or "pi-coding-agent" in lower:
            continue
        obsolete = bool(re.search(r"20261004-(?:final|v2|v3|luna-\d)(?:-|$)", run_id))
        print(json.dumps({"pid": proc.pid, "run": run_id, "rssMb": round(proc.memory_info().rss / 1024**2, 1),
                          "superseded": obsolete, "command": command[:220]}))
        if (args.close_superseded and obsolete) or run_id in args.close_run:
            for child in reversed(proc.children(recursive=True)):
                try:
                    child.terminate()
                except psutil.Error:
                    pass
            proc.terminate()
            print(json.dumps({"closedSupersededTrialServer": proc.pid, "run": run_id}))
    except (psutil.Error, IndexError):
        continue
