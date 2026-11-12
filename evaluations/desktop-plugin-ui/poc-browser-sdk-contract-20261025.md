# Focused MCP App SDK/browser contract, October 25, 2026

The final generated fixture passes independent compiler, SDK lifecycle and real
browser verification. The isolated forward run remains a **strict failure**
because it encountered two tool errors before repairing its own output. This
contract validates the final browser recipe on a fresh subject; it is separate
from complete plugin generation and installed assistant acceptance.

## Frozen task and subject

- Prompt: [browser SDK contract](../pi-prompts/desktop-plugin-ui-poc-browser-sdk-contract.md).
- Acceptance: [frozen contract criteria](poc-browser-sdk-contract-criteria.md).
- Run: `20261025-plugin-poc-v5-browser-sdk-sol-1`, one attempt, no reroll.
- Skill: runtime profile, 37 files, SHA-256
  `0b5d593f560a76a07c7b2775c40f4ca0f0adc99770859e13ad99542926abe4ae`.
- Prompt SHA-256:
  `c90d4a197ccfd3fc5f50da384cedfc4fd72aa9c8992efbdca5fb02b466b3e8e1`.
- Model: observed `openai-codex/gpt-6.1-sol`, medium, strict JSON, 900-second
  limit under the recorded model exception; actual duration 290.736 seconds.
- Started 22:10:57 UTC; finished 22:15:48 UTC. Pi exited zero, harness returned
  four, with artifacts and skill integrity passing and events failing.

Before the first forward run, the task pins were corrected to the diagnosed
TypeScript 5.9.3 and @types/node 24.10.1 installation. The initial drafted
TypeScript 7 pins were never forward-tested. Other exact pins are MCP Apps
1.7.5, MCP SDK 1.32.2, Playwright 1.64.1 and esbuild 0.28.2. Independent inspection
confirmed all six actual installed versions.

All ten exact required paths exist in the run workspace:
`fixture/package.json`, `fixture/package-lock.json`,
`fixture/tsconfig.app.json`, `fixture/tsconfig.tests.json`,
`fixture/src/app.ts`, `fixture/ui/index.html`, `fixture/dist/ui.html`,
`fixture/tests/browser.ts`, `fixture/results.json` and `fixture/USAGE.md`.
Supporting build code, retained attempts and screenshots are also present.

## Results and retained failures

| Layer | Result | Evidence |
| --- | --- | --- |
| Strict isolated generation | fail: two tool errors; valid events, expected model, no skill mutation | run `evaluation-result.json`, `event-check.json` and immutable `events.jsonl` |
| Exact required artifacts | 10/10 present | run `artifact-check.json` |
| Independent compiler, SDK and browser | 31/31 pass | project `browser-sdk-v5-independent/independent-review.json` |
| Delivered fixture replay in separate copy | typecheck, build and browser exit zero; 18/18 browser checks | project `browser-sdk-v5-replay/replay-review.json` and logs |
| Evaluator positive/negative selftests | 2/2 pass; fake close rejected | project `browser-sdk-verifier-selftests/20261025-v3-action-state/result.json` |
| Manual rendered inspection | pass at 320/900 pixels and initialization error | independent screenshot paths below |
| Joint strict acceptance | fail | working final output does not erase generation errors |

The two forward errors are ordinary code/test workflow findings, retained at
event lines 7084 and 7372:

1. The first real browser check measured disabled text at 4.439444354179187:1.
   The generator changed it to a darker declared ColorSet 1 text token and
   retained `results-attempt1.json`.
2. The Space test assumed that focus survived disabling the primary button
   during the previous request. Actual browser focus was inactive. The
   generator changed its test to re-enter through real Tab navigation and
   retained `results-attempt2.json`.

Both final fixes were made by the isolated generator during its one run. The
evaluator did not patch its source, bundle, test, results or original images.
These are not SDK incompatibility or browser installation failures. No new
canonical skill repair or another full plugin regeneration was performed.

## Independent lifecycle and browser proof

The app configuration uses ESNext/Bundler resolution with DOM and DOM.Iterable;
the separate Node/test configuration includes Node types. Both original
configurations compile under the pinned compiler without API casts. The
independent TypeScript checker resolves the actual `App` receiver and genuine
declarations for all three calls:

| Source call | Resolved declaration |
| --- | --- |
| `app.connect()` | MCP Apps `dist/src/app.d.ts` |
| `app.callServerTool(params, options)` | MCP Apps `dist/src/app.d.ts` |
| `app.close()` | inherited MCP SDK `dist/esm/shared/protocol.d.ts` |

A real installed SDK App instance exposes `close` and its promise resolves.
This confirms the earlier NodeNext declaration-resolution diagnosis; it does
not replace the API with a stub or treat the genuine inherited method as absent.
The primary pinned source also uses `this.close()` during failed connection
cleanup: [MCP Apps 1.7.5 app source](https://raw.githubusercontent.com/modelcontextprotocol/ext-apps/v1.7.5/src/app.ts).

The evaluator renders the exact delivered HTML in an iframe with only
`sandbox="allow-scripts"`. The real SDK performs initialization and receives
opening tool data through the standard bridge. No fabricated host object or
app-realm evaluation helper establishes the result. Checks independently cover:

- Zero-count opening; exact ready records `A-1` and `A-3`, with count two.
- Real Tab/Enter and Space activation, one direct call per activation, and
  held-response busy feedback with duplicate prevention.
- Error retaining the last authoritative data and successful Retry, with no
  model-message or sampling request.
- Genuine Disconnect, disabled loading and rejection of late result data.
- Visible initialization-failure recovery guidance; English accessible names.
- Actual layout and keyboard focus at 320 and 900 pixels, no horizontal
  overflow, no unexpected network requests or page errors.

The delivered browser test was also repeated in a fresh diagnostic copy. Its
18 checks pass, including both tool-level and JSON-RPC failure/Retry paths,
pointer activation, hover, busy, disconnected and initialization-error contrast.
It observes nine direct tool requests and zero model requests. The rebuild is
byte-identical to the original HTML, SHA-256
`16870a156f1a115853efef6caf6218ce031f95b5baba491ebbf10638069999d3`.

Actual browser: installed Microsoft Edge 156.0.4314.42, headless; Node 24.18.0.
The independent evaluator sets task-local TMP/TEMP/TMPDIR before SDK/Playwright
imports and observes both profile and artifact directories inside its `tmp/`.
The replay starts with the same task-local environment. The independent rendered
text minimum is 5.489814557409947:1; keyboard focus is 10.918238644424665:1 at both
widths. The delivered test independently confirms the same text minimum in
busy, error, hover, disconnected and initialization-error states.

Manually inspected independent images under
`projects/desktop-plugin-ui/artifacts/plugin-pocs/browser-sdk-v5-independent/`:

- `inventory-900.png`: correct two rows, visible action and keyboard focus.
- `inventory-320.png`: readable wrapped help, vertically arranged controls,
  correct data and no clipping or overflow.
- `initialization-failure.png`: visible failure and reload guidance, zero
  opening count, visibly disabled actions and retained layout.

The generated results contain H1–H10 findings linked to actual states and
test methods. This is a synthetic browser/SDK fixture. No assistant installation,
permission flow, production server tool visibility, real host paint or
representative user study is established. Both `host_acceptance_verified` and
`user_testing_performed` remain false.

## Evaluator calibration and reproducibility

The reusable independent checker is
[verify-browser-sdk-contract.ts](../../projects/desktop-plugin-ui/scripts/verify-browser-sdk-contract.ts).
Its [selftest](../../projects/desktop-plugin-ui/scripts/test-browser-sdk-contract.ts)
checks a valid actual SDK component and a deceptive close replacement. The
replacement can display a disconnected state, but the checker rejects it at
`genuine-typed-sdk-call:close` because the call does not resolve to the genuine
SDK declaration. No implementation mirrored assertion establishes close.

Before evaluating the generated output, evaluator calibration corrected a
focus-measurement false positive: real Tab/Shift+Tab establishes keyboard focus
before measuring `:focus-visible`. A later selector correction follows the
initial accessible primary button's actual identity while its legal label
changes between Load ready, Loading and Retry. It does not require extra
controls or weaken activation/state checks. Earlier selftest records remain in
separate ignored artifact directories.

Reproduce against the untouched fixture, using a fresh output directory:

```powershell
node projects/desktop-plugin-ui/scripts/verify-browser-sdk-contract.ts evaluations/runs/20261025-plugin-poc-v5-browser-sdk-sol-1/workspace/fixture projects/desktop-plugin-ui/artifacts/plugin-pocs/browser-sdk-v5-independent-fresh
node projects/desktop-plugin-ui/scripts/test-browser-sdk-contract.ts fresh-contract-selftest
uv run --script scripts/summarize-pi-json-events.py evaluations/runs/20261025-plugin-poc-v5-browser-sdk-sol-1/events.jsonl --require-model gpt-6.1-sol --fail-on-invalid-json --fail-on-tool-error
```

The final command intentionally fails on the two retained forward errors.
Full Desktop PoC results and archive identities remain in
[the separate Desktop report](poc-mcp-desktop-20261025.md). The final five-host
source collection should keep the V3 complete Desktop artifacts; this focused
fixture is additional recipe evidence and does not overwrite those sources.

Final collection integrity was checked independently: the two runtime archives
under `packages/poc-20261025-v1/` match the original V3 hashes in the Desktop
report exactly. All ten original focused outputs still match the harness's
recorded hashes after independent testing. Machine-readable receipts are
`browser-sdk-v5-independent/final-integrity-review.json` and
`browser-sdk-v5-independent/manual-review.json` under the project artifact root.
