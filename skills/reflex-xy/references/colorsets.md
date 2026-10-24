# Canonical colorset1 and colorset2

## Contents

- [Allocate exact category colors](#allocate-exact-category-colors)
- [Theme browser chrome and native exports together](#theme-browser-chrome-and-native-exports-together)
- [Quantitative colors without changing the source data](#quantitative-colors-without-changing-the-source-data)
- [Validate the portable helper](#validate-the-portable-helper)

Use `colorset1` by default. Select `colorset2` when the user requests it or when
several series need the red, blue, orange, green, purple, and yellow roles.
Honor an explicit source-style or user palette request. The exact contract is
bundled in [colorsets.json](../assets/palettes/colorsets.json); do not require a
repository-level file or a sibling skill.

## Allocate exact category colors

Import the bundled [xy_colorsets.py](../scripts/xy_colorsets.py) through its
directory. For an editable portable deliverable, copy that module and
`colorsets.json` beside the generated source; the module supports this layout.

```python
import sys
from pathlib import Path

sys.path.insert(0, str(Path("<skill-dir>") / "scripts"))
from xy_colorsets import categorical_colors, css, legend_style, load_palette, text_on, theme
import xy

selected = "colorset1"  # Change only this selector to use colorset2.
labels = ["North", "South", "East"]
colors = categorical_colors(selected, len(labels))
category_map = dict(zip(labels, colors))
chart = xy.scatter_chart(
    xy.scatter([1, 2, 3], [4, 7, 5], color=labels,
               size=12, opacity=1, stroke_width=0),
    theme(selected, palette=category_map),
    xy.x_axis(label="Input (units)"), xy.y_axis(label="Output (units)"),
    xy.legend(title="Region", loc="lower right", style=legend_style(selected)), title="Regional observations",
    width=800, height=440,
)
chart.to_html("chart.html", custom_css=css(selected))
chart.write_image("chart.svg")
```

Use the same category map across all panels, marks, legends, and filtered views.
An incomplete `xy.theme(palette={...})` map falls back to upstream colors for
unknown categories, so allocate every category before building. Multiple line
series use constant `color=colors[index]` and preserve meaningful line geometry.
Use `xy.legend(style=legend_style(selected))` for a borderless transparent legend
that inherits the chart canvas, with exact black text. XY's native legend
otherwise adds a `#cccccc` frame that chart-wide theme tokens do not override;
its native border-width override is not honored in 0.0.8. For a different canvas,
pass the same `background` hex to `legend_style(selected, background=...)` so
its black/white text retains maximum contrast.

XY legends occupy the plot area; they do not reserve an outside margin. Choose
an explicit empty location and inspect it against every point in both exports.
For a rising series with a high rightmost observation, the default upper-right
legend can hide the endpoint: start with `loc="lower right"` or add a justified
domain margin, then verify actual bounds. Exact palette paint is not a visual
pass when a legend obscures data.

For a Cartesian footer legend with up to three short series names, use
`xy.legend(loc="upper left", anchor=(0, -.18), ncols=3,
style=legend_style(selected))` with chart `height=480` and
`padding=(44, 28, 112, 64)` (top, right, bottom, left). The negative normalized
y anchor places the legend below the plot; explicit bottom padding reserves
space for it after the x-axis title. This preserves data and domains. XY does
not reserve that space automatically, and increasing top padding also moves
the title. Adapt the anchor/padding for different dimensions, labels or fonts.
Validate native SVG/PNG and actual HTML at desktop and 390px mobile sizes:
keep the legend below both data and axis title and wholly inside the canvas.

`categorical_colors(name, count=None, background=None)` returns the canonical
solid sequence after excluding the actual canvas. Its default canvas is
`#f7f7f7`; supply the same `background` to both it and `theme` when changing the
canvas. Colorset1 allocates primary red, interleaved dark/light grays, white,
then the remaining reds/pink. Colorset2 uses its base, dark, bright, neutral,
and soft sequence. Counts beyond usable capacity raise a clear error. Only
after using every usable solid should the design add explicit border-color,
dash, width, or symbol variants; document their category meaning.

Use `opacity=1` and `stroke_width=0` on ordinary filled marks. XY's defaults
include translucent scatter/bar fills, which blend into new colors. Preserve
semantic axes, connector paths, uncertainty limits, and explicit user styling.
For text inside a mark, use `text_on(fill)` to select the higher WCAG contrast
of black or white. Text laid on the chart canvas follows the same rule.

## Theme browser chrome and native exports together

`theme(name, background=None, *, style=None, **overrides)` returns a public
`xy.Theme`; it sets the figure/plot background, grid, axis, text, crosshair,
selection, tooltip, legend, badges, modebar, focus, and accent tokens. The
series palette is the complete usable solid sequence. Explicit caller tokens,
`style`, and `palette` overrides win, including source styles.

Use `css(name)` for standalone HTML and Chromium exports. It supplies remaining
DOM chrome variables and removes tooltip/control shadows instead of retaining
upstream slate/violet or translucent defaults. For example:

```python
chart.write_image("browser.png", engine=xy.Engine.chromium,
                  custom_css=css(selected))
```

Native SVG/PNG renderers ignore custom CSS; chart-wide theme, mark, and axis
properties carry their paint contract. Inspect at least one native export and
one actual HTML rendering. Check hover/focus controls and tooltip colors as
well as the initial view. Browser antialiasing, compositing, and optional density
aggregation may produce derivative pixels; distinguish these from off-palette
authored paints. Density aggregation can average distinct category colors;
use a nonaggregated view when exact per-category paint is essential.

## Quantitative colors without changing the source data

`binned_colors(values, name="colorset1", bins=4, domain=None)` maps numeric
values into two to four equal-width exact sequential palette colors. Keep the
original values for coordinates, tooltips, and data downloads. An explicit
finite increasing `domain=(low, high)` stabilizes thresholds across panels;
out-of-domain values clamp to endpoint bins. NaN/infinity return `None` so the
caller can omit missing geometry. An inferred constant domain uses the middle
bin. The helper never changes the caller's values.

For exact authored paints, create one constant-color mark per bin, or use bin
labels with a complete explicit `xy.theme(palette={label: color})` mapping.
Explain the thresholds in a discrete legend. Use data-unit rectangles for a
responsive matrix; fixed-pixel square scatter markers can overlap on narrow
screens. Preserve the original cell values in source. XY 0.0.8 recognizes
unambiguous `#hex`, `rgb(...)` and `hsl(...)` color arrays as direct per-point
paints; bare color words can be categorical labels and need a matching palette
mapping. Confirm the chosen mark's channel contract before binding these arrays.

`sequential_colors(name)` returns four exact stops for an optional continuous
numeric ramp: neutral-to-red for colorset1, pale-to-dark blue for colorset2.
XY 0.0.8 resamples/interpolates `colormap=` through its 256-entry renderer LUT.
Even a list containing only canonical stops therefore produces intermediate
colors in heatmaps, numeric scatter, colorbars, and density surfaces. Use that
API only when continuous interpolation is explicitly appropriate and disclose
this derivative-color behavior; it does not meet an exact discrete-paint
requirement. Do not relabel a gradient as exact palette bins.

## Validate the portable helper

```sh
uv run --script <skill-dir>/scripts/test_xy_colorsets.py --output-dir artifacts/xy-colorset-tests
```

The tests cover name/range validation, category capacity, canvas exclusion,
black/white contrast, numeric missing values and thresholds, genuine public
theme construction, native SVG paints, offline browser canvas paint, and actual
tooltip/modebar hover/focus styles. Inspect the generated screenshots. A local
Edge, Chrome, or Playwright Chromium is required for browser verification.
