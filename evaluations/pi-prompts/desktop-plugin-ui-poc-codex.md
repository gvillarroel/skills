Create a small runnable local Codex plugin named `release-checks-poc`. It helps
inspect three synthetic release checks: `R-21` ready, `R-22` blocked, `R-23`
ready. Deliver actual source and a distributable bundle, not a blueprint.

Use a supported portable plugin package with a bundled local stdio MCP server.
The plugin must work usefully in a text client. Implement `release_list` with
an explicit `view` enum (`all`, `ready`, `blocked`), concise text plus exact
structured results, and a clear error for an invalid view. Implement
`release_choose` to request a supported native MCP form containing that view
and a confirmation boolean. Accept, decline and cancel must be distinct;
decline/cancel must not choose or run a default. Its successful result returns
the chosen rows. A client declining elicitation must still be able to use
`release_list` directly. No inference, provider, browser, external service or
persistent business state is needed for these operations.

Create exactly these required paths (additional source/test files are allowed):

- `poc/plugin.json`
- `poc/mcp.json`
- `poc/package.json`
- `poc/package-lock.json`
- `poc/src/server.ts`
- `poc/dist/server.js`
- `poc/skills/release-checks/SKILL.md`
- `.agents/plugins/marketplace.json`
- `poc/USAGE.md`
- `poc/review.json`

Keep the manifest and MCP configuration schemas distinct and correct. The
marketplace must resolve this plugin inside this workspace, have the required
installation/authentication/category metadata, and require no personal catalog.
The packaged entry must be relocatable: extract/copy `poc/` into a fresh local
folder and run it without the original checkout or source dependencies. Bundle
the runtime dependencies. A declared Node prerequisite is acceptable.

The skill in the plugin must describe how to use its tools, not pretend that
text/JSON or an MCP callback proves a sidebar or form painted. Do not build a
custom frontend, HTML UI, HTTP listener or extra service for this text-first
PoC. All authored visible and accessible copy and documents must be English.
Use the default palette only where styling is actually authored; preserve
native host theme/permission ownership.

Include local scripts for build and protocol tests. Run `npm run build` and
`npm test` from `poc/`. Test initialize, tool discovery, each list filter,
invalid input, accepted form, declined form and cancelled form. Validate the
manifest/marketplace paths and relocatable bundled entry. `review.json` must
record actual checks with command/method, expected, actual, status and layer;
H1-H10 with concrete interaction findings; essential controls and architecture
choices; remaining checks; and `host_paint_verified:false` and
`user_testing_performed:false` unless those were genuinely performed. Do not
equate a self-authored passing JSON flag with independent acceptance.

You may fetch necessary primary documentation and npm dependencies, using a
cache inside this workspace. You may run installed version/help/native commands
with task-local state inside this workspace, but do not invoke another model,
install globally, read credentials, change host/personal configuration, or
activate a plugin in an existing user environment. Keep every generated file,
dependency cache and scratch artifact inside this workspace.

The only instructional source is this task and the copied read-only
`skills/desktop-plugin-ui/` bundle. Do not discover other skills, repository
examples, project artifacts or installed package sources. Ordinary installed
tools and declared dependency APIs are available. Keep the copied skill
unchanged and never write output inside it. Explain any actual host gate
without claiming an unperformed check failed or a whole product is unsupported.
