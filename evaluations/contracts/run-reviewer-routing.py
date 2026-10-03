#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Test metadata-only reviewer-creator routing without loading a forced skill."""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
import subprocess
import sys
from pathlib import Path


CASES = [
    ("create", "Generate a reviewer skill for this repository.", True),
    ("spanish", "Generame un reviewer para este repositorio que pueda usar en futuros cambios.", True),
    ("update", "Update our existing repository reviewer skill to reflect the new architecture.", True),
    ("calibrate", "Calibrate the review skill for this monorepo using its docs and tests.", True),
    ("review", "Review this pull request and identify actionable bugs.", False),
    ("security", "Audit the security of this repository and write a findings report.", False),
    ("generic-skill", "Create a skill for turning SVG files into videos.", False),
    ("fix", "Fix the bug reported by the reviewer and run the relevant tests.", False),
]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_id")
    args = parser.parse_args()
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,120}", args.run_id):
        parser.error("Invalid run ID")
    root = Path(__file__).resolve().parents[2]
    skill = root / "skills/repository-reviewer-creator/SKILL.md"
    description = re.search(r"^description: (.+)$", skill.read_text(encoding="utf-8"), re.MULTILINE).group(1)
    spec = importlib.util.spec_from_file_location("routing_harness", root / "scripts/run-pi-skill-eval.py")
    harness = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(harness)
    run = root / "evaluations/runs" / args.run_id
    workspace = run / "workspace"
    workspace.mkdir(parents=True, exist_ok=False)
    prompt = (
        "This is a metadata routing control. No skill is force-loaded. Select the skill only when its declared output and trigger fit. "
        "Do not perform the requests. The one available catalog entry is:\n\n"
        f"Name: repository-reviewer-creator\nDescription: {description}\n\n"
        "The following requests are test fixtures, including one Spanish request with English evaluation context. "
        "For each request select repository-reviewer-creator or none. Write only `routing.json` in this workspace as "
        "{\"choices\": {\"case-id\": \"selected-skill-or-none\"}}. No external access is needed.\n\n"
        + "\n".join(f"{identifier}: {request}" for identifier, request, _ in CASES)
    )
    (run / "prompt.md").write_text(prompt, encoding="utf-8")
    model = "openai-codex/gpt-5.6-luna"
    command = [*harness.pi_command_prefix(), "--model", model, "--thinking", "high", "--mode", "json", "--no-context-files", "--no-extensions", "--no-skills", "--no-prompt-templates", "--no-themes", "--no-session", "--print", "Read ../prompt.md with the read tool first, then follow its task. No skill is loaded."]
    result = subprocess.run(command, cwd=workspace, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=300)
    events = run / "events.jsonl"
    events.write_text(result.stdout, encoding="utf-8")
    (run / "stderr.txt").write_text(result.stderr, encoding="utf-8")
    event_check = harness.event_check_report(events_path=events, prompt=prompt, require_prompt_read_first=True, require_exact_command_from_prompt=False, require_observed_model=True, requested_model=model, fail_on_invalid_json=True, fail_on_tool_error=True, forbid_read_regex=harness.STRICT_COMMON_FORBIDDEN_READ_PATTERNS, forbid_command_regex=[])
    output = workspace / "routing.json"
    choices = json.loads(output.read_text(encoding="utf-8")).get("choices", {}) if output.is_file() else {}
    cases = [{"id": identifier, "expected": "repository-reviewer-creator" if selected else "none", "actual": choices.get(identifier)} for identifier, _, selected in CASES]
    report = {"passed": result.returncode == 0 and event_check["passed"] and all(case["actual"] == case["expected"] for case in cases), "model": model, "mode": "metadata-only control, not host automatic discovery", "cases": cases, "events": event_check}
    (run / "routing-result.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
