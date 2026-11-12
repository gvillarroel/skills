# Cross-assistant v1 contract and boundary validation

Date: 2026-10-24 America/New_York; runs started 2026-10-25 UTC. Skill:
`desktop-plugin-ui`. Model: **openai-codex/gpt-5.6-luna**, high thinking,
Pi 1.4.0, isolated runtime profile, strict JSON mode. This uses the existing
recorded Luna exception after Spark account rejection. No Claude or Copilot
inference was performed for these evaluations.

Both runs copied the same **15-file** frozen runtime payload:

`a54a8e1ea5bf4c5ab693557b90b711881cb9600b6df3ff45753eec2947d54fac`

| Case and run | Strict harness | Independent structure/source | Manual factual review | Outcome |
| --- | --- | --- | --- | --- |
| Contract: `20261024-desktop-ui-cross-v1-contract-luna-1` | Pass | Pass; 22 canonical patterns | Pass | Accepted contract case |
| Boundary: `20261024-desktop-ui-cross-v1-boundary-luna-1` | Pass | Fail: historical observation evidence strings omit canonical observed-* labels | Pass on substantive scope and facts | Bounded artifact-format failure; not a release pass |

Do not discard the boundary failure or count a temporary relaxed checker result
as acceptance. A follow-up skill clarification and a fresh frozen cohort can
address the format requirement without changing this result.

## Exact artifacts and hashes

All paths below are relative to each run's `workspace/`.

| Run case | Required artifact | SHA-256 |
| --- | --- | --- |
| Contract | `results/cross-reference.md` | `95fca8d88f20ea8a499a8af57d9a2b2378ca3e95933b51e5bc4e7e013a051b7a` |
| Contract | `results/cross-decisions.json` | `c30f32ec870ee313b7fbb24d948fbfbe24f2264688e0d99c918acd4ccc715edc` |
| Boundary | `review/cross-boundaries.md` | `0fcff8bfefa58ad236aeea4109bbbfd130407b30a6d33ab6f2719b229ef25402` |
| Boundary | `review/cross-status.json` | `6105680fbd116ce3b4e1fca9da4ac5f70cef5efe480592e61d534a7f75b7c5d1` |

Both exact-output/hash gates and all requested JSON boolean assertions passed.
Task-level `host_acceptance_verified` and `task_empirical_tests_performed`
remain false; the boundary preserves `product_confirmed: false`. Both copied
payloads remained unchanged.

## Independent factual and evidence review

The contract correctly covers all five products, with separate Desktop Chat
and Code-tab rows, plus terminal versus VS Code Copilot rows. Its 22 selected
patterns include text fallback, tool/resource registration, server validation,
native controls and previews, elicitation policy, optional capabilities,
ChatGPT deployment, editor webviews, canvas gates, and constrained budgets.
Each contract pattern has input, rule, fallback, evidence, and validation.
Primary links are exact members of the copied bundle/source catalog; both
the agent and evaluator source checks passed for both final artifacts.

The boundary review preserves the ambiguous Cloud product names while finishing
a conditional comparison. It rejects a universal native DOM container without
denying browser MCP Apps. It distinguishes the failed Codex app-server
`ui/initialize` and Copilot ACP `ui/show` methods from other UI mechanisms.
It correctly handles cancellation as a non-acceptance outcome, bounds native
`file:` link findings to the tested Claude tree, scopes VS Code inline/device
exclusions to MCP Apps, and does not convert absent PiP into a universal Claude
exclusion. No material factual error or fabricated citation was found.

Both artifacts preserve the historical layers: actual Claude Desktop Chat
3.6556.2 paint/direct interaction/fullscreen; Claude Code 2.1.302 engine-only
tests; Codex 0.145.0 CLI/protocol/form callbacks; actual Copilot CLI forms;
actual VS Code extension-owned webview; and incomplete ChatGPT setup consent
with separate fixture evidence. Neither promotes current advisory output to
fresh acceptance. A minor compressed contract phrase about headless decline
should be read with the named observed policy/client context, not as a rule
for every possible owned headless frontend.

The boundary JSON historical records provide version, surface, layer, result,
and narrative evidence but omit the canonical `observed-working` or
`observed-failed` token. The frozen evaluator requires those labels. Classify
this as an artifact-format gap rather than an empirical/factual failure.

## Trace and read-surface review

Both required-model trace summaries passed with observed `gpt-5.6-luna`, zero
invalid JSON lines, and zero tool errors. First read was `../prompt.md` followed
by the copied skill entry point. All remaining reads stayed inside the copied
bundle. Contract read the matrix and 12 relevant focused references; boundary
read the matrix and 11 references. Their breadth is appropriate for five-host
comparisons and the stated assumptions; no acceptance gallery, sibling skill,
repository document, prior run, or outside-workspace source was read.

Contract shell activity was only the bundled source check over both artifacts.
Boundary listed the bundled source catalog and then checked both outputs.
No network or external application/account/configuration operation was found.

## Evaluator correction history retained

During manual review the evaluator author initially considered the historical
label requirement stricter than the prompt's requested narrative evidence and
temporarily removed that one check. The resulting boundary pass was withdrawn
after the root reviewer directed retaining the original criterion. The check
and its self-test were restored before final grading. Preserve the temporary
result as `evaluations/runs/20261024-desktop-ui-cross-v1-boundary-independent-criterion-relaxation-withdrawn.json`;
it is not an accepted grade. The final original-criterion report is
`evaluations/runs/20261024-desktop-ui-cross-v1-boundary-independent.json`.

The helper's 15 deterministic self-tests pass after restoration. No skill
source changed during either run. There were no failed Pi execution attempts
for these two cases; the retained failure is the boundary artifact-format gate.

## Reproduction commands

```powershell
uv run --script scripts/run-pi-skill-eval.py desktop-plugin-ui --prompt-file evaluations/pi-prompts/desktop-plugin-ui-cross-contract.md --mode json --strict --model openai-codex/gpt-5.6-luna --run-id 20261024-desktop-ui-cross-v1-contract-luna-1 --expect-output results/cross-reference.md --expect-output results/cross-decisions.json --expect-output-json-field results/cross-decisions.json::host_acceptance_verified=false --expect-output-json-field results/cross-decisions.json::task_empirical_tests_performed=false --timeout-seconds 600
uv run --script scripts/run-pi-skill-eval.py desktop-plugin-ui --prompt-file evaluations/pi-prompts/desktop-plugin-ui-cross-boundary.md --mode json --strict --model openai-codex/gpt-5.6-luna --run-id 20261024-desktop-ui-cross-v1-boundary-luna-1 --expect-output review/cross-boundaries.md --expect-output review/cross-status.json --expect-output-json-field review/cross-status.json::host_acceptance_verified=false --expect-output-json-field review/cross-status.json::task_empirical_tests_performed=false --expect-output-json-field review/cross-status.json::product_confirmed=false --timeout-seconds 600
uv run --script scripts/summarize-pi-json-events.py evaluations/runs/20261024-desktop-ui-cross-v1-contract-luna-1/events.jsonl --require-model gpt-5.6-luna --fail-on-invalid-json --fail-on-tool-error --output evaluations/runs/20261024-desktop-ui-cross-v1-contract-luna-1/read-surface.json
uv run --script scripts/summarize-pi-json-events.py evaluations/runs/20261024-desktop-ui-cross-v1-boundary-luna-1/events.jsonl --require-model gpt-5.6-luna --fail-on-invalid-json --fail-on-tool-error --output evaluations/runs/20261024-desktop-ui-cross-v1-boundary-luna-1/read-surface.json
uv run --script evaluations/desktop-plugin-ui/inspect_cross_runs.py --prefix 20261024-desktop-ui-cross-v1-contract- --output evaluations/runs/20261024-desktop-ui-cross-v1-contract-independent.json
uv run --script evaluations/desktop-plugin-ui/inspect_cross_runs.py --prefix 20261024-desktop-ui-cross-v1-boundary- --output evaluations/runs/20261024-desktop-ui-cross-v1-boundary-independent.json
```

Raw manifests, JSONL, stderr, gate JSON, artifacts, and read summaries remain
under their original ignored `evaluations/runs/<run-id>/` folders. Keep the
failure and frozen payload evidence when evaluating the next cohort.
