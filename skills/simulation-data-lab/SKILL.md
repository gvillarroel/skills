---
name: simulation-data-lab
description: Design, run, audit, and compare reproducible stochastic or deterministic simulations that generate analysis-ready datasets for scenario exploration, sensitivity analysis, and support or challenge hypotheses under explicit model assumptions. Use for Monte Carlo, discrete-event, agent-based, dynamical-system, or counterfactual experiments; do not use for purely visual animation, Harbor evaluation datasets, or claims of empirical causal proof.
---

# Simulation Data Lab

Produce an executable experiment and an explorable data bundle, not only a
model or chart. Treat every conclusion as conditional on the model, assumptions,
parameter range, and diagnostics. A simulation alone cannot prove or refute a
claim about the real world.

## Route the request

- Preserve an engine, model format, or output path chosen by the user. Wrap an
  existing model instead of translating it silently.
- When the engine is open, select it from the system structure rather than from
  domain nouns. Read [references/engine-selection.md](references/engine-selection.md).
- Use this skill when persistent simulated data and an auditable experiment are
  primary. Use a visualization workflow when the request is only an interactive
  explanation or animation; use Harbor dataset tooling only for agent-evaluation
  tasks.
- If a proprietary model cannot be executed locally, create a precise run and
  export plan, but do not fabricate results or claim that it ran.

## Build the experiment

1. Operationalize the question before writing the model. Define the system
   boundary, claim, estimand, scenarios, machine-readable contrast, practical
   threshold, primary and challenge design points, time horizon or stopping
   condition, uncertain inputs, and explicit assumptions. Read
   [references/experiment-design.md](references/experiment-design.md).
2. Separate interventions into `scenarios`, epistemic or sensitivity settings
   into `designPoints`, and stochastic repetitions into `replications`. Do not
   count events, time steps, or agents within one run as independent replicates.
   Set `uncertaintyMode=deterministic` only for a one-run-per-cell model with no
   stochastic Monte Carlo error; otherwise use `stochastic`.
   Put every material policy, calibration, and assumption input in a scenario or
   design point with its unit and source. Do not hide an explorable input as a
   model-code literal. For a time-dependent model, set `experiment.timeUnit`;
   any emitted observation or event repeats it in `time_unit`.
3. Choose `pilot`, `exploratory`, `confirmatory`, or `robustness` before seeing
   the corresponding results. Keep pilot or calibration outputs distinct from
   confirmatory evidence and record deviations from a frozen plan.
4. Create a fresh output directory outside this read-only skill. When starting
   a Python model, copy and adapt `assets/templates/experiment.json` and
   `assets/templates/model.py`; remove template-specific claims and assumptions.
   Preserve every required hypothesis field from the experiment template,
   including both `decisionRule` and `falsificationRule`, even when
   `analysis.kind=not-identifiable`.
5. Validate and expand the spec into a stable run matrix:

```text
python <skill-directory>/scripts/run_simulation_experiment.py plan --spec <bundle>/experiment.json --output-dir <bundle>/design
```

Inspect the run count before execution. Use a bounded pilot first when runtime,
memory, or external cost is uncertain.

Treat bundled scripts as executable interfaces during normal work. Use the
commands documented here and in the references; do not read their source merely
to discover arguments or output fields.

## Implement and verify the model

- Keep the model mechanism separate from experiment orchestration. For the
  bundled runner, implement `simulate(run)` and concrete `MODEL_METADATA` as
  described in
  [references/data-and-provenance-contract.md](references/data-and-provenance-contract.md).
- Execute only agent-authored or reviewed, trusted model code. Importing a model
  runs arbitrary Python in the current process; inspect its imports and reject
  undeclared network, credential, subprocess, or filesystem side effects.
- Consume the assigned run seed through an explicit RNG object. Never use
  ambient global randomness or derive seeds from worker completion order.
- Use `paired-across-scenarios` only when common random numbers have a valid
  semantic coupling and the contrast will be analyzed as paired. Use named
  substreams inside complex models so scenario-dependent code paths do not
  silently destroy the coupling. Use the stable substream recipe in the data
  contract; never use Python's process-randomized `hash()` for a seed.
- Before a full run, test a fixed seed, a hand-calculable case, boundary and
  extreme inputs, domain invariants, and a perturbation expected to change an
  outcome. For continuous solvers, also test time-step or tolerance convergence;
  for steady-state models, test warm-up and horizon sensitivity.
- Collect only what the estimands and diagnostics require. Replication outcomes
  are mandatory; dense observations, events, and agent state are opt-in because
  they can dominate storage without adding inferential information.
- Mark failed numerical, conservation, accounting, and structural invariants as
  hypothesis-invalidating diagnostics. Do not leave a failed inference gate as
  advisory merely to retain a run in the analysis.

Run a compatible Python adapter with:

```text
python <skill-directory>/scripts/run_simulation_experiment.py run --root <bundle> --model model.py
```

The runner records every planned run, preserves failures, rejects non-finite or
schema-drifting output, calculates descriptive summaries and Monte Carlo error,
and emits starter DuckDB queries. If the chosen engine needs native parallel or
distributed execution, preserve the same run IDs, semantic seed keys, table
grains, and failure records in its adapter.

The bundled runner is for bounded local work. Individual ceilings are 100,000
runs, 100 declared outcomes, and 10,000 observation, event, or diagnostic rows
of each kind per run, but one stricter joint ceiling permits at most 1,000,000
materialized rows across the plan, runs, outcomes, summaries, observations,
events, and diagnostics. Use an engine-native streaming or partitioned Parquet
adapter for larger jobs; do not raise the limit and materialize an unsafe
workload in memory.

## Analyze and challenge

- Encode each supported core contrast as `comparison - baseline`, classify every
  design point as primary or challenge, and use the declared paired, independent,
  or deterministic mode. Keep design points separate.
- Report effect size, interval, practical threshold, replication count, and
  Monte Carlo standard error where applicable. A small p-value is not a
  substitute for a useful effect or a stable result.
- Actively try to make each evaluated claim fail within plausible bounds:
  stress assumptions, alternate input distributions, inspect failed-run regions,
  test numerical settings, or compare a rival mechanism. Read
  [references/diagnostics-and-inference.md](references/diagnostics-and-inference.md).
- Use only `supports-under-model`, `challenges-under-model`,
  `inconclusive-under-model`, or `not-identifiable-from-design`. Never say that
  the simulation proved reality. State when external calibration or validation
  remains necessary.
- Do not hand-author inferential numbers or statuses. For declared hypotheses,
  generate the result from validated replication outcomes:

```text
python <skill-directory>/scripts/analyze_simulation_hypotheses.py --root <bundle>
```

The v1 analyzer supports model-conditional mean differences with normal-Wald
Monte Carlo intervals for paired or independent stochastic replications, plus
exact deterministic contrasts and explicit non-identifiability. Read the result
contract before using a different estimand.

## Validate and deliver

Run the bundle integrity audit after analysis. It separately recomputes every
v1 estimate, MCSE, interval, per-design-point decision, aggregate status, and
challenge result from the generated tables:

```text
python <skill-directory>/scripts/validate_simulation_bundle.py --root <bundle> --report <bundle>/validation-report.json
```

Do not deliver an incomplete bundle as successful. `--allow-incomplete` writes
an explicitly non-release diagnostic report with `ok=false` and still exits 2;
use it only while repairing the model. Read
[references/data-and-provenance-contract.md](references/data-and-provenance-contract.md)
before changing the core tables or moving high-volume data to Parquet.

Hand off the question, model boundary, engine choice, run/failed counts, main
effect with uncertainty, strongest counterexample, unresolved assumptions,
validation result, and exact artifact paths. Distinguish a preregistered
`challenge` role from the result closest to the decision threshold; calculate
and label either claim correctly. Point the user to
`analysis/explore.sql`, `analysis/summary.csv`, and the data dictionary so
exploration can continue without reverse-engineering the model.
