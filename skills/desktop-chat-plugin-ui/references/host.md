# Claude Desktop Chat routes

Source review: November 11, 2026. Recheck the requested build before deployment.
Ordinary Chat can render an MCP App supplied by a connected MCP server. The
Desktop Code tab uses a different plugin runtime. A plugin package's local MCP
server and a Desktop local-server connector have distinct loading routes.
[MCP App quickstart](https://claude.com/docs/connectors/building/mcp-apps/getting-started),
[plugin surface support](https://support.claude.com/en/articles/13837440-use-plugins-in-claude).

## Local and remote transport

For local Desktop Chat, configure the requested stdio entry under `mcpServers`
or package it as an MCPB Desktop Extension. Include the declared executable,
runtime dependencies, paths, and only necessary typed `user_config` fields.
Keep secrets in sensitive configuration rather than source. Validate/pack with
the matching MCPB CLI and launch the extracted bundle before claiming it works.
The installer settings form is separate from the runtime App.
[Local extensions](https://support.claude.com/en/articles/10949351-getting-started-with-local-mcp-servers-on-claude-desktop),
[MCPB manifest](https://github.com/modelcontextprotocol/mcpb/blob/main/MANIFEST.md).

A remote connector must be reachable from Anthropic infrastructure; localhost
or VPN success on the user's machine does not establish this. Keep remote
deployment within the requested scope. For the documented remote `ui.domain`,
hash the exact full configured URL with SHA-256, take the first 32 hexadecimal
characters, and append `.claudemcpcontent.com`. A trailing slash changes the
value. Omit this URL-derived field for local stdio; there is no URL to hash.
[Troubleshooting](https://claude.com/docs/connectors/building/mcp-apps/troubleshooting#ui-domain-validation-fails).

## Placement and acceptance

Current documentation includes inline UI, side-panel/fullscreen flows, and app
entry points. Confirm the exact metadata and negotiated capabilities before
using a placement; do not infer arbitrary sidebar or host DOM insertion.
[Display modes](https://claude.com/docs/connectors/building/mcp-apps/display-modes),
[entry points](https://claude.com/docs/connectors/building/mcp-apps/entry-points).

Inherited historical observation: Claude Desktop Chat 3.6556.2 on Windows,
October 24, 2026, completed local stdio initialization, resource read, iframe
paint, direct tools, and fullscreen on a signed-in Free account. This bounded
observation does not establish current account enablement, remote transport,
MCPB installation, Code/Cowork/mobile, or every optional browser feature.
Reproduce the requested route and record actual permission, paint, keyboard,
resize, cancel/recovery, reopen, and tool dispatch separately.

Additional bounded observation: Claude Desktop 5.1231.2 on Windows,
November 12, 2026, rendered a fresh call through an already installed Reflex XY
local stdio connector on a signed-in Free account using Haiku 5.5 Medium. The
24-hour latency plot and separate objective series painted, the lower-right
legend left the endpoint clear, the host opened its fullscreen region, and
closing it returned to inline. Native screenshots were retained locally. This
does not establish installation of another MCP package, remote transport,
Desktop Code access or every optional MCP Apps action. A native capture must
be unobscured; bring the authorized target forward before recording evidence
when the capture backend includes occluding windows.
