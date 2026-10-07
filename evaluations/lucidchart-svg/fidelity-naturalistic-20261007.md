# Lucidchart SVG fidelity: naturalistic validation

Date: 2026-10-07. Case: `naturalistic-forward`, using [lucidchart-svg-fidelity-naturalistic.md](../pi-prompts/lucidchart-svg-fidelity-naturalistic.md). Model: `openai-codex/gpt-5.6-luna`, thinking `high`, under the already recorded Spark/provider exception. The prompt is offline and provides no Lucid session, credentials, service screenshot, or import result.

The final documentation bundle passes this naturalistic case **2/3** after independent artifact and factual-report review. All three final runs pass strict harness, exact-output, trace, and payload-integrity gates. Final repetition 1 retains a source-style factual error in its fidelity ledger and is classified as an **agent** failure. No run was rerolled and no generated result was repaired.

## Frozen payloads and attempts

All runs use the runtime profile with 10 copied bundle files. Prompt SHA-256: `40e3bd56c4415079259df5722f500264caf4b92270154392ca0d97eb79c62846`.

- Before the editorial clarification: `9b44effcffd8a0901506aefacdab0d5074fb067116e2d52d77667e01bb09586e`.
- Final documentation: `788b6401bc2f42f14e05bc1f86930a3f144044ad9c49f684d7bb33cdbfa454aa`.

The change between cohorts only clarified that an unstroked SVG path can still have a visible fill; it changed no compiler or inspector behavior. The first cohort had already completed and is retained as pre-clarification evidence, separate from final acceptance.

| Run ID | Payload phase | Seconds | Strict harness / trace | Independent result |
| --- | --- | ---: | --- | --- |
| [`20261007-lucid-svg-fidelity-natural-luna-1`](../runs/20261007-lucid-svg-fidelity-natural-luna-1/independent-artifact-review.json) | Before clarification | 45.322 | Pass / pass | Pass |
| [`20261007-lucid-svg-fidelity-natural-luna-2`](../runs/20261007-lucid-svg-fidelity-natural-luna-2/independent-artifact-review.json) | Before clarification | 76.397 | Pass / pass | Pass |
| [`20261007-lucid-svg-fidelity-natural-luna-3`](../runs/20261007-lucid-svg-fidelity-natural-luna-3/independent-artifact-review.json) | Before clarification | 46.895 | Pass / pass | Pass |
| [`20261007-lucid-svg-fidelity-natural-final-luna-1`](../runs/20261007-lucid-svg-fidelity-natural-final-luna-1/independent-artifact-review.json) | Final | 90.916 | Pass / pass | Fail: inaccurate border-style ledger |
| [`20261007-lucid-svg-fidelity-natural-final-luna-2`](../runs/20261007-lucid-svg-fidelity-natural-final-luna-2/independent-artifact-review.json) | Final | 41.685 | Pass / pass | Pass |
| [`20261007-lucid-svg-fidelity-natural-final-luna-3`](../runs/20261007-lucid-svg-fidelity-natural-final-luna-3/independent-artifact-review.json) | Final | 78.790 | Pass / pass | Pass |

Each linked independent review records the exact output inventory and hashes, 41 structural checks, manually assessed fidelity-note conclusions, and complete shell commands. Each run directory also preserves `run-manifest.json`, `evaluation-result.json`, `event-check.json`, `skill-integrity-check.json`, `read-surface-review.json`, `events.jsonl`, and the original generated outputs. All attempted repetitions remain available.

## Commands and output contract

Run from the repository root, once per listed run ID:

```powershell
uv run --script scripts/run-pi-skill-eval.py lucidchart-svg `
  --prompt-file evaluations/pi-prompts/lucidchart-svg-fidelity-naturalistic.md `
  --mode json --strict --model openai-codex/gpt-5.6-luna --thinking high `
  --run-id <listed-run-id> `
  --expect-output input/styled.svg `
  --expect-output deliver/artwork.svg `
  --expect-output deliver/inspection.json `
  --expect-output deliver/graph.json `
  --expect-output deliver/native.lucid `
  --expect-output deliver/document.json `
  --expect-output deliver/fidelity.md

uv run --script scripts/summarize-pi-json-events.py `
  evaluations/runs/<listed-run-id>/events.jsonl `
  --output evaluations/runs/<listed-run-id>/read-surface-review.json `
  --require-model gpt-5.6-luna --require-tool-call --require-read ../prompt.md `
  --fail-on-invalid-json --fail-on-tool-error `
  --forbid-read-regex '(?i)(^|[\\/])assets[\\/]examples([\\/]|$)' `
  --forbid-read-regex '(?i)^skills[\\/](?!lucidchart-svg([\\/]|$))'
```

The prompt specifies six delivery paths plus `input/styled.svg`, seven required outputs in total. Independent evaluator-side Python (`uv run python -`) compared source bytes, parsed SVG/graph/document data with ElementTree/JSON, and inspected ZIP bytes and members. The reviewer then read every generated `deliver/fidelity.md` in full; acceptance judged actual source-versus-output claims rather than regex wording.

## Independent findings

All six attempts preserve the source content, with the optional final newline and line-ending representation normalized for the verbatim-source check. Every prepared artwork file is an exact byte copy of its input: 1,009 bytes, SHA-256 `b49414000f733371799ad14d6914d47c795aa85bb6943dfcf54e8cc799e13146`.

Every recovered graph and native document has two exact labels (`Request & check`, `Store <P1>`), request bounds `(20,50,120,60)`, store bounds `(220,50,140,60)`, the specified solid fill/border/text colors, 20px text size, and one directed `request -> store` edge with explicit `(1,0.5)` to `(0,0.5)` ports. The `.lucid` ZIP contains only `document.json`, matching the emitted document bytes exactly; ZIP integrity passes.

Actual substitutions are consistent in all outputs: corner radii disappear; borders become 1px solid; Georgia bold/italic labels become centered Liberation Sans; the maroon dashed cubic connector and custom marker become a straight black 1px solid destination arrow; grouping is flattened; and the source `400x180` frame becomes a white `392x142` page. Source geometry is retained in the artwork bytes, while actual Lucid parsing and font/rendering behavior remain untested.

Final repetition 1 incorrectly describes the two source borders as “both dashed.” The supplied SVG declares `stroke-dasharray="5 3"` on request only; store has no dash declaration or inherited dashed style. Its [unaltered fidelity note](../runs/20261007-lucid-svg-fidelity-natural-final-luna-1/workspace/deliver/fidelity.md) therefore reports losing a store dash pattern that did not exist. Structural artifacts remain correct, but that factual ledger error fails the appearance-sensitive reporting criterion. The source and skill guidance were sufficient, so the failure is classified as `agent`, without a bundle repair or reroll.

All notes correctly qualify the local/live boundary, avoid an overall visual-fidelity percentage, and state that the artifacts are prepared local candidates rather than completed Lucid uploads. Shell review found bundled helper invocation and local artifact verification only. Read surfaces consist of the prompt, entry point, focused native/fidelity/editor references, and task outputs; there are no acceptance-fixture, sibling-skill, or ambient repository reads, and no payload modifications or tool errors.

## Scoped acceptance and remaining boundaries

The same final payload also passes the root-reviewed [contract run](../runs/20261007-lucid-svg-fidelity-contract-final-luna-1/evaluation-result.json). Current scoped acceptance is therefore contract **1/1** plus naturalistic **2/3**, or **3/4** after independent review; strict harness and structural artifact checks pass **4/4**. The final naturalistic case meets the repository's two-of-three threshold while preserving the failed attempt transparently.

This validation covers local preparation and accurate discussion of compiler substitutions. It supplies no service import, exported Lucid SVG, visual comparison, font-substitution check, or live native editability evidence. The skill remains `validating` for those live boundaries. No skill source, script, canonical backlog, or generated task output was changed by this evaluator.
