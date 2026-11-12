# Cross-v3 generalization validation

Date: October 24, 2026, America/New_York; UTC logs are October 25.
Skill: `desktop-plugin-ui`. Model: `openai-codex/gpt-5.6-luna`, under the
continuing recorded model exception. Prompt and original grader were unchanged.

**Result: 2/3 strict and original-grader passes. V3 generalization is not an
aggregate release pass.** Run 1 repaired its citation errors and produced valid
final outputs, but two ambiguous JSON `edit` calls failed along the way. The
zero-tool-error criterion remains enforced; this is a retained agent repair
failure, not a provider or product-host failure. No run was repeated, discarded,
repaired externally, or pooled with the separate clean v2 subset.

## Frozen contract

All three runs used the 15-file runtime payload SHA-256
`1cd3cedbc5124bde59e242b22770eb0505893f65058cb7d438b90f55f79863b3`.
The prompt remains [desktop-plugin-ui-cross-generalization.md](../pi-prompts/desktop-plugin-ui-cross-generalization.md),
SHA-256 `45d19d83b245ed31d9e0307b2da37910addb2cef0179670f91d44c5e52458a89`.
No skill source changed during these concurrent runs.

For each `N` in 1, 2, 3:

```powershell
uv run --script scripts/run-pi-skill-eval.py desktop-plugin-ui --prompt-file evaluations/pi-prompts/desktop-plugin-ui-cross-generalization.md --model openai-codex/gpt-5.6-luna --mode json --strict --timeout-seconds 600 --run-id 20261024-desktop-ui-cross-v3-generalization-luna-N --expect-output handoff/restricted-surfaces.md --expect-output handoff/recovery-plan.json --expect-output-json-field handoff/recovery-plan.json::host_acceptance_verified=false --expect-output-json-field handoff/recovery-plan.json::task_empirical_tests_performed=false
```

The mandatory event summarizer ran on every trace with
`--require-model gpt-5.6-luna --fail-on-invalid-json --fail-on-tool-error`.
Run 1's summary correctly reports `passed:false` and its two edit errors.
Runs 2 and 3 report `passed:true`. Every model record identifies exactly
`openai-codex` / `gpt-5.6-luna`; all runs have valid JSON and unchanged payloads.

| Suffix | Duration | Model records | Strict / original grader | Independent final sources |
| --- | ---: | ---: | --- | --- |
| `luna-1` | 95.024 s | 15 | Failed: two tool errors | Passed, 36 official URLs |
| `luna-2` | 99.366 s | 11 | Passed | Passed, 44 official URLs |
| `luna-3` | 72.041 s | 8 | Passed | Passed, 41 official URLs |

All exact output paths and false task-level boolean assertions passed. The
original grader result is retained in `cross-v3-generalization-structure.json`.
It found no unknown patterns, source failures, broad-exclusion cues or external
commands; run 1 fails because its strict/event gate failed. The copied bundle
contains 42 canonical pattern headings; the runs selected 12/18/18 patterns.

## Run 1 failure diagnosis

The agent initially wrote `modelcontextprotocol.org` instead of the copied
`modelcontextprotocol.io` citation. It used the default diagnostic source
checker, so the checker finding itself was not a tool error. This confirms the
v3 diagnostic-versus-CI clarification worked.

The agent then attempted to repair a URL appearing twice in the JSON with an
`edit` call requiring unique old text. The tool returned:

> Found 2 occurrences of the text in handoff/recovery-plan.json. The text must be unique. Please provide more context to make it unique.

It repeated an ambiguous edit, producing a second tool error. It subsequently
used contextual edits successfully, reran the source checker and validated the
JSON. Both final artifacts pass independent citation checks. The Python command
at the end inspected JSON fields; it did not perform the repair. This distinction
is retained so a future fix targets duplicate-citation repair mechanics.

The failure is not a UI capability, model entitlement, account, network, or
provider outage. A deterministic all-occurrence replacement of the exact
diagnostic URL, or an unambiguous contextual edit, would avoid this class of
repair error. Any skill change must be tested as a new frozen payload; no such
change was made by this reviewer.

## Factual and trace review

The final plans preserve the required host distinctions: native Claude terminal
controls versus HTML, negotiated Copilot terminal forms, tested VS Code webview
versus untested Copilot chat/canvas paint, Codex `never` automatic decline versus
a future owned `on-request` client, and historical Claude Desktop Chat paint
versus future ChatGPT acceptance. Image input, byte transport, native validation,
actual pixels and interactive canvas remain separate. Decline/cancel do not
grant approval. Local/remote deployment, optional capabilities, budgets and text
fallback are explicitly staged. No new product-host acceptance is invented.

The source checker was rerun independently from each copied bundle on both
final artifacts with `--fail-on-findings`; all passed. Manual content review
found no blocking factual UI overclaim in the final plans. That content result
does not waive run 1's strict execution failure.

Trace reads stayed inside the copied runtime bundle and task prompt. No host
application or account was opened and no downstream provider inference was
used. Run 1 additionally listed its isolated workspace, inspected duplicate
URL context, and read its generated JSON fields during repair; no project or
sibling-skill corpus was used.

Pi-reported evaluation-model usage, separate from application-provider probes:

| Run | Input | Output | Cache read | Total tokens |
| --- | ---: | ---: | ---: | ---: |
| 1 | 40,105 | 12,729 | 359,808 | 412,642 |
| 2 | 42,198 | 13,149 | 217,984 | 273,331 |
| 3 | 38,185 | 9,911 | 121,984 | 170,080 |

Raw events/stderr, manifests, final artifacts, strict checks,
`model-trace-summary.json`, and `source-check-independent.json` remain in
`evaluations/runs/20261024-desktop-ui-cross-v3-generalization-luna-{1,2,3}/`.
Final artifact hashes are recorded by both harness and original grader. The
clean v2 cohort remains separately documented in
[cross-v2-generalization.md](cross-v2-generalization.md).
