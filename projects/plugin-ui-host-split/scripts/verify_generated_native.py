#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Independently exercise completed native Claude and Pi generated artifacts."""
from pathlib import Path
import importlib.util
import json
import os
import shutil
import subprocess


ROOT = Path(__file__).resolve().parents[3]


def main():
    spec = importlib.util.spec_from_file_location("pi_runtime_probe", ROOT / "skills/pi-extension-ui/scripts/probe_runtime.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    prefix = module.resolve_pi(module.find_node())["command"]
    rows = []
    for skill in ["code-native-plugin-ui", "pi-extension-ui"]:
        for suffix in ["sol-recovery", "repeat-2", "repeat-3"]:
            run_id = f"20261111-host-split-{skill}-naturalistic-{suffix}"
            run = ROOT / "evaluations/runs" / run_id
            if not (run / "evaluation-result.json").is_file():
                continue
            workspace = run / "workspace"
            output = ROOT / "projects/plugin-ui-host-split/artifacts/reviews" / run_id
            output.mkdir(parents=True, exist_ok=True)
            env = {**os.environ, "TEMP": str(output), "TMP": str(output),
                   "CLAUDE_CONFIG_DIR": str(output / "claude-state"),
                   "PI_CODING_AGENT_DIR": str(output / "pi-state")}
            if skill == "code-native-plugin-ui":
                package = workspace / "deliverables/deployment-view"
                commands = [[shutil.which("claude"), "plugin", "validate", str(package), "--strict", "--json"],
                            [shutil.which("claude"), "plugin", "test", str(package)]]
                checks = []
                for index, argv in enumerate(commands):
                    result = subprocess.run(argv, cwd=workspace, env=env, capture_output=True, text=True, encoding="utf-8", timeout=60)
                    (output / f"native-{index}.log").write_text(result.stdout + result.stderr, encoding="utf-8")
                    checks.append({"command": argv, "passed": result.returncode == 0, "exit_code": result.returncode})
                row = {"run_id": run_id, "passed": all(check["passed"] for check in checks), "checks": checks,
                       "scope": "Independent real native validation and engine; visible paint untested."}
            else:
                extension = workspace / "deliverables/report-format.ts"
                argv = [*prefix, "--offline", "--mode", "json", "--print", "--no-session", "--no-context-files", "--no-extensions",
                        "--no-skills", "--no-prompt-templates", "--no-themes", "--no-mcp", "--no-tools", "--no-approve",
                        "-e", str(extension), "/report-format detailed"]
                result = subprocess.run(argv, cwd=workspace, env=env, capture_output=True, text=True, encoding="utf-8", timeout=40)
                (output / "pi-print.jsonl").write_text(result.stdout, encoding="utf-8")
                (output / "pi-stderr.txt").write_text(result.stderr, encoding="utf-8")
                try:
                    events = [json.loads(line) for line in result.stdout.splitlines() if line.strip()]
                    custom = [event["message"] for event in events if isinstance(event.get("message"), dict) and event["message"].get("customType")]
                    text_ok = any("detailed" in json.dumps(message.get("content")) for message in custom)
                    inference = sum(event.get("type") in {"agent_start", "turn_start"} for event in events)
                    passed = result.returncode == 0 and text_ok and inference == 0
                except ValueError:
                    text_ok, inference, passed = False, None, False
                row = {"run_id": run_id, "passed": passed, "command": argv,
                       "custom_result": text_ok, "model_turn_events": inference,
                       "scope": "Independent real JSON-print argument route; RPC artifact tests reviewed separately; TUI paint untested."}
            (output / "independent.json").write_text(json.dumps(row, indent=2), encoding="utf-8")
            rows.append(row)
    target = ROOT / "projects/plugin-ui-host-split/artifacts/manifests/independent-native.json"
    target.write_text(json.dumps(rows, indent=2), encoding="utf-8")
    print(json.dumps({"passed": all(row["passed"] for row in rows), "count": len(rows),
                      "results": [{"run_id": row["run_id"], "passed": row["passed"]} for row in rows]}, indent=2))
    return int(not all(row["passed"] for row in rows))


if __name__ == "__main__":
    raise SystemExit(main())
