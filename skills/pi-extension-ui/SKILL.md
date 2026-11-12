---
name: pi-extension-ui
description: Creates, improves, and validates Pi Coding Agent TypeScript extensions with commands, dialogs, widgets, and supported terminal controls. Use for Pi TUI, RPC UI contracts, stateful actions, or noninteractive fallbacks; model provider names do not identify the Pi frontend.
---

# Pi Extension UI

Start with the pending human decision. Read
[micro-decisions.md](references/micro-decisions.md) for the default agent UI:
one bounded question, only decision-relevant evidence, and a typed result
returned to the agent. Use a full workspace only when the user requests it.

For graphs, charts, dense tables, or linked multi-panel interfaces, read
[rich-interfaces.md](references/rich-interfaces.md) before choosing the layout.
Apply its graph/chart recipes, host alternatives, state rules and pixel critique.

For coordinated investigations, dense matrices and reviewed actions, read
[complex-workspaces.md](references/complex-workspaces.md).

Build a Pi Coding Agent extension, identifying `tui`, `rpc`, `json`, or print
mode first. Read [pi-extensions.md](references/pi-extensions.md) and retain the
exact task's output paths. Use installed declarations only when the task allows
that read surface. In a skill-only or resource-restricted workspace, use the
bundled API reference/templates; do not read installed docs, examples or source.

1. Run `python <bundle>/scripts/probe_runtime.py --host pi` for a version-only
   readiness check. Inspect JSON `passed` and per-check status. Pi loads
   TypeScript directly; do not add a compiler readiness requirement.
2. Prefer one native command and built-in dialogs. Copy/adapt
   [view-mode.ts](assets/templates/pi-command/view-mode.ts) when useful. Share
   ordinary domain functions with a model-facing tool only when needed.
   For a linked graph/metric inspector, adapt
   [inspect-flow.ts](assets/templates/pi-command/inspect-flow.ts). It includes
   TUI/RPC dialogs, staged cancellation and inference-free print output.
3. Guard custom TUI with `ctx.mode === "tui"`; `ctx.hasUI` also permits RPC
   dialogs and therefore does not establish a terminal renderer.
4. For editing or committing shared data across awaits, read
   [pi-stateful-actions.md](references/pi-stateful-actions.md) and use its
   bundled guarded-intent helper or an equivalent version-bound transaction.
5. Apply [interaction-quality.md](references/interaction-quality.md). Test
   discovery, selection, invalid input, cancellation, recovery, and explicit
   arguments through the actual mode. Inspect zero model-turn evidence for
   deterministic commands. Test visible TUI separately when claimed.
   Prefer the bundled [RPC checker](scripts/check_rpc_command.py) and the
   step format in [pi-extensions.md](references/pi-extensions.md) over inventing
   RPC response shapes or a custom transport test harness.

Deliver runnable extension files and dependencies, exact output paths,
one-invocation load commands, and concise tested limits. Keep project
installation local when requested. A JSON/RPC pass does not prove terminal
paint, focus, resize, arbitrary client UI, or persistent installation.

For a formatted single-choice TUI with semantic theme colors, adapt
[micro-choice.ts](assets/templates/pi-command/micro-choice.ts).
