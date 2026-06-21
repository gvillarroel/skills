# Lines Charts In Slidev

- **Data shape:** Use route objects with `coords: [[x1, y1], [x2, y2]]` and optional value.
- **Animation pattern:** Start with static lines, then enable `effect.show` and update line width by route value. Cartesian coordinates are enough for a local validation fixture.
- **Display guidance:** Use lines for origin-destination or connection movement. Pair with scatter points when endpoints need context.
- **Modules:** Register `LinesChart`, `ScatterChart`, `GridComponent`, and `TooltipComponent`.
- **Pitfalls:** Geo-based lines require registered maps or geo coordinates; use cartesian routes when spatial accuracy is not the point.
