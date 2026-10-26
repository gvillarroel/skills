# Native Claude Code Mod patterns

Contents: [Panes](#claude-ui-native-pane), [input](#claude-ui-native-input),
[preview](#claude-ui-native-preview), [actions](#claude-ui-native-actions),
[lifecycle](#claude-ui-native-lifecycle), [Client](#claude-ui-native-client).

Apply these patterns to Claude Code, including the **Code tab** in Claude Desktop. Ordinary Desktop chat MCP extensions use another host contract. A Mod's render tree consists of native elements; it is not an HTML document.

For a new executable plugin, first use the compact
[native authoring route](native-authoring.md) and its runtime template. It
includes authentic registration/execution contracts and native tests; keep
`command.register.name` distinct from `command.run.command` in hooks and tests.

Evidence: 2026-10-24, official Claude Code **2.1.302**, strict plugin validation and a **34/34 baseline** of native engine tests. The [expanded host-limits cohort](claude-host-limits.md) passes **57/57**, retaining all 34 baseline cases. Tests exercise engine trees, dispatch, and Client execution; installed paint, account installation, clipboard, process launching, and cloud delivery remain unverified.

Use [the reference](https://code.claude.com/docs/en/plugins/mods/reference), [interface guide](https://code.claude.com/docs/en/plugins/mods/interface), [API guide](https://code.claude.com/docs/en/plugins/mods/api), and [test kit](https://code.claude.com/docs/en/plugins/mods/test). Prefer the installed build's declarations over older public snapshots.

## claude-ui-native-pane

**Trigger/input:** A persistent panel or inspector. Supply a plugin manifest, a hooks module exporting `register(on, options)`, a stable pane ID, and a small view model.

**Rule:** List the module in `hooks/hooks.json`. Register a command during `session.start` and handle `command.run` by calling `$.ui.open({ id, title })`. Return `{}` for a command that only opens a view. In `ui.render` for `component: 'Pane'`, check `e.requestId` and pass other panes to `next(e)`. Obtain constructors from `$.ui.resolve(e)`. Size the compact `Box` tree to pane `bodyColumns` and scroll window, not viewport height. Request focus deliberately.

**Failure/fallback:** Handle an unplaced or unsupported pane with usable transcript text or another documented surface. A requested pane size/focus is not a guarantee. Explicitly branch on `e.surface`; a truthy constructor or its presence in `Object.keys($.ui.resolve(e))` does not prove support. Compatibility names are exposed even on surfaces that cannot draw them.

**Validate:** Run `claude plugin validate <plugin-dir> --strict` and `claude plugin test <plugin-dir>`. Mount with the correct `requestId`, explicit surface, and realistic props. Stub `ui.open` with `{ value: { isPlaced: false } }`. Check real narrow/wide placement and focus separately.

**Evidence:** Native tests passed the shared `Box`/content/control tree on desktop, terminal, and vscode, and the unplaced-pane fallback. Actual pane placement remains conditional. [Render sites and placement](https://code.claude.com/docs/en/plugins/mods/interface#pick-where-to-draw).

## claude-ui-native-input

**Trigger/input:** A form, search, or filter. Supply a field model, stable control keys, and unique option values.

**Rule:** Use keyed `Input`/`Select` constructors. Separate `onInput` drafts from `onSubmit` commits. Save drafts before invalidation to preserve typing. Keep Select values unique and reconcile the selection with them. Preserve keys across renders. Omit `autoFocus` when off; supply only `true` when needed. Label fields and explain invalid input visibly.

**Failure/fallback:** Duplicate option values refuse the drawing. `autoFocus: false` causes the constructor to reject and the hook to be skipped; omission is the supported off state. A surface accepting a native tree may ignore some focus props. For hosts without input/select protocol support, use supported buttons or ask for input in chat.

**Validate:** Run `ui.input({ key, text, kind: 'change' })`; assert only the draft changes. Separately test submit, `ui.select({ key, value })`, invalid values, and draft preservation. Verify real focus/editing.

**Evidence:** Native draft, submit, selection, and invalidation checks passed. Duplicate Select values were refused; invalid autofocus exposed the host fallback. [Controls and native drawing tests](https://code.claude.com/docs/en/plugins/mods/test#test-a-drawing).

## claude-ui-native-preview

**Trigger/input:** A chart, diagram, or screenshot. Supply bounded SVG or validated image data and descriptive alternative text.

**Rule:** Branch by surface: `Svg` on desktop/vscode; `Image` or documented `Raster` on terminal. Set meaningful `alt` and bounded dimensions. Cap SVG at 131,072 characters. Validate image encoding, dimensions, bytes, and whole-number generation counters. Use leaf constructors without children. Include a description and artifact route for essential graphics.

**Failure/fallback:** A raw terminal `Svg` or desktop `Image` refuses the tree. Invalid PNG bytes, fractional generation, and oversized SVG also refuse it. Even an empty `children: []` is invalid on a raw SVG leaf. `isInteractive: true` is a scriptless SVG mode intended for hover/CSS/SMIL; it is not a JavaScript application container. Use a separately supported application or exported artifact when the visual needs full scripting.

**Validate:** Mount valid previews and test unsupported surfaces, oversized/invalid input. Check real clipping, contrast, alternative text, hover, and animation separately.

**Evidence:** Native SVG trees passed on desktop/vscode; RGBA Image passed in terminal. All listed negative cases were observed. Raster remains documented rather than empirically verified in this cohort. [Surface elements and limits](https://code.claude.com/docs/en/plugins/mods/reference#elements).

## claude-ui-native-actions

**Trigger/input:** Navigation, copying, generation, or artifact opening. Supply a stable key, validated payload, and explicit destination/effect.

**Rule:** Use `Button.onPress` for actions and `Link` for supported canonical URLs. Pass argv arrays to `$.process.run(argv, options)` and structured data on stdin. Copy with `$.ui.copy({ text })`. Offer user-pressed OS-appropriate artifact opening plus copy-path fallback. Show failures and preserve the last useful result.

**Failure/fallback:** On tested 2.1.302 desktop trees, `file:`, `javascript:`, and remote plain `http:` Links become non-clickable Text; the rest of the drawing survives. This differs from an href exceeding 2,048 characters, which refuses the tree. Canonical HTTPS and `http://localhost` remain Links. Do not infer that a mounted link was opened or that a stubbed clipboard/process call succeeded at the OS boundary.

**Validate:** Press through the test handle. Stub process/clipboard APIs and assert argv, stdin, text, and errors; include literal shell metacharacters. Check real OS effects separately.

**Evidence:** Native copy and process event boundaries passed without launching or copying. URL downgrade, allowed URLs, and the href size rejection were observed. [Navigation](https://code.claude.com/docs/en/plugins/mods/interface#link-in-the-desktop-app) and [API methods](https://code.claude.com/docs/en/plugins/mods/api).

## claude-ui-native-lifecycle

**Trigger/input:** A view changes after work or an event. Supply session-scoped empty/loading/success/error states.

**Rule:** Scope state to the session and render from it. After changes, use `$.ui.invalidate('ui.render')` or documented `$.state` subscriptions. Avoid timers for unchanged content. Preserve useful output during updates and offer recoverable retries. Clean up owned tasks/listeners/state on lifecycle end. Choose feedback deliberately: transient toast, persistent status, or transcript/debug log.

**Failure/fallback:** Changing a module variable alone does not guarantee a new draw. Native invalidation is throttled/coalesced; do not treat each call as a distinct animation frame. A failed render hook can expose the host's fallback. Feedback APIs have different destinations; a passing stub asserts dispatch, not visibility. Headless/cloud execution must use an appropriate nonvisual result when no native painter is attached.

**Validate:** Test transitions, prior-result preservation, retry, session isolation, and separate toast/status/log events. Check real presentation/cleanup. This cohort did not test `$.state` persistence or background scheduling.

**Evidence:** Native button state plus invalidation changed the tree without a model turn. Distinct toast/status/log event dispatch passed against stubs. [Redraw and state](https://code.claude.com/docs/en/plugins/mods/interface) and [test stub boundaries](https://code.claude.com/docs/en/plugins/mods/test).

## claude-ui-native-client

**Trigger/input:** Custom key/pointer interaction or animation. Supply a supported surface, stable Client key, literal in-plugin module path, and plain-data props.

**Rule:** Return `Client({ key, module: './client.ts', props, width, height })`. Export a function `(props, surface)` returning `surface.elements` content. Use local state/setState, measured size, input listeners, and `surface.every`; initialize timers once. Send `surface.post(data)` to hooks and validate in `ui.message`. Returning `{ props }` updates props while keeping local state.

**Failure/fallback:** Client is a native drawing region, not arbitrary HTML, React DOM, or an iframe. Hooks lack `document`, `window`, and Node `process`; the tested loader's `require` function cannot load `node:fs`. Client has no mods API. Keep filesystem/process/network work in hooks behind that API. Use supported native content when Client is unavailable, and handle `ui.fault` for a Client that fails. Do not create a render loop with repeated `setState` calls during every render.

**Validate:** Mount both supported surfaces. Find content with `{ in: key }`; exercise `ui.key`, `ui.pointer`, `ui.advance`, `ui.post`, and `ui.resize`, including malformed posts. Check real input/animation and unmount cleanup separately.

**Evidence:** Six native Client checks passed: subtree execution, local key state, pointer cell coordinates, controlled timer ticks, validated message/props exchange, and measured resize. Arbitrary iframe tags were refused. [Client regions](https://code.claude.com/docs/en/plugins/mods/interface) and [test handle methods](https://code.claude.com/docs/en/plugins/mods/test#test-a-drawing).
