# D3 Visual Tokens

Use `assets/palettes/colorsets.json` and `references/palette-contract.md` as the authoritative palette contract. This file records shared typography and interaction conventions used by the published D3 galleries.

## Typography

- Primary font: `"Open Sans", Arial, sans-serif`.
- Apply it explicitly to SVG text because extracted SVG may not inherit page CSS.
- Keep labels horizontal when possible and use concise direct labels. Choose `#000000` or `#ffffff` by maximum WCAG contrast against the actual containing fill; use placement or a dedicated solid label area when dense marks impair readability.

## Palette Policy

- Use colorset1 by default: red-neutral hierarchy, grayscale structure, and exact tokens only.
- Use colorset2 only after an explicit extended/full-color request and only for meaningful categorical or state separation.
- Do not use raw D3 interpolator palettes. Build discrete ramps from the active colorset.
- Use opacity rather than generating RGBA colors.
- Allocate categorical fills from the active palette's complete `solidSequence`, excluding only the actual canvas. Use the saturated/base colors first, then the remaining dark, bright, and neutral tokens; soft tokens come late. Keep each filled mark borderless until all usable unique solid colors are exhausted, then add explicit overflow outline variants. Keep an opaque red keyboard focus outline for interaction visibility.

## Density

Follow `compact-composition.md`: measured nodes with 6 px vertical / 10 px
horizontal padding, 12 px panel padding, 8 px gaps, and 32 px controls (44 px for
touch). Preserve font sizes, scales, label clearance, and explicit dimensions.

## Interaction

- Pair hover, selection, warning, success, and focus color with a non-color cue.
- Give icon-only controls an `aria-label`; keep an accessible visible label when the action is not obvious.
- Ensure replay/reset controls restore a deterministic initial state without duplicating marks or listeners.

## Published Fixtures

The legacy `d3-animated-svg`, `d3-animated-svg-cs1`, `d3-animated-svg-colorset2`, `d3-logo-design`, and `d3-logo-textures` example-set IDs remain stable after skill consolidation. Apply the same solid-first paint and contrasting-label policy to their editable filled marks and new runtime artifacts while preserving their links.
