# R Graphics Cookbook

Status: processed

Local source: `artifacts/books/sources/r-graphics-cookbook/`

Official source: https://r-graphics.org/

## Evidence Inspected

- `ch05.Rmd:18` covers summarizing large data before display when raw points overplot.
- `ch05.Rmd:276-329` covers visual channel precision, outline/fill, transparency, area scaling, and avoiding confusing size and shape combinations.
- `ch05.Rmd:347-430` covers smaller or hollow points, transparency, binning, hexagons, and legend ranges.
- `ch05.Rmd:448-480` covers jitter and 2D density alternatives.
- `ch05.Rmd:505-591` covers confidence regions, fit lines, and combined jitter/opacity strategies.
- `ch05.Rmd:799-878` covers facets and simple annotation.
- `ch06.Rmd:780-852` covers 2D density, contours, tiles, bandwidth, and the difference between observed bins and estimated density.
- `ch14.Rmd:82` notes dense vector output can become large and slow.
- `ch15.Rmd:459-531` covers factor ordering for axes and legends.
- `ch15.Rmd:1213-1270` covers standard errors and confidence intervals with cautions.

## Assimilated Guidance

- Use an overplotting ladder: opacity, smaller/hollow marks, jitter, facets, rectangular bins, hex bins, density contours, and summaries.
- Declare whether binned color means count, rate, or density.
- Label density contours and smoothers as estimates, and validate bandwidth choices.
- Use x/y position for precision before size, area, or color when exact comparison matters.
- Treat factor, legend, and axis ordering as an explicit contract.
- Prefer bitmap layers for very dense marks when vector output becomes impractical, while keeping labels and axes crisp.

## Pattern Targets

- `.agents/skills/d3-animated-svg/references/pattern-selection-contracts.md`: Overplotting Ladder, Scale And Summary Semantics, Uncertainty And Model Contract.
- `pattern-opportunities.md`: Overplotting Resolution Ladder and Visual Grammar Contract.

## Copyright And Use Boundary

Use only practical pattern guidance and independent D3 examples. Do not copy cookbook prose, recipes, figures, or datasets into skills.
