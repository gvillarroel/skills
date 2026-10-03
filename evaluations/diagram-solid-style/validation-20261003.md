# Diagram renderer solid style validation

Date: 2026-10-03. Scope: Mermaid, PlantUML colorset renderer, ECharts animated SVG,
Slidev ECharts, Slidev Anime.js, and Slidev quality audit. This is supplementary
style regression coverage, not a replacement for each bundle's prior functional
evaluation matrix. The [sealed evidence](validation-20261003.json) records prompt,
current runtime payload, and exact output hashes, selected runs, read paths, and
retained failed attempts.

The six runtime bundles now start filled categories with opaque solid palette
colors and zero decorative outlines. Allocation exhausts the exact usable
sequence, excluding the actual canvas, before deterministic outline overflow.
Inside text uses the black or white value with greater WCAG relative-luminance
contrast. Meaningful chart lines, relationship arrows, class compartments,
source assets, explicit user style, and keyboard focus remain distinct exceptions.

## Current isolated trials

All selected trials use the runtime profile, `--mode json --strict`, and the
existing documented model exception `openai-codex/gpt-5.6-luna`. All six have valid
event JSON, the required observed model, zero tool errors, exact nonempty outputs,
an unchanged copied bundle, and a payload digest equal to the current source.
Manual inspection found no examples, sibling skill, harness metadata, or ancestor
repository reads in the selected trials.

| Bundle | Selected run suffix | Exact required outputs | Result |
| --- | --- | --- | --- |
| mermaid | mermaid-luna-12 | source.mmd; style-report.json; solid-styles.json; native-check.json; native-family-tests.log | Pass |
| plantuml-colorset-renderer | plantuml-colorset-renderer-luna-4 | rendered/svg/pipeline.svg; render-report.json; solid-styles.json | Pass |
| echarts-animated-svg | echarts-animated-svg-luna-9 | styles.json; chart.static.svg; chart.animated.svg; chart-validation.json; canvas-check.json; advanced-check.json | Pass |
| slidev-echarts | slidev-echarts-luna-12 | styles.json; option.json; integration.md; canvas-check.json; advanced-check.json | Pass |
| slidev-animejs | slidev-animejs-luna-4 | deck/assets/animated-svg/stagger-dashboard.svg; style-review.json; integration.md | Pass |
| slidev-quality-audit | slidev-quality-audit-luna-3 | style-audit-plan.json; integration.md | Pass |

Run IDs prepend `20261003-diagram-solid-` to the suffix above. Prompts are the
adjacent `mermaid-prompt.md`, `plantuml-prompt.md`, `echarts-prompt.md`,
`slidev-echarts-prompt.md`, `slidev-animejs-prompt.md`, and
`slidev-quality-prompt.md` files. Reproduce a trial with:

```powershell
uv run --script scripts/run-pi-skill-eval.py <bundle> --prompt-file evaluations/diagram-solid-style/<prompt>.md --mode json --strict --model openai-codex/gpt-5.6-luna --run-id <new-run-id> --expect-output <first-output> --expect-output <each-additional-output>
uv run --script scripts/summarize-pi-json-events.py evaluations/runs/<run-id>/events.jsonl --require-model gpt-5.6-luna --fail-on-invalid-json --fail-on-tool-error
uv run --script projects/diagram-solid-style/scripts/capture-validation-evidence.py
```

Earlier failures remain under `evaluations/runs/`. They include unnecessary
dependency probing, generated script escaping/syntax errors, wrong helper
argument signatures, an omitted check-command colorset, guessed capacities,
expecting the manifest-only overflow flag in ECharts itemStyle, and forbidden
harness metadata reads. Anime.js Luna3 passed automated strict checks but was
rejected manually because ancestor Git status/diff exposed repository context;
Luna4 replaced it. Prompts now state public API signatures and the workspace
boundary. Mermaid Luna8 incorrectly inspected XML presentation attributes instead of effective inline CSS; Slidev ECharts Luna9 required redundant per-item outside-label colors instead of inherited series label colors. Slidev ECharts Luna10 also initially used the wrong copied template path and assumed per-edge rather than inherited series lineStyle. These runs recovered, but were rejected for their initial tool errors and replaced by fresh strict trials. Mermaid Luna10 also guessed a hyphenated paint key and wrote `exact-native-family-tests.log` instead of the literal required filename; it is retained as failed and the prompt now states the dictionary keys and literal filename. Mermaid Luna11 produced all correct outputs and passed the portable 17 tests, but its first synthetic script had inconsistent variable capitalization; its recovered result is retained as failed for the initial tool error. Luna12 is a fresh unchanged-prompt/source trial. No failed run was relabeled as successful.

## Deterministic and visual evidence

`uv run --script projects/diagram-solid-style/scripts/test-solid-style.py` passes
four regression cases spanning all Python allocators, both independent ECharts
helpers, palette/canvas combinations, exact initial sequences, inside contrast,
overflow, named series containers, ID-only categories, Mermaid native Kanban and
section capacity, idempotent native finishing, and untouched connector paint.
This caught and repaired actual canvas exclusion and named series containers consuming node category slots. All Python/JavaScript overflow pools now use contrasting allowed border colors (at least 3:1 against the fill), cycle color/dash/width deterministically, and keep widths within 1Ã¢â‚¬â€œ3 px even at indices 256 and 5000. Capacity is finite; when combinations repeat, splitting or secondary labels is required.

`node projects/diagram-solid-style/scripts/test-echarts-rendered.mjs` passes fourteen actual ECharts SVG SSR cases across both self-contained helpers. The rendered tests check black pie/funnel outer text, white graph inside text without native halo, black text on explicit white label backing, and inherited label position with per-datum overrides. Translucent RGBA/eight-digit canvases use the actual composite over a white host fallback for outer text without replacing the requested paint. A different embedding host must supply its effective opaque background because external host pixels are unavailable to the helper. Additional assertions check opaque RGBA/eight-digit canvas aliases, stable identity mapping under reorder, the public categoryOrder registry across changing subsets, caller-authored mappings, the seventeenth colorset1 series using overflow, and preserved helper-produced overflow styles. Independent review reproduced these defects before the repair and rechecked the same cases after it. Rich-label backing and authored interaction-state labels use their effective paint, while meaningful connector lineStyle is retained.

Mermaid's regenerated maximum-complexity gallery has 31 families, 62 stable
patterns, and 62 static/animated pairs. `validate_gallery.py` passes all pairs;
`test_gallery.py` passes eight tests. Every one of the 124 generated SVGs is
already LF, with raw and LF-normalized bytes matching the manifest SHA-256.
The final manifest hash is
`2cfb39eb8ba41884f9c0de504d12e76fb15ac54a61c625cce0d0224b331919df`.
Native renderer builds encountered transient Windows file-open errors; the
bounded native writer and recovery script completed normalized native pairs.
Native pie wedges are opaque with no rim; native Kanban cards are filled solids.

Native family finishing now covers C4 entity stereotypes/captions, class-authored
Block/State label backings, Kanban, Swimlane headers, Journey beyond seven slots,
Gantt status fills, opaque Treemap allocation through full capacity then overflow,
ZenUML participant/occurrence columns, Railroad terminals, Wardley component
silhouettes, and Cynefin item cards. The portable native suite passes 17 tests.
Meaningful cylinder seams, compartment lines, lifelines, procurement/emotion
symbols, critical-status boundaries, native icons, and connectors retain geometry.

The computed-paint audit covers all 62 static and 62 animated native fixtures at
static, settled, and mid-reveal states (186 states), with zero unexplained rims
and zero contrast findings. Its label-center `isPointInFill` checks include
closed filled paths and partial containment, actual RGBA/fill-opacity layers
composited in paint order over canvas, and sequence numbers paired with their
referenced marker circles even though marker definitions have zero DOM bounds.
CSS opacity reveal targets and ancestors are explicitly classified; hidden and
partial reveal counts are recorded separately from meaningful paint opacity.
Native Venn/control-region translucency, curves, geometry, and source assets
remain intact. Sequence pale-region/stick-figure captions become black, numeric
marker labels use their actual backing, Cynefin center/edge captions use the
actual domain or ellipse, and Radar legend swatches are opaque and borderless
while retaining their curve identity. A separate reviewer accepted all 62 static
fixtures at 14:58:13 UTC with stable hashes, zero contrast/outside-actor/unexplained
rim findings, and 55 retained filled rims classified as explicit overflow or
meaningful Journey/Gantt/Wardley geometry. Updated Sequence, Venn, Cynefin, and
Radar screenshots were inspected independently, followed by a fresh 12-card
contact sheet and C4/deployment thumbnails.

```powershell
uv run --script projects/diagram-solid-style/scripts/finish-mermaid-gallery.py
uv run --script skills/mermaid/scripts/test_native_solid.py
node projects/diagram-solid-style/scripts/scan-mermaid-native.mjs
uv run --script skills/mermaid/assets/examples/mermaid-max-complexity/scripts/validate_gallery.py
uv run --script skills/mermaid/assets/examples/mermaid-max-complexity/scripts/test_gallery.py
uv run --script skills/mermaid/assets/examples/mermaid-max-elements/scripts/test_max_elements.py
```

PlantUML's two published galleries contain 54 SVGs and two Ditaa PNGs. Each
report covers 29 fixture results and 28 rendered diagrams, with chronology's
previously declared unavailable outcome retained. Both reports pass the render
and frozen coverage validators. Internal class compartments, cylinder details,
and activity connectors are visible after decorative silhouette removal.

```powershell
uv run --script skills/plantuml-colorset-renderer/scripts/validate_plantuml_render_report.py --report skills/plantuml-colorset-renderer/assets/examples/plantuml-colorset-renderer/render-report.json --output skills/plantuml-colorset-renderer/assets/examples/plantuml-colorset-renderer --colorset colorset2 --expected-diagrams 28 --coverage-manifest skills/plantuml-colorset-renderer/references/diagram-types.json
uv run --script skills/plantuml-colorset-renderer/scripts/validate_plantuml_render_report.py --report skills/plantuml-colorset-renderer/assets/examples/plantuml-colorset-renderer-cs1/render-report.json --output skills/plantuml-colorset-renderer/assets/examples/plantuml-colorset-renderer-cs1 --colorset colorset1 --expected-diagrams 28 --coverage-manifest skills/plantuml-colorset-renderer/references/diagram-types.json
```

ECharts gallery `npm run build` and `npm run verify`, run from
`skills/echarts-animated-svg/assets/examples/echarts-animated-svg`, pass all 43
cards. The final screenshot was inspected, including filled tree nodes,
saturated boxplots, borderless controls, and hierarchy labels. Slidev ECharts
`npm run build:html` and Anime.js `npm run export:html`, run from their respective
example deck directories, succeed. The existing Rolldown dependency annotation
warnings remain informational.

The final actual deck audits cover 36 ECharts slides/129 visual states with zero
errors and two existing density warnings on slide 31, and 30 Anime.js slides/93
visual states with zero findings. Initial contrast warnings were repaired in
the authored chip, panel, and stepped animation text styles.

```powershell
npx tsx skills/slidev-quality-audit/scripts/audit-slidev-quality.ts --deck skills/slidev-echarts/assets/examples/slidev-echarts --out projects/diagram-solid-style/artifacts/slidev-echarts-quality-final-4 --colorset colorset2 --screenshots issues --dwell 800 --click-dwell 400
npx tsx skills/slidev-quality-audit/scripts/audit-slidev-quality.ts --deck skills/slidev-animejs/assets/examples/slidev-animejs --out projects/diagram-solid-style/artifacts/slidev-animejs-quality-3 --colorset colorset2 --screenshots issues
npx tsx projects/diagram-solid-style/scripts/capture-native-review.ts
```

The native contact sheet loads 12 SVG images with no card overflow and was
inspected after fonts and two animation frames. A separate four-slide marked
regression deck demonstrates that the auditor rejects all three premature
outlines, accepts the initial solid slide and explicit meaningful boundaries,
and accepts a marked outline only after all 36 colorset2 solids are used. The
large capacity grid has one expected density warning. The first temporary-deck
attempt lacked the existing Vite dependency prebundle setting; a second had
insufficient Markdown slide separation. Those local attempts remain in artifacts;
the third has the correct four-slide structure and expected rule outcomes.

## Limits and publication handoff

The isolated tests are focused style/API exercises. The quality-audit trial
plans a run; the actual full decks and marked regression supply browser evidence.
The automatic outline rule sees visible marked DOM categories only. Hidden or
paginated categories require allocation-manifest checks, and Canvas/source
pixels require separate option/export review. Transparency in meaningful Venn
overlaps and data connections is retained. Existing supplied SVG/source style
fidelity remains explicit rather than being silently flattened.

Root owns global palette metadata, backlog notes, repository gates, local skill
synchronization, Pages build, commit/push, and public workflow verification. All
published pattern IDs and links in this group remain stable.
