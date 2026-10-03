#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = ["harbor==0.18.0", "PyYAML>=6,<7"]
# ///
"""Rank every retained candidate from native jobs without making model calls."""
import contextlib
import json
from pathlib import Path
import sys
import run_procedural_population

ROOT = Path(__file__).resolve().parents[3] / "evaluations/runs/svp3"


def arguments():
    first = json.loads((ROOT / "generation-000-argv.json").read_text())
    first[first.index("--generation")+1] = "1"
    return first + ["--candidate", "q=" + str(ROOT / "inputs/q/svg-brief-design"),
                    "--job", "b=" + str(ROOT / "generation-000/candidates/b/harbor-jobs/harbor-pop-g000-b"),
                    "--job", "p=" + str(ROOT / "generation-000/candidates/p/harbor-jobs/harbor-pop-g000-p"),
                    "--job", "q=" + str(ROOT / "jobs/q"), "--analyze-only"]


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "doctor"
    assert mode in {"doctor", "dry-run", "analyze", "stage-validation", "finish-validation"}
    argv = arguments()
    if mode in {"doctor", "dry-run"}:
        argv.remove("--analyze-only")
        while "--job" in argv:
            position = argv.index("--job")
            del argv[position:position+2]
        argv += ["--" + mode]
    if mode in {"stage-validation", "finish-validation"}:
        argv += ["--holdout-template", str(ROOT / "templates/validation.json")]
    if mode == "finish-validation":
        argv += ["--holdout-job", "baseline=" + str(ROOT / "private-jobs/b"), "--holdout-job", "winner=" + str(ROOT / "private-jobs/w")]
    sys.argv = ["population"] + argv
    print(json.dumps({"mode": mode, "model_calls": 0}), flush=True)
    stem = ROOT / f"generation-001-{mode}"
    repeat = 0
    while stem.with_suffix(".stdout.json").exists():
        repeat += 1
        stem = ROOT / f"generation-001-{mode}-{repeat}"
    with stem.with_suffix(".stdout.json").open("x") as out, stem.with_suffix(".stderr.txt").open("x") as err:
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = run_procedural_population.main()
    print(json.dumps({"mode": mode, "exit_code": code}), flush=True)
    return code


if __name__ == "__main__":
    raise SystemExit(main())
