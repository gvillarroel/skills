# Scoped usability and palette contract, v2

Date: 2026-10-25. Skill: `desktop-plugin-ui`. One fresh isolated Pi 1.4.0 run
used the recorded `openai-codex/gpt-5.6-luna` exception with high thinking after
all repository static gates passed. The prompt is unchanged from
[v1](design-contract-v1-luna-1.md). The subjects and results remain separate;
neither failing sample was replaced, edited, retried or pooled.

## Subject and outcome

Run ID: `20261025-desktop-ui-design-contract-v2-luna-1`.
Frozen source/runtime/full payload: 19 files, SHA-256
`d02ed682c82aaa66db71ca29019b3d866145c2a314bb0db3714dcde4d7c8f038`.
Prompt: [desktop-plugin-ui-design-contract.md](../pi-prompts/desktop-plugin-ui-design-contract.md),
SHA-256 `635da51c6847200a9de696720d3ee50c8f7b66b40ce56db922bd4d6e733f154c`.
The manifest records both exact digests, and the copied bundle stayed unchanged.

**Strict harness: 1/1 pass. Required-model trace: 1/1 pass. Conservative manual
and joint acceptance: 0/1.** The independent review passes H1-H10, default CS1,
all color values, all three contrast decisions/repairs and the requested host
styling boundaries. It finds **13/14 exact source-token paths valid**. The
remaining invalid path is an **agent / artifact-contract failure**, affecting a
required exact-provenance field. It is not a host limitation or infrastructure
failure. Correct color membership alone does not satisfy the token-path rule.

The exact required `design/ui-review.md` and `design/ui-contract.json` exist
and are nonempty; JSON is valid, and all three task-level booleans are false.
Both final artifacts were read in full. Their SHA-256 values are:

- Markdown: `841c8505a196139a9f2598fc2faae87d6fb46e4c22a555d03e6ee8dce5dc7ec7`.
- JSON: `b592567923295b33d6fe0bd90419bef6f1336d3f4132f80aef2a4d95f4fe6060`.

## Independent design review

**H1-H10 pass.** There are ten unique JSON records with the exact canonical
IDs and short labels, each providing interaction, status, finding, evidence,
fix and validation fields. Planned checks are `untested`; the report does not
claim a representative-user study. The queue plan covers search, selection,
draft/commit priority, errors, cancellation, refresh recovery, chart redundancy,
CSV and explicit assistant follow-up.

**Default palette and color values pass.** The active set is the exact copied
`skills/desktop-plugin-ui/assets/palettes/colorset1.yml`, selected by default.
CS2 remains conditional on an explicit current-deliverable choice; categories
and a dark host theme do not select it. All 14 role colors are exact CS1 values.
Success uses neutral text/checkmark; status and categories also have text,
icons, shapes or patterns. No CS2-only hue or invented shade was introduced.

**The exact source-token contract fails.** JSON
`palette.roles[9].exact_source_token` at `workspace/design/ui-contract.json:69`
contains `red.status`; Markdown repeats that supposed exact token at
`workspace/design/ui-review.md:110` and in its contrast table. There is no
top-level `red` mapping in the copied asset. The actual key is
`colors.red.status`, whose value is `#e8002a`; the same value also occurs at
`interface.action.destructive` and `interface.feedback.critical.text`.
The hex and intended error-accent use are correct, but the stated source path
cannot be resolved. All other 13 reported source-token/hex pairs match the
copied asset. No artifact was corrected after this finding.

**All three contrast cases pass independent review.** Separate calculations
use sRGB relative luminance and unrounded threshold comparisons:

| Use | Original pair | Independent ratio | Threshold | Replacement pair | Independent ratio |
| --- | --- | --- | --- | --- | --- |
| Sole focus indicator | `#cfcfcf` / `#ffffff` | 1.557955 | 3:1 | `#9e1b32` / `#ffffff` | 7.904688 |
| Identifying input border | `#9c9c9c` / `#ffffff` | 2.745446 | 3:1 | `#696969` / `#ffffff` | 5.489815 |
| Ordinary error text | `#e8002a` / `#ffccd5` | 3.326162 | 4.5:1 | `#333e48` / `#ffccd5` | 7.720737 |

All original pairs fail and replacements pass. All six reported ratios agree
with independent values to their six-decimal precision. Replacement token
paths are valid and retain the selected CS1. These calculations do not verify
paint after compositing, host theming, forced colors or actual rendering.

**The requested host-scope boundaries pass.** JSON separates authored MCP App
HTML/SVG/canvas as `exact` from surrounding host chrome as `host-owned`.
Markdown explicitly includes Copilot VS Code authored iframe paint in that
boundary. Native Claude nodes are `host-mapped`; terminal controls, Codex
elicitation, MCPB settings and permission dialogs remain `host-owned`.
Forced colors/high contrast preserve `accessibility-override`. The ChatGPT
recommendation now explicitly requires reachable HTTPS or a documented tunnel;
local Claude stdio is not presented as ChatGPT reachability. Both v1 scope
ambiguities are improved without claiming new host acceptance. Stock Codex,
ChatGPT widget and signed-in Copilot MCP App paint remain untested.

Eight JSON styling records and nine canonical interaction patterns support
the design. The source/report checker is narrower than this manual review: its
clean result cannot validate a YAML token path or clear the retained failure.

## Commands, checker and trace

```powershell
uv run --script scripts/run-pi-skill-eval.py desktop-plugin-ui --prompt-file evaluations/pi-prompts/desktop-plugin-ui-design-contract.md --model openai-codex/gpt-5.6-luna --mode json --strict --timeout-seconds 600 --run-id 20261025-desktop-ui-design-contract-v2-luna-1 --expect-output design/ui-review.md --expect-output design/ui-contract.json --expect-output-json-field 'design/ui-contract.json::host_acceptance_verified=false' --expect-output-json-field 'design/ui-contract.json::task_empirical_tests_performed=false' --expect-output-json-field 'design/ui-contract.json::user_testing_performed=false'
uv run --script scripts/summarize-pi-json-events.py evaluations/runs/20261025-desktop-ui-design-contract-v2-luna-1/events.jsonl --output evaluations/runs/20261025-desktop-ui-design-contract-v2-luna-1/trace-summary.json --require-model gpt-5.6-luna --require-tool-call --fail-on-invalid-json --fail-on-tool-error --require-read ../prompt.md --forbid-read-regex '(?i)(^|[\\/])assets[\\/]examples([\\/]|$)' --forbid-read-regex '(?i)^skills[\\/](?!desktop-plugin-ui([\\/]|$))'
```

The agent ran the exact required diagnostic after both writes and inspected
`passed`. An independent rerun from the copied workspace also passes:

```bash
uv run --script skills/desktop-plugin-ui/scripts/check_reports.py design/ui-review.md design/ui-contract.json
```

The checker reports **44 official URL checks, zero findings and zero
replacements**. Both reports cite the same 22 exact bundled primary URLs,
including Nielsen, W3C and relevant host documentation. There is no JSON
historical-observation array in this design contract, so its reported count
of zero is not evidence of testing historical fields.

The strict harness and required-model summary pass with only
`gpt-5.6-luna`, valid events, zero runtime tool errors, exact outputs, false
booleans and unchanged copied skill files. The **17 read-tool calls** cover the
prompt, entry point, all 13 compact host/design references and the two bundled
palette assets. Both assets were read; CS1 alone was activated. No acceptance
example, generated fixture, sibling skill, repository document, project artifact
or external read was used. Three shell calls only list bundled sources,
calculate contrast locally and check the two reports. Complete command review
found no task-level network/provider call, install, deployment, configuration
change or external app/account operation.

The run took **107.878 seconds**. OpenAI Pi usage aggregates are 47,128 input,
14,489 output, 187,520 cache-read and 249,137 total trace tokens. No Claude or
Copilot model allowance was consumed. There was no new UI rendering, user
testing, real host acceptance, contrast screenshot or OS file-delivery test.

Raw evidence remains under
`evaluations/runs/20261025-desktop-ui-design-contract-v2-luna-1/`.
`independent-review.json` records passing design subchecks, the unresolved
exact-token field, and false manual/joint acceptance. The command evidence is
in `independent-command-review.json`. The separate v1 record and both frozen
workspaces remain intact; no additional run or canonical change followed.
