# Native Arrow Contrast and Clearance

Use this reference for newly rendered diagrams with directional links. Keep category bodies solid and borderless; preserve compartments, icons, semantic line art, and the direction of each link.

Require at least 3:1 visible non-text contrast for both the shaft and the complete arrowhead against every actual painted backing at readable, resting, focus, and final delivery states. Composite alpha and opacity before measurement. Inspect the actual contour of enclosing deployment polygons and other regions, rather than assuming every arrow is on white.

The SVG renderer invokes the bundled `scripts/arrow_contrast.py` after native palette finishing. It keeps an already safe palette hue or chooses the nearest allowed paint that contrasts with all crossed regions. In a compound deployment region, a gray that passes on white can fail on a dark green enclosing silhouette. Shaft and explicit native head paint are checked independently; some heads lie in the white gutter while the shaft also crosses the enclosing region.

For SVG-capable authored diagrams, PNG derives from this same finished SVG using the declared `resvg-py` dependency, including PNG-only requests. The report records `svg_derived: true`. SVG and PNG retain the same geometry and corrected paints. The PNG canvas is opaque white, matching the native theme and its arrow/text contrast backing. Raster-only Ditaa/standalone math and source-media fidelity cases keep their native output path. Inspect the exported PNG at readable size after palette quantization; preserve system fonts or install the requested font when text metrics matter. The dependency's [SVG-to-PNG API](https://resvg-py.readthedocs.io/en/latest/api.html) documents font and renderer options.

Prefer clear gutters and heads outside target silhouettes, with a small explicit clearance. Preserve native open arrows, diamonds, circles, bars, and other meaningful glyphs. A hollow symbol communicates through its visible stroke, not its white void. If one paint cannot contrast with every crossed backing, change the source route or layout and rerender. Do not add decorative node borders, broad halos, or off-palette head colors.

The PlantUML finisher clips shallow grouped shaft contacts and moves filled
tips into their existing local gutter with 3 px clearance plus half the stroke
width. It retains native curve controls and body geometry. Test very small
insets as well as visible overlaps; a point containment tolerance must not
hide a short low-contrast stroke inside a body. JSON/YAML source ports require
special care: primary red and white cannot share one 3:1 connector paint. Move
the whole source dot and its straight initial shaft prefix into the existing
source gutter, leaving at least 3 px beyond the complete painted dot envelope.
Keep the native curve controls, target head, source labels and relationship
unchanged. Safe original source-port attachments remain in place. Unsupported
port prefixes fail explicitly. Semantic cardinality contacts retain their
intentional attachment.
Activity and state paths also clear hollow final-marker strokes. Short WBS
tree stems use the same visible contrast requirement and local body clearance;
their lack of an arrowhead is not a contrast exemption.

For SVG markers, inspect actual referenced instances, including `markerUnits`, `viewBox`, `refX`, `refY`, orientation, transforms, and every visible part of the head. A prototype in `<defs>` and an endpoint-only sample cannot establish arrow quality. Check any animated or exported counterpart again at its delivery state.

The bundled helper supports sampled native straight, quadratic, cubic, and elliptical-arc paths, rectangle/ellipse backings, and actual polygon contours. It is not a universal router for arbitrary transforms, gradients, filters, masks, or imported source artwork. Use browser measurements and a manual source-layout correction for unsupported geometry. Source-only, faithful imported media, and explicit user styling remain distinct contracts.

Run `uv run --script <skill-root>/scripts/test_arrow_contrast.py` for deterministic contrast, native compound-region contours, arc geometry, marker clearance and identity, meaningful hollow glyphs, and unchanged solid node bodies. Supplement this with actual rendered inspection; rerun the report validator after regenerating delivery files.
