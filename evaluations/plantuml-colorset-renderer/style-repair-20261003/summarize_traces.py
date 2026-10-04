#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Run the preregistered trace checks with structured arguments on Windows."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import subprocess


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-id", action="append", required=True)
    args = parser.parse_args()
    failed = False
    for run_id in args.run_id:
        if not re.fullmatch(r"[a-zA-Z0-9][a-zA-Z0-9._-]*", run_id):
            parser.error("Run ID must be a safe directory name.")
        run_dir = ROOT / "evaluations/runs" / run_id
        command = [
            "uv", "run", "--script", "scripts/summarize-pi-json-events.py",
            (run_dir / "events.jsonl").relative_to(ROOT).as_posix(),
            "--output", (run_dir / "read-surface.json").relative_to(ROOT).as_posix(),
            "--require-model", "gpt-5.6-luna", "--require-tool-call",
            "--fail-on-invalid-json", "--fail-on-tool-error",
            "--require-read", "../prompt.md",
            "--forbid-read-regex", r"(?i)(^|[\\/])assets[\\/]examples([\\/]|$)",
            "--forbid-read-regex", r"(?i)^skills[\\/](?!plantuml-colorset-renderer([\\/]|$))",
        ]
        if not (run_dir / "events.jsonl").is_file():
            print(json.dumps({"runId": run_id, "skipped": "No Pi event trace exists."}))
            failed = True
            continue
        result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True,
                                encoding="utf-8", errors="replace", check=False)
        (run_dir / "trace-dispatch.json").write_text(
            json.dumps({"runId": run_id, "command": command, "exitCode": result.returncode}, indent=2) + "\n",
            encoding="utf-8",
        )
        (run_dir / "trace-dispatch-log.txt").write_text(result.stdout + "\n" + result.stderr, encoding="utf-8")
        print(json.dumps({"runId": run_id, "exitCode": result.returncode}))
        failed |= result.returncode != 0
    return int(failed)


if __name__ == "__main__":
    raise SystemExit(main())
