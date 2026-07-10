# Source Processing Status

This tracker records which downloaded or mirrored book sources have been reviewed and assimilated into current reusable pattern guidance.

`processed` means the source was inspected locally, useful non-derivative guidance was summarized in `source-notes/`, and the reusable guidance was folded into `.agents/skills/d3-animated-svg/references/pattern-selection-contracts.md` or recorded as a future pattern opportunity.

| Source | Status | Local evidence | Assimilation target |
| --- | --- | --- | --- |
| Hands-On Data Visualization | processed | `source-notes/hands-on-data-visualization.md` | Chart purpose gate, map fit, publication metadata, interactive fallback. |
| ggplot Wizardry | processed | `source-notes/ggplot-wizardry.md` | Annotation finish, margin and clipping validation, layout polish, half-eye usage. |
| Beyond Bar and Box Plots | processed | `source-notes/beyond-bar-and-box-plots.md` | Distribution alternatives, raw/summary combinations, interval semantics. |
| ggplot2: Elegant Graphics for Data Analysis | processed | `source-notes/ggplot2-book.md` | Visual grammar contract, stat transforms, weights, annotations, facets. |
| Data Visualization: A Practical Introduction | processed | `source-notes/socviz.md` | Audience and purpose framing, reproducible chart selection, captions. |
| Interactive Web-Based Data Visualization with R, plotly, and shiny | processed | `source-notes/plotly-book.md` | Linked view query contract, highlight/filter/compare semantics, stable keys. |
| Fundamentals of Data Visualization | processed | `source-notes/wilke-dataviz.md` | Scale ambiguity, proportional ink, data/context balance, uncertainty, accessibility. |
| R Graphics Cookbook | processed | `source-notes/r-graphics-cookbook.md` | Overplotting ladder, bin/density semantics, channel precision, export format. |

## Current Assimilation

The first runtime promotion is `.agents/skills/d3-animated-svg/references/pattern-selection-contracts.md`. It now includes:

- Chart purpose selection before picking a chart family.
- Explicit visual grammar fields for mappings, transforms, scales, ordering, interaction, and accessibility.
- Distribution, uncertainty, overplotting, scale, linked-view, map, publication, and annotation validation contracts.

Future fixture work should use `pattern-opportunities.md` as the backlog for concrete examples and validators.
