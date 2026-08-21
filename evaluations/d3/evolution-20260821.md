# D3 Compaction and Reward Evolution — 2026-08-21

## Outcome

The repository retains one canonical D3 skill at `skills/d3/`. The selected
runtime candidate reduces the iteration-2 runtime from 309 to 279 files while
preserving all 242 pattern routes, passing fresh visible validation and a sealed
holdout, and keeping the 86-line `SKILL.md` progressive-disclosure entrypoint.

The final runtime profile is:

| Metric | Previous release | Final candidate | Delta |
| --- | ---: | ---: | ---: |
| Runtime files | 309 | 279 | -30 (-9.71%) |
| Runtime bytes | 3,205,411 | 3,208,747 | +3,336 (+0.10%) |
| Pattern reference files | 217 | 187 | -30 |
| Pattern routes | 242 | 242 | 0 |
| Consolidated or anchored routes | 24 | 57 | +33 |
| `SKILL.md` lines | 86 | 86 | 0 |
| Orphan root references | 0 | 0 | 0 |
| Bundle-efficiency score | 0.773522 | 0.903509 | +0.129987 |

Under the frozen 90% semantic / 10% bundle reward policy and a perfect semantic
score, the combined reward rises from 0.977352 to 0.990351 (+0.012999). The
small byte increase is intentional: 33 narrowly scoped recipes were replaced
by three indexed collections that preserve their full implementation guidance,
while the file-count component reached its best threshold.

The final profile validator passed with 279 files, 3,208,747 bytes, 187 pattern
files, 242 routes, 57 consolidated routes, no findings, and report SHA-256
`f11980eb07a03a823ecc037acbdc8215951322227fd901620e7223387cd684d1`.

## Implemented compaction

`evaluations/d3/consolidate_iteration3_patterns.py` deterministically replaces
33 small pattern files with these three indexed collections:

- `references/patterns/interaction-motion-collection.md`
- `references/patterns/science-geometry-collection.md`
- `references/patterns/statistical-collection.md`

The consolidator rewrites all routes in `references/pattern-index.md`, verifies
every anchor, checks that the source set is complete, and is idempotent after
application. Its regression suite proves the 33-to-3 mapping and the 30-file
reduction. No capability was split into another skill.

Visible validation also exposed an ordered-label failure in a flow
recomposition: a title introduced a later stage before intervening stages.
That finding produced a compact title-order guardrail in `SKILL.md`, a
fail-fast check in `scripts/build_contract_artifact.py`, and a regression in
`assets/examples/skill-tests/test_build_contract_artifact.py`.

## Fresh datasets

The cryptographically randomized dataset generator is
`evaluations/d3/build_evolution_iteration3_dataset.py`; its contract tests are
in `evaluations/d3/test_evolution_iteration3_dataset.py`.

Two three-way 4/4/4 cohorts were produced:

| Cohort | Train digest | Validation digest | Holdout digest | Prior overlap | Cross-split overlap |
| --- | --- | --- | --- | ---: | ---: |
| v1 | `05662cf98f6069840c4a08ab7ee4fdf166865c2bfe5dbd76885b4f5f924197bf` | `112bc215b4ae1282bfab9075060d0bdaee5095b83c017211586f4a83910e90a9` | `4b0165a86b4eef5ba5fce7c8eb3a632c4377498e6dca89865a448b434d381fd2` | 0 | 0 |
| v2 | `fb013341b0a9726ba46b60775c22ddd8deb3073942c5cd7155b6c3358760079b` | `1905ca16a33f871dfd0e6d06e9b386a5a45ba203c85e690cfee1b2a163d5c9e6` | `cf4d3e73a4e797da8a73bbeb2d979121ef71ff262661c642733f5030a4ff60dd` | 0 across 46 prior roots | 0 |

Each split covers visualization, logo, recomposition, and composition-audit
routes. Across each 12-task cohort, colorset1 appears nine times and colorset2
three times. The aggregate dataset test passed before v2 holdout disclosure
with `holdoutContentDisclosed: false`.

## Evolution decision

The bounded Harbor 0.18.0 / GEPA 0.1.2 run is preserved under
`evaluations/runs/d3-evolution-20260821-v5-gepa/`.

- The baseline passed the four visible validation cases at reward 0.990363.
- GEPA made 12 metric calls and proposed one expanded instruction candidate.
- The candidate subsample score was 3.941484 versus the baseline's 3.961452,
  so GEPA rejected it and retained the compact baseline.
- The v1 Spark holdout is invalid as semantic evidence: all eight baseline and
  eight candidate attempts stopped on the external Spark usage limit before
  producing task artifacts. The resulting 0.090363 values contain only the
  bundle component. The run was classified fail-closed and was not resumed
  because it was a standalone trial-queue evolution run rather than an eligible
  completed-agent/pre-verifier recovery.

The useful deterministic collection mutation was therefore applied and tested
directly, then evaluated on the fresh v2 cohort. No rejected GEPA instruction
candidate was promoted.

## Validation and sealed holdout

The final v2 runtime was staged before holdout at
`evaluations/runs/d3-evolution-20260821-v2-dataset/runtime-stage-r1/d3`.
Canonical and staged runtime digests matched; the release record binds candidate
digest `6f0d32855fa599047b85bd742cd2b3663b44eadfa81270efc5353bf03b15e38e`
to validation-result SHA-256
`f632a4e362825d19206fefe0ccd651a49aade8df5f8a734cbb2a73e608294947`.
Only then was the holdout released at `2026-08-21T09:44:55.7881376Z`.

| Gate | Trials | Errors | Retries | Semantic pass | Mean reward |
| --- | ---: | ---: | ---: | ---: | ---: |
| Visible validation before title guardrail | 4 | 0 | 0 | 3/4 | 0.765364 |
| Visible validation after title guardrail | 4 | 0 | 0 | 4/4 | 0.990351 |
| Once-released sealed holdout | 4 | 0 | 0 | 4/4 | 0.990351 |

The targeted guardrail improved visible validation by 0.224987 without adding a
runtime file. The sealed holdout passed routing, D3 execution, fidelity,
metadata, palette, rendering, and semantic gates for all four routes.

Model exception: the repository default `gpt-5.3-codex-spark` could not run
because its usage quota was exhausted, and the local WSL Codex authentication
refresh was invalid. The valid v2 visible validation and holdout therefore used
`openrouter/openai/gpt-5.1`, high reasoning, one attempt per task, and no
retries. This exception is explicit; the invalid v1 Spark holdout is not counted
as a pass.

## Strict isolated runtime test

Strict isolated run `d3-evolution-20260821-v2-strict-openrouter` passed with
model `openrouter/openai/gpt-5.1`:

- Pi exit code 0 and exact non-empty outputs
  `deliverables/evaluation.md` and `deliverables/decision.json`.
- Artifact, event, and unchanged-skill integrity gates passed.
- Zero invalid JSON events and zero tool errors.
- The only reads were the prompt, `skills/d3/SKILL.md`, and the two generated
  deliverables: 12,041 result bytes total.
- The skill payload was unchanged before and after the run, with digest
  `6a34f8dd5e8a7d1c28f402da7d050687ab57b52b11d3e32815072b3439afb149`.

## GitHub Pages

`skills/d3/assets/examples/d3/index.html` is the one canonical D3 hub. It opens
with one hero block and then exposes the complete surface through eight
capability cards and six focused gallery links. Existing detailed routes remain
available, while the repository home has one D3 entry.

After rebuilding `docs/`, Playwright verified both 1440x1000 desktop and 390x844
mobile layouts:

- one hero block, eight capability cards, and six gallery links;
- no horizontal overflow;
- zero console errors or warnings;
- successful navigation from the hub to the 225-pattern gallery;
- visually clean full-page screenshots at
  `projects/d3-skill-evolution/artifacts/screenshots/d3-pages-desktop.png` and
  `projects/d3-skill-evolution/artifacts/screenshots/d3-pages-mobile.png`.

The source includes an empty data-URL favicon so the standalone hub produces no
spurious browser request failure.

## Final validation commands

The following checks passed on the final source state:

```powershell
python -m unittest discover -s skills/d3/assets/examples/skill-tests -p 'test_*.py' -v
python -m unittest discover -s evaluations/d3 -p 'test_*.py' -v
python evaluations/d3/consolidate_iteration3_patterns.py --skill-root skills/d3
uv run --script evaluations/d3/validate_pareto_candidate.py skills/d3 --dataset-manifest evaluations/runs/d3-evolution-20260821-v2-dataset/dataset-manifest.json --report evaluations/runs/d3-evolution-20260821-v2-dataset/final-candidate-profile.json
uv run --script scripts/summarize-pi-json-events.py evaluations/runs/d3-evolution-20260821-v2-strict-openrouter/events.jsonl --require-model openai/gpt-5.1 --fail-on-invalid-json --fail-on-tool-error
uv run --script scripts/build-pages.py
uv run --script scripts/validate-pages-pattern-format.py
uv run --script scripts/validate-pattern-ids.py
uv run --script scripts/validate-skills.py
uv run --script scripts/test-skill-independence.py
uv run --script scripts/check-repo-payload.py
uv run --script scripts/sync-local-skills.py
git diff --check
```

The D3 skill suite passed 23/23 tests. The evaluation suite ran 12 tests and
skipped two dataset-root integration classes when their explicit environment
variable was absent; the active dataset integration gate was run separately
against v2 and passed. Pages generation produced 413 files (26.52 MiB), and all
repository structural, independence, payload, and pattern-ID gates passed. The
Pages build emitted non-blocking third-party Rolldown annotation warnings from
unrelated Slidev dependencies.

Bulky Harbor, Pi, screenshot, and browser artifacts remain under ignored
`evaluations/runs/` and `projects/*/artifacts/` directories. This file is the
durable source-controlled summary.
