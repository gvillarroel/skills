# Measured connected flows

Use `scripts/scaffold_connected_flow.py` for an ordered row of two to six
concepts, optionally one reciprocal auxiliary check and one backward return.
It emits a reusable Vue component and minimal Slidev deck. Use the general
integration workflow for other topologies and quantitative charts.

Write a JSON contract outside the skill, for example:

```json
{
  "id": "order-handoff",
  "title": "Order handoff",
  "labels": ["Order", "Pick", "Pack", "Dispatch"],
  "branch": {"at": 1, "label": "Inventory check", "outLabel": "check", "backLabel": "return"},
  "return": {"source": 2, "target": 1, "label": "missing item"},
  "palette": "colorset1"
}
```

Run from the task workspace with the loaded skill path:

```bash
uv run --script skills/slidev-animejs/scripts/scaffold_connected_flow.py flow.json --deck deck --component OrderHandoff
npm --prefix deck install
npm --prefix deck run build
uv run --script skills/slidev-animejs/scripts/capture_deck.py --deck deck --output-dir captures
```

Set `--component` to the exact requested component name. The outputs are
`<deck>/slides.md`, `<deck>/package.json`, and
`<deck>/components/<component>.vue`; existing outputs require intentional
`--force`. Adapt wording, props or slide composition after creation while
retaining measured geometry and path-based motion. Run npm in that deck or
with `--prefix`; the parent workspace has no package file.
For an existing deck, scaffold into a temporary task directory and transfer
the component; merge its dependencies and insert the slide/click props into
the existing presentation rather than replacing its package or slides.

The browser measures 18px node labels with 10px horizontal and 6px vertical
insets. Main routes use 48px node gaps to reserve a complete 10px head, a
source gutter, and a visible 8px parcel with head clearance. Check/return
directions use separate ports 28px apart above the row; the backward return
uses its own lower lane. Route labels stay at 16px. The cropped native SVG
fits a standard slide without scaling its fonts; labels beyond 850px width
fail clearly and need a separate subdiagram. Do not shrink the SVG to make
overlong labels pass.

All six base connections remain fully painted in every click/export state.
Click zero shows the complete static mechanism; click one moves the parcel
through the main route; click two follows return and reciprocal check paths.
Set `clicks: 2` in Slidev frontmatter and pass `:step="$clicks"`. Replay
restarts the current click state, scope cleanup stops stale motion, and
reduced motion keeps the complete static map. The parcel samples each
rendered path from eight units after its source to eighteen units before
its target, so it cannot enter an opaque node or cover its arrow tip.

Build, then use the owned capture helper and inspect actual native click
transitions, replay and reduced motion. Its SPA server supports current-route
reload; its scoped Chromium wake-lock permission avoids Slidev's background
permission error. Check every node label, source/target port, full head,
and closest parcel approach. For animated SVG-pack assets, centered scale
or rotation requires CSS `transform-box: fill-box; transform-origin: center`;
passing `transformOrigin` as an Anime.js option does not establish that CSS
pivot. Preserve source SVG geometry and measure the entire moving envelope.
Place static route labels in individual translated SVG groups; this preserves
paint positions during click-driven redraw, including when text DOM bounds
appear correct. Marker IDs are instance-specific so hidden Slidev copies do
not steal another diagram's marker references.

Run the scaffold's meaningful browser geometry tests with
`uv run --script skills/slidev-animejs/scripts/test_connected_flow.py`.
