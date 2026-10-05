---
name: usefulcharts-style
description: "Creates editable educational posters inspired by UsefulCharts, with compact family trees, classifications, branching histories, and parallel timelines. Use for genealogy, taxonomies, institutional or idea lineages, and chronological wall charts where spatial hierarchy, relationship routing, semantic color, and print readability matter."
---

# UsefulCharts-style posters

Read [palette-policy.md](references/palette-policy.md) before authoring or composing visuals. Apply one exact colorset to authored content and report preserved source media separately.
Read [solid-surfaces.md](references/solid-surfaces.md) for solid-first category fills, black/white text on the actual fill, and palette exhaustion before border variants.

Create an original information poster with clear relationships, stable family colors, compact labels, and deliberate connector corridors. UsefulCharts is the design reference; identify the result by its subject and author. A cream background and colored boxes alone do not establish a convincing resemblance.

**Require at least the useful knowledge density of the relevant reference.** Read [knowledge density](references/knowledge-density.md) before accepting the content selection or finished poster. Compare the amount of distinct supported records, relationships, temporal information and explanatory context at the same poster area, then inspect its distribution and readability. A sparse, clean diagram does not meet this default. More boxes, smaller text or decorative fill cannot substitute for more useful knowledge.

Read [arrow-visibility.md](references/arrow-visibility.md) when producing, importing or reviewing directional arrows. Audit actual shafts/heads at delivery scale.

## Pack measured calendar labels without drawing

For a layout-only request with supplied horizontal footprints, read [shared time rows](references/shared-time-rows.md), serialize the measured input, and run its documented helper in `numeric` mode. Deliver the generated layout at the requested path, retain owner identities, and state the remaining visual checks. Stop before poster rendering. Keep measured calendar x positions fixed; assign only y tracks and family pockets. Create input parents before writing nested files; use the helper's CLI without reading implementation or tests.

## Review supplied density evidence without drawing

For a density-only review, complete these steps and stop before the construction routes:

1. Read [knowledge density](references/knowledge-density.md) and [the census template](assets/templates/density-census.json). Use the documented interface; reading script implementation is unnecessary.
2. Save each supplied census with the template's exact field names, preserving the supplied counts, identities and review statuses. Keep synthetic evidence identified as synthetic.
3. Execute the following command for each candidate, substituting the actual skill directory and requested paths. Deliver its generated report unchanged; do not write a replacement JSON verdict by hand.

```sh
uv run --script <skill-dir>/scripts/compare_density.py <reference-census.json> <candidate-census.json> --report <requested-report.json>
```

4. Read each generated report. Explain the decision and specific repairs in the requested prose output. `passes_measured_floor` is the overall boolean. Use the candidate's **lower** bound and reference's **upper** bound for every repair target; overlapping intervals are insufficient. A completed command is not a pass.
5. State the evidence boundary: a declared census decision requires actual image, source, distribution and legibility review before an aesthetic claim. Do not draw when the request is review-only.

## Compose a poster

When no colors are supplied, assign categories from the selected colorset solid sequence, use borderless opaque fills, and select pure black or white text by the actual fill contrast. Preserve explicit colors supplied by the user or source.

When the subject or user calls for a different atmosphere, read [thematic art direction](references/thematic-art-direction.md), including for a planning-only request. Choose the background, imagery and visual metaphor together. Use reference-guided image generation when it would improve recognizable focal illustrations, while retaining factual text and quantitative geometry as editable vector layers. The default paper palette is not a universal template.

For a playful or illustrated brief, read [illustrated discovery](references/illustrated-discovery.md) before layout. Plan recognizable images within the information body, source-answerable visual comparisons and a clear path of exploration. A technically clean outline or a decorative header cannot satisfy that brief. Evaluate image usefulness and playful character independently from correctness; the chosen construction helper is only a starting point.

## Establish the information and editorial decisions

Before choosing coordinates, make three decisions explicit in the working brief; reuse the user's supplied decisions when available. This does not require another approval or an extra deliverable.

For a planning-only request, read [information and editorial planning](references/information-design.md). Deliver the subject-specific sufficiency decision, display selection, visual encoding and a concrete review-and-repair sequence. Then stop before rendering; a list of data checks does not replace the planned visual critique.

1. **Information sufficiency:** identify the question the poster should answer, its audience and scope. Check that identities, typed relationships, relevant dates, category meanings and evidence support that explanation and the required reference-level knowledge density. A small dataset may support a correct explanation while remaining insufficient for the requested dense poster. Distinguish a representable unknown from a material gap. Resolve missing evidence through available sources or a focused question; continue independent work. Do not invent filler.
2. **Editorial selection and visual encoding:** decide which facts are essential, which provide useful context, and which can remain outside the displayed story when selection is authorized. Preserve every required item. Choose schematic generations, causal branches or numeric time to match the evidence; assign positions, connectors, color, type and illustrations a stated meaning. Size the page for the selected content. Read [information and editorial planning](references/information-design.md) when working from broad source material, incomplete data or competing storylines.
3. **Critique and revision:** render, inspect and compare the actual result as required below. Review whether the explanation works as well as whether the diagram is attractive. Repair material weaknesses, then rerender and inspect the changed result. A checklist or a clean geometry report alone does not establish adequate visual quality.

## Select one construction route

Default connected trees, lineages and explanatory groups to the smallest readable composition. Read [compact connected composition](references/compact-composition.md) before selecting or refining their placement. Use the measured routes below, reclaim released pockets and shorten avoidable detours; preserve complete labels, illustration ownership, visible heads and independent routes. Numeric time coordinates remain fixed, and quantitative chart marks retain their measurement scales.

- **Unequal classification trees or long chains that waste a global rank grid:** read [compact outline panels](references/panel-outlines.md). Keep connected families in measured panels, balance their heights, and put short codes or dates beside names. The focused bundle command retains every selected record and typed relation; cross-panel references have two explicitly named endpoints. Use this only when a sectioned outline answers the question. A required numeric x axis must keep the shared-calendar route below.
- **Several entities per family row, with time on x:** read [shared time rows](references/shared-time-rows.md). Fix every calendar coordinate first, measure complete label/art footprints, and use the bundled shared-row helper in `numeric` mode to assign local y tracks. Use its shared track pool when another family should occupy a terminated branch's space while sibling branches continue; retain local family labels. A schematic chronological sequence cannot satisfy an explicit time-axis request.
- **Lineage with 30 records or fewer, including institutional mergers:** read [compact lineage](references/compact-lineage.md) and adapt [the data-only template](assets/templates/lineage.json). Start with `design: editorial`, `mode: lineage`, `layout: auto`, unless the user explicitly prescribes positions. Omit dimensions, coordinates, custom imprint and font overrides for the first preview so the renderer measures the subject. Two incoming links do not make a small history a dense authored poster. Continue directly to rendering; use authored placement only if the preview exposes a specific composition problem.
- **Medium institutional history, typically 31–100 records:** read [data-first branches](references/data-first-branches.md) and use its poster-bundle command on the complete records. It measures active stages, selects influence attachments and exports the composed source with its matching SVG and audit. Use [packed stories](references/packed-stories.md) when a deliberate relative arrangement is supplied. Omit page dimensions and font overrides initially unless the source requires them.
- **Genealogy with generations and partnerships:** read [cohort composition](references/cohort-composition.md) and adapt [the family template](assets/templates/cohorts.json). For 30 people or fewer, use `layout: cohorts` and omit page dimensions, generation bounds, coordinates and custom imprint initially. For 31–100 people, read [local family baselines](references/branch-baselines.md) and run its helper on a data-first cohort brief: omit dimensions, generation bounds, coordinates, node widths, font overrides and repeated style assignments for the first preview. The helper measures readable names, distinguishes ancestral nameplates from supporting relatives and places local family labels. Use the same baseline route to refine a dense mural's supplied geometry; its 10–13-unit typography is only for substantial data. Author difficult marriages after reviewing the result.
- **Dense institutional history or a prescribed layout:** read [institutional composition](references/institution-composition.md) and the graph fields in [the editorial contract](references/editorial-contract.md). Write individual histories before coordinates, then compose the difficult mergers as local groups. Place historical dates above compact name panels and contextual notes below them; reserve the complete content envelope and the longest influence corridors.
- **Parallel numeric timelines:** for a small comparison with few lanes and no branching, read [compact chronology](references/compact-chronology.md) and adapt [the timeline template](assets/templates/compact-timeline.json). For a history with dated notes or branching, read [narrative chronology](references/narrative-chronology.md) and the timeline fields in [the editorial contract](references/editorial-contract.md). With about 20 periods and 24 notes or fewer, start from [the compact annotated template](assets/templates/narrative-timeline.json), a 1300 × 1700 page and readable 18/15-unit notes; a few branches do not justify the dense mural defaults. Compose restrained period ribbons, then use the bundled note-placement helper around the full bridge and illustration geometry. Preserve the numeric scale, exact gaps, divisions and unions.

Use [the shared contract](references/data-contract.md) only for additional field detail or classic schematic compatibility. The classic renderer is not the poster aesthetic acceptance target. Use [composition critique](references/editorial-composition.md) when matching a dense reference, and [pattern recipes](references/pattern-recipes.md) when the task names a published pattern.

For chronology, vary the colored treatment selectively: full duration bands for principal periods, fine duration stems with local name capsules for quieter continuities. Give a region more horizontal space when its concurrent histories and notes need it. Use compact paragraphs for ordinary notes and separate headings for selected landmarks; read [note hierarchy and image ownership](references/note-hierarchy.md) when repeated labels or detached pictures weaken the page. Compose selected illustrations above, below or beside the relevant prose while keeping the event's numeric date on its first line. The [narrative chronology guide](references/narrative-chronology.md) describes weighted lanes, exact stem endpoints, contextual art and measured clearance. Converting every band to a thin line can create an empty framework; compare the mixed composition before accepting it.

## Preserve meaning while composing

Distinguish descent, partnership, succession, branching, influence and uncertainty. A chronological neighbor is not automatically an ancestor. Keep every supplied label, date and relationship in a display brief. When the user supplies a larger research pool and authorizes selection, preserve the original material and record the chosen scope before layout; do not silently remove required records or connect across omitted intermediates as if a direct relationship were established. Mark invented demonstration data visibly as synthetic; do not manufacture records or relationships to improve visual density.

Store known `birth` and `death` years as JSON numbers. For an unknown date, omit that numeric field or use `null`; preserve its wording in `detail` and, if useful, `birth_record` or `death_record`. For example, an unknown birth with a known death can use `"birth": null, "death": 1972, "detail": "birth unknown–1972"`. Never restore `"unknown"` or a quoted year into a numeric date field after layout. Keep this representation in the final editable source.

Keep the source-defined category through mergers and marriages. Do not invent a blended category for descendants of two differently colored parents. Assign each person's stated branch before placing them; preserve it when relationships cross. Importance changes typography and treatment, not automatically the family color. Vary cards, plain names, family pills and selected illustrations by meaning. Give dates and explanatory consequences subordinate type. Keep explanatory prose concise rather than repeating every edge inside its target label.

For genealogical grouping, read [name and date groups](references/genealogy-nameplates.md). Ordinary principal names and short dates normally share a compact colored card; portraits and longer context use a different treatment. When important people still blend into repetitive nameplates, read [focal people and the opening fan](references/focal-people.md). Measure selected portraits and names together, and use bounded `cohort_spread` preferences only where the source's early branches need more room.

A short history needs a compact canvas when that limited scope is requested. Compact routing is also useful during development, but it does not waive the default reference-density target: recover or research relevant content and report a shortfall if the requested scope cannot support it. Reserve the portrait 2:3 wall format and dense 10–16-unit typography for substantial data. Let terminated branches release space; let large descendant groups widen. Avoid rigid persistent columns, equally weighted cards and illustrations placed at mechanical intervals. A schematic composition can have uneven gaps; a numeric time scale cannot.

When small illustrations repeat or a pictured object needs a distinct identity, read [semantic emblems](references/semantic-emblems.md). Choose the source-appropriate subject and inspect its silhouette at the actual panel size; decorative variation alone does not improve the history.

When a compact institutional origin leaves useful open pockets, read [context insets](references/context-insets.md). Add a source-backed illustrated explanation or counts of the actual institutions shown, then reserve and inspect those regions. Context complements the complete history; it must not conceal an unresolved branch layout.

For institutional groups joined by conspicuous influence detours, read [lateral influence routes](references/influence-routes.md). Compose the local histories first, then choose explicit side attachments and short corridors. Compare the full page before accepting a smaller canvas: unchanged font units improve displayed readability only if the denser routing remains easy to follow.

When an institutional poster still reads as persistent columns, use [branch structure](references/branch-structure.md). Separate causal order from a numeric calendar, plan which later histories use released space, and inspect the resulting routes. Review `unrelated-shared-run` warnings: independent edges sharing a painted trunk can suggest a false union. Do not hide supplied notes or add invented branches to improve density.

For a data-first institutional composition, declare important node-anchored branch captions before running the helper. It reserves their complete text and illustration footprints while retaining the institution's own panel width; [data-first branches](references/data-first-branches.md) describes placement and routing. Adding a family title after packing may require recomposing that neighborhood.

When supplied places, courts or movements disappear among the names, read [source-bound landmarks](references/context-landmarks.md). For a new family, declare the bound captions before layout and run the baseline helper with `--reserve-context`; render its result directly. It reserves the full caption envelopes and routes around them. Use bounded pocket placement to refine an existing authored graph. Inspect actual branch ownership in the preview and preserve every required caption.

## Render and inspect

Write a UTF-8 JSON brief outside the skill bundle. For long data, assemble a Python or JavaScript object and serialize it rather than hand-writing repeated JSON arrays. Write a builder to a workspace-relative file before executing it; do not stage it in `/tmp` or another external directory. Execute the bundled scripts using their documented command line; implementation and test files are maintenance resources, not prerequisites for ordinary use.

```sh
uv run --script <skill-dir>/scripts/render_chart.py brief.json --svg poster.svg --html poster.html --report layout.json
uv run --script <skill-dir>/scripts/audit_chart.py poster.svg --source brief.json --report browser.json --png poster.png
```

Substitute exact requested paths. Both scripts create output parents. Keep footer notes to two short lines; leave implementation names and resource IDs out of the printable reading note. Image provenance is embedded automatically. The browser audit measures actual font geometry, source inventories, routes, time positions and illustration collisions. See [evaluation and repair](references/evaluation.md) if browser provisioning fails.

**Open the final PNG with the image-reading tool.** Reading dimensions, metadata or an audit report does not inspect the preview. Check the whole page, the busiest merger, the longest label and the uncertain connection. Repair the brief, rerender, and inspect the final revision. Do not remove information or repeatedly shrink type to make a collision disappear.

For connected layouts, also inspect unnecessary margins, empty branch bands and long connector detours. Compare a concrete tighter placement or shorter route when one is visible, using [compact connected composition](references/compact-composition.md). Keep the last passing version when extra packing hides a head, crowds text or makes source-to-target tracing less clear; the density target never overrides these readability gates.

To inspect a dense region at a larger display size, add `--detail-png detail.png --detail-box X Y WIDTH HEIGHT` to the audit command. Use coordinates from the source SVG inside its canvas, then open the detail PNG. The bundled browser renders it directly; an additional image-processing package is unnecessary.

If the model or tool explicitly cannot accept images, preserve the PNG for an external visual review and state that limitation. Importing Pillow or Matplotlib, converting to ASCII, or reading PNG headers cannot substitute for seeing the composition. The bundled browser audit already performs rendering and geometry checks without those packages.

Compare against a relevant reference at the same display width and compare a dense detail at the same relative scale. Write the three most visible differences before editing. Repair composition first, then hierarchy, connector rhythm, typography and artwork. Check actual transparency and the optical weight of illustrations at their placed size. A clean audit cannot override an obvious visual mismatch or prove indistinguishability.

Apply the [knowledge-density minimum](references/knowledge-density.md) separately from geometry: each useful-information layer must meet the reference, with readable distribution across the whole page and its upper, middle and lower thirds. A shortfall or incomplete census remains pending even when the composition looks busy. Retain density evidence with the working review; do not claim a measured pass from OCR or a visual impression alone.

Revisit the editorial brief if a visually tidy page still fails to explain the subject. Follow [evaluation and repair](references/evaluation.md) for acceptance criteria: distinguish verified content, technical checks and visual judgment; record unresolved differences. Do not call the result finished merely because an iteration count or an aggregate score was reached.

For unsupported structures, retain the data and visual grammar and author an SVG directly or extend a copy of the renderer outside the bundle. Do not force a cyclic network into a false tree. Custom SVG needs equivalent geometry and semantic checks.

Deliver the editable SVG, source JSON, preview and useful viewer. State what was verified and any remaining gap without inventing a similarity percentage or claiming unproven visual parity.

## Additional reference routes

Read only the resource matching the task.

- [Visible discovery](references/visible-discovery.md).
- [Visual grammar](references/visual-grammar.md).
