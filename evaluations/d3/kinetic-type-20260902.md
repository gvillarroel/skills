# D3 Kinetic Type Evaluation — 2026-09-02

## Scope

- Skill: `d3`
- Pattern: `d3-kinetic-glyph-mosaic`
- Model: `openai-codex/gpt-5.3-codex-spark`
- Runtime payload: 281 files, SHA-256
  `ef8ac010415e58d3978081a932e2f7bdb3b37a1b2992a29f9d82834d840a83ca`
- Cases: one command-contract smoke and three fresh naturalistic repetitions
- Release threshold: one passing smoke and at least two passing naturalistic
  repetitions out of three

## Result

PASS. The current payload passed the command-contract smoke and all three fresh
naturalistic repetitions. Every passing run used JSON strict mode, observed the
required Spark model, created the exact non-empty output, produced valid event
JSON with zero tool errors, kept the copied payload unchanged, and stayed within
the allowed read surface.

The three naturalistic artifacts were byte-identical, each with SHA-256
`19442b0fcb597c577e71e60c80d4ca879a6d0febdb080ae4f19f6666d614aa40`.
The contract artifact SHA-256 was
`3b80df3e7a37b479a2fb681b457780e492cdc16ae7d933bd30f7fd5e27ff655c`.

## Passing Runs

| Case | Run ID | Required output | Strict result | Independent browser result |
| --- | --- | --- | --- | --- |
| `contract-smoke` | `20260901-d3-kinetic-type-contract-spark-3` | `outputs/kinetic-type.html` | PASS | PASS |
| `naturalistic-forward` | `20260901-d3-kinetic-type-naturalistic-spark-2` | `artifacts/kinetic-launch.html` | PASS | PASS |
| `naturalistic-forward` | `20260901-d3-kinetic-type-naturalistic-spark-3` | `artifacts/kinetic-launch.html` | PASS | PASS |
| `naturalistic-forward` | `20260901-d3-kinetic-type-naturalistic-spark-4` | `artifacts/kinetic-launch.html` | PASS | PASS |

The isolated commands used the following form:

```powershell
uv run --script scripts/run-pi-skill-eval.py d3 --prompt-file evaluations/pi-prompts/d3-kinetic-type-contract-smoke.md --mode json --strict --run-id 20260901-d3-kinetic-type-contract-spark-3 --expect-output outputs/kinetic-type.html
uv run --script scripts/run-pi-skill-eval.py d3 --prompt-file evaluations/pi-prompts/d3-kinetic-type-naturalistic.md --mode json --strict --run-id <fresh-run-id> --expect-output artifacts/kinetic-launch.html
```

## Independent Validation

The evaluator-owned `evaluations/d3/verify_kinetic_type.py` check passed for all
four release runs. It opened the generated HTML in Chromium and verified:

- ready-state, pattern, colorset, motion, seed, title, card order, and material
  metadata;
- real readable SVG text at rest and non-empty deterministic component geometry;
- tile-only, line-only, dot-only, and mixed geometry for the requested variants;
- click pinning with synchronized `aria-pressed` state;
- keyboard focus reveal;
- static reveal with no active animation under reduced motion; and
- zero console, page, or failed-request errors.

Direct screenshot inspection confirmed readable idle typography and coherent
active tile and line deconstruction. The bundled self-contained, palette,
visual-contract, and browser-render checks also passed inside each naturalistic
run.

Read-surface summaries are retained as:

- `d3-kinetic-type-contract-20260901-read-surface-final.json`
- `d3-kinetic-type-naturalistic-20260901-read-surface-2.json`
- `d3-kinetic-type-naturalistic-20260901-read-surface-3.json`
- `d3-kinetic-type-naturalistic-20260901-read-surface-4.json`

## Recorded Failures And Repairs

- `20260901-d3-kinetic-type-contract-spark-1` failed because the evaluation
  prompt labeled an exact shell command as PowerShell, so the harness did not
  recognize it as an exact-command contract. Classification: `validator`. The
  prompt fence was corrected to `bash`.
- `20260901-d3-kinetic-type-naturalistic-spark-1` created the correct artifact
  but incurred two tool errors after following a validation section that named
  a maintainer-only acceptance test and did not distinguish whole-HTML checks
  from selected-SVG inspection. Classification: `skill`. The route now tells a
  runtime agent to use only shipped checks, run the page-level contract against
  the HTML, and never probe excluded `assets/examples/` fixtures.
- The first evaluator-side interaction attempt sampled opacity during its CSS
  transition and used programmatic focus. Classification: `validator`. The
  evaluator now waits for the transition and drives a real `Tab` keypress.
- The optional `@playwright/cli` launcher crashed in its Windows daemon before
  opening the page. Classification: `infrastructure`. The bundled Python
  Playwright/Chromium verifier completed the same browser checks successfully;
  this incident is not counted as a skill failure.

## Decision

The kinetic-type route is release-valid for the current D3 payload. The recorded
evidence satisfies the repository repetition policy for a naturalistic case and
adds direct browser inspection beyond the tested agent's own validation.
