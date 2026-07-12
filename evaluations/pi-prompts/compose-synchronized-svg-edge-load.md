Use the loaded `compose-synchronized-svg` skill to create a coherent, self-contained edge-delivery composition that remains correct at zero flow and above a capacity threshold.

Work only from this prompt and the loaded skill at `skills/compose-synchronized-svg/`. Treat the skill directory as read-only. Keep every generated file in the workspace. Do not inspect parent directories, sibling skills, repository documentation, evaluation files, acceptance examples, or the network. Do not use remote scripts, styles, fonts, maps, images, APIs, CDNs, or package downloads.

Follow the skill's normal-use read boundary exactly: read only `SKILL.md`, its three named focused references, and `assets/templates/composition-brief.json`. Do not list or search the bundle, probe for files, read `composition-plan.json`, inspect script source, or look for a README or package manifest.

Apply the skill's deterministic brief preflight before the single publishing compiler call. Expected preflight findings are not tool failures: rewrite the complete brief rather than using fragile exact-match edits, repeat preflight until `ok=true`, and call the compiler only once after that gate passes.

Create these exact files:

- `outputs/edge-load/composition-brief.json`
- `outputs/edge-load/composition-plan.json`
- `outputs/edge-load/composition-report.json`
- `outputs/edge-load/edge-load.svg`
- `outputs/edge-load/static-validation.json`
- `outputs/edge-load/browser-audit.json`
- `outputs/edge-load/overview.png`

Build one large synchronized SVG with at least seven nonredundant modules, seven distinct asset types, and at least five renderer families. Include an edge/origin topology, request split between cache and origin, capacity pressure, cache-hit behavior, overload evidence, blended latency, and an operational consequence such as SLO health or traffic cost. Connect the forward operating story and close it with an honest feedback relationship from the consequence back to traffic control. Request volume, cache hits, origin spill, latency, and overload must keep stable labels, units, direction, and non-color cues.

Use these named scenarios:

- `idle`: request rate 0 req/s, edge capacity 1,600 req/s, cache hit rate 75%, edge latency 35 ms, origin latency 180 ms.
- `baseline`: request rate 1,200 req/s, edge capacity 1,600 req/s, cache hit rate 75%, edge latency 35 ms, origin latency 180 ms.
- `surge`: request rate 2,200 req/s, edge capacity 1,800 req/s, cache hit rate 55%, edge latency 50 ms, origin latency 220 ms.
- `cache-recovery`: the same request rate, capacity, and latencies as `surge`, but cache hit rate 80%.

Derive edge-served rate as request rate multiplied by cache hit rate, origin rate as the remainder, request-to-capacity load ratio as request rate divided by edge capacity, overload as the greater of zero or request rate minus capacity, and blended latency as the cache-hit-weighted edge latency plus the miss-weighted origin latency. Reconcile these checkpoints:

- Idle: edge served 0 req/s, origin 0 req/s, load ratio 0%, overload 0 req/s.
- Baseline: edge served 900 req/s, origin 300 req/s, load ratio 75%, overload 0 req/s, blended latency 71.25 ms.
- Surge: edge served 1,210 req/s, origin 990 req/s, load ratio about 122.2%, overload 400 req/s, blended latency 126.5 ms.
- Cache recovery: edge served 1,760 req/s, origin 440 req/s, load ratio about 122.2%, overload 400 req/s, blended latency 84 ms.

The load ratio can exceed 100%. Do not call it utilization or encode it on a bounded radial gauge; use a threshold-capable form with an explicit 100% capacity marker and preserve the 122.2% reading. In `idle`, every zero-valued flow must render with zero thickness and without a false deficit or reverse-flow cue. Applying `cache-recovery` from `surge` must change the cache split, origin path, blended latency, and dependent consequence while request rate, capacity, load ratio, and overload remain unchanged.

Any generated flow or Sankey must put one conserved same-unit source first and only mutually exclusive branches after it. Those branches must sum algebraically to the source in baseline, surge, cache-recovery, idle, and any audited perturbation.

Include one seekable looping master timeline; no independent module clocks. The expanded source values, focus, and rendered state at `durationMs` must match time zero exactly. The literal script-free SVG must show a complete labeled baseline. Reduced motion must suppress nonessential motion while preserving essential marks, labels, scenarios, focus, and immediate semantic updates. Include keyboard-reachable labeled controls, a root title and description, explicit units, no essential hover-only information, and a visible note that the traffic values are a synthetic operating model.

Use the skill's normal compact-brief workflow and bundled validators. The final SVG must expose the documented `window.svgSync` API. `static-validation.json` and `browser-audit.json` must both contain `"ok": true`, and the screenshot must show the complete composition. Do not hand-author or patch the monolithic SVG. After both validators pass, do not read `composition-plan.json` or `edge-load.svg`; use only the compact brief, compact reports, and `overview.png` as review evidence, then stop. Keep `skills/compose-synchronized-svg/` unchanged.
