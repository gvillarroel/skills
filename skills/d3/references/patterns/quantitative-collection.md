# Quantitative Pattern Collection

Use the pattern index to route directly to one section in this compact collection. Read only that section and any reference it explicitly names.

## d3-bubble-scatter

### Bubble Scatter

- **Pattern ID:** `d3-bubble-scatter`
- **Gallery source ID:** `bubble-scatter`
- **Family:** Correlation
- **Use when:** Position, radius, and group encoded together.
- **Renderer:** `renderBubbleScatter`

#### Reuse Contract

- Use this file as the pattern source in isolated skill-only workspaces; read the gallery fixture only when maintaining that fixture.
- Keep data deterministic and inline small datasets.
- Preserve the pattern's core geometry and semantic color roles before changing labels or domain data.
- Use SVG-native animation for standalone output; do not leave runtime D3 or CDN dependencies in a self-contained deliverable.
- Include an SVG `<title>`, `<desc>`, stable `viewBox`, and final-state geometry.

#### Source Excerpt

The excerpt below is the compact renderer source for this pattern. If it references helpers such as `prepareSvg`, `fadeIn`, `grow`, `drawPath`, `palette`, `ramps`, `axisBottom`, or `axisLeft`, read `references/shared-renderer-helpers.md` and recreate only the needed helper behavior in the final artifact.

```js
function renderBubbleScatter() {
    const svg = prepareSvg("bubble-scatter", "Bubble scatter", "D3 scatterplot using radius and color encodings.");
    const data = d3.range(24).map(i => ({ x: 20 + i * 3 + (i % 4) * 8, y: 40 + Math.sin(i * .7) * 18 + (i % 5) * 9, r: 5 + (i % 6) * 2, group: i % 3 }));
    const margin = { top: 34, right: 36, bottom: 48, left: 54 };
    const x = d3.scaleLinear().domain([15, 120]).range([margin.left, width - margin.right]);
    const y = d3.scaleLinear().domain([15, 100]).range([height - margin.bottom, margin.top]);
    axisBottom(svg, x, height - margin.bottom, 5);
    axisLeft(svg, y, margin.left, 5);
    const dots = svg.append("g").selectAll("circle").data(data).join("circle")
      .attr("cx", d => x(d.x)).attr("cy", d => y(d.y)).attr("fill", d => colors[d.group]).attr("fill-opacity", .78).attr("stroke", "#fff");
    grow(dots, "r", 1, d => d.r, .08, .7);
  }
```

## d3-ridgeline

### Ridgeline

- **Pattern ID:** `d3-ridgeline`
- **Gallery source ID:** `ridgeline`
- **Family:** Distribution
- **Use when:** Stacked density curves for group comparison.
- **Renderer:** `renderRidgeline`

#### Reuse Contract

- Use this file as the pattern source in isolated skill-only workspaces; read the gallery fixture only when maintaining that fixture.
- Keep data deterministic and inline small datasets.
- Preserve the pattern's core geometry and semantic color roles before changing labels or domain data.
- Use SVG-native animation for standalone output; do not leave runtime D3 or CDN dependencies in a self-contained deliverable.
- Include an SVG `<title>`, `<desc>`, stable `viewBox`, and final-state geometry.

#### Source Excerpt

The excerpt below is the compact renderer source for this pattern. If it references helpers such as `prepareSvg`, `fadeIn`, `grow`, `drawPath`, `palette`, `ramps`, `axisBottom`, or `axisLeft`, read `references/shared-renderer-helpers.md` and recreate only the needed helper behavior in the final artifact.

```js
function renderRidgeline() {
    const svg = prepareSvg("ridgeline", "Ridgeline", "Stacked density curves reveal group shape differences.");
    const groups = ["North", "South", "East", "West"];
    const x = d3.scaleLinear().domain([0, 100]).range([54, width - 34]);
    const yBase = d3.scalePoint().domain(groups).range([82, 314]);
    const line = d3.area().x(d => x(d.x)).y0(0).y1(d => -d.y).curve(d3.curveBasis);
    groups.forEach((group, gi) => {
      const data = d3.range(28).map(i => ({ x: i * 3.7, y: 12 + Math.exp(-Math.pow((i - (9 + gi * 4)) / 5, 2)) * 62 }));
      const g = svg.append("g").attr("transform", `translate(0,${yBase(group)})`);
      g.append("path").datum(data).attr("d", line).attr("fill", colors[gi]).attr("fill-opacity", .72).attr("stroke", d3.color(colors[gi]).darker(.45));
      g.append("text").attr("class", "mark-label").attr("x", 42).attr("y", -8).text(group);
      fadeIn(g, .08 + gi * .08, .6);
    });
  }
```

## d3-histogram

### Histogram

- **Pattern ID:** `d3-histogram`
- **Gallery source ID:** `histogram`
- **Family:** Distribution
- **Use when:** Binned frequency with animated bars.
- **Renderer:** `renderHistogram`

#### Reuse Contract

- Use this file as the pattern source in isolated skill-only workspaces; read the gallery fixture only when maintaining that fixture.
- Keep data deterministic and inline small datasets.
- Preserve the pattern's core geometry and semantic color roles before changing labels or domain data.
- Use SVG-native animation for standalone output; do not leave runtime D3 or CDN dependencies in a self-contained deliverable.
- Include an SVG `<title>`, `<desc>`, stable `viewBox`, and final-state geometry.

#### Source Excerpt

The excerpt below is the compact renderer source for this pattern. If it references helpers such as `prepareSvg`, `fadeIn`, `grow`, `drawPath`, `palette`, `ramps`, `axisBottom`, or `axisLeft`, read `references/shared-renderer-helpers.md` and recreate only the needed helper behavior in the final artifact.

```js
function renderHistogram() {
    const svg = prepareSvg("histogram", "Histogram", "D3 bins continuous values into frequency bars.");
    const values = d3.range(90).map(i => 42 + Math.sin(i * .31) * 18 + Math.cos(i * .17) * 13 + (i % 7));
    const margin = { top: 34, right: 28, bottom: 48, left: 48 };
    const x = d3.scaleLinear().domain(d3.extent(values)).nice().range([margin.left, width - margin.right]);
    const bins = d3.bin().domain(x.domain()).thresholds(12)(values);
    const y = d3.scaleLinear().domain([0, d3.max(bins, d => d.length)]).nice().range([height - margin.bottom, margin.top]);
    axisBottom(svg, x, height - margin.bottom, 5);
    axisLeft(svg, y, margin.left, 4);
    const bars = svg.append("g").selectAll("rect").data(bins).join("rect")
      .attr("x", d => x(d.x0) + 1).attr("y", d => y(d.length)).attr("width", d => Math.max(1, x(d.x1) - x(d.x0) - 2))
      .attr("height", d => y(0) - y(d.length)).attr("fill", palette.blue).attr("rx", 2);
    fadeIn(bars, .05, .7);
  }
```

## d3-connected-scatter

### Connected Scatter

- **Pattern ID:** `d3-connected-scatter`
- **Gallery source ID:** `connected-scatter`
- **Family:** Correlation
- **Use when:** Trajectory across two changing measures.
- **Renderer:** `renderConnectedScatter`

#### Reuse Contract

- Use this file as the pattern source in isolated skill-only workspaces; read the gallery fixture only when maintaining that fixture.
- Keep data deterministic and inline small datasets.
- Preserve the pattern's core geometry and semantic color roles before changing labels or domain data.
- Use SVG-native animation for standalone output; do not leave runtime D3 or CDN dependencies in a self-contained deliverable.
- Include an SVG `<title>`, `<desc>`, stable `viewBox`, and final-state geometry.

#### Source Excerpt

The excerpt below is the compact renderer source for this pattern. If it references helpers such as `prepareSvg`, `fadeIn`, `grow`, `drawPath`, `palette`, `ramps`, `axisBottom`, or `axisLeft`, read `references/shared-renderer-helpers.md` and recreate only the needed helper behavior in the final artifact.

```js
function renderConnectedScatter() {
    const svg = prepareSvg("connected-scatter", "Connected scatter", "A D3 line through paired measures over time.");
    const data = d3.range(10).map(i => ({ t: i, x: 20 + i * 8 + Math.sin(i) * 5, y: 25 + i * 6 + Math.cos(i * .8) * 16 }));
    const margin = { top: 34, right: 36, bottom: 48, left: 54 };
    const x = d3.scaleLinear().domain([15, 100]).range([margin.left, width - margin.right]);
    const y = d3.scaleLinear().domain([10, 100]).range([height - margin.bottom, margin.top]);
    axisBottom(svg, x, height - margin.bottom, 5);
    axisLeft(svg, y, margin.left, 5);
    const line = d3.line().x(d => x(d.x)).y(d => y(d.y)).curve(d3.curveCatmullRom);
    const path = svg.append("path").datum(data).attr("d", line).attr("fill", "none").attr("stroke", palette.purple).attr("stroke-width", 3);
    drawPath(path, .1, 1);
    svg.append("g").selectAll("circle").data(data).join("circle").attr("cx", d => x(d.x)).attr("cy", d => y(d.y)).attr("r", 5).attr("fill", palette.orange);
  }
```

## d3-violin

### Violin Plot

- **Pattern ID:** `d3-violin`
- **Gallery source ID:** `violin`
- **Family:** Distribution
- **Use when:** Mirrored density shape for each group.
- **Renderer:** `renderViolin`

#### Reuse Contract

- Use this file as the pattern source in isolated skill-only workspaces; read the gallery fixture only when maintaining that fixture.
- Keep data deterministic and inline small datasets.
- Preserve the pattern's core geometry and semantic color roles before changing labels or domain data.
- Use SVG-native animation for standalone output; do not leave runtime D3 or CDN dependencies in a self-contained deliverable.
- Include an SVG `<title>`, `<desc>`, stable `viewBox`, and final-state geometry.

#### Source Excerpt

The excerpt below is the compact renderer source for this pattern. If it references helpers such as `prepareSvg`, `fadeIn`, `grow`, `drawPath`, `palette`, `ramps`, `axisBottom`, or `axisLeft`, read `references/shared-renderer-helpers.md` and recreate only the needed helper behavior in the final artifact.

```js
function renderViolin() {
    const svg = prepareSvg("violin", "Violin plot", "Mirrored density shapes derived from deterministic samples.");
    const groups = ["A", "B", "C"];
    const x = d3.scalePoint().domain(groups).range([105, width - 85]);
    const y = d3.scaleLinear().domain([15, 95]).range([height - 54, 42]);
    axisLeft(svg, y, 56, 5);
    const area = d3.area().x0(d => -d.w).x1(d => d.w).y(d => y(d.v)).curve(d3.curveBasis);
    groups.forEach((g, gi) => {
      const density = d3.range(28).map(i => {
        const v = 18 + i * 2.8;
        const w = 8 + Math.exp(-Math.pow((v - (42 + gi * 12)) / 18, 2)) * 35 + Math.sin(i * .5 + gi) * 3;
        return { v, w };
      });
      const grp = svg.append("g").attr("transform", `translate(${x(g)},0)`);
      grp.append("path").datum(density).attr("d", area).attr("fill", colors[gi]).attr("fill-opacity", .75).attr("stroke", "#fff");
      grp.append("text").attr("class", "mark-label").attr("x", 0).attr("y", height - 28).attr("text-anchor", "middle").text(g);
      fadeIn(grp, .1 + gi * .08, .7);
    });
  }
```

## d3-slope

### Slope Chart

- **Pattern ID:** `d3-slope`
- **Gallery source ID:** `slope`
- **Family:** Temporal
- **Use when:** Before-after movement with labels.
- **Renderer:** `renderSlope`

#### Reuse Contract

- Use this file as the pattern source in isolated skill-only workspaces; read the gallery fixture only when maintaining that fixture.
- Keep data deterministic and inline small datasets.
- Preserve the pattern's core geometry and semantic color roles before changing labels or domain data.
- Use SVG-native animation for standalone output; do not leave runtime D3 or CDN dependencies in a self-contained deliverable.
- Include an SVG `<title>`, `<desc>`, stable `viewBox`, and final-state geometry.

#### Source Excerpt

The excerpt below is the compact renderer source for this pattern. If it references helpers such as `prepareSvg`, `fadeIn`, `grow`, `drawPath`, `palette`, `ramps`, `axisBottom`, or `axisLeft`, read `references/shared-renderer-helpers.md` and recreate only the needed helper behavior in the final artifact.

```js
function renderSlope() {
    const svg = prepareSvg("slope", "Slope chart", "Before-after comparison with connected labels.");
    const data = [
      { name: "API", a: 42, b: 75 }, { name: "Search", a: 61, b: 68 }, { name: "Jobs", a: 74, b: 52 },
      { name: "Billing", a: 38, b: 59 }, { name: "Reports", a: 52, b: 82 }
    ];
    const y = d3.scaleLinear().domain([30, 90]).range([330, 54]);
    const x1 = 130, x2 = 410;
    axisLeft(svg, y, 70, 5);
    svg.append("text").attr("class", "mark-label").attr("x", x1).attr("y", 36).attr("text-anchor", "middle").text("Before");
    svg.append("text").attr("class", "mark-label").attr("x", x2).attr("y", 36).attr("text-anchor", "middle").text("After");
    const lines = svg.append("g").selectAll("line").data(data).join("line")
      .attr("x1", x1).attr("x2", x2).attr("y1", d => y(d.a)).attr("y2", d => y(d.b)).attr("stroke", (d, i) => colors[i]).attr("stroke-width", 2.5);
    fadeIn(lines, .1, .7);
    svg.append("g").selectAll("text").data(data).join("text").attr("class", "label")
      .attr("x", x2 + 12).attr("y", d => y(d.b) + 4).text(d => d.name);
  }
```

## d3-lollipop

### Lollipop

- **Pattern ID:** `d3-lollipop`
- **Gallery source ID:** `lollipop`
- **Family:** Ranking
- **Use when:** Ranked values with reduced bar ink.
- **Renderer:** `renderLollipop`

#### Reuse Contract

- Use this file as the pattern source in isolated skill-only workspaces; read the gallery fixture only when maintaining that fixture.
- Keep data deterministic and inline small datasets.
- Preserve the pattern's core geometry and semantic color roles before changing labels or domain data.
- Use SVG-native animation for standalone output; do not leave runtime D3 or CDN dependencies in a self-contained deliverable.
- Include an SVG `<title>`, `<desc>`, stable `viewBox`, and final-state geometry.

#### Source Excerpt

The excerpt below is the compact renderer source for this pattern. If it references helpers such as `prepareSvg`, `fadeIn`, `grow`, `drawPath`, `palette`, `ramps`, `axisBottom`, or `axisLeft`, read `references/shared-renderer-helpers.md` and recreate only the needed helper behavior in the final artifact.

```js
function renderLollipop() {
    const svg = prepareSvg("lollipop", "Lollipop chart", "Ranked values with stems and endpoints.");
    const data = ["API", "Search", "Jobs", "Billing", "Reports", "Auth"].map((name, i) => ({ name, value: [86, 74, 68, 59, 51, 45][i] }));
    const x = d3.scaleLinear().domain([0, 100]).range([100, width - 50]);
    const y = d3.scaleBand().domain(data.map(d => d.name)).range([54, 330]).padding(.42);
    axisBottom(svg, x, 350, 5);
    svg.append("g").selectAll("line").data(data).join("line").attr("x1", x(0)).attr("x2", d => x(d.value)).attr("y1", d => y(d.name) + y.bandwidth() / 2).attr("y2", d => y(d.name) + y.bandwidth() / 2).attr("stroke", palette.gray200).attr("stroke-width", 3);
    const circles = svg.append("g").selectAll("circle").data(data).join("circle").attr("cx", d => x(d.value)).attr("cy", d => y(d.name) + y.bandwidth() / 2).attr("fill", palette.blue);
    grow(circles, "r", 1, 9, .1, .65);
    svg.append("g").selectAll("text").data(data).join("text").attr("class", "mark-label").attr("x", 88).attr("y", d => y(d.name) + y.bandwidth() / 2 + 4).attr("text-anchor", "end").text(d => d.name);
  }
```

## d3-bump

### Bump Chart

- **Pattern ID:** `d3-bump`
- **Gallery source ID:** `bump`
- **Family:** Temporal
- **Use when:** Rank changes across time periods.
- **Renderer:** `renderBump`

#### Reuse Contract

- Use this file as the pattern source in isolated skill-only workspaces; read the gallery fixture only when maintaining that fixture.
- Keep data deterministic and inline small datasets.
- Preserve the pattern's core geometry and semantic color roles before changing labels or domain data.
- Use SVG-native animation for standalone output; do not leave runtime D3 or CDN dependencies in a self-contained deliverable.
- Include an SVG `<title>`, `<desc>`, stable `viewBox`, and final-state geometry.

#### Source Excerpt

The excerpt below is the compact renderer source for this pattern. If it references helpers such as `prepareSvg`, `fadeIn`, `grow`, `drawPath`, `palette`, `ramps`, `axisBottom`, or `axisLeft`, read `references/shared-renderer-helpers.md` and recreate only the needed helper behavior in the final artifact.

```js
function renderBump() {
    const svg = prepareSvg("bump", "Bump chart", "Rank movement across ordered periods.");
    const names = ["Alpha", "Beta", "Gamma", "Delta"];
    const periods = ["Q1", "Q2", "Q3", "Q4", "Q5"];
    const ranks = { Alpha: [1, 2, 2, 1, 1], Beta: [2, 1, 3, 3, 2], Gamma: [3, 4, 1, 2, 3], Delta: [4, 3, 4, 4, 4] };
    const x = d3.scalePoint().domain(periods).range([70, width - 50]);
    const y = d3.scalePoint().domain([1, 2, 3, 4]).range([70, 320]);
    periods.forEach(p => svg.append("text").attr("class", "label").attr("x", x(p)).attr("y", 350).attr("text-anchor", "middle").text(p));
    [1, 2, 3, 4].forEach(r => svg.append("text").attr("class", "label").attr("x", 48).attr("y", y(r) + 4).attr("text-anchor", "end").text(`#${r}`));
    const line = d3.line().x((d, i) => x(periods[i])).y(d => y(d)).curve(d3.curveMonotoneX);
    names.forEach((name, i) => {
      const path = svg.append("path").datum(ranks[name]).attr("d", line).attr("fill", "none").attr("stroke", colors[i]).attr("stroke-width", 3);
      drawPath(path, .12 + i * .05, .9);
      svg.append("text").attr("class", "mark-label").attr("x", width - 46).attr("y", y(ranks[name].at(-1)) + 4).attr("text-anchor", "end").text(name);
    });
  }
```
