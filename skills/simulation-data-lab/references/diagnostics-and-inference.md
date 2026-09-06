# Diagnostics and inference

Separate three questions:

1. **Verification:** was the intended model implemented and solved correctly?
2. **Validation:** is the model adequate for the target use and domain?
3. **Inference:** what does the generated experiment imply conditional on the
   verified model and declared assumptions?

More replications reduce Monte Carlo error; they do not repair a wrong mechanism,
poor calibration, or missing causal variable.

## Verification gates

Apply checks proportional to the claim and risk:

- fixed-seed repeatability and stable schema;
- hand-computable and degenerate cases;
- non-negativity, bounds, conservation, accounting identities, and impossible
  state rejection;
- positive and negative controls;
- metamorphic relations whose expected direction follows from the model;
- solver success, residuals, and time-step/tolerance convergence;
- horizon and warm-up sensitivity;
- alternate activation orders for ABM when scheduling matters;
- queue censoring and unfinished-entity accounting for DES;
- a reduced analytical solution or second implementation for high-impact
  conclusions.

Make accounting diagnostics capable of failing. Derive compared counts through
independent paths, such as accepted arrivals, generated services, recorded waits,
and completed entities; comparing a count with an alias or direct copy of itself
is a tautology, not a verification gate.

A failed numerical or structural diagnostic makes the affected inference
invalid. It is not evidence against the substantive hypothesis.

Check parameter activation, not just parameter serialization: perturb each
material declared factor and compare a mechanism-specific intermediate or
expected output. An unchanged value may be a valid saturation regime; justify
it with an oracle or try an active regime. A hash-bound but ignored setting is
a contract defect. Keep numerical verification, empirical calibration, and
structural challenge coverage as separate evidence. Millions of recomputed
cells can verify arithmetic without testing a single alternative mechanism.

## Monte Carlo precision

For an IID replication-level mean, estimate
`MCSE = sample_standard_deviation / sqrt(replications)`. Use a method appropriate
to the estimand for probabilities, ratios, quantiles, autocorrelated chains,
weighted rare-event samples, or clustered outcomes. Report both sampling/model
variation and finite-run Monte Carlo error when they are distinct.

Check convergence by cumulative batches or independent repetitions of the
experiment design. A fixed seed proves repeatability, not statistical stability.
If the interval or decision changes materially under a larger budget, report the
result as inconclusive.

For zero observed Bernoulli events in `n` independent trials, the exact one-sided
upper limit at confidence `1-alpha` is `1-alpha**(1/n)`, not zero. At 32 trials
and 95% confidence it is approximately 8.94%. Paired differences need a paired
method; do not combine unrelated marginal bounds as a paired interval. The
generic normal analyzer cannot replace an exact/binomial, clustered, weighted,
or tail-aware method. It records an empirical zero MCSE but marks stochastic
zero-variance decisions inconclusive, including constant paired differences.
A constant sample alone does not prove a constant population contrast.

The v2/v3 normal analyzer also leaves samples below 30 replications inconclusive.
This is a conservative automation rule, not a theorem that 30 observations
ensure valid coverage. Inspect skew, tails, effective sample size, and event
counts. An exact contrast oracle can be evaluated in a separate deterministic
adapter without relabeling a stochastic model as deterministic.

The template uses bounded Hoeffding-Bonferroni intervals; read
[bounded-mean-inference.md](bounded-mean-inference.md) before adapting its support
assumptions. This provides a conservative finite-sample alternative for bounded
means, including skewed or rare-shock outcomes, rather than relying on sample
size and nonzero variance as evidence of normal adequacy. Normal-Wald remains
an opt-in approximation, not an automatic fallback when bounds are unavailable.

The simultaneous methods use Bonferroni because looking for any reversal across
many points is a multiple-comparison claim. For `m` declared points and family
level `1-alpha`, each interval uses `1-alpha/m`. Dependence between points does
not invalidate the union bound, but invalid marginal intervals do. Pointwise
95% intervals can have only `0.95**20 = 35.85%` simultaneous coverage for 20
independent exact-normal intervals. Do not call a grid-wide decision “95%
confident” when it was based on pointwise intervals. A predeclared all-points
support test has different intersection-union logic; the correction here is
chosen to cover displayed intervals and the search for any contradiction.

When common random numbers are declared, compute within-`coupling_id` contrasts
and estimate uncertainty over paired differences. Do not analyze the same rows
as independent. If scenario code consumes streams differently and named
substreams were not used, abandon the paired claim and rerun with a valid design.

## Decision language

Use these statuses:

- `supports-under-model`: the preregistered criterion is met across its required
  design range and challenge checks did not expose a reversal;
- `challenges-under-model`: the preregistered contradiction criterion is met or
  a valid stress point reverses the claim;
- `inconclusive-under-model`: precision or robustness is insufficient, or the
  interval spans decision regions;
- `not-identifiable-from-design`: the executed design cannot estimate the
  declared contrast.

Do not equate absence of support with challenge. Do not equate statistical
significance with practical importance. State the effect, unit, interval method
and level, practical threshold, replication count, MCSE, failed-run rate, and
assumptions. A confirmatory claim cannot be rescued by changing its outcome,
threshold, or decision rule after viewing results; record the change and treat
it as a new exploratory study.

## Challenge the hypothesis

Every evaluated claim needs at least one credible attempt to make it fail:

- sweep the edge of plausible parameter ranges;
- use alternative distribution shapes, tails, or dependence structures;
- remove or relax one assumption at a time;
- compare a rival mechanism that can explain the same outcome;
- hold out a regime not used for calibration;
- test alternate numerical resolution, horizon, or warm-up;
- inspect whether failed runs cluster where the result would be unfavorable;
- search for the threshold at which the effect changes sign or no longer clears
  practical importance.

Report the strongest counterexample even when the headline claim remains
supported. Keep the range searched and budget visible so “no reversal found” is
not mistaken for “no reversal exists.”

For a policy recommendation, include at least one rival mechanism when structure
is uncertain, not merely different coefficients inside the same equation. Record
each selected challenge with its mechanism, case ID, tested values, result
artifact, and `tested`, `deferred`, or `not-applicable` status with a reason.
If a decision-critical challenge is deferred, label robustness to it unresolved.
Code coverage and parameter-grid size do not substitute for this inventory.

Keep role and result language separate. A preregistered `challenge` point is the
place where refutation was attempted. The point closest to a practical threshold
is determined from the correctly oriented interval margin and can be a different
point. Do not call one the other without calculating it.

## Sensitivity analysis

Match the method to the inputs and output behavior:

- Morris for economical screening with many inputs;
- Sobol indices for variance decomposition with a compatible sample design and
  usually independent inputs;
- PAWN, delta, regional, or other moment-independent methods for discontinuous
  or non-monotonic responses;
- dependence-aware or Shapley methods when inputs are correlated;
- importance sampling or subset methods for rare events;
- surrogate models only with explicit prediction error and held-out validation.

Record sample design, total evaluations, distributions, dependence, transform,
seed/scrambling, outcome window, index definition, uncertainty interval, and
stability check. SALib's
[documented workflow](https://salib.readthedocs.io/en/stable/user_guide/basics.html)
is sample, evaluate, then analyze with a matching method. OpenTURNS provides
[broader reliability and dependence-aware methods](https://openturns.github.io/openturns/latest/theory/reliability_sensitivity/reliability_sensitivity.html).

## External validation

When observed data exist, compare model outputs with quantities not used solely
to tune the model. Preserve calibration and validation provenance. Check more
than one aggregate: distributions, temporal patterns, cross-variable relations,
and behavior under interventions when available. A good fit to one target does
not identify the mechanism.

Use existing observations only. Do not execute the actual system, launch a real
agent, make inference/tool calls, or run a live benchmark to create this evidence.
When evidence is absent, report the missing calibration or validation and keep
the conclusion conditional. Neither a failed validation gate nor a desired
confidence level authorizes a live run.

For medical, safety, financial, legal, infrastructure, or policy decisions,
simulation evidence should complement domain review, empirical data, and
appropriate validation. Keep the conclusion explicitly conditional and surface
the consequences of model misspecification.

## Final audit

Before delivery, require:

1. exact planned run coverage or an explicit incomplete status;
2. no NaN/infinity, broken primary/foreign keys, unit drift, or duplicate
   run/outcome rows;
3. failed and invalid runs retained and analyzed;
4. summaries independently recomputed from valid outcomes;
5. model, spec, plan, and output hashes consistent;
6. each hypothesis tied to its preregistered estimand and decision rule;
7. intervals and MCSE appropriate to independent or paired design;
8. limitations and challenge-search results present;
9. `source_type=simulated` visible in generated measurements;
10. exploration queries and a data dictionary that let another analyst begin
    without reading model internals.

Method references: [Morris, White, and Crowther on simulation study design and
Monte Carlo error](https://pmc.ncbi.nlm.nih.gov/articles/PMC6492164/),
[NIST exact binomial limits](https://itl.nist.gov/div898/software/dataplot/refman2/auxillar/exacbino.htm),
and [NIST simultaneous Bonferroni intervals](https://www.itl.nist.gov/div898/handbook/prc/section4/prc463.htm).
