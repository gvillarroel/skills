#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Check final frozen cohorts, deterministic scripts and explicit trace summaries."""
import concurrent.futures
import importlib.util
import json
import re
import subprocess
import sys
from pathlib import Path

sys.dont_write_bytecode = True
SKILLS = {
    "polyhaven": "polyhaven-asset-search", "ambientcg": "ambientcg-material-search",
    "pexels": "pexels-media-search", "iconify": "iconify-icon-search", "kenney": "kenney-asset-search",
}
COHORTS = {
    "polyhaven": {"contract": "gallery-luna", "naturalistic": "gallery-luna", "generalization": "final-luna", "boundary": "gallery-luna"},
    "ambientcg": {"contract": "revised-luna", "naturalistic": "revised-luna", "generalization": "revised-luna", "boundary": "luna"},
    "pexels": {"contract": "luna", "naturalistic": "luna"},
    "iconify": {"contract": "luna", "naturalistic": "luna", "generalization": "luna", "boundary": "luna"},
    "kenney": {"contract": "revised-luna", "naturalistic": "revised-luna", "generalization": "final-luna", "boundary": "luna"},
}


def run_command(argv, output):
    result = subprocess.run(argv, capture_output=True, text=True, encoding="utf-8", errors="replace")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(result.stdout + result.stderr, encoding="utf-8")
    return {"command": argv, "passed": result.returncode == 0, "log": output.as_posix()}


def main():
    root = Path.cwd()
    folder = root / "projects/free-resource-skills/artifacts/reviews/release"
    spec = importlib.util.spec_from_file_location("harness", root / "scripts/run-pi-skill-eval.py")
    harness = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(harness)
    audit = json.loads((root / "evaluations/free-resource-skills/artifact-audit-20260927.json").read_text(encoding="utf-8"))
    audits = {row["run_id"]: row for row in audit["results"]}
    jobs = []
    payloads = {}
    for source, skill in SKILLS.items():
        payloads[source] = harness.snapshot_digest(harness.snapshot_tree(root / "skills" / skill))
        for test in ("test_asset_io.py", "test_" + source + ".py"):
            jobs.append((["uv", "run", "--script", f"skills/{skill}/scripts/{test}"], folder / f"{source}-{test}.log"))
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:
        deterministic = list(pool.map(lambda job: run_command(*job), jobs))
    trials = []
    trace_jobs = []
    for source, cases in COHORTS.items():
        for case, suffix in cases.items():
            for repetition in range(1, (3 if case in ("naturalistic", "generalization") else 1) + 1):
                run_id = f"free-{source}-{case}-20260927-{suffix}-{repetition}"
                row = audits[run_id]
                assert row["payload_sha256"] == payloads[source], "Different final payload: " + run_id
                trials.append({k: row[k] for k in ("run_id", "source", "case", "payload_sha256", "strict_passed", "independent_passed", "read_surface", "tool_errors")})
                argv = ["uv", "run", "--script", "scripts/summarize-pi-json-events.py", f"evaluations/runs/{run_id}/events.jsonl",
                        "--require-model", "gpt-5.6-luna", "--fail-on-invalid-json", "--fail-on-tool-error",
                        "--require-tool-call", "--require-read", "../prompt.md"]
                trace_jobs.append((argv, root / f"evaluations/runs/{run_id}/explicit-trace-summary.txt"))
    routing_id = "free-resources-routing-20260927-luna-1"
    trace_jobs.append((["uv", "run", "--script", "scripts/summarize-pi-json-events.py", f"evaluations/runs/{routing_id}/events.jsonl",
                       "--require-model", "gpt-5.6-luna", "--fail-on-invalid-json", "--fail-on-tool-error"],
                       root / f"evaluations/runs/{routing_id}/explicit-trace-summary.txt"))
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        traces = list(pool.map(lambda job: run_command(*job), trace_jobs))
    counts = []
    for source, cases in COHORTS.items():
        for case in cases:
            rows = [r for r in trials if r["source"] == source and r["case"] == case]
            count = sum(r["strict_passed"] and r["independent_passed"] for r in rows)
            counts.append({"source": source, "case": case, "passed": count, "total": len(rows)})
    routing = json.loads((root / f"evaluations/runs/{routing_id}/routing-review.json").read_text(encoding="utf-8"))
    test_count = sum(int(re.search(r"Ran (\d+) tests?", Path(r["log"]).read_text(encoding="utf-8"))[1]) for r in deterministic)
    passed = all(r["passed"] for r in deterministic + traces) and all(r["passed"] >= (2 if r["total"] == 3 else 1) for r in counts) and routing["passed"]
    report = {"passed": passed, "date": "2026-09-27", "model": "openai-codex/gpt-5.6-luna", "payloads": payloads,
              "deterministic_test_executions": test_count, "deterministic": deterministic, "cohorts": counts, "trials": trials,
              "explicit_trace_checks": traces, "routing": {"passed": routing["passed"], "correct": routing["correct"], "total": routing["total"]},
              "pexels_limit": "Missing-key handling and offline contracts only; no authenticated live search/download or browser fallback trial."}
    path = root / "evaluations/free-resource-skills/release-check-20260927.json"
    path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"passed": passed, "deterministic_test_executions": test_count, "cohorts": counts, "trace_checks": len(traces), "report": path.as_posix()}, indent=2))
    return 0 if passed else 1


if __name__ == "__main__": raise SystemExit(main())
