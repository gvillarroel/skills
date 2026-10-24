# Reflex XY colorsets and published examples

Date: 2026-10-24. Skill: [reflex-xy](../../skills/reflex-xy/SKILL.md).
The scoped two-palette revision meets its contract and naturalistic thresholds.
The broader skill remains `validating` because the earlier general chart-use
naturalistic cohort is retained at 1/3 strict passes; this revision does not
replace or pool those results. See [the original validation](validation-20261024.md).

## Frozen subject

The executable baseline is `xy==0.0.8`. Both named colorsets are bundled as an
exact copy of `docs/colorsets.json`, with SHA-256
`b557cb508d9b31534506b9ae22ad3073e8951b49f6ab4e2251f6727ac92a405c`.

| Payload | Files | Inventory SHA-256 |
| --- | ---: | --- |
| Source and full | 18 | `e3e3d030a84e948fc63f523a3e0c3351bca816ac93c8cd140e256c7ecab4def7` |
| Runtime | 15 | `f48cc7462c7372aa3ddbcca1cdd0e60f0eea222b698faf0ecc4897411895d3fb` |

Runtime excludes the three acceptance-gallery sources. Source/runtime/full
audits pass and the source digest was unchanged during the final audit.
The final source/full digest includes an EOF-whitespace-only gallery cleanup;
the evaluated runtime digest is unchanged.
The reusable helper supports theme, categorical order, exact sequential stops,
discrete numeric bins, contrast-aware labels, legend styling and browser chrome.
The starter and diagnostic accept `--colorset colorset1|colorset2`; colorset1
is the default. References explain capacity errors, exact-paint limits and
portable helper/palette copies.

## Deterministic checks and promoted corrections

Seven helper tests pass, including real native SVG paint checks and offline
browser pixels, hover/focus controls and computed tooltip colors. Both starter
variants export HTML/SVG/PNG. Both updated diagnostics pass native export with
the selected colorset and 640 by 360 PNG dimensions.

XY adds a default `#cccccc` legend border and continuous colormaps interpolate
additional colors. The helper now uses a transparent legend background and
the exact-paint recipes use discrete bins and opaque borderless fills. Legend
guidance requires visually verified empty space because an upper-right legend
can obscure high-valued records. These are reusable instructions, rather than
corrections confined to the gallery.

```powershell
& projects/reflex-xy/artifacts/runtime/.venv/Scripts/python.exe skills/reflex-xy/scripts/test_xy_colorsets.py --output-dir projects/reflex-xy/artifacts/palette-tests -v
& projects/reflex-xy/artifacts/runtime/.venv/Scripts/python.exe skills/reflex-xy/scripts/diagnose.py --colorset colorset1 --output-dir projects/reflex-xy/artifacts/final-diagnostic/cs1 --report projects/reflex-xy/artifacts/final-diagnostic/cs1.json
& projects/reflex-xy/artifacts/runtime/.venv/Scripts/python.exe skills/reflex-xy/scripts/diagnose.py --colorset colorset2 --output-dir projects/reflex-xy/artifacts/final-diagnostic/cs2 --report projects/reflex-xy/artifacts/final-diagnostic/cs2.json
```

## Isolated forward tests

The deliberate model exception remains `openai-codex/gpt-5.6-sol`, following
the retained Spark account/provider rejection before tools. All cases use
runtime-only payloads, JSON strict mode, exact output checks, no ambient
context/discovery, an unchanged read-only bundle and independent review.

The initial colorset cohort used runtime SHA-256
`3bf749102572c9819f9800e9dfbee30cf1144b69ee52d7e2b695a0f13579f6e9`.
Its contract and three naturalistic attempts passed strict runtime and artifact
checks, but two naturalistic visuals obscured an endpoint with the legend.
Naturalistic joint acceptance was 1/3. Those attempts are retained under
`20261024-reflex-xy-colorsets-{contract|naturalistic}-sol-*` and are not pooled
with the final subject.

After promoting the legend correction into the entrypoint and compact
reference, a fresh frozen-subject cohort used the unchanged prompts:

| Final case | Strict runtime | Independent artifacts | Manual visual | Joint |
| --- | ---: | ---: | ---: | ---: |
| Contract | 1/1 | 1/1 | 1/1 | 1/1 |
| Naturalistic | 2/3 | 3/3 | 3/3 | 2/3 |

The exact run prefix is `20261024-reflex-xy-colorsets-legend-`, followed by
`contract-sol-1` or `naturalistic-sol-1`, `-2`, `-3`. Naturalistic repetition 2
retains a strict **agent-workflow failure**: an extra agent-authored Playwright
`locator("canvas")` matched three canvases. The agent corrected its selector
afterward, but the zero-tool-error gate remains failed at event line 2289.
There was no waiver, repaired output, replacement repetition or cross-subject
pooling. The bundled verifier had passed, and independent artifact and visual
checks passed for this run.

Independent checks cover all eight final variants: exact canonical native
paints, original six-record data, individual point coordinates and group fills,
stable category order, identical paired geometry, actual offline browser fills,
canonical controls, visible point tooltips, and byte-identical regenerated
SVGs. All traces use only `gpt-5.6-sol`, valid JSON and clean read surfaces.

Prompts: [contract](../pi-prompts/reflex-xy-colorsets-contract.md) and
[naturalistic](../pi-prompts/reflex-xy-colorsets-naturalistic.md).
Reproduce the naturalistic cohort with three fresh run IDs:

```powershell
uv run --script scripts/run-pi-skill-eval.py reflex-xy --prompt-file evaluations/pi-prompts/reflex-xy-colorsets-naturalistic.md --model openai-codex/gpt-5.6-sol --mode json --strict --run-id <fresh-run-id> --timeout-seconds 600 --expect-output app.py --expect-output results/cs1.html --expect-output results/cs1.svg --expect-output results/cs2.html --expect-output results/cs2.svg --expect-output results/palettes.json
uv run --script scripts/summarize-pi-json-events.py evaluations/runs/<fresh-run-id>/events.jsonl --require-model gpt-5.6-sol --fail-on-invalid-json --fail-on-tool-error
& projects/reflex-xy/artifacts/runtime/.venv/Scripts/python.exe projects/reflex-xy/scripts/verify_palette_pi.py --run <fresh-run-id>
```

The contract uses its named prompt, `--require-exact-command-from-prompt`, and
ten `--expect-output` paths: each palette's `chart.html`, `chart.svg`,
`chart.png`, `browser.json` and `browser.png` under `results/cs1/` and
`results/cs2/`. Raw manifests/events remain in ignored `evaluations/runs/`.
The consolidated report is
`projects/reflex-xy/artifacts/pi-palette-verification/final-legend-cohort-summary.json`;
native/browser reports, inspected screenshots and tooltip screenshots are in
the per-run directories beside it. The final audit is
`projects/reflex-xy/artifacts/pi-palette-verification/payload-audit-472a0046/report.json`.

## Gallery and publication contract

Stable example-set ID: `reflex-xy-colorsets`. Public route:
[XY Colorset Chart Gallery](https://gvillarroel.github.io/skills/examples/reflex-xy-colorsets/).
The main examples catalog registers the gallery, and all twelve item IDs are
registered with the repository pattern validator.

The six mechanisms are category scatter, trend lines with a missing-value gap,
grouped bars, histogram, binned heatmap and dense scatter. Each has CS1 and CS2
variants with identical synthetic data, domains and geometry. The histogram
includes all 900 observations, the dense scatter renders all 8,000 points, and
the matrix uses data-unit rectangles with 84 original integer labels. Mobile
spacing and domain margins prevent overlapped cells and clipped end ticks.

The gallery offers native SVG previews, lazy interactive HTML, palette filters,
stable anchors, SVG downloads and a portable five-file source download set.
Source-only regeneration works without repository paths. The compact reusable
recipes live in the skill's own `references/pattern-recipes.md`; normal runtime
use never reads the acceptance gallery.

The final local Pages review passes: twelve exact-paint SVGs, six matched
geometry/text pairs, twelve desktop and twelve mobile interactive charts,
twelve visible wheel interactions, six responsive filter states, a single
Explore iframe, 33 working links, and root/catalog discovery. There are zero
browser console/page errors, external browser requests, mobile overflows or
clipped labels. The report is
`projects/reflex-xy/artifacts/colorset-gallery-review-pages/gallery-verification.json`.

```powershell
uv run --script scripts/build-pages.py
& projects/reflex-xy/artifacts/runtime/.venv/Scripts/python.exe projects/reflex-xy/scripts/verify_colorset_gallery.py --output-dir projects/reflex-xy/artifacts/colorset-gallery-review-pages
& projects/reflex-xy/artifacts/runtime/.venv/Scripts/python.exe projects/reflex-xy/scripts/verify_colorset_gallery.py --base-url https://gvillarroel.github.io/skills/ --output-dir projects/reflex-xy/artifacts/colorset-gallery-review-published
```

Publication uses the existing `main`-branch
[Pages workflow](https://github.com/gvillarroel/skills/actions/workflows/pages.yml).
The public verifier downloads the deployed manifest, twelve native SVGs,
gallery and source files, matches the verified release and repeats browser
checks against the public route. Its output directory above is the retained
post-deployment evidence location.

Repository checks include pattern IDs (1,234 total; twelve new), skill structure,
bundle independence, payload, colorset coverage, authoring audits, pattern
source traversal, Pages boundary (14 tests), unified Pages format and local
installation sync/check. The final local build contains 789 files, 64.54 MiB.

Arbitrary user charts, continuous renderer-derived tones, antialiased edge
pixels, live Reflex callback delivery and broad performance remain outside
the exact-paint and gallery acceptance claims.
