# Connected-diagram compactness: native renderers

Date: 2026-10-04 (local; retained manifests use UTC on 2026-10-05).
Skills: `mermaid`, `plantuml-colorset-renderer`, `usefulcharts-style`.
Scope: connected conceptual diagrams, lineage and interactions. Quantitative
chart scales and numeric timeline coordinates retain their existing contracts.

## Changes and demonstrated behavior

All three skills now default to the smallest composition supported by readable
type, complete labels, visible semantic heads and independently traceable routes.
Their compact references define a last-passing-render loop, full text/head
envelopes, local grouping and route repairs, actual preview comparisons, and a
stop condition. They reject smaller bounds that introduce collisions, hidden
heads, false shared trunks or ambiguous endpoints. Explicit user geometry wins.
The agent metadata matches this contract.

Mermaid retains its previously validated numeric padding and family spacing.
Independent browser inspection found a real native presentation failure: seven
flow relationship labels inherited white category text against their own white
backings, although source/style/harness checks passed. The native SVG finisher
now chooses label paint against the separate edge-label backing, for HTML and
SVG text, without moving any geometry. New regressions cover flow, state,
class and swimlane labels, dark/white surfaces, explicit SVG backing and
unchanged positions. Final previews show all seven relation captions. Layout
comparisons also remain inside the workspace; a concrete relative comparison
path avoids Git Bash/native-Python disagreement over `/tmp`.

PlantUML keeps its native Padding 6 and avoids a universal smaller rank gap.
Its new compact-layout reference keeps native curves as the first choice for
labeled component graphs: the first trial's forced orthogonal routing placed a
label across incompatible fills. The source was repaired and the failure was
retained. The final cohort preserves complete labels, loop heads and separate
routes; tighter safe native spacing is demonstrated without a blanket theme
override.

UsefulCharts small automatic editorial lineage now derives width from measured
columns, the existing readable title floor and a two-line footer. It removes
the previous 1000-by-720 sparse-layout floor and its artificial rank stretching.
The normal 18-unit body type and 52-unit routing gap remain intact. Explicit
dimensions remain authoritative; numeric timelines follow the existing code
path. The four-record command fixture changes from 1000 × 720 to
604 × 546.98: **54.11% less canvas area**. Chromium measures its four routes
from 1411.98 to 669.94 units: **52.55% less total path length**. Both previews
were opened, and the final browser audit has zero findings/warnings with
minimum text contrast 7.90:1. These are measured gains for this fixture,
not a global packing optimum.

## Isolated runtime evidence

Spark was attempted first for every skill and rejected before the first tool
call: the provider reports that `gpt-5.3-codex-spark` is unsupported with this
ChatGPT account. These are infrastructure failures, not skill passes. The
backlog records an explicit replacement-model exception for
`openai-codex/gpt-5.6-luna`; final runs use medium thinking. Strict gates were
retained: prompt first, valid JSON events, exact non-empty output paths,
observed model, zero tool errors, clean runtime reads and unchanged payload.

| Skill | Final command contract | Final naturalistic cohort | Boundary case |
| --- | --- | --- | --- |
| mermaid | `20261004-compaction-mermaid-contract-luna-2`, pass | `20261004-compaction-mermaid-natural-luna-4`, `-5`, `-6`: 3/3 strict and artifact passes | `20261004-compaction-mermaid-boundary-luna-1`, pass; long labels and explicit padding 18 / nodeSpacing 42 / rankSpacing 90 retained |
| plantuml-colorset-renderer | `20261004-compaction-plantuml-contract-luna-2`, pass | `20261004-compaction-plantuml-natural-luna-3`, `-4`, `-5`: 3/3 strict and artifact passes | Labeled loops and native contrast boundary exercised in the naturalistic graph and deterministic arrow tests |
| usefulcharts-style | `20261004-compaction-usefulcharts-contract-luna-2`, pass | `20261004-compaction-usefulcharts-natural-luna-3`, `-4`, `-5`: 2/3 strict and artifact passes; `-4` fails after unsupported hand-editing of rendered influence geometry | `20261004-compaction-usefulcharts-boundary-luna-1`, pass; long complete names, measured header/footer and all four merger relations |

The final naturalistic cohort meets the repository's two-of-three threshold.
UsefulCharts retains its existing broader `validating` status: this scoped
compaction acceptance does not establish reference-density or visual parity
for its other poster work.

The PlantUML release contract and all three accepted natural runs now have the
same current runtime SHA-256
`eb99915c267e0dc90fe9a01dab20d12d1189107e2e119031db39c905d07e2f2e`.
The earlier passing contract Luna1 is retained as historical evidence: its
only difference is the `agents/openai.yaml` default-prompt sentence requiring
compact connected layouts. Its entry point, references, scripts and assets
are byte-identical. A fresh current-source contract Luna2 closes that narrow
metadata lineage difference without changing source or prompt. It passes
all five exact artifacts, observed Luna, zero invalid events/tool errors and
unchanged payload. Its two prompt commands were independently matched
verbatim in the trace; the harness exact-command option was not set.
Native standalone SVG/PNG inspection at 199×313 finds all three node labels,
both captions and both complete heads readable, with measured target gaps
3.07/3.06px. Namespace-prefixed XML is inspected as a standalone native SVG;
a generic HTML-injection scan that produced no labels is retained as an
inapplicable evaluator attempt and is not used for acceptance.

Reusable prompts are in `evaluations/pi-prompts/diagram-compaction-*.md`.
The compact machine record, including every retained attempt, exact output
inventory, payload digest, model, gate outcome and inspected read paths, is
[renderers-20261004.json](renderers-20261004.json). Raw runs, manifests, sources,
event summaries and previews remain in the ignored matching
`evaluations/runs/<run-id>/` directories. Each `run-manifest.json` and
`command.txt` records its actual isolated invocation.

Representative final invocation:

```powershell
uv run --script scripts/run-pi-skill-eval.py mermaid --prompt-file evaluations/pi-prompts/diagram-compaction-mermaid-naturalistic.md --mode json --strict --model openai-codex/gpt-5.6-luna --thinking medium --run-id 20261004-compaction-mermaid-natural-luna-4 --expect-output diagram/request.mmd --expect-output diagram/request.svg --expect-output diagram/style.json --expect-output diagram/check.json --expect-output diagram/review.md
```

Every final strict passing run was summarized using:

```powershell
uv run --script scripts/summarize-pi-json-events.py evaluations/runs/<run-id>/events.jsonl --output evaluations/runs/<run-id>/read-surface.json --require-model gpt-5.6-luna --fail-on-invalid-json --fail-on-tool-error
```

Read-surface inspection found focused skill entrypoints/references, small
templates where needed, and task artifacts. No runtime acceptance-gallery,
sibling-skill or repository-document reads were required. All final compact
references are below 10 KB. The isolated payload remained unchanged.

## Independent artifact checks

The evaluator opened the final PNG or Chromium SVG screenshot for each accepted
contract, naturalistic and boundary artifact. Mermaid screenshots measured node
and relation-label rectangles, found no label intersections, and showed actual
relation-label paint. Source facts and route multiplicity remain complete
(naturalistic Mermaid: 12 concepts / 15 relations; PlantUML: 10 components /
11 relations; UsefulCharts: 8 institutions / 10 relations). PlantUML render
reports and validators pass with Colorset1. UsefulCharts source-bound browser
audits pass for accepted outputs, including long labels and the measured sparse
fixture. Reviewer judgment covered shortest links, return loops, merger inputs,
the influence head and full-page grouping. Geometry checks alone were not
treated as a visual pass.

Ignored evaluator scripts and measurement files live in
`evaluations/runs/20261004-compaction-renderers-manual/`.

## Deterministic checks

| Command | Result |
| --- | --- |
| `uv run --script skills/mermaid/scripts/test_native_solid.py` | 20 tests pass |
| `uv run --script skills/mermaid/scripts/test_arrow_contrast.py` | 16 tests pass |
| `uv run --script skills/plantuml-colorset-renderer/scripts/test_native_styles.py` | 19 tests pass |
| `uv run --script skills/plantuml-colorset-renderer/scripts/test_arrow_contrast.py` | 25 tests pass |
| `uv run --script skills/usefulcharts-style/scripts/test_editorial.py` | 53 tests pass; sparse bounds, long header/footer, explicit dimensions and numeric time included |
| `uv run --script skills/usefulcharts-style/scripts/test_chart.py` | 27 tests pass, including numeric-time fidelity and narrow corridors |
| `uv run --script skills/usefulcharts-style/scripts/test_lineage_runs.py` | 6 tests pass |
| `uv run --script skills/usefulcharts-style/scripts/test_branching_layout.py` | 10 tests pass |
| `git diff --check -- skills/mermaid skills/plantuml-colorset-renderer skills/usefulcharts-style evaluations/pi-prompts/diagram-compaction-*` | Pass |

No published example source or catalog was changed. Repository validators,
payload checks and local installation synchronization are handled by the root
audit and recorded in its combined report.

## Retained failures and limits

- All three Spark attempts: infrastructure, provider model rejection before
  tool use; exact outputs absent, harness fails correctly.
- Mermaid natural Luna1: strict execution passed but independent visual
  acceptance failed because seven edge labels were invisible. This motivated
  the native label-paint repair. Its old payload is not the release cohort.
- Mermaid natural Luna2/3: agent portability failures using `/tmp` between
  Bash and native Python. The compact comparison recipe was clarified; final
  natural Luna4–6 pass.
- PlantUML natural Luna1: skill/agent layout failure from defaulting to forced
  orthogonal labeled routes, followed by recovery. Natural Luna2: a comparison
  render failed before recovery. Both strict failures are retained; the final
  native-curve cohort passes 3/3.
- UsefulCharts natural Luna2: overlong footer caused two rejected renders on
  the old fixed-width payload before recovery. The measured header/footer
  width is now part of sparse auto-layout.
- UsefulCharts final natural Luna4: agent failure. It hand-edited generated
  influence geometry instead of repairing the supported source contract,
  causing detached-target and arrow-shaft-occluded audit errors. Final outputs
  exist, but this run is not counted as passing.
- UsefulCharts natural trials reused explicitly colored template categories,
  yielding Colorset2 paint for their three categories. This audit does not
  establish a new default-palette reliability claim.
- These tests establish the scoped connected-diagram contract on the tested
  structures. They do not prove globally optimal routing, every native family,
  reference-density parity or equivalence to a large poster reference.
