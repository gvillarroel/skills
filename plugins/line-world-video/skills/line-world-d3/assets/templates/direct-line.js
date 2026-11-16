(() => {
  const spec = JSON.parse(document.getElementById("line-data").textContent);
  const {categories, series, emphasis, title, unit, width, height, palette} = spec;
  const svg = d3.select("svg[data-renderer='d3']");
  const measure = document.createElement("canvas").getContext("2d");
  const textWidth = (text, font) => {
    measure.font = font;
    return measure.measureText(text).width;
  };
  const maxValue = d3.max(series.flatMap(row => row.values)) || 1;
  const y = d3.scaleLinear().domain([0, maxValue]).nice(4);
  const ticks = y.ticks(4);
  const tickFormat = y.tickFormat(4);
  const left = Math.max(44, Math.ceil(d3.max(ticks, tick => textWidth(tickFormat(tick), "12px Arial"))) + 18);
  const right = width - Math.ceil(d3.max(series, row => textWidth(row.label, "700 13px Arial"))) - 44;
  const plotTop = 67;
  const x = d3.scalePoint().domain(categories).range([left, right]);
  const widestCategory = d3.max(categories, label => textWidth(label, "12px Arial"));
  const angle = widestCategory + 7 > x.step() ? -38 : 0;
  const bottom = height - (angle ? 22 + Math.ceil(widestCategory * 0.66) : 37);
  if (right - left < 140 || bottom - plotTop < 110) {
    throw new Error("Use a larger chart for these labels.");
  }
  y.range([bottom, plotTop]);

  svg.append("rect").attr("width", width).attr("height", height).attr("fill", palette.surface);
  const headingSize = Math.min(22, Math.max(12, Math.floor(22 * (width - 32) / textWidth(title, "700 22px Arial"))));
  svg.append("text").attr("x", 16).attr("y", 31).attr("fill", palette.ink_dark)
    .attr("font-weight", 700).attr("font-size", headingSize).text(title);
  svg.append("text").attr("x", 16).attr("y", 52).attr("fill", palette.ink)
    .attr("font-size", 12).text(unit);

  svg.append("g").attr("aria-hidden", "true").selectAll("line").data(ticks).join("line")
    .attr("x1", left).attr("x2", right).attr("y1", y).attr("y2", y)
    .attr("stroke", tick => tick === 0 ? palette.line : palette.quiet);
  const horizontal = svg.append("g").attr("transform", `translate(0,${bottom})`)
    .call(d3.axisBottom(x).tickSize(4).tickPadding(8).tickSizeOuter(0));
  const vertical = svg.append("g").attr("transform", `translate(${left},0)`)
    .call(d3.axisLeft(y).tickValues(ticks).tickFormat(tickFormat).tickSize(0).tickPadding(9));
  horizontal.select(".domain").attr("stroke", palette.line);
  horizontal.selectAll(".tick line").attr("stroke", palette.line);
  vertical.select(".domain").remove();
  for (const axis of [horizontal, vertical]) {
    axis.selectAll("text").attr("fill", palette.ink).attr("font-size", 12);
  }
  if (angle) horizontal.selectAll("text").attr("text-anchor", "end").attr("transform", `rotate(${angle})`);

  const rows = series.map((row, index) => {
    const points = categories.map((category, i) => ({category, value: row.values[i]}));
    const visible = points.filter(point => point.value !== null);
    const last = visible.at(-1);
    return {...row, points, visible, last, labelY: y(last.value), index};
  });
  const byY = rows.slice().sort((a, b) => a.labelY - b.labelY);
  const gap = 20;
  byY.forEach((row, i) => {
    row.labelY = Math.max(row.labelY, i ? byY[i-1].labelY + gap : plotTop);
  });
  for (let i = byY.length - 1; i >= 0; i--) {
    byY[i].labelY = Math.min(byY[i].labelY, i === byY.length - 1 ? bottom : byY[i+1].labelY - gap);
  }
  const groups = svg.selectAll("g.line-series").data(rows, row => row.id).join("g")
    .attr("class", "line-series").attr("id", row => row.id).attr("aria-label", row => row.label);
  const line = d3.line().defined(point => point.value !== null)
    .x(point => x(point.category)).y(point => y(point.value));
  const colors = [palette.ink, palette.blue || palette.primary_dark, palette.purple || palette.ink_dark, palette.green || palette.ink];
  const dashes = ["7 4", "2 4", "9 4 2 4", "12 4"];
  groups.each(function (row) {
    const group = d3.select(this);
    const selected = row.id === emphasis;
    const secondary = row.index - (rows.findIndex(item => item.id === emphasis) < row.index ? 1 : 0);
    const paint = selected ? palette.primary : colors[secondary];
    const dash = selected ? null : dashes[secondary];
    group.append("path").attr("class", "series-line").attr("d", line(row.points)).attr("fill", "none")
      .attr("stroke", paint).attr("stroke-width", selected ? 2.8 : 2.2)
      .attr("stroke-linecap", "round").attr("stroke-linejoin", "round").attr("stroke-dasharray", dash);
    group.selectAll("circle").data(row.visible).join("circle")
      .attr("cx", point => x(point.category)).attr("cy", point => y(point.value)).attr("r", selected ? 3.4 : 2.7)
      .attr("fill", selected ? paint : palette.surface).attr("stroke", paint).attr("stroke-width", 1.4);
    const endX = x(row.last.category), endY = y(row.last.value);
    group.append("polyline").attr("points", `${endX},${endY} ${right+5},${endY} ${right+19},${row.labelY}`)
      .attr("fill", "none").attr("stroke", paint).attr("stroke-width", 1.2).attr("stroke-dasharray", dash);
    group.append("text").attr("class", "direct-label").attr("x", right + 24).attr("y", row.labelY)
      .attr("dy", "0.35em").attr("font-size", 13).attr("font-weight", 700).attr("fill", palette.ink_dark)
      .text(row.label);
  });
})();
