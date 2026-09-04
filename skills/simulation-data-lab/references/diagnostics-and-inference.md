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
