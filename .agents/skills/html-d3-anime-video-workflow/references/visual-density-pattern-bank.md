# Visual Density Pattern Bank

Use this reference when a video should be more complex, dynamic, information-dense, or less dependent on visible text. It is a compact video-facing pattern bank distilled from reusable D3 and systems-animation patterns so an isolated skill workspace can still choose stronger visual structures.

Choose patterns after the metaphor decision. A pattern is valid only when its geometry keeps the same semantic role as the concept.

## Density Principles

- Add information through encoded marks, flows, hierarchy, and state transitions, not through paragraphs.
- Use at least three semantic systems for substantial explainers: a primary mechanism, a secondary metric or state, and a camera or transition system.
- Prefer small multiples, matrices, tables with embedded bars, edge routes, state boards, and layered architecture over isolated labeled boxes.
- Preserve object identity through motion. A packet, token, request, dependency, claim, or row should remain trackable after it moves or transforms.
- Keep labels functional and local to objects. Narration carries definitions and caveats. Do not use ellipsized labels; recomposition is better than hiding source meaning behind `...`.
- For Metro work, adapt every pattern into square 4 px grid geometry, zero internal padding, colorset1, and grayscale hierarchy.

## Scripted Pattern Mix Gate

For Metro, complex, dynamic, low-text, or "not following the design" feedback, run the deterministic selector before accepting a scaffold:

```powershell
uv run --script skills/html-d3-anime-video-workflow/scripts/plan_metro_pattern_mix.py --prompt-file ../prompt.md --output projects/<project-id>/artifacts/reviews/metro-pattern-mix.json
```

In repository maintenance, use the repo-relative path:

```powershell
uv run --script .agents/skills/html-d3-anime-video-workflow/scripts/plan_metro_pattern_mix.py --prompt-file design/videos.md --output projects/<project-id>/artifacts/reviews/metro-pattern-mix.json
```

Require `passed: true`, at least six `patternIdsNamed`, at least three `patternsUsedInBeats`, five `functionalZones`, four `semanticMotionSystems`, and three `cameraPath` events. Use `selected.helperPattern` only for the first runnable helper scaffold; use `primaryPattern`, `secondaryPattern`, `supportPatterns`, zones, motion systems, transition contracts, `reusableD3PatternIds`, and `antiPatternRisks` as the actual design brief. A result that passes the helper wrapper but ignores these fields is still a design failure.

For Metro Minimal Tonal Motion, megacanvas, modular-map, or design-rejection prompts, require the mix to include `masonry-wall` as a layout armature or support pattern and require a `masonry-construction` transition contract when Masonry is present. The planner exposes this as `masonryContract.required`, `masonryContract.patternIncluded`, and `masonryContract.transitionIncluded` so isolated checks can reject a mix without walking arrays. This turns Masonry from a prose option into a concrete design path: differently sized modules enter, fit, and stabilize into an ordered wall instead of appearing as equal cards or disconnected slides.

For rendered Metro outputs, the semantic-density auditor must also see this mix. `scripts/audit_metro_semantic_density.py` defaults to requiring `wrapper.metroPatternMix`, verifies the mix passed, checks that `selected.helperPattern` matches the rendered `source-package.json.visualPattern`, and rejects weak pattern counts, missing zones, missing motion systems, missing camera events, missing transition contracts, too few transition types, missing modular transition types, required Masonry contracts without `masonry-wall` plus `masonry-construction` evidence, missing anti-pattern risks, nonzero mix padding, rounded mix geometry, or weak mix grayscale hierarchy. It also checks that the rendered artifact exposes real zones through `source-package.json.visualZones`, source-anchor-to-zone/mechanism/state mappings through `source-package.json.semanticBindings`, render-state `visibleZoneCount`, changing `activeZoneId`, and `activeSourceAnchors`, an ordered continuity path in `statesSample` with adjacent zone changes coupled to camera/reframe deltas, live SVG `data-zone-id`/`data-zone-role`/`data-source-anchor-json` markers with legacy `data-source-anchor` fallback, `metro-video-composition-audit.json` evidence that the encoded MP4/contact sheet has distributed grid coverage and spatial progression, and `metro-mute-test-audit.json` evidence that the text-hidden frame sequence still changes through marks, zones, and gray hierarchy, so a planning-only, label-only, source-scrambled, or raster-slide-like mix cannot pass.

`sourceAnchorVisualBindingCoverage` should be `1.0` for exact-output Metro validation: every required source anchor must appear in `semanticBindings`, in rendered `data-source-anchor-json` evidence, and in at least one render-state sample's `activeSourceAnchors`. This is the guard against generic diagrams that preserve anchors in arrays while the visible motion explains something else.

When `masonryContract.required` is true, rendered acceptance must include real module geometry, not just a named pattern. The helper should emit `masonryLayout.required`, `masonryModules`, and SVG `data-masonry-module` rectangles; the rendered-frame audit should prove at least six modules, at least four distinct module sizes, enough masonry area for the wall to read as the main composition, `masonryModuleCounts` growth over time, nondecreasing construction, and low text-element/text-character counts. The encoded MP4 contact sheet should also visibly follow this wall-construction contract and pass `audit_metro_video_composition.py`; reject outputs where the browser audit is low-text but the MP4 still shows labeled systems-flow boxes, weak quadrant distribution, or static slide-like tiles.

The encoded MP4 audit must also keep colorset1 red in a signal role. Inspect `summary.maxRedAreaRatio` from `metro-video-composition-audit.json`; values above `0.14` mean red-family pixels occupy too much of the delivered frame sequence. Recompose broad red blocks into grayscale modules with thin red edges, routes, caps, or active-state marks before accepting the video.

For matrix, evidence, and layered-architecture Masonry videos, keep the lower half of the encoded frame semantically occupied. Use a non-text evidence floor: small state tiles, verification bars, score blocks, or confidence columns snapped to the same 4 px grid. This prevents a rich upper matrix from becoming a three-quadrant composition in the MP4 while still avoiding captions or explanatory labels.

When a `design/videos.md` module names exact visual anchors, treat them as visible geometry requirements, not only source-preservation strings. For LLM probability/evaluation modules, `probability_bars`, context-window shifts, `passN_grid`, `test_runner`, and judge/rubric cues should render as distinct low-text marks inside the Masonry megacanvas: distribution bars, poor-to-rich context matrices, pass@N sample cells, executable-check rows, and rubric/gauge blocks. A generic comparison matrix that preserves those words in manifests but does not show those motifs is a design failure.

For Agent definition modules, `agent_loop_ring`, `context_window_box`, environment changes, fixed workflow versus adaptive agent lanes, approval checkpoint, and Model + Tools + State + Loop cues are also geometry contracts. The render should show a central observe-act-check-continue loop ring, stacked context panes feeding model state, mutable environment surfaces such as repo/browser/ticket/docs/database blocks, a straight fixed-workflow lane contrasted with a branching/replanning adaptive-agent lane, a hard-edge approval checkpoint, and four final Model/Tools/State/Loop modules. A generic `systems-flow` queue/worker/retry/dead-letter diagram that only preserves those words in labels or JSON is a design failure.

For Guardrail modules, `shield_gate`, `agent_loop_ring`, Input/Output/Action gates, prompt bubble versus hard gate, Model Armor filter lanes, `risk_score`, human approval, protected `.env`/destructive/deploy actions, safety-versus-friction balance, positive versus blocked paths, and policy matrix cues are geometry contracts. The render should show a hard shield closing over an agent loop, three separate inspection gates for prompt/output/tool-call streams, low-text risk and outcome modules for block/redact/route/escalate, an approval modal over risky deploy-style action tiles, a colorset1 gray/red policy matrix, and separate pass/stop paths. Guardrail red must be a thin edge, route, cap, or stop marker on gray modules; do not fill the shield, risk score, protected actions, or policy row as broad red slabs. A generic `risk-bowtie` threat/prevention/top-event/consequence diagram that only preserves those words in labels or JSON is a design failure.

For Harness modules, `comparison_grid`, runtime stack, engine-to-dashboard morph, same model badge in different shells, three-column harness cards, `credit_meter`, feature grid, use-case matrix, selection path, and any reused `agent_loop_ring` are geometry contracts. The render should show a comparison grid that zooms or routes into one runtime stack, layers for instructions/tools/permissions/loop/logging assembling around the model, a raw model core morphing into dashboard controls, the same model badge entering three visibly different Copilot/Claude Code/OpenCode-style shells, a cost meter rising with tool/context/retry/loop growth, and a final fit matrix with a highlighted selection path. A generic `systems-flow` queue/worker/retry/dead-letter diagram that only preserves those words in labels or JSON is a design failure.

For AI alternatives modules, Atlassian Rovo, Gemini App, GitHub Copilot, Claude Desktop or Claude Code, `comparison_grid`, home-base workspace, radar chart, `credit_meter`, workflow gravity, use-case selector, guardrails, permissions, and observability are geometry contracts. The render should show one four-column comparison surface, four visibly distinct workspace-home signatures tied to natural work surfaces, a fit radar that turns into use-case quadrants, four cost or credit meters, and a workflow-gravity selector whose selected route is wrapped by governance/observability blocks. Do not draw these as four padded product cards; all subdivisions should share edges or be declared fills, with no internal padding and no rounded borders. Product identity should come from geometry: Rovo can read as organizational knowledge/status grids, Gemini as a cross-quadrant personal workspace, Copilot as IDE/repo lanes plus branch routing, and Claude as terminal/research panes plus loop routing. Use gray hierarchy for the workspace surfaces and keep red as thin state edges, route strokes, or meter caps; the semantic-density gate should reject AI alternatives when `maxRedRectAreaRatio` exceeds `0.10`.

For Harness Hook modules, `event_timeline`, lifecycle event nodes, `shield_gate`, GitHub hook badges, Claude event cloud, OpenCode event list, PreToolUse Bash command block, dangerous-command stop path, log-filter/preprocessing path, hook-job cascade, token-savings counter, speed-vs-cost slider, and lifecycle-controls stamp are geometry contracts. The render should show one event pulse moving through lifecycle boundaries, a hard shield overlay converting events into executable policy, three provider/event surfaces with distinct geometry, one blocked destructive-command path, one filtered-output path that visibly shrinks context, and opposing token-savings versus latency/cost meters. Use gray fills for lifecycle panels and blocked-command modules, with red limited to a denial path, thin shield edge, latency cap, or command-stop marker. A generic `systems-flow` queue/worker/retry/dead-letter diagram, or a generic Harness shell comparison, that only preserves Hook words in labels or JSON is a design failure.

For Skill definition modules, `skill_card_stack`, `SKILL.md`, the long prompt wall collapse, compatible GitHub/Claude/OpenCode folder structures, progressive disclosure, cost meter or cost line, deploy-preview or example skill cards, tool badges, script blocks, read-surface levels, bloated mini-novel trimming, and `Skill = on-demand reusable workflow` are geometry contracts. The render should show reusable skill cards fanning open only when relevant, a large static prompt wall shrinking into one scoped skill card, three hard-edge folder structures snapping to the same `SKILL.md` resource model, a cost meter that stays flat until activation, example workflow cards cycling through deploy/debug/architecture/onboarding/codebase-map use cases, tool and script modules attaching to the active card, a bloated skill being cut down, and a final reusable workflow stamp. Trimmed or active skill elements should remain grayscale surfaces with red only as cut marks or small removed-token indicators. A generic `systems-flow` queue/worker/retry/dead-letter diagram that only preserves Skill words in labels or JSON is a design failure.

## Series Pattern Diversity Gate

When the source contains several videos or `###` modules, do not run only one global pattern mix over the whole document. A full-document mix tends to select the strongest repeated keywords and can hide that individual topics need different visual metaphors.

Run the series planner:

```powershell
uv run --script skills/html-d3-anime-video-workflow/scripts/plan_metro_video_series.py --prompt-file ../prompt.md --output projects/<project-id>/artifacts/reviews/metro-video-series-plan.json
```

In repository maintenance:

```powershell
uv run --script .agents/skills/html-d3-anime-video-workflow/scripts/plan_metro_video_series.py --prompt-file design/videos.md --output projects/<project-id>/artifacts/reviews/metro-video-series-plan.json
```

Require `passed: true`. The report should expose one module per timed-video section, per-module `helperPattern`, `primaryPattern`, `secondaryPattern`, `supportPatterns`, `reusableD3PatternIds`, and aggregate metrics for helper diversity, primary-pattern diversity, reusable D3 pattern count, and maximum repeated-helper run. If `maxSameHelperRun` is high, helper diversity is low, or every module collapses to `systems-flow`, redesign the batch before rendering. Individual video audits can still pass while the series fails visually because the videos share the same scaffold too often.

For a series repair after feedback that the videos are not following the design, use the series contract generator instead of hand-writing per-video prompts:

```powershell
uv run --script skills/html-d3-anime-video-workflow/scripts/build_metro_series_contract_prompts.py --source ../prompt.md --output-dir projects/<project-id>/artifacts/prompts --project-root projects/<project-id>/videos
```

In repository maintenance:

```powershell
uv run --script .agents/skills/html-d3-anime-video-workflow/scripts/build_metro_series_contract_prompts.py --source design/videos.md --output-dir projects/<project-id>/artifacts/prompts --project-root projects/<project-id>/videos
```

The generator writes one prompt contract per video module. Each generated prompt must run the wrapper and then `audit_metro_semantic_density.py`, with exact required outputs for the render-state check, full Metro audit suite, `metro-video-composition-audit.json`, and `metro-semantic-density-audit.json`. Reject a batch plan if the generated prompts omit the encoded-MP4 composition audit, because that is the gate that catches contact sheets that still read like labeled slides.

## Pattern Families

### Flow And Handoff

Use for pipelines, conversions, attribution, allocation shifts, handoffs, or multi-stage transformations.

- `flow-tokens`: moving units along fixed routes. Best for cause/effect, throughput, retries, or transfer.
- `sankey`, `alluvial`, `parallel-sets`: weighted flows that split, lose volume, merge, or shift categories.
- `swimlane-handoff`: owner lanes, SLA pressure, approval, rework, escalation, and completion.
- `plugin-bundle-swimlane`: for Harness Plugin explainers, keep the `swimlane-handoff` scaffold but replace owner-card visuals with a low-text `plugin_bundle_cube`, detachable module blocks for skills/hooks/MCP/agents/tools, GitHub manifest surface, Claude marketplace allowlist gate, OpenCode npm/runtime drop, team install fanout, version/upgrade arrows, and a good-plugin versus noisy-plugin cost split.
- Video adaptation: draw routes before packets move, expose split/loss/merge states, and let the camera follow a dominant route.

### Systems Resilience

Use for overload, reliability, incident response, safety, and fault-tolerance explainers.

- `critical-queue-backpressure`: queue slots, producer pressure, throttling, load shedding, retry, dead-letter, and recovery.
- `critical-cache-stampede`: fan-out waves, stale path, single-flight lock, origin shielding, and TTL jitter.
- `critical-circuit-breaker`: closed, open, half-open, fallback, probe, and retry suppression.
- `critical-dependency-blast-radius`: dependency rings, impact surfaces, failover routes, and blast waves.
- `critical-incident-escalation`: timeline lanes, page, mitigation, ownership, and recovery.
- `critical-slo-burn-rate`: burn budget, thresholds, alerts, and exhaustion.
- Video adaptation: show the failure mode first as a visible state change, then show the intervention as a separate mechanism.

### Risk And Evidence

Use for root-cause, governance, claims, risk review, or decision explainers.

- `critical-fault-tree`: top event, AND/OR gates, cut sets, and causal paths.
- `critical-bowtie-barrier`: threats, preventive barriers, top event, mitigative barriers, consequences, degraded controls, and repair.
- `scenario-tree`: branching futures, probability, upside, downside, decision gate, fallback, and selected outcome.
- `evidence-ladder`: claim, support, counterevidence, source gap, confidence, and recommendation timing.
- Video adaptation: keep the central event or claim fixed while branches, barriers, or evidence tiers activate around it.

### AI And Token Mechanics

Use for LLM, model, inference, retrieval, evaluation, context, and token-flow explainers.

- `attention-arc-decoding`: token arcs, causal attention, and decoding focus.
- `attention-matrix-tiles`: matrix cells, heads, masks, and activation patterns.
- `flashattention-blocks`: block tiling, streaming, and memory-aware compute.
- `kv-cache-growth` and `paged-kv-cache`: cache append, page allocation, eviction, and memory pressure.
- `matmul-tile-accumulation`: tiled compute, partial sums, accumulation, and output assembly.
- `moe-router-capacity`: routing, capacity overflow, expert selection, and dropped tokens.
- `paged-kv-cache`: fixed cache pages, reuse, allocation, eviction, and memory pressure.
- `qkv-projection-flow`: token projections into query, key, value streams.
- `token-boxes-to-context-window`: token groups becoming addressable context slots.
- `document-token-quality` and `document-token-extraction-buckets`: evidence blocks, extraction lanes, quality buckets, and source grounding.
- Video adaptation: make text token-owned from the first frame. Do not draw boxes over separate text.

### Dense Operations And Work Boards

Use for backlogs, staffing, queues, review systems, prioritization, and operational state.

- `asymmetric-task-overlap-saturated`: many labeled work items across overlapping scopes with external lanes.
- `kanban-assignee-board`: columns, cards, assignee dots, WIP, and ownership.
- `data-table-grid`, `inline-bar-table`, `sparkline-table`, `pivot-heat-table`, `column-profile-table`: table cells with embedded quantitative marks.
- `sortable-rank-table`: row reorder, rank movement, and comparison.
- Video adaptation: animate by row groups, columns, or state changes. Avoid individual cell noise in large tables.

### Networks, Dependencies, And Routes

Use for architecture, tool choice, systems maps, integration maps, and dependency stories.

- `force-network`, `cluster-hulls`, `edge-bundling`, `temporal-network`: topology, clusters, bundled routes, and time-varying relationships.
- `circuit-signal-traces`: orthogonal tool/client/server traces, handshakes, fault isolation, and fallback reroutes.
- `critical-dependency-blast-radius`: dependency rings, impact surfaces, critical links, and failover routes.
- `adjacency-matrix`: dense pairwise relationships when link overlap would become unreadable.
- `d3-flowchart-dag`, `critical-path`, `tangled-tree`, `tanglegram`: dependency ordering, bottlenecks, cross-links, and shared leaves.
- `sequence-trace`: spans, latency, handoffs, retries, and fallback.
- Video adaptation: use low-contrast ghost topology at the start, then reinforce active paths as proof advances.

### Space, Density, And Distribution

Use for clusters, capacity, geography, uncertainty, and surfaces.

- `hexbin`, `rectbin-density`, `contours`, `isoline-terrain`: density surfaces and thresholds.
- `beeswarm`, `mirrored-beeswarm`, `violin`, `ridgeline`: distributions and group comparison.
- `calendar-year`, `barcode`, `event-cascade`, `spiral-timeline`: time density and event rhythm.
- `voronoi`, `delaunay-mesh`, `quadtree-search`: spatial indexing, nearest search, and partitioning.
- Video adaptation: reveal cells, bins, or partitions by semantic order, then use camera focus to isolate the key region.

### Modular Composition Armatures

Use these as layout directions before detailed marks:

- Flow spine: one dominant route with side branches.
- Diagonal armature: progress, escalation, or tradeoff across the frame.
- Dense label lanes: high-cardinality evidence or task maps with labels outside the main geometry.
- Balanced bowtie: central event with symmetrical cause and consequence fields.
- Masonry wall: differently sized modules that fit into an ordered block composition.
- Matrix wall: a grid of stateful cells, mini charts, or records.
- Megacanvas map: multiple functional zones explored by camera.

## Selection Rules

1. Name the concept mechanic.
2. Pick one primary pattern family and one secondary support pattern.
3. Define the visual roles for shapes, routes, color, gray levels, and motion.
4. Define a camera path or transition that reveals how zones relate.
5. Remove all visible explanatory text that narration can carry.
6. Validate that the contact sheet shows different states, not just different labels.
7. Validate that ordered render-state samples move through zones with camera/reframe deltas instead of only reporting distinct zones in a summary.

## Anti-Patterns

- A central card plus surrounding labels.
- A dashboard of static boxes with tiny captions.
- Motion that only fades in text.
- Reusing a pattern because it looks complex while changing what its marks mean.
- One large gray surface with no tonal hierarchy.
- Rounded cards, padded chips, decorative badges, or title bands in Metro output.
