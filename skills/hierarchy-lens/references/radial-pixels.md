# Radial pixel heatmap

**Pattern ID:** `hierarchy-radial-pixels`

- **Trigger:** A hierarchy should read as pixel art or a text-free heatmap whose colors form meaningful patterns across multiple views.
- **Input:** The flat tree and dimensions in [data-contract.md](data-contract.md).
- **Output:** One offline HTML with a native square-pixel canvas, outside controls, image-only mode, search, zoom, category highlighting, and text-free SVG/PNG exports.
- **Example set:** `hierarchy-lens`; [live example](https://gvillarroel.github.io/skills/examples/hierarchy-lens/#hierarchy-radial-pixels).

## Build and inspect

```text
uv run --script <skill-root>/scripts/build_explorer.py --input hierarchy.json --view pixel --pixel-grid 256 --output portrait.html --report build.json
uv run --script <skill-root>/scripts/audit_pixels.py portrait.html --report audit.json --screenshot portrait.png
```

Use `--demo --demo-size N` instead of `--input` for a synthetic organization of exactly N records, and add `--data-output hierarchy.json` to retain editable input. `--initial-lens KEY` chooses the opening color dimension. Otherwise pixel mode starts with the first numeric dimension, or the first categorical dimension when no numeric one exists.

`--pixel-grid` is the starting logical width/height: 64, 128, 256, 512, 1024, or 2048. Try 64 or 128 for a small, deliberately chunky composition; 256 is the normal starting point. The builder doubles the grid until every record owns at least one square pixel. Read the actual `grid` and `minPixelsPerRecord` in the build report. A fine grid is sometimes necessary to preserve small branches. If 2048 still omits a record, fail explicitly rather than publishing a lossy map. The 20000-record input bound is not a guarantee that every possible topology fits.

## Meaning and geometry

1. Assign each record a fixed angular span proportional to its subtree count. Children partition their parent's span, leaving the parent's own share unfilled in the next ring. Do not create duplicate manager leaves.
2. Divide the radius into equal bands by reporting depth. The center disk belongs to the root. Empty outer regions mean the branch ended, not missing attribute data.
3. Sample this partition on a square grid at cell centers. Each filled pixel belongs to exactly one record. Refine for complete record coverage, then freeze the ownership grid across all color changes. Keep source sibling order.
4. Treat the pixels as the material of a record's region, not as people. One region can contain many pixels. Angular span conveys branch headcount; area varies with ring radius and is not a cross-ring headcount scale.
5. Paint categorical values with fixed, full-dataset category colors. Paint numeric values with eight discrete color bands. The darkest numeric band represents observed zero; missing values use a gray checkerboard. No interpolation, blur, glow, dither, animation, or random noise adds apparent measurements.
6. Default numeric bands use global quantiles of positive observations, making skewed usage patterns visible. Six cut points divide positive values into seven bands; repeated values may make bands empty. Offer linear and log1p alternatives, label the choice and thresholds outside the image, and keep all thresholds stable under zoom, search, and selection.
7. Sum only exclusive individual measurements when `aggregation: sum`. Report known/total coverage in details. Do not reinterpret already-overlapping team totals as individual measurements.

The rendering is a native logical pixel map, not a postprocessed screenshot. Canvas enlargement and PNG export use nearest-neighbor sampling. SVG export uses axis-aligned integer rectangles with `shape-rendering="crispEdges"`. All labels, legends, units, provenance, and instructions stay outside the image. Hidden SVG metadata retains source identities, values, active dimension, thresholds, and encoding semantics.

## Interaction and validation

Keep color buttons visible below the image; `F` or the image-only button hides controls, while Escape restores them and resets the view. Keys 1–9 switch dimensions without showing text inside the image. Mouse wheel/pan and branch search magnify the existing grid rather than changing the layout. Search and previous/next record controls expose exact identities outside the canvas; arrow keys provide record traversal.

Inspect an overview, two contrasting lenses, a focused branch, and a mobile view. Check that a leadership lens can form depth-like bands when supported by the data, role concentrations form sectors, and numeric values reveal local variation. Judge whether the intended patterns are visible; a technically valid image may still need a coarser starting grid or a better declared numeric scale. Zoom reveals hard square pixels and exact regions without smoothing. All records remain in the map even when highlighting dims other branches.

The audit independently checks that each occupied cell belongs to its owner's depth/angle, all records have pixels, raster hit testing reaches the correct record, null differs from zero, thresholds match the numeric definitions, color changes preserve ownership, keyboard/search/fullscreen work, downloads contain no visible text, mobile controls fit, and no network or browser errors occur. Keep the normalized JSON with the HTML for source verification.

SVG and PNG exports show the complete map with current colors/highlighting, regardless of camera zoom. They are static, text-free views; exact legend/context remains in the HTML and SVG metadata. Never suggest that a bare PNG explains its scale by itself.
