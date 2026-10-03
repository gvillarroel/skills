#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Bind final standalone skill payloads to strict, exact-output runtime evidence."""
from concurrent.futures import ThreadPoolExecutor
import importlib.util
import json
import os
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[3]
SPEC = importlib.util.spec_from_file_location("pi_runner", ROOT / "scripts/run-pi-skill-eval.py")
RUNNER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(RUNNER)
OUT = ROOT / "evaluations/arrow-contrast"
ART = ROOT / "projects/arrow-contrast/artifacts"


def runtime_snapshot(source):
    snapshot = {}
    for directory, children, files in os.walk(source):
        relative = Path(directory).relative_to(source)
        children[:] = [name for name in children if name not in RUNNER.COPY_IGNORE and relative / name not in RUNNER.RUNTIME_EXCLUDED_DIRS]
        for name in files:
            path = Path(directory) / name
            if name in RUNNER.COPY_IGNORE or path.suffix.lower() in RUNNER.SNAPSHOT_IGNORED_SUFFIXES:
                continue
            snapshot[path.relative_to(source).as_posix()] = {"sizeBytes": path.stat().st_size, "sha256": RUNNER.sha256_file(path)}
    return RUNNER.snapshot_digest(snapshot), len(snapshot)


def main():
    approval_path = OUT / "accepted-arrow-runs-20261003.json"
    approvals = json.loads(approval_path.read_text())
    approved = {row["skill"]: row for row in approvals["runs"]}
    if (len(approved) != len(approvals["runs"]) or not approvals["passed"]
            or any(row.get("independentlyPassed") is not True
                   or not row.get("evidencePaths")
                   or any(not (ROOT / path).is_file() for path in row["evidencePaths"])
                   for row in approvals["runs"])):
        raise SystemExit("Independent current output approvals must be unique and complete.")
    for row in approvals["runs"]:
        if any(row.get("evidenceSha256", {}).get(path) != RUNNER.sha256_file(ROOT / path)
               for path in row["evidencePaths"]):
            raise SystemExit("Independent output approval evidence changed after sealing.")
    attempts = []
    for run in sorted((ROOT / "evaluations/runs").iterdir()):
        if not any(token in run.name for token in ("solid", "arrow")) or "20261003" not in run.name:
            continue
        if not (run / "run-manifest.json").is_file():
            continue
        manifest = json.loads((run / "run-manifest.json").read_text())
        finalized = (run / "evaluation-result.json").is_file()
        result = json.loads((run / "evaluation-result.json").read_text()) if finalized else {}
        attempts.append({"runId": run.name, "skill": manifest["skill"]["name"],
                         "passed": result.get("passed", False), "evaluationFinalized": finalized,
                         "model": manifest["pi"]["model"], "payloadSha256": manifest["skill"]["payloadSha256"],
                         "startedAtUtc": result.get("startedAtUtc", manifest["createdAtUtc"]),
                         "gates": result.get("gates", {}), "strict": manifest["eventPolicy"]["strict"],
                         "command": manifest["command"],
                         "resultPath": f"evaluations/runs/{run.name}/evaluation-result.json" if finalized else None,
                         "acceptanceBoundary": "Unfinalized attempts are retained and never eligible for acceptance." if not finalized else "Strict completed result; eligibility also requires current payload and sealed outputs."})
    inventory = json.loads((ROOT / "evaluations/colorset-audit/coverage.json").read_text())
    previous = json.loads((ROOT / "evaluations/solid-colorset-style/final-runtime-20261003.json").read_text())
    prior_digests = {run["skill"]: run["payloadSha256"] for run in previous["selectedRuns"]}
    prior_ids = {run["skill"]: run["runId"] for run in previous["selectedRuns"]}
    selected, failures = [], []
    for row in inventory["skills"]:
        if row["scope"] == "nonvisual":
            continue
        digest, count = runtime_snapshot(ROOT / "skills" / row["skill"])
        changed = digest != prior_digests.get(row["skill"])
        approved_id = approved.get(row["skill"], {}).get("runId") if changed else prior_ids.get(row["skill"])
        if changed and approved.get(row["skill"], {}).get("payloadSha256") != digest:
            failures.append({"skill": row["skill"], "error": "Independent approval does not bind the current payload"})
        matches = [run for run in attempts if run["skill"] == row["skill"] and run["runId"] == approved_id and run["passed"] and run["payloadSha256"] == digest and run["strict"] is True and all(run["gates"].get(key) is True for key in ("events", "artifacts", "skillIntegrity"))]
        if not matches:
            failures.append({"skill": row["skill"], "currentPayloadSha256": digest, "error": "No strict exact-output run matches the final payload"})
            continue
        run = dict(max(matches, key=lambda item: item["startedAtUtc"]), runtimeFileCount=count, currentRuntimeMatches=True)
        run["payloadChangedSinceSolidRevision"] = digest != prior_digests.get(row["skill"])
        run["independentOutputApproval"] = approved[row["skill"]] if changed else {"runId": approved_id, "evidence": "Matching accepted solid-style revision, unchanged payload."}
        run["validationCohort"] = "fresh-arrow" if "arrow" in run["runId"] else "unchanged-solid-revision"
        if run["payloadChangedSinceSolidRevision"] and run["validationCohort"] != "fresh-arrow":
            failures.append({"skill": row["skill"], "runId": run["runId"],
                             "error": "Changed runtime lacks a fresh arrow revision trial"})
        run["outputs"] = json.loads((ROOT / f"evaluations/runs/{run['runId']}/artifact-check.json").read_text())["outputs"]
        workspace = ROOT / "evaluations/runs" / run["runId"] / "workspace"
        for output in run["outputs"]:
            artifact = (workspace / output["path"]).resolve()
            if (not artifact.is_relative_to(workspace.resolve()) or not artifact.is_file()
                    or artifact.stat().st_size != output["sizeBytes"]
                    or RUNNER.sha256_file(artifact) != output["sha256"]):
                failures.append({"runId": run["runId"], "artifact": output["path"],
                                 "error": "Accepted artifact no longer matches sealed bytes"})
        run["artifactBytesRechecked"] = True
        selected.append(run)

    def summarize(row):
        model = row["model"].split("/")[-1]
        command = ["uv", "run", "--script", "scripts/summarize-pi-json-events.py", f"evaluations/runs/{row['runId']}/events.jsonl", "--require-model", model, "--fail-on-invalid-json", "--fail-on-tool-error"]
        result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace")
        path = ART / "reviews" / (row["runId"] + "-trace.json")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(result.stdout + result.stderr, encoding="utf-8")
        return {"runId": row["runId"], "exitCode": result.returncode, "command": command, "log": path.relative_to(ROOT).as_posix()}

    with ThreadPoolExecutor(max_workers=3) as pool:
        summaries = list(pool.map(summarize, selected))
    failures.extend(item for item in summaries if item["exitCode"])
    changed_count = sum(row["payloadChangedSinceSolidRevision"] for row in selected)
    if changed_count != len(approved):
        failures.append({"error": "Independent approval count does not match current changed payload count", "changedCount": changed_count, "approvalCount": len(approved)})
    report = {"date": "2026-10-03", "passed": not failures and len(selected) == 30, "independentApprovalsPath": approval_path.relative_to(ROOT).as_posix(), "selectedRuns": selected, "traceSummaries": summaries, "retainedAttempts": attempts, "failures": failures, "scope": "Arrow revision: final payloads for all 30 authored-output bundles. Behavior-changed bundles require both independently accepted outputs and fresh strict arrow trials. Unchanged bundles retain the exact prior accepted solid-style run. Failed, superseded, independently rejected and unfinalized attempts remain retained and never selected merely because one strict gate passed. Earlier broader release cohorts and source fidelity boundaries remain unchanged."}
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "final-runtime-20261003.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"passed": report["passed"], "matchingRuntimes": len(selected), "retainedAttempts": len(attempts), "failures": failures}, indent=2))
    raise SystemExit(0 if report["passed"] else 1)


if __name__ == "__main__":
    main()
