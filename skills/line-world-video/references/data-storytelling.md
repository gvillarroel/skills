# Data storytelling

First write the viewer's question and the data's grain. State units, period,
population, denominator and whether the numbers are measured or illustrative.
Keep missing values missing; do not use zero as an absence marker. Do not infer
causality from correlated motion or invent an improvement claim.

| Viewer question | Representation | Linked-table behavior |
| --- | --- | --- |
| Which value differs most? | Sorted horizontal bars or dots with a shared zero baseline | Highlight the row, exact value and its matching mark |
| How did one entity change? | Paired dots, dumbbell or before/after bars | Keep both values visible; annotate the signed change with units |
| How does a quantity evolve? | Fixed-domain line chart with labelled time axis | Highlight the row and matching timestamp; preserve gaps |
| How do two measures relate? | Scatterplot with units on both axes | Move focus to the entity's point; label the selected point |
| How is a total divided? | Stacked bar or at most five meaningful treemap groups | Retain parent totals and denominator; never infer a time trend |
| What connects these objects? | Node-link or Mermaid flow, state or sequence diagram | Bind the same entity IDs to diagram nodes and related rows |

Prefer table left / chart right for a few exact records. Let the chart answer a
different question from the table: structure, change, rank or trend. Use a
single focus event `{rowId, metric, phase}` to update the row, plotted mark,
guide dot and value annotation together. Leave nonfocused rows visible and
quiet. A moving pointer should explain what it refers to, not obscure digits.

Reading budget: allow approximately 1 second to orient, 2–3 seconds per
meaningful comparison and 2 seconds to inspect the conclusion. Increase holds
for unfamiliar units, six or more rows, or several simultaneous curves. Avoid
switching chart types while the viewer is still reading a highlighted value.
Keep axes fixed when moving between rows so scale changes do not suggest
changes in the data. Never encode a smaller value using a longer mark.

The starter's synthetic case compares cycle time before/after across work
stages. Selection visits every row, maps paired values to the same fixed scale,
then reveals histories and a small categorical subdivision. Histories must
have equal lengths and nonnegative finite values. A history index is an
observation, not a calendar date unless supplied data establishes that mapping.

Keep `schemaVersion: 1`. Set `dataStatus` to exactly `synthetic` for invented
or illustrative values, or `supplied` for user-provided records; illustrative
user data can retain `synthetic`. Put explanatory wording in visible copy, not
in a new status enum. Preserve `copy.entity` and `copy.observations` as short
semantic labels. The renderer adds a small provenance tag for synthetic data.
Visible titles are absent by default. Only an explicit user request should
populate `presentation.contextLabels`, for example `{"compare": "Queue times"}`.
Keep each requested label to 1–6 words and at most 48 characters. Extra legacy
headline/slogan fields in `copy` do not authorize their display.
Each row needs `id`, `label`, `before`, `after`, and optionally `trend`; IDs are
unique lowercase hyphen-case. `palette` is exactly `colorset1` or `colorset2`,
and colorset2 requires a nonempty `paletteReason`.
