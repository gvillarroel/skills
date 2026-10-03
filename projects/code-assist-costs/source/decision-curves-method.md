# Decision curves presentation

## Aim and boundary

Re-express the September 6 AA-anchored study as interactive, one-decision scenes inspired by the read-only blog cost-efficiency slides and replayable alternate deck. The blog supplies visual composition, not numerical evidence. All code-assist events remain mathematical. Do not launch Pi, Copilot, agents, inference APIs, or their tools.

This is a fresh exploratory extension, not confirmation of the previous selected 180k policy. The accounting engine remains the reviewed `aa-ofat-model.py`. The parent experiment and its evidence stay immutable. Use the parent variable inventory, revising treatment labels to match the new parameter ranges. Every downstream mediator remains explicit.

## Frozen experiment

Use one deterministic replication per scenario and each of the parent short/long workloads. Generate these families before executing them:

- System size: 4,000 to 14,000 tokens, steps of 250. Only `system_tokens` changes.
- Tool count: baseline minus five to plus five calls, integer steps. Total task output and success stay frozen.
- Output: 50% to 150% of baseline, steps of 2%. Reasoning fraction stays fixed.
- Cache hits: 0% to 100%, steps of 1%. Compare no cap and a fixed 180k cap separately. Hit fraction represents an expected eligible-prefix fraction, not a measured TTL process.
- Compaction cap: 50k to 400k, steps of 1k. Summary length 20k, cold compactor, cold rebuilt prefix, lossless quality. Report all tied minimum grid ranges, never a universal optimum. Check a separately declared 500-token grid for resolution sensitivity.
- Fidelity: 90% to 100%, steps of 0.1 percentage point. Compare no cap with 180k under fixed beta 0.2, onset 100k. The primary link applies independent survival of ten critical facts through every compaction as an odds multiplier. The rival uses average per-call fidelity. These are assumptions, not empirical context-rot fits.
- Degradation slope: beta 0 to 1, steps of 0.01, fixed onset 100k and critical-fact fidelity 99%. Compare no cap and 180k.

The core contrast is +1k system tokens against baseline. Other curve crossings and minima use an independently checked extension, with exact evaluations at crossing brackets. For discontinuous policies, show sampled steps and search resolution. Do not smooth across jumps. For smooth crossings, bisection tolerance is 1e-10 in the x unit and 1e-7 USD/task residual.

## Analytic presentation extensions

Freeze before computing:

- Session trajectory: cumulative token cost and active main-call context, calls 1 through 40, no cap versus 180k. Charge compaction before the corresponding main call. This is simulated sequence, not historical provider data.
- AA model selection: cheapest of the six retained configurations meeting a quality floor from 75% through 95%. Use the published cost/pass@1 aggregates as unvalidated task-distribution proxies. A missing qualifying configuration is a valid result. Model selection changes a bundle, so label it as a selection scenario, not OFAT.
- Failure loss: Luna max versus Sol xhigh, loss L from 0 to 10 USD per failed task. Objective `C + (1-p)*L`. No additional human-work, latency, validation, or setup expense. Calculate their analytic crossing and verify both sides.
- Retry persistence: K=1,2,3, rho from 0 to 1, 95% completion floor. Same-cost retries and the parent persistent-failure mixture. Preserve previous enumeration/Monte Carlo evidence and independently enumerate boundary and intermediate cases here.
- Escalation recovery: Luna failure followed by Sol xhigh. Recovery r from 0 to 1, 95% completion floor, perfect validator. Sol conditional cost equals its unconditional mean by assumption. Neither AA pass@1 nor its Intelligence Index identifies r.
- Monthly variability: independent task output CV=1, common monthly output multiplier CV=0 or 0.3, N from 1k to 1m. Input bill is fixed. Show relative standard deviation, not a percentile or a confidence interval. For independent positive multipliers with unit mean, output variance ratio is `1/N + shockCV^2 + shockCV^2/N`. This is an exact moment calculation and needs no distributional noise. Do not infer empirical standard deviation from AA means.

## Interpretation and challenge coverage

The parent review covers outcome backtrace, lifecycle, dependence, heterogeneity, time/scale, accounting, rival mechanisms, and evidence gaps. This extension tests grid resolution, quality-link reversal, cache-policy interaction, failure-loss reversal, and persistent retries. Easy/hard task mixtures, early/late critical information, direct cache-write compactor pricing, imperfect validators, token-success dependence, capacity, plan allowances, taxes, and future tariffs remain unresolved or outside scope. A monthly token-value extrapolation is not an invoice.

Computational precision does not measure confidence that the system model is true. Deterministic cells have no Monte Carlo error. AA aggregate means are evidence, operational transfer is assumed, quality links are sensitivity mechanisms, and the inventory can still omit relevant factors.

## Visual contract

One dominant line chart or two aligned sequence plots, one concise claim, one essential caveat. Match the blog's large-chart/small-copy composition, keyboard navigation, replay and scrub controls. Use a standard red/neutral palette for clear policy distinction. Sources and full variable inventory live in expandable notes. Native browser ranges expose the selected parameter and update values, guide, point, and decision together. Reduced motion shows the settled state. Bundle D3, data, and runtime in one offline HTML file. Supply editable sources and exportable SVG charts.
