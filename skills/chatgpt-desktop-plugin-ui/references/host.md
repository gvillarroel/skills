# ChatGPT Desktop local and remote routes

Source review: November 11, 2026. Use current official docs and feature
negotiation for the actual Desktop build/thread. ChatGPT implements the MCP
Apps bridge; components run in an iframe. New components should use the shared
resource metadata and `ui/*` methods first.
[UI architecture](https://developers.openai.com/plugins/build/chatgpt-ui).

## Desktop-only package

A bundled local MCP server uses a stdio entry in root `mcp.json` with command,
arguments, working directory, and `${PLUGIN_ROOT}` for packaged resources.
Include runtime dependencies and test from an extracted copy. Desktop-only
plugins can be installed from the ChatGPT desktop app and mentioned in local
threads. Public local-MCP submissions require approved-partner eligibility;
that gate does not prove local development is unavailable.
[Desktop-only plugins](https://developers.openai.com/plugins/deploy/desktop-only).

## Remote connection

Remote connections use reachable HTTPS or the documented Secure MCP Tunnel.
Tunnel identity, runtime key, organization/workspace association and roles are
deployment requirements; keep credentials external. Local stdio success does
not establish remote connectivity. Refresh changed tool metadata and test in a
fresh conversation when the host caches it.
[Connections](https://developers.openai.com/plugins/deploy/connect-chatgpt),
[Secure MCP Tunnel](https://developers.openai.com/api/docs/guides/secure-mcp-tunnels).

## Optional UI and security boundaries

Use shared MCP Apps fields before compatibility aliases. Feature-detect
`window.openai` methods for files, host modals, widget state, and other optional
capabilities; keep eligibility-dependent workflows conditional. Distinguish
ephemeral component state, model context, widget persistence, and durable data.
Result `_meta` is component-only data, not an authorization mechanism.

Keep connect/resource/frame origins separate. Nested frames require the host's
documented CSP policy. Submission UI domains and trusted external-navigation
metadata have different contracts from Claude's URL-derived domain. Do not
copy Claude's hash rule. Sidebar apps, file viewers, richer forms and composer
entry points are documented extension points with surface/rollout boundaries,
not unrestricted host DOM access.
[Reference](https://developers.openai.com/plugins/reference),
[extensions](https://developers.openai.com/plugins/build/extensions).

Inherited October 24, 2026 evidence covers the signed-in web connection setup
and a synthetic standard-bridge browser fixture. It does not establish live
ChatGPT Desktop local installation, widget paint, optional APIs, or requested
display modes. Keep each of those current checks `untested` until executed in
the named build. Do not turn pending connection consent into a refusal.
