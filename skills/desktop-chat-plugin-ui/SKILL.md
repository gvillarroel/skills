---
name: desktop-chat-plugin-ui
description: Creates, improves, packages, and validates MCP App interfaces for ordinary Claude Desktop Chat, including local MCP servers and optional MCPB extensions. Use for interactive connectors, forms, charts, or installation diagnosis in Claude Desktop Chat; the Code tab uses a separate native runtime.
---

# Claude Desktop Plugin UI

Start with the pending human decision. Read
[micro-decisions.md](references/micro-decisions.md) for the default agent UI:
one bounded question, only decision-relevant evidence, and a typed result
returned to the agent. Use a full workspace only when the user requests it.

For graphs, charts, dense tables, or linked multi-panel interfaces, read
[rich-interfaces.md](references/rich-interfaces.md) before choosing the layout.
Apply its graph/chart recipes, host alternatives, state rules and pixel critique.

For coordinated investigations, dense matrices and reviewed actions, read
[complex-workspaces.md](references/complex-workspaces.md).

Build for ordinary Claude Desktop Chat. Identify Chat versus the Code tab
before choosing a runtime. Use [host.md](references/host.md) for transport,
packaging, current source links, and inherited evidence. Do not load a native
Claude Code Mod to supply a Chat iframe.

1. Define one complete user task and choose useful text/tools first. Add an MCP
   App when inspection or interaction benefits from UI.
2. Follow [mcp-apps.md](references/mcp-apps.md) for resources, the bridge, direct
   actions, and state. Keep host-dependent metadata in this adapter.
3. Use local stdio for local-only Desktop work. Add MCPB only when an installer
   or typed installation settings are requested. Test the extracted package.
4. Apply [interaction-quality.md](references/interaction-quality.md), including
   English copy, Nielsen H1-H10, owned palettes, and host theme boundaries.
5. Verify server, bridge, and browser behavior. Then verify actual Desktop
   resource delivery, paint, and interaction when the host is available and
   installation is authorized. Preserve unperformed checks as `untested`.

Produce runnable sources, dependency metadata, the requested package or local
configuration, exact output paths, and concise setup/test notes. Keep consent,
account policy, and remote reachability distinct from layout failures. A browser
pass alone does not establish Claude Desktop acceptance.

For sandbox integration tests, use [browser-validation.md](references/browser-validation.md).
