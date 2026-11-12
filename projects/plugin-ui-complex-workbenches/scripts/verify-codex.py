#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Exercise the installed Codex app-server with task-local read-only MCP config."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import queue
import shutil
import subprocess
import threading
import time

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--codex", type=Path, required=True)
    parser.add_argument("--label", default="desktop-core")
    parser.add_argument("--packaged", action="store_true", help="Install the portable package through a task-local marketplace instead of direct MCP config.")
    args = parser.parse_args()
    if not args.label.replace("-", "").isalnum():
        parser.error("Use a simple local run label.")
    output = ROOT / "artifacts/reviews/codex" / args.label
    output.mkdir(parents=True, exist_ok=True)
    task_home = output / "codex-home"
    task_home.mkdir(exist_ok=True)
    package = ROOT / "artifacts/packages/incident-analysis"
    config = 'approval_policy = "never"\nsandbox_mode = "read-only"\n'
    if not args.packaged:
        config += '[mcp_servers.incident-analysis]\ncommand = "node"\nargs = [' + json.dumps(str(package / "server.mjs")) + ']\ncwd = ' + json.dumps(str(package)) + '\nstartup_timeout_sec = 20\n'
    (task_home / "config.toml").write_text(config, encoding="utf-8")
    env = {**os.environ, "CODEX_HOME": str(task_home), "TEMP": str(output), "TMP": str(output)}
    for key in ["OPENAI_API_KEY", "CODEX_API_KEY", "CHATGPT_ACCESS_TOKEN"]:
        env.pop(key, None)
    version = subprocess.run([str(args.codex), "--version"], env=env, cwd=output, capture_output=True, text=True, encoding="utf-8", timeout=15).stdout.strip()
    package_checks = []
    if args.packaged:
        marketplace = output / "marketplace"
        catalog = marketplace / ".agents/plugins/marketplace.json"
        catalog.parent.mkdir(parents=True, exist_ok=True)
        copied = marketplace / "plugins/incident-analysis"
        shutil.copytree(package, copied)
        catalog.write_text(json.dumps({"name": "incident-review-local", "interface": {"displayName": "Incident Analysis Local Review"}, "plugins": [{"name": "incident-analysis", "source": {"source": "local", "path": "./plugins/incident-analysis"}, "policy": {"installation": "AVAILABLE", "authentication": "ON_INSTALL"}, "category": "Productivity"}]}, indent=2), encoding="utf-8")
        steps = [
            ("marketplace-add", ["plugin", "marketplace", "add", str(marketplace), "--json"]),
            ("plugin-list", ["plugin", "list", "--available", "--json"]),
            ("plugin-add", ["plugin", "add", "incident-analysis@incident-review-local", "--json"]),
        ]
        for name, parameters in steps:
            result = subprocess.run([str(args.codex), *parameters], env=env, cwd=output, capture_output=True, text=True, encoding="utf-8", timeout=60)
            (output / f"{name}.json").write_text(result.stdout, encoding="utf-8")
            (output / f"{name}.stderr.txt").write_text(result.stderr, encoding="utf-8")
            passed = result.returncode == 0 and "incident-review-local" in result.stdout
            if name == "plugin-list":
                passed = passed and "incident-analysis" in result.stdout
            package_checks.append({"name": f"Installed core {name} accepts the exact local portable package", "passed": passed})
            if not passed:
                report = {"passed": False, "version": version, "checks": package_checks, "failure": f"{name} failed", "hostPaintVerified": False, "scope": "Task-local portable marketplace trial; no direct MCP fallback or model turn."}
                (output / "review.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
                print(json.dumps(report))
                return 1
        cached = [file for file in (task_home / "plugins/cache").rglob("server.mjs") if hashlib.sha256(file.read_bytes()).digest() == hashlib.sha256((package / "server.mjs").read_bytes()).digest()]
        package_checks.append({"name": "Installed cache contains the exact portable server bytes", "passed": bool(cached)})
        package_checks.append({"name": "Plugin route has no direct mcp_servers configuration", "passed": "mcp_servers" not in (task_home / "config.toml").read_text(encoding="utf-8")})
    child = subprocess.Popen([str(args.codex), "app-server", "--listen", "stdio://", "-c", "project_doc_max_bytes=0"], env=env, cwd=output, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8")
    incoming, transcript, checks, stderr = queue.Queue(), [], package_checks, []

    def read():
        for line in child.stdout:
            try:
                incoming.put(json.loads(line))
            except ValueError:
                incoming.put({"invalidJson": line})

    threading.Thread(target=read, daemon=True).start()
    threading.Thread(target=lambda: stderr.extend(child.stderr.readlines()), daemon=True).start()
    sequence = 0

    def send(value):
        transcript.append({"direction": "sent", "message": value})
        child.stdin.write(json.dumps(value) + "\n")
        child.stdin.flush()

    def call(method, params):
        nonlocal sequence
        sequence += 1
        identifier = sequence
        send({"jsonrpc": "2.0", "id": identifier, "method": method, "params": params})
        deadline = time.monotonic() + 30
        while time.monotonic() < deadline:
            message = incoming.get(timeout=max(.01, deadline - time.monotonic()))
            transcript.append({"direction": "received", "message": message})
            if message.get("id") == identifier and "method" not in message:
                if "error" in message:
                    raise ValueError(json.dumps(message["error"]))
                return message.get("result", {})
            if "method" in message and "id" in message:
                send({"jsonrpc": "2.0", "id": message["id"], "error": {"code": -32601, "message": "This read-only fixture has no model, UI or approval callback."}})
        raise TimeoutError(method)

    def check(name, passed):
        checks.append({"name": name, "passed": bool(passed)})
        if not passed:
            raise ValueError(name)

    failure = None
    try:
        initialized = call("initialize", {"clientInfo": {"name": "rich_ui_lab", "version": "1.0.0"}, "capabilities": {"experimentalApi": True}})
        check("Installed app-server initializes", bool(initialized))
        send({"method": "initialized", "params": {}})
        thread = call("thread/start", {"cwd": str(output), "ephemeral": True, "approvalPolicy": "never", "sandbox": "read-only", "baseInstructions": "Synthetic direct MCP protocol test. Do not invoke a model."})
        thread_id = thread.get("thread", {}).get("id")
        check("Ephemeral thread starts without a turn", bool(thread_id))
        inventory = call("mcpServerStatus/list", {"threadId": thread_id})
        servers = inventory.get("data", [])
        matching = [s for s in servers if "open_incident_analysis" in json.dumps(s)]
        check("Configured MCP server and actual tools are discovered", bool(matching))
        response = call("mcpServer/tool/call", {"threadId": thread_id, "server": matching[0]["name"], "tool": "open_incident_analysis", "arguments": {}})
        text = json.dumps(response)
        check("Direct tool result preserves the exact synthetic snapshot", "serviceCount" in text and "96" in text and "9216" in text)
        check("No model turn was requested", not any(item["message"].get("method", "").startswith("turn/") for item in transcript))
    except Exception as error:
        failure = f"{type(error).__name__}: {error}"
    finally:
        child.stdin.close()
        try:
            child.wait(timeout=5)
        except subprocess.TimeoutExpired:
            child.terminate()
            child.wait(timeout=5)
        scope = "Installed Codex app-server with isolated-home portable marketplace installation, verified cache bytes, discovery and exact read-only tool. Stock frontend paint remains separate." if args.packaged else "Installed Codex app-server with isolated-home MCP configuration and direct read-only tool. Portable plugin catalog installation and frontend paint are separate."
        report = {"passed": not failure and all(c["passed"] for c in checks), "version": version, "checks": checks, "failure": failure, "hostPaintVerified": False, "scope": scope}
        (output / "events.json").write_text(json.dumps(transcript, indent=2), encoding="utf-8")
        (output / "stderr.txt").write_text("".join(stderr), encoding="utf-8")
        (output / "review.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
        print(json.dumps(report))
    return int(not report["passed"])


if __name__ == "__main__":
    raise SystemExit(main())
