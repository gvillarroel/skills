# Compose plugin UI across Codex, Pi and Claude

## Contents

- [Choose by task](#choose-by-the-users-task)
- [Host routes](#host-route-and-composition-boundary)
- [Combinations](#reusable-combinations)
- [Ownership](#keep-visual-and-state-ownership-aligned)

Snapshot: 2026-10-31. Separate documented mechanisms from the engineering
recommendations below. Use the installed version and the exact frontend;
availability is not a visual quality verdict. Read only the selected host's
implementation reference. Use [visual-review.md](visual-review.md) to compare
layouts when visual quality matters.

For delivery cost, cross-host reuse and OpenUI/framework choices, use
[efficient-delivery.md](efficient-delivery.md).

## Choose by the user's task

| Task | Useful composition | Poor fit and reason |
| --- | --- | --- |
| Pick one mode or record | Native choice + current value + explicit command/argument fallback | A dashboard, web server or nested dialogs add work to a bounded decision. |
| Review one result | Compact result + one clear next action + optional details | Several equal primary actions and raw logs obscure completion and the next decision. |
| Monitor ongoing work | Small truthful status + on-demand inspector + durable completion result | A tall permanent header, widget and footer reduce space for the conversation and editor. |
| Compare exact attributes | Labeled aligned rows/table + optional visual preview | A carousel hides neighboring values and makes exact comparisons depend on memory. |
| Browse visual alternatives | Small labeled cards/carousel + selection summary | Dense metric tables can hide the visual differences that drive this choice. |
| Edit spatial/large data | Compact summary leading to a supported larger view; preserve selection/draft on return | A full application squeezed into an inline card creates nested scrolling and hidden actions. |
| Explain a chart | Chart + selected value/units + accessible table or text equivalent | A chart plus a redundant table of every value can drown the question; disclose detail where appropriate. |

These are starting choices, not a universal preference for small UI. A large
comparison, map or editor can justify rich UI immediately. Required recovery,
permission meaning and important errors must remain discoverable.

## Host route and composition boundary

| Actual frontend | Available route to evaluate | Composition boundary |
| --- | --- | --- |
| Codex CLI | Tools/text/artifact links, negotiated elicitation | HTML bytes, image transport and callbacks do not establish terminal pixels or custom panels. |
| Codex desktop/IDE | Frontend-supported tool presentation and MCP App routes, where available | Test that specific host. Historical desktop chart paint exists; it does not establish every placement or IDE renderer. |
| Developer-owned Codex client | App-server events, approvals and elicitation + an authored frontend | Author the renderer in that client; app-server is not a stock-sidebar injection API. |
| Pi TUI | Commands, native dialogs, keyed status/widgets, custom renderers and bounded custom components | Add small surfaces first. Header/footer/editor factories replace existing UI; preserve needed host and other-extension functions deliberately. |
| Pi RPC | Dialog request/response bridge; client-dependent status/widgets | `hasUI` is true; custom terminal components still need `mode === "tui"`. JSON/print need explicit inputs and text/data fallback. |
| Claude Desktop ordinary Chat | MCP App inline HTML with supported larger display modes | Native Mods are another surface. Keep chat inline shallow; complex editing belongs in an appropriate larger view. |
| Claude Code / Desktop Code / VS Code | Native Mod controls, panes, shared prompt band and surface-specific previews | Compose shared render sites, use actual body dimensions and verify element/prop support on each frontend. |

Current [OpenAI UI guidance](https://developers.openai.com/plugins/build/chatgpt-ui)
uses the shared MCP Apps bridge first, capability detection for optional
extensions and useful tools without UI. The
[extension surfaces](https://developers.openai.com/plugins/build/extensions)
describe ChatGPT sidebar/composer/file integrations; do not transfer those
placements to Codex by name. The
[app-server contract](https://learn.chatgpt.com/docs/app-server#mcp-server-elicitation-requests)
requires response handling and capability opt-in for extended forms; the client
owns their rendering. Keep policy/decline/cancel separate from product limits.

## Reusable combinations

### plugin-ui-focus-disclose

- **Trigger/input:** A result has an identity, a few decision facts and optional
  long detail. Supply one authoritative record/version and a task action.
- **Rule:** Keep identity, outcome and action visible. Disclose explanation,
  logs or advanced settings separately. For Claude Chat, its
  [design guide](https://claude.com/docs/connectors/building/mcp-apps/design-guidelines)
  recommends about four or five facts and at most two bottom actions inline;
  these are design guidance, not protocol limits.
- **Failure/fallback:** Do not hide required errors or the only exit in Details.
  Use text and a supported expand route when richer presentation is absent.
- **Validate:** Inspect initial and expanded states at a narrow width; complete
  the task by keyboard and return to the same selected record.

### plugin-ui-status-inspector

- **Trigger/input:** Work continues while the user chats or edits. Supply job
  identity, actual state, attention reason and an on-demand inspection action.
- **Rule:** Give status, inspector and committed transcript outcome different
  jobs. In Pi use a stable `setStatus` key or compact `setWidget` before replacing
  the footer. Clear transient status/widgets when no longer relevant.
- **Failure/fallback:** A custom footer must preserve wanted model/context,
  branch and other-extension status explicitly. A persistent Claude pane should
  not hold other toasts. A collapsible band cannot be the sole required answer.
- **Validate:** Open a second synthetic plugin/status, resize to a short view,
  trigger an unrelated notification, close/reopen and check no information or
  editor access was lost. [Pi footer source](https://github.com/earendil-works/pi/blob/v1.4.0/packages/coding-agent/examples/extensions/custom-footer.ts).

### plugin-ui-choice-command

- **Trigger/input:** A deterministic bounded selection with stable option IDs,
  current value and optional explicit argument.
- **Rule:** Share one domain handler between command and native selector. Show
  the current value; separate cancel from empty input and validation failures.
  Let known selections run without inference.
- **Failure/fallback:** In noninteractive modes accept an argument or explain
  the exact command. Serialize decisions rather than stacking dialogs for a
  linear task; do not silently commit a cancelled choice.
- **Validate:** Exercise argument, selector, invalid value, cancellation and
  late reply after an intervening edit. Use the existing guarded-intent recipe
  for stateful Pi edits. [Pi mode contract](pi-extensions.md#account-for-the-frontend).

### plugin-ui-preview-controls

- **Trigger/input:** A chart/image/vector preview supports a decision. Supply
  source identity, selection and a textual equivalent.
- **Rule:** Put real labeled controls beside the preview; maintain a shared
  selected ID. Use SVG only on supported Claude native surfaces; terminal
  Image/Raster and Desktop SVG have different contracts.
- **Failure/fallback:** Pixels do not become buttons. A browser chart is not a
  native pane test. Preserve controls and an informative summary when the
  preview cannot render.
- **Validate:** Select by keyboard and verify preview, text and committed
  result agree. Test the unsupported-preview fallback on the named frontend.
  [Native elements](https://code.claude.com/docs/en/plugins/mods/reference#elements).

### plugin-ui-summary-workspace

- **Trigger/input:** A map, editor or comparison needs more room than inline.
  Supply record ID, draft/version, selection and supported display modes.
- **Rule:** Show a meaningful inline summary and explicit open action. Request
  the supported larger mode and retain selection/drafts when returning.
- **Failure/fallback:** Handle refusal or missing capability with a useful
  bounded view or artifact. Avoid duplicate chat composers, nested inline
  vertical scrolling and a multi-screen application hidden inside a card.
- **Validate:** Enter/exit/refuse the larger view, resize, cancel and reopen;
  assert the same record/draft. A local fullscreen prototype proves no host
  display-mode negotiation.

### plugin-ui-shared-surface

- **Trigger/input:** Multiple plugins share a prompt band, status area, keys,
  editor or notifications. Supply stable IDs and lifecycle ownership.
- **Rule:** Compose Claude `AbovePrompt` with `await next(e)` and preserve its
  returned content; returning only your tree can suppress other Mods. Use
  distinct hotkeys and short-lived focus capture. Pi custom components must
  finish via `done()`; hiding an overlay is not completion.
- **Failure/fallback:** Use a command-opened pane when persistent content can
  be collapsed. Reserve `holdToasts: true` for temporary decision dialogs.
  Release handlers/timers/focus on disposal and ignore late responses.
- **Validate:** Run two synthetic plugins together. Check each action, status,
  notification, Escape and focus restoration after closing one. Inspect the
  relevant [Claude render-site contract](https://code.claude.com/docs/en/plugins/mods/interface)
  and [Pi TUI contract](https://github.com/earendil-works/pi/blob/v1.4.0/packages/coding-agent/docs/tui.md).

## Keep visual and state ownership aligned

Share domain contracts across adapters, not one universal component tree.
Keep a single authoritative committed state; treat drafts, displayed state
and model-visible context as distinct. Correlate async results to the current
record/version and mounted view. Sorting, selection, filtering, pagination and
copying known values should not silently start model work. Label actions that
do need reasoning and measure inference separately from network requests.

Host chrome, approvals and elicitation own their paint and authority. An
authored confirmation must not impersonate a permission dialog. In authored
HTML use the selected exact palette with theme/contrast checks; Claude's
recommendation to use adaptive host structural tokens is a design tradeoff,
not proof that fixed palette paint matches the host. Record actual ownership
and preserve mandatory accessibility overrides.
