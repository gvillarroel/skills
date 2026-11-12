# Native XY MCP App

Version **0.3.1** defaults every new chart to **Colorset 1**. Colorset 2 remains
available only when the user explicitly requests it or clicks its selector.
An earlier Colorset 2 chart never changes a later chart's default. Omitting
`colorset` always selects `colorset1`, including categorical and multiseries
charts.

The component's own fallback colors also use the canonical Colorset 1 contract:
red active/focus/error states, neutral text and borders, and white/light-gray
surfaces. Host-provided theme variables remain supported. Explicitly selecting
Colorset 2 changes the chart; it does not automatically recolor the component
chrome or change the next chart's default.

The initial component shows the chart, **Save image**, and **More options**,
plus **Expand** only when supported by the host. Saving an image downloads the
original rendered PNG; it does not capture the current browser pan/zoom state.
More options progressively reveals two flat groups: **Display** contains
Palette, View and Show chart tools; **Export** contains a format selector and
one Download button. A separate **Edit chart data** disclosure reveals a JSON
specification editor and **Apply data**. It stays closed until explicitly opened.
Technical counts and engine details remain in structured
tool data and do not appear in the component. Success is quiet; status text
appears only while creating/updating a chart or when an error needs attention.

The app receives the original native HTML and SVG in app-private tool metadata.
It loads that HTML through a sandboxed `srcdoc` frame and the original SVG
through a data URL, without browser requests to localhost or a public server.
A small preview-only CSS rule hides the native `data-xy-slot="modebar"` element.
Native hover, wheel zoom and double-click reset remain available. Show chart
tools reveals the native toolbar without reloading the iframe or changing its
current view; Image offers the native SVG view. A fixed, parent-only boolean
message toggles the preview style and carries no code, HTML or URL commands.
The saved HTML and all original artifacts remain unchanged. If a host blocks
the native child scripts, a readiness timeout shows the original SVG image and
explains how to download the full interactive HTML. Display
and export controls use native labels and selects, plus a disclosure button
with `aria-expanded` and `aria-controls`. Its position stays fixed when the
panel opens. Escape closes More options and returns focus to its button. Mobile targets are at
least 44 pixels high.

This adapter exposes deterministic Python XY charts as MCP tools and a portable
MCP Apps component. It uses the packaged `reflex-xy` skill for chart construction,
styling and export guidance. It requires Node.js 22+, Python 3.11+, and `uv`.
No OpenAI API key is needed: rendering runs locally in Python.
Palette changes and data application call deterministic MCP tools directly;
view, toolbar, export selection and disclosure changes run in the component.
None of these controls sends a chat message, updates model context, requests
sampling, or calls a model API. Familiar chart requests can render directly;
capabilities and focused references are available only when needed.

Use the root project bootstrap/package instructions first so that the adjacent
`runtime/` directory contains `render.py`, `capabilities.json`, and the canonical
skill snapshot. Then run:

```powershell
npm ci --ignore-scripts
npm run check
npm run build
npm test
npm start
```

The default endpoint is `http://127.0.0.1:8787/mcp`. Logs go to stderr. Use
`node dist/server.js --stdio` for an MCP client that starts local processes;
this also starts the local artifact HTTP listener. Do not launch both modes on
the same port. The tools return text and download links even without an MCP Apps
renderer.

The production package also contains `dist/server-bundled.js`, with all Node
runtime dependencies included. Start it with `node dist/server-bundled.js` or
add `--stdio`; this form does not need `node_modules`. Keep `dist/widget.html`
beside it and include `dist/THIRD-PARTY-NOTICES.txt` when distributing either
the server bundle or the widget. The Python runtime and skill remain adjacent
to the `chatgpt/` directory as described above.

## Native Desktop plugin

The root distribution provides portable `plugin.json` and `mcp.json` files for
ChatGPT Desktop and a separate Claude Desktop package. The Node command is:

```text
node chatgpt/dist/server-bundled.js --stdio --desktop
```

`--desktop` requires `--stdio`. It enforces `127.0.0.1` and an automatically
assigned port, ignores inherited public URL/authentication/widget-domain
settings, and exposes only capability-protected artifacts plus local health
status over HTTP. `/mcp` returns 404; all MCP requests travel through the host's
local child-process transport. It needs no public endpoint, tunnel or API key.
Keep `widget.html` and the third-party notices beside the server bundle.

The portable wrapper sets trusted `XY_RENDER_SCRIPT` and `XY_SKILL_DIR` paths
inside its own package. Desktop packages keep the canonical skill at
`skills/reflex-xy/`. Without an explicit `XY_RUNTIME_DIR`, Desktop uses
`reflex-xy` under the operating system's temporary directory rather than writing
into the installed plugin cache. An explicit writable runtime directory wins.

`xy_open_chart_app` is app-only and declares documented global-sidebar and
conversation-side-panel entrypoints. In hosts that expose these entrypoints,
opening **XY charts** invokes the deterministic starter tool and presents a
clearly labeled Colorset 1 sample. No assistant turn is needed for that route.
Open **More options → Edit chart data** to replace the sample JSON and apply
data directly. The last valid chart and its Save image action remain usable
after an invalid input or render failure. App-only recoloring omits a resource
template so its response updates the existing component.

The official ChatGPT documentation supports desktop-only local stdio plugins;
public distribution of local MCP servers currently requires an approved
partner and an organization allowlist. Local marketplace and entrypoint
availability depend on the host/account. A real stdio handshake plus a browser
protocol fixture verifies this implementation, but cannot establish that a
particular ChatGPT or Claude Desktop version permits its embedded child frame
and downloads. Installation and screenshots in each actual host are separate
acceptance checks. The chart remains inside the MCP App. A host without
`downloadFile` receives a clear unsupported-download message; the app does not
attempt to open a loopback URL.

## Remote ChatGPT connection

The remote custom connection flow needs a reachable HTTPS MCP URL. Deploy the packaged server behind HTTPS
or expose its loopback listener through an operator-controlled tunnel. Set
`XY_PUBLIC_BASE_URL` to that public HTTPS origin, without a path. The same origin
serves the native chart HTML and downloads; it must be controlled by the operator.
The MCP App itself needs no network-resource or connection CSP permission.
Its nested frame source is `about:` for the self-contained native HTML.

```powershell
$env:XY_PUBLIC_BASE_URL = "https://xy.example.com"
Remove-Item Env:XY_MCP_BEARER_TOKEN -ErrorAction SilentlyContinue
npm start
```

For a remote host where the process must listen on every interface, also set
`HOST=0.0.0.0` and `XY_ALLOW_PUBLIC_NOAUTH=1`. That explicit development setting
permits anonymous rendering for public, non-sensitive demo data. Apply network rate
limits at the reverse proxy before public exposure.

In ChatGPT's custom MCP/plugin connection flow, enter
`https://xy.example.com/mcp` and choose **No authentication** for this prototype.
ChatGPT does not support a customer-supplied static API key or bearer secret in
place of its OAuth connection flow. Keep `XY_MCP_BEARER_TOKEN` unset for that
anonymous ChatGPT connection. The optional static bearer setting is for MCP
clients that explicitly support request headers; it is not ChatGPT OAuth.
Private production access requires an operator-supplied OAuth 2.1 gateway and
the standard MCP discovery/token-verification flow. This prototype does not
implement that gateway.
The account must support custom MCP connections. Refresh the connection after
changing tool metadata. The current official quickstart describes the connection
flow; account availability is determined by ChatGPT. A local build or host mock
does not install the connector in a user's account.

For public submission with UI, configure a dedicated component origin through
`XY_WIDGET_DOMAIN` and complete the platform's review process. This component
embeds the server's own chart HTML to preserve XY's native renderer, hover, pan
and zoom. The official iframe policy requires a submission justification and
can require additional review. See the exact documentation links in
`../notes/chatgpt-sources.md`.

## Tools and user flow

- `xy_capabilities`: obtain the authoritative allowlist, limits and examples.
- `xy_get_reference`: read the workflow or a focused bundled skill reference.
  Use topic `interaction` for the conditional progressive-disclosure guidance;
  the reference allowlist also includes colorsets, recipes, advanced, exports
  and live, without accepting arbitrary file paths.
- `xy_render_chart`: accept `spec_json`, a bounded JSON chart specification;
  produce HTML, SVG, PNG, editable Python and JSON input.
- `xy_recolor_chart`: app-only regeneration of an existing chart with Colorset 1
  or Colorset 2; it requires the opaque capability held by that widget.
- `xy_open_chart_app`: app-only global/thread entrypoint with a labeled Colorset 1
  sample; no model request or chart arguments are required.
- `xy_get_chart_artifact`: app-only original export reader requiring the chart's
  opaque capability. Its base64 file bytes stay in app-private metadata.

Example tool argument:

```json
{
  "spec_json": "{\"preset\":\"line\",\"colorset\":\"colorset1\",\"title\":\"Quarterly trend\"}"
}
```

Ask the assistant to use actual supplied data through the generic contract
returned by `xy_capabilities`. Preset defaults are explicitly synthetic samples.
The widget displays the native HTML in a sandboxed frame and offers a native SVG
preview. Palette switching calls the MCP server with the same specification and
is an explicit choice for that chart only. A new specification starts in
Colorset 1.
Downloads call the app-only export reader, then pass an embedded resource to
the standard host-mediated `ui/download-file` capability. The host receives
the original bytes and never needs to fetch a localhost file. UI size changes use the official
MCP Apps SDK's ResizeObserver bridge. Rendering errors keep the previous chart
available and display an accessible message.

## Runtime configuration

| Variable | Purpose |
| --- | --- |
| `PORT` | HTTP port, default `8787`. |
| `HOST` | Listen address, default loopback `127.0.0.1`. |
| `XY_PUBLIC_BASE_URL` | Public HTTP(S) origin used in optional artifact links. Embedded app previews and exports do not fetch those links. |
| `XY_MCP_BEARER_TOKEN` | Optional transport bearer secret for compatible MCP clients, not the ChatGPT prototype connection. Public bind requires this or explicit anonymous-demo opt-in. |
| `XY_WIDGET_DOMAIN` | Optional dedicated UI origin for a production submission. |
| `XY_RUNTIME_DIR` | Writable ephemeral artifact directory; Desktop defaults to the OS temporary directory's `reflex-xy/`, other modes to `.runtime/`. |
| `XY_RENDER_SCRIPT` | Trusted operator path to `runtime/render.py`. |
| `XY_SKILL_DIR` | Trusted operator path to the bundled `reflex-xy` skill. |
| `XY_PYTHON` | Optional prepared Python executable; bypasses `uv run`. |
| `XY_UV_BINARY` | Trusted `uv` executable, default `uv`. |
| `XY_BUILD_DIR` | Optional candidate build/output directory, also read by source-mode server and test runners. Production bundles normally use their adjacent `dist/`. |

The MCP endpoint validates origin and host, rejects compressed bodies, and limits
request size. A render accepts no filesystem paths, URLs or executable code.
The Python renderer independently validates the chart grammar. It runs through
an explicit argument vector, with a 90 second timeout and bounded output.
At most two renders run at once. Stored charts have a 20 minute lifetime;
the cache holds at most 40 records, with a 256 MiB eviction budget and a
64 MiB per-chart bundle limit. Eviction invalidates old links.
Embedded previews have an 8 MiB combined HTML/SVG limit; each embedded export
has a 16 MiB decoded-byte limit. Both are checked before returning app data.

Artifact URLs contain a random render ID plus a 256-bit capability token. They
are bearer links: anyone holding one can read that chart until expiry or server
restart. Keep them out of public logs. There is no directory listing or arbitrary
file route. Files live in fresh task directories under the configured runtime
root. Runtime storage is ephemeral and is not a durable private account store.
Expiry immediately invalidates links; a later render prunes expired records.
Files left by a stopped process may remain in the runtime directory and require
operator cleanup. The stated cache limits apply to the current server process.
For a multi-tenant service, add authenticated user ownership and durable storage
before using private organizational data.

## Validation

```powershell
npm run check
npm test
npm run build
npm run test:browser
npm run test:desktop
npm run test:fallbacks
npm run test:bundled
```

The browser test runs the actual MCP HTTP server and Python XY renderer,
initializes the official MCP Apps bridge in a protocol host fixture, switches
both palettes, loads native HTML and SVG, downloads a file through the bridge,
checks mobile overflow and records screenshots. Set `PLAYWRIGHT_CHANNEL=chrome`
if Microsoft Edge is unavailable, or install Playwright Chromium and change
the test's launch configuration. Test output goes under the project's ignored
`artifacts/` directory. These tests do not establish acceptance inside the actual
ChatGPT client.

The Desktop browser test runs the same component against a real bundled stdio
child process with hostile inherited public-hosting settings and no model API
keys. It checks the app-only launcher, loopback-only artifact links, absent HTTP
MCP endpoint, exact edited data, invalid-input recovery, both palettes, and the
bridge call sequence. It asserts zero `ui/message`, `ui/update-model-context`,
and `sampling/createMessage` calls. All browser HTTP(S) requests are blocked;
the fixture verifies native `srcdoc` paint, data-URL SVG, and all five original
embedded exports. The constrained-host fixture separately blocks child scripts
and omits download support, checking the image fallback and clear error.
The compact preview and all output files
still use native XY rendering. Reports are stored in separate versioned folders.

The bundled stdio test copies the production JavaScript and widget to an
isolated folder without `node_modules` in its ancestry, then starts a real MCP
client, inspects capabilities and generates/downloads native HTML, SVG and PNG.
The root package validation additionally checks the extracted distribution's
bundled skill snapshot and runtime paths.

Pinned MCP SDK 1.32.1 and MCP Apps 1.7.5 use the compatible v1 server interface
documented by the official quickstart. The environment's package age cutoff
prevented installing SDK 1.32.2. The initial dependency audit reports advisories
in transitive `body-parser` and `fast-uri`; fixed versions were published after
that cutoff. This implementation uses `node:http` with its own bounded JSON
parser and passes parsed bodies to the MCP transport; it does not invoke Express
or `body-parser`. Re-evaluate the lockfile when those security updates become
available under the installation policy.
