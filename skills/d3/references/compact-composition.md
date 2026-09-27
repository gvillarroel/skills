# Compact Composition

Apply this default to new D3 diagrams, dashboards, and controls. Preserve an
explicit user size, spacing, palette, or established semantic mapping.

## Boxes and page layout

| Element | Default |
| --- | --- |
| Diagram node | 6 px vertical, 10 px horizontal padding around measured text |
| Panel or card | 12 px padding; 8 px between heading and content |
| UI group | 8 px gap; remove empty header/footer rows |
| Button | 4 px vertical, 10 px horizontal padding; at least 32 px high |
| Touch button | At least 44 px high when the primary pointer is coarse |
| Tooltip or status | 4 px vertical, 8 px horizontal padding |

Measure labels with `getBBox()` after setting their final font. Derive box
height from line count and font metrics; a one-line 16 px label usually needs
about 30–34 px. Increase a box for wrapping, not every box for the longest
label. Keep diagram labels around 14–16 px at the intended display size.
Use separate hit areas when a compact visible mark needs a larger pointer target.

Remove unused vertical canvas space for a short process. The contract flow
builder defaults to a 180 px canvas and measured nodes with 6 px vertical
padding; `--height` preserves an explicitly requested canvas, and
`--node-padding-y` / `--node-padding-x` override box padding. Its minimum node
height is 32 px. Check arrow endpoints after changing dimensions.

Do not confuse `scaleBand().padding()` with CSS/node padding: band spacing
changes bar thickness and chart rhythm. Preserve quantitative scales, Sankey
widths, matrix cells, force distances, axis labels, legends, and useful whitespace.
For a dense or narrow diagram, wrap/reflow or provide a scrollable native-size
view before shrinking text to fit. Preserve an explicit `viewBox` contract.

## Color hierarchy

Start with white/light gray surfaces and dark neutral text. Use one deliberate
red role and reuse the same role across all nodes, frames, and linked views.
Use grayscale, labels, shape, stroke weight, or dash pattern for further
distinctions. More objects do not automatically require more colors.

Use `#e7e7e7` for a quiet selected surface and an opaque red outline or mark for
emphasis. Do not wash large red surfaces with white to simulate a pink secondary
category. Keep `#ffccd5` outside automatic sequences; use it only when remaining
red/neutral choices cannot distinguish an additional meaningful category, or
when explicitly requested. Record that reason. Colorset2 remains opt-in.

## Verify

Render at desktop and mobile sizes. Inspect the actual painted colors, label
fit, arrow clearance, final font sizes, and control targets. Compare bounding
boxes before/after; do not infer compactness from CSS alone. Run the palette
check on the extracted settled SVG as well as the source HTML.
