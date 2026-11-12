# Impeccable-informed refinement — 2026-11-12

Reviewed primary source at
[`pbakaus/impeccable@b4bff1626c344067788c2679f048a20057c7cc5a`](https://github.com/pbakaus/impeccable/tree/b4bff1626c344067788c2679f048a20057c7cc5a),
committed November 11, 2026. The [lesson map](../../docs/plugin-ui-impeccable-review.md)
records the exact source references and what was adapted. This was a selective
source review followed by independently implemented checks, not an invocation
of the upstream critique command or detector. No upstream code was copied into
the skill bundles. See [machine-readable evidence](impeccable-20261112.json).

## Design assessment before mechanical checks

The existing taxonomy micro UI already had the correct decision scope. Four
local refinements were identified before reading new mechanical results:

1. The subject nodes reused the strong action fill, reducing the distinction
   between what was being judged and what the user was about to do.
2. Fixed reading text needed browser-relative roles and a text-scaling path.
3. The generic action label omitted the chosen parent.
4. Pointer selection displayed an additional keyboard-style focus frame.

Kept the question, two alternatives, evidence and typed result unchanged. The
updated subject uses ink/outline and weight; selection and the enabled action
retain the accent. The action names the parent. Reading text starts at 1rem,
with dense reason/diagram roles separately justified. Oversized diagram labels
switch to an equivalent text tree. Pointer and keyboard focus are distinct.

## Executed evidence

- Existing browser/domain/MCP/SDK suite: **25/25** after the changes, with raw
  report at `projects/plugin-ui-micro-decisions/artifacts/reviews/browser/impeccable-first/review.json`.
- Targeted local quality checks: **14/14**, including real computed text
  contrast, readable neutral disabled state, associated radio hit areas,
  semantic emphasis, contextual action copy, pointer/keyboard focus, no added
  navigation and 200% root-font scaling at 542/320px. This is font scaling, not
  browser UI zoom. Raw report:
  `projects/plugin-ui-impeccable-review/artifacts/reviews/quality/review.json`.
- Actual integrated-browser capture: **542x767**, 16px browser-default root,
  one heading, zero global navigation, a neutral outlined subject and
  `Use Data integration` action. The image remains under ignored project artifacts.
- Native Pi source was unchanged. Its previous actual terminal captures and
  semantic theme checks are separate evidence; no new native acceptance is
  inferred from this web refinement.

The local reproduction command is:

```powershell
node projects/plugin-ui-impeccable-review/scripts/check-micro-quality.mjs
```

It uses the pinned Playwright dependency of the micro-decision project. Start
that project's loopback preview on port 8876 first.

## Seven independent skill bundles

Each existing `references/micro-decisions.md` now includes a compact craft pass
and local contents navigation. The additional guidance preserves the one-
decision default, host controls/themes and meaningful graph nodes. It does not
introduce a mandatory style package, new context files, global configuration,
new UI surfaces or blanket font/card/color bans. References remain below 10 KB.

Release forwards use one focused contract case per skill, with:

```powershell
uv run --script scripts/run-pi-skill-eval.py <skill> --prompt-file evaluations/pi-prompts/impeccable-ui-<skill>-contract.md --model openai-codex/gpt-6.1-sol --thinking medium --mode json --strict --expect-output quality-review.json --run-id 20261112-impeccable-ui-<skill>-sol-2 --timeout-seconds 360
uv run --script scripts/summarize-pi-json-events.py evaluations/runs/20261112-impeccable-ui-<skill>-sol-2/events.jsonl --require-model gpt-6.1-sol --fail-on-invalid-json --fail-on-tool-error
```

All seven strict runs and trace summaries passed: exact output, requested model,
valid events, zero tool errors, unchanged copied payload and clean runtime read
surface. Independent review confirmed the five required JSON keys, fewer than
750 words (585–680), design-before-metrics order, targeted role fixes, host
exceptions and honest unexecuted gates. The Sol/medium exception follows the
earlier recorded Spark account rejection. These are single contract cases, not
a generalization rate or proof of stock-host paint/continuation.

The seven `sol-1` launch attempts stopped at the source preflight because the
expanded references exceeded 100 lines without contents navigation. No model
started. Those logs are retained separately; adding the local contents sections
resolved the authoring issue before the seven model trials. Do not pool them
with runtime/model failures or with earlier frozen cohorts.

All seven skills remain `validating` where live host/account/deployment checks
remain open. The prior Claude/ChatGPT/Gemini boundaries remain unchanged.

## Repository gates

The clean main publication passes pattern IDs (1,348), full skill validation,
independence, payload, an 8-skill/16-bundle frozen authoring audit and the explicit
diff whitespace check. Scoped installation matches all 164 source files after
updating seven references, preserving other installed skills. The user worktree
passes pattern/independence/payload checks; four unrelated semantic-skill
authoring-route findings are preserved and excluded from this publication.
