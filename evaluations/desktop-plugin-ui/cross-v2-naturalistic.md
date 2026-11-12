# Cross-assistant naturalistic evaluation, frozen v2

Date: 2026-10-24 (America/New_York; UTC logs dated 2026-10-25). Skill:
`desktop-plugin-ui`. Model: recorded exception
`openai-codex/gpt-5.6-luna`, high thinking, Pi 1.4.0. No skill edits were made
by this evaluator. The task prompt and independent grader are unchanged from
[v1](cross-v1-naturalistic.md), whose two historical-label contract failures
remain retained and are not substituted by these results.

Frozen runtime payload SHA-256:
`455db7f6daee26026e3c3be314406baf2f19a9e3c31c2250f09fc4d978389c05`.
All three manifests record this same 15-file runtime payload. Prompt SHA-256:
`4b2f770266448125b47ac76a40bd42f730f170ebff7205ddf4d4752df1df41b4`.

## Outcome

**3/3 passed** the strict harness, unchanged independent artifact inspector,
and direct semantic review of both outputs. This satisfies the two-of-three
naturalistic threshold. Each fresh workspace contains the exact nonempty
`proposal/support-queue.md` and `proposal/host-decisions.json`; each JSON has
all five host IDs and both required task-level booleans set to false. Historical
records now retain the canonical observed evidence labels with named versions,
surfaces, outcomes, and evidence layers.

| Run suffix after `20261024-desktop-ui-cross-v2-` | Strict | Independent | Manual | Canonical IDs | Duration |
| --- | --- | --- | --- | --- | --- |
| `naturalistic-luna-1` | Pass | Pass | Pass | 17 | 69.561 s |
| `naturalistic-luna-2` | Pass | Pass | Pass | 27 | 77.693 s |
| `naturalistic-luna-3` | Pass | Pass | Pass | 25 | 72.806 s |

No timeout, tool error, malformed event, wrong artifact path, unknown pattern,
source-check finding, payload mutation, or unexpected external command was
found. Every agent ran the copied source checker after its final writes and
inspected its passed result. The independent inspector reran that checker
with `--fail-on-findings` on both outputs in all three workspaces.

## Reproduction

Three independent processes used the following command with run-number
suffixes 1, 2, and 3:

```powershell
uv run --script scripts/run-pi-skill-eval.py desktop-plugin-ui --prompt-file evaluations/pi-prompts/desktop-plugin-ui-cross-naturalistic.md --model openai-codex/gpt-5.6-luna --mode json --strict --timeout-seconds 600 --run-id 20261024-desktop-ui-cross-v2-naturalistic-luna-1 --expect-output proposal/support-queue.md --expect-output proposal/host-decisions.json --expect-output-json-field 'proposal/host-decisions.json::host_acceptance_verified=false' --expect-output-json-field 'proposal/host-decisions.json::task_empirical_tests_performed=false'
```

Each trace received a separate required-model summary; vary the run suffix:

```powershell
uv run --script scripts/summarize-pi-json-events.py evaluations/runs/20261024-desktop-ui-cross-v2-naturalistic-luna-1/events.jsonl --output evaluations/runs/20261024-desktop-ui-cross-v2-naturalistic-luna-1/trace-summary.json --require-model gpt-5.6-luna --require-tool-call --fail-on-invalid-json --fail-on-tool-error --require-read ../prompt.md --forbid-read-regex '(?i)(^|[\\/])assets[\\/]examples([\\/]|$)' --forbid-read-regex '(?i)^skills[\\/](?!desktop-plugin-ui([\\/]|$))'
uv run --script evaluations/desktop-plugin-ui/inspect_cross_runs.py --prefix 20261024-desktop-ui-cross-v2-naturalistic-luna- --output evaluations/runs/20261024-desktop-ui-cross-v2-naturalistic-inspection.json
```

All summaries observed only `openai-codex/gpt-5.6-luna`. Repetition 1 read the
prompt, skill, matrix, host references, and implementation references needed
for its selection (12 read calls); repetitions 2 and 3 read the full focused
cross-host reference set (14 each). This is a five-product request. No read
used acceptance examples, sibling skills, repository documentation, project
artifacts, or external state. Commands only ran local source/JSON checks;
repetition 1 also asserted the requested host IDs and JSON keys with Python.
There was no task-level provider invocation, install, configuration mutation,
network command, or application/account operation.

| Repetition | Input | Output | Cache-read | Trace token total |
| --- | --- | --- | --- | --- |
| 1 | 36,308 | 8,524 | 109,952 | 154,784 |
| 2 | 36,660 | 10,360 | 146,048 | 193,068 |
| 3 | 39,321 | 9,272 | 120,192 | 168,785 |

These are Pi trace aggregates for the OpenAI evaluation, not Claude/Copilot
allowance usage. Each process used an independent workspace and exactly the
copied read-only skill bundle.

## Direct artifact review

All six artifacts were read after completion. Each recommendation addresses
the requested queue search, selected ticket, editable priority, chart, CSV,
and explicit explanation action. They share server-authoritative records,
schemas, stable IDs, versioned edits, meaningful text/structured fallback,
and presentation-state/error rules. They preserve the prior queue on failed
refresh and distinguish draft/cancel from committed data. They recommend
local protocol/native/direct-control checks before scarce model work.

The proposals correctly keep these boundaries:

- Claude Desktop ordinary Chat's historical local stdio iframe paint,
  app-only action, error retention, and fullscreen differ from native Mods,
  remote acceptance, host elicitation, optional capabilities, and OS delivery.
- Claude Code terminal uses native controls and terminal-specific Image/Raster
  or text fallbacks; its SVG/HTML refusal and native engine success do not
  become actual terminal-pixel claims.
- Codex transport, resource metadata, HTML bytes, and elicitation callbacks
  stay at their measured backend layer. `never` versus `on-request` matters;
  a custom renderer is an owned frontend, not an injected stock app panel.
- ChatGPT's shared MCP Apps route, reachable HTTPS or authorized tunnel,
  optional extensions, state lifetimes, and policy/consent checks are separate.
  Setup consent and synthetic fixtures do not establish signed-in widget paint.
- Copilot CLI forms, VS Code inline MCP Apps, and separately installed
  extension webviews are separate surfaces. Drafted follow-up text is not a
  submitted assistant turn, and webview success is not Copilot Chat paint.

All products receive exact bundled primary-source URLs. Historical successes
and failures are retained under `historical_observations` with observed labels;
neither task-level boolean is inflated by past evidence. No blocking factual
overclaim, blanket product exclusion, invented host test, unsupported API, or
promotion of lower-layer evidence to stock assistant paint was found.

## Metadata-only routing control

The unchanged cross-assistant description separately passed **10/10** routing
decisions: five named-product positives, two ambiguity/evidence-mechanism
positives, and three unrelated negatives. Command:

```powershell
uv run --script evaluations/desktop-plugin-ui/cross-routing-control.py
```

The runner only streamed the skill frontmatter into the prompt and supplied
no body or `--skill` argument. The trace contains exactly one prompt read and
one output write, no commands, valid JSON, no tool errors, and only the required
Luna model. Metadata SHA-256:
`bcc1e483c6d80fa6c4c28831e00289fdeb4685422514042086d7e8f766c1baf2`.
It is a metadata applicability control, not proof of automatic product routing.
Prompt and runner are `cross-routing-prompt.md` and
`cross-routing-control.py`; raw result and required-model trace summary remain
under `evaluations/runs/20261024-desktop-ui-cross-routing-luna-1/`.

## Retained records

All three raw naturalistic runs, exact outputs, copied payloads, hashes,
manifests, checks, and required-model trace summaries remain under
`evaluations/runs/20261024-desktop-ui-cross-v2-naturalistic-luna-{1,2,3}/`.
The aggregate inspection is
`evaluations/runs/20261024-desktop-ui-cross-v2-naturalistic-inspection.json`.
The earlier v1 failures remain under their original paths and documented in
[cross-v1-naturalistic.md](cross-v1-naturalistic.md).
