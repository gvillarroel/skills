# Create Pi extensions with native interactions

Use this route for Pi Coding Agent, not Pi Durable or another assistant's
plugin manifest. Snapshot: Pi **1.4.0**, Node **24.18.0**, Windows, October 25,
2026. Use the [version preflight](#validate-interaction-and-evidence), installed
declarations and matching release docs before using APIs from another version.
Older releases may use different
package names or schema imports.

## Contents

- [Choose the smallest entry point](#choose-the-smallest-entry-point)
- [Native command with dialog and argument fallback](#native-command-with-dialog-and-argument-fallback)
- [Account for the frontend](#account-for-the-frontend)
- [Keep installation local](#keep-installation-local)
- [Validate interaction and evidence](#validate-interaction-and-evidence)

## Choose the smallest entry point

Start with one TypeScript file exporting a default `ExtensionAPI` factory.
Use `registerCommand` for a user-invoked deterministic action and native
dialogs for a small choice. Add `registerTool` only when the model must call
the operation; its model-facing description, parameter schema and result are
separate from command presentation. Both can call the same ordinary function.
An extension executes within Pi's process and OS permissions. It is not a
browser iframe or a filesystem sandbox.
[Extension contract](https://github.com/earendil-works/pi/blob/v1.4.0/packages/coding-agent/docs/extensions.md).

Use a custom terminal component only when native dialogs cannot express the
interaction. Keep normal editor keys, focus, Escape, terminal-width handling
and disposal intact. Do not add a web server, React application or MCP adapter
to implement a selector. Keep long-lived resources out of the registration
factory; initialize them only when needed and dispose them idempotently on
`session_shutdown` and local cancellation.

## Native command with dialog and argument fallback

Save as `view-mode.ts` in the requested output workspace, outside this skill.
This example changes an in-memory display preference; reopening the runtime
resets it. It does not install anything or write files.

```typescript
import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";

export default function (pi: ExtensionAPI) {
  let mode = "compact";
  pi.registerCommand("view-mode", {
    description: "Choose compact or detailed output; /view-mode [compact|detailed]",
    handler: async (args, ctx) => {
      const choices = ["compact", "detailed"];
      let next = args.trim();
      if (!next && ctx.hasUI) {
        next = (await ctx.ui.select(`Output: ${mode}`, choices,
          { timeout: 30000 })) ?? "";
        if (!next) return;
      }
      const valid = choices.includes(next);
      const message = valid ? `Output mode: ${next}`
        : "Use /view-mode compact or /view-mode detailed.";
      if (valid) mode = next;
      if (ctx.hasUI) ctx.ui.notify(message, valid ? "info" : "warning");
      else pi.sendMessage({ customType: "view-mode", content: message,
        display: true }, { triggerTurn: false });
    },
  });
}
```

Run `pi --extension ./view-mode.ts`, then `/view-mode`. TypeScript loads
directly; no compilation or dependency install is needed for this example.
An explicit argument bypasses the selector. A cancelled or timed-out selector
returns without changing the preference. A spelling error gives a usable
command instead of silently selecting a default.

Calling this command does not require a model turn. `sendUserMessage()` always
starts model work; use it only when requested behavior needs that work.
`sendMessage(..., { triggerTurn: false })` stores model-visible custom content
without starting a turn. For persistent private extension state, use an
appropriate custom entry or external store instead of model-visible messages.
Use a separate small domain function when implementing real operations so
tests can exercise them without terminal rendering.
[API and state details](https://github.com/earendil-works/pi/blob/v1.4.0/packages/coding-agent/src/core/extensions/types.ts).

## Account for the frontend

| Mode | Supported interaction | Required fallback |
| --- | --- | --- |
| `tui` | Native dialogs and custom terminal components | Exercise narrow/wide terminals, keyboard cancellation and focus. |
| `rpc` | Dialogs and notifications through `extension_ui_request` / `extension_ui_response` | Client must implement the requested method and match IDs; test cancellation and timeout. |
| `json` / `print` | No interactive UI | Accept explicit arguments and emit structured/text results, or give the exact supported command. |

`ctx.hasUI` is **true in RPC** because dialogs are forwarded. Guard a real
terminal component with `ctx.mode === "tui"`. RPC `custom()` returns
`undefined`; terminal input callbacks and several layout methods are no-ops.
String-array widgets can be forwarded, while component factories cannot.
Successful JSON transport establishes no native terminal painting or custom
RPC-client rendering.
[RPC UI contract](https://github.com/earendil-works/pi/blob/v1.4.0/packages/coding-agent/docs/rpc-extension-ui.md).

## Keep installation local

Use `pi -e ./view-mode.ts` for a one-invocation preview. For project discovery,
place one entry at `.pi/extensions/view-mode.ts` or
`.pi/extensions/view-mode/index.ts`, after resolving normal project trust.
Avoid discovering the same implementation twice through a wrapper and a
separate explicit path.

For a multi-file package, put runtime dependencies beside its entry and use
an ordinary `package.json` with an explicit resource declaration:

```json
{
  "name": "project-tools",
  "private": true,
  "type": "module",
  "pi": { "extensions": ["./src/extension.ts"] },
  "peerDependencies": { "@earendil-works/pi-coding-agent": "*" }
}
```

Preview the package by explicit path. If project registration is requested,
`pi install --local ./project-tools` records it in project settings. A local
source is referenced in place, not copied or dependency-installed; install
its own non-host dependencies within that project when needed. Pi-provided
packages belong in peer dependencies rather than a second bundled runtime.
Do not use a personal installation to satisfy a project-only task.
[Package scope and dependencies](https://github.com/earendil-works/pi/blob/v1.4.0/packages/coding-agent/docs/packages.md).

## Validate interaction and evidence

For Pi preflight, use the bundled [probe_runtime.py](../scripts/probe_runtime.py)
version-only inventory instead of chaining
manual PATH and compiler probes:

```text
uv run --script <bundle>/scripts/probe_runtime.py --host pi
```

Replace `<bundle>` with this skill's actual path. Read `passed`, each check's
`status`, `version` and resolved argv. Python runs the inventory helper; it is
not a Pi extension dependency. The helper never probes `tsc`: Pi loads the
extension's TypeScript directly. Do not add a compiler check or a no-op success
suffix to hide a failed probe. Missing/unresolvable tools return diagnostic
JSON and exit 0 by default; they are still `passed:false`. Use
`--fail-on-missing` for CI. A version command that actually fails, times out or
returns unexpected output exits 1 even in diagnostic mode. Keep that failure
visible and diagnose the named runtime before using it. No package, session,
model, authentication or global configuration action is performed.

For commands that edit or commit shared state through native dialogs, use
[pi-stateful-actions.md](pi-stateful-actions.md) and its small guarded-intent
helper. Capture authority before the first await and revalidate before applying
both edited input and confirmation; test an intervening edit to the same row.

1. Load explicitly with discovery disabled. For isolated checks, set
   `PI_CODING_AGENT_DIR` to a disposable directory inside the test workspace,
   then run the installed CLI with:
   `--offline --mode rpc --no-session --no-context-files --no-extensions --no-skills --no-prompt-templates --no-themes --no-mcp -e ./view-mode.ts`.
   When spawning on Windows, invoke `node` with Pi's installed JavaScript CLI
   entry; shell wrappers are not portable subprocess executables.
2. Send LF-delimited `get_commands`, then
   `{"id":"choose","type":"prompt","message":"/view-mode"}`.
   Verify the named command appears in `get_commands` before dispatch; if it
   is absent, repair loading instead of letting the request become model work.
   Reply to the emitted selector with
   `{"type":"extension_ui_response","id":"<request-id>","value":"detailed"}`.
   Test a second selector with `cancelled: true`, an invalid argument and an
   explicit valid argument. Require handled prompt responses and no
   `agent_start` or `turn_start` event. A handled response alone does not prove
   extension code never starts independent model work.
3. Test `--mode json --print` with `/view-mode compact`; require the exact
   custom result and no model-turn events. Exercise a mocked no-UI missing
   argument separately. Never print extra non-JSON diagnostics to RPC stdout.
   In Git Bash/MSYS, set `MSYS_NO_PATHCONV=1` when a slash command is a CLI
   positional argument; otherwise `/command` can become a filesystem path and
   miss the native handler. Prefer RPC JSON on stdin or a direct Node argument
   array for deterministic checks. `--offline` disables startup networking,
   not model requests; `--no-tools` is not an inference barrier either. Require
   the expected custom result and handled-command disposition where available,
   plus zero agent/turn events. A process exit code alone can hide an accidental
   provider attempt or error; retain the failed output and correct invocation.
4. Perform actual TUI keyboard, Escape, resize and screen-reader/terminal
   checks when terminal usability is claimed. Mark unperformed checks
   `untested`, retaining transport and engine evidence separately.
5. Apply [the ten-heuristic review](usability-and-color.md) to the real task:
   visible current state and completion, a reversible exit, valid choices,
   recoverable errors and optional expert arguments. Use host theme roles
   for native controls. Exact palettes apply only to styling the extension
   actually owns.

Reference example evidence: offline Pi 1.4.0 RPC passed **9/9** checks for
discovery, selector contract, state, cancellation, argument recovery, direct
argument, handled responses and zero model turns. Mode checks passed **6/6**:
three mocked branch checks plus real JSON print exit/result/no-inference
checks. These tests do not establish actual TUI painting, focus, resize,
screen-reader behavior, project installation or arbitrary RPC-client paint.
[RPC framing and command dispositions](https://github.com/earendil-works/pi/blob/v1.4.0/packages/coding-agent/docs/rpc-commands.md).
