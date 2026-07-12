# Asset Selection And Composition

Use this reference before drawing modules. Select assets from the questions the composition must answer, then choose one global armature and one shared identity system. The result should read as one explanatory object, not as unrelated dashboard cards.

## Start From Questions

1. State the overall idea in one sentence.
2. List viewer questions that expose different facets of it.
3. Turn each useful question into one complete module claim that visible marks can support.
4. Name the source or derived concepts needed by each claim.
5. Remove questions that repeat another claim, require unavailable data, or are clearer as short text.

Do not choose a chart merely to add variety. Prefer the simplest asset whose channels answer the question without distorting the data.

## Match Questions To Assets

| Viewer question | Prefer | Reject when |
| --- | --- | --- |
| What is the exact value, target, or state? | Direct value, bullet, compact table row, inline bar | A large chart adds no context beyond one number |
| Which item is larger, better, or ranked? | Aligned bars or dots, slope chart, ranked table | Area, angle, or color would make comparison less precise |
| What makes up the whole? | Stacked bar, waffle, treemap, nested units | Parts do not sum to a meaningful whole |
| How does it change over time? | Line, area, event strip, time small multiples | Only two states exist; use a before/after view |
| What is the distribution? | Raw dots, beeswarm, histogram, box plus observations, violin | A summary would hide meaningful shape or outliers |
| How are quantities related? | Scatter, connected scatter, matrix, model or interval overlay | The apparent relationship is only ordering or a shared time trend |
| What causes, transforms, or gates what? | Flow spine, process, state machine, sequence lanes, fault tree, schematic | Items are peers without a real causal or ordered path |
| What is allocated, split, lost, or transferred? | Sankey, alluvial, route bands, swimlanes | Band width cannot be tied to a quantity |
| What is the hierarchy or containment? | Tree, icicle, treemap, radial hierarchy | The nesting or center has no semantic role |
| Where is capacity, pressure, or a threshold? | Bullet, threshold bands, queue grid, capacity slots | A decorative gauge would conceal the scale or target |
| What could happen under uncertainty? | Point range, forecast fan, scenario tree, probability cells | Interval or probability semantics are unavailable |
| Where does location change the answer? | Map, route map, spatial grid, symbol map | Ranking or trend is the real question |
| How do many records or pairwise states compare? | Matrix, heatmap, embedded-mark table, adjacency matrix | Text or cells become unreadable at the target viewport |

Use stacked bars only with disjoint nonnegative parts that reconcile to one declared total. In a compact brief, set `stackTotal` to that canonical total. The compiler anchors the shared visual domain at canonical zero even when the total's credible source domain begins above zero. If quantities overlap, can become negative, represent subsets, or use incompatible units, choose grouped or diverging bars, a table, a network, or another non-additive form instead.

Use generated flows only when one same-unit source reconciles algebraically to mutually exclusive branches. Put the source first in the flow module's `values`; positive branches move forward, while a semantically intentional negative branch renders as a reverse deficit flow. Defaults, scenarios, and audited runtime states must conserve. The compiler can infer a source from a direct `add` or n-ary `subtract` reconciliation and reorder it, but explicit source-first authoring remains clearer and is preferred. Use a table or network for independent, overlapping, mixed-unit, or nonconserving quantities.

Treat part, subtotal, and total as a hierarchy in both mathematics and prose. Never add a conserved total to one of its own branches in a derived rollup, and never list a subtotal beside an already-included constituent as though both independently compose the next total. State the equations or stages explicitly. Use a table or arithmetic bridge for a static equality, unit conversion, or reconciliation. Choose a line/timeline asset only when the values form a genuine ordered progression with a meaningful axis; two synchronized values that should be equal are not a time series.

Use ordinary non-stacked bars only for a direct magnitude comparison in one canonical unit. Every bar must stay nonnegative, begin at the same zero baseline, and use one shared domain, range, and pixels-per-unit slope. Do not normalize each item to its own maximum: a smaller value must never appear longer than a larger peer. Until an explicit diverging-bar renderer exists, move values whose legal envelope crosses below zero to a flow, exact table, or another signed encoding.

Name each compact `assetType` with a supported semantic renderer token: bar/column/stack, flow/sankey/process, gauge/bullet/progress, line/timeline/series, network/graph/tree, spatial/map, table/matrix/grid, or waterfall. Do not invent generic `metric-card`, `panel`, or `surface` names and accept colored fallback blocks as evidence. If the desired form is not one of the eight generated families, choose the closest honest supported form or request explicit bespoke geometry.

Pair overview and detail assets only when their questions differ. A treemap can show compensation mix, a waterfall can show deductions, and a projection can show future accumulation. Three styled amount bars do not provide three facets.

Use a generated waterfall as an arithmetic bridge: order one nonnegative opening total, zero or more sign-stable deductions, and one nonnegative ending balance, all in the same unit. A deduction may be authored as a nonnegative magnitude or a nonpositive canonical value, but its inferred envelope must not cross zero. Every binding must map canonical zero to visual zero and use the same absolute pixels-per-unit slope. Opening minus deduction magnitudes must equal ending in every named scenario and sampled timeline state. Do not mix overlapping rollups, independent amounts, rates, and residuals merely because they share a unit; use grouped bars, a flow, or an exact table when there is no honest sequential reconciliation. Wrapper clipping is only a mechanical guard: any visually clamped waterfall step is a blocking arithmetic, ordering, or domain error.

Use the generated radial gauge only for a bounded fraction whose full legal envelope stays inside `[0, 1]` and increases from the left endpoint to the right endpoint. Its visible arc is a 180° upper semicircle, so declare the needle transform as `rotate` with range `[-180, 0]` (or equivalent `[180, 360]`). A demand/capacity ratio that can exceed 100% is load or overload evidence, not utilization: name it accordingly and use a bullet or capacity band with an explicit 100% threshold. Anchor percentage bullet/progress geometry at canonical zero; before saturation, its distance to the target must equal `value / target`. Keep exact negative or above-range values in the synchronized readout even when the visible mark clamps to zero or the 150% ceiling. A wider dial sweep is a semantic mismatch.

Use compact network and hierarchy assets to explain topology. Their generated nodes have equal area and exact synchronized value/unit readouts; every edge comes from a direct dependency declared in the derived-value DAG. Put at least one related source/derived pair in `values`, and reject a network whose only relation would be a decorative hub or generic “shared state.” When the claim spans a transitive dependency, include every intermediate node so the visible graph contains the claimed path; a total and distant leaves with the connecting subtotal omitted are not a composition diagram. Do not encode unlike units as comparable node radii. If quantitative node size is genuinely necessary, use one common unit, one shared domain, area-correct scaling, and a visible scale in bespoke geometry; otherwise keep node size structural.

Keep compact module value lists purposeful. Dense generated bars, tables, and networks adapt their columns, rows, and cards to the assigned body, but packing is not a substitute for selection: split a bar list when more than six values no longer share one comparison task, and split a network or table when more than roughly eight values obscure the dependency or lookup question.

Treat the sign of a generated flow as semantic. Decide zero and direction from the exact raw canonical value after negative-zero normalization, never from transformed pixel magnitude. Positive values move from the source to the destination, exact zero values have zero visible thickness, and negative values render as a dashed reverse band with an arrow and `DEFICIT` cue. Keep the signed exact value in its rail; never coerce a negative residual into a thin positive allocation. Keep the source header and every branch value label synchronized from the same formatted accessible value after every transaction; do not leave initial fallback text frozen while geometry changes.

## Score Candidates

Score each serious candidate from `0` to `2` on:

- **Question fit:** directly answers the module question.
- **Data truth:** channels map to declared data or state.
- **Complementarity:** adds a facet not already covered.
- **Binding value:** exposes a useful source or derived concept and coordinated change.
- **Composition fit:** fits its region with readable labels.
- **Portability:** can be inlined with deterministic geometry and no remote runtime.
- **Motion value:** state change teaches more than an entrance.
- **Accessibility:** meaning survives without hover, motion, or color alone.

Require at least `12/16`, with no zero for question fit, data truth, or binding value. Break ties in favor of the simpler, more portable asset. Store the decision in each compact-brief module as `selectionRationale` and `rejectedAlternative`; name why the chosen form wins and why the nearest candidate loses.

Reject a candidate immediately when it:

- bends quantitative geometry to a decorative armature;
- duplicates another module's question, concepts, and primary channel;
- needs invented values, categories, links, or precision;
- has no meaningful settled frame;
- depends on a paragraph, legend, or hover state for its main claim;
- introduces an independent clock or nondeterministic layout;
- cannot fit its longest required label at the smallest viewport.

## Check Coverage And Nonredundancy

Build three small matrices before implementation:

1. `question x module`: every accepted question has one clear owner.
2. `concept x module`: every intentionally shared concept appears in at least two modules, and every module names its concepts.
3. `phase or scenario x module`: every coordinated state has visible evidence in the expected modules.

Merge or remove modules that answer the same question with the same concept and channel. Keep two views of one concept only when the viewer tasks differ, such as exact lookup versus distribution or current state versus projection. A structural overview without a numeric binding is allowed only when it explains relationships needed by bound modules.

Do not force every concept into every module. Bind only consumers whose meaning changes. Give essential exact values a text, axis, table, or accessible-value path. Prefer a small complete set over a crowded set of weak facets. Use 13–16 modules only when the composition is intentionally a megacanvas, every module owns a nonredundant question, and one canonical semantic model plus a readable overview binds the extra detail together.

## Choose One Global Armature

Choose from the dominant story, not from the module count.

| Armature | Use when | Avoid when |
| --- | --- | --- |
| Modular grid | Peer modules need equal comparison | One module is clearly dominant |
| Masonry megacanvas | Importance and density vary; overview and detail coexist | Equal peers are the real structure |
| Flow spine | One causal, temporal, or handoff path organizes the whole | Modules share concepts but no path |
| Diagonal progression | Escalation, growth, conflict, or before-to-after matters | The story should feel balanced or cyclical |
| Radial hub | A real center, cycle, orbit, or peer-spoke relation exists | The center is decorative |
| Golden or root split | One dominant field needs a smaller evidence field | Both fields are equal peers |
| Balanced split | Two states, forces, or options need equal weight | Three or more peers are central |
| Dense label lanes | A central field needs external labels and leaders | Direct labels already fit |

Order compact-brief modules by intended reading preference and choose asset families before drawing marks. Above twelve modules the compiler preserves that order across the four-row megacanvas; for smaller briefs it may move heavy flow, network, spatial, or dense-table modules into wider slots while recording the resulting `layout.readingOrder`. The compiler assigns the root `viewBox`, safe module regions, baselines, and gutters. Record the intended armature in the brief. The current compact compiler preserves that intent as metadata while applying its validated asymmetric layout; use the advanced full-plan surface only when the task truly requires another geometry. Never hand-patch generated regions.

## Declare Honest Cross-Module Relationships

Use a relationship only when a viewer should follow a real handoff, dependency, or feedback path between two modules. Add compact records shaped like:

```json
{
  "id": "queue-to-cache",
  "source": "queue-pressure",
  "target": "cache-path",
  "kind": "flow",
  "label": "Queued requests probe the cache"
}
```

- Use `flow` for transfer or ordered handoff, `dependency` when one module's state informs another, and `feedback` when an observation closes a control loop.
- When the task asks for a forward causal chain, require all named facets to belong to one connected relationship component and let feedback return into that same spine. Do not submit several unrelated pairs or leave an obvious downstream branch detached.
- Make feedback evidence explicit. The target must either expose a recommendation derived from a source-module signal in the canonical DAG or a declared policy/source control that changes in a later scenario or phase after that signal. Because the state graph is acyclic, represent observation and subsequent actuation as an evidence-backed handoff; never use a connector to imply a computational dependency that the values do not contain.
- Connect two distinct declared module IDs. Keep IDs unique and labels readable without internal terminology.
- Let the composer route forward links through module gutters and feedback links through exterior lanes. Do not draw independent connector fragments or animate them on separate clocks.
- Keep incident markers at least 15 user-space pixels apart on the edge where they are actually painted. Allocate every lane before drawing and never apply a later clamp that collapses distinct route IDs onto one physical coordinate.
- Keep region names in the label-free half of a gutter. When a legitimate route must share that space, use the generated cartographic plaque: render the region fill first, the relationship path second, and an opaque label plaque plus text last. The plaque must be the label's immediate previous sibling, cover the browser-measured text box by at least 2 px, remain fully opaque and visible, and follow the path in DOM paint order. Never mark a crossing as exempt without that measured occlusion.
- Focus activates a link when both participating modules belong to the focused story; a single-module focus may reveal its incident links. The moving pulse always uses master phase progress.
- A relationship does not couple values. Canonical concepts and the derived DAG remain the only authority for semantic propagation.
- Omit connectors when shared state and identity are sufficient. Decorative arrows, generic hubs, and links whose direction cannot be defended are composition errors.
- Keep at most 18 visible relationships in the generated footer key and route layer. For a denser graph, retain the explanatory spine here and move exhaustive adjacency to a dedicated network module.

At overview scale, the primary region, secondary region, reading path, and active shared concept should remain apparent. Avoid nested-card chrome, repeated title bars, and equal boxes that turn the SVG into generic UI.

## Preserve Shared Identity

Define one identity record for every recurring concept:

- semantic color and neutral fallback;
- shape, stroke, dash, texture, or glyph cue;
- unit and number format;
- active, inactive, risk, and selected treatment;
- label vocabulary and abbreviation policy.

Keep exact shared values canonical in the compact brief and bind the same value ID wherever it recurs. The compiler assigns each source an enforceable canonical color token, non-color cue, and alias record. It preserves that identity automatically through direct references and pure constant multiplication, division, or rounding; a multi-input computation receives a distinct identity. Use `colorSource` only for deliberate inheritance from any genuine canonical source or derived ancestor that the compiler cannot infer. Use the advanced full-plan identity surface only when several different source/derived IDs are genuinely equivalent variants of one identity; justify that grouping and never alias values merely because they have similar labels, share a unit, or happen to use the same local palette.

The validator checks the declared canonical value token on each bound mark and checks that its `data-role` retains a declared non-color cue. Two distinct identities may share a color only when their non-color cues remain disjoint; they must never share the complete color/non-color signature. Unit conversions and rate/amount forms may be aliases when the rationale makes the semantic relationship explicit.

Keep these cues stable while geometry changes by asset. Salary may be a bar length, waterfall source, and projection input, but its accent, unit, and label identity should remain recognizable. Use a non-color cue for important concepts. Focus should add outline, halo, weight, or contrast rather than silently changing semantic color.

Let the shared identity override module-local palettes. Give derived concepts related but distinguishable cues. When two appearances use different scales, declare their units, domains, and transforms; never imply shared pixel magnitude.

## Import SVG Assets Safely

1. Render stable final geometry before import.
2. Copy asset content into a module `<g>` under the single root SVG. Map local coordinates into the declared region with one documented transform.
3. Prefix every imported ID as `<composition-id>--<module-id>--<source-id>`.
4. Rewrite matching `url(#...)`, `href`, `xlink:href`, fragment links, ARIA references, markers, masks, clips, filters, gradients, patterns, and SMIL `begin` or `end` references.
5. Scope classes, CSS custom properties, animation names, and keyframes that could collide.
6. Retain or move `<defs>` only after references are prefixed; never concatenate definition blocks blindly.
7. Remove remote scripts, fonts, styles, and images. Embed an indispensable image as a data URL and provide accessible context.
8. Disable autonomous CSS, SMIL, D3, Mermaid, or chart-library animation. Rebind meaningful changes to the composition clock and canonical state.
9. Preserve quantitative geometry and mark vocabulary. Recompose placement and emphasis, not facts.
10. Open the final SVG directly and inspect markers, masks, gradients, text, and clipping.

Prefer plain SVG text for portable output. Use `foreignObject` only when the target explicitly supports browser-only SVG documents.

## Composition Review Gate

Reject or recompose when:

- the page reads as disconnected cards;
- connectors exist only to prove relation;
- one concept has conflicting color, unit, direction, or category meaning;
- a visible value label, accessible value, or data-bearing mark changes without the other two settling to the same canonical value in the same transaction;
- a generated flow's source and algebraic branch sum do not reconcile in the current rendered state;
- modules repeat one claim with cosmetic variation;
- major regions float without a grid, axis, balance, spine, or intentional negative space;
- labels collide, clip, cross moving marks, or depend on ellipsis;
- imported IDs, definitions, selectors, or animation names collide;
- the initial, reduced-motion, or settled state is blank or misleading;
- decorative motion, controls, or panel chrome compete with the explanation;
- DOM size or per-frame mutation makes play, seek, or focus sluggish.

Fix structure before styling. Remove a module, change the asset family, resize regions, or choose a stronger armature before adding color or motion polish.
