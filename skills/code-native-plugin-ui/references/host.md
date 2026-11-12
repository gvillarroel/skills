# Native Claude Code surface boundaries

Review current help, installed declarations, and the exact frontend before
implementation. [Plugin overview](https://code.claude.com/docs/en/plugins),
[native creation](https://code.claude.com/docs/en/plugins/mods/create),
[elements](https://code.claude.com/docs/en/plugins/mods/reference#elements),
[native tests](https://code.claude.com/docs/en/plugins/mods/test).

The inherited October 25, 2026 snapshot used Claude Code 2.1.302 on Windows.
Native engine tests accepted supported Box/Text/Select/Button structures.
Raw HTML was refused. Terminal Svg was refused while Image/Raster validated;
Desktop Code and VS Code accepted Svg and refused terminal Image/Raster.
Client nodes and several props also differed across frontends. These are
bounded engine observations, not current rendering guarantees or universal
API exclusions. Use the installed host's type definitions and tests.

Use `.claude-plugin/plugin.json` for plugin metadata and `hooks/hooks.json`
with a real hooks module for a Mod. Components stay at the plugin root.
Supported namespaces and native constructors are statically analyzed. Keep
literal event names/matchers, direct supported `$` calls, and explicit surface,
component, and `requestId` guards. Mount test fixtures carry `plugin`, but
actual `ui.render` events in the tested build do not. Do not guard a render
with an invented `event.plugin`; it suppresses real UI. Do not alias or reflect
on the API.

## Preserve an independently usable route

For a list/filter interaction, keep `/command all`, a valid filtered argument,
help, and invalid-argument recovery. If `ui.open()` is denied or unplaced,
return useful text. A close/reopen must restore the intended initial state.
Let unrelated commands and panes continue through the host chain.

For writes, separate draft from commit, preserve cancel semantics, and bind a
late confirmation to the version it actually reviewed. Add only the controls
the task needs; do not add a save workflow to a read-only viewer.

Use task-local `CLAUDE_CONFIG_DIR` for isolated checks. `claude plugin validate
<plugin-dir> --strict --json` checks the package, and `claude plugin test
<plugin-dir>` exercises authentic native events without a model turn. Neither
proves visible keyboard focus, terminal dimensions, account enablement, or
Desktop/VS Code paint. Use the known public command for any headless receipt
check and inspect the receipt's turns, API milliseconds, and cost. Unknown or
rewritten slash commands can become model prompts; prefer direct argv and
preserve literal arguments on Windows/MSYS.
