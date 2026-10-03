# AA-anchored, one-factor cost study

This exploratory study replaces the previous presentation narrative, not the
previous experiment. It preserves the older bundle and uses a fresh mathematical
study at `artifacts/aa-ofat/study-v1/`. No Pi, Copilot, model inference or modeled
tool execution was performed. Public documentation retrieval and Google Slides
editing are authoring activities, not executions of the simulated system.

## Evidence and transfer

Read-only snapshots were taken on 6 September 2026 from
[Artificial Analysis Terminal-Bench v2.1](https://artificialanalysis.ai/evaluations/terminalbench-v2-1)
and the [model overview](https://artificialanalysis.ai/models). The published
JSON-LD `Dataset` blocks expose average answer/reasoning output, pass@1 and
average cost components. The study joins these by exact model/effort label;
it does not join models merely by family name. Six configurations have the
needed fields in the retrieved public chart slices. These slices are not the
complete AA leaderboard. The recorded HTML digests and extracted data are under
`artifacts/aa-ofat/source/`.

Terminal-Bench v2.1 comprises 89 tasks with pass@1 averaged over three repeats
per task, using Terminus 2. The mean output is a whole-task mean, not a per-call
budget. The Intelligence Index weighted task mean is retained separately. Its
score is not a probability of task success. No raw per-task token variance or
token/success joint distribution was present in the retrieved aggregates; this
is not a claim that no such data exist anywhere. Repeated tasks are clustered;
the study does not fabricate a binomial CI by treating all 267 trials as IID.
Small benchmark-score gaps are not claimed statistically significant.

Prices for the synthetic ledger follow the documented
[GitHub Copilot token schedule](https://docs.github.com/en/copilot/reference/copilot-billing/models-and-pricing).
Luna's Copilot long tier starts above 200,000 input tokens. The
[OpenAI API model page](https://developers.openai.com/api/docs/models/gpt-5.6-luna)
documents a different 272,000-token threshold for its direct route. The synthetic
main study uses the Copilot schedule and treats route threshold as an explicit
sensitivity input. AA-native benchmark cost comparisons remain separate from
this synthetic six-call ledger. No subscription invoice is inferred from token
value alone.

## Frozen design

The declared core has 38 scenarios, two workload design points, and exactly one
deterministic evaluation per cell: 76 cells. Each non-baseline scenario differs
from its baseline in exactly one primitive parameter, checked programmatically.
The inventory includes 36 implemented inputs plus ten unresolved mechanism
groups. It is an auditable scope review, not a certificate of exhaustiveness.

The short baseline uses Luna max's AA mean of 24,120.0674 output tokens and
0.808988764 pass@1 as explicitly unvalidated workload proxies. Its harness
structure is assumed: 4,000 system tokens, 2,000 schema tokens, 1,000 initial
user/background tokens, five 2,000-token tool results and six model calls.
The total output is spread evenly over calls; answer tokens persist while
reasoning tokens do not. The one-tool-removal experiment holds total task
output fixed, so it measures less input/replay, not an assumed output saving.
Batching retains every tool operation and applies only to independent tools.

The long design point uses 39 tools with 20,000-token results and 160,000 total
output tokens. Those sizes are assumptions, not AA measurements. Every main
and compaction request has mutually exclusive uncached/read/write input buckets
and a separately billed output bucket. The whole-request pricing tier is
selected from actual request input. A cap is a trigger: the input that triggers
the compaction may already exceed the tariff boundary. A summary is paid and
the next request rebuilds its explicitly declared cache state.

Exact expectations have no Monte Carlo error. This does not eliminate input or
structural uncertainty. The six core hypotheses use exact signed differences
with zero practical threshold; equality supports non-increase/non-decrease but
does not imply economically meaningful improvement.

## Stochastic and structural extensions

The extension plan was frozen in the spec before execution. Token variability
uses Gamma distributions with shape `1/CV^2` and scale `mean*CV^2`, so SD is
exactly `CV*mean` by construction. CV values 0.25, 0.50 and 1.00 are assumptions,
not estimates inferred from the AA mean or Intelligence Index. A lognormal
alternative preserves the same mean and SD but changes tails.

There are 20,000 draws per cell, two independent seeds for the Gamma cells,
and separate monthly calculations at 1,000 and 1,000,000 tasks. The sum of IID
Gamma output tokens is sampled directly; no million-row target job is executed.
In this dispersion experiment only output billing changes. Input replay, price
tier and success are deliberately frozen. Quantiles are predictive under this
restricted model; they are not confidence intervals on AA or operational budgets.
Shared lognormal month shocks challenge IID averaging separately. The first
seed's 1k-task P95 ranges from $37.08 to $38.23 as CV rises; the second gives
$37.08 to $38.26. This precision is adequate for that illustrative ordering,
not for fine-grained tail guarantees. Mean MCSE is retained in the CSV.

The context extension executes 1,152 cells varying onset, decay, fidelity,
average-versus-critical fact loss and smooth-versus-cliff degradation across
six compaction caps. The retry extension tests caps and persistent-failure
mixtures. Fallback recovery is a conditional probability given Luna failed,
not Sol's marginal pass@1. A perfect validator and unchanged conditional
fallback cost are explicit simplifying assumptions.

Not all planned sensitivity dimensions were used in the extension: successDelta
and failure-loss grids remain deferred. The core p-only scenarios and loss
activation test do not substitute for those grids. Early/late criticality,
cache-write summary input, task-stratum mixes, validator errors, and empirical
success-token dependence are also unresolved. No claim of global or production
robustness is made.

## Verification and artifacts

The preflight verifies a one-write hand oracle, a system-prefix marginal oracle,
45 independently enumerated retry cases, 36 active parameter perturbations,
and all 76 ledger invariants. The core skill runner and independent bundle audit
pass with zero failed/invalid runs and 1,292 numeric outcomes. A separate
200,000-task Bernoulli simulation checks exact retry expectations. Extension
CSV values are checked against persisted core outcomes, exported to SQLite, and
digest-pinned. Quantile results and shared shocks are illustrative and carry
the narrower uncertainty scope above; the core audit does not certify them.

Use `extension/ofat.csv`, `extension/ledger.csv`, `extension/token-spread.csv`,
`extension/monthly-spread.csv`, `extension/context-quality.csv`,
`extension/routing.csv`, and `extension/exploration.sqlite` for exploration.
Core normalized outcomes, units, plan, model review, uncertainty contract,
digests, and hypothesis calculations are also retained in the bundle.

An additional post-run SciPy distribution audit passed 162 CDF/quantile checks
against the assumed Gamma and lognormal laws, with a maximum CDF error of
0.00945. Its DKW union-bound tolerance is a simulation diagnostic, not evidence
of production calibration. The diagnostic was selected after generation and is
not relabeled as a preregistered policy test.

The existing Google Slides deck was updated in place from its native exemplars.
Thirty-two slides contain five native tables and editable native bar/label
shapes; chart values are not linked to a Google Sheet. Narrative text is not
rasterized. Every slide was rendered and visually inspected. The platform's
POSIX-only export helper was not runnable on Windows, so the established bounded
inline-PDF compatibility route and bundled Poppler were used with the same
read/parse/render/audit artifacts.

The old 16-slide content was replaced in the same presentation, with its full
pre-edit JSON snapshot and prior PDF retained locally. No sharing policy was
changed and no repository push was performed in this revision.
