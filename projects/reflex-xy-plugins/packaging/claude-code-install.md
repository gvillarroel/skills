# Reflex XY for Claude Code

This plugin includes a native Mod and the canonical `reflex-xy` runtime skill.
It requires a Claude Code release with Mods support, `uv`, and Python 3.11+.
Validation used Claude Code 2.1.302 and XY 0.0.8. No Node installation is needed
for production use; Claude loads the TypeScript module directly.

1. Extract this ZIP into a permanent directory.
2. From your working project, launch Claude with the extracted plugin:

```powershell
claude --plugin-dir "C:/path/to/reflex-xy-claude-code"
```

3. Run `/xy-chart`, `/xy-chart scatter`, or `/xy-chart sankey`.
   The first view shows the native chart, Save image and More options.
   Open More options to change the palette, try samples, render again or inspect
   artifact files. Samples replace the current data and are labelled accordingly.
   Every new command or tool call defaults to Colorset 1, even after a previous
   Colorset 2 chart. Use Colorset 2 only by explicit selection or a command such
   as `/xy-chart colorset2 scatter`.
4. Ask Claude to use `render_chart` with your actual data, or run
   `/xy-chart @charts/request.json` for a JSON specification in your project.

Save image writes a new PNG in the current project's `.xy-charts/exports/`
directory and confirms it inside the pane. Each save gets a unique filename;
existing files and the original XY image remain intact. The saved path and an
Open folder action are available in More options.

The slash command and native pane controls use local deterministic code. Sample
selection, palette edits, rerendering, saving and copying do not request a model
or submit a conversation turn. Asking Claude to design or explain a chart still
uses the normal model. The plugin does not attempt to bypass account limits.

The first render can download the pinned Python dependency through `uv`.
Configure the plugin's `uvExecutable` if `uv` is not on the execution host's PATH.
The engine takes declarative data and chart options, never submitted Python.

Artifacts are saved in the working project's `.xy-charts/`: interactive HTML,
SVG, PNG, editable Python and JSON. The pane displays native SVG in Desktop's
Code tab and VS Code; a compatible terminal receives PNG. These are the actual
native XY exports. Full XY browser hover and zoom live in the optional Open HTML
export in browser action under More options, rather than the default workflow.
The native Mod does not embed a DOM/WebGL app or replace XY with a custom plotter.
Source buttons copy paths without executing Python files. Exported HTML is a
snapshot; Python callbacks need a live host.

This is a Claude Code plugin. For Claude Desktop's ordinary chat, install the
separate `reflex-xy-claude-desktop.mcpb` extension.

Use `claude plugin validate <plugin-folder> --strict` and
`claude plugin test <plugin-folder>` for native scanner and hook tests.
The shipped tests do not claim acceptance by the installed Desktop painter.
They also include a standalone image saver check:

```powershell
$env:XY_TEST_OUTPUT_DIR = 'C:/your/project/artifacts/xy-save-tests'
uv run --script tests/test_save_image.py
```
