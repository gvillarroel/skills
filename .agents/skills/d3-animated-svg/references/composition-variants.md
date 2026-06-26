# D3 Composition Variants

Use this reference when maintaining `assets/examples/d3-animated-svg/composition-sheets.html` and `composition-sheets.js`.

## Purpose

Composition variants are visual-first examples that show how an existing D3 pattern can be recomposed for a specific armature. They are not a classification of the strongest current gallery examples. The sheet generator must review every current `window.D3_ANIMATED_SVG_EXAMPLES` record, infer useful target compositions for that source pattern, and keep only the targets that can visibly express the composition. A source pattern may appear in several composition sheets when it has distinct useful versions, such as:

- `d3-composition-balance-symmetry-force-network`
- `d3-composition-diagonal-armature-force-network`
- `d3-composition-radial-rosette-force-network`

## Variant Record

Each generated record in `composition-sheets.js` uses:

- `compositionId`: one of the published sheet IDs.
- `sourceId`: the source example ID from `window.D3_ANIMATED_SVG_EXAMPLES`.
- `kind`: renderer family for the preview SVG, such as `network`, `flow`, `matrix`, `radial`, `hierarchy`, `scatter`, `lanes`, `table`, or `bar`.
- `renderer`: the concrete preview renderer selected for the target composition.
- `sourceFamily`: the source gallery family or inferred pattern family.
- `inferredKind`: the source pattern kind inferred during review.
- `variantTitle`: short visible role for the variant.
- `recipe`: one-sentence recomposition instruction.
- `armatureLines`: the composition lines used by the target.
- `quadrants`: how the target composition uses Q1-Q4 or equivalent fields.
- `reviewed`: `true` after the source pattern has passed the per-pattern review.
- `id`: generated as `d3-composition-${compositionId}-${sourceId}`.

Each card renders an inline SVG preview and exposes:

- `data-composition-id`
- `data-example-id`
- `data-pattern-id`
- `data-composition-pattern-id`
- `data-source-family`
- `data-armature-lines`
- `data-quadrants`
- `data-reviewed`

Each preview SVG must expose the same composition/source attributes, include visible `.composition-line` guides, at least four `.quadrant-field` regions, a `.source-pattern-recomposition` group that preserves or faithfully recreates the rendered base marks, and a `.base-signature` group that ties the optimized variant back to the original source pattern. Generic renderer families are fallback scaffolds only; published cards should preserve the base SVG's mark vocabulary before adding composition-specific anchors.

Do not use fit tiers or fit badges. Keep only variants that are useful for the selected composition.

## Maintenance Rules

1. Review every current source pattern before publishing the sheets.
2. Add a target only when the source pattern can visibly express the target armature.
3. Preserve the source pattern's semantic meaning by cloning or faithfully recreating the rendered base SVG marks. When a target composition requires it, re-layout those marks, links, labels, and groups instead of only rotating or scaling the original SVG.
4. Keep the preview SVG nonblank and specific enough to evaluate the composition without opening the base gallery.
5. Keep the base pattern link intact so the source `d3-pattern-*` ID remains reachable.
6. Validate after changes:

```powershell
uv run --script .agents/skills/d3-animated-svg/scripts/verify_composition_sheets.py .agents/skills/d3-animated-svg/assets/examples/d3-animated-svg/composition-sheets.html --min-variants 180 --expected-reviewed-patterns 218 --required-variant d3-composition-radial-rosette-force-network --expect-clean
```
