# Composed visual colorset audit â€” 2026-10-02

This audit covers the seven composition, hierarchy, poster and video bundles listed below. Authored renderer paints, controls, labels, native marks, generated tints and exports now use exact colorset1 or colorset2 tokens. Every bundle carries its own identical copy of the canonical [colorsets.json](../../skills/hyperframes-explainer/assets/palettes/colorsets.json); no bundle requires a sibling skill at runtime.

The machine-readable [coverage inventory](compositions-20261002.json) records every output route, scan glob, source-preservation scope, test command, isolated run, exact output hash and remaining publication step. Existing uncommitted repository work was preserved. Repository-wide validators, installation synchronization, Pages generation and publication are owned by the root agent and are not claimed by this sub-audit.

## Output coverage and repairs

| Skill | Authored colorset and output routes | Concrete repair |
| --- | --- | --- |
| `compose-synchronized-svg` | colorset1 default; colorset2 for the explicit multicolor preset/legacy `classic`. Compact and navigable compositions, scaffold and custom fragments, all native line/bar/table/gauge/waterfall/flow/network renderers, static/reduced-motion views, scenario/timeline/camera states and published SVGs. | Replaced unlimited hue generation with finite allowed token sequences. Quantized generated opaque tints and inverse text tokens. Preserved logical identity owners and required redundant cues when physical colors repeat. Added exact overrides and authored-fragment/final-SVG paint gates. Removed `color-mix`; halos use `fill-opacity` and shadows use canonical black alpha. Rebuilt both published compositions from their original briefs. |
| `diagram-composition` | Neutral/red colorset1 wrapper; colorset2 for explicitly colored concepts. Hub, matrix, taxonomy, cycle and boundary native SVG panels; composed SVG; PNG/PDF derivatives; imported producer panels. | Replaced canvas, frame, surface, ink, connector and native mark defaults. Semantic/native shape colors reject arbitrary tokens. The highlight audit accepts the exact canonical highlight belonging to a category, while retaining its previous tint reasoning for diagnostic comparisons. |
| `hierarchy-lens` | colorset2 because simultaneous categorical lenses and numeric color bands require the expanded labeled categories. Analytical SVG explorer, radial/organic/decision canvas views, SVG and PNG snapshots and saved offline HTML. | All categories, numeric bands, zero/missing tokens and inactive cells are finite tokens. Removed arbitrary RGB interpolation and inactive-cell RGB blends. Numeric legends/exports use stepped stops. Chrome, alpha-shadow base and URL-encoded favicons are canonical. Removed fill-color transitions that synthesize intermediate hues. Rebuilt all four published views, preserving the 1,200 records and numeric totals. Updated browser oracles to the new exact background, zero and missing-observation tokens. |
| `usefulcharts-style` | colorset2 for simultaneous labeled family, institution and timeline categories. Genealogy/lineage SVG, numeric timeline SVG, illustrated editorial SVG, outline panels, offline HTML, PNG/PDF derivatives and three published poster fixtures. | Canonical paper, frame, text, artwork and group defaults; exact category guard; distinct canonical group templates. Rebuilt all three posters with unchanged record/relationship semantics and retained original source images. |
| `hyperframes-explainer` | Existing colorset1 default; existing colorset2 gate requires an actual extra semantic color and explicit decision. Primitive HTML, mechanism assets, palette-checked flattened SVG imports, preview/contact sheets and MP4. | Existing role palettes, primitive authoring and imported mark mapping were already exact. No renderer modification was required. Confirmed deterministic gates, isolated preflight/build and actual browser paints. |
| `video` | colorset1 canvas/connectors; colorset2 for the category-rich AI concept gallery. Mixed SVG/GIF/raster/HTML/video compositor, connector/signal overlays, browser MP4, Slidev recording and transition wrappers, gallery SVG/HTML and contact sheets. | Canonical canvas/connector templates and runtime exact-token guards. Replaced authored animated RGB interpolation in the gallery with finite colorset2 quantization. Added active-set metadata. Preserved original media pixels. |
| `manim-svg-video` | colorset1 default wrapper, with exact colorset2 overrides available. Replacement/mosaic scenes, vector/raster SVG imports, labels/placeholders, manifests and raw/exact-duration MP4. | Canonical title, tile, label and failure defaults; runtime wrapper-color guard. Verified generated scenes and a real short labeled MP4. |

The palette gate checks actual authored content rather than an unused declaration. Source SVG geometry and numerical semantics were preserved during regeneration. Category colors were reassigned explicitly where nearest-color migration would have merged distinct categories. A finite palette cannot provide arbitrarily many unique physical colors; logical identity aliases still remain stable, and direct labels/shape/dash/cue distinctions carry identity beyond the palette's capacity.

## Source fidelity boundaries

Source-preserved media is a separate, narrow output scope. It cannot establish full-image palette compliance. Every changed skill routes through its in-bundle `references/palette-policy.md` before authoring/composition.

- In synchronized custom fragments, only embedded raster image payloads may retain original pixels. The fragment's SVG paints, labels and wrapper remain checked.
- In diagram compositions, an original imported panel is the nested `svg[data-source=<panel-id>]` subtree. Generated native panels, titles, frames and cross-panel connectors remain checked.
- In posters, original portrait/object JPEGs, the historical Milner map JPEG and source illustration PNGs retain their image payloads. Authored map geometry/category fills, icons, insets, borders and labels remain checked.
- In mixed video, original producer-owned GIF/raster/HTML/Slidev/video content and the gallery's Wikimedia globe/source PNGs retain their source pixels. Authored stage/chrome/connectors/signals and gallery SVG marks remain checked.
- In Manim, the source loaded through `SVGMobject` or `ImageMobject` remains producer-owned. Every wrapper/title/tile/label/placeholder paint is checked.

To claim that an entire composition fits one colorset, prepare an explicitly restyled producer asset before composition. Do not silently recolor factual imagery. Browser antialiasing, alpha, blur and video compression can introduce intermediate display pixels; this audit verifies base authored paints and exact canvas cells instead of claiming that every encoded MP4 pixel equals a token.

## Deterministic and browser evidence

Commands and environment values are reproduced in the JSON inventory. Latest pertinent results:

- Synchronized SVG tools: 80 tests; theme contract: 13; real compiler/composer theme fixtures: 6; actual dark/tinted text-pair browser fixtures: 3. The replacement fixture verifies that an off-palette authored fragment is rejected atomically with JSON diagnostics.
- Diagram composition: 24 composition tests, 13 native-panel tests, 8 shared-color tests and 21 connector-quality tests.
- Hierarchy: 21 builder tests and 11 decision tests. Published radial/organic/decision browser audits each passed for 1,200 records. The decision audit retained all 54 pixel checks, playback prefix/next/back/play semantics, missing-versus-zero checks, source ownership, exports, edited rules and deterministic restore. The isolated 120-record decision output also passed the independent browser audit.
- Poster bundle: 243 tests passed with the declared scientific, Playwright and Pillow dependencies. Rebuilt posters contain 561/141/50 nodes respectively and no node or connector-node collisions. Existing general edge crossings remain disclosed; this pass changes palette behavior, not the underlying editorial layout.
- HyperFrames: 45 deterministic tests passed; renderer unchanged. Isolated starter preflight/build and six actual browser times passed.
- Video: 13 scene-contract tests passed, including a real mixed-media MP4 render and validation.
- Manim: real SVG vector import and labeled wrapper render passed. `ffprobe` reported 640Ã—360, 5 fps, 15 frames and exactly 3.000000 seconds. The renderer reported unsupported SVG text import; that pre-existing limitation is retained rather than hidden.
- Independent authored-paint audit passed 147 states/exports: all four hierarchy views and every lens/scope/scale, analytical/pixel SVG exports, both composition scenario sets, three poster SVGs, every AI concept at seven times and the HyperFrames starter at six times. There were no off-palette paints or browser errors. Five configurable public entry points also rejected `#123456`.
- The root's stronger colorset checker passed both regenerated composition SVGs explicitly as colorset1 and the illustrated atlas explicitly as colorset2, with zero findings.
- An expanded gallery CSS check found an old navy shadow in the composition index. Its shadow base now uses canonical `#333e48`, its keyboard focus outline uses `#9e1b32`, and gallery metadata explicitly selects colorset2 for the blue navigation links. The source checker passed with zero findings. This fixture-only correction leaves every strict runtime payload digest unchanged.
- Independent support QA passed all 54 desktop/mobile initial, hover and keyboard-focus states across six final resource previews, the composition gallery, the generated main Pages index and the direct regenerated Destockd QA file. Article-boundary checks confirm that the corrected missing-preview placeholder stays inside its mobile card. Four pixel/dither images also fit exact token sets; the GIF source passed colorset1 and its decoded output retained 20 distinct frames in two seconds. The compact evidence is [support-browser-20261002.json](support-browser-20261002.json); original failures and screenshots remain under ignored project artifacts.

Local screenshots, SVG snapshots, JSON reports, dependencies and media remain under ignored `projects/compositions-colorset-audit/artifacts/`. The actual Playwright screenshots were visually reviewed: hierarchy chrome/heat bands, compact composition, illustrated poster and Manim labeled wrapper remained usable. Normal native SVG imports still require the documented fidelity review.

## Isolated forward contracts

These are development command/render contracts and independent output checks, not sealed holdouts or a universal perceptual-quality score. The harness used runtime payloads, disabled ambient discovery/context, excluded `assets/examples/`, required exact requested paths and verified unchanged copied bundles.

| Skill | Final strict run | Observed model | Result |
| --- | --- | --- | --- |
| `compose-synchronized-svg` | `colorset-compose-synchronized-svg-20261002-8` | `gpt-5.6-luna` | Pass: compiler, composer, static contract, exact SVG/JSON outputs and healthy runtime surface. |
| `diagram-composition` | `colorset-diagram-composition-20261002-2` | `gpt-5.6-luna` | Pass: native panel generation, composition, exact outputs and browser audit. |
| `hierarchy-lens` | `colorset-hierarchy-lens-20261002-6` | `gpt-5.6-luna` | Pass: shared synthetic source, decision policy and both exact HTML outputs. Independent browser checks cover the output. |
| `usefulcharts-style` | `colorset-usefulcharts-style-20261002-4` | `gpt-5.6-luna` | Pass: unchanged starter records/relationships, exact SVG/HTML/render report and palette note. |
| `hyperframes-explainer` | `colorset-hyperframes-explainer-20261002-3` | `gpt-6-luna` | Pass: exact starter, preflight and project build outputs. |
| `video` | `colorset-video-20261002-2` | `gpt-5.6-luna` | Pass: canonical scene contract and validation outputs. |
| `manim-svg-video` | `colorset-manim-svg-video-20261002-2` | `gpt-5.6-luna` | Pass: generated scene/manifest; independent real MP4 check follows. |

For each run, the JSON inventory contains the copied payload digest, exact artifact hashes, gate results and the trace-summary command with `--require-model`, `--fail-on-invalid-json` and `--fail-on-tool-error`. The repeated final validations retained original failures and only followed an identified implementation, fixture, provider or task-contract repair.

Spark was attempted for `video` and `manim-svg-video` first. The provider rejected `gpt-5.3-codex-spark` as unsupported for this ChatGPT account before any tool call. The retained run IDs are `colorset-video-20261002-1` and `colorset-manim-svg-video-20261002-1`. The root agent authorized `gpt-5.6-luna` for the replacement tests and must record these new model exceptions in `SKILLS.md`. The other models use previously recorded exceptions.

The earlier composition run7 passed its original payload. The root's final exact-byte audit found that one test fixture file changed afterward; run8 was repeated with the current frozen bundle and accepted digest `55c47702247f003387a31d5a1b83f2fd1524c2e230d51bcbd7e5d2ef87a1f633`. Its five exact outputs, strict event/model/read-surface gates and payload integrity passed; the final SVG independently passed colorset1 with zero findings.

Earlier failures remain evidence: hierarchy ad hoc tool probes, an invented `usage.md` read and stale dark/zero/missing pixel audit expectations; a HyperFrames forbidden parent harness-manifest read; and one composition harness invocation whose expected flags named different files than its prompt. They are classified in the JSON inventory. Fixture/guard development also exposed a finite-palette identity assumption, collapsed category test colors, missing broad-suite dependencies and a newly added fragment case's diagnostic expectation; each was corrected before the final corresponding checks.

## Release handoff and limits

Republish the existing `compose-synchronized-svg`, `hierarchy-lens`, `usefulcharts-style` and `ai-concept-videos` example sets after the root's final Pages build and validation. Preserve their stable pattern/item identities. No new example-set catalog entry is needed.

No MP4 files ship in the gallery's source directory. If a separate external media release ships old encoded gallery videos, regenerate them from the corrected renderer during that release. Source photographs/videos remain source-preserved. HyperFrames encoding was not repeated because its renderer and exact-palette implementation were unchanged; this pass reran deterministic and actual generated-browser evidence. Manim's SVG text/CSS/SMIL limitation remains documented and requires outlined text or its raster import path where fidelity demands it.

Final repository validators, runtime payload checks, installation synchronization, authorized source publication and Pages workflow verification are pending at the root handoff. Existing backlog statuses outside this palette-specific evidence should remain honest; these contracts do not resolve unrelated release work.
