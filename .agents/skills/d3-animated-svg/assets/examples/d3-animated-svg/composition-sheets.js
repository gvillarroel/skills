(function () {
  const SVG_NS = "http://www.w3.org/2000/svg";

  const sheets = [
    {
      id: "balance-symmetry",
      order: "01",
      tab: "Balance",
      title: "Balance and Symmetry",
      metric: "center axes, mirrored weight, quadrant balance",
      summary: "Curated variants where the pattern reads from a stable center of mass instead of a loose default layout.",
      prompt: "Use these when the larger composition needs calm, comparison, or equal visual weight."
    },
    {
      id: "diagonal-armature",
      order: "02",
      tab: "Diagonal",
      title: "Diagonal Armature",
      metric: "major diagonal, minor diagonal, reciprocal diagonals",
      summary: "Curated variants where the same pattern family is reimagined as directional movement across the frame.",
      prompt: "Use these when a story needs entry, transition, conflict, or output energy."
    },
    {
      id: "golden-root",
      order: "03",
      tab: "Golden Root",
      title: "Golden and Root Divisions",
      metric: "golden section, root-2, root-3, root-5",
      summary: "Curated variants where a dominant field and a context field are separated by proportional divisions.",
      prompt: "Use these when one view is primary and the explanation, legend, or comparison is secondary."
    },
    {
      id: "thirds-fifths-grid",
      order: "04",
      tab: "Grid",
      title: "Thirds and Fifths Grid",
      metric: "third lines, fifth lines, modular rows",
      summary: "Curated variants where the pattern becomes a modular panel that can join a larger dashboard or report.",
      prompt: "Use these when repeated examples need shared rows, columns, headings, or aligned summaries."
    },
    {
      id: "radial-rosette",
      order: "05",
      tab: "Radial",
      title: "Radial and Rosette Composition",
      metric: "center, rings, spokes, rotational balance",
      summary: "Curated variants where the pattern works as a hub, orbit, ring, spoke system, or cyclic comparison.",
      prompt: "Use these when peer concepts should orbit a shared center or when the visual story is cyclical."
    },
    {
      id: "flow-spine",
      order: "06",
      tab: "Flow",
      title: "Flow Spine",
      metric: "source, transform, checkpoint, output",
      summary: "Curated variants where the pattern becomes one stage in a larger process or narrative path.",
      prompt: "Use these when the viewer should follow a source-to-output sequence."
    },
    {
      id: "dense-label-lanes",
      order: "07",
      tab: "Dense Labels",
      title: "Dense Label and Leader Lanes",
      metric: "external lanes, clearance bands, leader underpasses",
      summary: "Curated variants where dense points, labels, or annotations are separated into readable lanes.",
      prompt: "Use these when the data field must stay visible while text remains inspectable."
    }
  ];

  const variants = [
    ["balance-symmetry", "force-network", "network", "balanced network", "Split clusters around the center axis and keep bridge nodes near the visual middle."],
    ["diagonal-armature", "force-network", "network", "diagonal network", "Place source cluster low-left and outcome cluster high-right with bridges on the major diagonal."],
    ["radial-rosette", "force-network", "network", "radial network", "Turn the graph into a hub with peer clusters orbiting in rings."],
    ["balance-symmetry", "asymmetric-task-overlap", "set-overlap", "balanced overlap", "Center the shared task field and counterweight each side with scope labels."],
    ["dense-label-lanes", "asymmetric-task-overlap-saturated", "lanes", "external label lanes", "Keep the 100-task field central and move all text to audited outside lanes."],
    ["balance-symmetry", "mirrored-beeswarm", "scatter", "mirrored distribution", "Use mirrored swarms as left/right balance around a shared baseline."],
    ["diagonal-armature", "connected-scatter", "scatter", "diagonal trajectory", "Use the path as a diagonal change vector, with labels outside the route."],
    ["thirds-fifths-grid", "scatterplot-matrix", "matrix", "matrix grid", "Make every small panel share modular row and column guides."],
    ["dense-label-lanes", "pen-label-optimizer", "lanes", "optimized labels", "Move label candidates into lanes and reserve the active field for points."],
    ["dense-label-lanes", "occlusion-labels", "lanes", "label visibility lanes", "Keep only readable labels in the data field and push secondary labels outside."],
    ["golden-root", "treemap", "hierarchy", "golden treemap", "Give the largest branch the long field and reserve the short field for context."],
    ["thirds-fifths-grid", "treemap", "hierarchy", "modular treemap", "Snap group blocks to fifth columns so it can join a dashboard grid."],
    ["balance-symmetry", "circle-pack", "hierarchy", "centered pack", "Keep parent mass centered and distribute child bubbles as counterweights."],
    ["radial-rosette", "radial-hierarchy", "hierarchy", "radial hierarchy", "Use root-to-leaf branches as spokes around a central node."],
    ["radial-rosette", "sunburst", "radial", "partition rosette", "Use nested rings to keep hierarchy and cycle visible at once."],
    ["golden-root", "sunburst", "radial", "golden radial field", "Let the radial field dominate and use a short side strip for totals."],
    ["flow-spine", "sankey", "flow", "spine sankey", "Align source, transform, and output stages on one reading path."],
    ["diagonal-armature", "sankey", "flow", "diagonal sankey", "Tilt stage centers along the diagonal to show escalation or progress."],
    ["flow-spine", "alluvial", "flow", "category handoff spine", "Use the alluvial bands as a left-to-right handoff system."],
    ["diagonal-armature", "geo-route", "route", "diagonal route", "Use the route as the major diagonal and pin waypoints to reciprocal nodes."],
    ["flow-spine", "flow-tokens", "flow", "token stream", "Use moving tokens along the spine to show cadence and direction."],
    ["flow-spine", "critical-path", "flow", "critical path spine", "Place dependencies on a clear process spine and reserve branches for risks."],
    ["diagonal-armature", "critical-path", "flow", "diagonal critical path", "Put the critical dependency path on the major diagonal."],
    ["thirds-fifths-grid", "data-table-grid", "table", "structured table grid", "Use row bands and column fifths for scan-friendly tabular comparison."],
    ["golden-root", "inline-bar-table", "table", "dominant table field", "Let values use the long field and keep notes in the short field."],
    ["thirds-fifths-grid", "pivot-heat-table", "table", "modular heat table", "Snap heat cells to a modular grid so totals and rows align."],
    ["thirds-fifths-grid", "sortable-rank-table", "table", "rank modules", "Use grid rows as stable landing positions for sorted rows."],
    ["thirds-fifths-grid", "calendar-year", "matrix", "calendar module", "Use fifth columns and repeated rows to make the calendar a dashboard tile."],
    ["thirds-fifths-grid", "waffle", "matrix", "unit grid", "Use exact modular cells for part-to-whole composition."],
    ["thirds-fifths-grid", "context-window-matrix", "matrix", "context grid", "Use the grid as a finite capacity field with clear filled and empty slots."],
    ["thirds-fifths-grid", "attention-matrix-tiles", "matrix", "attention tile grid", "Keep rows, columns, and masked regions snapped to consistent modules."],
    ["golden-root", "document-token-quality", "document", "document plus summary", "Use the document as the long field and place quality summary in the short field."],
    ["golden-root", "gemma-comparison", "table", "scorecard split", "Give metrics the long side and keep model identity or caveats in the short side."],
    ["balance-symmetry", "population-pyramid", "bar", "mirrored age bars", "Use mirrored bars as explicit left/right balance."],
    ["diagonal-armature", "slope", "bar", "slope diagonal", "Use before and after endpoints as a diagonal comparison path."],
    ["flow-spine", "bar-race", "bar", "rank movement spine", "Let bars move along a stable track with winners landing at the output end."],
    ["radial-rosette", "chord", "radial", "chord rosette", "Use symmetric ring placement for reciprocal category flow."],
    ["radial-rosette", "token-roulette-sampler", "radial", "roulette wheel", "Keep weighted probabilities on a circular field with a fixed pointer."],
    ["radial-rosette", "circular-bar", "radial", "radial magnitude", "Use equal angular slots to compare categories around a ring."],
    ["radial-rosette", "radar", "radial", "metric rosette", "Use spokes as peer metric axes around one profile center."],
    ["radial-rosette", "polar-clock", "radial", "cycle clock", "Use circular time to organize a repeated sequence."],
    ["radial-rosette", "moon-phases", "radial", "phase ring", "Place phases around a cycle so state changes feel continuous."],
    ["radial-rosette", "symmetric-five-circle-rosette", "set-overlap", "five circle rosette", "Use equal peer circles as petals around a shared concept."],
    ["flow-spine", "d3-sequence-lifelines", "flow", "sequence spine", "Use lifelines as parallel tracks along the reading path."],
    ["flow-spine", "d3-state-machine", "flow", "state transition spine", "Place start, decision, and final states on a clear process path."],
    ["flow-spine", "d3-gantt-rollout", "flow", "rollout spine", "Use time as the main spine and reserve milestones for crossing nodes."],
    ["flow-spine", "d3-git-graph", "flow", "branch spine", "Treat mainline commits as spine and branches as temporary excursions."],
    ["flow-spine", "qkv-projection-flow", "flow", "QKV split spine", "Keep token input, projection split, and attention output on one path."],
    ["flow-spine", "flashattention-blocks", "matrix", "block movement spine", "Use memory transfer as a repeated checkpoint flow."],
    ["flow-spine", "moe-router-capacity", "flow", "router spine", "Use source tokens, routing decisions, expert capacity, and overflow as stages."],
    ["flow-spine", "speculative-decoding-verify", "flow", "verify spine", "Show draft, accept, reject, and target correction as sequential checkpoints."],
    ["flow-spine", "web-load-timeline", "flow", "page load spine", "Use load phases as a single timeline with secondary lanes."],
    ["dense-label-lanes", "airports-voronoi", "lanes", "service labels", "Keep service regions visible while airport names sit in outside lanes."],
    ["dense-label-lanes", "bubble-scatter", "scatter", "bubble label lanes", "Keep bubbles in the active field and route callouts to margins."],
    ["dense-label-lanes", "point-cloud", "scatter", "point cloud lanes", "Use outside lanes for selected points so the cloud remains legible."],
    ["dense-label-lanes", "hr-diagram", "scatter", "star labels", "Reserve lane labels for standout stars while preserving dense field texture."],
    ["dense-label-lanes", "word-cloud", "labels", "word field lanes", "Use the largest words as anchors and shift secondary text into bands."],
    ["diagonal-armature", "attention-arc-decoding", "flow", "attention diagonal", "Let the next-token slot pull attention arcs along a diagonal read."],
    ["diagonal-armature", "qkv-projection-flow", "flow", "projection diagonal", "Use the diagonal to show embedding split and recombination."],
    ["diagonal-armature", "lora-rank-update", "matrix", "rank bridge", "Use a diagonal bridge between frozen matrix and low-rank update."],
    ["balance-symmetry", "kanban-assignee-virtual-legend", "table", "balanced kanban", "Use the virtual legend column as right-side counterweight."],
    ["thirds-fifths-grid", "kanban-assignee-board", "table", "kanban modules", "Snap columns and cards to consistent modular tracks."],
    ["golden-root", "token-probability-sampler", "bar", "probability focus", "Use the long field for probabilities and the short field for selected output."],
    ["balance-symmetry", "boxplot", "bar", "balanced distribution", "Center group summaries and use whiskers as horizontal counterweight."]
  ].map(([compositionId, sourceId, kind, variantTitle, recipe]) => ({
    compositionId,
    sourceId,
    kind,
    variantTitle,
    recipe,
    id: `d3-composition-${compositionId}-${sourceId}`
  }));

  const semanticVariantExclusions = new Set([
    "d3-composition-diagonal-armature-apollonius-circles",
    "d3-composition-diagonal-armature-smooth-zoom",
    "d3-composition-diagonal-armature-xy-zoom",
    "d3-composition-golden-root-context-to-curve",
    "d3-composition-thirds-fifths-grid-context-to-curve",
    "d3-composition-radial-rosette-epicyclic-gearing",
    "d3-composition-radial-rosette-lasso-selection",
    "d3-composition-radial-rosette-shape-tween"
  ]);

  const metadata = (window.D3_ANIMATED_SVG_EXAMPLES || []).map((example, index) => ({ ...example, index }));
  const sourceById = new Map(metadata.map(example => [example.id, example]));
  const reviewedPatterns = metadata.map(reviewPatternForComposition);
  mergeGeneratedVariants(reviewedPatterns);

  window.D3_COMPOSITION_SHEETS = sheets;
  window.D3_COMPOSITION_VARIANTS = variants;
  window.D3_COMPOSITION_REVIEW = reviewedPatterns;

  const state = {
    sheetId: resolveInitialSheetId(),
    query: ""
  };

  function resolveInitialSheetId() {
    const hash = window.location.hash.replace(/^#/, "");
    if (sheets.some(sheet => sheet.id === hash)) return hash;
    const variant = variants.find(item => item.id === hash);
    return variant ? variant.compositionId : sheets[0].id;
  }

  function escapeHtml(value) {
    return String(value)
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#039;");
  }

  function hashString(value) {
    let hash = 2166136261;
    for (const char of String(value)) {
      hash ^= char.charCodeAt(0);
      hash = Math.imul(hash, 16777619);
    }
    return hash >>> 0;
  }

  function sourceTitle(source) {
    return source?.title || source?.id || "D3 pattern";
  }

  function titleWords(source) {
    return sourceTitle(source)
      .replace(/[^a-zA-Z0-9 ]/g, " ")
      .split(/\s+/)
      .filter(Boolean)
      .slice(0, 4);
  }

  function inferPatternKind(source) {
    const id = source.id || "";
    const family = `${source.kicker || ""} ${source.title || ""}`.toLowerCase();
    if (/airport/.test(family) || /airport/.test(id)) return "geospatial";
    if (/table|kanban|scorecard|document|gemma/.test(family) || /table|kanban|document|gemma/.test(id)) return "table";
    if (/matrix|heatmap|calendar|waffle|context|attention|correlogram|rectbin|tile|matmul/.test(family) || /matrix|calendar|waffle|context|attention|matmul/.test(id)) return "matrix";
    if (/\boverlap\b|\bvenn\b/.test(family) || /overlap|venn|circle-rosette|circle-chain|circle-cluster|circle-bridge|three-circle|five-circle|seven-circle/.test(id)) return "set-overlap";
    if (/\bflow\b|sankey|alluvial|sequence|state|gantt|git|journey|dag|pipeline|tokens|routing|router|decode|projection flow|parallel sets/.test(family) || /sankey|alluvial|(^|-)flow($|-)|sequence|state|gantt|git|journey|qkv|router|decoding|parallel-sets/.test(id)) return "flow";
    if (/network|simulation|bundle|arc diagram|quadtree|delaunay|voronoi|mesh|hulls|collisions/.test(family) || /network|bundle|quadtree|delaunay|voronoi|hulls|collisions/.test(id)) return "network";
    if (/hierarchy|tree|treemap|pack|sunburst|icicle|dendrogram|tangle/.test(family) || /tree|treemap|pack|sunburst|icicle|dendrogram|tangle/.test(id)) return "hierarchy";
    if (/radial|polar|chord|clock|moon|orbit|roulette|circular|rosette|flower|gear/.test(family) || /radial|polar|chord|clock|moon|orbit|roulette|circular|rosette|epicyclic/.test(id)) return "radial";
    if (/label|word|text/.test(family) || /label|word|text/.test(id)) return "lanes";
    if (/geo|map|projection|route|cartogram|choropleth|satellite|terminator|airport/.test(family) || /geo|map|projection|route|cartogram|choropleth|satellite|terminator|airport/.test(id)) return "geospatial";
    if (/temporal|financial|ranking|performance|timeline|slope|bump|line|area|bar|histogram|distribution|density|scatter|science|diagnostic|uncertainty/.test(family) || /line|area|bar|histogram|scatter|density|slope|bump|timeline|forecast|plot/.test(id)) return "chart";
    if (/morph|geometry|drawing|motion|interaction|brush|zoom|lasso|cursor/.test(family) || /tween|curve|brush|zoom|lasso|cursor|path|shape/.test(id)) return "geometry";
    return "chart";
  }

  function targetSpec(compositionId, source, renderer, reason) {
    const details = {
      "balance-symmetry": {
        variantTitle: "balanced quadrant version",
        armatureLines: "vertical center, horizontal center, mirrored diagonals",
        quadrants: "Q2/Q3 carry origin mass; Q1/Q4 counterweight outcomes",
        recipe: `Recompose ${sourceTitle(source)} around the center cross so the dominant marks balance across all four quadrants.`
      },
      "diagonal-armature": {
        variantTitle: "diagonal armature version",
        armatureLines: "major low-left to high-right line, reciprocal diagonal, parallel offsets",
        quadrants: "Q3 starts the reading path; Q1 resolves it; Q2/Q4 hold context",
        recipe: `Recompose ${sourceTitle(source)} onto a low-left to high-right armature while preserving its original data relationship.`
      },
      "golden-root": {
        variantTitle: "golden/root split version",
        armatureLines: "golden vertical split, root horizontal split, dominant field boundary",
        quadrants: "left long field carries primary marks; right short field carries legend, totals, or comparison",
        recipe: `Recompose ${sourceTitle(source)} into a dominant field and a proportional context field.`
      },
      "thirds-fifths-grid": {
        variantTitle: "thirds/fifths grid version",
        armatureLines: "third columns, fifth columns, modular rows",
        quadrants: "Q2/Q1 header row; Q3/Q4 repeated modules and summaries",
        recipe: `Recompose ${sourceTitle(source)} as aligned rows, columns, or modules that can join a larger sheet.`
      },
      "radial-rosette": {
        variantTitle: "radial rosette version",
        armatureLines: "center, inner ring, outer ring, eight spokes",
        quadrants: "center holds the semantic root; Q1-Q4 carry peer spokes or cycle stages",
        recipe: `Recompose ${sourceTitle(source)} around a real center with ring and spoke structure.`
      },
      "flow-spine": {
        variantTitle: "flow spine version",
        armatureLines: "source-to-output spline, station dividers, checkpoint cross-line",
        quadrants: "Q3 source, Q2 transform, Q4 checkpoint, Q1 output",
        recipe: `Recompose ${sourceTitle(source)} as a source-to-output path with branches returning to the spine.`
      },
      "dense-label-lanes": {
        variantTitle: "dense label lane version",
        armatureLines: "central field, left lane, right lane, leader-line underpasses",
        quadrants: "Q2/Q3 left labels; Q1/Q4 right labels; center preserves data marks",
        recipe: `Recompose ${sourceTitle(source)} with data marks in the field and labels routed into outside lanes.`
      }
    }[compositionId];
    return { compositionId, renderer, reason, ...details };
  }

  function sourceNarrativeText(source, kind) {
    return [
      source.id,
      source.kicker,
      source.title,
      source.copy,
      kind
    ].filter(Boolean).join(" ").toLowerCase();
  }

  function addNarrativeTargets(source, kind, add) {
    const id = source.id || "";
    const text = sourceNarrativeText(source, kind);
    const is = (...ids) => ids.includes(id);
    const has = regex => regex.test(id) || regex.test(text);

    if (is(
      "force-network",
      "beeswarm",
      "sketchy-beeswarm",
      "boxplot",
      "violin",
      "mirrored-beeswarm",
      "population-pyramid",
      "diverging-stack",
      "gemma-comparison",
      "sketchy-gemma-comparison",
      "projection-comparison",
      "tanglegram",
      "vaccine-impact",
      "binary-classifier",
      "binary-classifier-labeled"
    )) {
      add("balance-symmetry", "scatter", "the story is comparative, so the composition should expose counterweight across the center");
    }
    if (is(
      "asymmetric-task-overlap",
      "venn-three-circle",
      "venn-five-overlap",
      "venn-seven-overlap",
      "asymmetric-three-circle-chain",
      "asymmetric-five-circle-cluster",
      "asymmetric-seven-circle-bridge"
    )) {
      add("balance-symmetry", "set-overlap", "overlap strength is judged by visible mass on both sides of the shared center");
    }
    if (is("symmetric-three-circle-rosette", "symmetric-five-circle-rosette", "symmetric-seven-circle-flower")) {
      add("balance-symmetry", "set-overlap", "equal peer sets need stable quadrant weight before the shared center can read clearly");
      add("radial-rosette", "set-overlap", "equal peer sets have a real orbital center instead of a forced decorative circle");
    }
    if (is("chord", "directed-chord")) {
      add("balance-symmetry", "radial", "reciprocal ribbons need quadrant balance so dominant exchanges do not visually collapse to one side");
    }
    if (is("parallel-coordinates", "ternary", "point-range", "bullet")) {
      add("balance-symmetry", "scatter", "the marks compare opposing ranges, targets, or mixtures around a central decision line");
    }

    if (is(
      "connected-scatter",
      "sketchy-line-chart",
      "slope",
      "bump",
      "waterfall",
      "event-cascade",
      "difference-chart",
      "moving-average",
      "index-chart",
      "forecast-fan",
      "line-missing-data",
      "area-missing-data",
      "variable-color-line",
      "line-cursor",
      "you-draw-it",
      "bar-race",
      "logit-lens-rank-bump",
      "web-load-timeline",
      "marey-trains"
    )) {
      add("diagonal-armature", "scatter", "the reading path is a change over time or rank, so diagonal rise/fall clarifies direction");
    }
    if (is("geo-route", "world-tour", "satellite-projection", "solar-path")) {
      add("diagonal-armature", "route", "the spatial path has an origin and destination, so the diagonal can carry travel direction");
    }
    if (is("airports-voronoi")) {
      add("diagonal-armature", "route", "airport points keep relative spacing while the diagonal reads as near-to-far service reach");
    }
    if (is("freehand-trace", "ai-line-writing", "pen-curve-study", "path-tween", "arc-tween")) {
      add("diagonal-armature", "flow", "the motion trace has a natural handoff direction that benefits from a visible ascent");
    }
    if (is("critical-path", "attention-arc-decoding", "qkv-projection-flow", "token-boxes-to-context-window")) {
      add("diagonal-armature", "flow", "the component already describes staged transformation, so the diagonal can show escalation toward output");
    }

    if (is(
      "document-token-quality",
      "document-token-quality-red",
      "document-token-extraction-buckets",
      "agent-loop-partial-covers",
      "gemma-comparison",
      "sketchy-gemma-comparison",
      "inline-bar-table",
      "column-profile-table",
      "focus-context",
      "hierarchical-bars",
      "treemap",
      "sketchy-treemap",
      "circle-pack",
      "tidy-tree",
      "cluster-dendrogram",
      "tangled-tree",
      "tangled-tree-levels",
      "token-probability-sampler",
      "temperature-softmax",
      "nucleus-sampling",
      "logit-lens-rank-bump",
      "candlestick",
      "bollinger-bands"
    )) {
      add("golden-root", has(/tree|treemap|pack|dendrogram|tangle/) ? "hierarchy" : kind === "table" ? "table" : "matrix", "one dominant artifact needs a smaller context field for explanation, legend, or comparison");
    }

    if (is(
      "adjacency-matrix",
      "data-table-grid",
      "inline-bar-table",
      "pivot-heat-table",
      "sortable-rank-table",
      "sparkline-table",
      "column-profile-table",
      "document-token-extraction-buckets",
      "d3-er-schema",
      "d3-kanban-board",
      "kanban-assignee-board",
      "kanban-assignee-virtual-legend",
      "kanban-assignee-distributed-legend",
      "calendar",
      "calendar-year",
      "waffle",
      "context-window-matrix",
      "attention-matrix-tiles",
      "flashattention-blocks",
      "matmul-tile-accumulation",
      "scaled-dot-product-attention",
      "multi-head-attention-merge",
      "paged-kv-cache",
      "tile-choropleth",
      "facets",
      "scatterplot-matrix",
      "bivariate-choropleth",
      "projection-comparison",
      "sized-donut-multiples",
      "correlogram-histogram",
      "rectbin-density",
      "hierarchical-bars",
      "stacked-grouped-bars",
      "dot-plot",
      "lollipop",
      "bar-race",
      "marimekko"
    )) {
      add("thirds-fifths-grid", kind === "table" ? "table" : "matrix", "the information is modular, so rows, columns, and repeated panels carry the message better than a free layout");
    }

    if (is(
      "radial-hierarchy",
      "sunburst",
      "chord",
      "directed-chord",
      "circular-bar",
      "radar",
      "polar-area",
      "token-roulette-sampler",
      "rope-position-rotation",
      "radial-stacked-bars",
      "polar-clock",
      "moon-phases",
      "radial-area",
      "burtin-antibiotics",
      "exoplanet-orbits",
      "epicyclic-gearing",
      "orthographic-shading",
      "solar-terminator",
      "solar-path"
    )) {
      add("radial-rosette", has(/hierarchy|sunburst/) ? "hierarchy" : "radial", "the base pattern has a real center, cycle, orbit, or spoke relationship");
    }
    if (is("embedding-neighborhood", "cluster-hulls", "force-network", "temporal-network")) {
      add("radial-rosette", "network", "a hub-and-neighborhood story can use rings to separate core, peers, and outliers");
    }

    if (is(
      "sankey",
      "alluvial",
      "parallel-sets",
      "d3-flowchart-dag",
      "d3-sequence-lifelines",
      "d3-state-machine",
      "d3-gantt-rollout",
      "d3-git-graph",
      "d3-user-journey",
      "flow-tokens",
      "token-boxes-to-context-window",
      "token-probability-sampler",
      "temperature-softmax",
      "nucleus-sampling",
      "attention-routing",
      "attention-arc-decoding",
      "qkv-projection-flow",
      "moe-router-capacity",
      "speculative-decoding-verify",
      "scaled-dot-product-attention",
      "multi-head-attention-merge",
      "residual-rmsnorm-stream",
      "swiglu-feed-forward",
      "kv-cache-growth",
      "paged-kv-cache",
      "web-load-timeline",
      "event-cascade",
      "critical-path",
      "mlp-simple",
      "deep-learning-model-execution",
      "mlp-internals",
      "binary-classifier",
      "binary-classifier-labeled"
    )) {
      add("flow-spine", "flow", "the marks describe a source-to-transform-to-output chain, so branches should return to a readable spine");
    }

    if (is(
      "asymmetric-task-overlap-saturated",
      "bubble-scatter",
      "point-cloud",
      "contours",
      "hexbin",
      "embedding-neighborhood",
      "dorling",
      "quadtree-search",
      "geofence-join",
      "isoline-terrain",
      "pen-label-optimizer",
      "word-cloud",
      "voronoi-stippling",
      "pocket-monster-stippling",
      "tissot-indicatrix",
      "star-map",
      "spike-map",
      "bubble-map",
      "volcano-contours",
      "hr-diagram",
      "hexbin-map",
      "airports-voronoi",
      "occlusion-labels",
      "non-contiguous-cartogram",
      "tile-choropleth",
      "parallel-coordinates",
      "scatterplot-tour"
    )) {
      add("dense-label-lanes", "lanes", "the composition problem is mark density, so labels and callouts need external lanes without moving the data field");
    }
  }

  function reviewPatternForComposition(source) {
    const kind = inferPatternKind(source);
    const id = source.id;
    const family = source.kicker || kind;
    const targets = [];
    const add = (compositionId, renderer = kind, reason = "") => {
      if (!targets.some(target => target.compositionId === compositionId)) {
        targets.push(targetSpec(compositionId, source, renderer, reason));
      }
    };

    addNarrativeTargets(source, kind, add);
    const usefulTargets = targets.slice(0, /force-network|sankey|radial-hierarchy|asymmetric-task-overlap|airports-voronoi|token-boxes-to-context-window|gemma-comparison/.test(id) ? 3 : 2);
    return {
      sourceId: id,
      patternId: source.patternId || `d3-pattern-${id}`,
      title: sourceTitle(source),
      family,
      kind,
      reviewed: true,
      rejectedReason: usefulTargets.length ? "" : "No published composition target improved the base pattern narrative without distorting the data marks.",
      targets: usefulTargets
    };
  }

  function mergeGeneratedVariants(reviews) {
    const generatedVariants = [];
    const byId = new Map();
    reviews.forEach(review => {
      review.targets.forEach(target => {
        const id = `d3-composition-${target.compositionId}-${review.sourceId}`;
        if (semanticVariantExclusions.has(id)) return;
        const generated = {
          id,
          compositionId: target.compositionId,
          sourceId: review.sourceId,
          kind: target.renderer,
          renderer: target.renderer,
          variantTitle: target.variantTitle,
          recipe: target.recipe,
          reason: target.reason,
          sourceFamily: review.family,
          inferredKind: review.kind,
          armatureLines: target.armatureLines,
          quadrants: target.quadrants,
          reviewed: true
        };
        if (byId.has(id)) {
          Object.assign(byId.get(id), generated);
        } else {
          generatedVariants.push(generated);
          byId.set(id, generated);
        }
      });
    });
    variants.length = 0;
    variants.push(...generatedVariants);
    variants.sort((a, b) => {
      const sheetOrder = sheets.findIndex(sheet => sheet.id === a.compositionId) - sheets.findIndex(sheet => sheet.id === b.compositionId);
      return sheetOrder || a.sourceId.localeCompare(b.sourceId);
    });
  }

  function el(name, attrs = {}, children = []) {
    const node = document.createElementNS(SVG_NS, name);
    for (const [key, value] of Object.entries(attrs)) {
      if (value !== undefined && value !== null) node.setAttribute(key, String(value));
    }
    for (const child of children) node.appendChild(child);
    return node;
  }

  function textNode(value) {
    return document.createTextNode(value);
  }

  function appendText(parent, x, y, value, attrs = {}) {
    const node = el("text", { x, y, ...attrs });
    node.appendChild(textNode(value));
    parent.appendChild(node);
    return node;
  }

  function addLine(parent, x1, y1, x2, y2, attrs = {}) {
    return parent.appendChild(el("line", { x1, y1, x2, y2, ...attrs }));
  }

  function addCircle(parent, cx, cy, r, attrs = {}) {
    return parent.appendChild(el("circle", { cx, cy, r, ...attrs }));
  }

  function addRect(parent, x, y, width, height, attrs = {}) {
    return parent.appendChild(el("rect", { x, y, width, height, ...attrs }));
  }

  function addPath(parent, d, attrs = {}) {
    return parent.appendChild(el("path", { d, ...attrs }));
  }

  function cssEscape(value) {
    if (window.CSS && typeof window.CSS.escape === "function") return window.CSS.escape(String(value));
    return String(value).replace(/[^a-zA-Z0-9_-]/g, "\\$&");
  }

  function parseViewBox(value) {
    const parts = String(value || "").trim().split(/[\s,]+/).map(Number);
    if (parts.length !== 4 || parts.some(part => !Number.isFinite(part))) return [0, 0, 560, 420];
    return parts;
  }

  function sourceSvgForVariant(variant) {
    return document.querySelector(`.source-gallery-cache svg#${cssEscape(variant.sourceId)}`);
  }

  function compositionSourceFrame(compositionId) {
    const frames = {
      "balance-symmetry": { x: 36, y: 34, width: 288, height: 150, rotate: 0 },
      "diagonal-armature": { x: 48, y: 42, width: 264, height: 134, rotate: -8 },
      "golden-root": { x: 36, y: 38, width: 188, height: 132, rotate: 0 },
      "thirds-fifths-grid": { x: 42, y: 38, width: 276, height: 136, rotate: 0 },
      "radial-rosette": { x: 58, y: 26, width: 244, height: 168, rotate: 0 },
      "flow-spine": { x: 38, y: 48, width: 284, height: 124, rotate: 0 },
      "dense-label-lanes": { x: 104, y: 34, width: 152, height: 150, rotate: 0 }
    };
    return frames[compositionId] || frames["balance-symmetry"];
  }

  function prefixClonedIds(root, prefix) {
    const idMap = new Map();
    root.querySelectorAll("[id]").forEach(node => {
      const oldId = node.getAttribute("id");
      const nextId = `${prefix}-${oldId}`;
      idMap.set(oldId, nextId);
      node.setAttribute("id", nextId);
    });
    const attrs = ["href", "xlink:href", "clip-path", "mask", "filter", "fill", "stroke", "marker-start", "marker-mid", "marker-end"];
    root.querySelectorAll("*").forEach(node => {
      attrs.forEach(attr => {
        const value = node.getAttribute(attr);
        if (!value) return;
        let next = value.replace(/url\(#([^)]+)\)/g, (match, id) => `url(#${idMap.get(id) || id})`);
        if (next.startsWith("#")) {
          const id = next.slice(1);
          next = `#${idMap.get(id) || id}`;
        }
        if (next !== value) node.setAttribute(attr, next);
      });
    });
  }

  function removeRuntimeAnimation(root) {
    root.querySelectorAll("animate, animateMotion, animateTransform, script").forEach(node => node.remove());
    root.querySelectorAll("[opacity='0']").forEach(node => {
      if (!node.querySelector("animate, animateMotion, animateTransform")) node.setAttribute("opacity", "1");
    });
  }

  function clamp(value, min, max) {
    return Math.max(min, Math.min(max, value));
  }

  function numericAttr(node, attr, fallback = 0) {
    const value = Number(node.getAttribute(attr));
    return Number.isFinite(value) ? value : fallback;
  }

  function renderedPaint(node, attr, fallback) {
    const direct = node.getAttribute(attr);
    if (direct && direct !== "none" && !direct.startsWith("url(")) return direct;
    const style = window.getComputedStyle ? window.getComputedStyle(node) : null;
    const computed = style ? style.getPropertyValue(attr) : "";
    if (computed && computed !== "none" && computed !== "rgba(0, 0, 0, 0)") return computed;
    return fallback;
  }

  function pointInSourceSvg(sourceSvg, node, x, y) {
    const point = sourceSvg.createSVGPoint ? sourceSvg.createSVGPoint() : new DOMPoint(x, y);
    point.x = x;
    point.y = y;
    try {
      const sourceMatrix = sourceSvg.getScreenCTM && sourceSvg.getScreenCTM();
      const nodeMatrix = node.getScreenCTM && node.getScreenCTM();
      if (sourceMatrix && nodeMatrix) {
        return point.matrixTransform(sourceMatrix.inverse().multiply(nodeMatrix));
      }
    } catch (_) {
      // Fall back to local SVG coordinates below.
    }
    try {
      const matrix = node.getCTM && node.getCTM();
      if (matrix) return point.matrixTransform(matrix);
    } catch (_) {
      // Keep the untransformed point when the browser cannot resolve matrices.
    }
    return { x, y };
  }

  function elementCenterInSource(sourceSvg, node) {
    try {
      const box = node.getBBox();
      const center = pointInSourceSvg(sourceSvg, node, box.x + box.width / 2, box.y + box.height / 2);
      const edge = pointInSourceSvg(sourceSvg, node, box.x + box.width, box.y + box.height / 2);
      const radius = Math.hypot(edge.x - center.x, edge.y - center.y);
      return { x: center.x, y: center.y, r: radius, width: box.width, height: box.height };
    } catch (_) {
      const cx = numericAttr(node, "cx", 0);
      const cy = numericAttr(node, "cy", 0);
      return { x: cx, y: cy, r: numericAttr(node, "r", 3), width: 0, height: 0 };
    }
  }

  function circleLabel(circle) {
    const parent = circle.parentElement;
    const scoped = parent ? parent.querySelector("text") : null;
    const value = scoped?.textContent?.trim() || "";
    if (!value || value.length > 18) return "";
    return value;
  }

  function nodeBounds(nodes) {
    const xs = nodes.map(node => node.x);
    const ys = nodes.map(node => node.y);
    const minX = Math.min(...xs);
    const maxX = Math.max(...xs);
    const minY = Math.min(...ys);
    const maxY = Math.max(...ys);
    return {
      minX,
      maxX,
      minY,
      maxY,
      width: Math.max(1, maxX - minX),
      height: Math.max(1, maxY - minY),
      cx: (minX + maxX) / 2,
      cy: (minY + maxY) / 2
    };
  }

  function nearestSourceNode(nodes, point, maxDistance) {
    let best = -1;
    let bestDistance = Infinity;
    nodes.forEach((node, index) => {
      const distance = Math.hypot(node.x - point.x, node.y - point.y);
      if (distance < bestDistance) {
        best = index;
        bestDistance = distance;
      }
    });
    return bestDistance <= maxDistance ? best : -1;
  }

  function addUniqueEdge(edges, seen, a, b, attrs = {}) {
    if (a < 0 || b < 0 || a === b) return;
    const key = a < b ? `${a}:${b}` : `${b}:${a}`;
    if (seen.has(key)) return;
    seen.add(key);
    edges.push({ source: a, target: b, ...attrs });
  }

  function extractPathEndpoint(sourceSvg, path, atEnd) {
    try {
      const length = path.getTotalLength();
      if (!Number.isFinite(length) || length <= 0) return null;
      const point = path.getPointAtLength(atEnd ? length : 0);
      return pointInSourceSvg(sourceSvg, path, point.x, point.y);
    } catch (_) {
      const numbers = String(path.getAttribute("d") || "").match(/-?\d*\.?\d+(?:e[-+]?\d+)?/gi);
      if (!numbers || numbers.length < 4) return null;
      const index = atEnd ? numbers.length - 2 : 0;
      return pointInSourceSvg(sourceSvg, path, Number(numbers[index]), Number(numbers[index + 1]));
    }
  }

  function sourceCircleNodes(sourceSvg) {
    const circles = Array.from(sourceSvg.querySelectorAll("circle"));
    const nodes = circles.map((circle, index) => {
      const center = elementCenterInSource(sourceSvg, circle);
      const directRadius = numericAttr(circle, "r", center.r || 0);
      const radius = Math.max(center.r || 0, directRadius);
      return {
        index,
        x: center.x,
        y: center.y,
        sourceR: radius,
        fill: renderedPaint(circle, "fill", palette.blue),
        stroke: renderedPaint(circle, "stroke", palette.surface),
        strokeWidth: numericAttr(circle, "stroke-width", 1.4),
        opacity: circle.getAttribute("opacity") || circle.style.opacity || "1",
        label: circleLabel(circle),
        className: circle.getAttribute("class") || ""
      };
    }).filter(node => Number.isFinite(node.x) && Number.isFinite(node.y) && node.sourceR >= 2.2);
    return nodes;
  }

  function sourceTextNodes(sourceSvg) {
    const labels = Array.from(sourceSvg.querySelectorAll("text"));
    return labels.map((label, index) => {
      const value = label.textContent?.trim() || "";
      if (!value || value.length > 18) return null;
      const center = elementCenterInSource(sourceSvg, label);
      return {
        index,
        x: center.x,
        y: center.y,
        sourceR: Math.max(3, Math.min(7, Math.max(center.width, center.height) / 5)),
        fill: palette.surface,
        stroke: renderedPaint(label, "fill", palette.purple),
        strokeWidth: 1.4,
        opacity: label.getAttribute("opacity") || label.style.opacity || "1",
        label: value,
        className: label.getAttribute("class") || ""
      };
    }).filter(Boolean).filter(node => Number.isFinite(node.x) && Number.isFinite(node.y));
  }

  function sourceLineEdges(sourceSvg, nodes) {
    const edges = [];
    const seen = new Set();
    const bounds = nodeBounds(nodes);
    const maxDistance = Math.max(bounds.width, bounds.height) * 0.12 + 12;
    Array.from(sourceSvg.querySelectorAll("line")).forEach(line => {
      const start = pointInSourceSvg(sourceSvg, line, numericAttr(line, "x1"), numericAttr(line, "y1"));
      const end = pointInSourceSvg(sourceSvg, line, numericAttr(line, "x2"), numericAttr(line, "y2"));
      const a = nearestSourceNode(nodes, start, maxDistance);
      const b = nearestSourceNode(nodes, end, maxDistance);
      addUniqueEdge(edges, seen, a, b, {
        mark: "line",
        stroke: renderedPaint(line, "stroke", palette.line),
        strokeWidth: numericAttr(line, "stroke-width", 1.4),
        opacity: line.getAttribute("stroke-opacity") || line.getAttribute("opacity") || "0.64"
      });
    });
    Array.from(sourceSvg.querySelectorAll("path")).forEach(path => {
      const d = String(path.getAttribute("d") || "");
      if (!d || /z\s*$/i.test(d)) return;
      const start = extractPathEndpoint(sourceSvg, path, false);
      const end = extractPathEndpoint(sourceSvg, path, true);
      if (!start || !end || Math.hypot(start.x - end.x, start.y - end.y) < 1) return;
      const a = nearestSourceNode(nodes, start, maxDistance);
      const b = nearestSourceNode(nodes, end, maxDistance);
      addUniqueEdge(edges, seen, a, b, {
        mark: "path",
        stroke: renderedPaint(path, "stroke", palette.line),
        strokeWidth: numericAttr(path, "stroke-width", 1.2),
        opacity: path.getAttribute("stroke-opacity") || path.getAttribute("opacity") || "0.46"
      });
    });
    return { edges, seen };
  }

  function fallbackNetworkEdges(nodes, seen = new Set()) {
    const edges = [];
    const neighborCount = nodes.length > 34 ? 2 : 3;
    nodes.forEach((node, index) => {
      const candidates = nodes
        .map((other, otherIndex) => {
          const colorPenalty = node.fill === other.fill ? 0 : 3200;
          return { index: otherIndex, distance: Math.hypot(node.x - other.x, node.y - other.y) + colorPenalty };
        })
        .filter(candidate => candidate.index !== index)
        .sort((a, b) => a.distance - b.distance)
        .slice(0, neighborCount);
      candidates.forEach(candidate => addUniqueEdge(edges, seen, index, candidate.index, {
        mark: "line",
        stroke: node.fill === nodes[candidate.index].fill ? node.fill : palette.line,
        strokeWidth: 1.1,
        opacity: node.fill === nodes[candidate.index].fill ? "0.28" : "0.2"
      }));
    });
    return edges;
  }

  function extractSourceNetwork(sourceSvg) {
    const circleNodes = sourceCircleNodes(sourceSvg);
    const nodes = circleNodes.length >= 5 ? circleNodes : sourceTextNodes(sourceSvg);
    if (nodes.length < 5) return null;
    const maxRadius = Math.max(...nodes.map(node => node.sourceR), 1);
    const bounds = nodeBounds(nodes);
    nodes.forEach((node, index) => {
      node.order = index;
      node.normX = (node.x - bounds.minX) / bounds.width;
      node.normY = (node.y - bounds.minY) / bounds.height;
      node.angle = Math.atan2(node.y - bounds.cy, node.x - bounds.cx);
      node.previewR = clamp(2.9 + (node.sourceR / maxRadius) * (nodes.length > 24 ? 3.1 : 5.4), 2.9, nodes.length > 24 ? 6 : 8.4);
    });
    const extracted = sourceLineEdges(sourceSvg, nodes);
    const minimumEdgeCount = Math.min(nodes.length - 1, 8);
    const fallback = extracted.edges.length >= minimumEdgeCount ? [] : fallbackNetworkEdges(nodes, extracted.seen);
    const edges = extracted.edges.concat(fallback).slice(0, nodes.length > 42 ? 88 : 72);
    const degree = new Map(nodes.map((_, index) => [index, 0]));
    edges.forEach(edge => {
      degree.set(edge.source, (degree.get(edge.source) || 0) + 1);
      degree.set(edge.target, (degree.get(edge.target) || 0) + 1);
    });
    nodes.forEach((node, index) => {
      node.degree = degree.get(index) || 0;
    });
    return { nodes, edges, bounds };
  }

  function semanticNetworkLayout(graph, variant) {
    const nodes = graph.nodes.map(node => ({ ...node }));
    if (variant.compositionId === "diagonal-armature") return diagonalNetworkLayout(nodes, variant);
    if (variant.compositionId === "radial-rosette") return radialNetworkLayout(nodes, graph.edges, variant);
    return balancedNetworkLayout(nodes, variant);
  }

  function balancedNetworkLayout(nodes, variant) {
    const byDegree = [...nodes].sort((a, b) => b.degree - a.degree || a.order - b.order);
    const centerCount = nodes.length > 24 ? 3 : nodes.length > 10 ? 2 : 1;
    const centerIds = new Set(byDegree.slice(0, centerCount).map(node => node.index));
    const remaining = nodes.filter(node => !centerIds.has(node.index)).sort((a, b) => a.normX - b.normX || a.normY - b.normY);
    const left = [];
    const right = [];
    remaining.forEach((node, index) => {
      if (left.length <= right.length) left.push(node);
      else right.push(node);
      if (index % 2 === 1 && left.length !== right.length) {
        const source = left.length > right.length ? left : right;
        const target = left.length > right.length ? right : left;
        target.push(source.pop());
      }
    });
    const placeSide = (items, side) => {
      items.sort((a, b) => a.normY - b.normY || a.normX - b.normX).forEach((node, index) => {
        const t = (index + 0.5) / Math.max(items.length, 1);
        const bow = Math.sin(t * Math.PI);
        const jitter = seededRange(variant, node.order + (side < 0 ? 100 : 200), -5, 5);
        node.x = 180 + side * (48 + bow * 34) + jitter;
        node.y = 52 + t * 116 + seededRange(variant, node.order + 300, -3, 3);
      });
    };
    placeSide(left, -1);
    placeSide(right, 1);
    byDegree.slice(0, centerCount).forEach((node, index) => {
      const target = nodes.find(item => item.index === node.index);
      const offset = (index - (centerCount - 1) / 2) * 16;
      target.x = 180;
      target.y = 110 + offset;
      target.previewR = Math.min(10, target.previewR + 2);
    });
    return nodes;
  }

  function diagonalNetworkLayout(nodes, variant) {
    const sorted = [...nodes].sort((a, b) => (a.normX + (1 - a.normY)) - (b.normX + (1 - b.normY)) || a.order - b.order);
    const start = { x: 58, y: 170 };
    const end = { x: 306, y: 48 };
    const dx = end.x - start.x;
    const dy = end.y - start.y;
    const length = Math.hypot(dx, dy);
    const normal = { x: -dy / length, y: dx / length };
    sorted.forEach((node, rank) => {
      const t = (rank + 0.5) / Math.max(sorted.length, 1);
      const spread = nodes.length > 26 ? 24 : 38;
      const sourceOffset = (node.normY - 0.5) * spread + seededRange(variant, node.order + 400, -4, 4);
      node.x = start.x + dx * t + normal.x * sourceOffset;
      node.y = start.y + dy * t + normal.y * sourceOffset;
      if (rank === 0 || rank === sorted.length - 1) node.previewR = Math.min(9.5, node.previewR + 1.7);
    });
    return nodes;
  }

  function radialNetworkLayout(nodes, edges, variant) {
    const hub = [...nodes].sort((a, b) => b.degree - a.degree || a.order - b.order)[0] || nodes[0];
    const hubId = hub.index;
    const neighbors = new Set();
    edges.forEach(edge => {
      if (edge.source === hubId) neighbors.add(edge.target);
      if (edge.target === hubId) neighbors.add(edge.source);
    });
    const orbit = nodes.filter(node => node.index !== hubId).sort((a, b) => a.angle - b.angle || a.order - b.order);
    orbit.forEach((node, rank) => {
      const angle = -Math.PI / 2 + (Math.PI * 2 * rank) / Math.max(orbit.length, 1);
      const ring = neighbors.has(node.index)
        ? (nodes.length > 24 ? 44 : 48)
        : (nodes.length > 24 ? 76 - (rank % 2) * 13 : 74);
      const jitter = seededRange(variant, node.order + 500, -3, 3);
      node.x = 180 + Math.cos(angle + jitter * 0.01) * ring;
      node.y = 110 + Math.sin(angle + jitter * 0.01) * ring;
    });
    const center = nodes.find(node => node.index === hubId);
    center.x = 180;
    center.y = 110;
    center.previewR = Math.min(11, center.previewR + 2.6);
    return nodes;
  }

  function semanticEdgePath(a, b, compositionId, index) {
    if (compositionId !== "radial-rosette") return "";
    const mx = (a.x + b.x) / 2;
    const my = (a.y + b.y) / 2;
    const pull = index % 2 ? 0.18 : -0.14;
    const cx = mx + (180 - mx) * pull;
    const cy = my + (110 - my) * pull;
    return `M${a.x.toFixed(2)} ${a.y.toFixed(2)} Q${cx.toFixed(2)} ${cy.toFixed(2)} ${b.x.toFixed(2)} ${b.y.toFixed(2)}`;
  }

  function semanticNetworkLabelPosition(node, index, compositionId) {
    if (compositionId === "diagonal-armature") {
      const normal = { x: 0.441, y: 0.897 };
      const direction = index % 2 ? -1 : 1;
      const x = clamp(node.x + normal.x * direction * 19, 52, 308);
      return {
        x,
        y: clamp(node.y + normal.y * direction * 19 + 3, 36, 186),
        anchor: x < 70 ? "start" : x > 290 ? "end" : "middle"
      };
    }
    if (compositionId === "radial-rosette") {
      const dx = node.x - 180;
      const dy = node.y - 110;
      const distance = Math.hypot(dx, dy);
      if (distance < 10) {
        return { x: node.x, y: node.y + node.previewR + 14, anchor: "middle" };
      }
      const ux = dx / distance;
      const uy = dy / distance;
      return {
        x: clamp(node.x + ux * (node.previewR + 8), 36, 324),
        y: clamp(node.y + uy * (node.previewR + 8) + 3, 36, 186),
        anchor: ux < -0.24 ? "end" : ux > 0.24 ? "start" : "middle"
      };
    }
    if (Math.abs(node.x - 180) < 12) {
      return { x: node.x, y: node.y + node.previewR + 13, anchor: "middle" };
    }
    const side = node.x < 180 ? -1 : 1;
    return {
      x: clamp(node.x + side * (node.previewR + 6), 42, 318),
      y: clamp(node.y + 3, 44, 178),
      anchor: side < 0 ? "end" : "start"
    };
  }

  function renderSemanticNetworkVariant(svg, variant) {
    if (variant.renderer !== "network" && variant.inferredKind !== "network") return false;
    if (!["balance-symmetry", "diagonal-armature", "radial-rosette"].includes(variant.compositionId)) return false;
    const sourceSvg = sourceSvgForVariant(variant);
    if (!sourceSvg) return false;
    const graph = extractSourceNetwork(sourceSvg);
    if (!graph) return false;
    const frame = compositionSourceFrame(variant.compositionId);
    const layout = semanticNetworkLayout(graph, variant);
    const byIndex = new Map(layout.map(node => [node.index, node]));
    addSourceField(svg, frame, variant.compositionId);
    const group = svg.appendChild(el("g", {
      class: "source-pattern-recomposition semantic-network-recomposition",
      "data-source-svg-id": variant.sourceId,
      "data-source-view-box": sourceSvg.getAttribute("viewBox") || "",
      "data-recomposition-mode": `semantic-network-${variant.compositionId}`,
      "data-source-node-count": graph.nodes.length,
      "data-source-edge-count": graph.edges.length
    }));
    const edges = group.appendChild(el("g", { class: "semantic-network-links", fill: "none", "stroke-linecap": "round" }));
    graph.edges.forEach((edge, index) => {
      const a = byIndex.get(edge.source);
      const b = byIndex.get(edge.target);
      if (!a || !b) return;
      const attrs = {
        class: "semantic-network-link",
        stroke: edge.stroke || palette.line,
        "stroke-width": clamp(edge.strokeWidth || 1.2, 0.8, graph.nodes.length > 28 ? 1.45 : 2.2),
        "stroke-opacity": edge.opacity || "0.54"
      };
      const path = edge.mark === "path" ? semanticEdgePath(a, b, variant.compositionId, index) : "";
      if (path) addPath(edges, path, attrs);
      else addLine(edges, a.x, a.y, b.x, b.y, attrs);
    });
    const marks = group.appendChild(el("g", { class: "semantic-network-nodes" }));
    layout.forEach(node => {
      addCircle(marks, node.x, node.y, node.previewR, {
        class: `semantic-network-node ${node.className}`.trim(),
        fill: node.fill,
        "fill-opacity": clamp(Number(node.opacity) || 1, 0.35, 1),
        stroke: node.stroke || palette.surface,
        "stroke-width": clamp(node.strokeWidth || 1.4, 1, 2.2),
        "data-source-node-index": node.index,
        "data-source-label": node.label || undefined
      });
    });
    const labeled = layout.filter(node => node.label);
    if (labeled.length && labeled.length <= 14) {
      const labels = group.appendChild(el("g", { class: "semantic-network-labels" }));
      labeled.forEach((node, index) => {
        const label = semanticNetworkLabelPosition(node, index, variant.compositionId);
        appendText(labels, label.x, label.y, node.label, {
          class: "semantic-network-label",
          "text-anchor": label.anchor,
          "font-size": 7.3,
          "font-weight": 800,
          fill: palette.ink,
          stroke: palette.surface,
          "stroke-width": 2.4,
          "paint-order": "stroke",
          "stroke-linejoin": "round"
        });
      });
    }
    return true;
  }

  function visibleTextMarks(sourceSvg, limit = 18) {
    return Array.from(sourceSvg.querySelectorAll("text"))
      .map((label, index) => {
        const value = label.textContent?.trim() || "";
        if (!value || value.length > 22) return null;
        const center = elementCenterInSource(sourceSvg, label);
        return {
          index,
          x: center.x,
          y: center.y,
          text: value,
          fill: renderedPaint(label, "fill", palette.ink),
          className: label.getAttribute("class") || ""
        };
      })
      .filter(Boolean)
      .filter(mark => Number.isFinite(mark.x) && Number.isFinite(mark.y))
      .slice(0, limit);
  }

  function sourceRectMarks(sourceSvg, limit = 120) {
    const [vx, vy, vw, vh] = parseViewBox(sourceSvg.getAttribute("viewBox"));
    const frameArea = vw * vh;
    return Array.from(sourceSvg.querySelectorAll("rect"))
      .map((rect, index) => {
        const box = elementCenterInSource(sourceSvg, rect);
        const width = Math.max(box.width || numericAttr(rect, "width", 0), 0);
        const height = Math.max(box.height || numericAttr(rect, "height", 0), 0);
        const area = width * height;
        if (width < 2 || height < 2 || area > frameArea * 0.82) return null;
        return {
          index,
          x: box.x,
          y: box.y,
          width,
          height,
          area,
          fill: renderedPaint(rect, "fill", palette.blueHighlight),
          stroke: renderedPaint(rect, "stroke", "none"),
          opacity: rect.getAttribute("fill-opacity") || rect.getAttribute("opacity") || "1",
          rx: numericAttr(rect, "rx", 1.5)
        };
      })
      .filter(Boolean)
      .sort((a, b) => b.area - a.area)
      .slice(0, limit)
      .sort((a, b) => a.y - b.y || a.x - b.x);
  }

  function sourceCircleLikeMarks(sourceSvg, limit = 36) {
    const circles = Array.from(sourceSvg.querySelectorAll("circle,ellipse"))
      .map((mark, index) => {
        const center = elementCenterInSource(sourceSvg, mark);
        const tag = mark.tagName.toLowerCase();
        const rx = tag === "ellipse" ? numericAttr(mark, "rx", center.r || 4) : numericAttr(mark, "r", center.r || 4);
        const ry = tag === "ellipse" ? numericAttr(mark, "ry", center.r || 4) : rx;
        return {
          index,
          x: center.x,
          y: center.y,
          rx: Math.max(rx, center.r || 0),
          ry: Math.max(ry, center.r || 0),
          radius: Math.max(rx, ry, center.r || 0),
          fill: renderedPaint(mark, "fill", palette.blueHighlight),
          stroke: renderedPaint(mark, "stroke", palette.blue),
          opacity: mark.getAttribute("fill-opacity") || mark.getAttribute("opacity") || "0.72",
          strokeWidth: numericAttr(mark, "stroke-width", 1.3)
        };
      })
      .filter(mark => Number.isFinite(mark.x) && Number.isFinite(mark.y) && mark.radius > 2);
    return circles.sort((a, b) => b.radius - a.radius).slice(0, limit).sort((a, b) => a.index - b.index);
  }

  function sourcePathMarks(sourceSvg, limit = 36) {
    const pathMarks = Array.from(sourceSvg.querySelectorAll("path,line,polyline,polygon"))
      .map((mark, index) => {
        const tag = mark.tagName.toLowerCase();
        const center = elementCenterInSource(sourceSvg, mark);
        const stroke = renderedPaint(mark, "stroke", palette.blue);
        const fill = renderedPaint(mark, "fill", "none");
        const strokeWidth = numericAttr(mark, "stroke-width", 1.5);
        if (tag === "path" && !String(mark.getAttribute("d") || "").trim()) return null;
        if (stroke === "none" && fill === "none") return null;
        return {
          index,
          tag,
          x: center.x,
          y: center.y,
          stroke,
          fill,
          strokeWidth,
          opacity: mark.getAttribute("stroke-opacity") || mark.getAttribute("opacity") || "0.58"
        };
      })
      .filter(Boolean);
    return pathMarks.slice(0, limit);
  }

  function fitRadius(mark, target) {
    return clamp(Math.sqrt(Math.max(mark.radius || mark.area || 16, 16)) * 0.62, target.min, target.max);
  }

  function renderSemanticSetOverlapVariant(svg, variant) {
    if (variant.renderer !== "set-overlap" && variant.inferredKind !== "set-overlap") return false;
    if (!["balance-symmetry", "radial-rosette"].includes(variant.compositionId)) return false;
    const sourceSvg = sourceSvgForVariant(variant);
    if (!sourceSvg) return false;
    const circles = sourceCircleLikeMarks(sourceSvg, 9).filter(mark => mark.radius > 14);
    if (circles.length < 3) return false;
    const frame = compositionSourceFrame(variant.compositionId);
    addSourceField(svg, frame, variant.compositionId);
    const group = svg.appendChild(el("g", {
      class: "source-pattern-recomposition semantic-set-recomposition",
      "data-source-svg-id": variant.sourceId,
      "data-recomposition-mode": `semantic-set-${variant.compositionId}`,
      "data-source-circle-count": circles.length
    }));
    const center = { x: 180, y: 110 };
    circles.forEach((circle, index) => {
      let x;
      let y;
      let r;
      if (variant.compositionId === "radial-rosette") {
        if (index === 0 && !/rosette|flower|five|seven|three|venn/.test(variant.sourceId)) {
          x = center.x;
          y = center.y;
          r = 42;
        } else {
          const petalIndex = index === 0 ? 0 : index - 1;
          const petals = Math.max(circles.length - 1, 3);
          const angle = -Math.PI / 2 + (Math.PI * 2 * petalIndex) / petals;
          x = center.x + Math.cos(angle) * 44;
          y = center.y + Math.sin(angle) * 44;
          r = clamp(31 + (circle.radius % 11), 28, 41);
        }
      } else {
        const positions = [
          [180, 110], [145, 88], [215, 88], [145, 132], [215, 132],
          [180, 76], [180, 144], [118, 110], [242, 110]
        ];
        [x, y] = positions[index % positions.length];
        r = clamp(30 + (circle.radius % 13), 26, 43);
      }
      addCircle(group, x, y, r, {
        class: "semantic-set-circle",
        fill: circle.fill,
        "fill-opacity": clamp(Number(circle.opacity) || 0.55, 0.18, 0.58),
        stroke: circle.stroke || palette.blue,
        "stroke-width": clamp(circle.strokeWidth || 1.4, 1, 2.4)
      });
    });
    visibleTextMarks(sourceSvg, 6).forEach((label, index) => {
      const x = index % 2 ? 250 : 110;
      const y = 56 + Math.floor(index / 2) * 24;
      appendText(group, x, y, label.text, {
        class: "semantic-set-label",
        "text-anchor": index % 2 ? "start" : "end",
        "font-size": 7.2,
        "font-weight": 800,
        fill: palette.ink,
        stroke: palette.surface,
        "stroke-width": 2.2,
        "paint-order": "stroke"
      });
    });
    return true;
  }

  function flowStations(compositionId, count) {
    const base = compositionId === "diagonal-armature"
      ? [[54, 168], [112, 143], [180, 110], [248, 76], [310, 48]]
      : [[44, 128], [112, 82], [180, 112], [248, 144], [316, 90]];
    if (count <= base.length) return base.slice(0, count);
    return Array.from({ length: count }, (_, index) => {
      const t = index / Math.max(count - 1, 1);
      if (compositionId === "diagonal-armature") return [54 + t * 256, 168 - t * 120];
      return [44 + t * 272, 112 + Math.sin(t * Math.PI * 2 - 0.6) * 30];
    });
  }

  function flowPathD(a, b, compositionId, offset = 0) {
    if (compositionId === "diagonal-armature") {
      return `M${a[0]} ${a[1] + offset} C${(a[0] + b[0]) / 2} ${a[1] + offset - 18}, ${(a[0] + b[0]) / 2} ${b[1] + offset + 18}, ${b[0]} ${b[1] + offset}`;
    }
    return `M${a[0]} ${a[1] + offset} C${(a[0] + b[0]) / 2} ${a[1] - 34 + offset}, ${(a[0] + b[0]) / 2} ${b[1] + 34 + offset}, ${b[0]} ${b[1] + offset}`;
  }

  function renderSemanticGeospatialDiagonalVariant(svg, variant) {
    if (variant.compositionId !== "diagonal-armature") return false;
    if (variant.renderer !== "route" && variant.inferredKind !== "geospatial") return false;
    const sourceSvg = sourceSvgForVariant(variant);
    if (!sourceSvg) return false;
    const marks = scatterSourceMarks(sourceSvg).slice(0, 64);
    if (marks.length < 4) return false;
    const frame = compositionSourceFrame(variant.compositionId);
    addSourceField(svg, frame, variant.compositionId);
    const group = svg.appendChild(el("g", {
      class: "source-pattern-recomposition semantic-geospatial-diagonal-recomposition",
      "data-source-svg-id": variant.sourceId,
      "data-recomposition-mode": "semantic-geospatial-diagonal",
      "data-source-mark-count": marks.length
    }));
    const start = { x: 48, y: 170 };
    const end = { x: 312, y: 46 };
    const dx = end.x - start.x;
    const dy = end.y - start.y;
    const length = Math.hypot(dx, dy);
    const normal = { x: -dy / length, y: dx / length };
    const layout = marks.map(mark => {
      const spatialT = clamp(mark.normX * 0.68 + (1 - mark.normY) * 0.32, 0, 1);
      const t = 0.05 + spatialT * 0.9;
      const offset = (mark.normY - 0.5) * (marks.length > 34 ? 42 : 58) + seededRange(variant, mark.order + 720, -3, 3);
      return {
        ...mark,
        distanceT: spatialT,
        x: start.x + dx * t + normal.x * offset,
        y: start.y + dy * t + normal.y * offset
      };
    });
    const ordered = [...layout].sort((a, b) => a.distanceT - b.distanceT || a.order - b.order);
    if (/route|tour|path|solar|satellite/.test(variant.sourceId)) {
      const d = ordered.map((mark, index) => `${index ? "L" : "M"}${mark.x.toFixed(1)} ${mark.y.toFixed(1)}`).join(" ");
      addPath(group, d, {
        class: "semantic-geo-route",
        fill: "none",
        stroke: palette.red,
        "stroke-width": 2.2,
        "stroke-opacity": 0.52,
        "stroke-linejoin": "round",
        "stroke-linecap": "round"
      });
    }
    layout.forEach(mark => {
      const radius = clamp((mark.size || mark.radius || 7) * 0.26, 2.8, marks.length > 34 ? 5.4 : 7.8);
      addCircle(group, mark.x, mark.y, radius, {
        class: "semantic-geo-mark",
        fill: mark.fill || mark.stroke || palette.blue,
        "fill-opacity": clamp(Number(mark.opacity) || 0.72, 0.34, 0.92),
        stroke: mark.stroke === "none" ? palette.surface : mark.stroke,
        "stroke-width": 1
      });
    });
    const labels = visibleTextMarks(sourceSvg, 8);
    const labelMarks = ordered.filter((_, index) => index % Math.max(1, Math.floor(ordered.length / 7)) === 0).slice(0, 7);
    labelMarks.forEach((mark, index) => {
      const label = labels[index]?.text || tokenLabel(variant, "place", index);
      const side = index % 2 ? -1 : 1;
      const lx = mark.x + normal.x * side * 24;
      const ly = mark.y + normal.y * side * 24;
      addLine(group, mark.x, mark.y, lx, ly, {
        class: "semantic-geo-label-leader",
        stroke: palette.blue,
        "stroke-width": 0.9,
        "stroke-opacity": 0.34
      });
      appendText(group, lx, ly + 2, label, {
        class: "semantic-geo-label",
        "text-anchor": side > 0 ? "start" : "end",
        "font-size": 6.8,
        "font-weight": 800,
        fill: palette.ink,
        stroke: palette.surface,
        "stroke-width": 2.2,
        "paint-order": "stroke"
      });
    });
    return true;
  }

  function renderSemanticFlowVariant(svg, variant) {
    if (!["flow", "route"].includes(variant.renderer) && !["flow", "geospatial", "geometry"].includes(variant.inferredKind)) return false;
    if (!["flow-spine", "diagonal-armature"].includes(variant.compositionId)) return false;
    const sourceSvg = sourceSvgForVariant(variant);
    if (!sourceSvg) return false;
    const paths = sourcePathMarks(sourceSvg, 18);
    const labels = visibleTextMarks(sourceSvg, 7);
    if (paths.length < 1 && labels.length < 3) return false;
    const frame = compositionSourceFrame(variant.compositionId);
    addSourceField(svg, frame, variant.compositionId);
    const group = svg.appendChild(el("g", {
      class: "source-pattern-recomposition semantic-flow-recomposition",
      "data-source-svg-id": variant.sourceId,
      "data-recomposition-mode": `semantic-flow-${variant.compositionId}`,
      "data-source-path-count": paths.length,
      "data-source-label-count": labels.length
    }));
    const stationCount = clamp(Math.max(labels.length, Math.min(paths.length + 1, 6), 4), 4, 7);
    const stations = flowStations(variant.compositionId, stationCount);
    const pathCount = Math.max(paths.length, stationCount - 1);
    for (let index = 0; index < pathCount; index += 1) {
      const sourcePath = paths[index % Math.max(paths.length, 1)] || {};
      const a = stations[index % (stationCount - 1)];
      const b = stations[(index % (stationCount - 1)) + 1];
      const offset = (index - (pathCount - 1) / 2) * (pathCount > 8 ? 1.8 : 3.2);
      addPath(group, flowPathD(a, b, variant.compositionId, offset), {
        class: "semantic-flow-link",
        fill: "none",
        stroke: sourcePath.stroke || sourcePath.fill || palette.blue,
        "stroke-width": clamp(sourcePath.strokeWidth || 2, 1.4, 7),
        "stroke-opacity": clamp(Number(sourcePath.opacity) || 0.52, 0.22, 0.72),
        "stroke-linecap": "round"
      });
    }
    stations.forEach((station, index) => {
      const sourcePath = paths[index % Math.max(paths.length, 1)] || {};
      addCircle(group, station[0], station[1], index === 0 || index === stations.length - 1 ? 8.5 : 6.2, {
        class: "semantic-flow-station",
        fill: palette.surface,
        stroke: sourcePath.stroke || palette.red,
        "stroke-width": 1.8
      });
      const label = labels[index]?.text || tokenLabel(variant, index === 0 ? "source" : "stage", index);
      appendText(group, station[0], station[1] + (variant.compositionId === "diagonal-armature" ? 22 : 28), label, {
        class: "semantic-flow-label",
        "text-anchor": "middle",
        "font-size": 7.1,
        "font-weight": 800,
        fill: palette.ink,
        stroke: palette.surface,
        "stroke-width": 2.2,
        "paint-order": "stroke"
      });
    });
    return true;
  }

  function gridCellGeometry(compositionId, index, total) {
    if (compositionId === "golden-root") {
      const cols = 8;
      const rows = Math.ceil(Math.min(total, 72) / cols);
      const cell = Math.min(17, 112 / Math.max(rows, 1));
      return {
        x: 46 + (index % cols) * cell,
        y: 48 + Math.floor(index / cols) * cell,
        width: cell - 3,
        height: cell - 3
      };
    }
    const cols = 12;
    const rows = Math.ceil(Math.min(total, 120) / cols);
    const cellW = 236 / cols;
    const cellH = Math.min(13, 124 / Math.max(rows, 1));
    return {
      x: 62 + (index % cols) * cellW,
      y: 44 + Math.floor(index / cols) * cellH,
      width: cellW - 2.2,
      height: cellH - 2.2
    };
  }

  function renderSemanticGridVariant(svg, variant) {
    if (!["matrix", "table", "bar", "document"].includes(variant.renderer)) return false;
    if (!["thirds-fifths-grid", "golden-root"].includes(variant.compositionId)) return false;
    const sourceSvg = sourceSvgForVariant(variant);
    if (!sourceSvg) return false;
    let rects = sourceRectMarks(sourceSvg, variant.compositionId === "golden-root" ? 72 : 120);
    if (rects.length < 6) {
      rects = sourcePathMarks(sourceSvg, variant.compositionId === "golden-root" ? 72 : 120).map((mark, index) => ({
        index,
        x: mark.x,
        y: mark.y,
        width: 8,
        height: 8,
        area: 64,
        fill: mark.fill && mark.fill !== "none" ? mark.fill : mark.stroke,
        stroke: mark.stroke,
        opacity: mark.opacity,
        rx: 1.5
      }));
    }
    if (rects.length < 6) {
      rects = visibleTextMarks(sourceSvg, 40).map((mark, index) => ({
        index,
        x: mark.x || index,
        y: mark.y || index,
        width: 18,
        height: 8,
        area: 144,
        fill: [palette.blueHighlight, palette.greenHighlight, palette.yellowHighlight, palette.purpleHighlight][index % 4],
        stroke: palette.softLine,
        opacity: "0.86",
        rx: 2
      }));
    }
    if (rects.length < 6) return false;
    const frame = compositionSourceFrame(variant.compositionId);
    addSourceField(svg, frame, variant.compositionId);
    const group = svg.appendChild(el("g", {
      class: "source-pattern-recomposition semantic-grid-recomposition",
      "data-source-svg-id": variant.sourceId,
      "data-recomposition-mode": `semantic-grid-${variant.compositionId}`,
      "data-source-rect-count": rects.length
    }));
    rects.forEach((rect, index) => {
      const cell = gridCellGeometry(variant.compositionId, index, rects.length);
      addRect(group, cell.x, cell.y, cell.width, cell.height, {
        class: "semantic-grid-cell",
        rx: Math.min(3, rect.rx || 1.5),
        fill: rect.fill,
        "fill-opacity": clamp(Number(rect.opacity) || 0.86, 0.22, 1),
        stroke: rect.stroke === "none" ? palette.surface : rect.stroke,
        "stroke-width": 0.7,
        "stroke-opacity": 0.72
      });
    });
    const labels = visibleTextMarks(sourceSvg, variant.compositionId === "golden-root" ? 4 : 6);
    if (variant.compositionId === "golden-root") {
      const contextRows = labels.length ? labels : Array.from({ length: 5 }, (_, index) => ({ text: tokenLabel(variant, "context", index) }));
      contextRows.slice(0, 5).forEach((label, index) => {
        const y = 58 + index * 24;
        addRect(group, 244, y - 10, 70, 16, { rx: 4, fill: palette.surface, stroke: palette.softLine });
        addRect(group, 292, y - 4, 8 + ((hashString(`${variant.sourceId}:${index}`) % 16)), 4, {
          rx: 2,
          fill: [palette.blue, palette.green, palette.orange, palette.purple, palette.red][index % 5],
          "fill-opacity": 0.58,
          stroke: "none"
        });
        appendText(group, 250, y + 1.5, label.text, { "font-size": 7, "font-weight": 800, fill: palette.ink });
      });
    } else {
      labels.slice(0, 4).forEach((label, index) => {
        appendText(group, 72 + index * 58, 33, label.text, { "font-size": 7, "font-weight": 800, fill: palette.muted });
      });
    }
    return true;
  }

  function renderSemanticLaneVariant(svg, variant) {
    if (!["lanes", "labels"].includes(variant.renderer) && variant.compositionId !== "dense-label-lanes") return false;
    if (variant.compositionId !== "dense-label-lanes") return false;
    const sourceSvg = sourceSvgForVariant(variant);
    if (!sourceSvg) return false;
    const circles = sourceCircleLikeMarks(sourceSvg, 70);
    const rects = sourceRectMarks(sourceSvg, 40);
    const paths = sourcePathMarks(sourceSvg, 70);
    const labels = visibleTextMarks(sourceSvg, 10);
    if (circles.length + rects.length + paths.length < 5 && labels.length < 4) return false;
    const frame = compositionSourceFrame(variant.compositionId);
    addSourceField(svg, frame, variant.compositionId);
    const group = svg.appendChild(el("g", {
      class: "source-pattern-recomposition semantic-lane-recomposition",
      "data-source-svg-id": variant.sourceId,
      "data-recomposition-mode": "semantic-lanes-dense-label-lanes",
      "data-source-mark-count": circles.length + rects.length + paths.length,
      "data-source-label-count": labels.length
    }));
    const sourceMarks = circles.length ? circles : rects.length ? rects : paths;
    const bounds = nodeBounds(sourceMarks.map(mark => ({ x: mark.x, y: mark.y })));
    circles.forEach((circle, index) => {
      const x = 118 + ((circle.x - bounds.minX) / bounds.width) * 124;
      const y = 50 + ((circle.y - bounds.minY) / bounds.height) * 118;
      addCircle(group, x, y, clamp(circle.radius * 0.18, 2.2, 6.5), {
        class: "semantic-lane-mark",
        fill: circle.fill,
        "fill-opacity": clamp(Number(circle.opacity) || 0.72, 0.3, 0.9),
        stroke: circle.stroke || palette.surface,
        "stroke-width": 0.8
      });
    });
    rects.slice(0, Math.max(0, 60 - circles.length)).forEach((rect, index) => {
      const x = 118 + ((rect.x - bounds.minX) / bounds.width) * 124;
      const y = 50 + ((rect.y - bounds.minY) / bounds.height) * 118;
      addRect(group, x - 2.2, y - 2.2, 4.4, 4.4, {
        class: "semantic-lane-mark",
        rx: 1,
        fill: rect.fill,
        "fill-opacity": clamp(Number(rect.opacity) || 0.7, 0.22, 0.9),
        stroke: "none"
      });
    });
    paths.slice(0, Math.max(0, 60 - circles.length - rects.length)).forEach((path, index) => {
      const x = 118 + ((path.x - bounds.minX) / bounds.width) * 124;
      const y = 50 + ((path.y - bounds.minY) / bounds.height) * 118;
      addCircle(group, x, y, 2.5, {
        class: "semantic-lane-mark",
        fill: path.fill && path.fill !== "none" ? path.fill : path.stroke || palette.blue,
        "fill-opacity": clamp(Number(path.opacity) || 0.62, 0.24, 0.82),
        stroke: "none"
      });
    });
    const laneLabels = labels.length ? labels : Array.from({ length: 8 }, (_, index) => ({ text: tokenLabel(variant, "label", index) }));
    laneLabels.slice(0, 10).forEach((label, index) => {
      const left = index % 2 === 0;
      const laneIndex = Math.floor(index / 2);
      const x = left ? 38 : 286;
      const y = 48 + laneIndex * 25;
      const targetX = 136 + (laneIndex % 3) * 34;
      const targetY = 58 + laneIndex * 24;
      addRect(group, x, y - 8, 46, 14, { rx: 4, fill: palette.surface, stroke: palette.softLine });
      appendText(group, left ? x + 6 : x + 40, y + 2, label.text, {
        "text-anchor": left ? "start" : "end",
        "font-size": 6.8,
        "font-weight": 800,
        fill: palette.ink
      });
      addLine(group, left ? x + 46 : x, y - 1, targetX, targetY, {
        class: "semantic-lane-leader",
        stroke: palette.blue,
        "stroke-width": 0.9,
        "stroke-opacity": 0.34
      });
    });
    return true;
  }

  function normalizedMarks(marks) {
    const bounds = nodeBounds(marks.map(mark => ({ x: mark.x, y: mark.y })));
    return marks.map((mark, index) => ({
      ...mark,
      order: index,
      normX: (mark.x - bounds.minX) / bounds.width,
      normY: (mark.y - bounds.minY) / bounds.height
    }));
  }

  function scatterSourceMarks(sourceSvg) {
    const circles = sourceCircleLikeMarks(sourceSvg, 90).map(mark => ({ ...mark, shape: "circle", size: mark.radius }));
    if (circles.length >= 5) return normalizedMarks(circles);
    const rects = sourceRectMarks(sourceSvg, 90).map(mark => ({ ...mark, shape: "rect", size: Math.sqrt(mark.area) }));
    if (rects.length >= 5) return normalizedMarks(rects);
    const paths = sourcePathMarks(sourceSvg, 44).map(mark => ({ ...mark, shape: "path", size: Math.max(4, mark.strokeWidth * 2) }));
    return paths.length >= 3 ? normalizedMarks(paths) : [];
  }

  function scatterLayout(mark, variant, count) {
    if (variant.compositionId === "diagonal-armature") {
      const t = (mark.order + 0.5) / Math.max(count, 1);
      const start = { x: 56, y: 170 };
      const end = { x: 306, y: 48 };
      const dx = end.x - start.x;
      const dy = end.y - start.y;
      const length = Math.hypot(dx, dy);
      const normal = { x: -dy / length, y: dx / length };
      const offset = (mark.normY - 0.5) * (count > 45 ? 34 : 52);
      return {
        x: start.x + dx * t + normal.x * offset,
        y: start.y + dy * t + normal.y * offset
      };
    }
    const side = mark.normX < 0.5 ? -1 : 1;
    const distance = 30 + Math.abs(mark.normX - 0.5) * 128;
    return {
      x: 180 + side * distance,
      y: 48 + mark.normY * 124
    };
  }

  function renderSemanticScatterVariant(svg, variant) {
    if (variant.renderer !== "scatter" && !(variant.inferredKind === "chart" && ["balance-symmetry", "diagonal-armature"].includes(variant.compositionId))) return false;
    if (!["balance-symmetry", "diagonal-armature"].includes(variant.compositionId)) return false;
    const sourceSvg = sourceSvgForVariant(variant);
    if (!sourceSvg) return false;
    const marks = scatterSourceMarks(sourceSvg).slice(0, 88);
    if (marks.length < 3) return false;
    const paths = sourcePathMarks(sourceSvg, 8);
    const frame = compositionSourceFrame(variant.compositionId);
    addSourceField(svg, frame, variant.compositionId);
    const group = svg.appendChild(el("g", {
      class: "source-pattern-recomposition semantic-scatter-recomposition",
      "data-source-svg-id": variant.sourceId,
      "data-recomposition-mode": `semantic-scatter-${variant.compositionId}`,
      "data-source-mark-count": marks.length
    }));
    const layout = marks.map(mark => ({ ...mark, ...scatterLayout(mark, variant, marks.length) }));
    if (/line|area|slope|connected|path|bump|moving|index|forecast|cursor|ecdf/.test(variant.sourceId)) {
      const ordered = [...layout].sort((a, b) => a.x - b.x);
      const d = ordered.map((mark, index) => `${index ? "L" : "M"}${mark.x.toFixed(1)} ${mark.y.toFixed(1)}`).join(" ");
      addPath(group, d, {
        class: "semantic-scatter-trajectory",
        fill: "none",
        stroke: paths[0]?.stroke || palette.blue,
        "stroke-width": clamp(paths[0]?.strokeWidth || 2, 1.2, 4),
        "stroke-opacity": 0.58,
        "stroke-linejoin": "round",
        "stroke-linecap": "round"
      });
    }
    layout.forEach(mark => {
      const radius = clamp((mark.size || 6) * 0.28, 2.4, marks.length > 45 ? 4.6 : 7.2);
      if (mark.shape === "rect") {
        addRect(group, mark.x - radius, mark.y - radius, radius * 2, radius * 2, {
          class: "semantic-scatter-mark",
          rx: 1.4,
          fill: mark.fill,
          "fill-opacity": clamp(Number(mark.opacity) || 0.76, 0.3, 0.94),
          stroke: mark.stroke === "none" ? palette.surface : mark.stroke,
          "stroke-width": 0.8
        });
      } else {
        addCircle(group, mark.x, mark.y, radius, {
          class: "semantic-scatter-mark",
          fill: mark.fill || mark.stroke || palette.blue,
          "fill-opacity": clamp(Number(mark.opacity) || 0.76, 0.32, 0.94),
          stroke: mark.stroke || palette.surface,
          "stroke-width": 0.9
        });
      }
    });
    visibleTextMarks(sourceSvg, 4).forEach((label, index) => {
      const x = variant.compositionId === "diagonal-armature" ? 72 + index * 68 : index % 2 ? 254 : 106;
      const y = variant.compositionId === "diagonal-armature" ? 184 - index * 36 : 54 + Math.floor(index / 2) * 108;
      appendText(group, x, y, label.text, {
        "text-anchor": "middle",
        "font-size": 7.2,
        "font-weight": 800,
        fill: palette.ink,
        stroke: palette.surface,
        "stroke-width": 2.2,
        "paint-order": "stroke"
      });
    });
    return true;
  }

  function arcPath(cx, cy, innerRadius, outerRadius, startAngle, endAngle) {
    const large = endAngle - startAngle > Math.PI ? 1 : 0;
    const p0 = [cx + Math.cos(startAngle) * outerRadius, cy + Math.sin(startAngle) * outerRadius];
    const p1 = [cx + Math.cos(endAngle) * outerRadius, cy + Math.sin(endAngle) * outerRadius];
    const p2 = [cx + Math.cos(endAngle) * innerRadius, cy + Math.sin(endAngle) * innerRadius];
    const p3 = [cx + Math.cos(startAngle) * innerRadius, cy + Math.sin(startAngle) * innerRadius];
    return `M${p0[0].toFixed(2)} ${p0[1].toFixed(2)} A${outerRadius} ${outerRadius} 0 ${large} 1 ${p1[0].toFixed(2)} ${p1[1].toFixed(2)} L${p2[0].toFixed(2)} ${p2[1].toFixed(2)} A${innerRadius} ${innerRadius} 0 ${large} 0 ${p3[0].toFixed(2)} ${p3[1].toFixed(2)} Z`;
  }

  function renderSemanticRadialVariant(svg, variant) {
    if (variant.renderer !== "radial") return false;
    if (!["radial-rosette", "balance-symmetry"].includes(variant.compositionId)) return false;
    const sourceSvg = sourceSvgForVariant(variant);
    if (!sourceSvg) return false;
    const paths = sourcePathMarks(sourceSvg, 28);
    const circles = sourceCircleLikeMarks(sourceSvg, 20);
    const marks = paths.length ? paths : circles;
    if (marks.length < 2) return false;
    const frame = compositionSourceFrame(variant.compositionId);
    addSourceField(svg, frame, variant.compositionId);
    const group = svg.appendChild(el("g", {
      class: "source-pattern-recomposition semantic-radial-recomposition",
      "data-source-svg-id": variant.sourceId,
      "data-recomposition-mode": `semantic-radial-${variant.compositionId}`,
      "data-source-radial-mark-count": marks.length
    }));
    const count = clamp(Math.max(marks.length, 6), 6, 18);
    for (let index = 0; index < count; index += 1) {
      const source = marks[index % marks.length];
      const start = -Math.PI / 2 + (Math.PI * 2 * index) / count;
      const end = -Math.PI / 2 + (Math.PI * 2 * (index + 0.82)) / count;
      const ring = index % 3;
      const inner = variant.compositionId === "balance-symmetry" ? 35 + ring * 16 : 31 + ring * 18;
      const outer = inner + 12 + (index % 2) * 4;
      addPath(group, arcPath(180, 110, inner, outer, start, end), {
        class: "semantic-radial-segment",
        fill: source.fill && source.fill !== "none" ? source.fill : source.stroke || palette.blue,
        "fill-opacity": clamp(Number(source.opacity) || 0.72, 0.34, 0.86),
        stroke: palette.surface,
        "stroke-width": 0.8
      });
    }
    addCircle(group, 180, 110, 16, {
      class: "semantic-radial-center",
      fill: circles[0]?.fill || palette.surface,
      stroke: paths[0]?.stroke || circles[0]?.stroke || palette.red,
      "stroke-width": 2
    });
    visibleTextMarks(sourceSvg, 6).forEach((label, index) => {
      const angle = -Math.PI / 2 + (Math.PI * 2 * index) / 6;
      const x = 180 + Math.cos(angle) * 84;
      const y = 110 + Math.sin(angle) * 84 + 3;
      appendText(group, x, y, label.text, {
        "text-anchor": Math.cos(angle) < -0.25 ? "end" : Math.cos(angle) > 0.25 ? "start" : "middle",
        "font-size": 7,
        "font-weight": 800,
        fill: palette.ink,
        stroke: palette.surface,
        "stroke-width": 2.1,
        "paint-order": "stroke"
      });
    });
    return true;
  }

  function hierarchyLabels(sourceSvg) {
    const labels = visibleTextMarks(sourceSvg, 18);
    if (labels.length >= 4) return labels;
    return titleWords(sourceForVariant({ sourceId: sourceSvg.id })).map((word, index) => ({ text: word, index }));
  }

  function renderSemanticHierarchyVariant(svg, variant) {
    if (variant.renderer !== "hierarchy") return false;
    if (!["radial-rosette", "golden-root", "thirds-fifths-grid"].includes(variant.compositionId)) return false;
    const sourceSvg = sourceSvgForVariant(variant);
    if (!sourceSvg) return false;
    const labels = hierarchyLabels(sourceSvg).slice(0, 14);
    const marks = sourceCircleLikeMarks(sourceSvg, 20).concat(sourceRectMarks(sourceSvg, 20));
    if (labels.length < 3 && marks.length < 4) return false;
    const frame = compositionSourceFrame(variant.compositionId);
    addSourceField(svg, frame, variant.compositionId);
    const group = svg.appendChild(el("g", {
      class: "source-pattern-recomposition semantic-hierarchy-recomposition",
      "data-source-svg-id": variant.sourceId,
      "data-recomposition-mode": `semantic-hierarchy-${variant.compositionId}`,
      "data-source-label-count": labels.length
    }));
    if (variant.compositionId === "radial-rosette") {
      addCircle(group, 180, 110, 16, { fill: palette.redHighlight, stroke: palette.red, "stroke-width": 2 });
      appendText(group, 180, 114, labels[0]?.text || tokenLabel(variant, "root"), { "text-anchor": "middle", "font-size": 6.8, "font-weight": 800, fill: palette.ink });
      labels.slice(1, 11).forEach((label, index, peers) => {
        const angle = -Math.PI / 2 + (Math.PI * 2 * index) / Math.max(peers.length, 1);
        const radius = index % 2 ? 68 : 50;
        const x = 180 + Math.cos(angle) * radius;
        const y = 110 + Math.sin(angle) * radius;
        addLine(group, 180, 110, x, y, { stroke: palette.line, "stroke-width": 1.2, "stroke-opacity": 0.54 });
        addCircle(group, x, y, 8, { fill: [palette.blueHighlight, palette.greenHighlight, palette.orangeHighlight, palette.purpleHighlight][index % 4], stroke: palette.blue, "stroke-width": 1.4 });
        appendText(group, x, y + (Math.sin(angle) > 0.65 ? 20 : -13), label.text, { "text-anchor": "middle", "font-size": 6.7, "font-weight": 800, fill: palette.ink, stroke: palette.surface, "stroke-width": 2, "paint-order": "stroke" });
      });
    } else if (variant.compositionId === "golden-root") {
      const trunk = labels.slice(0, 5);
      trunk.forEach((label, index) => {
        const x = 70 + index * 34;
        const y = 62 + index * 20;
        if (index > 0) addLine(group, 70 + (index - 1) * 34, 62 + (index - 1) * 20, x, y, { stroke: palette.line, "stroke-width": 1.3 });
        addRect(group, x - 22, y - 10, 44, 20, { rx: 5, fill: index === 0 ? palette.blueHighlight : palette.surface, stroke: palette.blue, "stroke-width": 1.3 });
        appendText(group, x, y + 3, label.text, { "text-anchor": "middle", "font-size": 6.7, "font-weight": 800, fill: palette.ink });
      });
      const context = labels.slice(5, 10);
      const contextRows = (context.length ? context : labels.slice(1, 6)).concat(
        Array.from({ length: 5 }, (_, index) => ({ text: tokenLabel(variant, "branch", index + 1) }))
      ).slice(0, 5);
      contextRows.forEach((label, index) => {
        addRect(group, 246, 54 + index * 22, 68, 16, { rx: 4, fill: palette.surface, stroke: palette.softLine });
        addRect(group, 292, 59 + index * 22, 8 + ((hashString(`${variant.sourceId}:hierarchy:${index}`) % 16)), 3.5, {
          rx: 1.8,
          fill: [palette.blue, palette.green, palette.orange, palette.purple, palette.red][index % 5],
          "fill-opacity": 0.52,
          stroke: "none"
        });
        appendText(group, 280, 65 + index * 22, label.text, { "text-anchor": "middle", "font-size": 6.5, "font-weight": 800, fill: palette.muted });
      });
    } else {
      labels.slice(0, 12).forEach((label, index) => {
        const col = index % 4;
        const row = Math.floor(index / 4);
        const x = 66 + col * 72;
        const y = 58 + row * 45;
        if (row > 0) addLine(group, x, y - 22, x, y - 10, { stroke: palette.line, "stroke-width": 1 });
        addRect(group, x - 28, y - 11, 56, 22, { rx: 5, fill: [palette.blueHighlight, palette.yellowHighlight, palette.greenHighlight][row % 3], "fill-opacity": 0.72, stroke: palette.blue, "stroke-width": 1.1 });
        appendText(group, x, y + 3, label.text, { "text-anchor": "middle", "font-size": 6.4, "font-weight": 800, fill: palette.ink });
      });
    }
    return true;
  }

  function addSourceField(svg, frame, compositionId) {
    addRect(svg, frame.x, frame.y, frame.width, frame.height, {
      class: "source-pattern-field",
      rx: compositionId === "radial-rosette" ? 72 : 6,
      fill: "none",
      stroke: "none",
      "stroke-width": 0,
      "stroke-opacity": 0
    });
  }

  function renderSourceBasedVariant(svg, variant) {
    const sourceSvg = sourceSvgForVariant(variant);
    if (!sourceSvg) return false;
    const frame = compositionSourceFrame(variant.compositionId);
    const [vx, vy, vw, vh] = parseViewBox(sourceSvg.getAttribute("viewBox"));
    const scale = Math.min(frame.width / vw, frame.height / vh);
    const tx = frame.x + (frame.width - vw * scale) / 2 - vx * scale;
    const ty = frame.y + (frame.height - vh * scale) / 2 - vy * scale;
    addSourceField(svg, frame, variant.compositionId);
    const outer = svg.appendChild(el("g", {
      class: "source-pattern-recomposition",
      "data-source-svg-id": variant.sourceId,
      "data-source-view-box": sourceSvg.getAttribute("viewBox") || "",
      transform: frame.rotate ? `rotate(${frame.rotate} 180 110)` : undefined
    }));
    const content = outer.appendChild(el("g", {
      class: "source-pattern-content",
      transform: `translate(${tx.toFixed(3)} ${ty.toFixed(3)}) scale(${scale.toFixed(5)})`
    }));
    Array.from(sourceSvg.childNodes).forEach(child => {
      if (child.nodeType === Node.ELEMENT_NODE && ["title", "desc"].includes(child.tagName.toLowerCase())) return;
      content.appendChild(child.cloneNode(true));
    });
    removeRuntimeAnimation(content);
    prefixClonedIds(content, `${variant.id}-source`);
    return true;
  }

  const palette = {
    red: "#9e1b32",
    orange: "#e77204",
    yellow: "#f1c319",
    green: "#45842a",
    blue: "#007298",
    purple: "#652f6c",
    cyan: "#00ace6",
    ink: "#333e48",
    muted: "#696969",
    line: "#cfcfcf",
    softLine: "#e7e7e7",
    surface: "#ffffff",
    blueHighlight: "#cdf3ff",
    orangeHighlight: "#ffe5cc",
    yellowHighlight: "#fff4cc",
    greenHighlight: "#dbffcc",
    purpleHighlight: "#f9ccff",
    redHighlight: "#ffccd5"
  };

  function sourceForVariant(variant) {
    return sourceById.get(variant.sourceId) || {};
  }

  function seededUnit(variant, index = 0) {
    return (hashString(`${variant.sourceId}:${variant.compositionId}:${index}`) % 1000) / 999;
  }

  function seededRange(variant, index, min, max) {
    return min + seededUnit(variant, index) * (max - min);
  }

  function tokenLabel(variant, fallback, index = 0) {
    const words = titleWords(sourceForVariant(variant));
    const value = words[index % Math.max(words.length, 1)] || fallback;
    return value.length > 12 ? `${value.slice(0, 11)}.` : value;
  }

  function addPatternSignature(svg, variant) {
    const source = sourceForVariant(variant);
    const g = svg.appendChild(el("g", {
      class: "base-signature",
      "data-source-id": variant.sourceId,
      "data-source-family": variant.sourceFamily || source.kicker || variant.inferredKind || variant.kind
    }));
    appendText(g, 18, 212, variant.sourceId, { "font-size": 1, opacity: 0, fill: palette.muted });
  }

  function renderTabs() {
    const tabs = document.getElementById("sheet-tabs");
    tabs.innerHTML = sheets.map(sheet => {
      const count = variants.filter(variant => variant.compositionId === sheet.id).length;
      return `
        <button class="sheet-tab" type="button" id="tab-${sheet.id}" data-sheet-tab="${sheet.id}" role="tab" aria-selected="${sheet.id === state.sheetId ? "true" : "false"}">
          <span>${sheet.order} ${escapeHtml(sheet.tab)}</span>
          <span class="count-badge">${count}</span>
        </button>
      `;
    }).join("");
  }

  function armatureSvg(sheet) {
    const line = 'stroke="#333e48" stroke-opacity=".36" stroke-width="1.6"';
    const primaryGuide = 'stroke="#9e1b32" stroke-opacity=".9" stroke-width="2.4"';
    const soft = 'stroke="#007298" stroke-opacity=".46" stroke-width="1.5"';
    const mark = 'fill="#ffffff" stroke="#9e1b32" stroke-width="2"';
    const open = `<svg viewBox="0 0 480 300" role="img" aria-label="${escapeHtml(sheet.title)} armature"><rect x="18" y="18" width="444" height="264" rx="8" fill="#ffffff" stroke="#cfcfcf"/>`;
    const close = "</svg>";
    if (sheet.id === "balance-symmetry") {
      return `${open}<line x1="240" y1="18" x2="240" y2="282" ${primaryGuide}/><line x1="18" y1="150" x2="462" y2="150" ${primaryGuide}/><line x1="18" y1="18" x2="462" y2="282" ${line}/><line x1="18" y1="282" x2="462" y2="18" ${line}/><circle cx="240" cy="150" r="34" fill="#cdf3ff" stroke="#007298" stroke-width="2"/><circle cx="136" cy="150" r="18" ${mark}/><circle cx="344" cy="150" r="18" ${mark}/>${close}`;
    }
    if (sheet.id === "diagonal-armature") {
      return `${open}<line x1="18" y1="18" x2="462" y2="282" ${primaryGuide}/><line x1="18" y1="282" x2="462" y2="18" ${soft}/><line x1="18" y1="92" x2="332" y2="282" ${line}/><line x1="148" y1="18" x2="462" y2="208" ${line}/><circle cx="142" cy="92" r="16" ${mark}/><circle cx="240" cy="150" r="20" fill="#fff4cc" stroke="#e77204" stroke-width="2"/><circle cx="338" cy="208" r="16" ${mark}/>${close}`;
    }
    if (sheet.id === "golden-root") {
      return `${open}<rect x="18" y="18" width="274" height="264" fill="#cdf3ff" fill-opacity=".52"/><rect x="292" y="18" width="170" height="264" fill="#fff4cc" fill-opacity=".7"/><line x1="292" y1="18" x2="292" y2="282" ${primaryGuide}/><line x1="18" y1="120" x2="462" y2="120" ${soft}/><line x1="148" y1="18" x2="148" y2="282" ${line}/><line x1="18" y1="196" x2="462" y2="196" ${line}/><circle cx="292" cy="120" r="18" ${mark}/>${close}`;
    }
    if (sheet.id === "thirds-fifths-grid") {
      const verticals = [106.8, 195.6, 240, 284.4, 373.2].map(x => `<line x1="${x}" y1="18" x2="${x}" y2="282" ${line}/>`).join("");
      const horizontals = [70.8, 123.6, 150, 176.4, 229.2].map(y => `<line x1="18" y1="${y}" x2="462" y2="${y}" ${line}/>`).join("");
      return `${open}${verticals}${horizontals}<rect x="106.8" y="70.8" width="177.6" height="105.6" fill="#dbffcc" fill-opacity=".65" stroke="#45842a" stroke-width="2"/><rect x="284.4" y="176.4" width="88.8" height="52.8" fill="#f9ccff" fill-opacity=".7" stroke="#652f6c" stroke-width="2"/>${close}`;
    }
    if (sheet.id === "radial-rosette") {
      const spokes = Array.from({ length: 12 }, (_, index) => {
        const angle = (-90 + index * 30) * Math.PI / 180;
        return `<line x1="240" y1="150" x2="${(240 + Math.cos(angle) * 116).toFixed(2)}" y2="${(150 + Math.sin(angle) * 116).toFixed(2)}" ${line}/>`;
      }).join("");
      const petals = Array.from({ length: 6 }, (_, index) => {
        const angle = (-90 + index * 60) * Math.PI / 180;
        return `<circle cx="${(240 + Math.cos(angle) * 82).toFixed(2)}" cy="${(150 + Math.sin(angle) * 82).toFixed(2)}" r="24" fill="#cdf3ff" stroke="#007298" stroke-width="2"/>`;
      }).join("");
      return `${open}<circle cx="240" cy="150" r="116" fill="none" ${soft}/><circle cx="240" cy="150" r="64" fill="none" ${line}/>${spokes}${petals}<circle cx="240" cy="150" r="30" fill="#ffccd5" stroke="#9e1b32" stroke-width="2"/>${close}`;
    }
    if (sheet.id === "flow-spine") {
      return `${open}<path d="M58 150 C128 86 174 86 240 150 S352 214 422 150" fill="none" ${primaryGuide}/><line x1="58" y1="84" x2="58" y2="216" ${line}/><line x1="240" y1="58" x2="240" y2="242" ${soft}/><line x1="422" y1="84" x2="422" y2="216" ${line}/><circle cx="58" cy="150" r="20" fill="#cdf3ff" stroke="#007298" stroke-width="2"/><circle cx="240" cy="150" r="24" fill="#fff4cc" stroke="#e77204" stroke-width="2"/><circle cx="422" cy="150" r="20" fill="#dbffcc" stroke="#45842a" stroke-width="2"/>${close}`;
    }
    return `${open}<rect x="18" y="18" width="100" height="264" fill="#f9ccff" fill-opacity=".75"/><rect x="362" y="18" width="100" height="264" fill="#f9ccff" fill-opacity=".75"/><rect x="140" y="52" width="200" height="196" fill="#cdf3ff" fill-opacity=".42" stroke="#007298" stroke-width="2"/><line x1="140" y1="88" x2="118" y2="62" ${primaryGuide}/><line x1="340" y1="108" x2="362" y2="82" ${primaryGuide}/><line x1="140" y1="184" x2="118" y2="204" ${primaryGuide}/><line x1="340" y1="206" x2="362" y2="226" ${primaryGuide}/><circle cx="206" cy="138" r="9" ${mark}/><circle cx="268" cy="168" r="9" ${mark}/>${close}`;
  }

  function renderOverview(sheet, sheetVariants) {
    document.getElementById("sheet-overview").innerHTML = `
      <div class="armature-panel">${armatureSvg(sheet)}</div>
      <div class="sheet-copy">
        <p class="sheet-kicker">Sheet ${sheet.order}</p>
        <h2>${escapeHtml(sheet.title)}</h2>
        <p>${escapeHtml(sheet.summary)}</p>
        <p>${escapeHtml(sheet.prompt)}</p>
        <div class="sheet-metrics">
          <span class="metric"><span class="count-value">${sheetVariants.length}</span> curated variants</span>
          <span class="metric">${escapeHtml(sheet.metric)}</span>
        </div>
      </div>
    `;
  }

  function renderRows(sheet, sheetVariants) {
    const grid = document.getElementById("sheet-grid");
    grid.innerHTML = sheetVariants.map(variant => {
      const source = sourceForVariant(variant);
      const patternId = source.patternId || `d3-pattern-${variant.sourceId}`;
      const title = source.title || variant.sourceId;
      const search = `${variant.id} ${patternId} ${variant.compositionId} ${variant.sourceId} ${variant.kind} ${variant.sourceFamily} ${variant.armatureLines} ${variant.quadrants} ${title} ${variant.variantTitle} ${variant.recipe} ${variant.reason}`.toLowerCase();
      return `
        <article class="composition-card" id="${variant.id}" data-composition-id="${variant.compositionId}" data-example-id="${variant.sourceId}" data-pattern-id="${patternId}" data-composition-pattern-id="${variant.id}" data-kind="${variant.kind}" data-source-family="${escapeHtml(variant.sourceFamily || source.kicker || variant.kind)}" data-armature-lines="${escapeHtml(variant.armatureLines || "")}" data-quadrants="${escapeHtml(variant.quadrants || "")}" data-reviewed="${variant.reviewed ? "true" : "false"}" data-search="${escapeHtml(search)}">
          <div class="preview-frame">
            <svg id="${variant.id}-svg" data-composition-pattern-id="${variant.id}" data-pattern-id="${patternId}" role="img"></svg>
          </div>
          <div class="composition-card-body">
            <p class="pattern-kicker">${escapeHtml(sheet.tab)} / ${escapeHtml(source.kicker || variant.kind)}</p>
            <h3>${escapeHtml(title)}</h3>
            <p class="composition-id">${escapeHtml(variant.id)}</p>
            <p class="pattern-copy">${escapeHtml(variant.variantTitle)}</p>
            <p class="reason-text">${escapeHtml(variant.reason || "Composition selected for semantic fit.")}</p>
            <p class="plan-text">${escapeHtml(variant.recipe)}</p>
          </div>
          <a class="pattern-link" href="./index.html#${encodeURIComponent(patternId)}">Open base pattern</a>
        </article>
      `;
    }).join("");
    renderPreviews(sheetVariants);
    applyFilter();
  }

  function renderPreviews(sheetVariants) {
    sheetVariants.forEach(variant => {
      const svg = document.getElementById(`${variant.id}-svg`);
      const source = sourceForVariant(variant);
      if (!svg) return;
      svg.replaceChildren();
      svg.setAttribute("viewBox", "0 0 360 220");
      svg.setAttribute("data-composition-id", variant.compositionId);
      svg.setAttribute("data-example-id", variant.sourceId);
      svg.setAttribute("data-pattern-id", source.patternId || `d3-pattern-${variant.sourceId}`);
      svg.setAttribute("data-source-family", variant.sourceFamily || source.kicker || variant.kind);
      svg.setAttribute("data-armature-lines", variant.armatureLines || "");
      svg.setAttribute("data-quadrants", variant.quadrants || "");
      svg.setAttribute("data-narrative-fit", variant.reason || "");
      svg.setAttribute("data-base-pattern-title", sourceTitle(source));
      svg.setAttribute("aria-labelledby", `${variant.id}-title ${variant.id}-desc`);
      svg.appendChild(el("title", { id: `${variant.id}-title` }, [textNode(`${source.title || variant.sourceId} ${variant.variantTitle}`)]));
      svg.appendChild(el("desc", { id: `${variant.id}-desc` }, [textNode(`${variant.reason || ""} ${variant.recipe}`)]));
      addRect(svg, 8, 8, 344, 204, { rx: 8, fill: palette.surface, stroke: "none" });
      renderVariantMarks(svg, variant);
    });
  }

  function addGuideLayer(svg, compositionId) {
    const g = svg.appendChild(el("g", { class: "composition-guide", "stroke-linecap": "round" }));
    const quadrants = [
      { id: "q2", x: 22, y: 22, width: 158, height: 88, fill: palette.blueHighlight },
      { id: "q1", x: 180, y: 22, width: 158, height: 88, fill: palette.yellowHighlight },
      { id: "q3", x: 22, y: 110, width: 158, height: 88, fill: palette.greenHighlight },
      { id: "q4", x: 180, y: 110, width: 158, height: 88, fill: palette.purpleHighlight }
    ];
    quadrants.forEach(quadrant => {
      addRect(g, quadrant.x, quadrant.y, quadrant.width, quadrant.height, {
        class: `quadrant-field quadrant-${quadrant.id}`,
        fill: quadrant.fill,
        "fill-opacity": 0.06,
        stroke: "none"
      });
    });
    const guide = { class: "composition-line", stroke: palette.line, "stroke-width": 1, "stroke-dasharray": "4 6", "stroke-opacity": 0.24 };
    const redGuide = { ...guide, class: "composition-line composition-line-primary", stroke: palette.red, "stroke-opacity": 0.3 };
    if (compositionId === "balance-symmetry") {
      addLine(g, 180, 18, 180, 202, guide);
      addLine(g, 22, 110, 338, 110, guide);
      addLine(g, 34, 34, 326, 186, { ...guide, "stroke-opacity": 0.34 });
      addLine(g, 34, 186, 326, 34, { ...guide, "stroke-opacity": 0.34 });
    } else if (compositionId === "diagonal-armature") {
      addLine(g, 34, 186, 326, 34, redGuide);
      addLine(g, 34, 34, 326, 186, guide);
      addLine(g, 34, 146, 248, 34, { ...guide, "stroke-opacity": 0.42 });
      addLine(g, 112, 198, 338, 80, { ...guide, "stroke-opacity": 0.42 });
    } else if (compositionId === "golden-root") {
      addLine(g, 220, 18, 220, 202, redGuide);
      addLine(g, 22, 84, 338, 84, guide);
      addLine(g, 134, 18, 134, 202, { ...guide, "stroke-opacity": 0.42 });
      addLine(g, 22, 154, 338, 154, { ...guide, "stroke-opacity": 0.42 });
    } else if (compositionId === "thirds-fifths-grid") {
      [74, 137, 180, 223, 286].forEach(x => addLine(g, x, 22, x, 198, guide));
      [66, 110, 154].forEach(y => addLine(g, 22, y, 338, y, guide));
    } else if (compositionId === "radial-rosette") {
      addCircle(g, 180, 110, 72, { class: "composition-line", fill: "none", stroke: palette.line, "stroke-dasharray": "4 6", "stroke-opacity": 0.24 });
      addCircle(g, 180, 110, 34, { class: "composition-line", fill: "none", stroke: palette.line, "stroke-dasharray": "4 6", "stroke-opacity": 0.24 });
      for (let i = 0; i < 8; i += 1) {
        const angle = i * Math.PI / 4;
        addLine(g, 180, 110, 180 + Math.cos(angle) * 92, 110 + Math.sin(angle) * 92, guide);
      }
    } else if (compositionId === "flow-spine") {
      addPath(g, "M36 112 C108 54 252 166 324 88", { class: "composition-line composition-line-primary", fill: "none", stroke: palette.red, "stroke-width": 1.4, "stroke-dasharray": "5 6", "stroke-opacity": 0.62 });
      [62, 180, 298].forEach(x => addLine(g, x, 36, x, 184, { ...guide, "stroke-opacity": 0.48 }));
    } else {
      addRect(g, 22, 22, 74, 176, { fill: palette.purpleHighlight, "fill-opacity": 0.44, stroke: "none" });
      addRect(g, 264, 22, 74, 176, { fill: palette.purpleHighlight, "fill-opacity": 0.44, stroke: "none" });
      addLine(g, 96, 22, 96, 198, redGuide);
      addLine(g, 264, 22, 264, 198, redGuide);
      addLine(g, 22, 110, 338, 110, guide);
    }
  }

  function renderVariantMarks(svg, variant) {
    if (renderSemanticNetworkVariant(svg, variant)) {
      addPatternSignature(svg, variant);
      return;
    }
    if (renderSemanticSetOverlapVariant(svg, variant)) {
      addPatternSignature(svg, variant);
      return;
    }
    if (renderSemanticGeospatialDiagonalVariant(svg, variant)) {
      addPatternSignature(svg, variant);
      return;
    }
    if (renderSemanticFlowVariant(svg, variant)) {
      addPatternSignature(svg, variant);
      return;
    }
    if (renderSemanticGridVariant(svg, variant)) {
      addPatternSignature(svg, variant);
      return;
    }
    if (renderSemanticLaneVariant(svg, variant)) {
      addPatternSignature(svg, variant);
      return;
    }
    if (renderSemanticScatterVariant(svg, variant)) {
      addPatternSignature(svg, variant);
      return;
    }
    if (renderSemanticRadialVariant(svg, variant)) {
      addPatternSignature(svg, variant);
      return;
    }
    if (renderSemanticHierarchyVariant(svg, variant)) {
      addPatternSignature(svg, variant);
      return;
    }
    if (renderSourceBasedVariant(svg, variant)) {
      addPatternSignature(svg, variant);
      return;
    }
    const renderer = variant.renderer || variant.kind;
    if (renderer === "network") renderNetwork(svg, variant);
    else if (renderer === "flow" || renderer === "route") renderFlow(svg, variant);
    else if (renderer === "matrix") renderMatrix(svg, variant);
    else if (renderer === "radial") renderRadial(svg, variant);
    else if (renderer === "set-overlap") renderSetOverlap(svg, variant);
    else if (renderer === "hierarchy") renderHierarchy(svg, variant);
    else if (renderer === "scatter") renderScatter(svg, variant);
    else if (renderer === "lanes" || renderer === "labels") renderLanes(svg, variant);
    else if (renderer === "table" || renderer === "document") renderTable(svg, variant);
    else if (renderer === "bar" || renderer === "chart") renderBars(svg, variant);
    else renderGeneric(svg, variant);
    addPatternSignature(svg, variant);
  }

  function renderNetwork(svg, variant) {
    const compositionId = variant.compositionId;
    const g = svg.appendChild(el("g", { class: "preview-network" }));
    const count = 8 + (hashString(variant.sourceId) % 5);
    let nodes;
    if (compositionId === "radial-rosette") {
      nodes = Array.from({ length: count }, (_, i) => {
        const angle = -Math.PI / 2 + i * Math.PI * 2 / count;
        const radius = 54 + seededRange(variant, i, 0, 22);
        return { x: 180 + Math.cos(angle) * radius, y: 110 + Math.sin(angle) * radius, r: i % 3 === 0 ? 7 : 5 };
      });
      nodes.push({ x: 180, y: 110, r: 11 });
    } else if (compositionId === "diagonal-armature") {
      nodes = Array.from({ length: count }, (_, i) => {
        const t = i / Math.max(count - 1, 1);
        return {
          x: 58 + t * 252 + seededRange(variant, i, -8, 8),
          y: 170 - t * 126 + seededRange(variant, i + 10, -12, 12),
          r: i === 0 || i === count - 1 ? 10 : 5 + (i % 3)
        };
      });
    } else {
      const left = Math.ceil(count / 2);
      nodes = Array.from({ length: count }, (_, i) => {
        const side = i < left ? -1 : 1;
        const local = i < left ? i : i - left;
        return {
          x: 180 + side * (42 + seededRange(variant, i, 0, 36)),
          y: 76 + local * 22 + seededRange(variant, i + 10, -8, 8),
          r: local === 0 ? 9 : 5 + (i % 3)
        };
      });
      nodes.push({ x: 180, y: 110, r: 11 });
    }
    const hub = nodes.length - 1;
    const links = nodes.slice(0, -1).map((_, index) => [index, Math.min(index + 1, hub)]).concat([[0, hub], [Math.floor(hub / 2), hub]]);
    links.forEach(([a, b], index) => addLine(g, nodes[a].x, nodes[a].y, nodes[b].x, nodes[b].y, { stroke: index % 2 ? palette.line : palette.blue, "stroke-width": 1.8, "stroke-opacity": 0.64 }));
    nodes.forEach((node, index) => addCircle(g, node.x, node.y, node.r, { fill: index === nodes.length - 1 ? palette.red : index % 2 ? palette.blueHighlight : palette.greenHighlight, stroke: index === nodes.length - 1 ? palette.red : palette.blue, "stroke-width": 1.8 }));
    appendText(g, 180, 20, tokenLabel(variant, "network"), { "text-anchor": "middle", "font-size": 10, "font-weight": 800, fill: palette.ink });
  }

  function renderFlow(svg, variant) {
    const compositionId = variant.compositionId;
    const g = svg.appendChild(el("g", { class: "preview-flow" }));
    const points = compositionId === "diagonal-armature"
      ? [[50, 170], [112, 142], [178, 112], [246, 76], [310, 46]]
      : [[44, 128], [112, 88], [180, 112], [248, 144], [316, 90]].map((point, index) => [point[0], point[1] + seededRange(variant, index, -10, 10)]);
    points.forEach((point, index) => {
      if (index > 0) {
        const prev = points[index - 1];
        addPath(g, `M${prev[0]} ${prev[1]} C${(prev[0] + point[0]) / 2} ${prev[1] - 26}, ${(prev[0] + point[0]) / 2} ${point[1] + 26}, ${point[0]} ${point[1]}`, { fill: "none", stroke: index % 2 ? palette.blue : palette.orange, "stroke-width": 7 - index * 0.6, "stroke-opacity": 0.62, "stroke-linecap": "round" });
      }
    });
    points.forEach((point, index) => addCircle(g, point[0], point[1], index === 0 || index === points.length - 1 ? 11 : 8, { fill: index === points.length - 1 ? palette.greenHighlight : palette.surface, stroke: index === points.length - 1 ? palette.green : palette.red, "stroke-width": 2 }));
    appendText(g, points[0][0], points[0][1] + 30, tokenLabel(variant, "source", 0), { "text-anchor": "middle", "font-size": 10, fill: palette.muted });
    appendText(g, points.at(-1)[0], points.at(-1)[1] + 30, tokenLabel(variant, "output", 1), { "text-anchor": "middle", "font-size": 10, fill: palette.muted });
  }

  function renderMatrix(svg, variant) {
    const compositionId = variant.compositionId;
    const g = svg.appendChild(el("g", { class: "preview-matrix" }));
    const startX = compositionId === "golden-root" ? 46 : 58;
    const startY = 48;
    const cols = compositionId === "thirds-fifths-grid" ? 10 : 7 + (hashString(variant.sourceId) % 2);
    const rows = 4 + (hashString(variant.sourceId) % 2);
    for (let row = 0; row < rows; row += 1) {
      for (let col = 0; col < cols; col += 1) {
        const value = (row * 3 + col * 5 + hashString(variant.sourceId)) % 10;
        addRect(g, startX + col * 22, startY + row * 22, 17, 17, { rx: 3, fill: value > 6 ? palette.redHighlight : value > 3 ? palette.blueHighlight : palette.greenHighlight, stroke: palette.surface, "stroke-width": 1 });
      }
    }
    addRect(g, startX - 8, startY - 8, cols * 22 + 2, rows * 22 + 2, { fill: "none", stroke: palette.ink, "stroke-opacity": 0.28 });
    addRect(g, 250, 54, 58, 86, { rx: 5, fill: palette.yellowHighlight, stroke: palette.orange });
    appendText(g, 279, 103, tokenLabel(variant, "key"), { "text-anchor": "middle", "font-size": 12, "font-weight": 800, fill: palette.ink });
  }

  function renderRadial(svg, variant) {
    const g = svg.appendChild(el("g", { class: "preview-radial" }));
    const cx = 180;
    const cy = 110;
    const segments = 8 + (hashString(variant.sourceId) % 5) * 2;
    addCircle(g, cx, cy, 76, { fill: palette.blueHighlight, "fill-opacity": 0.24, stroke: palette.blue, "stroke-width": 1.8 });
    addCircle(g, cx, cy, 38, { fill: palette.yellowHighlight, "fill-opacity": 0.7, stroke: palette.orange, "stroke-width": 1.8 });
    for (let i = 0; i < segments; i += 1) {
      const angle0 = -Math.PI / 2 + i * Math.PI * 2 / segments;
      const angle1 = angle0 + Math.PI * 2 / (segments * 1.5);
      const r0 = 42 + seededRange(variant, i, -4, 4);
      const r1 = 74 + seededRange(variant, i + 30, -3, 5);
      const d = `M${cx + Math.cos(angle0) * r0} ${cy + Math.sin(angle0) * r0} L${cx + Math.cos(angle0) * r1} ${cy + Math.sin(angle0) * r1} A${r1} ${r1} 0 0 1 ${cx + Math.cos(angle1) * r1} ${cy + Math.sin(angle1) * r1} L${cx + Math.cos(angle1) * r0} ${cy + Math.sin(angle1) * r0} Z`;
      addPath(g, d, { fill: i % 3 === 0 ? palette.red : i % 3 === 1 ? palette.blue : palette.green, "fill-opacity": 0.72, stroke: palette.surface, "stroke-width": 1 });
    }
    addCircle(g, cx, cy, 17, { fill: palette.surface, stroke: palette.red, "stroke-width": 2 });
    appendText(g, cx, cy + 3, tokenLabel(variant, "root"), { "text-anchor": "middle", "font-size": 8.5, "font-weight": 800, fill: palette.ink });
  }

  function renderSetOverlap(svg, variant) {
    const compositionId = variant.compositionId;
    const g = svg.appendChild(el("g", { class: "preview-set-overlap" }));
    const centers = compositionId === "radial-rosette"
      ? [[180, 68], [220, 100], [204, 148], [156, 148], [140, 100]]
      : [[132, 104], [174, 86], [218, 104], [156, 138], [202, 138]];
    centers.forEach((point, index) => {
      addCircle(g, point[0] + seededRange(variant, index, -3, 3), point[1] + seededRange(variant, index + 10, -3, 3), 36 + seededRange(variant, index + 20, 0, 10), {
        fill: index % 5 === 0 ? palette.blueHighlight : index % 5 === 1 ? palette.greenHighlight : index % 5 === 2 ? palette.redHighlight : index % 5 === 3 ? palette.yellowHighlight : palette.purpleHighlight,
        "fill-opacity": 0.58,
        stroke: index % 2 ? palette.blue : palette.red,
        "stroke-width": 2
      });
    });
    addCircle(g, 180, 114, 10, { fill: palette.surface, stroke: palette.ink, "stroke-width": 1.8 });
    appendText(g, 180, 118, tokenLabel(variant, "set"), { "text-anchor": "middle", "font-size": 8, fill: palette.ink });
    [[92, 68], [268, 68], [92, 162], [268, 162]].forEach((point, index) => {
      addRect(g, point[0], point[1], 42, 12, { rx: 4, fill: palette.surface, stroke: index % 2 ? palette.blue : palette.green });
      addLine(g, point[0] + (point[0] < 180 ? 42 : 0), point[1] + 6, 180, 114, { stroke: palette.line, "stroke-width": 1, "stroke-opacity": 0.72 });
    });
  }

  function renderHierarchy(svg, variant) {
    const compositionId = variant.compositionId;
    const g = svg.appendChild(el("g", { class: "preview-hierarchy" }));
    const root = compositionId === "golden-root" ? [114, 84] : [180, 62];
    let children = compositionId === "golden-root"
      ? [[70, 140], [128, 146], [190, 126], [254, 152]]
      : [[86, 146], [144, 136], [216, 136], [274, 146]];
    children = children.map((point, index) => [point[0] + seededRange(variant, index, -7, 7), point[1] + seededRange(variant, index + 10, -7, 7)]);
    children.forEach((point, index) => {
      addPath(g, `M${root[0]} ${root[1]} C${root[0]} ${(root[1] + point[1]) / 2}, ${point[0]} ${(root[1] + point[1]) / 2}, ${point[0]} ${point[1]}`, { fill: "none", stroke: index % 2 ? palette.blue : palette.green, "stroke-width": 2, "stroke-opacity": 0.72 });
      addCircle(g, point[0], point[1], 16 + index * 2, { fill: index % 2 ? palette.blueHighlight : palette.greenHighlight, stroke: index % 2 ? palette.blue : palette.green, "stroke-width": 1.8 });
    });
    addCircle(g, root[0], root[1], 20, { fill: palette.redHighlight, stroke: palette.red, "stroke-width": 2 });
    appendText(g, root[0], root[1] + 3, tokenLabel(variant, "root"), { "text-anchor": "middle", "font-size": 8.5, "font-weight": 800, fill: palette.ink });
  }

  function renderScatter(svg, variant) {
    const compositionId = variant.compositionId;
    const g = svg.appendChild(el("g", { class: "preview-scatter" }));
    const count = 30 + (hashString(variant.sourceId) % 18);
    const points = Array.from({ length: count }, (_, index) => {
      const angle = index * 2.399;
      const radius = compositionId === "balance-symmetry" ? 18 + (index % 9) * 8 : 12 + index * 2.5;
      const x = compositionId === "diagonal-armature" ? 58 + index * 252 / Math.max(count - 1, 1) : 180 + Math.cos(angle) * radius + seededRange(variant, index, -3, 3);
      const y = compositionId === "diagonal-armature" ? 168 - index * 122 / Math.max(count - 1, 1) + Math.sin(angle) * 10 : 110 + Math.sin(angle) * radius * 0.62 + seededRange(variant, index + 40, -3, 3);
      return { x, y, r: 2.8 + (index % 4) * 0.8 };
    });
    points.forEach((point, index) => addCircle(g, point.x, point.y, point.r, { fill: index % 5 === 0 ? palette.red : index % 2 ? palette.blue : palette.green, "fill-opacity": 0.72, stroke: palette.surface, "stroke-width": 0.8 }));
    addPath(g, compositionId === "diagonal-armature" ? "M54 172 L306 48" : "M78 110 H282", { stroke: palette.ink, "stroke-opacity": 0.32, "stroke-width": 2, fill: "none" });
    appendText(g, 282, 42, tokenLabel(variant, "measure"), { "text-anchor": "middle", "font-size": 10, fill: palette.muted });
  }

  function renderLanes(svg, variant) {
    const g = svg.appendChild(el("g", { class: "preview-lanes" }));
    addRect(g, 112, 44, 136, 124, { rx: 6, fill: palette.blueHighlight, "fill-opacity": 0.42, stroke: palette.blue });
    const count = 18 + (hashString(variant.sourceId) % 8);
    for (let i = 0; i < count; i += 1) {
      const x = 126 + ((i * 37 + hashString(variant.sourceId)) % 108);
      const y = 58 + ((i * 29 + hashString(`${variant.sourceId}:lane`)) % 92);
      addCircle(g, x, y, 3.2, { fill: i % 3 === 0 ? palette.red : i % 3 === 1 ? palette.blue : palette.orange, stroke: palette.surface, "stroke-width": 0.8 });
      const left = i % 2 === 0;
      const laneX = left ? 28 : 282;
      const laneY = 30 + (i % 8) * 20;
      addLine(g, x, y, laneX + (left ? 70 : 0), laneY + 7, { stroke: i % 3 === 0 ? palette.red : palette.blue, "stroke-width": 1, "stroke-opacity": 0.44 });
    }
    for (let i = 0; i < 8; i += 1) {
      addRect(g, 24, 28 + i * 20, 74, 12, { rx: 3, fill: palette.surface, stroke: palette.line });
      addRect(g, 262, 28 + i * 20, 74, 12, { rx: 3, fill: palette.surface, stroke: palette.line });
      appendText(g, 61, 37 + i * 20, tokenLabel(variant, "label", i), { "text-anchor": "middle", "font-size": 7.5, fill: palette.muted });
      appendText(g, 299, 37 + i * 20, tokenLabel(variant, "label", i + 4), { "text-anchor": "middle", "font-size": 7.5, fill: palette.muted });
    }
  }

  function renderTable(svg, variant) {
    const compositionId = variant.compositionId;
    const g = svg.appendChild(el("g", { class: "preview-table" }));
    const x = compositionId === "golden-root" ? 42 : 54;
    const y = 46;
    const cols = compositionId === "golden-root" ? 4 : 5;
    const rows = 5;
    for (let row = 0; row < rows; row += 1) {
      for (let col = 0; col < cols; col += 1) {
        addRect(g, x + col * 42, y + row * 24, 36, 16, { rx: 2, fill: row === 0 ? palette.redHighlight : palette.surface, stroke: palette.line });
        if (row > 0 && col === cols - 1) {
          addRect(g, x + col * 42 + 5, y + row * 24 + 5, 12 + seededRange(variant, row + col, 4, 20), 5, { rx: 2, fill: row % 2 ? palette.blue : palette.green, stroke: "none" });
        }
        if (row === 0) {
          appendText(g, x + col * 42 + 18, y + 11, tokenLabel(variant, "col", col), { "text-anchor": "middle", "font-size": 7.5, fill: palette.ink });
        }
      }
    }
    if (compositionId === "golden-root") {
      addRect(g, 248, 54, 64, 82, { rx: 6, fill: palette.yellowHighlight, stroke: palette.orange });
      appendText(g, 280, 100, tokenLabel(variant, "note"), { "text-anchor": "middle", "font-size": 12, "font-weight": 800, fill: palette.ink });
    }
  }

  function renderBars(svg, variant) {
    const compositionId = variant.compositionId;
    const g = svg.appendChild(el("g", { class: "preview-bars" }));
    const values = Array.from({ length: 6 }, (_, index) => 36 + seededRange(variant, index, 0, 68));
    values.forEach((value, index) => {
      const x = 70 + index * 36;
      const y = 166 - value;
      addRect(g, x, y, 22, value, { rx: 3, fill: index % 2 ? palette.blue : palette.green, "fill-opacity": 0.82, stroke: palette.surface });
      if (compositionId === "diagonal-armature") addCircle(g, x + 11, y, 4, { fill: palette.red });
    });
    addLine(g, 52, 166, 310, 166, { stroke: palette.ink, "stroke-opacity": 0.42 });
    if (compositionId === "diagonal-armature") addLine(g, 70, 154, 270, 66, { stroke: palette.red, "stroke-width": 2, "stroke-opacity": 0.72 });
    appendText(g, 180, 36, tokenLabel(variant, "rank"), { "text-anchor": "middle", "font-size": 10, "font-weight": 800, fill: palette.ink });
  }

  function renderGeneric(svg, variant) {
    const g = svg.appendChild(el("g", { class: "preview-generic" }));
    addRect(g, 70, 58, 92, 92, { rx: 7, fill: palette.blueHighlight, stroke: palette.blue, "stroke-width": 2 });
    addRect(g, 188, 72, 98, 64, { rx: 7, fill: palette.greenHighlight, stroke: palette.green, "stroke-width": 2 });
    addPath(g, `M158 104 C186 ${64 + seededRange(variant, 1, -12, 12)} 216 ${154 + seededRange(variant, 2, -12, 12)} 246 110`, { fill: "none", stroke: palette.red, "stroke-width": 3, "stroke-linecap": "round" });
    appendText(g, 180, 172, tokenLabel(variant, "pattern"), { "text-anchor": "middle", "font-size": 10, "font-weight": 800, fill: palette.ink });
  }

  function renderSheet() {
    const sheet = sheets.find(item => item.id === state.sheetId) || sheets[0];
    const sheetVariants = variants.filter(variant => variant.compositionId === sheet.id);
    state.sheetId = sheet.id;
    document.body.dataset.activeCompositionSheet = sheet.id;
    window.location.hash = sheet.id;
    renderTabs();
    renderOverview(sheet, sheetVariants);
    renderRows(sheet, sheetVariants);
  }

  function applyFilter() {
    const query = state.query.trim().toLowerCase();
    const rows = Array.from(document.querySelectorAll(".composition-card"));
    let visible = 0;
    rows.forEach(row => {
      const matches = !query || row.dataset.search.includes(query);
      row.hidden = !matches;
      if (matches) visible += 1;
    });
    document.body.dataset.visibleVariantCount = String(visible);
  }

  function bindEvents() {
    document.getElementById("sheet-tabs").addEventListener("click", event => {
      const button = event.target.closest("[data-sheet-tab]");
      if (!button) return;
      state.sheetId = button.dataset.sheetTab;
      renderSheet();
    });
    document.getElementById("pattern-search").addEventListener("input", event => {
      state.query = event.target.value;
      applyFilter();
    });
    window.addEventListener("hashchange", () => {
      const next = resolveInitialSheetId();
      if (next === state.sheetId) return;
      state.sheetId = next;
      renderSheet();
    });
  }

  function renderEmptyState(message) {
    document.getElementById("sheet-overview").innerHTML = `<div class="sheet-copy"><h2>${escapeHtml(message)}</h2></div>`;
  }

  function init() {
    document.body.dataset.compositionSheetCount = String(sheets.length);
    document.body.dataset.compositionVariantCount = String(variants.length);
    document.body.dataset.compositionReviewedPatternCount = String(reviewedPatterns.length);
    document.getElementById("sheet-count").textContent = String(sheets.length);
    document.getElementById("variant-count").textContent = String(variants.length);
    document.getElementById("reviewed-count").textContent = String(reviewedPatterns.length);
    if (!metadata.length) {
      renderEmptyState("Pattern metadata is unavailable.");
      return;
    }
    bindEvents();
    renderSheet();
  }

  init();
})();
