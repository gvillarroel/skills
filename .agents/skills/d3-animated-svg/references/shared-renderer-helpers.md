# Shared Renderer Helpers

Use this reference only when a per-pattern file under `references/patterns/` includes helper names from the gallery fixture. Recreate the minimal behavior locally; do not read the gallery source for normal pattern generation.

## Default Geometry And Tokens

Most gallery excerpts assume these small constants:

```js
const width = 560;
const height = 420;
const palette = {
  blue: "#007298",
  orange: "#e77204",
  green: "#45842a",
  red: "#9e1b32",
  purple: "#652f6c",
  cyan: "#00ace6",
  gold: "#f1c319",
  ink: "#333e48",
  muted: "#696969",
  gray50: "#f7f7f7",
  gray100: "#e7e7e7",
  gray200: "#cfcfcf",
  gray300: "#b5b5b5",
  gray400: "#9c9c9c",
  gray500: "#828282",
  gray600: "#696969",
  gray700: "#4f4f4f",
  gray800: "#363636",
  gray900: "#1c1c1c",
  blueHover: "#004d66",
  orangeHover: "#994a00",
  greenHover: "#294d19",
  purpleHover: "#431f47",
  redHover: "#6d1222",
  blueHighlight: "#cdf3ff",
  orangeHighlight: "#ffe5cc",
  yellowHighlight: "#fff4cc",
  greenHighlight: "#dbffcc",
  purpleHighlight: "#f9ccff",
  redHighlight: "#ffccd5",
  surface: "#ffffff",
  line: "#cfcfcf"
};
const colors = [palette.blue, palette.orange, palette.green, palette.purple, palette.red];
const ramps = {
  blue: [palette.blueHighlight, palette.cyan, palette.blue, palette.blueHover],
  heat: [palette.yellowHighlight, palette.orangeHighlight, palette.orange, palette.red],
  terrain: [palette.yellowHighlight, palette.greenHighlight, palette.blueHighlight, palette.blue, palette.purple],
  gray: [palette.gray100, palette.gray200, palette.gray300, palette.gray400, palette.gray700]
};
```

For repository-owned artifacts, prefer the full token guidance in `references/visual-tokens.md` when choosing new semantic colors.

## Minimal Helpers

Use these helpers as compact equivalents when converting a pattern excerpt into a standalone artifact:

```js
function prepareSvg(id, title, desc) {
  const svg = d3.select("svg")
    .attr("id", id)
    .attr("data-pattern-id", `d3-pattern-${id}`)
    .attr("role", "img")
    .attr("viewBox", `0 0 ${width} ${height}`)
    .attr("width", width)
    .attr("height", height);
  svg.selectAll("*").remove();
  svg.append("title").text(title);
  svg.append("desc").text(desc);
  svg.append("rect")
    .attr("width", width)
    .attr("height", height)
    .attr("rx", 16)
    .attr("fill", palette.surface);
  return svg;
}

function fadeIn(selection, delay = 0, dur = 0.7) {
  selection.attr("opacity", 1)
    .append("animate")
    .attr("attributeName", "opacity")
    .attr("from", 0)
    .attr("to", 1)
    .attr("dur", `${dur}s`)
    .attr("begin", `${delay}s`)
    .attr("fill", "freeze");
}

function grow(selection, attr, from, to, delay = 0, dur = 0.7) {
  selection.attr(attr, to)
    .append("animate")
    .attr("attributeName", attr)
    .attr("from", from)
    .attr("to", to)
    .attr("dur", `${dur}s`)
    .attr("begin", `${delay}s`)
    .attr("fill", "freeze");
}

function drawPath(selection, delay = 0, dur = 1.1) {
  selection.each(function () {
    const length = this.getTotalLength();
    d3.select(this)
      .attr("stroke-dasharray", `${length} ${length}`)
      .attr("stroke-dashoffset", 0)
      .append("animate")
      .attr("attributeName", "stroke-dashoffset")
      .attr("from", length)
      .attr("to", 0)
      .attr("dur", `${dur}s`)
      .attr("begin", `${delay}s`)
      .attr("fill", "freeze");
  });
}

function axisBottom(svg, scale, y, ticks = 5) {
  return svg.append("g")
    .attr("class", "axis")
    .attr("transform", `translate(0,${y})`)
    .call(d3.axisBottom(scale).ticks(ticks));
}

function axisLeft(svg, scale, x, ticks = 5) {
  return svg.append("g")
    .attr("class", "axis")
    .attr("transform", `translate(${x},0)`)
    .call(d3.axisLeft(scale).ticks(ticks));
}
```

## Standalone Conversion Rules

- Inline the required helpers into the generated HTML or SVG; do not leave references to shared gallery state.
- If the final artifact must be self-contained, use static SVG geometry and SVG-native animation. Do not depend on CDN D3 or runtime JavaScript.
- Keep the excerpt's deterministic layout choices, such as seeded force simulations and fixed viewBox dimensions.
- Replace gallery-specific CSS classes with local styles when needed, especially for `.mark-label`, `.axis`, grid lines, and label halos.
