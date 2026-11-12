# Copilot capability study

Snapshot: October 25, 2026. Platform: Windows. This study keeps Copilot CLI,
SDK consumers, ordinary VS Code extensions, chat MCP Apps and preview canvases
as separate surfaces. The [machine-readable matrix](capability-matrix.json)
contains 22 feature rows with evidence layers, limits and primary sources.
No canonical skill or backlog file was edited.

## Current result

Fresh checks passed: **11 version/help inventory commands**, **15 SDK/runtime
checks**, **two ACP checks**, and **eight real VS Code extension-host checks**.
No model prompt was submitted. The SDK's local provider guard observed zero
requests. Fresh account/trust and signed-in chat acceptance remain pending.

The installed PATH CLI now reports **1.0.103**, matching the existing task-local
CLI. The prior 1.0.75 inventory is historical. Current SDK is **1.0.26**,
portable VS Code **1.143.1** (`e646868227c3e3a9e3f24277c8c7220be42c0be7`),
and its bundled Copilot Chat package **0.71.0**. This study reused those tools;
it installed or updated none of them.

Copilot offers distinct authoring routes:

- Experimental CLI extensions supply session-aware code, tools and slash
  commands. Plugins can package them; they are separate from IDE extensions
  and the retired GitHub App integration. [GitHub extension concepts](https://docs.github.com/en/copilot/concepts/customizations/extensions),
  [CLI extension tutorial](https://docs.github.com/en/copilot/tutorials/create-an-extension).
- VS Code chat MCP Apps provide sandboxed inline resource views. Follow-up
  messages draft input; context updates attach context. The documented host
  table excludes fullscreen/PiP and camera/microphone/geolocation; it lists
  clipboard support. Current signed-in paint is unverified. [MCP developer guide](https://code.visualstudio.com/api/extension-guides/ai/mcp).
- Ordinary VS Code extensions offer their own document views and native
  controls, with extension lifecycle and authority. Fresh tests below verify
  the webview route. Extension tools integrate agent actions through a
  different contribution API. [VS Code API](https://code.visualstudio.com/api/references/vscode-api),
  [Language Model Tool API](https://code.visualstudio.com/api/extension-guides/ai/tools).
- Preview canvases require a supported desktop local Copilot Agent Host
  session and a canvas extension. The documented exclusions include Claude,
  Codex, extension-host Local, remote Agent Host, web and auxiliary windows.
  No canvas was painted here. [Agent harnesses](https://code.visualstudio.com/docs/agents/run/agent-harnesses).
  The separate Copilot app exposes shared canvas surfaces that can be
  distributed by plugins. [App canvas extensions](https://docs.github.com/en/copilot/how-tos/github-copilot-app/working-with-canvas-extensions).

## Fresh zero-inference evidence

From the repository root:

```powershell
uv run --script projects/desktop-plugin-ui/capability-study-20261025/copilot/inventory.py
node projects/desktop-plugin-ui/capability-study-20261025/copilot/sdk-protocol.mjs
uv run --script projects/desktop-plugin-ui/capability-study-20261025/copilot/acp-protocol.py
```

`inventory.py` collects public build/help output, not account/configuration
contents. It records permissions, plugin/MCP help, usage limits and provider
configuration syntax. Tool availability and approval policy are different
controls. The installed help describes the credit limit as a soft cap, including
hidden model work; this study instead sends no model prompt.

The SDK probe uses the real CLI runtime, an explicit synthetic model, no
logged-in user, no discovered tools/instructions, and a localhost provider
that records and rejects requests. It checks:

- No-renderer `ui.elicitation=false`, followed by the expected unsupported-host
  confirmation error.
- A supplied consumer callback enabling elicitation, with confirmation
  accept/decline/cancel, selection accept/cancel, input accept/decline, an
  intentionally wrong confirmation field, and input schema options.
- Correct true/false/null results, complete callback consumption and zero
  provider requests.

These callbacks do not paint terminal dialogs. The earlier four real terminal
dialog interactions remain [separate historical evidence](../../cross-assistant/copilot/validation-20261024.md).
No terminal GUI was launched in this cohort.

Installed SDK types expose an experimental `enableMcpApps` opt-in and a
separate runtime feature gate. The types require an actual iframe renderer
before opting in. The bare consumer reports `mcpApps=false` and `canvases=false`;
that is a connection result, not a blanket Copilot exclusion. The opted-in
rendering path was not tested. [Official SDK repository](https://github.com/github/copilot-sdk).

ACP initialization reports CLI 1.0.103, image input and embedded context true,
audio false. The invented `ui/show` request returns -32601. This says nothing
about other rendering contracts. [ACP reference](https://docs.github.com/en/copilot/reference/copilot-cli-reference/acp-server).

The first ACP harness lacked write/cleanup-error handling. After retaining that
failure, a diagnostic run identified the actual startup gate: offline mode
requires a local provider. The corrected configuration supplies an unreachable
localhost provider and explicit synthetic model; initialization and the
negative method test then pass with no session/prompt. Both unsuccessful
attempts remain in the artifacts; they are setup/harness failures, not failed
Copilot UI features.

## Fresh extension-host evidence

The root agent authorized a separate, self-running hidden test window while
retaining control of the user's visible study window. The test used
`webview-probe/test.cjs`, a dedicated `profile-webview`, and these arguments:

```powershell
$StudyArtifacts = 'C:\Users\villa\dev\skills\projects\desktop-plugin-ui\artifacts\capability-study-20261025\copilot'
$StudyProbe = 'C:\Users\villa\dev\skills\projects\desktop-plugin-ui\capability-study-20261025\copilot\webview-probe'
Start-Process -FilePath 'C:\Users\villa\dev\skills\projects\desktop-plugin-ui\artifacts\cross-assistant\copilot\vscode\Code.exe' -ArgumentList @('--user-data-dir',"$StudyArtifacts\profile-webview",'--extensions-dir',"$StudyArtifacts\vscode-extensions",'--extensionDevelopmentPath',$StudyProbe,'--extensionTestsPath',"$StudyProbe\test.cjs",'--locale','en','--skip-welcome','--skip-release-notes','--new-window',$StudyProbe) -WindowStyle Hidden
```

All eight checks passed; the process exited 0. The runtime inventory included
VS Code 1.143.1 but returned `null` for Copilot extension metadata. Therefore
these are ordinary extension-host checks, not signed-in Copilot Chat evidence.

| Check | Observed result |
| --- | --- |
| Runtime inventory | VS Code version captured; no account API called |
| Scripts disabled by default | Zero webview messages |
| Script/button/action bridge | Synthetic value 7→8; unknown action refused; no privileged command executed |
| JSON state/content reload | `setState` value 7 returned through `getState` after replacement HTML |
| Disposed/new panel state | New panel did not inherit the disposed panel's state |
| Theme/language/isolation | `lang=en`, `vscode-dark`, theme variable `#bbbebf`; top DOM `SecurityError`; no Node globals |
| CSP refusal | Unapproved inline script blocked with `script-src-elem` |
| Disposal | Callback fired |

The active dark-theme variable is host-mapped paint, not an exact ColorSet
claim. Hidden-tab lifecycle, light/high-contrast switching, reduced-motion
behavior and restart serializers were not executed. The documented webview
state APIs and serializer contract are distinct from durable server storage.
[Webview API](https://code.visualstudio.com/api/extension-guides/webview).

## Coordinated chat paint readiness

`paint-workspace/.vscode/mcp.json` registers only the existing synthetic stdio
probe, exposing `ui_limits_open` plus an app-only increment tool. This server
exposes no private filesystem/account tool. VS Code's other enabled tools are
a separate host configuration; their absence was not proved by this server
configuration. Direct buttons use synthetic value 7.
No sampling request is made. Task profiles copy only ten safe settings;
credentials, databases, caches and global profiles were not copied.

The root agent reports the visible `paint-workspace` window in Restricted Mode,
with Models unavailable and Sign In visible. Human workspace-trust review and
GitHub sign-in are pending. The agent did not automate authentication/security
prompts, use bypass flags, or submit a Copilot model request. The next paint
step is one explicitly coordinated minimal tool-opening turn after that gate,
followed by direct app actions and cancellation checks without extra inference.

The initial interactive launch used Hidden and did not yield a discoverable
window; rerunning against that profile reused hidden IPC state. A fresh
`vscode-profile-visible` with only safe settings and a normal interactive
launch produced the visible window. This is a launch/profile issue, not an
unsupported UI feature. The user-facing window was left open.

**Filesystem boundary:** the root observed VS Code automatically creating
`%USERPROFILE%\.vscode-shared\sharedStorage\state.vscdb` despite task-scoped
user-data/extensions arguments. Neither agent read, deleted or edited that
database. Do not describe these arguments as strict filesystem isolation.
This automatic app state write is separate from an agent global-settings edit.
Scoped renderer logs also contain a bundled Copilot API-proposal mismatch and
a startup timeout; no proposal bypass was attempted.

### Scoped activation diagnostic before further human login work

A later read inspected only `vscode-profile-visible`'s `renderer.log` and
`exthost.log`; it read no global/shared database or credentials. The renderer
labels the `github.copilot-chat` proposal mismatch as **error**, not warning.
Its exact requested-but-not-granted proposal delta is **`authIssuers`** and
**`languageModelRateLimit`**. The distinct warning about unknown proposal
`agentsWindowActivation` belongs to `github.vscode-pull-request-github`.

The extension host started and reports eager extensions activated, but this
log has **no `github.copilot-chat` activation entry or activation-failure stack**.
The available evidence is a static validation diagnostic before any observed
Copilot activation attempt. It does not establish activation-fatal
incompatibility, and it is not sufficient to call the mismatch harmless.
The logs do not establish the cause of deferred/absent activation.

Next, after human trust review, inspect Running Extensions and these scoped
logs for an actual activation attempt before assuming the package can run.
If activation itself requires sign-in, disclose that a pre-login activation
verdict is unavailable. If an actual fatal compatibility error appears, use
a supported matching official build/package rather than enabling proposal
bypass flags. Keep sign-in/account readiness and the minimal model-budget
paint step separate. This diagnostic used zero GUI actions, settings changes
or model prompts. Public proposal names, counts and file hashes are preserved
in `activation-diagnostic.json` under the study artifacts.

## Evidence and proposed skill deltas

Raw evidence is under
`projects/desktop-plugin-ui/artifacts/capability-study-20261025/copilot/`:
`inventory.json`, `inventory-initial-decoding.json`, `sdk-protocol.json`, `acp-protocol.json`,
`acp-protocol-initial-harness-error.json`,
`acp-protocol-offline-config-failure.json`, `webview-launch.json`, and
`webview-contract-001.json`. No earlier fixture/run was overwritten.
The initial inventory used the shell's default text decoding; its raw record
is retained. The current inventory explicitly decodes CLI output as UTF-8.

Proposed changes for the parent to assess, without a canonical edit here:

1. Update current CLI inventory to 1.0.103 while preserving old builds as dated
   evidence.
2. Explain the SDK renderer opt-in/runtime-gate distinction and keep default
   capability flags scoped to their consumer connection.
3. Add fresh callback and webview state/theme/action findings at their precise
   layers; retain restart, full theme matrix and native/chat/canvas paint gaps.
4. Record task-profile limitations, including automatic shared storage.
5. Preserve the human authentication/trust and model-budget gate; an account
   blocker is not a product-wide UI exclusion.

Current research supports choosing a practical surface; it does not establish
every Copilot feature, entitlement, actual signed-in MCP App, native canvas,
OS permission effect, real download/navigation, screen-reader application,
full accessibility conformance or representative-user acceptance.
