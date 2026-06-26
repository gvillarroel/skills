# D3 Composition Variants

Use this reference when maintaining `assets/examples/d3-animated-svg/composition-sheets.html` and `composition-sheets.js`.

## Purpose

Composition variants are visual-first examples that show how an existing D3 pattern can be recomposed for a specific armature. They are not a classification of the strongest current gallery examples. A source pattern may appear in several composition sheets when it has distinct useful versions, such as:

- `d3-composition-balance-symmetry-force-network`
- `d3-composition-diagonal-armature-force-network`
- `d3-composition-radial-rosette-force-network`

## Variant Record

Each record in `composition-sheets.js` uses:

- `compositionId`: one of the published sheet IDs.
- `sourceId`: the source example ID from `window.D3_ANIMATED_SVG_EXAMPLES`.
- `kind`: renderer family for the preview SVG, such as `network`, `flow`, `matrix`, `radial`, `hierarchy`, `scatter`, `lanes`, `table`, or `bar`.
- `variantTitle`: short visible role for the variant.
- `recipe`: one-sentence recomposition instruction.
- `id`: generated as `d3-composition-${compositionId}-${sourceId}`.

Each card renders an inline SVG preview and exposes:

- `data-composition-id`
- `data-example-id`
- `data-pattern-id`
- `data-composition-pattern-id`

Do not use fit tiers or fit badges. Keep only variants that are useful for the selected composition.

## Maintenance Rules

1. Add a variant only when the source pattern can visibly express the target armature.
2. Preserve the source pattern's semantic meaning while changing placement, guides, grouping, and hierarchy.
3. Keep the preview SVG nonblank and specific enough to evaluate the composition without opening the base gallery.
4. Keep the base pattern link intact so the source `d3-pattern-*` ID remains reachable.
5. Validate after changes:

```powershell
uv run --script .agents/skills/d3-animated-svg/scripts/verify_composition_sheets.py .agents/skills/d3-animated-svg/assets/examples/d3-animated-svg/composition-sheets.html --min-variants 50 --required-variant d3-composition-radial-rosette-force-network --expect-clean
```
