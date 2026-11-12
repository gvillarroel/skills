# Reflex XY in Claude and ChatGPT

The project provides four adapters for the existing canonical `reflex-xy` skill:

| Package | Target interface | Rendering and connection |
| --- | --- | --- |
| `reflex-xy-claude-code.zip` | Claude Code CLI, VS Code, Desktop Code tab | Native Mod with SVG/PNG preview, local Python process. |
| `reflex-xy-claude-desktop.mcpb` | Claude Desktop ordinary chat | Local stdio MCP server and an MCP Apps component; installable desktop extension. |
| `reflex-xy-chatgpt-desktop.zip` | ChatGPT desktop local conversation | Portable plugin with a bundled local stdio server and MCP Apps UI; no public server or API key. |
| `reflex-xy-chatgpt.zip` | ChatGPT web custom MCP/plugin connection | MCP Apps component and Streamable HTTP server; requires a reachable HTTPS MCP endpoint. |

Source lives in [projects/reflex-xy-plugins](../projects/reflex-xy-plugins/README.md).
Every package copies the current skill runtime from `skills/reflex-xy`; it excludes
acceptance galleries, caches and dependency directories. No OpenAI API key is
required for native chart generation. All adapters use Python XY 0.0.8 rather
than recreating charts with a JavaScript plotting library.

Every new chart defaults to **Colorset 1**, including after a previous Colorset 2
chart. Use Colorset 2 only when the user explicitly requests or selects it.
Multiple categories do not change the default. This policy is shared by the
skill, tool instructions, omitted JSON palette fields and fresh Code commands.

The current distribution is **0.3.2**, containing the unchanged **0.3.1 MCP
runtime**. Version 0.3.2 updates installation guidance and distribution metadata;
it does not claim a new installed-host execution. Actual Claude Desktop Chat paints
the embedded chart and supports its local controls. ChatGPT Desktop paints the
same component through a directly configured local MCP server after a server
restart. Its installed folder plugin is recognized, but the bundled-server
discovery route did not expose the tools in the tested app build. The direct
connection is an observed workaround; it does not establish that the bundle's
sidebar entrypoint works. Claude Desktop Code still stops at its access screen.
See the [current installed-host evaluation](../evaluations/reflex-xy/native-desktop-20261025.md)
for the separate installation, paint, control and account results.

## Interaction model

The initial view focuses on the chart and one primary action. Both the MCP
component and native Code pane offer Save image. More options reveals display
and export choices; the Code pane keeps interactive HTML opening there because
its native pane paints an SVG/PNG preview.
Fullscreen appears only when the host supports it. Developer badges, mark/factory
counts, repeated titles and permanent success explanations are absent.

The MCP display group contains palette, interactive/image view and chart tools.
The export group provides one format selector and one Download action rather
than a row of format buttons. Toolbars are initially hidden only in the compact
embedded preview; hover/navigation remain available and original downloaded
HTML keeps its native controls. Showing chart tools does not reload the chart
or discard its zoom. Image downloads use the original rendered view; use the
native chart tools when working with its browser viewport.

The Code pane groups palette, explicitly labelled sample replacement, rerender,
image opening and editable artifact paths inside its options area. It preserves
the displayed successful data when editing a palette, including after a later
request fails. Closing options retains selections. Loading and actionable errors
appear when relevant, with the previous valid chart still available.

## Local desktop workflow and model usage

The ChatGPT Desktop package declares `xy_open_chart_app` as an app-only tool
with documented global and thread entrypoints. Compatible hosts can launch it
from their sidebar or conversation panel without an assistant request. It opens
a clearly labelled Colorset 1 sample. Its advanced data editor calls the local
render tool directly. Palette, view, tools and export controls do not submit a
chat message or update model context. A natural-language chart request still
uses the assistant; do not claim zero total conversation tokens.

The Claude Code Mod opens through `/xy-chart line`, executes Python locally,
and uses native controls. Save image copies the actual PNG bytes to a unique
project-local `.xy-charts/exports/` file without replacing an existing export.
Model completion and prompt submission are not part of these control paths.
Full XY browser interactions remain an optional HTML export; a native SVG
preview is not a DOM/WebGL application container.

The desktop server runs with `--stdio --desktop`. It ignores inherited public
endpoint settings, binds assets to an ephemeral loopback port and exposes no
HTTP MCP endpoint. The 0.3.1 component receives the original XY HTML and SVG in
app-private tool metadata, paints the interactive HTML in a sandboxed `srcdoc`
frame, and saves exports through the host's file bridge. It makes no browser
request to the asset listener. Loopback links remain available for compatible
direct clients. No authentication token or model API key is needed. The random
capability protects a chart record; it is not a billable model token.
Dependencies may download on the first render.

Opening `chart.html` in the built-in browser does not establish integrated
component acceptance. A protocol fixture also does not establish production
host permissions, visible paint or delivery of a saved file.

The reusable recipe is bundled in the skill's interaction-design reference.
[Research sources and design decisions](../projects/reflex-xy-plugins/notes/interaction-sources.md)
distinguish the adopted progressive-disclosure pattern from measured application
behavior. No user profiling or forced onboarding is required.

## Build

Requirements are Node.js 22+, `uv`, and Python 3.11+. From the repository root:

```powershell
Push-Location projects/reflex-xy-plugins/chatgpt
npm ci --ignore-scripts
npm run check
npm test
npm run build
Pop-Location
uv run --script projects/reflex-xy-plugins/scripts/build_plugins.py --desktop --output-dir projects/reflex-xy-plugins/artifacts/releases/0.3.2
```

The output directory must be new. The builder preserves previous builds, copies
the native renderer and exact skill runtime, writes per-file SHA-256 inventories,
and creates three ZIPs and one MCPB. Generated packages stay under ignored project
artifacts; source and compact evidence remain versioned. Each package includes
an `INSTALL.md`. The Desktop extension uses a standalone server bundle, its
third-party notices and a root `type:module` declaration, without `node_modules`.
The optional `--app-dist <validated-build-directory>` selects a separately
validated candidate build without replacing the default build output.
Distribution and bundle metadata declare `mcp_runtime_version: "0.3.1"` for the
MCP adapters. Their server/widget bytes and the Python/skill runtime match the
tested 0.3.1 release. Code's bundle has no MCP server and records that field as
null. Preserve this distinction when checking health/version responses.

## Install the local ChatGPT Desktop plugin

The portable ZIP contains root `plugin.json`, `mcp.json`, `skills/`, a bundled
server and its native Python runtime. A compatibility manifest is included for
Codex plugin loaders. Keep every file together when extracting.

For repository-local testing, stage both desktop adapters without writing global
configuration:

```powershell
uv run --script projects/reflex-xy-plugins/scripts/stage_desktop_demo.py --release-dir projects/reflex-xy-plugins/artifacts/releases/0.3.2
```

The helper verifies exact release inventories, configures absolute Node/uv paths
and package-relative runtime paths in its test copy, preserves unrelated
marketplace entries and writes `.agents/plugins/marketplace.json`. It is a fresh
staging operation and refuses an existing `reflex-xy` entry; preserve the prior
stage when reviewing an upgrade. Select **XY Desktop Local** in Plugins and
review installation. Staging a marketplace does not install or trust a plugin.
The installed Codex 0.145.0 loader needs `cwd: "./"` and relative bundle paths:
it left `${PLUGIN_ROOT}` literal in the earlier declaration.

Check whether the tool and the app entrypoint are actually exposed. **Refresh**
in Plugins updates the catalog; it is distinct from restarting MCP servers.
In the tested ChatGPT Desktop build, the folder plugin appeared as installed
without exposing its bundled server. The supported local fallback is
**Settings → Plugins → MCPs**: register the packaged `server-bundled.js` with
absolute Node, renderer, skill and uv paths, `--stdio --desktop`, and a writable
project runtime directory. Save the configuration, then select **Restart** in
the MCP server list. The [official MCP setup](https://learn.chatgpt.com/docs/extend/mcp)
also documents `codex mcp add` and the shared same-host configuration file.
This route loaded `reflex_xy_local` and rendered the component inside the
actual conversation. Its global/sidebar placement remains separately untested.

The same helper prepares an exact Claude plugin under a dedicated workspace's
`.claude/skills/reflex-xy`. Open that exact workspace in a local Desktop Code
session; workspace trust and account access remain host-controlled prerequisites.

## Install in Claude Desktop chat

Open the MCPB with a current Claude Desktop, review its local tools and install
the extension. Select a writable temporary chart directory. Install `uv` first;
configure its absolute executable path when Desktop cannot find it on PATH.
The host supplies Node and `uv` manages the pinned Python chart environment.

Enable the extension in the chat's connector/tool menu. Render familiar chart
requests directly with `xy_render_chart`; read `xy_capabilities` or one focused
reference only when the required data contract is unfamiliar.
The standard MCP Apps component offers both palettes, native HTML and SVG
previews, and downloadable artifacts. It leaves `ui.domain` unset, as required
for a local stdio connector. MCP carries the self-contained preview and original
export bytes; the component does not navigate to a loopback iframe. No public
endpoint is needed. This transport correction resolved the actual blank-frame
failure in Claude Desktop 3.6556.2. Its native file dialog may reencode PNG
metadata or compression: the saved image retained exactly equal RGBA pixels in
the installed-host check.

Claude Desktop supports interactive connectors through MCP Apps. The Code Mod
uses a different extension interface and does not run as a regular claude.ai
web-chat plugin. See the checked [Claude primary sources](../projects/reflex-xy-plugins/notes/claude-sources.md).

## Install in Claude Code

Extract the Code ZIP to a permanent location and launch Claude from your working
project with `claude --plugin-dir <extracted-folder>`. Run `/xy-chart`,
`/xy-chart colorset2 scatter`, or `/xy-chart sankey`. The preset selector exposes
all 36 presets. For actual data, use the `render_chart` tool or
`/xy-chart @charts/request.json` with a project-relative JSON file.

In Desktop, use a **Local** project (installed plugins are also supported for
SSH sessions; cloud and WSL sessions have different plugin availability). If
plugin changes are pending, type `/reload-plugins` directly into that Code
session, then run `/xy-chart line`. The Desktop reload command does not apply
plugin MCP-server changes. This native command path does not require an
assistant completion. See the official [Desktop plugin scope](https://code.claude.com/docs/en/desktop)
and [command reference](https://code.claude.com/docs/en/commands).

The plugin loads TypeScript through Claude's native Mods runtime and invokes
`uv` through a fixed argument vector with JSON on stdin. Its Desktop Code/VS Code
path uses native SVG; a compatible terminal gets PNG. This is the declared and
native-engine-tested implementation. The installed Desktop Code pane remains
unverified: the last Code-pane observation displayed **Get Claude Code** before
project access. A fresh CLI re-audit confirmed the user-scope plugin is still
enabled and signed-out CLI authentication; CLI status does not diagnose the
current Desktop account tier or prove that its earlier gate is still present.
The pane's Open interactive chart button
opens the full browser interactions. Artifacts remain in the project's
`.xy-charts/` directory. Python source paths can be copied without launching
the source through an executable file association.

## Connect ChatGPT

Extract the ChatGPT ZIP and start the self-contained entry point:

```powershell
node chatgpt/dist/server-bundled.js
```

It listens on `http://127.0.0.1:8787/mcp`. An operator-controlled HTTPS proxy or
tunnel must expose the MCP endpoint. Set
`XY_PUBLIC_BASE_URL=https://your-controlled-origin.example` before starting it,
and expose `/artifacts/` as well when direct download links are needed. The
0.3.1 component's embedded preview and host-mediated exports do not fetch those
routes; the reachable origin serves textual/direct-client links.

For a demonstration with non-sensitive sample data, leave
`XY_MCP_BEARER_TOKEN` unset and select **No authentication** in ChatGPT's custom
connection flow. If binding directly on every interface, explicitly set
`HOST=0.0.0.0` and `XY_ALLOW_PUBLIC_NOAUTH=1`. For private remote deployment,
put the server behind a supported OAuth gateway. The bundled static bearer
option serves compatible MCP clients; ChatGPT documents OAuth, no authentication,
and mixed OAuth/no-auth connection options, rather than a static bearer setting.

Open ChatGPT's Plugins page and follow the
[official connection steps](https://developers.openai.com/plugins/build/app-quickstart)
to add a custom MCP server using the HTTPS `/mcp` URL, review it and install it.
Refresh tool metadata after
server changes. Account/workspace permission is required. The rendering service
does not create account connections or public hosting on its own. The checked
[OpenAI sources](../projects/reflex-xy-plugins/notes/chatgpt-sources.md) describe
the current flow and own-domain iframe submission policy.

Secure MCP Tunnel is another supported transport for private MCP calls, but
requires a Platform tunnel, runtime API key and workspace association. It does
not automatically proxy separate artifact routes. The embedded 0.3.1 component
does not require those routes, but actual tunnel/account acceptance was not
tested in this release.
See the [official tunnel guide](https://developers.openai.com/api/docs/guides/secure-mcp-tunnels).

## Chart contract

The shared engine supports 36 presets, 28 public chart factories, 22 marks and
23 components. `xy_capabilities` returns the exact names, data columns, generic
descriptor grammar, limits and palette tokens. Preset requests use synthetic
defaults only when `data` is omitted. Supplying `data` requires every documented
column; unknown columns fail rather than being silently discarded.

For example, `xy_render_chart` accepts this MCP argument:

```json
{"spec_json":"{\"preset\":\"line\",\"title\":\"Measured response\",\"colorset\":\"colorset1\",\"data\":{\"x\":[0,2,5,9,14],\"y\":[4,7,3,11,8]}}"}
```

The Claude Code tool accepts the same inner object as its `spec` argument.
Both MCP adapters expose `xy_get_reference` for focused skill instructions;
Claude Code exposes `skill_reference`. A generic chart can combine named-column
marks, axes, annotations, legends, tooltips, interaction controls and export
settings using allowlisted public XY constructors. Colorset tokens resolve
through the canonical skill's palette helper. Explicit requested colors remain
explicit; native interpolation/alpha and funnel contrast exceptions are reported.

Every successful render generates `chart.html`, `chart.svg`, `chart.png`,
`chart.py` and `spec.json`. The Python file embeds its data, theme and narrow XY
SVG compatibility repair; it can regenerate all three formats without the
plugin or repository. Standalone HTML preserves enabled browser interactions.
Python callbacks, custom registered code and future streamed data require a
live Python host and are outside the declarative tool contract.

## Verification and limits

Run the native Claude scanner and tests against an extracted Code package:

```powershell
claude plugin validate <package-directory> --strict
claude plugin test <package-directory>
```

From the ChatGPT source directory, run `npm run check`, `npm test`,
`npm run test:browser` and `npm run test:bundled`. The browser tests use the
official MCP Apps protocol with real MCP HTTP and native Python charts; the
standalone test uses real SDK stdio without a dependency directory. Independent
tests under the project exercise all presets, native exports, paired palettes,
supplied measurements, injection controls, mobile rendering and archive isolation.

The [original release evaluation](../evaluations/reflex-xy/plugins-20261024.md),
[Colorset 1 default revision](../evaluations/reflex-xy/default-colorset1-20261024.md),
[progressive controls revision](../evaluations/reflex-xy/progressive-controls-20261024.md) and
[native desktop release](../evaluations/reflex-xy/native-desktop-20261024.md) and
[installed-host follow-up](../evaluations/reflex-xy/native-desktop-20261025.md) record
the exact commands, retained failures, corrected subjects and observed outcomes.
The follow-up establishes actual Claude Chat paint and controls, and actual
ChatGPT tool execution and component paint through direct local MCP setup.
ChatGPT controls and direct entrypoints remain untested in the installed host;
the Code access gate remains. Protocol/native CLI results are reported
separately and do not fill those remaining acceptance gaps.

MCP charts use random capability URLs, expire after 20 minutes and are kept in
bounded storage per server process. Expiry invalidates links immediately; a later
render prunes expired records. Files left by a stopped server may remain in its
runtime directory until removed. There is no durable account ownership store. Native
Code artifacts stay in the project until removed. The dependency notes retain
unavailable transitive security updates and describe the bounded parser path;
revisit the lockfile when the environment's package-age policy permits updates.

[Back to the documentation index](README.md).
