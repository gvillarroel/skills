#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Archive compact benchmark evidence without changing trials or original verdicts.

Run: uv run --script archive_results.py --cohort COHORT --regrade REGRADE
     --performance PERFORMANCE --output RESULTS
The original runner and manual gates are retained; R1 changes only the SVG oracle.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
import run_benchmark as runner

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
COMPONENTS = ("passed", "read_surface_passed", "commands_passed",
              "artifact_review_passed", "narrative_review_passed")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def relative(path: Path) -> str:
    return path.resolve().relative_to(ROOT).as_posix()


def evidence(path: Path) -> dict:
    return {"path": relative(path), "sha256": sha(path), "bytes": path.stat().st_size}


def workspace_digest(workspace: Path) -> tuple[str, int]:
    files = {path.relative_to(workspace).as_posix():
             {"bytes": path.stat().st_size, "sha256": sha(path)}
             for path in sorted(workspace.rglob("*")) if path.is_file()}
    digest = hashlib.sha256(json.dumps(files, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()
    return digest, len(files)


def archive(cohort_path: Path, regrade_path: Path, performance_path: Path,
            output: Path) -> dict:
    require(output.resolve().parent == HERE and not output.exists(),
            "Archive output must be a fresh path in this benchmark directory")
    manifest_path = HERE / "manifest.json"
    manifest, cohort, regrade, performance = map(load, (
        manifest_path, cohort_path, regrade_path, performance_path))
    runner.verify(manifest)
    require(regrade["parent_manifest_sha256"] == sha(manifest_path), "R1 parent differs")
    require(regrade["original_cohort_sha256"] == sha(cohort_path), "R1 cohort differs")
    require(regrade["resampling"] is False and regrade["manual_review_gates_unchanged"] is True,
            "R1 altered sampling or manual gates")
    revision_manifest = HERE / "verifier-revisions" / "r1" / "correction-manifest.json"
    require(sha(revision_manifest) == regrade["revision_manifest_sha256"], "R1 identity differs")
    require(cohort["completed_trials"] == cohort["planned_trials"] == manifest["required_trials"],
            "Cohort is incomplete")
    expected_inventory = {(case, repetition) for case, spec in manifest["cases"].items()
                          for repetition in range(1, spec["repetitions"] + 1)}
    actual_inventory = [(record["case"], record["repetition"]) for record in cohort["results"]]
    require(len(actual_inventory) == len(expected_inventory) and set(actual_inventory) == expected_inventory,
            "Actual cohort rows do not match the exact planned case/repetition inventory")
    original_summary_path = cohort_path.parent / "original-summary.json"
    runner.summarize(manifest, cohort_path, original_summary_path)
    original_summary = load(original_summary_path)
    require(all(item["manual_review_completed"] for item in original_summary["results"]),
            "Manual reviews are incomplete")
    revised = {item["run_id"]: item for item in regrade["results"]}
    require(len(revised) == len(regrade["results"]) == regrade["corrected_subjects"] == 6,
            "R1 must contain exactly six distinct original SVG trials")
    expected_revised = {item["run_id"] for item in cohort["results"]
                        if item["case"] in {"geometry", "relations"}}
    require(set(revised) == expected_revised, "Unexpected corrected trials")
    rows = []
    for record in cohort["results"]:
        case, run_id = record["case"], record["run_id"]
        run_dir = ROOT / "evaluations" / "runs" / run_id
        manual_path = run_dir / "manual-benchmark-review.json"
        manual = load(manual_path)
        require(manual["case"] == case and manual["run_id"] == run_id and
                manual["evidence_boundary"] == "local-only", "Manual identity/scope differs")
        manual_passed = all(manual.get(key) is True for key in COMPONENTS)
        original_artifact_passed = record["independent"]["exit_code"] == 0
        original_machine = record["payload_matches"] and all(
            record[key]["exit_code"] == 0 for key in ("harness", "independent", "read_surface"))
        require(original_machine == record["machine_passed"], "Original gate record differs")
        artifact_passed = original_artifact_passed
        correction = None
        if run_id in revised:
            correction = revised[run_id]
            require(correction["case"] == case and correction["output_hashes_unchanged"] is True
                    and correction["workspace_before_sha256"] == correction["workspace_after_sha256"],
                    "Regrade altered original artifacts")
            current_digest, current_count = workspace_digest(run_dir / "workspace")
            require(current_digest == correction["workspace_before_sha256"] and
                    current_count == correction["workspace_file_count"],
                    "Current workspace differs from the sealed correction subject")
            require(correction["original_artifact_checks_passed"] == original_artifact_passed,
                    "Original oracle verdict changed")
            artifact_passed = correction["artifact_checks_passed"] is True
            require(correction["passed"] == artifact_passed, "Inconsistent R1 gate")
        machine_passed = (record["payload_matches"] and record["harness"]["exit_code"] == 0
                          and record["read_surface"]["exit_code"] == 0 and artifact_passed)
        evaluation = load(run_dir / "evaluation-result.json")
        reads = load(run_dir / "benchmark-read-surface.json")
        classifications = []
        if correction and not original_artifact_passed:
            classifications.append("validator-design: equivalent RGB hex lettercase")
        if record["harness"]["exit_code"] != 0 or record["read_surface"]["exit_code"] != 0:
            classifications.append("agent: retained tool error")
        if manual["narrative_review_passed"] is False:
            classifications.append("agent: incomplete required rendered-marker review")
        artifacts = [evidence(run_dir / "workspace" / path)
                     for path in manifest["cases"][case]["expected_outputs"]]
        for item in artifacts:
            item["path"] = item["path"].split("/workspace/", 1)[1]
        original_outputs = {item["path"]: item for item in load(run_dir / "artifact-check.json")["outputs"]}
        require(set(original_outputs) == {item["path"] for item in artifacts} and
                all(item["sha256"] == original_outputs[item["path"]]["sha256"] and
                    item["bytes"] == original_outputs[item["path"]]["sizeBytes"] for item in artifacts),
                "Current task artifacts differ from the original strict harness snapshot")
        for path, pinned in manifest["subject"]["files"].items():
            resource = run_dir / "workspace" / "skills" / "lucidchart-svg" / path
            require(resource.stat().st_size == pinned["sizeBytes"] and sha(resource) == pinned["sha256"],
                    "Current copied skill resource differs from the frozen subject")
        row = {"case": case, "repetition": record["repetition"], "run_id": run_id,
               "original_artifact_passed": original_artifact_passed,
               "corrected_artifact_passed": artifact_passed,
               "strict_harness_passed": record["harness"]["exit_code"] == 0,
               "read_surface_machine_passed": record["read_surface"]["exit_code"] == 0,
               "payload_matches": record["payload_matches"],
               "outputs_match_original_harness_hashes": True,
               "original_machine_passed": original_machine, "corrected_machine_passed": machine_passed,
               "original_joint_passed": original_machine and manual_passed,
               "corrected_joint_passed": machine_passed and manual_passed,
               "manual_components": {key: manual[key] for key in COMPONENTS},
               "failure_classifications": classifications, "manual_findings": manual["findings"],
               "pi_duration_seconds": evaluation["durationSeconds"],
               "reported_token_usage": reads["usageTotals"],
               "tool_error_findings": reads["findings"], "artifacts": artifacts,
               "evidence": {name: evidence(run_dir / name) for name in (
                   "run-manifest.json", "evaluation-result.json", "events.jsonl",
                   "artifact-check.json", "independent-benchmark.json", "benchmark-read-surface.json",
                   "skill-integrity-check.json", "manual-benchmark-review.json")}}
        if correction:
            row["verifier_revision"] = {
                "revision_id": regrade["revision_id"],
                "workspace_sha256": correction["workspace_before_sha256"],
                "workspace_file_count": correction["workspace_file_count"],
                "report": evidence(run_dir / "independent-benchmark-r1.json")}
        rows.append(row)
    cases = {}
    for case, spec in manifest["cases"].items():
        observed = [row for row in rows if row["case"] == case]
        original = sum(row["original_joint_passed"] for row in observed)
        corrected = sum(row["corrected_joint_passed"] for row in observed)
        cases[case] = {"planned_trials": spec["repetitions"], "completed_trials": len(observed),
                       "required_joint_passes": spec["required_joint_passes"],
                       "original_joint_passes": original, "corrected_joint_passes": corrected,
                       "original_threshold_met": len(observed) == spec["repetitions"] and original >= spec["required_joint_passes"],
                       "corrected_threshold_met": len(observed) == spec["repetitions"] and corrected >= spec["required_joint_passes"]}
    require(performance["complete"] is True and len(performance["workloads"]) == 9 and
            all(item["passed"] and item["measured_repetitions"] == 3
                for item in performance["workloads"]), "Performance evidence incomplete")
    workload_fields = ("family", "items", "passed", "measured_repetitions", "median_seconds",
                       "minimum_seconds", "maximum_seconds", "source_sha256", "source_bytes", "package_sha256")
    result = {"schema_version": 1, "benchmark_id": manifest["benchmark_id"], "date": "2026-10-07",
              "visibility": "public-development", "is_holdout": False,
              "subject": manifest["subject"], "model": manifest["model"], "thinking": manifest["thinking"],
              "planned_trials": manifest["required_trials"], "completed_trials": len(rows),
              "original_artifact_passes": sum(row["original_artifact_passed"] for row in rows),
              "corrected_artifact_passes": sum(row["corrected_artifact_passed"] for row in rows),
              "original_machine_passes": sum(row["original_machine_passed"] for row in rows),
              "corrected_machine_passes": sum(row["corrected_machine_passed"] for row in rows),
              "original_joint_passes": sum(row["original_joint_passed"] for row in rows),
              "corrected_joint_passes": sum(row["corrected_joint_passed"] for row in rows),
              "original_case_thresholds_met": sum(row["original_threshold_met"] for row in cases.values()),
              "corrected_case_thresholds_met": sum(row["corrected_threshold_met"] for row in cases.values()),
              "cases": cases, "resources": original_summary["resources"],
              "performance": {"scope": performance["timing_scope"], "platform": performance["platform"],
                              "python_version": performance["python_version"],
                              "workloads": [{key: item.get(key) for key in workload_fields}
                                            for item in performance["workloads"]]},
              "evidence": {"original_manifest": evidence(manifest_path), "original_cohort": evidence(cohort_path),
                           "original_summary": evidence(original_summary_path), "regrade": evidence(regrade_path),
                           "revision_manifest": evidence(revision_manifest), "performance": evidence(performance_path),
                           "archiver": evidence(Path(__file__).resolve())},
              "resampling": False, "artifacts_repaired": False, "skill_changed": False,
              "live_lucid_acceptance": "unverified", "trials": rows}
    output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("cohort", "regrade", "performance", "output"):
        parser.add_argument(f"--{name}", required=True, type=Path)
    args = parser.parse_args()
    result = archive(args.cohort.resolve(), args.regrade.resolve(), args.performance.resolve(), args.output.resolve())
    print(json.dumps({key: result[key] for key in ("completed_trials", "original_joint_passes",
                                                  "corrected_joint_passes", "corrected_case_thresholds_met")}))


if __name__ == "__main__":
    main()
