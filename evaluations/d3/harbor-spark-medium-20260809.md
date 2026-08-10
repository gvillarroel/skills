# Unified D3 Harbor release evaluation

Date: 2026-08-09  
Status: **validation failed; keep the skill at `validating`**

## Scope

This evaluation covers the single canonical `d3` skill created by consolidating the former D3 visualization/animation, composition-evaluation, recomposition, and logo skills. The unified contract makes `colorset1` the standard and default palette. It permits `colorset2` only when a request explicitly asks for an extended, expanded, full-color, or multicolor palette.

The release candidate was evaluated as a runtime-profile bundle: `SKILL.md`, `agents/`, `references/`, `scripts/`, and runtime `assets/`, excluding acceptance examples and dependency/build directories.

## Frozen candidate identity

| Property | Value |
| --- | --- |
| Candidate | `release-candidate-v1` |
| Runtime files | 347 |
| Runtime bytes | 3,418,618 |
| Runtime payload SHA-256 | `732b2e6737f7ec4cd855a8954db574b9fc3939a7b247fa8aa2acf9dd5fd29507` |
| Organizer tree SHA-256 | `8810254c2a6de191289cf7c3191f340bd07eeb6feabd7e223616947de6498d09` |
| Ledger head SHA-256 | `16a8f7b2159928ef88055aab54ed5b744ecdcb28facacd648d953b81863d43db` |

The organizer tree digest matched before evaluation and at candidate freeze. A separate post-holdout runtime restage of the current `skills/d3/` source reproduced the runtime payload SHA-256, file count, and byte count exactly. No candidate mutation occurred after holdout release.

## Dataset and leakage controls

The evaluator owns the task prompts, public acceptance contracts, verification code, Chromium rendering, palette measurement, and counterfactual palette-influence checks. Every verifier-enforced literal and structural requirement is disclosed in its task prompt. Attribute arrays are explicitly documented as allowed alternatives, not values to concatenate.

| Split | Tasks | Attempts | Registered SHA-256 | Permitted use |
| --- | ---: | ---: | --- | --- |
| Development | 3 | 9 | `033b575e6a48922225559b65a4e4d75e610acf21f5d61e1d2556a87a8c457229` | Candidate development and development gate |
| Validation | 2 | 6 | `2174969001a82f5cfbf25c3f693434b69a84ed0224065c2ae609c6dd66c7e5ff` | Candidate selection only |
| Holdout | 5 | 15 | `3075b40434b4e237761312df3763097c50d1ce5dda489ecfca1e971d41c5e213` | One final frozen-candidate gate only |

All three split digests were registered before the release jobs. The holdout was sealed before development and validation evaluation, then released once only after the selection decision and digest freeze. It was not used for candidate creation, evolution, selection, retry targeting, or post-run edits. The current holdout is permanently ineligible for future evolution or another release claim.

Dataset regression tests pass 6/6 and verify:

- exact 3/2/5 split sizes and three attempts per task;
- disjoint, current split-tree digests;
- split-bound job configurations with no cross-split paths;
- complete public prompt/verifier-contract equality;
- route and palette coverage;
- explicit final-only holdout policy.

## Harbor results

Native Harbor 0.18.0 jobs used `openai-codex/gpt-5.3-codex-spark` and three independent trials per task.

| Gate | Completed | Passed | Verifier failures | Execution errors | Result |
| --- | ---: | ---: | ---: | ---: | --- |
| Development | 9 | 8 | 1 | 0 | Passed predefined per-case gates |
| Validation | 6 | 6 | 0 | 0 | Candidate selected and frozen |
| Final holdout | 15 | 8 | 7 | 0 | **Failed release gate** |

The final holdout pass rate is 53.33%. Because the final-only gate failed, the unified skill is not release-approved even though development and validation passed. No selective retry was run.

The final study verifies successfully with 5/5 completed stages, 32 append-only ledger events, 12 digest-bound evidence records, and a valid hash-chain head. Local study status: [`harbor-study-20260809-v5/status.md`](harbor-study-20260809-v5/status.md).

## Deterministic and independent checks

The frozen source passes:

- 19/19 skill script tests covering the contract builders, exact-term evaluation reports, colorset routing, forbidden color syntax, accessibility, exact DOM structure, and near-equivalent literal rejection;
- 6/6 dataset tests;
- 2/2 runtime-staging tests;
- 1/1 candidate/job binding test;
- 4/4 evaluator-owned verifier tests in WSL with explicit Chromium and `playwright-core`, including positive render/palette/influence checks and a colorset1 negative control;
- Harbor study verification with `--render`.

Post-holdout route smokes built separate colorset1 and colorset2 logo studios. Both dedicated validators passed all 90 registered patterns, 40 registered textures, 90 compositions, embedded D3 7.9.0 runtime execution, registry parity, text-clearance contracts, exact initial colorset selection, and standalone output.

One cross-route inconsistency remains. A radial recomposition from the passing validation cohort uses SVG ID `review-recomposition`, node class `source-node`, and link class `source-link`, as required by its public Harbor contract. The bundled `check_recomposition_contract.py` instead requires SVG ID `d3-composition-radial-review-flow` and literal `node`/`link` classes. Running the dedicated checker against that accepted artifact fails with zero recognized nodes or links. This is an unresolved interface incompatibility, not a verifier-infrastructure failure, and supports the non-release disposition.

A post-holdout strict isolated `pi` run, `d3-unified-standard-bar-20260809-spark`, observed the required Spark model, preserved the skill payload, and created both exact requested artifacts. Independent checks passed on its generated HTML and settled SVG: self-containment, `colorset1` palette, accessibility metadata, literal IDs/attributes/text, three bound bar marks, and item order. The strict run nevertheless failed because its event trace contained tool errors, including an unavailable `python3` invocation on Windows, an inapplicable colorset2 gate, and invalid auxiliary checks. Artifact success does not override the strict process failure.

## Disposition

Keep `d3` at `validating`. The consolidation and palette contract are implemented, and deterministic/evaluator infrastructure is healthy, but final generalization is not established.

Do not use this holdout or its case-level failures to evolve the current candidate. Any future release attempt must start a separate study with independently defined development and validation material, freeze a new candidate, and reserve a newly generated, never-inspected holdout for its final gate.

## Reproduction commands

```powershell
uv run python -m unittest discover -s skills/d3/scripts -p "test_*.py" -v
$env:D3_HARBOR_DATASET_ROOT=(Resolve-Path 'evaluations/runs/d3-unified-harbor-20260809-v5').Path
uv run --script evaluations/d3/test_harbor_dataset.py -v
uv run --script evaluations/d3/test_stage_runtime_skill.py -v
uv run --script evaluations/d3/test_write_candidate_job_config.py -v
python C:\Users\villa\.codex\skills\harbor-organize-evaluations\scripts\manage_harbor_evaluations.py verify evaluations/d3/harbor-study-20260809-v5 --render
```

The WSL verifier test additionally requires `HARBOR_PLAYWRIGHT_CORE_PATH` and `HARBOR_BROWSER_PATH` to point to the installed Playwright runtime and Chromium binary before running `python3 evaluations/d3/test_verify_task.py -v` inside WSL.
