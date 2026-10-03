# Luna SVG Color and Generation Review — 2026-09-04

## Scope and model

The user requested a Luna generation–critique loop for SVG quality, colors, recoloring, and generation behavior. This cycle targets `compose-synchronized-svg`, the owner of the shared composition renderer, palette, compiler, and browser auditor. It does not claim improvements to unrelated D3, Mermaid, or PlantUML bundles.

All isolated forward runs explicitly select `openai-codex/gpt-5.6-luna` with high thinking. The user-requested model exception is recorded in `SKILLS.md`; observed provider/model values, prompt hashes, runtime payload hashes, exact outputs, read surfaces, and immutable-bundle checks are retained. Luna also provided separate screenshot critiques and bounded code proposals, which the primary agent reviewed and tested rather than accepting from self-reports.

## Evidence and decisions

1. An initial independent Luna review of the Workshop Throughput Atlas identified saturated competing accents, small supporting text, ambiguous network convergence, and long cross-panel routes. See [workshop-independent-critique.md](workshop-independent-critique.md).
2. A fresh isolated water baseline exposed both the visual limitations and concrete generation defects: a disjoint subtraction branch was incorrectly suppressed as a stack subtotal; the browser auditor crashed on `timeline: null`; its reduced-motion check also incorrectly required a playback button when no timeline existed. The baseline is retained as a failed run, not discarded or counted as a pass.
3. The first candidate adds brief-owned theme roles and concept colors, an editorial preset, subject titles, quieter card surfaces, larger explanation/detail text, and unique network ports. Two fresh water runs and one microgrid run passed strict isolation and artifact gates.
4. A same-brief screenshot comparison preferred the restrained candidate palette but identified weaker connector visibility. The second iteration darkens essential routes, adds separate rectilinear lanes and arrowhead clearance, reorders nodes with deterministic barycenter sweeps, and routes skip-level edges through reserved upper gutters. See [water-comparison-luna.md](water-comparison-luna.md) and [water-v2-luna.md](water-v2-luna.md).
5. The initial Luna routing proposal used a common top gutter for all edges and did not match several claims in its completion report. It was not accepted as reported. Primary review replaced it with short adjacent-column routes, distinct long-edge lanes, horizontal destination approaches, bounded ports, and independent geometry assertions.

The comparison reviewer could see descriptive filenames, so this was an independent screenshot review, not a blinded experiment. Its early claim that the baseline changed capacity colors across panels was unsupported: the original generator already maintained canonical identity. The reviewer corrected that interpretation. The demonstrated changes are palette ownership, contrast/readability, and generation mechanics; semantic-color consistency remains enforced by the identity contract and validators.

A late preview appeared to clip text in microgrid repetition 3. Direct PNG comparison showed all four suspect text regions were pixel-identical to the independently captured image. No clipping defect was confirmed in the files; the experimental screenshot-capture change was reverted, restoring the exact validated payload. See [screenshot-investigation.json](screenshot-investigation.json). This false positive is retained to distinguish an apparent preview issue from a verified renderer defect.

## Implemented changes

- `theme_contract.py` resolves `editorial`/`classic`, validates opaque hex values and declared roles, rejects unsupported keys and conflicting alias overrides, enforces distinct root colors, and checks numerical contrast. A user color is normalized for case and either preserved or rejected, never silently substituted.
- The brief owns `theme`; the compiled plan stores its resolved form and the `composition-theme` SVG style emits shared role/concept variables. Static validation rejects changed, missing, or duplicated expected theme declarations. Renderer surfaces, labels, tracks, controls, warnings, and feedback colors derive from role tokens. Navigable district accents retain their existing separate spatial contract.
- New briefs default to a restrained editorial theme; legacy full plans keep the classic concept sequence. Optional module titles expose the subject instead of a renderer name. Explanation/detail text grows from 11 to 12 px, neutral panels have visible boundaries, and focus-region decoration no longer uses a rainbow of outlined row bands.
- Implicit network nodes remain equal-area and preserve the exact dependency edge inventory. Tests check endpoint uniqueness, direction, module bounds, deterministic output, and no crossing of non-endpoint card interiors in the focused skip-level fixture. Edge-to-edge crossings are not claimed eliminated.
- Stack rollup inference now distinguishes additive subtotals from disjoint residual branches. Composer reconciliation remains unchanged. No-timeline auditing now handles a null timeline and an absent playback control correctly.
- The skill contains a compact [color and critique workflow](../../../skills/compose-synchronized-svg/references/color-and-visual-quality.md), including same-input comparison, actual screenshot evidence, fresh-topic checks, and limits of model judgments.

## Validation

Final run inventory and compact results are recorded in `run-results.json`. Raw runs remain in ignored `evaluations/runs/`; each completed run has the harness manifest, event policy/results, exact artifact hashes, field checks, and unchanged-payload proof. The final runtime payload is frozen before its release repetitions.

| Cohort | Strict results | Interpretation |
| --- | --- | --- |
| Original water baseline | 0/1 | Eight tool errors following compiler/auditor defects and unsuccessful manual capture attempts; every requested artifact was retained, but the browser field and event gates failed. |
| Candidate v1 water / microgrid | 2/2 and 1/1 | Development evidence before connector refinement; not pooled into final-payload repetition results. |
| Final v2 water | 3/3 | Eight exact artifacts per run; zero tool errors, intact bundle, correct field assertions. |
| Final v2 microgrid | 3/3 | Same gates, plus independent exact brand-color verification. |
| Final v2 command smoke | 1/1 | Template → preflight → compiler → composer → static validator with exact paths. |
| Final v2 unreadable-palette boundary | 1/1 | Preserved requested colors, rejected `muted=#eeeeee` on white, and published no SVG. |

All eight final-payload runs used SHA-256 `fb3c585664f88bf97a3f173e6b8c0ea5de81a588542ed460dba9b006d3fd71f6`. The six final generated compositions also passed evaluator-owned checks for all 24 requested scenario/boundary states, with no numeric or stale-binding errors. The comparison page passed desktop (1440 px), mobile (390 px), image/link, slider, and zero-page-error checks. These are technical passes; the open visual findings below still prevent a clean visual release.

Local commands:

```text
uv run --script skills/compose-synchronized-svg/scripts/test_theme_contract.py
uv run --script skills/compose-synchronized-svg/scripts/test_network_ports.py
uv run --script skills/compose-synchronized-svg/scripts/test_stack_reconciliation.py
uv run --script skills/compose-synchronized-svg/scripts/test_svg_themes.py
uv run --script skills/compose-synchronized-svg/scripts/test_synchronized_svg_tools.py
uv run --script scripts/validate-pattern-ids.py
uv run --script scripts/validate-skills.py
uv run --script scripts/test-skill-independence.py
uv run --script scripts/check-repo-payload.py
uv run --script scripts/sync-local-skills.py
```

The focused suites contain 8 theme tests, 2 network tests, 2 stack tests, and 6 end-to-end theme/stack/browser tests. The existing suite passes 80/80. Its initial failure was a hard-coded legacy stroke-color assertion; it was updated to assert role ownership, while the existing routing, physical-clearance, and browser contrast checks remained in place and passed. The successful full suite was rerun after the final routing change.

The evaluator-owned [independent browser contract](../../contracts/inspect-svg-color-cases.py) computes task outcomes directly from the user-specified equations, checks every rendered binding against runtime state, captures four states and six module crops per inspected artifact, and checks the exact requested microgrid brand roles. It does not import the skill's arithmetic evaluator. For water, peak demand 180, capacity 150, and leakage 20% imply delivery 120 and unmet demand 30; repair at 8% implies delivery 138 with unmet demand still 30. Zero demand is included. Microgrid checks include curtailed generation outside the demand partition and an explicit zero-demand case.

Strict forward commands use `scripts/run-pi-skill-eval.py`, the versioned prompts `compose-svg-color-water.md`, `compose-svg-color-microgrid.md`, `compose-svg-theme-smoke.md`, and `compose-svg-theme-boundary.md`, `--mode json --strict`, exact `--expect-output` paths, JSON field assertions, and `--model openai-codex/gpt-5.6-luna --thinking high`. The boundary case expects `preflight.ok=false` and preserves the unreadable supplied palette without publishing an SVG. Read-surface summaries require Luna, valid event JSON, tool calls, and zero tool errors for passing candidates.

## Visual limits and status

The same-brief v2 review confirms improved line contrast and network structure while retaining the calm palette. It still identifies dense endpoint groups, long cross-panel dependencies, small metadata, and uneven use of panel space. These are visible limitations, not hidden by passing static or browser checks. Larger or denser graphs still require case-specific visual judgment; the numerical contrast checks do not certify every blended state, custom fragment, or color-vision condition.

Keep the skill `validating` while the dense-network and long-relationship visual findings remain open. Passing isolated generation cohorts demonstrate usability and a measurable reduction in failures for these cases; they do not establish a clean visual release for the full compact/world trigger surface. The microgrid case is a pre-authored generalization exercise, not a sealed holdout, and the evidence must not be described as a population-wide quality estimate.

Local deliverable: `projects/svg-quality-luna/artifacts/comparison.html`, with the original, first candidate, refined same-brief SVG, and first fresh final-payload water/microgrid examples. Generated images and SVGs remain ignored. No published examples or Pages catalog were changed.
