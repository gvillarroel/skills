# MCP Apps methods and boundary patterns

## Contents

[Registration](#claude-ui-tool-resource), [actions](#claude-ui-server-action),
[context](#claude-ui-context-followup), [modes](#claude-ui-mode-negotiation),
[CSP](#claude-ui-csp-sandbox), [capabilities](#claude-ui-optional-capability).

Snapshot: 2026-10-24. Use the current official SDK examples for implementation;
the local probes pinned ext-apps 1.7.5 and MCP SDK 1.32.1. Do not mix that v1
server scaffold with the newer split v2 packages without checking their API.

For executable package and browser tests, use
[browser-validation.md](browser-validation.md). It covers the actual extracted
resource and standard bridge, safe Playwright callback execution, sandboxed
keyboard actions, deferred responses and recovery. Fixture success remains
separate from real-host painting.

| Purpose | Portable method/metadata | Constraint |
| --- | --- | --- |
| Associate tool and View | `_meta.ui.resourceUri`, `ui://...` | Register a matching readable HTML resource. |
| UI MIME | `text/html;profile=mcp-app` | Plain HTML text is not sufficient registration. |
| Startup | `new App(...)`, handlers, `await app.connect()` | Register handlers before connecting; wait before host calls. |
| Input/result | `ontoolinput`, `ontoolinputpartial`, `ontoolresult` | Partial input is incomplete; never commit side effects from it. |
| Invoke server | `app.callServerTool(...)` / `tools/call` | Server validates and authorizes each call. |
| Inform next model turn | `app.updateModelContext(...)` | Replaces this View's context; does not start a reply. |
| Ask for model follow-up | `app.sendMessage(...)` | Host-mediated request; do not infer unattended sending. |
| Request presentation | `app.requestDisplayMode(...)` | Respect negotiated modes and actual returned mode. |
| Open/export | `app.openLink(...)`, `app.downloadFile(...)` | Optional host capabilities and host policy. |
| Theme/layout | `getHostContext`, `onhostcontextchanged`, auto resize | Host constrains final bounds. |

Authoritative references: [MCP Apps specification](https://github.com/modelcontextprotocol/ext-apps/blob/main/specification/2026-01-26/apps.mdx),
[App API](https://apps.extensions.modelcontextprotocol.io/api/classes/app.App.html),
[Claude getting started](https://claude.com/docs/connectors/building/mcp-apps/getting-started).

## claude-ui-tool-resource

- **Trigger/input:** Add an interactive View to a selected MCP tool; define a
  versioned `ui://` URI, schema, HTML bundle, and useful text result.
- **Rule:** Register the tool and resource with `registerAppTool` and
  `registerAppResource`; link `_meta.ui.resourceUri`. Return the UI MIME type.
  In the app, register handlers before `connect()`, then render tool results.
- **Failure/fallback:** Missing metadata/resource/MIME or handshake are distinct
  failures. A successfully installed server need not have a renderable View.
  Change the URI when incompatible content changes require cache invalidation.
  Keep the initial result small and fetch details on demand. Claude documents a
  roughly 150,000-character result issue when an active code-execution sandbox
  substitutes a file pointer, preventing hydration; this is not a universal
  protocol payload limit. [Hydration diagnosis](https://claude.com/docs/connectors/building/mcp-apps/troubleshooting).
- **Validate:** `tools/list`, `resources/read`, MIME, initialization, notification
  delivery, visible paint, and non-UI client result. Metadata/MIME/results passed
  real SDK tests; paint passed only a browser fixture.
- **Evidence:** Documented, with scoped observed-working registration/bridge.

## claude-ui-server-action

- **Trigger/input:** Refresh, pagination, or editing with validated arguments.
- **Rule:** Use `callServerTool`, pending/error state, and server-authoritative
  results. Give model tools clear intent; use `_meta.ui.visibility:["app"]`
  for controls intended only for the View where supported. Keep expensive data
  processing separate from render-tool attachment when it avoids remounts.
- **Failure/fallback:** App visibility is not an authorization boundary. Tool
  annotations are hints. Reject unknown tools and invalid requests on the
  server; never accept an arbitrary executable name from UI input.
- **Validate:** Good call, schema failure, unknown tool, missing connection,
  retained prior data, and concurrent update behavior.
- **Evidence:** Real SDK increment/schema rejection and browser bridge refresh
  passed; visibility filtering was documented but not exercised by the fixture.

## claude-ui-context-followup

- **Trigger/input:** A selection useful to later reasoning, or an explicit
  user action requesting analysis of the selected record.
- **Rule:** Use `updateModelContext` for concise current selection facts; use
  `sendMessage` for an intentional follow-up request. Keep transient hover and
  private display details local. Include stable IDs and the requested action.
- **Failure/fallback:** Context update does not invoke the model or create an
  append-only event log. An accepted synthetic message does not establish a
  model reply or an external email/chat message. Retain a readable selection.
- **Validate:** Last update replaces prior context; no unsolicited follow-up
  from local filtering; host rejection handled; actual next-turn behavior.
- **Evidence:** Fixture accepted both method shapes; real model delivery and
  resulting turn remain untested. [Context API](https://apps.extensions.modelcontextprotocol.io/api/classes/app.App.html#updateModelContext).

## claude-ui-mode-negotiation

- **Trigger/input:** A task requests inline, fullscreen, or optional PiP.
- **Rule:** Declare your app's modes and inspect the host's available modes.
  Request a supported change and reconcile with the returned actual mode.
  Keep the component's display-mode request separate from opening its host
  side-panel view. A fullscreen request does not prove that an automation
  controller can discover or bind a side-panel tab.
- **Failure/fallback:** `pip` in SDK types is not proof Claude Desktop offers
  it. Keep inline usable if mode is denied. Feature-detect capabilities rather
  than branching on product names.
- **Validate:** Host accepts fullscreen, returns inline on a denied request,
  emits context updates, and preserves state across the transition.
- **Evidence:** Negotiation/denied return passed the synthetic fixture.
  Claude documents inline/fullscreen; PiP stays conditional until host evidence.
  [Claude display guidance](https://claude.com/docs/connectors/building/mcp-apps/design-guidelines).

## claude-ui-csp-sandbox

- **Trigger/input:** A View needs CDN assets, API calls, nested media, or an
  external editor; inventory its exact origins and resource purposes.
- **Rule:** Bundle when practical. Declare `resourceDomains` for assets,
  `connectDomains` for network requests, and only required frame origins.
  Claude restricts `frameDomains` pending security review; check approval
  before planning an embedded third-party site. Treat UI data as untrusted.
- **Failure/fallback:** The sandbox isolates the application; an immediate
  proxy/wrapper parent may still be readable. Test the actual ancestry and
  protected host boundary separately. CSP,
  CORS, provider frame policy, and host permission are separate checks. A CSP
  allowlist does not grant authorization or bypass any of those policies.
- **Validate:** Authorized asset works, undeclared asset/network fails,
  protected host access is blocked, embedding policy, console errors, and external
  `openLink` fallback. Probe parent access raised `SecurityError`; `connect-src
  'none'` blocked fetch in an explicitly configured browser sandbox.
- **Evidence:** Documented boundary and observed-working browser restriction;
  this was not Claude's exact generated sandbox/CSP. The later real Desktop
  probe read the immediate `MCP-UI Proxy` parent's title; this did not test
  access to the top application document. See [live limits](claude-chat-live.md).
  [Claude CSP guidance](https://claude.com/docs/connectors/building/mcp-apps/design-guidelines).

## claude-ui-optional-capability

- **Trigger/input:** Downloads, links, sampling, clipboard, camera, microphone,
  location, or another optional host/browser method.
- **Rule:** Check advertised host capabilities, granted permissions, platform,
  browser API, and response. Request only needed permissions; use server-side
  handling/manual input as appropriate. Check each capability independently.
- **Failure/fallback:** A method's existence is not a support check. In the
  pinned SDK, `downloadFile` still dispatched with no advertised download
  capability; the test host had to reject it. Handle denial even after a
  positive capability check. Claude's current mobile guide excludes camera,
  microphone, and location access on mobile.
  Claude local/custom connector links normally require host confirmation;
  directory allowlisting plus a real user gesture can permit bypass. Even a
  successful bypass response establishes an attempted open, not verified
  navigation. [Claude external links](https://claude.com/docs/connectors/building/mcp-apps/external-links).
- **Validate:** Capability present/absent, explicit host denial, browser denial,
  manual fallback, and real target-host outcome. Never label a permission
  request, fixture acknowledgement, or SDK type as granted access.
- **Evidence:** Observed SDK dispatch plus synthetic host rejection; actual
  device permissions and sampling remain untested.
