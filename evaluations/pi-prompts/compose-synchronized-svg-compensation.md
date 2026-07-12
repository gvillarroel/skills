Use the loaded `compose-synchronized-svg` skill to create a coherent, self-contained compensation-planning composition.

Work only from this prompt and the loaded skill at `skills/compose-synchronized-svg/`. Treat the skill directory as read-only. Keep every generated file in the workspace. Do not inspect parent directories, sibling skills, repository documentation, evaluation files, acceptance examples, or the network. Do not use remote scripts, styles, fonts, images, APIs, CDNs, or package downloads.

Follow the skill's declared normal-use boundary exactly: read only `SKILL.md`, its three named focused references, and `assets/templates/composition-brief.json`. The skill intentionally has no README or package manifest; do not probe for either and do not list the bundle.

Apply the skill's deterministic brief preflight immediately after each complete brief write and before the single publishing compiler call. Do not reread, chunk-read, or inspect the brief between a write and preflight; the preflight is the inspection step. Expected findings are not tool failures: rewrite the complete brief rather than using fragile exact-match edits, repeat preflight until `ok=true`, and call the compiler only once after that gate passes.

Create these exact files:

- `outputs/compensation/composition-brief.json`
- `outputs/compensation/composition-plan.json`
- `outputs/compensation/composition-report.json`
- `outputs/compensation/compensation.svg`
- `outputs/compensation/static-validation.json`
- `outputs/compensation/browser-audit.json`
- `outputs/compensation/overview.png`

The SVG must be one large synchronized composition with at least six nonredundant modules, six distinct asset types, and at least four renderer families. Include complementary views for compensation mix, gross-to-net deductions, monthly cash allocation, effective tax rate, savings-target progress, and annual/monthly reconciliation. Use explicit causal or dependency relationships to connect the forward story and at least one honest feedback relationship from planning shortfall back to allocation. Recurring concepts must keep stable labels, units, direction, and non-color identity cues across modules.

Use these named scenarios:

- `baseline`: annual base salary 90,000 USD, annual bonus 10,000 USD, annual benefits 15,000 USD, effective tax rate 22%, savings rate 15%, monthly living cost 3,000 USD, monthly savings target 1,500 USD.
- `raise`: annual base salary 120,000 USD, annual bonus 15,000 USD, annual benefits 18,000 USD, effective tax rate 24%, savings rate 20%, monthly living cost 3,200 USD, monthly savings target 1,800 USD.

The model must reconcile these checkpoints:

- Baseline: gross cash 100,000 USD/year, total compensation 115,000 USD/year, tax 22,000 USD/year, net cash 78,000 USD/year, net cash 6,500 USD/month, savings 975 USD/month, flexible cash 2,525 USD/month, savings-target progress 65%.
- Raise: gross cash 135,000 USD/year, total compensation 153,000 USD/year, tax 32,400 USD/year, net cash 102,600 USD/year, net cash 8,550 USD/month, savings 1,710 USD/month, flexible cash 3,640 USD/month, savings-target progress 95%.

Ordinary comparative bars must contain only same-unit values that stay nonnegative over their full declared legal domains and must use one shared zero baseline. The module that contains `flexible-cash-monthly` must be a network, table, or flow asset from the first brief; its `assetType` must not contain `bar`. Do not narrow credible source domains merely to make a residual nonnegative.

Any generated flow or Sankey must put one conserved same-unit source first and only mutually exclusive branches after it. Those branches must sum algebraically to the source in baseline, raise, and the 25% savings state. Do not place a total and its own components together as peer branches, and do not use a flow for a multi-stage assembly or a nonconserving comparison.

After reset to baseline, changing only savings rate to 25% must produce monthly savings 1,625 USD, flexible cash 1,875 USD, and target progress about 108.3%, while compensation mix, gross cash, tax, net cash, and monthly net pay remain unchanged. A deductions focus must emphasize relevant modules without changing values.

Include one seekable looping master timeline that coordinates attention through earnings, deductions, allocation, and planning; no module may own an independent clock. The expanded source values, focus, and rendered state at `durationMs` must match time zero exactly. The literal script-free SVG must already show a complete labeled state. Reduced motion must suppress nonessential motion while preserving essential marks, text, scenario changes, focus, and immediate semantic updates. Include keyboard-reachable labeled controls, a root title and description, explicit units, no essential hover-only information, and the visible provenance note `Illustrative compensation model · synthetic USD values`.

Use the skill's normal compact-brief workflow and bundled validators. The final SVG must expose the documented `window.svgSync` API. `static-validation.json` and `browser-audit.json` must both contain `"ok": true`, and the screenshot must show the complete composition. Do not hand-author or patch the monolithic SVG. After both validators pass, do not read `composition-plan.json` or `compensation.svg`; use only the compact brief, compact reports, and `overview.png` as review evidence, then stop. Keep `skills/compose-synchronized-svg/` unchanged.
