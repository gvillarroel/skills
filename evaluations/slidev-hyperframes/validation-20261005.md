# Slidev HyperFrames integration validation — 2026-10-05

Status: done. This scoped update adds reusable HyperFrames support to `slidev-animejs` and `slidev-echarts`. The independent explainer CLI is unchanged.

## User-visible scope

Both owning bundles contain official player/core 0.8.134, local GSAP 3.14.2, exact colorsets, licensed Open Sans, a pure seekable scene and the same-model SVG fallback. Native clicks select seconds; backward clicks restore state, inactive scenes pause, and explicit exports seek deterministically. No sibling skill is required.

The reusable HyperframePreview owns accessible Play/Pause controls, leave cleanup and a separate 48-pixel control budget. The starter generator supplies three slides, editable JSON choreography/content/layout, native collection cells, package/Vite configuration and a review that reports only checks performed. Mermaid uses that same JSON colorset and the existing shared diagram defaults. Identical resources are accepted; conflicts are preflighted before writes.

Live scenes require HTTP. Single-file direct-open HTML uses the deterministic SVG fallback with an inline local font and no live controls. Custom offline scenes require a separately qualified poster/fallback. Bundled Open Sans covers Latin; preserve supplied custom composition styles.

## Runtime and compatibility

The frozen core passes 32 native/deterministic cases, including actual geometry/readouts, forward/back seeks, palettes, lifecycle, public seek, fonts, compact labels, cleanup, unique fallback IDs, duration clamping and file fallback. Root observes 0/20/70 percent and actual fill heights 0/33.6/117.6 at 0/4/9 seconds, with Open Sans and colorset2 blue inside the iframe.

An unmodified raw paused-GSAP scene from explainer CLI 0.8.111 passes 9/4/0/9-second probes, original numerical/fill checks and font/style preservation. This qualifies that scene, not every arbitrary external composition.

Clean current-transitive installation fails generated CSS minification with Vite 8.3.2 / UnoCSS 66.10.5 / Lightning CSS 1.33.0. A Lightning-only downgrade also fails. The esbuild diagnostic warns about malformed CSS and is not promoted. The qualified starter uses Vite 8.0.16 / UnoCSS 66.7.2 / Lightning CSS 1.32.0, Slidev 52.16.0, Vue 3.5.38, theme-default 0.25.0 and singlefile 2.3.3. Normal and direct-open builds are checked independently without source repair.

## Strict isolated forward tests

Both fresh own-skill Spark controls fail before tools because this ChatGPT-account provider does not support Spark. Retain them. The recorded scoped model exception is `openai-codex/gpt-5.6-sol`; strict JSON, observed model, exact outputs, clean read surface, immutable payload, zero tool errors and native/manual gates remain unchanged.

Each release cohort has one contract and three fresh naturalistic repetitions per owner. Acceptance requires the contract and at least two naturalistic cases to pass jointly. Authors do not install/build. The grader installs only declared dependencies in disposable copies and checks real marks, glyphs, geometry, fonts, clicks, controls, lifecycle, reduced motion and file fallback. Naturalistic prompts prescribe no implementation recipe; outputs are never repaired.

- Epoch 1 retains six attempts: four strict passes, two genuine edit-tool failures, and an Anime contract native failure where transformed screen measurements became logical CSS height and the player intercepted Play. The final two repetitions were not launched after the native failure.
- Epoch 2 retains eight attempts and 368 native cases. ECharts passes all four strict cases and its contract plus two joint naturalistic cases under the original grader. Anime has three genuine ambiguous edit-tool failures including the contract, so the cohort fails despite complete visually correct outputs. A third ECharts width result is a separately retained evaluator boundary defect.
- Epoch 3 adds reusable preview ownership and a deterministic starter to reduce repeated mutable adapter work. The final exact-byte generator golden passes clean install, both builds, 46 native cases and manual review. The reusable starter diagnostic passes 26 cases, including both Mermaid palettes and explicit overrides; all 13 generator regression groups pass. [The sealed final cohort](cohort-epoch-3-summary.json) passes all eight strict, native, data and manual gates jointly. Each owner passes one contract and 3/3 naturalistic repetitions; the eight decks pass 368 native cases and 24 clean install/build/build:html commands, with zero errors, remote requests or source changes. All 160 frozen source entries match. Source publication and the complete remote HyperFrames suite pass.

Evaluator corrections are independently qualified against collection, CSS-grid and direct-engine positives and a fixed 800-pixel negative that must reject the actual 680-pixel boundary. Earlier evaluators/matrices remain retained. An auto-height nested article whose glyphs remain inside the real card is distinguished from descendants that actually clip. A disposable dependency-tree retention mistake exhausted disk; all author traces are audited and contain no ENOSPC errors. Only verified completed project dependency trees were removed after retaining source, locks, reports and builds. No correction waives a strict or native failure.

## Fixtures and publication

Stable routes remain ECharts 42/43/44 and Anime.js 36/37/38 for live, cells and export. The original local frozen fixture passes 41 states and both catalog cards; existing layouts pass 188 states and 120 ordered traversals. Root manually reviews the retained screenshots. The final Preview fixture passes 45 states (42 HTTP plus three local-file cases), two catalog cards and six route captures. All eight retained final captures match the preliminary accepted PNG bytes exactly. The final remote suite passes, as detailed below.

Pages publication succeeded for source commit `21242fb1c88fd931f4aff164ad813baf8fa2b2a7` in [run 37362428891](https://github.com/gvillarroel/skills/actions/runs/37362428891). The unchanged project verifier `951318fd9706ac1c504ea6369f1103c534700c122e5ecbf25fd70ed00b254342` passed all **42 remote HTTP states**, both canonical index cards and the six stable routes on 2026-10-05 at 19:22 UTC. It verified actual official-player readiness, loaded local fonts, cue times 0/3/6/9 and native backward seeks, actual valve/tank/parcel geometry, real Play/Pause, inactive pause and paused return, opaque black/white text, exact palette paint/contrast, complete column/masonry pages, static 0/9 snapshots and logical sizing at 1280/980 viewports. No unexpected console errors or external scene requests occurred; 10 expected headless Wake Lock denials were retained. The three direct-file cases are a separate accepted local proof and are not counted as remote states.

The public index, six logical routes and 14 local scene/vendor/font/palette assets returned HTTP 200. All 14 assets matched canonical bytes, including colorsets `b557cb50…`, Open Sans `d8e4fe04…`, HyperFrames core `767f9ae1…` and GSAP `c174bfce…`. Response headers, ETags, last-modified values and cache evidence are retained; observed cache-control was `max-age=600` with ages 0–7 seconds. All six public PNGs are byte identical to the accepted final local captures, so the existing exact-pixel manual reviews carry forward with no visual differences.

Public routes remain [ECharts live](https://gvillarroel.github.io/skills/examples/slidev-echarts/#/42), [cells](https://gvillarroel.github.io/skills/examples/slidev-echarts/#/43) and [export](https://gvillarroel.github.io/skills/examples/slidev-echarts/#/44), plus [Anime.js live](https://gvillarroel.github.io/skills/examples/slidev-animejs/#/36), [cells](https://gvillarroel.github.io/skills/examples/slidev-animejs/#/37) and [export](https://gvillarroel.github.io/skills/examples/slidev-animejs/#/38). Both owning sets are discoverable from the [main examples index](https://gvillarroel.github.io/skills/). Bulky proof, exact native states, HTTP/resource hashes and six captures are retained under `projects/slidev-hyperframes/artifacts/published-remote/`; the sealed public summary is `publication-proof.json`.

`node --experimental-strip-types projects/slidev-hyperframes/scripts/verify-hyperframes-examples.ts --base-url https://gvillarroel.github.io/skills/ --output projects/slidev-hyperframes/artifacts/published-remote`

## Reproduction and evidence

```text
uv run --script projects/slidev-hyperframes/scripts/test-hyperframes-check.py
uv run --script projects/slidev-hyperframes/scripts/test-hyperframes-scaffold.py
node --experimental-strip-types projects/slidev-hyperframes/scripts/verify-hyperframes.ts
uv run --script scripts/validate-pattern-ids.py
uv run --script scripts/validate-skills.py
uv run --script scripts/test-skill-independence.py
uv run --script scripts/check-repo-payload.py
```

Project verifiers declare confined dependencies and output locations in their headers. Frozen manifests record the strict Pi commands and exact artifact gates; recheck events with `summarize-pi-json-events.py --require-model gpt-5.6-sol --fail-on-invalid-json --fail-on-tool-error`.

Durable summaries, prompts, rejections and read-surface audits are retained beside this record. Bulky events are ignored under `evaluations/runs/`; native matrices, screenshots, locks, builds, evaluator snapshots and source seals are ignored under `projects/slidev-hyperframes/artifacts/`. Repository gates and local sync/check pass. Successful Pages publication and remote native verification also pass. Both owning backlog rows are done.

## Final source seal

[The epoch-three freeze](frozen-evaluation-epoch-3.json) seals 82 ECharts and 78 Anime runtime files, including SKILL.md and metadata. The 33 required integration/starter/layout/diagram resources per owner total 740,989 bytes. Root independently verifies all 66 recorded entries against canonical bytes. Resource profiles are `d96780b9240f5441f7cac43c3c33551142d437bab64b8b6dca4e0ceba960490d` and `a8a7e1d071928ef2ea853bdda76186959690115ba912889d0f35e8ccbbe81d84`. Preview is `be59982edd2dce2e1d7d89beeb09f7649351f50cb81501c27ed380f2c8865c40`; core remains `0b36b5c193e2819ca14c1a37f9f3703f6fe3cfa114631e13d37d742c2851387e`. The qualified evaluator is `dbda186e9e9ff69421c7482b8d02795a34753a52e48fe8f3ba7494a1cec10f29`.

Local synchronization refreshes 26 files and confirms all 10,375 canonical files match the repository-local installation, with bundle validation passing. Repository validators, payload, colorset (19), Pi harness (17), bundle (11), authoring (30), reviewer (32), Pages boundary (14), runtime/full bundle audit (68 bundles) and diagram-family coverage pass. The broad staged whitespace check reports only four sealed original prompt EOF blanks and copied upstream minified-vendor whitespace; preserve these exact frozen bytes. All authored changes outside those eight precisely identified paths pass the whitespace check. Unrelated gallery/project changes are excluded from staging.

One exact strict release command is:

```text
uv run --script scripts\run-pi-skill-eval.py slidev-animejs --prompt-file evaluations\slidev-hyperframes\prompts\animejs-contract-v3.md --model openai-codex/gpt-5.6-sol --run-id 20261005-slidev-hyperframes-animejs-sol-v3-contract --thinking high --mode json --strict --profile runtime --timeout-seconds 900 --expect-output deck/slides.md --expect-output deck/package.json --expect-output deck/components/HyperframeStory.vue --expect-output deck/data/hyperframes-story.json --expect-output deck/components/HyperframeSlide.vue --expect-output deck/lib/hyperframes.js --expect-output deck/public/hyperframes/starter.html --expect-output deck/public/hyperframes/scene.js --expect-output deliverables/hyperframes-review.md --expect-output-json-field deck/data/hyperframes-story.json::cueTimes=[0,4,9] --expect-output-json-field deck/data/hyperframes-story.json::exportTime=9 --expect-output-json-field deck/data/hyperframes-story.json::colorset=colorset1
```

Repeat with the owning naturalistic prompt for three fresh run IDs; the recorded cohort plan and summaries retain every attempted case. Use a new run ID rather than overwriting retained runs.

The final Preview public-ref diagnostic also confirms controls=false playback advances the real clock, Pause retains its time, and seek(9) produces the actual 70% state with zero errors. Root independently verifies all 66 staged integration resource entries against the exact final source manifest, so checkout/deployment will use the tested bytes.

## Public diagram continuity regression

After actual live scene/font readiness, same-document navigation ECharts 42 to Mermaid 37 and Anime.js 36 to Mermaid 31 preserves default colorset1 red bodies, white node text, black edge captions and loaded Open Sans. Each diagram passes all five labels and 68 individual nonspace glyph bounds with no clipping. Persistent host font registration remains connected. There are no unexpected console/page/network errors; two known headless Wake Lock denials remain separately recorded. The existing native Mermaid rounding tolerance is 1.5 px. Both captures are manually reviewed; root separately reviewed the exact public HyperFrames cell capture and six-capture parity. Compact proof and its confined replay script remain under `projects/slidev-hyperframes/artifacts/public-diagram-regression/`.

The documentation closeout changes only this record and SKILLS.md. Runtime resources, examples, prompts and evaluation outcomes remain identical to the validated and publicly verified source commit. All unrelated user gallery/project edits remain unstaged.
