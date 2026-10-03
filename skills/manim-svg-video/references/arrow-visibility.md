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

The compositor audits transparent source areas against the actual opaque
`--tile-fill` delivery backing, recorded as `deliveryBacking` in the sidecar.
The root CSS background first composites over that tile (`sourceCssBacking`),
then ordinary SVG backing shapes apply in their paint order. Opaque source
canvases take precedence at their own pixels; alpha canvases still reveal the
paint beneath them. Root CSS background images require a separate pixel audit
and stop automatic marker conversion. The PNG keeps its original transparency
and source paint; changing
the tile color can require a different authored arrow color or an explicit
source fidelity disclosure.

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

For an explicitly preserved imported original, use the exact-path
`--preserve-source-media <original-path>` policy described in
[manim-svg-import.md](manim-svg-import.md). Its existing pale/thin arrow findings
remain in the sidecar and delivery notes; they are source fidelity exceptions,
not authored quality passes. Head loss, hidden/covered heads and unsupported
geometry still stop conversion. Do not apply this policy to newly authored arrows.
