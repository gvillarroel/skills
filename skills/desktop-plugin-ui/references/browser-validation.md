# Validate the delivered MCP App in a browser

Test an extracted web plugin and its real HTML through a standard-bridge
fixture. This does not establish signed-in host installation or paint.

## Contents

- [Keep tests independent of the authoring checkout](#keep-tests-independent-of-the-authoring-checkout)
- [Run browser callbacks without transform helpers](#run-browser-callbacks-without-transform-helpers)
- [Configure the actual SDK and tooling](#configure-the-actual-sdk-and-tooling)
- [Mount the actual resource through the standard bridge](#mount-the-actual-resource-through-the-standard-bridge)
- [Exercise native controls in the real sandbox](#exercise-native-controls-in-the-real-sandbox)
- [Measure and report the correct layer](#measure-and-report-the-correct-layer)

## Keep tests independent of the authoring checkout

Extract the ZIP/MCPB into a new task-owned directory. Run its declared command,
working directory and substituted paths. Initialize a real MCP client, discover
tools, read its `ui://` resource and call the opening tool. Check schema, MIME,
metadata and text/data output; use that exact resource and result in the browser.
A source-tree server or standalone HTML file does not prove the package/bridge.

Keep caches, browser profiles, screenshots and temporary files inside the task
workspace. Preserve failures; test
repairs on separately labeled diagnostic copies, leaving the original intact.

## Run browser callbacks without transform helpers

Playwright serializes `page.evaluate` callbacks into the browser. A TypeScript
runner or bundler can inject a helper such as `__name` into a nested function;
the browser cannot see a Node-side helper or closure variable. An otherwise
valid fixture can then fail before exercising the app.

With Node 24, run a test containing erasable TypeScript directly:

```bash
node tests/browser.ts
```

Use ESM and type-only imports. If using a transpiler, inspect its output or use
plain JavaScript callbacks. Evaluate callbacks must reference only their
serialized argument and browser globals. Do not add fake helpers to the app
or replace its SDK bridge with a test-only `window.openai` object.

## Configure the actual SDK and tooling

Pin the SDK and use its matching declarations. For a bundled browser App, a
tested TypeScript starting point is `module: "ESNext"`,
`moduleResolution: "Bundler"`, `lib: ["ES2022", "DOM", "DOM.Iterable"]`,
`types: []`, `strict: true`, `skipLibCheck: true` and `noEmit: true`. Keep the
Node server/test configuration separate and provide matching `@types/node`
where those files need Node globals. TypeScript does not install declarations.

App 1.7.5 inherits `close(): Promise<void>` from its protocol base. A minimal
same-source probe failed with TS2339 under NodeNext resolution but compiled
under Bundler; the real inherited method resolved at runtime. Diagnose the
declaration chain and resolver before declaring a host API absent. Do not cast
away the error or invent a replacement lifecycle method. Verify cleanup/retry
against the pinned API and test duplicate-handler behavior where applicable.

Inventory a known browser channel before coupling browser startup to app
checks. Use an installed channel or explicitly install the declared Playwright
browser into a task-local cache. Keep profiles/temp under the workspace. A
missing browser binary is tooling readiness, not a component execution failure.

Assert tool names, arguments, business fields and dispatch counts; allow valid
SDK metadata such as `_meta.progressToken`. Normalize incidental whitespace in
DOM text instead of rejecting a correct view's formatting. Keep optional
advisory commands separate from required build/test gates, record each actual
exit outcome, and continue relevant independent checks when an advisory fails.
Never hide a failed required check inside a successful shell chain.

## Mount the actual resource through the standard bridge

The fixture uses a real initialized `client`, resource `html`, opening result
`initial` and Playwright `page`. Replace `selected_filter` with the tested tool.
Keep the app's real SDK/host detection. Install handlers before `srcdoc` and
deliver results only after its initialized notification.

Keep SDK signatures distinct: browser `app.callServerTool(params, options)`
takes at most two arguments; MCP client's `client.callTool(params, schema,
options)` has a separate schema slot. Do not copy the latter's third-argument
timeout into the App method. Type-check against the selected SDK version.

```typescript
await page.exposeFunction("fixtureRpc", async (method, params) => {
  if (method === "ui/initialize") return {
    protocolVersion: params.protocolVersion,
    hostInfo: { name: "controlled-browser-fixture", version: "1.0.0" },
    hostCapabilities: { serverTools: {} },
    hostContext: {
      theme: "light", displayMode: "inline",
      availableDisplayModes: ["inline"]
    }
  };
  if (method === "tools/call" && params.name === "selected_filter")
    return client.callTool(params);
  throw new Error(`Unexpected fixture request: ${method}`);
});
await page.setContent('<iframe id="app" title="MCP App fixture" '
  + 'sandbox="allow-scripts" style="width:100%;height:800px;border:0"></iframe>');
await page.evaluate(({ html, initial }) => {
  const frame = document.getElementById("app") as HTMLIFrameElement;
  window.addEventListener("message", async event => {
    if (event.source !== frame.contentWindow || event.data?.jsonrpc !== "2.0")
      return;
    const message = event.data;
    if (message.method === "ui/notifications/initialized") {
      frame.contentWindow!.postMessage({ jsonrpc: "2.0",
        method: "ui/notifications/tool-result", params: initial }, "*");
      return;
    }
    if (message.id === undefined) return;
    try {
      const result = await (window as any).fixtureRpc(
        message.method, message.params ?? {});
      frame.contentWindow!.postMessage({ jsonrpc: "2.0",
        id: message.id, result }, "*");
    } catch (error) {
      frame.contentWindow!.postMessage({ jsonrpc: "2.0", id: message.id,
        error: { code: -32603, message: String(error) } }, "*");
    }
  });
  frame.srcdoc = html;
}, { html, initial });
```

Assert tool name, user arguments and dispatch count. Allow valid SDK metadata
such as `_meta.progressToken`; whole-object equality against a two-field
literal can reject a correct call. Record methods and expose needed capabilities.
Reject model
messages/sampling from deterministic controls; context updates are separate
from turns. Block unexpected network requests and capture browser errors.
The fixture's sandbox is a declared test condition, not proof of the exact
sandbox or policy used by any named assistant.
[MCP Apps contract](https://github.com/modelcontextprotocol/ext-apps/blob/main/specification/2026-01-26/apps.mdx),
[App API](https://apps.extensions.modelcontextprotocol.io/api/classes/app.App.html).

## Exercise native controls in the real sandbox

A sandbox without `allow-forms` can block form submission, including Enter.
For local actions, wire one click handler to a native `type="button"`; native
Enter and Space activation reach it. Forms can still group fields. Native
form submission needs actual host permission. Avoid click/key handlers that
dispatch the same operation twice.

Test with Playwright's real keyboard and pointer APIs, using accessible labels
and roles. A scripted DOM event or direct handler call does not prove native
keyboard activation. Verify the focused control before pressing a key: Enter
inside a select is not the same interaction as Enter on Apply.

For a draft/apply interaction, check these observable transitions:

- Deliver the opening result; the UI shows the exact authoritative records.
- Change a draft choice; neither server calls nor displayed committed data
  change. Cancel restores the committed choice and sends no server/model call.
- Hold a tool response with a controlled promise. While it is held, check real
  busy feedback and duplicate-submit prevention; then release it and inspect
  the returned result. Do not depend on a lucky delay or fabricated progress.
- Inject both a tool `isError` result and a rejected bridge request. Preserve
  the last good result and draft, expose useful recovery, and test Retry.
- Tab to the primary action and activate Enter and Space in separate cases.
  Check dispatch count and final data, not only that focus moved.
- Reject initialization separately; require visible recovery instead of an
  indefinitely connecting or blank UI. Test reconnection for duplicate handlers.
- Test close/reopen, context/theme changes and disposal when the task uses them.

## Measure and report the correct layer

Inspect at 320px and a useful wide width such as 900px. Check rendered text,
accessible names, focus indication, wrapping, horizontal overflow and every
required field. Inspect success and error screenshots yourself.

Check actual computed foreground/background contrast after opacity and
compositing, including errors, selected states and focus. Use exact chosen
palette tokens for authored styling, while preserving native/host theme and
accessibility overrides. Literal hex membership alone is not contrast approval;
native control internals or host-owned chrome are a separate styling scope.
Use [usability-and-color.md](usability-and-color.md) for H1-H10 and thresholds.

Report package, protocol, browser fixture, actual host paint and user testing
separately. Include build, sandbox/capabilities, sequence, dispatches, screenshots,
failures and pending checks. A working final artifact does not erase tool errors
from its strict generation trace or establish user testing.
