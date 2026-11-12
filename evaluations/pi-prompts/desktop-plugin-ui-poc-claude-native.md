Create a runnable local Claude Code Mod named `release-review` for inspecting a
tiny release queue. Target the Claude Code terminal and Claude Desktop Code
tab, using their supported native controls. This is executable plugin work,
not an implementation blueprint or an MCP server.

Use these immutable synthetic records: `R-71` ready, `R-72` blocked, and `R-73`
ready. Register `/release-review`. With no argument, request a native pane with
ID `release-review`, a native selector keyed `view` with All checks, Ready and
Blocked choices, a readable result, and a Cancel control keyed `cancel`.
Selection filters immediately; cancellation leaves the records unchanged and
exits the view without starting another action. Keep one obvious main task.
Support `/release-review all`, `/release-review ready`,
`/release-review blocked` and `/release-review help` as direct plain-text
routes without opening the pane. Invalid arguments must give actionable help.
If the pane cannot be placed, return all rows with usable direct-command
instructions. All authored copy must be English. Keep controls keyboard
friendly and respect host-owned themes rather than claiming exact palette
pixels for native controls.

Create exactly these required artifacts (supporting files are allowed):

- `poc/.claude-plugin/plugin.json`
- `poc/hooks/hooks.json`
- `poc/hooks/register.ts`
- `poc/package.json`
- `poc/tests/native.test.ts`
- `poc/USAGE.md`
- `poc/review.json`

Use no model generation, server, external service, network, database, persistent
application state or added package dependency for the plugin's normal actions.
The installed `claude` executable is available for help, strict validation and
native-engine tests. Run `claude plugin validate poc --strict --json` and
`claude plugin test poc`, repair actual code/test failures before finishing,
and preserve the failed checks in the review. Do not install or activate the
plugin globally. Do not start interactive Claude, authenticate, run Claude
inference, inspect installed package source, or open OS/application settings.
Put any host configuration, logs or cache used by tests in a dedicated folder
inside this workspace. No external repository or sibling skill may be read.

Native tests must exercise each filter's exact record IDs and values, direct
arguments, invalid arguments, no-placement fallback, cancellation, safe repeated
activation, and the supported native trees on terminal and desktop surfaces.
Include a test for command registration; a matched `command.run` handler alone
does not prove the command was registered. Distinguish native engine execution
from actual keyboard/focus/paint in an installed frontend.

`USAGE.md` must give local load and test commands, required host version, the
task and interaction flow, actual verification limits and a short H1-H10 review.
`review.json` must contain `artifacts`, `checks` (name, command or method,
expected, actual, status), `heuristics` (H1-H10 with interaction, finding and
evidence), `complexity` (initial_controls, required_decisions, primary_actions,
added_runtime_processes, added_dependencies, rationale),
`host_paint_verified:false` and `user_testing_performed:false`. Report real
execution results and retain failures; do not convert an unperformed paint
check into a failure or a pass. Use the default palette policy in the skill,
with an honest native styling boundary.

Read this prompt and the copied read-only `skills/desktop-plugin-ui/` bundle.
Use only the focused references needed for this host. Stay offline. Do not
modify the copied skill. Write the plugin, test scratch files and outputs only
inside this workspace, outside the copied bundle.
