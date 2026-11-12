# Elicitation is a separate conditional UI mechanism

Official-source review on 2026-10-24; no host or model execution was performed
for this research. This note is project research, not an isolated run result.

The [MCP elicitation specification for 2025-11-25](https://modelcontextprotocol.io/specification/2025-11-25/client/elicitation)
defines client-rendered structured forms and external URL flows. Modes depend
on advertised client capability. Form schemas have a restricted structure;
URL flows happen outside the client. Secrets must use URL mode. Accepting a
URL request records consent, not completed external work. Accept, decline and
cancel are distinct outcomes. These are protocol contracts, not proof that
Claude Desktop Chat implements either UI.

The [official Claude Code MCP guide](https://code.claude.com/docs/en/mcp#respond-to-mcp-elicitation-requests)
documents form dialogs and URL-mode prompts. It states that revision
2026-07-28 connections advertise both modes. The page also documents bounded
URL-handler argument length. This is Claude Code documentation; do not promote
it to ordinary Desktop Chat, Cowork or every embedded Code surface. Its example
mentions a password prompt, which conflicts with the MCP specification's
form-secret prohibition; follow the protocol restriction for secrets.

The current [Claude documentation index](https://claude.com/docs/llms.txt)
contains no elicitation-specific page. Searches of Claude's primary docs did
not find an ordinary Desktop Chat support promise. This bounded negative search
does not prove universal lack of implementation. Desktop availability should
remain conditional/untested until negotiation and a real host action succeed.

Some current reports in Anthropic-owned issue trackers describe embedded
Desktop/Cowork declaring form capability without showing a prompt, then timing
out or returning decline/cancel. These are reporter observations, not our own
reproductions and not normative documentation. If retained as investigation
leads, label them explicitly:

- [Embedded elicitation not rendered, issue 88901](https://github.com/anthropics/claude-code/issues/88901)
- [Controlling client returns decline without prompt, issue 89858](https://github.com/anthropics/claude-code/issues/89858)

A reusable conditional pattern should distinguish MCP host-rendered elicitation
from an HTML MCP App form, native Mod Input/Select, and MCPB settings. Inventory
the protocol revision and each elicitation mode independently. Use a bounded
synthetic form and verify visible presentation plus accepted data, decline,
cancel and timeout. For URL mode verify explicit consent and the actual
out-of-band completion separately. On absent capability or unavailable UI,
offer chat input for non-secret values or a supported explicit external flow.
Never bypass a required human decision merely because a dialog did not appear.

Do not copy the modern revision's wire shape into the bundle's pinned v1 SDK
recipes. The [current client concepts](https://modelcontextprotocol.io/docs/2026-07-28/learn/client-concepts)
uses a newer multi-round-trip request flow; implementation advice must match
the negotiated revision and SDK.
