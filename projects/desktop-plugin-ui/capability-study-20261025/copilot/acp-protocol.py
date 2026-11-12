#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Check current ACP negotiation and one invalid UI method without inference."""
import datetime
import json
import os
from pathlib import Path
import queue
import subprocess
import threading
import time

project = Path(__file__).resolve().parents[2]
out = project / "artifacts/capability-study-20261025/copilot"
out.mkdir(parents=True, exist_ok=True)
exe = project / "artifacts/cross-assistant/copilot/cli103/package/copilot.exe"
env = os.environ.copy()
env.update(COPILOT_HOME=str(out / "acp-profile"), COPILOT_AUTO_UPDATE="false", COPILOT_OFFLINE="true",
           COPILOT_PROVIDER_BASE_URL="http://127.0.0.1:9/v1", COPILOT_MODEL="ui-study-no-inference",
           COPILOT_PROVIDER_MODEL_ID="ui-study-no-inference")
for key in ("GITHUB_TOKEN", "GH_TOKEN", "COPILOT_GITHUB_TOKEN"):
    env.pop(key, None)
command = [str(exe), "--acp", "--no-auto-update", "--disable-client-telemetry", "--disable-builtin-mcps"]
proc = subprocess.Popen(command, cwd=Path(__file__).parent, env=env, stdin=subprocess.PIPE,
                        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8")
messages = queue.Queue()
stderr = []


def read_stdout():
    for line in proc.stdout:
        try:
            messages.put(json.loads(line))
        except json.JSONDecodeError:
            messages.put({"unexpected_stdout": line[:200]})


threading.Thread(target=read_stdout, daemon=True).start()
threading.Thread(target=lambda: stderr.extend(proc.stderr.readlines()), daemon=True).start()
requests = [
    {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {
        "protocolVersion": 1, "clientCapabilities": {},
        "clientInfo": {"name": "copilot-capability-study", "version": "1.0.0"}}},
    {"jsonrpc": "2.0", "id": 2, "method": "ui/show", "params": {"html": "<button>Probe</button>"}},
]
responses = []
write_error = None
close_error = None
try:
    for request in requests:
        try:
            proc.stdin.write(json.dumps(request) + "\n")
            proc.stdin.flush()
        except OSError as error:
            write_error = str(error)
            break
        deadline = time.monotonic() + 25
        while time.monotonic() < deadline:
            try:
                response = messages.get(timeout=.25)
            except queue.Empty:
                if proc.poll() is not None:
                    break
                continue
            responses.append(response)
            if response.get("id") == request["id"]:
                break
finally:
    try:
        proc.stdin.close()
    except OSError as error:
        close_error = str(error)
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        proc.terminate()
        proc.wait(timeout=5)
init = next((row for row in responses if row.get("id") == 1), {})
negative = next((row for row in responses if row.get("id") == 2), {})
checks = [
    {"id": "initialize-response", "passed": "result" in init},
    {"id": "invented-ui-show-rejected", "passed": negative.get("error", {}).get("code") == -32601},
]
report = {"timestamp_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
          "passed": all(row["passed"] for row in checks), "model_prompts": 0,
          "session_created": False, "gui_launched": False, "command": command,
          "requests": requests, "responses": responses, "stderr": "".join(stderr), "checks": checks,
          "write_error": write_error, "close_error": close_error, "process_exit_code": proc.returncode,
          "scope": "Only ACP initialization and this exact unsupported method are tested; no rendering exclusion is inferred."}
(out / "acp-protocol.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
print(json.dumps(report, indent=2))
raise SystemExit(0 if report["passed"] else 1)
