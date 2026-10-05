# Dynamic Slidev layout templates — 2026-10-05

## Scope and acceptance

Update the canonical `slidev-echarts` and `slidev-animejs` bundles with identical self-contained layout resources. The four modes are equal-width columns with balanced contiguous groups, row-major regular grid, shortest-column vertical masonry, and literal horizontal row masonry with configurable row count and item widths. The supplied horizontal example has three rows. Both bundles remain usable without sibling skills or repository files.

Use the existing exact Colorset 1 and Colorset 2 categorical sequence. Allocate identities before pagination, retain first-seen identities within an instance, and document a complete category manifest for cross-slide/remount continuity. Exclude the white canvas from category fills. Exhaust all usable solids before border overflow. Select opaque black or white text by maximum relative-luminance contrast. Keep Open Sans and explicit fixed typography; custom slots own their typography and content. Native diagrams continue through the separately qualified deck-wide Mermaid setup.

Capacity is a report, not an automatic promise that arbitrary content fits. Require `fits=true` in publication states. Paginate, widen cards, reduce columns or split slides when needed. Preserve all full item text and stable IDs. Never reduce type to fit, crop content, or remove excess items. Slots receive both outer dimensions and padding/border-adjusted content dimensions so responsive charts do not grow through measurement feedback. A custom slot is responsible for its own content contract.

The evaluator-owned [acceptance contract](../contracts/slidev-layout-templates.md) was frozen before the release cohort. Four isolated prompts under `evaluations/pi-prompts/slidev-layout-templates-*` cover exact contract and naturalistic authoring tasks. Required outputs are `deck/slides.md`, `deck/package.json`, `deck/components/CollectionStory.vue`, `deck/data/cards.json`, `deck/components/SlidevLayout.vue`, `deck/lib/slidev-layouts.mjs` and `deliverables/layout-review.md`.

## Frozen resources

Both skill copies have identical runtime resources and checker. The collection parent is 13,332 bytes because it contains native plaintext measurement, complete-partition planning, font/content lifecycle and slot/page controls; normal authoring can copy it using the compact guide without reading its implementation. This required resource remains well below the 50 KB gallery boundary. The two compact guides differ only where the owning skill and its published routes require it. Each guide is below 10 KB.

| Resource | SHA-256 |
| --- | --- |
| `assets/templates/slidev-layouts/components/SlidevLayout.vue` | `227f1258f0a7695e4551c8d5310a3d34c77ed3b0ac89029971d7684ad69389b3` |
| `assets/templates/slidev-layouts/lib/slidev-layouts.mjs` | `99fc6d415bd59417e59045703b02653a1f789b63ad1e209582b19ae6a4c0c439` |
| `scripts/check_layout_deck.py` | `63f52a4ff397a6a9b153162b28cf444344273cba601e5362ba0df444ba3fb4e9` |
| `assets/templates/slidev-layouts/components/SlidevCollection.vue` | `e15f3dcf7cbd0680aaa6f1e9a618750b058da7b4ee46ab5fe312fcd6318724b2` |
| Fixture `components/DynamicLayoutExample.vue` | `2895a2b299815205078c60fa3134f7603d1c362708ccceb5131dcb5f8ebd69f4` |

## Native and deterministic evidence

- `node --experimental-strip-types projects/slidev-layout-templates/scripts/test-layouts.ts`: 22 checks pass, including all four modes for counts 1–31 (124 geometry combinations), exact palette allocation, stable IDs and category order, invalid inputs, pagination and oversized content.
- `node --experimental-strip-types projects/slidev-layout-templates/scripts/test-layout-ssr.ts`: 32 native Vue SSR cases pass (8 engine cases and 24 collection cases) without browser globals.
- `node --experimental-strip-types projects/slidev-layout-templates/scripts/verify-native-layouts.ts`: the frozen final runtime passes 213/213 browser cases with zero JavaScript errors. The local evidence is `projects/slidev-layout-templates/artifacts/native-capacity-final/verification.json`. Check actual wide/narrow inner widths, four modes, counts 3/7/11, both palettes, light/dark UI, reduced motion, reorder/filter/restore, every page and ID, opaque text, fixed custom/default font sizes, first-seen category continuity, content-box chart sizing and parent capacity feedback. Deliberately oversized content reports `fits=false`; all original long labels/bodies recover through wider cards and explicit pagination.
- `uv run --script projects/slidev-layout-templates/scripts/test-static-layout-check.py`: 17 regression tests pass against both identical checker copies. Check valid Slidev headmatter and fenced extra CSS without guessing slide count, required CLI/theme/Vue declarations, immutable copied runtime, complete unique JSON IDs, finite positive widths, exact item count, and rejection of outside-deck data paths before reads. The checker remains read-only.
- Both fixture `npm run build` commands, ECharts `npm run build:html` and Anime.js `npm run export:html` pass. Independent browser verification passes 188 control states in 120 count/column/order groups, with all active IDs reachable by paging, complete readable text, stable identity colors, fixed fonts, native slide/viewport bounds, no unexpected console errors, and manually reviewed captures of all eight default slides. Retain five expected headless Wake Lock denials as environment evidence. Final local report: `projects/slidev-dynamic-layouts/artifacts/fixture-final3/summary.json`.

Retain initial capacity and fixture failures. The runtime repairs use real CSS pixel measurements under Slidev scaling, font-ready remeasurement, stable measurement feedback, default typography scoped to fallback content, and content-box budgets. The row fixture frame was corrected from 325 to 330 pixels after a 2-pixel overflow; vertical masonry uses a 72-pixel minimum to demonstrate variable natural heights. Preliminary successful subsets are not release evidence for the final source.

The final grid fixture uses two rows and `pageSize = columns × 2` to fill its stage without a reserved empty third track. Other modes keep their configured geometry. Both final production and Pages builds pass all 188 control states/120 page groups after this refinement. All 16 default captures are reviewed. Fresh reports are `projects/slidev-dynamic-layouts/artifacts/{fixture-grid-final,pages-grid-final}/{verification,summary}.json`; earlier reports remain as pre-revision evidence. The isolated runtime payload is unchanged.

## Isolated authoring release

Both mandated own-skill Spark attempts, `20261005-slidev-layouts-echarts-spark-contract` and `20261005-slidev-layouts-animejs-spark-contract`, fail before any tool call: the provider reports that `gpt-5.3-codex-spark` is unsupported with this ChatGPT account. No artifacts were produced and both failures remain retained. Record the release model exception as `openai-codex/gpt-5.6-sol` with high thinking, before launching its fresh cohorts; no strict gate changes. Both Sol contract harness runs pass all strict gates. Naturalistic result 2 for Anime.js is retained as a workflow failure: five tool errors (two reads before files existed, a nonunique edit, shell substitution and incorrect headmatter separator counting). Its clean isolation, immutable payload and produced artifacts do not waive those errors. The whole initial cohort completes with 7/8 strict passes. Native grading identifies genuine capacity/column adaptation, viewport budgeting and invisible badge defects. Joint naturalistic results are 0/3 for ECharts and 1/3 for Anime.js, below the required 2/3 threshold; this cohort is not accepted. Every final outcome is retained.

Use the runtime payload, strict JSON, exact output paths, zero tool errors, valid observed model, unchanged skill resources and a clean read surface. Run one contract case and three fresh naturalistic repetitions per skill. Independently build and grade every generated deck using the frozen browser grader; do not select only the best repetition or waive failures.

The first independent grader SHA-256 is `17eaf3a3d5d010d5a22740f2e911446750b165d2549e43f3157c851bd6011e4d`; its evaluator-owned initial preflight passes 47/47 native cases with zero JavaScript errors. The preflight corrected a hidden-slide navigation wait before any isolated output was graded, without changing acceptance gates. Evidence: `projects/slidev-layout-templates/artifacts/grader-golden/final/verification.json`.

The grader's narrower-available-width check uses an actual 680-CSS-pixel inner frame and width restoration. The completed golden preflight passes 101/101 with actual width changes/restoration and real keyboard navigation. Validator corrections remove an undeclared exact font-size floor, distinguish semantic title/body from order metadata, inspect labels against actual backing paint, retain off-viewport frames as failures, restore measured constraints and reject unreachable controls instead of force-clicking. All initial outputs were regraded with the frozen final source below.

The independent grader checks native parsed slide count, final copied runtime hashes, all requested count/column click states, both exact palettes, maximum-contrast opaque labels, capacity, nonoverlap, complete source text, page coverage and identity stability, narrow inner containers, reduced motion, literal three-row semantics, at least two final horizontal widths and vertical heights, and named page-control paint/active contrast. It accepts documented fixed compact 16/14-pixel slots and 20/18-pixel fallback text, while rejecting size changes across count/page/resize states.


| Initial Sol case | Strict | Independent native | Joint outcome |
| --- | --- | --- | --- |
| ECharts contract | Pass | Fail: narrow capacity, blocked controls and missing page coverage (107 cases) | Fail |
| ECharts natural-1 | Pass | Fail: narrow pager outside viewport (92 cases); fixed 13.5px body is manually confirmed readable | Fail |
| ECharts natural-2 | Pass | Fail: narrow frame overflow (176 cases) | Fail |
| ECharts natural-3 | Pass | Fail: blocked narrow pager and incomplete coverage (96 cases) | Fail |
| Anime.js contract | Pass | Fail: narrow frame/pager clipping (101 cases) | Fail |
| Anime.js natural-1 | Pass | Pass: 101 cases; manually confirmed readable native masonry | Pass |
| Anime.js natural-2 | Fail: five tool errors | Fail: count/columns/real clicks/coverage (93 cases) | Fail |
| Anime.js natural-3 | Pass | Fail: viewport clipping and ordinal paint at 1:1 contrast (107 cases) | Fail |

All initial run IDs are `20261005-slidev-layouts-<echarts|animejs>-sol-<contract|natural-1|natural-2|natural-3>`. Native reports are under `projects/slidev-layout-templates/artifacts/pi-old-final/<run-id>/verification.json`. The frozen final grader is `4bfd2e496078115b84d5b2203165f6e22ec7b078a827c312e2a2e6fb93f922ff`; the same exact source graded every retained output and passes 101/101 golden cases at `projects/slidev-layout-templates/artifacts/grader-golden/frozen-final/verification.json`.

## Skill simplification after the initial cohort

Add `SlidevCollection.vue` as the preferred copy-ready parent, leaving both frozen engine resources unchanged. It owns readable 16/14-pixel opaque Open Sans fallback cards, complete-data identity allocation before count selection, actual-container column limits, a globally qualified stable page partition, exact-palette accessible controls and optional slot forwarding. Measure every default plaintext card at its actual per-mode width and qualify every page with the pure planner before enabling navigation. Requalify for fonts and semantic geometry edits. Do not let transient child measurements mutate an already visited partition. Custom slots use an explicitly qualified fixed page budget and preserve failures without hidden duplicate component lifecycles. An individually oversized card remains a reported failure. The guide now registers real Slidev clicks and budgets a concise fixed heading through explicit default layout, avoiding the first-slide cover heading. No authored output or evaluation prompt is repaired to force a pass. The static checker qualifies all three copied runtime files; its 17 regressions pass, including missing/empty parent files. The frozen parent passes 571/571 native states and 188 complete ordered traversals, including all four modes/counts 3/7/11 and both palettes at 880/680/480 actual CSS pixels, all semantic setting edits, desired pageSize 100000, longer later copy, default/explicit identity manifests, custom inner-box charts, dark/reduced motion, full glyph/paint checks and keyboard reachability of oversized copy. Its evaluator-owned parent golden passes 93/93 cases under the unchanged 4bfd grader. One expected headless Wake Lock denial is retained separately; no unexpected browser errors occur. Source remains frozen. Fresh strict v2 cohorts launched with the recorded Sol exception and the same seven exact paths; acceptance remains one passing contract plus at least 2/3 joint naturalistic passes per skill.

Native parent command: `node --experimental-strip-types projects/slidev-layout-templates/scripts/verify-native-collection.ts`. Final evidence: `projects/slidev-layout-templates/artifacts/native-collection-full-e15/{summary,verification}.json` and `projects/slidev-layout-templates/artifacts/grader-golden-parent/candidate/verification.json`.

Frozen runtime payloads: ECharts 56 files / 308,489 bytes, SHA `9a922bf41c8905f05493439e3df38f5af8a5b5317bb7f02e8b03697243f4501c`; Anime.js 52 files / 192,191 bytes, SHA `d162bea4bb5e9ff2a447235276787503a2d7fbc4984aaacc24a936f380d928b8`. Candidate per-file snapshot: `projects/slidev-layout-templates/artifacts/qualification/collection-candidate-profile.json`.

## Second cohort and focused guide repair

All eight v2 runs retain their complete outcomes under the same frozen 4bfd grader: four strict passes, seven native passes across 824 cases, eight data-contract passes, seven manual visual passes and four joint passes. Both contracts pass, but each skill has only 1/3 joint naturalistic passes and remains unqualified. Four naturalistic authors edited the output copy of the parent to add reading-order text; the exact-runtime checker rejected those edits. They restored the original resource and delivered correct final copies, but the genuine tool error remains in strict history. ECharts natural-3 additionally used a custom item slot with pageSize eight, derived from four requested columns. At 680 CSS pixels the parent correctly lowers effective columns to three while preserving the custom fixed partition; slides 1, 2 and 4 in the final state overflow and report fits=false. No output was repaired or failure waived.

| V2 case | ECharts strict/native | Anime.js strict/native |
| --- | --- | --- |
| contract | Pass / Pass (101 cases) | Pass / Pass (110 cases) |
| natural-1 | Pass / Pass (101) | Pass / Pass (101) |
| natural-2 | Fail / Pass (101) | Fail / Pass (113) |
| natural-3 | Fail / Fail (101) | Fail / Pass (96) |

V2 IDs use `20261005-slidev-layouts-<echarts|animejs>-sol-v2-<case>`. Exact commands, body counts and captures are retained in `projects/slidev-layout-templates/artifacts/qualification/v2-cohort-final.json`; isolation/payload audits are in `evaluations/runs/20261005-slidev-layouts-v2-audit-summary.json`. All eight have clean reads, unchanged payloads, exact outputs and final frozen runtime copies.

The v3 repair changes only the two core instructions and compact guides (9,902 bytes each). Explicitly keep the three copied runtime resources unchanged. Add visible order by mapping the complete input data to numbered display titles in the wrapper; preserve original JSON titles, stable IDs and complete category allocation. Use the default plaintext renderer so global automatic qualification applies, avoiding a custom slot solely for metadata. Runtime, evaluator, naturalistic prompts, model exception and acceptance gates remain unchanged. Launch a fresh full cohort with IDs `20261005-slidev-layouts-<echarts|animejs>-sol-v3-<case>`; retain both prior failed cohorts.

The release invocation below is repeated for both owners, using their contract prompt once and naturalistic prompt three times with distinct run IDs. Every run records its exact command in `command.txt`; all seven expected paths remain mandatory.

```powershell
uv run --script scripts/run-pi-skill-eval.py slidev-echarts --prompt-file evaluations/pi-prompts/slidev-layout-templates-echarts-naturalistic.md --run-id 20261005-slidev-layouts-echarts-sol-v3-natural-1 --model openai-codex/gpt-5.6-sol --thinking high --mode json --strict --expect-output deck/slides.md --expect-output deck/package.json --expect-output deck/components/CollectionStory.vue --expect-output deck/data/cards.json --expect-output deck/components/SlidevLayout.vue --expect-output deck/lib/slidev-layouts.mjs --expect-output deliverables/layout-review.md
uv run --script scripts/summarize-pi-json-events.py evaluations/runs/20261005-slidev-layouts-echarts-sol-v3-natural-1/events.jsonl --require-model gpt-5.6-sol --fail-on-invalid-json --fail-on-tool-error
```

## Final v3 release cohort

Both owners meet the frozen release policy: a joint-passing contract and 2/3 joint naturalistic repetitions. All eight final native outputs pass 820 browser cases; all eight authored-copy and manual full-label/body reviews pass. All bodies have one to three sentences, and the naturalistic bodies stay below the declared 25-word maximum. Six workflows pass strict model/event/output/isolation/integrity/zero-tool-error gates. Retain two genuine workflow failures: ECharts natural-2 makes two false global separator-count assertions (expecting three then four); Anime.js natural-1 makes one (expecting five). The guide already explicitly forbids this counting method, both bundled checker runs pass, and all three runtime resources remain unchanged. Subsequent corrected source checks do not remove those historical errors. No reroll, failure waiver, author output edit or acceptance relaxation is used.

| V3 case | ECharts strict/native | Anime.js strict/native |
| --- | --- | --- |
| contract | Pass / Pass (113 cases) | Pass / Pass (119 cases) |
| natural-1 | Pass / Pass (91) | Fail / Pass (93) |
| natural-2 | Fail / Pass (101) | Pass / Pass (101) |
| natural-3 | Pass / Pass (101) | Pass / Pass (101) |

The numbered default-adapter golden independently passes 93 native cases plus 41 page states / 168 visible ordinal/full-title checks at 880/680 CSS pixels, with original JSON unchanged. Evidence: `projects/slidev-layout-templates/artifacts/qualification/numbered-golden-preflight.json`.

All eight read surfaces and shell results pass independent isolation, all seven required paths exist, all copied skill payloads are unchanged, and all final runtime hashes match the frozen resources. The source epoch remains fixed until these audits complete. V3 frozen payloads are ECharts 56 files / 308,578 bytes / SHA `97ef0d575c08a87571ffc8991e1e44453457cfd65f0b53e914d6cfd50903486f`, and Anime.js 52 files / 192,280 bytes / SHA `2db02008485e1e3b49ad5d38f286d71c39a62212b45ac1f12c9f5e27e9df816c`. Preserve `evaluations/runs/20261005-slidev-layouts-v3-frozen-profile-snapshots.json` and each run's `read-surface-summary.json`; native/data/manual outcomes and commands are consolidated in `projects/slidev-layout-templates/artifacts/qualification/v3-cohort-final.json`.

After all frozen-epoch audits complete, remove exactly one trailing guide space per skill and normalize the core files' 67/69 CRLF pairs to LF for Git. Independent complete-inventory comparison confirms exactly these four text deltas, equal normalized content, no other changes and identical runtime/checker/grader hashes. Released payloads: ECharts 56 files / 308,510 bytes / SHA `09f2be93b674301916d99d027d84f601f13ce6868efd54a6ebd729cb06dd38ed`; Anime.js 52 files / 192,210 bytes / SHA `530a8ad782587f9ce910238e8b0a39bc49437e0be297ae24ca28c3f27bab55e5`. Release guides are 9,901 bytes. Proof is `projects/slidev-layout-templates/artifacts/qualification/v3-release-independent-proof.json`; full release inventories are `evaluations/runs/20261005-slidev-layouts-release-profile-snapshots.json`. This formatting cleanup changes no skill behavior. The normalized release passes pattern IDs, skill validation, independence, payload and the full authoring audit; sequential local sync/check again matches all 10,321 canonical files. Commands and before/after hashes are retained under `projects/slidev-layout-templates/artifacts/release-normalization-gates/`.

## Publication and repository gates

Local publication validation passes: `build-pages.py` produces 729 files (56.27 MiB), `validate-pages-pattern-format.py` qualifies all 14 catalog example sets, `validate-pattern-ids.py` reports 1,222 globally unique canonical IDs with maximum length 46, and `test-pages-output.py` passes 14 regressions. The built Pages output passes all 188 control states on the eight native routes, including exact palette/maximum-contrast paint, opacity, full glyph bounds, no overlap, capacity, stable identities, every page and main-index discoverability. Evidence: `projects/slidev-dynamic-layouts/artifacts/pages-final/verification.json`; two expected headless Wake Lock denials are retained and no unexpected browser errors occur. Remote deployment remains pending.

Final pre-normalization repository/publication preparation passes all 12 recorded commands: pattern IDs, skill validation, independence, payload, Pages boundary tests (14), Pi harness tests (17), standalone authoring audit (34 source skills / 68 runtime/full bundles / zero issues), Pages build, pattern format, local sync, sequential sync check and reproducible native route verification. The latter passes 188 states / 120 traversals / eight routes / two main-index catalog cards; two expected headless Wake Lock denials are retained separately. All selected authored hashes are unchanged. Exact argv, timestamps, exit codes and logs are in `projects/slidev-layout-templates/artifacts/final-publication-gates/{commands,summary}.json`; native evidence is in `projects/slidev-layout-templates/artifacts/final-publication-local-routes/{summary,verification}.json`.

```powershell
uv run --script scripts/build-pages.py
uv run --script scripts/validate-pages-pattern-format.py
node --experimental-strip-types projects/slidev-layout-templates/scripts/verify-published-layout-routes.ts --base-url dist/pages --output projects/slidev-layout-templates/artifacts/final-publication-local-routes
uv run --script scripts/validate-pattern-ids.py
uv run --script scripts/validate-skills.py
uv run --script scripts/test-skill-independence.py
uv run --script scripts/check-repo-payload.py
uv run --script scripts/audit-skill-authoring.py --check-bundles --output projects/slidev-layout-templates/artifacts/final-publication-gates/authoring-audit.json
uv run --script scripts/test-pages-output.py
uv run --script scripts/test-pi-eval-harness.py
uv run --script scripts/sync-local-skills.py
uv run --script scripts/sync-local-skills.py --check
```

These additions extend the two existing catalog example sets and preserve all existing routes, including ECharts Mermaid `#/37` and Anime.js Mermaid `#/31`.

| Canonical pattern suffix | ECharts route | Anime.js route |
| --- | --- | --- |
| `dynamic-columns` | `#/38` | `#/32` |
| `dynamic-grid` | `#/39` | `#/33` |
| `masonry-rows` | `#/40` | `#/34` |
| `masonry-columns` | `#/41` | `#/35` |

Complete the Pages build, pattern/catalog validation, repository structure and independence validators, payload check, bundle authoring audit and local installation sync/check. Commit only the task's explicit source, reference, fixture, backlog and durable evaluation paths; preserve unrelated working-tree edits. Push the Pages branch, verify a successful workflow at the release SHA, and inspect the public native routes before marking both skills done.
