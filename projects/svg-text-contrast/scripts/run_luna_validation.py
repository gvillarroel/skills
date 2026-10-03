#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Run the fixed text-pair validation cohort with the user-requested Luna model."""

from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[3]
ARTIFACTS = ROOT / "projects/svg-text-contrast/artifacts"
CASES = [
    ("contract", "compose-svg-text-pair-contract.md", "pairs", ["brief.json", "preflight.json", "plan.json", "atlas.svg", "static.json", "browser.json", "overview.png"]),
    ("boundary", "compose-svg-text-pair-boundary.md", "boundary", ["brief.json", "preflight.json", "result.md"]),
    *[(f"dark-{index}", "compose-svg-text-pair-dark.md", "dark", ["brief.json", "plan.json", "dashboard.svg", "static.json", "browser.json", "overview.png", "color-editing.md"]) for index in range(1, 4)],
]


def run(case):
    name, prompt, folder, files = case
    run_id = f"20260904-svg-text-pair-luna-{name}"
    command = ["uv", "run", "--script", "scripts/run-pi-skill-eval.py", "compose-synchronized-svg",
               "--prompt-file", f"evaluations/pi-prompts/{prompt}", "--model", "openai-codex/gpt-5.6-luna",
               "--thinking", "high", "--mode", "json", "--strict", "--run-id", run_id]
    for file in files:
        command += ["--expect-output", f"outputs/{folder}/{file}"]
    assertions = {"preflight.json::ok": "false"} if name == "boundary" else {
        "static.json::ok": "true", "browser.json::ok": "true", "browser.json::metrics.textContrastIssueCount": "0"}
    if name == "contract":
        assertions["preflight.json::ok"] = "true"
    for field, expected in assertions.items():
        command += ["--expect-output-json-field", f"outputs/{folder}/{field}={expected}"]
    with (ARTIFACTS / f"{run_id}.log").open("w", encoding="utf-8") as log:
        result = subprocess.run(command, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT, check=False)
    record = {"runId": run_id, "case": name, "command": command, "exitCode": result.returncode}
    print(json.dumps(record), flush=True)
    return record


if __name__ == "__main__":
    ARTIFACTS.mkdir(parents=True, exist_ok=True)
    with ThreadPoolExecutor(max_workers=3) as executor:
        results = list(executor.map(run, CASES))
    (ARTIFACTS / "luna-cohort.json").write_text(json.dumps(results, indent=2), encoding="utf-8")
    raise SystemExit(1 if any(item["exitCode"] for item in results) else 0)
