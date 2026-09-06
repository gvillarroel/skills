---
name: simulation-data-lab
description: Build and execute mathematical models, never the systems being modeled, to generate explorable simulated data, expected behavior, risk estimates, and explicitly conditional uncertainty. Use for stochastic, deterministic, discrete-event, agent-based, dynamical-system, sensitivity, or counterfactual simulations; not for live benchmarks, target-program execution, real agent/model calls, or empirical causal proof.
---

# Simulation Data Lab

Produce an executable experiment and an explorable data bundle, not only a
model or chart. Treat every conclusion as conditional on the model, assumptions,
parameter range, and diagnostics. A simulation alone cannot prove or refute a
claim about the real world.

## Simulation-only boundary

- Execute only mathematical model code, local numerical/simulation engines, and
  local analysis/validation helpers. Do not execute, import as a live client,
  benchmark, instrument, or drive the actual program, agent, service, model,
  hardware, or workflow being emulated. This includes Pi/Copilot sessions,
  inference APIs, local LLM inference, and real tool calls by simulated agents.
- Represent tools, caches, failures, retries, latency, and quality as equations,
  state transitions, probability distributions, and synthetic events. An
  agent-based simulation means modeled actors, not real LLM agents.
- Use supplied or already existing datasets, logs, source files, published
  measurements, and read-only documentation for assumptions or calibration.
  Do not start live pilots, probes, benchmarks, or new target executions to
  obtain missing inputs. Label them assumed, sweep plausible ranges, or report
  non-identifiability. Every pilot in this workflow is a pilot of the simulator.
- External-validation requirements record an evidence gap, not a command to
  close it. Do not automatically launch, delegate, or schedule a real evaluation
  as a follow-up. An explicit empirical-evaluation request is a different
  workflow outside this skill; it does not become a simulation step.

## Route the request

- Preserve a local mathematical engine, model format, or output path chosen by
  the user. Wrap only an offline mathematical model, not the target application.
- When the engine is open, select it from the system structure rather than from
  domain nouns. Read [references/engine-selection.md](references/engine-selection.md).
- Use this skill when persistent simulated data and an auditable experiment are
  primary. Use a visualization workflow when the request is only an interactive
  explanation or animation. Live agent-evaluation tasks are outside this skill.
- If a mathematical model cannot run locally, supply its equations, execution
  plan, and limitations without fabricated results or a remote target run.

## Build the experiment

1. Operationalize the question before writing the model. Define the system
   boundary, claim, estimand, scenarios, machine-readable contrast, practical
   threshold, primary and challenge design points, time horizon or stopping
   condition, uncertain inputs, and explicit assumptions. Read
   [references/experiment-design.md](references/experiment-design.md).
   For realistic disturbances and behavioral uncertainty, read
   [references/uncertainty-and-behavior.md](references/uncertainty-and-behavior.md).
   For every new study, read
   [references/model-variable-review.md](references/model-variable-review.md)
   and author its candidate-variable and interaction review. Work backward from
   the outcomes and scan the wider lifecycle, not only the inputs the user names.
   Explain included, fixed, excluded, and unresolved factors to the human; do
   not claim exhaustive discovery or expose private deliberation. Prioritize
   omissions that could reverse the decision rather than maximizing model size.
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
   Replace the template's `extensions.simulation-data-lab.variableReview` with
   the reviewed candidates, mechanisms, evidence, and next checks for this task.
   Preserve every required hypothesis field from the experiment template,
   including both `decisionRule` and `falsificationRule`, even when
   `analysis.kind=not-identifiable`.
5. Validate and expand the spec into a stable run matrix:

```text
python <skill-directory>/scripts/run_simulation_experiment.py plan --spec <bundle>/experiment.json --output-dir <bundle>/design --require-variable-review
```

Inspect the run count before execution. Use a bounded simulator-only pilot when
local runtime, memory, or numerical stability is uncertain.
Inspect and share `design/model-review.md` and `design/variable-inventory.csv`,
which the planner generates from the spec. Resolve inconsistent parameter links
or units before running. High-impact or unknown-impact omissions require an
explicitly narrower conclusion or further mathematical sensitivity work, not a
silent assumption. Missing human input need not block a labeled exploratory
calculation; ask only when it would materially change the problem or decision.

Treat bundled scripts as executable interfaces during normal work. Use the
commands documented here and in the references; do not read their source merely
to discover arguments or output fields.

## Implement and verify the model

- Keep the model mechanism separate from experiment orchestration. For the
  bundled runner, implement `simulate(run)` and concrete `MODEL_METADATA` as
  described in
  [references/data-and-provenance-contract.md](references/data-and-provenance-contract.md).
- Execute only agent-authored or reviewed, trusted model code. Importing a model
  runs Python in the current process; inspect imports and all top-level code
  before import. Reject target-program launches, target SDKs, inference calls,
  network requests, credential access, and undeclared external-data reads or
  writes, even when described as calibration. Keep the adapter computational;
  let the runner write the declared artifacts. The runner is not a security
  sandbox, and a declaration or static check is not proof of isolation.
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
- Verify that changing a declared input reaches the implemented mechanism and
  changes the expected output or intermediate state. Hashing a specification
  only establishes its identity; it does not establish that the model uses it.
  Use the review's `nextCheck` entries to test activation, fixed assumptions,
  interaction boundaries, and plausible omitted mechanisms. Distinguish
  conditional one-factor accounting from policy effects propagated downstream.
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
and emits starter DuckDB queries. Local numerical parallelism must preserve run
IDs, semantic seed keys, table grains, and failure records. It must not launch
the emulated system or distribute real target work.

The bundled runner is for bounded local work. Individual ceilings are 100,000
runs, 100 declared outcomes, and 10,000 observation, event, or diagnostic rows
of each kind per run, but one stricter joint ceiling permits at most 1,000,000
materialized rows across the plan, runs, outcomes, summaries, observations,
events, diagnostics, and variable inventory. Use an engine-native streaming or
partitioned Parquet adapter for larger jobs; do not raise the limit and
materialize an unsafe workload in memory.

## Analyze and challenge

- Encode each supported core contrast as `comparison - baseline`, classify every
  design point as primary or challenge, and use the declared paired, independent,
  or deterministic mode. Keep design points separate.
- For context-length degradation, summary fidelity, retry economics, or a
  quality-adjusted compaction break-even, read
  [references/context-quality-cost.md](references/context-quality-cost.md).
- Report effect size, interval, practical threshold, replication count, and
  Monte Carlo standard error where applicable. A small p-value is not a
  substitute for a useful effect or a stable result.
- Report expected behavior, predictive quantiles and threshold-exceedance risk
  when relevant. Separate those from Monte Carlo confidence intervals and from
  parameter/structural sensitivity; do not collapse them into one confidence
  score. Follow the uncertainty reference for the required reporting contract.
- Actively try to make each evaluated claim fail within plausible bounds:
  stress assumptions, alternate input distributions, inspect failed-run regions,
  test numerical settings, or compare a rival mechanism. Read
  [references/diagnostics-and-inference.md](references/diagnostics-and-inference.md).
- Revisit the frozen variable review after results. Write
  `analysis/model-review-followup.md` with evidence paths for checks actually
  performed, decision reversals, new blind spots, unresolved items, and remaining
  questions. Separate measured sensitivity from a priori impact judgments. A new
  variable, changed mechanism, or selected strategy needs a fresh declared study;
  do not retrofit the original plan or count exploratory discovery as confirmation.
- Use only `supports-under-model`, `challenges-under-model`,
  `inconclusive-under-model`, or `not-identifiable-from-design`. Never say that
  the simulation proved reality. State when external calibration or validation
  remains missing, without attempting real-system execution to resolve it.
- Do not hand-author inferential numbers or statuses. For declared hypotheses,
  generate the result from validated replication outcomes:

```text
python <skill-directory>/scripts/analyze_simulation_hypotheses.py --root <bundle>
```

The current `mean-difference-v3` analyzer supports model-conditional mean
differences, exact deterministic contrasts, and non-identifiability. Choose the
interval method before seeing outcomes. For known finite support, read
[references/bounded-mean-inference.md](references/bounded-mean-inference.md);
the template uses its conservative Hoeffding-Bonferroni method. Never infer
support bounds from sample extrema. Normal intervals remain available when
their approximation is justified; fewer than 30 replications or zero observed
contrast variance prevent an automated normal decision, but passing those
guards does not establish coverage. Keep authoritative numbers at full
round-trip precision and round only presentation. Read the result contract for
unsupported estimands and immutable legacy replay.

## Validate and deliver

Run the bundle integrity audit after analysis. It separately recomputes every
supported estimate, MCSE, interval, per-design-point decision, aggregate status, and
challenge result from the generated tables:

```text
python <skill-directory>/scripts/validate_simulation_bundle.py --root <bundle> --report <bundle>/validation-report.json
```

Do not deliver an incomplete bundle as successful. `--allow-incomplete` writes
an explicitly non-release diagnostic report with `ok=false` and still exits 2;
use it only while repairing the model. Read
[references/data-and-provenance-contract.md](references/data-and-provenance-contract.md)
before changing the core tables or moving high-volume data to Parquet.
`releaseEligible` certifies the computational bundle contract only. The separate
`modelReview` status checks declarations, not exhaustiveness, actual code
coverage, empirical validity, or the truth of the authored follow-up. Do not
use a passing integrity audit to erase a decision-critical evidence gap.

Hand off the question, model boundary, engine choice, run/failed counts, main
effect with uncertainty, strongest counterexample, unresolved assumptions,
validation result, and exact artifact paths. Distinguish a preregistered
`challenge` role from the result closest to the decision threshold; calculate
and label either claim correctly. Point the user to
`analysis/explore.sql`, `analysis/summary.csv`, and the data dictionary so
exploration can continue without reverse-engineering the model.
Also deliver the variable inventory, readable preflight review, and post-run
follow-up: teach which additional factors could matter, why they were treated
that way, and which existing evidence or mathematical comparison would reduce
the most consequential uncertainty. State explicitly that unrecognized factors
can remain even after this review.
