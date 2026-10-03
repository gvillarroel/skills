#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""Make one isolated, tool-free Luna call through Pi's explicit SSE transport."""
from pathlib import Path
import argparse
import json
import os
import subprocess
import time

IMAGE = "fox-vector-agent:1.0.0"
IMAGE_ID = "sha256:f154aa38e1aad0dd0739800e9931a59e84252de6e934fe5a58b4ac181919110a"
CONTAINER_PROGRAM = r'''
from pathlib import Path
import json, os, subprocess, sys
request = json.load(sys.stdin)
root = Path('/root/.pi/agent')
root.mkdir(parents=True, exist_ok=True)
settings = {'transport':'sse','retry':{'enabled':False},'compaction':{'enabled':False},'enableSkillCommands':False}
models = {'providers':{'openai-codex':{'api':'openai-codex-responses','models':[{'id':'gpt-6-luna','name':'GPT-6 Luna','reasoning':True,'input':['text','image'],'contextWindow':1050000,'maxTokens':16384}]}}}
for filename, content in [('auth.json',request['auth']),('settings.json',settings),('models.json',models)]:
    path=root/filename
    path.write_text(json.dumps(content))
    path.chmod(0o600)
args=['pi','--print','--mode','json','--no-session','--offline','--no-extensions','--no-skills','--no-context-files','--no-prompt-templates','--no-themes','--no-tools','--provider','openai-codex','--model','gpt-6-luna','--thinking','medium',request['prompt']]
result=subprocess.run(args,cwd='/app',env={**os.environ,'PI_OFFLINE':'1','PI_TELEMETRY':'0'},capture_output=True,text=True,timeout=210)
sys.stdout.write(result.stdout)
sys.stderr.write(result.stderr)
sys.exit(result.returncode)
'''


def call_luna(prompt, evidence_dir):
    evidence_dir = Path(evidence_dir)
    evidence_dir.mkdir(parents=True, exist_ok=False)
    identity = json.loads(subprocess.check_output(["docker", "image", "inspect", IMAGE]))[0]["Id"]
    if identity != IMAGE_ID:
        raise ValueError("Frozen Pi image changed")
    credentials = json.loads(Path(os.environ["FOX_PI_AUTH"]).read_text(encoding="utf-8-sig"))
    request = {"auth": {"openai-codex": credentials["openai-codex"]}, "prompt": prompt}
    started = time.monotonic()
    result = subprocess.run(
        ["docker", "run", "--rm", "-i", "--network", "bridge", IMAGE, "python3", "-c", CONTAINER_PROGRAM],
        input=json.dumps(request), capture_output=True, text=True, timeout=240,
    )
    (evidence_dir / "events.jsonl").write_text(result.stdout, encoding="utf-8")
    (evidence_dir / "stderr.txt").write_text(result.stderr, encoding="utf-8")
    messages = []
    for line in result.stdout.splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if event.get("type") == "tool_execution_start":
            raise ValueError("Tool-free reflection unexpectedly invoked a tool")
        if event.get("type") == "message_end" and event.get("message", {}).get("role") == "assistant":
            messages.append(event["message"])
    valid = bool(messages) and all(m.get("model") == "gpt-6-luna" for m in messages)
    terminal = messages[-1] if messages else {}
    valid = valid and terminal.get("stopReason") not in {"error", "aborted"} and result.returncode == 0
    text = "\n".join(part["text"] for part in terminal.get("content", []) if part.get("type") == "text")
    receipt = {
        "model": "openai-codex/gpt-6-luna", "pi": "0.84.2", "transport": "sse", "tools": [],
        "passed": valid and bool(text.strip()), "exit_code": result.returncode,
        "error": terminal.get("errorMessage"), "usage": terminal.get("usage"),
        "elapsed_seconds": time.monotonic() - started, "image_id": identity,
    }
    (evidence_dir / "receipt.json").write_text(json.dumps(receipt, indent=2), encoding="utf-8")
    if not receipt["passed"]:
        raise RuntimeError("Luna SSE call failed: " + str(receipt["error"] or result.stderr[-500:]))
    (evidence_dir / "response.txt").write_text(text, encoding="utf-8")
    return text, receipt


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    response, receipt = call_luna("Reply with exactly READY. This is a connection check; no task or tools are provided.", args.output)
    receipt["exact_probe_response"] = response.strip() == "READY"
    print(json.dumps(receipt))
