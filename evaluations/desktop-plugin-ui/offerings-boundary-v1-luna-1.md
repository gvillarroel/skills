# Capability-offerings boundary evaluation, v1

Evaluated on October 25, 2026. **Strict: fail (0/1). Independent manual acceptance: fail (0/1). Joint: fail (0/1).** The single authorized attempt is retained without a retry, output repair, prompt change or frozen-bundle edit. Correct final calculations and checker success do not erase the execution failure or the missing historical records.

## Frozen subject and command

- Run ID: `20261025-desktop-ui-offerings-boundary-v1-luna-1`.
- Skill: `desktop-plugin-ui`, runtime profile, 21 files. Parent-announced source/runtime/full SHA-256: `26b12b4879ba0e4663b7d225bba066424f1baa1dee7d1461ba1c84a4de1060a5`. The harness copied that digest and recorded identical before/after digests with no added, removed or modified files.
- Prompt: [offerings-boundary](../pi-prompts/desktop-plugin-ui-offerings-boundary.md), source-byte SHA-256 `2b400960ed2e9ad88166176279f6de7c68d577d4ecc2a54b58103667077647d0`.
- Frozen [review criteria](offerings-review-criteria.md), SHA-256 `4e6d0d0a0f85c04cc7a73c4a89a8ae8d81f8a4caf8c87b6f9658832173b4d590`.
- The harness normalizes prompt newlines when reading. Its 1,995-byte LF text has SHA-256 `432f2b6261f71a7085bfde09fb7ef29d0c212109d82ba41b73ff774a6f4656e7`. The source has one CRLF; the Windows copied prompt has CRLF throughout. Normalized text is identical. These are byte-serialization differences, not revised instructions.

```powershell
uv run --script scripts/run-pi-skill-eval.py desktop-plugin-ui --prompt-file evaluations/pi-prompts/desktop-plugin-ui-offerings-boundary.md --model openai-codex/gpt-5.6-luna --mode json --strict --timeout-seconds 600 --run-id 20261025-desktop-ui-offerings-boundary-v1-luna-1 --expect-output offerings/boundary.md --expect-output offerings/boundary.json --expect-output-json-field offerings/boundary.json::host_acceptance_verified=false --expect-output-json-field offerings/boundary.json::task_empirical_tests_performed=false
```

The documented Luna exception was used. Pi 1.4.0 ran on Windows with the harness's isolated skill flags. Duration was 107.258 seconds; Pi exited 0, while evaluation failed its events gate. Artifacts, false Boolean fields and skill integrity passed.

## Trace and failure classification

The required trace review was run with:

```powershell
uv run --script scripts/summarize-pi-json-events.py evaluations/runs/20261025-desktop-ui-offerings-boundary-v1-luna-1/events.jsonl --require-model gpt-5.6-luna --fail-on-invalid-json --fail-on-tool-error
```

All 13 model records identify `openai-codex` / `gpt-5.6-luna`. There are zero invalid JSON lines and zero invalid event records. The 22 completed tool calls comprise 11 reads, nine shell calls and two writes. One shell call failed at event line 255:

```bash
uv run --script skills/desktop-plugin-ui/scripts/check_sources.py --list-sources > /tmp/desktop-plugin-ui-sources.json && python -c "import json; print(json.load(open('/tmp/desktop-plugin-ui-sources.json'))['sources'])"
```

Python raised `FileNotFoundError` for the absolute `/tmp` path. This is an agent command/path portability failure in the Windows shell/Python combination, not a host UI limitation, provider outage or failure of the source checker. The trace does not establish a shared mapping of that shell path and Python's absolute path. The original error and subsequent completion remain in the run. No rerun is warranted under the frozen protocol.

The recorded reads begin with `../prompt.md`, then `SKILL.md`, followed by only four relevant references (`capability-offerings`, `codex-limits`, `usability-and-color`, `evidence-and-probing`), ColorSet 1, three bundled scripts and the generated JSON. The observed read surface contains no acceptance gallery, repository documentation, sibling skill, account file or host profile. This is a statement about the recorded read surface; the failed temporary-path command is not a proof of complete filesystem isolation. No network, installation, host action, additional provider or UI prototype was used. Copilot provider prompts consumed by this evaluation: zero.

## Independent content review

| Area | Outcome | Evidence and limit |
| --- | --- | --- |
| Seven rollout claims | Pass for the core corrections | Separates npm CLI from desktop/core/IDE; transport from pixels; opt-in from interaction; plugin-bundle discovery from direct IDE MCP; method-specific callbacks; the exact root-prefixed token; and the unsafe focus color. It offers text/structured completion and conditional component/webview routes without a blanket stock-UI exclusion. |
| Historical record coverage | **Fail** | Assessment 3 cites serving-process `openai/form` advertisement and flat-form normalization, but none of the seven historical rows records those results. Assessment 2 also cites the current connected chart metadata result without its own historical row. Existing records cover earlier standard elicitation/resource transport, a refused handshake, bounded desktop paint, two nested-schema failures and Copilot callbacks. The frozen criterion requires each empirical historical claim used to have a scoped record; checker validation of existing rows cannot certify omitted rows. |
| Process and value semantics | Partial | Serving-process identity appears in the proposed validation, but the PID-bound serving/idle distinction is not explained. The Copilot `false` versus `null` callbacks are correct, but legitimate accepted Boolean `false` as data is not made explicit. These are recorded as explanatory gaps, without inventing a required phrase or a new callback result. |
| State and persistence | Partial | Authoritative server state, preserved drafts on error, cancellation, version/stale-edit checks and separate session/server/restart validation are described. Reconnect/reload ownership for local drafts, selection and preferences is not developed. No restart durability is claimed. |
| Design helper and arithmetic | Pass | Actual diagnostic calls reject `red.status` with `unknown_token_path` and exit successfully in diagnostic mode. Subsequent helper calls resolve `colors.red.status` and `colors.red.status.value` to `#e8002a`, calculate original/repair contrasts and retain the original palette. Eleven final binding paths resolve to their stated values. |
| English, ownership and heuristics | Pass | Concrete Save, Cancel, Explain, Export, error, unavailable-UI and recovery copy preserves `T-104`, `high` and `E_INVALID_PRIORITY`. All H1-H10 IDs and canonical labels are present and queue-specific. Default ColorSet 1 is explicit. Authored component paint is separated from host chrome/forms/accessibility overrides. No user test or rendered accessibility result is claimed. |
| Final report checker | Pass within its scope | The post-write call checks both exact artifacts and returns `passed:true`, 24 URL occurrences and seven historical records. An independent copied-bundle run with `--fail-on-findings` produces the same clean result. The 24 occurrences comprise 12 source URLs repeated across Markdown and JSON. |

The independent report-check command ran from the isolated workspace:

```powershell
uv run --script skills/desktop-plugin-ui/scripts/check_reports.py offerings/boundary.md offerings/boundary.json --fail-on-findings
```

All five final ratios were independently recomputed using the sRGB formula, with zero numeric difference from the supplied values (tolerance 1e-9):

| Foreground / background | Unrounded ratio | Stated use and result |
| --- | ---: | --- |
| `#333e48` / `#ffffff` | 10.918238644424665 | Ordinary text, 4.5 minimum: pass. |
| `#333e48` / `#ffccd5` | 7.720736540005823 | Ordinary error text, 4.5 minimum: pass. |
| `#e8002a` / `#ffccd5` | 3.326162240606473 | Ordinary text, 4.5 minimum: fail; retained as a redundant status accent. |
| `#cfcfcf` / `#ffffff` | 1.5579550563651179 | Sole essential focus cue, 3 minimum: fail. |
| `#9e1b32` / `#ffffff` | 7.9046884551695875 | Allowed focus repair, 3 minimum: pass. |

The output files contain valid middle-dot/ellipsis punctuation, not replacement characters; a terminal decoding artifact did not affect authored English copy. These are token calculations and document inspections, not observations of host paint.

## Retained evidence and limits

The ignored run directory is `evaluations/runs/20261025-desktop-ui-offerings-boundary-v1-luna-1/`. It retains the manifest, command, prompt, full JSONL events, stderr, all four harness gate reports, evaluation result, model-trace summary, independent report-check JSON and independent numeric/binding-check JSON. Outputs remain unchanged:

- `workspace/offerings/boundary.md`: 10,888 bytes, SHA-256 `bcb10457248590fb53a48bfaa425992308edc33a363d7cf1211f8368509c04cc`.
- `workspace/offerings/boundary.json`: 24,432 bytes, SHA-256 `99002be572c90a4c71a7e39ced95ac03b4bd2f7e819e5ea6964d87b71ec93d43`.

Usage reported by the model trace is 45,181 input, 14,913 output and 264,576 cached-read tokens, total 324,670. This OpenAI forward test does not consume a Copilot provider prompt. It is one boundary attempt on this payload, not a host comparison, a new empirical UI result, a user study, or evidence for a different payload's release acceptance. Both requested task flags remain Boolean false.

The existing Copilot feature-study inventory verifies CLI executable paths only: `C:\Users\villa\AppData\Local\Microsoft\WinGet\Links\copilot.EXE` and the task-local `projects/desktop-plugin-ui/artifacts/cross-assistant/copilot/cli103/package/copilot.exe`, both version 1.0.103. No standalone GitHub Copilot desktop-app executable path was verified. The VS Code Copilot Chat extension is a separate surface; Microsoft consumer `copilotapp.exe` must not fill that evidence gap. No additional app was installed or authenticated for this report.
