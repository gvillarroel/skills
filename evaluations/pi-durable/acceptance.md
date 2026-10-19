# Pi Durable independent acceptance contract

Evaluate the generated artifacts independently of the agent's final answer. This contract covers isolated use of the runtime payload, excluding acceptance examples. It is evaluator-owned and must not be copied into a forward-test workspace.

## Shared gates

- Run each case in a fresh workspace containing only the task prompt, the copied runtime skill, and normal tools. Preserve the copied skill hashes.
- Require valid strict JSON event capture, the observed release-test model, zero tool errors, an unchanged skill payload, and every exact nonempty output path.
- Inspect read surfaces and shell commands. No repository/sibling/acceptance-fixture dependency, outside-workspace write, credential read, live GitHub request, real model call, service registration, or residual daemon is permitted.
- Dependency installation is permitted only for contract and naturalistic cases; npm caches must stay inside the workspace. Distinguish unavailable package infrastructure from skill failures.
- Parse every required JSON artifact with an independent JSON parser. Inspect commands/configuration and verify build results rather than accepting self-reported success. Record the real native platform from evaluator evidence.
- Preserve every run result and classify failure as `skill`, `agent`, `validator`, `harness`, `infrastructure`, or `external-service`. A blocked model/infrastructure run is not a pass.

## Contract smoke

Required outputs: `service/package.json`, `service/config.json`, `plan.json`, `verification.md`.

1. Verify the exact scaffold command appeared in the trace and the project was generated outside the skill.
2. Check exact 1.3.0 runtime dependency pins, an offline `faux` provider, agent ID `contract-reviewer`, and disabled GitHub detection.
3. Compile the generated project independently or inspect a recorded successful `npm run build` and verify its output. The CLI plan must be emitted by executing the compiled CLI, not invented by the agent.
4. Parse `plan.json`; verify the plan's platform matches the observed host, `executed` is false when the CLI wraps a dry-run result, and artifacts/commands resolve to the chosen service identity. Missing execution flags can be accepted only if the CLI schema is a plain `ServicePlan` and trace inspection proves dry-run.
5. Check that verification distinguishes generated native plans from registration and gives usable foreground/console commands. Check the process table or recorded shutdown to confirm no daemon remains.

Run once after deterministic bundle checks pass.

## Naturalistic forward use

Required outputs: `service/config.json`, `OPERATIONS.md`, `plans.json`.

1. Check the generated configuration identifies `atlas-reviewer`, repository `acme/widgets`, offline provider, PR polling, and an interval of 60,000 ms. The task did not authorize running GitHub polling during validation.
2. The private-review instructions must not authorize posting, merging, shell execution from PR content, or arbitrary repository access. First-run behavior should avoid an unrequested historical import.
3. Parse both deployment plans. Check Windows and macOS paths against the prompt, correct platform values, a Task Scheduler login trigger and a user LaunchAgent respectively, argv/path quoting, correct log paths, and all lifecycle actions. macOS must use UID 501 and the supplied home directory.
4. Build the generated project independently when installation succeeded. Do not require unavailable acceptance tests from the runtime payload. Check generated lifecycle data without executing registration.
5. Check commands against the actual compiled CLI or its usage text. The guide must cover list agents, inspect/list jobs, a stable job ID for task chat, correcting current work with `steer`, later work with `followUp`, snapshot/reconnect behavior, stop/status/uninstall, and the configured environment/state/log paths.
6. Explain one-owner storage, durable event and request deduplication, recovery after a receipt/admission interruption, idle periods without model polling, and laptop login/sleep limits. Actual testing must identify its native platform and distinguish Windows/macOS dry-run plans from native installation.

Run three fresh repetitions; require at least two complete passes. Because external writes and registration are explicitly excluded, do not treat this as a safety-critical activation benchmark.

## Generalization beyond GitHub

Required outputs: `adapter-contract.json`, `operations.md`.

1. Parse a coherent input contract containing every supplied CI field and selecting failed builds. File detection must be ordinary host code and account for complete-file publication, duplicates, startup scanning, and out-of-order arrival.
2. Separate delivery identity from logical build identity so delivery-1 and delivery-2 produce one investigation for engine/build-100 at a1b2c3; build-101 remains separate. Accept alternative key encodings with equivalent semantics.
3. Require durable admission before marking/removing/acknowledging an input file, atomic job-to-conversation mapping or a concrete equivalent reconciliation mechanism, stable Pi request IDs, retryable accepted work, and explicit effect idempotency boundaries.
4. Human chat must resolve to the saved build investigation. Control chat and job chat must not collapse all build logs into a single ever-growing transcript. Correct and subsequent messages need deliberate busy policies.
5. The guide must name the missing/custom local-file adapter and avoid claiming the shipped GitHub adapter already implements CI files. Windows/macOS lifecycle choices must be feasible and remain plans.
6. Codex integration must be assessed honestly: a custom local registry/chat console is feasible, but arbitrary Pi conversation insertion/attachment into Codex's sidebar is not a capability established by this skill. Require a supported bridge or an explicit unsupported boundary; reject fabricated registration commands or successful external-console claims.
7. Require an offline verification sequence with observable duplicate, restart, chat reattachment, and idle outcomes. Report the observed native platform; do not invent executed tests.

Run three fresh repetitions; require at least two complete passes.

## Boundary and recovery

Required outputs: `compatibility.json`, `operations.md`.

1. Parse the 1.3.0 version and individual verdicts for `runtime.sleepUntil`, `harness.wake`, `restartLimit`, and `harness.retryTask`. All four are absent from this release. Evidence should cite the pinned official source/declarations or exact bundled compatibility reference rather than unversioned main.
2. Recommend host event/timer waiting, persistent deadlines/checkpoints, explicit queue/restart reconciliation, and supervisor limits without invoking unsupported APIs or changing the pin. Mention that release `runtime.sleep` waits inside a live invocation if proposing it.
3. Require one owner per store, recovery through reopened state and scheduling, replay-safe versus idempotent external effects, and explicit handling of follow-ups left queued after model failure.
4. Inspect every executable snippet: no main-only API, automatic external retry claim, exactly-once effect claim, or OS registration command is executed. A hypothetical deployment command can be documented with its scope stated.
5. Check the native platform record against evaluator evidence and require separate native verification of other-platform lifecycle. Generated/configured plans alone do not prove macOS startup behavior.

Run once. A failure exposing incorrect API compatibility or false platform claims must be repaired before release.

## Evidence summary

Record case, repetition, date, model, prompt/payload hashes, full command, required paths, strict-harness checks, independent artifact checks, observed native platform, result, and failure classification. Keep raw runs ignored under `evaluations/runs/` and link a compact durable summary from the backlog validation notes.
