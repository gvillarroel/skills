# Composition Audit

Use this reference when reviewing the compositional structure of an SVG pattern, especially after a user asks for dynamic symmetry, point verification, balance, or visual improvement beyond collision checks.

## Dynamic Symmetry Audit

Run `scripts/audit_dynamic_symmetry.py` against the current SVG or a selected SVG child object. The script opens the source in Chromium, extracts final rendered SVG points, and compares them with a dynamic-symmetry armature.

The measured armature includes:

- frame boundaries and center axes
- thirds, fifths, golden-section divisions, and root-2/root-3/root-5 divisions
- primary rectangle diagonals
- reciprocal and diagonal-parallel armature lines clipped to the composition frame
- intersections between the guide lines

The script extracts points from circles, ellipses, rectangles, lines, polylines, polygons, paths, text anchors, text bounds, image bounds, and fallback bounding boxes. It resolves transforms, CSS sizing, and `viewBox` scaling in the browser before scoring.

## Command

Audit a gallery SVG by ID:

```powershell
uv run --script .agents/skills/d3-animated-svg/scripts/audit_dynamic_symmetry.py .agents/skills/d3-animated-svg/assets/examples/d3-animated-svg/index.html --selector "svg#asymmetric-task-overlap-saturated" --output projects/d3-animated-svg-validation/artifacts/data/asymmetric-task-overlap-saturated-dynamic-symmetry.json
```

Audit a nested object using its own bounding box as the frame:

```powershell
uv run --script .agents/skills/d3-animated-svg/scripts/audit_dynamic_symmetry.py scene.html --selector "g.current-object" --frame object
```

Use `--expect-min-score` or `--expect-min-line-rate` only when a pattern has a known target. Do not force all chart types to the same score; dense scatter, label-heavy, or stochastic-looking patterns can be visually correct with weaker armature alignment than diagrammatic patterns.

## Interpreting Results

- `dynamicSymmetryScore`: a weighted 0-100 score from guide alignment, node alignment, and point-balance. Treat it as a critique signal, not as an absolute quality grade.
- `lineAlignmentRate`: share of extracted points within tolerance of a dynamic guide.
- `nodeAlignmentRate`: share of extracted points close to guide intersections.
- `centerRoles`: focused score for centers and text anchors. Improve these before moving secondary corners or decorative marks.
- `terminalRoles`: focused score for line/path endpoints. Useful for leader lines, arrows, routes, and connector-heavy diagrams.
- `farthestPoints`: points farthest from any guide; inspect these first when a pattern feels arbitrary.
- `outsideFramePointCount`: should usually be zero for published SVGs unless overflow is intentional.

## Improvement Loop

1. Run the audit on the current SVG or selected object.
2. Inspect `centerRoles`, `terminalRoles`, `guideHits`, and `farthestPoints`.
3. Move primary centers, major line endpoints, label columns, or dominant containers toward nearby named guides.
4. Keep semantic data truth first. Do not distort quantitative geometry just to raise a score.
5. Rerun collision, text-fit, gallery, or screenshot checks after geometric changes.

For dense patterns, improve the most structural anchors rather than every small point. A handful of strongly aligned centers or terminals can improve visual order without making the output look mechanically gridded.

## Composition Variant Sheets

Use `assets/examples/d3-animated-svg/composition-sheets.html` when a user wants pages or sheets organized by composition type instead of visualization type. The sheet generator reviews every current source pattern from `window.D3_ANIMATED_SVG_EXAMPLES`, assigns only the useful target compositions for that pattern, and renders optimized variants with visible lines and quadrant use. Each sheet is a curated set of good SVG variants, not a repeated copy of the full D3 gallery. Only add a source pattern to a sheet when the pattern can express that composition clearly.

Current sheet IDs:

- `balance-symmetry`: center axes, mirrored weight, and quadrant balance.
- `diagonal-armature`: major diagonal, minor diagonal, and reciprocal diagonal motion.
- `golden-root`: golden section plus root-2/root-3/root-5 divisions.
- `thirds-fifths-grid`: modular thirds/fifths rows and columns.
- `radial-rosette`: center, rings, spokes, and rotational balance.
- `flow-spine`: source, transform, checkpoint, and output roles.
- `dense-label-lanes`: external lanes, clearance bands, and leader underpasses.

Each variant must expose a stable composition-specific ID:

```text
d3-composition-<composition-id>-<source-example-id>
```

Examples:

- `d3-composition-balance-symmetry-force-network`
- `d3-composition-diagonal-armature-force-network`
- `d3-composition-radial-rosette-force-network`

Each rendered card must include an inline SVG preview and expose:

- `data-composition-id`: the active sheet ID.
- `data-example-id`: the gallery source example ID.
- `data-pattern-id`: the stable `d3-pattern-*` ID.
- `data-composition-pattern-id`: the stable composition-specific variant ID.
- `data-source-family`: the source gallery family or inferred family.
- `data-armature-lines`: the lines used to optimize the target composition.
- `data-quadrants`: the quadrant roles used by the optimized variant.
- `data-reviewed`: `true` after the pattern has been reviewed.

Each inline SVG preview must include visible `.composition-line` elements, at least four `.quadrant-field` regions, a `.source-pattern-recomposition` group cloned from the rendered base SVG, and a `.base-signature` group that identifies the source pattern used for the recomposition. Composition anchors, lane labels, rings, grid cells, or context panels may be added around the clone, but they should strengthen the requested armature without replacing the source pattern.

Do not use `data-fit`, fit badges, or `strong` / `support` tiers. The sheet membership itself means the variant is good enough for that composition.

When adding a variant:

1. Preserve the source pattern's data semantics.
2. Start from the rendered source SVG geometry, then recompose the preview toward the sheet armature: center balance, diagonal movement, golden/root split, modular grid, radial rings, process spine, or label lanes.
3. Render a nonblank SVG preview on the card so the composition can be visually inspected without opening the base gallery.
4. Keep the base pattern link so the original `d3-pattern-*` ID remains discoverable.
5. Search by the composition ID, source pattern ID, title, or role should reveal the card.

Validate the sheets after adding, removing, or renaming D3 patterns:

```powershell
uv run --script .agents/skills/d3-animated-svg/scripts/verify_composition_sheets.py .agents/skills/d3-animated-svg/assets/examples/d3-animated-svg/composition-sheets.html --min-variants 180 --expected-reviewed-patterns 218 --required-variant d3-composition-radial-rosette-force-network --expect-clean
```
