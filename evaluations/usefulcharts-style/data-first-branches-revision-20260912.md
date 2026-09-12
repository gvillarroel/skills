# Data-first branches and painted connections

Date: 2026-09-12. Baseline: `2ea5183bb71e6737a74cbac3554d82ea2a10aca0`.

**The skill now composes a medium institutional history from complete records, and the published institutional mural has thirteen fewer ambiguous painted connections. Visual parity remains unmet.** Keep the skill `validating` and the user's goal active. The new 59- and 70-record compositions are retained as development evidence, not substituted for the public mural.

## Visual decision

The official [Christian Denominations Family Tree](https://usefulcharts.com/products/christian-denominations-family-tree) combines a small ancestral opening with contextual illustrations and quantitative insets, then distributes later histories across many unequal families. Distinctive emblems, differently weighted institutions and local family headings make the dense page readable. These features are visible in the reference; they are not captured by a node-collision test.

The earlier medium-case workflow required guessed relative coordinates. This revision derives a starting arrangement from the records instead. Fifteen attempts remain in [the complete evidence summary](data-first-branches-summary-20260912.json): twelve completed proposals or displays and three routing failures. Ten completed PNGs were inspected directly. The alternating-axis proposal has a retained SVG but no separate PNG review; the full influence search has a completed source and report but no separate rendering. Neither is treated as a visually accepted result.

The 59-record case narrows from the previous 1962 × 2598.2 units to 1530 × 2392.39 while retaining its complete information and typography. Its nine-record common-origin sequence still leaves a conspicuous empty field on both sides. The width reduction improves displayed type at an equal page width, but does not solve that compositional weakness.

The new fictional publishing subject contains 70 individually authored institutions and 97 typed relationships across seven categories. The final arrangement uses 1988 × 2016.885 units, complete notes and eight assigned images. It gives mergers readable local groups and makes much better use of the middle of the page. However, the upper-right area remains empty, the education family forms a long isolated right-hand spine, and several dotted influences cross large areas. A limited illustration vocabulary and repeated node treatment also remain visible. The source was developed before the forward tests; this is disclosed development on a new subject, not a blind validation or holdout.

The existing 141-institution mural receives only a narrower, demonstrably useful correction. Thirteen eight-unit shifts affect twelve authored corridors. All 141 nodes, 171 typed relationships, 133 printed notes, categories, fonts, illustrations and node positions remain unchanged. The independent browser now reports zero unrelated painted-run overlaps, compared with thirteen before repair. Route length changes from approximately 32,045 to 31,960 units; bends remain 488 and proper crossing entries change from 77 to 76. These counts are diagnostics, not a quality score. The persistent large regions and limited illustration variety remain.

The private comparison is `projects/usefulcharts-style/artifacts/reviews/local-stories-v31/comparison/comparison.html`. It includes equal-width reference/baseline/revised views, a larger interactive corridor detail and the new publishing case. Reference artwork stays local. The genealogy and chronology gallery sources are unchanged and retain their previously documented aesthetic gaps.

## Reusable behavior

The new [data-first branch guide](../../skills/usefulcharts-style/references/data-first-branches.md) routes normal medium histories through `compose_branching_history.py`. It measures complete labels and notes, derives active structural stages and their required width, then freezes a fully editable authored source. When all founding years are numeric, ordinal date bands and available vertical slack improve chronology. Partial dates use causal order without inventing a year. Neither mode claims a proportional calendar.

The helper preserves all source facts. Prescribed geometry, unsupported partnerships, fixed insets, cycles, unknown endpoints and incompatible absolute routes fail explicitly instead of being silently reinterpreted. Authored or packed routes remain available for a deliberate composition. The helper considers local side attachments for influence edges before widening the search, avoiding the failed strategy of forcing every influence through structural top and bottom ports.

The router now reserves a four-unit centerline clearance against unrelated existing straight runs. The independent SVG audit also uses painted stroke width. An early publishing prototype had a centerline difference of about 0.02217 units that rounded to about 0.02 in the rendered SVG; the old exact-collinearity check could miss the visibly merged strokes. The new audit detects that case and near-parallel painted overlap, including with falsified saved route metadata. It still permits perpendicular crossings and legitimate shared endpoints.

This is a straight-segment diagnostic for the generated institutional poster coordinate space. It does not comprehensively grade curves, semantic meaning or arbitrary transformed stroke widths. The local eight-unit corridor-repair script remains project-specific; the reusable guide explains the observed problem without making this greedy repair a universal layout strategy.

Three failed prototypes are preserved: stricter run reservation first fails to route `review-to-pictures`, and ten- and eighteen-unit future-port reservations fail at the same relationship. Those experimental reservations were reverted. The later full influence search completed successfully; a guarded attempt to stop it found no matching running process, so it is not classified as cancelled. Local-first composition then completed and became the frozen runtime route.

## Frozen forward evidence

The runtime has 97 files and SHA-256 `d49bf99fe163dc1e69fb15381b6e85157bb9ee2e6ac01cf9faceb227e3aaf23c`. A fresh runtime-profile copy matches every tested payload. All trials exclude acceptance fixtures, ambient context and sibling skills and keep the copied bundle unchanged.

| Trial | Model | Strict execution | Independent final contract |
| --- | --- | --- | --- |
| `usefulcharts-v31-publishing-1-20260912` | GPT-5.5 | Pass | Pass |
| `usefulcharts-v31-publishing-2-20260912` | GPT-5.5 | Pass | Pass |
| `usefulcharts-v31-publishing-3-20260912` | GPT-5.5 | Pass | Pass |
| `usefulcharts-v31-contract-spark-20260912` | GPT-5.3-Codex-Spark | Pass | Pass |

The existing scoped GPT-5.5 exception applies to image-dependent naturalistic work; Spark remains the default exact-command control. All four trials have valid events, expected models, zero tool errors, exact requested outputs, confined reads and unchanged payloads. All four evaluator browser reruns pass. Naturalistic contracts preserve every supplied institution, date, note, color, relationship, image identity and emphasis assignment. The stricter title contract was added after the cohort and rerun successfully against each captured original prompt.

The three naturalistic PNGs are byte-identical: SHA-256 `76ca265f853590517c10b4a01027ab8f24dbaf6164b737a98c2e5493a321c5c2`. Every evaluated agent opened its own final PNG. The author directly inspected one shared image after checking all three hashes, rather than treating these as three different design outcomes. This proves reproducibility of the layout but does not establish aesthetic equivalence.

Normal runtime reads cover only the copied `SKILL.md`, its focused data-first guide and requested task inputs or output reports/images. No implementation source, gallery, repository document or sibling skill is needed. All three agents removed their temporary builder and data-first draft despite the guide recommending their retention. The complete authored source and captured input survive. This is a workflow limitation; it does not erase the successful exact-output or integrity checks.

### Disclosed fixture corrections

Early natural, dated and ordered prototypes called one institution **Railway News Service**. Before Pi, the author changed that fictional name to **Roadside News Service** to match its supplied coach illustration. The early source records were reconstructed from the captured prompt with the original name, and all three reconstructions match the data SHA-256 stored by their original render. Those recovered files identify their later reconstruction; they do not imply preservation of every intermediate algorithm version.

After the cohort, the author noticed that the supplied title **Five Centuries of Northbridge Publishing** understated the span from 1428 to 2024. The current generator, reusable prompt and final author display say **Six Centuries**. Raw Pi prompts, outputs and reviews retain their original supplied title. The corrected display differs only in the top-level title; every node, edge and placement is identical. It was rerendered, audited and directly inspected. This is an author content correction, not another agent repetition or a change to the frozen skill.

## Verification and reproduction

All 158 skill tests pass: 27 classic, 51 editorial, 19 family-baseline, 13 context, 25 timeline-event, 11 timeline-geometry, six lineage-run and six new branching tests. The new tests exercise complete-source preservation, unknown dates, measured long captions, invalid prescribed geometry and structural failures. Fourteen Pi harness tests also pass.

All eight independent browser controls and thirteen institutional SVG mutations pass. The three canonical mural audits have no hard findings or composition warnings. The responsive gallery retains its three stable IDs at 1440 and 390 pixels without overflow; fit, zoom, native width and all embedded images pass. Repository metadata, pattern IDs, structure, independence and payload gates pass. Pages generation and local synchronization are part of the publication verification below.

The main deterministic commands are:

```powershell
uv run --script projects/usefulcharts-style/scripts/prepare_publishing_case.py
uv run --script skills/usefulcharts-style/scripts/compose_branching_history.py projects/usefulcharts-style/artifacts/reviews/local-stories-v31/publishing-input.json --output projects/usefulcharts-style/artifacts/reviews/publishing-reproduction/source.json --report projects/usefulcharts-style/artifacts/reviews/publishing-reproduction/composition.json
uv run --script skills/usefulcharts-style/scripts/render_chart.py projects/usefulcharts-style/artifacts/reviews/publishing-reproduction/source.json --svg projects/usefulcharts-style/artifacts/reviews/publishing-reproduction/poster.svg --html projects/usefulcharts-style/artifacts/reviews/publishing-reproduction/poster.html --report projects/usefulcharts-style/artifacts/reviews/publishing-reproduction/layout.json
uv run --script skills/usefulcharts-style/scripts/audit_chart.py projects/usefulcharts-style/artifacts/reviews/publishing-reproduction/poster.svg --source projects/usefulcharts-style/artifacts/reviews/publishing-reproduction/source.json --report projects/usefulcharts-style/artifacts/reviews/publishing-reproduction/browser.json --png projects/usefulcharts-style/artifacts/reviews/publishing-reproduction/poster.png
uv run --script skills/usefulcharts-style/scripts/test_branching_layout.py
uv run --script skills/usefulcharts-style/scripts/test_lineage_runs.py
uv run --script projects/usefulcharts-style/scripts/verify_shared_runs.py --output projects/usefulcharts-style/artifacts/reviews/paint-controls-reproduction
uv run --script projects/usefulcharts-style/scripts/compare_data_first_branches.py
uv run --script projects/usefulcharts-style/scripts/summarize_data_first_branches.py
uv run --script scripts/build-pages.py
uv run --script scripts/sync-local-skills.py
uv run --script scripts/validate-pattern-ids.py
uv run --script scripts/validate-skills.py
uv run --script scripts/test-skill-independence.py
uv run --script scripts/check-repo-payload.py
```

The current prompt uses the corrected Six title. To reproduce the historical cohort exactly, use its captured `evaluations/runs/<run-id>/prompt.md`. Use fresh IDs for further evaluations; substitute 1, 2 and 3 for `N`:

```powershell
uv run --script scripts/run-pi-skill-eval.py usefulcharts-style --prompt-file evaluations/pi-prompts/usefulcharts-data-first-publishing.md --model openai-codex/gpt-5.5 --mode json --strict --run-id usefulcharts-v31-publishing-N-20260912 --timeout-seconds 900 --expect-output result/source.json --expect-output result/poster.svg --expect-output result/poster.html --expect-output result/layout.json --expect-output result/browser.json --expect-output result/poster.png --expect-output result/review.md
uv run --script evaluations/contracts/verify-usefulcharts-data-first-publishing.py evaluations/runs/usefulcharts-v31-publishing-N-20260912 --output evaluations/runs/usefulcharts-v31-publishing-N-20260912/independent-artifact.json
uv run --script skills/usefulcharts-style/scripts/audit_chart.py evaluations/runs/usefulcharts-v31-publishing-N-20260912/workspace/result/poster.svg --source evaluations/runs/usefulcharts-v31-publishing-N-20260912/workspace/result/source.json --report evaluations/runs/usefulcharts-v31-publishing-N-20260912/independent-browser.json
uv run --script scripts/summarize-pi-json-events.py evaluations/runs/usefulcharts-v31-publishing-N-20260912/events.jsonl --require-model gpt-5.5 --fail-on-invalid-json --fail-on-tool-error
uv run --script scripts/run-pi-skill-eval.py usefulcharts-style --prompt-file evaluations/pi-prompts/usefulcharts-data-first-contract.md --mode json --strict --run-id usefulcharts-v31-contract-spark-20260912 --timeout-seconds 900 --require-exact-command-from-prompt --expect-output draft.json --expect-output result/source.json --expect-output result/composition.json --expect-output result/poster.svg --expect-output result/poster.html --expect-output result/layout.json --expect-output result/browser.json --expect-output result/poster.png
uv run --script scripts/summarize-pi-json-events.py evaluations/runs/usefulcharts-v31-contract-spark-20260912/events.jsonl --require-model gpt-5.3-codex-spark --fail-on-invalid-json --fail-on-tool-error
```

The next aesthetic pass should address purposeful use of the opening whitespace, varied illustration identity and the long separated education family, while preserving the supplied information. Another clean geometry report alone cannot satisfy the requested standard.
