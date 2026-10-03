# Information selection and reversible vector editing

Research date: 2026-09-26. Proposed mechanism, not an observed performance gain.
This note uses public development evidence only. The installed skill remains
the accepted nine-file construction bundle until a separate gate passes.

## Sources and transfer limits

1. [NN/g: Aesthetic and Minimalist Design](https://www.nngroup.com/articles/aesthetic-minimalist-design/).
   Necessary information must remain findable; both excess content and missing
   content hurt usefulness. Transfer: identify required features and their
   supporting relationships before removing optional marks. This is a design
   hypothesis for illustrations, not an empirical result about SVG quality.
2. [NN/g: Visual Hierarchy](https://www.nngroup.com/articles/visual-hierarchy-ux-definition/).
   Relative scale, contrast and grouping guide attention. Transfer: distinguish
   the main form, explanatory information and optional accents by visual weight.
   Do not impose a universal label count, density percentage or three-item cap.
3. [IxDF: Proximity, Connectedness and Continuation](https://assets.interaction-design.org/literature/article/laws-of-proximity-uniform-connectedness-and-continuation-gestalt-principles-2).
   Proximity and connected paths establish perceived relationships. Transfer:
   share tangent direction across a smooth join, clarify a crossing with a gap,
   and use coherent channels instead of arbitrary gaps. This does not imply all
   curves must be smooth or all industrial corners must be rounded.
4. [Inkscape: Advanced Tutorial](https://inkscape.org/es/doc/tutorials/advanced/tutorial-advanced.html?switchlang=es).
   Boolean operations and compound paths provide different ways to construct
   silhouettes; simplification reduces nodes while approximating shape.
   Transfer: union joining material; subtract an opening; use a compound path
   for intentional nested holes. The search-indexed official tutorial was
   available, but direct fetching returned an access error in this session.
5. [Adobe: Simplify paths manually](https://helpx.adobe.com/illustrator/desktop/draw-shapes-and-paths/modify-paths/manually-simplify-paths.html).
   Curve precision, corner thresholds and preview support controlled node
   reduction. Transfer: simplify only an irregular segment, compare the result,
   and preserve extrema, intended corners and shared boundaries. Fewer nodes
   alone do not establish better design.
6. [Adobe: Nondestructive editing](https://helpx.adobe.com/ca/photoshop/using/nondestructive-editing.html).
   Separate layers and masks preserve the underlying material while trying
   changes. Transfer: retain editable SVG groups and hide optional groups in
   diagnostic copies. No Photoshop dependency or rasterized final is needed.
7. [W3C SVG: Fill rules](https://www.w3.org/TR/SVG2/painting.html#FillRuleProperty).
   The evenodd rule determines interior regions by crossing parity. Transfer:
   create actual transparent holes and inspect the source on a colored ground;
   a white shape is not equivalent to missing material. Overlapping evenodd
   holes can refill their overlap, so this is not a general Boolean subtraction.

## Decision matrix

| Observed problem | Technique to try | Check | Avoid |
| --- | --- | --- | --- |
| Verbose compact artifact | Assign each text run a required identifier, relationship, or optional role; group related items | Required meaning survives at delivery size | Removing requested information or inventing specifications |
| Generic oversimplified silhouette | Preserve characteristic proportions, articulations and relationships before detail reduction | Subject and mood remain specific | Treating minimum element count as the goal |
| Fragmented ornament | Shared curve construction, continuous tangents, explicit crossing order | One coherent rhythm and clear opening | Independent random bends or unexplained collisions |
| Heavy mechanical blob | Construct adjacent masses and exterior-connected channels | Empty regions help describe the body | White patches, decorative microholes and excessive outlines |
| Nervous outline | Local node reduction or common tangent adjustment | Compare extrema and junctions before/after | Global smoothing that changes topology |
| Wrong visual emphasis | Change relative stroke, spacing and type hierarchy | Dominant form reads before annotation | Thickening every element uniformly |
| Uncertain decorative detail | Hide optional SVG groups in a diagnostic copy | Retain detail only when it adds useful rhythm or recognition | Letting an automated pixel count choose artistic quality |

## Bounded experiment

Hypothesis: a role-based information budget plus a deterministic proof sheet
will help Luna preserve required features while choosing useful detail and
detecting false cutouts. This differs from the three rejected svt3 mutations:
it makes alternate views directly inspectable instead of adding another shape
generator or only enlarging prose. An exact-path link correction prevents a
previously observed reference-name ambiguity; the experiment estimates the
whole bundle effect and cannot isolate either component causally.

One candidate against a fresh control: six public families, two independent
attempts each, 24 generation calls. Exact openai-codex/gpt-6-luna at medium,
unchanged Jev 6.3 evaluator. Native Harbor ranks qualified candidates. Require
at least two points mean gain, no family loss over eight points, all artifacts
valid and zero tool errors. If the baseline has attributable agent errors, also
require the same gain on unaffected families; missing evaluator evidence is
unavailable, not zero. No semantic retries.

The three-case svt3 reserved cohort was never released, run or read by the
optimizer. Adopt its bytes and provenance explicitly for one possible final
gate, without repeating curation or calling it newly authored. It remains
unseen until a selected winner is digest-frozen. If no candidate qualifies,
close this experiment and retain the installed skill. Do not reset the closed
three-failure campaign or silently continue it.

Do not alter brief wording, Jev's rubric or source-relative utility calibration
in this experiment. The score is not an absolute professional grade. Purchased
art remains evaluator-only; neither source vectors nor extracted geometry are
placed in the candidate.
