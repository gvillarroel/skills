# Advanced Cartesian charts

Use verified XY 0.0.8 families alongside [chart recipes](chart-recipes.md)
and the [colorset workflow](colorsets.md). The [capability gallery](https://gvillarroel.github.io/skills/examples/reflex-xy-capabilities/)
is an optional visual reference; runtime work does not require its source files.

## Contents

- [Choose a family](#choose-a-family)
- [Set up a portable chart](#set-up-a-portable-chart)
- [Preserve geometry and distribution contracts](#preserve-geometry-and-distribution-contracts)
- [Draw uncertainty](#draw-uncertainty)
- [Draw fields and density](#draw-fields-and-density)
- [Draw flows and funnels](#draw-flows-and-funnels)
- [Verify the result](#verify-the-result)

## Choose a family

Use `xy.chart`
for mixed marks. Family factories use `<mark>_chart`; use `histogram_chart` for
`hist`/`histogram`, and `chart` for `ribbon`.

| Question / input | Public marks | Contract |
| --- | --- | --- |
| Relationships; aligned rows | `scatter` | Category/numeric color, size and symbol channels; density is an aggregate |
| Ordered trajectory | `line` | One constant color per series; preserve NaN gaps |
| Amount above a baseline | `area` | `y` is the upper endpoint; `base` is the lower boundary |
| Categories / series matrix | `bar` | `mode="grouped"`, `"stacked"`, or `"normalized"`; `y` is height above `base` |
| Vertical columns | `column` | Public aliases using the bar renderer |
| Samples / fixed bin edges | `hist` or `histogram` | Distinguish counts, density and cumulative mass |
| Change takes effect at a boundary | `step` | `where="pre"`, `"mid"`, or `"post"` |
| Precomputed interval values | `stairs` | N values require N+1 edges |
| Discrete impulses | `stem` | Baseline, endpoint marker and stroke have independent options |
| Cumulative sample distribution | `ecdf` | Input is samples; optional `bins` bounds resolution |
| Quartiles / outliers | `box` | Tukey boxes with separate median, whisker and outlier styles |
| Distribution shape | `violin` | Bounded-resolution density estimate; `bins` controls resolution |
| Supplied measurement uncertainty | `errorbar` | Nonnegative symmetric or lower/upper error magnitudes |
| Supplied interval boundaries | `error_band` | Aligned x/lower/upper arrays; no automatic confidence calculation |
| Rectangular scalar grid | `heatmap` | z has shape `(len(y), len(x))` for explicit centers |
| Dense spatial counts | `hexbin` | `gridsize`, `mincnt`, and a quantitative count scale |
| Regular-grid thresholds | `contour` | Explicit `levels`; optional `filled`, `dash_negative`, `corner_mask` |
| Independent endpoint pairs | `segments` | Each row supplies x0/y0/x1/y1 |
| Explicit triangles | `triangle_mesh` | Three vertices per row; constant or per-triangle color |
| Explicit face-to-face spans | `ribbon` inside `chart` | x0/x1 plus source and target lower/upper boundaries |
| Weighted node links | `sankey` | `(source, target, value)` triples; layout occurs in Python |
| Ordered conversion stages | `funnel` | Nonnegative stage counts; stage order is preserved |

There is no public
`hist_chart` or candlestick/OHLC factory in this release. Compose a documented
custom chart from `segments` and `bar` when needed; identify it as a composition.

## Set up a portable chart

Import the bundled helper as in [colorsets.md](colorsets.md). Copy it with its
JSON beside portable source; pin `xy==0.0.8` in the environment or uv metadata.

```python
import numpy as np
import xy
from xy_colorsets import categorical_colors, css, legend_style, sequential_colors, text_on, theme

selected = "colorset1"  # Use "colorset2" for the second canonical set.
colors = categorical_colors(selected, 4)
ink = colors[0] if selected == "colorset1" else colors[1]
legend = xy.legend(loc="lower right", style=legend_style(selected))
layout = dict(width="100%", height=480)
```

Keep complete category maps stable across views. For one measurement, red in
CS1 and blue in CS2 expose the style difference. `opacity=1` preserves exact
fill paints; default translucency creates additional composited colors. Export outside the
skill bundle with `chart.to_html(path, custom_css=css(selected))`; export native
images with explicit dimensions, for example `chart.to_svg(path, width=820,
height=480)`. CSS is browser-only; native output uses chart styles.

## Preserve geometry and distribution contracts

- Stack areas explicitly: draw `area(x, lower, base=0)`, then
  `area(x, lower+upper, base=lower)`. A bar instead draws `base + y` as its top.
- For grouped bars, supply a series-by-category matrix, matching `series` names,
  and matching `colors`. Use `orientation="horizontal"` without swapping the
  source category/value arrays. Normalized bars express shares, not raw totals.
- Keep histogram edges wide enough to include every intended observation.
  `density=True, cumulative=True` ends at one only when the bins cover the sample.
- Pass a one-dimensional sample with row-aligned `x` or `group` to boxes and
  violins; a single `x=[position]` does not match a multirow sample. A supported
  two-dimensional sample is column-oriented. Choose a clear orientation.
- Unambiguous hex/rgb/hsl arrays are direct paints. Bare color words can be
  category labels; numeric arrays invoke a colormap.

```python
sample = np.array([4.1, 4.8, 5.2, 5.7, 6.0, 7.8])
box = xy.box_chart(
    xy.box(sample, x=np.zeros(len(sample)), color=ink, opacity=1,
           show_outliers=True, style={"stroke-width": 0},
           whisker_style={"stroke": ink, "stroke-width": 1.5},
           median_style={"stroke": text_on(ink), "stroke-width": 2}),
    theme(selected), xy.legend(show=False), **layout,
)
```

Box-part styles use CSS `stroke` and `stroke-width`, not `color` or `width`.
Violin styling is fill-only. Its aligned group-position `x` also works with
`orientation="horizontal"`.

## Draw uncertainty

```python
x = np.arange(6, dtype=float)
mean = np.array([3, 4, 3.5, 6, 5, 7])
chart = xy.error_band_chart(
    xy.error_band(x, mean-.8, mean+1.2,
                  color=sequential_colors(selected)[0], opacity=1),
    xy.line(x, mean, color=ink, width=2),
    xy.x_axis(label="Observation"), xy.y_axis(label="Response (units)"),
    theme(selected), xy.legend(show=False), **layout,
)
```

For bars around observations, substitute
`xy.errorbar(x, mean, yerr=[np.full(6,.6), np.full(6,1.1)], xerr=.15,
color=ink, width=2, cap_size=.18)` and optional scatter markers. The two y-error
arrays are magnitudes below and above the observation, not absolute endpoints.
In XY 0.0.8, `cap_size` uses perpendicular data-axis units, despite the wrapper
docstring's pixel claim. Choose a small value relative to the plotted domain;
`width` still controls the stroke in pixels. Reserve clear space for a
transparent legend, such as a y-domain with headroom above stacked areas.

## Draw fields and density

```python
xs, ys = np.linspace(-2, 2, 32), np.linspace(-2, 2, 24)
gx, gy = np.meshgrid(xs, ys)
z = np.exp(-(gx**2 + gy**2))
field = xy.heatmap_chart(
    xy.heatmap(z, x=xs, y=ys, domain=(0,1),
               colormap=sequential_colors(selected), opacity=1),
    xy.colorbar(title="Magnitude"), theme(selected),
    xy.legend(show=False), **layout,
)
```

Use `xy.contour(z, x=xs, y=ys, levels=[.1,.3,.5,.7], color=colors,
width=2, opacity=1)` for exact-color isolines. Use `filled=True` and an explicit
`colormap` for interval surfaces. Negative isolines can use `dash_negative=True`;
`corner_mask=True` preserves valid triangles near missing grid corners.

For point inputs, use `xy.hexbin(x, y, gridsize=22, mincnt=1,
colormap=sequential_colors(selected), opacity=1)` with a count colorbar, or
`xy.scatter(x, y, color=ink, density=True)` for native density aggregation.
Ramps, colorbars and density derive intermediate shades or alpha. Canonical
stops do not imply exact discrete paints. Declare this boundary, or use exact
bins and constant-color marks. Heatmap/density SVGs can contain raster layers.

## Draw flows and funnels

```python
flow = xy.sankey_chart(
    [("Input","Lab",12), ("Input","Field",8),
     ("Lab","Output",12), ("Field","Output",8)],
    theme(selected, annotation_text="#ffffff"), xy.legend(show=False),
    nodes=["Input","Lab","Field","Output"],
    colors=[colors[i % 2] for i in range(4)],
    link_opacity=1, navigation=False, **layout,
)
```

Sankey labels use the theme's `annotation_text` without per-node contrast.
Keep every label over a dark node/ribbon and use canonical white text, as
above; inspect both native and HTML exports. Node names preserve identity
when dark colors repeat. Sankey interpolates node colors even at full opacity.
For an exact flat ribbon use
`xy.ribbon([0],[2],[0],[1],[1],[2], color=ink, opacity=1)` inside `xy.chart`;
omit `color_target`. The arrays describe x faces and their lower/upper spans.
Disable navigation on fixed diagrams to prevent zoom cropping their labels;
hover tooltips can remain available.

```python
funnel = xy.funnel_chart(
    xy.funnel(["Visits","Leads","Trials","Paid"], [1200,780,420,210],
              colors=colors, geometry="bar", orientation="horizontal",
              opacity=1, show_values=True, show_conversion=True,
              show_dropoff=True),
    theme(selected), xy.legend(show=False), navigation=False, **layout,
)
```

`geometry="area"` gives the classic taper; its painted area is not proportional
to the count. `geometry="bar"` uses proportional centered widths. XY 0.0.8
automatically paints inside funnel labels with `#f7f8fa` or `#1f2430`; those
renderer-owned contrast colors bypass the theme. Document these exact exceptions
when retaining native labels. They do not excuse off-palette authored stage fills
or unrelated chrome. For strict black/white text, disable native labels and build
an explicitly labeled composition using `text_on(fill)`.

## Verify the result

Execute final source, parse native output, and inspect desktop/mobile browser
renders. Confirm arrays, names, gaps, bin coverage and interval meaning. Native
legends occupy plot space; choose an empty location. Distinguish initial clipping
from intentional zoom cropping. Check the requested host and interactions; a
snapshot does not prove live callbacks. Use [outputs-and-validation.md](outputs-and-validation.md)
for the offline verifier and export boundaries. These are representative verified
patterns, not every parameter combination.
