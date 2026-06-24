# Antimeridian Cutting

- **Pattern ID:** `d3-pattern-antimeridian-cutting`
- **Gallery source ID:** `antimeridian-cutting`
- **Family:** Projection
- **Use when:** A route splits cleanly at the dateline instead of crossing the map.
- **Renderer:** `renderAntimeridianCutting`

## Reuse Contract

- Use this file as the pattern source in isolated skill-only workspaces; read the gallery fixture only when maintaining that fixture.
- Keep data deterministic and inline small datasets.
- Preserve the pattern's core geometry and semantic color roles before changing labels or domain data.
- Use SVG-native animation for standalone output; do not leave runtime D3 or CDN dependencies in a self-contained deliverable.
- Include an SVG `<title>`, `<desc>`, stable `viewBox`, and final-state geometry.

## Source Excerpt

The excerpt below is the compact renderer source for this pattern. If it references helpers such as `prepareSvg`, `fadeIn`, `grow`, `drawPath`, `palette`, `ramps`, `axisBottom`, or `axisLeft`, read `references/shared-renderer-helpers.md` and recreate only the needed helper behavior in the final artifact.

```js
function renderAntimeridianCutting() {
    const svg = prepareSvg("antimeridian-cutting", "Antimeridian cutting", "A route splits cleanly at the dateline instead of crossing the map.");
    const projection = d3.geoEquirectangular().fitExtent([[52, 58], [508, 334]], { type: "Sphere" });
    const path = d3.geoPath(projection);
    svg.append("path").datum({ type: "Sphere" }).attr("d", path).attr("fill", "#f7f7f7").attr("stroke", palette.line);
    svg.append("g").selectAll("path").data(d3.geoGraticule().step([30, 30]).lines()).join("path")
      .attr("d", path).attr("fill", "none").attr("stroke", palette.gray200).attr("stroke-width", .8);
    const seamX = projection([180, 0])[0];
    svg.append("line").attr("x1", seamX).attr("x2", seamX).attr("y1", 58).attr("y2", 334).attr("stroke", palette.red).attr("stroke-width", 2).attr("stroke-opacity", .72).attr("stroke-dasharray", "6 4");
    const segments = [
      { type: "LineString", coordinates: [[132, 36], [160, 42], [179, 38]] },
      { type: "LineString", coordinates: [[-179, 38], [-150, 34], [-124, 40]] }
    ];
    const routes = svg.append("g").selectAll("path").data(segments).join("path").attr("d", path).attr("fill", "none").attr("stroke", palette.blueHover).attr("stroke-width", 3.4).attr("stroke-linecap", "round");
    drawPath(routes, .1, .85);
    svg.append("text").attr("class", "mark-label").attr("x", seamX - 8).attr("y", 52).attr("text-anchor", "end").text("180 deg seam");
  }
```
