# Standalone Treemap Builder Local Acceptance — 2026-10-03

The new deterministic [builder](../../skills/d3/scripts/build_treemap.py) passes local acceptance. This is builder-level evidence; it does not replace the isolated Pi release gate or turn any prior failed Pi attempt into a pass.

- Final script: 234 lines; SHA256 `53fb3be9152d7107dadf9aa0b573736ecaef147cba483fc322e1f4d23742eac2`.
- Focused [test suite](../../skills/d3/assets/examples/skill-tests/test_build_treemap.py): **5/5 tests**, **96 HTML states** and **4 production SVG export states**, all passing.
- Exact contract and naturalistic prompt data: **8/8 independent HTML/SVG render states** at 960/420 pixels, zero findings, browser errors or external network requests.
- Largest branch area-fraction error: contract `0.004353`, naturalistic `0.007117`; largest within-branch leaf area-fraction error: contract `0.004957`, naturalistic `0.004877`. Both are below the independent grader's existing `0.06` threshold.
- Root and worker directly inspected the resulting desktop/mobile screenshots and confirmed clear grouping, contained direct names/values, borderless opaque tonal cells and exact black/white labels.

## Implementation scope

The builder embeds the unmodified bundled D3 runtime and computes real `d3.hierarchy().sum().sort()` and `d3.treemap()` geometry. Native `treemapDice` divides the root into stable vertical branch columns; native `treemapSlice` divides each branch into horizontal weighted leaf rows. This standalone tiling keeps the normal prompt data readable at narrow widths. It is separate from the canonical gallery treemap renderer, whose geometry was preserved.

The first three sorted branches use the existing red/two-gray families in colorset1 or blue/orange/green families in colorset2. A single sibling uses the middle tone, two use endpoints, three use all tones, and larger sibling sets reuse the finite ramp with neutral gutters and direct labels. The bundled colorset adapter finalizes every HTML artifact. Replay, resizing and export retain family/tone assignments. Genuinely tiny cells receive a complete visible SVG data key instead of silently losing names or values; the normal three-by-three prompt cases require no key.

Input checks reject invalid hierarchy depth, empty branches, duplicate sibling names, control characters, nonnumeric/nonpositive/nonfinite weights, unsafe aggregate numeric totals and writes inside the skill resource. Literal HTML/script, color-like and template-placeholder text survives as text. Tests cover changed data, one/two/four-child boundaries, tiny-cell fallback, both colorsets, initial state, Replay twice, reduced motion, 960/420 pixels, offline/palette compliance and the existing production exporter.

## Commands and retained evidence

```text
uv run --script skills/d3/assets/examples/skill-tests/test_build_treemap.py --artifacts projects/treemap-tones/artifacts/builder
uv run --script scripts/validate-pattern-ids.py
uv run --script scripts/test-skill-independence.py
```

For each exact prompt case, run the builder with `--data hierarchy.json --output <exact-name>.html --title "Operating portfolio"`, then `render_d3_svg.py <html> --output <exact-name>.svg --viewport 960x720 --wait-ms 650`. Capture with `projects/treemap-tones/scripts/inspect_isolated_artifact.py <workspace> --basename <exact-name> --output <review>`, then grade with `grade_isolated_artifact.py <review>/render-review.json --case contract|naturalistic --output <grade.json>`.

Bulky local evidence remains under `projects/treemap-tones/artifacts/builder/`: `acceptance-summary.json`, final `test-report.json`, both exact-case `grade.json` and `review/render-review.json`, HTML/SVG files and screenshots. The final independent capture SHA256 values are contract `f85dae735959c60b4e6ee4ed2ca1ace4e6b3c5b4f01f41ef699767e739a390dd` and naturalistic `653406068cd42c555a0e3c1b434b8911de1532a5c1d8eb5f3bb3932e2645927b`.

Retained unsuccessful local authoring checks are recorded separately, without counting them as passes:

- `test-report-initial-failure.json`: static SVG description was missing and a word was split before smaller fonts were tried; both corrected.
- `test-report-second-failure.json`: a narrow word still needed a smaller readable font; the test helper also used `passed` instead of the palette validator's public `ok` field; both corrected.
- `test-report-before-tiling.json`: passing earlier suite, superseded by the final tiling revision.
- Both `grade-before-tiling.json` files and matching captures: squarify created narrow Recovery/Discovery cells at 420 pixels; corrected through native tiling.
- Both `grade-before-dice.json` files and matching captures: squarified root plus sliced leaves created short rows and invoked the complete key for normal data; corrected with root dice columns.
- `test-report-boundary-header-failure.json`: the one-child branch header needed bounded 12-to-9-pixel fitting; corrected and the affected suite rerun passed.

The final script was frozen before the new isolated runtime cohort started. No runtime edits followed this local acceptance.
