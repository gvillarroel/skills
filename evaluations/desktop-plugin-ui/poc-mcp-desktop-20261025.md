# Executable MCP Desktop PoCs and browser-workflow repair

Date: October 25, 2026. This record covers actual generated plugins for Claude
Desktop ordinary Chat and ChatGPT Desktop local threads. It excludes Claude's
Code tab. Package/protocol/browser fixture acceptance is separate from actual
signed-in host installation and representative-user testing.

## Frozen generation contract

The [Claude prompt](../pi-prompts/desktop-plugin-ui-poc-claude-desktop.md),
[ChatGPT prompt](../pi-prompts/desktop-plugin-ui-poc-chatgpt-desktop.md) and
[independent criteria](poc-mcp-desktop-criteria.md) were frozen before artifacts.
Each task requests editable TypeScript, locked dependency metadata, bundled
server/UI, correct host manifests, a runnable smoke test, a concise Nielsen
review and a complete distribution archive. Both implement the same immutable
three-ticket queue: a model-visible opening tool and an app-only filtering tool.
Draft selection, Apply, Cancel and Retry have observable contracts.

Outer model: observed `openai-codex/gpt-6.1-sol`, medium, strict JSON runtime
profile, 900-second budget. The existing Spark-unavailable model exception is
preserved. The copied skill is read-only and all exact outputs are required.
Task-local package/primary-documentation downloads are allowed; other provider
calls, external account activation and global configuration are forbidden.

| Subject | Files | Runtime SHA-256 | Run IDs |
| --- | --- | --- | --- |
| Baseline V1 | 26 | `ed3f7529ae344b2bf9c29dbb73c2e3a787c99ed1ce39bca769dc747588fb66d7` | `20261025-plugin-poc-v1-{claude-desktop,chatgpt-desktop}-sol-1` |
| Repaired V3 | 34 | `e005f79036bfe0ef156a1c7c64fceb113f5ee277f7a2217ff9fddd9e8d1f245d` | `20261025-plugin-poc-v3-{claude-desktop,chatgpt-desktop}-sol-1` |

## Baseline results retained

| Host | Strict generation | Package validation | Independent runtime/browser | Joint |
| --- | --- | --- | --- | --- |
| Claude Desktop Chat | fail: 11 tool errors; 868.275 seconds | 11/11 pass | 53/53 pass | fail |
| ChatGPT Desktop local | fail: 6 tool errors; 653.104 seconds | 14/14 pass | 53/53 pass | fail |

Both models produced all requested artifacts and clean final runnable packages.
The strict errors are retained despite correct final code. No evaluator repair
of those PoCs was used. Both copied skill payloads remain unchanged; event JSON
and observed models are valid. Summarized traces retain the tool errors.

The original archives remain in their ignored run workspaces:

| Archive | Bytes | SHA-256 |
| --- | --- | --- |
| Claude `poc/releases/queue-review.mcpb` | 365052 | `fd9f2dc2e8be19c891e5e9245443c8128a3dd23b8b0f75a7951c02f2655896b8` |
| ChatGPT `poc/releases/queue-review-chatgpt.zip` | 281181 | `900f1f564adf1b233427cf6cbab75ca5654c2765f8b3dd4a5c05a8bfdc634f60` |

Claude locks MCP Apps 1.7.5 / MCP SDK 1.32.2; ChatGPT locks MCP Apps 2.0.3 /
MCP SDK 1.32.2. These observed working combinations do not establish every API
combination. The evaluator uses its separately locked SDK 1.32.1 and Playwright
1.64.1; real wire interoperability is exercised rather than inferred.

## What actually failed and what was promoted

The common browser failures were not a broken delivered bridge. A `tsx`
transformation injected `__name` into callbacks serialized by Playwright; that
helper did not exist in the browser realm. The models then hit timeouts while
relying on native form submission in a sandbox without `allow-forms`. Their
final apps use direct primary-button handlers and pass real Enter and Space
activation. ChatGPT's final tests run through Node 24 native TypeScript; Claude's
own fixture supplies a host-realm helper, but the independent fixture supplies
none and still passes. Neither delivered app is patched with a fake host API.

Claude additionally copied a three-argument MCP client tool-call signature into
the two-argument browser `App.callServerTool` API, producing TS2554. A generated
assertion compared an entire RPC parameter object to a two-field literal and
rejected valid `_meta.progressToken` metadata. A generated bundle regex treated
SDK documentation/string content as an external import. Optional npm audit
commands returned nonzero and one ambiguous text edit failed. ChatGPT retained
two failed exact-text documentation edits in addition to its browser errors.

The owning skill now contains
[browser-validation.md](../../skills/desktop-plugin-ui/references/browser-validation.md)
with a standard-bridge fixture recipe, Node 24 callback guidance, correct SDK
signature distinction, semantic RPC assertions, sandbox/native-control rules,
controlled async/recovery checks and measured layout/contrast. A bridge-pattern
pointer and root-owned direct routing make it discoverable. Root-owned portable
packaging guidance covers structural bundle metadata and clean extraction rather
than broad import-string regexes. No new universal host restrictions were inferred.

## Independent verification method

[Package inspection](../../projects/desktop-plugin-ui/scripts/inspect-mcp-poc-package.py)
checks archive path safety, root manifests and declared runtime files, portable
Agent Plugins 1.0.0 schemas, official pinned MCPB CLI 2.1.2 validation, contained
working directory and literal launch substitution. It extracts into a fresh
project-artifact directory outside the generated source/dependency tree.

[Runtime verification](../../projects/desktop-plugin-ui/scripts/verify-mcp-poc.ts)
starts that extracted package with installed Node only. A real MCP client checks
initialization, tools/resources, MIME, resource association, app-only metadata,
exact records/counts/text fallback for all filters, invalid/missing filters and
unknown tools, immutable reopening, and delivered HTML bytes.

The actual HTML runs unchanged in an opaque sandboxed iframe through a real
standard MCP Apps handshake. The browser fixture forwards direct tool calls to
the real extracted server and injects controlled failures. It checks draft and
Cancel dispatch counts, held-response busy/duplicate prevention, error/data/draft
preservation, Retry, native Tab/Enter/Space, visible focus, initialization failure,
320px/900px overflow and computed text contrast at both widths, tool failure and
initialization failure. Background alpha layers are composed; group opacity is
recorded as a separate manual-review limitation. Enabled baseline text is opaque.
It blocks
browser network requests, captures errors, and rejects model-message/sampling
requests. It does not fabricate `window.openai` or replace the delivered SDK.

Both baseline plugins pass the final 53 checks. Earlier 47/48/51-check reports are
preserved; adding explicit Enter, Space and computed focus/both-width/error contrast
checks was evaluator coverage expansion on unchanged generated artifacts, not
a model reroll or weakened acceptance rule.

The independent Edge/Chromium fixture reports build `156.0.4314.42`. Both PoCs
have a measured minimum enabled text contrast of 5.124406531604723 and focus
outline contrast of 7.378543797130064 in this fixture. Literal authored CSS hex
values belong to ColorSet 1. Native control internals/accessibility overrides
and surrounding host chrome remain separately scoped. Manual screenshot
inspection confirms readable English labels/values, visible focus and no clipping
at 320/900px, plus understandable initialization recovery.

Selftests: [package evaluator](../../projects/desktop-plugin-ui/scripts/test-mcp-poc-package.py)
5/5 accepted valid/rejected malformed fixtures, including traversal refusal;
[runtime evaluator](../../projects/desktop-plugin-ui/scripts/test-mcp-poc-runtime.ts)
2/2 accepts the valid 53-check fixture and rejects a Cancel implementation that
dispatches a request. A parent-directory preflight error in evaluator setup was
corrected before PoC grading; it is not a generated-plugin failure.

Earlier browser-evaluator runs used Playwright's default profile/temp location,
so they did not establish workspace-only scratch placement. The evaluator was
corrected before V3 inspection: set `TMP`, `TEMP`, `TMPDIR` and browser cache under
its output before importing/launching Playwright, disable Node compile caching,
and drop inherited Node module/loader paths for clean server startup. Baseline
artifacts were then rechecked unchanged: both pass 53/53 in the final
`*-v1-runtime-scoped` folders. Reports record the actual task-local temporary
directory entries observed after launch. The two positive/negative selftests
also pass with this corrected scope (`20261025-v5-scoped-temp`). No generation
trace or generated package was altered to obtain these evaluator results.

## Reproduce inspection

Each harness manifest records the exact generation command and every required
output. V3 uses the same prompts and outputs as V1; subjects are not pooled.
For example, from the repository root:

```powershell
uv run --script projects/desktop-plugin-ui/scripts/inspect-mcp-poc-package.py --poc evaluations/runs/20261025-plugin-poc-v1-chatgpt-desktop-sol-1/workspace/poc --kind chatgpt-desktop --output projects/desktop-plugin-ui/artifacts/plugin-pocs/chatgpt-desktop-v1-package
node projects/desktop-plugin-ui/scripts/verify-mcp-poc.ts projects/desktop-plugin-ui/artifacts/plugin-pocs/chatgpt-desktop-v1-package/package-review.json projects/desktop-plugin-ui/artifacts/plugin-pocs/chatgpt-desktop-v1-runtime-scoped
uv run --script projects/desktop-plugin-ui/scripts/test-mcp-poc-package.py --run-id 20261025-v1
node projects/desktop-plugin-ui/scripts/test-mcp-poc-runtime.ts 20261025-v5-scoped-temp
```

Use fresh output/run IDs: evaluators preserve existing evidence. Claude uses
`--kind claude-desktop`. Screenshots are under
`projects/desktop-plugin-ui/artifacts/plugin-pocs/screenshots/<runtime-run>/`;
the final baseline folders are `claude-desktop-v1-runtime-scoped` and
`chatgpt-desktop-v1-runtime-scoped`. Reports, archive inventories, launch commands,
stdio stderr and bridge calls are in matching package/runtime folders.

Primary contracts were fetched before evaluation: [OpenAI packaging](https://developers.openai.com/plugins/build/plugins),
[desktop-only local MCP](https://developers.openai.com/plugins/deploy/desktop-only),
[MCPB manifest](https://raw.githubusercontent.com/modelcontextprotocol/mcpb/main/MANIFEST.md),
[Claude local MCP Apps](https://claude.com/docs/connectors/building/mcp-apps/getting-started),
[portable plugin schema](https://agent-plugins.org/schemas/1.0.0/plugin.schema.json),
[portable MCP schema](https://agent-plugins.org/schemas/1.0.0/mcp.schema.json).

## Repaired-subject follow-up

Fresh V3 generations use the unchanged prompts on the frozen 34-file subject.
No live Desktop account installation, permission flow, native loader or host UI
acceptance is claimed by the following fixture results.

| Host | Strict generation | Package checks | Independent runtime/browser | Manual review | Joint |
| --- | --- | --- | --- | --- | --- |
| Claude Desktop Chat | fail: 9 tool errors; 481.348 seconds | 11/11 pass | 53/53 pass | pass | fail |
| ChatGPT Desktop local | fail: 7 tool errors; 657.269 seconds | 14/14 pass | 53/53 pass | pass | fail |

Both final archives start from clean extractions with Node only, include their
registered UI exactly, return the correct immutable records/counts and pass
all draft, Apply, Cancel, busy, Retry, keyboard, focus, contrast and layout checks.
The final original archives are:

| Archive | Bytes | SHA-256 |
| --- | --- | --- |
| Claude `poc/releases/queue-review.mcpb` | 364624 | `d058ce737e539cba8312a338dc531c9d810d52fa5841132479c2f4fbc5eb0d79` |
| ChatGPT `poc/releases/queue-review-chatgpt.zip` | 367503 | `5f6df75e5da2c599ab3a7049c4de9531261af18d4dd1d08070a4044ebd03f466` |

V3 evidence folders use `claude-desktop-v3-package`, `claude-desktop-v3-runtime`,
`chatgpt-desktop-v3-package`, and `chatgpt-desktop-v3-runtime`. Screenshots use the
matching runtime names under `artifacts/plugin-pocs/screenshots/`. All six success,
narrow-layout and initialization-error screenshots were manually inspected.
Both text minima remain 5.124406531604723; focus contrast is 10.19150880927122 for
Claude and 7.378543797130064 for ChatGPT. Actual Playwright profile/artifact
directories were observed inside each runtime output's `tmp/`.

The earlier `__name`, sandbox form-submit, three-argument App call and complete
RPC-object equality failures do not recur in the V3 traces. New retained errors
include missing browser installation preflight, incomplete TypeScript Node/DOM
library configuration, a guessed upstream example URL returning 404, brittle
HTML marker/text-whitespace assertions, one ambiguous source edit and optional
npm audit findings chained into otherwise successful functional commands.
Both models also encountered TS2339 on `App.close` under NodeNext. This last
failure required the declaration-resolution diagnosis below; it is not proof
that the selected SDK has no close API. Final delivered PoCs remain unchanged
by the evaluator, and these repaired artifacts do not erase their strict errors.

## Pinned lifecycle/type-resolution diagnosis

The [read-only probe](../../projects/desktop-plugin-ui/scripts/probe-mcp-sdk-lifecycle.ts)
uses the actual V3 ChatGPT PoC's installed SDK and TypeScript. It writes only an
ignored project-artifact fixture. The diagnosed installation is TypeScript
5.9.3 with @types/node 24.10.1; this is not a TypeScript 7 result. The identical typed source constructs `App`
and calls its genuine `connect`, `callServerTool` and `close` methods:

| Configuration or check | Actual result |
| --- | --- |
| NodeNext module/resolution, skipLibCheck true | exit 2: TS2339 says close does not exist |
| ESNext module / Bundler resolution, same typed source | exit 0; no diagnostics |
| Actual App 1.7.5 runtime instance | close is a function and its promise resolves |
| NodeNext with library checking enabled | TS2834 explicitly identifies extensionless relative imports in app.d.ts; inherited members then appear missing |

The declaration chain is `App -> ProtocolWithEvents -> MCP SDK Protocol`, whose
declaration has `close(): Promise<void>`. Primary
[pinned App 1.7.5 source](https://raw.githubusercontent.com/modelcontextprotocol/ext-apps/v1.7.5/src/app.ts)
uses `this.close()` during failed connection cleanup. That same source makes
`PostMessageTransport(window.parent, window.parent)` its default transport, so
the V3 ChatGPT explicit equivalent is a route/style deviation rather than
evidence of unsupported host behavior. Current host auto-detection claims still
require their selected SDK/host version and actual client checks.

Reproduce the diagnostic:

```powershell
node projects/desktop-plugin-ui/scripts/probe-mcp-sdk-lifecycle.ts evaluations/runs/20261025-plugin-poc-v3-chatgpt-desktop-sol-1/workspace/poc projects/desktop-plugin-ui/artifacts/plugin-pocs/lifecycle-sdk-175
```

Use a fresh output path. Existing raw results are
`projects/desktop-plugin-ui/artifacts/plugin-pocs/lifecycle-sdk-175/result.json`
and `NodeNext-check-libraries-stdout.txt`. Do not promote a false claim that
App1.7.5 lacks close, silence the inherited API with casts, or force a different
host transport merely to conceal a compiler resolution problem. A focused
fresh SDK/browser contract prompt and criteria were prepared separately from
the full-plugin cohorts; they do not reuse these artifacts as hidden input.

A fresh read-only diagnostic at `artifacts/plugin-pocs/lifecycle-sdk-175-pinned/`
also records actual package identities directly in its JSON: TypeScript 5.9.3,
@types/node 24.10.1, MCP SDK 1.32.2 and MCP Apps 1.7.5. It reproduces the same
NodeNext failure, Bundler success and real inherited-close resolution. The
focused prompt's initial draft compiler pins were corrected to this environment
before its first forward run; no TypeScript 7 result is claimed.

The fresh 37-file subject was subsequently tested once with that focused
contract. Its final fixture passes 31/31 independent checks and its delivered
18-check browser test repeats successfully in a separate copy; the strict run
still fails on two retained selftest errors. See the
[focused SDK/browser report](poc-browser-sdk-contract-20261025.md) for the exact
subject, inherited API proof, error classification and evidence scope. This
additional fixture does not replace or alter either V3 full-plugin archive.
