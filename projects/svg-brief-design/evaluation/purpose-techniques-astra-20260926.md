# Purpose-matched techniques and Astra transfer

Research date: 2026-09-26. This is development-only hypothesis formation, not
evidence of effectiveness. No private task, source geometry or private outcome
was inspected to produce it.

## Why the previous proposals were insufficient

The public svt7 trials do not establish that more general design advice improves
the skill. Contour/counterform instructions lost 7.07 points on the complete
vintage family; print advice gained 13.55 on space but lost 0.66 on vintage.
Both also contain execution failures. General woodcut/engraving advice offers
too many plausible treatments for these short briefs. The current skill already
contains negative-space, hierarchy, taper and subtraction advice. Repetition is
not a new mechanism.

The narrower hypothesis is **assign a representational function to every mark
and resolve one local construction before repeating or embellishing it**. The
guide must select by intended artifact, not impose one historical process or a
universal minimum number of elements. This is our synthesis; sources do not
prove it improves generated SVGs.

## Sources and limits

- [Princeton/Rutgers, Suggestive Contours](https://gfx.cs.princeton.edu/proj/sugcon/index.html)
  distinguishes silhouette, occlusion and additional shape-conveying lines. We
  adapt the principle of choosing informative cues for an invented drawing; we
  do not implement their mesh algorithm or call an arbitrary stroke a computed
  suggestive contour.
- [Cole et al., How Well Do Line Drawings Depict Shape?](https://www.cs.princeton.edu/~funk/cole09.pdf)
  studies perceived surface shape and localized line-dependent errors. Its
  results do not establish aesthetic quality, brand style or SVG evaluation
  scores. This supports checking a line's local meaning rather than rewarding
  line count or smoothness alone.
- [Adobe, Join and trim paths](https://www.adobe.com/learn/illustrator/web/join-trim-paths-lines)
  describes removing overshoot, joining intersections and closing gaps. Adapted
  operation: decide a junction's ownership before joining or trimming it. Do not
  close an intentionally open channel just because a join operation is available.
- [Adobe, Width tool](https://helpx.adobe.com/illustrator/using/tool-techniques/width-tool.html)
  documents reusable variable-width profiles. Adapted operation: coordinate a
  band's two edges and terminal taper. Variable width is optional, not a quality
  target for every diagram or label.
- [NPS, Wayside exhibit design](https://www.nps.gov/subjects/hfc/wayside-exhibit-design.htm)
  starts with interpretive purpose and small sketches that expose hierarchy.
  Adapted operation: plan the principal reading before styling. Its outdoor
  exhibit dimensions and typography do not transfer to a compact vector label.
- [NPS, Map standards](https://www.nps.gov/subjects/hfc/upload/map-standards.pdf)
  uses a label hierarchy and avoids overprinting linework. We transfer only
  purpose/placement, not its fonts, point sizes, map vocabulary or physical rules.
- [IBM, Pictogram design](https://www.ibm.com/design/language/iconography/pictograms/design/)
  specifies a grid and a particular icon system. Rejected as a general recipe:
  enforcing that system would flatten expressive editorial illustration into
  generic product icons. Optical decisions are useful, the branded grid is not.

## Operational mapping

| Intended artifact | Decision before adding detail | Visible failure to correct |
| --- | --- | --- |
| Expressive figure | Landmarks and planar relationships carry the mood; choose which edges are omitted | Generic face made from unrelated symbols; bars hide facial construction |
| Interlaced ornament | Each junction is a union, separation or over/under event | Unowned crossing, pinched sliver, a strand that cannot be followed |
| Open mechanical form | A common directional structure aligns separated masses | Heavy slab with random slots, or disconnected hardware |
| Compact technical graphic | Required fields and one reading path determine occupied size | Invented telemetry, extra rules or an oversized container |
| Editorial scientific diagram | The explanatory relation determines curve, axes and notation | Modern chart furniture with cosmetic antique lettering |

## Frozen experiment

Run the installed nine-file baseline and one ten-file conditional-guide variant
under exact `openai-codex/gpt-6-astra`, medium effort. Each arm has the same six
public briefs, three attempts, unchanged Jev 6.3, tools, container, time limit,
16,384 configured output cap and no retries. Skill contents are model-independent;
Astra selection is in the execution profile, not the skill frontmatter.

Native Pareto qualification and prior declared gain/regression guards apply.
At most 36 public and 12 once-only reserved generation calls; one changed
candidate and one generation. The untouched two-family svt7 reserve is adopted
with provenance and remains invisible until a single finalist is frozen.

Historical Luna svt7 baseline has identical skill bytes and briefs. Compare it
descriptively with the Astra baseline, disclosing historical run timing and
incomplete Luna families. Do not pool the two model profiles in a Pareto archive,
claim paired seeds, or assign quality values to execution errors.

[Official Astra model documentation](https://developers.openai.com/api/docs/models/gpt-6-astra)
confirms its identifier, text/image inputs and medium reasoning support. The
local Pi adapter enforces observed identity; documentation alone is not an
execution receipt. Keep the same configured cap for this comparison even though
the model supports a larger output window.
