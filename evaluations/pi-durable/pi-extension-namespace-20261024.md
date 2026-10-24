# Durable console namespace correction, 2026-10-24

The native Pi extension now registers only `/durable` and `/durable-chat`.
Generic `/agents` and `/agent` names remain available to the host harness;
there are no compatibility aliases. Help, errors, current documentation,
generated skill templates and acceptance tests use the Durable namespace.
The existing `durable_agents` model tool and `/v1/agents` service API already
have their own namespaces and are unchanged.

Frozen runtime: 48 files, SHA-256
`f5597c3e5e79fa12e85adac61cb120049fae08e29ccee3b65f4b024c4e9889b8`.
Full bundle: 59 files, SHA-256
`54e0b5282740b49196769dbcdefb7186aa0f1d30e1a096eae6a11bc28f39b25b`.

## Regression evidence

- `npm run check` and all 34 extension tests pass. The registration test asserts
  the exact command set and explicitly rejects generic agent aliases.
- Actual installed Pi 0.84.2 loads the project extension with a disposable Pi
  home. `get_commands` returns `durable` and `durable-chat`, with neither
  generic alias. Help, list, services, status, jobs, public history, traces and
  cancelled chat selection pass.
- Native read-only checks have zero outer model/tool events, empty outer
  message history, valid JSONL and no stderr. Provider counters remain 4/2;
  budgets, jobs and control conversations are unchanged. Both operating agents
  still use `gpt-6.1-sol`; no new remote messages were submitted for this rename.
- Repository pattern-ID (1,348), skill, independence and payload gates pass.
  Diff checking and local synchronization are also checked before handoff.

Native evidence remains ignored under
`projects/pi-agent-services/artifacts/pi-extension-namespace/`, including
`native-rpc-report.json`, the executable probe, raw events and read-surface
summary. The original [console cohort](pi-extension-20261024.md) retains the
earlier command names and real live-message evidence; it is historical.

## Frozen skill-only contract

One new attempt passes strict execution, exact artifacts, clean read surface
and unchanged payload gates. Independent review checks exact registrations,
command examples, file hashes, copied template and report semantics. An
evaluator rerun of TypeScript checking passes. Runtime fixtures correctly omit
acceptance tests. The report's `genericAgentCommandsReserved: true` means the
generic names are left reserved for the harness; actual registrations prove
the extension does not claim them.

```powershell
uv run --script scripts/run-pi-skill-eval.py pi-durable --prompt-file evaluations/pi-prompts/pi-durable-pi-console-namespace-contract.md --model openai-codex/gpt-5.6-sol --mode json --strict --run-id pi-durable-pi-console-namespace-20261024-contract --expect-output fixtures/service/config.json --expect-output outputs/pi-console/extension.ts --expect-output outputs/pi-console/src/client.ts --expect-output outputs/pi-console/durable-agents.json --expect-output outputs/pi-console/scaffold-manifest.json --expect-output outputs/console-check.json
uv run --script scripts/summarize-pi-json-events.py evaluations/runs/pi-durable-pi-console-namespace-20261024-contract/events.jsonl --require-model gpt-5.6-sol --fail-on-invalid-json --fail-on-tool-error
```

Run receipts remain under the matching ignored `evaluations/runs/` directory.
This uses the recorded Sol 5.6 evaluation exception after Spark rejection,
separately from operating agents on requested Sol 6.1. It is one scoped
contract (1/1), not a reroll or replacement for earlier service-authoring
naturalistic failures (0/3). Overall skill status remains `validating`.
Native Windows is verified; native macOS loading remains unverified.
