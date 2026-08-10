(function attachD3LogoDesign(root) {
  "use strict";

  const VIEW_BOX = "0 0 480 320";
  const SVG_NS = "http://www.w3.org/2000/svg";

  function deepFreeze(value) {
    if (value && typeof value === "object" && !Object.isFrozen(value)) {
      Object.freeze(value);
      Object.keys(value).forEach((key) => deepFreeze(value[key]));
    }
    return value;
  }

  const PATTERNS = deepFreeze([
    { id: "d3-logo-type-orbit", label: "Type Orbit", family: "typographic", geometrySignature: "textpath-circle", intentionalOmissions: [{ textRole: "tagline", when: "small-size", reason: "The compact 96 px lockup omits the tagline to preserve legibility." }] },
    { id: "d3-logo-bezier-wordpath", label: "Bezier Wordpath", family: "typographic", geometrySignature: "textpath-cubic" },
    { id: "d3-logo-variable-axis-wordmark", label: "Variable Axis Wordmark", family: "typographic", geometrySignature: "per-glyph-axis" },
    { id: "d3-logo-ligature-bridge", label: "Ligature Bridge", family: "typographic", geometrySignature: "initial-connector", intentionalOcclusions: [{ textRole: "initials", occluderRole: "ligature-connector", reason: "The connector intentionally crosses the joined initials.", maxOcclusionRatio: 0.22 }, { textRole: "initials", occluderRole: "ligature-anchor", reason: "The small connector terminals intentionally touch the joined initials at their attachment points.", maxOcclusionRatio: 0.03 }] },
    { id: "d3-logo-stencil-cuts", label: "Stencil Cuts", family: "typographic", geometrySignature: "masked-stencil-cuts" },
    { id: "d3-logo-letter-window", label: "Letter Window", family: "typographic", geometrySignature: "text-clip-window" },
    { id: "d3-logo-mirrored-monogram", label: "Mirrored Monogram", family: "typographic", geometrySignature: "mirror-transform-axis", intentionalOcclusions: [{ textRole: "initials", occluderRole: "mirror-joint", reason: "The small center joint intentionally pins the mirrored initials at their shared axis.", maxOcclusionRatio: 0.05 }] },
    { id: "d3-logo-glyph-rosette", label: "Glyph Rosette", family: "typographic", geometrySignature: "radial-glyph-repeat" },
    { id: "d3-logo-baseline-wave", label: "Baseline Wave", family: "typographic", geometrySignature: "per-letter-wave" },
    { id: "d3-logo-stack-offset", label: "Stack Offset", family: "typographic", geometrySignature: "offset-copy-stack" },
    { id: "d3-logo-slice-shift", label: "Slice Shift", family: "typographic", geometrySignature: "clip-slice-shift" },
    { id: "d3-logo-multi-stroke-wordmark", label: "Multi-stroke Wordmark", family: "typographic", geometrySignature: "multi-stroke-use" },
    { id: "d3-logo-extruded-wordmark", label: "Extruded Wordmark", family: "typographic", geometrySignature: "translated-depth-stack" },
    { id: "d3-logo-letter-weave", label: "Letter Weave", family: "typographic", geometrySignature: "crossing-mask-weave" },
    { id: "d3-logo-responsive-lockup", label: "Responsive Lockup", family: "typographic", geometrySignature: "responsive-lockup-states" },
    { id: "d3-logo-spiral-trace", label: "Spiral Trace", family: "generative", geometrySignature: "polar-radius-trace" },
    { id: "d3-logo-orbit-network", label: "Orbit Network", family: "generative", geometrySignature: "orbit-link-network" },
    { id: "d3-logo-grid-activation", label: "Grid Activation", family: "generative", geometrySignature: "modular-cell-activation" },
    { id: "d3-logo-contour-fingerprint", label: "Contour Fingerprint", family: "generative", geometrySignature: "scalar-field-contours" },
    { id: "d3-logo-voronoi-shards", label: "Voronoi Shards", family: "generative", geometrySignature: "voronoi-clipped-shards" },
    { id: "d3-logo-animal-facets", label: "Animal Facets", family: "generative", geometrySignature: "delaunay-animal-facets" },
    { id: "d3-logo-animal-surface-mask", label: "Animal Surface Mask", family: "generative", geometrySignature: "animal-surface-mask" },
    { id: "d3-logo-negative-space-reveal", label: "Negative Space Reveal", family: "generative", geometrySignature: "subtractive-negative-space" },
    { id: "d3-logo-folded-ribbon", label: "Folded Ribbon", family: "generative", geometrySignature: "folded-wide-ribbon" },
    { id: "d3-logo-boolean-lens", label: "Boolean Lens", family: "generative", geometrySignature: "overlap-intersection-lens" },
    { id: "d3-logo-radiant-pulse", label: "Radiant Pulse", family: "generative", geometrySignature: "variable-radial-rays" },
    { id: "d3-logo-parametric-wave", label: "Parametric Wave", family: "generative", geometrySignature: "closed-harmonic-curve" },
    { id: "d3-logo-kaleidoscope-wedges", label: "Kaleidoscope Wedges", family: "generative", geometrySignature: "mirrored-radial-wedges" },
    { id: "d3-logo-polar-halo", label: "Polar Halo", family: "generative", geometrySignature: "data-driven-polar-arcs" },
    { id: "d3-logo-aperture-iris", label: "Aperture Iris", family: "generative", geometrySignature: "overlapping-iris-blades" },
    { id: "d3-logo-terminal-extension", label: "Terminal Extension", family: "typographic", geometrySignature: "glyph-terminal-rule-extension" },
    { id: "d3-logo-vertical-rail-wordmark", label: "Vertical Rail Wordmark", family: "typographic", geometrySignature: "stacked-glyph-reading-rail" },
    { id: "d3-logo-hinged-glyph-fan", label: "Hinged Glyph Fan", family: "typographic", geometrySignature: "baseline-pivot-rotation" },
    { id: "d3-logo-justified-word-block", label: "Justified Word Block", family: "typographic", geometrySignature: "measured-multiline-justification" },
    { id: "d3-logo-fill-outline-cadence", label: "Fill Outline Cadence", family: "typographic", geometrySignature: "per-glyph-fill-outline-alternation" },
    { id: "d3-logo-punctuation-armature", label: "Punctuation Armature", family: "typographic", geometrySignature: "bbox-punctuation-frame" },
    { id: "d3-logo-circle-pack-cluster", label: "Circle Pack Cluster", family: "generative", geometrySignature: "hierarchical-circle-enclosure" },
    { id: "d3-logo-treemap-mosaic", label: "Treemap Mosaic", family: "generative", geometrySignature: "hierarchical-rect-subdivision" },
    { id: "d3-logo-convex-hull-shells", label: "Convex Hull Shells", family: "generative", geometrySignature: "iterative-point-hulls" },
    { id: "d3-logo-phyllotaxis-bloom", label: "Phyllotaxis Bloom", family: "generative", geometrySignature: "golden-angle-disc-sequence" },
    { id: "d3-logo-tangency-chain", label: "Tangency Chain", family: "generative", geometrySignature: "mutually-tangent-circle-chain" },
    { id: "d3-logo-tangram-dissection", label: "Tangram Dissection", family: "generative", geometrySignature: "rule-based-polygon-dissection" },
    { id: "d3-logo-superellipse-family", label: "Superellipse Family", family: "generative", geometrySignature: "superellipse-exponent-nesting" },
    { id: "d3-logo-isometric-block-stack", label: "Isometric Block Stack", family: "generative", geometrySignature: "axonometric-cube-aggregation" },
    { id: "d3-logo-eulerian-one-stroke", label: "Eulerian One Stroke", family: "generative", geometrySignature: "euler-circuit-graph-trace" },
    { id: "d3-logo-perfect-maze", label: "Perfect Maze", family: "generative", geometrySignature: "spanning-tree-corridors" },
    { id: "d3-logo-split-merge-stream", label: "Split Merge Stream", family: "generative", geometrySignature: "conserved-multistream-routing" },
    { id: "d3-logo-dendrogram-crown", label: "Dendrogram Crown", family: "generative", geometrySignature: "hierarchy-cluster-branches" },
    { id: "d3-logo-linked-ring-chain", label: "Linked Ring Chain", family: "generative", geometrySignature: "interlocking-component-cycles" },
    { id: "d3-logo-lsystem-branch", label: "L-system Branch", family: "generative", geometrySignature: "grammar-turtle-branching" },
    { id: "d3-logo-hilbert-route", label: "Hilbert Route", family: "generative", geometrySignature: "space-filling-continuous-path" },
    { id: "d3-logo-reciprocal-profiles", label: "Reciprocal Profiles", family: "generative", geometrySignature: "paired-silhouette-shared-boundary" },
    { id: "d3-logo-modular-gutter-symbol", label: "Modular Gutter Symbol", family: "generative", geometrySignature: "gap-defined-modular-symbol" },
    { id: "d3-logo-tangent-void-star", label: "Tangent Void Star", family: "generative", geometrySignature: "tangent-primitives-central-void" },
    { id: "d3-logo-reciprocal-tessellation", label: "Reciprocal Tessellation", family: "generative", geometrySignature: "dual-figure-ground-tiling" },
    { id: "d3-logo-impossible-triangle", label: "Impossible Triangle", family: "generative", geometrySignature: "cyclic-occlusion-beams" },
    { id: "d3-logo-necker-cube", label: "Necker Cube", family: "generative", geometrySignature: "bistable-wireframe-depth" },
    { id: "d3-logo-kanizsa-closure", label: "Kanizsa Closure", family: "generative", geometrySignature: "inducer-based-illusory-contour" },
    { id: "d3-logo-line-screen-silhouette", label: "Line Screen Silhouette", family: "generative", geometrySignature: "variable-line-segmentation-encoding" },
    { id: "d3-logo-perspective-portal", label: "Perspective Portal", family: "generative", geometrySignature: "receding-quadrilateral-frame" },
    { id: "d3-logo-reuleaux-body", label: "Reuleaux Body", family: "mathematical", geometrySignature: "equilateral-vertex-constant-width-arcs" },
    { id: "d3-logo-cassini-oval", label: "Cassini Oval", family: "mathematical", geometrySignature: "fixed-foci-distance-product-locus" },
    { id: "d3-logo-polar-reciprocal", label: "Polar Reciprocal", family: "mathematical", geometrySignature: "convex-polygon-polar-duality" },
    { id: "d3-logo-minkowski-sum", label: "Minkowski Sum", family: "mathematical", geometrySignature: "convex-set-vector-addition-boundary" },
    { id: "d3-logo-pedal-curve", label: "Pedal Curve", family: "mathematical", geometrySignature: "tangent-perpendicular-foot-locus" },
    { id: "d3-logo-involute-gear", label: "Involute Gear", family: "mathematical", geometrySignature: "base-circle-unwound-string-flanks" },
    { id: "d3-logo-desargues-incidence", label: "Desargues Incidence", family: "mathematical", geometrySignature: "perspective-triangles-collinear-axis" },
    { id: "d3-logo-circle-inversion", label: "Circle Inversion", family: "mathematical", geometrySignature: "reciprocal-radius-circle-line-transform" },
    { id: "d3-logo-catenary-funicular", label: "Catenary Funicular", family: "mathematical", geometrySignature: "uniform-load-hyperbolic-cable" },
    { id: "d3-logo-joukowski-airfoil", label: "Joukowski Airfoil", family: "mathematical", geometrySignature: "complex-circle-joukowski-map" },
    { id: "d3-logo-hyperbolic-geodesics", label: "Hyperbolic Geodesics", family: "mathematical", geometrySignature: "poincare-boundary-orthogonal-arcs" },
    { id: "d3-logo-elliptic-group-law", label: "Elliptic Group Law", family: "mathematical", geometrySignature: "cubic-chord-tangent-addition" },
    { id: "d3-logo-mobius-strip", label: "Mobius Strip", family: "mathematical", geometrySignature: "half-twist-nonorientable-band" },
    { id: "d3-logo-torus-knot", label: "Torus Knot", family: "mathematical", geometrySignature: "coprime-toroidal-winding-curve" },
    { id: "d3-logo-ruled-hyperboloid", label: "Ruled Hyperboloid", family: "mathematical", geometrySignature: "doubly-ruled-quadric-line-family" },
    { id: "d3-logo-tensegrity-prism", label: "Tensegrity Prism", family: "mathematical", geometrySignature: "prestressed-strut-cable-equilibrium" },
    { id: "d3-logo-maxwell-reciprocal", label: "Maxwell Reciprocal", family: "mathematical", geometrySignature: "form-force-reciprocal-diagrams" },
    { id: "d3-logo-medial-axis", label: "Medial Axis", family: "mathematical", geometrySignature: "maximal-inscribed-disc-center-locus" },
    { id: "d3-logo-string-parabola", label: "String Parabola", family: "mathematical", geometrySignature: "indexed-segment-parabolic-envelope" },
    { id: "d3-logo-circle-caustic", label: "Circle Caustic", family: "mathematical", geometrySignature: "specular-reflection-nephroid-envelope" },
    { id: "d3-logo-moire-beat", label: "Moire Beat", family: "mathematical", geometrySignature: "phase-offset-frequency-interference" },
    { id: "d3-logo-peaucellier-linkage", label: "Peaucellier Linkage", family: "mathematical", geometrySignature: "exact-straight-line-inversor-linkage" },
    { id: "d3-logo-lorenz-attractor", label: "Lorenz Attractor", family: "mathematical", geometrySignature: "nonlinear-ode-chaotic-trajectory" },
    { id: "d3-logo-affine-ifs", label: "Affine IFS", family: "mathematical", geometrySignature: "contractive-affine-iteration-invariant" },
    { id: "d3-logo-cellular-automaton", label: "Cellular Automaton", family: "mathematical", geometrySignature: "boolean-neighborhood-time-evolution" },
    { id: "d3-logo-logistic-bifurcation", label: "Logistic Bifurcation", family: "mathematical", geometrySignature: "parameter-swept-period-doubling" },
    { id: "d3-logo-field-streamlines", label: "Field Streamlines", family: "mathematical", geometrySignature: "numerically-integrated-vector-field" },
    { id: "d3-logo-newton-basin", label: "Newton Basin", family: "mathematical", geometrySignature: "complex-newton-root-basin" },
    { id: "d3-logo-steiner-tree", label: "Steiner Tree", family: "mathematical", geometrySignature: "length-minimizing-120-degree-network" },
    { id: "d3-logo-penrose-substitution", label: "Penrose Substitution", family: "mathematical", geometrySignature: "aperiodic-rhomb-substitution" }
  ]);

  const TEXTURES = deepFreeze([
    {"id":"d3-logo-micro-grid","label":"Micro Grid","family":"geometric","geometrySignature":"orthogonal-tile-grid","description":"A tiled square grid with optional subdivisions for restrained technical structure.","parameters":["tileSize","subdivision","lineWidth","angle"],"avoidWhen":"Avoid when the primary mark already uses a dense cell grid."},
    {"id":"d3-logo-diagonal-hatch","label":"Diagonal Hatch","family":"linework","geometrySignature":"single-angle-hatch","description":"One evenly spaced diagonal stroke family for economical print-like shading.","parameters":["pitch","angle","dashRhythm","lineWidth"],"avoidWhen":"Avoid when narrow glyph counters could collapse."},
    {"id":"d3-logo-crosshatch","label":"Crosshatch","family":"linework","geometrySignature":"dual-angle-hatch","description":"Two opposing stroke families that create a compact engraved field.","parameters":["primaryAngle","secondaryAngle","pitch","lineWidth"],"avoidWhen":"Avoid when the symbol already contains many intersections."},
    {"id":"d3-logo-halftone-dots","label":"Halftone Dots","family":"print","geometrySignature":"modulated-dot-tile","description":"A regular dot screen with deterministic radius modulation for printed tonal rhythm.","parameters":["cellSize","radiusMin","radiusMax","screenAngle"],"avoidWhen":"Avoid when the smallest output is below 128 pixels wide."},
    {"id":"d3-logo-seeded-stipple","label":"Seeded Stipple","family":"print","geometrySignature":"seeded-point-tile","description":"A repeatable seeded point field that adds tactile grain without external imagery.","parameters":["density","radiusMin","radiusMax","minimumDistance","seed"],"avoidWhen":"Avoid when the silhouette depends on tiny negative spaces."},
    {"id":"d3-logo-topographic-lines","label":"Topographic Lines","family":"linework","geometrySignature":"contour-line-tile","description":"Procedural contour-like paths that suggest terrain and layered surfaces.","parameters":["thresholdCount","spacing","smoothing","seed"],"avoidWhen":"Avoid when the primary pattern is already a contour fingerprint."},
    {"id":"d3-logo-voronoi-mosaic","label":"Voronoi Mosaic","family":"geometric","geometrySignature":"cell-fragment-tile","description":"A seeded space-filling cell field with discrete palette assignment.","parameters":["siteCount","cellGap","seed","roleSequence"],"avoidWhen":"Avoid when the primary pattern already uses Voronoi shards."},
    {"id":"d3-logo-guilloche-waves","label":"Guilloche Waves","family":"ornamental","geometrySignature":"phase-wave-tile","description":"Phase-shifted harmonic lines for currency-like ornamental detail.","parameters":["frequency","amplitude","phaseStep","lineCount"],"avoidWhen":"Avoid when the primary pattern already uses a wave baseline."},
    {"id":"d3-logo-woven-checker","label":"Woven Checker","family":"textile","geometrySignature":"alternating-band-tile","description":"Orthogonal bands with an alternating over-under crossing schedule.","parameters":["tileSize","bandWidth","crossingSchedule","rotation"],"avoidWhen":"Avoid when the primary mark already uses a letter weave."},
    {"id":"d3-logo-directional-fibers","label":"Directional Fibers","family":"organic","geometrySignature":"seeded-fiber-tile","description":"Short parallel strokes with seeded displacement for directional material grain.","parameters":["spacing","direction","displacement","length","seed"],"avoidWhen":"Avoid when a crisp institutional seal is required."},
    {"id":"d3-logo-hex-cell-lattice","label":"Hex Cell Lattice","family":"geometric","geometrySignature":"regular-hexagon-edge-lattice","description":"A staggered field of regular hexagon outlines for modular scientific identities.","parameters":["cellRadius","gap","lineWidth","rowOffset","rotation"],"avoidWhen":"Avoid when the mark already relies on honeycomb or hexagonal geometry."},
    {"id":"d3-logo-triangle-flip-tiles","label":"Triangle Flip Tiles","family":"geometric","geometrySignature":"alternating-equilateral-triangle-facets","description":"Equilateral triangle facets whose fills alternate by orientation and grid parity.","parameters":["edgeLength","gap","fillCadence","rotation","sequenceOffset"],"avoidWhen":"Avoid when small counters cannot preserve the triangular facet rhythm."},
    {"id":"d3-logo-truchet-arc-links","label":"Truchet Arc Links","family":"geometric","geometrySignature":"seeded-quarter-circle-tile-connectivity","description":"Seeded quarter-circle tiles that join into deterministic flowing routes.","parameters":["tileSize","arcRadius","lineWidth","seed","rotation"],"avoidWhen":"Avoid when the primary symbol already contains routed arc networks."},
    {"id":"d3-logo-houndstooth-blocks","label":"Houndstooth Blocks","family":"textile","geometrySignature":"offset-notched-houndstooth-polygons","description":"Offset notched polygons that form a bold houndstooth textile repeat.","parameters":["moduleSize","toothDepth","rowOffset","gap","rotation"],"avoidWhen":"Avoid when a quiet or minimal luxury treatment is required."},
    {"id":"d3-logo-argyle-diamonds","label":"Argyle Diamonds","family":"textile","geometrySignature":"staggered-diamond-fields-with-seam-threads","description":"Staggered filled diamonds crossed by sparse seam threads.","parameters":["diamondWidth","diamondHeight","rowShift","seamWidth","sequenceCadence"],"avoidWhen":"Avoid when the logo already contains dominant diamond geometry."},
    {"id":"d3-logo-running-brick-bond","label":"Running Brick Bond","family":"geometric","geometrySignature":"half-offset-masonry-rectangle-bond","description":"Rectangular modules arranged in half-offset masonry rows.","parameters":["brickRatio","rowHeight","mortarGap","rowPhase","rotation"],"avoidWhen":"Avoid when rigid masonry cues conflict with the brand personality."},
    {"id":"d3-logo-isometric-cube-tiles","label":"Isometric Cube Tiles","family":"geometric","geometrySignature":"three-rhombus-axonometric-cube-repeat","description":"Three rhombus faces repeat as compact axonometric cube units.","parameters":["moduleSize","skewAngle","faceGap","cubeSpacing","rotation"],"avoidWhen":"Avoid when the primary mark already uses an isometric block stack."},
    {"id":"d3-logo-greek-key-meander","label":"Greek Key Meander","family":"ornamental","geometrySignature":"continuous-orthogonal-fret-meander","description":"A continuous orthogonal fret path that forms a seamless border-like field.","parameters":["stepSize","inset","lineWidth","turnPeriod","rotation"],"avoidWhen":"Avoid when the available fill area is too narrow to show complete turns."},
    {"id":"d3-logo-chainmail-rings","label":"Chainmail Rings","family":"textile","geometrySignature":"interleaved-over-under-ring-arc-lattice","description":"Split ring arcs alternate front and back to create linked metallic rhythm.","parameters":["ringRadius","linkSpacing","lineWidth","overlapPhase","rotation"],"avoidWhen":"Avoid when ring crossings would compete with thin lettering."},
    {"id":"d3-logo-seigaiha-fans","label":"Seigaiha Fans","family":"ornamental","geometrySignature":"staggered-nested-semicircle-fan-motifs","description":"Discrete staggered fans built from nested semicircular arcs.","parameters":["fanRadius","ringCount","rowOverlap","lineWidth","phase"],"avoidWhen":"Avoid when the concept should not suggest water, waves, or heritage ornament."},
    {"id":"d3-logo-knit-v-loops","label":"Knit V Loops","family":"textile","geometrySignature":"interlocking-curved-v-stitch-loops","description":"Curved V-shaped stitches interlock in staggered knitted rows.","parameters":["loopWidth","loopHeight","tension","stitchPitch","lineWidth"],"avoidWhen":"Avoid when textile or hand-crafted cues are inappropriate."},
    {"id":"d3-logo-pinwheel-quilt","label":"Pinwheel Quilt","family":"textile","geometrySignature":"fourfold-rotated-triangle-pinwheel-block","description":"Four rotated triangle patches form a repeating pinwheel block.","parameters":["blockSize","centerOffset","triangleGap","rotation","colorCadence"],"avoidWhen":"Avoid when multiple palette faces would make the mark visually busy."},
    {"id":"d3-logo-star-kite-lattice","label":"Star Kite Lattice","family":"ornamental","geometrySignature":"eight-point-star-and-kite-tiling","description":"Eight-point stars and surrounding kite polygons form a precise ornamental lattice.","parameters":["starRadius","kiteLength","gap","lineWidth","rotation"],"avoidWhen":"Avoid when the silhouette is too small to preserve star points."},
    {"id":"d3-logo-chevron-bands","label":"Chevron Bands","family":"geometric","geometrySignature":"filled-zigzag-ribbon-cadence","description":"Closed filled zigzag ribbons create a strong directional cadence.","parameters":["pitch","bandThickness","pointDepth","spacing","rotation"],"avoidWhen":"Avoid when the primary mark already has aggressive directional motion."},
    {"id":"d3-logo-pixel-staircase","label":"Pixel Staircase","family":"digital","geometrySignature":"quantized-diagonal-stair-band-repeat","description":"Integer-aligned rectangles form diagonal stepped bands with a digital character.","parameters":["cellSize","run","rise","bandWidth","phase","rotation"],"avoidWhen":"Avoid when the desired identity should feel organic or handcrafted."},
    {"id":"d3-logo-terrazzo-chips","label":"Terrazzo Chips","family":"material","geometrySignature":"seeded-independent-angular-chip-scatter","description":"Independent seeded polygon chips float over a flat substrate without sharing boundaries.","parameters":["chipCount","sizeRange","elongation","minimumGap","seed"],"avoidWhen":"Avoid when the primary form already uses fragmented polygon facets."},
    {"id":"d3-logo-linocut-gouges","label":"Linocut Gouges","family":"print","geometrySignature":"seeded-tapered-negative-gouge-cuts","description":"Tapered curved negative cuts emulate hand-carved linocut marks.","parameters":["gougeCount","length","taper","curvature","direction","seed"],"avoidWhen":"Avoid when pristine geometric precision is central to the identity."},
    {"id":"d3-logo-letterpress-slippage","label":"Letterpress Slippage","family":"print","geometrySignature":"dual-offset-stamp-registration-impressions","description":"A repeated stamp receives a controlled second impression with visible registration offset.","parameters":["stampMotif","offsetX","offsetY","impressionSize","repeatPitch","rotation"],"avoidWhen":"Avoid when any registration error would undermine a precision-focused brand."},
    {"id":"d3-logo-dry-roller-bands","label":"Dry Roller Bands","family":"print","geometrySignature":"seeded-broken-coverage-broad-bands","description":"Broad bands break into deterministic ink runs and substrate gaps.","parameters":["bandHeight","coverageRatio","breakCount","direction","seed"],"avoidWhen":"Avoid when distressed print texture would weaken small-size recognition."},
    {"id":"d3-logo-embossed-lozenges","label":"Embossed Lozenges","family":"material","geometrySignature":"paired-offset-lozenge-relief-faces","description":"Paired light and dark offset faces imply lozenge relief without gradients.","parameters":["lozengeSize","bevelDepth","gap","lightDirection","rotation"],"avoidWhen":"Avoid when flat one-color reproduction is the primary delivery mode."},
    {"id":"d3-logo-camouflage-islands","label":"Camouflage Islands","family":"organic","geometrySignature":"seeded-union-of-organic-closed-islands","description":"Seeded closed blobs overlap into a repeatable organic island field.","parameters":["islandCount","lobeCount","radiusRange","overlap","seed","rotation"],"avoidWhen":"Avoid when camouflage, outdoor, or tactical associations are undesirable."},
    {"id":"d3-logo-leaf-vein-repeat","label":"Leaf Vein Repeat","family":"organic","geometrySignature":"mirrored-secondary-veins-on-leaf-midrib","description":"Repeated leaf silhouettes carry a midrib and mirrored secondary veins.","parameters":["leafSize","veinCount","veinSlant","rowOffset","lineWidth","rotation"],"avoidWhen":"Avoid when botanical or sustainability cues would be misleading."},
    {"id":"d3-logo-pinecone-scales","label":"Pinecone Scales","family":"organic","geometrySignature":"staggered-pointed-lens-scale-overlap","description":"Pointed lens-shaped scales overlap in staggered natural rows.","parameters":["scaleWidth","scaleHeight","overlap","rowOffset","gap","rotation"],"avoidWhen":"Avoid when the mark already uses feather, scale, or petal geometry."},
    {"id":"d3-logo-coral-branchlets","label":"Coral Branchlets","family":"organic","geometrySignature":"recursive-forked-microbranch-colonies","description":"Bounded recursive forks form connected microbranch colonies.","parameters":["recursionDepth","branchRatio","forkAngle","stemWidth","seed"],"avoidWhen":"Avoid when thin branches cannot survive the smallest required reproduction."},
    {"id":"d3-logo-circuit-traces","label":"Circuit Traces","family":"technical","geometrySignature":"seeded-orthogonal-routing-with-terminal-pads","description":"Seeded Manhattan routes connect compact terminal pads across a coarse lattice.","parameters":["gridStep","traceCount","bendCount","lineWidth","padRadius","seed"],"avoidWhen":"Avoid when technology or electronics associations do not support the brief."},
    {"id":"d3-logo-barcode-cadence","label":"Barcode Cadence","family":"encoded","geometrySignature":"hash-derived-variable-width-bar-sequence","description":"A brand hash generates a repeatable sequence of variable-width vertical bars.","parameters":["sourceText","moduleWidth","barHeight","quietZone","checksumLength","rotation"],"avoidWhen":"Avoid when barcode or retail associations would distract from the brand."},
    {"id":"d3-logo-microtype-ribbons","label":"Microtype Ribbons","family":"typographic","geometrySignature":"repeated-brand-microtype-row-ribbons","description":"The supplied brand or tagline repeats in offset microtype rows behind the primary wordmark.","parameters":["sourceText","fontStack","fontSize","tracking","rowPitch","angle"],"avoidWhen":"Avoid when the texture copy cannot remain secondary to the primary wordmark."},
    {"id":"d3-logo-morse-stripes","label":"Morse Stripes","family":"encoded","geometrySignature":"hash-encoded-dot-dash-baseline-rows","description":"A fixed Morse table converts supplied copy into aligned dot-dash rows.","parameters":["sourceText","unitSize","dashRatio","characterGap","rowPitch","inversion"],"avoidWhen":"Avoid when dot-dash encoding could be mistaken for unreadable primary text."},
    {"id":"d3-logo-radial-calibration","label":"Radial Calibration","family":"technical","geometrySignature":"repeated-concentric-dial-and-tick-motifs","description":"Compact repeated dials combine discrete rings with major and minor radial ticks.","parameters":["dialRadius","tickCount","majorCadence","ringCount","lineWidth","phase"],"avoidWhen":"Avoid when instrument, measurement, or precision cues conflict with the brief."},
    {"id":"d3-logo-seven-segment-code","label":"Seven Segment Code","family":"digital","geometrySignature":"hash-selected-seven-segment-glyph-grid","description":"A brand hash selects digits rendered through a fixed seven-segment glyph grid.","parameters":["sourceText","seed","digitCount","cellSize","segmentThickness","rowShift"],"avoidWhen":"Avoid when a retro-digital display aesthetic is inappropriate."}
  ]);

  const COMPOSITIONS = deepFreeze([
    { id: "d3-logo-heritage-orbit-lockup", exampleId: "type-orbit", patternId: "d3-logo-type-orbit", textureId: "d3-logo-diagonal-hatch", brand: "NORTHLIGHT", tagline: "Signal in motion", colorset: "colorset1", font: "geometric", density: 1.0, curvature: 0.72, scale: 1.0, rotation: 0, textureStrength: 0.38, seed: 101 },
    { id: "d3-logo-rising-curve-lockup", exampleId: "bezier-wordpath", patternId: "d3-logo-bezier-wordpath", textureId: "d3-logo-directional-fibers", brand: "TIDELINE", tagline: "Move with purpose", colorset: "colorset2", font: "humanist", density: 0.9, curvature: 0.82, scale: 1.0, rotation: -4, textureStrength: 0.32, seed: 102 },
    { id: "d3-logo-variable-editorial-lockup", exampleId: "variable-axis-wordmark", patternId: "d3-logo-variable-axis-wordmark", textureId: "d3-logo-micro-grid", brand: "FORMFIELD", tagline: "A flexible identity", colorset: "colorset1", font: "editorial", density: 1.1, curvature: 0.45, scale: 1.0, rotation: 0, textureStrength: 0.24, seed: 103 },
    { id: "d3-logo-joined-initial-lockup", exampleId: "ligature-bridge", patternId: "d3-logo-ligature-bridge", textureId: "d3-logo-crosshatch", brand: "ARC UNION", tagline: "Built together", colorset: "colorset2", font: "geometric", density: 1.0, curvature: 0.6, scale: 1.02, rotation: 0, textureStrength: 0.34, seed: 104 },
    { id: "d3-logo-stenciled-utility-lockup", exampleId: "stencil-cuts", patternId: "d3-logo-stencil-cuts", textureId: "d3-logo-seeded-stipple", brand: "IRONVALE", tagline: "Made to endure", colorset: "colorset1", font: "condensed", density: 1.2, curvature: 0.35, scale: 1.0, rotation: -2, textureStrength: 0.28, seed: 105 },
    { id: "d3-logo-textured-letter-window", exampleId: "letter-window", patternId: "d3-logo-letter-window", textureId: "d3-logo-voronoi-mosaic", brand: "LUMA", tagline: "See what is possible", colorset: "colorset2", font: "geometric", density: 1.0, curvature: 0.5, scale: 1.08, rotation: 0, textureStrength: 0.58, seed: 106 },
    { id: "d3-logo-mirror-axis-lockup", exampleId: "mirrored-monogram", patternId: "d3-logo-mirrored-monogram", textureId: "d3-logo-woven-checker", brand: "AXIS", tagline: "Balanced by design", colorset: "colorset1", font: "editorial", density: 0.9, curvature: 0.55, scale: 1.0, rotation: 0, textureStrength: 0.3, seed: 107 },
    { id: "d3-logo-radial-glyph-emblem", exampleId: "glyph-rosette", patternId: "d3-logo-glyph-rosette", textureId: "d3-logo-guilloche-waves", brand: "AERIA", tagline: "Many voices, one form", colorset: "colorset2", font: "humanist", density: 1.2, curvature: 0.68, scale: 0.98, rotation: 8, textureStrength: 0.36, seed: 108 },
    { id: "d3-logo-wave-baseline-lockup", exampleId: "baseline-wave", patternId: "d3-logo-baseline-wave", textureId: "d3-logo-topographic-lines", brand: "SONORA", tagline: "Make the signal visible", colorset: "colorset1", font: "humanist", density: 1.0, curvature: 0.9, scale: 1.0, rotation: 0, textureStrength: 0.3, seed: 109 },
    { id: "d3-logo-echo-stack-lockup", exampleId: "stack-offset", patternId: "d3-logo-stack-offset", textureId: "d3-logo-halftone-dots", brand: "ECHOFORM", tagline: "Repeat with intent", colorset: "colorset2", font: "condensed", density: 1.1, curvature: 0.4, scale: 1.0, rotation: -5, textureStrength: 0.32, seed: 110 },
    { id: "d3-logo-sliced-motion-lockup", exampleId: "slice-shift", patternId: "d3-logo-slice-shift", textureId: "d3-logo-directional-fibers", brand: "KINETIQ", tagline: "Designed in motion", colorset: "colorset1", font: "geometric", density: 1.0, curvature: 0.45, scale: 1.0, rotation: -3, textureStrength: 0.3, seed: 111 },
    { id: "d3-logo-outline-signal-lockup", exampleId: "multi-stroke-wordmark", patternId: "d3-logo-multi-stroke-wordmark", textureId: "d3-logo-micro-grid", brand: "SIGNAL", tagline: "Clarity through layers", colorset: "colorset2", font: "monospace", density: 1.0, curvature: 0.5, scale: 1.0, rotation: 0, textureStrength: 0.22, seed: 112 },
    { id: "d3-logo-depth-step-lockup", exampleId: "extruded-wordmark", patternId: "d3-logo-extruded-wordmark", textureId: "d3-logo-diagonal-hatch", brand: "MONOLITH", tagline: "Depth without noise", colorset: "colorset1", font: "condensed", density: 1.1, curvature: 0.35, scale: 0.96, rotation: 0, textureStrength: 0.34, seed: 113 },
    { id: "d3-logo-woven-initial-lockup", exampleId: "letter-weave", patternId: "d3-logo-letter-weave", textureId: "d3-logo-seeded-stipple", brand: "INTERLACE", tagline: "Different paths, shared future", colorset: "colorset2", font: "editorial", density: 1.0, curvature: 0.74, scale: 1.0, rotation: 0, textureStrength: 0.4, seed: 114 },
    { id: "d3-logo-responsive-brand-family", exampleId: "responsive-lockup", patternId: "d3-logo-responsive-lockup", textureId: "d3-logo-guilloche-waves", brand: "MODULA", tagline: "One system, every space", colorset: "colorset1", font: "geometric", density: 0.9, curvature: 0.5, scale: 1.0, rotation: 0, textureStrength: 0.25, seed: 115 },
    { id: "d3-logo-spiral-core-lockup", exampleId: "spiral-trace", patternId: "d3-logo-spiral-trace", textureId: "d3-logo-voronoi-mosaic", brand: "SPIRA", tagline: "Ideas in orbit", colorset: "colorset2", font: "humanist", density: 1.2, curvature: 0.86, scale: 1.0, rotation: 6, textureStrength: 0.34, seed: 116 },
    { id: "d3-logo-connected-orbit-lockup", exampleId: "orbit-network", patternId: "d3-logo-orbit-network", textureId: "d3-logo-woven-checker", brand: "NEXUS", tagline: "Connect what matters", colorset: "colorset1", font: "geometric", density: 1.1, curvature: 0.65, scale: 1.0, rotation: 0, textureStrength: 0.28, seed: 117 },
    { id: "d3-logo-modular-grid-lockup", exampleId: "grid-activation", patternId: "d3-logo-grid-activation", textureId: "d3-logo-directional-fibers", brand: "GRIDWORK", tagline: "Systems made visible", colorset: "colorset2", font: "monospace", density: 1.2, curvature: 0.4, scale: 1.0, rotation: 0, textureStrength: 0.24, seed: 118 },
    { id: "d3-logo-contour-medallion", exampleId: "contour-fingerprint", patternId: "d3-logo-contour-fingerprint", textureId: "d3-logo-diagonal-hatch", brand: "TERRAIN", tagline: "Defined by place", colorset: "colorset1", font: "editorial", density: 1.0, curvature: 0.7, scale: 1.0, rotation: 0, textureStrength: 0.42, seed: 119 },
    { id: "d3-logo-voronoi-window-lockup", exampleId: "voronoi-shards", patternId: "d3-logo-voronoi-shards", textureId: "d3-logo-guilloche-waves", brand: "VORO", tagline: "Order from fragments", colorset: "colorset2", font: "geometric", density: 1.0, curvature: 0.5, scale: 1.02, rotation: 0, textureStrength: 0.46, seed: 120 },
    { id: "d3-logo-faceted-fauna-lockup", exampleId: "animal-facets", patternId: "d3-logo-animal-facets", textureId: "d3-logo-halftone-dots", brand: "WILDFOLD", tagline: "Built for open ground", colorset: "colorset1", font: "condensed", density: 1.2, curvature: 0.58, scale: 1.0, rotation: 0, textureStrength: 0.3, seed: 121 },
    { id: "d3-logo-surface-fauna-lockup", exampleId: "animal-surface-mask", patternId: "d3-logo-animal-surface-mask", textureId: "d3-logo-topographic-lines", brand: "ROAM", tagline: "Follow your nature", colorset: "colorset2", font: "humanist", density: 1.0, curvature: 0.68, scale: 1.0, rotation: 0, textureStrength: 0.55, seed: 122 },
    { id: "d3-logo-hidden-initial-lockup", exampleId: "negative-space-reveal", patternId: "d3-logo-negative-space-reveal", textureId: "d3-logo-crosshatch", brand: "REVEAL", tagline: "Look twice", colorset: "colorset1", font: "geometric", density: 0.9, curvature: 0.5, scale: 1.0, rotation: 0, textureStrength: 0.34, seed: 123 },
    { id: "d3-logo-ribbon-fold-lockup", exampleId: "folded-ribbon", patternId: "d3-logo-folded-ribbon", textureId: "d3-logo-micro-grid", brand: "CONTINUUM", tagline: "A path that keeps moving", colorset: "colorset2", font: "humanist", density: 1.0, curvature: 0.84, scale: 0.98, rotation: 0, textureStrength: 0.3, seed: 124 },
    { id: "d3-logo-overlap-lens-lockup", exampleId: "boolean-lens", patternId: "d3-logo-boolean-lens", textureId: "d3-logo-seeded-stipple", brand: "SYNTHESIS", tagline: "Better at the intersection", colorset: "colorset1", font: "editorial", density: 1.0, curvature: 0.52, scale: 1.0, rotation: 0, textureStrength: 0.28, seed: 125 },
    { id: "d3-logo-radiant-core-lockup", exampleId: "radiant-pulse", patternId: "d3-logo-radiant-pulse", textureId: "d3-logo-halftone-dots", brand: "RADIANT", tagline: "Turn energy outward", colorset: "colorset2", font: "condensed", density: 1.2, curvature: 0.64, scale: 1.0, rotation: 0, textureStrength: 0.32, seed: 126 },
    { id: "d3-logo-harmonic-wave-lockup", exampleId: "parametric-wave", patternId: "d3-logo-parametric-wave", textureId: "d3-logo-crosshatch", brand: "HARMONIC", tagline: "Find the shared frequency", colorset: "colorset1", font: "monospace", density: 1.1, curvature: 0.88, scale: 1.0, rotation: 4, textureStrength: 0.34, seed: 127 },
    { id: "d3-logo-kaleidoscope-emblem", exampleId: "kaleidoscope-wedges", patternId: "d3-logo-kaleidoscope-wedges", textureId: "d3-logo-woven-checker", brand: "PRISMATA", tagline: "Many angles, one identity", colorset: "colorset2", font: "geometric", density: 1.0, curvature: 0.62, scale: 1.0, rotation: 12, textureStrength: 0.4, seed: 128 },
    { id: "d3-logo-polar-data-lockup", exampleId: "polar-halo", patternId: "d3-logo-polar-halo", textureId: "d3-logo-voronoi-mosaic", brand: "CYCLE", tagline: "Measure the whole system", colorset: "colorset1", font: "humanist", density: 1.0, curvature: 0.56, scale: 1.0, rotation: 0, textureStrength: 0.28, seed: 129 },
    { id: "d3-logo-iris-aperture-lockup", exampleId: "aperture-iris", patternId: "d3-logo-aperture-iris", textureId: "d3-logo-topographic-lines", brand: "APERTURE", tagline: "Bring the idea into focus", colorset: "colorset2", font: "condensed", density: 1.1, curvature: 0.76, scale: 1.0, rotation: -8, textureStrength: 0.32, seed: 130 },
    { id: "d3-logo-terminal-rule-lockup", exampleId: "terminal-extension", patternId: "d3-logo-terminal-extension", textureId: "d3-logo-micro-grid", brand: "ASCENT", tagline: "Extend the signal", colorset: "colorset1", font: "geometric", density: 1.0, curvature: 0.48, scale: 1.0, rotation: 0, textureStrength: 0.24, seed: 131 },
    { id: "d3-logo-vertical-rail-lockup", exampleId: "vertical-rail-wordmark", patternId: "d3-logo-vertical-rail-wordmark", textureId: "d3-logo-diagonal-hatch", brand: "NORTH", tagline: "Read upward", colorset: "colorset2", font: "condensed", density: 1.1, curvature: 0.42, scale: 1.0, rotation: 0, textureStrength: 0.3, seed: 132 },
    { id: "d3-logo-hinged-letter-lockup", exampleId: "hinged-glyph-fan", patternId: "d3-logo-hinged-glyph-fan", textureId: "d3-logo-crosshatch", brand: "FOLD", tagline: "Ideas open outward", colorset: "colorset1", font: "humanist", density: 1.0, curvature: 0.74, scale: 1.0, rotation: -4, textureStrength: 0.28, seed: 133 },
    { id: "d3-logo-justified-block-lockup", exampleId: "justified-word-block", patternId: "d3-logo-justified-word-block", textureId: "d3-logo-halftone-dots", brand: "COMMON", tagline: "Every line aligns", colorset: "colorset2", font: "editorial", density: 1.0, curvature: 0.36, scale: 1.0, rotation: 0, textureStrength: 0.3, seed: 134 },
    { id: "d3-logo-cadence-type-lockup", exampleId: "fill-outline-cadence", patternId: "d3-logo-fill-outline-cadence", textureId: "d3-logo-seeded-stipple", brand: "RHYTHM", tagline: "Form meets interval", colorset: "colorset1", font: "monospace", density: 1.1, curvature: 0.5, scale: 1.0, rotation: 0, textureStrength: 0.26, seed: 135 },
    { id: "d3-logo-punctuation-frame-lockup", exampleId: "punctuation-armature", patternId: "d3-logo-punctuation-armature", textureId: "d3-logo-topographic-lines", brand: "CLAUSE", tagline: "Pause with purpose", colorset: "colorset2", font: "geometric", density: 0.9, curvature: 0.58, scale: 1.0, rotation: 0, textureStrength: 0.32, seed: 136 },
    { id: "d3-logo-packed-cluster-lockup", exampleId: "circle-pack-cluster", patternId: "d3-logo-circle-pack-cluster", textureId: "d3-logo-voronoi-mosaic", brand: "KINSHIP", tagline: "Room for every part", colorset: "colorset1", font: "humanist", density: 1.2, curvature: 0.64, scale: 1.0, rotation: 0, textureStrength: 0.36, seed: 137 },
    { id: "d3-logo-treemap-mosaic-lockup", exampleId: "treemap-mosaic", patternId: "d3-logo-treemap-mosaic", textureId: "d3-logo-guilloche-waves", brand: "PARCEL", tagline: "Fit the whole story", colorset: "colorset2", font: "condensed", density: 1.1, curvature: 0.4, scale: 1.0, rotation: 0, textureStrength: 0.34, seed: 138 },
    { id: "d3-logo-hull-shell-lockup", exampleId: "convex-hull-shells", patternId: "d3-logo-convex-hull-shells", textureId: "d3-logo-woven-checker", brand: "ENVELOPE", tagline: "Hold the outer edge", colorset: "colorset1", font: "editorial", density: 1.0, curvature: 0.72, scale: 1.0, rotation: 3, textureStrength: 0.28, seed: 139 },
    { id: "d3-logo-phyllotaxis-bloom-lockup", exampleId: "phyllotaxis-bloom", patternId: "d3-logo-phyllotaxis-bloom", textureId: "d3-logo-directional-fibers", brand: "SEEDLING", tagline: "Growth finds order", colorset: "colorset2", font: "geometric", density: 1.2, curvature: 0.82, scale: 1.0, rotation: 7, textureStrength: 0.3, seed: 140 },
    { id: "d3-logo-tangent-chain-lockup", exampleId: "tangency-chain", patternId: "d3-logo-tangency-chain", textureId: "d3-logo-micro-grid", brand: "TOUCHPOINT", tagline: "Connected at the edge", colorset: "colorset1", font: "monospace", density: 1.0, curvature: 0.62, scale: 1.0, rotation: 0, textureStrength: 0.24, seed: 141 },
    { id: "d3-logo-tangram-form-lockup", exampleId: "tangram-dissection", patternId: "d3-logo-tangram-dissection", textureId: "d3-logo-diagonal-hatch", brand: "SEVEN", tagline: "Pieces become form", colorset: "colorset2", font: "humanist", density: 1.0, curvature: 0.44, scale: 1.0, rotation: -3, textureStrength: 0.3, seed: 142 },
    { id: "d3-logo-superellipse-nest-lockup", exampleId: "superellipse-family", patternId: "d3-logo-superellipse-family", textureId: "d3-logo-crosshatch", brand: "SOFTBOX", tagline: "Shape between forms", colorset: "colorset1", font: "geometric", density: 1.1, curvature: 0.78, scale: 1.0, rotation: 0, textureStrength: 0.28, seed: 143 },
    { id: "d3-logo-isometric-stack-lockup", exampleId: "isometric-block-stack", patternId: "d3-logo-isometric-block-stack", textureId: "d3-logo-halftone-dots", brand: "UPSTACK", tagline: "Build from every side", colorset: "colorset2", font: "condensed", density: 1.2, curvature: 0.38, scale: 1.0, rotation: 0, textureStrength: 0.32, seed: 144 },
    { id: "d3-logo-euler-route-lockup", exampleId: "eulerian-one-stroke", patternId: "d3-logo-eulerian-one-stroke", textureId: "d3-logo-seeded-stipple", brand: "UNBROKEN", tagline: "One path through all", colorset: "colorset1", font: "editorial", density: 1.0, curvature: 0.7, scale: 1.0, rotation: 0, textureStrength: 0.26, seed: 145 },
    { id: "d3-logo-perfect-maze-lockup", exampleId: "perfect-maze", patternId: "d3-logo-perfect-maze", textureId: "d3-logo-topographic-lines", brand: "WAYFIND", tagline: "Every turn connects", colorset: "colorset2", font: "monospace", density: 1.2, curvature: 0.34, scale: 1.0, rotation: 0, textureStrength: 0.34, seed: 146 },
    { id: "d3-logo-stream-routing-lockup", exampleId: "split-merge-stream", patternId: "d3-logo-split-merge-stream", textureId: "d3-logo-voronoi-mosaic", brand: "CONFLUX", tagline: "Many paths, one current", colorset: "colorset1", font: "humanist", density: 1.1, curvature: 0.82, scale: 1.0, rotation: 0, textureStrength: 0.36, seed: 147 },
    { id: "d3-logo-dendrogram-crown-lockup", exampleId: "dendrogram-crown", patternId: "d3-logo-dendrogram-crown", textureId: "d3-logo-guilloche-waves", brand: "LINEAGE", tagline: "Branch into clarity", colorset: "colorset2", font: "geometric", density: 1.0, curvature: 0.68, scale: 1.0, rotation: 0, textureStrength: 0.32, seed: 148 },
    { id: "d3-logo-ring-chain-lockup", exampleId: "linked-ring-chain", patternId: "d3-logo-linked-ring-chain", textureId: "d3-logo-woven-checker", brand: "LINKAGE", tagline: "Held by connection", colorset: "colorset1", font: "condensed", density: 1.0, curvature: 0.58, scale: 1.0, rotation: -5, textureStrength: 0.28, seed: 149 },
    { id: "d3-logo-lsystem-growth-lockup", exampleId: "lsystem-branch", patternId: "d3-logo-lsystem-branch", textureId: "d3-logo-directional-fibers", brand: "ARBOR", tagline: "Rules become growth", colorset: "colorset2", font: "editorial", density: 1.2, curvature: 0.76, scale: 1.0, rotation: 0, textureStrength: 0.3, seed: 150 },
    { id: "d3-logo-hilbert-route-lockup", exampleId: "hilbert-route", patternId: "d3-logo-hilbert-route", textureId: "d3-logo-micro-grid", brand: "LOCALITY", tagline: "Fill space continuously", colorset: "colorset1", font: "monospace", density: 1.2, curvature: 0.3, scale: 1.0, rotation: 0, textureStrength: 0.24, seed: 151 },
    { id: "d3-logo-profile-boundary-lockup", exampleId: "reciprocal-profiles", patternId: "d3-logo-reciprocal-profiles", textureId: "d3-logo-diagonal-hatch", brand: "DIALOGUE", tagline: "Meet at one boundary", colorset: "colorset2", font: "humanist", density: 1.0, curvature: 0.7, scale: 1.0, rotation: 0, textureStrength: 0.3, seed: 152 },
    { id: "d3-logo-gutter-symbol-lockup", exampleId: "modular-gutter-symbol", patternId: "d3-logo-modular-gutter-symbol", textureId: "d3-logo-crosshatch", brand: "INTERVAL", tagline: "Meaning lives between", colorset: "colorset1", font: "geometric", density: 1.1, curvature: 0.4, scale: 1.0, rotation: 0, textureStrength: 0.28, seed: 153 },
    { id: "d3-logo-central-void-lockup", exampleId: "tangent-void-star", patternId: "d3-logo-tangent-void-star", textureId: "d3-logo-halftone-dots", brand: "STARVOID", tagline: "Space makes the symbol", colorset: "colorset2", font: "condensed", density: 1.0, curvature: 0.66, scale: 1.0, rotation: 6, textureStrength: 0.32, seed: 154 },
    { id: "d3-logo-reciprocal-tile-lockup", exampleId: "reciprocal-tessellation", patternId: "d3-logo-reciprocal-tessellation", textureId: "d3-logo-seeded-stipple", brand: "DUALITY", tagline: "Ground becomes figure", colorset: "colorset1", font: "editorial", density: 1.2, curvature: 0.52, scale: 1.0, rotation: 0, textureStrength: 0.26, seed: 155 },
    { id: "d3-logo-impossible-beam-lockup", exampleId: "impossible-triangle", patternId: "d3-logo-impossible-triangle", textureId: "d3-logo-topographic-lines", brand: "PARADOX", tagline: "Follow every edge", colorset: "colorset2", font: "monospace", density: 1.0, curvature: 0.46, scale: 1.0, rotation: 0, textureStrength: 0.34, seed: 156 },
    { id: "d3-logo-necker-depth-lockup", exampleId: "necker-cube", patternId: "d3-logo-necker-cube", textureId: "d3-logo-voronoi-mosaic", brand: "FLIPSPACE", tagline: "See depth two ways", colorset: "colorset1", font: "geometric", density: 1.0, curvature: 0.48, scale: 1.0, rotation: 0, textureStrength: 0.36, seed: 157 },
    { id: "d3-logo-kanizsa-closure-lockup", exampleId: "kanizsa-closure", patternId: "d3-logo-kanizsa-closure", textureId: "d3-logo-guilloche-waves", brand: "IMPLIED", tagline: "Complete what is absent", colorset: "colorset2", font: "humanist", density: 0.9, curvature: 0.62, scale: 1.0, rotation: 0, textureStrength: 0.32, seed: 158 },
    { id: "d3-logo-line-screen-lockup", exampleId: "line-screen-silhouette", patternId: "d3-logo-line-screen-silhouette", textureId: "d3-logo-woven-checker", brand: "SCANLINE", tagline: "Shape through intervals", colorset: "colorset1", font: "condensed", density: 1.2, curvature: 0.56, scale: 1.0, rotation: 0, textureStrength: 0.28, seed: 159 },
    { id: "d3-logo-perspective-portal-lockup", exampleId: "perspective-portal", patternId: "d3-logo-perspective-portal", textureId: "d3-logo-directional-fibers", brand: "THRESHOLD", tagline: "Enter the next frame", colorset: "colorset2", font: "editorial", density: 1.1, curvature: 0.6, scale: 1.0, rotation: -2, textureStrength: 0.3, seed: 160 },
    { id: "d3-logo-reuleaux-body-lockup", exampleId: "reuleaux-body", patternId: "d3-logo-reuleaux-body", textureId: "d3-logo-micro-grid", brand: "CONSTANT", tagline: "Width in every direction", colorset: "colorset1", font: "geometric", density: 1.0, curvature: 0.68, scale: 1.0, rotation: 0, textureStrength: 0.24, seed: 161 },
    { id: "d3-logo-cassini-oval-lockup", exampleId: "cassini-oval", patternId: "d3-logo-cassini-oval", textureId: "d3-logo-diagonal-hatch", brand: "LOCUS", tagline: "Distance becomes form", colorset: "colorset2", font: "humanist", density: 0.9, curvature: 0.76, scale: 1.0, rotation: -3, textureStrength: 0.28, seed: 162 },
    { id: "d3-logo-polar-reciprocal-lockup", exampleId: "polar-reciprocal", patternId: "d3-logo-polar-reciprocal", textureId: "d3-logo-crosshatch", brand: "DUAL", tagline: "Every edge has a counterpart", colorset: "colorset1", font: "editorial", density: 1.1, curvature: 0.52, scale: 1.0, rotation: 2, textureStrength: 0.26, seed: 163 },
    { id: "d3-logo-minkowski-sum-lockup", exampleId: "minkowski-sum", patternId: "d3-logo-minkowski-sum", textureId: "d3-logo-halftone-dots", brand: "SUMFORM", tagline: "Shapes add into structure", colorset: "colorset2", font: "condensed", density: 1.0, curvature: 0.58, scale: 1.02, rotation: 0, textureStrength: 0.3, seed: 164 },
    { id: "d3-logo-pedal-curve-lockup", exampleId: "pedal-curve", patternId: "d3-logo-pedal-curve", textureId: "d3-logo-seeded-stipple", brand: "FOOTPOINT", tagline: "Trace the perpendicular", colorset: "colorset1", font: "monospace", density: 1.2, curvature: 0.72, scale: 1.0, rotation: 4, textureStrength: 0.25, seed: 165 },
    { id: "d3-logo-involute-gear-lockup", exampleId: "involute-gear", patternId: "d3-logo-involute-gear", textureId: "d3-logo-topographic-lines", brand: "UNWIND", tagline: "Motion shaped by contact", colorset: "colorset2", font: "geometric", density: 1.1, curvature: 0.46, scale: 0.98, rotation: -2, textureStrength: 0.32, seed: 166 },
    { id: "d3-logo-desargues-incidence-lockup", exampleId: "desargues-incidence", patternId: "d3-logo-desargues-incidence", textureId: "d3-logo-voronoi-mosaic", brand: "AXIS", tagline: "Perspective proves alignment", colorset: "colorset1", font: "humanist", density: 1.0, curvature: 0.5, scale: 1.0, rotation: 0, textureStrength: 0.27, seed: 167 },
    { id: "d3-logo-circle-inversion-lockup", exampleId: "circle-inversion", patternId: "d3-logo-circle-inversion", textureId: "d3-logo-guilloche-waves", brand: "INVERSE", tagline: "Near becomes far", colorset: "colorset2", font: "editorial", density: 1.2, curvature: 0.64, scale: 1.0, rotation: 5, textureStrength: 0.34, seed: 168 },
    { id: "d3-logo-catenary-funicular-lockup", exampleId: "catenary-funicular", patternId: "d3-logo-catenary-funicular", textureId: "d3-logo-woven-checker", brand: "FUNICULAR", tagline: "Load finds its curve", colorset: "colorset1", font: "condensed", density: 0.9, curvature: 0.82, scale: 1.0, rotation: 0, textureStrength: 0.28, seed: 169 },
    { id: "d3-logo-joukowski-airfoil-lockup", exampleId: "joukowski-airfoil", patternId: "d3-logo-joukowski-airfoil", textureId: "d3-logo-directional-fibers", brand: "TRANSFORM", tagline: "Map flow into form", colorset: "colorset2", font: "monospace", density: 1.1, curvature: 0.6, scale: 1.0, rotation: -4, textureStrength: 0.3, seed: 170 },
    { id: "d3-logo-hyperbolic-geodesics-lockup", exampleId: "hyperbolic-geodesics", patternId: "d3-logo-hyperbolic-geodesics", textureId: "d3-logo-micro-grid", brand: "GEODESIC", tagline: "Shortest paths bend", colorset: "colorset1", font: "geometric", density: 1.2, curvature: 0.78, scale: 1.0, rotation: 0, textureStrength: 0.24, seed: 171 },
    { id: "d3-logo-elliptic-group-law-lockup", exampleId: "elliptic-group-law", patternId: "d3-logo-elliptic-group-law", textureId: "d3-logo-diagonal-hatch", brand: "TANGENT", tagline: "Addition through incidence", colorset: "colorset2", font: "humanist", density: 1.0, curvature: 0.66, scale: 1.0, rotation: 3, textureStrength: 0.28, seed: 172 },
    { id: "d3-logo-mobius-strip-lockup", exampleId: "mobius-strip", patternId: "d3-logo-mobius-strip", textureId: "d3-logo-crosshatch", brand: "ONESIDE", tagline: "Continuity with a twist", colorset: "colorset1", font: "editorial", density: 1.1, curvature: 0.74, scale: 1.0, rotation: -5, textureStrength: 0.26, seed: 173 },
    { id: "d3-logo-torus-knot-lockup", exampleId: "torus-knot", patternId: "d3-logo-torus-knot", textureId: "d3-logo-halftone-dots", brand: "COPRIME", tagline: "One curve many crossings", colorset: "colorset2", font: "condensed", density: 1.2, curvature: 0.7, scale: 0.98, rotation: 6, textureStrength: 0.3, seed: 174 },
    { id: "d3-logo-ruled-hyperboloid-lockup", exampleId: "ruled-hyperboloid", patternId: "d3-logo-ruled-hyperboloid", textureId: "d3-logo-seeded-stipple", brand: "RULED", tagline: "Lines compose a surface", colorset: "colorset1", font: "monospace", density: 1.1, curvature: 0.56, scale: 1.0, rotation: 0, textureStrength: 0.25, seed: 175 },
    { id: "d3-logo-tensegrity-prism-lockup", exampleId: "tensegrity-prism", patternId: "d3-logo-tensegrity-prism", textureId: "d3-logo-topographic-lines", brand: "EQUILIBRIUM", tagline: "Tension holds the whole", colorset: "colorset2", font: "geometric", density: 1.0, curvature: 0.48, scale: 1.0, rotation: -3, textureStrength: 0.32, seed: 176 },
    { id: "d3-logo-maxwell-reciprocal-lockup", exampleId: "maxwell-reciprocal", patternId: "d3-logo-maxwell-reciprocal", textureId: "d3-logo-voronoi-mosaic", brand: "RECIPROCAL", tagline: "Force mirrors form", colorset: "colorset1", font: "humanist", density: 1.1, curvature: 0.54, scale: 1.0, rotation: 2, textureStrength: 0.27, seed: 177 },
    { id: "d3-logo-medial-axis-lockup", exampleId: "medial-axis", patternId: "d3-logo-medial-axis", textureId: "d3-logo-guilloche-waves", brand: "SKELETON", tagline: "The center of every boundary", colorset: "colorset2", font: "editorial", density: 1.2, curvature: 0.76, scale: 1.0, rotation: 0, textureStrength: 0.34, seed: 178 },
    { id: "d3-logo-string-parabola-lockup", exampleId: "string-parabola", patternId: "d3-logo-string-parabola", textureId: "d3-logo-woven-checker", brand: "ENVELOPE", tagline: "Straight lines reveal a curve", colorset: "colorset1", font: "condensed", density: 1.1, curvature: 0.8, scale: 1.0, rotation: 4, textureStrength: 0.28, seed: 179 },
    { id: "d3-logo-circle-caustic-lockup", exampleId: "circle-caustic", patternId: "d3-logo-circle-caustic", textureId: "d3-logo-directional-fibers", brand: "CAUSTIC", tagline: "Reflection gathers light", colorset: "colorset2", font: "monospace", density: 1.2, curvature: 0.72, scale: 1.0, rotation: -4, textureStrength: 0.3, seed: 180 },
    { id: "d3-logo-moire-beat-lockup", exampleId: "moire-beat", patternId: "d3-logo-moire-beat", textureId: "d3-logo-micro-grid", brand: "BEATFIELD", tagline: "Difference makes rhythm", colorset: "colorset1", font: "geometric", density: 1.2, curvature: 0.6, scale: 1.0, rotation: 5, textureStrength: 0.24, seed: 181 },
    { id: "d3-logo-peaucellier-linkage-lockup", exampleId: "peaucellier-linkage", patternId: "d3-logo-peaucellier-linkage", textureId: "d3-logo-diagonal-hatch", brand: "LINKAGE", tagline: "Mechanism draws truth", colorset: "colorset2", font: "humanist", density: 1.0, curvature: 0.5, scale: 1.0, rotation: 0, textureStrength: 0.28, seed: 182 },
    { id: "d3-logo-lorenz-attractor-lockup", exampleId: "lorenz-attractor", patternId: "d3-logo-lorenz-attractor", textureId: "d3-logo-crosshatch", brand: "STRANGEFLOW", tagline: "Order beyond repetition", colorset: "colorset1", font: "editorial", density: 1.1, curvature: 0.84, scale: 1.0, rotation: 3, textureStrength: 0.26, seed: 183 },
    { id: "d3-logo-affine-ifs-lockup", exampleId: "affine-ifs", patternId: "d3-logo-affine-ifs", textureId: "d3-logo-halftone-dots", brand: "INVARIANT", tagline: "Simple maps grow complexity", colorset: "colorset2", font: "condensed", density: 1.2, curvature: 0.7, scale: 1.0, rotation: -2, textureStrength: 0.3, seed: 184 },
    { id: "d3-logo-cellular-automaton-lockup", exampleId: "cellular-automaton", patternId: "d3-logo-cellular-automaton", textureId: "d3-logo-seeded-stipple", brand: "LOCALRULE", tagline: "Neighborhoods shape time", colorset: "colorset1", font: "monospace", density: 1.2, curvature: 0.4, scale: 1.0, rotation: 0, textureStrength: 0.25, seed: 185 },
    { id: "d3-logo-logistic-bifurcation-lockup", exampleId: "logistic-bifurcation", patternId: "d3-logo-logistic-bifurcation", textureId: "d3-logo-topographic-lines", brand: "CASCADE", tagline: "Change splits into branches", colorset: "colorset2", font: "geometric", density: 1.1, curvature: 0.62, scale: 1.0, rotation: 0, textureStrength: 0.32, seed: 186 },
    { id: "d3-logo-field-streamlines-lockup", exampleId: "field-streamlines", patternId: "d3-logo-field-streamlines", textureId: "d3-logo-voronoi-mosaic", brand: "FLOWFIELD", tagline: "Follow the vector", colorset: "colorset1", font: "humanist", density: 1.2, curvature: 0.82, scale: 1.0, rotation: 4, textureStrength: 0.27, seed: 187 },
    { id: "d3-logo-newton-basin-lockup", exampleId: "newton-basin", patternId: "d3-logo-newton-basin", textureId: "d3-logo-guilloche-waves", brand: "BASIN", tagline: "Every start finds a root", colorset: "colorset2", font: "editorial", density: 1.2, curvature: 0.74, scale: 1.0, rotation: -3, textureStrength: 0.34, seed: 188 },
    { id: "d3-logo-steiner-tree-lockup", exampleId: "steiner-tree", patternId: "d3-logo-steiner-tree", textureId: "d3-logo-woven-checker", brand: "STEINER", tagline: "Connect more with less", colorset: "colorset1", font: "condensed", density: 1.0, curvature: 0.56, scale: 1.0, rotation: 0, textureStrength: 0.28, seed: 189 },
    { id: "d3-logo-penrose-substitution-lockup", exampleId: "penrose-substitution", patternId: "d3-logo-penrose-substitution", textureId: "d3-logo-directional-fibers", brand: "APERIODIC", tagline: "Pattern without repetition", colorset: "colorset2", font: "monospace", density: 1.1, curvature: 0.68, scale: 1.0, rotation: 5, textureStrength: 0.3, seed: 190 }
  ]);

  const FONT_STACKS = deepFreeze([
    { id: "geometric", label: "Geometric Sans", value: '"Avenir Next", "Century Gothic", Arial, sans-serif' },
    { id: "humanist", label: "Humanist Sans", value: '"Open Sans", "Segoe UI", Arial, sans-serif' },
    { id: "condensed", label: "Condensed Sans", value: '"Arial Narrow", "Roboto Condensed", "Liberation Sans Narrow", sans-serif' },
    { id: "editorial", label: "Editorial Serif", value: 'Georgia, "Times New Roman", serif' },
    { id: "monospace", label: "Monospaced", value: '"IBM Plex Mono", Consolas, "Courier New", monospace' }
  ]);

  const FONTS = deepFreeze(Object.fromEntries(FONT_STACKS.map((font) => [font.id, {
    id: font.id,
    label: font.label,
    value: font.value,
    family: font.value
  }])));

  const COLORSETS = deepFreeze({
    colorset1: {
      name: "basic-red-neutral-style",
      allowed: ["#000000", "#1c1c1c", "#333e48", "#363636", "#4f4f4f", "#696969", "#6d1222", "#828282", "#9c9c9c", "#9e1b32", "#b5b5b5", "#cfcfcf", "#e7e7e7", "#e8002a", "#f7f7f7", "#ffccd5", "#ffffff"],
      roles: { background: "#f7f7f7", surface: "#ffffff", ink: "#333e48", inkDark: "#1c1c1c", primary: "#9e1b32", primaryDark: "#6d1222", accent: "#e8002a", accentSoft: "#ffccd5", muted: "#828282", line: "#cfcfcf", quiet: "#e7e7e7" },
      sequence: ["#9e1b32", "#333e48", "#6d1222", "#828282", "#e8002a", "#cfcfcf"]
    },
    colorset2: {
      name: "full-color-style",
      allowed: ["#000000", "#004d66", "#007298", "#00ace6", "#1c1c1c", "#294d19", "#333e48", "#363636", "#36b300", "#431f47", "#45842a", "#4f4f4f", "#652f6c", "#696969", "#6d1222", "#828282", "#98700c", "#994a00", "#9c9c9c", "#9e00b3", "#9e1b32", "#b5b5b5", "#cdf3ff", "#cfcfcf", "#dbffcc", "#e77204", "#e7e7e7", "#e8002a", "#f1c319", "#f7f7f7", "#f9ccff", "#ff9633", "#ffccd5", "#ffd332", "#ffe5cc", "#fff4cc", "#ffffff"],
      roles: { background: "#f7f7f7", surface: "#ffffff", ink: "#333e48", inkDark: "#1c1c1c", primary: "#9e1b32", primaryDark: "#6d1222", secondary: "#007298", secondaryDark: "#004d66", tertiary: "#e77204", positive: "#45842a", attention: "#f1c319", special: "#652f6c", accent: "#e8002a", accentSoft: "#ffccd5", muted: "#828282", line: "#cfcfcf", quiet: "#e7e7e7" },
      sequence: ["#9e1b32", "#007298", "#e77204", "#45842a", "#652f6c", "#f1c319"]
    }
  });

  const PATTERN_BY_ID = new Map(PATTERNS.map((item) => [item.id, item]));
  const TEXTURE_BY_ID = new Map(TEXTURES.map((item) => [item.id, item]));
  const COMPOSITION_BY_ID = new Map(COMPOSITIONS.map((item) => [item.id, item]));
  const COMPOSITION_BY_PATTERN = new Map(COMPOSITIONS.map((item) => [item.patternId, item]));
  const FONT_BY_ID = new Map(FONT_STACKS.map((item) => [item.id, item]));

  function getD3() {
    const d3 = root.d3;
    if (!d3 || typeof d3.select !== "function" || typeof d3.line !== "function" || typeof d3.arc !== "function") {
      throw new Error("D3 Logo Design requires the global D3 v7 bundle before renderLogo or renderTexture is called.");
    }
    if (d3.version && String(d3.version).split(".")[0] !== "7") {
      throw new Error(`D3 Logo Design requires D3 v7; found ${d3.version}.`);
    }
    return d3;
  }

  function clamp(value, minimum, maximum) {
    return Math.max(minimum, Math.min(maximum, value));
  }

  function finiteNumber(value, fallback) {
    const number = Number(value);
    return Number.isFinite(number) ? number : fallback;
  }

  function sanitizeId(value) {
    const clean = String(value == null ? "logo" : value)
      .toLowerCase()
      .replace(/[^a-z0-9_-]+/g, "-")
      .replace(/^-+|-+$/g, "")
      .replace(/-+/g, "-");
    return clean || "logo";
  }

  function hashString(value) {
    let hash = 2166136261;
    const text = String(value);
    for (let index = 0; index < text.length; index += 1) {
      hash ^= text.charCodeAt(index);
      hash = Math.imul(hash, 16777619);
    }
    return (hash >>> 0).toString(36);
  }

  function makeIdFactory(prefix) {
    const seen = new Map();
    return function uid(label) {
      const slug = sanitizeId(label);
      const count = (seen.get(slug) || 0) + 1;
      seen.set(slug, count);
      return `${prefix}-${slug}${count > 1 ? `-${count}` : ""}`;
    };
  }

  function fragmentUrl(id) {
    return `url(#${id})`;
  }

  function resolveFont(value) {
    const requested = value == null ? "geometric" : String(value);
    if (FONT_BY_ID.has(requested)) return FONT_BY_ID.get(requested);
    const byValue = FONT_STACKS.find((item) => item.value === requested || item.label === requested);
    if (byValue) return byValue;
    if (requested.trim() && requested.length <= 180 && !/[{};]/.test(requested)) {
      return { id: "custom", label: "Custom licensed font", value: requested };
    }
    throw new RangeError(`Invalid custom font stack: ${requested}`);
  }

  function isValidCanonicalId(value) {
    return typeof value === "string" && value.length <= 64 && /^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(value);
  }

  function normalizeConfig(input) {
    const source = input && typeof input === "object" ? input : {};
    const requestedComposition = source.compositionId == null ? null : String(source.compositionId);
    const requestedPattern = source.patternId == null
      ? (source.pattern == null ? null : String(source.pattern))
      : String(source.patternId);
    const requestedTexture = source.textureId == null
      ? (source.texture == null ? null : String(source.texture))
      : String(source.textureId);

    let composition;
    let compositionId;
    if (requestedComposition) {
      composition = COMPOSITION_BY_ID.get(requestedComposition);
      if (composition) {
        if (requestedPattern && requestedPattern !== composition.patternId) {
          throw new RangeError(`Composition ${requestedComposition} requires pattern ${composition.patternId}.`);
        }
        compositionId = composition.id;
      } else {
        if (!isValidCanonicalId(requestedComposition)) {
          throw new RangeError(`Invalid custom composition ID: ${requestedComposition}`);
        }
        if (!requestedPattern || !PATTERN_BY_ID.has(requestedPattern)) {
          throw new RangeError(`Custom composition ${requestedComposition} requires a registered patternId.`);
        }
        composition = COMPOSITION_BY_PATTERN.get(requestedPattern);
        compositionId = requestedComposition;
      }
    } else if (requestedPattern) {
      composition = COMPOSITION_BY_PATTERN.get(requestedPattern);
      if (!composition) throw new RangeError(`Unknown pattern ID: ${requestedPattern}`);
      compositionId = composition.id;
    } else {
      composition = COMPOSITIONS[0];
      compositionId = composition.id;
    }

    const patternId = requestedPattern || composition.patternId;
    const textureId = requestedTexture || composition.textureId;
    const expectedExampleId = patternId.replace(/^d3-logo-/, "");
    const exampleId = source.exampleId == null ? composition.exampleId : String(source.exampleId);
    const colorset = source.colorset == null ? composition.colorset : String(source.colorset);
    if (!PATTERN_BY_ID.has(patternId)) throw new RangeError(`Unknown pattern ID: ${patternId}`);
    if (!TEXTURE_BY_ID.has(textureId)) throw new RangeError(`Unknown texture ID: ${textureId}`);
    if (!isValidCanonicalId(exampleId) || exampleId !== expectedExampleId) {
      throw new RangeError(`Example ID ${exampleId} must match the local technique slug ${expectedExampleId}.`);
    }
    if (!Object.prototype.hasOwnProperty.call(COLORSETS, colorset)) {
      throw new RangeError(`Unknown colorset: ${colorset}`);
    }

    const font = resolveFont(source.font == null ? (source.fontFamily == null ? composition.font : source.fontFamily) : source.font);
    const brand = String(source.brand == null ? composition.brand : source.brand);
    const tagline = String(source.tagline == null ? composition.tagline : source.tagline);
    const density = clamp(finiteNumber(source.density, composition.density), 0.45, 2.0);
    const curvature = clamp(finiteNumber(source.curvature, composition.curvature), 0, 1);
    const scale = clamp(finiteNumber(source.scale, composition.scale), 0.6, 1.35);
    const rotation = clamp(finiteNumber(source.rotation, composition.rotation), -180, 180);
    const textureStrength = clamp(finiteNumber(source.textureStrength, composition.textureStrength), 0, 1);
    const seed = Math.trunc(finiteNumber(source.seed, composition.seed));

    return Object.freeze({
      compositionId,
      exampleId,
      patternId,
      textureId,
      brand,
      tagline,
      colorset,
      font: font.id,
      fontFamily: font.value,
      density,
      curvature,
      scale,
      rotation,
      textureStrength,
      seed,
      viewBox: VIEW_BOX,
      accessibilityLabel: String(source.accessibilityLabel == null ? `${brand}${tagline ? ` — ${tagline}` : ""}` : source.accessibilityLabel),
      instanceId: source.instanceId == null ? "" : String(source.instanceId),
      outputWidth: finiteNumber(source.outputWidth, 0),
      smallSize: source.smallSize === true || source.swatch === true
    });
  }

  function normalizeTextureConfig(input) {
    const source = input && typeof input === "object" ? input : {};
    const requestedTexture = source.textureId == null
      ? (source.texture == null ? TEXTURES[0].id : String(source.texture))
      : String(source.textureId);
    const texture = TEXTURE_BY_ID.get(requestedTexture);
    if (!texture) throw new RangeError(`Unknown texture ID: ${requestedTexture}`);

    const colorset = source.colorset == null ? "colorset1" : String(source.colorset);
    if (!Object.prototype.hasOwnProperty.call(COLORSETS, colorset)) {
      throw new RangeError(`Unknown colorset: ${colorset}`);
    }
    const font = resolveFont(source.font == null ? (source.fontFamily == null ? "monospace" : source.fontFamily) : source.font);
    const brand = String(source.brand == null ? "BRAND" : source.brand).trim() || "BRAND";
    const strengthSource = source.textureStrength == null ? source.strength : source.textureStrength;
    const density = clamp(finiteNumber(source.density, 1), 0.45, 2.0);
    const curvature = clamp(finiteNumber(source.curvature, 0.5), 0, 1);
    const textureStrength = clamp(finiteNumber(strengthSource, 0.7), 0, 1);
    const seed = Math.trunc(finiteNumber(source.seed, 101));
    const exampleId = requestedTexture.replace(/^d3-logo-/, "");

    return Object.freeze({
      exampleId,
      patternId: requestedTexture,
      textureId: requestedTexture,
      colorset,
      brand,
      font: font.id,
      fontFamily: font.value,
      density,
      curvature,
      textureStrength,
      seed,
      viewBox: VIEW_BOX,
      accessibilityLabel: String(source.accessibilityLabel == null ? `${texture.label} texture` : source.accessibilityLabel),
      instanceId: source.instanceId == null ? "" : String(source.instanceId),
      outputWidth: finiteNumber(source.outputWidth, 0),
      smallSize: source.smallSize === true || source.swatch === true
    });
  }

  function effectiveWidth(svgNode, config) {
    if (config.outputWidth > 0) return config.outputWidth;
    if (typeof svgNode.getBoundingClientRect === "function") {
      const measured = finiteNumber(svgNode.getBoundingClientRect().width, 0);
      if (measured > 0) return measured;
    }
    const widthAttribute = finiteNumber(svgNode.getAttribute("width"), 0);
    return widthAttribute > 0 ? widthAttribute : 480;
  }

  function markContainsText(markNode, ctx) {
    if (markNode.querySelector("text, [data-text-proxy]")) return true;
    return Array.from(markNode.querySelectorAll("use")).some((node) => resolvedUseTarget(node, ctx.svgNode)?.localName === "text");
  }

  function rotatedScaleLimit(box, rotation, safeBounds) {
    const pivotX = 240;
    const pivotY = 145;
    const radians = rotation * Math.PI / 180;
    const cosine = Math.cos(radians);
    const sine = Math.sin(radians);
    const corners = [
      [box.x, box.y],
      [box.x + box.width, box.y],
      [box.x + box.width, box.y + box.height],
      [box.x, box.y + box.height]
    ];
    let limit = Number.POSITIVE_INFINITY;
    for (const [x, y] of corners) {
      const dx = x - pivotX;
      const dy = y - pivotY;
      const rotatedX = dx * cosine - dy * sine;
      const rotatedY = dx * sine + dy * cosine;
      if (rotatedX < 0) limit = Math.min(limit, (pivotX - safeBounds.left) / -rotatedX);
      if (rotatedX > 0) limit = Math.min(limit, (safeBounds.right - pivotX) / rotatedX);
      if (rotatedY < 0) limit = Math.min(limit, (pivotY - safeBounds.top) / -rotatedY);
      if (rotatedY > 0) limit = Math.min(limit, (safeBounds.bottom - pivotY) / rotatedY);
    }
    return Number.isFinite(limit) && limit > 0 ? limit : 1;
  }

  function applySafeMarkTransform(markGroup, ctx) {
    const markNode = markGroup.node();
    const requestedScale = ctx.config.scale;
    const requestedRotation = ctx.config.rotation;
    const carriesText = markContainsText(markNode, ctx);
    const reservesBrand = !ctx.brandHandled;
    const reservesTagline = !ctx.taglineHandled && Boolean(ctx.config.tagline);
    const safeBounds = {
      left: 18,
      right: 462,
      top: 14,
      bottom: reservesBrand ? 238 : (reservesTagline ? 282 : 306)
    };
    let effectiveScale = requestedScale;
    try {
      markGroup.attr("transform", null);
      const box = markNode.getBBox();
      if ([box.x, box.y, box.width, box.height].every(Number.isFinite) && box.width > 0 && box.height > 0) {
        effectiveScale = Math.min(requestedScale, rotatedScaleLimit(box, requestedRotation, safeBounds) * 0.98);
      }
    } catch (error) {
      effectiveScale = requestedScale;
    }
    effectiveScale = clamp(effectiveScale, 0.25, requestedScale);
    markGroup
      .attr("data-requested-scale", requestedScale)
      .attr("data-effective-scale", effectiveScale.toFixed(4))
      .attr("data-requested-rotation", requestedRotation)
      .attr("data-effective-rotation", requestedRotation)
      .attr("data-carries-text", carriesText ? "true" : "false")
      .attr("data-reserves-brand", reservesBrand ? "true" : "false")
      .attr("data-reserves-tagline", reservesTagline ? "true" : "false")
      .attr("data-safe-bounds", `${safeBounds.left},${safeBounds.top},${safeBounds.right},${safeBounds.bottom}`)
      .attr("transform", `translate(240,145) rotate(${requestedRotation}) scale(${effectiveScale}) translate(-240,-145)`);
    ctx.svg
      .attr("data-effective-scale", effectiveScale.toFixed(4))
      .attr("data-effective-rotation", requestedRotation);
    return effectiveScale;
  }

  function stablePrefix(svgNode, config) {
    const ownerDocument = svgNode.ownerDocument;
    const existingInstance = svgNode.getAttribute("data-logo-instance") || "";
    const explicitIdentity = config.instanceId || svgNode.getAttribute("id") || existingInstance;
    let documentIndex = 0;
    if (!explicitIdentity && ownerDocument && typeof ownerDocument.querySelectorAll === "function") {
      const nodes = Array.from(ownerDocument.querySelectorAll("svg"));
      const found = nodes.indexOf(svgNode);
      if (found >= 0) documentIndex = found;
    }
    const nodeIdentity = explicitIdentity || `${config.compositionId}-${documentIndex}`;
    const instance = `${sanitizeId(config.compositionId)}-${hashString(nodeIdentity)}`;
    svgNode.setAttribute("data-logo-instance", instance);
    return `d3ld-${instance}`;
  }

  function stableTexturePrefix(svgNode, config) {
    const ownerDocument = svgNode.ownerDocument;
    const existingInstance = svgNode.getAttribute("data-texture-instance") || "";
    const explicitIdentity = config.instanceId || svgNode.getAttribute("id") || existingInstance;
    let documentIndex = 0;
    if (!explicitIdentity && ownerDocument && typeof ownerDocument.querySelectorAll === "function") {
      const nodes = Array.from(ownerDocument.querySelectorAll("svg"));
      const found = nodes.indexOf(svgNode);
      if (found >= 0) documentIndex = found;
    }
    const nodeIdentity = explicitIdentity || `${config.textureId}-${documentIndex}`;
    const instance = `${sanitizeId(config.textureId)}-${hashString(nodeIdentity)}`;
    svgNode.setAttribute("data-texture-instance", instance);
    return `d3ldt-${instance}`;
  }

  function seededRandom(d3, seed, salt) {
    const mixed = ((seed >>> 0) ^ parseInt(hashString(salt), 36)) >>> 0;
    return d3.randomLcg(mixed);
  }

  function texturePattern(defs, ctx, size) {
    const texture = TEXTURE_BY_ID.get(ctx.config.textureId);
    return defs.append("pattern")
      .attr("id", ctx.texturePatternId)
      .attr("data-texture-id", texture.id)
      .attr("data-geometry-signature", texture.geometrySignature)
      .attr("patternUnits", "userSpaceOnUse")
      .attr("width", size)
      .attr("height", size)
      .attr("viewBox", `0 0 ${size} ${size}`);
  }

  function textureBase(pattern, ctx, size, fill) {
    pattern.append("rect")
      .attr("width", size)
      .attr("height", size)
      .attr("fill", fill || ctx.palette.roles.primary);
  }

  const TEXTURE_RENDERERS = {
    "d3-logo-micro-grid": function renderMicroGrid(defs, ctx) {
      const size = 20 / ctx.config.density;
      const pattern = texturePattern(defs, ctx, size);
      textureBase(pattern, ctx, size);
      pattern.append("path")
        .attr("d", `M${size / 2},0V${size}M0,${size / 2}H${size}M${size},0H0V${size}`)
        .attr("fill", "none")
        .attr("stroke", ctx.palette.roles.ink)
        .attr("stroke-width", Math.max(0.6, 1.25 / ctx.config.density))
        .attr("opacity", ctx.config.textureStrength);
      return pattern;
    },

    "d3-logo-diagonal-hatch": function renderDiagonalHatch(defs, ctx) {
      const size = 18 / ctx.config.density;
      const pattern = texturePattern(defs, ctx, size);
      textureBase(pattern, ctx, size);
      pattern.append("path")
        .attr("d", `M${-size / 3},${size}L${size},${-size / 3}M0,${size * 1.33}L${size * 1.33},0`)
        .attr("fill", "none")
        .attr("stroke", ctx.palette.roles.ink)
        .attr("stroke-width", Math.max(0.8, 1.7 / ctx.config.density))
        .attr("opacity", ctx.config.textureStrength);
      return pattern;
    },

    "d3-logo-crosshatch": function renderCrosshatch(defs, ctx) {
      const size = 21 / ctx.config.density;
      const pattern = texturePattern(defs, ctx, size);
      textureBase(pattern, ctx, size);
      pattern.selectAll("path")
        .data([
          `M${-size / 3},${size}L${size},${-size / 3}M0,${size * 1.33}L${size * 1.33},0`,
          `M0,${-size / 3}L${size * 1.33},${size}M${-size / 3},0L${size},${size * 1.33}`
        ])
        .join("path")
        .attr("d", (d) => d)
        .attr("fill", "none")
        .attr("stroke", ctx.palette.roles.ink)
        .attr("stroke-width", Math.max(0.55, 1.15 / ctx.config.density))
        .attr("opacity", ctx.config.textureStrength * 0.82);
      return pattern;
    },

    "d3-logo-halftone-dots": function renderHalftoneDots(defs, ctx) {
      const size = 24 / ctx.config.density;
      const pattern = texturePattern(defs, ctx, size);
      textureBase(pattern, ctx, size, ctx.palette.roles.surface);
      if (ctx.smallSize) {
        pattern.attr("data-flat-fallback", "true");
        pattern.select("rect").attr("fill", ctx.palette.roles.primary);
        return pattern;
      }
      const random = seededRandom(ctx.d3, ctx.config.seed, "halftone");
      const cells = [
        [size * 0.25, size * 0.25], [size * 0.75, size * 0.25],
        [size * 0.25, size * 0.75], [size * 0.75, size * 0.75]
      ].map((point, index) => ({ x: point[0], y: point[1], r: size * (0.08 + random() * 0.11 + index * 0.012) }));
      pattern.selectAll("circle")
        .data(cells)
        .join("circle")
        .attr("cx", (d) => d.x)
        .attr("cy", (d) => d.y)
        .attr("r", (d) => d.r)
        .attr("fill", ctx.palette.roles.primary)
        .attr("opacity", 0.45 + ctx.config.textureStrength * 0.55);
      return pattern;
    },

    "d3-logo-seeded-stipple": function renderSeededStipple(defs, ctx) {
      const size = 34 / ctx.config.density;
      const pattern = texturePattern(defs, ctx, size);
      textureBase(pattern, ctx, size);
      const random = seededRandom(ctx.d3, ctx.config.seed, "stipple");
      const count = Math.max(8, Math.round(15 * ctx.config.density));
      const points = ctx.d3.range(count).map(() => ({
        x: random() * size,
        y: random() * size,
        r: 0.55 + random() * 1.45
      }));
      pattern.selectAll("circle")
        .data(points)
        .join("circle")
        .attr("cx", (d) => d.x)
        .attr("cy", (d) => d.y)
        .attr("r", (d) => d.r)
        .attr("fill", ctx.palette.roles.ink)
        .attr("opacity", ctx.config.textureStrength);
      return pattern;
    },

    "d3-logo-topographic-lines": function renderTopographicLines(defs, ctx) {
      const size = 72 / ctx.config.density;
      const pattern = texturePattern(defs, ctx, size);
      pattern.attr("data-texture-mechanism", "nested-closed-isolines");
      textureBase(pattern, ctx, size, ctx.palette.roles.surface);
      const random = seededRandom(ctx.d3, ctx.config.seed, "topographic-closed-isolines");
      const clusters = [
        { cx: size * 0.28, cy: size * 0.34, radius: size * 0.31, levels: 5 },
        { cx: size * 0.78, cy: size * 0.78, radius: size * 0.25, levels: 4 },
        { cx: size * 0.94, cy: size * 0.18, radius: size * 0.19, levels: 3 }
      ];
      const contours = clusters.flatMap((cluster, clusterIndex) => ctx.d3.range(cluster.levels).map((level) => {
        const radius = cluster.radius * (1 - level * 0.155);
        const pointCount = 24;
        const phase = random() * Math.PI * 2;
        const points = ctx.d3.range(pointCount).map((index) => {
          const angle = phase + index / pointCount * Math.PI * 2;
          const harmonic = Math.sin(angle * (3 + clusterIndex) + phase) * 0.045 + Math.cos(angle * 5 - phase) * 0.025;
          const jitter = (random() - 0.5) * 0.045;
          const localRadius = radius * (1 + harmonic + jitter);
          const squash = 0.74 + clusterIndex * 0.08;
          return [
            cluster.cx + Math.cos(angle) * localRadius,
            cluster.cy + Math.sin(angle) * localRadius * squash
          ];
        });
        return { clusterIndex, level, points };
      }));
      const line = ctx.d3.line().curve(ctx.d3.curveCardinalClosed.tension(0.18 + ctx.config.curvature * 0.62));
      pattern.selectAll("path.topographic-isoline")
        .data(contours)
        .join("path")
        .attr("class", "topographic-isoline")
        .attr("data-isoline-closed", "true")
        .attr("data-contour-cluster", (d) => d.clusterIndex)
        .attr("data-contour-level", (d) => d.level)
        .attr("d", (d) => {
          const path = line(d.points);
          return /Z$/i.test(path) ? path : `${path}Z`;
        })
        .attr("fill", "none")
        .attr("stroke", (d) => d.level === 0 ? ctx.palette.roles.primary : ctx.palette.roles.ink)
        .attr("stroke-width", Math.max(0.55, 1.1 / ctx.config.density))
        .attr("opacity", (d) => 0.34 + ctx.config.textureStrength * (d.level === 0 ? 0.62 : 0.5));
      return pattern;
    },

    "d3-logo-voronoi-mosaic": function renderVoronoiMosaic(defs, ctx) {
      const size = 46 / ctx.config.density;
      const pattern = texturePattern(defs, ctx, size);
      const random = seededRandom(ctx.d3, ctx.config.seed, "texture-voronoi");
      const sites = ctx.d3.range(9).map(() => [random() * size, random() * size]);
      const voronoi = ctx.d3.Delaunay.from(sites).voronoi([0, 0, size, size]);
      const line = ctx.d3.line().curve(ctx.d3.curveLinearClosed);
      pattern.selectAll("path")
        .data(Array.from(voronoi.cellPolygons()))
        .join("path")
        .attr("d", line)
        .attr("fill", (d, index) => index === 0 ? ctx.textureFillFallback : ctx.palette.sequence[index % ctx.palette.sequence.length])
        .attr("stroke", ctx.palette.roles.background)
        .attr("stroke-width", 0.9)
        .attr("opacity", (d, index) => index === 0 ? 1 : 0.55 + ctx.config.textureStrength * 0.45);
      return pattern;
    },

    "d3-logo-guilloche-waves": function renderGuillocheWaves(defs, ctx) {
      const size = 58 / ctx.config.density;
      const pattern = texturePattern(defs, ctx, size);
      textureBase(pattern, ctx, size);
      const line = ctx.d3.line().curve(ctx.d3.curveBasis);
      const waves = ctx.d3.range(7).map((row) => ctx.d3.range(17).map((column) => {
        const x = column * size / 16;
        const y = size * (row + 0.5) / 7 + Math.sin(column * 0.85 + row * 0.72) * size * 0.075 * ctx.config.curvature;
        return [x, y];
      }));
      pattern.selectAll("path")
        .data(waves)
        .join("path")
        .attr("d", line)
        .attr("fill", "none")
        .attr("stroke", ctx.palette.roles.ink)
        .attr("stroke-width", 0.85)
        .attr("opacity", ctx.config.textureStrength);
      return pattern;
    },

    "d3-logo-woven-checker": function renderWovenChecker(defs, ctx) {
      const size = 32 / ctx.config.density;
      const pattern = texturePattern(defs, ctx, size);
      textureBase(pattern, ctx, size);
      const band = size / 4;
      pattern.selectAll("rect.vertical")
        .data([0, 2])
        .join("rect")
        .attr("class", "vertical")
        .attr("x", (d) => d * band)
        .attr("width", band)
        .attr("height", size)
        .attr("fill", ctx.palette.sequence[1 % ctx.palette.sequence.length])
        .attr("opacity", 0.4 + ctx.config.textureStrength * 0.6);
      pattern.selectAll("rect.horizontal")
        .data([0, 2])
        .join("rect")
        .attr("class", "horizontal")
        .attr("y", (d) => d * band)
        .attr("width", size)
        .attr("height", band)
        .attr("fill", ctx.palette.roles.ink)
        .attr("opacity", 0.35 + ctx.config.textureStrength * 0.55);
      pattern.selectAll("rect.over")
        .data([[0, 0], [2, 2]])
        .join("rect")
        .attr("class", "over")
        .attr("x", (d) => d[0] * band)
        .attr("y", (d) => d[1] * band)
        .attr("width", band)
        .attr("height", band)
        .attr("fill", ctx.palette.roles.primary);
      return pattern;
    },

    "d3-logo-directional-fibers": function renderDirectionalFibers(defs, ctx) {
      const size = 42 / ctx.config.density;
      const pattern = texturePattern(defs, ctx, size);
      textureBase(pattern, ctx, size);
      const random = seededRandom(ctx.d3, ctx.config.seed, "fibers");
      const count = Math.max(9, Math.round(17 * ctx.config.density));
      const fibers = ctx.d3.range(count).map(() => {
        const x = random() * size;
        const y = random() * size;
        const length = size * (0.2 + random() * 0.42);
        return { x1: x, y1: y, x2: x + length, y2: y + length * (0.14 + ctx.config.curvature * 0.28) };
      });
      pattern.selectAll("line")
        .data(fibers)
        .join("line")
        .attr("x1", (d) => d.x1)
        .attr("y1", (d) => d.y1)
        .attr("x2", (d) => d.x2)
        .attr("y2", (d) => d.y2)
        .attr("stroke", ctx.palette.roles.ink)
        .attr("stroke-width", 1)
        .attr("opacity", ctx.config.textureStrength);
      return pattern;
    },

    "d3-logo-hex-cell-lattice": function renderHexCellLattice(defs, ctx) {
      const size = 58 / ctx.config.density;
      const pattern = texturePattern(defs, ctx, size);
      textureBase(pattern, ctx, size, ctx.palette.roles.surface);
      const radius = size / 5;
      const centers = [[0, size / 2], [size * 0.3, 0], [size * 0.3, size], [size * 0.6, size / 2], [size * 0.9, 0], [size * 0.9, size]];
      const points = ([cx, cy]) => ctx.d3.range(6).map((index) => {
        const angle = Math.PI / 3 * index;
        return `${cx + Math.cos(angle) * radius},${cy + Math.sin(angle) * radius}`;
      }).join(" ");
      pattern.selectAll("polygon")
        .data(centers)
        .join("polygon")
        .attr("points", points)
        .attr("fill", (d, index) => index % 3 === 1 ? ctx.palette.roles.primary : "none")
        .attr("fill-opacity", ctx.config.textureStrength * 0.28)
        .attr("stroke", ctx.palette.roles.ink)
        .attr("stroke-width", Math.max(0.7, 1.45 / ctx.config.density))
        .attr("opacity", 0.45 + ctx.config.textureStrength * 0.55);
      return pattern;
    },

    "d3-logo-triangle-flip-tiles": function renderTriangleFlipTiles(defs, ctx) {
      const size = 48 / ctx.config.density;
      const pattern = texturePattern(defs, ctx, size);
      textureBase(pattern, ctx, size, ctx.palette.roles.surface);
      const half = size / 2;
      const triangles = [
        [[0, 0], [half, 0], [0, half]], [[half, 0], [half, half], [0, half]],
        [[half, 0], [size, 0], [size, half]], [[half, 0], [size, half], [half, half]],
        [[0, half], [half, half], [half, size]], [[0, half], [half, size], [0, size]],
        [[half, half], [size, half], [half, size]], [[size, half], [size, size], [half, size]]
      ];
      pattern.selectAll("polygon")
        .data(triangles)
        .join("polygon")
        .attr("points", (d) => d.map((point) => point.join(",")).join(" "))
        .attr("fill", (d, index) => ctx.palette.sequence[index % ctx.palette.sequence.length])
        .attr("stroke", ctx.palette.roles.background)
        .attr("stroke-width", 0.65)
        .attr("opacity", 0.5 + ctx.config.textureStrength * 0.5);
      return pattern;
    },

    "d3-logo-truchet-arc-links": function renderTruchetArcLinks(defs, ctx) {
      const size = 64 / ctx.config.density;
      const pattern = texturePattern(defs, ctx, size);
      textureBase(pattern, ctx, size, ctx.palette.roles.surface);
      const cell = size / 2;
      const radius = cell / 2;
      const random = seededRandom(ctx.d3, ctx.config.seed, "truchet-arc-links");
      const paths = [];
      for (let row = 0; row < 2; row += 1) {
        for (let column = 0; column < 2; column += 1) {
          const x = column * cell;
          const y = row * cell;
          if (random() < 0.5) {
            paths.push(`M${x + radius},${y}A${radius},${radius} 0 0 0 ${x},${y + radius}`);
            paths.push(`M${x + cell},${y + radius}A${radius},${radius} 0 0 0 ${x + radius},${y + cell}`);
          } else {
            paths.push(`M${x + radius},${y}A${radius},${radius} 0 0 1 ${x + cell},${y + radius}`);
            paths.push(`M${x},${y + radius}A${radius},${radius} 0 0 1 ${x + radius},${y + cell}`);
          }
        }
      }
      pattern.selectAll("path")
        .data(paths)
        .join("path")
        .attr("d", (d) => d)
        .attr("fill", "none")
        .attr("stroke", ctx.palette.roles.primary)
        .attr("stroke-width", Math.max(1.4, 3 / ctx.config.density))
        .attr("stroke-linecap", "round")
        .attr("opacity", 0.42 + ctx.config.textureStrength * 0.58);
      return pattern;
    },

    "d3-logo-houndstooth-blocks": function renderHoundstoothBlocks(defs, ctx) {
      const size = 60 / ctx.config.density;
      const pattern = texturePattern(defs, ctx, size);
      textureBase(pattern, ctx, size, ctx.palette.roles.surface);
      const module = size / 2;
      const motif = [[0, 0], [module * 0.58, 0], [module * 0.58, module * 0.22], [module, module * 0.22], [module * 0.72, module * 0.5], [module, module * 0.78], [module * 0.58, module * 0.78], [module * 0.58, module], [0, module], [module * 0.28, module * 0.5]];
      const placements = [[0, 0], [module, module], [-module / 2, module], [module / 2, 0]];
      pattern.selectAll("polygon")
        .data(placements)
        .join("polygon")
        .attr("points", ([dx, dy]) => motif.map(([x, y]) => `${x + dx},${y + dy}`).join(" "))
        .attr("fill", (d, index) => index % 2 ? ctx.palette.roles.ink : ctx.palette.roles.primary)
        .attr("opacity", 0.52 + ctx.config.textureStrength * 0.48);
      return pattern;
    },

    "d3-logo-argyle-diamonds": function renderArgyleDiamonds(defs, ctx) {
      const size = 72 / ctx.config.density;
      const pattern = texturePattern(defs, ctx, size);
      textureBase(pattern, ctx, size, ctx.palette.roles.surface);
      const diamonds = [[size / 2, size / 2], [0, 0], [size, 0], [0, size], [size, size]];
      pattern.selectAll("polygon")
        .data(diamonds)
        .join("polygon")
        .attr("points", ([cx, cy]) => `${cx},${cy - size * 0.28} ${cx + size * 0.23},${cy} ${cx},${cy + size * 0.28} ${cx - size * 0.23},${cy}`)
        .attr("fill", (d, index) => ctx.palette.sequence[index % ctx.palette.sequence.length])
        .attr("opacity", 0.38 + ctx.config.textureStrength * 0.5);
      pattern.selectAll("path.argyle-seam")
        .data([`M0,${size * 0.22}L${size},${size * 0.78}`, `M0,${size * 0.78}L${size},${size * 0.22}`])
        .join("path")
        .attr("class", "argyle-seam")
        .attr("d", (d) => d)
        .attr("fill", "none")
        .attr("stroke", ctx.palette.roles.ink)
        .attr("stroke-width", 1.15)
        .attr("stroke-dasharray", "5 3")
        .attr("opacity", ctx.config.textureStrength);
      return pattern;
    },

    "d3-logo-running-brick-bond": function renderRunningBrickBond(defs, ctx) {
      const size = 72 / ctx.config.density;
      const pattern = texturePattern(defs, ctx, size);
      textureBase(pattern, ctx, size, ctx.palette.roles.background);
      const rowHeight = size / 3;
      const brickWidth = size / 2;
      const bricks = ctx.d3.range(3).flatMap((row) => ctx.d3.range(-1, 3).map((column) => ({
        x: column * brickWidth + (row % 2 ? brickWidth / 2 : 0),
        y: row * rowHeight,
        row,
        column
      })));
      pattern.selectAll("rect.brick")
        .data(bricks)
        .join("rect")
        .attr("class", "brick")
        .attr("x", (d) => d.x + 1)
        .attr("y", (d) => d.y + 1)
        .attr("width", brickWidth - 2)
        .attr("height", rowHeight - 2)
        .attr("fill", (d) => ctx.palette.sequence[(d.row + d.column + 12) % ctx.palette.sequence.length])
        .attr("opacity", 0.45 + ctx.config.textureStrength * 0.55);
      return pattern;
    },

    "d3-logo-isometric-cube-tiles": function renderIsometricCubeTiles(defs, ctx) {
      const size = 64 / ctx.config.density;
      const pattern = texturePattern(defs, ctx, size);
      textureBase(pattern, ctx, size, ctx.palette.roles.surface);
      const cubeFaces = (cx, cy, radius) => {
        const top = [[cx, cy - radius], [cx + radius, cy - radius / 2], [cx, cy], [cx - radius, cy - radius / 2]];
        const left = [[cx - radius, cy - radius / 2], [cx, cy], [cx, cy + radius], [cx - radius, cy + radius / 2]];
        const right = [[cx, cy], [cx + radius, cy - radius / 2], [cx + radius, cy + radius / 2], [cx, cy + radius]];
        return [top, left, right];
      };
      const faces = [...cubeFaces(size * 0.25, size * 0.3, size * 0.2), ...cubeFaces(size * 0.75, size * 0.8, size * 0.2)];
      pattern.selectAll("polygon")
        .data(faces)
        .join("polygon")
        .attr("points", (d) => d.map((point) => point.join(",")).join(" "))
        .attr("fill", (d, index) => ctx.palette.sequence[index % 3])
        .attr("stroke", ctx.palette.roles.background)
        .attr("stroke-width", 0.8)
        .attr("opacity", 0.52 + ctx.config.textureStrength * 0.48);
      return pattern;
    },

    "d3-logo-greek-key-meander": function renderGreekKeyMeander(defs, ctx) {
      const size = 64 / ctx.config.density;
      const pattern = texturePattern(defs, ctx, size);
      textureBase(pattern, ctx, size);
      const paths = [
        `M0,${size * 0.25}H${size * 0.75}V${size * 0.75}H${size * 0.25}V${size * 0.5}H${size * 0.55}V${size * 0.25}H${size}`,
        `M0,${size * 0.75}H${size * 0.25}V${size * 0.5}`
      ];
      pattern.selectAll("path")
        .data(paths)
        .join("path")
        .attr("d", (d) => d)
        .attr("fill", "none")
        .attr("stroke", ctx.palette.roles.ink)
        .attr("stroke-width", Math.max(1.4, 2.8 / ctx.config.density))
        .attr("stroke-linejoin", "miter")
        .attr("opacity", 0.42 + ctx.config.textureStrength * 0.58);
      return pattern;
    },

    "d3-logo-chainmail-rings": function renderChainmailRings(defs, ctx) {
      const size = 60 / ctx.config.density;
      const pattern = texturePattern(defs, ctx, size);
      pattern.attr("data-texture-mechanism", "alternating-under-over-ring-crossings");
      textureBase(pattern, ctx, size, ctx.palette.roles.surface);
      const radius = size * 0.22;
      const rings = [
        { cx: size * 0.2, cy: size * 0.28, row: 0, column: 0 },
        { cx: size * 0.7, cy: size * 0.28, row: 0, column: 1 },
        { cx: size * 0.45, cy: size * 0.74, row: 1, column: 0 },
        { cx: size * 0.95, cy: size * 0.74, row: 1, column: 1 }
      ].map((ring) => ({ ...ring, parity: (ring.row + ring.column) % 2 }));
      pattern.selectAll("circle.chainmail-under-ring")
        .data(rings)
        .join("circle")
        .attr("class", "chainmail-under-ring")
        .attr("data-crossing-parity", (d) => d.parity)
        .attr("cx", (d) => d.cx)
        .attr("cy", (d) => d.cy)
        .attr("r", radius)
        .attr("fill", "none")
        .attr("stroke", ctx.palette.roles.primary)
        .attr("stroke-width", Math.max(2, 4 / ctx.config.density))
        .attr("opacity", 0.4 + ctx.config.textureStrength * 0.6);
      const crossings = rings.map((ring) => ({
        ...ring,
        d: ring.parity === 0
          ? `M${ring.cx - radius},${ring.cy}A${radius},${radius} 0 0 1 ${ring.cx + radius},${ring.cy}`
          : `M${ring.cx + radius},${ring.cy}A${radius},${radius} 0 0 1 ${ring.cx - radius},${ring.cy}`
      }));
      pattern.selectAll("path.chainmail-crossing-cover")
        .data(crossings)
        .join("path")
        .attr("class", "chainmail-crossing-cover")
        .attr("data-crossing-parity", (d) => d.parity)
        .attr("d", (d) => d.d)
        .attr("fill", "none")
        .attr("stroke", ctx.palette.roles.surface)
        .attr("stroke-width", Math.max(4.6, 7.2 / ctx.config.density))
        .attr("stroke-linecap", "round");
      pattern.selectAll("path.chainmail-over-arc")
        .data(crossings)
        .join("path")
        .attr("class", "chainmail-over-arc")
        .attr("data-crossing-parity", (d) => d.parity)
        .attr("d", (d) => d.d)
        .attr("fill", "none")
        .attr("stroke", (d) => d.parity ? ctx.palette.roles.ink : ctx.palette.roles.primaryDark)
        .attr("stroke-width", Math.max(2, 4 / ctx.config.density))
        .attr("stroke-linecap", "round")
        .attr("opacity", 0.48 + ctx.config.textureStrength * 0.52);
      return pattern;
    },

    "d3-logo-seigaiha-fans": function renderSeigaihaFans(defs, ctx) {
      const size = 64 / ctx.config.density;
      const pattern = texturePattern(defs, ctx, size);
      textureBase(pattern, ctx, size);
      const centers = [[0, size * 0.45], [size / 2, size * 0.45], [size, size * 0.45], [size / 4, size], [size * 0.75, size]];
      const arcs = centers.flatMap(([cx, cy]) => ctx.d3.range(1, 5).map((ring) => {
        const radius = size * 0.07 * ring;
        return `M${cx - radius},${cy}A${radius},${radius} 0 0 1 ${cx + radius},${cy}`;
      }));
      pattern.selectAll("path")
        .data(arcs)
        .join("path")
        .attr("d", (d) => d)
        .attr("fill", "none")
        .attr("stroke", ctx.palette.roles.ink)
        .attr("stroke-width", Math.max(0.65, 1.25 / ctx.config.density))
        .attr("opacity", 0.38 + ctx.config.textureStrength * 0.62);
      return pattern;
    },

    "d3-logo-knit-v-loops": function renderKnitVLoops(defs, ctx) {
      const size = 56 / ctx.config.density;
      const pattern = texturePattern(defs, ctx, size);
      const tension = 0.18 + ctx.config.curvature * 0.7;
      pattern
        .attr("data-texture-mechanism", "alternating-knit-loop-crossings")
        .attr("data-loop-tension", tension.toFixed(4));
      textureBase(pattern, ctx, size, ctx.palette.roles.surface);
      const pitch = size / 3;
      const drop = pitch * (0.58 + tension * 0.25);
      const stitches = ctx.d3.range(-1, 4).flatMap((row) => ctx.d3.range(-1, 4).map((column) => {
        const x = column * pitch + (row % 2 ? pitch / 2 : 0);
        const y = row * pitch * 0.72;
        const handle = pitch * (0.16 + tension * 0.16);
        return {
          row,
          column,
          x,
          y,
          parity: (row + column + 10) % 2,
          d: `M${x - pitch * 0.36},${y}C${x - pitch * 0.32 + handle},${y + drop * 0.55} ${x - handle},${y + drop * 0.92} ${x},${y + drop}C${x + handle},${y + drop * 0.92} ${x + pitch * 0.32 - handle},${y + drop * 0.55} ${x + pitch * 0.36},${y}`
        };
      }));
      const strokeWidth = Math.max(1.2, 2.35 / ctx.config.density);
      pattern.selectAll("path.knit-loop-under")
        .data(stitches)
        .join("path")
        .attr("class", "knit-loop-under")
        .attr("data-crossing-parity", (d) => d.parity)
        .attr("d", (d) => d.d)
        .attr("fill", "none")
        .attr("stroke", ctx.palette.roles.primary)
        .attr("stroke-width", strokeWidth)
        .attr("stroke-linecap", "round")
        .attr("opacity", 0.4 + ctx.config.textureStrength * 0.6);
      const bridges = stitches.map((stitch) => {
        const cx = stitch.x;
        const cy = stitch.y + drop * 0.57;
        const half = pitch * 0.13;
        const rise = pitch * (0.08 + tension * 0.05);
        return {
          ...stitch,
          bridge: stitch.parity === 0
            ? `M${cx - half},${cy + rise}Q${cx},${cy - rise} ${cx + half},${cy - rise}`
            : `M${cx - half},${cy - rise}Q${cx},${cy + rise} ${cx + half},${cy + rise}`
        };
      });
      pattern.selectAll("path.knit-crossing-cover")
        .data(bridges)
        .join("path")
        .attr("class", "knit-crossing-cover")
        .attr("data-crossing-parity", (d) => d.parity)
        .attr("d", (d) => d.bridge)
        .attr("fill", "none")
        .attr("stroke", ctx.palette.roles.surface)
        .attr("stroke-width", strokeWidth + Math.max(2.4, 3.8 / ctx.config.density))
        .attr("stroke-linecap", "round");
      pattern.selectAll("path.knit-loop-over-bridge")
        .data(bridges)
        .join("path")
        .attr("class", "knit-loop-over-bridge")
        .attr("data-crossing-parity", (d) => d.parity)
        .attr("d", (d) => d.bridge)
        .attr("fill", "none")
        .attr("stroke", (d) => d.parity ? ctx.palette.roles.ink : ctx.palette.roles.primaryDark)
        .attr("stroke-width", strokeWidth)
        .attr("stroke-linecap", "round")
        .attr("opacity", 0.48 + ctx.config.textureStrength * 0.52);
      return pattern;
    },

    "d3-logo-pinwheel-quilt": function renderPinwheelQuilt(defs, ctx) {
      const size = 64 / ctx.config.density;
      const pattern = texturePattern(defs, ctx, size);
      textureBase(pattern, ctx, size, ctx.palette.roles.surface);
      const centers = [[size / 2, size / 2], [0, 0], [size, size]];
      const triangles = centers.flatMap(([cx, cy]) => {
        const radius = size * 0.28;
        return ctx.d3.range(4).map((index) => {
          const angle = index * Math.PI / 2;
          const point = (offset, distance) => [cx + Math.cos(angle + offset) * distance, cy + Math.sin(angle + offset) * distance];
          return [[cx, cy], point(-Math.PI / 4, radius), point(Math.PI / 4, radius * 0.38)];
        });
      });
      pattern.selectAll("polygon")
        .data(triangles)
        .join("polygon")
        .attr("points", (d) => d.map((point) => point.join(",")).join(" "))
        .attr("fill", (d, index) => ctx.palette.sequence[index % ctx.palette.sequence.length])
        .attr("stroke", ctx.palette.roles.background)
        .attr("stroke-width", 0.8)
        .attr("opacity", 0.45 + ctx.config.textureStrength * 0.55);
      return pattern;
    },

    "d3-logo-star-kite-lattice": function renderStarKiteLattice(defs, ctx) {
      const size = 68 / ctx.config.density;
      const pattern = texturePattern(defs, ctx, size);
      textureBase(pattern, ctx, size, ctx.palette.roles.surface);
      const cx = size / 2;
      const cy = size / 2;
      const star = ctx.d3.range(16).map((index) => {
        const angle = -Math.PI / 2 + index * Math.PI / 8;
        const radius = index % 2 ? size * 0.14 : size * 0.3;
        return [cx + Math.cos(angle) * radius, cy + Math.sin(angle) * radius];
      });
      pattern.append("polygon")
        .attr("points", star.map((point) => point.join(",")).join(" "))
        .attr("fill", ctx.palette.roles.primary)
        .attr("stroke", ctx.palette.roles.ink)
        .attr("stroke-width", 1)
        .attr("opacity", 0.48 + ctx.config.textureStrength * 0.52);
      const kites = ctx.d3.range(8).map((index) => {
        const angle = index * Math.PI / 4;
        const radial = (distance, offset = 0) => [cx + Math.cos(angle + offset) * distance, cy + Math.sin(angle + offset) * distance];
        return [radial(size * 0.31), radial(size * 0.49, -Math.PI / 12), radial(size * 0.6), radial(size * 0.49, Math.PI / 12)];
      });
      pattern.selectAll("polygon.kite")
        .data(kites)
        .join("polygon")
        .attr("class", "kite")
        .attr("points", (d) => d.map((point) => point.join(",")).join(" "))
        .attr("fill", (d, index) => ctx.palette.sequence[(index + 1) % ctx.palette.sequence.length])
        .attr("stroke", ctx.palette.roles.background)
        .attr("stroke-width", 0.7)
        .attr("opacity", ctx.config.textureStrength * 0.72);
      return pattern;
    },

    "d3-logo-chevron-bands": function renderChevronBands(defs, ctx) {
      const size = 64 / ctx.config.density;
      const pattern = texturePattern(defs, ctx, size);
      textureBase(pattern, ctx, size, ctx.palette.roles.surface);
      const band = size * 0.17;
      const depth = size * (0.16 + ctx.config.curvature * 0.08);
      const chevron = (centerY) => [
        [-size * 0.1, centerY - band], [size * 0.25, centerY + depth - band], [size * 0.5, centerY - band], [size * 0.75, centerY + depth - band], [size * 1.1, centerY - band],
        [size * 1.1, centerY], [size * 0.75, centerY + depth], [size * 0.5, centerY], [size * 0.25, centerY + depth], [-size * 0.1, centerY]
      ];
      pattern.selectAll("polygon")
        .data([chevron(size * 0.2), chevron(size * 0.72)])
        .join("polygon")
        .attr("points", (d) => d.map((point) => point.join(",")).join(" "))
        .attr("fill", (d, index) => index ? ctx.palette.roles.ink : ctx.palette.roles.primary)
        .attr("opacity", 0.42 + ctx.config.textureStrength * 0.58);
      return pattern;
    },

    "d3-logo-pixel-staircase": function renderPixelStaircase(defs, ctx) {
      const size = 48 / ctx.config.density;
      const pattern = texturePattern(defs, ctx, size);
      textureBase(pattern, ctx, size, ctx.palette.roles.surface);
      const cell = size / 8;
      const pixels = ctx.d3.range(8).flatMap((row) => ctx.d3.range(8).flatMap((column) => {
        const phase = (column - row + 16) % 6;
        return phase < 2 ? [{ row, column, phase }] : [];
      }));
      pattern.selectAll("rect.pixel")
        .data(pixels)
        .join("rect")
        .attr("class", "pixel")
        .attr("x", (d) => d.column * cell)
        .attr("y", (d) => d.row * cell)
        .attr("width", cell)
        .attr("height", cell)
        .attr("fill", (d) => d.phase ? ctx.palette.roles.ink : ctx.palette.roles.primary)
        .attr("opacity", 0.44 + ctx.config.textureStrength * 0.56);
      return pattern;
    },

    "d3-logo-terrazzo-chips": function renderTerrazzoChips(defs, ctx) {
      const size = 72 / ctx.config.density;
      const pattern = texturePattern(defs, ctx, size);
      textureBase(pattern, ctx, size, ctx.palette.roles.surface);
      const random = seededRandom(ctx.d3, ctx.config.seed, "terrazzo-chips");
      const chips = ctx.d3.range(Math.max(10, Math.round(16 * ctx.config.density))).map((index) => {
        const cx = random() * size;
        const cy = random() * size;
        const radius = size * (0.025 + random() * 0.07);
        const sides = 3 + Math.floor(random() * 4);
        const angleOffset = random() * Math.PI * 2;
        const points = ctx.d3.range(sides).map((side) => {
          const angle = angleOffset + side / sides * Math.PI * 2;
          const localRadius = radius * (0.65 + random() * 0.7);
          return [cx + Math.cos(angle) * localRadius, cy + Math.sin(angle) * localRadius];
        });
        return { points, index };
      });
      const line = ctx.d3.line().curve(ctx.d3.curveLinearClosed);
      pattern.selectAll("path.chip")
        .data(chips)
        .join("path")
        .attr("class", "chip")
        .attr("d", (d) => line(d.points))
        .attr("fill", (d) => ctx.palette.sequence[d.index % ctx.palette.sequence.length])
        .attr("opacity", 0.4 + ctx.config.textureStrength * 0.6);
      return pattern;
    },

    "d3-logo-linocut-gouges": function renderLinocutGouges(defs, ctx) {
      const size = 68 / ctx.config.density;
      const pattern = texturePattern(defs, ctx, size);
      textureBase(pattern, ctx, size, ctx.palette.roles.ink);
      const random = seededRandom(ctx.d3, ctx.config.seed, "linocut-gouges");
      const gouges = ctx.d3.range(Math.max(8, Math.round(13 * ctx.config.density))).map(() => {
        const x = random() * size;
        const y = random() * size;
        const length = size * (0.14 + random() * 0.28);
        const angle = -0.55 + random() * 1.1;
        const ex = x + Math.cos(angle) * length;
        const ey = y + Math.sin(angle) * length;
        const nx = -Math.sin(angle);
        const ny = Math.cos(angle);
        const bow = length * (0.08 + ctx.config.curvature * 0.14) * (random() < 0.5 ? -1 : 1);
        const mx = (x + ex) / 2 + nx * bow;
        const my = (y + ey) / 2 + ny * bow;
        const taper = 0.8 + random() * 1.8;
        return `M${x},${y}Q${mx + nx * taper},${my + ny * taper} ${ex},${ey}Q${mx - nx * taper * 0.45},${my - ny * taper * 0.45} ${x},${y}Z`;
      });
      pattern.selectAll("path.gouge")
        .data(gouges)
        .join("path")
        .attr("class", "gouge")
        .attr("d", (d) => d)
        .attr("fill", ctx.palette.roles.surface)
        .attr("opacity", 0.36 + ctx.config.textureStrength * 0.64);
      return pattern;
    },

    "d3-logo-letterpress-slippage": function renderLetterpressSlippage(defs, ctx) {
      const size = 64 / ctx.config.density;
      const pattern = texturePattern(defs, ctx, size);
      pattern.attr("data-texture-mechanism", "offset-type-slug-registration");
      textureBase(pattern, ctx, size, ctx.palette.roles.surface);
      const stamps = [
        { cx: size * 0.24, cy: size * 0.25, index: 0 },
        { cx: size * 0.72, cy: size * 0.25, index: 1 },
        { cx: size * 0.24, cy: size * 0.75, index: 2 },
        { cx: size * 0.72, cy: size * 0.75, index: 3 }
      ];
      const stampWidth = size * 0.27;
      const stampHeight = size * 0.31;
      const capHeight = stampHeight * 0.3;
      const stemWidth = stampWidth * 0.34;
      const typeSlugPoints = (stamp, dx, dy) => {
        const left = stamp.cx - stampWidth / 2 + dx;
        const right = stamp.cx + stampWidth / 2 + dx;
        const top = stamp.cy - stampHeight / 2 + dy;
        const bottom = stamp.cy + stampHeight / 2 + dy;
        const stemLeft = stamp.cx - stemWidth / 2 + dx;
        const stemRight = stamp.cx + stemWidth / 2 + dx;
        return [
          [left, top], [right, top], [right, top + capHeight], [stemRight, top + capHeight],
          [stemRight, bottom], [stemLeft, bottom], [stemLeft, top + capHeight], [left, top + capHeight]
        ].map((point) => point.join(",")).join(" ");
      };
      pattern.selectAll("polygon.letterpress-first-impression")
        .data(stamps)
        .join("polygon")
        .attr("class", "letterpress-stamp letterpress-first-impression")
        .attr("data-registration-impression", "first")
        .attr("data-stamp-shape", "type-slug")
        .attr("data-stamp-index", (d) => d.index)
        .attr("points", (d) => typeSlugPoints(d, -2.2, -1.4))
        .attr("fill", ctx.palette.roles.primary)
        .attr("opacity", 0.34 + ctx.config.textureStrength * 0.42);
      pattern.selectAll("polygon.letterpress-offset-impression")
        .data(stamps)
        .join("polygon")
        .attr("class", "letterpress-stamp letterpress-offset-impression")
        .attr("data-registration-impression", "offset")
        .attr("data-stamp-shape", "type-slug")
        .attr("data-stamp-index", (d) => d.index)
        .attr("points", (d) => typeSlugPoints(d, 2.4, 1.7))
        .attr("fill", ctx.palette.roles.ink)
        .attr("opacity", 0.24 + ctx.config.textureStrength * 0.5);
      return pattern;
    },

    "d3-logo-dry-roller-bands": function renderDryRollerBands(defs, ctx) {
      const size = 72 / ctx.config.density;
      const pattern = texturePattern(defs, ctx, size);
      textureBase(pattern, ctx, size, ctx.palette.roles.surface);
      const random = seededRandom(ctx.d3, ctx.config.seed, "dry-roller-bands");
      const segments = [];
      for (let row = 0; row < 4; row += 1) {
        let x = -size * 0.05;
        while (x < size) {
          const gap = size * (0.018 + random() * 0.07);
          const width = size * (0.07 + random() * 0.2);
          x += gap;
          segments.push({ x, y: row * size / 4 + random() * size * 0.035, width, row });
          x += width;
        }
      }
      pattern.selectAll("rect.ink-run")
        .data(segments)
        .join("rect")
        .attr("class", "ink-run")
        .attr("x", (d) => d.x)
        .attr("y", (d) => d.y)
        .attr("width", (d) => d.width)
        .attr("height", size * (0.1 + random() * 0.06))
        .attr("fill", (d) => d.row % 2 ? ctx.palette.roles.ink : ctx.palette.roles.primary)
        .attr("opacity", 0.36 + ctx.config.textureStrength * 0.64);
      return pattern;
    },

    "d3-logo-embossed-lozenges": function renderEmbossedLozenges(defs, ctx) {
      const size = 64 / ctx.config.density;
      const pattern = texturePattern(defs, ctx, size);
      pattern.attr("data-texture-mechanism", "faceted-lozenge-relief");
      textureBase(pattern, ctx, size, ctx.palette.roles.surface);
      const centers = [[size * 0.25, size * 0.25], [size * 0.75, size * 0.75], [size * 0.75, size * 0.25], [size * 0.25, size * 0.75]];
      const radius = size * 0.17;
      const lozenges = centers.map(([cx, cy], index) => {
        const outer = {
          top: [cx, cy - radius], right: [cx + radius * 0.74, cy],
          bottom: [cx, cy + radius], left: [cx - radius * 0.74, cy]
        };
        const innerRadius = radius * 0.58;
        const inner = {
          top: [cx, cy - innerRadius], right: [cx + innerRadius * 0.74, cy],
          bottom: [cx, cy + innerRadius], left: [cx - innerRadius * 0.74, cy]
        };
        return { index, outer, inner };
      });
      const facets = lozenges.flatMap((lozenge) => [
        { ...lozenge, tone: "light", side: "top-right", points: [lozenge.outer.top, lozenge.outer.right, lozenge.inner.right, lozenge.inner.top] },
        { ...lozenge, tone: "light", side: "top-left", points: [lozenge.outer.left, lozenge.outer.top, lozenge.inner.top, lozenge.inner.left] },
        { ...lozenge, tone: "dark", side: "bottom-right", points: [lozenge.outer.right, lozenge.outer.bottom, lozenge.inner.bottom, lozenge.inner.right] },
        { ...lozenge, tone: "dark", side: "bottom-left", points: [lozenge.outer.bottom, lozenge.outer.left, lozenge.inner.left, lozenge.inner.bottom] }
      ]);
      pattern.selectAll("polygon.embossed-bevel-facet")
        .data(facets)
        .join("polygon")
        .attr("class", (d) => `embossed-bevel-facet embossed-bevel-${d.tone}`)
        .attr("data-bevel-tone", (d) => d.tone)
        .attr("data-bevel-side", (d) => d.side)
        .attr("data-lozenge-index", (d) => d.index)
        .attr("points", (d) => d.points.map((point) => point.join(",")).join(" "))
        .attr("fill", (d) => d.tone === "light" ? ctx.palette.roles.quiet : ctx.palette.roles.primaryDark)
        .attr("stroke", ctx.palette.roles.ink)
        .attr("stroke-width", 0.35)
        .attr("opacity", 0.48 + ctx.config.textureStrength * 0.48);
      pattern.selectAll("polygon.embossed-center")
        .data(lozenges)
        .join("polygon")
        .attr("class", "embossed-center")
        .attr("data-lozenge-index", (d) => d.index)
        .attr("points", (d) => [d.inner.top, d.inner.right, d.inner.bottom, d.inner.left].map((point) => point.join(",")).join(" "))
        .attr("fill", ctx.palette.roles.primary)
        .attr("stroke", ctx.palette.roles.ink)
        .attr("stroke-width", 0.65)
        .attr("opacity", 0.52 + ctx.config.textureStrength * 0.48);
      return pattern;
    },

    "d3-logo-camouflage-islands": function renderCamouflageIslands(defs, ctx) {
      const size = 76 / ctx.config.density;
      const pattern = texturePattern(defs, ctx, size);
      textureBase(pattern, ctx, size, ctx.palette.roles.surface);
      const random = seededRandom(ctx.d3, ctx.config.seed, "camouflage-islands");
      const islands = ctx.d3.range(Math.max(7, Math.round(10 * ctx.config.density))).map((index) => {
        const cx = random() * size;
        const cy = random() * size;
        const lobes = 7 + Math.floor(random() * 5);
        const baseRadius = size * (0.09 + random() * 0.13);
        const points = ctx.d3.range(lobes).map((lobe) => {
          const angle = lobe / lobes * Math.PI * 2;
          const radius = baseRadius * (0.65 + random() * 0.55);
          return [cx + Math.cos(angle) * radius, cy + Math.sin(angle) * radius];
        });
        return { points, index };
      });
      const line = ctx.d3.line().curve(ctx.d3.curveBasisClosed);
      pattern.selectAll("path.island")
        .data(islands)
        .join("path")
        .attr("class", "island")
        .attr("d", (d) => line(d.points))
        .attr("fill", (d) => ctx.palette.sequence[d.index % ctx.palette.sequence.length])
        .attr("opacity", 0.38 + ctx.config.textureStrength * 0.62);
      return pattern;
    },

    "d3-logo-leaf-vein-repeat": function renderLeafVeinRepeat(defs, ctx) {
      const size = 72 / ctx.config.density;
      const pattern = texturePattern(defs, ctx, size);
      textureBase(pattern, ctx, size, ctx.palette.roles.surface);
      const leaves = [[size * 0.25, size * 0.28, -18], [size * 0.72, size * 0.72, 22], [size * 0.82, size * 0.12, 35], [size * 0.12, size * 0.85, -32]];
      const groups = pattern.selectAll("g.leaf")
        .data(leaves)
        .join("g")
        .attr("class", "leaf")
        .attr("transform", (d) => `translate(${d[0]},${d[1]}) rotate(${d[2]})`);
      const leafLength = size * 0.32;
      const leafWidth = size * 0.12;
      groups.append("path")
        .attr("d", `M${-leafLength / 2},0C${-leafLength * 0.18},${-leafWidth} ${leafLength * 0.18},${-leafWidth} ${leafLength / 2},0C${leafLength * 0.18},${leafWidth} ${-leafLength * 0.18},${leafWidth} ${-leafLength / 2},0Z`)
        .attr("fill", ctx.palette.roles.primary)
        .attr("opacity", 0.34 + ctx.config.textureStrength * 0.54);
      groups.append("line")
        .attr("x1", -leafLength / 2).attr("x2", leafLength / 2)
        .attr("stroke", ctx.palette.roles.ink).attr("stroke-width", 1);
      const veinFractions = [-0.28, -0.12, 0.04, 0.2, 0.36];
      groups.selectAll("path.vein")
        .data(veinFractions)
        .join("path")
        .attr("class", "vein")
        .attr("d", (fraction) => {
          const x = fraction * leafLength;
          const reach = leafWidth * (0.78 - Math.abs(fraction) * 0.7);
          return `M${x},0L${x + leafLength * 0.08},${-reach}M${x},0L${x + leafLength * 0.08},${reach}`;
        })
        .attr("fill", "none")
        .attr("stroke", ctx.palette.roles.ink)
        .attr("stroke-width", 0.65)
        .attr("opacity", ctx.config.textureStrength);
      return pattern;
    },

    "d3-logo-pinecone-scales": function renderPineconeScales(defs, ctx) {
      const size = 60 / ctx.config.density;
      const pattern = texturePattern(defs, ctx, size);
      textureBase(pattern, ctx, size);
      const rowHeight = size / 5;
      const scaleWidth = size / 3;
      const scales = ctx.d3.range(-1, 6).flatMap((row) => ctx.d3.range(-1, 4).map((column) => ({
        cx: column * scaleWidth + (row % 2 ? scaleWidth / 2 : 0),
        cy: row * rowHeight,
        row,
        column
      })));
      pattern.selectAll("path.scale")
        .data(scales)
        .join("path")
        .attr("class", "scale")
        .attr("d", (d) => `M${d.cx},${d.cy - rowHeight * 0.62}Q${d.cx + scaleWidth * 0.5},${d.cy} ${d.cx},${d.cy + rowHeight * 0.68}Q${d.cx - scaleWidth * 0.5},${d.cy} ${d.cx},${d.cy - rowHeight * 0.62}Z`)
        .attr("fill", (d) => ctx.palette.sequence[(d.row + d.column + 12) % ctx.palette.sequence.length])
        .attr("stroke", ctx.palette.roles.ink)
        .attr("stroke-width", 0.6)
        .attr("opacity", 0.36 + ctx.config.textureStrength * 0.58);
      return pattern;
    },

    "d3-logo-coral-branchlets": function renderCoralBranchlets(defs, ctx) {
      const size = 76 / ctx.config.density;
      const pattern = texturePattern(defs, ctx, size);
      textureBase(pattern, ctx, size, ctx.palette.roles.surface);
      const random = seededRandom(ctx.d3, ctx.config.seed, "coral-branchlets");
      const segments = [];
      const grow = (x, y, length, angle, depth, colony) => {
        if (depth <= 0 || length < size * 0.025) return;
        const ex = x + Math.cos(angle) * length;
        const ey = y + Math.sin(angle) * length;
        segments.push({ x1: x, y1: y, x2: ex, y2: ey, depth, colony });
        const fork = 0.35 + random() * 0.28;
        const ratio = 0.58 + random() * 0.12;
        grow(ex, ey, length * ratio, angle - fork, depth - 1, colony);
        grow(ex, ey, length * ratio, angle + fork, depth - 1, colony);
      };
      grow(size * 0.2, size, size * 0.28, -Math.PI / 2, 4, 0);
      grow(size * 0.72, size * 0.55, size * 0.25, -Math.PI / 2.3, 4, 1);
      pattern.selectAll("line.branch")
        .data(segments)
        .join("line")
        .attr("class", "branch")
        .attr("x1", (d) => d.x1).attr("y1", (d) => d.y1)
        .attr("x2", (d) => d.x2).attr("y2", (d) => d.y2)
        .attr("stroke", (d) => d.colony ? ctx.palette.roles.ink : ctx.palette.roles.primary)
        .attr("stroke-width", (d) => Math.max(0.65, d.depth * 0.52 / ctx.config.density))
        .attr("stroke-linecap", "round")
        .attr("opacity", 0.38 + ctx.config.textureStrength * 0.62);
      return pattern;
    },

    "d3-logo-circuit-traces": function renderCircuitTraces(defs, ctx) {
      const size = 72 / ctx.config.density;
      const pattern = texturePattern(defs, ctx, size);
      textureBase(pattern, ctx, size, ctx.palette.roles.surface);
      const random = seededRandom(ctx.d3, ctx.config.seed, "circuit-traces");
      const step = size / 8;
      const routes = ctx.d3.range(8).map((index) => {
        const x1 = Math.round(random() * 7) * step;
        const y1 = Math.round(random() * 7) * step;
        const x2 = Math.round(random() * 7) * step;
        const y2 = Math.round(random() * 7) * step;
        const bendX = Math.round((x1 + (x2 - x1) * random()) / step) * step;
        return { index, x1, y1, x2, y2, d: `M${x1},${y1}H${bendX}V${y2}H${x2}` };
      });
      pattern.selectAll("path.trace")
        .data(routes)
        .join("path")
        .attr("class", "trace")
        .attr("d", (d) => d.d)
        .attr("fill", "none")
        .attr("stroke", (d) => ctx.palette.sequence[d.index % ctx.palette.sequence.length])
        .attr("stroke-width", Math.max(1, 1.8 / ctx.config.density))
        .attr("stroke-linejoin", "round")
        .attr("opacity", 0.4 + ctx.config.textureStrength * 0.6);
      pattern.selectAll("circle.pad")
        .data(routes.flatMap((route) => [[route.x1, route.y1, route.index], [route.x2, route.y2, route.index]]))
        .join("circle")
        .attr("class", "pad")
        .attr("cx", (d) => d[0]).attr("cy", (d) => d[1])
        .attr("r", Math.max(1.4, 2.6 / ctx.config.density))
        .attr("fill", (d) => ctx.palette.sequence[d[2] % ctx.palette.sequence.length])
        .attr("stroke", ctx.palette.roles.ink)
        .attr("stroke-width", 0.55);
      return pattern;
    },

    "d3-logo-barcode-cadence": function renderBarcodeCadence(defs, ctx) {
      const size = 84 / ctx.config.density;
      const pattern = texturePattern(defs, ctx, size);
      textureBase(pattern, ctx, size, ctx.palette.roles.surface);
      const source = `${ctx.config.brand}|${ctx.config.seed}|${hashString(ctx.config.brand)}`;
      const unit = size / 52;
      const bars = [];
      let x = size * 0.055;
      let index = 0;
      while (x < size * 0.95) {
        const code = source.charCodeAt(index % source.length);
        const modules = 1 + code % 4;
        const gapModules = 1 + (code >> 2) % 2;
        const heightRatio = 0.5 + ((code >> 3) % 5) * 0.09;
        bars.push({ x, width: modules * unit, height: size * Math.min(0.9, heightRatio), index });
        x += (modules + gapModules) * unit;
        index += 1;
      }
      pattern.selectAll("rect.bar")
        .data(bars)
        .join("rect")
        .attr("class", "bar")
        .attr("x", (d) => d.x)
        .attr("y", (d) => (size - d.height) / 2)
        .attr("width", (d) => d.width)
        .attr("height", (d) => d.height)
        .attr("fill", (d) => d.index % 5 === 0 ? ctx.palette.roles.primary : ctx.palette.roles.ink)
        .attr("opacity", 0.48 + ctx.config.textureStrength * 0.52);
      return pattern;
    },

    "d3-logo-microtype-ribbons": function renderMicrotypeRibbons(defs, ctx) {
      const size = 96 / ctx.config.density;
      const pattern = texturePattern(defs, ctx, size);
      textureBase(pattern, ctx, size, ctx.palette.roles.surface);
      const brand = String(ctx.config.brand || "BRAND").toLocaleUpperCase();
      const phrase = `${brand} / ${brand} / ${brand} / `;
      const rows = ctx.d3.range(9).map((row) => ({ row, x: row % 2 ? -size * 0.18 : -size * 0.02, y: (row + 0.72) * size / 9 }));
      pattern.selectAll("text.microtype")
        .data(rows)
        .join("text")
        .attr("class", "microtype")
        .attr("x", (d) => d.x)
        .attr("y", (d) => d.y)
        .attr("fill", (d) => d.row % 3 === 0 ? ctx.palette.roles.primary : ctx.palette.roles.ink)
        .attr("font-family", ctx.config.fontFamily)
        .attr("font-size", Math.max(4.5, size / 15))
        .attr("font-weight", 700)
        .attr("letter-spacing", size / 120)
        .attr("opacity", 0.28 + ctx.config.textureStrength * 0.58)
        .text(phrase);
      return pattern;
    },

    "d3-logo-morse-stripes": function renderMorseStripes(defs, ctx) {
      const size = 96 / ctx.config.density;
      const pattern = texturePattern(defs, ctx, size);
      textureBase(pattern, ctx, size);
      const table = {
        A: ".-", B: "-...", C: "-.-.", D: "-..", E: ".", F: "..-.", G: "--.", H: "....", I: "..", J: ".---", K: "-.-", L: ".-..", M: "--", N: "-.", O: "---", P: ".--.", Q: "--.-", R: ".-.", S: "...", T: "-", U: "..-", V: "...-", W: ".--", X: "-..-", Y: "-.--", Z: "--..",
        0: "-----", 1: ".----", 2: "..---", 3: "...--", 4: "....-", 5: ".....", 6: "-....", 7: "--...", 8: "---..", 9: "----."
      };
      const source = Array.from(String(ctx.config.brand || "BRAND").toLocaleUpperCase()).filter((character) => table[character]);
      const symbols = (source.length ? source : ["B", "R", "A", "N", "D"]).flatMap((character, characterIndex) => [
        ...Array.from(table[character]).map((symbol) => ({ symbol, characterIndex })),
        { symbol: "gap", characterIndex }
      ]);
      const unit = size / 54;
      const marks = [];
      for (let row = 0; row < 5; row += 1) {
        let x = unit * (row % 2 ? -4 : 1);
        let symbolIndex = row;
        while (x < size) {
          const entry = symbols[symbolIndex % symbols.length];
          const width = entry.symbol === "-" ? unit * 3 : entry.symbol === "." ? unit : unit * 2;
          if (entry.symbol !== "gap") marks.push({ row, x, width, dot: entry.symbol === ".", characterIndex: entry.characterIndex });
          x += width + unit;
          symbolIndex += 1;
        }
      }
      pattern.selectAll("rect.dash")
        .data(marks.filter((mark) => !mark.dot))
        .join("rect")
        .attr("class", "dash")
        .attr("x", (d) => d.x)
        .attr("y", (d) => (d.row + 0.5) * size / 5 - unit / 2)
        .attr("width", (d) => d.width)
        .attr("height", unit)
        .attr("rx", unit / 2)
        .attr("fill", (d) => ctx.palette.sequence[d.characterIndex % ctx.palette.sequence.length])
        .attr("opacity", 0.42 + ctx.config.textureStrength * 0.58);
      pattern.selectAll("circle.dot")
        .data(marks.filter((mark) => mark.dot))
        .join("circle")
        .attr("class", "dot")
        .attr("cx", (d) => d.x + unit / 2)
        .attr("cy", (d) => (d.row + 0.5) * size / 5)
        .attr("r", unit / 2)
        .attr("fill", (d) => ctx.palette.sequence[d.characterIndex % ctx.palette.sequence.length])
        .attr("opacity", 0.42 + ctx.config.textureStrength * 0.58);
      return pattern;
    },

    "d3-logo-radial-calibration": function renderRadialCalibration(defs, ctx) {
      const size = 72 / ctx.config.density;
      const pattern = texturePattern(defs, ctx, size);
      textureBase(pattern, ctx, size, ctx.palette.roles.surface);
      const dials = [[size * 0.26, size * 0.3, size * 0.19], [size * 0.74, size * 0.72, size * 0.19]];
      pattern.selectAll("circle.dial-ring")
        .data(dials.flatMap(([cx, cy, radius], dial) => ctx.d3.range(1, 4).map((ring) => ({ cx, cy, radius: radius * ring / 3, dial, ring }))))
        .join("circle")
        .attr("class", "dial-ring")
        .attr("cx", (d) => d.cx).attr("cy", (d) => d.cy).attr("r", (d) => d.radius)
        .attr("fill", "none")
        .attr("stroke", (d) => d.ring === 3 ? ctx.palette.roles.primary : ctx.palette.roles.ink)
        .attr("stroke-width", (d) => d.ring === 3 ? 1.25 : 0.65)
        .attr("opacity", 0.36 + ctx.config.textureStrength * 0.64);
      const ticks = dials.flatMap(([cx, cy, radius], dial) => ctx.d3.range(20).map((index) => {
        const angle = index / 20 * Math.PI * 2;
        const major = index % 5 === 0;
        const inner = radius * (major ? 0.66 : 0.78);
        return { dial, major, x1: cx + Math.cos(angle) * inner, y1: cy + Math.sin(angle) * inner, x2: cx + Math.cos(angle) * radius, y2: cy + Math.sin(angle) * radius };
      }));
      pattern.selectAll("line.tick")
        .data(ticks)
        .join("line")
        .attr("class", "tick")
        .attr("x1", (d) => d.x1).attr("y1", (d) => d.y1)
        .attr("x2", (d) => d.x2).attr("y2", (d) => d.y2)
        .attr("stroke", (d) => d.major ? ctx.palette.roles.primary : ctx.palette.roles.ink)
        .attr("stroke-width", (d) => d.major ? 1.5 : 0.7)
        .attr("opacity", 0.4 + ctx.config.textureStrength * 0.6);
      return pattern;
    },

    "d3-logo-seven-segment-code": function renderSevenSegmentCode(defs, ctx) {
      const size = 96 / ctx.config.density;
      const pattern = texturePattern(defs, ctx, size);
      textureBase(pattern, ctx, size, ctx.palette.roles.inkDark);
      const digitSegments = [
        [0, 1, 2, 3, 4, 5], [1, 2], [0, 1, 6, 4, 3], [0, 1, 6, 2, 3], [5, 6, 1, 2],
        [0, 5, 6, 2, 3], [0, 5, 6, 4, 2, 3], [0, 1, 2], [0, 1, 2, 3, 4, 5, 6], [0, 1, 2, 3, 5, 6]
      ];
      const segmentBoxes = [
        [0.18, 0.08, 0.64, 0.1], [0.78, 0.14, 0.1, 0.34], [0.78, 0.52, 0.1, 0.34],
        [0.18, 0.82, 0.64, 0.1], [0.12, 0.52, 0.1, 0.34], [0.12, 0.14, 0.1, 0.34], [0.18, 0.45, 0.64, 0.1]
      ];
      const hash = `${hashString(ctx.config.brand)}${Math.abs(ctx.config.seed)}`;
      const digits = ctx.d3.range(4).map((index) => (hash.charCodeAt(index % hash.length) + ctx.config.seed + index * 7) % 10);
      const cellWidth = size / 4;
      const segments = digits.flatMap((digit, digitIndex) => digitSegments[Math.abs(digit)].map((segment) => ({ digitIndex, digit, segment })));
      pattern.selectAll("rect.segment")
        .data(segments)
        .join("rect")
        .attr("class", "segment")
        .attr("x", (d) => d.digitIndex * cellWidth + segmentBoxes[d.segment][0] * cellWidth)
        .attr("y", (d) => segmentBoxes[d.segment][1] * size)
        .attr("width", (d) => segmentBoxes[d.segment][2] * cellWidth)
        .attr("height", (d) => segmentBoxes[d.segment][3] * size)
        .attr("rx", Math.max(0.7, size * 0.012))
        .attr("fill", (d) => ctx.palette.sequence[d.digitIndex % ctx.palette.sequence.length])
        .attr("opacity", 0.48 + ctx.config.textureStrength * 0.52);
      return pattern;
    }
  };

  function createTexture(defs, ctx) {
    if (ctx.config.textureStrength === 0) {
      const flat = texturePattern(defs, ctx, 16);
      flat.attr("data-flat-fallback", "texture-strength-zero");
      textureBase(flat, ctx, 16, ctx.palette.roles.primary);
      return flat;
    }
    const renderer = TEXTURE_RENDERERS[ctx.config.textureId];
    if (!renderer) throw new RangeError(`No texture renderer for ${ctx.config.textureId}.`);
    return renderer(defs, ctx);
  }

  function brandInitials(brand) {
    const words = String(brand).trim().split(/\s+/u).filter(Boolean);
    if (!words.length) return "?";
    if (words.length > 1) return words.slice(0, 2).map((word) => Array.from(word)[0]).join("").toLocaleUpperCase();
    return Array.from(words[0]).slice(0, 2).join("").toLocaleUpperCase();
  }

  function fittedFontSize(text, preferred, maxWidth, minimum = 8) {
    const length = Math.max(1, Array.from(String(text)).length);
    return Math.max(minimum, Math.min(preferred, maxWidth / (length * 0.59)));
  }

  function fitTextToWidth(selection, maxWidth, minimumSize = 6) {
    const node = selection.node();
    if (!node || !(maxWidth > 0) || typeof node.getComputedTextLength !== "function") return selection;
    const currentSize = finiteNumber(node.getAttribute("font-size"), 16);
    let measuredWidth = 0;
    try {
      measuredWidth = node.getComputedTextLength();
    } catch (error) {
      measuredWidth = 0;
    }
    if (!(measuredWidth > maxWidth)) {
      node.setAttribute("data-text-fit", "natural");
      return selection;
    }
    const fittedSize = Math.max(minimumSize, currentSize * maxWidth / measuredWidth);
    node.setAttribute("font-size", fittedSize.toFixed(3));
    node.setAttribute("data-text-fit", "font-size");
    try {
      measuredWidth = node.getComputedTextLength();
    } catch (error) {
      measuredWidth = 0;
    }
    if (measuredWidth > maxWidth + 0.25) {
      node.setAttribute("textLength", maxWidth);
      node.setAttribute("lengthAdjust", "spacingAndGlyphs");
      node.setAttribute("data-text-fit", "length-adjust");
    }
    return selection;
  }

  function balancedTextLines(value) {
    const text = String(value).trim();
    const words = text.split(/\s+/u).filter(Boolean);
    if (words.length > 1) {
      let splitIndex = 1;
      let bestDifference = Number.POSITIVE_INFINITY;
      for (let index = 1; index < words.length; index += 1) {
        const first = words.slice(0, index).join(" ");
        const second = words.slice(index).join(" ");
        const difference = Math.abs(Array.from(first).length - Array.from(second).length);
        if (difference < bestDifference) {
          bestDifference = difference;
          splitIndex = index;
        }
      }
      return [words.slice(0, splitIndex).join(" "), words.slice(splitIndex).join(" ")];
    }
    const characters = Array.from(text);
    const midpoint = Math.ceil(characters.length / 2);
    return [characters.slice(0, midpoint).join(""), characters.slice(midpoint).join("")].filter(Boolean);
  }

  function fitOrWrapText(selection, value, maxWidth, minimumSize, lineHeight) {
    const node = selection.node();
    if (!node || typeof node.getComputedTextLength !== "function") return selection;
    const currentSize = finiteNumber(node.getAttribute("font-size"), 16);
    let measuredWidth = 0;
    try {
      measuredWidth = node.getComputedTextLength();
    } catch (error) {
      measuredWidth = 0;
    }
    const requiredSize = measuredWidth > 0 ? currentSize * maxWidth / measuredWidth : currentSize;
    if (requiredSize >= minimumSize) return fitTextToWidth(selection, maxWidth, minimumSize);

    const lines = balancedTextLines(value);
    if (lines.length < 2) return fitTextToWidth(selection, maxWidth, minimumSize);
    const x = finiteNumber(node.getAttribute("x"), 240);
    const centerY = finiteNumber(node.getAttribute("y"), 160);
    const originalHasSpaces = /\s/u.test(String(value));
    selection
      .text(null)
      .attr("aria-label", String(value))
      .attr("data-text-fit", "wrapped-2-lines")
      .attr("data-text-line-count", lines.length);
    lines.forEach((line, index) => {
      const renderedLine = originalHasSpaces && index < lines.length - 1 ? `${line} ` : line;
      const lineSelection = selection.append("tspan")
        .attr("x", x)
        .attr("y", centerY + (index - (lines.length - 1) / 2) * lineHeight)
        .attr("data-text-line", index + 1)
        .text(renderedLine);
      fitTextToWidth(lineSelection, maxWidth, minimumSize);
    });
    return selection;
  }

  function addText(group, ctx, options) {
    const className = options.className || "";
    const inferredRole = options.role || (
      /tagline/.test(className) ? "tagline" :
      /initial|monogram|ligature/.test(className) ? "initials" :
      /value/.test(className) ? "label" :
      /brand|wordmark|window|axis-glyph|wave-glyph|stack-copy|depth-copy/.test(className) ? "brand" :
      "decorative"
    );
    const selection = group.append("text")
      .attr("class", options.className || null)
      .attr("data-text-role", inferredRole)
      .attr("x", options.x == null ? 240 : options.x)
      .attr("y", options.y == null ? 160 : options.y)
      .attr("text-anchor", options.anchor || "middle")
      .attr("dominant-baseline", options.baseline || "middle")
      .attr("font-family", ctx.config.fontFamily)
      .attr("font-size", options.size == null ? 32 : options.size)
      .attr("font-weight", options.weight == null ? 700 : options.weight)
      .attr("letter-spacing", options.tracking == null ? 0 : options.tracking)
      .attr("fill", options.fill || ctx.palette.roles.ink)
      .text(options.text == null ? "" : options.text);
    if (options.maxWidth != null) {
      const minimumSize = options.minimumSize == null ? 6 : options.minimumSize;
      if (options.maxLines > 1) {
        fitOrWrapText(selection, options.text, options.maxWidth, minimumSize, options.lineHeight || minimumSize * 1.25);
      } else {
        fitTextToWidth(selection, options.maxWidth, minimumSize);
      }
    }
    return selection;
  }

  function resolvedUseTarget(node, svgNode) {
    if (String(node.localName).toLowerCase() !== "use") return null;
    const href = node.getAttribute("href") || node.getAttribute("xlink:href") || "";
    return href.startsWith("#") ? svgNode.querySelector(href) : null;
  }

  function inferRenderedTextRole(node, ctx) {
    const explicit = node.getAttribute("data-text-role");
    if (explicit) return explicit;
    const target = resolvedUseTarget(node, ctx.svgNode);
    const className = `${node.getAttribute("class") || ""} ${target?.getAttribute("class") || ""}`;
    const text = `${node.textContent || ""}${target?.textContent || ""}`.trim();
    if (/tagline/.test(className) || text === ctx.config.tagline) return "tagline";
    if (/initial|monogram|ligature/.test(className) || text === brandInitials(ctx.config.brand)) return "initials";
    if (/polar-value|label/.test(className)) return "label";
    if (/rosette-glyph/.test(className)) return "decorative";
    if (/axis-glyph|wave-glyph|stack-copy|shifted-slice|stroke-layer|stroke-fill|depth-copy|brand|wordmark|window/.test(className)) return "brand";
    if (text === ctx.config.brand) return "brand";
    if (text.includes(ctx.config.brand) && ctx.config.tagline && text.includes(ctx.config.tagline)) return "brand-tagline";
    return "decorative";
  }

  function annotateTextLayers(compositionGroup, ctx) {
    const root = compositionGroup.node();
    const candidates = Array.from(root.querySelectorAll("text, use, [data-text-proxy]"))
      .filter((node) => {
        if (node.matches("[data-text-proxy], text")) return true;
        return resolvedUseTarget(node, ctx.svgNode)?.localName === "text";
      })
      .filter((node, index, values) => !values.some((parent, parentIndex) => parentIndex !== index && parent.contains(node) && parent.hasAttribute("data-text-proxy")));
    for (const node of candidates) {
      const role = inferRenderedTextRole(node, ctx);
      const source = node.getAttribute("data-text-proxy") || (
        String(node.localName).toLowerCase() === "use" ? "use-stack" :
        node.querySelector?.("textPath") ? "text-path" :
        node.matches("text") ? "glyph-run" : "proxy"
      );
      const layerSuffix = node.getAttribute("data-text-layer-suffix");
      const layerId = `${ctx.config.exampleId}--${sanitizeId(role)}${layerSuffix ? `-${sanitizeId(layerSuffix)}` : ""}`;
      node.setAttribute("data-text-role", role);
      node.setAttribute("data-text-layer-id", layerId);
      node.setAttribute("data-text-source", source);
      if (!node.hasAttribute("data-text-policy")) node.setAttribute("data-text-policy", "clear");
    }

    const layerCounts = new Map();
    const drawables = root.querySelectorAll("path, rect, circle, ellipse, line, polyline, polygon, use, text");
    for (const node of drawables) {
      if (node.closest("[data-text-layer-id]")) continue;
      const classToken = (node.getAttribute("class") || "").trim().split(/\s+/u).filter(Boolean)[0];
      const role = node.getAttribute("data-layer-role") || classToken || String(node.localName).toLowerCase();
      const safeRole = sanitizeId(role);
      const ordinal = (layerCounts.get(safeRole) || 0) + 1;
      layerCounts.set(safeRole, ordinal);
      node.setAttribute("data-layer-role", role);
      node.setAttribute("data-layer-id", `${ctx.config.exampleId}--${safeRole}-${ordinal}`);
    }
  }

  function addBrandLockup(group, ctx, y) {
    addText(group, ctx, {
      className: "brand-lockup",
      text: ctx.config.brand,
      x: 240,
      y: y == null ? 246 : y,
      size: fittedFontSize(ctx.config.brand, 32, 330),
      weight: 750,
      tracking: 1.2,
      fill: ctx.palette.roles.ink,
      maxWidth: 330,
      minimumSize: 8
    });
    ctx.brandHandled = true;
  }

  function addTagline(group, ctx, y) {
    if (!ctx.config.tagline) {
      ctx.taglineHandled = true;
      return;
    }
    addText(group, ctx, {
      className: "tagline-lockup",
      text: ctx.config.tagline,
      x: 240,
      y: y == null ? 282 : y,
      size: fittedFontSize(ctx.config.tagline, 13, 330),
      weight: 500,
      tracking: 1.35,
      fill: ctx.palette.sequence[1 % ctx.palette.sequence.length],
      maxWidth: 330,
      minimumSize: 9,
      maxLines: 2,
      lineHeight: 12
    });
    ctx.taglineHandled = true;
  }

  function originalAnimalPoints(curvature) {
    const lift = (curvature - 0.5) * 12;
    return [
      [112, 158], [143, 143 - lift * 0.25], [176, 121 - lift], [224, 116 - lift],
      [267, 123 - lift * 0.65], [296, 113 - lift * 0.4], [304, 96 - lift], [316, 119],
      [343, 137], [324, 153], [298, 157], [280, 177], [291, 207], [270, 207],
      [250, 178], [210, 176], [194, 207], [173, 207], [179, 173], [147, 167]
    ];
  }

  function originalAnimalPath(ctx) {
    return ctx.d3.line()
      .curve(ctx.d3.curveCatmullRomClosed.alpha(0.35 + ctx.config.curvature * 0.5))
      (originalAnimalPoints(ctx.config.curvature));
  }

  function renderTypeOrbit(group, ctx) {
    if (ctx.smallSize) {
      group.attr("data-small-size-lockup", "compact-horizontal");
      group.append("circle")
        .attr("class", "orbit-compact-ring")
        .attr("cx", 108)
        .attr("cy", 145)
        .attr("r", 78)
        .attr("fill", ctx.textureFill)
        .attr("stroke", ctx.palette.roles.ink)
        .attr("stroke-width", 5);
      group.append("circle")
        .attr("class", "orbit-compact-core")
        .attr("cx", 108)
        .attr("cy", 145)
        .attr("r", 61)
        .attr("fill", ctx.palette.roles.primary);
      addText(group, ctx, {
        className: "orbit-compact-initials",
        text: brandInitials(ctx.config.brand),
        x: 108,
        y: 145,
        size: 64,
        weight: 850,
        fill: ctx.palette.roles.surface
      });
      addText(group, ctx, {
        className: "orbit-compact-wordmark",
        text: ctx.config.brand,
        x: 208,
        y: 145,
        anchor: "start",
        size: fittedFontSize(ctx.config.brand, 42, 236),
        weight: 800,
        fill: ctx.palette.roles.ink
      });
      group.attr("data-small-size-tagline", "hidden");
      ctx.brandHandled = true;
      ctx.taglineHandled = true;
      return;
    }
    const pathId = ctx.uid("orbit-text-path");
    const radius = 74 + ctx.config.curvature * 24;
    const startX = 240 - radius;
    ctx.defs.append("path")
      .attr("id", pathId)
      .attr("d", `M${startX},145a${radius},${radius} 0 1,1 ${radius * 2},0a${radius},${radius} 0 1,1 ${-radius * 2},0`);
    group.append("circle")
      .attr("class", "orbit-core")
      .attr("cx", 240)
      .attr("cy", 145)
      .attr("r", 52)
      .attr("fill", ctx.textureFill)
      .attr("stroke", ctx.palette.roles.ink)
      .attr("stroke-width", 3);
    group.append("circle")
      .attr("class", "orbit-guide")
      .attr("cx", 240)
      .attr("cy", 145)
      .attr("r", radius)
      .attr("fill", "none")
      .attr("stroke", ctx.palette.sequence[1 % ctx.palette.sequence.length])
      .attr("stroke-width", 1.5);
    const text = group.append("text")
      .attr("font-family", ctx.config.fontFamily)
      .attr("font-size", fittedFontSize(ctx.config.brand, 18, radius * 3.9))
      .attr("font-weight", 700)
      .attr("letter-spacing", 2.2)
      .attr("fill", ctx.palette.roles.ink);
    text.append("textPath")
      .attr("href", `#${pathId}`)
      .attr("startOffset", "50%")
      .attr("text-anchor", "middle")
      .text(`${ctx.config.brand} · ${ctx.config.tagline || ctx.config.brand} ·`);
    addText(group, ctx, { className: "orbit-initials", text: brandInitials(ctx.config.brand), x: 240, y: 145, size: 34, weight: 800, fill: ctx.palette.roles.surface });
    ctx.brandHandled = true;
    ctx.taglineHandled = true;
  }

  function renderBezierWordpath(group, ctx) {
    const pathId = ctx.uid("bezier-wordpath");
    const lift = 45 + ctx.config.curvature * 75;
    const pathData = `M58,184 C150,${184 - lift} 308,${184 + lift * 0.45} 422,132`;
    ctx.defs.append("path").attr("id", pathId).attr("d", pathData);
    group.append("path")
      .attr("class", "bezier-baseline")
      .attr("d", pathData)
      .attr("fill", "none")
      .attr("stroke", ctx.textureFill)
      .attr("stroke-width", 11)
      .attr("stroke-linecap", "round");
    const text = group.append("text")
      .attr("font-family", ctx.config.fontFamily)
      .attr("font-size", fittedFontSize(ctx.config.brand, 42, 335))
      .attr("font-weight", 800)
      .attr("letter-spacing", 1.4)
      .attr("fill", ctx.palette.roles.ink);
    text.append("textPath")
      .attr("href", `#${pathId}`)
      .attr("startOffset", "50%")
      .attr("text-anchor", "middle")
      .attr("dy", -10)
      .text(ctx.config.brand);
    group.selectAll("circle.bezier-terminal")
      .data([[58, 184], [422, 132]])
      .join("circle")
      .attr("class", "bezier-terminal")
      .attr("cx", (d) => d[0])
      .attr("cy", (d) => d[1])
      .attr("r", 6)
      .attr("fill", ctx.palette.sequence[1]);
    ctx.brandHandled = true;
  }

  function renderVariableAxisWordmark(group, ctx) {
    group.attr("data-axis-mode", "fallback");
    const glyphs = Array.from(ctx.config.brand);
    const size = fittedFontSize(ctx.config.brand, 66, 360);
    const weightScale = ctx.d3.scaleLinear().domain([0, Math.max(1, glyphs.length - 1)]).range([540, 860]);
    const strongColors = [
      ctx.palette.roles.inkDark,
      ctx.palette.roles.primary,
      ctx.palette.roles.primaryDark,
      ctx.palette.roles.secondaryDark || ctx.palette.roles.ink,
      ctx.palette.roles.special || ctx.palette.roles.ink
    ];
    const glyphData = glyphs.map((glyph, index) => ({
      glyph,
      index,
      baseSize: size * (0.92 + index % 3 * 0.05)
    }));
    const glyphSelection = group.selectAll("text.axis-glyph")
      .data(glyphData)
      .join("text")
      .attr("class", "axis-glyph")
      .attr("data-text-layer-suffix", (d) => `glyph-${d.index + 1}`)
      .attr("x", 0)
      .attr("y", (d) => 151 + Math.sin(d.index * 0.8) * ctx.config.curvature * 7)
      .attr("text-anchor", "middle")
      .attr("dominant-baseline", "middle")
      .attr("font-family", ctx.config.fontFamily)
      .attr("font-size", (d) => d.baseSize)
      .attr("font-weight", (d) => Math.round(weightScale(d.index)))
      .attr("letter-spacing", 0)
      .attr("fill", (d) => strongColors[d.index % strongColors.length])
      .text((d) => d.glyph);

    const measureGlyphs = () => glyphSelection.nodes().map((node, index) => {
      const renderedSize = finiteNumber(node.getAttribute("font-size"), glyphData[index].baseSize);
      if (/\s/u.test(glyphData[index].glyph)) return renderedSize * 0.36;
      try {
        const measured = Number(node.getComputedTextLength());
        if (Number.isFinite(measured) && measured > 0) return measured;
      } catch (error) {
        // Detached renderers use the deterministic width fallback below.
      }
      return renderedSize * 0.59;
    });
    const gap = clamp(7.2 - glyphs.length * 0.08 + (ctx.config.density - 1) * 0.3, 5, 7);
    let widths = measureGlyphs();
    const availableGlyphWidth = Math.max(48, 330 - gap * Math.max(0, glyphs.length - 1));
    const measuredGlyphWidth = widths.reduce((sum, width) => sum + width, 0);
    let commonScale = Math.min(1, availableGlyphWidth / Math.max(1, measuredGlyphWidth));
    glyphSelection.attr("font-size", (d) => d.baseSize * commonScale);
    widths = measureGlyphs();
    let totalWidth = widths.reduce((sum, width) => sum + width, 0) + gap * Math.max(0, glyphs.length - 1);
    if (totalWidth > 330) {
      const correction = availableGlyphWidth / Math.max(1, widths.reduce((sum, width) => sum + width, 0));
      commonScale *= correction;
      glyphSelection.attr("font-size", (d) => d.baseSize * commonScale);
      widths = measureGlyphs();
      totalWidth = widths.reduce((sum, width) => sum + width, 0) + gap * Math.max(0, glyphs.length - 1);
    }
    let cursor = 240 - totalWidth / 2;
    glyphSelection.attr("x", (d, index) => {
      const center = cursor + widths[index] / 2;
      cursor += widths[index] + gap;
      return center;
    });
    group.attr("data-axis-scale", commonScale.toFixed(4)).attr("data-axis-gap", gap.toFixed(2));
    group.append("rect")
      .attr("class", "axis-rule")
      .attr("x", 240 - totalWidth / 2)
      .attr("y", 194)
      .attr("width", Math.max(72, totalWidth))
      .attr("height", 7)
      .attr("fill", ctx.textureFill);
    ctx.brandHandled = true;
  }

  function renderLigatureBridge(group, ctx) {
    const initials = Array.from(brandInitials(ctx.config.brand));
    const left = initials[0] || "A";
    const right = initials[1] || left;
    addText(group, ctx, { className: "ligature-left", text: left, x: 164, y: 143, size: 92, weight: 800, fill: ctx.palette.roles.ink });
    addText(group, ctx, { className: "ligature-right", text: right, x: 316, y: 143, size: 92, weight: 800, fill: ctx.palette.roles.ink });
    const bend = 34 + ctx.config.curvature * 56;
    group.append("path")
      .attr("class", "ligature-connector")
      .attr("d", `M196,155 C220,${155 - bend} 260,${155 + bend} 284,133`)
      .attr("fill", "none")
      .attr("stroke", ctx.textureFill)
      .attr("stroke-width", 12 + ctx.config.density * 4)
      .attr("stroke-linecap", "round");
    group.selectAll("circle.ligature-anchor")
      .data([[196, 155], [284, 133]])
      .join("circle")
      .attr("class", "ligature-anchor")
      .attr("cx", (d) => d[0])
      .attr("cy", (d) => d[1])
      .attr("r", 5)
      .attr("fill", ctx.palette.roles.accent);
  }

  function renderStencilCuts(group, ctx) {
    const maskId = ctx.uid("stencil-mask");
    const mask = ctx.defs.append("mask")
      .attr("id", maskId)
      .attr("maskUnits", "userSpaceOnUse")
      .attr("x", 44)
      .attr("y", 82)
      .attr("width", 392)
      .attr("height", 134);
    mask.append("text")
      .attr("x", 240)
      .attr("y", 164)
      .attr("text-anchor", "middle")
      .attr("dominant-baseline", "middle")
      .attr("font-family", ctx.config.fontFamily)
      .attr("font-size", fittedFontSize(ctx.config.brand, 78, 370))
      .attr("font-weight", 900)
      .attr("letter-spacing", 1)
      .attr("fill", ctx.palette.roles.surface)
      .text(ctx.config.brand);
    const cutCount = Math.max(4, Math.round(6 * ctx.config.density));
    mask.selectAll("rect.stencil-cut")
      .data(ctx.d3.range(cutCount))
      .join("rect")
      .attr("class", "stencil-cut")
      .attr("x", (d) => 82 + d * 310 / Math.max(1, cutCount - 1))
      .attr("y", 92)
      .attr("width", 7 + ctx.config.curvature * 8)
      .attr("height", 136)
      .attr("fill", ctx.palette.allowed[0])
      .attr("transform", (d) => `rotate(${-18 + ctx.config.rotation * 0.12} ${82 + d * 310 / Math.max(1, cutCount - 1)} 160)`);
    group.append("rect")
      .attr("class", "stencil-wordmark")
      .attr("data-text-proxy", "mask-proxy")
      .attr("data-text-role", "brand")
      .attr("x", 44)
      .attr("y", 82)
      .attr("width", 392)
      .attr("height", 134)
      .attr("fill", ctx.textureFill)
      .attr("mask", fragmentUrl(maskId));
    ctx.brandHandled = true;
  }

  function renderLetterWindow(group, ctx) {
    const clipId = ctx.uid("letter-window-clip");
    const size = fittedFontSize(ctx.config.brand, 112, 374);
    const clip = ctx.defs.append("clipPath")
      .attr("id", clipId)
      .attr("clipPathUnits", "userSpaceOnUse");
    clip.append("text")
      .attr("x", 240)
      .attr("y", 151)
      .attr("text-anchor", "middle")
      .attr("dominant-baseline", "middle")
      .attr("font-family", ctx.config.fontFamily)
      .attr("font-size", size)
      .attr("font-weight", 900)
      .attr("letter-spacing", -1)
      .text(ctx.config.brand);
    group.append("rect")
      .attr("class", "letter-window-surface")
      .attr("data-text-proxy", "clip-proxy")
      .attr("data-text-role", "brand")
      .attr("x", 42)
      .attr("y", 74)
      .attr("width", 396)
      .attr("height", 158)
      .attr("fill", ctx.textureFill)
      .attr("clip-path", fragmentUrl(clipId));
    addText(group, ctx, { className: "letter-window-outline", text: ctx.config.brand, x: 240, y: 151, size, weight: 900, fill: "none" })
      .attr("stroke", ctx.palette.roles.ink)
      .attr("stroke-width", 1.5);
    ctx.brandHandled = true;
  }

  function renderMirroredMonogram(group, ctx) {
    const initial = Array.from(brandInitials(ctx.config.brand))[0] || "A";
    const mark = group.append("g").attr("class", "mirrored-axis-mark").attr("transform", "translate(240,145)");
    mark.append("line")
      .attr("x1", 0).attr("y1", -82).attr("x2", 0).attr("y2", 82)
      .attr("stroke", ctx.palette.roles.line).attr("stroke-width", 2);
    mark.append("text")
      .attr("class", "mirror-initial")
      .attr("x", -3).attr("y", 0).attr("text-anchor", "middle").attr("dominant-baseline", "middle")
      .attr("font-family", ctx.config.fontFamily).attr("font-size", 118).attr("font-weight", 800)
      .attr("fill", ctx.textureFill).text(initial);
    mark.append("text")
      .attr("class", "mirror-initial")
      .attr("x", -3).attr("y", 0).attr("text-anchor", "middle").attr("dominant-baseline", "middle")
      .attr("font-family", ctx.config.fontFamily).attr("font-size", 118).attr("font-weight", 800)
      .attr("fill", ctx.palette.roles.primaryDark)
      .attr("transform", `scale(-1,1) translate(${-18 * ctx.config.curvature},0)`).text(initial);
    mark.append("circle").attr("class", "mirror-joint").attr("cx", 0).attr("cy", 0).attr("r", 7).attr("fill", ctx.palette.roles.accent);
  }

  function renderGlyphRosette(group, ctx) {
    const glyph = Array.from(brandInitials(ctx.config.brand))[0] || "A";
    const centerY = 132;
    const count = clamp(Math.round(8 + ctx.config.density * 4.5), 10, 16);
    const radius = 78 + clamp((ctx.config.density - 1) * 5, 0, 5);
    const arcLength = Math.PI * 2 * radius / count;
    const glyphSize = clamp(arcLength * 0.55, 16, 22);
    const strongColors = [
      ctx.palette.roles.inkDark,
      ctx.palette.roles.primary,
      ctx.palette.roles.primaryDark,
      ctx.palette.roles.secondaryDark || ctx.palette.roles.ink,
      ctx.palette.roles.special || ctx.palette.roles.ink
    ];
    group.selectAll("text.rosette-glyph")
      .data(ctx.d3.range(count))
      .join("text")
      .attr("class", "rosette-glyph")
      .attr("data-text-layer-suffix", (d) => `glyph-${d + 1}`)
      .attr("x", 240)
      .attr("y", centerY - radius)
      .attr("text-anchor", "middle")
      .attr("dominant-baseline", "middle")
      .attr("font-family", ctx.config.fontFamily)
      .attr("font-size", (d) => glyphSize * (d % 2 ? 0.9 : 1))
      .attr("font-weight", 850)
      .attr("fill", (d) => strongColors[d % strongColors.length])
      .attr("stroke", ctx.palette.roles.background)
      .attr("stroke-width", 1.8)
      .attr("paint-order", "stroke fill")
      .attr("transform", (d) => `rotate(${d * 360 / count} 240 ${centerY})`)
      .text(glyph);
    group.append("circle")
      .attr("class", "rosette-core")
      .attr("cx", 240).attr("cy", centerY).attr("r", 36)
      .attr("fill", ctx.textureFill).attr("stroke", ctx.palette.roles.ink).attr("stroke-width", 3);
    addText(group, ctx, { className: "rosette-initials", text: brandInitials(ctx.config.brand), x: 240, y: centerY, size: 24, weight: 850, fill: ctx.palette.roles.surface });
  }

  function renderBaselineWave(group, ctx) {
    const glyphs = Array.from(ctx.config.brand);
    const left = 62;
    const right = 418;
    const amplitude = 18 + ctx.config.curvature * 38;
    const frequency = 1.25 + ctx.config.density * 0.55;
    const xFor = (index) => glyphs.length < 2 ? 240 : left + index * (right - left) / (glyphs.length - 1);
    const yFor = (index) => 146 + Math.sin(index / Math.max(1, glyphs.length - 1) * Math.PI * 2 * frequency) * amplitude;
    const areaData = ctx.d3.range(41).map((index) => {
      const x = left + index * (right - left) / 40;
      const y = 146 + Math.sin(index / 40 * Math.PI * 2 * frequency) * amplitude;
      return [x, y];
    });
    group.append("path")
      .attr("class", "wave-ribbon")
      .attr("d", ctx.d3.area().x((d) => d[0]).y0((d) => d[1] + 14).y1((d) => d[1] + 25).curve(ctx.d3.curveBasis)(areaData))
      .attr("fill", ctx.textureFill);
    group.selectAll("text.wave-glyph")
      .data(glyphs)
      .join("text")
      .attr("class", "wave-glyph")
      .attr("x", (d, index) => xFor(index))
      .attr("y", (d, index) => yFor(index))
      .attr("text-anchor", "middle")
      .attr("dominant-baseline", "middle")
      .attr("font-family", ctx.config.fontFamily)
      .attr("font-size", fittedFontSize(ctx.config.brand, 44, 350))
      .attr("font-weight", 800)
      .attr("fill", ctx.palette.roles.ink)
      .attr("transform", (d, index) => {
        const next = Math.min(glyphs.length - 1, index + 1);
        const angle = Math.atan2(yFor(next) - yFor(index), Math.max(1, xFor(next) - xFor(index))) * 180 / Math.PI;
        return `rotate(${angle} ${xFor(index)} ${yFor(index)})`;
      })
      .text((d) => d);
    ctx.brandHandled = true;
  }

  function renderStackOffset(group, ctx) {
    const copies = clamp(Math.round(3 + ctx.config.density * 2.4), 4, 7);
    const center = (copies - 1) / 2;
    const offsetX = 3.6 + ctx.config.curvature * 1.6;
    const offsetY = 4.2 + ctx.config.curvature * 1.8;
    const effectiveRotation = ctx.config.rotation;
    const angle = Math.abs(effectiveRotation) * Math.PI / 180;
    const glyphWidthFactor = Math.max(1, Array.from(ctx.config.brand).length * 0.59);
    const availableWidth = Math.max(120, 2 * (180 / ctx.config.scale - center * offsetX));
    const availableHeight = Math.max(70, 2 * (78 / ctx.config.scale - center * offsetY));
    const widthBound = availableWidth / (glyphWidthFactor * Math.cos(angle) + Math.sin(angle));
    const heightBound = availableHeight / (glyphWidthFactor * Math.sin(angle) + Math.cos(angle));
    const size = clamp(Math.min(68, widthBound, heightBound), 14, 68);
    const stack = group.append("g")
      .attr("class", "stack-safe-area")
      .attr("data-effective-rotation", effectiveRotation);
    stack.selectAll("text.stack-copy")
      .data(ctx.d3.range(copies).reverse())
      .join("text")
      .attr("class", "stack-copy")
      .attr("x", (d) => 240 + (d - center) * offsetX)
      .attr("y", (d) => 150 + (d - center) * offsetY)
      .attr("text-anchor", "middle")
      .attr("dominant-baseline", "middle")
      .attr("font-family", ctx.config.fontFamily)
      .attr("font-size", size)
      .attr("font-weight", 900)
      .attr("letter-spacing", 0.6)
      .attr("fill", (d) => d === 0 ? ctx.textureFill : ctx.palette.sequence[d % ctx.palette.sequence.length])
      .text(ctx.config.brand);
    ctx.brandHandled = true;
  }

  function renderSliceShift(group, ctx) {
    const textId = ctx.uid("slice-source-text");
    const size = fittedFontSize(ctx.config.brand, 82, 365);
    ctx.defs.append("text")
      .attr("id", textId)
      .attr("x", 240).attr("y", 153)
      .attr("text-anchor", "middle").attr("dominant-baseline", "middle")
      .attr("font-family", ctx.config.fontFamily).attr("font-size", size).attr("font-weight", 900)
      .text(ctx.config.brand);
    const slices = Math.max(4, Math.round(5 + ctx.config.density * 2));
    const top = 96;
    const height = 118 / slices;
    ctx.d3.range(slices).forEach((index) => {
      const clipId = ctx.uid(`slice-clip-${index}`);
      ctx.defs.append("clipPath")
        .attr("id", clipId)
        .append("rect")
        .attr("x", 42).attr("y", top + index * height).attr("width", 396).attr("height", height + 1)
        .attr("transform", `skewX(${-10 + ctx.config.curvature * 20})`);
      group.append("use")
        .attr("class", "shifted-slice")
        .attr("href", `#${textId}`)
        .attr("clip-path", fragmentUrl(clipId))
        .attr("transform", `translate(${(index % 2 ? 1 : -1) * (8 + ctx.config.curvature * 16)},0)`)
        .attr("fill", index === Math.floor(slices / 2) ? ctx.textureFill : ctx.palette.sequence[index % ctx.palette.sequence.length]);
    });
    ctx.brandHandled = true;
  }

  function renderMultiStrokeWordmark(group, ctx) {
    const textId = ctx.uid("multi-stroke-source");
    const size = fittedFontSize(ctx.config.brand, 74, 350);
    ctx.defs.append("text")
      .attr("id", textId)
      .attr("x", 240).attr("y", 151)
      .attr("text-anchor", "middle").attr("dominant-baseline", "middle")
      .attr("font-family", ctx.config.fontFamily).attr("font-size", size).attr("font-weight", 850)
      .text(ctx.config.brand);
    const layers = [
      { width: 11, dash: "2 9", color: ctx.palette.roles.line },
      { width: 7, dash: "14 5", color: ctx.palette.roles.primaryDark },
      { width: 3, dash: "1 0", color: ctx.palette.roles.ink }
    ];
    group.selectAll("use.stroke-layer")
      .data(layers)
      .join("use")
      .attr("class", "stroke-layer")
      .attr("href", `#${textId}`)
      .attr("fill", "none")
      .attr("stroke", (d) => d.color)
      .attr("stroke-width", (d) => d.width)
      .attr("stroke-dasharray", (d) => d.dash)
      .attr("stroke-linejoin", "round");
    group.append("use").attr("class", "stroke-fill").attr("href", `#${textId}`).attr("fill", ctx.textureFill);
    ctx.brandHandled = true;
  }

  function renderExtrudedWordmark(group, ctx) {
    const steps = Math.max(5, Math.round(7 + ctx.config.density * 6));
    const size = fittedFontSize(ctx.config.brand, 69, 340);
    const angle = (-28 + ctx.config.curvature * 16) * Math.PI / 180;
    group.selectAll("text.depth-copy")
      .data(ctx.d3.range(steps).reverse())
      .join("text")
      .attr("class", "depth-copy")
      .attr("x", (d) => 240 + Math.cos(angle) * d * 3.2)
      .attr("y", (d) => 151 + Math.sin(angle) * d * 3.2)
      .attr("text-anchor", "middle").attr("dominant-baseline", "middle")
      .attr("font-family", ctx.config.fontFamily).attr("font-size", size).attr("font-weight", 900)
      .attr("fill", (d) => d === 0 ? ctx.textureFill : ctx.palette.sequence[(d + 1) % ctx.palette.sequence.length])
      .attr("stroke", (d) => d === 0 ? ctx.palette.roles.ink : "none")
      .attr("stroke-width", 1.4)
      .text(ctx.config.brand);
    ctx.brandHandled = true;
  }

  function renderLetterWeave(group, ctx) {
    const initials = Array.from(brandInitials(ctx.config.brand).padEnd(2, "A"));
    const bendA = ((initials[0].charCodeAt(0) % 13) - 6) * 2;
    const bendB = ((initials[1].charCodeAt(0) % 13) - 6) * 2;
    group.attr("data-weave-initials", initials.slice(0, 2).join(""));
    const maskId = ctx.uid("weave-crossing-mask");
    const mask = ctx.defs.append("mask")
      .attr("id", maskId)
      .attr("maskUnits", "userSpaceOnUse")
      .attr("x", 100).attr("y", 54).attr("width", 280).attr("height", 190);
    mask.append("rect").attr("x", 100).attr("y", 54).attr("width", 280).attr("height", 190).attr("fill", ctx.palette.roles.surface);
    mask.selectAll("circle")
      .data([[215, 140], [278, 156]])
      .join("circle")
      .attr("cx", (d) => d[0]).attr("cy", (d) => d[1]).attr("r", 13 + ctx.config.curvature * 7)
      .attr("fill", ctx.palette.allowed[0]);
    const line = ctx.d3.line().curve(ctx.d3.curveBasis);
    const pathA = line([[128, 204], [162 + bendA, 76], [238, 192 - bendB], [310 - bendA, 78], [350, 201]]);
    const pathB = line([[126, 88], [195, 204 - bendA], [240 + bendB, 94], [286, 204 + bendA], [354, 92]]);
    group.append("path")
      .attr("class", "weave-under")
      .attr("d", pathB).attr("fill", "none").attr("stroke", ctx.palette.roles.primaryDark)
      .attr("stroke-width", 23).attr("stroke-linecap", "square");
    group.append("path")
      .attr("class", "weave-over")
      .attr("d", pathA).attr("fill", "none").attr("stroke", ctx.textureFill)
      .attr("stroke-width", 23).attr("stroke-linecap", "square").attr("mask", fragmentUrl(maskId));
    group.selectAll("circle.weave-terminal")
      .data([[128, 204], [350, 201], [126, 88], [354, 92]])
      .join("circle").attr("class", "weave-terminal")
      .attr("cx", (d) => d[0]).attr("cy", (d) => d[1]).attr("r", 6).attr("fill", ctx.palette.roles.accent);
  }

  function renderResponsiveLockup(group, ctx) {
    const mode = ctx.effectiveWidth < 180 ? "compact" : (ctx.effectiveWidth < 360 ? "stacked" : "wide");
    const taglineFill = ctx.palette.roles.secondaryDark || ctx.palette.roles.ink;
    group.attr("data-lockup-mode", mode);
    const symbol = group.append("g").attr("class", `responsive-symbol responsive-symbol-${mode}`);
    const cells = [[0, 0], [1, 0], [0, 1], [1, 1]];
    const origin = mode === "wide" ? [104, 112] : [208, mode === "stacked" ? 68 : 86];
    symbol.selectAll("rect")
      .data(cells)
      .join("rect")
      .attr("x", (d) => origin[0] + d[0] * 36)
      .attr("y", (d) => origin[1] + d[1] * 36)
      .attr("width", 32).attr("height", 32)
      .attr("fill", (d, index) => index === 0 ? ctx.textureFill : ctx.palette.sequence[index % ctx.palette.sequence.length]);
    if (mode === "wide") {
      addText(group, ctx, { className: "responsive-brand", text: ctx.config.brand, x: 278, y: 137, size: fittedFontSize(ctx.config.brand, 47, 230), weight: 850, fill: ctx.palette.roles.ink });
      addText(group, ctx, { className: "responsive-tagline", text: ctx.config.tagline, x: 278, y: 176, size: fittedFontSize(ctx.config.tagline, 14, 220), weight: 650, tracking: 0.7, fill: taglineFill });
    } else if (mode === "stacked") {
      addText(group, ctx, { className: "responsive-brand", text: ctx.config.brand, x: 240, y: 196, size: fittedFontSize(ctx.config.brand, 42, 280), weight: 850, fill: ctx.palette.roles.ink });
      addText(group, ctx, { className: "responsive-tagline", text: ctx.config.tagline, x: 240, y: 228, size: fittedFontSize(ctx.config.tagline, 13, 270), weight: 650, tracking: 0.7, fill: taglineFill });
    } else {
      addText(group, ctx, { className: "responsive-initials", text: brandInitials(ctx.config.brand), x: 240, y: 124, size: 24, weight: 900, fill: ctx.palette.roles.surface });
      addText(group, ctx, { className: "responsive-brand", text: ctx.config.brand, x: 240, y: 208, size: fittedFontSize(ctx.config.brand, 30, 250), weight: 850, fill: ctx.palette.roles.ink });
    }
    ctx.brandHandled = true;
    ctx.taglineHandled = true;
  }

  function renderSpiralTrace(group, ctx) {
    const samples = Math.max(90, Math.round(120 * ctx.config.density));
    const turns = 2.4 + ctx.config.curvature * 2.6;
    const points = ctx.d3.range(samples).map((index) => {
      const t = index / (samples - 1);
      return {
        angle: t * Math.PI * 2 * turns,
        radius: 8 + t * (84 + ctx.config.curvature * 22)
      };
    });
    const spiral = ctx.d3.lineRadial()
      .angle((d) => d.angle)
      .radius((d) => d.radius)
      .curve(ctx.d3.curveCatmullRom.alpha(0.55));
    const mark = group.append("g").attr("class", "spiral-trace-mark").attr("transform", "translate(240,143)");
    mark.append("path")
      .attr("d", spiral(points))
      .attr("fill", "none")
      .attr("stroke", ctx.palette.roles.ink)
      .attr("stroke-width", 13)
      .attr("stroke-linecap", "round");
    mark.append("path")
      .attr("d", spiral(points))
      .attr("fill", "none")
      .attr("stroke", ctx.textureFill)
      .attr("stroke-width", 8)
      .attr("stroke-linecap", "round");
    const finalPoint = points[points.length - 1];
    const terminal = ctx.d3.pointRadial(finalPoint.angle, finalPoint.radius);
    mark.append("circle")
      .attr("class", "spiral-terminal")
      .attr("cx", terminal[0]).attr("cy", terminal[1]).attr("r", 7)
      .attr("fill", ctx.palette.roles.accent);
  }

  function renderOrbitNetwork(group, ctx) {
    const count = Math.max(7, Math.round(9 + ctx.config.density * 5));
    const random = seededRandom(ctx.d3, ctx.config.seed, "orbit-network");
    const nodes = [{ id: "core", x: 240, y: 143, fx: 240, fy: 143, r: 25 }]
      .concat(ctx.d3.range(count).map((index) => ({
        id: `node-${index}`,
        x: 240 + (random() - 0.5) * 160,
        y: 143 + (random() - 0.5) * 160,
        r: 7 + random() * 7
      })));
    const links = ctx.d3.range(count).map((index) => ({ source: "core", target: `node-${index}` }));
    for (let index = 0; index < count; index += 3) {
      links.push({ source: `node-${index}`, target: `node-${(index + 2) % count}` });
    }
    const simulation = ctx.d3.forceSimulation(nodes)
      .randomSource(ctx.d3.randomLcg(((ctx.config.seed >>> 0) ^ 0x51f15e) >>> 0))
      .force("charge", ctx.d3.forceManyBody().strength(-32))
      .force("radial", ctx.d3.forceRadial((d, index) => index === 0 ? 0 : 70 + index % 3 * 22, 240, 143).strength(0.72))
      .force("link", ctx.d3.forceLink(links).id((d) => d.id).distance((d, index) => 58 + index % 4 * 9).strength(0.2))
      .force("collide", ctx.d3.forceCollide((d) => d.r + 4).iterations(2))
      .stop();
    for (let tick = 0; tick < 120; tick += 1) simulation.tick();
    group.append("g")
      .attr("class", "orbit-links")
      .selectAll("line")
      .data(links)
      .join("line")
      .attr("x1", (d) => d.source.x).attr("y1", (d) => d.source.y)
      .attr("x2", (d) => d.target.x).attr("y2", (d) => d.target.y)
      .attr("stroke", ctx.palette.roles.line).attr("stroke-width", 2.2);
    group.append("g")
      .attr("class", "orbit-nodes")
      .selectAll("circle")
      .data(nodes)
      .join("circle")
      .attr("cx", (d) => d.x).attr("cy", (d) => d.y).attr("r", (d) => d.r)
      .attr("fill", (d, index) => index === 0 ? ctx.textureFill : ctx.palette.sequence[index % ctx.palette.sequence.length])
      .attr("stroke", ctx.palette.roles.background).attr("stroke-width", 2);
    addText(group, ctx, { className: "orbit-network-initials", text: brandInitials(ctx.config.brand), x: 240, y: 143, size: 14, weight: 850, fill: ctx.palette.roles.surface });
  }

  function renderGridActivation(group, ctx) {
    const columns = Math.max(8, Math.round(9 + ctx.config.density * 5));
    const rows = Math.max(5, Math.round(6 + ctx.config.density * 3));
    const cell = Math.min(28, 300 / columns);
    const gap = 4;
    const width = columns * cell;
    const height = rows * cell;
    const left = 240 - width / 2;
    const top = 143 - height / 2;
    const random = seededRandom(ctx.d3, ctx.config.seed, "grid-activation");
    const cells = [];
    for (let row = 0; row < rows; row += 1) {
      for (let column = 0; column < columns; column += 1) {
        const diagonal = Math.abs(column / Math.max(1, columns - 1) - row / Math.max(1, rows - 1));
        const ring = Math.abs(Math.hypot(column - columns / 2, row - rows / 2) - Math.min(columns, rows) * 0.3);
        cells.push({ row, column, active: diagonal < 0.16 || ring < 0.7 || random() < 0.13 * ctx.config.density });
      }
    }
    group.append("g").attr("class", "activation-grid")
      .selectAll("rect")
      .data(cells)
      .join("rect")
      .attr("x", (d) => left + d.column * cell + gap / 2)
      .attr("y", (d) => top + d.row * cell + gap / 2)
      .attr("width", cell - gap).attr("height", cell - gap)
      .attr("fill", (d, index) => d.active ? (index % 7 === 0 ? ctx.textureFill : ctx.palette.sequence[index % ctx.palette.sequence.length]) : ctx.palette.roles.quiet)
      .attr("data-active", (d) => d.active ? "true" : "false");
  }

  function renderContourFingerprint(group, ctx) {
    const gridWidth = 46;
    const gridHeight = 30;
    const random = seededRandom(ctx.d3, ctx.config.seed, "contour-field");
    const values = [];
    for (let y = 0; y < gridHeight; y += 1) {
      for (let x = 0; x < gridWidth; x += 1) {
        const dx = (x - gridWidth / 2) / gridWidth;
        const dy = (y - gridHeight / 2) / gridHeight;
        const radial = Math.exp(-(dx * dx * 5 + dy * dy * 8));
        const ridges = Math.sin(x * 0.42 + Math.cos(y * 0.31) * 2.2) * 0.13;
        values.push(radial + ridges + (random() - 0.5) * 0.035);
      }
    }
    const thresholdCount = Math.max(8, Math.round(10 + ctx.config.density * 8));
    const thresholds = ctx.d3.range(thresholdCount).map((index) => 0.08 + index * 0.76 / thresholdCount);
    const contours = ctx.d3.contours().size([gridWidth, gridHeight]).smooth(true).thresholds(thresholds)(values);
    const clipId = ctx.uid("contour-medallion-clip");
    ctx.defs.append("clipPath").attr("id", clipId).append("ellipse")
      .attr("cx", 240).attr("cy", 143).attr("rx", 122).attr("ry", 93);
    group.append("ellipse")
      .attr("class", "contour-field-base")
      .attr("cx", 240).attr("cy", 143).attr("rx", 122).attr("ry", 93)
      .attr("fill", ctx.textureFill).attr("stroke", ctx.palette.roles.ink).attr("stroke-width", 3);
    const contourGroup = group.append("g")
      .attr("class", "scalar-field-contours")
      .attr("clip-path", fragmentUrl(clipId))
      .attr("transform", `translate(102,53) scale(${276 / gridWidth},${180 / gridHeight})`);
    contourGroup.selectAll("path")
      .data(contours)
      .join("path")
      .attr("d", ctx.d3.geoPath())
      .attr("fill", "none")
      .attr("stroke", (d, index) => ctx.palette.sequence[index % ctx.palette.sequence.length])
      .attr("stroke-width", 0.48)
      .attr("vector-effect", "non-scaling-stroke");
  }

  function renderVoronoiShards(group, ctx) {
    const random = seededRandom(ctx.d3, ctx.config.seed, "voronoi-shards");
    const count = Math.max(14, Math.round(18 + ctx.config.density * 12));
    const sites = ctx.d3.range(count).map(() => [128 + random() * 224, 42 + random() * 202]);
    const voronoi = ctx.d3.Delaunay.from(sites).voronoi([120, 35, 360, 251]);
    const clipId = ctx.uid("voronoi-shard-clip");
    ctx.defs.append("clipPath").attr("id", clipId).append("path")
      .attr("d", `M240,39 C315,39 361,85 361,143 C361,205 310,247 240,247 C170,247 119,205 119,143 C119,85 165,39 240,39Z`);
    const line = ctx.d3.line().curve(ctx.d3.curveLinearClosed);
    group.append("g")
      .attr("class", "voronoi-shard-cells")
      .attr("clip-path", fragmentUrl(clipId))
      .selectAll("path")
      .data(Array.from(voronoi.cellPolygons()))
      .join("path")
      .attr("d", line)
      .attr("fill", (d, index) => index === 0 ? ctx.textureFill : ctx.palette.sequence[index % ctx.palette.sequence.length])
      .attr("stroke", ctx.palette.roles.background)
      .attr("stroke-width", 2.2 + ctx.config.curvature * 1.4);
    group.append("path")
      .attr("class", "voronoi-shard-outline")
      .attr("d", `M240,39 C315,39 361,85 361,143 C361,205 310,247 240,247 C170,247 119,205 119,143 C119,85 165,39 240,39Z`)
      .attr("fill", "none").attr("stroke", ctx.palette.roles.ink).attr("stroke-width", 3);
  }

  function renderAnimalFacets(group, ctx) {
    const animalPath = originalAnimalPath(ctx);
    const polygon = originalAnimalPoints(ctx.config.curvature);
    const clipId = ctx.uid("animal-facet-clip");
    ctx.defs.append("clipPath").attr("id", clipId).append("path").attr("d", animalPath);
    const random = seededRandom(ctx.d3, ctx.config.seed, "animal-facets");
    const target = Math.max(22, Math.round(25 + ctx.config.density * 18));
    const points = polygon.slice();
    let attempts = 0;
    while (points.length < target && attempts < target * 30) {
      const point = [112 + random() * 232, 94 + random() * 116];
      if (ctx.d3.polygonContains(polygon, point)) points.push(point);
      attempts += 1;
    }
    const delaunay = ctx.d3.Delaunay.from(points);
    const triangles = Array.from(delaunay.trianglePolygons());
    const line = ctx.d3.line().curve(ctx.d3.curveLinearClosed);
    group.append("g")
      .attr("class", "animal-delaunay-facets")
      .attr("clip-path", fragmentUrl(clipId))
      .selectAll("path")
      .data(triangles)
      .join("path")
      .attr("d", line)
      .attr("fill", (d, index) => index === 0 ? ctx.textureFill : ctx.palette.sequence[index % ctx.palette.sequence.length])
      .attr("stroke", ctx.palette.roles.background)
      .attr("stroke-width", 1.7);
    group.append("path")
      .attr("class", "original-animal-outline")
      .attr("data-original-procedural", "true")
      .attr("d", animalPath).attr("fill", "none")
      .attr("stroke", ctx.palette.roles.ink).attr("stroke-width", 3.5).attr("stroke-linejoin", "round");
  }

  function renderAnimalSurfaceMask(group, ctx) {
    const animalPath = originalAnimalPath(ctx);
    const clipId = ctx.uid("animal-surface-clip");
    ctx.defs.append("clipPath").attr("id", clipId).append("path").attr("d", animalPath);
    const surface = group.append("g")
      .attr("class", "animal-surface-bands")
      .attr("clip-path", fragmentUrl(clipId));
    surface.append("rect").attr("x", 104).attr("y", 88).attr("width", 248).attr("height", 128).attr("fill", ctx.textureFill);
    const bandCount = Math.max(6, Math.round(7 + ctx.config.density * 5));
    const line = ctx.d3.line().curve(ctx.d3.curveBasis);
    const bands = ctx.d3.range(bandCount).map((index) => ctx.d3.range(9).map((column) => [
      104 + column * 31,
      103 + index * 104 / Math.max(1, bandCount - 1) + Math.sin(column * 0.9 + index) * (5 + ctx.config.curvature * 10)
    ]));
    surface.selectAll("path")
      .data(bands)
      .join("path")
      .attr("d", line).attr("fill", "none")
      .attr("stroke", (d, index) => ctx.palette.sequence[(index + 1) % ctx.palette.sequence.length])
      .attr("stroke-width", 10).attr("stroke-linecap", "round");
    group.append("path")
      .attr("class", "original-animal-outline")
      .attr("data-original-procedural", "true")
      .attr("d", animalPath).attr("fill", "none").attr("stroke", ctx.palette.roles.ink).attr("stroke-width", 3.5);
  }

  function renderNegativeSpaceReveal(group, ctx) {
    const maskId = ctx.uid("negative-space-mask");
    const initial = Array.from(brandInitials(ctx.config.brand))[0] || "A";
    const mask = ctx.defs.append("mask")
      .attr("id", maskId).attr("maskUnits", "userSpaceOnUse")
      .attr("x", 105).attr("y", 40).attr("width", 270).attr("height", 210);
    mask.selectAll("circle")
      .data([[190, 135, 76], [290, 135, 76], [240, 182, 66]])
      .join("circle")
      .attr("cx", (d) => d[0]).attr("cy", (d) => d[1]).attr("r", (d) => d[2])
      .attr("fill", ctx.palette.roles.surface);
    mask.append("text")
      .attr("x", 240).attr("y", 147).attr("text-anchor", "middle").attr("dominant-baseline", "middle")
      .attr("font-family", ctx.config.fontFamily).attr("font-size", 118).attr("font-weight", 900)
      .attr("fill", ctx.palette.allowed[0]).text(initial);
    group.append("g")
      .attr("class", "negative-space-primitives")
      .attr("data-text-proxy", "negative-space")
      .attr("data-text-role", "initials")
      .attr("mask", fragmentUrl(maskId))
      .selectAll("circle")
      .data([[190, 135, 76], [290, 135, 76], [240, 182, 66]])
      .join("circle")
      .attr("cx", (d) => d[0]).attr("cy", (d) => d[1]).attr("r", (d) => d[2])
      .attr("fill", (d, index) => index === 0 ? ctx.textureFill : ctx.palette.sequence[index % ctx.palette.sequence.length]);
    group.append("text")
      .attr("class", "negative-space-outline")
      .attr("data-text-role", "initials")
      .attr("x", 240).attr("y", 147).attr("text-anchor", "middle").attr("dominant-baseline", "middle")
      .attr("font-family", ctx.config.fontFamily).attr("font-size", 118).attr("font-weight", 900)
      .attr("fill", "none").attr("stroke", ctx.palette.roles.background).attr("stroke-width", 2).text(initial);
  }

  function renderFoldedRibbon(group, ctx) {
    const points = [[86, 187], [153, 92], [224, 187], [294, 92], [394, 178]];
    const line = ctx.d3.line().curve(ctx.d3.curveCatmullRom.alpha(0.25 + ctx.config.curvature * 0.65));
    const ribbon = line(points);
    group.append("path")
      .attr("class", "ribbon-clearance")
      .attr("d", ribbon).attr("fill", "none")
      .attr("stroke", ctx.palette.roles.background).attr("stroke-width", 48).attr("stroke-linecap", "square").attr("stroke-linejoin", "miter");
    group.append("path")
      .attr("class", "ribbon-body")
      .attr("d", ribbon).attr("fill", "none")
      .attr("stroke", ctx.textureFill).attr("stroke-width", 34).attr("stroke-linecap", "square").attr("stroke-linejoin", "miter");
    const overpass = ctx.d3.line().curve(ctx.d3.curveLinear)([[205, 160], [224, 187], [247, 156]]);
    group.append("path")
      .attr("class", "ribbon-overpass-gap")
      .attr("d", overpass).attr("fill", "none").attr("stroke", ctx.palette.roles.background).attr("stroke-width", 46).attr("stroke-linecap", "square");
    group.append("path")
      .attr("class", "ribbon-overpass")
      .attr("d", overpass).attr("fill", "none").attr("stroke", ctx.palette.roles.primaryDark).attr("stroke-width", 34).attr("stroke-linecap", "square");
    group.selectAll("polygon.ribbon-fold")
      .data([[[139, 103], [153, 92], [169, 111]], [[278, 111], [294, 92], [309, 110]]])
      .join("polygon")
      .attr("class", "ribbon-fold")
      .attr("points", (d) => d.map((point) => point.join(",")).join(" "))
      .attr("fill", ctx.palette.roles.ink);
  }

  function renderBooleanLens(group, ctx) {
    const clipId = ctx.uid("boolean-lens-clip");
    ctx.defs.append("clipPath").attr("id", clipId).append("circle").attr("cx", 202).attr("cy", 143).attr("r", 82);
    group.append("circle").attr("class", "boolean-shape-a").attr("cx", 202).attr("cy", 143).attr("r", 82).attr("fill", ctx.palette.roles.primary);
    group.append("circle").attr("class", "boolean-shape-b").attr("cx", 278).attr("cy", 143).attr("r", 82).attr("fill", ctx.palette.sequence[1 % ctx.palette.sequence.length]);
    group.append("circle")
      .attr("class", "boolean-intersection")
      .attr("cx", 278).attr("cy", 143).attr("r", 82)
      .attr("clip-path", fragmentUrl(clipId)).attr("fill", ctx.textureFill);
    group.append("path")
      .attr("class", "boolean-axis")
      .attr("d", "M240,61V225")
      .attr("fill", "none").attr("stroke", ctx.palette.roles.background).attr("stroke-width", 2);
    addText(group, ctx, { className: "boolean-initials", text: brandInitials(ctx.config.brand), x: 240, y: 143, size: 28, weight: 900, fill: ctx.palette.roles.surface });
  }

  function renderRadiantPulse(group, ctx) {
    const count = Math.max(18, Math.round(22 + ctx.config.density * 14));
    const random = seededRandom(ctx.d3, ctx.config.seed, "radiant-pulse");
    const rays = ctx.d3.range(count).map((index) => {
      const angle = index * Math.PI * 2 / count;
      const inner = 47;
      const outer = 72 + random() * 48 + Math.sin(index * 1.7) * 10 * ctx.config.curvature;
      return { angle, inner, outer, width: 1.5 + random() * 3.2 };
    });
    group.append("g").attr("class", "radiant-rays")
      .selectAll("line")
      .data(rays)
      .join("line")
      .attr("x1", (d) => 240 + Math.cos(d.angle) * d.inner)
      .attr("y1", (d) => 143 + Math.sin(d.angle) * d.inner)
      .attr("x2", (d) => 240 + Math.cos(d.angle) * d.outer)
      .attr("y2", (d) => 143 + Math.sin(d.angle) * d.outer)
      .attr("stroke", (d, index) => ctx.palette.sequence[index % ctx.palette.sequence.length])
      .attr("stroke-width", (d) => d.width).attr("stroke-linecap", "round");
    group.append("circle").attr("class", "radiant-core").attr("cx", 240).attr("cy", 143).attr("r", 43)
      .attr("fill", ctx.textureFill).attr("stroke", ctx.palette.roles.ink).attr("stroke-width", 3);
    const initials = brandInitials(ctx.config.brand);
    const labelRadius = clamp(22 + ctx.config.density * 2, 23, 27);
    group.append("circle")
      .attr("class", "radiant-label-disc")
      .attr("cx", 240).attr("cy", 143).attr("r", labelRadius)
      .attr("fill", ctx.palette.roles.inkDark)
      .attr("stroke", ctx.palette.roles.surface).attr("stroke-width", 2);
    addText(group, ctx, { className: "radiant-initials", text: initials, x: 240, y: 143, size: fittedFontSize(initials, 27, labelRadius * 1.55), weight: 900, fill: ctx.palette.roles.surface });
  }

  function renderParametricWave(group, ctx) {
    const samples = Math.max(180, Math.round(220 * ctx.config.density));
    const phase = (ctx.config.seed % 360) * Math.PI / 180;
    const frequencyX = 3;
    const frequencyY = 2 + Math.round(ctx.config.curvature * 2);
    const points = ctx.d3.range(samples).map((index) => {
      const t = index / samples * Math.PI * 2;
      return [240 + Math.sin(frequencyX * t + phase) * 116, 143 + Math.sin(frequencyY * t) * 78];
    });
    const line = ctx.d3.line().curve(ctx.d3.curveCatmullRomClosed.alpha(0.5));
    group.append("path")
      .attr("class", "harmonic-curve-shadow")
      .attr("d", line(points)).attr("fill", "none")
      .attr("stroke", ctx.palette.roles.line).attr("stroke-width", 17).attr("stroke-linejoin", "round");
    group.append("path")
      .attr("class", "harmonic-curve")
      .attr("d", line(points)).attr("fill", "none")
      .attr("stroke", ctx.textureFill).attr("stroke-width", 10).attr("stroke-linejoin", "round");
    group.append("circle").attr("cx", 240).attr("cy", 143).attr("r", 10).attr("fill", ctx.palette.roles.accent);
  }

  function renderKaleidoscopeWedges(group, ctx) {
    const motifId = ctx.uid("kaleidoscope-motif");
    ctx.defs.append("path")
      .attr("id", motifId)
      .attr("d", `M0,-30 C${18 + ctx.config.curvature * 25},-52 ${42 + ctx.config.curvature * 16},-86 0,-116 C-9,-84 -13,-58 0,-30Z`);
    const sectors = Math.max(8, Math.round(10 + ctx.config.density * 6));
    const mark = group.append("g").attr("class", "kaleidoscope-sector-field").attr("transform", "translate(240,143)");
    mark.selectAll("use")
      .data(ctx.d3.range(sectors))
      .join("use")
      .attr("href", `#${motifId}`)
      .attr("transform", (d) => `rotate(${d * 360 / sectors}) scale(${d % 2 ? -1 : 1},1)`)
      .attr("fill", (d) => d === 0 ? ctx.textureFill : ctx.palette.sequence[d % ctx.palette.sequence.length])
      .attr("stroke", ctx.palette.roles.background).attr("stroke-width", 1.4);
    mark.append("circle").attr("r", 29).attr("fill", ctx.palette.roles.background).attr("stroke", ctx.palette.roles.ink).attr("stroke-width", 3);
    addText(mark, ctx, { className: "kaleidoscope-initials", text: brandInitials(ctx.config.brand), x: 0, y: 0, size: 18, weight: 900, fill: ctx.palette.roles.ink });
  }

  function renderPolarHalo(group, ctx) {
    const count = Math.max(9, Math.round(10 + ctx.config.density * 6));
    const random = seededRandom(ctx.d3, ctx.config.seed, "polar-halo");
    const gap = 0.035 + (1 - ctx.config.curvature) * 0.04;
    const values = ctx.d3.range(count).map((index) => ({ index, value: 0.35 + random() * 0.65 }));
    const arc = ctx.d3.arc()
      .innerRadius((d) => 64 + d.index % 3 * 8)
      .outerRadius((d) => 76 + d.index % 3 * 8 + d.value * 22)
      .startAngle((d) => d.index * Math.PI * 2 / count + gap)
      .endAngle((d) => (d.index + 1) * Math.PI * 2 / count - gap);
    const mark = group.append("g").attr("class", "polar-data-arcs").attr("transform", "translate(240,143)");
    mark.selectAll("path")
      .data(values)
      .join("path")
      .attr("d", arc)
      .attr("fill", (d) => d.index === 0 ? ctx.textureFill : ctx.palette.sequence[d.index % ctx.palette.sequence.length]);
    mark.append("circle").attr("r", 52).attr("fill", ctx.palette.roles.surface).attr("stroke", ctx.palette.roles.ink).attr("stroke-width", 3);
    addText(mark, ctx, { className: "polar-initials", text: brandInitials(ctx.config.brand), x: 0, y: -7, size: 28, weight: 900, fill: ctx.palette.roles.ink });
    addText(mark, ctx, { className: "polar-value", text: String(ctx.config.seed), x: 0, y: 23, size: 12, weight: 750, tracking: 0.6, fill: ctx.palette.roles.inkDark });
  }

  function renderApertureIris(group, ctx) {
    const blades = Math.max(7, Math.round(7 + ctx.config.density * 3));
    const outer = 107;
    const inner = 30 + (1 - ctx.config.curvature) * 23;
    const bladePath = `M0,${-outer} C${outer * 0.66},${-outer * 0.84} ${outer},${-outer * 0.18} ${outer * 0.7},${outer * 0.2} L${inner * 0.55},${inner * 0.82} C${inner * 0.1},${inner * 0.45} ${-inner * 0.22},${-inner * 0.28} 0,${-inner}Z`;
    const mark = group.append("g").attr("class", "aperture-blades").attr("transform", "translate(240,151)");
    mark.selectAll("path")
      .data(ctx.d3.range(blades))
      .join("path")
      .attr("d", bladePath)
      .attr("transform", (d) => `rotate(${d * 360 / blades + ctx.config.curvature * 18})`)
      .attr("fill", (d) => d === 0 ? ctx.textureFill : ctx.palette.sequence[d % ctx.palette.sequence.length])
      .attr("stroke", ctx.palette.roles.background).attr("stroke-width", 1.7);
    mark.append("circle")
      .attr("class", "iris-opening")
      .attr("r", inner).attr("fill", ctx.palette.roles.background)
      .attr("stroke", ctx.palette.roles.ink).attr("stroke-width", 3);
    mark.append("circle").attr("r", inner * 0.32).attr("fill", ctx.palette.roles.accent);
  }

  function renderTerminalExtension(group, ctx) {
    const curvature = ctx.config.curvature;
    group.append("path")
      .attr("class", "terminal-extension-rule")
      .attr("d", `M78,177 H${334 + curvature * 34} Q${370 + curvature * 18},177 ${386 + curvature * 8},${157 - curvature * 18} V${110 - curvature * 10}`)
      .attr("fill", "none")
      .attr("stroke", ctx.textureFill)
      .attr("stroke-width", 8 + ctx.config.density * 2)
      .attr("stroke-linecap", "round")
      .attr("stroke-linejoin", "round");
    group.append("circle")
      .attr("class", "terminal-extension-anchor")
      .attr("cx", 78).attr("cy", 177).attr("r", 7)
      .attr("fill", ctx.palette.roles.accent);
    addText(group, ctx, {
      className: "terminal-extension-wordmark",
      role: "brand",
      text: ctx.config.brand,
      x: 230,
      y: 132,
      size: fittedFontSize(ctx.config.brand, 68, 302, 10),
      weight: 820,
      tracking: 0.8,
      fill: ctx.palette.roles.ink,
      maxWidth: 302,
      minimumSize: 10
    });
    ctx.brandHandled = true;
  }

  function renderVerticalRailWordmark(group, ctx) {
    const characters = Array.from(ctx.config.brand || "?");
    const count = Math.max(1, characters.length);
    const top = 48;
    const bottom = 226;
    const step = count === 1 ? 0 : (bottom - top) / (count - 1);
    const size = clamp(Math.min(27, 154 / count + 8), 7, 27);
    group.append("line")
      .attr("class", "vertical-reading-rail")
      .attr("x1", 205).attr("y1", top - 15)
      .attr("x2", 205).attr("y2", bottom + 15)
      .attr("stroke", ctx.textureFill)
      .attr("stroke-width", 9)
      .attr("stroke-linecap", "round");
    group.selectAll("circle.vertical-rail-stop")
      .data([top - 15, bottom + 15])
      .join("circle")
      .attr("class", "vertical-rail-stop")
      .attr("cx", 205).attr("cy", (d) => d).attr("r", 7)
      .attr("fill", ctx.palette.roles.accent);
    if (count > 12) {
      addText(group, ctx, {
        className: "vertical-rail-compact-wordmark",
        role: "brand",
        text: ctx.config.brand,
        x: 246,
        y: 139,
        size: fittedFontSize(ctx.config.brand, 24, 168, 7),
        weight: 820,
        tracking: 0.5,
        fill: ctx.palette.roles.ink,
        maxWidth: 168,
        minimumSize: 7
      }).attr("transform", "rotate(-90,246,139)");
      ctx.brandHandled = true;
      return;
    }
    characters.forEach((character, index) => {
      addText(group, ctx, {
        className: "vertical-rail-glyph",
        role: "brand",
        text: character,
        x: 244,
        y: count === 1 ? 137 : top + index * step,
        size,
        weight: 820,
        fill: index % 2 ? ctx.palette.roles.primary : ctx.palette.roles.ink
      }).attr("data-text-layer-suffix", index + 1);
    });
    ctx.brandHandled = true;
  }

  function renderHingedGlyphFan(group, ctx) {
    const characters = Array.from(ctx.config.brand || "?");
    const count = Math.max(1, characters.length);
    const span = Math.min(310, Math.max(70, count * 38));
    const step = count === 1 ? 0 : span / (count - 1);
    const start = 240 - span / 2;
    const size = clamp(Math.min(58, 292 / count * 1.45), 9, 58);
    group.append("line")
      .attr("class", "hinge-baseline")
      .attr("x1", start - 18).attr("x2", start + span + 18)
      .attr("y1", 178).attr("y2", 178)
      .attr("stroke", ctx.palette.roles.line).attr("stroke-width", 4);
    if (count > 12) {
      const angle = (ctx.config.curvature - 0.5) * 12;
      group.append("circle")
        .attr("class", "glyph-hinge compact-hinge")
        .attr("cx", 240).attr("cy", 178).attr("r", 6)
        .attr("fill", ctx.palette.roles.accent);
      addText(group, ctx, {
        className: "hinged-compact-wordmark",
        role: "brand",
        text: ctx.config.brand,
        x: 240,
        y: 139,
        size: fittedFontSize(ctx.config.brand, 42, 306, 8),
        weight: 820,
        tracking: 0.45,
        fill: ctx.palette.roles.ink,
        maxWidth: 306,
        minimumSize: 8
      }).attr("transform", `rotate(${angle},240,178)`);
      ctx.brandHandled = true;
      return;
    }
    characters.forEach((character, index) => {
      const x = count === 1 ? 240 : start + index * step;
      const normalized = count === 1 ? 0 : index / (count - 1) * 2 - 1;
      const angle = normalized * (4 + ctx.config.curvature * 9);
      group.append("circle")
        .attr("class", "glyph-hinge")
        .attr("cx", x).attr("cy", 178).attr("r", 4.5)
        .attr("fill", ctx.palette.sequence[index % ctx.palette.sequence.length]);
      addText(group, ctx, {
        className: "hinged-brand-glyph",
        role: "brand",
        text: character,
        x,
        y: 143,
        size,
        weight: 820,
        fill: ctx.palette.roles.ink
      })
        .attr("transform", `rotate(${angle},${x},178)`)
        .attr("data-text-layer-suffix", index + 1);
    });
    ctx.brandHandled = true;
  }

  function renderJustifiedWordBlock(group, ctx) {
    const blockWidth = 306;
    group.selectAll("rect.justification-rail")
      .data([78, 402])
      .join("rect")
      .attr("class", "justification-rail")
      .attr("x", (d) => d - 4).attr("y", 75)
      .attr("width", 8).attr("height", 132)
      .attr("rx", 4)
      .attr("fill", (d, index) => index ? ctx.palette.roles.accent : ctx.textureFill);
    const lines = balancedTextLines(ctx.config.brand);
    const wordBlock = addText(group, ctx, {
      className: "justified-brand-block",
      role: "brand",
      text: "",
      x: 240,
      y: 141,
      size: 48,
      weight: 820,
      tracking: 0.4,
      fill: ctx.palette.roles.ink,
    })
      .attr("aria-label", ctx.config.brand)
      .attr("data-text-fit", "justified-2-lines")
      .attr("data-text-line-count", lines.length);
    const sourceHasSpaces = /\s/u.test(ctx.config.brand);
    lines.forEach((line, index) => {
      const renderedLine = sourceHasSpaces && index < lines.length - 1 ? `${line} ` : line;
      const lineSelection = wordBlock.append("tspan")
        .attr("x", 240)
        .attr("y", 141 + (index - (lines.length - 1) / 2) * 52)
        .attr("data-text-line", index + 1)
        .text(renderedLine);
      fitTextToWidth(lineSelection, blockWidth, 14);
      lineSelection
        .attr("textLength", blockWidth)
        .attr("lengthAdjust", "spacing")
        .attr("data-text-fit", "justified-spacing");
    });
    group.append("line")
      .attr("class", "justification-measure")
      .attr("x1", 87).attr("x2", 393).attr("y1", 215).attr("y2", 215)
      .attr("stroke", ctx.palette.roles.line).attr("stroke-width", 3);
    ctx.brandHandled = true;
  }

  function renderFillOutlineCadence(group, ctx) {
    const characters = Array.from(ctx.config.brand || "?");
    const count = Math.max(1, characters.length);
    const span = Math.min(330, Math.max(70, count * 42));
    const step = count === 1 ? 0 : span / (count - 1);
    const start = 240 - span / 2;
    const size = clamp(Math.min(60, count === 1 ? 60 : step * 1.02), 9, 60);
    if (count > 12) {
      addText(group, ctx, {
        className: "cadence-compact-wordmark",
        role: "brand",
        text: ctx.config.brand,
        x: 240,
        y: 143,
        size: fittedFontSize(ctx.config.brand, 42, 320, 8),
        weight: 850,
        tracking: 0.4,
        fill: ctx.palette.roles.background,
        maxWidth: 320,
        minimumSize: 8
      })
        .attr("stroke", ctx.palette.roles.ink)
        .attr("stroke-width", 1.8)
        .attr("paint-order", "stroke fill");
      group.append("path")
        .attr("class", "cadence-index")
        .attr("d", "M80,194H400")
        .attr("stroke", ctx.textureFill).attr("stroke-width", 5).attr("stroke-linecap", "round");
      ctx.brandHandled = true;
      return;
    }
    characters.forEach((character, index) => {
      const outline = index % 2 === 1;
      addText(group, ctx, {
        className: "cadence-brand-glyph",
        role: "brand",
        text: character,
        x: count === 1 ? 240 : start + index * step,
        y: 143,
        size,
        weight: 850,
        fill: outline ? "none" : ctx.palette.sequence[index % ctx.palette.sequence.length]
      })
        .attr("stroke", outline ? ctx.palette.roles.ink : "none")
        .attr("stroke-width", outline ? Math.max(1.5, size * 0.055) : 0)
        .attr("paint-order", "stroke")
        .attr("data-text-layer-suffix", index + 1);
    });
    group.append("path")
      .attr("class", "cadence-index")
      .attr("d", `M${start - 10},194 H${start + span + 10}`)
      .attr("stroke", ctx.textureFill).attr("stroke-width", 5).attr("stroke-linecap", "round");
    ctx.brandHandled = true;
  }

  function renderPunctuationArmature(group, ctx) {
    const inset = 78 + ctx.config.curvature * 18;
    const outer = 402 - ctx.config.curvature * 18;
    const top = 72;
    const bottom = 205;
    group.append("path")
      .attr("class", "punctuation-bracket-left")
      .attr("d", `M${inset + 28},${top} H${inset} V${bottom} H${inset + 28}`)
      .attr("fill", "none").attr("stroke", ctx.textureFill)
      .attr("stroke-width", 10).attr("stroke-linecap", "round").attr("stroke-linejoin", "round");
    group.append("path")
      .attr("class", "punctuation-bracket-right")
      .attr("d", `M${outer - 28},${top} H${outer} V${bottom} H${outer - 28}`)
      .attr("fill", "none").attr("stroke", ctx.palette.roles.accent)
      .attr("stroke-width", 10).attr("stroke-linecap", "round").attr("stroke-linejoin", "round");
    group.selectAll("circle.punctuation-stop")
      .data([[inset + 45, 92], [outer - 45, 185]])
      .join("circle")
      .attr("class", "punctuation-stop")
      .attr("cx", (d) => d[0]).attr("cy", (d) => d[1]).attr("r", 7)
      .attr("fill", ctx.palette.roles.primaryDark);
    addText(group, ctx, {
      className: "punctuation-armature-wordmark",
      role: "brand",
      text: ctx.config.brand,
      x: 240,
      y: 139,
      size: fittedFontSize(ctx.config.brand, 58, 250, 10),
      weight: 820,
      tracking: 1,
      fill: ctx.palette.roles.ink,
      maxWidth: 250,
      minimumSize: 10
    });
    ctx.brandHandled = true;
  }

  function renderCirclePackCluster(group, ctx) {
    const random = seededRandom(ctx.d3, ctx.config.seed, "circle-pack-cluster");
    const count = Math.max(9, Math.round(10 + ctx.config.density * 7));
    const data = { children: ctx.d3.range(count).map((index) => ({ value: 1 + random() * (4 + index % 3) })) };
    const root = ctx.d3.pack().size([204, 184]).padding(3 + (1 - ctx.config.curvature) * 4)(
      ctx.d3.hierarchy(data).sum((d) => d.value || 0)
    );
    const mark = group.append("g").attr("class", "hierarchical-circle-pack").attr("transform", "translate(138,48)");
    mark.selectAll("circle.pack-disc")
      .data(root.leaves())
      .join("circle")
      .attr("class", "pack-disc")
      .attr("cx", (d) => d.x).attr("cy", (d) => d.y).attr("r", (d) => d.r)
      .attr("fill", (d, index) => index === 0 ? ctx.textureFill : ctx.palette.sequence[index % ctx.palette.sequence.length])
      .attr("stroke", ctx.palette.roles.background).attr("stroke-width", 2);
    mark.append("circle")
      .attr("class", "pack-boundary")
      .attr("cx", root.x).attr("cy", root.y).attr("r", root.r)
      .attr("fill", "none").attr("stroke", ctx.palette.roles.ink).attr("stroke-width", 3);
  }

  function renderTreemapMosaic(group, ctx) {
    const random = seededRandom(ctx.d3, ctx.config.seed, "treemap-mosaic");
    const count = Math.max(8, Math.round(8 + ctx.config.density * 8));
    const hierarchy = ctx.d3.hierarchy({ children: ctx.d3.range(count).map((index) => ({ value: 1 + random() * (7 + index % 4) })) })
      .sum((d) => d.value || 0)
      .sort((a, b) => b.value - a.value);
    ctx.d3.treemap()
      .size([242, 174])
      .paddingInner(2 + (1 - ctx.config.curvature) * 3)
      .round(true)(hierarchy);
    const mark = group.append("g").attr("class", "hierarchical-treemap").attr("transform", "translate(119,47)");
    mark.selectAll("rect.treemap-leaf")
      .data(hierarchy.leaves())
      .join("rect")
      .attr("class", "treemap-leaf")
      .attr("x", (d) => d.x0).attr("y", (d) => d.y0)
      .attr("width", (d) => Math.max(0, d.x1 - d.x0))
      .attr("height", (d) => Math.max(0, d.y1 - d.y0))
      .attr("rx", 2 + ctx.config.curvature * 7)
      .attr("fill", (d, index) => index === 0 ? ctx.textureFill : ctx.palette.sequence[index % ctx.palette.sequence.length]);
    mark.append("rect")
      .attr("class", "treemap-boundary")
      .attr("width", 242).attr("height", 174).attr("rx", 8)
      .attr("fill", "none").attr("stroke", ctx.palette.roles.ink).attr("stroke-width", 3);
  }

  function renderConvexHullShells(group, ctx) {
    const random = seededRandom(ctx.d3, ctx.config.seed, "convex-hull-shells");
    let points = ctx.d3.range(Math.max(24, Math.round(26 + ctx.config.density * 18))).map(() => {
      const angle = random() * Math.PI * 2;
      const radius = Math.sqrt(random());
      return [240 + Math.cos(angle) * radius * 118, 139 + Math.sin(angle) * radius * 88];
    });
    const shells = [];
    while (points.length >= 3 && shells.length < 7) {
      const hull = ctx.d3.polygonHull(points);
      if (!hull || hull.length < 3) break;
      shells.push(hull);
      const keys = new Set(hull.map((point) => `${point[0].toFixed(5)},${point[1].toFixed(5)}`));
      points = points.filter((point) => !keys.has(`${point[0].toFixed(5)},${point[1].toFixed(5)}`));
    }
    const line = ctx.d3.line().curve(ctx.d3.curveLinearClosed);
    group.append("g").attr("class", "convex-hull-peeling")
      .selectAll("path.hull-shell")
      .data(shells)
      .join("path")
      .attr("class", "hull-shell")
      .attr("d", line)
      .attr("fill", (d, index) => index === shells.length - 1 ? ctx.textureFill : "none")
      .attr("stroke", (d, index) => ctx.palette.sequence[index % ctx.palette.sequence.length])
      .attr("stroke-width", (d, index) => Math.max(2, 7 - index * 0.65))
      .attr("stroke-linejoin", "round");
    group.selectAll("circle.hull-core-point")
      .data(points.slice(0, 8))
      .join("circle")
      .attr("class", "hull-core-point")
      .attr("cx", (d) => d[0]).attr("cy", (d) => d[1]).attr("r", 3.5)
      .attr("fill", ctx.palette.roles.ink);
  }

  function renderPhyllotaxisBloom(group, ctx) {
    const count = Math.max(42, Math.round(48 + ctx.config.density * 32));
    const goldenAngle = Math.PI * (3 - Math.sqrt(5));
    const maxRadius = 104;
    const seeds = ctx.d3.range(count).map((index) => {
      const radius = maxRadius * Math.sqrt((index + 0.5) / count);
      const angle = index * goldenAngle + ctx.config.curvature * 0.35;
      return {
        x: 240 + Math.cos(angle) * radius,
        y: 139 + Math.sin(angle) * radius,
        r: 2.8 + (1 - index / count) * 4.8
      };
    });
    group.append("g").attr("class", "golden-angle-seed-field")
      .selectAll("circle.seed-disc")
      .data(seeds)
      .join("circle")
      .attr("class", "seed-disc")
      .attr("cx", (d) => d.x).attr("cy", (d) => d.y).attr("r", (d) => d.r)
      .attr("fill", (d, index) => index === 0 ? ctx.textureFill : ctx.palette.sequence[index % ctx.palette.sequence.length]);
    group.append("circle")
      .attr("class", "phyllotaxis-boundary")
      .attr("cx", 240).attr("cy", 139).attr("r", maxRadius + 7)
      .attr("fill", "none").attr("stroke", ctx.palette.roles.ink).attr("stroke-width", 2.5);
  }

  function renderTangencyChain(group, ctx) {
    const scale = clamp(0.82 + (ctx.config.density - 0.5) * 0.12, 0.82, 1.02);
    const radii = [18, 25, 15, 22, 14, 24, 18].map((radius) => radius * scale);
    const angles = [0.12, -0.18, 0.2, -0.16, 0.12, -0.08].map((angle) => angle * (0.65 + ctx.config.curvature));
    const circles = [{ x: 120, y: 142, r: radii[0] }];
    for (let index = 1; index < radii.length; index += 1) {
      const previous = circles[index - 1];
      const distance = previous.r + radii[index];
      const angle = angles[index - 1];
      circles.push({
        x: previous.x + Math.cos(angle) * distance,
        y: previous.y + Math.sin(angle) * distance,
        r: radii[index]
      });
    }
    group.append("g").attr("class", "mutually-tangent-chain")
      .selectAll("circle.tangent-disc")
      .data(circles)
      .join("circle")
      .attr("class", "tangent-disc")
      .attr("cx", (d) => d.x).attr("cy", (d) => d.y).attr("r", (d) => d.r)
      .attr("fill", (d, index) => index === Math.floor(circles.length / 2) ? ctx.textureFill : ctx.palette.sequence[index % ctx.palette.sequence.length])
      .attr("stroke", ctx.palette.roles.ink).attr("stroke-width", 2.2);
    group.selectAll("circle.tangency-contact")
      .data(circles.slice(1).map((circle, index) => {
        const previous = circles[index];
        const total = previous.r + circle.r;
        return {
          x: previous.x + (circle.x - previous.x) * previous.r / total,
          y: previous.y + (circle.y - previous.y) * previous.r / total
        };
      }))
      .join("circle")
      .attr("class", "tangency-contact")
      .attr("cx", (d) => d.x).attr("cy", (d) => d.y).attr("r", 3)
      .attr("fill", ctx.palette.roles.background)
      .attr("stroke", ctx.palette.roles.ink).attr("stroke-width", 1.5);
  }

  function renderTangramDissection(group, ctx) {
    const pieces = [
      [[0, 0], [100, 0], [0, 100]],
      [[100, 0], [200, 0], [200, 100]],
      [[200, 100], [200, 200], [100, 200]],
      [[100, 200], [0, 200], [0, 100]],
      [[100, 0], [200, 100], [100, 200]],
      [[100, 0], [100, 100], [0, 100]],
      [[0, 100], [100, 100], [100, 200]]
    ];
    const mark = group.append("g")
      .attr("class", "rule-based-tangram")
      .attr("transform", `translate(140,39) rotate(${(ctx.config.curvature - 0.5) * 8},100,100)`);
    mark.selectAll("polygon.tangram-piece")
      .data(pieces)
      .join("polygon")
      .attr("class", "tangram-piece")
      .attr("points", (piece) => piece.map((point) => point.join(",")).join(" "))
      .attr("fill", (d, index) => index === 4 ? ctx.textureFill : ctx.palette.sequence[index % ctx.palette.sequence.length])
      .attr("stroke", ctx.palette.roles.background).attr("stroke-width", 3)
      .attr("stroke-linejoin", "round");
    mark.append("rect")
      .attr("class", "tangram-master-boundary")
      .attr("width", 200).attr("height", 200)
      .attr("fill", "none").attr("stroke", ctx.palette.roles.ink).attr("stroke-width", 3);
  }

  function renderSuperellipseFamily(group, ctx) {
    const exponents = [1.15, 1.55, 2.1, 3.2, 5.2 + ctx.config.curvature * 2.8];
    const sizes = [112, 91, 70, 49, 28];
    const line = ctx.d3.line().curve(ctx.d3.curveLinearClosed);
    const shapes = exponents.map((exponent, index) => ctx.d3.range(160).map((sample) => {
      const angle = sample / 160 * Math.PI * 2;
      const cosine = Math.cos(angle);
      const sine = Math.sin(angle);
      const radius = sizes[index];
      return [
        240 + Math.sign(cosine) * Math.pow(Math.abs(cosine), 2 / exponent) * radius,
        139 + Math.sign(sine) * Math.pow(Math.abs(sine), 2 / exponent) * radius * 0.78
      ];
    }));
    group.append("g").attr("class", "nested-superellipse-family")
      .selectAll("path.superellipse-level")
      .data(shapes)
      .join("path")
      .attr("class", "superellipse-level")
      .attr("d", line)
      .attr("fill", (d, index) => index === 2 ? ctx.textureFill : (index % 2 ? ctx.palette.roles.background : ctx.palette.sequence[index % ctx.palette.sequence.length]))
      .attr("stroke", (d, index) => ctx.palette.sequence[(index + 1) % ctx.palette.sequence.length])
      .attr("stroke-width", 2.5);
  }

  function renderIsometricBlockStack(group, ctx) {
    const cells = [
      [0, 0, 0], [1, 0, 0], [2, 0, 0], [0, 1, 0], [1, 1, 0], [2, 1, 0],
      [1, 0, 1], [1, 1, 1], [2, 1, 1], [1, 1, 2]
    ];
    const size = 31;
    const project = (x, y, z) => [240 + (x - y - 0.5) * size, 182 + (x + y - 2) * size * 0.5 - z * size];
    const facePoints = (cell) => {
      const [x, y, z] = cell;
      const top = [project(x, y, z + 1), project(x + 1, y, z + 1), project(x + 1, y + 1, z + 1), project(x, y + 1, z + 1)];
      const left = [project(x, y + 1, z), project(x, y + 1, z + 1), project(x + 1, y + 1, z + 1), project(x + 1, y + 1, z)];
      const right = [project(x + 1, y, z), project(x + 1, y + 1, z), project(x + 1, y + 1, z + 1), project(x + 1, y, z + 1)];
      return { top, left, right };
    };
    const sorted = cells.slice().sort((a, b) => (a[0] + a[1] + a[2]) - (b[0] + b[1] + b[2]));
    const cubes = group.append("g").attr("class", "axonometric-voxel-stack")
      .selectAll("g.isometric-cube")
      .data(sorted)
      .join("g")
      .attr("class", "isometric-cube");
    cubes.each(function drawCube(cell, index) {
      const faces = facePoints(cell);
      const cube = ctx.d3.select(this);
      cube.selectAll("polygon.cube-face")
        .data([
          { role: "cube-left", points: faces.left, fill: ctx.palette.sequence[(index + 2) % ctx.palette.sequence.length] },
          { role: "cube-right", points: faces.right, fill: ctx.palette.sequence[(index + 1) % ctx.palette.sequence.length] },
          { role: "cube-top", points: faces.top, fill: index === sorted.length - 1 ? ctx.textureFill : ctx.palette.sequence[index % ctx.palette.sequence.length] }
        ])
        .join("polygon")
        .attr("class", (face) => `cube-face ${face.role}`)
        .attr("points", (face) => face.points.map((point) => point.join(",")).join(" "))
        .attr("fill", (face) => face.fill)
        .attr("stroke", ctx.palette.roles.background).attr("stroke-width", 1.6)
        .attr("stroke-linejoin", "round");
    });
  }

  function renderEulerianOneStroke(group, ctx) {
    const route = [
      [240, 139], [160, 58], [103, 139], [160, 220], [240, 139],
      [320, 58], [377, 139], [320, 220], [240, 139]
    ];
    const line = ctx.d3.line().curve(ctx.d3.curveCatmullRom.alpha(0.25 + ctx.config.curvature * 0.5));
    group.append("path")
      .attr("class", "euler-circuit-clearance")
      .attr("d", line(route)).attr("fill", "none")
      .attr("stroke", ctx.palette.roles.background).attr("stroke-width", 18)
      .attr("stroke-linecap", "round").attr("stroke-linejoin", "round");
    group.append("path")
      .attr("class", "euler-circuit-trace")
      .attr("d", line(route)).attr("fill", "none")
      .attr("stroke", ctx.textureFill).attr("stroke-width", 10)
      .attr("stroke-linecap", "round").attr("stroke-linejoin", "round");
    group.selectAll("circle.euler-vertex")
      .data(route.slice(0, -1).filter((point, index, values) => values.findIndex((item) => item[0] === point[0] && item[1] === point[1]) === index))
      .join("circle")
      .attr("class", "euler-vertex")
      .attr("cx", (d) => d[0]).attr("cy", (d) => d[1]).attr("r", 6)
      .attr("fill", (d, index) => ctx.palette.sequence[index % ctx.palette.sequence.length])
      .attr("stroke", ctx.palette.roles.background).attr("stroke-width", 2);
  }

  function renderPerfectMaze(group, ctx) {
    const columns = Math.max(9, Math.round(9 + ctx.config.density * 3));
    const rows = 7;
    const cell = Math.min(22, 236 / columns);
    const width = columns * cell;
    const height = rows * cell;
    const offsetX = 240 - width / 2;
    const offsetY = 139 - height / 2;
    const random = seededRandom(ctx.d3, ctx.config.seed, "perfect-maze");
    const cells = ctx.d3.range(columns * rows).map(() => ({ visited: false, walls: [true, true, true, true], parent: -1 }));
    const stack = [0];
    cells[0].visited = true;
    while (stack.length) {
      const current = stack[stack.length - 1];
      const x = current % columns;
      const y = Math.floor(current / columns);
      const neighbors = [];
      if (y > 0 && !cells[current - columns].visited) neighbors.push([current - columns, 0, 2]);
      if (x < columns - 1 && !cells[current + 1].visited) neighbors.push([current + 1, 1, 3]);
      if (y < rows - 1 && !cells[current + columns].visited) neighbors.push([current + columns, 2, 0]);
      if (x > 0 && !cells[current - 1].visited) neighbors.push([current - 1, 3, 1]);
      if (!neighbors.length) {
        stack.pop();
        continue;
      }
      const [next, wall, opposite] = neighbors[Math.floor(random() * neighbors.length)];
      cells[current].walls[wall] = false;
      cells[next].walls[opposite] = false;
      cells[next].visited = true;
      cells[next].parent = current;
      stack.push(next);
    }
    const solution = [];
    let cursor = columns * rows - 1;
    while (cursor >= 0) {
      solution.push([offsetX + (cursor % columns + 0.5) * cell, offsetY + (Math.floor(cursor / columns) + 0.5) * cell]);
      if (cursor === 0) break;
      cursor = cells[cursor].parent;
    }
    group.append("path")
      .attr("class", "maze-solution-route")
      .attr("d", ctx.d3.line().curve(ctx.d3.curveLinear)(solution.reverse()))
      .attr("fill", "none").attr("stroke", ctx.palette.roles.accent)
      .attr("stroke-width", Math.max(3, cell * 0.22)).attr("stroke-linecap", "round").attr("stroke-linejoin", "round");
    let walls = "";
    cells.forEach((mazeCell, index) => {
      const x = offsetX + (index % columns) * cell;
      const y = offsetY + Math.floor(index / columns) * cell;
      if (mazeCell.walls[0]) walls += `M${x},${y}H${x + cell}`;
      if (mazeCell.walls[3]) walls += `M${x},${y}V${y + cell}`;
      if (index % columns === columns - 1 && mazeCell.walls[1]) walls += `M${x + cell},${y}V${y + cell}`;
      if (Math.floor(index / columns) === rows - 1 && mazeCell.walls[2]) walls += `M${x},${y + cell}H${x + cell}`;
    });
    group.append("path")
      .attr("class", "perfect-maze-walls")
      .attr("d", walls).attr("fill", "none")
      .attr("stroke", ctx.palette.roles.ink).attr("stroke-width", 2.6)
      .attr("stroke-linecap", "square");
    group.selectAll("circle.maze-terminal")
      .data([solution[0], solution[solution.length - 1]])
      .join("circle")
      .attr("class", "maze-terminal")
      .attr("cx", (d) => d[0]).attr("cy", (d) => d[1]).attr("r", 5)
      .attr("fill", ctx.textureFill);
  }

  function renderSplitMergeStream(group, ctx) {
    const streamCount = 4;
    const sources = [78, 119, 160, 201];
    const targets = [84, 121, 165, 198];
    const xValues = [88, 145, 205, 240, 275, 335, 392];
    const area = ctx.d3.area()
      .x((d) => d.x)
      .y0((d) => d.y - d.width / 2)
      .y1((d) => d.y + d.width / 2)
      .curve(ctx.d3.curveCatmullRom.alpha(0.45 + ctx.config.curvature * 0.35));
    const streams = ctx.d3.range(streamCount).map((index) => {
      const centerOffset = (index - (streamCount - 1) / 2) * 13;
      return xValues.map((x, pointIndex) => {
        const progress = pointIndex / (xValues.length - 1);
        const merge = Math.sin(progress * Math.PI);
        const base = sources[index] * (1 - progress) + targets[(index + 1) % streamCount] * progress;
        return { x, y: base * (1 - merge * 0.58) + (139 + centerOffset) * merge * 0.58, width: 10 + (index % 2) * 3 };
      });
    });
    group.append("g").attr("class", "conserved-stream-routing")
      .selectAll("path.flow-ribbon")
      .data(streams)
      .join("path")
      .attr("class", "flow-ribbon")
      .attr("d", area)
      .attr("fill", (d, index) => index === 0 ? ctx.textureFill : ctx.palette.sequence[index % ctx.palette.sequence.length])
      .attr("stroke", ctx.palette.roles.background).attr("stroke-width", 1.8);
    group.selectAll("circle.flow-terminal")
      .data(sources.map((y, index) => ({ x: 88, y, index })).concat(targets.map((y, index) => ({ x: 392, y, index: index + streamCount }))))
      .join("circle")
      .attr("class", "flow-terminal")
      .attr("cx", (d) => d.x).attr("cy", (d) => d.y).attr("r", 5)
      .attr("fill", (d) => ctx.palette.sequence[d.index % ctx.palette.sequence.length]);
  }

  function renderDendrogramCrown(group, ctx) {
    const data = {
      children: ctx.d3.range(4).map((branch) => ({
        children: ctx.d3.range(2 + branch % 2).map((leaf) => ({ value: branch * 3 + leaf + 1 }))
      }))
    };
    const root = ctx.d3.hierarchy(data);
    ctx.d3.cluster().size([250, 145])(root);
    const position = (node) => ({ x: 115 + node.x, y: 215 - node.y });
    const links = root.links();
    group.append("g").attr("class", "hierarchy-crown-links")
      .selectAll("path.crown-link")
      .data(links)
      .join("path")
      .attr("class", "crown-link")
      .attr("d", (link) => {
        const source = position(link.source);
        const target = position(link.target);
        const middle = (source.y + target.y) / 2;
        return `M${source.x},${source.y}C${source.x},${middle} ${target.x},${middle} ${target.x},${target.y}`;
      })
      .attr("fill", "none")
      .attr("stroke", (d, index) => ctx.palette.sequence[index % ctx.palette.sequence.length])
      .attr("stroke-width", (d) => d.target.children ? 5 : 3)
      .attr("stroke-linecap", "round");
    group.append("g").attr("class", "hierarchy-crown-nodes")
      .selectAll("circle.crown-node")
      .data(root.descendants())
      .join("circle")
      .attr("class", "crown-node")
      .attr("cx", (d) => position(d).x).attr("cy", (d) => position(d).y)
      .attr("r", (d) => d.children ? 7 : 5)
      .attr("fill", (d, index) => d.depth === 0 ? ctx.textureFill : ctx.palette.sequence[index % ctx.palette.sequence.length])
      .attr("stroke", ctx.palette.roles.background).attr("stroke-width", 2);
  }

  function renderLinkedRingChain(group, ctx) {
    const rings = [
      { cx: 176, cy: 139, rx: 70, ry: 47, rotation: -24 },
      { cx: 240, cy: 139, rx: 70, ry: 47, rotation: 24 },
      { cx: 304, cy: 139, rx: 70, ry: 47, rotation: -24 }
    ];
    const sampleRing = (ring, start = 0, end = Math.PI * 2) => ctx.d3.range(65).map((index) => {
      const angle = start + (end - start) * index / 64;
      const cosine = Math.cos(ring.rotation * Math.PI / 180);
      const sine = Math.sin(ring.rotation * Math.PI / 180);
      const x = Math.cos(angle) * ring.rx;
      const y = Math.sin(angle) * ring.ry;
      return [ring.cx + x * cosine - y * sine, ring.cy + x * sine + y * cosine];
    });
    const line = ctx.d3.line().curve(ctx.d3.curveBasis);
    rings.forEach((ring, index) => {
      const path = line(sampleRing(ring));
      group.append("path")
        .attr("class", "ring-cycle-clearance")
        .attr("d", path).attr("fill", "none")
        .attr("stroke", ctx.palette.roles.background).attr("stroke-width", 17)
        .attr("stroke-linecap", "round");
      group.append("path")
        .attr("class", "ring-cycle")
        .attr("d", path).attr("fill", "none")
        .attr("stroke", index === 1 ? ctx.textureFill : ctx.palette.sequence[index % ctx.palette.sequence.length])
        .attr("stroke-width", 10).attr("stroke-linecap", "round");
    });
    rings.forEach((ring, index) => {
      const start = index % 2 ? Math.PI * 0.82 : Math.PI * 1.82;
      const segment = line(sampleRing(ring, start, start + Math.PI * 0.32));
      group.append("path")
        .attr("class", "ring-overpass-gap")
        .attr("d", segment).attr("fill", "none")
        .attr("stroke", ctx.palette.roles.background).attr("stroke-width", 18).attr("stroke-linecap", "round");
      group.append("path")
        .attr("class", "ring-overpass")
        .attr("d", segment).attr("fill", "none")
        .attr("stroke", index === 1 ? ctx.textureFill : ctx.palette.sequence[index % ctx.palette.sequence.length])
        .attr("stroke-width", 10).attr("stroke-linecap", "round");
    });
  }

  function renderLsystemBranch(group, ctx) {
    let grammar = "F";
    const depth = 3;
    for (let index = 0; index < depth; index += 1) grammar = grammar.replaceAll("F", "F[+F]F[-F]F");
    const angleStep = (18 + ctx.config.curvature * 15) * Math.PI / 180;
    let state = { x: 240, y: 222, angle: -Math.PI / 2, length: 6.2 + ctx.config.density * 1.1 };
    const stack = [];
    const segments = [];
    for (const token of grammar) {
      if (token === "F") {
        const next = {
          x: state.x + Math.cos(state.angle) * state.length,
          y: state.y + Math.sin(state.angle) * state.length,
          angle: state.angle,
          length: state.length
        };
        segments.push([[state.x, state.y], [next.x, next.y], stack.length]);
        state = next;
      } else if (token === "+") {
        state.angle += angleStep;
      } else if (token === "-") {
        state.angle -= angleStep;
      } else if (token === "[") {
        stack.push({ ...state });
        state.length *= 0.74;
      } else if (token === "]") {
        state = stack.pop() || state;
      }
    }
    group.append("g").attr("class", "lsystem-grammar-branches")
      .selectAll("line.branch-segment")
      .data(segments)
      .join("line")
      .attr("class", "branch-segment")
      .attr("x1", (d) => d[0][0]).attr("y1", (d) => d[0][1])
      .attr("x2", (d) => d[1][0]).attr("y2", (d) => d[1][1])
      .attr("stroke", (d, index) => index % 11 === 0 ? ctx.textureFill : ctx.palette.sequence[d[2] % ctx.palette.sequence.length])
      .attr("stroke-width", (d) => Math.max(1.2, 5 - d[2] * 0.8))
      .attr("stroke-linecap", "round");
    group.append("circle")
      .attr("class", "lsystem-root")
      .attr("cx", 240).attr("cy", 222).attr("r", 8)
      .attr("fill", ctx.palette.roles.ink);
  }

  function renderHilbertRoute(group, ctx) {
    const order = ctx.config.density > 1.2 ? 5 : 4;
    const side = 2 ** order;
    function rotateHilbert(n, x, y, rx, ry) {
      let nextX = x;
      let nextY = y;
      if (ry === 0) {
        if (rx === 1) {
          nextX = n - 1 - nextX;
          nextY = n - 1 - nextY;
        }
        const swap = nextX;
        nextX = nextY;
        nextY = swap;
      }
      return [nextX, nextY];
    }
    function distanceToPoint(size, distance) {
      let x = 0;
      let y = 0;
      let value = distance;
      for (let scale = 1; scale < size; scale *= 2) {
        const rx = 1 & Math.floor(value / 2);
        const ry = 1 & (value ^ rx);
        [x, y] = rotateHilbert(scale, x, y, rx, ry);
        x += scale * rx;
        y += scale * ry;
        value = Math.floor(value / 4);
      }
      return [x, y];
    }
    const extent = 192;
    const points = ctx.d3.range(side * side).map((distance) => {
      const [x, y] = distanceToPoint(side, distance);
      return [144 + x * extent / (side - 1), 43 + y * extent / (side - 1)];
    });
    const path = ctx.d3.line().curve(ctx.d3.curveLinear)(points);
    group.append("path")
      .attr("class", "hilbert-route-clearance")
      .attr("d", path).attr("fill", "none")
      .attr("stroke", ctx.palette.roles.background).attr("stroke-width", order === 5 ? 7 : 11)
      .attr("stroke-linecap", "round").attr("stroke-linejoin", "round");
    group.append("path")
      .attr("class", "hilbert-continuous-path")
      .attr("d", path).attr("fill", "none")
      .attr("stroke", ctx.textureFill).attr("stroke-width", order === 5 ? 3.5 : 6)
      .attr("stroke-linecap", "round").attr("stroke-linejoin", "round");
    group.selectAll("circle.hilbert-terminal")
      .data([points[0], points[points.length - 1]])
      .join("circle")
      .attr("class", "hilbert-terminal")
      .attr("cx", (d) => d[0]).attr("cy", (d) => d[1]).attr("r", order === 5 ? 4 : 6)
      .attr("fill", (d, index) => ctx.palette.sequence[index % ctx.palette.sequence.length]);
  }

  function renderReciprocalProfiles(group, ctx) {
    const depth = 18 + ctx.config.curvature * 18;
    const leftPath = `M92,49 H205 C${226 - depth},65 ${226 + depth},84 214,103 C201,116 234,124 215,140 C196,157 229,169 213,187 C201,201 220,216 205,229 H92Z`;
    const rightPath = `M388,49 H275 C${254 + depth},65 ${254 - depth},84 266,103 C279,116 246,124 265,140 C284,157 251,169 267,187 C279,201 260,216 275,229 H388Z`;
    group.append("path")
      .attr("class", "reciprocal-profile reciprocal-profile-left")
      .attr("d", leftPath).attr("fill", ctx.textureFill)
      .attr("stroke", ctx.palette.roles.ink).attr("stroke-width", 2.5).attr("stroke-linejoin", "round");
    group.append("path")
      .attr("class", "reciprocal-profile reciprocal-profile-right")
      .attr("d", rightPath).attr("fill", ctx.palette.sequence[1 % ctx.palette.sequence.length])
      .attr("stroke", ctx.palette.roles.ink).attr("stroke-width", 2.5).attr("stroke-linejoin", "round");
    group.append("path")
      .attr("class", "shared-boundary-axis")
      .attr("d", "M240,54V224")
      .attr("stroke", ctx.palette.roles.line).attr("stroke-width", 2).attr("stroke-dasharray", "4 8");
  }

  function renderModularGutterSymbol(group, ctx) {
    const gap = 13 + ctx.config.curvature * 11;
    const pieces = [
      [[116, 57], [224 - gap, 57], [224 - gap, 124], [191, 124]],
      [[256 + gap, 57], [364, 57], [289, 124], [256 + gap, 124]],
      [[116, 221], [191, 154], [224 - gap, 154], [224 - gap, 221]],
      [[256 + gap, 154], [289, 154], [364, 221], [256 + gap, 221]],
      [[205, 124], [240, 89], [275, 124], [240, 144]],
      [[205, 154], [240, 134], [275, 154], [240, 189]]
    ];
    group.append("g").attr("class", "gap-defined-modules")
      .selectAll("polygon.gutter-module")
      .data(pieces)
      .join("polygon")
      .attr("class", "gutter-module")
      .attr("points", (piece) => piece.map((point) => point.join(",")).join(" "))
      .attr("fill", (d, index) => index === 0 ? ctx.textureFill : ctx.palette.sequence[index % ctx.palette.sequence.length])
      .attr("stroke", ctx.palette.roles.background).attr("stroke-width", 2.2)
      .attr("stroke-linejoin", "round");
    group.append("rect")
      .attr("class", "gutter-boundary")
      .attr("x", 110).attr("y", 51).attr("width", 260).attr("height", 176).attr("rx", 9)
      .attr("fill", "none").attr("stroke", ctx.palette.roles.ink).attr("stroke-width", 3);
  }

  function renderTangentVoidStar(group, ctx) {
    const count = 6;
    const orbit = 63 + ctx.config.curvature * 8;
    const radius = orbit * Math.sin(Math.PI / count);
    const circles = ctx.d3.range(count).map((index) => {
      const angle = -Math.PI / 2 + index * Math.PI * 2 / count;
      return { x: 240 + Math.cos(angle) * orbit, y: 139 + Math.sin(angle) * orbit, r: radius };
    });
    group.append("g").attr("class", "tangent-void-primitives")
      .selectAll("circle.void-disc")
      .data(circles)
      .join("circle")
      .attr("class", "void-disc")
      .attr("cx", (d) => d.x).attr("cy", (d) => d.y).attr("r", (d) => d.r)
      .attr("fill", (d, index) => index === 0 ? ctx.textureFill : ctx.palette.sequence[index % ctx.palette.sequence.length])
      .attr("stroke", ctx.palette.roles.ink).attr("stroke-width", 2);
    group.append("circle")
      .attr("class", "unpainted-star-guide")
      .attr("cx", 240).attr("cy", 139).attr("r", Math.max(5, orbit - radius * 2.02))
      .attr("fill", ctx.palette.roles.background);
  }

  function renderReciprocalTessellation(group, ctx) {
    const columns = 5;
    const rows = 3;
    const width = 54;
    const height = 54;
    const startX = 105;
    const startY = 58;
    const tiles = [];
    for (let row = 0; row < rows; row += 1) {
      for (let column = 0; column < columns; column += 1) {
        tiles.push({ row, column, x: startX + column * width, y: startY + row * height, mirror: (row + column) % 2 === 1 });
      }
    }
    const mark = group.append("g").attr("class", "dual-figure-ground-tiles");
    tiles.forEach((tile, index) => {
      const direction = tile.mirror ? -1 : 1;
      const topX = tile.x + width * (0.5 - direction * 0.12);
      const bottomX = tile.x + width * (0.5 + direction * 0.12);
      const c1x = tile.x + width * (0.5 + direction * (0.16 + ctx.config.curvature * 0.08));
      const c2x = tile.x + width * (0.5 - direction * (0.16 + ctx.config.curvature * 0.08));
      const boundary = `C${c1x},${tile.y + height * 0.32} ${c2x},${tile.y + height * 0.68} ${bottomX},${tile.y + height}`;
      mark.append("path")
        .attr("class", "reciprocal-tile reciprocal-tile-a")
        .attr("d", `M${tile.x},${tile.y}H${topX}${boundary}H${tile.x}Z`)
        .attr("fill", index === 0 ? ctx.textureFill : ctx.palette.sequence[index % ctx.palette.sequence.length]);
      mark.append("path")
        .attr("class", "reciprocal-tile reciprocal-tile-b")
        .attr("d", `M${topX},${tile.y}H${tile.x + width}V${tile.y + height}H${bottomX}C${c2x},${tile.y + height * 0.68} ${c1x},${tile.y + height * 0.32} ${topX},${tile.y}Z`)
        .attr("fill", ctx.palette.sequence[(index + 2) % ctx.palette.sequence.length]);
    });
    mark.append("rect")
      .attr("class", "reciprocal-tile-boundary")
      .attr("x", startX).attr("y", startY).attr("width", columns * width).attr("height", rows * height)
      .attr("fill", "none").attr("stroke", ctx.palette.roles.ink).attr("stroke-width", 3);
  }

  function renderImpossibleTriangle(group, ctx) {
    const vertices = [[240, 45], [373, 220], [107, 220]];
    const beams = [
      { from: vertices[0], to: vertices[1], color: ctx.palette.sequence[0] },
      { from: vertices[1], to: vertices[2], color: ctx.palette.sequence[1] },
      { from: vertices[2], to: vertices[0], color: ctx.textureFill }
    ];
    beams.forEach((beam, index) => {
      group.append("line")
        .attr("class", "impossible-beam-clearance")
        .attr("x1", beam.from[0]).attr("y1", beam.from[1])
        .attr("x2", beam.to[0]).attr("y2", beam.to[1])
        .attr("stroke", ctx.palette.roles.background).attr("stroke-width", 42)
        .attr("stroke-linecap", "square");
      group.append("line")
        .attr("class", `impossible-beam impossible-beam-${index + 1}`)
        .attr("x1", beam.from[0]).attr("y1", beam.from[1])
        .attr("x2", beam.to[0]).attr("y2", beam.to[1])
        .attr("stroke", beam.color).attr("stroke-width", 29)
        .attr("stroke-linecap", "square");
    });
    const overpasses = [
      [[240, 45], [267, 80], ctx.palette.sequence[0]],
      [[373, 220], [328, 220], ctx.palette.sequence[1]],
      [[107, 220], [132, 187], ctx.textureFill]
    ];
    overpasses.forEach((segment, index) => {
      group.append("line")
        .attr("class", "cyclic-depth-gap")
        .attr("x1", segment[0][0]).attr("y1", segment[0][1])
        .attr("x2", segment[1][0]).attr("y2", segment[1][1])
        .attr("stroke", ctx.palette.roles.background).attr("stroke-width", 43).attr("stroke-linecap", "square");
      group.append("line")
        .attr("class", `cyclic-depth-overpass cyclic-depth-overpass-${index + 1}`)
        .attr("x1", segment[0][0]).attr("y1", segment[0][1])
        .attr("x2", segment[1][0]).attr("y2", segment[1][1])
        .attr("stroke", segment[2]).attr("stroke-width", 29).attr("stroke-linecap", "square");
    });
    group.append("polygon")
      .attr("class", "impossible-inner-void")
      .attr("points", "240,103 308,191 172,191")
      .attr("fill", ctx.palette.roles.background)
      .attr("stroke", ctx.palette.roles.ink).attr("stroke-width", 2);
  }

  function renderNeckerCube(group, ctx) {
    const offset = 48 + ctx.config.curvature * 15;
    const back = [[145, 52], [286, 52], [286, 193], [145, 193]];
    const front = back.map((point) => [point[0] + offset, point[1] + 34]);
    const edges = [
      ...ctx.d3.range(4).map((index) => [back[index], back[(index + 1) % 4]]),
      ...ctx.d3.range(4).map((index) => [front[index], front[(index + 1) % 4]]),
      ...ctx.d3.range(4).map((index) => [back[index], front[index]])
    ];
    group.append("g").attr("class", "bistable-necker-wireframe")
      .selectAll("line.necker-edge")
      .data(edges)
      .join("line")
      .attr("class", "necker-edge")
      .attr("x1", (d) => d[0][0]).attr("y1", (d) => d[0][1])
      .attr("x2", (d) => d[1][0]).attr("y2", (d) => d[1][1])
      .attr("stroke", (d, index) => index < 4 ? ctx.textureFill : ctx.palette.sequence[index % ctx.palette.sequence.length])
      .attr("stroke-width", 6).attr("stroke-linecap", "round");
    group.selectAll("circle.necker-joint")
      .data(back.concat(front))
      .join("circle")
      .attr("class", "necker-joint")
      .attr("cx", (d) => d[0]).attr("cy", (d) => d[1]).attr("r", 5)
      .attr("fill", ctx.palette.roles.background)
      .attr("stroke", ctx.palette.roles.ink).attr("stroke-width", 2);
  }

  function renderKanizsaClosure(group, ctx) {
    const center = [240, 139];
    const inducers = [[165, 64], [315, 64], [315, 214], [165, 214]];
    const radius = 37 + ctx.config.curvature * 5;
    const arc = ctx.d3.arc().innerRadius(0).outerRadius(radius);
    group.append("g").attr("class", "kanizsa-inducer-field")
      .selectAll("path.kanizsa-inducer")
      .data(inducers)
      .join("path")
      .attr("class", "kanizsa-inducer")
      .attr("d", (point) => {
        const angle = Math.atan2(center[1] - point[1], center[0] - point[0]) + Math.PI / 2;
        return arc({ startAngle: angle + 0.62, endAngle: angle + Math.PI * 2 - 0.62 });
      })
      .attr("transform", (point) => `translate(${point[0]},${point[1]})`)
      .attr("fill", (d, index) => index === 0 ? ctx.textureFill : ctx.palette.sequence[index % ctx.palette.sequence.length]);
    group.selectAll("circle.kanizsa-anchor")
      .data(inducers)
      .join("circle")
      .attr("class", "kanizsa-anchor")
      .attr("cx", (d) => d[0]).attr("cy", (d) => d[1]).attr("r", 4)
      .attr("fill", ctx.palette.roles.ink);
  }

  function renderLineScreenSilhouette(group, ctx) {
    const rows = Math.max(15, Math.round(16 + ctx.config.density * 8));
    const yScale = ctx.d3.scaleLinear().domain([0, rows - 1]).range([48, 226]);
    const segments = [];
    ctx.d3.range(rows).forEach((index) => {
      const y = yScale(index);
      const normalized = (index / (rows - 1)) * 2 - 1;
      const halfWidth = 124 * Math.sqrt(Math.max(0, 1 - normalized * normalized * 0.86));
      const shift = Math.sin(normalized * Math.PI * 1.4) * (18 + ctx.config.curvature * 24);
      const gap = 12 + (1 - Math.abs(normalized)) * 18;
      segments.push({ x1: 240 - halfWidth, x2: 240 + shift - gap, y, index });
      segments.push({ x1: 240 + shift + gap, x2: 240 + halfWidth, y, index });
    });
    group.append("g").attr("class", "variable-line-screen")
      .selectAll("line.screen-segment")
      .data(segments.filter((segment) => segment.x2 > segment.x1))
      .join("line")
      .attr("class", "screen-segment")
      .attr("x1", (d) => d.x1).attr("x2", (d) => d.x2)
      .attr("y1", (d) => d.y).attr("y2", (d) => d.y)
      .attr("stroke", (d) => d.index % 4 === 0 ? ctx.textureFill : ctx.palette.sequence[d.index % ctx.palette.sequence.length])
      .attr("stroke-width", Math.max(3, 7 - rows * 0.12))
      .attr("stroke-linecap", "round");
    group.append("ellipse")
      .attr("class", "line-screen-boundary")
      .attr("cx", 240).attr("cy", 137).attr("rx", 132).attr("ry", 97)
      .attr("fill", "none").attr("stroke", ctx.palette.roles.ink).attr("stroke-width", 2.5);
  }

  function renderPerspectivePortal(group, ctx) {
    const outer = [[105, 43], [376, 61], [350, 224], [126, 211]];
    const vanishing = [286 + (ctx.config.curvature - 0.5) * 35, 137];
    group.append("g").attr("class", "portal-perspective-guides")
      .selectAll("line.portal-guide")
      .data(outer)
      .join("line")
      .attr("class", "portal-guide")
      .attr("x1", (d) => d[0]).attr("y1", (d) => d[1])
      .attr("x2", vanishing[0]).attr("y2", vanishing[1])
      .attr("stroke", ctx.palette.roles.line).attr("stroke-width", 2);
    const levels = Math.max(7, Math.round(7 + ctx.config.density * 4));
    const frames = ctx.d3.range(levels).map((index) => {
      const t = index / levels * 0.86;
      return outer.map((point) => [
        point[0] + (vanishing[0] - point[0]) * t,
        point[1] + (vanishing[1] - point[1]) * t
      ]);
    });
    group.append("g").attr("class", "receding-portal-frames")
      .selectAll("polygon.portal-frame")
      .data(frames)
      .join("polygon")
      .attr("class", "portal-frame")
      .attr("points", (frame) => frame.map((point) => point.join(",")).join(" "))
      .attr("fill", "none")
      .attr("stroke", (d, index) => index === 1 ? ctx.textureFill : ctx.palette.sequence[index % ctx.palette.sequence.length])
      .attr("stroke-width", (d, index) => Math.max(2.5, 10 - index * 0.65))
      .attr("stroke-linejoin", "round");
    group.append("circle")
      .attr("class", "portal-vanishing-point")
      .attr("cx", vanishing[0]).attr("cy", vanishing[1]).attr("r", 7)
      .attr("fill", ctx.palette.roles.accent);
  }

  function mathSegmentsPath(segments) {
    return segments.map((segment) => `M${segment[0][0].toFixed(2)},${segment[0][1].toFixed(2)}L${segment[1][0].toFixed(2)},${segment[1][1].toFixed(2)}`).join("");
  }

  function mathPolygonPath(points) {
    if (!points.length) return "";
    return `M${points.map((point) => `${point[0].toFixed(2)},${point[1].toFixed(2)}`).join("L")}Z`;
  }

  function mathLineIntersection(a, b, c, d) {
    const denominator = (a[0] - b[0]) * (c[1] - d[1]) - (a[1] - b[1]) * (c[0] - d[0]);
    if (Math.abs(denominator) < 1e-8) return null;
    const crossA = a[0] * b[1] - a[1] * b[0];
    const crossB = c[0] * d[1] - c[1] * d[0];
    return [
      (crossA * (c[0] - d[0]) - (a[0] - b[0]) * crossB) / denominator,
      (crossA * (c[1] - d[1]) - (a[1] - b[1]) * crossB) / denominator
    ];
  }

  function mathFitTransform(points, bounds) {
    const xs = points.map((point) => point[0]);
    const ys = points.map((point) => point[1]);
    const minX = Math.min(...xs);
    const maxX = Math.max(...xs);
    const minY = Math.min(...ys);
    const maxY = Math.max(...ys);
    const scale = Math.min(
      (bounds[2] - bounds[0]) / Math.max(1e-6, maxX - minX),
      (bounds[3] - bounds[1]) / Math.max(1e-6, maxY - minY)
    );
    const sourceCenter = [(minX + maxX) / 2, (minY + maxY) / 2];
    const targetCenter = [(bounds[0] + bounds[2]) / 2, (bounds[1] + bounds[3]) / 2];
    return (point) => [
      targetCenter[0] + (point[0] - sourceCenter[0]) * scale,
      targetCenter[1] + (point[1] - sourceCenter[1]) * scale
    ];
  }

  function mathProject3D(point, options) {
    const rx = options.rx || 0;
    const ry = options.ry || 0;
    const cosX = Math.cos(rx);
    const sinX = Math.sin(rx);
    const cosY = Math.cos(ry);
    const sinY = Math.sin(ry);
    const y1 = point[1] * cosX - point[2] * sinX;
    const z1 = point[1] * sinX + point[2] * cosX;
    const x2 = point[0] * cosY + z1 * sinY;
    const z2 = -point[0] * sinY + z1 * cosY;
    const perspective = 1 / Math.max(0.55, 1 + z2 * (options.perspective || 0.08));
    return [
      options.cx + x2 * options.scale * perspective,
      options.cy - y1 * options.scale * perspective,
      z2
    ];
  }

  function mathCircumcenter(a, b, c) {
    const denominator = 2 * (a[0] * (b[1] - c[1]) + b[0] * (c[1] - a[1]) + c[0] * (a[1] - b[1]));
    if (Math.abs(denominator) < 1e-8) return null;
    const aa = a[0] * a[0] + a[1] * a[1];
    const bb = b[0] * b[0] + b[1] * b[1];
    const cc = c[0] * c[0] + c[1] * c[1];
    return [
      (aa * (b[1] - c[1]) + bb * (c[1] - a[1]) + cc * (a[1] - b[1])) / denominator,
      (aa * (c[0] - b[0]) + bb * (a[0] - c[0]) + cc * (b[0] - a[0])) / denominator
    ];
  }

  function renderReuleauxBody(group, ctx) {
    const center = [240, 126];
    const line = ctx.d3.line().curve(ctx.d3.curveLinearClosed);
    const bodies = ctx.d3.range(3).map((index) => {
      const side = 116 - index * 25;
      const height = side * Math.sqrt(3) / 2;
      const vertices = [
        [center[0], center[1] - height * 2 / 3],
        [center[0] + side / 2, center[1] + height / 3],
        [center[0] - side / 2, center[1] + height / 3]
      ];
      const arcs = [
        [vertices[2], vertices[0], vertices[1], -Math.PI / 3, 0],
        [vertices[0], vertices[1], vertices[2], Math.PI / 3, 2 * Math.PI / 3],
        [vertices[1], vertices[2], vertices[0], Math.PI, 4 * Math.PI / 3]
      ];
      const points = [];
      arcs.forEach(([arcCenter, start, end, startAngle, endAngle]) => {
        ctx.d3.range(13).forEach((sample) => {
          const angle = startAngle + (endAngle - startAngle) * sample / 12;
          points.push([arcCenter[0] + side * Math.cos(angle), arcCenter[1] + side * Math.sin(angle)]);
        });
        points[points.length - 1] = end;
        if (points.length === 13) points[0] = start;
      });
      return points;
    });
    group.selectAll("path.reuleaux-body")
      .data(bodies)
      .join("path")
      .attr("class", "reuleaux-body")
      .attr("d", line)
      .attr("fill", (d, index) => index === 2 ? ctx.textureFill : "none")
      .attr("stroke", (d, index) => ctx.palette.sequence[index % ctx.palette.sequence.length])
      .attr("stroke-width", (d, index) => 8 - index * 1.8)
      .attr("stroke-linejoin", "round");
    group.append("circle").attr("class", "reuleaux-center").attr("cx", center[0]).attr("cy", center[1]).attr("r", 6).attr("fill", ctx.palette.roles.accent);
  }

  function renderCassiniOval(group, ctx) {
    const center = [240, 126];
    const a = 62;
    const ratios = [0.78, 1, 1.2];
    const paths = [];
    ratios.forEach((ratio, ratioIndex) => {
      let segment = [];
      ctx.d3.range(361).forEach((sample) => {
        const theta = sample / 360 * Math.PI * 2;
        const b = a * ratio;
        const discriminant = Math.pow(b, 4) - Math.pow(a, 4) * Math.pow(Math.sin(2 * theta), 2);
        const radiusSquared = a * a * Math.cos(2 * theta) + Math.sqrt(Math.max(0, discriminant));
        if (discriminant >= 0 && radiusSquared >= 0) {
          const radius = Math.sqrt(radiusSquared);
          segment.push([center[0] + radius * Math.cos(theta), center[1] + radius * Math.sin(theta)]);
        } else if (segment.length > 1) {
          paths.push({ ratioIndex, points: segment });
          segment = [];
        } else {
          segment = [];
        }
      });
      if (segment.length > 1) paths.push({ ratioIndex, points: segment });
    });
    const line = ctx.d3.line().curve(ctx.d3.curveLinear);
    group.selectAll("path.cassini-locus")
      .data(paths)
      .join("path")
      .attr("class", "cassini-locus")
      .attr("d", (d) => line(d.points))
      .attr("fill", "none")
      .attr("stroke", (d) => d.ratioIndex === 1 ? ctx.textureFill : ctx.palette.sequence[d.ratioIndex])
      .attr("stroke-width", (d) => d.ratioIndex === 1 ? 7 : 4)
      .attr("stroke-linecap", "round");
    group.selectAll("circle.cassini-focus")
      .data([-a, a])
      .join("circle")
      .attr("class", "cassini-focus")
      .attr("cx", (d) => center[0] + d).attr("cy", center[1]).attr("r", 5)
      .attr("fill", ctx.palette.roles.accent);
  }

  function renderPolarReciprocal(group, ctx) {
    const center = [240, 126];
    const source = [-1.45, -0.55, 0.55, 1.75, 2.75].map((angle, index) => {
      const radius = [76, 68, 73, 63, 70][index];
      return [radius * Math.cos(angle), radius * Math.sin(angle)];
    });
    let dual = source.map((point, index) => {
      const next = source[(index + 1) % source.length];
      const a = point[1] - next[1];
      const b = next[0] - point[0];
      const c = a * point[0] + b * point[1];
      return [2700 * a / c, 2700 * b / c];
    });
    const maxDual = Math.max(...dual.map((point) => Math.hypot(point[0], point[1])));
    if (maxDual > 82) dual = dual.map((point) => [point[0] * 82 / maxDual, point[1] * 82 / maxDual]);
    const toCanvas = (point) => [center[0] + point[0], center[1] + point[1]];
    const sourceCanvas = source.map(toCanvas);
    const dualCanvas = dual.map(toCanvas);
    group.append("path").attr("class", "polar-source-polygon").attr("d", mathPolygonPath(sourceCanvas))
      .attr("fill", ctx.textureFill).attr("fill-opacity", 0.26).attr("stroke", ctx.palette.roles.ink).attr("stroke-width", 4);
    group.append("path").attr("class", "polar-dual-polygon").attr("d", mathPolygonPath(dualCanvas))
      .attr("fill", "none").attr("stroke", ctx.palette.roles.primary).attr("stroke-width", 7).attr("stroke-linejoin", "round");
    const incidence = dualCanvas.map((point, index) => {
      const a = sourceCanvas[index];
      const b = sourceCanvas[(index + 1) % sourceCanvas.length];
      return [[(a[0] + b[0]) / 2, (a[1] + b[1]) / 2], point];
    });
    group.append("path").attr("class", "polar-incidence-lines").attr("d", mathSegmentsPath(incidence))
      .attr("fill", "none").attr("stroke", ctx.palette.roles.accent).attr("stroke-width", 2).attr("stroke-dasharray", "3 5");
    group.selectAll("circle.polar-dual-vertex").data(dualCanvas).join("circle").attr("class", "polar-dual-vertex")
      .attr("cx", (d) => d[0]).attr("cy", (d) => d[1]).attr("r", 4.5).attr("fill", ctx.palette.roles.accent);
  }

  function renderMinkowskiSum(group, ctx) {
    const a = [[-30, 25], [0, -32], [34, 22]];
    const b = [[-26, -20], [28, -20], [28, 20], [-26, 20]];
    const sum = ctx.d3.polygonHull(a.flatMap((pointA) => b.map((pointB) => [pointA[0] + pointB[0], pointA[1] + pointB[1]]))) || [];
    const place = (points, x, scale) => points.map((point) => [x + point[0] * scale, 126 + point[1] * scale]);
    const aCanvas = place(a, 113, 0.82);
    const bCanvas = place(b, 226, 0.82);
    const sumCanvas = place(sum, 356, 0.88);
    group.append("path").attr("class", "minkowski-set-a").attr("d", mathPolygonPath(aCanvas))
      .attr("fill", ctx.palette.sequence[1]).attr("stroke", ctx.palette.roles.ink).attr("stroke-width", 3);
    group.append("path").attr("class", "minkowski-set-b").attr("d", mathPolygonPath(bCanvas))
      .attr("fill", ctx.palette.sequence[2]).attr("stroke", ctx.palette.roles.ink).attr("stroke-width", 3);
    group.append("path").attr("class", "minkowski-sum-boundary").attr("d", mathPolygonPath(sumCanvas))
      .attr("fill", ctx.textureFill).attr("stroke", ctx.palette.roles.primaryDark).attr("stroke-width", 6).attr("stroke-linejoin", "round");
    const plusSegments = [[[164, 126], [183, 126]], [[173.5, 116.5], [173.5, 135.5]]];
    const arrowSegments = [[[276, 126], [307, 126]], [[297, 117], [307, 126]], [[297, 135], [307, 126]]];
    group.append("path").attr("class", "minkowski-operators").attr("d", mathSegmentsPath(plusSegments.concat(arrowSegments)))
      .attr("fill", "none").attr("stroke", ctx.palette.roles.accent).attr("stroke-width", 4).attr("stroke-linecap", "round");
  }

  function renderPedalCurve(group, ctx) {
    const center = [240, 128];
    const rx = 104;
    const ry = 67;
    const fixed = [172, 66];
    const feet = ctx.d3.range(181).map((sample) => {
      const t = sample / 180 * Math.PI * 2;
      const point = [center[0] + rx * Math.cos(t), center[1] + ry * Math.sin(t)];
      const normal = [Math.cos(t) / rx, Math.sin(t) / ry];
      const normalLength = normal[0] * normal[0] + normal[1] * normal[1];
      const factor = ((fixed[0] - point[0]) * normal[0] + (fixed[1] - point[1]) * normal[1]) / normalLength;
      return [fixed[0] - factor * normal[0], fixed[1] - factor * normal[1]];
    });
    const ellipse = ctx.d3.range(121).map((sample) => [
      center[0] + rx * Math.cos(sample / 120 * Math.PI * 2),
      center[1] + ry * Math.sin(sample / 120 * Math.PI * 2)
    ]);
    const line = ctx.d3.line().curve(ctx.d3.curveLinearClosed);
    group.append("path").attr("class", "pedal-source-ellipse").attr("d", line(ellipse))
      .attr("fill", "none").attr("stroke", ctx.palette.roles.line).attr("stroke-width", 3);
    group.append("path").attr("class", "pedal-foot-locus").attr("d", line(feet))
      .attr("fill", ctx.textureFill).attr("fill-opacity", 0.18).attr("stroke", ctx.palette.roles.primary).attr("stroke-width", 7).attr("stroke-linejoin", "round");
    const construction = ctx.d3.range(0, feet.length, 30).map((index) => [fixed, feet[index]]);
    group.append("path").attr("class", "pedal-projections").attr("d", mathSegmentsPath(construction))
      .attr("fill", "none").attr("stroke", ctx.palette.sequence[2]).attr("stroke-width", 2).attr("opacity", 0.72);
    group.append("circle").attr("class", "pedal-fixed-point").attr("cx", fixed[0]).attr("cy", fixed[1]).attr("r", 7).attr("fill", ctx.palette.roles.accent);
  }

  function renderInvoluteGear(group, ctx) {
    const center = [240, 126];
    const baseRadius = 54;
    const teeth = 12;
    const flankSegments = [];
    const toothTips = [];
    const rotate = (point, angle) => [
      center[0] + point[0] * Math.cos(angle) - point[1] * Math.sin(angle),
      center[1] + point[0] * Math.sin(angle) + point[1] * Math.cos(angle)
    ];
    ctx.d3.range(teeth).forEach((tooth) => {
      const angle = tooth / teeth * Math.PI * 2;
      const left = [];
      const right = [];
      ctx.d3.range(13).forEach((sample) => {
        const t = sample / 12 * 0.72;
        const x = baseRadius * (Math.cos(t) + t * Math.sin(t));
        const y = baseRadius * (Math.sin(t) - t * Math.cos(t));
        left.push(rotate([x, y], angle - 0.12));
        right.push(rotate([x, -y], angle + 0.12));
      });
      for (let index = 1; index < left.length; index += 1) flankSegments.push([left[index - 1], left[index]]);
      for (let index = 1; index < right.length; index += 1) flankSegments.push([right[index - 1], right[index]]);
      toothTips.push([left[left.length - 1], right[right.length - 1]]);
    });
    group.append("circle").attr("class", "involute-gear-body").attr("cx", center[0]).attr("cy", center[1]).attr("r", baseRadius + 5)
      .attr("fill", ctx.textureFill).attr("stroke", ctx.palette.roles.ink).attr("stroke-width", 4);
    group.append("path").attr("class", "involute-flanks").attr("d", mathSegmentsPath(flankSegments.concat(toothTips)))
      .attr("fill", "none").attr("stroke", ctx.palette.roles.primary).attr("stroke-width", 5).attr("stroke-linecap", "round");
    group.append("circle").attr("class", "involute-base-circle").attr("cx", center[0]).attr("cy", center[1]).attr("r", baseRadius)
      .attr("fill", "none").attr("stroke", ctx.palette.sequence[2]).attr("stroke-width", 2).attr("stroke-dasharray", "5 5");
    group.append("circle").attr("class", "involute-bore").attr("cx", center[0]).attr("cy", center[1]).attr("r", 18)
      .attr("fill", ctx.palette.roles.background).attr("stroke", ctx.palette.roles.ink).attr("stroke-width", 5);
  }

  function renderDesarguesIncidence(group, ctx) {
    const origin = [0, -90];
    const triangleA = [[-90, 30], [90, 20], [-20, 120]];
    const scales = [0.45, 0.8, 0.25];
    const triangleB = triangleA.map((point, index) => [
      origin[0] + (point[0] - origin[0]) * scales[index],
      origin[1] + (point[1] - origin[1]) * scales[index]
    ]);
    const pairs = [[0, 1], [1, 2], [2, 0]];
    const axisPoints = pairs.map(([a, b]) => mathLineIntersection(triangleA[a], triangleA[b], triangleB[a], triangleB[b])).filter(Boolean);
    const toCanvas = (point) => [240 + point[0], 125 + (point[1] - 15) * 0.86];
    const o = toCanvas(origin);
    const aCanvas = triangleA.map(toCanvas);
    const bCanvas = triangleB.map(toCanvas);
    const axisCanvas = axisPoints.map(toCanvas);
    const perspectiveRays = aCanvas.map((point) => [o, point]);
    group.append("path").attr("class", "desargues-perspective-rays").attr("d", mathSegmentsPath(perspectiveRays))
      .attr("fill", "none").attr("stroke", ctx.palette.roles.line).attr("stroke-width", 2.5);
    group.append("path").attr("class", "desargues-triangle-a").attr("d", mathPolygonPath(aCanvas))
      .attr("fill", ctx.textureFill).attr("fill-opacity", 0.22).attr("stroke", ctx.palette.roles.ink).attr("stroke-width", 5);
    group.append("path").attr("class", "desargues-triangle-b").attr("d", mathPolygonPath(bCanvas))
      .attr("fill", "none").attr("stroke", ctx.palette.roles.primary).attr("stroke-width", 6);
    if (axisCanvas.length > 1) {
      const sorted = axisCanvas.slice().sort((left, right) => left[0] - right[0]);
      group.append("path").attr("class", "desargues-collinear-axis").attr("d", mathSegmentsPath([[sorted[0], sorted[sorted.length - 1]]]))
        .attr("fill", "none").attr("stroke", ctx.palette.roles.accent).attr("stroke-width", 4).attr("stroke-dasharray", "8 5");
    }
    group.selectAll("circle.desargues-axis-point").data(axisCanvas).join("circle").attr("class", "desargues-axis-point")
      .attr("cx", (d) => d[0]).attr("cy", (d) => d[1]).attr("r", 5).attr("fill", ctx.palette.roles.accent);
    group.append("circle").attr("class", "desargues-center").attr("cx", o[0]).attr("cy", o[1]).attr("r", 7).attr("fill", ctx.palette.sequence[2]);
  }

  function renderCircleInversion(group, ctx) {
    const center = [240, 126];
    const inversionRadius = 54;
    const sourceLines = [-76, -42, 42, 76].map((offset, index) => ({
      vertical: index % 2 === 0,
      offset
    }));
    const inversePaths = sourceLines.map((spec) => ctx.d3.range(121).map((sample) => {
      const t = -112 + sample / 120 * 224;
      const local = spec.vertical ? [spec.offset, t] : [t, spec.offset];
      const magnitudeSquared = local[0] * local[0] + local[1] * local[1];
      return [
        center[0] + inversionRadius * inversionRadius * local[0] / magnitudeSquared,
        center[1] + inversionRadius * inversionRadius * local[1] / magnitudeSquared
      ];
    }));
    const guideSegments = sourceLines.map((spec) => spec.vertical
      ? [[center[0] + spec.offset, 35], [center[0] + spec.offset, 217]]
      : [[92, center[1] + spec.offset], [388, center[1] + spec.offset]]);
    group.append("path").attr("class", "inversion-source-lines").attr("d", mathSegmentsPath(guideSegments))
      .attr("fill", "none").attr("stroke", ctx.palette.roles.line).attr("stroke-width", 2);
    group.selectAll("path.inversion-image")
      .data(inversePaths)
      .join("path")
      .attr("class", "inversion-image")
      .attr("d", ctx.d3.line().curve(ctx.d3.curveBasis))
      .attr("fill", "none")
      .attr("stroke", (d, index) => index === 1 ? ctx.textureFill : ctx.palette.sequence[index % ctx.palette.sequence.length])
      .attr("stroke-width", 6)
      .attr("stroke-linecap", "round");
    group.append("circle").attr("class", "inversion-circle").attr("cx", center[0]).attr("cy", center[1]).attr("r", inversionRadius)
      .attr("fill", "none").attr("stroke", ctx.palette.roles.ink).attr("stroke-width", 4).attr("stroke-dasharray", "6 5");
    group.append("circle").attr("class", "inversion-center").attr("cx", center[0]).attr("cy", center[1]).attr("r", 7).attr("fill", ctx.palette.roles.accent);
  }

  function renderCatenaryFunicular(group, ctx) {
    const cableSpecs = [
      { x0: 92, x1: 388, top: 55, sag: 98, a: 82 },
      { x0: 126, x1: 354, top: 79, sag: 70, a: 66 }
    ];
    const line = ctx.d3.line().curve(ctx.d3.curveLinear);
    const cables = cableSpecs.map((spec) => {
      const centerX = (spec.x0 + spec.x1) / 2;
      const half = (spec.x1 - spec.x0) / 2;
      const denominator = Math.cosh(half / spec.a) - 1;
      return ctx.d3.range(121).map((sample) => {
        const x = spec.x0 + sample / 120 * (spec.x1 - spec.x0);
        const normalized = (Math.cosh(half / spec.a) - Math.cosh((x - centerX) / spec.a)) / denominator;
        return [x, spec.top + spec.sag * normalized];
      });
    });
    group.selectAll("path.catenary-cable").data(cables).join("path").attr("class", "catenary-cable")
      .attr("d", line).attr("fill", "none")
      .attr("stroke", (d, index) => index === 0 ? ctx.palette.roles.primary : ctx.textureFill)
      .attr("stroke-width", (d, index) => index === 0 ? 8 : 5).attr("stroke-linecap", "round");
    const hangers = ctx.d3.range(13).map((index) => {
      const point = cables[0][index * 10];
      return [point, [point[0], 205]];
    });
    group.append("path").attr("class", "catenary-hangers").attr("d", mathSegmentsPath(hangers))
      .attr("fill", "none").attr("stroke", ctx.palette.sequence[2]).attr("stroke-width", 2.5);
    group.append("path").attr("class", "funicular-deck").attr("d", "M84,205H396")
      .attr("fill", "none").attr("stroke", ctx.palette.roles.ink).attr("stroke-width", 7).attr("stroke-linecap", "round");
  }

  function renderJoukowskiAirfoil(group, ctx) {
    const mapped = ctx.d3.range(361).map((sample) => {
      const theta = sample / 360 * Math.PI * 2;
      const z = [-0.09 + 1.04 * Math.cos(theta), 0.08 + 1.04 * Math.sin(theta)];
      const magnitudeSquared = z[0] * z[0] + z[1] * z[1];
      return [
        z[0] + z[0] / magnitudeSquared,
        z[1] - z[1] / magnitudeSquared
      ];
    });
    const fit = mathFitTransform(mapped, [86, 62, 394, 190]);
    const airfoil = mapped.map(fit);
    const line = ctx.d3.line().curve(ctx.d3.curveLinearClosed);
    group.append("path").attr("class", "joukowski-airfoil").attr("d", line(airfoil))
      .attr("fill", ctx.textureFill).attr("stroke", ctx.palette.roles.ink).attr("stroke-width", 6).attr("stroke-linejoin", "round");
    const flowLines = [-34, -17, 0, 17, 34].map((offset) => ctx.d3.range(45).map((sample) => {
      const x = 82 + sample / 44 * 316;
      const normalized = (x - 240) / 154;
      const displacement = offset * (0.85 + 0.15 * normalized * normalized) - 18 * Math.exp(-normalized * normalized * 2.5) * (offset / 38);
      return [x, 126 + displacement];
    }));
    group.selectAll("path.joukowski-flow").data(flowLines).join("path").attr("class", "joukowski-flow")
      .attr("d", ctx.d3.line().curve(ctx.d3.curveBasis)).attr("fill", "none")
      .attr("stroke", (d, index) => ctx.palette.sequence[(index + 1) % ctx.palette.sequence.length])
      .attr("stroke-width", 2).attr("opacity", 0.72);
    group.append("circle").attr("class", "joukowski-map-pole").attr("cx", airfoil[0][0]).attr("cy", airfoil[0][1]).attr("r", 5).attr("fill", ctx.palette.roles.accent);
  }

  function renderHyperbolicGeodesics(group, ctx) {
    const center = [240, 126];
    const radius = 92;
    const clipId = ctx.uid("poincare-disc-clip");
    ctx.defs.append("clipPath").attr("id", clipId).append("circle").attr("cx", center[0]).attr("cy", center[1]).attr("r", radius);
    const anglePairs = [[-2.75, -0.55], [-2.35, 0.15], [-1.95, 0.75], [-1.45, 1.25], [-0.95, 1.85], [-0.4, 2.45], [0.15, 2.9]];
    const geodesics = anglePairs.map(([angleA, angleB]) => {
      const u = [Math.cos(angleA), Math.sin(angleA)];
      const v = [Math.cos(angleB), Math.sin(angleB)];
      const determinant = u[0] * v[1] - u[1] * v[0];
      const circleCenter = [(v[1] - u[1]) / determinant, (u[0] - v[0]) / determinant];
      const circleRadius = Math.sqrt(Math.max(0, circleCenter[0] * circleCenter[0] + circleCenter[1] * circleCenter[1] - 1));
      const start = Math.atan2(u[1] - circleCenter[1], u[0] - circleCenter[0]);
      const end = Math.atan2(v[1] - circleCenter[1], v[0] - circleCenter[0]);
      const candidates = [1, -1].map((direction) => {
        let delta = end - start;
        if (direction > 0 && delta < 0) delta += Math.PI * 2;
        if (direction < 0 && delta > 0) delta -= Math.PI * 2;
        return ctx.d3.range(61).map((sample) => {
          const angle = start + delta * sample / 60;
          return [circleCenter[0] + circleRadius * Math.cos(angle), circleCenter[1] + circleRadius * Math.sin(angle)];
        });
      });
      const chosen = candidates.sort((left, right) => {
        const leftScore = left.reduce((sum, point) => sum + Math.hypot(point[0], point[1]), 0);
        const rightScore = right.reduce((sum, point) => sum + Math.hypot(point[0], point[1]), 0);
        return leftScore - rightScore;
      })[0];
      return chosen.map((point) => [center[0] + point[0] * radius, center[1] + point[1] * radius]);
    });
    group.append("circle").attr("class", "poincare-disc").attr("cx", center[0]).attr("cy", center[1]).attr("r", radius)
      .attr("fill", ctx.textureFill).attr("fill-opacity", 0.18).attr("stroke", ctx.palette.roles.ink).attr("stroke-width", 6);
    group.append("g").attr("class", "hyperbolic-geodesic-field").attr("clip-path", `url(#${clipId})`)
      .selectAll("path.hyperbolic-geodesic").data(geodesics).join("path").attr("class", "hyperbolic-geodesic")
      .attr("d", ctx.d3.line().curve(ctx.d3.curveLinear)).attr("fill", "none")
      .attr("stroke", (d, index) => ctx.palette.sequence[index % ctx.palette.sequence.length])
      .attr("stroke-width", 5).attr("stroke-linecap", "round");
  }

  function renderEllipticGroupLaw(group, ctx) {
    const coefficientA = -1;
    const coefficientB = 0.3;
    const curveValue = (x) => x * x * x + coefficientA * x + coefficientB;
    const xDomain = [-1.22, 1.48];
    const xScale = ctx.d3.scaleLinear().domain(xDomain).range([98, 382]);
    const yScale = ctx.d3.scaleLinear().domain([-1.45, 1.45]).range([215, 38]);
    const branches = [];
    [1, -1].forEach((sign) => {
      let branch = [];
      ctx.d3.range(241).forEach((sample) => {
        const x = xDomain[0] + sample / 240 * (xDomain[1] - xDomain[0]);
        const value = curveValue(x);
        if (value >= 0) {
          branch.push([xScale(x), yScale(sign * Math.sqrt(value))]);
        } else if (branch.length > 1) {
          branches.push(branch);
          branch = [];
        } else {
          branch = [];
        }
      });
      if (branch.length > 1) branches.push(branch);
    });
    const xP = -0.88;
    const xQ = 1.13;
    const yP = Math.sqrt(curveValue(xP));
    const yQ = Math.sqrt(curveValue(xQ));
    const slope = (yQ - yP) / (xQ - xP);
    const xR = slope * slope - xP - xQ;
    const yOnLine = yP + slope * (xR - xP);
    const points = [
      { id: "p", point: [xScale(xP), yScale(yP)] },
      { id: "q", point: [xScale(xQ), yScale(yQ)] },
      { id: "minus-r", point: [xScale(xR), yScale(yOnLine)] },
      { id: "sum", point: [xScale(xR), yScale(-yOnLine)] }
    ];
    group.append("path").attr("class", "elliptic-axes").attr("d", mathSegmentsPath([[[98, yScale(0)], [382, yScale(0)]], [[xScale(0), 38], [xScale(0), 215]]]))
      .attr("fill", "none").attr("stroke", ctx.palette.roles.line).attr("stroke-width", 2);
    group.selectAll("path.elliptic-curve-branch").data(branches).join("path").attr("class", "elliptic-curve-branch")
      .attr("d", ctx.d3.line().curve(ctx.d3.curveLinear)).attr("fill", "none").attr("stroke", ctx.palette.roles.primary).attr("stroke-width", 6);
    const chordY0 = yP + slope * (xDomain[0] - xP);
    const chordY1 = yP + slope * (xDomain[1] - xP);
    group.append("path").attr("class", "elliptic-chord").attr("d", mathSegmentsPath([[[xScale(xDomain[0]), yScale(chordY0)], [xScale(xDomain[1]), yScale(chordY1)]], [points[2].point, points[3].point]]))
      .attr("fill", "none").attr("stroke", ctx.textureFill).attr("stroke-width", 4).attr("stroke-dasharray", "8 5");
    group.selectAll("circle.elliptic-group-point").data(points).join("circle").attr("class", (d) => `elliptic-group-point elliptic-${d.id}`)
      .attr("cx", (d) => d.point[0]).attr("cy", (d) => d.point[1]).attr("r", (d) => d.id === "sum" ? 8 : 5)
      .attr("fill", (d) => d.id === "sum" ? ctx.palette.roles.accent : ctx.palette.roles.ink);
  }

  function renderMobiusStrip(group, ctx) {
    const options = { cx: 240, cy: 126, scale: 61, rx: -0.62, ry: 0.32, perspective: 0.1 };
    const segments = 28;
    const halfWidth = 0.32;
    const surfacePoint = (angle, width) => [
      (1.45 + width * Math.cos(angle / 2)) * Math.cos(angle),
      (1.45 + width * Math.cos(angle / 2)) * Math.sin(angle),
      width * Math.sin(angle / 2)
    ];
    const faces = ctx.d3.range(segments).map((index) => {
      const a0 = index / segments * Math.PI * 2;
      const a1 = (index + 1) / segments * Math.PI * 2;
      const points = [
        mathProject3D(surfacePoint(a0, -halfWidth), options),
        mathProject3D(surfacePoint(a1, -halfWidth), options),
        mathProject3D(surfacePoint(a1, halfWidth), options),
        mathProject3D(surfacePoint(a0, halfWidth), options)
      ];
      return { index, points, depth: ctx.d3.mean(points, (point) => point[2]) };
    }).sort((a, b) => b.depth - a.depth);
    group.selectAll("path.mobius-face").data(faces).join("path")
      .attr("class", "mobius-face")
      .attr("d", (d) => mathPolygonPath(d.points))
      .attr("fill", (d) => d.index % 7 === 0 ? ctx.textureFill : ctx.palette.sequence[d.index % ctx.palette.sequence.length])
      .attr("stroke", ctx.palette.roles.background)
      .attr("stroke-width", 1.5)
      .attr("stroke-linejoin", "round");
    const boundary = [-halfWidth, halfWidth].map((width) => ctx.d3.range(121).map((sample) => {
      const angle = sample / 120 * Math.PI * 2;
      return mathProject3D(surfacePoint(angle, width), options);
    }));
    group.selectAll("path.mobius-boundary").data(boundary).join("path").attr("class", "mobius-boundary")
      .attr("d", ctx.d3.line().curve(ctx.d3.curveLinear)).attr("fill", "none").attr("stroke", ctx.palette.roles.ink).attr("stroke-width", 3);
  }

  function renderTorusKnot(group, ctx) {
    const options = { cx: 240, cy: 126, scale: 66, rx: -0.7, ry: 0.22, perspective: 0.09 };
    const samples = ctx.d3.range(181).map((sample) => {
      const t = sample / 180 * Math.PI * 2;
      const radial = 1.18 + 0.43 * Math.cos(3 * t);
      return mathProject3D([
        radial * Math.cos(2 * t),
        radial * Math.sin(2 * t),
        0.43 * Math.sin(3 * t)
      ], options);
    });
    const line = ctx.d3.line().curve(ctx.d3.curveCatmullRom.alpha(0.5));
    group.append("path").attr("class", "torus-knot-underlay").attr("d", line(samples))
      .attr("fill", "none").attr("stroke", ctx.palette.roles.inkDark).attr("stroke-width", 14).attr("stroke-linecap", "round").attr("stroke-linejoin", "round");
    const segmentSize = 3;
    const segments = ctx.d3.range(0, samples.length - 1, segmentSize).map((start) => {
      const points = samples.slice(start, Math.min(samples.length, start + segmentSize + 1));
      return { points, depth: ctx.d3.mean(points, (point) => point[2]), index: start / segmentSize };
    }).sort((a, b) => b.depth - a.depth);
    group.selectAll("path.torus-knot-segment").data(segments).join("path").attr("class", "torus-knot-segment")
      .attr("d", (d) => line(d.points)).attr("fill", "none")
      .attr("stroke", (d) => d.index % 9 === 0 ? ctx.textureFill : ctx.palette.sequence[d.index % ctx.palette.sequence.length])
      .attr("stroke-width", 8).attr("stroke-linecap", "round");
  }

  function renderRuledHyperboloid(group, ctx) {
    const center = [240, 126];
    const count = 17;
    const topY = 43;
    const bottomY = 209;
    const rx = 92;
    const ry = 27;
    const rotation = 0.82;
    const topPoints = ctx.d3.range(count).map((index) => {
      const angle = index / count * Math.PI * 2;
      return [center[0] + rx * Math.cos(angle), topY + ry * Math.sin(angle)];
    });
    const bottomA = ctx.d3.range(count).map((index) => {
      const angle = index / count * Math.PI * 2 + rotation;
      return [center[0] + rx * Math.cos(angle), bottomY + ry * Math.sin(angle)];
    });
    const bottomB = ctx.d3.range(count).map((index) => {
      const angle = index / count * Math.PI * 2 - rotation;
      return [center[0] + rx * Math.cos(angle), bottomY + ry * Math.sin(angle)];
    });
    const familyA = topPoints.map((point, index) => [point, bottomA[index]]);
    const familyB = topPoints.map((point, index) => [point, bottomB[index]]);
    group.append("path").attr("class", "hyperboloid-rulings-a").attr("d", mathSegmentsPath(familyA))
      .attr("fill", "none").attr("stroke", ctx.palette.roles.primary).attr("stroke-width", 3.5).attr("opacity", 0.86);
    group.append("path").attr("class", "hyperboloid-rulings-b").attr("d", mathSegmentsPath(familyB))
      .attr("fill", "none").attr("stroke", ctx.textureFill).attr("stroke-width", 3.5).attr("opacity", 0.82);
    group.append("ellipse").attr("class", "hyperboloid-rim-top").attr("cx", center[0]).attr("cy", topY).attr("rx", rx).attr("ry", ry)
      .attr("fill", "none").attr("stroke", ctx.palette.roles.ink).attr("stroke-width", 5);
    group.append("ellipse").attr("class", "hyperboloid-rim-bottom").attr("cx", center[0]).attr("cy", bottomY).attr("rx", rx).attr("ry", ry)
      .attr("fill", "none").attr("stroke", ctx.palette.roles.ink).attr("stroke-width", 5);
  }

  function renderTensegrityPrism(group, ctx) {
    const options = { cx: 240, cy: 126, scale: 58, rx: -0.32, ry: 0.38, perspective: 0.08 };
    const bottom = ctx.d3.range(3).map((index) => {
      const angle = index / 3 * Math.PI * 2 - Math.PI / 2;
      return mathProject3D([Math.cos(angle), -1.25, Math.sin(angle)], options);
    });
    const top = ctx.d3.range(3).map((index) => {
      const angle = index / 3 * Math.PI * 2 - Math.PI / 2 + 0.72;
      return mathProject3D([Math.cos(angle), 1.25, Math.sin(angle)], options);
    });
    const ringSegments = [];
    const crossCables = [];
    ctx.d3.range(3).forEach((index) => {
      ringSegments.push([bottom[index], bottom[(index + 1) % 3]], [top[index], top[(index + 1) % 3]]);
      crossCables.push([bottom[index], top[(index + 1) % 3]], [bottom[index], top[(index + 2) % 3]]);
    });
    const struts = ctx.d3.range(3).map((index) => [bottom[index], top[index]]);
    group.append("path").attr("class", "tensegrity-cable-network").attr("d", mathSegmentsPath(ringSegments.concat(crossCables)))
      .attr("fill", "none").attr("stroke", ctx.palette.roles.primary).attr("stroke-width", 3).attr("stroke-linecap", "round");
    group.selectAll("path.tensegrity-strut").data(struts).join("path").attr("class", "tensegrity-strut")
      .attr("d", (d) => mathSegmentsPath([d])).attr("fill", "none")
      .attr("stroke", (d, index) => index === 1 ? ctx.textureFill : ctx.palette.sequence[(index + 2) % ctx.palette.sequence.length])
      .attr("stroke-width", 13).attr("stroke-linecap", "round");
    group.selectAll("circle.tensegrity-joint").data(bottom.concat(top)).join("circle").attr("class", "tensegrity-joint")
      .attr("cx", (d) => d[0]).attr("cy", (d) => d[1]).attr("r", 6).attr("fill", ctx.palette.roles.accent).attr("stroke", ctx.palette.roles.background).attr("stroke-width", 2);
  }

  function renderMaxwellReciprocal(group, ctx) {
    const formNodes = [[92, 190], [150, 55], [208, 190], [150, 132]];
    const formEdges = [[0, 1], [1, 2], [2, 0], [0, 3], [1, 3], [2, 3]].map(([a, b]) => [formNodes[a], formNodes[b]]);
    const forceNodes = [[290, 177], [337, 56], [393, 151], [344, 207]];
    const forceEdges = forceNodes.map((point, index) => [point, forceNodes[(index + 1) % forceNodes.length]]);
    const spokes = forceNodes.map((point) => [[343, 143], point]);
    group.append("path").attr("class", "maxwell-form-diagram").attr("d", mathSegmentsPath(formEdges))
      .attr("fill", "none").attr("stroke", ctx.palette.roles.ink).attr("stroke-width", 6).attr("stroke-linecap", "round");
    group.append("path").attr("class", "maxwell-force-polygon").attr("d", mathPolygonPath(forceNodes))
      .attr("fill", ctx.textureFill).attr("fill-opacity", 0.24).attr("stroke", ctx.palette.roles.primary).attr("stroke-width", 6).attr("stroke-linejoin", "round");
    group.append("path").attr("class", "maxwell-reciprocal-spokes").attr("d", mathSegmentsPath(spokes))
      .attr("fill", "none").attr("stroke", ctx.palette.sequence[2]).attr("stroke-width", 2.5);
    group.append("path").attr("class", "maxwell-reciprocal-link").attr("d", "M228,126H263")
      .attr("fill", "none").attr("stroke", ctx.palette.roles.accent).attr("stroke-width", 5).attr("stroke-dasharray", "6 5");
    group.selectAll("circle.maxwell-form-node").data(formNodes).join("circle").attr("class", "maxwell-form-node")
      .attr("cx", (d) => d[0]).attr("cy", (d) => d[1]).attr("r", 5).attr("fill", ctx.palette.roles.accent);
  }

  function renderMedialAxis(group, ctx) {
    const center = [240, 126];
    const boundary = ctx.d3.range(48).map((index) => {
      const angle = index / 48 * Math.PI * 2;
      const radius = 82 + 19 * Math.cos(3 * angle) + 8 * Math.sin(5 * angle);
      return [center[0] + radius * Math.cos(angle), center[1] + radius * 0.78 * Math.sin(angle)];
    });
    const delaunay = ctx.d3.Delaunay.from(boundary);
    const triangleCount = delaunay.triangles.length / 3;
    const centers = ctx.d3.range(triangleCount).map((triangleIndex) => {
      const offset = triangleIndex * 3;
      const a = boundary[delaunay.triangles[offset]];
      const b = boundary[delaunay.triangles[offset + 1]];
      const c = boundary[delaunay.triangles[offset + 2]];
      const point = mathCircumcenter(a, b, c);
      if (!point || !ctx.d3.polygonContains(boundary, point)) return null;
      const radius = Math.min(...boundary.map((edgePoint) => Math.hypot(edgePoint[0] - point[0], edgePoint[1] - point[1])));
      return { point, radius };
    });
    const skeleton = [];
    for (let edge = 0; edge < delaunay.halfedges.length; edge += 1) {
      const opposite = delaunay.halfedges[edge];
      if (opposite <= edge) continue;
      const left = centers[Math.floor(edge / 3)];
      const right = centers[Math.floor(opposite / 3)];
      if (!left || !right || Math.min(left.radius, right.radius) < 9) continue;
      if (Math.hypot(left.point[0] - right.point[0], left.point[1] - right.point[1]) > 54) continue;
      skeleton.push([left.point, right.point]);
    }
    group.append("path").attr("class", "medial-source-silhouette").attr("d", mathPolygonPath(boundary))
      .attr("fill", ctx.textureFill).attr("fill-opacity", 0.18).attr("stroke", ctx.palette.roles.ink).attr("stroke-width", 5).attr("stroke-linejoin", "round");
    group.append("path").attr("class", "medial-axis-network").attr("d", mathSegmentsPath(skeleton))
      .attr("fill", "none").attr("stroke", ctx.palette.roles.primary).attr("stroke-width", 6).attr("stroke-linecap", "round").attr("stroke-linejoin", "round");
    const visibleCenters = centers.filter((entry) => entry && entry.radius >= 9);
    group.selectAll("circle.medial-disc-center").data(visibleCenters).join("circle").attr("class", "medial-disc-center")
      .attr("cx", (d) => d.point[0]).attr("cy", (d) => d.point[1]).attr("r", (d) => clamp(d.radius * 0.09, 2.5, 6))
      .attr("fill", ctx.palette.roles.accent);
  }

  function renderStringParabola(group, ctx) {
    const count = 22;
    const leftSegments = ctx.d3.range(count + 1).map((index) => {
      const t = index / count;
      return [[92 + 148 * t, 205], [92, 205 - 166 * t]];
    });
    const rightSegments = ctx.d3.range(count + 1).map((index) => {
      const t = index / count;
      return [[388 - 148 * t, 205], [388, 205 - 166 * t]];
    });
    group.append("path").attr("class", "string-parabola-left").attr("d", mathSegmentsPath(leftSegments))
      .attr("fill", "none").attr("stroke", ctx.palette.roles.primary).attr("stroke-width", 2.6).attr("opacity", 0.82);
    group.append("path").attr("class", "string-parabola-right").attr("d", mathSegmentsPath(rightSegments))
      .attr("fill", "none").attr("stroke", ctx.textureFill).attr("stroke-width", 2.6).attr("opacity", 0.82);
    group.append("path").attr("class", "string-parabola-baseline").attr("d", "M82,205H398")
      .attr("fill", "none").attr("stroke", ctx.palette.roles.ink).attr("stroke-width", 5).attr("stroke-linecap", "round");
    group.append("circle").attr("class", "string-parabola-focus").attr("cx", 240).attr("cy", 154).attr("r", 7).attr("fill", ctx.palette.roles.accent);
  }

  function renderCircleCaustic(group, ctx) {
    const center = [240, 126];
    const radius = 91;
    const rays = ctx.d3.range(19).map((index) => {
      const angle = -Math.PI / 2 + 0.15 + index / 18 * (Math.PI - 0.3);
      const normal = [Math.cos(angle), Math.sin(angle)];
      const hit = [center[0] + radius * normal[0], center[1] + radius * normal[1]];
      const incoming = [1, 0];
      const dot = incoming[0] * normal[0] + incoming[1] * normal[1];
      const reflected = [incoming[0] - 2 * dot * normal[0], incoming[1] - 2 * dot * normal[1]];
      return {
        incoming: [[82, hit[1]], hit],
        reflected: [hit, [hit[0] + reflected[0] * 185, hit[1] + reflected[1] * 185]]
      };
    });
    const clipId = ctx.uid("caustic-circle-clip");
    ctx.defs.append("clipPath").attr("id", clipId).append("circle").attr("cx", center[0]).attr("cy", center[1]).attr("r", radius);
    group.append("circle").attr("class", "caustic-reflector").attr("cx", center[0]).attr("cy", center[1]).attr("r", radius)
      .attr("fill", ctx.textureFill).attr("fill-opacity", 0.12).attr("stroke", ctx.palette.roles.ink).attr("stroke-width", 6);
    group.append("path").attr("class", "caustic-incoming-rays").attr("d", mathSegmentsPath(rays.map((ray) => ray.incoming)))
      .attr("fill", "none").attr("stroke", ctx.palette.roles.line).attr("stroke-width", 2);
    group.append("path").attr("class", "caustic-reflected-rays").attr("clip-path", `url(#${clipId})`).attr("d", mathSegmentsPath(rays.map((ray) => ray.reflected)))
      .attr("fill", "none").attr("stroke", ctx.palette.roles.primary).attr("stroke-width", 2.8).attr("opacity", 0.82);
    const nephroid = ctx.d3.range(181).map((sample) => {
      const t = sample / 180 * Math.PI * 2;
      const a = 20;
      return [center[0] + 3 * a * Math.cos(t) - a * Math.cos(3 * t), center[1] + 3 * a * Math.sin(t) - a * Math.sin(3 * t)];
    });
    group.append("path").attr("class", "nephroid-envelope").attr("d", ctx.d3.line().curve(ctx.d3.curveLinearClosed)(nephroid))
      .attr("fill", "none").attr("stroke", ctx.palette.roles.accent).attr("stroke-width", 7).attr("stroke-linejoin", "round");
  }

  function renderMoireBeat(group, ctx) {
    const clipId = ctx.uid("moire-field-clip");
    ctx.defs.append("clipPath").attr("id", clipId).append("rect").attr("x", 82).attr("y", 34).attr("width", 316).attr("height", 184).attr("rx", 34);
    group.append("rect").attr("class", "moire-field-surface").attr("x", 82).attr("y", 34).attr("width", 316).attr("height", 184).attr("rx", 34)
      .attr("fill", ctx.palette.roles.quiet).attr("stroke", ctx.palette.roles.ink).attr("stroke-width", 5);
    const clipLineToRect = (base, direction) => {
      let low = Number.NEGATIVE_INFINITY;
      let high = Number.POSITIVE_INFINITY;
      const limits = [[82, 398, 0], [34, 218, 1]];
      limits.forEach(([minimum, maximum, axis]) => {
        if (Math.abs(direction[axis]) < 1e-9) return;
        const first = (minimum - base[axis]) / direction[axis];
        const second = (maximum - base[axis]) / direction[axis];
        low = Math.max(low, Math.min(first, second));
        high = Math.min(high, Math.max(first, second));
      });
      if (!(low <= high)) return null;
      return [
        [base[0] + direction[0] * low, base[1] + direction[1] * low],
        [base[0] + direction[0] * high, base[1] + direction[1] * high]
      ];
    };
    const field = (angle, spacing, phase) => {
      const direction = [Math.cos(angle), Math.sin(angle)];
      const normal = [-direction[1], direction[0]];
      return ctx.d3.range(-28, 29).map((index) => {
        const offset = (index + phase) * spacing;
        const base = [240 + normal[0] * offset, 126 + normal[1] * offset];
        return clipLineToRect(base, direction);
      }).filter(Boolean);
    };
    const fieldA = field(0.19, 8.8, 0);
    const fieldB = field(0.275, 9.35, 0.42);
    const clipped = group.append("g").attr("class", "moire-interference-fields").attr("clip-path", `url(#${clipId})`);
    clipped.append("path").attr("class", "moire-frequency-a").attr("d", mathSegmentsPath(fieldA))
      .attr("fill", "none").attr("stroke", ctx.palette.roles.primary).attr("stroke-width", 2.8).attr("opacity", 0.72);
    clipped.append("path").attr("class", "moire-frequency-b").attr("d", mathSegmentsPath(fieldB))
      .attr("fill", "none").attr("stroke", ctx.palette.sequence[1]).attr("stroke-width", 2.4).attr("opacity", 0.54);
    group.append("path").attr("class", "moire-phase-markers").attr("d", "M102,52H164M316,200H378")
      .attr("fill", "none").attr("stroke", ctx.palette.roles.accent).attr("stroke-width", 6).attr("stroke-linecap", "round");
  }

  function renderPeaucellierLinkage(group, ctx) {
    const origin = [174, 126];
    const circleRadius = 52;
    const circleCenter = [origin[0] + circleRadius, origin[1]];
    const theta = 1.08;
    const localQ = [circleRadius + circleRadius * Math.cos(theta), circleRadius * Math.sin(theta)];
    const q = [origin[0] + localQ[0], origin[1] + localQ[1]];
    const invariant = 6500;
    const qMagnitudeSquared = localQ[0] * localQ[0] + localQ[1] * localQ[1];
    const p = [origin[0] + invariant * localQ[0] / qMagnitudeSquared, origin[1] + invariant * localQ[1] / qMagnitudeSquared];
    const diagonal = Math.hypot(p[0] - q[0], p[1] - q[1]);
    const bar = diagonal / 2 + 31;
    const midpoint = [(p[0] + q[0]) / 2, (p[1] + q[1]) / 2];
    const halfHeight = Math.sqrt(Math.max(0, bar * bar - diagonal * diagonal / 4));
    const unitPerpendicular = [-(p[1] - q[1]) / diagonal, (p[0] - q[0]) / diagonal];
    const b = [midpoint[0] + unitPerpendicular[0] * halfHeight, midpoint[1] + unitPerpendicular[1] * halfHeight];
    const d = [midpoint[0] - unitPerpendicular[0] * halfHeight, midpoint[1] - unitPerpendicular[1] * halfHeight];
    const traceX = origin[0] + invariant / (2 * circleRadius);
    const trace = ctx.d3.range(101).map((sample) => {
      const angle = 0.34 + sample / 100 * (Math.PI * 2 - 0.68);
      const local = [circleRadius + circleRadius * Math.cos(angle), circleRadius * Math.sin(angle)];
      const magnitudeSquared = local[0] * local[0] + local[1] * local[1];
      return [origin[0] + invariant * local[0] / magnitudeSquared, origin[1] + invariant * local[1] / magnitudeSquared];
    }).filter((point) => point[1] >= 35 && point[1] <= 215);
    group.append("circle").attr("class", "peaucellier-input-circle").attr("cx", circleCenter[0]).attr("cy", circleCenter[1]).attr("r", circleRadius)
      .attr("fill", "none").attr("stroke", ctx.palette.roles.line).attr("stroke-width", 3);
    group.append("path").attr("class", "peaucellier-straight-trace").attr("d", ctx.d3.line()(trace))
      .attr("fill", "none").attr("stroke", ctx.palette.roles.accent).attr("stroke-width", 7).attr("stroke-linecap", "round");
    const bars = [[origin, b], [origin, d], [b, p], [p, d], [d, q], [q, b]];
    group.append("path").attr("class", "peaucellier-bars").attr("d", mathSegmentsPath(bars))
      .attr("fill", "none").attr("stroke", ctx.palette.roles.primary).attr("stroke-width", 6).attr("stroke-linecap", "round").attr("stroke-linejoin", "round");
    group.append("path").attr("class", "peaucellier-invariant-line").attr("d", mathSegmentsPath([[origin, q], [q, p]]))
      .attr("fill", "none").attr("stroke", ctx.textureFill).attr("stroke-width", 3).attr("stroke-dasharray", "6 4");
    group.selectAll("circle.peaucellier-joint").data([origin, b, p, d, q]).join("circle").attr("class", "peaucellier-joint")
      .attr("cx", (point) => point[0]).attr("cy", (point) => point[1]).attr("r", 6).attr("fill", ctx.palette.roles.ink);
    group.append("path").attr("class", "peaucellier-trace-guide").attr("d", `M${traceX},35V215`)
      .attr("fill", "none").attr("stroke", ctx.palette.roles.accent).attr("stroke-width", 2).attr("opacity", 0.45);
  }

  function renderLorenzAttractor(group, ctx) {
    const sigma = 10;
    const rho = 28;
    const beta = 8 / 3;
    const dt = 0.0065;
    let state = [0.1, 0, 0];
    const derivative = ([x, y, z]) => [sigma * (y - x), x * (rho - z) - y, x * y - beta * z];
    const step = (current) => {
      const k1 = derivative(current);
      const k2 = derivative(current.map((value, index) => value + k1[index] * dt / 2));
      const k3 = derivative(current.map((value, index) => value + k2[index] * dt / 2));
      const k4 = derivative(current.map((value, index) => value + k3[index] * dt));
      return current.map((value, index) => value + dt * (k1[index] + 2 * k2[index] + 2 * k3[index] + k4[index]) / 6);
    };
    const raw = [];
    ctx.d3.range(4300).forEach((index) => {
      state = step(state);
      if (index > 650) raw.push([state[0], state[2]]);
    });
    const fit = mathFitTransform(raw, [92, 34, 388, 216]);
    const points = raw.map(fit);
    const line = ctx.d3.line().curve(ctx.d3.curveLinear);
    group.append("path").attr("class", "lorenz-trajectory-underlay").attr("d", line(points))
      .attr("fill", "none").attr("stroke", ctx.palette.roles.ink).attr("stroke-width", 5).attr("opacity", 0.28);
    group.append("path").attr("class", "lorenz-chaotic-trajectory").attr("d", line(points))
      .attr("fill", "none").attr("stroke", ctx.palette.roles.primary).attr("stroke-width", 2.2).attr("stroke-linecap", "round").attr("stroke-linejoin", "round");
    group.selectAll("circle.lorenz-state-marker").data([points[0], points[Math.floor(points.length * 0.54)], points[points.length - 1]]).join("circle")
      .attr("class", "lorenz-state-marker").attr("cx", (d) => d[0]).attr("cy", (d) => d[1]).attr("r", 5).attr("fill", (d, index) => index === 1 ? ctx.textureFill : ctx.palette.roles.accent);
  }

  function renderAffineIfs(group, ctx) {
    const random = seededRandom(ctx.d3, ctx.config.seed, "affine-ifs");
    let point = [0, 0];
    const buckets = [[], [], [], []];
    ctx.d3.range(4800).forEach((iteration) => {
      const value = random();
      let transformIndex;
      if (value < 0.01) transformIndex = 0;
      else if (value < 0.86) transformIndex = 1;
      else if (value < 0.93) transformIndex = 2;
      else transformIndex = 3;
      const [x, y] = point;
      if (transformIndex === 0) point = [0, 0.16 * y];
      if (transformIndex === 1) point = [0.85 * x + 0.04 * y, -0.04 * x + 0.85 * y + 1.6];
      if (transformIndex === 2) point = [0.2 * x - 0.26 * y, 0.23 * x + 0.22 * y + 1.6];
      if (transformIndex === 3) point = [-0.15 * x + 0.28 * y, 0.26 * x + 0.24 * y + 0.44];
      if (iteration > 40) buckets[transformIndex].push(point);
    });
    const xScale = ctx.d3.scaleLinear().domain([-2.3, 2.8]).range([159, 321]);
    const yScale = ctx.d3.scaleLinear().domain([0, 10]).range([216, 35]);
    const pointPath = (points) => points.map(([x, y]) => {
      const px = xScale(x).toFixed(2);
      const py = yScale(y).toFixed(2);
      return `M${px},${py}h1.55v1.55h-1.55Z`;
    }).join("");
    group.selectAll("path.affine-ifs-bucket").data(buckets).join("path").attr("class", "affine-ifs-bucket")
      .attr("d", pointPath)
      .attr("fill", (d, index) => index === 1 ? ctx.textureFill : ctx.palette.sequence[(index + 1) % ctx.palette.sequence.length])
      .attr("opacity", (d, index) => index === 1 ? 0.92 : 0.74);
    group.append("path").attr("class", "affine-ifs-ground").attr("d", "M144,218H336")
      .attr("fill", "none").attr("stroke", ctx.palette.roles.ink).attr("stroke-width", 4).attr("stroke-linecap", "round");
  }

  function renderCellularAutomaton(group, ctx) {
    const columns = 47;
    const rows = 27;
    const rule = 110;
    const cellWidth = 6;
    const cellHeight = 6;
    const startX = 99;
    const startY = 43;
    let state = ctx.d3.range(columns).map((index) => index === Math.floor(columns / 2) || ((ctx.config.seed >> (index % 8)) & 1) === 1 && index % 11 === 0);
    const buckets = [[], [], []];
    ctx.d3.range(rows).forEach((row) => {
      state.forEach((active, column) => {
        if (!active) return;
        const x = startX + column * cellWidth;
        const y = startY + row * cellHeight;
        buckets[row % buckets.length].push(`M${x},${y}h${cellWidth - 0.8}v${cellHeight - 0.8}h${-(cellWidth - 0.8)}Z`);
      });
      state = state.map((value, column) => {
        const left = state[(column - 1 + columns) % columns] ? 1 : 0;
        const center = value ? 1 : 0;
        const right = state[(column + 1) % columns] ? 1 : 0;
        const neighborhood = (left << 2) | (center << 1) | right;
        return ((rule >> neighborhood) & 1) === 1;
      });
    });
    group.append("rect").attr("class", "cellular-automaton-field").attr("x", startX - 5).attr("y", startY - 5)
      .attr("width", columns * cellWidth + 10).attr("height", rows * cellHeight + 10).attr("rx", 12)
      .attr("fill", ctx.palette.roles.quiet).attr("stroke", ctx.palette.roles.ink).attr("stroke-width", 4);
    group.selectAll("path.cellular-automaton-state").data(buckets).join("path").attr("class", "cellular-automaton-state")
      .attr("d", (d) => d.join(""))
      .attr("fill", (d, index) => index === 1 ? ctx.textureFill : ctx.palette.sequence[index % ctx.palette.sequence.length]);
  }

  function renderLogisticBifurcation(group, ctx) {
    const x0 = 90;
    const x1 = 390;
    const y0 = 38;
    const y1 = 215;
    const columns = 132;
    const buckets = [[], [], [], []];
    ctx.d3.range(columns).forEach((column) => {
      const r = 2.5 + column / (columns - 1) * 1.5;
      let value = 0.5 + ((ctx.config.seed % 17) - 8) * 0.001;
      ctx.d3.range(190).forEach(() => { value = r * value * (1 - value); });
      ctx.d3.range(32).forEach((sample) => {
        value = r * value * (1 - value);
        const x = x0 + column / (columns - 1) * (x1 - x0);
        const y = y1 - value * (y1 - y0);
        const bucket = Math.min(3, Math.floor(value * 4));
        buckets[bucket].push(`M${x.toFixed(2)},${y.toFixed(2)}h1.65v1.65h-1.65Z`);
      });
    });
    group.append("path").attr("class", "bifurcation-axes").attr("d", mathSegmentsPath([[[x0, y0], [x0, y1]], [[x0, y1], [x1, y1]]]))
      .attr("fill", "none").attr("stroke", ctx.palette.roles.ink).attr("stroke-width", 4).attr("stroke-linecap", "round");
    group.selectAll("path.logistic-attractor-band").data(buckets).join("path").attr("class", "logistic-attractor-band")
      .attr("d", (d) => d.join(""))
      .attr("fill", (d, index) => index === 2 ? ctx.textureFill : ctx.palette.sequence[index % ctx.palette.sequence.length])
      .attr("opacity", 0.88);
    group.append("path").attr("class", "period-doubling-threshold").attr("d", `M${x0 + (3.57 - 2.5) / 1.5 * (x1 - x0)},${y0}V${y1}`)
      .attr("fill", "none").attr("stroke", ctx.palette.roles.accent).attr("stroke-width", 2).attr("stroke-dasharray", "5 5");
  }

  function renderFieldStreamlines(group, ctx) {
    const bounds = [-1.8, -1.1, 1.8, 1.1];
    const toCanvas = (point) => [
      91 + (point[0] - bounds[0]) / (bounds[2] - bounds[0]) * 298,
      215 - (point[1] - bounds[1]) / (bounds[3] - bounds[1]) * 177
    ];
    const vector = ([x, y]) => [
      Math.sin(y * 2.2) + 0.42 * x - 0.16 * y,
      Math.cos(x * 1.65) - 0.36 * y + 0.12 * x
    ];
    const integrate = (seed, direction) => {
      const points = [seed];
      let current = seed;
      for (let step = 0; step < 105; step += 1) {
        const velocity = vector(current);
        const magnitude = Math.max(0.2, Math.hypot(velocity[0], velocity[1]));
        const dt = direction * 0.034 / magnitude;
        const midpoint = [current[0] + velocity[0] * dt / 2, current[1] + velocity[1] * dt / 2];
        const middleVelocity = vector(midpoint);
        const next = [current[0] + middleVelocity[0] * dt, current[1] + middleVelocity[1] * dt];
        if (next[0] < bounds[0] || next[0] > bounds[2] || next[1] < bounds[1] || next[1] > bounds[3]) break;
        points.push(next);
        current = next;
      }
      return points;
    };
    const seeds = ctx.d3.range(15).map((index) => [-1.58 + index / 14 * 3.16, -0.92 + (index % 4) * 0.58]);
    const streamlines = seeds.map((seed) => integrate(seed, -1).reverse().slice(0, -1).concat(integrate(seed, 1))).map((points) => points.map(toCanvas));
    group.append("rect").attr("class", "vector-field-domain").attr("x", 86).attr("y", 33).attr("width", 308).attr("height", 187).attr("rx", 18)
      .attr("fill", ctx.textureFill).attr("fill-opacity", 0.11).attr("stroke", ctx.palette.roles.ink).attr("stroke-width", 4);
    group.selectAll("path.field-streamline").data(streamlines).join("path").attr("class", "field-streamline")
      .attr("d", ctx.d3.line().curve(ctx.d3.curveBasis)).attr("fill", "none")
      .attr("stroke", (d, index) => index % 5 === 0 ? ctx.palette.roles.accent : ctx.palette.sequence[index % ctx.palette.sequence.length])
      .attr("stroke-width", (d, index) => index % 5 === 0 ? 4.5 : 3).attr("stroke-linecap", "round");
  }

  function renderNewtonBasin(group, ctx) {
    const columns = 54;
    const rows = 34;
    const x0 = 91;
    const y0 = 38;
    const width = 298;
    const height = 176;
    const roots = [[1, 0], [-0.5, Math.sqrt(3) / 2], [-0.5, -Math.sqrt(3) / 2]];
    const buckets = ctx.d3.range(9).map(() => []);
    const square = (value) => [value[0] * value[0] - value[1] * value[1], 2 * value[0] * value[1]];
    const multiply = (a, b) => [a[0] * b[0] - a[1] * b[1], a[0] * b[1] + a[1] * b[0]];
    ctx.d3.range(rows).forEach((row) => {
      ctx.d3.range(columns).forEach((column) => {
        let z = [-1.65 + column / (columns - 1) * 3.3, 1.08 - row / (rows - 1) * 2.16];
        let iteration = 0;
        for (; iteration < 19; iteration += 1) {
          const z2 = square(z);
          const z3 = multiply(z2, z);
          const f = [z3[0] - 1, z3[1]];
          if (Math.hypot(f[0], f[1]) < 1e-4) break;
          const derivative = [3 * z2[0], 3 * z2[1]];
          const denominator = derivative[0] * derivative[0] + derivative[1] * derivative[1];
          if (denominator < 1e-10) break;
          const quotient = [(f[0] * derivative[0] + f[1] * derivative[1]) / denominator, (f[1] * derivative[0] - f[0] * derivative[1]) / denominator];
          z = [z[0] - quotient[0], z[1] - quotient[1]];
        }
        let rootIndex = 0;
        roots.forEach((root, index) => {
          if (Math.hypot(z[0] - root[0], z[1] - root[1]) < Math.hypot(z[0] - roots[rootIndex][0], z[1] - roots[rootIndex][1])) rootIndex = index;
        });
        const speedBand = Math.min(2, Math.floor(iteration / 7));
        const bucket = rootIndex * 3 + speedBand;
        const x = x0 + column / columns * width;
        const y = y0 + row / rows * height;
        buckets[bucket].push(`M${x.toFixed(2)},${y.toFixed(2)}h${(width / columns + 0.2).toFixed(2)}v${(height / rows + 0.2).toFixed(2)}h${(-width / columns - 0.2).toFixed(2)}Z`);
      });
    });
    group.append("rect").attr("class", "newton-basin-frame").attr("x", x0 - 4).attr("y", y0 - 4).attr("width", width + 8).attr("height", height + 8).attr("rx", 12)
      .attr("fill", ctx.palette.roles.quiet).attr("stroke", ctx.palette.roles.ink).attr("stroke-width", 5);
    group.selectAll("path.newton-basin-region").data(buckets).join("path").attr("class", "newton-basin-region")
      .attr("d", (d) => d.join(""))
      .attr("fill", (d, index) => index === 4 ? ctx.textureFill : ctx.palette.sequence[Math.floor(index / 3) % ctx.palette.sequence.length])
      .attr("opacity", (d, index) => 0.48 + (index % 3) * 0.24);
    group.selectAll("circle.newton-root").data(roots).join("circle").attr("class", "newton-root")
      .attr("cx", (root) => x0 + (root[0] + 1.65) / 3.3 * width)
      .attr("cy", (root) => y0 + (1.08 - root[1]) / 2.16 * height)
      .attr("r", 5).attr("fill", ctx.palette.roles.accent).attr("stroke", ctx.palette.roles.background).attr("stroke-width", 2);
  }

  function renderSteinerTree(group, ctx) {
    const terminals = [[112, 190], [214, 43], [374, 184]];
    let junction = [ctx.d3.mean(terminals, (point) => point[0]), ctx.d3.mean(terminals, (point) => point[1])];
    ctx.d3.range(80).forEach(() => {
      const weights = terminals.map((point) => 1 / Math.max(1e-6, Math.hypot(point[0] - junction[0], point[1] - junction[1])));
      const total = ctx.d3.sum(weights);
      junction = [
        ctx.d3.sum(terminals, (point, index) => point[0] * weights[index]) / total,
        ctx.d3.sum(terminals, (point, index) => point[1] * weights[index]) / total
      ];
    });
    const network = terminals.map((terminal) => [junction, terminal]);
    group.append("path").attr("class", "steiner-terminal-hull").attr("d", mathPolygonPath(terminals))
      .attr("fill", ctx.textureFill).attr("fill-opacity", 0.13).attr("stroke", ctx.palette.roles.line).attr("stroke-width", 3);
    group.selectAll("path.steiner-branch").data(network).join("path").attr("class", "steiner-branch")
      .attr("d", (d) => mathSegmentsPath([d])).attr("fill", "none")
      .attr("stroke", (d, index) => ctx.palette.sequence[index % ctx.palette.sequence.length])
      .attr("stroke-width", 10).attr("stroke-linecap", "round");
    group.selectAll("circle.steiner-terminal").data(terminals).join("circle").attr("class", "steiner-terminal")
      .attr("cx", (d) => d[0]).attr("cy", (d) => d[1]).attr("r", 12).attr("fill", ctx.palette.roles.ink).attr("stroke", ctx.palette.roles.background).attr("stroke-width", 3);
    group.append("circle").attr("class", "steiner-junction").attr("cx", junction[0]).attr("cy", junction[1]).attr("r", 14)
      .attr("fill", ctx.palette.roles.accent).attr("stroke", ctx.palette.roles.background).attr("stroke-width", 4);
    const angleMarkers = terminals.map((terminal) => {
      const dx = terminal[0] - junction[0];
      const dy = terminal[1] - junction[1];
      const length = Math.hypot(dx, dy);
      return [junction, [junction[0] + dx / length * 31, junction[1] + dy / length * 31]];
    });
    group.append("path").attr("class", "steiner-angle-markers").attr("d", mathSegmentsPath(angleMarkers))
      .attr("fill", "none").attr("stroke", ctx.palette.roles.background).attr("stroke-width", 2);
  }

  function renderPenroseSubstitution(group, ctx) {
    const phi = (1 + Math.sqrt(5)) / 2;
    const center = [240, 126];
    const radius = 94;
    let triangles = ctx.d3.range(10).map((index) => {
      const angleA = (2 * index - 1) * Math.PI / 10 - Math.PI / 2;
      const angleB = (2 * index + 1) * Math.PI / 10 - Math.PI / 2;
      const left = [center[0] + radius * Math.cos(angleA), center[1] + radius * Math.sin(angleA)];
      const right = [center[0] + radius * Math.cos(angleB), center[1] + radius * Math.sin(angleB)];
      return { type: 0, points: index % 2 === 0 ? [center, left, right] : [center, right, left] };
    });
    ctx.d3.range(3).forEach(() => {
      const next = [];
      triangles.forEach((triangle) => {
        const [a, b, c] = triangle.points;
        if (triangle.type === 0) {
          const p = [a[0] + (b[0] - a[0]) / phi, a[1] + (b[1] - a[1]) / phi];
          next.push({ type: 0, points: [c, p, b] });
          next.push({ type: 1, points: [p, c, a] });
        } else {
          const q = [b[0] + (a[0] - b[0]) / phi, b[1] + (a[1] - b[1]) / phi];
          const r = [b[0] + (c[0] - b[0]) / phi, b[1] + (c[1] - b[1]) / phi];
          next.push({ type: 1, points: [r, c, a] });
          next.push({ type: 1, points: [q, r, b] });
          next.push({ type: 0, points: [r, q, a] });
        }
      });
      triangles = next;
    });
    const buckets = [0, 1].map((type) => triangles.filter((triangle) => triangle.type === type).map((triangle) => mathPolygonPath(triangle.points)).join(""));
    group.selectAll("path.penrose-substitution-tile").data(buckets).join("path").attr("class", "penrose-substitution-tile")
      .attr("d", (d) => d)
      .attr("fill", (d, index) => index === 0 ? ctx.textureFill : ctx.palette.sequence[2])
      .attr("stroke", ctx.palette.roles.background).attr("stroke-width", 1.35).attr("stroke-linejoin", "round");
    group.append("circle").attr("class", "penrose-boundary").attr("cx", center[0]).attr("cy", center[1]).attr("r", radius)
      .attr("fill", "none").attr("stroke", ctx.palette.roles.ink).attr("stroke-width", 6);
    group.append("circle").attr("class", "penrose-center").attr("cx", center[0]).attr("cy", center[1]).attr("r", 6).attr("fill", ctx.palette.roles.accent);
  }

  const PATTERN_RENDERERS = Object.freeze({
    "d3-logo-type-orbit": renderTypeOrbit,
    "d3-logo-bezier-wordpath": renderBezierWordpath,
    "d3-logo-variable-axis-wordmark": renderVariableAxisWordmark,
    "d3-logo-ligature-bridge": renderLigatureBridge,
    "d3-logo-stencil-cuts": renderStencilCuts,
    "d3-logo-letter-window": renderLetterWindow,
    "d3-logo-mirrored-monogram": renderMirroredMonogram,
    "d3-logo-glyph-rosette": renderGlyphRosette,
    "d3-logo-baseline-wave": renderBaselineWave,
    "d3-logo-stack-offset": renderStackOffset,
    "d3-logo-slice-shift": renderSliceShift,
    "d3-logo-multi-stroke-wordmark": renderMultiStrokeWordmark,
    "d3-logo-extruded-wordmark": renderExtrudedWordmark,
    "d3-logo-letter-weave": renderLetterWeave,
    "d3-logo-responsive-lockup": renderResponsiveLockup,
    "d3-logo-spiral-trace": renderSpiralTrace,
    "d3-logo-orbit-network": renderOrbitNetwork,
    "d3-logo-grid-activation": renderGridActivation,
    "d3-logo-contour-fingerprint": renderContourFingerprint,
    "d3-logo-voronoi-shards": renderVoronoiShards,
    "d3-logo-animal-facets": renderAnimalFacets,
    "d3-logo-animal-surface-mask": renderAnimalSurfaceMask,
    "d3-logo-negative-space-reveal": renderNegativeSpaceReveal,
    "d3-logo-folded-ribbon": renderFoldedRibbon,
    "d3-logo-boolean-lens": renderBooleanLens,
    "d3-logo-radiant-pulse": renderRadiantPulse,
    "d3-logo-parametric-wave": renderParametricWave,
    "d3-logo-kaleidoscope-wedges": renderKaleidoscopeWedges,
    "d3-logo-polar-halo": renderPolarHalo,
    "d3-logo-aperture-iris": renderApertureIris,
    "d3-logo-terminal-extension": renderTerminalExtension,
    "d3-logo-vertical-rail-wordmark": renderVerticalRailWordmark,
    "d3-logo-hinged-glyph-fan": renderHingedGlyphFan,
    "d3-logo-justified-word-block": renderJustifiedWordBlock,
    "d3-logo-fill-outline-cadence": renderFillOutlineCadence,
    "d3-logo-punctuation-armature": renderPunctuationArmature,
    "d3-logo-circle-pack-cluster": renderCirclePackCluster,
    "d3-logo-treemap-mosaic": renderTreemapMosaic,
    "d3-logo-convex-hull-shells": renderConvexHullShells,
    "d3-logo-phyllotaxis-bloom": renderPhyllotaxisBloom,
    "d3-logo-tangency-chain": renderTangencyChain,
    "d3-logo-tangram-dissection": renderTangramDissection,
    "d3-logo-superellipse-family": renderSuperellipseFamily,
    "d3-logo-isometric-block-stack": renderIsometricBlockStack,
    "d3-logo-eulerian-one-stroke": renderEulerianOneStroke,
    "d3-logo-perfect-maze": renderPerfectMaze,
    "d3-logo-split-merge-stream": renderSplitMergeStream,
    "d3-logo-dendrogram-crown": renderDendrogramCrown,
    "d3-logo-linked-ring-chain": renderLinkedRingChain,
    "d3-logo-lsystem-branch": renderLsystemBranch,
    "d3-logo-hilbert-route": renderHilbertRoute,
    "d3-logo-reciprocal-profiles": renderReciprocalProfiles,
    "d3-logo-modular-gutter-symbol": renderModularGutterSymbol,
    "d3-logo-tangent-void-star": renderTangentVoidStar,
    "d3-logo-reciprocal-tessellation": renderReciprocalTessellation,
    "d3-logo-impossible-triangle": renderImpossibleTriangle,
    "d3-logo-necker-cube": renderNeckerCube,
    "d3-logo-kanizsa-closure": renderKanizsaClosure,
    "d3-logo-line-screen-silhouette": renderLineScreenSilhouette,
    "d3-logo-perspective-portal": renderPerspectivePortal,
    "d3-logo-reuleaux-body": renderReuleauxBody,
    "d3-logo-cassini-oval": renderCassiniOval,
    "d3-logo-polar-reciprocal": renderPolarReciprocal,
    "d3-logo-minkowski-sum": renderMinkowskiSum,
    "d3-logo-pedal-curve": renderPedalCurve,
    "d3-logo-involute-gear": renderInvoluteGear,
    "d3-logo-desargues-incidence": renderDesarguesIncidence,
    "d3-logo-circle-inversion": renderCircleInversion,
    "d3-logo-catenary-funicular": renderCatenaryFunicular,
    "d3-logo-joukowski-airfoil": renderJoukowskiAirfoil,
    "d3-logo-hyperbolic-geodesics": renderHyperbolicGeodesics,
    "d3-logo-elliptic-group-law": renderEllipticGroupLaw,
    "d3-logo-mobius-strip": renderMobiusStrip,
    "d3-logo-torus-knot": renderTorusKnot,
    "d3-logo-ruled-hyperboloid": renderRuledHyperboloid,
    "d3-logo-tensegrity-prism": renderTensegrityPrism,
    "d3-logo-maxwell-reciprocal": renderMaxwellReciprocal,
    "d3-logo-medial-axis": renderMedialAxis,
    "d3-logo-string-parabola": renderStringParabola,
    "d3-logo-circle-caustic": renderCircleCaustic,
    "d3-logo-moire-beat": renderMoireBeat,
    "d3-logo-peaucellier-linkage": renderPeaucellierLinkage,
    "d3-logo-lorenz-attractor": renderLorenzAttractor,
    "d3-logo-affine-ifs": renderAffineIfs,
    "d3-logo-cellular-automaton": renderCellularAutomaton,
    "d3-logo-logistic-bifurcation": renderLogisticBifurcation,
    "d3-logo-field-streamlines": renderFieldStreamlines,
    "d3-logo-newton-basin": renderNewtonBasin,
    "d3-logo-steiner-tree": renderSteinerTree,
    "d3-logo-penrose-substitution": renderPenroseSubstitution
  });

  function assertPaletteSafe(svgNode, palette) {
    const allowed = new Set(palette.allowed);
    const paintAttributes = ["fill", "stroke", "color", "stop-color", "flood-color"];
    for (const element of svgNode.querySelectorAll("*")) {
      for (const attribute of paintAttributes) {
        if (!element.hasAttribute(attribute)) continue;
        const raw = element.getAttribute(attribute).trim();
        const normalized = raw.toLowerCase();
        const isLocalPaintServer = /^url\(#[a-z0-9_.:-]+\)$/.test(normalized);
        if (normalized !== "none" && normalized !== "currentcolor" && !isLocalPaintServer && !allowed.has(normalized)) {
          throw new Error(`Palette violation in ${attribute}: ${raw}`);
        }
      }
    }
    if (svgNode.querySelector("linearGradient, radialGradient, meshgradient")) {
      throw new Error("Color-gradient elements are not permitted by the logo palette contract.");
    }
  }

  function renderTexture(target, input, options) {
    const d3 = getD3();
    const svgNode = target && typeof target.node === "function" ? target.node() : target;
    if (!svgNode || String(svgNode.localName).toLowerCase() !== "svg" || svgNode.namespaceURI !== SVG_NS) {
      throw new TypeError("renderTexture expects an SVG element or a D3 selection containing one SVG element.");
    }

    const renderOptions = options && typeof options === "object" ? options : {};
    const sourceConfig = input && typeof input === "object" ? input : {};
    const config = normalizeTextureConfig({
      ...sourceConfig,
      smallSize: sourceConfig.smallSize === true || sourceConfig.swatch === true || renderOptions.smallSize === true || renderOptions.swatch === true,
      outputWidth: renderOptions.outputWidth == null ? sourceConfig.outputWidth : renderOptions.outputWidth
    });
    const palette = COLORSETS[config.colorset];
    const texture = TEXTURE_BY_ID.get(config.textureId);
    const width = effectiveWidth(svgNode, config);
    const smallSize = config.smallSize || width < 128;
    const prefix = stableTexturePrefix(svgNode, config);
    const uid = makeIdFactory(prefix);
    const titleId = uid("title");
    const descId = uid("desc");
    const texturePatternId = uid("texture-fill");
    const svg = d3.select(svgNode);
    const flatFallback = config.textureStrength === 0 || (smallSize && config.textureId === "d3-logo-halftone-dots");

    svg.selectAll("*").remove();
    svg
      .attr("viewBox", VIEW_BOX)
      .attr("width", 480)
      .attr("height", 320)
      .attr("preserveAspectRatio", "xMidYMid meet")
      .attr("role", "img")
      .attr("focusable", "false")
      .attr("aria-labelledby", `${titleId} ${descId}`)
      .attr("data-example-id", config.exampleId)
      .attr("data-pattern-id", config.textureId)
      .attr("data-texture-id", config.textureId)
      .attr("data-geometry-signature", texture.geometrySignature)
      .attr("data-texture-family", texture.family || "")
      .attr("data-colorset", config.colorset)
      .attr("data-density", config.density)
      .attr("data-curvature", config.curvature)
      .attr("data-texture-strength", config.textureStrength)
      .attr("data-seed", config.seed)
      .attr("data-effective-width", width)
      .attr("data-small-size", smallSize ? "true" : "false")
      .attr("data-texture-flat-fallback", flatFallback ? "true" : "false");

    svg.append("title").attr("id", titleId).text(`${texture.label} — ${texture.id}`);
    svg.append("desc").attr("id", descId).text(
      `${config.accessibilityLabel}. ${texture.description || texture.label} Rendered from ${config.brand} in ${config.colorset}.`
    );

    const defs = svg.append("defs");
    const context = {
      d3,
      svg,
      svgNode,
      defs,
      uid,
      config,
      palette,
      texture,
      effectiveWidth: width,
      smallSize,
      texturePatternId,
      textureFillFallback: palette.roles.primary,
      textureFill: fragmentUrl(texturePatternId)
    };
    createTexture(defs, context);

    svg.append("rect")
      .attr("class", "texture-background")
      .attr("x", 0).attr("y", 0).attr("width", 480).attr("height", 320)
      .attr("fill", palette.roles.background);
    const swatch = svg.append("g")
      .attr("class", "texture-composition")
      .attr("data-example-id", config.exampleId)
      .attr("data-pattern-id", config.textureId)
      .attr("data-texture-id", config.textureId)
      .attr("data-geometry-signature", texture.geometrySignature)
      .attr("data-colorset", config.colorset);
    swatch.append("rect")
      .attr("class", "texture-surface")
      .attr("x", 18).attr("y", 18).attr("width", 444).attr("height", 284)
      .attr("rx", 0).attr("ry", 0)
      .attr("fill", fragmentUrl(texturePatternId))
      .attr("stroke", palette.roles.ink)
      .attr("stroke-width", 3);

    assertPaletteSafe(svgNode, palette);
    return svgNode;
  }

  function renderLogo(target, input, options) {
    const d3 = getD3();
    const svgNode = target && typeof target.node === "function" ? target.node() : target;
    if (!svgNode || String(svgNode.localName).toLowerCase() !== "svg" || svgNode.namespaceURI !== SVG_NS) {
      throw new TypeError("renderLogo expects an SVG element or a D3 selection containing one SVG element.");
    }

    const renderOptions = options && typeof options === "object" ? options : {};
    const sourceConfig = input && typeof input === "object" ? input : {};
    const config = normalizeConfig({
      ...sourceConfig,
      smallSize: sourceConfig.smallSize === true || sourceConfig.swatch === true || renderOptions.smallSize === true || renderOptions.swatch === true,
      outputWidth: renderOptions.outputWidth == null ? sourceConfig.outputWidth : renderOptions.outputWidth
    });
    const palette = COLORSETS[config.colorset];
    const pattern = PATTERN_BY_ID.get(config.patternId);
    const texture = TEXTURE_BY_ID.get(config.textureId);
    const renderer = PATTERN_RENDERERS[config.patternId];
    if (!renderer) throw new RangeError(`No pattern renderer for ${config.patternId}.`);

    const width = effectiveWidth(svgNode, config);
    const smallSize = config.smallSize || width < 128;
    const prefix = stablePrefix(svgNode, config);
    const uid = makeIdFactory(prefix);
    const titleId = uid("title");
    const descId = uid("desc");
    const texturePatternId = uid("texture-fill");
    const svg = d3.select(svgNode);

    svg.selectAll("*").remove();
    svg
      .attr("viewBox", VIEW_BOX)
      .attr("width", 480)
      .attr("height", 320)
      .attr("preserveAspectRatio", "xMidYMid meet")
      .attr("role", "img")
      .attr("focusable", "false")
      .attr("aria-labelledby", `${titleId} ${descId}`)
      .attr("data-composition-id", config.compositionId)
      .attr("data-example-id", config.exampleId)
      .attr("data-pattern-id", config.patternId)
      .attr("data-texture-id", config.textureId)
      .attr("data-colorset", config.colorset)
      .attr("data-geometry-signature", pattern.geometrySignature)
      .attr("data-intentional-text-occlusions", JSON.stringify(pattern.intentionalOcclusions || []))
      .attr("data-intentional-text-omissions", JSON.stringify(pattern.intentionalOmissions || []))
      .attr("data-font", config.font)
      .attr("data-density", config.density)
      .attr("data-curvature", config.curvature)
      .attr("data-scale", config.scale)
      .attr("data-rotation", config.rotation)
      .attr("data-texture-strength", config.textureStrength)
      .attr("data-seed", config.seed)
      .attr("data-effective-width", width)
      .attr("data-small-size", smallSize ? "true" : "false")
      .attr("data-texture-flat-fallback", config.textureStrength === 0 || (smallSize && config.textureId === "d3-logo-halftone-dots") ? "true" : "false");

    svg.append("title").attr("id", titleId).text(`${config.brand} — ${pattern.label}`);
    svg.append("desc").attr("id", descId).text(
      `${config.accessibilityLabel}. ${pattern.label} using ${texture.label} in ${config.colorset}.`
    );

    const defs = svg.append("defs");
    svg.append("rect")
      .attr("class", "logo-background")
      .attr("x", 0).attr("y", 0).attr("width", 480).attr("height", 320)
      .attr("fill", palette.roles.background);

    const context = {
      d3,
      svg,
      svgNode,
      defs,
      uid,
      config,
      palette,
      pattern,
      texture,
      effectiveWidth: width,
      smallSize,
      texturePatternId,
      textureFillFallback: palette.roles.primary,
      textureFill: config.textureStrength === 0 || (smallSize && config.textureId === "d3-logo-halftone-dots")
        ? palette.roles.primary
        : fragmentUrl(texturePatternId),
      brandHandled: false,
      taglineHandled: false
    };
    createTexture(defs, context);

    const compositionGroup = svg.append("g")
      .attr("class", "logo-composition")
      .attr("data-composition-id", config.compositionId)
      .attr("data-example-id", config.exampleId)
      .attr("data-pattern-id", config.patternId)
      .attr("data-texture-id", config.textureId)
      .attr("data-colorset", config.colorset)
      .attr("data-geometry-signature", pattern.geometrySignature);
    const markGroup = compositionGroup.append("g")
      .attr("class", `logo-mark logo-mark-${sanitizeId(config.patternId.replace(/^d3-logo-/, ""))}`)
      .attr("data-mechanism", pattern.geometrySignature)
      .attr("transform", `translate(240,145) rotate(${config.rotation}) scale(${config.scale}) translate(-240,-145)`);

    renderer(markGroup, context);
    applySafeMarkTransform(markGroup, context);
    if (!context.brandHandled) addBrandLockup(compositionGroup, context, 270);
    if (!context.taglineHandled) addTagline(compositionGroup, context, 302);
    annotateTextLayers(compositionGroup, context);
    assertPaletteSafe(svgNode, palette);
    return svgNode;
  }

  const API = Object.freeze({
    version: "1.0.0",
    d3Version: "7",
    VIEW_BOX,
    PATTERNS,
    TEXTURES,
    COMPOSITIONS,
    FONT_STACKS,
    FONTS,
    COLORSETS,
    PALETTES: COLORSETS,
    TEXTURE_RENDERER_IDS: Object.freeze(Object.keys(TEXTURE_RENDERERS)),
    normalizeConfig,
    normalizeTextureConfig,
    renderTexture,
    renderLogo
  });

  root.D3LogoDesign = API;
})(typeof window !== "undefined" ? window : globalThis);
