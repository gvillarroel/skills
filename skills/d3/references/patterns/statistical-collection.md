# Statistical and Analytical Pattern Collection

Use the pattern index to route directly to one section in this compact collection. Read only that section and any reference it explicitly names.

## d3-qq-plot

### Q-Q Plot

- **Pattern ID:** `d3-qq-plot`
- **Gallery source ID:** `qq-plot`
- **Family:** Diagnostics
- **Use when:** Sample quantiles are compared against a reference line.
- **Renderer:** `renderQqPlot`

#### Reuse Contract

- Use this file as the pattern source in isolated skill-only workspaces; read the gallery fixture only when maintaining that fixture.
- Keep data deterministic and inline small datasets.
- Preserve the pattern's core geometry and semantic color roles before changing labels or domain data.
- Use SVG-native animation for standalone output; do not leave runtime D3 or CDN dependencies in a self-contained deliverable.
- Include an SVG `<title>`, `<desc>`, stable `viewBox`, and final-state geometry.

#### Source Excerpt

The excerpt below is the compact renderer source for this pattern. If it references helpers such as `prepareSvg`, `fadeIn`, `grow`, `drawPath`, `palette`, `ramps`, `axisBottom`, or `axisLeft`, read `references/shared-renderer-helpers.md` and recreate only the needed helper behavior in the final artifact.

```js
function renderQqPlot() {
    const svg = prepareSvg("qq-plot", "Q-Q plot", "Sample quantiles are compared against a theoretical reference line.");
    const theoretical = [-2.05, -1.55, -1.2, -.94, -.72, -.53, -.34, -.17, 0, .17, .34, .53, .72, .94, 1.2, 1.55, 2.05];
    const sample = theoretical.map((q, i) => ({ q, value: q * 1.12 + Math.sin(i * .8) * .32 + (i > 12 ? .3 : 0) }));
    const margin = { top: 40, right: 40, bottom: 56, left: 58 };
    const x = d3.scaleLinear().domain([-2.3, 2.3]).range([margin.left, width - margin.right]);
    const y = d3.scaleLinear().domain([-2.6, 2.8]).range([height - margin.bottom, margin.top]);
    axisBottom(svg, x, height - margin.bottom, 5);
    axisLeft(svg, y, margin.left, 5);
    const ref = svg.append("line").attr("x1", x(-2.2)).attr("x2", x(2.2)).attr("y1", y(-2.2)).attr("y2", y(2.2)).attr("stroke", palette.gray400).attr("stroke-width", 2).attr("stroke-dasharray", "5 5");
    fadeIn(ref, .05, .5);
    const dots = svg.append("g").selectAll("circle").data(sample).join("circle")
      .attr("cx", d => x(d.q)).attr("cy", d => y(d.value)).attr("fill", d => Math.abs(d.value - d.q) > .42 ? palette.red : palette.blue).attr("stroke", "#fff");
    grow(dots, "r", 1, 6, .08, .55);
    svg.append("text").attr("class", "mark-label").attr("fill", palette.red).attr("x", width - 46).attr("y", 34).attr("text-anchor", "end").text("tail deviation");
  }
```

## d3-dot-plot

### Dot Plot

- **Pattern ID:** `d3-dot-plot`
- **Gallery source ID:** `dot-plot`
- **Family:** Ranking
- **Use when:** Compact ranked points compare paired measures.
- **Renderer:** `renderDotPlot`

#### Reuse Contract

- Use this file as the pattern source in isolated skill-only workspaces; read the gallery fixture only when maintaining that fixture.
- Keep data deterministic and inline small datasets.
- Preserve the pattern's core geometry and semantic color roles before changing labels or domain data.
- Use SVG-native animation for standalone output; do not leave runtime D3 or CDN dependencies in a self-contained deliverable.
- Include an SVG `<title>`, `<desc>`, stable `viewBox`, and final-state geometry.

#### Source Excerpt

The excerpt below is the compact renderer source for this pattern. If it references helpers such as `prepareSvg`, `fadeIn`, `grow`, `drawPath`, `palette`, `ramps`, `axisBottom`, or `axisLeft`, read `references/shared-renderer-helpers.md` and recreate only the needed helper behavior in the final artifact.

```js
function renderDotPlot() {
    const svg = prepareSvg("dot-plot", "Dot plot", "Compact ranked points compare paired measures.");
    const data = [
      ["Model", 68, 82], ["Data", 54, 71], ["UX", 46, 63], ["Ops", 73, 78], ["Infra", 38, 56], ["QA", 62, 69]
    ].map(d => ({ name: d[0], a: d[1], b: d[2] }));
    const margin = { top: 44, right: 48, bottom: 48, left: 100 };
    const x = d3.scaleLinear().domain([30, 90]).range([margin.left, width - margin.right]);
    const y = d3.scalePoint().domain(data.map(d => d.name)).range([76, 316]).padding(.5);
    axisBottom(svg, x, 340, 6);
    svg.selectAll(".dot-label").data(data).join("text").attr("class", "mark-label").attr("x", margin.left - 14).attr("y", d => y(d.name)).attr("text-anchor", "end").attr("dy", ".35em").text(d => d.name);
    const links = svg.append("g").selectAll("line").data(data).join("line")
      .attr("x1", d => x(d.a)).attr("x2", d => x(d.b)).attr("y1", d => y(d.name)).attr("y2", d => y(d.name)).attr("stroke", palette.line).attr("stroke-width", 3);
    fadeIn(links, .08, .55);
    const points = svg.append("g").selectAll("circle").data(data.flatMap(d => [{ ...d, value: d.a, color: palette.blue }, { ...d, value: d.b, color: palette.red }])).join("circle")
      .attr("cx", d => x(d.value)).attr("cy", d => y(d.name)).attr("fill", d => d.color).attr("stroke", "#fff").attr("stroke-width", 1.5);
    grow(points, "r", 2, 7, .12, .55);
  }
```

## d3-boxplot

### Box Plot

- **Pattern ID:** `d3-boxplot`
- **Gallery source ID:** `boxplot`
- **Family:** Distribution
- **Use when:** Quartiles, whiskers, and outliers per group.
- **Renderer:** `renderBoxPlot`

#### Reuse Contract

- Use this file as the pattern source in isolated skill-only workspaces; read the gallery fixture only when maintaining that fixture.
- Keep data deterministic and inline small datasets.
- Preserve the pattern's core geometry and semantic color roles before changing labels or domain data.
- Use SVG-native animation for standalone output; do not leave runtime D3 or CDN dependencies in a self-contained deliverable.
- Include an SVG `<title>`, `<desc>`, stable `viewBox`, and final-state geometry.

#### Source Excerpt

The excerpt below is the compact renderer source for this pattern. If it references helpers such as `prepareSvg`, `fadeIn`, `grow`, `drawPath`, `palette`, `ramps`, `axisBottom`, or `axisLeft`, read `references/shared-renderer-helpers.md` and recreate only the needed helper behavior in the final artifact.

```js
function renderBoxPlot() {
    const svg = prepareSvg("boxplot", "Box plot", "Quartile summaries and outliers across groups.");
    const groups = ["A", "B", "C"];
    const values = groups.map((g, gi) => d3.range(28).map(i => 36 + gi * 12 + Math.sin(i * .6 + gi) * 10 + (i % 5)));
    const stats = values.map((arr, i) => {
      const sorted = arr.slice().sort(d3.ascending);
      return { group: groups[i], min: d3.min(sorted), q1: d3.quantile(sorted, .25), median: d3.quantile(sorted, .5), q3: d3.quantile(sorted, .75), max: d3.max(sorted) };
    });
    const x = d3.scaleBand().domain(groups).range([80, width - 50]).padding(.35);
    const y = d3.scaleLinear().domain([20, 85]).range([height - 58, 42]);
    axisLeft(svg, y, 56, 5);
    const g = svg.append("g").selectAll("g").data(stats).join("g").attr("transform", d => `translate(${x(d.group) + x.bandwidth() / 2},0)`);
    g.append("line").attr("y1", d => y(d.min)).attr("y2", d => y(d.max)).attr("stroke", palette.ink);
    g.append("rect").attr("x", -28).attr("y", d => y(d.q3)).attr("width", 56).attr("height", d => y(d.q1) - y(d.q3)).attr("fill", palette.orange).attr("fill-opacity", .75).attr("stroke", "#fff");
    g.append("line").attr("x1", -32).attr("x2", 32).attr("y1", d => y(d.median)).attr("y2", d => y(d.median)).attr("stroke", palette.ink).attr("stroke-width", 2);
    svg.append("g").attr("class", "axis").attr("transform", `translate(0,${height - 58})`).call(d3.axisBottom(x));
    fadeIn(g, .05, .7);
  }
```

## d3-ecdf

### Empirical CDF

- **Pattern ID:** `d3-ecdf`
- **Gallery source ID:** `ecdf`
- **Family:** Distribution
- **Use when:** Cumulative probability reveals quantiles and tails.
- **Renderer:** `renderEcdf`

#### Reuse Contract

- Use this file as the pattern source in isolated skill-only workspaces; read the gallery fixture only when maintaining that fixture.
- Keep data deterministic and inline small datasets.
- Preserve the pattern's core geometry and semantic color roles before changing labels or domain data.
- Use SVG-native animation for standalone output; do not leave runtime D3 or CDN dependencies in a self-contained deliverable.
- Include an SVG `<title>`, `<desc>`, stable `viewBox`, and final-state geometry.

#### Source Excerpt

The excerpt below is the compact renderer source for this pattern. If it references helpers such as `prepareSvg`, `fadeIn`, `grow`, `drawPath`, `palette`, `ramps`, `axisBottom`, or `axisLeft`, read `references/shared-renderer-helpers.md` and recreate only the needed helper behavior in the final artifact.

```js
function renderEcdf() {
    const svg = prepareSvg("ecdf", "Empirical CDF", "Sorted observations accumulate into cumulative probability.");
    const values = d3.range(48).map(i => 28 + Math.sin(i * .47) * 15 + Math.cos(i * .19) * 12 + i * .65).sort(d3.ascending);
    const data = values.map((value, i) => ({ value, p: (i + 1) / values.length }));
    const margin = { top: 38, right: 34, bottom: 52, left: 56 };
    const x = d3.scaleLinear().domain(d3.extent(values)).nice().range([margin.left, width - margin.right]);
    const y = d3.scaleLinear().domain([0, 1]).range([height - margin.bottom, margin.top]);
    axisBottom(svg, x, height - margin.bottom, 5);
    axisLeft(svg, y, margin.left, 5);
    const rug = svg.append("g").selectAll("line").data(values).join("line")
      .attr("x1", d => x(d)).attr("x2", d => x(d))
      .attr("y1", height - margin.bottom + 8).attr("y2", height - margin.bottom + 20)
      .attr("stroke", palette.cyan).attr("stroke-width", 1.4);
    fadeIn(rug, .03, .5);
    const line = d3.line().x(d => x(d.value)).y(d => y(d.p)).curve(d3.curveStepAfter);
    const path = svg.append("path").datum(data).attr("d", line).attr("fill", "none").attr("stroke", palette.blue).attr("stroke-width", 3);
    drawPath(path, .15, 1);
    [.25, .5, .75].forEach(q => {
      const value = d3.quantileSorted(values, q);
      svg.append("line").attr("x1", x(value)).attr("x2", x(value)).attr("y1", y(q)).attr("y2", height - margin.bottom)
        .attr("stroke", palette.orange).attr("stroke-dasharray", "4 5");
      svg.append("text").attr("class", "label").attr("x", x(value) + 5).attr("y", y(q) - 5).text(`q${q * 100}`);
    });
  }
```

## d3-bullet

### Bullet Chart

- **Pattern ID:** `d3-bullet`
- **Gallery source ID:** `bullet`
- **Family:** Performance
- **Use when:** Target, ranges, and current value in compact form.
- **Renderer:** `renderBullet`

#### Reuse Contract

- Use this file as the pattern source in isolated skill-only workspaces; read the gallery fixture only when maintaining that fixture.
- Keep data deterministic and inline small datasets.
- Preserve the pattern's core geometry and semantic color roles before changing labels or domain data.
- Use SVG-native animation for standalone output; do not leave runtime D3 or CDN dependencies in a self-contained deliverable.
- Include an SVG `<title>`, `<desc>`, stable `viewBox`, and final-state geometry.

#### Source Excerpt

The excerpt below is the compact renderer source for this pattern. If it references helpers such as `prepareSvg`, `fadeIn`, `grow`, `drawPath`, `palette`, `ramps`, `axisBottom`, or `axisLeft`, read `references/shared-renderer-helpers.md` and recreate only the needed helper behavior in the final artifact.

```js
function renderBullet() {
    const svg = prepareSvg("bullet", "Bullet chart", "Compact performance bands compare current value against a target.");
    const data = [
      { name: "Latency", value: 72, target: 64, ranges: [45, 68, 90] },
      { name: "Quality", value: 83, target: 78, ranges: [55, 75, 95] },
      { name: "Reach", value: 58, target: 70, ranges: [40, 62, 88] }
    ];
    const x = d3.scaleLinear().domain([0, 100]).range([122, width - 44]);
    const y = d3.scaleBand().domain(data.map(d => d.name)).range([78, 310]).padding(.42);
    data.forEach(row => {
      const g = svg.append("g").attr("transform", `translate(0,${y(row.name)})`);
      row.ranges.slice().reverse().forEach((range, i) => {
        g.append("rect").attr("x", x(0)).attr("y", 0).attr("width", x(range) - x(0)).attr("height", y.bandwidth())
          .attr("fill", ["#dfe6ee", "#c4ceda", "#aab8c7"][i]).attr("rx", 4);
      });
      const value = g.append("rect").attr("x", x(0)).attr("y", y.bandwidth() * .28)
        .attr("width", x(row.value) - x(0)).attr("height", y.bandwidth() * .44)
        .attr("fill", palette.blue).attr("rx", 3);
      value.append("animate").attr("attributeName", "width").attr("from", 0).attr("to", x(row.value) - x(0)).attr("dur", ".8s").attr("fill", "freeze");
      g.append("line").attr("x1", x(row.target)).attr("x2", x(row.target)).attr("y1", -4).attr("y2", y.bandwidth() + 4)
        .attr("stroke", palette.ink).attr("stroke-width", 2.2);
      g.append("text").attr("class", "mark-label").attr("x", 108).attr("y", y.bandwidth() / 2 + 4).attr("text-anchor", "end").text(row.name);
    });
    axisBottom(svg, x, 342, 5);
  }
```

## d3-point-range

### Point Range

- **Pattern ID:** `d3-point-range`
- **Gallery source ID:** `point-range`
- **Family:** Uncertainty
- **Use when:** Estimates with confidence intervals by group.
- **Renderer:** `renderPointRange`

#### Reuse Contract

- Use this file as the pattern source in isolated skill-only workspaces; read the gallery fixture only when maintaining that fixture.
- Keep data deterministic and inline small datasets.
- Preserve the pattern's core geometry and semantic color roles before changing labels or domain data.
- Use SVG-native animation for standalone output; do not leave runtime D3 or CDN dependencies in a self-contained deliverable.
- Include an SVG `<title>`, `<desc>`, stable `viewBox`, and final-state geometry.

#### Source Excerpt

The excerpt below is the compact renderer source for this pattern. If it references helpers such as `prepareSvg`, `fadeIn`, `grow`, `drawPath`, `palette`, `ramps`, `axisBottom`, or `axisLeft`, read `references/shared-renderer-helpers.md` and recreate only the needed helper behavior in the final artifact.

```js
function renderPointRange() {
    const svg = prepareSvg("point-range", "Point range", "Estimates and uncertainty intervals show overlap across groups.");
    const data = ["Alpha", "Beta", "Gamma", "Delta", "Epsilon"].map((name, i) => {
      const estimate = [42, 55, 63, 48, 71][i];
      const low = estimate - [8, 11, 7, 13, 9][i];
      const high = estimate + [10, 8, 12, 9, 7][i];
      return { name, estimate, low, high };
    });
    const x = d3.scaleLinear().domain([25, 85]).range([86, width - 44]);
    const y = d3.scaleBand().domain(data.map(d => d.name)).range([64, 326]).padding(.45);
    axisBottom(svg, x, 350, 5);
    const ranges = svg.append("g").selectAll("line").data(data).join("line")
      .attr("x1", d => x(d.low)).attr("x2", d => x(d.high))
      .attr("y1", d => y(d.name) + y.bandwidth() / 2)
      .attr("y2", d => y(d.name) + y.bandwidth() / 2)
      .attr("stroke", "#8fa0b3").attr("stroke-width", 4).attr("stroke-linecap", "round");
    drawPath(ranges, .08, .75);
    const dots = svg.append("g").selectAll("circle").data(data).join("circle")
      .attr("cx", d => x(d.estimate)).attr("cy", d => y(d.name) + y.bandwidth() / 2)
      .attr("fill", palette.orange).attr("stroke", "#fff").attr("stroke-width", 1.6);
    grow(dots, "r", 2, 8, .18, .55);
    svg.append("g").selectAll("text").data(data).join("text")
      .attr("class", "mark-label").attr("x", 74).attr("y", d => y(d.name) + y.bandwidth() / 2 + 4)
      .attr("text-anchor", "end").text(d => d.name);
  }
```

## d3-barcode-plot

### Barcode Plot

- **Pattern ID:** `d3-barcode-plot`
- **Gallery source ID:** `barcode-plot`
- **Family:** Events
- **Use when:** Dense event timing as ordered tick marks.
- **Renderer:** `renderBarcode`

#### Reuse Contract

- Use this file as the pattern source in isolated skill-only workspaces; read the gallery fixture only when maintaining that fixture.
- Keep data deterministic and inline small datasets.
- Preserve the pattern's core geometry and semantic color roles before changing labels or domain data.
- Use SVG-native animation for standalone output; do not leave runtime D3 or CDN dependencies in a self-contained deliverable.
- Include an SVG `<title>`, `<desc>`, stable `viewBox`, and final-state geometry.

#### Source Excerpt

The excerpt below is the compact renderer source for this pattern. If it references helpers such as `prepareSvg`, `fadeIn`, `grow`, `drawPath`, `palette`, `ramps`, `axisBottom`, or `axisLeft`, read `references/shared-renderer-helpers.md` and recreate only the needed helper behavior in the final artifact.

```js
function renderBarcode() {
    const svg = prepareSvg("barcode-plot", "Barcode plot", "Dense event times are encoded as ordered ticks on multiple lanes.");
    const lanes = ["API", "Jobs", "Search", "Billing"];
    const data = lanes.flatMap((lane, li) => d3.range(24).map(i => ({
      lane,
      time: (i * (7 + li * 2) + li * 9) % 96,
      severity: (i + li) % 4
    }))).sort((a, b) => d3.ascending(a.time, b.time));
    const x = d3.scaleLinear().domain([0, 100]).range([82, width - 36]);
    const y = d3.scaleBand().domain(lanes).range([72, 314]).padding(.34);
    axisBottom(svg, x, 346, 5);
    svg.append("g").selectAll("text").data(lanes).join("text")
      .attr("class", "mark-label").attr("x", 68).attr("y", d => y(d) + y.bandwidth() / 2 + 4)
      .attr("text-anchor", "end").text(d => d);
    const ticks = svg.append("g").selectAll("line").data(data).join("line")
      .attr("x1", d => x(d.time)).attr("x2", d => x(d.time))
      .attr("y1", d => y(d.lane)).attr("y2", d => y(d.lane) + y.bandwidth())
      .attr("stroke", d => colors[d.severity]).attr("stroke-width", 2.1).attr("stroke-linecap", "round");
    fadeIn(ticks, .035, .55);
    lanes.forEach(lane => {
      svg.append("line").attr("x1", x(0)).attr("x2", x(100)).attr("y1", y(lane) + y.bandwidth() + 7).attr("y2", y(lane) + y.bandwidth() + 7)
        .attr("stroke", "#e3e8ee");
    });
  }
```

## d3-facet-sparklines

### Facet Sparklines

- **Pattern ID:** `d3-facet-sparklines`
- **Gallery source ID:** `facet-sparklines`
- **Family:** Small multiples
- **Use when:** Repeated scales compare patterns across panels.
- **Renderer:** `renderFacets`

#### Reuse Contract

- Use this file as the pattern source in isolated skill-only workspaces; read the gallery fixture only when maintaining that fixture.
- Keep data deterministic and inline small datasets.
- Preserve the pattern's core geometry and semantic color roles before changing labels or domain data.
- Use SVG-native animation for standalone output; do not leave runtime D3 or CDN dependencies in a self-contained deliverable.
- Include an SVG `<title>`, `<desc>`, stable `viewBox`, and final-state geometry.

#### Source Excerpt

The excerpt below is the compact renderer source for this pattern. If it references helpers such as `prepareSvg`, `fadeIn`, `grow`, `drawPath`, `palette`, `ramps`, `axisBottom`, or `axisLeft`, read `references/shared-renderer-helpers.md` and recreate only the needed helper behavior in the final artifact.

```js
function renderFacets() {
    const svg = prepareSvg("facet-sparklines", "Facet sparklines", "Small multiples repeat scale and encoding across comparable panels.");
    const groups = ["North", "South", "East", "West", "Core", "Labs"];
    const data = groups.map((name, gi) => ({
      name,
      values: d3.range(18).map(i => ({ x: i, y: 42 + Math.sin(i / 2.5 + gi) * 18 + Math.cos(i / 4 + gi * .7) * 9 }))
    }));
    const panelW = 150, panelH = 92;
    const x = d3.scaleLinear().domain([0, 17]).range([18, panelW - 14]);
    const y = d3.scaleLinear().domain([15, 75]).range([panelH - 22, 16]);
    const line = d3.line().x(d => x(d.x)).y(d => y(d.y)).curve(d3.curveMonotoneX);
    const panels = svg.append("g").selectAll("g").data(data).join("g")
      .attr("transform", (d, i) => `translate(${54 + (i % 3) * 162},${48 + Math.floor(i / 3) * 142})`);
    panels.append("rect").attr("width", panelW).attr("height", panelH).attr("rx", 6).attr("fill", palette.gray50).attr("stroke", palette.gray200);
    const paths = panels.append("path").attr("d", d => line(d.values)).attr("fill", "none").attr("stroke", (d, i) => colors[i % colors.length]).attr("stroke-width", 2.3);
    drawPath(paths, .08, .7);
    panels.append("text").attr("class", "mark-label").attr("x", 12).attr("y", 14).text(d => d.name);
  }
```

## d3-normalized-stacked-area

### Normalized Stacked Area

- **Pattern ID:** `d3-normalized-stacked-area`
- **Gallery source ID:** `normalized-stacked-area`
- **Family:** Temporal
- **Use when:** Category shares sum to 100 percent across time.
- **Renderer:** `renderNormalizedStackedArea`

#### Reuse Contract

- Use this file as the pattern source in isolated skill-only workspaces; read the gallery fixture only when maintaining that fixture.
- Keep data deterministic and inline small datasets.
- Preserve the pattern's core geometry and semantic color roles before changing labels or domain data.
- Use SVG-native animation for standalone output; do not leave runtime D3 or CDN dependencies in a self-contained deliverable.
- Include an SVG `<title>`, `<desc>`, stable `viewBox`, and final-state geometry.

#### Source Excerpt

The excerpt below is the compact renderer source for this pattern. If it references helpers such as `prepareSvg`, `fadeIn`, `grow`, `drawPath`, `palette`, `ramps`, `axisBottom`, or `axisLeft`, read `references/shared-renderer-helpers.md` and recreate only the needed helper behavior in the final artifact.

```js
function renderNormalizedStackedArea() {
    const svg = prepareSvg("normalized-stacked-area", "Normalized stacked area", "Category shares sum to 100 percent across time.");
    const keys = ["Search", "Assist", "Build", "Review"];
    const data = d3.range(10).map(i => ({
      t: i,
      Search: 28 + Math.sin(i / 1.4) * 8,
      Assist: 22 + i * 2.2,
      Build: 30 + Math.cos(i / 1.7) * 9,
      Review: 16 + Math.sin(i / 2 + 1) * 6
    }));
    const margin = { top: 42, right: 34, bottom: 54, left: 58 };
    const series = d3.stack().keys(keys).offset(d3.stackOffsetExpand)(data);
    const x = d3.scaleLinear().domain(d3.extent(data, d => d.t)).range([margin.left, width - margin.right]);
    const y = d3.scaleLinear().domain([0, 1]).range([height - margin.bottom, margin.top]);
    const area = d3.area().x(d => x(d.data.t)).y0(d => y(d[0])).y1(d => y(d[1])).curve(d3.curveBasis);
    const layers = svg.append("g").selectAll("path").data(series).join("path")
      .attr("d", area).attr("fill", (d, i) => colors[i]).attr("opacity", .88);
    fadeIn(layers, .08, .75);
    axisBottom(svg, x, height - margin.bottom, 5);
    axisLeft(svg, y.tickFormat ? y : y, margin.left, 4);
    svg.append("text").attr("class", "label").attr("x", margin.left).attr("y", 30).text("share of total");
  }
```

## d3-moving-average

### Moving Average

- **Pattern ID:** `d3-moving-average`
- **Gallery source ID:** `moving-average`
- **Family:** Analysis
- **Use when:** A smoothed trend line separates signal from noise.
- **Renderer:** `renderMovingAverage`

#### Reuse Contract

- Use this file as the pattern source in isolated skill-only workspaces; read the gallery fixture only when maintaining that fixture.
- Keep data deterministic and inline small datasets.
- Preserve the pattern's core geometry and semantic color roles before changing labels or domain data.
- Use SVG-native animation for standalone output; do not leave runtime D3 or CDN dependencies in a self-contained deliverable.
- Include an SVG `<title>`, `<desc>`, stable `viewBox`, and final-state geometry.

#### Source Excerpt

The excerpt below is the compact renderer source for this pattern. If it references helpers such as `prepareSvg`, `fadeIn`, `grow`, `drawPath`, `palette`, `ramps`, `axisBottom`, or `axisLeft`, read `references/shared-renderer-helpers.md` and recreate only the needed helper behavior in the final artifact.

```js
function renderMovingAverage() {
    const svg = prepareSvg("moving-average", "Moving average", "A rolling mean separates a smoother trend from noisy observations.");
    const data = d3.range(32).map(i => ({ t: i, y: 44 + Math.sin(i / 2.4) * 13 + Math.cos(i * .85) * 7 + i * .8 }));
    const smooth = data.map((d, i) => {
      const window = data.slice(Math.max(0, i - 2), Math.min(data.length, i + 3));
      return { t: d.t, y: d3.mean(window, item => item.y) };
    });
    const margin = { top: 34, right: 34, bottom: 48, left: 54 };
    const x = d3.scaleLinear().domain(d3.extent(data, d => d.t)).range([margin.left, width - margin.right]);
    const y = d3.scaleLinear().domain([25, 88]).range([height - margin.bottom, margin.top]);
    axisBottom(svg, x, height - margin.bottom, 5);
    axisLeft(svg, y, margin.left, 4);
    const line = d3.line().x(d => x(d.t)).y(d => y(d.y)).curve(d3.curveMonotoneX);
    const noisy = svg.append("path").datum(data).attr("d", line).attr("fill", "none").attr("stroke", palette.gray300).attr("stroke-width", 2);
    const avg = svg.append("path").datum(smooth).attr("d", line).attr("fill", "none").attr("stroke", palette.blue).attr("stroke-width", 3.3);
    drawPath(noisy, .05, .8);
    drawPath(avg, .35, 1);
    const dots = svg.append("g").selectAll("circle").data(data.filter((_, i) => i % 3 === 0)).join("circle")
      .attr("cx", d => x(d.t)).attr("cy", d => y(d.y)).attr("fill", palette.orange).attr("stroke", "#fff");
    grow(dots, "r", 1, 4, .18, .45);
  }
```

## d3-variable-color-line

### Variable Color Line

- **Pattern ID:** `d3-variable-color-line`
- **Gallery source ID:** `variable-color-line`
- **Family:** Encoding
- **Use when:** Line segments change color as a thresholded value changes.
- **Renderer:** `renderVariableColorLine`

#### Reuse Contract

- Use this file as the pattern source in isolated skill-only workspaces; read the gallery fixture only when maintaining that fixture.
- Keep data deterministic and inline small datasets.
- Preserve the pattern's core geometry and semantic color roles before changing labels or domain data.
- Use SVG-native animation for standalone output; do not leave runtime D3 or CDN dependencies in a self-contained deliverable.
- Include an SVG `<title>`, `<desc>`, stable `viewBox`, and final-state geometry.

#### Source Excerpt

The excerpt below is the compact renderer source for this pattern. If it references helpers such as `prepareSvg`, `fadeIn`, `grow`, `drawPath`, `palette`, `ramps`, `axisBottom`, or `axisLeft`, read `references/shared-renderer-helpers.md` and recreate only the needed helper behavior in the final artifact.

```js
function renderVariableColorLine() {
    const svg = prepareSvg("variable-color-line", "Variable color line", "A line changes segment color when values cross thresholds.");
    const data = d3.range(24).map(i => ({ t: i, y: 48 + Math.sin(i / 2) * 18 + Math.cos(i * .85) * 8 + i * .7 }));
    const margin = { top: 34, right: 34, bottom: 48, left: 54 };
    const x = d3.scaleLinear().domain(d3.extent(data, d => d.t)).range([margin.left, width - margin.right]);
    const y = d3.scaleLinear().domain([25, 90]).range([height - margin.bottom, margin.top]);
    axisBottom(svg, x, height - margin.bottom, 5);
    axisLeft(svg, y, margin.left, 4);
    const threshold = 58;
    svg.append("line").attr("x1", margin.left).attr("x2", width - margin.right).attr("y1", y(threshold)).attr("y2", y(threshold)).attr("stroke", palette.gray600).attr("stroke-dasharray", "4 5");
    const segments = d3.pairs(data);
    const line = d3.line().x(d => x(d.t)).y(d => y(d.y)).curve(d3.curveMonotoneX);
    const paths = svg.append("g").selectAll("path").data(segments).join("path")
      .attr("d", d => line(d))
      .attr("fill", "none")
      .attr("stroke", d => d3.mean(d, p => p.y) >= threshold ? palette.red : palette.blue)
      .attr("stroke-width", 3)
      .attr("stroke-linecap", "round");
    drawPath(paths, .03, .55);
    svg.append("text").attr("class", "mark-label").attr("x", width - 38).attr("y", y(threshold) - 8).attr("text-anchor", "end").text("threshold");
  }
```
