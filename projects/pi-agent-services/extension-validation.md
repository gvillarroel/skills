# Native Pi extension validation, 2026-10-24

The current terminal chat uses a persistent conversation panel; its independent
tests and actual Pi 0.84.2/1.4.0 Windows captures are recorded in the
[chat UI evaluation](../../evaluations/pi-durable/pi-chat-ui-20261024.md).
The original live communication cohort below remains historical evidence.

Command namespace update: the current extension exposes `/durable` and
`/durable-chat`, with no `/agents` or `/agent` aliases. The checks below retain
the initial command names used in those original live communication receipts.
The [namespace regression record](../../evaluations/pi-durable/pi-extension-namespace-20261024.md)
covers the renamed registrations and fresh read-only native checks; the service
API and agent conversations did not change.

The extension is implemented under `pi-extension/` with a standalone HTTP client
and package. The project loader `.pi/extensions/durable-agents.ts` provides
normal Pi discovery; `.pi/durable-agents.json` points to the active independent
service config. No global account directory or settings were modified.

## Deterministic checks

`npm run check` passes against Pi Coding Agent/TUI 0.84.2 declarations.
`npm test` passes 34/34 tests: 19 HTTP/configuration cases and 15 native-command
and tool behavior cases. They cover multi-service targets, token rotation,
loopback/redirect limits, size/time bounds, stable admission retry, admitted
receipt retention, local cancellation versus explicit remote abort, public-only
history, user input preservation and credential-safe errors. Surplus positional
arguments are rejected before an operation, including accidental unflagged job
IDs on abort; task selection requires `--job ID`.

## Actual Pi runtime

Installed Pi 0.84.2 loaded the TypeScript extension through its real RPC runtime
with an isolated Pi home under the project artifact directory. Read-only help,
list, services, status, jobs and history worked; cancelling the chooser admitted
nothing. There were zero outer model events, valid LF-delimited JSON, no stderr,
and no console/reply cards in `get_messages`. Remote provider counters were
unchanged by read-only operations.

Two explicitly authorized live checks succeeded:

- Interactive `/agent`: select `local/repo-quality`, send one message through
  its editor, receive `EXTENSION_READY`, and cancel the next editor.
- One-shot `/agent local/delivery-watch ...`: receive `EXTENSION_READY`.

Independent fresh service evidence confirms `openai-codex/gpt-6.1-sol`, one
remote generation per agent and zero tool calls. The outer Pi session remained
offline with zero model turns. The service/configuration was not changed.
Provider counters moved from quality 3/delivery 1 to quality 4/delivery 2.

Raw RPC traces, local Pi homes, connection fixtures and reports remain ignored
under `artifacts/pi-extension-validation/`. Key reports are
`native-rpc-report.json` and `live-native-rpc-report.json`.

## Scope

The extension does not start, install, stop, evolve or reconfigure services.
It lists configured registries rather than scanning arbitrary machine ports.
Bare agent IDs must be unique; qualified targets remove ambiguity. Cancelling
an extension wait preserves remote work; abort is an explicit operation.
Native Windows Pi behavior and both actual remote agents were tested. Native
macOS loading remains unverified. Service job IDs currently contain no spaces;
the command parser is not a general shell parser.
