# Compiled Plan and Bindings

## Contents

- [Understand compiled `composition-plan.json`](#understand-compiled-composition-planjson)
- [Understand compiled bindings](#understand-compiled-bindings)

Read this only for explicit custom-fragment work or maintenance of the compiler contract. Normal generation uses the [compact brief](semantic-state-contract.md) and never reads or edits the compiled plan. Runtime methods are documented in [runtime-api.md](runtime-api.md).

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
  "timeline": null,
  "world": null,
  "navigation": null
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
- `modules[].diagram`: optionally define a connected qualitative tree or network with `layout`, `nodes`, and `links`. Use 2–18 nodes, 1–32 links, `tree`, `radial`, or `lanes`, and only the documented structural kinds. Every numeric value listed by the module must bind to exactly one diagram node.
- `relationships`: optionally define `{ "id", "source", "target", "kind", "label" }` records. Source and target must be distinct declared modules; kind must be `flow`, `dependency`, or `feedback`. Relationships coordinate reading and focus but never create state dependencies.
- `focusGroups`: map one focus ID to the module IDs that should receive coordinated emphasis. This top-level array is the sole authoring authority for membership; do not duplicate `focusGroups` inside compact brief modules. The compiler derives each compiled module's `focusGroups` field from `moduleIds` and ignores legacy module-level copies.
- `timeline`: use `null` unless time explains the idea. When present, provide `durationMs`, `loop`, optional `baseScenario`, `interpolation` (`step`, `linear`, or `smooth`), `autoplay`, and non-overlapping ordered `phases` with `id`, optional `label`, `startMs`, `endMs`, optional `focusId`, and a source-only `values` patch.
- `world`: use `null` for compact plans. In navigable plans, the compiler emits the validated world mode, armature, root district, bounds, districts, directed links, and derived `trunk`, `crosslink`, or `feedback` tree roles.
- `navigation`: use `null` for compact plans. In navigable plans, the compiler emits the fixed outer camera viewport, world bounds, depth-0/1/2 anchors, semantic-zoom thresholds, initial anchor, and deterministic route. Add `navigation` to `syncModes` only when this object exists.

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
- Navigable root: also expose the current camera anchor, tier, route time, and camera revision. Commit these attributes before one `svg-camera-change` event and never reuse `data-state-revision` for camera movement.
- Root and module groups: use `role="group"`, not an atomic `img` or `application` role, so labeled descendants remain visible to assistive technology. Give the root `aria-labelledby`; give each module `data-module-id`, `data-asset-type`, and an accessible `<title>` or `aria-labelledby`.
- Bound mark: `data-role`, `data-bind`, `data-channel`, and an explicit exposed descendant role such as `img` or `meter`. Keep each binding selector local to its module group. Also keep `data-accessible-label`, `data-value-unit`, `data-accessible-value`, and `aria-label` synchronized from the same canonical value in every render transaction. Any visible text that echoes a binding must update from that same formatted canonical value in the same transaction. Generated `data-flow-source-label` text must combine its stable base label with the current accessible value; `data-flow-value-label` text must exactly mirror the branch mark's current accessible value. Put the human label, formatted value, and unit in the accessible name; never expose an internal value ID. Use `aria-valuemin`, `aria-valuemax`, `aria-valuenow`, and `aria-valuetext` only for a genuine range role such as `meter`; do not put ignored range properties on `role="img"`. Do not accept DOM attributes alone: correlate each DOM node to its own Chromium accessibility node, including duplicate labels within one module, after every scenario, source perturbation, and legal zero-flow boundary.
- Focus target: `data-focus-group`; separate focus control: `data-module-focus-id`, `role="button"`, camera-appropriate `tabindex`, and synchronized `aria-pressed`. In a navigable world, only world district controls, active-district module destinations, or active-module focus controls enter tab order at their respective tier; every off-camera control uses `tabindex="-1"`.
- Root timeline state: `data-time-ms`, `data-phase-id`, and `data-phase-progress`.

Restrict `channel` to an explicit allowlist such as `text`, `x`, `y`, `width`, `height`, `r`, `path`, `transform`, `opacity`, `class`, or `aria-value`. Give each binding exactly one value source. Use multiple bindings when a value drives multiple channels. Preserve the same unit, direction, category color, and meaning wherever a concept recurs.

When `identity` is present, include at least one declared non-color cue in every bound role for that identity, such as `tax-step`, `tax-rate-label`, or `tax-needle`. Every bound appearance of one identity must resolve to its declared canonical value token. Distinct identities may reuse a color only when that reuse is deliberate and their visible non-color cues stay disjoint; identical color/cue signatures are a conflation error.

