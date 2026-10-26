# Evidence and repeatable investigation

## Contents

[Evidence register](#evidence-register),
[investigation](#investigation-recipe), [diagnosis](#first-failure-diagnosis),
[sources](#primary-source-map).

Snapshot: 2026-10-24. Knowledge is intentionally bounded by product, version,
surface, and test layer. Recheck current official documentation when answering
version-sensitive questions. All newly executed checks used synthetic data.

## Evidence register

| Finding | Evidence and scope | Status |
| --- | --- | --- |
| Inline cards/carousels/fullscreen in Chat | Claude design and interactive connector documentation | documented; initial fixture cohort did not test Desktop paint |
| Local stdio MCP Apps route | Claude getting-started walkthrough; later real Desktop 3.6556.2 configuration and resource fetch | documented; later observed-working local route |
| Actual Claude Desktop Chat | Signed-in Free account, one minimal Haiku 5.5 turn: local MCP App painted, button called app-only tool, value changed 7 to 8, invalid input returned -32602 and preserved 8 | observed-working actual chat; see [live limits](claude-chat-live.md) |
| Tool/resource URI and UI MIME | MCP SDK 1.32.1 with ext-apps 1.7.5, real linked SDK transports | observed-working in SDK |
| Useful text/data without View | Tool returned text and structured count 7 | observed-working in SDK |
| Server validation | Negative count rejected; unknown tool rejected | observed-working in SDK/bridge fixture |
| UI refresh and error preservation | Sandboxed Edge fixture incremented 7 to 8, then retained 8 after error | observed-working in fixture |
| Context and follow-up methods | Real App SDK sent protocol methods; synthetic host accepted | observed-working transport; model effect untested |
| Fullscreen and denied PiP request | Fixture returned fullscreen or inline; app received actual return | observed-working negotiation; actual mode paint untested |
| Download/open requests | Fixture accepted requests; absent capability was rejected by fixture | conditional; OS delivery untested |
| SDK capability assumption | First probe incorrectly expected SDK auto-rejection; method dispatched anyway | observed-failed assumption, not a host defect |
| Parent DOM/file path/network | Browser raised SecurityError, InvalidStateError, and blocked fetch under configured CSP | observed boundary in browser fixture |
| Theme/keyboard/narrow layout | Host notification, Enter disclosure, no overflow at 360px and button height >=44px | observed-working fixture; mobile device untested |
| Claude remote origin hash | Node SHA-256 matched documented example; slash variant differed | observed-working computation; server acceptance untested |
| MCPB settings/runtime distinction | Official MCPB manifest and Desktop Extensions docs | documented; new installer execution untested |
| Native Code Mod behavior | Claude Code 2.1.302: 34 baseline engine cases, expanded to 57; see [host limits](claude-host-limits.md) | native-engine evidence; Desktop painter untested |

The browser host was deliberately a small **synthetic protocol fixture**, with
an opaque-origin `sandbox="allow-scripts"` iframe and a test CSP. Its bridge
responses and policies are evaluator-owned. It does not implement Claude's
complete sandbox, permission model, mode transitions, model delivery, download
manager, or account controls. A passed fixture records interoperability with
those supplied responses, not production-host support.

The successful MCP/browser probe contains 25 assertions. The first attempt
stopped on an incorrect evaluator assumption about download capability
enforcement. The correction made the fixture explicitly reject the unsupported
method and retained a check showing the SDK still dispatched it. Do not erase
this distinction or describe the earlier attempt as a successful run.

## Investigation recipe

1. **Identify:** Record application, build/OS, Chat/Code/Cowork, local/remote
   connection, extension version, SDK major versions, admin state, and exact
   capability negotiation. Clarify “Cloud Desktop” if product context is absent.
2. **Source:** Read the smallest authoritative page that defines the surface.
   Capture URL, retrieval date, and version when present. Treat design advice
   separately from enforced protocol/runtime restrictions.
3. **Isolate:** Use a disposable synthetic-data server/project. Keep generated
   files outside installed/read-only skill resources. Pin a compatible SDK pair
   and record the browser/runtime version. Do not silently upgrade a production
   extension or change user-level configuration.
4. **Probe useful behavior:** Exercise a real scenario: schema, output, visible
   interaction, state, and a relevant failure. A node's existence or a schema
   pass alone is insufficient. For native UI use the official Mod test engine;
   for Chat use real SDK server calls plus a sandboxed View test host.
5. **Probe restrictions:** Denied optional capability, server error, unsupported
   mode, bad input, unregistered tool, blocked origin, long content, and absent
   resource are useful candidates. Select failures relevant to the request.
6. **Verify artifact:** Inspect visible paint/screenshots, dimensions, focus,
   state after error, console errors, and exact download bytes where applicable.
   Distinguish actual observations from fixture responses.
7. **Confirm host:** When available and authorized, repeat in a signed-in target
   Desktop build. Observe tool discovery, UI consent, resource fetch, first
   paint, interaction, denied action, reload, and actual delivery. Otherwise
   mark this layer untested and retain the lower-layer result.
8. **Promote:** Add a bounded fact to the owning pattern, including version,
   method, rule, negative/fallback, and recheck condition. Never generalize a
   single provider outage or layout error to every plugin.

Use this compact result shape in reports or JSON:

```json
{
  "pattern_id": "claude-ui-mode-negotiation",
  "checked_at": "2026-10-24",
  "host": "synthetic MCP Apps protocol fixture",
  "surface": "sandboxed browser View",
  "versions": {"mcp_sdk": "1.32.1", "ext_apps": "1.7.5"},
  "action": "request pip; host returns inline",
  "expected": "use actual returned mode",
  "observed": "inline returned",
  "status": "observed-working",
  "evidence_layer": "browser-fixture",
  "limits": ["Claude Desktop PiP availability untested"]
}
```

## First-failure diagnosis

| Symptom | Check next | Avoid concluding |
| --- | --- | --- |
| No tool | Installation, enablement, server startup, tools/list, admin controls | The UI renderer is broken. |
| Tool works, no View | UI extension support, tool metadata, URI/MIME/read, UI consent | Every MCP tool automatically creates UI. |
| Blank View | Handler order, initialize/result events, bundle errors, CSP, dimensions | Plain browser success proves hosted paint. |
| Some actions fail | Server schema/auth, capability, response, timeout, granted permissions | A declared permission or SDK method is enough. |
| Blank after expansion | Viewer first-size calculation, mount timing, resize | All hidden HTML is forbidden. |
| Remote connection fails | Cloud reachability, auth, URL, certificate, host route | Local curl proves a remote connector works. |
| Origin validation fails | Exact URL hash; omit ui.domain for local stdio | Reusing another host's domain fixes it. |

## Primary source map

- [Claude MCP Apps quickstart](https://claude.com/docs/connectors/building/mcp-apps/getting-started):
  local examples, SDK bridge, and sandbox-origin setup.
- [Claude design guidelines](https://claude.com/docs/connectors/building/mcp-apps/design-guidelines):
  card/carousel/fullscreen, styles, safe areas, mobile, CSP and interaction.
- [Claude troubleshooting](https://claude.com/docs/connectors/building/mcp-apps/troubleshooting):
  developer diagnostics, size and origin failures.
- [Interactive connector help](https://support.claude.com/en/articles/13454812-use-interactive-connectors-in-claude):
  user/account surface and enabled interactive connectors.
- [MCP Apps specification](https://github.com/modelcontextprotocol/ext-apps/blob/main/specification/2026-01-26/apps.mdx)
  and [App API](https://apps.extensions.modelcontextprotocol.io/api/classes/app.App.html):
  bridge schemas, capabilities, lifecycle, contexts, downloads.
- [MCPB manifest](https://github.com/modelcontextprotocol/mcpb/blob/main/MANIFEST.md):
  package schema and user configuration.
- [Claude Mods overview](https://code.claude.com/docs/en/plugins/mods/overview),
  [reference](https://code.claude.com/docs/en/plugins/mods/reference), and
  [test kit](https://code.claude.com/docs/en/plugins/mods/test): native Code UI.

No finite probe establishes every possible UI. Cover the relevant mechanisms,
record unsupported or unknown cases, and expand the ledger when a new class of
behavior is actually investigated.
