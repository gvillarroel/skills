# Native Arrow Contrast and Clearance

Use this reference when authoring connections, inspecting direction, or debugging native SVG output. Keep category nodes as opaque solids without decorative outlines.

Require at least 3:1 visible non-text contrast for both the shaft and every visible part of its head against the actual local backing at readable, resting, focus, and final delivery states. Composite paint alpha, stroke opacity, ancestor opacity, and translucent regions before measuring. A head passing on white does not establish that it passes on a colored domain. Preserve native circles, bars, diamonds, crowfeet, and open arrow glyphs; a hollow cardinality symbol communicates through its visible stroke, rather than through its white void.

## Author and Render

1. Route connections through clear gutters. End the head outside the solid target silhouette; leave a small clearance instead of covering the head with a node. Inspect the complete head footprint, including its rear circle or diamond, at both ends of a short relation.
2. Use the selected palette's nearest contrast-safe paint while retaining a usable semantic hue. If one paint cannot contrast with every crossed region, change the route. Avoid node outlines, broad halos, and arbitrary off-palette colors.
3. Run the styler and native renderer in the normal workflow. Newly generated output invokes `scripts/arrow_contrast.py`: it corrects native connector paint, creates per-edge marker identities, and preserves direction and glyph geometry. Supplied SVG input retains source styling and requires an explicit authorized edit before repair.
4. Inspect actual browser output in both requested palettes. Check shaft samples along the whole curve, actual referenced marker instances, and the tip and rear of each head. Resolve `markerUnits`, `viewBox`, `refX`, `refY`, orientation, transforms, and animation CSS marker aliases; inspecting an unused `<defs>` prototype is insufficient.
5. Check settled and intermediate animation states separately. A partially revealed mark or a line deliberately fading behind a revealing node is transient; readable or paused focus states still require 3:1. The renderer updates `--am-marker-start/end` identities while retaining native reveal timing.

## Native Family Rules

- C4 bypass relationships use an exterior gutter when their native curve crosses an unrelated entity. Native body contacts are clipped before the marker clearance is applied. The relation caption moves with its bypass, wraps beside the gutter, and keeps its source wording. Nodes, icons, compartments, and relation direction remain intact.
- Event-modeling relations approach card tops perpendicularly through the existing gap between rows. A shallow diagonal can leave the rear of a triangular head on the card even when its tip is clear.
- ER capacity diagrams use `er.rankSpacing: 80`. Preserve full circles and crowfeet. The finisher rejects a gutter that cannot fit both complete cardinality glyphs; increase spacing and rerender rather than shrinking the glyph or hiding it beneath an entity. Native XHTML relation captions choose black or white against their composited CSS backing.
- Cynefin arrows on the upper dark domains use a paint that contrasts with both actual domain fills. GitGraph and Mindmap edges retain an already usable branch hue; pale native edge colors move to the closest allowed safe tone.
- Timeline's backbone may pass behind native boxes. Preserve that meaningful layering; the direction head must remain clear at the delivered state.

## Geometry Scope and Validation

The helper samples native straight, quadratic, cubic, and elliptical-arc connector paths and uses polygon contours rather than polygon bounding rectangles. The C4 routing pass targets the absolute native entity silhouettes; event routing targets native card rows. This is not a general router for arbitrarily transformed imported SVGs, masks, filters, gradients, or custom marker geometry. Such output needs actual browser measurements and a manual source layout adjustment; do not claim universal clearance from approximate bounds.

Run `uv run --script <skill-root>/scripts/test_arrow_contrast.py` for deterministic paint, arc, contour, marker identity, clearance, C4/event routing, ER capacity, hollow glyph, and borderless-node regressions. These tests supplement actual rendered inspection. Keep node fills and inside-label contrast checks in the normal visual gate after changing routes.
