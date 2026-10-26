#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Verify a generated console's isolated native Pi registration and factory plan."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import platform
import queue
import shutil
import subprocess
import threading
import time

ROOT = Path(__file__).resolve().parents[3]
AREA = ROOT / "projects/pi-extension-install"


def digest(path):
    path = Path(path)
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def tree(root):
    skip = {"node_modules", ".cache", "__pycache__", "dist"}
    return {p.relative_to(root).as_posix(): digest(p) for p in root.rglob("*")
            if p.is_file() and not skip.intersection(p.relative_to(root).parts)}


def execute(argv, cwd, env, target, timeout=300):
    started = time.monotonic()
    result = subprocess.run([str(item) for item in argv], cwd=cwd, env=env,
                            capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=timeout)
    receipt = {"argv": [str(item) for item in argv], "cwd": str(cwd), "exitCode": result.returncode,
               "durationSeconds": round(time.monotonic() - started, 3),
               "stdout": result.stdout, "stderr": result.stderr}
    write(target, receipt)
    if result.returncode:
        raise RuntimeError(f"Command failed; inspect {target.name}.")
    return receipt


def rpc(cli, cwd, env, output):
    argv = [shutil.which("node"), str(cli), "--offline", "--mode", "rpc", "--no-session",
            "--no-approve", "--no-context-files", "--no-mcp", "--no-skills", "--no-prompt-templates",
            "--no-themes", "--no-builtin-tools"]
    process = subprocess.Popen(argv, cwd=cwd, env=env, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE, text=True, encoding="utf-8", errors="replace", bufsize=1)
    messages, errors, events = queue.Queue(), [], []

    def read_stdout():
        for line in process.stdout:
            messages.put(line)
        messages.put(None)

    def read_stderr():
        errors.extend(process.stderr.readlines())

    threading.Thread(target=read_stdout, daemon=True).start()
    threading.Thread(target=read_stderr, daemon=True).start()

    def request(identifier, value, notification=None):
        process.stdin.write(json.dumps({"id": identifier, **value}) + "\n")
        process.stdin.flush()
        deadline, response, notifications = time.monotonic() + 45, None, []
        while time.monotonic() < deadline:
            try:
                line = messages.get(timeout=1)
            except queue.Empty:
                continue
            if line is None:
                raise RuntimeError("Native RPC exited before the request settled.")
            event = json.loads(line)
            events.append(event)
            if event.get("type") == "response" and event.get("id") == identifier:
                response = event
            if event.get("type") == "extension_ui_request" and event.get("method") == "notify":
                notifications.append(event.get("message", ""))
            if response is not None and (notification is None or any(notification in text for text in notifications)):
                if not response.get("success"):
                    raise RuntimeError("Native RPC rejected the request.")
                return response, notifications
        raise RuntimeError("Native RPC request timed out.")

    try:
        command_response, _ = request("commands", {"type": "get_commands"})
        commands = command_response.get("data", {}).get("commands", [])
        names = [item.get("name") for item in commands]
        if names.count("durable") != 1 or names.count("durable-chat") != 1:
            raise RuntimeError("The registered console commands are missing or duplicated.")
        _, help_notifications = request("help", {"type": "prompt", "message": "/durable help"}, "/durable new")
        _, list_notifications = request("list", {"type": "prompt", "message": "/durable list"}, "Pi Durable agents")
        if any(event.get("type") in {"agent_start", "turn_start"} for event in events):
            raise RuntimeError("A command unexpectedly started outer model work.")
        result = {"registeredDiscovery": True, "explicitExtensionFlag": False, "projectFilesApproved": False,
                  "commands": names, "helpNotifications": help_notifications, "listNotifications": list_notifications,
                  "modelStartEvents": 0, "events": events}
    finally:
        process.stdin.close()
        try:
            process.wait(timeout=3)
        except subprocess.TimeoutExpired:
            process.terminate()
            process.wait(timeout=10)
        write(output, {"argv": argv, "pid": process.pid, "closed": process.poll() is not None,
                       "exitCode": process.returncode, "stderr": "".join(errors),
                       "events": events, "result": locals().get("result")})
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pi-cli", type=Path, required=True)
    parser.add_argument("--npm-cli", type=Path, required=True)
    parser.add_argument("--run-id", default="native-install-20261026-01")
    args = parser.parse_args()
    run = (AREA / "artifacts" / args.run_id).resolve()
    if not run.is_relative_to((AREA / "artifacts").resolve()) or run.exists():
        raise ValueError("Choose an unused private run ID inside this project's artifacts.")
    run.mkdir(parents=True)
    workspace, console, agent_dir = run / "workspace with spaces", run / "console with spaces", run / "isolated pi"
    workspace.mkdir()
    canonical = ROOT / "skills/pi-durable"
    before = tree(canonical)
    global_settings = Path.home() / ".pi/agent/settings.json"
    global_before = digest(global_settings)
    write(run / "source-before.json", {"canonical": before, "globalSettingsSha256": global_before})
    names = {"PATH", "PATHEXT", "SYSTEMROOT", "WINDIR", "COMSPEC", "TEMP", "TMP", "HOME", "USERPROFILE",
             "APPDATA", "LOCALAPPDATA", "PROGRAMFILES", "PROGRAMFILES(X86)", "LANG", "LC_ALL"}
    env = {key: value for key, value in os.environ.items() if key.upper() in names}
    env.update(PI_CODING_AGENT_DIR=str(agent_dir), PI_DURABLE_CONNECTIONS=str(console / "durable-agents.json"),
               PI_OFFLINE="1", NPM_CONFIG_CACHE=str(run / "npm-cache"), PYTHONDONTWRITEBYTECODE="1")
    node = shutil.which("node")
    execute(["uv", "run", "--script", canonical / "scripts/scaffold-pi-extension.py", console], workspace, env, run / "scaffold.json")
    execute([node, args.npm_cli, "ci", "--ignore-scripts", "--no-audit", "--no-fund"], console, env, run / "npm-ci.json")
    entry = console / "extension.ts"
    execute([node, args.pi_cli, "install", entry], workspace, env, run / "install.json")
    installed = execute([node, args.pi_cli, "list"], workspace, env, run / "installed-list.json")
    if str(entry) not in installed["stdout"]:
        raise RuntimeError("Pi list did not show the isolated registered entry.")
    try:
        native = rpc(args.pi_cli, workspace, env, run / "native-rpc.json")
        prepare_file = run / "prepare-only.mts"
        prepare_file.write_text('''import {pathToFileURL} from 'node:url';
import {existsSync} from 'node:fs';
const [consoleDir,baseDir,npmCliPath,piCliPath]=process.argv.slice(2);
const {prepareAgentCreation}=await import(pathToFileURL(consoleDir+'/src/agent-creation.ts').href);
const plan=await prepareAgentCreation({id:'install-proof',name:'Install proof',baseDir,
 instructions:'Inspect only this fixture when explicitly asked.',task:'coding',
 model:'openai-codex/gpt-6.1-sol',thinkingLevel:'medium'},
 {cwd:baseDir,extensionDir:consoleDir,connectionsFile:consoleDir+'/durable-agents.json',npmCliPath,piCliPath});
if(existsSync(plan.projectDir)||existsSync(baseDir+'/.pi'))throw new Error('Preparation wrote an agent project.');
console.log(JSON.stringify({prepared:plan,projectCreated:false,serviceStarted:false,modelCalls:0}));
''', encoding="utf-8")
        prepared = execute([node, "--import", "tsx", prepare_file, console, workspace, args.npm_cli, args.pi_cli],
                           console, env, run / "factory-prepare.json")
        prepare = json.loads(prepared["stdout"])
    finally:
        execute([node, args.pi_cli, "remove", entry], workspace, env, run / "remove.json")
        removed = execute([node, args.pi_cli, "list"], workspace, env, run / "removed-list.json")
    if str(entry) in removed["stdout"]:
        raise RuntimeError("The isolated registration was not removed.")
    if tree(canonical) != before:
        raise RuntimeError("Canonical source changed during verification.")
    settings = json.loads((agent_dir / "settings.json").read_text(encoding="utf-8"))
    result = {"version": 1, "atUtc": datetime.now(timezone.utc).isoformat(), "passed": True,
              "sourceUnchanged": True, "realUserSettingsHashMatched": digest(global_settings) == global_before,
              "realUserSettingsAttribution": "Observation only; concurrent tasks may change actual settings. All installer invocations use the isolated agent directory.",
              "registeredDiscovery": native["registeredDiscovery"],
              "commandsUnique": True, "emptyRegistry": True, "modelCalls": 0, "serviceStarted": False,
              "factoryPlanOnly": prepare, "isolatedRegistrationRemoved": not settings.get("packages"),
              "platform": platform.system(), "limitations": "Only this recorded native platform and RPC dispatch are checked; no TUI rendering, agent creation execution, model call, login registration or existing service operation."}
    write(run / "summary.json", result)
    print(json.dumps({key: result[key] for key in ("passed", "sourceUnchanged", "realUserSettingsHashMatched",
          "registeredDiscovery", "modelCalls", "serviceStarted", "isolatedRegistrationRemoved")}))


if __name__ == "__main__":
    main()
