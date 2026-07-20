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

Check both directions:

1. Same inputs produce the same bytes or normalized geometry hash.
2. A different seed changes seeded geometry while preserving counts, IDs, bounds, and accessibility metadata.

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

## Static Validation

Run:

```powershell
uv run --script skills/procedural-svg-animation/scripts/validate_procedural_svg.py artifact.svg --require-standalone --require-motion
```

The gate should confirm:

- parseable SVG XML and a stable `viewBox`;
- direct nonempty title and description;
- required root audit metadata;
- finite serialized numeric values;
- unique IDs and resolvable local references;
- no external URLs, scripts, remote fonts, or imports;
- at least one declared animation surface when motion is required;
- a reduced-motion/static layer pair with duplicate-free IDs and an in-SVG media query;
- a mechanically checkable loop contract: closed keyframes, master-duration SMIL, nonpositive phase offsets, indefinite repetition, and CSS periods that divide the master clock.

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
