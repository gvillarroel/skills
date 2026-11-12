# Cross-assistant naturalistic evaluation, frozen v1

Date: 2026-10-24 (America/New_York; UTC logs are dated 2026-10-25).
Skill: `desktop-plugin-ui`. Case: `naturalistic-forward`. Model exception:
`openai-codex/gpt-5.6-luna`, as recorded for this skill after Spark rejection.
No skill edits, output repairs, replacement samples, or favorable substitutions
were made during these repetitions.

Frozen runtime payload SHA-256:
`a54a8e1ea5bf4c5ab693557b90b711881cb9600b6df3ff45753eec2947d54fac`.
All three manifests record the same 15-file payload. Prompt SHA-256:
`4b2f770266448125b47ac76a40bd42f730f170ebff7205ddf4d4752df1df41b4`.

## Outcome

The strict harness passed **3/3**. Independent artifact acceptance passed
**1/3**, below the required two-of-three naturalistic threshold. Runs 2 and 3
preserve concrete historical successes, failures, versions, surfaces, and
current-task uncertainty, but omit canonical `observed-working` or
`observed-failed` labels inside `historical_observations`. Their host rows do
include those labels; that does not repair the historical-record contract.
Classify both as **agent / artifact-contract failures**. Retain the failed
artifacts and grader result; do not weaken the grader or erase the failures.

| Run ID suffix after `20261024-desktop-ui-cross-v1-` | Strict harness | Independent acceptance | Selected IDs | Duration |
| --- | --- | --- | --- | --- |
| `naturalistic-luna-1` | Pass | Pass | 36 canonical IDs | 68.408 s |
| `naturalistic-luna-2` | Pass | Fail: historical evidence labels omitted | 25 canonical IDs | 65.415 s |
| `naturalistic-luna-3` | Pass | Fail: historical evidence labels omitted | 28 canonical IDs | 75.716 s |

Each produced the exact nonempty `proposal/support-queue.md` and
`proposal/host-decisions.json`, with all five required host IDs. Both
`host_acceptance_verified` and `task_empirical_tests_performed` are false in
every JSON output. Artifact hashes are retained in each harness report and
the independent inspection result.

## Commands and trace checks

Three fresh isolated processes ran the following command, varying the final
run-number suffix from 1 through 3:

```powershell
uv run --script scripts/run-pi-skill-eval.py desktop-plugin-ui --prompt-file evaluations/pi-prompts/desktop-plugin-ui-cross-naturalistic.md --model openai-codex/gpt-5.6-luna --mode json --strict --timeout-seconds 600 --run-id 20261024-desktop-ui-cross-v1-naturalistic-luna-1 --expect-output proposal/support-queue.md --expect-output proposal/host-decisions.json --expect-output-json-field 'proposal/host-decisions.json::host_acceptance_verified=false' --expect-output-json-field 'proposal/host-decisions.json::task_empirical_tests_performed=false'
```

Each trace was separately summarized with:

```powershell
uv run --script scripts/summarize-pi-json-events.py evaluations/runs/20261024-desktop-ui-cross-v1-naturalistic-luna-1/events.jsonl --output evaluations/runs/20261024-desktop-ui-cross-v1-naturalistic-luna-1/trace-summary.json --require-model gpt-5.6-luna --require-tool-call --fail-on-invalid-json --fail-on-tool-error --require-read ../prompt.md --forbid-read-regex '(?i)(^|[\\/])assets[\\/]examples([\\/]|$)' --forbid-read-regex '(?i)^skills[\\/](?!desktop-plugin-ui([\\/]|$))'
uv run --script evaluations/desktop-plugin-ui/inspect_cross_runs.py --prefix 20261024-desktop-ui-cross-v1-naturalistic-luna- --output evaluations/runs/20261024-desktop-ui-cross-v1-naturalistic-inspection.json
```

All trace summaries require and observe only `gpt-5.6-luna` through
`openai-codex`. They report valid JSON events, zero tool errors, prompt-first
reads, and unchanged skill payloads. All 14 read-tool calls per run are the
prompt, skill entry point, and relevant bundled references. The five-product
request resulted in broad reference coverage; no examples, sibling skills,
repository documentation, project artifacts, or external reads were used.
Shell commands only listed the local source catalog or checked the two final
artifacts. No task-level network, install, configuration, host operation, or
provider invocation was found in the trace.

| Repetition | Input | Output | Cache-read | Trace token total |
| --- | --- | --- | --- | --- |
| 1 | 34,116 | 8,680 | 117,248 | 160,044 |
| 2 | 34,798 | 8,770 | 124,032 | 167,600 |
| 3 | 36,148 | 9,807 | 145,024 | 190,979 |

These are Pi trace aggregates, not Claude/Copilot allowance usage. All model
evaluation work used the recorded OpenAI model exception.

## Independent content review

All six artifacts were read after completion. All three proposals cover the
requested search, selected ticket, priority draft/submit, chart, CSV export,
and explicit explanation action. They keep authoritative records and versions
on the server, use stable ticket IDs, preserve last-good data after refresh
failure, and provide text/structured fallback. Repetition 3 gives the clearest
post-submit cancellation rule: if commit outcome is uncertain, re-fetch and
reconcile rather than claiming cancellation after a possible commit.

The product distinctions are bounded and consistent with the copied bundle:

- Claude Desktop Chat uses the local MCP App route; its historical signed-in
  paint/direct actions/fullscreen are not relabeled current-task acceptance.
  Remote, host-owned elicitation, actual export bytes, mobile, and optional
  capability acceptance remain separate checks.
- Claude Code terminal uses native Mod controls and surface-specific preview
  fallbacks. Native engine tests, terminal SVG rejection, and Image/Raster
  acceptance are not promoted to actual terminal pixels or OS effects.
- Codex tool data, HTML bytes, metadata, and app-server callbacks remain
  backend evidence. Approval policy and custom frontend ownership are explicit;
  the failed app-server `ui/initialize` does not become a blanket UI exclusion.
- ChatGPT requires the documented HTTPS/tunnel deployment, optional extensions
  and account/policy checks. Setup consent and browser fixtures remain below
  signed-in widget paint. No current-task acceptance is invented.
- Copilot VS Code inline MCP Apps, separately installed extension webviews,
  and CLI terminal forms remain distinct. Drafted follow-up text is not a
  submitted assistant turn; extension-webview success is not Copilot Chat paint.

Every product has exact bundled primary-source URLs. Each agent successfully
ran the source checker after its final writes and inspected the passed result.
The independent inspector reran the copied checker with
`--fail-on-findings`; all three source checks passed. All selected pattern IDs
are canonical. No broad product exclusion, fabricated live test, or promotion
of lower-layer success to stock assistant paint was found.

Repetition 1's recommendation to avoid sharing renderer code is a conservative
design choice: portable HTML/components can be shared with host adapters.
This does not change its source/evidence acceptance result. The two explicit
historical-label omissions remain the only independent acceptance findings.

## Retained evidence

Raw runs, copied payloads, exact artifacts, manifests, events, trace summaries,
source-check results, and hashes remain under
`evaluations/runs/20261024-desktop-ui-cross-v1-naturalistic-luna-{1,2,3}/`.
The aggregate independent result is
`evaluations/runs/20261024-desktop-ui-cross-v1-naturalistic-inspection.json`.
Do not treat this v1 case as release-passing; a revised frozen payload needs a
new, separately recorded repetition set.
