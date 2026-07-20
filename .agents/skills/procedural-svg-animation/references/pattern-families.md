# Procedural Pattern Families

Use this reference when choosing or extending a mechanism. From the task workspace root, query exact catalog metadata with `uv run --script skills/procedural-svg-animation/scripts/build_procedural_svg.py --list` or `--describe <id>`.

## Selection Matrix

| Family | Choose it when | Primary state | Best animation surfaces | Main risk |
| --- | --- | --- | --- | --- |
| Timing | Motion relationships matter more than geometry | phase, delay, state, response | CSS, SMIL, sampled keyframes | decorative motion without hierarchy |
| Transform | Parts move as frames, joints, gears, or layers | transform matrix or joint angle | `animateTransform`, CSS transforms | wrong pivot or inherited transform |
| Path | A route, outline, trace, or topology carries the story | path length, point, tangent, compatible `d` | dash offsets, `animateMotion`, path values | incompatible morph topology |
| Parametric | Equations should directly define the visible form | coefficient set and normalized parameter | generated paths plus transform/dash motion | aliasing or non-closing loops |
| Field | Many marks sample a continuous spatial function | scalar/vector value at `(x,y,t)` | precomputed paths, glyph transforms, filters | too many DOM nodes |
| Simulation | Local rules create emergent state | fixed-step state vector | precomputed frames/paths | nondeterminism and unstable integration |
| Growth | Order, recursion, or accumulation is meaningful | branch/attachment generation | staged path draw and mark reveal | dense late frames and hidden order |
| Tiling | A repeated cell or symmetry rule creates global form | tile coordinate, orientation, phase | `<symbol>/<use>`, pattern transforms, stagger | seams and accidental moiré overload |
| Paint | Geometry is stable but its reveal or surface changes | paint server, mask, clip, filter parameter | SMIL attributes and CSS | clipped filter regions or expensive blur |
| Composition | Several systems must share one causal clock | named phases and shared derived state | mixed SVG-native animation | unsynchronized independent loops |

## Family Catalog

### Timing systems

Use one clock and derive local timing rather than starting unrelated animations.

- `procedural-svg-stagger-wave`: spatial index to delay.
- `procedural-svg-phase-lattice`: continuous phase offsets.
- `procedural-svg-easing-orchestra`: transfer-curve comparison.
- `procedural-svg-state-sequencer`: state transitions plus dwell.
- `procedural-svg-loop-crossfade`: complementary loop envelopes.
- `procedural-svg-spring-chain`: sampled damped response.

### Transform mechanics

Put every pivot in an explicit group. Distinguish revolution, local rotation, and orientation compensation.

- `procedural-svg-orbit-nested`, `procedural-svg-counter-rotation`
- `procedural-svg-pendulum-cascade`, `procedural-svg-gear-train`
- `procedural-svg-kinematic-arm`, `procedural-svg-parallax-layers`

### Path choreography

Measure or sample the path once, then reuse that geometry for reveal, motion, tangent, labels, and masks.

- `procedural-svg-stroke-draw`, `procedural-svg-dash-conveyor`
- `procedural-svg-motion-follow`, `procedural-svg-path-morph`
- `procedural-svg-trim-window`, `procedural-svg-handwriting-reveal`

For morphs, normalize direction, start point, winding, command types, and control-point count. Prefer a crossfade or mask when the source shapes do not share semantics.

### Parametric geometry

Sample a closed interval consistently and record the coefficient set. Repeat the first sample at the endpoint for closed paths.

- `procedural-svg-lissajous-bloom`, `procedural-svg-rose-curve`
- `procedural-svg-spirograph`, `procedural-svg-fourier-epicycles`
- `procedural-svg-superformula`, `procedural-svg-wave-interference`

Increase sample count with curvature, not just canvas size. Keep equations in the pattern description or audit metadata.

### Fields and sampling

Separate field definition, seeding, numerical integration, and rendering. A field may drive arrows, lines, particles, contours, color, or masks without changing its identity.

- `procedural-svg-vector-field`, `procedural-svg-curl-streamlines`
- `procedural-svg-noise-ribbons`, `procedural-svg-particle-advection`
- `procedural-svg-distance-contours`, `procedural-svg-metaball-field`

Use fixed integration steps. Cap path length, detect boundary exits, and seed every streamline or particle deterministically.

### Simulation systems

Precompute deterministic states using a fixed step and explicit update order. Render selected states or trajectories into SVG-native playback.

- `procedural-svg-boid-flock`: separation, alignment, cohesion.
- `procedural-svg-verlet-cloth`: Verlet prediction plus constraint projection.
- `procedural-svg-spring-mesh`: damped mass-spring propagation.
- `procedural-svg-cellular-automaton`: discrete neighborhood updates.
- `procedural-svg-reaction-diffusion`: coupled field evolution.
- `procedural-svg-diffusion-limited`: random walks with seeded attachment.

Do not make frame rate part of the physics. Preserve stable particle IDs and use the same iteration order across platforms.

### Recursive growth

Store generation, depth, parent, and reveal order on every produced segment or mark.

- `procedural-svg-lsystem-canopy`, `procedural-svg-phyllotaxis-bloom`
- `procedural-svg-fractal-lightning`, `procedural-svg-space-colonization`
- `procedural-svg-vein-growth`, `procedural-svg-recursive-coral`

Show coarse structure before fine detail. Stop recursion by explicit depth, scale, or spatial threshold.

### Tiling and symmetry

Generate one canonical cell or sector and reuse it. Derive orientation and phase from coordinates plus the seed.

- `procedural-svg-truchet-flow`, `procedural-svg-hex-wave`
- `procedural-svg-voronoi-pulse`, `procedural-svg-moire-rotation`
- `procedural-svg-kaleidoscope`, `procedural-svg-quasicrystal`

Verify edges, pattern bounds, and mobile-scale aliasing. Dense interference patterns should not flash or overwhelm labels.

### Paint and compositing

Keep source geometry outside `<defs>` and reusable paint machinery inside it. Expand filter regions only as much as the effect needs.

- `procedural-svg-gradient-cycle`, `procedural-svg-mask-wipe`
- `procedural-svg-clip-morph`, `procedural-svg-turbulence-warp`
- `procedural-svg-gooey-merge`, `procedural-svg-lighting-sweep`

Maintain a sharp semantic layer when blur, displacement, thresholding, or lighting makes the effected layer hard to read.

### Hybrid compositions

Use named phases and one master duration. Each phase must alter a semantic object rather than add ambient motion.

- `procedural-svg-pulse-network`, `procedural-svg-growth-to-flow`
- `procedural-svg-field-glyph-morph`, `procedural-svg-orbit-trail-system`
- `procedural-svg-tiled-wavefront`, `procedural-svg-stateful-infographic`

## Extension Contract

When adding a pattern:

1. Choose one canonical family and a semantic `procedural-svg-<slug>` ID.
2. Declare the generator, time signal, animated channels, motion engine, final state, seed behavior, and loop invariant.
3. Reuse an existing renderer only when the visual mechanism remains distinct after parameters change.
4. Make the same seed byte-stable; make a different seed change generated geometry without breaking structure.
5. Add the pattern to the machine catalog, generator, gallery, reference routing, and validator inventory together.
