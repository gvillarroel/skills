# Reflex XY for ChatGPT

This package contains an MCP server, a portable MCP Apps component, the Python
XY renderer and the canonical `reflex-xy` runtime skill. Requirements: Node.js
22+, `uv`, and Python 3.11+. Rendering needs no OpenAI API key.

Extract the ZIP and run the prebuilt, self-contained Node server from its root:

```powershell
node chatgpt/dist/server-bundled.js
```

No npm installation is needed for this prebuilt entry point. The local endpoint is
`http://127.0.0.1:8787/mcp`. The first render may download XY 0.0.8 through `uv`.

The remote ChatGPT route requires a reachable HTTPS MCP endpoint. Configure an
HTTPS reverse proxy or operator-controlled tunnel for `/mcp`, set the public
origin, then start the server. Integrated previews and host-mediated downloads
do not require exposing `/artifacts/`; those routes serve optional links only:

```powershell
$env:XY_PUBLIC_BASE_URL = "https://xy.example.com"
node chatgpt/dist/server-bundled.js
```

For a demonstration with non-sensitive sample data, enter
`https://xy.example.com/mcp` in ChatGPT's custom MCP/plugin connection flow and
select **No authentication**. Leave `XY_MCP_BEARER_TOKEN` unset for that flow.
The account must support custom connections.
The example domain is a placeholder; this archive does not create hosting or
install a connection in an account. For a direct public bind, set `HOST=0.0.0.0`
and `XY_ALLOW_PUBLIC_NOAUTH=1` explicitly for this sample-data demonstration.
Use a supported OAuth gateway before deploying for private remote use. The
server's optional static bearer secret is for compatible MCP clients; ChatGPT's
documented custom connection flow does not offer static bearer authentication.

Once connected, ask: “Use XY to plot these measurements in Colorset 1 and let me
switch to Colorset 2.” Familiar requests can call `xy_render_chart` directly
with `spec_json`. Read `xy_capabilities` or one focused reference only for an
unfamiliar chart contract. The initial view
shows the chart and Save image. More options exposes display choices, chart
tools, other export formats and the JSON data editor. Original XY HTML/SVG
travel in app-private metadata; the preview makes no browser HTTP requests.
Original exports use the host download bridge. Controls do not send a model
message or update model context. Chart records and optional download links
expire after 20 minutes or server restart.

Every new chart defaults to Colorset 1. Colorset 2 requires an explicit user
request or palette selection; previous charts and category count do not change
the default. A full example with sample data is:

```json
{"spec_json":"{\"preset\":\"scatter\",\"colorset\":\"colorset1\"}"}
```

See `chatgpt/README.md` for configuration, tests, privacy limits, dependency audit
notes and public-submission iframe review. Local MCP/browser tests establish
protocol behavior; activation in a real ChatGPT account remains a separate step.
