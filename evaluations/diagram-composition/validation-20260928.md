# Diagram composition validation — 2026-09-28

## Scope

The new `diagram-composition` bundle plans compact static explanations before
choosing renderers. It supplies conceptual decomposition, visual-family choice,
weighted grid spans, optional specialist handoffs, SVG/icon normalization,
geometry assembly, and rendered review at the requested display size. It
complements `compose-synchronized-svg` rather than replacing its live-state or
navigable-world behavior.

The canonical bundle is `skills/diagram-composition/`. All generated model runs
remain in ignored `evaluations/runs/`; generated examples remain in ignored
`projects/diagram-composition/artifacts/`. No public Pages example was added.

## Local gates and integration evidence

- `uv run --script skills/diagram-composition/scripts/test_composition.py`:
  24 passing deterministic geometry, identity, reference, embedded-vector,
  static-portability, and semantic-contract controls. The final three controls
  prove that layout accepts unbuilt port coordinates, rejects unknown panels,
  and still prevents composition with unresolved endpoints.
- `uv run --script skills/diagram-composition/scripts/test_browser.py`:
  11 passing browser controls, including small text/tspans, text collisions,
  cross-panel connector collisions, mark overflow, intentional viewport clipping,
  CSS normalization, unused renderer animation rules, and active-animation rejection.
- `uv run --script skills/diagram-composition/scripts/test_native_panels.py`:
  ten passing controls, including independent browser execution of all five native
  families at the requested display scale, text-budget rejection, recurrence,
  matrix shape, explicit-only boundary relations, actual nested review enclosures,
  overlapping-group rejection, readable text with bright category swatches, and
  failure-report persistence without publishing invalid panels or replacing inputs.
- `uv run --with pyyaml python C:/Users/villa/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/diagram-composition`:
  pass. The first invocation lacked PyYAML; the declared dependency corrected
  that local validator prerequisite.
- The 14-test isolated-harness regression suite passed before the forward cohorts.
  Final repository validators, independence checks, and payload check also passed
  after the nested-boundary change. Pattern validation covered 1,222 canonical IDs.

The first browser attempt lacked Playwright's currently requested Chromium binary.
The bundle now falls back to installed Chrome/Edge only when that binary is absent.
Subsequent browser controls use the installed Chrome channel successfully.

Real logo integration exported exact GitHub Copilot and Claude SVGs through
`technical-logo-assets`, and `lucide:cloud` through `iconify-icon-search`, retaining
their source/license files. The Claude export exposed embedded vector-image
wrappers; recursive SVG inlining was promoted into the compositor with positive
and negative tests. The final three-panel workspace example has 32 text marks,
minimum 15 displayed pixels at 1280px width, no text/connector collisions, no
overflow or clipped marks, and no external requests. All three chosen identities
were inspected in the actual screenshot.

Mermaid integration uses the versioned source
`projects/diagram-composition/mermaid/review-sequence.mmd`. After styling,
accessibility validation, and static rendering, CSS materialization produced
pixel-identical source/prepared screenshots and identical text geometry/colors.
Two copies composed together retain distinct SVG identities and local definitions.
Mermaid's six intentionally viewport-clipped lifelines are recorded and inspected;
their clipping is preserved and they do not spill into the surrounding page.

Reproduction:

```powershell
uv run --script projects/diagram-composition/scripts/build_demo.py --skill-root skills/diagram-composition --artifacts projects/diagram-composition/artifacts
uv run --script skills/diagram-composition/scripts/audit_diagram.py audit --input projects/diagram-composition/artifacts/svgs/workspace-composition.svg --report projects/diagram-composition/artifacts/reviews/workspace-audit.json --screenshot projects/diagram-composition/artifacts/images/workspace-preview.png --overwrite
uv run --script projects/diagram-composition/scripts/check_mermaid_import.py --skill-root skills/diagram-composition --artifacts projects/diagram-composition/artifacts
```

These project scripts require the already exported SVG inputs. The reusable
runtime instructions and tools are wholly inside the owning skill bundle.

## Isolated model protocol

The default `openai-codex/gpt-5.3-codex-spark` probe was rejected by the provider
before its first tool call: the account did not support that model. This is an
infrastructure failure, not a behavioral pass. `openai-codex/gpt-5.6-luna`, high
effort, is the recorded model exception. The runtime payload excludes acceptance
examples, loads exactly one skill, and is hash-checked as read-only.

Prompts and the independent semantic contract are versioned under
`evaluations/pi-prompts/diagram-composition-*.md` and
`evaluations/contracts/diagram-composition-acceptance.md`. Each strict run requires
the exact plan, SVG, report, audit, screenshot, and review paths, plus `audit.ok`.

```powershell
uv run --script evaluations/contracts/run-diagram-composition-release.py --prefix diagram-composition-20260928-final --workers 3
uv run --script evaluations/contracts/run-diagram-composition-release.py --prefix diagram-composition-20260928-color --workers 3 --transfer-only
uv run --script evaluations/contracts/run-diagram-composition-release.py --prefix diagram-composition-20260928-groups --workers 3 --naturalistic-only
uv run --script evaluations/contracts/run-diagram-composition-release.py --prefix diagram-composition-20260928-layout --workers 3 --boundary-only
uv run --script evaluations/contracts/run-diagram-composition-routing.py --run-id diagram-composition-20260928-routing-2
uv run --script evaluations/contracts/summarize-diagram-composition.py --output evaluations/diagram-composition/release-evidence-20260928.json
```

The runner calls `scripts/run-pi-skill-eval.py` in strict JSON mode for one
contract, three naturalistic, three generalization, and one ambiguity-boundary
case. Every required artifact has `--expect-output`; each run is a fresh workspace.
The summarizer explicitly checks the observed model, valid events and tool errors.
Independent structure/fidelity checks and screenshot reviews are separate gates.

## Retained development findings

- Initial contract/naturalistic runs produced artifacts but failed strict traces
  on ordinary draft-audit findings, overwrite mistakes, and/or failed edits.
  Draft `--inspect` mode now reports `ok: false` without a command error; final
  audit still fails on findings. Regeneration explicitly requires `--overwrite`.
- The first naturalistic output changed the requested display width from 1000px
  to 1200px. Independent validation rejects it despite a passing self-report.
- The first release-candidate contract and naturalistic screenshots revealed
  connectors crossing title/edge-label text. A browser path/text collision check
  and negative control were added. Their old passing static/audit results are
  not treated as final visual passes.
- The following raw-SVG cohort exposed a broader skill difficulty: a model could
  satisfy font/containment checks while crowding icons against labels, drawing
  oversized internal arrowheads, or writing a headline with the wrong actor.
  These outputs are not promoted. The native-panel builder was added for five
  common fallback families, with data-only authoring, display-derived type,
  explicit text budgets, separate icon space, fixed arrowhead size, and computed
  semantic ports. The skill now requires that simpler fallback for supported
  forms when no specialist is available; custom SVG remains for unsupported forms.
- One early portrait run produced a useful artifact but had two failed editing
  calls; it remains a strict failure. Correct artifacts do not erase trace errors.
- The first metadata-routing run selected the intended skills but used the wrong
  output path and null instead of the requested none string. It is retained as an
  agent contract failure. A fresh, clearer exact-path control passed 12/12 choices,
  with zero tool errors and the expected model. This tests descriptions, not native
  app discovery.
- Native fallback naturalistic trials exposed a missing actual review enclosure
  and an invented claim that peers could read build results. These were artifact
  failures even when strict traces passed. The boundary builder now supports
  explicit nested groups; the selection reference distinguishes stated access
  from unknown permissions. Unit/browser controls cover the new enclosures.
- Fresh equipment-domain trials exposed yellow essential text on white. Category
  colors now live in bands and swatches; essential text remains dark. This is a
  visual failure classification, not a provider failure. The earlier novel-transfer
  cohort remains retained and is not the accepted transfer evidence.
- The late ambiguity rerun `native-boundary-2` passed strict and mechanical gates,
  but manual review found a workspace label crowding its icon/card and a legend
  describing dashed marks that were absent. It is not a joint release pass.
- The next two ambiguity runs produced correct native artifacts but failed strict
  traces on two and five text-match editing errors. This recurring authoring
  difficulty led to an explicit parse/update/serialize-or-rewrite JSON procedure.
  The native port example was also corrected to connect the same workspace
  identity across panels, instead of suggesting a workspace-to-source endpoint.
  Neither change alters renderer code. Targeted fresh boundary and naturalistic
  follow-ups exercise these final instruction changes.
- The JSON-boundary follow-up exposed a real stage-order bug: the layout-only CLI
  rejected named endpoints whose source panels had not been built yet. Layout
  now defers missing port coordinates with explicit warnings; it still rejects
  unknown panels, and final composition still requires every port to resolve.
  Three new controls cover that boundary. The JSON instruction now explicitly
  excludes text-match editing of briefs/plans. Three fresh ambiguity repetitions
  exercise the final repair; earlier failures remain retained.
- Two layout-stage repetitions then attempted to read their requested native
  diagnostic report after a rejected build. The builder had only printed the
  error. It now persists `ok: false` diagnostics at the requested safe report
  path, without publishing an invalid plan/SVG. Collision/unwritable paths remain
  stdout-only; a new control proves input preservation and diagnostic persistence.
  This final repair has a separate fresh boundary follow-up.
- The final follow-up passed strict execution and browser review. Its first
  independent check incorrectly required the literal word `unknown`; the figure
  visibly uses `Still unresolved`, `Unspecified`, and `Open = not supplied`.
  The evaluator now accepts those explicit semantic equivalents, without treating
  an unqualified `open` as enough. Six positive and three negative vocabulary
  controls pass. The original failed report remains in
  `diagnostics-boundary-1/independent-check-original.json`; no figure was changed
  to satisfy a hidden word requirement.

## Release evidence by revision

All runs below occurred on 2026-09-28 using `openai-codex/gpt-5.6-luna`, high
effort, in fresh strict runtime workspaces with the six exact output paths. The
compact [machine evidence](release-evidence-20260928.json) includes all completed
development attempts, strict results, observed reads, payload hashes, independent
checks, evaluator browser reports, and recorded manual artifact reviews. Strict
success alone is never labeled artifact success.

| Case / run prefix | Strict | Joint strict + artifact | Review |
| --- | --- | --- | --- |
| Contract / `native-contract-1` | 1/1 | 1/1 | Three distinct forms, exact paths, declared service/library and permissions endpoints, readable labels. |
| Naturalistic / `groups-naturalistic-{1,2,3}` | 3/3 | 2/3 | Runs 1 and 2 preserve all scopes and actual review containment at 1000px. Run 3 connects the shared-workspace identity to the source object; reject that endpoint despite its clean audit. |
| Fresh domain transfer / `color-transfer-{1,2,3}` | 2/3 | 2/3 | Runs 1 and 3 preserve equipment membership, all-return recurrence, category colors, cases, and 15px labels in portrait orientation. Run 2 retains a failing final-audit tool call and is a strict failure. |
| Ambiguity / `groups-boundary-{1,2}` | 0/2 | 0/2 | Correct, independently reviewed native artifacts; two/five failed edit calls make both traces strict failures. |
| Naturalistic instruction follow-up / `json-naturalistic-1` | 1/1 | 1/1 | Final payload preserves all scopes, containment and readability; zero tool errors and a correct native artifact. |
| Ambiguity instruction follow-up / `json-boundary-1` | 0/1 | 0/1 | Correct artifact, but the unbuilt-port layout failure and one failed edit invalidate the strict trace. |
| Ambiguity / `layout-boundary-{1,2,3}` | 1/3 | 1/3 | Run 2 passes. Runs 1/3 read absent diagnostics; manual review also rejects a floating endpoint in 1 and unsupported arrow direction in 3. |
| Diagnostic recovery / `diagnostics-boundary-1` | 1/1 | 1/1 | Final payload, zero tool errors, complete exact outputs, explicit unresolved facts, readable native composition and correct persisted-report recovery. |
| Metadata routing / `routing-2` | Pass | 12/12 choices | Description-only positive and negative controls; not a native app discovery claim. |

The seed-library `native-generalization-{1,2,3}` cohort achieved 2/3 strict
passes with reviewed artifacts. Because the native recipe contains a related
seed example, these are recorded as rehearsals; the equipment-domain transfer
cohort supplies the separate generalization evidence.

Six runtime payloads are deliberately distinguished:

- Native fallback: `cc2db3a66a7ddf0869c9b2bcb6b400c0fc61cf6ef226c343a7865940740f09ce`.
- Readable category colors: `d62443db26727b116ed5956524b7f358f724cd4a4f3ea864f2eec85e27421837`.
- Nested groups: `8877cc59c081a4cd838f4d73f07e00affa331c556cc8dcf13f75c585f1211ad6`.
- JSON/port instructions: `7d8a03dc3e7bc3076cf27d3de57a45f9fef910178d0e30ad6913dece1a43b9cc`.
- Planning-stage repair: `139ae97d9c35b6d1b9354ee8a05ec445ceb6c1bdda159b8b74ec46c295d855b8`.
- Final persisted diagnostics: `11b6fe3be3100fc73c070c5879f333f4ee9e96da13e0c27d21b33d37fdcf4ac1`.

Each has 14 runtime files. The last visible renderer change adds optional boundary groups and
slightly reduces card padding; it does not change taxonomy, matrix color, cycle,
SVG import, or composition behavior. The affected naturalistic case was repeated
three times on that payload. All 41 local tests passed after that change.
The final planning-stage repair leaves final rendering unchanged; all 44 local
tests pass with that repair. Persisted diagnostics adds a final passing control,
bringing the total to 45; the ten-test native family suite passes on the final bundle.
Earlier contract and color-transfer evidence is scoped to its recorded revision,
not misreported as having executed on the final hash.

The final builders also re-rendered four accepted earlier plans into a
separate project-artifact directory. Each complete SVG is byte-identical to the
accepted source output (SHA-256), and all four fresh browser audits pass. This
isolates the late change's effect without modifying or relabeling the original
model trials. The [compact regression record](final-panel-regressions-20260928.json)
contains source-plan/output hashes and measured sizes. Command:

```powershell
uv run --script projects/diagram-composition/scripts/verify_panel_regressions.py --skill-root skills/diagram-composition --runs evaluations/runs --output projects/diagram-composition/artifacts/reviews/final-panels
```

Read-surface review of accepted runs found the prompt, skill entry point, focused
references/template, required bundled scripts, and generated local task outputs.
No acceptance galleries, repository documents, sibling skills, external network,
or mutated skill payload were needed. Normal traces do not read large gallery
sources. The browser audit still needs manual checks for semantic endpoints,
internal glyph/card interactions, and contrast; automatic route generation is
not a complete obstacle-avoidance solver.

The final follow-ups use the unchanged task prompts and their recorded frozen
skill payloads. Preceding editing failures are agent failures, not infrastructure
failures, and remain recorded. The final diagnostic follow-up used:

```powershell
uv run --script scripts/run-pi-skill-eval.py diagram-composition --prompt-file evaluations/pi-prompts/diagram-composition-boundary.md --model openai-codex/gpt-5.6-luna --mode json --strict --run-id diagram-composition-20260928-diagnostics-boundary-1 --timeout-seconds 900 --expect-output out/plan.json --expect-output out/figure.svg --expect-output out/report.json --expect-output out/audit.json --expect-output out/preview.png --expect-output out/review.md --expect-output-json-field 'out/audit.json::ok=true'
```

Release outcome: **done** for the documented compact static composition scope.
Contract, repeated naturalistic/generalization, boundary recovery, routing,
standalone payload, browser review and repository gates are satisfied. This is
not a claim that every attempt succeeds or that mechanical checks establish
semantic correctness. All 45 isolated development attempts are retained; strict
and manual acceptance remain separate. The final 14-file local installation
matches the canonical bundle. No public example publication was requested or added.
