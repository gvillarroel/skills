#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""One bounded real Codex exec inference against the synthetic local fixture."""
import argparse
import json
import subprocess
import sys
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("--codex", type=Path, required=True)
parser.add_argument("--out", type=Path, required=True)
parser.add_argument("--model", required=True)
args = parser.parse_args()
out = args.out.resolve()
out.mkdir(parents=True, exist_ok=True)
if (out / "stdout.jsonl").exists() or (out / "mcp-events.jsonl").exists():
    parser.error("Choose a fresh output folder; existing evidence will not be overwritten.")
fixture = Path(__file__).with_name("fixture.py").resolve()
command = [str(args.codex), "exec", "--ignore-user-config", "--ephemeral", "--json", "--color", "never", "--skip-git-repo-check", "--sandbox", "read-only", "--model", args.model, "-c", 'model_reasoning_effort="low"', "-c", "project_doc_max_bytes=0", "-c", "mcp_servers.ui_probe.command=" + json.dumps(sys.executable), "-c", "mcp_servers.ui_probe.args=" + json.dumps([str(fixture), "--log", str(out / "mcp-events.jsonl")])]
prompt = "Synthetic UI boundary test. Call ui_probe.ui_card exactly once, then ui_probe.form exactly once. Use no other tools. After both calls, reply exactly UI_PROBE_DONE."
command.append(prompt)
result = subprocess.run(command, cwd=out, stdin=subprocess.DEVNULL, capture_output=True, text=True, encoding="utf-8", timeout=180)
(out / "stdout.jsonl").write_text(result.stdout, encoding="utf-8")
(out / "stderr.txt").write_text(result.stderr, encoding="utf-8")
events = []
invalid = 0
for line in result.stdout.splitlines():
    try:
        events.append(json.loads(line))
    except json.JSONDecodeError:
        invalid += 1
methods = []
if (out / "mcp-events.jsonl").exists():
    methods = [json.loads(line) for line in (out / "mcp-events.jsonl").read_text(encoding="utf-8").splitlines()]
report = {"date": "2026-10-24", "scope": "Installed Codex exec noninteractive JSON stream, synthetic MCP fixture only", "requestedModel": args.model, "modelTurnsStarted": 1, "inferenceHttpRequests": "Not counted; a tool loop may make multiple requests", "exitCode": result.returncode, "validJsonLines": len(events), "invalidJsonLines": invalid, "eventTypes": [event.get("type") for event in events], "mcpToolCalls": [event.get("params", {}).get("name") for event in methods if event.get("method") == "tools/call"], "elicitationResponses": [event for event in methods if str(event.get("id", "")).startswith("elicitation-")], "usage": [event.get("usage") for event in events if event.get("usage")], "finalMarker": "UI_PROBE_DONE" in result.stdout}
(out / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
print(json.dumps(report, indent=2))
raise SystemExit(0 if result.returncode == 0 and report["finalMarker"] else 1)
