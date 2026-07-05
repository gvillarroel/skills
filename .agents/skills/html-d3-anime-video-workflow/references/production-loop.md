# Production Loop

Use this reference for standalone HTML+D3+Anime.js video pipelines that are not Slidev decks.

## 1. Refresh Script Claims

- Recheck current facts before visual production when the script mentions products, pricing, plan limits, model support, security guidance, standards, or recent capabilities.
- Prefer primary sources and record the exact check date in production notes.
- Keep unstable claims conservative in the rendered video. Put exact live pricing or plan limits in notes unless the user explicitly asks for them on-screen.
- In isolated or forward-validation runs, treat prompt facts as the available source package when live research is not required. If the prompt gives exact paths, dates, facts, duration, aspect, or topic anchors, preserve them and proceed. Do not ask for optional preferences; choose conservative defaults and record non-blocking gaps in `missingFacts` or production notes.
- Asking for clarification is only appropriate when a required local source file is missing, the requested output path is unsafe or impossible to write, or the requested artifact cannot be produced by any available local tool. Missing style, audience, narration, or exact script details should not block a draft video when the prompt already asks for one.
- In isolated `pi` workspaces, read `../prompt.md` before choosing helper arguments. The prompt contract overrides script defaults, examples, and convenient scratch names. Producing a good video under a nearby directory still fails validation when `--expect-output` names different paths.

## 2. Design The Visual Metaphor Before Reuse

- Start with the concept's causal mechanic, not with the last successful scene or the nearest gallery component.
- For broader video requests, read `html-video-orchestration-patterns.md` before the metaphor pass so the source package, storyboard contract, media plan, and validation gates are clear before scene code begins.
- Read `visual-metaphor-design.md` for new concept videos, weak beats, or feedback that the video copied an old pattern without explaining the new idea.
- Read `scene-pattern-recipes.md` after a metaphor is chosen and before reusing an approved scene, shared helper, or example module.
- For Metro, complex dynamic, low-text, or "not following the design" feedback, run `scripts/plan_metro_pattern_mix.py` before accepting a scaffold or wrapper output. Treat its `selected.helperPattern` as the helper scaffold only; the design must also use the selected density patterns, functional zones, camera path, semantic motion systems, transition contracts, `reusableD3PatternIds`, and anti-pattern risks.
- For a multi-video Metro series after design-rejection feedback, run `scripts/build_metro_series_contract_prompts.py` before rendering. Use its generated per-video prompts for isolated `pi` runs so every module requires render-state, full Metro audit suite, encoded-MP4 composition, and semantic-density reports. Do not rely on hand-written prompts that only require `metro-style-audit.json`; they can skip the MP4 gate that catches slide-like delivered videos.
- Generate multiple candidate metaphors and reject the weaker ones before writing scene code.
- Define a local visual vocabulary: which shapes are nouns, which motions are verbs, and which colors or state changes are adjectives.
- Reuse a previous scene pattern only when the repeated marks keep the same semantic role. Reuse helpers freely, but do not reuse a matrix, meter, loop, or machine box as a generic placeholder.
- Reuse a previous motion pattern only when the motion keeps the same semantic role. If a repeated sweep, pulse, cursor, or ambient layer exists only to avoid a static frame, replace it with each scene's own visual verb.
- The selected metaphor should let a viewer infer the mechanic with narration muted. If it cannot, improve the metaphor before adding labels or legends.

## 3. Storyboard Mechanisms Before Text

- Start each beat with the visible mechanism: what enters, splits, moves, stacks, ranks, branches, blocks, transforms, repeats, or exits.
- For narrated explainers, render no visible explanatory text by default. Avoid titles, bullets, labels, captions, legends, and callouts unless the user explicitly asks for on-screen words.
- Do not add progress, duration, timeline, chapter, watermark, or status components to the rendered frame unless they are part of the concept model itself.
- For every scene, identify the simultaneous animation systems that will carry meaning, such as moving tokens, changing ranks, growing meters, trace lines, highlights, feedback loops, or state transitions.
- During review, flag any frame where reading text is required or where text appears as a crutch. Replace it with motion, geometry, color, ordering, or cause/effect sequencing.

Before coding a beat, answer or ask concise visual preference questions:

- What mechanism must the viewer see: splitting, ranking, sampling, routing, accumulation, capacity, or transformation?
- What shape metaphor should carry the idea: matrix, wheel, queue, stack, network, path, meter, grid, or layered machine?
- What can narration say so the frame can omit it?
- Which on-screen words are data or unavoidable labels, and which are explanatory text that should be removed?
- Which existing D3/gallery/example component can express the chosen metaphor after it is selected?
- What must the first and last frame match if this beat touches an adjacent approved segment?

For layout and motion:

- Define layout regions first, such as full-height rows, horizontal columns, or quadrants. Then scale objects to those regions instead of placing unrelated coordinates by hand.
- Keep peer objects on shared baselines with matching visual weight when the scene compares or connects them.
- For silent diagram videos that need on-screen labels, render scene titles and critical SVG labels in a top text layer after mechanisms, and use a `paint-order: stroke` halo or equivalent so rays, routes, particles, and compression cannot make them unreadable. Inspect full-size frames where moving marks cross labels.
- Bind label and callout opacity to the mechanism they name. A route, conversion, or output label should not become fully visible before the route, conversion, or output itself is visible.
- Treat approved recurring marks as visual-language components, not redraw suggestions. When a model box, matrix, roulette, meter, or other semantic object is approved and will appear in another beat, extract it into a shared helper before the next segment render. Remove local variants that change geometry, color, internal placement, or activation style unless the semantic role intentionally changes.
- Prefer direct mechanical paths over decorative curves. If a guide line accompanies a moving object, make the line share the same source, target, timing, and fade as the object.
- Avoid persistent motion trails when the moving object already explains the transformation. A trail must be a semantic mark, not residue; if it survives arrival or shows up as a visible streak in contact sheets, remove it or fade it to zero before landing.
- For multi-scene composition tests, vary D3 structures by scene job and keep continuity through palette, typography, spacing, token identity, and named motion verbs. Use network routing, branch splitting, bar filling, radial completion, or another scene-local mechanism instead of a shared decorative background layer.
- When a model or processor box becomes active, animate the internal mechanism instead of adding a generic glow. For neural-network metaphors, adapt an existing D3 MLP activation pattern: keep the primary label centered, keep the network small and secondary, pulse nodes and links by layer, and use a soft translucent brand color so activation reads as work without competing with the main concept.
- For model-as-enclosure scenes, draw flow objects that enter or exit the model on a lower layer than the model box, border, label, and internal activation. The enclosing box should hide tokens while they are inside it, so output appears from the model boundary rather than floating over the box. Inspect full-size frames, not only contact sheets, for z-order leaks.
- Keep exact numeric readouts, prices, or cost totals in fixed secondary panels aligned to their reference table. Let meters, ticks, and accumulated marks carry the mechanic; avoid attaching precise numbers to moving dots or tokens unless the number itself is the object being tracked.
- Keep legends compact and inside the semantic region of the mark they explain. Avoid adding a legend when color or order can explain the state directly.
- For repeated loops, make the same data object visibly re-enter the system and append to the accumulated state. Add a short pulse on the newly occupied state cell after append; this often explains growth more clearly than a label.
- In probability or ranking scenes, show relative magnitude with bars, wedges, ordering, or area before showing numbers. Remove percentages when narration can explain probability and the visual ordering is unambiguous.

For tokenizer or context-window scenes:

- Render prompt text as token-owned groups from the first frame. Each token group owns its text node, invisible or low-emphasis rectangle, and later visual states. Do not draw rectangles over a separate sentence; text measurement and glyph overhangs will drift.
- Use explicit inter-token spacing and measured token widths. Do not rely on trailing spaces in SVG text for token boundaries.
- Show the mechanical chain as token boxes -> numeric ID boxes -> colored square cells. Make each element keep identity through the transformation.
- Use a square neutral context-window matrix for capacity. Fill occupied cells left-to-right, top-to-bottom in concept order, and avoid decorative outer borders unless the border itself is part of the model.

## 4. Build One Data Model

Create one structured module for:

- video IDs and titles
- exact duration
- beat start/end times
- scene headlines, bullets, and callouts
- references and research notes
- visual metrics and palette tokens
- output filenames

For input-driven videos, create a source package first and point the data model at it. Website/product packages should freeze screenshots, visible text, brand tokens, and selected assets. PR packages should freeze metadata, files, selected diff hunks, and contributor notes. Topic explainers should keep the verbatim source text and checked facts. Music-driven pieces should keep the canonical audio map. Existing footage workflows should keep transcript, keep-out, and overlay timing data. Do not let final render code fetch or infer these facts live.

Avoid scattering script text across HTML, renderer code, and export scripts.

For long videos, keep one orchestrating entry point but split implementation by approved beat or substantial subscene. Use shared modules for palette tokens, timing helpers, token geometry, matrix geometry, and layout regions. New work should usually start in a new beat file once the previous beat is approved, so late-video iteration does not require editing one oversized renderer.

## 5. Use Deterministic Timestamp Rendering

For final export, expose a browser callable function similar to:

```js
window.renderConceptFrame = (conceptId, seconds, options = {}) => {
  // update DOM text
  // redraw D3 SVG from the current timestamp
  // return a small validation state
}
```

Make the rendered frame depend on `conceptId` and `seconds`, not wall-clock animation state. This makes rerenders, reviews, and individual frame debugging repeatable.

Use Anime.js for live preview cues, authoring ergonomics, or interaction demos. Do not make final capture depend on Anime.js timers unless the export script can seek them deterministically.

Build each beat's static hero frame before adding motion. Verify fixed canvas dimensions, resolved container heights, safe padding, wrapping, and peak clearance for pulsing or overshooting elements. Then animate from or through that known-good layout with transforms, opacity, color, and deterministic redraws.

## 6. Serve HTML Over Local HTTP

Do not rely on `file://` for ES modules. Chromium blocks module loading from `file://` in common capture paths. Use a local static server inside the export script or run an explicit local preview server.

For export scripts:

- bind to `127.0.0.1`
- choose an available port automatically when possible
- serve only the intended deck or example root
- close the server in a `finally` block

## 7. Capture Frames, Then Encode

For deterministic standalone web videos:

1. Launch Chromium with the target viewport.
2. Load the local HTTP URL.
3. Wait for fonts and initial network idle.
4. For each frame, call `renderConceptFrame(id, frame / fps, { capture: true })`.
5. Capture a PNG screenshot.
6. Encode numbered frames with ffmpeg to H.264 MP4.
7. Generate contact sheets from the MP4, not from raw frames.

Keep raw frames only while diagnosing. Delete them by default to avoid large transient output.

For a reusable capture command against any generated HTML that exposes `window.renderConceptFrame`, use:

```powershell
uv run --script skills/html-d3-anime-video-workflow/scripts/capture_html_video.py --html projects/<project-id>/src/index.html --output projects/<project-id>/artifacts/video-renders/draft/videos/<video>-browser.mp4 --video-id <video-id> --duration <seconds> --fps <fps> --width 1280 --height 720 --manifest projects/<project-id>/artifacts/reviews/browser-capture-manifest.json
```

Use this after the scaffold helper when you need to prove the HTML contract is capturable in Chromium, not only that the helper can emit a Pillow-rendered MP4.

For a faster semantic browser gate that does not encode a new MP4, sample the same deterministic frame function:

```powershell
uv run --script skills/html-d3-anime-video-workflow/scripts/check_html_render_state.py --html projects/<project-id>/src/index.html --video-id <video-id> --duration <seconds> --samples 6 --width 1280 --height 720 --manifest projects/<project-id>/artifacts/reviews/render-state-check.json --expect-state visualPattern=<pattern> --expect-state-final <late-key>=true --expect-state-transition <late-key>=false->true --expect-state-contains <label-array-key>="<exact label>" --expect-state-monotonic visibleMechanismCount=nondecreasing --min-distinct-state visibleMechanismCount=4
```

Use this after helper generation and before expensive visual iteration when the risk is semantic: wrong pattern, missing exact labels, no late mechanism reveal, no branch progression, or generic state that does not reflect the prompt. Use `--expect-state-contains` for label arrays such as `metricLabels`, `thresholdLabels`, `phaseLabels`, `treeLabels`, `routeLabels`, `checkpointLabels`, `systemLabels`, `stateLabels`, `guardLabels`, `decisionOptions`, `decisionCriteria`, `causalLabels`, `flowLabels`, `laneLabels`, `handoffLabels`, `threatLabels`, `barrierLabels`, `consequenceLabels`, `scenarioLabels`, `probabilityLabels`, `claimLabels`, `evidenceLabels`, `layerLabels`, or `concernLabels`. It proves the browser can execute `renderConceptFrame` and that the returned state progresses over time; it does not prove encoded-frame visual richness, so keep the MP4 quality, motion, and contact-sheet checks for final review.

For state-aware captures, add checks such as `--expect-state visualPattern=systems-flow`, `--expect-state-final retryVisible=true`, `--expect-state-transition retryVisible=false->true`, `--expect-state-final feedbackVisible=true`, `--expect-state-final interventionVisible=true`, `--expect-state-monotonic visibleMechanismCount=nondecreasing`, and `--min-distinct-state visibleMechanismCount=4`. The capture manifest then records a `stateSummary` with distinct values and numeric ranges for keys returned by `renderConceptFrame`, plus `passed` and `findings` fields. For advanced systems-flow or causal-loop videos, run at least one full-duration capture that proves late mechanisms such as retry, dead-letter, backpressure, feedback control, side effects, or interventions transition from hidden to visible; a short early segment can pass motion checks while missing the main mechanic.

For contact-sheet review, generate the sheet from the encoded MP4 with the bundled composer instead of relying on ad hoc ffmpeg tiling:

```powershell
uv run --script skills/html-d3-anime-video-workflow/scripts/make_video_contact_sheet.py --video projects/<project-id>/artifacts/video-renders/draft/videos/<video>.mp4 --output projects/<project-id>/artifacts/reviews/contact-sheet.jpg --manifest projects/<project-id>/artifacts/reviews/contact-sheet.json --samples 6 --columns 3 --thumb-width 426 --label-times --min-tile-color-buckets 12 --min-tile-nonbackground-ratio 0.015 --min-consecutive-change-ratio 0.002 --min-changing-pairs 2 --max-low-change-pairs 1
```

Use a sample count and column count that match the review need. Prefer `--thumb-width 426` or larger for text-heavy diagrams; 320 px thumbnails are only for coarse motion checks because they can hide label and overlap defects. The composer avoids sampling exact EOF, creates only real image tiles, and writes a JSON manifest with tile diversity, nonbackground content, and consecutive-tile change metrics; this prevents empty black cells or repeated frames from being mistaken for acceptable video review.

For isolated validation or a first runnable scaffold, prefer the prompt-contract wrapper when the prompt uses standard exact-output sections:

```powershell
uv run --script skills/html-d3-anime-video-workflow/scripts/build_from_prompt_contract.py --prompt ../prompt.md --manifest projects/<project-id>/artifacts/reviews/prompt-contract-build.json
```

The wrapper report should include top-level `passed: true`, no findings, a `sourcePreservation` block with no missing facts or anchors, a `media` block whose actual duration, fps, width, and height match the prompt contract, and a `contactSheet` block with `passed: true`, real sample times, per-tile motion/diversity metrics, `openingTile`, `finalTile`, `openingTileAssessment`, and no findings.

For Metro Minimal Tonal Motion, strict-grid, square-edge, or user-supplied colorset1/2 constraints, name the Metro audit suite, its child reports, and the encoded-MP4 composition report in the prompt or pass them to the wrapper:

```powershell
uv run --script skills/html-d3-anime-video-workflow/scripts/build_from_prompt_contract.py --prompt ../prompt.md --manifest projects/<project-id>/artifacts/reviews/prompt-contract-build.json --metro-style-manifest projects/<project-id>/artifacts/reviews/metro-style-audit.json --metro-composition-manifest projects/<project-id>/artifacts/reviews/metro-composition-audit.json --metro-rendered-frame-manifest projects/<project-id>/artifacts/reviews/metro-rendered-frame-audit.json --metro-mute-test-manifest projects/<project-id>/artifacts/reviews/metro-mute-test-audit.json --metro-video-composition-manifest projects/<project-id>/artifacts/reviews/metro-video-composition-audit.json --metro-audit-suite-manifest projects/<project-id>/artifacts/reviews/metro-audit-suite.json
```

The wrapper derives `metro-style-audit.json`, `metro-composition-audit.json`, `metro-rendered-frame-audit.json`, `metro-mute-test-audit.json`, `metro-video-composition-audit.json`, and `metro-audit-suite.json` paths from prompt text when those filenames are listed, and it also creates default audit paths under `projects/<project-id>/artifacts/reviews/` when the prompt asks for Metro, hard-edge, strict-grid, no-padding, or grayscale-level critique. It runs `run_metro_audit_suite.py` and `audit_metro_video_composition.py` before exact-output verification, so the suite JSON, child audit JSON files, and MP4 composition JSON may be required by the prompt and by the outer `pi` harness. A passing tonal audit proves the generated HTML uses the approved colorset1 tonal palette, avoids visible editorial title/date/draft text, and preserves visual anchors in the source package. A passing composition audit proves nonzero rounded values and rounded line caps/joins are absent, rectangle edges align to the grid, dynamic rectangles have runtime grid normalization, major edges share enough structure for an ordered composition, zero internal box-padding/inset signals are present, and the selected `visualPattern` branch has distinct grayscale hierarchy levels with enough luminance spread. A passing rendered-frame audit proves Chromium-sampled `renderConceptFrame` output keeps live SVG rects square, transformed/rendered rect edges grid-aligned, shared-edge aligned, backed by area-weighted visible final-frame and median active-sample grayscale hierarchy, meeting the active gray sample pass ratio, measuring zero-padding geometry for associated fills, rejecting high-confidence untagged inset panels that look like internal padding, carrying the declared zero-padding policy, exposing functional-zone DOM markers, staying visually driven through low rendered text-area ratio, enough mark-to-text density, no dominant text box, no title/date/editorial text band, and, when Masonry is required, real module count, size variety, occupied area, nondecreasing construction counts, and low text counts. The suite uses a bounded four-sample mute test by default so long videos do not stall wrapper validation, while the mute-test still requires three hidden changing pairs and therefore all adjacent hidden-text pairs must change. A passing mute-test audit proves that hiding all SVG text still leaves enough visual motion, mark density, functional zones, gray hierarchy, and nonbackground area for the major mechanic to read without labels. A passing MP4 composition audit proves the delivered video itself has distributed grid coverage, four-quadrant occupation, a non-weak opening composition, spatial progression across sampled frames, and low text-like component pressure. It catches cases where the DOM audits pass but the encoded video still reads as six labeled slides.

When changing these Metro audit rules, run `scripts/validate_metro_audit_fixtures.py` as a regression gate. It creates small positive and negative fixtures for external gutters, forbidden padding, rendered internal-padding geometry, untagged inset boxes with and without strokes, transformed off-grid geometry, CSS-applied rounding, area-weighted weak grayscale hierarchy, rendered title/editorial bands, excessive rendered text area, single dominant text boxes, weak mark-to-text density, and suite-output-only child report derivation. When changing scaffold geometry, gray hierarchy, zero-padding normalization, or selected-pattern rendering, also run `scripts/validate_metro_pattern_smoke.py` with all patterns so semantic panels do not regress into padding false positives and every scaffold keeps enough rendered grayscale levels. Inspect the smoke report's top-level `aggregateMetrics` before accepting the run; the maximum rendered padding, total padding/inset violations, minimum median/final gray levels, and weak-gray pattern lists should support the visual claim.

For multi-video sources, run `scripts/plan_metro_video_series.py` before rendering the batch. Use its per-module pattern choices rather than one document-wide `metroPatternMix`, and reject a batch plan with low helper diversity, low primary-pattern diversity, too few reusable D3 pattern IDs, or long repeated-helper runs.

When the prompt states where the wrapper report must be written, `build_from_prompt_contract.py` can derive that path even if `--manifest` is omitted. Still pass `--manifest` in exact commands when practical, because it makes the output contract obvious in the command line.

When the prompt also names a `render-state` or `browser-state` JSON report path, the wrapper can derive `--state-manifest` and default state expectations even if the command only includes `--prompt` and `--manifest`. The defaults assert the selected `visualPattern`, final-state and `false->true` late pattern-specific mechanism reveals, first/last preserved labels for available label arrays, monotonic `visibleMechanismCount`, and distinct mechanism-count progression. For `systems-flow`, the defaults also assert final `queueSlots=8`, final `visibleMechanismCount=6`, monotonic `queueSlots`, and distinct queue/mechanism progression, because a flow video must prove queue pressure and full mechanism reveal before retry, dead-letter, and feedback states are accepted. For `skill-tree`, the defaults also assert final `routeCount=5`, monotonic `routeCount`, and at least three distinct route-count values under the wrapper's six-sample state check, because a route-map video must prove the path grows before keystone or Atlas layers are accepted. For `skill-tree-route`, the defaults also assert final `activeRouteNodeCount=8`, final `visibleMechanismCount=7`, monotonic `activeRouteNodeCount`, damage/defense cluster, attribute bridge, keystone tradeoff, respec route, and late-specialization transitions, plus distinct route/mechanism progression, because a tree-route video must prove path cost, side clusters, tradeoff, and late-layer separation instead of showing static highlighted nodes. For `state-machine`, the defaults assert final `activeState=5`, monotonic `activeState`, and at least four distinct active-state values, because a lifecycle video must prove the main state path advances before rollback and terminal-state callouts are accepted. For `comparison-matrix`, the defaults assert final `criteriaRevealed=4`, monotonic `criteriaRevealed`, and at least three distinct criteria counts, because a comparison video must prove evidence appears before recommendation and guardrail states are accepted. For `causal-loop`, the defaults assert loop, delay, amplifier, damping, side-effect, and intervention transitions plus final `visibleMechanismCount=6`, because a feedback explainer must prove the whole causal mechanism, not only the last remedy. For `phase-timeline`, the defaults assert risk, gate, handoff, and final milestone transitions plus final monotonic `activePhase=5`, because a timeline must prove phase traversal rather than static milestone labels. For `dependency-map`, the defaults also assert final `edgeCount=7`, monotonic `edgeCount`, and distinct edge-count progression, because a dependency map must prove the graph edges arrive and complete. For `sequence-trace`, the defaults also assert final `activeSpanCount=7`, monotonic `activeSpanCount`, and distinct span-count progression, because ghost rails can orient the viewer but must not be mistaken for active or complete trace progress. For `sankey-flow`, the defaults also assert final `activeFlowCount=7`, monotonic `activeFlowCount`, split/loss/bottleneck/merge/output transitions, and distinct flow/mechanism progression, because a conversion map must prove value movement, explicit loss, recombination, and output readiness instead of showing a static funnel. For `swimlane-handoff`, the defaults also assert final `activeHandoffCount=8`, monotonic `activeHandoffCount`, SLA/rework/approval/escalation/completion transitions, and distinct handoff/mechanism progression, because a workflow map must prove owner transfer and exception routing instead of showing static lanes. For `risk-bowtie`, the defaults also assert final `activeThreatCount=4`, monotonic `activeThreatCount`, preventive/top-event/mitigative/consequence/degraded/action transitions, and distinct threat/mechanism progression, because a risk bowtie must prove control timing and assurance gaps rather than showing static risk labels. For `scenario-tree`, the defaults also assert final `activeScenarioCount=7`, monotonic `activeScenarioCount`, probability/risk/upside/decision/fallback/outcome transitions, and distinct scenario/mechanism progression, because a scenario tree must prove branching futures and fallback before selecting an outcome. For `evidence-ladder`, the defaults also assert final `activeEvidenceCount=6`, final `visibleMechanismCount=6`, monotonic `activeEvidenceCount`, claim/counterevidence/source-gap/confidence/recommendation transitions, and distinct evidence/mechanism progression, because a research video must prove support, uncertainty, and recommendation timing rather than showing a flat source list. For `layered-architecture`, the defaults also assert final `activeLayerCount=6`, final `visibleMechanismCount=6`, monotonic `activeLayerCount`, cross-cutting/failure/observability/rollout transitions, and distinct layer/mechanism progression, because an architecture video must prove ownership and operational overlays rather than showing static stacked boxes. For `data-lineage`, the defaults also assert final `activeLineageCount=6`, final `visibleMechanismCount=6`, monotonic `activeLineageCount`, transform/quality-gate/drift/consumer/rollback transitions, and distinct lineage/mechanism progression, because a lineage video must prove provenance and operational trust checks rather than showing a static pipeline arrow.

When the same exact-output task also requires semantic browser-state proof, run the wrapper with integrated state-check flags:

```powershell
uv run --script skills/html-d3-anime-video-workflow/scripts/build_from_prompt_contract.py --prompt ../prompt.md --manifest projects/<project-id>/artifacts/reviews/prompt-contract-build.json --state-manifest projects/<project-id>/artifacts/reviews/render-state-check.json --state-expect visualPattern=<pattern> --state-expect-final <late-key>=true --state-expect-transition <late-key>=false->true --state-expect-contains <label-array-key>="<exact label>" --state-expect-monotonic visibleMechanismCount=nondecreasing --state-min-distinct visibleMechanismCount=4
```

The wrapper report then includes `stateCheck`. Require `stateCheck.passed: true` in addition to the top-level wrapper pass, embedded `contactSheet.passed`, the contact-sheet manifest pass, and `contactSheet.openingTileAssessment.weak: false`. The wrapper should emit a `weak-opening-tile` finding and fail when the opening tile assessment is weak. Compare `contactSheet.openingTile` with the later per-tile metrics before accepting the draft; a sparse or unreadable opening frame should be improved even when aggregate motion metrics pass. The wrapper runs integrated state and Metro audit checks before exact-output verification, so those JSON report paths can be included in exact output contracts when the prompt names them. For Metro/no-padding critiques, require both `metroAuditSuite.passed: true` and `metroRenderedFrameAudit.passed: true` so source-level normalization is confirmed against the live DOM.

Use the direct helper command below only as a manual fallback when the wrapper cannot derive the prompt contract. Treat both scripts as executable tools; do not open their source just to learn arguments.

```powershell
uv run --script skills/html-d3-anime-video-workflow/scripts/build_standalone_explainer.py --project-root projects/<project-id> --title "<topic>" --output-id <output-id> --fact "<source fact>"
```

Use it when the task requires a real MP4 and no project-specific capture pipeline exists yet. It is a draft scaffold, not a substitute for a final bespoke HTML/D3 render: preserve prompt facts with `--fact`, then inspect and improve the generated HTML, MP4, metric contact-sheet manifest, contact sheet, and self-review.

Choose the helper pattern deliberately:

- `--pattern skill-tree-route` for advanced passive-tree pathing, build-route planning, travel-node cost, keystone tradeoffs, respec checkpoints, or late-specialization videos. This pattern should show main route growth, damage cluster, defense cluster, attribute bridge, keystone tradeoff, respec route, and late specialization as distinct mechanisms. When the prompt supplies route or checkpoint names, pass them as `--route-label` and `--checkpoint-label` values so the source package preserves exact tree-route vocabulary.
- `--pattern skill-tree` for simpler route maps, passive trees, build paths, strategy maps, branching choices, keystone tradeoffs, or separate specialization layers. When the prompt supplies concrete node or meter names, pass them as `--tree-label` and `--meter-label` values so the route map labels the actual build priorities instead of generic start, notable, damage, defense, attribute, gear, keystone, and Atlas nodes.
- `--pattern systems-flow` for architecture, reliability, event pipelines, queues, retries, dead-letter paths, worker pools, capacity, throughput, and feedback-control explainers. This pattern should show at least three semantic motion systems, such as packet route, queue fill, branch split, worker pulse, metric movement, and feedback loop. When the prompt supplies concrete component names, pass them as `--system-label` values so the flow map names the actual intake, bus, queue, worker, store, retry, dead-letter, metric, and throttle components.
- `--pattern state-machine` for lifecycles, workflow states, guarded transitions, approvals, rollback, compensation, invariant restoration, and terminal-state explainers. This pattern should show state activation, guard checks, success transitions, recovery path, and terminal-state separation as distinct mechanisms. When the prompt supplies lifecycle state or transition guard names, pass them as `--state-label` and `--guard-label` values so the state machine explains the actual workflow instead of generic states.
- `--pattern comparison-matrix` for option comparisons, tradeoff explainers, decision matrices, scorecards, recommendation rationale, and guardrail-based selection. This pattern should show option reveal, criteria scoring, score-shift markers, tradeoff lens, delayed recommendation, and guardrail as distinct mechanisms. When the prompt supplies option or criterion names, pass them as `--option-label` and `--criterion-label` values so the matrix explains the actual decision instead of generic columns and rows.
- `--pattern causal-loop` for causal-loop maps, feedback loops, root-cause explainers, delayed effects, side effects, leverage points, and intervention strategy. This pattern should show cause-chain reveal, reinforcing loop, delayed effect, balancing loop, side-effect branch, and intervention as distinct mechanisms. When the prompt supplies causal variables, pass them as `--node-label` values in trigger, pressure, behavior, outcome, side-effect, and intervention order so the video explains the source domain rather than generic nodes.
- `--pattern phase-timeline` for chronological plans, roadmaps, release plans, incident timelines, approval calendars, and phase-based project narratives. This pattern should show source-locked phase cards, risk surfacing, a decision gate, handoff route, release milestone, and current-phase token as distinct mechanisms. When the prompt supplies phase names, pass them as `--phase-label` values in chronological order so the timeline explains the actual plan instead of generic phases.
- `--pattern metric-dashboard` for KPI, SLO, error-budget, burn-rate, threshold, anomaly, forecast, or metric-health explainers. This pattern should show primary metric ownership, trend reveal, healthy/warning/action thresholds, anomaly marker, forecast cone, and late decision window as distinct mechanisms. The wrapper's derived state checks must prove trend and threshold visibility as well as anomaly, forecast, and decision visibility. When the prompt supplies metric or threshold names, pass them as `--metric-label` and `--threshold-label` values so the dashboard explains the actual operating rule instead of generic KPI cards.
- `--pattern dependency-map` for dependency graphs, DAG explainers, migration dependencies, blocked-by maps, bottleneck analysis, release cutovers, fallback planning, and cross-team readiness videos. This pattern should show cluster boundaries, converging dependency edges, risk edge, bottleneck, cutover gate, fallback path, and release readiness as distinct mechanisms. When the prompt supplies dependency or cluster names, pass them as `--dependency-label` and `--cluster-label` values so the graph preserves exact source labels. Keep low-contrast ghost labels visible from the first frame, then reinforce active nodes as proof advances; an opening topology with no readable node names is a failed dependency-map critique even if motion metrics pass.
- `--pattern sequence-trace` for distributed traces, request traces, span waterfalls, latency-budget investigations, critical-path explainers, service-call debugging, retry/fallback analysis, and observability videos. This pattern should show fixed service lanes, span-duration bars, handoff markers, critical path, latency budget, retry branch, fallback route, and final response as distinct mechanisms. When the prompt supplies service or span names, pass them as `--trace-label` values in request-path order so the trace preserves exact source labels instead of generic services.
- `--pattern sankey-flow` for Sankey maps, conversion flows, value streams, flow splits, dropoff analysis, retained/lost value, transformation lanes, merge points, bottleneck analysis, and output-readiness videos. This pattern should show one input band, explicit retained and loss branches, parallel transform lanes, merge point, bottleneck, output readiness, and final output as distinct mechanisms. When the prompt supplies flow names, pass them as `--flow-label` values in input, retained branch, loss branch, transform A, transform B, merge, bottleneck, and output order so the source package preserves exact flow vocabulary.
- `--pattern swimlane-handoff` for swimlane diagrams, role-lane workflows, cross-team handoffs, service-level workflows, approval routes, rework loops, escalation paths, ownership transfer, and completion-readiness videos. This pattern should show fixed owner lanes, sequential handoff motion, SLA pressure, approval gate, rework loop, escalation path, and completion as distinct mechanisms. When the prompt supplies owner or step names, pass them as `--lane-label` and `--handoff-label` values so the source package preserves exact responsibility and process vocabulary.
- `--pattern risk-bowtie` for risk bowties, hazard analysis, barrier analysis, top-event explainers, preventive versus mitigative control stories, degraded-control reviews, assurance gaps, residual risk, and repair-action videos. This pattern should show threats, preventive barriers, top event, mitigative barriers, consequences, degraded barrier, residual risk, and repair action as distinct mechanisms. When the prompt supplies threat, barrier, or consequence names, pass them as `--threat-label`, `--barrier-label`, and `--consequence-label` values so the source package preserves exact risk-control vocabulary.
- `--pattern scenario-tree` for scenario trees, decision trees, branching futures, probability branches, expected-value reasoning, upside/downside strategy, fallback scenarios, and selected-outcome videos. This pattern should show a decision root, scenario branches, probability labels, evidence weight, upside branch, risk branch, decision gate, fallback route, and selected outcome as distinct mechanisms. When the prompt supplies scenario or probability names, pass them as `--scenario-label` and `--probability-label` values so the source package preserves exact scenario vocabulary.
- `--pattern evidence-ladder` for research evidence, claim support, source-confidence, counterevidence, source-gap, methodology caveat, and recommendation-confidence videos. This pattern should show working claim, tiered support, counterevidence, source gap, confidence, uncertainty, and delayed recommendation as distinct mechanisms. When the prompt supplies claim or evidence names, pass them as `--claim-label` and `--evidence-label` values so the source package preserves exact research vocabulary.
- `--pattern layered-architecture` for layered architecture, layer stacks, platform architecture, cross-cutting concerns, observability layers, failure routing, and rollout-gate videos. This pattern should show layer activation, request path, cross-cutting policy, failure path, observability, and rollout gate as distinct mechanisms. When the prompt supplies layer or concern names, pass them as `--layer-label` and `--concern-label` values so the source package preserves exact architecture vocabulary.
- `--pattern data-lineage` for data lineage, lineage graphs, data pipelines, ETL/ELT flows, schema checks, freshness windows, drift monitoring, source-to-consumer maps, and rollback-readiness videos. This pattern should show source-to-consumer activation, transform rule, quality gate, drift monitor, consumer contract, and rollback route as distinct mechanisms. When the prompt supplies lineage or quality names, pass them as `--lineage-label` and `--quality-label` values so the source package preserves exact data-platform vocabulary.

When exact output paths are supplied, derive the helper arguments from those paths instead of from the title. The project root is the shared prefix before `source/`, `src/`, and `artifacts/`; the output id is the requested MP4 filename without `.mp4`. If the helper writes a valid video under a different title-derived directory, the validation still fails until the exact paths are produced.

For isolated forward tests of the helper itself, keep the prompt command-first and short. Put the exact `uv run --script ... build_standalone_explainer.py` command before broader storytelling requirements, then list the required output paths. Long mixed prompts that ask for source preservation, story design, exact paths, and helper usage at once can lead the model to run a title-derived project slug instead of the required path; treat that as a prompt-contract failure and simplify the validation prompt before judging video quality.

For final quality:

- Use at least 30 fps. Use 6 fps only for drafts and contact-sheet iteration.
- For Metro Minimal Tonal Motion, design the video as a large modular map or megacanvas with named functional zones that can be explored by camera movement, not as disconnected slides. Use zooms, pans, expanding blocks, masked reframing, or tile morphs to move between zones while keeping flat surfaces and clean modular structure. Default scaffold colors to colorset1: red, dark red, status red, red highlight, neutral text, white, black, and grays. Use colorset2 only when colorset1 cannot separate semantic states, and record the reason in production notes. Use `--edge-style square` or the prompt wrapper's default square edge style for hard-edge/scaffold videos. Boxes must have zero internal padding: do not create inset bars, inset labels, padded chips, or nested panels to simulate hierarchy. Use external gutters and distinct grayscale levels for hierarchy instead. For Masonry/megacanvas repairs, require a non-weak opening tile and visible block construction in the MP4 contact sheet, not just in HTML state samples.
- Do not render visible title, checked-date, draft/scaffold, or beat-caption bands inside the video frame. Keep those facts in source packages, manifests, filenames, or post-production copy.
- Use CRF 16-18 for H.264 diagram videos unless file size is the primary constraint.
- Supersample raster captures when practical, such as Chromium `deviceScaleFactor: 2`, then downscale with Lanczos during encoding.
- Encode diagram-heavy motion with a slow preset and animation tuning when ffmpeg supports it.
- Check the final MP4 at normal playback speed, not only contact sheets; contact sheets hide temporal stutter.

For faster iteration, expose explicit render tiers instead of making every preview pay final-render cost:

- `quick`: 6 fps, CRF 24, device scale 1, veryfast encoding, no contact sheet. Use only for storyboard timing and rough layout.
- `draft`: 12 fps, CRF 24, device scale 1, veryfast encoding, no contact sheet. Use for most visual-shape iterations before judging smoothness.
- `motion`: 30 fps, CRF 20, device scale 1, faster encoding, contact sheet enabled. Use when the animation timing or stutter is the thing being reviewed.
- `fast`: 30 fps, CRF 16, device scale 2, veryfast encoding, no contact sheet. Use when the user needs a near-final-looking segment without paying for slow encoding or review artifacts.
- `final`: 30 fps, CRF 16, device scale 2, slow encoding, contact sheet enabled. Use for approved segments and deliverables.

Prefer rendering only the changed time range with `--start` and `--duration`. Render full videos only for continuity checks, final review, or when a change touches shared helpers across multiple beats.

When using npm scripts with extra renderer flags in PowerShell, pass a double separator so npm does not consume option names:

```powershell
npm run render:fast -- -- --concept 01-what-is-an-llm --start 36 --duration 30
```

Calling the renderer directly is also valid for segment work:

```powershell
node projects/ai-concept-videos/scripts/render-videos.mjs --preset fast --concept 01-what-is-an-llm --start 36 --duration 30
```

For separately rendered or separately authored segments, lock continuity at boundaries. Render both adjacent segments with raw frames kept, then compare the previous segment's last intended frame (`duration * fps - 1`) against the next segment's first frame by hash or pixel diff. Treat a mismatch as a visual bug unless the cut is intentionally visible.

## 8. Review In Three Passes

Apply at least three concrete improvement passes before final delivery:

- Pass 1: source, metaphor, and storyboard. Verify references, simplify claims, align the data model, decide the visual metaphor, and ensure every video has the expected beat structure.
- Pass 2: coordinated animation. Add at least two simultaneous animation systems per concept, and at least three for polished Metro or complex low-text explainers, such as D3 visual motion, metric updates, beat progress, token/packet movement, camera reframing, matrix fills, route drawing, or block construction.
- Pass 3: visual QA polish. Review contact sheets, fix text fit, balance palette use, remove clutter, and verify the output does not read as static, padded, rounded, title-led, or slide-like.

Record the passes in production notes with one row per video.

## Too Simple, Too Textual, Too Static Gate

Reject or redesign before final delivery when the video fails any of these checks:

- The first and final contact-sheet tiles read as labeled diagrams rather than a designed visual system.
- The explanation depends on title, subtitle, caption, paragraph text, or one dominant label.
- Motion is mostly fades, slides, or identical reveals rather than visible state change.
- There are fewer than three semantic motion systems in a Metro, complex, or narrated low-text explainer.
- A Metro video lacks functional zones, camera exploration, square 4 px grid geometry, zero internal padding, or distinct grayscale hierarchy.
- Transitions are generic cuts or pulses when the style calls for zoom, pan, tile morph, expanding block, masked reframe, masonry construction, or surface wipe.
- The composition uses colorset1 only as a palette skin while ignoring its gray-level hierarchy, hard-edge box model, or modular alignment rules.

Use `metro-minimal-tonal-motion.md` for design-specific rejection and `visual-density-pattern-bank.md` to choose stronger visual structures. Passing wrapper reports and audits is not enough for final polished design when this gate fails.

When the critique says the output is not following the design, produce or inspect a `metroPatternMix` report from `plan_metro_pattern_mix.py` and verify that the video visibly uses the reported zones and camera path. A draft with a passing wrapper but no visible pattern mix is rejected as too textual, too static, or too slide-like. For helper-generated drafts, require source `visualZones` and `semanticBindings`, state `visibleZoneCount`, changing `activeZoneId`, and `activeSourceAnchors`, rendered SVG `data-zone-id`/`data-zone-role`/`data-source-anchor-json` markers with legacy `data-source-anchor` fallback, and an MP4 contact sheet that matches the same low-text modular composition before accepting the redesigned megacanvas.

For videos with planned transitions, add transition midpoint screenshots to the smoke or review pass. Contact sheets sampled every few seconds can miss a cut that violates its transition contract, such as a planned zoom, portal, or morph that renders only as a generic pulse.

## 9. Automated Review Gate

Use `ffprobe` and `ffmpeg` checks before delivery:

- duration within tolerance
- expected resolution
- expected frame count or frame rate
- black frame detection
- freeze detection with a threshold that does not false-positive on small UI motion
- contact sheet generation

When a durable JSON review artifact is useful, run the bundled reviewer:

```powershell
uv run --script skills/html-d3-anime-video-workflow/scripts/review_video_quality.py --video projects/<project-id>/artifacts/video-renders/draft/videos/<video>.mp4 --report projects/<project-id>/artifacts/reviews/quality-report.json --expect-width 1280 --expect-height 720 --expect-duration <seconds> --expect-fps <fps>
```

For diagram videos with small semantic motion, keep the reviewer sensitive enough to avoid false freeze positives. The default `--freeze-noise 0.0001` is tuned for small SVG packet, route, and meter changes; raise it only when real sensor noise or compression flicker hides actual stillness.

For frame-level richness beyond black/freeze checks, run the motion auditor:

```powershell
uv run --script skills/html-d3-anime-video-workflow/scripts/audit_video_motion.py --video projects/<project-id>/artifacts/video-renders/draft/videos/<video>.mp4 --report projects/<project-id>/artifacts/reviews/motion-audit-report.json --sample-fps 1 --min-samples 4 --min-color-buckets 12 --min-nonbackground-ratio 0.015 --min-changing-pairs 2
```

Use this to catch videos that technically encode and pass black/freeze checks but are visually empty, one-color, or nearly static. Tune thresholds per format, but require at least some color diversity, nonbackground content, and sampled-frame change for advanced explainer work.

For reusable visual contact-sheet review, run the bundled contact-sheet composer:

```powershell
uv run --script skills/html-d3-anime-video-workflow/scripts/make_video_contact_sheet.py --video projects/<project-id>/artifacts/video-renders/draft/videos/<video>.mp4 --output projects/<project-id>/artifacts/reviews/contact-sheet.jpg --manifest projects/<project-id>/artifacts/reviews/contact-sheet.json --samples 6 --columns 3 --thumb-width 426 --label-times --min-tile-color-buckets 12 --min-tile-nonbackground-ratio 0.015 --min-consecutive-change-ratio 0.002 --min-changing-pairs 2 --max-low-change-pairs 1
```

Treat a missing, empty, or non-passing contact-sheet manifest as a review failure. Inspect the sheet visually after generation; it proves sampled frame content and coarse state progression, not temporal smoothness.

For reusable semantic browser state review without encoding a video, run the render-state checker:

```powershell
uv run --script skills/html-d3-anime-video-workflow/scripts/check_html_render_state.py --html projects/<project-id>/src/index.html --video-id <video-id> --duration <seconds> --samples 6 --width 1280 --height 720 --manifest projects/<project-id>/artifacts/reviews/render-state-check.json --expect-state visualPattern=<pattern> --expect-state-final <late-key>=true --expect-state-transition <late-key>=false->true --expect-state-contains <label-array-key>="<exact label>" --expect-state-monotonic visibleMechanismCount=nondecreasing --min-distinct-state visibleMechanismCount=4
```

Treat a non-passing render-state manifest as a source-preservation or storyboard-state failure. It catches wrong pattern routing, generic labels, and missing late mechanisms earlier than MP4 review, but it does not replace full visual inspection.

For Metro, complex, dynamic, or low-text explainers, run the semantic-density auditor after wrapper, state, contact-sheet, Metro audit, mute-test, and MP4 composition reports exist:

```powershell
uv run --script skills/html-d3-anime-video-workflow/scripts/audit_metro_semantic_density.py --wrapper-report projects/<project-id>/artifacts/reviews/prompt-contract-build.json --state-manifest projects/<project-id>/artifacts/reviews/render-state-check.json --contact-sheet-manifest projects/<project-id>/artifacts/video-renders/draft/review/<video>-contact-sheet.json --metro-audit-suite projects/<project-id>/artifacts/reviews/metro-audit-suite.json --metro-mute-test-audit projects/<project-id>/artifacts/reviews/metro-mute-test-audit.json --metro-video-composition-audit projects/<project-id>/artifacts/reviews/metro-video-composition-audit.json --output projects/<project-id>/artifacts/reviews/metro-semantic-density-audit.json
```

Treat a failing semantic-density report as a design failure, not a reporting problem. It means the artifact may be styled correctly but still too static, too shallow, too text-dependent, missing camera exploration, missing text-hidden visual progression, or lacking enough visible mechanism change.

The semantic-density auditor also requires `wrapper.metroPatternMix` by default. It checks that the mix passed, that `selected.helperPattern` matches the rendered `source-package.json.visualPattern`, that the mix includes enough visual-density patterns, used beat patterns, functional zones, semantic motion systems, camera events, transition contracts, transition type variety, modular transition types, and expected anti-pattern risks. It also requires enough source `visualZones`, complete source-anchor `semanticBindings`, render-state `visibleZoneCount` and distinct `activeZoneId` evidence, render-state `activeSourceAnchors`, ordered `statesSample` continuity with adjacent zone changes coupled to camera/reframe deltas, meaningful camera travel and zoom depth, rendered DOM zone and source-anchor markers, no ellipsized rendered labels, mute-test evidence, and MP4 composition evidence for distributed grid/quadrant/opening/progression quality. Rendered source-anchor markers should use JSON attributes such as `data-source-anchor-json` rather than relying only on delimiter-joined text, because source anchors often contain Markdown tables, code, citations, and `|` characters. If Masonry is required, it also requires rendered-frame evidence for `data-masonry-module` count, module-size variety, occupied area, construction progression through `masonryModuleCounts`, nondecreasing module growth, and low rendered text counts. This makes the pattern mix a rendered, source-bound, and encoded-video acceptance condition instead of a planning-only JSON.

For exact output contracts, especially after a failed isolated run, add a local contract check:

```powershell
uv run --script skills/html-d3-anime-video-workflow/scripts/check_video_outputs.py --require projects/<project-id>/src/index.html --require projects/<project-id>/artifacts/video-renders/draft/videos/<video>.mp4 --require-json-passed projects/<project-id>/artifacts/reviews/quality-report.json --require-text projects/<project-id>/source/source-package.json::"<literal source anchor>" --report projects/<project-id>/artifacts/reviews/output-contract-report.json
```

The checker also accepts required paths as positional arguments, `--required-anchors` for literal text that may appear in any text-like required output, and media expectations such as `--duration`, `--fps`, `--width`, and `--height`. Use those public arguments instead of opening the checker source during normal runtime.

Treat failures as blocking unless the user explicitly accepts them.

Scale validation to the source and route. For input-driven videos, also verify the source package exists and that unstable claims have checked dates. For multi-beat videos, verify the storyboard tiles the duration and every beat has a visible mechanism. For motion-heavy work, review key timestamps for expected state changes before paying for a final render. If freeze detection fails, first add or extend semantic scene-local motion such as a packet route, branch lane fill, chart cursor, or checklist orbit. Do not solve it with a global repeated sweep unless that sweep is the subject of the video.

Make review artifacts honest. Choose contact-sheet tile geometry that matches the number of sampled frames, or compose sheets with `make_video_contact_sheet.py` so the layout cannot introduce empty black cells. Empty cells create false visual defects and can hide whether the last sampled frames were actually generated. Regenerate contact sheets after the final render, not only after a draft.

Inspect full-size keyframes for every shared lower-third, rail, watermark, recurring packet, or reusable symbol. Contact sheets can hide collisions between small repeated labels and scene-specific chips. When a shared symbol overlaps local scene text, remove the duplicate label or move the symbol; do not shrink critical text to make decorative continuity fit.

## 10. Output Layout

Use `projects/<project-id>/artifacts/` for generated artifacts:

```text
projects/<project-id>/
  scripts/
  source/
  artifacts/
    documents/
    svgs/
    gifs/
    images/
    data/
    manifests/
    video-renders/
      final/
        videos/
        review/
        render-manifest.json
        production-notes.md
      draft-pass/
      smoke/
    videos/
    screenshots/
    reviews/
```

For the AI concept video project, the default renderer layout is:

```text
projects/ai-concept-videos/artifacts/video-renders/
  final/
    videos/
    review/
    render-manifest.json
    production-notes.md
  draft-pass/
  smoke/
```

Keep reusable example source under the owning skill's `assets/examples/<project>/` directory, project-specific automation under `projects/<project-id>/scripts/`, and generated documents, videos, SVGs, GIFs, screenshots, manifests, review output, and data under `projects/<project-id>/artifacts/`.
