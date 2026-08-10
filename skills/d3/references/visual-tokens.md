# D3 Visual Tokens

Use `assets/palettes/colorsets.json` and `references/palette-contract.md` as the authoritative palette contract. This file records shared typography and interaction conventions used by the published D3 galleries.

## Typography

- Primary font: `"Open Sans", Arial, sans-serif`.
- Apply it explicitly to SVG text because extracted SVG may not inherit page CSS.
- Keep labels horizontal when possible, use concise direct labels, and add a light halo over dense marks.

## Palette Policy

- Use colorset1 by default: red-neutral hierarchy, grayscale structure, and exact tokens only.
- Use colorset2 only after an explicit extended/full-color request and only for meaningful categorical or state separation.
- Do not use raw D3 interpolator palettes. Build discrete ramps from the active colorset.
- Use opacity rather than generating RGBA colors.

## Interaction

- Pair hover, selection, warning, success, and focus color with a non-color cue.
- Give icon-only controls an `aria-label`; keep an accessible visible label when the action is not obvious.
- Ensure replay/reset controls restore a deterministic initial state without duplicating marks or listeners.

## Published Fixtures

The legacy `d3-animated-svg`, `d3-animated-svg-cs1`, `d3-animated-svg-colorset2`, `d3-logo-design`, and `d3-logo-textures` example-set IDs remain stable after skill consolidation. New runtime artifacts follow the unified colorset1-default policy even when an older base gallery preserves historical styling for link compatibility.
