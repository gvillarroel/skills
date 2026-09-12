# Local family baselines

Use this route when a dense genealogy looks like repeated rows of identical pairs. It refines the family-unit packing with source dates, complete label envelopes and local attachment space. It does not alter people, marriages, parentage, wording or category membership. For 30 people or fewer, start with the measured compact cohort route and use this refinement only for a visible problem.

## Prepare the data and hierarchy

Start with `design: editorial`, `mode: genealogy`, `layout: cohorts`; explicit integer `row` values; normal two-person `unions`; and any supported typed edges. Add a numeric `birth` field only when the source supplies it. A missing date stays missing. Dates printed in `detail` are text, not machine-readable chronology. A different numeric field can be selected with `--date-field`.

Separate three useful levels of information:

- Principal people: compact colored nameplates, with `detail_position: outside` and the supplied dates in `detail` below the name. For a substantial 1800 × 2700 poster, start around 11.8-unit names and 9.1-unit dates, then inspect at print scale. These dense sizes are inappropriate for a short family.
- Supporting people: plain names and subordinate dates. Keep their source category. A plain consort can have a different category from the neighboring principal person.
- Historical landmarks: source-supported founders, courts, territorial changes or consequential transitions. Use locally attached family pills, a larger name or a selected portrait. Put an explanatory territorial label near the branch that it explains. Do not turn every person into a landmark or fill unused areas with invented history.

Measure nameplate widths from both the name and the entire date caption. When using `text_width` from the bundled renderer, reserve at least 14 units beyond the measured bold name plus any portrait width, and 16 beyond the measured caption. Extra slack avoids a barely fitting caption wrapping because of fractional measurement. Prefer widths fitted to content over one width for all rulers. Reserve the full outside caption and portrait envelope for connectors. A selected portrait needs enough optical weight at its actual printed size; around 33–36 units can work on a dense poster, but inspect the asset itself.

For 31–100 people, write a data-first brief and omit page dimensions, generation bounds, coordinates, node widths, font overrides and repeated style assignments initially. The helper measures the busiest row and the complete labels with 18-unit names and 13-unit dates. Founding people receive larger nameplates; source-connected ancestors use compact nameplates with dates below; external partners and terminal relatives use plain names. Mark `emphasis: true` only for source-supported landmarks. These are initial structural treatments, not invented historical ranks. Explicit styles and dimensions are respected, so supplying a style for every person or arbitrary mural dimensions defeats these defaults. Inspect the first preview before making targeted overrides.

## Resolve the local arrangement

```sh
uv run --script <skill-dir>/scripts/space_family_branches.py draft.json --output brief.json --report spacing.json --local-labels
uv run --script <skill-dir>/scripts/render_chart.py brief.json --svg poster.svg --html poster.html --report layout.json
uv run --script <skill-dir>/scripts/audit_chart.py poster.svg --source brief.json --report browser.json --png poster.png
```

Use distinct input and output paths. The helper keeps the horizontal cohort packing and writes an `authored` source with resolved coordinates. It preserves source record order and all identity, date, category and relationship fields. Audit against that resolved source, which is the editable deliverable.

Within each generation, the preferred baseline follows a family unit's mean known birth date relative to that generation's median. A constrained least-squares fit then reserves label and portrait space, partnership alignment and a complete departure gutter below each parent. Undated families prefer the original cohort baseline. This is **schematic arrangement, not a numeric time scale**. State that in the reading note. Never change the dates to make the composition fit.

The default date scale is derived from the available vertical span and known date range. `--date-scale` supplies units of preferred displacement per source year; use it only after inspecting a concrete problem. A larger value can increase detours even while breaking monotonous rows. Zero is valid and retains only the geometry constraints.

`--local-labels` deliberately places anchored `kind: pill` annotations immediately above their named person, clamped inside the paper, and reserves their complete text box. Omit that flag to preserve supplied `dx` and `dy`. Do not use large horizontal offsets that name an unrelated neighbor. Headings and their icons still need an editorial pass after fitting; they are not part of the optimization. The renderer positions a heading icon above its complete multiline text block, and the browser audit checks it against text and paper boundaries.

## Inspect and repair

Open the PNG. Compare the whole page and dense details against a relevant reference at matched display width. Trace at least one intermarriage, a large sibling group, a short terminated line and an uncertain relation. Look for long colored contours dominating the names, shared routes that resemble false joins, and unused space beside a crowded union. A smaller crossing count does not establish an easier read.

Keep fewer bends and legible destinations ahead of decorative variation. For remaining difficult junctions, edit the resolved authored coordinates as a local group and reserve explicit corridors, then render and audit again. Preserve all people and facts. Do not repeatedly increase the canvas or shrink typography to evade a local layout failure.

The helper rejects multiple partnerships, nonnumeric source dates, nonadvancing parentage, inconsistent partner offsets, absolute route coordinates, fixed insets and unanchored annotations. Compose those structures deliberately after resolving the ordinary branches, or use authored placement from the beginning. A capacity failure means the complete content does not fit the chosen span; choose a justified larger span or recompose the region. A clean fit and browser audit are geometry evidence, not proof of visual parity.
