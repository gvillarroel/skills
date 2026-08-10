---
name: procedural-svg-animation
description: "Generate, combine, animate, and validate deterministic standalone SVG systems from programmatic geometry, oscillators, paths, particles, fields, simulations, topology, transport, recursive growth, tilings, masks, gradients, and filter graphs. Use for procedural motion studies, generative SVG art, mathematical animation, multi-strata numerical solvers, seeded visual systems, technique exploration, seamless loops, or self-contained animated SVG/HTML where a chart, Mermaid diagram, or manually authored timeline is not the primary abstraction."
---

# Procedural SVG Animation

Build SVG as a reproducible system where visual state is a function of time, seed, and explicit parameters. Prefer a small composable mechanism over an isolated hand-authored animation.

## Core Workflow

1. Lock the output contract. Preserve every requested path, dimension, duration, ID, seed, palette, loop rule, and accessibility requirement exactly.
2. Choose the smallest sufficient pattern:
   - From the task workspace root, run `uv run --script skills/procedural-svg-animation/scripts/build_procedural_svg.py --list` to inspect the shipped catalog.
   - Run `uv run --script skills/procedural-svg-animation/scripts/build_procedural_svg.py --describe <procedural-svg-id>` before using an unfamiliar pattern.
   - Read `references/pattern-families.md` when selecting among technique families or designing a new variant.
   - Read `references/multi-strata-mastery.md` before changing a topology, transport, front-propagation, agent-field, or fluid solver.
   - Read `references/composition-recipes.md` when two or more mechanisms must share one clock or state model.
3. Make the system deterministic. Fix the seed, order all generated marks, avoid wall-clock randomness, and derive every delay or frame from stable indices, normalized time, or audited solver events.
4. Generate the exact artifact. For example:

```powershell
uv run --script skills/procedural-svg-animation/scripts/build_procedural_svg.py --pattern procedural-svg-curl-streamlines --output outputs/flow.svg --seed 104729 --width 960 --height 600 --duration-ms 8000 --palette colorset2
```

Run from the workspace root; do not change into the skill directory. Interpret every requested relative output path against the task workspace, create its parent directory when needed, and never redirect task artifacts into `skills/`.

For a catalog pattern with typed parameters, put the pattern, common options, and a `parameters` object in JSON and pass `--config request.json`. Query `--describe` for exact types, defaults, and bounds; do not guess parameter names.

5. Validate the artifact before styling around it:

```powershell
uv run --script skills/procedural-svg-animation/scripts/validate_procedural_svg.py outputs/flow.svg --require-motion --require-standalone --expected-pattern-id procedural-svg-curl-streamlines --expected-seed 104729
```

6. Open the SVG directly in a browser. Inspect the first state, an intermediate state, the loop boundary, the reduced-motion state, and the final readable composition. Read `references/runtime-and-validation.md` for embedding modes, replay, performance, and browser checks.

## Composition Model

Treat each result as a pipeline:

`geometry generator × population/layout × time signal × animated channel × compositor × input × driver`

- Keep geometry independent from time when possible; sample `t ∈ [0,1]` through one shared clock.
- Compose by passing stable outputs between stages: a field produces paths, paths carry particles, particles feed a mask, or a state machine gates all three.
- Repeat the first computed state at the loop endpoint. Do not hide a discontinuity with a fade unless crossfade is the intended recipe.
- Keep text and semantic labels outside moving, clipped, blurred, or displaced groups.
- Encode a complete readable base state in SVG attributes. Animation must enhance that state rather than create the only visible content.

## Output Rules

- Emit a stable `viewBox`, direct `<title>` and `<desc>`, semantic groups, finite coordinates, unique IDs, and self-contained paint/filter definitions.
- Preserve root audit metadata from the builder: pattern ID and revision, family, techniques, seed, duration, loop flag, motion engine, resolved parameters, and parameter hash.
- For multi-strata patterns, preserve ordered `data-stratum` groups, canonical solver-render correspondence, canonical diagnostics and hashes, the viewport-independent solver-state digest, and the all-invariants status. Preserve solver-native evidence such as Sinkhorn scaling checkpoints and constant plan masses, live heap trial state, a serialized visible network root, and pre/post projection residuals; never infer or cosmetically rewrite numerical state. Use event-derived animated states and the solver-selected semantic static state rather than an arbitrary frame.
- Prefer SVG-native CSS or SMIL for portable files. Do not add remote scripts, fonts, styles, images, or runtime imports.
- Use seeded precomputation for simulations. SVG is the playback surface, not a reason to run an unbounded physics loop in the browser.
- Honor `prefers-reduced-motion`; keep every mark visible and meaningful when motion is reduced.
- Provide pause/replay controls when continuous motion appears beside other content for more than five seconds.
- Avoid rapid flashing, large full-frame scale/pan loops, excessive filter regions, and thousands of independently animated DOM nodes.

## Routing

- Use `d3` when data binding, scales, projections, chart marks, or interactive quantitative exploration are the primary problem.
- Use `mermaid` when Mermaid source notation and diagram geometry must be preserved.
- Use `echarts-animated-svg` when animating existing ECharts SVG output.
- Use `compose-synchronized-svg` when many semantic modules must share canonical business or system state.
- Use this skill when the mechanism itself is procedural and can be expressed as `state = f(time, seed, parameters)`.

## Progressive Disclosure

- `references/pattern-families.md`: family selection, technique signatures, and extension rules.
- `references/multi-strata-mastery.md`: solver pipelines, typed parameters, numerical invariants, snapshot loops, and pitfalls for the six mastery patterns.
- `references/technique-matrix.md`: comprehensive programmable geometry, timing, channel, compositor, input, and driver capability matrix.
- `references/composition-recipes.md`: tested combinations, shared-clock contracts, and failure modes.
- `references/runtime-and-validation.md`: portability, embedding, replay, accessibility, performance, deterministic QA, and browser checks.
- `references/research-sources.md`: authoritative specifications, API documentation, and primary algorithm sources behind the catalog.
- `assets/pattern-specs.json`: machine-readable catalog used by the builder; query it through `--list` or `--describe` instead of loading the whole file when one pattern is enough.

## Maintenance

Keep gallery fixtures under `assets/examples/procedural-svg-animation/`; normal runtime work must not read them. When adding a reusable mechanism, update the catalog, generator, compact family guidance, gallery, tests, and canonical ID inventory together. Validate exact paths, deterministic hashes, alternate seeds, standalone SVG behavior, reduced motion, desktop/mobile layout, isolated skill use, and the canonical multi-strata adversarial test before marking the skill done.
