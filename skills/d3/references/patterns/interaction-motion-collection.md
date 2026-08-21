# Interaction and Motion Pattern Collection

Use the pattern index to route directly to one section in this compact collection. Read only that section and any reference it explicitly names.

## d3-shape-tween

### Shape Tween

- **Pattern ID:** `d3-shape-tween`
- **Gallery source ID:** `shape-tween`
- **Family:** Morph
- **Use when:** A polygon morphs between two compatible point sets.
- **Renderer:** `renderShapeTween`

#### Reuse Contract

- Use this file as the pattern source in isolated skill-only workspaces; read the gallery fixture only when maintaining that fixture.
- Keep data deterministic and inline small datasets.
- Preserve the pattern's core geometry and semantic color roles before changing labels or domain data.
- Use SVG-native animation for standalone output; do not leave runtime D3 or CDN dependencies in a self-contained deliverable.
- Include an SVG `<title>`, `<desc>`, stable `viewBox`, and final-state geometry.

#### Source Excerpt

The excerpt below is the compact renderer source for this pattern. If it references helpers such as `prepareSvg`, `fadeIn`, `grow`, `drawPath`, `palette`, `ramps`, `axisBottom`, or `axisLeft`, read `references/shared-renderer-helpers.md` and recreate only the needed helper behavior in the final artifact.

```js
function renderShapeTween() {
    const svg = prepareSvg("shape-tween", "Shape tween", "A polygon morphs between two compatible point sets.");
    const cx = width / 2, cy = height / 2 + 10;
    const start = d3.range(10).map(i => {
      const a = i / 10 * Math.PI * 2 - Math.PI / 2;
      const r = i % 2 ? 66 : 124;
      return [cx + Math.cos(a) * r, cy + Math.sin(a) * r];
    });
    const end = d3.range(10).map(i => {
      const a = i / 10 * Math.PI * 2 - Math.PI / 2;
      const r = 78 + Math.sin(i * 1.7) * 26;
      return [cx + Math.cos(a) * r * 1.35, cy + Math.sin(a) * r * .78];
    });
    const line = d3.line().curve(d3.curveLinearClosed);
    const path = svg.append("path").attr("d", line(end)).attr("fill", palette.blue).attr("fill-opacity", .26).attr("stroke", palette.blue).attr("stroke-width", 3);
    path.append("animate").attr("attributeName", "d").attr("from", line(start)).attr("to", line(end)).attr("dur", "1.35s").attr("begin", ".08s").attr("fill", "freeze");
    const dots = svg.append("g").selectAll("circle").data(end).join("circle").attr("cx", d => d[0]).attr("cy", d => d[1]).attr("fill", palette.red);
    grow(dots, "r", 2, 5.5, .25, .5);
  }
```

## d3-arc-tween

### Arc Tween

- **Pattern ID:** `d3-arc-tween`
- **Gallery source ID:** `arc-tween`
- **Family:** Morph
- **Use when:** Radial segments interpolate from one angle state to another.
- **Renderer:** `renderArcTween`

#### Reuse Contract

- Use this file as the pattern source in isolated skill-only workspaces; read the gallery fixture only when maintaining that fixture.
- Keep data deterministic and inline small datasets.
- Preserve the pattern's core geometry and semantic color roles before changing labels or domain data.
- Use SVG-native animation for standalone output; do not leave runtime D3 or CDN dependencies in a self-contained deliverable.
- Include an SVG `<title>`, `<desc>`, stable `viewBox`, and final-state geometry.

#### Source Excerpt

The excerpt below is the compact renderer source for this pattern. If it references helpers such as `prepareSvg`, `fadeIn`, `grow`, `drawPath`, `palette`, `ramps`, `axisBottom`, or `axisLeft`, read `references/shared-renderer-helpers.md` and recreate only the needed helper behavior in the final artifact.

```js
function renderArcTween() {
    const svg = prepareSvg("arc-tween", "Arc tween", "Radial segments interpolate from one angle state to another.");
    const cx = width / 2, cy = height / 2 + 8;
    const data = [
      { label: "Now", a0: .18, a1: .74, c: palette.red },
      { label: "Plan", a0: .1, a1: .52, c: palette.blue },
      { label: "Risk", a0: .06, a1: .34, c: palette.orange },
      { label: "Reach", a0: .24, a1: .88, c: palette.green }
    ];
    const arc = d3.arc().startAngle(-Math.PI * .75).cornerRadius(9);
    const group = svg.append("g").attr("transform", `translate(${cx},${cy})`);
    data.forEach((d, i) => {
      const outer = 156 - i * 30, inner = outer - 18;
      group.append("path").attr("d", arc({ innerRadius: inner, outerRadius: outer, endAngle: Math.PI * .75 })).attr("fill", "#e7e7e7");
      const mark = group.append("path")
        .attr("d", arc({ innerRadius: inner, outerRadius: outer, endAngle: -Math.PI * .75 + Math.PI * 1.5 * d.a1 }))
        .attr("fill", d.c);
      mark.append("animate").attr("attributeName", "d")
        .attr("from", arc({ innerRadius: inner, outerRadius: outer, endAngle: -Math.PI * .75 + Math.PI * 1.5 * d.a0 }))
        .attr("to", arc({ innerRadius: inner, outerRadius: outer, endAngle: -Math.PI * .75 + Math.PI * 1.5 * d.a1 }))
        .attr("dur", ".95s").attr("begin", `${.08 + i * .08}s`).attr("fill", "freeze");
      group.append("text").attr("class", "mark-label").attr("x", 0).attr("y", -outer + 13).attr("text-anchor", "middle").text(d.label);
    });
  }
```

## d3-path-tween

### Path Tween

- **Pattern ID:** `d3-path-tween`
- **Gallery source ID:** `path-tween`
- **Family:** Morph
- **Use when:** A path interpolates between two line geometries.
- **Renderer:** `renderPathTween`

#### Reuse Contract

- Use this file as the pattern source in isolated skill-only workspaces; read the gallery fixture only when maintaining that fixture.
- Keep data deterministic and inline small datasets.
- Preserve the pattern's core geometry and semantic color roles before changing labels or domain data.
- Use SVG-native animation for standalone output; do not leave runtime D3 or CDN dependencies in a self-contained deliverable.
- Include an SVG `<title>`, `<desc>`, stable `viewBox`, and final-state geometry.

#### Source Excerpt

The excerpt below is the compact renderer source for this pattern. If it references helpers such as `prepareSvg`, `fadeIn`, `grow`, `drawPath`, `palette`, `ramps`, `axisBottom`, or `axisLeft`, read `references/shared-renderer-helpers.md` and recreate only the needed helper behavior in the final artifact.

```js
function renderPathTween() {
    const svg = prepareSvg("path-tween", "Path tween", "A path interpolates between two line geometries.");
    const x = d3.scaleLinear().domain([0, 11]).range([60, width - 56]);
    const y = d3.scaleLinear().domain([10, 90]).range([330, 58]);
    const a = d3.range(12).map(i => [x(i), y(36 + Math.sin(i / 1.4) * 18 + i * 1.6)]);
    const b = d3.range(12).map(i => [x(i), y(72 - Math.cos(i / 1.7) * 16 - i * 1.2)]);
    const line = d3.line().curve(d3.curveCatmullRom);
    axisBottom(svg, x, 340, 6);
    const before = svg.append("path").attr("d", line(a)).attr("fill", "none").attr("stroke", palette.line).attr("stroke-width", 2).attr("stroke-dasharray", "5 5");
    fadeIn(before, .05, .4);
    const path = svg.append("path").attr("d", line(b)).attr("fill", "none").attr("stroke", palette.purple).attr("stroke-width", 4).attr("stroke-linecap", "round");
    path.append("animate").attr("attributeName", "d").attr("from", line(a)).attr("to", line(b)).attr("dur", "1.25s").attr("begin", ".1s").attr("fill", "freeze");
    drawPath(path, .1, 1.25);
  }
```

## d3-text-tween

### Text Tween

- **Pattern ID:** `d3-text-tween`
- **Gallery source ID:** `text-tween`
- **Family:** Motion
- **Use when:** Counters and labels animate value changes directly.
- **Renderer:** `renderTextTween`

#### Reuse Contract

- Use this file as the pattern source in isolated skill-only workspaces; read the gallery fixture only when maintaining that fixture.
- Keep data deterministic and inline small datasets.
- Preserve the pattern's core geometry and semantic color roles before changing labels or domain data.
- Use SVG-native animation for standalone output; do not leave runtime D3 or CDN dependencies in a self-contained deliverable.
- Include an SVG `<title>`, `<desc>`, stable `viewBox`, and final-state geometry.

#### Source Excerpt

The excerpt below is the compact renderer source for this pattern. If it references helpers such as `prepareSvg`, `fadeIn`, `grow`, `drawPath`, `palette`, `ramps`, `axisBottom`, or `axisLeft`, read `references/shared-renderer-helpers.md` and recreate only the needed helper behavior in the final artifact.

```js
function renderTextTween() {
    const svg = prepareSvg("text-tween", "Text tween", "Counters and labels animate value changes directly.");
    const metrics = [
      { label: "Reach", from: 42, to: 86, c: palette.blue, fill: palette.blueHighlight },
      { label: "Quality", from: 38, to: 74, c: palette.green, fill: palette.greenHighlight },
      { label: "Risk", from: 61, to: 29, c: palette.red, fill: palette.redHighlight }
    ];
    const group = svg.append("g").selectAll("g").data(metrics).join("g").attr("transform", (d, i) => `translate(${122 + i * 158},${height / 2})`);
    group.append("circle").attr("r", 56).attr("fill", d => d.fill).attr("fill-opacity", .78).attr("stroke", d => d.c).attr("stroke-width", 2.8);
    const text = group.append("text").attr("text-anchor", "middle").attr("dy", ".18em").attr("font-size", 32).attr("font-weight", 800).attr("fill", palette.ink).text(d => d.to);
    text.each(function (d, i) {
      const node = d3.select(this);
      node.append("animate").attr("attributeName", "opacity").attr("from", 0).attr("to", 1).attr("dur", ".25s").attr("begin", `${.08 + i * .08}s`).attr("fill", "freeze");
      node.append("animate").attr("attributeName", "data-value").attr("from", d.from).attr("to", d.to).attr("dur", ".9s").attr("begin", `${.08 + i * .08}s`).attr("fill", "freeze");
    });
    group.append("text").attr("class", "mark-label").attr("fill", d => d.c).attr("text-anchor", "middle").attr("dy", 82).text(d => d.label);
    group.append("text").attr("class", "mark-label").attr("text-anchor", "middle").attr("dy", 101).text(d => `${d.from} -> ${d.to}`);
  }
```

## d3-brush-handles

### Brush Handles

- **Pattern ID:** `d3-brush-handles`
- **Gallery source ID:** `brush-handles`
- **Family:** Interaction
- **Use when:** Custom brush handles make a selected interval legible.
- **Renderer:** `renderBrushHandles`

#### Reuse Contract

- Use this file as the pattern source in isolated skill-only workspaces; read the gallery fixture only when maintaining that fixture.
- Keep data deterministic and inline small datasets.
- Preserve the pattern's core geometry and semantic color roles before changing labels or domain data.
- Use SVG-native animation for standalone output; do not leave runtime D3 or CDN dependencies in a self-contained deliverable.
- Include an SVG `<title>`, `<desc>`, stable `viewBox`, and final-state geometry.

#### Source Excerpt

The excerpt below is the compact renderer source for this pattern. If it references helpers such as `prepareSvg`, `fadeIn`, `grow`, `drawPath`, `palette`, `ramps`, `axisBottom`, or `axisLeft`, read `references/shared-renderer-helpers.md` and recreate only the needed helper behavior in the final artifact.

```js
function renderBrushHandles() {
    const svg = prepareSvg("brush-handles", "Brush handles", "Custom brush handles make a selected interval legible.");
    const x = d3.scaleLinear().domain([0, 100]).range([62, width - 56]);
    const y = d3.scaleLinear().domain([0, 80]).range([296, 76]);
    const data = d3.range(32).map(i => ({ x: i * 3.1, y: 28 + Math.sin(i / 3) * 18 + (i % 7) * 2 }));
    const line = d3.line().x(d => x(d.x)).y(d => y(d.y)).curve(d3.curveMonotoneX);
    drawPath(svg.append("path").datum(data).attr("d", line).attr("fill", "none").attr("stroke", palette.gray700).attr("stroke-width", 2.6), .08, .8);
    axisBottom(svg, x, 316, 6);
    const brush = { x0: x(24), x1: x(64), y0: 82, y1: 296 };
    const rect = svg.append("rect").attr("x", brush.x0).attr("y", brush.y0).attr("width", brush.x1 - brush.x0).attr("height", brush.y1 - brush.y0)
      .attr("fill", "#cdf3ff").attr("fill-opacity", .42).attr("stroke", palette.blue).attr("stroke-width", 1.8);
    rect.append("animate").attr("attributeName", "x").attr("from", x(16)).attr("to", brush.x0).attr("dur", ".75s").attr("begin", ".12s").attr("fill", "freeze");
    const handles = svg.append("g").selectAll("rect").data([brush.x0, brush.x1]).join("rect")
      .attr("x", d => d - 5).attr("y", brush.y0 - 6).attr("width", 10).attr("height", brush.y1 - brush.y0 + 12).attr("rx", 5)
      .attr("fill", palette.blue).attr("stroke", "#fff").attr("stroke-width", 1.4);
    fadeIn(handles, .16, .45);
  }
```

## d3-brush-snapping

### Brush Snapping

- **Pattern ID:** `d3-brush-snapping`
- **Gallery source ID:** `brush-snapping`
- **Family:** Interaction
- **Use when:** A loose brush snaps to calendar-like interval boundaries.
- **Renderer:** `renderBrushSnapping`

#### Reuse Contract

- Use this file as the pattern source in isolated skill-only workspaces; read the gallery fixture only when maintaining that fixture.
- Keep data deterministic and inline small datasets.
- Preserve the pattern's core geometry and semantic color roles before changing labels or domain data.
- Use SVG-native animation for standalone output; do not leave runtime D3 or CDN dependencies in a self-contained deliverable.
- Include an SVG `<title>`, `<desc>`, stable `viewBox`, and final-state geometry.

#### Source Excerpt

The excerpt below is the compact renderer source for this pattern. If it references helpers such as `prepareSvg`, `fadeIn`, `grow`, `drawPath`, `palette`, `ramps`, `axisBottom`, or `axisLeft`, read `references/shared-renderer-helpers.md` and recreate only the needed helper behavior in the final artifact.

```js
function renderBrushSnapping() {
    const svg = prepareSvg("brush-snapping", "Brush snapping", "A loose brush snaps to calendar-like interval boundaries.");
    const x = d3.scaleBand().domain(d3.range(12).map(String)).range([62, width - 54]).padding(.16);
    const y = d3.scaleLinear().domain([0, 100]).range([302, 72]);
    const data = d3.range(12).map(i => ({ i, value: 28 + ((i * 19) % 62) }));
    svg.append("g").selectAll("rect.bar").data(data).join("rect")
      .attr("class", "bar").attr("x", d => x(String(d.i))).attr("y", d => y(d.value)).attr("width", x.bandwidth()).attr("height", d => y(0) - y(d.value)).attr("fill", palette.green).attr("fill-opacity", .68);
    axisBottom(svg, d3.scaleLinear().domain([0, 11]).range([62, width - 54]), 322, 6);
    const loose = { x: x("2") - 13, w: x("7") - x("2") + x.bandwidth() + 26 };
    const snapped = { x: x("2"), w: x("7") - x("2") + x.bandwidth() };
    const selection = svg.append("rect").attr("x", snapped.x).attr("y", 62).attr("width", snapped.w).attr("height", 242).attr("fill", palette.yellowHighlight).attr("fill-opacity", .65).attr("stroke", palette.yellowHover).attr("stroke-width", 2);
    selection.append("animate").attr("attributeName", "x").attr("from", loose.x).attr("to", snapped.x).attr("dur", ".8s").attr("begin", ".12s").attr("fill", "freeze");
    selection.append("animate").attr("attributeName", "width").attr("from", loose.w).attr("to", snapped.w).attr("dur", ".8s").attr("begin", ".12s").attr("fill", "freeze");
    svg.append("text").attr("class", "mark-label").attr("x", snapped.x + snapped.w / 2).attr("y", 52).attr("text-anchor", "middle").text("snaps to bins 2-7");
  }
```

## d3-ordinal-brushing

### Ordinal Brushing

- **Pattern ID:** `d3-ordinal-brushing`
- **Gallery source ID:** `ordinal-brushing`
- **Family:** Interaction
- **Use when:** Categorical bins are selected with an ordinal brush range.
- **Renderer:** `renderOrdinalBrushing`

#### Reuse Contract

- Use this file as the pattern source in isolated skill-only workspaces; read the gallery fixture only when maintaining that fixture.
- Keep data deterministic and inline small datasets.
- Preserve the pattern's core geometry and semantic color roles before changing labels or domain data.
- Use SVG-native animation for standalone output; do not leave runtime D3 or CDN dependencies in a self-contained deliverable.
- Include an SVG `<title>`, `<desc>`, stable `viewBox`, and final-state geometry.

#### Source Excerpt

The excerpt below is the compact renderer source for this pattern. If it references helpers such as `prepareSvg`, `fadeIn`, `grow`, `drawPath`, `palette`, `ramps`, `axisBottom`, or `axisLeft`, read `references/shared-renderer-helpers.md` and recreate only the needed helper behavior in the final artifact.

```js
function renderOrdinalBrushing() {
    const svg = prepareSvg("ordinal-brushing", "Ordinal brushing", "Categorical bins are selected with an ordinal brush range.");
    const groups = ["A", "B", "C", "D", "E", "F", "G"];
    const x = d3.scalePoint().domain(groups).range([74, width - 74]);
    const y = d3.scaleLinear().domain([0, 100]).range([304, 72]);
    const data = groups.flatMap((g, gi) => d3.range(8).map(i => ({ group: g, value: 18 + ((gi * 23 + i * 11) % 72), selected: gi >= 2 && gi <= 4 })));
    svg.append("g").selectAll("line").data(groups).join("line").attr("x1", d => x(d)).attr("x2", d => x(d)).attr("y1", 72).attr("y2", 304).attr("stroke", "#e7e7e7");
    const dots = svg.append("g").selectAll("circle").data(data).join("circle")
      .attr("cx", d => x(d.group) + (((d.value * 7) % 17) - 8)).attr("cy", d => y(d.value))
      .attr("fill", d => d.selected ? palette.red : palette.blue).attr("fill-opacity", d => d.selected ? .9 : .42);
    grow(dots, "r", 2, 4.6, .05, .45);
    const x0 = x("C") - 32, x1 = x("E") + 32;
    const brush = svg.append("rect").attr("x", x0).attr("y", 62).attr("width", x1 - x0).attr("height", 254).attr("fill", "#ffccd5").attr("fill-opacity", .28).attr("stroke", palette.red).attr("stroke-width", 2);
    fadeIn(brush, .14, .45);
    svg.selectAll(".ordinal-label").data(groups).join("text").attr("class", "mark-label").attr("x", d => x(d)).attr("y", 336).attr("text-anchor", "middle").text(d => d);
  }
```

## d3-zoomable-bar

### Zoomable Bar

- **Pattern ID:** `d3-zoomable-bar`
- **Gallery source ID:** `zoomable-bar`
- **Family:** Focus
- **Use when:** A local categorical range expands while context remains visible.
- **Renderer:** `renderZoomableBar`

#### Reuse Contract

- Use this file as the pattern source in isolated skill-only workspaces; read the gallery fixture only when maintaining that fixture.
- Keep data deterministic and inline small datasets.
- Preserve the pattern's core geometry and semantic color roles before changing labels or domain data.
- Use SVG-native animation for standalone output; do not leave runtime D3 or CDN dependencies in a self-contained deliverable.
- Include an SVG `<title>`, `<desc>`, stable `viewBox`, and final-state geometry.

#### Source Excerpt

The excerpt below is the compact renderer source for this pattern. If it references helpers such as `prepareSvg`, `fadeIn`, `grow`, `drawPath`, `palette`, `ramps`, `axisBottom`, or `axisLeft`, read `references/shared-renderer-helpers.md` and recreate only the needed helper behavior in the final artifact.

```js
function renderZoomableBar() {
    const svg = prepareSvg("zoomable-bar", "Zoomable bar", "A local categorical range expands while context remains visible.");
    const data = d3.range(18).map(i => ({ name: `C${i + 1}`, value: 18 + ((i * 29) % 76), focus: i >= 6 && i <= 11 }));
    const overview = { x: 54, y: 292, w: 452, h: 42 };
    const detail = { x: 74, y: 64, w: 412, h: 182 };
    const xO = d3.scaleBand().domain(data.map(d => d.name)).range([overview.x, overview.x + overview.w]).padding(.18);
    const yO = d3.scaleLinear().domain([0, 100]).range([overview.y + overview.h, overview.y]);
    svg.append("g").selectAll("rect.overview").data(data).join("rect")
      .attr("class", "overview").attr("x", d => xO(d.name)).attr("y", d => yO(d.value)).attr("width", xO.bandwidth()).attr("height", d => yO(0) - yO(d.value))
      .attr("fill", d => d.focus ? palette.red : palette.gray300);
    const selected = data.filter(d => d.focus);
    const x = d3.scaleBand().domain(selected.map(d => d.name)).range([detail.x, detail.x + detail.w]).padding(.22);
    const y = d3.scaleLinear().domain([0, 100]).range([detail.y + detail.h, detail.y]);
    const bars = svg.append("g").selectAll("rect.detail").data(selected).join("rect")
      .attr("class", "detail").attr("x", d => x(d.name)).attr("width", x.bandwidth()).attr("y", d => y(d.value)).attr("height", d => y(0) - y(d.value)).attr("fill", palette.red);
    grow(bars, "height", 1, d => y(0) - y(d.value), .08, .65);
    bars.attr("y", d => y(d.value));
    svg.append("rect").attr("x", xO("C7") - 4).attr("y", overview.y - 7).attr("width", xO("C12") - xO("C7") + xO.bandwidth() + 8).attr("height", overview.h + 14).attr("fill", "none").attr("stroke", palette.redHover).attr("stroke-width", 2);
  }
```

## d3-xy-zoom

### X/Y Zoom

- **Pattern ID:** `d3-xy-zoom`
- **Gallery source ID:** `xy-zoom`
- **Family:** Focus
- **Use when:** Independent axis windows crop a two-dimensional scatter field.
- **Renderer:** `renderXyZoom`

#### Reuse Contract

- Use this file as the pattern source in isolated skill-only workspaces; read the gallery fixture only when maintaining that fixture.
- Keep data deterministic and inline small datasets.
- Preserve the pattern's core geometry and semantic color roles before changing labels or domain data.
- Use SVG-native animation for standalone output; do not leave runtime D3 or CDN dependencies in a self-contained deliverable.
- Include an SVG `<title>`, `<desc>`, stable `viewBox`, and final-state geometry.

#### Source Excerpt

The excerpt below is the compact renderer source for this pattern. If it references helpers such as `prepareSvg`, `fadeIn`, `grow`, `drawPath`, `palette`, `ramps`, `axisBottom`, or `axisLeft`, read `references/shared-renderer-helpers.md` and recreate only the needed helper behavior in the final artifact.

```js
function renderXyZoom() {
    const svg = prepareSvg("xy-zoom", "X/Y zoom", "Independent axis windows crop a two-dimensional scatter field.");
    const data = d3.range(90).map(i => ({ x: ((i * 37) % 100), y: ((i * 61 + i * 3) % 100) }));
    const left = { x: 46, y: 68, w: 214, h: 238 };
    const right = { x: 314, y: 68, w: 200, h: 238 };
    const x0 = d3.scaleLinear().domain([0, 100]).range([left.x, left.x + left.w]);
    const y0 = d3.scaleLinear().domain([0, 100]).range([left.y + left.h, left.y]);
    const focus = { x0: 32, x1: 68, y0: 38, y1: 76 };
    const x1 = d3.scaleLinear().domain([focus.x0, focus.x1]).range([right.x, right.x + right.w]);
    const y1 = d3.scaleLinear().domain([focus.y0, focus.y1]).range([right.y + right.h, right.y]);
    svg.append("rect").attr("x", left.x).attr("y", left.y).attr("width", left.w).attr("height", left.h).attr("fill", "#ffffff").attr("stroke", palette.line);
    svg.append("rect").attr("x", right.x).attr("y", right.y).attr("width", right.w).attr("height", right.h).attr("fill", "#ffffff").attr("stroke", palette.line);
    svg.append("g").selectAll("circle.context").data(data).join("circle").attr("class", "context").attr("cx", d => x0(d.x)).attr("cy", d => y0(d.y)).attr("r", 3).attr("fill", palette.blue).attr("fill-opacity", .42);
    svg.append("rect").attr("x", x0(focus.x0)).attr("y", y0(focus.y1)).attr("width", x0(focus.x1) - x0(focus.x0)).attr("height", y0(focus.y0) - y0(focus.y1)).attr("fill", "#cdf3ff").attr("fill-opacity", .28).attr("stroke", palette.blue).attr("stroke-width", 2);
    const detail = data.filter(d => d.x >= focus.x0 && d.x <= focus.x1 && d.y >= focus.y0 && d.y <= focus.y1);
    const dots = svg.append("g").selectAll("circle.detail").data(detail).join("circle").attr("class", "detail").attr("cx", d => x1(d.x)).attr("cy", d => y1(d.y)).attr("fill", palette.red).attr("fill-opacity", .82);
    grow(dots, "r", 2, 5, .12, .45);
    svg.append("text").attr("class", "mark-label").attr("x", left.x).attr("y", 48).text("context");
  }
```

## d3-versor-dragging

### Versor Dragging

- **Pattern ID:** `d3-versor-dragging`
- **Gallery source ID:** `versor-dragging`
- **Family:** Projection
- **Use when:** A globe rotates along a drag arc using spherical interpolation.
- **Renderer:** `renderVersorDragging`

#### Reuse Contract

- Use this file as the pattern source in isolated skill-only workspaces; read the gallery fixture only when maintaining that fixture.
- Keep data deterministic and inline small datasets.
- Preserve the pattern's core geometry and semantic color roles before changing labels or domain data.
- Use SVG-native animation for standalone output; do not leave runtime D3 or CDN dependencies in a self-contained deliverable.
- Include an SVG `<title>`, `<desc>`, stable `viewBox`, and final-state geometry.

#### Source Excerpt

The excerpt below is the compact renderer source for this pattern. If it references helpers such as `prepareSvg`, `fadeIn`, `grow`, `drawPath`, `palette`, `ramps`, `axisBottom`, or `axisLeft`, read `references/shared-renderer-helpers.md` and recreate only the needed helper behavior in the final artifact.

```js
function renderVersorDragging() {
    const svg = prepareSvg("versor-dragging", "Versor dragging", "A globe rotates along a drag arc using spherical interpolation.");
    const projection = d3.geoOrthographic().rotate([-22, -16]).fitExtent([[94, 48], [466, 356]], { type: "Sphere" });
    const path = d3.geoPath(projection);
    const globe = svg.append("g");
    globe.append("path").datum({ type: "Sphere" }).attr("d", path).attr("fill", "#cdf3ff").attr("stroke", palette.ink).attr("stroke-width", 2);
    globe.append("g").selectAll("path").data(d3.geoGraticule().step([20, 20]).lines()).join("path")
      .attr("d", path).attr("fill", "none").attr("stroke", palette.blue).attr("stroke-opacity", .18).attr("stroke-width", .8);
    globe.append("animateTransform").attr("attributeName", "transform").attr("type", "rotate").attr("from", `0 ${width / 2} ${height / 2}`).attr("to", `18 ${width / 2} ${height / 2}`).attr("dur", "1.3s").attr("begin", ".08s").attr("fill", "freeze");
    const dragArc = [[154, 300], [224, 182], [338, 112], [420, 144]];
    const line = svg.append("path").datum(dragArc).attr("d", d3.line().curve(d3.curveBasis)).attr("fill", "none").attr("stroke", palette.red).attr("stroke-width", 3).attr("stroke-linecap", "round");
    drawPath(line, .12, .95);
    svg.append("circle").attr("cx", 420).attr("cy", 144).attr("r", 8).attr("fill", palette.red).attr("stroke", palette.redHighlight).attr("stroke-width", 4);
  }
```

## d3-you-draw-it

### You Draw It

- **Pattern ID:** `d3-you-draw-it`
- **Gallery source ID:** `you-draw-it`
- **Family:** Prediction
- **Use when:** A guessed trajectory reveals against the observed series.
- **Renderer:** `renderYouDrawIt`

#### Reuse Contract

- Use this file as the pattern source in isolated skill-only workspaces; read the gallery fixture only when maintaining that fixture.
- Keep data deterministic and inline small datasets.
- Preserve the pattern's core geometry and semantic color roles before changing labels or domain data.
- Use SVG-native animation for standalone output; do not leave runtime D3 or CDN dependencies in a self-contained deliverable.
- Include an SVG `<title>`, `<desc>`, stable `viewBox`, and final-state geometry.

#### Source Excerpt

The excerpt below is the compact renderer source for this pattern. If it references helpers such as `prepareSvg`, `fadeIn`, `grow`, `drawPath`, `palette`, `ramps`, `axisBottom`, or `axisLeft`, read `references/shared-renderer-helpers.md` and recreate only the needed helper behavior in the final artifact.

```js
function renderYouDrawIt() {
    const svg = prepareSvg("you-draw-it", "You draw it", "A guessed trajectory reveals against the observed series.");
    const margin = { top: 46, right: 42, bottom: 52, left: 58 };
    const x = d3.scaleLinear().domain([0, 10]).range([margin.left, width - margin.right]);
    const y = d3.scaleLinear().domain([0, 100]).range([height - margin.bottom, margin.top]);
    const observed = d3.range(11).map(i => ({ t: i, v: 26 + i * 5.8 + Math.sin(i / 1.2) * 11 }));
    const guess = d3.range(11).map(i => ({ t: i, v: 30 + i * 3.4 + Math.cos(i / 1.9) * 8 }));
    axisBottom(svg, x, height - margin.bottom, 5);
    axisLeft(svg, y, margin.left, 5);
    const line = d3.line().x(d => x(d.t)).y(d => y(d.v)).curve(d3.curveMonotoneX);
    const guessPath = svg.append("path").datum(guess).attr("d", line).attr("fill", "none").attr("stroke", palette.gray700).attr("stroke-width", 3).attr("stroke-dasharray", "7 5");
    drawPath(guessPath, .05, .85);
    const obsPath = svg.append("path").datum(observed).attr("d", line).attr("fill", "none").attr("stroke", palette.red).attr("stroke-width", 3.4);
    drawPath(obsPath, .55, .95);
    svg.append("text").attr("class", "mark-label").attr("x", x(2)).attr("y", y(42)).text("drawn guess");
    svg.append("text").attr("class", "mark-label").attr("x", x(7.8)).attr("y", y(76)).text("revealed actual");
  }
```
