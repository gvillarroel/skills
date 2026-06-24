# Projection Comparison

- **Pattern ID:** `d3-pattern-projection-comparison`
- **Gallery source ID:** `projection-comparison`
- **Family:** Projection
- **Use when:** The same coordinates expose projection distortion side by side.
- **Renderer:** `renderProjectionComparison`

## Reuse Contract

- Use this file as the pattern source in isolated skill-only workspaces; read the gallery fixture only when maintaining that fixture.
- Keep data deterministic and inline small datasets.
- Preserve the pattern's core geometry and semantic color roles before changing labels or domain data.
- Use SVG-native animation for standalone output; do not leave runtime D3 or CDN dependencies in a self-contained deliverable.
- Include an SVG `<title>`, `<desc>`, stable `viewBox`, and final-state geometry.

## Source Excerpt

The excerpt below is the compact renderer source for this pattern. If it references helpers such as `prepareSvg`, `fadeIn`, `grow`, `drawPath`, `palette`, `ramps`, `axisBottom`, or `axisLeft`, read `references/shared-renderer-helpers.md` and recreate only the needed helper behavior in the final artifact.

```js
function renderProjectionComparison() {
    const svg = prepareSvg("projection-comparison", "Projection comparison", "The same graticule and route expose projection distortion.");
    const sphere = { type: "Sphere" };
    const graticule = d3.geoGraticule().step([30, 30]).lines();
    const route = { type: "LineString", coordinates: [[-120, 35], [-60, 50], [0, 20], [72, 30], [135, -15]] };
    const projections = [
      { name: "Mercator", p: d3.geoMercator().scale(53).translate([151, 184]) },
      { name: "Natural", p: d3.geoNaturalEarth1().fitExtent([[302, 66], [518, 302]], sphere) }
    ];
    projections.forEach((item, pi) => {
      const path = d3.geoPath(item.p);
      svg.append("rect").attr("x", pi === 0 ? 44 : 302).attr("y", 66).attr("width", pi === 0 ? 214 : 216).attr("height", 236).attr("rx", 6).attr("fill", palette.gray50).attr("stroke", palette.gray200);
      svg.append("g").selectAll("path").data(graticule).join("path").attr("d", path).attr("fill", "none").attr("stroke", palette.gray100).attr("stroke-width", .8);
      const routePath = svg.append("path").datum(route).attr("d", path).attr("fill", "none").attr("stroke", colors[pi]).attr("stroke-width", 3.2);
      drawPath(routePath, .12, .85);
      svg.append("text").attr("class", "mark-label").attr("x", pi === 0 ? 151 : 410).attr("y", 334).attr("text-anchor", "middle").text(item.name);
    });
  }
```
