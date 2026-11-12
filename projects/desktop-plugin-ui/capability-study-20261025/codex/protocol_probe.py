#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Exercise installed Codex app-server UI contracts without model inference."""
import argparse
import datetime as dt
import json
import os
import queue
import subprocess
import sys
import threading
import time
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("--codex", type=Path, required=True)
parser.add_argument("--out", type=Path, required=True)
parser.add_argument("--no-openai-form", action="store_true")
parser.add_argument("--approval-policy", choices=("never", "on-request"), default="never")
args = parser.parse_args()
out = args.out.resolve()
out.mkdir(parents=True, exist_ok=True)
if (out / "mcp-events.jsonl").exists() or (out / "protocol-events.jsonl").exists():
    parser.error("Choose a fresh output folder; existing evidence will not be overwritten.")
probe_home = out / "isolated-home"
probe_home.mkdir(exist_ok=True)
fixture = Path(__file__).with_name("fixture.py").resolve()
fixture_log = out / "mcp-events.jsonl"
config = {"mcp_servers": {"ui_probe": {"command": sys.executable, "args": [str(fixture), "--log", str(fixture_log)], "startup_timeout_sec": 15}}}
env = dict(os.environ, CODEX_HOME=str(probe_home))
command = [str(args.codex), "app-server", "--listen", "stdio://", "-c", "project_doc_max_bytes=0"]
for key, value in config["mcp_servers"]["ui_probe"].items():
    # JSON strings and arrays are valid TOML for these primitive values.
    command.extend(["-c", f"mcp_servers.ui_probe.{key}={json.dumps(value)}"])
proc = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8", env=env, cwd=out)
received = queue.Queue()
stderr = []
events = []
checks = []


def read_stdout():
    for line in proc.stdout:
        try:
            received.put(json.loads(line))
        except json.JSONDecodeError:
            received.put({"nonJsonStdout": line.rstrip()})


def read_stderr():
    for line in proc.stderr:
        stderr.append(line.rstrip())


threading.Thread(target=read_stdout, daemon=True).start()
threading.Thread(target=read_stderr, daemon=True).start()
next_id = 0


def send(message):
    events.append({"direction": "sent", "message": message})
    proc.stdin.write(json.dumps(message) + "\n")
    proc.stdin.flush()


def call(method, params, timeout=30):
    global next_id
    next_id += 1
    identifier = next_id
    send({"id": identifier, "method": method, "params": params})
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        message = received.get(timeout=max(0.1, deadline - time.monotonic()))
        events.append({"direction": "received", "message": message})
        if "id" in message and "method" in message:
            if message["method"] == "mcpServer/elicitation/request":
                mode = message["params"].get("mode")
                result = {"action": "accept", "content": {"choice": "alpha", "enabled": True, "record": {"name": "synthetic"}}} if mode != "url" else {"action": "decline", "content": None}
                send({"id": message["id"], "result": result})
            else:
                send({"id": message["id"], "error": {"code": -32601, "message": "Probe client has no handler"}})
        if message.get("id") == identifier and "method" not in message:
            return message
    raise TimeoutError(method)


def check(identifier, passed, detail):
    checks.append({"id": identifier, "passed": bool(passed), "detail": detail})


try:
    initialize = call("initialize", {"clientInfo": {"name": "plugin_ui_boundary_probe", "title": "Plugin UI Boundary Probe", "version": "1.0.0"}, "capabilities": {"experimentalApi": True, "mcpServerOpenaiFormElicitation": not args.no_openai_form}})
    check("codex-initialize", "result" in initialize, initialize)
    send({"method": "initialized", "params": {}})
    thread = call("thread/start", {"cwd": str(out), "ephemeral": True, "approvalPolicy": args.approval_policy, "sandbox": "read-only", "baseInstructions": "Synthetic local UI protocol probe; do not invoke any model.", "developerInstructions": "Only synthetic fixture data is used."})
    thread_id = thread.get("result", {}).get("thread", {}).get("id")
    check("codex-ephemeral-thread", bool(thread_id), {"created": bool(thread_id)})
    if thread_id:
        inventory = call("mcpServerStatus/list", {"threadId": thread_id}, timeout=45)
        check("codex-mcp-inventory", "ui_probe" in json.dumps(inventory) and "ui_card" in json.dumps(inventory), inventory)
        for tool in ("ui_card", "image", "form", "url", "openai_form", "extended_form"):
            response = call("mcpServer/tool/call", {"threadId": thread_id, "server": "ui_probe", "tool": tool, "arguments": {}}, timeout=30)
            check("codex-direct-" + tool, "result" in response and "isError\": true" not in json.dumps(response), response)
            if tool in ("form", "url", "openai_form"):
                # Policy-specific expected values are established by the zero-model exploratory run.
                expected_action = "decline" if args.approval_policy == "never" or tool == "url" else "accept"
                check("codex-direct-" + tool + "-action", '"' + expected_action + '"' in str(response).replace("\\\"", '"'), {"approvalPolicy": args.approval_policy, "expectedAction": expected_action})
            elif tool == "extended_form":
                check("codex-thread-extended-form-rejected", "-32601" in str(response) and "elicitation/create" in str(response), "Nested object requestedSchema failed on the thread MCP connection, which did not advertise openai/form even when the app-scoped connection did.")
        resource = call("mcpServer/resource/read", {"threadId": thread_id, "server": "ui_probe", "uri": "ui://codex-ui-probe/card.html"})
        check("codex-ui-resource-bytes", "UI_PROBE_BUTTON" in json.dumps(resource), resource)
    unsupported = call("ui/initialize", {"appInfo": {"name": "ui-boundary-probe", "version": "1"}, "appCapabilities": {}, "protocolVersion": "2026-01-26"})
    check("codex-appserver-is-not-mcp-app-bridge", "error" in unsupported, unsupported)
    fixture_events = [json.loads(line) for line in fixture_log.read_text(encoding="utf-8").splitlines()]
    capabilities = [event.get("params", {}).get("capabilities", {}) for event in fixture_events if event.get("method") == "initialize"]
    check("codex-negotiates-elicitation", any("elicitation" in cap and "form" in cap["elicitation"] and "url" in cap["elicitation"] for cap in capabilities), capabilities)
    check("codex-no-mcp-apps-extension-advertised", not any("io.modelcontextprotocol/ui" in cap.get("extensions", {}) for cap in capabilities), capabilities)
    callbacks = [event for event in events if event["direction"] == "received" and event["message"].get("method") == "mcpServer/elicitation/request"]
    expected_callback_count = 0 if args.approval_policy == "never" else 3
    check("codex-direct-elicitation-host-callbacks", len(callbacks) == expected_callback_count, {"callbackCount": len(callbacks), "expected": expected_callback_count, "approvalPolicy": args.approval_policy})
except Exception as error:
    checks.append({"id": "probe-unexpected-error", "passed": False, "detail": type(error).__name__ + ": " + str(error)})
finally:
    proc.terminate()
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait(timeout=5)
    (out / "protocol-events.jsonl").write_text("\n".join(json.dumps(event) for event in events) + "\n", encoding="utf-8")
    (out / "stderr.txt").write_text("\n".join(stderr), encoding="utf-8")
    report = {"capturedAtUtc": dt.datetime.now(dt.timezone.utc).isoformat(), "modelCalls": 0, "modelTurnsStarted": 0, "approvalPolicy": args.approval_policy, "openaiFormOptIn": not args.no_openai_form, "scope": "installed Codex app-server stdio protocol; no frontend renderer", "checks": checks, "passed": sum(c["passed"] for c in checks), "total": len(checks)}
    (out / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({"passed": report["passed"], "total": report["total"], "output": str(out), "checks": [{"id": c["id"], "passed": c["passed"]} for c in checks]}, indent=2))
raise SystemExit(0 if report["passed"] == report["total"] else 1)
