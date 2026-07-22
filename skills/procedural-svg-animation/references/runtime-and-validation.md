# Runtime and Validation

## Embedding Modes

| Mode | SVG-native CSS/SMIL | Script and interaction | Use it for |
| --- | --- | --- | --- |
| Direct `.svg` document | yes | top-level scripts can run, but omit them for portability | deliverable and browser QA |
| Inline `<svg>` in HTML | yes | yes | interactive controls, WAAPI, pointer input |
| `<object data="asset.svg">` | yes | same-origin document access | galleries with isolated SVGs |
| `<img src="asset.svg">` | secure declarative animation may run | no | decorative or self-contained playback |
| CSS background/image | secure declarative animation may run | no | noninteractive decoration |

This skill defaults to self-contained SVG-native playback. Use HTML plus script only when seeking, input, or live simulation is an explicit requirement.

## Deterministic Contract

- Record pattern ID, family, techniques, seed, duration, loop flag, motion engine, and parameter hash on the root SVG.
- Use a named seeded PRNG. Never mix `random`, wall-clock time, browser frame count, or object iteration order into geometry.
- Use fixed numerical steps and stable update order for simulations.
- Quantize serialized coordinates consistently to avoid meaningless byte differences.
- Repeat the start state at the loop endpoint or declare a deliberate crossfade.
- Keep topology and stable IDs constant across keyframes.
- Give every repeating SMIL surface the declared master duration, use nonpositive phase offsets, and make every CSS animation period divide that duration exactly.
- When an effect cannot close naturally, serialize a forward-and-return trajectory instead of claiming a seamless loop.
- For `palindromic-snapshots`, serialize ordered solver states forward and then backward, repeat the first state at the endpoint, and keep snapshot membership unchanged across playback modes.
- Derive numerical snapshots from solver events or fixed steps. Let each pattern choose its semantic static frame from those states instead of assuming the midpoint or final frame.
- For multi-strata output, hash canonical solver state into `stateDigest`. Exclude viewport dimensions and presentation-only duration, palette, styling, and motion mode so those changes cannot alter the numerical identity.

Check both directions:

1. Same inputs produce the same bytes or normalized geometry hash.
2. A different seed changes seeded geometry while preserving counts, IDs, bounds, and accessibility metadata.

## Typed Configuration

Use `--config` for catalog patterns whose solver parameters must be explicit. Common build options remain separate from the pattern-specific `parameters` object:

```json
{
  "pattern": "procedural-svg-optimal-transport",
  "seed": 104729,
  "width": 960,
  "height": 600,
  "duration_ms": 8000,
  "palette": "colorset2",
  "motion": "full",
  "loop": true,
  "parameters": {"site_count": 10, "epsilon": 0.08, "minimum_iterations": 100, "frame_count": 7}
}
```

Run `build_procedural_svg.py --config request.json --output output.svg`. Reject unknown fields, missing pattern IDs, wrong primitive types, nonfinite numbers, and values outside the catalog range. A JSON boolean is not an integer. Record resolved defaults as well as overrides in `data-parameter-values`; include the catalog revision and resolved values in `data-parameter-hash`.

## Accessibility

- Place direct `<title>` and `<desc>` children in every standalone SVG.
- Use a meaningful base/final state so disabling animation never produces a blank artifact.
- Honor `prefers-reduced-motion`; keep the animated artwork in a motion layer and a separately rendered, ID-safe static state in a reduced-motion layer. Switch the layers with an in-SVG media query so direct, `<img>`, and CSS-background use do not depend on host-page JavaScript.
- Provide pause, play, and replay controls for continuous gallery motion longer than five seconds.
- Keep controls keyboard accessible and visibly focused.
- Do not animate tokens, filters, masks, or large marks across readable text.
- Avoid flashing. Do not alternate large bright regions at rapid rates.

## Performance Budget

- Prefer grouped transforms and shared `<symbol>/<use>` instances to per-node attribute animation.
- Combine noninteractive particles or segments into paths when individual semantics are not required.
- Precompute path samples, total lengths, simulation frames, and topology.
- Keep filter regions tight; reduce turbulence octaves, blur radius, and simultaneous filtered groups.
- Use paths or sampled keyframes for simulations instead of a permanent JavaScript loop.
- Validate at representative mobile dimensions. Dense moiré, quasicrystal, and filter patterns can alias or saturate before desktop layouts do.

Multi-strata entries also declare maximum serialized bytes, SVG elements, and motion elements. Check those limits after both full and reduced generation; do not remove evidence strata merely to meet a budget.

## Multi-strata Diagnostics

For a catalog entry with `strata` and `invariants`:

- Emit one semantic group for every declared `data-stratum`, in catalog order, and set the root `data-strata-count` to that exact count.
- Store canonical JSON diagnostics in a direct `<metadata>` child. Include pattern revision, resolved parameters, measured metrics, and an evaluation for every invariant.
- Hash the canonical diagnostic payload with SHA-256 into `data-diagnostics-hash`; set `data-invariants-status` to the exact passed/total ratio such as `5/5`, and accept release only when every declared comparison passes.
- Set `data-state-hash` to the solver `stateDigest`. Recompute it from the canonical variant, algorithm, seed, parameters, geometry, frames, selected static frame, and metrics; do not include viewport or presentation settings.
- Evaluate only the catalog operations `eq`, `lte`, and `gte`. Reject missing or nonfinite metrics and reject an SVG whose invariant ID, metric, operation, or threshold differs from the catalog.
- Rebuild each multi-strata renderer from the audited root seed, dimensions, palette, motion mode, and resolved parameters. Compare normalized subtree structure for every stratum in both motion layers; reject swapped, replaced, or stale drawing bodies even when diagnostics remain valid.
- Derive full-motion and reduced-motion layers from the same solver result. Full motion uses the event/step frames; reduced motion uses the solver-selected semantic static frame. Diagnostics and `stateDigest` must not change when playback is disabled.
- Preserve solver-native evidence: reconstruct the OT plan from serialized final `u/K/v`, validate its checkpoint residuals and constant frame masses, audit Fast Marching trial state from the live heap rather than neighboring cells, serialize and mark the Physarum inoculum root, and require fluid projection residuals to fall to at most 35% of their pre-projection values.

## Canonical Adversarial Test

Run:

```powershell
uv run --script skills/procedural-svg-animation/scripts/multistrata_core.py --self-test --json
uv run --script skills/procedural-svg-animation/scripts/test_multistrata_contracts.py
```

The solver self-test checks deterministic and viewport-independent state digests plus boundary cases. The adversarial test requires clean canonical Alpha, transport, and Fast Marching artifacts to pass and requires swapped strata, flattened snapshot schedules, swapped motion-layer roles, a changed Sinkhorn scaling bar, and changed live-trial geometry to fail. Treat a missed mutation as a release failure.

## Static Validation

Run:

```powershell
uv run --script skills/procedural-svg-animation/scripts/validate_procedural_svg.py artifact.svg --require-standalone --require-motion
```

The gate should confirm:

- parseable SVG XML and a stable `viewBox`;
- direct nonempty title and description;
- required root audit metadata;
- catalog revision and canonical resolved-parameter metadata;
- finite serialized numeric values;
- unique IDs and resolvable local references;
- no external URLs, scripts, remote fonts, or imports;
- at least one declared animation surface when motion is required;
- a reduced-motion/static layer pair with duplicate-free IDs and an in-SVG media query;
- a mechanically checkable loop contract: closed keyframes, master-duration SMIL, nonpositive phase offsets, indefinite repetition, and CSS periods that divide the master clock.
- for multi-strata patterns, exact ordered strata, canonical solver-render correspondence, viewport-independent solver digest, semantic static frame, canonical diagnostics/hash, passing invariant comparisons, and catalog byte/element/motion budgets.

## Browser Validation

Serve the containing folder over local HTTP and inspect the SVG directly plus its gallery card.

1. Capture the initial state.
2. Capture one intermediate state and confirm visible semantic change.
3. Capture the end/loop boundary and check for a jump.
4. Emulate reduced motion and confirm a nonblank readable frame.
5. Exercise pause, play, replay, search, filters, keyboard focus, and a direct `#pattern-id` link.
6. Repeat at desktop and mobile widths.
7. Fail console errors, page errors, missing resources, blank previews, clipped labels, and off-screen controls.

For `<object>` galleries, replay only the selected document. Use `pauseAnimations()`, `setCurrentTime(0)`, and `unpauseAnimations()` for SMIL when supported; reload only that object as a fallback. Never rebuild unrelated cards.

## Delivery Checklist

- Exact requested path exists.
- Generator report records the exact path and parameters.
- Validator report is clean.
- Same-seed and alternate-seed checks pass.
- Direct-open SVG works without network access.
- First, middle, final, and reduced-motion frames are meaningful.
- Loop and replay are deterministic.
- Desktop and mobile browser checks are clean.
