# D3 Consolidation and Release Validation — 2026-08-14

## Outcome

The repository now has one canonical D3 skill at `skills/d3/` and one canonical
D3 entry on the GitHub Pages home page. The frozen runtime candidate passed the
full release gate and the backlog status is `done`.

## Consolidated Runtime

- `SKILL.md`: 86 lines.
- Runtime payload: 309 files and 3,205,411 bytes.
- Pattern routing: 242 pattern references across 217 pattern files.
- Consolidated routes: 24 former standalone recipes represented by three
  anchored collections.
- Root reference orphans: zero.
- Largest Markdown reference: 49,917 bytes.
- Bundle-efficiency score: 0.916773.
- Runtime manifest SHA-256:
  `bfe4d4f21e2af4927030687ac9a5690dcc4dbbdf47d3da11738b55009d182b60`.
- Candidate profile SHA-256:
  `847ae3e689375a20b5eac2cde7a365fc5d7a3922fb00e01d97ae118a47c6f443`.

The final maintenance pass also made deterministic-builder use resilient to a
missing `python` alias by requiring an immediate `python3` fallback, and it
requires quoting complete CLI values that contain whitespace.

## Compact GitHub Pages Surface

The main catalog exposes exactly one D3 card with canonical example-set ID
`d3`. That card opens `skills/d3/assets/examples/d3/index.html`, which presents:

- eight capability groups;
- six focused gallery links;
- the 242-route pattern inventory;
- 225 gallery cards, 78 composition variants, 90 logo mechanisms, and 40
  textures;
- preserved legacy routes for the detailed pattern, colorset, composition,
  logo, and texture galleries.

`scripts/build-pages.py` produced 413 files (26.52 MiB), and
`scripts/validate-pages-pattern-format.py` validated 11 published entries.
Playwright checks passed at 1440×1000 and 390×844 with no horizontal overflow
or console errors. The detailed pattern gallery opened from the hub with all
225 cards.

## Frozen Datasets

The study uses a fresh random split generated before candidate selection. Its
four validation tasks and four final-test tasks are disjoint from each other
and from the twelve prior D3 dataset roots supplied to the generator. Each task
was run twice with `gpt-5.3-codex-spark`.

| Dataset | Tasks | Attempts | SHA-256 |
| --- | ---: | ---: | --- |
| Validation | 4 | 8 | `42bf00999411ceca26fd0e7aaabfac203f03c212800769e04999e92c8e7ff078` |
| Sealed final test | 4 | 8 | `1809ac63ceb4b44275b8ad3751ce685806b211d769b1d697d471ab3b8bb18687` |

`evaluations/d3/test_pareto_iteration2_dataset.py` passed the split count,
zero-overlap, and undisclosed-holdout checks. The final-test cohort was released
once only after candidate v3 was frozen; the skill was not mutated afterward.

## Verification Results

### Local and Browser Gates

- 22/22 D3 skill unit tests passed.
- The 225-card replay verifier passed 225/225.
- The 225-card visual audit reported zero blank, clipping, text, font,
  animation, replay, or browser failures.
- Colorset 1 and Colorset 2 galleries each passed 225/225 with zero invalid
  paint tokens.
- All seven composition sheets passed with 78 variants and 225 reviewed source
  patterns.
- Pattern-ID validation passed 1,159 canonical IDs; maximum length was 46.
- Repository skill validation, skill independence, payload, Pages format, and
  diff checks passed.

### Strict Isolated Pi

Final run `d3-consolidation-standard-20260814-spark-v3` passed strict JSON mode
with the observed `gpt-5.3-codex-spark` model, exact output paths, unchanged
runtime payload, valid event JSON, zero tool errors, and a focused read surface.
Independent checks passed self-containment, colorset1, rendered SVG structure,
three exact bars, ordered values, attributes, unit, route, and decision fields.
The run used 90,689 total tokens.

Two immediately preceding strict runs are retained as useful diagnostics: both
created correct, immutable artifacts but failed the zero-tool-error gate after
first passing an unquoted whitespace value to the visual-contract CLI and then
correcting it. Their repeated failure caused the final quoting rule added to
the skill; candidate v3 then passed cleanly.

### Harbor Validation and Final Test

The completed canonical study is
`evaluations/d3/harbor-consolidation-study-20260814-v2/`.

| Stage | Semantic passes | Completed | Errors | Result |
| --- | ---: | ---: | ---: | --- |
| Validation v2 | 8 | 8 | 0 | Pass |
| Once-released final test v2 | 8 | 8 | 0 | Pass |

The final ledger has 26 events, 10 digest-bound evidence records, four of four
completed stages, and head SHA-256
`bb40364b6f04d76ae3697b2ab189038797d8f5af2e19c72f03021d8019bd8327`.
The public final-decision evidence SHA-256 is
`cd950a9c2352092651aa8d92949f29c32d3b8a0985d2c5561ce079aa1f0db67a`.

The preceding v1 study remains as append-only diagnostic history. It was
superseded before its holdout was released after strict Pi exposed the quoting
gap.

## Representative Commands

```powershell
uv run python -m unittest discover -s skills/d3/assets/examples/skill-tests -p 'test_*.py' -v
uv run --script scripts/validate-pattern-ids.py
uv run --script scripts/validate-skills.py
uv run --script scripts/test-skill-independence.py
uv run --script scripts/check-repo-payload.py
uv run --script scripts/build-pages.py
uv run --script scripts/validate-pages-pattern-format.py
uv run --script scripts/run-pi-skill-eval.py d3 --prompt-file evaluations/pi-prompts/d3-unified-standard-bar.md --model openai-codex/gpt-5.3-codex-spark --mode json --strict --run-id d3-consolidation-standard-20260814-spark-v3 --expect-output deliverables/visual.html --expect-output deliverables/decision.json
```

Harbor validation and final-test jobs were run from runtime-bound configs under
`evaluations/runs/d3-consolidation-20260814-v3-candidate/`. Native jobs, traces,
and bulky reports remain under ignored `evaluations/runs/`; the study
publication index exposes only reviewed aggregate decision evidence.
