# Compact Composition

Apply this default to new D3 diagrams, dashboards, and controls. Preserve an
explicit user size, spacing, palette, or established semantic mapping.

## Connected diagrams

Default to the smallest readable occupied layout for processes, node-link
networks, architecture, dependency trees and explanatory mechanisms. Measure
text with its final font, size each node to its own content, then shorten gaps
and routes and trim unused outer space. Prefer reordering siblings, moving a
port or reflowing a branch over reducing text, arrowheads or meaningful strokes.

Reserve each label's painted bounds, complete arrowhead, source/target port,
separate parallel/return lanes and the swept bounds of moving tokens. A short
connector still needs a visible shaft and direction. Do not merge unrelated
edges into an ambiguous shared segment or route through another node/label.
Keep a necessary crossing visibly traceable; reroute when its endpoints become
ambiguous. Inspect at the actual display size, including motion and reduced
motion when present. Try a tighter layout, compare its occupied bounds and
readability with the previous render, and retain it only when space decreases
and readability and fidelity stay at least as good.
Stop after the local spacing/reflow alternatives stop saving space safely;
keep the last passing layout instead of chasing a packing ratio.

The contract builder packs flow nodes from measured text and attaches network
arrows outside measured circles. Omitted diagram dimensions use content bounds;
explicit `--width`/`--height` remain fixed. Distinct return/skip/parallel flow
links get separate lanes. If a fixed canvas cannot contain the readable geometry,
report that constraint rather than scaling down the font.

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

In an adjustable logo or illustration studio, show the preview before the
controls on a narrow screen. Use the artwork's aspect ratio instead of a fixed
430 px minimum viewport. Split short controls into two columns when labels fit,
and keep an explicit expanded view for dense chart labels. A compact gallery
thumbnail does not replace inspection at the source's native dimensions.

Remove unused vertical canvas space for a short process. The contract flow
builder starts from measured nodes with 6 px vertical
padding and crops omitted dimensions to content; `--height` preserves an explicitly requested canvas, and
`--node-padding-y` / `--node-padding-x` override box padding. Its minimum node
height is 32 px. Check arrow endpoints after changing dimensions.

Do not confuse `scaleBand().padding()` with CSS/node padding: band spacing
changes bar thickness and chart rhythm. Preserve quantitative scales, Sankey
widths, matrix cells, physically meaningful force distances, axis labels,
legends, and useful whitespace. For a conceptual network, tune layout distances
to measured label and route clearance instead of preserving arbitrary gaps.
For a dense or narrow diagram, wrap/reflow or provide a scrollable native-size
view before shrinking text to fit. Preserve an explicit `viewBox` contract.

## Color hierarchy

Start with white/light gray surfaces and dark neutral text. Use one deliberate
red role and reuse the same role across all nodes, frames, and linked views.
Use grayscale, labels, shape, stroke weight, or dash pattern for further
distinctions. More objects do not automatically require more colors.

Use a solid red fill or a direct label for
emphasis. Do not wash large red surfaces with white to simulate a pink secondary
category. Keep `#ffccd5` outside automatic sequences; use it only when remaining
red/neutral choices cannot distinguish an additional meaningful category, or
when explicitly requested. Record that reason. Colorset2 remains opt-in.

## Verify

Render at desktop and mobile sizes. Inspect the actual painted colors, label
fit, arrow clearance, final font sizes, and control targets. Compare bounding
boxes before/after; do not infer compactness from CSS alone. Run the palette
check on the extracted settled SVG as well as the source HTML.
