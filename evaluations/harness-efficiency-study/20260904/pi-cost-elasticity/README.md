# Pi-through-Copilot cost elasticity — 2026-09-04

## Executive answer

This study made **zero real Pi, Copilot, or model API calls**. It is a
deterministic, offline accounting simulation: every hypothetical request is
split into mutually exclusive uncached-input, cache-read, cache-write, and
output buckets, then priced from the GitHub Copilot rate card captured on
2026-09-04.

The main result is that cost is substantially more elastic to prompt stability,
pricing-tier crossings, and sequential model roundtrips than to a small stable
prompt block in isolation:

- Adding 1,000 stable system-prompt tokens to a ten-call Luna session costs
  USD 0.00043 per session, USD 0.43 per 1,000 sessions, or USD 430 per one
  million sessions.
- Making those same 1,000 tokens uncached on all ten calls costs USD 2,000 per
  million Luna sessions, 4.65 times the stable-prefix increment.
- If the 1,000-token increase crosses Luna's 200,000-token pricing boundary,
  the finite jump is USD 4,630 per million warm calls or USD 50,975 per million
  cold cache-write calls. The whole request changes tier, not only the last
  1,000 tokens.
- A fifth sequential tool in the 50k fixture costs USD 1,813 per million Luna
  sessions. Putting the fifth tool in the existing parallel batch costs USD
  645, 64.42% less, because it avoids another model roundtrip and prefix replay.
- The same fifth sequential tool from an 800k prefix costs USD 33,566 per one
  million Luna sessions, 18.51 times the short-context fixture.
- In the fixed 39-call Luna session, proactive compaction at 200k costs USD
  0.5952 versus USD 1.0204 without compaction, even after four uncached summary
  calls, four cold prompt rebuilds, and 80k extra output tokens. The modeled
  saving is 41.67%, or USD 425.20 per 1,000 such sessions.

These are conditional accounting results, not observations of task quality,
latency, cache hit rate, or service availability. A cheaper token policy is
worth adopting only when its expected quality, rework, latency, and
implementation penalty stays below the reported token saving.

## Fixed pricing boundary

Prices are USD per one million tokens. A request exactly at the threshold is in
the short tier; a request one token above uses the long rates for the entire
request.

| Model | Copilot long tier starts above | Short input / read / write / output | Long input / read / write / output |
| --- | ---: | ---: | ---: |
| GPT-5.6 Luna | 200,000 | 0.20 / 0.02 / 0.25 / 1.20 | 0.40 / 0.04 / 0.50 / 1.80 |
| GPT-5.6 Terra | 272,000 | 2.00 / 0.20 / 2.50 / 12.00 | 4.00 / 0.40 / 5.00 / 18.00 |
| GPT-5.6 Sol | 272,000 | 4.00 / 0.40 / 5.00 / 20.00 | 8.00 / 0.80 / 10.00 / 30.00 |

The route is fixed-model Pi through GitHub Copilot. No automatic-model-selection
discount is assumed. Provider token value is also reported as GitHub AI Credits
at USD 0.01 per credit. It is not automatically the user's incremental cash
bill: unused plan allowance can absorb the charge, while consuming that
allowance still has opportunity cost.

The Pi catalog observed for Sol displayed an older, lower price surface than
GitHub's current billing table. This study deliberately uses GitHub's official
route pricing as the billing source of truth; using the displayed Pi Sol
estimate would materially understate the simulated cost.

## 1,000 extra system-prompt tokens

The stable-prefix formula for `R` requests is:

```text
delta = 1,000 / 1,000,000 * (cache_write_rate + (R - 1) * cache_read_rate)
```

The first call writes the extra block and later calls read it. The dynamic case
charges the extra block as uncached input on every call.

| Model | One cold call: 1k / 1m sessions | 10 stable calls: 1k / 1m | 50 stable calls: 1k / 1m | 10 uncached calls: 1k / 1m |
| --- | ---: | ---: | ---: | ---: |
| Luna | USD 0.25 / 250 | USD 0.43 / 430 | USD 1.23 / 1,230 | USD 2.00 / 2,000 |
| Terra | USD 2.50 / 2,500 | USD 4.30 / 4,300 | USD 12.30 / 12,300 | USD 20.00 / 20,000 |
| Sol | USD 5.00 / 5,000 | USD 8.60 / 8,600 | USD 24.60 / 24,600 | USD 40.00 / 40,000 |

The system-prompt and visible-tool-schema experiments are identical when both
are stable prefix tokens. Their semantic role does not alter billing. Their
position and stability do.

### Crossing the pricing threshold

The threshold fixture moves each model from 500 tokens below its Copilot limit
to 500 tokens above it, with 1,000 output tokens held fixed.

| Model | Warm baseline → comparison | Warm delta: 1k / 1m calls | Cold-write baseline → comparison | Cold delta: 1k / 1m calls |
| --- | ---: | ---: | ---: | ---: |
| Luna | 0.005190 → 0.009820 | USD 4.63 / 4,630 | 0.051075 → 0.102050 | USD 50.98 / 50,975 |
| Terra | 0.066300 → 0.127000 | USD 60.70 / 60,700 | 0.690750 → 1.380500 | USD 689.75 / 689,750 |
| Sol | 0.128600 → 0.248000 | USD 119.40 / 119,400 | 1.377500 → 2.755000 | USD 1,377.50 / 1,377,500 |

Near the boundary, a single constant “USD per additional token” is misleading.
The correct estimand is this finite tier-switch difference.

## Four versus five tools

The short fixture starts from a 50k prompt. Every tool uses 100 output tokens
for arguments and returns 2,000 tokens; results are retained and external tool
fees are zero. After four tools, the exact accumulated prompt replayed by the
extra sequential roundtrip is 58.4k tokens.

| Model | Fifth sequential tool: 1k / 1m sessions | Fifth tool in existing batch: 1k / 1m | Batch reduction | Fifth sequential tool from 800k: 1k / 1m |
| --- | ---: | ---: | ---: | ---: |
| Luna | USD 1.813 / 1,813 | USD 0.645 / 645 | 64.42% | USD 33.566 / 33,566 |
| Terra | USD 18.130 / 18,130 | USD 6.450 / 6,450 | 64.42% | USD 335.660 / 335,660 |
| Sol | USD 35.860 / 35,860 | USD 12.500 / 12,500 | 65.14% | USD 670.720 / 670,720 |

The important distinction is not only “five tools versus four.” It is whether
the fifth tool creates a serial `model → tool → model` cycle. Parallel tools in
one batch can increase argument and result volume without adding another full
prefix replay. Any external API fee for the tool must be added separately.

## Long session: retain 800k or compact proactively

The fixed logical workload has 39 main model calls. Without compaction, request
input grows from 40k through 800k in 20k increments. Each main call emits 1k
output tokens. The fixed-200k policy compacts before the next main call would
exceed 200k, emits a 20k summary, and rebuilds a 40k prompt. It performs four
compactions. The primary accounting treats every compaction request as fully
uncached and every rebuilt prompt as a cold cache write.

| Model | No compaction | Fixed cap 200k | Cap at model pricing boundary | Preferred token policy | Saving / session | Saving at 1k / 1m sessions |
| --- | ---: | ---: | ---: | --- | ---: | ---: |
| Luna | USD 1.0204 | USD 0.5952 | USD 0.5952 | 200k / model threshold | USD 0.4252 | USD 425.20 / 425,200 |
| Terra | USD 9.9040 | USD 5.9520 | USD 5.8420 | model threshold | USD 4.0620 | USD 4,062 / 4,062,000 |
| Sol | USD 19.5980 | USD 11.4280 | USD 11.2880 | model threshold | USD 8.3100 | USD 8,310 / 8,310,000 |

For Luna, 200k is the pricing boundary. For Terra and Sol, a universal 200k cap
compacts one extra time without avoiding any additional long-tier call. The
model-specific 272k policy is therefore cheaper in this fixture.

### What if compaction cache behavior differs?

The fixed-200k sensitivity changes only the input bucket used by the compaction
call, or the treatment of a retained 20k system prefix. All alternatives still
include the summary output and rebuilt context.

| Compaction accounting | Luna | Terra | Sol |
| --- | ---: | ---: | ---: |
| Compaction input is cache read | USD 0.4512 | USD 4.5120 | USD 8.5480 |
| Uncached input, retain 20k system prefix | USD 0.5768 | USD 5.7680 | USD 11.0600 |
| Uncached input, full cold rebuild — primary | USD 0.5952 | USD 5.9520 | USD 11.4280 |
| Compaction input is cache write | USD 0.6352 | USD 6.3520 | USD 12.2280 |
| No compaction | USD 1.0204 | USD 9.9040 | USD 19.5980 |

This rules out the simplistic conclusion that compacting is free, but it also
shows that cache loss alone does not reverse the decision in this long,
39-call fixture. Shorter remaining horizons can reverse it; these totals must
not be extrapolated to a session with only one or two calls left.

### Quality and rework break-even

Token savings are the maximum total penalty that compaction can absorb. For the
model-threshold policy, the budgets are USD 0.4252 per Luna session, USD 4.0620
per Terra session, and USD 8.3100 per Sol session.

If a degraded session costs USD 100, the maximum additional degradation
probability is:

| Model | Compactions | Break-even probability per session | Break-even probability per independent compaction |
| --- | ---: | ---: | ---: |
| Luna | 4 | 0.4252% | 0.1063% |
| Terra | 3 | 4.0620% | 1.3540% |
| Sol | 3 | 8.3100% | 2.7700% |

Use the per-session column when one session-level degradation event is the unit
of risk. Use the per-compaction column only when each compaction has an
independent chance of causing the full USD 100 loss. For another loss value
`L`, divide the token saving by `L`, and by the number of compactions as well
for the independent-per-compaction interpretation. These are decision
thresholds, not simulated defect rates.

## Other Luna elasticities

These contrasts use the declared short-context fixtures and scale one
hypothetical session algebraically.

| Change with everything else fixed | Delta / session | Delta at 1k sessions | Delta at 1m sessions |
| --- | ---: | ---: | ---: |
| +1k stable visible-tool-schema tokens over 10 calls | USD 0.000430 | USD 0.43 | USD 430 |
| +1k non-retained output tokens on one call | USD 0.001200 | USD 1.20 | USD 1,200 |
| Add one 50k-prefix roundtrip with 500 output tokens | USD 0.001600 | USD 1.60 | USD 1,600 |
| Retain four 2k tool results instead of excluding them | USD 0.002240 | USD 2.24 | USD 2,240 |
| Add 1k to each of four retained tool results | USD 0.001120 | USD 1.12 | USD 1,120 |
| Increase four tool results from 2k to 10k each | USD 0.008960 | USD 8.96 | USD 8,960 |
| Rewrite a 50k prefix on all 10 calls instead of write once/read nine | USD 0.103500 | USD 103.50 | USD 103,500 |

The prefix-churn result is deliberately a conservative all-cold boundary. It
shows why timestamps, changing tool registries, changing system instructions,
or model switches near the front of a prompt can dominate the cost of the
volatile text itself by invalidating a much larger suffix.

## Decision rules

For this Pi route, the modeled cost-minimizing order of operations is:

1. Keep the leading system prompt and tool schema stable. Move volatile content
   behind the reusable prefix where semantics permit.
2. Avoid crossing the model-specific long-context boundary for a small amount
   of marginal context. Luna's Copilot boundary is 200k; Terra and Sol use
   272k.
3. Reduce sequential model roundtrips before deleting useful tool capability.
   Batch independent tool calls, truncate or summarize oversized results, and
   retain only what later calls need.
4. Compact when the expected future long-context savings exceed the summary,
   cache-rebuild, quality, rework, latency, and implementation costs. Do not use
   200k as a universal threshold for every model.
5. Treat output tokens and newly retained history as persistent costs when they
   flow into later calls, not merely as one-time generation costs.
6. Convert provider value into actual cash only after applying the user's
   remaining AI-credit allowance and overage settings.

Pi does not automatically compact at 200k under its nominal 1.05M catalog
window. With the documented 16,384-token reserve, its default trigger is about
1,033,616 tokens. A 200k strategy needs manual/custom compaction or an effective
context window near 216,384 tokens. The 800k path is conditional price
arithmetic: Pi advertises a 1.05M model window, but GitHub's public 1M-context
client guarantee names VS Code and Copilot CLI rather than third-party Pi.

## Data and validation

The analysis-ready bundle contains:

- `call-ledger.csv`: 2,059 hypothetical provider requests with exact token
  buckets, tier, component rates, component costs, and compaction markers.
- `scenario-results.csv`: 126 model/arm summaries.
- `contrast-results.csv`: 63 one-factor-at-a-time comparisons: 21 designs for
  each of Luna, Terra, and Sol.
- `scale-results.csv`: 126 exact projections at 1,000 and 1,000,000 executions.
- `break-even.csv`: 30 quality-loss thresholds for the two primary compaction
  policies, three models, and five loss values.
- `study-results.json`: all compact results and provenance in one object.
- `data-dictionary.json`: row grains, invariants, and formulas.
- `explore.sql`: DuckDB views and starter queries.
- `manifest.json`: deterministic artifact hashes.
- `independent-validation-report.json`: independent recomputation evidence.

Validation passed 19 unit/oracle tests. A separate standard-library validator
that does not import the simulator passed 50,792 checks with zero failures and
zero warnings. It recomputed every call from an independent rate oracle,
reconciled all aggregation levels, checked exact threshold behavior, proved
one-factor-at-a-time parameter structure, checked algebraic volume scaling, and
verified the complete 39-call compaction schedule. Repeated generation produced
identical hashes, and all statements in `explore.sql` executed successfully in
DuckDB.

## Inference boundary

This simulation identifies the accounting consequences of its declared token
flows. It does not measure actual Pi/Copilot cache behavior, empirical tool
parallelizability, task correctness, semantic loss after compaction, latency,
reliability, or the availability of 800k requests through third-party Pi.
Before operational adoption, replace the synthetic token inputs with observed
telemetry and measure any quality/rework term separately. No live run was
performed here because this study was explicitly requested as simulation only.

## Sources

- [GitHub Copilot models and pricing](https://docs.github.com/en/copilot/reference/copilot-billing/models-and-pricing)
- [GitHub usage-based billing for individuals](https://docs.github.com/en/copilot/concepts/billing/usage-based-billing-for-individuals)
- [GitHub guidance for optimizing AI usage](https://docs.github.com/en/copilot/tutorials/optimize-ai-usage)
- [Pi compaction and branch summarization](https://pi.dev/docs/latest/compaction)
- [Pi model and tier configuration](https://pi.dev/docs/latest/models)
- [OpenAI GPT-5.6 Luna](https://developers.openai.com/api/docs/models/gpt-5.6-luna) — direct-API cross-check only; its 272k threshold must not replace the Copilot Luna threshold in this route.
