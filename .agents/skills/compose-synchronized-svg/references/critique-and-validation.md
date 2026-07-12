# Critique and Validation

Use this review after generating a synchronized SVG and after every material change. Validate semantics before polish. A high score never compensates for wrong data, false coupling, a blank fallback, or inaccessible controls.

## Keep evidence

Keep review artifacts outside the read-only skill bundle. Preserve the compact brief, compiler result, compiled plan, SVG, validation report, serialized state checkpoints, overview screenshots, readable module crops, and a contact sheet covering representative states, reduced motion, and the script-free fallback. Pause playback and use deterministic calls after `window.svgSync.ready`; never grade a wall-clock animation at an arbitrary instant.

Use the bundled auditor as one supervised command. It runs the browser worker in an isolated process group with kill-on-close containment where supported, sweeps surviving descendants after exit, handles cancellation and POSIX terminal closure, and retries one timeout internally. It preserves real failure codes and emits retained timeout diagnostics only when both attempts time out. Do not wrap it in a second shell retry, because the strict trace must distinguish a recovered transient startup hang from a repeated timeout or real semantic failure.

## Pass blocking checks first

Every item must pass before scoring:

1. **Artifact integrity:** the exact output exists, parses as SVG, has a finite positive `viewBox`, unique stable IDs, root `title` and `desc`, and no `NaN`, `undefined`, or unresolved template tokens.
2. **Standalone output:** data, geometry, styles, fonts or fallbacks, controls, and runtime logic are local. Reject network requests, external scripts or CSS, remote images, and external `<use>` references.
3. **Plan integrity:** concepts and units are valid; derived references resolve; the dependency graph is acyclic; scenarios patch source concepts only; selectors resolve locally and uniquely; bindings use allowed channels; focus and phase IDs resolve.
4. **Semantic coverage:** every essential claim is visible, each module has a distinct useful claim, and the module-concept graph is coherent even when modules have no visual connectors. Reject decorative or generic fallback modules presented as evidence, unsupported asset names that render only anonymous blocks, network edges without a declared semantic relation, networks whose selected transitive endpoints omit a required intermediate dependency, conflated outcomes such as rework versus loss, stock labels attached to rates, node areas that compare incompatible units, ordinary bars with mixed units, independent domains, a nonzero baseline, or negative legal states, utilization scales above 100%, accidental physical color reuse between distinct identity tokens, waterfalls without one shared zero-anchored scale and exact opening-minus-deductions reconciliation, progress marks whose distance to the 100% target differs from their canonical ratio, flows with mixed units, non-finite values, or a source that differs from the algebraic branch sum in any audited state, and any ledger `total` or `check` that adds a conserved whole to the same allocation or rollup parts it already contains. Also reject prose that treats a subtotal and an already-included constituent as peer components, plus a static reconciliation drawn as a line without a real ordered axis. Require the stated reconciliation equality to hold in every scenario.
For feedback specifically, reject a target value that is unrelated to the source signal and has no explicit later policy or actuation change. Require the causal handoff to be visible in the canonical DAG, named scenarios, or ordered phases; a connector and persuasive label are not evidence by themselves.

5. **Runtime correctness:** `ready` resolves; public calls return finite stable snapshots; invalid calls cause no partial mutation; successful calls settle the DOM synchronously; no console or page error occurs.
6. **Synchronization correctness:** every changed value reaches its complete dependency closure, every affected binding updates, unrelated bindings remain unchanged, and scenarios never reveal mixed old and new state.
7. **Visible and accessible usability:** no essential mark or label is clipped, unreadably small, obscured, or dependent only on hover, motion, or color. The SVG root and module containers are non-atomic groups; every bound mark is a separately exposed, human-named browser accessibility node with the current formatted value; controls are labeled, keyboard reachable, and visibly focused. For generated flows, require the visible source header and branch value labels to match their current accessible values after every scenario, perturbation, phase, and zero-flow state. Emit module groups in `layout.readingOrder` and require Chromium's module traversal to follow that same visual sequence. Module focus uses a separate button semantic with synchronized `aria-pressed`, never an unlabeled interactive group. Focus may dim marks or borders, but must not lower text below 4.5:1 or dim an ancestor that contains essential text. Resting relationship paths must remain visibly distinguishable in the static fallback instead of depending on active focus or animation for sufficient contrast.
8. **Evidence honesty:** a concise visible provenance note distinguishes sourced, assumed, simulated, and synthetic values. Never rely on metadata alone or present illustrative precision as observed evidence.
9. **Fallback behavior:** the literal SVG is meaningful without script, and reduced-motion mode disables autoplay and nonessential transitions without removing information. Playback controls expose their current visible and accessible state; disable or remove them from keyboard order when reduced motion makes playback unavailable.

Stop at the earliest failing layer, repair it, and rerun all earlier layers before interpreting later results.

## Test propagation and isolation

Build expected affected sets from the plan, not from observed DOM changes. For each source concept:

1. Reset to a known scenario. Record `serializeSnapshot()`, bound DOM values, focus, time, event count, and any revision token.
2. Apply a legal perturbation large enough to cross a formatting, scale, or clamp boundary. Compute the transitive derived-value closure.
3. Require an observable update in every module that binds the source or a descendant. Rendered values must agree with the returned snapshot and declared transform or format.
4. Require modules outside the closure to retain identical bound values. This negative control catches global side effects and concepts coupled only by similar labels.
5. Try an invalid value, unknown ID, and derived-value override. Snapshot, DOM, focus, time, event count, and revision must remain unchanged.

For every flow value with a legal zero somewhere along a one-source domain slice, discover and render at least one non-baseline boundary. Sample the interior before bracketing so multiple roots are still found when both domain endpoints have the same sign. Accept the boundary only when browser recomputation produces exact canonical zero after negative-zero normalization; a numerical residual is not zero. When no exactly representable root exists, retain the adjacent-sign diagnostic as `noExactRepresentableRoot` instead of recording a false zero-flow pass. Require zero visible thickness, a neutral `zero` direction, no reverse arrow, dash, or deficit cue, and a human-readable zero rather than negative zero. Keep positive and negative tests as separate states.

Rounding or clamping can legitimately preserve a capped independent bar or progress mark. In that case, choose another legal input or prove the unchanged formatted result matches the plan. Waterfall clamping and material stack clipping are never legitimate: they are blocking arithmetic, ordering, domain, or reconciliation failures. Ignore only sub-quarter-pixel stack serialization noise.

### Atomicity and revision

Listen for `svg-sync-change` before a mutating call. Require exactly one event for one committed transaction, with the DOM already matching its snapshot inside the listener. No module may issue a later semantic commit.

If the runtime exposes a revision, require one increment per successful transaction and the same revision on all updated modules or marks. Failed calls must not advance it. Otherwise, use the harness event sequence as the transaction revision and prove that all expected bindings settled within that one event.

### Idempotence

Run the same patches, scenarios, focus changes, and seeks in two fresh browser loads. Require byte-identical snapshots and DOM state at every checkpoint. Within one load, reapplying current state must keep the revision and snapshot unchanged. When comparing sequences separated by `reset()`, normalize the monotonic revision. No replay may drift geometry, duplicate nodes, or compound transforms.

For a timeline, call `pause()` and sample every phase start, midpoint, end, and loop boundary with `seek(ms)`. Derive the expected phase progress independently from the requested time and phase bounds; require the snapshot, root attribute, visible phase label, and relationship pulses to agree with that oracle. All modules must read one composition clock. A modeled semantic lag is valid; independent module timers are not.
Require a visible current phase or scenario label plus progress cue while playback is available. If motion has no inspectable narrative state beyond scenario buttons, omit the timeline instead of adding an opaque Play control. For a loop, require the semantic and rendered state at `durationMs` to match time zero exactly.

### Relationship and interaction checks

When the plan declares cross-module relationships:

1. Require one stable DOM relationship group and visible key item per declared ID, the correct source/target module IDs, a readable label, and one visible arrow path. Require unique incident ports separated by at least 15 user-space pixels at the painted module edge, unique physical route lanes without post-allocation clamp collapse, stable user-space markers, and distinct line treatments for flow, dependency, and feedback. Duplicate, missing, undeclared, or physically overlapping unbundled links fail the plan.
2. When the brief promises one forward causal chain, require every named facet to occur in one connected relationship component and feedback to close that same component. Reject a set of disconnected pairs even when every individual route is geometrically valid.
3. Inspect routing at overview scale. Forward paths should use adjacent gaps or shared row gutters; feedback should use deliberate exterior lanes. Reject any connector that cuts through a module's essential text, marks, focus-region label, or relationship key. A focus-label crossing is acceptable only when the generated opaque plaque fully covers the browser-measured label with the required clearance and is painted after the path; a data attribute alone is never evidence of clearance.
4. Pause and seek into every focus phase. Require the active set to match the focused endpoints, unrelated links to remain contextual, and each active pulse to occupy the declared path at the same master phase progress.
5. Seek twice inside one phase and prove the pulse moves without changing semantic values. Under reduced motion, hide the moving pulse while preserving the relationship path, direction, and label.

Exercise real input, not only API calls. Click and keyboard-activate every module focus control—including every membership on a multi-story module—toggle each off, clear focus with Escape, use Home/End and arrow keys on the timeline, seek with a pointer, apply a scenario, and toggle Play/Pause. Every control must pause or preserve playback exactly as specified, expose visible focus, synchronize `aria-pressed` across all controls that target the same group, and produce no console or page error.

## Review both visual scales

A giant SVG need not expose every detail when fitted to one screen. Its overview must explain the structure, and every module must become clear at its intended crop or zoom.

### Macro overview

Capture the complete `viewBox` for the initial state and each materially different scenario or phase. Check:

- one clear entry point, focal hierarchy, and plausible reading path;
- semantic grouping rather than a uniform wall of cards;
- balanced mass without unexplained dead zones or overloaded corners;
- distinct modules using visual forms suited to different questions;
- recurring concepts preserving units, direction, labels, category colors, and meaning;
- connectors only where they encode a real relationship, use clear gutters, and reveal the active causal path without crossing essential content;
- focus states coordinating attention without making other modules unreadable.

### Module crops

Capture every module near its intended reading scale in the initial state and any state that changes it materially. Check:

- title, claim, value, unit, legend, axes, and annotations fit;
- no text collision, truncation, ambiguous leader, hidden mark, or misleading scale;
- labels remain attached to the correct marks after perturbation;
- generated flow source and branch labels remain synchronized after state changes, and their displayed algebraic values conserve;
- area, length, position, order, and direction agree with the state;
- structural network nodes remain equal-area unless one common quantitative scale is explicitly declared, dependency edges match the model, and load ratios above 100% use a threshold view rather than a bounded-utilization dial;
- repeated elements have deliberate alignment and spacing;
- the module remains understandable without the overview or animation.

Use browser-resolved bounds to find clipping, text overlap, body marks crossing above `data-content-top`, and a module footprint below 70% of either canvas dimension; then inspect screenshots. Measure footprint against the transformed SVG content box, not CSS letterboxing created by `preserveAspectRatio`. Bounds can flag intentional nesting or halos, while clean geometry cannot prove hierarchy or asset suitability, so visual review decides both cases.

## Verify static and reduced-motion modes

Test two additional loads:

1. **Script-free:** render as an image or block scripts. Require a complete initial scenario in literal geometry and text. Hide controls that cannot work. Essential marks must not start transparent while waiting for initialization. Require every visible and accessible formatted value to equal the initialized `en-US` runtime string for the same initial snapshot.
2. **Reduced motion:** set `prefers-reduced-motion: reduce` before loading. Require autoplay and CSS/SMIL motion to stop at a stable meaningful state. Semantic, scenario, and focus changes must still apply immediately. Preserve every essential distinction with text, shape, pattern, or another non-color cue. If the playback control remains visible, require an explicit disabled label, `aria-disabled="true"`, and removal from keyboard order.

Capture both modes and compare their visible claims with the normal initial state. Different choreography is acceptable; missing meaning is not.

## Use a reconciled 100-point rubric

Score each category from zero to its maximum and show the arithmetic. The maxima total exactly 100:

| Category | Max | Full-credit evidence |
| --- | ---: | --- |
| Aspect and asset selection | 20 | Nonredundant claims use forms suited to their questions and data. |
| Semantic truth and synchronization | 20 | Units, derivations, closure, atomic updates, and negative controls are correct. |
| Macro composition and reading path | 15 | Hierarchy, grouping, balance, and navigation are deliberate. |
| Cross-module visual language | 10 | Shared concepts retain meaning while modules remain distinguishable. |
| Module legibility and craft | 10 | Crops have clear labels, scales, spacing, and truthful encodings. |
| State, focus, and time choreography | 10 | Changes are deterministic, coordinated, and narratively useful. |
| Accessibility and fallbacks | 10 | Titles, controls, focus, contrast, static mode, and reduced motion work. |
| Portability and efficiency | 5 | Output is self-contained, responsive, reasonably sized, and avoids errors or needless DOM duplication. |

Zero means absent or unusable, half credit means functional but materially weak, and full credit means no actionable issue remains after direct evidence review. Require at least 85/100, at least 80% in each of the first three categories, and at least 60% in every other category. A score never overrides a blocker.

## Exit after two clean rounds

Each critique round must rerun blockers and perturbations, regenerate screenshots, inspect the overview before crops, rank findings by semantic harm and usability, and fix every objective or low-cost actionable issue.

A round is clean only when blockers are clear, score thresholds pass, no high- or medium-impact issue remains, and review finds no new low-cost polish fix. Exit only after two consecutive clean rounds with fresh evidence. Prefer an independent reviewer for the final round; do not show that reviewer the earlier critique before the first inspection.

Classify remaining feedback as **subjective** only when every option preserves the contract, data truth, accessibility, legibility, and acceptance criteria, and the difference is genuine taste such as equally valid palette temperature, ornament, or armature. Record the alternatives and tradeoffs. Recurring confusion, weak hierarchy, unsuitable asset choice, inconsistent meaning, or an issue raised independently by multiple reviewers is actionable, not subjective.

Turn user feedback that reveals a repeated failure or durable preference into a scoped rule and regression case. Promote transferable lessons; keep concept-specific taste decisions in project review notes.
