# Shared semantic colors — 2026-09-28

This narrow follow-up makes cross-panel color alignment an explicit, executable
contract. Canonical concepts can carry an opaque categorical color; native cards,
matrix entries, taxonomy bands, and boundaries bind to it. Imported SVGs annotate
their actual fill or stroke. The composer preserves the registry, and the browser
checks computed paint and per-panel coverage. Logos retain their original artwork.
Quantitative scales and the neutral theme have shared-design guidance; they are
not automatically certified by the categorical-paint audit.

## Frozen candidate and scope

- Runtime payload: 16 files, SHA-256
  `a4c8124edb83d051adbecf8f067b60dccd8ebdbad25c3ee1b2c0c0d23a1d77fa`.
- Model: `openai-codex/gpt-5.6-luna`, high, strict JSON mode, isolated runtime
  payload with ambient discovery disabled and unchanged read-only skill files.
- Exception: Spark was provider-rejected before tools in the same session;
  preserve the [earlier model evidence](validation-20260928.md). This update
  does not claim a successful Spark run.
- Four fresh forward tests: one command-contract and three naturalistic
  repetitions. No model attempt was retried or omitted in this update.
- The previous full composition release remains in
  [validation-20260928.md](validation-20260928.md). This update does not replace
  its historical results with the color-specific cohort.

## Deterministic checks

All 53 tests pass: 24 composition, 11 browser, ten native-panel, and eight
shared-color tests. The new suite exercises five native families, conflicting
local colors, unknown concepts, computed CSS overrides, missing per-panel
coverage, hidden/transparent/off-canvas accents, invalid channels, duplicate
palette meanings, and a CSS preparation/import/final-audit round trip. Tampering
with actual SVG paint makes the final audit fail. A test-only initial failure
from nested Playwright contexts was fixed by separating the import test class;
it did not require a runtime change.

Four previously accepted composition plans were regenerated after the update.
All four final SVGs are byte-identical to their originals and pass browser audits;
optional shared-color bindings do not alter existing unbound sources.

```powershell
uv run --script skills/diagram-composition/scripts/test_composition.py
uv run --script skills/diagram-composition/scripts/test_browser.py
uv run --script skills/diagram-composition/scripts/test_native_panels.py
uv run --script skills/diagram-composition/scripts/test_shared_colors.py
uv run --script projects/diagram-composition/scripts/verify_panel_regressions.py --skill-root skills/diagram-composition --runs evaluations/runs --output projects/diagram-composition/artifacts/reviews/color-update-regressions
```

## Isolated results and manual inspection

All four runs pass exact output, JSON field, observed model, event integrity,
zero tool-error, read-surface, and payload-integrity gates. Independent browser
audits and the evaluator-owned contract confirm the supplied blue/crimson
mapping in every required panel. All four screenshots were inspected.

| Run suffix after `diagram-colors-20260928-` | Strict | Palette/artifact | Manual review |
| --- | --- | --- | --- |
| `contract-1` | Pass | 4 occurrences / 2 panels | Pass; readable hub and matrix. The footer's hex values are unnecessary editorial detail. |
| `naturalistic-1` | Pass | 6 occurrences / 3 panels | Color pass; broader composition review flags an unlabeled directed cross-view arrow and a shared endpoint. Do not count it toward the full naturalistic visual gate. |
| `naturalistic-2` | Pass | 6 occurrences / 3 panels | Pass; consistent node outlines, row swatches, and group bands. Long identity routes are clear but could be shorter. |
| `naturalistic-3` | Pass | 6 occurrences / 3 panels | Pass; visible storage facts and direct identity mapping with no process implied. |

Thus the focused palette gate is 4/4; the broader naturalistic joint gate is
2/3. Color agreement does not prove semantic edge quality or optimal density.
The tall synthesis regions contain substantial whitespace because the supplied
brief fixes a two-row span for only two small collections. Labels remain at or
above 14 displayed pixels; no viewing-scale inflation was used.

Every trace reads the small `shared-colors.md` reference. Runtime reads are
limited to the supplied prompt, the owning skill's entry point, selected compact
references/template, and generated task outputs. No acceptance fixture, sibling
skill, repository document, or large renderer source was read.

Durable per-run trace and artifact records are adjacent files named
`colors-contract-20260928-{trace,artifact}.json` and
`colors-naturalistic-{1,2,3}-20260928-{trace,artifact}.json`. Raw manifests,
events, screenshots, editable SVGs, and harness results remain under
`evaluations/runs/diagram-colors-20260928-<suffix>/`.

## Reproduction

Run the following with `$Case = 'naturalistic'` and `$Attempt = 1, 2, 3` in
separate fresh workspaces. For the single contract case use `$Case = 'contract'`,
`$Attempt = 1`, its prompt below, and add `--expect-output out/brief.json`.

```powershell
$Prompt = 'evaluations/pi-prompts/diagram-composition-shared-colors.md'
# Contract prompt: evaluations/pi-prompts/diagram-composition-colors-contract.md
$RunId = "diagram-colors-20260928-$Case-$Attempt"
uv run --script scripts/run-pi-skill-eval.py diagram-composition --prompt-file $Prompt --model openai-codex/gpt-5.6-luna --mode json --strict --timeout-seconds 900 --run-id $RunId --expect-output out/plan.json --expect-output out/figure.svg --expect-output out/report.json --expect-output out/audit.json --expect-output out/preview.png --expect-output out/review.md --expect-output-json-field out/audit.json::ok=true --expect-output-json-field out/audit.json::semanticColors.status=checked
uv run --script scripts/summarize-pi-json-events.py "evaluations/runs/$RunId/events.jsonl" --require-model gpt-5.6-luna --fail-on-invalid-json --fail-on-tool-error
uv run --script skills/diagram-composition/scripts/audit_diagram.py audit --input "evaluations/runs/$RunId/workspace/out/figure.svg" --report "projects/diagram-composition/artifacts/reviews/colors-$Case-$Attempt.json" --screenshot "projects/diagram-composition/artifacts/images/colors-$Case-$Attempt.png" --overwrite
uv run --script evaluations/contracts/check-diagram-colors.py "evaluations/runs/$RunId" --case $Case --browser-report "projects/diagram-composition/artifacts/reviews/colors-$Case-$Attempt.json" --output "evaluations/diagram-composition/colors-$Case-$Attempt-artifact.json"
```

Use a new run ID for reproduction; never overwrite historical runs. The contract
prompt SHA-256 is `7f105d07c70e54f724d24826c01dbad00dbf0d87ec2235e2e31a1d7aa8e3e4b6`;
the naturalistic prompt SHA-256 is
`1d9475bc1ee204d418ebccf6d63b46cc089686729983e7e41e844a2f2999988e`.

## Local example and release checks

The illustrative Copilot/Claude/cloud figure now uses one consistent semantic
outline per tool in the hub, matrix, synthesis, and shared legend. All nine panel
occurrences and three legend occurrences match their registry. Its independent
browser audit reports zero issues or clipped marks, 32 text elements, and a
15px minimum at 1280px display width. Official logos were preserved. The final
screenshot was visually inspected.

```powershell
uv run --script projects/diagram-composition/scripts/build_demo.py --skill-root skills/diagram-composition --artifacts projects/diagram-composition/artifacts
uv run --script skills/diagram-composition/scripts/audit_diagram.py audit --input projects/diagram-composition/artifacts/svgs/workspace-composition.svg --report projects/diagram-composition/artifacts/reviews/workspace-audit.json --screenshot projects/diagram-composition/artifacts/images/workspace-preview.png --overwrite
uv run --script scripts/validate-pattern-ids.py
uv run --script scripts/validate-skills.py
uv run --script scripts/test-skill-independence.py
uv run --script scripts/check-repo-payload.py
uv run --script scripts/sync-local-skills.py --source skills/diagram-composition --destination .agents/skills/diagram-composition
uv run --script scripts/sync-local-skills.py --source skills/diagram-composition --destination .agents/skills/diagram-composition --check
```

Pattern, structure, independence, and payload gates pass. Generated media remains
under the ignored project artifacts directory. Local sync/check matches all 16
canonical files. No Pages example was introduced.
