# Input contract

The builder accepts UTF-8 JSON with this shape:

```json
{
  "title": "Organization atlas",
  "description": "Reporting lines with comparable attribute views.",
  "entityLabel": "people",
  "provenance": "Synthetic demonstration; no real employee data.",
  "dimensions": [
    {"key": "leadership", "label": "Leadership", "type": "categorical", "categories": ["L1", "L2", "L3", "Individual contributor"]},
    {"key": "contract", "label": "Contract", "type": "categorical"},
    {"key": "tokens", "label": "AI tokens", "type": "numeric", "unit": "tokens", "period": "2026-08", "aggregation": "sum"}
  ],
  "nodes": [
    {"id": "ceo", "parentId": null, "label": "Chief executive", "values": {"leadership": "L1", "contract": "Permanent", "tokens": 5000}},
    {"id": "eng", "parentId": "ceo", "label": "Engineering director", "values": {"leadership": "L2", "contract": "Permanent", "tokens": 12000}},
    {"id": "dev", "parentId": "eng", "label": "Platform engineer", "values": {"leadership": "Individual contributor", "contract": "Contractor", "tokens": null}}
  ]
}
```

## Identity and structure

- Exactly one root has `parentId: null`. Every other parent must exist. IDs and dimension keys are nonempty strings and unique in their domains. Keys/IDs are looked up as data, never as executable code or CSS selectors.
- Every node represents one entity and contributes one to subtree size, including managers. Preserve input sibling order across all lenses and focus states.
- A manager is a record, not a second copy of their team's aggregate. The source must contain individual, exclusive measurements before using `aggregation: "sum"`.
- Flat CSV sources should be normalized once: map identity, parent, label, and chosen dimensions; turn blank numeric cells into null. Preserve IDs such as `0012` as strings. Do not guess whether a preaggregated cost or token column is individual.
- Reject duplicate IDs, cycles, forests, missing parents, missing labels, non-finite or negative numeric values, and inconsistent descriptors. The current runtime accepts at most 20000 records and 64 reporting edges per path. This is a validation limit, not a claim that all marks remain readable at that scale.

## Dimensions

- Categorical values are nonempty strings or null. Optional `categories` fixes the global category order and must contain every observed non-null value. Without it, first occurrence order becomes the global order. The current palette supports up to eight categories per lens; use an explicitly documented grouping or a different rendering if more are needed. Do not silently merge categories.
- Numeric values are finite nonnegative JSON numbers or null. `unit` and `period` are required nonempty strings. For timeless quantities use an explicit period such as `Snapshot 2026-09-25`.
- `aggregation` is `none` (default) or `sum`. Rates, percentages, averages, cumulative rollups, and overlapping totals should use `none`. The builder cannot determine from values whether a source is already aggregated; establish that from source documentation.
- Missing or omitted keys become null. Zero is a measurement and gets a numeric color. Missing values get a gray hatch and an explicit label. Subtree sums retain known-record coverage; partial sums are labeled as observed, not complete totals. An entirely missing subtree stays null.
- Categorical lenses always show the node's own attribute. Numeric lenses can show individual values, or additive subtree sums including the node. L1/L2/L3 are attributes, independent of ring depth.

All human-readable input text is displayed as text. The JSON payload escapes HTML-closing tokens. HTML output is a local, inspectable file; no upload or server is needed.
