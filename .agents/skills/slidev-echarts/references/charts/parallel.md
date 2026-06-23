# Parallel Charts In Slidev

- **Data shape:** Use rows of normalized metrics. Define `parallelAxis` explicitly so dimensions remain understandable.
- **Animation pattern:** Update row values while keeping axis order and min/max fixed. Use moderate line opacity to reduce overplotting.
- **Display guidance:** Best for comparing several entities across many dimensions. Keep dimensions to four to seven on a slide.
- **Modules:** Register `ParallelChart`, `ParallelComponent`, and `TooltipComponent`.
- **Pitfalls:** Raw units on mixed axes mislead; normalize or clearly label every axis.
