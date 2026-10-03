#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Run the two final isolated arrow-option/component cases with strict gates."""
from concurrent.futures import ThreadPoolExecutor
import argparse
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "projects/arrow-contrast/artifacts/pi"


def run(skill, attempt):
    run_id = "20261003-arrow-" + skill + "-final-" + str(attempt)
    outputs = ["echarts-colorsets.mjs", "option-checks.json"]
    if skill == "echarts-animated-svg":
        outputs += [name + suffix for name in
                    ("graph-cs1", "graph-cs2", "routes-cs1", "routes-cs2")
                    for suffix in (".static.svg", ".animated.svg", ".validation.json")]
    else:
        outputs += ["ArrowRoutes.vue", "integration.md"]
    prompt = "echarts-prompt.md" if skill == "echarts-animated-svg" else "slidev-echarts-prompt.md"
    command = ["uv", "run", "--script", "scripts/run-pi-skill-eval.py", skill,
               "--prompt-file", "evaluations/arrow-contrast/" + prompt,
               "--model", "openai-codex/gpt-5.6-luna", "--mode", "json", "--strict",
               "--run-id", run_id, "--expect-output-json-field", "option-checks.json::passed=true"]
    for artifact in outputs:
        command += ["--expect-output", artifact]
    result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True,
                            encoding="utf-8", errors="replace")
    (OUT / (skill + f"-{attempt}.log")).write_text(result.stdout + result.stderr, encoding="utf-8")
    return {"skill": skill, "runId": run_id, "exitCode": result.returncode,
            "command": command, "outputs": outputs,
            "result": f"evaluations/runs/{run_id}/evaluation-result.json"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--attempt", type=int, default=2)
    parser.add_argument("--workers", type=int, choices=(1, 2), default=1)
    parser.add_argument("--skills", nargs="+", choices=("echarts-animated-svg", "slidev-echarts"), default=["echarts-animated-svg", "slidev-echarts"])
    args = parser.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        results = list(pool.map(lambda skill: run(skill, args.attempt), args.skills))
    destination = ROOT / "evaluations/arrow-contrast/echarts-runtime-20261003.json"
    report = {"date": "2026-10-03", "passed": all(row["exitCode"] == 0 for row in results),
              "modelException": "Existing recorded gpt-5.6-luna exception; strict observation still required.",
              "runs": results}
    if destination.is_file():
        previous = json.loads(destination.read_text())
        untouched = [row for row in previous["runs"] if row["skill"] not in args.skills]
        report["runs"] += untouched
        report["passed"] = all(row["exitCode"] == 0 for row in report["runs"])
        history = previous.get("retainedEarlierRuns", []) + previous["runs"]
        report["retainedEarlierRuns"] = list({row["runId"]: row for row in history}.values())
    destination.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"passed": report["passed"], "runs": [{key: row[key] for key in ("skill", "runId", "exitCode")} for row in report["runs"]]}, indent=2))
    raise SystemExit(0 if report["passed"] else 1)


if __name__ == "__main__":
    main()
