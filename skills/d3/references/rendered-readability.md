# Rendered readability

Set the chart's hierarchy and data mapping before placing labels. Keep the plot area large enough to see the data, with separate bands for the title, axes, legends, and direct labels where they need room. Keep data labels, axis ticks, and unit labels at least 12 effective CSS pixels at the target size. Use the active palette's exact color tokens and choose text paint with at least 4.5:1 contrast against the actual fill for ordinary small text. Preserve data or state distinctions with text or geometry.

For near-colliding direct labels, reserve a right-hand gutter before scaling the plot. Project endpoint positions through the actual y scale. Sort labels by projected y, walk the sorted list enforcing a minimum gap of one line height plus breathing room, and walk it backward if the last label exceeds the gutter. Use thin leader segments from actual endpoints to displaced labels. Keep endpoint coordinates tied to the data and preserve gaps for missing samples. Use the same check on the smallest intended viewport.

For a zero-based category line chart, use `scripts/build_direct_line.py`. Write a local JSON file first and pass its path to `--data PATH`. Supply 2–18 ordered categories and 1–5 series. Each series has a stable `id`, a visible `label`, and a nonnegative number or `null` for each category. The builder uses genuine offline D3, leaves gaps for missing values, and measures the direct-label gutter.

```json
{"categories":["Week 1","Week 2","Week 3"],"series":[{"id":"checkout","label":"Checkout","values":[20,null,11]}]}
```

```text
uv run --script <d3-skill>/scripts/build_direct_line.py --data data.json --id incident-series --title "Incident detection" --description "The Checkout line has a gap where there was no sample." --unit "Minutes" --width 640 --height 320 --output chart.html
```

```text
uv run --script <d3-skill>/scripts/render_d3_svg.py chart.html --viewport 640x320 --wait-ms 0 --output settled.svg --screenshot preview.png --layout-report labels.json --strict-layout --min-label-px 12
```

The report measures rendered text in CSS pixels, including scale transforms, and lists viewport clipping, undersized text, and significant collisions between label boxes. During layout iteration, use `--layout-report` to collect measurements. Resolve its findings before adding `--strict-layout` to the final export. Use a smaller threshold only when the design has a justified secondary tier. For intentional text layering, put a specific reason on the affected text with `data-d3-layout-overlap`; it still receives size and viewport checks. Compare the PNG with the SVG and inspect glyph readability and contrast separately. The boxes can overstate overlap for rotated or multirun text, and do not measure line-to-label collisions.

Keep replay and exploration controls outside the art where possible. Mark presentation-only controls with `data-d3-export-ignore`. The HTML remains interactive, while the portable SVG omits those nodes and the inspection PNG hides marked overlays without reflow. When an SVG carries deliberate surrounding workspace or a legend needs to be excluded from a slide, mark the intended frame on the SVG root with `data-d3-export-frame="x y width height"` in SVG user coordinates. Verify the full visual and the chosen frame. Consumers may use this metadata when fitting the SVG to a presentation.

For display lettering that depends on a specific heavy font or rendering effect, mark its top-level paint unit with `data-d3-export-raster` and a reason. The portable SVG retains its text and the Slides exporter can preserve its appearance as an isolated image while keeping adjacent geometry editable.
