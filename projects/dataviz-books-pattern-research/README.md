# Data Visualization Book Pattern Research

This project captures a local review of the data visualization books listed in Rosana Ferrero's X post:

- Source post: https://x.com/RosanaFerrero/status/2073010918707868006
- Tweet image saved locally: `artifacts/images/tweet-book-list.jpg`

The goal is to identify reusable, non-derivative pattern guidance for the current Codex skill pattern libraries. Downloaded books, cloned source repositories, HTML mirrors, and screenshots are local research artifacts under `artifacts/` and are intentionally kept out of git.

Processing status and source-by-source notes are tracked in `source-processing-status.md` and `source-notes/`.

## Downloaded And Mirrored Sources

| Title | Official source | Local artifact | Notes |
| --- | --- | --- | --- |
| Hands-On Data Visualization | https://handsondataviz.org/ | `artifacts/books/hands-on-data-visualization.pdf`; `artifacts/books/sources/handsondataviz-book/` | Official PDF and source repo. Book text is CC BY-NC-ND, so use only high-level ideas and original pattern contracts. |
| ggplot Wizardry | https://github.com/z3tt/outlierconf2021 | `artifacts/books/ggplot-wizardry-extended.pdf`; `artifacts/books/sources/ggplot-wizardry/` | Workshop materials by Cedric Scherer. License is CC BY-NC-SA 4.0 in the repo. Useful for annotation, half-eye, clipping, margin, and layout patterns. |
| Beyond Bar and Box Plots | https://github.com/z3tt/beyond-bar-and-box-plots | `artifacts/books/beyond-bar-and-box-plots.pdf`; `artifacts/books/sources/beyond-bar-and-box-plots/` | Workshop materials by Cedric Scherer. License is CC BY-NC-SA 4.0 in the repo. Useful for distribution alternatives and richer uncertainty summaries. |
| ggplot2: Elegant Graphics for Data Analysis | https://ggplot2-book.org/ | `artifacts/books/sources/ggplot2-book/` | Official online source. Useful for grammar-of-graphics structure: data, mapping, statistical transform, scale, coordinate system, facet, and theme. |
| Data Visualization: A Practical Introduction | https://socviz.co/ | `artifacts/books/html/socviz/` | Official HTML pages mirrored for local review. Use as conceptual support for practical chart selection and explanatory discipline. |
| Interactive Web-Based Data Visualization with R, plotly, and shiny | https://plotly-r.com/ | `artifacts/books/sources/plotly-book/` | Official online source and repo. License is CC BY-NC-ND 3.0 US. Useful for linked views, graphical queries, hover, filtering, and interaction state contracts. |
| Fundamentals of Data Visualization | https://clauswilke.com/dataviz/ | `artifacts/books/sources/wilke-dataviz/` | Official source repo. License notes identify CC BY-NC-ND; use only high-level ideas. Useful for aesthetic mappings, scale ambiguity, overplotting, uncertainty, and accessibility. |
| R Graphics Cookbook | https://r-graphics.org/ | `artifacts/books/sources/r-graphics-cookbook/` | Official online source repo. License was not confirmed in the quick local audit. Useful for practical implementation recipes such as overplotting strategies, facets, confidence regions, and dot plots. |

## Local Download Summary

The most directly downloadable PDFs from official sources were saved:

- `artifacts/books/hands-on-data-visualization.pdf`
- `artifacts/books/ggplot-wizardry-extended.pdf`
- `artifacts/books/beyond-bar-and-box-plots.pdf`

Official source repositories were cloned when that was the clearest legal and maintainable way to inspect the book:

- `artifacts/books/sources/handsondataviz-book/`
- `artifacts/books/sources/wilke-dataviz/`
- `artifacts/books/sources/plotly-book/`
- `artifacts/books/sources/r-graphics-cookbook/`
- `artifacts/books/sources/ggplot2-book/`
- `artifacts/books/sources/ggplot-wizardry/`
- `artifacts/books/sources/beyond-bar-and-box-plots/`

The `socviz.co` book was mirrored as official HTML pages instead of using third-party PDFs:

- `artifacts/books/html/socviz/`

## Use Boundary

Do not copy book prose, figures, datasets, or slides into skills. The useful work here is to extract generic reusable pattern contracts, validation checks, and original examples that can be implemented independently in the owning skill directories.

For current pattern work, use `source-processing-status.md` for processed-source status and `pattern-opportunities.md` as the distilled backlog.
