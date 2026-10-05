# Dynamic Slidev layout acceptance contract

This evaluator-owned contract covers the copy-ready Slidev layout runtime in slidev-echarts and slidev-animejs. It evaluates browser geometry and actual computed paint independently of author self-reports. Runtime resources must remain self-contained. The isolated harness must exclude acceptance fixtures and retain an unchanged copied payload.

## Required artifact surface

Each contract or naturalistic forward test produces the exact nonempty paths deck/slides.md, deck/package.json, deck/components/CollectionStory.vue, deck/data/cards.json, deck/components/SlidevLayout.vue, deck/lib/slidev-layouts.mjs and deliverables/layout-review.md. Extra supporting files are allowed. The package declares Slidev and the chosen theme. The author does not install or build; evaluator-side tooling supplies the existing fixture dependencies.

## Native layout matrix

- Modes: columns, grid, masonry-columns and masonry-rows. Row masonry uses three literal rows; vertical masonry uses columns and actual measured natural heights.
- Content counts: 3, 7 and 11, plus a filtered/reordered state with a complete persistent category manifest. In generated decks, verify both direct native click states and actual ArrowRight navigation staying on the same Slidev route for the first two clicks.
- Widths: a wide container and a genuinely narrower inner container, independent of Slidev's outer viewport scaling. Generated decks use a 680 CSS-pixel parent/frame constraint and an explicit restoration of the original measured container constraint. At the narrower width, allow a documented positive configured column count no greater than the requested count; horizontal masonry retains its literal three configured rows. Walk every page at both widths.
- Palettes: colorset1 and colorset2. UI scheme and reduced-motion variants must preserve the declared fills and content geometry.
- Publication states: fits=true, complete readable labels/bodies, no card overlap, no clipping and no hidden overflow. Explicit pagination or split views retain every identity at readable font sizes. The negative capacity fixture must report fits=false instead of claiming a valid fit, and any debug notice must be opt-in.
- Pagination: visible IDs match the selected page; walking every page reaches all active identities exactly once; reordering and paging do not recolor the same identity.
- Semantic order: stable IDs and source-order labels remain available even when shortest-column or variable-width packing changes visual placement.

## Independent browser checks

Inspect actual card bounding boxes, row/column membership, child text range rectangles, viewport/container bounds, native computed fills/ink and declared exact palette tokens. Require black or white inside labels chosen by maximum relative-luminance contrast against the actual fill. Check decorative borders are absent until the selected palette's usable solid capacity is exhausted. Preserve explicit overflow metadata after capacity. Require at least two actual widths across final horizontal-masonry pages and two actual heights across final vertical-masonry pages. Qualify the named Previous page/Next page controls for exact palette paint and opaque active text contrast, excluding Slidev navigation chrome; disabled controls do not require the active-state contrast gate. Support the documented fixed compact 16px-title/14px-body slot recipe as well as the native 20px/18px fallback. The recipe is not an exhaustive font whitelist or a hard floor: custom slots own explicit fixed typography. Inspect title/body legibility at the captured final size, report their font sizes, and reject font-size changes across count, page, or resize states. Keep IDs/source-number metadata distinct from semantic title/body text. Reject unexpected author colors, overlapping rectangles, cropped glyphs, shrink-to-fit typography, wrong horizontal-row semantics, stale count/page states, and title or body text replaced with a placeholder.

An editable item slot must support richer Vue content. Qualify at least one custom slot using the same wrapper tokens and one ordinary Mermaid fence alongside it when practical. Plain Mermaid remains governed by the deck-wide diagram setup; layout geometry must not replace diagram semantics or introduce per-fence color directives.

## Isolated release policy

Run one contract case and three naturalistic repetitions for each changed skill with strict JSON, exact required outputs, zero tool errors, a clean runtime read surface and unchanged payload. Attempt the default Spark model for each skill; retain any provider rejection and record an explicit model exception before switching. Do not waive a strict gate because the output looks correct. Render generated decks independently and inspect all requested click states, page states, resized geometry and reduced-motion state. Retain failed attempts and classify provider failures separately from workflow or artifact failures.
