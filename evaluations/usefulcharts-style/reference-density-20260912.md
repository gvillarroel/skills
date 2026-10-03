# Reference knowledge density

Date: 2026-09-12. Skill: `usefulcharts-style`. Status: **validating**.

## Finding and acceptance boundary

The requested minimum is at least the useful knowledge density of the relevant UsefulCharts poster. The current chronology does not provide comparable branching and explanatory detail. The genealogy has a substantial inventory, and the institutional example has substantial text, but neither has a reviewed full-body semantic census establishing the requested minimum. **None of the three current examples receives a reference-density pass in this evaluation.** Clean geometry and a large number of records do not establish that result.

The updated skill treats knowledge density as a requirement in all three stages: information sufficiency, editorial selection, and final critique. It compares distinct named records, typed relationships, temporal anchors, and explanatory or comparative claims separately. Each candidate lower count bound must meet the corresponding reference upper bound. Extra names cannot compensate for insufficient context. Facts must be supported, relevant and readable; resizing, decorative fill, repeated labels and generic prose cannot repair a deficit.

## Reference inspection

The following official product pages and their actual full-poster previews were inspected. Reference images remain in ignored private project artifacts; they are not distributed inside the skill or the public gallery.

| Family | Official reference | Actual preview size | Image SHA-256 |
| --- | --- | --- | --- |
| Genealogy | [European Royal Family Tree (West)](https://usefulcharts.com/products/european-royal-family-tree) | 1240 × 1862 | `9521e8272f4f141d79c080cb4794cc1a1b7adffe3eb56e717e070cab5ce37681` |
| Institutional lineage | [Christian Denominations Family Tree](https://usefulcharts.com/products/christian-denominations-family-tree) | 1284 × 1924 | `05db9954eb790dfcba475daa2c178ee8fed815b5bb504abaa58b970043ed331d` |
| Parallel chronology | [Timeline of World History](https://usefulcharts.com/products/timeline-of-world-history) | 1200 × 1800 | `a0c934e1c28719994372677ee717197856faaa4f4b67438fa267d7fbbafcb107` |

The lineage product description advertises over 100 denominations and uses major-branch colors. That advertised count establishes broad scope, not a complete density specification. The chronology page describes a history starting in 3300 BCE with the Americas, Europe, Africa, the Middle East and Asia displayed alongside each other. Reading the actual images is necessary to see how their information layers are distributed.

Observed design consequences:

- **Genealogy:** focal rulers, supporting relatives, partnerships, dates, family membership, places and roles share local groups. A dense name inventory alone does not reproduce the historical explanation. The current 561-person example is substantial, but its semantic equivalence remains unverified.
- **Institutional lineage:** short institution labels and dated predecessors combine with irregular splits, continuities and transitions. Quantitative and geographic context adds knowledge beyond the genealogy of institutions. The current 141-node example contains long-lived families and long influence routes; similar text volume cannot establish equivalent content or spatial use.
- **Chronology:** periods, dated developments, concurrent histories, causes and consequences accumulate across a shared scale. Later centuries use many more local branches and contextual notes than the early section. The current five-lane example is visibly more regular and sparse, with broad colored periods and a repetitive division/union cadence. Fifty periods and sixty event notes do not reproduce that richer narrative. A background map does not itself establish supported geographic assertions.

These are direct visual judgments, not a similarity percentage or a completed semantic census. No exact reference minimum is invented from an unreadable label.

## Comparable display and diagnostic measurements

A [private comparison viewer](../../projects/usefulcharts-style/artifacts/reviews/density-v35/comparison/index.html) displays each reference and candidate at equal total area while preserving aspect ratio. It offers a family selector, zoom, body-third guides and a narrow-screen layout. Playwright verified all three equal-area pairs and all four controls. The evaluator also opened the complete reference images, all three current renders and the timeline comparison screenshot. Upper, middle and lower regions were inspected rather than selecting only the densest pocket.

Current source inventories and browser results are useful descriptive evidence, but are **not the new semantic census units**:

| Current example | Source inventory | Browser/geometry result |
| --- | --- | --- |
| `aurelian-families` | 561 people; 323 renderer edges; 261 unions | Pass; 1,154 text elements; zero findings |
| `atlas-of-inquiry` | 141 nodes; 171 renderer edges | Pass; 648 text elements; zero findings |
| `five-regional-histories` | 50 periods; 55 transitions; 60 event notes | Pass; 353 text elements; zero findings |

All three browser reports show minimum measured text contrast 4.9491. Rendered PNG identities are respectively `1f3acf13525b8e243c4eb7bb516830ea510d3e8999b0200ccce8e5ec7bd3d997`, `af27177e1ae2411e20d6e00db63bbeaa63648bf6d184fd7afbf1d01b644d85b2`, and `e4e50f484b47df39e7158584e5a8d3a7161e12b85d7ffd3c6724ffea70bdf63c`.

RapidOCR 3.9.2 provided a **screening experiment only**. Each image was normalized to 1,600 pixels wide, then divided into two columns and three rows with 40-pixel overlaps. Recognition used twice the tile resolution, and overlapping detections were deduplicated. A 4.5–98.5% vertical body window excluded most title/footer regions. This shared-width OCR protocol is not the equal-area semantic acceptance method.

| Image | Detected body text lines | Recognized non-space characters | Lines in upper / middle / lower body third |
| --- | ---: | ---: | --- |
| Royal genealogy reference | 312 | 2,175 | 127 / 95 / 90 |
| Current genealogy | 1,150 | 9,381 | 325 / 421 / 404 |
| Denominations reference | 879 | 6,896 | 186 / 296 / 397 |
| Current institutional history | 647 | 6,848 | 135 / 294 / 218 |
| World history reference | 1,058 | 8,298 | 182 / 345 / 531 |
| Current parallel history | 351 | 5,052 | 86 / 121 / 144 |

The initial whole-image protocol detected only 73 genealogy lines and 599 characters. Tiling improved recognition but still missed many small names. That retained failure prevents interpreting the candidate's apparent numerical advantage as greater knowledge density. OCR can also read map lettering or logos, split lines differently, duplicate a semantic claim and misrecognize words. Character volume and text-box area cannot verify relevance or factual meaning. The chronology's detected text deficit supports further inspection; it is not a measured percentage of missing knowledge. The institution's similar character count is not a pass.

Both protocols, full private OCR results, cached models, renders, browser reports and screenshots remain under `projects/usefulcharts-style/artifacts/reviews/density-v35/`. Reproduce the analysis with:

```powershell
uv run --script projects/usefulcharts-style/scripts/measure_reference_text.py projects/usefulcharts-style/artifacts/images/reference-royal.png projects/usefulcharts-style/artifacts/images/reference-denominations.png projects/usefulcharts-style/artifacts/images/reference-history.png projects/usefulcharts-style/artifacts/reviews/density-v35/rendered/aurelian-families.png projects/usefulcharts-style/artifacts/reviews/density-v35/rendered/atlas-of-inquiry.png projects/usefulcharts-style/artifacts/reviews/density-v35/rendered/five-regional-histories.png --output projects/usefulcharts-style/artifacts/reviews/density-v35/ocr-tiled
uv run --script projects/usefulcharts-style/scripts/build_density_review.py
```

The OCR tool is a project research aid, not a required skill dependency. The locked environment contains the OCR dependencies; runtime poster generation does not.

## Reusable minimum and repair behavior

[Knowledge-density guidance](../../skills/usefulcharts-style/references/knowledge-density.md) defines the four counting units, equal-area comparison, complete image coverage, source ledger and independent legibility review. [The census template](../../skills/usefulcharts-style/assets/templates/density-census.json) starts with unknown counts and pending reviews. It cannot pass merely by being copied.

[The comparator](../../skills/usefulcharts-style/scripts/compare_density.py) validates the declared census and calculates conservative shortfalls. It rejects malformed intervals and mismatched families or comparison bases. Unknown counts, OCR-only evidence, selected crops, missing image/ledger identity and incomplete semantic or legibility review remain `needs-evidence`. A reviewed census below any one layer's minimum is `below-reference`. Only four sufficient reviewed layers produce `meets-measured-floor`.

The helper does not verify a ledger's truth, recount a rendered poster or certify aesthetics. A successful command means that comparison completed. Use `--require-pass` when a failing decision must also return a nonzero exit code. Read the report and independently verify its evidence in all cases.

Repair order is substantive first: recover useful omitted facts and intermediates; research relevant missing relationships, dates, roles, causes, consequences and comparisons; then reclaim space and improve the composition. Recount and re-inspect after a structural change. A smaller page is not an automatic waiver of the requested knowledge inventory. Honor an explicitly limited-scope request while describing its actual scope honestly.

## Frozen isolated validation

The development contract preregistered three fresh naturalistic runs plus one command control, using `openai-codex/gpt-5.3-codex-spark`, high thinking, strict JSON mode and a read-only runtime payload. After observing failures, each subsequent cohort was preregistered in `SKILLS.md` with the same prompt and unchanged criteria. Acceptance examples and ambient repository context are excluded. Each cohort and its corresponding control share the same 116-file frozen runtime:

| Cohort | Runtime SHA-256 | Strict naturalistic execution | Independent machine contract | Complete naturalistic contract |
| --- | --- | ---: | ---: | ---: |
| A | `fd8ae41044433f540c1cc8ee311a2718c7d337b668eaa97660c4997bf54771b1` | 0/3 | 0/3 | 0/3 |
| B | `5748e33311d2589ed150aca534cebebc01ee8203463265eead249e05a6a03517` | 1/3 | 1/3 | 0/3 |
| C | `a2a9d55eb11cb90e9a481dd92303b0316d8941e9f51fcc00598f3ffd77448e8d` | 2/3 | 3/3 | 1/3 |

- Naturalistic prompt: [density review](../pi-prompts/usefulcharts-density-review.md), SHA-256 `c116b8b00c7ece0bc1c745451bc4b2692c72f88f6227ad1b1e4cf4abacaebe01`.
- Exact command: [comparator interface](../pi-prompts/usefulcharts-density-contract.md).
- Independent criteria: [density contract](../contracts/usefulcharts-density-review.md), not supplied to the model.
- Naturalistic run IDs: `usefulcharts-v35-density-spark-{1,2,3}-20260912`.
- Control run ID: `usefulcharts-v35-density-contract-spark-20260912`.
- Revised cohort and control IDs replace `v35` with `v35b` and `v35c` respectively.

The counts and image identities in these prompts are **explicitly synthetic workflow fixtures**. They are not the values measured from UsefulCharts. The three negative drafts exercise excess names with insufficient context, unreviewed OCR counts, and sufficient declared content that is unreadable. The positive control checks equal reviewed point counts. These tests cannot establish historical research quality, actual visual density, a complete render/critique loop, or model ranking.

**Cohort A: 0/3 complete naturalistic passes.** All three correctly withhold production approval for the unsuitable drafts, but hand-write incompatible census profiles and reports instead of using the supported interface. All three fail the preregistered JSON boolean checks and independent replay. A1 reads the knowledge-density reference; A2 and A3 read only the entry point. A2 recommends adding 41–58 contextual statements, and A3 targets the reference's lower bound of 145 rather than requiring the candidate's lower bound to reach 150. These optimistic repairs fail the conservative minimum; the required guaranteed addition is 58. No failure is discarded or reclassified as a pass because the broad rejection decision was correct.

The initial command control passes strict execution and independent replay. It correctly limits the result to a synthetic declared-census check. Cohort A and its control have valid event traces, zero tool errors and unchanged payloads; those technical results do not erase the content/interface failures.

The first revision adds a direct density-review route near the entry point, canonical template fields, mandatory comparator-generated reports and explicit conservative repair targets. It does not add test values to the skill or change the user prompt, expected output paths, numeric floor or acceptance contract.

**Cohort B: 0/3 complete naturalistic passes.** B1 uses the comparator, preserves the supplied profiles, produces correct conservative shortfalls and passes strict execution and independent replay. Its prose omits the broader image/source/distribution boundary before an aesthetic claim. B2 and B3 continue to hand-write incompatible profiles and reports; both incorrectly mark evidence-deficient drafts as measured-floor passes while separately withholding production approval. B3 also stores count layers outside the required `counts` object, so the comparator cannot replay its inputs. Its repair target of 151 is unnecessarily strict; equality at 150 would satisfy the actual minimum. All failures remain recorded.

The final revision turns the review route into five ordered steps with a standalone command and an explicit final evidence boundary. **Cohort C produces correct machine artifacts in 3/3 runs and complete acceptance in 1/3.** All three now execute the comparator, preserve supplied evidence, reject the three unsuitable drafts and calculate the context shortfall as 58. Independent replay exactly matches all nine delivered reports.

- C1 explicitly states the evidence boundary and supplies useful repairs, but its unnecessary verification script iterates over census inputs and density reports alike, then calls `len(None)` on a report without `image_sha256`. The retained tool error fails strict execution. Classify this as an agent verification-script error, not a comparator defect or external infrastructure failure.
- C2 passes the complete contract: correct profiles and reports, meaningful repairs, no production approval for deficient drafts, and an explicit requirement for image, source, distribution and legibility evidence before aesthetic acceptance.
- C3 correctly uses the comparator and passes strict execution, but its prose omits the complete image/source/distribution boundary before aesthetic acceptance. The generated JSON scope statement remains correct; that is not counted as fulfilling the required prose explanation.

Complete acceptance remains below the preregistered two-of-three threshold. Do not select only C2 or report the three correct machine outputs as three complete skill-use passes. All three command controls pass strict execution, independent replay and direct review of the final scope statements. No further cohort was run to select a more favorable result.

All twelve copied payloads remain unchanged. Eleven trace checks pass; C1 correctly retains its tool-error failure. All read surfaces exclude acceptance examples, external context and sibling skills. Final normal-use reads are limited to the entry point, census template, knowledge-density reference and, in some cases, the compact comparator source. Reading that implementation is unnecessary for ordinary use but does not introduce hidden repository knowledge. The [compact result ledger](reference-density-20260912.json) records each run's model, prompt and payload hashes, technical gates, human review, failure classification and actual read paths.

The [independent inspection script](../contracts/inspect-usefulcharts-density.py) checks supplied profile values against the original packet, invokes each run's frozen comparator, compares delivered reports against that replay, checks expected decisions and shortfalls, and verifies that the replay leaves inputs unchanged. Prose decisions require separate direct review.

For each naturalistic run, use the registered run ID:

```powershell
uv run --script scripts/run-pi-skill-eval.py usefulcharts-style --prompt-file evaluations/pi-prompts/usefulcharts-density-review.md --model openai-codex/gpt-5.3-codex-spark --thinking high --mode json --strict --run-id <run-id> --timeout-seconds 900 --expect-output result/reference.json --expect-output result/draft-a.json --expect-output result/draft-b.json --expect-output result/draft-c.json --expect-output result/draft-a-density.json --expect-output result/draft-b-density.json --expect-output result/draft-c-density.json --expect-output result/review.md --expect-output-json-field 'result/draft-a-density.json::passes_measured_floor=false' --expect-output-json-field 'result/draft-b-density.json::passes_measured_floor=false' --expect-output-json-field 'result/draft-c-density.json::passes_measured_floor=false'
uv run --script evaluations/contracts/inspect-usefulcharts-density.py evaluations/runs/<run-id>
uv run --script scripts/summarize-pi-json-events.py evaluations/runs/<run-id>/events.jsonl --output evaluations/runs/<run-id>/independent-trace.json --require-model gpt-5.3-codex-spark --require-tool-call --fail-on-invalid-json --fail-on-tool-error --require-read ../prompt.md
```

For each exact-command control:

```powershell
uv run --script scripts/run-pi-skill-eval.py usefulcharts-style --prompt-file evaluations/pi-prompts/usefulcharts-density-contract.md --model openai-codex/gpt-5.3-codex-spark --thinking high --mode json --strict --run-id <control-run-id> --timeout-seconds 900 --require-exact-command-from-prompt --expect-output reference.json --expect-output candidate.json --expect-output result/density.json --expect-output-json-field 'result/density.json::passes_measured_floor=true'
uv run --script evaluations/contracts/inspect-usefulcharts-density.py evaluations/runs/<control-run-id> --control
```

## Local verification

Passed all nine deterministic density tests, including layer deficits, conservative intervals, missing evidence, OCR-only counts, illegibility, family/basis mismatches, invalid values and CLI exit/overwrite behavior. The Pi harness passes 14 tests. Final pattern IDs (1,222), repository structure, skill independence, payload, quick metadata and whitespace checks pass. Project/evaluator Python files compile, and the OCR environment lock is current. The private browser comparison passes all three equal-area pairs and four controls.

```powershell
uv run --script skills/usefulcharts-style/scripts/test_density.py
uv run --script scripts/test-pi-eval-harness.py
uv run --script scripts/validate-pattern-ids.py
uv run --script scripts/validate-skills.py
uv run --script scripts/test-skill-independence.py
uv run --script scripts/check-repo-payload.py
uv lock --check --script projects/usefulcharts-style/scripts/measure_reference_text.py
git diff --check
uv run --script scripts/sync-local-skills.py --source skills/usefulcharts-style --destination .agents/skills/usefulcharts-style
uv run --script scripts/sync-local-skills.py --source skills/usefulcharts-style --destination .agents/skills/usefulcharts-style --check
```

Synchronization refreshes eight changed files and its check confirms all 133 canonical source files. The runtime fingerprint remains the frozen cohort C fingerprint. The prior three-stage evaluation separately records the existing geometry regression suites; no new geometry improvement is inferred from this density study.

## Remaining limits

An actual full-body reference census remains incomplete. None of the gallery images is certified to meet the new minimum. The chronology needs more relevant detail and varied historical structure before another finished-poster claim. The earlier unpublished chronology prototype also remains unsuccessful because illustrated-note placement fails; the runtime contains its four previously uncommitted geometry changes, and this census-only study cannot validate those new visual features. Its retained evidence remains under `projects/usefulcharts-style/artifacts/reviews/varied-chronology-v34/`.

No published example or pattern is changed by this density workflow revision. Continue the original aesthetic objective without treating the new acceptance rule, a passing unit test or a metadata-only exercise as evidence of indistinguishability.
