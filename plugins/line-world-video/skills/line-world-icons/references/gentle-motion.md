# Gentle movement for static visual assets

## Contents

- [Choose one small movement](#choose-one-small-movement)
- [Apply the shared clock](#apply-the-shared-clock)
- [Verify before delivering](#verify-before-delivering)

Use this recipe for logos, isolated photographs, illustrations and static
concept groups. Keep moving footage readable; add a detail camera only to a
deliberate held frame when a reviewed region benefits from emphasis. Use space
and alignment to compose sections. Do not add a decorative central rule, panel
outline, separator strip or column border. Preserve meaningful axes, table
rules, source-paper ink, connectors and intentional group boundaries.

## Choose one small movement

| Asset and purpose | Starting settings at 1920 × 1080 |
| --- | --- |
| A few independent logos or images feel suspended | Float by 3 units horizontally and 8 vertically; 10-second cycle; stable per-ID phases. |
| A connected static concept group needs life | Float the complete group, including its edges and labels, by 2–3 / 5–8 units. Keep internal relationships fixed. |
| A useful detail in a photograph deserves attention | One 1.08–1.12 zoom, 4 seconds in, at least 3 seconds held, 4–6 seconds out. |
| Several nearby image details need explanation | Enter once and pan slowly at a stable scale; hold at each destination. |
| A paper, table or plot is being read | Keep its reading geometry stable. Use its specialist source tour or meaningful trace rather than floating individual values or cycling zoom. |

These are editorial defaults, not a medical guarantee or an accessibility
certificate. Do not stack float, rotation, zoom and parallax on one target.
Avoid bounce, random jitter, rapid repeated zoom, synchronized bobbing and large
rotations. Keep source colors, geometry, crops and identities intact. Preserve
the photograph's original view before and after a detail cycle.

## Apply the shared clock

Copy `assets/runtime/gentle-motion.js` into the project and load it before scene
code. Use a dedicated empty SVG `g` wrapper; keep authored placement/transforms
on its children. For detail motion, put the original image inside that wrapper
and an outer fixed viewport with a real clip path. Keep captions, guide and
container edges outside the zoomed layer.

```js
const movement = LineWorldGentleMotion.attach(stage, [
  {id:'brand-a', target:'#brand-a-motion', type:'float',
   start:0, end:18, amplitudeX:3, amplitudeY:8, period:10},
  {id:'photo-detail', target:'#photo-camera', type:'detail',
   start:3, end:14, width:800, height:600, focus:[.2,.1,.6,.55],
   zoom:1.10, inSeconds:4, holdSeconds:3, outSeconds:4}
]);
window.renderAt = seconds => {
  // Preserve the authored renderer, camera and speech-linked guide.
  renderAuthoredScene(seconds);
  return {gentle:movement.render(seconds)};
};
```

Use `compile(spec).at(seconds)` when the host owns native video composition or
needs the same pure transform without attaching DOM elements. `envelope` gives
the float's maximum travel. Inflate placement/route obstacles by that envelope,
move complete logo/label assemblies together and derive the guide's adjacent
port from the displayed transform. Audit the actual maximum guide size. Internal
photo zoom keeps its outer viewport and guide port fixed.

The runtime validates finite windows, slow cycle lengths and a normalized
reviewed focus rectangle. Float settles at both ends. A detail cycle enters,
holds and returns once; it is not an autonomous loop. Short scenes must use a
smaller movement or a single entry rather than compressing the cycle. Include
the returned active transform in frame-cache identities; a changing image must
not reuse a static-hold PNG. `scene-effects.js` accepts these windows in
`gentle`, with scene-local clocks and `sceneId`.

For an interactive reduced-motion preview, explicitly choose
`{reducedMotion:true}` from the user's preference. This returns the original
static view. Declare the export's setting; do not let ambient OS timing or an
autonomous CSS animation change deterministic rendering. See the primary
[W3C technique](https://www.w3.org/WAI/WCAG22/Techniques/css/C39.html) and
[WebKit motion guidance](https://webkit.org/blog/7551/responsive-design-for-motion/).
Neither source prescribes the numeric video defaults above.

## Verify before delivering

Use `scripts/inspect_gentle_motion.py` for an authored offline preview. This
avoids writing a new browser driver or color-mask checker for each project:

```text
uv run --script <skill-root>/scripts/inspect_gentle_motion.py --html film.html --width 1920 --height 1080 --times 0,3,6,8,11,14 --float-target "#brand-a-motion" --detail-target "#photo-camera" --viewport "#photo-viewport" --fixed-target "#caption" --output quality.json --screenshot reading.png --screenshot-time 6
```

Choose real entry/hold/return times and explicit selectors. For `--viewport`,
select its fixed rectangle, nested SVG or HTML container, not a content group
whose browser bounds follow the transformed children. Run additional
semantic focus checks when the guide is present. The inspector checks actual
pixels, fixed captions, selected group dimensions, source identity and viewport
coverage with a 0.02 CSS-pixel geometry allowance for browser rounding. It does
not certify narrative timing or native export. Do not infer a whole-image
feature's center from a color mask when that feature is intentionally cropped.

Run `scripts/test_gentle_motion.py` for actual browser motion, identity, clipping
and repeated-seek checks. Inspect the target at entry, maximum displacement,
the detail hold and its return. Test repeated forward/backward seeks and include
the movement in the source's geometry and whole-film review. Confirm that a
subject, logo or label is not clipped and that moving media/edges do not cover
text. Check the actual encoded movie; a source transform alone does not prove
native-render parity, comfort or speech alignment.

For browser evidence, read SVG captions with `locator.text_content()` or
`element.textContent`; Playwright `inner_text()` requires an HTML element.
Use actual fixed viewport screenshots when checking moving pixels, since a
locator screenshot can follow a floating target and conceal its displacement.
