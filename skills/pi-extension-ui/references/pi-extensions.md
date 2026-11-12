# Build for the actual Pi mode

Inherited baseline: Pi 1.4.0, Node 24.18.0, Windows, October 25, 2026.
Read installed help/types and matching release docs before using other versions
only when that source access is allowed by the task.
[Extensions](https://github.com/earendil-works/pi/blob/v1.4.0/packages/coding-agent/docs/extensions.md),
[API types](https://github.com/earendil-works/pi/blob/v1.4.0/packages/coding-agent/src/core/extensions/types.ts).

## Contents

- [Native controls](#choose-and-compose-native-controls)
- [Load and validate](#load-and-validate)
- [Real RPC checker](#reuse-the-real-rpc-checker)

## Choose and compose native controls

Export a default factory accepting `ExtensionAPI` from
`@earendil-works/pi-coding-agent`. Use `registerCommand` for deterministic
user-invoked work. A model-facing `registerTool` has a separate schema and
description; add it only when the model must call the operation. Both routes
can share ordinary domain logic. Extensions run with the process's permissions,
not a browser sandbox. Keep resources lazy and cleanup idempotent.

Prefer `ctx.ui.select`, `input`, and `confirm` for small decisions. Handle
undefined, timeout, Escape, and cancellation without submitting a default.
Use `setStatus(key, text)` for concise persistent state and `setWidget(key,
lines, options)` for task context; clear keyed surfaces with `undefined`.
Pair status with a details command instead of a permanently tall widget.
Header/footer/editor replacements must preserve other extensions' controls,
branch/model/context information, host keys, focus, and notifications.

For a custom TUI, use terminal column-width utilities, propagate input focus,
handle resize, wide text and theme invalidation, and finish through `done()`.
Hiding an overlay alone does not complete its pending interaction. Test both
regular/fullscreen keyboard behavior and dispose resources on shutdown.
[TUI contracts](https://github.com/earendil-works/pi/blob/v1.4.0/packages/coding-agent/docs/tui.md).

| Mode | Contract |
| --- | --- |
| `tui` | Native dialogs and supported custom terminal components. |
| `rpc` | UI requests/responses need client callbacks and matching IDs; custom component factories do not paint. |
| `json` / print | Accept explicit arguments and return useful text or structured output; no interactive dialog. |

`ctx.hasUI` is true in RPC. Use `ctx.mode === "tui"` for terminal factories.
RPC `custom()` returns undefined and several layout methods are no-ops.
[RPC UI contract](https://github.com/earendil-works/pi/blob/v1.4.0/packages/coding-agent/docs/rpc-extension-ui.md).

`sendUserMessage()` starts model work. For a displayed custom result without a
new turn, use `sendMessage(..., {triggerTurn:false})`; its content is still
model-visible. Keep private durable state in an appropriate store/custom entry.
An in-memory variable resets with the runtime. Do not label it persistent.

## Load and validate

Preview with `pi -e ./view-mode.ts`. Project discovery can use
`.pi/extensions/view-mode.ts` after normal trust resolution; avoid loading the
same implementation twice. A package declares `pi.extensions` in package.json
and uses host packages as peer dependencies. `pi install --local ./package`
references local source; it does not copy it or install its dependencies.
[Packages](https://github.com/earendil-works/pi/blob/v1.4.0/packages/coding-agent/docs/packages.md).

Keep test state inside the workspace with task-local `PI_CODING_AGENT_DIR`.
Load explicitly with `--offline --mode rpc --no-session --no-context-files
--no-extensions --no-skills --no-prompt-templates --no-themes --no-mcp -e
./view-mode.ts`. On Windows spawn Node with the installed JS CLI entry rather
than executing a PowerShell wrapper as a subprocess.

Send LF-delimited `get_commands`, verify registration, then send a prompt
whose message is the exact registered slash command. Answer a selector with
`extension_ui_response` and the emitted request ID; test selected, cancelled,
invalid, and explicit-argument paths. Require the expected result, handled
command disposition, and zero `agent_start`/`turn_start` events. Test JSON print
with a direct argument too. `--offline` and `--no-tools` are not inference
barriers. Preserve slash arguments through MSYS or prefer stdin JSON/direct argv.
[RPC commands](https://github.com/earendil-works/pi/blob/v1.4.0/packages/coding-agent/docs/rpc-commands.md).

For the tested Pi 1.4.0 command route, the response to a handled prompt is:

```json
{"id":"choose","type":"response","command":"prompt","success":true,"data":{"disposition":"handled"}}
```

Assert `response.data.disposition === "handled"`, not a top-level disposition
or the invented value `"command"`. Registration discovery is in
`response.data.commands`. These are transport assertions; check the actual
selection notification/state and absence of model-turn events independently.

Historical RPC checks passed command discovery, selection, cancellation,
argument recovery, and zero model turns. That does not establish actual TUI
pixels, focus, resize, screen-reader behavior, or a custom RPC client's paint.

## Reuse the real RPC checker

Run `python <bundle>/scripts/check_rpc_command.py --extension view.ts
--command workflow-view --steps steps.json --print-args "enrich metrics"
--expect-print "180 ms" --report rpc-review.json` for an authored deterministic
command. Keep paths/output outside the read-only bundle. The checker uses the
installed JS entry from the bundled runtime probe, disables ambient resources,
and verifies real registration, matching dialog IDs, handled responses, exact
notifications and inference-free JSON print. It does not read installed docs.

Use a workspace-local steps array; adapt actual offered choices and expected
text to the extension:

```json
[
  {"answers":["enrich","metrics"],"expect":["180 ms","150 ms"]},
  {"answers":["store",null],"expectNoNotify":true},
  {"answers":[null],"expectTitle":"current: enrich","expectNoNotify":true},
  {"args":"store metrics","expect":["no latency"]}
]
```

Do not guess a top-level disposition or use raw stdout in a JSON event stream.
Keep command data assertions separate from host painting. A failed authored
check must remain in the validation history even after correcting the source.
