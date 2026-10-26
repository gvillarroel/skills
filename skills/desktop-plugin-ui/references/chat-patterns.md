# Chat UI patterns

## Contents

[Fallback](#claude-ui-text-fallback), [card](#claude-ui-inline-card),
[carousel](#claude-ui-option-carousel), [fullscreen](#claude-ui-fullscreen-workspace),
[form](#claude-ui-validated-form), [chart](#claude-ui-chart-canvas),
[files](#claude-ui-file-review-export), [theme/layout](#claude-ui-responsive-theme),
[details](#claude-ui-progressive-details), [state](#claude-ui-async-state).

Snapshot: 2026-10-24. These are MCP Apps inside Claude Chat. Native Code Mods
have different contracts. `documented` is not a signed-in Desktop test result.
Use the bridge reference for exact protocol mechanics.

The pattern evidence below preserves the initial fixture/documentation scope.
Later [actual Desktop Chat observations](claude-chat-live.md) establish local
installation, paint, direct tool actions, error preservation and fullscreen
for one build/account. They do not verify every pattern in this catalog.

The [Claude design guide](https://claude.com/docs/connectors/building/mcp-apps/design-guidelines)
defines conversation-oriented card, carousel, and fullscreen presentations.
The numerical limits below are documented design guidance, not claims of API
schema rejection. The remaining validation and recovery choices are engineering
recommendations derived from the protocol and the scoped probes.

## claude-ui-text-fallback

- **Trigger/input:** A result must remain useful with UI disabled; provide a
  concise summary, stable record IDs, and structured values with units.
- **Rule:** Return meaningful MCP `content` with `structuredContent`; attach UI
  only where presentation helps. Text, images, audio, resource links, and
  embedded resources are core MCP result types, not arbitrary executable UI.
- **Failure/fallback:** Raw HTML returned as text does not by itself register an
  MCP App. Preserve the actual business result when no View is rendered.
- **Validate:** Call the tool with an ordinary MCP client and inspect its text
  and data; separately verify UI resource registration. The scoped SDK probe
  passed a headless result containing count 7 and corresponding text.
- **Evidence:** Documented and observed-working in the MCP SDK fixture;
  actual host rendering remains untested. [MCP Apps overview](https://modelcontextprotocol.io/extensions/apps/overview).

## claude-ui-inline-card

- **Trigger/input:** A short status or decision with a few facts and actions.
- **Rule:** Use one self-contained card. Claude recommends up to two bottom
  actions and roughly four or five facts. Make the primary action explicit.
- **Failure/fallback:** Avoid nested vertical scrolling, deep navigation, and
  popovers that extend outside the frame; move extended work to fullscreen.
- **Validate:** Test content height, longest labels, keyboard access, and a
  narrow container; confirm the result remains understandable in text.
- **Evidence:** Documented presentation; no Desktop painter acceptance.

## claude-ui-option-carousel

- **Trigger/input:** Comparable product, venue, or media options; each has a
  stable ID, image, title, brief metadata, and optional action.
- **Rule:** Claude recommends three to eight consistent cards, short metadata,
  and at most one optional action per card. Keep selection tied to the ID.
- **Failure/fallback:** Do not treat each card as a separate host display mode.
  Provide list text when images or the carousel fail; do not force vertical
  scrolling inside an inline app.
- **Validate:** Verify horizontal keyboard/touch navigation, consistent sizing,
  the visible next-card cue, and selection after filtering.
- **Evidence:** Documented design pattern; execution untested in Desktop.

## claude-ui-fullscreen-workspace

- **Trigger/input:** A dense dashboard, document editor, map, or analysis canvas.
- **Rule:** Declare supported display modes, request fullscreen through the
  bridge, and use the returned mode. Keep controls clear of host safe areas;
  the conversation composer remains part of the experience.
- **Failure/fallback:** Keep a useful inline summary if the transition is
  denied. Prefer tabs, pagination, or collapsible sections to floating panels.
- **Validate:** Exercise inline to fullscreen and back, denied mode, preserved
  selection/draft, safe areas, and actual target-host transition.
- **Evidence:** Documented in Claude; request/response passed a synthetic host
  only. [Interactive connectors](https://support.claude.com/en/articles/13454812-use-interactive-connectors-in-claude).

## claude-ui-validated-form

- **Trigger/input:** Typed editable fields, defaults, constraints, and a target
  server tool; for consequential edits include record ID and version.
- **Rule:** Use labeled HTML controls inside an MCP App. Validate locally for
  feedback and again in the server tool; render the authoritative response.
  Separate draft edits from committed state. Use a focused form or fullscreen
  for larger tasks.
- **Failure/fallback:** A disabled button is not server validation. Preserve
  drafts after a rejected request; never replace supplied data with samples.
- **Validate:** Empty/invalid values, stale versions, double-submit behavior,
  keyboard labels/focus, server rejection, and successful response rendering.
- **Evidence:** Forms are documented MCP Apps use cases. The SDK probe rejected
  a negative integer; production edit persistence was not exercised.
  [MCP Apps overview](https://modelcontextprotocol.io/extensions/apps/overview).

## claude-ui-chart-canvas

- **Trigger/input:** Structured rows/series with IDs, units, categories, or
  geometry, plus a question the visual answers.
- **Rule:** Build HTML/SVG/Canvas/WebGL inside the View, using any suitable
  framework or vanilla JavaScript. Apply deterministic local filters and
  bridge calls for server recomputation; offer fullscreen for dense work.
- **Failure/fallback:** A native Mod `Svg` preview does not provide an arbitrary
  DOM, browser hover handlers, or a live Python callback. Offer static media or
  an external viewer when interactive rendering is unavailable.
- **Validate:** Check actual painted pixels, selected values, empty data,
  resizing, tool errors, and declared asset origins. A nonempty canvas alone
  does not prove a chart is correct.
- **Evidence:** Claude documents chart, globe, shader, and music examples;
  this bundle's probe tests bridge/UI behavior, not every renderer.
  [Claude MCP Apps examples](https://claude.com/docs/connectors/building/mcp-apps/getting-started).

## claude-ui-file-review-export

- **Trigger/input:** A previewable file and a downloadable resource with a
  meaningful name, MIME type, and authorized URI or embedded contents.
- **Rule:** Render a supported preview within the View; request downloads with
  the SDK's host-mediated `downloadFile` only when offered. Provide a supported
  host `openLink` route or a copyable authorized link when export is absent.
- **Failure/fallback:** A clicked anchor, generated server file, or fixture
  acknowledgement is not proof the OS saved a file. Do not assume iframe
  download, file-input path assignment, filesystem access, or PDF embedding.
  Validate file type/size on the server after explicit selection/upload.
- **Validate:** Capability absent, permission rejected, expired link, downloaded
  bytes/name, preview failure, and server-side authorization. The browser probe
  observed `InvalidStateError` for programmatic file-path assignment.
- **Evidence:** Conditional host feature. Fixture bridge acceptance only.
  [App download API](https://apps.extensions.modelcontextprotocol.io/api/classes/app.App.html#downloadFile).

## claude-ui-responsive-theme

- **Trigger/input:** Host theme, container dimensions, safe-area insets, and
  content that must reflow across inline/fullscreen containers.
- **Rule:** Read host context and updates; apply host style variables, responsive
  layout, accessible contrast, and safe-area padding. Start testing around
  320 CSS px; Claude recommends 44pt minimum touch targets.
- **Failure/fallback:** Fixed widths, root `min-height:100vh`, and nested scroll
  areas can clip content or cause growth loops. Mobile has a different host
  renderer; desktop browser sizing is not a mobile-device acceptance test.
- **Validate:** Narrow/wide, light/dark, long strings, focus visibility,
  horizontal overflow, safe areas, and actual content height.
- **Evidence:** Documented; fixture theme update and 360px/44px checks passed.
  Pixel/point equivalence and real mobile behavior were not measured.

## claude-ui-progressive-details

- **Trigger/input:** A useful primary result with optional advanced details.
- **Rule:** Show the result and essential action first; disclose secondary
  controls in-flow with a visible toggle. Keep errors visible and retain
  keyboard focus. Avoid overflow menus for essential actions.
- **Failure/fallback:** Do not initialize a dimension-sensitive viewer inside
  `display:none`; mount it when shown or notify/resize it. Do not hide the
  only recovery action. This is component-specific, not an HTML prohibition.
- **Validate:** Enter/Space activation, expansion, Escape where implemented,
  focus retention, first visible paint, and repeated reopen without reset.
- **Evidence:** Keyboard disclosure passed the browser fixture. Hidden-viewer
  sizing is an engineering pitfall requiring component-specific verification.

## claude-ui-async-state

- **Trigger/input:** A refresh or edit that may be pending, cancelled, rejected,
  or complete; a stable last-successful snapshot and current draft.
- **Rule:** Keep business state on the server, presentation state in the View,
  and durable preferences in storage you control. Mark busy/stale status;
  apply only the latest relevant response and preserve compatible selection.
- **Failure/fallback:** Do not erase the last successful view after failure or
  use iframe storage as an authoritative cross-session database. Context sent
  to the model is not durable UI storage.
- **Validate:** Pending state, out-of-order replies, controlled error, retry,
  two simultaneous instances, and teardown. The probe kept value 8 after a
  controlled rejected refresh; races and durable storage remain untested.
- **Evidence:** Scoped observed-working recovery plus engineering rules.
  [MCP Apps lifecycle and methods](https://apps.extensions.modelcontextprotocol.io/api/classes/app.App.html).
