# Simulation-only execution contract — 2026-09-04

## User requirement

The skill must build a mathematical representation of the system, model its
relevant variability and disturbances, execute only the mathematical simulation,
and explain expected behavior and the uncertainty around it. It must not run
the target program, agent, service, model, hardware, or workflow.

## Implemented boundary

- Discovery text, the entrypoint, UI metadata, and the model template now say
  explicitly that this is mathematical simulation only.
- Real Pi/Copilot sessions, local or remote LLM inference, target SDKs, real tool
  calls, live probes, benchmarks, hardware connections, and target execution for
  calibration are outside the skill.
- Existing datasets, logs, source files, published results, and read-only
  documentation can inform parameters. Missing values remain assumptions,
  sensitivity ranges, or non-identifiable quantities.
- Pilot and confirmation runs are runs of the simulator. An external-validation
  requirement records an evidence gap; it does not authorize launching,
  delegating, or scheduling a real run, including an automatic follow-up.
- Mathematical simulation engines and local analysis helpers remain allowed.
  Supplied models must exclude live connectors and target callbacks. If an
  offline mathematical representation is not possible, report that limitation.
- The experiment template preserves this boundary and an uncertainty contract
  in namespaced extension metadata. These declarations guide the workflow; they
  are not a security sandbox or a claim of operating-system isolation.

The runner itself still executes reviewed Python model code. It is not safe for
arbitrary untrusted adapters. The revised contract explicitly requires source
review before import, rejects target execution even when labeled calibration,
and explains that provenance checks cannot prove an adapter has no side effects.

## Behavior and uncertainty contract

The new self-contained `references/uncertainty-and-behavior.md` describes:

1. State, policy, disturbances, parameters, mechanisms, units, and time horizon.
2. Mechanism-specific variability: burst demand, positive/skewed work sizes,
   cache expiry, persistent failures, common shocks, drift, queues, and
   critical-information loss. None is inserted without relevance and a declared
   assumption or existing evidence.
3. Separate predictive variability, finite Monte Carlo estimation error,
   parameter uncertainty, and structural/numerical uncertainty.
4. Expected values, relevant predictive quantiles, threshold-exceedance risk,
   appropriate estimation intervals, sensitivity reversals, and missing evidence.
5. A distinction between a predictive interval and an interval for a mean or
   probability. More repetitions do not validate the model or its assumptions.
6. Whole-horizon risk: monthly percentiles cannot be obtained by multiplying a
   per-task percentile, particularly with shared shocks and dependent cache or
   workload state.

The mean-contrast analyzer is not relabeled as a universal uncertainty engine.
Unsupported quantiles, tail risks, and ratio estimands require a separate,
appropriate local analysis and independently validated extension artifacts.

## Validation

The new three-test mathematical-template suite evaluates observable behavior:

- Loads the actual model template and evaluates 64 seeds twice under Python
  audit detection of process launches, network operations, and selected inference
  client imports. It verifies repeatability, nonconstant stochastic output, and
  bounds without observing a forbidden capability.
- Checks a deterministic zero-noise limit and an exact stock-policy effect.
- Sends synthetic audit records directly to verify that the test fails on
  process, socket, and inference-import sentinels. No subprocess, socket, or
  inference client is created by these negative controls.

This is a check of the shipped template and its observer. It is not a proof that
an arbitrary future Python adapter cannot bypass audit coverage, and not a real
agent forward test. No target executable or inference API was used.

Commands:

```text
python -B skills/simulation-data-lab/scripts/test_simulation_only_boundary.py
python -B skills/simulation-data-lab/scripts/test_run_simulation_experiment.py
python -B skills/simulation-data-lab/scripts/test_analyze_simulation_hypotheses.py
python -B skills/simulation-data-lab/scripts/test_validate_simulation_bundle.py
uv run --script scripts/validate-pattern-ids.py
uv run --script scripts/validate-skills.py
uv run --script scripts/test-skill-independence.py
uv run --script scripts/check-repo-payload.py
uv run --script scripts/sync-local-skills.py --source skills/simulation-data-lab --destination .agents/skills/simulation-data-lab
uv run --script scripts/sync-local-skills.py --source skills/simulation-data-lab --destination .agents/skills/simulation-data-lab --check
```

All 51 tests pass: 3 simulation-boundary, 20 runner, 16 analyzer, and 12 validator.
A fresh template plan/run/analyze/validate bundle is retained at
`evaluations/runs/simulation-only-template-20260904`, with 128 planned and valid
simulations and no failed or invalid runs. Its output remains mathematical,
synthetic, and hypothesis-inconclusive where the existing inference guards
require it. Repository validation, payload, quick validation, compilation, and
targeted local synchronization are checked before handoff.

Keep `simulation-data-lab` at `validating` under the repository promotion policy.
Do not trigger its real-agent validation gate: the user expressly excludes such
execution. This administrative status is separate from the passing local
mathematical and contract tests.
