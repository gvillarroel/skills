# Scoped usability and palette contract, v1

Date: 2026-10-25. Skill: `desktop-plugin-ui`. One isolated Pi 1.4.0 run used
the recorded `openai-codex/gpt-5.6-luna` exception with high thinking. The run
followed the completed repository static gates. No retry, runtime-payload
change, or post-run output edit was made.

## Subject and outcome

Run ID: `20261025-desktop-ui-design-contract-v1-luna-1`.
Frozen source/runtime/full payload: 19 files, SHA-256
`bcc6c0051fa2ceaf157a86a58444436d7fad694bec56b586f415aebc53121a86`.
Prompt: [desktop-plugin-ui-design-contract.md](../pi-prompts/desktop-plugin-ui-design-contract.md),
SHA-256 `635da51c6847200a9de696720d3ee50c8f7b66b40ce56db922bd4d6e733f154c`.
The run manifest confirms both digests.

**Strict harness: 1/1 pass. Required-model trace: 1/1 pass. Independent
structure/token/contrast/source checks: 1/1 pass. Conservative manual and joint
acceptance: 0/1.** This is a partial design success with retained **agent /
semantic-scope failures** in the leading transport recommendation and one
styling ownership record. It is not a harness or infrastructure failure.

The exact required `design/ui-review.md` and `design/ui-contract.json` are
nonempty and valid. All three task-level booleans are false. Both artifacts
were read in full; their SHA-256 values are:

- Markdown: `830a25eab4a25b2ee6c1feb97e036d690e71feb262c1c3877fd93628a4db82f6`.
- JSON: `1172d4d277eb89c3646688b9cdda28b362bf59ec0cc53951be491dca9a3c3527`.

## Independent findings

The design includes exactly **ten unique H1-H10 records**, each with concrete
interaction, status, finding, evidence, fix and validation fields. Their planned
checks remain `untested`; they do not claim representative-user testing. The
active palette is the bundled `assets/palettes/colorset1.yml`, selected by the
default rule. All **14 semantic role/token/hex mappings** match that exact
copied asset. Success uses neutral text and a checkmark; chart categories have
labels and shape/pattern cues. CS2 is conditional on an explicit future
deliverable choice and is not silently activated by categories or host theme.

The independent review recalculated all original and replacement pairs from
sRGB relative luminance and compared unrounded values with the thresholds:

| Use | Original pair | Original ratio | Threshold | Allowed-token replacement | Replacement ratio |
| --- | --- | --- | --- | --- | --- |
| Sole focus indicator | `#cfcfcf` / `#ffffff` | 1.557955 | 3:1 | `#9e1b32` / `#ffffff` | 7.904688 |
| Identifying input border | `#9c9c9c` / `#ffffff` | 2.745446 | 3:1 | `#696969` / `#ffffff` | 5.489815 |
| Ordinary error text | `#e8002a` / `#ffccd5` | 3.326162 | 4.5:1 | `#333e48` / `#ffccd5` | 7.720737 |

All three original pairs fail and all three proposed replacements pass. The
agent's rounded numbers match the independent calculations. Replacement token
paths and values also match the asset. These are local arithmetic checks;
they establish neither rendered contrast nor a complete accessibility audit.

The proposal uses 16 canonical interaction IDs and records 11 styling scopes,
including native nodes, terminal forms, elicitation, MCPB settings, permission
dialogs, host chrome, authored HTML and accessibility overrides. It preserves
forced colors, labels, keyboard focus and text fallback. Its historical
observations remain separate from current-task acceptance.

Two scope problems prevent conservative full acceptance:

1. `workspace/design/ui-review.md:5` opens with **“Use a local MCP App for the
   primary implementation on Claude Desktop Chat and ChatGPT”**. A later
   paragraph correctly says local stdio success is not ChatGPT deployment or
   paint. The leading recommendation nevertheless leaves the ChatGPT transport
   unqualified. A portable authored View should be separated from Claude local
   stdio and the required reachable ChatGPT HTTPS/authorized-tunnel route.
2. `workspace/design/ui-contract.json:48` labels **“Copilot VS Code MCP App”**
   as `host-mapped`, with owner **“host plus authored iframe”**. This combines
   two styling owners under one scope. The authored iframe can bind exact
   palette paint; surrounding host chrome remains host-owned or host-mapped.
   Other records and the Markdown make the general distinction correctly, but
   do not disambiguate this specific machine-readable row.

The outputs are preserved with those issues. The checker's clean result
checks source and historical-label contracts; it does not clear these semantic
findings. No new stock-host paint, control rendering, user study, or actual
CSV download was tested. Only the default-CS1 design branch was exercised.

## Commands, checker and read surface

```powershell
uv run --script scripts/run-pi-skill-eval.py desktop-plugin-ui --prompt-file evaluations/pi-prompts/desktop-plugin-ui-design-contract.md --model openai-codex/gpt-5.6-luna --mode json --strict --timeout-seconds 600 --run-id 20261025-desktop-ui-design-contract-v1-luna-1 --expect-output design/ui-review.md --expect-output design/ui-contract.json --expect-output-json-field 'design/ui-contract.json::host_acceptance_verified=false' --expect-output-json-field 'design/ui-contract.json::task_empirical_tests_performed=false' --expect-output-json-field 'design/ui-contract.json::user_testing_performed=false'
uv run --script scripts/summarize-pi-json-events.py evaluations/runs/20261025-desktop-ui-design-contract-v1-luna-1/events.jsonl --output evaluations/runs/20261025-desktop-ui-design-contract-v1-luna-1/trace-summary.json --require-model gpt-5.6-luna --require-tool-call --fail-on-invalid-json --fail-on-tool-error --require-read ../prompt.md --forbid-read-regex '(?i)(^|[\\/])assets[\\/]examples([\\/]|$)' --forbid-read-regex '(?i)^skills[\\/](?!desktop-plugin-ui([\\/]|$))'
```

The agent ran the exact required report diagnostic after writing both outputs
and inspected `passed`. An independent rerun of the copied
`skills/desktop-plugin-ui/scripts/check_reports.py` on both artifacts also
passes: **25 exact official URLs, five historical observation evidence fields,
zero findings, zero replacements**.

The strict harness confirms exact outputs, false booleans, valid events and an
unchanged copied payload. The required-model summary observes only
`gpt-5.6-luna`, with zero runtime tool errors. There are **17 read-tool calls**:
the prompt, entry point, all 13 compact cross-host/design references, the active
CS1 asset and the report helper. The five-host task justifies those bounded
references; no examples, sibling skill, repository document, generated fixture,
project artifact or external read was used. CS2 was not read or activated.

Four shell calls only inventory the copied bundle, list its exact source
catalog, calculate contrast locally and run the report diagnostic. The complete
command review found no task-level network/provider call, install, deployment,
configuration change or external app/account operation. The run took
**111.623 seconds**. OpenAI Pi usage aggregates are 46,369 input, 13,409 output,
218,624 cache-read and 278,402 total trace tokens; this consumed no Claude or
Copilot model allowance.

Raw outputs, checks and manifests remain under
`evaluations/runs/20261025-desktop-ui-design-contract-v1-luna-1/`. The local
`independent-review.json` separates passing deterministic checks from false
manual/joint acceptance and lists both retained scope findings.
`independent-contrast-reference.json` and `independent-command-review.json`
retain the calculation and command evidence. This scoped result does not
replace or pool earlier cross-assistant evaluation cohorts.
