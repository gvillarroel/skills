# MLP Simple

- **Pattern ID:** `d3-pattern-mlp-simple`
- **Gallery source ID:** `mlp-simple`
- **Family:** AI
- **Use when:** Gray neurons pulse red one layer at a time.
- **Renderer:** `renderMlpSimple`

## Reuse Contract

- Use this file as the pattern source in isolated skill-only workspaces; read the gallery fixture only when maintaining that fixture.
- Keep data deterministic and inline small datasets.
- Preserve the pattern's core geometry and semantic color roles before changing labels or domain data.
- Use SVG-native animation for standalone output; do not leave runtime D3 or CDN dependencies in a self-contained deliverable.
- Include an SVG `<title>`, `<desc>`, stable `viewBox`, and final-state geometry.

## Source Excerpt

The excerpt below is the compact renderer source for this pattern. If it references helpers such as `prepareSvg`, `fadeIn`, `grow`, `drawPath`, `palette`, `ramps`, `axisBottom`, or `axisLeft`, read `references/shared-renderer-helpers.md` and recreate only the needed helper behavior in the final artifact.

```js
function renderMlpSimple() {
    const svg = prepareSvg("mlp-simple", "MLP simple network", "A multilayer perceptron activates each layer progressively.");
    const layout = mlpLayout([4, 5, 4, 2], [70, width - 70], [80, 318]);
    layout.nodes.forEach(d => d.r = d.layer === 0 || d.layer === layout.layers.length - 1 ? 12 : 13);
    const delayForLayer = layer => .2 + layer * 1.55;
    const link = d3.linkHorizontal().x(d => d.x).y(d => d.y);
    const paths = svg.append("g").selectAll("path").data(layout.links, d => d.id).join("path")
      .attr("d", d => link({ source: d.source, target: d.target }))
      .attr("fill", "none")
      .attr("stroke", palette.gray100)
      .attr("stroke-width", 1.5)
      .attr("stroke-opacity", .34)
      .attr("stroke-linecap", "round");
    const groups = svg.append("g").selectAll("g").data(layout.nodes, d => d.id).join("g")
      .attr("transform", d => `translate(${d.x},${d.y})`);
    const circles = groups.append("circle")
      .attr("r", d => d.r)
      .attr("fill", palette.gray200);
    pulseMlpNodes(circles, delayForLayer);
  }
```
