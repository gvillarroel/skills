# Harness, model, tool, and cache efficiency evaluation — 2026-09-04

## Executive decision

There is no defensible context-free winner between GitHub Copilot CLI and Pi.
The decision unit is:

`harness × provider/auth route × model × tool policy × cache policy × workload × billing policy`

Under this study's synthetic mechanism, a resource-aware fixed-model policy is
the most robust default. It exposes only the tools needed for the current phase,
keeps reusable prefixes stable, caps retained tool output, and escalates model
strength only when a measured quality gate requires it. This policy reduced the
primary-cohort provider-value ledger by 66.34%, wall time by 17.31%, and total
economic loss by 17.55% relative to the deliberately resource-unaware baseline,
while simulated acceptance declined by 0.641 percentage points. These are
model-conditional estimates, not observed production savings.

Pi was not uniformly better than Copilot CLI in the controlled synthetic study.
It had lower normalized provider cost on three of eight primary workload
families, nearly tied on three, and was worse on two. Its quality-noninferiority
hypothesis was challenged by the localized-bug and test-debug workloads. The
reverse universal claim is also unsupported: Pi appeared on the primary
cost/quality/time Pareto frontier in seven of eight workload cells, while
Copilot CLI appeared in four. Frontier counts overlap and do not constitute a
single ranking.

## Question and inference boundary

The study asks which harness/model/tool/cache configurations should be expected
to process coding work efficiently for a stated purpose. "Efficient" is not
token price alone. It includes accepted work, external quality, policy failures,
cash and non-cash provider value, human review/rework, latency, retries,
compaction, tool failures, and the economic cost of rejected work.

The study does **not** identify which harness is better on real repositories.
The live pilot isolates fixed context and cache accounting with a trivial prompt;
it does not measure coding quality. The larger studies are simulations with
declared causal mechanisms and stress ranges. All conclusions are conditional
on those mechanisms, inputs, and ranges.

## Current product and rate boundary

The rate snapshot is frozen at 2026-09-04. Normal GitHub Copilot individual
billing is modeled as token usage converted to AI credits; legacy premium-request
billing is excluded from the primary analysis. The snapshot includes separate
uncached-input, cache-read, cache-write, output, and long-context rates for
GPT-5.6 Luna, Terra, and Sol; Copilot Pro, Pro+, and Max fees/allowances; and the
paid-plan automatic-model-selection discount.

Primary sources:

- [GitHub Copilot models and pricing](https://docs.github.com/en/copilot/reference/copilot-billing/models-and-pricing)
- [Usage-based billing for individuals](https://docs.github.com/en/copilot/concepts/billing/usage-based-billing-for-individuals)
- [GitHub Copilot plans](https://docs.github.com/en/copilot/get-started/plans)
- [GitHub guidance for optimizing AI usage](https://docs.github.com/en/copilot/tutorials/optimize-ai-usage)
- [Copilot CLI context management](https://docs.github.com/en/copilot/concepts/agents/copilot-cli/context-management)
- [Copilot CLI reference and OpenTelemetry](https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-command-reference)
- [OpenAI GPT-5.6 Luna](https://developers.openai.com/api/docs/models/gpt-5.6-luna)
- [OpenAI GPT-5.6 Sol](https://developers.openai.com/api/docs/models/gpt-5.6-sol)
- [OpenAI model comparison](https://developers.openai.com/api/docs/models/compare)
- [Pi repository and documentation](https://github.com/earendil-works/pi)

Prices and product behavior are time-varying. Refresh
`projects/harness-efficiency-study/source/rate-card-20260904.json` before using
this study for a later purchasing decision.

### Long-context threshold correction

The original three stochastic bundles used a uniform 272,000-token
long-context threshold for Luna, Terra, and Sol. Current GitHub Copilot pricing
uses a route-specific 200,000-token threshold for Luna and 272,000 for Terra and
Sol. Therefore, do not use the original bundle to estimate Luna long-context or
compaction economics. The offline Pi-only cost-elasticity extension in
`pi-cost-elasticity/` supersedes that part of the analysis with a call-level
ledger and the corrected thresholds. The earlier stochastic results remain the
frozen evidence for their declared synthetic design; they have not been
silently recomputed under the corrected Luna boundary.

### Context-rot extension

`pi-context-rot/` adds a fully offline, assumption-driven quality layer to the
corrected Pi cost ledger. It does not execute Pi, Copilot, GPT-5.6, or any other
model. Across 1,189 parameter sets it varies context-decay onset and strength,
summary fidelity, evidence position, retries, compaction cache treatment, and
model cost tier.

The named primary case compares the 39-call grow-to-800k trajectory with a
fixed 200k cap. Under an assumed 200k degradation onset, context effect that
halves grow-session odds, 95% evidence survival per compaction, uniform evidence
positions, and three attempts, grow resolves 92.1484% of assigned sessions and
the cap resolves 96.7227%. Luna expected provider spend per assigned session is
$1.530381 versus $0.788915 after retries. At one million assigned sessions that
is a model-conditional reduction of $741,466 and 45,742 additional completions.

The 95% completion SLO requires at least 83.9632% evidence survival per
compaction in this fixture. Cost alone is much less restrictive: the uncached
cap remains no more expensive per completed session down to 22.7543% survival
for Luna, 24.9478% for Terra, and 22.7318% for Sol. These boundaries are model
outputs, not empirical summary-quality estimates.

The evidence inventory includes NoLiMa, RULER, Lost in the Middle, and a
commit-pinned reanalysis of Chroma LongMemEval. It demonstrates why no universal
failure length is defensible: historical curves range from steep degradation
to near-flat behavior through 128k, while evidence position and distractor
structure also alter outcomes. Details, equations, decision tables, and source
links are in `pi-context-rot/README.md`.

## Variables included

| Layer | Material variables represented |
| --- | --- |
| Work | task family, difficulty, repository/context size, required tools, number of phases, verification burden, monthly volume, value of accepted work, cost of failure, and SLA |
| Harness | fixed prompt, built-in and registered tools, relevant-tool coverage, tool-selection confusion, retained result size, compaction behavior, approvals, parallelism, coordination, and conflict/rework overhead |
| Cache | eligible stable prefix, minimum cacheable size, retention window, inter-call gap, prefix stability/churn, model continuity, cache read/write partition, compaction resets, and cold/hot sessions |
| Model | Luna/Terra/Sol phase routing, model quality contribution, input/output price, cache read/write price, latency, provider reliability, and long-context surcharge |
| Tools | schema tokens, result tokens, calls, latency, success probability, external per-call cost, output truncation/retention, required-tool omission, and registry sprawl up to 500 tools |
| Orchestration | model calls, retries, retry limits, parallelizable fraction, concurrency, subtask coordination, conflict probability, context growth, and overflow/compaction loss |
| Economics | provider token-value ledger, direct marginal cash, subscription allowance and overage, allocated subscription fee, automatic-selection discount, external tool spend, human time, failure cost, and SLA penalty |
| Outcomes | 24 registered measures covering acceptance, external quality, policy violations, three cash/value ledgers, economic loss, normalized efficiency, time, token partitions, calls, retries, compactions, cache hit rate, and budget exhaustion |

Harness and provider labels do not directly add a hidden quality bonus. They
select explicit mechanism parameters. This prevents the simulation from
answering the question by embedding the desired brand conclusion in the label.

## Live calibration

The pilot used exactly `Reply with exactly OK. Do not use tools.`, GPT-5.6 Luna,
and the GitHub Copilot route. It measured fixed context overhead, not task
performance.

| Harness condition | Tool definitions | Cold prompt accounting | Warm continuation accounting | Reported cost surface |
| --- | ---: | --- | --- | --- |
| Copilot CLI default | 22 | 18,181 input; 18,178 cache-write tokens | 18,067 cache-read; 187 cache-write tokens | $0.004551 cold; $0.000415 warm |
| Copilot CLI `rg` + `glob` | 2 | 4,899 input; 4,896 cache-write tokens | not run | $0.001231 cold |
| Copilot CLI zero-tool observation | 0 | 4,256 input; 4,253 cache-write tokens | 4,168 cache-read; 132 cache-write tokens | $0.001070 cold; $0.000123 warm |
| Pi default | 4 | 3 uncached; 1,107 cache-write tokens | 1,107 cache-read; 21 cache-write tokens | catalog estimate only |
| Pi zero tools | 0 | 429 uncached input tokens | not run | catalog estimate only |

In this one prompt, reducing Copilot CLI from its full tool set to two tools cut
cold input by 73.05%. Reusing the default-tool prefix cut reported cost by
90.89%. These observations motivate, but do not numerically prove, the broader
simulation relationships. Pi's GitHub-route catalog estimate assigned no value
to reported cache writes, so it is explicitly excluded as evidence of actual
Copilot cash charges.

## Experimental design

All matched scenarios use common random numbers through named SHA-256
substreams. Each scenario/design-point cell has 200 replications and four
latent tasks per replication. The complete run executed 33,600 simulation runs,
representing 134,400 simulated task executions, and emitted 806,400 outcome rows
plus 235,200 diagnostics.

| Study | Purpose | Scenarios | Design points | Runs |
| --- | --- | ---: | ---: | ---: |
| `controlled-harness` | Separate whole-harness behavior from provider route while fixing workload and model policy | 3 | 16 | 9,600 |
| `monthly-economics` | Compare direct API and Copilot Pro+ cash allocation across monthly volume | 3 | 12 | 7,200 |
| `usage-policy` | Compare resource-unaware, resource-aware fixed-model, and phase-routed policies under ordinary and adversarial conditions | 3 | 28 | 16,800 |

The design includes hot cache, cold cache, prefix churn, tool-registry sprawl,
lossy long sessions, unreliable tools, missing relevant tools, high coordination,
and underpowered-model challenges. Challenge points are deliberately capable of
reversing a claim; they are not estimates of the prevalence of those conditions.

## Main results

### Controlled harness comparison

Primary-cohort averages:

| Scenario | Accepted fraction | Provider value / task | Marginal cash / task | Allocated cash / task | Economic loss / task | Wall seconds / task |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Copilot CLI via Copilot | 0.248 | $10.2336 | $10.1187 | $10.2487 | $125.02 | 1,625.6 |
| Pi via Copilot | 0.204 | $10.1810 | $10.0329 | $10.1629 | $126.40 | 1,636.5 |
| Pi via direct OpenAI API | 0.204 | $10.1810 | $10.2663 | $10.2663 | $126.50 | 1,636.5 |

The Pi provider routes have identical synthetic quality, time, and provider-value
ledgers by construction; only the billing route changes. This negative control
passed exactly. Direct API marginal cash was $0.2333/task higher in the
controlled portfolio because the modeled Copilot allowance absorbed part of the
same provider-value ledger.

The registered Pi-versus-Copilot normalized-cost claim was challenged. Pi met
the cost threshold in three of eight primary workloads, was close but missed it
in three, and was worse in the localized-bug and test-debug workloads. Pi's
quality-noninferiority claim also failed globally: the largest primary deficits
were -0.0659 external-quality-score units for localized bugs and -0.1156 for
test debugging, both beyond the preregistered -0.02 margin. Conversely, Pi had higher continuous
quality in six of eight primary workloads and appeared on more Pareto-frontier
cells. The correct interpretation is workload-dependent trade-off, not brand
dominance.

### Tool/context policy comparison

Primary-cohort averages:

| Policy | Accepted fraction | Provider value / task | Economic loss / task | Wall seconds / task | Tool-schema tokens / task | Uncached input / task |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Resource-unaware, fixed Sol | 0.2422 | $26.8064 | $145.58 | 1,916.5 | 324,644 | 4,326,947 |
| Resource-aware, fixed Terra | 0.2358 | $9.0238 | $120.03 | 1,584.8 | 45,489 | 3,739,097 |
| Resource-aware, phase-routed | 0.2306 | $8.6997 | $120.18 | 1,589.8 | 45,489 | 3,739,097 |

Relative to the unaware policy, the fixed resource-aware policy reduced
tool-schema tokens by 85.99% and uncached input by 13.59%. It occupied the
primary Pareto frontier in 13 of 16 harness/workload cells, versus four each for
the phase-routed and unaware policies; counts overlap where policies tie or are
non-dominated.

Phase routing reduced the provider ledger another 3.59% relative to fixed
resource-aware Terra, but economic loss increased 0.131%, wall time increased
0.315%, and acceptance fell 0.523 percentage points. Token savings alone did not
win once quality, rework, and delay were included. Phase routing should therefore
be enabled only after a workload-specific quality gate, not assumed beneficial.

### Monthly economics

Across 12 design points, allocated cash was lower for Copilot Pro+ in 11 and
lower for Pi with direct OpenAI API in one. This does not mean a subscription is
always cheaper: the allocated fee dominates at very low volume, whereas included
allowance dominates later.

Only the `localized-hot` workload had comparable points bracketing a crossover:

- 30 tasks/month: direct Pi $0.5115/task versus Copilot Pro+ $1.3188/task;
- 320 tasks/month: Copilot Pro+ $0.3722/task versus direct Pi $0.5092/task;
- 3,200 tasks/month: Copilot Pro+ $0.4558/task versus direct Pi $0.5056/task.

Linear interpolation gives a model-conditional break-even near 278 tasks/month.
No crossover is reported for other workload families because their available
points do not provide a comparable bracket; extrapolation would be unjustified.

## Hypothesis disposition

| Registered hypothesis | Result | Interpretation |
| --- | --- | --- |
| Pi has lower normalized cost than Copilot CLI under a matched provider/model | `challenges-under-model` | Some workloads support it; several ordinary and adversarial points reverse it. |
| Pi quality is noninferior within -0.02 external-quality-score units | `challenges-under-model` | Localized-bug and test-debug workloads cross the noninferiority margin. |
| Pi provider routes have equal provider-value ledgers | `supports-under-model` | Exact negative control; billing route changes cash, not synthetic work behavior. |
| Direct API has higher marginal cash when Copilot allowance applies | `supports-under-model` | Supported across all controlled points. |
| Copilot Pro+ beats direct API at high monthly volume | `supports-under-model` | Supported under modeled allowance and auto-selection discount. |
| Direct API wins at low monthly volume | `challenges-under-model` | True for one low-volume workload, not universal across task families. |
| Resource-aware tooling reduces provider cost, latency, and preserves quality | `challenges-under-model` | Strong in the primary cohort, but hot-cache/underpowered-model challenges reverse all three universal claims. |
| Phase routing lowers cost while preserving quality | Cost: `challenges-under-model`; quality: `supports-under-model` | Savings are fragile; the noninferiority gate survives the declared challenges. |
| A real-world best harness follows from this simulation | `not-identifiable-from-design` | Requires paired repository tasks and an external verifier. |

## Strongest counterexample

The strongest registered contradiction was the Pi hot-cache challenge. The
resource-unaware Sol policy accepted 0.8988 of simulated tasks and completed in
372.3 seconds/task. The resource-aware Terra policy accepted 0.1000 and required
1,184.8 seconds/task because the underpowered configuration triggered a retry
and rework cascade. The normalized-wall-time delta was +6.018 versus the
registered requirement of at most -0.1.

This is a deliberately extreme failure-seeking condition, not a forecast. Its
decision value is architectural: tool/context pruning and cheaper models need a
quality escape hatch. A safe policy monitors verifier failure/retry rate and
escalates model/tool access before token savings turn into rework.

## Conditional harness choice

| Situation | Best starting configuration | Why | What must be verified |
| --- | --- | --- | --- |
| Low, irregular monthly volume | Pi with direct API and a small phase-complete tool set | Avoids allocating a monthly fee to a few tasks and gives direct control of provider/model routing | Actual API spend, verifier pass rate, and setup/maintenance time |
| Predictable medium or high volume already inside Copilot | Copilot Pro+ or Pi through the Copilot route, depending on workflow fit | Included AI-credit allowance can lower marginal cash after the fee is committed | Allowance exhaustion, overage, automatic-routing discount, and whether the chosen harness exposes actual billing telemetry |
| Fast localized edit with a stable warm prefix | The harness with the smallest sufficient fixed context, usually a lower-cost model plus verifier | Fixed overhead and cache reuse dominate a short task | Cold versus warm runs, required-tool coverage, and retry escalation |
| Broad repository refactor or parallel analysis | Pi-like minimal core with explicit parallel tools/agents, or equivalently configured Copilot | The synthetic Pi policy benefits where parallelism and reduced registry overhead matter | Coordination/conflict rate, tool-result retention, and external quality |
| Browser/integration-heavy workflow | Copilot-like richer tool policy initially | Removing a necessary diverse tool can cost more than its schema overhead | Tool relevance, external tool reliability/cost, approvals, and policy violations |
| High-stakes verification or repeated failures | Resource-aware policy with Sol escalation for verification | Cheaper fixed or phase-routed models can trigger retry/rework cascades | Independent verifier, failure cost, human review, and escalation threshold |
| Long session with unstable prefixes or model switches | Stable model/tool configuration, bounded summaries, and deliberate compaction | Cache writes, invalidation, long-context rates, and information loss can dominate | Cache hit/write partition, compaction loss, and long-context surcharge |

This matrix recommends a starting experiment, not a procurement verdict. Copilot
offers a more integrated default workflow; Pi offers a smaller programmable core
and finer composition. Either can be configured poorly, and Pi can use the
GitHub Copilot provider route, so the harness name alone does not determine the
model, bill, or efficiency.

## Recommended operating policy

1. Define the purpose first: low-latency edit, broad repository change, browser
   workflow, test repair, or long-horizon research require different frontiers.
2. Instrument uncached input, cache reads, cache writes, output, visible tool
   schemas, retained tool results, model/tool calls, retries, compactions,
   verifier pass rate, wall time, and human rework. Keep provider value,
   marginal cash, and allocated subscription cost as separate ledgers.
3. Start with the smallest phase-complete tool set. Do not expose hundreds of
   tools to every model turn, but never remove a required tool without an
   escalation path.
4. Keep system instructions and other reusable content at the front of the
   prompt, preserve model/tool configuration within a session, and avoid
   unnecessary prefix churn. Track cold and warm performance separately.
5. Use a mid-tier model as the fixed default only where a verifier confirms it
   is adequate. Escalate on difficulty, repeated failure, verification, or
   long-context risk. Treat phase routing as an empirically tuned policy.
6. Choose direct API versus subscription from workload-specific monthly volume,
   allowance exhaustion, and opportunity cost. Do not compare catalog token
   estimates with actual subscription cash as though they were the same metric.
7. Before standardizing a harness, run a paired crossover trial on real tasks:
   same task snapshots, provider/model, tool entitlement, time budget, and
   external verifier; randomized order; repeated cold and warm sessions; report
   the Pareto frontier and challenge failures rather than one aggregate score.

## Validation and reproducibility

Every planned simulation completed and every bundle passed independent
recalculation and provenance validation:

| Study | Planned / successful | Failed | Invalid | Outcome rows | Diagnostic rows | Release eligible |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| Controlled harness | 9,600 / 9,600 | 0 | 0 | 230,400 | 67,200 | yes |
| Monthly economics | 7,200 / 7,200 | 0 | 0 | 172,800 | 50,400 | yes |
| Usage policy | 16,800 / 16,800 | 0 | 0 | 403,200 | 117,600 | yes |

The compact versioned tables in this directory are generated from the ignored
replication-level bundle. Reproduce the complete raw data with:

```powershell
python -B projects\harness-efficiency-study\scripts\run_all_studies.py `
  --run-root projects\harness-efficiency-study\artifacts\runs\reproduction
```

The exact release inputs and validation digests are preserved in the three
`*-validation.json` files. The canonical experiment specs and model are
versioned under `projects/harness-efficiency-study/`.

The context-rot extension separately passes 16 deterministic/oracle tests and
5,116,530 implementation-independent recomputations with zero failures or
warnings. Its six paired 200,000-task Monte Carlo sentinels validate analytic
completion and cost-per-completion arithmetic only; they do not validate the
hypothetical quality equations against production behavior.

## Exploration map

- `scenario-summary.csv`: portfolio and cohort averages by outcome.
- `workload-ranking.csv`: one row per scenario/design-point pair with all 24
  measures and within-workload efficiency rank.
- `pairwise-deltas.csv`: registered pairwise effects, uncertainty intervals,
  thresholds, roles, and result classifications.
- `pareto-frontier.csv`: cost/quality/time dominance by workload.
- `break-even.csv`: monthly direct-versus-subscription point comparisons and
  defensible interpolation status.
- `study-results.json`: compact machine-readable headline results.
- `generated-report.md`: deterministic report emitted by the analyzer.
- `explore.sql`: DuckDB views and starter questions over the versioned CSVs.
- `*-hypotheses.json`: full generated hypothesis evidence.
- `*-validation.json`: release and digest evidence.
- `pi-cost-elasticity/`: deterministic Pi request, cache, tool, and compaction
  cost ledger.
- `pi-context-rot/`: context-quality sensitivity surface, empirical evidence
  inventory, decision boundaries, and independent validation report.
- `checksums.sha256`: SHA-256 integrity ledger for every other versioned file.

Run DuckDB from this directory:

```powershell
duckdb :memory: -c ".read explore.sql"
```

The full raw bundle also contains tidy replication-level `runs.csv`,
`outcomes.csv`, diagnostics, a machine-readable data dictionary, and its own
`analysis/explore.sql`.

## Limitations

- The pilot has one trivial prompt and sequential observations; it cannot
  estimate coding quality, congestion, or long-session behavior.
- Synthetic quality, latency, retry, human-time, compaction-loss, and failure
  functions are assumptions. Wide challenge points test fragility but do not
  estimate real-world frequencies.
- Primary averages weight declared workload cells equally; they are not an
  organization's observed task mix.
- Acceptance is a strict synthetic threshold and is intentionally pessimistic
  in this failure-seeking study. Do not treat the absolute rates as forecasts.
- Copilot Cloud agent Actions minutes and remote-environment overhead are outside
  the local CLI comparison.
- Pi's catalog cost on the Copilot route is not verified cash billing.
- The Pi-only 800k extension is conditional price arithmetic: Pi exposes a
  1.05M catalog window, while GitHub's public 1M client guarantee does not name
  third-party Pi. It is not an availability claim.
- Rate cards, included allowances, default tools, model aliases, context rules,
  and harness versions can change. Recalibrate before operational use.
