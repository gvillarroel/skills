# Compact organic cells

**Pattern ID:** `hierarchy-organic-pixels`

- **Trigger:** A radial pixel image has a bulky center, thick bands, thin needles, excessive diameter, or should grow as one compact slime-like body.
- **Input:** The same flat hierarchy and dimensions in [data-contract.md](data-contract.md).
- **Output:** An offline interactive HTML with one equal square per record, a connected seeded outline, stable color lenses, outside controls, and native-size text-free PNG/SVG exports.
- **Example set:** `hierarchy-lens`; [live example](https://gvillarroel.github.io/skills/examples/hierarchy-lens/#hierarchy-organic-pixels).

## Build

```text
uv run --script <skill-root>/scripts/build_explorer.py --input hierarchy.json --view organic --cell-pixels 2 --seed 73021 --output compact.html --report build.json
uv run --script <skill-root>/scripts/audit_pixels.py compact.html --report audit.json --screenshot compact.png
```

For a fictional organization of exactly N people, use `--demo --demo-size N` instead of `--input` and add `--data-output hierarchy.json`. Keep outputs outside the bundle. Normal runtime use needs this reference and the input contract, not template or generator source.

`--cell-pixels` is an integer from 1 to 4. Default 2 means each record, including the root and every manager, owns exactly four logical pixels. Use 1 for a minimal native image; 3 or 4 increases all cells equally. The grid is calculated from the packed body's bounds and has a power-of-two side. It does not depend on metric values. `--seed` controls the reproducible packing contour; `--initial-lens KEY` chooses the opening colors.

The initial display enlarges native pixels 3× while keeping the image compact. The outside key offers 1×, 2×, 3×, 4×, and 6× display scales; wheel zoom and pan inspect small cells. Display scale changes neither ownership nor exports. PNG and SVG keep the native logical dimensions. A 1200-record default example occupies 4800 colored pixels inside a 128 × 128 image, including padding. Do not enlarge the center or convert small records to subpixel slivers.

## Growth and meaning

1. Start with one occupied lattice site at the center. Grow only into a vacant four-neighbor site of the occupied body, so there are no disconnected islands or diagonal-only joins.
2. Prioritize sites using a seeded smooth radial field with bounded broad lobes. Positive arrival increments maintain a growth order. This is a deterministic packing process, not a biological simulation or an organization's history.
3. Allocate all records in generation zero, then generation one, and so on, to successive growth sites. Every completed generation remains connected to the previous body. Depth follows this growth order; equal depths do not have equal Euclidean radii.
4. Within a generation, preserve circular hierarchy order and choose an angular alignment near subtree midpoints. This encourages locality but is not a guarantee that each subtree is connected. Do not describe cell contact, contour lobes, or exact angle as reporting relationships. The outline is a packing choice, not another measured attribute.
5. Expand each site into one equal square of the requested pixel size. No manager receives extra area for its descendants. Total occupied area therefore counts records; attribute values never resize or relocate cells. A highlighted branch can contain separated cells; its membership follows the exact tree, not visual adjacency.
6. Reuse the categorical and numeric color rules from the pixel view: stable full-dataset categories, global positive-value quantiles by default, optional linear/log1p bands, distinct zero, and gray missing observations. Preserve exclusive individual versus observed subtree sums and known/total coverage.

The exact tree remains available through search, branch highlighting, and each record's parent in the outside details panel. Preserve input identities and parents. Use radial pixel mode when exact depth rings and angular subdivision matter more than equal small cells; use organic mode for compact pattern recognition with few pixels per record.

## Validate

Run `test_explorer.py` when changing packing or its options. Use `audit_pixels.py` on the actual output; it selects the layout's semantic checks automatically. For organic output it checks equal square coverage, unique cells, exact pixel ownership, connectedness, every generation prefix, absence of enclosed holes, growth order, scale controls, hit testing, native-size exports, and hidden SVG context. The shared checks cover fixed lenses, global numeric thresholds, missing versus zero, keyboard/search, image-only mode, mobile layout, offline requests, and browser errors.

Inspect the native PNG and a modest integer enlargement. Confirm that the center is a small cell, records have uniform thickness, the body is cohesive, and the role and numeric lenses form useful different patterns. Validate a chain, a star, an uneven tree, alternate seeds, and a larger record count when changing the algorithm. Treat the 20000-record input cap as a bound, not a promise of arbitrary scale or instant rendering on every device.

SVG metadata includes source records, reporting parents, values, seed, cell positions, growth order, and the meaning of each visual channel. The bare PNG remains intentionally wordless; deliver its HTML and input for context. Keep published radial and analytical links available when making the organic example the default.
