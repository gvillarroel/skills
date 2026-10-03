#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""Inspect GEPA progress without opening private trial outcomes or artifacts."""
from pathlib import Path
from collections import Counter
import json
import pickle
import statistics
import argparse

REPO = Path(__file__).resolve().parents[3]
parser = argparse.ArgumentParser()
parser.add_argument("--study", type=Path, default=REPO / "evaluations/runs/svg-brief-design-gepa-20260925")
STUDY = parser.parse_args().study.resolve()
RUN = STUDY / "run-async-compatible"
development = []
for path in sorted((RUN / "harbor-trials/development").glob("*/evaluation.json")):
    row = json.loads(path.read_text())
    development.append({"digest": row.get("skillProvenance", {}).get("candidateSkillMdDigest"), "reward": row.get("reward"), "evaluable": row.get("evaluable"), "error": row.get("error")})
report = {
    "run_finished": (RUN / "run.json").is_file(),
    "execution_failure": (STUDY / "async-compatible-execution-failure.json").is_file(),
    "development_trials_finished": len(development),
    "development_trials_started": len(list((RUN / "harbor-trials/development").glob("*/skills"))),
    "non_evaluable_development_trials": sum(not row["evaluable"] for row in development),
    "candidate_evaluation_counts": dict(Counter(row["digest"] for row in development)),
    "reflection_calls": len(list((STUDY / "reflection").glob("call-*/receipt.json"))),
    "validation_trials_started": sum(len(list((RUN / ("harbor-trials/" + phase)).glob("*/skills"))) for phase in ("validation-baseline", "validation-candidate")),
    "holdout_trials_started": sum(len(list((RUN / ("harbor-trials/" + phase)).glob("*/skills"))) for phase in ("holdout-baseline", "holdout-candidate")),
}
if report["execution_failure"]:
    report["failure"] = json.loads((STUDY / "async-compatible-execution-failure.json").read_text())
# This file is written atomically by our own GEPA process, never by an agent.
# It contains evolution state only; the private gate is not part of GEPA.
state_file = RUN / "gepa/gepa_state.bin"
if state_file.is_file():
    with state_file.open("rb") as handle:
        state = pickle.load(handle)
    report["evolution_pool"] = [{"index": index, "mean": statistics.mean(scores.values()), "cases": len(scores)} for index, scores in enumerate(state.get("prog_candidate_val_subscores", [])) if scores]
print(json.dumps(report, indent=2))
