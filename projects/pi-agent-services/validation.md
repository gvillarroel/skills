# Local pilot validation, 2026-10-24

## Subject and scope

The pilot is a generated independent application under `app/`, customized for
the existing skills checkout. It runs two agents in one hidden Windows Node
process, with separate agent Harness databases, durable event/job routing and
reconnectable control/task chat. Runtime state, credentials, machine config,
logs and generated reports are excluded from Git.

The activity assessment is a bounded convenience sample, not an exhaustive
analysis of Codex history. No recurring task title was treated as authorization
to publish, merge, purchase, delete, or message another person.

## Actual Windows/model observations

- Both agents completed a genuine initial-readiness job using
  `openai-codex/gpt-5.6-sol`, Pi CLI 0.84.2 and Pi AI/Durable 1.3.0.
- `repo-quality` observed exit code 0 from all four approved repository checks:
  pattern IDs, skill structure, skill independence and payload. The initial
  implementation scanned 10,318 relevant source files. Its report disclosed
  the bounded changed-file listing and the limits of source validation.
- `delivery-watch` observed zero open PRs, successful completed Pages CI for
  HEAD `ec1e9e16...`, and 15 relevant dirty source paths. Its report correctly
  distinguished published CI from uncommitted working-tree changes.
- A subsequent delivery-state change automatically produced another real job.
  It used a persisted transition ID rather than a fabricated PR event.
- A real follow-up chat answered from the completed quality task. Submitting
  the identical human request twice returned the same submission ID.
- Before the first restart, public evidence contained four model requests for
  quality (including chat) and three for delivery, each with matching real
  model responses and a persisted public decision receipt. After restart,
  both original task conversation/submission IDs remained unchanged; status,
  evidence and chat snapshots generated zero new requests.
- Four initial desktop start/completion attempts reached `provider_accepted`.
  This proves acceptance by the local notification operation, not visibility,
  phone delivery or a read receipt.

The original full-file capture took approximately 35 seconds. A tested
optimization anchors committed source with Git HEAD and hashes only dirty or
untracked relevant source. An actual capture took 229 ms. The fixed validator
set runs after stable changes, not on unchanged idle polls. Source mutation
during checks invalidates the report.

One actual transition report during this optimization claimed 10,309 changed
paths because it compared the old full-file checkpoint with the new dirty-source
inventory. That count was a baseline migration artifact rather than a verified
count of source changes or deletions. The watcher now identifies this transition
as `baseline-migration`, reports `baselineChanged: true`, and scopes its path
count to current dirty sources. It preserves the old checkpoint until durable
admission is acknowledged. Ten focused watcher tests pass, including a retained
10,000-path legacy-checkpoint fixture that verifies migration and restart replay.
The historical report remains intact; corrective feedback is retained
alongside its evidence so the original observation and its correction remain
auditable.

Private receipts live under `artifacts/manifests/`: `live-chat.json`,
`live-before-restart.json`, `live-after-restart.json`, and final restart receipts
when present. Operational reports are in `artifacts/state/reports/`. Public
generation evidence retains brief output summaries, hashes and version lineage;
private model thinking is not exported as decision evidence.

## Deterministic checks

The application passed 97/97 tests after watcher optimization, covering the
original service/evolution mechanics plus provider auth, outbox behavior,
targeted local events, semantic recurrence, budgets, cancellation and replay.
After final configuration/timeout alignment, 12 focused provider/integration
tests passed, compilation passed, and the moved-project standalone test passed.
Those deterministic tests use faux models and injected commands where stated;
they are separate from the actual model/Windows observations above.

Automatic jobs are limited to four per agent per UTC day and at least 15 minutes
apart; a job has an eight-minute deadline. Request timeouts/retries are bounded.
Pinned Codex ignores the generic `maxTokens` option in its wire builder, so no
server-side output-token or spending cap is claimed. User chat is separate from
the automatic watcher admission cap.

## Remaining limits

The process is running in the current Windows session. No login startup task
was installed. The read-only bridge requires an existing Pi account and fails
visibly when its credential expires; it does not provision or refresh account
credentials. Native macOS operation, mobile delivery, public webhooks and
quality across a broad corpus of real PRs remain untested.

Telegram code is implemented and disabled. WhatsApp was researched, not
connected. Phone delivery requires the owner's selected channel and private
recipient/credential configuration. No paid account or mobile message was
created. Requested self-improvement remains inactive and retains the generated
request/evidence/evaluation/promotion/rollback lifecycle.

The final complete application suite passes 98/98 tests, including the legacy 10,000-path inventory regression. Its correction is retained as feedback and an acknowledged message in the original task conversation.

## Current-agent operational review — 2026-10-25

Both pilots were already stopped at review and remain stopped. Their 15 retained
jobs include 13 completed reports and two unanswered model errors. Sampled reports
already separate partial source coverage, failed GitHub observations and older
CI from actual current results; no broad prompt-policy replacement is justified.
There are no attributable outcome-verification receipts, so completed jobs are
not labeled quality passes.

The selective custom-host repair preserves watchers/notifications and adds safe
remote draining, actual standalone process exit, exact owned-session cleanup and
observed conversation model/effort provenance. Final build, faux smoke and Node
tests pass 108/108. Retain the initial 106/107 full-suite observation with an
unchanged abrupt-recovery random-port fetch failure, its isolated pass and the
final additional late-watcher regression.

The independent `scripts/review-evidence.py` case index passes 12 deterministic
tests and indexes all retained pilot jobs without changing original SQLite
bytes. It queries stable private DB+WAL copies to avoid live SHM reader-mark
writes. Cases without actual bound outcome verification remain insufficient;
human-control completion is not inferred from model output.

The separately registered custodian was reviewed and repaired in its own private
application with its existing schedule, tools and permission boundaries. It was
returned to a healthy running state with its owned watchdog enabled; the delayed
daily slot is admitted once. Its protected implementation and live state are not
published here. [Full scoped methods, retained failures and limits](../../evaluations/pi-durable/current-agent-review-20261025.md).
