# D3/SVG Composition Evaluation Rubric

Use this rubric to evaluate a rendered D3 or SVG pattern, composition variant, or gallery card.

## Contract Checks

- The SVG is visible, nonblank, and framed inside the card or page without clipping important marks.
- The SVG has a `title`, `desc`, stable `id`, and a predictable selector for validation.
- A composition variant uses `d3-composition-<composition-id>-<source-id>` as its stable ID.
- The variant exposes enough metadata to trace it back to the base pattern, such as source example ID and `d3-pattern-*` ID.
- The card shows the SVG preview directly; text-only cards are not sufficient for composition review.

## Composition Checks

- Balance and symmetry: primary masses counterweight across a center axis or central frame without dead corners.
- Diagonal armature: source, transition, and outcome points form a readable diagonal or reciprocal diagonal path.
- Golden/root split: the dominant visual field and supporting context field have clear proportional roles.
- Thirds/fifths grid: repeated rows, columns, cards, or modules snap to a shared grid and can join a larger page.
- Radial/rosette: peers orbit a center, rings and spokes stay legible, and the center has an explicit role.
- Flow spine: the viewer can follow source, transformation, checkpoint, and output without backtracking.
- Dense-label lanes: labels sit in lanes or margins with clean leaders, while the data field remains inspectable.

## Quality Checks

- Preserve data truth. Do not bend quantitative positions, areas, ranks, or relationships merely to improve an armature score.
- Check text fit, overlap, label contrast, and leader-line ambiguity at desktop and mobile sizes when the artifact is responsive.
- Prefer a small set of strongly placed anchors over forcing every minor point to a guide line.
- A publishable variant should be understandable from the SVG preview before opening the source gallery.

## Reporting

Report findings in this order:

1. Blocking contract failures: blank SVG, missing ID, missing source link, broken render, or clipped content.
2. Composition failures: weak armature, unclear center, poor visual weight, broken reading path, or bad label lanes.
3. Refinements: palette balance, guide contrast, secondary label placement, or spacing adjustments.

For each finding, name the affected selector, pattern ID, composition ID, or file path when available.
