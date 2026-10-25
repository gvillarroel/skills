# Complete managed-agent lifecycle, 2026-10-25

## Delivered scope

The Pi console now covers creation, offline inventory, owner status,
start/pause/resume/drained stop/restart/recovery, public logs, task verification,
requested evolution, per-user login deployment, archive and reconnection.
Owner, quality and operations menus are grouped and paged before rendering;
creation/reconnection remain pinned in large inventories. Generic harness
`/agents` commands remain untouched.

Lifecycle writes require a project-local managed descriptor, the exact host
digest and an authenticated PID/nonce/configuration identity. External/custom
services retain chat and read-only status through their existing integration.
This revision does not migrate or overwrite their source or private state.
Archive removes only a stopped registration and preserves all project files.

Each new application carries its own compiled control CLI under
`dist/src/console/`, verification CLI, evolution engine, prompts, dependencies
and runbook. It operates after the original console/skill is unavailable.
Native login plans use the managed host; installed starts follow the owned
native registration rather than creating a second detached owner. Managed
macOS plans restart unsuccessful exits and leave a clean drained stop stopped.

## State, duty and improvement contracts

Status inspects every actual live Harness task and unsettled submission,
including control, child and retained background work. It distinguishes active
generation from cumulative provider calls and process/queue state. Pause
persists, blocks new admissions/polling and lets accepted work drain. An
in-flight poll after pause cannot admit work or advance its checkpoint.
Admission while paused returns 503; a busy shutdown deadline returns 409,
preserves work and leaves admissions paused. Stop never implicitly aborts.
Explicit `abort --background` has its own human review.

Duty verification starts disabled. Concrete literal-output, structural-JSON or
bounded workspace-file assertions produce passed, failed, inconclusive or
unconfigured receipts. Receipt identities bind the actual agent, admission,
conversation, completed submission, source version, output hash and contract
hash. A process being alive, completed submission or self-claimed success does
not establish a quality pass. File assertions observe current files rather
than proving which actor created them.

Requested evolution records exact editable paths, observed evidence and a
trusted frozen verifier/fixtures. Reflection drafts and imported candidates
stay inactive. Promotion requires a passing exact paired evaluation and
drained/stopped work; build and offline smoke precede explicit restart.
Rollback restores exact original bytes. The duty contract, management code and
core workspace/repository permission tools are protected. History reports
metadata-only transactions and observed source-byte activation state, without
exposing preimages or confusing historical commitment with current activation.

## Frozen subjects and isolated forward trial

| Subject | Files | SHA-256 |
|---|---:|---|
| Delivered/final runtime | 102 | `9b4e575546f2003baa67ec55f7d72156ffec5cd3e29e0f0e67a1334cf66b07cb` |
| Delivered/final full bundle | 134 | `f076c400af8ec52f15519fba569763bcad4edac7d16e48ef22d0d49c81d64a95` |
| Retained first runtime | 102 | `c60c5ba3ed14723588a042745ee750aafb23c77a558c28f0adfd1b939476ac0b` |
| Retained first full bundle | 134 | `2dd1108f6335fbb977668b1f6c36e36d882546adbecd9b485576e32719c90ca0` |

The user's current `openai-codex/gpt-6.1-sol`, medium reasoning, continues the
recorded forward-model exception. The final scoped
[lifecycle contract](../pi-prompts/pi-durable-lifecycle-contract.md) passes
**1/1 strict, artifact, independent and manual gates**. It creates the actual
independent faux service in an exact folder with spaces, uses its compiled
control CLI, exercises pause refusal/restart, persists positive and negative
duty receipts, and proves the final PID absent and state-owner lock released.
Its copied runtime payload remains unchanged; there are no observed tool errors
or forbidden reads. It installs no OS jobs and performs no nested real inference.

```powershell
uv run --script scripts/run-pi-skill-eval.py pi-durable --prompt-file evaluations/pi-prompts/pi-durable-lifecycle-contract.md --model openai-codex/gpt-6.1-sol --thinking medium --mode json --strict --require-prompt-read-first --run-id pi-durable-lifecycle-v2-20261025-contract --expect-output outputs/console/scaffold-manifest.json --expect-output "outputs/workspace with spaces/.pi/durable/lifecycle-eval/managed-agent.json" --expect-output outputs/lifecycle.json --expect-output outputs/verification.json --expect-output outputs/report.md --timeout-seconds 900
uv run --script scripts/summarize-pi-json-events.py evaluations/runs/pi-durable-lifecycle-v2-20261025-contract/events.jsonl --require-model gpt-6.1-sol --fail-on-invalid-json --fail-on-tool-error
uv run --script evaluations/contracts/pi-durable-lifecycle.py evaluations/runs/pi-durable-lifecycle-v2-20261025-contract/workspace --output <new-external-receipt.json>
```

The evaluator compares generated code with the frozen source, reads actual
SQLite verification evidence/receipts, probes the last owned PID through a
read-only Windows process handle, and checks the released state-owner lock.
Four negative controls reject a false stopped state, changed conversation,
self-claimed negative-control pass and altered console source. Positive data
is restored. Mutable connection registration is not treated as immutable source;
the receipt-selected registry may be the adjacent default or another explicit
workspace-local file. Initial overly restrictive checker receipts remain beside
the corrected receipts; no candidate output was changed for the checker.

The first frozen trial remains **0/1 strict** despite correct artifacts/manual
results: it guessed `verification-cli.ts`, used unmatched source globs and
expected 409 rather than 503 for paused admission. It corrected its local probe
using the same stable request ID, without duplicating admitted work. The final
reference documents exact CLI entry names, client contracts and status codes.
The second subject also includes the independently discovered Windows encoding
fixes below. Both trials use the same prompt and distinct fresh workspaces;
do not pool them or present the first as a pass.

## Functional, live and native evidence

- Final console: TypeScript and **140/140** tests pass. They cover creation,
  current/closed ownership, stopped inventory, shared lifecycle/quality locks,
  explicit cancellation, background abort, structured receipts, model freezing,
  version activation, paged UI and decoded/redacted Unicode log tails.
- Final Windows service: build and **155/156** tests pass; the POSIX-only FIFO
  test is explicitly skipped. New lifecycle, verification, actual CLI shutdown
  and four provider-session ownership regressions pass. Event/chat and
  parallel/pipeline faux smokes pass, with zero duplicate admission and reopen
  generation. Existing POSIX reader evidence remains in the prior creation
  report; native macOS is not inferred from it.
- Actual faux full cycle passes **9/9**, including renaming the entire original
  console away, then operating through the independent project's CLI. A fresh
  final factory separately verifies all 57 authored initial hashes, actual
  process exit, a real compiled Windows login plan with execution false, and
  a **10/10** continuation on the same project/task. No OS job was installed.
- Actual verification/evolution cycle passes **8/8**: the same predeclared
  contract rejects self-claimed completion and accepts its actual marker;
  failed/passed verification records feed the request/reflection pack. A real
  paired evaluation improves **0.75 to 1.0** on the synthetic task-policy
  fixture, then promotes, builds/smokes, restarts, rolls back exact original
  bytes, rebuilds/smokes and restarts. Final owner is stopped. This proves those
  mechanics, not PR-review intelligence or private task-quality gain.
- Actual Sol 6.1 performs one `workspace_read` task with two real responses.
  Its exact-output contract passes; an intentionally wrong criterion fails
  against that same output, then the original contract is restored. Recovery
  retains conversation/output hashes and performs no task reroll. Real model
  locking preserves a catalog snapshot, original configuration backup and
  exact Sol 6.1/medium choices. One separately requested no-tool Sol reflection
  returns an **inactive null candidate**, correctly recognizing the negative
  control and insufficient evidence of a repeated defect. No real source
  candidate is activated. Final owned live host is absent.
- Actual Windows Pi **1.4.0 at 110x38** and pinned **0.84.2 at 48x20** pass with
  32 and 33 ConPTY frames. Twenty-four stopped agents span six pages with the
  creation action/title visible. Real menus/reviews verify default cancellation,
  explicit Apply, failed/inconclusive outcomes, promotion/rebuild and no
  automatic restart. Effects are injected in-memory; no model/service/native
  job is invoked. Actual RPC separately verifies exact targets, grouped stages,
  empty outer-model context and zero remaining owned fixture processes.

The actual-service evidence is under the ignored
`projects/pi-durable-lifecycle/artifacts/` tree: `fullcycle-faux/`,
`final-factory/`, `quality-fullcycle/`, `live-sol/` and `native-ui/`.
Recheck terminal evidence with `node .../native-ui/verify.mjs`. Executed UI
component hashes match canonical source; later backend-only refinements were
mocked in that presentation probe and are covered separately above.

## Failures retained and repaired

The first real Sol task passed its duty checks but revealed an owned Codex
WebSocket keeping Node alive after the Harness/database closed. The exact inert
test PID was terminated only after matching command line, creation time,
creation receipt, available exclusive state lock and `runtime.closed` evidence.
Its original failed receipt remains intact. A guarded host/descriptor/runtime
repair preserves the initial manifest and completed submission; the validated
continuation performs no extra task generation. Providers now release only
their observed sessions after their Harness closes, with shared-session
reference counts. The isolated reflector does the same. Standalone hosts also
perform final owned-process cleanup, bounded stream flushing and explicit exit.
Missing active receipts with a still-live retained PID fail closed as
unreachable rather than claiming stopped; explicit recovery never kills a PID.

The first compact operation menu overflowed its 48x20 terminal. Grouped, paged,
width-bounded menus fix it. Windows fixture teardown and unnecessary attempts
to rename their own working directory encountered EBUSY. Those receipts remain
separate; same-project continuations and bounded teardown retries address the
fixture conditions without repeating model tasks or masking product failures.

Actual Windows PowerShell **5.1.26100.9711** exposed a further native defect:
UTF-8-without-BOM script literals corrupted a `Café 日本` working folder.
Windows `.ps1` artifacts now carry a BOM. The same unchanged fake host/folder
passes with the canonical runner: exit 0, empty stderr and exact Unicode path.
Native PowerShell redirection emits UTF-16LE logs; the console now detects BOMs,
aligns UTF-16 tail reads and redacts after decoding. The failing baseline and
artifact-only proposed variant remain beside `ps51-unicode/canonical-fixed-result.json`.
The probe executed no Task Scheduler action or credential/model request.

## Delivery and remaining boundaries

The installed extension and its ignored factory resources are refreshed while
both existing user registries and the registered wrapper remain unchanged.
Actual installed Pi 1.4 RPC verifies all 17 owned source files, lifecycle help,
inactive inventory/folder, real managed status and disabled duty inspection,
then cancels the actual stop review. The selected QA PID had been reused by an
unrelated PowerShell process; the console correctly reports conservative
unreachable state while exact QA host identity is absent. It kills nothing.
Both user registries and protected QA source/SQLite hashes remain unchanged;
there are zero outer generations, user-service/native mutations or remaining
owned Pi processes. The temporary registry selects only QA, never user agents.
The required repository sync copied 28 source-owned files; scoped refreshes
include the final encoding/reference/test changes and verify all 134 files.
Registry files remain outside this change's staged paths. Pattern, skill,
independence, payload and scaffolder checks are part of release closure.

Native macOS activation, actual native login installation, logout/sleep
behavior, mobile delivery, unattended credential renewal and broad private
quality improvement remain unverified. Native plans and execution mocks are
distinguished from a real OS registration. Source-byte activation history is
distinguished from a completed rebuild, restarted owner and verified task.
The retained forward outputs contain the existing `[CIRCULAR]` marker for some
shared provider metadata; version digests, admission IDs and persisted version
manifests remain authoritative rather than claiming lossless display of every
repeated in-memory field.
The skill remains `validating` for these and previously recorded broader
authoring/installer cohort gaps. It is not promoted by one scoped lifecycle case.
