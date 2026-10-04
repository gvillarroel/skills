# Boxplot Charts In Slidev

Follow [native median contrast](../boxplot-median-contrast.md) for newly
authored filled boxplots. Pin ECharts 6.1.0 and call
`qualifyBoxplotMedians(chart, echarts, selected)` after native `setOption`,
then repeat after resize/click updates. Normalize delivered SVG paint. This
preserves the opaque borderless box and native five-number geometry while
giving the median independent black or white ink.

- **Data shape:** Use precomputed five-number summaries `[min, q1, median, q3, max]` by category.
- **Animation pattern:** Update the five-number arrays across `$clicks`; keep y-axis scale fixed for fair comparison.
- **Display guidance:** Use boxplots when the distribution summary matters more than individual points. Add points only when outliers are central to the story.
- **Modules:** Register `BoxplotChart`, `GridComponent`, and `TooltipComponent`.
- **Pitfalls:** ECharts can compute boxplots through transforms, but precomputed data is more deterministic for deck fixtures.
