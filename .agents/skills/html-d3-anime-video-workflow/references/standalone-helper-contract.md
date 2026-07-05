# Standalone Helper Contract

Use this reference when a prompt asks for a complete standalone HTML video package but does not provide an exact wrapper or `build_standalone_explainer.py` command.

Read-surface rule: do not open helper, wrapper, suite, audit, or checker script source just to discover arguments or diagnose a passing run. Treat `build_from_prompt_contract.py`, `build_standalone_explainer.py`, `run_metro_audit_suite.py`, `audit_metro_tonal_style.py`, `audit_metro_composition.py`, `audit_metro_rendered_frames.py`, `audit_metro_mute_test.py`, and `check_video_outputs.py` as executable tools unless the task is to modify or debug those scripts. Derive commands from this contract, the exact requested paths, the compact wrapper report, and the prompt facts.

If the prompt already gives an exact `build_from_prompt_contract.py` command, skip this reference, run the command, then verify the wrapper report and requested outputs.

For prompts that use the standard sections `Required exact outputs`, `Topic`, `Video title`, `Checked date`, `Preserve these source facts`, and `Preserve these visual anchors`, prefer the deterministic wrapper:

```powershell
uv run --script skills/html-d3-anime-video-workflow/scripts/build_from_prompt_contract.py --prompt ../prompt.md --manifest projects/<project-id>/artifacts/reviews/prompt-contract-build.json
```

The wrapper derives `--project-root`, `--output-id`, pattern, format, facts, and anchors, runs `build_standalone_explainer.py`, verifies exact paths, checks the generated contact-sheet manifest, summarizes its sample times and per-tile motion/diversity metrics in `contactSheet`, adds `openingTile`, `finalTile`, and `openingTileAssessment` snapshots, fails with `weak-opening-tile` when the opening assessment is weak, verifies `sourceFacts` and `strategyAnchors` in `source-package.json`, probes the MP4 with `ffprobe` for duration, fps, width, and height, runs any derived Metro audits, derives `metroPatternMix` for Metro or design-fidelity prompts, and writes a JSON report.

For Metro Minimal Tonal Motion, strict colorset, strict-grid, square-edge, or design-rejection prompts, name the audit JSON paths in the prompt or pass them to the wrapper:

```powershell
uv run --script skills/html-d3-anime-video-workflow/scripts/build_from_prompt_contract.py --prompt ../prompt.md --manifest projects/<project-id>/artifacts/reviews/prompt-contract-build.json --metro-style-manifest projects/<project-id>/artifacts/reviews/metro-style-audit.json --metro-composition-manifest projects/<project-id>/artifacts/reviews/metro-composition-audit.json --metro-rendered-frame-manifest projects/<project-id>/artifacts/reviews/metro-rendered-frame-audit.json --metro-mute-test-manifest projects/<project-id>/artifacts/reviews/metro-mute-test-audit.json --metro-video-composition-manifest projects/<project-id>/artifacts/reviews/metro-video-composition-audit.json --metro-audit-suite-manifest projects/<project-id>/artifacts/reviews/metro-audit-suite.json
```

The wrapper can also derive `metro-style-audit.json`, `metro-composition-audit.json`, `metro-rendered-frame-audit.json`, `metro-mute-test-audit.json`, `metro-video-composition-audit.json`, and `metro-audit-suite.json` when the prompt names those paths. It runs `run_metro_audit_suite.py` and `audit_metro_video_composition.py` before exact-output verification, so those report paths may be included in the exact output contract and in the outer `pi` harness. If only `metro-audit-suite.json` is supplied, the wrapper and suite runner derive the four child reports beside it; the wrapper also derives a sibling `metro-video-composition-audit.json`; suite mode is all-or-nothing, not a partial audit. The suite uses a bounded four-sample mute test by default so long videos do not stall wrapper validation, while still requiring three hidden changing pairs. It runs the separate `stateCheck` only when the prompt names a `render-state` or `browser-state` report path, or when explicit state flags are supplied or derived from that path. The composition audit enforces 0-radius geometry, hard line caps/joins, grid-aligned rectangle edges, runtime normalization for dynamic rectangles, shared-edge structure, zero internal box-padding/inset signals, and distinct grayscale hierarchy levels in the selected `visualPattern` branch with enough luminance spread to read as hierarchy. The rendered-frame audit loads the generated HTML in Chromium, samples `renderConceptFrame`, and checks live SVG rect radii, line caps/joins, transformed/rendered grid-aligned rect edges, shared-edge composition, the declared zero-padding policy, measured zero-padding geometry for any `data-box-id`/`data-fill-for` fill associations, high-confidence untagged inset panels that look like internal padding, rendered `data-zone-id`/`data-zone-role`/`data-source-anchor-json` functional-zone markers with legacy `data-source-anchor` fallback, area-weighted visible grayscale hierarchy, median active-sample gray hierarchy, active-sample pass ratio, final-frame grayscale hierarchy, text-area ratio, mark-to-text density, dominant text boxes, and title/date/editorial text bands. The mute-test audit hides rendered text and verifies that the remaining geometry still carries motion, mark density, functional zones, gray hierarchy, and nonbackground area. The MP4 composition audit samples the encoded video and rejects slide-like output with weak grid coverage, weak quadrant distribution, weak opening composition, weak distributed spatial progression, or excessive text-like component pressure. When the compact wrapper report shows `passed: true` and embeds passing `metroAuditSuite`, `metroStyleAudit`, `metroCompositionAudit`, `metroRenderedFrameAudit`, `metroMuteTestAudit`, and `metroVideoCompositionAudit` objects, accept those results without reading child manifests or script sources.

For Metro, complex dynamic, low-text, or design-rejection prompts, the wrapper runs the same selection logic as `scripts/plan_metro_pattern_mix.py` and embeds `metroPatternMix`. Its schema distinguishes `selected.helperPattern` from the richer design plan: `primaryPattern`, `secondaryPattern`, `supportPatterns`, `functionalZones`, `semanticMotionSystems`, `cameraPath`, `transitionContracts`, `antiPatternRisks`, and `reusableD3PatternIds`. Use `helperPattern` only to choose the first runnable standalone scaffold. The final video must visibly use the pattern mix, zone plan, gray hierarchy, source-anchor bindings, and camera/reframe path; otherwise a passing scaffold remains a design failure. In helper-generated Metro outputs, this means `source-package.json.visualZones` and `source-package.json.semanticBindings`, SVG `data-zone-id`/`data-zone-role`/`data-source-anchor-json` markers with legacy `data-source-anchor` fallback, render-state `visibleZoneCount`/`activeZoneId`/`activeSourceAnchors` evidence, meaningful camera travel/zoom-depth evidence, and `metro-video-composition-audit.json` grid/quadrant/progression evidence should all agree with the mix's functional-zone count and source anchors. Prefer the JSON marker for rendered source-anchor coverage because source anchors may include Markdown tables, code snippets, and literal `|` characters.

For a multi-video prompt or a Markdown source with several `###` timed-video modules, run the series planner before rendering the batch:

```powershell
uv run --script skills/html-d3-anime-video-workflow/scripts/plan_metro_video_series.py --prompt-file ../prompt.md --output projects/<project-id>/artifacts/reviews/metro-video-series-plan.json
```

Use the report's per-module `helperPattern`, `primaryPattern`, `supportPatterns`, and `reusableD3PatternIds` to choose each video's scaffold and D3 pattern references. Require aggregate helper and primary-pattern diversity and a low `maxSameHelperRun`; a single full-document `metroPatternMix` is not enough evidence that a series follows the design.

For a design-repair batch, generate per-video prompt contracts before invoking isolated `pi` runs:

```powershell
uv run --script skills/html-d3-anime-video-workflow/scripts/build_metro_series_contract_prompts.py --source ../prompt.md --output-dir projects/<project-id>/artifacts/prompts --project-root projects/<project-id>/videos
```

In repository maintenance:

```powershell
uv run --script .agents/skills/html-d3-anime-video-workflow/scripts/build_metro_series_contract_prompts.py --source design/videos.md --output-dir projects/<project-id>/artifacts/prompts --project-root projects/<project-id>/videos
```

Use the generated prompt files as the task prompts for the per-video runs. They intentionally require the wrapper command plus the semantic-density command and exact output paths for `prompt-contract-build.json`, `render-state-check.json`, `metro-audit-suite.json`, `metro-video-composition-audit.json`, and `metro-semantic-density-audit.json`. Do not hand-maintain a series prompt that only names `metro-style-audit.json`; that path can pass while the encoded MP4 still looks like a labeled slide sheet.

If `--manifest` is omitted, the wrapper attempts to parse a prompt-named report path such as `projects/<project-id>/artifacts/reviews/prompt-contract-build.json`. Prefer passing `--manifest` when the prompt gives an exact command, but do not fail a no-command workflow just because the manifest path needs to be derived from prose.

If the prompt names a `render-state` or `browser-state` JSON report path and the wrapper command has no state flags, the wrapper derives `--state-manifest` from that path and adds default semantic checks for the selected scaffold pattern. The derived checks include `visualPattern=<pattern>`, final-state and `false->true` late-mechanism reveal checks for that pattern, first/last preserved label containment where label headings are present, monotonic `visibleMechanismCount`, and distinct mechanism-count progression. For `systems-flow`, the defaults also require final `queueSlots=8`, final `visibleMechanismCount=6`, monotonic `queueSlots`, at least five distinct mechanism-count values, and at least three distinct queue-slot values so a flow video cannot pass with only late branch callouts. For `skill-tree`, the defaults also require final `routeCount=5`, monotonic `routeCount`, and at least three distinct route-count values under the wrapper's six-sample state check so a route map cannot pass with only late branch callouts. For `skill-tree-route`, the defaults require damage cluster, defense cluster, attribute bridge, keystone tradeoff, respec route, and late specialization transitions plus final `activeRouteNodeCount=8`, final `visibleMechanismCount=7`, monotonic `activeRouteNodeCount`, at least four distinct route-node counts, and at least five distinct mechanism-count values so tree-route videos prove path cost, side clusters, tradeoff, and late layer progression. For `state-machine`, the defaults require final `activeState=5`, monotonic `activeState`, and at least four distinct active-state values so lifecycle videos prove the main state path advances before recovery callouts are accepted. For `comparison-matrix`, the defaults require final `criteriaRevealed=4`, monotonic criteria reveal, and at least three distinct criteria counts so a decision video cannot pass with only the recommendation and guardrail panels. For `causal-loop`, the defaults require loop, delay, amplifier, damping, side-effect, and intervention transitions plus final `visibleMechanismCount=6` so a cause map cannot pass with only side-effect and intervention callouts. For `phase-timeline`, the defaults require risk, gate, handoff, and final milestone transitions plus final `activePhase=5`, monotonic `activePhase`, and distinct active-phase progression so a timeline cannot pass as a static checklist. For `dependency-map`, the defaults also require final `edgeCount=7`, monotonic `edgeCount`, and distinct edge-count progression so a map cannot pass with static or incomplete dependency edges. For `sequence-trace`, the defaults also require final `activeSpanCount=7`, monotonic `activeSpanCount`, and distinct span-count progression so static span rails or partial traces cannot masquerade as a complete trace reveal. For `sankey-flow`, the defaults require split, loss, bottleneck, merge, and output transitions plus final `activeFlowCount=7`, final `visibleMechanismCount=6`, monotonic `activeFlowCount`, at least four distinct active-flow counts, and at least five distinct mechanism-count values so a conversion video proves the flow advances through split, loss, transform, merge, bottleneck, and output states. For `swimlane-handoff`, the defaults require SLA, rework, approval, escalation, and completion transitions plus final `activeHandoffCount=8`, final `visibleMechanismCount=6`, monotonic `activeHandoffCount`, at least four distinct active-handoff counts, and at least five distinct mechanism-count values so a workflow video proves owner handoffs and exception routes rather than only static lanes. For `risk-bowtie`, the defaults require preventive, top-event, mitigative, consequence, degraded, and action transitions plus final `activeThreatCount=4`, final `visibleMechanismCount=7`, monotonic `activeThreatCount`, at least three distinct active-threat counts, and at least five distinct mechanism-count values so a risk video proves prevention, mitigation, degradation, and repair timing. For `scenario-tree`, the defaults require probability, risk, upside, decision, fallback, and outcome transitions plus final `activeScenarioCount=7`, final `visibleMechanismCount=7`, monotonic `activeScenarioCount`, at least four distinct active-scenario counts, and at least five distinct mechanism-count values so a scenario video proves branching futures before selecting an outcome. For `evidence-ladder`, the defaults require claim, counterevidence, source-gap, confidence, and recommendation transitions plus final `activeEvidenceCount=6`, final `visibleMechanismCount=6`, monotonic `activeEvidenceCount`, at least four distinct evidence counts, and at least five distinct mechanism-count values so research videos prove support, uncertainty, and recommendation timing. For `layered-architecture`, the defaults require cross-cutting, failure-path, observability, and rollout transitions plus final `activeLayerCount=6`, final `visibleMechanismCount=6`, monotonic `activeLayerCount`, at least four distinct layer counts, and at least five distinct mechanism-count values so architecture videos prove layer ownership and operational overlays. For `data-lineage`, the defaults require transform, quality-gate, drift, consumer, and rollback transitions plus final `activeLineageCount=6`, final `visibleMechanismCount=6`, monotonic `activeLineageCount`, at least four distinct lineage counts, and at least five distinct mechanism-count values so lineage videos prove provenance and operational trust checks.

When the same pass should also prove browser render state, add state-check options to the wrapper command instead of running a separate checker command:

```powershell
uv run --script skills/html-d3-anime-video-workflow/scripts/build_from_prompt_contract.py --prompt ../prompt.md --manifest projects/<project-id>/artifacts/reviews/prompt-contract-build.json --state-manifest projects/<project-id>/artifacts/reviews/render-state-check.json --state-expect visualPattern=<pattern> --state-expect-final <late-key>=true --state-expect-transition <late-key>=false->true --state-expect-contains <label-array-key>="<exact label>" --state-expect-monotonic visibleMechanismCount=nondecreasing --state-min-distinct visibleMechanismCount=4
```

The wrapper runs `check_html_render_state.py` after the scaffold is generated and records a `stateCheck` object in the wrapper report. A nonzero state-check exit adds a wrapper finding and makes the wrapper fail. Use explicit state flags when the prompt needs stricter checks than the derived defaults. For Metro design-fidelity checks, include or inspect `visibleZoneCount` and `activeZoneId` in the state summary; a useful megacanvas should expose at least five visible zones and several distinct active zones over the sampled duration.

Standard prompt-contract headings:

- `Preserve these source facts` -> repeated `--fact`.
- `Preserve these visual anchors` -> repeated `--anchor`.
- `Preserve these causal variables` -> repeated `--node-label`.
- `Preserve these decision options` -> repeated `--option-label`.
- `Preserve these decision criteria` -> repeated `--criterion-label`.
- `Preserve these lifecycle states` -> repeated `--state-label`.
- `Preserve these transition guards` -> repeated `--guard-label`.
- `Preserve these system components` -> repeated `--system-label`.
- `Preserve these tree nodes` -> repeated `--tree-label`.
- `Preserve these strategy meters` -> repeated `--meter-label`.
- `Preserve these route labels` -> repeated `--route-label`.
- `Preserve these checkpoint labels` -> repeated `--checkpoint-label`.
- `Preserve these timeline phases` -> repeated `--phase-label`.
- `Preserve these metric labels` -> repeated `--metric-label`.
- `Preserve these threshold labels` -> repeated `--threshold-label`.
- `Preserve these dependency labels` -> repeated `--dependency-label`.
- `Preserve these dependency clusters` -> repeated `--cluster-label`.
- `Preserve these trace labels` -> repeated `--trace-label`.
- `Preserve these flow labels` -> repeated `--flow-label`.
- `Preserve these lane labels` -> repeated `--lane-label`.
- `Preserve these handoff labels` -> repeated `--handoff-label`.
- `Preserve these threat labels` -> repeated `--threat-label`.
- `Preserve these barrier labels` -> repeated `--barrier-label`.
- `Preserve these consequence labels` -> repeated `--consequence-label`.
- `Preserve these scenario labels` -> repeated `--scenario-label`.
- `Preserve these probability labels` -> repeated `--probability-label`.
- `Preserve these claim labels` -> repeated `--claim-label`.
- `Preserve these evidence labels` -> repeated `--evidence-label`.
- `Preserve these layer labels` -> repeated `--layer-label`.
- `Preserve these concern labels` -> repeated `--concern-label`.
- `Preserve these lineage labels` -> repeated `--lineage-label`.
- `Preserve these quality labels` -> repeated `--quality-label`.

Do not read broader design or production-loop references before this wrapper path. Use them only after the scaffold exists and the task requires bespoke visual redesign, deeper critique, or a project-specific capture pipeline.

## Manual Fallback Command Shape

Use this only when the wrapper is unavailable, cannot parse the prompt, or the prompt requires a nonstandard helper command.

```powershell
uv run --script skills/html-d3-anime-video-workflow/scripts/build_standalone_explainer.py --project-root <project-root> --title "<title>" --topic "<topic>" --output-id <output-id> --pattern <pattern> --checked-date "<date>" --duration <seconds> --fps <fps> --width <width> --height <height> --fact "<fact>" --anchor "<anchor>"
```

Repeat `--fact`, `--anchor`, and `--source-url` for every supplied item. Use `--edge-style square` for Metro Minimal Tonal Motion, strict-grid, technical, editorial-grid, terminal, blueprint, or hard-edge style requests. For those requests, boxes should use no internal padding: content, bars, and fills are flush to the declared box bounds or represented as separate adjacent objects, and hierarchy should be separated with multiple grayscale levels rather than extra inset panels.

## Path Derivation

Derive `--project-root` from the shared prefix that contains the requested `source/`, `src/`, and `artifacts/` directories.

Examples:

- Required `projects/example-video/source/source-package.json` and `projects/example-video/artifacts/video-renders/draft/videos/example.mp4` -> `--project-root projects/example-video`.
- Required MP4 `projects/example-video/artifacts/video-renders/draft/videos/example.mp4` -> `--output-id example`.

Never derive these values from the title when exact output paths are listed.

## Pattern Selection

For Metro design-following work, choose the density mix before relying on a helper pattern:

```powershell
uv run --script skills/html-d3-anime-video-workflow/scripts/plan_metro_pattern_mix.py --prompt-file ../prompt.md --output projects/<project-id>/artifacts/reviews/metro-pattern-mix.json
```

Require the report's `passed` field to be `true`. If the wrapper already embeds `metroPatternMix`, use that embedded result instead of running the selector again.

When the embedded `metroPatternMix.masonryContract.required` is true, the wrapper should pass `--masonry-layout` to the helper. The generated source package must include `masonryLayout.required: true` and `masonryModules`, and the rendered SVG must expose `data-masonry-module` rectangles so the rendered-frame and semantic-density audits can prove module count, size variety, occupied area, construction over time, and low text dependency. It must also expose each visual-zone source anchor through `data-source-anchor-json` on rendered rectangles so low-text Masonry can still prove source binding without visible labels. The rendered-frame report should include `masonryModuleCounts`, nondecreasing growth, at least three distinct module counts, enough count range, and low `maxTextElementCount`/`maxTextCharacterCount` for required Masonry. Do not accept a Masonry plan that renders as equal cards, padded panels, plain systems-flow columns, or many small labels.

Use `--pattern skill-tree-route` for advanced passive-tree pathing, route planners, travel-node cost, build-route, respec-checkpoint, keystone-tradeoff, or late-specialization explainers where path cost and progression layers matter.

For `skill-tree-route`, pass up to eight `--route-label` values for class start, travel nodes, damage cluster, defense cluster, attribute bridge, keystone tradeoff, respec checkpoint, and late specialization. Pass up to five `--checkpoint-label` values for build checkpoints or review gates. Preserve exact labels in `source-package.json`; the renderer may compact long labels visually. A useful tree-route video needs main route growth, side clusters, bridge cost, keystone tradeoff, respec route, and late specialization as separate mechanisms.

Use `--pattern skill-tree` for simpler passive-tree, route-map, build-path, keystone, Atlas, or game strategy-map explainers.

For `skill-tree`, pass up to eleven `--tree-label` values when the prompt supplies concrete passive-tree nodes. The order is start, early support, notable, damage branch, defense branch, attribute checkpoint, gear checkpoint, keystone/tradeoff, Atlas node 1, Atlas node 2, and Atlas node 3. Pass up to three `--meter-label` values for the bottom strategy meters. Preserve exact labels in `source-package.json`; the renderer may compact long labels visually.

Use `--pattern systems-flow` for architecture, reliability, queue, retry, feedback-loop, event pipeline, worker-pool, backpressure, dead-letter, or multi-stage process explainers.

For `systems-flow`, pass up to eleven `--system-label` values when the prompt supplies concrete components. The order is intake source, intake event, intake signal, bus, queue, worker pool, store, retry control, dead-letter control, throughput metric, and throttle. Preserve the exact labels in `source-package.json`; the renderer may compact long labels visually.

Use `--pattern state-machine` for lifecycle, workflow state, guarded transition, approval state, rollback, compensation, invariant restoration, or terminal-state explainers.

For `state-machine`, pass up to six `--state-label` values and up to three `--guard-label` values when the prompt supplies lifecycle states or transition guards. Preserve the exact labels in `source-package.json`; the renderer may compact long labels visually.

Use `--pattern comparison-matrix` for option comparisons, tradeoff explainers, decision matrices, scorecards, criteria-weighted choices, recommendation rationale, or guardrail-based selection.

For `comparison-matrix`, pass up to three `--option-label` values and up to four `--criterion-label` values when the prompt supplies decision options or criteria. Preserve the exact labels in `source-package.json`; the renderer may compact long labels visually.

Use `--pattern causal-loop` for causal-loop maps, feedback loops, reinforcing or balancing loops, delayed effects, side effects, root-cause explainers, leverage points, or intervention strategy.

For `causal-loop`, pass up to six `--node-label` values when the prompt supplies causal variables. The order is trigger, pressure, behavior, outcome, side-effect, and intervention. Preserve the exact labels in `source-package.json`; the renderer may compact long labels visually.

Use `--pattern phase-timeline` for chronological plans, roadmaps, release plans, incident timelines, milestone explainers, approval calendars, or phase-based project narratives.

For `phase-timeline`, pass up to six `--phase-label` values when the prompt supplies phase names. The order is chronological from left to right. Preserve exact labels in `source-package.json`; the renderer may compact long labels visually.

Use `--pattern metric-dashboard` for KPI, SLO, threshold, trend, anomaly, burn-rate, error-budget, forecast, metric-health, or decision-dashboard explainers.

For `metric-dashboard`, pass up to five `--metric-label` values for primary, input, output, quality, and risk metrics. Pass up to three `--threshold-label` values for healthy, warning, and action thresholds. Preserve exact labels in `source-package.json`; the renderer may compact long labels visually. Derived state checks should prove trend and threshold visibility as well as anomaly, forecast, and decision visibility.

Use `--pattern dependency-map` for dependency graphs, DAG explainers, migration dependencies, blocked-by maps, bottleneck analysis, release cutovers, fallback planning, or cross-team readiness videos.

For `dependency-map`, pass up to eight `--dependency-label` values for source feed, identity, normalizer, policy check, data contract, integration, release gate, and fallback route. Pass up to three `--cluster-label` values for source, integration, and release clusters. Preserve exact labels in `source-package.json`; the renderer may compact long labels visually. Keep low-contrast ghost labels visible from the first frame, then reinforce active nodes as dependency proof advances, so the opening contact-sheet tile is interpretable instead of an unlabeled topology.

Use `--pattern sequence-trace` for distributed traces, request traces, span waterfalls, latency-budget investigations, critical-path explainers, service-call debugging, retry/fallback analysis, or observability videos.

For `sequence-trace`, pass up to eight `--trace-label` values for client request, edge gateway, auth span, inventory span, payment span, database wait, fallback cache, and response. Preserve exact labels in `source-package.json`; the renderer may compact long labels visually. A useful trace video needs fixed service lanes, span-duration bars, parent-child handoff markers, critical-path emphasis, latency-budget state, retry branch, fallback route, and final response as separate mechanisms.

Use `--pattern sankey-flow` for Sankey maps, conversion flows, value streams, flow splits, dropoff analysis, retained/lost value, transformation lanes, merge points, bottleneck analysis, or output-readiness videos.

For `sankey-flow`, pass up to eight `--flow-label` values for input stream, retained branch, loss branch, transform A, transform B, merge point, bottleneck, and final output. Preserve exact labels in `source-package.json`; the renderer may compact long labels visually. A useful Sankey video needs one input band, explicit value and loss branches, parallel transforms, a merge point, bottleneck state, separate input/retained/output meters, and delayed final output as separate mechanisms.

Use `--pattern swimlane-handoff` for swimlane diagrams, role-lane workflows, cross-team handoffs, service-level workflows, approval routes, rework loops, escalation paths, ownership transfer, or completion-readiness videos.

For `swimlane-handoff`, pass up to four `--lane-label` values for owner or team lanes and up to eight `--handoff-label` values for process steps in order. Preserve exact labels in `source-package.json`; the renderer may compact long labels visually. A useful swimlane video needs fixed owner lanes, a moving handoff path, SLA pressure, approval gate, rework loop, escalation path, and delayed completion as separate mechanisms.

Use `--pattern risk-bowtie` for risk bowties, hazard analysis, barrier analysis, top-event explainers, preventive versus mitigative control stories, degraded-control reviews, assurance gaps, residual risk, or repair-action videos.

For `risk-bowtie`, pass up to four `--threat-label` values, up to six `--barrier-label` values in preventive-then-mitigative order, and up to four `--consequence-label` values. Preserve exact labels in `source-package.json`; the renderer may compact long labels visually. A useful bowtie video needs threats, preventive barriers, top event, mitigative barriers, consequences, degraded barrier, residual risk, and repair action as separate mechanisms.

Use `--pattern scenario-tree` for scenario trees, decision trees, branching futures, probability branches, expected-value reasoning, upside/downside strategy, fallback scenarios, or selected-outcome videos.

For `scenario-tree`, pass up to seven `--scenario-label` values for decision root, scenario branches, and outcomes, plus up to four `--probability-label` values for branch probabilities or weights. Preserve exact labels in `source-package.json`; the renderer may compact long labels visually. A useful scenario video needs decision root, scenario branches, probability labels, evidence weight, upside branch, risk branch, fallback route, decision gate, and selected outcome as separate mechanisms.

Use `--pattern evidence-ladder` for research evidence, claim support, source-confidence, counterevidence, source-gap, confidence-ladder, methodology caveat, or recommendation-confidence videos.

For `evidence-ladder`, pass up to four `--claim-label` values for working claim, baseline reading, counterclaim, and recommendation. Pass up to six `--evidence-label` values for supporting evidence tiers, counterevidence, source gap, and decision evidence. Preserve exact labels in `source-package.json`; the renderer may compact long labels visually. A useful evidence video needs claim, tiered support, counterevidence, source gap, confidence, uncertainty, and delayed recommendation as separate mechanisms.

Use `--pattern layered-architecture` for layered architecture, layer stacks, platform architecture, cross-cutting concerns, observability layers, failure routing, or rollout-gate videos.

For `layered-architecture`, pass up to six `--layer-label` values in top-to-bottom order and up to four `--concern-label` values for cross-cutting policy, failure route, observability, and rollout gate. Preserve exact labels in `source-package.json`; the renderer may compact long labels visually. A useful architecture video needs layer activation, request path, cross-cutting policy, failure path, observability, and rollout gate as separate mechanisms.

Use `--pattern data-lineage` for data lineage, lineage graphs, data pipelines, ETL/ELT flows, schema checks, freshness windows, drift monitoring, source-to-consumer maps, or rollback-readiness videos.

For `data-lineage`, pass up to six `--lineage-label` values from source through consumer, plus up to four `--quality-label` values for schema, freshness, drift, and rollback controls. Preserve exact labels in `source-package.json`; the renderer may compact long labels visually. A useful lineage video needs source-to-consumer activation, transform rule, quality gate, drift monitor, consumer contract, and rollback route as separate mechanisms.

Use `--pattern auto` only when the prompt does not make the visual pattern clear.

## Default Outputs

For `--project-root projects/<project-id>` and `--output-id <output-id>`, the helper writes:

- `projects/<project-id>/source/source-package.json`
- `projects/<project-id>/source/production-notes.md`
- `projects/<project-id>/src/index.html`
- `projects/<project-id>/src/render.mjs`
- `projects/<project-id>/artifacts/video-renders/draft/videos/<output-id>.mp4`
- `projects/<project-id>/artifacts/video-renders/draft/review/<output-id>-contact-sheet.jpg`
- `projects/<project-id>/artifacts/video-renders/draft/review/<output-id>-contact-sheet.json`
- `projects/<project-id>/artifacts/reviews/self-review.md`

The generated HTML exposes `window.renderConceptFrame(videoId, seconds, options)` for Chromium capture.

Use `check_html_render_state.py` for a fast browser semantic check when you need to prove the HTML contract, exact labels, or late mechanism states without encoding another MP4:

```powershell
uv run --script skills/html-d3-anime-video-workflow/scripts/check_html_render_state.py --html projects/<project-id>/src/index.html --video-id <output-id> --duration <seconds> --samples 6 --manifest projects/<project-id>/artifacts/reviews/render-state-check.json --expect-state visualPattern=<pattern> --expect-state-final <late-key>=true --expect-state-transition <late-key>=false->true --expect-state-contains <label-array-key>="<exact label>" --expect-state-monotonic visibleMechanismCount=nondecreasing --min-distinct-state visibleMechanismCount=4
```

For `systems-flow`, the returned render state includes `visualPattern`, `sourceFacts`, `beat`, `systemLabels`, `queueSlots`, `workerActive`, `retryVisible`, `deadLetterVisible`, `feedbackVisible`, `visibleMechanismCount`, `visibleZoneCount`, and `activeZoneId`. Derived state checks should prove the queue fills to eight slots, mechanism count reaches six, zones are visible, and retry, dead-letter, feedback, and active-zone states transition from hidden or early to visible later states. Use `--state-expect-final visibleZoneCount=<count>` for zone count and `--min-distinct-state activeZoneId=<count>` for traversal; do not require distinct `visibleZoneCount` values.

For every generated pattern, the returned render state also includes `visibleZoneCount` and `activeZoneId` when the helper's zone overlay is active. Use `visibleZoneCount` as a stable count and `--min-distinct-state activeZoneId=3` for Metro repair tasks that need proof of camera or beat progression through the megacanvas.

For `skill-tree`, the returned render state includes `visualPattern`, `sourceFacts`, `treeLabels`, `meterLabels`, `routeCount`, `damageBranchVisible`, `defenseBranchVisible`, `keystoneVisible`, `atlasVisible`, and `visibleMechanismCount`.

For `skill-tree-route`, the returned render state includes `visualPattern`, `sourceFacts`, `routeLabels`, `checkpointLabels`, `activeRouteNodeCount`, `damageClusterVisible`, `defenseClusterVisible`, `attributeBridgeVisible`, `keystoneTradeoffVisible`, `respecVisible`, `lateClusterVisible`, and `visibleMechanismCount`.

For `state-machine`, the returned render state includes `visualPattern`, `sourceFacts`, `stateLabels`, `guardLabels`, `activeState`, `rollbackVisible`, `compensationVisible`, `terminalVisible`, and `visibleMechanismCount`. Derived state checks should prove `activeState` advances monotonically to the final state before rollback, compensation, and terminal-state checks are accepted.

For `comparison-matrix`, the returned render state includes `visualPattern`, `sourceFacts`, `optionCount`, `criteriaRevealed`, `scoreShiftVisible`, `tradeoffVisible`, `recommendationVisible`, `guardrailVisible`, and `visibleMechanismCount`. Derived state checks should prove all four criteria reveal monotonically and that score-shift, tradeoff, recommendation, and guardrail states transition from hidden to visible.

If decision options or criteria were provided, `source-package.json` includes `decisionOptions` and `decisionCriteria`, and the `comparison-matrix` render state returns those exact labels.

For `causal-loop`, the returned render state includes `visualPattern`, `sourceFacts`, `loopVisible`, `delayVisible`, `amplifierVisible`, `dampingVisible`, `sideEffectVisible`, `interventionVisible`, and `visibleMechanismCount`. Derived state checks should prove all six mechanisms transition from hidden to visible and that the final mechanism count reaches six.

If causal variables were provided, `source-package.json` includes `causalLabels`, and the `causal-loop` render state returns those exact labels.

For `phase-timeline`, the returned render state includes `visualPattern`, `sourceFacts`, `phaseLabels`, `activePhase`, `riskVisible`, `gateVisible`, `handoffVisible`, `finalVisible`, and `visibleMechanismCount`. Derived state checks should prove risk, gate, handoff, and final milestone transitions, plus monotonic `activePhase` progress through the final phase.

For `metric-dashboard`, the returned render state includes `visualPattern`, `sourceFacts`, `metricLabels`, `thresholdLabels`, `activeMetric`, `trendVisible`, `thresholdVisible`, `anomalyVisible`, `forecastVisible`, `decisionVisible`, and `visibleMechanismCount`.

For `dependency-map`, the returned render state includes `visualPattern`, `sourceFacts`, `dependencyLabels`, `clusterLabels`, `edgeCount`, `riskVisible`, `bottleneckVisible`, `cutoverVisible`, `fallbackVisible`, and `visibleMechanismCount`.

For `sequence-trace`, the returned render state includes `visualPattern`, `sourceFacts`, `traceLabels`, `activeSpanCount`, `criticalPathVisible`, `latencyBudgetVisible`, `retryVisible`, `fallbackVisible`, `responseVisible`, and `visibleMechanismCount`.

For `sankey-flow`, the returned render state includes `visualPattern`, `sourceFacts`, `flowLabels`, `activeFlowCount`, `splitVisible`, `lossVisible`, `bottleneckVisible`, `mergeVisible`, `outputVisible`, and `visibleMechanismCount`.

For `swimlane-handoff`, the returned render state includes `visualPattern`, `sourceFacts`, `laneLabels`, `handoffLabels`, `activeHandoffCount`, `slaVisible`, `reworkVisible`, `approvalVisible`, `escalationVisible`, `completeVisible`, and `visibleMechanismCount`.

For `risk-bowtie`, the returned render state includes `visualPattern`, `sourceFacts`, `threatLabels`, `barrierLabels`, `consequenceLabels`, `activeThreatCount`, `preventiveVisible`, `topEventVisible`, `mitigativeVisible`, `consequenceVisible`, `degradedVisible`, `actionVisible`, and `visibleMechanismCount`.

For `scenario-tree`, the returned render state includes `visualPattern`, `sourceFacts`, `scenarioLabels`, `probabilityLabels`, `activeScenarioCount`, `probabilityVisible`, `riskVisible`, `upsideVisible`, `decisionVisible`, `fallbackVisible`, `outcomeVisible`, and `visibleMechanismCount`.

For `evidence-ladder`, the returned render state includes `visualPattern`, `sourceFacts`, `claimLabels`, `evidenceLabels`, `activeEvidenceCount`, `claimVisible`, `counterEvidenceVisible`, `gapVisible`, `confidenceVisible`, `recommendationVisible`, and `visibleMechanismCount`.

For `layered-architecture`, the returned render state includes `visualPattern`, `sourceFacts`, `layerLabels`, `concernLabels`, `activeLayerCount`, `crossCuttingVisible`, `failurePathVisible`, `observabilityVisible`, `rolloutVisible`, and `visibleMechanismCount`.

For `data-lineage`, the returned render state includes `visualPattern`, `sourceFacts`, `lineageLabels`, `qualityLabels`, `activeLineageCount`, `transformVisible`, `qualityGateVisible`, `driftVisible`, `consumerVisible`, `rollbackVisible`, and `visibleMechanismCount`.

## Required Validation

After running the helper:

1. Verify exact requested paths, not nearby title-derived paths.
2. Read the contact-sheet JSON manifest and require top-level `"passed": true`.
3. Read the wrapper report and verify `sourcePreservation.missingFacts` and `sourcePreservation.missingAnchors` are empty.
4. Read the wrapper report and verify the `media.actual` values match requested duration, fps, width, and height.
5. Read the wrapper report and require `contactSheet.passed` to be `true`, with nonempty `sampleTimes`, per-tile metric arrays, `metrics.changingPairs`, `openingTile`, `finalTile`, `openingTileAssessment`, and no `contactSheet.findings`. If `openingTileAssessment.weak` is true, the wrapper should also include a `weak-opening-tile` finding and fail; improve the opening frame before accepting the draft.
6. Read `self-review.md` and ensure it critiques the draft rather than claiming final quality.
7. If the wrapper command used or derived `--state-manifest`, read the wrapper report and require `stateCheck.passed` to be `true`; also read the state manifest when diagnosing failures.
8. If the wrapper command used or derived Metro audit manifests, require `metroAuditSuite.passed`, `metroStyleAudit.passed`, `metroCompositionAudit.passed`, and `metroRenderedFrameAudit.passed` to be `true`; read the audit manifests when diagnosing palette, rounded-border, grid, shared-edge, box-padding, rendered-frame, or grayscale-hierarchy failures.
9. Run `check_html_render_state.py` directly when you need a separate quick Chromium proof of exact labels, pattern identity, late mechanism visibility, or state progression without re-encoding an MP4.
10. If full browser proof is needed, run `capture_html_video.py` against `src/index.html` and assert semantic state values.
11. For Metro polished-output prompts, run `audit_metro_semantic_density.py` against the wrapper report, state manifest, contact-sheet manifest, Metro audit suite, mute-test audit, and MP4 composition audit. Require top-level `"passed": true` before accepting the video as design-ready; the rendered-frame evidence should include low text-area ratio, enough mark-to-text density, zero title-band text, rendered source anchors, and, when Masonry is required, real module count/size/construction/low-text evidence. The MP4 composition evidence should include distributed grid coverage, four-quadrant occupation, non-weak opening composition, spatial progression, and low text-like component pressure. The semantic-density auditor requires `wrapper.metroPatternMix` by default, checks that `selected.helperPattern` matches the rendered `source-package.json.visualPattern`, requires `source-package.json.semanticBindings`, and fails weak pattern, zone, source-anchor visual binding, motion, camera, transition, anti-pattern-risk, padding, radius, grayscale, or encoded-MP4 composition contracts.

## Scaffold Acceptance Boundary

The helper and wrapper produce a validated scaffold. Treat a passing scaffold as final only when the prompt asks for a first runnable draft, exact-output smoke, or mechanical validation.

For Metro Minimal Tonal Motion, design-fidelity, complex dynamic, low-text narrated, or polished final requests, a passing wrapper means the artifact is ready for critique, not accepted. Load `metro-minimal-tonal-motion.md` and `visual-density-pattern-bank.md`, then reject or improve the artifact if it is slide-like, text-dependent, too static, rounded, padded, weakly aligned, missing camera exploration, lacking enough semantic motion systems, has a weak opening tile, or shows different design behavior in the encoded MP4 contact sheet than in the sampled HTML audits.

If an exact path is missing, rerun the helper with corrected `--project-root` or `--output-id`; do not rename files after generation unless the user explicitly asked for a manual file move.

If the wrapper report and generated contact-sheet manifest already have top-level `"passed": true`, do not regenerate the requested contact sheet at the same path. Extra quality checks should write separate review reports or alternate contact sheets so they cannot degrade the exact required artifacts.
