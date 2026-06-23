# Boxplot Charts In Slidev

- **Data shape:** Use precomputed five-number summaries `[min, q1, median, q3, max]` by category.
- **Animation pattern:** Update the five-number arrays across `$clicks`; keep y-axis scale fixed for fair comparison.
- **Display guidance:** Use boxplots when the distribution summary matters more than individual points. Add points only when outliers are central to the story.
- **Modules:** Register `BoxplotChart`, `GridComponent`, and `TooltipComponent`.
- **Pitfalls:** ECharts can compute boxplots through transforms, but precomputed data is more deterministic for deck fixtures.
