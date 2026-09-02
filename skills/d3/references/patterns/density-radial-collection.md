# Density and Radial Pattern Collection

Use the pattern index to route directly to one section in this compact collection. Read only that section and any reference it explicitly names.

## d3-calendar

### Calendar Heatmap

- **Pattern ID:** `d3-calendar`
- **Gallery source ID:** `calendar`
- **Family:** Heatmap
- **Use when:** Repeated temporal cells with intensity.
- **Renderer:** `renderCalendar`

#### Reuse Contract

- Use this file as the pattern source in isolated skill-only workspaces; read the gallery fixture only when maintaining that fixture.
- Keep data deterministic and inline small datasets.
- Preserve the pattern's core geometry and semantic color roles before changing labels or domain data.
- Use SVG-native animation for standalone output; do not leave runtime D3 or CDN dependencies in a self-contained deliverable.
- Include an SVG `<title>`, `<desc>`, stable `viewBox`, and final-state geometry.

#### Source Excerpt

The excerpt below is the compact renderer source for this pattern. If it references helpers such as `prepareSvg`, `fadeIn`, `grow`, `drawPath`, `palette`, `ramps`, `axisBottom`, or `axisLeft`, read `references/shared-renderer-helpers.md` and recreate only the needed helper behavior in the final artifact.

```js
function renderCalendar() {
    const svg = prepareSvg("calendar", "Calendar heatmap", "Repeated temporal cells showing intensity by day.");
    const days = d3.range(35).map(i => ({ i, value: 1 + (i * 7) % 13 }));
    const cell = 34;
    const color = quantizedRamp([1, 13], ramps.blue);
    const g = svg.append("g").attr("transform", "translate(80,58)");
    const cells = g.selectAll("rect").data(days).join("rect")
      .attr("x", d => (d.i % 7) * cell).attr("y", d => Math.floor(d.i / 7) * cell)
      .attr("width", cell - 3).attr("height", cell - 3).attr("rx", 4)
      .attr("fill", d => color(d.value));
    fadeIn(cells, .05, .6);
    ["Mon", "Tue", "Wed", "Thu", "Fri"].forEach((d, i) => g.append("text").attr("class", "label").attr("x", -12).attr("y", i * cell + 20).attr("text-anchor", "end").text(d));
    d3.range(7).forEach(i => g.append("text").attr("class", "label").attr("x", i * cell + 15).attr("y", -12).attr("text-anchor", "middle").text(`D${i + 1}`));
  }
```

## d3-contours

### Density Contours

- **Pattern ID:** `d3-contours`
- **Gallery source ID:** `contours`
- **Family:** Density
- **Use when:** Two-dimensional concentration fields.
- **Renderer:** `renderContours`

#### Reuse Contract

- Use this file as the pattern source in isolated skill-only workspaces; read the gallery fixture only when maintaining that fixture.
- Keep data deterministic and inline small datasets.
- Preserve the pattern's core geometry and semantic color roles before changing labels or domain data.
- Use SVG-native animation for standalone output; do not leave runtime D3 or CDN dependencies in a self-contained deliverable.
- Include an SVG `<title>`, `<desc>`, stable `viewBox`, and final-state geometry.

#### Source Excerpt

The excerpt below is the compact renderer source for this pattern. If it references helpers such as `prepareSvg`, `fadeIn`, `grow`, `drawPath`, `palette`, `ramps`, `axisBottom`, or `axisLeft`, read `references/shared-renderer-helpers.md` and recreate only the needed helper behavior in the final artifact.

```js
function renderContours() {
    const svg = prepareSvg("contours", "Density contours", "D3 contourDensity estimates two-dimensional concentration.");
    const pts = d3.range(160).map(i => {
      const cluster = i % 3;
      const cx = [180, 300, 390][cluster], cy = [150, 240, 140][cluster];
      return [cx + Math.sin(i * 1.7) * (34 + cluster * 6), cy + Math.cos(i * 1.3) * (28 + cluster * 8)];
    });
    const contours = d3.contourDensity().x(d => d[0]).y(d => d[1]).size([width, height]).bandwidth(24).thresholds(8)(pts);
    const color = quantizedRamp([0, d3.max(contours, d => d.value)], [palette.purpleHighlight, palette.blueHighlight, palette.cyan, palette.blue, palette.blueHover]);
    const path = d3.geoPath();
    const shapes = svg.append("g").selectAll("path").data(contours).join("path")
      .attr("d", path).attr("fill", d => color(d.value)).attr("stroke", "#fff").attr("stroke-width", .8);
    fadeIn(shapes, .06, .8);
    svg.append("g").selectAll("circle").data(pts.filter((d, i) => i % 5 === 0)).join("circle").attr("cx", d => d[0]).attr("cy", d => d[1]).attr("r", 2).attr("fill", palette.ink).attr("opacity", .35);
  }
```

## d3-volcano-contours

### Volcano Contours

- **Pattern ID:** `d3-volcano-contours`
- **Gallery source ID:** `volcano-contours`
- **Family:** Surface
- **Use when:** A synthetic height field becomes nested contour bands.
- **Renderer:** `renderVolcanoContours`

#### Reuse Contract

- Use this file as the pattern source in isolated skill-only workspaces; read the gallery fixture only when maintaining that fixture.
- Keep data deterministic and inline small datasets.
- Preserve the pattern's core geometry and semantic color roles before changing labels or domain data.
- Use SVG-native animation for standalone output; do not leave runtime D3 or CDN dependencies in a self-contained deliverable.
- Include an SVG `<title>`, `<desc>`, stable `viewBox`, and final-state geometry.

#### Source Excerpt

The excerpt below is the compact renderer source for this pattern. If it references helpers such as `prepareSvg`, `fadeIn`, `grow`, `drawPath`, `palette`, `ramps`, `axisBottom`, or `axisLeft`, read `references/shared-renderer-helpers.md` and recreate only the needed helper behavior in the final artifact.

```js
function renderVolcanoContours() {
    const svg = prepareSvg("volcano-contours", "Volcano contours", "A synthetic height field becomes nested contour bands.");
    const nx = 46, ny = 32;
    const values = [];
    for (let y = 0; y < ny; y += 1) {
      for (let x = 0; x < nx; x += 1) {
        const dx = (x - 21) / 11, dy = (y - 15) / 8;
        const peak = Math.exp(-(dx * dx + dy * dy)) * 98;
        const ridge = Math.exp(-(((x - 31) / 8) ** 2 + ((y - 9) / 5) ** 2)) * 48;
        values.push(18 + peak + ridge + Math.sin(x / 3) * 4);
      }
    }
    const contours = d3.contours().size([nx, ny]).thresholds(d3.range(25, 126, 14))(values);
    const projection = d3.geoIdentity().scale(10.2).translate([46, 50]);
    const path = d3.geoPath(projection);
    const fill = d3.scaleQuantize().domain([25, 125]).range(["#cdf3ff", "#dbffcc", "#fff4cc", "#ffe5cc", "#ffccd5", "#f9ccff"]);
    const bands = svg.append("g").selectAll("path").data(contours).join("path")
      .attr("d", path).attr("fill", d => fill(d.value)).attr("stroke", "#fff").attr("stroke-width", 1.1);
    fadeIn(bands, .08, .65);
  }
```

## d3-polar-clock

### Polar Clock

- **Pattern ID:** `d3-polar-clock`
- **Gallery source ID:** `polar-clock`
- **Family:** Radial
- **Use when:** Nested arcs encode cyclic units of time.
- **Renderer:** `renderPolarClock`

#### Reuse Contract

- Use this file as the pattern source in isolated skill-only workspaces; read the gallery fixture only when maintaining that fixture.
- Keep data deterministic and inline small datasets.
- Preserve the pattern's core geometry and semantic color roles before changing labels or domain data.
- Use SVG-native animation for standalone output; do not leave runtime D3 or CDN dependencies in a self-contained deliverable.
- Include an SVG `<title>`, `<desc>`, stable `viewBox`, and final-state geometry.

#### Source Excerpt

The excerpt below is the compact renderer source for this pattern. If it references helpers such as `prepareSvg`, `fadeIn`, `grow`, `drawPath`, `palette`, `ramps`, `axisBottom`, or `axisLeft`, read `references/shared-renderer-helpers.md` and recreate only the needed helper behavior in the final artifact.

```js
function renderPolarClock() {
    const svg = prepareSvg("polar-clock", "Polar clock", "Nested arcs encode cyclic units as radial progress.");
    const center = svg.append("g").attr("transform", `translate(${width / 2},${height / 2 + 8})`);
    const units = [
      { label: "month", value: .83, color: palette.blue },
      { label: "week", value: .64, color: palette.green },
      { label: "day", value: .42, color: palette.orange },
      { label: "hour", value: .76, color: palette.purple }
    ];
    const arc = d3.arc().startAngle(0).cornerRadius(8);
    units.forEach((unit, i) => {
      const outer = 160 - i * 30;
      const inner = outer - 18;
      center.append("path").attr("d", arc({ innerRadius: inner, outerRadius: outer, endAngle: Math.PI * 2 })).attr("fill", palette.gray100);
      const mark = center.append("path").attr("d", arc({ innerRadius: inner, outerRadius: outer, endAngle: Math.PI * 2 * unit.value })).attr("fill", unit.color);
      fadeIn(mark, .12 + i * .08, .55);
      center.append("text").attr("class", "mark-label").attr("x", 0).attr("y", -outer + 13).attr("text-anchor", "middle").text(unit.label);
    });
  }
```

## d3-radial-area

### Radial Area

- **Pattern ID:** `d3-radial-area`
- **Gallery source ID:** `radial-area`
- **Family:** Radial
- **Use when:** A cyclic time series wraps into a filled polar profile.
- **Renderer:** `renderRadialArea`

#### Reuse Contract

- Use this file as the pattern source in isolated skill-only workspaces; read the gallery fixture only when maintaining that fixture.
- Keep data deterministic and inline small datasets.
- Preserve the pattern's core geometry and semantic color roles before changing labels or domain data.
- Use SVG-native animation for standalone output; do not leave runtime D3 or CDN dependencies in a self-contained deliverable.
- Include an SVG `<title>`, `<desc>`, stable `viewBox`, and final-state geometry.

#### Source Excerpt

The excerpt below is the compact renderer source for this pattern. If it references helpers such as `prepareSvg`, `fadeIn`, `grow`, `drawPath`, `palette`, `ramps`, `axisBottom`, or `axisLeft`, read `references/shared-renderer-helpers.md` and recreate only the needed helper behavior in the final artifact.

```js
function renderRadialArea() {
    const svg = prepareSvg("radial-area", "Radial area", "A cyclic time series wraps into a filled polar profile.");
    const data = d3.range(36).map(i => ({ angle: i / 36 * Math.PI * 2, value: 58 + Math.sin(i / 3) * 20 + Math.cos(i / 5) * 12 }));
    const r = d3.scaleLinear().domain([20, 92]).range([48, 158]);
    const area = d3.radialArea().angle(d => d.angle).innerRadius(42).outerRadius(d => r(d.value)).curve(d3.curveCatmullRomClosed);
    const center = svg.append("g").attr("transform", `translate(${width / 2},${height / 2 + 10})`);
    d3.range(1, 4).forEach(i => center.append("circle").attr("r", 42 + i * 36).attr("fill", "none").attr("stroke", "#e7e7e7"));
    const mark = center.append("path").datum(data).attr("d", area).attr("fill", palette.blueHighlight).attr("fill-opacity", .58).attr("stroke", palette.blue).attr("stroke-width", 2.8);
    fadeIn(mark, .08, .7);
    drawPath(center.append("path").datum(data).attr("d", d3.lineRadial().angle(d => d.angle).radius(d => r(d.value)).curve(d3.curveCatmullRomClosed)).attr("fill", "none").attr("stroke", palette.blue).attr("stroke-width", 2.1), .1, 1);
  }
```

## d3-waffle

### Waffle Matrix

- **Pattern ID:** `d3-waffle`
- **Gallery source ID:** `waffle`
- **Family:** Part-to-whole
- **Use when:** Individual units grouped into exact shares.
- **Renderer:** `renderWaffle`

#### Reuse Contract

- Use this file as the pattern source in isolated skill-only workspaces; read the gallery fixture only when maintaining that fixture.
- Keep data deterministic and inline small datasets.
- Preserve the pattern's core geometry and semantic color roles before changing labels or domain data.
- Use SVG-native animation for standalone output; do not leave runtime D3 or CDN dependencies in a self-contained deliverable.
- Include an SVG `<title>`, `<desc>`, stable `viewBox`, and final-state geometry.

#### Source Excerpt

The excerpt below is the compact renderer source for this pattern. If it references helpers such as `prepareSvg`, `fadeIn`, `grow`, `drawPath`, `palette`, `ramps`, `axisBottom`, or `axisLeft`, read `references/shared-renderer-helpers.md` and recreate only the needed helper behavior in the final artifact.

```js
function renderWaffle() {
    const svg = prepareSvg("waffle", "Waffle matrix", "D3 unit grid shows exact part-to-whole composition.");
    const shares = [
      { name: "Build", count: 36, color: palette.blue },
      { name: "Review", count: 24, color: palette.orange },
      { name: "Ship", count: 22, color: palette.green },
      { name: "Learn", count: 18, color: palette.purple }
    ];
    const units = shares.flatMap(group => d3.range(group.count).map(() => group));
    const cell = 25;
    const origin = [118, 70];
    const marks = svg.append("g").selectAll("rect").data(units).join("rect")
      .attr("x", (d, i) => origin[0] + (i % 10) * cell)
      .attr("y", (d, i) => origin[1] + Math.floor(i / 10) * cell)
      .attr("width", cell - 4)
      .attr("height", cell - 4)
      .attr("rx", 5)
      .attr("fill", d => d.color)
      .attr("stroke", "#fff");
    fadeIn(marks, .04, .55);
    let y = 92;
    shares.forEach(group => {
      svg.append("rect").attr("x", 392).attr("y", y - 12).attr("width", 14).attr("height", 14).attr("fill", group.color).attr("rx", 3);
      svg.append("text").attr("class", "mark-label").attr("x", 414).attr("y", y).text(`${group.name} ${group.count}%`);
      y += 30;
    });
  }
```

## d3-parallel-coordinates

### Parallel Coordinates

- **Pattern ID:** `d3-parallel-coordinates`
- **Gallery source ID:** `parallel-coordinates`
- **Family:** Multivariate
- **Use when:** Many-dimensional profiles as polylines.
- **Renderer:** `renderParallelCoordinates`

#### Reuse Contract

- Use this file as the pattern source in isolated skill-only workspaces; read the gallery fixture only when maintaining that fixture.
- Keep data deterministic and inline small datasets.
- Preserve the pattern's core geometry and semantic color roles before changing labels or domain data.
- Use SVG-native animation for standalone output; do not leave runtime D3 or CDN dependencies in a self-contained deliverable.
- Include an SVG `<title>`, `<desc>`, stable `viewBox`, and final-state geometry.

#### Source Excerpt

The excerpt below is the compact renderer source for this pattern. If it references helpers such as `prepareSvg`, `fadeIn`, `grow`, `drawPath`, `palette`, `ramps`, `axisBottom`, or `axisLeft`, read `references/shared-renderer-helpers.md` and recreate only the needed helper behavior in the final artifact.

```js
function renderParallelCoordinates() {
    const svg = prepareSvg("parallel-coordinates", "Parallel coordinates", "Multiple numeric dimensions drawn as connected axes.");
    const dims = ["Speed", "Cost", "Quality", "Risk", "Reach"];
    const rows = [
      { name: "A", values: [82, 35, 76, 42, 66] }, { name: "B", values: [58, 62, 64, 38, 74] },
      { name: "C", values: [70, 47, 88, 58, 52] }, { name: "D", values: [45, 72, 55, 66, 86] }
    ];
    const x = d3.scalePoint().domain(dims).range([58, width - 44]);
    const y = d3.scaleLinear().domain([0, 100]).range([330, 62]);
    const line = d3.line().x((d, i) => x(dims[i])).y(d => y(d)).curve(d3.curveMonotoneX);
    dims.forEach(dim => {
      svg.append("g").attr("class", "axis").attr("transform", `translate(${x(dim)},0)`).call(d3.axisLeft(y).ticks(4));
      svg.append("text").attr("class", "mark-label").attr("x", x(dim)).attr("y", 42).attr("text-anchor", "middle").text(dim);
    });
    const paths = svg.append("g").attr("fill", "none").attr("stroke-width", 2.4).selectAll("path").data(rows).join("path")
      .attr("d", d => line(d.values)).attr("stroke", (d, i) => colors[i]).attr("stroke-opacity", .78);
    drawPath(paths, .15, .95);
  }
```

## d3-hexbin

### Hexbin Field

- **Pattern ID:** `d3-hexbin`
- **Gallery source ID:** `hexbin`
- **Family:** Density
- **Use when:** Binned point density in hexagonal cells.
- **Renderer:** `renderHexbin`

#### Reuse Contract

- Use this file as the pattern source in isolated skill-only workspaces; read the gallery fixture only when maintaining that fixture.
- Keep data deterministic and inline small datasets.
- Preserve the pattern's core geometry and semantic color roles before changing labels or domain data.
- Use SVG-native animation for standalone output; do not leave runtime D3 or CDN dependencies in a self-contained deliverable.
- Include an SVG `<title>`, `<desc>`, stable `viewBox`, and final-state geometry.

#### Source Excerpt

The excerpt below is the compact renderer source for this pattern. If it references helpers such as `prepareSvg`, `fadeIn`, `grow`, `drawPath`, `palette`, `ramps`, `axisBottom`, or `axisLeft`, read `references/shared-renderer-helpers.md` and recreate only the needed helper behavior in the final artifact.

```js
function renderHexbin() {
    const svg = prepareSvg("hexbin", "Hexbin field", "Point density aggregated into hand-built hexagonal cells.");
    const pts = d3.range(180).map(i => [80 + (i * 37 % 390) + Math.sin(i) * 18, 62 + (i * 53 % 280) + Math.cos(i * .7) * 18]);
    const r = 16;
    const bins = new Map();
    pts.forEach(([px, py]) => {
      const q = Math.round(px / (r * 1.5));
      const row = Math.round((py - (q % 2) * r * .86) / (r * 1.72));
      const key = `${q}|${row}`;
      const cx = q * r * 1.5;
      const cy = row * r * 1.72 + (q % 2) * r * .86;
      const item = bins.get(key) || { x: cx, y: cy, count: 0 };
      item.count += 1;
      bins.set(key, item);
    });
    const cells = Array.from(bins.values()).filter(d => d.x > 45 && d.x < width - 35 && d.y > 35 && d.y < height - 35);
    const color = quantizedRamp([0, d3.max(cells, d => d.count)], ramps.heat);
    const hex = d3.range(6).map(i => [Math.cos(Math.PI / 3 * i) * r, Math.sin(Math.PI / 3 * i) * r]).map(d => d.join(",")).join(" ");
    const polygons = svg.append("g").selectAll("polygon").data(cells).join("polygon")
      .attr("points", hex).attr("transform", d => `translate(${d.x},${d.y})`).attr("fill", d => color(d.count)).attr("stroke", "#fff");
    fadeIn(polygons, .05, .65);
  }
```
