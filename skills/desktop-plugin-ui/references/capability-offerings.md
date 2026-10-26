# Copilot and Codex feature offerings

Snapshot: October 25, 2026, Windows. Use this reference to choose what a plugin
can offer on a named client. Read the matching host reference for implementation
rules. Versions, account access, protocol support and visible rendering are
separate facts. Preserve English component copy and the selected ColorSet.
Use `observed-working` for the stated executed backend/extension-host checks,
including intended negative checks. Use `observed-failed` only when an executed
check misses its expectation, `documented` for sourced declarations and
`untested`/`conditional` for unexercised frontend or access paths. Keep raw
refusals separate from whether the check passed; use the typed workflow in
[report-authoring.md](report-authoring.md).

## Contents

- [Identify the runtime](#identify-the-runtime)
- [Choose an offering](#choose-an-offering)
- [Interpret the new probes](#interpret-the-new-probes)
- [Check deployment and access](#check-deployment-and-access)
- [Validate the intended product](#validate-the-intended-product)

## Identify the runtime

| Surface | Observed inventory | Boundary |
| --- | --- | --- |
| npm Codex CLI | 0.145.0 | This older executable is distinct from the desktop-bundled core. |
| Windows desktop package | `OpenAI.Codex` 26.1021.3705.0; bundled core 0.164.0-alpha.11.1 | A newer backend does not establish a particular widget or permission effect. |
| GitHub Copilot CLI | Installed and task-local binaries 1.0.103; SDK 1.0.26 | Earlier installed 1.0.75 evidence remains historical. |
| VS Code | Portable 1.143.1; Copilot Chat 0.71.0 on disk | Package presence is separate from active extension inventory and signed-in chat. |

Keep Microsoft consumer/Office Copilot separate from GitHub Copilot. A Claude,
GPT or Codex model inside a Copilot session does not change its harness.

## Choose an offering

| Requested feature | Codex route and measured boundary | Copilot route and measured boundary |
| --- | --- | --- |
| Useful answers without a widget | Text and authoritative structured tools work in CLI/app-server. | MCP tools and text remain the fallback for terminal or unavailable UI. |
| Confirmation, choice or short input | Standard form callbacks accept string, integer, boolean and enum-array values in the tested client. Actual form pixels are separate. | Historical CLI 1.0.103 terminal dialogs worked; fresh SDK callbacks verify accept/decline/cancel without painting a dialog. |
| Interactive cards, forms and charts | Desktop MCP App chart paint has bounded Windows evidence. A fresh connected chart call returned metadata; direct controls still awaited panel expansion in this study. CLI HTML-resource receipt alone is not paint. | VS Code documents inline MCP Apps; current signed-in chat paint remains untested behind workspace/account gates. |
| A custom HTML panel | A developer-owned frontend can present the app-server's data/events. Do not infer stock sidebar injection from that API. | A separately installed VS Code extension owns a webview; fresh tests verify script permission, actions, CSP and disposal. |
| Fullscreen or picture in picture | Test the actual MCP App frontend's mode negotiation; no placement method was found in the tested app-server request unions. This is not a universal frontend exclusion. | VS Code's documented MCP Apps surface is inline-only. A separate ordinary webview or canvas has its own contract. |
| Images, vector/audio data or files | PNG, embedded SVG, valid WAV bytes and CSV resource links survived backend transport. Display, playback, navigation and saving are separate checks. | ACP advertises image input, not audio input, in the tested connection. This does not describe every Copilot voice or output feature. |
| Direct controls without a model turn | Keep local interactions and explicit server-tool actions inside a supported component; verify the returned state. | Terminal extension controls and supplied SDK callbacks can run without model inference. Webview actions use the extension bridge. |
| Context or a follow-up action | Feature-detect the component host's bridge; do not copy ChatGPT-only extension APIs into another client. | VS Code MCP Apps document context attachments and a drafted follow-up message, rather than automatic submission. |
| Selection and edit state | Synthetic server state, version increments and stale-edit rejection passed; process restart durability was not tested. | Webview JSON state survived content replacement. A disposed/new panel did not inherit it; serializers and server storage require separate tests. |
| Progress and recovery | The tested direct-call route returned the final result without progress events. Do not promise streamed progress from that observation. | Expose truthful status and recovery through supported controls; callback acceptance is not a progress renderer. |
| Canvas or shared artifact | A custom frontend or supported component may provide a canvas; no stock canvas-placement result is claimed here. | Preview canvases require the documented desktop local Copilot Agent Host and a canvas extension. A `canvases:true` flag is not visible canvas acceptance. |
| Theme and English UI | Bind authored paint to exact tokens and keep host chrome separate. Check all visible/accessible states. | Actual webviews received dark-theme variables and `lang=en`; host variables are mapped paint, not exact ColorSet pixels. |

The [VS Code MCP guide](https://code.visualstudio.com/api/extension-guides/ai/mcp)
defines its inline/messaging/device limits. The separate
[webview API](https://code.visualstudio.com/api/extension-guides/webview) and
[agent-harness guide](https://code.visualstudio.com/docs/agents/run/agent-harnesses)
cover extension panels and preview canvas exclusions. Do not transfer those
contracts between surfaces.

## Interpret the new probes

Fresh Codex feature checks pass 21 assertions per tested configuration across
the older npm and newer bundled cores, including opt-in/policy variations.
They use zero model turns. They observe transport, callbacks, synthetic state
and failures; they do not paint the stock frontend.

Instrument the process actually serving each tool. Fresh PID-bound records
show `openai/form` advertised on that serving process when opted in, in both
cores. An idle connection can omit it. The earlier inference that the executing
thread connection lacked the extension was wrong and is withdrawn. Arbitrary
nested schemas still fail: the older core returns -32601, the newer returns
-32602. A basic flat `openai/form` or `openaiForm` normalizes to ordinary `form`,
even without opt-in; none of this proves a rich form painted.

A separate October 25 Windows desktop capture in Codex mode shows an actual
inline MCP App chart through direct same-host MCP configuration after Save and
Restart. Folder-plugin server discovery had failed; that direct configuration
was an observed workaround, not an account-tier exclusion. The particular
capture's app build was not recorded per image, so do not assign it the newer
core's version. The current study's connected CS1 chart call returned valid
metadata and export formats, but live controls remained untested while its
inline component was not expanded into a controller-visible panel.

The per-process experimental `enable_mcp_apps=true` override did not add the
MCP Apps UI extension or placement methods to the tested stdio app-server path.
This result cannot exclude a desktop frontend's own renderer. Default feature
flags and model catalogs are not entitlement or visual acceptance tests.
See the [app-server contract](https://learn.chatgpt.com/docs/app-server).

Fresh Copilot checks pass 11 inventory commands, 15 SDK/runtime cases, two ACP
checks and eight ordinary VS Code extension-host cases, with zero model
prompts. The SDK guard observes zero provider requests. Callback behavior is
not a terminal painter; the extension-test runtime returned no Copilot metadata,
so its webview pass is not signed-in Copilot Chat acceptance. See the
[SDK source](https://github.com/github/copilot-sdk) and
[CLI extension tutorial](https://docs.github.com/en/copilot/tutorials/create-an-extension).
SDK MCP Apps require the appropriate opt-in, runtime gate and an actual supplied
renderer; a flag alone is not a UI. Copilot app canvases also have their own
contract, separate from VS Code preview canvases and CLI capability flags.
In the tested SDK consumer, confirmation decline and cancel both return `false`;
selection cancel and input decline return `null`. Interpret method/action
semantics instead of imposing one universal false/null meaning.

## Check deployment and access

Codex clients can share direct MCP configuration on the same host. The plugin
bundle/directory path is distinct: current official controls document plugins
in the desktop app and CLI browser, but not in the IDE extension. That does
not exclude direct IDE MCP tools. See
[MCP setup](https://learn.chatgpt.com/docs/extend/mcp) and
[plugin controls](https://learn.chatgpt.com/docs/enterprise/apps-and-connectors).

A fresh VS Code study workspace visibly remained in Restricted Mode with
Models unavailable and Sign In present. Human trust/authentication was pending;
this is an access gate, not a product-wide MCP App exclusion. Preserve the
default permission model and do not bypass the gate for a test.

Later on October 25, the human-reviewed/reopened workspace no longer showed
Restricted Mode but still displayed Sign In and required sign-in for models.
Scoped logs recorded a Copilot Chat activation attempt, then orderly host
termination, with no observed activation-failure stack. The user selected
continuation without sign-in; actual signed-in chat/canvas paint stays
untested. A new CS1/English probe passed 24 real-MCP/synthetic-browser checks;
this is fixture evidence, not Copilot Chat acceptance.

The user reported the fresh Codex chart expanded and visible. The controller
briefly listed its app tab, failed to bind it, then listed no tabs. Registration
source declares the proper UI resource and private metadata; the component's
Expand action requests fullscreen, separately from host side-panel opening.
Record this as a controller discovery/binding gap, not verified controls or a
product-wide rendering exclusion. Model-visible omission of app-private
metadata also does not establish that the server or host omitted its delivery.

Task-scoped `--user-data-dir` and `--extensions-dir` did not provide complete
filesystem isolation: VS Code automatically initialized shared storage under
the user's `.vscode-shared` directory. The study did not read or edit that
database. Do not promise that a task profile prevents every app-owned write.

## Validate the intended product

1. Record executable/package/frontend versions and the actual account/policy
   state. Keep model names separate.
2. Test discovery, resource bytes, initialization, pixels, interaction,
   authoritative response and close/reopen separately. Instrument serving
   processes rather than inferring their role from log order.
3. Exercise one useful success and one relevant failure using synthetic data;
   include decline, cancel, invalid/stale input and missing capability.
4. Verify actual file bytes, clipboard/navigation and permissions only when
   those effects are part of the authorized workflow. Do not infer them from
   a result URI, method name or advertised flag.
5. Record English visible/accessible copy, exact authored token bindings,
   measured contrast and remaining host checks. A local browser preview or
   ordinary extension test remains distinct from assistant-chat acceptance.
