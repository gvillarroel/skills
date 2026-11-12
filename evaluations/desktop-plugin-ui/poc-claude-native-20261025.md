# Executable Claude native plugin PoC

Date: October 25, 2026. This is the Claude Code / Claude Desktop Code track of
the user's executable plugin-PoC request. No ordinary Desktop Chat claim is
made. The original forward output is preserved unchanged.

## Frozen forward task and outcome

- Prompt: [desktop-plugin-ui-poc-claude-native.md](../pi-prompts/desktop-plugin-ui-poc-claude-native.md),
  SHA-256 `1df762094ea88a61a0b8db9feef79bcabf5d7db46bedf287b39c30a8c884d3f1`.
- Run: `evaluations/runs/20261025-plugin-poc-v1-claude-native-sol-1/`.
- Subject: 26-file runtime `desktop-plugin-ui`, SHA-256
  `ed3f7529ae344b2bf9c29dbb73c2e3a787c99ed1ce39bca769dc747588fb66d7`.
- Requested/observed model: `openai-codex/gpt-6.1-sol`, medium; existing
  recorded Spark account/provider exception. Pi 1.4.0, Windows.
- Native runtime: Claude Code **2.1.302**, no account/network/model needed
  for strict validation and native-engine tests.
- Strict forward outcome: **fail**, 391.312 seconds, Pi exit 0/harness exit 4.
  All seven exact outputs exist; copied skill integrity passes. Fourteen
  tool-error calls remain, including API discovery, malformed probes and
  failed patching/testing attempts. Invalid JSON and outside-skill reads are
  not the failure basis.
- Generated strict plugin validation passes, and its own **13/13** native
  tests pass. Independent engine tests pass only **2/9**. This is a genuine
  functional failure, not merely a strict-trace failure or absent host paint.

Reproduction, from the repository root:

```powershell
uv run --script scripts/run-pi-skill-eval.py desktop-plugin-ui --prompt-file evaluations/pi-prompts/desktop-plugin-ui-poc-claude-native.md --model openai-codex/gpt-6.1-sol --thinking medium --mode json --strict --run-id 20261025-plugin-poc-v1-claude-native-sol-1 --timeout-seconds 900 --expect-output poc/.claude-plugin/plugin.json --expect-output poc/hooks/hooks.json --expect-output poc/hooks/register.ts --expect-output poc/package.json --expect-output poc/tests/native.test.ts --expect-output poc/USAGE.md --expect-output poc/review.json
node projects/desktop-plugin-ui/scripts/verify-native-poc.ts evaluations/runs/20261025-plugin-poc-v1-claude-native-sol-1/workspace/poc v1-sol-1
```

Run IDs and evaluator labels are immutable; choose fresh ones for a new
attempt. The forward run copies only this skill and disables ambient context,
extensions, skill discovery, templates and themes. The task is offline, permits
only the installed CLI's help/validation/native tests, and forbids installed
package-source inspection and global installation.

## Observed defect and independent confirmation

The generated hook handled `command.run` with
`if (e.name !== 'release-review') return next(e)`. Its own tests dispatched
`$.command.run({ name: 'release-review', args: ... })`. Those two incorrect
assumptions agreed, so its own test suite passed. The actual native execution
event uses **`command`**, while **registration uses `name`**.

The independent suite dispatches `{ command: 'release-review', args: ... }`.
Registration and unrelated-pane pass-through pass; all seven public-command
and view tests fail with `no implementation for command.run` because the hook
passes every real invocation to the host fallback. This reproduces the bug in
the installed native engine.

A separate minimal diagnostic plugin registered `/contract-probe` and returned
the actual native event. An installed, signed-out, task-state-isolated headless
invocation returned `{ command: 'contract-probe', args: 'smoke', ... }`, with
zero turns, API milliseconds, inference cost and token usage. Raw receipt:
`projects/desktop-plugin-ui/artifacts/plugin-pocs/native-command-contract/stdout.json`.
This confirms the authoritative execution field without a model call.

A separate diagnostic copy changes only the hook guard to `e.command` and
the seven generated test invocations to `{ command: ... }`. The original
isolated output is unchanged. On that copy, strict validation, generated
13/13 tests and independent **9/9** native tests pass. The actual headless
`/release-review ready` returns exactly `R-71/R-73`, again with zero
turns/API milliseconds/cost. This is a diagnostic repair, not a recovered
forward pass or fresh-subject acceptance.

Evidence roots:

- Original evaluator: `projects/desktop-plugin-ui/artifacts/plugin-pocs/native-v1-sol-1/`.
- Diagnostic repaired source: `projects/desktop-plugin-ui/artifacts/plugin-pocs/diagnostic-command-field/poc/`.
- Repaired evaluator and direct-command receipt: `projects/desktop-plugin-ui/artifacts/plugin-pocs/native-diagnostic-command-field/`.

## Canonical repair

Added [native-authoring.md](../../skills/desktop-plugin-ui/references/native-authoring.md)
and the five-file runtime template
[claude-native](../../skills/desktop-plugin-ui/assets/templates/claude-native/).
The existing native-patterns reference routes new builds to this starter;
the parent linked the direct skill entrypoint route before freezing the combined
repair subject.

The reusable starter uses neutral `T-1/T-2/T-3` task data and a distinct
`task-view` command. It makes these contracts concrete:

- Literal `on("command.run", { command: "task-view" }, ...)` matching, separate
  from `$.command.register({ name: "task-view" })`.
- Authentic execution events in tests, plus a negative test showing that a
  registration-shaped `{ name }` event must not stand in for a real command.
- Correct native constructors, unwrapped placement results, event identity,
  denied/unplaced fallback, direct text routes and close/reopen behavior.
- Native test stubs registered before `$`, explicit session-start firing,
  `{ value }` API floors, and engine-owned invalidation rather than a no-op
  redraw stub.
- Relevant static-analysis rules: literal events, named hook arguments,
  visible `$` API paths, no namespace reflection/aliasing or arbitrary rest
  probes. These are learned from the retained generation failures.

The new reference is 6,430 bytes and has a contents section. It needs no
sibling skill, repository file, gallery, dependency, build tool or server.
It preserves the existing English, Nielsen and host-owned styling boundaries.

## Template checks

```powershell
claude plugin validate skills/desktop-plugin-ui/assets/templates/claude-native --strict --json
claude plugin test skills/desktop-plugin-ui/assets/templates/claude-native
node projects/desktop-plugin-ui/scripts/probe-native-command.ts skills/desktop-plugin-ui/assets/templates/claude-native "/task-view open" template-v1
```

All commands use artifact-local `CLAUDE_CONFIG_DIR`; the reusable probe removes
provider credentials from its child environment. Current results:

| Check | Result |
| --- | --- |
| Strict manifest/module validation | pass, no errors or warnings |
| Native template tests | **13/13**, including terminal/Desktop trees at 32/80 columns |
| Installed headless command | expected `T-1/T-3` open tasks, exit 0 |
| Inference receipt | zero turns, API ms, cost and tokens; empty model usage |
| Unrelated pane and command | preserve host fallbacks |
| Canonical template output hygiene | only the five authored runtime files; no generated types/logs |

An initial template test query by a noninteractive Text key returned undefined
on four cases. The template test was corrected to use the native supported
Text-content query, and unnecessary Text keys were removed. Prior source/test
files are retained under `template-development-v1/`; this deterministic
development correction is separate from the original frozen forward failure.
Current validation/test outputs are `template-validation.json` and
`template-tests.log`; the direct receipt is `headless-template-v1/stdout.json`
under `projects/desktop-plugin-ui/artifacts/plugin-pocs/`.

## Fresh generation from the repaired frozen skill

Run `20261025-plugin-poc-v3-claude-native-sol-1` uses the **identical frozen
prompt** and the same Sol 6.1/medium, strict runtime and 900-second budget.
The copied subject is the final 34-file runtime, SHA-256
`e005f79036bfe0ef156a1c7c64fceb113f5ee277f7a2217ff9fddd9e8d1f245d`.
The parent source/runtime/full audit at
`evaluations/runs/20261025-plugin-poc-v4-audit/report.json` matches this hash.
The `v3` forward ID and `v4` audit ID are separate evidence names for the
same frozen subject, not a source mutation during testing.

The new isolated generation passes **joint acceptance 1/1**. No generated
file was repaired by the evaluator and no further canonical edit or model
reroll was used. Its code uses a literal `{ command: "release-review" }`
matcher and authentic command execution events. The original `e.name`
functional defect is absent. Its negative registration-shaped event test
explicitly preserves the host fallback rather than faking a real execution.

| Check | Original 26-file subject | Fresh repaired 34-file subject |
| --- | --- | --- |
| Strict isolated harness | fail, 14 tool-error calls | **pass**, zero tool errors |
| Generated strict validation | pass | **pass**, no errors/warnings |
| Generated native tests | 13/13, but shared an incorrect event shape | **15/15**, authentic execution events |
| Independent native engine | 2/9; seven public-command/view failures | **9/9** |
| Actual installed headless direct command | Original not attempted after independent failure | **pass**, exact R-71/R-73 ready rows |
| Inference receipt | Separate diagnostic only | **zero turns, API ms, cost and tokens** |
| Copied skill integrity | pass | **pass**, unchanged e005 subject |
| Invalid event JSON | zero | **zero** |
| Observed forward tool calls | 92 | **29** |
| Harness duration | 391.312 seconds | **153.914 seconds** |

The call/time values describe these two samples; they do not establish a
statistical or model-wide performance guarantee. The fresh trace reads only
the task, target entrypoint, relevant native/design references, five runtime
template files and its own output/evidence. No acceptance gallery, sibling
skill, repository example or installed package source is read.

Manual review confirms the task's exact values, matching public/pane/control
identities, direct/help/invalid recovery, unwrapped denied/unplaced fallback,
native redraw, Cancel-only close, safe repeated activation/reopen, and
unrelated-pane pass-through. Native generated tests cover terminal/Desktop
at 32/80 columns and preserve unsupported VS Code rendering as host fallback.
The review counts two initial controls, zero required filtering decisions
(all rows appear immediately), one primary inspection task and zero added
runtime processes/dependencies. H1-H10 findings are concrete and explicitly
leave actual focus/accessibility/paint untested. This is heuristic and
implementation review, not representative-user evidence.

Reproduction with fresh IDs/output labels as needed:

```powershell
uv run --script scripts/run-pi-skill-eval.py desktop-plugin-ui --prompt-file evaluations/pi-prompts/desktop-plugin-ui-poc-claude-native.md --model openai-codex/gpt-6.1-sol --thinking medium --mode json --strict --run-id 20261025-plugin-poc-v3-claude-native-sol-1 --timeout-seconds 900 --expect-output poc/.claude-plugin/plugin.json --expect-output poc/hooks/hooks.json --expect-output poc/hooks/register.ts --expect-output poc/package.json --expect-output poc/tests/native.test.ts --expect-output poc/USAGE.md --expect-output poc/review.json
node projects/desktop-plugin-ui/scripts/verify-native-poc.ts evaluations/runs/20261025-plugin-poc-v3-claude-native-sol-1/workspace/poc v3-sol-1-validator-v2
uv run --script scripts/summarize-pi-json-events.py evaluations/runs/20261025-plugin-poc-v3-claude-native-sol-1/events.jsonl --require-model gpt-6.1-sol --fail-on-invalid-json --fail-on-tool-error --require-tool-call --output evaluations/runs/20261025-plugin-poc-v3-claude-native-sol-1/read-surface.json
```

Retain one evaluator correction separately: the first metadata check assumed
`review.heuristics` was an array and failed on the generated, valid keyed
H1-H10 object. The prompt did not prescribe one serialization. All nine
independent engine tests and the actual headless command already passed on
that first application. The initial result and evaluator source remain in
`projects/desktop-plugin-ui/artifacts/plugin-pocs/native-v3-sol-1/`.
The evaluator now accepts both faithful representations, checks the same
ten IDs/findings, and reruns the **same unchanged artifacts** under
`native-v3-sol-1-validator-v2/`: all **14/14** artifact/package/behavior
checks pass, with a separate observed-working headless receipt. Classification
of the initial false failure is `validator`; no skill or model reroll fixes it.

## Evidence limits

The native engine executes real hooks and validates native trees, but does not
paint a terminal/Desktop interface. Stubbed placement/close dispatch does not
prove actual placement, keyboard behavior, focus, accessibility or dismissal.
The direct headless command proves that installed native dispatch works for
that command, not interactive paint. No account authentication, model inference,
global installation or ordinary Desktop Chat interaction was performed.
The fresh scoped generation above is separate from the failed original
subject and diagnostic copy. It establishes this contract case, not every
possible native plugin or an all-host/user-study release certification.
