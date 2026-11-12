Build a small executable browser/SDK acceptance fixture for a local MCP App.
This is a focused SDK and browser contract, not another full plugin/server.
The development environment has Node 24 and installed Microsoft Edge available.

Use real locked packages: @modelcontextprotocol/ext-apps 1.7.5,
@modelcontextprotocol/sdk 1.32.2, TypeScript 5.9.3, @types/node 24.10.1,
Playwright 1.64.1 and esbuild 0.28.2. The browser App must instantiate the real
SDK class and directly call its genuine typed `connect()`,
`callServerTool(params, options)` and inherited `close()` methods. Do not
replace those APIs with stubs, widen the SDK through ambient declarations,
use `any`/`unknown` casts to hide an API error, or skip type checking. Choose
separate compilation settings suited to browser code and Node browser tests.
Use ordinary .ts build/test files run with Node 24 native TypeScript support.

The component shows Inventory Review, a status, the authoritative item count
and a native Load ready button. It initializes with a count of zero. The
button calls app-only `inventory_ready` with `{ scope: "ready" }` and renders
the returned `{ count: 2, items: [{ id: "A-1", state: "ready" },
{ id: "A-3", state: "ready" }] }`. It runs deterministically without a model
message. Show real busy state, prevent duplicate dispatch, retain the last
result on a failed call and allow Retry. A native Disconnect button invokes
the actual SDK `close()` and leaves a clear disconnected status with the load
action disabled. A late host result after disconnect must not change the data.
Register SDK result handlers before initialization. Use default SDK host
detection; do not force a product-specific transport.

Build one self-contained `dist/ui.html`. The evaluator host in tests must load
that exact HTML in a `sandbox="allow-scripts"` iframe, perform the real standard
MCP Apps initialization handshake, deliver the opening tool result, and answer
the actual SDK tool calls with synthetic data. No real MCP server is needed.
Do not fabricate `window.openai`, replace the App SDK or inject transpiler
helpers into the app. Exercise actual Tab, Enter and Space, native primary
activation in the sandbox, busy/duplicate behavior, failure/Retry, disconnect,
late-result handling and visible initialization failure. Count direct tool
dispatches and reject model-message or sampling requests. Use English accessible
labels, ColorSet 1 defaults, visible focus and readable 320px/900px layouts.
Check actual rendered text/focus contrast and inspect screenshots.

Deliver exactly these required paths, plus necessary small supporting files:

- `fixture/package.json`, `fixture/package-lock.json`
- `fixture/tsconfig.app.json`, `fixture/tsconfig.tests.json`
- `fixture/src/app.ts`, `fixture/ui/index.html`, `fixture/dist/ui.html`
- `fixture/tests/browser.ts`
- `fixture/results.json`, `fixture/USAGE.md`

Include package scripts for typecheck, build and browser tests, then execute
them. results.json must record actual check name/method/expected/actual/status,
SDK versions, browser channel/build, direct tool/model-message counts, screenshot
paths, concise H1-H10 findings, `host_acceptance_verified:false` and
`user_testing_performed:false`. Do not claim real assistant installation or host
paint from this browser fixture. Keep the review short and evidence scoped.

Read only this task and the copied read-only `skills/desktop-plugin-ui/` bundle
as task context. You may install/run the locked dependencies in this workspace,
inspect their local package metadata and type declarations, and fetch current
primary package documentation if necessary. Do not read sibling skills, older
PoCs, repository sources or ambient installed package sources outside this
workspace. Keep generated files, npm/browser caches, browser profiles and all
temporary files within this workspace, outside the copied skill. Do not call
another model/provider, start a service, operate desktop accounts, change global
configuration or install/activate a plugin. Preserve the skill unchanged.
