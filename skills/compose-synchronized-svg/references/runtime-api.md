# Runtime API and Synchronization

## Contents

- [Synchronize five independent modes](#synchronize-five-independent-modes)
- [Expose a deterministic runtime](#expose-a-deterministic-runtime)
- [Produce stable snapshots](#produce-stable-snapshots)
- [Preserve static and reduced-motion meaning](#preserve-static-and-reduced-motion-meaning)
- [Small salary example](#small-salary-example)

Read this when the task requires direct API integration, custom interaction checks, or runtime maintenance. The normal composer already implements this API; normal generation uses the bundled auditor without loading implementation contracts. For compiled selectors and bindings, read [compiled-plan-and-bindings.md](compiled-plan-and-bindings.md).

## Synchronize five independent modes

- **Semantic synchronization:** update one source concept, recompute its transitive dependents, and rerender every binding that reads any changed value. Do this even when the modules are not connected visually.
- **State synchronization:** apply a named scenario as one transaction. Never reveal an intermediate mixture of old and new values.
- **Focus synchronization:** emphasize all modules in one focus group without changing their data. Keep nonparticipants legible and expose focus through more than color alone.
- **Time synchronization:** when a timeline exists, derive every timed mark from one composition clock. Treat each phase `values` object as an atomic patch over `timeline.baseScenario` when declared, otherwise over the composition's initial scenario. This lets a rich script-free fallback remain distinct from the clean state where a loop begins. Never accumulate over whichever phase happened to run before it. Make `seek(ms)` authoritative and independent of navigation history; do not run independent timers inside modules. A composition without a timeline must still support semantic, state, and focus synchronization.
- **Navigation synchronization:** when a world exists, derive the camera, semantic-zoom tier, active anchor, HUD, minimap, and camera-aware tab order from one camera snapshot. Keep it independent from semantic values, scenario, focus, and the optional timeline. Camera-only actions must not advance semantic revision or dispatch `svg-sync-change`.

Timeline interpolation defaults to `step`, which applies the active phase patch at the phase boundary. Set `timeline.interpolation` to `linear` or `smooth` only when phase values should act as end keyframes and continuous change teaches the story. Mark discrete source concepts such as counts, slots, pages, or selected items with `"interpolation": "step"`; they switch at the boundary even inside a smooth timeline. Set `timeline.autoplay` only when continuous playback adds meaning, always retain visible Play/Pause and the seek rail, and disable autoplay under reduced motion.

Never implement focus by lowering opacity on a module ancestor that also contains text. Dim only nonessential marks or borders and preserve at least 4.5:1 text contrast. Keep module containers as non-atomic `role="group"` regions so their bound values remain discoverable; put each focus action on a separate keyboard-reachable `role="button"` control whose accessible name explains the target and whose `aria-pressed` value follows the active focus state. Keep the playback control's visible label, `aria-label`, and `aria-pressed` synchronized with the runtime. Under reduced motion, expose an explicit disabled state and remove a no-op playback control from keyboard order.

## Expose a deterministic runtime

Publish one API after the embedded script initializes:

```js
window.svgSync = Object.freeze({
  version: "1.0",
  ready,                 // Promise<void>
  getPlan,               // () => deep-cloned plan
  getState,              // () => deep-cloned current state
  setState,              // (sourcePatch) => snapshot
  applyScenario,         // (scenarioId) => snapshot
  setFocus,              // (focusIdOrNull) => snapshot
  seek,                  // (timeMs) => snapshot
  play,                  // () => snapshot
  pause,                 // () => snapshot
  reset,                 // () => snapshot
  snapshot,              // () => stable snapshot object
  serializeSnapshot      // () => canonical JSON string
});
```

When `navigation` exists, add the camera methods `getCamera`, `setCamera`, `navigateTo`, `seekCamera`, `fitOverview`, `nextAnchor`, `previousAnchor`, `playCamera`, `pauseCamera`, and `resetCamera`. Keep camera snapshots separate from semantic snapshots. Require identical camera results for identical route times regardless of prior pan, zoom, or anchor history. Use `#view=<anchor-id>` for deterministic deep links.

Make every mutating call validate first, update atomically, render synchronously after `ready`, and return the resulting snapshot. Reject unknown IDs and invalid values without partially changing the SVG. Dispatch one `svg-sync-change` `CustomEvent` after a successful commit with the same snapshot in `detail`.

Make `seek(ms)` clamp to `[0, durationMs]`, or normalize modulo the duration only when `loop` is true. Tests must call `pause()` and `seek()` rather than depend on wall-clock playback. If `timeline` is `null`, keep `seek`, `play`, and `pause` as harmless deterministic no-ops that return the current snapshot.

## Produce stable snapshots

Return only semantic state, never transient DOM measurements:

```json
{
  "version": 1,
  "compositionId": "sync-svg-compensation",
  "revision": 4,
  "scenarioId": "baseline",
  "sourceValues": { "gross-annual": 90000 },
  "derivedValues": { "gross-monthly": 7500 },
  "focusId": null,
  "timeMs": 0,
  "phaseId": null,
  "phaseProgress": 0,
  "motion": "full"
}
```

Order concept and derived keys lexicographically in `serializeSnapshot()`. Round derived numbers at semantic boundaries, not pixel precision. From the same fresh state, the same calls must produce byte-identical snapshots and rendered attributes. Reapplying current state must not advance the revision. Capture the initial and named scenarios, every focus group, and each phase boundary. Verify that affected bindings update and unrelated bindings remain unchanged.

## Preserve static and reduced-motion meaning

- Render the complete initial scenario as literal SVG geometry, text, titles, legends, and ARIA labels before any script runs. The file must remain understandable when JavaScript is disabled.
- Compare every literal fallback value string with the initialized runtime's initial-state string. JavaScript initialization may reveal controls, but it must not change grouping, rounding, sign, currency, percent, suffix, scientific fallback, or zero formatting.
- Hide interactive controls by default and reveal them only after adding a root `svg-sync-ready` class. Do not show controls that cannot work without script.
- Honor `prefers-reduced-motion: reduce`. Disable CSS/SMIL transitions and autoplay, freeze the optional clock at a stable phase, and apply semantic, scenario, and focus changes immediately.
- Never hide essential meaning behind hover, motion, focus, or color. Provide a readable static state and textual value for each essential encoding.

## Small salary example

This fragment shows one source value affecting two disconnected representations through a derived DAG:

```json
{
  "concepts": [
    {
      "id": "gross-annual",
      "label": "Annual gross salary",
      "type": "number",
      "unit": "USD/year",
      "default": 90000,
      "domain": [0, 200000]
    }
  ],
  "derived": [
    {
      "id": "gross-monthly",
      "label": "Monthly gross salary",
      "type": "number",
      "unit": "USD/month",
      "dependsOn": ["gross-annual"],
      "compute": {
        "op": "divide",
        "args": [{ "ref": "gross-annual" }, 12]
      }
    }
  ],
  "scenarios": [
    {
      "id": "baseline",
      "label": "Baseline",
      "values": { "gross-annual": 90000 }
    }
  ],
  "modules": [
    {
      "id": "annual-bar",
      "claim": "Annual pay relative to the selected range.",
      "assetType": "bar-chart",
      "bindings": [{ "value": "gross-annual", "selector": "[data-role='bar']", "channel": "width" }]
    },
    {
      "id": "monthly-table",
      "claim": "The corresponding monthly gross amount.",
      "assetType": "comparison-table",
      "bindings": [{ "value": "gross-monthly", "selector": "[data-role='value']", "channel": "text" }]
    }
  ],
  "timeline": null
}
```

Calling `window.svgSync.setState({ "gross-annual": 120000 })` must atomically change the annual bar and the monthly value to `10000`, while any module not bound to `gross-annual` or its descendants remains unchanged.
