# Give an open origin area useful context

Use this route when an institutional lineage has a small ancestral story and meaningful empty pockets beside it. Keep the complete graph, readable type and real branch structure. Add an inset only when its information helps the reader: a short source-backed explanation, an illustrative object, or counts of records actually shown. A map needs supplied geographic assignments; a blank area does not justify invented geography or statistics.

## Compose the history first

For a medium data-first history, run the normal branch composer without fixed insets. Open its PNG and inspect the resolved node envelopes and routes. Choose a clear pocket inside the paper, usually beside the opening story. Use the complete authored result for the next step; keep its measured font sizes and all supplied facts. Do not restart with smaller labels merely to make room for context.

Add `story` or `counts` entries to its `insets` array. Boxes are absolute `[x, y, width, height]` in source SVG units. Avoid nodes, the category key, existing insets and captions. The new inset boxes reserve complete regions for routing. Keep the existing key unless the count inset displays every necessary group label and color; if replacing that redundant key, remove `_cohort_key` and set `legend: false` in the authored source.

The dimensions below illustrate a pocket; choose actual coordinates and size from the reviewed page.

```json
{
  "id": "workshop-roots",
  "kind": "story",
  "box": [80, 180, 330, 245],
  "title": "From workshops to readers",
  "text": "Two workshops combine in the common press. Later branches serve science, schools and public readers.",
  "source_nodes": ["first-workshop", "second-workshop", "common-press", "school-press"],
  "icon": "illustration-printing-press-bookman",
  "art_width": 90,
  "art_height": 152,
  "title_size": 17,
  "size": 14
}
```

Replace the sample prose and IDs with the supplied history. `source_nodes` binds the explanation to existing records; it does not prove that arbitrary prose is historically true. Preserve exact user-provided text. When authoring new prose, state only supported facts and distinctions. Image provenance and dates remain separate from the chart's fictional or historical event.

The story measures its complete title, wrapped paragraph and optional image. Title size defaults to 17, paragraph size to 14 and image width to 90 units. Image height defaults to its width; specify a taller viewport for an appropriate source illustration. The renderer preserves a source illustration's aspect ratio. Original vector devices use the requested dimensions, so prefer a square viewport for them. Direct rendering rejects a too-short box; the composition helper below can enlarge it without shrinking content.

```json
{
  "id": "record-counts",
  "kind": "counts",
  "box": [1260, 175, 630, 240],
  "title": "Institutions represented in this history",
  "groups": ["crafts", "books", "science", "education", "arts", "news", "digital"],
  "columns": 2
}
```

Use the source's real category IDs. Omit `groups` to include every category in source order. The count inset derives every number and building-shaped mark from the complete `nodes` array: one mark represents one institution shown. It is neither population nor market share. Zero-count categories remain explicitly zero. One, two or three columns are supported; each needs at least 150 units of width. Labels wrap, marker rows follow actual counts and the required height is measured. Default title and label sizes are 17 and 12. The older `isotype` inset remains available for a tall traditional single-column presentation.

## Freeze and inspect the composition

```sh
uv run --script <skill-dir>/scripts/compose_context_insets.py contextual-draft.json --fit-pockets --output brief.json --report context.json
uv run --script <skill-dir>/scripts/render_chart.py brief.json --svg poster.svg --html poster.html --report layout.json
uv run --script <skill-dir>/scripts/audit_chart.py poster.svg --source brief.json --report browser.json --png poster.png
```

Substitute requested output paths. Use `--fit-pockets` for proposed positions: it measures complete content height and finds the nearest clear position within 120 units on each axis. It keeps width, typography, nodes, prose, category assignments and relation kinds, and reports each box adjustment. The usable field runs from x = 48 to width − 48 and y = 130 to height − 85; it also reserves full node, connection attachment, key, caption and existing inset envelopes. It cannot make an oversized or occupied region usable by deleting information. If no nearby position fits, revise the proposed pocket or the surrounding composition. Omit the flag when the user requires exact inset coordinates. The helper records the actual corridors after they avoid the final inset boxes.

Open the final PNG. Compare the top, middle and lower thirds at the same page width as the reference. Context should balance the opening and clarify its subject. It cannot repair a remote descendant family or a long influence detour. For those, recompose the local nodes with complete name/note envelopes, then reroute and inspect again.

For a larger detail, reuse the audit browser instead of assuming a separate image-processing package is installed. Add `--detail-png detail.png --detail-box X Y WIDTH HEIGHT` to the audit command, using source SVG coordinates inside the page. This renders the selected region directly while retaining the full preview and audit. Read that detail PNG with the image tool; the report alone cannot verify its appearance.

The browser independently checks visible inset text, source counts, painted category colors, mark separation, image identifiers, font sizes, full box boundaries and collisions with nodes, captions and relationship paths. Geometry and exact counts are necessary checks; they do not grade historical interpretation or aesthetic parity.
