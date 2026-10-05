# Compact conceptual graphs and trees

## Contents

- [Simple native conceptual graphs](#simple-native-conceptual-graphs)
- [Prescribed native rectangles](#prescribed-native-rectangles)
- [Other conceptual layouts](#other-conceptual-layouts)

Apply this pass to connected explanations inside a slide. Quantitative
charts retain useful data dimensions, comparable scales, axes and legends.
Supplied geometry remains unchanged during capture-only tasks.

## Simple native conceptual graphs

For a small workflow, start with IDs, complete labels and directed edges,
marking cycle-closing relationships `kind: "return"`. Omit guessed `x`/`y`
and let the helper compute ranks; use integer `rank` on every node when the
ordering matters. Probe this first draft before rendering final paths.
The helper renders native ECharts 6.1.0 symbols, arrows and captions;
computes the canvas from full labels; protects complete envelopes; and uses
a 1:1 native view transform. It installs the pinned ECharts dependency in
the current task workspace when needed, without reading acceptance fixtures.

```json
{
  "title": "Review workflow",
  "nodes": [
    {"id": "input", "label": "Complete incoming material label"},
    {"id": "review", "label": "Independent review"},
    {"id": "archive", "label": "Archive"}
  ],
  "edges": [
    {"source": "input", "target": "review", "label": "Verify"},
    {"source": "review", "target": "archive"},
    {"source": "review", "target": "input", "kind": "return", "label": "Retest"}
  ]
}
```

Render **every unverified first draft** with `--probe` into fresh task-owned
candidate paths. This includes prescribed dimensions and optional custom
coordinates. Read the review JSON's `accepted` field before using a candidate:

```text
uv run --script skills/slidev-echarts/scripts/render_concept_graph.py source/graph.json --probe --svg candidates/initial.svg --option candidates/initial-option.json --review candidates/initial-review.json
```

`accepted: false` is expected layout feedback: exit zero, a `gate`/`reason`,
and no SVG/option. Correct that draft and use new candidate paths. Preserve
the last passing layout. Invalid input, dependencies, parser errors and
unexpected exceptions still fail. Never preview rejected or stale candidates.
Run the probe alone, then read `accepted`; never chain it to preview or
qualification with `&&`, because rejected probes deliberately exit zero.

After `accepted: true`, render and open its native preview. Only then render
the approved input to the exact final paths **without** `--probe`:

```text
uv run --script skills/slidev-echarts/scripts/render_svg_preview.py candidates/initial.svg --output candidates/initial-preview.png
uv run --script skills/slidev-echarts/scripts/render_concept_graph.py source/graph.json --svg deliverables/graph.svg --option source/graph-option.json --review deliverables/graph-geometry.json
```

Final readability gates remain hard failures. Reuse this probe/inspect/final
sequence for tighter candidates. The geometry report contains node/caption/head
envelopes, ranks, routes, natural/explicit canvas dimensions and repeated
arrow-inset findings. Keep the same SVG dimensions in a slide so its readable
fonts remain the planned size. For a live Vue/ECharts component, import the
JSON option and initialize a container at the review's dimensions. Call
`await document.fonts.ready` before the first native `setOption`. Call
`insetGraphArrowRoutes(chart, 3)` after `setOption` and native layout settling,
then `settleConceptGraphCaptions(chart)` from the bundled
`assets/templates/concept-graph-labels.mjs`. This positions existing native
Line captions near visible shafts using the smallest clear displacement;
native backing and emitted glyph envelopes must clear every shaft and head.
Repeat both after option/resize/click updates; inspect actual slide
states. The caption adapter requires this helper's 1:1 native view transform.
Keep ordinary captions on native links through live clicks. Never bypass a
rejected caption gate by replacing the required label with unqualified
graphic text. If custom graphics are needed, inspect shaft/glyph clearance
in every settled click, replay, resize and reduced-motion state.

Build and capture the actual deck with the bundled lifecycle helper:

```text
npm --prefix deck run build
uv run --script skills/slidev-echarts/scripts/capture_deck.py --deck deck --output-dir deliverables/deck-capture --clicks 1
```

Set `--clicks` to the deck's declared count after its initial state; `1`
captures two states, while `0` captures only the initial export view. The
helper owns SPA serving, available port, browser, click focus, replay,
1024×768 resize, reduced motion and cleanup. Read `capture.json` and open
every PNG for labels, heads and route attribution. Page errors still fail.
Use `--slide` for the start slide and `--settle-ms` for authored timing.
Set visible component `data-render-ready="false"` before updates and `true`
after native arrow/caption qualification. Unready components time out.

The helper supports 1–40 nodes and up to 80 directed edges. `colorset`
defaults to `colorset1`. Labels wrap without abbreviation. Default node and
caption fonts are 18/14 px with 14 px heads; requested sizes have minima of
16/14/14 px. Omit `width`/`height` for content sizing. Explicit dimensions
center the same unscaled content and fail when too small. Supply integer
`rank` for every node to control columns, or let non-return DAG edges compute
ranks. Mark cycle-closing relationships `kind: "return"`. Alternatively,
supply finite `x`/`y` for every node and optional edge `curveness` when the
task prescribes coordinates or a measured candidate needs them. Those first
custom drafts also require a probe before final rendering.

Self loops, overlapping nodes/captions, and routes through unrelated nodes
are rejected without delivering an SVG. Reorder ranks or supply a clear
route; split a complex network or use a specialist layout when needed.
Preserve every fact and full label. The report is an automated aid and
still requires Chromium inspection of the final slide, including settled
click/replay states. Quantitative ECharts recipes retain their normal paths.

## Prescribed native rectangles

When the task supplies native symbol dimensions, use the same primary helper
with positive `width`/`height` on each prescribed node and `symbol: "rect"`.
Omitted node dimensions still use measured content sizing. Fixed rectangles
preserve those exact dimensions and full labels at readable size; an
insufficient rectangle fails `fixed-symbol-label-fit` instead of shrinking
type, abbreviating a label or increasing requested dimensions. Both node
dimensions must be supplied together. Canvas `width`/`height` remain separate.

For example, this input renders the complete 90×40 native symbols on a
640×360 canvas, retaining the same y coordinate and clear directed gutters:

```json
{
  "width": 640, "height": 360, "symbol": "rect",
  "nodes": [
    {"id": "alpha", "label": "Alpha", "width": 90, "height": 40, "x": 120, "y": 180},
    {"id": "beta", "label": "Beta", "width": 90, "height": 40, "x": 320, "y": 180},
    {"id": "gamma", "label": "Gamma", "width": 90, "height": 40, "x": 520, "y": 180}
  ],
  "edges": [
    {"source": "alpha", "target": "beta"},
    {"source": "beta", "target": "gamma"}
  ]
}
```

Probe that fixed input first, inspect its acceptance, then qualify the
accepted candidate and open its preview before rendering exact final paths.
This command owns its browser lifecycle and loads
the task's pinned dependency plus bundled palette/caption modules directly;
no handwritten ESM server or browser-discovery script is needed:

```text
uv run --script skills/slidev-echarts/scripts/render_concept_graph.py source/fixed.json --probe --svg candidates/fixed.svg --option candidates/fixed-option.json --review candidates/fixed-review.json
```

Read `candidates/fixed-review.json`. Only when `accepted` is true, qualify:

```text
uv run --script skills/slidev-echarts/scripts/qualify_concept_graph.py candidates/fixed-option.json --width 640 --height 360 --review candidates/fixed-native.json --preview candidates/fixed-preview.png
```

Open the returned preview and inspect the native findings, then render final:

```text
uv run --script skills/slidev-echarts/scripts/render_concept_graph.py source/fixed.json --svg deliverables/graph.svg --option deliverables/graph-option.json --review deliverables/graph-geometry.json
```

The qualification JSON measures native symbols, complete DOM text, caption
envelopes and heads at delivery, larger canvas, restored canvas, replay and
reduced motion. It reapplies native arrow/caption qualification after each
update and verifies repeated insetting, unchanged symbol dimensions, full
label fit, actual caption glyph/shaft/head clearance and routes avoiding
unrelated nodes. A page error or readability
finding remains a failing exit. Record its actual findings in the task's
human review. The same command also qualifies content-sized graph options;
pass their geometry report's width/height. Actual Slidev components still
need the deck's click/resize capture path described above.

## Other conceptual layouts

Freeze full facts, readable fonts/heads/strokes and slide dimensions. Measure
labels; compare orientation or sibling ordering before shrinking rank gaps.
Preserve visible shafts, complete heads, clear endpoints and separate return
lanes. Avoid unrelated labels and junction-like crossings.

Native `layout: 'none'` fits source coordinates through a view transform;
tighter coordinates may stretch to fill an oversized container. Set
content-sized series bounds and inspect emitted positions. Reapply the
[native arrow helper](arrow-contrast.md) after layout, resize and clicks.

Compare at the same delivery scale. Reject overlap, clipping, hidden heads,
ambiguous attachments or lost movement clearance; restore that local gap.
Keep the smallest passing layout and record bounds/gap changes. Preserve
fonts and facts. Inspect click/focus/replay, reduced motion and final export.
