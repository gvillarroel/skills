# Composition Recipes

Read this when combining techniques. Give every composition one normalized clock `t ∈ [0,1]`, one seed, named phases, and a readable static state.

## Shared-Clock Contract

1. Compute immutable geometry and seeded initial state.
2. Derive all phase windows from the master duration.
3. Pass stable outputs between stages rather than recomputing them independently.
4. Keep the loop endpoint identical to the start when the composition repeats.
5. Gate expensive filters to the smallest group and time window that needs them.

## Repeatable Recipes

| Recipe | Pipeline | Useful for | Validate |
| --- | --- | --- | --- |
| Draw and follow | path generator → length cache → dash reveal → tangent follower → fading trail | routes, handwriting, signatures | follower never outruns reveal |
| Curl trail field | seeded curl field → streamline integration → particles → opacity-decay trail → clip | wind, currents, energy flow | fixed steps and bounded paths |
| Boid metaballs | boid simulation → particle positions → blurred circles → alpha threshold → sharp agent overlay | collective motion, organism-like blobs | agents remain identifiable |
| Automaton contour | cellular states → scalar density → contour/edge extraction → goo compositor | evolving territories, digital growth | discrete state and contour agree |
| Reaction sweep | reaction-diffusion frames → thresholds → contour bands → moving mask/light sweep | biological texture, phase change | no full-frame flashing |
| Growth to transport | recursive branches → reveal by depth → route reuse → motion tokens | networks that become operational | flow begins after its route exists |
| Attractor morph | attractor samples → equal-count resampling → compatible path → morph → afterimage | mathematical form transitions | winding and correspondence stable |
| Harmonic lattice | grid/radial layout → phase law → transform/color channels → mask | loading systems, waves, kinetic texture | phase derives from position |
| Tiled wavefront | tile adjacency → distance field → staggered cell state → edge flow | propagation over topology | adjacency, not DOM order, drives delay |
| Orbit and trace | nested frames → orbit markers → sampled trajectories → phase-decayed traces | astronomy, mechanism, recurrence | trace matches moving body |
| Field glyph morph | field sample → glyph orientation → compatible glyph states → opacity scale | direction and confidence fields | orientation and state share one sample |
| Semantic state scene | finite-state machine → masks → routes → annotations → reset | compact explainers | each transition has a named cause |

## Phase Patterns

- **Context → mechanism → consequence:** reveal stable context, run the procedural mechanism, then hold the meaningful result.
- **Structure → activation → circulation:** build geometry first, activate key nodes, then introduce persistent flow.
- **Sample → aggregate → resolve:** reveal individual samples, show their interaction, then settle into a stable summary.
- **Diffuse → focus → release:** begin with a field, focus attention through a mask/camera, then return to the complete state.
- **A/B bridge:** hold source state, interpolate only compatible channels, hold target state, then reverse or reset deliberately.

## Failure Modes

- Independent loops drift because they use different durations or clocks.
- A particle follows a route before the viewer can see the route.
- A path morph twists because point correspondence was inferred from index alone.
- A filter changes the apparent bounds and clips glow or displacement.
- A static reduced-motion state captures a transition midpoint instead of the semantic result.
- Too many channels change simultaneously, so no mechanism remains legible.
- A crossfade conceals a broken loop seam and is later reused where continuous geometry was expected.

Limit most compositions to one structural mechanism, one temporal mechanism, and one compositor. Add another stage only when it carries distinct meaning.
