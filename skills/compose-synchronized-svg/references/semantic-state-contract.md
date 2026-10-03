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

Write the idea-specific contract, pass it through `preflight_svg_brief.py`, and let `compile_synchronized_svg_plan.py` expand mechanics only after preflight reports `ok: true`. A compact brief keeps source records, derived computation trees, scenarios, modules, a global armature name, optional cross-module relationships, focus groups, and optional timeline phases. A navigable-world brief adds `world`, optional explicit `module.diagram` records, and a deterministic camera route while retaining the same canonical value model. For each module, provide a `values` list instead of manual selectors or channels:

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

Use 6–12 modules in a normal compact brief and extend to 13–16 only for a true fitted megacanvas. Use 12–48 modules in navigable-world mode, partitioned exactly once across 4–12 districts with 1–8 modules each. In world mode the overview communicates topology, district views provide labeled local destinations, and module views expose complete diagrams; do not demand readable chart detail at fit-to-world scale. Use exactly `en-US`; the compiler rejects every other locale. The Python literal formatter and browser `Intl.NumberFormat` path must agree on grouping, half rounding, currency sign placement, percentages, suffixes, and normalized zero. Common currencies use the same symbol map in both paths; other valid three-letter currency codes use the code plus a nonbreaking space deterministically instead of a browser-specific symbol.

Keep `values` unique within a module and order them by visual importance. For a stacked bar, list only mutually exclusive nonnegative parts and set `stackTotal` to the canonical total whose domain every segment must share; this makes segment lengths additive and the visible ceiling truthful. Detectable derived subtotals are moved to exact readouts instead of being stacked twice. For a flow module, put the conserved same-unit source total first and list only mutually exclusive branches after it. Flow conservation is algebraic: signed reverse or deficit branches are allowed when semantically justified, but the branch sum must equal the source in defaults and every scenario, and the browser audit rechecks conservation after legal state changes. Use a network or table when the values do not form a conserved partition.

Each source starts with its own canonical color token. Direct references and pure constant multiplication, division, or rounding inherit the ancestor identity automatically; multi-input computations remain distinct. A derived record may set `colorSource` to any genuine canonical source or derived ancestor when deliberate inheritance is semantically useful and is not inferred; the compiler rejects unrelated color ancestry. Network modules without `module.diagram` use equal-area nodes, exact synchronized readouts, and only real edges from the declared dependency DAG. Include at least one source/derived dependency pair in such a network's `values`; otherwise choose a non-network asset or declare a connected qualitative diagram. An explicit diagram uses 2–18 nodes, 1–32 links, a `tree`, `radial`, or `lanes` layout, documented node/link kinds, and exactly one node binding for every numeric module value. It may include unbound qualitative nodes.

Use node kinds `root`, `notable`, `merge`, `gate`, `leaf`, or `evidence`. Use link kinds `parent`, `prerequisite`, `dependency`, `flow`, or `feedback`. Wrap complete labels into readable lines and never rely on ellipsis at module tier.

Use a radial gauge only for a fraction whose full legal envelope stays inside `[0, 1]` or an equivalent percentage-point value whose envelope stays inside `[0, 100]`; the composer renders both unit systems without multiplying percentage points twice. Represent a load or target ratio that can exceed 100% with a zero-anchored bullet or progress asset and its 100% marker. Name an unbounded demand/capacity result as a load ratio, not utilization. Declare no more than 18 module `relationship` records, only between distinct modules, and choose `flow`, `dependency`, or `feedback`; the composer routes them without changing value semantics. A module may belong to at most four top-level focus groups so every story retains a distinct visible control. Focus groups that form contiguous rows or columns become subtle labeled composition regions, and timeline phases expose a visible label and progress rail. For `loop: true`, exact `durationMs` wraps to time zero; add a return-to-start final phase only when the approach to that seam should also be visually smooth. In world mode, `world.links` separately define district topology; require directed non-feedback reachability from `rootDistrictId`. Treat route `focusId` and `handoff` as narration metadata, not state patches. The compiler derives `dependsOn`, layout, reading order, selectors, channels, transforms, formats, identities, aliases, spatial anchors, tree roles, and exact phase or route boundaries. If it reports a safe divisor-domain normalization, preserve that report beside the plan. Fix compiler errors in the brief and regenerate; never patch compiler output.

Never create a derived rollup that adds a conserved flow total to one of its own branches; the compact compiler rejects the detectable additive form because it counts the same quantity twice. A signed `total - branches` reconciliation is valid. When visible text names a subtotal and its constituents, state the hierarchy explicitly instead of presenting the subtotal and an included part as peers. Show a static equality or unit conversion with a table or arithmetic bridge. Use a line/timeline module only for a genuine ordered progression with a meaningful axis, not for two values whose sole claim is that they are equal.

For a network claim, include the complete direct-dependency path between every selected ancestor/descendant pair; the compiler rejects a transitive pair with an omitted intermediate bridge. For a scenario-isolation promise, audit at module level as well as value level: a module described as unchanged must bind only values outside the changed dependency closure. When the task requests a forward chain, keep every required facet in one connected relationship spine. A feedback label must distinguish a current required response from a deployed response that persists after the triggering risk has fallen, and its DAG or ordered phase story must support that distinction.

For an exact ledger or table, define every value named `total`, `check`, `reconciliation`, `residual`, or `remainder` by an explicit equality before encoding it. A partition check may be `sum(parts)`, `whole - sum(parts)`, or a visible comparison between the two; never add a conserved whole to the same allocation or rollup parts it already contains. Verify the equality in every scenario.

## Optional extension contracts

- Read [compiled-plan-and-bindings.md](compiled-plan-and-bindings.md) only for an explicit custom-fragment request or compiler-contract maintenance.
- Read [runtime-api.md](runtime-api.md) only for direct API integration, custom interaction tests, or runtime maintenance.
- Use [spatial-world-and-camera.md](spatial-world-and-camera.md) for navigable-world authoring and camera contracts.

Normal generation stays at the brief level and uses the bundled composer and auditor.
