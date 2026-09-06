# Experiment design

Use an ADEMP+R structure: aim, data-generating mechanism, estimand, methods or
scenarios, performance outcomes, and replication/robustness/refutation. The
specification freezes what will be learned before repeated simulation makes
almost any small difference appear precise.

The executable object is a mathematical representation, never the target
program or service. A pilot, calibration, robustness run, or confirmation sample
in this workflow uses the simulator and existing evidence only. Treat
`externalValidationRequired=true` as an unresolved evidence condition, not an
instruction to collect new real-system data.

## Operationalize the claim

For each claim, define:

- a plain-language statement and whether its scope is `model-internal`,
  `conditional-real-world`, or `empirically-calibrated`;
- the scenarios being contrasted;
- one replication-level outcome and an exact estimand, such as a paired mean
  difference, risk ratio, failure probability, or quantile difference;
- a structured analysis method, baseline, comparison, pairing mode, and complete
  classification of design points as primary or challenge;
- a contrast-scale practical threshold, unit, and `ge` or `le` operator, not
  only a significance level;
- a narrative decision and falsification rule that explains, but never overrides,
  the machine-readable analysis contract;
- the assumption IDs on which it depends and whether external validation is
  still required.

If the request is underidentified, either state a bounded exploratory assumption
and test alternatives or declare `analysis.kind=not-identifiable` with the
missing mechanism or contrast. Do not hide a material choice inside code.

Before planning, verify that every hypothesis copied from the template retains
all required fields: `hypothesisId`, `claim`, `claimScope`, `assumptionIds`,
`externalValidationRequired`, `outcome`, `scenarioIds`, `estimand`, `analysis`,
`practicalThreshold`, `decisionRule`, and `falsificationRule`. A
`not-identifiable` analysis still needs the narrative decision and falsification
fields so the unanswered claim and missing evidence stay explicit.

## Separate experimental axes

Use the canonical unit:

```text
scenario x design_point x replication
```

- `scenario` represents an intervention, policy, counterfactual, or named world.
- `design_point` represents fixed, calibrated, or sampled parameter settings.
- `replication` represents stochastic variation at one scenario/design point.
- `run_id` is the independent execution identity.
- `coupling_id` identifies valid common-random-number pairing across scenarios.

Do not pool stochastic, epistemic, structural, and numerical uncertainty into
one unlabeled set of draws. With stochastic and parameter uncertainty, place
parameter points outside and replications inside. Evaluate variability at both
levels.

Separate accounting contrasts from intervention claims. A one-factor-at-a-time
contrast can price an extra tool result while holding everything else fixed;
it cannot establish the real policy effect if removing that tool changes
reasoning, correctness, retries, or later context. Declare the frozen downstream
mechanisms, then test their plausible response when selecting a policy. Use
factorial or joint sensitivity points for interactions. Fractions of an
arbitrary grid that favor a policy are coverage of that grid, not probabilities
that the policy is best; probability statements need justified joint weights.

Use `uncertaintyMode=deterministic` only when the model has no stochastic draw
and each scenario/design-point cell runs once. Use `stochastic` otherwise. A
deterministic result has no Monte Carlo interval, but it remains conditional on
parameter choices, model structure, and numerical correctness.

The bundled v1 planner accepts explicit design points. For Latin hypercube,
Sobol/QMC, Morris, posterior draws, or another generated design, materialize the
points with stable IDs before planning. Keep the design method, distributions,
dependence assumptions, scrambling seed, and generation code in provenance.

## Choose a design

| Goal | Useful design | Important condition |
| --- | --- | --- |
| Debugging and variance estimate | Small fixed pilot | Pilot results do not become confirmatory evidence silently |
| Compare a few policies | Factorial scenarios with independent or paired replications | Pair only semantically corresponding random mechanisms |
| Explore a modest parameter space | Stratified or Latin hypercube design | Preserve constraints and joint dependence |
| Screen many inputs | Morris | Treat it as screening, not a complete variance decomposition |
| Decompose variance | Sobol design and matching analyzer | Classical Sobol indices assume an appropriate design and usually independent inputs |
| Smooth integration with bounded budget | Scrambled Sobol QMC | Preserve balanced sample sizes, commonly powers of two |
| Rare failures | Importance sampling, splitting, subset simulation, or reliability methods | Report weights and effective sample size; crude Monte Carlo may see no events |
| Expensive model | Validated surrogate or emulator | Include emulator error and out-of-sample validation |

Never apply a sensitivity analyzer to an arbitrary sample matrix merely because
the column names match. The sampler and analyzer form one design contract.

## Define time and observation

For time-dependent models, state:

- initial conditions and initialization source;
- `experiment.timeUnit`, horizon, observation grid, and termination condition;
- warm-up rule and whether warm-up rows are retained and labeled;
- censoring rules for unfinished entities;
- solver method, tolerances, and event handling for continuous systems;
- activation order or scheduling semantics for agents;
- observation granularity needed by each estimand.

Test alternate horizons, warm-up lengths, time steps, or tolerances when they
can change the claim. A visually smooth trajectory is not evidence of numerical
convergence.

The bundled adapter passes a declared time unit to the model as
`run["time_unit"]`. It rejects non-empty observations or events when
`experiment.timeUnit` is absent and repeats the declaration in each generated
row's `time_unit` column so downstream analysts never have to infer whether
`sim_time=10` means seconds, days, or another unit.

## Manage seeds and parallelism

Use a root seed plus a stable semantic derivation keyed by experiment,
scenario when independent, design point, replication, and stream purpose. The
bundled planner does this without depending on scenario order or worker order.

Inside NumPy models, prefer an explicit `Generator` and derive named substreams
with `SeedSequence` or another documented scheme. NumPy documents
[parallel seed spawning](https://numpy.org/doc/stable/reference/random/parallel.html).
Record the bit generator and NumPy version because a seed alone does not promise
cross-version bitwise identity.

Common random numbers can reduce contrast variance, but identical top-level
seeds are insufficient when scenarios consume random values in different
orders. Give arrivals, service times, failures, behavior, and resampling their
own named streams. Analyze coupled runs as paired; never count the duplicate
seed as two independent random sources.

## Set a stopping rule and budget

Prefer a fixed run count chosen from a pilot variance estimate or a predeclared
precision target. Track interval width or MCSE by batches. If using a precision
stopping rule, declare the outcome, formula, target, minimum, maximum, and check
frequency in advance. Repeatedly simulating until a preferred conclusion appears
is not a valid rule.

Planning a stopping rule does not by itself make fixed-sample intervals valid
after optional stopping. The bundled analyzer assumes a fixed replication
count. Use a sequentially valid method or a fresh fixed-count confirmation
sample when stopping on observed precision or a decision. Reserve new random
seeds or an independent confirmation design after choosing a candidate from
exploratory results; document the selected candidate and frozen rule first.

Freeze the family of comparisons as well as the run count. For searching any
contradiction over a hypothesis's design points, use an appropriate simultaneous
method: `intervalLevel` covers that hypothesis's primary and challenge points.
For a priori finite support, use the template's `bounded-hoeffding-bonferroni`
route and read [bounded-mean-inference.md](bounded-mean-inference.md). Otherwise,
`normal-approximation-bonferroni` requires a justified marginal normal
approximation; correction alone does not supply one. Choose the method from the
mechanism and estimand, not from whichever interval yields a preferred decision.
Across multiple hypotheses or outcomes, declare a larger family and use an
appropriate external analyzer if a study-wide error guarantee is needed.

Estimate expanded run count, per-run time, memory, and projected output size
before a costly run. Use a bounded pilot and a hard maximum. Do not log every
event or agent by default; aggregate within each run when raw detail is not
needed to diagnose or estimate the claim.

## Validate the design before inference

Confirm that:

- every scenario/design-point combination has its planned replications;
- calibration, pilot, exploratory, robustness, and holdout cohorts remain
  distinguishable;
- retries reuse the same logical `run_id` and seed rather than becoming new
  replicates;
- new randomness receives a new replication ID;
- failed runs remain in the denominator and are investigated for parameter-
  dependent missingness;
- all outcome derivations use only post-warm-up observations when required;
- comparisons use the declared independent or paired unit.
- every design point is included as primary or as an explicit challenge in each
  executable v1 hypothesis; none can disappear after results are visible.
