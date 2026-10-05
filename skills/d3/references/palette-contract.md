# D3 Palette Contract

Treat `assets/palettes/colorsets.json` as the machine-readable source of truth for every repository-owned D3 artifact. Use one active colorset per render.

## Contents

- [Selection](#selection)
- [Paint syntax](#paint-syntax)
- [Colorset1 standard](#colorset1--standard)
- [Colorset2 extended](#colorset2--extended)
- [Bind categories without cycling early](#bind-categories-without-cycling-early)
- [Contrast and small-size gate](#contrast-and-small-size-gate)
- [Logo-specific restrictions](#logo-specific-restrictions)
- [Validation](#validation)

## Selection

- Use `colorset1` for every request unless the user explicitly asks for an extended, expanded, full-color, or multicolor palette.
- Do not infer colorset2 from words such as *colored*, *polished*, *branded*, *vibrant*, or *accessible* alone.
- Use `colorset2` only when the explicit request and the data both justify multiple semantic hues. Record the reason in artifact metadata or the accompanying decision file.
- When colorset2 is selected, make at least one colorset2-only token visibly affect a mark. Merely embedding its palette JSON or unused CSS is not compliance.

## Paint Syntax

- Permit only exact lowercase six-digit hex tokens in the active colorset.
- Apply the contract to every output route, including named standalone builders, editable starters, SVG exports, logos, textures, composition sheets, controls and reports. Named builders use `scripts/colorset_adapter.py` and default to colorset1; select colorset2 explicitly with their `--colorset` flag.
- Restrict gallery override values and their declared allowed list to the canonical selected set. For animated discrete semantic colors, map every SMIL `from`, `to`, `by` and `values` endpoint and use `calcMode="discrete"`; checking only the settled `fill` misses future palette leaks. Gradient endpoints and opacity may composite in the renderer, but authored stops remain canonical.
- Permit `none`, `currentColor`, `url(#...)`, and opacity as non-color SVG values. Resolve `currentColor` to an active token.
- Reject named colors, three/eight-digit hex, RGB/RGBA, HSL/HSLA, LCH/OKLCH, sampled image colors, and arbitrary user-supplied paint values.
- Do not interpolate through undeclared colors or use raw `d3-scale-chromatic` ramps. Build ordinal, threshold, or quantized ramps from active tokens.
- Prefer geometry, masks, dash offsets, opacity, transforms, or discrete token changes for animation.
- Apply the contract to page background, text, controls, focus states, tooltips, and SVG marks, not only the primary data series.

## Colorset1 — Standard

Colorset1 contains 17 red-neutral tokens. Allocate indexed category fills from
the bundled `solidSequence`: primary red `#9e1b32`, interleaved dark/middle grays
including black, white, then
the remaining colors. Exclude only the actual canvas token. These named roles
describe semantic paint and page structure separately from category order:

- background `#f7f7f7`
- surface `#ffffff`
- ink `#333e48`
- dark ink `#1c1c1c`
- primary `#9e1b32`
- primary dark `#6d1222`
- critical accent `#e8002a`
- last-resort pink `#ffccd5` (legacy `accentSoft`; outside default color assignments)
- muted `#828282`
- line `#cfcfcf`
- quiet surface `#e7e7e7`

Use primary red for the first indexed category and continue through the bundled
order for distinct categories. Reuse a fill for the same semantic role; retain
explicit status meanings and ordered-value scales. Use shape, position, and
direct labels alongside color.

Use white or `#e7e7e7` for page surfaces, with an opaque red mark when emphasis
is needed. Keep initial category faces borderless. Do not automatically select
pink for the second series, highlights, focus, replay, or additional nodes.
Only introduce pink for an additional meaningful category after all preceding
usable tokens in the complete sequence are exhausted: primary red, the
dark/middle gray interleave including black, white, then the remaining colors
in their listed order. An explicit pink
request may select it directly; retain justified status, brand and tonal meanings.
Reuse role colors before allocating a new token.

## Colorset2 — Extended

Colorset2 contains every colorset1 token plus blue, orange, green, yellow, purple, interaction, highlight, and status tokens. Its primary categorical sequence is:

`#9e1b32`, `#007298`, `#e77204`, `#45842a`, `#652f6c`, `#f1c319`.

Assign hues by meaning and keep the mapping stable across frames and linked views. Prefer one dominant hue plus neutrals when the data does not require six categories.

## Bind Categories Without Cycling Early

For a directly labeled grid or category catalogue, use
`scripts/build_category_grid.py` with `references/category-grid.md`.
It handles the entire ordinal/overflow contract, mobile geometry and actual
HTML-to-SVG export without manually rebuilding the allocator.

For an unsupported form, embed the chosen contract from
`assets/palettes/colorsets.json` as `window.D3_SOLID_PALETTES`, then inline
`assets/templates/solid-style.js` before the rendering script. The standalone
builders and `colorset_adapter.py` already bundle both resources. When using
the adapter, run the authored renderer on `DOMContentLoaded` so its appended
runtime is available. Inline the genuine unchanged
`assets/vendor/d3.v7.9.0.min.js` and use actual D3 joins; do not create a
lookalike API stub. Copy resources into the output; keep the skill bundle
read-only and do not add a fetch dependency on its installed path. Include
SVG title and desc in the authored HTML before its first validation command.

Pass the original category index directly to `categoryStyle`; do not reduce it
with modulo or force all strokes to `none`. On a white colorset1 canvas, indices
0–15 use distinct borderless fills, index 15 keeps `#ffccd5`, and index 16 starts
the contrasting overflow tier. Carry that allocation into every mark and legend:

```js
const activeColorset = "colorset1";
const actualCanvas = "#ffffff";
const categories = data.map((item, index) => ({
  ...item,
  style: window.D3SolidStyle.categoryStyle(index, activeColorset, actualCanvas)
}));
const marks = svg.selectAll("g.category").data(categories).join("g")
  .attr("class", "category")
  .attr("data-outline-tier", d => d.style.tier);
marks.append("rect")
  .attr("x", d => d.x).attr("y", d => d.y)
  .attr("width", d => d.width).attr("height", d => d.height)
  .attr("fill", d => d.style.fill)
  .attr("stroke", d => d.style.stroke)
  .attr("stroke-width", d => d.style.strokeWidth)
  .attr("stroke-dasharray", d => d.style.strokeDasharray);
marks.append("text")
  .attr("x", d => d.x + 8).attr("y", d => d.y + 20)
  .attr("fill", d => d.style.text)
  .text(d => d.label);
```

When a category index is part of the public contract, put
`data-category-index` on exactly one filled body per category; its label and
group inherit their association without duplicating that indexed body field.
The `data-outline-tier="overflow"` ancestor keeps valid overflow rims through
normalization. Preserve this metadata in exported SVG. Inspect computed styles
after Replay and export; source JSON or a manually cycled palette is insufficient.

## Contrast and Small-Size Gate

- Use exactly `#000000` or `#ffffff` for inside text, choosing the larger relative-luminance contrast against the actual fill or composited background.
- Place labels on readable containing faces or clear canvas space; use an opaque label face when mixed underlays prevent readable placement.
- Do not encode a state by hue alone; pair color with position, shape, texture, label, or stroke pattern.
- Inspect the intended desktop/mobile size. For logos, also inspect a 96 px-wide preview and simplify geometry or texture until the brand name remains recognizable.

## Logo-Specific Restrictions

- Do not use gradients in logo or texture outputs, even when every stop is palette-safe.
- Use filters only for alpha or geometry; never expose raw filter RGB output.
- Keep texture secondary to the wordmark or dominant silhouette.
- An intentional text-occlusion exception must follow `references/text-clearance-contract.md` and may never exceed its declared ratio.

## Validation

Run `scripts/check_palette_contract.py` on ordinary HTML or SVG output. For JavaScript-rendered HTML, also render in a browser and inspect computed SVG paint because the static checker intentionally ignores runtime script bodies. Use the dedicated logo/gallery browser validators when their route applies.
