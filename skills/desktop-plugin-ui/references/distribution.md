# Host, packaging, and distribution

Snapshot: 2026-10-24. Recheck current primary documentation before installing.

## Ordinary Desktop Chat

Claude documents local stdio MCP Apps: add a server under `mcpServers` in the
Desktop configuration, then connect it and allow the UI. A local server can
also be delivered as a Desktop Extension (`.mcpb`). These are ordinary Chat
routes, separate from a Claude Code plugin's Mod runtime.
[Claude local MCP Apps walkthrough](https://claude.com/docs/connectors/building/mcp-apps/getting-started).

For remote custom connectors, Anthropic infrastructure contacts the MCP URL,
including when the client is Desktop. A successful localhost/VPN request from
the user's computer is not a remote-connectivity test. Use the documented
local Desktop route for local-only servers, or deploy an authorized reachable
remote endpoint. Account/workspace controls may restrict installation or UI.
[Remote connector requirements](https://support.claude.com/en/articles/11175166-get-started-with-custom-connectors-using-remote-mcp).

Do not conflate a plugin's bundled local MCP configuration with the Desktop
local-server mechanism. Current plugin help says plugin local MCP servers,
hooks, and subagents run in Cowork/Claude Code rather than Chat; skill and
command behavior differs. Identify the exact package and route before diagnosing.
[Claude plugin behavior](https://support.claude.com/en/articles/13837440-use-plugins-in-claude).

## claude-ui-extension-settings

- **Trigger/input:** Local server installation with typed paths, strings,
  booleans, or secret configuration values.
- **Rule:** Use the MCPB manifest's typed `user_config`, required/default fields,
  and sensitive secret handling. Bundle the declared entry point and dependencies;
  validate/pack with the official MCPB CLI. Distinguish manifest schema versions
  from CLI/package versions.
- **Failure/fallback:** Generated installation/settings screens do not supply a
  custom runtime React panel. Successful `mcpb validate` proves manifest shape,
  not installed UI, runtime dependencies, trust approval, or account enablement.
- **Validate:** Manifest schema, fresh extracted package, stdio handshake,
  configuration substitution, missing prerequisites, and actual install when
  authorized. Keep credentials out of screenshots and logs.
- **Evidence:** Documented; this skill's new probes did not install an extension.
  [MCPB manifest](https://github.com/modelcontextprotocol/mcpb/blob/main/MANIFEST.md),
  [Desktop Extensions](https://www.anthropic.com/research/desktop-extensions).

## Origin and transport pitfalls

Claude's remote `ui.domain` is the first 32 hexadecimal characters of SHA-256
of the exact configured full server URL, followed by `.claudemcpcontent.com`.
A trailing slash changes the hash. Local stdio connectors have no URL to hash;
omit this field. Do not copy a ChatGPT widget domain into Claude metadata.
[Claude domain diagnosis](https://claude.com/docs/connectors/building/mcp-apps/troubleshooting#ui-domain-validation-fails).

The local computation probe matched the documented example:
`https://example.com/mcp` maps to
`c3d80a4ed901ee05b21755a88273b4a4.claudemcpcontent.com`.
It also demonstrated different hashes for the slash variant. This validates
the computation, not remote connector acceptance.

The MCP tool transport (stdio/HTTP) and the iframe bridge (`postMessage`
JSON-RPC, or another SDK-selected host transport) are separate channels.
Do not point a browser UI directly at a local stdio stream. Register tools and
resources through standard helpers; call `App.connect()` without imposing a
Desktop-specific browser transport when current SDK host detection applies.

## Cross-host portability

Use MCP Apps metadata, tool schemas, and the shared bridge for portable UI.
Keep host-specific domains, CSP, auth, install paths, and optional features in
small adapters. ChatGPT documents shared methods first and optional
`window.openai` extensions for capabilities beyond the standard. Those methods
do not establish a Claude API. Reachable HTTPS is a common ChatGPT deployment
route; a local stdio success does not prove its remote route or asset URLs.
[OpenAI MCP UI documentation](https://developers.openai.com/plugins/build/chatgpt-ui).

Plain HTML, React, Vue, Svelte, and similar frameworks describe implementation
choices inside a View; they are not distinct host UI surfaces. Likewise,
tables, trees, timelines, charts, maps, media, forms, and drag/drop are web
patterns subject to that View's sandbox and capabilities. Browser support must
be checked for each renderer, permission, and host.

## Adjacent surfaces and unknowns

Claude artifacts are a separate host workspace. Verify current templates,
plan, and capabilities before suggesting them. Current help distinguishes
modern artifacts from retained legacy artifacts; do not present artifact
creation as an MCP protocol operation.
[Artifacts guide](https://support.claude.com/en/articles/17153992-what-are-artifacts-and-how-do-i-use-them).

No evidence in this bundle establishes arbitrary plugin insertion into Claude's
main sidebar, host toolbar, native OS windows, or unrestricted host DOM.
Mark these requests `untested` or unsupported only where an explicit contract
excludes them. Browser sandbox isolation is an explicit boundary; an unrelated
native API possibility cannot be inferred from it.
