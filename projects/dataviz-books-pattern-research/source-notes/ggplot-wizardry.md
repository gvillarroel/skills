# ggplot Wizardry

Status: processed

Local source: `artifacts/books/ggplot-wizardry-extended.pdf`; `artifacts/books/sources/ggplot-wizardry/`

Official source: https://github.com/z3tt/outlierconf2021

## Evidence Inspected

- `README.md:63-65` and `README.md:73` list the workshop package surface, including rich text, annotation, distribution, and layout helpers.
- `R/OutlierConf2021_ggplotWizardry_HandsOn.Rmd:117-120` covers markdown and HTML-style text rendering in plot text elements.
- `R/OutlierConf2021_ggplotWizardry_HandsOn.Rmd:183-265` uses rich text boxes and off-plot clipping control.
- `R/OutlierConf2021_ggplotWizardry_HandsOn.Rmd:281-357` uses geometric callout regions around marks.
- `R/OutlierConf2021_ggplotWizardry_HandsOn.Rmd:406-438` covers legend placement, clipping, and plot margin control.
- `R/OutlierConf2021_ggplotWizardry_HandsOn.Rmd:459-591` combines distribution summaries, multi-panel layout, and clipping comparisons.

## Assimilated Guidance

- Treat annotation, direct labels, and callout regions as designed layers with collision space, not as post-processing.
- Reserve margins for labels and callouts that sit outside the plotting area.
- Validate clipping behavior explicitly; accidental clipping is a chart failure.
- Use text boxes, label backplates, leader lines, and direct labels to reduce legend lookup when they improve scanning.
- Combine distribution summaries and layouts only when shared scales and interval semantics remain clear.

## Pattern Targets

- `skills/d3/references/pattern-selection-contracts.md`: Annotation And Finish, Distribution Pattern Choice.
- `pattern-opportunities.md`: Annotation And Direct Label Polish and Distribution Alternatives Composite.

## Copyright And Use Boundary

Use only generic implementation ideas and independently designed examples. Do not copy workshop slides, figures, layout designs, or source prose into skills.
