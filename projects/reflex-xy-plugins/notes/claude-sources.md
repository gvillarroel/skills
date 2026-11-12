# Claude XY adapter: sources and validation

Checked on 2026-10-24. The Code adapter is a Claude Code plugin containing a Mod,
two model tools, a slash command and the existing runtime skill. It is not a
plugin for the ordinary claude.ai chat interface.

## Version 0.3.0: native local actions

The Code pane now keeps its actual XY SVG/PNG preview inside the native app and
uses **Save image** as its primary action. This invokes the bundled
`scripts/save_image.py` helper with explicit argv and a bounded JSON title.
The helper copies the native PNG bytes to a unique filename in the current
project's `.xy-charts/exports/` directory. It rejects out-of-project sources,
symlink/junction redirects and malformed PNG headers, and uses exclusive file
creation so existing exports remain intact. Success is confirmed inside the
pane; the saved path and folder action remain under More options.

The optional HTML export moves behind More options and is explicitly labeled
as opening in a browser. The default flow no longer opens another application.
Palette edits, samples, rerendering, saving, copying and disclosure use local
deterministic code. The native test traps and portable harness both observe
**zero model calls and zero submitted conversation turns** for those actions.
An initial natural-language request to Claude can still use the normal model;
these checks do not claim that all account usage is free.

The current source passes strict Claude 2.1.302 plugin validation, **9/9 native
tests**, **209 portable assertions**, and **8/8 standalone saver tests**. The
saver tests include exact bytes/checksum, repeat-save uniqueness, hostile title
characters, outside sources, PNG validation, authored-file preservation and a
real symlink redirection refusal. The packaged real-renderer integration also
presses Save image for each colorset and compares the saved bytes with XY's
original output; final packaging evidence owns that result and archive identity.

The current official [Mods reference](https://code.claude.com/docs/en/plugins/mods/reference)
documents Client as a native drawing region on terminal/Desktop, with no Client
surface in VS Code. Its native API is separate from a browser DOM/WebGL runtime.
The scriptless `Svg` mode does not enable XY's JavaScript client. This adapter
therefore preserves XY's own native image export and does not invent a custom
plotter or claim native XY hover/pan/zoom. Client pointer/key machinery alone
would not establish that integration. Full XY browser interaction remains an
optional export. Installed Desktop painting and real OS folder opening remain
untested in this pass.

## Version 0.2.0: progressive chart pane

The default successful pane contains its native preview with the chart title, one
primary **Open interactive chart** button, and a collapsed **More options**
button. Palette controls, sample selection, rerendering, file actions, paths,
engine/version metadata and export warnings are hidden until the user expands
the native options button. The expansion state belongs to the current session.
The pane does not repeat the native image's title as an outer heading. A text
heading remains when a native preview is unavailable or no chart exists yet.

The optional sample selector explicitly says it replaces current data. Palette
changes and rerendering retain the displayed chart's request and observations,
including after another request fails. The default Colorset 1 rule from 0.1.1
remains unchanged; explicit Colorset 2 choices remain supported.

The empty pane offers **Create a sample chart**; an initial pending render shows
**Creating your chart…**. An export failure offers **Try again** with the same
request, while a parsing failure does not silently substitute sample data.
Errors remain visible and concise even when options are collapsed. Native
buttons supply keyboard navigation and stable keys preserve the host's current
focus; rerenders do not request autofocus. Preview images retain descriptive
alternative text. Longer diagnostics and unique, actionable export warnings
live in the options area. Routine snapshot warnings and engine/version/dimension
metadata are omitted from the pane; the detailed host boundary remains in the
help command and tool contract.

The 0.2.0 source passed strict Claude 2.1.302 plugin validation,
**8/8 native tests**, **195 portable assertions**, and official MCPB 2.1.2
Desktop manifest schema validation. Native checks exercise actual options-button
dispatch, the two-action default tree, supported surface elements, hidden
technical details, palette edits with supplied data, retained displayed data
after a rejected request, and the existing CS1/explicit-CS2 regression. Portable
checks additionally hold the process promise pending to inspect loading, test
empty/error/retry transitions, and verify expansion isolation between sessions.
Installed Desktop/VS Code paint and real OS opening remain separate acceptance
steps.

## Version 0.1.1: Colorset 1 default

Every new `/xy-chart` request, inline JSON object, `@file.json` request, and
`render_chart` tool call now chooses Colorset 1 when `colorset` is absent.
An earlier explicit Colorset 2 chart does not change that default. Colorset 2
remains available through an explicit argument, specification field or pane
selection. Edits made with the pane's preset and palette controls can retain
the palette explicitly selected for that chart.

This revision removes the parser's configurable fallback palette and the tool's
use of session palette as a fallback. The Claude Code manifest, its package
metadata and the ordinary Desktop MCPB manifest are version 0.1.1.

That revision passed strict Claude 2.1.302 plugin validation, **7/7 native
tests**, **157 portable assertions**, and official MCPB 2.1.2 Desktop manifest
validation. The added native and portable regressions switch to Colorset 2,
then submit omitted-palette commands, inline JSON, file JSON and tool requests;
each new request returns to Colorset 1. Explicit Colorset 2 and the pane edit
controls remain accepted. Earlier 0.1.0 development-package evidence below is
retained as historical evidence, not a substitute for final 0.1.1 packaging.

## Primary sources

- [Mods overview](https://code.claude.com/docs/en/plugins/mods/overview): local
  Mods extend the CLI, the Claude Desktop **Code tab**, and the VS Code extension.
  Cloud/headless execution does not provide the same pane surface.
- [Manifest reference](https://code.claude.com/docs/en/plugins-reference):
  `.claude-plugin/plugin.json`, local loading through `--plugin-dir`, plugin
  configuration, and the authoritative `plugin validate --strict` command.
- [Mods reference](https://code.claude.com/docs/en/plugins/mods/reference):
  `hooks/hooks.json` lists a module exporting `register`; the module runs without
  Node APIs. `Svg` belongs to Desktop/VS Code, while `Image` belongs to terminal.
  SVG markup is capped at 131,072 characters; the adapter also caps PNG previews
  at 2 MiB. The public declarations snapshot describes an older release, so
  exact-host validation takes precedence.
- [Mods API](https://code.claude.com/docs/en/plugins/mods/api): register commands
  and tools during `session.start`; invoke executables using an argument array
  with `process.run`, with JSON delivered on stdin and no shell expansion.
- [Native test kit](https://code.claude.com/docs/en/plugins/mods/test):
  `.test.ts` files run through Claude's own hook engine without an account,
  network or model request. Surface trees and button dispatch are tested; this
  does not test the installed Desktop, VS Code or terminal painter.
- [Public declarations](https://github.com/anthropics/claude-code/blob/main/mods/types/claude-code.d.ts):
  inspected as a read-only research artifact. Its header identifies 2.1.277.
  It lacks newer `ui.copy` declarations, so it is not used to claim a complete
  type check of the 2.1.302 adapter.

## Implementation decisions

The generated Claude distribution keeps the canonical runtime skill once at
`skills/reflex-xy/`. The Python bridge is invoked with an explicit `--skill-dir`
pointing to that copy. The source adapter contains no maintained copy of the
skill. `runtime/contract.json` supplies the renderer's full preset list; the
model can request that contract or one of ten compact skill references through
`skill_reference`. The direct `render_chart` tool accepts the declarative
contract, preserving supplied observations rather than executing submitted code.

Preview state, busy status, palette selection and artifact paths are keyed by
`session.id()` and removed on `session.end`. Different sessions cannot inherit
each other's previews. The same session can show its artifacts on several
surfaces. Output directories are fresh children of the current project's
`.xy-charts/` folder.

The `@relative/spec.json` command rejects lexical absolute and parent paths.
Host symlinks retain their normal filesystem meaning; this check is not an OS
sandbox. Bundled reference reads use an exact allowlist. Engine stdout is
validated for the schema version, palette, dimensions, metadata and five fixed
artifact basenames before a preview is drawn.

Native testing exposed two real integration details:

1. Desktop does not accept `file:` links in a `Link` element. The adapter uses
   explicit user-pressed Open buttons for HTML/SVG/PNG, plus Copy-path buttons.
   Openers use fixed argument vectors: `explorer.exe`, macOS `open`, or Linux
   `xdg-open`. There is no shell. Source Python is only copied, never opened
   through a potentially executable OS file association.
2. The actual clipboard signature is `ui.copy({text})`. Its failure is caught
   and the artifact directory remains visible as a fallback.

The SVG/PNG in the pane is a preview. Full XY hover, zoom and browser controls
remain in the exported HTML. Python callbacks need a live Python host.

## Reproducible local checks

No `claude` executable was initially on PATH. The official npm distribution was
installed under ignored project artifacts. The current registry version,
2.1.310, was rejected by the environment's release-age policy; that policy was
honored and 2.1.302 was used instead. No global installation, user configuration,
account sign-in or model request was needed.

From the repository root in PowerShell:

```powershell
$env:CLAUDE_CONFIG_DIR = 'C:/Users/villa/dev/skills/projects/reflex-xy-plugins/artifacts/claude-config'
$claudeExecutable = 'projects/reflex-xy-plugins/artifacts/claude-cli/node_modules/@anthropic-ai/claude-code-win32-x64/claude.exe'
& $claudeExecutable plugin validate projects/reflex-xy-plugins/claude --strict
& $claudeExecutable plugin test projects/reflex-xy-plugins/claude
node projects/reflex-xy-plugins/artifacts/claude-cli/node_modules/tsx/dist/cli.mjs projects/reflex-xy-plugins/claude/tests/portable.ts
```

The native scanner passes. All **six native tests** pass, covering session
activation, preset discovery, tool registration, command-to-stdin construction,
surface element rules, actual clipboard button dispatch, tool errors, bounded
references and path rejection. The portable harness passes **69 assertions**
for protocol, state isolation, size limits, file basenames, JSON literal
preservation, opener argument separation and retained artifacts after errors.
These portable checks are not described as native host acceptance.

To exercise the real packaged Python engine through the adapter, build the
distribution and pass its directory:

```powershell
$env:UV_CACHE_DIR = 'C:/Users/villa/dev/skills/projects/reflex-xy-plugins/artifacts/uv-cache'
node projects/reflex-xy-plugins/artifacts/claude-cli/node_modules/tsx/dist/cli.mjs projects/reflex-xy-plugins/claude/tests/portable.ts --plugin-root <built-plugin-directory> --integration
```

The independent release report records that command's final result and the
extracted ZIP identity. No real OS opener, installed Desktop/VS Code painter,
regular claude.ai chat or cloud pane has been claimed as accepted by these tests.

The `dev-01/reflex-xy-claude-code` distribution passes strict native validation
and all six native tests. Its Mod entry hash matches the source:
`3ee53ab3dbee596d6ab2ae61ab578adce819e14f88613c2de7fe636b8c0fcfe7`.
The real renderer integration passes **104 portable assertions**, including
both palettes, all five artifact paths and an actual SVG preview. Both generated
PNGs were inspected for correct red/blue palette choices, readable labels and
clipping. This is a scoped development-package result; the independent release
report owns the final archive identity and any later engine changes.

## Ordinary Claude Desktop chat

The additional `claude-desktop/manifest.json` targets ordinary Claude Desktop
chat through a local MCP Apps server, independently of the Code Mod.
[Claude's MCP Apps developer guide](https://claude.com/docs/connectors/building/mcp-apps/getting-started)
explicitly demonstrates local stdio MCP Apps in Desktop. The
[interactive connector help page](https://support.claude.com/en/articles/13454812-use-interactive-connectors-in-claude)
documents their inline and fullscreen conversation UI. The same MCP Apps server
can support ChatGPT and Claude; no custom Mod elements are needed on this path.

[Claude's local extension help](https://support.claude.com/en/articles/10949351-getting-started-with-local-mcp-servers-on-claude-desktop)
documents installation of custom `.mcpb` files through Settings, Desktop app,
Extensions, Advanced settings, Install Extension. An actual app/account
installation remains a separate acceptance step.

The extension uses stable MCPB manifest **0.3**, `server.type: node`, with its
entire MCP server dependency graph bundled into
`chatgpt/dist/server-bundled.js`. The Node runtime must be at least 22; `uv`
is an explicit user-configured prerequisite for Python rendering. The
[`@anthropic-ai/mcpb` 2.1.2 schema and CLI](https://github.com/modelcontextprotocol/mcpb)
validate the authored manifest. Its 0.4 UV schema exists but is labeled
experimental, so this extension does not depend on host-managed UV support.
The official guide gives no numeric Desktop version floor for MCP Apps; the
manifest therefore does not invent one. Use a current Desktop release and
enable the extension for the conversation.

The manifest sets loopback binding and an ephemeral port, passes trusted runtime
and skill paths, and prompts for a writable artifact directory. It deliberately
omits `ui.domain`: the
[official troubleshooting guide](https://claude.com/docs/connectors/building/mcp-apps/troubleshooting#ui-domain-validation-fails)
states that local stdio connectors have no URL to hash and must not set this
field. Remote Claude connectors need their own prescribed hash domain rather
than the ChatGPT widget domain.

Validate and pack the fully populated distribution with the official CLI:

```powershell
$mcpbCli = 'projects/reflex-xy-plugins/artifacts/claude-cli/node_modules/@anthropic-ai/mcpb/dist/cli/cli.js'
node $mcpbCli validate projects/reflex-xy-plugins/claude-desktop/manifest.json
node $mcpbCli pack <built-desktop-directory> <output-file.mcpb>
```

The manifest schema check passes. The independent release report records the
final archive validation and standalone stdio handshake. Successful protocol
and reference-host browser tests do not prove installation in a signed-in
Claude Desktop conversation.
