---
name: code-native-plugin-ui
description: Creates and validates native Claude Code plugin commands, Mods, panes, and controls for the terminal, Desktop Code tab, or Claude VS Code surface. Use for native plugin UI authoring and host compatibility diagnosis; ordinary Claude Desktop Chat uses MCP Apps.
---

# Claude Code Plugin UI

Start with the pending human decision. Read
[micro-decisions.md](references/micro-decisions.md) for the default agent UI:
one bounded question, only decision-relevant evidence, and a typed result
returned to the agent. Use a full workspace only when the user requests it.

When authoring or refining presentation, follow
[craft-by-surface.md](references/craft-by-surface.md) for the actual
styling owner, supported mechanism, fallback and acceptance checks.

For graphs, charts, dense tables, or linked multi-panel interfaces, read
[rich-interfaces.md](references/rich-interfaces.md) before choosing the layout.
Apply its graph/chart recipes, host alternatives, state rules and pixel critique.

For coordinated investigations, dense matrices and reviewed actions, read
[complex-workspaces.md](references/complex-workspaces.md).

Identify terminal, Desktop Code tab, or VS Code before selecting controls.
Read [host.md](references/host.md) for bounded surface support, then
[native-authoring.md](references/native-authoring.md) for the tested starter and
real event contracts. Read neither another assistant's manifest nor web UI
instructions to implement a native pane.

1. Choose a skill for model-led guidance, a native command for deterministic
   work, and a Mod only when persistent native interaction is needed.
2. Copy [claude-native](assets/templates/claude-native/) to the requested output
   workspace and adapt domain data, identity, copy, and authentic native tests.
   Claude loads TypeScript directly; the starter needs no web service/build.
3. Preserve registration `name`, execution `command`, explicit mount guards,
   supported constructors, text fallback, cancellation, and unrelated panes.
4. Apply [interaction-quality.md](references/interaction-quality.md). Preserve
   host paint/theme and check behavior in every claimed native surface.
5. Run strict plugin validation and the native test engine with task-local
   configuration. Use a known registered direct command for a receipt check;
   inspect actual inference counters. Check real paint separately.

Deliver runnable plugin sources, authentic tests, exact requested paths, and
load/run commands. A native engine pass does not establish Desktop placement,
terminal pixels, focus, accessibility, account installation, or a different
frontend. Keep failed probes and unperformed host checks explicit.
