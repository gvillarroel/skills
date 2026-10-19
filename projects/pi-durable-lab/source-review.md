# Pi Durable source review

Reviewed on 2026-10-19. This memo separates the installed release from development documentation; it is a source review, not a record that every item below passed a local test. The executable test results belong in the lab's validation artifacts.

## Version and source boundary

The lab pins `@earendil-works/pi-durable`, `@earendil-works/pi-ai`, `@earendil-works/chord`, and `@earendil-works/pi-codemode` to **1.3.0**, released 2026-10-15, and uses Node **24.18.0**. The official `v1.3.0` tag resolves to `71023aec1546d6d677a65669c5665c0927ce0dd0`. The reviewed development head was `d2e7d8b7c1d31d3661f769d5caef7ba8d50c3e03`; `main` is a moving reference.

Use the installed release's `dist/*.d.ts`, bundled README, and implementation for executable signatures. The package explicitly labels its API experimental. The pinned specification contains some stale illustrative declarations: its input `SubmissionDraft` says `entry?: never`, while the 1.3.0 implementation and declarations support custom input entries; its `HarnessSettings` excerpt omits `progress`, which the release supports. These inconsistencies are documentation drift, not evidence that those release APIs are unavailable.

Primary sources: [release source tree](https://github.com/earendil-works/pi/tree/v1.3.0/packages/durable), [release README](https://github.com/earendil-works/pi/blob/v1.3.0/packages/durable/README.md), [release specification](https://github.com/earendil-works/pi/blob/v1.3.0/packages/durable/docs/spec.md), [release public harness types](https://github.com/earendil-works/pi/blob/v1.3.0/packages/durable/src/harness/types.ts), [release core types](https://github.com/earendil-works/pi/blob/v1.3.0/packages/durable/src/types.ts), and [release changelog](https://github.com/earendil-works/pi/blob/v1.3.0/packages/durable/CHANGELOG.md).

### Features documented on main that are absent from 1.3.0

| Development API | Release 1.3.0 situation | Operational consequence |
|---|---|---|
| `runtime.sleepUntil(until, checkpoint, context)` and persisted `sleeping` task state | Has `runtime.sleep(until, context)`, which waits inside a live invocation | Persist a deadline and a phase before an in-phase sleep; a restart reruns that phase. Do not copy main's sleep-state code into this release. |
| `setTimer`, `onWake`, `harness.wake()` | Absent | The main Durable Object alarm/hibernation example is not a release recipe. An evictable host needs an independently designed wake mechanism or a suitably pinned later implementation. |
| `restartLimit`, `harness.retryTask()` and `restart_limit` blocking | Absent | 1.3.0 does not provide main's crash-loop parking controls. A supervisor must bound repeated restarts if the application requires this. |
| `settings.afterFailedRun` | Absent | Queued follow-ups remain queued after a failed run until another boundary processes them or the host withdraws them. |
| `compaction.modelOverrides` | Absent | Use release settings getters or separate harness policies when models have very different context windows. |
| Supplier functions for `HarnessOptions.models` and `.settings` | Accepts objects in 1.3.0; settings object property getters remain supported | Do not pass main's supplier-function form. |
| `HarnessOptions.telemetry`, `DURABLE_TELEMETRY_SCHEMA`, stored trace carriers, `TaskOptions.trace` | Absent | Use release `onReport`, usage, views, and host instrumentation. Do not present main's tracing schema as tested release functionality. |
| `onReport(error, info)` with report categories and task/extension attribution | Release callback is `onReport(error)` | A two-argument callback cannot rely on `info` on 1.3.0. |

Confirmed by searching the installed declaration files and comparing the bundled README with [the development README at the reviewed commit](https://github.com/earendil-works/pi/blob/d2e7d8b7c1d31d3661f769d5caef7ba8d50c3e03/packages/durable/README.md), [development harness types](https://github.com/earendil-works/pi/blob/d2e7d8b7c1d31d3661f769d5caef7ba8d50c3e03/packages/durable/src/harness/types.ts), and [development core types](https://github.com/earendil-works/pi/blob/d2e7d8b7c1d31d3661f769d5caef7ba8d50c3e03/packages/durable/src/types.ts).

## Which Pi component to use

| Need | Component | Reason |
|---|---|---|
| Work interactively in a repository, use installed skills/extensions/themes, automate existing CLI/RPC behavior | `@earendil-works/pi-coding-agent` | A finished coding product with interactive, print/JSON, RPC, and SDK surfaces. |
| Build an application's durable agent lifecycle, typed application state, recovery, owned tasks, and UI projection | `@earendil-works/pi-durable` | A TypeScript runtime embedded by a host that provides models, storage, registry, and environments. |
| Call model providers without durable conversations or orchestration | `@earendil-works/pi-ai` | Provider/model access underneath both product and runtime. |
| Compose many tools programmatically while controlling what reaches the model | Durable's `createCodemodeExtension({ sandbox })` plus `@earendil-works/pi-codemode` | QuickJS scripts use nested durable tool calls and deterministic journal replay. |

Do not assume a coding-agent extension, skill, permission system, or CLI flag is automatically a Durable extension or setting. The host explicitly installs Durable tools and extensions. The CLI product's official entry points are documented in [its README](https://github.com/earendil-works/pi/blob/v1.3.0/packages/coding-agent/README.md) and [pi.dev](https://pi.dev/).

## Release feature inventory and when to use it

The following inventory was checked against the installed 1.3.0 README, declarations, and implementation. Tests should select representative cases from every family and report unexecuted integrations explicitly.

### Conversation lifecycle and model context

| Feature and public API | Best use | Behavior to verify |
|---|---|---|
| `Harness.open(storage, { models, registry }, context)`, `root(context, options)` | Start one application's durable session | Root is created once, reopens with the same ID, and first-creation options do not overwrite an existing root. |
| `Conversation.submit({ type: "input", content, requestId? }, context)`; `Submission.status()` / `.wait()` | Admit a user request and reconnect to its outcome | Wait settles `done` with an answer entry or `unanswered` with a reason; cancellation of the wait does not abort admitted work. |
| `requestId`; `harness.submission(id)` | Client retry after disconnect or process restart | The same key in the same conversation returns the original submission; host retries must preserve the intended key. |
| `whenBusy: "followUp"`, `"steer"`, `"reject"`; queue modes | Queue new work, redirect active work, or enforce idle-only actions | Follow-up waits for the answer, steer joins after a tool round, reject throws `ConversationBusy`; queued submission abort withdraws it. |
| `submit({ type: "write", entry }, context)` | Add app/UI facts or place model-context changes at a safe boundary | A display-only `kind`/`data` entry is immediate, except behind a queued reset; model/head/edit writes use boundaries. |
| Custom input `entry: { kind, data }` | Show a domain-specific message while retaining user-input semantics | Application kind is preserved; `content` still contributes a user message; avoid reserved `pi.` kinds. |
| `Conversation.context(context, { at? })`; `.entries(query, limit, cursor, context)` | Read exact model context versus stored history | Context applies heads/edits and model filtering; entries remain immutable history. Pagination supports ascending and descending scans. |
| `configure(change, context)`; `agent(context)` | Give each reviewer/worker its own model, tools, instructions, and cwd | `null` clears to defaults, omitted fields are unchanged; names persist, code resolves from the registry. |
| `reset(handoff, context)`; tool `control.handoff` | Start a new task context or deliberately pass a compact handoff | Old entries remain stored; busy reset ends current work at its placement boundary. |
| `compact(instructions, context)`; `CompactionTask`; auto/background/overflow compaction | Long conversations retaining recent details | Old history remains; observe the task outcome and summary submission placement; stale summaries do not replace newer cuts. |
| `createConversation({ ownership, agent?, init? }, context)`; `fork(entryId, options, context)` | Independent specialist work or alternate solutions from a historical point | Fork sees inclusive parent history through that entry, agent choices as of that entry, and independent document copies. |
| Persisted `ProviderDoc` session identity | Preserve provider cache/session affinity across reopen | Root identity persists across retry/reset/compaction/model changes; a child or fork receives a fresh identity. |

Implementation references: [harness](https://github.com/earendil-works/pi/blob/v1.3.0/packages/durable/src/harness/harness.ts), [inbox](https://github.com/earendil-works/pi/blob/v1.3.0/packages/durable/src/harness/inbox.ts), [submission handling](https://github.com/earendil-works/pi/blob/v1.3.0/packages/durable/src/harness/submissions.ts), [context reduction](https://github.com/earendil-works/pi/blob/v1.3.0/packages/durable/src/harness/context.ts), [agent resolution](https://github.com/earendil-works/pi/blob/v1.3.0/packages/durable/src/harness/agent.ts), [compaction](https://github.com/earendil-works/pi/blob/v1.3.0/packages/durable/src/harness/compaction.ts), [provider identity](https://github.com/earendil-works/pi/blob/v1.3.0/packages/durable/src/harness/provider.ts).

### Extensions, tools, and code mode

| Feature and public API | Best use | Behavior to verify |
|---|---|---|
| `defineExtension`, `createRegistry`, `install`, `uninstall` | Bundle tool/prompt/policy/task behavior | Same-name install replaces code; reinstall after restart; running work finishes with the implementation it captured. |
| `section`, `wrapSection`, `wrapTool` | Build stable prompts and decorate selected behavior | Later same-name tools win; wrappers decorate the winning tool; instructions render last. |
| `hook(GenerationTask, ...)`, `hook(ToolTask, ...)`, `hook(CompactionTask, ...)` | Request transforms, continuation, argument guards, redaction, custom summaries | Verify hook order, blocking, rewritten arguments/results, and exception handling; hooks apply only when the extension is selected. |
| `defineTool({ parameters, execute, replay? })` | Add schema-validated application operations | Invalid arguments do not execute; thrown errors become tool results; default unsafe replay interrupts rather than blindly rerunning. |
| Tool `api.output`, `api.details`, output limits, diagnostics, usage | Show bounded progress, separate UI metadata, and count tool spend | Progress is committed; retained tail/head obeys limits; final result and error channels remain usable. |
| `structuredOutputSchema`, `structuredOutput`, `output`, `details` | Give programs typed results and models concise text | Invalid structured output is diagnosed; transcript keeps model output/details, while nested callers receive structured results. |
| `api.executeTool(name, args, context, { key?, progress? })` | Compose tools, MCP bridges, scripts | Nested tasks receive validation/hooks/replay policy; explicit stable keys reattach across replay; nested spend is already counted. |
| Tool `callers`, agent `tools` and `modelTools` | Limit enabled tools separately from model exposure | A hidden model tool may remain callable from another tool; disabled tools are unavailable to both paths. |
| Tool `deferred: true`, `createToolSearchExtension`, `control.addTools` | Large MCP/tool catalogs | Search loads matching deferred tools, loaded names persist on that conversation branch and survive compaction. |
| `createCodingTools`, `CodingTools`; `createReadTool`, `createWriteTool`, `createEditTool`, `createBashTool` | Coding/file work through an execution environment | Nothing installs automatically; read/write/edit require an env; edits/writes to one file serialize by env identity/path. |
| `createPowerShellTool()` | Windows commands using PowerShell semantics | Install separately: `CodingTools` includes `bash`, not `powershell`; verify UTF-8 output and nonzero exit structured result. |
| `createNodePhotonImages`, `createPhotonImages`, Cloudflare image loader | Image reads beyond native model size/format limits | Optional processor rotates/resizes/converts; no processor accepts supported in-limit images only; non-vision model receives placeholder diagnostics. |
| `createCodemodeExtension({ sandbox })`, `CodemodeSandbox` | Batch/filter/loop across tools without sending intermediate data to the model | `tools.*`, discovery helpers, result journal, store/load, output bounds, thrown errors, and nonzero `bash` exit handling. |
| Code-mode `store(key,value)` / `load(key)` | Persist small script JSON values per conversation | Values survive reopen and fork as of the fork entry; journal replay reproduces the same call sequence. |
| Code-mode `models.*`, `models: false`, namespaces, remote sandbox | Provider classification/image workflows or remote hosting | Catalog/discovery can be exercised offline; actual classification/image generation and remote sandbox require integration tests. |

Implementation references: [extension helpers](https://github.com/earendil-works/pi/blob/v1.3.0/packages/durable/src/harness/define.ts), [tool task](https://github.com/earendil-works/pi/blob/v1.3.0/packages/durable/src/harness/tool.ts), [coding tools](https://github.com/earendil-works/pi/blob/v1.3.0/packages/durable/src/tools/index.ts), [shell tools](https://github.com/earendil-works/pi/blob/v1.3.0/packages/durable/src/tools/bash.ts), [tool search](https://github.com/earendil-works/pi/blob/v1.3.0/packages/durable/src/tool-search/tool-search.ts), [code mode](https://github.com/earendil-works/pi/blob/v1.3.0/packages/durable/src/codemode/codemode.ts), [code-mode model tools](https://github.com/earendil-works/pi/blob/v1.3.0/packages/durable/src/codemode/models.ts), [Node images](https://github.com/earendil-works/pi/blob/v1.3.0/packages/durable/src/images/node.ts).

### Durable tasks, documents, observation, and operations

| Feature and public API | Best use | Behavior to verify |
|---|---|---|
| `defineTask`, `tx.createTask`, `runtime.commit` | Application workflow with explicit durable checkpoints | Commit intent, perform effect outside commit, commit outcome; restart reruns from checkpoint rather than from a saved JavaScript stack. |
| `runtime.memo(name, candidate, context)` | Save small first-writer-wins identities/results | The durable winner survives checkpoints; use documents for growing progress and entries for large retained results. |
| Task `version`, `migrate`; registry changes | Upgrade live workflow implementations | Missing/newer/unmigratable definitions remain blocked and visible in `inspect()` until usable code arrives. |
| `waiting` state, `on`, `policy: "allSettled"` or `"failFast"`; `runtime.outcomes` | Fan out work and durably join | All-settled waits for every task; fail-fast aborts remaining owned siblings; invalid cycles are rejected. |
| Task/conversation ownership; foreground subagent conversation | Delegated work whose parent must wait and cancel together | Parent remains completing until ordinary descendants drain; abort handlers execute after owned work is settled. |
| Conversation-owned `background: true`; background subagent anchors | Independent persistent workers | Ordinary idle/abort excludes their subtree; explicit background-inclusive abort reaches it. |
| `abandonOnRestart` | Children whose only waiter cannot resume | Restart aborts them before rerunning effects; unsafe tools automatically abandon owned nested work. |
| `abortTask`, `Conversation.abort`, `waitForIdle`, `waitForTask`; `close` | Distinguish cancel, join, and host shutdown | Abort writes durable intent; close interrupts invocations and leaves pending work resumable. |
| `defineDoc`, `defineDocFamily`, `tx.doc`, `retireDoc` | Typed app state stored atomically with transcript/tasks | Session/conversation/task scopes, lazy creation, stable family key and first seed, task retirement, rollback. |
| Doc history `latest` / `rewindable`; fork `initial` / `current` / `asOf`; `snapshotAsOf` | Choose deliberate branch state semantics | `asOf` requires rewindable history; same-commit entries see final document state of that commit. |
| Document `version`, `migrate`, `checkpointWhen` | Upgrade schema and bound replay cost | Read migration remains in memory; first typed transaction persists the migrated base; kinds cannot be renamed by value migration. |
| `snapshot`, `documentState`, `watchDoc`, `conversationCreated`, creation `init` | Read/observe state and initialize every child consistently | Snapshot/watch of missing docs does not create them; creation callback and init share the creation transaction. |
| `viewState`, `watch`, `watchEvents` | UI state, remote patches, or coding-agent style events | Initialize snapshot before starting delivery; slow consumers eventually get replacement snapshots; events are experimental. |
| `taskGraph`, `watchTaskGraph`, `inspect` | Monitor live ownership and diagnose blocked work | Graph contains live tasks; inspection supplies derived blocked reasons; terminal receipts remain queryable by task ID. |
| `usage`, `UsageDoc`; task/response `durationMs` and lifecycle timestamps | Cost panels and operational diagnostics | Model, tool, failed, and aborted attempts count; lifecycle span differs from execution duration. |
| `env` factory, `NodeExecutionEnv`, custom `ExecutionEnv` | Per-conversation filesystem/container/process execution | Use current cwd/committed state; argv `exec` avoids shell parsing; cwd alone is not a sandbox. |
| `registerStorageConformance`, `registerEnvConformance` | Validate custom adapters | Run complete conformance on an actual backend/environment; a stub import proves only the export exists. |

Implementation references: [core types and task contracts](https://github.com/earendil-works/pi/blob/v1.3.0/packages/durable/src/types.ts), [document definitions](https://github.com/earendil-works/pi/blob/v1.3.0/packages/durable/src/documents.ts), [session](https://github.com/earendil-works/pi/blob/v1.3.0/packages/durable/src/session/session.ts), [task scheduler](https://github.com/earendil-works/pi/blob/v1.3.0/packages/durable/src/harness/scheduler.ts), [events](https://github.com/earendil-works/pi/blob/v1.3.0/packages/durable/src/harness/events.ts), [views](https://github.com/earendil-works/pi/blob/v1.3.0/packages/durable/src/harness/view.ts), [task graph](https://github.com/earendil-works/pi/blob/v1.3.0/packages/durable/src/harness/task-graph.ts), [usage](https://github.com/earendil-works/pi/blob/v1.3.0/packages/durable/src/harness/usage.ts), [environment contract](https://github.com/earendil-works/pi/blob/v1.3.0/packages/durable/src/env/index.ts), [Node environment](https://github.com/earendil-works/pi/blob/v1.3.0/packages/durable/src/env/node.ts), [testing exports](https://github.com/earendil-works/pi/blob/v1.3.0/packages/durable/src/testing/index.ts).

## Storage choice

| Backend | Recommended moment | Limits and required validation |
|---|---|---|
| `MemoryStorage` | Fast isolated tests, disposable runs | No persistence across process loss. Closing/reopening the same object is not evidence of disk crash durability. |
| `openNodeSqliteStorage(path, { prefix? })` | Default for long-lived Node agents | Built-in Node SQLite, WAL, synchronous NORMAL. Process-crash recovery differs from power/host-loss guarantees. One owner process per storage. |
| `openNodeJsonlStorage(directory, context, { fsync: true })` | Inspectable small logs and debugging | Append-only log plus whole history in memory. Fsync flushes before commit markers; it is not an automatic corruption-repair or log-compaction service. |
| `openDurableObjectSqliteStorage(ctx.storage, { prefix? })` | Cloudflare SQLite Durable Object deployments | Needs real Workers integration, object lifecycle/alarm design, and compatible execution/codemode environments. Local Node tests cannot certify it. |
| Portable `SqliteStorage` / `JsonlStorage` and custom adapters | Another database/runtime/file capability | Implement the complete contract and run conformance; portable cores do not imply an included adapter for every database. |

`prefix` namespaces tables/indexes and does not migrate existing data. Multiple Cloudflare adapters for the same storage coordinate through a shared queue in 1.3.0. Host SQL must use the same database facade/queue; direct host SQL can otherwise cross an adapter transaction. Neither SQLite nor JSONL makes one Pi storage a cross-process or multi-writer database.

References: [SQLite storage](https://github.com/earendil-works/pi/blob/v1.3.0/packages/durable/src/storage/sqlite/storage.ts), [Node SQLite adapter](https://github.com/earendil-works/pi/blob/v1.3.0/packages/durable/src/storage/sqlite/node.ts), [Cloudflare adapter](https://github.com/earendil-works/pi/blob/v1.3.0/packages/durable/src/storage/sqlite/cloudflare.ts), [JSONL implementation](https://github.com/earendil-works/pi/blob/v1.3.0/packages/durable/src/storage/jsonl/storage.ts), [JSONL Node helper](https://github.com/earendil-works/pi/blob/v1.3.0/packages/durable/src/storage/jsonl/node.ts).

## Operational rules that make recovery correct

1. Pin every Pi package and lock dependencies; review release source before adopting code from main.
2. Persist identity before effect: store task phase and idempotency key, perform the external operation outside a transaction, then store its receipt. A crash after the effect but before receipt is ambiguous; `replay: "safe"` does not grant exactly-once effects.
3. Use stable nested call keys if branch/concurrency order can vary. A replay-safe parent reuses completed nested calls; a still-running child follows its own replay policy. Never report a nested call's usage again in its parent result.
4. Reinstall the same required extension definitions before scheduling recovered work. Persisted names do not persist executable code. Retain old resources until their captured running calls finish.
5. Keep commit callbacks short and use only the current `tx` inside them. Read required table rows before the first table write. Awaiting network, a model, a process, another commit, or a session read that needs the mutation line can deadlock or stall every commit.
6. Use write submissions to change a busy transcript. Raw entry writes racing request preparation can put system entries in the wrong place.
7. Treat `Context` cancellation as cancellation of one call/wait unless using an API that commits abort intent. Use `abort` for durable cancellation and `close` for resumable host shutdown. Cooperative handlers must honor their signal or shutdown can hang.
8. Keep permission guards in every selected extension array that needs them. `modelTools` hides model access but does not revoke nested access; use enabled `tools`/`callers` and environment enforcement for actual policy.
9. Use stable prompt sections to preserve provider caching. Agent configuration changes take effect at request/phase boundaries, while a rebuilt environment can use the conversation's current cwd on recovery.
10. Keep large results in durable entries or documents and store references in task outcomes. Task-scoped documents retire when their task becomes terminal; snapshot/watch revisions are immutable and may share internal containers.
11. Treat watches as convergence streams. A slow subscriber can miss intermediate commits after the 100-frame buffer collapses; store audit facts as entries and query history if every transition matters.
12. Place model edits/heads before starting compaction. A summary computed concurrently can describe older material and cut past a later edit. Summaries cost a model call even when their result becomes stale.
13. On a storage failure, let the failed harness close, reopen storage, and retry admission using the same request ID. Invalid read requests fail one call; actual storage exceptions fail the session. Transient retries belong inside a custom storage adapter.
14. Do not treat all background work as cancelled or finished when ordinary idle resolves. Scope abort/idle deliberately and expose background tasks in the host UI.
15. On Windows, prefer the separately installed PowerShell tool when PowerShell syntax is intended; its presence in the package does not replace CodingTools' bash automatically.

## Coverage gaps to preserve in the final report

An offline deterministic provider can exercise harness state transitions, request shape, tools, retries, compaction scheduling, usage accumulation, and observation. It cannot establish live model quality, provider prompt-cache hits, OAuth/API-key authentication, network retries against a real service, deferred-provider behavior, image-generation/classification quality, price correctness, or context-overflow responses from each provider.

A proper crash test kills a separate process after a known persisted checkpoint and opens the same durable backend in a new process. A cooperative `close()` plus reopen is useful but distinct. Run both unsafe and safe interruption cases, and show an actual external side effect count when claiming replay avoids duplicates.

Cloudflare Durable Object transactions/lifecycle, remote execution and remote QuickJS, fsync under power failure, filesystem watcher reliability across OS/filesystems, hostile scripts, and high-load/memory endurance require dedicated integrations or fault testing. Label them documented, imported, locally smoke-tested, or untested as applicable; never collapse these into “all functionality passed.”

For a small initial application, prefer: Node SQLite; one owner process; one explicitly selected extension bundle; direct tools; stable request IDs; structured outputs for composition; guarded replay-safe tools only when their external effects are idempotent; `viewState` for a local UI; manual/background compaction only after selecting thresholds appropriate to the model; explicit foreground ownership first, then background workers when independent lifetime is required.
