# Mermaid compact composition review — 2026-09-27

## Scope and result

This is a focused revision of Mermaid's default composition. It reduces native box whitespace, keeps readable text, and makes colorset1 prioritize white, gray, black, and red. Pink is a documented last-resort additional category; none of the standard generated family themes, nine semantic roles, or twelve indexed slots needs it.

The source is `skills/mermaid/`. Reusable guidance is in `references/compact-composition.md`, with the core policy also present in `SKILL.md` and the selection and capacity references. The local installation was synchronized with the canonical source. No published gallery source changed.

## Implementation

- Flowchart uses native `padding: 6`, `nodeSpacing: 24`, and `rankSpacing: 32`. The group title margin reserves space above compact nodes.
- Class, Sequence, ER, State, Mindmap, Block, and Requirement receive appropriate native compact options. Mermaid 11.16.0 State v2 needs the shared Flowchart spacing; ER uses `diagramPadding` inside empty entity boxes and `entityPadding` in attribute tables. ER retains enough separation for cardinality markers and relationship labels.
- Standard unclassified boxes use white with a red outline. `csPrimary` is brand red with white text, critical uses a red outline, success uses dark ink with white text, and secondary roles use neutrals.
- The former pink terminal scale entry is gray 200. All twelve indexed colors remain distinct. Black is an available label color so all twelve standard scale color/label pairs and all nine semantic class pairs reach at least 4.5:1 contrast.
- Explicit authored spacing, zero values, comments, and nested configuration survive restyling. Missing block-map fields receive defaults. Inline maps, aliases, and merge maps remain complete overrides. Repeated styling and colorset switching are stable.

## Rendered comparison

The comparison uses identical source facts and Mermaid CLI 11.16.0. The browser measures native SVG bounds, actual shape bounds, and label font sizes. Each before/after screenshot uses a shared display scale.

| Case | Before height | After height | Reduction |
| --- | ---: | ---: | ---: |
| Five-step vertical flow | 486 px | 324 px | 33.33% |
| Branching flow with recovery | 185.16 px | 134.16 px | 27.54% |
| Multiline labels and a group | 424 px | 332 px | 21.70% |
| Sequence | 347 px | 265 px | 23.63% |
| State | 388 px | 316 px | 18.56% |
| Class | 524 px | 416 px | 20.61% |
| ER without attribute rows | 470 px | 344 px | 26.81% |
| Nine semantic roles | 902 px | 532 px | 41.02% |

The vertical flow's individual rectangles change from 54 to 36 pixels high. Label text remains 16 pixels. The nine comparisons, including a twelve-category Mindmap, pass browser error, exact-pink-fill, and group-title overlap checks. Flowchart labels retain shape clearance. Screenshots were inspected for labels, routing, group titles, role colors, and ER cardinalities. These measurements describe these fixtures, not a universal shrink ratio.

Local artifacts: `projects/mermaid-composition/artifacts/comparison/index.html`, `metrics.json`, `review.json`, and the per-case PNG/SVG files. The baseline styler snapshot is under `artifacts/baseline/`; its SHA-256 is `c009b548a248309573920a150ec01cf93417f944f020de0e42aadf5c367c519c`. The starting repository commit was `8d5699f88526633160a082ef55cd65135ea9d863`.

## Deterministic gates

- 10 new composition tests pass: default geometry, all-family absence of generated pink, semantic color/contrast, twelve-slot capacity/contrast, both colorsets, idempotence, partial/complete maps, quoted keys, aliases, and merge overrides.
- Existing maximum-capacity tests: 12/12 pass. Metadata tests: 8/8. Editorial semantic verifier tests: 9/9. Visual palette tests: 2/2.
- Full family regression: 31 families, 25 finite cases, 200 finite slots, 62 styled diagrams, 62 SVG renders, and 11 cyclic contracts; zero findings in `artifacts/all-families-final-report.json`.
- Pattern IDs, skill structure, independence, payload, quick skill validation, Python compilation, and diff checks pass. Pi harness tests pass 14/14.
- Local synchronization/check matches 229 canonical Mermaid files.

## Isolated forward tests

The initial cohort used the read-only runtime payload: 18 files, SHA-256 `0251ae01eb5152be231fb71368e4362141d19405718864da727fd5614f0f47ba`. Model exception: `openai-codex/gpt-5.6-luna`, medium thinking. The required Spark attempt was rejected by the provider before any tool call because the ChatGPT account does not support Spark.

| Run ID suffix after `mermaid-compact-` | Outcome | Classification / evidence |
| --- | --- | --- |
| `contract-20260927-spark-1` | Blocked before execution | Infrastructure; unsupported model, zero tool calls. |
| `contract-20260927-luna-1` | Strict gate failed; artifacts correct | Harness prompt used a `powershell` fence, which the exact-command extractor does not recognize. The trace did run the exact command. Retained; corrected only the reusable prompt fence to `sh`. |
| `contract-20260927-luna-2` | Pass | All exact paths, literal command, JSON fields, model/events, zero tool errors, confined reads, unchanged payload. |
| `naturalistic-20260927-luna-1` | Pass | Correct seven-node shipment workflow, six relationships, primary storage emphasis, metadata, and native compact styling. |
| `naturalistic-20260927-luna-2` | Strict gate failed; final artifact correct | Agent combined mutually exclusive `--write --check`, received a tool error, then recovered. Retained as a failure. |
| `naturalistic-20260927-luna-3` | Pass | Same independent requirements as repetition 1. |
| `boundary-20260927-luna-1` | Pass | Authored padding 18, node spacing 70, rank spacing 90, and linear curves remain intact. |
| `generalization-20260927-luna-1` | Strict gate failed; final artifact correct | Agent checked the unstyled source before applying the styler, then recovered. |
| `generalization-20260927-luna-2` | Strict gate failed; final artifact correct | Agent combined `--write --check`, then recovered. |
| `generalization-20260927-luna-3` | Strict gate failed; final artifact correct | Agent checked the unstyled source before applying the styler, then recovered. |

The initial naturalistic cohort passed 2/3 strict repetitions, but the generalization cohort failed 0/3. This repeated failure justified clarifying workflow steps 5 and 6: apply `--write` first, including for hand-styled sources, then use `--check` in a separate command. No failure was discarded or counted as a strict pass. All initial final artifacts pass independent inspection, but that does not override strict trace failures.

The final payload is 18 files, SHA-256 `9863be6b6e3f02bb0144e8ac227decd0c939abb481db2208dbfbdb6ec53333a1`. All eight fresh release runs pass strict execution and independent artifact validation:

| Final run IDs after `mermaid-compact-` | Strict result | Independent artifact result |
| --- | --- | --- |
| `contract-20260927-luna-final-1` | 1/1 pass | Correct native defaults, labels, relations, and metadata. |
| `naturalistic-20260927-luna-final-{1,2,3}` | 3/3 pass | Correct seven-node workflows, six relationships, primary storage emphasis, and metadata. |
| `boundary-20260927-luna-final-1` | 1/1 pass | Explicit padding, spacing, curve, and labels preserved. |
| `generalization-20260927-luna-final-{1,2,3}` | 3/3 pass | Correct ER schemas, eight typed/keyed attributes, two exact cardinalities, relationship labels, compact geometry, and metadata. |

The final artifacts pass independent SVG rendering, visible-label, exact spacing, relation-count, unique-ID, and resolved title/description checks. Source relations were reviewed against the supplied facts; screenshots confirm readable tables, the highlighted storage step, and retained custom spacing. Evidence is in `artifacts/final-forward-summary.json`, `artifacts/forward/review.json`, the eight per-run read summaries, and the SVG/PNG files. The final tested bundle is the locally synchronized source.

Read surfaces contain the prompt, skill entry point, compact composition reference, relevant selection/accessibility references, and the run's own outputs. No acceptance fixtures, sibling skills, or repository documentation were read. Final payload integrity passes. Raw evidence stays under `evaluations/runs/`; compact read summaries and external SVGs are under `projects/mermaid-composition/artifacts/`.

## Corrections during validation

- A first compact subgraph left insufficient room for the group heading. A native title margin fixed it, and a browser overlap check now guards the case.
- A first ER rank spacing of 48 placed cardinality markers too close to relationship labels. Restoring 80 retained the box padding benefit without that crowding.
- The first full-family run found black label colors absent from the palette's token registry. Explicit black tokens repaired the registry; the final 62 renders pass.
- The independent naturalistic validator initially demanded `Accepted?`, while the prompt supplied `Accepted`. A correct decision diamond used the exact supplied label. Corrected the validator to accept that label with an optional question mark; retained the prior report as `artifacts/forward/review-before-label-fix.json`. No agent artifact changed for this correction.
- The comparison Mindmap rejected `accTitle`/`accDescr` as multiple roots in this pinned renderer. It is a palette-only probe without an accessibility pass claim; all isolated forward cases use families with rendered metadata support. No accessibility behavior changed in this revision.

## Reproduction

```sh
uv run --script evaluations/mermaid/test_compact_composition.py
uv run --script skills/mermaid/assets/examples/mermaid-max-elements/scripts/test_max_elements.py
uv run --script evaluations/mermaid/test_editorial_accessibility.py
uv run --script evaluations/mermaid/test_editorial_queue_verifier.py
uv run --script evaluations/mermaid/test_visual_palette.py

uv run --script projects/mermaid-composition/scripts/verify_composition.py --cli <cached-mermaid-cli-11.16.0>/src/cli.js
uv run --script projects/mermaid-composition/scripts/verify_composition.py --cli <cached-mermaid-cli-11.16.0>/src/cli.js --full --run-name <fresh-name>
uv run --script projects/mermaid-composition/scripts/verify_forward_outputs.py --cli <cached-mermaid-cli-11.16.0>/src/cli.js --run-id <retained-run-id>

uv run --script scripts/run-pi-skill-eval.py mermaid --prompt-file evaluations/pi-prompts/mermaid-compact-contract.md --model openai-codex/gpt-5.6-luna --thinking medium --mode json --strict --require-exact-command-from-prompt --run-id <fresh-contract-run> --timeout-seconds 600 --expect-output deliverables/diagrams/intake.mmd --expect-output deliverables/style.json --expect-output deliverables/check.json --expect-output-json-field deliverables/check.json::missingStyleCount=0 --expect-output-json-field deliverables/check.json::missingAccessibilityCount=0
uv run --script scripts/run-pi-skill-eval.py mermaid --prompt-file evaluations/pi-prompts/mermaid-compact-naturalistic.md --model openai-codex/gpt-5.6-luna --thinking medium --mode json --strict --run-id <fresh-naturalistic-run> --timeout-seconds 600 --expect-output deliverables/shipment.mmd --expect-output deliverables/style-check.json --expect-output-json-field deliverables/style-check.json::missingStyleCount=0 --expect-output-json-field deliverables/style-check.json::missingAccessibilityCount=0
uv run --script scripts/run-pi-skill-eval.py mermaid --prompt-file evaluations/pi-prompts/mermaid-compact-boundary.md --model openai-codex/gpt-5.6-luna --thinking medium --mode json --strict --run-id <fresh-boundary-run> --timeout-seconds 600 --expect-output deliverables/manual-review.mmd --expect-output deliverables/check.json --expect-output-json-field deliverables/check.json::missingStyleCount=0 --expect-output-json-field deliverables/check.json::missingAccessibilityCount=0
uv run --script scripts/run-pi-skill-eval.py mermaid --prompt-file evaluations/pi-prompts/mermaid-compact-generalization.md --model openai-codex/gpt-5.6-luna --thinking medium --mode json --strict --run-id <fresh-generalization-run> --timeout-seconds 600 --expect-output deliverables/lending.mmd --expect-output deliverables/check.json --expect-output-json-field deliverables/check.json::missingStyleCount=0 --expect-output-json-field deliverables/check.json::missingAccessibilityCount=0
uv run --script scripts/summarize-pi-json-events.py evaluations/runs/<run-id>/events.jsonl --require-model gpt-5.6-luna --fail-on-invalid-json --fail-on-tool-error --output <summary.json>

uv run --script scripts/validate-pattern-ids.py
uv run --script scripts/validate-skills.py
uv run --script scripts/test-skill-independence.py
uv run --script scripts/check-repo-payload.py
uv run --script scripts/test-pi-eval-harness.py
uv run --with pyyaml python <skill-creator>/scripts/quick_validate.py skills/mermaid
uv run --script scripts/sync-local-skills.py --source skills/mermaid --destination .agents/skills/mermaid
uv run --script scripts/sync-local-skills.py --source skills/mermaid --destination .agents/skills/mermaid --check
git diff --check
```

The comparison baseline can be recovered from the starting commit's `skills/mermaid/scripts/style_mermaid_directory.py` and `references/diagram-types.json` into the corresponding paths under the local `artifacts/baseline/` directory. Use a fresh name for full-family render runs so prior evidence remains intact.
