# Circular Barplot

- **Pattern ID:** `d3-pattern-circular-bar`
- **Gallery source ID:** `circular-bar`
- **Family:** Ranking
- **Use when:** Radial magnitude around a categorical wheel.
- **Renderer:** `renderCircularBar`

## Reuse Contract

- Use this file as the pattern source in isolated skill-only workspaces; read the gallery fixture only when maintaining that fixture.
- Keep data deterministic and inline small datasets.
- Preserve the pattern's core geometry and semantic color roles before changing labels or domain data.
- Use SVG-native animation for standalone output; do not leave runtime D3 or CDN dependencies in a self-contained deliverable.
- Include an SVG `<title>`, `<desc>`, stable `viewBox`, and final-state geometry.

## Source Excerpt

The excerpt below is the compact renderer source for this pattern. If it references helpers such as `prepareSvg`, `fadeIn`, `grow`, `drawPath`, `palette`, `ramps`, `axisBottom`, or `axisLeft`, read `references/shared-renderer-helpers.md` and recreate only the needed helper behavior in the final artifact.

```js
function renderCircularBar() {
    const svg = prepareSvg("circular-bar", "Circular barplot", "Categorical magnitudes arranged around a radial axis.");
    const data = d3.range(18).map(i => ({ name: `C${i + 1}`, value: 30 + (i * 17) % 70 }));
    const inner = 68, outer = 166;
    const x = d3.scaleBand().domain(data.map(d => d.name)).range([0, 2 * Math.PI]).padding(.08);
    const y = d3.scaleRadial().domain([0, 100]).range([inner, outer]);
    const arc = d3.arc().innerRadius(inner).outerRadius(d => y(d.value)).startAngle(d => x(d.name)).endAngle(d => x(d.name) + x.bandwidth()).padAngle(.01);
    const g = svg.append("g").attr("transform", `translate(${width / 2},${height / 2 + 14})`);
    const bars = g.selectAll("path").data(data).join("path").attr("d", arc).attr("fill", (d, i) => colors[i % colors.length]).attr("fill-opacity", .86);
    fadeIn(bars, .06, .75);
  }
```
