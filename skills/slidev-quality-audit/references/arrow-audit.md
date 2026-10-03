# Marked SVG Arrow Audit

Use this reference when interpreting connection findings or preparing authored diagrams for the quality audit. Keep solid category nodes borderless.

Mark each authored SVG shaft or explicit filled head with a stable `data-arrow-id`, `data-connector-id`, or `data-role="edge"`. Keep imported source pixels inside a narrow `data-source-media` boundary. Horizontal and vertical strokes have zero-area DOM boxes but visible ink; the auditor still measures them.

The audit checks these error rules:

| Rule | Evidence | Correction |
| --- | --- | --- |
| `arrow-low-contrast` | A shaft sample or an actual referenced head paint has visible composite contrast below 3:1 against its local canvas or filled region. | Route through a clear gutter or choose an allowed paint with at least 3:1 on every crossed backing. Check alpha and interaction-state opacity. |
| `arrowhead-covered` | A later opaque filled shape covers sampled geometry of a referenced head. | End the complete head outside the target silhouette. Correct `refX`, marker size, orientation, or route, and leave a small clearance. |

The threshold is non-text contrast at readable, resting, focus, and delivery states. Both shaft and head must pass. A black shaft with a white head on white is a failure. A gray with 3:1 as an opaque base can fail when its opacity is 0.25. A connection crossing a translucent path must be measured against that path composited with the canvas.

The browser pass samples shafts and actual referenced marker instances, resolves ordinary marker units, viewBox scaling, orientation, local transforms and `context-stroke`, and checks filled path contours in paint order. Hollow ER symbols communicate through their visible rim; their white interiors are structural voids. A visible filled head with no stroke is checked by its interior paint.

Declare `data-arrow-transient` only on an intentional partial reveal. This exemption applies while the marked element has an active animation; it does not excuse a resting or final low-contrast arrow. Prefer running the audit after the intended readable dwell. Inspect paused focus states separately when animation affects direction.

Inspect gradients, filters, complex clips/masks, arbitrary custom marker hierarchies, and connector crossings manually. Narrow open connector strokes are not modeled as painted background regions. The automatic check supplements real screenshots and routing inspection; it cannot certify those unsupported effects.

When reporting a defect, include the state, stable arrow ID, failing part, actual backing, measured ratio, and concrete correction. Preserve semantic direction, native glyphs, and source fidelity. Fix geometry or paint; do not hide the problem with node borders, broad halos, a weaker threshold, or a blanket ignore selector.
