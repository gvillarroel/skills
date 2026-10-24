# Pi console user-wide installation, 2026-10-24

## Subject and frozen payload

This update documents the supported local-file `pi install` workflow for the
independent Pi Durable console. Global registration and project discovery must
identify the same wrapper entry. Registering its implementation package beside
a different project wrapper loads two extension instances, duplicates the tool,
and can suffix commands. A local file registration references existing files;
dependencies remain beside the implementation, and moves require registration
updates. Runtime code and acceptance tests are unchanged.

The frozen `pi-durable` runtime payload contains 48 files, SHA-256
`f71d51386aaa923668022c7bbd1f9d9a4b5d8f2b0b1fc5835b2c51d9b64ad1dc`.
The full bundle contains 59 files, SHA-256
`3e39ef344ffa4d48df7c6c4642b4b53c0f9097e00b502f099b33d7a1244d4d39`.
The console uses Pi Coding Agent 0.84.2 on Windows with Node 24; the service's
Pi Durable 1.3.0 version is separate.

## Actual authorized installation: pass

At the user's explicit request, the supported CLI registered the project's
existing `.pi/extensions/durable-agents.ts` loader in the user's Pi settings.
Other settings and previously registered packages were preserved. Native Pi
RPC probes then used normal automatic discovery, without `-e` or an isolated
Pi home, from both the repository and an unrelated Windows system directory.
Both registered exactly `durable` and `durable-chat`, with no generic aliases
or duplicate tool error.

Both probes passed help, list, services, status, jobs, public history, evidence,
and chooser cancellation. They emitted no stderr, invalid JSON or outer model
events, made no remote submissions, and preserved service job/transcript
digests. Provider counters stayed at 4 for `repo-quality` and 2 for
`delivery-watch`; both remained configured for `openai-codex/gpt-6.1-sol`.
The visible Windows Terminal was opened with `pi /durable` and its Pi process
remained alive. This process check does not claim a screenshot-based UI audit.
Native macOS installation remains unverified.

Private receipts remain under the ignored
`projects/pi-agent-services/artifacts/pi-extension-install/`. Personal settings,
tokens and full native event traces are not published.

## Isolated skill-only installer contract: strict fail, artifacts pass

One frozen `contract-smoke` attempt used the previously recorded
`openai-codex/gpt-5.6-sol` benchmark exception. The deployed agents separately
use the user's requested Sol 6.1. The test copied only the runtime skill and
used an offline service fixture. Every nested Pi command set a disposable
workspace-local `PI_CODING_AGENT_DIR`, `PI_OFFLINE=1`, and `PI_TELEMETRY=0`.
It did not start a backend, message an agent or run a nested model session.

```powershell
uv run --script scripts/run-pi-skill-eval.py pi-durable --prompt-file evaluations/pi-prompts/pi-durable-pi-global-install-contract.md --model openai-codex/gpt-5.6-sol --mode json --strict --run-id pi-durable-pi-global-install-20261024-contract --expect-output fixtures/service/config.json --expect-output outputs/pi-console/extension.ts --expect-output outputs/pi-console/src/client.ts --expect-output outputs/pi-console/durable-agents.json --expect-output outputs/pi-console/scaffold-manifest.json --expect-output outputs/demo-project/.pi/extensions/durable-agents.ts --expect-output outputs/pi-home/settings.json --expect-output outputs/install-check.json
uv run --script scripts/summarize-pi-json-events.py evaluations/runs/pi-durable-pi-global-install-20261024-contract/events.jsonl --output evaluations/runs/pi-durable-pi-global-install-20261024-contract/read-surface.json --require-model gpt-5.6-sol --fail-on-invalid-json --fail-on-tool-error
```

All eight exact nonempty outputs were created and the skill payload remained
unchanged. The first installation attempt returned `pi: command not found` in
the harness's Bash environment. During recovery, the agent read an installed
global package manifest outside the isolated workspace. It subsequently found
the generated package's local Pi executable, installed the correct wrapper in
the disposable home, and verified it with `pi list`.

Strict evaluation therefore fails: one tool error and one forbidden external
read, with the requested model correctly observed and valid event JSON. The
failure classifications are an environment/PATH failure followed by a boundary
violation during recovery. The failure is retained as 0/1 for this scoped
strict cohort; it was not retried or replaced. The read surface otherwise
contains the prompt, skill entry point, focused console reference and generated
configuration/source files, with no acceptance fixtures or sibling skills.

Independent artifact inspection passes 11 checks: manifest hashes,
independence/test flags, byte-identical runtime sources, relative fixture
connection, exactly one wrapper registration, wrapper import resolution,
reported paths/fields, command namespace, isolated-home containment, an
evaluator-side `pi list`, and an evaluator-side `npm run check`. The latter
checks invoke the generated package's installed Pi and TypeScript directly;
they validate the artifacts without erasing the failed forward trace.

Raw events, the immutable-payload receipt, read-surface findings, generated
workspace and independent validation receipt remain under the ignored
`evaluations/runs/pi-durable-pi-global-install-20261024-contract/`. No runtime
change or broader skill completion is inferred from this environment failure.
The overall skill remains `validating`, preserving earlier cohorts and the
[console extension validation](pi-extension-20261024.md).
