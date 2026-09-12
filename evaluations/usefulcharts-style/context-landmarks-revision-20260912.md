# Source-bound editorial landmarks

Date: 2026-09-12. Skill: `usefulcharts-style`. Status: `validating`.

The objective remains indistinguishable visual quality and composition compared with the relevant UsefulCharts posters. This revision improves the intermediate layer between family names and individual records and makes required context part of initial family composition. It does not establish parity, close the earlier institutional-routing or timeline-composition findings, or replace the dense target with a smaller passing family.

The principal comparison is the official [European Royal Family Tree](https://usefulcharts.com/products/european-royal-family-tree). The [Christian Denominations Family Tree](https://usefulcharts.com/products/christian-denominations-family-tree) and [Timeline of World History](https://usefulcharts.com/products/timeline-of-world-history) remain the other two visual targets. The prior source analysis and critique records remain authoritative for their unresolved findings.

## Visual changes and retained evidence

The 561-person genealogy retains every person, date, title, role, house, source order, partnership and relationship from `caa49bf`. Its 261 partnerships and 323 relationships retain their geometry. The twelve existing family/court/heading annotations are preserved. Seven territorial captions now expose existing `realm` fields; each carries an original fictional device in its declared category color. The source note adds only the disclosure that the devices are fictional. No historical events, relatives or relationships were added.

The first prototype passed geometry but failed visual association. Independent inspection found Falken apparently attached to the nearby green Baldwin II; Everen appeared closer to green figures; Corven and Daleshire sat among competing branches. The bottom Rosene caption also read like a terminal footnote. These failures remain in the v20 PNG and the saved source/SVG/placement snapshot under `projects/usefulcharts-style/artifacts/reviews/landmarks-v20-development/`.

The category-affinity revision relocates the captions to nearby same-color families, moves Rosene into the middle-right branch, and tightens the actual emblem-caption group within its reserved envelope. The independent v20 and v21 reviews are separate files in the local reviews directory. The final comparison includes all three original references, the previous revision and the final examples at equal display width; it is an unblinded author review, not an indistinguishability experiment. Reference artwork remains private local evidence.

Early attempts using eleven additional captions could not fit the four court captions without invading the existing composition. The four original court annotations remain visible and unchanged. Only the optional duplicate court treatment was rejected. Two stacked/wide realm trials also failed local placement. The prototype records rejected candidate anchors; they are not passing aesthetic examples. The resulting seven territorial captions add orientation, but their uniform format, limited explanation of transitions, and the existing long routes still distinguish the composition from the reference.

## Reusable behavior

`kind: landmark` binds a visible serif caption to a known node and textual `field`. A supplied replacement label must match exactly; category reassignment, unknown anchors, numeric fields and unreadable formats are rejected. Optional artwork can sit above or beside the text. The seven `heraldry` variants are original fictional devices, explicitly described as diagram identifiers, not historical coats of arms.

The standalone `place_context_landmarks.py` helper measures a rendered base with Chromium, including actual text and artwork, existing annotations, rounded relationships and partnership bars. It reserves the complete envelope and changes only annotation offsets. Its bounded search now checks competing-category proximity as well as geometric clearance. A missing pocket fails without deleting required context or altering data. The compact reference explains composing additional local room and selecting an alternative record only for an optional repeated orientation label.

The v21 naturalistic trials exposed a workflow flaw: required captions were added to an already packed family, where bounded pocket search repeatedly failed or placed the right text near the wrong person. V22 adds `space_family_branches.py --reserve-context`. It measures all required captions before initial placement, reserves each complete envelope above its owner, restores fitted nameplate widths, includes the envelope in local baseline constraints and routes around it. The new-family route renders this result directly. Bounded pocket search remains the refinement route for an existing authored graph. All three v22 families produced the required captions without the earlier layout failures.

Two v22 runs then exposed a separate source-schema failure: they temporarily removed `birth: "unknown"` to run placement and restored that string in the final source. The printed birth remained explicitly unknown; no numeric birth was invented. V23 makes the representation explicit at the entry point and both genealogy references: known years are JSON numbers, unknown numeric fields are missing or `null`, and source wording stays in `detail` or a separate record field. This changes guidance, not the numeric acceptance rule or renderer geometry.

The browser audit independently checks exact visible source text, binding, position, heraldic color, envelope containment and collisions with nodes, annotations and full paths. Nine new visible mutations are detected. These semantic and geometric checks support correctness; they are not a visual resemblance score.

## Forward evaluation

Each runtime contains 79 files. The GPT-5.5 exception remains scoped to image-dependent cases; Spark still validates the exact command interfaces.

| Runtime | SHA-256 | Change |
| --- | --- | --- |
| v21 | `acce640a75cf4ca283cc58b1bad5e4fa527cbb5343c4d21a926f9e5bc28366a3` | Source-bound captions and bounded category-aware pocket placement. |
| v22 | `00de5845846b515c3e46eb8c911e874c090882c8d03f4bda8d217440ee93d774` | Reserve required context before family placement and route around its complete envelope. |
| v23, final | `4f2870dcf06dd5ff14a9e7ab0cab1611f435b7c594d34c1e48398f4299f6813c` | Explicit numeric-or-missing source dates through the final authored output. |

The naturalistic cohort retains the complete Silver Vale case: 48 people, 21 partnerships, 36 relationships, 95 known numeric dates, one unknown birth, four declared houses and three required local place captions. The prompt requires larger serif captions, original symbols, exact source binding and clear branch ownership. It does not expose the acceptance fixture or the revised dense composition. The same prompt hash, `ea4f708630c5622902d11722b62c326c4da125996beeaa21c1776809ab340d65`, is used for all nine family attempts. This is a development cohort with repeated feedback, not a sealed holdout.

All fourteen attempts are retained in [the machine-readable evidence](context-landmarks-summary-20260912.json), including tool errors, read surfaces, unchanged payload checks, exact outputs, independent artifact checks and direct image judgments.

| Attempt | Strict execution | Independent artifact | Interpretation |
| --- | --- | --- | --- |
| v21 pocket contract, Spark 1 | Pass | Pass | Exact authored-graph helper interface. |
| v21 family, GPT-5.5 1 | Fail | Pass after repair | Ten tool errors; broad final composition still has dominant crossing corridors. |
| v21 family, GPT-5.5 2 | Timeout | Fail | Forty-eight death years are quoted strings, with unchanged numeric values. The school caption is also visibly too far from Klara. |
| v21 family, GPT-5.5 3 | Timeout | Fail | Required final artifact set is missing; fourteen recorded tool errors. |
| v22 pocket contract, Spark 1 | Fail | Pass after repair | Handwritten JSON was malformed; subsequent missing-output and failed-edit errors remain failures. |
| v22 reservation contract, Spark 1 | Pass | Pass | Exact pre-layout context reservation interface. |
| v22 family, GPT-5.5 1 | Fail | Fail | One initial nonnumeric-date error; final unknown-birth string violates the source schema. Captions and geometry pass. |
| v22 family, GPT-5.5 2 | Pass | Pass | Complete facts, captions, PNG inspection and clean runtime use. |
| v22 family, GPT-5.5 3 | Fail | Fail | Same unknown-birth representation failure; no birth year was invented. Captions and geometry pass. |
| v23 family, GPT-5.5 1–3 | Pass, 3/3 | Pass, 3/3 | Complete 48/21/36 inventory, all 95 numeric known dates, unknown birth preserved, all three captions; supported PNG inspection and confined reads. |
| v23 pocket and reservation contracts, Spark | Pass, 2/2 | Pass, 2/2 | Both exact command routes on the final frozen runtime. |

The final v23 payload passes all five strict attempts with zero tool errors and an unchanged runtime bundle. Across the complete v21–v23 development history, eight of fourteen strict attempts pass. The six failures remain failures even where the final repaired artifact passes the independent checker.

The supplemental date diagnosis distinguishes type violations from altered historical values without changing prior verdicts. The Windows wrappers for the two v21 timeouts retained child Pi processes after their recorded 900-second deadline. Cleanup inspected each exact workspace, executable and process creation time and terminated only those expired evaluation processes and their owned descendants. Their native timeout results, errors and `expired-process-review.json` evidence remain recorded; they are not counted as successful retries or excused as quota failures.

Direct inspection accepts the three v23 outputs as compact development examples, not as proof of indistinguishability. Every required caption has clear local ownership and readable serif type. The long cross-family routes, similarly sized principal nameplates and wide opening fan still make these pages more schematic than the reference. The first v23 footer also exposes internal person IDs, a small editorial weakness retained in its critique rather than corrected by the evaluator.

For the dense mural, [the independent visual critique](context-landmarks-independent-critique-20260912.md) recommends replacing v19 with the final candidate: realm ownership and tighter symbol-caption grouping improve orientation. The remaining priorities are stronger emphasis around significant source records, a broader early distribution of the existing branches, and a clearer distinction between the adjacent Everen realm and court headings. A clean geometry audit does not override these visible differences.

## Validation and reproduction

Local validation passes 107 tests: 26 classic, 43 editorial, 16 family baselines, 9 timeline notes and 13 context tests. All 42 visible mutations are detected across the three canonical posters: 19 genealogy, 9 institutions and 14 chronology. All three source-backed browser audits pass; desktop/mobile gallery, fit, zoom and embedded images pass. The genealogy fact comparison passes with seven additional source-bound landmarks and no changed original annotation facts. Its source file SHA-256 is `67a4469caa01aad62490f6356c03e7afac4a02f98702ffe392db32ca89584d30`.

```powershell
uv run --script skills/usefulcharts-style/scripts/test_context_landmarks.py
uv run --script skills/usefulcharts-style/scripts/test_chart.py
uv run --script skills/usefulcharts-style/scripts/test_editorial.py
uv run --script skills/usefulcharts-style/scripts/test_family_baselines.py
uv run --script skills/usefulcharts-style/scripts/test_timeline_events.py
uv run --script skills/usefulcharts-style/assets/examples/usefulcharts-style/build_examples.py --renderer skills/usefulcharts-style/scripts/render_chart.py
uv run --script projects/usefulcharts-style/scripts/verify_genealogy_revision.py --before caa49bf --output projects/usefulcharts-style/artifacts/reviews/landmarks-final-facts.json
uv run --script projects/usefulcharts-style/scripts/compare_posters.py --repository . --before-revision caa49bf --artifacts projects/usefulcharts-style/artifacts --after-prefix landmarks-final --comparison-name landmarks-final-comparison --before-label "Previous local-baseline revision"
uv run --script projects/usefulcharts-style/scripts/verify_gallery.py skills/usefulcharts-style/assets/examples/usefulcharts-style --artifacts projects/usefulcharts-style/artifacts/reviews/landmarks-final-gallery
uv run --script projects/usefulcharts-style/scripts/summarize_landmark_revision.py
```

For each canonical ID (`aurelian-families`, `atlas-of-inquiry`, `five-regional-histories`):

```powershell
uv run --script skills/usefulcharts-style/scripts/audit_chart.py skills/usefulcharts-style/assets/examples/usefulcharts-style/<id>.svg --source skills/usefulcharts-style/assets/examples/usefulcharts-style/<id>.json --report projects/usefulcharts-style/artifacts/reviews/landmarks-final-<id>-browser.json --png projects/usefulcharts-style/artifacts/images/landmarks-final-<id>.png
uv run --script projects/usefulcharts-style/scripts/verify_mutations.py --skill skills/usefulcharts-style --svg skills/usefulcharts-style/assets/examples/usefulcharts-style/<id>.svg --source skills/usefulcharts-style/assets/examples/usefulcharts-style/<id>.json --artifacts projects/usefulcharts-style/artifacts/reviews/landmarks-final-mutations/<id>
```

Use a fresh run ID for each isolated repetition; retain the recorded workspaces unchanged:

```powershell
uv run --script scripts/run-pi-skill-eval.py usefulcharts-style --prompt-file evaluations/pi-prompts/usefulcharts-landmark-contract.md --mode json --strict --run-id <fresh-contract-id> --require-exact-command-from-prompt --expect-output draft.json --expect-output result/source.json --expect-output result/placement.json --expect-output result/poster.svg --expect-output result/layout.json --expect-output result/browser.json --expect-output result/poster.png --expect-output-json-field result/placement.json::status=pass --expect-output-json-field result/browser.json::status=pass
uv run --script scripts/run-pi-skill-eval.py usefulcharts-style --prompt-file evaluations/pi-prompts/usefulcharts-reserved-context-contract.md --mode json --strict --run-id <fresh-reservation-contract-id> --require-exact-command-from-prompt --expect-output draft.json --expect-output result/source.json --expect-output result/placement.json --expect-output result/poster.svg --expect-output result/layout.json --expect-output result/browser.json --expect-output result/poster.png --expect-output-json-field result/placement.json::status=pass --expect-output-json-field result/browser.json::status=pass
uv run --script scripts/run-pi-skill-eval.py usefulcharts-style --prompt-file evaluations/pi-prompts/usefulcharts-family-landmarks.md --model openai-codex/gpt-5.5 --mode json --strict --run-id <fresh-family-id> --expect-output result/source.json --expect-output result/poster.svg --expect-output result/poster.html --expect-output result/layout.json --expect-output result/browser.json --expect-output result/poster.png --expect-output-json-field result/layout.json::status=pass --expect-output-json-field result/browser.json::status=pass
uv run --script evaluations/contracts/verify-usefulcharts-family-landmarks.py evaluations/runs/<fresh-family-id> --output evaluations/runs/<fresh-family-id>/independent-artifact.json
uv run --script scripts/summarize-pi-json-events.py evaluations/runs/<fresh-family-id>/events.jsonl --require-model gpt-5.5 --fail-on-invalid-json --fail-on-tool-error
```

Pattern IDs, skill structure, independence, payload, quick skill validation, Pages generation and local installation synchronization pass. The local Pages build produces 639 files / 41.83 MiB. Final runtime copies and exact outputs were inspected before explicit staging of this skill's changes; unrelated working changes remain outside these commits.

## Publication

Implementation commit `e948a77cc891d2bac45c85944b5e8d506c2e5a6a` is published on `main`. The [Pages workflow 34680066156](https://github.com/gvillarroel/skills/actions/runs/34680066156) completed successfully. Independent HTTP verification compared all eleven gallery, manifest and poster files against the complete expected committed bytes after the standard Pages metadata and whitespace transformations. All matched and the main example catalog still links this gallery. Local evidence: `projects/usefulcharts-style/artifacts/reviews/context-landmarks-publication-verification.json`.

The [published gallery](https://gvillarroel.github.io/skills/examples/usefulcharts-style/) retains its three stable routes. The updated [Aurelian genealogy](https://gvillarroel.github.io/skills/examples/usefulcharts-style/aurelian-families.html) exposes the seven source-bound realm captions. The institutional and timeline examples remain available with their earlier unresolved visual findings. Publication is delivery evidence, not an aesthetic pass; the skill and the indistinguishability objective remain in validation.
