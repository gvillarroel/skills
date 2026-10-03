# Knowledge density at the reference level

The default target is at least the useful knowledge density of the relevant UsefulCharts reference. A sparse chart is not an accepted substitute for that target, even if its geometry is clean. Treat this as part of information sufficiency, editorial selection and final critique.

## Select and inspect the actual reference

Use the supplied reference first. For the supported families, the comparison sources are [European Royal Family Tree (West)](https://usefulcharts.com/products/european-royal-family-tree), [Christian Denominations Family Tree](https://usefulcharts.com/products/christian-denominations-family-tree), and [Timeline of World History](https://usefulcharts.com/products/timeline-of-world-history). Inspect the actual full poster and its dense details. A product thumbnail, advertised record count or palette is not a density specification.

Compare at the same displayed or printed poster area and at a readable detail scale. Inspect the upper, middle and lower thirds separately. Do not judge the page only from its busiest pocket. The reference chronology becomes substantially denser toward recent periods; the institutional reference combines a branching history with quantitative and geographic context; the genealogy encodes supporting people, partnerships, dates and family membership together with focal rulers. Preserve these layers of useful information rather than only the silhouette of the boxes.

## Count useful content consistently

Use the same definitions for reference and candidate. Retain a census ledger or annotated review so counts can be checked against the actual image and source. Count each distinct displayed claim once:

- `named_records`: identifiable people, institutions, periods or equivalent subject records. Repeated names, headings and legend entries are not additional records.
- `typed_relations`: distinct source-backed descent, partnership, succession, influence, division or union assertions. A shared parentage assertion is one parent-set-to-child relation; a multi-input institutional merger is one union assertion. Do not count each elbow or painted line fragment.
- `temporal_anchors`: a distinct date, life/reign/operation interval or dated event attached to a record. Count a repeated date label once; ruler ticks and grid labels do not add knowledge. Apply the same interval convention on both sides.
- `context_statements`: distinct relevant explanatory or comparative claims, including meaningful role, cause, consequence or quantity information. A paragraph may contain several claims only when the ledger identifies them separately. A copied label, decorative image, generic slogan or repeated pictogram does not add a claim. Count a sourced chart value once, not once per repeated icon used to represent it.

Require source support and legibility before counting a candidate claim. Keep numerical comparison separate from the semantic review: a larger count of invented, irrelevant or unreadable material cannot meet this target. Do not discount real repeated relationship types simply because historical successions have similar structure; assess whether each assertion adds a distinct supported fact.

Use a full-body census for a numerical pass. If small raster lettering prevents reliable counting, record uncertainty or `null` instead of guessing. OCR character counts, detected text boxes, ink coverage, colored area and page occupancy are screening aids only. OCR can miss most small genealogical names while recognizing larger chronology prose. It cannot certify knowledge density, and a low OCR count must never lower the minimum.

## Apply the minimum independently to each layer

Create a reference census and candidate census using [the census template](../assets/templates/density-census.json). Preserve its field names, including `image_sha256` and `ledger`, so the evidence remains usable by the comparator. Enter an exact count as `[n, n]` or a justified interval as `[lower, upper]`; use `null` while a count remains unknown. Identify the reference family and counting protocol, record the reviewed image hash and cite the ledger. Use the same whole-poster comparison basis. Resizing the page or font does not increase the number of useful claims available to a reader in that comparison.

```sh
uv run --script <skill-dir>/scripts/compare_density.py reference-census.json candidate-census.json --report density.json
```

Use this helper for supported census comparisons, including review-only tasks. Deliver its generated report unchanged rather than inventing a different JSON decision schema. The helper requires the candidate's lower bound to meet or exceed the reference's upper bound for **every** layer. Set each repair target to that upper bound and use the reported conservative shortfall; interval overlap is insufficient. Extra names cannot compensate for missing relationships or context. Unknown counts, unreviewed evidence and failed legibility remain unresolved; they cannot produce a pass. The helper checks the declared census and does not independently establish the truth of its historical claims or the completeness of a human count. Verify those against the rendered image and source.

Read `status`, `passes_measured_floor`, each layer's `shortfall`, and `pending` in the report. A successful command only means the comparison completed. Add `--require-pass` for a CI gate that exits nonzero on a shortfall or incomplete evidence.

## Repair a density shortfall

First recover useful source material lost in selection: necessary intermediates, collateral branches, dates, roles, causes, consequences and comparisons. Research additional relevant evidence within the requested scope when necessary. If the scope cannot support the required density, report the exact shortfall and keep the full-density poster pending; do not silently switch to a small diagram or claim that a smaller canvas solves the content deficit. Honor an explicit request for a miniature or limited-data diagram, but describe its actual scope rather than claiming reference-level density.

Then improve the composition: reclaim space after terminated branches, shorten avoidable detours, fit captions with their owners, and use compact layered labels with distinct emphasis. Preserve readable type and honest numeric time. Removing useful facts, shrinking text until it is unreadable, stretching colored ribbons or adding generic icons does not repair knowledge density.

After each structural revision, repeat the source inventory, census comparison and full-page/detail inspection. Both the overall amount of useful knowledge and its distribution must be at least as convincing as the chosen reference. A numerical census pass is one acceptance condition, not proof of good composition or visual indistinguishability.
