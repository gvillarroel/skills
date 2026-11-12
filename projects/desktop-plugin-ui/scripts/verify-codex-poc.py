#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Independently exercise a generated Codex plugin without inference or global writes."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
from pathlib import Path
import queue
import shutil
import subprocess
import threading
import time


ROOT = Path(__file__).resolve().parents[3]


class Rpc:
    def __init__(self, argv: list[str], cwd: Path, env: dict[str, str]):
        self.process = subprocess.Popen(argv, cwd=cwd, env=env, stdin=subprocess.PIPE,
                                        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                        text=True, encoding="utf-8")
        self.received: queue.Queue = queue.Queue()
        self.events: list[dict] = []
        self.errors: list[str] = []
        self.next_id = 0
        self.form_action = "accept"
        self.form_confirm = True
        self.form_requests = 0
        self.model_requests = 0
        threading.Thread(target=self._read, daemon=True).start()
        threading.Thread(target=self._stderr, daemon=True).start()

    def _read(self):
        for line in self.process.stdout:
            try:
                self.received.put(json.loads(line))
            except ValueError:
                self.received.put({"nonJson": line.rstrip()})

    def _stderr(self):
        self.errors.extend(line.rstrip() for line in self.process.stderr)

    def send(self, message):
        self.events.append({"direction": "sent", "message": message})
        self.process.stdin.write(json.dumps(message) + "\n")
        self.process.stdin.flush()

    def call(self, method, params, timeout=25):
        self.next_id += 1
        identifier = self.next_id
        self.send({"jsonrpc": "2.0", "id": identifier, "method": method, "params": params})
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            message = self.received.get(timeout=max(.1, deadline - time.monotonic()))
            self.events.append({"direction": "received", "message": message})
            if "method" in message and "id" in message:
                if message["method"] in {"elicitation/create", "mcpServer/elicitation/request"}:
                    self.form_requests += 1
                    properties = message.get("params", {}).get("requestedSchema", {}).get("properties", {})
                    content = {}
                    for key, schema in properties.items():
                        if schema.get("type") == "boolean":
                            content[key] = self.form_confirm
                        elif "blocked" in schema.get("enum", []):
                            content[key] = "blocked"
                    result = {"action": self.form_action}
                    if self.form_action == "accept":
                        result["content"] = content
                    self.send({"jsonrpc": "2.0", "id": message["id"], "result": result})
                else:
                    if "sampling" in message["method"] or "turn" in message["method"]:
                        self.model_requests += 1
                    self.send({"jsonrpc": "2.0", "id": message["id"], "error": {
                        "code": -32601, "message": "Evaluator has no handler for this request"}})
            elif message.get("id") == identifier:
                return message
        raise TimeoutError(method)

    def close(self):
        if self.process.poll() is None:
            self.process.stdin.close()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.terminate()
                self.process.wait(timeout=5)


def encode(value):
    return json.dumps(value, ensure_ascii=False)


def result_rows(response):
    structured = response.get("result", {}).get("structuredContent")
    if structured is None:
        return None
    rows = {}

    def walk(value):
        if isinstance(value, list):
            for child in value:
                walk(child)
        elif isinstance(value, dict):
            if value.get("id") in {"R-21", "R-22", "R-23"}:
                rows[value["id"]] = value.get("state", value.get("status"))
            for key, child in value.items():
                if key in {"R-21", "R-22", "R-23"} and isinstance(child, str):
                    rows[key] = child
                walk(child)

    walk(structured)
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--codex", type=Path, required=True)
    parser.add_argument("--approval-policy", choices=("never", "on-request"), default="on-request")
    args = parser.parse_args()
    workspace, out = args.workspace.resolve(), args.out.resolve()
    if not workspace.is_relative_to(ROOT) or not out.is_relative_to(ROOT):
        parser.error("Workspace and evaluator output must stay inside the authorized repository")
    if out.exists():
        parser.error("Choose a fresh output directory; retained evidence is not overwritten")
    out.mkdir(parents=True)
    checks, commands = [], []

    def check(name, passed, detail=None, layer="independent protocol"):
        checks.append({"name": name, "passed": bool(passed), "detail": detail, "layer": layer})

    plugin = workspace / "poc"
    extracted = out / "extracted"
    shutil.copytree(plugin, extracted, ignore=shutil.ignore_patterns("node_modules", ".cache", ".npm-cache", "releases"))
    manifest = json.loads((extracted / "plugin.json").read_text(encoding="utf-8-sig"))
    config = json.loads((extracted / "mcp.json").read_text(encoding="utf-8-sig"))
    marketplace = json.loads((workspace / ".agents/plugins/marketplace.json").read_text(encoding="utf-8-sig"))
    check("portable-plugin-manifest", manifest.get("name") == "release-checks-poc" and bool(manifest.get("version")) and
          manifest.get("$schema", "").endswith("/plugin.schema.json"), manifest, "package inspection")
    check("portable-mcp-schema", config.get("$schema", "").endswith("/mcp.schema.json"), config.get("$schema"), "package inspection")
    entries = [entry for entry in marketplace.get("plugins", []) if entry.get("name") == manifest.get("name")]
    entry = entries[0] if len(entries) == 1 else {}
    source = entry.get("source", {})
    relative = source if isinstance(source, str) else source.get("path", "")
    check("local-marketplace-path-policy", relative.startswith("./") and (workspace / relative).resolve() == plugin.resolve()
          and bool(entry.get("category")) and "installation" in entry.get("policy", {}) and
          "authentication" in entry.get("policy", {}), entry, "package inspection")
    servers = config.get("mcpServers", {})
    server_name, server = next(iter(servers.items()))
    check("one-local-stdio-server", len(servers) == 1 and server.get("type") == "stdio", server, "package inspection")

    def expand(value):
        return str(value).replace("${PLUGIN_ROOT}", str(extracted))

    argv = [expand(server["command"]), *map(expand, server.get("args", []))]
    cwd = Path(expand(server.get("cwd", str(extracted))))
    if not cwd.is_absolute():
        cwd = extracted / cwd
    env = {**os.environ, **{key: expand(value) for key, value in server.get("env", {}).items()}}
    rpc = Rpc(argv, cwd, env)
    direct = {}
    try:
        init = rpc.call("initialize", {"protocolVersion": "2025-06-18", "capabilities": {"elicitation": {"form": {}}},
                                      "clientInfo": {"name": "independent-poc-evaluator", "version": "1.0.0"}})
        check("extracted-server-initialize", "result" in init, init)
        rpc.send({"jsonrpc": "2.0", "method": "notifications/initialized"})
        tools = rpc.call("tools/list", {})
        names = {tool["name"] for tool in tools.get("result", {}).get("tools", [])}
        check("tool-discovery", {"release_list", "release_choose"} <= names, sorted(names))
        for view, expected in {"all": {"R-21": "ready", "R-22": "blocked", "R-23": "ready"},
                               "ready": {"R-21": "ready", "R-23": "ready"}, "blocked": {"R-22": "blocked"}}.items():
            response = rpc.call("tools/call", {"name": "release_list", "arguments": {"view": view}})
            direct[view] = response
            check("filter-" + view, result_rows(response) == expected, response)
            check("text-fallback-" + view, bool(response.get("result", {}).get("content")), response.get("result", {}).get("content"))
        invalid = rpc.call("tools/call", {"name": "release_list", "arguments": {"view": "unexpected"}})
        check("invalid-view-refused", "error" in invalid or invalid.get("result", {}).get("isError") is True, invalid)
        for action, confirm in (("accept", True), ("accept", False), ("decline", True), ("cancel", True)):
            rpc.form_action, rpc.form_confirm = action, confirm
            response = rpc.call("tools/call", {"name": "release_choose", "arguments": {}})
            direct[f"choose-{action}-{confirm}"] = response
            if action == "accept" and confirm:
                check("accepted-form-exact-rows", result_rows(response) == {"R-22": "blocked"}, response)
            elif action == "accept" and not confirm:
                check("false-confirmation-no-default", not result_rows(response), response)
            else:
                text = encode(response).lower()
                labels = ("declin", "reject") if action == "decline" else ("cancel", "abort")
                check(f"form-{action}-{confirm}-no-default", any(label in text for label in labels) and not result_rows(response), response)
        check("form-action-distinction", direct["choose-decline-True"] != direct["choose-cancel-True"], {
            "decline": direct["choose-decline-True"], "cancel": direct["choose-cancel-True"]})
        check("native-form-requests", rpc.form_requests == 4, rpc.form_requests)
        check("zero-sampling-model-requests", rpc.model_requests == 0, rpc.model_requests)
    except Exception as error:
        check("direct-protocol-completion", False, f"{type(error).__name__}: {error}")
    finally:
        rpc.close()
        (out / "direct-events.json").write_text(encode(rpc.events) + "\n", encoding="utf-8")
        (out / "direct-stderr.txt").write_text("\n".join(rpc.errors), encoding="utf-8")
    check("protocol-only-stdout", not any("nonJson" in event["message"] for event in rpc.events), None)

    home = out / "codex-home"
    home.mkdir()
    codex_env = {**os.environ, "CODEX_HOME": str(home)}
    for key in ("OPENAI_API_KEY", "CODEX_API_KEY", "CHATGPT_ACCESS_TOKEN"):
        codex_env.pop(key, None)

    def native(arguments, timeout=45):
        result = subprocess.run([str(args.codex), *arguments], cwd=workspace, env=codex_env,
                                capture_output=True, text=True, encoding="utf-8", timeout=timeout)
        record = {"argv": [str(args.codex), *arguments], "exit": result.returncode,
                  "stdout": result.stdout, "stderr": result.stderr}
        commands.append(record)
        return result

    try:
        version = native(["--version"])
        check("native-version", version.returncode == 0, version.stdout.strip(), "installed Codex")
        added = native(["plugin", "marketplace", "add", str(workspace), "--json"])
        check("marketplace-native-add", added.returncode == 0, added.stdout + added.stderr, "installed Codex")
        listed = native(["plugin", "list", "--available", "--json"])
        check("plugin-native-discovery", listed.returncode == 0 and manifest["name"] in listed.stdout, listed.stdout + listed.stderr, "installed Codex")
        installed = native(["plugin", "add", manifest["name"] + "@" + marketplace["name"], "--json"])
        check("plugin-native-isolated-install", installed.returncode == 0, installed.stdout + installed.stderr, "installed Codex")
        # Native discovery/install are distinct from the app-server tool layer.
        app = Rpc([str(args.codex), "app-server", "--listen", "stdio://", "-c", "project_doc_max_bytes=0"], workspace, codex_env)
        try:
            initialized = app.call("initialize", {"clientInfo": {"name": "plugin_poc_evaluator", "version": "1.0.0"},
                                                    "capabilities": {"experimentalApi": True}})
            check("app-server-initialize", "result" in initialized, initialized, "installed Codex app-server")
            app.send({"method": "initialized", "params": {}})
            thread = app.call("thread/start", {"cwd": str(workspace), "ephemeral": True,
                                               "approvalPolicy": args.approval_policy, "sandbox": "read-only",
                                               "baseInstructions": "Synthetic plugin test; do not invoke a model."})
            thread_id = thread.get("result", {}).get("thread", {}).get("id")
            check("ephemeral-thread-no-turn", bool(thread_id), thread, "installed Codex app-server")
            inventory = app.call("mcpServerStatus/list", {"threadId": thread_id}, timeout=50)
            (out / "plugin-server-inventory.json").write_text(encode(inventory) + "\n", encoding="utf-8")
            candidates = inventory.get("result", {}).get("data", [])
            matching = [item for item in candidates if "release_list" in encode(item)]
            check("plugin-mcp-server-discovery", bool(matching), inventory, "installed Codex app-server")
            if matching:
                actual_server = matching[0].get("name", server_name)
                response = app.call("mcpServer/tool/call", {"threadId": thread_id, "server": actual_server,
                                                           "tool": "release_list", "arguments": {"view": "blocked"}})
                check("installed-plugin-real-tool", result_rows(response) == {"R-22": "blocked"}, response, "installed Codex app-server")
                for action, confirm in (("accept", True), ("accept", False), ("decline", True), ("cancel", True)):
                    if args.approval_policy == "never" and action != "accept":
                        continue
                    app.form_action, app.form_confirm = action, confirm
                    chosen = app.call("mcpServer/tool/call", {"threadId": thread_id, "server": actual_server,
                                                             "tool": "release_choose", "arguments": {}})
                    if args.approval_policy == "never":
                        check("installed-policy-never-no-choice-" + str(confirm), not result_rows(chosen) and app.form_requests == 0,
                              chosen, "installed Codex app-server")
                    elif action == "accept" and confirm:
                        check("installed-form-accept", result_rows(chosen) == {"R-22": "blocked"}, chosen,
                              "installed Codex app-server")
                    else:
                        check("installed-form-no-default-" + action + "-" + str(confirm), not result_rows(chosen), chosen,
                              "installed Codex app-server")
                check("installed-form-callback-count", app.form_requests == (0 if args.approval_policy == "never" else 4),
                      app.form_requests, "installed Codex app-server")
            check("no-model-turn-events", not any(event["message"].get("method", "").startswith("turn/") for event in app.events), None,
                  "installed Codex app-server")
        finally:
            app.close()
            (out / "app-server-events.json").write_text(encode(app.events) + "\n", encoding="utf-8")
            (out / "app-server-stderr.txt").write_text("\n".join(app.errors), encoding="utf-8")
    except Exception as error:
        check("native-workflow-completion", False, f"{type(error).__name__}: {error}", "installed Codex")
    report = {"capturedAt": dt.datetime.now(dt.timezone.utc).isoformat(), "workspace": str(workspace),
              "checks": checks, "passed": all(item["passed"] for item in checks), "commands": commands,
              "approvalPolicy": args.approval_policy,
              "hostPaintVerified": False, "userTestingPerformed": False,
              "scope": "Copied-plugin stdio protocol and task-local native Codex loader/app-server; no frontend paint or inference."}
    (out / "result.json").write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"passed": report["passed"], "checks": len(checks), "failed": [item["name"] for item in checks if not item["passed"]],
                      "report": str(out / "result.json")}))
    return int(not report["passed"])


if __name__ == "__main__":
    raise SystemExit(main())
