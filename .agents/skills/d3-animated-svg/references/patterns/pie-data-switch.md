# Pie Data Switch

- **Pattern ID:** `d3-pattern-pie-data-switch`
- **Gallery source ID:** `pie-data-switch`
- **Family:** Transition
- **Use when:** Arc slices tween between two part-to-whole states.
- **Renderer:** `renderPieDataSwitch`

## Reuse Contract

- Use this file as the pattern source in isolated skill-only workspaces; read the gallery fixture only when maintaining that fixture.
- Keep data deterministic and inline small datasets.
- Preserve the pattern's core geometry and semantic color roles before changing labels or domain data.
- Use SVG-native animation for standalone output; do not leave runtime D3 or CDN dependencies in a self-contained deliverable.
- Include an SVG `<title>`, `<desc>`, stable `viewBox`, and final-state geometry.

## Source Excerpt

The excerpt below is the compact renderer source for this pattern. If it references helpers such as `prepareSvg`, `fadeIn`, `grow`, `drawPath`, `palette`, `ramps`, `axisBottom`, or `axisLeft`, read `references/shared-renderer-helpers.md` and recreate only the needed helper behavior in the final artifact.

```js
function renderPieDataSwitch() {
    const svg = prepareSvg("pie-data-switch", "Pie data switch", "Arc slices tween between two part-to-whole states.");
    const before = [18, 26, 14, 20, 22];
    const after = [30, 12, 24, 10, 24];
    const pie = d3.pie().sort(null);
    const arc = d3.arc().innerRadius(58).outerRadius(142).cornerRadius(4);
    const center = svg.append("g").attr("transform", `translate(${width / 2},${height / 2 + 8})`);
    const a = pie(before), b = pie(after);
    const slices = center.selectAll("path").data(b).join("path")
      .attr("d", d => arc(d)).attr("fill", (_, i) => colors[i]).attr("stroke", "#fff").attr("stroke-width", 2);
    slices.each(function (d, i) {
      d3.select(this).append("animate").attr("attributeName", "d")
        .attr("from", arc(a[i])).attr("to", arc(d)).attr("dur", "1s").attr("begin", `${.08 + i * .04}s`).attr("fill", "freeze");
    });
  }
```
