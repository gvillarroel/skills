# Component copy audit

Date: October 25, 2026. Project: `desktop-plugin-ui`.

**No non-English authored UI copy was found in the scoped component sources.**
This is a read-only source audit, not a new rendering or interaction test.
No app, provider, network probe, installation, or host setting was used or
changed. Component sources and historical evidence were left untouched.

## Scope and method

Reviewed the owned HTML-producing templates, widget handlers, native hooks,
CLI extension, webview tests, Codex MCP fixture, and their display metadata.
The source inventory contains **25 code/configuration files**: 11 TypeScript,
six JSON, four Python, two MJS, and two CJS files. It includes hidden
`.claude-plugin/plugin.json` metadata. The rendering/interaction producers and
metadata were read; supporting tests/probe harnesses were inspected for emitted
copy and sample values. Searches covered non-ASCII characters, Unicode escapes,
common non-English copy, and user-facing string sinks. No non-ASCII source
characters or non-English authored phrases were found; the English conclusion
also depends on manual review, not character detection alone.

| Owned source group | Scope | Authored UI copy examples |
| --- | --- | --- |
| [MCP fixture](../../projects/desktop-plugin-ui/mcp-probe/probe.ts) and [widget](../../projects/desktop-plugin-ui/mcp-probe/widget.ts) | Embedded HTML, labels, controls, host-fixture iframe title, status/error text, tool output and context/message samples | “Review result”, “Value”, “Increment”, “More options”, “Attach a file”, “Tool rejected”, “ready”, “waiting”, “Research protocol host”, “Controlled rejection”, “Count”, “Selected row: seven” |
| [Live server](../../projects/desktop-plugin-ui/mcp-probe/live-server.ts) and [live widget](../../projects/desktop-plugin-ui/mcp-probe/live-widget.ts) | Embedded view, tool title/descriptions, handshake state, controls, synthetic content and download text | “Assistant UI limits probe”, “Waiting for host handshake”, “Connected to actual host”, “Increment locally via tool”, “Reject invalid input”, “Fullscreen”, “Picture in picture”, “Update model context only”, “Check sandbox”, “Download synthetic text”, “Open example.com”, “Negotiated host capabilities” |
| [Original Mod hooks](../../projects/desktop-plugin-ui/mods-probe/hooks/register.ts) and [client](../../projects/desktop-plugin-ui/mods-probe/hooks/client.ts) | Pane title, links, controls, options, draft/submit/status messages, native image/SVG alternatives and sample code/Markdown | “UI probe”, “Use the transcript fallback”, “Pane requested”, “Add one”, “Query”, “Draft”, “Submitted”, “Size”, “Small”, “Large”, “Selected”, “Copy path”, “Generate”, “Notify”, “Complete”, “1 ready”, “Ready locally”, “Red square”, “Red pixel”, “Update through hooks” |
| [Expanded Claude hooks](../../projects/desktop-plugin-ui/cross-assistant/claude/native-probe/hooks/register.ts) and [client](../../projects/desktop-plugin-ui/cross-assistant/claude/native-probe/hooks/client.ts) | The preceding native copy plus boundary/invalid-input cases | “HTML probe”, “Bounded link”, “Exact source length”, “Wrong pixel count”, “Too wide”, “Missing file”, “Bounded option”, “Invalid autofocus”, “Validated fallback”; existing controls remain English |
| [Copilot CLI extension](../../projects/desktop-plugin-ui/cross-assistant/copilot/cli-extension/extension.mjs) | Confirmation, select/input/cancel prompts, option labels, completion notices and sample input | “UI evidence probe: accept this synthetic confirmation?”, “UI evidence probe: select Beta”, “Alpha”, “Beta”, “UI evidence probe: type synthetic”, “UI evidence probe: cancel this input with Escape”; completion notices are English |
| [VS Code webview tests](../../projects/desktop-plugin-ui/cross-assistant/copilot/vscode-probe/test.cjs) and [extension metadata](../../projects/desktop-plugin-ui/cross-assistant/copilot/vscode-probe/package.json) | Panel/extension title, HTML button, timeout/error copy, result labels | “UI Evidence Probe”, “Probe”, “Webview message timeout”, “UI evidence probe had failures”; the activation module adds no visible copy |
| [Codex MCP fixture](../../projects/desktop-plugin-ui/cross-assistant/codex/fixture.py) | HTML button/sample identifiers, resource name, fallback, elicitation message/options, unknown-tool/method errors | “UI_PROBE_BUTTON”, “UI boundary card”, “This is a text result, with a separate HTML resource.”, “Synthetic UI probe; no account details required.”, “alpha”, “beta”, “Unknown probe tool”, “Unknown fixture method” |

Both native plugin manifests describe “Local account-free probes of Claude Code
Mod UI contracts.” Supporting native test values, SDK callback prompts, Codex
test prompts and harness diagnostics are also English. Stable protocol keys,
paths, version strings, executable/API names, base64 image data, and synthetic
marker identifiers are technical data, not prose requiring translation.

Visible titles, buttons, option labels, statuses, errors, details summaries,
file labels, native `alt` text and the iframe `title` were included. No authored
chart axes, series/legend labels, tooltip strings, placeholders, or explicit
`aria-label` strings occur in these components. Existing accessible copy uses
HTML/native labels, alternative text, titles, and status regions; this does not
claim a complete accessibility audit.

## Findings and language boundaries

**Exact non-English authored-copy findings: none.** No translation edit is
needed for the inspected fixed strings. This does not establish that every
possible runtime value will be English. Several diagnostic/data paths preserve
uncontrolled text:

- `mcp-probe/widget.ts:46` displays `String(e)` after connection failure.
  `live-widget.ts:21` displays raw error text; lines 3–7 and 25 render tool,
  capability, and host-context data. Lines 18–19 can report a host-owned
  document title. Their authored labels are English, but external values are
  not language-normalized.
- Both native `hooks/register.ts:19` return raw `error.message`; line 21
  accepts an incoming label. The client draws `props.label`, while draft and
  submitted values reflect user input. English surrounding labels do not
  translate those user/host values.
- `cross-assistant/codex/fixture.py:81` echoes elicitation replies/errors as
  diagnostic JSON. Copilot/VS Code probe failure reports likewise preserve
  raw runtime errors rather than authoring translated UI sentences.

These are scope limits, not observed non-English failures. If a later
implementation requires every generated explanatory message to be English,
give failures stable English summaries and keep quoted raw diagnostics/source
data identified separately. Do not silently rewrite raw evidence or user data
and then claim that the original text was English.

Host-owned UI—including file pickers, permission dialogs, elicitation button
labels, installer chrome, browser errors and terminal/client menus—may follow
the host locale. The owned source strings do not control that locale. Historical
captures, logs, protocol traces and raw errors were not translated or regenerated
for this audit. Generated `view.html`, dependency bundles, installed application
resources, screenshots, and external pages were not re-rendered or recertified.
No new claim about actual host paint or screen-reader output follows from this
source review.

## Post-audit source correction

Later on October 25, the root agent updated the components. The raw-error
observations above describe the **pre-change sources** and remain preserved
for chronology. Re-reading the changed sources confirms:

- `mcp-probe/widget.ts` now displays “Unable to connect to the host. Please
  retry.” on connection failure. The raw error accompanies the English
  `console.error` diagnostic instead of replacing visible recovery copy.
- `mcp-probe/live-widget.ts` now summarizes rejected input as “The input was
  rejected. Check the value and try again.” and action exceptions as “The
  requested action failed. Please retry.” Both preserve the current value;
  raw rejected payloads/errors are sent to console diagnostics.
- The authored HTML roots in `mcp-probe/probe.ts` (inner app),
  `mcp-probe/live-server.ts`, `cross-assistant/codex/fixture.py`, and all three
  VS Code webview templates now declare `lang="en"`. At this source check,
  the synthetic outer host-wrapper document in `probe.ts:57` still has a bare
  `<html>` root; its authored “Host content” and iframe title are English.
  This remaining declaration gap is not a non-English copy finding.

English recovery summaries do not translate original user input, incoming
labels, protocol identifiers, host-context/title data, successful raw tool
results, console diagnostics, or elicitation replies. Those remaining data
boundaries and host-owned locale limits still apply. Existing historical
captures/logs were not rewritten. This follow-up verified source changes only:
no browser/native host was opened or rendered, no provider/network test was
run, and no new paint, screen-reader-language, or recovery-behavior claim is
made. Runtime fixture verification belongs to a separately recorded run.
