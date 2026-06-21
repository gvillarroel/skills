# ECharts Chart-Type Index For Slidev

Use this index when the task names a chart type or when choosing a chart grammar for a Slidev data story. Load only the specific chart reference needed after reading the core workflow.

## Chart References

- `charts/line.md`: ordered trends and continuity.
- `charts/bar.md`: categorical magnitude and before-after ranking.
- `charts/pie.md`: small part-to-whole composition.
- `charts/scatter.md`: two-measure relationships and bubble encodings.
- `charts/radar.md`: compact multidimensional profiles.
- `charts/map.md`: region-based spatial comparison with local GeoJSON.
- `charts/tree.md`: parent-child hierarchy.
- `charts/treemap.md`: hierarchical area allocation.
- `charts/graph.md`: node-link topology.
- `charts/chord.md`: overlap or reciprocal flow among categories.
- `charts/gauge.md`: one headline ratio.
- `charts/funnel.md`: ordered stage attrition.
- `charts/parallel.md`: many-dimensional entity comparison.
- `charts/sankey.md`: directed volume flow.
- `charts/boxplot.md`: distribution summaries.
- `charts/candlestick.md`: open-high-low-close movement.
- `charts/effect-scatter.md`: pulsing priority points.
- `charts/lines.md`: animated route or connection lines.
- `charts/heatmap.md`: two-dimensional intensity grids.
- `charts/pictorial-bar.md`: repeated-symbol magnitude.
- `charts/theme-river.md`: topic or channel volume over time.
- `charts/sunburst.md`: radial hierarchical allocation.
- `charts/custom.md`: domain-specific marks with `renderItem`.

## Shared Example Fixture

The validation deck in `examples/slidev-echarts/` uses shared synthetic data files:

- `data/time-series.json` for line, bar, route context, and temporal examples.
- `data/categorical.json` for bar, pie, funnel, gauge, and pictorial bar.
- `data/distributions.json` for scatter, radar, parallel, boxplot, heatmap, effect scatter, and custom.
- `data/financial.json` for candlestick.
- `data/hierarchy.json` for tree, treemap, and sunburst.
- `data/relationships.json` for graph, chord, and sankey.
- `data/river.json` for theme river.
- `data/spatial.json` for map and lines.

Keep synthetic data deterministic. For animation tests, change values across Slidev clicks while preserving names, category order, and stable series IDs.
