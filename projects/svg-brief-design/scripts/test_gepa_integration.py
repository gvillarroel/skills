#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = ["gepa==0.1.2"]
# ///
"""Deterministic integration checks; no Harbor trials or model calls are made."""
from pathlib import Path
import asyncio
import json
from gepa.optimize_anything import optimize_anything, EngineConfig, GEPAConfig, ReflectionConfig
from run_gepa_study import FORBIDDEN, sanitized_development_feedback
from gepa_async_bridge import AsyncEvaluatorBridge

REPO = Path(__file__).resolve().parents[3]
STUDY = REPO / "evaluations/runs/svg-brief-design-gepa-20260925"


def main():
    rejected = [
        '<svg viewBox="0 0 10 10"/>', '<path d="M0 0L1 1"/>',
        'data:image/svg+xml;base64,anything', 'vector-020',
        'https://example.invalid/reference.svg?download=1',
    ]
    assert all(FORBIDDEN.search(text) for text in rejected)
    assert not FORBIDDEN.search("Use coherent strokes and intentional negative space. Consult references/svg-mechanics.md.")
    try:
        sanitized_development_feedback(Path("/harbor-trials/holdout-candidate/one/trials"), "pi")
    except ValueError:
        pass
    else:
        raise AssertionError("Private feedback was not rejected")
    reflection_calls = []

    def reflect(prompt):
        reflection_calls.append(prompt)
        return "```\ngood\n```"

    observed_loops = set()

    async def evaluate(candidate, example):
        observed_loops.add(id(asyncio.get_running_loop()))
        await asyncio.sleep(0)
        return (1.0 if candidate.strip() == "good" else 0.2), {"feedback": "Use the word good. This is a deterministic integration fixture."}

    bridge = AsyncEvaluatorBridge(evaluate)
    result = optimize_anything(
        seed_candidate="bad", evaluator=bridge, dataset=["fixture-one", "fixture-two"], valset=["fixture-one", "fixture-two"],
        objective="Exercise the supported callable reflection interface.", background="Integration fixture only; not quality evidence.",
        config=GEPAConfig(
            engine=EngineConfig(run_dir=str(STUDY / "integration-async-fixture"), max_metric_calls=8, max_candidate_proposals=1, max_workers=2, parallel=True, cache_evaluation=False, raise_on_exception=True, display_progress_bar=False),
            reflection=ReflectionConfig(reflection_lm=reflect, reflection_minibatch_size=1, reflection_prompt_template=None),
        ),
    )
    bridge.close()
    assert result.best_candidate.strip() == "good" and len(reflection_calls) == 1
    assert len(observed_loops) == 1
    report = {"passed": True, "forbidden_payload_cases": len(rejected), "private_feedback_rejected": True, "callable_reflection_verified": True, "single_async_loop": True, "real_model_calls": 0, "harbor_trials": 0, "purpose": "Deterministic API and boundary integration check only"}
    with (STUDY / "integration-async-check.json").open("x") as handle:
        json.dump(report, handle, indent=2)
    print(json.dumps(report))


if __name__ == "__main__":
    main()
