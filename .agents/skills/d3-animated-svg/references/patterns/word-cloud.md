# Word Cloud

- **Pattern ID:** `d3-pattern-word-cloud`
- **Gallery source ID:** `word-cloud`
- **Family:** Text
- **Use when:** Weighted terms occupy an animated text layout.
- **Renderer:** `renderWordCloud`

## Reuse Contract

- Use this file as the pattern source in isolated skill-only workspaces; read the gallery fixture only when maintaining that fixture.
- Keep data deterministic and inline small datasets.
- Preserve the pattern's core geometry and semantic color roles before changing labels or domain data.
- Use SVG-native animation for standalone output; do not leave runtime D3 or CDN dependencies in a self-contained deliverable.
- Include an SVG `<title>`, `<desc>`, stable `viewBox`, and final-state geometry.

## Source Excerpt

The excerpt below is the compact renderer source for this pattern. If it references helpers such as `prepareSvg`, `fadeIn`, `grow`, `drawPath`, `palette`, `ramps`, `axisBottom`, or `axisLeft`, read `references/shared-renderer-helpers.md` and recreate only the needed helper behavior in the final artifact.

```js
function renderWordCloud() {
    const svg = prepareSvg("word-cloud", "Word cloud", "Weighted text marks are placed around a compact semantic center.");
    const terms = [
      ["D3", 100], ["SVG", 82], ["layout", 68], ["scales", 58], ["joins", 54], ["force", 46],
      ["paths", 43], ["axis", 38], ["hierarchy", 36], ["voronoi", 34], ["motion", 31], ["shape", 29],
      ["data", 27], ["brush", 25], ["ticks", 23], ["ribbon", 21], ["cells", 19], ["labels", 18]
    ].map(([text, value], i) => ({ text, value, i }));
    const size = d3.scaleSqrt().domain(d3.extent(terms, d => d.value)).range([14, 54]);
    const color = d3.scaleOrdinal(terms.map(d => d.text), [palette.ink, palette.blue, palette.red, palette.orange, palette.green, palette.purple, palette.gray700]);
    const placed = terms.map((d, i) => {
      const angle = i * 2.32;
      const radius = i === 0 ? 0 : 24 + i * 8.8;
      return {
        ...d,
        x: width / 2 + Math.cos(angle) * radius * 1.18,
        y: height / 2 + Math.sin(angle) * radius * .72,
        rotate: i % 5 === 0 ? -24 : i % 4 === 0 ? 22 : 0
      };
    });
    const words = svg.append("g").selectAll("text").data(placed).join("text")
      .attr("x", d => d.x)
      .attr("y", d => d.y)
      .attr("text-anchor", "middle")
      .attr("dominant-baseline", "central")
      .attr("font-size", d => size(d.value))
      .attr("font-weight", d => d.value > 50 ? 750 : 600)
      .attr("fill", d => color(d.text))
      .attr("transform", d => `rotate(${d.rotate},${d.x},${d.y})`)
      .text(d => d.text);
    fadeIn(words, .04, .7);
    words.each(function (_, i) {
      d3.select(this).append("animateTransform")
        .attr("attributeName", "transform")
        .attr("type", "scale")
        .attr("additive", "sum")
        .attr("from", ".82")
        .attr("to", "1")
        .attr("dur", ".65s")
        .attr("begin", `${i * .025}s`)
        .attr("fill", "freeze");
    });
  }
```
