# Codex UI, packaging, and policy boundaries

Source review: November 11, 2026. Inspect the local executable/help/schema and
fetch current official guidance before installation or API advice.
[Packaging](https://developers.openai.com/plugins/build/plugins),
[MCP UI](https://developers.openai.com/plugins/build/chatgpt-ui),
[app-server](https://developers.openai.com/codex/app-server),
[MCP setup](https://learn.chatgpt.com/docs/extend/mcp).

## Identify the layer

CLI terminal output, an app-server consumer, the desktop frontend, and the IDE
extension have separate renderers. Tools can return text, structured data,
images, and resource content without any frontend painting an App. Inspect
advertised capabilities and the actual resource/result path. A manifest links
components and tools; it is not a renderer. Current documentation distinguishes
plugin installation surfaces from IDE extension support; direct MCP support is
a separate question. [Plugin surfaces](https://learn.chatgpt.com/docs/plugins).

An owned client may render its own dashboard and callbacks using app-server.
Implement auth/context, request IDs, timeouts, cancellation, and event lifecycle
there. This proves that client, not stock desktop/IDE paint. When a stock host
route has not been executed, label it `untested`, not impossible or exclusive.

## Packaging and executing loaders

Portable root `plugin.json` and `mcp.json` use distinct schemas. OpenAI-specific
metadata goes under `extensions.com.openai`. The supported compatibility
`.codex-plugin/plugin.json` layout has a different schema; renaming files cannot
convert it. Use the bundled packaging reference for minimal JSON and clean-copy
checks. Prefer a project-local catalog for a scoped trial.

Inherited October 25, 2026 observations: npm Codex 0.145.0 discovered/installed
the portable package but returned no plugin servers in the tested app-server
thread. Desktop-bundled 0.164.0-alpha.11.1 connected its server and passed an
exact direct tool call. This is a bounded loader comparison, not a universal
version cutoff or frontend paint result. Verify catalog, install, server list,
and real tool separately through the binary that actually runs the work.

## Elicitation and actual consent

Host forms and URL elicitation are distinct from an app-owned form. Inspect
supported schema, policy, callback delivery, and the visible frontend. In the
historical CLI/app-server probe, `never` declined forms and `on-request`
forwarded callbacks. Do not generalize that result across builds or manufacture
consent by retrying with a different policy. Cancellation is not acceptance.
Keep native permission UI and accessibility styles host-owned.

Validate an ephemeral synthetic app-server thread's MCP status and direct tool
before a model turn. Preserve logs without credentials. A successful backend
callback, returned HTML, or ordinary browser test does not establish stock
desktop/IDE/TUI paint, keyboard focus, or form placement.
