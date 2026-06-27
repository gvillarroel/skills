---
name: d3-composition-recomposer
description: Recompose an existing D3 or SVG pattern into a requested composition armature while preserving source data semantics and creating stable composition variant IDs. Use when a user asks to convert, reimagine, or generate balance, diagonal, radial, grid, flow, proportional, or dense-label versions of a pattern.
---

# D3 Composition Recomposer

## Workflow

1. Identify the source pattern, its data semantics, and the requested target composition. If the user gives a source ID, preserve it exactly.
   - If the user names an exact output file or path, write that exact path. Do not replace it with a different filename or a conversational-only response.
   - In skill-only or isolated validation, treat the prompt as complete unless it names a local artifact to inspect. Do not search parent repositories, sibling skills, evaluation prompt folders, or gallery fixtures for extra context.
2. Assign the variant ID before editing: `d3-composition-<composition-id>-<source-id>`.
3. Choose a recipe from `references/recomposition-recipes.md` and map the source pattern's primary marks to the target armature.
4. Preserve the source pattern's meaning and visual vocabulary. When a rendered source SVG is available, start from that geometry or a faithful clone before adding the target armature; do not replace it with a generic renderer, fabricate different data, or change quantitative relationships without a clear request.
5. Build or update a visible SVG preview for the variant. Include `title`, `desc`, stable IDs, `data-composition-id`, `data-example-id`, `data-pattern-id`, and `data-composition-pattern-id` when the output is a gallery card.
6. Validate in a real browser when possible. Check that the SVG is nonblank, labels fit, the composition ID is searchable, and the source pattern remains discoverable.

## Gallery Variant Rules

- Do not add every source pattern to every composition. Add only variants that work well for that armature.
- Choose targets by narrative fit before geometric fit. The composition should make the source story clearer: comparison for balance, change or route distance for diagonal, dominant artifact plus context for golden/root, modular repetition for grid, real cycles or hubs for radial, handoffs for flow, and density/readability for label lanes.
- Do not use `strong`, `support`, or other fit tiers. Curated membership means the variant is good enough to show.
- Keep each card visual-first: the SVG preview should explain the composition before the text does.
- If multiple variants share a source pattern, each variant must have a different composition-specific ID.
- If a reviewed source pattern has no target that improves the story without distorting its data marks, record an explicit rejection reason instead of publishing a forced variant.

## Progressive Disclosure

Read `references/recomposition-recipes.md` before converting a source pattern into a new composition or adding a new reusable composition family.
