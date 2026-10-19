# Pi Durable generalization: final frozen subject, 2026-10-19

The final frozen subject has **0/3 passing strict generalization runs** within the configured 240-second deadline. All three created both requested artifacts, and their captured traces passed model/read-surface checks, but each helper recorded a timeout. Repetition 3 also emitted a schema that rejects the task's supplied `a1b2c3` value. This cohort does not satisfy the required two-of-three joint acceptance threshold, so it cannot justify marking the skill done.

This note covers only the three delegated generalization runs. The final contract, boundary, naturalistic, deterministic, and repository checks are recorded separately by their owners. Earlier unsuccessful subjects remain in [initial design cases](design-cases-20261019.md) and [revised design cases](design-cases-v2-20261019.md).

## Subject and constraints

- Runtime skill: `pi-durable`, 23 copied files, `assets/examples/` excluded.
- Frozen payload SHA-256, identical in all three manifests: `b6fa474c26b9a3dfc3ae3920b3a4edcb145ad132e0028ba23e0c8dc4f267590d`.
- Prompt: [generalization](../pi-prompts/pi-durable-generalization.md), unchanged SHA-256 `3296d5a89e5912a83dfdb6eb8d568d8952dd6ae6c4fb93e89b510d33ce8b70fc`.
- Acceptance: [independent contract](acceptance.md), unchanged criteria and two-of-three threshold.
- Model: requested and observed `openai-codex/gpt-5.6-sol`, thinking `high`. `SKILLS.md` records this deliberate complex-authoring exception after the retained Spark rejection and unsuccessful Luna cohorts. No unsupported-model explanation is inferred for these Sol runs.
- Host: Windows 11 build 26200, Node 24.18.0, Pi 0.84.2. Native platform was observed as `win32`; no OS service or macOS lifecycle was executed.
- The three runs were concurrent and used independent fresh workspaces. No source changes were made during the cohort or after its freeze.

## Results

| Run ID | Strict result | Recorded wall time | Artifact diagnostics |
|---|---|---|---|
| `20261019-pi-durable-generalization-v3-sol-1` | Timeout, no pass | 268.206 s including cleanup | Both outputs exist; JSON parses; supplied fixture accepted by emitted schema |
| `20261019-pi-durable-generalization-v3-sol-2` | Timeout, no pass | 268.200 s including cleanup | Both outputs exist; JSON parses; supplied fixture accepted by emitted schema |
| `20261019-pi-durable-generalization-v3-sol-3` | Timeout, no pass | 253.931 s | Both outputs exist; JSON parses; emitted schema rejects supplied fixture |

Every `evaluation-result.json` records `returnCode: 124`, `timedOut: true`, and unchanged skill integrity. These runs were not silently repeated or counted as completed passes. The evaluator did not award full independent artifact acceptance after the failed strict gate.

The exact nonempty files are `adapter-contract.json` and `operations.md`. Evaluator-owned `independent-artifact-check.json` records their byte counts and SHA-256 hashes in each raw run directory, along with independent JSON parsing and a direct supplied-fixture check.

## Independent diagnostics

The verifier recursively located the emitted event schema with all six task fields and checked the literal task instance:

```json
{"eventId":"delivery-1","project":"engine","buildId":"build-100","commitSha":"a1b2c3","status":"failed","logPath":"logs/build-100.txt"}
```

It applied the emitted string types, length bounds, enum values, and regular-expression constraints without introducing a hidden SHA grammar. Repetitions 1 and 2 accepted this instance. Repetition 3 used `$.input.schema.properties.commitSha.pattern = "^[0-9A-Fa-f]{7,64}$"`, rejecting the supplied six-character value. This is an **agent** artifact defect independently of its timeout. The same failure shape appeared in the preceding Luna subject and remains retained.

Captured trace summaries all passed with observed Sol models, zero invalid JSON lines, zero reported tool errors, and unchanged skill bundles. Tool-call counts were 10, 11, and 11. Every run read only the prompt, `SKILL.md`, and five focused references: event architecture, runtime decisions, service lifecycle, version compatibility, and template operations. Bash commands observed the native platform and, in repetitions 2 and 3, parsed or checked the generated artifacts. The captured commands did not search global caches, other evaluation runs, or user-home trees, and did not install packages, call the network, read credentials, or register a service.

The traces therefore show that the explicit bounded-evidence guidance avoided the earlier outside-workspace declaration searches. A passing trace summary is not a substitute for the failed process-exit/deadline gate or the supplied-input check.

## Timeout handling and limits

The helper's 240-second subprocess deadline killed the `pi.cmd` parent in repetitions 1 and 2 while a Node child retained capture-pipe handles. Before the deadline, the evaluator recorded the live helper-to-child ancestry. After verifying that each parent was absent and the child still had the expected Pi/Sol command line and recorded identity, only owned child PIDs 43636 and 39608 were stopped. That released the helpers and retained the timeout reports. No unrelated process was stopped.

Repetition 3's helper returned its timeout without manual child termination. Captured traces for repetitions 2 and 3 contain `agent_end` and `agent_settled`; their launcher processes still did not return within the configured deadline. Repetition 1's capture ends during another message. These observations establish incomplete bounded execution and a Windows process-tree cleanup limitation; they do not establish the root cause of the overrun or a model/provider outage. Classify the delayed cleanup as **harness**, preserve the execution timeouts, and keep the repetition-3 schema issue separately classified as **agent**.

## Commands and retained evidence

From the repository root:

```powershell
$env:UV_CACHE_DIR = Join-Path (Get-Location) 'evaluations/runs/pi-durable-cache/uv'
uv run --script scripts/run-pi-skill-eval.py pi-durable --prompt-file evaluations/pi-prompts/pi-durable-generalization.md --mode json --strict --model openai-codex/gpt-5.6-sol --run-id 20261019-pi-durable-generalization-v3-sol-1 --expect-output adapter-contract.json --expect-output operations.md --timeout-seconds 240
```

Repetitions 2 and 3 changed only the final repetition number in the run ID. After preserving all timeout evidence, the evaluator summarized each capture with:

```powershell
uv run --script scripts/summarize-pi-json-events.py evaluations/runs/<run-id>/events.jsonl --output evaluations/runs/<run-id>/read-surface.json --require-model gpt-5.6-sol --require-tool-call --fail-on-invalid-json --fail-on-tool-error --require-read ../prompt.md --forbid-read-regex '(?i)(^|[\\/])assets[\\/]examples([\\/]|$)' --forbid-read-regex '(?i)^skills[\\/](?!pi-durable([\\/]|$))'
```

All three summary commands returned zero. The raw run directories retain the exact prompt, copied payload, manifest, partial/completed event capture, stderr, timeout result, integrity result, read-surface summary, generated deliverables, and independent artifact hashes/fixture diagnostics. No further runs or source changes were performed for this delegated pass. Design outputs and platform plans are not evidence of a working CI adapter, Codex bridge, real-provider quality, service activation, or native macOS behavior.
