#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

"""Build, execute, validate, and consolidate all harness-efficiency studies."""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import shutil
import subprocess
import sys
from typing import Sequence


STUDIES = ("controlled-harness", "monthly-economics", "usage-policy")


def _run(command: Sequence[str], cwd: Path) -> None:
    print("RUN " + " ".join(command), flush=True)
    subprocess.run(command, cwd=cwd, check=True)


def _run_study(
    study: str,
    repository_root: Path,
    run_root: Path,
    project_root: Path,
    model: Path,
    runner: Path,
    hypothesis_analyzer: Path,
    validator: Path,
) -> None:
    bundle = run_root / study
    bundle.mkdir()
    shutil.copy2(project_root / "studies" / study / "experiment.json", bundle)
    shutil.copy2(model, bundle / "model.py")
    _run(
        [
            sys.executable,
            "-B",
            str(runner),
            "plan",
            "--spec",
            str(bundle / "experiment.json"),
            "--output-dir",
            str(bundle / "design"),
        ],
        repository_root,
    )
    _run(
        [
            sys.executable,
            "-B",
            str(runner),
            "run",
            "--root",
            str(bundle),
            "--model",
            "model.py",
        ],
        repository_root,
    )
    _run(
        [
            sys.executable,
            "-B",
            str(hypothesis_analyzer),
            "--root",
            str(bundle),
        ],
        repository_root,
    )
    _run(
        [
            sys.executable,
            "-B",
            str(validator),
            "--root",
            str(bundle),
            "--report",
            str(bundle / "validation-report.json"),
        ],
        repository_root,
    )


def run_all(repository_root: Path, run_root: Path) -> None:
    if run_root.exists() and any(run_root.iterdir()):
        raise ValueError(f"run root must be fresh or empty: {run_root}")
    run_root.mkdir(parents=True, exist_ok=True)

    project_root = repository_root / "projects" / "harness-efficiency-study"
    skill_root = repository_root / "skills" / "simulation-data-lab"
    generator = project_root / "scripts" / "build_experiments.py"
    model = project_root / "src" / "model.py"
    runner = skill_root / "scripts" / "run_simulation_experiment.py"
    hypothesis_analyzer = skill_root / "scripts" / "analyze_simulation_hypotheses.py"
    validator = skill_root / "scripts" / "validate_simulation_bundle.py"
    consolidator = project_root / "scripts" / "analyze_studies.py"

    _run([sys.executable, "-B", str(generator), "--check"], repository_root)
    with ThreadPoolExecutor(max_workers=len(STUDIES)) as executor:
        futures = [
            executor.submit(
                _run_study,
                study,
                repository_root,
                run_root,
                project_root,
                model,
                runner,
                hypothesis_analyzer,
                validator,
            )
            for study in STUDIES
        ]
        for future in futures:
            future.result()

    _run(
        [
            sys.executable,
            "-B",
            str(consolidator),
            "--runs-root",
            str(run_root),
            "--output-dir",
            str(run_root / "consolidated"),
        ],
        repository_root,
    )
    manifest = {
        "ok": True,
        "studyBundles": [str((run_root / study).resolve()) for study in STUDIES],
        "consolidatedAnalysis": str((run_root / "consolidated").resolve()),
    }
    (run_root / "run-all-result.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="",
    )


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--repository-root",
        type=Path,
        default=Path(__file__).resolve().parents[3],
        help="skills repository root",
    )
    parser.add_argument(
        "--run-root",
        type=Path,
        required=True,
        help="fresh directory for ignored raw bundles and consolidated analysis",
    )
    return parser


def main() -> int:
    args = _parser().parse_args()
    try:
        run_all(args.repository_root.resolve(), args.run_root.resolve())
    except (OSError, ValueError, subprocess.CalledProcessError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, sort_keys=True))
        return 2
    print(
        json.dumps(
            {
                "ok": True,
                "runRoot": str(args.run_root.resolve()),
                "studies": list(STUDIES),
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
