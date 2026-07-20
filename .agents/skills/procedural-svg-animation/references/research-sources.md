# Research Sources

Use these sources when extending the catalog or choosing a browser/runtime contract. Prefer the specification or primary algorithm source over a secondary tutorial.

## SVG and Web Animation

- [SVG 2](https://svgwg.org/svg2-draft/): document structure, geometry, paths, painting, grouping, scripting, and dynamic SVG behavior.
- [SVG Animations](https://svgwg.org/specs/animations/): declarative animation model, timing, value interpolation, motion paths, transforms, additive behavior, and synchronization.
- [SVG Integration](https://svgwg.org/specs/integration/): processing modes and the restrictions that change when SVG is inline, an object, an image, or a CSS resource.
- [Web Animations Level 1](https://www.w3.org/TR/web-animations-1/): stateless timing, seeking, playback rate, effects, and the browser animation model.
- [CSS Animations Level 2](https://www.w3.org/TR/css-animations-2/): CSS keyframes, timelines, composition, and event behavior.
- [Scroll-driven Animations](https://www.w3.org/TR/scroll-animations-1/): scroll and view timelines for input-driven motion.
- [CSS Transforms Level 1](https://www.w3.org/TR/css-transforms-1/): transform matrices, reference boxes, and SVG transform behavior.
- [CSS Color Level 4](https://www.w3.org/TR/css-color-4/): perceptual color spaces and interpolation choices.
- [Filter Effects Level 1](https://www.w3.org/TR/filter-effects-1/): compositing order and filter primitives including turbulence, displacement, morphology, blur, transfer, and lighting.

## Programmatic Geometry and Dynamics

- [D3 shape generators](https://d3js.org/d3-shape): arcs, lines, areas, curves, links, symbols, and radial geometry.
- [D3 interpolation](https://d3js.org/d3-interpolate): numeric, color, transform, zoom, and general value interpolation.
- [D3 force simulation](https://d3js.org/d3-force/simulation): fixed-step force integration, explicit ticking, and seeded random sources.
- [D3 Delaunay and Voronoi](https://d3js.org/d3-delaunay/voronoi): spatial partitions and nearest-site structures.
- [D3 contours](https://d3js.org/d3-contour): marching-squares contour and density generation.
- [Flocks, Herds, and Schools](https://www.red3d.com/cwr/papers/1987/boids.html): Reynolds' original distributed behavioral model and the separation, alignment, and cohesion rules.
- [The Algorithmic Beauty of Plants](https://algorithmicbotany.org/papers/abop/abop.pdf): L-systems, turtle interpretation, branching, and procedural plant structures.
- [Lindenmayer Systems, Fractals, and Plants](https://algorithmicbotany.org/papers/lsfp.pdf): formal rewriting systems for generated growth.
- [Modeling Trees with a Space Colonization Algorithm](https://algorithmicbotany.org/papers/colonization.egwnp2007.html): nearest-node attractor assignment, influence and kill distances, and branching skeleton growth.
- [The Chemical Basis of Morphogenesis](https://www.dna.caltech.edu/courses/cs191/paperscs191/turing.pdf): the reaction-diffusion basis for self-organizing spatial patterns.
- [Complex Patterns in a Simple System](https://doi.org/10.1126/science.261.5118.189): numerical pattern regimes in the Gray–Scott reaction-diffusion model.
- [Diffusion-Limited Aggregation, a Kinetic Critical Phenomenon](https://doi.org/10.1103/PhysRevLett.47.1400): seeded random-walk attachment and fractal aggregate growth.
- [Advanced Character Physics](https://www.cs.cmu.edu/afs/cs/academic/class/15462-s13/www/lec_slides/Jakobsen.pdf): position-based Verlet integration, iterative distance-constraint projection, and particle-based cloth/rigid systems.
- [An Image Synthesizer](https://www.cs.drexel.edu/~david/Classes/Papers/p287-perlin.pdf): Perlin's original procedural noise work.
- [Implementing Improved Perlin Noise](https://developer.nvidia.com/gpugems/gpugems/part-i-natural-effects/chapter-5-implementing-improved-perlin-noise): deterministic improved-noise implementation choices.

## Multi-strata Topology and Transport

- [Alpha Shapes](https://www.clear.rice.edu/comp551/papers/Edelsbrunner-AlphaShapes.pdf): Delaunay-derived alpha complexes and scale-dependent boundaries.
- [Topological Persistence and Simplification](https://www.math.uchicago.edu/~shmuel/AAT-readings/Data%20Analysis/Edelsbrunner-Letscher-Zomordian.pdf): filtration order, persistence pairing, and homological lifetime.
- [Computing Contour Trees in All Dimensions](https://www.cs.ubc.ca/sites/default/files/tr/1999/TR-99-09_0.pdf): join/split-tree sweeps, critical-point connectivity, and contour-tree construction for scalar fields.
- [Sinkhorn Distances: Lightspeed Computation of Optimal Transport](https://papers.nips.cc/paper/4927-sinkhorn-distances-lightspeed-computation-of-optimal-transport.pdf): entropic regularization, diagonal matrix scaling, and marginal residuals.
- [A Fast Marching Level Set Method for Monotonically Advancing Fronts](https://doi.org/10.1073/pnas.93.4.1591): causal upwind Eikonal updates and smallest-trial acceptance.
- [Influences on the Formation and Evolution of Physarum polycephalum-inspired Emergent Transport Networks](https://ics-websites.science.uu.nl/docs/vakken/b2nb/stuff/Influences%20on%20the%20formation%20and%20evolution%20of%20Physarum%20Polycephalum%20inspired%20emergent%20transport%20networks%20-%20J.%20Jones%20-%202011.pdf): three-sensor particle steering coupled to deposited, diffused, and decayed trails.
- [Stable Fluids](https://graphics.stanford.edu/courses/cs448-01-spring/papers/stam.pdf): semi-Lagrangian advection, diffusion, and pressure projection for stable incompressible flow playback.

## Accessibility and Performance

- [WCAG Pause, Stop, Hide](https://www.w3.org/WAI/WCAG22/Understanding/pause-stop-hide): user control for automatically moving content lasting more than five seconds.
- [WCAG Animation from Interactions](https://www.w3.org/WAI/WCAG22/Understanding/animation-from-interactions): reducing nonessential motion triggered by interaction.
- [Reduced motion media feature](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/At-rules/%40media/prefers-reduced-motion): browser support and practical reduced-motion substitution.
- [Graphics ARIA](https://www.w3.org/TR/graphics-aria-1.0/): accessible roles and structure for graphical documents.
- [`requestAnimationFrame`](https://developer.mozilla.org/en-US/docs/Web/API/Window/requestAnimationFrame): display-synchronized callbacks and timestamp-based progression.

## Research Conclusions Applied Here

- Define the recipe independently of the driver; choose CSS, SMIL, WAAPI, or scripted updates from the embedding and interaction contract.
- Normalize path topology before morphing.
- Use fixed-step deterministic simulation and SVG-native playback for portable output.
- Treat filters as bounded compositing graphs, not cost-free vector operations.
- Make pause and reduced-motion behavior part of the pattern contract, not a gallery-only patch.
- Expose numerical strata and invariant residuals alongside solver imagery; a plausible rendering is not numerical validation.
- Use a palindromic playback sequence when a dissipative or monotone solver has no natural periodic orbit.
