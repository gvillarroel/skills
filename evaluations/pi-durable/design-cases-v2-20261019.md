# Pi Durable design cases: revised subject, 2026-10-19

The revised frozen bundle passed the strict harness in **3/3 generalization runs**, but only **1/3** passed independent artifact acceptance. Its boundary run failed strict and independent isolation checks. This cohort does **not** satisfy the design-case release gate. Preserve these results without selecting only successful artifacts.

## Subject and method

- Skill: `pi-durable`, runtime profile, 23 files; acceptance examples excluded.
- Frozen payload SHA-256 in all four manifests: `6f25c64a9f600c4837a43dde9e9f4c78d23aba46ee320046db78da2a87fc57fa`.
- Model: observed `openai-codex/gpt-5.6-luna`, thinking `high`. The deliberate exception follows the retained Spark provider rejection recorded in `SKILLS.md` and the [initial design-case report](design-cases-20261019.md).
- Host: Windows 11 build 26200, Node 24.18.0, Pi 0.84.2. Every run used a fresh workspace, strict JSON capture, and the unchanged prompts and [independent acceptance contract](acceptance.md).
- Generalization prompt SHA-256: `3296d5a89e5912a83dfdb6eb8d568d8952dd6ae6c4fb93e89b510d33ce8b70fc`.
- Boundary prompt SHA-256: `f412dd01a075ad9a30c30c14bb1811e0284554d235d5ad36b66631d4f6025522`.

## Results

| Run ID | Strict harness | Independent acceptance | Duration |
|---|---|---|---|
| `20261019-pi-durable-generalization-v2-luna-1` | Pass | Pass | 76.244 s |
| `20261019-pi-durable-generalization-v2-luna-2` | Pass | Fail: mapping creation protocol incomplete | 58.391 s |
| `20261019-pi-durable-generalization-v2-luna-3` | Pass | Fail: schema rejects supplied input | 81.494 s |
| `20261019-pi-durable-boundary-v2-luna-1` | Fail: two tool errors | Fail: outside-workspace searches | 129.382 s |

All generalization runs produced exact nonempty `adapter-contract.json` and `operations.md` files; the boundary produced exact nonempty `compatibility.json` and `operations.md`. Independent PowerShell `ConvertFrom-Json` parsing succeeded for all four JSON artifacts. Every copied skill payload remained unchanged and every observed model matched the deliberate Luna exception.

## Artifact review

Generalization repetition 1 met the fixed contract: it distinguished delivery and logical build IDs, selected failed events, retained the supplied build-100 duplicate as one investigation and build-101 as another, specified stable files/startup scanning, durable admission before acknowledgement, an atomic Pi conversation-plus-mapping path, stable request IDs, restart reconciliation, confined untrusted logs, same-thread chat, busy policies, idle behavior, and realistic Windows/macOS lifecycle choices. It correctly described a custom CI adapter and a separate supported integration for the existing Codex task console. Its observable checks were explicitly a future verification plan, not invented execution results.

Repetition 2 covered most of those requirements but only said to create/recover the job conversation and persist its mapping before submission, then reconcile after restart. It did not specify atomic conversation-plus-mapping creation or an equivalent concrete protocol closing the crash window between creation and recording the ID. That fails generalization criterion 3. Stable request IDs cannot deduplicate inputs sent to a newly duplicated conversation. Classification: **agent**, applying an otherwise documented requirement incompletely.

Repetition 3 included an atomic mapping path and a robust hashed logical identity, but its `input.eventSchema.properties.commitSha.pattern` was `^[A-Fa-f0-9]{7,128}$`. The supplied task fixture uses the literal six-character value `a1b2c3`; the emitted schema rejects that input. This fails supplied-input compatibility under criterion 1. No prompt required a full-length Git SHA. Classification: **agent**, introducing an unsupported schema restriction.

The boundary's artifact content correctly marked all four named development APIs absent from 1.3.0, cited the bundled pinned-version evidence, recommended host event/timer waiting and bounded recovery, covered queued follow-ups after failure, separated idempotency from replay policy, and recorded Windows observation without a macOS/native-service claim. Those correct deliverables do not override its failed execution gates.

## Trace review

The three generalization runs had 11, 12, and 11 tool calls, zero reported tool errors, valid events, passing exact-path/integrity gates, and passing retained `read-surface.json` summaries. Reads were limited to the prompt, `SKILL.md`, and five relevant references. Bash calls observed the host and checked generated artifacts; no dependency install, network request, credential access, daemon, or OS registration occurred.

The boundary used 22 tool calls. It searched the user's home tree, global npm package directory, other evaluation runs, and the global npm cache while looking for installed declarations unavailable in its own workspace. Two broad `find` operations failed and were reported as tool errors at event-check lines 391 and 574. The global/cache/sibling searches also violate independent isolation expectations even where individual commands returned success. The final artifacts themselves acknowledged that installed declarations were absent and used the bundled evidence instead; that conclusion should have been reached without ambient searches. Classification: **agent** scope violation, with a need for clearer instructions on unavailable dependency evidence. No provider-outage or native-platform explanation is inferred from the trace.

## Reproduction

From the repository root, with a workspace-contained uv cache:

```powershell
$env:UV_CACHE_DIR = Join-Path (Get-Location) 'evaluations/runs/pi-durable-cache/uv'
uv run --script scripts/run-pi-skill-eval.py pi-durable --prompt-file evaluations/pi-prompts/pi-durable-generalization.md --mode json --strict --model openai-codex/gpt-5.6-luna --run-id 20261019-pi-durable-generalization-v2-luna-1 --expect-output adapter-contract.json --expect-output operations.md --timeout-seconds 240
uv run --script scripts/run-pi-skill-eval.py pi-durable --prompt-file evaluations/pi-prompts/pi-durable-boundary.md --mode json --strict --model openai-codex/gpt-5.6-luna --run-id 20261019-pi-durable-boundary-v2-luna-1 --expect-output compatibility.json --expect-output operations.md --timeout-seconds 240
```

Generalization repetitions 2 and 3 changed only the repetition suffix. The three generalization invocations ran concurrently in independent workspaces; the boundary was also independent. Each trace was summarized with:

```powershell
uv run --script scripts/summarize-pi-json-events.py evaluations/runs/<run-id>/events.jsonl --output evaluations/runs/<run-id>/read-surface.json --require-model gpt-5.6-luna --require-tool-call --fail-on-invalid-json --fail-on-tool-error --require-read ../prompt.md --forbid-read-regex '(?i)(^|[\\/])assets[\\/]examples([\\/]|$)' --forbid-read-regex '(?i)^skills[\\/](?!pi-durable([\\/]|$))'
```

Summary exit codes were zero for all generalization runs and one for the boundary. Every raw manifest, artifact hash, event stream, gate result, generated deliverable, and read-surface summary remains under ignored `evaluations/runs/<run-id>/`. These are instruction-selection/design tests; none establishes a functioning custom CI adapter, Codex bridge, live-provider quality, native service registration, or macOS lifecycle behavior.
