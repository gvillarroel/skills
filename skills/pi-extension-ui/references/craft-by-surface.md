# Craft for Pi TUI, RPC and print

Select the actual Pi mode before presentation. Prefer native `ctx.ui.select`
for a simple choice; a custom TUI is justified when comparative tree structure
helps the same decision. RPC dialogs and print output have their own contracts.

## TUI implementation

1. Guard terminal components with `ctx.mode === "tui"`. Use the bundled
   `micro-choice.ts` as the formatted, self-contained starting point.
2. Use `theme.fg` semantic roles: `accent` for active choice, `warning` when
   uncertainty needs attention, `success` for an acknowledged selected answer,
   `error` for a failed action and `muted`/`dim` for context. Keep deferral
   neutral. Pair roles with words, circles/checks and weight. Preserve the
   user's theme; do not paste browser colors or RGB escape sequences into it.
3. Measure terminal columns with host width utilities such as `truncateToWidth`,
   which account for ANSI and wide characters. Reserve actual host rows and
   keep both alternatives and decision keys reachable in a short terminal.
   Browser `rem`, CSS grids and pixel contrast scans do not style terminal cells.
4. Use bounded whitespace and aligned tree connectors. The evidence disclosure
   returns to the same pending question. Escape there closes evidence; Escape
   at the choice returns deferral, never a default parent.
5. Resolve `ctx.ui.custom` with `done(optionId)` or an explicit no-choice result.
   A native demonstration can put typed details into model-visible history
   with `triggerTurn:false`; do not call that a resumed model turn.

## Other modes

When `ctx.hasUI` is true in RPC, use native selection requests and matching
response IDs. A custom terminal factory does not paint in an RPC client.
For JSON/print accept explicit option IDs and return useful text/structured
results; do not request an invisible dialog. Preserve invalid-input recovery.

## Verify

Use the bundled RPC checker for actual discovery/request/response contracts and
inspect returned choice or deferral independently. Capture the real TUI at
80x32 and 60x16 cells, including evidence, selection, completed result and
neutral deferral. Inspect actual theme roles and ANSI-aware geometry; a version
probe, JSON transcript or HTML terminal mock alone does not prove native paint.
