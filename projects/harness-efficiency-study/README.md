# Harness efficiency study

This project evaluates how coding-agent harness design, provider routing, model
tier, tool exposure, cache behavior, and billing policy interact. It compares
GitHub Copilot CLI and Pi only after separating the product label from the
mechanisms that can actually change outcomes.

The study is intentionally hybrid:

- a small live pilot measures fixed prompt/tool-registry overhead and warm-cache
  behavior on one trivial prompt;
- three preregistered synthetic studies explore mechanisms and boundary cases;
- explicit `not-identifiable-from-design` hypotheses prevent simulated results
  from being presented as evidence of real-world harness superiority.

The simulation is built with the repository's `simulation-data-lab` skill. Its
model is deterministic for a given specification and seed, uses named SHA-256
random substreams, couples matched scenarios with common random numbers, and
emits separate provider-value, marginal-cash, allocated-cash, and total-economic
ledgers.

## Project layout

- `source/`: official rate snapshot, assumptions, and live calibration summary.
- `src/model.py`: the trusted simulation adapter and its 123-parameter contract.
- `studies/`: generated experiment specifications for the three studies.
- `scripts/build_experiments.py`: deterministic specification generator/checker.
- `scripts/run_all_studies.py`: parallel plan/run/analyze/validate orchestrator.
- `scripts/analyze_studies.py`: cross-study consolidation and decision tables.
- `scripts/test_model.py` and `scripts/test_analyze_studies.py`: regression tests.
- `artifacts/`: ignored raw run bundles and temporary verification output.
- `../../evaluations/harness-efficiency-study/20260904/`: versioned findings,
  validation evidence, and compact exploration tables.

## Reproduce

Run from the repository root:

```powershell
python -B projects\harness-efficiency-study\scripts\test_model.py
python -B projects\harness-efficiency-study\scripts\test_analyze_studies.py
python -B projects\harness-efficiency-study\scripts\build_experiments.py --check
python -B projects\harness-efficiency-study\scripts\run_all_studies.py `
  --run-root projects\harness-efficiency-study\artifacts\runs\reproduction
```

The run root must be fresh or empty. The orchestrator plans, executes, analyzes,
and validates all three studies before generating the consolidated tables.

## Inference boundary

The model is a transparent decision laboratory, not a benchmark of production
repositories. Its quality, retry, latency, failure, compaction, and human-review
relationships are declared assumptions. Use the results to decide what to
measure and which policies deserve an empirical trial. Use matched real tasks,
the same provider/model, a fixed external verifier, and repeated observations
before adopting a harness as a production standard.
