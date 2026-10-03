# Native ECharts and Slidev arrow validation — 2026-10-03

Both final owning runtimes pass strict isolated qualification and independent
inspection of their exact generated artifacts. Selected runs are
`20261003-arrow-echarts-animated-svg-final-11` and
`20261003-arrow-slidev-echarts-final-8`. The full current artifact probe passes
20 actual browser states with no errors or covered head samples.

The byte-identical owning helper is SHA-256
`2d0efdadd18d071af33305ebff9b86a3520f5efc6af84905217f33d7c9cb008b`.
It qualifies native graph edges, Cartesian lines, moving arrow effects,
default markLine heads, per-terminal symbol overrides and declared
emphasis/select/blur styles. It measures unrounded alpha composites against
the actual declared canvas, chooses allowed paint reaching 3:1 and uses at
least a 1.5 px shaft. Unknown, gradient and unresolved CSS arrow/backing paint
is rejected; percentage alpha is parsed and composited. Solid category bodies
remain borderless, and canonical tokens remain unchanged.

Continuous two-point Cartesian routes can use the public pixel-inset helper
after layout. It preserves original coordinates and shortens native terminals
along curved tangents. Seven pixels gives a radius-four endpoint mark three
pixels of clearance. Resize and click changes recompute from original data.
Unsupported axes, polylines, short routes and nonfinite geometry fail rather
than receive guessed offsets. Fixed graphs retain native view coordinates and
endpoint clipping; a zero-gap native terminal is acceptable when its complete
head remains outside the target silhouette.

## Actual evidence

| Gate | Result and boundary |
| --- | --- |
| Both owning `scripts/test_arrow_options.py` commands | 216 palette/backing combinations per bundle plus focused native override, alpha, unsupported paint/geometry, in-place preparation, nonmutating inset and source-fidelity checks pass. |
| [Eight native states](echarts-final-20261003.json) | Graph and curved routes, both palettes, white/quiet canvases. All actual sampled heads and shafts pass; minimum 3.08987:1. [Baseline](echarts-before-20261003.json) reproduces four pale graph failures around 1.09–1.11:1. |
| [Independent 22-state native override review](../arrow-contrast-diagrams/echarts-overrides-20261003.json) | 16 client and six SSR states per phase. Fourteen baseline failures become zero final failures; original symbols/show flags and native glyph paths remain unchanged. Per-terminal markLine: 1.1096 → 3.8429; inherited item-show-false moving effect: 1.5580 → 3.8429; native effect opacity: 1.2539 → 21. |
| [Unsupported paint controls](echarts-unsupported-paint-final-20261003.json) and [declared-backing controls](echarts-prepared-backing-final-20261003.json) | Genuine sealed old-helper counterexamples are retained. Unknown/gradient CSS paints and unresolved backings are refused, not measured against fabricated white. Percentage alpha receives a real visible composite. |
| ECharts acceptance gallery | Production build and browser verifier pass all 43 cards/SVGs. |
| [Eight actual Slidev delivery states](slidev-routes-20261003.json) | Four routes across click states, widths 1280/1600 and normal/reduced motion. Minimum 3.21845:1; complete heads remain outside target marks. Only the exact offline Wake Lock permission denial is classified as an expected host warning. |
| [Current accepted-artifact probe](echarts-runtime-artifacts-20261003.json) | Four native charts at static, animation-final and reduced-motion states (12), plus the exact generated Vue component compiled/rendered at two widths, click states and motion preferences (eight). All 20 pass with no browser errors; sealed workspace files are read-only. |
| [Current component-only probe](slidev-runtime-component-20261003.json) | Eight independently passing states on the exact Slidev-8 component. |
| [Independent SSR recipe review](custom-native-ssr-recipe-review-20261003.json) | Actual ECharts 6.1.0 in both palettes: opaque native 60 px solid nodes, no painted stroke, 16 px native heads, 2 px rendered shafts, minimum 3.8429449545:1; no hidden head interior. |

The four large browser reports retain compact per-state minima, paint/opacity,
counts and backing classifications; detailed sample arrays remain under ignored
project artifacts with their exact SHA-256. Final graph and component
screenshots were manually inspected. Counts overlap and are not an aggregate
claim of distinct scenes or continuous-frame coverage.

## Strict trials and retained failures

The [runtime receipt](echarts-runtime-20261003.json) retains all completed runs.
Both selected trials use the existing recorded `openai-codex/gpt-5.6-luna`
exception. Observed model, valid JSON, zero tool errors, exact outputs, clean
read surface and immutable copied payloads pass. Final ECharts runtime SHA-256
is `07590acbf38e4d4cbd7bc67402744cbe5baba73191b4b338bc6d2df5d4dec9a8`.
The main [runtime seal](final-runtime-20261003.json) binds both current payloads
and rechecks every accepted artifact byte; the parent [report](validation-20261003.md)
records installation, commit and publication acceptance.

Attempts remain classified separately:

- Initial strict passes became superseded by actual moving-effect, declared
  canvas, per-terminal marker and native effect-opacity repairs. The final
  native override probe uses the immutable copied Slidev-5 helper as baseline.
- ECharts-2 emitted wrong exact filenames; files were not renamed into a pass.
  ECharts-3 guessed nonexistent modular axis exports and a script path; strict
  gates retained three tool errors. Owning guidance now names the registered
  full package and exact scripts. ECharts-4/5 passes are superseded.
- ECharts-6 passed before the later in-place preparation reference clarification.
  Slidev-6/7 failed an edit and cross-palette shared-object assertion. Guidance
  now states that preparation mutates nested options; each chart needs fresh
  state declarations. Cartesian insetting remains separately nonmutating.
- ECharts-8 misordered prepared-style assertions and applied Cartesian logic to
  graph data. ECharts-9 compared undefined JSON fields. ECharts-10 read four
  nonexistent fresh-workspace files and explicitly removed the native graph
  coordinate system. Repaired outputs are retained, but tool errors remain
  strict failures. Compact native SSR guidance now states that layout none
  still uses view coordinates, with a directly verified recipe. The final
  prompt explains fresh-workspace discovery and keeps small assertion loops.
- The first deck probe guessed three routes while the actual fixture has four;
  raw failed evidence remains retained. The final probe derives count from
  fixture data. This did not change chart geometry or contrast requirements.
- The first independent SSR recipe probe counted later-painted nodes as
  underlays and a default unpainted stroke width as a border. The retained
  failed evaluator was corrected to respect paint order and `stroke: none`;
  the recipe bytes stayed unchanged.

## Reproduction and limits

```powershell
uv run --script skills/echarts-animated-svg/scripts/test_arrow_options.py
uv run --script skills/slidev-echarts/scripts/test_arrow_options.py
node --experimental-strip-types projects/arrow-contrast/scripts/review-echarts-arrows.ts --phase final
node --experimental-strip-types projects/arrow-contrast/scripts/review-slidev-routes.ts
node --experimental-strip-types projects/arrow-contrast/scripts/review-unsupported-paint.ts --phase final
node --experimental-strip-types projects/arrow-contrast/scripts/review-native-edge-overrides.ts --phase final
uv run --script projects/arrow-contrast/scripts/run_echarts_pi.py --attempt 11 --skills echarts-animated-svg
node --experimental-strip-types projects/arrow-contrast/scripts/review-runtime-echarts.ts --echarts-run 20261003-arrow-echarts-animated-svg-final-11 --slidev-run 20261003-arrow-slidev-echarts-final-8
```

Also run the ECharts fixture's `npm run build`/`npm run verify` and Slidev's
`npm run build:html`. The two upstream Rolldown pure-annotation warnings do
not change chart behavior. A declared-canvas helper cannot infer arbitrary
intervening fills, inherited host opacity, custom symbols or plot obstacles.
Those surfaces require actual rendered review. Finishing an animation verifies
its readable final state, not every reveal frame. Interior paint sampling
excludes antialias edge blends and does not certify complete accessibility
conformance or arbitrary future graph routing.
