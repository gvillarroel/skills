#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Retain strict trace summaries and artifact contracts for completed UI cases."""
from pathlib import Path
import json
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[3]


def main():
    rows = []
    for run in sorted((ROOT / "evaluations/runs").glob("20261111-host-split-*")):
        result_path = run / "evaluation-result.json"
        if not result_path.is_file() or "spark-contract" in run.name:
            continue
        result = json.loads(result_path.read_text())
        event_path = run / "event-check.json"
        event = json.loads(event_path.read_text()) if event_path.is_file() else {
            "passed": False, "findings": [{"code": "timeout-before-event-gates" if result.get("timedOut") else "missing-event-gates"}]}
        manifest = json.loads((run / "run-manifest.json").read_text())
        summary_path = run / "trace-summary.json"
        argv = [sys.executable, str(ROOT / "scripts/summarize-pi-json-events.py"), str(run / "events.jsonl"),
                "--require-model", "gpt-6.1-sol", "--fail-on-invalid-json", "--fail-on-tool-error", "--output", str(summary_path)]
        checked = subprocess.run(argv, cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace")
        (run / "trace-summary.log").write_text(checked.stdout + checked.stderr, encoding="utf-8")
        workspace = run / "workspace"
        errors = []
        review = workspace / "deliverables/review.json"
        if review.is_file():
            try:
                data = json.loads(review.read_text(encoding="utf-8"))
                for field in ["host", "mechanism", "tests", "remaining_host_checks", "heuristics"]:
                    if field not in data or data[field] is None:
                        errors.append(f"Missing review field {field}.")
            except ValueError as error:
                errors.append(str(error))
        checks = workspace / "deliverables/checks.json"
        if checks.is_file():
            data = json.loads(checks.read_text(encoding="utf-8"))
            if not isinstance(data.get("checks"), list) or not data["checks"]:
                errors.append("Missing nonempty checks array.")
            else:
                for check in data["checks"]:
                    if not isinstance(check, dict) or not {"layer", "action", "expected", "status"}.issubset(check):
                        errors.append("Malformed check record.")
        design = workspace / "deliverables/design.json"
        if design.is_file():
            if json.loads(design.read_text(encoding="utf-8")).get("passed") is not True:
                errors.append("Bundled design command did not pass.")
        prompt_source = Path(manifest["prompt"]["source"]).relative_to(ROOT).as_posix()
        reproduction = ["uv", "run", "--script", "scripts/run-pi-skill-eval.py", manifest["skill"]["name"],
                        "--prompt-file", prompt_source, "--mode", "json", "--strict", "--model", manifest["pi"]["model"],
                        "--thinking", manifest["pi"]["thinking"], "--run-id", run.name, "--timeout-seconds", str(manifest["pi"]["timeoutSeconds"])]
        if manifest["eventPolicy"].get("requireExactCommandFromPrompt"):
            reproduction.append("--require-exact-command-from-prompt")
        for path in manifest["expectedOutputs"]:
            reproduction.extend(["--expect-output", path])
        row = {"run_id": run.name, "strict_passed": result["passed"],
               "command": reproduction, "expected_outputs": manifest["expectedOutputs"],
               "prompt_sha256": manifest["prompt"]["sha256"], "subject": manifest["skill"],
               "artifacts_present": result["gates"].get("artifacts"),
               "artifacts_present_after_timeout": all((workspace / path).is_file() and (workspace / path).stat().st_size for path in manifest.get("expectedOutputs", [])) if result.get("timedOut") else None,
               "timed_out": result.get("timedOut", False),
               "payload_unchanged": result["gates"]["skillIntegrity"],
               "trace_summary_exit": checked.returncode,
               "event_findings": event["findings"], "artifact_schema_findings": errors,
               "seconds": result["durationSeconds"],
               "model": manifest.get("pi", {}).get("model", "openai-codex/gpt-6.1-sol")}
        rows.append(row)
    path = ROOT / "projects/plugin-ui-host-split/artifacts/manifests/evaluation-review.json"
    path.write_text(json.dumps(rows, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"completed": len(rows), "strict_passed": sum(row["strict_passed"] for row in rows),
                      "artifact_schema_failures": [row["run_id"] for row in rows if row["artifact_schema_findings"]]}, indent=2))


if __name__ == "__main__":
    main()
