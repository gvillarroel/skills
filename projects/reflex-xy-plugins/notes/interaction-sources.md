# Interaction design evidence — 2026-10-24

The user requested an uncluttered first view that exposes advanced capabilities
as the user learns. The implementation uses one initial chart task and one
discoverable secondary options region; it does not infer proficiency, track
users or introduce a required onboarding flow.

## Primary sources read

- [Jakob Nielsen, Progressive Disclosure](https://www.nngroup.com/articles/progressive-disclosure/)
  separates common initial actions from infrequent specialized choices. It also
  warns against deep disclosure hierarchies and unclear entry labels.
- [W3C WAI disclosure pattern](https://www.w3.org/WAI/ARIA/apg/patterns/disclosure/)
  defines a trigger and controlled region, Enter/Space activation and expanded
  state. Native HTML controls or the appropriate button semantics are preferable
  to inventing a menu with unimplemented keyboard behavior.
- [W3C WCAG 2.2 enhanced target size](https://www.w3.org/WAI/WCAG22/Understanding/target-size-enhanced.html)
  describes 44 by 44 CSS pixel pointer targets, with exceptions. The project
  adopts this size for its authored component controls; this is not a claim of
  complete WCAG conformance or measured native Claude painter geometry.

These sources motivate the design. The project's three-action first-view limit
is a local acceptance choice, not a numerical recommendation from those sources.
No human usability study or usage-frequency analytics were run in this pass.

## Applied changes

The interactive MCP component initially prioritizes the chart and saving its
image. Display, other formats and chart tools belong in one options region,
with purpose-based labels. The Code pane initially prioritizes its native
preview and opening the interactive chart. Palette, samples, rerender and
artifact paths belong behind its native options toggle.

Remove duplicate engine badges, mark/factory counts, persistent success prose
and repeated backend explanations from the initial product flow. Preserve all
five artifact formats and explicit Colorset 2. Keep existing data on palette or
view changes, retain the previous chart on regeneration failure and label sample
data replacement clearly. Put expiry and limitations where an action needs them.

The reusable recipe is bundled in the canonical skill at
`references/interaction-design.md`; normal skill use does not depend on this
project note. Acceptance fixtures and screenshots remain project artifacts.
