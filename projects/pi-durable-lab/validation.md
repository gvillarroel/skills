# Pi Durable 1.3.0 validation report

Validated 2026-10-19 on Windows, Node 24.18.0. The lab pins `@earendil-works/pi-durable`, `@earendil-works/pi-ai`, `@earendil-works/chord`, and `@earendil-works/pi-codemode` to 1.3.0, with tsx 4.20.6. The npm lockfile records the exact transitive graph and package integrity values. No global Pi installation, credentials, user settings, or unrelated repository changes were modified.

The final combined run produced **129 tests: 128 passed, zero assertion failures, one skipped/blocked direct integration**. The blocked integration is the direct Photon image-processor import. Its portable ESM-bundled workaround passed real decoding and a coding read. A skipped integration is not a successful test.

The Harness, scheduler, transactions, tools, SQLite/JSONL storage, shells, QuickJS, and bundled image decoder execute for real. Model responses come from Pi's official deterministic faux provider. Its token accounting is synthetic; these tests establish runtime mechanics, not autonomous model quality, remote latency, billing, or provider cache behavior.

## Reproduce

From `projects/pi-durable-lab/`:

```powershell
$env:npm_config_cache = Join-Path (Get-Location) 'artifacts/npm-cache'
npm ci --ignore-scripts --no-audit --no-fund
npm test
```

To save both complete TAP and JUnit evidence:

```powershell
New-Item -ItemType Directory -Force artifacts | Out-Null
node --import tsx --test `
  --test-reporter=tap --test-reporter-destination=artifacts/tests-final.tap `
  --test-reporter=junit --test-reporter-destination=artifacts/tests-final.junit.xml `
  scripts/conversation.test.ts scripts/tools.test.ts scripts/storage-tasks.test.ts
```

To observe request deduplication across two separate processes:

```powershell
npm run demo -- starter-1
npm run demo -- starter-1
```

On the fresh lab database the first process made two provider requests and persisted submission ID 8. The second process returned the same answer/submission with zero provider calls. IDs are generated, so a reused local database may have different values; equality and the absence of new provider work are the relevant properties. The small [demo](scripts/demo.ts) is safe to read before execution and writes only to the ignored demo artifacts directory.

## Feature evidence

| Suite | Count and result | Evidence |
|---|---|---|
| Conversation C01–C30 | 30 passed | [Script](scripts/conversation.test.ts), [feature/result matrix](conversation-results.md). Inputs, queues, steer/follow-up/reject, cancellation, forks, configuration, observers/backpressure, usage, retry/deferred, all main compaction paths, foreground/background subagents. |
| Upstream storage conformance | 72 passed: 24 cases each for Memory, Node SQLite, and JSONL with fsync | [Storage/task script](scripts/storage-tasks.test.ts). Atomic mixed commits, detached values, immutable/root ownership, IDs, scans/cursors, deep ancestry, documents, lifecycle/version bases, rollback, indexes, closed resources. These cases are supplied by the package, not 72 independently authored application scenarios. |
| Additional storage/task/document probes | 13 passed | Same script. Persistent reopen/deduplication (2), document rollback/asOf/families, task joins/memos/graph/faults, missing definitions/late install/abandonment, actual fail-fast sibling abort, task migrations/background abort, document migrations/creation/watch/fork policies, true process kills (3), fatal storage failure, small timing comparison. |
| Tools/extensions/environment/Code Mode | 13 passed; 1 direct integration blocked | [Script](scripts/tools.test.ts), [matrix, error, and workaround](tools-results.md). Schema channels, hooks/wrappers, discovery, tool routes, concurrency, files/shells/PowerShell/Unicode, argv, Windows watch, QuickJS, compatible images, bundled Photon. |

The script counts above sum to 129. The final retained TAP run completed in approximately 6.3 seconds. Test duration includes local scheduling and tool setup and is not an agent/model speed benchmark. Each exact final run's duration remains in its report.

## Abrupt process recovery

The recovery tests launch [recovery-fixture.ts](scripts/recovery-fixture.ts) as a separate Node process, wait for a marker emitted after a real durable checkpoint or tool effect, kill that process with `SIGKILL`, wait for its exit, and reopen its SQLite database in the parent process. This is an abrupt process interruption, not only a graceful `close()` simulation.

| Interrupted work | Observed result after reopen | Meaning |
|---|---|---|
| A two-phase custom task, after phase one committed phase two | Phase one external marker appears once; phase two completes from its saved checkpoint | Completed durable phases are not rerun just because a later phase was interrupted. |
| A tool explicitly marked `replay: "safe"`, after an external append but before final result | Tool executes again; two external marker lines exist | The safe flag permits replay. It does not deduplicate the external append. |
| A tool with default unsafe policy at the same point | Tool is not called again; one external marker line exists; transcript contains `interrupted` | Unsafe incomplete effects are surfaced instead of silently repeating them. |

The input request ID was reused after each tool recovery, and the completed submission was returned. Neither the model nor the application operation was submitted twice through that retry. This does not establish exactly-once behavior of an arbitrary external service.

## Local storage timing comparison

The final combined run measured 30 sequential passive kind/data writes per backend, after creating the root, with no generation or network. Values are milliseconds; rounded for readability. Each backend ran once in the same local process. Its frozen snapshot is `artifacts/storage-tasks/storage-timing-final.json`; `storage-timing.json` is overwritten by a subsequent run of the timing case.

| Backend | Open time | Median write | p95 write | Total for 30 writes |
|---|---:|---:|---:|---:|
| Memory | 0.122 | 0.056 | 0.105 | 1.864 |
| Node SQLite | 7.541 | 0.188 | 0.233 | 5.640 |
| JSONL, default flush | 0.558 | 0.557 | 0.800 | 16.952 |
| JSONL, fsync enabled | 0.662 | 0.590 | 2.975 | 25.595 |

SQLite had lower write latency than either JSONL variant in this small run, while Memory was fastest and did not persist. The two JSONL medians are too close and noisy to claim that fsync is free or faster. No warm/cold-cache control, repetitions, growing-history/memory analysis, sustained-load profile, or power-loss experiment was performed. The SQLite default recommendation also depends on its bounded history memory behavior; this timing table alone is not a production capacity result.

## Retained failed attempts and interpretation

Earlier local logs remain under `artifacts/`; unsuccessful trials were not deleted to make the final result look cleaner.

- The initial storage/doc probe used `tx.append`; the actual release API is `tx.appendEntry`. The probe was corrected and rerun.
- The initial task no-progress probe expected an `onReport` call. Release 1.3.0 stores the faulted outcome but does not report that particular scheduler fault through the callback. The final assertion checks the durable `faulted` receipt and its progress diagnostic. No-progress was not converted into a success condition.
- Initial tool probes assumed parallel transcript result order, provider `context.tools`, and a sub-2-second Windows watcher deadline. The release instead uses call IDs, tool declarations in system messages, and roughly 2-second default polling. The corrected probes assert those contracts.
- A first manually supplied PNG had invalid compressed data. The final fixture is generated with valid chunks/CRCs, and decoding succeeds through the bundled processor.
- An initial conversation assertion treated tool handoff like a host reset. The actual release returns different submission settlements; the probes and guide now document both.
- The direct image import remains blocked by a real named-export compatibility error. It was not repaired by editing installed sources or marked passed because a separate bundled route worked.

For the full conditions and error stack, see the [tools results](tools-results.md) and [conversation results](conversation-results.md).

## Source, version, and integration boundaries

The [source review](source-review.md) checks the release feature inventory against the installed public declarations, implementation, release README, and specification. All 36 pinned source-file URLs in that review were checked against the official Git tree. Development APIs such as persisted `sleepUntil`, host wake/alarm integration, crash-loop parking/retry, `afterFailedRun`, richer telemetry, and compaction model overrides are deliberately identified as absent from 1.3.0.

The release's `runtime.sleep()` was executed as part of cancellable task phases. It is an in-invocation wait, not the development persisted sleeping state. No Cloudflare alarm example is presented as a working 1.3.0 recipe.

The following remain reviewed or untested integrations rather than passed capabilities:

- Cloudflare Durable Object deployment, alarms, eviction/hibernation, shared host SQL queues, custom SQLite adapters, and remote sandboxes.
- Real provider authentication, request/session affinity behavior, commercial classifier/image outputs, cost reconciliation, model answer quality, and summary fidelity.
- A process kill in the middle of Code Mode's journal replay, its store across reopen/fork, deep nested replay stress, and arbitrary extension upgrade compatibility.
- Power/host failure durability, multiple process owners, adversarial corruption, large histories, sustained load, memory endurance, and every image format/EXIF/resize/worker path.
- Permission enforcement by an operating-system sandbox. Node environment cwd is not a permission boundary; QuickJS's restricted globals do not remove the powers of tools the host exposes.

## Repository and artifact checks

The repository-level pattern ID validator, skill validator, skill independence tests, and payload check all passed. Their command outputs are retained under `artifacts/`. No canonical skill behavior was changed, so an isolated skill-authoring Pi evaluation or local skill sync was not applicable to this research project.

The project verifier also passed: it cross-checks TAP/JUnit totals, the exact dependency pins, all local Markdown links in the authored guide/project, and source hashes. Run it from the repository root after creating the retained test reports and frozen timing snapshot:

```powershell
uv run --script projects/pi-durable-lab/scripts/verify_lab.py
```

Its generated report is `artifacts/data/verification.json`. Diagram style/accessibility gates and Chromium/manual review passed; [diagram validation](diagrams/validation.md) records the precise scope and commands.

```powershell
uv run --script scripts/validate-pattern-ids.py
uv run --script scripts/validate-skills.py
uv run --script scripts/test-skill-independence.py
uv run --script scripts/check-repo-payload.py
```

The final Markdown guide is linked from [the repository documentation index](../../docs/README.md). Generated reports, databases, bundles, cache files, rendered diagrams, and screenshots stay under ignored `artifacts/`. The guide, test sources, pinned manifests, source review, diagram sources, and durable validation notes are authored source. No Pages examples or catalog entries were changed, and no publication was requested.

[Usage guide](../../docs/pi-durable.md) · [Diagram validation](diagrams/validation.md).
