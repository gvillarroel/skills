# ChatGPT plugin UI limits

Snapshot: October 24, 2026. Distinguish ChatGPT web, desktop, Work, mobile,
Codex, and a standalone browser. A ChatGPT subscription authenticating Codex
does not make Codex's renderer the ChatGPT renderer.

## Contents

- [Portable foundation](#portable-foundation)
- [Host extensions and restrictions](#host-extensions-and-restrictions)
- [Deployment and empirical boundary](#deployment-and-empirical-boundary)
- [Decision recipes](#decision-recipes)

## Portable foundation

Use `_meta.ui.resourceUri`, a `ui://` HTML resource with
`text/html;profile=mcp-app`, and the MCP Apps bridge. ChatGPT renders the
component in an iframe. Keep data tools useful when no component renders;
separate data processing from render tools to avoid unnecessary remounts.
Detect optional `window.openai` functions before using them. Keep authoritative
data on the server; widget state is not durable business storage.
[OpenAI UI architecture](https://developers.openai.com/plugins/build/chatgpt-ui).

## Host extensions and restrictions

| Area | Documented boundary |
| --- | --- |
| Placement | Inline, fullscreen and picture-in-picture exist; declare supported modes and negotiate actual availability. |
| CSP | Separate `connectDomains`, `resourceDomains`, and `frameDomains`. Nested frames are denied by default; submission can require justification/review. |
| Origin | A unique `_meta.ui.domain` is required when submitting UI; default sandbox is `https://web-sandbox.oaiusercontent.com`. Do not copy Claude's hash rule. |
| External navigation | Legacy `openai/widgetCSP.redirect_domains` remains needed for trusted `window.openai.openExternal` destinations. Standard CSP does not replace it. |
| Data visibility | `content` and `structuredContent` reach model/component. Result `_meta` goes to component, hidden from the model; it is not an authorization system. |
| Optional APIs | File selection/upload/download URLs, host modal, widget persistence and checkout require specific feature checks and eligibility. |

See the [OpenAI plugin reference](https://developers.openai.com/plugins/reference).
The table describes contract availability; actual permissions, plan and renderer
must still be tested. Arbitrary access to host application DOM, Node, or local
files does not follow from having iframe JavaScript.

OpenAI extensions add sidebar apps, conversation panels, settings, file viewers,
deep links, extended context/messages/forms, composer mentions and onboarding.
These are explicit extension points, not unrestricted host DOM insertion.
Composer mentions are desktop-only in the snapshot. Web extension rollout for
Free/Go is described as coming soon; existing plugin functionality is separate.
Extended forms can add thumbnail options, and OpenAI-registered MCP servers require
multi-round-trip requests (MRTR).
[Extension contract and rollout](https://developers.openai.com/plugins/build/extensions).

## Deployment and empirical boundary

ChatGPT accepts a reachable public HTTPS MCP endpoint or Secure MCP Tunnel.
Local stdio can be reached through an appropriately configured private tunnel;
do not declare local stdio universally impossible. Refresh changed metadata and
test in a new conversation. Account/workspace controls apply.
[Connection guide](https://developers.openai.com/plugins/deploy/connect-chatgpt).

Private tunnels require a tunnel ID, runtime key, organization/workspace
association and roles. Documented service limits: 600 requests/minute,
10 MiB serialized envelope, 120-second request deadline, 1,000 queued requests.
These are tunnel limits, not general component size or chat time limits.
[Secure MCP Tunnel](https://developers.openai.com/api/docs/guides/secure-mcp-tunnels).

Observed in this investigation:

- Signed-in ChatGPT web exposed Add custom MCP server, endpoint/auth fields,
  risk acknowledgement, and Create as a plugin. A public reference server
  reached the final Connect consent screen. This proves the setup UI, not
  completed connection or component paint.
- The exact public reference endpoint came from the
  [Excalidraw MCP repository](https://github.com/excalidraw/excalidraw-mcp).
  No inference or external tool call was sent through it before connection.
- A synthetic local SDK/server/browser fixture passed bridge and sandbox
  tests. These are portable implementation tests, not ChatGPT host acceptance.
- A proposed public development tunnel was rejected by execution policy;
  no tunnel started. That is an environment-policy blocker, not proof that
  ChatGPT rejects custom UI. The private OpenAI tunnel route was documented,
  not configured or empirically tested in this investigation.

Widget paint, optional OpenAI APIs, real-host device permissions and mode
changes remain untested here. Do not generalize a setup screen to all plans,
platforms or workspaces. Treat uncompleted consent as pending, not refusal.

## Decision recipes

### `chatgpt-ui-shared-bridge`

- Trigger/input: a tool has structured results requiring interactive inspection.
- Rule: use the shared MCP Apps resource/bridge first; implement optional host
  functions behind capability checks and keep text output useful.
- Failure/check: inspect resource fetch, initialization and result delivery,
  then actual iframe paint. A successful ordinary browser is a lower layer.

### `chatgpt-ui-entrypoints`

- Trigger/input: a sidebar app, file editor, settings or composer workflow.
- Rule: choose the documented entrypoint and confirm platform/rollout first;
  register its metadata and supported file types where applicable.
- Failure/check: verify discoverability and interaction in the named frontend.
  Fall back to a supported inline app or file artifact when unavailable.

### `chatgpt-ui-capability-gates`

- Trigger/input: modal, file action, display mode, navigation or payment UI.
- Rule: feature-detect each method and enforce server permissions. Return a
  clear supported alternative when absent; cancellation is not acceptance.
- Failure/check: test one allowed and one absent/denied case, preserving state.
  Payment eligibility or private beta cannot be inferred from method names.

### `chatgpt-ui-private-deployment`

- Trigger/input: private local tools need ChatGPT UI without public ingress.
- Rule: use the documented Secure MCP Tunnel with correct associations and
  runtime roles; keep keys out of commands, reports and screenshots.
- Failure/check: verify client readiness and discovery, then one synthetic tool
  and actual widget. A missing role is an access gate, not an HTML limitation.

### `chatgpt-ui-state-lifetimes`

- Trigger/input: selections, staged edits or preferences must survive changes.
- Rule: separate component-local state, model context, widget persistence and
  durable server state. Do not depend on localStorage for cross-session data.
- Failure/check: test local interaction without inference, remount and a new
  session; rehydrate authoritative data and report which state survived.
