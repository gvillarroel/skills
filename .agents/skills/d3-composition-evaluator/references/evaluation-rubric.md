# D3/SVG Composition Evaluation Rubric

Use this rubric to evaluate a rendered D3 or SVG pattern, composition variant, or gallery card.

## Contract Checks

- The SVG is visible, nonblank, and framed inside the card or page without clipping important marks.
- The SVG has a `title`, `desc`, stable `id`, and a predictable selector for validation.
- A composition variant uses `d3-composition-<composition-id>-<source-id>` as its stable ID.
- The variant exposes enough metadata to trace it back to the base pattern, such as source example ID and `d3-pattern-*` ID.
- The card shows the SVG preview directly; text-only cards are not sufficient for composition review.
- If a reviewed source pattern is not published in any composition sheet, the review records an explicit rejection reason. Missing targets without a rejection reason are an audit failure.
- Card previews should not rely on visible composition scaffolding. Visible guide lines, quadrant overlays, source-field borders, signature boxes, or direction cues are failures unless they are source-derived data marks, route paths, flow links, label leaders, or another narrative element.

## Composition Checks

- Evaluate composition from the relevant source-derived components, not from every SVG primitive. Choose the focus set by pattern family: graph nodes plus links, grid/table cells, flow stations plus connectors, chart data marks, radial rings/segments, hierarchy nodes plus branches, and dense-label lane text plus leaders.
- Ignore composition guides, quadrant fields, source signatures, hidden source caches, and explanatory overlays when measuring placement. In card previews, visible guide overlays should be reported as visual defects instead of counted as composition evidence.
- Check where the focus components land against the intended attention points and armature lines. The primary question is placement: center, balance, diagonal proximity, grid track alignment, radial sector/ring placement, flow start/output positions, or lane/field separation.
- Check how focus components relate to each other. Graph links, hierarchy branches, flow paths, and label leaders should align organically with the selected armature; unsupported or decorative connectors should not inflate the score.
- Check the narrative fit before rewarding the geometry. A publishable composition should explain why that armature clarifies the source: comparison, route/change, dominant artifact plus context, modular repetition, real center/cycle, source-to-output handoff, or dense-label readability.
- Balance and symmetry: primary masses counterweight across a center axis or central frame without dead corners.
- Diagonal armature: source, transition, and outcome points form a readable diagonal or reciprocal diagonal path.
- Golden/root split: the dominant visual field and supporting context field have clear proportional roles.
- Thirds/fifths grid: repeated rows, columns, cards, or modules snap to a shared grid and can join a larger page.
- Radial/rosette: peers orbit a center, rings and spokes stay legible, and the center has an explicit role.
- Flow spine: the viewer can follow source, transformation, checkpoint, and output without backtracking.
- Dense-label lanes: labels sit in lanes or margins with clean leaders, while the data field remains inspectable.

## Quality Checks

- Preserve data truth. Do not bend quantitative positions, areas, ranks, or relationships merely to improve an armature score.
- For charts and maps, identify which elements are compositional emphasis marks versus protected data geometry before scoring. Do not reward moving axes, scales, geographic shapes, or quantitative positions only to hit a symmetry guide.
- Check text fit, overlap, label contrast, and leader-line ambiguity at desktop and mobile sizes when the artifact is responsive.
- Prefer a small set of strongly placed anchors over forcing every minor point to a guide line.
- A publishable variant should be understandable from the SVG preview before opening the source gallery.

## Source-Closeness Checks

Use these when evaluating a recomposed variant against the source pattern that generated it:

- The card, SVG, and link expose the original source example ID and stable `d3-pattern-*` ID.
- The visible source signature or title trace makes the base pattern identifiable without opening the source gallery.
- Source-closeness scoring should compare the recomposed source content against the base SVG, excluding composition-only anchors such as guide lines, lane labels, context panels, or radial/grid cues.
- The preview renderer is compatible with the source pattern kind. For example, a source network can become balanced, diagonal, or radial, but it should still read as nodes and links.
- The simplified preview keeps a reasonable mark vocabulary from the base SVG: node-link patterns keep circles and connectors, matrices keep cells, flows keep connectors, dense-label views keep labels and leaders.
- Lower source-closeness scores are acceptable for highly abstract previews, but the score should explain what became more generic.

## Scripted Scoring

For gallery-level composition sheets, prefer `scripts/evaluate_composition_variants.py` after basic render validation. It opens the rendered composition sheet and base gallery in Chromium and reports:

- `sourceClosenessScore`: traceability, renderer continuity, mark profile similarity, palette overlap, source signature, title trace, protected chart/map geometry, and contract health.
- `compositionScore`: contract health plus target-specific placement and relationship metrics for balance, diagonal, golden/root split, thirds/fifths grid, radial/rosette, flow spine, and dense-label lanes. The metric uses a focus filter so charts are scored from data marks, graphs from nodes and links, grids from cells, flows from stations/connectors, and lanes from labels/leaders.
- `overallScore`: weighted source closeness plus composition fit.

The evaluator should resolve rendered transforms before extracting mark centers. Use the JSON output for regression checks and the generated worst-score screenshots for visual calibration. Do not rely on scores alone when a score conflicts with obvious visual evidence.

When evaluating galleries with replay or entrance animation, score the settled frame after the active tab has finished animating. Measuring immediately after a tab change can undercount source-derived marks that are still transparent and produce false composition failures.

## Reporting

Report findings in this order:

1. Blocking contract failures: blank SVG, missing ID, missing source link, broken render, or clipped content.
2. Source-closeness failures: missing base trace, incompatible renderer, or mark vocabulary that no longer resembles the source pattern.
3. Composition failures: weak armature, unclear center, poor visual weight, broken reading path, or bad label lanes.
4. Refinements: palette balance, guide contrast, secondary label placement, or spacing adjustments.

For each finding, name the affected selector, pattern ID, composition ID, or file path when available.
