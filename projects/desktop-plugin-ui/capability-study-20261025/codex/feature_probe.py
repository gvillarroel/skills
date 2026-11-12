#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Observe current Codex state/media/form contracts without starting a model turn."""

import argparse
import base64
import datetime as dt
import io
import json
import os
import queue
import subprocess
import sys
import threading
import time
import wave
from pathlib import Path

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--codex", type=Path, required=True)
parser.add_argument("--out", type=Path, required=True)
parser.add_argument("--nested-error-code", type=int, choices=(-32601, -32602), required=True)
parser.add_argument("--approval-policy", choices=("never", "on-request"), default="on-request")
parser.add_argument("--no-openai-form", action="store_true")
parser.add_argument("--enable-mcp-apps", action="store_true", help="Enable only this process's experimental MCP Apps flag.")
args = parser.parse_args()
out = args.out.resolve()
if out.exists():
    parser.error("Choose a fresh directory; previous evidence will not be overwritten.")
out.mkdir(parents=True)
home = out / "isolated-home"
home.mkdir()
fixture = Path(__file__).with_name("feature_fixture.py").resolve()
log = out / "mcp-events.jsonl"
command = [str(args.codex), "app-server", "--listen", "stdio://", "-c", "project_doc_max_bytes=0"]
if args.enable_mcp_apps:
    command.extend(["-c", "features.enable_mcp_apps=true"])
for key, value in {"command": sys.executable, "args": [str(fixture), "--log", str(log)], "startup_timeout_sec": 15}.items():
    command.extend(["-c", f"mcp_servers.feature_study.{key}={json.dumps(value)}"])
proc = subprocess.Popen(command, cwd=out, env=dict(os.environ, CODEX_HOME=str(home)),
                        stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                        text=True, encoding="utf-8")
received = queue.Queue()
events, stderr, checks, observations = [], [], [], {}
next_id = 0


def reader():
    for line in proc.stdout:
        try:
            received.put(json.loads(line))
        except ValueError:
            received.put({"nonJsonStdout": line.rstrip()})


def error_reader():
    stderr.extend(line.rstrip() for line in proc.stderr)


threading.Thread(target=reader, daemon=True).start()
threading.Thread(target=error_reader, daemon=True).start()


def send(message):
    events.append({"direction": "sent", "message": message})
    proc.stdin.write(json.dumps(message) + "\n")
    proc.stdin.flush()


def call(method, params, timeout=35):
    global next_id
    next_id += 1
    identifier = next_id
    send({"id": identifier, "method": method, "params": params})
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        message = received.get(timeout=max(.1, deadline - time.monotonic()))
        events.append({"direction": "received", "message": message})
        if "id" in message and "method" in message:
            if message["method"] == "mcpServer/elicitation/request":
                text = message["params"].get("message", "")
                action = "cancel" if text.startswith("form_cancel") else "decline" if text.startswith("form_decline") else "accept"
                content = {"choice": "alpha", "title": "Synthetic title", "count": 2, "enabled": True, "tags": ["one"]} if action == "accept" else None
                send({"id": message["id"], "result": {"action": action, "content": content}})
            else:
                send({"id": message["id"], "error": {"code": -32601, "message": "No synthetic handler for this request"}})
        if message.get("id") == identifier and "method" not in message:
            return message
    raise TimeoutError(method)


def check(name, passed, detail):
    checks.append({"id": name, "passed": bool(passed), "detail": detail})


def start_thread():
    response = call("thread/start", {"cwd": str(out), "ephemeral": True, "approvalPolicy": args.approval_policy,
                                    "sandbox": "read-only", "baseInstructions": "Synthetic protocol study. Do not invoke a model."})
    identifier = response.get("result", {}).get("thread", {}).get("id")
    if not identifier:
        raise RuntimeError("Synthetic thread creation failed: " + json.dumps(response))
    return identifier


def tool(thread, name, arguments=None, meta=None):
    params = {"threadId": thread, "server": "feature_study", "tool": name, "arguments": arguments or {}}
    if meta:
        params["_meta"] = meta
    response = call("mcpServer/tool/call", params)
    observations[name] = response
    return response


try:
    init = call("initialize", {"clientInfo": {"name": "codex_feature_study", "version": "1.0.0"},
                              "capabilities": {"experimentalApi": True, "mcpServerOpenaiFormElicitation": not args.no_openai_form}})
    check("initialize", "result" in init, init)
    send({"method": "initialized", "params": {}})
    thread = start_thread()
    check("ephemeral-thread", True, "Only this newly created synthetic thread is read.")
    inventory = call("mcpServerStatus/list", {"threadId": thread})
    check("fixture-discovery", "feature_study" in json.dumps(inventory), inventory)
    panel = tool(thread, "panel")
    check("panel-text-data-meta", all(term in json.dumps(panel) for term in ("Synthetic panel fallback", "structuredContent", "resourceUri")), panel)
    state = tool(thread, "state_get")
    check("state-initial", state.get("result", {}).get("structuredContent") == {"value": 0, "version": 0}, state)
    updated = tool(thread, "state_set", {"expectedVersion": 0})
    check("state-mutation", updated.get("result", {}).get("structuredContent") == {"value": 1, "version": 1}, updated)
    stale = tool(thread, "state_set", {"expectedVersion": 0})
    check("state-stale-rejected", stale.get("result", {}).get("isError") is True and stale.get("result", {}).get("structuredContent") == {"value": 1, "version": 1}, stale)
    audio_response = tool(thread, "audio")
    audio = next((item for item in audio_response.get("result", {}).get("content", []) if item.get("type") == "audio"), None)
    audio_valid = False
    if audio:
        with wave.open(io.BytesIO(base64.b64decode(audio["data"])), "rb") as stream:
            audio_valid = stream.getnframes() == 80 and stream.getframerate() == 8000
    check("wav-transport-valid-bytes", audio_valid, {"audioContentReceived": bool(audio), "playbackTested": False})
    link = tool(thread, "resource_link")
    check("resource-link-transport", "resource_link" in json.dumps(link) and "text/csv" in json.dumps(link), link)
    embedded = tool(thread, "embedded_resource")
    check("embedded-svg-bytes", "image/svg+xml" in json.dumps(embedded) and "Synthetic chart" in json.dumps(embedded), embedded)
    progress = tool(thread, "progress", meta={"progressToken": "study-progress"})
    check("progress-final-result", progress.get("result", {}).get("structuredContent") == {"complete": True}, progress)
    for name in ("form_types", "form_decline", "form_cancel", "openai_flat", "openai_alias", "nested_invalid"):
        response = tool(thread, name)
        if name == "nested_invalid":
            check("nested-invalid-version-aware", str(args.nested_error_code) in json.dumps(response), response)
        elif name != "openai_alias":
            expected = "decline" if args.approval_policy == "never" or name == "form_decline" else "cancel" if name == "form_cancel" else "accept"
            check(name + "-response", '"action": "' + expected + '"' in json.dumps(response).replace('\\"', '"'), response)
    invalid = tool(thread, "bad_content")
    check("invalid-content-rejected", "error" in invalid or invalid.get("result", {}).get("isError") is True, invalid)
    for uri, marker in (("ui://codex-feature-study/panel.html", "FEATURE_PANEL_READY"), ("resource://codex-feature-study/sample.csv", "Synthetic record")):
        response = call("mcpServer/resource/read", {"threadId": thread, "server": "feature_study", "uri": uri})
        check("read-resource-" + marker, marker in json.dumps(response), response)
    observations["modelCatalog"] = call("model/list", {"limit": 3, "includeHidden": False})
    observations["threadMetadataRead"] = call("thread/read", {"threadId": thread, "includeTurns": False})
    wrong = call("ui/initialize", {"appInfo": {"name": "Synthetic app", "version": "1"}, "protocolVersion": "2026-01-26", "appCapabilities": {}})
    check("app-server-is-not-iframe-bridge", "error" in wrong, wrong)
    second_thread = start_thread()
    call("mcpServerStatus/list", {"threadId": second_thread})
    second_state = tool(second_thread, "state_get")
    observations["secondThreadState"] = second_state
    check("second-thread-state-readable", isinstance(second_state.get("result", {}).get("structuredContent", {}).get("version"), int), second_state)
except Exception as error:
    check("unexpected-probe-error", False, type(error).__name__ + ": " + str(error))
finally:
    proc.terminate()
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait(timeout=5)
    (out / "protocol-events.jsonl").write_text("\n".join(json.dumps(event) for event in events) + "\n", encoding="utf-8")
    (out / "stderr.txt").write_text("\n".join(stderr), encoding="utf-8")
    fixture_events = [json.loads(line) for line in log.read_text(encoding="utf-8").splitlines()] if log.exists() else []
    connections = {}
    for event in fixture_events:
        record = connections.setdefault(str(event["pid"]), {"capabilities": None, "toolCalls": []})
        message = event["message"]
        if message.get("method") == "initialize":
            record["capabilities"] = message.get("params", {}).get("capabilities")
        elif message.get("method") == "tools/call":
            record["toolCalls"].append(message.get("params", {}).get("name"))
    callbacks = [event["message"]["params"] for event in events if event["direction"] == "received" and event["message"].get("method") == "mcpServer/elicitation/request"]
    progress_events = [event["message"] for event in events if event["direction"] == "received" and "progress" in event["message"].get("method", "").lower()]
    report = {"capturedAtUtc": dt.datetime.now(dt.timezone.utc).isoformat(), "modelTurnsStarted": 0,
              "scope": "Backend JSON-RPC and synthetic MCP transport/state; no frontend paint or real account data",
              "approvalPolicy": args.approval_policy, "openaiFormOptIn": not args.no_openai_form,
              "experimentalMcpAppsEnabled": args.enable_mcp_apps,
              "expectedNestedErrorCode": args.nested_error_code, "passed": sum(item["passed"] for item in checks),
              "total": len(checks), "checks": checks, "observations": observations,
              "connections": connections, "elicitationCallbacks": callbacks, "progressEvents": progress_events}
    (out / "report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: report[key] for key in ("passed", "total", "modelTurnsStarted", "approvalPolicy", "expectedNestedErrorCode")}, indent=2))
raise SystemExit(0 if report["passed"] == report["total"] else 1)
