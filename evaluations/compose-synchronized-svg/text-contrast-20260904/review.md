# SVG text/background pairing review — 2026-09-04

The user identified text foregrounds that were poorly chosen for their backgrounds and requested continued Luna generation and critique. This pass changes the canonical `compose-synchronized-svg` bundle. It does not claim coverage of every SVG-producing skill.

## Findings and changes

Palette-wide checks missed the actual surface under individual labels. The previous world HUD used a foreground intended for light surfaces on its dark navigation panel. The previous focus audit compared every label with its module frame, excluded focused modules, and omitted outer controls. Transparent backplates, flow ribbons, card edges, and overridden renderer font sizes could create a different local background.

The generator now derives foreground/background pairs for inverse controls and numeric labels, preserves exact supplied concept paints for marks, and attenuates only generated decorative tints when needed. Essential label surfaces remain opaque during focus. Caption bands, wider flow endpoints, lower chart margins, and labels beside dense bars keep text on its intended surface. Global text fill and font-size overrides no longer defeat explicit renderer choices.

The browser audit resolves solid foreground paint and self alpha, captures the actual background with text hidden, then uses individually encoded glyph masks to sample local background pixels. It compares author colors rather than antialiased letter-edge darkness. It does not substitute a bounding-box majority color. Restoration tests cover exact inline styles, capture failure, and repeated CSS transitions. Scenarios, focused and unfocused content, outer controls, navigation anchors, reduced motion, and script-free views are included.

The generated-text threshold is conservatively 4.5:1 for all sizes, without rounding a failure upward. This follows the relative-luminance method in [W3C Contrast Minimum](https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html). Unsupported masks, mixed text paints, halos, group-opacity compositing, and unsupported filters remain explicit incomplete findings; hidden or unpainted text is counted separately. A passing sampled view is not accessibility certification or proof of every animation frame.

## Controlled comparison

Each before/after pair uses the same brief, canonical plan, data, and initial scenario. Before generation uses the local source snapshot from the beginning of this pass. Baseline source hashes and artifact hashes are retained in `results.json`; bulky source snapshots, SVGs, PNGs, and logs remain under the ignored project artifacts directory.

| Case | Initial failures before | Initial failures after | After labels measured | After full text-state checks | After full label observations |
| --- | ---: | ---: | ---: | ---: | ---: |
| World navigation, light theme | 11, plus 4 incomplete | 0 | 33 | 26 | 718 |
| Near-threshold gray on white | 25 | 0 | 79 | 7 | 544 |
| Compatible dark theme | 0 | 0 | 79 | 7 | 544 |
| Exact light concept mark | 0 | 0 | 79 | 7 | 544 |

The controlled initial total is **36 confirmed failures before and zero after**, with incomplete findings reduced from four to zero. The current full browser audits pass **47 text-state checks and 2,350 label observations**, with zero text-contrast issues. Observations repeat labels across states; they are not 2,350 distinct labels. The dark and light-mark initial cases are regression controls, not evidence of a before/after numerical failure reduction.

The local [comparison page](../../../projects/svg-text-contrast/artifacts/comparison.html) passes desktop and 390-pixel mobile inspection: four pairs, eight loaded images, no page overflow, and no browser errors. Source SVGs open from each image. The current world HUD secondary copy is visibly clearer. The gray concept mark remains exact while its associated value text uses readable ink.

## Deterministic and repository validation

All **116 skill tests** pass: 80 existing tool regressions, 13 theme tests, 10 rendered text-audit tests, three generated pairing tests, six theme-generation tests, two network-port tests, and two stack-reconciliation tests. The independent Pi harness also passes its 12 tests. Pattern IDs, skill metadata/structure, bundle independence, payload, quick validation, and diff checks pass. The local installation is synchronized with all 36 source-owned files in this skill.

Retained development failures led to real corrections: an early full suite found five affected layout/expectation cases; a subsequent suite retained one long flow-endpoint caption failure. The final 80-test suite passes in 133.906 seconds. No contrast threshold or failed check was suppressed to obtain that pass. Initial sampler drafts were not accepted until opacity, variable backgrounds, glyph attribution, and style-restoration regressions passed.

Reproduction commands:

```powershell
uv run --script projects/svg-text-contrast/scripts/build_contrast_cases.py
uv run --script projects/svg-text-contrast/scripts/capture_contrast_cases.py
uv run --script projects/svg-text-contrast/scripts/run_luna_validation.py
uv run --script projects/svg-text-contrast/scripts/inspect_luna_outputs.py
uv run --script projects/svg-text-contrast/scripts/collect_evidence.py
```

The fixed runner uses `openai-codex/gpt-5.6-luna`, high reasoning, strict JSON, exact expected paths, JSON field assertions, and the isolated runtime payload. Run IDs are append-only; use a new cohort ID for a future repetition. The source snapshot is local retained evidence, not a published fixture. All transient test directories were placed inside the project artifacts tree.

## Isolated Luna evidence

All **five strict runs pass**: one command contract, one incompatible-palette boundary, and three fresh repetitions of a naturalistic municipal-water task with exact dark surfaces. All five read-surface reviews and evaluator-owned output inspections also pass. Every run used frozen runtime SHA-256 `d15c415dfaf980eed6705b20534cb56e7e11b33f3d5bb09c5d20403f58c44c61`, with valid events, the observed Luna model, zero tool errors, exact outputs, and an unchanged copied payload. The user-requested Luna model is an explicit exception to the repository's default Spark model.

| Run suffix after `20260904-svg-text-pair-luna-` | Case | Strict result | Independent result |
| --- | --- | --- | --- |
| `contract` | Near-threshold text and exact gray mark | Pass | Preserved brief data and colors; rendered scenario text passes |
| `boundary` | Fixed white text on yellow | Pass | Original colors retained, request rejected, no generated SVG |
| `dark-1` | Municipal water, repetition 1 | Pass | Exact dark surfaces, legal domains, scenario values, arithmetic, bindings, and text pass |
| `dark-2` | Municipal water, repetition 2 | Pass | Same independent contract passes |
| `dark-3` | Municipal water, repetition 3 | Pass | Same independent contract passes |

The naturalistic runs required authoring recovery inside their isolated workspaces: they encountered one, four, and three preflight findings respectively. These included nonconserving flow selection, insufficient concept-mark contrast, an alias color override, and one malformed brief. The preflight reports findings without a tool error and blocks compilation until they are resolved. The run traces and `expectedAuthoringFindings` preserve every occurrence; these are successful recovery runs, not first-attempt generation successes. No canonical skill source changed during the cohort.

The boundary requires unchanged white text and yellow surfaces to be rejected without publishing an SVG. The contract requires a preserved `#888888` concept mark and preserved `#767676` text roles on white. The naturalistic task requires exact `#101820` canvas and `#18242f` cards, three scenarios, zero-demand support, six meaningful modules, and a color-editing handoff. Independent arithmetic checks recompute water processing, leakage, delivery, unmet demand, load, and every bound mark across normal, peak, repair, and zero demand.

Independent checks pass all **12 water arithmetic states** and **14 rendered text states** across the produced SVGs. Direct overview and module-crop inspection confirms readable value labels in the first passing naturalistic run, retained as the representative [dark SVG](../../../projects/svg-text-contrast/artifacts/luna/dark-1/dashboard.svg). All three runs remain in the evidence; no best-of selection was used. Read traces contain only the task prompt, this skill's focused references/template, and generated outputs. The boundary reads its template through an explicit shell command; full shell commands were also reviewed for indirect context reads.

## Visual review and disposition

Luna supplied both discovery criticism and a final screenshot review. The [discovery review](discovery-review.md) describes intermediate source and superseded declarations; it is retained to show why the changes were made. Its comments about old compact artifacts and latent HUD states are not counted as visible failures in those compact overviews. The [final visual review](final-visual-review.md) found no confirmed remaining text/background failure in the latest four controlled renders.

The reviewer knew before/after labels and validation results. This is an evidence-guided critique, not a blinded preference study, universal quality score, or sealed holdout. Near-threshold gray has little margin (the lowest local after observation is about 4.504:1); the test deliberately preserves that supplied color instead of silently darkening it. The sparse world overview, small footer labels, dense dependency endpoints, and long cross-panel routes remain broader composition findings.

Keep the skill **`validating`** for its full visual trigger surface. Accept the focused text-pairing improvement on the recorded deterministic, isolated, independent, and visual evidence; retain the broader layout findings and authoring-recovery friction as open work. The local installation was refreshed, and no Pages example or publication was changed.
