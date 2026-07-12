# PlantUML normalized logo assets — 2026-07-12

- Skill: `plantuml-colorset-renderer`
- Change: add ten normalized SVG technology logos, per-logo provenance and licensing, an offline export command, and PlantUML insertion guidance.
- Source: Simple Icons commit `0f9fa549da00e9aa6e3ef8d3d2171f481360e638`; every upstream SVG is SHA-256 pinned before normalization.
- Common contract: intrinsic `256×256`, `viewBox="0 0 24 24"`, and `preserveAspectRatio="xMidYMid meet"`.

## Deterministic and visual validation

- `uv run --script .agents/skills/plantuml-colorset-renderer/scripts/sync_normalized_logos.py --check` — passed for all ten assets.
- `uv run --script .agents/skills/plantuml-colorset-renderer/scripts/sync_normalized_logos.py --export projects/plantuml-colorset-renderer/artifacts/logo-export` followed by `--check --output ...` — passed and preserved the full bundle.
- `uv run --script .agents/skills/plantuml-colorset-renderer/scripts/test_plantuml_coverage.py` — 16 tests passed.
- Playwright Chromium grid check — all ten images reported natural dimensions `256×256`, rendered in `96×96` boxes, decoded successfully, and produced zero console errors after adding an empty data favicon. Visual inspection found no stretching or clipping.
- `uv run --script scripts/validate-pattern-ids.py` — passed.
- `uv run --script scripts/validate-skills.py` — passed.
- `uv run --script scripts/check-repo-payload.py` — passed.
- `uv run --script scripts/test-pi-eval-harness.py` — 11 tests passed.

## Isolated Spark validation

Prompt: `evaluations/pi-prompts/plantuml-normalized-logo-export.md`  
Model: `openai-codex/gpt-5.3-codex-spark`  
Profile: runtime, JSON strict mode  
Required outputs: `outputs/plantuml-logos/license_log.md`, `apache.svg`, and `openjdk.svg`; external validation then required the exact ten-SVG inventory and synchronized license log.

Results for the final three-run naturalistic cohort:

- `20260712-plantuml-normalized-logos-export-spark-1` — passed strict harness, exact outputs, payload integrity, external ten-asset validator, and read-surface review.
- `20260712-plantuml-normalized-logos-export-spark-2` — passed the same gates.
- `20260712-plantuml-normalized-logos-export-spark-3` — artifact generation succeeded but strict event validation failed because the sampled agent first listed a not-yet-created output directory and later used a malformed Python heredoc. Classified as `agent`; the deterministic `--export` operation itself succeeded.

Outcome: 2/3 final-cohort passes, meeting the naturalistic repetition threshold. Passing read surfaces are recorded in `evaluations/plantuml-normalized-logos-export-spark-1-read-surface.json` and `evaluations/plantuml-normalized-logos-export-spark-2-read-surface.json`; neither read acceptance examples, sibling skills, or outside-workspace files.

Earlier catalog experiments (`naturalistic-spark-1` through `-4`) generated valid artifacts but mixed logo export with unrelated HTML authoring and exposed shell/Python quoting failures. They were replaced by the narrower export case; browser layout remains independently covered by Playwright.
