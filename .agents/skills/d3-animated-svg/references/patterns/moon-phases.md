# Moon Phases

- **Pattern ID:** `d3-pattern-moon-phases`
- **Gallery source ID:** `moon-phases`
- **Family:** Astronomy
- **Use when:** Repeated masks show the lunar cycle as changing illumination.
- **Renderer:** `renderMoonPhases`

## Reuse Contract

- Use this file as the pattern source in isolated skill-only workspaces; read the gallery fixture only when maintaining that fixture.
- Keep data deterministic and inline small datasets.
- Preserve the pattern's core geometry and semantic color roles before changing labels or domain data.
- Use SVG-native animation for standalone output; do not leave runtime D3 or CDN dependencies in a self-contained deliverable.
- Include an SVG `<title>`, `<desc>`, stable `viewBox`, and final-state geometry.

## Source Excerpt

The excerpt below is the compact renderer source for this pattern. If it references helpers such as `prepareSvg`, `fadeIn`, `grow`, `drawPath`, `palette`, `ramps`, `axisBottom`, or `axisLeft`, read `references/shared-renderer-helpers.md` and recreate only the needed helper behavior in the final artifact.

```js
function renderMoonPhases() {
    const svg = prepareSvg("moon-phases", "Moon phases", "Repeated masks show a simplified lunar illumination cycle.");
    const phases = d3.range(8).map(i => ({ i, phase: i / 7 }));
    const groups = svg.append("g").selectAll("g").data(phases).join("g")
      .attr("transform", d => `translate(${74 + (d.i % 4) * 136},${128 + Math.floor(d.i / 4) * 128})`);
    groups.append("circle").attr("r", 34).attr("fill", palette.gray900).attr("stroke", palette.gray200).attr("stroke-width", 2);
    groups.append("circle").attr("r", 34).attr("fill", palette.yellowHighlight).attr("clip-path", d => `url(#moon-phase-clip-${d.i})`);
    const defs = svg.append("defs");
    phases.forEach(d => {
      const offset = (d.phase - .5) * .82;
      const clip = defs.append("clipPath").attr("id", `moon-phase-clip-${d.i}`).attr("clipPathUnits", "objectBoundingBox");
      clip.append("ellipse").attr("cx", .5 + offset).attr("cy", .5).attr("rx", Math.max(.04, Math.abs(Math.cos(d.phase * Math.PI)) * .5)).attr("ry", .5);
    });
    fadeIn(groups, .08, .65);
    groups.append("text").attr("class", "mark-label").attr("text-anchor", "middle").attr("dy", 56).text(d => `${Math.round(d.phase * 100)}%`);
  }
```
