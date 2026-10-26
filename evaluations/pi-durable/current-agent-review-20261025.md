# Existing agent review and bounded repairs — 2026-10-25

## Scope and initial observations

Review the two local pilots and the separately registered custom repository
custodian. Preserve each application's task, exact Sol 6.1 selection, private
state and existing ownership. This is an operational/data-readiness repair, not
a measured general improvement in PR review or repository maintenance quality.

| Agent | Initial state | Recorded experience at review |
| --- | --- | --- |
| `local/repo-quality` | Stopped | 8 jobs: 7 completed and one unanswered model error; public decision evidence, no outcome-verification receipt. |
| `local/delivery-watch` | Stopped | 7 jobs: 6 completed and one unanswered model error; public decision evidence, no outcome-verification receipt. |
| `custodian/repo-custodian` | Running with native watchdog | Four control submissions, no completed scheduled daily cycle; zero public decisions before this revision. |

The pilots' sampled retained reports already distinguish partial source coverage,
GitHub API limitations, older-commit CI and dirty files correctly. Their unanswered
jobs do not demonstrate a policy defect. Do not force a prompt candidate against
a baseline that has not shown the proposed decision failure.

Private audit artifacts are under `projects/pi-current-agents/artifacts/`.
Credentials, raw transcripts, actual state, custom custodian source and operation
journals remain local. The user-authorized review includes that registered custom
application; its files are not added to this public repository.

## Local pilot repairs

The custom pilot host retains its watchers, notification outbox, admission caps
and exact model pin. Selective changes:

- Read the actual conversation's `AgentDoc` model/effort for request provenance;
  keep the host model separately and preserve historical job version manifests.
- Pause new admissions for authenticated shutdown, drain accepted jobs/control
  messages and actual background/child tasks, and fence late watcher/poll results.
  Success closes the actual standalone process, including retained idle handles.
- Dispose exact provider-owned sessions after Harness close; never use global
  cleanup without a session ID or close another provider owner's shared session.
- Preserve accepted work on a busy deadline. This legacy host returns 409 and
  resumes admissions; drain admission refusals return 503. It is different from
  the new console's persisted-pause management API.
- Add independent case indexing and self-contained operator readiness guidance.
  The existing task prompts remain unchanged because the sampled decisions do
  not justify a semantic policy replacement.

From `projects/pi-agent-services/app`:

```powershell
npm run build
npm test
npm run smoke
uv run --script scripts/test-review-evidence.py
uv run --script scripts/review-evidence.py --config config.local.json --output ../artifacts/reviews/current-agent-cases.json
```

Final Node suite: **108/108**, including five actual shutdown/process/race cases,
four owned-session cases and seven evidence/provenance cases. Compilation and
the native faux dedup/reopen smoke pass. One subprocess accepts two queued jobs
plus a control message, completes all three, exits zero despite an injected idle
interval, releases SQLite ownership and reopens without another generation.

Retain the first full-suite observation: 106/107, with the existing abrupt-death
recovery test reporting Undici `fetch failed / bad port`. The unchanged isolated
case passes; the final full suite includes an additional late-watcher regression
and passes 108/108. No production pilot owner or real provider was started.

## Byte-preserving private case indexing

The project-local `review-evidence.py` reads stable private DB+WAL copies; it
never opens live source databases with SQLite. Direct `mode=ro`/`query_only`
was observed to update live SHM reader marks during helper development. Source
hash/stat and copy-hash checks reject concurrent changes and rollback journals;
temporary cleanup is scoped to its own artifact directory. No cross-database
atomic snapshot is claimed.

All **12** independent helper tests pass, covering missing databases, bounds,
wrong-agent/case/hash receipts, failure retention, human-control ambiguity,
concurrent writers, live WAL visibility and unchanged original DB/WAL/SHM bytes.
Actual invocations index all 15 pilot jobs and correctly report no verified
outcomes. Custodian control work is explicitly unjoined rather than inferred
complete from model responses. Byte comparisons around both actual invocations
confirm the original SQLite files and sidecars are unchanged.

The index retains identities, evidence IDs, version/result hashes and gaps without
raw inputs, results or private summaries. Even a correctly attributed historical
verification would require claim-specific readiness review.

## Custom custodian repair and deployment

Prepare an isolated authored-source copy, reproduce the old process-lifetime
defect with a faux owner and inert idle handle, and test before touching live
source. The original probe accepted shutdown and released SQLite ownership but
left its process alive. The corrected identical probe exits zero.

The reviewed patch preserves configuration, exact Sol 6.1/medium, maintenance
worker/tool, repository/workspace boundaries, scanner policy, exclusions, package
pins and evolution permissions. Changes add closed lifetime, exact owned-session
cleanup, busy shutdown refusal without cancellation, HTTP/daily admission fences,
evidence-only prompt/runbook guidance and a persistent watchdog pause.

An independent review found an accepted-message admission race in the first
candidate. The final candidate checks the in-flight admission counter before
activity snapshots and retains the postcheck. Its adversarial regression holds
an accepted message until a stale activity snapshot would otherwise miss it;
shutdown refuses with 409, preserves that message and later succeeds.

Validation of the exact frozen candidate:

- Node build and **139/139** tests.
- Focused scheduler/session/lifecycle/process regressions **11/11**.
- Disposable local-Git fixed-worker security fixtures **8/8**.
- Python watchdog checks **14/14**.
- Native PowerShell 5.1 AST/mock checks **7/7**, without OS job effects.
- Both faux service/specialist smokes.

Retain initial isolated-copy omissions: missing scaffold manifest and scanner
metadata caused fixture failures. Restoring unchanged authored provenance and
read-only scanner dependencies resolves them; these are not agent-quality gains.

For live deployment, suspend the exact owned watchdog trigger and stop the
authenticated owner. PID 31200 exited normally; no forced termination occurred.
Back up stopped state without credentials, validate every source preimage, and
apply only 11 changed existing files plus three regression tests. Rebuild and
run the deployed project's faux smoke before restarting its native service.

The first native startup failed on a 15-second Pi model-inventory timeout. It
admitted no daily work. Suspend retries while diagnosing; an independent bounded
inventory returns seven models, including Sol 6.1, in 6.484 seconds. One startup
retry succeeds without changing configuration or credentials. Restore the owned
service and watchdog registrations to enabled. The revised watchdog `stop`
disables its five-minute trigger as well as stopping the current run; `start`
enables then starts it. No new registration or schedule was created.

At local 20:08, authenticated discovery succeeds, control conversation 1 contains
the exact updated prompt and retains observed Sol 6.1/medium, and one overdue
daily submission for October 25 is admitted with stable identity 117. The first
post-restart observation records a real public decision; this demonstrates
collection use, not correct completion of daily maintenance. The daily result
remains in progress at the recorded checkpoint.

Continuity checks compare immutable pre-maintenance bytes with the restarted
service: all 117 evidence records, 55 entries, 50 tasks and four submissions are
retained. Updated current profile documents are intentionally excluded. The
original scaffold manifest is preserved; exact rollback source and activation
hashes remain in the private stopped backup/patch receipt.

## Reusable skill promotion and isolated checks

Promote the WAL/SHM lesson to `references/evidence-readiness.md`; no project helper
or custom runtime becomes a skill dependency. The compact reference remains
8,862 bytes. New frozen runtime: 103 files,
`b6aacc9da69f39abb134adb3082940f771ff89a68b3b893787f26be5946f10e3`;
full: 135 files,
`82957c9933484ff8849805492322fa81e9f6a0d66d416ccf7e303eb57771c838`.

Run IDs use `pi-durable-current-review-guidance-20261025-` followed by `contract`,
`natural-1`, `natural-2`, and `natural-3`. All four pass strict/artifact/manual and
read-surface checks with 94/94 independent artifact checks, zero tool errors,
valid JSON and unchanged copied skill. User-requested Sol 6.1/medium remains the
recorded model exception. Older subjects and failures are not pooled.

```powershell
uv run --script scripts/run-pi-skill-eval.py pi-durable --prompt-file evaluations/pi-prompts/pi-durable-evidence-guidance-contract.md --model openai-codex/gpt-6.1-sol --thinking medium --mode json --strict --require-prompt-read-first --run-id pi-durable-current-review-guidance-20261025-contract --expect-output outputs/agent/scaffold-manifest.json --expect-output outputs/agent/AGENTS.md --expect-output outputs/agent/prompts/pr-reviewer.md --expect-output outputs/handoff.md --timeout-seconds 600
uv run --script scripts/run-pi-skill-eval.py pi-durable --prompt-file evaluations/pi-prompts/pi-durable-evidence-guidance-naturalistic.md --model openai-codex/gpt-6.1-sol --thinking medium --mode json --strict --require-prompt-read-first --run-id pi-durable-current-review-guidance-20261025-natural-1 --expect-output outputs/readiness.json --expect-output outputs/agent-instructions.md --expect-output outputs/operations.md --timeout-seconds 600
```

Repeat the second command with fresh run IDs `natural-2` and `natural-3`. Run the
existing evaluator-owned `evaluations/contracts/pi-durable-evidence-guidance.py`
and `scripts/summarize-pi-json-events.py` on each run, requiring the exact model,
valid JSON and zero tool errors. Trace reads stay within the own focused
references/generated outputs; no credentials, sibling skills or live services
are accessed. Source/installed parity and required pattern, structure,
independence and payload gates pass. The broader skill remains `validating` for
its previously recorded gaps; this review proves neither general task quality
nor native macOS operation.
