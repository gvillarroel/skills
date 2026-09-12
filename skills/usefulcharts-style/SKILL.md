---
name: usefulcharts-style
description: Create editable educational posters inspired by UsefulCharts, with compact family trees, branching histories, and parallel timelines. Use for genealogy, dynasties, institutional or idea lineages, and chronological wall charts where spatial hierarchy, relationship routing, semantic color, and print readability matter.
---

# UsefulCharts-style posters

Create an original information poster with clear relationships, stable family colors, compact labels, and deliberate connector corridors. UsefulCharts is the design reference; identify the result by its subject and author. A cream background and colored boxes alone do not establish a convincing resemblance.

## Select one construction route

- **Lineage with 30 records or fewer, including institutional mergers:** read [compact lineage](references/compact-lineage.md) and adapt [the data-only template](assets/templates/lineage.json). Start with `design: editorial`, `mode: lineage`, `layout: auto`, unless the user explicitly prescribes positions. Omit dimensions, coordinates, custom imprint and font overrides for the first preview so the renderer measures the subject. Two incoming links do not make a small history a dense authored poster. Continue directly to rendering; use authored placement only if the preview exposes a specific composition problem.
- **Medium institutional history, typically 31–100 records:** read [packed stories](references/packed-stories.md). Use `layout: packed` with relative neighborhood hints, explicit dates and meaningful emphasis. Omit page dimensions and font overrides initially. The renderer measures the page and the complete records; a larger dataset is not a reason to scatter small labels across a huge sheet.
- **Genealogy with generations and partnerships:** read [cohort composition](references/cohort-composition.md) and adapt [the family template](assets/templates/cohorts.json). For 30 people or fewer, use `layout: cohorts` and omit page dimensions, generation bounds, coordinates and custom imprint initially. For 31–100 people, read [local family baselines](references/branch-baselines.md) and run its helper on a data-first cohort brief: omit dimensions, generation bounds, coordinates, node widths, font overrides and repeated style assignments for the first preview. The helper measures readable names, distinguishes ancestral nameplates from supporting relatives and places local family labels. Use the same baseline route to refine a dense mural's supplied geometry; its 10–13-unit typography is only for substantial data. Author difficult marriages after reviewing the result.
- **Dense institutional history or a prescribed layout:** read [institutional composition](references/institution-composition.md) and the graph fields in [the editorial contract](references/editorial-contract.md). Write individual histories before coordinates, then compose the difficult mergers as local groups. Place historical dates above compact name panels and contextual notes below them; reserve the complete content envelope and the longest influence corridors.
- **Parallel numeric timelines:** for a small comparison with few lanes and no branching, read [compact chronology](references/compact-chronology.md) and adapt [the timeline template](assets/templates/compact-timeline.json). For a history with dated notes or branching, read [narrative chronology](references/narrative-chronology.md) and the timeline fields in [the editorial contract](references/editorial-contract.md). With about 20 periods and 24 notes or fewer, start from [the compact annotated template](assets/templates/narrative-timeline.json), a 1300 × 1700 page and readable 18/15-unit notes; a few branches do not justify the dense mural defaults. Compose restrained period ribbons, then use the bundled note-placement helper around the full bridge and illustration geometry. Preserve the numeric scale, exact gaps, divisions and unions.

Use [the shared contract](references/data-contract.md) only for additional field detail or classic schematic compatibility. The classic renderer is not the poster aesthetic acceptance target. Use [composition critique](references/editorial-composition.md) when matching a dense reference, and [pattern recipes](references/pattern-recipes.md) when the task names a published pattern.

## Preserve meaning while composing

Distinguish descent, partnership, succession, branching, influence and uncertainty. A chronological neighbor is not automatically an ancestor. Keep every supplied label, date and relationship. Mark invented demonstration data visibly as synthetic; do not manufacture records or relationships to improve visual density.

Store known `birth` and `death` years as JSON numbers. For an unknown date, omit that numeric field or use `null`; preserve its wording in `detail` and, if useful, `birth_record` or `death_record`. For example, an unknown birth with a known death can use `"birth": null, "death": 1972, "detail": "birth unknown–1972"`. Never restore `"unknown"` or a quoted year into a numeric date field after layout. Keep this representation in the final editable source.

Keep the source-defined category through mergers and marriages. Do not invent a blended category for descendants of two differently colored parents. Assign each person's stated branch before placing them; preserve it when relationships cross. Importance changes typography and treatment, not automatically the family color. Vary cards, plain names, family pills and selected illustrations by meaning. Give dates and explanatory consequences subordinate type. Keep explanatory prose concise rather than repeating every edge inside its target label.

When important people still blend into repetitive nameplates, read [focal people and the opening fan](references/focal-people.md). Measure selected portraits and names together, and use bounded `cohort_spread` preferences only where the source's early branches need more room.

A short history needs a compact canvas. Reserve the portrait 2:3 wall format and dense 10–16-unit typography for substantial data. Let terminated branches release space; let large descendant groups widen. Avoid rigid persistent columns, equally weighted cards and illustrations placed at mechanical intervals. A schematic composition can have uneven gaps; a numeric time scale cannot.

When supplied places, courts or movements disappear among the names, read [source-bound landmarks](references/context-landmarks.md). For a new family, declare the bound captions before layout and run the baseline helper with `--reserve-context`; render its result directly. It reserves the full caption envelopes and routes around them. Use bounded pocket placement to refine an existing authored graph. Inspect actual branch ownership in the preview and preserve every required caption.

## Render and inspect

Write a UTF-8 JSON brief outside the skill bundle. For long data, assemble a Python or JavaScript object and serialize it rather than hand-writing repeated JSON arrays. Write a builder to a workspace-relative file before executing it; do not stage it in `/tmp` or another external directory. Execute the bundled scripts using their documented command line; implementation and test files are maintenance resources, not prerequisites for ordinary use.

```sh
uv run --script <skill-dir>/scripts/render_chart.py brief.json --svg poster.svg --html poster.html --report layout.json
uv run --script <skill-dir>/scripts/audit_chart.py poster.svg --source brief.json --report browser.json --png poster.png
```

Substitute exact requested paths. Both scripts create output parents. Keep footer notes to two short lines; leave implementation names and resource IDs out of the printable reading note. Image provenance is embedded automatically. The browser audit measures actual font geometry, source inventories, routes, time positions and illustration collisions. See [evaluation and repair](references/evaluation.md) if browser provisioning fails.

**Open the final PNG with the image-reading tool.** Reading dimensions, metadata or an audit report does not inspect the preview. Check the whole page, the busiest merger, the longest label and the uncertain connection. Repair the brief, rerender, and inspect the final revision. Do not remove information or repeatedly shrink type to make a collision disappear.

If the model or tool explicitly cannot accept images, preserve the PNG for an external visual review and state that limitation. Importing Pillow or Matplotlib, converting to ASCII, or reading PNG headers cannot substitute for seeing the composition. The bundled browser audit already performs rendering and geometry checks without those packages.

Compare against a relevant reference at the same display width and compare a dense detail at the same relative scale. Write the three most visible differences before editing. Repair composition first, then hierarchy, connector rhythm, typography and artwork. Check actual transparency and the optical weight of illustrations at their placed size. A clean audit cannot override an obvious visual mismatch or prove indistinguishability.

For unsupported structures, retain the data and visual grammar and author an SVG directly or extend a copy of the renderer outside the bundle. Do not force a cyclic network into a false tree. Custom SVG needs equivalent geometry and semantic checks.

Deliver the editable SVG, source JSON, preview and useful viewer. State what was verified and any remaining gap without inventing a similarity percentage or claiming unproven visual parity.
