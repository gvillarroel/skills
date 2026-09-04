# Pi context-rot cost-quality sensitivity — 2026-09-04

## Executive answer

This study made **zero real Pi, GitHub Copilot, GPT-5.6, or other model/API
calls**. It extends the deterministic Pi-through-Copilot cost ledger with an
explicitly hypothetical quality layer so that context growth, compaction loss,
bounded retries, and provider cost can be compared on the same assigned-session
unit.

There is no evidence-supported universal token count at which an agent starts
to fail. Published results differ sharply by task, model, distractor structure,
and evidence position. The defensible output is therefore a sensitivity
surface and decision boundaries, not a single production forecast.

In the named primary scenario, the uncompacted 39-call session grows from 40K
to 800K input tokens. The alternative compacts before the next main call would
exceed 200K, producing four summaries at logical calls 9, 18, 27, and 36. The
quality assumption says that context exposure halves the odds of single-attempt
success along the full grow trajectory, while each compaction retains 95% of
task-relevant evidence. With at most three independent attempts:

- growing to 800K resolves 92.1484% of assigned sessions and misses the 95% SLO;
- capping at 200K resolves 96.7227% and meets the SLO;
- the uncached-compaction policy reduces expected provider spend per assigned
  session by 48.45% for Luna, 46.89% for Terra, and 48.46% for Sol after retry
  behavior is included;
- the 200K policy needs at least 83.9632% per-compaction evidence survival to
  meet the 95% completion SLO under this exact model;
- at the primary 95% survival assumption, the 200K policy is already cheaper
  per completed session even when the context-length penalty is set to zero.

Those are conditional model results. The 95% summary fidelity, onset, task mix,
and independent retry recovery are assumptions, not measured properties of Pi
or GPT-5.6.

## What the external evidence does and does not establish

The evidence inventory contains 47 source-bound statistics across nine series.
It keeps source-reported results separate from independently recomputed values,
approximate chart/repository values, inequalities, and tokenless position
controls.

| Evidence | Directly observed result | What can be concluded |
| --- | --- | --- |
| NoLiMa GPT-4.1 | Accuracy falls from 95.6% at 1K to 64.7% at 128K; the authors report a 16K effective length under their 85%-of-base rule. | Semantic retrieval without literal overlap can degrade far before a claimed 1M context capacity. It is not a coding-agent or GPT-5.6 curve. |
| RULER GPT-4-1106 | Mean score falls from 96.6% at 4K to 81.2% at 128K. | The same broad direction appears on a 13-task synthetic suite, but the aggregate hides task heterogeneity. |
| RULER Gemini 1.5 Pro | Mean score changes from 96.7% at 4K to 94.4% at 128K. | Some model/task combinations remain comparatively flat, refuting a universal steep decay law. |
| Chroma GPT-4.1 LongMemEval | The pinned row-level data yield 267/306 correct for focused prompts averaging 268.6 tokens and 191/306 for full prompts averaging 112,672.8 tokens. The paired difference is 24.8366 percentage points; paired bootstrap 95% interval 19.2810–30.3922 points; exact McNemar p ≈ 8.065×10⁻¹⁶. | Degradation is clearly present by the long full-history condition in this protocol. The two conditions also differ in retrieval and distractor burden, and two endpoints cannot identify where the decline began. |
| Lost in the Middle | Performance depends on where relevant evidence appears, often favoring the beginning or end over the middle. | Token count alone is insufficient; evidence position must be varied or blocked in a realistic evaluation. |

Primary evidence sources are the [NoLiMa official repository](https://github.com/adobe-research/NoLiMa),
the [RULER official repository](https://github.com/NVIDIA/RULER), the
[Chroma Context Rot report](https://www.trychroma.com/research/context-rot) and
[commit-pinned result files](https://github.com/chroma-core/context-rot/tree/af80a08018f2b7257c0336d04bcd02f936088106/results),
and the [Lost in the Middle paper](https://aclanthology.org/2024.tacl-1.9/).
OpenAI's own GPT-4.1 guidance likewise distinguishes context capacity from
uniform task performance: it notes degradation when retrieval requires more
items or reasoning over the state of the full context, and it notes that prompt
placement matters. See [OpenAI model guidance](https://developers.openai.com/api/docs/guides/latest-model?model=gpt-4.1).

The committed Chroma focused and full CSVs are pinned to repository commit
`af80a08018f2b7257c0336d04bcd02f936088106`. Their recorded SHA-256 digests are
`03ab9d9798263cc9c02d87da111b8715e1822c5a874f9ca29afbb7710135d874`
and `037fd6e862d173dca9ad15793cca15d9609840d200dd17a0c754903ae070ff80`.

## Descriptive retention crossings

`evidence-onsets.csv` normalizes each eligible curve to its earliest eligible
context point and uses log2-context interpolation only across an observed
downward bracket. It never extrapolates. These are descriptive crossings of
published point estimates, not confidence-bounded failure onsets.

| Historical series | 95% retained | 90% retained | 85% retained | Lower thresholds |
| --- | ---: | ---: | ---: | --- |
| NoLiMa GPT-4.1, relative to its 1K point | 4.625K | 11.807K | 26.241K | 80% at 40.189K; 70% at 94.092K; 50% unidentifiable |
| RULER GPT-4-1106, relative to its 4K point | 37.548K | 64.461K | 114.810K | 80% and below unidentifiable through 128K |
| RULER Gemini 1.5 Pro | unidentifiable | unidentifiable | unidentifiable | No declared retention threshold is crossed through 128K |

The Chroma two-point series also produces mathematical interpolations in the
file, but those values must be treated only as a stress mapping: the gap from
approximately 269 to 112,673 mean tokens is too wide, and the focused/full
conditions change retrieval burden as well as length. The evidence establishes
a difference at the endpoints, not an onset inside the gap.

## Simulation model

### Fixed workload and strategies

The cost layer is imported without modification from the independently
validated `pi-cost-elasticity` bundle. Every retry repeats one complete
hypothetical session trajectory at the same deterministic provider-token value.

Five strategies are evaluated:

1. `grow_to_800k` — no compaction; 39 main prompts from 40K to 800K.
2. `cap_200k_uncached` — four uncached summary calls and cold prompt rebuilds.
3. `cap_200k_cache_read` — optimistic cache-read accounting sensitivity for
   the compaction input.
4. `cap_200k_cache_write` — conservative cache-write accounting sensitivity.
5. `cap_pricing_threshold_uncached` — 200K for Luna and the model-specific
   Copilot threshold for Terra/Sol.

Pi's documentation says its automatic trigger is
`contextTokens > contextWindow - reserveTokens`, with a default 16,384-token
reserve and 20K recent-token retention. It also says compaction uses a fresh
routing session and commonly disables prompt-cache writes for the one-off
summary request. Therefore, the fixed 200K policy is proactive/manual in this
study, and the uncached case is primary; cache-read and cache-write cases are
sensitivities. See [Pi compaction documentation](https://pi.dev/docs/latest/compaction).

### Quality and retry equations

For active main-request prompt tokens `L_i`, assumed degradation onset `O`, and
39 calls, context exposure is:

```text
E = sum(max(L_i - O, 0)) / (39 * 100000)
```

The fixed 100K unit keeps a given `beta` comparable when only the onset changes.
For the grow trajectory at a 200K onset, `E = 31/13`; for the 200K cap, `E = 0`.

Each compaction has assumed task-evidence survival `f`. Evidence introduced at
different points crosses a different number of summaries. Uniform,
front-loaded, and back-loaded evidence-position profiles convert those losses
into effective session fidelity `F`. At `f = 0.95` with uniform positions and
four 200K compactions:

```text
F = (9*f^4 + 9*f^3 + 9*f^2 + 9*f + 3) / 39
  = 0.890241826923077
```

For each task stratum, the single-attempt success assumption is:

```text
p = logistic(logit(p0) - beta * E + ln(F))
```

The hypothetical workload weights easy, typical, and hard tasks 25%/50%/25%,
with short-context `p0` values 0.95/0.80/0.55. Results are computed inside each
stratum before weighting, so the nonlinear retry formula is not incorrectly
applied to an average probability. With at most `K` conditionally independent
attempts:

```text
P(complete) = 1 - (1-p)^K
E[attempts] = sum((1-p)^j, j=0..K-1)
assigned provider spend = cost_per_attempt * E[attempts]
cost per completed session = weighted assigned spend / weighted P(complete)
```

Independent retries are optimistic when the same missing evidence or defective
summary persists. The one-attempt grid acts as a no-recovery challenge, but it
does not estimate real retry correlation.

## Primary result

The named primary point uses onset 200K,
`beta = ln(2) * 13/31 = 0.2906746241`, per-compaction evidence survival 0.95,
uniform evidence positions, and three attempts maximum.

| Model | Strategy | Cost / attempt | Completion | Spend / assigned | Cost / completed | Meets 95% SLO |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| Luna | Grow to 800K | $1.020400 | 92.1484% | $1.530381 | $1.660778 | no |
| Luna | Cap 200K, uncached | $0.595200 | 96.7227% | $0.788915 | $0.815647 | yes |
| Luna | Cap 200K, cache-read | $0.451200 | 96.7227% | $0.598048 | $0.618313 | yes |
| Terra | Grow to 800K | $9.904000 | 92.1484% | $14.853877 | $16.119509 | no |
| Terra | Cap 200K, uncached | $5.952000 | 96.7227% | $7.889150 | $8.156466 | yes |
| Terra | Cap 200K, cache-read | $4.512000 | 96.7227% | $5.980485 | $6.183127 | yes |
| Sol | Grow to 800K | $19.598000 | 92.1484% | $29.392799 | $31.897227 | no |
| Sol | Cap 200K, uncached | $11.428000 | 96.7227% | $15.147380 | $15.660633 | yes |
| Sol | Cap 200K, cache-read | $8.548000 | 96.7227% | $11.330049 | $11.713956 | yes |

Quality is identical across Luna, Terra, and Sol by construction; the model
label changes only the imported cost surface. No unsupported GPT-5.6 quality
ranking is embedded in the simulation.

### Algebraic scale to one million assigned sessions

| Model | Grow spend / completed | Cap 200K uncached spend / completed | Expected additional completed sessions | Expected spend reduction |
| --- | ---: | ---: | ---: | ---: |
| Luna | $1,530,381 / 921,484 | $788,915 / 967,227 | 45,742 | $741,466 |
| Terra | $14,853,877 / 921,484 | $7,889,150 / 967,227 | 45,742 | $6,964,727 |
| Sol | $29,392,799 / 921,484 | $15,147,380 / 967,227 | 45,742 | $14,245,419 |

The million-session rows are exact multiplication of one model-conditional
expectation; they are not one million independent observations and do not make
the quality assumptions more certain.

## Decision boundaries

`fidelity-boundaries.csv` solves the exact analytic model by bisection.

| Model | Minimum `f` for uncached cap to cost no more per completion | Minimum `f` for cache-read cap to cost no more per completion | Minimum `f` for 95% completion SLO |
| --- | ---: | ---: | ---: |
| Luna | 22.7543% | 4.3322% | 83.9632% |
| Terra | 24.9478% | 6.1457% | 83.9632% |
| Sol | 22.7318% | 3.5145% | 83.9632% |

The SLO, not token cost, is the binding boundary in the primary fixture. At
`f = 0.95`, the minimum `beta` needed for the compact strategy to be cheaper
per completed session is zero for all six model/cache comparisons: the token
saving already offsets the modeled summary loss even if long-context quality
is flat. That result is specific to this 39-call cost ratio and does not imply
that compacting a shorter session, a high-value evidence record, or a different
summary mechanism is always optimal.

## Sensitivity surface

The bundle evaluates 1,189 parameter sets:

- 1,080 generic points crossing onsets 16K/32K/113K/200K/400K/600K, `beta`
  0/0.25/0.5/1/2, fidelity 1/.99/.97/.95/.90/.80, one or three attempts, and
  uniform/front-loaded/back-loaded evidence;
- 108 historical-proxy stress points using two-anchor Chroma, RULER, and NoLiMa
  log-odds slopes, explicitly labeled as non-GPT-5.6 calibrations;
- one named primary point.

The output has 53,505 stratum rows, 17,835 aggregate rows, 14,268 matched
strategy contrasts, 14,268 failure-loss break-even rows, and 35,670 algebraic
volume projections. Use `explore.sql` to answer narrower questions without
loading every result into a spreadsheet.

## Artifacts

- `trajectory-metrics.csv`: active prompt paths, onset exposure, and
  compaction positions.
- `quality-stratum-results.csv.gz`: exact quality/retry arithmetic by task stratum.
- `quality-aggregate-results.csv.gz`: weighted session outcomes.
- `quality-contrast-results.csv.gz`: compact-minus-grow comparisons.
- `break-even.csv.gz`: provider saving versus incremental unresolved-session
  trade-offs.
- `fidelity-boundaries.csv`: quality and cost boundary roots.
- `scale-results.csv.gz`: exact 1K and 1M assigned-session projections.
- `monte-carlo-summary.csv`: six paired common-random-number arithmetic checks.
- `evidence-curves.csv` and `evidence-onsets.csv`: source-bound evidence and
  no-extrapolation retention crossings.
- `study-results.json`: compact machine-readable design and primary results.
- `data-dictionary.json`: grains, fields, equations, and interpretation.
- `explore.sql`: DuckDB views and starter queries.
- `manifest.json` and `checksums.sha256`: provenance and integrity records.
- `independent-validation-report.json`: implementation-independent audit.

The five `.csv.gz` files are ordinary UTF-8 CSV streams wrapped in deterministic
gzip containers. DuckDB reads them directly through `read_csv_auto`; Python can
use `gzip.open`. The manifest records both each stored-byte digest and its
uncompressed CSV digest, byte count, compression level, zero timestamp, Python
version, and zlib versions.

## Reproduce and validate

From the repository root:

```powershell
python -B projects\harness-efficiency-study\scripts\test_pi_context_rot.py

python -B projects\harness-efficiency-study\scripts\run_pi_context_rot.py `
  --cost-bundle evaluations\harness-efficiency-study\20260904\pi-cost-elasticity `
  --evidence-csv projects\harness-efficiency-study\source\context-rot-evidence-20260904.csv `
  --spec-json projects\harness-efficiency-study\source\pi-context-rot-spec-20260904.json `
  --output-dir projects\harness-efficiency-study\artifacts\runs\pi-context-rot-reproduction

python -B projects\harness-efficiency-study\scripts\validate_pi_context_rot.py `
  projects\harness-efficiency-study\artifacts\runs\pi-context-rot-reproduction `
  --cost-bundle evaluations\harness-efficiency-study\20260904\pi-cost-elasticity `
  --report projects\harness-efficiency-study\artifacts\runs\pi-context-rot-reproduction-validation.json
```

The independent validator does not import the simulator. On the versioned
bundle it completed 5,116,530 checks with zero failures and zero warnings; its
report is bound to the manifest and checksum-inventory digests. All
six analytic completion and cost-per-completion contrasts fall inside their
fixed-seed paired Monte Carlo 95% intervals. Monte Carlo validates arithmetic
under the declared equations; it does not validate the equations against the
world.

Release validation on 2026-09-04 also passed 16 context-rot unit/oracle tests,
37 `simulation-data-lab` tests, 19 prior Pi cost-elasticity regression tests,
50,792 prior-bundle independent checks, Ruff formatting/lint, byte-identical
regeneration of all 16 generated artifacts, direct DuckDB reads of all five
large tables, pattern-ID validation, skill validation, skill independence, the
repository payload gate, and local skill synchronization. No command in this
release validation invoked Pi, Copilot, GPT-5.6, or another model/API. The
normally required isolated Pi forward test was intentionally not run because
the user expressly prohibited real Pi/model executions; the skill therefore
remains `validating` rather than being promoted to `done`.

## Inference boundary

This study supports or challenges context policies only under its declared
session, evidence-retention, context-decay, retry, and cost assumptions. It
does not establish an empirical GPT-5.6 context-rot curve, summary fidelity,
actual cache eligibility, or third-party 800K availability. Before adopting a
policy, run matched representative tasks with immutable external graders,
randomize evidence position and distractor density, log actual prompt/cache
buckets, and measure whether summary-induced failures persist across retries.
