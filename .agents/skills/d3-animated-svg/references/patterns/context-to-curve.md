# Context to Curve

- **Pattern ID:** `d3-pattern-context-to-curve`
- **Gallery source ID:** `context-to-curve`
- **Family:** Geometry
- **Use when:** The same control points render through multiple D3 curve contexts.
- **Renderer:** `renderContextToCurve`

## Reuse Contract

- Use this file as the pattern source in isolated skill-only workspaces; read the gallery fixture only when maintaining that fixture.
- Keep data deterministic and inline small datasets.
- Preserve the pattern's core geometry and semantic color roles before changing labels or domain data.
- Use SVG-native animation for standalone output; do not leave runtime D3 or CDN dependencies in a self-contained deliverable.
- Include an SVG `<title>`, `<desc>`, stable `viewBox`, and final-state geometry.

## Source Excerpt

The excerpt below is the compact renderer source for this pattern. If it references helpers such as `prepareSvg`, `fadeIn`, `grow`, `drawPath`, `palette`, `ramps`, `axisBottom`, or `axisLeft`, read `references/shared-renderer-helpers.md` and recreate only the needed helper behavior in the final artifact.

```js
function renderContextToCurve() {
    const svg = prepareSvg("context-to-curve", "Context to curve", "The same control points render through multiple D3 curve contexts.");
    const points = [[62, 304], [132, 112], [208, 216], [288, 82], [372, 244], [488, 126]];
    const curves = [
      { name: "linear", curve: d3.curveLinear, y: 0, c: palette.gray600 },
      { name: "basis", curve: d3.curveBasis, y: 16, c: palette.blue },
      { name: "step", curve: d3.curveStep, y: 32, c: palette.red }
    ];
    curves.forEach((item, i) => {
      const shifted = points.map(p => [p[0], p[1] + item.y]);
      const path = svg.append("path").datum(shifted).attr("d", d3.line().curve(item.curve)).attr("fill", "none").attr("stroke", item.c).attr("stroke-width", i === 0 ? 2 : 3).attr("stroke-opacity", i === 0 ? .55 : .9);
      drawPath(path, .08 + i * .08, .85);
      svg.append("text").attr("class", "mark-label").attr("x", 488).attr("y", shifted.at(-1)[1] + 16).attr("text-anchor", "end").text(item.name);
    });
    svg.append("g").selectAll("circle").data(points).join("circle").attr("cx", d => d[0]).attr("cy", d => d[1]).attr("r", 4).attr("fill", palette.ink);
  }
```
