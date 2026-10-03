# Native Diagram Arrow Validation — 2026-10-03

The final Mermaid, PlantUML and Slidev quality-audit runtime payloads pass their selected strict isolated trials. The native browser gate passes 252 states, 1,210 shaft instances, 30 explicit native head instances, and 716 actual referenced marker instances. The 5,272 projected marker paint samples include no covered head sample. There are zero readable shaft/head contrast findings; the minimum measured readable sample contrast is 3.0853:1 against the actual local backing.

The machine-readable [sealed result](validation-20261003.json) records all six runtime attempts, exact artifact paths and hashes, payload identities, retained native occlusion counts, browser regression case IDs, and fixture publication boundaries. Its [sealing script](../../projects/arrow-contrast-diagrams/scripts/seal-validation.py) compares fresh runtime-only copies with the selected trial payloads. It passed after the final source freeze. These are tested working-tree byte hashes; repository publication records separately disclose Git text normalization.

## Scope and Repairs

The behavior-changed bundles owned by this group are `mermaid`, `plantuml-colorset-renderer`, and `slidev-quality-audit`. `slidev-animejs` required no source change: six SVG asset templates were checked at settled and mid-reveal states. ECharts and Slidev ECharts were handed to the root agent; their final independent SSR, deck and strict trial evidence is maintained in [the parent arrow report](../arrow-contrast/validation-20261003.md).

- **Mermaid:** The final native finishing pass chooses the nearest allowed paint that reaches 3:1 on every crossed backing, samples actual straight/Bézier/elliptical-arc geometry and polygon contours, and preserves meaningful glyphs. It creates per-edge marker identities with native units/viewBox/refX geometry and explicit clearance, including the animation marker aliases. C4 bypass links move into exterior gutters with their own wrapped captions. Event-modeling heads approach cards perpendicularly. ER capacity spacing is 80 so full bars, circles and crowfeet fit outside entities; an insufficient gutter is rejected. Native XHTML ER captions use exact black/white against their composited CSS backing. Cynefin dark-domain and pale branch connectors receive contrast-safe palette paints. Solid node bodies keep their borderless presentation.
- **PlantUML:** Newly rendered SVGs receive the same supported native paint/backing inspection through a self-contained bundled helper. SVG-capable authored PNG output derives from the finished SVG, including PNG-only requests, so exports share corrected paint and geometry. The raster canvas is explicitly opaque white, and the report records `svg_derived: true`. Raster-only Ditaa, standalone mathematics and source-media fidelity paths retain their native behavior.
- **Slidev quality audit:** Marked shafts and explicit heads are measured even when their DOM box has zero width or height. The actual browser check composites HTML ancestor canvas paint, SVG regions and alpha in paint order, projects referenced marker glyphs, and reports `arrow-low-contrast` and `arrowhead-covered`. Hollow glyphs are judged by visible rims. An explicit transient flag applies only during an active partial reveal; it cannot excuse a final low-contrast arrow.

Reusable rules and supported-geometry limits are in [Mermaid arrow guidance](../../skills/mermaid/references/arrow-contrast.md), [PlantUML arrow guidance](../../skills/plantuml-colorset-renderer/references/arrow-contrast.md), and [Slidev arrow audit guidance](../../skills/slidev-quality-audit/references/arrow-audit.md). The finite palette definitions and token ordering were unchanged by this follow-up.

## Rendered Evidence

The native inventory covers 186 Mermaid states (31 families × two palettes × static, animated settled and animated mid-reveal), 54 PlantUML SVGs (27 SVG-capable native fixtures × two palettes), and 12 unchanged Anime.js asset states. Families without directional arrows remain in the inventory with zero arrow counts. The scanner measures actual referenced instances, rather than counting unused prototypes in `<defs>`.

Native shaft contacts hidden by semantic silhouettes remain recorded in the JSON. They comprise GitGraph commit contacts, Mindmap branch/root contacts, Timeline date/event layering, Architecture service-icon origins, Wardley procurement symbols, PlantUML railroad terminal contacts and task dependency contacts. They do not hide a referenced head. Eight additional mid-reveal sample contacts are explicitly transient: two GitGraph, four Timeline and two Architecture samples. All eight native occlusion families were also inspected in actual browser screenshots. A broad claim of zero occlusion is deliberately avoided.

The final C4, ER, Event Modeling and Cynefin screenshots were inspected after two animation frames. The selected isolated Mermaid static and settled animated outputs were separately inspected: complete native cardinality glyphs remain in the gutters, black captions remain readable on the pale backing, and white entity labels remain readable on solid red. The selected PlantUML SVG and PNG were inspected, including its curved request route, visible complete head and opaque raster canvas.

The actual production Slidev browser audit passes ten regressions: low shaft, independent low head, safe shaft/head, dark filled path backing, SVG alpha region, shaft alpha, HTML alpha canvas, covered head, transformed marker instance, and explicit filled head without stroke. Negative cases produce the intended errors; passing cases retain an empty finding set. Browser/runtime errors: zero.

Commands for retained local evidence:

```powershell
node --experimental-strip-types projects/arrow-contrast-diagrams/scripts/inventory-native-arrows.ts
node --experimental-strip-types projects/arrow-contrast-diagrams/scripts/probe-quality-arrows.ts
node --experimental-strip-types projects/arrow-contrast-diagrams/scripts/capture-native-arrows.ts
node --experimental-strip-types projects/arrow-contrast-diagrams/scripts/capture-native-arrows.ts --occlusion
node --experimental-strip-types projects/arrow-contrast-diagrams/scripts/capture-native-arrows.ts --runtime
uv run --script projects/arrow-contrast-diagrams/scripts/seal-validation.py
```

Detailed inventories, screenshot files and raw event traces remain under ignored project artifacts and `evaluations/runs/`; their current hashes are recorded in the sealed JSON. Local debugging also exposed and repaired an SVG-XML locator screenshot issue; the capture script now uses actual SVG bounds and waits for computed animation state. This affected evidence capture, not the producer payload.

## Deterministic and Repository Gates

All final targeted checks pass: 16 Mermaid arrow regressions, 17 existing native solid-presentation regressions, 14 PlantUML arrow regressions, 19 existing PlantUML coverage tests, and three actual SVG-to-PNG raster tests. The raster tests cover PNG-only output, reuse of the finished SVG for a two-format request, source/raster exceptions, an explicitly opaque white pixel, retained clear arrow geometry, and removal of temporary output. Gallery/report validators retain 31 Mermaid families and 62 static/animated pairs, plus both PlantUML native coverage reports. Stable pattern IDs remain intact.

```powershell
uv run --script skills/mermaid/scripts/test_arrow_contrast.py
uv run --script skills/mermaid/scripts/test_native_solid.py
uv run --script skills/plantuml-colorset-renderer/scripts/test_arrow_contrast.py
uv run --script skills/plantuml-colorset-renderer/scripts/test_plantuml_coverage.py
uv run --script skills/plantuml-colorset-renderer/scripts/test_plantuml_raster.py
uv run --script skills/mermaid/assets/examples/mermaid-max-complexity/scripts/validate_gallery.py
uv run --script skills/plantuml-colorset-renderer/scripts/validate_plantuml_render_report.py --report skills/plantuml-colorset-renderer/assets/examples/plantuml-colorset-renderer/render-report.json --output skills/plantuml-colorset-renderer/assets/examples/plantuml-colorset-renderer --colorset colorset2
uv run --script skills/plantuml-colorset-renderer/scripts/validate_plantuml_render_report.py --report skills/plantuml-colorset-renderer/assets/examples/plantuml-colorset-renderer-cs1/render-report.json --output skills/plantuml-colorset-renderer/assets/examples/plantuml-colorset-renderer-cs1 --colorset colorset1
uv run --script scripts/validate-pattern-ids.py
uv run --script scripts/validate-skills.py
uv run --script scripts/test-skill-independence.py
```

The final 178 SVG fixture files use LF; none contains CR and none differs from its Git-normalized blob representation. The matching Mermaid gallery SHA-256 is `8e6369677754ff3148a80aab007ad325eace22cfec495311d9733b0599275722`. Atomic bounded fixture writes avoid Windows reader locks and leave unchanged bytes untouched. The root agent handles final payload/publication gates and broader skill status; these targeted passes do not override unrelated historical validation conditions.

## Strict Isolated Runtime Trials

All cases use the existing recorded `openai-codex/gpt-5.6-luna` model exception, runtime-only payloads, strict JSON mode, exact output gates, disabled ambient discovery, and immutable copied resources. The selected trials have zero tool errors, valid events, clean runtime read surfaces, and unchanged payloads. Each read only its own entry point and task-relevant compact resources; none reads acceptance examples or sibling/repository resources.

| Run ID | Outcome | Selection |
| --- | --- | --- |
| `arrow-native-mermaid-luna1-20261003` | Strict failure: one check tool error after editing already styled source. Outputs were repaired and retained. | Unselected; predates final caption corrections. |
| `arrow-native-plantuml-colorset-renderer-luna1-20261003` | Strict pass. | Superseded after manual review exposed transparent PNG canvas. |
| `arrow-native-slidev-quality-audit-luna1-20261003` | Strict pass. | Superseded after the actual HTML-alpha canvas regression required a producer fix. |
| `arrow-native-mermaid-luna2-20261003` | Strict pass; six exact artifacts. | Selected final payload. |
| `arrow-native-plantuml-colorset-renderer-luna2-20261003` | Strict pass; five exact artifacts, SVG and PNG inspected. | Selected final payload. |
| `arrow-native-slidev-quality-audit-luna2-20261003` | Strict pass; two exact review artifacts and correct three actionable repairs. | Selected final payload. |

Selected payload SHA-256 values:

- Mermaid: `8e350ae361819866a6e2b5bbe65ba2e6bca32f2e19f74daee4ecb0c99ee5a901`.
- PlantUML: `a59c777e8febfc5af45626e5f6eb60068d6957f3ab653d7d7c33148414a2617a`.
- Slidev quality audit: `fa2859228d442f5d68058db0442ef25d68e3160d00e983905cc1550ad45c37ee`.

The versioned prompts are [Mermaid](mermaid-runtime.md), [PlantUML](plantuml-runtime.md), and [quality audit](quality-runtime.md). Final harness commands:

```powershell
uv run --script scripts/run-pi-skill-eval.py mermaid --prompt-file evaluations/arrow-contrast-diagrams/mermaid-runtime.md --mode json --strict --model openai-codex/gpt-5.6-luna --run-id arrow-native-mermaid-luna2-20261003 --expect-output diagram.mmd --expect-output style.json --expect-output check.json --expect-output diagram.static.svg --expect-output diagram.animated.svg --expect-output review.md
uv run --script scripts/run-pi-skill-eval.py plantuml-colorset-renderer --prompt-file evaluations/arrow-contrast-diagrams/plantuml-runtime.md --mode json --strict --model openai-codex/gpt-5.6-luna --run-id arrow-native-plantuml-colorset-renderer-luna2-20261003 --expect-output input/deployment.puml --expect-output renders/svg/deployment.svg --expect-output renders/png/deployment.png --expect-output render-report.json --expect-output review.md
uv run --script scripts/run-pi-skill-eval.py slidev-quality-audit --prompt-file evaluations/arrow-contrast-diagrams/quality-runtime.md --mode json --strict --model openai-codex/gpt-5.6-luna --run-id arrow-native-slidev-quality-audit-luna2-20261003 --expect-output review.md --expect-output repairs.json
```

The explicit summarizer was run successfully for every selected `events.jsonl` with `--require-model gpt-5.6-luna --fail-on-invalid-json --fail-on-tool-error`. All six raw attempt folders remain retained; passed superseded snapshots are not counted as acceptance of the final source.

Geometry support is deliberately bounded. Imported source SVGs, gradients, complex masks/clips/filters, arbitrary transformed marker hierarchies and connector crossings still require actual rendered review and a source layout adjustment when needed. The native producers and marked audit supplement that review; they do not claim universal routing or continuous geometric proof from a finite sample grid.

The subsequent read-only independent ECharts review identified and verified the root agent's finite native override repairs in both palettes. Its [separate report](echarts-overrides-20261003.md) and [22-state before/after ledger](echarts-overrides-20261003.json) preserve actual SSR/client evidence, unchanged native glyphs and show flags, the immutable baseline helper and the final byte-identical helper copies. This did not modify the three native/QA payloads sealed above.
