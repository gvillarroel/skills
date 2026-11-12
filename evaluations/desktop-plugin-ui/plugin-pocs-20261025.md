# Executable plugin PoCs and failure-driven skill repair

Date: October 25, 2026. The user asked for actual generated plugins and repairs
to `desktop-plugin-ui` based on the PoCs' observed failures. This study tests
executable packages and interactions, not architecture-only plans.

## Method and provenance

Each forward run starts in a fresh isolated Pi workspace with only the copied
read-only runtime skill and its frozen task. Use strict JSON, observed
`openai-codex/gpt-6.1-sol`, medium, and a 900-second budget. This is the existing
explicit model exception after the recorded Spark account/provider rejection;
no global model selection changed. Each exact requested artifact is passed
with `--expect-output`. Prompts are versioned under
`evaluations/pi-prompts/desktop-plugin-ui-poc-<host>.md`.

Independent evaluators run actual generated source, native test engines,
extracted MCP servers, real app-server/RPC calls, and sandboxed browser
interactions. They do not use generated review assertions as the grader.
Failed generations and evaluator corrections remain separate. Diagnostic
copies do not become forward passes. Archive collection preserves the exact
source run and skill identity; it does not grant host acceptance.

| Subject | Files | SHA-256 | Forward scope |
| --- | --- | --- | --- |
| Baseline | 26 | `ed3f7529ae344b2bf9c29dbb73c2e3a787c99ed1ce39bca769dc747588fb66d7` | Five executable host PoCs |
| Intermediate Pi repetition | 34 | `a834d3fc90a8687caf03df636fb7d7b33ed54d0fb82c06afa0779df656a6a954` | Three Pi repetitions exposing stale Edit |
| Native/browser/package repair | 34 | `e005f79036bfe0ef156a1c7c64fceb113f5ee277f7a2217ff9fddd9e8d1f245d` | Fresh Claude native, Claude Chat, ChatGPT Desktop and Codex |
| Stateful and invocation repair | 36 | `cd60a5fb2431cbe96de7537bbb182dd0fe3cd831d23cb134c962b6fcc0bccb3b` | Three fresh Pi repetitions |
| Final preflight/report/config repair | 37 | `0b5d593f560a76a07c7b2775c40f4ca0f0adc99770859e13ad99542926abe4ae` | Three final Pi repetitions and one focused browser/SDK contract |

Keep these complete subject hashes separate. The 36-file repair resolves the
Pi race but all three generations still probe an unnecessary compiler and
fail strict. The final subject supplies a bounded, version-only runtime probe,
clarifies the requested review format, fixes JSON URL extraction and records
the verified browser TypeScript configuration. Do not pool the subjects into
a whole-skill release pass.

## Functional defects and repairs

| Observed failure | Evidence | Reusable repair |
| --- | --- | --- |
| Claude Code command never dispatches under its real event | Its own 13 tests passed using invented `name`; independent tests passed only 2/9 with the real `command` field. A real headless probe confirmed the host event. | [Native authoring](../../skills/desktop-plugin-ui/references/native-authoring.md), literal event matcher, authentic native tests and a five-file runtime starter. |
| Stale Pi Edit overwrites a newer value of the same row | All three intermediate repetitions pass their own tests but fail independent interleaving; actual installed Pi RPC reproduces the overwrite with zero model turns. | [Stateful Pi actions](../../skills/desktop-plugin-ui/references/pi-stateful-actions.md) and a dependency-free collect/version-check/synchronous-apply primitive. |
| Windows Git Bash rewrites a slash command into a path | One failed Pi attempt unintentionally tries provider work, receives an invalid-key error, then corrects invocation. `--offline` did not prevent that attempt. | Native argv/RPC invocation, explicit MSYS path-conversion guidance, registered-command checks and measured inference receipts. |
| Source checker refuses genuine portable schema URLs | Codex generation's report check rejects both published Agent Plugins schemas even with an independently verified explicit allowance. | Exact primary-host recognition and schema catalog, retaining unknown-path/spoof/credential/plain-HTTP refusal; source tests grow from 67 to 75. |
| Browser fixture contains a serialized `__name` helper | Transpiled callback fails before exercising the app. | [Browser validation](../../skills/desktop-plugin-ui/references/browser-validation.md): erasable Node 24 TypeScript or plain callbacks without Node closure helpers. |
| Local form action silently waits in a sandbox without `allow-forms` | Browser Apply/Enter tests time out until the generated app uses a direct native button action. | One explicit native click action, actual Enter/Space tests, dispatch-count assertions and a declared sandbox. |
| Valid SDK metadata or embedded text breaks a test | Whole-object RPC equality rejects `_meta.progressToken`; text regex treats bundled SDK strings as unresolved imports. | Business-field assertions, bundler metadata for externals, and actual extracted runtime execution. |
| JSON report scanning invents a trailing-backslash URL | A valid quoted URL inside a JSON command is scanned before decoding JSON escapes. | Decode JSON keys/values before URL extraction; retain duplicate-key values and plain-text behavior. Source checks now pass 81/81; report checks 38/38. |
| Correct Pi generation fails an irrelevant compiler probe | All three 36-file generations pass behavior but execute `command -v tsc`, although Pi directly loads the TypeScript extension. | [Version-only runtime probe](../../skills/desktop-plugin-ui/scripts/probe_runtime.py), 17/17 tests, safe argv and bounded Windows shim resolution. Final repetition family passes joint acceptance 2/3. |
| `App.close()` appears missing under NodeNext resolution | The pinned SDK inherits the method; identical typed source fails under NodeNext but passes ESNext/Bundler, and the real runtime method resolves. | Separate browser and test compiler configurations, DOM iterable types and genuine inherited lifecycle verification; never invent or cast away a missing method. |

The browser/package recipes also clarify two-argument `App.callServerTool`
versus the MCP client's request-schema/options signature. These are focused
repairs grounded in recorded attempts, not extra product features.

## Baseline outcomes

| PoC | Strict forward | Independent actual artifact/runtime result |
| --- | --- | --- |
| Claude Code / Desktop Code | fail, 14 tool errors | Own tests 13/13 but realistic native behavior 2/9: genuine command defect. Diagnostic corrected copy 9/9 is not a forward pass. |
| Claude Desktop Chat | fail, 11 tool errors | MCPB 11/11; extracted stdio and final scoped browser checks 53/53. |
| ChatGPT Desktop | fail, 6 tool errors | Portable package 14/14; extracted stdio and final scoped browser checks 53/53. |
| Codex | fail, 2 tool errors | Current Desktop core actual installed-plugin checks 35/35 on-request and 33/33 never; old CLI discovery 28/29 remains a bounded failure. |
| Pi | pass, 174.913 seconds | Independent state checks 116/116; actual RPC 48/48 plus JSON-print no-UI; generated scenarios independently rerun. |

Baseline run IDs are `20261025-plugin-poc-v1-<host>-sol-1`. The three later
`20261025-plugin-poc-v2-pi-sol-<1..3>` attempts all fail the same-row stale-input
check, so their joint outcome is 0/3 even though repetition 3 passes strict.
Sequential self-tests missed that race. Broad-revision and corrected same-row
evaluator records are preserved; the same-row case avoids imposing a hidden
ban on merging independent records.

## Repair validation and evidence

| Fresh case | Strict forward result | Independent final artifact/runtime result |
| --- | --- | --- |
| V3 Claude Code / Desktop Code, 34-file subject | **pass**, 153.914 seconds, zero tool errors | Generated tests 15/15, native behavior 9/9, clean manifest and real headless command dispatch with exact rows and zero inference. |
| V3 Claude Desktop Chat, same subject | **fail**, 481.348 seconds, 9 tool errors | Original MCPB 11/11 package checks; extracted stdio and sandbox browser 53/53. |
| V3 ChatGPT Desktop, same subject | **fail**, 657.269 seconds, 7 tool errors | Original portable ZIP 14/14 package checks; extracted stdio and sandbox browser 53/53. |
| V3 Codex, same subject | **fail**, 340.729 seconds, 3 tool errors | Actual installed plugin on Desktop core 0.164.0-alpha.11.1: 35/35 on-request and 33/33 never; zero model-turn events. |
| V4 Pi, 36-file subject, three repetitions | **0/3 strict/joint** | All pass 118/118 behavior; selected repetition passes actual installed RPC 57/57 including stale-input counterexample. Compiler-probe errors remain failures. |
| V5 Pi, final 37-file subject, three repetitions | **2/3 strict/joint**; repetition 1 retains 3 tool errors | All three pass independent behavior 118/118 and generated semantic checks. Selected repetition 2 passes actual RPC 57/57 and JSON-print no-UI. Its extracted delivery source ZIP repeats 118/118 and actual RPC 57/57 unchanged. |
| V5 focused browser/SDK contract, final subject | **fail**, 2 tool errors retained | Independent 31/31; delivered compiler/build/browser sequence rerun in a diagnostic copy passes, including 18/18 authored checks. |

Final Pi repetition 2 takes 241.136 seconds; repetition 3 takes 186.557 seconds.
The focused browser attempt fixes disabled text contrast measured at 4.439:1
and a test's incorrect assumption that focus survives disabling a control.
Its final real keyboard, lifecycle and bridge behavior pass; those corrections
do not erase the two strict errors. Independent final text contrast is at
least 5.4898:1 and focus contrast 10.9182:1. The earlier NodeNext, serialized
callback, three-argument App call and whole-metadata test defects do not recur.

The original full Desktop generations retain their distinct tool errors;
the focused contract is not a replacement whole-plugin pass. Generated
self-tests and reports are supporting artifacts, not the independent grader.

- [Native Claude case, receipts and evaluator correction](poc-claude-native-20261025.md).
- [Desktop MCP cases, package/browser checks and screenshots](poc-mcp-desktop-20261025.md).
- [Codex schemas, actual loader versions and form policies](poc-codex-20261025.md).
- [Pi state machine, actual RPC, race counterexample and repair](poc-pi-20261025.md).
- [Focused browser/SDK contract](poc-browser-sdk-contract-20261025.md).

Each report identifies exact commands, model, subject, required files,
positive/negative tests, read surfaces, retained failures and limits. Raw
forward workspaces stay under ignored `evaluations/runs/`; runtime evidence
and screenshots stay under `projects/desktop-plugin-ui/artifacts/plugin-pocs/`.

Reusable evaluator tools are under `projects/desktop-plugin-ui/scripts/`:

- `verify-native-poc.ts`, `probe-native-command.ts`.
- `inspect-mcp-poc-package.py`, `verify-mcp-poc.ts`.
- `verify-codex-poc.py`.
- `verify-pi-import-poc.ts`, `verify-pi-import-rpc.ts`.
- `test-pi-guarded-intent.ts`, evaluator defect-injection selftests.
- `collect-plugin-pocs.py` with safe archive/provenance/exclusion selftests.

The final 37-file source/runtime/full audit passes at
`evaluations/runs/20261025-plugin-poc-preflight-audit/report.json`, with equal
hashes in all three profiles. Local installation sync/check matches all 10,613
canonical source files. Relevant deterministic checks pass: source 81/81,
report 38/38, typed integration 41/41, runtime probe 17/17, guarded-intent
primitive 10/10 and collector 24/24. Final repository gates pass:

```powershell
uv run --script scripts/validate-pattern-ids.py
uv run --script scripts/validate-skills.py
uv run --script scripts/test-skill-independence.py
uv run --script scripts/check-repo-payload.py
uv run --script scripts/sync-local-skills.py --check
```

Pattern validation covers 1,348 canonical item IDs. Final source/report/probe
checks use their named project scripts; typed integration uses a fresh retained
run ID:

```powershell
uv run --script projects/desktop-plugin-ui/scripts/test-source-checker.py
uv run --script projects/desktop-plugin-ui/scripts/test-report-checker.py
uv run --script projects/desktop-plugin-ui/scripts/test-typed-report-checker.py --run-id 20261025-delivery-final
uv run --script projects/desktop-plugin-ui/scripts/test-runtime-probe.py
```

`git diff --check` passes. No new published example set or pattern ID was created.

## Delivered PoCs

The selected source and original runtime archives are collected in
[poc-20261025-v1](../../projects/desktop-plugin-ui/artifacts/plugin-pocs/packages/poc-20261025-v1/USAGE.md).
Its [validation guide](../../projects/desktop-plugin-ui/artifacts/plugin-pocs/packages/poc-20261025-v1/VALIDATION.md)
states the independent results and limits separately from each recorded strict
forward result. `manifest.json` preserves run identity, subject, requested model,
original paths, file sizes and SHA-256 for every source file and archive.

The five source ZIPs preserve the original workspace layout. Codex additionally
includes its local marketplace and the two exact schema fixtures required by
its authored tests. Claude Desktop supplies the original `.mcpb`, ChatGPT the
original runtime ZIP, and Codex the original `.tgz`. Dependency trees, caches,
transcripts and isolated agent state are excluded. Collected files remain
byte-identical to the selected generation; evaluators do not patch them.

The [collector](../../projects/desktop-plugin-ui/scripts/collect-plugin-pocs.py)
checks archive membership, provenance and containment. Its acceptance field
correctly remains unassessed: independent runtime checks are reported separately.
Native/Pi source ZIPs and Codex relocated execution receive separate delivery
checks. Browser checks already execute the exact extracted original archives.

The independent delivery review passes 214 checks across 98 source files,
five exact ZIP inventories and three original runtime archives. Actual delivered
Claude ZIP extraction passes 23 integrity checks, strict native validation,
generated 15/15, independent 9/9, artifact evaluator 14/14 and real headless
dispatch with zero inference. The selected Pi ZIP hash matches its tested
extraction; Codex's actual final extracted ZIP repeats 35/35 installed-loader
checks. Receipts are `delivery-integrity-v1/result.json`,
`delivery-native-audit-20261025-v1/result.json`,
`pi-packaged-verification/v5-rep2/` and
`codex-packaged-current-forms/result.json` in the project PoC artifact root.

## Acceptance boundaries

Actual native command execution and backend/RPC transport are established only
for named checks and versions. Browser fixtures establish delivered component
behavior under their declared sandbox, including real keyboard, focus, layout,
contrast, errors and retry. They do not establish signed-in Claude/ChatGPT UI
installation, every host's generated sandbox, accessibility user testing or
representative-user usability. The older Codex loader failure is not a universal
product exclusion. Keep overall skill status `validating` for broader gaps and
retained strict failures while delivering the functioning PoCs.
