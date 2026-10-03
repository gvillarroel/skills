#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = ["harbor==0.18.0", "gepa==0.1.2"]
# ///
"""Run the deadline-bound additive study through the established native adapter."""
from pathlib import Path
from datetime import datetime, timezone
import json
import os
import run_gepa_study as study


def check_addition(candidate, baseline):
    original = baseline.split()
    proposed = candidate.split()
    iterator = iter(proposed)
    if not all(any(word == wanted for word in iterator) for wanted in original):
        raise ValueError("This experiment permits additions only, not deletion or rewriting of the baseline")
    if not 30 <= len(proposed) - len(original) <= 180:
        raise ValueError("The additive instruction must contain 30 to 180 words")


if __name__ == "__main__":
    study.STUDY = study.REPO / "evaluations/runs/svg-brief-design-deadline-20260926"
    protocol = json.loads((study.STUDY / "protocol.json").read_text())
    assert study.digest(Path(__file__)) == protocol["launcher_sha256"]
    os.environ["GIT_CEILING_DIRECTORIES"] = protocol["runtime_metadata_boundary"]["GIT_CEILING_DIRECTORIES"]
    original_loader = study.load_engine

    def load_bound_engine():
        engine = original_loader()
        original_validate = engine.validate_candidate
        baseline = (study.REPO / "skills/svg-brief-design/SKILL.md").read_text()
        original_trial = engine.run_candidate_trial
        cutoff = datetime.fromisoformat(protocol["trial_admission_cutoff_utc"])

        def validate(candidate, name):
            original_validate(candidate, name)
            if candidate != baseline:
                check_addition(candidate, baseline)

        async def bounded_trial(*args, **kwargs):
            if datetime.now(timezone.utc) >= cutoff:
                raise RuntimeError("Declared trial-admission cutoff reached; incomplete campaign cannot be promoted")
            return await original_trial(*args, **kwargs)

        engine.validate_candidate = validate
        engine.run_candidate_trial = bounded_trial
        return engine

    study.load_engine = load_bound_engine
    study.main()
