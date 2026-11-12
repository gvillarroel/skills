#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Check an authored deterministic Pi command through real RPC and JSON print."""
import argparse
import json
import os
from pathlib import Path
import queue
import subprocess
import sys
import threading
import time


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--extension", type=Path, required=True)
    parser.add_argument("--command", required=True)
    parser.add_argument("--steps", type=Path, required=True)
    parser.add_argument("--print-args", required=True)
    parser.add_argument("--expect-print", action="append", default=[])
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    if not args.command.replace("-", "").isalnum():
        parser.error("Use one registered command name without slash or whitespace.")
    extension, report = args.extension.resolve(), args.report.resolve()
    report.parent.mkdir(parents=True, exist_ok=True)
    steps = json.loads(args.steps.read_text(encoding="utf-8-sig"))
    if not isinstance(steps, list) or not 1 <= len(steps) <= 20:
        parser.error("Provide one to twenty command steps.")
    probe = subprocess.run([sys.executable, str(Path(__file__).with_name("probe_runtime.py")), "--host", "pi"], capture_output=True, text=True, encoding="utf-8", check=True)
    runtime = next(c for c in json.loads(probe.stdout)["checks"] if c["name"] == "pi")
    prefix = runtime["command"][:-1]
    flags = ["--offline", "--no-session", "--no-context-files", "--no-extensions", "--no-skills", "--no-prompt-templates", "--no-themes", "--no-mcp", "--no-tools", "--no-approve", "-e", str(extension)]
    env = {**os.environ, "PI_CODING_AGENT_DIR": str(report.parent / (report.stem + "-state"))}
    child = subprocess.Popen([*prefix, "--mode", "rpc", *flags], cwd=report.parent, env=env, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8")
    incoming, events, checks = queue.Queue(), [], []
    raw, failures = [], []

    def consume():
        for line in child.stdout:
            raw.append(line)
            try:
                incoming.put(json.loads(line))
            except ValueError:
                incoming.put({"invalidJson": True})

    threading.Thread(target=consume, daemon=True).start()

    def check(name, passed):
        checks.append({"name": name, "passed": bool(passed)})
        if not passed:
            raise ValueError(name)

    def send(value):
        child.stdin.write(json.dumps(value) + "\n")
        child.stdin.flush()

    def wait(predicate):
        deadline = time.monotonic() + 20
        while time.monotonic() < deadline:
            event = incoming.get(timeout=max(.01, deadline - time.monotonic()))
            events.append(event)
            if event.get("invalidJson") or event.get("type") in {"agent_start", "turn_start"}:
                child.kill()
                raise ValueError("Invalid RPC output or unexpected model work.")
            if predicate(event):
                return event
        raise TimeoutError("No matching RPC response.")

    try:
        send({"id": "discovery", "type": "get_commands"})
        discovered = wait(lambda e: e.get("type") == "response" and e.get("id") == "discovery")
        check("Command is registered", any(c["name"] == args.command for c in discovered.get("data", {}).get("commands", [])))
        for index, step in enumerate(steps):
            start = len(events)
            identifier = f"step-{index}"
            send({"id": identifier, "type": "prompt", "message": "/" + args.command + (" " + step["args"] if step.get("args") else "")})
            for answer_index, answer in enumerate(step.get("answers", [])):
                request = wait(lambda e: e.get("type") == "extension_ui_request" and e.get("method") == "select")
                if answer_index == 0 and step.get("expectTitle"):
                    check(f"Step {index}: retained selector state", step["expectTitle"] in request.get("title", ""))
                if answer is None:
                    send({"type": "extension_ui_response", "id": request["id"], "cancelled": True})
                else:
                    check(f"Step {index}: offered choice", answer in request.get("options", []))
                    send({"type": "extension_ui_response", "id": request["id"], "value": answer})
            response = wait(lambda e: e.get("type") == "response" and e.get("id") == identifier)
            check(f"Step {index}: handled without inference", response.get("success") and response.get("data", {}).get("disposition") == "handled")
            notices = [e.get("message", "") for e in events[start:] if e.get("method") == "notify"]
            for expected in step.get("expect", []):
                check(f"Step {index}: exact output {expected}", any(expected in text for text in notices))
            if step.get("expectNoNotify"):
                check(f"Step {index}: cancellation has no success notification", not notices)
        printed = subprocess.run([*prefix, "--mode", "json", "--print", *flags, "/" + args.command + (" " + args.print_args if args.print_args else "")], cwd=report.parent, env=env, capture_output=True, text=True, encoding="utf-8", timeout=30)
        print_events = [json.loads(line) for line in printed.stdout.splitlines() if line.strip()]
        check("JSON print exits cleanly without inference", printed.returncode == 0 and not any(e.get("type") in {"agent_start", "turn_start"} for e in print_events))
        content = [str(e.get("message", {}).get("content", "")) for e in print_events]
        for expected in args.expect_print:
            check("JSON print exact output " + expected, any(expected in value for value in content))
    except (ValueError, TimeoutError, queue.Empty, subprocess.SubprocessError) as error:
        failures.append(str(error))
    finally:
        child.terminate()
        try:
            child.wait(timeout=5)
        except subprocess.TimeoutExpired:
            child.kill()
            child.wait()
        events_path = report.with_suffix(".events.jsonl")
        events_path.write_text("".join(raw), encoding="utf-8")
        result = {"passed": not failures and all(c["passed"] for c in checks), "version": runtime["version"], "checks": checks, "failures": failures, "scope": "Real Pi RPC dialogs/commands and JSON-print output. No TUI or RPC-client paint claim. Offline is not a general inference barrier; only test authored deterministic commands."}
        report.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(result))
    return int(not result["passed"])


if __name__ == "__main__":
    raise SystemExit(main())
