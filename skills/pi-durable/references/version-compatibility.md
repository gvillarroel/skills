# Version and compatibility boundary

Use **1.3.0** as this skill's reference release. Pin `@earendil-works/pi-durable`, `@earendil-works/pi-ai`, `@earendil-works/chord`, and optional `@earendil-works/pi-codemode` to compatible exact versions, then retain the lockfile. The reference runtime used Node **24.18.0**; verify Node's SQLite availability on the actual supported platforms before installation.

The release is experimental. Resolve executable signatures from installed `dist/*.d.ts` and source. Do not turn an unversioned development README into a release recipe. Tag `v1.3.0` resolves to commit `71023aec1546d6d677a65669c5665c0927ce0dd0`. The previously reviewed development snapshot was `d2e7d8b7c1d31d3661f769d5caef7ba8d50c3e03`; use that immutable snapshot for comparison rather than assuming today's `main` has the same API.

For an offline compatibility/design request, this reference's pinned API table
and source links are sufficient evidence for the release verdict. Inspect installed
declarations only when they exist inside the user's authorized target project.
If that project has no installed package and installation/network are prohibited,
state that local package inspection was unavailable and use this bundled evidence.
Do not search parent directories, home directories, global npm/Pi caches, or other
evaluation runs to find a different installation. Report the observed host platform
without treating a library source search as a prerequisite for a design answer.

## Account for these differences

| Development feature at that snapshot | Release 1.3.0 | Host action |
|---|---|---|
| `sleepUntil`, persisted `sleeping` task state | Absent; `runtime.sleep(until, context)` waits inside a live invocation | Keep idle event detection in the host. Persist retry deadlines/checkpoints and provide a host wake strategy. |
| `setTimer`, `onWake`, `harness.wake()` | Absent | Use an actual host timer/event adapter or supported platform wake mechanism. |
| `restartLimit`, `retryTask`, parked crash-loop controls | Absent | Bound repeated restarts and expose failures in the supervisor/host. |
| `settings.afterFailedRun` | Absent | Reconcile queued follow-ups after model failure explicitly. |
| `compaction.modelOverrides` | Absent | Use available release compaction configuration/hooks. |
| Supplier functions for Harness `models` / `settings` | Release accepts objects | Use the release constructor form. |
| Harness telemetry options and stored trace carriers | Absent | Use host instrumentation, usage, views, and inspection. |
| `onReport(error, info)` | Release receives `error` only | Do not read unavailable attribution/category information. |

The [release README](https://github.com/earendil-works/pi/blob/v1.3.0/packages/durable/README.md), [release public types](https://github.com/earendil-works/pi/blob/v1.3.0/packages/durable/src/harness/types.ts), and [release core contracts](https://github.com/earendil-works/pi/blob/v1.3.0/packages/durable/src/types.ts) are primary references. Compare the immutable [development README](https://github.com/earendil-works/pi/blob/d2e7d8b7c1d31d3661f769d5caef7ba8d50c3e03/packages/durable/README.md) only when planning an upgrade.

## Preserve storage and environment limits

- Node SQLite uses WAL with `synchronous=NORMAL` in this release. Process-crash recovery is a different guarantee from persistence after host power loss. Give one process ownership of a Pi store; table prefixes do not supply multi-process coordination. See the [adapter implementation](https://github.com/earendil-works/pi/blob/v1.3.0/packages/durable/src/storage/sqlite/node.ts).
- JSONL with `fsync: true` flushes writes before commit markers but retains the whole history in memory. Use it deliberately for inspectability. See the [JSONL implementation](https://github.com/earendil-works/pi/blob/v1.3.0/packages/durable/src/storage/jsonl/storage.ts).
- The direct `images/node` import encountered a Photon export-interoperability failure in the reference Windows environment. Supported images within model limits can work without the optional processor. Recheck the installed image path before promising preprocessing; do not silently add a required image dependency to an event-only service. See [image loading](https://github.com/earendil-works/pi/blob/v1.3.0/packages/durable/src/images/node.ts).
- CodingTools installs `bash`; PowerShell is a separately installed tool. Validate the intended shell and absolute executable paths under the service account. See [shell tools](https://github.com/earendil-works/pi/blob/v1.3.0/packages/durable/src/tools/bash.ts).
- Pi Durable is an embedded host runtime. Pi Coding Agent's interactive/RPC features, installed skill discovery, and CLI options are separate product surfaces. See the pinned [Coding Agent README](https://github.com/earendil-works/pi/blob/v1.3.0/packages/coding-agent/README.md).

## Upgrade with durable state present

1. Back up persisted databases and record dependency versions; upgrade an isolated copy first.
2. Compare public declarations and task/document schema changes. Keep migrations for all live historical versions; missing definitions can block recovered tasks.
3. Rebuild required extensions/providers on startup and call `resume()` against the copied database.
4. Exercise replay-safe and unsafe interruption, duplicate input admission, queued follow-ups, schema migration, snapshot/watch reconnect, and console reattachment to the same IDs.
5. Recheck native lifecycle on Windows and macOS. Report a template inspection separately from a native install/start/restart test.
6. Promote the exact dependency set only after those checks pass. Preserve retained live state and migration code until old tasks can no longer resume.
