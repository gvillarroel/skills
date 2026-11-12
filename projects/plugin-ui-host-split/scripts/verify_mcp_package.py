#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["jsonschema>=4.26"]
# ///
"""Independently inspect a generated read-only MCP package over real stdio."""
from pathlib import Path
import argparse
import hashlib
import json
import os
import queue
import shutil
import subprocess
import threading
from urllib.request import urlopen

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[3]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("package", type=Path)
    parser.add_argument("--label", required=True)
    args = parser.parse_args()
    package = args.package.resolve()
    if not package.is_relative_to(ROOT):
        raise ValueError("The generated package must stay inside the workspace.")
    output = ROOT / "projects/plugin-ui-host-split/artifacts/reviews" / args.label
    output.mkdir(parents=True, exist_ok=True)
    checks = []
    sources = {}
    for filename, schema_name in [("plugin.json", "plugin"), ("mcp.json", "mcp")]:
        target = package / filename
        if not target.is_file():
            continue
        url = f"https://agent-plugins.org/schemas/1.0.0/{schema_name}.schema.json"
        with urlopen(url, timeout=30) as response:
            raw = response.read()
        sources[url] = hashlib.sha256(raw).hexdigest()
        (output / f"{schema_name}.schema.json").write_bytes(raw)
        errors = [error.message for error in Draft202012Validator(json.loads(raw)).iter_errors(json.loads(target.read_text()))]
        checks.append({"name": f"Official {filename} schema", "passed": not errors, "errors": errors})
    launch_cwd = package
    if (package / "mcp.json").is_file():
        declarations = json.loads((package / "mcp.json").read_text())["mcpServers"]
        local = [value for value in declarations.values() if value.get("type") == "stdio"]
        if len(local) != 1 or local[0].get("command") != "node":
            raise ValueError("This read-only evaluator expects one declared Node stdio entry.")
        declaration = local[0]
        arguments = [argument.replace("${PLUGIN_ROOT}", str(package)) for argument in declaration.get("args", [])]
        launch_cwd = Path(declaration.get("cwd", str(package)).replace("${PLUGIN_ROOT}", str(package))).resolve()
        if not launch_cwd.is_relative_to(package):
            raise ValueError("Declared working directory escapes the package.")
        command = [shutil.which("node"), *arguments]
    else:
        command = [shutil.which("node"), str(package / "server.mjs")]
    checks.append({"name": "Declared runtime command selected", "passed": True, "argv": command, "cwd": str(launch_cwd)})
    env = {**os.environ, "TEMP": str(output), "TMP": str(output)}
    child = subprocess.Popen(command, cwd=launch_cwd, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE, text=True, encoding="utf-8", env=env)
    incoming = queue.Queue()
    transcript = []

    def reader():
        for line in child.stdout:
            try:
                incoming.put(json.loads(line))
            except ValueError:
                incoming.put({"invalid_json": line})

    threading.Thread(target=reader, daemon=True).start()

    def send(value):
        transcript.append({"direction": "send", "value": value})
        child.stdin.write(json.dumps(value) + "\n")
        child.stdin.flush()

    sequence = 0

    def call(method, params=None):
        nonlocal sequence
        sequence += 1
        identifier = sequence
        send({"jsonrpc": "2.0", "id": identifier, "method": method, "params": params or {}})
        while True:
            reply = incoming.get(timeout=20)
            transcript.append({"direction": "receive", "value": reply})
            if "invalid_json" in reply:
                raise ValueError("Non-protocol data on stdout.")
            if reply.get("id") == identifier:
                if "error" in reply:
                    raise ValueError(str(reply["error"]))
                return reply["result"]

    failure = None
    values = []
    try:
        initialized = call("initialize", {"protocolVersion": "2025-06-18", "capabilities": {}, "clientInfo": {"name": "independent-host-split-review", "version": "1.0.0"}})
        checks.append({"name": "Real stdio initialization", "passed": bool(initialized.get("protocolVersion"))})
        send({"jsonrpc": "2.0", "method": "notifications/initialized"})
        tools = call("tools/list")["tools"]
        checks.append({"name": "Nonempty discovery", "passed": bool(tools), "tools": [tool["name"] for tool in tools]})
        useful = False
        uris = set()
        for tool in tools:
            uri = tool.get("_meta", {}).get("ui", {}).get("resourceUri")
            if uri:
                uris.add(uri)
            if not tool.get("inputSchema", {}).get("required"):
                result = call("tools/call", {"name": tool["name"], "arguments": {}})
                values.append({"tool": tool["name"], "result": result})
                useful |= not result.get("isError", False) and bool(result.get("structuredContent")) and any(item.get("type") == "text" and item.get("text") for item in result.get("content", []))
        checks.append({"name": "Useful text and structured result from actual tool", "passed": useful})
        checks.append({"name": "MCP App tool metadata", "passed": bool(uris), "uris": sorted(uris)})
        for index, uri in enumerate(sorted(uris)):
            content = call("resources/read", {"uri": uri})["contents"]
            html = next((item for item in content if item.get("uri") == uri and item.get("mimeType") == "text/html;profile=mcp-app" and item.get("text")), None)
            checks.append({"name": f"Actual HTML/MIME resource {uri}", "passed": bool(html)})
            if html:
                (output / f"resource-{index}.html").write_text(html["text"], encoding="utf-8")
    except Exception as error:
        failure = f"{type(error).__name__}: {error}"
    finally:
        child.terminate()
        try:
            child.wait(timeout=5)
        except subprocess.TimeoutExpired:
            child.kill()
        stderr = child.stderr.read()
    report = {"passed": failure is None and all(check["passed"] for check in checks), "checks": checks,
              "schema_sources": sources, "failure": failure, "tool_results": values,
              "scope": "Independent schema and real stdio checks only; browser interaction and signed-in host paint are separate."}
    (output / "transcript.json").write_text(json.dumps(transcript, indent=2), encoding="utf-8")
    (output / "stderr.txt").write_text(stderr, encoding="utf-8")
    (output / "review.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({key: value for key, value in report.items() if key != "tool_results"}, indent=2))
    return int(not report["passed"])


if __name__ == "__main__":
    raise SystemExit(main())
