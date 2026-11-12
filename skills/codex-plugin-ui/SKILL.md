---
name: codex-plugin-ui
description: Creates, packages, and validates Codex plugins and MCP interactions for the CLI, desktop, app-server, or IDE surface. Use for plugin UI authoring, elicitation, loader diagnosis, or a custom app-server frontend, with separate checks for transport and actual rendering.
---

# Codex Plugin UI

Start with the pending human decision. Read
[micro-decisions.md](references/micro-decisions.md) for the default agent UI:
one bounded question, only decision-relevant evidence, and a typed result
returned to the agent. Use a full workspace only when the user requests it.

For graphs, charts, dense tables, or linked multi-panel interfaces, read
[rich-interfaces.md](references/rich-interfaces.md) before choosing the layout.
Apply its graph/chart recipes, host alternatives, state rules and pixel critique.

For coordinated investigations, dense matrices and reviewed actions, read
[complex-workspaces.md](references/complex-workspaces.md).

Identify the executing Codex binary, frontend, build, approval policy, and
negotiated capabilities. Read [host.md](references/host.md); a model name,
shared account, MCP result, or package install does not identify the renderer.

1. Keep useful text/structured/image tool output. Select only a documented or
   observed mechanism for the requested CLI, desktop, IDE, or owned frontend.
2. For a package, use [portable-packaging.md](references/portable-packaging.md)
   and validate the actual executing loader plus a fresh extracted runtime.
3. If the selected frontend supports an MCP App, use
   [mcp-apps.md](references/mcp-apps.md). If paint is untested, preserve that
   uncertainty and continue independent server/package/browser work.
4. For a requested custom app-server client, implement its event handling and
   presentation explicitly. Treat an HTML response as data until the frontend
   actually renders it. Do not describe a custom client as the only UI route.
5. Apply [interaction-quality.md](references/interaction-quality.md). Test
   discovery and direct tools without a model turn, then exercise actual host
   UI, elicitation, cancellation, and policy boundaries when available.

Deliver working sources, package/configuration, exact paths, setup/test
commands, and remaining frontend checks. Do not claim a painted form from a
JSON callback or route an approval refusal through an equivalent alternate tool.
Keep loader, protocol, fixture, and real-host results distinct.

For sandbox integration tests, use [browser-validation.md](references/browser-validation.md).
