# D3 authoring validation closeout — 2026-10-02

The named speculative-decoding recipe now passes the previously unmet behavior
gate. A single frozen runtime candidate produces eight strict isolated passes
and eight independent browser/manual passes. Naturalistic and generalization
cohorts each pass 3/3; the command contract and zero/full-prefix boundary pass
1/1 each. The [machine evidence](20261002-d3-validation.json) records the
candidate hash, manifests, exact artifacts, commands, read surfaces and checks.

## Change and authoring rationale

The failed capture cohort had functional colors outside the palette, HTML
control requirements applied to a captured SVG, and a final progress dot over
the rejected token. More prose alone did not make the recipe reliable.

The bundle now includes a parameterized
[`build_speculative_decoding.py`](../../skills/d3/scripts/build_speculative_decoding.py).
It preserves literal proposal order, prefix count, target continuation,
dimensions, colorset and optional alternates. It emits offline HTML and portable
SVG together using the canonical palette and native finite animation. The
target continuation originates at the last accepted context; a separate marker
rail preserves text visibility and removes its marker at settlement. Alternate
connectors avoid the draft-position labels.

The focused
[`verify_speculative_decoding.py`](../../skills/d3/scripts/verify_speculative_decoding.py)
declares its Playwright dependency, uses installed Edge/Chrome when managed
Chromium is absent, clicks Replay twice, checks final/reduced-motion text and
matching SVG viewports, and writes the inspection PNG. This replaces the
observed ad hoc iframe replay test without relying on external repository
resources. The direct recipe differentiates HTML controls, portable SVG
structure and evaluation-report flags.

The constructor is bounded to a linear proposal with 1–12 tokens and one
alternate per draft position, subject to readable fit. Unsupported structures
retain the compact source-excerpt/custom-geometry workflow. The change does not
restrict the skill's other charts, simulations, typography, logos or recipes.
Published example sources, canonical pattern IDs and historical Harbor study
records are unchanged. This is a focused behavior patch, not a new Harbor
evolution or holdout claim.

## Deterministic and browser checks

```powershell
uv run --script skills/d3/scripts/test_speculative_decoding.py
uv run --script skills/d3/assets/examples/skill-tests/test_palette_contract.py
uv run --script scripts/validate-pattern-ids.py
uv run --script scripts/validate-skills.py
uv run --script scripts/test-skill-independence.py
uv run --script scripts/check-repo-payload.py
uv run --script scripts/test-pi-eval-harness.py
uv run --script scripts/test-bundle-validation.py
uv run --script skills/repository-reviewer-creator/scripts/test_skill_authoring.py
uv run --script skills/repository-reviewer-creator/scripts/test_validate_reviewer.py
```

The new suite passes 12 tests covering ordered literal data, Unicode/XML
escaping, repeated tokens, both palettes, exact files and deterministic reruns,
changed dimensions and branches, zero/full acceptance, invalid-input no-write
behavior, portable SVG, finite marker lifetime, positive browser checks,
missing Replay, incompatible viewports and input/output conflicts. The existing
palette suite passes seven tests; the authoring/copy/generator/harness suites
pass 88 combined tests.

The evaluator-owned
[`check-d3-decoding.py`](../contracts/check-d3-decoding.py) inspects both formats
at 0, 0.45, 1.25, 2.25, 3.4 and 20 seconds. It checks actual glyph hit points
for later painted obstructions, text envelopes, exact tokens/alternates,
visible motion, Replay twice, initial/final reduced-motion text, accessibility,
viewBox, static palettes, offline requests and browser errors. Manual review
checks prefix/tail semantics, resumption source, visual hierarchy and readable
captions. Naturalistic/transfer artifacts are byte-identical across their
respective repetitions; every repetition also receives independent checks.

The old capture repetition `20261002-authoring-d3-capture-luna-2` is an explicit
negative control: the new independent grader rejects its obscured token during
motion, settlement, replay and reduced motion. That artifact was accepted by
the earlier mechanical grader and rejected during manual inspection. Its
failure remains recorded.

## Frozen forward cohort

All final runs use `openai-codex/gpt-5.6-luna`, high reasoning, strict JSON,
fresh isolated runtime workspaces and an unchanged 285-file payload:

`163ac42cc33cc9142ffde1969cdc8c4bf2e59b0ce3ec4a210f7b0918c4c1f540`

The existing backlog's model exception is retained because the provider
rejected Spark before tools. No criteria were relaxed and no model was switched
to rescue these cases. Claude model families were not tested.

| Case | Final run ID suffixes after `20261002-authoring-d3-verified-` | Strict / artifact / manual / joint | Required |
| --- | --- | --- | --- |
| Contract | `contract-luna-1` | 1 / 1 / 1 / 1 | 1/1 |
| Naturalistic | `natural-luna-1`, `-2`, `-3` | 3 / 3 / 3 / 3 | At least 2/3 |
| Generalization | `transfer-luna-1`, `-2`, `-3` | 3 / 3 / 3 / 3 | At least 2/3 |
| Boundary | `boundary-luna-1` | 1 / 1 / 1 / 1 | 1/1 |

The boundary produces two pairs of artifacts: zero accepted tokens and all
accepted tokens. There are 18 exact output files across the eight runs.

Run commands use this form, with the matching prompt, suffix and exact outputs:

```powershell
uv run --script scripts/run-pi-skill-eval.py d3 --prompt-file evaluations/pi-prompts/d3-authoring-direct-recipe.md --model openai-codex/gpt-5.6-luna --mode json --strict --run-id 20261002-authoring-d3-verified-natural-luna-1 --timeout-seconds 480 --expect-output out/decode.html --expect-output out/decode.svg
uv run --script evaluations/contracts/check-d3-decoding.py --run-id 20261002-authoring-d3-verified-natural-luna-1 --case naturalistic --report projects/skill-authoring-audit/artifacts/reviews/d3-verified-natural-independent.json
uv run --script scripts/summarize-pi-json-events.py evaluations/runs/20261002-authoring-d3-verified-natural-luna-1/events.jsonl --require-model gpt-5.6-luna --fail-on-invalid-json --fail-on-tool-error
```

Other prompts are
[`d3-authoring-builder-contract.md`](../pi-prompts/d3-authoring-builder-contract.md),
[`d3-authoring-builder-generalization.md`](../pi-prompts/d3-authoring-builder-generalization.md)
and [`d3-authoring-builder-boundary.md`](../pi-prompts/d3-authoring-builder-boundary.md).
The original [naturalistic prompt](../pi-prompts/d3-authoring-direct-recipe.md)
remains unchanged. The model reads only the prompt, D3 entrypoint, focused
decoding recipe and its own generated files/preview; any additional focused
references are enumerated in the machine trace record. No fixture, sibling
skill, repository documentation or source mutation passes the strict policy.

## Retained development evidence

All original failed cohorts remain in
[`20261002-forward-evidence.json`](20261002-forward-evidence.json).
The first constructor revision produced contract 1/1, naturalistic 3/3 and
generalization 3/3 strict/artifact passes. Manual inspection then improved branch
connector clearance. Its boundary produced correct media but two failed tool
operations in an invented iframe replay test, so it remains a strict failure.
The browser verifier was added to the reusable bundle before the fresh final
cohort. Preliminary successes are not counted toward the final threshold.

Original deterministic setup errors while developing the helper (a wrong
palette JSON level and invalid local validator CLI usage) were corrected before
the frozen cohort. They are local development failures, not agent passes.
Non-LLM smoke workspaces are kept separate from model attempt counts.

## Authoring and distribution closeout

The [final actual-bundle audit](20261002-bundles-validated.json) checks all 34
sources and 68 runtime/full copies, with exact profile hashes and no findings.
The final D3 runtime hash matches every final model manifest. The
[`20261002-bundles-closeout.json`](20261002-bundles-closeout.json) snapshot was
an earlier valid constructor revision and is superseded by the final audit.

```powershell
uv run --script scripts/audit-skill-authoring.py --check-bundles --output evaluations/skill-authoring/20261002-bundles-validated.json
uv run --script scripts/sync-local-skills.py
uv run --script scripts/sync-local-skills.py --check
uv run --script scripts/build-pages.py
uv run --script scripts/test-pages-output.py
uv run --script scripts/validate-pages-pattern-format.py
git diff --check
```

Local Pages builds retain 646 files, 45.61 MiB and 14 published entries. Build
output stays under `dist/pages/`; all three boundary tests pass. No published
example or URL changed. The summary closes D3's new validation gap and leaves
unrelated skill release limits attached to their own backlog records.
