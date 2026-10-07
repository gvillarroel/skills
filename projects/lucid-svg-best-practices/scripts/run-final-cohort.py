#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Run the frozen skill-only cohort and independent checks in fresh workspaces."""

from concurrent.futures import ThreadPoolExecutor, as_completed
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[3]
OUTPUTS = {
    "contract": ["input/graph.json", "out/diagram.lucid", "out/document.json", "out/native-report.json", "out/status.md"],
    "naturalistic": ["input/source.svg", "out/inspection.json", "out/mapping.json", "out/graph.json", "out/diagram.lucid", "out/document.json", "out/native-report.json", "out/changes.md"],
    "generalization": ["input/layout.json", "out/diagram.lucid", "out/document.json", "out/layout-report.json", "out/changes.md"],
    "boundary": ["input/ambiguous.svg", "result/inspection.json", "result/status.md"],
}


def command(args: list[str]) -> dict:
    result = subprocess.run(args, cwd=ROOT, capture_output=True, text=True, encoding="utf-8")
    return {"exit_code": result.returncode, "stdout": result.stdout, "stderr": result.stderr}


def evaluate(case: str, repetition: int) -> dict:
    run_id = f"20261007-lucid-svg-best-final-{case}-luna-{repetition}"
    prompt = f"lucidchart-svg-best-practices-{case}" if case != "boundary" else "lucidchart-svg-boundary"
    args = ["uv", "run", "--script", "scripts/run-pi-skill-eval.py", "lucidchart-svg", "--prompt-file", f"evaluations/pi-prompts/{prompt}.md",
            "--model", "openai-codex/gpt-5.6-luna", "--thinking", "high", "--mode", "json", "--strict", "--run-id", run_id]
    for path in OUTPUTS[case]:
        args += ["--expect-output", path]
    if case == "contract":
        args.append("--require-exact-command-from-prompt")
    run_dir = Path("evaluations/runs") / run_id
    result = {"case": case, "run_id": run_id, "harness": command(args)}
    oracle = "validate_artifacts.py" if case == "boundary" else "validate_best_practices.py"
    result["independent"] = command(["uv", "run", "--script", f"evaluations/lucidchart-svg/{oracle}", case, str(run_dir / "workspace"), "--report", str(run_dir / "independent-artifacts.json")])
    result["read_surface"] = command(["uv", "run", "--script", "scripts/summarize-pi-json-events.py", str(run_dir / "events.jsonl"), "--require-model", "gpt-5.6-luna", "--fail-on-invalid-json", "--fail-on-tool-error", "--output", str(run_dir / "read-surface.json")])
    result["gates_passed"] = all(result[key]["exit_code"] == 0 for key in ("harness", "independent", "read_surface"))
    manifest = ROOT / run_dir / "run-manifest.json"
    if manifest.is_file():
        result["payload"] = json.loads(manifest.read_text(encoding="utf-8"))["skill"]
    print(json.dumps({key: result[key] for key in ("case", "run_id", "gates_passed", "payload") if key in result}), flush=True)
    return result


def main() -> None:
    cases = [("contract", 1), ("boundary", 1)] + [(case, index) for index in range(1, 4) for case in ("naturalistic", "generalization")]
    completed = []
    destination = ROOT / "projects/lucid-svg-best-practices/artifacts/reviews/final-cohort.json"
    destination.parent.mkdir(parents=True, exist_ok=True)
    with ThreadPoolExecutor(max_workers=4) as pool:
        jobs = [pool.submit(evaluate, *case) for case in cases]
        for job in as_completed(jobs):
            completed.append(job.result())
            destination.write_text(json.dumps(completed, indent=2) + "\n", encoding="utf-8")
    if not all(item["gates_passed"] for item in completed):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
