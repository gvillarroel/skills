Use the loaded `compose-synchronized-svg` skill to create a coherent, self-contained urban-cloudburst composition that proves the workflow transfers beyond its bundled planning template.

Work only from this prompt and the loaded skill at `skills/compose-synchronized-svg/`. Treat the skill directory as read-only. Keep every generated file in the workspace. Do not inspect parent directories, sibling skills, repository documentation, evaluation files, acceptance examples, or the network. Do not use remote scripts, styles, fonts, maps, images, APIs, CDNs, or package downloads.

Follow the skill's normal-use read boundary exactly: read only `SKILL.md`, its three named focused references, and `assets/templates/composition-brief.json`. Do not list or search the bundle, probe for files, read `composition-plan.json`, inspect script source, or look for a README or package manifest.

Apply the skill's deterministic brief preflight immediately after each complete brief write and before the single publishing compiler call. Do not reread, chunk-read, or inspect the brief between a write and preflight; the preflight is the inspection step. Expected findings are not tool failures: rewrite the complete brief rather than using fragile exact-match edits, repeat preflight until `ok=true`, and call the compiler only once after that gate passes.

Create these exact files:

- `outputs/cloudburst/composition-brief.json`
- `outputs/cloudburst/composition-plan.json`
- `outputs/cloudburst/composition-report.json`
- `outputs/cloudburst/cloudburst.svg`
- `outputs/cloudburst/static-validation.json`
- `outputs/cloudburst/browser-audit.json`
- `outputs/cloudburst/overview.png`

Build one large synchronized SVG with at least eight nonredundant modules, eight distinct asset types, and at least five renderer families. Show a rainfall pulse over time, an abstract catchment surface, runoff entering a drainage network, drainage capacity versus load, retention-buffer use, downstream overflow, neighborhood risk, and an adaptive operating response. Connect the views with a legible forward causal chain plus an honest feedback relationship from downstream risk to the operating response. Water, capacity, retention, and risk must keep stable labels, units, direction, and non-color cues.

Use these named scenarios:

- `baseline`: rainfall intensity 30 mm/h, runoff coefficient 0.60, drainage capacity 40 mm/h, retention buffer 8 mm/h.
- `cloudburst`: rainfall intensity 90 mm/h, runoff coefficient 0.70, drainage capacity 40 mm/h, retention buffer 8 mm/h.
- `capacity-response`: the cloudburst rainfall and runoff coefficient, drainage capacity 55 mm/h, retention buffer 8 mm/h.

Derive runoff load as rainfall intensity multiplied by runoff coefficient, capacity gap as drainage capacity minus runoff load, and retention-adjusted overflow as the greater of zero or runoff load minus drainage capacity minus retention buffer. Reconcile these checkpoints:

- Baseline: runoff load 18 mm/h, capacity gap +22 mm/h, overflow 0 mm/h.
- Cloudburst: runoff load 63 mm/h, capacity gap -23 mm/h, overflow 15 mm/h.
- Capacity response: runoff load 63 mm/h, capacity gap -8 mm/h, overflow 0 mm/h.

Ordinary comparative bars must contain only same-unit values that stay nonnegative over their full declared legal domains and must use one shared zero baseline. Capacity gap is signed across these scenarios, so encode it with a table, line, flow, or another honest signed form rather than an ordinary bar.

Any generated flow or Sankey must put one conserved same-unit source first and only mutually exclusive branches after it. Those branches must sum algebraically to the source in every named scenario; use a table, network, or line for independent, staged, or nonconserving values.

Applying `capacity-response` from `cloudburst` must update capacity, retention/overflow, risk, and response views while the rainfall pulse and runoff-coefficient representation remain unchanged. A risk focus must emphasize capacity, retention, overflow, neighborhood risk, and response without changing values.

Make the risk-to-response feedback evidential, not decorative. The response view must either show a recommendation derived from overflow/risk or a declared policy control that changes in the later `capacity-response` scenario or timeline phase after the risk signal. Do not claim that risk drives a response value computed only from an unrelated input.

Include one seekable looping master timeline that coordinates storm, runoff, capacity, risk, and response; no independent module timers. The expanded source values, focus, and rendered state at `durationMs` must match time zero exactly. The literal script-free SVG must show a complete labeled baseline. Reduced motion must suppress nonessential motion while preserving essential geometry, labels, scenarios, focus, and immediate semantic updates. Include keyboard-reachable labeled controls, a root title and description, explicit units, no essential hover-only information, and a visible note that the supplied storm values are a synthetic scenario model.

Use the skill's normal compact-brief workflow and bundled validators. The final SVG must expose the documented `window.svgSync` API. `static-validation.json` and `browser-audit.json` must both contain `"ok": true`, and the screenshot must show the complete composition. Do not hand-author or patch the monolithic SVG. After both validators pass, do not read `composition-plan.json` or `cloudburst.svg`; use only the compact brief, compact reports, and `overview.png` as review evidence, then stop. Keep `skills/compose-synchronized-svg/` unchanged.
