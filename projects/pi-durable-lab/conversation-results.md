# Pi Durable 1.3.0 conversation probe results

Date: 2026-10-19. Packages: `@earendil-works/pi-durable`, `pi-ai`, and `chord` pinned to 1.3.0. Runner: local `tsx` 4.20.6 and Node's built-in test/assert APIs. See the project lockfile for the complete dependency graph.

The suite executes the real Harness, registry, tasks, transactions, submissions, observations, compaction, ownership, and usage accounting against MemoryStorage. The official `pi-ai/providers/faux` provider supplies explicit scripted responses and estimates token usage. There are no remote model calls or credentials. These are behavior and integration probes, not a comparison of real model answer quality, provider cache billing, latency, or production throughput.

Run from `projects/pi-durable-lab/`:

```powershell
.\node_modules\.bin\tsx.cmd --test scripts/conversation.test.ts
.\node_modules\.bin\tsx.cmd --test --test-reporter=tap scripts/conversation.test.ts
```

Final result: **30 passed, 0 failed, 0 skipped**. The observed full run took about 1.4 seconds including runner startup. This timing is descriptive only. Local TAP evidence is in ignored `artifacts/conversation/conversation.tap`.

## Observed feature coverage

| ID | Feature and tested invariant | Result |
| --- | --- | --- |
| C01 | Basic input produces an answer; requestId returns the existing submission; reacquisition by ID works; custom input entry preserves model content | Pass |
| C02 | Passive kind/data entry appends without generation and contributes nothing to model context | Pass |
| C03 | Follow-up queues behind a tool run and starts a different run; display-only writes bypass that queue; queued input abort withdraws it | Pass |
| C04 | Steer joins the active run after its tool round, sharing the original answer; reject throws ConversationBusy and writes no entry | Pass |
| C05 | Cancelling a submission waiter leaves work placed and running; conversation abort stops active work and withdraws queued inputs | Pass |
| C06 | Provider UUID has UUIDv7 form, is forwarded to requests, survives reset and model change, and is fresh on a fork | Pass |
| C07 | Fork sees history and agent choices as of its cut, then has independent later context; context(at) respects that cut | Pass |
| C08 | Configure controls extensions, enabled/callable/model tools, instructions, cwd, and thinking; null restores host tool selection; uninstall/reinstall resolves stored names | Pass |
| C09 | Plain reset empties active model context while historical entries remain; a reset note is visible as user context | Pass |
| C10 | Host reset queued during tools ends the old input unanswered with reason reset and places the handoff context | Pass |
| C11 | viewState subscription and serialized structural watch advance from committed state with actual operations | Pass |
| C12 | watchEvents begins from a snapshot and delivers run, turn, message, submission, and usage lifecycle events | Pass |
| C13 | Manual compaction hook supplies a summary without a model call, shrinks active context, preserves history and UUID, and receives instructions | Pass |
| C14 | Compaction hook can decline; default summarization calls the provider and adds usage | Pass |
| C15 | Session usage sums independent conversation spend, including failed model attempts | Pass |
| C16 | Transient rate-limit error retries; invalid input and 429 quota/billing exhaustion fail without retry | Pass |
| C17 | Deferred submission persists a handle, polls through a pending response, and completes with the final answer | Pass |
| C18 | followUpMode all groups queued inputs into one successor answer; a model-visible write waits for a turn boundary | Pass |
| C19 | Tool control.handoff resets context and settles the original input done, referring to the tool-call assistant entry | Pass |
| C20 | Automatic blocking threshold compaction completes before the next generation request | Pass |
| C21 | A failed blocking compaction prevents a generation request, settles model_error, and remains in pi.live.compactionFailure | Pass |
| C22 | Provider context overflow triggers one compaction and a successful generation retry | Pass |
| C23 | Conversation abort cancels a deferred provider handle before polling | Pass |
| C24 | Foreground subagent owns an isolated child, inherits instructions/cwd, changes model, removes recursive delegation, reuses owner index and requestId, and gets a fresh provider UUID | Pass |
| C25 | Foreground parent abort cascades through its tool to the child's active work and queued input | Pass |
| C26 | A conversation-owned background anchor and its subagent survive ordinary parent abort and idle; abort with background true reaches both | Pass |
| C27 | A throwing foreground tool owner aborts its running child before the parent finishes | Pass |
| C28 | Background compaction does not block current generation or ordinary idle and survives ordinary abort | Pass |
| C29 | A slower summary with an older cut settles stale after a newer farther summary is placed | Pass |
| C30 | Slow structural callbacks stay serialized; more than 100 pending frames coalesce; event backlog recovers using a fresh snapshot plus later delta batches | Pass |

All helper waits use explicit abort timeouts, every Harness closes in finally, each observer stops or disposes in finally, and test latches release in finally. The suite additionally asserts that Harness.onReport receives no unexpected nonfatal error. Assertions inspect actual submission status, model context, immutable entry history, documents, provider counters, observer payloads, or task receipts.

## Recommendations supported by these probes

| Situation | Recommended mechanism | Reason and operational detail |
| --- | --- | --- |
| Retried client requests or reconnects | Stable requestId per logical action; persist submission ID | C01 prevents duplicate admitted actions. The key is scoped to a conversation. A different payload with the same key still returns the original action: never reuse a key for a new instruction. |
| A new independent user task while busy | Default follow-up; one-at-a-time unless grouping is intended | C03 keeps separate answers. Use followUpMode all only when combining instructions into one next run is appropriate (C18). |
| Correct the current tool-driven task | whenBusy steer | C04 joins at the next tool boundary. This is boundary-based coordination; it does not replace an already streaming provider request. |
| Only start if work is idle | whenBusy reject | C04 provides an explicit busy failure without creating a transcript record. |
| Add UI notes or bookkeeping | Passive kind/data write | C02/C03 append immediately and avoid extra model tokens or generation. Include model messages only when the agent must see the entry (C18). |
| Cancel a UI wait or network request | Cancel that wait's Chord context | C05 leaves durable work running. To stop execution itself, call conversation.abort. |
| Build a local UI | viewState; dispose it | C11 offers a direct reactive state. For serialized remote state replication use watch and apply its operations. |
| Build a coding-agent event consumer | watchEvents and its initial snapshot | C12/C30 require consumers to handle a replacement snapshot followed by deltas. Events and tools need stable IDs for correlation. |
| Explore an alternative branch | fork at a concrete visible entry | C07 preserves the corresponding historical agent and avoids subsequent context contamination. Provider cache/session identity is fresh (C06). |
| Start a new topic without erasing evidence | reset; include a short handoff when continuity matters | C09 preserves storage history but cuts the model context. During tools a host reset makes the previous input unanswered/reset (C10). |
| End a tool-driven run and prepare the next context | Tool control.handoff | C19 returns done without a fresh prose answer; do not render every done.answer as though it were final answer text. |
| Long conversations | Automatic background + blocking compaction with context-appropriate token budgets | C20/C28 allow useful work to continue until the blocking threshold. Keep failure UI for C21; inspect task outcome and summary submission separately for manual compaction. |
| Domain-specific compression with exact invariants | beforeCompact hook returning a summary | C13 bypasses the provider summarization call. The host becomes responsible for summary fidelity. It can decline instead (C14). |
| Several compactions race | Honor stale as an expected summary-placement result | C29 protects the farther cut. Completion of the compaction task alone does not prove its summary was applied. |
| Temporary provider load | Bounded durable retries with short test delays and production-appropriate backoff | C16 distinguishes transient rate limits from quota/billing exhaustion. Failed attempts still consume tracked usage (C15). |
| Provider-supported deferred processing | stream.deferred, live deferred status, explicit abort control | C17/C23 exercise the durable handle/poll/cancel mechanics offline. Validate the selected real provider's support separately. |
| A delegated task whose answer is needed now | Replay-safe foreground tool owning its child conversation | C24/C25/C27 bind lifetime, idempotent child acquisition, input deduplication, and cancellation to the owner. Configure the child to prevent unintended recursive delegation. |
| Independent ongoing delegated work | Conversation-owned background anchor task owning the child | C26 keeps parent idle/ordinary abort independent. Expose a separate stop operation that uses abort with background true when the user intends to stop everything. |

## Interpretation corrections during authoring

Two initial assertions were based on overly broad interpretations rather than package failures:

1. C19 initially expected host reset and tool handoff to have identical submission settlement. The actual tool handoff returned done. Installed generation.js finishToolRound explicitly settles done with the prior assistant entry for tool handoff/terminate, whereas its queued host reset path settles unanswered/reset. The test now asserts this distinction and inspects the answer entry. This is a practical integration caveat.
2. C30 initially expected the replacement snapshot to contain the final write of an entire backlog. The snapshot is created when pending frames cross the limit, and later commits then arrive as delta batches. The corrected test requires a replacement snapshot, the final delta/state, fewer callbacks than writes, and single-callback serialization. No final update was lost.

No runtime defect was demonstrated by the final conversation suite. These corrections are retained so future readers can distinguish a changed test expectation from a fixed package bug.

## Limits and coverage owned elsewhere

- This suite does not prove real OpenAI, Anthropic, AWS, Cloudflare, or other provider transport behavior, real authentication, actual cache billing, deferred availability, or semantic compaction quality. Faux requests are deterministic mechanism probes.
- Filesystem JSONL/SQLite reopen, true process-kill replay, storage conformance, custom documents, checkpoint migration, graphs, and custom task joins are intentionally covered by the other project suites rather than duplicated here.
- This is broad representative feature coverage, not an exhaustive state-space proof. Some policy combinations such as every queue mode under every possible reset/failure interleaving remain untested.
- Provider session identity survival across storage reopen is delegated to the persistence suite; C06 directly covers reset/model changes/fork identity within one Harness.
- This suite does not run isolated pi skill validation because it creates no reusable skill and changes no skill behavior.

The installed package README and exported TypeScript declarations were read before authoring. Where settlement details were ambiguous, the shipped generation, compaction, event, and faux provider implementation was inspected to derive explicit assertions.
