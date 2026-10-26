# GitHub Copilot UI boundaries

## Contents

[Restrictions](#documented-host-restrictions), [observations](#empirical-observations),
[recipes](#reusable-decision-recipes).

Snapshot: October 24, 2026 (America/New_York). Identify client, harness, build,
and policy. GitHub Copilot CLI/app, VS Code Copilot, Microsoft Copilot, and
Microsoft 365 Copilot are distinct. A Claude model in the Copilot harness
still uses Copilot's UI contract.

For the October 25 current CLI/SDK/webview study and practical offerings, read
[capability-offerings.md](capability-offerings.md). Current installed and
task-local CLI are both 1.0.103. Preserve the 1.0.75 rows below as historical.

## Documented host restrictions

For VS Code MCP Apps, register the tool/resource pair with `ui://` and
`text/html;profile=mcp-app`. The current host contract is:

| Method or feature | Restriction | Evidence |
| --- | --- | --- |
| Display mode | `inline` only; no `fullscreen` or `pip`. | documented |
| `sendMessage` | Fills the chat input; does not submit it. | documented |
| `updateModelContext` | Appears as a context attachment. | documented |
| Clipboard write | Supported by the documented host contract; still test policy and interaction. | documented; conditional |
| Camera, microphone, geolocation | Not supported in this MCP Apps surface. | unsupported |
| Network and embedded content | Sandboxed iframe; declare `connectDomains`, `resourceDomains`, and `frameDomains` in CSP metadata. | documented; conditional |

These statements apply to MCP Apps in VS Code, not every browser or native
extension webview. See the [VS Code MCP developer guide](https://code.visualstudio.com/api/extension-guides/ai/mcp).

VS Code native canvases are a separate preview surface. Enable
`chat.canvases.enabled` before creating a supported session. They require
desktop, a supported local Copilot Agent Host session, and a canvas extension.
They are excluded from Claude, Codex, extension-host Local, remote Agent Host,
web/browser, and auxiliary-window hosting. The editor Canvas menu appears
after the first message when available extensions are installed. Changing a
model does not change the harness. See [harness and canvas requirements](https://code.visualstudio.com/docs/agents/run/agent-harnesses).

The GitHub Copilot app supports plugin-bundled canvases in its side panel;
terminal rendering needs separate evidence. See [app canvas extensions](https://docs.github.com/en/copilot/how-tos/github-copilot-app/working-with-canvas-extensions).

## Empirical observations

All probes used Windows and synthetic data with **zero model inference**.
No Copilot allowance was consumed by a model request. The terminal
probe used an offline configuration and an unreachable local provider; no
natural-language prompt was sent. Its `/usage` view reported zero messages.

| Probe | Actual result | Evidence layer |
| --- | --- | --- |
| Existing CLI `--version` | `1.0.75`; its ACP `agentInfo.version` reported `1.0.73`. Preserve both values. | observed-working; installed CLI |
| Task-local current CLI | Official npm Windows binary `1.0.103`; ACP also reported `1.0.103`. | observed-working; installed CLI |
| ACP `initialize` on both builds | Protocol 1; image input advertised, audio false, embedded context true. | observed-working; protocol negotiation |
| ACP `ui/show` on both builds | JSON-RPC `-32601`, method not found. This excludes that invented method only. | observed-working negative check; request rejected as expected |
| CLI 1.0.103 extension `session.ui.confirm` | Real terminal Yes/No/Other dialog; accepting Yes returned `true`. | observed-working; actual terminal UI |
| CLI extension `select` | Real Alpha/Beta picker; selecting Beta returned `"Beta"`. | observed-working; actual terminal UI |
| CLI extension `input` and cancellation | Typed `synthetic` returned that string; Escape on the next input returned `null`. | observed-working; actual terminal UI |
| Same terminal's negotiated capabilities | `elicitation:true`, `mcpApps:false`, `canvases:true`, `extensions:false`. Capability presence alone does not prove a canvas painted. | observed-working; negotiated capabilities |
| Bare SDK consumer, SDK 1.0.26 / CLI 1.0.103 | No renderer/callback: elicitation, MCP Apps, canvases all false; `confirm` threw the explicit unsupported-host error. | observed-working expected gate check; native UI untested |
| SDK with explicit elicitation callback | Elicitation true; correct `confirmed:true` field returned true. Wrong `value:true` field returned false. Provider requests: zero. | observed-working field-contract checks; consumer callback, not native UI |
| Task-local VS Code install | `1.143.1`; bundled GitHub Copilot Chat `0.71.0` on disk. | observed-working; local install |
| Marketplace extension install attempt | Rejected older Copilot Chat `0.48.1` because bundled `0.71.0` cannot be downgraded. | observed-failed; install guard |
| VS Code native webview, scripts default | No script message received; `enableScripts` false. Positive enabled-script control below passed. | observed-working; real extension host |
| Native webview, scripts enabled | Button handler and `acquireVsCodeApi().postMessage` worked; `require` and `process` undefined. | observed-working; real extension host |
| Native webview DOM boundary | Immediate wrapper parent document readable; top application document raised `SecurityError`. | observed-working isolation check; top access refused as expected |
| Native webview nonce CSP and lifecycle | Approved script ran; unapproved inline script blocked with `script-src-elem`; disposal callback fired. | observed-working; real extension host |
| Copilot chat MCP App paint, mode request, clipboard, device permission | Not exercised in a signed-in Copilot chat session. The native extension test host exposed no Copilot extension in its runtime inventory. | untested; documentation remains separate |
| Native canvas visual rendering | `canvases:true` was observed in CLI 1.0.103, but no canvas was opened. | conditional; untested paint |

ACP audio flags do not describe every Copilot voice feature. Wrapper access
does not grant app-document access; canvas capability is not painted HTML.
The observed `extensions:false` flag did not prevent this extension from
loading; do not interpret it as an empty extension inventory.

Fresh October 25 checks pass 11 inventory commands, 15 real SDK callback cases,
two ACP cases and eight ordinary VS Code extension-host checks, with zero model
prompts and zero requests at the SDK provider guard.
In that SDK consumer, confirmation accept returns `true`, while decline and
cancel both return `false`; selection cancel and input decline return `null`.
Interpret the method and request action together, not a universal false/null
mapping. These callback outcomes do not establish terminal key behavior.
Webview JSON state survives content replacement, while a disposed/new panel
loses it; dark theme variables,
validated 7-to-8 actions, refused unknown actions, CSP and disposal are observed.
The test runtime has no Copilot extension metadata, so this is not Copilot chat
paint. The earlier visible study workspace was in Restricted Mode with Models
unavailable and Sign In present. A later human-reviewed/reopened workspace no
longer showed Restricted Mode, but still required sign-in to use Copilot models.
Scoped logs recorded a Copilot Chat activation attempt and later orderly host
termination, without an observed activation-failure stack. Neither activation
nor cleared workspace trust establishes signed-in chat readiness or app paint.
The user then chose to continue without sign-in; actual MCP App/canvas
acceptance remains untested. Task profile arguments also
did not prevent VS Code's automatic shared-storage write outside that profile.

A new exact-CS1/English probe passed 24 checks over real MCP stdio and an
offline synthetic browser, including valid/invalid/recovery state, context
without a model message, sandbox denial, keyboard focus and three viewport
widths. This validates that fixture, not its delivery inside Copilot Chat.

## Reusable decision recipes

### `copilot-ui-cli-forms`

- Trigger/input: a terminal plugin needs confirmation, a choice, or short text.
- Rule: load a trusted experimental JavaScript extension and use the negotiated
  `session.ui` methods only when `capabilities.ui.elicitation` is true. Return
  typed results from the requested field names. Treat `false` and `null`
  explicitly; cancellation is not acceptance.
- Fallback/check: provide a text workflow when the capability is absent; test
  accept, alternate choice, and Escape without asking a model to generate UI.
- Evidence: CLI 1.0.103 terminal forms passed. CLI extensions are experimental;
  pin tested versions. See [CLI extension tutorial](https://docs.github.com/en/copilot/tutorials/create-an-extension).

### `copilot-ui-vscode-apps`

- Trigger/input: a server tool returns an interactive dashboard or form.
- Rule: use the MCP Apps resource contract and the host restriction table above.
  A button requesting a follow-up must tolerate a drafted, unsent message.
- Fallback/check: retain useful text tool output; verify the resource loads,
  inline layout works, the input receives the draft, and context is attached.
- Evidence: current official host contract; signed-in Copilot paint untested.

### `copilot-ui-vscode-webview`

- Trigger/input: a full VS Code extension owns an editor-side HTML panel.
- Rule: use the VS Code extension/webview bridge, explicit script permission,
  and narrow CSP. Keep privileged actions in extension code and validate every
  incoming message. A VS Code extension is a separate installation surface.
- Fallback/check: test disabled/enabled scripts and CSP denial. Check the top
  application boundary, not only the immediate iframe wrapper. Close the panel
  and verify disposal.
- Evidence: five actual extension-host checks passed on VS Code 1.143.1; this
  does not establish MCP Apps in Copilot chat.

### `copilot-ui-native-canvas`

- Trigger/input: a shared editable artifact needs a persistent visual surface.
- Rule: identify Copilot app versus VS Code Agent Host; apply documented
  canvas exclusions and check actual renderer negotiation before declaring
  support. Extensions packaged by a plugin can contribute canvases.
- Fallback/check: preserve text or provide a separately identified browser
  artifact. Observe open, interaction, action response, close, and reopen in
  the named host; a registration or `canvases:true` result is insufficient.
- Evidence: documented support/exclusions; CLI capability observed; paint untested.

### `copilot-ui-acp-client`

- Trigger/input: an editor or custom frontend integrates the CLI agent.
- Rule: ACP carries negotiated content and session events; the integrating
  frontend supplies its own presentation. Never invent `ui/show` or infer
  an HTML renderer from image-input support.
- Fallback/check: initialize first and respect advertised capabilities. Avoid
  `session/prompt` during transport tests. See [Copilot ACP server](https://docs.github.com/en/copilot/reference/copilot-cli-reference/acp-server).
- Evidence: both tested builds initialize; `ui/show` failed consistently.

### `copilot-ui-budget`

- Trigger/input: an investigation has a limited Copilot allowance.
- Rule: inventory/version/help, local validation, protocol negotiation, and
  direct extension commands before model work. Use task-owned config/data
  directories. Do not rely on `--max-ai-credits` as a zero-cost guard: tested
  help requires a minimum of 30 and calls it a soft cap; hidden compaction can
  count. Distinguish zero inference from zero total network traffic.
- Fallback/check: test offline against a local endpoint that cannot run a
  model, inspect provider request count and native usage, and preserve failures.
  CLI 1.0.103 rejects the removed `--no-remote` flag; recheck current help.
- Evidence: zero-model CLI, SDK, terminal, and VS Code probes on the snapshot date.
