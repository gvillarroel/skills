# Native Pi console extension validation, 2026-10-24

## Subject and scope

The `pi-durable` skill now generates an independent Pi Coding Agent console for
existing Durable services. The canonical resources are its
`references/pi-extension.md`, `scripts/scaffold-pi-extension.py`, seven runtime
template files, and two optional acceptance-test sources. The working local
console is `projects/pi-agent-services/pi-extension/`; `.pi/extensions/` loads it
for this project. No global Pi account or settings were modified.

Frozen runtime: 48 files, SHA-256
`a2122969fca385bcdf959fca161139a5d70ba0c5a4f79458d7ce8288fdf49c31`.
Full bundle: 59 files, SHA-256
`527a04072bafcd046e8b135b109e9ac08d1788e75c0b213f5a68fc2e3bd7a1a4`.
The console pins Pi Coding Agent/TUI 0.84.2, uses Node 24+, and connects to the
bundled service HTTP API. Pi Durable 1.3.0 is the service's distinct runtime.

## Deterministic and native checks

- `npm run check` and `npm test` in the project extension pass: 34/34 tests,
  comprising 19 client/configuration and 15 command/tool cases. The generated
  full extension independently passes the same checks.
- Twelve scaffolder checks pass: invalid hosts, ports and booleans, empty state,
  credential fields, invalid service ID, destinations inside the skill or
  nonempty destinations, runtime payload without fixtures, and portable
  configuration/file hashes.
- Installed Pi 0.84.2 loads the actual TypeScript entry, the project discovery
  loader, and the adjacent-config fallback from a different working directory.
  Native RPC checks cover registration, help, list, services, status, jobs,
  public history, and chooser cancellation.
- Read-only commands and chooser cancellation cause zero outer model turns,
  zero remote generations and no service mutation. Custom console entries
  display without appearing in `get_messages` or the outer model context.
- Explicit live checks send one message through the interactive agent selector
  to `repo-quality` and one through a one-shot command to `delivery-watch`.
  Both return `EXTENSION_READY`. Fresh service evidence identifies
  `openai-codex/gpt-6.1-sol`, one generation per agent and zero tool calls.
  The outer Pi remains offline. Provider counters move from 3/1 to 4/2 and
  remain unchanged by later read-only checks.
- Requests reread local bearer state, reject redirects and non-loopback
  endpoints, bound time/size, and preserve request/submission IDs on ambiguous
  admission or interrupted waits. Local cancellation and explicit remote abort
  have separate tested behavior. Surplus positional arguments, including an
  accidental unflagged abort job ID, fail before a remote operation.

The deterministic tests use fake transports and UI contexts; real native RPC
and live provider checks are separate evidence. Raw traces, token-bearing state,
Pi homes and generated workspaces remain ignored in project artifacts.

## Isolated skill-only contract

One frozen contract attempt passes strict execution, exact nonempty output,
read-surface and immutable payload gates. There was no reroll. It uses the
existing `openai-codex/gpt-5.6-sol` forward-model exception after the earlier
Spark provider rejection; the operating agents separately use requested Sol
6.1. This case tests offline generation and type checking, not backend behavior.

```powershell
uv run --script scripts/run-pi-skill-eval.py pi-durable --prompt-file evaluations/pi-prompts/pi-durable-pi-console-contract.md --model openai-codex/gpt-5.6-sol --mode json --strict --run-id pi-durable-pi-console-20261024-contract --expect-output fixtures/service/config.json --expect-output outputs/pi-console/extension.ts --expect-output outputs/pi-console/src/client.ts --expect-output outputs/pi-console/durable-agents.json --expect-output outputs/pi-console/scaffold-manifest.json --expect-output outputs/console-check.json
uv run --script scripts/summarize-pi-json-events.py evaluations/runs/pi-durable-pi-console-20261024-contract/events.jsonl --require-model gpt-5.6-sol --fail-on-invalid-json --fail-on-tool-error
```

The agent reads only the task prompt, skill entry point, console reference and
its generated connection/manifest. It runs the bundled scaffolder and
`npm ci --ignore-scripts --no-audit --no-fund` followed by TypeScript checking.
Acceptance fixtures are correctly absent from the runtime payload and
`testsIncluded` is false. It does not invent test results or start a backend.
Independent review verifies the relative `lab` connection, manifest hashes,
copied runtime sources, command examples and cancellation semantics; an
evaluator rerun of `npm run check` also passes.

Run receipts remain under
`evaluations/runs/pi-durable-pi-console-20261024-contract/`. Native receipts are
under `projects/pi-agent-services/artifacts/pi-extension-validation/`; generator
and frozen bundle receipts are under the adjacent `pi-extension-release/`.
The [project validation record](../../projects/pi-agent-services/extension-validation.md)
and [console guide](../../projects/pi-agent-services/pi-extension/README.md)
describe operation and evidence boundaries.

## Release gates and limits

The repository pattern-ID (1,348 IDs), skill, independence and payload
validators pass. The Pages build succeeds with 1,180 files, 127.66 MiB; its
existing third-party build warnings do not fail the build. Diff checking and
local skill synchronization are also checked before publication.
The console client manages configured services; it does not scan arbitrary
processes, deploy/start services, or initiate evolution. Windows native runtime
and real Sol 6.1 communication are verified. Native macOS UI loading is
unverified. Task IDs currently have no spaces; the parser is not a full shell.

This scoped contract is 1/1. It does not replace earlier broader naturalistic
service-authoring failures (0/3), so the overall skill remains `validating`.
Earlier service/evolution/provider cohorts and their retained failures stay in
the [local pilots record](local-pilots-20261024.md) and
[evolution record](evolution-20261024.md).
