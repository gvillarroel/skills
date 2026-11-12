# Assistant surface matrix

Routing updated November 11, 2026; dated observations below remain separate.
This is a bounded evidence inventory, not a claim
to enumerate every possible product limit. Recheck the named frontend/build,
transport, account, policy, and negotiated capabilities before deployment.
Cloud Code/Desktop is interpreted as Claude only when session context resolves it.

| Assistant and surface | UI mechanism | Measured boundary | Detail |
| --- | --- | --- | --- |
| Claude Desktop Chat 3.6556.2 | Local stdio MCP Apps HTML iframe; separate host elicitation contract | Actual initialization, resource read, UI paint, direct tools and fullscreen succeeded on a signed-in Free account. Host form/URL paint, remote, Cowork and mobile remain untested. | [Live Chat](claude-chat-live.md), [deployment](distribution.md) |
| Claude Code 2.1.302 terminal | Native Mods, hook render sites, terminal primitives | 57 native engine tests passed without inference. Raw HTML refused; Svg refused; Image/Raster accepted by validator. Paint remains a separate check. | [Native limits](claude-host-limits.md) |
| Claude Desktop Code / Claude VS Code | Native Mods with frontend-specific primitives/props | Engine accepts Svg, refuses terminal Image/Raster; VS Code refuses Client and ignores documented props. Actual paint untested. | [Native limits](claude-host-limits.md) |
| Codex CLI 0.145.0 | Tool text/structured/image content and elicitation policy | Real CLI turn completed. App-server returns HTML bytes but did not advertise MCP Apps on observed connections; `never` declines forms, `on-request` forwards callbacks. | [Codex](codex-limits.md) |
| Codex desktop / IDE / custom app-server client | Frontend-owned rendering and host APIs | Historical Windows desktop chart paint is bounded evidence; IDE and new placements/forms still need their own checks. A custom client can render its own UI. | [Current offerings](capability-offerings.md), [Codex](codex-limits.md) |
| ChatGPT web / desktop | MCP Apps and optional OpenAI extensions | Signed-in web connection workflow inspected; live component acceptance pending. Standard bridge fixture success does not establish ChatGPT paint. | [ChatGPT](chatgpt-limits.md) |
| ChatGPT Desktop local threads | Desktop-only plugin with bundled local stdio MCP | Current documented local route; separate from remote connection and public submission. Recheck the actual build and local installation. | [Authoring](plugin-authoring.md) |
| Pi TUI / RPC / JSON / print | TypeScript extension commands and tools; native UI bridge in interactive modes | Native dialogs and custom TUI have different mode support; `hasUI` alone does not establish terminal painting. | [Pi extensions](pi-extensions.md) |
| Google Cloud Gemini Enterprise app | Host-supported A2UI catalogs over A2A; hosted agent and administrator registration | Current documentation supports A2UI v0.8/v0.9, host styling, and version-compatible A2A streaming. Local protocol/catalog tests and signed-in host paint remain separate; inherited live paint is absent. | [A2UI registration](https://docs.cloud.google.com/gemini/enterprise/docs/a2ui-agents/register-and-manage-an-a2ui-agent), [component catalog](https://docs.cloud.google.com/gemini/enterprise/docs/a2ui-agents/a2ui-component-gallery-reference) |
| Copilot CLI 1.0.103 | Experimental extension UI; native terminal forms | Actual confirm/select/input/cancel passed with zero model requests. `mcpApps:false` in this terminal; bare SDK requires UI callbacks. | [Copilot](copilot-limits.md) |
| Copilot VS Code 1.143.1 | MCP Apps chat, extension webviews, preview canvases | Five actual webview checks passed; Copilot chat MCP Apps paint remains untested. Documented MCP Apps are inline only. | [Copilot](copilot-limits.md) |

## Cover each limitation dimension

For Gemini Enterprise, prepare an A2A agent with the host-compatible A2UI
extension/catalog declaration, validate the versioned message and component
schemas, exercise streaming and action responses, then deploy/register only
within the requested scope. The upstream newest A2UI/A2A version does not
establish host support. Gemini CLI, Code Assist, consumer Gemini, and MCP Apps
use different contracts. An absent specialist does not require another skill:
the official registration and component links above provide this bundle's
standalone fallback. Keep actual host UI acceptance untested until executed.

For a requested host, report each relevant dimension as documented, observed,
conditional, unsupported, or untested. Do not fill unknowns with a universal no.

| Dimension | Required distinction |
| --- | --- |
| Content | Transcript Markdown/code/image is separate from executing HTML/JS, native SVG, canvas/WebGL, or a downloaded browser artifact. Framework choice does not grant a UI surface. |
| Placement | Inline, fullscreen, picture-in-picture, pane, sidebar, composer mention, file viewer and host modal require their own contract. |
| Controls | App-owned form, host-owned elicitation, terminal prompt, permission dialog and package settings have different schemas and authority. |
| Authority | CSP/network origins, iframe ancestry, Node/filesystem access, trusted host bridge and tool permissions are independent boundaries. |
| Browser features | Clipboard, download/upload, camera/mic/location, embedded frames, external links and storage require individual host checks. |
| State | Component-local state, model context, drafted/submitted messages, widget persistence and server-authoritative data have different lifetimes. |
| Lifecycle | Test mount/result ordering, errors, cancellation, reload, resize/theme, close/disposal and reopen. A validator pass is insufficient. |
| Deployment | Local stdio, reachable HTTPS, private tunnel, local extension installation, account plan and workspace policy are separate gates. |
| Budgets | Record bytes/chars/dimensions/time/rate only for the measured or documented host/version. Record model calls separately from network traffic. |
| Evidence | Keep synthetic bridge tests, real engine/extension-host tests, actual terminal paint, and signed-in chat UI acceptance distinct. |

## Investigate in increasing cost order

Inventory installed builds and help; inspect account status without credentials;
validate package/schema; initialize protocol; exercise direct local controls;
then use one minimal model turn only when needed to reach actual chat UI.
Use synthetic data and a server with no unrelated filesystem or command tools.
Preserve failed attempts, expected/actual results, logs, and screenshots outside
the skill payload. Stop at account, policy, or permission gates and name that
gate accurately. Never bypass a rejected action through an equivalent command.

Shared rules and primary links are in the linked references. A product sharing
the same model or MCP transport does not inherit another product's renderer.
