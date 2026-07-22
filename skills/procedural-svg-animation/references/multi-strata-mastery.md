# Multi-strata Solver Mastery

Use this reference for six patterns that expose substrate, state, analysis, geometry, and playback. They are not production solvers. Query a spec with `build_procedural_svg.py --describe <pattern-id>`.

Contents: [Alpha persistence](#alpha-persistence) · [Lower-star join tree](#lower-star-join-tree) · [Optimal transport](#optimal-transport) · [Fast Marching](#fast-marching-front) · [Physarum](#physarum-network) · [Stable fluid](#stable-fluid)

## Shared Contract

- Resolve typed `parameters` from defaults plus JSON `--config`; reject unknown keys, booleans as numbers, and out-of-range values.
- Precompute fixed-order snapshots from consequential solver events or fixed simulation steps. Keep strata in `data-stratum` groups and serialize invariant results in diagnostics metadata.
- Play snapshots forward, then backward. `palindromic-snapshots` repeats the first state at the endpoint without claiming the solver is periodic.
- Reduced motion uses the solver-selected complete, ID-safe semantic snapshot with the same strata and diagnostics; it need not be the midpoint or final frame.
- Hash canonical solver state, not presentation. `stateDigest` must remain unchanged across viewport dimensions, duration, palette, styling, and full/reduced playback for the same variant, seed, and parameters.
- Rebuild every rendered stratum from audited inputs and compare it with the canonical solver render; matching diagnostics alone are insufficient.
- Treat a failed invariant, nonfinite metric, missing stratum, exceeded catalog budget, or diagnostic-hash mismatch as a build failure.

Generate and validate any entry with:

```powershell
uv run --script skills/procedural-svg-animation/scripts/build_procedural_svg.py --pattern <pattern-id> --output output.svg --seed 104729 --width 960 --height 600 --duration-ms 8000 --palette colorset2
uv run --script skills/procedural-svg-animation/scripts/validate_procedural_svg.py output.svg --require-standalone --require-motion --expected-pattern-id <pattern-id> --expected-seed 104729
```

Also build with `--motion reduced` and omit `--require-motion`. Rebuild with the same and alternate seeds to test stability and variation. Run `uv run --script skills/procedural-svg-animation/scripts/test_multistrata_contracts.py`; its clean Alpha, transport, and Fast Marching artifacts must pass, while stratum swaps, lockstep snapshot tampering, motion-role swaps, altered Sinkhorn scalings, and altered live-trial geometry must fail.

## Alpha Persistence

Pattern: `procedural-svg-alpha-persistence`. Primary sources: [Alpha Shapes](https://www.clear.rice.edu/comp551/papers/Edelsbrunner-AlphaShapes.pdf) and [Topological Persistence and Simplification](https://www.math.uchicago.edu/~shmuel/AAT-readings/Data%20Analysis/Edelsbrunner-Letscher-Zomordian.pdf).

Pipeline: `samples` (seed → ordered sites) → `delaunay` (sites → simplicial complex) → `filtration` (complex → ordered simplices) → `homology` (simplices → persistence pairs) → `boundary` (active complex → alpha boundary) → `timeline` (ranked atomic filtration events → consequential palindromic frames).

Parameters: `point_count` integer, default 18, range 12–28; `frame_count` integer, default 7, range 5–9.

Invariants: `alpha.faceClosureErrors == 0`; `alpha.eulerResidualMax == 0`; `alpha.negativeLifetimes == 0`; `alpha.stagnantTransitions == 0`. Group equal-valued simplices as one atomic event, distribute frames by cumulative event rank, require every post-initial frame to add simplices, check faces enter only after their edges, verify `V-E+F = β₀-β₁`, and require birth ≤ death.

Loop/reduced: sweep alpha snapshots, then reverse them. The semantic static state is the frame with maximum `β₁`, breaking ties by proximity to the timeline midpoint and then by earlier index; its complex, barcode, and boundary remain synchronized. Avoid nonrobust orientation/circumcircle tests, unstably ordered ties, or treating alpha circles as homology evidence.

Validation: use the shared commands with `procedural-svg-alpha-persistence`.

## Lower-star Join Tree

Pattern: `procedural-svg-join-tree`. Primary source: [Computing Contour Trees in All Dimensions](https://www.cs.ubc.ca/sites/default/files/tr/1999/TR-99-09_0.pdf). This pattern implements the ascending join-tree half of the broader contour-tree construction; it does not claim the descending split tree.

Pipeline: `field` (meaningfully seed-varied basis → scalar samples) → `triangulation` (samples → piecewise-linear domain) → `critical-points` (lower-star order → birth/merge events) → `join-tree` (events → component tree) → `isolines` (field and level → tracked contours) → `timeline` (rank-sampled critical values, supplemented by lower-star sample events when slots remain → consequential palindromic frames).

Parameters: `grid_columns` integer, default 26, range 18–34; `grid_rows` integer, default 16, range 12–22; `frame_count` integer, default 7, range 5–9.

Invariants: `joinTree.treeStructureErrors == 0`; `joinTree.eventOrderErrors == 0`; `joinTree.componentAccountingErrors == 0`; `joinTree.stagnantTransitions == 0`. Seed the wells, hill, oscillation, and deterministic tie noise; stable-sort equal scalar samples, replay every birth/merge, and require one connected acyclic tree with exactly one parent per nonroot node and a changed state at every frame transition.

Loop/reduced: sweep critical levels upward, then reverse them; the static state synchronizes isolines, critical markers, and merge tree. Avoid bilinear cells in a PL model, ambiguous marching diagonals, or calling a merge tree a full contour tree on an incompatible domain.

Validation: use the shared commands with `procedural-svg-join-tree`.

## Optimal Transport

Pattern: `procedural-svg-optimal-transport`. Primary source: [Sinkhorn Distances: Lightspeed Computation of Optimal Transport](https://papers.nips.cc/paper/4927-sinkhorn-distances-lightspeed-computation-of-optimal-transport.pdf).

Pipeline: `source-target` (seed → weighted sites) → `cost-kernel` (sites → Gibbs kernel) → `sinkhorn` (kernel and marginals → scalings) → `transport-plan` (scalings → coupling) → `interpolation` (coupling and time → mass trajectories) → `timeline` (barycentric states → palindromic frames).

Parameters: `site_count` integer, default 9, range 6–14; `epsilon` number, default 0.08, range 0.03–0.2; `minimum_iterations` integer, default 80, range 40–160; `frame_count` integer, default 7, range 5–9. The solver may continue in bounded four-step blocks until the marginal residual reaches `1e-7`, capped at eight times `minimum_iterations` or 2,000 total iterations. Diagnostics report the actual work as `metrics.iterations`.

Invariants: `transport.maxRowError <= 0.0001`; `transport.maxColumnError <= 0.0001`; `transport.massError <= 0.000001`; `transport.scalingReconstructionMaxError <= 1e-7`; `negativeEntryCount == 0`. Normalize both marginals to equal total mass, guard divisions by tiny kernel products, reject negative plan entries, and expose residuals rather than assuming the iteration count converged. The reconstruction gate binds the final plan to the serialized `u`, kernel, and `v` through `P = diag(u) K diag(v)`.

Evidence/loop: serialize final `u`, `v`, and the Gibbs kernel at 15 significant decimal digits, plus iteration-indexed `u`/`v` checkpoints with row, column, and mass residuals. Render the kernel as heat, the active checkpoint as `u`/`v` bars, and residual history with a checkpoint cursor; preserve exact inspectable values in `data-kernel-value`, `data-scaling-value`, and `data-plan-mass`, then map every moving term back to that plan with `data-plan-entry`. Interpolate source to target and reverse; every frame reuses the final plan mass for each `Pᵢⱼ` while only its `x`/`y` position changes. Render all entries as ribbons and all moving mass terms; never infer, filter, or renormalize them for presentation. The static state shows both marginals, the complete coupling, and intermediate mass.

Validation: use the shared commands with `procedural-svg-optimal-transport`.

## Fast Marching Front

Pattern: `procedural-svg-fast-marching-front`. Primary source: [A Fast Marching Level Set Method for Monotonically Advancing Fronts](https://doi.org/10.1073/pnas.93.4.1591).

Pipeline: `speed-field` (seed and spatial modulation → positive-speed grid) → `arrival-time` (speed grid and source → Eikonal solution) → `accepted-front` (heap events → accepted/trial sets) → `isocontours` (arrival time → wavefront rings) → `geodesics` (arrival gradient and targets → backtraced routes) → `timeline` (acceptance events → palindromic frames).

Parameters: `grid_columns` integer, default 30, range 22–38; `grid_rows` integer, default 18, range 14–24; `frame_count` integer, default 7, range 5–9; `speed_modulation` number, default 0.45, range 0–0.75.

Invariants: `front.acceptedOrderErrors == 0`; `front.analyticMaxError <= 0.12`; `front.unreachableTargets == 0`; `front.trialStateErrors == 0`. Accept only the smallest trial value, test the constant-speed solution against radial distance in normalized-domain units, and require every selected target to obtain a finite arrival time. At each frame, serialize the true live heap trial state as exact comma-separated `data-trial-cell-ids` and `data-trial-arrival-times`, with `data-trial-count`, `data-trial-heap-entry-count`, and `data-trial-stale-entry-count`; do not reconstruct it from accepted neighbors.

Loop/reduced: reveal acceptance snapshots, then reverse; the static state keeps the speed field, contours, accepted/trial evidence, and geodesics. Avoid nonpositive speed, stale heap entries, noncausal updates, or describing scalar modulation as a tensor metric.

Validation: use the shared commands with `procedural-svg-fast-marching-front`.

## Physarum Network

Pattern: `procedural-svg-physarum-network`. Primary source: [Influences on the Formation and Evolution of Physarum polycephalum-inspired Emergent Transport Networks](https://ics-websites.science.uu.nl/docs/vakken/b2nb/stuff/Influences%20on%20the%20formation%20and%20evolution%20of%20Physarum%20Polycephalum%20inspired%20emergent%20transport%20networks%20-%20J.%20Jones%20-%202011.pdf).

Pipeline: `nutrients` (seed → food sources and guidance targets) → `agents` (central inoculum with stratified outward headings → Jones-inspired three-sensor movement plus bounded one-third-horizon guidance) → `trail-field` (post-move deposits → pre-diffusion field) → `diffusion` (separate buffer → post-diffusion/decay field) → `network` (decayed cumulative reinforcement → one deterministic active root nearest the inoculum → thresholded connected component → predecessor-extracted backbone) → `timeline` (scheduler snapshots → palindromic frames).

Parameters: `agent_count` integer, default 90, range 60–140; `steps` integer, default 120, range 80–180; `frame_count` integer, default 7, range 5–9; `sensor_offset` number, default 4, range 2–6.

Invariants: `physarum.nonfiniteCount == 0`; `physarum.outOfBounds == 0`; `physarum.networkConnectedSiteReach >= 0.8`; `physarum.networkBackboneErrors == 0`. Treat this as a transparent Jones-inspired hybrid, not a pure Jones reproduction: the central inoculum, bounded early nutrient guidance/coupling, cumulative network field, thresholded site reach, and sparse predecessor-extracted backbone are explicit adaptations. Preserve distinct pre- and post-diffusion fields. After burn-in, require one path per connected nutrient site, one shared deterministic root, adjacent path cells, an exact path-edge union, and structural reachability from that root.

Loop/reduced: reverse recorded states, not agent rules. Serialize the exact deterministic inoculum `networkRootCellId`, include it in the structural audit, and visibly mark it in the network stratum. The final semantic static state combines food, agents, pre/post trail evidence, the root, and the audited backbone. Avoid in-place diffusion, unseeded choices, oversized sensor offsets, or claims of biological fidelity or shortest-path optimality.

Validation: use the shared commands with `procedural-svg-physarum-network`.

## Stable Fluid

Pattern: `procedural-svg-stable-fluid`. Primary source: [Stable Fluids](https://graphics.stanford.edu/courses/cs448-01-spring/papers/stam.pdf).

Pipeline: `sources` (seeded source program and step → exact force center and dye-inlet cell) → `velocity` (add force, diffuse/project, then advect → captured pre-final-projection velocity) → `projection` (captured pre-projection divergence → removed divergence plus post-projection residual) → `dye` (diffuse/advect through the projected velocity → bounded density) → `streamlines` (projected velocity → cell-center-mapped flow traces) → `timeline` (solver snapshots → palindromic frames).

Parameters: `grid_columns` integer, default 20, range 16–26; `grid_rows` integer, default 12, range 10–18; `steps` integer, default 48, range 32–72; `frame_count` integer, default 7, range 5–9; `viscosity` number, default 0.001, range 0–0.01.

Invariants: `fluid.nonfiniteCount == 0`; `fluid.maxDivergence <= 0.08`; `fluid.dyeBoundsErrors == 0`; `projectionReductionErrors == 0`; `projectionResidualRatioMax <= 0.35`. Preserve both `advectedVelocity`/`advectedDivergenceField` and `projectedVelocity`/`divergenceField`; every captured projection must reduce the maximum residual to at most 35% of its pre-projection value, then dye advances only with the projected field. Audit the exact seeded source center/inlet against its source program. Map stored `(column−0.5,row−0.5)` velocity samples with cell-center normalization by `(columns,rows)`, not node-grid normalization by `(columns−1,rows−1)`. Audit dye before clamping and report every correction as telemetry.

Loop/reduced: play solver snapshots forward and backward; the final semantic static state shows the exact source, pre/post projection evidence, dye, and projected streamlines. Avoid unprojected dye advection, half-cell rendering drift, mixed units, weak pressure solves, or equating numerical dissipation with viscosity.

Validation: use the shared commands with `procedural-svg-stable-fluid`.
