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

## Composition Sheets

Use `assets/examples/d3-animated-svg/composition-sheets.html` when a user wants pages or sheets organized by composition type instead of visualization type. Each sheet must keep the full current D3 pattern catalog so a larger composition can be assembled from any pattern family without losing the stable `d3-pattern-*` IDs.

Current sheet IDs:

- `balance-symmetry`: center axes, mirrored weight, and quadrant balance.
- `diagonal-armature`: major diagonal, minor diagonal, and reciprocal diagonal motion.
- `golden-root`: golden section plus root-2/root-3/root-5 divisions.
- `thirds-fifths-grid`: modular thirds/fifths rows and columns.
- `radial-rosette`: center, rings, spokes, and rotational balance.
- `flow-spine`: source, transform, checkpoint, and output roles.
- `dense-label-lanes`: external lanes, clearance bands, and leader underpasses.

Each rendered row must expose:

- `data-composition-id`: the active sheet ID.
- `data-example-id`: the gallery source example ID.
- `data-pattern-id`: the stable `d3-pattern-*` ID.
- `data-fit`: `strong`, `ready`, or `support`.

Validate the sheets after adding, removing, or renaming D3 patterns:

```powershell
uv run --script .agents/skills/d3-animated-svg/scripts/verify_composition_sheets.py .agents/skills/d3-animated-svg/assets/examples/d3-animated-svg/composition-sheets.html --expected-patterns 218 --expect-clean
```
