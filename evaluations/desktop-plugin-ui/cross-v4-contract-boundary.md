# Cross-assistant v4 contract and boundary validation

Date: 2026-10-24 America/New_York / 2026-10-25 UTC. Model:
`openai-codex/gpt-5.6-luna`, high thinking, Pi 1.4.0, isolated runtime profile,
strict JSON. The existing documented Luna exception applies. No Claude or
Copilot inference was used for these advisory evaluations.

Both cases ran once after root's final coordinated freeze. The same 16-file
payload was copied, SHA-256:

`2b35617cd80abae02ad208d099c5d328d25d2f85c654fea1c9f10518ecb824ee`

Copied report helper SHA-256:
`68892c9952c6036c2e07cade284280282f4d97f7aef2f04be0395fd3a983e1b2`.
The predeclared separate v4 grader is documented in
[the checker/evaluator review](report-checker-v4-review.md). Original v1–v3
grader and results remain unchanged. Neither skill nor grader changed during
these runs; there were no same-payload favorable rerolls or manual repairs.

| Run | Strict harness | V4 independent result | Direct review/outcome |
| --- | --- | --- | --- |
| `20261024-desktop-ui-cross-v4-contract-luna-1` | Pass | Pass; 22 canonical patterns | Pass on facts, exact citations, evidence fields, five-host coverage, and useful rules |
| `20261024-desktop-ui-cross-v4-boundary-luna-1` | Fail: two edit-tool errors, Pi exit zero | Fail: strict/events plus empty sources for assessment zero | Final evidence/source checks pass; substantive facts remain bounded, but execution and artifact-format failures are retained |

Both exact-output, JSON false-boolean, observed-model, and copied-payload
integrity gates passed. Boundary cannot be counted as a clean strict release
case even though its final files were repaired by the evaluated agent.

## Contract direct review

The contract correctly distinguishes ordinary Claude Desktop Chat, Desktop
Code/native Mods, Claude terminal, Codex CLI/backend/custom frontend, ChatGPT,
and Copilot CLI versus VS Code MCP Apps/webviews/canvases. Its 22 canonical
patterns provide input, implementation rule, fallback, evidence, and concrete
validation. It covers native controls/previews, HTML Apps resources/bridge,
host-owned forms, images/artifacts, deployment, policy/cancellation, and
constrained investigations.

Historical observations preserve actual Claude Chat 3.6556.2 paint and direct
actions, Claude Code 2.1.302 engine-only checks, Codex 0.145.0 transport and
callbacks, actual Copilot terminal forms, real extension-owned webviews, and
ChatGPT setup/fixture evidence without claiming widget acceptance. Every
historical `evidence` field contains canonical lowercase observed-* labels
with scope. Current task acceptance/testing booleans remain false.

No invented source or material factual exclusion was found. Codex content,
callbacks, and an owned client are separated from stock iframe/pane acceptance;
the native Claude DOM restriction is not applied to ordinary Chat. Host
permission, cancellation, transport, and actual OS effects remain distinct.
Agent and independent `check_reports.py` checks passed on both final artifacts.

## Boundary retained failures and final state

The first diagnostic report check identified a citation domain mutation in
Markdown. Instead of using the supplied exact all-occurrence replacement
option, the agent attempted manual `edit` calls. One failed because its text
occurred twice; the next failed because the proposed old text did not match.
The agent subsequently repaired its final Markdown and reran the report
checker successfully. Strict mode correctly retains both failed tool calls.
Classify this as `agent` execution/workflow failure; do not erase it after
repair or reroll the same payload for a favorable grade.

The final JSON also has `assessments[0].sources: []` for the unresolved-product
identity topic. The original nonempty-source acceptance criterion, retained
in the versioned v4 grader, flags it as an artifact-format gap. This is not a
fabricated citation or false product claim; the other assessments have exact
bundled primary sources. The helper validates actual citation URLs and
historical evidence fields, not the entire evaluator-owned report schema.

Final `check_reports.py` passes for both boundary artifacts, including each
historical `evidence` field. The content preserves Cloud ambiguity, scopes
native DOM and protocol failures, distinguishes fullscreen/device support by
host, treats cancellation as non-authorization, and does not promote lower
layers to actual paint. No additional material factual defect was found in
direct inspection. This bounded content result does not override the failed
earlier strict gate or the empty-source finding.

## Traces and source isolation

Both traces observe the required `gpt-5.6-luna` model and zero invalid JSON
lines. Contract has zero tool errors; boundary has exactly the two edit-tool
errors above, so its required-model trace summary exits one. Both read only
`../prompt.md` and copied bundle references. No fixture gallery, prior run,
sibling skill, repository documentation, outside-workspace source, network,
account/configuration, or external application operation was found.

The successful post-final-write report checks cover both artifacts. The
contract also satisfies its explicit original source-check command. Boundary
shell activity lists bundled sources, runs diagnostic report checks, and
locates the mutated domain with local `rg`; the failed actions are local edit
tool calls, not denied host UI operations. Payload digests remain unchanged.

## Exact outputs and hashes

Paths are relative to each run's `workspace/`.

| Case | Artifact | SHA-256 |
| --- | --- | --- |
| Contract | `results/cross-reference.md` | `9cbc57000fc0125cdd451307e0b486ccd31c3839d0c9bfcc8abde0a28cc2bc10` |
| Contract | `results/cross-decisions.json` | `62156c44e288b4c2c74db4635b25f8095f183ae61cdbd06177b221d18ff759b7` |
| Boundary | `review/cross-boundaries.md` | `4086b91ee179f668cbfd64ef92b4954cbfa1ab0d2b84b337bdad7bf5225fde0e` |
| Boundary | `review/cross-status.json` | `689618a425fdef3ce60a3f738b9b23abe5de479e06f9ddc5325556fbf3a8462b` |

## Commands and evidence retention

Harness arguments are the same as the unchanged-prompt commands in
[v1](cross-v1-contract-boundary.md), with `cross-v4-` in the run ID. Every
expected path and task-level false boolean was asserted by the harness.
The v4-specific independent commands are:

```powershell
uv run --script scripts/summarize-pi-json-events.py evaluations/runs/20261024-desktop-ui-cross-v4-contract-luna-1/events.jsonl --require-model gpt-5.6-luna --fail-on-invalid-json --fail-on-tool-error --output evaluations/runs/20261024-desktop-ui-cross-v4-contract-luna-1/read-surface.json
uv run --script scripts/summarize-pi-json-events.py evaluations/runs/20261024-desktop-ui-cross-v4-boundary-luna-1/events.jsonl --require-model gpt-5.6-luna --fail-on-invalid-json --fail-on-tool-error --output evaluations/runs/20261024-desktop-ui-cross-v4-boundary-luna-1/read-surface.json
uv run --script evaluations/desktop-plugin-ui/inspect_cross_v4.py --prefix 20261024-desktop-ui-cross-v4-contract- --output evaluations/runs/20261024-desktop-ui-cross-v4-contract-independent.json
uv run --script evaluations/desktop-plugin-ui/inspect_cross_v4.py --prefix 20261024-desktop-ui-cross-v4-boundary- --output evaluations/runs/20261024-desktop-ui-cross-v4-boundary-independent.json
```

Keep raw events, stderr, prompt/manifests, exact files, failed edit messages,
diagnostic findings/repairs, independent reports, and unchanged payload copies
in the original ignored run folders. Earlier v1–v3 cohorts and the aborted
v2 rerun remain separately recorded. No failed result is relabeled as a pass.
