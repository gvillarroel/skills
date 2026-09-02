#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Write a native Harbor job config bound to one staged D3 candidate."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys

from build_harbor_dataset import write_job_config


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--split", choices=("development", "validation", "holdout"), required=True)
    parser.add_argument("--skill-source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--jobs-dir", type=Path)
    parser.add_argument("--job-name", required=True)
    parser.add_argument("--attempts", type=int, default=3)
    parser.add_argument("--concurrency", type=int, default=4)
    parser.add_argument("--model", default="gpt-5.3-codex-spark")
    parser.add_argument(
        "--no-prime-environment-skill",
        action="store_false",
        dest="prime_environment_skill",
        help="Install the candidate only through the Harbor agent skill binding.",
    )
    parser.set_defaults(prime_environment_skill=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    run_root = args.run_root.resolve()
    skill_source = args.skill_source.resolve()
    output = args.output.resolve()
    jobs_dir = args.jobs_dir.resolve() if args.jobs_dir else None
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", args.job_name):
        raise SystemExit("--job-name must be lowercase hyphen-case")
    if args.attempts < 1 or args.concurrency < 1:
        raise SystemExit("--attempts and --concurrency must be positive")
    if not (run_root / args.split).is_dir():
        raise SystemExit(f"Frozen split is missing: {run_root / args.split}")
    if not (skill_source / "SKILL.md").is_file():
        raise SystemExit(f"Staged skill is missing SKILL.md: {skill_source}")
    if output.exists():
        raise SystemExit(f"Refusing existing config: {output}")
    repo_root = Path(__file__).resolve().parents[2]
    path = write_job_config(
        run_root,
        repo_root,
        args.split,
        args.job_name,
        args.attempts,
        args.concurrency,
        args.model,
        skill_source=skill_source,
        config_path=output,
        job_name=args.job_name,
        prime_environment_skill=args.prime_environment_skill,
        jobs_dir=jobs_dir,
    )
    print(
        json.dumps(
            {
                "config": str(path),
                "dataset": str(run_root / args.split),
                "skillSource": str(skill_source),
                "jobName": args.job_name,
                "jobsDir": str(jobs_dir or run_root / "jobs"),
                "primeEnvironmentSkill": args.prime_environment_skill,
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
