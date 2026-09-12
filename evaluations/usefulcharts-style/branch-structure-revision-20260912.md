# Branch structure and ambiguous connections

Date: 2026-09-12. Baseline: `0be67c64c8f9ce74708b2d35fe355204004f21df`.

**The new chapter compositions were rejected as replacements for the published mural.** The skill gains a concrete routing correction and an independent visible-path check, but the user's standard of equivalent UsefulCharts quality and composition remains unmet. Keep the skill `validating` and the existing goal active.

## What the comparison exposed

The official [Christian Denominations Family Tree](https://usefulcharts.com/products/christian-denominations-family-tree) uses unequal historical stages, many small intermediate names, selected larger institutions and numerous distinctive emblems. Later families occupy different parts of the page. The existing fictional institution study has fewer families and more persistent regional spines. Its repeated captions also give almost every institution a similar three-part envelope.

The new project-only prototypes separate causal succession from a proportional calendar, reallocate space as local histories finish, and select consequential captions from the author's fictional study. They preserve all 141 institutional identities, founding dates, categories, illustration identities, type sizes and 171 typed relationships. All 133 original nonempty notes remain in `research_note`; only 33 are printed. This is an explicitly disclosed editorial edition of synthetic material, **not** proof that the same complete printed information fits a smaller page. The published source and its 133 printed notes remain unchanged.

Seventeen attempts are retained: eight completed proposals, eight placement/solver failures and one author-cancelled routing attempt. Seven rendered candidate PNGs were inspected directly. Initial CP searches found no complete solution within their limits; early greedy proposals ran out of descendant space; two overly strict solver runs reached their iteration limit. A subsequent feasible relaxation retains measured envelopes and causal order. The full attempt inventory, driver hashes, comparisons and forward results are in [the machine-readable summary](branch-structure-summary-20260912.json).

The final candidate uses 1620 × 2300 units, compared with the baseline's 1620 × 2430. Its lower field is more occupied and the selected notes make some local groups easier to scan. However, its measured routes grow from 32,045 to 36,669 units, bends from 488 to 556, and proper crossing entries from 77 to 106. These counts are diagnostics, not aesthetic scores. Direct full-page and detail inspection also shows more detours, continuing large regional structures and conspicuous repeated image panels. The total result is not a clear enough improvement to replace the existing gallery example.

The private comparison is `projects/usefulcharts-style/artifacts/reviews/institution-chapters-v30/comparison-final/comparison.html`; its full-page screenshot, opening and closing details remain beside it. Reference artwork is used only for local critique and is not included in published examples. The final rejected SVG has SHA-256 `c4b327dd61d3dc8740f25dcede7576e470996a863e89c9978120c3c672514073`; its inspected PNG has SHA-256 `5a44d37843cca97e3b75d9b15e1241d8b430fea1fc2959a0d7ec7fced7236866`.

## Reusable correction

Moving the graph exposed a correctness problem: the former automatic renderer could accept a node-clear orthogonal route that shared a straight run with a completely unrelated edge. The first relaxed chapter candidate has 25 affected edge pairs under independent inspection, corresponding to 26 overlapping straight segments in the separate route diagnostic.

The institutional renderer now reserves already composed runs whose edges share no endpoint with the new relation. The influence helper applies the same rule when choosing side attachments. Perpendicular crossings remain possible and legitimate shared endpoints remain available. Explicit authored corridors are preserved for external review. Memoization bounds repeated clearance and crossing calculations within each route search. The earlier prolonged render was cancelled after verifying its owned process; the cached version completed, but no controlled runtime speedup is claimed. Large unconstrained murals can still require a substantial routing pass; frozen reviewed corridors render quickly.

The browser audit now reports `unrelated-shared-run` for more than four units of a visible straight stroke shared by unrelated institutional edges. It reads actual SVG path commands and transforms, rather than accepting route metadata as evidence. It does not prove historical interpretation, inspect every curved coincidence, or score resemblance. It deliberately reports a composition warning so an authored shared structure can be reviewed without silently changing the source.

After recomposition, the final candidate has zero unrelated shared-run warnings and zero unrelated collinear overlaps under the separate diagnostic. The remaining 17 mixed-kind shared-endpoint segments are not covered by the unrelated-edge rule and still require visual interpretation. The retained published mural already has zero unrelated overlaps; the correction protects newly composed histories.

The new [branch-structure recipe](../../skills/usefulcharts-style/references/branch-structure.md) explains causal chapters, source limitations, selective author-created copy, required visible notes, warning interpretation and rejection of misleading density improvements. It explicitly forbids hiding supplied notes or manufacturing branches to imitate the reference's density.

## Isolated forward evaluation

The final runtime has 93 files and SHA-256 `99793d4932a0e886278c0ea7bc734db69e1562de8952fbab1a2adc36730c4e0f`. All four trials use that exact read-only payload without examples or ambient repository context.

The naturalistic prompt uses 59 mechanical, optical and common-origin records, 65 relationships and 15 visible notes selected from disclosed development material. It asks the agent to compose local chapters, preserve every supplied field, inspect the final image and critique its output. This is not a blind, independent-subject or holdout test. The scoped GPT-5.5 exception continues because Spark cannot inspect PNGs; a default Spark command control exercises a precise four-node crossing arrangement.

| Trial | Strict execution | Final artifact contract | Direct visual assessment |
| --- | --- | --- | --- |
| `usefulcharts-v30-branches-1-20260912` | Pass | Pass | Clear names and dates, but a large quiet upper field and optical successors displaced toward the right. |
| `usefulcharts-v30-branches-2-20260912` | Fail | Pass after repairs | More compact final optical grouping; large quiet fields and repeated levels remain. |
| `usefulcharts-v30-branches-3-20260912` | Pass | Pass | Selected illustrations and correct categories; long regular stages and isolated lower groups remain. |
| `usefulcharts-v30-contract-spark-20260912` | Pass | Pass | Exact-command routing control; no visual-parity claim or agent image requirement. |

Run 2 retains three tool errors: an attempted lateral attachment on a structural relationship, absolute routes left in a packed layout followed by auditing an older SVG against the changed source, and a failed shell command. Its eventual artifact passes, but the strict failure is not reclassified. No extra trial was selected to erase it.

All three naturalistic final PNGs were inspected by the evaluated model and independently by the author. All final source inventories, visible names/notes/years, colors and relationship kinds pass the independent contract. All four evaluator-owned browser reruns pass without unrelated-run warnings. Strict execution passes 3/4 overall, including 2/3 naturalistic repetitions. Every trace uses the expected model, remains confined to the runtime/workspace read surface and leaves the payload unchanged. All three substantial outputs remain visually distinguishable from the intended reference grammar, especially in their oversized common-origin area.

## Verification

- All 151 skill tests pass: the existing 146 plus five new shared-run tests. The new cases distinguish collinear runs from crossings and touching endpoints, exercise an alternate clear corridor, retain source immutability and explicit corridors, and preserve a legitimate sibling junction.
- Five independent browser controls pass, including detection when saved route metadata is deliberately falsified. Perpendicular crossings and legitimate siblings do not produce the warning.
- All 13 institutional SVG mutations are detected. These cover source revision, dates, captions, inventory, text geometry, contrast, relation kinds and attachment corruption.
- The three canonical examples rebuild without a tracked content change. All three mural browser audits, the responsive gallery, 14 Pi harness tests, metadata validation, pattern IDs, repository structure, bundle independence and payload checks pass.
- Pages build and local installation synchronization are included in the final repository verification. Publication applies to the updated reusable pattern guidance and skill; no rejected poster replaces a public example.

The next structural work should address the large unused field in normal 31–100-record outputs and test a meaningful subject with richer branching. Do not treat another small coordinate adjustment of the same persistent regional graph as sufficient evidence of visual parity.

## Reproduction

```powershell
uv run --script projects/usefulcharts-style/scripts/compose_institution_chapters.py --profile chapters --method greedy-relax --output projects/usefulcharts-style/artifacts/reviews/branch-chapters-reproduction
uv run --script skills/usefulcharts-style/scripts/route_influences.py projects/usefulcharts-style/artifacts/reviews/branch-chapters-reproduction/source.json --output projects/usefulcharts-style/artifacts/reviews/branch-chapters-reproduction/routed.json --report projects/usefulcharts-style/artifacts/reviews/branch-chapters-reproduction/routing.json
uv run --script skills/usefulcharts-style/scripts/test_lineage_runs.py
uv run --script projects/usefulcharts-style/scripts/verify_shared_runs.py --output projects/usefulcharts-style/artifacts/reviews/shared-runs-reproduction
uv run --script projects/usefulcharts-style/scripts/summarize_branch_structure.py
uv run --script skills/usefulcharts-style/assets/examples/usefulcharts-style/build_examples.py --renderer skills/usefulcharts-style/scripts/render_chart.py
uv run --script scripts/build-pages.py
uv run --script scripts/sync-local-skills.py
uv run --script scripts/validate-pattern-ids.py
uv run --script scripts/validate-skills.py
uv run --script scripts/test-skill-independence.py
uv run --script scripts/check-repo-payload.py
```

For fresh forward tests, replace `N` with 1, 2 and 3 and use unused run IDs:

```powershell
uv run --script scripts/run-pi-skill-eval.py usefulcharts-style --prompt-file evaluations/pi-prompts/usefulcharts-branch-structure.md --model openai-codex/gpt-5.5 --mode json --strict --run-id usefulcharts-v30-branches-N-20260912 --timeout-seconds 900 --expect-output result/source.json --expect-output result/poster.svg --expect-output result/poster.html --expect-output result/layout.json --expect-output result/browser.json --expect-output result/poster.png --expect-output result/review.md
uv run --script evaluations/contracts/verify-usefulcharts-branch-structure.py evaluations/runs/usefulcharts-v30-branches-N-20260912 --output evaluations/runs/usefulcharts-v30-branches-N-20260912/independent-artifact.json
uv run --script scripts/run-pi-skill-eval.py usefulcharts-style --prompt-file evaluations/pi-prompts/usefulcharts-branch-structure-contract.md --mode json --strict --run-id usefulcharts-v30-contract-spark-20260912 --timeout-seconds 900 --require-exact-command-from-prompt --expect-output draft.json --expect-output result/poster.svg --expect-output result/poster.html --expect-output result/layout.json --expect-output result/browser.json --expect-output result/poster.png
uv run --script scripts/summarize-pi-json-events.py evaluations/runs/usefulcharts-v30-contract-spark-20260912/events.jsonl --require-model gpt-5.3-codex-spark --fail-on-invalid-json --fail-on-tool-error
```
