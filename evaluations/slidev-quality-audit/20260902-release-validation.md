# Slidev Quality Audit Release Validation — 2026-09-02

## Outcome

The current wrapped-inline hit-testing implementation passes deterministic regression, browser-geometry, screenshot, and full acceptance-deck integration checks. The required isolated Spark gate could not be launched because the shared `gpt-5.3-codex-spark` usage quota was already exhausted. Under the repository release policy, this is an infrastructure-blocked Pi gate rather than a skill failure or a complete isolated release pass.

- Repository commit: `29ae22617120b1d04fae1bfbd10f9b22cf4d1c3f`
- Skill script SHA-256: `771ea44a9cf7834509a7a32e0f178e7d5668657854d3a523a73a27dff7dcfa38`
- `SKILL.md` SHA-256: `a2527b56933e507d9a9ca9fa87a8c6178d03e61da82dfc62b258da9a8e500283`
- Audit-rules reference SHA-256: `07233ded6b164795f6b6cdd1648a98169a642ad2b061f5b8c4619bdc7705d3bf`

## Full Acceptance-Deck Integrations

Both integration audits used the current bundled script with strict mode and the locally installed Chromium browser:

```powershell
npx tsx skills/slidev-quality-audit/scripts/audit-slidev-quality.ts --deck skills/slidev-echarts/assets/examples/slidev-echarts --out evaluations/runs/slidev-quality-audit-current-echarts --screenshots none --strict --channel none
npx tsx skills/slidev-quality-audit/scripts/audit-slidev-quality.ts --deck skills/slidev-animejs/assets/examples/slidev-animejs --out evaluations/runs/slidev-quality-audit-current-animejs --screenshots none --strict --channel none
```

Results:

- Slidev ECharts: 36 slides, 129 visual states, 0 findings, exit 0.
- Slidev Anime.js: 30 slides, 93 visual states, 0 findings, exit 0.
- ECharts report SHA-256: `5cd33e9ea32fdba88eb0d3a0dc50edea30ba91bdaa31071134e51188234dd216`.
- Anime.js report SHA-256: `e9fd51a6da5acbb63c0ec0afe2559321805f510efc7783d11cbfa4d9784048af`.

Slidev emitted its expected denied-Wake-Lock message in the headless browser. The auditor's documented runtime filter ignored that known non-actionable message. Neither report contains browser-console or page-error findings.

## Focused Wrapped-Inline Regression

The evaluator fixture contains two slides:

1. A fragmented inline span with a neighboring `audit-token` placed inside the empty center of the span's union rectangle. The text itself remains fully visible.
2. A genuine sibling overlay covering a text span, used as a positive control.

The fixture pins Slidev `52.16.0`, Playwright `1.60.0`, tsx `4.23.12`, and Vite `8.0.16`. Its Vite configuration explicitly prebundles `@fix-webm-duration/fix`, matching the known-good dependency behavior of the repository acceptance decks. A preliminary evaluator-only dependency trial without that pin resolved Vite `8.2.2` and produced six `fixWebmDuration` module-interop page errors. That failed preliminary trial was caused by the newly resolved fixture dependency graph; it was excluded from skill scoring and fixed in the evaluator fixture rather than suppressed in the skill.

Final command:

```powershell
npx tsx skills/slidev-quality-audit/scripts/audit-slidev-quality.ts --deck evaluations/slidev-quality-audit/fixture --out evaluations/runs/slidev-quality-audit-wrapped-inline-local --screenshots all --strict --channel none --timeout 120000
uv run --script evaluations/slidev-quality-audit/verify_report.py evaluations/runs/slidev-quality-audit-wrapped-inline-local/quality-report.json --screenshots evaluations/runs/slidev-quality-audit-wrapped-inline-local/screenshots
```

Final result:

- 2 slides and 2 visual states audited.
- 0 error findings.
- Slide 1: 0 findings; specifically, no `covered-content` false positive for `wrapped-inline`.
- Slide 2: exactly 1 warning, the expected `covered-content` true positive targeting `span[covered-target]`.
- Both screenshots are valid, nontrivial 1280×720 PNGs.
- JSON report SHA-256: `db52e7d0745a7cbd9804f28d1343b870dcb466f8c0410837c5958978a00faedb`.
- Slide 1 screenshot SHA-256: `cf561b5f5016612f56452ec565d33110135e2f22139edff03eb225e9c58573a0`.
- Slide 2 screenshot SHA-256: `409db103b8a4e6d22dbd81277fa394d136337d661d4f278cb87ce48d428abb60`.

Visual inspection confirmed that slide 1's four inline fragments and the neighboring token are all readable and non-overlapping. Slide 2 visibly obscures the intended control text with the dark overlay, matching the reported warning.

## Independent Browser-Geometry Check

The evaluator-side geometry verifier established that the fixture exercises the exact historical false-positive condition:

```powershell
node evaluations/slidev-quality-audit/verify_wrapped_inline_geometry.mjs --fixture evaluations/slidev-quality-audit/fixture --url "http://localhost:3998/1?embedded=true&clicks=0" --out evaluations/runs/slidev-quality-audit-wrapped-inline-local/geometry-report.json
```

- The legacy union-rectangle center was `(339.0859375, 408)` and resolved to `neighbor-token`, which is not the audited text node, a descendant, or an ancestor.
- The current implementation tested four rendered fragment centers.
- Every fragment center resolved to `wrapped-inline` and was correctly recognized as its own text surface.
- The geometry verifier passed, proving that the fixture would exercise the legacy false positive while the fragment-aware implementation avoids it.

## Isolated Pi Gate

The durable prompt is `evaluations/slidev-quality-audit/forward-wrapped-inline-prompt.md`. It requires exact JSON, Markdown, and two screenshot outputs and includes the same pinned two-slide evaluator fixture.

No Pi process was started after the root task observed the global error `The usage limit has been reached` with zero Spark tokens remaining. Retrying would not produce model evidence and would only create an infrastructure-failure run. Classification: `infrastructure-blocked (global Spark quota exhaustion)`. Re-run the prompt in runtime profile, JSON strict mode, with exact-output checks when Spark capacity is restored.

Suggested release command:

```powershell
uv run --script scripts/run-pi-skill-eval.py slidev-quality-audit --prompt-file evaluations/slidev-quality-audit/forward-wrapped-inline-prompt.md --mode json --strict --require-exact-command-from-prompt --run-id 20260902-slidev-quality-wrapped-inline-spark-1 --expect-output outputs/audit/quality-report.json --expect-output outputs/audit/quality-report.md --expect-output outputs/audit/screenshots/slide-001-click-00.png --expect-output outputs/audit/screenshots/slide-002-click-00.png --expect-output-json-field outputs/audit/quality-report.json::slideCount=2 --expect-output-json-field outputs/audit/quality-report.json::stateCount=2 --expect-output-json-field outputs/audit/quality-report.json::findingCount=1 --expect-output-json-field outputs/audit/quality-report.json::ruleCounts.covered-content=1
```

Until that command passes and its event trace is summarized, the deterministic and integration layers are green, while the policy-mandated isolated Spark layer remains explicitly unverified.
