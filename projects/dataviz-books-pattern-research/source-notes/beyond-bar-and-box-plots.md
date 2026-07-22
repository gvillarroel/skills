# Beyond Bar and Box Plots

Status: processed

Local source: `artifacts/books/beyond-bar-and-box-plots.pdf`; `artifacts/books/sources/beyond-bar-and-box-plots/`

Official source: https://github.com/z3tt/beyond-bar-and-box-plots

## Evidence Inspected

- `README.md:31-33` points to the official slides, tutorial, and code.
- `BeyondBarAndBoxPlots.Rmd:34-37` lists distribution-focused packages used in the workshop.
- `BeyondBarAndBoxPlots.Rmd:100-160` contrasts bar and box summaries with distribution-revealing alternatives.
- `BeyondBarAndBoxPlots.Rmd:201-218` uses half-eye style summaries.
- `BeyondBarAndBoxPlots.Rmd:226-390` covers ridgelines, quantile/tail encodings, interval strips, and interval widths.
- `BeyondBarAndBoxPlots.Rmd:402-631` covers raw point, barcode, jitter, dot, beeswarm, box-plus-point, and violin-plus-point combinations.
- `BeyondBarAndBoxPlots.Rmd:651-704` combines raw data, density, summaries, and intervals in a raincloud-style composite.

## Assimilated Guidance

- Do not hide sample shape behind a bar or a box when the distribution shape or sample size matters.
- Prefer raw points, jitter, beeswarm, dot strips, violin, ridgeline, half-eye, or composites according to the task and density.
- Label interval width and interval meaning whenever uncertainty is drawn.
- Use composite distribution views when the task needs raw observations, density shape, summary statistics, and uncertainty together.
- Keep group comparisons on shared scales unless independent scales are explicitly labeled.

## Pattern Targets

- `skills/d3-animated-svg/references/pattern-selection-contracts.md`: Distribution Pattern Choice, Uncertainty And Model Contract.
- `pattern-opportunities.md`: Distribution Alternatives Composite and Layered Refinement Animation.

## Copyright And Use Boundary

Use only high-level distribution-selection knowledge and original D3 implementations. Do not copy figures, tutorial prose, or workshop layouts into skills.
