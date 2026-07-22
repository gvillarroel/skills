# ggplot2: Elegant Graphics for Data Analysis

Status: processed

Local source: `artifacts/books/sources/ggplot2-book/`

Official source: https://ggplot2-book.org/

## Evidence Inspected

- `annotations.qmd:14` frames annotations as layers that use the same visual grammar as plotted data.
- `annotations.qmd:48-49` covers rich text support in theme elements.
- `annotations.qmd:79-147` covers text aesthetics and the need to use them with restraint.
- `annotations.qmd:186-220` covers overlap avoidance for labels.
- `annotations.qmd:239-267` covers text, rectangles, lines, and reference marks as annotation tools.
- `statistical-summaries.qmd:80-83` notes that weights can affect summaries without being directly visible.
- `statistical-summaries.qmd:141-263` covers distribution summaries, binning, boxplots, violins, and dot plots.
- `statistical-summaries.qmd:289-401` covers overplotting, binning, density, and stat transform outputs.
- `arranging-plots.qmd:11-145` covers facets, arranged plots, aligned panels, guide collection, and shared axes.

## Assimilated Guidance

- State the data fields, visual mappings, statistical transforms, scales, coordinates, facets, and annotation layers before coding.
- Declare weights because they change statistical results invisibly.
- Treat annotations and reference marks as semantic layers tied to data or layout coordinates.
- Use facets or arranged panels when shared scale comparison is more important than a single crowded view.
- Keep generated summaries traceable to the transform that produced them.

## Pattern Targets

- `skills/d3-animated-svg/references/pattern-selection-contracts.md`: Visualization Contract, Scale And Summary Semantics, Annotation And Finish.
- `pattern-opportunities.md`: Visual Grammar Contract and Overplotting Resolution Ladder.

## Copyright And Use Boundary

Use only generic grammar and validation concepts. Do not copy book prose, source examples, figures, or datasets into skills.
