#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Inventory public build/help metadata without prompts or account-file reads."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess

PROJECT = Path(__file__).resolve().parents[2]
ARTIFACTS = PROJECT / "artifacts/capability-study-20261025/copilot"
PREVIOUS = PROJECT / "artifacts/cross-assistant/copilot"
ARTIFACTS.mkdir(parents=True, exist_ok=True)
CLI = PREVIOUS / "cli103/package/copilot.exe"
CODE = PREVIOUS / "vscode/bin/code.cmd"
commands = []
env = os.environ.copy()
env.update(COPILOT_AUTO_UPDATE="false", COPILOT_OFFLINE="true")


def run(executable, args, label):
    command = [str(executable), *args]
    result = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", timeout=35, env=env)
    commands.append({"label": label, "command": command, "exit_code": result.returncode,
                     "stdout": result.stdout, "stderr": result.stderr})


run(shutil.which("copilot"), ["--version"], "installed-cli-version")
for arguments in (["--version"], ["--help"], ["login", "--help"], ["plugin", "--help"],
                  ["mcp", "--help"], ["help", "commands"], ["help", "permissions"],
                  ["help", "limits"], ["help", "providers"]):
    run(CLI, arguments, "task-local-cli-" + "-".join(arguments))
run(CODE, ["--version"], "portable-vscode-version")
sdk = json.loads((PREVIOUS / "package/package.json").read_text(encoding="utf-8"))
extension = json.loads((PREVIOUS / "vscode/e646868227/resources/app/extensions/copilot/package.json").read_text(encoding="utf-8"))
report = {"timestamp_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
          "model_prompts": 0, "gui_launched": False, "account_files_read": False,
          "commands": commands,
          "cli_sha256": hashlib.sha256(CLI.read_bytes()).hexdigest(),
          "sdk": {key: sdk.get(key) for key in ("name", "version", "copilotCliVersion")},
          "bundled_extension": {key: extension.get(key) for key in ("name", "publisher", "version", "engines")},
          "auth_readiness": {"state": "not-queried-by-this-help-inventory",
                             "note": "Login help has no status subcommand. No login flow, device code, token, profile, or account identifier is collected."}}
destination = ARTIFACTS / "inventory.json"
destination.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"output": str(destination), "commands": len(commands),
                  "exit_codes": [row["exit_code"] for row in commands], "model_prompts": 0,
                  "sdk": report["sdk"], "bundled_extension": report["bundled_extension"]}, indent=2))
