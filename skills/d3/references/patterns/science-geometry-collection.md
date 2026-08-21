# Science and Geometry Pattern Collection

Use the pattern index to route directly to one section in this compact collection. Read only that section and any reference it explicitly names.

## d3-hr-diagram

### H-R Diagram

- **Pattern ID:** `d3-hr-diagram`
- **Gallery source ID:** `hr-diagram`
- **Family:** Science
- **Use when:** Stars map temperature and luminosity into a scientific scatter.
- **Renderer:** `renderHrDiagram`

#### Reuse Contract

- Use this file as the pattern source in isolated skill-only workspaces; read the gallery fixture only when maintaining that fixture.
- Keep data deterministic and inline small datasets.
- Preserve the pattern's core geometry and semantic color roles before changing labels or domain data.
- Use SVG-native animation for standalone output; do not leave runtime D3 or CDN dependencies in a self-contained deliverable.
- Include an SVG `<title>`, `<desc>`, stable `viewBox`, and final-state geometry.

#### Source Excerpt

The excerpt below is the compact renderer source for this pattern. If it references helpers such as `prepareSvg`, `fadeIn`, `grow`, `drawPath`, `palette`, `ramps`, `axisBottom`, or `axisLeft`, read `references/shared-renderer-helpers.md` and recreate only the needed helper behavior in the final artifact.

```js
function renderHrDiagram() {
    const svg = prepareSvg("hr-diagram", "Hertzsprung-Russell diagram", "Stars map temperature and luminosity into a scientific scatter.");
    const data = d3.range(140).map(i => {
      const hot = (i * 37) % 100;
      const temp = 3300 + hot * 72;
      const lum = Math.pow(10, -1.2 + ((i * 53) % 100) / 24 + Math.sin(i / 11) * .5);
      return { temp, lum, type: hot > 70 ? "hot" : hot < 26 ? "cool" : "main" };
    });
    const margin = { top: 46, right: 38, bottom: 58, left: 70 };
    const x = d3.scaleLinear().domain([10500, 3000]).range([margin.left, width - margin.right]);
    const y = d3.scaleLog().domain([.04, 1000]).range([height - margin.bottom, margin.top]);
    axisBottom(svg, x, height - margin.bottom, 5);
    axisLeft(svg, y, margin.left, 4);
    const dots = svg.append("g").selectAll("circle").data(data).join("circle")
      .attr("cx", d => x(d.temp)).attr("cy", d => y(d.lum)).attr("fill", d => d.type === "hot" ? "#cdf3ff" : d.type === "cool" ? "#ffe5cc" : "#fff4cc")
      .attr("stroke", d => d.type === "hot" ? palette.blue : d.type === "cool" ? palette.orange : palette.gold).attr("stroke-width", .8).attr("fill-opacity", .78);
    grow(dots, "r", 1, d => d.type === "main" ? 3.5 : 5.5, .02, .5);
  }
```

## d3-solar-path

### Solar Path

- **Pattern ID:** `d3-solar-path`
- **Gallery source ID:** `solar-path`
- **Family:** Astronomy
- **Use when:** Seasonal sun arcs cross a local horizon diagram.
- **Renderer:** `renderSolarPath`

#### Reuse Contract

- Use this file as the pattern source in isolated skill-only workspaces; read the gallery fixture only when maintaining that fixture.
- Keep data deterministic and inline small datasets.
- Preserve the pattern's core geometry and semantic color roles before changing labels or domain data.
- Use SVG-native animation for standalone output; do not leave runtime D3 or CDN dependencies in a self-contained deliverable.
- Include an SVG `<title>`, `<desc>`, stable `viewBox`, and final-state geometry.

#### Source Excerpt

The excerpt below is the compact renderer source for this pattern. If it references helpers such as `prepareSvg`, `fadeIn`, `grow`, `drawPath`, `palette`, `ramps`, `axisBottom`, or `axisLeft`, read `references/shared-renderer-helpers.md` and recreate only the needed helper behavior in the final artifact.

```js
function renderSolarPath() {
    const svg = prepareSvg("solar-path", "Solar path", "Seasonal sun arcs cross a local horizon diagram.");
    const cx = width / 2, horizon = 326;
    svg.append("line").attr("x1", 54).attr("x2", width - 54).attr("y1", horizon).attr("y2", horizon).attr("stroke", palette.ink).attr("stroke-width", 2);
    const seasons = [
      { name: "winter", h: 82, c: palette.blue },
      { name: "equinox", h: 142, c: palette.green },
      { name: "summer", h: 206, c: palette.orange }
    ];
    const paths = svg.append("g").selectAll("path").data(seasons).join("path")
      .attr("d", d => `M78,${horizon}Q${cx},${horizon - d.h} ${width - 78},${horizon}`)
      .attr("fill", "none").attr("stroke", d => d.c).attr("stroke-width", 3).attr("stroke-linecap", "round");
    drawPath(paths, .08, .95);
    seasons.forEach((s, i) => svg.append("text").attr("class", "mark-label").attr("fill", s.c).attr("x", width - 66).attr("y", horizon - s.h * .48 + i * 2).attr("text-anchor", "end").text(s.name));
    const sun = svg.append("circle").attr("r", 9).attr("fill", palette.gold).attr("stroke", palette.yellowHover).attr("stroke-width", 2);
    sun.append("animateMotion").attr("dur", "3s").attr("repeatCount", "indefinite")
      .append("mpath").attr("href", "#solar-path-motion");
    svg.append("path").attr("id", "solar-path-motion").attr("d", `M78,${horizon}Q${cx},${horizon - 206} ${width - 78},${horizon}`).attr("fill", "none").attr("stroke", "none");
  }
```

## d3-parabolic-arcs

### Parabolic Arcs

- **Pattern ID:** `d3-parabolic-arcs`
- **Gallery source ID:** `parabolic-arcs`
- **Family:** Geometry
- **Use when:** Curved trajectories connect ordered endpoints with height encoding.
- **Renderer:** `renderParabolicArcs`

#### Reuse Contract

- Use this file as the pattern source in isolated skill-only workspaces; read the gallery fixture only when maintaining that fixture.
- Keep data deterministic and inline small datasets.
- Preserve the pattern's core geometry and semantic color roles before changing labels or domain data.
- Use SVG-native animation for standalone output; do not leave runtime D3 or CDN dependencies in a self-contained deliverable.
- Include an SVG `<title>`, `<desc>`, stable `viewBox`, and final-state geometry.

#### Source Excerpt

The excerpt below is the compact renderer source for this pattern. If it references helpers such as `prepareSvg`, `fadeIn`, `grow`, `drawPath`, `palette`, `ramps`, `axisBottom`, or `axisLeft`, read `references/shared-renderer-helpers.md` and recreate only the needed helper behavior in the final artifact.

```js
function renderParabolicArcs() {
    const svg = prepareSvg("parabolic-arcs", "Parabolic arcs", "Curved trajectories connect endpoints with arc height encoding.");
    const baseline = 326;
    const x = d3.scalePoint().domain(d3.range(8)).range([70, width - 70]);
    const arcs = [
      { a: 0, b: 5, v: 92, c: palette.blue },
      { a: 1, b: 7, v: 126, c: palette.red },
      { a: 2, b: 4, v: 66, c: palette.green },
      { a: 3, b: 6, v: 104, c: palette.orange },
      { a: 0, b: 2, v: 48, c: palette.purple },
      { a: 5, b: 7, v: 58, c: palette.gold }
    ];
    svg.append("line").attr("x1", 52).attr("x2", width - 52).attr("y1", baseline).attr("y2", baseline).attr("stroke", palette.gray300).attr("stroke-width", 2);
    const paths = svg.append("g").attr("fill", "none").selectAll("path").data(arcs).join("path")
      .attr("d", d => {
        const x0 = x(d.a), x1 = x(d.b), xm = (x0 + x1) / 2;
        return `M${x0},${baseline}Q${xm},${baseline - d.v} ${x1},${baseline}`;
      })
      .attr("stroke", d => d.c).attr("stroke-width", d => 1.8 + d.v / 45).attr("stroke-linecap", "round").attr("opacity", .9);
    drawPath(paths, .08, 1.05);
    const endpoints = d3.range(8).map(i => ({ i, x: x(i) }));
    const dots = svg.append("g").selectAll("circle").data(endpoints).join("circle")
      .attr("cx", d => d.x).attr("cy", baseline).attr("fill", palette.ink).attr("stroke", "#fff").attr("stroke-width", 1.5);
    grow(dots, "r", 2, 7, .1, .55);
  }
```

## d3-apollonius-circles

### Apollonius Circles

- **Pattern ID:** `d3-apollonius-circles`
- **Gallery source ID:** `apollonius-circles`
- **Family:** Geometry
- **Use when:** Circle solutions reveal tangent constraints between anchors.
- **Renderer:** `renderApolloniusCircles`

#### Reuse Contract

- Use this file as the pattern source in isolated skill-only workspaces; read the gallery fixture only when maintaining that fixture.
- Keep data deterministic and inline small datasets.
- Preserve the pattern's core geometry and semantic color roles before changing labels or domain data.
- Use SVG-native animation for standalone output; do not leave runtime D3 or CDN dependencies in a self-contained deliverable.
- Include an SVG `<title>`, `<desc>`, stable `viewBox`, and final-state geometry.

#### Source Excerpt

The excerpt below is the compact renderer source for this pattern. If it references helpers such as `prepareSvg`, `fadeIn`, `grow`, `drawPath`, `palette`, `ramps`, `axisBottom`, or `axisLeft`, read `references/shared-renderer-helpers.md` and recreate only the needed helper behavior in the final artifact.

```js
function renderApolloniusCircles() {
    const svg = prepareSvg("apollonius-circles", "Apollonius circles", "Circle solutions reveal tangent constraints between anchors.");
    const anchors = [
      { x: 188, y: 166, r: 42, c: palette.blue },
      { x: 322, y: 164, r: 34, c: palette.orange },
      { x: 260, y: 276, r: 38, c: palette.green }
    ];
    const solutions = [
      { x: 260, y: 198, r: 98, c: palette.purple },
      { x: 242, y: 211, r: 63, c: palette.red },
      { x: 300, y: 226, r: 54, c: palette.cyan }
    ];
    svg.append("g").selectAll("circle").data(anchors).join("circle")
      .attr("cx", d => d.x).attr("cy", d => d.y).attr("r", d => d.r)
      .attr("fill", d => d.c).attr("fill-opacity", .14).attr("stroke", d => d.c).attr("stroke-width", 2.2);
    const solution = svg.append("g").selectAll("circle").data(solutions).join("circle")
      .attr("cx", d => d.x).attr("cy", d => d.y).attr("fill", "none").attr("stroke", d => d.c).attr("stroke-width", 2.4).attr("stroke-dasharray", "7 5");
    grow(solution, "r", 5, d => d.r, .1, .9);
    const points = svg.append("g").selectAll("circle.point").data(anchors).join("circle")
      .attr("class", "point").attr("cx", d => d.x).attr("cy", d => d.y).attr("fill", d => d.c).attr("stroke", "#fff").attr("stroke-width", 2);
    grow(points, "r", 2, 7, .14, .45);
  }
```

## d3-tissot-indicatrix

### Tissot Indicatrix

- **Pattern ID:** `d3-tissot-indicatrix`
- **Gallery source ID:** `tissot-indicatrix`
- **Family:** Projection
- **Use when:** Equal angular circles reveal distortion across a map.
- **Renderer:** `renderTissotIndicatrix`

#### Reuse Contract

- Use this file as the pattern source in isolated skill-only workspaces; read the gallery fixture only when maintaining that fixture.
- Keep data deterministic and inline small datasets.
- Preserve the pattern's core geometry and semantic color roles before changing labels or domain data.
- Use SVG-native animation for standalone output; do not leave runtime D3 or CDN dependencies in a self-contained deliverable.
- Include an SVG `<title>`, `<desc>`, stable `viewBox`, and final-state geometry.

#### Source Excerpt

The excerpt below is the compact renderer source for this pattern. If it references helpers such as `prepareSvg`, `fadeIn`, `grow`, `drawPath`, `palette`, `ramps`, `axisBottom`, or `axisLeft`, read `references/shared-renderer-helpers.md` and recreate only the needed helper behavior in the final artifact.

```js
function renderTissotIndicatrix() {
    const svg = prepareSvg("tissot-indicatrix", "Tissot indicatrix", "Equal angular circles reveal projection distortion across the map.");
    const projection = d3.geoNaturalEarth1().fitExtent([[44, 48], [516, 340]], { type: "Sphere" });
    const path = d3.geoPath(projection);
    svg.append("path").datum({ type: "Sphere" }).attr("d", path).attr("fill", palette.gray50).attr("stroke", palette.gray200);
    svg.append("g").selectAll("path").data(d3.geoGraticule().step([30, 30]).lines()).join("path").attr("d", path).attr("fill", "none").attr("stroke", palette.gray100).attr("stroke-width", .8);
    const circles = [];
    [-120, -60, 0, 60, 120].forEach(lon => [-50, 0, 50].forEach(lat => circles.push(d3.geoCircle().center([lon, lat]).radius(8)())));
    const marks = svg.append("g").selectAll("path").data(circles).join("path")
      .attr("d", path).attr("fill", palette.orangeHighlight).attr("fill-opacity", .45).attr("stroke", palette.orange).attr("stroke-width", 2);
    fadeIn(marks, .06, .55);
  }
```

## d3-vector-field

### Vector Field

- **Pattern ID:** `d3-vector-field`
- **Gallery source ID:** `vector-field`
- **Family:** Field
- **Use when:** Direction and magnitude are encoded as small arrows.
- **Renderer:** `renderVectorField`

#### Reuse Contract

- Use this file as the pattern source in isolated skill-only workspaces; read the gallery fixture only when maintaining that fixture.
- Keep data deterministic and inline small datasets.
- Preserve the pattern's core geometry and semantic color roles before changing labels or domain data.
- Use SVG-native animation for standalone output; do not leave runtime D3 or CDN dependencies in a self-contained deliverable.
- Include an SVG `<title>`, `<desc>`, stable `viewBox`, and final-state geometry.

#### Source Excerpt

The excerpt below is the compact renderer source for this pattern. If it references helpers such as `prepareSvg`, `fadeIn`, `grow`, `drawPath`, `palette`, `ramps`, `axisBottom`, or `axisLeft`, read `references/shared-renderer-helpers.md` and recreate only the needed helper behavior in the final artifact.

```js
function renderVectorField() {
    const svg = prepareSvg("vector-field", "Vector field", "Direction and magnitude are encoded with small arrows on a grid.");
    const x = d3.scaleLinear().domain([0, 6]).range([78, width - 70]);
    const y = d3.scaleLinear().domain([0, 4]).range([320, 78]);
    const data = d3.range(7).flatMap(i => d3.range(5).map(j => {
      const angle = Math.sin(i * .8) + Math.cos(j * .9);
      const mag = .55 + Math.abs(Math.sin(i + j * .7)) * .45;
      return { i, j, angle, mag };
    }));
    const color = quantizedRamp([.55, 1], [palette.gold, palette.orange, palette.red]);
    d3.range(7).forEach(i => svg.append("line").attr("x1", x(i)).attr("x2", x(i)).attr("y1", y(0)).attr("y2", y(4)).attr("stroke", palette.gray100));
    d3.range(5).forEach(j => svg.append("line").attr("x1", x(0)).attr("x2", x(6)).attr("y1", y(j)).attr("y2", y(j)).attr("stroke", palette.gray100));
    const arrows = svg.append("g").selectAll("g").data(data).join("g").attr("transform", d => `translate(${x(d.i)},${y(d.j)}) rotate(${d.angle * 48})`);
    arrows.append("line").attr("x1", -11).attr("x2", d => 18 * d.mag).attr("y1", 0).attr("y2", 0).attr("stroke", d => color(d.mag)).attr("stroke-width", 2.6).attr("stroke-linecap", "round");
    arrows.append("path").attr("d", d3.symbol().type(d3.symbolTriangle).size(42)).attr("transform", d => `translate(${18 * d.mag},0) rotate(90)`).attr("fill", d => color(d.mag));
    fadeIn(arrows, .025, .55);
  }
```

## d3-curve-contexts

### Context to Curve

- **Pattern ID:** `d3-curve-contexts`
- **Gallery source ID:** `curve-contexts`
- **Family:** Geometry
- **Use when:** The same control points render through multiple D3 curve contexts.
- **Renderer:** `renderContextToCurve`

#### Reuse Contract

- Use this file as the pattern source in isolated skill-only workspaces; read the gallery fixture only when maintaining that fixture.
- Keep data deterministic and inline small datasets.
- Preserve the pattern's core geometry and semantic color roles before changing labels or domain data.
- Use SVG-native animation for standalone output; do not leave runtime D3 or CDN dependencies in a self-contained deliverable.
- Include an SVG `<title>`, `<desc>`, stable `viewBox`, and final-state geometry.

#### Source Excerpt

The excerpt below is the compact renderer source for this pattern. If it references helpers such as `prepareSvg`, `fadeIn`, `grow`, `drawPath`, `palette`, `ramps`, `axisBottom`, or `axisLeft`, read `references/shared-renderer-helpers.md` and recreate only the needed helper behavior in the final artifact.

```js
function renderContextToCurve() {
    const svg = prepareSvg("curve-contexts", "Context to curve", "The same control points render through multiple D3 curve contexts.");
    const points = [[62, 304], [132, 112], [208, 216], [288, 82], [372, 244], [488, 126]];
    const curves = [
      { name: "linear", curve: d3.curveLinear, y: 0, c: palette.gray600 },
      { name: "basis", curve: d3.curveBasis, y: 16, c: palette.blue },
      { name: "step", curve: d3.curveStep, y: 32, c: palette.red }
    ];
    curves.forEach((item, i) => {
      const shifted = points.map(p => [p[0], p[1] + item.y]);
      const path = svg.append("path").datum(shifted).attr("d", d3.line().curve(item.curve)).attr("fill", "none").attr("stroke", item.c).attr("stroke-width", i === 0 ? 2 : 3).attr("stroke-opacity", i === 0 ? .55 : .9);
      drawPath(path, .08 + i * .08, .85);
    });
    const legend = svg.append("g").attr("transform", "translate(88,32)");
    const legendItem = legend.selectAll("g").data(curves).join("g").attr("transform", (_, i) => `translate(${i * 126},0)`);
    legendItem.append("line").attr("x1", 0).attr("x2", 26).attr("y1", 0).attr("y2", 0).attr("stroke", d => d.c).attr("stroke-width", 3);
    legendItem.append("text").attr("class", "caption").attr("x", 34).attr("y", 4).text(d => d.name);
    svg.append("g").selectAll("circle").data(points).join("circle").attr("cx", d => d[0]).attr("cy", d => d[1]).attr("r", 4).attr("fill", palette.ink);
  }
```

## d3-adaptive-sampling

### Adaptive Sampling

- **Pattern ID:** `d3-adaptive-sampling`
- **Gallery source ID:** `adaptive-sampling`
- **Family:** Geometry
- **Use when:** More sample points appear where a curve bends sharply.
- **Renderer:** `renderAdaptiveSampling`

#### Reuse Contract

- Use this file as the pattern source in isolated skill-only workspaces; read the gallery fixture only when maintaining that fixture.
- Keep data deterministic and inline small datasets.
- Preserve the pattern's core geometry and semantic color roles before changing labels or domain data.
- Use SVG-native animation for standalone output; do not leave runtime D3 or CDN dependencies in a self-contained deliverable.
- Include an SVG `<title>`, `<desc>`, stable `viewBox`, and final-state geometry.

#### Source Excerpt

The excerpt below is the compact renderer source for this pattern. If it references helpers such as `prepareSvg`, `fadeIn`, `grow`, `drawPath`, `palette`, `ramps`, `axisBottom`, or `axisLeft`, read `references/shared-renderer-helpers.md` and recreate only the needed helper behavior in the final artifact.

```js
function renderAdaptiveSampling() {
    const svg = prepareSvg("adaptive-sampling", "Adaptive sampling", "More sample points appear where a curve bends sharply.");
    const f = x => 210 + Math.sin(x / 34) * 74 + Math.sin(x / 12) * 18;
    const coarse = d3.range(62, 500, 44).map(x => [x, f(x)]);
    const dense = d3.range(62, 500, 14).map(x => [x, f(x)]);
    const line = d3.line().curve(d3.curveCatmullRom);
    svg.append("path").datum(coarse).attr("d", line).attr("fill", "none").attr("stroke", palette.gray600).attr("stroke-width", 2).attr("stroke-dasharray", "6 5");
    const sampled = svg.append("path").datum(dense).attr("d", line).attr("fill", "none").attr("stroke", palette.orange).attr("stroke-width", 3);
    drawPath(sampled, .08, .9);
    const points = svg.append("g").selectAll("circle").data(dense).join("circle").attr("cx", d => d[0]).attr("cy", d => d[1]).attr("fill", palette.red).attr("fill-opacity", .82).attr("stroke", "#fff").attr("stroke-width", 1);
    grow(points, "r", 1.5, 3.5, .12, .45);
  }
```

## d3-satellite-projection

### Satellite Projection

- **Pattern ID:** `d3-satellite-projection`
- **Gallery source ID:** `satellite-projection`
- **Family:** Projection
- **Use when:** Perspective footprint and horizon rings explain a satellite view.
- **Renderer:** `renderSatelliteProjection`

#### Reuse Contract

- Use this file as the pattern source in isolated skill-only workspaces; read the gallery fixture only when maintaining that fixture.
- Keep data deterministic and inline small datasets.
- Preserve the pattern's core geometry and semantic color roles before changing labels or domain data.
- Use SVG-native animation for standalone output; do not leave runtime D3 or CDN dependencies in a self-contained deliverable.
- Include an SVG `<title>`, `<desc>`, stable `viewBox`, and final-state geometry.

#### Source Excerpt

The excerpt below is the compact renderer source for this pattern. If it references helpers such as `prepareSvg`, `fadeIn`, `grow`, `drawPath`, `palette`, `ramps`, `axisBottom`, or `axisLeft`, read `references/shared-renderer-helpers.md` and recreate only the needed helper behavior in the final artifact.

```js
function renderSatelliteProjection() {
    const svg = prepareSvg("satellite-projection", "Satellite projection", "Perspective footprint and horizon rings explain a satellite view.");
    const cx = width / 2, cy = height / 2 + 8;
    const rings = [
      { r: 154, c: palette.blueHighlight, stroke: palette.blue, label: "horizon" },
      { r: 108, c: palette.orangeHighlight, stroke: palette.orange, label: "scan" },
      { r: 58, c: palette.greenHighlight, stroke: palette.green, label: "nadir" }
    ];
    rings.forEach((ring, i) => {
      const circle = svg.append("circle").attr("cx", cx).attr("cy", cy).attr("fill", ring.c).attr("fill-opacity", .34).attr("stroke", ring.stroke).attr("stroke-width", 2);
      grow(circle, "r", 4, ring.r, .08 + i * .08, .55);
      svg.append("text").attr("class", "mark-label").attr("x", cx + ring.r * .7).attr("y", cy - ring.r * .58).text(ring.label);
    });
    const beam = svg.append("path").attr("d", `M${cx},${cy - 186}L${cx - 58},${cy - 58}L${cx + 58},${cy - 58}Z`).attr("fill", palette.redHighlight).attr("fill-opacity", .36).attr("stroke", palette.red).attr("stroke-width", 2);
    fadeIn(beam, .2, .55);
    svg.append("circle").attr("cx", cx).attr("cy", cy - 186).attr("r", 8).attr("fill", palette.red).attr("stroke", "#fff").attr("stroke-width", 2);
  }
```

## d3-exoplanet-orbits

### Exoplanet Orbits

- **Pattern ID:** `d3-exoplanet-orbits`
- **Gallery source ID:** `exoplanet-orbits`
- **Family:** Science
- **Use when:** Orbital radius and planet size encode a compact science catalog.
- **Renderer:** `renderExoplanetOrbits`

#### Reuse Contract

- Use this file as the pattern source in isolated skill-only workspaces; read the gallery fixture only when maintaining that fixture.
- Keep data deterministic and inline small datasets.
- Preserve the pattern's core geometry and semantic color roles before changing labels or domain data.
- Use SVG-native animation for standalone output; do not leave runtime D3 or CDN dependencies in a self-contained deliverable.
- Include an SVG `<title>`, `<desc>`, stable `viewBox`, and final-state geometry.

#### Source Excerpt

The excerpt below is the compact renderer source for this pattern. If it references helpers such as `prepareSvg`, `fadeIn`, `grow`, `drawPath`, `palette`, `ramps`, `axisBottom`, or `axisLeft`, read `references/shared-renderer-helpers.md` and recreate only the needed helper behavior in the final artifact.

```js
function renderExoplanetOrbits() {
    const svg = prepareSvg("exoplanet-orbits", "Exoplanet orbits", "Orbital radius and planet size encode a compact science catalog.");
    const systems = [
      { name: "Kepler-1", x: 120, planets: [22, 46, 76] },
      { name: "TRAPPIST", x: 280, planets: [18, 30, 42, 58, 74, 94] },
      { name: "HD 403", x: 436, planets: [28, 54, 104] }
    ];
    systems.forEach((system, si) => {
      const cy = height / 2 + 10;
      svg.append("circle").attr("cx", system.x).attr("cy", cy).attr("r", 8).attr("fill", palette.gold).attr("stroke", "#fff").attr("stroke-width", 2);
      const systemColor = [palette.blue, palette.purple, palette.green][si];
      const orbits = svg.append("g").selectAll("circle.orbit").data(system.planets).join("circle")
        .attr("class", "orbit").attr("cx", system.x).attr("cy", cy).attr("fill", "none").attr("stroke", palette.gray300).attr("stroke-opacity", .72).attr("stroke-width", 1.2);
      grow(orbits, "r", 4, d => d, .06 + si * .04, .5);
      const planets = svg.append("g").selectAll("circle.planet").data(system.planets).join("circle")
        .attr("class", "planet").attr("cx", d => system.x + d).attr("cy", (d, i) => cy + Math.sin(i * 1.7) * 8)
        .attr("fill", systemColor).attr("fill-opacity", .88).attr("stroke", "#fff").attr("stroke-width", 1.3);
      grow(planets, "r", 2, (d, i) => 4 + (i % 3) * 1.8, .12 + si * .04, .45);
      svg.append("text").attr("class", "mark-label").attr("x", system.x).attr("y", 348).attr("text-anchor", "middle").text(system.name);
    });
  }
```

## d3-epicyclic-gearing

### Epicyclic Gearing

- **Pattern ID:** `d3-epicyclic-gearing`
- **Gallery source ID:** `epicyclic-gearing`
- **Family:** Geometry
- **Use when:** Nested circular motion traces gear-like paths.
- **Renderer:** `renderEpicyclicGearing`

#### Reuse Contract

- Use this file as the pattern source in isolated skill-only workspaces; read the gallery fixture only when maintaining that fixture.
- Keep data deterministic and inline small datasets.
- Preserve the pattern's core geometry and semantic color roles before changing labels or domain data.
- Use SVG-native animation for standalone output; do not leave runtime D3 or CDN dependencies in a self-contained deliverable.
- Include an SVG `<title>`, `<desc>`, stable `viewBox`, and final-state geometry.

#### Source Excerpt

The excerpt below is the compact renderer source for this pattern. If it references helpers such as `prepareSvg`, `fadeIn`, `grow`, `drawPath`, `palette`, `ramps`, `axisBottom`, or `axisLeft`, read `references/shared-renderer-helpers.md` and recreate only the needed helper behavior in the final artifact.

```js
function renderEpicyclicGearing() {
    const svg = prepareSvg("epicyclic-gearing", "Epicyclic gearing", "Nested circular motion traces a gear-like parametric path.");
    const cx = width / 2, cy = height / 2 + 4;
    const R = 100, r = 34, d = 58;
    svg.attr("data-curve-family", "epitrochoid").attr("data-safe-frame", "true");
    const points = d3.range(0, Math.PI * 2.01, .045).map(t => [
      cx + (R + r) * Math.cos(t) - d * Math.cos(((R + r) / r) * t),
      cy + (R + r) * Math.sin(t) - d * Math.sin(((R + r) / r) * t)
    ]);
    svg.append("circle").attr("cx", cx).attr("cy", cy).attr("r", R).attr("fill", "none").attr("stroke", palette.gray200).attr("stroke-width", 2);
    svg.append("circle").attr("cx", cx + R + r).attr("cy", cy).attr("r", r).attr("fill", palette.gray50).attr("stroke", palette.blue).attr("stroke-width", 2);
    const line = d3.line().curve(d3.curveCatmullRomClosed);
    const path = svg.append("path").attr("id", "epicyclic-gearing-path").attr("d", line(points)).attr("fill", "none").attr("stroke", palette.orange).attr("stroke-width", 2.6).attr("stroke-opacity", .86);
    drawPath(path, .1, 1.2);
    const dot = svg.append("circle").attr("r", 6).attr("fill", palette.red).attr("stroke", "#fff").attr("stroke-width", 2.2);
    dot.append("animateMotion").attr("dur", "3.4s").attr("repeatCount", "indefinite").append("mpath").attr("href", "#epicyclic-gearing-path");
    svg.append("text").attr("class", "mark-label").attr("x", cx).attr("y", 30).attr("text-anchor", "middle").text("epitrochoid path");
  }
```
