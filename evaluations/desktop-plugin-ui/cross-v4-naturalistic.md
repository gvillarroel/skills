# Cross-assistant naturalistic evaluation, frozen v4

Date: 2026-10-24 (America/New_York; UTC logs dated 2026-10-25).
Skill: `desktop-plugin-ui`. Recorded model exception:
`openai-codex/gpt-5.6-luna`, high thinking, Pi 1.4.0. The task prompt is
unchanged from [v1](cross-v1-naturalistic.md), [v2](cross-v2-naturalistic.md),
and [v3](cross-v3-naturalistic.md). Prior cohorts and their failures remain
separate. There were no rerolls or post-run artifact edits.

Frozen 16-file runtime payload SHA-256:
`2b35617cd80abae02ad208d099c5d328d25d2f85c654fea1c9f10518ecb824ee`.
All three manifests record that payload. Prompt SHA-256:
`4b2f770266448125b47ac76a40bd42f730f170ebff7205ddf4d4752df1df41b4`.
The copied report helper has SHA-256
`68892c9952c6036c2e07cade284280282f4d97f7aef2f04be0395fd3a983e1b2`.
The separate [v4 inspector](inspect_cross_v4.py) adds per-field historical
evidence and bundled report-helper checks; the earlier inspector is preserved.

## Outcome

**3/3 strict harness, required-model trace, and v4 independent structural/source
checks passed. Conservative manual acceptance is 2/3.** This meets the
naturalistic two-of-three threshold. Run 3 repeats an overly exclusive Codex
availability claim despite the skill's explicit warning and later caveats in
the generated artifact. Retain this as an **agent / semantic wording failure**;
it is not evidence of a product renderer limitation.

| Suffix after `20261024-desktop-ui-cross-v4-` | Strict | V4 independent | Manual | Selected canonical IDs | Duration |
| --- | --- | --- | --- | --- | --- |
| `naturalistic-luna-1` | Pass | Pass | Pass | 23 | 71.465 s |
| `naturalistic-luna-2` | Pass | Pass | Pass with scoped wording caution | 34 | 66.588 s |
| `naturalistic-luna-3` | Pass | Pass | Fail: Codex exclusivity phrase | 19 | 73.931 s |

Each run created the exact nonempty `proposal/support-queue.md` and
`proposal/host-decisions.json`, covered all five host IDs, used only canonical
patterns, supplied exact bundled primary sources for each host, and kept
`host_acceptance_verified` and `task_empirical_tests_performed` false.
All 19 historical observation rows across the three final JSON records have
literal `observed-working` or `observed-failed` labels in the required
`historical_observations[i].evidence` field. Every agent checked both final
artifacts with `check_reports.py` and inspected its clean result. The v4
inspector independently reran the copied helper and passed both artifacts.

## Manual artifact review

All six final artifacts were read in full.

1. **Run 3: conservative semantic failure.** The lead recommendation at
   `workspace/proposal/support-queue.md:23` says, “A full Codex dashboard
   requires a frontend that we own.” The evidence establishes a tested
   tool/resource/callback path and an available custom-client route; stock
   desktop/IDE dashboard paint remains untested. The claim of necessity
   excludes more than that evidence permits. Later prose and JSON correctly
   retain stock paint as untested, but do not repair the stronger lead claim.
   The inspector's broad-exclusion heuristic did not flag this wording, which
   demonstrates why the manual review remains necessary. The output is
   preserved unchanged.
2. **Run 2: pass with a bounded evidence wording caution.** Its Codex JSON
   `hosts[2].evidence` says `observed-failed ... never-policy presentation`.
   Read this with the adjacent limits and historical row: the policy declined
   elicitation and `ui/initialize` failed at the app-server endpoint; no stock
   form or dashboard paint was established. The proposal explicitly calls
   desktop/IDE paint untested and permits an optional MCP Apps resource where
   an actual frontend supports it. The phrase must not be reused as proof of
   a failed stock renderer. Its custom-client recommendation is not exclusive.
3. **Run 1: pass.** It distinguishes Codex resource bytes and app-server
   callbacks from stock pixels, recommends a custom client conditionally, and
   keeps host acceptance untested. Its first report-helper invocation diagnosed
   all six misplaced historical labels. The agent edited those exact evidence
   fields and reran diagnostics successfully. Both invocations exited normally;
   the repair introduced no tool error and the helper invented no labels.

The form evidence remains correctly scoped across the cohort: **Copilot CLI
1.0.103 has actual terminal confirm/select/input and Escape observations with
zero model inference; Codex 0.145.0 has callback/transport and policy evidence,
including synthetic responses, with actual frontend form paint untested.**
Claude Code native-engine tests remain separate from terminal pixels. Claude
Desktop's signed-in local-stdio paint is historical; ChatGPT's setup consent
screen and synthetic fixture do not establish connection completion or widget
paint. Copilot's extension webview success remains separate from its stock
Chat MCP App surface.

All proposals cover search, stable selection, priority draft and commit,
accessible chart fallback, authorized CSV export, explicit explanation,
last-good refresh state, version checks, and useful text/structured output.
They distinguish local stdio from remote HTTPS/tunnel deployment, optional
capabilities from policy/consent, and drafted follow-up text from a submitted
model turn. Run 3 correctly notes that client cancellation can finish
server-side and requires reconciliation; its failure concerns the Codex
availability phrase above, not its state design.

## Commands and trace checks

Three fresh isolated processes used this command, varying suffix 1, 2, and 3:

```powershell
uv run --script scripts/run-pi-skill-eval.py desktop-plugin-ui --prompt-file evaluations/pi-prompts/desktop-plugin-ui-cross-naturalistic.md --model openai-codex/gpt-5.6-luna --mode json --strict --timeout-seconds 600 --run-id 20261024-desktop-ui-cross-v4-naturalistic-luna-1 --expect-output proposal/support-queue.md --expect-output proposal/host-decisions.json --expect-output-json-field 'proposal/host-decisions.json::host_acceptance_verified=false' --expect-output-json-field 'proposal/host-decisions.json::task_empirical_tests_performed=false'
```

Each trace was separately summarized with the required model and read gates:

```powershell
uv run --script scripts/summarize-pi-json-events.py evaluations/runs/20261024-desktop-ui-cross-v4-naturalistic-luna-1/events.jsonl --output evaluations/runs/20261024-desktop-ui-cross-v4-naturalistic-luna-1/trace-summary.json --require-model gpt-5.6-luna --require-tool-call --fail-on-invalid-json --fail-on-tool-error --require-read ../prompt.md --forbid-read-regex '(?i)(^|[\\/])assets[\\/]examples([\\/]|$)' --forbid-read-regex '(?i)^skills[\\/](?!desktop-plugin-ui([\\/]|$))'
uv run --script evaluations/desktop-plugin-ui/inspect_cross_v4.py --prefix 20261024-desktop-ui-cross-v4-naturalistic-luna- --output evaluations/runs/20261024-desktop-ui-cross-v4-naturalistic-inspection.json
```

All required-model summaries pass and observe only
`openai-codex/gpt-5.6-luna`: valid event JSON, zero runtime tool errors,
prompt-first reads, exact outputs, and unchanged copied payloads. The runs have
13, 14, and 13 read-tool calls, respectively, confined to the prompt, entry
point, and compact bundled cross-host references. No acceptance examples,
sibling bundles, repository documents, project artifacts, or external read
surface was used. Shell calls only listed bundled sources or checked the two
local reports. No task-level network command, provider call, installation,
configuration change, deployment, or external app/account operation was found.

| Repetition | Input | Output | Cache-read | Trace token total |
| --- | --- | --- | --- | --- |
| 1 | 34,143 | 8,889 | 179,200 | 222,232 |
| 2 | 39,152 | 8,325 | 119,552 | 167,029 |
| 3 | 33,992 | 9,696 | 117,120 | 160,808 |

These are OpenAI Pi evaluation aggregates. This cohort consumed no Claude or
Copilot model allowance. Exact artifacts, trace summaries, hashes, checker
results, and manifests remain under
`evaluations/runs/20261024-desktop-ui-cross-v4-naturalistic-luna-{1,2,3}/`.
The separate metadata-only routing control remains 10/10 because the routing
description is unchanged; see [the v2 record](cross-v2-naturalistic.md#metadata-only-routing-control).
