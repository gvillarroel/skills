# Capability-offerings boundary evaluation, v2

Evaluated on October 25, 2026. **Strict: pass (1/1). Independent manual acceptance: fail (0/1). Joint: fail (0/1).** This is one fresh attempt on the revised v2 subject, using the original prompt and criteria. It is not a retry of v1: [the v1 failure](offerings-boundary-v1-luna-1.md) remains separately recorded and is not pooled with this result. No post-run output repair, rerun or frozen skill edit was performed.

## Frozen subject and command

- Run ID: `20261025-desktop-ui-offerings-boundary-v2-luna-1`.
- Skill runtime profile: 22 files, SHA-256 `42df224d120f4bfd71445670e55c25891cb8e540eb8a2ec6c21fb8ee7a9d34f6`. The parent announced identical source/runtime/full digests. A preflight runtime copy matched before launch; the actual run manifest and before/after skill-integrity digests matched it too.
- Revision: added `references/report-authoring.md` and the entry-point route to it. The new procedure covers evidence-ledger reconciliation, mechanism-specific contracts and portable scratch paths.
- Unchanged [boundary prompt](../pi-prompts/desktop-plugin-ui-offerings-boundary.md), raw source SHA-256 `2b400960ed2e9ad88166176279f6de7c68d577d4ecc2a54b58103667077647d0`.
- Unchanged [frozen criteria](offerings-review-criteria.md), SHA-256 `4e6d0d0a0f85c04cc7a73c4a89a8ae8d81f8a4caf8c87b6f9658832173b4d590`.
- The harness reads the prompt with universal-newline normalization. Its 1,995-byte LF representation has SHA-256 `432f2b6261f71a7085bfde09fb7ef29d0c212109d82ba41b73ff774a6f4656e7`, identical in text to the source/copy. This byte-serialization distinction was already present in v1.

```powershell
uv run --script scripts/run-pi-skill-eval.py desktop-plugin-ui --prompt-file evaluations/pi-prompts/desktop-plugin-ui-offerings-boundary.md --model openai-codex/gpt-5.6-luna --mode json --strict --timeout-seconds 600 --run-id 20261025-desktop-ui-offerings-boundary-v2-luna-1 --expect-output offerings/boundary.md --expect-output offerings/boundary.json --expect-output-json-field offerings/boundary.json::host_acceptance_verified=false --expect-output-json-field offerings/boundary.json::task_empirical_tests_performed=false
```

The documented Luna exception was used. Pi 1.4.0 completed in 112.539 seconds with exit 0. All four gates passed: artifacts, events, exact false Boolean fields and skill integrity. The final outputs exist at their requested paths.

## Required trace review

```powershell
uv run --script scripts/summarize-pi-json-events.py evaluations/runs/20261025-desktop-ui-offerings-boundary-v2-luna-1/events.jsonl --require-model gpt-5.6-luna --fail-on-invalid-json --fail-on-tool-error
```

The summary passes. All 17 model records identify `openai-codex` / `gpt-5.6-luna`. There are zero tool errors, invalid JSON lines and invalid event records. The 25 completed calls comprise 11 reads, 11 shell calls, two writes and one successful edit of generated JSON. The edit adds the synthetic-state historical record before the final checker and reread; it is part of the original attempt, not an evaluator repair.

The trace begins with the prompt and `SKILL.md`. Subsequent reads are limited to five relevant references (`capability-offerings`, `copilot-limits`, `usability-and-color`, `codex-limits`, `report-authoring`), the report checker and the generated reports. Palette inspection occurs through the bundled value helper. A shallow listing stays inside the task workspace. No acceptance gallery, repository documentation, sibling skill, external artifact, account profile or global settings file appears in the recorded read surface. No network, installation, host/account action, additional provider, UI prototype or host paint test was performed. Copilot provider prompts: zero.

The value helper produces expected diagnostic `passed:false` results for `red.status` and an exploratory `interface.focus.value` path without a tool error. The agent reads the token catalog and uses valid final paths. These are successful diagnostic executions, not hidden strict failures. The v1 `/tmp` command is absent from v2.

## Independent acceptance review

| Area | Outcome | Evidence and limits |
| --- | --- | --- |
| Seven rollout corrections | Pass for the main decisions | Separates CLI/package/core/frontend versions and persistence; resource bytes from UI/canvas pixels; opt-in/callbacks from interaction; IDE bundle discovery from direct MCP; method-specific `false`/`null`; root-prefixed token paths; and the focus-contrast trap. Useful text/tool fallbacks and conditional component/webview routes are provided without blanket stock-UI exclusions. |
| Used historical observation coverage | **Fail** | Markdown line 31 uses `mcpApps:false` / `canvases:true` to discuss negotiation. The terminal-form row records dialogs and return values but not these capability flags. The bare SDK row records MCP Apps and canvases both false, which is a different consumer/result. No row records the used terminal CLI true-canvas negotiation. The original frozen rule requires a scoped historical record for each empirical claim used; neither a correct nearby callback row nor a different consumer's flags satisfies it. |
| Improvements over v1 | Pass as specific improvements | Rows now cover PID-bound serving-process advertisement and idle-connection omission, flat-form normalization/nested-schema refusal, synthetic state/version/stale-edit results, and the current chart metadata result. Unknown capture build remains unknown. These improvements do not remove the remaining capability-ledger omission. |
| Mechanism and evidence boundaries | Mostly correct; cautions | MCP Apps, terminal forms, webviews, canvases and custom frontends are separated. SDK refusal is tied to the bare consumer and its unsupported-host error; no rich dialog paint is inferred. Some historical rows combine two core versions or successful normalization with schema refusal. They retain explicit mappings, so grouping alone is not used as a new hard gate; separate records would improve clarity. The desktop-chart record also mentions failed folder discovery while its evidence emphasizes successful direct-route paint. |
| State and values | Partial | Server ownership, client draft, invalid/stale saves, cancellation and independent restart checks are explicit. PID versus idle is now present in the ledger. Reload/reconnect handling for drafts, selection and preferences remains brief. Copilot method-specific `false`/`null` results are correct, but legitimate accepted Boolean `false` as data is not stated explicitly. These explanatory gaps are retained without inventing a required phrase or new result. |
| Palette and calculations | Pass | Default ColorSet 1, all seven final bindings and two additional claimed paths resolve exactly. Actual helper calls reject the bad path, identify `colors.red.status`, calculate the original focus failure and validate an allowed unchanged-palette repair. All four final unrounded ratios independently match exactly. |
| English, ownership and H1-H10 | Pass | Concrete Save, Cancel, Explain, Export, error, recovery and fallback copy preserves `T-104`, `high` and `E_INVALID_PRIORITY`. All ten canonical heuristic IDs/labels are queue-specific. Authored iframe/webview paint is separated from host chrome/forms, themes and accessibility overrides. No user-study result is claimed. |
| Final source/row checker | Pass within its scope | Both exact artifacts were checked after the generated JSON edit. The final trace returns `passed:true`, 32 URL occurrences and 12 historical records, followed by a final JSON read. An independent copied-bundle checker returns the same result. Existing-row validity does not prove that all used observations are recorded. |

The manual failure is a missing observation scoped to its actual mechanism. It does not depend on a hidden row ID, a preferred prose style, a fixed number of records, a preferred architecture or a new post-run requirement. The CLI terminal flags are factual in the bundle; their omission from the required ledger is the failure. The bare SDK's false/false record must not be treated as the CLI false/true result.

## Independent checker and numeric inspection

The evaluator ran this command from the isolated workspace without modifying outputs:

```powershell
uv run --script skills/desktop-plugin-ui/scripts/check_reports.py offerings/boundary.md offerings/boundary.json --fail-on-findings
```

Result: `passed:true`, no findings, 32 exact official URL occurrences (16 source URLs repeated across Markdown/JSON), and 12 existing historical records. The agent's initial check counted 11 rows; after its own reconciliation edit the final check counted 12. The final artifact hashes match the harness's retained outputs.

All seven final binding entries match the frozen palette. The additional `interface.feedback.critical.text` and `interface.state.focus` paths resolve to `#e8002a` and `#cfcfcf`. Independent sRGB arithmetic gives zero difference from each supplied ratio, within the frozen 1e-9 tolerance:

| Foreground / background | Unrounded ratio | Stated use and threshold decision |
| --- | ---: | --- |
| `#cfcfcf` / `#ffffff` | 1.5579550563651179 | Essential focus cue, 3.0: fail. |
| `#9e1b32` / `#ffffff` | 7.9046884551695875 | Allowed focus repair, 3.0: pass. |
| `#333e48` / `#ffccd5` | 7.720736540005823 | Ordinary error text, 4.5: pass. |
| `#e8002a` / `#ffccd5` | 3.326162240606473 | Ordinary error text, 4.5: fail; use as redundant accent. |

These are opaque sRGB calculations and document checks. They do not measure host compositing, keyboard focus, forced-color behavior, screen-reader output or actual rendered accessibility.

## Retained artifacts and limits

The ignored run directory is `evaluations/runs/20261025-desktop-ui-offerings-boundary-v2-luna-1/`. It retains the manifest, prompt, command, complete events/stderr, artifact/event/JSON-field/integrity gates, evaluation result, required model summary, independent report-check result and independent numeric/binding result. Exact outputs are unchanged:

- `workspace/offerings/boundary.md`: 15,918 bytes; SHA-256 `3d43a0cd0fac949dffe4bf03863322414d22043f00579e5d50c61077bf9c0b5f`.
- `workspace/offerings/boundary.json`: 25,422 bytes; SHA-256 `deabd718b5b6c1e7240caddd8da43b80f6ff395517bb1e89046237fb7dc69e04`.

Both requested flags remain Boolean false. Trace usage is 50,683 input, 15,349 output and 408,960 cached-read tokens, total 474,992. This is an OpenAI isolated forward test with zero Copilot provider inference, not a new assistant-host experiment or current account-acceptance result. One strict pass does not satisfy joint acceptance while the independent historical-record criterion fails. No additional app was installed or authenticated, and no prior payload's results are pooled into this v2 boundary outcome.
