# Independent ECharts Native Override Review — 2026-10-03

The finite recheck accepts the root agent's final helper, SHA-256 `2d0efdadd18d071af33305ebff9b86a3520f5efc6af84905217f33d7c9cb008b`. The ECharts and Slidev ECharts helper copies are byte-identical. All 22 final actual rendering states pass; the same 22-state baseline reproduces 14 failures. Original series and edge show flags, terminal symbols and actual native glyph paths remain unchanged.

The [compact before/after result](echarts-overrides-20261003.json) records every state, its canvas/palette, measured shaft/head contrast and geometry/flag preservation. The [reusable project reproducer](../../projects/arrow-contrast/scripts/review-native-edge-overrides.ts) runs eight case categories in actual client SVG for each palette; the three markLine categories also render through native SVG SSR. This gives 16 client states and six SSR states per phase, 44 total before/after states.

The independent review found three concrete supported native rendering bypasses and disclosed them before source mutation:

| Native case | Baseline visible contrast | Final visible contrast | Cause |
| --- | --- | --- | --- |
| Per-terminal `markLine` arrow with a series symbol of `none` or `['circle','none']` | 1.1096:1 for shaft and head | 3.8429:1 for shaft and head | The helper initially looked only at the parent symbol and skipped the native per-terminal override. |
| Moving arrow with series effect enabled and edge `effect.show: false` plus a pale edge effect color | 1.5580:1 head | 3.8429:1 head | Native ECharts selects EffectLine at the series level and still renders this glyph; the helper initially treated the edge flag as disabling it. |
| Series or edge native effect opacity of 0.1 on a black moving arrow | 1.2539:1 head | 21:1 head | Native EffectLine applies item-style opacity to the moving symbol; the helper initially qualified its color alone. |

Ordinary default/inherited moving-effect color and `markLine` endpoint itemStyle overrides already passed and remain controls. Native `markLine` symbols share the qualified line color/opacity; endpoint itemStyle did not independently override the visible head. The default effect symbol is a circle; directional effect qualification concerns an actual arrow symbol. Native effect opacity is accepted by EffectLine's style mapper even though it is absent from the published effect option type; the final helper now measures and repairs that actual opacity.

The baseline helper is pinned to the immutable copied Slidev final-5 trial resource, SHA-256 `8e6156f545f174112a15e99c8639a20595fbe01bcc80e5932a26cf291e742459`. The initial exploratory SSR/client scripts, their JSON, SVGs and screenshots remain retained under `projects/arrow-contrast/artifacts/reviews/`. A first combined-capture attempt stopped when changing an SVG XML document into HTML with `setContent`; its partial output is retained under `edge-overrides-before-attempt1/`. The final reusable capture resets to a blank HTML document before client rendering. This was an evidence-capture repair and changed no canonical producer.

Reproduction commands:

```powershell
node --experimental-strip-types projects/arrow-contrast/scripts/review-native-edge-overrides.ts --phase before --module evaluations/runs/20261003-arrow-slidev-echarts-final-5/workspace/skills/slidev-echarts/assets/templates/echarts-colorsets.mjs
node --experimental-strip-types projects/arrow-contrast/scripts/review-native-edge-overrides.ts --phase final
```

Detailed final reports, SVGs and screenshots are retained under `projects/arrow-contrast/artifacts/reviews/edge-overrides-final/`; baseline counterparts remain under `edge-overrides-before/`. Final screenshots for a moving opacity repair, per-terminal markLine arrow and inherited edge show flag were inspected independently and retain clear native direction with no added rims or halos.

This review used ordinary Cartesian axes and a declared white canvas in both palettes. It did not expand support to custom symbols, gradients, host-opacity effects or filled region crossings. The frozen helper's source inspection found no additional material declared-canvas/percentage-alpha, graph focus inheritance, pixel-inset nonmutation or documented target-clearance defect. Root-owned isolated trials and publication binding remain separate gates in [the main arrow report](../arrow-contrast/validation-20261003.md).
