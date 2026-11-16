# Shared video style and handoff contract

## Contents

- [Composition](#composition)
- [Color and focus](#color-and-focus)
- [Producer handoff](#producer-handoff)
- [Motion and timing](#motion-and-timing)
- [Incremental changes](#incremental-changes)
- [Verification](#verification)

Use this contract for the Line World plugin's specialized producer copies.
The general producer's standalone-document styling does not set the film's
defaults. Keep the original general skills available outside this plugin.

## Composition

- Default to no visible titles, subtitles, chapter numbers, slogans, CTA cards,
  logos, presentation chrome, explanatory banners or decorative badges.
- Preserve essential names, numeric values, axes, units, short legends and the
  symbols required by the notation. Add contextual words only when requested.
- Partition the entire 1920×1080 logical frame for simultaneous concepts.
  Put margins inside sections. Extend shared dividers to their actual frame
  boundaries; do not frame every diagram as an inset dashboard card.
- Use simple geometry on a white field, solid individual marks and outlined
  white grouping shells. Keep an intentional
  size hierarchy. Measure text after fitting the actual producer SVG; aim for
  at least 20 pixels in a normal reading shot. Change direction or partition
  when a native layout does not fit. An overview follows readable full-size shots.
- Keep a meaningful object visible from frame zero through every camera pan.
  A guide, divider or blank panel does not qualify. Retain outgoing context and
  overlap reveals instead of fading all panel contents out during a handoff.

## Color and focus

Keep the overall composition predominantly white, with grays organizing
structure/information and primary red directing attention. This is a flexible
visual hierarchy, not a pixel quota or a required background division. Judge
the objects, negative space, visual weight and contrast together. Use colorset2
exceptionally when a chart has several entities, independent lines or categories
that need distinct colors. Keep the entity-to-color mapping stable. Real photos
and logos retain their colors. The shared
`assets/palettes/video-color-direction.json` records this qualitative direction.
Return representative reading and transition frames for visual review.

Use borderless solid gray for small individual objects, and solid primary red
with white internal text and monochrome icons for active emphasis. Reserve white interiors and
discreet medium-gray contours for groups/containers; their focus may use a red
contour. Never use pink object backgrounds. Retain
dark-gray secondary comparisons, exact quantitative fills and photographic/brand
identity. `LineWorldTheme.focus(root,target,role)` reversibly applies this
emphasis, including native SVG CSS, without changing geometry or adding timers.
Mark shapes `data-lw-surface="item"` or `"group"` and call
`LineWorldTheme.finish(root)` after fonts load. `focus` also accepts an array of
related targets, resolves a text target to its small containing face and chooses
readable internal text automatically. Mark quantitative/category paints with
`data-encoding` or `data-lw-preserve="paint"` to keep them stable.
For custom recoloring, call `LineWorldTheme.contrast(root)` afterward. It
recomputes nested SVG text/tspans and HTML label colors, including unbound values,
so inactive labels return to dark ink when the active body changes. Mark
monochrome glyph wrappers, symbol uses or SVG images `data-lw-icon="monochrome"`;
the theme adapts their actual paint while retaining transparent holes. Keep
real brand assets unmarked. Center the combined icon/label block horizontally
and vertically after fonts/assets load. Give each face its own parent; use an
explicit `data-lw-content` wrapper with `data-lw-for="face-id"` for deliberate
layouts. `finish` centers simple item content automatically; call `center(root)`
after content changes. Do not recenter data coordinates or entire group layouts.
Use `data-lw-align="preserve"` for deliberately aligned objects. The theme audit
flags incorrect icon ink, content off-center by more than two CSS pixels and
content overflow. Verify selected and inactive states at playback size.

- Default to exact colorset1 with primary red first, light/medium grays second
  and black last. Use the bundled video palette sequence, not a general
  producer's black-second order. Keep white `#ffffff` for normal surfaces.
- Use `assets/palettes/video-colors.json` for the video sequence and text
  choices. `colorsets.json` retains the unchanged base token contract.
- Use dark gray `#696969` for the second highlighted comparison series or bar.
  Keep pale grays for quiet quantitative areas and inactive category fills. Keep
  charcoal `#333e48` for readable text, icons and fine structural outlines.
  Reserve near-black/black for a concrete last contrast or notation need;
  avoid large black blocks. Preserve quantitative widths and areas.
- Use red `#9e1b32` as a filled small object, selected label, small accent or guiding
  point. Avoid filling large panels red merely to create energy.
- Keep the guide exactly primary red `#9e1b32`, never accent `#e8002a`.
  Enlarge it at focus/emission, contract it in travel, and settle afterward.
  Its size expresses attention rather than a measured quantity.
- Use colorset2 only when distinct simultaneous categories need extra hues.
  Record the reason and mapping. Maintain stable identity across all views;
  use labels, dash or shape as well as color.
- Keep semantic shapes and quantitative geometry. Remove decorative shadows,
  gradients, shiny cards, fake depth, arbitrary rounding and visual noise.
  A proportion, Sankey width, confidence band or genuine hierarchy remains data.
- Additional points must carry quantities or categories. Keep their category
  colors stable, reserve primary red for the guide and show a useful unit or
  legend. Conserve encoded quantities; use area for a fractional final point.
  An observation point is not interchangeable with a quantity token.

## Producer handoff

Prefer sourced photographs for real physical objects and documented products.
Verify the exact model and variant; do not draw a generic chip to impersonate a
specific graphics card. Keep diagrams for mechanisms, relationships and data.
Combine a real object photo with its functional diagram when both help explain
the subject. Use a baked grayscale, edge, pixel or one-bit treatment only when
it preserves recognition. Retain the original source, rights and transformation
record; avoid circular hardware crops, decorative frames and changing dither
texture on each frame. The primary producer includes a standalone documentary
photo helper; optional image companions are not required for that workflow.

Narration explains the subject's mechanisms, evidence and consequences. Let
the image carry its own geometry and motion. Avoid spending speech on the
pointer, diagram simplifications or the fact that a chart repeats a table.
Keep brief navigation and limitations that change the evidence's meaning.
Review wording before generating speech, then measure the actual voice and
re-align semantic cues after any script change.

When showing a real person, supply a sourced contribution, a short adjacent
name/role caption and the spoken-name cue. The narration must explain who they
are and why they matter to this stage. A portrait, current job title or company
logo alone cannot provide that context. Preserve team/coauthor attribution.

Create project-owned assets. Return the SVG or HTML, source, native bounds,
semantic IDs, data/units, palette, focus ports and a producer/hash receipt.
Use `data-entity-id` to join the same entity across charts and diagrams.
Namespace IDs, CSS, marker references and ARIA references before composition.
Keep the producer's actual geometry instead of drawing an imitation.

Prefer complementary views: process plus durations, schema plus records,
hierarchy plus proportion, timeline plus histories, Sankey plus matrix. A pie
and a donut usually repeat the same fact; compare alternatives deliberately.
Do not equate legal transitions with measured events or rank with magnitude.

## Motion and timing

Give every delivered asset one `renderAt(seconds)` or equivalent pure state
function. Make random geometry seeded and pre-tick simulations. Use the parent
composition's clock when embedded. Do not start a competing autoplay timer,
CSS loop, `Date.now()` animation or independent requestAnimationFrame loop.

Separate arrival, reveal, focus movement and reading holds. Let the camera pan
through a larger persistent world. Do not shake, bounce or rotate labels for
decoration. Make red focus move between matching objects without covering text.
Keep duration and focus windows in editable project data, not scattered magic
timestamps. Put transport and editing controls outside the film.

When a chart or diagram remains in focus for more than two seconds, keep
meaningful motion in that figure throughout the hold: trace a real curve,
follow an actual connection, reveal related parts or add restrained emphasis.
Preserve fixed values, labels and camera stability. Guide movement alone does
not qualify. Use the bundled `assets/runtime/focus-motion.js` for deterministic
trace/pulse overlays from the parent clock, or retain suitable native motion.
Prefer a calm 3.2-second cycle. Do not distort data or move labels to create
activity; avoid rapid repeating zooms. Check actual target pixels and reading
states, including backward seeks. Paper/photo source pixels remain unchanged.

The bundled `assets/runtime/attention.js` exposes pure
`LineWorldAttention.settings`, `radius`, `tokens`, `sample` and `clearPort`.
Use the parent clock and project-owned size/emission/flight settings. Keep
the largest guide clear of labels. Do not add idle pulsing or confetti.

For narration, bind each spoken reference to a stable target ID and a word time
from the actual audio. Separate equal values by identity and occurrence. Use
`assets/runtime/focus.js`: `port` reserves space beside the target, `route`
avoids text, and `pose` follows the parent clock, arriving on the spoken word.
Keep the largest guide/keyline clear of labels and essential marks. Prefer
0.18–0.35-second travel. A decorative sweep does not replace semantic focus.
Preserve late cues throughout the measured voice instead of freezing early.
Run its `audit(stageSvg)` after fonts load for text/text, text/frame and actual
stroke/text conflicts. Reroute arrows around labels; preserve divider continuity
by fitting labels inside their sections. Inspect cue arrivals and encoded audio.

## Incremental changes

For secondary photographic components, keep the prepared neutral treatment
outside semantic focus and restore the aligned prepared original colors only
while focused. Use `assets/runtime/photo-focus.js` with the parent clock,
reviewed neutral/color pairs and editable `start`/`end`/`transition` fields.
Default to a 0.35-second crossfade inside each focus boundary. Preserve crop,
fit, geometry, identity, rights and source pixels; never invent missing color.
Await the controller's `ready` before capture. Preserve evidence-bearing colors
in source charts and documents. The orchestrator supplies a verified pair and
measured cue windows; return the binding plan with the produced asset.

Keep stable scene/entity/cue IDs and expose editable values as project JSON.
Inspect only the requested IDs; return a small field patch instead of rewriting
the whole storyboard. The primary video skill has a deterministic semantic
editor and local render plan. Exchange patches and assets, not sibling imports.
Ship shared colors/type/strokes through project-owned `theme.json`/`theme.css`.
This copy includes `assets/runtime/theme.js` and default CSS; read
`LineWorldTheme.colors()`, `.fontScale()` and `.lineWidth()` in authored HTML.
For native SVG styles, substitute the same semantic tokens at render time.
Keep imported native geometry and namespaces intact. After style changes,
audit actual label/stroke clearance. Give the orchestrator renderer inputs and
real first/last poses so it can validate reuse and joins. A local cache receipt
does not confirm speech timing, native editor changes or a final export.

## Verification

Review actual reading frames, camera transitions, the final overview and a
repeated arbitrary seek. Check complete partitions, label bounds, pairwise text
clearance, units, honest scales, stable IDs, exact palette and data agreement.
Render and decode the final movie before calling delivery verified. Preserve
failed checks and record which renderer and plugin copy produced the result.

Capture websites and application interfaces in their native light theme.
Select the supported appearance control before capture, verify the visible
result and keep subsequent views in the same theme. Preserve those original
light screenshot pixels; a recoloring filter is not a native light capture.

For website tutorials, return actual captured interface states with source URLs,
account state and source-pixel control/port coordinates. Preserve native UI
colors and complete labels. Explain observed account gates; do not redraw a
lookalike UI or imply that a gated action completed. The primary orchestrator
can compose and audit captured states with its website-tour utility.
