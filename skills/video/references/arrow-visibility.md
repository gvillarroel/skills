# Arrow visibility

Keep category cards solid and borderless. Give each directional shaft and painted
head at least 3:1 WCAG contrast against every actual local canvas, node, region or
label backing at resting states and readable interaction/delivery states. Compute
source-over alpha before luminance; never round a ratio into a pass. Whole fades
from/to a hidden state are transitions, not readable states.

Use a darker allowed variant of the same semantic hue, or reroute through a clear
gutter. Preserve source identity, direction and meaningful geometry. Do not add
node outlines or general halos. End the painted tip outside the target silhouette,
with a short visible gap; derive marker refX/refY from the actual painted tip, use
an adequate viewBox, and inspect instances after markerUnits, orient and transforms.
A path with correct attributes can still have an invisible or covered head.

For authored non-marker heads, tag their geometry with data-arrow-head and shafts
with data-arrow-shaft; share data-arrow-id on their group or individual elements.
The bundled [arrow_quality.py](../scripts/arrow_quality.py) samples actual projected
marker geometry and alpha-composited filled backings in Chromium. Run:

```text
uv run --script <skill-root>/scripts/arrow_quality.py diagram.svg --width 1600 --report arrow-audit.json
```

Use --selector for HTML containing multiple SVGs and --width/--height for actual
delivery dimensions. HTML with modules requires its normal local HTTP server;
use the owning browser audit or evaluate ARROW_AUDIT in its loaded page. Check
shaft/head records, occlusion, painted tip offsets and the exact reported ratios.
Review the actual browser still and decoded media too. Test focus, zoom, input
extremes, reduced motion, paused readable reveal states and final delivery size.
A foreground node hiding any sampled shaft or head is an error; never discard
covered samples as proof of contrast.

The sampler supports solid SVG fills, native fill alpha, ancestor opacity,
opacity filters, ordinary marker children/transforms, userSpaceOnUse/strokeWidth
units and default centered meet/none marker viewBox scaling. URL shaft/head/backing paint and intermediate marker instances
are reported as unsupported; custom alignment, clip/mask geometry, blur and complex
filters need a separate actual-pixel review. Narrow connector intersections are
geometry rather than filled backing regions; inspect ambiguous crossings and
coincident routes separately. Only a data-relationship-pulse connector-owned
moving signal may be classified as a semantic overlay for shafts; persistent
heads and meaningful terminals must remain visible, and heads receive no exemption.
Do not extend this exception to arbitrary filled shapes.

Read palette data as an object: `data['colorsets']['colorset2']` (or colorset1),
then its `allowed`, `roles`, `solidSequence` and `textOnFill` fields. In bash,
export `VIDEO_SKILL="$PWD/skills/video"` before a separate command uses
`"$VIDEO_SKILL/scripts/..."`; an assignment on that same command does not supply
its already-expanded argument. The render-state checker declares Playwright for
its browser-module fallback and serves the HTML over HTTP when its Node stub
cannot execute ES modules.

For programmatic SVG arrows, copy [svg-arrows.js](../assets/templates/svg-arrows.js)
into the project. Call drawArrow while building the frame, then finishArrows after
all solid category bodies exist, passing the selected palette.allowed and actual
canvas. It retains hue, clips endpoints to clear body ports and chooses a clear
orthogonal gutter before repainting; audit the resulting DOM rather than accepting
the painter's cached minimum alone. Preserve imported source graphics deliberately.

The helper is a browser ES module; import it in a script with type="module".
Pass a native SVG element directly to drawArrow, or a D3-style selection. No D3
package is required for native DOM scenes. Use id="stage" on the captured SVG,
or pass the actual --selector to capture_html_video.py. Expose renderConceptFrame
before capture and return the deterministic state as the renderer contract describes.
For a legitimate very short, simple clip, lower check_video_artifact.py's generic
--min-bytes floor deliberately (for example 1000 for a two-second smoke clip), then
verify streams, duration and actual decoded content. A static compressed clip may
be small without being blank; byte size alone cannot decide arrow visibility.
