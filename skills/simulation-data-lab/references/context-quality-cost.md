# Context-quality-cost simulations

Use this workflow when a longer context, retrieval policy, or compaction policy
changes both provider cost and the probability that a task completes correctly.
The result is a conditional decision model, not an empirical evaluation of a
model or harness.

Do not run the studied harness, its tools, a local LLM, or an inference API.
Generate token ledgers, cache events, failures, and quality outcomes from the
declared mathematical model. Use existing evidence for calibration; missing
target-task evidence remains a limitation rather than triggering a live pilot.

## Keep four layers separate

1. **Deterministic accounting** maps a declared request ledger to token cost.
2. **Empirical evidence** records what a named study actually observed, including
   model, task, context, metric, sample size, uncertainty, and limitations.
3. **Quality assumptions** transfer or replace those observations with an
   explicit operational mechanism for the target use case.
4. **Stochastic validation** checks the analytic quality and retry calculations;
   it does not turn assumptions into measurements.

Give each layer its own inputs and outputs. Never fit a curve to one model and
benchmark and describe it as calibration for an untested model, agent harness,
or production task. Label such a curve `historical-proxy`, keep a generic
sensitivity grid, and record missing target-task validation as a limitation on
operational use. Do not collect it through a live run in this workflow.

## Build an evidence table before a curve

Store one source-reported or independently derived statistic per row. At
minimum retain:

- a stable evidence and series ID;
- study, model, task, metric, context tokens, score, and units;
- sample size and its unit;
- `source-reported` versus `independently-derived` status;
- numeric precision such as `exact`, `rounded`, `approximate`, or `inequality`;
- a precise source location and URL;
- the derivation, reported uncertainty, limitations, and transfer scope.

Do not silently digitize a plot, convert an inequality into an equality, or mix
an independently recomputed statistic with a reported statistic. A mean context
length is not a controlled fixed context length. A focused-versus-full prompt
contrast can also change distractor and retrieval burden, so it is not a pure
token-length causal effect.

When a source-reported series contains context/score anchors, normalize scores
to a declared short-context reference before estimating a retention threshold.
An exact independently derived proportion may also be an anchor when its
row-level source is immutable and digest-pinned, its derivation is reproducible,
and the policy explicitly allows that series. Do not generalize this exception
to derived counts, p-values, approximate values, inequalities, or tokenless
statistics.
For a target retention `r*` bracketed by adjacent observations `(x0, r0)` and
`(x1, r1)`, log-context interpolation is:

```text
log2(x*) = log2(x0)
          + (r* - r0) / (r1 - r0) * (log2(x1) - log2(x0))
```

Use the first declared downward crossing when a curve is non-monotone. Report
`interpolated` only when the target is bracketed. Report `unidentifiable` when
it is not. Extrapolate only under an explicit, separately labeled rule; never
present extrapolation as an observed threshold.

## Define the operational quality mechanism

Represent task heterogeneity before averaging. A compact structure is a set of
strata `s`, each with weight `w_s` and short-context success probability
`p0_s`. Weights sum to one. Keep retrieval, tracking, aggregation, multi-hop,
generation, and agentic execution separate when evidence suggests different
length sensitivity.

For a session with `n` main calls, one transparent fixed-unit exposure is:

```text
E = sum_i max(L_i - onset, 0) / (n * 100000)
```

Here `L_i` is the effective active input context at call `i`, not the discarded
logical history; `onset` is an assumed context at which degradation begins. The
unit is 100,000 excess token-calls, so one `beta` remains comparable across the
onset grid. The unit is a declared modeling convention, not a scientific
constant. Replace this exposure only before seeing results and test an
onset-normalized or threshold alternative when it could reverse the decision.
An onset-scaled exposure requires its own parameterization and beta units;
never reuse or compare the same numeric beta across the two normalizations.

Treat compaction as a possible information-loss mechanism distinct from context
exposure. If one compaction retains a fraction `f` of task-relevant information
and `c_i` compactions affect the evidence needed at call `i`, define a weighted
session fidelity such as:

```text
F = sum_i v_i * f^c_i / sum_i v_i
```

Declare the call weights `v_i`. Uniform, early-critical, and late-critical
profiles are useful challenge cases. `f` is an assumption about retained
task-relevant information, not the token compression ratio. It must remain in
`[0, 1]`; `f=1` is the lossless boundary.

A bounded quality link that separates baseline difficulty, exposure, and
fidelity is:

```text
p_single_s = logistic(logit(p0_s) - beta * E + ln(F))
```

Use `0 < p0_s < 1`, `beta >= 0`, and `0 < F <= 1`. The link expresses a model
assumption: exposure reduces log-odds at rate `beta`, while compaction fidelity
applies an additional odds multiplier. It is not the only defensible mechanism.
Challenge it with a probability-scale decline, a threshold cliff, interactions
between difficulty and length, or task-specific `beta_s` when those alternatives
could reverse the decision.

Average exposure and average fidelity can hide a critical failure. If success
requires every one of `r` facts to survive `c` compactions, an independent
fact-survival alternative has retention `f^(r*c)`, not an average `F` used as an
odds multiplier. State the independence assumption and challenge it with shared
loss of related facts. A peak-context cliff or an all-required-steps mechanism
is likewise different from changing the slope of average exposure. Keep each
rival mechanism in a separate declared case. Define the `F=0` limit explicitly
as zero success for the displayed link; never evaluate `log(0)` or manufacture
a finite cost per completion when no completion is possible.

An empirical two-anchor hinge proxy may derive

```text
beta = (logit(p_low) - logit(p_high))
       / ((context_high - context_low) / 100000)
```

only when the operational exposure uses the compatible per-100,000-token
scale. Record both anchors and the derivation. This is a historical proxy, not
target-model calibration, unless the same target, task, prompts, and measurement
protocol were validated.

## Price each attempt independently of quality

Create a request-level ledger for every strategy. For each request, partition
input tokens into mutually exclusive uncached, cache-read, and cache-write
buckets, add output tokens, and select the pricing tier from total request input
using the provider's exact boundary rule. Compaction is an additional request;
record its input cache mode, summary output, rebuilt context, and next-request
cache state explicitly.

Compute one-attempt provider cost from the ledger before applying any quality
probability. Preserve model-specific thresholds, rates, and context-availability
caveats. Distinguish provider token value or credits from incremental cash after
plan allowances.

## Calculate retry economics exactly

For bounded retries, read [retry-economics.md](retry-economics.md) before
calculating completion or cost per success. It defines independent, conditional,
and persistent-failure mechanisms, task-stratum aggregation, zero-success
boundaries, and exact validation oracles. Changing an attempt cap alone does not
test dependent failure.

## Compare strategies and locate break-even points

For each strategy report at least:

- deterministic cost per attempt and the request/token mechanisms producing it;
- single-attempt success, capped completion probability, and expected attempts;
- expected provider spend per submitted task and per completed task;
- results by task stratum and the weighted aggregate;
- values at requested volumes by algebraic scaling, not row replication.

For strategies `A` and `B`, define the direction before analysis. A simple
quality-adjusted decision uses:

```text
total_expected_cost
  = expected_provider_spend
  + P_exhausted * failure_loss
  + expected_human_rework
  + expected_latency_cost
  + implementation_overhead
```

Solve the value of fidelity, degradation rate, failure loss, or retry cost where
`total_expected_cost_A = total_expected_cost_B`. Report all crossing intervals
for non-monotone results and `no crossing in searched range` when appropriate.
Do not infer a business loss value from token prices.

## Use Monte Carlo as a verification layer

When an exact expectation exists, calculate it first. Then simulate Bernoulli
attempt outcomes with a frozen seed and enough replications to verify completion
probabilities, expected attempts, and expected spend within a predeclared Monte
Carlo tolerance. Couple strategies with common uniforms only when their task and
attempt events have a valid correspondence, and analyze paired differences.

Keep design-point uncertainty outside stochastic replications. An onset/beta/
fidelity grid represents epistemic alternatives; its range is not a confidence
interval. Monte Carlo error shrinks with more replications, while transfer and
structural uncertainty do not.

## Required challenge cases

At minimum test:

- no degradation (`beta=0`) and lossless summaries (`f=1`);
- onset below the first call, near a pricing threshold, and beyond the final call;
- weak and severe degradation, including an abrupt-threshold alternative;
- uniform, early-critical, and late-critical information demand;
- easy, typical, and hard task mixtures rather than only an aggregate baseline;
- uncached, cache-read, and cache-write compaction inputs;
- retained versus cold post-compaction prefixes;
- one attempt versus bounded retries, correlated failure, and changed retry cost;
- source-series non-monotonicity, rounded anchors, missing uncertainty, and
  unidentifiable retention thresholds;
- loss values large enough to reverse a token-cost recommendation.

Record a challenge inventory with case IDs, mechanisms, ranges, evidence paths,
and `tested`, `deferred`, or `not-applicable` status. A coefficient grid does
not execute a correlated-retry or critical-fact-loss mechanism. State explicitly
when any required structural challenge remains unresolved; do not label the
entire study robust merely because its arithmetic validator passes.

Deliver the strongest reversal found. State that conclusions are conditional on
the cost ledger, quality link, parameter grid, task mix, retry semantics, and
context availability. Existing target-task evidence is required before describing
the selected policy as empirically better; do not execute that evaluation as
part of this skill or as an automatic follow-up.
