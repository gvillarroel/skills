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

## Pi cost-elasticity extension

The `pi-cost-elasticity` extension is a separate, fully offline deterministic
ledger. It makes no Pi, Copilot, or model API calls. It fixes the harness to Pi
and the provider route to GitHub Copilot, then changes one prompt, tool, cache,
or compaction parameter at a time. Its call-level output separates uncached
input, cache reads, cache writes, and output; applies the route-specific 200k
Luna and 272k Terra/Sol long-context thresholds; and scales one hypothetical
execution algebraically to 1,000 and 1,000,000 monthly executions.

The extension includes the requested 1,000-token system-prompt elasticity,
four-versus-five sequential and batched tool comparisons, 800k long-session
strategies, compaction-cache sensitivities, prefix churn, retained tool results,
output size, and extra model roundtrips. Its quality layer reports the maximum
external loss that token savings can tolerate; it does not invent an empirical
quality effect.

## Pi context-rot extension

The `pi-context-rot` extension joins that deterministic cost ledger to an
explicitly hypothetical session-quality model. It compares the same 39-call
grow-to-800k trajectory with fixed-200k and model-threshold compaction policies,
then varies degradation onset and strength, per-compaction evidence survival,
evidence position, retry cap, cache treatment, and model cost tier.

Historical NoLiMa, RULER, Chroma LongMemEval, and Lost in the Middle results are
stored as a source-bound evidence inventory. They define observed endpoints and
stress profiles, not a GPT-5.6 calibration. Retention thresholds are
interpolated only within observed brackets and never extrapolated. The named
primary case, all 1,188 challenge points, and the exact decision boundaries are
therefore labeled model-conditional. The bundle remains fully offline and makes
no Pi, Copilot, or model call.

## Project layout

- `source/`: official rate snapshot, assumptions, and live calibration summary.
- `src/model.py`: the trusted simulation adapter and its 123-parameter contract.
- `studies/`: generated experiment specifications for the three studies.
- `scripts/build_experiments.py`: deterministic specification generator/checker.
- `scripts/run_all_studies.py`: parallel plan/run/analyze/validate orchestrator.
- `scripts/analyze_studies.py`: cross-study consolidation and decision tables.
- `scripts/test_model.py` and `scripts/test_analyze_studies.py`: regression tests.
- `src/pi_cost_elasticity.py`: deterministic Pi-only request and pricing ledger.
- `scripts/run_pi_cost_elasticity.py`: offline bundle generator.
- `scripts/test_pi_cost_elasticity.py`: closed-form regression oracles.
- `scripts/validate_pi_cost_elasticity.py`: independent bundle recomputation.
- `src/pi_context_rot.py`: context-length, fidelity, retry, and cost model.
- `scripts/run_pi_context_rot.py`: offline context-rot bundle generator.
- `scripts/test_pi_context_rot.py`: deterministic and Monte Carlo regression
  oracles.
- `scripts/validate_pi_context_rot.py`: independent context-rot recomputation.
- `source/pi-context-rot-spec-20260904.json`: frozen context-rot preregistration.
- `source/context-rot-evidence-20260904.csv`: source-bound empirical inventory.
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

Reproduce only the offline Pi elasticity extension with:

```powershell
python -B projects\harness-efficiency-study\scripts\test_pi_cost_elasticity.py
python -B projects\harness-efficiency-study\scripts\run_pi_cost_elasticity.py `
  --output-dir projects\harness-efficiency-study\artifacts\runs\pi-cost-elasticity
python -B projects\harness-efficiency-study\scripts\validate_pi_cost_elasticity.py `
  projects\harness-efficiency-study\artifacts\runs\pi-cost-elasticity
```

Reproduce the context-rot extension without any provider/model execution with:

```powershell
python -B projects\harness-efficiency-study\scripts\test_pi_context_rot.py
python -B projects\harness-efficiency-study\scripts\run_pi_context_rot.py `
  --cost-bundle evaluations\harness-efficiency-study\20260904\pi-cost-elasticity `
  --evidence-csv projects\harness-efficiency-study\source\context-rot-evidence-20260904.csv `
  --spec-json projects\harness-efficiency-study\source\pi-context-rot-spec-20260904.json `
  --output-dir projects\harness-efficiency-study\artifacts\runs\pi-context-rot
python -B projects\harness-efficiency-study\scripts\validate_pi_context_rot.py `
  projects\harness-efficiency-study\artifacts\runs\pi-context-rot `
  --cost-bundle evaluations\harness-efficiency-study\20260904\pi-cost-elasticity
```

## Inference boundary

The model is a transparent decision laboratory, not a benchmark of production
repositories. Its quality, retry, latency, failure, compaction, and human-review
relationships are declared assumptions. Use the results to decide what to
measure and which policies deserve an empirical trial. Use matched real tasks,
the same provider/model, a fixed external verifier, and repeated observations
before adopting a harness as a production standard.
