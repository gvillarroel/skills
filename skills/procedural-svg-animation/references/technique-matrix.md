# Programmable SVG Technique Matrix

Use this inventory when exploring capabilities or designing a pattern that is not yet in the shipped catalog. Select one entry from each relevant axis; do not treat every combination as automatically useful.

## Geometry Generators

| Group | Programmable techniques |
| --- | --- |
| Native primitives | rect, rounded rect, circle, ellipse, line, polyline, polygon, symbol/use instances |
| Path construction | line/cubic/quadratic Bézier segments, arcs, Catmull-Rom or basis splines converted to paths, closed ribbons, offset strokes |
| Polar curves | spirals, rose curves, limacons, cardioids, superformula, polar waves, radial links |
| Harmonic curves | Lissajous, harmonograph, Fourier sums, epicycles, standing waves, signal interference |
| Rolling curves | hypotrochoids, epitrochoids, spirographs, cycloids, gear-derived loci |
| Implicit geometry | metaballs, signed-distance fields, threshold regions, marching-squares contours, iso-bands |
| Constructive geometry | boolean-like masks, clips, compound paths, stroke expansion approximations, repeated transforms |
| Projected geometry | scripted 3D-to-2D points, ribbons, wireframes, depth-sorted polygons, faux lighting |
| Text geometry | glyph outlines when available, text-on-path, per-tspan layout, procedural lettering traces, kinetic type grids |

## Population and Layout

| Group | Programmable techniques |
| --- | --- |
| Regular layouts | Cartesian, isometric, triangular, hexagonal, polar, concentric, spiral, modular grids |
| Deterministic sampling | uniform, stratified, jittered, Poisson-disc-like, low-discrepancy, weighted/rejection sampling |
| Mathematical packing | phyllotaxis, circle packing, Apollonian-like packing, recursive subdivision |
| Spatial partitions | Delaunay, Voronoi, nearest-site sampled cells, quadtrees, kd-like partitions |
| Topological complexes | Delaunay simplices, alpha complexes, filtrations, boundary chains, persistence barcodes |
| Hierarchies | trees, dendrograms, radial trees, treemaps, packs, recursive nesting |
| Networks | adjacency layouts, force-directed placement, route grids, edge bundling, port/lane routing |
| Tiling | Truchet, Wang-style edge rules, substitution tilings, Penrose-like systems, quasicrystal samples |
| Symmetry | cyclic, dihedral, reflection, glide, kaleidoscopic sectors, rotational copies |

## Randomness, Noise, and Fields

| Group | Programmable techniques |
| --- | --- |
| Seeded randomness | hash PRNG, shuffled indices, reproducible weighted choices, stable perturbation |
| Coherent noise | value noise, gradient/Perlin noise, simplex-like noise, fractal Brownian motion, ridged noise |
| Noise transforms | turbulence, domain warping, curl fields, octave mixing, anisotropic scaling, time slices through higher-dimensional noise |
| Vector fields | analytic rotation/saddle/source/sink fields, noise-derived direction, gradients, curl, combined attract/repel fields |
| Scalar fields | distance, density, potential, reaction concentration, occupancy, signed-distance combinations |
| Field renderers | arrows, glyphs, streamlines, particles, ribbons, contours, heat bands, masks, displacement maps |

## Dynamics and Generative Algorithms

| Group | Programmable techniques |
| --- | --- |
| Stateless motion | sine/cosine oscillation, triangle/sawtooth signals, modular phase, envelopes, beats |
| Mechanical systems | orbits, n-body approximations, pendulums, coupled oscillators, gears, articulated forward kinematics |
| Particle systems | emitters, lifetime envelopes, gravity, drag, attraction/repulsion, boundary wrapping, collision response |
| Behavioral agents | boid separation/alignment/cohesion, goal steering, obstacle avoidance, predator/prey rules |
| Constraint physics | springs, dampers, Verlet chains/cloth, rods, distance constraints, inverse-kinematic approximations |
| Cellular systems | Life-like rules, cyclic automata, elementary automata, Langton-style walkers, graph automata |
| Continuous fields | reaction-diffusion, wave equations, diffusion/decay, potential relaxation, coupled maps |
| Topological analysis | lower-star sweeps, union-find merge trees, critical events, Z2 reduction, Betti/Euler checks |
| Mass transport | entropic Sinkhorn scaling, Gibbs cost kernels, coupling marginals, barycentric interpolation |
| Front propagation | upwind Eikonal updates, heap-ordered Fast Marching, accepted/trial sets, arrival contours, gradient backtracing |
| Agent-field coupling | three-sensor steering, trail deposition, buffered diffusion/decay, transport networks |
| Incompressible flow | semi-Lagrangian advection, iterative diffusion, pressure projection, dye transport, sampled streamlines |
| Accretion and growth | DLA, random walks, Eden-like growth, space colonization, vein networks, recursive branching |
| Grammars and fractals | L-systems, iterated function systems, turtle graphics, midpoint displacement, recursive substitution |
| Optimization/evolution | Lloyd relaxation, iterative packing, hill-climbing layouts, genetic parameter search when explicitly bounded |

## Time Signals and Scheduling

| Group | Programmable techniques |
| --- | --- |
| Basic timing | delay, duration, repeat, repeat delay, direction, alternate/yoyo, fill, playback rate |
| Easing | linear, step, cubic Bézier, paced distance, sampled springs, overshoot, bounce, asymmetric envelopes |
| Sequencing | named phases, begin chains, event sync, stagger, overlap, hold/dwell, crossfade, state machines |
| Spatial timing | delay by index, row/column, radial distance, path length, graph distance, data value, random-but-seeded rank |
| Composition | additive transforms, accumulated cycles, nested clocks, master/subtimeline mapping, reversible phases |
| Input time | clock, seek/scrub, scroll progress, view progress, pointer distance, drag, keyboard/focus, data updates, audio/sensor samples |
| Deterministic capture | normalized `renderAt(t)`, fixed steps, timestamp sampling, exact start/middle/end frames, loop seam frames |

## Animated SVG Channels

| Surface | Programmable channels |
| --- | --- |
| Geometry | x/y, cx/cy, width/height, radius, points, path `d`, arc flags, viewBox |
| Transform | translate, rotate, scale, skew, matrix, transform origin/reference box, pattern/gradient transform |
| Stroke | width, dash array/offset, line cap/join, miter, markers, path length calibration |
| Paint | fill/stroke color, opacity, gradient stop color/opacity/offset, pattern phase, blend mode |
| Visibility/order | opacity, display/visibility states, clip/mask coverage, DOM/group layering, `<use>` instance state |
| Path attachment | motion path progress, auto-rotation/tangent, textPath start offset, marker positions |
| Filters | blur deviation, turbulence frequency/seed/octaves, displacement scale, morphology radius, color matrices, transfer functions, light position/color |
| Text | position, rotation, spacing, line offsets, per-span stagger, masks and outlines; avoid animating body copy continuously |
| Camera | viewBox, focus bounds, nested parallax, semantic zoom; provide reduced-motion substitution |

## Compositors and Surface Effects

- Alpha and luminance masks; geometric clip paths; animated reveal fronts.
- Gradient and pattern animation; nested pattern interference and conveyors.
- Duplicate sharp/blur layers for glow, neon traces, and readable filtered shapes.
- Blur plus alpha threshold for goo/metaballs; morphology for grow/shrink/outline.
- Turbulence plus displacement for liquid, smoke, paper, or organic warping.
- Color matrices and component transfer for hue, contrast, threshold, duotone, and channel remapping.
- Blend and composite operators for screen, multiply, masking, cutouts, and source-in/out effects.
- Diffuse/specular lighting driven by generated height fields.
- Trails through sampled path history, duplicated strokes, opacity envelopes, or precomputed afterimages.

## Runtime Drivers

| Driver | Strength | Constraint |
| --- | --- | --- |
| SVG animation elements | portable attribute, motion-path, and transform playback | support and seeking differ by context/API |
| CSS animations/transitions | cascade, media queries, reusable keyframes, transform/paint motion | arbitrary XML attributes and path morphs vary |
| Web Animations API | programmatic seek, pause, rate, promises, dynamic keyframes | requires script-capable embedding |
| `requestAnimationFrame` | arbitrary geometry, simulation, input, custom renderAt | requires script and careful timestamp/fixed-step design |
| Precomputed keyframes/paths | deterministic portable simulation playback | larger files and finite sampled resolution |
| D3 timers/transitions | data joins, interpolation, layout integration | extracted SVG must receive native playback rules |
| Animation libraries | morph, timeline, spring, draggable, and sequencing helpers | bundle/license/network constraints; use only when requested or vendored |

## Combination Grammar

Build a pattern as:

`geometry × layout × time signal × animated channel × compositor × input × driver`

Examples:

- Curve × path samples × paced time × dash/follower × glow × clock × SMIL.
- Curl field × seeded particles × fixed-step time × position/opacity × clip/trails × clock × precomputed paths.
- Cellular grid × sampled contours × stepped states × `d`/color × goo × seek input × inline SVG/WAAPI.
- Tiling × radial distance × wave phase × transform/fill × mask × reduced-motion-aware clock × CSS.
- Projected ribbon × depth order × camera phase × path/viewBox × lighting × scroll × scripted inline SVG.
- Solver substrate × typed state × invariant analysis × extracted geometry × palindromic snapshots × precomputed SMIL.

Reject a combination when the compositor hides semantics, the driver conflicts with the embedding mode, topology cannot remain stable, or reduced motion would remove the only meaningful state.
