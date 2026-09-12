# Compose an institutional history from its records

Use this route for roughly 31–100 institutions when the source supplies names, dates and relationships but no required coordinates. The composer allocates width to active stages and moves connected records toward one another. It avoids asking the author to guess dozens of relative coordinates before seeing a first page.

Use [packed stories](packed-stories.md) when the user supplies a deliberate relative arrangement. Use authored placement for fixed coordinates, a dense mural, partnerships or a complex context inset. Do not reinterpret supplied positions as disposable hints.

## Prepare a data-first draft

Set `design: editorial`, `mode: lineage`, and `layout: branches`. Supply `id`, `title`, a visible `source_note`, category `groups`, individual `nodes`, and typed `edges`. Each node needs its stable `id`, exact `label`, and source-defined `group`. Keep a known founding or reorganisation year as numeric `founded`; use `date_label` for the exact printed wording and `detail` for the required explanatory note. Unknown or approximate dates must retain their supplied wording.

Omit coordinates, rows, page dimensions, font overrides, absolute routes and node widths for the first preview unless the user explicitly supplies them. Mark a few consequential institutions with `emphasis: true`. An optional meaningful `icon` can distinguish a landmark. The composer retains every required name, note, year, category and relationship; it does not create missing facts or choose notes to hide.

For example, a source record can be:

```json
{"id":"library","label":"United Public Library","group":"civic","founded":1840,"date_label":"1840","detail":"Two collections and staffs unite","emphasis":true,"icon":"book"}
```

Connect its two stated predecessors with two `branch` edges. An intellectual or technical contribution uses `influence`. These have different meanings and may use different attachment sides. Two incoming links never justify changing the supplied category.

If every record has a finite numeric `founded` year, source order helps place later institutions in later parts of the composition. Otherwise the default uses causal depth. Optional `branch_order: causal` explicitly selects causal order; `branch_order: founded` requires complete numeric years. This remains a schematic lineage: order and attachment space determine distances, **not a common numeric time scale**. Use the timeline workflow for exact elapsed-time comparisons.

## Compose and export a consistent poster

For a normal poster bundle, use one command:

```sh
uv run --script <skill-dir>/scripts/create_branch_poster.py draft.json --output-dir result
```

It writes `result/source.json`, `poster.svg`, `poster.html`, `layout.json`, `browser.json` and `poster.png`. The source is the **composed, render-ready brief**, with the exact coordinates and routes used by that SVG. The command checks the original supplied fields and audits these final file paths. It supplies the editorial/lineage/branches profile when those fields are absent; explicit conflicting profiles remain errors. Open the final PNG and a dense detail, then write the user's requested review. Keep the original `draft.json` outside the bundle. Do not replace the delivered `source.json` with that draft after rendering.

When the user requests different filenames or a specific intermediate editing step, use the individual operations below with those exact final paths. Audit the delivered source and SVG again after any copying or later edits:

```sh
uv run --script <skill-dir>/scripts/compose_branching_history.py draft.json --output brief.json --report composition.json
uv run --script <skill-dir>/scripts/verify_branch_source.py draft.json brief.json --report source-check.json
uv run --script <skill-dir>/scripts/render_chart.py brief.json --svg poster.svg --html poster.html --report layout.json
uv run --script <skill-dir>/scripts/audit_chart.py poster.svg --source brief.json --report browser.json --png poster.png
```

Use the exact output paths requested by the user. Keep `draft.json` as the original data-first input. The helper writes an authored `brief.json` containing measured readable typography, complete content envelopes, the category key, resolved coordinates and calculated corridors. It first composes structural descent, then tries lateral attachments for influence. This avoids forcing every influence through a bottom-to-top connection before side ports can be chosen.

Use the bundled source check before rendering; put its report outside an exact final deliverable directory unless requested there. Layout resolution adds coordinates to records, `via` bends and ports to edges, and offsets to captions. Whole-object or whole-array equality therefore gives false alarms. The source check matches stable identities, requires every original item and supplied field, and allows additional layout fields; it does not replace the independent SVG audit or visual inspection.

The helper tries five attachment pairs in nearby corridors first. If none works, it broadens the search. This is a bounded preference for local connections, not a claim of a globally optimal layout; difficult large graphs can still take substantial time. A valid path is a proposal for visual review. The report records selected ports and whether each search needed the broader pass.

Declare meaningful local family captions before composing. An anchored `pill`, illustrated `heading`, or source-bound `landmark` is measured together with its institution, including wrapped text and the complete illustration. For example, `{"node":"library","kind":"pill","label":"PUBLIC READING TRADITIONS","width":280,"size":16,"group":"civic"}` gives the local branch a name. Omit `dx` and `dy` for a title immediately above its institution. Explicit offsets are retained and must clear that institution and its other captions. A caption can be wider than its name panel: the composer allocates the larger footprint without widening the panel or changing the text size. It also protects the caption from unrelated routes; a family pill may sit on its own incoming trunk. The resolved source retains these reservations when rendered again.

Explicit page dimensions are honored only when complete records fit. A too-small page produces an explanation instead of shrinking text or losing records. Cycles, unknown endpoints, partnerships, fixed insets and prescribed coordinates need their appropriate workflow. Do not repeatedly retry an unchanged structural error.

## Compare and refine the actual image

Open the final PNG. Check the opening story, a merger with two parents, the widest active group, the end of a short branch and the longest influence path. Compare the whole page and a dense detail with the relevant reference at equal display width. Look for meaningful changes in color area, larger landmarks and smaller supporting names, rather than an evenly weighted grid.

Inspect `unrelated-shared-run` warnings. Two almost coincident paths can look joined even when their center coordinates differ. The browser check uses visible SVG strokes and their widths; automatic routing leaves four units beside unrelated parallel runs. Authored paths retain their coordinates and can still need a local shift or different attachment. [Influence routes](influence-routes.md) explains the refinement helper.

For a content or emphasis revision, edit the retained data-first draft, compose again and inspect the new output. For a specific difficult neighborhood, edit the authored result and remove only the stale routes affected by the move; recompose influences and audit the final source. Do not replace the whole graph with a larger empty page to fix one corridor.

A source with one long common-origin chain still has one long common-origin chain. Choose meaningful supplied context for adjacent open space or a different demonstration subject when allowed. Do not manufacture branches, geographic prevalence or decorative statistics to fill the page. A smaller canvas, correct source inventory and clean audit do not establish visual parity with UsefulCharts.

For a useful opening explanation or source-derived count overview, continue with [context insets](context-insets.md) on the complete authored result. It keeps the branch composition intact while measuring and reserving the new contextual footprints.
