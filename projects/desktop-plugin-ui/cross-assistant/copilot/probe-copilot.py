#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Run no-inference CLI/ACP checks without reading account secrets."""
from __future__ import annotations

import datetime
import argparse
import json
import os
from pathlib import Path
import queue
import shutil
import subprocess
import threading
import time

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "artifacts/cross-assistant/copilot"
OUT.mkdir(parents=True, exist_ok=True)
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--executable", default=shutil.which("copilot"))
parser.add_argument("--output-name", default="copilot-cli-zero-model.json")
args = parser.parse_args()
EXE = args.executable
if not EXE:
    raise SystemExit("Copilot CLI was not found.")


def cli(args):
    result = subprocess.run([EXE, *args], capture_output=True, text=True, timeout=25)
    return {"command": ["copilot", *args], "exit_code": result.returncode,
            "stdout": result.stdout, "stderr": result.stderr}


def acp():
    # No session/prompt is created; initialize and unknown-method are local RPCs.
    env = os.environ.copy()
    env["COPILOT_AUTO_UPDATE"] = "false"
    proc = subprocess.Popen([EXE, "--acp", "--no-auto-update", "--disable-builtin-mcps"],
                            cwd=Path(__file__).parent, env=env, stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    messages = queue.Queue()
    errors = []
    def read_stdout():
        for line in proc.stdout:
            try:
                messages.put(json.loads(line))
            except json.JSONDecodeError:
                messages.put({"non_json": line[:200]})
    def read_stderr():
        for line in proc.stderr:
            errors.append(line)
    threading.Thread(target=read_stdout, daemon=True).start()
    threading.Thread(target=read_stderr, daemon=True).start()
    requests = [
        {"jsonrpc":"2.0", "id":1, "method":"initialize", "params":{
            "protocolVersion":1, "clientCapabilities":{},
            "clientInfo":{"name":"ui-evidence-probe", "version":"1.0.0"}}},
        {"jsonrpc":"2.0", "id":2, "method":"ui/show", "params":{"html":"<button>Probe</button>"}}
    ]
    received = []
    try:
        for request in requests:
            try:
                proc.stdin.write(json.dumps(request) + "\n")
                proc.stdin.flush()
            except OSError as error:
                received.append({"write_error":str(error)})
                break
            deadline = time.monotonic() + 25
            while time.monotonic() < deadline:
                try:
                    value = messages.get(timeout=0.25)
                except queue.Empty:
                    if proc.poll() is not None:
                        break
                    continue
                received.append(value)
                if value.get("id") == request["id"]:
                    break
    finally:
        try:
            proc.stdin.close()
        except OSError:
            pass
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.terminate()
            proc.wait(timeout=5)
    return {"command":["copilot","--acp","--no-auto-update","--disable-builtin-mcps"],
            "requests":requests,"responses":received,"stderr":"".join(errors),
            "exit_code":proc.returncode,"session_created":False,"model_prompts":0}


report = {"timestamp_utc":datetime.datetime.now(datetime.timezone.utc).isoformat(),
          "platform":"Windows", "model_prompts":0,
          "checks":[cli(["--version"]), cli(["--help"]),
                    cli(["plugin","--help"]),cli(["help","limits"]),
                    cli(["help","commands"]),cli(["mcp","--help"]),acp()]}
(OUT / args.output_name).write_text(json.dumps(report, indent=2), encoding="utf-8")
print(json.dumps({"output":str(OUT / args.output_name),
                  "model_prompts":0,"acp":report["checks"][-1]}, indent=2))
