# Solar Terminator

- **Pattern ID:** `d3-pattern-solar-terminator`
- **Gallery source ID:** `solar-terminator`
- **Family:** Geospatial
- **Use when:** A day-night boundary sweeps across a world grid.
- **Renderer:** `renderSolarTerminator`

## Reuse Contract

- Use this file as the pattern source in isolated skill-only workspaces; read the gallery fixture only when maintaining that fixture.
- Keep data deterministic and inline small datasets.
- Preserve the pattern's core geometry and semantic color roles before changing labels or domain data.
- Use SVG-native animation for standalone output; do not leave runtime D3 or CDN dependencies in a self-contained deliverable.
- Include an SVG `<title>`, `<desc>`, stable `viewBox`, and final-state geometry.

## Source Excerpt

The excerpt below is the compact renderer source for this pattern. If it references helpers such as `prepareSvg`, `fadeIn`, `grow`, `drawPath`, `palette`, `ramps`, `axisBottom`, or `axisLeft`, read `references/shared-renderer-helpers.md` and recreate only the needed helper behavior in the final artifact.

```js
function renderSolarTerminator() {
    const svg = prepareSvg("solar-terminator", "Solar terminator", "A day-night boundary sweeps across a gridded world view.");
    const plot = { x: 48, y: 58, w: 464, h: 260 };
    svg.append("rect").attr("x", plot.x).attr("y", plot.y).attr("width", plot.w).attr("height", plot.h).attr("rx", 8).attr("fill", palette.blueHighlight).attr("stroke", palette.gray200);
    d3.range(1, 6).forEach(i => svg.append("line").attr("x1", plot.x + i * plot.w / 6).attr("x2", plot.x + i * plot.w / 6).attr("y1", plot.y).attr("y2", plot.y + plot.h).attr("stroke", palette.gray200));
    d3.range(1, 4).forEach(i => svg.append("line").attr("x1", plot.x).attr("x2", plot.x + plot.w).attr("y1", plot.y + i * plot.h / 4).attr("y2", plot.y + i * plot.h / 4).attr("stroke", palette.gray200));
    const boundary = d3.range(0, 101).map(i => {
      const x = plot.x + i / 100 * plot.w;
      const y = plot.y + plot.h / 2 + Math.sin(i / 100 * Math.PI * 2 - .7) * 48;
      return [x, y];
    });
    const night = [[plot.x, plot.y], [plot.x + plot.w, plot.y], ...boundary.slice().reverse(), [plot.x, plot.y]];
    const nightPath = svg.append("path").attr("d", `${d3.line()(night)}Z`).attr("fill", palette.ink).attr("fill-opacity", .38);
    fadeIn(nightPath, .12, .55);
    const line = svg.append("path").attr("d", d3.line()(boundary)).attr("fill", "none").attr("stroke", palette.orange).attr("stroke-width", 3.5);
    drawPath(line, .15, 1);
    svg.append("circle").attr("cx", plot.x + plot.w - 52).attr("cy", plot.y + 42).attr("r", 16).attr("fill", palette.gold).attr("stroke", palette.yellowHover).attr("stroke-width", 2);
  }
```
