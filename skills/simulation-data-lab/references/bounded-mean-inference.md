# Bounded mean contrasts

Use this route for independent replication-level outcomes whose entire support
is known before looking at the simulated sample: proportions, bounded scores,
or costs with a genuine modeled hard cap. It is useful when skew or rare shocks
make a normal approximation doubtful. The intervals can be much wider than
normal intervals; that is a precision cost, not evidence that the simulator is
wrong. For an unbounded cost, a quantile, a ratio, dependent replications, or a
sequential stopping rule, use a different justified method and an audited
extension. Never invent a cost cap or truncate unfavorable rows to qualify.

## Freeze support, not sample extrema

Select `analysis.intervalMethod=bounded-hoeffding-bonferroni` and add:

```json
"outcomeBounds": {
  "baseline": {"low": 0, "high": 1},
  "comparison": {"low": 0, "high": 1},
  "assumptionId": "a-outcome-support"
}
```

Add that ID to the hypothesis's `assumptionIds` and the experiment's assumptions.
Explain why the bounds hold for every possible draw at every classified design
point, in the outcome's declared unit. Use a separate hypothesis or a defensible
common envelope if supports change across the grid. Equal low/high bounds mean
a mathematically fixed arm, not a constant observed sample. Bounds are required
only for this method; other methods reject the field instead of ignoring it.

The planner checks finite, ordered, representable bounds and their assumption
link. Both analyzer and validator reject observations outside them. These
checks can falsify a bound but cannot prove it holds in unseen outcomes. Verify
it from the model mechanism; a hash, an assumption label, or observed min/max
does not constitute that proof.

## Interval and dependence contract

Let `A` be baseline, `B` comparison, `wA = upperA-lowerA`,
`wB = upperB-lowerB`, and `delta = mean(B)-mean(A)`. Freeze the family of `m`
primary plus challenge points and family level `1-alpha`. Under independent
replications, inversion of the two-sided Hoeffding bound gives:

```text
L = log(2*m/alpha)
paired:       radius = (wA+wB) * sqrt(L/(2*n))
independent:  radius = sqrt((wA^2/nA + wB^2/nB) * L/2)
interval = [delta-radius, delta+radius]
           intersect [lowerB-upperA, upperB-lowerA]
```

Paired means arbitrary within-pair dependence is allowed, but whole pairs must
be independent across replications. Independent means all arm observations are
independent. Using the independent formula on dependent pairs can understate
uncertainty. The paired formula deliberately uses a worst-case difference
range, not the observed covariance or an assumed positive benefit of coupling.
It may be conservative even when common random numbers are effective.

The weighted-sum formulas above are an application of
[Hoeffding's bounded-sum inequality](https://doi.org/10.1080/01621459.1963.10500830).
Bonferroni allocates `alpha/m` per point, without requiring independence between
design points. This is a finite-sample coverage statement conditional on the
support and sampling assumptions, not a claim about real-world validity. No
study-wide or optional-stopping coverage is supplied. Exported intervals record
the adjusted marginal level, `1-alpha/m`, and a `hoeffding-*-bonferroni-v3`
method. Numerically unrepresentable levels fail instead of claiming 100% coverage.

Empirical MCSE is still reported for the mean contrast, but it does not determine
this interval's width. Zero observed variance does not collapse a nonconstant
support. Normal-only small-sample and zero-variance guards do not apply to this
method: uncertainty is instead controlled by the declared range and fixed
sample size. A support that fixes both arms can identify an exact contrast.

For a desired untrimmed half-width `epsilon`, equal arm counts need at least
`ceil((wA+wB)^2 * L/(2*epsilon^2))` paired replications, or
`ceil((wA^2+wB^2) * L/(2*epsilon^2))` independent observations per arm. Choose the
budget before inspecting results and respect the runner's materialization
ceiling. If it is too large, report insufficient precision or justify a sharper
method; do not keep sampling with fixed-count intervals until a claim passes.

For a single Bernoulli probability, an exact binomial interval can be sharper.
It is a different estimand from a paired mean difference; do not substitute
unrelated marginal intervals. See
[NIST's small-failure interval guidance](https://www.itl.nist.gov/div898/handbook/prc/section2/prc241.htm).

## Verification and interpretation

Test formulas against hand-computable ranges, arm exchange, constant arms,
small samples, zero events, and out-of-support outcomes. Enumerate finite
distributions to audit coverage where feasible. Preserve independent validator
recomputation, and test that narrowing or relabeling a report is rejected.

Use full binary64 round-trip precision for authoritative v3 numbers and
threshold comparisons. Round only the presentation. A value just below a
threshold must not become support because both display as `1.00`. Full
precision prevents that formatting defect; it does not bound floating-point
solver error. Near a numerically uncertain boundary, run a higher-precision or
convergence check and report the decision unresolved when warranted. Any
practical tolerance belongs in the frozen threshold, not a post-hoc epsilon.
