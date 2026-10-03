#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Record a frozen D3 cohort, exact outputs, trace summaries and independent browser gates."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[3]
RUNS = ROOT / "evaluations/runs"
REVIEWS = ROOT / "projects/skill-authoring-audit/artifacts/reviews"
CASES = {"contract": (1, "contract"), "natural": (3, "naturalistic"),
         "transfer": (3, "generalization"), "boundary": (1, "boundary")}


def read(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    records = []
    for slug, (count, case) in CASES.items():
        report_path = REVIEWS / f"d3-verified-{slug}-independent.json"
        reports = {r["run"]: r for r in read(report_path)["results"]}
        for n in range(1, count + 1):
            run_id = f"20261002-authoring-d3-verified-{slug}-luna-{n}"
            run = RUNS / run_id
            trace_path = run / "trace-summary.json"
            command = [sys.executable, str(ROOT / "scripts/summarize-pi-json-events.py"), str(run / "events.jsonl"),
                       "--output", str(trace_path), "--require-model", "gpt-5.6-luna", "--fail-on-invalid-json", "--fail-on-tool-error"]
            traced = subprocess.run(command, capture_output=True, text=True)
            trace = read(trace_path)
            manifest, result, integrity = (read(run / filename) for filename in ("run-manifest.json", "evaluation-result.json", "skill-integrity-check.json"))
            artifacts = []
            for relative in manifest["expectedOutputs"]:
                path = run / "workspace" / relative
                artifacts.append({"path": relative, "bytes": path.stat().st_size, "sha256": hashlib.sha256(path.read_bytes()).hexdigest()})
            independent = reports[run_id]
            # Manual judgments are entered only after opening retained HTML/SVG
            # and motion screenshots, not inferred from a mechanical pass.
            manual_path = REVIEWS / "d3-verified-manual.json"
            manual = read(manual_path)["results"][run_id]
            records.append({"runId": run_id, "case": case, "manifest": manifest,
                            "harness": result, "integrity": integrity, "artifacts": artifacts,
                            "tracePassed": traced.returncode == 0 and trace["passed"],
                            "observedModels": trace["models"], "readPaths": trace["policyReadPaths"],
                            "toolCounts": trace["toolCounts"], "toolErrors": [r for r in trace["calls"] if r["isError"]],
                            "piCommand": manifest["command"], "independentCommand": ["uv", "run", "--script", "evaluations/contracts/check-d3-decoding.py", "--run-id", run_id, "--case", case, "--report", report_path.relative_to(ROOT).as_posix()],
                            "independentChecks": independent["checks"], "screenshots": independent["screenshots"], "manualReview": manual,
                            "passed": result["passed"] and traced.returncode == 0 and independent["passed"] and manual["passed"]})
    hashes = sorted({r["manifest"]["skill"]["payloadSha256"] for r in records})
    cases = []
    for case in ("contract", "naturalistic", "generalization", "boundary"):
        selected = [r for r in records if r["case"] == case]
        required = 2 if len(selected) == 3 else 1
        passes = sum(r["passed"] for r in selected)
        cases.append({"case": case, "runs": len(selected), "jointPasses": passes, "requiredPasses": required, "passed": passes >= required})
    audit_path = ROOT / "evaluations/skill-authoring/20261002-bundles-validated.json"
    audit = read(audit_path)
    final_runtime = next(r for r in audit["results"] if r["skill"] == "d3" and r["profile"] == "runtime")
    # The copied runtime profile must be the exact candidate used by every run.
    frozen = len(hashes) == 1 and hashes[0] == final_runtime["payloadSha256"]
    evidence = {"schemaVersion": 1, "date": "2026-10-02", "skill": "d3", "model": "openai-codex/gpt-5.6-luna",
                "modelException": "The existing backlog records Spark provider unavailability; the same Luna model and strict gates were retained.",
                "passed": all(c["passed"] for c in cases) and frozen and audit["passed"], "frozenPayloadSha256": hashes,
                "candidateMatchesFinalRuntimeBundle": frozen, "runtimeFiles": records[0]["manifest"]["skill"]["fileCount"],
                "authoringBundleAudit": audit_path.relative_to(ROOT).as_posix(), "cases": cases, "records": records,
                "retainedHistory": "20261002-forward-evidence.json",
                "scope": "Focused authoring/navigation and named decoding recipe validation. Prior D3 releases remain recorded; no new Harbor study or Claude model certification is claimed."}
    output = ROOT / "evaluations/skill-authoring/20261002-d3-validation.json"
    output.write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in evidence.items() if k not in {"records", "retainedHistory", "scope"}}, indent=2))
    return 0 if evidence["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
