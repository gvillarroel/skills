# Pi Durable usage and feature selection

To get `/durable`, `/durable new` and `/durable-chat` in Pi Coding Agent, follow
the [console extension installation guide](pi-durable-console.md). The console
is an optional extension; installing the skill collection alone does not load it.

Use **Pi Durable with Node SQLite, one owning process, stable request IDs, explicit tools, and foreground ownership** as the starting configuration for an application that must recover agent work after a process restart. Use Pi Coding Agent for an interactive terminal coding session. Add Code Mode when several tool calls benefit from programmatic composition; add background ownership only when the work should survive cancellation of its parent.

This guide covers the published **1.3.0** release, tested on **Windows with Node 24.18.0 on 2026-10-19**. The API is experimental. The official release is pinned to commit `71023aec1546d6d677a65669c5665c0927ce0dd0`. Development documentation was also reviewed at `d2e7d8b7c1d31d3661f769d5caef7ba8d50c3e03`; several APIs there are absent from 1.3.0.

The [source review and full feature inventory](../projects/pi-durable-lab/source-review.md) records the release/development differences and exact source links. The [validation report](../projects/pi-durable-lab/validation.md) records execution, retained failed experiments, and integration limits. The [conversation](../projects/pi-durable-lab/conversation-results.md) and [tools](../projects/pi-durable-lab/tools-results.md) notes provide feature-level evidence.

For a reusable agent workflow and service starter, use the [Pi Durable skill](../skills/pi-durable/SKILL.md). Its [service validation record](../evaluations/pi-durable/validation-20261019.md) distinguishes template checks, isolated authoring outcomes, and unverified native deployments.

Generated applications include their own operations guide, prompts, source, local helper and portable provenance; they operate without the generating skill. The [requested evolution workflow](../skills/pi-durable/references/agent-evolution.md) adds public evidence, versioned decisions, inactive model-assisted proposals, paired evaluation and source rollback. The [evolution validation record](../evaluations/pi-durable/evolution-20261024.md) separates tested mechanics from unverified model-quality improvements.

## Working model

A **Harness** owns one open storage and its task scheduler. A **conversation** is a transcript plus typed documents. An **input submission** starts or joins a run; a **write submission** records something without asking the model. A **task** is a durable state machine. Model requests, tools, compaction, and application workflows all use tasks.

Durable state is committed before observers see it. Recovery resumes the stored task checkpoint. It does not restore an arbitrary JavaScript stack, undo filesystem writes, or make a remote API operation exactly once. A task phase may execute again after interruption; external effects need their own stable operation IDs or idempotent behavior.

- [Runtime and recovery diagram source](../projects/pi-durable-lab/diagrams/runtime-flow.mmd)
- [Feature decision diagram source](../projects/pi-durable-lab/diagrams/decision-guide.mmd)

The [reproduction commands](../projects/pi-durable-lab/diagrams/validation.md) generate local SVGs under `projects/pi-durable-lab/artifacts/svgs/`; generated output remains outside Git.

The official [release core types](https://github.com/earendil-works/pi/blob/v1.3.0/packages/durable/src/types.ts) define the checkpoint and commit contracts. The [Harness implementation](https://github.com/earendil-works/pi/blob/v1.3.0/packages/durable/src/harness/harness.ts) owns admission and scheduling.

## Pick the feature that matches the job

| Situation | Prefer | Reason and practical boundary |
|---|---|---|
| One person working interactively in a terminal | Pi Coding Agent | Durable is an application harness; it does not automatically supply the terminal product, resource discovery, authentication UI, or client policy. |
| Restart recovery or several clients steering one agent | Pi Durable | Persist input admission, transcript, progress, and task checkpoints under one host. |
| Local persistent service | Node SQLite | Database storage avoids retaining the full JSONL history in memory. Give one process ownership. |
| Disposable unit or workflow tests | `MemoryStorage` with the official faux provider | Fast, deterministic, no remote credentials; no persistence beyond the storage object's lifetime. |
| Human-inspectable append-only local history | JSONL, normally `{ fsync: true }` when flush durability is required | Easy to inspect; retains the entire history in memory. It is a different durability/performance tradeoff from SQLite. |
| A few tools with simple inputs | Direct `defineTool()` calls | Less machinery and easy diagnosis. Use TypeBox validation and hooks at the tool boundary. |
| Loops, filtering, aggregation, or composition of many calls | Code Mode | Run JavaScript in QuickJS, call `tools.*`, and return selected results to the model. Nested calls still receive validation, hooks, ownership, and replay policy. |
| A large tool or MCP catalog | Deferred tools plus `tool_search` | Search loads a relevant subset instead of offering the entire catalog at each request. |
| Programmatic consumers need reliable fields | `structuredOutputSchema` and `structuredOutput` | Separate typed program results from concise model output and UI `details`. |
| A correction to current work | `whenBusy: "steer"` | Place at the next tool-round boundary. It does not interrupt the provider halfway through a request. |
| A new job after the current answer | Default follow-up | Queue it for the next run. |
| Admission must require an idle conversation | `whenBusy: "reject"` | Reject with `ConversationBusy` and admit nothing. |
| UI/chat audit data that should not trigger generation | `type: "write"` | A write with just kind/data is visible immediately, including mid-run, except behind a queued reset. |
| Try another direction from an earlier entry | `fork(entryId, ...)` | Preserve the parent and branch at a concrete historical cutoff. A fork gets a new provider session identity. |
| Fresh model context in the same stored history | `reset()`; supply a handoff summary when useful | Old entries remain stored. A reset by itself does not start a model request. |
| Keep a long conversation within the model window | Compaction | Keep recent entries and replace an older active range with a summary. Custom hooks can summarize or decline. |
| A delegated task whose parent should wait/cancel with it | Task-owned foreground conversation | Ownership gives cascading cancellation and correct idle/completing semantics. |
| Work that should survive the parent's normal abort | Background anchor task owning a child conversation | Parent idle and ordinary abort exclude that subtree. Use background-inclusive abort for an explicit full stop. |
| A multi-step workflow, durable join, or migration | `defineTask()` and checkpoints | Persist decisions and phase transitions; do effects outside the commit. |
| All branches should finish | `waiting` with `allSettled` | Collect every outcome explicitly. |
| An early branch failure invalidates its remaining siblings | `waiting` with `failFast` | Abort unfinished owned siblings before collecting their outcomes. |
| Application state must change atomically with transcript/tasks | `defineDoc()` / `defineDocFamily()` | Choose scope, history, fork policy, and schema migration deliberately. |
| A UI needs current state | `viewState()` | Subscribe to committed structural state and dispose it before closing the Harness. |
| A remote client needs patches | `watch()` | Start with the current snapshot, then apply serialized patches; reconnect from a fresh snapshot. |
| Familiar turn/tool events | `watchEvents()` | Useful adapter, still experimental. Treat structural committed state as the authority. |
| Operations need to inspect work | `inspect()`, task graph, usage | Inspect blocked tasks, ownership, queues, outcomes, and model/tool spend. The 1.3.0 graph itself omits blocking reasons; use `inspect()`. |

The [public Harness types](https://github.com/earendil-works/pi/blob/v1.3.0/packages/durable/src/harness/types.ts), [code-mode implementation](https://github.com/earendil-works/pi/blob/v1.3.0/packages/durable/src/codemode/codemode.ts), and [tool-search implementation](https://github.com/earendil-works/pi/blob/v1.3.0/packages/durable/src/tool-search/tool-search.ts) define the corresponding release behavior. The table's preferred defaults are judgments based on those contracts and the local probes.

## Run the small reproducible lab

From the repository root:

```powershell
Set-Location projects/pi-durable-lab
$env:npm_config_cache = Join-Path (Get-Location) 'artifacts/npm-cache'
npm ci --ignore-scripts --no-audit --no-fund
npm test
npm run demo -- starter-1
npm run demo -- starter-1
```

The [demo](../projects/pi-durable-lab/scripts/demo.ts) uses the official offline faux provider and a read-only counting tool. On a fresh database, the first invocation makes two provider calls: a tool request and an answer. The second invocation finds the same persisted submission and makes **zero** provider calls. To submit a different logical input, give it a different request ID. The SQLite file lives under `projects/pi-durable-lab/artifacts/demo/` and is not tracked in Git.

The demo intentionally uses a stable provider/model identity across process starts. A real host supplies configured `Models` providers and credentials instead of the faux provider; test authentication, provider-specific errors, image support, caching, and billing with that provider before treating that integration as verified.

## Use the host lifecycle correctly

1. Register trusted extensions, task definitions, and providers on every process start. The registry's executable code is not stored in the database.
2. Open one storage and one Harness. Reacquire the existing root conversation; `root()` creation options apply only when creating it. Use `configure()` for later changes.
3. Call `resume()` to recover pending work even when no new client input arrives. Calls that request progress, including `submit()` and waits, also start scheduling. Read-only viewers do not.
4. Admit each logical input with a stable `requestId`. A network retry reuses the ID; a new input gets a new ID. IDs deduplicate within one conversation. Keep input content consistent for a reused ID.
5. Store task inputs, checkpoints, and typed documents as JSON. Use memos for small first-writer-wins values and durable identities. Avoid large retained data in memos.
6. Observe the current snapshot before starting a watch. Do not replay old transport deltas after reconnect.
7. Dispose states and stop watches, then `close()`. Cooperative tools and task phases must honor cancellation. Close waits for code that ignores its signal.
8. A fatal storage error ends the Harness; reopen from storage. An invalid request affects that call. A tool exception becomes a tool error result. A phase that makes no durable progress faults its task.

Inside a `commit()` callback, use only the provided `tx` for reads and writes. Calling Harness snapshot/state/watch methods there can queue a read behind the transaction that is waiting for that read. Execute model requests, shell commands, and other external effects outside the callback; atomically commit their intent or outcome instead.

These boundaries come from the [transaction and task interfaces](https://github.com/earendil-works/pi/blob/v1.3.0/packages/durable/src/types.ts), [scheduler](https://github.com/earendil-works/pi/blob/v1.3.0/packages/durable/src/harness/scheduler.ts), and [Session implementation](https://github.com/earendil-works/pi/blob/v1.3.0/packages/durable/src/session/session.ts).

## Cancellation and recovery are different operations

| Operation | What it does |
|---|---|
| Cancel a Chord context used by a wait | Cancel that observer's wait. The admitted work continues. |
| `submission.abort()` while queued | Withdraw that queued submission. A placed input is already part of a run. |
| `conversation.abort()` | Withdraw queued inputs, cancel ordinary owned work, and wait for the ordinary scope to become idle. Queued writes remain. |
| `conversation.abort(context, { background: true })` | Also mark the background work reached when the abort is admitted. |
| `abortTask()` | Persist an abort mark and run bottom-up cleanup; it does not mean a JavaScript function has instantly stopped. |
| `close()` | Stop this host's active invocations and close storage; unfinished work remains recoverable. |
| Abrupt process death | Reopen the store and resume from the last committed checkpoint; replay policy decides what an interrupted tool may do. |

The process-kill probes demonstrated three concrete outcomes: the completed first phase of a task was not run again; an interrupted tool marked `replay: "safe"` ran again; and a default unsafe tool returned an `interrupted` result without repeating its test effect. The safe tool deliberately appended the same external effect twice, exposing why the flag is a promise made by the tool author rather than an idempotency service.

## Tool and environment choices

Install only the extensions/tools the conversation should use. `tools` controls availability at all; `modelTools` controls model exposure. A tool hidden from the model can remain callable by another tool. `callers` can further restrict calls from models or tools. These controls do not sandbox the tool implementation.

Use `output` for the model, `structuredOutput` for programs, and `details` for UI metadata. Redaction hooks must redact both model and structured channels. Correlate parallel tool results by `toolCallId`: their transcript completion order need not match the request order. Sequential execution is appropriate when later effects depend on earlier ones; parallel execution is appropriate for independent operations. The local concurrency probe observed peak execution counts of one and two respectively.

`NodeExecutionEnv` uses the host filesystem and processes. A `cwd` is a working directory, not a filesystem permission boundary. For an untrusted workload, supply an environment whose file/process APIs enforce the intended restrictions. The local coding probes performed all writes under the lab artifacts directory; remote sandbox confinement was not tested.

On Windows, `CodingTools` installs `bash`, alongside read/write/edit. Install `createPowerShellTool()` separately when PowerShell command semantics are required. Both shell paths were executed locally, including a nonzero exit. Available shells and their behavior are host prerequisites.

The direct `@earendil-works/pi-durable/images/node` import failed in this release/environment before processor construction because of the Photon export interop. Ordinary supported images within limits worked without a processor. The lab also verified a portable bundling route that loads WASM bytes; its exact command and error evidence are in [the tools results](../projects/pi-durable-lab/tools-results.md). Treat that as a tested workaround with an extra build step, and recheck the upstream import when upgrading.

Relevant sources: [tool execution](https://github.com/earendil-works/pi/blob/v1.3.0/packages/durable/src/harness/tool.ts), [Node environment](https://github.com/earendil-works/pi/blob/v1.3.0/packages/durable/src/env/node.ts), [shell tools](https://github.com/earendil-works/pi/blob/v1.3.0/packages/durable/src/tools/bash.ts), and [image processor](https://github.com/earendil-works/pi/blob/v1.3.0/packages/durable/src/images/index.ts).

## State, branching, compaction, and upgrades

Choose `scope: "session"` for shared state, `"conversation"` for branch state, and `"task"` for temporary workflow state. Task-scoped documents retire with the task. Use `history: "latest"` when only the current value matters; use `"rewindable"` for historical reads. Fork `"initial"` resets state, `"current"` copies the current value, and `"asOf"` reconstructs the value at the branch entry and requires rewindable history. Entries and document edits made in the same commit share that commit's state.

Version task and document definitions when schemas change. Task migration supplies a compatible input/checkpoint before resuming. A missing task definition blocks work until the registry has it. Document read migration can happen without persisting a new base; a later typed document transaction persists the migrated value. Keep migration code available while old live records can exist.

Compaction preserves older stored entries while reducing active model context. Test manual, threshold, overflow, and failed-summary behavior separately. A hook-provided summary is useful when an application can summarize deterministically; provider-generated summaries require quality checks on the selected model. Use `fork()` for a branch and `reset(handoff)` for a fresh active context. In the tested release, a tool's `control.handoff` settles its original input `done` with the tool-call assistant entry, whereas a host reset during tool execution settles the active input `unanswered` with reason `reset`. A client must interpret the settlement and entry kind rather than assuming every `done` points to final answer text.

Sources: [document definitions](https://github.com/earendil-works/pi/blob/v1.3.0/packages/durable/src/documents.ts), [task definitions](https://github.com/earendil-works/pi/blob/v1.3.0/packages/durable/src/tasks.ts), [compaction](https://github.com/earendil-works/pi/blob/v1.3.0/packages/durable/src/harness/compaction.ts), and [generation settlement](https://github.com/earendil-works/pi/blob/v1.3.0/packages/durable/src/harness/generation.ts).

## Storage comparison and version limits

The lab runs the package's 24 storage conformance cases against Memory, SQLite, and JSONL, plus application-level persistence and recovery probes. Its small timing comparison measures 30 sequential passive writes per backend. It excludes model requests, network traffic, production load, long histories, and host/power failure. Use the recorded measurements in the validation report as a local smoke comparison rather than a general throughput ranking.

SQLite's Node adapter uses WAL with `synchronous=NORMAL`: process-crash recovery and power-loss durability are different guarantees. JSONL's `fsync: true` flushes affected files before commit markers but retains history in memory. A single process owns a store; do not interpret SQLite's file locks or a table prefix as permission to run multiple Harness owners concurrently. Cloudflare's SQLite-backed Durable Object adapter is a separate host integration and was reviewed, not deployed here.

| Seen in development documentation | Release 1.3.0 action |
|---|---|
| `sleepUntil`, persisted `sleeping`, `wake`, `onWake`, `setTimer` | These APIs are absent. `runtime.sleep(until, context)` exists but waits inside a live invocation. Persist the deadline/checkpoint first; an evictable host also needs its own wake strategy. |
| `restartLimit`, `retryTask`, parked crash loops | Absent. Bound repeated process restarts in the supervisor when required. |
| `afterFailedRun` | Absent. Queued follow-ups can remain waiting after a model failure; design explicit queue recovery. |
| `compaction.modelOverrides` | Absent. Use the release's available compaction configuration and hooks. |
| Harness telemetry/trace carriers and typed `onReport(error, info)` | Absent. Release `onReport` receives the error only; use the release's inspection and usage APIs. |
| Supplier functions for `models` or `settings` | Absent. Pass the objects supported by the installed release. |

Use [the pinned release README](https://github.com/earendil-works/pi/blob/v1.3.0/packages/durable/README.md) together with the installed declarations. Re-run the lab after any dependency upgrade; never copy an unversioned example into a pinned application without checking its public types.

[Back to the documentation index](README.md).
