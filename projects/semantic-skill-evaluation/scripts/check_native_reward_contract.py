#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Check canonical Oracle report rewards against a trace gate before inference.

This is an interface preflight over trusted harbor-run-results reports, not a
trial scorer, evaluator, optimizer, recovery tool, or report authenticity check.
It emits aggregate metadata only, including when an input report is private.
"""
from __future__ import annotations

import argparse
from collections import Counter
from hashlib import sha256
import json
import math
from pathlib import Path
import sys


def pairs(rows):
    result = {}
    for key, value in rows:
        if key in result:
            raise ValueError("Duplicate JSON key")
        result[key] = value
    return result


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8-sig"), object_pairs_hook=pairs,
                      parse_constant=lambda _: (_ for _ in ()).throw(ValueError("Nonfinite JSON")))


def number(value):
    return type(value) in (int, float) and math.isfinite(value)


def required_rewards(config):
    if type(config.get("schemaVersion")) is not int or config["schemaVersion"] != 2:
        raise ValueError("A schema2 trace config is required")
    harbor = config["harbor"]
    key, threshold = harbor["rewardKey"], harbor["passThreshold"]
    extra = harbor["requiredRewards"]
    if not isinstance(key, str) or not key.strip() or not number(threshold) or not isinstance(extra, dict):
        raise ValueError("Invalid declared reward contract")
    required = {key: threshold}
    for name, value in extra.items():
        if not isinstance(name, str) or not name.strip() or not number(value):
            raise ValueError("Invalid required reward")
        required[name] = max(required.get(name, value), value)
    return required


def inspect(config, reports):
    required = required_rewards(config)
    failures = Counter()
    jobs_checked = trials_checked = 0
    if not reports:
        raise ValueError("At least one actual canonical Oracle report is required")
    for report in reports:
        if report.get("schemaVersion") != 1 or report.get("source") != "harbor" or report.get("harborVersion") != "0.18.0":
            raise ValueError("Expected an owning native Harbor0.18.0 final report")
        if report.get("rewardKey") != config["harbor"]["rewardKey"] or report.get("passThreshold") != config["harbor"]["passThreshold"]:
            failures["primary-report-contract-mismatch"] += 1
        jobs = report.get("jobs")
        if not isinstance(jobs, list) or not jobs:
            raise ValueError("Native report has no jobs")
        for job in jobs:
            jobs_checked += 1
            summary, trials = job["summary"], job["trials"]
            counts = [summary.get(name) for name in ("requestedTrials", "completedTrials", "passedTrials", "erroredTrials")]
            if any(type(value) is not int or value < 0 for value in counts) or not isinstance(trials, list):
                raise ValueError("Invalid native completeness metadata")
            requested, completed, passed, errors = counts
            if job.get("complete") is not True or job.get("completenessProblems") or requested < 1 or requested != completed or len(trials) != completed:
                failures["incomplete-canonical-job"] += 1
            if passed != completed or errors:
                failures["canonical-primary-outcome-not-clean"] += 1
            for trial in trials:
                trials_checked += 1
                if trial.get("agent") != "oracle":
                    failures["not-canonical-oracle-evidence"] += 1
                if trial.get("passed") is not True or trial.get("error") is not None:
                    failures["canonical-trial-not-clean"] += 1
                rewards = trial.get("rewards")
                if not isinstance(rewards, dict):
                    failures["missing-reward-map"] += 1
                    continue
                for name, threshold in required.items():
                    if name not in rewards:
                        failures["missing-required-reward:" + name] += 1
                    elif not number(rewards[name]):
                        failures["invalid-required-reward:" + name] += 1
                    elif rewards[name] < threshold:
                        failures["canonical-required-reward-below-threshold:" + name] += 1
    return {"schemaVersion": 1, "kind": "canonical-reward-interface-preflight", "notAScorer": True,
            "passed": not failures, "reportsChecked": len(reports), "jobsChecked": jobs_checked,
            "trialsChecked": trials_checked, "requiredRewardKeys": sorted(required),
            "failureCounts": dict(sorted(failures.items())),
            "limits": "Trusted native reports and actual canonical Oracle provenance remain prerequisites; no semantic score is created or repaired."}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True, help="Frozen schema2 trace config")
    parser.add_argument("--report", type=Path, action="append", required=True, help="Owning actual Oracle final-report.json; repeat per cohort")
    parser.add_argument("--output", type=Path, help="New aggregate receipt; never an input or existing file")
    args = parser.parse_args(argv)
    try:
        paths = [args.config, *args.report]
        if args.output and (args.output.exists() or args.output.resolve() in {p.resolve() for p in paths}):
            raise ValueError("Output must be a new file outside the inputs")
        result = inspect(load(args.config), [load(path) for path in args.report])
        result["configSha256"] = sha256(args.config.read_bytes()).hexdigest()
        result["sourceReportSha256"] = [sha256(path.read_bytes()).hexdigest() for path in args.report]
        if args.output:
            with args.output.open("x", encoding="utf-8", newline="\n") as stream:
                stream.write(json.dumps(result, indent=2) + "\n")
        print(json.dumps(result, sort_keys=True))
        return 0 if result["passed"] else 1
    except (OSError, ValueError, KeyError, TypeError) as error:
        # Avoid echoing private file names, task IDs or JSON contents.
        print(json.dumps({"passed": False, "preflightError": type(error).__name__}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
