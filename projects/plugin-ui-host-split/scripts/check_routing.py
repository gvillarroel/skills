#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Evaluate the seven skill descriptions without loading or forcing any skill."""
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess


ROOT = Path(__file__).resolve().parents[3]
MODEL = "openai-codex/gpt-6.1-sol"
CASES = [
    ("desktop-chat", "Build an interactive local inventory connector for ordinary Claude Desktop Chat.", "desktop-chat-plugin-ui"),
    ("native-code", "Create a native Claude Code Mod with a selectable pane in the terminal and Desktop Code tab.", "code-native-plugin-ui"),
    ("pi-command", "Build a Pi extension command with a native selector, cancel, and direct argument.", "pi-extension-ui"),
    ("pi-rpc", "Repair a Pi RPC extension that mistakes hasUI for support for a custom terminal component.", "pi-extension-ui"),
    ("codex", "Package a local Codex plugin and distinguish app-server tool receipt from stock desktop painting.", "codex-plugin-ui"),
    ("chatgpt-local", "Create a ChatGPT Desktop local-thread MCP App with optional host modal capability checks.", "chatgpt-desktop-plugin-ui"),
    ("enterprise", "Build a Google Cloud Gemini Enterprise A2UI status panel and prepare its A2A registration.", "gemini-enterprise-ui"),
    ("cross-host", "Compare plugin UI routes across Claude Desktop, Claude Code, Pi, Codex, ChatGPT Desktop, and Gemini Enterprise.", "desktop-plugin-ui"),
    ("react-site", "Build a standalone React marketing site for a bakery.", None),
    ("csv", "Sort a CSV file by invoice date.", None),
    ("gemini-cli", "Configure a Gemini CLI authentication error without any user interface authoring.", None),
]


def main():
    metadata = []
    for name in dict.fromkeys(row[2] for row in CASES if row[2]):
        text = (ROOT / "skills" / name / "SKILL.md").read_text(encoding="utf-8")
        metadata.append(text.split("---", 2)[1].strip())
    prompt = """Choose the single best skill for each request using only the supplied name/description metadata. Use null when none applies. Do not read skill bodies, browse, execute commands, or implement the requests. Write exactly `results/routing.json` as {"decisions":[{"id":"...","skill":"... or null","reason":"..."}]}, preserving request order. This is a metadata decision control, not a claim about automatic product discovery.

Skill metadata:
""" + "\n\n".join(metadata) + "\n\nRequests:\n" + "\n".join(f"{identifier}: {request}" for identifier, request, _ in CASES)
    run = ROOT / "evaluations/runs/20261111-host-split-routing-sol-1"
    workspace = run / "workspace"
    workspace.mkdir(parents=True, exist_ok=False)
    (run / "prompt.md").write_text(prompt, encoding="utf-8")
    spec = importlib.util.spec_from_file_location("host_split_harness", ROOT / "scripts/run-pi-skill-eval.py")
    harness = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(harness)
    argv = [*harness.pi_command_prefix(), "--model", MODEL, "--thinking", "medium", "--mode", "json",
            "--no-context-files", "--no-extensions", "--no-skills", "--no-prompt-templates", "--no-themes",
            "--no-session", "--print", "Read ../prompt.md with the read tool first, then complete that task. No skill body is loaded."]
    (run / "run-manifest.json").write_text(json.dumps({"model": MODEL, "command": argv, "no_forced_skill": "--skill" not in argv, "metadata_sha256": hashlib.sha256("\n".join(metadata).encode()).hexdigest()}, indent=2), encoding="utf-8")
    with (run / "events.jsonl").open("w", encoding="utf-8") as out, (run / "stderr.txt").open("w", encoding="utf-8") as err:
        result = subprocess.run(argv, cwd=workspace, stdout=out, stderr=err, timeout=240)
    trace = harness.event_check_report(events_path=run / "events.jsonl", prompt=prompt,
             require_prompt_read_first=True, require_exact_command_from_prompt=False,
             require_observed_model=True, requested_model=MODEL, fail_on_invalid_json=True,
             fail_on_tool_error=True, forbid_read_regex=[r"^(?!\.\./prompt\.md$).+"],
             forbid_command_regex=[r"(?s).+"])
    (run / "event-check.json").write_text(json.dumps(trace, indent=2), encoding="utf-8")
    artifact = workspace / "results/routing.json"
    decisions = json.loads(artifact.read_text(encoding="utf-8"))["decisions"] if artifact.is_file() else []
    grades = [{"id": identifier, "expected": expected, "actual": decision.get("skill"),
               "passed": decision.get("id") == identifier and decision.get("skill") == expected and bool(decision.get("reason")),
               "reason": decision.get("reason")}
              for (identifier, _, expected), decision in zip(CASES, decisions)]
    report = {"passed": result.returncode == 0 and trace["passed"] and len(decisions) == len(CASES) and all(row["passed"] for row in grades),
              "correct": sum(row["passed"] for row in grades), "total": len(CASES),
              "trace_passed": trace["passed"], "grades": grades,
              "scope": "Metadata-only decision control; no forced skill or skill body; not automatic host selection."}
    (run / "result.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    return int(not report["passed"])


if __name__ == "__main__":
    raise SystemExit(main())
