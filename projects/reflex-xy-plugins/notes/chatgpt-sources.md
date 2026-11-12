# ChatGPT adapter: verified official sources

Adapter 0.3.1 always defaults a new chart to Colorset 1. Colorset 2 requires an
explicit user request or selector click. The request boundary normalizes an
omitted colorset independently for each request; no previous chart or widget
selection changes that default. Real HTTP and bundled stdio regressions render
explicit Colorset 2 first, then a fresh omitted-colorset chart and verify the
returned palette and downloadable specification are Colorset 1.

The 0.3.1 component initially presents only the interactive chart, Save image,
More options, and Expand when the host supports it. A stable disclosure button
reveals two flat groups, Display and Export, with labeled native selects.
The preview-only compact response hides the native modebar; a parent-only fixed
boolean message reveals it without navigation or loss of the current chart view.
Original exported HTML and image files remain intact. Component template URI
`ui://reflex-xy/chart-v4.html` separates the corrected embedded transport from
the earlier loopback-frame resource. Actual ChatGPT tool execution and paint
now pass through a direct local MCP connection; sidebar entrypoints and its
installed-host control paths remain separate checks.

Checked on 2026-10-24 through the official OpenAI documentation MCP server.
Searched `Apps SDK MCP Apps UI iframe`, then fetched the actual pages before
implementing the adapter. The documentation currently calls the integration
plugins and recommends standards-first MCP Apps.

- [Add UI to your MCP server](https://developers.openai.com/plugins/build/chatgpt-ui):
  `_meta.ui.resourceUri`, `ui/initialize`, tool result notifications, tool calls,
  host-mediated actions and optional ChatGPT extensions. The adapter uses the
  portable bridge rather than assuming `window.openai` exists.
- [MCP server and UI quickstart](https://developers.openai.com/plugins/build/app-quickstart):
  the official Node SDK and MCP Apps helpers, stateless Streamable HTTP `/mcp`,
  `text/html;profile=mcp-app` resources, publicly reachable HTTPS and custom
  connection steps. This adapter uses the same server interface with explicit
  dependency pins and its own bounded HTTP parser.
- [Reference](https://developers.openai.com/plugins/reference): output schemas,
  read-only/destructive/open-world annotations, standard UI metadata, resource
  CSP `connectDomains`, `resourceDomains`, `frameDomains`, and dedicated UI
  origins for public submissions. Tool output remains useful without a widget.
- [Iframe policy](https://developers.openai.com/plugins/plugin-guidelines#iframes-and-embedded-pages):
  own-domain pages may be embedded when declared in `frameDomains`; public
  submission still needs a justification and may need additional review.
- [Authentication](https://developers.openai.com/plugins/build/auth): private
  authenticated connections use OAuth 2.1 with MCP discovery, PKCE and token
  verification. ChatGPT cannot present a custom API key. The prototype's
  ChatGPT connection therefore uses No authentication for non-sensitive demo
  data; its optional static bearer transport secret is only for compatible
  clients, not a substitute for ChatGPT OAuth.
- [Desktop-only plugins](https://developers.openai.com/plugins/deploy/desktop-only):
  ChatGPT Desktop can run a packaged local MCP server over stdio, with explicit
  `type`, `command`, `args`, and `cwd` in `mcp.json`; `${PLUGIN_ROOT}` resolves
  portable paths. The approval/allowlisting statement concerns publication
  submissions; it does not establish a gate for direct local MCP development.
- [Model Context Protocol](https://learn.chatgpt.com/docs/extend/mcp):
  ChatGPT Desktop, Codex CLI and IDE share same-host MCP configuration. The
  documented settings flow saves a STDIO server then selects Restart; `/mcp`
  shows connected servers. The CLI alternative is `codex mcp add`.
- [Portable plugins](https://developers.openai.com/plugins/build/plugins):
  `plugin.json`, root-level skills and `mcp.json` form a portable local bundle.
  Local/repository marketplace availability varies by desktop surface/account.
- [Sidebar apps](https://developers.openai.com/plugins/build/extensions#sidebar-apps):
  tool metadata `_meta["openai/ui"].entrypoints` accepts `{type:"global"}` for
  the global sidebar and `{type:"thread"}` for a conversation's side panel.
  The app-only `xy_open_chart_app` advertises both and deterministically seeds
  the existing component with explicitly labeled Colorset 1 sample data.

For the 0.3.0 desktop update, searched the exact topics `ChatGPT desktop local
plugins stdio mcp.json` and `plugin sidebar app entrypoint tool launcher`, then
fetched the pages above before changing sources. Sidebar metadata follows the
official OpenAI page's exact object shape. Host fixture tests do not demonstrate
that an actual installed host surfaces these entries or allows loopback assets.

### Observed local loader compatibility

On October 25, 2026, the installed Codex 0.145.0 loader discovered the plugin's
skill and MCP server but left the documented `${PLUGIN_ROOT}` placeholder
literal in the server arguments, working directory and environment. The real
`codex mcp list --json` output rooted that literal working directory beneath
the installed package. The server therefore could not start from that launch
declaration. This is an `observed-failed` loader result, not an MCP Apps UI
support conclusion.

Use `cwd: "./"` and package-relative server, renderer and skill paths for this
adapter. The published Agent Plugins MCP schema accepts `./` as the working
directory; it rejects `.`. The staging helper also converts older package
placeholder prefixes before installation. With this declaration, the real
Codex app-server initialized the installed server, returned all five tools,
the UI resource and global/thread entrypoint metadata without a model turn.
An exact-installed subprocess test also rendered Colorset 1, recolored to
Colorset 2 and created a fresh Colorset 1 chart. These are `observed-working`
launch and tool results; desktop component painting remains a separate check.

The direct same-host fallback was subsequently configured as `reflex_xy_local`
with absolute Node, renderer, skill and uv paths, a project-contained runtime,
and the installed bundle as working directory. The actual Settings → Plugins
→ MCPs screen showed the server and a Restart control after Save. Restart
loaded `mcp__reflex_xy_local` in the running conversation. An actual
`xy_render_chart` request returned a Colorset 1 chart, and the native window
showed its genuine XY plot inside the tool component. This is
`observed-working` for direct MCP execution and inline paint, while the
installed folder plugin's own server/entrypoint discovery remains
`observed-failed` in that same app build. It is not evidence of a plan gate or
an unsupported MCP Apps renderer.

The inline `extensions.com.openai` object replaces the compatibility overlay
for OpenAI-specific settings, while root portable components remain canonical.
The [manifest reference](https://developers.openai.com/plugins/deploy/submission#manifest-fields)
explicitly assigns discovery to root `skills/` and `mcp.json`; repeating
`skills` or `mcpServers` inside the inline object cannot alter those portable
components. The [packaging guide](https://developers.openai.com/plugins/build/plugins#add-openai-specific-metadata)
confirms the same distinction. Duplicating those fields is therefore not a
documented repair for this observed Desktop discovery failure. A legacy-only
package would be a separate compatibility experiment, not an established fix.

The current [app-server contract](https://learn.chatgpt.com/docs/app-server#api-overview)
documents `config/mcpServer/reload` for reloading disk configuration and queuing
a refresh of loaded threads. The observed `codex plugin` CLI has no reload
subcommand. A native Plugins refresh, a protocol reload and restarting an
application are separate actions; verify the actual frontend's discovery after
using its supported control.

## Implementation decision

The 0.3.1 UI receives native standalone XY HTML and SVG in app-private result
metadata and embeds the HTML with sandboxed `srcdoc`. It displays an original
SVG data URL if the host prevents child scripts from executing.
The renderer receives only a validated JSON chart grammar. It returns native
SVG and PNG alongside editable Python and the HTML. There is no alternate
JavaScript plotting implementation. An accessible SVG preview and downloads
provide useful output when an embedded interactive frame is unavailable.

The standard MCP Apps SDK handles the host handshake, validated postMessage
transport, size notifications, tool calls and file/link actions. The browser
test uses a protocol host fixture, not the actual ChatGPT account interface.
Remote ChatGPT acceptance requires a reachable HTTPS MCP endpoint and an account
that supports custom MCP connections. The native Desktop route uses local stdio
with no HTTP MCP endpoint or public deployment. The component makes no browser
HTTP(S) requests. Its app-only `xy_get_chart_artifact` returns bounded original
export bytes to standard `app.downloadFile` as an embedded resource. The asset
listener remains optional for direct clients; it is not the preview's transport.
Actual ChatGPT file delivery remains untested. Claude Desktop's native Save
dialog succeeded, with host PNG reencoding but exactly preserved RGBA pixels.
No OpenAI model API calls or API key are involved in deterministic rendering.

The earlier 0.3.0 outer MCP App painted in actual Claude Chat, but its nested
loopback navigation produced `chrome-error://chromewebdata/`. That failed
acceptance remains recorded. The 0.3.1 correction uses genuine XY exports rather
than replacing the plot with another JavaScript chart engine. Preview payloads
above 8 MiB and exports above 16 MiB are rejected; invalid capabilities return
no bytes. Protocol fixtures verify these boundaries with all browser HTTP(S)
requests blocked, but those fixtures do not establish another host's policy.

The advanced JSON editor calls `xy_render_chart` via the standard `tools/call`
UI bridge; palettes call app-only `xy_recolor_chart`. The editable validated
specification is returned in `_meta.spec_json` for the component, while the
structured model output contract remains unchanged. These controls never send
`ui/message`, `ui/update-model-context`, or `sampling/createMessage`. Data/view
changes therefore do not require another model turn. Reference and capability
tools are optional focused aids rather than a mandatory preflight per chart.

## Dependency baseline

Official packages were inspected through npm metadata and their installed type
declarations. `@modelcontextprotocol/sdk` 1.32.1 and
`@modelcontextprotocol/ext-apps` 1.7.5 are compatible according to the latter's
`^1.29.0` SDK peer range. The newer MCP Apps 2.x branch uses separate MCP 2.x
packages; mixing that branch with the v1 SDK is unsupported. The bundled
lockfile preserves the tested compatible graph.

The environment automatically applies an npm package-age cutoff of
2026-10-19. SDK 1.32.2, body-parser 2.4.0 and fast-uri 3.1.9 were newer than
that boundary. The retained audit findings and mitigated parser path are
recorded in the adapter's README; no override bypasses the package-age policy.
