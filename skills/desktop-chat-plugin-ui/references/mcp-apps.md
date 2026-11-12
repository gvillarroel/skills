# Build and validate an MCP App

Use the current MCP SDK and MCP Apps SDK with pinned versions. Keep the
server's business operations useful through text and structured tool results.
Register a `ui://` resource with MIME `text/html;profile=mcp-app`, and link the
render tool through `_meta.ui.resourceUri`. Keep data-only operations separate
when attaching UI to every result would cause unnecessary remounts.

In the browser, create `App` from `@modelcontextprotocol/ext-apps`, register
`ontoolinput` and `ontoolresult` before `await app.connect()`, and render the
received structured data. Use `app.callServerTool({name, arguments})` for direct
actions, validate its result, show failures, and preserve entered state.
The App method and MCP client's `callTool` have different argument signatures;
type-check against the installed declarations instead of copying timeout slots.

The tool transport and UI bridge are distinct. Stdio carries MCP between the
host and local server; the browser uses the SDK-selected host transport.
Do not connect a browser directly to a stdio pipe or invent an HTTP server just
to draw a form. A framework does not grant placement or host permissions.
[MCP Apps standard](https://modelcontextprotocol.io/docs/extensions/apps),
[SDK](https://github.com/modelcontextprotocol/ext-apps).

## Patterns and contracts

- Tool/resource: accept a validated domain input; return text plus structured
  data; read the declared URI and verify its MIME and exact linked metadata.
- Direct action: accept an explicit control event; call a scoped tool; update
  the view without another model turn. Test denied and malformed results.
- State: rehydrate server-authoritative data after mount; retain local drafts
  across recoverable failures; distinguish durable storage from widget state.
- Presentation: start inline and request other modes only through negotiated
  capabilities. Test refusal and keep a usable inline or text route.
- Isolation: declare only the required connect/resource/frame origins. Keep
  nested frames, device access, storage, files, and external navigation behind
  individual host contracts and checks.

Enforce authorization and input validation on the server. UI capability flags
and result metadata are not authorization. Render untrusted strings as text.
Do not read the host DOM, expose secrets in component data, or assume Node or
filesystem APIs inside an iframe.

## Verification

Start the declared command from an extracted/copied package outside the
author's dependency tree. Require initialize, tools/list, tools/call, and
resources/read through a real client. Reserve stdio stdout for protocol JSON.
Check build metadata for unbundled imports rather than grepping bundled SDK
strings. Then use [browser-validation.md](browser-validation.md) to render
the actual resource in a sandbox through a real standard bridge fixture.
Check narrow/wide layouts, keyboard, cancellation, recovery, and direct-action
dispatch. A standalone preview or fake `window.openai` object is insufficient.

For missing UI, inspect discovery, metadata, resource fetch, initialization,
result delivery, CSP, policy, and finally paint. Real host installation and
visible interaction require their own acceptance checks. Keep text fallback
usable when the host does not render UI.
