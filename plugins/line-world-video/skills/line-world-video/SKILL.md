---
name: line-world-video
description: Creates balanced explanatory videos with sourced photographs, a guiding dot, original-paper and website screenshot tours, full-frame D3/Mermaid sections, linked data and editable timing. Use for clean geometric stories, narrated research or website walkthroughs and diagram journeys with colorset1 by default, justified colorset2, browser preview and final MP4; visible titles are opt-in.
---

# Line World Video

Turn the viewer's attention into a visible journey. Keep one continuous world,
one guiding dot, stable object identities, and one clock for all representations.
Keep the overall composition predominantly white, use grays for structure and
information, and reserve primary red for selective emphasis. Judge the visual
hierarchy of the complete composition; do not enforce pixel percentages or
derive a background split from this direction. Use colorset2 exceptionally when
multiple entities or independent data lines need additional distinct colors.
Keep those identities stable. Give primary red the leading accent role.
Use dark gray `#696969` for a second
highlighted comparison and light grays for quiet marks. Reserve charcoal/black
for text, fine details or a last contrast need.
Avoid large black blocks. Read [color priority](references/color-priority.md)
when choosing fills or adapting imported producer palettes.
Use borderless solid gray for small objects and solid primary red for their
active emphasis, with readable internal text. Reserve white interiors and
discreet outlines for groups/containers. Preserve quantitative and brand colors;
never use pink object backgrounds. Mark item/group surface roles, then use the
shared theme's `finish` and reversible `focus` helpers for native SVGs.
Use white text and monochrome icons inside red objects. Read
[icon contrast and centering](references/icons-and-alignment.md) for background-aware
glyphs, two-axis content alignment and the one-command item audit.
Keep that guide in primary red `#9e1b32`. Vary its size with attention and travel;
let additional points encode actual quantities or categories. Read
[attention choreography](references/attention-choreography.md) when adapting
these behaviors, category colors or emission timing.
Default to no visible titles, subtitles, slogans or explanatory banners. Let the
figures occupy the frame in balance; retain only essential entity labels, values,
units and legends. Add a few contextual words only when the user explicitly asks
for a title, through `presentation.contextLabels` for the requested beat.
When dividing the presentation, partition the complete frame; place margins
inside sections and use each section for a related concept.

## Plan the story

For website navigation or participation tutorials, read
[real website screenshot tours](references/website-tours.md). Select the native
light theme before capturing pages and interfaces; verify its visible result
and keep it consistent. Preserve the actual interface and account gates, then use the bundled
builder for source-pixel targets, measured audio cues and a downloadable MP4.

For a research-paper walkthrough, read [original-paper tours](references/paper-tours.md).
Use actual pinned PDF captures, source-region identities and measured narration
cues. Preserve the paper's figures, colors and values; apply the film theme to
added overlays and derived views. Use `paper_video.py` for cached page capture,
text-region lookup, deterministic preview, trajectory audit and scene rendering.
Default to one gradual camera entry followed by pans at a fixed scale. Keep
reading holds and skip unnecessary moves between nearby targets. Use clear
margin marks and the adjacent guide; protect source text and raster connectors
from emphasis ink. Never pulse in and out for each narrated item.

1. Preserve the requested facts, output paths, dimensions, language and duration.
   Mark synthetic data explicitly. Read [visual direction](references/visual-direction.md)
   for the sparse geometry, camera and palette rules.
2. Read [data storytelling](references/data-storytelling.md) for tabular inputs.
   Identify the question, meaningful values, units, comparison and caveats before
   choosing chart types. Bind focus by stable row ID, never by screen coordinates.
3. Read [timing](references/timing.md). Allocate arrival, reveal, travel and reading
   holds separately. Keep all scene boundaries and highlights derived from the
   project-owned `story.json`; never scatter absolute timestamps across code.
4. Before generating narration, read [subject-centered scripts](references/narration.md).
   Explain mechanisms, evidence and consequences; review production commentary
   with `narration_review.py`. Keep limitations that affect interpretation.
   For timing, read [speech-linked focus and label clearance](references/speech-focus.md).
   Bind each spoken reference to a semantic target and a measured audio time.
   Arrive beside the object, including separate destinations for repeated values.
   Audit text against other text, dividers, connectors and the guide's full size.
5. Before drawing physical objects, read [real objects and photographic treatments](references/documentary-images.md).
   Prefer verified photographs for documented hardware and other real objects.
   Use `documentary_assets.py` for cached originals, grayscale/edge/pixel/one-bit
   variants, credits and object-binding audits. Keep diagrams for explanatory
   mechanisms and relationships. Inspect recognition at actual delivery size.
   Keep secondary component photographs neutral; restore their reviewed original
   colors only during semantic focus, then return to gray. Use
   [photographic focus](references/photo-focus.md) for aligned pairs, editable
   transitions and the parent-clock pixel check.
6. When the story needs recognizable people or company marks, read
   [portraits and circular logos](references/people-and-logos.md). Research real
   source photographs and their contribution context, then use `media_assets.py`
   for cached acquisition, circular assets, attribution and graph-node exports.
   Keep photo/brand identity intact and reserve an adjacent attention port.
   Introduce every visible person by name and relevant contribution in both
   narration and a short adjacent caption. Bind their first spoken name to a
   distinct guide target. Run `people_context.py` before voice generation and
   again with actual source/audio observations before delivery; a face alone
   cannot explain who contributed or why they matter.

## Build and adapt

For each chart/diagram held in focus longer than two seconds, read
[long-focus motion](references/focus-motion.md). Animate a meaningful relation,
trace or restrained emphasis throughout the hold while preserving readable
labels and truthful data. The guide's movement alone does not satisfy this.
Use the bundled parent-clock runtime and actual-target pixel audit when helpful.

For revisions, read [incremental editing](references/incremental-editing.md)
before reading source or rewriting arrays. Use the semantic editor's bounded
inspection, stable-ID patches, shared CSS theme and dependency/continuity plan.
Let deterministic helpers perform repeated work; reserve model reasoning for
the narrative, representation choice and visual review.

For several simultaneous concepts, full-surface sections, or a broad comparison
of D3 and Mermaid, read [full-frame atlas](references/full-frame-atlas.md) and use
`init --layout atlas`. Its sixteen scenes include native Mermaid sources/SVGs,
linked D3 views and an exact coverage manifest. Choose useful complementary
representations; treat redundant pairings as comparisons, not default recipes.

Run the bundled builder to create an editable offline composition. Substitute
the actual loaded skill directory for `<skill-root>`; keep that directory read-only.

```text
uv run --script <skill-root>/scripts/line_world.py init --project film
uv run --script <skill-root>/scripts/line_world.py build --project film
```

`init` creates a small synthetic story and copies the runtime template, real D3,
GSAP, a local font, and licensed monochrome icons. `build` validates the story and
updates `story.js`, timing/selection manifests and the root composition duration.
It also creates a project-owned `theme.json`, compiled `theme.css` and editing
registry. Keep routine style changes in the theme rather than scattered SVG code.
Use `--story input.json` with `init` for supplied data. Edit generated project
files, not the skill. Preserve `window.renderAt(seconds)`, `window.snapshot()`
and the paused registered HyperFrames timeline when extending geometry.
Vendor files created by `init` live under `film/assets/vendor/`.
For a small custom narrated figure, copy only `assets/runtime/focus.js` into the
task workspace and author its HTML directly. Use `scripts/inspect_focus.py`
with `--html figure.html --times 2.2,4.1,5 --output focus-review.json
--screenshot preview.png` to perform local browser checks without scaffolding
the unrelated starter or probing dependency folders. The helper owns browser
discovery, font readiness, geometry checks and repeat seeking.

For changes to timing, palette, attention or data, use
`line_world.py update --project film --patch changes.json`. It validates a JSON
merge patch, saves the prior story, rebuilds dependent files and rolls back if
an asset fails. Unchanged edits skip rebuilding. Arrays replace whole arrays.

The starter supports 2–8 nonnegative paired rows and optional same-length
histories of at least two points. It is a worked visual grammar, not a reason to
force unrelated facts into before/after data. For other data, adapt the generated
scene and story contract using the reference's chart-selection guide.

Read [producer handoff](references/producers.md) when using D3, Mermaid or Iconify.
The plugin includes those companion skills; discover their actual installed
locations and prefer its dedicated `line-world-*` copies. Their defaults remove
document/gallery chrome and share this film's aesthetic and timing contract.
Exchange project-owned SVG/data/receipts,
not sibling imports. The standalone starter has a local D3 implementation and
small licensed SVG assets, so these companions are optional at runtime.
For plugin maintenance, read [dedicated profiles](references/plugin-profiles.md).

## Preview, test and deliver

For prepared narrated clips or a visual-only revision, read
[reusable project delivery](references/project-delivery.md). Use
`project_delivery.py` to prepare measured assembly requests, cache local
assemblies and package portable inputs without project-specific code.
Run this standard-library/FFmpeg utility through uv; use `uv run --with pillow`
only when a separate custom image operation actually needs Pillow.

When the requested editor or voice provider is Google Vids, use the optional
`line-world-google-vids` companion to assemble the prepared clips and exact scripts
through its native interface. Measure generated voice durations before finalizing
the visual holds, preserve one guide/camera pose across scene joins, and verify
the downloaded native export. A local render remains available when that editor
is not requested or is unavailable; label its provenance accurately.

Read [rendering](references/rendering.md). The preview provides scrub, playback,
speed, beat selection, drag-to-pan and reset. Controls never appear in the film.
Run the deterministic browser audit before rendering:

```text
uv run --script <skill-root>/scripts/render_line_world.py --project film --audit-only --report audit.json
uv run --script <skill-root>/scripts/render_line_world.py --project film --output final.mp4 --report render.json
```

The bundled capture fallback renders exact timestamps with Playwright/FFmpeg.
Direct browser capture is the default; use `--capture svg` only when that
computed-SVG/resvg route is needed. This avoids the per-frame computed-style
export cost for ordinary video production.
For native HyperFrames, install the project's pinned dependency using project-local
caches, then use `node scripts/hf.ts lint`, `validate` and `render`. Keep the native
and fallback render evidence separate. Never call an unexecuted host installation
or native render verified.

Inspect the contact sheet and full-resolution hero/transition frames. Verify units,
table/chart agreement, focus transitions, arrow tips, label clearance, exact output
dimensions, frame count, duration and final state. Deliver the MP4, preview,
editable story, timing manifest, inspection images, and actual validation results.
Keep at least one explanatory object visible from the first encoded frame through
every pan and handoff. A guide dot, divider or empty panel is insufficient.
The default renderer checks source anchors and encoded content automatically.
For custom/native-editor films, run the whole-film review before delivery too.

For a complete visual revision, read [whole-film visual review](references/visual-review.md).
Use `scripts/review_video.py` to decode the actual movie, sample cue travel and
scene openings, scan guide geometry throughout the source clock, and produce
a cached gallery plus compact timestamped findings. Inspect and record the
visual decisions, correct the source, and repeat against the new native export.

For the reusable mechanisms and their contracts, read
[pattern recipes](references/pattern-recipes.md). Do not read acceptance galleries
or large vendor sources during ordinary use.
