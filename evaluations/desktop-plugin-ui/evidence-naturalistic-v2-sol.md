# Evidence-classification repair: naturalistic v2 GPT-6.1 Sol review

Date: October 25, 2026, America/New_York. These are three separate first
attempts on the unchanged V2 subject using the deliberately recorded
`openai-codex/gpt-6.1-sol` model exception. The prompt and semantic standards
remain unchanged. Preserve the [V2 Luna review](evidence-naturalistic-v2-luna.md)
and [V1 Luna review](evidence-naturalistic-v1-luna.md), including their failures;
this cohort does not replace or pool with them.

## Result

| Run | Strict execution | Final typed checker | Semantic content | Allowed read/write scope | Manual / joint |
| --- | --- | --- | --- | --- | --- |
| 1 | Pass | Pass | Pass | Pass | Pass / Pass |
| 2 | Pass | Pass | Pass, with bounded wording caveat below | Pass | Pass / Pass |
| 3 | Fail: timeout | Pass on stable final artifacts | Pass on stable final artifacts | Pass | Pass / Fail |
| Total | **2/3** | **3/3** | **3/3** | **3/3** | **3/3 / 2/3** |

The frozen naturalistic joint threshold of at least 2/3 is **met for this
separate Sol cohort**. Run 3 remains an execution failure: a valid artifact
cannot erase the timeout. No sample was rerun, no timeout was extended, and
no tested output was repaired by the reviewer.

All six final artifacts exist, contain the required fields and Boolean false
current-task flags, and retain the default ColorSet 1. Independent checks pass
**37 token-path assertions, 35 explicit hex-binding assertions, 39 contrast
ratios and 30 H1-H10 canonical ID/short-label checks**. The final two-file typed
checker passes **92 official URL checks and 101 normalized records** across
the cohort. URL counts deduplicate each URL within a report. These checks
establish declared structure and arithmetic, not factual truth or UI paint.

## Frozen identities and commands

- Announced source/runtime/full subject: 23 files, SHA-256
  `ec22cd32a6c02aeaccd7178ff09be04d34d90a9798f07facab98ea81e6049e6f`.
  Each actual copied runtime manifest and independently recomputed final
  snapshot has this exact count/hash and remains unchanged.
- Helper SHA-256:
  `63fddc71df0b659b9d630487b73bcfe05f18b395a08b49398f75d07dfc01a80b`.
- Unchanged naturalistic prompt raw SHA-256:
  `ee44ad5752083b38ea153182d63eb31955fb790e8c86969c01ebd42c3134a390`.
- Model-specific frozen criteria raw SHA-256:
  `0a94fd291070d026215d42b19ef816fad4b6b0e2e8aab55de87e35ce63f4a3db`.
  Its semantic standards and thresholds match the Luna criteria; the model
  identity and cohort explanation are the only substantive setup changes.
- Model: `openai-codex/gpt-6.1-sol`, high reasoning, JSON strict mode,
  600-second requested timeout. No tested agent could read earlier outputs.

The raw prompt hash includes the source file's line endings. The harness's
LF-normalized prompt identity is
`899e81598d1a99f13df9d5e5212ea69817239e4eb3ec2f275d6c14c696482e6d`;
these identities describe the same prompt text, not different prompts.

| Run suffix | Effective duration | Completed tool calls | Observed Sol records | Retained execution issue |
| --- | --- | --- | --- | --- |
| `1` | 498.060s | 35: read 23, bash 7, write 2, edit 3 | 18 | None |
| `2` | 599.085s | 38: read 25, bash 8, write 1, edit 4 | 26 | None |
| `3` | 685.208s | 39: read 23, bash 10, write 2, edit 4 | 28 | Requested 600s timeout; no successful Pi completion |

Runs 1 and 2 have Pi exit 0 and all strict artifact/event/JSON-field/integrity
gates passing. Run 3 has `timedOut:true`, wrapper result code 124, null Pi exit
code and only the integrity gate recorded by the timeout path. The elapsed
685.208 seconds is the actual harness receipt, not a revised deadline. All
independent event summaries require the observed Sol model and report valid
event JSON, zero completed-tool errors and no forbidden reads. A passing trace
summary alone does not establish completion and does not override run 3's
timeout. Its MD/JSON hashes remain stable between independent content checking
and the final identity check after termination.

Representative commands from the repository root, with `N` replaced by 1, 2
or 3. Retained IDs must not be reused:

```powershell
uv run --script scripts/run-pi-skill-eval.py desktop-plugin-ui --prompt-file evaluations/pi-prompts/desktop-plugin-ui-evidence-naturalistic.md --run-id 20261025-desktop-ui-evidence-naturalistic-v2-sol-N --model openai-codex/gpt-6.1-sol --mode json --strict --expect-output offerings/recommendation.md --expect-output offerings/recommendation.json --expect-output-json-field offerings/recommendation.json::host_acceptance_verified=false --expect-output-json-field offerings/recommendation.json::task_empirical_tests_performed=false --timeout-seconds 600
uv run --script scripts/summarize-pi-json-events.py evaluations/runs/20261025-desktop-ui-evidence-naturalistic-v2-sol-N/events.jsonl --output evaluations/runs/20261025-desktop-ui-evidence-naturalistic-v2-sol-N/independent-event-summary.json --require-model gpt-6.1-sol --require-tool-call --fail-on-invalid-json --fail-on-tool-error --require-read ../prompt.md --forbid-read-regex '(?i)(^|[\\/])assets[\\/]examples([\\/]|$)' --forbid-read-regex '(?i)^skills[\\/](?!desktop-plugin-ui([\\/]|$))' --forbid-read-regex '(?i)^(?:[A-Za-z]:[\\/]|/|\\\\)'
uv run --script projects/desktop-plugin-ui/scripts/review-evidence-naturalistic.py --prefix 20261025-desktop-ui-evidence-naturalistic-v2-sol
```

## Semantic and evidence review

The final JSON recommendations, normalized records and Markdown narratives
were inspected. Run 1's assembly script was also read: it deterministically
renders the final JSON content and appends the helper's table. All three reuse
the helper-rendered table and run the typed checker on both final paths after
the final content changes. Their traces inspect or print `passed:true`; the
independent reviewer repeats the same typed final checks. Evidence references
resolve without imposing a hidden row count, preferred ID spelling, or minimum
number of optional patterns.

All three provide useful mechanisms, prerequisites, explicit fallback copy and
future checks for npm Codex CLI, Codex desktop, Codex IDE, Copilot CLI, Copilot
Chat, ordinary VS Code webviews and preview canvases. They cover search,
selected details, staged priority/Save/Cancel, a chart or equivalent count
table, refresh/recovery, selected CSV and Explain. They separate focused
details from the action selection, selection/drafts from authoritative business
state, and preferences from host permissions. Reload/reconnect/failure plans
include scoped restoration, version validation, lost-save reconciliation and
no blind replay. Export excludes drafts and unrelated/unselected tickets;
Explain uses explicit saved selection and an intentional draft/copy/send
boundary. Required identifiers `T-104`, `high`, `pending` and
`E_INVALID_PRIORITY` are preserved. Copy is English; no user study is claimed.

The central classification distinctions are preserved:

- Historical Codex inline chart pixels are separate from the later chart
  metadata/export formats, a human expansion report, a source-declared Expand
  handler, and the genuine failed controller-binding attempt. Capture-specific
  versions remain unknown rather than inheriting a newer installed package.
- Neither a source-declared fullscreen request nor a briefly discoverable tab
  becomes verified fullscreen/control execution. Stock IDE paint stays
  untested, and a developer-owned frontend is an optional architecture rather
  than a universal requirement or exclusion of stock UI.
- Normal never-policy decline, missing-renderer refusal and correctly blocked
  CSP actions can pass their expected negative checks. An actual unmet
  controller-bind expectation stays `observed-failed`. Unperformed queue and
  signed-in Chat checks stay `untested`.
- Real Copilot terminal controls, bare SDK negotiation and supplied callback
  outcomes keep their distinct method/action meanings. In run 2 the used
  terminal `canvases:true`/`mcpApps:false` facts have a scoped execution record,
  separate from bare-consumer false flags. Run 3 makes no positive historical
  terminal canvas-advertisement claim; its hypothetical flag warning does not
  manufacture an execution fact.
- Ordinary extension-host bridge/CSP/lifecycle behavior is not authenticated
  Copilot Chat acceptance. MCP App CSP fields are not ordinary webview
  configuration. Preview canvas exclusions remain specific to that documented
  host surface. Trust cleared while sign-in remained required; all three
  preserve the user's choice to continue without signing in.

Run 2's `CX-controls.reason` says the component was not expanded into a
controller-visible panel for checks. Read literally as an account of every
earlier discovery state, that is imprecise: `CX-bind` in the same final ledger
explicitly records the briefly listed tab, failed binding and subsequent empty
list, while `CX-human` preserves the human's visibility report. The narrative
also states failed binding. Its scoped conclusion is unverified direct
controls, not no human-visible panel or universal rendering failure. This is a
bounded wording caveat, not a contradictory capability classification or an
added hidden phrasing requirement.

All three distinguish proposed exact CS1 authored paint from host-owned chrome,
native forms/terminal controls, individually host-mapped roles and mandatory
accessibility overrides. Claimed token paths/hex bindings match the frozen
palette and trace actual bundled design-helper use. All 39 claimed unrounded
ratios independently recompute within 1e-9. Low-contrast focus/border options
and ordinary red-on-pink error text are rejected; selected/notice helper text
uses darker ink, focus has a white gap around red controls, and charts use
labels/shapes/table equivalents. H1-H10 use the exact canonical short labels
with concrete findings, fixes and next checks. These remain design review and
arithmetic, not rendered accessibility certification.

## Complete read/write-path audit

The independent audit includes every read/write/edit call, every full raw
`tool_execution_start.args.command`, shell redirection and generated script
file operation. Event summaries shorten commands, so their displayed command
previews alone were not used to approve scope. Full untruncated shell arguments
are retained in `independent-full-write-path-audit.json` for each run.

All reads stay within `../prompt.md`, the copied skill and each run's own
`work/` or exact `offerings/` outputs. No acceptance examples, prior cohorts,
repository documents, sibling skills or outside absolute paths are read.
Commands run bundled source/palette/ledger/checker utilities and local Python
inspection/assembly. No prohibited installation, extra provider call, account,
app, sign-in, actual-host UI or online-fetch action occurs.

- Run 1 writes/edits `work/facts.json` and `work/assemble_markdown.py`; shell
  redirects design values and ledger diagnostics to `work/`, writes the
  helper table there and writes the two exact `offerings/` reports. The
  assembler reads only those local files. Its final checker runs after final
  Markdown regeneration.
- Run 2 creates `work/` and `offerings/`, writes/edits `work/facts.json`,
  generates local design/ledger/check receipts and both exact final reports,
  then edits the Markdown narrative and checks both final paths. All shell
  `open()` calls inspect those local receipts/reports.
- Run 3 uses the same local roots and explicitly sets `UV_OFFLINE=1` and
  `UV_CACHE_DIR=work/uv-cache` on its script runs. Python appends/replaces the
  helper table only in `offerings/recommendation.md`. Its last command removes
  a named list of its own `work/` scratch files and `work/uv-cache`, removes
  the now-empty local directory, and rechecks both final reports. There is no
  system-temp target or outside-scope cleanup. The raw trace retains the
  removed scratch contents/actions; the reviewer does not recreate them or
  change the final artifacts.

This audit approves explicit tested-agent task paths and actions. It does not
claim to enumerate operating-system or tool-internal cache I/O invisible to
the trace. No outside-temp inspection or cleanup was performed by the reviewer.

## Retained evidence and limits

Run roots are `evaluations/runs/20261025-desktop-ui-evidence-naturalistic-v2-sol-1`,
`-2` and `-3`. Each retains `events.jsonl`, `stderr.txt`, `command.txt`, the
copied payload/manifest, harness receipts, exact final outputs, independent
event summary, independent content check, full write-path audit and final
identity receipt. Run 3's timeout result is retained without inventing the
strict completion gates that the harness did not produce.

| Run | Typed records | Official URL checks | Paths / hex bindings / ratios / H labels |
| --- | --- | --- | --- |
| 1 | 33 | 34 | 13 / 12 / 14 / 10 |
| 2 | 39 | 30 | 12 / 12 / 14 / 10 |
| 3 | 29 | 28 | 12 / 11 / 11 / 10 |

| Run | Final Markdown SHA-256 | Final JSON SHA-256 |
| --- | --- | --- |
| 1 | `18e43272af2ee229d8f3c59c6086ecc22add8cc84583307267e193247ca4afee` | `6b97ad3c824fc14779ce7d2fc18e01a85d040fa60923748c5cb7b90621fe788c` |
| 2 | `606402217f7882075a9fd0656a49cd1f786cc07fc3dfe7de7c883d414628eace` | `51b34411f563e7f11ad25056950d0f108ba68f834f32b90c113a690bf0727196` |
| 3 | `7487682ac539a602d2e27cd6c018cd6b472e68fbf96fd854d46f345f1013a5a4` | `57123024bfd77f77bf07fa63531f271fa5910dbf16f3b5f1dfc8d484ec3e25d0` |

The independent numeric reviewer was extended to recognize the outputs'
equivalent `token_path`, `pair` and `ratio_unrounded` representations. Initial
subset receipts for runs 2/3 are preserved as
`independent-content-check-initial.json`; their zero counts meant those
representations were not yet enumerated, not incorrect artifact arithmetic.
No tested artifact or frozen criterion changed. Human review remains necessary
for factual coverage, mixed claims, role thresholds and Markdown meaning.
This cohort verifies offline recommendation behavior under the named model,
not actual host rendering, signed-in Copilot readiness or universal reliability.
