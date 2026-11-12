# Copilot empirical UI investigation

Date: October 24, 2026, America/New_York (raw UTC records cross into October 25).
Model used for Copilot/SDK tests: none. Model prompts: zero. The native terminal
used an offline BYOK configuration pointed to an unreachable localhost port;
the separate SDK probe counted all localhost provider requests and observed zero.
No GitHub device code, credential, account token, or private account content was
collected. Scope: Windows, GitHub Copilot CLI, SDK protocol gates, and VS Code
extension webviews. Signed-in Copilot chat MCP App rendering is not a passed test.

## Installed environment

- Existing WinGet Copilot CLI: `--version` reports 1.0.75, ACP reports 1.0.73.
- Task-local official npm `@github/copilot-win32-x64@1.0.103`: CLI and ACP agree.
- Task-local official `@github/copilot-sdk@1.0.26`, installed only for its runtime
  API test. Its package declares CLI 1.0.103 compatibility.
- Task-local VS Code archive: 1.143.1,
  commit `e646868227c3e3a9e3f24277c8c7220be42c0be7`.
- The VS Code archive contains built-in GitHub Copilot Chat 0.71.0, at
  `vscode/e646868227/resources/app/extensions/copilot/package.json`.
- Marketplace installation attempted Copilot Chat 0.48.1 and was rejected as a
  downgrade of the built-in extension. Nothing was removed to bypass that guard.
- No globally installed app, account setting, or extension configuration was
  altered. User data, extensions, CLI state, downloaded executables and packages
  live under `projects/desktop-plugin-ui/artifacts/cross-assistant/copilot/`.

Primary download sources:

- Official VS Code archive retrieval endpoint: HTTPS host
  `update.code.visualstudio.com`, path `/latest/win32-x64-archive/stable`.
  A final independent HEAD request returned HTTP 200 and
  `application/octet-stream` on the investigation date. This is a binary
  retrieval record, not a documentation citation. The citation checker does
  not trust this download subdomain as a primary documentation source.
- [Official GitHub SDK source](https://github.com/github/copilot-sdk).
- npm packages in the GitHub-owned `@github` scope, with the exact versions above.

## Repeatable tests

From the repository root:

```powershell
uv run --script projects/desktop-plugin-ui/cross-assistant/copilot/probe-copilot.py
uv run --script projects/desktop-plugin-ui/cross-assistant/copilot/probe-copilot.py --executable C:\Users\villa\dev\skills\projects\desktop-plugin-ui\artifacts\cross-assistant\copilot\cli103\package\copilot.exe --output-name copilot-cli103-zero-model.json
node projects/desktop-plugin-ui/cross-assistant/copilot/probe-sdk.mjs
```

The CLI probe runs version/help/plugin/MCP/limits commands, starts actual ACP,
sends `initialize` followed by the deliberately invalid `ui/show`, then exits
without a session or model prompt. Both versions negotiate image=true,
audio=false, embeddedContext=true, and reject `ui/show` with -32601. That failure
only concerns the tested method, not every possible Copilot UI mechanism.

For the native terminal probe, copy `cli-extension/extension.mjs` to the
task-local `tui-home/extensions/ui-evidence/extension.mjs`. Launch task-local CLI
1.0.103 with `--experimental --no-custom-instructions --no-auto-update
--disable-builtin-mcps --model ui-evidence-no-inference`, with `COPILOT_HOME`
pointing to `tui-home`, `COPILOT_OFFLINE=true`,
`COPILOT_PROVIDER_BASE_URL=http://127.0.0.1:9/v1`, and
`COPILOT_MODEL=ui-evidence-no-inference`. Accept trust for this synthetic fixture
only, then interact with four real host dialogs:

1. Confirmation: Enter selected Yes and returned true.
2. Selection: Down + Enter selected Beta and returned `"Beta"`.
3. Input: `synthetic` + Enter returned that exact string.
4. Cancellation: Escape returned null.

`/usage` displayed zero messages; `/exit` closed the terminal. No natural-language
prompt was entered. Real TUI capabilities were elicitation=true, MCP Apps=false,
canvases=true, extensions=false. Canvas painting was not tested. The SDK consumer
with no renderer reported all three UI capabilities false; `confirm` threw.
Adding an explicit consumer elicitation callback made that capability true and
returned the supplied `confirmed:true`. This callback test is not a native UI.

For VS Code's actual extension-host checks:

```powershell
$TaskArtifacts = 'C:\Users\villa\dev\skills\projects\desktop-plugin-ui\artifacts\cross-assistant\copilot'
$TaskProbe = 'C:\Users\villa\dev\skills\projects\desktop-plugin-ui\cross-assistant\copilot\vscode-probe'
& "$TaskArtifacts\vscode\bin\code.cmd" --user-data-dir "$TaskArtifacts\vscode-data" --extensions-dir "$TaskArtifacts\vscode-extensions" --extensionDevelopmentPath $TaskProbe --extensionTestsPath "$TaskProbe\test.cjs" --skip-welcome --skip-release-notes --disable-workspace-trust --new-window $TaskProbe
```

All five final checks passed: runtime inventory; disabled scripts; enabled
scripts/button/postMessage with no Node globals and blocked top-document access;
CSP inline-script denial; disposal event. Test window title was
`[Extension Development Host] vscode-probe - Visual Studio Code`; it exited.
The extension test host's runtime inventory did not expose GitHub Copilot, so
these passes cannot establish Copilot chat App rendering.

## Retained evidence and failures

All raw files below are under the ignored task artifacts directory:

- `copilot-cli-zero-model.json`, `copilot-cli103-zero-model.json`: commands and
  full sanitized ACP requests/responses.
- `vscode-extension-host.json`: five final passes.
- `vscode-extension-host-initial.json`: initial wrong expectations retained:
  Copilot was not exposed in the extension test runtime; the immediate webview
  parent is a readable wrapper. The top application document does raise
  SecurityError. The corrected test checks the actual intended boundary.
- `copilot-sdk-no-inference.json`: final gate/callback result, providerRequests=[];
  `copilot-sdk-no-inference-initial.json`: startup rejected a BYOK configuration
  without an explicit model; `copilot-sdk-no-inference-wrong-confirm-field.json`:
  callback field `value` returned false instead of `confirmed`.
- `tui-home/ui-extension-result.json`: native form results and capabilities;
  `tui-confirm-initial.json`: first confirmation-only pass;
  `tui-usage.ansi.txt`: actual zero-message usage output.
- CLI 1.0.103 rejected `--no-remote` as removed. The ACP probe was repaired to use
  supported launch options. No global binary was updated.
- First native terminal setup used a relative copy path from the wrong cwd;
  it failed before the extension loaded. The file was copied with an absolute
  task-owned path before trust was accepted. No inference occurred.

Node syntax checks passed for the SDK probe, native extension, and VS Code test.
The canonical `copilot-limits.md` source checker passed with the exact verified
Copilot/VS Code URLs explicitly allowed. The parent task owns repository-wide
validation and isolated forward evaluation after integrating all assistants.
