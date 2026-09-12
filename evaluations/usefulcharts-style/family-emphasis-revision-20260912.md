# UsefulCharts-style: focal people and the opening family fan

The v24 candidate improves the visibility of the existing significant people and opens the first family branches without changing the source. It is a useful revision to the dense genealogy, but the output is still distinguishable from UsefulCharts. Keep the skill and the full quality-and-composition objective in `validating`.

The comparison baseline is immutable commit `b910a022ad0218ba00dd96b1d8f4e15678df2077`, the published v23 context-landmark revision. The final v24 runtime contains 80 files and has SHA-256 `eacada1f8275db839a2c3f6ae4da60af9366b14fe3ebd4c6be18cdccc1d47067`. All four forward tests use that same frozen runtime. The [machine-readable summary](family-emphasis-summary-20260912.json) retains every attempt and the final source and browser checks. Earlier revision summaries remain unchanged.

## What changed and why

The dense Aurelian source still contains all 561 people, 261 partnerships, 323 relationships, 41 generations and 19 annotations. All nonvisual person fields, original image identifiers, relationships, categories and annotation node/field bindings match v23. No new people, portraits, titles or historical claims were invented to increase visual density.

The 17 previously illustrated founders and landmark rulers now have larger name-and-image groups. The root changes from 13.5-unit type and a 36-unit portrait to 15.5 and 52; the other selected records change from 11.8 and 33 to 13.3 and 46. Ordinary principal names remain 11.8, with 9.1-unit dates; plain consorts retain their prior scale. The canvas grows proportionally from 1800 × 2700 to 1890 × 2835. At an unchanged display or print width, ordinary names therefore become approximately 4.8% smaller. That is a visible tradeoff, not free room.

The new optional `cohort_spread` expands complete family units after ordinary parent/child relaxation. The first six rows use factors tapering from 1.35 to approximately 1.058. Each row is limited by its existing printable bounds; partnership ordering and internal gaps survive. Later rows retain their unexpanded preferences. Invalid row keys, nonfinite values, booleans and factors outside 1–2 are rejected.

Enlarging these groups consumed some previous realm-caption pockets. All seven realm captions remain bound to their original person and field. The Alder caption uses narrower stacked artwork; the Falken caption also narrows. The remaining captions retain a compact beside-art arrangement. No caption was dropped to obtain a geometry pass.

Reusable instructions are in [focal people](../../skills/usefulcharts-style/references/focal-people.md), linked from `SKILL.md`, cohort composition, local baselines and the published genealogy pattern recipe. This is a self-contained runtime route, not knowledge available only in the example builder.

## The connector defect and rejected alternatives

The larger groups exposed a router defect. A legal 18-unit gap had room for a connection with the existing seven-unit obstacle clearance, but the old visibility grid only sampled coordinates fourteen units outside obstacle boundaries. It never discovered the remaining clear corridor. A reduced four-obstacle case preserves the failed parental attachment and proves that an eight-unit candidate grid can find a short path while retaining all seven units of clearance.

The final router tries all existing broad search regions first. Only after those searches fail does it try the closer coordinates. An earlier unconditional close-grid attempt changed successful institutional routes and increased their counted crossings from 63 to 64; it was rejected. The final institutional and timeline SVGs match v23 after line-ending normalization. Genealogy crossings change from 22 to 17, institutional crossings remain 63, and timeline crossings remain zero. These counts describe this renderer's geometry, not aesthetic equivalence.

Sixteen exploratory compositions are retained in the summary: fourteen fail, and two complete candidates pass. Five fail vertical capacity, five fail the old connector search, and four cannot place a required realm caption. The accepted candidates use 40-unit portraits on a 2% larger canvas and 46-unit portraits on a 5% larger canvas. Direct comparison selects the latter for stronger focal hierarchy. These experiments used an evolving project driver and router; their results are retained without presenting them as digest-frozen independent trials. Partial `composition-stage` files omit the seven required realm captions and never count as final passes.

The reduced corridor evidence lives locally at `projects/usefulcharts-style/artifacts/reviews/family-emphasis-v24/founders-44/corridor-investigation.json`. The final narrow-corridor regression verifies endpoints, the original clearance and a route shorter than 180 units. Placement regressions verify source preservation, complete-family expansion, page bounds and invalid inputs.

## Visual critique

This is an unblinded author review of the final PNGs and browser detail captures, not a human discrimination study or an independent aesthetic score. The local comparison displays the official reference, v23 and v24 at identical widths, preserving aspect ratios. It is available at `projects/usefulcharts-style/artifacts/reviews/family-emphasis-comparison/index.html`; official preview artwork stays outside the public gallery.

The final genealogy makes Aurelian, the early founders and the later illustrated rulers easier to locate. Portraits remain visible beside editable names, dates remain subordinate, and the wider early fan reduces the top's pinched appearance. Reading-scale inspection of the middle families shows clear partner links and no new clipping or covered names. The source-bound territorial captions remain readable.

The [European royal reference](https://usefulcharts.com/products/european-royal-family-tree) still has a more varied rhythm of compact name groups, significant figures, local heraldry and explanatory context. Our mural has many similar one-line principal panels and long sequences of similarly shaped family units. The larger portraits improve selected locations but do not remove that overall regularity. The lower cross-family routes remain conspicuous. The Everen realm caption and its adjacent court capsule still compete as a small pair of headings. Changing source facts or adding arbitrary portrait records would not be an acceptable remedy.

The other two families remain part of the target. Direct comparison of the unchanged [institutional study](https://gvillarroel.github.io/skills/examples/usefulcharts-style/atlas-of-inquiry.html) and [chronology](https://gvillarroel.github.io/skills/examples/usefulcharts-style/five-regional-histories.html) preserves the earlier findings: institutional districts still persist too regularly, some long influence connections need stronger local composition, and the chronology has regular streams with limited illustration variety. These are unresolved requirements, not exclusions from the task.

## Isolated forward evidence

The naturalistic prompt uses the complete 48-person Silver Vale family, including 21 unions, 36 relationships, all 95 known numeric dates, Xavier's unknown birth and three required field-bound place captions. It additionally requests exactly three decorative museum portraits for Ada, Elin and Klara. This is development reuse of a known family with a new emphasis requirement, not a sealed holdout. It cannot replace the three dense poster families as the acceptance target.

The existing GPT-5.5 model exception is retained for image-dependent tests because Spark cannot inspect PNG input. The separate command contract uses the default Spark model and makes no aesthetic claim.

| Run | Strict execution | Independent artifact | Direct visual review |
| --- | --- | --- | --- |
| v24 family, GPT-5.5 1 | Pass | Pass | Three clear focal groups and correct captions; long middle routes and dark principal fills remain. |
| v24 family, GPT-5.5 2 | Pass | Pass | Clear focal hierarchy and local captions; broad connector shelves and some winding lower links remain. |
| v24 family, GPT-5.5 3 | Fail | Pass | The final page is readable, but its footer exposes internal union ID `u16`; long links and regular nameplates remain. |
| v24 emphasis command contract, Spark | Pass | Pass | Exact seven outputs and source-backed geometry; command control only. |

All three naturalistic runs read the focused new guide, preserve the complete facts, use exactly the three requested portrait owners and inspect the final PNG through a supported image result. Focal names are visibly larger than the 18-unit ordinary median: 19–21, 20 and 21–23 units respectively. Portrait widths are 46–54 units. All copied skill payloads remain unchanged, and no run reads acceptance examples, repository documents or sibling skills.

Run 3 has one recorded tool error in an auxiliary post-render file check: an incorrectly escaped Python backslash causes an unterminated string. Classify this as `agent`; the final artifact passes but the strict run remains failed. Two of three naturalistic strict runs pass, meeting the repository's repetition threshold. Do not relabel the failed execution or replace it with an unrecorded retry. All three pages are accepted as compact development artifacts with the stated residual differences. Their dark fills and white principal labels also show that palette choices can drift from the lighter dense-reference treatment.

## Validation and reproduction

All 110 renderer/placement tests pass: 27 classic, 43 editorial, 18 family baselines, 9 timeline notes and 13 context tests. All 42 deliberate SVG mutations are detected: 19 genealogy, 9 institutional and 14 chronology. All three source-backed browser audits pass, as do responsive gallery, fit/zoom and embedded-image checks. The viewer's 100% width now follows its source canvas rather than assuming 1800 units. The genealogy's final source-file SHA-256 is `ff07689ac54f41a50f0ed71c444df136634ec5e089f620e13637dd9f88cd1e85`.

```powershell
uv run --script skills/usefulcharts-style/scripts/test_chart.py
uv run --script skills/usefulcharts-style/scripts/test_editorial.py
uv run --script skills/usefulcharts-style/scripts/test_family_baselines.py
uv run --script skills/usefulcharts-style/scripts/test_timeline_events.py
uv run --script skills/usefulcharts-style/scripts/test_context_landmarks.py
uv run --script skills/usefulcharts-style/assets/examples/usefulcharts-style/build_examples.py --renderer skills/usefulcharts-style/scripts/render_chart.py
uv run --script projects/usefulcharts-style/scripts/verify_genealogy_revision.py --before b910a022 --output projects/usefulcharts-style/artifacts/reviews/emphasis-final-facts.json
uv run --script projects/usefulcharts-style/scripts/verify_gallery.py skills/usefulcharts-style/assets/examples/usefulcharts-style --artifacts projects/usefulcharts-style/artifacts/reviews/emphasis-final-gallery
uv run --script projects/usefulcharts-style/scripts/compare_posters.py --repository . --before-revision b910a022 --artifacts projects/usefulcharts-style/artifacts --after-prefix emphasis-final --comparison-name family-emphasis-comparison --before-label "Previous context-landmark revision"
uv run --script projects/usefulcharts-style/scripts/summarize_emphasis_revision.py
```

For each canonical ID (`aurelian-families`, `atlas-of-inquiry`, `five-regional-histories`):

```powershell
uv run --script skills/usefulcharts-style/scripts/audit_chart.py skills/usefulcharts-style/assets/examples/usefulcharts-style/<id>.svg --source skills/usefulcharts-style/assets/examples/usefulcharts-style/<id>.json --report projects/usefulcharts-style/artifacts/reviews/emphasis-final-<id>-browser.json --png projects/usefulcharts-style/artifacts/images/emphasis-final-<id>.png
uv run --script projects/usefulcharts-style/scripts/verify_mutations.py --skill skills/usefulcharts-style --svg skills/usefulcharts-style/assets/examples/usefulcharts-style/<id>.svg --source skills/usefulcharts-style/assets/examples/usefulcharts-style/<id>.json --artifacts projects/usefulcharts-style/artifacts/reviews/emphasis-final-mutations/<id>
```

Use a new workspace/run ID for each repetition; keep the recorded workspaces unchanged:

```powershell
uv run --script scripts/run-pi-skill-eval.py usefulcharts-style --prompt-file evaluations/pi-prompts/usefulcharts-family-emphasis.md --model openai-codex/gpt-5.5 --mode json --strict --run-id <fresh-family-id> --expect-output result/source.json --expect-output result/poster.svg --expect-output result/poster.html --expect-output result/layout.json --expect-output result/browser.json --expect-output result/poster.png --expect-output-json-field result/layout.json::status=pass --expect-output-json-field result/browser.json::status=pass
uv run --script scripts/run-pi-skill-eval.py usefulcharts-style --prompt-file evaluations/pi-prompts/usefulcharts-emphasis-contract.md --mode json --strict --require-exact-command-from-prompt --run-id <fresh-contract-id> --expect-output draft.json --expect-output result/source.json --expect-output result/placement.json --expect-output result/poster.svg --expect-output result/layout.json --expect-output result/browser.json --expect-output result/poster.png --expect-output-json-field result/layout.json::status=pass --expect-output-json-field result/browser.json::status=pass
uv run --script evaluations/contracts/verify-usefulcharts-family-emphasis.py evaluations/runs/<fresh-family-id> --output evaluations/runs/<fresh-family-id>/independent-artifact.json
uv run --script scripts/summarize-pi-json-events.py evaluations/runs/<fresh-family-id>/events.jsonl --require-model gpt-5.5 --fail-on-invalid-json --fail-on-tool-error
```

Pattern IDs, repository structure, skill independence, payload, the 14 Pi-harness tests and quick skill validation pass. The local Pages build passes with 639 files / 41.83 MiB. Local installation synchronization copies the 14 changed skill files and preserves other local files. The Pages workflow also passes its diagram coverage, generated-output boundary and unified Pages checks.

## Delivery state

Implementation `e8ed87e0ccdc150152fe808e55776b54fcf10eec` is committed and published on `main`. [Pages workflow 34682038023](https://github.com/gvillarroel/skills/actions/runs/34682038023) completed successfully. Independent HTTP verification compared all eleven gallery, manifest and poster files to their complete expected committed bytes after standard Pages metadata and whitespace transformations; all match. The main examples catalog still links the gallery. Local evidence: `projects/usefulcharts-style/artifacts/reviews/family-emphasis-publication-verification.json`.

The revised [Aurelian genealogy](https://gvillarroel.github.io/skills/examples/usefulcharts-style/aurelian-families.html) is available at its unchanged route with the complete SVG and editable source. The [three-poster gallery](https://gvillarroel.github.io/skills/examples/usefulcharts-style/) preserves the institutional and chronology examples. Publication completes delivery of this revision, not the full quality-and-composition objective; visual parity remains unproven.
