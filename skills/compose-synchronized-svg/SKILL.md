---
name: compose-synchronized-svg
description: "Designs, builds, synchronizes, and validates giant standalone SVG compositions made from many related diagrams, charts, maps, schematics, illustrations, and explanatory assets. Use when Codex must turn one idea into a coherent 6–16-module megacanvas or a 12–48-module navigable world such as a Path of Exile-style skill tree, giant genealogy, causal atlas, or linked-diagram map; keep recurring concepts visually consistent; propagate canonical values through every relevant view; coordinate focus, time, world-to-district-to-module semantic zoom, or a deterministic camera route for video; and deliver one self-contained interactive SVG with meaningful static and reduced-motion fallbacks."
---

# Compose Synchronized SVG

Read [palette-policy.md](references/palette-policy.md) before authoring or composing visuals. Apply one exact colorset to authored content and report preserved source media separately.

Build one explanatory SVG whose recurring values come from one canonical state. Give each module a distinct viewer question. Semantic propagation is required; animation is optional.

## Read for the current task

- **Create or revise a brief:** read [asset-selection-and-composition.md](references/asset-selection-and-composition.md) and [semantic-state-contract.md](references/semantic-state-contract.md). Then select exactly one template: [composition-brief.json](assets/templates/composition-brief.json) for a compact 6–16-module canvas, or [navigable-world-brief.json](assets/templates/navigable-world-brief.json) for 12–48 modules in 4–12 districts.
- **Create a navigable world:** also read [spatial-world-and-camera.md](references/spatial-world-and-camera.md) before authoring districts, links, semantic zoom, or a camera route.
- **Set colors or improve visual quality:** read [color-and-visual-quality.md](references/color-and-visual-quality.md). Use brief-owned `theme` roles, pair text with its actual local background, and preserve canonical concept paints through regeneration.
- **Validate or review an existing SVG:** read [critique-and-validation.md](references/critique-and-validation.md) and use the validation commands below. Do not load authoring templates unless a finding requires a brief change.
- **Implement an explicitly requested custom fragment or maintain the compiler:** read [compiled-plan-and-bindings.md](references/compiled-plan-and-bindings.md). For direct API integration or custom interaction tests, read [runtime-api.md](references/runtime-api.md). These extension contracts are unnecessary for normal generation.

Keep generated briefs, plans, SVGs, reports, and screenshots outside the read-only skill bundle. During normal generation, use the named resources and executable scripts without inspecting helper source, enumerating the bundle, probing for README/package manifests, or loading acceptance examples or sibling skills. The bundle uses `uv` Python and needs no Node project. Explicit skill maintenance may inspect the affected source and tests.

## Author one brief

State the thesis, audience, delivery context, and evidence status. Choose distinct claims and honest encodings before geometry. Label assumptions and synthetic values in a visible `provenance` note. Use exactly `en-US` for deterministic literal/browser formatting.

Write one complete brief from the selected template. Let the compiler generate regions, anchors, selectors, identities, transforms, reading order, and exact omitted phase/route times. Do not copy, read, or hand-edit the advanced `composition-plan.json` template during normal use.

Before writing, check these authoring invariants:

- Give source concepts stable IDs, units, defaults, and credible full-domain envelopes. Store `fraction` in 0..1 and percentage points as `percent` in 0..100. Use documented pure computation nodes; omit `dependsOn`, which the compiler derives. Model every possible zero divisor explicitly with `max`/`clamp` or choose a finite alternative.
- Bind every declared source visibly. Keep module value lists purposeful, with a specific `selectionRationale` and `rejectedAlternative`. Use the supported renderer-family tokens documented in the selection reference; anonymous metric cards are not semantic renderers.
- Give modules short subject titles with optional `title`. For palette or brand requests, set top-level `theme` using the color reference. Keep labels and non-color cues; reject incompatible colors explicitly instead of silently replacing them.
- Keep ordinary bars same-unit, nonnegative, zero-based, and on one shared scale. Stack only disjoint nonnegative parts with their `stackTotal`. Flows put one conserved same-unit source first, followed by mutually exclusive branches. Waterfalls reconcile opening minus sign-stable deduction magnitudes to ending without clamping.
- Define the equality behind every total, check, residual, and reconciliation. Never add a whole to its included parts or describe a subtotal and its constituent as peers. Use tables or arithmetic bridges for static equalities, and lines only for meaningful ordered axes.
- Bound radial gauges to 0..1 fractions or 0..100 percentage points across the entire legal domain. If demand/capacity can exceed 100%, name it a load ratio and use a bullet/progress view with a 100% target and exact readout.
- An implicit network needs a real selected source/derived edge and every intermediate dependency behind its claim. Include all direct parents of visible derived nodes. An explicit `module.diagram` must be connected, use supported kinds, and bind each numeric module value exactly once.
- Declare atomic source-only scenarios. A module promised unchanged must bind only values outside the transition's changed dependency closure.
- Declare focus membership only in top-level `focusGroups`; every phase `focusId` must resolve there. Use `timeline: null` unless time explains the subject. A looping timeline must return to the initial values, focus, and marks at `durationMs`.
- Make any requested causal spine connected. Relationship labels may claim only the shared value or declared dependency carried between their endpoints. Support feedback through a derived recommendation or an explicit later policy/scenario change; a connector alone proves no causality.
- In world mode, partition modules exactly once among districts, ensure directed non-feedback reachability from the root, and make looping camera routes cover required districts and return to their initial anchor. Camera actions must not change semantic state.

## Compile and compose

Replace `<skill-root>` with this bundle's path and choose exact workspace output paths. In Git Bash on Windows, first create `.tmp` in the workspace with `mkdir -p .tmp` and prefix bundled `uv run` commands with `TMPDIR="$(pwd)/.tmp"`. Do not rely on `/tmp` outside the workspace. Commands below are single lines so they work without shell-specific continuations.

After each complete brief write, make preflight the first external command; do not reread the brief or run a speculative linter/help probe first:

```text
uv run --script <skill-root>/scripts/preflight_svg_brief.py --brief composition-brief.json --json
```

Expected authoring findings exit zero. Inspect `ok`; if false, rewrite the complete brief and repeat preflight. Only `ok: true` permits publishing a plan:

```text
uv run --script <skill-root>/scripts/compile_synchronized_svg_plan.py --brief composition-brief.json --output composition-plan.json --force --json
uv run --script <skill-root>/scripts/compose_synchronized_svg.py --spec composition-plan.json --output <exact-output.svg> --report <composition-report.json> --force --json
```

Preserve any reported divisor-domain normalization. Use this compiler/composer pair for normal generation. It creates the canonical runtime, final module geometry, literal fallback, and optional navigation atomically. Specialized asset names still map to eight renderer families; do not count every asset name as a distinct renderer. Improve claims, values, asset choices, domains, focus, or districts in the brief and regenerate; do not patch the monolithic SVG or create a second wrapper.

Use scaffold/replacer tools only for explicitly requested bespoke module geometry. In that mode, consult their help and the compiled-binding contract, preserve the body-local shell, and never rewrite the full SVG.

## Validate and review

Read [critique-and-validation.md](references/critique-and-validation.md) before the first review. Run static validation with the counts required by the accepted brief:

```text
uv run --script <skill-root>/scripts/validate_synchronized_svg.py <exact-output.svg> --output <static-validation.json> --json --min-modules <module-count> --min-asset-types <asset-type-count> --min-renderer-families <family-count> --min-shared-sources 1 --min-modules-per-shared-source 2 --min-encodings-per-shared-source 2
```

Never use `--allow-placeholders` for a deliverable. Add `--require-time-sync` only for a declared timeline. In world mode, also add `--require-navigation --min-navigation-regions 4 --min-anchor-depth 2 --min-world-detail-area-ratio 16 --min-distant-shared-sources 1`, or stricter accepted minima.

Run one supervised browser audit:

```text
uv run --script <skill-root>/scripts/audit_synchronized_svg.py <exact-output.svg> --report <browser-audit.json> --screenshot <overview.png> --compact-report
```

Use the compact report and rendered screenshot as the normal evidence surface. Inspect local text contrast, including controls and focus states; a passing palette check alone is insufficient. The auditor already handles containment, a finite worker timeout, and one internal timeout retry; do not add an external retry loop. Static validation and browser propagation are blocking gates. If Chromium is unavailable, retain static results and report browser validation as incomplete.

Review hierarchy, claim/asset fit, connectors, readability, literal fallback, and reduced-motion behavior against the reference rubric. A fitted overview proves structure, not readable module detail. Release-grade work also needs readable module crops and materially different states; worlds need district views plus route arrivals/midpoints. Require two consecutive clean reviews with fresh evidence. Use direct browser interactions only when requested acceptance goes beyond the bundled audit.

For visual improvement work, freeze one brief, generate and critique its actual screenshots, fix the responsible input or reusable generator, and compare a regenerated version using the same data. Then check a fresh topic. Follow the color reference's generation–critique loop and retain failures; structural validation alone cannot establish visual quality.

For actionable semantic, quantitative, geometry, accessibility, relationship, or navigation findings, revise the brief, preflight, and rerun compiler → composer → validator → audit. For `runtime-api`, `real-input-controls`, `navigation-input-controls`, worker, timeout, or playback-timing failures, or an identical repeated check, preserve the exact check ID/message and report a generator/auditor defect. Do not weaken semantics, tune timing to evade a mechanical check, inspect implementation internals during normal generation, or hide the failure.

Deliver the exact SVG and concise evidence of passing gates. Preserve its brief, compiled plan, reports, and screenshots alongside it unless the user requests only the SVG. Claim completion only when synchronization and unrelated-value isolation, truthful encodings, accessible marks/controls, meaningful script-free and reduced-motion states, required navigation, and visual reviews all pass.
