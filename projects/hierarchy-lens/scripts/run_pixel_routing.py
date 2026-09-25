#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Run one unforced metadata routing probe in an isolated workspace."""

import datetime
import hashlib
import json
import shutil
import subprocess
from pathlib import Path

root = Path.cwd().resolve()
run = root / "evaluations/runs/hierarchy-pixels-routing-20260925-luna-1"
workspace = run / "workspace"
workspace.mkdir(parents=True, exist_ok=False)
prompt = (root / "evaluations/pi-prompts/hierarchy-pixels-routing.md").read_text(encoding="utf-8")
(workspace / "prompt.md").write_text(prompt, encoding="utf-8")
executable = shutil.which("pi.cmd") or shutil.which("pi")
if not executable:
    raise SystemExit("Pi is not available")
command = [executable, "--model", "openai-codex/gpt-5.6-luna", "--thinking", "high", "--mode", "json",
           "--no-context-files", "--no-extensions", "--no-skills", "--no-prompt-templates", "--no-themes", "--no-session",
           "--print", "Read prompt.md and complete its routing task. Write routing.json in this workspace."]
(run / "manifest.json").write_text(json.dumps({"command": command, "cwd": str(workspace), "model": "openai-codex/gpt-5.6-luna",
    "forcedSkill": False, "promptSha256": hashlib.sha256(prompt.encode()).hexdigest(),
    "startedAt": datetime.datetime.now(datetime.timezone.utc).isoformat()}, indent=2), encoding="utf-8")
result = subprocess.run(command, cwd=workspace, capture_output=True, timeout=180)
(run / "events.jsonl").write_bytes(result.stdout)
(run / "stderr.txt").write_bytes(result.stderr)
routing = json.loads((workspace / "routing.json").read_text(encoding="utf-8"))
expected = {1: True, 2: True, 3: False, 4: False, 5: False, 6: True, 7: False, 8: True}
passed = result.returncode == 0 and len(routing) == 8 and {r["request"]: r["useSkill"] for r in routing} == expected
report = {"passed": passed, "cases": 8, "model": "openai-codex/gpt-5.6-luna", "forcedSkill": False, "routing": routing}
(run / "result.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
print(json.dumps(report))
raise SystemExit(0 if passed else 1)
