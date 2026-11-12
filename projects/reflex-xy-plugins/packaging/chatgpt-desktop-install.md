# XY Charts in ChatGPT Desktop

This is a local desktop plugin with a bundled MCP Apps component. It is not a
standalone browser preview. Requirements: Node.js 22+, `uv`, and a current
ChatGPT desktop app with local plugin support. No OpenAI API key, bearer token,
public server, tunnel, or remote hosting is required by this package.


## Verified direct local MCP connection

The observed Desktop build installed the folder plugin's skill but did not
start its bundled MCP server. Direct same-host MCP configuration resolved this
discovery failure and painted the actual chart. Extract the ZIP to a permanent
folder, then use Settings → Plugins → MCPs → Add → STDIO (some versions label
this Settings → MCP servers).

| Setting | Value |
| --- | --- |
| Name | `reflex_xy_local` |
| Command | Absolute path to the installed Node executable |
| Arguments, one per entry | `<bundle>/chatgpt/dist/server-bundled.js`, `--stdio`, `--desktop` |
| Working directory | Absolute path to the extracted bundle |
| `XY_RENDER_SCRIPT` | `<bundle>/runtime/render.py` |
| `XY_SKILL_DIR` | `<bundle>/skills/reflex-xy` |
| `XY_UV_BINARY` | Absolute path to the installed uv executable |
| `XY_RUNTIME_DIR` | Absolute writable artifact folder outside the bundle |
| `PYTHONIOENCODING` | `utf-8` |
| `PYTHONDONTWRITEBYTECODE` | `1` |

Replace `<bundle>` with a real absolute path; it is explanatory notation, not
an environment variable. Save the server, then select **Restart** in the server
list. This reloads MCP configuration. The plugin directory's Refresh action
updates its catalog. Use `/mcp` to inspect connections. The official
`codex mcp add` command can register the same settings in shared
`~/.codex/config.toml`; preserve existing server entries.

Keep one active XY route if the plugin's bundled server later starts. Portable
root `mcp.json` and `skills/` are canonical; duplicating their declarations in
`extensions.com.openai` does not repair discovery. The package uses `cwd: "./"`
and relative paths for Codex 0.145, which left `${PLUGIN_ROOT}` literal.

Sources: [local MCP configuration](https://learn.chatgpt.com/docs/extend/mcp)
and [canonical portable components](https://developers.openai.com/plugins/deploy/submission#manifest-fields).

## Optional local marketplace route

1. Extract this ZIP to a permanent local folder. Keep `plugin.json`, `mcp.json`,
   `skills/`, `runtime/`, and `chatgpt/` together.
2. Add the folder to a repository or personal plugin marketplace. The repository
   helper can stage a test using only files inside this repository:
   `uv run --script projects/reflex-xy-plugins/scripts/stage_desktop_demo.py --release-dir <release-directory>`.
3. Restart ChatGPT Desktop, choose the local marketplace in Plugins, and review
   and install **XY Charts**. Use a local conversation. Account or managed
   policies may restrict local plugins.
4. Ask for one familiar chart directly with `xy_render_chart`, or invoke the tool through a host-supported tool
   test interface. Confirm that the result component appears in the conversation,
   rather than opening `chart.html` in a browser tab.
5. Use More options for palette and export controls. These controls call the
   local server directly and do not submit another model message. Rendering,
   hover, zoom, view changes and downloads do not call a model API.

The first natural-language request still uses the host's assistant. Generating
that request is distinct from the deterministic Python render and subsequent
UI interactions. Do not claim zero total conversation tokens.

Every new chart defaults to Colorset 1. Colorset 2 requires an explicit request
or selection. The server uses stdio and an ephemeral loopback listener for
optional capability-protected links, with no public MCP endpoint. Original
XY HTML/SVG travel in app-private metadata and a sandboxed local document.
Host-mediated exports use MCP bytes; neither flow fetches loopback HTTP assets.
Local records
expire after 20 minutes. Save downloads to keep them.

Both portable and Codex compatibility manifests are included. Actual ChatGPT
inline painting passed through the direct MCP route above. Installed-host
control actions and global/thread launchers remain separate acceptance checks. A schema or protocol test does not prove
that a component has appeared in a real conversation.

Sources: [local plugin packaging](https://developers.openai.com/plugins/build/plugins#install-a-local-plugin-manually),
[desktop stdio plugins](https://developers.openai.com/plugins/deploy/desktop-only),
and [MCP Apps UI](https://developers.openai.com/plugins/build/chatgpt-ui).
