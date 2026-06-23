# Custom Charts In Slidev

- **Data shape:** Define tuples around the geometry you need, then document the dimensions with `encode`. For ranges, use `[categoryIndex, start, end, value]`.
- **Animation pattern:** Keep `renderItem` deterministic and update encoded dimensions across `$clicks`. ECharts can animate the resulting shapes when identities stay stable.
- **Display guidance:** Use custom series only when built-in charts cannot express the mark. Keep the rendered shape simple enough to inspect in screenshots.
- **Modules:** Register `CustomChart`, `GridComponent`, and any components used by the coordinate system.
- **Pitfalls:** Complex render functions are harder to debug in decks; start with rectangles, lines, or symbols before building bespoke shapes.
