# Pi-to-Copilot cost-elasticity method

This preregistered extension answers a deliberately narrow question: how much
does the provider token value of a hypothetical Pi task or session change when
one prompt, tool, cache, or compaction decision changes? It is an offline,
deterministic accounting simulation. It must not invoke Pi, Copilot, an OpenAI
API, or another model endpoint.

The machine-readable source of truth is
`pi-cost-elasticity-spec-20260904.json`. Prices are frozen as observed on
2026-09-04. Refresh and version the rate card before reusing results for a later
decision.

## Scope and estimand

The harness is Pi, the provider/authentication route is GitHub Copilot, and each
contrast fixes one model: GPT-5.6 Luna, Terra, or Sol. There is no automatic
model routing and no automatic-selection discount. The main estimand is the
public token value charged through the modeled route, in USD and GitHub AI
Credits. One AI Credit is modeled as USD 0.01.

The observed Pi Sol catalog exposed an older, lower price surface than GitHub's
current billing table. Use GitHub's route table as the pricing source of truth;
otherwise Sol costs can be materially understated.

Provider token value is not necessarily the user's incremental cash bill. A
paid plan can absorb credits until its allowance is exhausted, while allowance
use still has opportunity cost. Do not report simulated provider value as cash
outlay unless the remaining allowance and overage state are supplied.

## Request ledger and tier selection

Every request has four non-overlapping token buckets:

- uncached input;
- cache read;
- cache write;
- output.

The three input buckets must sum to total request input. For request \(r\),
model \(m\), and the tier selected by total input, cost is:

```text
C(r,m) = (U * p_input + R * p_read + W * p_write + O * p_output) / 1,000,000
```

The long-context tier applies to all four rates when request input is strictly
greater than 200,000 tokens for Luna or 272,000 tokens for Terra and Sol. A
request exactly at its threshold remains short tier. This GitHub Copilot rule
is route-specific: direct OpenAI Luna documentation uses a different 272,000
token threshold, so direct-API rates or thresholds must not be substituted into
this Pi-through-Copilot study.

A stable prefix is cache-written on the first request. An append-only
continuation cache-reads the previous prefix and cache-writes only its new
suffix. Tool-call arguments are billed once as model output and are retained as
part of the next input suffix along with the tool result. Full-prefix churn
cache-writes the affected prompt again. These are explicit model assumptions,
not measurements of a live provider cache.

## One-factor-at-a-time design

Each pair changes one declared decision variable. Model, route, retry count,
tool fees, output policy, latency value, labor value, and all remaining token
inputs stay fixed unless the scenario names one of them as the factor. A policy
change may mechanically alter downstream request counts or token partitions;
those are outcomes, not additional experimental factors.

There are 21 preregistered contrasts:

1. `stable-system-1-call` adds 1,000 stable system-prompt tokens to one cold
   call.
2. `stable-system-10-calls` adds the same stable segment across 10 calls.
3. `stable-system-50-calls` adds the same stable segment across 50 calls.
4. `dynamic-system-10-calls` adds 1,000 non-reusable system-prompt tokens to
   each of 10 calls.
5. `system-threshold-cold` moves one cold prompt from 500 tokens below to 500
   tokens above the model's Copilot long-context threshold.
6. `system-threshold-warm` repeats that discontinuity with an initially hot
   prefix.
7. `sequential-tools-4-to-5` adds a fifth sequential tool, an additional model
   roundtrip, and its accumulated-context replay.
8. `batched-tools-4-to-5` adds a fifth tool inside the same parallel batch while
   keeping the model request count at two.
9. `tool-count-4-vs-5-sequential-800k` repeats the sequential fifth-tool
   contrast from a conditional 800,000-token prefix.
10. `stable-tool-schema-10-calls` adds 1,000 stable visible tool-schema tokens
    across 10 calls.
11. `output-1k-one-call` adds 1,000 output tokens to one cold call.
12. `retain-tool-results-4-tools` injects and retains the four existing
    2,000-token sequential tool results instead of discarding them.
13. `tool-result-size-plus-1k` adds 1,000 retained tokens to each of four
    sequential tool results.
14. `tool-result-2k-vs-10k-sequential-4` increases every retained result from
    2,000 to 10,000 tokens as a stress case.
15. `prefix-churn-10-calls` replaces a stable 50,000-token prefix with a full
    prefix rewrite on each of 10 calls.
16. `extra-roundtrip-10-to-11` adds one warm fixed-prefix model roundtrip to a
    10-roundtrip task.
17. `long-cap-200k-uncached` compares an uncompacted 40,000-to-800,000-token
    session with compaction before the next main call would exceed 200,000
    tokens.
18. `long-cap-pricing-threshold-uncached` uses each model's Copilot price-tier
    threshold as the compaction cap: 200,000 for Luna and 272,000 for Terra and
    Sol.
19. `compaction-input-cache-read-sensitivity` changes only the 200,000-token
    cap's compaction input from uncached input to cache read.
20. `compaction-input-cache-write-sensitivity` changes only that compaction
    input from uncached input to cache write.
21. `compaction-retained-system-sensitivity` changes only the rebuilt prompt
    from a full cold write to reuse of a retained 20,000-token system prefix.

For \(T\) sequential tool invocations, there are \(T+1\) model requests. The
first request writes the initial prompt. Before each later request, the prior
tool argument and result are appended; the old prefix is read and that suffix is
written. For one parallel batch there are always two model requests: the first
writes the prompt and emits all tool arguments, while the second reads the
prompt, writes all argument-plus-result suffixes, and emits the final answer.

## Long-session and compaction policy

The uncompacted fixture has 39 main requests at 40,000, 60,000, ..., 800,000
input tokens. The compact fixture preserves 39 logical main requests but
compacts before the next main request would exceed 200,000 tokens. It resets the
next prompt to 40,000 tokens, emits a 20,000-token summary, and therefore adds
four compaction requests. Its main requests never exceed 200,000 tokens.

The two primary compaction contrasts treat each compaction request as fully
uncached and the rebuilt 40,000-token prompt as a cold cache write. One uses a
fixed 200,000-token cap; the other uses the active model's Copilot price-tier
threshold. The conservative uncached treatment follows the implication of a
fresh Pi routing-session identifier and disabled cache writes on the compaction
call. Three one-factor sensitivity contrasts start from the fixed 200,000-token
policy: charge compaction input as a cache read; charge it as a cache write; or
retain a 20,000-token system prefix for the rebuilt request. These sensitivity
contrasts are not headline estimates.

The 200,000-token cap is a simulated strategy, not Pi's default. With a
1,050,000-token catalog window and the default 16,384-token reserve, Pi's
automatic trigger is approximately 1,033,616 tokens; a 200,000-token policy
therefore requires manual/custom compaction or an effective context window near
216,384 tokens. Pi also keeps 20,000 recent tokens by default.

The 800,000-token path is conditional. Pi's catalog exposes a 1,050,000-token
window, but GitHub's public one-million-token context guarantee is documented
for VS Code and Copilot CLI, not third-party Pi. The simulation can price the
path but cannot establish that GitHub will serve it through Pi.

## Scaling and elasticity

Compute each task or session once, then multiply totals by 1,000 and 1,000,000
hypothetical monthly executions. Do not materialize one million duplicate rows.
Report baseline, comparison, absolute delta, percent delta, AI Credits, and
token-partition deltas.

For positive numeric decision variables, report arc elasticity:

```text
elasticity = ((comparison cost - baseline cost) / baseline cost)
             / ((comparison value - baseline value) / baseline value)
```

Also report marginal USD per changed unit. For booleans and threshold crossings,
report only the finite difference. Mark threshold switches explicitly because a
discontinuous tariff has no useful local derivative at the boundary.

## Quality and decision break-even

Token accounting alone cannot determine whether lossy compaction is worthwhile.
For every compact-versus-uncompacted result, calculate token savings and expose
an external penalty layer:

```text
total incremental penalty
  = degradation probability * loss per degraded execution
  + additional human rework
  + additional latency value
  + implementation overhead
```

The compact policy is economically preferred only when token savings exceed
that penalty. With all other penalties set to zero, the break-even degradation
probability is token savings divided by loss per degraded execution. Evaluate
loss values of USD 10, 50, 100, 500, and 1,000. These probabilities are decision
thresholds, not estimates of how often compaction actually causes harm.

Report a second threshold for an independent per-compaction risk model by
dividing the same saving by both the loss per degraded compaction and the number
of compactions. Use the first threshold when degradation is assessed once per
session; use the second only when every compaction independently risks the full
declared loss.

## Required validation and interpretation

An independent validator must recompute each request from the detailed token
ledger, verify mutually exclusive input buckets, assert the model-specific tier
boundary at threshold and threshold plus one, check exact algebraic volume
scaling, and confirm that only the declared decision variable changes within
each pair. The compact fixture must have 39 main calls, four compaction calls,
and a maximum main prompt of exactly 200,000 tokens.

Results support statements such as "under these token-flow assumptions, one
additional stable system-prompt kilotoken costs X at one million executions."
They do not support claims about real cache hit rates, model quality, latency,
third-party context availability, or whether Pi is superior to another harness.

## Sources

- [GitHub Copilot models and pricing](https://docs.github.com/en/copilot/reference/copilot-billing/models-and-pricing)
- [Optimize AI usage and reduce costs](https://docs.github.com/en/copilot/tutorials/optimize-ai-usage)
- [Pi compaction documentation](https://github.com/earendil-works/pi-mono/blob/main/packages/coding-agent/docs/compaction.md)
- [Pi model and tier configuration](https://pi.dev/docs/latest/models)
- [OpenAI GPT-5.6 Luna model documentation](https://developers.openai.com/api/docs/models/gpt-5.6-luna) — direct-API cross-check only
