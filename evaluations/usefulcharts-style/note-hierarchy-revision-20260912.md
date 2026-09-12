# Paragraph hierarchy and illustration ownership

Date: 2026-09-12. Baseline: `5b2d3674c65d3b1594b7747ddfef432b0739d9e7`. Status: **validating**. This is a development refinement, not a blind equivalence test or evidence of visual indistinguishability.

## Comparison and resulting composition

The previous chronology repeated a separate heading/body stack for every note. Its narrow island paragraphs and central green bands weakened the local reading order. An independent image trial also showed a clock above the 1820 schools sharing the preceding 1808 harbor note's date band. Correct coordinates and zero overlaps had not prevented a misleading perceived association.

The selected 1680 × 2300 composition flows 54 ordinary or illustrated notes as compact paragraphs and retains six separate landmark headings. It moves two island continuities 40 units left, widens their narrative groups, and keeps the navigation instrument below its own explanation. The bridge fits above its road caption. It preserves all 50 periods, 55 typed transitions, 60 complete notes, every type size, all seven illustrations and their dimensions. The canvas is 100 units shorter than the published baseline, without changing the numeric year scale's meaning.

Seventeen development explorations are retained: six render successfully and eleven report insufficient layout space. The narrower 1560-unit pages and more aggressive height reductions are rejected. `note-hierarchy-v29e/moderate-page` is the selected source. Its actual SVG and PNG exactly match the canonical fixture; no unreviewed transfer variant was substituted.

Direct equal-width comparison still rejects parity. The original has more varied territorial growth, denser local changes and a broader range of illustration silhouettes and visual weight. The revised page is easier to read locally, but five persistent regional histories and recurring split/merge shapes remain conspicuous. Fewer source records are not a reason to invent filler, and a local typographic improvement is not a professional-equivalence score.

## Reusable skill changes

- Optional `text_layout: paragraph` emits editable mixed SVG text runs: a bold lead-in, regular explanation, preserved font sizes and exact source words. A terminal display period is added unless the source heading already ends in `.?!:`. Source JSON is unchanged by this formatting. `stacked` remains the compatible default.
- Optional `art_position: auto` evaluates four image arrangements against complete text, image, period and bridge geometry. It avoids placing an image over another same-region event's date band, considering earlier and later notes. Explicit positions remain fixed. The packing output resolves `auto` before rendering.
- The independent browser audit verifies source words, run order, font size, weight, visibility, contrast, actual glyph positions and image viewport. It reports `illustration-competing-date` warnings from observed SVG geometry separately from hard failures. This is an ownership-review heuristic, not a proof of reader interpretation.
- A compact [runtime recipe](../../skills/usefulcharts-style/references/note-hierarchy.md) explains hierarchy, exact positioning, the limits of the heuristic and visual repair. It requires explicit left/right placement when the user asks for a picture beside its prose, and repacking after a visual edit changes a group's footprint.

The live pattern remains [`usefulcharts-parallel-history`](https://gvillarroel.github.io/skills/examples/usefulcharts-style/five-regional-histories.html). The compact runtime template demonstrates ordinary paragraphs and a separate landmark. Its four-event preview is a functional starter, not an aesthetic acceptance result.

## Isolated forward evaluation

The naturalistic prompt retains the twelve-period, eighteen-note, three-region development history from the preceding contextual-art revision. It requests running paragraphs, three named landmarks with separate headings, three identified drawings and explicit ownership of the clockmaking illustration. It leaves implementation to the agent. This reused development case is not a fresh holdout.

The scoped `openai-codex/gpt-5.5` exception continues for image-dependent naturalistic trials because Spark cannot inspect the rendered PNG. The default Spark command control verifies exact files, mixed paragraphs, automatic clock placement and preserved explicit image arrangements. Runtime copies exclude examples and remain read-only.

Initial 91-file payload `716e23981ec2eeebd3e915c4d5c485cda54675be45a970e97ba896f599a58028` passes 2/3 strict naturalistic executions plus the Spark control. All four final artifacts pass the independent contracts. Run 1 first rendered and audited correctly, then changed the stagecoach to the requested side position using hand-authored offsets; that edit put prose over a duration stem. Its final correction succeeds, but the strict failure remains. The runtime recipe now requires repacking after this kind of change. A fresh v29b cohort evaluates that guidance, retaining the first cohort in the summary.

The first independent paragraph verifier also misdecoded UTF-8 JSON using the Windows default encoding, falsely flagging the middle-dot year separator in runs 2 and 3. Explicit UTF-8 reads repair the evaluator; original Pi artifacts were not changed. See [the distinct verifier-repair record](note-hierarchy-verifier-repair-20260912.json). Do not conflate that defect with run 1's actual placement failure.

Final 91-file v29b payload `f151828b1fd620283b5334dbb629af9e8bcbb8af9d494bd82869674f433bd2f4` passes 2/3 strict naturalistic executions and the fresh Spark control. Run 2 first failed to place the side-image group, then attempted to read a placement report that had not been created. Its repaired final artifact passes, but both tool errors remain failures. No additional retry was selected to conceal this outcome. All eight final artifact contracts, all six evaluator-owned naturalistic browser reruns, observed models, supported final PNG reads, confined read surfaces and unchanged payload checks pass. Across both cohorts, 6/8 strict executions pass; the two strict failures remain distinct from the repaired evaluator defect.

| Final trial | Image-group result from direct inspection | Remaining visual difference |
| --- | --- | --- |
| `usefulcharts-v29b-notes-1-20260912` | Coach beside its note, clock attached to the schools, separate landmarks. | Coach prose remains narrow; long bands dominate. |
| `usefulcharts-v29b-notes-2-20260912` | Final repaired groups are readable and complete. | Narrow coach paragraph, large quiet intervals and persistent columns. |
| `usefulcharts-v29b-notes-3-20260912` | More comfortable coach prose and clear clock ownership. | Repeated regional structure and limited visual variety persist. |

All evidence and commands remain in [the complete summary](note-hierarchy-summary-20260912.json) and [per-image critiques](note-hierarchy-visual-reviews-20260912.json). Keep the skill **validating**: side-image composition and missing-report recovery still need simplification, and none of these outputs establishes visual parity.

## Validation evidence

- All 146 skill tests pass: 27 classic, 51 editorial, 19 family, 13 context, 25 note placement and 11 timeline geometry. The added coverage protects mixed text, punctuation, escaping, source immutability, automatic arrangements and competing dates.
- All 41 chronology SVG mutations are detected, including eight paragraph corruptions of words, roles, order, font size, emphasis, color, visibility and run position. The checks operate on independently mutated visible SVG.
- The earlier v28b clock example now produces the expected independent warning linking `ec2` to competing date `ec1`. The selected mural has no composition warnings and no geometry findings.
- All three mural browser audits pass. Genealogy and institutional SVGs remain byte-for-byte unchanged from the baseline. The three-card gallery passes desktop/mobile overflow, fit/zoom, embedded-image and browser-error checks.
- The 14 Pi harness tests, skill metadata, pattern IDs, repository structure, bundle independence and payload checks pass. Pages builds 640 files, 42.50 MiB. Local synchronization refreshes 17 changed files while preserving additional local resources.
- Selected SVG SHA-256: `4ef60ed3fb88be1244a829c1e7acce50e816188a46e606c03817dfebb3bcf2b0`. Selected PNG SHA-256: `e4e50f484b47df39e7158584e5a8d3a7161e12b85d7ffd3c6724ffea70bdf63c`. Canonical semantic JSON SHA-256: `16acc43d3a9aac44072d50bc5e2797c27a001e92db32978eb132482c9a6fca12`. These establish reproducibility, not resemblance.

## Reproduction commands

```powershell
uv run --script projects/usefulcharts-style/scripts/compose_note_hierarchy.py --phase e --output projects/usefulcharts-style/artifacts/reviews/note-hierarchy-reproduction
uv run --script skills/usefulcharts-style/assets/examples/usefulcharts-style/build_examples.py --renderer skills/usefulcharts-style/scripts/render_chart.py --only five-regional-histories
uv run --script skills/usefulcharts-style/scripts/test_editorial.py
uv run --script skills/usefulcharts-style/scripts/test_timeline_events.py
uv run --script projects/usefulcharts-style/scripts/compare_timeline_revision.py --before 5b2d3674 --output projects/usefulcharts-style/artifacts/reviews/note-hierarchy-comparison-reproduction
uv run --script projects/usefulcharts-style/scripts/verify_mutations.py --skill skills/usefulcharts-style --svg skills/usefulcharts-style/assets/examples/usefulcharts-style/five-regional-histories.svg --source skills/usefulcharts-style/assets/examples/usefulcharts-style/five-regional-histories.json --artifacts projects/usefulcharts-style/artifacts/reviews/note-hierarchy-mutations-reproduction
uv run --script projects/usefulcharts-style/scripts/verify_gallery.py skills/usefulcharts-style/assets/examples/usefulcharts-style --artifacts projects/usefulcharts-style/artifacts/reviews/note-hierarchy-gallery-reproduction
uv run --script projects/usefulcharts-style/scripts/summarize_note_hierarchy.py
uv run --script scripts/validate-pattern-ids.py
uv run --script scripts/validate-skills.py
uv run --script scripts/test-skill-independence.py
uv run --script scripts/check-repo-payload.py
uv run --script scripts/build-pages.py
uv run --script scripts/sync-local-skills.py
```

Use fresh run IDs to reproduce forward tests, replacing `N` with 1, 2 and 3:

```powershell
uv run --script scripts/run-pi-skill-eval.py usefulcharts-style --prompt-file evaluations/pi-prompts/usefulcharts-note-hierarchy.md --model openai-codex/gpt-5.5 --mode json --strict --run-id usefulcharts-v29b-notes-N-20260912 --timeout-seconds 900 --expect-output result/source.json --expect-output result/poster.svg --expect-output result/poster.html --expect-output result/layout.json --expect-output result/browser.json --expect-output result/poster.png
uv run --script scripts/run-pi-skill-eval.py usefulcharts-style --prompt-file evaluations/pi-prompts/usefulcharts-note-hierarchy-contract.md --mode json --strict --run-id usefulcharts-v29b-contract-spark-20260912 --timeout-seconds 900 --require-exact-command-from-prompt --expect-output draft.json --expect-output deliverables/brief.json --expect-output deliverables/placements.json --expect-output deliverables/poster.svg --expect-output deliverables/layout.json --expect-output deliverables/browser.json --expect-output deliverables/poster.png
uv run --script evaluations/contracts/verify-usefulcharts-note-hierarchy.py evaluations/runs/usefulcharts-v29b-notes-N-20260912 --output evaluations/runs/usefulcharts-v29b-notes-N-20260912/independent-artifact.json
uv run --script scripts/summarize-pi-json-events.py evaluations/runs/usefulcharts-v29b-contract-spark-20260912/events.jsonl --require-model gpt-5.3-codex-spark --fail-on-invalid-json --fail-on-tool-error
```

The author opened the selected full PNG, the equal-width comparison, native-scale trade/navigation details, the compact template preview and every completed naturalistic PNG directly. Private reference artwork and bulky run evidence remain outside Git.

## Verified publication

Implementation `91dab70d212b458f5aa41f9f0ac445a0a9d6dd95` passes [Pages workflow 34692761288](https://github.com/gvillarroel/skills/actions/runs/34692761288). All eleven public gallery/source/poster files match the committed bytes after standard Pages transformations; the main example catalog retains the stable link. The [revised chronology](https://gvillarroel.github.io/skills/examples/usefulcharts-style/five-regional-histories.html) is available at its existing route.

Verification command: `uv run --script projects/usefulcharts-style/scripts/verify_publication.py --commit 91dab70d --workflow 34692761288 --report projects/usefulcharts-style/artifacts/reviews/note-hierarchy-publication-verification.json`.

The published naturalistic prompt removes one trailing space from the request paragraph. The exact tested prompts and their original byte hashes remain in the run manifests; task wording is unchanged. The runtime skill payload is unchanged from the final v29b tests. Publication confirms availability and reproducibility; the skill remains `validating` for the documented reliability and visual gaps.
