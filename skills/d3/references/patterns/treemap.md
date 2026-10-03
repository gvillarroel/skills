# Treemap

## Contents

- [Reuse Contract](#reuse-contract)
- [Borderless Sibling Tones](#borderless-sibling-tones)
- [Standalone Builder](#standalone-builder)
- [Source Excerpt](#source-excerpt)

- **Pattern ID:** `d3-treemap`
- **Gallery source ID:** `treemap`
- **Family:** Hierarchy
- **Use when:** Nested area allocation with readable groups.
- **Renderer:** `renderTreemap`

## Reuse Contract

- Use this file as the pattern source in isolated skill-only workspaces; read the gallery fixture only when maintaining that fixture.
- Keep data deterministic and inline small datasets.
- Preserve the pattern's core geometry and semantic color roles before changing labels or domain data.
- Use SVG-native animation for standalone output; do not leave runtime D3 or CDN dependencies in a self-contained deliverable.
- Include an SVG `<title>`, `<desc>`, stable `viewBox`, and final-state geometry.

## Borderless Sibling Tones

Use stepped solid family tones when sibling cells disappear into their parent's fill. Keep the existing D3 area layout, values, ordering and branch mapping. Paint each parent's body with the neutral canvas and reserve its original category fill for a header inside `paddingTop`; keep real empty gutters between leaves. Do not paint a continuous colored parent behind identically colored children or replace gutters with strokes.

Set `activeColorset` from the requested palette, defaulting to `colorset1`. Recreate only the needed `palette` keys from the bundled contract. For the excerpt's three branch families, colorset1 maps `blue` to `#9e1b32`, `orange` to `#696969`, and `green` to `#4f4f4f`. Its sibling ramps are dark-to-bright red (`#6d1222`, `#9e1b32`, `#e8002a`) and two stepped gray families (`#4f4f4f`, `#828282`, `#b5b5b5`; `#363636`, `#696969`, `#9c9c9c`). Colorset2 uses the corresponding dark/base/bright blue, orange and green tokens. Keep all fills opaque and borderless; each cell uses one token, with no gradients or interpolated colors.

Choose a tone from the sibling's stable sorted position. A single child uses the middle tone; two use the endpoints; three use all steps. More siblings quantize to the finite ramp and remain individually separated by neutral gutters and direct labels; do not claim that every additional sibling has a unique color. Tone distinguishes cells within a family, while area alone communicates value. Keep tone assignments unchanged across Replay, resizing and export. Choose exact black or white by maximum luminance contrast for the actual header or leaf fill, and show requested values inside the available cell space.

Validation hooks: inspect actual rendered sibling fills after any shared paint normalizer; require distinct increasing-luminance tones for this three-child fixture, opaque paint, no decorative strokes, visible neutral gutters, and labels contained in their header or leaf with at least 4.5:1 contrast. Check desktop, narrow layout, Replay twice, reduced motion and the standalone SVG. Preserve canonical IDs including `d3-treemap-cs1` and `d3-treemap-cs2`.

## Standalone Builder

For a new two-level treemap, use `scripts/build_treemap.py` instead of recreating the renderer by hand. Write the supplied hierarchy to an owned JSON file with a named root, named branch `children`, and named leaf `children` containing positive numeric `value` fields. Keep every supplied label and value exact. The builder embeds the bundled offline D3 runtime, computes the weighted layout, shows leaf names and values, and applies the colorset finalizer automatically. It uses native D3 dice for vertical branch columns and slice for weighted leaf rows, retaining enough width for direct labels on narrow screens. A finalized HTML avoids metadata omissions and inconsistent text paint between HTML and export.

```text
python <d3-skill>/scripts/build_treemap.py --help
python <d3-skill>/scripts/build_treemap.py --data <owned-input>/hierarchy.json --output <requested.html> --title "Requested title" --colorset colorset1
python <d3-skill>/scripts/check_self_contained_html.py <requested.html>
python <d3-skill>/scripts/check_palette_contract.py <requested.html> --colorset colorset1
uv run --script <d3-skill>/scripts/render_d3_svg.py <requested.html> --output <requested.svg> --screenshot <owned-scratch>/treemap.png --wait-ms 1200 --viewport 960x720
python <d3-skill>/scripts/check_palette_contract.py <requested.svg> --colorset colorset1
```

The builder's SVG root has `id="treemap"`; its canonical pattern metadata is `data-pattern-id="d3-treemap-cs1"` or `d3-treemap-cs2`. Use `--require-id treemap` if checking the root with `check_visual_contract.py`, and derive any class cardinality from the requested input. Check only IDs and counts supplied by the caller or documented builder contract.

Use `colorset2` consistently for an explicit extended-palette request. Keep generated input, output and screenshots outside the read-only skill bundle. Do not post-edit a supported builder output: correct the input or flags, rerun the builder, then export from its finalized HTML. Inspect names, values, area proportions, all sibling tones, header and leaf text at desktop and narrow widths, Replay twice, reduced motion and the exported SVG. More than three siblings share the finite ramp; neutral gutters and direct labels retain cell identity. For an extreme tiny cell that cannot fit readable direct text, the builder supplies a complete visible data key below the SVG rather than omitting a name or value. Normal-sized cells keep their labels inside the cell.

The source excerpt below remains the maintenance recipe for the published gallery. Preserve its existing data and coordinates when repairing that fixture; a new hierarchy uses its own D3 geometry through the standalone builder.

## Source Excerpt

The excerpt below is the compact renderer source for this pattern. If it references helpers such as `prepareSvg`, `fadeIn`, `grow`, `drawPath`, `palette`, `ramps`, `axisBottom`, or `axisLeft`, read `references/shared-renderer-helpers.md` and recreate only the needed helper behavior in the final artifact.

```js
function renderTreemap() {
    const svg = prepareSvg("treemap", "Treemap", "D3 treemap layout showing nested area allocation. Stepped solid tones distinguish siblings; cell area encodes value.");
    const root = d3.hierarchy(hierarchyData()).sum(d => d.value || 0).sort((a, b) => b.value - a.value);
    d3.treemap().size([width - 48, height - 56]).paddingOuter(5).paddingTop(20).paddingInner(3).round(true)(root);
    const g = svg.append("g").attr("transform", "translate(24,28)");
    const color = d3.scaleOrdinal(root.children.map(d => d.data.name), colors);
    const branchName = d => d.ancestors().find(node => node.depth === 1).data.name;
    const familyTones = new Map(activeColorset === "colorset1" ? [
      [palette.blue, [palette.redHover, palette.red, palette.error]],
      [palette.orange, [palette.gray700, palette.gray500, palette.gray300]],
      [palette.green, [palette.gray800, palette.gray600, palette.gray400]]
    ] : [
      [palette.blue, [palette.blueHover, palette.blue, palette.cyan]],
      [palette.orange, [palette.orangeHover, palette.orange, palette.warning]],
      [palette.green, [palette.greenHover, palette.green, palette.success]]
    ]);
    const toneIndex = d => {
      const siblings = d.parent.children;
      return siblings.length === 1 ? 1 : Math.round(siblings.indexOf(d) * 2 / (siblings.length - 1));
    };
    const cellFill = d => {
      const base = color(branchName(d));
      return (familyTones.get(base) || [palette.gray800, palette.gray500, palette.gray200])[toneIndex(d)];
    };
    const textFor = fill => {
      const channels = [1, 3, 5].map(i => parseInt(fill.slice(i, i + 2), 16) / 255)
        .map(v => v <= .04045 ? v / 12.92 : ((v + .055) / 1.055) ** 2.4);
      const luminance = channels.reduce((sum, value, i) => sum + value * [.2126, .7152, .0722][i], 0);
      return (luminance + .05) / .05 >= 1.05 / (luminance + .05) ? palette.black : palette.white;
    };
    const nodes = g.selectAll("g").data(root.descendants().filter(d => d.depth)).join("g")
      .attr("class", d => `treemap-node ${d.children ? "treemap-parent" : "treemap-leaf"}`)
      .attr("data-name", d => d.data.name).attr("data-branch", branchName).attr("data-value", d => d.value)
      .attr("data-text-backing", d => d.children ? ".treemap-branch-header" : ".treemap-leaf-cell")
      .attr("transform", d => `translate(${d.x0},${d.y0})`);
    nodes.append("rect").attr("class", d => d.children ? "treemap-branch-backing" : "treemap-leaf-cell")
      .attr("width", d => Math.max(0, d.x1 - d.x0)).attr("height", d => Math.max(0, d.y1 - d.y0))
      .attr("data-tone-index", d => d.children ? null : toneIndex(d))
      .attr("rx", 3).attr("fill", d => d.children ? palette.surface : cellFill(d)).attr("fill-opacity", 1)
      .attr("stroke", "none");
    nodes.filter(d => d.children).append("rect").attr("class", "treemap-branch-header")
      .attr("width", d => Math.max(0, d.x1 - d.x0)).attr("height", 18).attr("rx", 3)
      .attr("fill", d => color(branchName(d))).attr("stroke", "none");
    nodes.filter(d => d.children && (d.x1 - d.x0) > 52 && (d.y1 - d.y0) > 22).append("text")
      .attr("class", "treemap-parent-label")
      .attr("x", 7).attr("y", 15)
      .attr("fill", d => textFor(color(branchName(d))))
      .attr("stroke", "none")
      .attr("font-size", 12)
      .attr("font-weight", 800)
      .text(d => d.data.name);
    nodes.filter(d => !d.children && (d.x1 - d.x0) > 52 && (d.y1 - d.y0) > 24).append("text")
      .attr("class", "treemap-leaf-label")
      .attr("x", 7).attr("y", 17)
      .attr("fill", d => textFor(cellFill(d)))
      .attr("stroke", "none")
      .attr("font-size", 12)
      .attr("font-weight", 760)
      .text(d => d.data.name);
    fadeIn(nodes, .05, .7);
  }
```
