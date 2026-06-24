# Bivariate Choropleth

- **Pattern ID:** `d3-pattern-bivariate-choropleth`
- **Gallery source ID:** `bivariate-choropleth`
- **Family:** Geospatial
- **Use when:** Two metrics combine into a 3-by-3 regional color key.
- **Renderer:** `renderBivariateChoropleth`

## Reuse Contract

- Use this file as the pattern source in isolated skill-only workspaces; read the gallery fixture only when maintaining that fixture.
- Keep data deterministic and inline small datasets.
- Preserve the pattern's core geometry and semantic color roles before changing labels or domain data.
- Use SVG-native animation for standalone output; do not leave runtime D3 or CDN dependencies in a self-contained deliverable.
- Include an SVG `<title>`, `<desc>`, stable `viewBox`, and final-state geometry.

## Source Excerpt

The excerpt below is the compact renderer source for this pattern. If it references helpers such as `prepareSvg`, `fadeIn`, `grow`, `drawPath`, `palette`, `ramps`, `axisBottom`, or `axisLeft`, read `references/shared-renderer-helpers.md` and recreate only the needed helper behavior in the final artifact.

```js
function renderBivariateChoropleth() {
    const svg = prepareSvg("bivariate-choropleth", "Bivariate choropleth", "Two regional metrics combine into a compact color matrix.");
    const palette2 = ramps.bivariate;
    const regions = d3.range(18).map(i => ({
      x: 86 + (i % 6) * 56 + ((i % 2) * 8),
      y: 72 + Math.floor(i / 6) * 74,
      a: i % 3,
      b: Math.floor((i * 5) % 9 / 3),
      label: String.fromCharCode(65 + i)
    }));
    const cells = svg.append("g").selectAll("path").data(regions).join("path")
      .attr("d", d => {
        const pts = [[d.x, d.y], [d.x + 44, d.y + 8], [d.x + 38, d.y + 48], [d.x - 8, d.y + 42]];
        return `${d3.line()(pts)}Z`;
      })
      .attr("fill", d => palette2[d.b][d.a])
      .attr("stroke", "#fff")
      .attr("stroke-width", 2);
    fadeIn(cells, .04, .55);
    svg.append("g").selectAll("text").data(regions).join("text")
      .attr("class", "mark-label").attr("x", d => d.x + 18).attr("y", d => d.y + 28).attr("text-anchor", "middle").text(d => d.label);
    const key = svg.append("g").attr("transform", "translate(410,246)");
    d3.range(9).forEach(i => {
      const a = i % 3, b = Math.floor(i / 3);
      key.append("rect").attr("x", a * 24).attr("y", (2 - b) * 24).attr("width", 22).attr("height", 22).attr("fill", palette2[b][a]).attr("stroke", "#fff");
    });
    key.append("text").attr("class", "label").attr("x", 36).attr("y", 88).attr("text-anchor", "middle").text("A + B");
  }
```
