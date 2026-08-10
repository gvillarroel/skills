# D3 Palette Contract

Treat `assets/palettes/colorsets.json` as the machine-readable source of truth for every repository-owned D3 artifact. Use one active colorset per render.

## Selection

- Use `colorset1` for every request unless the user explicitly asks for an extended, expanded, full-color, or multicolor palette.
- Do not infer colorset2 from words such as *colored*, *polished*, *branded*, *vibrant*, or *accessible* alone.
- Use `colorset2` only when the explicit request and the data both justify multiple semantic hues. Record the reason in artifact metadata or the accompanying decision file.
- When colorset2 is selected, make at least one colorset2-only token visibly affect a mark. Merely embedding its palette JSON or unused CSS is not compliance.

## Paint Syntax

- Permit only exact lowercase six-digit hex tokens in the active colorset.
- Permit `none`, `currentColor`, `url(#...)`, and opacity as non-color SVG values. Resolve `currentColor` to an active token.
- Reject named colors, three/eight-digit hex, RGB/RGBA, HSL/HSLA, LCH/OKLCH, sampled image colors, and arbitrary user-supplied paint values.
- Do not interpolate through undeclared colors or use raw `d3-scale-chromatic` ramps. Build ordinal, threshold, or quantized ramps from active tokens.
- Prefer geometry, masks, dash offsets, opacity, transforms, or discrete token changes for animation.
- Apply the contract to page background, text, controls, focus states, tooltips, and SVG marks, not only the primary data series.

## Colorset1 — Standard

Colorset1 contains 17 red-neutral tokens. Use these roles first:

- background `#f7f7f7`
- surface `#ffffff`
- ink `#333e48`
- dark ink `#1c1c1c`
- primary `#9e1b32`
- primary dark `#6d1222`
- critical accent `#e8002a`
- soft accent `#ffccd5`
- muted `#828282`
- line `#cfcfcf`
- quiet surface `#e7e7e7`

Use grayscale value, stroke weight, texture, shape, position, and direct labels before adding more hue. Reserve red for the primary series, selection, change, risk, or another declared semantic role.

## Colorset2 — Extended

Colorset2 contains every colorset1 token plus blue, orange, green, yellow, purple, interaction, highlight, and status tokens. Its primary categorical sequence is:

`#9e1b32`, `#007298`, `#e77204`, `#45842a`, `#652f6c`, `#f1c319`.

Assign hues by meaning and keep the mapping stable across frames and linked views. Prefer one dominant hue plus neutrals when the data does not require six categories.

## Contrast and Small-Size Gate

- Use `#1c1c1c` or `#333e48` on light surfaces and `#ffffff` on dark or saturated surfaces.
- Add a white or light halo behind labels placed over marks.
- Do not encode a state by hue alone; pair color with position, shape, texture, label, or stroke pattern.
- Inspect the intended desktop/mobile size. For logos, also inspect a 96 px-wide preview and simplify geometry or texture until the brand name remains recognizable.

## Logo-Specific Restrictions

- Do not use gradients in logo or texture outputs, even when every stop is palette-safe.
- Use filters only for alpha or geometry; never expose raw filter RGB output.
- Keep texture secondary to the wordmark or dominant silhouette.
- An intentional text-occlusion exception must follow `references/text-clearance-contract.md` and may never exceed its declared ratio.

## Validation

Run `scripts/check_palette_contract.py` on ordinary HTML or SVG output. For JavaScript-rendered HTML, also render in a browser and inspect computed SVG paint because the static checker intentionally ignores runtime script bodies. Use the dedicated logo/gallery browser validators when their route applies.
