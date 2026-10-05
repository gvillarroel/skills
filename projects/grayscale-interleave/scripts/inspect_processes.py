#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["psutil>=7"]
# ///
"""Inspect only this revision's current test process tree."""
import json
import psutil

for process in psutil.process_iter(["pid", "ppid", "name", "cmdline", "memory_info"]):
    try:
        command = " ".join(process.info["cmdline"] or [])
        if any(token in command for token in ("review_outputs.py", "playwright", "chrome-headless-shell")):
            print(json.dumps({"pid": process.pid, "ppid": process.ppid(), "name": process.name(),
                              "memoryMB": round(process.memory_info().rss / 1048576, 1), "command": command[:500]}))
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        pass
