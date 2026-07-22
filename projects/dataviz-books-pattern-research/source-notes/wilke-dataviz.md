# Fundamentals of Data Visualization

Status: processed

Local source: `artifacts/books/sources/wilke-dataviz/`

Official source: https://clauswilke.com/dataviz/

## Evidence Inspected

- `aesthetic_mapping.Rmd:14-22` describes mapping data values to position, shape, size, color, line width, and line type.
- `aesthetic_mapping.Rmd:137-141` notes that scales must map data to aesthetics without ambiguity.
- `balance_data_context.Rmd:12-24` covers balancing data ink and contextual information.
- `balance_data_context.Rmd:71-73` and `balance_data_context.Rmd:198-200` show that excessive context removal can make axes, legends, and reference anchors harder to read.
- `balance_data_context.Rmd:323-344` covers label placement and reference-line usefulness.
- `docs/proportional_ink.md:37-117` covers proportional ink and baseline expectations for bars and ratio/log displays.
- `docs/small_axis_labels.md:55-58` recommends checking scaled-down figures for label legibility.
- `_book_production/preface.md:20` favors reproducible figure generation over manual post-processing.

## Assimilated Guidance

- Map data to visual channels deliberately and avoid ambiguous scales.
- Balance context and data: remove clutter, but keep axes, references, and legends sufficient for decoding.
- Use proportional ink rules for bars and choose point encodings when a zero baseline is not meaningful.
- Validate scaled-down and mobile readability.
- Prefer reproducible rendering over manual figure edits.

## Pattern Targets

- `skills/d3-animated-svg/references/pattern-selection-contracts.md`: Visualization Contract, Scale And Summary Semantics, Publication Data Contract.
- `pattern-opportunities.md`: Visual Grammar Contract, Overplotting Resolution Ladder, Publishable Accessibility Contract.

## Copyright And Use Boundary

Use only high-level design and validation principles. Do not copy prose, figures, source examples, or datasets into skills.
