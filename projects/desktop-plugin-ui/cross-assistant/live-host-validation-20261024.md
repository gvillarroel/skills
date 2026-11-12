# Actual Desktop Chat and ChatGPT setup investigation

Date: October 24, 2026, America/New_York. This extends the earlier synthetic
SDK/browser fixture without replacing its separate evidence layer.

## Claude Desktop actual chat

Environment: Windows; Claude Desktop 3.6556.2, signed-in Free account; local
stdio server; Node task package with MCP SDK 1.32.1, ext-apps 1.7.5, esbuild
0.28.2 and tsx 4.23.15. The server exposes only synthetic UI methods and has
no account, command or filesystem tools. Source:
`projects/desktop-plugin-ui/mcp-probe/live-server.ts` and `live-widget.ts`.

One user-prompted conversation turn used Haiku 5.5 Medium after inspecting the
model picker. The exact prompt was: “Call assistant-ui-limits-probe
ui_limits_open once. No explanation.” Claude discovered the tool, displayed
an Allow once/Always allow/Deny prompt, and the test selected Allow once.
The actual token total was not exposed, so none is estimated. Subsequent
button actions did not add conversation turns.

Observed chain: real MCP initialize advertised the UI MIME, host forms and URL
elicitation; a resource read and one opening-tool call were logged; the actual
iframe painted connected state and 7; a visible direct-tool button changed
7 to 8; invalid input returned -32602 through an error result and preserved 8.
The host entered fullscreen, retained 8, and returned to inline retaining 8.
Context update returned an acknowledgement without a reply. PiP was absent
from availableDisplayModes and the probe disabled its control.

The real host displayed Download file consent for a synthetic text resource;
Cancel returned isError true. The real host displayed Open external link
consent for example.com; Cancel returned isError true. No download file or
external navigation was completed. Form/URL elicitation advertisement was
not exercised as a rendered host-owned form or URL flow.

The immediate parent title was MCP-UI Proxy, window.openai was undefined, and
the secure-context flag was true. This did not test access to top application
DOM, Node, cookies, clipboard, storage, sampling or device permissions. The
synthetic fixture's opaque-parent SecurityError must not be generalized to
every immediate parent in production.

The first inline viewport clipped controls. An offscreen accessible-button
click did not invoke the tool; scrolling revealed the button, after which the
action worked. Preserve this failed automation attempt as a layout/reachability
issue. The declared UI bundle was roughly 973 KB; its acceptance is not a
measurement of a maximum resource size.

Raw sanitized MCP logs, private screenshots/AX captures and verification JSON
are under `projects/desktop-plugin-ui/artifacts/cross-assistant/claude-desktop-live/`.
Screenshots can contain unrelated sidebar/account labels and remain ignored.
No private payload is copied into the runtime skill or versioned report.

Recheck captured evidence without another model call:

```powershell
uv run --script projects/desktop-plugin-ui/scripts/verify-live-captures.py
```

Result: **14/14 capture assertions passed**. This is an audit of retained
observations, not a fresh replay. It checks discovery, resource/open count,
paint, increment, error preservation, fullscreen/inline, context, ancestry,
available modes, both consent cancellations, screenshots and restoration.

## Configuration restoration

Before adding the task server, the configuration was backed up privately and
hashed. Exactly one temporary key, assistant-ui-limits-probe, was added; the
existing server was preserved. After testing, Claude was exited through its
File menu. The current configuration matched the task's written hash, so the
original bytes were restored exactly. The restoration check reports one
original server, no temporary server, and matching original SHA-256. Claude
was reopened with that configuration. Startup automation initially timed out
waiting for a window; a later inventory confirmed it running. This was a
target-acquisition timing issue, not a failed MCP server or product crash.

The separate loopback HTTP fixture was stopped. No public tunnel was started.

## Claude Code account handoff

The already installed Claude Code 2.1.302 passed the independent native tests
without a login or model request. Sanitized CLI auth status remained logged
out even though Desktop was signed in. At the user's request,
`claude auth login --claudeai` opened the official browser flow. The user must
finish its account challenge. No password, OAuth state, code or credential
file was displayed or copied into evidence. Actual authenticated terminal
paint remains pending that gate; engine acceptance is recorded separately.

## ChatGPT setup and bounded blockers

A signed-in Chrome ChatGPT web session exposed Add custom MCP server and its
name, URL, authentication and acknowledgement controls. The official
[Excalidraw MCP repository](https://github.com/excalidraw/excalidraw-mcp)
provided the public reference endpoint. A task-named personal plugin draft
reached the final Connect consent screen. That screen states the app can
receive relevant conversation/memory context, so the final connection was
left pending explicit user confirmation. No tool call, prompt or UI was
sent through the reference server. Setup UI is observed; component paint is
untested. Pending consent is neither an app failure nor a product exclusion.

An attempted public Cloudflare development tunnel for the synthetic-only
server was rejected by automatic execution review with “blocked by policy.”
The command did not run; no more specific reason was supplied. It was not
retried through an equivalent command or another execution route. The safer
public reference setup above was prepared instead. The official private
[Secure MCP Tunnel](https://developers.openai.com/api/docs/guides/secure-mcp-tunnels)
route was researched, including organization/workspace associations, API key
and roles; it was not configured. A policy denial is not evidence that
ChatGPT cannot render MCP Apps.

The [current connection guide](https://developers.openai.com/plugins/deploy/connect-chatgpt)
confirms public HTTPS or private Secure MCP Tunnel, account/workspace controls,
metadata refresh, and new-conversation testing. These are documented routes;
only the setup-screen stage above was observed here.
