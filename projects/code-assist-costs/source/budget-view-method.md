# A $200 monthly token budget

This is an exploratory presentation transform of the frozen, validated
`decision-curves-v1` data, not a new target-system experiment. It changes the
decision unit from dollars per million tasks to use affordable within $200.
The underlying request ledgers, dated prices, benchmark aggregates, quality
mechanisms and unresolved candidate inventory remain unchanged.

## Frozen display contract

- Budget: $200 USD per month, entirely available for metered token charges.
- Mean-rate task capacity: budget / provider spend per submitted task.
- Mean-rate successful-task capacity: budget * completion probability /
  provider spend per submitted task. Spend on failed attempts remains included.
- Whole task-run planning figures round capacity down. Success estimates round
  to the nearest integer and retain an approximate label. Neither is a quota
  promise or the expectation of a finite-budget stopping process.
- Curves retain full precision and display continuous mean-rate equivalents.
  Slider selections use source cells or interpolate the underlying cost before
  taking its reciprocal. A displayed line between cells is only a guide.
- Same-use spending compares each policy at floor(200 / baseline cost) tasks.
  Additional capacity compares the difference between whole planning figures.
- The short workload has five tool calls, six model calls, 2,000 tokens per
  tool result and 24,120 total answer/reasoning output tokens per task.
- Long workloads have 39 tools, 40 model calls and 160,000 output tokens per
  task. Their counts must never be compared with short-workload counts.
- Model selection uses AA benchmark mean task costs and success point estimates,
  not the custom short ledger. Keep that distinct accounting basis visible.
- The calendar illustration assumes five identical long tasks per day for a
  30-day month. It is a synthetic mean-cost projection, not observed history.
- A reserve is money deliberately left unplanned: usable = 200 - reserve.
  Maximum affordable mean-cost increase = 200 / usable - 1, ignoring rounding.
  The reserve is a what-if, not a calibrated percentile or confidence guarantee.

## Review of the budget framing

Included: token costs, tool/context/cache policy, failed-attempt spending,
quality-adjusted throughput, model-specific token and success aggregates,
retry dependence, fallback recovery and a visible planning reserve.

Fixed: $200, the separate task definitions, benchmark snapshot, token prices,
and each scene's named comparison. Settings reset between scenes; separate
savings must not be added as though a combined policy was simulated.

Unresolved: a real $200 subscription's included quota, credits, restrictions,
taxes, actual task mix, cost/success dependence, price changes, rate limits,
joint stopping-time distributions and human labor. The wider 46-candidate
inventory is retained. This review does not establish exhaustive discovery.

No distribution of costs is identifiable from a mean alone. B / E[C] is a
planning rate, not E[number completed before the budget runs out]. No success
probability or token variance becomes empirical through this transformation.
Quality probabilities transferred from AA or the context model remain assumed
for the user's own tasks.

## Verification plan

Verify budget conservation, inverse cost/capacity ordering, the exact $0.00035
per-task system-token increment, discrete task counts, and quality/cost
identities for every source row. Check zero-budget, zero-success, invalid-cost,
reserve and rounding boundaries. Recompute the fidelity decision reversal at
95% and 99%, retry independence and persistence limits, and the unchanged
conditional recovery threshold. Verify the 30-day illustration independently.
Preserve the original study and first published Site version.

Budget CSVs and a data dictionary support exploration of the transformed units.
Numerical and browser checks certify implementation, not real-world adequacy.
