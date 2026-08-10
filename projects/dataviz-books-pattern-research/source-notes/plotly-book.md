# Interactive Web-Based Data Visualization with R, plotly, and shiny

Status: processed

Local source: `artifacts/books/sources/plotly-book/`

Official source: https://plotly-r.com/

## Evidence Inspected

- `creating-overview.Rmd:174-195` describes figure structure as traces plus layout, with per-trace mappings and interactive properties.
- `creating-overview.Rmd:237` demonstrates interaction for comparing categories through legend filtering.
- `creating-overview.Rmd:325-327` emphasizes hover, zoom, filter, and linked views.
- `arranging.Rmd:261-342` covers interactive layouts, sorting, filtering, and linked summaries.
- `figure-refs.Rmd:270-397` covers metadata keys, graphical queries, filtering, and responsive crossfiltering.
- `linked-views.Rmd:109-267` covers overview first, details on demand, linked query behavior, highlight versus filter semantics, and stable query variables.
- `linked-views-examples.Rmd:5-227` covers linked panels, shared groups, selection layers, statistical trace comparability, and map/histogram/table linking.

## Assimilated Guidance

- Define one shared query state for multi-view interactions.
- Use stable row or group keys so every linked view resolves selections in the same namespace.
- Distinguish highlight, filter, compare, detail, persistent selection, and clear-state behavior.
- Keep a meaningful baseline view before interaction; avoid empty panels that only make sense after a brush.
- Keep summary parameters comparable across selection layers unless recomputation is labeled.

## Pattern Targets

- `skills/d3/references/pattern-selection-contracts.md`: Linked View Query Contract, Uncertainty And Model Contract.
- `pattern-opportunities.md`: Linked Brushing Dashboard and Publishable Accessibility Contract.

## Copyright And Use Boundary

Use only generic interaction contracts and independent implementations. Do not copy book prose, examples, or datasets into skills.
