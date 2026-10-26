# Host-owned forms and native render sites

Snapshot: 2026-10-24. These mechanisms are separate from an HTML form inside an
MCP App, an MCPB settings form, and a native custom Pane. Their availability
must be established for the named host surface.

## claude-ui-host-elicitation

- **Trigger/input:** A running server operation needs additional structured
  user input, or a separate external interaction. Input is a supported form
  schema or a URL with a clear purpose and server identity.
- **Rule:** Inspect the MCP client's negotiated `elicitation` modes before
  sending `elicitation/create`. Form mode uses a restricted flat schema and
  host-rendered input; URL mode directs the user to a separate destination.
  Handle `accept`, `decline`, and `cancel`. Do not request passwords, API keys,
  tokens, or payment credentials through form mode; the specification requires
  the out-of-band URL flow for such interactions. A form is not arbitrary HTML.
- **Failure/fallback:** Claude Code officially documents form dialogs and URL
  consent. This does not establish ordinary Claude Desktop Chat behavior.
  Desktop support is untested here; do not rely on an SDK method or a CLI
  example. If negotiation or real rendering fails, collect the non-sensitive
  input through chat or a supported MCP App form. An elicitation URL flow is
  not authorization to bypass a host's link confirmation.
- **Validate:** Check advertised modes, visible prompt, edited response,
  decline/cancel, server continuation, timeouts, and absence of sensitive values
  in client-bound form data. Test the exact Desktop Chat build before claiming
  that it renders elicitation. No elicitation execution was performed in this
  skill's probe cohort.
- **Evidence:** Documented MCP and Claude Code contract; ordinary Desktop Chat
  remains conditional/untested. [MCP elicitation specification](https://modelcontextprotocol.io/specification/2025-11-25/client/elicitation),
  [Claude Code elicitation](https://code.claude.com/docs/en/mcp#respond-to-mcp-elicitation-requests).

## claude-ui-native-render-site

- **Trigger/input:** A Code Mod needs to augment an existing tool result,
  transcript row, progress indicator, question dialog, or supported prompt band.
  Input is the documented render-site name, event props, surface, and a compact
  native element tree.
- **Rule:** Filter `ui.render` by the site's documented `component`. Use
  `next(e)` or pass modified documented props when augmenting existing output;
  return a supported native tree when replacing the site. Examples include
  `UserMessage`, `AssistantMessage`, `ToolUse`, `ToolResult`, `Spinner`,
  `ToolProgress`, `AskUserQuestion`, and `Pane`. Consult the installed build's
  surface/site matrix before using bands such as `AbovePrompt`.
- **Failure/fallback:** A custom `Pane` is only one render site. Modifying a
  documented question dialog does not grant arbitrary access to permission
  prompts, host toolbars, sidebars, browser DOM, or OS windows. Preserve host
  behavior when a site is unavailable; a native mount test cannot prove that a
  deployed host requests that site.
- **Validate:** Mount the named site with realistic props and supported
  surfaces in the native test engine; verify pass-through, augmented, replaced,
  and malformed-tree behavior. Then inspect that exact site in the installed
  host. The current probes tested Pane trees, native controls, and Client
  regions; other render-site replacements are documented but untested.
- **Evidence:** Official native interface contract, with explicitly limited
  local coverage. [Draw in the interface](https://code.claude.com/docs/en/plugins/mods/interface),
  [Mods reference](https://code.claude.com/docs/en/plugins/mods/reference),
  [Native tests](https://code.claude.com/docs/en/plugins/mods/test).
