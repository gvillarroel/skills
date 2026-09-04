# Pi context-rot cost-quality sensitivity method

## Preregistered question

This study asks when a long Pi session that grows toward 800,000 input tokens is
preferable to a session that compacts earlier, after accounting for provider
token value, possible long-context degradation, possible summary loss, and
bounded retries. It is an offline simulation. It does not execute Pi, GitHub
Copilot, GPT-5.6, or any model API.

The study deliberately separates four claims that are often conflated:

1. the deterministic provider cost of a declared request ledger;
2. empirical observations from historical long-context benchmarks;
3. hypothetical equations that transfer context and summary assumptions to a Pi
   session; and
4. Monte Carlo agreement with exact retry economics.

Only the first and fourth layers can be verified internally. The quality layer
remains conditional on its assumptions. Historical GPT-4.1, GPT-4-1106, Gemini
1.5, GPT-3.5, Llama, MPT, and LongChat results are not GPT-5.6 calibration.

The machine-readable preregistration is
`pi-context-rot-spec-20260904.json`; the evidence inventory is
`context-rot-evidence-20260904.csv`.

## Fixed session and strategies

One assigned task is a hypothetical 39-call Pi session. Without compaction,
main-request input grows from 40,000 to 800,000 tokens in 20,000-token steps:

```text
L_i = 40000 + 20000 * (i - 1), i = 1,...,39.
```

Each main call emits 1,000 output tokens in the source cost study. The primary
compaction policy caps active main-request input at 200,000 tokens. Its active
trajectory repeats 40K, 60K, ..., 200K four times and ends at 40K, 60K, 80K.
Compaction occurs after logical calls 9, 18, 27, and 36. Each compaction emits a
20,000-token summary and the following main request cold-writes the rebuilt
context.

Five strategy IDs are frozen:

- `grow_to_800k`;
- `cap_200k_uncached`;
- `cap_200k_cache_read`;
- `cap_200k_cache_write`; and
- `cap_pricing_threshold_uncached`.

The last four are compared with `grow_to_800k`. The primary comparison is
`cap_200k_uncached` versus `grow_to_800k`; the other three test compaction cache
accounting and model-specific pricing-cap alternatives.

The 800K trajectory is conditional. Pi's catalog exposes a 1,050,000-token
window, while GitHub's public one-million-token guarantee names supported
Copilot clients and does not establish third-party Pi availability.

## Deterministic provider-cost layer

The simulator imports scenario totals and call trajectories from the separately
validated `pi-cost-elasticity` bundle. It does not reconstruct a different rate
card for quality analysis. In that source study, input buckets are mutually
exclusive, request tier selection uses total request input, and all categories
switch to the long rate only when request input is strictly greater than the
model-specific GitHub Copilot threshold. Fixed-model Pi receives no automatic
model-selection discount.

The hand oracles for one complete attempt of the primary strategies are:

| Cost model | Grow to 800K | Cap 200K, uncached compaction |
| --- | ---: | ---: |
| Luna | $1.0204 | $0.5952 |
| Terra | $9.904 | $5.952 |
| Sol | $19.598 | $11.428 |

These values are provider token value before included AI Credits, subscription
allocation, and overage state. They are not necessarily incremental cash.

## Hypothetical task mix

The quality model has three strata, calculated separately before aggregation:

| Stratum | Weight | Short-context success probability |
| --- | ---: | ---: |
| Easy | 0.25 | 0.95 |
| Typical | 0.50 | 0.80 |
| Hard | 0.25 | 0.55 |

The weighted baseline is 0.775, but the retry transform is never applied only to
that average. Nonlinearity requires calculating success, completion, expected
attempts, and cost within each stratum and then applying the weights.

These weights and probabilities are assumed. The outputs must expose all three
strata so an analyst can replace the mixture rather than accepting a hidden
population model.

## Context exposure

For strategy `a` and onset `o`, active-context exposure is the mean excess
token-call area measured in fixed 100,000-token units:

```text
E(a,o) = sum_i max(L_ai - o, 0) / (39 * 100000).
```

`L_ai` is the active prompt at main call `i` after any compaction. Discarded
logical history is not counted as active context. The fixed denominator is
important: a given `beta` keeps the same log-odds-per-100K meaning across onset
values and is compatible with the historical two-anchor proxy derivations.

At the primary onset of 200,000 tokens, grow exposure is exactly `31/13`, or
2.3846153846153846, and cap-200K exposure is zero. An onset-normalized exposure
would answer a different question and is not substituted after viewing results.

## Summary fidelity and evidence position

Let `f` be the assumed fraction of task-relevant evidence retained by one
compaction. It is not the ratio of summary tokens to discarded tokens. Evidence
introduced at call `i` crosses each later compaction whose logical position `j`
satisfies `j >= i`. Define:

```text
c_i = count(j in compaction_positions where j >= i)
F = sum_i v_i * f^c_i / sum_i v_i.
```

The call weights are frozen as:

```text
uniform:      v_i = 1
front_loaded: v_i = 40 - i
back_loaded:  v_i = i
```

An uncompacted strategy has `F=1`. With four cap-200K compactions, `f=0.95`,
and uniform weights, `F=0.890241826923077`. The multiplicative-loss rule and
the position profiles are stylized assumptions; they are sensitivity axes, not
measurements of Pi summaries.

## Single-attempt quality equation

For task stratum `s`:

```text
p_as = logistic(logit(p0_s) - beta * E(a,o) + ln(F_a)).
```

`beta` is a nonnegative log-odds decline per mean excess 100K-token-call unit.
The equation keeps probabilities within zero and one, separates context exposure
from summary fidelity, and is simple enough to audit. It does not assert that
real model quality is logistic, monotone, or homogeneous across tasks.

The primary parameter set is
`primary-onset-200k-half-odds-f095-k3-uniform`:

- onset: 200,000 tokens;
- `beta = ln(2) * 13 / 31 = 0.2906746241057835`;
- per-compaction fidelity: 0.95;
- at most three attempts; and
- uniform evidence-position weights.

Because grow exposure is `31/13`, its context term multiplies baseline odds by
exactly 0.5. This is an interpretable hypothetical reference, not a fitted
GPT-5.6 effect.

## Sensitivity and historical-proxy design

The generic grid is the complete Cartesian product of:

- onset: 16K, 32K, 113K, 200K, 400K, and 600K;
- beta: 0, 0.25, 0.5, 1, and 2;
- per-compaction fidelity: 1, 0.99, 0.97, 0.95, 0.90, and 0.80;
- maximum attempts: 1 and 3; and
- evidence position: uniform, front-loaded, and back-loaded.

This produces 1,080 generic parameter sets. Each has design role `sensitivity`
and scope `hypothetical-not-empirical-calibration`.

Three historical slopes are added as challenge profiles. For compatible
two-anchor probabilities, the derived slope is:

```text
beta = [logit(p_low) - logit(p_high)]
       / [(context_high - context_low) / 100000].
```

The profiles are:

| Proxy ID | Low anchor | High anchor | Derived beta |
| --- | --- | --- | ---: |
| `chroma-context-rot-proxy` | 267/306 at mean 268.617647 tokens | 191/306 at mean 112672.843137 tokens | 1.260046681 |
| `ruler-gpt-4-1106-proxy` | 0.966 at 4K | 0.812 at 128K | 1.519149139 |
| `nolima-gpt-4-1-proxy` | 0.956 at 1K | 0.647 at 128K | 1.947000033 |

Each proxy is crossed with all 36 fidelity/retry/position combinations, adding
108 historical-proxy challenge points. Together with the one primary point, the
study has 1,189 parameter sets. The Chroma condition also changes retrieval and
distractor burden, and all three profiles use historical models and non-agent
tasks. They deliberately stress the simulator; they do not estimate GPT-5.6.

## Exact retry economics

Attempts are independent and identically distributed conditional on stratum and
strategy. A retry repeats the full session trajectory and pays the same
deterministic one-attempt provider cost. For single-attempt success `p` and cap
`K`:

```text
P(complete) = 1 - (1 - p)^K
E[attempts] = sum_(j=0)^(K-1) (1 - p)^j
assigned provider cost = attempt cost * E[attempts].
```

Aggregate completion and assigned cost are weighted sums over strata. Provider
cost per successful session is aggregate assigned cost divided by aggregate
completion probability. This cohort ratio allocates spend from exhausted
failures to successful work; it is not the cost conditional only on a lucky
first-attempt success.

Retry independence is likely optimistic when a missing fact, corrupted summary,
or persistent prompt flaw causes repeated failure. Perfect correlation and
changed retry prompts/cache states are required external challenge cases, not
silently folded into the primary result.

## Contrasts, scale, and break-even

For every model, parameter set, and compact strategy, report comparison minus
grow for completion probability, expected attempts, and cost per successful
session. Report provider savings as grow minus comparison. Label the result as
comparison dominance, baseline dominance, or a cost-quality tradeoff without
turning the label into an empirical recommendation.

For 1,000 and 1,000,000 assigned sessions, calculate expected completions,
unresolved sessions, and provider spend by exact multiplication. Do not
materialize one million synthetic session rows.

If a compact strategy saves provider value but reduces completion, define:

```text
completion loss = max(P_grow - P_compact, 0)
break-even loss per incremental unresolved session
  = provider savings per assigned session / completion loss.
```

Compaction is cheaper after monetizing failure only when the value assigned to
one additional unresolved session is below that threshold. If savings or quality
move in another direction, report the corresponding dominance or
willingness-to-pay status rather than forcing a finite threshold. Human rework,
latency, and implementation cost are zero in this narrow break-even unless an
analyst supplies them as an explicit extension.

The study also solves primary decision frontiers for each cost model and the
uncached and cache-read 200K caps. With onset 200K, uniform position weights,
and three attempts, monotone bisection over fidelity `[0,1]` finds (a) the
minimum fidelity at the primary beta for which compact cost per successful
session does not exceed grow and (b) the minimum fidelity that meets the 95%
completion SLO. A second bisection over beta `[0,10]`, holding fidelity at 0.95,
finds the minimum degradation rate at which compact cost per successful session
does not exceed grow. The tolerance is `1e-12` with at most 100 iterations.
Each result is labeled `identified_by_bisection`,
`already_satisfied_at_lower_bound`, or `not_reached_within_bounds`; an absent
crossing is not replaced by extrapolation. These rows are written to
`fidelity-boundaries.csv`.

## Monte Carlo validation

Analytic expectations are authoritative. A fixed-seed Monte Carlo sentinel
validates the implementation for six primary-case pairs:

- Luna, Terra, and Sol for cap-200K uncached versus grow;
- Luna for cap-200K cache-read versus grow; and
- Terra and Sol for pricing-threshold cap versus grow.

Each sentinel draws 200,000 assigned tasks with Python
`random.Random` MT19937 and seed 20260904. The strategies share the task-stratum
uniform and every attempt uniform, preserving a valid paired comparison. Raw
task rows are not retained.

Completion-difference uncertainty uses the paired sample standard error.
Cost-per-success-difference uncertainty uses a paired delta-method influence
function for the two cost/success ratios. The fixed normal 95% multiplier is
1.959963984540054. Both analytic deltas must lie within their corresponding
Monte Carlo intervals. These intervals measure finite simulation error only;
they do not cover parameter, transfer, or empirical uncertainty.

## Evidence inventory and threshold derivation

The evidence CSV preserves study, model, task, metric, context, score, sample
size, provenance class, numeric precision, source location, uncertainty, and
limitations. `source-reported` and `independently-derived` are never merged.
Approximate values and inequalities remain visible but cannot become exact curve
points.

Eligible retention anchors must contain finite positive context and a proportion
score. The normal route is `source-reported` with precision `exact` or
`rounded`. One preregistered exception admits the exact independently derived
proportions in `chroma-gpt41-longmemeval-reanalysis`, because both underlying
row-level files are frozen by commit and SHA-256. This exception does not admit
derived counts, p-values, approximate values, inequalities, tokenless controls,
or other unapproved derived series. Within each series, retention is score
divided by the earliest eligible anchor. For targets 95%, 90%, 85%, 80%, 70%,
and 50%, the first adjacent downward crossing is interpolated linearly in
retention on `log2(context_tokens)`. An unbracketed target is
`unidentifiable`. Extrapolation is forbidden.

Important evidence boundaries include:

- NoLiMa's official GPT-4.1 row reports 95.6% at 1K and 64.7% at 128K. Scores
  are rounded; 64K and 128K use 11 placements rather than 26.
- RULER reports means over 13 synthetic tasks with 500 examples per task. Its
  GPT-4-1106 row goes from 96.6% at 4K to 81.2% at 128K, while Gemini 1.5 Pro
  goes from 96.7% to 94.4%. The aggregate hides task heterogeneity.
- The Chroma GPT-4.1 LongMemEval values in this project are independently
  recomputed from 306 paired prompts, not copied from a reported confidence
  interval. Focused input has 267/306 correct and mean 268.617647 tokens; full
  input has 191/306 correct and mean 112672.843137 tokens. Discordant counts are
  87 focused-only and 11 full-only. The focused-minus-full difference is
  24.836601 percentage points; a paired 100,000-resample bootstrap with seed
  20260904 gives a 95% percentile interval of 19.2810 to 30.3922 percentage
  points, and the two-sided exact McNemar p-value is approximately
  `8.065e-16`. The contrast changes retrieval burden as well as length.
- Lost in the Middle reports exact table controls and qualitative bounds, while
  its repository describes several displayed reproduction targets as
  approximately around the listed values. Tokenless controls, document-position
  sweeps, inequalities, and approximate targets are retained for interpretation
  but excluded from token-onset interpolation.

Most source tables provide point estimates without confidence intervals. Missing
source uncertainty must remain missing; simulator precision cannot replace it.

## Frozen Chroma provenance

The Chroma row-level reanalysis is bound to repository commit
`af80a08018f2b7257c0336d04bcd02f936088106`:

- focused evaluated CSV SHA-256:
  `03AB9D9798263CC9C02D87DA111B8715E1822C5A874F9CA29AFBB7710135D874`;
- full evaluated CSV SHA-256:
  `037FD6E862D173DCA9AD15793CCA15D9609840D200DD17A0C754903AE070FF80`.

Any changed source bytes require a new evidence version and reanalysis rather
than silently replacing these statistics.

## Execution and validation sequence

1. Validate the preregistration JSON and the evidence CSV schema.
2. Load only the passing deterministic cost bundle and verify its checksums and
   independent validation report.
3. Reconstruct the five 39-call active-context trajectories and compaction
   positions from the source call ledger.
4. Expand the 1,189 frozen parameter sets without random sampling.
5. Calculate exposure, evidence fidelity, stratum quality, exact retries,
   aggregate cost, all strategy contrasts, break-even values, the analytic
   fidelity/beta boundaries, and the two scale volumes.
6. Run only the six paired fixed-seed Monte Carlo sentinels and compare them with
   the analytic answers.
7. Normalize eligible empirical curves and derive only bracketed log2-context
   retention thresholds.
8. Write tidy CSV outputs, study metadata, a data dictionary, starter SQL,
   summary, manifest, and SHA-256 inventory.
9. Run an independent validator that does not import the simulator and that
   recomputes trajectories, exposure, fidelity, retry economics, scale,
   break-even, Monte Carlo gates, and evidence onsets.

Expected data surfaces are `trajectory-metrics.csv`,
`quality-stratum-results.csv.gz`, `quality-aggregate-results.csv.gz`,
`quality-contrast-results.csv.gz`, `break-even.csv.gz`, `scale-results.csv.gz`,
`fidelity-boundaries.csv`, `monte-carlo-summary.csv`, `evidence-curves.csv`, and
`evidence-onsets.csv`, plus study metadata and integrity files.

The five large `.csv.gz` outputs retain their full logical CSV rows. Write them
with compression level 9, `mtime=0`, and no embedded original filename. Record
stored and uncompressed hashes and byte counts plus the Python and zlib runtime
versions in the manifest. DuckDB must be able to read them directly.

## Interpretation boundary

The deterministic ledger can answer what the declared tokens are worth under
the frozen rate rules. The quality model can answer how recommendations change
under declared onset, slope, fidelity, task, and retry assumptions. The Monte
Carlo sentinel can verify the analytic implementation. None can establish real
Pi summary fidelity, GPT-5.6 long-context quality, cache behavior, or business
loss. A production recommendation requires target-model, target-harness,
target-task validation and an explicit value for failure, rework, and latency.
