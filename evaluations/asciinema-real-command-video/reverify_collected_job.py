#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""Re-run the evaluator against artifacts already collected by Harbor."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--job-root", type=Path, required=True)
    parser.add_argument("--dataset-root", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_arguments()
    job_root = args.job_root.resolve()
    dataset_root = args.dataset_root.resolve()
    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    verifier = Path(__file__).with_name("verify_task.py").resolve()
    results: list[dict[str, object]] = []

    for trial in sorted(path for path in job_root.iterdir() if path.is_dir()):
        task_id = trial.name.split("__", 1)[0]
        result_path = trial / "result.json"
        if result_path.is_file():
            try:
                trial_result = json.loads(result_path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                trial_result = {}
            if isinstance(trial_result, dict) and isinstance(
                trial_result.get("task_name"), str
            ):
                task_id = trial_result["task_name"]
        contract = dataset_root / task_id / "tests" / "contract.json"
        artifact_root = trial / "artifacts"
        trial_output = output_dir / task_id
        if not contract.is_file():
            raise SystemExit(f"Contract is missing for {task_id}: {contract}")
        trial_output.mkdir(parents=True, exist_ok=True)
        environment = {
            **os.environ,
            "HARBOR_APP_DIR": str(artifact_root),
            "HARBOR_ARTIFACT_DIR": str(artifact_root),
            "HARBOR_CONTRACT_PATH": str(contract),
            "HARBOR_VERIFIER_LOG_DIR": str(trial_output),
        }
        completed = subprocess.run(
            [sys.executable, str(verifier)],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            env=environment,
            check=False,
            timeout=600,
        )
        verification_path = trial_output / "verification.json"
        if not verification_path.is_file():
            raise SystemExit(
                f"Verifier did not produce output for {task_id}: {completed.stderr}"
            )
        result = json.loads(verification_path.read_text(encoding="utf-8"))
        result["verifierExitCode"] = completed.returncode
        results.append(result)

    aggregate = {
        "schemaVersion": 1,
        "jobRoot": str(job_root),
        "datasetRoot": str(dataset_root),
        "caseCount": len(results),
        "passCount": sum(1 for result in results if result["ok"]),
        "results": results,
    }
    (output_dir / "aggregate.json").write_text(
        json.dumps(aggregate, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(json.dumps(aggregate, indent=2, sort_keys=True))
    return 0 if aggregate["passCount"] == aggregate["caseCount"] else 1


if __name__ == "__main__":
    sys.exit(main())
