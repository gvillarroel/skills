# XY colorset pattern recipes

Use these patterns when the requested result resembles a published example.
Select `colorset1` or `colorset2` using [colorsets.md](colorsets.md); keep the
same data, domains and category identities when comparing styles.

The published set is
[reflex-xy-colorsets](https://gvillarroel.github.io/skills/examples/reflex-xy-colorsets/).
Each mechanism has two canonical IDs, formed by appending `-cs1` or `-cs2`
to the base ID below. The gallery exposes them as card IDs and
`data-pattern-id` values. Normal authoring uses this compact recipe rather
than reading or copying the acceptance gallery.

| Base pattern ID | Trigger and input contract | Implementation |
| --- | --- | --- |
| `reflex-xy-category-scatter` | Compare named cohorts with aligned numeric x/y columns | Allocate a stable cohort-to-color map. Build one opaque `xy.scatter` per cohort; preserve original rows and use different symbols as a second cue when helpful. Add labeled axes and a styled legend. |
| `reflex-xy-trend-lines` | Compare ordered measurements across several series | Build one `xy.line` per series with a constant canonical color. Use named series, stable dash patterns and a shared domain. Retain missing observations as gaps; inspect native and browser output. |
| `reflex-xy-grouped-bars` | Compare several measures within the same categories | Use `xy.bar(categories, series_matrix, series=names, colors=colors, opacity=1)`. Rows of the matrix represent named series. Use a zero baseline and preserve group order; style the legend explicitly. |
| `reflex-xy-histogram` | Show the distribution of a numeric sample | Use documented `xy.hist` options or compute fixed shared edges/counts for native bars. Preserve raw samples in source. Use one opaque canonical fill and an explicitly labeled canonical median/reference line. |
| `reflex-xy-heatmap` | Compare cells in a numeric row-by-column matrix with exact palette paints | Compute `binned_colors` over the original values with a fixed domain. Draw data-unit rectangles with `xy.bar(x, height, base=y-height/2, width=cell_width)`, one constant-color mark per bin, so cells resize with the chart. Label original values when space permits and explain thresholds in the legend; avoid an interpolating native heatmap for exact bins. |
| `reflex-xy-dense-scatter` | Inspect structure in many individual observations | Use small opaque marks with `density=False` when exact category paint is essential and the dataset is manageable. Keep domains stable across palettes. For much larger data, apply the live/density guidance and disclose aggregate/averaged colors rather than pretending every source point is drawn. |

## Common construction

Import the portable helper as shown in the colorset reference. Add
`theme(selected)` as a chart child, `xy.legend(style=legend_style(selected))`
for native-compatible legend paint, and `custom_css=css(selected)` to HTML
export. Set filled marks to `opacity=1` and zero decorative stroke width.
Use `text_on(fill)` for text inside a filled region; allow axes and meaningful
line work to retain their geometry. Prefer shared numeric domains and a stable
category order before styling.

The matrix pattern intentionally uses direct rectangles: XY 0.0.8 interpolates
its public numeric colormap even with exact endpoint colors. Retain each
unrounded measurement in the input/source; visible rounded labels and color
bins are presentation encodings. Do not promise arbitrary extra tooltip fields
that the installed renderer has not retained.

Fixed-pixel square scatter markers can overlap on a narrow responsive matrix;
use data-unit rectangles or deliberately scroll a chart with a readable minimum
width. Place legends outside the cell region and check the smallest viewport.

## Recreate and verify

For a compact editable chart, execute the runtime starter with either selector:

```sh
uv run --script <skill-dir>/assets/templates/chart.py --colorset colorset1 --output-dir results/cs1
uv run --script <skill-dir>/assets/templates/chart.py --colorset colorset2 --output-dir results/cs2
```

When copying the starter to another folder, copy `xy_colorsets.py` and
`colorsets.json` beside it, or pass
`--colorset-helper <skill-dir>/scripts/xy_colorsets.py`. Keep generated output
outside the skill. For a source-only project, retain the copied palette resource
with the helper so the project remains independent of this bundle.

Run the bundled browser verifier against each HTML and inspect its screenshot.
Parse native SVG paint attributes and compare authored fills/strokes/text against
the selected palette. Check tooltips, modebar focus/hover and selection chrome,
not just initial marks. Compare categories, numeric values, gaps and axes between
variants. Test the final responsive viewport and inspect small cell labels at
their delivered size. Alpha and antialiasing are derived pixels, not permission
to introduce arbitrary authored base colors.

If maintaining the published fixture itself, run its `build.py --output-dir`
command in a workspace, inspect all twelve results and preserve the stable IDs.
The fixture is an acceptance source and is not required for ordinary chart work.
