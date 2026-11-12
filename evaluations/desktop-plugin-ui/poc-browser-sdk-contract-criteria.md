# Focused MCP App browser/SDK contract criteria

Frozen October 25, 2026, after diagnosing a pinned declaration-resolution issue
and before any forward output for this contract. This tests the repaired
browser-fixture workflow; it is separate from the full Desktop PoC cohorts.
Use one strict runtime contract attempt with exact expected paths, observed
Sol 6.1 medium under the recorded Spark exception, and a 900-second budget.
Do not pool its result into a complete full-plugin release pass.

Preflight task-design correction before the first forward run: align the
compiler/type pins with the actual read-only diagnostic environment,
TypeScript 5.9.3 and @types/node 24.10.1. The initially drafted 7.0.2/24.10.0
pins were not the diagnosed installation and were never forward-tested in this
contract. No claim of a TypeScript 7 lifecycle result is made. Other package
pins, behavior, exact outputs, model, budget and acceptance rules are unchanged.

## Required acceptance

- Every prompt-named artifact is nonempty; the skill payload is unchanged and
  the strict trace has the expected model, valid event JSON, no tool errors and
  an authorized read/write surface. Package metadata and type declarations
  installed by the agent inside its workspace are expressly allowed here.
- Actual package versions match the pins. Both TypeScript configurations compile
  real code using the real SDK. No fake App class, ambient widening, `any` or
  `unknown` API cast, unchecked optional-close workaround, or disabled typecheck
  can establish the lifecycle proof. Inspect source and run the typecheck again.
- The built HTML is self-contained. The actual delivered SDK performs the
  standard initialize/initialized/tool-result sequence through a sandboxed host
  fixture. No custom `window.openai`, SDK replacement or app-realm helper hides
  serialization problems. A new server, account or service is unnecessary.
- Independently run the browser sequence and check exact inventory IDs/counts,
  one direct dispatch per Enter or Space activation, real busy/duplicate guard,
  last-result preservation and successful Retry. Disconnect executes genuine
  `App.close()`, disables load and prevents late host data from being accepted.
- Missing/denied initialization has visible recovery feedback. Inspect actual
  English accessible names, focus and contrast, width320/900 overflow and
  screenshots. Capture tool dispatches; no model-message/sampling request may
  occur. Browser profiles/caches/temp must be task-local before launch.
- Source, compiler, browser fixture and real-host/user-study evidence remain
  distinct. Both live flags stay false; concise H1-H10 findings name real states.

## Grounding and error classification

Read-only diagnostic with actual MCP Apps1.7.5 showed NodeNext producing TS2339
for `App.close`, while ESNext/Bundler compiled the identical typed source and
the actual runtime inherited close method resolved. Primary pinned app source
uses `this.close()` during failed connect cleanup; it is not an unsupported API.
Do not teach a cast or false product exclusion as the repair. Raw diagnostic is
under ignored project artifacts and is not supplied as a hidden forward input.

Retain failed attempts. Separate agent code/test workflow errors, API/config
guidance problems, grader mistakes and browser/package infrastructure failures.
Correct artifacts do not erase strict trace errors. If the contract reveals a
new failure, record it before any source repair and freeze a fresh subject.
