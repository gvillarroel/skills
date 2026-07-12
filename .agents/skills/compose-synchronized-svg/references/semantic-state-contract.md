# Semantic State Contract

Use this contract when several SVG modules encode the same idea or a value derived from it. Keep one canonical state store, compute dependencies once, and render every bound module from the resulting snapshot. Treat animation as an optional synchronization layer, not as the source of truth.

## Model canonical concepts

1. Assign every user-controlled fact a stable lowercase hyphen-case concept ID, unit, domain, and default value. Compact-brief v1 is numeric-only; the compiler emits `type: "number"` in the full plan.
   Set the domain to the complete credible decision envelope. It must contain every named scenario and expected manual patch, while remaining tight enough that normal values use the visual scale. A legal domain extreme must never push a bound mark outside its module.
2. Preserve canonical numeric truth in derived values. When a bar, gauge, or progress track has a visual ceiling, clamp only its binding transform; do not clamp the derived value or its textual readout. A 260% result may saturate a 150% track, but it must still read as 260%. Anchor percentage bullet/progress transforms at canonical zero: negative values render zero length, and every unsaturated nonnegative mark must cover the same fraction of its target distance as `value / target`.
3. Define every calculated value in `derived`. Declare its direct dependencies and a pure computation tree.
4. Validate the dependency graph as a directed acyclic graph (DAG). Reject missing references, cycles, conflicting units, non-finite results, and attempts to override derived values.
5. Recompute derived values in topological order after a source change. Commit the source patch and all derived results atomically, then render once.
6. Never read geometry or formatted DOM text back into state. The state snapshot, not any individual module, is authoritative.

Use safe computation nodes instead of executable strings. A node may be a finite literal, `{ "ref": "concept-id" }`, or `{ "op": "...", "args": [...] }`. Support only documented pure operations such as `add`, `subtract`, `multiply`, `divide`, `min`, `max`, `clamp`, and `round`; never pass plan content to `eval` or `Function`. `subtract` accepts two or more arguments and subtracts every trailing argument from the first; `divide` accepts exactly two arguments. `round` mirrors JavaScript `Math.round` with an optional decimal-place argument, so exact half ties resolve toward positive infinity in compiler, fallback, runtime, and auditor alike.

## Author the compact brief in normal use

Write the idea-specific contract, pass it through `preflight_synchronized_svg_brief.py`, and let `compile_synchronized_svg_plan.py` expand mechanics only after preflight reports `ok: true`. A compact brief keeps source records, derived computation trees, scenarios, modules, a global armature name, optional cross-module relationships, focus groups, and optional timeline phases. For each module, provide a `values` list instead of manual selectors or channels:

```json
{
  "compositionId": "system-capacity-atlas",
  "title": "System capacity atlas",
  "provenance": "Illustrative operating model · synthetic values",
  "initialScenario": "baseline",
  "armature": "flow-spine",
  "concepts": [
    {"id": "load", "label": "Incoming load", "unit": "req/s", "default": 1200, "domain": [0, 2400]}
  ],
  "derived": [
    {"id": "served-load", "label": "Served load", "unit": "req/s", "compute": {"ref": "load"}}
  ],
  "scenarios": [
    {"id": "baseline", "label": "Baseline", "values": {"load": 1200}}
  ],
  "modules": [
    {
      "id": "load-overview",
      "question": "How much load reaches the system?",
      "claim": "One canonical arrival rate drives every downstream view.",
      "assetType": "bar-chart",
      "values": ["load", "served-load"],
      "selectionRationale": "Aligned lengths make arrival and service magnitude directly comparable.",
      "rejectedAlternative": "A pie chart was rejected because these values are not parts of one fixed whole."
    }
  ],
  "relationships": [],
  "focusGroups": [
    {"id": "load-story", "label": "Load path", "moduleIds": ["load-overview"]}
  ],
  "timeline": null
}
```

Use 6–12 modules in a normal deliverable brief. Extend to 13–16 only for a true megacanvas where every extra module owns a distinct viewer question, recurring concepts propagate across materially different encodings, and the overview plus readable crops remain viable. The compiler assigns four rows above twelve modules to preserve usable module width. Use exactly `en-US`; the compiler rejects every other locale. The Python literal formatter and browser `Intl.NumberFormat` path must agree on grouping, half rounding, currency sign placement, percentages, suffixes, and normalized zero. Common currencies use the same symbol map in both paths; other valid three-letter currency codes use the code plus a nonbreaking space deterministically instead of a browser-specific symbol. Keep `values` unique within a module and order them by visual importance. For a stacked bar, list only mutually exclusive nonnegative parts and set `stackTotal` to the canonical total whose domain every segment must share; this makes segment lengths additive and the visible ceiling truthful. Detectable derived subtotals are moved to exact readouts instead of being stacked twice. For a flow module, put the conserved same-unit source total first and list only mutually exclusive branches after it. Flow conservation is algebraic: signed reverse or deficit branches are allowed when semantically justified, but the branch sum must equal the source in defaults and every scenario, and the browser audit rechecks conservation after legal state changes. Use a network or table when the values do not form a conserved partition. Each source starts with its own canonical color token. Direct references and pure constant multiplication, division, or rounding inherit the ancestor identity automatically; multi-input computations remain distinct. A derived record may set `colorSource` to any genuine canonical source or derived ancestor when deliberate inheritance is semantically useful and is not inferred; the compiler rejects unrelated color ancestry. Compact network modules use equal-area nodes, exact synchronized readouts, and only real edges from the declared dependency DAG, so mixed units never become an area comparison and a decorative hub cannot imply false topology. Include at least one source/derived dependency pair in a network module's `values`; otherwise choose a non-network asset. Use a radial gauge only for a fraction whose full legal envelope stays inside `[0, 1]` or an equivalent percentage-point value whose envelope stays inside `[0, 100]`; the composer renders both unit systems without multiplying percentage points twice. Represent a load or target ratio that can exceed 100% with a zero-anchored bullet or progress asset and its 100% marker. Name an unbounded demand/capacity result as a load ratio, not utilization. Declare no more than 18 `relationship` records, only between distinct modules, and choose `flow`, `dependency`, or `feedback`; the composer routes them without changing value semantics. A module may belong to at most four top-level focus groups so every story retains a distinct visible control. Focus groups that form contiguous rows or columns become subtle labeled composition regions, and timeline phases expose a visible label and progress rail. For `loop: true`, exact `durationMs` wraps to time zero; add a return-to-start final phase only when the approach to that seam should also be visually smooth. The compiler derives `dependsOn`, layout, reading order, selectors, channels, transforms, formats, identities, aliases, and exact phase boundaries. If it reports a safe divisor-domain normalization, preserve that report beside the plan. Fix compiler errors in the brief and regenerate; never patch compiler output.

Never create a derived rollup that adds a conserved flow total to one of its own branches; the compact compiler rejects the detectable additive form because it counts the same quantity twice. A signed `total - branches` reconciliation is valid. When visible text names a subtotal and its constituents, state the hierarchy explicitly instead of presenting the subtotal and an included part as peers. Show a static equality or unit conversion with a table or arithmetic bridge. Use a line/timeline module only for a genuine ordered progression with a meaningful axis, not for two values whose sole claim is that they are equal.

For a network claim, include the complete direct-dependency path between every selected ancestor/descendant pair; the compiler rejects a transitive pair with an omitted intermediate bridge. For a scenario-isolation promise, audit at module level as well as value level: a module described as unchanged must bind only values outside the changed dependency closure. When the task requests a forward chain, keep every required facet in one connected relationship spine. A feedback label must distinguish a current required response from a deployed response that persists after the triggering risk has fallen, and its DAG or ordered phase story must support that distinction.

For an exact ledger or table, define every value named `total`, `check`, `reconciliation`, `residual`, or `remainder` by an explicit equality before encoding it. A partition check may be `sum(parts)`, `whole - sum(parts)`, or a visible comparison between the two; never add a conserved whole to the same allocation or rollup parts it already contains. Verify the equality in every scenario.

## Understand compiled `composition-plan.json`

The following full contract is compiler output and an advanced extension surface. Do not author it directly during normal use.

Use this minimum top-level contract:

```json
{
  "version": 1,
  "compositionId": "sync-svg-compensation",
  "title": "Compensation explorer",
  "subtitle": "Earnings and planning from one canonical state",
  "provenance": "Illustrative model · synthetic USD values",
  "locale": "en-US",
  "viewBox": [0, 0, 1600, 1000],
  "initialScenario": "baseline",
  "syncModes": ["semantic", "state", "focus"],
  "identity": {},
  "identityAliases": [],
  "layout": {
    "armature": "asymmetric-megacanvas",
    "safeArea": [48, 128, 1504, 824],
    "gap": 24,
    "readingOrder": []
  },
  "concepts": [],
  "derived": [],
  "scenarios": [],
  "modules": [],
  "relationships": [],
  "focusGroups": [],
  "timeline": null
}
```

Apply these rules:

- `compositionId`: use one stable, globally unique lowercase hyphen-case ID. Put the same value on the root SVG as `data-composition-id`.
- `subtitle`: optionally provide one concise, project-specific line; the final composer uses it instead of generic status copy.
- `provenance`: provide one concise visible evidence note. State whether the values are sourced, assumed, simulated, or synthetic; never present illustrative precision as observed fact.
- `locale`: use exactly `en-US`. It is a validated deterministic contract, not a presentation preference; unsupported locales fail before SVG generation.
- `identity`: optionally map canonical identity IDs to `{ "colorToken": "canonical-value-id", "nonColor": ["role-cue"] }`. The token may name a source or derived value and must resolve to one stable CSS token in the standalone SVG.
- `identityAliases`: declare alongside `identity` as records shaped like `{ "identity": "tax", "values": ["tax-rate", "tax-annual"], "rationale": "..." }`. Cover every bound value exactly once, justify true source/derived variants, and never alias unrelated values to reuse a color.
- Embed the complete plan as JSON text in `<metadata id="sync-composition-plan">`; keep the authoring sidecar outside the shipped SVG when the user requests one file.
- `concepts`: define source records with `id`, `label`, `type`, `unit`, `default`, and an optional numeric `domain`.
- `derived`: define records with `id`, `label`, `type`, `unit`, `dependsOn`, and `compute`. Keep `dependsOn` equal to the direct `{ "ref": ... }` leaves in `compute`.
- `scenarios`: define named atomic source patches as `{ "id", "label", "values" }`. Include source IDs only.
- `modules`: define each visual claim and every state-to-mark binding. A module may be spatially disconnected only when no cross-module path is semantically necessary.
- `relationships`: optionally define `{ "id", "source", "target", "kind", "label" }` records. Source and target must be distinct declared modules; kind must be `flow`, `dependency`, or `feedback`. Relationships coordinate reading and focus but never create state dependencies.
- `focusGroups`: map one focus ID to the module IDs that should receive coordinated emphasis. This top-level array is the sole authoring authority for membership; do not duplicate `focusGroups` inside compact brief modules. The compiler derives each compiled module's `focusGroups` field from `moduleIds` and ignores legacy module-level copies.
- `timeline`: use `null` unless time explains the idea. When present, provide `durationMs`, `loop`, optional `baseScenario`, `interpolation` (`step`, `linear`, or `smooth`), `autoplay`, and non-overlapping ordered `phases` with `id`, optional `label`, `startMs`, `endMs`, optional `focusId`, and a source-only `values` patch.

Every source used directly as a division denominator needs an explicit legal domain that excludes zero. The compact-brief compiler may tighten such a domain away from exact zero when the default and all named scenarios are nonzero; it must report that normalization. Do not hide a genuinely meaningful zero-capacity or zero-baseline state behind this rule—model its finite consequence explicitly with `max`, `clamp`, or a separate state instead.

Treat semantic zero as exact numeric equality after normalizing negative zero. Decide flow direction from the raw canonical value, never from a transformed pixel magnitude. Reconciliation and root-search tolerances may account for floating-point operations, but they must never change a value's sign or reclassify a finite nonzero value as zero.

## Understand compiled bindings

The compiler expands each brief module into the explicit form below. Read this only when maintaining the contract or when the user explicitly requests custom fragments; normal generation should stay at the compact `values` list.

Define a module with this shape:

```json
{
  "id": "annual-pay-bar",
  "question": "How large is annual gross pay relative to the selected range?",
  "claim": "Annual gross pay sets the scale of compensation.",
  "assetType": "bar-chart",
  "selectionRationale": "Aligned length makes the magnitude precise and easy to compare.",
  "rejectedAlternative": "A gauge was rejected because it would weaken range comparison.",
  "region": [80, 160, 620, 300],
  "focusGroups": ["gross-pay"],
  "bindings": [
    {
      "value": "gross-annual",
      "selector": "[data-role='gross-bar']",
      "channel": "width",
      "transform": {
        "op": "linear",
        "domain": [0, 200000],
        "range": [0, 480],
        "clamp": true
      }
    },
    {
      "value": "gross-annual",
      "selector": "[data-role='gross-label']",
      "channel": "text",
      "format": {
        "style": "currency",
        "currency": "USD",
        "maximumFractionDigits": 0
      }
    }
  ]
}
```

Use stable IDs and attributes in the SVG:

- Root: `data-composition-id` and `data-plan-version`.
- Root: also expose `data-static-state`, `data-state-revision`, and `data-sync-ready`.
- Root and module groups: use `role="group"`, not an atomic `img` or `application` role, so labeled descendants remain visible to assistive technology. Give the root `aria-labelledby`; give each module `data-module-id`, `data-asset-type`, and an accessible `<title>` or `aria-labelledby`.
- Bound mark: `data-role`, `data-bind`, `data-channel`, and an explicit exposed descendant role such as `img` or `meter`. Keep each binding selector local to its module group. Also keep `data-accessible-label`, `data-value-unit`, `data-accessible-value`, and `aria-label` synchronized from the same canonical value in every render transaction. Any visible text that echoes a binding must update from that same formatted canonical value in the same transaction. Generated `data-flow-source-label` text must combine its stable base label with the current accessible value; `data-flow-value-label` text must exactly mirror the branch mark's current accessible value. Put the human label, formatted value, and unit in the accessible name; never expose an internal value ID. Use `aria-valuemin`, `aria-valuemax`, `aria-valuenow`, and `aria-valuetext` only for a genuine range role such as `meter`; do not put ignored range properties on `role="img"`. Do not accept DOM attributes alone: correlate each DOM node to its own Chromium accessibility node, including duplicate labels within one module, after every scenario, source perturbation, and legal zero-flow boundary.
- Focus target: `data-focus-group`; separate focus control: `data-module-focus-id`, `role="button"`, `tabindex="0"`, and synchronized `aria-pressed`.
- Root timeline state: `data-time-ms`, `data-phase-id`, and `data-phase-progress`.

Restrict `channel` to an explicit allowlist such as `text`, `x`, `y`, `width`, `height`, `r`, `path`, `transform`, `opacity`, `class`, or `aria-value`. Give each binding exactly one value source. Use multiple bindings when a value drives multiple channels. Preserve the same unit, direction, category color, and meaning wherever a concept recurs.

When `identity` is present, include at least one declared non-color cue in every bound role for that identity, such as `tax-step`, `tax-rate-label`, or `tax-needle`. Every bound appearance of one identity must resolve to its declared canonical value token. Distinct identities may reuse a color only when that reuse is deliberate and their visible non-color cues stay disjoint; identical color/cue signatures are a conflation error.

## Synchronize four independent modes

- **Semantic synchronization:** update one source concept, recompute its transitive dependents, and rerender every binding that reads any changed value. Do this even when the modules are not connected visually.
- **State synchronization:** apply a named scenario as one transaction. Never reveal an intermediate mixture of old and new values.
- **Focus synchronization:** emphasize all modules in one focus group without changing their data. Keep nonparticipants legible and expose focus through more than color alone.
- **Time synchronization:** when a timeline exists, derive every timed mark from one composition clock. Treat each phase `values` object as an atomic patch over `timeline.baseScenario` when declared, otherwise over the composition's initial scenario. This lets a rich script-free fallback remain distinct from the clean state where a loop begins. Never accumulate over whichever phase happened to run before it. Make `seek(ms)` authoritative and independent of navigation history; do not run independent timers inside modules. A composition without a timeline must still support semantic, state, and focus synchronization.

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
      "id": "monthly-card",
      "claim": "The corresponding monthly gross amount.",
      "assetType": "metric-card",
      "bindings": [{ "value": "gross-monthly", "selector": "[data-role='value']", "channel": "text" }]
    }
  ],
  "timeline": null
}
```

Calling `window.svgSync.setState({ "gross-annual": 120000 })` must atomically change the annual bar and the monthly value to `10000`, while any module not bound to `gross-annual` or its descendants remains unchanged.
