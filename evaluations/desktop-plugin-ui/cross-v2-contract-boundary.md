# Cross-assistant v2 contract and boundary validation

Date: 2026-10-24 America/New_York / 2026-10-25 UTC. Model:
`openai-codex/gpt-5.6-luna`, high thinking, Pi 1.4.0; existing documented Luna
exception. Both cases used strict JSON mode and a fresh isolated runtime copy.
No Claude or Copilot inference occurred during these evaluations.

The same 15-file payload was frozen for both cases:

`455db7f6daee26026e3c3be314406baf2f19a9e3c31c2250f09fc4d978389c05`

The v2 change made canonical evidence labels explicit in machine-readable
historical records and narrowed the OpenAI-registered server MRTR wording.
Prompts and the original evaluator criterion remained unchanged.

| Case/run | Strict result | Independent result | Manual review | Outcome |
| --- | --- | --- | --- | --- |
| `20261024-desktop-ui-cross-v2-contract-luna-1` | Fail: one source-check tool error | Final artifact/source checks pass; aggregate fails strict/events gates | Bounded source-repaired final output; no release acceptance | Retained citation-copy/workflow failure |
| `20261024-desktop-ui-cross-v2-boundary-luna-1` | Pass | Pass, 12 canonical patterns | Pass | Accepted boundary case for v2 |

## Contract failure retained

Pi exited zero and both exact outputs, JSON booleans, and payload integrity
passed. The initial source check with `--fail-on-findings` rejected one copied
elicitation citation because the agent wrote the `.org` domain instead of the
bundled `.io` domain. The agent repaired it to the exact catalog URL and the
second source check passed. The strict event gate correctly retains the first
tool error; later repair does not erase it.

Classify the initial citation mistake as `agent`, with a workflow difficulty
around using a failing CI mode during iterative report repair. Do not count the
final source-repaired artifacts as a clean strict run. The required-model trace
summary also returns failure for the retained tool error. It shows zero invalid
JSON lines and the expected Luna model. No ambient source or external operation
was involved.

The final contract artifacts contain 30 canonical patterns, complete expected
fields, five-host coverage, scoped historical evidence labels, and exact source
links. Independent grading reports only `Strict harness result failed` and
`events gate failed`. Following gate order, no full release-level semantic
acceptance is inferred after that earlier failure.

## Boundary review

The v2 boundary artifact now includes canonical evidence labels within each
historical evidence field. It correctly retains unresolved product identity,
separates actual Chat paint from native engine/terminal/extension-host/protocol
evidence, and rejects universal DOM, mode, device, and cancellation assumptions
at their proper surfaces. It preserves text/data and owned-client alternatives.
No factual or citation defect was found.

The grader's broad-exclusion review cue, `Codex has no UI`, occurs in the
explicitly negated sentence "not a claim that Codex has no UI." Manual review
dismissed the cue; it is not an actual broad exclusion. Both agent and evaluator
source checks passed on both final boundary artifacts. Current-task product
confirmation/host acceptance/empirical-test booleans remain false.

Boundary trace: expected Luna model, zero invalid JSON, zero tool errors,
14 read paths comprising `../prompt.md` and copied bundle material only.
Shell calls were only the bundled source checker. No fixture gallery, prior
run, sibling skill, repository document, network, account, or external app
was accessed. Payload remained unchanged.

## Exact outputs

| Case | Workspace-relative path | SHA-256 |
| --- | --- | --- |
| Contract | `results/cross-reference.md` | `7ad897f4a20b3e86d48e6595ea3d5bea7e17bb66ef137d0fc846fc0c0f1e0a09` |
| Contract | `results/cross-decisions.json` | `f229c0e4ce3a60184c958fc99cbd7b5aa8a61e3f0b74f9dd61d05e649956fa09` |
| Boundary | `review/cross-boundaries.md` | `db92ef14c88b2065a1680c9f004eeb3ae03aa3bb6b717b08bf550d710f3bf7ec` |
| Boundary | `review/cross-status.json` | `7c27313a6e940c940d7a841ec70c058cc653a5f45676779041dca009d566be8c` |

## Aborted rerun excluded

An attempted `20261024-desktop-ui-cross-v2-contract-luna-2` launch began just
before root's instruction against same-payload rerolling arrived. It was
interrupted immediately on receipt with Ctrl-C. Preserve its prompt, manifest,
and workspace as an aborted attempt; it produced no evaluation result or
accepted grade. A later process inventory found no remaining process from its
launch window. No same-payload favorable reroll is used in the evidence.

## Commands and evidence

The exact harness command arrays, prompt hashes, outputs, and frozen payload
hash are preserved in each `run-manifest.json`. These cases use the same
commands recorded in [the v1 review](cross-v1-contract-boundary.md), replacing
`cross-v1-` with `cross-v2-` in run IDs only; prompt paths, model, strict mode,
exact expected output paths, and JSON boolean assertions are unchanged.

```powershell
uv run --script scripts/summarize-pi-json-events.py evaluations/runs/20261024-desktop-ui-cross-v2-contract-luna-1/events.jsonl --require-model gpt-5.6-luna --fail-on-invalid-json --fail-on-tool-error --output evaluations/runs/20261024-desktop-ui-cross-v2-contract-luna-1/read-surface.json
uv run --script scripts/summarize-pi-json-events.py evaluations/runs/20261024-desktop-ui-cross-v2-boundary-luna-1/events.jsonl --require-model gpt-5.6-luna --fail-on-invalid-json --fail-on-tool-error --output evaluations/runs/20261024-desktop-ui-cross-v2-boundary-luna-1/read-surface.json
uv run --script evaluations/desktop-plugin-ui/inspect_cross_runs.py --prefix 20261024-desktop-ui-cross-v2-contract- --output evaluations/runs/20261024-desktop-ui-cross-v2-contract-independent.json
uv run --script evaluations/desktop-plugin-ui/inspect_cross_runs.py --prefix 20261024-desktop-ui-cross-v2-boundary- --output evaluations/runs/20261024-desktop-ui-cross-v2-boundary-independent.json
```

Raw JSONL, stderr, final artifacts, source-check failure/repair, strict gates,
and copied payloads remain under the original ignored run folders. Do not
replace their results with later cohorts.
