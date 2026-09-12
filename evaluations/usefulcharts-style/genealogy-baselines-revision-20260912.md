# Genealogy baselines and medium-family revision

Date: 2026-09-12. Skill: `usefulcharts-style`. Status: **validating**.

The revision makes the dense genealogy easier to follow and makes the new medium-family route reproducibly readable. It does **not** establish the user's requested indistinguishable quality and composition relative to UsefulCharts. The implementation and independent reviewer both identify a weaker intermediate layer of territorial captions, heraldry, explanatory transitions and selectively emphasized figures.

## Result and visual evidence

The dense Aurelian study preserves every nonvisual node field, original record order, all 561 people, all 261 partnerships and all 323 relationships. The categories, dates, reigns, houses, realms, roles, courts, portrait identities and annotation wording are unchanged. Only placement and visual treatment change. All three example posters remain original synthetic studies.

Principal names now use slimmer fitted nameplates with dates below them. Selected portraits have more presence, house and court pills sit beside the person they identify, and local family baselines follow supplied dates while reserving full parental departure space. A multiline heading's icon sits above the entire text block. Larger nameplate text is vertically centered with adequate measured margin.

The local reference comparison uses the official royal-family chart already documented in [reference analysis](reference-analysis-20260911.md). Complete pages have matched display widths; dense details use matched relative scale. Original reference artwork is retained privately for comparison and is not included in the published gallery.

The independent reviewer inspected the upper-middle blue family and lower multicolor junctions before and after the departure-space correction. The Richard I → Stephen II → William I → Edward I region is more open and easier to follow. At lower junctions, relationship origins are clearer, while long horizontal routes still require careful tracing. The crown collision is repaired. No material regression in typography, portrait legibility or page balance was identified; a few enlarged bends are a minor trade-off. This is an unblinded qualitative review, not a provenance-identification experiment.

Private evidence:

- `projects/usefulcharts-style/artifacts/reviews/genealogy-baselines-comparison/`: v17 reference/before/after study.
- `projects/usefulcharts-style/artifacts/reviews/genealogy-baselines-v19-comparison/`: final rendered reference/before/after study.
- `projects/usefulcharts-style/artifacts/reviews/genealogy-baselines-independent-review.md`: first independent critique.
- `projects/usefulcharts-style/artifacts/reviews/genealogy-baselines-final-independent-review.md`: departure-space comparison.
- `projects/usefulcharts-style/artifacts/reviews/genealogy-baselines-facts.json`: complete nonvisual-data comparison against `ef294e37`.
- `projects/usefulcharts-style/artifacts/reviews/family-baselines-forward-comparison/`: all six medium-family outputs, including rejected attempts.

The final dense source's semantic digest is `a5401a071e3f4a4b11c8c24abf035ec3429f951afdbc31274ead9326b896bdf2`. Its locally rebuilt JSON file digest before Git/Pages line-ending normalization is `750eb446744f0efcdb8945b7a51c58430e2a444c97ab508089221097c5d99cb8`. The route count changes from 31 crossings in the development nameplate candidate to 22 after reserving complete parental departure space. The direct visual review supports the improvement; those counts are not an aesthetic score.

## Reusable skill changes

- `space_family_branches.py` fits dated family units with a sparse constrained least-squares solver. Partners remain aligned; parentage advances; component label and portrait geometry and local family pills retain clearance. Dates are preferences within a schematic layout, not an invented metric time axis.
- Missing birth dates remain missing. Formatted date strings, impossible spans, nonadvancing relationships, multiple partnerships, inconsistent partner offsets and fixed geometry that requires deliberate recomposition fail with an actionable explanation.
- For 31–100 people, the runtime route now starts from a data-first brief without dimensions, node widths, fonts or repetitive style assignments. It measures 18-unit names, 13-unit dates, larger founders and source-supported landmarks. Source-connected ancestors receive nameplates; external partners and terminal relatives receive plain names. Explicit user styles and dimensions remain authoritative.
- `references/branch-baselines.md` promotes the nameplate/date system, complete departure gutters, source-based date preferences, locally meaningful labels and the need for an editorial pass over remaining long routes. Core routing and cohort guidance link to it. The runtime does not depend on acceptance galleries or repository files.
- The browser audit detects heading illustrations that touch text or leave the paper. The renderer exposes annotation groups and clears the complete multiline heading rather than using a fixed icon offset.

## Isolated forward evaluation

Both versions are retained as complete read-only runtime copies. The task prompt is unchanged across versions. The generalization case supplies 48 people, 21 partnerships, 36 relationships, 95 known numeric birth/death facts, one unknown birth, four explicit houses and three locally attached contextual labels.

After evaluation, terminal blank lines were removed from the two repository prompt files for the whitespace gate. The complete original prompts and original prompt digests remain frozen in every run; task wording and inputs are unchanged.

| Version | Runtime files and SHA-256 | Spark command contract | GPT-5.5 strict family runs | Independent final facts/geometry | Visual judgment |
| --- | --- | --- | --- | --- | --- |
| v18 | 75 · `fd6320cd3875794b7c2b2f6bc51985340b7dab29b8df63cc02210ace49606ec9` | 1/1 pass | 2/3 pass | 3/3 pass | Rejected as parity: repetitive filled cards, undersized nameplates or a very sparse tall page. |
| v19 | 75 · `23fae87d089c5d95dd50bbb86fadeb37c951ca4760b35c382eefb798dedea578` | 1/1 pass | 2/3 pass | 3/3 pass | All three final pages are readable compact compositions; parity remains unproven. |

The v19 pages consistently measure 1470.88 × 990.16. All three preserve the exact people, unions, descent and uncertainty, declared houses, known dates and unknown birth. Each supplies all six exact deliverables and uses supported image inspection. The final pages show distinct nameplate/plain-name treatment and locally attached context. Long lateral marriage corridors still dominate part of the middle; this small family is not evidence of dense poster parity.

The GPT-5.5 exception remains scoped to image-dependent evaluation because the documented Spark image limitation omits PNG input. Spark still validates the exact command contract. Strict mode checks model, valid events, zero tool errors, exact output paths, allowed reads and unchanged runtime payload. Normal read surfaces contain the prompt, the loaded skill, focused cohort/baseline/contract references, the small family template and generated outputs. No run reads an acceptance gallery, sibling skill or repository source.

Every attempt is recorded in [the machine-readable summary](genealogy-baselines-summary-20260912.json). v18 family repetition 2 fails strict execution after a too-small partnership gap, then produces a correct but visually poor large poster. v19 repetition 2 initially supplies a formatted unknown-birth value where the helper requires numeric or missing data; the helper rejects it, the agent repairs the record, and the final artifact passes. Its strict failure remains a failure. This is useful recovery evidence, not a zero-error pass.

An evaluator false negative in v19 repetition 3 treated the wrapped phrase “Birch reading room” as missing. Direct image inspection confirmed both lines. The contract now normalizes whitespace across actual SVG text elements, excluding metadata. The original failed evaluator JSON is retained beside the corrected report. This changes the verifier only, not the frozen skill or agent output.

## Deterministic and browser checks

All 91 tests pass: 26 classic renderer tests, 43 editorial tests, 13 family-baseline tests and 9 timeline-placement tests. The new tests cover an analytic projection, all-fact preservation, cross-family membership, undated records, per-component portrait clearance, full parental departure space, local labels, measured medium pages, explicit-style preservation, infeasible inputs and exact CLI outputs. The Pi harness's 14 tests pass.

All three canonical source-backed browser audits pass. The mutation suite detects 10 genealogy, 9 institutional and 14 timeline defects. The gallery passes desktop, mobile, fit, zoom and natural-aspect checks. The unchanged v18 text placement produces five expected name-envelope failures at 22-unit type; the corrected centering passes on the same source. That negative control is retained in `genealogy-editorial-development/preflight-v19/before-text-centering-*`.

Two earlier mutation-test failures were verifier defects: a union-origin displacement was initially graded as a person-origin displacement, and a reentry probe stayed inside the empty partnership gap. The repaired probes target the proper union-origin condition and actually pass through a partner's occupied box. No geometry threshold was relaxed.

Development attempts remain under `projects/usefulcharts-style/artifacts/genealogy-editorial-development/`: an initial projection produced an occupied attachment port; a stronger pure-Python projection did not converge; early nameplate variants exposed caption wrapping, insufficient vertical capacity and an unreserved family label. Per-component label reservation and the promoted solver resolved those cases. Local orchestration also attempted to read a few outputs before native background commands finished; those attempts are not counted as validation passes.

## Reproduction commands

Run from the repository root. The two prompt files contain the complete isolated inputs.

```powershell
uv run --script skills/usefulcharts-style/scripts/test_chart.py
uv run --script skills/usefulcharts-style/scripts/test_editorial.py
uv run --script skills/usefulcharts-style/scripts/test_family_baselines.py
uv run --script skills/usefulcharts-style/scripts/test_timeline_events.py
uv run --script scripts/test-pi-eval-harness.py
uv run --script skills/usefulcharts-style/assets/examples/usefulcharts-style/build_examples.py --renderer skills/usefulcharts-style/scripts/render_chart.py
uv run --script projects/usefulcharts-style/scripts/verify_genealogy_revision.py --output projects/usefulcharts-style/artifacts/reviews/genealogy-baselines-facts.json
uv run --script projects/usefulcharts-style/scripts/summarize_baseline_revision.py
uv run --script projects/usefulcharts-style/scripts/compare_family_baselines.py --output projects/usefulcharts-style/artifacts/reviews/family-baselines-forward-comparison
```

For each of `aurelian-families`, `atlas-of-inquiry`, and `five-regional-histories`, run:

```powershell
uv run --script skills/usefulcharts-style/scripts/audit_chart.py skills/usefulcharts-style/assets/examples/usefulcharts-style/<id>.svg --source skills/usefulcharts-style/assets/examples/usefulcharts-style/<id>.json --report projects/usefulcharts-style/artifacts/reviews/baselines-v19-<id>-browser.json --png projects/usefulcharts-style/artifacts/images/baselines-v19-<id>.png
uv run --script projects/usefulcharts-style/scripts/verify_mutations.py --skill skills/usefulcharts-style --svg skills/usefulcharts-style/assets/examples/usefulcharts-style/<id>.svg --source skills/usefulcharts-style/assets/examples/usefulcharts-style/<id>.json --artifacts projects/usefulcharts-style/artifacts/reviews/baselines-v19-mutations/<id>
```

Fresh strict runs use a new run ID; do not overwrite the recorded workspaces:

```powershell
uv run --script scripts/run-pi-skill-eval.py usefulcharts-style --prompt-file evaluations/pi-prompts/usefulcharts-baseline-contract.md --mode json --strict --run-id <fresh-contract-id> --require-exact-command-from-prompt --expect-output draft.json --expect-output deliverables/brief.json --expect-output deliverables/spacing.json --expect-output deliverables/poster.svg --expect-output deliverables/layout.json --expect-output-json-field deliverables/spacing.json::status=pass --expect-output-json-field deliverables/layout.json::status=pass
uv run --script scripts/run-pi-skill-eval.py usefulcharts-style --prompt-file evaluations/pi-prompts/usefulcharts-family-baselines.md --model openai-codex/gpt-5.5 --mode json --strict --run-id <fresh-family-id> --expect-output result/source.json --expect-output result/poster.svg --expect-output result/poster.html --expect-output result/layout.json --expect-output result/browser.json --expect-output result/poster.png --expect-output-json-field result/layout.json::status=pass --expect-output-json-field result/browser.json::status=pass
uv run --script evaluations/contracts/verify-usefulcharts-family-baselines.py evaluations/runs/<fresh-family-id> --output evaluations/runs/<fresh-family-id>/independent-artifact.json
uv run --script scripts/summarize-pi-json-events.py evaluations/runs/<fresh-family-id>/events.jsonl --require-model gpt-5.5 --fail-on-invalid-json --fail-on-tool-error
```

Release gates: pattern IDs, skill structure, independence, payload, quick skill validation, Pages build, local synchronization, responsive gallery verification and diff review. Keep the skill `validating`: remaining dense narrative hierarchy, long institutional corridors, timeline lane regularity and previously recorded unresolved-source reliability gaps are not closed by this revision.
