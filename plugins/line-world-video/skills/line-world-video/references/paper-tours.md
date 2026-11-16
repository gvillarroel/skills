# Original-paper tours

## Contents

- [Source and narrative decisions](#source-and-narrative-decisions)
- [Cheap capture and region lookup](#cheap-capture-and-region-lookup)
- [Compact story contract](#compact-story-contract)
- [Camera and emphasis defaults](#camera-and-emphasis-defaults)
- [Voice, rendering and review](#voice-rendering-and-review)

Use this mode when the viewer should read the actual paper while it is explained.
Keep the paper as the visual evidence. Add camera moves, adjacent primary-red
attention ports and clear margin marks; do not replace every figure with a
redrawn approximation. Do not invent a visible title card. The paper's own title,
figure captions, axes, table headers and notation are source content.

## Source and narrative decisions

Pin the arXiv version and record title, authors, URL, PDF digest, license and
adaptations. Inspect the actual PDF before selecting regions. Prefer a paper
with reusable figures and tables; comply with its license and attribution.
Preserve all original colors, including semantic diagram/grid colors. The
white/gray/red direction applies to additions, not a recoloring of evidence.
Keep original typography and numbers intact. Make charts from reviewed table
values, with a zero baseline, explicit units and stable row/column identities.

Choose a question, method, observed results and material limitations. Explain
which model, data split, sample size, metric and comparison a result belongs to.
Distinguish percentages from percentage-point differences. A small selected
benchmark is not its full parent benchmark. Show contradictory comparisons as
readily as favorable ones. Separate author claims, measured results and narrator
interpretation. Keep a project-owned claim-to-page/figure/table ledger.

## Cheap capture and region lookup

Use the actual loaded skill root; keep the skill read-only. These commands write
only into the task project. Download a reviewed PDF through ordinary public
access first. No browser session extraction is needed.

```text
uv run --script <skill-root>/scripts/paper_video.py prepare --pdf paper.pdf --pages 1,2,5,7 --project film
uv run --script <skill-root>/scripts/paper_video.py inspect --project film --page 7 --max-chars 3000
uv run --script <skill-root>/scripts/paper_video.py locate --project film --page 7 --text "Success Rate"
```

`prepare` captures original pages at 300 DPI, saves page dimensions and extractable
word boxes in `paper.json`, and reuses images only when source, DPI and image
digests match. Specify only needed capture pages. Use `inspect` for bounded page
text and block rectangles instead of writing a
one-off PDF extraction script. Its CLI emits ASCII-safe JSON, preventing Windows
console failures and Unicode line-separator corruption in event logs. Requests
above 12000 characters are capped and reported without a failed call.
`locate` returns PDF-point rectangles with a top-left origin, in the original
page's dimensions. For a
raster diagram embedded in the PDF, inspect its actual page image and annotate
component rectangles. Extractable text boxes do not prove OCR coverage.
Add `avoid: [[left, top, right, bottom]]` for raster plot bodies, axes or labels
that the point must stay outside. A heatmap's unselected cells still belong to
the figure: protect its complete body, not just the currently highlighted row.

## Compact story contract

Keep the story in the project, with one `source` record and `scenes` array.
Each scene has a stable `id`, exact `script`, frame-rounded `duration`, `page`,
`layout`, `view: [left, top, right, bottom]`, `targets` mapping semantic IDs to
PDF rectangles, and ordered `cues: [{target, at, phrase}]` in scene-local seconds.
Preserve narration measurement evidence; initial word-count budgets are estimates.
Do not ship estimates as measured synchronization.

Layouts are `paper`, `table-side` (original left, derived bars right) and
`table-stack` (original top, derived bars below). Each partition spans the entire
frame; put margins inside it. The paper camera enters gradually once, then
pans between targets at a fixed scale. Use `cameraZoom: false` or
`camera: {mode: "static"}` when stable axes/context are more useful.
An optional first-scene `entry: {page, view}` shows the actual title/abstract
before the first figure. Keep that transition before the first spoken figure cue.
Within one native voice scene, `shots: [{at, page, view, cameraZoom}]` can visit
another source region and return without splitting the audio. Each interval
needs at least one parent cue; its `at` remains relative to the native scene.
Keep target rectangles appropriate to the active page. Combine neighboring
regions on the same page into one view when both remain readable; move the
guide between them rather than cutting between almost identical crops.

For a derived percentage chart, add:

```json
{"chart":{"unit":"Success (%)","columns":["Setting A","Setting B"],
"rows":[{"id":"baseline","label":"Baseline","values":[20,25]},
{"id":"method","label":"Method","values":[50,45]}]}}
```

A cue may select `column` and `row`, and use `guide: "chart"` to lead the eye from
the original cell to its matching bar. Values must be reviewed against the PDF;
the range check cannot verify a transcription. Added bars are solid gray or
primary red without borders, with white values inside sufficiently wide bars.
Keep second comparisons dark gray and preserve units when switching columns.

## Camera and emphasis defaults

Treat the viewport as a window over a continuous page. Give the viewer time to
read at each stop. Do not zoom out before every next reference, oscillate scale
with repeated values or re-center for a tiny displacement. Keep tables and axes
stable. An overview is preferable when dense narration cannot support a slow pan.

The deterministic `assets/paper-video/paper-motion.js` owns this behavior.
It has no browser or account actions. Set scene/shot `camera` fields in the story:

```json
{"camera":{"mode":"pan","zoom":1.3,"enterSeconds":2.6,
"travelSeconds":2,"minTravelSeconds":1.4,"minHoldSeconds":1.1,
"safeInset":58,"maxPanSpeed":540},"emphasis":"margin"}
```

These are editable production defaults, not a medical comfort guarantee.
`zoom` is the maximum scale relative to the initial fitted source view. The
planner reduces it to retain complete active regions and the guide. `enterSeconds`
controls the single entry; it never resets for each cue. `travelSeconds` is the
preferred pan length; `minTravelSeconds`, `minHoldSeconds` and `maxPanSpeed` bound
dense transitions. Pan speed is measured in 1920x1080 composition pixels/second.
Near targets can remain under a stable camera. If a necessary pan cannot meet
the time/speed budget, the scene keeps its overview. Short readings stay static.
The guide travels with a planned pan and arrives at the original spoken cue.
These camera settings do not alter narration or scene duration.

`emphasis: "margin"` draws short exterior segments only where source words,
annotated bodies and actual PDF raster pixels leave clear room. The raster test
also protects non-extractable lettering and connectors. Marks are omitted when
no clear margin exists; the adjacent red guide still leads attention. Use
`emphasis: "none"` for a guide alone. Do not add closed rectangles or translucent
fills across the source. Target/view bounds expand to include complete intersected
PDF words. This is not OCR or a guarantee that a poorly chosen raster crop is safe;
inspect embedded figure labels and complete equations manually.

## Voice, rendering and review

For Google Vids, use its native voice generation and measure scene durations.
Align cue phrases with word timestamps from the actual exported voice, using the
plugin's Google Vids companion when available. A standalone workflow can import
reviewed audio timestamps directly into `cues[].at`; record their source and
precision. Separate repeated values by phrase occurrence and semantic target.
Render a scene to its frame-rounded measured budget; a small end hold may fill a
frame, but speech must not be sped up or cut to fit a guessed duration.

```text
uv run --script <skill-root>/scripts/paper_video.py build --project film --story story.json
uv run --script <skill-root>/scripts/paper_video.py audit --project film --report audit.json
uv run --script <skill-root>/scripts/paper_video.py render --project film --output clips --report render.json
```

The preview offers scrubbing/playback; `?capture=1` removes those controls.
`renderClip(index, seconds)`, `renderAt(seconds)` and `snapshot()` use one clock.
Page changes crossfade with visible explanatory content throughout. The guide
uses adjacent ports and obstacle routes. Cached reading holds avoid repeated
screenshots. Use `--scene stable-id` to render only a changed scene.
Add `--poster review/hero.png --poster-scene stable-id --poster-at 3.2` to an
audit to save an exact requested frame without another browser script.

Inspect actual reading, close-up, travel and page-change frames at full resolution.
The automatic word check covers extractable PDF text; manually inspect raster
figure labels, connectors, source cropping and derived-chart labels too. Verify
the guide's entire radius and all-frame trajectory, the active original cell,
the corresponding chart value and the current units. Check margin marks against
the original pixels and verify complete active source regions at reading stops.
The all-frame audit reports scale rate, translation speed and any zoom-out frames
inside a shot; repeated zoom pulses fail the audit. Keep the source frame and its meaning
visible during every handoff. Then assemble in the requested editor, download
the complete movie, and inspect encoded samples and audio continuity.
Deliver the final MP4, editable preview/story/timing, source attribution and
actual validation scope. Keep original-page evidence separate from generated
charts and do not claim a local clip was itself a native editor export.
For reading holds longer than two seconds, the bundled player traces a calm
red segment along the existing safe margin emphasis mark. The PDF pixels,
connectors and table values remain intact. The 3.2-second phase comes from the
same scene clock and is included in the capture state so PNG hold reuse cannot
freeze it. This is an emphasis overlay, not an inferred source relation or a
new datum. Keep its complete ink envelope outside protected words and figures.
