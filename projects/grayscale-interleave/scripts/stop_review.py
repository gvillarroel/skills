#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["psutil>=7"]
# ///
"""Stop only a verified stalled native reviewer and its own child processes."""
import sys
import psutil

process = psutil.Process(int(sys.argv[1]))
command = " ".join(process.cmdline())
if "evaluations" not in command or "grayscale-interleave" not in command or "review_outputs.py" not in command:
    raise ValueError("The target is not this revision's native reviewer")
children = process.children(recursive=True)
for child in reversed(children):
    try:
        child.terminate()
    except psutil.NoSuchProcess:
        pass
process.terminate()
print(f"Stopped only native reviewer {process.pid} and its verified process descendants.")
