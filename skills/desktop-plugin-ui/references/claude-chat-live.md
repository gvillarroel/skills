# Actual Claude Desktop Chat observations

Snapshot: October 24, 2026, America/New_York. Windows, Claude Desktop
**3.6556.2**, signed-in Free account, local stdio MCP server, MCP SDK 1.32.1
and ext-apps 1.7.5. One fresh minimal Haiku 5.5 Medium request opened the
synthetic app. Exact token totals were not exposed by the UI; do not estimate
them. All subsequent button tests used zero additional model turns.

This is ordinary **Chat**, separate from Desktop Code/native Mods. The account
being signed in here did not sign in Claude Code CLI: its sanitized auth
status remained logged out and its requested OAuth flow awaited the user.

## Actual results and rules

| Action | Observed result | Transferable rule |
| --- | --- | --- |
| Add one temporary local server and restart | Existing server preserved; probe appeared in Connectors | Installation/configuration, discovery and painting are distinct stages. Restore temporary changes after testing. |
| MCP initialize | Real `claude-ai` client advertised UI MIME extension, form and URL elicitation | Advertisement proves negotiation only; host-owned form/URL rendering was not exercised. |
| Request opening tool | Host showed request `{}` and Allow once/Always allow/Deny | Preserve host authority; the test used Allow once. |
| UI resource and first paint | Resource read logged; inline HTML iframe displayed connected state and value 7 | Actual signed-in chat paint succeeded for this route/build/account. |
| App-only increment tool | Button called the local server and changed 7 to 8 | Direct app tool interaction can work without another model turn. |
| Invalid input | Server returned `-32602` via `isError:true`; displayed value remained 8 | Preserve last authoritative state on a failed mutation. |
| Fullscreen | Real host returned `{mode:"fullscreen"}`, enlarged the same app and retained 8 | Use the returned mode and test actual layout, state and return-to-inline. |
| Picture-in-picture | Host context listed inline/fullscreen only; probe disabled PiP | Absence in this context is conditional availability, not a universal Claude exclusion. No PiP request was sent. |
| Update model context | Actual bridge acknowledged `{}`; no reply/new model turn occurred | Context delivery acknowledgement does not prove a future model consumed it. |
| Sandbox inspection | `window.parent.document.title` returned `MCP-UI Proxy`; `window.openai` undefined; secure context true | Immediate proxy access can work. Top application DOM, cookies, Node and arbitrary local files were not tested. Do not import ChatGPT-specific APIs. |
| Download synthetic text | Real host showed Download file consent for `result.txt`; Cancel returned `isError:true` | Capability presence does not bypass consent. Actual file writing/bytes were not tested. |
| External example.com link | Real host showed Open external link consent; user-action path was cancelled | An openLinks capability is not automatic navigation. Actual browser navigation was not tested. |

The widget received `openLinks`, `downloadFile`, server tools/resources,
logging, text/image context, and text message capabilities. Its resource CSP
listed empty connect/resource origin arrays. These observations do not prove
clipboard, sampling, camera, microphone, geolocation or storage access.
Display context included dark theme, desktop platform, dimensions and safe-area
insets. Theme switching, resize and alternate platforms remain untested here.

## Layout and evidence cautions

The first inline frame was short and controls required scrolling. A click at
an offscreen accessible element did not invoke its handler; after scrolling,
the same button worked. Distinguish an automation/layout issue from tool failure.
Design for the reported container, send appropriate size updates, and test
keyboard and narrow layouts. Fullscreen preserved state in this cohort; it
does not prove arbitrary remount persistence.

The server exposed only synthetic probe tools and UI; it had no account,
filesystem or command tool. Raw traces/screenshots and the temporary config
backup belong outside the runtime bundle. Keep private account identifiers,
OAuth state and unrelated chat content out of reusable evidence.

## Reproduction

Follow the [official local route](https://claude.com/docs/connectors/building/mcp-apps/getting-started)
with a minimal trusted server. Register a tool/UI resource, retain a plain
text/structured result, initialize before updating the UI, and log only
synthetic method names/capabilities. Use the
[SDK App contract](https://apps.extensions.modelcontextprotocol.io/api/classes/app.App.html)
for direct actions, errors, modes and optional capabilities, and check
[external-link behavior](https://claude.com/docs/connectors/building/mcp-apps/external-links).

Record build, account type, exact transport, one model-turn count, resource
read, actual paint, direct action, schema error, mode, consent and cancellation.
Compare before/after configuration hashes and restore only task-owned changes.
Remote deployment, MCPB installer, Cowork, mobile, native Code paint and
host-owned elicitation are separate acceptance cases.
