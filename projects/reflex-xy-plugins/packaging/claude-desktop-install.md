# Reflex XY for Claude Desktop chat

This desktop extension connects the same MCP Apps component and native Python
XY renderer to Claude Desktop's ordinary chat. It is separate from the Claude
Code Mod. Both colorsets, the 36 presets, generic declarative chart construction,
native previews and HTML/SVG/PNG/Python/JSON exports use the bundled runtime skill.

Install `uv` and make Python 3.11+ available on the computer running Claude.
Open `reflex-xy-claude-desktop.mcpb` with Claude Desktop, review its local tool
permissions and install the extension. If `uv` is not on the Desktop process's
PATH, set the extension's uv executable configuration to its absolute path.
The host provides Node for the packaged JavaScript server. XY dependencies are
resolved through `uv` on first use; the extension does not bundle a Python runtime.

Enable the extension in the chat's connectors/tools menu. Ask Claude to render
your actual data directly with `xy_render_chart` for a familiar request. Use
`xy_capabilities` or one focused reference only for an unfamiliar contract. The first view prioritizes the chart and Save image.
Open More options for display choices, chart tools and other export formats.
Every new chart uses Colorset 1 by default; Colorset 2 requires
an explicit request or palette selection. Multiple categories and prior palette
choices do not change that default. A sample chart request is `{"preset":"line"}`
inside the tool's `spec_json` string. Preset defaults are synthetic examples.

The local server uses stdio for MCP and a dynamically assigned loopback HTTP
port for optional artifact links. The actual component receives original XY
HTML/SVG in app-private metadata and uses a sandboxed local document. Original
exports use the host download bridge; no browser HTTP asset access is needed. Artifacts have random capability URLs, a 20 minute
lifetime and a bounded cache per server process. Links stop working on expiry
or restart; download anything you want to keep. Expired files are pruned on a
later render, and files left by a stopped server may remain in your selected
directory until you remove them. No OpenAI API key, public hosting or HTTPS
tunnel is needed for this local extension.

Actual Claude Chat passed integrated painting, fullscreen, explicit CS2, PNG
saving and exact data edits while retaining the same two conversation messages.
The host reencoded its saved PNG but preserved identical RGBA pixels. A manual
configuration-file setup can use the extracted bundle's absolute Node command,
`chatgpt/dist/server-bundled.js --stdio --desktop`, renderer at
`runtime/render.py`, and skill at `runtime/skill/reflex-xy`. Merge one MCP server
entry, preserve existing connectors, then fully quit and reopen Claude.

Extension-install UI and account policy still require the user's
Desktop application. A validated archive and a real stdio/browser protocol test
do not by themselves establish that account-level installation has happened.
