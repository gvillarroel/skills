# Narrow live follow-up: isolated skill-use review

Date: October 25, 2026, America/New_York. Skill: `desktop-plugin-ui`.
Case: one narrow evidence-status diagnostic, retained first attempt. Model:
`openai-codex/gpt-5.6-luna`, thinking high, under the existing recorded model
exception. This is a new scoped subject and does not repeat or clear the
earlier offerings cohorts.

## Result

| Gate | Result | Scope |
| --- | --- | --- |
| Strict harness | **1/1 pass** | Exact artifacts, event policy, false JSON flags and unchanged copied skill pass. |
| Final report checker | **1/1 pass** | Twelve official URL occurrences and five listed historical records are clean. |
| Conservative independent manual acceptance | **0/1** | Two evidence labels promote untested or source-defined behavior to failed/observed execution. |
| Joint strict/manual acceptance | **0/1** | The strict pass does not erase the semantic failures. |

The run exits 0 in **56.691 seconds**, with 15 tool calls: nine reads, four
bash calls and two writes. The independent event summary finds ten Luna model
records, zero tool errors, zero invalid JSON and zero policy findings. No
rerun, evaluator repair, extra provider, account, browser, prototype or host
operation was performed. The forward-test model itself is the deliberately
authorized OpenAI call; it submitted no Claude or Copilot inference request.

## Frozen identities and exact outputs

| Item | Identity |
| --- | --- |
| Run ID | `20261025-desktop-ui-live-followup-v1-luna-1` |
| Copied runtime | 22 files, SHA-256 `9146fdf19d45fa9f3e3608f48677ca43b21ca16763e302956caccbe6a6ac68cf` |
| Source prompt | `evaluations/pi-prompts/desktop-plugin-ui-live-followup.md`, SHA-256 `3305e4c3bbf55e5ef12007acc3525b465d350a7c16a2fa0ebe782849a4887c1f` |
| Frozen review criteria | `evaluations/desktop-plugin-ui/live-followup-review-criteria.md`, SHA-256 `28bdc420c8613e9b8640d444630a07087fe01738dd8bd3e5f26cf05a075c562c` |
| Markdown output | `workspace/followup/status.md`, SHA-256 `61c0835ce32ced5c06c9f042f0f2ba1fc1797228ca95f441e8120e0249dd47d0` |
| JSON output | `workspace/followup/status.json`, SHA-256 `0ebf49b47a49e7f9b26965131623d9fe21cfb5f550d8591d8d4bc8118304ee29` |

The manifest's prompt hash matches the frozen source bytes. The copied
`prompt.md` has Windows CRLF newlines and SHA-256
`9bba46af5548f266884d99e0d1e8b53ec08725613f56f636d7af94100013dd69`.
Its normalized text exactly equals the source: source 1,541 bytes/zero CRLF,
copy 1,565 bytes/24 CRLF. This is newline serialization, not a prompt change.
Preflight verified that no run directory with this ID already existed.

The two requested artifacts are nonempty, JSON contains all requested fields,
and both `host_acceptance_verified` and `task_empirical_tests_performed` are
literal Boolean `false`. The copied payload still matches the frozen hash
after the independent review. The original outputs remain unchanged.

Raw evidence is retained under
`evaluations/runs/20261025-desktop-ui-live-followup-v1-luna-1/`, including the
manifest, events, original stdout/stderr, all four gate reports,
`independent-event-summary.json` and `independent-review-identities.json`.

## Independent content review

The output usefully covers the four requested factual areas:

- The later workspace no longer shows Restricted Mode but still requires
  Copilot model sign-in. It preserves the user's decision to continue without
  signing in and proposes no automatic login or model attempt.
- Activation is an attempt, not signed-in readiness or painted MCP Apps. The
  output retains orderly host termination and the absence of an observed
  activation-failure stack. It does not declare the proposal mismatch fatal
  or harmless.
- The 24-check CS1/English result is identified as real MCP stdio plus an
  offline synthetic-browser fixture, with Copilot Chat delivery untested.
- The user-reported chart visibility, transient app-tab listing, failed bind
  and subsequent empty discovery are recorded without certifying controls or
  making a product-wide rendering exclusion. Unknown capture versions remain
  explicitly unknown. Fullscreen and host side-panel operations are separated.

English prose and the existing palette/host-style boundaries pass. No new UI,
numeric contrast value or exact token-path assertion is added, so no new
palette calculation or heuristic checklist is required by this narrow case.
The six source URLs are exact catalog entries in both outputs. The agent runs
the report checker after writing both artifacts, receives `passed:true`, and
then reads both completed files. The evaluator independently repeats the
checker and receives the same clean result.

Two statements still fail the frozen requirement to preserve the execution
layer and result of every empirical claim:

1. **Untested readiness/paint is labeled as failure.** In both outputs, H2's
   evidence includes `observed-failed: readiness and paint not established`.
   Its own result records only an activation attempt, orderly termination and
   no failure stack. There is no named failed readiness or paint action. The
   narrative correctly leaves those outcomes untested, but the ledger turns
   missing acceptance evidence into an observed failure. The canonical label
   requirement does not authorize inventing a failed observation.
2. **Source-defined fullscreen behavior becomes an observed request.** H5's
   result says the component's Expand action *requested* fullscreen, and its
   evidence says `observed-working: registration and request were observed`.
   The frozen bundle says registration **source declares** its resource and
   that the component's Expand action **requests** fullscreen. The follow-up
   could not bind the tab and did not establish the actual request or controls.
   Source inspection supports the API distinction; it does not support this
   claimed execution. The output should keep that source-defined behavior
   separate from the reported visibility and failed controller bind.

These findings concern factual evidence calibration, not a hidden minimum row
count, preferred ID, output schema or wording requirement. The five rows are
present and checker-clean; their stated outcomes still need manual review.
The combined fixture row is not independently rejected merely for summarizing
the explicitly requested 24-check mixed-layer probe.

## Read surface and isolation

The first completed tool read is `../prompt.md`, followed by the loaded
`skills/desktop-plugin-ui/SKILL.md`. Subsequent bundled reads are limited to:

- `references/capability-offerings.md`
- `references/copilot-limits.md`
- `references/evidence-and-probing.md`
- `references/codex-limits.md`
- `references/report-authoring.md`

The only other read-tool paths are the two generated outputs. Shell calls
list the bundled source catalog, check for existing exact outputs, execute
the bundled report checker and list the final two files. No acceptance
fixture, sibling skill, repository/project document, network, installation or
account operation appears in the runtime trace. The two slightly over-10 KB
host/offerings references contain the selected cross-host findings; no file
above 50 KB, gallery or generated fixture is read.

## Reproduction

From the repository root:

```powershell
uv run --script scripts/run-pi-skill-eval.py desktop-plugin-ui --prompt-file evaluations/pi-prompts/desktop-plugin-ui-live-followup.md --run-id 20261025-desktop-ui-live-followup-v1-luna-1 --model openai-codex/gpt-5.6-luna --mode json --strict --expect-output followup/status.md --expect-output followup/status.json --expect-output-json-field followup/status.json::host_acceptance_verified=false --expect-output-json-field followup/status.json::task_empirical_tests_performed=false --timeout-seconds 600
uv run --script scripts/summarize-pi-json-events.py evaluations/runs/20261025-desktop-ui-live-followup-v1-luna-1/events.jsonl --output evaluations/runs/20261025-desktop-ui-live-followup-v1-luna-1/independent-event-summary.json --require-model gpt-5.6-luna --require-tool-call --fail-on-invalid-json --fail-on-tool-error --require-read ../prompt.md --forbid-read-regex '(?i)(^|[\\/])assets[\\/]examples([\\/]|$)' --forbid-read-regex '(?i)^skills[\\/](?!desktop-plugin-ui([\\/]|$))'
uv run --script evaluations/runs/20261025-desktop-ui-live-followup-v1-luna-1/workspace/skills/desktop-plugin-ui/scripts/check_reports.py evaluations/runs/20261025-desktop-ui-live-followup-v1-luna-1/workspace/followup/status.md evaluations/runs/20261025-desktop-ui-live-followup-v1-luna-1/workspace/followup/status.json --fail-on-findings
```

The existing run ID is intentionally retained; do not reuse it for another
attempt. Overall skill status and earlier cohorts remain separate. This
review performs no canonical skill or backlog edits and clears no live-host
acceptance gate.
