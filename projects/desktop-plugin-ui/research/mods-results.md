# Claude Code Mods UI: native contract probes

Checked on 2026-10-24 with the official Windows executable reporting **Claude Code 2.1.302**. The final fixture passes strict plugin validation and **34/34 native tests**. This probes the Claude Code Mod engine and its simulated surfaces; it does not prove the installed Claude Desktop painter, clipboard, browser opening, installation, account access, or cloud delivery.

The target is Claude Code, including the **Code tab** of Claude Desktop. Ordinary Claude Desktop chat extensions/MCP servers are a different integration. Do not advertise a Mod pane as an ordinary Desktop chat artifact or MCP App.

## Reproduction and retained evidence

The executable was read from the prior project without modifying it:

```powershell
$env:CLAUDE_CONFIG_DIR = Join-Path (Get-Location) 'projects/desktop-plugin-ui/artifacts/mods-config'
$probeExecutable = 'projects/reflex-xy-plugins/artifacts/claude-cli/node_modules/@anthropic-ai/claude-code-win32-x64/claude.exe'
& $probeExecutable --version
& $probeExecutable plugin validate projects/desktop-plugin-ui/mods-probe --strict
& $probeExecutable plugin test projects/desktop-plugin-ui/mods-probe
```

All new files are inside `projects/desktop-plugin-ui/`. No account session, model call, real process execution from the plugin, OS opener, or clipboard mutation was performed. The native API boundaries for processes, clipboard, pane placement, notifications, and logs use floor stubs. Actual native tree validation, hook dispatch, Client module execution, and simulated input/frame-clock events use the executable's test engine.

- `mods-probe/`: minimal plugin manifest, hooks configuration, hooks module, Client module, and native tests.
- `artifacts/mods-environment.json`: exact version, executable SHA-256, and scope flags.
- `artifacts/mods-validate-04.txt`: passing strict scanner including detected Client module.
- `artifacts/mods-test-final.txt`: 34 passing tests and structured exact rejection diagnostics.
- `artifacts/mods-sources/`: downloaded official reference, interface, gallery, testing guide, and public declarations.

Exploratory failures remain available. `mods-test-01.txt` was 16/25: the probe mistakenly attached `children: []` to leaf elements, expected unsupported URL schemes to reject the entire tree, and treated constructor names as a capability test. `mods-validate-01.txt` failed strict validation because the probe lacked author attribution. `mods-test-02.txt` was 26/27 because an internal loader `require` function exists despite the lack of Node process/DOM globals. The corrected node-module denial probe passes in `mods-test-03.txt` (28/28). Adding six Client checks passes in `mods-test-04.txt` and the final diagnostic run (34/34). These are retained exploratory revisions, not independent authoring evaluations.

## Per-probe outcomes

“Pass” means an observed native contract result. “Negative confirmed” means an intended invalid operation was rejected or downgraded. “Conditional” means the plugin's event/argument behavior passed against a stub and its external effect is untested.

| # | Probe | Outcome | Observed result or established rule |
| --- | --- | --- | --- |
| 1 | Shared layout and controls | Pass | `Box`, `Text`, `Button`, `Input`, `Select`, `Link`, `Code`, and `Markdown` form valid trees on desktop, terminal, and vscode. |
| 2 | Button and invalidation | Pass | A press increments the counter and redraws the tree without a model call. |
| 3 | Input change | Pass | A change updates draft text while leaving submitted text empty. |
| 4 | Input submit | Pass | Submit dispatches the supplied string to the submission callback. |
| 5 | Select dispatch | Pass | Selecting `large` updates the displayed choice. |
| 6 | SVG preview | Pass | A valid `Svg` tree with `isInteractive: true` is accepted on desktop and vscode. Actual hover/SMIL paint is untested. |
| 7 | SVG in terminal | Negative confirmed | A raw `Svg` rejects with a surface error. |
| 8 | RGBA Image in terminal | Pass | One valid base64 RGBA pixel with declared dimensions is accepted. |
| 9 | Image in desktop | Negative confirmed | A raw `Image` rejects with a surface error. |
| 10 | `file:` Link | Negative confirmed | The desktop tree survives, but the element becomes non-clickable `Text`; no `Link` remains. |
| 11 | `javascript:` Link | Negative confirmed | The desktop engine downgrades the element to `Text`. |
| 12 | Remote plain `http:` Link | Negative confirmed | The desktop engine downgrades the element to `Text`. |
| 13 | Allowed links | Pass | Canonical HTTPS and `http://localhost:3000/` remain `Link` elements. No URL is opened. |
| 14 | Oversized href | Negative confirmed | An href longer than 2,048 characters refuses the drawing. |
| 15 | Oversized SVG | Negative confirmed | SVG source longer than 131,072 characters refuses the drawing. |
| 16 | Invalid PNG | Negative confirmed | Base64 that lacks a PNG header is refused. |
| 17 | Fractional Image generation | Negative confirmed | A fractional `source.generation` is refused. |
| 18 | Arbitrary iframe tag | Negative confirmed | `iframe` is not a native element and the drawing is refused. |
| 19 | `autoFocus: false` | Negative confirmed | The constructor rejects this value, the hook is skipped, and the test observes the host's fallback renderer. Omit the prop to disable autofocus. |
| 20 | Duplicate Select values | Negative confirmed | Duplicate option values refuse the drawing. |
| 21 | Clipboard button | Conditional | Press sends exactly `C:/work/result.html` through `ui.copy({ text })`; OS clipboard remains untested. |
| 22 | Process boundary | Conditional | The native event preserves separate argv elements, literal `$()`/semicolon text, and stdin JSON. The stub launches nothing. |
| 23 | Toast, status, and log | Conditional | The button dispatches three distinct events and expected strings. Their actual presentation is untested. |
| 24 | Unplaced pane fallback | Conditional | When stubbed `ui.open` reports `isPlaced: false`, the command returns a transcript fallback. Actual placement remains untested. |
| 25 | Constructor table detection | Pass | Desktop's resolver exposes compatibility names for `Image`/`Raster`; names and truthiness alone do not establish surface support. |
| 26 | Leaf children | Negative confirmed | Even `children: []` on a raw `Svg` is refused. Use the official constructor and valid leaf props. |
| 27 | Global environment | Pass | `document`, `window`, and `process` are undefined. The loader's `require` is a function on this build. |
| 28 | Node filesystem import | Negative confirmed | That loader cannot load `node:fs`; its existence does not grant Node APIs. |
| 29 | Client native subtree | Pass | The Client module executes and draws its own `Box`, `Text`, and `Button` subtree on desktop and terminal. |
| 30 | Client key | Pass | Simulated `right` reaches the Client listener and updates local state. |
| 31 | Client pointer | Pass | A simulated down event preserves region-relative cell coordinates `3,2`. |
| 32 | Client frame timer | Pass | Advancing its frame clock 2,500 ms runs a 1,000-ms interval twice. |
| 33 | Client post and props | Pass | Posting reaches `ui.message`; validated string props return to the Client. A number produces the explicit fallback. |
| 34 | Client resize | Pass | A simulated resize updates the region measurement to 42 columns × 8 rows. |

The raw trees in negative tests are intentional. Production plugins should use constructors from `$.ui.resolve(e)` and explicitly branch on supported surfaces. Otherwise compatibility constructors can produce fragments and obscure missing capability.

## Available UI methods and boundaries

These are Mod methods, not HTML DOM components:

- Native layout and content: `Box`, `Text`, `Markdown`, and `Code`.
- Native interaction: keyed `Button`, `Input`, and `Select`, with callbacks returning through the engine.
- Navigation: constrained `Link` elements. A local artifact path needs an explicit action strategy such as a user-pressed process-backed opener and a copy-path fallback, separately tested on the target OS.
- Vector preview: `Svg` on desktop/vscode. Interactive mode is intended for scriptless SVG behavior; it does not turn SVG into a general JavaScript application.
- Terminal graphics: `Image` and `Raster`. The fixture verifies `Image`; `Raster` is documented and remains untested here.
- Custom local interaction: `Client` on desktop/terminal, using a second module, native elements, local state, input listeners, a frame clock, and plain-data posts to the hooks module. It is not a DOM/webview escape hatch.
- Placement: a `Pane` is a named region requested through `ui.open`. Render hooks can also target supported existing sites. Their availability varies by surface; native mounting a site is not evidence that every deployed host actually requests it.
- Lightweight feedback: `ui.toast`, `ui.status`, `ui.log`, and notifications have distinct destinations. The fixture only verifies the first three event boundaries.

The documented surfaces also include mobile with a narrower control protocol. No mobile painter or mobile protocol behavior was validated. VS Code's deployed rendering has extension-version requirements and ignores some styling/hotkey props; a passing native tree does not verify those pixels or shortcuts.

## Rules to promote into the skill

1. Name the exact host area before selecting an integration: Claude Code Desktop Code tab and ordinary Desktop chat have different contracts.
2. Record executable/host versions and prefer declarations produced by the installed build over older public snapshots.
3. Use native tree constructors and explicit surface branches; constructor truthiness is not feature detection.
4. Use keys for addressable controls and the correct action event: press, input change, input submit, or select.
5. Keep a draft separate from submitted data when typing should not commit an action.
6. Omit autofocus when it is off; only supply `true` when the interaction warrants focus.
7. Give Select options unique values and keep selection within the declared input contract.
8. Treat SVG as a vector preview with scriptless optional interaction; provide an alternate route when full application behavior is required.
9. Match graphics to the surface and reject over-limit payloads before a render hook returns them.
10. Preserve valid link schemes and canonical URLs. Do not promise clickable local file links; verify whether a build downgrades or rejects invalid schemes.
11. Prefer a user-pressed explicit opener and copy-path fallback for local artifacts; preserve argv boundaries and handle failure visibly.
12. Use `Client` for native local state, pointer/key input, and animation. Validate every data post in `ui.message` before performing privileged work.
13. Handle unavailable or unplaced panes with a usable transcript/band/text route and avoid assuming successful placement.
14. Keep process/filesystem/network work behind the mods API, separate from hooks and Client drawing globals.
15. Distinguish static validation, native contract tests, simulated actions, real painter checks, and account installation in every evidence claim.

## Primary sources

- [Mods overview](https://code.claude.com/docs/en/plugins/mods/overview): product and installation boundary.
- [Mods reference](https://code.claude.com/docs/en/plugins/mods/reference): files, render sites, surface element matrix, and limits.
- [Draw in the interface](https://code.claude.com/docs/en/plugins/mods/interface): native trees, panes, Client regions, lifecycle, and graphics.
- [Use the mods API](https://code.claude.com/docs/en/plugins/mods/api): commands, tools, processes, feedback, and state.
- [Test a mod](https://code.claude.com/docs/en/plugins/mods/test): account-free native tests and their painter limitation.
- [Public TypeScript declarations](https://github.com/anthropics/claude-code/blob/main/mods/types/claude-code.d.ts): the downloaded snapshot identifies 2.1.277, older than the tested 2.1.302 executable. The native experiments take precedence for the observed behavior.
